// v2 of docs-page-chain.js (docs reset pass 1, Tasks 8 and 9): drafts through
// `cairn-docs-drafter` by default, tests each page against real reader jobs, and never runs a
// profile-grader agent. `docs-page-chain.js` is untouched and stays the chain the unmerged
// draft-docs pass B and C plans and the `register-check` skill depend on; nothing points at v2
// until a plan names it. Task 4's baseline record ruled which of the spec's pass 1 item 6 changes
// this file builds; everything else is deferred (`docs/internal/record/2026-09-23-docs-reset-baseline.md`).
//
// PROTOCOL: two stages, run as two separate Workflow invocations around the reader runner, which
// is not a Workflow step (it drives headless containers and needs a working directory this
// sandboxed script does not have).
//
//   Stage 1 (args.stage: 1). Per page: a drafter writes the page at its final path and runs the
//   page gate; a register editor reads it once, adversarially, carrying the profile, the omission
//   checklist, and a request for real reader jobs. Stage 1 never redrafts and never scores a
//   third-party profile grader (removed; the editor's own "Profile" section covers it). It ends by
//   dispatching one write to a JSON handoff file at `docs/internal/handoffs/<runId>.json` in the
//   worktree, holding every page's draft, editor findings and omissions, and proposed reader jobs,
//   and returns that file's path.
//
//   Outside the Workflow, the conductor runs `scripts/docs-readers/run.ts` in cairn-cms over the
//   handoff's jobs and writes each job's verified report under a results directory.
//
//   Stage 2 (args.stage: 2, args.handoffPath, args.resultsDir). Per page: a fresh read loads the
//   handoff and the verified reader reports; a redraft applies every finding the editor marked
//   (blocking or advisory) and every reader-verified defect, unless the conductor struck one; the
//   page gate runs again; a fresh applied-findings read grades the redraft against the prior
//   findings (applied, not applied, applied wrongly) and flags any new text the redraft
//   introduced. A blocking finding marked anything but "applied" is unresolved. This is the only
//   redraft round: a page still unresolved after it escalates to the conductor and is never sent
//   to a third round.
//
// Invocation from the conductor session (copy this file to the session scratchpad first; the
// Workflow tool refuses a `~/.claude/workflows` scriptPath):
//
//   Workflow({
//     scriptPath: "<scratchpad>/docs-page-chain-v2.js",
//     args: {
//       stage: 1,
//       worktree: "/home/glw907/Projects/cairn-cms/.claude/worktrees/<name>",
//       gate: "npm run check:docs && npm run check:vale && ...",   // the docs gate string;
//                                                                   // v2 always adds check:provenance
//       gateLane: "light",                 // optional; "light" prefixes CAIRN_GATE_LANE=light
//       inFlight: 3,                       // optional; pages drafted at once, default 3
//       toolGate: "make -C <worktree>/tool check",   // optional; appended for a page with `pinned`
//       drafterType: "cairn-docs-drafter", // optional; defaults to cairn-docs-drafter in v2
//                                          // (v1 defaults to cairn-implementer)
//       profile: "<the track profile, printed verbatim>",
//       registerPaths: ["docs/internal/docs-register.md#..."],   // what every agent reads
//       valeErrorRules: "<the error-tier rule list, verbatim>",
//       drafterModel: "claude-opus-5-5",   // optional
//       reviewModel: "claude-opus-5-5",    // optional
//       runId: "<a stable id for this batch, e.g. the plan task id>",
//       pages: [
//         {
//           id: "is-it-working",
//           path: "docs/admin/is-it-working.md",
//           brief: "<the brief from the plan, verbatim>",
//           inputs: ["docs/superpowers/plans/<plan>.mining.md#is-it-working", "..."],
//           exemplar: "docs/admin/<page>.md",
//           pinned: ["#slug-one", "#slug-two"],   // optional; slugs the page must keep
//           extraChecks: ["<a sentence the applied-findings read must also verify>"]   // optional
//         }
//       ]
//     }
//   })
//
// Then, after the reader runner has written its results directory:
//
//   Workflow({
//     scriptPath: "<scratchpad>/docs-page-chain-v2.js",
//     args: {
//       stage: 2,
//       worktree: "...", gate: "...", profile: "...", registerPaths: [...], valeErrorRules: "...",
//       drafterType: "cairn-docs-drafter", drafterModel: "...", reviewModel: "...",
//       handoffPath: "<the path stage 1 returned>",
//       resultsDir: "<the reader runner's results directory>"
//     }
//   })
//
// Every agent starts with zero context. The runner renders each stage's prompt from args and
// the page record; nothing load-bearing may live only in the conductor's conversation.

