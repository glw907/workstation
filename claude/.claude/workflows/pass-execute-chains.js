// Chain-aware variant of ~/.claude/workflows/pass-execute.js for the cairn
// internals-B pass: five mutually independent chains run in parallel, each in
// its own git worktree, with the tasks inside a chain strictly sequential.
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
    gateCommand: { type: "string" }
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
          commentOnly: { type: "boolean" }
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

function implementPrompt(t, chain, a, blocking, baseSha) {
  const onMain = chain.repo === a.mainCheckout;
  const paintFlag = t.paint != null ? ` --paint ${t.paint ? "yes" : "no"}` : "";
  const pinFlag = t.gateTier ? ` --pin ${t.gateTier}` : "";
  const classifierCmd = `node scripts/checks/gate-tier.mjs --range ${baseSha}..HEAD${paintFlag}${pinFlag}`;
  const lines = [
    onMain
      ? `Repo (the main checkout, branch main; this pass runs on main by its plan's rule, no worktree, commit directly on main): ${chain.repo}`
      : `Repo (your working directory, a dedicated git worktree on branch ${chain.branch}): ${chain.repo}`,
    onMain
      ? `You are the ONLY writer in this checkout for the duration of this task.`
      : `You are the ONLY writer in this worktree. Work only here, never in the main checkout.`,
    `Plan file (committed in this repo): ${a.planPath}`,
    `Task ${t.id}: ${t.title}`,
    ``,
    `FIRST read, in the plan file: the "Global constraints" section, the "Ruled inputs" section, and the full "Task ${t.id}" section (its Files, Interfaces, Steps, and Acceptance criteria). The plan section is the authority; the criteria below are the condensed form.`,
    `Acceptance criteria (condensed): ${t.criteria}${a.paintProtocol ? " " + a.paintProtocol : ""}`,
    t.files ? `Files: ${t.files.join(", ")}` : "",
    t.notes ? `Notes: ${t.notes}` : "",
    ``,
    `Gate command: ${t.gate || a.gate}`,
    `Before running the gate, check whether scripts/checks/gate-tier.mjs exists in this repo. If it does, run \`${classifierCmd}\` from the repo root, after your commits and before the gate, and run the gate string it prints on stdout instead of the Gate command above (report gateTier: "${t.gateTier ? "pin" : "computed"}" and gateCommand as that exact string). If the script is absent, exits non-zero, or prints nothing, run the Gate command above unchanged (report gateTier: "default" and gateCommand as that string).`,
    `Run the gate ONLY through \`cairn-run-gate '<the gate string>'\` as a plain foreground Bash call with \`timeout: 600000\`. The runner starts the gate detached and waits up to nine minutes; when it prints "gate still running" (exit 75), re-issue the SAME cairn-run-gate command, which reattaches and waits again, and repeat until it prints "gate exit:" with the last 60 lines. That re-issue is the only permitted wait: never run the gate or any test yourself with run_in_background, and never tail, wc, cat, ps, or sleep on a log. A transcript containing such polling calls is a task failure the conductor halts. Report the runner's exact exit line.`,
    `Commit at each step boundary the plan marks "Commit", following the repo's git conventions (imperative mood, specific files, the repo's co-author footer). Report every commit SHA you made in the commits field.`,
    `Scope expectation: this is one focused task; sweeps rewrite comments, casts, and whitespace and never behavior unless the plan section says a step is behavioral; if you find yourself changing logic the plan does not name as changing, stop and report it in unspecifiedDecisions instead.`,
    `Skip agent-memory maintenance for this dispatch.`
  ];
  if (blocking && blocking.length > 0) {
    lines.push("The previous attempt failed review. Fix exactly these blocking findings (fix commits on top, do not rewrite history):");
    for (const b of blocking) {
      lines.push(`- ${b.location}: ${b.finding}. Fix: ${b.fix}`);
    }
    if (blocking.every(b => b.commentOnly)) {
      lines.push("Every finding above is COMMENT-ONLY (the fix changes comment or doc text, never code behavior). For this fix round the gate is reduced by the conductor's 2026-09-09 ruling: run `npm run check:comments && npm run check:symbols && npm run check:docs` plus the unit test files that cover the touched files, through cairn-run-gate, and report that reduced gate as the gate result; do not run the full gate string.");
    }
  }
  return lines.filter(Boolean).join("\n");
}

