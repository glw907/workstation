# The drafter pipeline design

Status: design approved section by section by Geoff, 2026-10-12, in the session that ran the
spike. Revised the same day by the fold of three reviews (mechanics, contract, integrity); the fold
record is `docs/superpowers/research/2026-10-12-drafter-pipeline-fold.md`. Geoff ruled the three
questions under "Owner rulings" the same day, and in the same session approved the changes for
generality, the "Configuration" section, and sub-project 5. This spec covers sub-project 1 of
five. It awaits Geoff's review of the written text before a plan is written.

## Why

Geoff's Max 20x plan includes $200 a month of Claude API credits that expire each billing cycle and
go unused. The credits cover the Claude API, the Batch API, and the Claude Agent SDK, including
`claude -p` run with an API key. They don't cover interactive Claude Code sessions. Docs work is
the workstation's largest consumer of model time, and it's rarely urgent. Geoff: "I'm usually not
in a hurry with docs development."

The goal is to move the drafting and review half of docs work onto those credits without lowering
quality. Geoff set the bar: "current quality is the base standard. I won't shed any tears if this
new system improves it!"

drafter is built for Geoff first, but it has to work for other Claude Code users too. Geoff: "The
tool is obviously for me, but I'd like to build it in such a way that it's useful to other claude
code users." So sub-project 1 assumes nothing about this workstation. Anything that differs
between users or projects is a setting (see "Configuration"), and Geoff's own setup is a set of
values for those settings.

## Outcome

Claude Code still plans each page on Geoff's plan: page inputs, the page plan, the plan read, and
the framing record. A new Go tool, `drafter`, takes each planned page from there. It drafts the
page, gates it, runs the review seats, redrafts, and runs the final read, with every model call
billed to the API key drafter is given. By default each call is a request in a Message Batch,
which the batch documentation prices at "50% of the standard API prices"; a `sync` mode sends
ordinary Messages calls at full price. Each page ends accepted or escalated, with a record of
every request, finding, resolution, fault, and cost. drafter never commits: the planning session
reads the records and commits what it accepts.

The planner is whatever writes drafter's handoff file. In Geoff's setup that is the chain's front
half in Claude Code; sub-project 5 adds a Claude Code plugin that plans a page for any user.

## The spike

The design rests on a spike run on 2026-10-12, in scratch worktrees, with nothing committed.

- The batched one-shot drafter matched the chain's drafter. A blind grader rated three round-1
  drafts of `rotate-the-github-app-key` (the original chain draft, the drafter agent run through
  `claude -p` on the key, and a single batched call with its inputs assembled by script) and found
  "the spread between the three is narrow." All three passed the docs gate. The batched call cost
  about $0.90, against about $2 for the agentic step.
- The full batched back half reached the floor. With Claude Code doing the planning steps, the
  batched pipeline took two pages through every seat. Against the published pages, a blind grader
  rated the published rotate page "slightly better," with the batched one "publishable after
  ordinary fixes." It rated the batched `choose-an-ai-posture` page "clearly better" than the
  published one, which it found "materially below standard." Most of that lead came from fresh page
  inputs, which found a missing regeneration step and a snippet that fails typechecking on the
  published page.
- Cost and speed. A page cost $3 to $4.50 in credits. Batches returned in two to six minutes,
  so a page ran end to end in under an hour.
- No run reached `accepted`. All four recorded runs escalated, and the runs were stitched: one
  supplied its round-1 draft and another reused earlier round-1 reads. The October 7 chain run
  also escalated all five of its pages, so neither path has yet shown a page reaching `accepted`.
- Every escalation traced upstream of drafting: two facts that contradict another page, a fact
  that overclaims, and two plan gaps a reader would hit. The pipeline surfaced them and refused to
  invent facts to cover them. The October 7 escalations had causes of the same kinds.
- A whole-page redraft ignored an explicit blocking finding. It received the finding and a
  proposed sentence, and regenerated the page without it. An edit-contract redraft on the same
  findings resolved each one by number and changed nothing else.
- The spike's harness also misfired once on its own: after a reader redraft's edits failed the
  gate, its retry asked for "only the further edits," then refused the answer for lacking
  resolutions to findings the first attempt had already resolved, at a cost of $0.58
  (`run-rotate-edit2.log`, 11:49:57 to 11:54:06). The edit contract below closes that hole.

The spike's evidence lives at `~/.local/share/drafter/spike/`: the harness (`batchchain.py`), the
four `run-*/` directories with every request, response, and edit-contract answer, the goja probe
(`gojaprobe/`), and two docs-gate logs under `gate-logs/`. The build's first task copies the
fixtures the tests name into `~/Projects/drafter/testdata/spike/`, and a test whose fixture is
missing fails instead of skipping. No saved log has a failing `check:provenance` section, so that
task regenerates one with a deliberate provenance failure.

## Scope

Geoff decomposed the initiative into five sub-projects, each with its own spec, plan, and build:

1. This spec: drafter's `page` mode on cairn, the handoff file format, the layered configuration,
   the YAML plan format, and the plan checks.
2. Issue capture and the nightly run: `issue file`, `issue list`, `run`, a systemd user timer, and
   a registry of participating repos. Issues are GitHub issues labelled `docs-fix` on each
   project's own repo (Geoff, 2026-10-12). Queueing a `page` run for the night belongs here.
3. Workstation rollout: a `docs-fix` skill, the tooling manifests, `claude-infra` placement, and
   per-repo adoption.
4. Docs bootstrapping for repos with no docs, later and repo by repo.
5. Public readiness, after the pilot (Geoff, 2026-10-12: "a later sub-project"): a Claude Code
   plugin with a skill that plans a page in drafter's YAML format, runs `drafter check-plan` in
   its loop, and writes the handoff file; a stock prompts module on the Google developer
   documentation style; examples; and a public release.

Out of scope here: figure pages and rework pages, which stay on the chain; the issue queue; the
timer; any pilot repo but cairn; and all of sub-project 5, namely the planning plugin and skill,
the stock prompts module, the examples, and the public release. A figure page needs the
figure-verifier seat. A rework page needs the chain's `git diff` scoping, and the spike never ran
one, so the pilot couldn't judge it.

Sub-project 1 still builds nothing that only this workstation can use: the handoff file, the
plain gate, the key source, the optional facts store, and the configuration layers below are
general from the first build, so sub-project 5 adds a planner and a stock module without
reworking drafter.

## The tool

`drafter` is a standalone Go module, `github.com/glw907/drafter`, at `~/Projects/drafter`. Geoff
chose the name, after checking that the one prior `drafter` (Apiary's archived API Blueprint
parser) is disabled in Homebrew. It calls the API through the official Go SDK,
`github.com/anthropics/anthropic-sdk-go`.

