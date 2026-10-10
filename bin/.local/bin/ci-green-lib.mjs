// The logic behind the ci-green command (see ci-green for the command line and exit codes). The
// classifier, the rerun plan, the log and retry readers, and the wait record are pure or take their
// effects as arguments; main() is the only function that runs git, gh, the clock, and the terminal.
import { execFileSync, spawnSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join, basename } from "node:path";

export const EXIT = { green: 0, red: 1, missing: 2, unavailable: 3, pending: 75 };

const MINUTE = 60_000;
const MISSING_AFTER = 5 * MINUTE;
const UNAVAILABLE_AFTER = 60 * MINUTE;
const CONFIG_PATH = ".github/ci-green.json";
const LOG_TAIL_LINES = 40;

const ANSI = /\x1b\[[0-9;]*m/g;
// A step whose failure says the runner or the network failed, not the code under test.
const SETUP_STEP = /^(Set up job|Complete job|Run actions\/(checkout|setup-node|cache|upload-artifact|download-artifact)|Run \.\/\.github\/actions\/(bounded-install|install-diagnostics)|Run npm (ci|install)\b|Run npx playwright install|Install )/;
const BAD_JOB = new Set(["failure", "cancelled", "timed_out", "startup_failure"]);

// ---- the expected-set file ----

/**
 * Reads `.github/ci-green.json` as `git show` returned it.
 *
 * @param {string | null | undefined} text - The file's content, or null when git could not read it.
 * @returns {{ ok: true, config: object } | { ok: false, error: string }} The validated config, or
 *   why it cannot be used.
 */
export function parseConfig(text) {
  if (typeof text !== "string" || text.trim() === "") return { ok: false, error: "absent or empty" };
  let config;
  try {
    config = JSON.parse(text);
  } catch (e) {
    return { ok: false, error: `not valid JSON (${e.message})` };
  }
  for (const key of ["expected", "judgedWhenPresent", "neverOnPullRequest", "ignorePrefixes"]) {
    if (key === "expected" && Array.isArray(config?.expected) && config.expected.length === 0) {
      return { ok: false, error: '"expected" must not be empty' };
    }
    if (!Array.isArray(config?.[key]) || !config[key].every((v) => typeof v === "string")) {
      return { ok: false, error: `"${key}" must be an array of strings` };
    }
  }
  return { ok: true, config };
}

/**
 * Splits `git diff --name-only` output into paths.
 *
 * @param {string} text - One path per line.
 * @returns {string[]} The non-empty paths.
 */
export function parseNameOnly(text) {
  return text.split("\n").map((l) => l.trim()).filter(Boolean);
}

/**
 * The workflows that must have run: the expected set whenever the diff touches a path outside the
 * ignored prefixes, none for a diff that stays inside them. An empty diff (a SHA already in
 * origin/main) cannot show it stays inside them, so it requires the expected set too.
 *
 * @param {{ expected: string[], ignorePrefixes: string[] }} config - The parsed config.
 * @param {string[]} files - The diff's changed paths.
 * @returns {string[]} Workflow file paths.
 */
export function requiredWorkflows(config, files) {
  if (files.length === 0) return config.expected;
  const outside = files.some((f) => !config.ignorePrefixes.some((p) => f.startsWith(p)));
  return outside ? config.expected : [];
}

// ---- the classifier ----

/**
 * Moves the missing and unavailable clocks to the latest rerun's start, since a rerun gives the
 * workflow a fresh attempt to finish in.
 *
 * @param {number} pushedAtMs - When the SHA reached GitHub.
 * @param {Array<{ run_attempt: number, run_started_at: string }>} runs - The SHA's workflow runs.
 * @returns {number} Epoch milliseconds.
 */
export function clockStart(pushedAtMs, runs) {
  const reruns = runs.filter((r) => r.run_attempt > 1).map((r) => Date.parse(r.run_started_at));
  return Math.max(pushedAtMs, ...reruns);
}

/**
 * Classifies a SHA's workflow runs. Only run conclusions count, never raw check runs, so a job
 * skipped by its own `if:` inside a successful run is not red. Red wins, then a missing workflow
 * past 5 minutes, then pending (unavailable past 60 minutes), then a missing workflow inside the
 * 5 minutes, then green. Zero runs is never green.
 *
 * @param {object} input - The classifier input.
 * @param {Array<object>} input.runs - Workflow-run objects from the runs API.
 * @param {{ expected: string[], ignorePrefixes: string[] }} input.config - The parsed config.
 * @param {string[]} input.files - The diff's changed paths.
 * @param {number} input.nowMs - The current time.
 * @param {number} input.clockStartMs - When the clocks started, see {@link clockStart}.
 * @param {string | null} [input.apiError] - Why the runs could not be read, if they could not.
 * @returns {{ state: string, exit: number, red: object[], pending: object[], missing: string[],
 *   noRuns: boolean, rerunRuns: object[], reason: string | null }} The verdict.
 */
export function classify({ runs, config, files, nowMs, clockStartMs, apiError = null }) {
  const verdict = (state, extra = {}) => ({
    state, exit: EXIT[state], red: [], pending: [], missing: [], noRuns: runs.length === 0, rerunRuns: [], reason: null, ...extra,
  });
  if (apiError) return verdict("unavailable", { reason: apiError });
  const elapsed = nowMs - clockStartMs;
  const done = runs.filter((r) => r.status === "completed");
  const red = done.filter((r) => r.conclusion !== "success");
  const pending = runs.filter((r) => r.status !== "completed");
  const present = new Set(runs.map((r) => r.path));
  const missing = requiredWorkflows(config, files).filter((p) => !present.has(p));
  const rerunRuns = runs.filter((r) => r.run_attempt > 1);
  const noRuns = runs.length === 0;
  if (red.length) return verdict("red", { red, pending, missing, rerunRuns });
  if ((missing.length || noRuns) && elapsed >= MISSING_AFTER) return verdict("missing", { pending, missing, rerunRuns });
  if (pending.length) {
    if (elapsed >= UNAVAILABLE_AFTER) {
      return verdict("unavailable", { pending, rerunRuns, reason: "no terminal result 60 minutes after the push" });
    }
    return verdict("pending", { pending, missing, rerunRuns });
  }
  if (missing.length || noRuns) return verdict("pending", { missing, rerunRuns });
  return verdict("green", { rerunRuns });
}

/**
 * Describes the likeliest reason a pull request's SHA got no runs.
 *
 * @param {{ number: number, mergeable_state?: string } | null} pr - The pull request object.
 * @returns {string | null} A sentence, or null when nothing explains the absence.
 */
export function missingNote(pr) {
  if (pr?.mergeable_state === "dirty") {
    return `PR #${pr.number} has merge conflicts with its base, so GitHub starts no pull_request workflows; resolve them and push.`;
  }
  return null;
}

// ---- failures and reruns ----

/**
 * Lists a run's jobs that did not succeed, with the steps that failed in each. A skipped job is
 * not listed.
 *
 * @param {Array<{ id: number, name: string, conclusion: string | null, steps?: object[] }>} jobs - A run's jobs.
 * @returns {Array<{ id: number, name: string, conclusion: string, steps: string[] }>} The bad jobs.
 */
export function failingJobs(jobs) {
  return jobs
    .filter((j) => BAD_JOB.has(j.conclusion))
    .map((j) => ({
      id: j.id,
      name: j.name,
      conclusion: j.conclusion,
      steps: (j.steps ?? []).filter((s) => BAD_JOB.has(s.conclusion)).map((s) => s.name),
    }));
}

/**
 * Plans the single rerun an infrastructure red earns. A run still on its first attempt whose
 * failures are all cancelled or timed-out jobs reruns those jobs one by one; one whose failed jobs
 * all failed in setup steps reruns with `--failed`. Any other red, or a run already on a second
 * attempt, plans nothing, and a plan covers every red run or none.
 *
 * @param {Array<{ id: number, run_attempt: number }>} redRuns - The red runs.
 * @param {Record<string, object[]>} jobsByRun - Each red run's jobs, keyed by run id.
 * @returns {string[][]} `gh` argument lists, empty when the red stands.
 */
export function planReruns(redRuns, jobsByRun) {
  const commands = [];
  for (const run of redRuns) {
    if (run.run_attempt !== 1) return [];
    const jobs = jobsByRun[run.id];
    if (!jobs) return [];
    const bad = failingJobs(jobs);
    if (!bad.length) return [];
    const failed = bad.filter((j) => j.conclusion === "failure");
    if (failed.length) {
      if (!failed.every((j) => j.steps.length && j.steps.every((s) => SETUP_STEP.test(s)))) return [];
      commands.push(["run", "rerun", String(run.id), "--failed"]);
    } else {
      // One --failed covers cancelled jobs too, and GitHub may refuse a second --job rerun while
      // the first is still running.
      if (bad.length > 1) commands.push(["run", "rerun", String(run.id), "--failed"]);
      else commands.push(["run", "rerun", String(run.id), "--job", String(bad[0].id)]);
    }
  }
  return commands;
}

const cleanLine = (raw) =>
  raw
    .replace(ANSI, "")
    .replace(/^(?:[^\t]*\t[^\t]*\t)?﻿?\d{4}-\d\d-\d\dT[\d:.]+Z ?/, "")
    .trimEnd();

/**
 * Pulls failing test names out of a `gh run view --log-failed` log: the Playwright summary's
 * "N failed" block and Vitest's `FAIL` lines.
 *
 * @param {string} log - The failed-step log.
 * @returns {string[]} Distinct test names in log order.
 */
export function failedTests(log) {
  const names = [];
  let inFailed = false;
  for (const raw of log.split("\n")) {
    const line = cleanLine(raw);
    if (/^\s*\d+ failed\s*$/.test(line)) inFailed = true;
    else if (/^\s*\d+ (flaky|skipped|passed|did not run|interrupted)/.test(line)) inFailed = false;
    else if (inFailed && line.trim()) names.push(line.trim());
    else {
      const vitest = /^\s*FAIL\s+(.+)$/.exec(line);
      if (vitest) names.push(vitest[1].trim());
    }
  }
  return [...new Set(names)];
}

/**
 * The last lines of a failed-step log, with the job, step, and timestamp prefix removed.
 *
 * @param {string} log - The failed-step log.
 * @param {number} [cap] - The most lines to keep.
 * @returns {string[]} At most `cap` lines.
 */
export function logTail(log, cap = LOG_TAIL_LINES) {
  const lines = log.split("\n").map(cleanLine);
  while (lines.length && !lines.at(-1).trim()) lines.pop();
  return lines.slice(-cap);
}

// ---- retried tests ----

/**
 * Keeps the jobs that report retried tests, found by their reporting step.
 *
 * @param {Array<{ steps?: Array<{ name: string }> }>} jobs - A run's jobs.
 * @returns {object[]} The test jobs.
 */
export function testJobs(jobs) {
  return jobs.filter((j) => (j.steps ?? []).some((s) => /^Report retried tests$/i.test(s.name)));
}

/**
 * Splits a `retries` annotation message into retried test names and unreadable-report reasons.
 *
 * @param {string} message - `none`, names joined by `, `, `unknown (<reason>)`, or names then
 *   `; unknown (<reason>)`.
 * @returns {{ retried: string[], unknown: string[] }} The parts.
 */
export function parseRetries(message) {
  const retried = [];
  const unknown = [];
  for (const part of message.trim().split(/;\s*(?=unknown \()/)) {
    const reason = /^unknown \((.*)\)$/s.exec(part);
    if (reason) unknown.push(reason[1]);
    else if (part !== "none" && part !== "") retried.push(...part.split(", ").map((n) => n.trim()).filter(Boolean));
  }
  return { retried, unknown };
}

/**
 * Turns each test job's annotations into the lines the green report prints.
 *
 * @param {Array<{ job: { workflow: string, name: string }, annotations: Array<{ title?: string, message?: string }> }>} entries -
 *   One per test job.
 * @returns {{ lines: string[], retried: string[] }} The printed lines and every retried test name.
 */
export function retriesReport(entries) {
  const lines = [];
  const retried = [];
  for (const { job, annotations } of entries) {
    const where = `${job.workflow} / ${job.name}`;
    const note = annotations.find((a) => a.title === "retries");
    if (!note) {
      lines.push(`retries not reported (${where})`);
      continue;
    }
    const parsed = parseRetries(note.message ?? "");
    retried.push(...parsed.retried);
    const parts = [parsed.retried.join(", "), ...parsed.unknown.map((u) => `unknown (${u})`)].filter(Boolean);
    lines.push(`retried: ${parts.length ? parts.join("; ") : "none"} (${where})`);
  }
  return { lines, retried };
}

// ---- the wait record ----

const iso = (ms) => new Date(ms).toISOString().replace(/\.\d{3}Z$/, "Z");

/**
 * Builds the CI line of the shared run records file.
 *
 * @param {object} f - The wait's facts.
 * @param {number} f.startMs - When the wait began.
 * @param {number} f.endMs - When it ended.
 * @param {string[]} f.retried - Retried test names read from the annotations.
 * @returns {object} The record.
 */
export function ciRecord({ sha, pr, task, toplevel, branch, startMs, endMs, queueSeconds, outcome, retried }) {
  return { kind: "ci", sha, pr, task, toplevel, branch, start: iso(startMs), end: iso(endMs), queueSeconds, outcome, retried };
}

/**
 * Appends one record to `runs.jsonl` under the `runs.lock` flock, the way cairn-run-gate does.
 * Best effort: a failure warns once and returns.
 *
 * @param {string} dir - The records directory.
 * @param {object} record - The record to write.
 * @param {{ lockWait: number, warn: (msg: string) => void }} opts - Seconds to wait for the lock, and the warning sink.
 */
export function appendRecord(dir, record, { lockWait, warn }) {
  try {
    mkdirSync(dir, { recursive: true });
  } catch {
    warn(`ci-green: record not written (cannot create ${dir})`);
    return;
  }
  const res = spawnSync(
    "flock",
    ["-w", String(lockWait), "-E", "3", join(dir, "runs.lock"), "sh", "-c", 'printf "%s\\n" "$1" >> "$2"', "sh", JSON.stringify(record), join(dir, "runs.jsonl")],
    { stdio: "ignore" },
  );
  if (res.status === 0) return;
  warn(res.status === 3 ? "ci-green: record not written (the records lock stayed held)" : `ci-green: record not written (cannot write ${dir}/runs.jsonl)`);
}

// ---- the command ----

const USAGE = "usage: ci-green <sha> --pr <n> [--wait] [--pushed-at <iso>] [--task <id>]";

function parseArgs(args) {
  const opts = { sha: null, pr: null, wait: false, pushedAt: null, task: null };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--wait") opts.wait = true;
    else if (a === "--pr" || a === "--pushed-at" || a === "--task") {
      const value = args[++i];
      if (value === undefined) return { error: `${a} needs a value` };
      if (a === "--pr") opts.pr = value;
      else if (a === "--pushed-at") opts.pushedAt = value;
      else opts.task = value;
    } else if (a.startsWith("-")) return { error: `unknown option ${a}` };
    else if (opts.sha === null) opts.sha = a;
    else return { error: `unexpected argument ${a}` };
  }
  if (!opts.sha) return { error: "a SHA is required" };
  if (!/^\d+$/.test(opts.pr ?? "")) return { error: "--pr <n> is required" };
  opts.pr = Number(opts.pr);
  return { opts };
}

const realDeps = () => ({
  git: (args) => execFileSync("git", args, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], maxBuffer: 1 << 26 }),
  gh: (args) => execFileSync("gh", args, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], maxBuffer: 1 << 26 }),
  out: (s) => process.stdout.write(`${s}\n`),
  err: (s) => process.stderr.write(`${s}\n`),
  now: () => Date.now(),
  sleep: (ms) => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms),
  env: process.env,
});

