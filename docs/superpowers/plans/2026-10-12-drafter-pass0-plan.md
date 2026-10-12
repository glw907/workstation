# Pass 0 plan: the YAML plan format and `drafter check-plan`

**Design:** approved by Geoff, 2026-10-12, in session dotfiles-5a ("You can include it. Draft the
plan."). Spec: `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, section "The plan
format". This pass builds only that section's offline part; the rest of the spec is later passes.

**Outcome:** a planner writes `<page>.plan.yaml`, runs `drafter check-plan`, and gets every error
as `file:line` with the fix. The docs page chain's plan step writes YAML plans and runs the
validator until clean, so pages planned after the merge carry addressable items, the reader-state
walk, the recovery matrix, and the link and fact checks. The chain's back half drafts from a YAML
plan unchanged, since it reads the plan file as text.

**Risk class:** `runner` (the chain change). The drafter repo tasks are `ordinary`. No
`live-account` flag: nothing calls an API or deploys. Geoff reads and merges the dotfiles PR; the
drafter PR merges with it.

**Estimate:** 455 task-minutes against a design estimate of 350 (under the 2x line of 700).

**Repos:**
- `~/Projects/drafter`, new, `github.com/glw907/drafter`, private for now (public release is
  sub-project 5). Gate: `make check` (go-conventions: vet, golangci-lint, test).
- `~/.dotfiles`, through the `dotfiles-pass` adapter. Gate: `bash scripts/gate.sh`. The chain edit
  is made only in the pass's dotfiles worktree: `~/.claude/workflows` links into the main checkout,
  so an edit there would change the live chain under the cairn docs sessions.

**Out of scope:** batching, prompts, the pipeline, the ledger, the handoff, configuration layers
beyond the one optional `drafter.toml` read below, and the consistency read (an API call that lives
in pipeline stage 1). No cairn-cms repo change: `check-plan` takes the facts directory as a flag,
so cairn needs no `drafter.toml` yet.

**Standing approvals for an unattended run** (Geoff answers these before launch; see "Launch"):
an estimate overrun up to a named ceiling continues without a stop.

## Tasks

Each task: outcome, files, class, acceptance, test, estimate. No implementation code here; the
spec's "The plan format" section and go-conventions govern the how.

### T1. Bootstrap the drafter repo (40 min, ordinary)

- Outcome: `~/Projects/drafter` exists with `go.mod` (`github.com/glw907/drafter`, the installed Go
  version), `cmd/drafter/` (main.go and a cobra root with a `check-plan` stub), `internal/`, a
  Makefile (build, test, vet, lint, install, check, clean; `install` copies the binary to
  `~/.local/bin/drafter` with mode 0755, as poplar's does), `.golangci.yml` per the go-conventions
  linting reference, a CLAUDE.md naming the gate and the conventions skill, and a one-paragraph
  README stub. A private GitHub repo `glw907/drafter` with `main` pushed.
- Files: the repo skeleton above.
- Acceptance: `make check` passes on the skeleton; `gh repo view glw907/drafter` resolves.
- Test: `make check`.

### T2. Plan types, schema, and strict decoding (70 min, ordinary)

- Outcome: `internal/plan` decodes a `<page>.plan.yaml` into typed structs matching the spec's
  plan format: the page block, the argument, the order and its reasons, the introduction, sections
  with `opens` and `items`, dispositions, drafting constraints, and friction. Items carry id,
  section, kind (`fact`, `sentence` with `mode` `verbatim` or `claim`, `link`, `handoff`, `reason`,
  `step` with `requires`, `produces`, and `canFail`, `failure` with `from`, `symptom`, and
  `handledBy`). Decoding walks the `yaml.Node` tree, so every error carries its line. It refuses
  an unknown field, a missing required field, a wrong type, and any prose field in plain style that
  carries a line comment (the review's probe: `claim: Push the new key first # then delete the old`
  decodes truncated with no error under `yaml.v3`). `schema/plan.schema.json` is the published JSON
  Schema for the same shape, kept in step by a test.
- Files: `internal/plan/plan.go`, `decode.go`, their tests, `schema/plan.schema.json`,
  `internal/plan/testdata/`.
- Acceptance: each refusal above has a table row whose fixture fails for that reason alone, with
  the expected line; a valid fixture decodes; the schema test decodes every valid fixture's
  structure and fails if the Go types and the JSON Schema disagree on a field.
- Test: `go test ./internal/plan/...`.

### T3. The mechanical checks (90 min, ordinary)

- Outcome: `internal/plan` runs, over a decoded plan and a repo root:
  - Id integrity: ids unique; every id an item references (`from`, `handledBy`) exists.
  - Reader-state walk: every `step`'s `requires` is produced by an earlier step or listed in the
    plan's preconditions.
  - Recovery matrix: every step with `canFail: true` has at least one `failure` item, and every
    failure's `handledBy` names an existing item.
  - Links and anchors: every `link` target exists under the repo root, and an anchor matches a
    heading slug of that file, by GitHub's slug rule as `github-slugger` implements it (the spec
    records that cairn's renderer uses it through `rehype-slug`).
  - Fact citability, only when a facts directory is given: every `fact` item's id resolves to a
    bullet whose status tag is citable, never `[rejected]`, `[candidate]` (any qualifier), or
    `[docs-drift]`. The bullet format is cairn's documented one
    (`docs/internal/facts/README.md`: ``- `f:<id>` <claim>. Source: ... [<tag>]``), the default;
    a `drafter.toml` `[facts]` table may override the pattern.
  Each finding carries file, line, the check's name, and a one-sentence fix.
- Files: `internal/plan/check.go`, `slug.go`, `facts.go`, their tests, fixtures under
  `internal/plan/testdata/repo/`.
- Acceptance: one failing fixture per rule (a dangling `handledBy`, a duplicate id, an unmet
  `requires`, a failing step with no failure item, a missing link target, a missing anchor, a placed
  `[rejected]` fact, a placed `[candidate: excluded]` fact) and one clean fixture; slug rows cover
  punctuation, backticks, duplicate headings (`-1` suffix), and non-ASCII, with expected slugs taken
  from `github-slugger`'s own test cases.
- Test: `go test ./internal/plan/...`.
- Pair: with T5 (disjoint files).

### T4. The `check-plan` command (50 min, ordinary)

- Outcome: `drafter check-plan [--facts <dir>] [--root <dir>] [--json] <plan>...` decodes and
  checks each plan. It prints findings as `file:line: check: message (fix)` to stdout, a count to
  stderr, and exits 0 when clean, 1 on findings, 2 on a usage or read error. `--root` defaults to
  the repo root found from the plan's path (`git rev-parse --show-toplevel`). It reads an optional
  `drafter.toml` at the root for `[facts]` only and ignores every other key in this pass.
- Files: `cmd/drafter/checkplan.go`, `e2e/` (TestMain builds the binary once), `e2e/testdata/`.
- Acceptance: the e2e test runs the real binary on (a) today's spike plan for
  `rotate-the-github-app-key` rewritten in YAML without its two recovery gaps (a failed publish
  while `/healthz` passes, and telling the old key from the new one), which must report both as
  recovery-matrix findings, and (b) the same plan with them added, which must exit 0. The spike's
  markdown plan is at `~/.local/share/drafter/spike/` (`grade2/rotate-the-github-app-key.plan.md`);
  the YAML version is written for the fixture, with its facts checked against a copied facts file.
- Test: `go test ./e2e/...`, then `make check`.

### T5. The plan format reference and README (30 min, ordinary)

- Outcome: `docs/plan-format.md` documents every field and item kind with an example, the
  checks and what each catches, the line-comment rule (prose fields use `|` blocks or quotes), and
  the facts bullet format and its override. The README covers what drafter is, `make install`, and
  `check-plan`. Both follow the Google developer documentation style (the workstation's
  `technical-doc-go` register).
- Files: `docs/plan-format.md`, `README.md`.
- Acceptance: every field in `schema/plan.schema.json` appears in the reference; `tellgrader
  --register docs` reports no gating finding on either file.
- Test: a Go test that fails if a schema field name is missing from `docs/plan-format.md`.
- Pair: with T3.

### T6. Install and record (15 min, ordinary)

- Outcome: `make install` puts `drafter` in `~/.local/bin`; `drafter` is added to
  `~/.dotfiles/bluefin/untracked-bin.txt` (the manifest for plain-file executables that own their
  install path), so `check-drift` accepts it.
- Files: `~/.dotfiles/bluefin/untracked-bin.txt` (dotfiles worktree).
- Acceptance: `command -v drafter` resolves; `check-drift` reports no stray for it.
- Test: `drafter check-plan --help` exits 0.

### T7. The chain writes YAML plans (90 min, runner)

- Outcome, in `claude/.claude/workflows/docs-page-chain.js` (dotfiles worktree only):
  - A `planFormat` argument, `"yaml"` by default, `"markdown"` keeping today's behavior for an
    in-flight run. `planPathFor` returns `.plan.yaml` or `.plan.md` by it.
  - `planPrompt`, in YAML mode, tells the plan step to write the plan in the format
    `~/Projects/drafter/docs/plan-format.md` documents, with every prose field as a `|` block, and
    to run `drafter check-plan --facts docs/internal/facts <plan>` until it exits 0, reporting the
    final run's output. The plan step's `PLAN_SCHEMA` result is unchanged apart from that report.
  - `structurePrompt` in plan mode, in YAML mode, grades the plan's `step` and `failure` items:
    the reader-state walk proves consistency, not completeness, so the seat judges whether a step
    or a failure the page needs is missing (the review's finding 18).
  - The header comment documents `planFormat`.
- Files: `claude/.claude/workflows/docs-page-chain.js`, `tests/docs-page-chain-plan-format.test.mjs`.
- Acceptance: the new test loads the chain the way the existing chain tests do, renders
  `planPrompt` and the plan-mode `structurePrompt` in both formats, and asserts the YAML mode names
  `.plan.yaml`, the `drafter check-plan` command, and the `|` rule, and that markdown mode is
  byte-identical to the pre-change output for the same inputs. The existing chain tests still pass.
- Test: `bash scripts/gate.sh`.

### T8. End-to-end on one cairn page (40 min, runner)

- Outcome: the chain's plan step, rendered from the T7 chain in YAML mode and run as one Agent
  dispatch (Opus 5.5, high effort, as `planStep` sets it) in a scratch cairn-cms worktree, writes a
  YAML plan for one page Geoff names or, by default, `docs/extend/rotate-the-github-app-key.md`, and
  `drafter check-plan` exits 0 on it. The plan-mode structural read, rendered the same way, runs on
  it. Nothing in cairn-cms is committed; the scratch worktree is removed after.
- Acceptance: the plan file, the final `check-plan` output, and the structural read's verdict are
  recorded in the PR body.
- Test: the recorded `check-plan` exit 0.

### Close (30 min)

The whole-branch `diff-reviewer` reads both branches (go-conventions for `*.go`, ts-conventions for
`*.mjs` and `*.js`). The dotfiles close checklist runs: `claude-tooling-sync verify`, one
`gitleaks git` branch-history scan, the manifest record. Two PRs: `glw907/drafter` and
`glw907/dotfiles`, each body naming the other, the dotfiles one carrying the score and "Found, not
done". Geoff reads both on the review desk; the drafter PR merges first, then the dotfiles PR, then
`git -C ~/.dotfiles pull --ff-only` per pass-core "Close".

## Launch

The planning session merges the spec branch (spec, reviews, fold, and this plan; docs only) to
dotfiles `main` itself, as a hand-over, after this plan's review fold. It then launches the
executor from `~/.dotfiles` with the pass-core "Execute" line, `--name drafter-pass0`, and a
committed prompt file. The executor's first act is `EnterWorktree` in dotfiles; it creates
`~/Projects/drafter` by path in T1 and works there on a `pass0` branch after the initial commit on
`main`.

Before launch, the cairn docs sessions (`cairn-cms-aa`, `draft-docs-2b-part1`) were told on
2026-10-12 that the chain change is coming and asked not to edit `docs-page-chain.js` meanwhile.
