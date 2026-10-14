# drafter pass 4 plan: page parts

Design: `~/.dotfiles/docs/superpowers/specs/2026-10-13-drafter-completion-design.md`, pass 4,
approved by Geoff on 2026-10-13. Spec:
`~/.dotfiles/docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, sections "Input
assembly", "The edit contract", "Coverage", "Projects without facts", "Shared worktree", "The gate",
"The plan format" (the consistency read's answer), and "Testing" (the edit contract, coverage, input
assembly, gate, and projects-without-facts rows, as this plan assigns them). Fold record:
`~/.dotfiles/docs/superpowers/research/2026-10-13-drafter-completion-plan-fold.md`.

## Outcome

drafter has every part a page passes through, each tested on its own: `assemble` turns a rendered
prompt into a complete API request with the right files, command outputs, and source excerpts;
`edits` applies or refuses an edit-contract answer; `coverage` checks a page against its plan and
verifies the coverage read's quotes; `gate` runs a project's gate and says which failures belong to
which page. Pass 5 wires them into the pipeline.

## Shape

- Risk class: `ordinary` for every task. No `live-account` flag: nothing calls the API. Geoff's
  ruling (design, Technical notes 8): `assemble` stays `ordinary` on the footing of pass 1's config
  task; its path-safety rows (`..`, symlinks, separator boundaries) are written and committed before
  the code, and named in the close review's dispatch.
- Repo: `~/Projects/drafter` (`glw907/drafter`). The executor launches from the main checkout and
  works in the worktree `EnterWorktree` creates (name `p4-page-parts`); pair subagents get worktrees
  of their own, dispatched on `sonnet` at `medium` with the `description` `p4-page-parts task <n>`.
- Gate, from the worktree root: `DRAFTER_DIR="$PWD" bash ~/.dotfiles/scripts/drafter-gate.sh`.
  Full-suite home: that gate, once, on the close head. No CI.
- Clock file: the pass worktree's git dir.
- Path estimate: 285 minutes. P4.1 and P4.2 as a pair (85), P4.3 in the session (35), P4.4 and P4.5
  as a pair (140), Close (25). The design's estimate is 180, so the path is 1.6 times it, inside the
  3x line (540).
- Standing approvals: the plan proceeds within 3x. The pass is `ordinary`, so it merges its own PR
  under pass-core's exception when the close review accepts and "Found, not done" is empty. A clock
  stop has no standing answer, so it stops as pass-core says.
- No new dependency.

## Interfaces

Consumes: from pass 1, `config.Config`, `config.Gate`, `config.Seat`, `atomicfile.WriteFile`; from
pass 2, `batch.Request`, `batch.Message`; from Pass 0 and F1, `plan.Plan`, `plan.Section`,
`plan.Item`, `plan.Facts`, `plan.Fact`, `plan.LoadFacts`.

Creates, for pass 5. Names and purposes are fixed; a signature change that keeps every caller
compiling is allowed and stated in the PR body.

`internal/edits`

- `type Finding struct`: `N int` (its number, unique within a page's exchange), `Seat`, `Location`,
  `Text`, `Rewrite string`, `Blocking bool`.
- `type Edit struct`: `File` (`page` or `brief`), `Old`, `New string`.
- `type Resolution struct`: `Finding int`, `Status` (`edited` or `declined`), `Edits []int` (0-based
  indexes into the same answer's `edits`), `Reason string`.
- `type Answer struct`: `Edits []Edit`, `Resolutions []Resolution`.
- `Schema() json.RawMessage`: the answer's JSON Schema, sent as structured output; its descriptions
  state that edit indexes are 0-based into the same answer.
- `Instructions() string`: the contract as the model reads it, appended to every redraft and
  gate-fix turn, naming the index base.
- `Render(fs []Finding) string`: the numbered findings text a redraft answers, each with its number,
  seat, blocking flag, location, text, and rewrite. Pass 5 puts it in the context's `findings`.
- `Apply(page, brief string, fs []Finding, prior []Resolution, a Answer) (Applied, error)`: applies
  `a`'s edits in order. These rules check the current answer alone: each old span occurs exactly
  once in the text as earlier edits left it; `file` is `page` or `brief`; old and new differ; every
  edit is claimed by a resolution; every edit index exists in this answer; every finding number
  exists; no finding has two resolutions in this answer; a blocking finding resolved `edited` names
  an edit; the brief is valid JSON after the edits. Over the union of `prior` and `a`'s resolutions,
  a later resolution of a finding overriding an earlier one, every finding has a resolution.
  `Applied` holds the new `Page`, `Brief`, and `Resolutions` (the union). The error is a `*Refusal`
  whose `Problems []string` go back to the model verbatim. A refused answer applies nothing and adds
  nothing to the union.
- `Declined(fs []Finding, rs []Resolution) []DeclinedFinding`: each blocking finding resolved
  `declined`, with its reason, for that seat's next read.

`internal/coverage`

- `Normalize(s string) string`: whitespace collapsed; Markdown emphasis and code delimiters removed.
- `type Brief struct`: the sentence-to-fact brief drafter reads, `{ "sentences": [{ "text": ...,
  "id": <string or list of strings> }] }`, the shape the chain's drafter writes. Unknown fields
  (cairn's `page`, `cuts`, `local`) are ignored, and an `id` of `"no-claim"` cites no fact.
- `type Miss struct`: `Item`, `Section`, `Kind`, `Reason string`.
- Sections: a page heading belongs to a plan section when its normalized text equals that section's
  normalized heading, matched in plan order; a heading that matches no plan section belongs to the
  planned section above it, so an unplanned `####` never splits a section. A text's section is the
  planned section it falls in. A plan section whose heading isn't on the page makes each of its
  items a miss with the reason `heading not found`.