export const meta = {
  name: "docs-page-chain-v2",
  description: "Drafts docs pages through cairn-docs-drafter, gate, and a register editor read; hands off to the reader runner; redrafts on the editor's findings and the verified reader reports, then checks what the redraft applied.",
  whenToUse: "A draft-docs pass plan names this workflow's v2 stages for its page tasks.",
  phases: [
    { title: "Draft", detail: "one drafter per page, page gate inside" },
    { title: "Read", detail: "register editor with the omission checklist and reader-job proposals" },
    { title: "Handoff", detail: "stage 1 writes the JSON handoff file for the reader runner" },
    { title: "Load", detail: "stage 2 loads the handoff and the verified reader reports" },
    { title: "Redraft", detail: "one round on the editor's findings and the reader reports" },
    { title: "Applied", detail: "a fresh read grades what the redraft actually applied" },
    { title: "Report", detail: "per-page records for the conductor" }
  ]
};

const DRAFT_SCHEMA = {
  type: "object",
  properties: {
    path: { type: "string" },
    gate: { type: "string", enum: ["pass", "fail", "not run"] },
    gateCommand: { type: "string" },
    gateTail: { type: "string" },
    bulletsFiled: { type: "array", items: { type: "string" } },
    frictionFiled: { type: "array", items: { type: "string" } },
    couldNotDo: { type: "array", items: { type: "string" } }
  },
  required: ["path", "gate", "gateCommand"]
};

const FINDING = {
  type: "object",
  properties: {
    location: { type: "string" },
    finding: { type: "string" },
    rewrite: { type: "string" },
    blocking: { type: "boolean" }
  },
  required: ["location", "finding", "blocking"]
};

const OMISSION_ITEM = {
  type: "object",
  properties: {
    item: { type: "string" },
    status: { type: "string", enum: ["present", "missing"] },
    evidence: { type: "string" }
  },
  required: ["item", "status"]
};

const READER_JOB = {
  type: "object",
  properties: {
    id: { type: "string" },
    task: { type: "string" },
    doneSignal: { type: "string" }
  },
  required: ["id", "task", "doneSignal"]
};

// The register editor's stage-1 read: the same ranked findings as v1, plus the omission
// checklist graded item by item, plus the reader jobs a real-reader batch should attempt.
const EDITOR_SCHEMA = {
  type: "object",
  properties: {
    verdict: { type: "string", enum: ["accept", "fix"] },
    findings: { type: "array", items: FINDING },
    omissions: { type: "array", items: OMISSION_ITEM },
    readerJobs: { type: "array", items: READER_JOB },
    summary: { type: "string" }
  },
  required: ["verdict", "findings", "omissions", "readerJobs", "summary"]
};

// The applied-findings read after a redraft: a verdict per prior finding, never a fresh grade.
const APPLIED_SCHEMA = {
  type: "object",
  properties: {
    perFinding: {
      type: "array",
      items: {
        type: "object",
        properties: {
          location: { type: "string" },
          finding: { type: "string" },
          blocking: { type: "boolean" },
          status: { type: "string", enum: ["applied", "not applied", "applied wrongly"] },
          evidence: { type: "string" }
        },
        required: ["location", "finding", "blocking", "status"]
      }
    },
    newIssues: { type: "array", items: FINDING },
    summary: { type: "string" }
  },
  required: ["perFinding", "newIssues", "summary"]
};

