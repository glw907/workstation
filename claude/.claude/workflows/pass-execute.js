// Runs a pass plan's task list through the thin-conductor chain: implement,
// review, fix-loop, gate. The conductor invokes this instead of dispatching
// the chain per task inline.
//
// Invocation from the conductor session: by name, never by path and never from a scratchpad
// copy (a copy would make a later edit to this file invisible to the run).
//
//   Workflow({
//     name: "pass-execute",
//     args: {
//       repo: "/home/glw907/Projects/<repo>",
//       gate: "npm run check && npm test",
//       implementer: "cairn-implementer",
//       reviewer: "diff-reviewer",       // optional, defaults below
//       maxFix: 1,                        // optional, defaults below
//       parallel: false,                  // optional, defaults to sequential
//       reducedGate: "...",               // optional; the gate string a fix round runs
//                                         // when every blocking finding is commentOnly
//                                         // (or, under a passClass, commentOnly/testOnly).
//                                         // Absent, and no passClass, means every round
//                                         // runs the full gate, the unchanged behavior.
//       passClass: "paint",               // optional; see "Pass class" below. A task's own
//                                         // `passClass` overrides it for that task.
//       reviewerModel: "sonnet",          // optional; overrides the class's reviewer model.
//       stopOnEscalate: true,             // optional; sequential runs only, defaults to true.
//                                         // See "Stop on an unaccepted task" below.
//       commonNotes: "...",               // optional; appended after every task's own
//                                         // `notes` line in the implement prompt. Absent
//                                         // adds nothing, matching today's prompts.
//       tasks: [
//         { id: "1", title: "...", criteria: "...", files: ["..."], notes: "...",
//           passClass: "engine-logic", gate: "...", reducedGate: "..." }  // last three optional
//       ]
//     }
//   })
//
// `repo` is prompt text only: the runner never reads or writes that path itself, it only
// hands the string to the dispatched agents. Every gate string (`gate`, `reducedGate`, a
// task's own `gate`) is absolute per tree, since the runner has no working directory of its
// own to resolve a relative one against.
//
// The conductor reads only the returned per-task records. It never reads a
// diff, a gate transcript, or an agent's full report; the review step already
// did that.
//
// One invocation runs one segment. The runner has no mid-run conductor hook, so a pass
// carrying conductor checkpoint or segment boundaries is launched one invocation per segment;
// the conductor's checkpoint and any batched simplifier round fall between invocations, not
// inside one.
//
// Gate tier (Geoff, 2026-09-15): when `<a.repo>/scripts/checks/gate-tier.mjs` exists, the gate
// string for a task is chosen from its committed diff rather than fixed by the plan. A task may
// carry `gateTier` to pin a tier the diff cannot size (a token value); a task's `paint` flag
// (true/false) is passed through as the classifier's `--paint` flag. The implementer runs the
// classifier itself (its prompt says how) and reports the tier and string it ran; the runner
// independently resolves the same tier via a probe agent and hands the reviewer both, flagging a
// mismatch as blocking. The workflow runtime has no filesystem or exec access, so every git/node
// call here goes through a small probe agent rather than direct code.

// Gate lane (Geoff, 2026-09-20): `args.gateLane` or a task's `gateLane` set to "light" makes the
// implementer prefix every cairn-run-gate call with CAIRN_GATE_LANE=light, for a gate that launches
// no browser. Unset means the default heavy lane.

// Stop on an unaccepted task (2026-09-23): in a sequential run, a task whose final status is not
// "accepted" (a reviewer escalate, a fix verdict still standing after maxFix rounds, an accept
// without a passing gate, or a failed dispatch) ends the run, because every later task would
// build and commit on top of an unaccepted one. The run returns that task's record and marks
// every task after it "skipped". Set `stopOnEscalate: false` to run the whole list regardless.
// A parallel run never stops early, since its tasks are independent by the plan's own marking.
// pass-execute-chains.js already halts a chain the same way.

