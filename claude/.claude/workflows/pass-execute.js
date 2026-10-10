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
//       classifier: true,                 // optional; an explicit boolean skips the gate-tier
//                                         // existence probe (see "Classifier caching" below).
//       reducedGate: "...",               // optional; the gate string a fix round runs
//                                         // when every blocking finding is commentOnly
//                                         // (or, under a passClass, commentOnly/testOnly).
//                                         // Absent, a no-class round whose findings are all
//                                         // commentOnly still reduces, to the class default
//                                         // (CLASS_DEFAULT_REDUCED_GATE: the repo's type
//                                         // check plus the test files the round touched),
//                                         // never the full gate (Geoff's 2026-09-09 ruling).
//       passClass: "paint",               // optional; see "Pass class" below. A task's own
//                                         // `passClass` overrides it for that task.
//       reviewerModel: "sonnet",          // optional; overrides the class's reviewer model.
//       stopOnEscalate: true,             // optional; sequential runs only, defaults to true.
//                                         // See "Stop on an unaccepted task" below.
//       ci: { pr: 110 },                  // optional; sequential runs only. Pipelines CI behind the
//                                         // chain; see "CI pipelining" below. Absent, or under
//                                         // `parallel: true`, the runner never pushes and never
//                                         // calls ci-green.
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
// mismatch as blocking. A pinned task skips the classifier on both sides: the runner keeps `t.gate`
// or `args.gate`, and the implementer prompt says to run that string unchanged (2026-10-08: the
// prompt still routed a pinned task through the classifier, which printed the narrower tier string,
// and the reviewer escalated the mismatch). The workflow runtime has no filesystem or exec access,
// so every git/node call here goes through a small probe agent rather than direct code.

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
// repo's type check plus the test files the fix touched, run as the implementer's validated
// concrete command; see "Reduced fix rounds" below), except under `auth-data`, where only a
// comment-only round reduces. The per-task gate is sized by the gate-tier classifier when the repo
// has scripts/checks/gate-tier.mjs, unless a task pins `gateTier` (which keeps `t.gate` or
// `args.gate`); without the classifier it is the plan's `t.gate` or `args.gate`. The `tool` class
// defaults to the light gate lane.
// Born of the theme identity pass A evaluation: a CSS retheme ran the full engine gate per task,
// at about 4.4 test lines per source line, and every test-only fix round reran the full gate.
// Without a passClass every prompt and verdict is exactly the pre-class behavior.
// Keep PASS_CLASSES in step with pass-execute-chains.js.

// Classifier caching (AW-13): `args.classifier`, when explicit, else one cached existence probe
// (`model: "haiku"`) for whether `args.repo` carries `scripts/checks/gate-tier.mjs`, run once
// for the whole run and reused for every task, rather than once per task. `classifier: false`
// skips the probe entirely: no per-task tier probe ever runs, and the implementer prompt
// renders no classifier paragraph.

// Cairn friction (Geoff, 2026-10-07): in a cairn-family repo, every dispatch also harvests
// friction with cairn itself: a docs gap, a suggested engine improvement, or a DX snag met while
// using a cairn surface. The implementer reports it in `cairnFriction`, the reviewer in
// `outOfScope` with `cairn: true`, and both land in the record's `outOfScope` tagged
// `cairn: true`, so the conductor verifies each and files it in cairn-cms's
// `docs/internal/docs-friction-log.md`. `args.cairnFriction` (boolean) overrides the repo-path
// test in CAIRN_FAMILY.

// Gate receipts (Geoff, 2026-10-08): the independent gate step no longer reruns a gate the
// implementer already passed on the same tree. Its Haiku agent first runs `cairn-run-gate --receipt
// '<gate>'` (with the task's lane prefix); a receipt matches only the exact gate string on a tree
// whose fingerprint (HEAD's tree, git status, the content of changed and untracked files, the
// lockfiles, and an env allowlist; cairn-run-gate's header is the full list) equals the recorded
// run's, and only a passing run's receipt counts. On a match the record carries `fromReceipt: true`
// and the receipt line, and the reviewer prompt says the record came from a receipt; otherwise the
// agent runs the gate as before. Since a receipt matches only the exact resolved string, a
// narrower tier never satisfies a wider requirement. `gateMatches` still governs the
// implementer-versus-resolved comparison.

// Reduced fix rounds (Geoff, 2026-10-08): a fix round that takes the reduced gate runs it on the
// independent gate agent too. An explicit `reducedGate` string runs as given. For the class
// default, which names no command, the implementer composes a concrete one (the type check plus
// `npx vitest run <the touched test files>`, or the repo's equivalent), reports it as gateCommand,
// and lists its test files in `reducedTestFiles`; the runner records the round's base commit
// before the fix dispatch, asks a probe for `git diff --name-only <base>`, and runs the command
// only when every test file it names is in that list and every test file in that list is named
// (validatedReducedCommand). A failed check
// falls back to the reviewer reproducing the gate itself, and the reviewer prompt says why. A
// no-class reduced round keeps running the resolved gate, as before.