The layout follows the go-conventions skill. `cmd/drafter/` holds only the cobra wiring.
`internal/` holds one package per concern:

| Package | Job |
|---|---|
| `config` | Loads the three configuration layers, resolves each setting with its source layer, and refuses money and credentials in `drafter.toml`. |
| `handoff` | Decodes a handoff file, or a chain's Workflow run file, into one handoff struct and verifies its checksum. |
| `key` | Resolves the API key from `key_command` or the named environment variable. |
| `assemble` | Builds each seat's request: the prompt, the agent definition as the system prompt, the files and command outputs the seat's inputs name, and the source excerpt behind each cited fact. |
| `prompts` | Loads a prompts module in goja and returns each seat's prompt. |
| `batch` | Sends each stage's requests, as a Message Batch in `batch` mode or as streamed Messages calls in `sync` mode, and classifies each result. |
| `ledger` | Reserves and settles spend, enforces the caps, and reports spend. |
| `pipeline` | The per-page state machine and its stop rules. |
| `edits` | The edit contract: its schema, applying edits, and refusing a bad answer. |
| `coverage` | The plan's mechanical coverage checks and the verification of the coverage read's quotes. |
| `gate` | Runs the gate and index-link commands, follows the `cairn-run-gate` protocol when the project sets it, and attributes each failing section to a page. |
| `plan` | Parses and validates YAML plans and runs the plan checks. |
| `run` | Run IDs, the run directory, state, snapshots, locks, and records. |
| `atomicfile` | The go-conventions atomic write. |

Its commands for this sub-project:

| Command | Does |
|---|---|
| `drafter page <handoff-file>...` | Runs each handoff file's page through the pipeline. `--workflow-run <wf-file>` reads the pages from a chain run's Workflow run file instead. `--dry-run` assembles the first stage's requests, prints their sizes and estimated cost, and submits nothing. `--resume <run-id>` continues a stopped run. `--sync` sends ordinary Messages calls for this run. |
| `drafter check-plan <file>` | Validates a plan's syntax and schema and runs the mechanical plan checks, offline, printing errors as `file:line` with the fix. |
| `drafter check-prompts` | Loads the prompts module and renders every seat over the test matrix. With `--expect <file>`, compares each prompt byte for byte with Node's rendering of the same context. |
| `drafter spend` | Prints spend by repo and seat for the current billing cycle, or for `--since` and `--until` UTC dates. |
| `drafter config` | Prints every resolved setting for the current project and the layer each came from. |

Every command prints for a person by default and takes `--json` for agents and scripts.

Nothing in drafter is cairn-specific. A project opts in with a `drafter.toml` at its root, and
everything that can differ between users, machines, or projects is a setting in the layers that
"Configuration" defines.

## Configuration

Settings differ between projects on one workstation, not only between users. Geoff: "some of
this might be different from project-to-project on the same workstation," and "configuration
will need to handle that." drafter mirrors Claude Code's settings pattern, whose docs describe a
committed `.claude/settings.json` that "everyone who clones the repository gets" and a
`.claude/settings.local.json` for "Personal overrides for one project," which Claude Code
"applies ... over the committed `.claude/settings.json`" (code.claude.com/docs/en/settings).

### Layers

drafter reads three TOML files:

| Layer | File | Holds |
|---|---|---|
| User | `~/.config/drafter/config.toml` | One user's settings for every project on the machine |
| Project | `drafter.toml` at the project root, committed | Settings everyone who works on the project shares |
| Local | `drafter.local.toml` at the project root, gitignored | One user's settings for one project |

A setting resolves from the first source that sets it, in this order: a command-line flag, an
environment variable, `drafter.local.toml`, `drafter.toml`, then the user config. The project root
is the worktree's top level (`git rev-parse --show-toplevel`). Each scalar setting reads an
environment variable named `DRAFTER_` plus its key in upper case, with each dot written as `_`
(`mode` is `DRAFTER_MODE`, `gate.protocol` is `DRAFTER_GATE_PROTOCOL`); tables and lists have
none. The two caps are the exception to that order: each resolves to the lowest value any source
sets, so a layer can tighten a cap and never loosen one.

Money and credentials never live in the committed file. drafter refuses a `drafter.toml` that
sets any setting the table below marks as money or credentials, naming the key, its line, and the
file to move it to. Claude Code has a narrower form of the rule: it reads `modelPicker` only from
managed, `--settings`, and user settings, and "ignores the key in project and local settings"
(code.claude.com/docs/en/settings). drafter refuses rather than ignores, so a misplaced cap or key
source can't fail silently. It also departs from Claude Code on credential commands. Claude Code
accepts `apiKeyHelper` in any file and, "when the command comes from project or local settings,
... doesn't run it until you accept the workspace trust prompt"
(code.claude.com/docs/en/settings-reference). drafter runs unattended and has no trust prompt, so
`key_command` can't come from the committed file at all.

Two more rules keep a cloned project from reaching outside itself. Every path in `drafter.toml`
must resolve inside the project. A machine-specific path, such as an agent definition under
`~/.claude/agents/`, belongs in the local or user layer. Until cutover, cairn's prompts module (the
chain script) and its agent definitions both live outside cairn's repo, and Geoff's
`drafter.local.toml` for cairn names them. The second rule: drafter refuses a `drafter.local.toml`
that `git check-ignore` doesn't report as ignored, because that file may hold a key source and
caps. Every layer decodes strictly: an unknown key is an error naming the file and line.

### Settings

"Layers" names the files a setting may appear in. Any scalar setting also reads its environment
variable, and a flag exists only where the table names one.

| Setting | Layers | Default | Money or credentials |
|---|---|---|---|
| `prices`: the dated price table, per model | user, local | none; a seat whose model has no entry refuses at load | money |
| `billing_cycle_day` | user, local | `1` | money |
| `workspace_id`: the expected Console workspace | user, local | none; required | credentials |
| `key_env`: the variable that holds the key | user, local | `DRAFTER_API_KEY` | credentials |
| `key_command`: a command that prints the key | user, local | unset | credentials |
| `api_base_url` | user, local | `https://api.anthropic.com` | credentials, since the key is sent there |
| `page_cap`, `cycle_ceiling` | user, local | none; both required | money |
| `mode`: `batch` or `sync` (flag `--sync`) | all | `batch` | no |
| `state_dir` | user | `~/.local/state/drafter` | money, since it holds the ledger |
| `retention_days` | user, local | `30` | no |
| `output`: `human` or `json` (flag `--json`) | all | `human` | no |
| `pages_in_flight` | all | `3` | no |
| `retries.gate_fix`, `retries.edit_contract` | all | `2` each | no |
| `gate.command`, `index_link_command` | project, local | none; `gate.command` required | no |
| `gate.protocol`: `plain` or `cairn-run-gate` | project, local | `plain` | no |
| `gate.lane` | project, local | unset; `cairn-run-gate` protocol only | no |
| `gate.section_pattern`, `gate.failure_pattern` | project, local | unset; the whole log is one section | no |
| `prompts`: the prompts module | project, local | none; required | no |
| `seats`: which seats run | project, local | every seat | no |
| `seat.<name>`: agent definition, model, effort, `max_tokens`, inputs | project, local | none; required for each seat that runs | no |
| `facts.dir`, `facts.bullet_format` | project, local | unset, meaning no facts store | no |
| `register.<track>`: the register sections each track reads | project, local | unset | no |
| `inline_files`: out-of-repo files a seat may inline | user, local | none | credentials, since it can send any file on the machine |

