# drafter Pass 0 plan review fold

Folds `2026-10-12-drafter-pass0-plan-review-mechanics.md` (30 findings) into
`docs/superpowers/plans/2026-10-12-drafter-pass0-plan.md`, 2026-10-12. Each finding was checked
against source or a probe before it was acted on. Task numbers below are the revised plan's: old T6
merged into T4, old T7 is now T6, and old T8 is now T7.

Probes run for this fold: a scratch Go module on `go.yaml.in/yaml/v3` v3.0.5 (duplicate keys,
`Node.Decode` with unknown fields, empty and second documents, one-line and multi-line plain values
with `# tail`); `go list -m` for cobra v1.10.2, goldmark v1.8.6, and yaml v3.0.5; cairn's
`scripts/checks/check-facts.mjs` (`extractBullets`, `checkTag`, `factsFiles`, `FACT_ID_RE`,
`SKIPPED_SECTIONS`) and `docs/internal/facts/README.md:187-188`; `scripts/docs-review/embed.mjs`
`planPathFor`; `docs/internal/outlines/extend.json` (`pages[].path`); github-slugger's repo (tag
`2.0.0` has `test/fixtures.json`, 78 cases; the installed npm 2.0.0 has no `test/`; ISC `LICENSE`);
cairn's `src/lib/render/pipeline.ts` (rehype-raw, sanitize, then rehype-slug); the spike's
`run-rotate-the-github-app-key-edit2/reader.response.json` (both recovery gaps);
`claude-clock-stop:14-17`; `check-drift:14`; `scripts/gate.sh`'s header; `scripts/check.sh:60`;
code.claude.com/docs/en/worktrees; `claude --help` (`--bg`, `--add-dir`, `--name`); `go help build`
(`-C dir`).

## Dispositions