// Pass class (Geoff, 2026-09-27): `args.passClass`, or a task's own `passClass`, names the kind of
// change, and the class sets the ceremony instead of one chain for every task. The runner renders
// the class's test mandate into the implementer prompt and its blocking bar into the reviewer
// prompt, and enforces two parts in code: under a class whose coverage does not block, a blocking
// finding the reviewer marks `coverageOnly` moves to nonBlocking (a `fix` verdict left with no
// blocking finding becomes `accept`), and the demoted notes return on the task record as
// `batchedNotes` for the segment boundary; and a fix round whose findings are all `commentOnly` or
// `testOnly` runs the reduced gate (`t.reducedGate`, `args.reducedGate`, or the class default: the
// repo's type check plus the test files the fix touched), except under `auth-data`, where only a
// comment-only round reduces. The per-task gate itself stays the plan's (`t.gate` or `args.gate`);
// a `paint` plan names a targeted gate per task. The `tool` class defaults to the light gate lane.
// Born of the theme identity pass A evaluation: a CSS retheme ran the full engine gate per task,
// at about 4.4 test lines per source line, and every test-only fix round reran the full gate.
// Without a passClass every prompt and verdict is exactly the pre-class behavior.
// Keep PASS_CLASSES in step with pass-execute-chains.js.

export const meta = {
  name: "pass-execute",
  description: "Runs a pass plan's tasks through implementer, diff-reviewer, and gate in a chain. One invocation runs one segment; a pass with conductor boundaries is launched once per segment.",
  whenToUse: "A pass plan names the workflow mode, or the pass has six or more tasks, or the plan marks tasks independent.",
  phases: [
    { title: "Implement", detail: "one implementer dispatch per task, plus fix rounds" },
    { title: "Review", detail: "diff-reviewer verdict per dispatch" },
    { title: "Report", detail: "tally and per-task records" }
  ]
};

const IMPL_SCHEMA = {
  type: "object",
  properties: {
    filesTouched: { type: "array", items: { type: "string" } },
    gate: { type: "string", enum: ["pass", "fail", "not run"] },
    gateOutput: { type: "string" },
    // Both optional, present only when the repo has a gate-tier classifier
    // script (scripts/checks/gate-tier.mjs): gateTier is "pin", "computed",
    // or "default"; gateCommand is the exact gate string the implementer ran.
    gateTier: { type: "string" },
    gateCommand: { type: "string" },
    // Optional: one row per mutation the plan named for this task. Never in
    // `required`, since a consumer whose implementer definition does not name
    // mutations must not be asked for it.
    mutationLedger: {
      type: "array",
      items: {
        type: "object",
        properties: {
          mutation: { type: "string" },
          site: { type: "string" },
          provingTest: { type: "string" },
          fired: { type: "boolean" }
        },
        required: ["mutation", "fired"]
      }
    },
    unspecifiedDecisions: { type: "array", items: { type: "string" } },
    couldNotDo: { type: "array", items: { type: "string" } },
    summary: { type: "string" }
  },
  required: ["filesTouched", "gate", "gateOutput", "unspecifiedDecisions", "couldNotDo", "summary"]
};

const GATE_PROBE_SCHEMA = {
  type: "object",
  properties: {
    sha: { type: "string" }
  },
  required: ["sha"]
};

const GATE_TIER_SCHEMA = {
  type: "object",
  properties: {
    exists: { type: "boolean" },
    gate: { type: "string" }
  },
  required: ["exists", "gate"]
};

