// Overnight orchestrator: chassis-B2 (from the post-Task-2 CI regen) through polish-11a,
// polish-11b, and, when args.c.approved is true, polish-C and the release cut. All three
// polish plans are authored, reviewed, and read by Geoff BEFORE launch; this script only
// executes them. Without C approval it stops after 11b with STATUS pointing at Geoff's read. Every conductor action is an
// agent step; the conductor never reads a diff. Each pass chain runs through the chains
// script (nested one level). Halts write STATUS with the exact resume state and return.
//
// args: {
//   date: "2026-09-08",                       // stamp for records (scripts cannot read the clock)
//   repo: "/var/home/glw907/Projects/cairn-cms",
//   chainsScript: "<path to pass-execute-chains.js>",
//   b2:  { worktree, branch, pr, plan, run2Args, cache, ceilingM, spentSoFarM },
//   a11: { worktree, branch, plan, run1Args, run2Args, cache, ceilingM },
//   b11: { worktree, branch, plan, runs: [chainArgs...], regenAfterRuns: [..], reviewers, verifierSurfaces, cache, ceilingM },
//   c:   { approved: bool, worktree, branch, plan, runs, regenAfterRuns, reviewers, verifierSurfaces, cache, ceilingM }
// }

export const meta = {
  name: "cairn-overnight-to-release",
  description: "B2, 11a, 11b executed on their reviewed plans and merged; then C and the release cut if approved, else stop for Geoff's read",
  phases: [
    { title: "B2 execute", detail: "CI regen, Tasks 3 to 8 chain" },
    { title: "B2 close", detail: "simplifier, gates, verifier, reviewers, records, merge" },
    { title: "11a execute", detail: "worktree, run one, CI regen, run two" },
    { title: "11a close", detail: "simplifier, gates, reviewers, records, merge" },
    { title: "11b execute", detail: "worktree, runs with CI regens between" },
    { title: "11b close", detail: "simplifier, gates, verifier, reviewers, records, merge" },
    { title: "C execute", detail: "worktree, runs with CI regens between (only if approved)" },
    { title: "C close", detail: "simplifier, gates, reviewers, records, merge" },
    { title: "Release", detail: "the cut through cairn-release" }
  ]
};

const a = args;
const M = 1_000_000;

// ---------- schemas ----------
const REPORT = {
  type: "object",
  properties: {
    ok: { type: "boolean" },
    summary: { type: "string" },
    commits: { type: "array", items: { type: "string" } },
    details: { type: "string" },
    blockers: { type: "array", items: { type: "string" } }
  },
  required: ["ok", "summary", "commits", "details", "blockers"]
};

const VERDICT = {
  type: "object",
  properties: {
    pass: { type: "boolean" },
    summary: { type: "string" },
    structural: { type: "array", items: { type: "string" } },
    cosmetic: { type: "array", items: { type: "string" } },
    report: { type: "string" }
  },
  required: ["pass", "summary", "structural", "cosmetic", "report"]
};

const REVIEW = {
  type: "object",
  properties: {
    blocking: { type: "array", items: { type: "object", properties: { location: { type: "string" }, finding: { type: "string" }, fix: { type: "string" } }, required: ["location", "finding", "fix"] } },
    nonBlocking: { type: "array", items: { type: "object", properties: { location: { type: "string" }, finding: { type: "string" } }, required: ["location", "finding"] } },
    summary: { type: "string" }
  },
  required: ["blocking", "nonBlocking", "summary"]
};

// ---------- helpers ----------
const RULES = [
  "Skip agent-memory maintenance for this dispatch.",
  "Work only in the named worktree; never touch the main checkout except where this step says so, and never touch these untracked files in the main checkout: docs/extend/assets/, docs/internal/site-figures.*, scripts/figures/, docs/internal/record/2026-09-04-cairn-case/25-front-door-proposal.md, or the uncommitted diffs to package.json and .github/workflows/test.yml.",
  "No em dashes in any comment, doc, or commit message. Commits: imperative mood, specific files, footer `Co-Authored-By: Claude <noreply@anthropic.com>`.",
  "Poll a background command with `sleep 30` between checks, never repeated no-op commands. Run the showcase e2e alone; nothing else binds port 4173 while it runs.",
  "Return raw facts; your final output is data for a conductor, not a message for a person."
].join("\n");