const PATH_RESULT = { type: "object", properties: { path: { type: "string" } }, required: ["path"] };

const HANDOFF_LOAD_SCHEMA = {
  type: "object",
  properties: { pages: { type: "array", items: { type: "object" } } },
  required: ["pages"]
};

const READER_RESULTS_SCHEMA = {
  type: "object",
  properties: {
    results: {
      type: "array",
      items: {
        type: "object",
        properties: {
          jobId: { type: "string" },
          pageId: { type: "string" },
          verified: { type: "boolean" },
          report: { type: "string" }
        },
        required: ["jobId", "pageId", "verified", "report"]
      }
    }
  },
  required: ["results"]
};

const a = args || {};
const WT = a.worktree;
const GATE = a.gate;
const LANE = a.gateLane === "light" ? "CAIRN_GATE_LANE=light " : "";
const IN_FLIGHT = Number.isInteger(a.inFlight) && a.inFlight > 0 ? a.inFlight : 3;
const DRAFTER = a.drafterModel || "claude-opus-5-5";
const DRAFTER_TYPE = a.drafterType || "cairn-docs-drafter";
const TOOL_GATE = a.toolGate || null;   // appended for a page carrying `pinned`, e.g. "make -C <wt>/tool check"
const REVIEWER = a.reviewModel || "claude-opus-5-5";
const STAGE = a.stage;

if (STAGE !== 1 && STAGE !== 2) {
  throw new Error("docs-page-chain-v2 needs args.stage, 1 or 2 (see the file header's PROTOCOL)");
}
if (!WT || !GATE || !a.profile) {
  throw new Error("docs-page-chain-v2 needs args.worktree, args.gate, and args.profile");
}

const OMISSION_CHECKLIST = `- Every prerequisite the reader needs before starting.
- Every value the reader must supply themselves (a name, a token, a path, a URL).
- Every failure a step on this page can produce, and its fix.
- The version and platform scope this page applies to.
- Where the reader goes next when finished.`;

const common = `Work only in the worktree ${WT}; run every command from there and never cd to another checkout.
The register is ${(a.registerPaths || ["docs/internal/docs-register.md"]).join(", ")}: read the universal
contract and the track section before anything else. The Names convention in that file's "Names"
section is enforced by Vale (Cairn.Names, Cairn.NamesRetired); use the sanctioned name for every
part. The track profile, verbatim:

${a.profile}

Error-tier Vale rules, verbatim:

${a.valeErrorRules || "(run `npm run check:vale` and fix every error-tier finding)"}
`;

// v2's page gate always adds `check:provenance` (validates the drafter's sentence-to-fact brief),
// on top of the caller's own gate string and, when the page is `pinned`, the tool gate.
const gateFor = (p) => {
  const parts = [GATE, "npm run check:provenance"];
  if (p.pinned && p.pinned.length && TOOL_GATE) parts.push(TOOL_GATE);
  return parts.join(" && ");
};
const gateLine = (p) => `Run the docs gate through the gate runner, exactly:
  ${LANE}cairn-run-gate '${gateFor(p)}'
On exit 75, re-issue the same command until it prints \`gate exit:\`; never poll a log. Report
the exact command and the last twenty lines. A gate that is red on a rule the plan says a later
task closes (for example check:arm-indexes before the index task) is reported as "fail" with the
failing rule named, and is not a reason to edit an index page this task does not own.`;

function briefPathFor(p) {
  return `docs/internal/briefs/${p.track || "<track>"}/${p.id}.json`;
}