`state_dir` is user-only because the ledger in it enforces the cycle ceiling across every project;
a project that moved it would get a ledger, and a ceiling, of its own. The `draft` seat always
runs. Leaving a review seat out of `seats` removes its stages and its rows of the stop table, and
the record notes each seat that didn't run. The consistency read runs only when a facts store is
configured (see "Projects without facts").

Two things are deliberately not settings. The stop rules and the edit contract's refusal rules
are the quality contract: a project can set how many retries a budget allows, but not what counts
as accepted or what an answer must satisfy. Nor is the platform a setting. The credits work only
on the Claude API, so drafter speaks only to it, and `api_base_url` exists for tests and for
proxies that forward to that API.

### Inspecting the result

`drafter config` resolves every setting for the project it runs in and prints each value with
the layer, flag, or variable it came from, and each cap with every source that set it. It prints
`key_command` and `key_env` but never a key. A project with a refused `drafter.toml` prints the
refusal and exits nonzero.

## Seat prompts

The chain's prompts are code, not templates: 28 builder functions, 665 lines, and 109 branches or
loops, varying by page type, round, narrowed reads, and outline. They change often. The chain
script took 28 commits in the month before this spec. A copy would drift within days.

The prompts stay in JavaScript, and drafter runs them in-process with goja
(`github.com/dop251/goja`). Geoff chose this over Go templates because agents edit the prompts
often and are most fluent in JavaScript.

### Beside the chain

The builders aren't yet pure functions. They close over top-level state built from the chain's
`args` (`WT`, `GATE`, `OUTLINE`, `INDEX`, `OPTION_MAP`, `REGISTER`, `common`), and the chain's top
level awaits two `agent()` probes: the outline probe whenever `args.outline` is set, which is the
normal cairn case, and the rework probe. goja also rejects ES module syntax: a probe of
`export function draftPrompt(c){}` and of `export const meta = {}` both return `SyntaxError:
Unexpected reserved word`.

So during the beside-the-chain period drafter loads `docs-page-chain.js` itself, and the chain
gains three small pieces for it:

- `resolvePages()` opens with `if (typeof DRAFTER_HOST !== "undefined") return
  DRAFTER_HOST.resolved;`, so under drafter the page list and index come from the handoff, and
  the outline probe never runs.
- A `DRAFTER_SEATS` object maps each back-half seat to its builder (`draft`, `structure`,
  `editor`, `fact`, `reader`).
- Just before the slot pool, `if (typeof DRAFTER_HOST !== "undefined") return DRAFTER_SEATS;`
  ends the script under drafter.

drafter makes one textual change, `export const meta` to `const meta`, wraps the script in an
async function, and runs it with `args` from the handoff, a `DRAFTER_HOST` global carrying the
handoff's resolved pages and index, no-op `phase`, `log`, `parallel`, and `pipeline`, and an
`agent` that fails the load if called. The rework probe never calls `agent`, since a drafter
handoff carries no rework page. A fold probe ran this on a copy of the chain with those three
edits and an outline set, and goja's rendering of six prompts (the round-1 draft, a round-2 draft
with findings, the structural edit, the register editor, the fact read, and the task-guide final
reader) matched Node's byte for byte.

### At cutover

