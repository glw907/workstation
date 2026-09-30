// Chain-aware variant of ~/.claude/workflows/pass-execute.js: a plan's mutually independent
// chains run in parallel, each in its own git worktree (or the main checkout, when the plan
// says so), with the tasks inside a chain strictly sequential.
// The conductor reads only the returned per-task records. A task may carry `model`
// ("opus" or "fable") to upshift its implementer dispatch per the workstation rule, and
// `gate` to override the chain's gate string for that task alone (paint tasks keep the e2e).
// `args.mainCheckout`, when a chain's `repo` equals it, tells the prompts that the chain runs on
// main by its plan's rule rather than in a worktree, so the never-touch-main sentence is dropped.
//
// Gate tier (Geoff, 2026-09-15): when `<chain.repo>/scripts/checks/gate-tier.mjs` exists, the
// gate string for a task is chosen from its committed diff rather than fixed by the plan. A task
// may carry `gateTier` to pin a tier the diff cannot size (a token value); a task's `paint` flag
// (true/false) is passed through as the classifier's `--paint` flag. The implementer runs the
// classifier itself (its prompt says how) and reports the tier and string it ran; the runner
// independently resolves the same tier via a probe agent and hands the reviewer both, flagging a
// mismatch as blocking. The workflow runtime has no filesystem or exec access, so every git/node
// call here goes through a small probe agent rather than direct code.

// Gate lane (Geoff, 2026-09-20): `args.gateLane` or a task's `gateLane` set to "light" makes the
// implementer prefix every cairn-run-gate call with CAIRN_GATE_LANE=light, for a gate that launches
// no browser (a Go `make check`, a lint-only run). Unset means the default heavy lane.

// Pass class (Geoff, 2026-09-27): `args.passClass` or a task's `passClass` selects the test mandate,
// the reviewer's blocking bar and model, and whether a test-only fix round takes the reduced gate
// (`t.reducedGate`, `args.reducedGate`, or the class default: the repo's type check plus only the
// test files this fix round touched). Coverage-only findings under a non-blocking class move to
// nonBlocking and return as `batchedNotes`. Full rationale in pass-execute.js; without a passClass
// every prompt is the pre-class one.

// Classifier caching (AW-13): a chain's own `classifier` boolean, else `args.classifier`, else one
// cached existence probe (`model: "haiku"`) for whether that chain's repo carries
// `scripts/checks/gate-tier.mjs`, run once per chain and reused for every task in it.
// `classifier: false` skips the probe entirely: no per-task tier probe ever runs for that chain,
// and the implementer prompt renders no classifier paragraph.

export const meta = {
  name: "pass-execute-chains",
  description: "Runs a pass plan's chains in parallel worktrees, tasks sequential within each chain",
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
    commits: { type: "array", items: { type: "string" } },
    unspecifiedDecisions: { type: "array", items: { type: "string" } },
    couldNotDo: { type: "array", items: { type: "string" } },
    summary: { type: "string" },
    // Both optional: only present when the repo has a gate-tier classifier
    // script. gateTier is "pin", "computed", or "default"; gateCommand is the
    // exact gate string the implementer ran.
    gateTier: { type: "string" },
    gateCommand: { type: "string" },
    // Optional: one row per mutation the plan named for this task, so the auth-data mandate
    // can be met. Never in `required`, since a consumer whose implementer definition does not
    // name mutations must not be asked for it.
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
    }
  },
  required: ["filesTouched", "gate", "gateOutput", "commits", "unspecifiedDecisions", "couldNotDo", "summary"]
};

const GATE_PROBE_SCHEMA = {
  type: "object",
  properties: {
    sha: { type: "string" }
  },
  required: ["sha"]
};

const CLASSIFIER_PROBE_SCHEMA = {
  type: "object",
  properties: {
    exists: { type: "boolean" }
  },
  required: ["exists"]
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
          commentOnly: { type: "boolean" },
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
        properties: { location: { type: "string" }, finding: { type: "string" } },
        required: ["location", "finding"]
      }
    }
  },
  required: ["verdict", "summary", "blocking", "nonBlocking", "gate", "unspecified"]
};

const DEFAULT_REVIEWER_MODEL = "claude-opus-5-5";

// The class table. `mandate` goes to the implementer, `bar` to the reviewer; `coverageBlocks`
// false demotes coverageOnly findings; `testOnlyReduces` lets a test-only fix round take the
// reduced gate. Keep in step with pass-execute.js.
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

// Repo-neutral (RC4): a reduced round never assumes npm. The class default names no tool the
// runner cannot know the repo has; a plan that needs a specific reduced gate names it as
// `t.reducedGate` or `args.reducedGate`.
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