function allAccepted(chainResult) {
  const results = (chainResult && chainResult.chains || []).flatMap(c => c.results || []);
  return results.length > 0 && results.every(r => r.status === "accepted");
}
function chainSummary(chainResult) {
  const results = (chainResult && chainResult.chains || []).flatMap(c => c.results || []);
  return results.map(r => `task ${r.id} (${r.title}): ${r.status}, fixRounds ${r.fixRounds}`).join("; ");
}

async function halt(stage, why, resume) {
  log(`HALT at ${stage}: ${why}`);
  await agent([
    `Repo (main checkout): ${a.repo}. Edit docs/STATUS.md on main and commit it (only that file).`,
    `The overnight run halted at stage "${stage}" on ${a.date}. Reason: ${why}`,
    `PREPEND one paragraph to the "Immediate next action" section (keep every existing bullet of that section intact): state the halt, the stage, the reason, and this resume prompt verbatim: ${resume}`,
    `Keep STATUS present tense and under 60 lines; move nothing else. Commit message: "docs(status): overnight run halted at ${stage}".`,
    RULES
  ].join("\n"), { label: `halt:${stage}`, model: "sonnet", effort: "medium" });
  return { halted: stage, why, resume, spent: budget.spent() };
}

// A conductor CI regen: dispatch e2e.yml with update_snapshots on the branch, wait, pull into the worktree, report the diff.
async function ciRegen(p, label) {
  return agent([
    `Worktree: ${p.worktree} (branch ${p.branch}). Push the branch first (git push). Then dispatch the baseline regen: \`gh workflow run e2e.yml --ref ${p.branch} -f update_snapshots=true\`.`,
    `Find the run with \`gh run list --workflow e2e.yml --branch ${p.branch} -L 3\` (the newest workflow_dispatch), then \`gh run watch <id> --exit-status\`. If it fails, report ok=false with the failing step's last 40 log lines (\`gh run view <id> --log-failed | tail -40\`).`,
    `On success: \`git pull --ff-only\` in the worktree, then report which baseline PNGs the regen commit changed (\`git show --stat HEAD\`), and the surfaces they belong to. ok=true only if the pull was a clean fast-forward and the changed set is listed.`,
    RULES
  ].join("\n"), { label, model: "sonnet", effort: "medium", schema: REPORT });
}