const message = (e) => String(e?.stderr || e?.message || e).trim().split("\n")[0];

/**
 * Runs the command.
 *
 * @param {string[]} args - The command-line arguments after the program name.
 * @param {object} [deps] - Replaceable effects: `git`, `gh` (each takes an argument list and
 *   returns stdout or throws), `out`, `err`, `now`, `sleep`, and `env`.
 * @returns {number} The exit code.
 */
export function main(args, deps = realDeps()) {
  const { git, gh, out, err, now, sleep, env } = deps;
  const parsed = parseArgs(args);
  if (parsed.error) {
    err(`ci-green: ${parsed.error}\n${USAGE}`);
    return EXIT.unavailable;
  }
  const { opts } = parsed;
  const { pr, wait } = opts;
  // The runs API matches head_sha only against a full SHA, so the argument is resolved after the fetch.
  let sha = opts.sha;
  const startMs = now();
  const quiet = (fn, fallback = "") => {
    try {
      return fn().trim();
    } catch {
      return fallback;
    }
  };
  const toplevel = quiet(() => git(["rev-parse", "--show-toplevel"]));
  const branch = quiet(() => git(["branch", "--show-current"]));
  const short = sha.slice(0, 8);
  let clockStartMs = startMs;
  let pushedAtMs = startMs;
  let retried = [];

  const finish = (outcome, line) => {
    out(`ci-green: ${line}`);
    if (wait) {
      const dir = env.CAIRN_GATE_RECORDS_DIR || join(env.HOME || homedir(), ".local/state/cairn-run-gate");
      const lockWait = Number(env.CAIRN_GATE_RECORDS_LOCK_WAIT) || 10;
      const queueSeconds = Math.max(0, Math.round((startMs - pushedAtMs) / 1000));
      appendRecord(dir, ciRecord({ sha, pr, task: opts.task, toplevel, branch, startMs, endMs: now(), queueSeconds, outcome, retried }), { lockWait, warn: err });
    }
    return EXIT[outcome];
  };
  const unavailable = (why) => finish("unavailable", `unavailable (${why}) ${short}`);

  // The SHA, the merge base, and the config must all come from a fresh view of origin.
  try {
    git(["fetch", "origin", "main", "--quiet"]);
    try {
      sha = git(["rev-parse", "--verify", `${opts.sha}^{commit}`]).trim();
    } catch {
      git(["fetch", "origin", `pull/${pr}/head`, "--quiet"]);
      sha = git(["rev-parse", "--verify", `${opts.sha}^{commit}`]).trim();
    }
  } catch (e) {
    return unavailable(`cannot fetch ${short}: ${message(e)}`);
  }
  let configText = null;
  try {
    configText = git(["show", `${sha}:${CONFIG_PATH}`]);
  } catch {
    configText = null;
  }
  const config = parseConfig(configText);
  if (!config.ok) return unavailable(`${CONFIG_PATH} at ${short} is ${config.error}`);
  let files;
  try {
    const base = git(["merge-base", "origin/main", sha]).trim();
    files = parseNameOnly(git(["diff", "--name-only", `${base}...${sha}`]));
  } catch (e) {
    return unavailable(`cannot diff ${short} against origin/main: ${message(e)}`);
  }
  pushedAtMs = Date.parse(opts.pushedAt ?? quiet(() => git(["show", "-s", "--format=%cI", sha])));
  if (Number.isNaN(pushedAtMs)) return unavailable("cannot read the push time; pass --pushed-at <iso>");
  clockStartMs = pushedAtMs;

  const api = (path) => JSON.parse(gh(["api", path]));
  const jobsOf = (run) => {
    try {
      return api(`repos/{owner}/{repo}/actions/runs/${run.id}/jobs?per_page=100`).jobs;
    } catch {
      return null;
    }
  };
  const waitMs = (Number(env.CI_GREEN_WAIT_SECONDS) || 540) * 1000;
  const pollMs = (Number(env.CI_GREEN_POLL_SECONDS) || 20) * 1000;
  const deadline = startMs + waitMs;
  let rerunDone = false;
  let rerunFailed = false;

  for (;;) {
    let runs = [];
    let apiError = null;
    try {
      const page = api(`repos/{owner}/{repo}/actions/runs?head_sha=${sha}&per_page=100`);
      runs = page.workflow_runs;
      if (page.total_count > runs.length) {
        runs = [];
        apiError = `run list truncated (${page.total_count} runs, ${page.workflow_runs.length} returned)`;
      }
    } catch (e) {
      apiError = message(e);
    }
    clockStartMs = clockStart(pushedAtMs, runs);
    let verdict = classify({ runs, config: config.config, files, nowMs: now(), clockStartMs, apiError });
    let jobsByRun = {};
    let plan = [];
    if (verdict.state === "red") {
      for (const run of verdict.red) jobsByRun[run.id] = jobsOf(run);
      plan = planReruns(verdict.red, jobsByRun);
      if (plan.length && wait && !rerunFailed) {
        if (!rerunDone) {
          try {
            for (const cmd of plan) gh(cmd);
            rerunDone = true;
            out(`ci-green: infrastructure red on attempt 1; reran once (${plan.map((c) => c.join(" ")).join("; ")})`);
          } catch (e) {
            rerunFailed = true;
            err(`ci-green: rerun failed: ${message(e)}`);
          }
        }
        // The API can still show the first attempt for a moment after the rerun is accepted.
        if (rerunDone) verdict = { ...verdict, state: "pending", exit: EXIT.pending };
      }
    }
    const left = deadline - now();
    const stillWaiting = verdict.exit === EXIT.pending || (apiError && now() - clockStartMs < UNAVAILABLE_AFTER);
    if (wait && stillWaiting && left > 0) {
      sleep(Math.min(pollMs, left));
      continue;
    }
    if (apiError && wait && verdict.exit !== EXIT.unavailable) verdict = { ...verdict, state: "unavailable", exit: EXIT.unavailable, reason: apiError };

    const names = (paths) => paths.map((p) => basename(p)).join(", ");
    switch (verdict.state) {
      case "green": {
        const entries = [];
        for (const run of runs) {
          for (const job of testJobs(jobsOf(run) ?? [])) {
            let annotations = [];
            try {
              annotations = api(`repos/{owner}/{repo}/check-runs/${job.id}/annotations?per_page=100`);
            } catch {
              annotations = [];
            }
            entries.push({ job: { workflow: basename(run.path, ".yml"), name: job.name }, annotations });
          }
        }
        const report = retriesReport(entries);
        retried = report.retried;
        for (const line of report.lines) out(line);
        for (const run of verdict.rerunRuns) out(`rerun: ${basename(run.path)} needed attempt ${run.run_attempt}`);
        return finish("green", `green ${short} (${runs.length} runs)`);
      }
      case "red": {
        for (const run of verdict.red) {
          out(`red: ${basename(run.path)} ${run.conclusion} (run ${run.id}, attempt ${run.run_attempt})`);
          for (const job of failingJobs(jobsByRun[run.id] ?? [])) {
            for (const step of job.steps.length ? job.steps : ["(no step recorded)"]) out(`  failed: ${job.name} / ${step}`);
          }
          const log = quiet(() => gh(["run", "view", String(run.id), "--log-failed"]));
          for (const name of failedTests(log)) out(`  failed test: ${name}`);
          for (const line of logTail(log)) out(`  | ${line}`);
          const main_ = quiet(() => {
            const latest = api(`repos/{owner}/{repo}/actions/workflows/${basename(run.path)}/runs?branch=main&status=completed&per_page=1`).workflow_runs[0];
            return latest ? `${latest.conclusion} (${latest.head_sha.slice(0, 8)}, ${latest.created_at})` : "no completed run";
          }, "unreadable");
          out(`  main's latest ${basename(run.path)} run: ${main_}`);
        }
        if (plan.length && !wait) out(`ci-green: an infrastructure red; --wait would rerun once: ${plan.map((c) => c.join(" ")).join("; ")}`);
        return finish("red", `red ${short}`);
      }
      case "missing": {
        let prObject = null;
        try {
          prObject = api(`repos/{owner}/{repo}/pulls/${pr}`);
        } catch {
          prObject = null;
        }
        const note = missingNote(prObject);
        out(verdict.noRuns && !verdict.missing.length ? "missing: no workflow run exists on the SHA" : `missing: no run for ${names(verdict.missing)}`);
        if (note) out(note);
        return finish("missing", `missing ${short}`);
      }
      case "unavailable":
        return finish("unavailable", `unavailable (${verdict.reason}) ${short}`);
      default: {
        const waiting = [...verdict.pending.map((r) => basename(r.path)), ...verdict.missing.map((p) => `${basename(p)} (not started)`)];
        return finish("pending", `pending ${short}${waiting.length ? `: ${waiting.join(", ")}` : ": no workflow run yet"}`);
      }
    }
  }
}