function reviewPrompt(t, chain, a, implReport, resolvedGate) {
  const ranCommand = implReport.gateCommand || t.gate || a.gate;
  const mismatch =
    resolvedGate.gate && implReport.gateCommand && implReport.gateCommand !== resolvedGate.gate
      ? `MISMATCH: the runner independently resolved a different gate string ("${resolvedGate.gate}") than the implementer reports running. Treat this mismatch itself as a blocking finding.`
      : "";
  return [
    chain.repo === a.mainCheckout
      ? `Repo (the main checkout, branch main; this pass runs on main by its plan's rule): ${chain.repo}`
      : `Repo (a dedicated git worktree on branch ${chain.branch}): ${chain.repo}`,
    `Plan file: ${a.planPath}`,
    `Task ${t.id}: ${t.title}`,
    `Read the plan's "Task ${t.id}" section (its acceptance criteria are the contract) plus the "Global constraints" section before verdicting.`,
    `For each blocking finding set commentOnly: true when its fix changes only comment or doc text and no code behavior; a fix round whose findings are all comment-only runs a reduced gate (check:comments, check:symbols, check:docs, the touched files' unit tests) by the conductor's 2026-09-09 ruling, so mark it honestly. If you are reviewing such a fix round, the reduced gate is the expected gate.`,
    `Acceptance criteria (condensed): ${t.criteria}${a.paintProtocol ? " " + a.paintProtocol : ""}`,
    `The task's diff is exactly the commits the implementer reports below (diff each against its parent; the worktree has no other writers).`,
    `The gate string this task ran: ${ranCommand}`,
    `Reproduce the gate with: ${resolvedGate.gate}`,
    mismatch,
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
    { label, phase: phaseName, schema: GATE_PROBE_SCHEMA, effort: "low" }
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
async function resolveGate(t, chain, a, baseSha, phaseName, label) {
  if (t.gateTier) {
    return { gate: t.gate || a.gate, source: "pin", tier: t.gateTier };
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
    { label, phase: phaseName, schema: GATE_TIER_SCHEMA, effort: "low" }
  );
  if (!probe || !probe.exists || !probe.gate) {
    return { gate: t.gate || a.gate, source: "fallback", tier: "default" };
  }
  return { gate: probe.gate, source: "classifier", tier: "computed" };
}

function logGateTier(t, resolved) {
  log(`task ${t.id}: gate tier ${resolved.tier} (${resolved.source})`);
}

async function runTask(t, chain, a) {
  const maxFix = a.maxFix == null ? 1 : a.maxFix;
  const phaseName = `Chain ${chain.id}`;

  const baseSha = await recordBaseSha(chain, phaseName, `base:${t.id}`);

  let implReport = await agent(implementPrompt(t, chain, a, null, baseSha), {
    label: `impl:${t.id}`,
    phase: phaseName,
    agentType: a.implementer,
    ...(t.model ? { model: t.model } : {}),
    schema: IMPL_SCHEMA
  });

  if (!implReport) {
    log(`task ${t.id}: implementer failed to return a report`);
    return { id: t.id, title: t.title, status: "failed", fixRounds: 0, implementer: null, review: null };
  }

  let resolvedGate = await resolveGate(t, chain, a, baseSha, phaseName, `gatetier:${t.id}`);
  logGateTier(t, resolvedGate);

  let review = await agent(reviewPrompt(t, chain, a, implReport, resolvedGate), {
    label: `review:${t.id}`,
    phase: phaseName,
    model: "claude-opus-5",
    agentType: a.reviewer || "diff-reviewer",
    schema: REVIEW_SCHEMA
  });

  if (!review) {
    log(`task ${t.id}: reviewer failed to return a verdict`);
    return { id: t.id, title: t.title, status: "failed", fixRounds: 0, implementer: implReport, review: null };
  }

  let fixRounds = 0;
  while (review.verdict === "fix" && fixRounds < maxFix) {
    fixRounds += 1;
    implReport = await agent(implementPrompt(t, chain, a, review.blocking, baseSha), {
      label: `impl:${t.id}:fix${fixRounds}`,
      phase: phaseName,
      agentType: a.implementer,
      ...(t.model ? { model: t.model } : {}),
      schema: IMPL_SCHEMA
    });

    if (!implReport) {
      log(`task ${t.id}: implementer failed on fix round ${fixRounds}`);
      return { id: t.id, title: t.title, status: "failed", fixRounds, implementer: null, review };
    }

    resolvedGate = await resolveGate(t, chain, a, baseSha, phaseName, `gatetier:${t.id}:fix${fixRounds}`);
    logGateTier(t, resolvedGate);

    review = await agent(reviewPrompt(t, chain, a, implReport, resolvedGate), {
      label: `review:${t.id}:fix${fixRounds}`,
      phase: phaseName,
      model: "claude-opus-5",
      agentType: a.reviewer || "diff-reviewer",
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

async function runChain(chain, a) {
  const results = [];
  for (const t of chain.tasks) {
    const record = await runTask(t, chain, a);
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
  if (!args || !Array.isArray(args.chains) || args.chains.length === 0) {
    throw new Error("args.chains must be a non-empty array");
  }
  if (!args.gate || !args.implementer || !args.planPath) {
    throw new Error("args.gate, args.implementer, and args.planPath are required");
  }

  const chainResults = await parallel(args.chains.map((c) => () => runChain(c, args)));
  const kept = chainResults.filter(Boolean);

  phase("Report");
  const flat = kept.flatMap((c) => c.results);
  const finalTally = tally(flat);
  log(`tally: accepted ${finalTally.accepted}, needs-decision ${finalTally.needsDecision}, escalated ${finalTally.escalated}, failed ${finalTally.failed}, deferred ${finalTally.deferred}`);
  return { chains: kept, tally: finalTally, spent: budget.spent() };
}

return main();
