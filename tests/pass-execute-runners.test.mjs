// Runs pass-execute.js and pass-execute-chains.js bodies with agent, parallel, and log
// stubbed, and unit-tests their extracted pure functions, following the marker-extraction and
// new Function pattern of tests/docs-page-chain-derivation.test.mjs (a script with a top-level
// `return` this repo's test runner cannot import as a module). Run with:
//   node tests/pass-execute-runners.test.mjs
// Exits 0 with "ALL PASS" on success; prints failures and exits 1 otherwise.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import assert from "node:assert/strict";

const HERE = dirname(fileURLToPath(import.meta.url));
const SEQ_PATH = join(HERE, "..", "claude", ".claude", "workflows", "pass-execute.js");
const CHAINS_PATH = join(HERE, "..", "claude", ".claude", "workflows", "pass-execute-chains.js");
const PASS_CORE_PATH = join(HERE, "..", "claude", ".claude", "skills", "pass-core", "SKILL.md");

const SEQ_SRC = readFileSync(SEQ_PATH, "utf8");
const CHAINS_SRC = readFileSync(CHAINS_PATH, "utf8");
const PASS_CORE_SRC = readFileSync(PASS_CORE_PATH, "utf8");

const failures = [];
const pending = [];
function check(name, fn) {
  pending.push({ name, fn });
}
async function runChecks() {
  for (const { name, fn } of pending) {
    try {
      await fn();
      console.log(`ok - ${name}`);
    } catch (e) {
      failures.push(name);
      console.log(`FAIL - ${name}`);
      console.log(`  ${(e && e.stack) || e}`);
    }
  }
}

// -------------------------------------------------------------------------------------------
// Harness: strip the runner's `export` keyword (new Function cannot parse it), replace its
// trailing `return main();` with a bundle of every internal a test needs, and compile it with
// args, agent, parallel, log, phase, and budget as injected parameters, matching the workflow
// runtime's own ambient globals. Calling the compiled factory never invokes main() itself; a
// test calls bundle.main() only when it needs the full async flow.
// -------------------------------------------------------------------------------------------

const INTERNALS = [
  "main", "PASS_CLASSES", "CLASS_DEFAULT_REDUCED_GATE", "DEFAULT_REVIEWER_MODEL", "gateCore",
  "gateMatches", "classOf", "reducedGateFor", "applyClassBar", "taskStatus", "IMPL_SCHEMA",
  "REVIEW_SCHEMA", "recordBaseSha", "resolveGate", "resolveClassifier", "implementPrompt",
  "reviewPrompt", "validateArgs", "runTask", "runChain", "tally", "gateToRun",
  "runGateIndependently", "validatedReducedCommand", "gateRecordLines", "reducedCheckLine",
  "touchedFiles"
];

function loadFactory(src) {
  const marker = "\nreturn main();";
  const idx = src.lastIndexOf(marker);
  assert.notEqual(idx, -1, 'expected a trailing "return main();" to replace for the test harness');
  const body = src.slice(0, idx).replace(/^export const meta/m, "const meta");
  const bundleExpr = `{ ${INTERNALS.map((n) => `${n}: typeof ${n} !== "undefined" ? ${n} : undefined`).join(", ")} }`;
  // eslint-disable-next-line no-new-func -- running the runner body with injected globals
  // (args, agent, parallel, log, phase, budget) is the documented pattern for a workflow
  // script this test runner cannot import as an ES module.
  return new Function("args", "agent", "parallel", "log", "phase", "budget", `${body}\nreturn ${bundleExpr};`);
}

const seqFactory = loadFactory(SEQ_SRC);
const chainsFactory = loadFactory(CHAINS_SRC);

function makeLog() {
  const lines = [];
  const log = (msg) => lines.push(String(msg));
  log.lines = lines;
  return log;
}

function makeBudget() {
  return { total: null, remaining: () => Infinity, spent: () => 0 };
}

async function defaultParallel(fns) {
  return Promise.all(fns.map((fn) => fn()));
}

/**
 * A scripted `agent` mock: `routes` is an array of `[labelPrefix, handler]` pairs tried in
 * order. A label matching no route throws, so a stray probe the test did not expect fails
 * loudly instead of silently.
 */
function makeAgentMock(routes) {
  const calls = [];
  const agent = async (prompt, opts = {}) => {
    calls.push({ prompt, opts, label: opts.label || "" });
    for (const [prefix, handler] of routes) {
      if ((opts.label || "").startsWith(prefix)) {
        return handler(prompt, opts);
      }
    }
    throw new Error(`unhandled agent label: "${opts.label || ""}"`);
  };
  agent.calls = calls;
  return agent;
}

/**
 * Compiles a runner factory into its bundle of internals, with args and every ambient global
 * bound. `routes` scripts the `agent` mock; a test that never calls `bundle.main()` can pass an
 * empty array, since no agent call happens until main() (or a function under test) runs.
 */
function load(factory, args = {}, routes = []) {
  const log = makeLog();
  const agent = makeAgentMock(routes);
  const bundle = factory(args, agent, defaultParallel, log, () => {}, makeBudget());
  return { bundle, agent, log };
}

const SHA = "a".repeat(40);
const baseShaHandler = () => ({ sha: SHA });
const gateRunPass = () => ({ command: "g", exitCode: 0, result: "pass", excerpt: "" });
const acceptReview = () => ({ verdict: "accept", summary: "", blocking: [], nonBlocking: [], gate: "pass", unspecified: [] });
const implOk = (extra = {}) => ({
  filesTouched: ["x.js"],
  gate: "pass",
  gateOutput: "ok",
  commits: ["deadbeef"],
  unspecifiedDecisions: [],
  couldNotDo: [],
  summary: "done",
  ...extra
});

// -------------------------------------------------------------------------------------------
// A balanced-paren extractor for a static "every agent( call names a model" scan: skips string,
// template, and comment content so a prompt string's own punctuation cannot desync the depth
// count.
// -------------------------------------------------------------------------------------------

function extractCall(src, startIndex) {
  let i = startIndex;
  let depth = 0;
  let inSingle = false, inDouble = false, inTemplate = false, inLine = false, inBlock = false;
  for (; i < src.length; i++) {
    const c = src[i];
    const prev = src[i - 1];
    if (inLine) { if (c === "\n") inLine = false; continue; }
    if (inBlock) { if (prev === "*" && c === "/") inBlock = false; continue; }
    if (inSingle) { if (c === "'" && prev !== "\\") inSingle = false; continue; }
    if (inDouble) { if (c === '"' && prev !== "\\") inDouble = false; continue; }
    if (inTemplate) { if (c === "`" && prev !== "\\") inTemplate = false; continue; }
    if (c === "/" && src[i + 1] === "/") { inLine = true; continue; }
    if (c === "/" && src[i + 1] === "*") { inBlock = true; continue; }
    if (c === "'") { inSingle = true; continue; }
    if (c === '"') { inDouble = true; continue; }
    if (c === "`") { inTemplate = true; continue; }
    if (c === "(") depth++;
    if (c === ")") {
      depth--;
      if (depth === 0) return src.slice(startIndex, i + 1);
    }
  }
  throw new Error(`unbalanced parens scanning from index ${startIndex}`);
}

