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
// Run with: node docs-page-chain-v2.fixture.test.mjs
// Exits 0 with "ALL PASS" on success, prints failures and exits 1 otherwise. No dependencies
// beyond the Node runtime (this repo has no package.json / test runner to plug into).

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import assert from "node:assert/strict";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC_PATH = join(HERE, "docs-page-chain-v2.js");
const SRC = readFileSync(SRC_PATH, "utf8");

const failures = [];
function check(name, fn) {
  try {
    fn();
    console.log(`ok - ${name}`);
  } catch (e) {
    failures.push(name);
    console.log(`FAIL - ${name}`);
    console.log(`  ${e && e.stack || e}`);
  }
}
async function checkAsync(name, fn) {
  try {
    await fn();
    console.log(`ok - ${name}`);
  } catch (e) {
    failures.push(name);
    console.log(`FAIL - ${name}`);
    console.log(`  ${e && e.stack || e}`);
  }
}

// ---------------------------------------------------------------------------------------------
// Static checks against the source text: cheap, and they are exactly what the acceptance
// bullets ask for ("the v2 source names check:provenance", "no profile-grader agent").
// ---------------------------------------------------------------------------------------------

check("v2 source's page gate names check:provenance", () => {
  assert.match(SRC, /check:provenance/);
  // it must be in the gate-building function, not just a comment
  assert.match(SRC, /const gateFor = \(p\) => \{[\s\S]*?check:provenance[\s\S]*?\};/);
});

check("v2 source names no profile-grader agent", () => {
  // The header prose documents the removal ("never scores a ... profile grader"); what must be
  // absent is the agent call itself: its prompt builder, its schema, and any agent() dispatch
  // carrying that label.
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
  assert.match(SRC, /function factPrompt\(p\)/);
  assert.match(SRC, /READ_SCHEMA/);
  assert.match(SRC, /label: `fact:\$\{p\.id\}`/);
});

check("the handoff write resolves the cache path, never a path under the worktree", () => {
  assert.match(SRC, /XDG_CACHE_HOME/);
  assert.match(SRC, /docs-page-chain\/handoffs/);
  assert.match(SRC, /\.cache\/docs-page-chain\/handoffs/);
});

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
    return agentImpl(prompt, opts, calls.length);
  };
  const parallel = async (thunks) => Promise.all(thunks.map((t) => t().catch(() => null)));
  const phase = () => {};
  const log = () => {};
  const budget = { total: null, spent: () => 0, remaining: () => Infinity };
  const workflow = async () => { throw new Error("nesting not used by this script"); };
  return { agent, parallel, phase, log, budget, workflow, calls };
}

const PAGE = {
  id: "is-it-working",
  path: "docs/admin/is-it-working.md",
  brief: "Explain cairn doctor.",
  inputs: ["docs/superpowers/plans/x.mining.md#is-it-working"],
  exemplar: "docs/admin/other.md",
  pinned: []
};

const BASE_ARGS = {
  worktree: "/tmp/wt",
  gate: "npm run check:docs",
  profile: "The admin track profile, verbatim.",
  runId: "fixture-run"
};

await checkAsync("stage 1 dispatches a fact read alongside the editor, and the editor prompt carries the omission checklist and asks for reader jobs", async () => {
  let factCalled = false;
  const h = stubHarness((prompt, opts) => {
    if (opts.label === "draft:is-it-working") {
      return { path: PAGE.path, gate: "pass", gateCommand: "cairn-run-gate '...'" };
    }
    if (opts.label === "editor:is-it-working") {
      assert.match(prompt, /Every prerequisite the reader needs/);
      assert.match(prompt, /Every value the reader must supply themselves/);
      assert.match(prompt, /Every failure a step on this page can produce/);
      assert.match(prompt, /version and platform scope/);
      assert.match(prompt, /where the reader goes next/i);
      assert.match(prompt, /readerJobs/);
      return {
        verdict: "fix",
        findings: [{ location: "para 2", finding: "missing a failure mode", blocking: true, rewrite: "add it" }],
        omissions: [{ item: "version and platform scope", status: "missing", evidence: "no version line" }],
        readerJobs: [{ id: "r1", task: "run cairn doctor", doneSignal: "prints a verdict" }],
        summary: "one blocking finding, one omission"
      };
    }
    if (opts.label === "fact:is-it-working") {
      factCalled = true;
      assert.match(prompt, /Fact read of/);
      assert.match(prompt, /joining two neighboring manifest entries/);
      return {
        verdict: "fix",
        findings: [{ location: "para 3", finding: "composed from two manifest entries no source states together", blocking: true }],
        summary: "one blocking finding"
      };
    }
    if (opts.label === "handoff-write") {
      assert.match(prompt, /XDG_CACHE_HOME/);
      assert.match(prompt, /docs-page-chain\/handoffs\/fixture-run\.json/);
      assert.doesNotMatch(prompt, /\/tmp\/wt\/docs-page-chain\/handoffs/, "the handoff must not be written under the worktree");
      return { path: "/home/glw907/.cache/docs-page-chain/handoffs/fixture-run.json" };
    }
    throw new Error(`unexpected agent call: ${opts.label}`);
  });
  const result = await run({ ...BASE_ARGS, stage: 1, pages: [PAGE] }, h.agent, h.parallel, h.phase, h.log, h.budget, h.workflow);
  assert.ok(factCalled, "stage 1 must dispatch a fact read");
  assert.equal(result.handoffPath, "/home/glw907/.cache/docs-page-chain/handoffs/fixture-run.json");
  assert.equal(result.pages[0].status, "handed-off");
  assert.equal(result.readerJobCount, 1);
});

