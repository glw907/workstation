// Tests ci-green's decision logic over recorded `gh api` output (tests/fixtures/ci-green/): the
// classifier's exit codes, the expected-set rules, the rerun plan, the retry print, the log reading,
// the CI wait record, and the command's whole flow with git and gh stubbed.
// Run with: node tests/ci-green.test.mjs
// Exits 0 with "ALL PASS" on success; prints failures and exits 1 otherwise.
//
// The fixtures are trimmed copies of real responses from glw907/cairn-cms. Three are derived from a
// recorded object and say so where they are built: the retries test jobs (the workflow step that
// emits the notice is not on the default branch yet), their annotations, and the extra run in the
// unexpected-workflow case.
import { readFileSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import assert from "node:assert/strict";
import * as lib from "../bin/.local/bin/ci-green-lib.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const FIX = join(HERE, "fixtures", "ci-green");
const text = (name) => readFileSync(join(FIX, name), "utf8");
const json = (name) => JSON.parse(text(name));
const runsOf = (name) => json(name).workflow_runs;

const config = lib.parseConfig(text("ci-green.json")).config;
const NONTOOL = ["src/lib/index.ts", "tool/cmd/main.go"];
const TOOL_ONLY = ["tool/cmd/main.go", "tool/internal/x.go"];
const MIN = 60_000;
const T0 = Date.parse("2026-10-10T12:00:00Z");

// Every stubbed command run writes its CI line here, never to the real records directory.
const SCRATCH = mkdtempSync(join(tmpdir(), "ci-green-scratch-"));

const failures = [];
const pending = [];
function check(name, fn) {
  pending.push({ name, fn });
}
const verdict = (input) => lib.classify({ config, files: NONTOOL, clockStartMs: T0, nowMs: T0 + 10 * MIN, ...input });

// ---- classifier: one case per state ----

check("green: a full run set on 8483ca5b exits 0", () => {
  const v = verdict({ runs: runsOf("runs-green-8483ca5b.json") });
  assert.equal(v.exit, 0);
  assert.equal(v.state, "green");
});

check("red: test.yml and tool.yml failing on 92325c02 exit 1 and name both", () => {
  const v = verdict({ runs: runsOf("runs-red-92325c02.json") });
  assert.equal(v.exit, 1);
  assert.deepEqual(v.red.map((r) => r.path).sort(), [".github/workflows/test.yml", ".github/workflows/tool.yml"]);
});

check("cancelled after a hang: run 37893646318 exits 1 and plans one job rerun", () => {
  const run = json("run-cancelled-37893646318.json");
  const v = verdict({ runs: [run] });
  assert.equal(v.exit, 1);
  const plan = lib.planReruns(v.red, { [run.id]: json("jobs-cancelled-37893646318.json").jobs });
  assert.deepEqual(plan, [["run", "rerun", "37893646318", "--job", "113699950701"]]);
});

check("tool workflows absent: 3ef9a8d9 with a non-tool diff exits 0", () => {
  const v = verdict({ runs: runsOf("runs-no-tool-3ef9a8d9.json") });
  assert.equal(v.exit, 0);
});

check("a file list over 300 files (PR 107) requires the five expected workflows", () => {
  const files = lib.parseNameOnly(text("pr-107-files.txt"));
  assert.ok(files.length > 300, `fixture holds ${files.length} files`);
  assert.deepEqual(lib.requiredWorkflows(config, files), config.expected);
  const v = verdict({ runs: runsOf("runs-no-tool-3ef9a8d9.json").slice(0, 3), files });
  assert.equal(v.exit, 2);
  assert.equal(v.missing.length, 2);
});

check("a red in a workflow no list names exits 1", () => {
  const runs = runsOf("runs-green-8483ca5b.json");
  // Derived: the recorded test run, re-pathed to a workflow the config does not mention.
  const stray = { ...runs[0], id: 1, path: ".github/workflows/stray.yml", conclusion: "failure" };
  const v = verdict({ runs: [...runs, stray] });
  assert.equal(v.exit, 1);
  assert.deepEqual(v.red.map((r) => r.path), [".github/workflows/stray.yml"]);
});

check("a rerun superseding a red exits 0 and reports the attempt above 1", () => {
  const v = verdict({ runs: runsOf("runs-rerun-b5953af8.json") });
  assert.equal(v.exit, 0);
  assert.deepEqual(v.rerunRuns.map((r) => [r.path, r.run_attempt]), [[".github/workflows/e2e.yml", 2]]);
});

check("pending: runs in progress exit 75, and 3 once the SHA is 60 minutes old", () => {
  const runs = runsOf("runs-pending-148ff15a.json");
  assert.equal(verdict({ runs }).exit, 75);
  assert.equal(verdict({ runs, nowMs: T0 + 61 * MIN }).exit, 3);
});

check("missing: no runs on a non-tool diff is 75 before 5 minutes and 2 after", () => {
  assert.equal(verdict({ runs: [], nowMs: T0 + 2 * MIN }).exit, 75);
  const v = verdict({ runs: [], nowMs: T0 + 6 * MIN });
  assert.equal(v.exit, 2);
  assert.deepEqual(v.missing, config.expected);
});

check("missing with a conflicted PR names the conflict", () => {
  const pr = json("pr-63-conflicted.json");
  assert.equal(pr.mergeable_state, "dirty");
  assert.match(lib.missingNote(pr), /merge conflict/);
  assert.equal(lib.missingNote(json("pr-110.json")), null);
});

check("unavailable: an API failure exits 3", () => {
  const v = verdict({ runs: [], apiError: "HTTP 502" });
  assert.equal(v.exit, 3);
  assert.equal(v.state, "unavailable");
});

check("a tool-only file list with zero runs exits 75, then 2 past 5 minutes, never 0", () => {
  assert.deepEqual(lib.requiredWorkflows(config, TOOL_ONLY), []);
  assert.equal(verdict({ runs: [], files: TOOL_ONLY, nowMs: T0 + 1 * MIN }).exit, 75);
  assert.equal(verdict({ runs: [], files: TOOL_ONLY, nowMs: T0 + 6 * MIN }).exit, 2);
});

check("an empty file list requires the expected set: one green run exits 75, then 2 past 5 minutes", () => {
  const one = runsOf("runs-green-8483ca5b.json").slice(0, 1);
  assert.deepEqual(lib.requiredWorkflows(config, []), config.expected);
  assert.equal(verdict({ runs: one, files: [], nowMs: T0 + 1 * MIN }).exit, 75);
  assert.equal(verdict({ runs: one, files: [], nowMs: T0 + 6 * MIN }).exit, 2);
});

check("a tool-only diff with only the tool workflow green exits 0", () => {
  const runs = runsOf("runs-green-8483ca5b.json").filter((r) => r.path.includes("tool"));
  assert.equal(verdict({ runs, files: TOOL_ONLY }).exit, 0);
});

check("a job skipped by its own if inside a successful run is not red", () => {
  const jobs = json("jobs-green-skipped-release-37997884859.json").jobs;
  assert.ok(jobs.some((j) => j.conclusion === "skipped"));
  assert.deepEqual(lib.failingJobs(jobs), []);
  assert.equal(verdict({ runs: runsOf("runs-green-8483ca5b.json") }).exit, 0);
});

check("the clock restarts at a rerun's start", () => {
  const runs = runsOf("runs-rerun-b5953af8.json");
  const rerunStart = Date.parse("2026-10-09T21:28:55Z");
  assert.equal(lib.clockStart(Date.parse("2026-10-09T21:00:00Z"), runs), rerunStart);
  assert.equal(lib.clockStart(Date.parse("2026-10-09T21:00:00Z"), runsOf("runs-green-8483ca5b.json")), Date.parse("2026-10-09T21:00:00Z"));
});

// ---- the config at the SHA ----

check("an absent or malformed ci-green.json is not ok", () => {
  assert.equal(lib.parseConfig(null).ok, false);
  assert.equal(lib.parseConfig("{not json").ok, false);
  assert.equal(lib.parseConfig('{"expected": "x"}').ok, false);
  assert.equal(lib.parseConfig('{"expected": [], "judgedWhenPresent": [], "neverOnPullRequest": []}').ok, false);
  assert.equal(lib.parseConfig('{"expected": [], "judgedWhenPresent": [], "neverOnPullRequest": [], "ignorePrefixes": []}').ok, false);
  assert.equal(lib.parseConfig(text("ci-green.json")).ok, true);
});

// ---- the rerun plan ----

check("an infra red on attempt 1 plans a rerun; on attempt 2 it is red", () => {
  const run = json("run-cancelled-37893646318.json");
  const jobs = { [run.id]: json("jobs-cancelled-37893646318.json").jobs };
  assert.equal(lib.planReruns([run], jobs).length, 1);
  assert.deepEqual(lib.planReruns([{ ...run, run_attempt: 2 }], jobs), []);
});

check("several cancelled jobs in one run plan a single --failed rerun", () => {
  const run = json("run-cancelled-37893646318.json");
  const base = json("jobs-cancelled-37893646318.json").jobs[0];
  // Derived: the recorded cancelled job, twice.
  const jobs = [base, { ...base, id: base.id + 1, name: "test 2" }];
  assert.deepEqual(lib.planReruns([run], { [run.id]: jobs }), [["run", "rerun", "37893646318", "--failed"]]);
});

check("a failure in a test step is not infra and plans nothing", () => {
  const run = runsOf("runs-red-92325c02.json").find((r) => r.id === 37898484811);
  const jobs = { [run.id]: json("jobs-red-test-37898484811.json").jobs };
  assert.deepEqual(lib.planReruns([run], jobs), []);
});

check("a failure in an install step reruns with --failed", () => {
  const run = runsOf("runs-red-92325c02.json").find((r) => r.id === 37898484811);
  const jobs = json("jobs-red-test-37898484811.json").jobs.map((j) => ({
    ...j,
    // Derived: the recorded failing step, renamed to the install step it would be in an infra red.
    steps: j.steps.map((s) => (s.conclusion === "failure" ? { ...s, name: "Run ./.github/actions/bounded-install" } : s)),
  }));
  assert.deepEqual(lib.planReruns([run], { [run.id]: jobs }), [["run", "rerun", "37898484811", "--failed"]]);
});

// ---- failure detail ----

check("failing jobs name their failing steps", () => {
  const failing = lib.failingJobs(json("jobs-red-tool-37898484804.json").jobs);
  assert.equal(failing.length, 3);
  assert.deepEqual(failing[0].steps, ["Run make -C tool check"]);
});

check("failed tests come from the summary block, not the flaky one", () => {
  const log = text("log-failed-e2e-38024099177.txt");
  assert.deepEqual(lib.failedTests(log), ["e2e/edit-save-failure.spec.ts:256:1 › a dictionary commit that never answers holds the save only until its deadline"]);
});

check("the log tail is capped, strips the job and timestamp prefix, and keeps the last lines", () => {
  const log = text("log-failed-e2e-38024099177.txt");
  const tail = lib.logTail(log, 4);
  assert.equal(tail.length, 4);
  assert.match(tail.at(-1), /Process completed with exit code 1/);
  assert.ok(!tail.some((l) => l.includes("UNKNOWN STEP")));
});

// ---- retries ----

// Derived: a test job as the retries step will leave it, built from a recorded job, plus one
// annotation per message built from a recorded annotation.
const testJob = (workflow, name, id) => ({
  workflow,
  id,
  name,
  steps: [{ name: "Run npm test", conclusion: "success" }, { name: "Report retried tests", conclusion: "success" }],
});
const annotationsFor = (message) => {
  const real = json("annotations-real.json");
  const notice = real.find((a) => a.annotation_level === "notice");
  return message === null ? real : [...real, { ...notice, title: "retries", message }];
};

check("a retries annotation naming one retried test prints that test", () => {
  const r = lib.retriesReport([{ job: testJob("test", "test", 1), annotations: annotationsFor("tests/a.test.ts > saves twice") }]);
  assert.deepEqual(r.retried, ["tests/a.test.ts > saves twice"]);
  assert.deepEqual(r.lines, ["retried: tests/a.test.ts > saves twice (test / test)"]);
});

check("a retries annotation reading none prints no retried test", () => {
  const r = lib.retriesReport([{ job: testJob("test", "test", 1), annotations: annotationsFor("none") }]);
  assert.deepEqual(r.retried, []);
  assert.deepEqual(r.lines, ["retried: none (test / test)"]);
});

check("an expected test job with no annotation prints retries not reported", () => {
  const r = lib.retriesReport([{ job: testJob("e2e", "e2e", 2), annotations: annotationsFor(null) }]);
  assert.deepEqual(r.lines, ["retries not reported (e2e / e2e)"]);
});

check("several names and an unreadable report both survive", () => {
  const r = lib.retriesReport([{ job: testJob("test", "test", 1), annotations: annotationsFor("a > b, c > d; unknown (vitest-component-retries.json is absent)") }]);
  assert.deepEqual(r.retried, ["a > b", "c > d"]);
  assert.match(r.lines[0], /unknown \(vitest-component-retries.json is absent\)/);
});

check("only a job with the retries step counts as a test job", () => {
  const jobs = json("jobs-cancelled-37893646318.json").jobs;
  assert.deepEqual(lib.testJobs(jobs), []);
  assert.deepEqual(lib.testJobs([{ ...jobs[0], steps: [...jobs[0].steps, { name: "Report retried tests" }] }]).length, 1);
});

// ---- the CI wait record ----

const withDir = (fn) => {
  const dir = mkdtempSync(join(tmpdir(), "ci-green-test-"));
  try {
    return fn(dir);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
};

check("a CI line lands in runs.jsonl with the shared fields", () =>
  withDir((dir) => {
    const rec = lib.ciRecord({
      sha: "8483ca5b", pr: 110, task: null, toplevel: "/w/cairn", branch: "gate-economy",
      startMs: T0, endMs: T0 + 90_000, queueSeconds: 12, outcome: "green", retried: ["a > b"],
    });
    const warnings = [];
    lib.appendRecord(dir, rec, { lockWait: 5, warn: (m) => warnings.push(m) });
    lib.appendRecord(dir, { ...rec, task: "4b" }, { lockWait: 5, warn: (m) => warnings.push(m) });
    assert.deepEqual(warnings, []);
    const lines = readFileSync(join(dir, "runs.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l));
    assert.equal(lines.length, 2);
    assert.deepEqual(lines[0], {
      kind: "ci", sha: "8483ca5b", pr: 110, task: null, toplevel: "/w/cairn", branch: "gate-economy",
      start: "2026-10-10T12:00:00Z", end: "2026-10-10T12:01:30Z", queueSeconds: 12, outcome: "green", retried: ["a > b"],
    });
    assert.equal(lines[1].task, "4b");
  }),
);

check("an unwritable records directory warns once and does not throw", () =>
  withDir((dir) => {
    const blocker = join(dir, "file");
    writeFileSync(blocker, "x");
    const warnings = [];
    lib.appendRecord(join(blocker, "sub"), { kind: "ci" }, { lockWait: 1, warn: (m) => warnings.push(m) });
    assert.equal(warnings.length, 1);
    assert.match(warnings[0], /record not written/);
  }),
);

// ---- the command, end to end with git and gh stubbed ----

function harness({ configText, files = ["src/lib/index.ts"], routes = {}, args }) {
  const out = [];
  const err = [];
  const calls = [];
  const sleeps = [];
  let now = T0 + 10 * MIN;
  const git = (a) => {
    const key = a.join(" ");
    calls.push(["git", key]);
    if (key.startsWith("fetch")) return "";
    if (key.startsWith("cat-file")) return "";
    if (key.startsWith("show -s --format=%cI")) return "2026-10-10T12:00:00Z\n";
    if (key.startsWith("show ") && key.includes(".github/ci-green.json")) {
      if (configText === null) throw new Error("fatal: path '.github/ci-green.json' does not exist");
      return configText;
    }
    if (key.startsWith("merge-base")) return "basesha\n";
    if (key.startsWith("diff --name-only")) return files.join("\n") + "\n";
    if (key.startsWith("rev-parse --show-toplevel")) return "/w/cairn\n";
    if (key.startsWith("branch --show-current")) return "gate-economy\n";
    throw new Error(`unstubbed git ${key}`);
  };
  const gh = (a) => {
    const key = a.join(" ");
    calls.push(["gh", key]);
    for (const [pattern, reply] of Object.entries(routes)) {
      if (key.includes(pattern)) {
        if (reply instanceof Error) throw reply;
        return typeof reply === "string" ? reply : JSON.stringify(reply);
      }
    }
    throw new Error(`unstubbed gh ${key}`);
  };
  const deps = {
    git, gh, out: (s) => out.push(s), err: (s) => err.push(s),
    now: () => now, sleep: (ms) => { sleeps.push(ms); now += ms; },
    env: { CAIRN_GATE_RECORDS_DIR: SCRATCH },
  };
  return { deps, out, err, calls, sleeps, args, run: () => lib.main(args, deps) };
}

check("main exits 3 naming ci-green.json when the file is absent at the SHA", () =>
  withDir((dir) => {
    const h = harness({ configText: null, args: ["abc123", "--pr", "110", "--wait"] });
    h.deps.env.CAIRN_GATE_RECORDS_DIR = dir;
    assert.equal(h.run(), 3);
    assert.match(h.out.join("\n") + h.err.join("\n"), /\.github\/ci-green\.json/);
    const rec = JSON.parse(readFileSync(join(dir, "runs.jsonl"), "utf8").trim());
    assert.equal(rec.outcome, "unavailable");
  }),
);

check("main exits 3 naming ci-green.json when the file is malformed", () => {
  const h = harness({ configText: "{oops", args: ["abc123", "--pr", "110"] });
  assert.equal(h.run(), 3);
  assert.match(h.out.join("\n") + h.err.join("\n"), /\.github\/ci-green\.json/);
});

check("main exits 0 on green, prints retries, and appends a CI line under --wait", () =>
  withDir((dir) => {
    const runs = json("runs-green-8483ca5b.json");
    const testRun = runs.workflow_runs.find((r) => r.path.endsWith("/test.yml"));
    const jobsFor = (run) => ({
      total_count: 1,
      jobs: [{ id: run.id + 1, run_id: run.id, name: run.name, status: "completed", conclusion: "success", steps: [{ name: "Report retried tests", conclusion: "success" }] }],
    });
    const routes = { "actions/runs?head_sha": runs };
    for (const r of runs.workflow_runs) {
      routes[`actions/runs/${r.id}/jobs`] = r === testRun ? jobsFor(r) : { total_count: 0, jobs: [] };
    }
    routes[`check-runs/${testRun.id + 1}/annotations`] = annotationsFor("tests/a.test.ts > saves twice");
    const h = harness({ configText: text("ci-green.json"), routes, args: ["8483ca5b", "--pr", "110", "--wait", "--task", "4b"] });
    h.deps.env.CAIRN_GATE_RECORDS_DIR = dir;
    assert.equal(h.run(), 0);
    const printed = h.out.join("\n");
    assert.match(printed, /retried: tests\/a\.test\.ts > saves twice/);
    const rec = JSON.parse(readFileSync(join(dir, "runs.jsonl"), "utf8").trim());
    assert.equal(rec.kind, "ci");
    assert.equal(rec.task, "4b");
    assert.equal(rec.pr, 110);
    assert.equal(rec.outcome, "green");
    assert.deepEqual(rec.retried, ["tests/a.test.ts > saves twice"]);
    assert.equal(rec.toplevel, "/w/cairn");
  }),
);

check("main under --wait reruns an infra red once, then polls", () => {
  const run = json("run-cancelled-37893646318.json");
  const calls = [];
  const routes = {
    "actions/runs?head_sha": { total_count: 1, workflow_runs: [run] },
    [`actions/runs/${run.id}/jobs`]: json("jobs-cancelled-37893646318.json"),
    "run rerun": "",
    "run view": "",
    "workflows/test.yml/runs": json("runs-main-test.json"),
  };
  const h = harness({ configText: text("ci-green.json"), routes, args: ["092176c1", "--pr", "110", "--wait"] });
  const start = h.deps.now();
  const code = h.run();
  calls.push(...h.calls.filter(([k, c]) => k === "gh" && c.startsWith("run rerun")).map(([, c]) => c));
  assert.deepEqual(calls, ["run rerun 37893646318 --job 113699950701"]);
  assert.equal(code, 75);
  assert.ok(h.deps.now() - start <= 540_000 + 20_000, "the wait stays inside its budget");
});

check("main prints an unrerunnable red's failing job, step, test, log tail and main's conclusion", () => {
  const run = runsOf("runs-red-92325c02.json").find((r) => r.id === 37898484811);
  const routes = {
    "actions/runs?head_sha": { total_count: 1, workflow_runs: [run] },
    [`actions/runs/${run.id}/jobs`]: json("jobs-red-test-37898484811.json"),
    "run view": text("log-failed-e2e-38024099177.txt"),
    "workflows/test.yml/runs": json("runs-main-test.json"),
  };
  const h = harness({ configText: text("ci-green.json"), routes, args: ["92325c02", "--pr", "110"] });
  assert.equal(h.run(), 1);
  const printed = h.out.join("\n");
  assert.match(printed, /test \/ Run npm run check:template/);
  assert.match(printed, /edit-save-failure\.spec\.ts:256:1/);
  assert.match(printed, /main's latest test\.yml run: success/);
});

check("main exits 3 when the API stays down", () => {
  const h = harness({ configText: text("ci-green.json"), routes: { "actions/runs?head_sha": new Error("HTTP 502") }, args: ["abc123", "--pr", "110"] });
  assert.equal(h.run(), 3);
});

check("main exits 75 past the wait budget while runs are pending", () => {
  const h = harness({
    configText: text("ci-green.json"),
    routes: { "actions/runs?head_sha": json("runs-pending-148ff15a.json") },
    args: ["148ff15a", "--pr", "110", "--wait"],
  });
  assert.equal(h.run(), 75);
  assert.ok(h.sleeps.length > 0);
  assert.ok(h.sleeps.reduce((a, b) => a + b, 0) <= 540_000 + 20_000);
});

check("main exits 3 when the run list is truncated by the page size", () => {
  const runs = json("runs-green-8483ca5b.json");
  const h = harness({
    configText: text("ci-green.json"),
    routes: { "actions/runs?head_sha": { ...runs, total_count: runs.workflow_runs.length + 50 } },
    args: ["8483ca5b", "--pr", "110"],
  });
  assert.equal(h.run(), 3);
  assert.match(h.out.join("\n"), /truncated/);
});

check("queueSeconds counts from the push, not from a rerun's restarted clock", () =>
  withDir((dir) => {
    const runs = json("runs-rerun-b5953af8.json");
    const h = harness({ configText: text("ci-green.json"), routes: { "actions/runs?head_sha": runs, "/jobs": { jobs: [] } }, args: ["b5953af8", "--pr", "110", "--wait", "--pushed-at", "2026-10-09T21:00:00Z"] });
    h.deps.env.CAIRN_GATE_RECORDS_DIR = dir;
    h.deps.now = () => Date.parse("2026-10-09T21:40:00Z");
    assert.equal(h.run(), 0);
    const rec = JSON.parse(readFileSync(join(dir, "runs.jsonl"), "utf8").trim());
    assert.equal(rec.queueSeconds, 40 * 60);
  }),
);

check("main rejects a missing --pr", () => {
  const h = harness({ configText: text("ci-green.json"), args: ["abc123"] });
  assert.equal(h.run(), 3);
  assert.match(h.err.join("\n"), /usage/i);
});

// ---- run ----

for (const { name, fn } of pending) {
  try {
    await fn();
  } catch (e) {
    failures.push(`FAIL ${name}\n  ${String(e.message).split("\n").join("\n  ")}`);
  }
}
rmSync(SCRATCH, { recursive: true, force: true });
if (failures.length) {
  console.error(failures.join("\n"));
  console.error(`${failures.length} of ${pending.length} failed`);
  process.exit(1);
}
console.log(`ALL PASS (${pending.length})`);
