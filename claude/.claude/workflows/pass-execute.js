// Runs a pass plan's task list through the thin-conductor chain: implement,
// review, fix-loop, gate. The conductor invokes this instead of dispatching
// the chain per task inline.
//
// Invocation from the conductor session:
//
//   Workflow({
//     scriptPath: "~/.claude/workflows/pass-execute.js",
//     args: {
//       repo: "/home/glw907/Projects/<repo>",
//       gate: "npm run check && npm test",
//       implementer: "cairn-implementer",
//       reviewer: "diff-reviewer",       // optional, defaults below
//       maxFix: 1,                        // optional, defaults below
//       parallel: false,                  // optional, defaults to sequential
//       reducedGate: "...",               // optional; the gate string a fix round runs
//                                         // when every blocking finding is commentOnly.
//                                         // Absent means every round runs the full gate,
//                                         // which is the unchanged behavior.
//       tasks: [
//         { id: "1", title: "...", criteria: "...", files: ["..."], notes: "..." }
//       ]
//     }
//   })
//
// The conductor reads only the returned per-task records. It never reads a
// diff, a gate transcript, or an agent's full report; the review step already
// did that.
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

export const meta = {
  name: "pass-execute",
  description: "Runs a pass plan's tasks through implementer, diff-reviewer, and gate in a chain.",
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

function validateArgs(a) {
  if (!a || typeof a !== "object") {
    throw new Error("args must be an object");
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
  const paintFlag = t.paint != null ? ` --paint ${t.paint ? "yes" : "no"}` : "";
  const pinFlag = t.gateTier ? ` --pin ${t.gateTier}` : "";
  const light = (t.gateLane || a.gateLane) === "light";
  const lanePrefix = light ? "CAIRN_GATE_LANE=light " : "";
  const laneNote = light ? " (keep the CAIRN_GATE_LANE=light prefix on the first call and on every re-issue: this gate launches no browser, so it takes the light lane)" : "";
  const classifierCmd = `node scripts/checks/gate-tier.mjs --range ${baseSha}..HEAD${paintFlag}${pinFlag}`;
  const lines = [
    `Repo: ${a.repo}`,
    `Task ${t.id}: ${t.title}`,
    `Acceptance criteria: ${t.criteria}`,
    t.files ? `Files: ${t.files.join(", ")}` : "Files: not specified",
    t.notes ? `Notes: ${t.notes}` : "",
    `Gate command: ${t.gate || a.gate}`,
    `Before running the gate, check whether scripts/checks/gate-tier.mjs exists in this repo. If it does, run \`${classifierCmd}\` from the repo root, after your commits and before the gate, and run the gate string it prints on stdout instead of the Gate command above (report gateTier: "${t.gateTier ? "pin" : "computed"}" and gateCommand as that exact string). If the script is absent, exits non-zero, or prints nothing, run the Gate command above unchanged (report gateTier: "default" and gateCommand as that string).`,
    "Run the gate through `" + lanePrefix + "cairn-run-gate '<the gate string>'`" + laneNote + " (it blocks to completion and prints the tail); never poll a log; report its exact result.",
    "Skip agent-memory maintenance for this dispatch."
  ];
  if (blocking && blocking.length > 0) {
    lines.push("The previous attempt failed review. Fix exactly these blocking findings:");
    for (const b of blocking) {
      lines.push(`- ${b.location}: ${b.finding}. Fix: ${b.fix}`);
    }
    if (a.reducedGate && blocking.every((b) => b.commentOnly)) {
      lines.push(`Every finding above is COMMENT-ONLY (the fix changes comment or doc text, never code behavior). For this fix round the gate is reduced: run \`${a.reducedGate}\` through cairn-run-gate and report that reduced gate as the gate result; do not run the full gate string. If your fix diff touches any non-comment line, run the full gate string instead.`);
    }
  }
  return lines.filter(Boolean).join("\n");
}

function reviewPrompt(t, a, implReport, resolvedGate) {
  const ranCommand = implReport.gateCommand || t.gate || a.gate;
  const mismatch =
    resolvedGate.gate && implReport.gateCommand && implReport.gateCommand !== resolvedGate.gate
      ? `MISMATCH: the runner independently resolved a different gate string ("${resolvedGate.gate}") than the implementer reports running. Treat this mismatch itself as a blocking finding.`
      : "";
  return [
    `Repo: ${a.repo}`,
    `Task ${t.id}: ${t.title}`,
    `Acceptance criteria: ${t.criteria}`,
    `The gate string this task ran: ${ranCommand}`,
    `Reproduce the gate with: ${resolvedGate.gate}`,
    mismatch,
    a.reducedGate
      ? `For each blocking finding set commentOnly: true when its fix changes only comment or doc text and no code behavior; a fix round whose findings are all comment-only runs the reduced gate \`${a.reducedGate}\`, so mark it honestly. If you are reviewing such a fix round, that reduced gate is the expected gate.`
      : "",
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

  let review = await agent(reviewPrompt(t, a, implReport, resolvedGate), {
    label: `review:${t.id}`,
    phase: "Review",
    model: "claude-opus-5",
    agentType: reviewer,
    schema: REVIEW_SCHEMA
  });

  if (!review) {
    log(`task ${t.id}: reviewer failed to return a verdict`);
    return { id: t.id, title: t.title, status: "failed", fixRounds: 0, implementer: implReport, review: null };
  }

  let fixRounds = 0;
  while (review.verdict === "fix" && fixRounds < maxFix) {
    fixRounds += 1;
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

    review = await agent(reviewPrompt(t, a, implReport, resolvedGate), {
      label: `review:${t.id}:fix${fixRounds}`,
      phase: "Review",
      model: "claude-opus-5",
      agentType: reviewer,
      schema: REVIEW_SCHEMA
    });

    if (!review) {
      log(`task ${t.id}: reviewer failed on fix round ${fixRounds}`);
      return { id: t.id, title: t.title, status: "failed", fixRounds, implementer: implReport, review: null };
    }
  }

  const status = taskStatus(review, implReport);
  log(`task ${t.id} (${t.title}): ${status}, verdict ${review.verdict}, fixRounds ${fixRounds}`);

  return { id: t.id, title: t.title, status, fixRounds, implementer: implReport, review };
}

function tally(results) {
  const t = { accepted: 0, needsDecision: 0, escalated: 0, failed: 0, deferred: 0 };
  for (const r of results) {
    if (r.status === "accepted") t.accepted += 1;
    else if (r.status === "needs-decision") t.needsDecision += 1;
    else if (r.status === "escalated") t.escalated += 1;
    else if (r.status === "failed") t.failed += 1;
    else if (r.status === "deferred") t.deferred += 1;
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
    results = [];
    for (const t of args.tasks) {
      if (isDeferred()) {
        log(`task ${t.id} (${t.title}): deferred for budget`);
        results.push({ id: t.id, title: t.title, status: "deferred", fixRounds: 0, implementer: null, review: null });
        continue;
      }
      const record = await runTask(t, args);
      results.push(record);
    }
  }

  phase("Report");

  const finalTally = tally(results);
  log(`tally: accepted ${finalTally.accepted}, needs-decision ${finalTally.needsDecision}, escalated ${finalTally.escalated}, failed ${finalTally.failed}, deferred ${finalTally.deferred}`);

  return { tasks: results, tally: finalTally, spent: budget.spent() };
}

return main();
