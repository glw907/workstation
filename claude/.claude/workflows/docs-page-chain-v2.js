// v2 of docs-page-chain.js (docs reset pass 1, Tasks 8 and 9): drafts through
// `cairn-docs-drafter` by default, tests each page against real reader jobs, and never runs a
// profile-grader agent. `docs-page-chain.js` is untouched and stays the chain the unmerged
// draft-docs pass B and C plans and the `register-check` skill depend on; nothing points at v2
// until a plan names it. Task 4's baseline record ruled which of the spec's pass 1 item 6 changes
// this file builds; everything else is deferred (`docs/internal/record/2026-09-23-docs-reset-baseline.md`).
// Only the profile grader is removed from v1's three-way stage-1 read; the fact read stays (it is
// the stage that caught pass A's P1, a sentence the drafter composed by joining neighboring
// manifest entries, which no register or reader-job read would have caught on its own).
//
// PROTOCOL: two stages, run as two separate Workflow invocations around the reader runner, which
// is not a Workflow step (it drives headless containers and needs a working directory this
// sandboxed script does not have).
//
//   Stage 1 (args.stage: 1). Per page: a drafter writes the page at its final path; a register
//   editor and a fact read run together (as v1 runs them), each with zero context; then the page
//   gate of record runs. The editor carries the profile, the omission checklist, the page's
//   extraChecks, and a request for one to three real reader jobs, each with its reader class (it
//   is the only stage-1 read left to originate them). The fact read traces every claim on the
//   page to an input and flags a claim, command, or transcript with no source behind it, as v1's
//   does. Stage 1 never redrafts and never scores a third-party profile grader (removed; the
//   editor's own "Profile" section covers profile grading). It ends by dispatching one write of a
//   single JSON handoff file, one per batch, and returns that file's path.
//
//   NO SELF-VERIFIED FACTS. The drafter and the redraft file a fact the page needs only as a
//   `[candidate]` bullet in the facts container and never retag any bullet. The independent fact
//   read (stage 1) and the applied-findings read (stage 2, for the bullets the redraft filed)
//   trace each candidate filed this run against its cited code and, where the code supports it
//   exactly, retag it `[verified]` with a code Source (`path:line` or a `src/` `path#Symbol`,
//   followed by a quoted anchor, per the site repo's docs/internal/facts/README.md), or leave it
//   `[candidate]` with a reason. Both reads report what they retagged and what they left. Before
//   editing, each compares the tag of every fact the page's brief cites against HEAD and flags,
//   as blocking, any change no read reported (this read's own retags come after the check; stage
//   2 also accepts the handoff's `factRetagged`), restoring the HEAD tag. A retag of a bullet the
//   page does not cite cannot help its provenance, so no cross-page attribution is needed. The
//   page gate (with `check:provenance`) runs only after those retags, never inside the drafter, so
//   the drafter is never tempted to clear a provenance failure by grading its own citations. The
//   gate runs `check:provenance -- <the page's own brief>`, never the all-briefs form, so a page
//   is not failed by another in-flight page's brief. Pages in flight at once can edit the same
//   facts file; each read edits only the bullets it names.
//
//   Each handoff page carries the page args verbatim (id, path, track, brief, inputs, exemplars,
//   pinned, extraChecks), the gate-of-record result (gate, gateCommand, gateTail), the bullets
//   the drafter filed and the fact read's retag report, one flat `findings` list, the editor's
//   omissions, the proposed reader jobs, and an empty `struckReaderFindings` list. Every finding
//   carries a stable id stage 1 assigns: `gate` (a gate of record that was not "pass", with its
//   tail), `ed-<n>` (register editor), `fact-<n>` (fact read), `om-<n>` (an omission-checklist
//   item reported missing, always blocking).
//
//   The handoff never lands in the site repository's docs tree (a page task must not carry an
//   untracked file into `docs/`): it is written to
//   `$XDG_CACHE_HOME/docs-page-chain/handoffs/<runId>-<UTC stamp>.json`, or
//   `~/.cache/docs-page-chain/handoffs/<runId>-<UTC stamp>.json` when `XDG_CACHE_HOME` is unset,
//   resolved by the write agent's own shell at write time (the script itself has no environment,
//   clock, or filesystem access). The stamp (`date -u +%Y%m%d-%H%M%S`) means two batches never
//   overwrite each other; stage 1 returns the exact path the write agent used.
//
//   STRIKING A FINDING. Between the stages the conductor may edit the handoff file: set
//   `"struck": true` on any finding in a page's `findings` to drop it, or add a reader-defect id
//   (below) to that page's `struckReaderFindings`. Stage 2 filters every struck finding out of
//   the redraft and the applied-findings read. The `gate` finding cannot be struck: a red gate is
//   always grounds for the redraft, and the redraft's own gate must pass. A reader stall the
//   job's class cannot avoid (a docs-only reader told to run a command it has no shell for) is a
//   harness defect, not a page defect: the conductor strikes it through `struckReaderFindings`,
//   and fixes the entry's class for the next batch.
//
//   THE READER STAGE (the conductor, outside the Workflow). Build one runner batch from the
//   handoff and run it in cairn-cms:
//     { "name": "<the handoff file's basename without .json>", "concurrency": 4,
//       "budgetTokens": <the plan's reader budget>,
//       "jobs": [ one per readerJobs entry of every handed-off page:
//         { "id": "<the readerJobs id, already `<pageId>--<n>`>",
//           "class": "<the readerJobs entry's class: docs-only, docs-and-binary, docs-and-site,
//                     or repository>",
//           "model": "claude-opus-5-5",
//           "arrival": "<the readerJobs entry's arrival>",
//           "job": "<its task> You're done once <its doneSignal>. Quote the exact lines you relied
//                   on, with their file path and line number, the way your Read tool shows them.",
//           "docsSet": ["<the page's path>", "<each page it links that the job needs>"],
//           "timeoutMinutes": 30 } ] }
//     npx tsx scripts/docs-readers/run.ts <batch.json> --out <absolute results dir>
//   and, after a verification-logic fix, `npx tsx scripts/docs-readers/reverify.ts <batch.json>
//   <results dir>`. Job ids MUST keep the `<pageId>--<n>` form: stage 2 assigns a job to a page
//   by the `<pageId>--` prefix. (The runner's id pattern is `^[a-z0-9][a-z0-9-]*$`, so a colon
//   separator is not available; page ids must therefore not themselves contain `--`.) If the
//   conductor sends no reader jobs for a page, stage 2 still runs on its stage-1 findings.
//
//   Stage 2 (args.stage: 2, args.handoffPath, args.resultsDir). args.resultsDir is the absolute
//   path of the runner's `--out` directory (default `~/.cache/docs-readers/results/<batch>-<run>`);
//   there is no default here, and stage 2 refuses to run without it. A fresh read loads the
//   handoff; another loads `report.reverified.json` from the results dir when present, else
//   `report.json` (a BatchReport). Only jobs whose `verified.ok` is true count as evidence. A
//   verified job yields a blocking reader defect for each way it fell short: `rd-<jobId>-outcome`
//   when its outcome is not "done", `rd-<jobId>-stall-<k>` per stall, `rd-<jobId>-assumed-<k>`
//   per assumption; a clean done job yields nothing. Per page, a redraft applies every
//   unstruck finding (blocking or advisory) and every unstruck reader defect, with the stage-1
//   gate tail when that gate was red; a fresh applied-findings read grades the redraft against
//   those findings by id (applied, not applied, applied wrongly), checks the extraChecks again,
//   traces the candidates the redraft filed, and flags any new text the redraft introduced
//   (a retag by the redraft included); then the page gate of record runs again. The page
//   escalates unless every blocking finding and every reader defect comes back with a matching
//   perFinding entry marked "applied", no new blocking text appears, and the redraft's gate
//   passes. The blocking flags are the script's own, never the ones the read echoes back. This
//   is the only redraft round: a page still unresolved after it escalates to the conductor and
//   is never sent to a third round.
//
// Other decisions carried from the first build of this file: the register editor, not a separate
// agent, proposes the reader jobs (nothing else is left in stage 1 to originate them); one
// handoff file covers the whole batch, not one per page; every filesystem read or write the
// script itself cannot do (workflow scripts carry no Node.js or filesystem API) is done by a
// `general-purpose` agent dispatch, never assumed.
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
//       profile: "<the track profile's full text, verbatim, never a path>",
//       registerPaths: ["docs/internal/docs-register.md#..."],   // what every agent reads
//       valeErrorRules: "<the error-tier rule list, verbatim>",
//       drafterModel: "claude-opus-5-5",   // optional
//       reviewModel: "claude-opus-5-5",    // optional
//       gateModel: "sonnet", gateEffort: "low",   // optional; the gate-of-record agent
//       runId: "<optional prefix, e.g. the plan task id; lowercased to [a-z0-9-]>",
//       pages: [
//         {
//           id: "is-it-working",           // a slug with no `--` (reader job ids build on it)
//           path: "docs/admin/is-it-working.md",
//           track: "admin",                // admin | editors | extend | reference | front-door;
//                                          // names the brief file docs/internal/briefs/<track>/<id>.json
//           brief: "<the brief from the plan, verbatim>",
//           inputs: ["docs/superpowers/plans/<plan>.mining.md#is-it-working", "..."],
//           exemplars: [ { path: "docs/admin/<page>.md", text: "<that page's full text>" } ],
//                                          // two or three; each reaches the drafter inside <example> tags
//           pinned: ["#slug-one", "#slug-two"],   // optional; slugs the page must keep
//           extraChecks: ["<a sentence the editor and the applied-findings read must verify>"]   // optional
//         }
//       ]
//     }
//   })
//
// Then, after the reader runner has written its results directory (and after any strikes):
//
//   Workflow({
//     scriptPath: "<scratchpad>/docs-page-chain-v2.js",
//     args: {
//       stage: 2,
//       worktree: "...", gate: "...", profile: "...", registerPaths: [...], valeErrorRules: "...",
//       drafterType: "cairn-docs-drafter", drafterModel: "...", reviewModel: "...",
//       handoffPath: "<the path stage 1 returned>",
//       resultsDir: "<absolute path of the runner's --out directory>"
//     }
//   })
//
// Every agent starts with zero context. The runner renders each stage's prompt from args and
// the page record; nothing load-bearing may live only in the conductor's conversation.

