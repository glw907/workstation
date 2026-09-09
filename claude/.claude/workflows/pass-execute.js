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
//       tasks: [
//         { id: "1", title: "...", criteria: "...", files: ["..."], notes: "..." }
//       ]
//     }
//   })
//
// The conductor reads only the returned per-task records. It never reads a
// diff, a gate transcript, or an agent's full report; the review step already
// did that.

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
    unspecifiedDecisions: { type: "array", items: { type: "string" } },
    couldNotDo: { type: "array", items: { type: "string" } },
    summary: { type: "string" }
  },
  required: ["filesTouched", "gate", "gateOutput", "unspecifiedDecisions", "couldNotDo", "summary"]
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
          fix: { type: "string" }
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

function implementPrompt(t, a, blocking) {
  const lines = [
    `Repo: ${a.repo}`,
    `Task ${t.id}: ${t.title}`,
    `Acceptance criteria: ${t.criteria}`,
    t.files ? `Files: ${t.files.join(", ")}` : "Files: not specified",
    t.notes ? `Notes: ${t.notes}` : "",
    `Gate command: ${t.gate || a.gate}`,
    "Run the gate through `cairn-run-gate '<the gate string>'` (it blocks to completion and prints the tail); never poll a log; report its exact result.",
    "Skip agent-memory maintenance for this dispatch."
  ];
  if (blocking && blocking.length > 0) {
    lines.push("The previous attempt failed review. Fix exactly these blocking findings:");
    for (const b of blocking) {
      lines.push(`- ${b.location}: ${b.finding}. Fix: ${b.fix}`);
    }
  }
  return lines.filter(Boolean).join("\n");
}

function reviewPrompt(t, a, implReport) {
  return [
    `Repo: ${a.repo}`,
    `Task ${t.id}: ${t.title}`,
    `Acceptance criteria: ${t.criteria}`,
    `Gate command: ${t.gate || a.gate}`,
    "Implementer report (JSON):",
    JSON.stringify(implReport)
  ].join("\n");
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

async function runTask(t, a) {
  const implementer = a.implementer;
  const reviewer = a.reviewer || "diff-reviewer";
  const maxFix = a.maxFix == null ? 1 : a.maxFix;

  // A task may name an implementer model override (t.model); agent()'s model
  // option takes precedence over the agent definition's pinned model.
  const implOpts = t.model ? { model: t.model } : {};

  let implReport = await agent(implementPrompt(t, a, null), {
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

  let review = await agent(reviewPrompt(t, a, implReport), {
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
    implReport = await agent(implementPrompt(t, a, review.blocking), {
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

    review = await agent(reviewPrompt(t, a, implReport), {
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