await checkAsync("applied-findings read returns a verdict per finding on a fixture redraft, and a page with a blocking finding not applied escalates without a third round", async () => {
  const page = {
    id: "is-it-working",
    path: PAGE.path,
    briefPath: "docs/internal/briefs/admin/is-it-working.json",
    status: "handed-off",
    draft: { brief: PAGE.brief, inputs: PAGE.inputs, exemplar: PAGE.exemplar, pinned: PAGE.pinned },
    editorFindings: [
      { location: "para 2", finding: "missing a failure mode", blocking: true, rewrite: "add it" },
      { location: "para 4", finding: "a tricolon", blocking: false, rewrite: "cut to one item" }
    ],
    factFindings: [
      { location: "para 3", finding: "composed from two manifest entries no source states together", blocking: true }
    ],
    omissions: [{ item: "version and platform scope", status: "missing", evidence: "no version line" }],
    readerJobs: []
  };

  let redraftCalls = 0;
  let appliedCalls = 0;
  const h = stubHarness((prompt, opts) => {
    if (opts.label === "load-handoff") return { pages: [page] };
    if (opts.label === "load-reader-results") {
      return { results: [{ jobId: "is-it-working:r1", pageId: "is-it-working", verified: true, report: "the doctor command in step 3 fails as written" }] };
    }
    if (opts.label && opts.label.startsWith("redraft:")) {
      redraftCalls += 1;
      // the redraft prompt must apply every finding, blocking or advisory (item 3's ruling),
      // must carry the fact read's finding, and must carry the verified reader report.
      assert.match(prompt, /applying every finding below, blocking or advisory/);
      assert.match(prompt, /a tricolon/);
      assert.match(prompt, /composed from two manifest entries/);
      assert.match(prompt, /doctor command in step 3 fails/);
      return { path: PAGE.path, gate: "pass", gateCommand: "cairn-run-gate '...'" };
    }
    if (opts.label && opts.label.startsWith("applied:")) {
      appliedCalls += 1;
      assert.match(prompt, /composed from two manifest entries/, "the fact read's finding must reach the applied-findings read too");
      return {
        perFinding: [
          { location: "para 2", finding: "missing a failure mode", blocking: true, status: "not applied", evidence: "still absent" },
          { location: "para 4", finding: "a tricolon", blocking: false, status: "applied", evidence: "cut to one item" },
          { location: "para 3", finding: "composed from two manifest entries no source states together", blocking: true, status: "applied", evidence: "split into two sentences" }
        ],
        newIssues: [],
        summary: "one blocking finding not applied"
      };
    }
    throw new Error(`unexpected agent call: ${opts.label}`);
  });

  const result = await run({ ...BASE_ARGS, stage: 2, handoffPath: "docs/internal/handoffs/fixture-run.json", resultsDir: "/tmp/results" }, h.agent, h.parallel, h.phase, h.log, h.budget, h.workflow);

  assert.equal(redraftCalls, 1, "exactly one redraft round runs (the two-round cap)");
  assert.equal(appliedCalls, 1, "exactly one applied-findings read runs");
  assert.equal(result.pages.length, 1);
  const p = result.pages[0];
  assert.equal(p.status, "escalate", "a blocking finding marked not applied stays unresolved");
  assert.equal(p.unresolved.length, 1);
  assert.equal(p.unresolved[0].location, "para 2");
  // No agent call is a second redraft or a second applied-findings read: the cap is structural
  // (redraftPage never loops), not merely a count this fixture happens to hit.
  assert.equal(h.calls.filter((c) => c.opts.label && c.opts.label.startsWith("redraft:")).length, 1);
  assert.equal(h.calls.filter((c) => c.opts.label && c.opts.label.startsWith("applied:")).length, 1);
});

await checkAsync("a page whose redraft applies every blocking finding is accepted", async () => {
  const page = {
    id: "is-it-working",
    path: PAGE.path,
    briefPath: "docs/internal/briefs/admin/is-it-working.json",
    status: "handed-off",
    draft: { brief: PAGE.brief, inputs: PAGE.inputs, exemplar: PAGE.exemplar, pinned: PAGE.pinned },
    editorFindings: [{ location: "para 2", finding: "missing a failure mode", blocking: true, rewrite: "add it" }],
    omissions: [],
    readerJobs: []
  };
  const h = stubHarness((prompt, opts) => {
    if (opts.label === "load-handoff") return { pages: [page] };
    if (opts.label === "load-reader-results") return { results: [] };
    if (opts.label && opts.label.startsWith("redraft:")) return { path: PAGE.path, gate: "pass", gateCommand: "cairn-run-gate '...'" };
    if (opts.label && opts.label.startsWith("applied:")) {
      return {
        perFinding: [{ location: "para 2", finding: "missing a failure mode", blocking: true, status: "applied", evidence: "now present" }],
        newIssues: [],
        summary: "applied"
      };
    }
    throw new Error(`unexpected agent call: ${opts.label}`);
  });
  const result = await run({ ...BASE_ARGS, stage: 2, handoffPath: "x", resultsDir: "/tmp/results" }, h.agent, h.parallel, h.phase, h.log, h.budget, h.workflow);
  assert.equal(result.pages[0].status, "accepted");
});

console.log("");
if (failures.length) {
  console.log(`${failures.length} FAILING: ${failures.join(", ")}`);
  process.exit(1);
}
console.log("ALL PASS");