const REVIEW_SCHEMA = {
  type: "object",
  properties: {
    verdict: { type: "string", enum: ["accept", "fix", "escalate"] },
    summary: { type: "string" },
    blocking: {
      type: "array",
      items: {
        type: "object",
        properties: {
          location: { type: "string" },
          finding: { type: "string" },
          fix: { type: "string" },
          // Both optional, for the same shared-asset reason as mutationLedger.
          commentOnly: { type: "boolean" },
          // Both optional, read only under a passClass: testOnly means the fix touches test
          // files alone; coverageOnly means the finding is test coverage or granularity with
          // no behavior defect.
          testOnly: { type: "boolean" },
          coverageOnly: { type: "boolean" },
          severity: {
            type: "string",
            enum: ["blocking-correctness", "blocking-contract", "comment-only", "optional"]
          }
        },
        required: ["location", "finding", "fix"]
      }
    },
    nonBlocking: {
      type: "array",
      items: {
        type: "object",
        properties: {
          location: { type: "string" },
          finding: { type: "string" }
        },
        required: ["location", "finding"]
      }
    },
    gate: { type: "string", enum: ["pass", "fail", "not run"] },
    unspecified: { type: "array", items: { type: "string" } }
  },
  required: ["verdict", "summary", "blocking", "nonBlocking", "gate", "unspecified"]
};

const DEFAULT_REVIEWER_MODEL = "claude-opus-5-5";

// The class table. `mandate` goes to the implementer, `bar` to the reviewer; `coverageBlocks`
// false demotes coverageOnly findings; `testOnlyReduces` lets a test-only fix round take the
// reduced gate. Keep in step with pass-execute-chains.js.
const PASS_CLASSES = {
  "auth-data": {
    mandate: "Test-first: write or confirm the failing test before the change. For each auth, signing, session, D1, or commit-path branch you add, apply a mutation, confirm a test fails, revert it, and record it in mutationLedger. The pass end adds a web-auth-security-reviewer read and a live admin smoke.",
    bar: "Block on any behavior defect, unmet outcome, or coverage gap: an untested branch in auth, signing, sessions, D1, or the commit path is itself a defect.",
    coverageBlocks: true,
    testOnlyReduces: false,
    reviewerModel: DEFAULT_REVIEWER_MODEL
  },
  "engine-logic": {
    mandate: "Test-first: write or confirm the failing test before the change.",
    bar: "Block on behavior defects and unmet outcomes. A coverage gap blocks only where the untested path is reachable behavior; a gap on an unreachable or purely defensive path is not blocking (list it in nonBlocking, or mark it coverageOnly: true and the runner moves it there).",
    coverageBlocks: false,
    testOnlyReduces: true,
    reviewerModel: DEFAULT_REVIEWER_MODEL
  },
  paint: {
    mandate: "One cascade test per rule: the rule renders, and a utility class beats it. Add a per-state table only where the framework restates values per state. Keep tests table-driven, and add no tests beyond these. Your gate is the targeted gate named above; the full suite runs at the segment boundary or on CI.",
    bar: "Block only on a behavior defect or an unmet outcome. Test coverage, granularity, and test shape never block: list them in nonBlocking (a blocking finding marked coverageOnly: true is moved there by the runner) and the conductor batches them to the segment boundary.",
    coverageBlocks: false,
    testOnlyReduces: true,
    reviewerModel: DEFAULT_REVIEWER_MODEL
  },
  sweep: {
    mandate: "Mechanical change only: existing tests stay green, and add no new test unless the plan names one.",
    bar: "Run each grep-based post-condition the criteria name and report its count. Block only on a failed post-condition, a behavior change, or an unmet outcome; coverage notes go to nonBlocking.",
    coverageBlocks: false,
    testOnlyReduces: true,
    reviewerModel: "sonnet"
  },
  docs: {
    mandate: "No test mandate: the docs gates are the proof.",
    bar: "Block on a factual error against the code, a failing docs gate, or an unmet outcome. Prose register belongs to the register chain, not this review.",
    coverageBlocks: false,
    testOnlyReduces: true,
    reviewerModel: DEFAULT_REVIEWER_MODEL
  },
  tool: {
    mandate: "Follow go-conventions: test-first for behavior, table-driven tests, wrapped errors, the Go comment standard. A TUI change owes a tui-visual-verify capture at the close.",
    bar: "Block on behavior defects, unmet outcomes, go-conventions violations, and coverage gaps on reachable behavior.",
    coverageBlocks: true,
    testOnlyReduces: true,
    reviewerModel: DEFAULT_REVIEWER_MODEL,
    gateLane: "light"
  }
};