// The pass-end ritual shared by every pass; the verifier stage is optional.
async function closePass(p, opts) {
  const phaseName = opts.phase;
  const spentAtStart = budget.spent();

  // 1. simplifier
  const simp = await agent([
    `Worktree: ${p.worktree} (branch ${p.branch}), plan ${p.plan}. Run over the code changed in this pass (\`git diff main...HEAD --stat\` names it). Preserve behavior. Commit refinements in one commit if any; report the SHA or "no change".`,
    RULES
  ].join("\n"), { label: `${opts.tag}:simplify`, phase: phaseName, agentType: "code-simplifier:code-simplifier", schema: REPORT });
  if (simp && !simp.ok) log(`${opts.tag}: simplifier reported a problem: ${simp.summary}`);

  // 2. the full gate plus the CI-only six plus the from-scratch consumer build
  const gate = await agent([
    `Worktree: ${p.worktree} (branch ${p.branch}), plan ${p.plan}. Run the pass gate exactly as the plan's Gate section states, then BY NAME: npm run check:comments, check:reference:signatures, check:surface, check:snippets, check:transcripts, check:symbols, check:package, check:reference, check:docs, check:idioms, check:cm-internals, check:rulings-format; then the from-scratch consumer build: rm -rf examples/showcase/{node_modules,package-lock.json}, npm --prefix examples/showcase install, npm --prefix examples/showcase run build, and CI=1 npm --prefix examples/showcase run test:e2e; then a fresh scaffold from templates/waymark through the create-site.yml bake command into a temp dir with install, format:check, test:unit, build. Run sequentially (npm test and check:custom-surface both repackage dist).`,
    `BASELINE RULE: the visual baselines are CI-canonical. If the branch carries a CI regen commit (a github-actions commit titled "chore(e2e): regenerate ..."), the local e2e may fail on exactly the baselines that commit rewrote because this workstation renders them differently; that set, and only that set, is not a red: name the regen commit, paste the failing snapshot names, confirm they equal the commit's file list, and treat the e2e as green. Never regenerate those files locally.`,
    `If anything else is red: fix it ONLY if the fix is a mechanical consequence of this pass's own changes (a stale snippet, a missed rename, a comment gate); commit the fix and rerun that gate. If a red gate needs a design decision, report ok=false with the exact failing output (last 40 lines) and do not guess.`,
    `Report ok=true only with every named gate green and its final line quoted in details.`,
    RULES
  ].join("\n"), { label: `${opts.tag}:gate`, phase: phaseName, agentType: "cairn-implementer", schema: REPORT });
  if (!gate || !gate.ok) return { ok: false, stage: `${opts.tag}:gate`, why: gate ? gate.summary : "gate agent returned nothing" };

  // 3. pass-end CI regen and pull (baselines are CI-canonical)
  const regen = await ciRegen(p, `${opts.tag}:ci-regen-end`);
  if (!regen || !regen.ok) return { ok: false, stage: `${opts.tag}:ci-regen-end`, why: regen ? regen.summary : "regen agent returned nothing" };

  // 4. verifier (bounded loop: verify, fix, fresh verify; a second FAIL halts)
  if (opts.verifierSurfaces && opts.verifierSurfaces.length) {
    for (let round = 0; round < 2; round++) {
      const cap = (round === 0 && p.captureAfterDone) ? { ok: true, summary: "after set already captured (args flag)" } : await agent([
        `Worktree: ${p.worktree} (branch ${p.branch}, pulled head). Capture the pass after set with the capture tool (examples/showcase/scripts/capture-surfaces.mjs, read its usage) into ${p.cache}/pass/after${round ? "-round" + (round + 1) : ""}/ for surfaces: ${opts.verifierSurfaces.join(", ")}; both schemes, the five widths (320, 390, 768, 1440, 2560). The directory is write-once; report a collision instead of overwriting. Nothing else may bind port 4173.`,
        `Report ok=true with the directory path and the tile count per surface.`,
        RULES
      ].join("\n"), { label: `${opts.tag}:capture-after${round ? round + 1 : ""}`, phase: phaseName, model: "sonnet", effort: "medium", schema: REPORT });
      if (!cap || !cap.ok) return { ok: false, stage: `${opts.tag}:capture-after`, why: cap ? cap.summary : "capture agent returned nothing" };

      const verdict = await agent([
        `Fresh-context visual verification of pass ${opts.tag} (plan ${p.plan}). Inputs: BEFORE tiles at ${p.cache}/pass/before/tiles/, AFTER tiles at ${p.cache}/pass/after${round ? "-round" + (round + 1) : ""}/tiles/, and the committed intended-moves manifest ${a.repo}/docs/internal/record/2026-09-04-chassis-inputs/chassis-b-intended-moves.md (its section for this pass names every intended move by surface, width, scheme, and what moves).`,
        `ADAPTED VOCABULARY for this dispatch: per surface and width, one of INTENDED-AND-CORRECT / INTENDED-BUT-WRONG / UNINTENDED (STRUCTURAL or COSMETIC) / UNCHANGED, and for every surface new to the matrix (${opts.newSurfaces || "none"}) also COMPOSED | UNBROKEN-ONLY | BROKEN, where UNBROKEN-ONLY is a FAIL for a new surface. Surfaces: ${opts.verifierSurfaces.join(", ")}; both schemes; widths 320, 390, 768, 1440, 2560. Read tiles, never full-page files. The contrast probe is MANDATORY on every surface with interactive elements (run it against the built showcase in ${p.worktree}/examples/showcase with Playwright from its node_modules if the tiles cannot settle it).`,
        `pass=true only when no INTENDED-BUT-WRONG, no UNINTENDED STRUCTURAL, and every new surface is COMPOSED. List every STRUCTURAL finding with surface, width, scheme, and tile path; list COSMETIC findings separately. Put the full per-surface table in report.`
      ].join("\n"), { label: `${opts.tag}:verify${round ? round + 1 : ""}`, phase: phaseName, agentType: "visual-verifier", schema: VERDICT });
      if (!verdict) return { ok: false, stage: `${opts.tag}:verify`, why: "verifier returned nothing" };
      if (verdict.pass) { log(`${opts.tag}: verifier PASS`); break; }
      if (round === 1) return { ok: false, stage: `${opts.tag}:verify`, why: `second verifier FAIL: ${verdict.summary}` };
      log(`${opts.tag}: verifier FAIL round 1, dispatching one fix`);
      const fix = await agent([
        `Worktree: ${p.worktree} (branch ${p.branch}), plan ${p.plan}. The pass-end visual verifier FAILED with these STRUCTURAL findings; fix exactly these, following the plan's paint protocol (before/after capture per touched surface, INTENDED MOVES, MOVED BASELINES produced by the unmodified suites, regeneration by file path, the intended-moves manifest row in the same commit), then run the plan's full gate, then commit.`,
        ...verdict.structural.map(s => `- ${s}`),
        `Report ok=true with the commit SHA and the MOVED BASELINES list.`,
        RULES
      ].join("\n"), { label: `${opts.tag}:verify-fix`, phase: phaseName, agentType: "cairn-implementer", schema: REPORT });
      if (!fix || !fix.ok) return { ok: false, stage: `${opts.tag}:verify-fix`, why: fix ? fix.summary : "fix agent returned nothing" };
      const regen2 = await ciRegen(p, `${opts.tag}:ci-regen-fix`);
      if (!regen2 || !regen2.ok) return { ok: false, stage: `${opts.tag}:ci-regen-fix`, why: regen2 ? regen2.summary : "regen returned nothing" };
    }
  }

  // 5. reviewer fan-out, then one fix round on blocking findings
  const reviews = await parallel((opts.reviewers || []).map(r => () => agent([
    `Worktree: ${p.worktree} (branch ${p.branch}), plan ${p.plan}. Review the whole pass diff (\`git diff main...HEAD\`) in your specialty against the plan's acceptance criteria and the repo's conventions. Report blocking findings (a defect, a regression, a security or a11y fault) with file:line and the fix, and non-blocking ones separately. Do not edit files.`
  ].join("\n"), { label: `${opts.tag}:review:${r}`, phase: phaseName, agentType: r, schema: REVIEW })));
  const blocking = reviews.filter(Boolean).flatMap(r => r.blocking);
  if (blocking.length) {
    log(`${opts.tag}: ${blocking.length} blocking review findings, one fix round`);
    const fix = await agent([
      `Worktree: ${p.worktree} (branch ${p.branch}), plan ${p.plan}. The pass-end reviewers returned these blocking findings. Fix exactly these (fix commits on top, no history rewrite), run the plan's full gate, commit. A finding you judge wrong: do not fix it, explain in details with evidence.`,
      ...blocking.map(b => `- ${b.location}: ${b.finding}. Fix: ${b.fix}`),
      RULES
    ].join("\n"), { label: `${opts.tag}:review-fix`, phase: phaseName, agentType: "cairn-implementer", schema: REPORT });
    if (!fix || !fix.ok) return { ok: false, stage: `${opts.tag}:review-fix`, why: fix ? fix.summary : "fix agent returned nothing" };
  }

  // 6. records: post-mortem, HISTORY, STATUS wording, budgets; then push, CI, merge
  const spentM = ((budget.spent() - spentAtStart) / M).toFixed(2);
  const records = await agent([
    `Worktree: ${p.worktree} (branch ${p.branch}), plan ${p.plan}, date ${a.date}. Close the pass's records per the cairn-pass ritual: append the post-mortem to the plan file (what was built, what was verified with evidence, decisions locked, what the gate caught, both budgets: tokens against the ceiling of ${p.ceilingM}M with the close-out spend of about ${spentM}M added to the execution spend the chain reported, and attended time as two counts: planning misses and execution sittings, both 0 unless the run halted); add this pass's entry to docs/HISTORY.md (newest first: what landed, what the gate caught, what a later pass would be wrong to rediscover); make sure CHANGELOG.md's Unreleased entry and docs/extend/migration-notes.md carry this pass per the plan; ROADMAP items this pass shipped leave the tiers; the reviewer verdicts and the verifier verdict are recorded in the post-mortem. Do NOT edit docs/STATUS.md here. Run check:docs, check:vale, check:rulings-format. Commit.`,
    RULES
  ].join("\n"), { label: `${opts.tag}:records`, phase: phaseName, model: "sonnet", effort: "high", schema: REPORT });
  if (!records || !records.ok) return { ok: false, stage: `${opts.tag}:records`, why: records ? records.summary : "records agent returned nothing" };

  const merge = await agent([
    `Worktree: ${p.worktree} (branch ${p.branch}). FIRST bring the branch up to date: git fetch origin; if origin/main has commits the branch lacks, git merge origin/main (a merge commit, never a rebase or force). Resolve conflicts by these rules: docs/STATUS.md takes origin/main's version whole (conductor-owned); docs/HISTORY.md keeps both sides with this pass's entry first and no duplicates; CHANGELOG.md keeps both sides' bullets under Unreleased; any other conflicting file is resolved by keeping both sides' intent and re-running the gate that covers it, and if that needs a design decision report ok=false naming the file. Run npm run check:docs after any resolution. Commit the merge and push. ${p.pr ? `The PR is #${p.pr}.` : `Open a PR to main (title from the plan's title; body: the pass summary, the verifier verdict if any, the reviewer verdicts, and the footer "🤖 Generated with [Claude Code](https://claude.com/claude-code)").`} Wait for CI: \`gh pr checks <n> --watch --fail-fast\`. If a check fails, report ok=false with the failing job's last 40 log lines and do not merge.`,
    `On green: merge with a merge commit (\`gh pr merge <n> --merge --delete-branch=false\`), then in the main checkout ${a.repo} run \`git pull --ff-only\` and report the merge SHA. Then edit docs/STATUS.md on main: the pass is MERGED (one line, present tense, pointing at HISTORY), the immediate next action names the next stage of the overnight run; commit STATUS only.`,
    RULES
  ].join("\n"), { label: `${opts.tag}:merge`, phase: phaseName, model: "sonnet", effort: "medium", schema: REPORT });
  if (!merge || !merge.ok) return { ok: false, stage: `${opts.tag}:merge`, why: merge ? merge.summary : "merge agent returned nothing" };
  return { ok: true, merge: merge.summary, commits: merge.commits };
}