- `Check(p *plan.Plan, page, brief []byte, facts bool) ([]Miss, error)`: the mechanical checks
  (fact, verbatim sentence, link), `fact` items skipped when `facts` is false. A link counts when the
  page links the item's target inside the section: a repo path resolved from the page's directory,
  anchor included; a same-page `#anchor` matched as written; a URL matched exactly. The error is a
  brief that isn't valid JSON.
- `Prompt(p *plan.Plan, page []byte) string` and `Schema() json.RawMessage`: the coverage read's
  request text, listing every `claim` sentence, `handoff`, and `reason` item with its id, section
  heading, and text, and the page itself; the answer is `{ "items": [{ "id": ..., "quote": ... }]
  }`, an empty quote meaning missing.
- `Verify(p *plan.Plan, page, answer []byte) (misses []Miss, faults []string, err error)`: each
  listed item absent from the answer or answered empty is a miss; each quote not found, after
  normalization, inside its item's section is a miss and a fault. The error is an answer that doesn't
  parse.

`internal/gate`

- `Command(tmpl, page, brief, slug, baseline string) string`: substitutes the four placeholders
  where they aren't preceded by `$` (pass 1's rule), each value single-quoted for POSIX `sh` with an
  embedded `'` written as `'\''`.
- `Env(c *config.Config) []string`: the process environment without the variable `c.KeyEnv` names,
  every `ANTHROPIC_*` variable, and `RUN_GATE_IF_BUSY`. Every command drafter runs (the gate, the
  index-link command, each seat input) gets this environment, so no key reaches a child process,
  its log, or a prompt.