const CLASS_DEFAULT_REDUCED_GATE = "the repo's type check plus only the test files this fix round touched";

function classOf(t, a) {
  const name = t.passClass || a.passClass;
  return name ? { name, ...PASS_CLASSES[name] } : null;
}

/**
 * Returns the reduced gate a fix round runs, or null for the full gate. Without a class this is
 * the pre-class rule: `args.reducedGate` set and every finding commentOnly.
 */
function reducedGateFor(t, a, cls, blocking) {
  if (!blocking || blocking.length === 0) {
    return null;
  }
  if (!cls) {
    return a.reducedGate && blocking.every((b) => b.commentOnly) ? a.reducedGate : null;
  }
  const reducible = (b) => b.commentOnly || (cls.testOnlyReduces && b.testOnly);
  if (!blocking.every(reducible)) {
    return null;
  }
  return t.reducedGate || a.reducedGate || CLASS_DEFAULT_REDUCED_GATE;
}

/**
 * Under a class whose coverage does not block, moves coverageOnly findings out of blocking and
 * turns a `fix` verdict left with nothing blocking into `accept`. Returns the demoted findings.
 */
function applyClassBar(review, cls) {
  if (!cls || cls.coverageBlocks || !review || !Array.isArray(review.blocking)) {
    return [];
  }
  const demoted = review.blocking.filter((b) => b.coverageOnly);
  if (demoted.length === 0) {
    return [];
  }
  review.blocking = review.blocking.filter((b) => !b.coverageOnly);
  review.nonBlocking = [...(review.nonBlocking || []), ...demoted.map((b) => ({ location: b.location, finding: b.finding }))];
  if (review.verdict === "fix" && review.blocking.length === 0) {
    review.verdict = "accept";
    review.demotedFrom = "fix";
  }
  return demoted;
}

function validateArgs(a) {
  if (!a || typeof a !== "object") {
    throw new Error("args must be an object");
  }
  const classes = [a.passClass, ...(Array.isArray(a.tasks) ? a.tasks.map((t) => t && t.passClass) : [])];
  for (const c of classes) {
    if (c && !PASS_CLASSES[c]) {
      throw new Error(`unknown passClass "${c}"; expected one of ${Object.keys(PASS_CLASSES).join(", ")}`);
    }
  }
  if (!a.repo) {
    throw new Error("args.repo is required");
  }
  if (!a.gate) {
    throw new Error("args.gate is required");
  }
  if (!a.implementer) {
    throw new Error("args.implementer is required");
  }
  if (!Array.isArray(a.tasks) || a.tasks.length === 0) {
    throw new Error("args.tasks must be a non-empty array");
  }
}