The back-half builders move into a module in cairn's repo. A prompts module is a plain script, not
an ES module, whose completion value is an object mapping each seat to a function of one context
object (the page, its inputs, the round, the findings, a narrowed read's diff) that returns a
string. A probe confirmed that goja returns such an object as the script's completion value and
calls its functions. goja's runtime defines no `require`, `fetch`, `process`, `console`, or
`setTimeout` (probed with `typeof`), so a module can compute text and nothing else. Turning the
closures into functions of a context object is cutover work. The context object also says whether
the project has a facts store, so a module can word the fact read for either case. A stock module
for a project with no voice of its own is sub-project 5's; until then a project names its own
module in the `prompts` setting.

### Checking the prompts

`drafter check-prompts` renders each seat over a matrix: page type (task guide, concept,
reference) by round (round 1; round 2 narrowed; round 2 whole; after the final read), with an
outline set. Each rendered prompt must contain the context's page path and, when the context has
findings, their text. In the dotfiles gate, a Node script renders the same matrix through the
chain and pipes it to `drafter check-prompts --expect`, which compares each prompt byte for byte.
The gate fails when the `drafter` binary is absent. The matrix's contexts live in
`~/.dotfiles/tests/fixtures/drafter/`.

## The handoff

A handoff tells drafter everything about one planned page. Any planner can write one, so its
format is documented and versioned, and drafter decodes every handoff into one struct whichever
way it arrived.

### The handoff file

A handoff file is a JSON object, one page per file, and `drafter page` takes one or more:

| Field | Holds |
|---|---|
| `version` | The format version, `1` |
| `project` | The project root, absolute; drafter loads `drafter.toml` and `drafter.local.toml` from it |
| `page` | The page's path and its brief's path, both relative to the project, and its type: `task-guide`, `concept`, or `reference` |
| `plan` | The plan's path, relative to the project |
| `framing` | The framing record's path, or absent when the planner wrote none |
| `inputs` | The page inputs with the plan's and the framing's dispositions applied: the page's job, the register sections to read, the exemplar sources, the claim inventory, and, when the project has a facts store, the fact ids |
| `context` | Optional. An object drafter passes to the prompts module unchanged |
| `checksum` | `sha256:` and the hex SHA-256 of the plan file's bytes followed by the framing file's bytes, when there is one |

drafter decodes each file strictly against its versioned struct and refuses an unknown version or
field, naming the file. It also refuses a path that resolves outside `project`, a checksum that
doesn't match the files on disk, and a set of handoffs that name more than one project, since one
run works one worktree. The checksum pins the plan and framing the planner checked: a plan edited
after the handoff was written fails it, and so does one edited between a stop and a resume. A
planner computes it with `cat <plan> <framing> | sha256sum`.

### The chain's Workflow run file

Geoff's chain has a shorter path. The chain gains a `backHalf` argument. With
`backHalf: "drafter"`, the Workflow refuses at start if any page carries `figure` or `rework`, and
otherwise stops after framing and returns `{ handoff }`. That handoff holds a schema version, the
chain's `args`, the resolved pages and index, the worktree path, and one entry per page: the page
config, the page inputs with the plan's and the framing's dispositions applied, and the plan and
framing paths. A pure `handoffFor` function builds it, inside a `// === HANDOFF ===` block that a
node test extracts, the way the existing derivation and outline tests extract theirs
(`scripts/check.sh:60-61`). The test runs it on a recorded page and compares the result with a
fixture that drafter's own tests also decode.

The Workflow runtime persists each run's `args` and return value verbatim in
`~/.claude/projects/<project>/<session>/workflows/wf_<id>.json` (observed in
`wf_7ef2ce8f-59b.json`, whose `result` holds the chain's return object). `drafter page
--workflow-run <wf-file>` reads the handoff from that file, so no model retypes it and nothing
lands in the worktree. That file is Claude Code's internal format, so drafter reads only
`.result.handoff`, decodes it strictly against its own versioned struct, and refuses an unknown
version or field with the file path in the error. It then converts each page to the handoff
struct. The worktree becomes `project`. The chain's `args` with the resolved pages and index become
`context`, which the beside-the-chain loader hands to `DRAFTER_HOST`. No model retyped anything, so
drafter computes the checksum itself at conversion and records it. A resume then checks the plan
and framing exactly as it would for a handoff file.

Before running drafter, the planning session commits the plans and framing records, since drafter
starts only on a clean worktree. With `backHalf` unset, the chain runs as it does today, and that
is the fallback (Geoff, 2026-10-12: beside the chain first, cutover after a pilot).

## The pipeline

Each page runs these stages, with the chain's rules. A stage's requests go out together, as one
batch in `batch` mode or one after another in `sync` mode; "batched" below means either.

1. Plan check. `check-plan` runs on the page's plan. When the project has a facts store, one
   batched consistency read then checks the placed fact bullets against each other and against the
   headings of every linked page. A `check-plan` error or a consistency finding escalates to the
   planning session before any drafting spend.
2. Draft. One batched call returns the page and its brief. drafter runs the index-link command,
   then the gate. A red gate opens an edit-contract exchange in the same conversation, with this
   page's failing gate sections as the numbered blocking findings, inside the gate-fix budget
   (`retries.gate_fix`, default 2).
3. Coverage. The plan's mechanical items are checked against the page and brief. Then one batched
   coverage read quotes the sentence that satisfies each `claim`, `handoff`, and `reason` item, or
   reports it missing. drafter verifies each quote (see "Coverage" below). Each miss becomes a
   blocking finding from the `coverage` seat.
4. Round-1 reads. The structural edit, register editor, and fact read run in one batch.
5. Redraft. If any round-1 seat returned fix or coverage reported a miss, one edit-contract
   redraft, then the index-link command, the gate, and the coverage check again.
6. Round-2 reads. Only the seats that returned fix, narrowed to the redraft's diff.
7. Final reader read. If it returns fix, one edit-contract redraft, the gate, the coverage check,
   scoped re-reads by the register editor and fact read, and a reader retest.

A read that returned nothing, didn't parse, or failed its schema never counts as accept.

### Stop rules

| Where | Trigger | Budget | Outcome |
|---|---|---|---|
| Plan check | A `check-plan` error or a consistency finding | none | escalate: `plan` |
| Draft | A truncated or unparseable answer, or a brief that isn't JSON | one retry | escalate: `unreadable draft` |
| Draft | A red gate naming this page | `retries.gate_fix` | escalate: `red gate` |
| Any stage | A red gate naming no file of this page | none | the page holds; see "Shared worktree" |
| Redraft, reader redraft | A refused edit-contract answer, or a red gate after applied edits | `retries.edit_contract`, shared | escalate: `contract` |
| Redraft | A coverage miss after the redraft | none | escalate: `second fix verdict` |
| Round 2 | Any seat returns fix | none | escalate: `second fix verdict` |
| Round 2 or final read | A read missing or unreadable | none | escalate: `unreadable <seat>` |
| Final read | A coverage miss, a scoped re-read's fix, or the retest's fix | none | escalate: `fix after the reader redraft` |
| Any stage | The stage's reservation would cross the page cap | none | escalate: `cap` |
| Any stage | The reservation would cross the cycle ceiling, or the API reports a spend limit | none | the run stops, resumable: `cycle cap` or `spend limit` |

There is no third round. An escalated page keeps its whole record, and its record names the stop
rule and the seat and finding numbers that triggered it.

### Input assembly

Each seat receives its prompt, its agent definition as the system prompt, the files and command
outputs its inputs name, and, when the project has a facts store, a source excerpt for each cited
fact. A note tells the seat that
files are inlined, that a command whose output isn't inlined is not to be run, and that any edit
it would make, or any check it couldn't make, becomes a finding. So a chain edit that adds a step
drafter doesn't supply shows up as a finding in the record, not as a silent gap.

- Files. drafter inlines each path in the rendered prompt that `git ls-files` lists in the worktree,
  plus the out-of-repo files the `inline_files` setting allows (for cairn, Geoff's local layer
  allows the exemplars under `~/.local/share/cairn/exemplars/`). Anything else named stays out, and
  a file over the size limit becomes an explicit `not inlined: N bytes` block.
- Commands. Each seat's inputs (its `seat.<name>` setting) list the commands whose output it gets:
  Vale on the page, the page's pending option-map rows, and, in round 2, the diff. drafter runs each
  from the worktree just before the request and inlines its output under the command text.
- The round-2 diff. drafter keeps the round-1 page as a file in the run directory, passes its
  `git hash-object` ID as the narrowed read's baseline, and inlines the diff from that snapshot to
  the current page under the command the prompt names.
- Source excerpts. A `path:line` pointer yields the lines around it. A `path#name` pointer yields
  the lines around the declaration of `name`, found by a declaration pattern (a Go `func`, `type`,
  `var`, or `const`; a TypeScript or JavaScript `function`, `class`, `interface`, `type`, `enum`,
  `const`, or `let`), not by any mention. A bare file is inlined whole up to the size limit. A
  directory or a prose source yields an explicit `no excerpt: <form>` block. A count of cairn's
  fact files found 1,550 Source lines: about 1,030 with a line range, about 620 with a
  declaration, and the rest in neither form.

The final reader holds the page alone. Its first turn carries the reader prompt with steps 1 and 2
and only the page, and returns its paraphrase and answers. The second turn, a continuation in the
next stage, gives the page's job (the outline entry's job text, inlined) and asks for step 3. So
the job never sits in the reader's context while it paraphrases. It costs one more stage, about
two minutes in `batch` mode, and well under a cent.

### The edit contract

Every redraft and gate-fix turn returns exact edits, each a file (`page` or `brief`), an old span,
and its replacement, plus one resolution per numbered finding: `edited` with the indexes of its
edits, or `declined` with a reason. drafter applies the edits in order, and each old span must
occur exactly once in the text as the earlier edits in the same answer left it.

drafter refuses an answer when any of these hold:

- an old span occurs zero or several times
- a `file` is neither `page` nor `brief`
- an edit's old and new text are equal
- an edit no resolution claims
- a resolution names an edit index that doesn't exist, or a finding number that doesn't exist
- a finding, blocking or advisory, has no resolution, or has more than one
- a blocking finding resolved `edited` has no edits
- the brief isn't valid JSON after the edits

A refused answer gets its problems back. Resolutions accumulate across attempts: a retry adds to
or overrides earlier resolutions, and drafter checks the union. When edits applied cleanly and
the gate then fails, the continuation carries the current page and the failing sections as new
numbered findings, and the earlier resolutions stand. Refusals and post-edit gate failures share
one budget, `retries.edit_contract` (default 2); the failure after the budget is spent escalates
with `contract`.

A blocking finding may be declined only when it is factually wrong about the page. drafter can't
judge that, so it passes each declined blocking finding and its reason to that seat's next read,
which must accept the decline or raise the finding again.

### Coverage

The mechanical checks need each plan section's page heading, so every plan section names its
heading text. A brief sentence is located on the page by its text after a fixed normalization
(collapsed whitespace, with Markdown emphasis and code delimiters removed), and its section is the
nearest heading above it. A sentence that can't be located is reported as a miss, never skipped.

A coverage-read quote counts only when it occurs, after the same normalization, inside the section
the plan item names. A quote that fails is a miss, and the event lands in the record's faults.

### The agentic exception

A fact read that needs code its excerpts don't cover reports that as a finding, and the page
escalates. A `claude -p` fact read on the key is the remedy if the pilot shows the need. The first
build leaves it out, since the spike never needed it.

### Projects without facts

The facts store is optional. A project that leaves `facts.dir` unset still runs every page, with
these differences:

- The fact read checks the page's claims against the code the page names. drafter inlines each
  path the page or its brief names that `git ls-files` lists, under the same size limit, in place
  of fact excerpts.
- `check-plan` skips each `fact` item with a warning naming its line, and its link and fact test
  checks links only.
- Stage 1 runs no consistency read, and the coverage check skips `fact` items.
- The record notes `facts: none`, so a reader of the record knows which checks didn't run.

cairn sets `facts.dir` and keeps every facts behavior this spec describes.

### Shared worktree

Several pages run in one worktree, and most docs-gate components read the whole tree: only Vale,
tellgrader, and provenance narrow to `--page` and `--brief` (`docs-gate.mjs:7-12`). So the gate
package splits the log into sections with `gate.section_pattern` (for cairn, its `== component ==`
headers) and finds failing lines with `gate.failure_pattern`, then tags each failing line by
whether it names this page or its brief. With no section pattern the whole log is one section, and
with no failure pattern every line of a red log counts as failing. A log the patterns can't parse
falls back to its tail, recorded as `gate_log: unparsed`.

- A gate-fix turn gets only the sections that name this page.
- A red gate with no failure naming this page is foreign. It costs no fix turn; the page waits,
  and drafter gates it again after the other pages settle. A foreign failure that persists stops
  the run with `tree red outside drafter's pages`, and no page escalates for it.
- When a page escalates, drafter restores its page and brief to their pre-run snapshots, or
  removes them when drafter created them, so the tree stays green for the other pages. The draft
  stays in the record as `final.page.md` and `final.brief.json`.

## The plan format

The plan becomes one YAML file, `<page>.plan.yaml`, validated against a JSON Schema that drafter
publishes. It holds the argument, the order and its reasons, the introduction, each section with
its page heading and its items, the dispositions, and the drafting constraints. Prose fields use
`|` block scalars.

Geoff asked for the format that gives the best and most predictable outcome and is easiest for
Claude Code to work with. YAML won on editing: Claude Code writes the plan with Write and revises
it with Edit, and YAML keeps prose readable with no escaping to match. Its parsing traps are closed
by validation in the writer's loop: the plan step ends by running `drafter check-plan` until it
reports no errors, and the plan read starts only on a clean plan. JSON was rejected for unreadable
prose, markdown with an item grammar for drift from an invented syntax, and TOML for awkward
nesting.

One trap is silent. Probed with `gopkg.in/yaml.v3`, `claim: Push the new key first # then delete
the old` decodes to `Push the new key first` with no error, and the rest lands in the node's
`LineComment`. So `check-plan` walks the `yaml.Node` tree and rejects any prose field with a line
comment, naming the line and the fix (a `|` block or quotes). The other traps already fail loudly:
`claim: Note: the old key still works` is a parse error, and `claim: no` decodes as the string
`"no"` into a string field.

Each plan item has an id, a section, and a kind:

| Kind | Pins down | Checked by |
|---|---|---|
| `fact` | A fact id placed in a section | Mechanically: the brief cites it in a sentence located in that section; skipped without a facts store |
| `sentence` | A load-bearing sentence, `verbatim` or `claim` | Verbatim mechanically, claim by the coverage read |
| `link` | A target path and anchor | Mechanically: the page links it in that section |
| `handoff`, `reason` | A section's closing turn, or a "why" that must survive | The coverage read |
| `step` | A task step, with `requires` and `produces` state | The plan check |
| `failure` | A failure a step can cause, its symptom, and the item that handles it | The plan check |

`check-plan` runs three mechanical tests, offline:

- The reader-state walk confirms every step's `requires` is produced by an earlier step or listed
  as a precondition. It proves consistency, not completeness: a page with no deploy step passes
  unless some step declares `requires: deployed`. The plan-mode structural read stays the
  completeness check.
- The recovery matrix confirms every step marked `canFail` has a `failure` item and that every
  handler exists.
- The link and fact test confirms every target file and anchor exists on disk, with anchors matched
  by GitHub's slug rule as `github-slugger` implements it (the rule cairn's renderer uses, through
  `rehype-slug`), and that every placed fact exists in the facts files and is citable. `[rejected]`
  and `[candidate]` facts are not citable.