function implementPrompt(t, chain, a, blocking, baseSha, classifierExists) {
  const cls = classOf(t, a);
  const onMain = chain.repo === a.mainCheckout;
  const paintFlag = t.paint != null ? ` --paint ${t.paint ? "yes" : "no"}` : "";
  const pinFlag = t.gateTier ? ` --pin ${t.gateTier}` : "";
  const light = (t.gateLane || a.gateLane || (cls && cls.gateLane)) === "light";
  const lanePrefix = light ? "CAIRN_GATE_LANE=light " : "";
  const laneNote = light ? " (keep the CAIRN_GATE_LANE=light prefix on the first call and on every re-issue: this gate launches no browser, so it takes the light lane and does not queue behind a browser gate)" : "";
  const classifierCmd = `node scripts/checks/gate-tier.mjs --range ${baseSha}..HEAD${paintFlag}${pinFlag}`;
  const lines = [
    onMain
      ? `Repo (the main checkout, branch main; this pass runs on main by its plan's rule, no worktree, commit directly on main): ${chain.repo}`
      : `Repo (your working directory, a dedicated git worktree on branch ${chain.branch}): ${chain.repo}`,
    onMain
      ? `You are the ONLY writer in this checkout for the duration of this task.`
      : `You are the ONLY writer in this worktree. Work only here, never in the main checkout.`,
    `Plan file (an absolute path): ${a.planPath}`,
    `Task ${t.id}: ${t.title}`,
    ``,
    `FIRST read, in the plan file: the "Global constraints" section, the "Ruled inputs" section (if present), and the full "Task ${t.id}" section (its Files, Interfaces, Steps, and Acceptance criteria). The plan section is the authority; the criteria below are the condensed form.`,
    `Acceptance criteria (condensed): ${t.criteria}${a.paintProtocol ? " " + a.paintProtocol : ""}`,
    t.files ? `Files: ${t.files.join(", ")}` : "",
    t.notes ? `Notes: ${t.notes}` : "",
    cls ? `Pass class: ${cls.name}. Test mandate: ${cls.mandate}` : "",
    ``,
    `Gate command: ${t.gate || a.gate}`,
    classifierExists
      ? `Before running the gate, check whether scripts/checks/gate-tier.mjs exists in this repo. If it does, run \`${classifierCmd}\` from the repo root, after your commits and before the gate, and run the gate string it prints on stdout instead of the Gate command above (report gateTier: "${t.gateTier ? "pin" : "computed"}" and gateCommand as that exact string). If the script is absent, exits non-zero, or prints nothing, run the Gate command above unchanged (report gateTier: "default" and gateCommand as that string).`
      : "",
    `Run the gate ONLY through \`${lanePrefix}cairn-run-gate '<the gate string>'\`${laneNote} as a plain foreground Bash call with \`timeout: 600000\`, and follow its own output for whether to re-issue and for the result: never run the gate or any test yourself with run_in_background, and never tail, wc, cat, ps, or sleep on a log. A transcript containing such polling calls is a task failure the conductor halts. Report the runner's exact exit line.`,
    `Commit at each step boundary the plan marks "Commit", following the repo's git conventions (imperative mood, specific files, the repo's co-author footer). Report every commit SHA you made in the commits field.`,
    `Scope expectation: this is one focused task; sweeps rewrite comments, casts, and whitespace and never behavior unless the plan section says a step is behavioral; if you find yourself changing logic the plan does not name as changing, stop and report it in unspecifiedDecisions instead.`,
    `Skip agent-memory maintenance for this dispatch.`
  ];
  if (blocking && blocking.length > 0) {
    lines.push("The previous attempt failed review. Fix exactly these blocking findings (fix commits on top, do not rewrite history):");
    for (const b of blocking) {
      lines.push(`- ${b.location}: ${b.finding}. Fix: ${b.fix}`);
    }
    const reduced = reducedGateFor(t, a, cls, blocking);
    if (reduced && !cls) {
      lines.push(`Every finding above is COMMENT-ONLY (the fix changes comment or doc text, never code behavior). For this fix round the gate is reduced: run ${renderGateText(reduced)} through cairn-run-gate and report that reduced gate as the gate result; do not run the full gate string. If your fix diff touches any non-comment line, run the full gate string instead.`);
    } else if (reduced) {
      lines.push(`Every finding above is COMMENT-ONLY or TEST-ONLY (the fix changes comment or doc text, or test files alone, never source behavior). For this fix round the gate is reduced: run ${renderGateText(reduced)}, through cairn-run-gate, and report that exact string as gateCommand and its result as the gate result; do not run the full gate string. If your fix diff touches any source line outside tests and comments, run the full gate string instead.`);
    }
  }
  return lines.filter(Boolean).join("\n");
}