function implementPrompt(t, a, blocking, baseSha) {
  const cls = classOf(t, a);
  const paintFlag = t.paint != null ? ` --paint ${t.paint ? "yes" : "no"}` : "";
  const pinFlag = t.gateTier ? ` --pin ${t.gateTier}` : "";
  const light = (t.gateLane || a.gateLane || (cls && cls.gateLane)) === "light";
  const lanePrefix = light ? "CAIRN_GATE_LANE=light " : "";
  const laneNote = light ? " (keep the CAIRN_GATE_LANE=light prefix on the first call and on every re-issue: this gate launches no browser, so it takes the light lane)" : "";
  const classifierCmd = `node scripts/checks/gate-tier.mjs --range ${baseSha}..HEAD${paintFlag}${pinFlag}`;
  const lines = [
    `Repo: ${a.repo}`,
    `Work in that repo: cd to it first and use absolute paths under it. It governs over any working directory your environment block names, which follows the conductor session and can point at another worktree.`,
    `Never use git stash: the stash stack is shared by every worktree and concurrent session. To set work aside, copy files to your scratchpad or make a WIP commit. Keep scratch and debug files in your scratchpad, never in the repo.`,
    `Task ${t.id}: ${t.title}`,
    `Acceptance criteria: ${t.criteria}`,
    t.files ? `Files: ${[].concat(t.files).join(", ")}` : "Files: not specified",
    t.notes ? `Notes: ${t.notes}` : "",
    a.commonNotes ? `Notes: ${a.commonNotes}` : "",
    cls ? `Pass class: ${cls.name}. Test mandate: ${cls.mandate}` : "",
    `Gate command: ${t.gate || a.gate}`,
    `Before running the gate, check whether scripts/checks/gate-tier.mjs exists in this repo. If it does, run \`${classifierCmd}\` from the repo root, after your commits and before the gate, and run the gate string it prints on stdout instead of the Gate command above (report gateTier: "${t.gateTier ? "pin" : "computed"}" and gateCommand as that exact string). If the script is absent, exits non-zero, or prints nothing, run the Gate command above unchanged (report gateTier: "default" and gateCommand as that string).`,
    "Run the gate through `" + lanePrefix + "cairn-run-gate '<the gate string>'`" + laneNote + ": exit 75 means still running, so re-issue the exact same command until it prints \"gate exit:\" with the tail; a report that the gate process vanished without a status means the run was lost, so start a fresh run rather than report red; never run it in the background and never poll a log; report its exact result.",
    "Skip agent-memory maintenance for this dispatch."
  ];
  if (blocking && blocking.length > 0) {
    lines.push("The previous attempt failed review. Fix exactly these blocking findings:");
    for (const b of blocking) {
      lines.push(`- ${b.location}: ${b.finding}. Fix: ${b.fix}`);
    }
    const reduced = reducedGateFor(t, a, cls, blocking);
    if (reduced && !cls) {
      lines.push(`Every finding above is COMMENT-ONLY (the fix changes comment or doc text, never code behavior). For this fix round the gate is reduced: run \`${reduced}\` through cairn-run-gate and report that reduced gate as the gate result; do not run the full gate string. If your fix diff touches any non-comment line, run the full gate string instead.`);
    } else if (reduced) {
      const gateText = reduced === CLASS_DEFAULT_REDUCED_GATE ? reduced : `\`${reduced}\``;
      lines.push(`Every finding above is COMMENT-ONLY or TEST-ONLY (the fix changes comment or doc text, or test files alone, never source behavior). For this fix round the gate is reduced: run ${gateText}, through cairn-run-gate, and report that exact string as gateCommand and its result as the gate result; do not run the full gate string. If your fix diff touches any source line outside tests and comments, run the full gate string instead.`);
    }
  }
  return lines.filter(Boolean).join("\n");
}

function reviewClassLines(cls, reduced) {
  const lines = [
    `Pass class: ${cls.name}. Blocking bar: ${cls.bar}`,
    `For each blocking finding set commentOnly: true when its fix changes only comment or doc text; set testOnly: true when its fix changes only test files; set coverageOnly: true when the finding concerns test coverage or granularity with no behavior defect. A fix round whose findings are all comment-only${cls.testOnlyReduces ? " or test-only" : ""} runs a reduced gate, so mark them honestly.`
  ];
  if (reduced) {
    lines.push(`This is such a fix round: the expected gate is the reduced gate (${reduced}), so a gate string that differs from the full gate is not a mismatch. If the fix diff touches any source line outside tests and comments, the full gate was owed: treat that as blocking.`);
  }
  return lines;
}