async function makeWorktree(p, label) {
  return agent([
    `Main checkout: ${a.repo}. Create the pass worktree: \`git -C ${a.repo} pull --ff-only\`, then \`git worktree add ${p.worktree} -b ${p.branch} main\`. In it, from-scratch showcase install: \`rm -rf examples/showcase/node_modules examples/showcase/package-lock.json\` is NOT wanted (the lockfile is committed); do \`rm -rf examples/showcase/node_modules && npm --prefix examples/showcase install\`, then verify both symlinks point INTO THIS worktree: \`readlink -f examples/showcase/node_modules/@glw907/cairn-cms\` and \`.../cairn-cms-dev\` must resolve under ${p.worktree}. Root install: \`npm ci\`. Then \`npm run package\` once and \`npm run check\` to prove the worktree builds. Report ok=true with the readlink outputs.`,
    RULES
  ].join("\n"), { label, model: "sonnet", effort: "medium", schema: REPORT });
}

async function runChain(chainArgs, label, phaseName) {
  log(`${label}: launching chain with ${chainArgs.chains[0].tasks.length} task(s)`);
  const result = await workflow({ scriptPath: a.chainsScript }, chainArgs);
  log(`${label}: ${chainSummary(result)}`);
  return result;
}

async function ceilingCheck(tag, spentAtStart, ceilingM) {
  const used = (budget.spent() - spentAtStart) / M;
  if (used > ceilingM) { log(`${tag}: ceiling ${ceilingM}M exceeded (${used.toFixed(2)}M)`); return false; }
  return true;
}