- `type Section struct`: `Name string`, `Lines`, `Failing []string`.
- `type Result struct`: `Green bool`, `Log string` (the log file's path), `Sections []Section`,
  `Unparsed bool`, `Tail []string` (the log's last 60 lines when unparsed).
- `Run(ctx, g config.Gate, env []string, root, command, logPath string) (Result, error)`: one run
  under the configured protocol. `ErrInfra` wraps the `cairn-run-gate` vanish result. Pass 5 runs
  the index-link command through it with `Protocol` `plain`.
- `(Result) ForPage(page, brief string) (own []Section, foreign bool)`: the sections with a failing
  line naming the page or its brief, the path bounded by the line's start, whitespace, or a
  character that can't be part of a path on its left (so `docs/x.md` doesn't match inside
  `examples/docs/x.md`), and whether the gate is red with none naming either. An unparsed red log
  counts as the page's own, its tail standing as the one section, since drafter can't show it is
  foreign.

`internal/assemble`

- `type Answer string`: which answer a request asks for: `draft`, `edits`, `read`, `reader1`,
  `reader2`, `coverage`, or `consistency`.
- `type Input struct`: `Seat string`, `Answer Answer`, `Config *config.Config`, `Prompt string`
  (the module's rendering, or drafter's continuation text), `History []batch.Message` (earlier turns
  of a continuation), `Page`, `Brief string` (repo-relative), `Slug`, `Baseline string`, `Facts
  *plan.Facts` (nil without a facts store), `FactIDs []string`, `Declined
  []edits.DeclinedFinding`, `CustomID string`.
- `Build(ctx, in Input) (batch.Request, error)`: the seat's model, effort, `max_tokens`, and system
  prompt (its agent definition's body after the front matter, empty with no `agent`); the answer's
  schema and its output contract text; the inlining note; the files, command outputs, and excerpts.
  Commands run under `ctx` with a 5-minute timeout each and `gate.Env`'s environment.
- `ConsistencyPrompt(p *plan.Plan, facts *plan.Facts, root string) (string, error)` and the
  consistency answer `{ "conflicts": [{ "facts": [...], "with": "<fact id or page#heading>",
  "conflict": "..." }] }`. The placed facts are the plan's `fact` items plus every `facts` list an
  item or the introduction carries (`docs/plan-format.md` names them); each placed fact appears with
  its text. The linked pages are each `link` target that is a repo path, resolved from the page's
  directory, with their headings listed; a URL target is skipped; a linked file that doesn't exist
  is listed as `missing: <path>`.
- The answer schemas: `draft` is `{ page, brief, friction }` with `brief` a string holding JSON;
  `read` is `{ verdict, findings: [{ location, finding, rewrite, blocking }], summary, friction }`;
  `reader1` is `{ paraphrase, summary }`; `reader2` is `read`'s; `edits`, `coverage`, and
  `consistency` are the schemas above. `friction` is an optional list of strings in each. Every
  schema keeps to the structured-output limits (platform.claude.com, structured outputs, "JSON
  Schema limitations", read 2026-10-13): `additionalProperties` "must be set to `false` for
  objects"; no "String constraints (`minLength`, `maxLength`)", no "Numerical constraints", no
  "Array constraints beyond `minItems` of 0 or 1"; and at most 24 optional parameters per request.

`internal/plan` gains, for `assemble`: `Fact.Text` (the bullet's claim text), `Fact.Sources
[]string`, and `(*Facts) Get(id string) (Fact, bool)` (true only when exactly one bullet holds the
id). `Sources` holds the backticked spans in the bullet's `Source:` part, outside parentheses, whose
text before a `:` or `#` is a file or directory under the facts store's repo root; a `:` suffix is a
comma list of `N` or `A-B`. Other spans (commands, commentary, URLs, `[external: ...]`) are skipped.

## Out of scope

The stages, budgets, stop rules, records, and resume (pass 5); building seat contexts (pass 5);
prompt caching; and the agentic fact read (the spec's "The agentic exception").

## Tasks

Every drafter task starts by invoking `go-conventions`. Fixtures are synthetic. The spike's recorded
files are back on this machine at `~/.local/share/drafter/spike/` as a reference; the repo is
public, so each fixture the spec ties to the spike is a synthetic one modeled on it.

### P4.1 The edit contract (75 min, ordinary)

- Outcome: `internal/edits` as listed.
- Files: `internal/edits/` with tests and `testdata/`.
- Acceptance, the spec's edit-contract row as assigned here, each refusal with the exact problem
  text and a clean twin:
  - One row per refusal rule: an old span found zero times, and several times; a `file` other than
    `page` or `brief`; an edit whose old and new text are equal; an edit no resolution claims; a
    resolution naming an edit index that doesn't exist, and one naming a finding number that doesn't
    exist; a finding, blocking and advisory, with no resolution in the union; one finding resolved
    twice in one answer; a blocking finding resolved `edited` with no edits; a brief that isn't valid
    JSON after the edits.
  - Edits apply in order, and an old span that occurs twice in the original but once after an
    earlier edit is accepted.
  - Resolutions accumulate: an applied answer resolves findings 1 to 3, the gate then adds finding 4,
    and a second answer that resolves only 4, with its edit indexes starting at 0, is accepted
    against the union; a second answer that re-resolves finding 2 overrides it.
  - A declined advisory finding is accepted; a declined blocking finding is accepted and returned by
    `Declined` with its reason.
  - `testdata/reader-redraft.answer.json`, a synthetic answer modeled on the spike's
    `reader-redraft-1.answer.json` (several reader findings, each resolved by number, with edits to
    both the page and the brief), is accepted against its findings and page.
- Test: the gate.
- Pair: with P4.2.

### P4.2 Coverage (85 min, ordinary)

- Outcome: `internal/coverage` as listed. A brief sentence is located on the page by its normalized
  text, and its section is the planned section it falls in; a sentence that can't be located is a
  miss, never skipped.
- Files: `internal/coverage/` with tests and `testdata/` (a synthetic page, brief, plan, and coverage
  answers).
- Acceptance, the spec's coverage row and the coverage half of the projects-without-facts row, each
  with its twin: a verbatim item present and absent; a fact cited in its section and in another; a
  link in and out of its section, a same-page `#anchor` link, and a URL link; a brief sentence that
  differs from the page only in a code span (located); a brief sentence not on the page (a miss); a
  sentence under an unplanned `####` inside a planned section (counted in that section); a plan
  section whose heading is missing from the page (its items miss with `heading not found`); `fact`
  items skipped when `facts` is false; a coverage answer whose quote isn't on the page (a miss and a
  fault); a quote that is on the page but in another section (a miss and a fault); an item the
  answer leaves out (a miss); a brief that isn't JSON (the error); a brief with a `cuts` field and a
  `"no-claim"` id (decodes).
- Test: the gate.
- Pair: with P4.1.

### P4.3 cairn's gate logs (35 min, ordinary; in the session)

- Outcome: four scrubbed gate logs in `internal/gate/testdata/logs/`, committed before the P4.4 and
  P4.5 pair is dispatched, since a worktree-isolated session's Bash guard refuses
  `cairn-run-gate '<string>'` (`~/.dotfiles/scripts/gate.sh` lines 3-5). The executing session does
  this task itself:
  - `git clone --shared ~/Projects/cairn-cms <scratch dir>` at `origin/main`, outside every repo's
    tree, and root `npm ci` there (68 s in the plan review's probe; no worktree or branch is added
    to cairn, and its main checkout is never touched).
  - A scratch script with no arguments, outside every repo, runs each gate as
    `CAIRN_GATE_LANE=light cairn-run-gate --fresh '<command>' <log>` from the clone and re-issues
    on exit 75 until stdout carries `gate exit:`. The four runs of `npm run check:docs-gate -- --page
    <p> --brief <b>`: a green run on a published extend page A; a run with a deliberate
    `check:provenance` failure on page A; a run with a deliberate Vale error on page A; and a run
    where a second page B carries a broken link while page A is gated.
  - Scrub each log: drop the npm banner lines; every absolute path becomes `/work/project`; cairn's
    page and brief names become synthetic ones, consistently; prose excerpts (provenance previews,
    snippet reasons, leak warnings) become synthetic text; each log is trimmed to the sections the
    tests need, keeping one green section that names page A.
  - Derive the section and failure patterns that parse those logs. Vale names the file on a header
    line and the error on a line below it; green sections also name pages; RE2 has no lookahead. The
    tellgrader format comes from cairn's `scripts/checks/check-tellgrader.mjs` source (`gatingLines`),
    stated as such in the PR.
  - Delete the clone.
- Files: `internal/gate/testdata/logs/` (the four scrubbed logs).
- Acceptance: a grep of the logs for `/var/home`, `/home/`, `glw907`, and `@glw907` finds nothing;
  the patterns are written down for P4.4's tests and the PR body.
- Test: none of its own; P4.4's tests read the logs.

### P4.4 The gate (80 min, ordinary)

- Outcome: `internal/gate` as listed, following the spec's "The gate" and "Shared worktree":
  - `plain` runs the command through `/bin/sh -c` from the root with the given environment, writes
    combined output to the log, and reads the exit code.
  - `cairn-run-gate` execs `cairn-run-gate --fresh '<command>' <logPath>` with `CAIRN_GATE_LANE` set
    from `gate.lane`, then re-issues without `--fresh` on exit 75 ("Reattaching to a run still in
    flight is never affected by --fresh", the wrapper's header) until its standard output carries a
    `gate exit:` line. The wrapper writes `gate exit: N` and the vanish line to standard output only,
    never to the log (`cairn-run-gate` lines 410 and 439), so drafter reads the result from stdout
    and parses `logPath` only for sections. `gate exit: 1 (vanished 3 times)` returns `ErrInfra`. It
    never passes `--receipt`.
  - With `gate.section_pattern`, a line matching it opens a section named by its first capture
    group, and lines before the first match form a preamble section with an empty name; without it
    the log is one section. With `gate.failure_pattern`, matching lines in a red log are failing;
    without it every line of a red log is. A red log where no line matches the failure pattern, or
    where a section pattern is set and no line matches it, is unparsed.
- Files: `internal/gate/` with tests and `internal/gate/testdata/bin/` (a fake `cairn-run-gate`
  script the tests put first on `PATH`, which prints `gate exit:` to stdout and writes only gate
  output to the log).
- Acceptance, the spec's gate row: a plain gate's exit 0 and nonzero, each with and without the two
  patterns; with the recorded cairn patterns, the provenance log's failing sections attributed to
  page A, the Vale log's error attributed to page A, the two-page log foreign to page A, and green
  sections naming page A not failing; a red log whose failure pattern matches nothing (unparsed, tail
  kept, counted as the page's own); the preamble section; `ForPage` not matching a page path inside a
  longer path. Under the fake `cairn-run-gate`: exit 75 then a result, with `--fresh` on the first
  call only; the vanish line (`ErrInfra`); the log path passed as the second argument;
  `CAIRN_GATE_LANE` set from `gate.lane`; `RUN_GATE_IF_BUSY` absent though the test's environment
  sets it. `Env` drops `KeyEnv`'s variable and an `ANTHROPIC_*` variable the test sets. `Command`
  substitutes all four placeholders, quotes a value holding a space and one holding `'`, and leaves
  `${arm}` alone. Nothing under `testdata/` names a workstation path.
- Test: the gate.
- Pair: with P4.5.

### P4.5 Input assembly (140 min, ordinary; path-safety rows first)

- Order: the `inline_files` path-safety rows below are written and committed failing before the code
  (Geoff's ruling 8), then the rest.
- Outcome: `internal/assemble` as listed, plus the `internal/plan` additions. Following the spec's
  "Input assembly":
  - The note opens the first user turn: files are inlined, a command whose output isn't inlined is
    not to be run, and any edit the seat would make, or any check it couldn't make, becomes a
    finding.
  - Naming: the rendered prompt is split into tokens on whitespace, backticks, quotes, parentheses,
    brackets, angle brackets, and commas. A token names a file when it equals a path `git ls-files`
    lists in the root, in repo-relative form or joined to the root as an absolute path; a token that
    is an absolute path or starts with `~` outside the root is a candidate for `inline_files`.
  - Files: each named tracked file is inlined whole, in one block per file with a fixed header line
    and footer line naming the path, the same delimiters for every block and stated in the note. An
    out-of-repo path is inlined when an `inline_files` entry names it or a directory above it. Both
    sides are expanded (`~`), cleaned, and resolved through symlinks before matching, and a match
    holds only at a path-separator boundary (`/x/exemplars` doesn't admit `/x/exemplars-old/f`). A
    tracked file that resolves through a symlink to a path outside the root is treated as
    out-of-repo. `inline_files` is read only from `Config` (the user and local layers), never from a
    prompt or a handoff. A named path that is neither stays out. A file over 256 KiB becomes a
    `not inlined: N bytes` block; an allowed path that doesn't exist becomes `not inlined: missing`.
  - Commands: each command in the seat's `inputs` runs from the root, with placeholders substituted
    by `gate.Command`, just before the request, and its output is inlined under the command text
    whatever its exit status, with a nonzero status noted (`diff` exits 1 when it finds a change).
    A command naming `{baseline}` runs only when `Baseline` is set.
  - Source excerpts, when `Facts` is set, for each id in `FactIDs`: `path:N` yields lines N-10 to
    N+10; `path:A-B` yields A-5 to B+5; a comma list yields each; ranges are clamped to the file.
    `path#name` yields 5 lines before to 40 after the first declaration of `name` (its last dotted
    segment), found by the spec's declaration patterns with their modifiers (a Go `func`, including
    a method `func (r *T) Name`, `type`, `var`, or `const`; a TypeScript or JavaScript `function`,
    `class`, `interface`, `type`, `enum`, `const`, or `let`, after any of `export`, `export
    default`, `async`, `declare`, or `abstract`), never by a mere mention. A bare file is inlined
    whole up to the size limit. Each other case is a named block: `no excerpt: directory`, `no
    excerpt: prose`, `no excerpt: declaration not found`, `no excerpt: missing`, and `no excerpt:
    untracked` (a source path `git ls-files` doesn't list).
  - Without a facts store, the `fact` seat's request inlines each tracked path the page or its brief
    names, under the same limit, in place of excerpts.
  - The final reader: `reader1` holds exactly one file block, the page, whatever paths its prompt
    names; `reader2` continues that conversation with the module's turn-2 prompt and inlines nothing.
    An `edits` continuation inlines the current page and brief.
  - `coverage` and `consistency` requests take their prompt as built and inline nothing more.
  - `Declined` findings, with their reasons, follow the prompt in a block telling the seat to accept
    each decline or raise the finding again.
- Files: `internal/assemble/` with tests and `testdata/` (Go and TypeScript sources, a facts file,
  an agent definition with front matter); `internal/plan/facts.go` and its test. The tests build the
  synthetic repo at test time: copy `testdata/` into `t.TempDir()`, `git init`, and `git add` every
  file but one, as `e2e/e2e_test.go` does, since a nested `.git` can't be committed.
- Acceptance, the spec's input-assembly row and the fact-read half of the projects-without-facts
  row, each with its twin:
  - Written first, the path-safety rows: an `inline_files` entry with a path that climbs out through
    `..`; a symlink inside the allowed directory that points outside it; a sibling directory sharing
    the entry's prefix (`exemplars-old`); a tracked symlink pointing outside the root; each stays out.
  - An untracked path stays out; an allowed out-of-repo path is in; a repo-relative and a
    root-absolute mention of one tracked file each inline it once; an oversized file is a `not
    inlined` block.
  - Excerpts for `path:line`, `path:A-B`, a comma list, a range past the end (clamped), a bare file,
    a directory, a prose source, a `#name` whose name is imported above its declaration (the excerpt
    holds the declaration, not the import), a Go method, an `export default` TypeScript class, a
    `#name` with no declaration, a missing source path, and an untracked one.
  - `Fact.Sources` on synthetic bullets in cairn's shapes: a comma list of ranges
    (`src/x.ts:100-110,163-166`), backticked commentary in parentheses, a backticked command, a URL,
    and an `[external: ...]` part; `Get` on an id held by two bullets returns false.
  - The reader's first turn holds exactly one file block, the page, and no job text, although its
    synthetic prompt names an outline file; `reader2` inlines nothing; an `edits` continuation
    inlines the current page and brief.
  - The fact read without facts inlines the tracked files the page names; a command with
    `{baseline}` is skipped without a baseline and run with one; a command that sleeps past its
    timeout is cut off and noted; a command's environment holds no `KeyEnv` variable.
  - A declined blocking finding and its reason appear in the next read's request; the system prompt
    is the agent definition's body without its front matter.
  - `ConsistencyPrompt` on a synthetic plan with facts and two linked pages, one URL target, and one
    missing linked file.
  - A schema walk over `draft`, `read`, `reader1`, `reader2`, `edits`, `coverage`, and
    `consistency`: every object has `additionalProperties: false`, no schema uses a keyword the
    structured-output limits exclude, and each holds no more than 24 optional parameters.
- Test: the gate.
- Pair: with P4.4.

### Close (25 min)

The gate, once, on the close head. One whole-branch `diff-reviewer` run against `main`, with
go-conventions for `*.go`; its dispatch names P4.5's written-first path-safety rows for a read of
their own (ruling 8). One batched fix chain if needed, then the gate again. `gitleaks git` over the
branch history, and a grep of `testdata/` for `/var/home`, `/home/`, `glw907`, and `@glw907` that
finds nothing. Push the branch to `glw907/drafter` and open the PR: `## Brief`, what landed, the
review verdict, cairn's gate patterns from P4.3 with where each came from, the score rows (gate time
from `~/.local/state/cairn-run-gate/runs.jsonl` records whose `gate` names this worktree; the Work
and review row puts the 285-minute path beside the actual), and "Found, not done" with a proposed
disposition each.

When the review accepted and "Found, not done" is empty, merge with `gh pr merge <n> -R
glw907/drafter --merge`, then `git -C ~/Projects/drafter pull --ff-only` and `make -C
~/Projects/drafter install`. Otherwise stop at PR-ready and name the PR in the final message; the
conductor takes it to Geoff.

## Later

- A setting for the inline size limit, if a project's sources outgrow 256 KiB per file.