function reviewPrompt(t, a, implReport, resolvedGate, reduced) {
  const cls = classOf(t, a);
  const ranCommand = implReport.gateCommand || t.gate || a.gate;
  // The probe can return the classifier's whole stdout (preamble, file list, then the command),
  // and an implementer may report the cairn-run-gate wrapper, so compare on the command alone.
  const gateCore = (s) => {
    const last = String(s).trim().split("\n").pop().trim();
    const wrapped = last.match(/cairn-run-gate\s+'([^']+)'/);
    const cmd = wrapped ? wrapped[1] : last;
    // An absolute repo path and a repo-relative one name the same target; so does extra spacing.
    return cmd.split(`${a.repo}/`).join("").replace(/\s+/g, " ").trim();
  };
  // A task gate may carry a `<placeholder>` the implementer fills in (for example
  // `<the touched unit test files>`); the placeholder matches any non-empty text.
  const gateMatches = (ran, resolved) => {
    const pattern = gateCore(resolved)
      .split(/<[^<>]+>/)
      .map((part) => part.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
      .join(".+?");
    return new RegExp(`^${pattern}$`).test(gateCore(ran));
  };
  const classReduced = cls && reduced;
  // WATCH: a gate string that adds a test file the criteria permit (a new sibling test on the
  // unit leg) differs from the resolved string, so it reads as a MISMATCH the reviewer escalates
  // (theme identity pass A, segment B). If it recurs, let the resolved gate accept an added test
  // path under the task's Files.
  const mismatch =
    !classReduced && resolvedGate.gate && implReport.gateCommand && !gateMatches(implReport.gateCommand, resolvedGate.gate)
      ? `MISMATCH: the runner independently resolved a different gate string ("${resolvedGate.gate}") than the implementer reports running. Treat this mismatch itself as a blocking finding.`
      : "";
  return [
    `Repo: ${a.repo}`,
    `Work in that repo: cd to it first and use absolute paths under it. It governs over any working directory your environment block names, which follows the conductor session and can point at another worktree.`,
    `Task ${t.id}: ${t.title}`,
    `Acceptance criteria: ${t.criteria}`,
    `The gate string this task ran: ${ranCommand}`,
    classReduced ? `Reproduce the full gate, if owed, with: ${resolvedGate.gate}` : `Reproduce the gate with: ${resolvedGate.gate}`,
    mismatch,
    ...(cls
      ? reviewClassLines(cls, reduced)
      : [a.reducedGate
          ? `For each blocking finding set commentOnly: true when its fix changes only comment or doc text and no code behavior; a fix round whose findings are all comment-only runs the reduced gate \`${a.reducedGate}\`, so mark it honestly. If you are reviewing such a fix round, that reduced gate is the expected gate.`
          : ""]),
    "Implementer report (JSON):",
    JSON.stringify(implReport)
  ].filter(Boolean).join("\n");
}

function taskStatus(review, implReport) {
  if (!review || !implReport) {
    return "failed";
  }
  if (review.verdict === "escalate") {
    return "escalated";
  }
  if (review.verdict === "accept" && review.gate === "pass") {
    return "accepted";
  }
  if (review.verdict === "fix") {
    return "needs-decision";
  }
  return "needs-decision";
}

/**
 * Captures the task's starting commit before the implementer's first
 * dispatch. The gate-tier classifier diffs against this base, and it must be
 * captured before any commit lands, since HEAD moves as soon as the
 * implementer commits. The workflow runtime has no direct git access, so a
 * minimal probe agent runs the command instead.
 */
async function recordBaseSha(a, label) {
  const out = await agent(
    `Repo: ${a.repo}\nRun \`git rev-parse HEAD\` there and report exactly that commit SHA, nothing else.`,
    { label, phase: "Implement", schema: GATE_PROBE_SCHEMA, effort: "low" }
  );
  return out && out.sha ? out.sha.trim() : "";
}