// A stage-launchable run: each launch carries only the passes it runs; a missing pass is skipped
// and, when the next pass is absent too, the run stops with STATUS naming the next launch.
async function stopWith(doneStage, nextLaunch) {
  await agent([
    `Main checkout ${a.repo}. Edit docs/STATUS.md on main and commit only it. The overnight run (${a.date}) completed ${doneStage} (MERGED; HISTORY carries it). Immediate next action: ${nextLaunch}. Record the spend ${(budget.spent() / M).toFixed(2)}M. Present tense, under 60 lines.`,
    RULES
  ].join("\n"), { label: "final-status", model: "sonnet", effort: "medium" });
  return { done: doneStage, spent: budget.spent() };
}

// ---------- B2 ----------
const b2 = a.b2;
let b2Spent = budget.spent();
if (b2) {
phase("B2 execute");
{
  const regen = b2.skipInitialRegen ? { ok: true, summary: "skipped by args" } : await ciRegen(b2, "b2:ci-regen-task2");
  if (!regen || !regen.ok) return halt("b2:ci-regen-task2", regen ? regen.summary : "regen returned nothing", `Resume chassis-B2 at the post-Task-2 CI regen (plan ${b2.plan}); then Tasks 3 to 8 as one chain run from ${b2.cache}/b2-args.json filtered to tasks 3 to 8.`);
  const run2 = await runChain(b2.run2Args, "b2:run2", "B2 execute");
  if (!allAccepted(run2)) return halt("b2:run2", chainSummary(run2), `Read the B2 chain journal, decide the non-accepted task, then resume the remaining B2 tasks as one chain run; then the pass-end ritual.`);
}
phase("B2 close");
{
  const closed = await closePass(b2, { tag: "b2", phase: "B2 close", reviewers: ["svelte-reviewer", "web-auth-security-reviewer", "cloudflare-workers-reviewer"], verifierSurfaces: ["home", "article", "styleguide", "error404", "signups", "archive2"], newSurfaces: "archive2" });
  if (!closed.ok) return halt(closed.stage, closed.why, `Resume chassis-B2's pass-end ritual at step "${closed.stage}" in ${b2.worktree}; the earlier steps are committed on the branch.`);
  log(`B2 merged: ${closed.merge}; B2 spend this run ${((budget.spent() - b2Spent) / M).toFixed(2)}M`);
}
}