The consistency read runs once per page, in pipeline stage 1, not in the writer's loop: it is a
model call, nondeterministic, and minutes long under batching. It returns JSON: a list of
conflicts, each with the fact ids involved, the conflicting fact id or `page#heading`, and one
sentence naming the conflict. An empty list passes.

Each test answers a failure the evidence shows. The plan reads of the October 7 run caught
reader-state gaps by hand, such as a page with no deploy step. The spike's final reader found two
recovery gaps the plan never listed. Both of the exemplar page's escalations were fact conflicts,
which the consistency read targets. Three of the five October 7 escalations were plan-placed
content that a redraft compressed away, which the coverage check targets. Whether each check
catches its target is measured in the pilot: each escalation record names the check that caught
its cause, if any.

In cairn, the chain's plan prompt writes YAML and runs `check-plan`, and the plan-mode structural
read gains the state and recovery checks. An existing markdown plan still runs, with a warning and
without the plan-dependent checks, and the record notes `plan_format: markdown`.

## Operations

### Caps

Two caps, both user settings with no built-in amount: a cap per page (`page_cap`) and a ceiling
per billing cycle (`cycle_ceiling`). They live in the user config or `drafter.local.toml`, never in
the committed `drafter.toml`, and each resolves to the lowest value set (see "Configuration").
drafter refuses to start until both are set, so it never spends against a default the user
didn't choose (Geoff, 2026-10-12: "That should be something a user can decide."). Geoff's own
config sets $10 per page and $160 per cycle, which is 80% of his $200 credit. The $40 per-run cap
Geoff first set is dropped: overspend is already bounded by the ceiling and a runaway page by the
page cap, and Geoff allowed dropping it if redundant.

