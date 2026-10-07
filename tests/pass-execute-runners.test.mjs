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
  "reviewPrompt", "validateArgs", "runTask", "runChain", "tally"
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

console.log("");
await runChecks();
if (failures.length) {
  console.log(`${failures.length} FAILING: ${failures.join(", ")}`);
  process.exit(1);
}
console.log("ALL PASS");