// Only the implementer dispatch (the two `agent(implementPrompt(...), { ..., ...implOpts })`
// calls per runner, first round and fix round) is exempt, and only because of its `...implOpts`
// spread: an unset t.model leaves the implementer's own frontmatter pin standing, and a set
// t.model reaches the call through that spread rather than a literal `model:` key, so the call's
// own text can carry no literal model: for either case. Every other agent( call, including both
// reviewer dispatches in each runner (which always pass a literal `model: reviewerModel`), still
// owes a literal model: in its own call text.
function agentCallsMissingModel(src) {
  const offenders = [];
  const re = /(^|[^.\w])agent\(/g;
  let m;
  while ((m = re.exec(src))) {
    const start = m.index + m[0].length - "agent(".length;
    const callText = extractCall(src, start);
    if (/\.\.\.implOpts\b/.test(callText)) {
      continue;
    }
    if (!/\bmodel\s*:/.test(callText)) {
      offenders.push(src.slice(0, start).split("\n").length);
    }
  }
  return offenders;
}

function extractMatcherBody(src, label) {
  const START = "// === GATE MATCHER";
  const END = "// === END GATE MATCHER ===";
  const s = src.indexOf(START);
  const e = src.indexOf(END);
  assert.notEqual(s, -1, `${label}: gate matcher start marker missing`);
  assert.notEqual(e, -1, `${label}: gate matcher end marker missing`);
  const afterFirstLine = src.indexOf("\n", s) + 1;
  return src.slice(afterFirstLine, e);
}

// -------------------------------------------------------------------------------------------
// Parity (AW-11): PASS_CLASSES, the reduced-gate default, and the gate matcher stay equal
// across both runners; pass-core's table stays equal to the class-name set, reviewer model,
// and gate lane the runner enforces.
// -------------------------------------------------------------------------------------------

check("PASS_CLASSES is identical across both runners", () => {
  const seq = load(seqFactory).bundle;
  const chn = load(chainsFactory).bundle;
  assert.deepEqual(seq.PASS_CLASSES, chn.PASS_CLASSES);
});

check("CLASS_DEFAULT_REDUCED_GATE is identical across both runners and names no npm command", () => {
  const seq = load(seqFactory).bundle;
  const chn = load(chainsFactory).bundle;
  assert.equal(seq.CLASS_DEFAULT_REDUCED_GATE, chn.CLASS_DEFAULT_REDUCED_GATE);
  assert.doesNotMatch(seq.CLASS_DEFAULT_REDUCED_GATE, /npm/i);
});

check("the gate matcher (gateCore/gateMatches) is identical source text across both runners", () => {
  const seqBody = extractMatcherBody(SEQ_SRC, "pass-execute.js");
  const chainsBody = extractMatcherBody(CHAINS_SRC, "pass-execute-chains.js");
  assert.equal(seqBody, chainsBody);
});

check("the gate matcher accepts the three named forms: a cairn-run-gate wrapper, a cd prefix, and multi-line stdout", () => {
  for (const factory of [seqFactory, chainsFactory]) {
    const { bundle } = load(factory);
    const resolved = "cd /repo && npm run check";
    assert.ok(bundle.gateMatches(resolved, resolved, "/repo"), "exact match with a cd prefix");
    assert.ok(bundle.gateMatches(`cairn-run-gate '${resolved}'`, resolved, "/repo"), "cairn-run-gate wrapper");
    assert.ok(
      bundle.gateMatches(`gate still running\nmore output\n${resolved}`, resolved, "/repo"),
      "multi-line stdout, last line only"
    );
  }
});

check("the gate matcher accepts allowlisted assignments and extra trailing steps, and discards the pre-wrapper prefix", () => {
  for (const factory of [seqFactory, chainsFactory]) {
    const { bundle } = load(factory);
    const g = "npm run check && npm test";
    const m = (ran, resolved = g) => bundle.gateMatches(ran, resolved, "/repo");
    assert.ok(m(`cairn-run-gate 'CAIRN_GATE_LANE=light ${g}'`), "assignment prefix inside the quotes");
    assert.ok(m(`cairn-run-gate 'CI=1 E2E_PORT=4173 ${g}'`), "two assignments");
    assert.ok(m(`cairn-run-gate 'export CI=1 && ${g}'`), "export step");
    assert.ok(m(`cairn-run-gate 'CAIRN_GATE_LANE=light && ${g}'`), "assignment step");
    assert.ok(m(`CAIRN_GATE_LANE=light ${g}`), "assignment on an unwrapped command");
    assert.ok(m(`cairn-run-gate '${g} && git status'`), "extra trailing step");
    assert.ok(m(`cd /repo && cairn-run-gate '${g}'`), "cd before the wrapper is discarded");
    assert.ok(m(`cd /repo && CAIRN_GATE_LANE=light cairn-run-gate '${g}'`), "assignment before the wrapper is discarded");
    assert.ok(m(`cairn-run-gate 'CI=1 npm run check && npm test && echo done'`, g), "prefix plus trailing step");
  }
});

check("the gate matcher rejects a cd step, an unlisted assignment, another command, and a dropped step inside the quotes", () => {
  for (const factory of [seqFactory, chainsFactory]) {
    const { bundle } = load(factory);
    const g = "npm run check && npm test";
    const m = (ran, resolved = g) => bundle.gateMatches(ran, resolved, "/repo");
    assert.ok(!m(`cairn-run-gate 'cd /elsewhere && ${g}'`), "extra leading cd");
    assert.ok(!m(`cairn-run-gate 'pushd /elsewhere && ${g}'`), "extra leading pushd");
    assert.ok(!m(`cairn-run-gate 'echo hi && ${g}'`), "extra leading command");
    assert.ok(!m(`cairn-run-gate 'FOO=1 ${g}'`), "unlisted assignment prefix");
    assert.ok(!m(`cairn-run-gate 'export FOO=1 && ${g}'`), "unlisted export step");
    assert.ok(!m(`cairn-run-gate 'CI=1 FOO=1 ${g}'`), "unlisted assignment after an allowed one");
    assert.ok(!m(`cairn-run-gate 'npm run check'`), "dropped gate step");
    assert.ok(!m(`cairn-run-gate 'CI=1 npm run check'`), "dropped gate step with assignment");
    assert.ok(!m(`cairn-run-gate 'npm run lint && npm test'`), "different command");
    assert.ok(!m(`cd /elsewhere && cairn-run-gate 'cd /elsewhere && ${g}'`), "inner cd still rejected");
  }
});

check("the gate matcher bounds trailing steps to plain && steps and keeps placeholders from swallowing steps", () => {
  for (const factory of [seqFactory, chainsFactory]) {
    const { bundle } = load(factory);
    const g = "npm run check && npm test";
    const m = (ran, resolved = g) => bundle.gateMatches(ran, resolved, "/repo");
    assert.ok(m(`${g} && echo ok`), "plain trailing step");
    assert.ok(!m(`${g} && true || true`), "|| hides a failure");
    assert.ok(!m(`${g} && x; true`), "semicolon");
    assert.ok(!m(`${g} && x | cat`), "pipe");
    assert.ok(!m(`${g} && x # c`), "comment");
    const p = "npx vitest run <the touched unit test files> && npm run check && npm test";
    assert.ok(m("npx vitest run a.test.ts b.test.ts && npm run check && npm test && echo ok", p), "placeholder plus trailing step");
    assert.ok(!m("npx vitest run a.test.ts && npm run check", p), "placeholder gate with dropped step");
    assert.ok(!m(`npx vitest run "a && npm run check && npm test && x"`, p), "quoted placeholder swallowing steps");
  }
});

check("pass-core's class table matches PASS_CLASSES: the class-name set, the reviewer model, and the gate lane", () => {
  const rowRe = /^\|\s*`([a-z-]+)`[^|]*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|\s*$/gm;
  const rows = [...PASS_CORE_SRC.matchAll(rowRe)];
  assert.ok(rows.length >= 6, `expected at least 6 class rows in pass-core's table, found ${rows.length}`);
  for (const factory of [seqFactory, chainsFactory]) {
    const { bundle } = load(factory);
    const tableNames = new Set(rows.map((m) => m[1]));
    assert.deepEqual(tableNames, new Set(Object.keys(bundle.PASS_CLASSES)));
    for (const m of rows) {
      const name = m[1];
      const gateCol = m[2];
      const barCol = m[3].trim();
      const cls = bundle.PASS_CLASSES[name];
      assert.ok(cls, `pass-core names a class "${name}" the runner does not define`);
      if (/^Opus\b/.test(barCol)) {
        assert.equal(cls.reviewerModel, "claude-opus-5-5", `${name}: pass-core's bar column says Opus`);
      } else if (/^Sonnet\b/.test(barCol)) {
        assert.equal(cls.reviewerModel, "sonnet", `${name}: pass-core's bar column says Sonnet`);
      }
      const wantsLight = /light gate lane/.test(gateCol);
      assert.equal(Boolean(cls.gateLane === "light"), wantsLight, `${name}: gate lane mismatch against pass-core`);
    }
  }
});

// -------------------------------------------------------------------------------------------
// Schema completeness (AW-05, AW-12): every field a mandate cites exists in IMPL_SCHEMA; every
// REVIEW_SCHEMA blocking-item field is read somewhere (the removed severity field was not).
// -------------------------------------------------------------------------------------------

check("every field the auth-data mandate cites exists in IMPL_SCHEMA (both runners)", () => {
  for (const factory of [seqFactory, chainsFactory]) {
    const { bundle } = load(factory);
    const mandate = bundle.PASS_CLASSES["auth-data"].mandate;
    const cited = [...mandate.matchAll(/\b([a-zA-Z]+Ledger)\b/g)].map((m) => m[1]);
    assert.ok(cited.length > 0, "expected the auth-data mandate to cite at least one *Ledger field");
    for (const field of cited) {
      assert.ok(field in bundle.IMPL_SCHEMA.properties, `IMPL_SCHEMA is missing "${field}"`);
    }
  }
});

check("every REVIEW_SCHEMA blocking-item field is read, and the unread severity field is gone", () => {
  for (const [name, src, factory] of [
    ["pass-execute.js", SEQ_SRC, seqFactory],
    ["pass-execute-chains.js", CHAINS_SRC, chainsFactory]
  ]) {
    const { bundle } = load(factory);
    const fields = Object.keys(bundle.REVIEW_SCHEMA.properties.blocking.items.properties);
    for (const field of fields) {
      assert.match(src, new RegExp(`\\bb\\.${field}\\b`), `${name}: blocking-item field "${field}" is never read as b.${field}`);
    }
    assert.doesNotMatch(src, /\bseverity\b/, `${name}: the unread severity field lingers`);
  }
});

// -------------------------------------------------------------------------------------------
// AW-01 / AW-04: the two-step reduced-gate resolution, and a no-class reduced round renders
// no MISMATCH line and no npm command (AW-03 for the pre-class a.reducedGate fallback).
// -------------------------------------------------------------------------------------------

check("reducedGateFor: a named gate with no reducedGate renders the class default; an explicit reducedGate renders it", () => {
  for (const factory of [seqFactory, chainsFactory]) {
    const { bundle } = load(factory);
    const cls = { name: "sweep", ...bundle.PASS_CLASSES.sweep };
    const blocking = [{ location: "x", finding: "y", fix: "z", commentOnly: true }];
    assert.equal(bundle.reducedGateFor({ id: "t1" }, {}, cls, blocking), bundle.CLASS_DEFAULT_REDUCED_GATE);
    assert.equal(
      bundle.reducedGateFor({ id: "w1", reducedGate: "bash scripts/check.sh" }, {}, cls, blocking),
      "bash scripts/check.sh"
    );
  }
});

check("a no-class reduced round renders no MISMATCH line and no npm command (pass-execute.js)", () => {
  const { bundle } = load(seqFactory);
  const t = { id: "1", title: "T", criteria: "C" };
  const a = { repo: "/repo", gate: "full gate", reducedGate: "targeted reduced gate", implementer: "i" };
  const blocking = [{ location: "x", finding: "y", fix: "z", commentOnly: true }];
  const reduced = bundle.reducedGateFor(t, a, null, blocking);
  assert.ok(reduced, "expected a reduced gate for an all-commentOnly round");
  const implPrompt = bundle.implementPrompt(t, a, blocking, "deadbeef");
  assert.doesNotMatch(implPrompt, /npm/i);
  assert.match(implPrompt, /targeted reduced gate/);
  const implReport = {
    gate: "pass", gateOutput: "", gateCommand: "totally different string",
    filesTouched: [], unspecifiedDecisions: [], couldNotDo: [], summary: ""
  };
  const resolvedGate = { gate: "some other resolved gate", source: "fallback", tier: "default" };
  const reviewText = bundle.reviewPrompt(t, a, implReport, resolvedGate, reduced);
  assert.doesNotMatch(reviewText, /MISMATCH/);
  assert.doesNotMatch(reviewText, /npm/i);
});

check("a no-class reduced round renders no MISMATCH line and no npm command (pass-execute-chains.js)", () => {
  const { bundle } = load(chainsFactory);
  const t = { id: "1", title: "T", criteria: "C" };
  const chain = { id: "C", repo: "/repo", branch: "chain-c" };
  const a = { gate: "full gate", reducedGate: "targeted reduced gate", implementer: "i", planPath: "/p" };
  const blocking = [{ location: "x", finding: "y", fix: "z", commentOnly: true }];
  const reduced = bundle.reducedGateFor(t, a, null, blocking);
  assert.ok(reduced, "expected a reduced gate for an all-commentOnly round");
  const implPrompt = bundle.implementPrompt(t, chain, a, blocking, "deadbeef", false);
  assert.doesNotMatch(implPrompt, /npm/i);
  assert.match(implPrompt, /targeted reduced gate/);
  const implReport = {
    gate: "pass", gateOutput: "", gateCommand: "totally different string", commits: [],
    filesTouched: [], unspecifiedDecisions: [], couldNotDo: [], summary: ""
  };
  const resolvedGate = { gate: "some other resolved gate", source: "fallback", tier: "default" };
  const reviewText = bundle.reviewPrompt(t, chain, a, implReport, resolvedGate, reduced);
  assert.doesNotMatch(reviewText, /MISMATCH/);
  assert.doesNotMatch(reviewText, /npm/i);
});

// -------------------------------------------------------------------------------------------
// AW-01 fix round: a no-class fix round whose findings are all commentOnly must still resolve
// to `t.reducedGate || a.reducedGate || CLASS_DEFAULT_REDUCED_GATE`, never fall through to the
// full gate for want of an explicit `a.reducedGate` (Geoff's 2026-09-09 ruling).
// -------------------------------------------------------------------------------------------

check("reducedGateFor (no class): an all-commentOnly round with no reducedGate named anywhere resolves the class default, never null; t.reducedGate wins over a.reducedGate", () => {
  for (const factory of [seqFactory, chainsFactory]) {
    const { bundle } = load(factory);
    const blocking = [{ location: "x", finding: "y", fix: "z", commentOnly: true }];
    assert.equal(bundle.reducedGateFor({ id: "t1" }, {}, null, blocking), bundle.CLASS_DEFAULT_REDUCED_GATE);
    assert.equal(
      bundle.reducedGateFor(
        { id: "t2", reducedGate: "bash scripts/check.sh" },
        { reducedGate: "some other gate" },
        null,
        blocking
      ),
      "bash scripts/check.sh"
    );
  }
});

check("a no-class all-commentOnly round with no reducedGate renders the class default sentence, not the full gate (pass-execute.js)", () => {
  const { bundle } = load(seqFactory);
  const t = { id: "1", title: "T", criteria: "C" };
  const a = { repo: "/repo", gate: "full gate", implementer: "i" };
  const blocking = [{ location: "x", finding: "y", fix: "z", commentOnly: true }];
  const reduced = bundle.reducedGateFor(t, a, null, blocking);
  assert.equal(reduced, bundle.CLASS_DEFAULT_REDUCED_GATE);
  const implPrompt = bundle.implementPrompt(t, a, blocking, "deadbeef", false);
  assert.doesNotMatch(implPrompt, /npm/i);
  assert.match(implPrompt, /the repo's type check plus only the test files this fix round touched/);
  const implReport = {
    gate: "pass", gateOutput: "", gateCommand: "some gate the implementer ran",
    filesTouched: [], unspecifiedDecisions: [], couldNotDo: [], summary: ""
  };
  const resolvedGate = { gate: "some other resolved gate", source: "fallback", tier: "default" };
  const fixRoundReview = bundle.reviewPrompt(t, a, implReport, resolvedGate, reduced);
  assert.doesNotMatch(fixRoundReview, /MISMATCH/);
  assert.doesNotMatch(fixRoundReview, /npm/i);
  assert.match(fixRoundReview, /the repo's type check plus only the test files this fix round touched/);
  // The reviewer's first-round prompt (before any fix round; reduced is not yet known) must
  // still name the resolved reduced gate, so the reviewer knows what a reduced round would be.
  const firstRoundReview = bundle.reviewPrompt(t, a, implReport, resolvedGate, null);
  assert.match(firstRoundReview, /the repo's type check plus only the test files this fix round touched/);
});

check("a no-class all-commentOnly round with no reducedGate renders the class default sentence, not the full gate (pass-execute-chains.js)", () => {
  const { bundle } = load(chainsFactory);
  const t = { id: "1", title: "T", criteria: "C" };
  const chain = { id: "C", repo: "/repo", branch: "chain-c" };
  const a = { gate: "full gate", implementer: "i", planPath: "/p" };
  const blocking = [{ location: "x", finding: "y", fix: "z", commentOnly: true }];
  const reduced = bundle.reducedGateFor(t, a, null, blocking);
  assert.equal(reduced, bundle.CLASS_DEFAULT_REDUCED_GATE);
  const implPrompt = bundle.implementPrompt(t, chain, a, blocking, "deadbeef", false);
  assert.doesNotMatch(implPrompt, /npm/i);
  assert.match(implPrompt, /the repo's type check plus only the test files this fix round touched/);
  const implReport = {
    gate: "pass", gateOutput: "", gateCommand: "some gate the implementer ran", commits: [],
    filesTouched: [], unspecifiedDecisions: [], couldNotDo: [], summary: ""
  };
  const resolvedGate = { gate: "some other resolved gate", source: "fallback", tier: "default" };
  const fixRoundReview = bundle.reviewPrompt(t, chain, a, implReport, resolvedGate, reduced);
  assert.doesNotMatch(fixRoundReview, /MISMATCH/);
  assert.doesNotMatch(fixRoundReview, /npm/i);
  assert.match(fixRoundReview, /the repo's type check plus only the test files this fix round touched/);
  const firstRoundReview = bundle.reviewPrompt(t, chain, a, implReport, resolvedGate, null);
  assert.match(firstRoundReview, /the repo's type check plus only the test files this fix round touched/);
});

// -------------------------------------------------------------------------------------------
// AW-06: the plan-file line names an absolute path, never "committed in this repo"; the
// "Ruled inputs" section reads as optional.
// -------------------------------------------------------------------------------------------

check("the chain runner's plan-file line names an absolute path and treats Ruled inputs as optional", () => {
  const { bundle } = load(chainsFactory);
  const t = { id: "1", title: "T", criteria: "C" };
  const chain = { id: "C", repo: "/repo", branch: "chain-c" };
  const a = { gate: "g", implementer: "i", planPath: "/abs/plan.md" };
  const prompt = bundle.implementPrompt(t, chain, a, null, "deadbeef", false);
  assert.match(prompt, /Plan file \(an absolute path\): \/abs\/plan\.md/);
  assert.doesNotMatch(prompt, /committed in this repo/);
  assert.match(prompt, /"Ruled inputs" section \(if present\)/);
});

// -------------------------------------------------------------------------------------------
// AW-13 / the style-guide-sync fixture (Pass B acceptance, amendment 1): chains R and W run in
// one invocation. R carries no `classifier` field and gets one cached haiku existence probe
// across its two tasks; W sets `classifier: false` and spawns none. W's tasks carry
// `reducedGate: "bash scripts/check.sh"`, in the same form as their named gate, and its
// reduced round names no npm command and no MISMATCH line.
// -------------------------------------------------------------------------------------------

check("resolveClassifier resolution order: a chain's own value, else args.classifier, else one probe", async () => {
  const { bundle, agent } = load(chainsFactory, {}, [["classifier:", () => ({ exists: true })]]);
  assert.equal(await bundle.resolveClassifier({ id: "c1", classifier: false }, {}), false);
  assert.equal(await bundle.resolveClassifier({ id: "c2" }, { classifier: true }), true);
  assert.equal(agent.calls.length, 0, "an explicit chain or args classifier value must spawn no probe");
  const probed = await bundle.resolveClassifier({ id: "c3" }, {});
  assert.equal(probed, true);
  assert.equal(agent.calls.length, 1);
  assert.equal(agent.calls[0].opts.model, "haiku");
});

check("style-guide-sync fixture: chains R and W in one invocation", async () => {
  const chainR = {
    id: "R",
    repo: "/repo-r",
    branch: "chain-r",
    tasks: [
      { id: "r1", title: "R task 1", criteria: "c", passClass: "engine-logic" },
      { id: "r2", title: "R task 2", criteria: "c", passClass: "engine-logic" }
    ]
  };
  const chainW = {
    id: "W",
    repo: "/repo-w",
    branch: "chain-w",
    classifier: false,
    tasks: [
      {
        id: "w1", title: "W task", criteria: "c", passClass: "sweep",
        gate: "bash scripts/check.sh", reducedGate: "bash scripts/check.sh"
      }
    ]
  };
  const args = {
    gate: "bash scripts/check.sh",
    implementer: "cairn-implementer",
    planPath: "/abs/plan.md",
    chains: [chainR, chainW]
  };
  const routes = [
    ["classifier:R", () => ({ exists: true })],
    ["base:", baseShaHandler],
    ["gatetier:r", () => ({ exists: false, gate: "" })],
    ["impl:r1", () => implOk()],
    ["gaterun:", gateRunPass],
    ["review:r1", () => acceptReview()],
    ["impl:r2", () => implOk()],
    ["review:r2", () => acceptReview()],
    ["impl:w1:fix1", () => implOk({ gateCommand: "totally different string" })],
    ["impl:w1", () => implOk()],
    ["review:w1:fix1", () => acceptReview()],
    ["review:w1", () => ({
      verdict: "fix", summary: "", nonBlocking: [], gate: "fail", unspecified: [],
      blocking: [{ location: "x", finding: "y", fix: "z", commentOnly: true }]
    })]
  ];
  const { bundle, agent } = load(chainsFactory, args, routes);
  await bundle.main();

  const classifierCalls = agent.calls.filter((c) => c.label.startsWith("classifier:"));
  assert.equal(classifierCalls.length, 1, "R's existence probe must run exactly once across its two tasks, W's not at all");
  assert.equal(classifierCalls[0].label, "classifier:R");
  assert.equal(classifierCalls[0].opts.model, "haiku");

  const wCalls = agent.calls.filter((c) => c.label.includes("w1"));
  assert.ok(wCalls.length > 0, "expected W's task to dispatch");
  for (const c of wCalls) {
    assert.doesNotMatch(c.prompt, /npm/i, `W's "${c.label}" prompt must name no npm command`);
  }
  const fixPrompt = agent.calls.find((c) => c.label === "impl:w1:fix1");
  // Assert the reduced-round sentence itself, not merely that the gate string appears anywhere
  // in the prompt (the "Gate command: bash scripts/check.sh" line would also satisfy a bare
  // substring match; this fails if W's reduced resolution falls back to the class default).
  assert.match(fixPrompt.prompt, /gate is reduced: run `bash scripts\/check\.sh`/);
  const fixReview = agent.calls.find((c) => c.label === "review:w1:fix1");
  assert.doesNotMatch(fixReview.prompt, /MISMATCH/, "a reduced round must carry no MISMATCH-blocking line");
});

// -------------------------------------------------------------------------------------------
// AW-13 mirrored onto pass-execute.js: one args.classifier boolean skips the probe entirely;
// absent runs one cached haiku existence probe for the whole run, never one per task.
// -------------------------------------------------------------------------------------------

check("resolveClassifier (pass-execute.js): args.classifier value skips the probe; absent runs exactly one", async () => {
  const { bundle, agent } = load(seqFactory, {}, [["classifier", () => ({ exists: true })]]);
  assert.equal(await bundle.resolveClassifier({ classifier: false }), false);
  assert.equal(await bundle.resolveClassifier({ classifier: true }), true);
  assert.equal(agent.calls.length, 0, "an explicit args.classifier value must spawn no probe");
  const probed = await bundle.resolveClassifier({});
  assert.equal(probed, true);
  assert.equal(agent.calls.length, 1);
  assert.equal(agent.calls[0].opts.model, "haiku");
});

check("pass-execute.js implementPrompt renders the classifier paragraph only when classifierExists is true", () => {
  const { bundle } = load(seqFactory);
  const t = { id: "1", title: "T", criteria: "c" };
  const a = { repo: "/repo", gate: "g", implementer: "i" };
  assert.match(bundle.implementPrompt(t, a, null, "deadbeef", true), /gate-tier\.mjs/);
  assert.doesNotMatch(bundle.implementPrompt(t, a, null, "deadbeef", false), /gate-tier\.mjs/);
});

check("pass-execute.js resolveGate: classifierExists false returns the fallback and spawns no probe", async () => {
  const { bundle, agent } = load(seqFactory, {}, []);
  const resolved = await bundle.resolveGate({ id: "1" }, { gate: "g" }, "deadbeef", false, "gatetier:1");
  assert.deepEqual(resolved, { gate: "g", source: "fallback", tier: "default" });
  assert.equal(agent.calls.length, 0);
});

check("pass-execute.js: classifier absent spawns exactly one cached probe across two tasks and no per-task gate-tier probe follows a classifier: false run", async () => {
  const argsNoField = {
    repo: "/repo", gate: "g", implementer: "i",
    tasks: [
      { id: "1", title: "T1", criteria: "c" },
      { id: "2", title: "T2", criteria: "c" }
    ]
  };
  const routesNoField = [
    ["classifier", () => ({ exists: false })],
    ["base:", baseShaHandler],
    ["impl:", () => implOk()],
    ["gaterun:", gateRunPass],
    ["review:", () => acceptReview()]
  ];
  const { bundle: bNoField, agent: agentNoField } = load(seqFactory, argsNoField, routesNoField);
  await bNoField.main();
  const classifierCalls = agentNoField.calls.filter((c) => c.label === "classifier");
  assert.equal(classifierCalls.length, 1, "an absent args.classifier must spawn exactly one cached probe across every task");

  const argsFalse = { ...argsNoField, classifier: false };
  const routesFalse = [
    ["base:", baseShaHandler],
    ["impl:", () => implOk()],
    ["gaterun:", gateRunPass],
    ["review:", () => acceptReview()]
  ];
  const { bundle: bFalse, agent: agentFalse } = load(seqFactory, argsFalse, routesFalse);
  await bFalse.main();
  const classifierCallsFalse = agentFalse.calls.filter((c) => c.label === "classifier");
  assert.equal(classifierCallsFalse.length, 0, "classifier: false must spawn no existence probe at all");
  const gatetierCallsFalse = agentFalse.calls.filter((c) => c.label.startsWith("gatetier:"));
  assert.equal(gatetierCallsFalse.length, 0, "classifier: false must skip every per-task gate-tier probe too");
});

// -------------------------------------------------------------------------------------------
// General robustness: every agent( call names a model; the launch NOTE prints at main()'s start.
// -------------------------------------------------------------------------------------------

check("no agent( call lacks an explicit model:, except an implementer dispatch (...implOpts) left to its own frontmatter pin (both runners)", () => {
  for (const [name, src] of [["pass-execute.js", SEQ_SRC], ["pass-execute-chains.js", CHAINS_SRC]]) {
    const offenders = agentCallsMissingModel(src);
    assert.deepEqual(offenders, [], `${name}: agent( calls at line(s) ${offenders.join(", ")} name no model`);
  }
});

check("the implementer dispatch omits model when t.model is unset, and passes it verbatim when set (pass-execute.js)", async () => {
  const args = {
    repo: "/repo", gate: "g", implementer: "cairn-implementer", classifier: false,
    tasks: [
      { id: "1", title: "T1", criteria: "c" },
      { id: "2", title: "T2", criteria: "c", model: "opus" }
    ]
  };
  const routes = [
    ["base:", baseShaHandler],
    ["impl:1", () => implOk()],
    ["impl:2", () => implOk()],
    ["gaterun:", gateRunPass],
    ["review:1", () => acceptReview()],
    ["review:2", () => acceptReview()]
  ];
  const { bundle, agent } = load(seqFactory, args, routes);
  await bundle.main();
  const impl1 = agent.calls.find((c) => c.label === "impl:1");
  const impl2 = agent.calls.find((c) => c.label === "impl:2");
  assert.equal(impl1.opts.agentType, "cairn-implementer");
  assert.ok(!("model" in impl1.opts), "an undeclared task must not override the implementer's own frontmatter model pin");
  assert.equal(impl2.opts.model, "opus", "a task's own model override must reach the dispatch");
  const review1 = agent.calls.find((c) => c.label === "review:1");
  assert.equal(review1.opts.model, bundle.DEFAULT_REVIEWER_MODEL, "the reviewer dispatch always carries a literal model, unlike the exempt implementer dispatch");
});

check("the implementer dispatch omits model when t.model is unset, and passes it verbatim when set (pass-execute-chains.js)", async () => {
  const chain = {
    id: "C", repo: "/repo", branch: "chain-c", classifier: false,
    tasks: [
      { id: "1", title: "T1", criteria: "c" },
      { id: "2", title: "T2", criteria: "c", model: "opus" }
    ]
  };
  const args = { gate: "g", implementer: "cairn-implementer", planPath: "/p", chains: [chain] };
  const routes = [
    ["base:", baseShaHandler],
    ["impl:1", () => implOk()],
    ["impl:2", () => implOk()],
    ["gaterun:", gateRunPass],
    ["review:1", () => acceptReview()],
    ["review:2", () => acceptReview()]
  ];
  const { bundle, agent } = load(chainsFactory, args, routes);
  await bundle.main();
  const impl1 = agent.calls.find((c) => c.label === "impl:1");
  const impl2 = agent.calls.find((c) => c.label === "impl:2");
  assert.equal(impl1.opts.agentType, "cairn-implementer");
  assert.ok(!("model" in impl1.opts), "an undeclared task must not override the implementer's own frontmatter model pin");
  assert.equal(impl2.opts.model, "opus", "a task's own model override must reach the dispatch");
  const review1 = agent.calls.find((c) => c.label === "review:1");
  assert.equal(review1.opts.model, bundle.DEFAULT_REVIEWER_MODEL, "the reviewer dispatch always carries a literal model, unlike the exempt implementer dispatch");
});

check("the launch NOTE prints, naming the runaway guard and the wake-up (pass-execute.js)", async () => {
  const args = {
    repo: "/repo", gate: "g", implementer: "i", classifier: false,
    tasks: [{ id: "1", title: "T", criteria: "c" }]
  };
  const routes = [
    ["base:", baseShaHandler],
    ["impl:", () => implOk()],
    ["gaterun:", gateRunPass],
    ["review:", () => acceptReview()]
  ];
  const { bundle, log } = load(seqFactory, args, routes);
  await bundle.main();
  assert.ok(log.lines.length > 0, "expected at least one log line");
  assert.match(log.lines[0], /claude-wf-guard/);
  assert.match(log.lines[0], /\/loop/);
});

check("the launch NOTE prints, naming the runaway guard and the wake-up (pass-execute-chains.js)", async () => {
  const args = {
    gate: "g", implementer: "i", planPath: "/p",
    chains: [{ id: "C", repo: "/repo", branch: "b", classifier: false, tasks: [{ id: "1", title: "T", criteria: "c" }] }]
  };
  const routes = [
    ["base:", baseShaHandler],
    ["impl:", () => implOk()],
    ["gaterun:", gateRunPass],
    ["review:", () => acceptReview()]
  ];
  const { bundle, log } = load(chainsFactory, args, routes);
  await bundle.main();
  assert.ok(log.lines.length > 0, "expected at least one log line");
  assert.match(log.lines[0], /claude-wf-guard/);
  assert.match(log.lines[0], /\/loop/);
});

// -------------------------------------------------------------------------------------------
// AW-01: no plan is rejected for a missing reducedGate.
// -------------------------------------------------------------------------------------------

check("validateArgs never rejects a plan for a missing reducedGate (pass-execute.js)", () => {
  const { bundle } = load(seqFactory);
  const args = { repo: "/repo", gate: "g", implementer: "i", tasks: [{ id: "1", title: "T", criteria: "c" }] };
  assert.doesNotThrow(() => bundle.validateArgs(args));
});

// A reviewer's outOfScope findings never touch the verdict; the runner keeps every round's
// findings (a fix round's review replaces the record's `review`) and rolls them up per task.
const outOfScopeRoutes = [
  ["base:", baseShaHandler],
  ["impl:1", () => implOk()],
  ["gaterun:", gateRunPass],
  ["review:1:fix", () => ({ ...acceptReview(), outOfScope: [{ location: "b.md:2", finding: "second" }] })],
  ["review:1", () => ({
    ...acceptReview(),
    verdict: "fix",
    blocking: [{ location: "x.js:1", finding: "f", fix: "fx" }],
    outOfScope: [{ location: "a.md:1", finding: "first" }]
  })]
];
const expectedOutOfScope = [
  { task: "1", location: "a.md:1", finding: "first" },
  { task: "1", location: "b.md:2", finding: "second" }
];

check("outOfScope findings from every review round reach the run's result (pass-execute.js)", async () => {
  const args = { repo: "/repo", gate: "g", implementer: "i", classifier: false, tasks: [{ id: "1", title: "T", criteria: "c" }] };
  const { bundle } = load(seqFactory, args, outOfScopeRoutes);
  const result = await bundle.main();
  assert.deepEqual(result.outOfScope, expectedOutOfScope);
  assert.match(bundle.reviewPrompt(args.tasks[0], args, implOk(), { gate: "g" }, null), /outOfScope/);
});

check("outOfScope findings from every review round reach the run's result (pass-execute-chains.js)", async () => {
  const chain = { id: "C", repo: "/repo", branch: "chain-c", classifier: false, tasks: [{ id: "1", title: "T", criteria: "c" }] };
  const args = { gate: "g", implementer: "i", planPath: "/p", chains: [chain] };
  const { bundle } = load(chainsFactory, args, outOfScopeRoutes);
  const result = await bundle.main();
  assert.deepEqual(result.outOfScope, expectedOutOfScope);
});

// -------------------------------------------------------------------------------------------
// Independent gate runner: a Haiku record replaces the reviewer's own gate reproduction.
// -------------------------------------------------------------------------------------------

const failRecord = (extra = {}) => ({ command: "g", exitCode: 1, result: "fail", excerpt: "boom", ...extra });
const gateRunRoutes = (record, extra = []) => [
  ["base:", baseShaHandler],
  ["impl:", () => implOk()],
  ["gaterun:", record],
  ...extra,
  ["review:", () => acceptReview()]
];
const gateRunTask = { id: "1", title: "T", criteria: "c" };
const gateRunArgs = { repo: "/repo", gate: "bash gate.sh", implementer: "i" };
const gateRunChain = { id: "C", repo: "/repo", branch: "b", tasks: [] };
const gateRunChainsArgs = { gate: "bash gate.sh", implementer: "i", planPath: "/p.md", chains: [gateRunChain] };

async function runSeq(record, { t = gateRunTask, a = gateRunArgs, extra = [] } = {}) {
  const { bundle, agent } = load(seqFactory, a, gateRunRoutes(record, extra));
  await bundle.runTask(t, a, false);
  return agent;
}
async function runChains(record, { t = gateRunTask, extra = [] } = {}) {
  const { bundle, agent } = load(chainsFactory, gateRunChainsArgs, gateRunRoutes(record, extra));
  await bundle.runTask(t, gateRunChain, gateRunChainsArgs, false);
  return agent;
}
const reviewPromptOf = (agent, label = "review:1") => agent.calls.find((c) => c.label === label).prompt;

for (const [name, run] of [["pass-execute.js", runSeq], ["pass-execute-chains.js", runChains]]) {
  check(`gate runner: a passing record reaches the reviewer as the gate result (${name})`, async () => {
    const agent = await run(() => ({ command: "bash gate.sh", exitCode: 0, result: "pass", excerpt: "" }));
    const run1 = agent.calls.find((c) => c.label === "gaterun:1");
    assert.equal(run1.opts.model, "haiku");
    assert.equal(run1.opts.effort, "low");
    assert.match(run1.prompt, /bash gate\.sh/);
    const prompt = reviewPromptOf(agent);
    assert.match(prompt, /Independent gate run/);
    assert.match(prompt, /exit code 0, result pass/);
    assert.doesNotMatch(prompt, /Reproduce the gate with/);
  });

  check(`gate runner: a null record restores the Reproduce wording (${name})`, async () => {
    const agent = await run(() => null);
    const prompt = reviewPromptOf(agent);
    assert.match(prompt, /Reproduce the gate with: bash gate\.sh/);
    assert.doesNotMatch(prompt, /Independent gate run/);
  });

  check(`gate runner: a "not run" or inconsistent record falls back (${name})`, async () => {
    for (const rec of [
      { command: "g", exitCode: null, result: "not run", excerpt: "" },
      { command: "g", exitCode: 0, result: "fail", excerpt: "x" },
      { command: "g", exitCode: 2, result: "pass", excerpt: "" },
      { command: "g", exitCode: null, result: "pass", excerpt: "" }
    ]) {
      const prompt = reviewPromptOf(await run(() => rec));
      assert.match(prompt, /Reproduce the gate with: bash gate\.sh/, JSON.stringify(rec));
    }
  });

  check(`gate runner: a <placeholder> gate dispatches no runner (${name})`, async () => {
    const agent = await run(() => failRecord(), { t: { ...gateRunTask, gate: "bash t.sh <the touched unit test files>" } });
    assert.equal(agent.calls.filter((c) => c.label.startsWith("gaterun:")).length, 0);
    assert.match(reviewPromptOf(agent), /Reproduce the gate with:/);
  });

  check(`gate runner: the excerpt is capped at 150 lines and 12000 chars (${name})`, async () => {
    const many = Array.from({ length: 400 }, (_, i) => `line ${i}`).join("\n");
    const agent = await run(() => failRecord({ excerpt: many }));
    const prompt = reviewPromptOf(agent);
    assert.match(prompt, /line 399/);
    assert.doesNotMatch(prompt, /line 249\b/);
    assert.match(prompt, /line 250\b/);
    const wide = Array.from({ length: 150 }, () => "x".repeat(200)).join("\n");
    const agent2 = await run(() => failRecord({ excerpt: wide }));
    const excerpt = reviewPromptOf(agent2).split("Failing output, verbatim from the runner:\n")[1].split("\n")[0];
    assert.ok(excerpt.length <= 12000);
  });
}

const commentOnlyFix = [
  ["review:1:fix", () => acceptReview()],
  ["review:1", () => ({
    verdict: "fix", summary: "", nonBlocking: [], gate: "fail", unspecified: [],
    blocking: [{ location: "x", finding: "y", fix: "z", commentOnly: true }]
  })]
];
const routesWithFix = (record) => [
  ["base:", baseShaHandler],
  ["impl:", () => implOk()],
  ["gaterun:", record],
  ...commentOnlyFix
];

check("gate runner (pass-execute.js): a no-class reduced round runs the resolved gate", async () => {
  const a = { ...gateRunArgs, reducedGate: "bash reduced.sh" };
  const { bundle, agent } = load(seqFactory, a, routesWithFix(gateRunPass));
  await bundle.runTask(gateRunTask, a, false);
  const fixRun = agent.calls.find((c) => c.label === "gaterun:1:fix1");
  assert.match(fixRun.prompt, /bash gate\.sh/);
  assert.doesNotMatch(fixRun.prompt, /reduced\.sh/);
});

check("gate runner (pass-execute.js): a class-reduced round runs the reduced gate and names the full gate as owed", async () => {
  const a = { ...gateRunArgs, passClass: "engine-logic", reducedGate: "bash reduced.sh" };
  const { bundle, agent } = load(seqFactory, a, routesWithFix(gateRunPass));
  await bundle.runTask(gateRunTask, a, false);
  const fixRun = agent.calls.find((c) => c.label === "gaterun:1:fix1");
  assert.match(fixRun.prompt, /bash reduced\.sh/);
  assert.match(reviewPromptOf(agent, "review:1:fix1"), /If the full gate was owed, reproduce it with: bash gate\.sh/);
});

check("gate runner (pass-execute.js): a class-default reduced gate dispatches no runner", async () => {
  const a = { ...gateRunArgs, passClass: "engine-logic" };
  const { bundle, agent } = load(seqFactory, a, routesWithFix(gateRunPass));
  await bundle.runTask(gateRunTask, a, false);
  assert.ok(agent.calls.some((c) => c.label === "gaterun:1"), "first round still runs the gate");
  assert.equal(agent.calls.filter((c) => c.label === "gaterun:1:fix1").length, 0);
  assert.match(reviewPromptOf(agent, "review:1:fix1"), /Reproduce the full gate, if owed, with: bash gate\.sh/);
});

check("gate runner (pass-execute-chains.js): a no-class reduced round runs the resolved gate", async () => {
  const a = { ...gateRunChainsArgs, reducedGate: "bash reduced.sh" };
  const { bundle, agent } = load(chainsFactory, a, routesWithFix(gateRunPass));
  await bundle.runTask(gateRunTask, gateRunChain, a, false);
  const fixRun = agent.calls.find((c) => c.label === "gaterun:1:fix1");
  assert.match(fixRun.prompt, /bash gate\.sh/);
  assert.doesNotMatch(fixRun.prompt, /reduced\.sh/);
});

// -------------------------------------------------------------------------------------------
// Gate receipts and reduced fix rounds (Geoff, 2026-10-08).
// -------------------------------------------------------------------------------------------

check("the receipt and reduced-round helpers are identical source text across both runners", () => {
  for (const name of ["validatedReducedCommand", "gateToRun", "gateRecordLines", "reducedCheckLine", "touchedFiles"]) {
    const re = new RegExp(`\\n(?:async )?function ${name}\\([\\s\\S]*?\\n}\\n`);
    assert.equal(SEQ_SRC.match(re)[0], CHAINS_SRC.match(re)[0], name);
  }
  for (const name of ["CONCRETE_REDUCED_ASK", "TEST_FILE_TOKEN"]) {
    const re = new RegExp(`\\nconst ${name} = .*\\n`);
    assert.equal(SEQ_SRC.match(re)[0], CHAINS_SRC.match(re)[0], name);
  }
});

check("validatedReducedCommand: accepts listed touched test files, rejects anything else", () => {
  const { bundle } = load(seqFactory, {});
  const v = (cmd, files, touched) => bundle.validatedReducedCommand({ gateCommand: cmd, reducedTestFiles: files }, touched, "/repo");
  const cmd = "npm run check && npx vitest run src/a.test.ts";
  assert.equal(v(cmd, ["src/a.test.ts"], ["src/a.test.ts", "src/b.ts"]), cmd);
  assert.equal(v(`cd /repo && CAIRN_GATE_LANE=light cairn-run-gate '${cmd}'`, ["src/a.test.ts"], ["src/a.test.ts"]), cmd, "unwraps cairn-run-gate");
  assert.equal(v("npx vitest run /repo/src/a.test.ts", ["./src/a.test.ts"], ["src/a.test.ts"]), "npx vitest run /repo/src/a.test.ts", "absolute and ./ forms");
  assert.equal(v("npm run check", [], ["src/a.ts"]), "npm run check", "type check only");
  assert.equal(v("npm run check", [], ["src/a.test.ts"]), "", "a touched test file the command skips");
  assert.equal(v(cmd, ["src/a.test.ts"], ["src/a.test.ts", "src/b.test.ts"]), "", "a second touched test file left out");
  assert.equal(v(cmd, ["src/a.test.ts"], ["src/b.ts"]), "", "listed file outside the diff");
  assert.equal(v(cmd, [], ["src/a.test.ts"]), "", "unlisted test file in the command");
  assert.equal(v("npm run check", ["src/a.test.ts"], ["src/a.test.ts"]), "", "listed file absent from the command");
  assert.equal(v("npx vitest run <the touched test files>", [], []), "", "placeholder");
  assert.equal(bundle.validatedReducedCommand({ gateCommand: cmd }, ["src/a.test.ts"], "/repo"), "", "no reducedTestFiles");
  assert.equal(v(cmd, ["src/a.test.ts"], null), "", "touched probe failed");
});

const testOnlyFix = [
  ["review:1:fix", () => acceptReview()],
  ["review:1", () => ({
    verdict: "fix", summary: "", nonBlocking: [], gate: "fail", unspecified: [],
    blocking: [{ location: "x", finding: "y", fix: "z", testOnly: true }]
  })]
];
const concreteCmd = "npm run check && npx vitest run src/a.test.ts";
const reducedRoutes = (fixImpl, touched) => [
  ["base:", baseShaHandler],
  ["impl:1:fix", fixImpl],
  ["impl:", () => implOk()],
  ["touched:", () => ({ files: touched })],
  ["gaterun:", gateRunPass],
  ...testOnlyFix
];
const fixImplWith = (files) => () => implOk({ gateCommand: concreteCmd, reducedTestFiles: files });

for (const [name, factory, runIt] of [
  ["pass-execute.js", seqFactory, (b, t, a) => b.runTask(t, a, false)],
  ["pass-execute-chains.js", chainsFactory, (b, t, a) => b.runTask(t, gateRunChain, a, false)]
]) {
  const baseArgs = name === "pass-execute.js" ? gateRunArgs : gateRunChainsArgs;

  check(`reduced round (${name}): a class round with an explicit reducedGate runs it on the gate agent`, async () => {
    const a = { ...baseArgs, passClass: "engine-logic", reducedGate: "bash reduced.sh" };
    const { bundle, agent } = load(factory, a, reducedRoutes(() => implOk(), []));
    await runIt(bundle, gateRunTask, a);
    assert.match(agent.calls.find((c) => c.label === "gaterun:1:fix1").prompt, /bash reduced\.sh/);
    assert.match(reviewPromptOf(agent, "review:1:fix1"), /If the full gate was owed, reproduce it with: bash gate\.sh/);
    assert.equal(agent.calls.filter((c) => c.label.startsWith("touched:")).length, 0);
  });

  check(`reduced round (${name}): a class-default round runs the validated concrete command`, async () => {
    const a = { ...baseArgs, passClass: "engine-logic" };
    const { bundle, agent } = load(factory, a, reducedRoutes(fixImplWith(["src/a.test.ts"]), ["src/a.test.ts"]));
    await runIt(bundle, gateRunTask, a);
    assert.ok(agent.calls.some((c) => c.label === "base:1:fix1"), "round base recorded");
    const touched = agent.calls.find((c) => c.label === "touched:1:fix1");
    assert.match(touched.prompt, new RegExp(`diff --name-only ${SHA}`));
    assert.equal(touched.opts.model, "haiku");
    assert.ok(agent.calls.findIndex((c) => c.label === "base:1:fix1") < agent.calls.findIndex((c) => c.label === "impl:1:fix1"));
    assert.match(agent.calls.find((c) => c.label === "gaterun:1:fix1").prompt, /npx vitest run src\/a\.test\.ts/);
    assert.match(reviewPromptOf(agent, "review:1:fix1"), /the implementer's concrete command/);
    assert.match(agent.calls.find((c) => c.label === "impl:1:fix1").prompt, /reducedTestFiles/);
  });

  check(`reduced round (${name}): a concrete command naming a file outside the diff falls back`, async () => {
    const a = { ...baseArgs, passClass: "engine-logic" };
    const { bundle, agent } = load(factory, a, reducedRoutes(fixImplWith(["src/a.test.ts"]), ["src/other.ts"]));
    await runIt(bundle, gateRunTask, a);
    assert.equal(agent.calls.filter((c) => c.label === "gaterun:1:fix1").length, 0);
    const prompt = reviewPromptOf(agent, "review:1:fix1");
    assert.match(prompt, /failed the runner's check/);
    assert.match(prompt, /Reproduce the full gate, if owed, with: bash gate\.sh/);
  });

  check(`receipt (${name}): the gate agent looks up a receipt first, with the lane prefix`, async () => {
    const a = { ...baseArgs, gateLane: "light" };
    const { bundle, agent } = load(factory, a, gateRunRoutes(gateRunPass));
    await runIt(bundle, gateRunTask, a);
    const prompt = agent.calls.find((c) => c.label === "gaterun:1").prompt;
    assert.match(prompt, /CAIRN_GATE_LANE=light cairn-run-gate --receipt '<the gate string>'/);
    assert.match(prompt, /The gate string: bash gate\.sh/);
  });

  check(`receipt (${name}): a receipt record reaches the reviewer named as a receipt`, async () => {
    const line = "receipt: exit 0 (log: /s/log) fingerprint abc head def recorded now";
    const agent = await (name === "pass-execute.js" ? runSeq : runChains)(() => ({ command: "bash gate.sh", exitCode: 0, result: "pass", excerpt: "", fromReceipt: true, receipt: line }));
    const prompt = reviewPromptOf(agent);
    assert.match(prompt, /from a cairn-run-gate receipt, not a rerun/);
    assert.ok(prompt.includes(line));
    assert.doesNotMatch(prompt, /Reproduce the gate with/);
  });

  check(`receipt (${name}): a receipt record without a pass receipt line falls back`, async () => {
    const agent = await (name === "pass-execute.js" ? runSeq : runChains)(() => ({ command: "bash gate.sh", exitCode: 0, result: "pass", excerpt: "", fromReceipt: true, receipt: "receipt: none" }));
    assert.match(reviewPromptOf(agent), /Reproduce the gate with: bash gate\.sh/);
  });
}

// -------------------------------------------------------------------------------------------
// CI pipelining (pass-execute.js, sequential only): the runner pushes after every implementer
// commit and runs ci-green through probe agents. Every case drives main() through a scripted
// agent mock and reads which labels were dispatched, and in what order.
// -------------------------------------------------------------------------------------------

/**
 * Routes for a CI run. `ciExits` maps a task id to the ci-green exits its probe reports, one per
 * dispatch (the last repeats). `gatetier` maps a task id to extra gate-probe fields. `reviews`
 * maps a label to a queue of review verdicts.
 */
function ciHarness({ tasks, ciExits = {}, gatetier = {}, reviews = {}, push = null, args: extra = {} }) {
  const order = [];
  let pushN = 0;
  const shaOf = {};
  const queues = {};
  for (const [k, v] of Object.entries(ciExits)) queues[k] = [...v];
  const routes = [
    ["classifier", () => ({ exists: true })],
    ["base:", baseShaHandler],
    ["impl:", (_p, o) => { order.push(o.label); return implOk(); }],
    ["push:", (_p, o) => {
      order.push(o.label);
      if (push) return push(o.label);
      pushN += 1;
      const rec = { sha: `sha${pushN}`, pushedAt: `2026-10-10T00:00:0${pushN}Z`, pushed: true };
      shaOf[o.label] = rec.sha;
      return rec;
    }],
    ["gatetier:", (_p, o) => {
      const id = o.label.split(":")[1];
      return { exists: true, gate: "computed gate", protectedExit: 0, protectedOut: "", ...(gatetier[id] || {}) };
    }],
    ["gaterun:", gateRunPass],
    ["review:", (_p, o) => {
      const q = reviews[o.label];
      return q && q.length ? q.shift() : acceptReview();
    }],
    ["ci:", (prompt, o) => {
      order.push(o.label);
      const id = o.label.split(":")[1];
      const q = queues[id] || [{ exitCode: 0, output: "" }];
      const next = q.length > 1 ? q.shift() : q[0];
      return typeof next === "number" ? { exitCode: next, output: "" } : next;
    }]
  ];
  const args = { repo: "/repo", gate: "g", implementer: "i", ci: { pr: 7 }, tasks, ...extra };
  const loaded = load(seqFactory, args, routes);
  return { ...loaded, order, args };
}

const T = (id, extra = {}) => ({ id, title: `T${id}`, criteria: "c", ...extra });
const idx = (order, label) => order.indexOf(label);
const labelsOf = (agent, prefix) => agent.calls.filter((c) => c.label.startsWith(prefix)).map((c) => c.label);

check("ci: green dispatches N+2 after N+1, and N+1 starts before N's check", async () => {
  const h = ciHarness({ tasks: [T("1"), T("2"), T("3")] });
  const result = await h.bundle.main();
  assert.equal(result.ciRed, undefined);
  assert.equal(result.ciUnavailable, undefined);
  assert.deepEqual(result.tasks.map((t) => t.status), ["accepted", "accepted", "accepted"]);
  assert.ok(idx(h.order, "impl:2") < idx(h.order, "ci:1"), "N+1 is dispatched without waiting on N");
  assert.ok(idx(h.order, "ci:1") < idx(h.order, "impl:3"), "N's CI is read before N+2 starts");
  const prompt = h.agent.calls.find((c) => c.label === "ci:1").prompt;
  assert.match(prompt, /ci-green sha1 --pr 7 --wait --pushed-at 2026-10-10T00:00:01Z --task 1/);
  assert.equal(h.agent.calls.find((c) => c.label === "ci:1").opts.model, "haiku");
});

check("ci: a red N halts after N+1 finishes and returns the ciRed record", async () => {
  const detail = "FAIL test.yml / unit / vitest: foo.test.ts\nmain: test success";
  const h = ciHarness({ tasks: [T("1"), T("2"), T("3")], ciExits: { "1": [{ exitCode: 1, output: detail }] } });
  const result = await h.bundle.main();
  assert.ok(h.order.includes("impl:2"), "N+1 finishes its chain");
  assert.ok(!h.order.includes("impl:3"), "N+2 is never dispatched");
  assert.deepEqual(result.tasks.map((t) => t.status), ["accepted", "accepted", "skipped"]);
  assert.deepEqual(result.ciRed, { sha: "sha1", task: "1", verdict: "red", exitCode: 1, detail });
  assert.equal(result.ciUnavailable, undefined);
});

check("ci: a missing N (exit 2) halts the same way", async () => {
  const h = ciHarness({ tasks: [T("1"), T("2"), T("3")], ciExits: { "1": [{ exitCode: 2, output: "no runs" }] } });
  const result = await h.bundle.main();
  assert.ok(h.order.includes("impl:2"));
  assert.ok(!h.order.includes("impl:3"));
  assert.equal(result.ciRed.verdict, "missing");
  assert.equal(result.ciRed.sha, "sha1");
  assert.equal(result.ciRed.exitCode, 2);
});

check("ci: unavailable (exit 3, or any exit outside the five codes) halts with the ciUnavailable record", async () => {
  for (const code of [3, 127, null]) {
    const h = ciHarness({ tasks: [T("1"), T("2"), T("3")], ciExits: { "1": [{ exitCode: code, output: "no ci-green.json" }] } });
    const result = await h.bundle.main();
    assert.ok(!h.order.includes("impl:3"), `exit ${code}: N+2 is never dispatched`);
    assert.equal(result.ciRed, undefined);
    assert.equal(result.ciUnavailable.sha, "sha1");
    assert.equal(result.ciUnavailable.task, "1");
    assert.equal(result.ciUnavailable.exitCode, code);
    assert.deepEqual(result.tasks.map((t) => t.status), ["accepted", "accepted", "skipped"]);
  }
});

check("ci: pending (75, then 0) waits by re-dispatching the probe, then resolves", async () => {
  const h = ciHarness({ tasks: [T("1"), T("2"), T("3")], ciExits: { "1": [75, 0] } });
  const result = await h.bundle.main();
  assert.equal(labelsOf(h.agent, "ci:").length, 2);
  assert.ok(h.order.includes("impl:3"));
  assert.equal(result.ciRed, undefined);
  assert.match(h.agent.calls.find((c) => c.label === "ci:1").prompt, /re-issue/);
});

check("ci: a check still pending after CI_MAX_WAITS dispatches halts as ciUnavailable with exit 75", async () => {
  const h = ciHarness({ tasks: [T("1"), T("2"), T("3")], ciExits: { "1": [75] } });
  const result = await h.bundle.main();
  assert.equal(labelsOf(h.agent, "ci:").length, 12);
  assert.ok(!h.order.includes("impl:3"));
  assert.equal(result.ciRed, undefined);
  assert.equal(result.ciUnavailable.exitCode, 75);
  assert.equal(result.ciUnavailable.task, "1");
});

check("ci: the unread heads are logged and listed in ci.unchecked", async () => {
  const h = ciHarness({ tasks: [T("1"), T("2")] });
  const result = await h.bundle.main();
  assert.deepEqual(result.ci.unchecked.map((u) => [u.task, u.sha]), [["1", "sha1"], ["2", "sha2"]]);
  const line = h.log.lines.find((l) => /never read green/.test(l));
  assert.match(line, /task 1 sha1/);
  assert.match(line, /task 2 sha2/);
});

check("ci: a push reported pushed with an empty pushedAt counts as a failed push", async () => {
  const h = ciHarness({ tasks: [T("1"), T("2"), T("3")], push: () => ({ sha: "s", pushedAt: "", pushed: true }) });
  const result = await h.bundle.main();
  assert.ok(!h.order.includes("impl:3"));
  assert.equal(result.ciUnavailable.task, "1");
  assert.match(result.ciUnavailable.reason, /push/);
  assert.equal(labelsOf(h.agent, "ci:").length, 0);
});

check("ci: an auth-data task blocks N+1's dispatch until green", async () => {
  const h = ciHarness({ tasks: [T("1", { passClass: "auth-data" }), T("2")] });
  await h.bundle.main();
  assert.ok(idx(h.order, "ci:1") !== -1 && idx(h.order, "ci:1") < idx(h.order, "impl:2"));
  const red = ciHarness({ tasks: [T("1", { passClass: "auth-data" }), T("2")], ciExits: { "1": [{ exitCode: 1, output: "boom" }] } });
  const result = await red.bundle.main();
  assert.ok(!red.order.includes("impl:2"), "a red wait leaves N+1 undispatched");
  assert.equal(result.ciRed.task, "1");
  assert.equal(result.tasks[1].status, "skipped");
});

check("ci: a task with its own ciWait: true blocks N+1's dispatch until green", async () => {
  const h = ciHarness({ tasks: [T("1", { ciWait: true }), T("2")] });
  await h.bundle.main();
  assert.ok(idx(h.order, "ci:1") !== -1 && idx(h.order, "ci:1") < idx(h.order, "impl:2"));
});

check("ci: a task whose gate probe reports a protected-path touch blocks N+1's dispatch until green", async () => {
  const h = ciHarness({ tasks: [T("1"), T("2")], gatetier: { "1": { protectedOut: "ciWait" } } });
  await h.bundle.main();
  assert.ok(idx(h.order, "ci:1") !== -1 && idx(h.order, "ci:1") < idx(h.order, "impl:2"));
  const plain = ciHarness({ tasks: [T("1"), T("2")] });
  await plain.bundle.main();
  assert.ok(!plain.order.includes("ci:1"), "an unflagged task does not wait");
});

check("ci: a pinned task is still probed for --protected, keeps its pinned gate, and waits when flagged", async () => {
  const h = ciHarness({ tasks: [T("1", { gateTier: "full", gate: "pinned gate" }), T("2")], gatetier: { "1": { protectedOut: "ciWait" } } });
  const result = await h.bundle.main();
  const probe = h.agent.calls.find((c) => c.label === "gatetier:1");
  assert.ok(probe, "a pin no longer skips the gate probe");
  assert.match(probe.prompt, /gate-tier\.mjs --range [a]{40}\.\.HEAD --protected/);
  assert.doesNotMatch(probe.prompt, /gate-tier\.mjs --range [a]{40}\.\.HEAD(?! --protected)/, "the pinned gate string is never recomputed");
  assert.match(h.agent.calls.find((c) => c.label === "gaterun:1").prompt, /The gate string: pinned gate/);
  assert.ok(idx(h.order, "ci:1") < idx(h.order, "impl:2"));
  assert.equal(result.tasks[0].status, "accepted");
  const direct = await load(seqFactory, {}, [["g", () => ({ exists: true, gate: "", protectedExit: 0, protectedOut: "" })]])
    .bundle.resolveGate({ id: "1", gateTier: "full", gate: "pinned gate" }, { gate: "x", ci: { pr: 7 } }, SHA, true, "g");
  assert.deepEqual(direct, { gate: "pinned gate", source: "pin", tier: "full", ciWait: false });
});

check("ci: a --protected run that exits non-zero, or never reports, counts as ciWait; an absent classifier does not", async () => {
  const wait = async (fields) => {
    const { bundle } = load(seqFactory, {}, [["g", () => ({ exists: true, gate: "x", ...fields })]]);
    return (await bundle.resolveGate({ id: "1" }, { gate: "g", ci: { pr: 7 } }, SHA, true, "g")).ciWait;
  };
  assert.equal(await wait({ protectedExit: 0, protectedOut: "" }), false);
  assert.equal(await wait({ protectedExit: 0, protectedOut: "ciWait\n" }), true);
  assert.equal(await wait({ protectedExit: 2, protectedOut: "" }), true);
  assert.equal(await wait({ protectedExit: null, protectedOut: "" }), true);
  assert.equal(await wait({}), true, "an omitted exit code fails closed");
  const absent = load(seqFactory, {}, [["g", () => ({ exists: false, gate: "" })]]);
  assert.equal((await absent.bundle.resolveGate({ id: "1" }, { gate: "g", ci: { pr: 7 } }, SHA, true, "g")).ciWait, false);
  const p = load(seqFactory, {}, [["g", () => ({ exists: true, gate: "x", protectedExit: 0, protectedOut: "" })]]);
  await p.bundle.resolveGate({ id: "1" }, { gate: "g", ci: { pr: 7 } }, SHA, true, "g");
  assert.match(p.agent.calls[0].prompt, /--protected/);
  assert.match(p.agent.calls[0].prompt, /non-zero/);
});

check("ci: no ci argument never pushes and never calls ci-green, and the gate probe stays as before", async () => {
  const h = ciHarness({ tasks: [T("1", { passClass: "auth-data" }), T("2"), T("3")], args: { ci: undefined } });
  const result = await h.bundle.main();
  assert.equal(h.agent.calls.filter((c) => /^(push|ci):/.test(c.label)).length, 0);
  assert.doesNotMatch(h.agent.calls.find((c) => c.label === "gatetier:2").prompt, /--protected/);
  assert.equal(result.ci, undefined);
  assert.equal(result.tasks.every((t) => t.ci === undefined), true);
});

check("ci: parallel: true never pushes and never calls ci-green", async () => {
  const h = ciHarness({ tasks: [T("1", { passClass: "auth-data" }), T("2")], args: { parallel: true } });
  await h.bundle.main();
  assert.equal(h.agent.calls.filter((c) => /^(push|ci):/.test(c.label)).length, 0);
});

check("ci: a fix round's commit is pushed, and the check reads the pushed head", async () => {
  const fixReview = { verdict: "fix", summary: "", blocking: [{ location: "x", finding: "f", fix: "g" }], nonBlocking: [], gate: "pass", unspecified: [] };
  const h = ciHarness({ tasks: [T("1"), T("2")], reviews: { "review:1": [fixReview] } });
  await h.bundle.main();
  assert.deepEqual(labelsOf(h.agent, "push:"), ["push:1", "push:1:fix1", "push:2"]);
  assert.ok(idx(h.order, "push:1:fix1") > idx(h.order, "impl:1:fix1"));
});

check("ci: the push precedes the review, and the accepted SHA is the last push", async () => {
  const fixReview = { verdict: "fix", summary: "", blocking: [{ location: "x", finding: "f", fix: "g" }], nonBlocking: [], gate: "pass", unspecified: [] };
  const h = ciHarness({ tasks: [T("1", { ciWait: true }), T("2")], reviews: { "review:1": [fixReview] } });
  const result = await h.bundle.main();
  const calls = h.agent.calls.map((c) => c.label);
  assert.ok(calls.indexOf("push:1") < calls.indexOf("review:1"));
  assert.ok(calls.indexOf("push:1:fix1") < calls.indexOf("review:1:fix1"));
  assert.match(h.agent.calls.find((c) => c.label === "ci:1").prompt, /ci-green sha2 /);
  assert.equal(result.tasks[0].ci.sha, "sha2");
});

check("ci: a failed push surfaces as ciUnavailable when that task's check comes due", async () => {
  const h = ciHarness({ tasks: [T("1"), T("2"), T("3")], push: (label) => (label === "push:1" ? { sha: "", pushedAt: "", pushed: false } : { sha: "s", pushedAt: "2026-10-10T00:00:00Z", pushed: true }) });
  const result = await h.bundle.main();
  assert.ok(!h.order.includes("impl:3"));
  assert.equal(result.ciUnavailable.task, "1");
  assert.match(result.ciUnavailable.reason, /push/);
  assert.equal(labelsOf(h.agent, "ci:").length, 0);
});

check("ci: validateArgs rejects a ci object without a numeric pr", () => {
  const { bundle } = load(seqFactory);
  const base = { repo: "/r", gate: "g", implementer: "i", tasks: [T("1")] };
  assert.doesNotThrow(() => bundle.validateArgs({ ...base, ci: { pr: 7 } }));
  assert.throws(() => bundle.validateArgs({ ...base, ci: {} }), /ci\.pr/);
  assert.throws(() => bundle.validateArgs({ ...base, ci: { pr: "x" } }), /ci\.pr/);
});

check("ci: auth-data carries ciWait in both runners, and no other class does", () => {
  for (const factory of [seqFactory, chainsFactory]) {
    const { bundle } = load(factory);
    for (const [name, cls] of Object.entries(bundle.PASS_CLASSES)) {
      assert.equal(cls.ciWait === true, name === "auth-data", name);
    }
  }
});

check("classifier commands carry --class when a class is set, and omit it otherwise (both runners)", async () => {
  const t = { id: "1", title: "T", criteria: "c", passClass: "auth-data" };
  const a = { repo: "/repo", gate: "g", implementer: "i" };
  const seq = load(seqFactory, {}, [["g", () => ({ exists: true, gate: "x", protectedExit: 0, protectedOut: "" })]]);
  assert.match(seq.bundle.implementPrompt(t, a, null, "deadbeef", true), /--range deadbeef\.\.HEAD --class auth-data/);
  assert.doesNotMatch(seq.bundle.implementPrompt({ ...t, passClass: undefined }, a, null, "deadbeef", true), /--class/);
  await seq.bundle.resolveGate(t, a, "deadbeef", true, "g");
  assert.match(seq.agent.calls[0].prompt, /--range deadbeef\.\.HEAD --class auth-data/);
  const pinned = seq.bundle.implementPrompt({ ...t, gateTier: "full" }, a, null, "deadbeef", true);
  assert.doesNotMatch(pinned, /gate-tier\.mjs --range/);

  const chn = load(chainsFactory, {}, [["g", () => ({ exists: true, gate: "x" })]]);
  const chain = { id: "C", repo: "/repo", branch: "b" };
  assert.match(chn.bundle.implementPrompt(t, chain, a, null, "deadbeef", true), /--range deadbeef\.\.HEAD --class auth-data/);
  assert.doesNotMatch(chn.bundle.implementPrompt({ ...t, passClass: undefined }, chain, a, null, "deadbeef", true), /--class/);
  await chn.bundle.resolveGate(t, chain, a, "deadbeef", true, "P", "g");
  assert.match(chn.agent.calls[0].prompt, /--range deadbeef\.\.HEAD --class auth-data/);
});

console.log("");
await runChecks();
if (failures.length) {
  console.log(`${failures.length} FAILING: ${failures.join(", ")}`);
  process.exit(1);
}
console.log("ALL PASS");
