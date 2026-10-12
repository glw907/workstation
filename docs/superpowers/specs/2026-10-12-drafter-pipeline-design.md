# drafter: the batched docs pipeline (design)

**Status:** design approved section by section by Geoff, 2026-10-12, in the session that ran the
spike. This spec covers sub-project 1 of four. It awaits Geoff's review of the written text before a
plan is written.

## Why

Geoff's Max 20x plan includes $200 a month of Claude API credits that expire each billing cycle and
go unused. The credits cover the Claude API, the Batch API, and the Claude Agent SDK, including
`claude -p` run with an API key. They don't cover interactive Claude Code sessions. Docs work is
the workstation's largest consumer of model time, and it's rarely urgent. Geoff: "I'm usually not
in a hurry with docs development."

The goal is to move the drafting and review half of docs work onto those credits without lowering
quality. Geoff set the bar: "current quality is the base standard. I won't shed any tears if this
new system improves it!"

## Outcome

Claude Code still plans each page on Geoff's plan: page inputs, the page plan, the plan read, and
the framing record. A new Go tool, `drafter`, takes each planned page from there. It drafts the
page, gates it, runs the review seats, redrafts, and runs the final read, with every model call a
batched Messages API request billed to the credits. Each page ends accepted or escalated, with a
record of every request, finding, resolution, and cost.

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
- Every escalation traced upstream of drafting: two facts that contradict another page, a fact
  that overclaims, and two plan gaps a reader would hit. The pipeline surfaced them and refused to
  invent facts to cover them. The October 7 chain run escalated all five of its pages for causes
  of the same kinds.
- A whole-page redraft ignored an explicit blocking finding. It received the finding and a
  proposed sentence, and regenerated the page without it. An edit-contract redraft on the same
  findings resolved each one by number and changed nothing else.

The spike's harness lives in the session scratchpad and is throwaway. Its recorded requests and
responses become test fixtures.

## Scope

Geoff decomposed the initiative into four sub-projects, each with its own spec, plan, and build:

1. **This spec:** drafter's `page` mode on cairn, the YAML plan format, and the plan checks.
2. Issue capture and the nightly run: `issue file`, `issue list`, `run`, a systemd user timer, and
   a registry of participating repos. Issues are GitHub issues labelled `docs-fix` on each
   project's own repo (Geoff, 2026-10-12).
3. Workstation rollout: a `docs-fix` skill, the tooling manifests, `claude-infra` placement, and
   per-repo adoption.
4. Docs bootstrapping for repos with no docs, later and repo by repo.

Out of scope here: figure verification (a page with a figure stays on the chain), the issue queue,
the timer, and any repo but cairn.

## The tool

`drafter` is a standalone Go module, `github.com/glw907/drafter`, at `~/Projects/drafter`. Geoff
chose the name, after checking that the one prior `drafter` (Apiary's archived API Blueprint
parser) is disabled in Homebrew.

The layout follows the go-conventions skill. `cmd/drafter/` holds only the cobra wiring.
`internal/` holds one package per concern:

| Package | Job |
|---|---|
| `assemble` | Builds each seat's request: the prompt, the agent definition as the system prompt, every repository file the prompt names, command outputs, and the source excerpt behind each cited fact. |
| `prompts` | Runs a project's prompts module in goja and returns each seat's prompt. |
| `batch` | Submits and polls Batch API requests, computes cost, and keeps the ledger. |
| `pipeline` | The per-page state machine and its stop rules. |
| `edits` | The edit contract: its schema, applying edits, and refusing a bad answer. |
| `gate` | Runs the project's gate and index-link commands, and extracts each failing component's section of the gate log. |
| `plan` | Parses and validates YAML plans and runs the plan checks. |

Its commands for this sub-project:

| Command | Does |
|---|---|
| `drafter page <handoff>...` | Runs each handed-off page through the pipeline. `--dry-run` assembles the first stage's requests, prints their sizes and estimated cost, and submits nothing. `--resume <run>` continues a stopped run. |
| `drafter check-plan <file>` | Validates a plan's syntax and schema and runs the plan checks, printing errors as `file:line` with the fix. |
| `drafter check-prompts` | Loads the project's prompts module, confirms every seat builder exists, and renders each against fixture inputs. |
| `drafter spend` | Prints the current billing cycle's spend by repo and seat. |

Nothing in drafter is cairn-specific. A project opts in with a `drafter.toml` at its root, which
names the gate and index-link commands, the prompts module, each seat's agent definition, model,
and effort, the facts directory and its bullet format, the register sections each track reads, and
the caps.

## Seat prompts

The chain's prompts are code, not templates: 28 builder functions, 665 lines, and 109 branches or
loops, varying by page type, round, narrowed reads, and outline. They change often. The chain
script took 28 commits in the month before this spec. A copy would drift within days.

The prompts stay in JavaScript, and drafter runs them in-process with goja
(`github.com/dop251/goja`). Geoff chose this over Go templates because agents edit the prompts
often and are most fluent in JavaScript. A goja probe ran the entire chain script and built the
drafter prompt byte-identical to Node's output, in 31 milliseconds.