// ---------- 11a ----------
const a11 = a.a11;
const a11Spent = budget.spent();
if (!a11) return stopWith("chassis-B2", "launch the overnight orchestrator again with the polish-11a args (run one and run two from ~/.cache/cairn-polish-11a/), plus 11b's and C's if their reviewed plans are committed and, for C, Geoff has approved its names");
phase("11a execute");
{
  const wt = await makeWorktree(a11, "11a:worktree");
  if (!wt || !wt.ok) return halt("11a:worktree", wt ? wt.summary : "worktree agent returned nothing", `Create the polish-11a worktree off main with a from-scratch showcase install, then run ${a11.cache}/11a-run1-args.json as a chain.`);
  const run1 = await runChain(a11.run1Args, "11a:run1", "11a execute");
  if (!allAccepted(run1)) return halt("11a:run1", chainSummary(run1), `Read the 11a run-one journal, decide the non-accepted task, then resume the remaining run-one tasks; then the CI regen; then run two.`);
  if (!(await ceilingCheck("11a", a11Spent, a11.ceilingM))) return halt("11a:ceiling", "ceiling exceeded after run one", `Resume polish-11a at the post-Task-7 CI regen, then run two from ${a11.cache}/11a-run2-args.json.`);
  const regen = await ciRegen(a11, "11a:ci-regen-task7");
  if (!regen || !regen.ok) return halt("11a:ci-regen-task7", regen ? regen.summary : "regen returned nothing", `Resume polish-11a at the post-Task-7 CI regen, then run two from ${a11.cache}/11a-run2-args.json.`);
  const run2 = await runChain(a11.run2Args, "11a:run2", "11a execute");
  if (!allAccepted(run2)) return halt("11a:run2", chainSummary(run2), `Read the 11a run-two journal, decide the non-accepted task, then resume the remaining tasks; then the pass-end ritual.`);
}
phase("11a close");
{
  const closed = await closePass(a11, { tag: "11a", phase: "11a close", reviewers: ["cloudflare-workers-reviewer", "web-auth-security-reviewer", "svelte-reviewer"], verifierSurfaces: [] });
  if (!closed.ok) return halt(closed.stage, closed.why, `Resume polish-11a's pass-end ritual at step "${closed.stage}" in ${a11.worktree}.`);
  log(`11a merged: ${closed.merge}; 11a spend ${((budget.spent() - a11Spent) / M).toFixed(2)}M`);
}