/**
 * Resolves the gate string the runner hands the reviewer, independently of
 * whatever the implementer ran. A plan pin (`t.gateTier`) skips the
 * classifier entirely and keeps the task's declared gate string, matching
 * pre-classifier behavior; so does a repo with no classifier script. Any
 * other task asks a probe agent to run the classifier over the task's diff
 * so far (base..HEAD, which grows across fix rounds).
 */
async function resolveGate(t, a, baseSha, label) {
  if (t.gateTier) {
    return { gate: t.gate || a.gate, source: "pin", tier: t.gateTier };
  }
  const paintFlag = t.paint != null ? ` --paint ${t.paint ? "yes" : "no"}` : "";
  const cmd = `node scripts/checks/gate-tier.mjs --range ${baseSha}..HEAD${paintFlag}`;
  const probe = await agent(
    [
      `Repo: ${a.repo}`,
      `Work in that repo: cd to it first and use absolute paths under it. It governs over any working directory your environment block names, which follows the conductor session and can point at another worktree.`,
      `Check whether the file scripts/checks/gate-tier.mjs exists there.`,
      `If it does not, report exists: false and gate: "".`,
      `If it does, run exactly \`${cmd}\` from the repo root and report exists: true and gate: "<its exact stdout, trimmed>". On a non-zero exit or empty stdout, report exists: true and gate: "".`,
      `Do not run any other command and never modify a file.`
    ].join("\n"),
    { label, phase: "Implement", schema: GATE_TIER_SCHEMA, effort: "low" }
  );
  if (!probe || !probe.exists || !probe.gate) {
    return { gate: t.gate || a.gate, source: "fallback", tier: "default" };
  }
  return { gate: probe.gate, source: "classifier", tier: "computed" };
}

function logGateTier(t, resolved) {
  log(`task ${t.id}: gate tier ${resolved.tier} (${resolved.source})`);
}

async function runTask(t, a) {
  const implementer = a.implementer;
  const reviewer = a.reviewer || "diff-reviewer";
  const maxFix = a.maxFix == null ? 1 : a.maxFix;
  const cls = classOf(t, a);
  const reviewerModel = a.reviewerModel || (cls ? cls.reviewerModel : DEFAULT_REVIEWER_MODEL);
  const batchedNotes = [];

  // A task may name an implementer model override (t.model); agent()'s model
  // option takes precedence over the agent definition's pinned model.
  const implOpts = t.model ? { model: t.model } : {};

  const baseSha = await recordBaseSha(a, `base:${t.id}`);

  let implReport = await agent(implementPrompt(t, a, null, baseSha), {
    label: `impl:${t.id}`,
    phase: "Implement",
    agentType: implementer,
    schema: IMPL_SCHEMA,
    ...implOpts
  });

  if (!implReport) {
    log(`task ${t.id}: implementer failed to return a report`);
    return { id: t.id, title: t.title, status: "failed", fixRounds: 0, implementer: null, review: null };
  }

  let resolvedGate = await resolveGate(t, a, baseSha, `gatetier:${t.id}`);
  logGateTier(t, resolvedGate);

  let review = await agent(reviewPrompt(t, a, implReport, resolvedGate, null), {
    label: `review:${t.id}`,
    phase: "Review",
    model: reviewerModel,
    agentType: reviewer,
    schema: REVIEW_SCHEMA
  });

  if (!review) {
    log(`task ${t.id}: reviewer failed to return a verdict`);
    return { id: t.id, title: t.title, status: "failed", fixRounds: 0, implementer: implReport, review: null };
  }
  batchedNotes.push(...applyClassBar(review, cls));

  let fixRounds = 0;
  while (review.verdict === "fix" && fixRounds < maxFix) {
    fixRounds += 1;
    const reduced = reducedGateFor(t, a, cls, review.blocking);
    implReport = await agent(implementPrompt(t, a, review.blocking, baseSha), {
      label: `impl:${t.id}:fix${fixRounds}`,
      phase: "Implement",
      agentType: implementer,
      schema: IMPL_SCHEMA,
      ...implOpts
    });

    if (!implReport) {
      log(`task ${t.id}: implementer failed on fix round ${fixRounds}`);
      return { id: t.id, title: t.title, status: "failed", fixRounds, implementer: null, review };
    }

    resolvedGate = await resolveGate(t, a, baseSha, `gatetier:${t.id}:fix${fixRounds}`);
    logGateTier(t, resolvedGate);

    review = await agent(reviewPrompt(t, a, implReport, resolvedGate, reduced), {
      label: `review:${t.id}:fix${fixRounds}`,
      phase: "Review",
      model: reviewerModel,
      agentType: reviewer,
      schema: REVIEW_SCHEMA
    });

    if (!review) {
      log(`task ${t.id}: reviewer failed on fix round ${fixRounds}`);
      return { id: t.id, title: t.title, status: "failed", fixRounds, implementer: implReport, review: null };
    }
    batchedNotes.push(...applyClassBar(review, cls));
  }

  const status = taskStatus(review, implReport);
  log(`task ${t.id} (${t.title}): ${status}, verdict ${review.verdict}, fixRounds ${fixRounds}${cls ? `, class ${cls.name}, ${batchedNotes.length} coverage notes batched` : ""}`);

  const record = { id: t.id, title: t.title, status, fixRounds, implementer: implReport, review };
  return cls ? { ...record, passClass: cls.name, batchedNotes } : record;
}

