# drafter pass 4 plan: page parts

Design: `docs/superpowers/specs/2026-10-13-drafter-completion-design.md`, pass 4, approved by Geoff
on 2026-10-13. Spec: `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, sections "Input
assembly", "The edit contract", "Coverage", "Projects without facts", "Shared worktree", "The gate",
"The plan format" (the consistency read's answer), and "Testing" (the edit contract, coverage, input
assembly, gate, and projects-without-facts rows, as this plan assigns them).

## Outcome

drafter has every part a page passes through, each tested on its own: `assemble` turns a rendered
prompt into a complete API request with the right files, command outputs, and source excerpts;
`edits` applies or refuses an edit-contract answer; `coverage` checks a page against its plan and
verifies the coverage read's quotes; `gate` runs a project's gate and says which failures belong to
which page. Pass 5 wires them into the pipeline.

## Shape

- Risk class: `ordinary` for every task. No `live-account` flag: nothing calls the API. P4.3 runs
  cairn's docs gate locally on a scratch worktree to regenerate logs; nothing there is committed or
  pushed.
- Repo: `~/Projects/drafter` (`glw907/drafter`). The executor launches from the main checkout and
  works in the worktree `EnterWorktree` creates (name `p4-page-parts`); pair subagents get worktrees
  of their own.
- Gate, from the worktree root: `DRAFTER_DIR="$PWD" bash ~/.dotfiles/scripts/drafter-gate.sh`.
  Full-suite home: that gate, once, on the close head. No CI.
- Clock file: the pass worktree's git dir.
- Path estimate: 205 minutes. P4.1 and P4.2 as a pair (75), P4.3 and P4.4 as a pair (110), Close
  (20). The design's estimate is 180, so the path is 1.1 times it, inside the 3x line (540).
- Standing approvals: the plan proceeds within 3x. The pass is `ordinary`, so it merges its own PR
  under pass-core's exception when the close review accepts and "Found, not done" is empty. A clock
  stop has no standing answer, so it stops as pass-core says.
- No new dependency.

## Interfaces

Consumes: from pass 1, `config.Config`, `config.Gate`, `config.Seat`, `atomicfile.WriteFile`; from
pass 2, `batch.Request`, `batch.Message`; from Pass 0 and F1, `plan.Plan`, `plan.Section`,
`plan.Item`, `plan.Facts`, `plan.Fact`, `plan.LoadFacts`, and the slugger behind check-plan's anchor
check.

Creates, for pass 5. Names and purposes are fixed; a signature change that keeps every caller
compiling is allowed and stated in the PR body.

`internal/edits`

- `type Finding struct`: `N int` (its number, unique within a page's exchange), `Seat`, `Location`,
  `Text`, `Rewrite string`, `Blocking bool`.
- `type Edit struct`: `File` (`page` or `brief`), `Old`, `New string`.
- `type Resolution struct`: `Finding int`, `Status` (`edited` or `declined`), `Edits []int`, `Reason
  string`.
- `type Answer struct`: `Edits []Edit`, `Resolutions []Resolution`.
- `Schema() json.RawMessage`: the answer's JSON Schema, sent as structured output.
- `Instructions() string`: the contract as the model reads it, appended to every redraft and
  gate-fix turn.
- `Render(fs []Finding) string`: the numbered findings text a redraft answers, each with its number,
  seat, blocking flag, location, text, and rewrite. Pass 5 puts it in the context's `findings`.
- `Apply(page, brief string, fs []Finding, prior []Resolution, a Answer) (Applied, error)`: applies
  the edits in order and checks the spec's refusal rules over the union of `prior` (the resolutions
  of earlier answers that were applied) and `a`'s, a later resolution of a finding overriding an
  earlier one. `Applied` holds the new `Page`, `Brief`, and `Resolutions` (the union). The error is
  a `*Refusal` whose `Problems []string` go back to the model verbatim. A refused answer applies
  nothing and adds nothing to the union.
- `Declined(fs []Finding, rs []Resolution) []DeclinedFinding`: each blocking finding resolved
  `declined`, with its reason, for that seat's next read.

`internal/coverage`

- `Normalize(s string) string`: whitespace collapsed; Markdown emphasis and code delimiters removed.
- `type Brief struct`: the sentence-to-fact brief drafter reads, `{ "page": ..., "sentences": [{
  "text": ..., "id": <string or list of strings> }] }`, the shape the chain's drafter writes.
- `type Miss struct`: `Item`, `Section`, `Kind`, `Reason string`.
- `Check(p *plan.Plan, page, brief []byte, facts bool) ([]Miss, error)`: the mechanical checks
  (fact, verbatim sentence, link), `fact` items skipped when `facts` is false. The error is a brief
  that isn't valid JSON.
- `Prompt(p *plan.Plan, page []byte) string` and `Schema() json.RawMessage`: the coverage read's
  request text, listing every `claim` sentence, `handoff`, and `reason` item with its id, section
  heading, and text, and the page itself; the answer is `{ "items": [{ "id": ..., "quote": ... }]
  }`, an empty quote meaning missing.
- `Verify(p *plan.Plan, page, answer []byte) (misses []Miss, faults []string, err error)`: each
  listed item absent from the answer or answered empty is a miss; each quote not found, after
  normalization, inside its item's section is a miss and a fault. The error is an answer that doesn't
  parse.

`internal/gate`

- `Command(tmpl, page, brief, slug, baseline string) string`: substitutes the four placeholders.
- `type Section struct`: `Name string`, `Lines`, `Failing []string`.
- `type Result struct`: `Green bool`, `Log string` (the log file's path), `Sections []Section`,
  `Unparsed bool`, `Tail []string` (the log's last 60 lines when unparsed).
- `Run(ctx, g config.Gate, root, command, logPath string) (Result, error)`: one gate run under the
  configured protocol. `ErrInfra` wraps the `cairn-run-gate` vanish result.
- `(Result) ForPage(page, brief string) (own []Section, foreign bool)`: the sections with a failing
  line naming the page or its brief, and whether the gate is red with none naming either. An
  unparsed red log counts as the page's own, its tail standing as the one section, since drafter
  can't show it is foreign.

`internal/assemble`

- `type Answer string`: which answer a request asks for: `draft`, `edits`, `read`, `reader1`,
  `reader2`, `coverage`, or `consistency`.
- `type Input struct`: `Seat string`, `Answer Answer`, `Config *config.Config`, `Prompt string`
  (the module's rendering, or drafter's continuation text), `History []batch.Message` (earlier turns
  of a continuation), `Page`, `Brief string` (repo-relative), `Slug`, `Baseline string`, `Facts
  *plan.Facts` (nil without a facts store), `FactIDs []string`, `Declined
  []edits.DeclinedFinding`, `CustomID string`.
- `Build(in Input) (batch.Request, error)`: the seat's model, effort, `max_tokens`, and system
  prompt (its agent definition's body after the front matter, empty with no `agent`); the answer's
  schema and its output contract text; the inlining note; the files, command outputs, and excerpts.
- `ConsistencyPrompt(p *plan.Plan, facts *plan.Facts, root string) (string, error)` and the
  consistency answer `{ "conflicts": [{ "facts": [...], "with": "<fact id or page#heading>",
  "conflict": "..." }] }`.
- The answer schemas: `draft` is `{ page, brief, friction }` with `brief` a string holding JSON;
  `read` is `{ verdict, findings: [{ location, finding, rewrite, blocking }], summary, friction }`;
  `reader1` is `{ paraphrase, summary }`; `reader2` is `read`'s; `edits`, `coverage`, and
  `consistency` are the schemas above. `friction` is an optional list of strings in each.

`internal/plan` gains, for `assemble`: `Fact.Text` (the bullet's claim text), `Fact.Sources
[]string` (the pointers its `Source:` part names), and `(*Facts) Get(id string) (Fact, bool)`
(true only when exactly one bullet holds the id).

## Out of scope

The stages, budgets, stop rules, records, and resume (pass 5); building seat contexts (pass 5);
prompt caching; and the agentic fact read (the spec's "The agentic exception").

## Tasks

Every task starts by invoking `go-conventions`. Fixtures are synthetic; the spike's recorded files
no longer exist, so each fixture the spec ties to the spike is a synthetic one modeled on its
description.

### P4.1 The edit contract (70 min, ordinary)

- Outcome: `internal/edits` as listed.
- Files: `internal/edits/` with tests and `testdata/`.
- Acceptance, the spec's edit-contract row as assigned here, each refusal with the exact problem
  text and a clean twin:
  - One row per refusal rule: an old span found zero times, and several times; a `file` other than
    `page` or `brief`; an edit whose old and new text are equal; an edit no resolution claims; a
    resolution naming an edit index that doesn't exist, and one naming a finding number that doesn't
    exist; a finding, blocking and advisory, with no resolution, and one with two; a blocking finding
    resolved `edited` with no edits; a brief that isn't valid JSON after the edits.
  - Edits apply in order, and an old span that occurs twice in the original but once after an
    earlier edit is accepted.
  - Resolutions accumulate: an applied answer resolves findings 1 to 3, the gate then adds finding 4,
    and a second answer that resolves only 4 is accepted against the union.
  - A declined advisory finding is accepted; a declined blocking finding is accepted and returned by
    `Declined` with its reason.
  - `testdata/reader-redraft.answer.json`, a synthetic answer modeled on the spike's
    `reader-redraft-1.answer.json` (several reader findings, each resolved by number, with edits to
    both the page and the brief), is accepted against its findings and page.
- Test: the gate.
- Pair: with P4.2.

### P4.2 Coverage (75 min, ordinary)

- Outcome: `internal/coverage` as listed. A brief sentence is located on the page by its normalized
  text, and its section is the nearest heading above it; a sentence that can't be located is a miss,
  never skipped. A link counts when the page links the item's target (resolved from the page's
  directory, anchor included) inside the section.
- Files: `internal/coverage/` with tests and `testdata/` (a synthetic page, brief, plan, and coverage
  answers).
- Acceptance, the spec's coverage row and the coverage half of the projects-without-facts row, each
  with its twin: a verbatim item present and absent; a fact cited in its section and in another; a
  link in and out of its section; a brief sentence that differs from the page only in a code span
  (located); a brief sentence not on the page (a miss); `fact` items skipped when `facts` is false; a
  coverage answer whose quote isn't on the page (a miss and a fault); a quote that is on the page but
  in another section (a miss and a fault); an item the answer leaves out (a miss); a brief that
  isn't JSON (the error).
- Test: the gate.
- Pair: with P4.1.

### P4.3 The gate and its regenerated logs (90 min, ordinary)

- Outcome: `internal/gate` as listed, following the spec's "The gate" and "Shared worktree":
  - `plain` runs the command through `/bin/sh -c` from the root, writes combined output to the log,
    and reads the exit code.
  - `cairn-run-gate` execs `cairn-run-gate '<command>' <logPath>`, with `CAIRN_GATE_LANE` set from
    `gate.lane` and `RUN_GATE_IF_BUSY` removed from the environment. On exit 75 it re-issues the
    same command until the log holds a `gate exit:` line, reads the result from that line, and
    parses the whole log. `gate exit: 1 (vanished 3 times)` returns `ErrInfra`. It never passes
    `--receipt`.
  - With `gate.section_pattern`, a line matching it opens a section named by its first capture
    group; without it the log is one section. With `gate.failure_pattern`, matching lines in a red
    log are failing; without it every line of a red log is. A red log with a section pattern but no
    matching line is unparsed.
  - The logs: the spike's `gate-logs/` are gone, so regenerate three in a scratch cairn-cms worktree
    (`git -C ~/Projects/cairn-cms worktree add` on a scratch branch from `origin/main`, then
    cairn-pass's setup command): a green run of `npm run check:docs-gate -- --page <p> --brief <b>`
    on a published extend page; a run with a deliberate `check:provenance` failure on that page; and
    a run where a second page carries a broken link while the first page is gated. Run each through
    `CAIRN_GATE_LANE=light cairn-run-gate '<command>' <log>`. Scrub each log: workstation paths become
    `/work/project`, and cairn's page and brief names become synthetic ones, consistently. Remove the
    scratch worktree and branch after; nothing in cairn-cms is committed.
  - Record in the PR body the section and failure patterns that parse those logs, for cairn's
    `drafter.toml` in pass 5.
- Files: `internal/gate/` with tests, `internal/gate/testdata/logs/` (the three scrubbed logs) and
  `internal/gate/testdata/bin/` (a fake `cairn-run-gate` script the tests put first on `PATH`).
- Acceptance, the spec's gate row: a plain gate's exit 0 and nonzero, each with and without the two
  patterns; the failing sections of the regenerated provenance log, attributed to its page; an
  unparseable log (unparsed, tail kept, counted as the page's own); the two-page log, where page B's
  broken link makes page A's result foreign; under the fake `cairn-run-gate`, exit 75 then a result,
  the vanish line (`ErrInfra`), the log path passed as the second argument, `CAIRN_GATE_LANE` set from
  `gate.lane`, and `RUN_GATE_IF_BUSY` absent though the test's environment sets it. `Command`
  substitutes all four placeholders. Nothing under `testdata/` names a workstation path.
- Test: the gate.
- Pair: with P4.4.

### P4.4 Input assembly (110 min, ordinary)

- Outcome: `internal/assemble` as listed, plus the `internal/plan` additions. Following the spec's
  "Input assembly":
  - The note opens the first user turn: files are inlined, a command whose output isn't inlined is
    not to be run, and any edit the seat would make, or any check it couldn't make, becomes a
    finding.
  - Files: every path the rendered prompt names that `git ls-files` lists in the root is inlined
    whole, each in one block headed by its path; an out-of-repo path is inlined when an
    `inline_files` entry names it or a directory above it, with `~` expanded on both sides. A named
    path that is neither stays out. A file over 256 KiB becomes a `not inlined: N bytes` block; an
    allowed path that doesn't exist becomes `not inlined: missing`.
  - Commands: each command in the seat's `inputs` runs from the root, with placeholders
    substituted, just before the request, and its output is inlined under the command text whatever
    its exit status, with a nonzero status noted (`diff` exits 1 when it finds a change). A command
    naming `{baseline}` runs only when `Baseline` is set.
  - Source excerpts, when `Facts` is set, for each id in `FactIDs`: `path:N` yields lines N-10 to
    N+10; `path:A-B` yields A-5 to B+5; a comma list yields each; `path#name` yields 5 lines before
    to 40 after the declaration of `name` (its last dotted segment), found by the spec's declaration
    patterns and never by a mere mention; a bare file is inlined whole up to the size limit; a
    directory yields `no excerpt: directory`; anything else yields `no excerpt: prose`.
  - Without a facts store, the `fact` seat's request inlines each tracked path the page or its brief
    names, under the same limit, in place of excerpts.
  - The final reader: `reader1` holds exactly one file block, the page, whatever paths its prompt
    names; `reader2` continues that conversation with the module's turn-2 prompt.
  - `coverage` and `consistency` requests take their prompt as built and inline nothing more.
  - `Declined` findings, with their reasons, follow the prompt in a block telling the seat to accept
    each decline or raise the finding again.