A prompts module is plain JavaScript that exports one pure function per seat. Each takes a context
object (the page, its inputs, the round, the findings, a narrowed read's diff) and returns a string.
It does no I/O and keeps no global state. goja's runtime has no filesystem, network, or process
access by default, so a module can compute text and nothing else.

During the beside-the-chain period, `docs-page-chain.js` gains that export beside its own use of the
same builders, so there is one source of truth. `drafter check-prompts` runs in the dotfiles gate so
that a chain edit that breaks drafter fails at commit time. At cutover, the back-half builders move
into a module in cairn's repo, and the chain keeps its planning half. drafter also embeds a stock
module on the base Google register for a project with no voice of its own.

## The handoff

The chain gains a `backHalf` argument. With `backHalf: "drafter"`, the Workflow stops after framing
and returns one handoff record per page: the page config, the page inputs with the plan's and the
framing's dispositions applied, and the plan and framing paths. The planning session writes the
records into the worktree and runs `drafter page` on them, in the foreground or queued for the
night. With `backHalf` unset, the chain runs as it does today, and that is the fallback (Geoff,
2026-10-12: beside the chain first, cutover after a pilot).

## The pipeline

Each page runs these stages, with the chain's rules:

1. **Plan check.** `check-plan` runs on the page's plan. A failing plan escalates to the planning
   session before any drafting spend.
2. **Draft.** One batched call returns the page and its brief. The gate runs, with up to two
   gate-fix turns in the same conversation. Each turn receives every failing component's section of
   the gate log, not its tail.
3. **Coverage check.** The plan's mechanical items are checked against the page and brief. Then one
   batched coverage read quotes the sentence that satisfies each `claim`, `handoff`, and `reason`
   item, or reports it missing. Missing items join round 1's findings.
4. **Round-1 reads.** The structural edit, register editor, and fact read run in one batch.
5. **Redraft.** If any read returned fix, one edit-contract redraft, then the gate, then the
   coverage check again.
6. **Round-2 reads.** Only the seats that returned fix, narrowed to the redraft's diff.
7. **Final reader read.** If it returns fix, one edit-contract redraft, scoped re-reads by the
   register editor and fact read, and a retest.

A second fix verdict escalates, a red gate after the fix turns escalates, and there is no third
round. An escalated page keeps its whole record.

### Input assembly

Each seat receives its prompt, its agent definition as the system prompt, every
repository file the prompt names, the output of each command the seat would have run (Vale, open
option-map rows, the round-2 diff), and the code excerpt each cited fact's `Source:` pointer names.
A note tells the seat that files are inlined and that any edit it would make becomes a finding. The
final reader gets only the page, with the job held back until its step 3, to keep the cold read.

### The edit contract

Every redraft returns exact edits, each a file (`page` or `brief`), an old
span that occurs exactly once, and its replacement, plus one resolution per numbered finding:
`edited` with the indexes of its edits, or `declined` with a reason. A blocking finding may be
declined only when it is factually wrong about the page. drafter refuses an answer that leaves a
blocking finding unresolved, names an old span that occurs zero or several times, or breaks the
brief's JSON. A refused answer gets its problems back, up to two retries.

### The agentic exception

A fact read that needs code its excerpts don't cover reports that as a
finding, and the page escalates. A `claude -p` fact read on the key is the remedy if the pilot shows
the need. The first build leaves it out, since the spike never needed it.

## The plan format

The plan becomes one YAML file, `<page>.plan.yaml`, validated against a JSON Schema that drafter
publishes. It holds the argument, the order and its reasons, the introduction, each section with its
items, the dispositions, and the drafting constraints. Prose fields use `|` block scalars.

Geoff asked for the format that gives the best and most predictable outcome and is easiest for
Claude Code to work with. YAML won on editing: Claude Code writes the plan with Write and revises it
with Edit, and YAML keeps prose readable with no escaping to match. Its parsing traps (a colon or `#`
in unquoted prose, indentation, words read as booleans) are closed by validation in the writer's
loop: the plan step ends by running `drafter check-plan` until it reports no errors, and the plan
read starts only on a clean plan. JSON was rejected for unreadable prose, markdown with an item
grammar for drift from an invented syntax, and TOML for awkward nesting.

Each plan item has an id, a section, and a kind:

| Kind | Pins down | Checked by |
|---|---|---|
| `fact` | A fact id placed in a section | Mechanically: the brief cites it in that section |
| `sentence` | A load-bearing sentence, `verbatim` or `claim` | Verbatim mechanically, claim by the coverage read |
| `link` | A target path and anchor | Mechanically: the page links it in that section |
| `handoff`, `reason` | A section's closing turn, or a "why" that must survive | The coverage read |
| `step` | A task step, with `requires` and `produces` state | The plan check |
| `failure` | A failure a step can cause, its symptom, and the item that handles it | The plan check |

The plan check runs four tests. The reader-state walk confirms every step's `requires` is produced
by an earlier step or listed as a precondition. The recovery matrix confirms every step marked
`canFail` has a `failure` item and that every handler exists. The link and fact test confirms every
target and anchor exists on disk and every placed fact is citable. A batched consistency read checks
the placed fact bullets against each other and against the headings of every linked page.

Each test answers a failure the evidence shows. The plan reads of the October 7 run caught
reader-state gaps by hand, such as a page with no deploy step. The spike's final reader found two
recovery gaps the plan never listed. Both of the exemplar page's escalations were fact conflicts a
consistency read would have caught before drafting. Three of the five October 7 escalations were
plan-placed content that a redraft compressed away, which the coverage check targets.

In cairn, the chain's plan prompt writes YAML and runs `check-plan`, and the plan-mode structural
read gains the state and recovery checks. An existing markdown plan still runs, with a warning and
without the plan-dependent checks.

## Operations

### Caps

$10 per page, $40 per `page` run, and a $160 ceiling per billing cycle, which is 80% of
the $200 credit (Geoff, 2026-10-12). All three live in `drafter.toml`. Before each submission,
drafter estimates input cost with the token-counting endpoint, so a cap stops a stage before the
spend. A page at its cap escalates with its record.

### The ledger

Each batch result appends a line to `~/.local/state/drafter/ledger.jsonl`: date,
repo, page, seat, model, tokens, and cost. The ceiling resets on the billing-cycle date set in
config, since that's when the credits refresh.

### A server-side backstop

drafter uses its own key in its own Console workspace, with the
workspace spend limit set to $160, so a fault in drafter's accounting can't overspend. The key goes
through the secrets flow (`secret-receive`, then the age store). drafter reads `ANTHROPIC_API_KEY`
from the environment, never prints it, and never uses OAuth, so it can't bill Geoff's plan.

### Caching

Prompt caching applies only where a prefix is reused: the gate-fix and contract-retry
continuations. The spike showed a one-hour cache write on a single request doubles its input cost.

### Records

Each page run writes its requests, responses, edit-contract answers, gate excerpts,
and a `record.json` (stages, verdicts, findings, resolutions, cost, final status) under
`~/.local/state/drafter/runs/<repo>/<date>-<page>/`, outside the repo. Records older than 30 days
are pruned. The Batch API's own results expire after 29 days.

### Resume

State is written after every stage, including the ID of any batch in flight. Batches
run on even if drafter dies, so `--resume` reattaches to an in-flight batch instead of paying for it
twice.

### Concurrency

drafter submits every page's current stage and runs one sequential poll loop over
all in-flight batches. It starts no goroutines. Gates run one at a time, as `cairn-run-gate` takes a
lock.

### Failures

A server-side request error is retried once. An invalid request or a model refusal
escalates the page with its reason.

### Models

Every seat runs on `claude-opus-5-5`: the drafter and redrafts at high effort, the
review seats at medium, the coverage and consistency reads at low. A seat's model changes only in
config, on pilot evidence.

## Testing

Unit tests are table-driven and use the standard library only.

- The edit contract: applied edits, a refused span count, a refused unresolved blocking finding,
  a refused broken brief, and an accepted declined advisory.
- The plan checks: an unmet `requires`, a failing step with no handler, a handler that doesn't
  exist, a missing anchor, and a placed `[rejected]` fact.
- Input assembly: path detection in prompts, inlining, and source excerpts from both
  `path:line` and `path#declaration` pointers.
- Gate log extraction: failing sections from a real log, including the spike's provenance case.
- Caps and the ledger: a stage refused at each cap, and the cycle resetting on the billing date.
- The pipeline state machine: every transition and stop rule, against a fake batch client whose
  fallible methods each carry an error field.

Parsing tests use the spike's recorded responses as fixtures. End-to-end tests build the binary and
run `check-plan`, `check-prompts`, and `page --dry-run` on fixtures. A `make smoke` target runs one
real Haiku 5.5 batch before a release; it stays out of `make check` because it spends money.

## The pilot

The next cairn docs pass runs on drafter, with the chain's back half as the fallback. Cutover needs
all four:

1. Geoff accepts every page drafter accepted, after ordinary fixes, in the pass's PR. A blind
   grader reads each against the register as a second opinion.
2. Every escalation's record names a cause in the inputs: a plan gap, a fact conflict, or a missing
   fact. A pipeline fault, such as a dropped finding or a broken edit, counts against cutover.
3. The average cost stays at or below $5 a page, and no page reaches the $10 cap.
4. drafter's ledger matches the Console's credit usage within 5%, and none of its spend reaches the
   plan.

The pilot covers at least five pages, including two task guides and one concept page. Cutover is
Geoff's call. It moves the back-half prompts into cairn's repo and deletes the chain's back half
and the `backHalf` flag.

## drafter's own docs

The repo carries a README, the plan schema reference, the prompts-module contract, and the
`drafter.toml` reference, written to the Google developer documentation style.

## Open items

- Whether the Admin API can set a workspace spend limit, or the backstop takes a one-time Console
  step. To be verified during the build.
- Whether the coverage read moves to Haiku 5.5, decided on the pilot's cost and accuracy data.
- Two findings from the spike for cairn: the published `choose-an-ai-posture` page lacks a
  `site-facts.json` regeneration step, and its route snippet fails typechecking. They become the
  first `docs-fix` issues once sub-project 2 lands, or a direct fix sooner.