function tally(results) {
  const t = { accepted: 0, needsDecision: 0, escalated: 0, failed: 0, deferred: 0, skipped: 0 };
  for (const r of results) {
    if (r.status === "accepted") t.accepted += 1;
    else if (r.status === "needs-decision") t.needsDecision += 1;
    else if (r.status === "escalated") t.escalated += 1;
    else if (r.status === "failed") t.failed += 1;
    else if (r.status === "deferred") t.deferred += 1;
    else if (r.status === "skipped") t.skipped += 1;
  }
  return t;
}

const BUDGET_FLOOR = 40000;

function isDeferred() {
  return budget.total != null && budget.remaining() < BUDGET_FLOOR;
}

// All async work lives inside main so the top level never uses the `await`
// keyword directly; the top level only calls and returns main().
async function main() {
  phase("Implement");

  validateArgs(args);

  let results;

  if (args.parallel === true) {
    results = await parallel(
      args.tasks.map((t) => async () => {
        if (isDeferred()) {
          log(`task ${t.id} (${t.title}): deferred for budget`);
          return { id: t.id, title: t.title, status: "deferred", fixRounds: 0, implementer: null, review: null };
        }
        return runTask(t, args);
      })
    );
    results = results.filter(Boolean);
  } else {
    const stopOnEscalate = args.stopOnEscalate !== false;
    results = [];
    for (const [i, t] of args.tasks.entries()) {
      if (isDeferred()) {
        log(`task ${t.id} (${t.title}): deferred for budget`);
        results.push({ id: t.id, title: t.title, status: "deferred", fixRounds: 0, implementer: null, review: null });
        continue;
      }
      const record = await runTask(t, args);
      results.push(record);
      if (stopOnEscalate && record.status !== "accepted") {
        log(`stopping after task ${t.id} (${record.status}); remaining tasks skipped`);
        for (const rest of args.tasks.slice(i + 1)) {
          results.push({ id: rest.id, title: rest.title, status: "skipped", fixRounds: 0, implementer: null, review: null });
        }
        break;
      }
    }
  }

  phase("Report");

  const finalTally = tally(results);
  log(`tally: accepted ${finalTally.accepted}, needs-decision ${finalTally.needsDecision}, escalated ${finalTally.escalated}, failed ${finalTally.failed}, deferred ${finalTally.deferred}, skipped ${finalTally.skipped}`);

  return { tasks: results, tally: finalTally, spent: budget.spent() };
}

return main();