// CI pipelining: with `ci: { pr: <n> }` a sequential run reads CI as the full gate and overlaps
// it with the next task's work. Every probe below is a Haiku agent; the runner itself has no exec.
//   - After every implementer commit, fix rounds included, a `push:<task>[:fix<n>]` probe pushes
//     (never forcing) and returns `{ pushed, sha, pushedAt }`. The push comes before the gate
//     probe and the review, so CI runs while the reviewer reads. A task's `ci` field on its
//     record is its last push plus `wait`, the accepted head.
//   - After task N is accepted, N+1 is dispatched at once. Before task N+2 is dispatched, a
//     `ci:<N>` probe runs `ci-green <sha> --pr <n> --wait --pushed-at <iso> --task <N>` on N's
//     accepted SHA, so N+1 has finished its chain by the time a red N is read.
//   - A task with `wait` set is read before N+1 is dispatched, and N+1 never starts on a red
//     one. `wait` holds when the class sets `ciWait` (`auth-data`), when the task carries
//     `ciWait: true`, or when the gate probe's `--protected` run says so. That probe runs on every
//     task of a CI run, a pinned task included (the pinned gate string stays as written): its
//     `protectedExit` and `protectedOut` make `ciWait` true when the exit is non-zero or missing
//     or the output names `ciWait`, and false when the classifier is absent. The probe runs at
//     the head being accepted, so a fix round's range is covered.
//   - A `ci:` probe runs `ci-green --wait` (each call blocks up to 540 seconds) and itself
//     re-issues the call on exit 75. If it still reports 75, the runner re-dispatches the probe,
//     and caps those re-dispatches at CI_MAX_WAITS, after which the check is unavailable.
//     Exit 0 is green. Exit 1 is red and exit 2 is missing: the run halts, the tasks not yet
//     dispatched are marked "skipped", and the result carries `ciRed`: `{ sha, task, verdict:
//     "red" | "missing", exitCode, detail }`, where `detail` is ci-green's own output (the failing
//     workflows, jobs, steps, and tests, and `main`'s latest conclusion per workflow). Exit 3, any
//     other exit, a failed push, or a probe that returns nothing halts the same way with
//     `ciUnavailable`: `{ sha, task, exitCode, reason }`, and the conductor then runs the local
//     full gate on that SHA.
//   - The result's `ci.unchecked` lists `{ task, sha, pushedAt }` for every accepted task whose
//     read never ran: the segment's last heads, which have no later dispatch to trigger a read,
//     and a halted task whose read did not come back green. The run also logs them.
// An unaccepted task ends the run as before, with no further CI reads.

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
    // Optional: on a class-default reduced fix round, the test files the concrete reduced
    // command names, repo-relative, for the runner to check against the round's diff.
    reducedTestFiles: { type: "array", items: { type: "string" } },
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
    cairnFriction: {
      type: "array",
      items: {
        type: "object",
        properties: {
          location: { type: "string" },
          finding: { type: "string" },
          kind: { type: "string", enum: ["docs", "engine", "dx"] }
        },
        required: ["location", "finding"]
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
    gate: { type: "string" },
    // Only on a CI run: the exit code and stdout of the classifier's --protected mode. The runner
    // derives ciWait from them, so a non-zero or missing exit fails closed.
    protectedExit: { type: ["integer", "null"] },
    protectedOut: { type: "string" }
  },
  required: ["exists", "gate"]
};

const PUSH_SCHEMA = {
  type: "object",
  properties: {
    pushed: { type: "boolean" },
    sha: { type: "string" },
    pushedAt: { type: "string" }
  },
  required: ["pushed", "sha", "pushedAt"]
};

const CI_SCHEMA = {
  type: "object",
  properties: {
    exitCode: { type: ["integer", "null"] },
    output: { type: "string" }
  },
  required: ["exitCode", "output"]
};

const GATE_RUN_SCHEMA = {
  type: "object",
  properties: {
    command: { type: "string" },
    exitCode: { type: ["integer", "null"] },
    result: { type: "string", enum: ["pass", "fail", "not run"] },
    excerpt: { type: "string" },
    // Both optional: set when a cairn-run-gate receipt stood in for a rerun.
    fromReceipt: { type: "boolean" },
    receipt: { type: "string" }
  },
  required: ["command", "exitCode", "result", "excerpt"]
};

const TOUCHED_SCHEMA = {
  type: "object",
  properties: {
    files: { type: "array", items: { type: "string" } }
  },
  required: ["files"]
};

const CLASSIFIER_PROBE_SCHEMA = {
  type: "object",
  properties: {
    exists: { type: "boolean" }
  },
  required: ["exists"]
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
          coverageOnly: { type: "boolean" }
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
    unspecified: { type: "array", items: { type: "string" } },
    // Defects noticed outside the task's criteria. Never blocking; the runner collects them
    // across fix rounds and returns them so the conductor files each in the repo's friction log.
    outOfScope: {
      type: "array",
      items: {
        type: "object",
        properties: { location: { type: "string" }, finding: { type: "string" }, cairn: { type: "boolean" } },
        required: ["location", "finding"]
      }
    }
  },
  required: ["verdict", "summary", "blocking", "nonBlocking", "gate", "unspecified"]
};

const DEFAULT_REVIEWER_MODEL = "claude-opus-5-5";