function draftPrompt(p, round, redraftInputs) {
  const head = round === 1
    ? `Draft the page ${p.path} at its final path, from the brief and the inputs below and nothing else.`
    : `Redraft ${p.path} once, applying every finding below, blocking or advisory, unless it is
marked struck. Do not widen the page.`;
  return `${head}

${common}
The brief, verbatim:

${p.brief}

Inputs (read each in full; the manifests and bullets are the only source of a command, a
transcript, a JSON example, or a fact; never compose one and never open the old page or a
tool/docs/ original):
${(p.inputs || []).map((i) => `- ${i}`).join("\n")}

Exemplar to imitate for anatomy and register: ${p.exemplar || "(none named; follow the register's anatomy)"}
${p.pinned && p.pinned.length ? `Pinned heading slugs this page must keep, verbatim: ${p.pinned.join(", ")}` : ""}
${round > 1 ? `\nFindings to apply, from the register editor and from real readers who attempted this page (apply every one, blocking or advisory, unless the conductor struck it):\n${redraftInputs}\n` : ""}
A fact the page needs that no input records is filed as a [candidate] bullet against code on
main in the facts container (name it in bulletsFiled); something no source can supply goes to
docs/internal/docs-friction-log.md (name it in frictionFiled). Commit nothing; leave the tree
with your edits in place.

${gateLine(p)}

Return the structured report only.`;
}

function editorPrompt(p) {
  return `Adversarial register edit of ${p.path} in ${WT}. Read the page, then the register's
universal contract and its track section, then grade. Your report MUST carry a section titled
"Profile" grading the page against this profile, one line per element:

${a.profile}

Also apply the tell catalogue, the Names section, logic, and facts-adjacent phrasing. Return
ranked findings with a proposed rewrite each, and a verdict: "fix" if any finding is blocking.

Also run this omission checklist against the page and report each item as present or missing,
with the evidence (a quoted line, or what is absent), as \`omissions\`:
${OMISSION_CHECKLIST}

Also propose one to three real reader jobs a reader-runner batch should attempt against this
page, as \`readerJobs\`: a task phrased the way this profile's audience would phrase it, using
only what the page itself tells them, with a stated done signal a script can check.`;
}

function appliedFindingsPrompt(p, priorFindings) {
  return `Fresh read of the redraft of ${p.path} in ${WT}. You were not the agent that wrote it
and were not shown these findings until now. For each prior finding below, read the current page
and report whether the redraft applied it, did not apply it, or applied it wrongly (made the
change but left the underlying problem, or introduced a new error while trying), with the
evidence:

${priorFindings}

Also flag any new text the redraft introduced beyond what these findings called for, as
\`newIssues\`, each with a \`blocking\` flag. A blocking finding that comes back anything but
"applied" is unresolved; this is the only redraft this page gets.`;
}

function findingsBlock(name, findings) {
  return findings.map((f) => `- [${f.blocking ? "BLOCKING" : "advisory"}] (${name}) ${f.location}: ${f.finding}${f.rewrite ? `\n  rewrite: ${f.rewrite}` : ""}`).join("\n");
}

// ---------------------------------------------------------------------------------------------
// Stage 1: draft, gate, one editor read. Ends with the handoff write.
// ---------------------------------------------------------------------------------------------

async function draftAndRead(p) {
  const record = { id: p.id, path: p.path, briefPath: briefPathFor(p) };
  const d1 = await agent(draftPrompt(p, 1), { label: `draft:${p.id}`, phase: "Draft", schema: DRAFT_SCHEMA, model: DRAFTER, agentType: DRAFTER_TYPE });
  if (!d1) return { ...record, status: "escalate", reason: "drafter returned nothing" };
  record.draft = d1;
  const editor = await agent(editorPrompt(p), { label: `editor:${p.id}`, phase: "Read", schema: EDITOR_SCHEMA, model: REVIEWER, agentType: "cairn-register-editor" });
  if (!editor) return { ...record, status: "escalate", reason: "editor read returned nothing" };
  record.editor = editor;
  record.status = "handed-off";
  return record;
}