Before each submission, drafter reserves the stage's worst case: input counted by the
token-counting endpoint, plus each request's `max_tokens` at the output price. Output was 6% to 60%
of a request's cost in the spike, so input alone can't bound a stage. Each cap counts settled
spend plus every open reservation, across all pages and processes. A stage whose reservation
would cross the page cap escalates the page with `cap`. One that would cross the ceiling stops the
run, resumable, with `cycle cap`. Each seat's `max_tokens` lives in its `seat.<name>` setting;
cairn starts
at 64,000 for the drafting seats (the largest spike output was 43,995) and 32,000 for the reads
(the largest was 11,648).

The ceiling resets at 00:00 UTC on `billing_cycle_day`; a cycle day past a month's end resets on
that month's last day.

### The ledger

`ledger.jsonl` in `state_dir` (default `~/.local/state/drafter`) holds two kinds of line, each
with the run ID, repo, page, seat, model, and mode:

- A reserve line, written before the stage's requests go out, with the stage's intent ID and its
  worst-case cost.
- A settle line per result, keyed by batch ID and `custom_id` in `batch` mode or by the message ID
  in `sync` mode, with tokens by kind and the computed cost. Settling a key twice is a no-op.

Every cap check, submission, and append happens under `flock` on `ledger.lock` beside it, so two
drafter processes can't both pass a cap. Per-page spend derives from the ledger by run ID and page.
A resumed run therefore carries its earlier spend.

Cost comes from the dated price table in the `prices` setting, citing the published pricing page.
The table holds input, output, five-minute and one-hour cache-write, and cache-read rates per model,
and the 50% batch discount, which drafter applies only to `batch` mode results. Haiku 5.5 carries
both tiers: a prompt over 100,000 tokens pays higher prices. drafter refuses at config load any
seat whose model has no price entry, so a missing price can't compute as zero.

### A server-side backstop

drafter's setup docs recommend a key of its own in a Console workspace of its own, with the
workspace spend limit set in the Console. Geoff's install does this. Workspace spend limits can be
set only there (Settings, Workspaces, Spend limits), and they cap a calendar month, while drafter's
ceiling follows the billing cycle. The amount is the user's decision (Owner ruling 3). drafter's
setup docs explain the trade: a limit equal to the ceiling is a coarse guard that a cycle spanning
two calendar months can exceed, and a lower limit is tighter but caps what drafter can spend in one
month. They also tell the user to confirm the API organization has no payment method or auto-reload
if the credit should be the hard stop. Geoff's install sets the limit to $160. The batch
documentation warns that "batches may go slightly over your Workspace's configured spend limit", so
the backstop is coarse.

### The key

drafter takes its key from one of two sources, both settings in the user or local layer:

- `key_command`, when set: a command that prints the key. It is modeled on Claude Code's
  `apiKeyHelper`, which runs "your own command to produce the credential Claude Code sends with
  model requests" and is meant "for dynamic or rotating credentials, such as short-lived tokens
  fetched from a vault" (code.claude.com/docs/en/settings-reference). drafter runs it through
  `/bin/sh -c` at the start of each run and each resume and takes its standard output, trimmed. A
  nonzero exit or empty output refuses the run, and drafter never logs the output.
- Otherwise the environment variable `key_env` names, by default `DRAFTER_API_KEY`.

The default is a variable of drafter's own so that a general `ANTHROPIC_API_KEY` already in the
shell never bills drafter's runs by accident; a user who wants that key names it in `key_env`.
drafter builds its client with `option.WithoutEnvironmentDefaults()` and `option.WithAPIKey(key)`,
which skips the SDK's credential chain (`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, profiles,
federation, and `ANTHROPIC_BASE_URL`), and sets `option.WithBaseURL` from `api_base_url`. It
refuses to start when the resolved source yields no key. On its first call of each run it reads
the documented `anthropic-workspace-id` response header and stops before any request when it
differs from `workspace_id`. drafter never prints the key and never uses OAuth, so it can't bill a
Claude subscription.

drafter knows nothing about where a user keeps the key. Geoff's setup is his own note, filed with
sub-project 3's rollout: `DRAFTER_API_KEY` is kept in the age store through the secrets flow
(`secret-receive`, then `secret-set.sh`), and his `~/.local/secrets` already exports the general
`ANTHROPIC_API_KEY`, which serves the Claude CLI and two workers, into every interactive shell.

### Caching

No prompt caching in the first build. A continuation is a new request sent after a gate run, so
only a one-hour cache could survive, and `cache_control` has to sit on the earlier request before
anyone knows a continuation will follow. On Opus 5.5 a one-hour write costs 2x the input price and
a cache read 0.05x (published pricing), so one continuation costs 2.05x against 2x uncached. The
pilot's ledger shows how often continuations happen; caching returns only if pages average more
than one.

### Records

Each run gets an ID at start, a UTC timestamp plus a short random suffix. Records live under
`runs/<repo>/<run-id>/<page>/` in `state_dir`, outside the repo, and drafter creates the
run directory exclusively. A page's record holds its requests, responses, edit-contract answers,
gate excerpts, the pre-run and round-1 snapshots, `final.page.md` and `final.brief.json` with
their hashes, and a `record.json`: stages, verdicts, findings, resolutions, faults, friction,
escalation (stop rule, seat, and finding numbers), cost, mode, plan format, facts store, seats
that didn't run, input hashes, and final status.