- Files: `internal/assemble/` with tests and `testdata/` (a synthetic repo with Go and TypeScript
  sources, a facts file, an agent definition with front matter); `internal/plan/facts.go` and its
  test.
- Acceptance, the spec's input-assembly row and the fact-read half of the projects-without-facts
  row, each with its twin: an untracked path stays out; an allowed out-of-repo path is in; an
  oversized file is a `not inlined` block; excerpts for `path:line`, `path:A-B`, a bare file, a
  directory, a prose source, and a `#name` whose name is imported above its declaration (the excerpt
  holds the declaration, not the import); the reader's first turn holds exactly one file block, the
  page, and no job text although its prompt names the outline; the fact read without facts inlines
  the tracked files the page names; a command with `{baseline}` is skipped without a baseline and
  run with one; a declined blocking finding and its reason appear in the next read's request; the
  system prompt is the agent definition's body without its front matter. `Fact.Text`,
  `Fact.Sources`, and `Get` have their own rows in `internal/plan`.
- Test: the gate.
- Pair: with P4.3.

### Close (20 min)

The gate, once, on the close head. One whole-branch `diff-reviewer` run against `main`, with
go-conventions for `*.go`. One batched fix chain if needed, then the gate again. `gitleaks git` over
the branch history, and a grep of `testdata/` for `/var/home`, `/home/`, and `glw907` that finds
nothing. Push the branch to `glw907/drafter` and open the PR: `## Brief`, what landed, the review
verdict, cairn's gate patterns from P4.3, the score rows (the Work and review row puts the
205-minute path beside the actual), and "Found, not done" with a proposed disposition each.

When the review accepted and "Found, not done" is empty, merge with `gh pr merge <n> -R
glw907/drafter --merge`, then `git -C ~/Projects/drafter pull --ff-only` and `make -C
~/Projects/drafter install`. Otherwise stop at PR-ready and name the PR in the final message; the
conductor takes it to Geoff.

## Later

- A setting for the inline size limit, if a project's sources outgrow 256 KiB per file.