| # | Finding | Disposition |
|---|---|---|
| 1 | T7 YAML default breaks the outline test | Folded, T6: existing cases pass `planFormat: "markdown"` via `baseArgs`; new YAML cases go in the outline test file, which `scripts/check.sh:60` already runs. Verified `stubPlan`'s `.plan.md` regex at outline test :142. |
| 2 | T3/T5 pair can't be isolated | Folded, T3: T5 runs after T4; T3 pairs with T6 instead (T3 subagent unisolated as drafter's only writer, T6 subagent worktree-isolated in dotfiles). Docs quote: isolation checks "apply to the repository you launched Claude Code from". |
| 3 | Plan schema undefined | Folded, T2: field table, item kind table, prose column, item id separate from fact id, nesting with no `section` field, placed facts as items and dispositions for subordinated and cut only. Fields drawn from the chain's `planPrompt` (three-part introduction, `opens`, order reason). |
| 4 | Fact bullets wrap their tags | Folded, T3: `check-facts.mjs` named as the reference with its functions; citable allow-list `verified`, `external`, `vendor` (cairn README :187); rows for a wrapped tag, a code-span bracket, `## Provenance`, README exclusion. |
| 5 | Links to siblings not yet drafted | Owner ruling applied (option a), T3, T4, T6: `--outline <file>` reads `pages[].path`; a listed target not on disk is a warning, anchor unchecked; any other missing target is an error; warnings exit 0; the chain adds `--outline` when the run has `args.outline`. |
| 6 | cairn review page reads only `.plan.md` | Owner ruling applied (option b), "Shape" and Close: cairn follow-up before the next YAML chain run, in "Found, not done" with disposition "now". Verified `embed.mjs:72-76`. |
| 7 | Duplicate keys, `Node.Decode` ignores `KnownFields` | Folded, T2: probed on v3.0.5 and confirmed; the Node walk checks unknown, required, typed, and duplicate fields, plus empty and second documents (second-document drop found by this fold's probe). |
| 8 | T4 e2e fixture state unnamed | Folded, T4: synthetic `e2e/testdata/project/` (stub pages, facts file, outline), `canFail` gap form and clean form, a `git init` row for the default root, provenance cited to the spike's reader response; no cairn text in the public repo. |
| 9 | Markdown-mode byte identity needs goldens | Folded, T6: render both prompts through the outline test's full-runner dry run before any edit, saved under `tests/fixtures/docs-page-chain/`. |
| 10 | Validator loop unbounded and unchecked | Folded, T6: optional `checkPlan: { exit, output }` in `PLAN_SCHEMA`; `planStep` escalates on missing or nonzero in YAML mode; three runs per write, then `couldNotDo`; rework case: the step reads the committed `.plan.md` as the prior plan and deletes it once `.plan.yaml` is written. |
| 11 | Launch preconditions unmet | Folded, "Launch": per the planner's launch shape (dotfiles back to `main` via PR, drafter created with `go.mod` and README and pushed, `--add-dir`, both push targets, `bash/.bashrc` owned by another session and never touched). |
| 12 | `check-drift` fails mid-pass | Folded: old T6 merged into T4 with `command -v drafter` and a worktree manifest grep; `check-drift` moves to Close after the merge and pull. Verified `check-drift:14` reads `$HOME/.dotfiles`. |
| 13 | Dependencies unnamed, yaml.v3 archived | Folded, "Shape": cobra v1.10.2, `go.yaml.in/yaml/v3` v3.0.5, goldmark v1.8.6, each confirmed by `go list -m`; TOML dropped. |
| 14 | Absent, empty, malformed, mixed states | Folded, T4: one-row-per-state table with report and exit code; T3 rows for the spec's missing cases (id in no facts file, no and unknown tag, id on two bullets, no-facts warning, `https://`, same-page anchor, directory target). The malformed `drafter.toml` row is moot with TOML dropped. |
| 15 | T8 renderer unnamed | Folded, T7: `chainprompts.mjs` with `job-rotate-current.json` (chain path and `planFormat` set) and `rotate-pageinputs.json`; scratch worktree on `origin/main`; no-claim path rewritten to scratch. |
| 16 | One clock-file location | Folded, "Standing approvals": the dotfiles pass worktree's git dir; cwd stays there and drafter commands take `-C` paths. Verified the hook reads `cwd` (`claude-clock-stop:14-16`). |
| 17 | drafter has no adapter | Folded, "Shape" and T1: gate `bash scripts/drafter-gate.sh` (a no-argument wrapper, since the worktree-isolated Bash guard refuses `cairn-run-gate '<string>'`, per `scripts/gate.sh`), light lane, local full-suite home, `gitleaks git` at Close. T1 becomes `runner` for the wrapper. |
| 18 | T1 skeleton on `main` escapes review | Folded, "Launch" and Close: `main` holds only `go.mod` and the README; the pass works on `pass0`. |
| 19 | Close: two reviews, then install | Folded, Close: two whole-branch `diff-reviewer` runs; a `## Before merge` section for the drafter merge, switch to `main`, pull, and `make install`. |
| 20 | Embed `plan-format.md`, expose a command | Refused: a new command is public surface the spec's command table doesn't list; the chain is a workstation script and may name the checkout path. |
| 21 | Re-estimate | Folded: T3 150, T4 110 (with old T6); total 615 against the 700 line. |
| 22 | `gh repo create` touches a real account | Folded, "Launch": the planner creates the public repo before launch, so the pass keeps no `live-account` flag. |
| 23 | Facts-pattern override | Owner ruling applied: deferred to the configuration pass; "Shape" states it governs reading facts files, not plans, and adds the stability rule (`version: 1`, later passes add only optional fields). TOML and `drafter.toml` dropped. |
| 24 | `--json` has no consumer | Folded, T4: the spec says every command takes `--json`; field list named and one e2e row added. |
| 25 | Schema sync by reflection | Folded, T2 acceptance: field names and required sets compared by reflection, standard library only. |
| 26 | github-slugger fixtures not in npm | Folded, T3: vendor `test/fixtures.json` at tag `2.0.0` with its ISC `LICENSE`, the same notice on the `regex.js` port; fenced code skipped. The existing-`id` row is refused: in cairn a heading's `id` can come only from raw HTML, which passes through rehype-raw and sanitize before rehype-slug, so its final anchor depends on the sanitize schema; raw-HTML headings are documented as not anchors this pass. |
| 27 | Standing answers | Owner ruling applied, "Standing approvals": continue while elapsed task-minutes stay under 900, the same answer for a clock stop; past 900, STATUS, `notify-send -u normal`, wait. |
| 28 | T8 commits nothing, so `ordinary` | Folded, T7 is `ordinary`; the pass stays `runner` from T1 and T6. |
| 29 | List prose fields, multi-line comment row | Folded, T2: prose column; probe confirmed a two-line plain value's `# tail` lands in `LineComment`; row added. |
| 30 | Tell cairn sessions at Close | Folded, Close: the merger tells the cairn docs sessions the merge time and the `planFormat: "markdown"` escape hatch. |

Count: 25 folded (26 with its existing-`id` row refused), 4 owner rulings applied (5, 6, 23, 27),
and 1 refused (20). Geoff's T7 page choice and the launch shape the planning session set are
applied in the plan without a finding number.

## Contestable points this fold decided

- The rework case deletes the committed `.plan.md` once `.plan.yaml` is written (T6), so each page
  keeps one plan. Until the cairn review-page follow-up lands, such a page shows no plan there.
- A same-page anchor must match the plan's title or a section heading; an anchor to a sub-heading
  the plan doesn't list is an error the planner fixes by listing it.
- T1 adds `scripts/drafter-gate.sh` to dotfiles, a `runner` path, so later drafter passes launched
  from dotfiles reuse it.