`faults` is computed mechanically on every page. It lists a blocking finding left without a
resolution, a refused answer whose problem the answer didn't cause, a read that returned nothing
or didn't parse, and a coverage quote that isn't on the page. `friction` holds each seat's
friction entries; the planning session files them into the friction log when it commits.

At each run start, drafter deletes the run directories older than `retention_days` (default 30)
whose every page ended accepted or escalated; a stopped, resumable run is never pruned, and the
ledger is never pruned, since `drafter spend` reads it. The Batch API's own results expire after
29 days.

### Run inputs

At run start, drafter copies the prompts module, each seat's agent definition, and the resolved
configuration, with each setting's source layer and without credentials, into the run directory with
their hashes, and builds every stage from those copies. A chain edit, an agent-definition change, or
a configuration change mid-run, or between a stop and a resume, then can't change a run's prompts or
seats. Three things are read fresh at resume: the caps, so a tightened cap applies at once; the key;
and `workspace_id`. State carries a schema version and the drafter version, and a resume under
another state schema refuses with a clear message.

### One run per worktree

drafter takes a non-blocking `flock` on `$(git rev-parse --git-dir)/drafter.lock` for the whole
run, and another on the run directory. A busy lock exits with the holder's PID. At start drafter
refuses a worktree with uncommitted changes and records the branch and HEAD in state. At resume
the branch must match, HEAD must be that commit or a
descendant, and the only changes must be drafter's own files at their recorded hashes. The
planning session doesn't edit the worktree while drafter runs; it learns drafter is done from the
lock and the records.

### Resume

State is written after every step that spends money or writes the worktree:

- Before creating a batch, drafter writes an intent with the stage, the attempt, a timestamp, and
  `custom_id`s unique to run, page, stage, and attempt. After `create` returns, it records the
  batch ID. On resume, an intent with no batch ID lists the workspace's batches created after the
  intent's timestamp, waits for each to end, and adopts the one whose results carry its
  `custom_id`s before resubmitting anything. drafter's own workspace keeps that list short.
- In `sync` mode, before sending each request, drafter writes the same intent, then saves the
  response and its message ID when the stream ends. A sync request can't be reattached, so on
  resume an intent with no saved response settles at its reservation, marked `estimated` in the
  ledger since its real usage can't be recovered, and is sent again.
- Before writing the page and brief, drafter saves their contents and SHA-256 hashes, writes both
  through `atomicfile.WriteFile`, then records the post-write hashes. On resume, files at the
  post-write hashes continue; files at the pre-write hashes redo the write from the saved answer
  at no cost; anything else stops and names the changed file, and drafter never overwrites it.

Batches run on if drafter dies, so in `batch` mode `--resume` reattaches to an in-flight batch
instead of paying for it twice, and it settles any ended batch it hasn't ledgered.

### Concurrency

drafter keeps up to `pages_in_flight` pages (default 3) in the pipeline at once. In `batch` mode
it submits each such page's current stage and runs one sequential poll loop over all in-flight
batches. In `sync` mode it sends one request at a time, streamed, since the API docs advise
against "setting a large `max_tokens` value without using the streaming Messages API or Message
Batches API" (platform.claude.com/docs/en/api/errors). It starts no goroutines. Gates run one at a
time.

### The gate

By default the gate is a plain command (`gate.protocol = "plain"`). drafter runs `gate.command`
through `/bin/sh -c` from the project root, writes its combined output to a log in the run
directory, and reads the exit code: 0 is green, anything else is red. The index-link command runs
the same way.

With `gate.protocol = "cairn-run-gate"`, drafter runs the gate command through `cairn-run-gate`,
which needs a caller outside Claude to follow its protocol:

- drafter passes a log path in the run directory as the wrapper's second argument (its usage is
  `cairn-run-gate [--fresh] '<gate string>' [log path]`) and parses that whole log, since the
  wrapper prints only the last 60 lines.
- Exit 75 means "still running": drafter re-issues the same command until a `gate exit:` line
  appears.
- drafter clears `RUN_GATE_IF_BUSY` from the gate's environment, so it never gets the deferred
  exit 76.
- `gate exit: 1 (vanished 3 times)` is infrastructure: the run stops, resumable, and no page
  escalates.
- drafter sets `CAIRN_GATE_LANE` from `gate.lane`; cairn sets `light`, since its docs gate
  launches no browser.
- The wrapper writes its own receipt and run record for each finished gate. drafter never uses
  `--receipt` in place of a run, since every gate it needs follows a write to the tree.

### Failures

| Result | Action |
|---|---|
| HTTP transport error (DNS, reset, timeout) | Retry with backoff, bounded by wall time; the page's state doesn't change |
| 429 with `retry-after` | Wait, then retry |
| 429 `enforced_spend_limit_reached`, or 400 "You have reached your specified workspace API usage limits" | Stop the run, resumable; escalate nothing; print the limit message |
| `errored` with `api_error` or `overloaded_error`, or in `sync` mode HTTP 500 or 529 | Resubmit once |
| `errored` with `invalid_request_error`, or in `sync` mode HTTP 400 | Escalate with the error |
| `canceled` or `expired` | Resubmit once (neither is billed), then stop the run as infrastructure |
| `stop_reason` of `max_tokens`, or a parse or schema failure | Refuse the answer and never write it; one retry, then escalate with `unreadable <seat>` |
| `stop_reason` of `refusal` | Escalate with the refusal |

The API client sets a per-request timeout (`option.WithRequestTimeout`) and turns off the SDK's own
retries (`option.WithMaxRetries(0)`), which the API docs say retry "transient failures (such as
connection errors, rate limits, and 5xx server errors) ... twice by default." drafter retries by
this table instead, so every attempt has an intent and a ledger line.

### Models

Each seat's model and effort are settings. cairn's `drafter.toml` runs every seat on
`claude-opus-5-5`: the drafter and redrafts at high effort, the review seats at medium, the
coverage and consistency reads at low. cairn changes a seat's model only on pilot evidence.

## Testing

Unit tests are table-driven and use the standard library only. Each negative row asserts the exact
error and, where it has one, `file:line`, and pairs with a clean twin that must pass. A test whose
fixture is missing fails.

- The edit contract: one row per refusal rule; applied edits in order with uniqueness measured
  after earlier edits; resolutions accumulating across attempts; a red gate after applied edits
  sharing the retry budget; an accepted declined advisory; a declined blocking finding passed to
  the next read; and the spike's `reader-redraft-1.answer.json`, which must now be accepted.