export const meta = {
  name: "docs-page-chain-v2",
  description: "Drafts docs pages through cairn-docs-drafter, gate, a register editor read, and a fact read; hands off to the reader runner; redrafts on the editor's and fact read's findings plus the verified reader reports, then checks what the redraft applied.",
  whenToUse: "A draft-docs pass plan names this workflow's v2 stages for its page tasks.",
  phases: [
    { title: "Draft", detail: "one drafter per page; new facts filed only as candidates" },
    { title: "Read", detail: "register editor (omission checklist, classed reader-job proposals) and fact read (traces and retags candidates), in parallel" },
    { title: "Gate", detail: "the page gate of record, after the retags" },
    { title: "Handoff", detail: "stage 1 writes the JSON handoff file (cache path) for the reader runner" },
    { title: "Load", detail: "stage 2 loads the handoff and the verified reader reports" },
    { title: "Redraft", detail: "one round on the editor's and fact read's findings, a red stage-1 gate, and the verified reader reports" },
    { title: "Applied", detail: "a fresh read grades what the redraft actually applied" },
    { title: "Report", detail: "per-page records for the conductor" }
  ]
};

// The drafter's report. It runs no page gate (the gate of record runs after the independent
// retags), so it reports the facts it filed as candidates instead.
const DRAFT_SCHEMA = {
  type: "object",
  properties: {
    path: { type: "string" },
    bulletsFiled: { type: "array", items: { type: "string" } },
    frictionFiled: { type: "array", items: { type: "string" } },
    couldNotDo: { type: "array", items: { type: "string" } }
  },
  required: ["path", "bulletsFiled"]
};