async function stage1() {
  if (!PAGES.length) throw new Error("docs-page-chain-v2 stage 1 needs args.pages");
  phase("Draft");
  const queue = PAGES.slice();
  const records = [];
  async function worker(n) {
    while (queue.length) {
      const p = queue.shift();
      log(`worker ${n}: ${p.id}`);
      try {
        records.push(await draftAndRead(p));
      } catch (e) {
        records.push({ id: p.id, path: p.path, status: "escalate", reason: String(e && e.message || e) });
      }
    }
  }
  await parallel(Array.from({ length: Math.min(IN_FLIGHT, PAGES.length) }, (_, i) => () => worker(i + 1)));

  const handoff = {
    runId: a.runId || null,
    pages: records.map((r) => ({
      id: r.id,
      path: r.path,
      briefPath: r.briefPath,
      status: r.status,
      draft: r.draft || null,
      editorFindings: r.editor ? r.editor.findings : [],
      omissions: r.editor ? r.editor.omissions : [],
      readerJobs: r.editor ? r.editor.readerJobs.map((j) => ({ ...j, id: `${r.id}:${j.id}` })) : []
    }))
  };
  const handoffPath = `docs/internal/handoffs/${a.runId || "docs-page-chain"}.json`;
  phase("Handoff");
  const written = await agent(
    `Write the file ${handoffPath} in ${WT} with exactly this JSON content, creating any parent
directories that do not exist yet. Overwrite the file if it exists. Do not reformat or reorder
the content.

${JSON.stringify(handoff, null, 2)}

Return only the path you wrote.`,
    { label: "handoff-write", phase: "Handoff", schema: PATH_RESULT, agentType: "general-purpose" }
  );
  if (!written) throw new Error("docs-page-chain-v2 stage 1: the handoff write returned nothing");

  const jobs = handoff.pages.flatMap((p) => p.readerJobs);
  return {
    handoffPath: written.path,
    pages: records.map((r) => ({ id: r.id, path: r.path, status: r.status })),
    readerJobCount: jobs.length
  };
}

// ---------------------------------------------------------------------------------------------
// Stage 2: load the handoff and the verified reader reports, redraft, then check what applied.
// ---------------------------------------------------------------------------------------------

async function loadHandoff(handoffPath) {
  return agent(
    `Read the JSON file ${handoffPath} in ${WT} and return its \`pages\` array exactly as
written, with no summarizing or reformatting.`,
    { label: "load-handoff", phase: "Load", schema: HANDOFF_LOAD_SCHEMA, agentType: "general-purpose" }
  );
}

async function loadReaderResults(resultsDir) {
  return agent(
    `Read every job result file under ${resultsDir} in ${WT}. Each holds a job id, the page id it
targeted, whether the record writer verified it, and its report text. Return one entry per file
as \`results\`; a file you cannot parse is reported with \`verified: false\` and the parse error
as its report.`,
    { label: "load-reader-results", phase: "Load", schema: READER_RESULTS_SCHEMA, agentType: "general-purpose" }
  );
}