- The plan checks: a `requires` produced only by a later step (fails), a `requires` met by a
  precondition (passes), a failing step with no handler, a handler that doesn't exist, a missing
  target file, a missing anchor, a placed id absent from the facts files, a placed `[rejected]` and
  a placed `[candidate]` fact, and a prose field with a line comment.
- Coverage: a verbatim item present and absent; a fact cited in its section and in another; a link
  in and out of its section; a brief sentence that differs from the page only in a code span; and
  a recorded coverage response whose quote isn't on the page, which must come back a miss.
- Input assembly: an untracked path, an allowed out-of-repo path, an oversized file, and source
  excerpts for `path:line`, a bare file, a directory, a prose source, and a `#name` whose name is
  imported above its declaration (the excerpt must hold the declaration). The final reader's first
  turn holds exactly one file block, the page, and no job text.
- The handoff: a handoff file decodes; an unknown version, an unknown field, a path outside the
  project, two handoffs naming different projects, and a checksum that doesn't match the plan and
  framing are refused; a plan edited between a stop and a resume fails the checksum. The chain
  test's fixture, read as a Workflow run file, converts to the same struct as the equivalent
  handoff file, and a figure or rework page in it is refused.
- The gate: a plain gate's exit 0 and nonzero, with and without section and failure patterns;
  failing sections from real logs (`gate-logs/` and the regenerated provenance case); an
  unparseable log; and two pages where page B's broken link reaches page A's gate without spending
  A's fix turns. Under `cairn-run-gate`: exit 75 then a result, the vanish case, the log path
  passed as the second argument, and `CAIRN_GATE_LANE` set from `gate.lane`.
- Caps and the ledger: a stage whose input fits under the page cap but whose input plus
  `max_tokens` doesn't (refused, `cap`); several in-flight pages crossing the ceiling; two
  processes against one ledger; a settle applied twice; the reset at its exact instant and on a
  cycle day of 31 in February; a cost row for a one-hour cache write and one for a Haiku request
  over 100,000 tokens; and a seat whose model has no price.
- The key: with only `ANTHROPIC_API_KEY` set, and with only an OAuth variable set, drafter
  refuses; `key_env` naming another variable reads it; `key_command` wins over the variable, and
  its nonzero exit or empty output refuses the run without printing anything it wrote; a
  mismatched `anthropic-workspace-id` stops the run before any request.
- Configuration: a setting overridden at each layer (user, `drafter.toml`, `drafter.local.toml`,
  environment, flag) resolves to the highest source, and `drafter config` names that source; a cap
  set at two layers resolves to the lower value whichever layer holds it; a `drafter.toml` holding
  `key_command`, `key_env`, `workspace_id`, `prices`, or a cap is refused with the key and line; a
  `drafter.toml` path outside the project is refused; a `drafter.local.toml` that git doesn't
  ignore is refused; an unknown key at any layer is refused.
- A project without facts: `check-plan` warns on and skips a `fact` item; stage 1 sends no
  consistency read; the fact read's request inlines the tracked files the page names; the record
  notes `facts: none`.
- Retention: a finished run older than `retention_days` is pruned, a stopped run of any age is
  kept, and the ledger is untouched.
- The pipeline state machine: every row of the stop table and the failures table, against a fake
  API client whose fallible methods each carry an error field. Resume rows: a stop after `create`
  with no recorded ID (no second `create`); a stop after a batch ended but before ledgering (one
  settle line per `custom_id`); a stop between the pre-write record and the write; a resume whose
  page file changed by hand (stops, names it); a resume with earlier page spend (the cap counts
  it); a `sync` intent with no saved response (settled at its reservation as `estimated`, then sent
  once more); and a synthetic run that reaches `accepted` in each mode.

Parsing tests use the spike's recorded responses as fixtures. End-to-end tests build the binary and
run `check-plan`, `check-prompts`, and `page --dry-run` on fixtures; the dry run points the client
at an `httptest` server through `option.WithBaseURL`, which returns a fixed `input_tokens`, and
the printed estimate must equal a hand-computed figure. A `make smoke` target, kept out of
`make check` because it spends money, submits one request per seat shape (schema, effort, and
system prompt as production builds them) on Haiku 5.5 in `batch` mode, plus one request in
`sync` mode, and asserts each result parses to its
schema, the ledger gains one settle line per request, and each line's cost matches its usage block
under the price table.

## The pilot

The next cairn docs pass runs on drafter in `batch` mode, reading the chain's Workflow run file,
with the chain's back half as the fallback. Every pilot page runs on a YAML plan. Cutover needs all
four:

1. Geoff accepts every page drafter accepted, after ordinary fixes, in the pass's PR, and the
   pilot meets the acceptance floor Owner ruling 1 sets. A blind grader reads each accepted page
   against the register as a second opinion.
2. Every escalated record has an empty `faults` list. The planning session writes one cause per
   escalation into the pass record (a plan gap, a fact conflict, or a missing fact), citing the
   record's escalation findings, and Geoff confirms them in the PR.
3. Accepted pages average $5 or less in ledger cost, no record ends with `cap`, and no page's
   ledger total exceeds $10.
4. `drafter spend` over the pilot's UTC dates matches the Console's cost for drafter's workspace
   over the same dates within 5%, and the key tests above pass.

The pilot covers at least five pages, including two task guides and one concept page. Cutover is
Geoff's call. It moves the back-half prompts into cairn's repo and deletes the chain's back half,
the `DRAFTER_HOST` hooks, and the `backHalf` flag.

## drafter's own docs

The repo carries a README, the plan schema reference, the prompts-module contract, the handoff
file format, the configuration reference (the three layers, their precedence, and every setting in
the table above), and the setup guide (the key source, the Console workspace, and the spend-limit
trade), written to the Google developer documentation style. Nothing in them assumes this
workstation; Geoff's own values live in his config files and his setup note.

## Owner rulings

Geoff ruled the three questions the fold raised, 2026-10-12:

1. Cutover requires at least three accepted pilot pages. A page escalated for an input cause may be
   rerun after the planning session fixes the input, and the rerun counts. The pilot record carries
   the count, so criterion 1 can fail.
2. The task-guide final reader stays a batched, read-only reader in the first build, and each
   "inferred, not run" finding is recorded. A `claude -p` reader on the key is added only if the
   pilot's task guides show a gap.
3. The workspace spend limit is the user's decision, not drafter's: "That should be something a
   user can decide." The caps and the setup docs above carry it. Geoff's install sets $160.

## Open items

- Whether the coverage read moves to Haiku 5.5, decided on the pilot's cost and accuracy data.
- Two findings from the spike for cairn: the published `choose-an-ai-posture` page lacks a
  `site-facts.json` regeneration step, and its route snippet fails typechecking. They become the
  first `docs-fix` issues once sub-project 2 lands, or a direct fix sooner.