// The page gate of record.
const GATE_SCHEMA = {
  type: "object",
  properties: {
    gate: { type: "string", enum: ["pass", "fail", "not run"] },
    gateCommand: { type: "string" },
    gateTail: { type: "string" }
  },
  required: ["gate", "gateCommand", "gateTail"]
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
    class: { type: "string", enum: ["docs-only", "docs-and-binary", "docs-and-site", "repository"] },
    arrival: { type: "string" },
    task: { type: "string" },
    doneSignal: { type: "string" }
  },
  required: ["id", "class", "arrival", "task", "doneSignal"]
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

// A candidate bullet a read retagged [verified], and one it left [candidate].
const RETAGGED = {
  type: "object",
  properties: { id: { type: "string" }, source: { type: "string" } },
  required: ["id", "source"]
};
const LEFT_CANDIDATE = {
  type: "object",
  properties: { id: { type: "string" }, reason: { type: "string" } },
  required: ["id", "reason"]
};

// The fact read's stage-1 verdict: v1's, plus the retag report on the candidates filed this run.
const READ_SCHEMA = {
  type: "object",
  properties: {
    verdict: { type: "string", enum: ["accept", "fix"] },
    findings: { type: "array", items: FINDING },
    retagged: { type: "array", items: RETAGGED },
    leftCandidate: { type: "array", items: LEFT_CANDIDATE },
    summary: { type: "string" }
  },
  required: ["verdict", "findings", "retagged", "leftCandidate", "summary"]
};

// The applied-findings read after a redraft: a verdict per prior finding, keyed by the finding's
// stable id, never a fresh grade.
const APPLIED_SCHEMA = {
  type: "object",
  properties: {
    perFinding: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          status: { type: "string", enum: ["applied", "not applied", "applied wrongly"] },
          evidence: { type: "string" }
        },
        required: ["id", "status", "evidence"]
      }
    },
    newIssues: { type: "array", items: FINDING },
    retagged: { type: "array", items: RETAGGED },
    leftCandidate: { type: "array", items: LEFT_CANDIDATE },
    summary: { type: "string" }
  },
  required: ["perFinding", "newIssues", "retagged", "leftCandidate", "summary"]
};

const PATH_RESULT = { type: "object", properties: { path: { type: "string" } }, required: ["path"] };

const STRINGS = { type: "array", items: { type: "string" } };

// A handoff finding. Every field is always present (empty string when unused), so the handoff
// load can require all of them and an agent cannot quietly drop one.
const HANDOFF_FINDING = {
  type: "object",
  additionalProperties: false,
  properties: {
    id: { type: "string" },
    source: { type: "string" },
    location: { type: "string" },
    finding: { type: "string" },
    rewrite: { type: "string" },
    tail: { type: "string" },
    blocking: { type: "boolean" },
    struck: { type: "boolean" }
  },
  required: ["id", "source", "location", "finding", "rewrite", "tail", "blocking", "struck"]
};

const HANDOFF_PAGE = {
  type: "object",
  additionalProperties: false,
  properties: {
    id: { type: "string" },
    path: { type: "string" },
    track: { type: "string" },
    briefPath: { type: "string" },
    status: { type: "string", enum: ["handed-off", "escalate"] },
    reason: { type: "string" },
    brief: { type: "string" },
    inputs: STRINGS,
    exemplars: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: { path: { type: "string" }, text: { type: "string" } },
        required: ["path", "text"]
      }
    },
    pinned: STRINGS,
    extraChecks: STRINGS,
    gate: { type: "string", enum: ["pass", "fail", "not run"] },
    gateCommand: { type: "string" },
    gateTail: { type: "string" },
    bulletsFiled: STRINGS,
    factRetagged: { type: "array", items: { ...RETAGGED, additionalProperties: false } },
    factLeftCandidate: { type: "array", items: { ...LEFT_CANDIDATE, additionalProperties: false } },
    findings: { type: "array", items: HANDOFF_FINDING },
    omissions: { type: "array", items: OMISSION_ITEM },
    readerJobs: { type: "array", items: READER_JOB },
    struckReaderFindings: STRINGS
  },
  required: [
    "id", "path", "track", "briefPath", "status", "reason", "brief", "inputs", "exemplars",
    "pinned", "extraChecks", "gate", "gateCommand", "gateTail", "bulletsFiled", "factRetagged",
    "factLeftCandidate", "findings", "omissions",
    "readerJobs", "struckReaderFindings"
  ]
};