// === GATE MATCHER (tests extract this block; kept identical in pass-execute.js) ===
/**
 * Normalizes a gate string for comparison: keeps only its last non-empty line (a probe can
 * return the classifier's whole stdout, preamble and all), unwraps a `cairn-run-gate '<cmd>'`
 * call, and treats an absolute repo path and its repo-relative form, or extra spacing, as the
 * same target.
 */
function gateCore(s, repo) {
  const last = String(s).trim().split("\n").pop().trim();
  const wrapped = last.match(/cairn-run-gate\s+'([^']+)'/);
  const cmd = wrapped ? wrapped[1] : last;
  return cmd.split(`${repo}/`).join("").replace(/\s+/g, " ").trim();
}

/**
 * True when the gate string the implementer ran matches the gate string the runner
 * independently resolved. A task gate may carry a `<placeholder>` the implementer fills in (for
 * example `<the touched unit test files>`); the placeholder matches any non-empty text.
 */
function gateMatches(ran, resolved, repo) {
  const pattern = gateCore(resolved, repo)
    .split(/<[^<>]+>/)
    .map((part) => part.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join(".+?");
  return new RegExp(`^${pattern}$`).test(gateCore(ran, repo));
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

function reviewPrompt(t, chain, a, implReport, resolvedGate, reduced) {
  const cls = classOf(t, a);
  const ranCommand = implReport.gateCommand || t.gate || a.gate;
  // Any reduced round, class-based or the pre-class a.reducedGate fallback, is exempt from the
  // mismatch check: its expected gate is the reduced one, not resolvedGate.
  const mismatch =
    !reduced && resolvedGate.gate && implReport.gateCommand && !gateMatches(implReport.gateCommand, resolvedGate.gate, chain.repo)
      ? `MISMATCH: the runner independently resolved a different gate string ("${resolvedGate.gate}") than the implementer reports running. Treat this mismatch itself as a blocking finding.`
      : "";
  return [
    chain.repo === a.mainCheckout
      ? `Repo (the main checkout, branch main; this pass runs on main by its plan's rule): ${chain.repo}`
      : `Repo (a dedicated git worktree on branch ${chain.branch}): ${chain.repo}`,
    `Plan file: ${a.planPath}`,
    `Task ${t.id}: ${t.title}`,
    `Read the plan's "Task ${t.id}" section (its acceptance criteria are the contract) plus the "Global constraints" section before verdicting.`,
    ...(cls
      ? reviewClassLines(cls, reduced)
      : [noClassReviewLine(t, a)]),
    `Acceptance criteria (condensed): ${t.criteria}${a.paintProtocol ? " " + a.paintProtocol : ""}`,
    `The task's diff is exactly the commits the implementer reports below (diff each against its parent; the worktree has no other writers).`,
    `The gate string this task ran: ${ranCommand}`,
    `Reproduce the gate with: ${resolvedGate.gate}`,
    mismatch,
    "Out of scope: list in outOfScope any real defect you notice outside this task's criteria (a bug, a stale doc or comment, a false claim, a gate gap), one {location, finding} each. It never affects the verdict; the conductor files each one in the repo's friction log.",
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
  return "needs-decision";
}

/**
 * Captures the task's starting commit before the implementer's first
 * dispatch. The gate-tier classifier diffs against this base, and it must be
 * captured before any commit lands, since HEAD moves as soon as the
 * implementer commits. The workflow runtime has no direct git access, so a
 * minimal probe agent runs the command instead.
 */
async function recordBaseSha(chain, phaseName, label) {
  const out = await agent(
    `Repo: ${chain.repo}\nRun \`git rev-parse HEAD\` there and report exactly that commit SHA, nothing else.`,
    { label, phase: phaseName, schema: GATE_PROBE_SCHEMA, model: "haiku", effort: "low" }
  );
  return out && out.sha ? out.sha.trim() : "";
}

/**
 * Resolves, once per chain, whether that chain's repo carries the gate-tier classifier
 * script, caching the answer for every task in the chain. An explicit `chain.classifier` or
 * `args.classifier` boolean skips the probe entirely; `classifier: false` means no per-task
 * tier probe ever runs for this chain and the implementer prompt renders no classifier
 * paragraph.
 */
async function resolveClassifier(chain, a) {
  if (typeof chain.classifier === "boolean") {
    return chain.classifier;
  }
  if (typeof a.classifier === "boolean") {
    return a.classifier;
  }
  const probe = await agent(
    [
      `Repo: ${chain.repo}`,
      `Check whether the file scripts/checks/gate-tier.mjs exists there. Report exists: true or exists: false.`,
      `Do not run any other command and never modify a file.`
    ].join("\n"),
    { label: `classifier:${chain.id}`, phase: `Chain ${chain.id}`, schema: CLASSIFIER_PROBE_SCHEMA, model: "haiku", effort: "low" }
  );
  return !!(probe && probe.exists);
}

/**
 * Resolves the gate string the runner hands the reviewer, independently of
 * whatever the implementer ran. A plan pin (`t.gateTier`) skips the
 * classifier entirely and keeps the task's declared gate string, matching
 * pre-classifier behavior; so does a chain whose cached `classifierExists` is false. Any
 * other task asks a probe agent to run the classifier over the task's diff
 * so far (base..HEAD, which grows across fix rounds).
 */
async function resolveGate(t, chain, a, baseSha, classifierExists, phaseName, label) {
  if (t.gateTier) {
    return { gate: t.gate || a.gate, source: "pin", tier: t.gateTier };
  }
  if (!classifierExists) {
    return { gate: t.gate || a.gate, source: "fallback", tier: "default" };
  }
  const paintFlag = t.paint != null ? ` --paint ${t.paint ? "yes" : "no"}` : "";
  const cmd = `node scripts/checks/gate-tier.mjs --range ${baseSha}..HEAD${paintFlag}`;
  const probe = await agent(
    [
      `Repo: ${chain.repo}`,
      `Check whether the file scripts/checks/gate-tier.mjs exists there.`,
      `If it does not, report exists: false and gate: "".`,
      `If it does, run exactly \`${cmd}\` from the repo root and report exists: true and gate: "<its exact stdout, trimmed>". On a non-zero exit or empty stdout, report exists: true and gate: "".`,
      `Do not run any other command and never modify a file.`
    ].join("\n"),
    { label, phase: phaseName, schema: GATE_TIER_SCHEMA, model: "haiku", effort: "low" }
  );
  if (!probe || !probe.exists || !probe.gate) {
    return { gate: t.gate || a.gate, source: "fallback", tier: "default" };
  }
  return { gate: probe.gate, source: "classifier", tier: "computed" };
}

function logGateTier(t, resolved) {
  log(`task ${t.id}: gate tier ${resolved.tier} (${resolved.source})`);
}

async function runTask(t, chain, a, classifierExists) {
  const maxFix = a.maxFix == null ? 1 : a.maxFix;
  const phaseName = `Chain ${chain.id}`;
  const cls = classOf(t, a);
  const reviewerModel = a.reviewerModel || (cls ? cls.reviewerModel : DEFAULT_REVIEWER_MODEL);
  // A task may name an implementer model override (t.model); a dispatch's model option takes
  // precedence over the agent definition's pinned model, so an undeclared task must pass no
  // model at all and let the implementer's own frontmatter pin stand.
  const implOpts = t.model ? { model: t.model } : {};
  const batchedNotes = [];
  const outOfScope = [];

  const baseSha = await recordBaseSha(chain, phaseName, `base:${t.id}`);

  let implReport = await agent(implementPrompt(t, chain, a, null, baseSha, classifierExists), {
    label: `impl:${t.id}`,
    phase: phaseName,
    agentType: a.implementer,
    schema: IMPL_SCHEMA,
    ...implOpts
  });

  if (!implReport) {
    log(`task ${t.id}: implementer failed to return a report`);
    return { id: t.id, title: t.title, status: "failed", fixRounds: 0, implementer: null, review: null };
  }

  let resolvedGate = await resolveGate(t, chain, a, baseSha, classifierExists, phaseName, `gatetier:${t.id}`);
  logGateTier(t, resolvedGate);

  let review = await agent(reviewPrompt(t, chain, a, implReport, resolvedGate, null), {
    label: `review:${t.id}`,
    phase: phaseName,
    model: reviewerModel,
    agentType: a.reviewer || "diff-reviewer",
    schema: REVIEW_SCHEMA
  });

  if (!review) {
    log(`task ${t.id}: reviewer failed to return a verdict`);
    return { id: t.id, title: t.title, status: "failed", fixRounds: 0, implementer: implReport, review: null };
  }
  batchedNotes.push(...applyClassBar(review, cls));
  outOfScope.push(...(review.outOfScope || []));

  let fixRounds = 0;
  while (review.verdict === "fix" && fixRounds < maxFix) {
    fixRounds += 1;
    const reduced = reducedGateFor(t, a, cls, review.blocking);
    implReport = await agent(implementPrompt(t, chain, a, review.blocking, baseSha, classifierExists), {
      label: `impl:${t.id}:fix${fixRounds}`,
      phase: phaseName,
      agentType: a.implementer,
      schema: IMPL_SCHEMA,
      ...implOpts
    });

    if (!implReport) {
      log(`task ${t.id}: implementer failed on fix round ${fixRounds}`);
      return { id: t.id, title: t.title, status: "failed", fixRounds, implementer: null, review };
    }

    resolvedGate = await resolveGate(t, chain, a, baseSha, classifierExists, phaseName, `gatetier:${t.id}:fix${fixRounds}`);
    logGateTier(t, resolvedGate);

    review = await agent(reviewPrompt(t, chain, a, implReport, resolvedGate, reduced), {
      label: `review:${t.id}:fix${fixRounds}`,
      phase: phaseName,
      model: reviewerModel,
      agentType: a.reviewer || "diff-reviewer",
      schema: REVIEW_SCHEMA
    });

    if (!review) {
      log(`task ${t.id}: reviewer failed on fix round ${fixRounds}`);
      return { id: t.id, title: t.title, status: "failed", fixRounds, implementer: implReport, review: null };
    }
    batchedNotes.push(...applyClassBar(review, cls));
  outOfScope.push(...(review.outOfScope || []));
  }

  const status = taskStatus(review, implReport);
  log(`task ${t.id} (${t.title}): ${status}, verdict ${review.verdict}, fixRounds ${fixRounds}${cls ? `, class ${cls.name}, ${batchedNotes.length} coverage notes batched` : ""}`);
  const record = { id: t.id, title: t.title, status, fixRounds, implementer: implReport, review, outOfScope };
  return cls ? { ...record, passClass: cls.name, batchedNotes } : record;
}

async function runChain(chain, a) {
  const classifierExists = await resolveClassifier(chain, a);
  const results = [];
  for (const t of chain.tasks) {
    const record = await runTask(t, chain, a, classifierExists);
    results.push(record);
    if (record.status !== "accepted") {
      log(`chain ${chain.id}: halting after task ${t.id} (${record.status}); remaining tasks deferred`);
      for (const rest of chain.tasks.slice(chain.tasks.indexOf(t) + 1)) {
        results.push({ id: rest.id, title: rest.title, status: "deferred", fixRounds: 0, implementer: null, review: null });
      }
      break;
    }
  }
  return { chain: chain.id, branch: chain.branch, results };
}

function tally(all) {
  const t = { accepted: 0, needsDecision: 0, escalated: 0, failed: 0, deferred: 0 };
  for (const r of all) {
    if (r.status === "accepted") t.accepted += 1;
    else if (r.status === "needs-decision") t.needsDecision += 1;
    else if (r.status === "escalated") t.escalated += 1;
    else if (r.status === "failed") t.failed += 1;
    else if (r.status === "deferred") t.deferred += 1;
  }
  return t;
}

async function main() {
  log("NOTE: past ~30 minutes unattended, arm the runaway guard with `claude-wf-guard <transcript-dir> <tier> [run-id]` and start /loop with no interval as the wake-up (unattended-work-guards.md); the sleep inhibitor is already tool-enforced.");
  if (!args || !Array.isArray(args.chains) || args.chains.length === 0) {
    throw new Error("args.chains must be a non-empty array");
  }
  if (!args.gate || !args.implementer || !args.planPath) {
    throw new Error("args.gate, args.implementer, and args.planPath are required");
  }
  const classes = [args.passClass, ...args.chains.flatMap((c) => (c.tasks || []).map((t) => t && t.passClass))];
  for (const c of classes) {
    if (c && !PASS_CLASSES[c]) {
      throw new Error(`unknown passClass "${c}"; expected one of ${Object.keys(PASS_CLASSES).join(", ")}`);
    }
  }

  const chainResults = await parallel(args.chains.map((c) => () => runChain(c, args)));
  const kept = chainResults.filter(Boolean);

  phase("Report");
  const flat = kept.flatMap((c) => c.results);
  const finalTally = tally(flat);
  log(`tally: accepted ${finalTally.accepted}, needs-decision ${finalTally.needsDecision}, escalated ${finalTally.escalated}, failed ${finalTally.failed}, deferred ${finalTally.deferred}`);
  return { chains: kept, tally: finalTally, spent: budget.spent(), outOfScope: flat.flatMap((r) => (r.outOfScope || []).map((o) => ({ task: r.id, ...o }))) };
}

return main();