async function redraftPage(page, readerResults) {
  const record = { id: page.id, path: page.path, briefPath: page.briefPath };
  if (page.status !== "handed-off") {
    return { ...record, status: "escalate", reason: `stage 1 status was "${page.status}", not handed off` };
  }
  const editorFindings = page.editorFindings || [];
  const missingOmissions = (page.omissions || []).filter((o) => o.status === "missing");
  const verifiedReports = readerResults.filter((r) => r.pageId === page.id && r.verified);
  const unverified = readerResults.filter((r) => r.pageId === page.id && !r.verified).length;

  const priorFindings = [
    findingsBlock("register editor", editorFindings),
    missingOmissions.length
      ? findingsBlock("omission checklist", missingOmissions.map((o) => ({ location: o.item, finding: o.evidence || "missing", blocking: true, rewrite: undefined })))
      : "",
    verifiedReports.length
      ? verifiedReports.map((r) => `- [BLOCKING] (reader ${r.jobId}) ${r.report}`).join("\n")
      : ""
  ].filter(Boolean).join("\n");

  if (!editorFindings.length && !missingOmissions.length && !verifiedReports.length) {
    record.status = "accepted";
    record.note = unverified ? `${unverified} unverified reader run(s) excluded from evidence` : undefined;
    return record;
  }

  // The page brief supplies the page's own inputs for a redraft; the drafter re-reads what it
  // already wrote plus the findings, so only the findings block and the page path are needed here.
  const p = { id: page.id, path: page.path, brief: page.draft && page.draft.brief, inputs: page.draft && page.draft.inputs, exemplar: page.draft && page.draft.exemplar, pinned: page.draft && page.draft.pinned };
  const d2 = await agent(draftPrompt(p, 2, priorFindings), { label: `redraft:${page.id}`, phase: "Redraft", schema: DRAFT_SCHEMA, model: DRAFTER, agentType: DRAFTER_TYPE });
  if (!d2) return { ...record, status: "escalate", reason: "redrafter returned nothing" };
  record.draft = d2;

  const flatPrior = [
    ...editorFindings.map((f) => ({ ...f })),
    ...missingOmissions.map((o) => ({ location: o.item, finding: `omission checklist: ${o.item}`, blocking: true }))
  ];
  const priorText = flatPrior.map((f) => `- [${f.blocking ? "BLOCKING" : "advisory"}] ${f.location}: ${f.finding}`).join("\n") +
    (verifiedReports.length ? `\n${verifiedReports.map((r) => `- [BLOCKING] (reader ${r.jobId}) ${r.report}`).join("\n")}` : "");

  const applied = await agent(appliedFindingsPrompt(p, priorText), { label: `applied:${page.id}`, phase: "Applied", schema: APPLIED_SCHEMA, model: REVIEWER, agentType: "cairn-register-editor" });
  if (!applied) return { ...record, status: "escalate", reason: "applied-findings read returned nothing" };
  record.applied = applied;

  const unresolved = applied.perFinding.filter((f) => f.blocking && f.status !== "applied");
  const newBlocking = (applied.newIssues || []).filter((f) => f.blocking);
  // Two-round cap: this is the one redraft this page gets, so anything still unresolved here
  // escalates to the conductor rather than triggering a third round.
  if (unresolved.length || newBlocking.length || d2.gate !== "pass") {
    return {
      ...record,
      status: "escalate",
      reason: "unresolved blocking finding, new blocking text, or a red gate after the one redraft round",
      unresolved,
      newBlocking
    };
  }
  record.status = "accepted";
  record.note = unverified ? `${unverified} unverified reader run(s) excluded from evidence` : undefined;
  return record;
}

async function stage2() {
  if (!a.handoffPath) throw new Error("docs-page-chain-v2 stage 2 needs args.handoffPath");
  if (!a.resultsDir) throw new Error("docs-page-chain-v2 stage 2 needs args.resultsDir");
  phase("Load");
  const [loaded, reader] = await parallel([
    () => loadHandoff(a.handoffPath),
    () => loadReaderResults(a.resultsDir)
  ]);
  if (!loaded) throw new Error("docs-page-chain-v2 stage 2: the handoff load returned nothing");
  if (!reader) throw new Error("docs-page-chain-v2 stage 2: the reader-results load returned nothing");

  phase("Redraft");
  const results = await parallel(loaded.pages.map((page) => () => redraftPage(page, reader.results)));

  phase("Report");
  const accepted = results.filter((r) => r && r.status === "accepted").length;
  log(`${accepted}/${results.length} pages accepted; ${results.length - accepted} escalated`);
  return {
    pages: results,
    accepted,
    escalated: results.filter((r) => r && r.status !== "accepted").map((r) => r.id)
  };
}

const PAGES = a.pages || [];

if (STAGE === 1) {
  return await stage1();
}
return await stage2();