// ---------- generic pass executor for a pre-planned pass ----------
async function executePass(p, tag, phaseExec, phaseClose) {
  phase(phaseExec);
  const spentAt = budget.spent();
  const wt = await makeWorktree(p, `${tag}:worktree`);
  if (!wt || !wt.ok) return halt(`${tag}:worktree`, wt ? wt.summary : "worktree agent returned nothing", `Create the ${p.branch} worktree off main with a from-scratch showcase install, then run ${p.cache}/run1-args.json as a chain per ${p.plan}.`);
  for (let i = 0; i < p.runs.length; i++) {
    const r = await runChain(p.runs[i], `${tag}:run${i + 1}`, phaseExec);
    if (!allAccepted(r)) return halt(`${tag}:run${i + 1}`, chainSummary(r), `Read the ${tag} run-${i + 1} journal, decide the non-accepted task, then resume the remaining tasks per ${p.plan}.`);
    if (!(await ceilingCheck(tag, spentAt, p.ceilingM))) return halt(`${tag}:ceiling`, `ceiling exceeded after run ${i + 1}`, `Resume ${tag} after run ${i + 1} per ${p.plan}.`);
    if ((p.regenAfterRuns || []).includes(i + 1)) {
      const regen = await ciRegen(p, `${tag}:ci-regen-run${i + 1}`);
      if (!regen || !regen.ok) return halt(`${tag}:ci-regen-run${i + 1}`, regen ? regen.summary : "regen returned nothing", `Resume ${tag} at the CI regen after run ${i + 1}, then run ${i + 2} per ${p.plan}.`);
    }
  }
  phase(phaseClose);
  const closed = await closePass(p, { tag, phase: phaseClose, reviewers: p.reviewers || [], verifierSurfaces: p.verifierSurfaces || [], newSurfaces: "none" });
  if (!closed.ok) return halt(closed.stage, closed.why, `Resume ${tag}'s pass-end ritual at step "${closed.stage}" in ${p.worktree}.`);
  log(`${tag} merged: ${closed.merge}; spend ${((budget.spent() - spentAt) / M).toFixed(2)}M`);
  return null;
}

// ---------- 11b (only if its reviewed plan was passed in) ----------
if (!a.b11) {
  await agent([
    `Main checkout ${a.repo}. Edit docs/STATUS.md on main and commit only it. The overnight run (${a.date}) completed chassis-B2 and polish-11a (both MERGED; HISTORY carries each). Immediate next action: launch the next overnight run with the polish-11b args (and polish-C's if Geoff has approved its names) from their caches under ~/.cache/. Record the spend ${(budget.spent() / M).toFixed(2)}M. Present tense, under 60 lines.`,
    RULES
  ].join("\n"), { label: "final-status", model: "sonnet", effort: "medium" });
  return { done: "through-11a", spent: budget.spent() };
}
{
  const h = await executePass(a.b11, "11b", "11b execute", "11b close");
  if (h) return h;
}

// ---------- C and the cut, only if Geoff approved C's names ----------
if (!a.c || !a.c.approved) {
  await agent([
    `Main checkout ${a.repo}. Edit docs/STATUS.md on main and commit only it. The overnight run (${a.date}) completed: chassis-B2, polish-11a, and polish-11b are MERGED (HISTORY carries each). Immediate next action: Geoff reads the polish-C plan ${a.c ? a.c.plan : "(not yet passed in)"} (its "Verb-first names for Geoff's read" section); on approval, the next run executes polish-C from ${a.c ? a.c.cache : "~/.cache/cairn-polish-c"}/ and cuts the release through cairn-release automatically (Geoff's ruling ${a.date}). Record the overnight spend ${(budget.spent() / M).toFixed(2)}M. Present tense, under 60 lines.`,
    RULES
  ].join("\n"), { label: "final-status", model: "sonnet", effort: "medium" });
  return { done: "through-11b", spent: budget.spent() };
}
{
  const h = await executePass(a.c, "c", "C execute", "C close");
  if (h) return h;
}

phase("Release");
const cut = await agent([
  `Main checkout ${a.repo}, date ${a.date}. Cut the cairn-cms release through the cairn-release skill's procedure (read ~/.claude/skills/cairn-release/SKILL.md in full and follow it exactly). Geoff's ruling (${a.date}): cut automatically once polish-C lands. Steps: confirm main is the merged head and clean; run the release gate the skill names, sequentially; list published versions with npm view and pick the first free number, sizing the bump by the skill's rule against the actual Unreleased window (state the derivation); npm version <x.y.z> --no-git-tag-version; finalize CHANGELOG (Unreleased to the number, the release-size marker if minor); compose the notes file from the whole window since the last published tag carrying every Consumers must: line; commit and fast-forward push to main; gh release create v<x.y.z> --target main with the notes; watch publish.yml to green; verify npm view @glw907/cairn-cms version and the -dev package. Then edit docs/STATUS.md: published version, the four consumer sites' upgrade named as the next action with the Consumers must: list pointer; commit.`,
  `If any step fails, stop, do not retry the publish, and report ok=false with the exact output.`,
  RULES
].join("\n"), { label: "release:cut", phase: "Release", model: "opus", effort: "high", schema: REPORT });
if (!cut || !cut.ok) return halt("release:cut", cut ? cut.summary : "release agent returned nothing", `Resume the release cut through cairn-release from the step that failed; main is merged and green.`);
return { done: "released", release: cut.summary, spent: budget.spent() };
