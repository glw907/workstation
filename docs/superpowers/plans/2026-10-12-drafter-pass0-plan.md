# Pass 0 plan for the YAML plan format and `drafter check-plan`

Design: approved by Geoff, 2026-10-12, in session dotfiles-5a ("You can include it. Draft the
plan."). Spec: `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, section "The plan
format". This pass builds only that section's offline part; the rest of the spec is later passes.
The mechanics review (`docs/superpowers/research/2026-10-12-drafter-pass0-plan-review-mechanics.md`)
is folded per `docs/superpowers/research/2026-10-12-drafter-pass0-plan-fold.md`.

## Outcome

A planner writes `<page>.plan.yaml`, runs `drafter check-plan`, and gets every finding as
`file:line` with the fix. The docs page chain's plan step writes YAML plans and runs the validator
until it exits 0, so pages planned after the merge carry addressable items, the reader-state walk,
the recovery matrix, and the link and fact checks. The chain's back half drafts from a YAML plan
unchanged, since it reads the plan file as text.

## Shape

Risk class: `runner` (T1's gate wrapper and T6's chain change). The other tasks are `ordinary`. No
`live-account` flag: the planning session creates the GitHub repo before launch, and nothing in the
pass calls an API or deploys. Geoff reads and merges the dotfiles PR; the drafter PR merges first.

Estimate: 615 task-minutes against a design estimate of 350 (under the 2x line of 700).

Dependencies, each at its newest release: `github.com/spf13/cobra` (v1.10.2), `go.yaml.in/yaml/v3`
(v3.0.5, the YAML org's maintained module; `gopkg.in/yaml.v3` was archived April 1, 2025), and
`github.com/yuin/goldmark` (v1.8.6) for heading extraction. Tests use the standard library only.

Repos:

- `~/Projects/drafter`, `github.com/glw907/drafter`, public from the start. Before launch it holds
  only `go.mod` and a README on `main` (see "Launch"); the pass works on a `pass0` branch in that
  checkout. Nothing in the repo names a workstation path, an account detail, or a key source, and
  every fixture is synthetic. Gate: `bash scripts/drafter-gate.sh` from the dotfiles pass worktree
  (T1), which runs `CAIRN_GATE_LANE=light cairn-run-gate 'make -C ~/Projects/drafter check'`.
  Full-suite home: that same command, once on the close head; there is no CI.
- `~/.dotfiles`, through the `dotfiles-pass` adapter. Gate: `bash scripts/gate.sh`. The chain edit
  is made only in the pass's dotfiles worktree: `~/.claude/workflows` links into the main checkout,
  so an edit there would change the live chain under the cairn docs sessions.

The executor never touches `bash/.bashrc` in the dotfiles main checkout: its uncommitted change
belongs to another session.

Plan-schema stability: every plan carries `version: 1`. A later pass may only add optional fields,
so no Pass 0 plan ever needs rewriting. The facts-pattern override and the rest of configuration
come in the configuration pass; they govern how drafter reads facts files, not plans, so plans
written now stay valid.

Out of scope: batching, prompts, the pipeline, the ledger, the handoff, every configuration layer
(no TOML and no `drafter.toml` read: `check-plan` takes flags only), and the consistency read (an
API call that lives in pipeline stage 1). No cairn-cms change in this pass. cairn's docs review page
reads only `<slug>.plan.md` (`scripts/docs-review/embed.mjs` `planPathFor`), so a cairn follow-up
that teaches it `.plan.yaml` must land before the next chain run that uses YAML plans; the dotfiles
PR records it under "Found, not done" with disposition "now" (Geoff's ruling, 2026-10-12).

## Standing approvals

Geoff answered these before launch (2026-10-12), and the session applies them in place of
stopping:

- An estimate overrun continues without a stop while the pass's elapsed task-minutes (finished
  tasks plus the one in flight) stay under 900. Past 900 the session writes STATUS, runs
  `notify-send -u normal`, and waits.
- A per-task clock stop gets the same answer: under the 900 total, the session rewrites `start=` in
  the clock file and continues; past it, it stops as above.

The session keeps the running total in STATUS. One clock-file location serves the whole pass: the
dotfiles pass worktree's git dir (`git rev-parse --absolute-git-dir` there). The session's working
directory stays in that worktree, and every drafter command takes a path (`make -C`, `git -C`,
`go -C`), so `claude-clock-stop`, which resolves the git dir from the hook input's `cwd`, always
finds the file.

## Tasks

Each task: outcome, files, class, acceptance, test, estimate. No implementation code here; the
spec's "The plan format" section and go-conventions govern the how.

### T1. The drafter skeleton and its gate (25 min, runner)

- Outcome: on `pass0` in `~/Projects/drafter`, `cmd/drafter/` (main.go and a cobra root with a
  `check-plan` stub, per go-conventions' cobra shape), `internal/`, a Makefile (build, test, vet,
  lint, install, check, clean; `install` copies the binary to `~/.local/bin/drafter` with mode
  0755), `.golangci.yml` per the go-conventions linting reference, `.gitignore`, and a CLAUDE.md
  naming `make check` and the go-conventions skill. In the dotfiles worktree,
  `scripts/drafter-gate.sh`, a no-argument wrapper shaped like `scripts/gate.sh`: a worktree-isolated
  session's Bash guard refuses `cairn-run-gate '<string>'` and accepts a no-argument wrapper
  (`scripts/gate.sh`'s header comment).
- Files: the drafter skeleton above; `scripts/drafter-gate.sh` (dotfiles worktree).
- Acceptance: `bash scripts/drafter-gate.sh` prints `gate exit: 0` on the skeleton.
- Test: `bash scripts/drafter-gate.sh`.

### T2. Plan types, schema, and strict decoding (90 min, ordinary)

- Outcome: `internal/plan` decodes a `<page>.plan.yaml` into typed structs with this shape. A prose
  field is one a planner writes as a sentence or more; it must be a `|` block or quoted.

  | Field | Type | Required | Prose |
  |---|---|---|---|
  | `version` | integer, `1` | yes | no |
  | `page` | map: `path` (repo-relative), `title` (the H1), `type` (the page type) | yes, all three | no |
  | `argument` | string | yes | yes |
  | `introduction` | map: `covers`, `priorKnowledge`, `notCovered` (Google's three parts) | yes, all three | yes |
  | `orderReason` | string: why the sections run in this order | yes | yes |
  | `preconditions` | list of state tokens the reader holds before the first step | no | no |
  | `sections` | list, in page order: `heading` (verbatim), `opens` (the section's first sentence), `items` | yes, one or more | `opens` |
  | `dispositions` | list: `fact`, `disposition` (`subordinated` or `cut`), `reference` (a link target, required when subordinated), `reason` | no | `reason` |
  | `constraints` | list of strings: drafting constraints | no | yes |
  | `friction` | list of strings | no | yes |

  Items nest in their section and carry no `section` field. Every item has `id` (a lowercase token,
  unique across the plan) and `kind`, plus the fields of its kind and no others:

  | Kind | Fields |
  |---|---|
  | `fact` | `fact`: a fact id. The item id is separate, so one fact may sit in two sections. |
  | `sentence` | `mode` (`verbatim` or `claim`), `text` (prose) |
  | `link` | `target`: `path`, `path#anchor`, `#anchor`, or an `http(s)://` URL; a path resolves from the page's directory, as the page's own link would |
  | `handoff`, `reason` | `text` (prose) |
  | `step` | `text` (prose); `requires` and `produces` (lists of state tokens, optional); `canFail` (boolean, default false) |
  | `failure` | `from` (a step's id), `symptom` (prose), `handledBy` (an item's id) |

  A placed fact is a `fact` item; `dispositions` holds only subordinated and cut facts. Decoding
  walks the `yaml.Node` tree itself, so every finding carries its line. The walk refuses an unknown
  field, a missing required field, a wrong type, a duplicate key, an empty document, a second YAML
  document, and a prose field in plain style that carries a line comment. Each of these is probed
  on `go.yaml.in/yaml/v3` v3.0.5: `id: a` twice unmarshals into a Node with no error; `Node.Decode`
  ignores unknown fields (the decoder's `KnownFields` doesn't reach it); an empty document gives an
  empty Node with no error; `yaml.Unmarshal` drops a second document silently; and both `claim:
  Push first # then delete` and a two-line plain value ending in `# tail` decode truncated, the rest
  in `LineComment`. `schema/plan.schema.json` is the published JSON Schema for the same shape.
- Files: `internal/plan/plan.go`, `decode.go`, their tests, `schema/plan.schema.json`,
  `internal/plan/testdata/`, `go.mod` and `go.sum` (`go.yaml.in/yaml/v3`).
- Acceptance: each refusal has a table row whose fixture fails for that reason alone, with the
  expected line, and a clean twin that decodes; the line-comment rows cover a one-line and a
  multi-line plain value, and quoted and `|` twins pass. The schema sync test reflects over the Go
  types' YAML tags and fails if a field name or a required set differs from `plan.schema.json`
  (standard library only).
- Test: `go -C ~/Projects/drafter test ./internal/plan/...`.

### T3. The mechanical checks (150 min, ordinary)

- Outcome: `internal/plan` runs, over a decoded plan, a repo root, an optional facts directory, and
  an optional outline:
  - Id integrity: ids unique; `from` names a step; `handledBy` names an existing item; no fact is
    both a `fact` item and a disposition.
  - Reader-state walk: in page order, every step's `requires` is produced by an earlier step or
    listed in `preconditions`.
  - Recovery matrix: every step with `canFail: true` is the `from` of at least one `failure` item.
  - Links and anchors, for every `link` target and subordinated `reference`: an `http(s)://` target
    is not checked; a path must exist under the root (a directory passes, an anchor on it fails); an
    anchor must match a heading slug in that file, and a same-page `#anchor` must match the slug of
    the plan's `page.title` or a section `heading`. A target the outline lists that isn't on disk
    yet is a warning, not an error, and its anchor isn't checked (Geoff's ruling, 2026-10-12: "I
    expect this to be a fairly regular occurance when drafting new docs"). Any other missing target
    stays an error.
  - Slugs follow GitHub's rule as `github-slugger` 2.0.0 implements it (the version cairn has
    installed; cairn's renderer applies it through `rehype-slug`, one slugger per file, so a repeated
    heading takes `-1`). Headings come from goldmark's CommonMark parse, ATX and setext, never from
    fenced code, with text taken as `hast-util-to-string` takes it (inline code's text kept, markup
    and link URLs dropped). A heading written as raw HTML isn't an anchor in this pass; the reference
    says so.
  - Fact citability, only when a facts directory is given: every `fact` item's id, and every
    disposition's `fact`, resolves to exactly one bullet, and a `fact` item's bullet is citable. The
    reader follows cairn's `scripts/checks/check-facts.mjs` as the reference: every `*.md` but
    `README.md` (`factsFiles`); bullets joined across soft-wrapped lines under their `## ` section,
    with `Harvest record` and `Provenance` sections skipped (`extractBullets`, `SKIPPED_SECTIONS`);
    the id from a leading code span (`FACT_ID_RE`); the status tag as the bullet's last bracket, with
    code spans and quoted spans masked first (`checkTag`). Citable tags are `verified`, `external`,
    and `vendor`; `candidate` (any qualifier), `rejected`, `docs-drift`, a missing tag, and a tag
    outside the vocabulary are not (cairn's `docs/internal/facts/README.md`). Without a facts
    directory, each `fact` item is skipped with a warning naming its line (spec, "Projects without
    facts").
  - Outline: a JSON file whose `pages` array holds objects with a repo-relative `path`; drafter
    reads nothing else from it. cairn's `docs/internal/outlines/extend.json` has that shape.
  Each finding carries file, line, severity (`error` or `warning`), the check's name, and a
  one-sentence fix.
- Files: `internal/plan/check.go`, `slug.go`, `facts.go`, `outline.go`, their tests, fixtures under
  `internal/plan/testdata/repo/`, and `internal/plan/testdata/github-slugger/` holding
  `fixtures.json` from github-slugger's repo at tag `2.0.0` (`test/fixtures.json`, 78 cases; the npm
  package doesn't ship it) with its ISC `LICENSE`. The Go port of `regex.js` in `slug.go` carries the
  same notice in its header. `go.mod` and `go.sum` gain goldmark.
- Acceptance: one failing fixture and one clean twin per rule: a duplicate id, a dangling
  `handledBy`, a `from` naming a non-step, a fact both placed and disposed, a `requires` met only by
  a later step, a `requires` met by a precondition (passes), a failing step with no failure item, a
  missing target, a missing anchor, an anchor on a directory, an unmatched same-page anchor, an
  outline-listed target not on disk (warning), a placed id in no facts file, an id on two bullets, a
  placed `[rejected]`, `[candidate: excluded]`, and `[docs-drift: ...]` fact, a bullet with no tag,
  and the no-facts warning. Facts rows cover a bullet whose tag wraps to a second line, a bracket
  inside a code span, a bullet under `## Provenance`, and a `README.md` holding a matching id
  (ignored). Slug rows run every vendored case in order on one slugger, plus a heading in fenced code
  (ignored), a setext heading, and a heading with inline code and a link.
- Test: `go -C ~/Projects/drafter test ./internal/plan/...`.
- Pair: with T6. T3 goes to an Agent subagent without isolation, working `~/Projects/drafter` by
  path as its only writer; T6 goes to one with `isolation: "worktree"`. Worktree isolation covers
  only the launch repository: "The checks apply to the repository you launched Claude Code from"
  (code.claude.com/docs/en/worktrees), so a subagent worktree is a dotfiles worktree and can't
  isolate drafter. The session merges T6's branch into its dotfiles branch and runs both gates.

### T4. The `check-plan` command and install (110 min, ordinary)

- Outcome: `drafter check-plan [--facts <dir>] [--outline <file>] [--root <dir>] [--json] <plan>...`
  decodes and checks each plan. It prints each finding as `file:line: severity: check: message
  (fix)` to stdout and a count to stderr. `--json` prints the same findings as one JSON array (each
  object: `file`, `line`, `severity`, `check`, `message`, `fix`), with the same exit code. `--root`
  defaults to `git rev-parse --show-toplevel` from the first plan's directory. Each state has one
  report:

  | State | Report | Exit |
  |---|---|---|
  | Clean | the count only | 0 |
  | Warnings only | each warning, the count | 0 |
  | Any error finding | every finding, the count | 1 |
  | Empty file, malformed YAML, a second document | a decode finding at its line | 1 |
  | Several plans | every plan checked, one count; mixed results exit by the worst | 0 or 1 |
  | No plan argument, an unknown flag | usage on stderr | 2 |
  | A plan file missing or unreadable | the path and error on stderr | 2 |
  | `--facts` missing, or holding no facts file | the path and error on stderr | 2 |
  | `--outline` missing, not JSON, or without a `pages` array | the path and error on stderr | 2 |
  | No `--root` and the plan outside a git tree | the error on stderr | 2 |

  `make install` puts the binary in `~/.local/bin`, and `drafter` is added to
  `bluefin/untracked-bin.txt` in the dotfiles worktree (the manifest for plain-file executables that
  own their install path).
- Files: `cmd/drafter/checkplan.go`, `e2e/` (TestMain builds the binary once), `e2e/testdata/`;
  `bluefin/untracked-bin.txt` (dotfiles worktree).
- Acceptance: the e2e test runs the real binary on `e2e/testdata/project/`, a synthetic project (a
  fictional tool's docs, no cairn text): stub sibling pages carrying the headings the plan's anchors
  name, a `docs/facts/` file with citable, rejected, and wrapped bullets and a `## Provenance`
  section, and `docs/outline.json` listing one sibling not on disk. Its plan for a key-rotation task
  guide comes in two forms, modeled on the two recovery gaps the spike's final reader found (a
  failed publish while the health check passes, and telling the old key from the new; the spike's
  `run-rotate-the-github-app-key-edit2/reader.response.json`). Rows: (a) the gaps plan, whose two
  steps carry `canFail: true` with no `failure` item, reports exactly those two recovery-matrix
  errors and the outline warning, exit 1; (b) the clean plan, with both failure items, prints only
  the warning, exit 0; (c) a `git init` temp copy run without `--root` matches (b); (d) `--json` on
  (a) gives three objects with their severities; (e) (b) without `--facts` warns on each `fact`
  item, exit 0; (f) one row per exit-2 state in the table. In the dotfiles worktree, `command -v
  drafter` resolves and `grep -x drafter bluefin/untracked-bin.txt` matches.
- Test: `bash scripts/drafter-gate.sh` (it runs the e2e suite), then `drafter check-plan --help`.

### T5. The plan format reference and README (35 min, ordinary)

- Outcome: `docs/plan-format.md` documents `version` and the stability rule, every field and item
  kind with an example, each check and what it catches, the warning and exit-code table, the
  line-comment rule (prose fields use `|` blocks or quotes), the outline contract, the facts bullet
  grammar and the citable tags, and the raw-HTML heading limit. The README covers what drafter is,
  `make install`, and `check-plan`. Both follow the Google developer documentation style and name no
  workstation path.
- Files: `docs/plan-format.md`, `README.md`.
- Acceptance: every field in `schema/plan.schema.json` appears in the reference; `tellgrader
  --register docs` reports no gating finding on either file.
- Test: a Go test that fails if a schema field name is missing from `docs/plan-format.md`.

### T6. The chain writes YAML plans (120 min, runner)

- Outcome, in `claude/.claude/workflows/docs-page-chain.js` (dotfiles worktree only):
  - Before any edit, both `planPrompt` and the plan-mode `structurePrompt` are rendered for fixed
    inputs through the outline test's full-runner dry run and saved under
    `tests/fixtures/docs-page-chain/` as markdown-mode goldens.
  - A `planFormat` argument, `"yaml"` by default, `"markdown"` keeping today's behavior for an
    in-flight run. `planPathFor` returns `.plan.yaml` or `.plan.md` by it.
  - `planPrompt` in YAML mode tells the plan step to write the plan in the format
    `~/Projects/drafter/docs/plan-format.md` documents, with every prose field as a `|` block, and
    to run `drafter check-plan --facts docs/internal/facts <plan>`, adding `--outline <outline>`
    when the run has `args.outline`. It runs the validator at most three times per write; when the
    third run still exits nonzero, it reports the remaining findings as `couldNotDo`. A page whose
    committed `.plan.md` exists is read as the prior plan, and the step deletes that file once its
    `.plan.yaml` is written, so each page keeps one plan.
  - `PLAN_SCHEMA` gains an optional `checkPlan: { exit, output }`, the final run's exit code and
    output. In YAML mode `planStep` escalates when `checkPlan` is missing or its exit is nonzero,
    naming the output, since the runtime has no exec access to rerun it.
  - `structurePrompt` in plan mode, in YAML mode, grades the plan's `step` and `failure` items: the
    reader-state walk proves consistency, not completeness, so the seat judges whether a step or a
    failure the page needs is missing.
  - The header comment documents `planFormat`, the validator loop, and the rework case.
- Files: `claude/.claude/workflows/docs-page-chain.js`, `tests/docs-page-chain-outline.test.mjs`,
  `tests/fixtures/docs-page-chain/`.
- Acceptance: the existing outline test's cases pass `planFormat: "markdown"` through `baseArgs`
  and stay green unchanged otherwise (its `stubPlan` matches `.plan.md`). New cases in the same file
  run the runner in YAML mode and assert the `.plan.yaml` path, the `drafter check-plan` line with
  and without `--outline`, the `|` rule, the three-run cap, and an escalation for a missing and a
  nonzero `checkPlan`, each with a passing twin. Markdown-mode renders equal the goldens byte for
  byte.
- Test: `bash scripts/gate.sh` (`scripts/check.sh` already runs the outline test).

### T7. End-to-end on one cairn page (45 min, ordinary)

- Outcome: the YAML-mode plan step and plan-mode structural read for
  `docs/extend/rotate-the-github-app-key.md` (Geoff's choice), rendered from the T6 chain by
  `~/.local/share/drafter/spike/chainprompts.mjs` with `job-rotate-current.json` (its `chain` path
  set to the worktree's chain, `planFormat: "yaml"` added) and `rotate-pageinputs.json`. The plan
  step runs as one Agent dispatch (Opus 5.5, high effort, as `planStep` sets it) in a scratch
  cairn-cms worktree based on `origin/main`, with the rendered no-claim path rewritten to a scratch
  path, since `~/.cache/docs-page-chain/<slug>.no-claim.txt` is shared with live runs. The page's
  committed `.plan.md` exercises the rework case. The structural read runs on the result. Nothing in
  cairn-cms is committed; the scratch worktree is removed after.
- Acceptance: `drafter check-plan --facts docs/internal/facts --outline
  docs/internal/outlines/extend.json` exits 0 on the plan; the plan file, that output, and the
  structural read's verdict are recorded in the dotfiles PR body.
- Test: the recorded exit 0.

### Close (40 min)

`bash scripts/drafter-gate.sh` and `bash scripts/gate.sh` run once on the close heads. Two
whole-branch `diff-reviewer` runs: drafter's `pass0` against `main` (which holds only `go.mod` and
the README, so the review covers every line the pass wrote; go-conventions for `*.go`), and the
dotfiles branch (ts-conventions for `*.js` and `*.mjs`). The dotfiles close checklist runs:
`claude-tooling-sync verify`, a `gitleaks git` branch-history scan in each repo, the manifest
record. Two PRs, `glw907/drafter` and `glw907/dotfiles`, each body naming the other. The dotfiles
body carries the score, T7's record, and "Found, not done", including the cairn review-page
follow-up (disposition "now") and the `planFormat: "markdown"` escape hatch for in-flight runs.

The dotfiles PR carries a `## Before merge` section: the drafter PR is merged, then `git -C
~/Projects/drafter switch main`, `git -C ~/Projects/drafter pull --ff-only`, and `make -C
~/Projects/drafter install`; the check is `drafter check-plan --help` exiting 0 and
`~/Projects/drafter/docs/plan-format.md` existing on `main`. After the dotfiles merge, the merger
runs `git -C ~/.dotfiles pull --ff-only` per pass-core "Close", then `check-drift` (it reads
`$HOME/.dotfiles`, so it can't pass before the manifest line lands there), and tells the cairn docs
sessions the merge time and the `planFormat: "markdown"` escape hatch.

## Launch

The planning session prepares everything before launch, then hands off and closes. A conductor
session, not the planner, launches the executor and watches it.

1. Merge the spec branch (spec, reviews, folds, this plan, and the launch prompt; docs only) to
   dotfiles `main` through a PR, as a hand-over. Switch `~/.dotfiles` to `main` and pull. The
   uncommitted `bash/.bashrc` change belongs to another session and stays as it is.
2. Create `~/Projects/drafter` with `go.mod` (`github.com/glw907/drafter`, the installed Go
   version) and a one-paragraph README, committed on `main`. Create the public GitHub repo
   `glw907/drafter` and push `main`.
3. Run pass-core's "Execute" pre-launch checks on `~/.dotfiles`.
4. The conductor launches from `~/.dotfiles`: `claude --bg --model sonnet --effort medium --name
   drafter-pass0 --add-dir ~/Projects/drafter "$(cat <launch prompt file>)"`.

The launch prompt names both push targets, `glw907/dotfiles` and `glw907/drafter`; both gates
(`bash scripts/gate.sh` and, from T1, `bash scripts/drafter-gate.sh`); the drafter full-suite home
(local, that same gate once on the close head); the close `gitleaks git` scans; the clock-file
location and the standing approvals above; and that the session never touches `bash/.bashrc`. The
executor's first act is `EnterWorktree` in dotfiles; it then switches `~/Projects/drafter` to a new
`pass0` branch.

Before launch, the cairn docs sessions (`cairn-cms-aa`, `draft-docs-2b-part1`) were told on
2026-10-12 that the chain change is coming and asked not to edit `docs-page-chain.js` meanwhile.
