// Fixture harness for docs-page-chain-v2.js (docs reset pass 1, Task 9).
//
// The Workflow tool executes a workflow script's body as an async function whose free
// variables (`args`, `agent`, `parallel`, `phase`, `log`, `budget`, `workflow`) are supplied by
// the host; the file itself carries a top-level `export const meta = {...}` (parsed separately,
// as a pure literal, for the permission dialog) and top-level `await`/`return` (valid inside that
// function wrapper, not inside a real ES module). This harness reproduces that shape well enough
// to exercise the script's logic: it strips the `export ` keyword and runs the remainder as an
// `AsyncFunction` body, with `agent()` stubbed to return canned responses keyed by label.
//
// Every stubbed structured return is validated against the schema the script passed, so a stub
// cannot invent a shape the real agent could not return. Stage-2 fixtures never hand-build a
// handoff: they run stage 1 against stubs, capture the exact handoff JSON the write agent was
// told to write, and feed that into stage 2's load.
//
// Run with: node docs-page-chain-v2.fixture.test.mjs
// Exits 0 with "ALL PASS" on success, prints failures and exits 1 otherwise. No dependencies
// beyond the Node runtime (this repo has no package.json / test runner to plug into).

import { readFileSync, writeFileSync, mkdtempSync, existsSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import assert from "node:assert/strict";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC_PATH = join(HERE, "docs-page-chain-v2.js");
const SRC = readFileSync(SRC_PATH, "utf8");

const failures = [];
const tempDirs = [];
function fail(name, e) {
  failures.push(name);
  console.log(`FAIL - ${name}`);
  console.log(`  ${e && e.stack || e}`);
}
function check(name, fn) {
  try {
    fn();
    console.log(`ok - ${name}`);
  } catch (e) {
    fail(name, e);
  }
}
async function checkAsync(name, fn) {
  try {
    await fn();
    console.log(`ok - ${name}`);
  } catch (e) {
    fail(name, e);
  }
}

// ---------------------------------------------------------------------------------------------
// Static checks against the source text.
// ---------------------------------------------------------------------------------------------

check("v2 source's page gate names check:provenance", () => {
  assert.match(SRC, /check:provenance/);
  assert.match(SRC, /const gateFor = \(p\) => \{[\s\S]*?check:provenance[\s\S]*?\};/);
});

check("v2 source names no profile-grader agent", () => {
  assert.doesNotMatch(SRC, /graderPrompt/);
  assert.doesNotMatch(SRC, /GRADER_SCHEMA/);
  assert.doesNotMatch(SRC, /label: `grader:/);
  assert.doesNotMatch(SRC, /agentType: "general-purpose", schema: GRADER/);
});

check("every v1 gate also appears in v2 (the cairn-run-gate page-gate line)", () => {
  const v1 = readFileSync(join(HERE, "docs-page-chain.js"), "utf8");
  const v1GateLines = [...v1.matchAll(/\$\{LANE\}cairn-run-gate '\$\{gateFor\(p\)\}'/g)];
  assert.ok(v1GateLines.length >= 1, "v1 has no cairn-run-gate page-gate line to compare against");
  assert.match(SRC, /\$\{LANE\}cairn-run-gate '\$\{gateFor\(p\)\}'/);
});

check("v2 keeps the fact read (only the profile grader is removed)", () => {
  assert.match(SRC, /function factPrompt\(p, filed\)/);
  assert.match(SRC, /READ_SCHEMA/);
  assert.match(SRC, /label: `fact:\$\{p\.id\}`/);
});

check("the header documents struck findings, the reader batch shape, the job-id prefix, and track", () => {
  assert.match(SRC, /"struck": true/);
  assert.match(SRC, /struckReaderFindings/);
  assert.match(SRC, /scripts\/docs-readers\/run\.ts <batch\.json> --out/);
  assert.match(SRC, /<pageId>--<n>/);
  assert.match(SRC, /track: "admin"/);
});

// ---------------------------------------------------------------------------------------------
// A minimal JSON Schema validator (the subset the script's schemas use).
// ---------------------------------------------------------------------------------------------

function validate(schema, value, where = "$") {
  const errs = [];
  const t = schema.type;
  const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
  if (t === "object" && !isObj(value)) return [`${where}: not an object`];
  if (t === "array" && !Array.isArray(value)) return [`${where}: not an array`];
  if (t === "string" && typeof value !== "string") return [`${where}: not a string`];
  if (t === "boolean" && typeof value !== "boolean") return [`${where}: not a boolean`];
  if (schema.enum && !schema.enum.includes(value)) errs.push(`${where}: ${JSON.stringify(value)} not in enum`);
  if (t === "object") {
    for (const k of schema.required || []) if (!(k in value)) errs.push(`${where}: missing ${k}`);
    for (const [k, v] of Object.entries(value)) {
      if (schema.properties && schema.properties[k]) errs.push(...validate(schema.properties[k], v, `${where}.${k}`));
      else if (schema.additionalProperties === false) errs.push(`${where}: unexpected ${k}`);
    }
  }
  if (t === "array" && schema.items) value.forEach((v, i) => errs.push(...validate(schema.items, v, `${where}[${i}]`)));
  return errs;
}

// ---------------------------------------------------------------------------------------------
// Load the script body as a callable async function, `agent()` stubbed.
// ---------------------------------------------------------------------------------------------

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const body = SRC.replace(/^export const meta/m, "const meta");
const run = new AsyncFunction("args", "agent", "parallel", "phase", "log", "budget", "workflow", body);

function stubHarness(agentImpl) {
  const calls = [];
  const agent = async (prompt, opts) => {
    calls.push({ prompt, opts });
    const out = await agentImpl(prompt, opts, calls.length);
    if (out && opts.schema) {
      const errs = validate(opts.schema, out);
      if (errs.length) throw new Error(`stub for ${opts.label} violates its schema: ${errs.join("; ")}`);
    }
    return out;
  };
  // Like the real parallel(): a thunk that throws resolves to null. The harness surfaces the
  // error so a failing assertion inside a stub is never swallowed silently.
  const thrown = [];
  const parallel = async (thunks) => Promise.all(thunks.map((t) => t().catch((e) => { thrown.push(e); return null; })));
  const logs = [];
  const phase = () => {};
  const log = (m) => logs.push(m);
  const budget = { total: null, spent: () => 0, remaining: () => Infinity };
  const workflow = async () => { throw new Error("nesting not used by this script"); };
  return { agent, parallel, phase, log, budget, workflow, calls, logs, thrown };
}
async function go(a, h) {
  const out = await run(a, h.agent, h.parallel, h.phase, h.log, h.budget, h.workflow);
  if (h.thrown.length) throw h.thrown[0];
  return out;
}
const labelled = (h, prefix) => h.calls.filter((c) => c.opts.label && c.opts.label.startsWith(prefix));

const EXEMPLAR_TEXT = "# Check your site\n\nRun one command. It prints a verdict.";
const PAGE = {
  id: "is-it-working",
  path: "docs/admin/is-it-working.md",
  track: "admin",
  brief: "Explain cairn doctor to a site operator who has never opened a terminal log.",
  inputs: ["docs/superpowers/plans/x.mining.md#is-it-working"],
  exemplars: [{ path: "docs/admin/other.md", text: EXEMPLAR_TEXT }],
  pinned: ["#check-your-site"],
  extraChecks: ["The page names the exit code a green verdict returns."]
};

const BASE_ARGS = {
  worktree: "/tmp/wt",
  gate: "npm run check:docs",
  toolGate: "make -C /tmp/wt/tool check",
  profile: "The admin track profile, verbatim.",
  runId: "Fixture Run/9"
};

const EDITOR_FINDINGS = [
  { location: "para 2", finding: "missing a failure mode", blocking: true, rewrite: "add it" },
  { location: "para 4", finding: "a tricolon", blocking: false, rewrite: "cut to one item" }
];
const FACT_FINDINGS = [{ location: "para 3", finding: "composed from two manifest entries no source states together", blocking: true }];
const CLEAN_EDITOR = (jobs = []) => ({ verdict: "accept", findings: [], omissions: [], readerJobs: jobs, summary: "clean" });
const CLEAN_FACT = { verdict: "accept", findings: [], retagged: [], leftCandidate: [], summary: "clean" };
const GATE_PASS = { gate: "pass", gateCommand: "cairn-run-gate '...'", gateTail: "gate exit: 0" };
const JOB = (id) => ({ id, class: "docs-and-binary", arrival: "Your site stopped updating.", task: "run cairn doctor", doneSignal: "it prints a verdict" });

// Stage-1 stubs. `over` replaces a label's response.
function stage1Stubs(over = {}) {
  return (prompt, opts) => {
    if (opts.label in over) return over[opts.label];
    if (opts.label === `draft:${PAGE.id}`) return { path: PAGE.path, bulletsFiled: [] };
    if (opts.label === `gate:${PAGE.id}`) return GATE_PASS;
    if (opts.label === `editor:${PAGE.id}`) {
      return {
        verdict: "fix",
        findings: EDITOR_FINDINGS,
        omissions: [
          { item: "version and platform scope", status: "missing", evidence: "no version line" },
          { item: "where the reader goes next", status: "present", evidence: "See next steps" }
        ],
        readerJobs: [JOB("r1")],
        summary: "two findings, one omission"
      };
    }
    if (opts.label === `fact:${PAGE.id}`) return { verdict: "fix", findings: FACT_FINDINGS, retagged: [], leftCandidate: [], summary: "one blocking" };
    if (opts.label === "handoff-write") return { path: "/home/u/.cache/docs-page-chain/handoffs/fixture-run-9-20260923-120000.json" };
    throw new Error(`unexpected stage-1 agent call: ${opts.label}`);
  };
}

// Run stage 1 against stubs and capture the exact handoff the write agent was told to write.
async function runStage1(over = {}) {
  const h = stubHarness(stage1Stubs(over));
  const result = await go({ ...BASE_ARGS, stage: 1, pages: [PAGE] }, h);
  const write = h.calls.find((c) => c.opts.label === "handoff-write");
  const m = write.prompt.match(/BEGIN HANDOFF JSON\n([\s\S]*?)\nEND HANDOFF JSON/);
  assert.ok(m, "the handoff-write prompt carries the JSON between its markers");
  return { h, result, handoff: JSON.parse(m[1]), writePrompt: write.prompt };
}

// A results directory shaped like the runner's (`report.json` is a BatchReport), on disk; the
// load-reader-results stub follows its prompt's own instructions against it.
function writeResultsDir(jobs, { reverified } = {}) {
  const dir = mkdtempSync(join(tmpdir(), "dpc-v2-results-"));
  tempDirs.push(dir);
  const usage = { input: 1, output: 1, cacheCreation: 0, cacheRead: 0, counted: 2 };
  const job = (j) => ({
    id: j.id, class: "docs-only", model: "claude-opus-5-5", outcome: j.outcome,
    ...(j.abortReason ? { abortReason: j.abortReason } : {}),
    stalls: j.stalls || [], assumed: j.assumed || [], pagesRead: [PAGE.path], quotes: [], checks: [],
    ruleCandidates: [], denials: [], proxyBlocked: [], packageFetches: [], usage,
    verified: { ok: j.ok, init: true, canaries: true, quotes: [], problems: j.ok ? [] : ["quote did not match"] }
  });
  const report = (js) => ({ batch: "fixture", runId: "r", stopReason: "complete", budgetTokens: 1000, usage, jobs: js.map(job), verified: true });
  writeFileSync(join(dir, "report.json"), JSON.stringify(report(jobs)));
  if (reverified) writeFileSync(join(dir, "report.reverified.json"), JSON.stringify(report(reverified)));
  return dir;
}
function loadResultsLikeTheAgent(prompt, dir) {
  assert.ok(prompt.includes(dir), "the loader is pointed at the results dir");
  assert.ok(prompt.indexOf("report.reverified.json") < prompt.indexOf("otherwise read"), "the reverified report is preferred");
  const src = existsSync(join(dir, "report.reverified.json")) ? "report.reverified.json" : existsSync(join(dir, "report.json")) ? "report.json" : "missing";
  if (src === "missing") return { source: src, jobs: [] };
  const rep = JSON.parse(readFileSync(join(dir, src), "utf8"));
  return {
    source: src,
    jobs: rep.jobs.map((j) => ({
      id: j.id, outcome: j.outcome, ...(j.abortReason ? { abortReason: j.abortReason } : {}),
      stalls: j.stalls, assumed: j.assumed, verifiedOk: j.verified.ok, verifiedProblems: j.verified.problems
    }))
  };
}

// Stage-2 stubs over a captured handoff and a real-shaped results dir.
function stage2Stubs(handoff, dir, over = {}) {
  return (prompt, opts) => {
    if (opts.label in over) return typeof over[opts.label] === "function" ? over[opts.label](prompt, opts) : over[opts.label];
    if (opts.label === "load-handoff") return { pages: handoff.pages };
    if (opts.label === "load-reader-results") return loadResultsLikeTheAgent(prompt, dir);
    if (opts.label.startsWith("redraft:")) return { path: PAGE.path, bulletsFiled: [] };
    if (opts.label.startsWith("regate:")) return GATE_PASS;
    throw new Error(`unexpected stage-2 agent call: ${opts.label}`);
  };
}
// An applied read that answers every id it was shown: "applied", or the status in `overrides`;
// ids in `drop` are left out.
function appliedAll(overrides = {}, drop = []) {
  return (prompt) => {
    const ids = [...prompt.matchAll(/^- \[([a-z0-9-]+)\] \[/gm)].map((m) => m[1]).filter((id) => !drop.includes(id));
    return {
      perFinding: ids.map((id) => ({ id, status: overrides[id] || "applied", evidence: "checked" })),
      newIssues: [],
      retagged: [],
      leftCandidate: [],
      summary: "graded"
    };
  };
}
const S2 = (extra) => ({ ...BASE_ARGS, stage: 2, handoffPath: "/home/u/.cache/docs-page-chain/handoffs/x.json", ...extra });
const APPLIED = `applied:${PAGE.id}`;

// ---------------------------------------------------------------------------------------------
// Stage 1.
// ---------------------------------------------------------------------------------------------

await checkAsync("stage 1: fact read runs; editor prompt carries the omission checklist, extraChecks, and reader-job request; drafter gets exemplars in <example> tags", async () => {
  const { h, result, handoff, writePrompt } = await runStage1();
  const draft = labelled(h, "draft:")[0].prompt;
  assert.match(draft, /<example path="docs\/admin\/other\.md">\n# Check your site/);
  assert.match(draft, /docs\/internal\/briefs\/admin\/is-it-working\.json/);
  const editor = labelled(h, "editor:")[0].prompt;
  for (const re of [/Every prerequisite the reader needs/, /Every value the reader must supply themselves/, /Every failure a step on this page can produce/, /version and platform scope/, /where the reader goes next/i, /readerJobs/, /arrival/]) assert.match(editor, re);
  assert.match(editor, /names the exit code a green verdict returns/, "extraChecks reach the editor");
  assert.equal(labelled(h, "fact:").length, 1);
  assert.match(labelled(h, "fact:")[0].prompt, /joining two neighboring manifest entries/);
  // handoff path: sanitized runId plus a shell-resolved stamp, under the cache, never the worktree
  assert.match(writePrompt, /XDG_CACHE_HOME/);
  assert.match(writePrompt, /docs-page-chain\/handoffs\/fixture-run-9-STAMP\.json/);
  assert.match(writePrompt, /date -u \+%Y%m%d-%H%M%S/);
  assert.match(writePrompt, /never overwrite a handoff/);
  assert.doesNotMatch(writePrompt, /\/tmp\/wt\/docs-page-chain\/handoffs/);
  assert.equal(result.handoffPath, "/home/u/.cache/docs-page-chain/handoffs/fixture-run-9-20260923-120000.json");
  assert.equal(result.pages[0].status, "handed-off");
  assert.equal(result.readerJobCount, 1);
  // the handoff carries the page args verbatim and stable finding ids
  const hp = handoff.pages[0];
  assert.equal(handoff.runId, "fixture-run-9");
  for (const k of ["brief", "inputs", "exemplars", "pinned", "extraChecks", "track"]) assert.deepEqual(hp[k], PAGE[k], `handoff page carries ${k}`);
  assert.deepEqual(hp.findings.map((f) => f.id), ["ed-1", "ed-2", "fact-1", "om-1"]);
  assert.ok(hp.findings.every((f) => f.struck === false));
  assert.deepEqual(hp.readerJobs.map((j) => j.id), ["is-it-working--1"]);
  assert.match(hp.readerJobs[0].id, /^[a-z0-9][a-z0-9-]*$/, "the job id passes the runner's id pattern");
});

await checkAsync("stage 1: the captured handoff satisfies stage 2's strict load schema, which rejects a dropped or invented field", async () => {
  const { handoff } = await runStage1();
  const dir = writeResultsDir([]);
  const h = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll() }));
  await go(S2({ resultsDir: dir }), h);   // the stub harness validates load-handoff's return
  const loadSchema = h.calls.find((c) => c.opts.label === "load-handoff").opts.schema;
  const noBrief = { ...handoff.pages[0] };
  delete noBrief.brief;
  assert.ok(validate(loadSchema, { pages: [noBrief] }).length > 0, "a page missing its brief fails the load schema");
  assert.ok(validate(loadSchema, { pages: [{ ...handoff.pages[0], summary: "x" }] }).length > 0, "an extra field fails the load schema");
});

await checkAsync("stage 1 rejects a page id containing `--`", async () => {
  const h = stubHarness(stage1Stubs());
  await assert.rejects(go({ ...BASE_ARGS, stage: 1, pages: [{ ...PAGE, id: "a--b" }] }, h), /no `--`/);
});

// ---------------------------------------------------------------------------------------------
// Stage 2, always fed stage 1's captured handoff.
// ---------------------------------------------------------------------------------------------

await checkAsync("finding 1: stage 2 rebuilds the page from the handoff (brief, inputs, exemplars, pinned -> TOOL_GATE)", async () => {
  const { handoff } = await runStage1();
  const dir = writeResultsDir([]);
  const h = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll() }));
  await go(S2({ resultsDir: dir }), h);
  const redraft = labelled(h, "redraft:")[0].prompt;
  assert.doesNotMatch(redraft, /undefined/);
  assert.ok(redraft.includes(`The brief, verbatim:\n\n${PAGE.brief}`));
  assert.match(redraft, /- docs\/superpowers\/plans\/x\.mining\.md#is-it-working/);
  assert.match(redraft, /<example path="docs\/admin\/other\.md">/);
  assert.match(redraft, /#check-your-site/);
  assert.match(labelled(h, "regate:")[0].prompt, /make -C \/tmp\/wt\/tool check/, "a pinned page keeps the tool gate on the redraft's gate");
});

await checkAsync("the redraft applies every finding (advisory and fact read included) plus verified reader defects; a blocking finding not applied escalates without a third round", async () => {
  const { handoff } = await runStage1();
  const dir = writeResultsDir([{ id: "is-it-working--1", outcome: "stalled", stalls: ["the doctor command in step 3 fails as written"], ok: true }]);
  const h = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll({ "ed-1": "not applied" }) }));
  const result = await go(S2({ resultsDir: dir }), h);
  const redraft = labelled(h, "redraft:")[0].prompt;
  assert.match(redraft, /applying every finding below, blocking or advisory/);
  assert.match(redraft, /\[ed-2\] \[advisory\].*a tricolon/);
  assert.match(redraft, /\[fact-1\] \[BLOCKING\] \(fact read\).*composed from two manifest entries/);
  assert.match(redraft, /\[om-1\] \[BLOCKING\] \(omission checklist\)/);
  assert.match(redraft, /\[rd-is-it-working--1-outcome\]/);
  assert.match(redraft, /\[rd-is-it-working--1-stall-1\].*doctor command in step 3 fails/);
  const applied = labelled(h, "applied:")[0].prompt;
  assert.match(applied, /composed from two manifest entries/, "the fact read's finding reaches the applied read");
  assert.match(applied, /rd-is-it-working--1-stall-1/);
  const p = result.pages[0];
  assert.equal(p.status, "escalate");
  assert.deepEqual(p.unresolved.map((u) => u.id), ["ed-1"]);
  assert.equal(labelled(h, "redraft:").length, 1, "exactly one redraft round (the two-round cap)");
  assert.equal(labelled(h, "applied:").length, 1);
});

await checkAsync("finding 2: a red stage-1 gate with no findings is redrafted with its tail, not accepted; a red redraft gate escalates", async () => {
  const { handoff } = await runStage1({
    [`gate:${PAGE.id}`]: { gate: "fail", gateCommand: "cairn-run-gate 'x'", gateTail: "check:provenance: sentence 4 has no fact id" },
    [`editor:${PAGE.id}`]: CLEAN_EDITOR(),
    [`fact:${PAGE.id}`]: CLEAN_FACT
  });
  assert.deepEqual(handoff.pages[0].findings.map((f) => f.id), ["gate"]);
  handoff.pages[0].findings[0].struck = true;   // the gate finding ignores a strike
  const dir = writeResultsDir([]);
  const h = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll() }));
  const result = await go(S2({ resultsDir: dir }), h);
  assert.equal(labelled(h, "redraft:").length, 1, "a red gate is grounds for a redraft");
  assert.match(labelled(h, "redraft:")[0].prompt, /\[gate\] \[BLOCKING\] \(page gate\)[\s\S]*check:provenance: sentence 4 has no fact id/);
  assert.equal(result.pages[0].status, "accepted", "accepted once the redraft's gate passes");

  const h2 = stubHarness(stage2Stubs(handoff, dir, {
    [`regate:${PAGE.id}`]: { gate: "fail", gateCommand: "x", gateTail: "red" },
    [APPLIED]: appliedAll()
  }));
  assert.equal((await go(S2({ resultsDir: dir }), h2)).pages[0].status, "escalate");
});

await checkAsync("finding 5: an applied read that omits a blocking finding escalates (an omitted advisory one does not)", async () => {
  const { handoff } = await runStage1();
  const dir = writeResultsDir([]);
  const h = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll({}, ["fact-1"]) }));
  const result = await go(S2({ resultsDir: dir }), h);
  assert.equal(result.pages[0].status, "escalate");
  assert.deepEqual(result.pages[0].omitted, ["fact-1"]);
  const h2 = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll({}, ["ed-2"]) }));
  assert.equal((await go(S2({ resultsDir: dir }), h2)).pages[0].status, "accepted");
});

await checkAsync("finding 5: the script's own blocking flag decides, not the read's", async () => {
  const { handoff } = await runStage1();
  const dir = writeResultsDir([]);
  const h = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll({ "om-1": "applied wrongly" }) }));
  const result = await go(S2({ resultsDir: dir }), h);
  assert.equal(result.pages[0].status, "escalate");
  assert.deepEqual(result.pages[0].unresolved.map((u) => u.id), ["om-1"]);
});

await checkAsync("finding 6: struck findings (handoff and reader) are filtered from the redraft and the applied read", async () => {
  const { handoff } = await runStage1();
  handoff.pages[0].findings.find((f) => f.id === "fact-1").struck = true;
  handoff.pages[0].struckReaderFindings = ["rd-is-it-working--1-stall-1"];
  const dir = writeResultsDir([{ id: "is-it-working--1", outcome: "done", stalls: ["a stall the conductor ruled out"], ok: true }]);
  const h = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll() }));
  const result = await go(S2({ resultsDir: dir }), h);
  for (const label of ["redraft:", "applied:"]) {
    const prompt = labelled(h, label)[0].prompt;
    assert.doesNotMatch(prompt, /composed from two manifest entries/, `${label} drops the struck fact finding`);
    assert.doesNotMatch(prompt, /conductor ruled out/, `${label} drops the struck reader defect`);
    assert.match(prompt, /\[ed-1\]/);
  }
  assert.equal(result.pages[0].status, "accepted");
  assert.match(result.pages[0].note, /2 struck finding/);
});

await checkAsync("finding 4: a real-shaped results dir; unverified jobs excluded, a clean done job yields no blocking finding", async () => {
  const { handoff } = await runStage1({ [`editor:${PAGE.id}`]: CLEAN_EDITOR([JOB("a"), JOB("b")]), [`fact:${PAGE.id}`]: CLEAN_FACT });
  const dir = writeResultsDir([
    { id: "is-it-working--1", outcome: "done", ok: true },
    { id: "is-it-working--2", outcome: "stalled", stalls: ["could not find the command"], assumed: ["guessed the flag"], ok: false },
    { id: "other-page--1", outcome: "done", ok: true }
  ]);
  const h = stubHarness(stage2Stubs(handoff, dir));
  const result = await go(S2({ resultsDir: dir }), h);
  assert.equal(result.readerSource, "report.json");
  assert.equal(labelled(h, "redraft:").length, 0, "a clean done job and an unverified job give no redraft");
  assert.equal(result.pages[0].status, "accepted");
  assert.match(result.pages[0].note, /1 unverified reader run/);
  assert.deepEqual(result.orphanReaderJobs, ["other-page--1"]);
});

await checkAsync("finding 4: report.reverified.json is preferred, and its verified defects become findings", async () => {
  const { handoff } = await runStage1({ [`editor:${PAGE.id}`]: CLEAN_EDITOR([JOB("a")]), [`fact:${PAGE.id}`]: CLEAN_FACT });
  const dir = writeResultsDir(
    [{ id: "is-it-working--1", outcome: "done", ok: false }],
    { reverified: [{ id: "is-it-working--1", outcome: "aborted", abortReason: "timeout", assumed: ["the site was deployed"], ok: true }] }
  );
  const h = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll({ "rd-is-it-working--1-assumed-1": "not applied" }) }));
  const result = await go(S2({ resultsDir: dir }), h);
  assert.equal(result.readerSource, "report.reverified.json");
  const redraft = labelled(h, "redraft:")[0].prompt;
  assert.match(redraft, /\[rd-is-it-working--1-outcome\].*ended "aborted" \(timeout\)/);
  assert.match(redraft, /\[rd-is-it-working--1-assumed-1\].*the site was deployed/);
  assert.equal(result.pages[0].status, "escalate");
});

await checkAsync("finding 4: stage 2 requires an absolute resultsDir", async () => {
  const h = stubHarness(() => { throw new Error("no agent should run"); });
  await assert.rejects(go(S2({}), h), /absolute path/);
  await assert.rejects(go(S2({ resultsDir: "results/x" }), h), /absolute path/);
});

await checkAsync("finding 3: extraChecks reach the editor prompt and, through the handoff, the applied read", async () => {
  const { h: h1, handoff } = await runStage1();
  assert.match(labelled(h1, "editor:")[0].prompt, /names the exit code a green verdict returns/);
  const dir = writeResultsDir([]);
  const h = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll() }));
  await go(S2({ resultsDir: dir }), h);
  assert.match(labelled(h, "applied:")[0].prompt, /names the exit code a green verdict returns/);
});

await checkAsync("a page whose redraft applies every blocking finding is accepted", async () => {
  const { handoff } = await runStage1();
  const dir = writeResultsDir([]);
  const h = stubHarness(stage2Stubs(handoff, dir, { [APPLIED]: appliedAll() }));
  assert.equal((await go(S2({ resultsDir: dir }), h)).pages[0].status, "accepted");
});

await checkAsync("a stage-1 escalated page escalates in stage 2 without a redraft", async () => {
  const { handoff } = await runStage1({ [`draft:${PAGE.id}`]: null });
  assert.equal(handoff.pages[0].status, "escalate");
  const dir = writeResultsDir([]);
  const h = stubHarness(stage2Stubs(handoff, dir));
  const result = await go(S2({ resultsDir: dir }), h);
  assert.equal(result.pages[0].status, "escalate");
  assert.equal(labelled(h, "redraft:").length, 0);
});

// ---------------------------------------------------------------------------------------------
// Dry-run gap 1: no self-verified facts. Gap 2: reader class.
// ---------------------------------------------------------------------------------------------

const FILED = ["docs/internal/facts/admin.md f:doctor-exit", "docs/internal/facts/admin.md f:doctor-flag"];

await checkAsync("gap 1: the drafter files candidates only and runs no gate; the fact read traces them, retags one and leaves one; the gate runs after it", async () => {
  const { h, handoff } = await runStage1({
    [`draft:${PAGE.id}`]: { path: PAGE.path, bulletsFiled: FILED },
    [`fact:${PAGE.id}`]: {
      verdict: "accept", findings: [],
      retagged: [{ id: "f:doctor-exit", source: "tool/cmd/cairn/doctor.go:41 (`os.Exit(0)`)" }],
      leftCandidate: [{ id: "f:doctor-flag", reason: "the cited line defines no such flag" }],
      summary: "traced"
    }
  });
  const draft = labelled(h, "draft:")[0].prompt;
  assert.match(draft, /tagged `\[candidate: \.\.\.\]` and nothing else/);
  assert.match(draft, /Never\nchange the tag of any bullet/);
  assert.doesNotMatch(draft, /cairn-run-gate/, "the drafter never runs the gate of record");
  const fact = labelled(h, "fact:")[0].prompt;
  for (const b of FILED) assert.ok(fact.includes(b), `the fact read is handed ${b}`);
  assert.match(fact, /retag it \[verified\] in place with a code Source/);
  assert.match(fact, /quoted anchor/);
  assert.match(fact, /leftCandidate/);
  assert.match(fact, /whose tag is no longer \[candidate\] was retagged by the drafter itself/);
  const order = h.calls.map((c) => c.opts.label);
  assert.ok(order.indexOf(`gate:${PAGE.id}`) > order.indexOf(`fact:${PAGE.id}`), "the gate runs after the fact read's retags");
  assert.match(labelled(h, "gate:")[0].prompt, /check:provenance/);
  const hp = handoff.pages[0];
  assert.deepEqual(hp.bulletsFiled, FILED);
  assert.deepEqual(hp.factRetagged.map((x) => x.id), ["f:doctor-exit"]);
  assert.deepEqual(hp.factLeftCandidate.map((x) => x.id), ["f:doctor-flag"]);
});

await checkAsync("gap 1: a redraft's attempt to retag is flagged by the applied read as a blocking new issue, and the page escalates", async () => {
  const { handoff } = await runStage1({
    [`draft:${PAGE.id}`]: { path: PAGE.path, bulletsFiled: FILED },
    [`fact:${PAGE.id}`]: { ...CLEAN_FACT, findings: FACT_FINDINGS, verdict: "fix",
      retagged: [{ id: "f:doctor-exit", source: "tool/cmd/cairn/doctor.go:41 (`os.Exit(0)`)" }],
      leftCandidate: [{ id: "f:doctor-flag", reason: "no such flag" }] }
  });
  const dir = writeResultsDir([]);
  const redraftFiled = ["docs/internal/facts/admin.md f:doctor-json"];
  const h = stubHarness(stage2Stubs(handoff, dir, {
    [`redraft:${PAGE.id}`]: { path: PAGE.path, bulletsFiled: redraftFiled },
    [APPLIED]: (prompt) => {
      const base = appliedAll()(prompt);
      return {
        ...base,
        newIssues: [{ location: "admin.md f:doctor-flag", finding: "retagged [verified] by the redraft itself; restored to [candidate]", blocking: true }],
        leftCandidate: [{ id: "f:doctor-json", reason: "not traced to code" }]
      };
    }
  }));
  const result = await go(S2({ resultsDir: dir }), h);
  const applied = labelled(h, "applied:")[0].prompt;
  assert.ok(applied.includes(redraftFiled[0]), "the applied read traces the redraft's candidates");
  assert.match(applied, /- f:doctor-flag/, "the stage-1 leftover candidate is on the self-retag watch list");
  assert.match(applied, /retagged by the redraft itself[\s\S]*blocking `newIssues` entry/);
  assert.equal(labelled(h, "applied:")[0].opts.agentType, "general-purpose", "the read that retags is not the read-only editor");
  const order = h.calls.map((c) => c.opts.label);
  assert.ok(order.indexOf(`regate:${PAGE.id}`) > order.indexOf(APPLIED), "the redraft's gate runs after the applied read's retags");
  assert.equal(result.pages[0].status, "escalate");
  assert.equal(result.pages[0].newBlocking.length, 1);
});

await checkAsync("gap 2: a readerJobs entry carries its class through the handoff; the editor is told how to pick one", async () => {
  const { h, handoff } = await runStage1({
    [`editor:${PAGE.id}`]: CLEAN_EDITOR([{ ...JOB("a"), class: "docs-only" }, { ...JOB("b"), class: "docs-and-site" }]),
    [`fact:${PAGE.id}`]: CLEAN_FACT
  });
  const editor = labelled(h, "editor:")[0].prompt;
  for (const c of ["docs-only", "docs-and-binary", "docs-and-site", "repository"]) assert.ok(editor.includes(`"${c}"`), `the class rule names ${c}`);
  assert.deepEqual(handoff.pages[0].readerJobs.map((j) => [j.id, j.class]), [["is-it-working--1", "docs-only"], ["is-it-working--2", "docs-and-site"]]);
  assert.match(SRC, /"class": "<the readerJobs entry's class/);
  assert.match(SRC, /struck by the conductor|strikes it through `struckReaderFindings`/);
});

for (const d of tempDirs) rmSync(d, { recursive: true, force: true });

console.log("");
if (failures.length) {
  console.log(`${failures.length} FAILING: ${failures.join(", ")}`);
  process.exit(1);
}
console.log("ALL PASS");