const HANDOFF_LOAD_SCHEMA = {
  type: "object",
  properties: { pages: { type: "array", items: HANDOFF_PAGE } },
  required: ["pages"]
};

// The reader runner's report, cut to what stage 2 uses. One entry per `jobs[]` element of the
// BatchReport (`scripts/docs-readers/lib/types.ts`), copied, never judged by the loading agent.
const READER_RESULTS_SCHEMA = {
  type: "object",
  properties: {
    source: { type: "string", enum: ["report.reverified.json", "report.json", "missing"] },
    jobs: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          outcome: { type: "string", enum: ["done", "stalled", "refused", "aborted", "error"] },
          abortReason: { type: "string" },
          stalls: STRINGS,
          assumed: STRINGS,
          verifiedOk: { type: "boolean" },
          verifiedProblems: STRINGS
        },
        required: ["id", "outcome", "stalls", "assumed", "verifiedOk", "verifiedProblems"]
      }
    }
  },
  required: ["source", "jobs"]
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
const GATE_MODEL = a.gateModel || "sonnet";
const GATE_EFFORT = a.gateEffort || "low";
const STAGE = a.stage;
const PAGES = a.pages || [];
const RUN_ID = String(a.runId || "").toLowerCase().replace(/[^a-z0-9-]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "") || "docs-page-chain";

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
// It names the page's own brief: several pages are drafted at once, and the bare all-briefs form
// would fail page A on page B's in-flight brief.
const gateFor = (p) => {
  const parts = [GATE, `npm run check:provenance -- ${briefPathFor(p)}`];
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

function bulletList(items) {
  return (items || []).map((i) => `- ${i}`).join("\n");
}

function exemplarBlock(p) {
  const ex = p.exemplars || [];
  if (!ex.length) return "(no exemplar supplied; say so in couldNotDo and follow the register's anatomy)";
  return ex.map((e) => `<example path="${e.path}">\n${e.text}\n</example>`).join("\n\n");
}

function extraChecksBlock(p, lead) {
  const checks = p.extraChecks || [];
  return checks.length ? `\n${lead}\n${bulletList(checks)}\n` : "";
}

function draftPrompt(p, round, redraftInputs) {
  const head = round === 1
    ? `Draft the page ${p.path} at its final path, from the brief and the inputs below and nothing else.`
    : `Redraft ${p.path} once, applying every finding below, blocking or advisory. The conductor has
already removed any finding it struck. Do not widen the page.`;
  return `${head}

${common}
The page's track is ${p.track || "(not given; take it from the brief)"}; write its sentence-to-fact
brief to ${briefPathFor(p)}.

The brief, verbatim:

${p.brief}

Inputs (read each in full; the manifests and bullets are the only source of a command, a
transcript, a JSON example, or a fact; never compose one and never open the old page or a
tool/docs/ original):
${bulletList(p.inputs)}

Exemplars to imitate for anatomy and register:

${exemplarBlock(p)}
${p.pinned && p.pinned.length ? `\nPinned heading slugs this page must keep, verbatim: ${p.pinned.join(", ")}\n` : ""}
${round > 1 ? `\nFindings to apply, from the page gate, the register editor, the fact read, the omission checklist, and real readers who attempted this page (apply every one, blocking or advisory):\n${redraftInputs}\n` : ""}
${FILE_CANDIDATES_RULE}
Something no source can supply goes to docs/internal/docs-friction-log.md (name it in
frictionFiled). Commit nothing; leave the tree with your edits in place.

Do not run the page gate or check:provenance: the gate of record runs after an independent fact
read has traced your candidates, and a provenance failure on a candidate you cited is expected
until then. You may run \`npm run check:facts\` and \`npm run check:vale\` to check your own work.

Return the structured report only.`;
}

const FILE_CANDIDATES_RULE = `A fact the page needs that no input records is filed as a new bullet
against code on main in the facts container, tagged \`[candidate: ...]\` and nothing else, with the
code Source you believe supports it; name each in bulletsFiled as "<facts file> <its f: id>". Never
change the tag of any bullet, one you filed or one already there: an independent read traces your
candidates and retags the ones the code supports. You may cite your own candidates in the brief.`;

// Which runner class a reader job needs (scripts/docs-readers/classes/).
const READER_CLASS_RULE = `Give each job the reader class its task needs, as \`class\`: "docs-only" when
the reader only reads and answers (no shell, no files); "docs-and-binary" when it runs read-only
cairn CLI operator commands (cairn doctor, cairn auth check) against a scratch site;
"docs-and-site" when it installs, edits, or builds a scaffolded site with its npm scripts;
"repository" when it works in the cairn-cms source tree itself.`;

// The independent trace of this run's candidates, and the self-retag check over every fact the
// page's brief cites. Only a read may retag; `legit` lists the retags earlier reads reported.
function retagRule(p, filed, who, legit, flagAs) {
  return `First, before you edit anything, check for self-retags. Read the page's brief,
${briefPathFor(p)}, and collect every fact id its sentences cite (skip "no-claim"). For each,
find its bullet under docs/internal/facts/ and compare its tag at HEAD (\`git show
HEAD:<facts file>\`) with its current tag. These retags were reported by an earlier read and are
legitimate:
${bulletList(legit.length ? legit : ["(none)"])}
Any other tag change was made by the drafting chain (${who} or an earlier draft), which must
never retag: report each as ${flagAs} naming the bullet, and restore its HEAD tag (a bullet
that is new since HEAD goes back to [candidate: ...]).

Then trace the candidates ${who} filed this run:
${bulletList(filed.length ? filed : ["(none)"])}
For each one, trace the claim against the code its Source cites. Where the code supports it
exactly, retag it [verified] in place with a code Source, per docs/internal/facts/README.md:
path:line or path:line-line (or a src/ path#Symbol declaration), followed by a quoted anchor, a
code span in parentheses copied verbatim from those lines. Report it in \`retagged\` with that
Source. Otherwise leave it [candidate: <what was and was not checked>] and report it in
\`leftCandidate\` with the reason. Edit no bullet beyond these and the restores above.`;
}

function editorPrompt(p) {
  return `Adversarial register edit of ${p.path} in ${WT}. Read the page, then the register's
universal contract and its track section, then grade. Your report MUST carry a section titled
"Profile" grading the page against this profile, one line per element:

${a.profile}
${extraChecksBlock(p, "Also verify each of these, as further profile elements; a failed one is a blocking finding with the location and what would pass:")}
Also apply the tell catalogue, the Names section, logic, and facts-adjacent phrasing. Return
ranked findings with a proposed rewrite each, and a verdict: "fix" if any finding is blocking.

Also run this omission checklist against the page and report each item as present or missing,
with the evidence (a quoted line, or what is absent), as \`omissions\`:
${OMISSION_CHECKLIST}

Also propose one to three real reader jobs a reader-runner batch should attempt against this
page, as \`readerJobs\`: an arrival (one or two second-person sentences on the situation the
reader arrives in), a task phrased the way this profile's audience would phrase it, using only
what the page itself tells them, and a stated done signal a script can check.
${READER_CLASS_RULE}`;
}

function factPrompt(p, filed) {
  return `Fact read of ${p.path} in ${WT}. Trace every claim on the page (each step, command,
transcript, figure, warning, success signal, and prose assertion) to one of these sources:
${bulletList(p.inputs)}
A claim with no bullet or ratified disposition behind it is a blocking finding (location, claim,
what the source lacks). A bullet or skeleton step in the sources that the page dropped is a
blocking finding naming the bullet. A command or example that differs from its manifest entry by
one character is blocking. A sentence composed by joining two neighboring manifest entries into
one claim neither entry states on its own is blocking. A bullet the drafter filed this run
counts as a source only once you have traced it below. Verdict "fix" if any blocking finding
exists; otherwise "accept" with the count of claims traced.

${retagRule(p, filed, "the drafter", [], "a blocking finding")}`;
}

function appliedFindingsPrompt(p, priorFindings, filed, legit) {
  return `Fresh read of the redraft of ${p.path} in ${WT}. You were not the agent that wrote it
and were not shown these findings until now. For EVERY prior finding below, one \`perFinding\`
entry carrying the finding's id exactly as shown in the first brackets: read the current page and
report whether the redraft applied it, did not apply it, or applied it wrongly (made the change
but left the underlying problem, or introduced a new error while trying), with the evidence. An
id you leave out is treated as not applied.

${priorFindings || "(no prior finding; only the stage-1 gate was red)"}
${extraChecksBlock(p, "Also verify each of these still holds on the redraft; a failed one goes in `newIssues` as blocking:")}
Also flag any new text the redraft introduced beyond what these findings called for, as
\`newIssues\`, each with a \`blocking\` flag. This is the only redraft this page gets.

${retagRule(p, filed, "the redraft", legit, "a blocking \`newIssues\` entry")}`;
}

function gatePrompt(p) {
  return `Run the page gate of record for ${p.path} in ${WT}, from that worktree. Edit nothing.
${gateLine(p)}
Return gate "pass" or "fail", the exact command, and the last twenty lines as gateTail.`;
}

async function runGate(p, label) {
  return agent(gatePrompt(p), { label, phase: "Gate", schema: GATE_SCHEMA, model: GATE_MODEL, effort: GATE_EFFORT, agentType: "general-purpose" });
}

function findingLine(f) {
  return `- [${f.id}] [${f.blocking ? "BLOCKING" : "advisory"}] (${f.source}) ${f.location}: ${f.finding}` +
    (f.rewrite ? `\n  rewrite: ${f.rewrite}` : "") +
    (f.tail ? `\n  gate tail:\n${f.tail.split("\n").map((l) => `    ${l}`).join("\n")}` : "");
}

function handoffFinding(id, source, f) {
  return {
    id,
    source,
    location: f.location || "",
    finding: f.finding || "",
    rewrite: f.rewrite || "",
    tail: f.tail || "",
    blocking: !!f.blocking,
    struck: false
  };
}

// ---------------------------------------------------------------------------------------------
// Stage 1: draft, gate, the register editor read and the fact read. Ends with the handoff write.
// ---------------------------------------------------------------------------------------------

async function draftAndRead(p) {
  const record = { id: p.id, path: p.path };
  const d1 = await agent(draftPrompt(p, 1), { label: `draft:${p.id}`, phase: "Draft", schema: DRAFT_SCHEMA, model: DRAFTER, agentType: DRAFTER_TYPE });
  if (!d1) return { ...record, status: "escalate", reason: "drafter returned nothing" };
  record.draft = d1;
  // The register editor and the fact read run together, as v1 runs them, each on Opus with zero
  // context; only the profile grader is gone.
  const [editor, fact] = await parallel([
    () => agent(editorPrompt(p), { label: `editor:${p.id}`, phase: "Read", schema: EDITOR_SCHEMA, model: REVIEWER, agentType: "cairn-register-editor" }),
    () => agent(factPrompt(p, d1.bulletsFiled || []), { label: `fact:${p.id}`, phase: "Read", schema: READ_SCHEMA, model: REVIEWER, agentType: "general-purpose" })
  ]);
  if (!editor) return { ...record, status: "escalate", reason: "editor read returned nothing" };
  if (!fact) return { ...record, status: "escalate", reason: "fact read returned nothing" };
  record.editor = editor;
  record.fact = fact;
  // The gate of record runs only after the fact read's retags have landed.
  const g = await runGate(p, `gate:${p.id}`);
  if (!g) return { ...record, status: "escalate", reason: "the gate run returned nothing" };
  record.gate = g;
  record.status = "handed-off";
  return record;
}

// One handoff page: the page args verbatim, so stage 2 rebuilds the page from them, plus the
// stage-1 results with a stable id on every finding.
function handoffPage(p, r) {
  const g = r.gate || null;
  const findings = [];
  if (g && g.gate !== "pass") {
    findings.push(handoffFinding("gate", "page gate", {
      location: g.gateCommand,
      finding: `the stage-1 page gate was "${g.gate}"`,
      tail: g.gateTail || "(no gate tail reported)",
      blocking: true
    }));
  }
  if (r.editor) r.editor.findings.forEach((f, i) => findings.push(handoffFinding(`ed-${i + 1}`, "register editor", f)));
  if (r.fact) r.fact.findings.forEach((f, i) => findings.push(handoffFinding(`fact-${i + 1}`, "fact read", f)));
  const omissions = r.editor ? r.editor.omissions : [];
  omissions.filter((o) => o.status === "missing").forEach((o, i) =>
    findings.push(handoffFinding(`om-${i + 1}`, "omission checklist", { location: o.item, finding: `missing: ${o.evidence || o.item}`, blocking: true })));
  return {
    id: p.id,
    path: p.path,
    track: p.track || "",
    briefPath: briefPathFor(p),
    status: r.status === "handed-off" ? "handed-off" : "escalate",
    reason: r.reason || "",
    brief: p.brief || "",
    inputs: p.inputs || [],
    exemplars: (p.exemplars || []).map((e) => ({ path: e.path, text: e.text })),
    pinned: p.pinned || [],
    extraChecks: p.extraChecks || [],
    gate: g ? g.gate : "not run",
    gateCommand: g ? g.gateCommand : "",
    gateTail: (g && g.gateTail) || "",
    bulletsFiled: (r.draft && r.draft.bulletsFiled) || [],
    factRetagged: r.fact ? r.fact.retagged.map((x) => ({ id: x.id, source: x.source })) : [],
    factLeftCandidate: r.fact ? r.fact.leftCandidate.map((x) => ({ id: x.id, reason: x.reason })) : [],
    findings,
    omissions,
    readerJobs: r.editor ? r.editor.readerJobs.map((j, i) => ({ id: `${p.id}--${i + 1}`, class: j.class, arrival: j.arrival, task: j.task, doneSignal: j.doneSignal })) : [],
    struckReaderFindings: []
  };
}

async function stage1() {
  if (!PAGES.length) throw new Error("docs-page-chain-v2 stage 1 needs args.pages");
  const bad = PAGES.filter((p) => !p.id || String(p.id).includes("--"));
  if (bad.length) throw new Error("docs-page-chain-v2: every page needs an id with no `--` (reader job ids are `<pageId>--<n>`)");
  phase("Draft");
  const queue = PAGES.slice();
  const records = new Map();
  async function worker(n) {
    while (queue.length) {
      const p = queue.shift();
      log(`worker ${n}: ${p.id}`);
      try {
        records.set(p.id, await draftAndRead(p));
      } catch (e) {
        records.set(p.id, { id: p.id, path: p.path, status: "escalate", reason: String(e && e.message || e) });
      }
    }
  }
  await parallel(Array.from({ length: Math.min(IN_FLIGHT, PAGES.length) }, (_, i) => () => worker(i + 1)));

  const handoff = {
    runId: RUN_ID,
    pages: PAGES.map((p) => handoffPage(p, records.get(p.id) || { status: "escalate", reason: "no stage-1 record" }))
  };
  phase("Handoff");
  const written = await agent(
    `Resolve the handoff path. Let STAMP be the output of \`date -u +%Y%m%d-%H%M%S\`. If the
environment variable XDG_CACHE_HOME is set and non-empty, use
"$XDG_CACHE_HOME/docs-page-chain/handoffs/${RUN_ID}-STAMP.json"; otherwise use
"$HOME/.cache/docs-page-chain/handoffs/${RUN_ID}-STAMP.json". If that file already exists, append
"-2", "-3", and so on before ".json" until the name is free; never overwrite a handoff. This path
is outside any git checkout, so run it from your own shell, never from inside ${WT}. Create any
parent directories that do not exist yet, then write that file with exactly the JSON between the
two marker lines below (the markers themselves excluded), never reformatting, reordering, or
summarizing the content. Write it with a quoted heredoc or a file-write tool so nothing in it is
shell-expanded, then confirm it parses with \`node -e\` or \`python3 -m json.tool\`.

BEGIN HANDOFF JSON
${JSON.stringify(handoff, null, 2)}
END HANDOFF JSON

Return only the absolute path you wrote.`,
    { label: "handoff-write", phase: "Handoff", schema: PATH_RESULT, agentType: "general-purpose" }
  );
  if (!written) throw new Error("docs-page-chain-v2 stage 1: the handoff write returned nothing");

  return {
    handoffPath: written.path,
    pages: handoff.pages.map((p) => ({ id: p.id, path: p.path, status: p.status, reason: p.reason || undefined, findings: p.findings.length, readerJobs: p.readerJobs.length })),
    readerJobCount: handoff.pages.reduce((n, p) => n + p.readerJobs.length, 0)
  };
}

// ---------------------------------------------------------------------------------------------
// Stage 2: load the handoff and the verified reader reports, redraft, then check what applied.
// ---------------------------------------------------------------------------------------------

async function loadHandoff(handoffPath) {
  return agent(
    `Read the JSON file at the absolute path ${handoffPath}. It is outside any git checkout (a
cache path, not part of the worktree), so read it from your own shell rather than assuming it
sits under a repository. Return its \`pages\` array exactly as written: every page with every
field, every string byte for byte (the brief, the exemplar texts, the gate tail, and every
finding included), no summarizing, trimming, or reformatting. A field the file lacks is an
error to report, never a value to invent.`,
    { label: "load-handoff", phase: "Load", schema: HANDOFF_LOAD_SCHEMA, agentType: "general-purpose" }
  );
}

async function loadReaderResults(resultsDir) {
  return agent(
    `The reader runner wrote its results to the absolute directory ${resultsDir}, outside any git
checkout; read it from your own shell. If ${resultsDir}/report.reverified.json exists, read that
file; otherwise read ${resultsDir}/report.json. If neither exists, return source "missing" and
no jobs. The file is one JSON object whose \`jobs\` array holds one job report each. For every
element of \`jobs\`, in order, return: \`id\`, \`outcome\`, \`abortReason\` (when present), \`stalls\`,
\`assumed\`, \`verified.ok\` as \`verifiedOk\`, and \`verified.problems\` as \`verifiedProblems\`,
every value copied verbatim. Do not judge, filter, merge, or summarize any job. Return which file
you read as \`source\`.`,
    { label: "load-reader-results", phase: "Load", schema: READER_RESULTS_SCHEMA, agentType: "general-purpose" }
  );
}

// A verified job's blocking reader defects: one per way it fell short. A clean done job (outcome
// "done", no stalls, no assumptions) yields none.
function readerDefects(job) {
  const src = `reader ${job.id}`;
  const out = [];
  if (job.outcome !== "done") {
    out.push(handoffFinding(`rd-${job.id}-outcome`, src, {
      location: "reader outcome",
      finding: `the reader's job ended "${job.outcome}"${job.abortReason ? ` (${job.abortReason})` : ""}`,
      blocking: true
    }));
  }
  (job.stalls || []).forEach((s, i) => out.push(handoffFinding(`rd-${job.id}-stall-${i + 1}`, src, { location: "reader stall", finding: s, blocking: true })));
  (job.assumed || []).forEach((s, i) => out.push(handoffFinding(`rd-${job.id}-assumed-${i + 1}`, src, { location: "reader assumption", finding: `the reader had to assume: ${s}`, blocking: true })));
  return out;
}

async function redraftPage(page, jobs) {
  const record = { id: page.id, path: page.path, briefPath: page.briefPath };
  if (page.status !== "handed-off") {
    return { ...record, status: "escalate", reason: `stage 1 status was "${page.status}", not handed off${page.reason ? `: ${page.reason}` : ""}` };
  }
  const pageJobs = jobs.filter((j) => j.id.startsWith(`${page.id}--`));
  const verifiedJobs = pageJobs.filter((j) => j.verifiedOk === true);
  const unverified = pageJobs.length - verifiedJobs.length;
  const allReader = verifiedJobs.flatMap(readerDefects);
  const struckReader = new Set(page.struckReaderFindings || []);
  const readerFindings = allReader.filter((f) => !struckReader.has(f.id));

  // A struck finding is dropped everywhere; the gate finding ignores `struck`.
  const pageFindings = page.findings || [];
  const stage1Findings = pageFindings.filter((f) => f.id === "gate" || !f.struck);
  const struck = pageFindings.length - stage1Findings.length + allReader.length - readerFindings.length;
  const all = [...stage1Findings, ...readerFindings];
  const redGate = all.some((f) => f.id === "gate");
  const graded = all.filter((f) => f.id !== "gate");

  const notes = [];
  if (unverified) notes.push(`${unverified} unverified reader run(s) excluded from evidence`);
  if (struck) notes.push(`${struck} struck finding(s) filtered`);
  record.note = notes.length ? notes.join("; ") : undefined;

  if (!all.length) {
    record.status = "accepted";
    return record;
  }

  // The handoff page carries the page args verbatim, so it is the page for both prompts.
  const d2 = await agent(draftPrompt(page, 2, all.map(findingLine).join("\n")), { label: `redraft:${page.id}`, phase: "Redraft", schema: DRAFT_SCHEMA, model: DRAFTER, agentType: DRAFTER_TYPE });
  if (!d2) return { ...record, status: "escalate", reason: "redrafter returned nothing" };
  record.draft = d2;

  // A general-purpose agent, not the read-only register editor: this read edits the facts
  // container when it retags the redraft's candidates.
  const redraftFiled = d2.bulletsFiled || [];
  const legit = (page.factRetagged || []).map((x) => x.id);
  const appliedPrompt = appliedFindingsPrompt(page, graded.map(findingLine).join("\n"), redraftFiled, legit);
  const applied = await agent(appliedPrompt, { label: `applied:${page.id}`, phase: "Applied", schema: APPLIED_SCHEMA, model: REVIEWER, agentType: "general-purpose" });
  if (!applied) return { ...record, status: "escalate", reason: "applied-findings read returned nothing" };
  record.applied = applied;
  const g2 = await runGate(page, `regate:${page.id}`);
  if (!g2) return { ...record, status: "escalate", reason: "the gate run returned nothing" };
  record.gate = g2;

  // The blocking flags are the script's own; the read's echo is never trusted. Every blocking
  // finding and every reader defect needs a matching entry marked "applied".
  const byId = new Map(applied.perFinding.map((e) => [e.id, e]));
  const required = graded.filter((f) => f.blocking);
  const omitted = required.filter((f) => !byId.has(f.id)).map((f) => f.id);
  const unresolved = required
    .filter((f) => byId.has(f.id) && byId.get(f.id).status !== "applied")
    .map((f) => ({ id: f.id, source: f.source, location: f.location, finding: f.finding, status: byId.get(f.id).status, evidence: byId.get(f.id).evidence }));
  const newBlocking = (applied.newIssues || []).filter((f) => f.blocking);
  // Two-round cap: this is the one redraft this page gets, so anything still unresolved here
  // escalates to the conductor rather than triggering a third round.
  if (omitted.length || unresolved.length || newBlocking.length || g2.gate !== "pass") {
    const why = [];
    if (omitted.length) why.push(`the applied read omitted blocking finding(s) ${omitted.join(", ")}`);
    if (unresolved.length) why.push(`${unresolved.length} blocking finding(s) not applied`);
    if (newBlocking.length) why.push(`${newBlocking.length} new blocking issue(s)`);
    if (g2.gate !== "pass") why.push(`the redraft's gate was "${g2.gate}"${redGate ? " (the stage-1 gate was red too)" : ""}`);
    return { ...record, status: "escalate", reason: `${why.join("; ")} after the one redraft round`, omitted, unresolved, newBlocking };
  }
  record.status = "accepted";
  return record;
}

async function stage2() {
  if (!a.handoffPath) throw new Error("docs-page-chain-v2 stage 2 needs args.handoffPath");
  if (!a.resultsDir || !String(a.resultsDir).startsWith("/")) {
    throw new Error("docs-page-chain-v2 stage 2 needs args.resultsDir, the absolute path of the reader runner's --out directory");
  }
  phase("Load");
  const [loaded, reader] = await parallel([
    () => loadHandoff(a.handoffPath),
    () => loadReaderResults(a.resultsDir)
  ]);
  if (!loaded) throw new Error("docs-page-chain-v2 stage 2: the handoff load returned nothing");
  if (!reader) throw new Error("docs-page-chain-v2 stage 2: the reader-results load returned nothing");
  if (reader.source === "missing") throw new Error(`docs-page-chain-v2 stage 2: no report.json under ${a.resultsDir}`);
  const orphans = reader.jobs.filter((j) => !loaded.pages.some((p) => j.id.startsWith(`${p.id}--`))).map((j) => j.id);
  if (orphans.length) log(`reader job(s) matching no handoff page, ignored: ${orphans.join(", ")}`);

  phase("Redraft");
  const results = (await parallel(loaded.pages.map((page) => () => redraftPage(page, reader.jobs))))
    .map((r, i) => r || { id: loaded.pages[i].id, path: loaded.pages[i].path, status: "escalate", reason: "the stage-2 chain threw" });

  phase("Report");
  const accepted = results.filter((r) => r.status === "accepted").length;
  log(`${accepted}/${results.length} pages accepted; ${results.length - accepted} escalated`);
  return {
    readerSource: reader.source,
    orphanReaderJobs: orphans,
    pages: results,
    accepted,
    escalated: results.filter((r) => r.status !== "accepted").map((r) => r.id)
  };
}

if (STAGE === 1) {
  return await stage1();
}
return await stage2();