// The class table. `mandate` goes to the implementer, `bar` to the reviewer; `coverageBlocks`
// false demotes coverageOnly findings; `testOnlyReduces` lets a test-only fix round take the
// reduced gate; `ciWait` makes a CI run read CI green before the next task. Keep in step with
// pass-execute-chains.js.
const PASS_CLASSES = {
  "auth-data": {
    mandate: "Test-first: write or confirm the failing test before the change. For each auth, signing, session, D1, or commit-path branch you add, apply a mutation, confirm a test fails, revert it, and record it in mutationLedger. The pass end adds a web-auth-security-reviewer read and a live admin smoke.",
    bar: "Block on any behavior defect, unmet outcome, or coverage gap: an untested branch in auth, signing, sessions, D1, or the commit path is itself a defect.",
    coverageBlocks: true,
    testOnlyReduces: false,
    reviewerModel: DEFAULT_REVIEWER_MODEL,
    ciWait: true
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
 * The reduced gate a task names, most specific first: `t.reducedGate`, then `a.reducedGate`,
 * then the class default.
 */
function configuredReducedGate(t, a) {
  return t.reducedGate || a.reducedGate || CLASS_DEFAULT_REDUCED_GATE;
}

/**
 * Returns the reduced gate a fix round runs, or null for the full gate. A round reduces when
 * every blocking finding is commentOnly, or, under a class whose `testOnlyReduces` is set,
 * commentOnly or testOnly. Without a class an all-commentOnly round still reduces (Geoff's
 * 2026-09-09 ruling: a fix round never falls through to the full gate for want of an explicit
 * `a.reducedGate`).
 */
function reducedGateFor(t, a, cls, blocking) {
  if (!blocking || blocking.length === 0) {
    return null;
  }
  const testOnlyReduces = Boolean(cls && cls.testOnlyReduces);
  const reducible = (b) => b.commentOnly || (testOnlyReduces && b.testOnly);
  return blocking.every(reducible) ? configuredReducedGate(t, a) : null;
}

/**
 * Renders a resolved reduced-gate value for prose: the class default reads as its own sentence,
 * an explicit gate string is backtick-quoted as a command.
 */
function renderGateText(g) {
  return g === CLASS_DEFAULT_REDUCED_GATE ? g : `\`${g}\``;
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
  if (a.ci != null && !(a.ci && Number.isInteger(Number(a.ci.pr)) && Number(a.ci.pr) > 0 && a.ci.pr !== true)) {
    throw new Error("args.ci.pr must be a pull request number");
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

const CAIRN_FAMILY = /cairn|907-life|ecxc-ski|aksailingclub|xcathletes/;

function harvestsCairnFriction(a, repo) {
  return a.cairnFriction != null ? a.cairnFriction : CAIRN_FAMILY.test(repo || a.repo || "");
}

const CAIRN_FRICTION_ASK = "Cairn friction: this repo builds on cairn (@glw907/cairn-cms, its tools, docs, and theme contract). List in cairnFriction any friction with cairn you met during this task: a docs gap or error, a suggested engine improvement, or a DX snag. Give each a location (a cairn doc path, export, tool, or the file:line where it bit), the finding, and a kind of docs, engine, or dx. Report only what you met, never a hunch; an empty list is fine. It never affects the verdict.";

const CAIRN_REVIEW_ASK = "Cairn friction: this repo builds on cairn. Also list in outOfScope, with cairn: true, any friction with cairn the diff shows (a docs gap, an engine improvement, a DX snag the implementer worked around). The conductor files those in cairn-cms's friction log.";

function implFriction(implReport) {
  return ((implReport && implReport.cairnFriction) || []).map((f) => ({ ...f, cairn: true }));
}

function implementPrompt(t, a, blocking, baseSha, classifierExists) {
  const cls = classOf(t, a);
  const paintFlag = t.paint != null ? ` --paint ${t.paint ? "yes" : "no"}` : "";
  const pinFlag = t.gateTier ? ` --pin ${t.gateTier}` : "";
  const light = (t.gateLane || a.gateLane || (cls && cls.gateLane)) === "light";
  const lanePrefix = light ? "CAIRN_GATE_LANE=light " : "";
  const laneNote = light ? " (keep the CAIRN_GATE_LANE=light prefix on the first call and on every re-issue: this gate launches no browser, so it takes the light lane)" : "";
  const classFlag = cls ? ` --class ${cls.name}` : "";
  const classifierCmd = `node scripts/checks/gate-tier.mjs --range ${baseSha}..HEAD${paintFlag}${classFlag}${pinFlag}`;
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
    // A pinned tier keeps the plan's gate string (resolveGate), so the implementer must run that
    // same string; sending it through the classifier would report a narrower one and trip the
    // reviewer's mismatch check.
    t.gateTier
      ? `This task pins its gate tier, so run the Gate command above exactly as written, as one cairn-run-gate call with no classifier step and no split into separate runs (report gateTier: "pin" and gateCommand as that exact string). The runner's independent gate run uses the same string.`
      : classifierExists
      ? `Before running the gate, check whether scripts/checks/gate-tier.mjs exists in this repo. If it does, run \`${classifierCmd}\` from the repo root, after your commits and before the gate, and run the gate string it prints on stdout instead of the Gate command above (report gateTier: "${t.gateTier ? "pin" : "computed"}" and gateCommand as that exact string). If the script is absent, exits non-zero, or prints nothing, run the Gate command above unchanged (report gateTier: "default" and gateCommand as that string).`
      : "",
    "Run the gate through `" + lanePrefix + "cairn-run-gate '<the gate string>'`" + laneNote + " and follow its own output for whether to re-issue and for the result; never run it in the background and never poll a log; report its exact result.",
    "Skip agent-memory maintenance for this dispatch.",
    harvestsCairnFriction(a, a.repo) ? CAIRN_FRICTION_ASK : ""
  ];
  if (blocking && blocking.length > 0) {
    lines.push("The previous attempt failed review. Fix exactly these blocking findings:");
    for (const b of blocking) {
      lines.push(`- ${b.location}: ${b.finding}. Fix: ${b.fix}`);
    }
    const reduced = reducedGateFor(t, a, cls, blocking);
    if (reduced && !cls) {
      lines.push(`Every finding above is COMMENT-ONLY (the fix changes comment or doc text, never code behavior). For this fix round the gate is reduced: run ${renderGateText(reduced)} through cairn-run-gate and report that reduced gate as the gate result; do not run the full gate string. If your fix diff touches any non-comment line, run the full gate string instead.`);
    } else if (reduced) {
      lines.push(`Every finding above is COMMENT-ONLY or TEST-ONLY (the fix changes comment or doc text, or test files alone, never source behavior). For this fix round the gate is reduced: run ${renderGateText(reduced)}, through cairn-run-gate, and report that exact string as gateCommand and its result as the gate result; do not run the full gate string. If your fix diff touches any source line outside tests and comments, run the full gate string instead.`);
      if (reduced === CLASS_DEFAULT_REDUCED_GATE) {
        lines.push(CONCRETE_REDUCED_ASK);
      }
    }
  }
  return lines.filter(Boolean).join("\n");
}

const CONCRETE_REDUCED_ASK = "That reduced gate names no fixed command, so compose a concrete one: the repo's type check plus a run of only the test files this fix round changed (for example `<the type check> && npx vitest run <the touched test files>`, or the repo's equivalent). Run it as one string through cairn-run-gate, report that exact string as gateCommand, and list in reducedTestFiles every test file it names, repo-relative (an empty list when it names none). The runner checks each against this round's diff and reruns the command independently; a file outside the diff sends the reviewer back to reproducing the gate by hand.";

/** Paths a reduced command may name only when the fix round touched them. */
const TEST_FILE_TOKEN = /(?:\.(?:test|spec)\.[cm]?[jt]sx?|_test\.go)$/;

/**
 * The implementer's concrete reduced command for a class-default reduced round, validated against
 * the fix round's diff, or "" when it cannot stand. `touched` is the `git diff --name-only <round
 * base>` list. Every file in reducedTestFiles must be in `touched` and appear in the command, every
 * test file in `touched` must be in reducedTestFiles, and every test-file token in the command
 * must be in reducedTestFiles. A `<placeholder>` left in the
 * command, or a report with no gateCommand or reducedTestFiles, also fails.
 */
function validatedReducedCommand(implReport, touched, repo) {
  if (!implReport || !implReport.gateCommand || !Array.isArray(implReport.reducedTestFiles) || !Array.isArray(touched)) {
    return "";
  }
  const last = String(implReport.gateCommand).trim().split("\n").pop().trim();
  const wrapped = last.match(/cairn-run-gate\s+'([^']+)'/);
  const cmd = (wrapped ? wrapped[1] : last).trim();
  if (!cmd || /<[^<>]+>/.test(cmd)) {
    return "";
  }
  const norm = (p) => String(p).trim().split(`${repo}/`).join("").replace(/^\.\//, "");
  const touchedSet = new Set(touched.map(norm));
  const listed = implReport.reducedTestFiles.map(norm);
  if (!listed.every((f) => f && touchedSet.has(f) && cmd.includes(f))) {
    return "";
  }
  // A test file the round edited must run, or the reduced gate never exercises the fix.
  if (![...touchedSet].filter((f) => TEST_FILE_TOKEN.test(f)).every((f) => listed.includes(f))) {
    return "";
  }
  const named = cmd
    .split(/\s+/)
    .map((tok) => norm(tok.replace(/^['"]|['"]$/g, "")))
    .filter((tok) => TEST_FILE_TOKEN.test(tok));
  return named.every((tok) => listed.includes(tok)) ? cmd : "";
}

// === GATE MATCHER (tests extract this block; kept identical in pass-execute-chains.js) ===
/** Variables an implementer may set ahead of a gate command without changing what the gate proves. */
const GATE_ENV_ALLOWLIST = ["CAIRN_GATE_LANE", "CI", "E2E_PORT"];

/**
 * Drops leading allowlisted assignments from a gate's steps: a whole step of `VAR=value` or
 * `export VAR=value`, or a `VAR=value ` prefix on the first real command. Stripping stops at the
 * first step that is not an allowlisted assignment, so a `cd`, any other command, or an
 * unlisted variable stays in place and fails the comparison.
 */
function stripGateAssignments(steps) {
  const out = [...steps];
  const lead = /^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=("[^"]*"|\S*)(?:\s+|$)/;
  while (out.length > 0) {
    const m = out[0].match(lead);
    if (!m || !GATE_ENV_ALLOWLIST.includes(m[1])) break;
    const rest = out[0].slice(m[0].length).trim();
    if (rest) out[0] = rest;
    else out.shift();
  }
  return out;
}

/**
 * Normalizes a gate string for comparison: keeps only its last non-empty line (a probe can
 * return the classifier's whole stdout, preamble and all), unwraps a `cairn-run-gate '<cmd>'`
 * call (discarding anything before it, such as the `cd <repo> &&` the runner tells implementers
 * to run), treats an absolute repo path and its repo-relative form, or extra spacing, as the
 * same target, and drops leading allowlisted assignments. Returns the `&&` steps joined by " && ".
 */
function gateCore(s, repo) {
  const last = String(s).trim().split("\n").pop().trim();
  const wrapped = last.match(/cairn-run-gate\s+'([^']+)'/);
  const cmd = wrapped ? wrapped[1] : last;
  const flat = cmd.split(`${repo}/`).join("").replace(/\s+/g, " ").trim();
  return stripGateAssignments(flat.split(/\s*&&\s*/)).join(" && ");
}

/**
 * True when the gate string the implementer ran matches the gate string the runner
 * independently resolved: equal after normalization, or the same gate steps followed by extra
 * `&&` steps. A task gate may carry a `<placeholder>` the implementer fills in (for example
 * `<the touched unit test files>`); the placeholder matches one or more characters other than `|`, `;`, `#`, quotes, backticks, and `&`.
 */
function gateMatches(ran, resolved, repo) {
  const pattern = gateCore(resolved, repo)
    .split(/<[^<>]+>/)
    .map((part) => part.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join("[^|;#'\"`&]+?");
  return new RegExp(`^${pattern}(?: && [^|;#'"\`&]+)*$`).test(gateCore(ran, repo));
}
// === END GATE MATCHER ===

/**
 * The no-class reviewer instruction: always names the reduced gate a comment-only round would
 * take (`t.reducedGate`, `a.reducedGate`, or the class default), never conditioned on whether
 * this particular round is one.
 */
function noClassReviewLine(t, a) {
  return `For each blocking finding set commentOnly: true when its fix changes only comment or doc text and no code behavior; a fix round whose findings are all comment-only runs the reduced gate ${renderGateText(configuredReducedGate(t, a))}, so mark it honestly. If you are reviewing such a fix round, that reduced gate is the expected gate.`;
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

// Longest failing-output excerpt the gate runner's record may carry into the reviewer's prompt.
const GATE_EXCERPT_LINES = 150;
const GATE_EXCERPT_CHARS = 12000;

/**
 * The gate string the independent gate runner executes, or "" when it cannot run one without a
 * judgment call. A class-reduced round runs its reduced gate: an explicit string as given, the
 * class default only as the implementer's validated concrete command (`concreteReduced`, "" when
 * validation failed). A pinned or fallback gate may still carry a `<placeholder>` the implementer
 * fills in. Every "" falls back to the reviewer reproducing the gate itself.
 */
function gateToRun(resolvedGate, reduced, cls, concreteReduced) {
  // A no-class reduced round (comment-only, or the pre-class a.reducedGate fallback) keeps the
  // resolved gate the reviewer always reproduced.
  let g = resolvedGate.gate;
  if (cls && reduced) {
    g = reduced === CLASS_DEFAULT_REDUCED_GATE ? concreteReduced || "" : reduced;
  }
  return g && !/<[^<>]+>/.test(g) ? g : "";
}

/**
 * Runs the gate the reviewer would otherwise reproduce, on a Haiku agent, so the gate transcript
 * never lands in Opus context. The agent copies; it never summarizes or decides. Returns a record
 * of the command, exit code, result, and a capped verbatim excerpt of failing output, or null when
 * there is nothing to run or the runner fails (the reviewer then reproduces the gate itself).
 */
async function runGateIndependently(t, a, cls, gate, label) {
  if (!gate) {
    return null;
  }
  const light = (t.gateLane || a.gateLane || (cls && cls.gateLane)) === "light";
  const lanePrefix = light ? "CAIRN_GATE_LANE=light " : "";
  const out = await agent(
    [
      `Repo: ${a.repo}`,
      `Work in that repo: cd to it first and use absolute paths under it. It governs over any working directory your environment block names, which follows the conductor session and can point at another worktree.`,
      `The gate string: ${gate}`,
      "First look for a receipt: run `" + lanePrefix + "cairn-run-gate --receipt '<the gate string>'` (if the gate string already begins with cairn-run-gate, insert --receipt right after it) as a plain foreground Bash call. If it exits 0 and prints a line starting `receipt: exit 0`, do not run the gate: report command as the gate string, exitCode 0, result pass, excerpt the empty string, fromReceipt true, and receipt as that line verbatim. Otherwise it prints `receipt: none`; go on and run the gate, and report fromReceipt false.",
      "Without a receipt, run exactly that gate and nothing else, through `" + lanePrefix + "cairn-run-gate '<the gate string>'` (if the string above already begins with cairn-run-gate, run it as given) as a plain foreground Bash call with `timeout: 600000`. On exit 75, re-issue the same call until it prints `gate exit:`. Never run it in the background, never poll a log, and never edit a file.",
      "Report command as the exact string you ran and exitCode as the number after `gate exit:`, exactly as printed (null when it never printed). Set result to pass when the exit code is 0, fail when it is not, and not run when the runner never printed `gate exit:`.",
      `On a fail, copy into excerpt the last ${GATE_EXCERPT_LINES} lines of the failing output verbatim. Do not summarize, interpret, reorder, or trim a line. On a pass, excerpt is the empty string.`,
      "Skip agent-memory maintenance for this dispatch."
    ].join("\n"),
    { label, phase: "Review", schema: GATE_RUN_SCHEMA, model: "haiku", effort: "low" }
  );
  // A "not run" record, or one whose result contradicts its exit code (null counts as nonzero),
  // cannot stand in for the gate, so the reviewer reproduces the gate itself.
  if (!out || out.result === "not run" || (out.exitCode === 0) !== (out.result === "pass")) {
    return null;
  }
  // A receipt stands in only for a pass, and only with the lookup's own line to show for it.
  if (out.fromReceipt && (out.exitCode !== 0 || !/^receipt: exit 0 /.test(String(out.receipt || "").trim()))) {
    return null;
  }
  const tail = String(out.excerpt || "").split("\n").slice(-GATE_EXCERPT_LINES).join("\n");
  return { ...out, excerpt: tail.slice(-GATE_EXCERPT_CHARS) };
}

/**
 * The reviewer lines that carry the gate: the runner's independent record when there is one,
 * else today's "Reproduce the gate" instruction. `fallbackLine` is that instruction.
 */
function gateRecordLines(gateRun, fallbackLine, fullGateLine) {
  if (!gateRun) {
    return [fallbackLine];
  }
  const source = gateRun.fromReceipt
    ? `Independent gate record from a cairn-run-gate receipt, not a rerun (${gateRun.command} already passed on this exact tree, matched by fingerprint; ${String(gateRun.receipt).trim()})`
    : `Independent gate run (a separate runner executed ${gateRun.command})`;
  const lines = [
    `${source}: exit code ${gateRun.exitCode}, result ${gateRun.result}. Treat this as the gate result and rerun the gate only if the diff gives you a specific reason to doubt it.`
  ];
  if (gateRun.excerpt) {
    lines.push("Failing output, verbatim from the runner:", gateRun.excerpt);
  }
  if (fullGateLine) {
    lines.push(fullGateLine);
  }
  return lines;
}

// A weakened check is a blocking finding on any class: CI's full run is the holdout only while the
// checks that select and run it stay intact (an observed instance of an agent editing tests to
// pass: arXiv 2511.21654).
const TEST_WEAKENING_LINE = "Blocking finding, any class: an existing test deleted, skipped, `.only`'d, or loosened; or a bucket, no-check entry, e2e map entry, trigger, protected path, `check:close` component, `ci-green.json` entry, or workflow test step narrowed or weakened, that the task's criteria do not name.";

function reviewPrompt(t, a, implReport, resolvedGate, reduced, gateRun, reducedCheck) {
  const cls = classOf(t, a);
  const ranCommand = implReport.gateCommand || t.gate || a.gate;
  const classReduced = cls && reduced;
  // WATCH: a gate string that adds a test file the criteria permit (a new sibling test on the
  // unit leg) differs from the resolved string, so it reads as a MISMATCH the reviewer escalates
  // (theme identity pass A, segment B). If it recurs, let the resolved gate accept an added test
  // path under the task's Files.
  // Any reduced round, class-based or the pre-class a.reducedGate fallback, is exempt from the
  // mismatch check: its expected gate is the reduced one, not resolvedGate.
  const mismatch =
    !reduced && resolvedGate.gate && implReport.gateCommand && !gateMatches(implReport.gateCommand, resolvedGate.gate, a.repo)
      ? `MISMATCH: the runner independently resolved a different gate string ("${resolvedGate.gate}") than the implementer reports running. Treat this mismatch itself as a blocking finding.`
      : "";
  return [
    `Repo: ${a.repo}`,
    `Work in that repo: cd to it first and use absolute paths under it. It governs over any working directory your environment block names, which follows the conductor session and can point at another worktree.`,
    `Task ${t.id}: ${t.title}`,
    `Acceptance criteria: ${t.criteria}`,
    `The gate string this task ran: ${ranCommand}`,
    reducedCheckLine(reducedCheck),
    ...gateRecordLines(
      gateRun,
      classReduced ? `Reproduce the full gate, if owed, with: ${resolvedGate.gate}` : `Reproduce the gate with: ${resolvedGate.gate}`,
      classReduced ? `The runner executed the reduced gate. If the full gate was owed, reproduce it with: ${resolvedGate.gate}` : ""
    ),
    mismatch,
    ...(cls
      ? reviewClassLines(cls, reduced)
      : [noClassReviewLine(t, a)]),
    TEST_WEAKENING_LINE,
    "Out of scope: list in outOfScope any real defect you notice outside this task's criteria (a bug, a stale doc or comment, a false claim, a gate gap), one {location, finding} each. It never affects the verdict; the conductor files each one in the repo's friction log.",
    harvestsCairnFriction(a, a.repo) ? CAIRN_REVIEW_ASK : "",
    "Implementer report (JSON):",
    JSON.stringify(implReport)
  ].filter(Boolean).join("\n");
}

/**
 * The files `git diff --name-only <base>` lists in the repo (committed and uncommitted changes
 * since the fix round's base), or null when there is no base or the probe fails.
 */
async function touchedFiles(repo, base, phaseName, label) {
  if (!base) {
    return null;
  }
  const out = await agent(
    [
      `Repo: ${repo}`,
      `Run \`git -C ${repo} diff --name-only ${base}\` and report every path it prints in files, verbatim, one entry per line of output.`,
      `Do not run any other command and never modify a file.`
    ].join("\n"),
    { label, phase: phaseName, schema: TOUCHED_SCHEMA, model: "haiku", effort: "low" }
  );
  return out && Array.isArray(out.files) ? out.files : null;
}

/**
 * The reviewer line for a class-default reduced round whose concrete command was checked: what
 * the runner did with it. Empty when no check ran.
 */
function reducedCheckLine(check) {
  if (!check || !check.attempted) {
    return "";
  }
  return check.concrete
    ? `The reduced gate the runner ran is the implementer's concrete command (\`${check.concrete}\`), after checking that every test file it names is in this fix round's diff.`
    : "The implementer's concrete reduced command failed the runner's check (a test file it names is not in this fix round's diff, or the report did not list them), so the runner did not run it: reproduce the reduced gate yourself.";
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
    { label, phase: "Implement", schema: GATE_PROBE_SCHEMA, model: "haiku", effort: "low" }
  );
  return out && out.sha ? out.sha.trim() : "";
}

/**
 * Resolves, once per run, whether args.repo carries the gate-tier classifier script
 * (scripts/checks/gate-tier.mjs). An explicit `a.classifier` boolean skips the probe entirely;
 * `classifier: false` means no per-task tier probe ever runs and the implementer prompt renders
 * no classifier paragraph (AW-13, mirrored from pass-execute-chains.js).
 */
async function resolveClassifier(a) {
  if (typeof a.classifier === "boolean") {
    return a.classifier;
  }
  const probe = await agent(
    [
      `Repo: ${a.repo}`,
      `Check whether the file scripts/checks/gate-tier.mjs exists there. Report exists: true or exists: false.`,
      `Do not run any other command and never modify a file.`
    ].join("\n"),
    { label: "classifier", phase: "Implement", schema: CLASSIFIER_PROBE_SCHEMA, model: "haiku", effort: "low" }
  );
  return !!(probe && probe.exists);
}

/**
 * Resolves the gate string the runner hands the reviewer, independently of
 * whatever the implementer ran. A plan pin (`t.gateTier`) skips the
 * classifier entirely and keeps the task's declared gate string, matching
 * pre-classifier behavior; so does a run whose cached `classifierExists` is
 * false. Any other task asks a probe agent to run the classifier over the
 * task's diff so far (base..HEAD, which grows across fix rounds).
 */
async function resolveGate(t, a, baseSha, classifierExists, label) {
  const watch = ciActive(a);
  const protectedCmd = `node scripts/checks/gate-tier.mjs --range ${baseSha}..HEAD --protected`;
  const protectedLines = watch
    ? [
        `Then run exactly \`${protectedCmd}\` from the repo root and report protectedExit as its exit code (null when it never ran) and protectedOut as its exact stdout, trimmed. Report a non-zero exit as it is; never retry it or read meaning into it.`
      ]
    : [];
  const home = [
    `Repo: ${a.repo}`,
    `Work in that repo: cd to it first and use absolute paths under it. It governs over any working directory your environment block names, which follows the conductor session and can point at another worktree.`,
    `Check whether the file scripts/checks/gate-tier.mjs exists there.`,
    `If it does not, report exists: false and gate: "".`
  ];
  const last = [`Do not run any other command and never modify a file.`];
  if (t.gateTier) {
    const pinned = { gate: t.gate || a.gate, source: "pin", tier: t.gateTier };
    if (!watch || !classifierExists) {
      return pinned;
    }
    const probe = await agent(
      [
        ...home,
        `If it does, report exists: true and gate: "" (this task pins its gate; do not compute one).`,
        ...protectedLines,
        ...last
      ].join("\n"),
      { label, phase: "Implement", schema: GATE_TIER_SCHEMA, model: "haiku", effort: "low" }
    );
    return { ...pinned, ciWait: protectedWait(probe) };
  }
  if (!classifierExists) {
    return { gate: t.gate || a.gate, source: "fallback", tier: "default" };
  }
  const paintFlag = t.paint != null ? ` --paint ${t.paint ? "yes" : "no"}` : "";
  const cls = classOf(t, a);
  const classFlag = cls ? ` --class ${cls.name}` : "";
  const cmd = `node scripts/checks/gate-tier.mjs --range ${baseSha}..HEAD${paintFlag}${classFlag}`;
  const probe = await agent(
    [
      ...home,
      `If it does, run exactly \`${cmd}\` from the repo root and report exists: true and gate: "<its exact stdout, trimmed>". On a non-zero exit or empty stdout, report exists: true and gate: "".`,
      ...protectedLines,
      ...last
    ].join("\n"),
    { label, phase: "Implement", schema: GATE_TIER_SCHEMA, model: "haiku", effort: "low" }
  );
  const ciPart = watch ? { ciWait: protectedWait(probe) } : {};
  if (!probe || !probe.exists || !probe.gate) {
    return { gate: t.gate || a.gate, source: "fallback", tier: "default", ...ciPart };
  }
  return { gate: probe.gate, source: "classifier", tier: "computed", ...ciPart };
}

/**
 * Whether a gate probe's `--protected` run demands a CI wait. A missing probe, a missing exit
 * code, and any non-zero exit fail closed to true; an absent classifier is false; otherwise the
 * mode's stdout names `ciWait` exactly when the range touched a protected path.
 */
function protectedWait(probe) {
  if (!probe) {
    return true;
  }
  if (!probe.exists) {
    return false;
  }
  if (probe.protectedExit !== 0) {
    return true;
  }
  return /ciWait/.test(String(probe.protectedOut || ""));
}

function logGateTier(t, resolved) {
  log(`task ${t.id}: gate tier ${resolved.tier} (${resolved.source})`);
}

/** True for a sequential run that was handed a pull request to read CI from. */
function ciActive(a) {
  return Boolean(a && a.ci && a.ci.pr != null && a.parallel !== true);
}

/** The most `ci-green --wait` dispatches one check may take before it reads as unavailable. */
const CI_MAX_WAITS = 12;

/**
 * Pushes the repo's HEAD through a probe agent and returns the push record
 * `{ pushed, sha, pushedAt }`. A failed probe or a failed push is `pushed: false`.
 */
async function pushHead(a, label) {
  const out = await agent(
    [
      `Repo: ${a.repo}`,
      `Work in that repo: cd to it first and use absolute paths under it. It governs over any working directory your environment block names, which follows the conductor session and can point at another worktree.`,
      `Run \`git push\` there (if the branch has no upstream, \`git push -u origin HEAD\`). Never force push and never change any other ref.`,
      `Then run \`git rev-parse HEAD\` and \`date -u +%Y-%m-%dT%H:%M:%SZ\`. Report pushed: true only when the push exited 0, sha as the HEAD SHA, and pushedAt as the date output taken straight after the push. On a failed push report pushed: false with the same two values.`,
      `Do not run any other command and never modify a file.`
    ].join("\n"),
    { label, phase: "Implement", schema: PUSH_SCHEMA, model: "haiku", effort: "low" }
  );
  const ok = Boolean(out && out.pushed === true && out.sha && String(out.pushedAt || "").trim());
  return { pushed: ok, sha: ok ? String(out.sha).trim() : "", pushedAt: out && out.pushedAt ? String(out.pushedAt).trim() : "" };
}

/**
 * Reads CI for one accepted task's pushed SHA. Returns `{ kind: "green" }`, `{ kind: "red",
 * record }` (red, or missing: ci-green exit 1 or 2), or `{ kind: "unavailable", record }`
 * (exit 3, any exit outside the five codes, a failed push or probe, or a check still pending
 * after CI_MAX_WAITS dispatches). Each dispatch is one `ci-green --wait` call, and the runner
 * re-dispatches on exit 75.
 */
async function ciCheck(a, entry) {
  const { task, ci } = entry;
  const unavailable = (exitCode, reason) => ({ kind: "unavailable", record: { sha: ci.sha, task, exitCode, reason } });
  if (!ci.pushed) {
    return unavailable(null, "the commit was not pushed (push failed), so there is no SHA to read");
  }
  const cmd = `ci-green ${ci.sha} --pr ${a.ci.pr} --wait --pushed-at ${ci.pushedAt} --task ${task}`;
  for (let n = 1; n <= CI_MAX_WAITS; n += 1) {
    const out = await agent(
      [
        `Repo: ${a.repo}`,
        `Work in that repo: cd to it first and use absolute paths under it. It governs over any working directory your environment block names, which follows the conductor session and can point at another worktree.`,
        `Run exactly \`${cmd}\` from the repo root as a plain foreground Bash call with \`timeout: 600000\`. It blocks up to 540 seconds. On exit 75 (still pending), re-issue the identical call; stop on any other exit. Never poll a log, never run anything else, and never modify a file.`,
        `Report exitCode as the last exit code, exactly as it exited (null when the command never ran or was not found), and output as that call's full stdout verbatim (the last 200 lines at most). Do not summarize, interpret, or reorder a line.`,
        "Skip agent-memory maintenance for this dispatch."
      ].join("\n"),
      { label: `ci:${task}`, phase: "Review", schema: CI_SCHEMA, model: "haiku", effort: "low" }
    );
    if (!out) {
      return unavailable(null, "the ci-green probe returned no report");
    }
    const code = out.exitCode;
    const detail = String(out.output || "");
    if (code === 0) {
      return { kind: "green" };
    }
    if (code === 1 || code === 2) {
      return { kind: "red", record: { sha: ci.sha, task, verdict: code === 1 ? "red" : "missing", exitCode: code, detail } };
    }
    if (code !== 75) {
      return unavailable(code, `ci-green exited ${code === null ? "without a code" : code}${detail ? `: ${detail}` : ""}`);
    }
  }
  return unavailable(75, `ci-green still pending after ${CI_MAX_WAITS} waits`);
}

/**
 * Runs the checks a task about to be dispatched owes. Before task `i` starts, task `i - 2`'s
 * accepted SHA must read green, and so must task `i - 1`'s when that task set `ci.wait`. A
 * green check is marked on its ledger entry so nothing reads twice. Returns the first
 * non-green check, or null.
 */
async function ciBeforeDispatch(a, ledger, i) {
  for (const k of [i - 2, i - 1]) {
    const entry = ledger[k];
    if (!entry || entry.checked || (k === i - 1 && !entry.ci.wait)) {
      continue;
    }
    const verdict = await ciCheck(a, entry);
    if (verdict.kind !== "green") {
      log(`task ${entry.task}: CI ${verdict.kind}; the run halts before task ${i + 1}`);
      return verdict;
    }
    entry.checked = true;
  }
  return null;
}

async function runTask(t, a, classifierExists) {
  const implementer = a.implementer;
  const reviewer = a.reviewer || "diff-reviewer";
  const maxFix = a.maxFix == null ? 1 : a.maxFix;
  const cls = classOf(t, a);
  const reviewerModel = a.reviewerModel || (cls ? cls.reviewerModel : DEFAULT_REVIEWER_MODEL);
  const batchedNotes = [];
  const outOfScope = [];

  // A task may name an implementer model override (t.model); a dispatch's model option takes
  // precedence over the agent definition's pinned model, so an undeclared task must pass no
  // model at all and let the implementer's own frontmatter pin stand.
  const implOpts = t.model ? { model: t.model } : {};

  const baseSha = await recordBaseSha(a, `base:${t.id}`);

  let implReport = await agent(implementPrompt(t, a, null, baseSha, classifierExists), {
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

  const ciOn = ciActive(a);
  let pushRecord = ciOn ? await pushHead(a, `push:${t.id}`) : null;

  let resolvedGate = await resolveGate(t, a, baseSha, classifierExists, `gatetier:${t.id}`);
  logGateTier(t, resolvedGate);

  let gateRun = await runGateIndependently(t, a, cls, gateToRun(resolvedGate, null, cls, ""), `gaterun:${t.id}`);
  let review = await agent(reviewPrompt(t, a, implReport, resolvedGate, null, gateRun), {
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
  outOfScope.push(...(review.outOfScope || []), ...implFriction(implReport));

  let fixRounds = 0;
  while (review.verdict === "fix" && fixRounds < maxFix) {
    fixRounds += 1;
    const reduced = reducedGateFor(t, a, cls, review.blocking);
    // A class-default reduced round runs the implementer's concrete command only after checking
    // it against this round's diff, so the round's base is captured before the fix dispatch.
    const classDefault = Boolean(cls && reduced === CLASS_DEFAULT_REDUCED_GATE);
    const roundBase = classDefault ? await recordBaseSha(a, `base:${t.id}:fix${fixRounds}`) : "";
    implReport = await agent(implementPrompt(t, a, review.blocking, baseSha, classifierExists), {
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

    if (ciOn) {
      pushRecord = await pushHead(a, `push:${t.id}:fix${fixRounds}`);
    }

    resolvedGate = await resolveGate(t, a, baseSha, classifierExists, `gatetier:${t.id}:fix${fixRounds}`);
    logGateTier(t, resolvedGate);

    let reducedCheck = null;
    if (classDefault && implReport.gateCommand && Array.isArray(implReport.reducedTestFiles)) {
      const touched = await touchedFiles(a.repo, roundBase, "Review", `touched:${t.id}:fix${fixRounds}`);
      reducedCheck = { attempted: true, concrete: validatedReducedCommand(implReport, touched, a.repo) };
      log(`task ${t.id}: fix ${fixRounds} reduced command ${reducedCheck.concrete ? "validated" : "failed the diff check; the reviewer reproduces the gate"}`);
    }
    gateRun = await runGateIndependently(t, a, cls, gateToRun(resolvedGate, reduced, cls, reducedCheck && reducedCheck.concrete), `gaterun:${t.id}:fix${fixRounds}`);
    review = await agent(reviewPrompt(t, a, implReport, resolvedGate, reduced, gateRun, reducedCheck), {
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
  outOfScope.push(...(review.outOfScope || []), ...implFriction(implReport));
  }

  const status = taskStatus(review, implReport);
  log(`task ${t.id} (${t.title}): ${status}, verdict ${review.verdict}, fixRounds ${fixRounds}${cls ? `, class ${cls.name}, ${batchedNotes.length} coverage notes batched` : ""}`);

  const record = { id: t.id, title: t.title, status, fixRounds, implementer: implReport, review, outOfScope };
  if (ciOn) {
    record.ci = { ...pushRecord, wait: Boolean(resolvedGate.ciWait || t.ciWait || (cls && cls.ciWait)) };
  }
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
  log("NOTE: past ~30 minutes unattended, arm the runaway guard with `claude-wf-guard <transcript-dir> <tier> [run-id]` and start /loop with no interval as the wake-up (unattended-work-guards.md); the sleep inhibitor is already tool-enforced.");
  phase("Implement");

  validateArgs(args);

  const classifierExists = await resolveClassifier(args);

  let results;
  const ledger = [];
  let ciRed = null;
  let ciUnavailable = null;

  if (args.parallel === true) {
    results = await parallel(
      args.tasks.map((t) => async () => {
        if (isDeferred()) {
          log(`task ${t.id} (${t.title}): deferred for budget`);
          return { id: t.id, title: t.title, status: "deferred", fixRounds: 0, implementer: null, review: null };
        }
        return runTask(t, args, classifierExists);
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
      if (ciActive(args)) {
        const halt = await ciBeforeDispatch(args, ledger, i);
        if (halt) {
          if (halt.kind === "red") ciRed = halt.record;
          else ciUnavailable = halt.record;
          for (const rest of args.tasks.slice(i)) {
            results.push({ id: rest.id, title: rest.title, status: "skipped", fixRounds: 0, implementer: null, review: null });
          }
          break;
        }
      }
      const record = await runTask(t, args, classifierExists);
      results.push(record);
      if (record.status === "accepted" && record.ci) {
        ledger[i] = { task: t.id, ci: record.ci, checked: false };
      }
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

  const unchecked = ciActive(args) ? ledger.filter((e) => e && !e.checked).map((e) => ({ task: e.task, sha: e.ci.sha, pushedAt: e.ci.pushedAt })) : [];
  if (unchecked.length > 0) {
    log(`CI never read green for: ${unchecked.map((u) => `task ${u.task} ${u.sha || "(not pushed)"}`).join("; ")}`);
  }
  const ciPart = ciActive(args)
    ? {
        ci: { pr: args.ci.pr, unchecked },
        ...(ciRed ? { ciRed } : {}),
        ...(ciUnavailable ? { ciUnavailable } : {})
      }
    : {};
  return { tasks: results, tally: finalTally, spent: budget.spent(), outOfScope: results.flatMap((r) => (r.outOfScope || []).map((o) => ({ task: r.id, ...o }))), ...ciPart };
}

return main();
