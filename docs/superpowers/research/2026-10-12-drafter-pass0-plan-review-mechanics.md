# drafter Pass 0 plan: mechanics and feasibility review

Target: `docs/superpowers/plans/2026-10-12-drafter-pass0-plan.md` at `e726371`. Reviewer: the
`plan-reviewer` agent, 2026-10-12, with probes (scratch Go module, scratch chain copy, installed
tools) or quoted docs for every claim. Saved by the dispatching session; content as reported.

**Verdict:** feasible in shape, but not launchable as written: T7 turns the chain gate red
(reproduced), the T3/T5 pair can't be isolated, the plan schema is defined nowhere, and two premises
fail against cairn's data (the fact-bullet layout, and links to siblings not yet on disk). 2
blockers, 13 majors, 15 minors.

## Blockers

1. **[blocker, correctness] T7 (plan :135-153): the YAML default breaks 20 existing chain tests,
   and the new test never runs in the gate.** With only `planPathFor` changed to `.plan.yaml`,
   `node tests/docs-page-chain-outline.test.mjs` fails 20 dry-run checks; HEAD prints `ALL PASS`.
   `stubPlan` matches `/docs\/internal\/briefs\/\S+?\.plan\.md/` (outline test :142), and `.plan.md`
   is hard-coded at :1027, :1171, :1210, :1226. `scripts/check.sh:60-68` lists each test by name, so
   a new test file never runs. Fold: add the outline test to T7's files and pass `planFormat:
   "markdown"` in `baseArgs` or move the stub to the YAML suffix; better, put the new checks in the
   outline test file, which has the runner harness (`runRunner`, `makeAgent`); if a new file stays,
   add its `run` line to `scripts/check.sh`.
2. **[blocker, correctness] The T3/T5 pair can't be worktree-isolated (plan :95, :124).** pass-core
   "Pairs" uses Agent subagents with `isolation: "worktree"`; per code.claude.com/docs/en/worktrees,
   subagent worktrees come from the session's repository, which is dotfiles after `EnterWorktree`.
   Both subagents would edit `~/Projects/drafter` by path on one branch, with `index.lock` races; T5
   also documents checks T3 is still building. Fold: drop the pair and run T5 after T3, or pair T7
   (dotfiles, where isolation works) with T3.

## Majors

3. **[major, correctness] T2/T3: the plan schema is never defined.** T3 checks `requires` against
   "the plan's preconditions", which T2 never lists; `opens` exists only in the plan; the spec gives
   no shape for `requires`/`produces`, `dispositions`, or `friction`; whether an item's id is the
   fact id is undecided (and if so, one fact in two sections breaks id uniqueness); items are nested
   in sections and also carry `section`. An unattended Sonnet executor would design public surface.
   Fold: a field table in T2 (fields, types, required, which are prose), the item-id versus `fact:`
   rule, and either nesting or the `section` field, not both.
4. **[major, correctness] T3 fact citability: one bullet in five wraps its tag.** 333 of 1,672
   `` - `f:`` bullets in cairn's facts files don't end in `]` on their first line. Cairn's reader
   excludes `README.md` (`check-facts.mjs:765-768`), skips `## Harvest record` and `## Provenance`
   (`SKIPPED_SECTIONS`, :92), and ignores brackets inside code spans; the tag vocabulary is
   `verified, docs-drift, external, vendor, candidate, rejected` (:95). Fold: make
   `scripts/checks/check-facts.mjs` (`extractBullets`, `checkTag`, `factsFiles`) the reference; state
   the citable allow-list (`verified`, `external`, `vendor`); add fixture rows for a wrapped bullet,
   a bracket in a code span, a skipped section, and README exclusion.
5. **[major, correctness] OWNER FORK: links to siblings not yet drafted.** `extend.json` lists 25
   pages, 14 not on disk, with 71 crossLinks; "target file exists" can never pass for them, and "run
   until exit 0" never ends. Options: (a) a warning for a target the outline lists but isn't on disk;
   (b) an error the planner reports as `couldNotDo`; (c) skip the anchor check for missing targets.
   Recommendation (a).
6. **[major, correctness] OWNER FORK: cairn's review page and docs read only `.plan.md`.**
   `scripts/docs-review/embed.mjs:64-84` builds `<slug>.plan.md`; `docs/internal/briefs/README.md`
   (:81-87) documents it. Options: (a) a cairn task and third PR; (b) a cairn follow-up before the
   next chain run; (c) accept the gap. Recommendation (b), recorded as "Found, not done", "now".
7. **[major, correctness] yaml.v3 accepts duplicate keys, and `Node.Decode` ignores `KnownFields`.**
   Probed on `gopkg.in/yaml.v3` v3.0.1 and `go.yaml.in/yaml/v3` v3.0.5: `id: a\nid: b` unmarshals
   into a Node without error; `n.Decode(&item)` with an unknown field returns nil; an empty document
   gives an empty Node. Fold: the Node walk itself checks unknown, required, and typed fields and
   duplicate keys; add duplicate-key and empty-document rows.
8. **[major, correctness] T4 e2e fixture state is unnamed.** (a) passes only if the fixture marks
   the two gap steps `canFail: true` with no failure item; (b) needs a `--root` tree with every linked
   page and anchor (the spike plan has 27 links and 27 fact ids) and a facts subset. The `--root`
   default is never exercised (testdata isn't its own repo). Fold: name the fixture tree, the
   `canFail` marking, the facts subset, a `git init` temp-dir row for the default, and cite the
   spike's final-reader output for the two gaps. Prefer synthetic stub pages, since the repo is
   public.
9. **[major, correctness] T7 "byte-identical markdown mode" needs a golden file and a loader.**
   `planPrompt` and `structurePrompt` read module state, so the derivation test's marker extraction
   can't load them. Loaders that work: the outline test's full-runner dry run (:111-115), or the
   spike's `chainprompts.mjs` slice. Fold: before any edit, render both prompts in markdown mode for
   fixed inputs into `tests/fixtures/`, and compare against those.
10. **[major, correctness] T7's validator loop is unbounded and unchecked.** The runtime has no exec
    access (chain :87). Fold: a `PLAN_SCHEMA` field such as `checkPlan: { exit, output }`;
    `planStep` escalates when it's missing or nonzero; the prompt caps the loop (three runs, then
    `couldNotDo`); name the rework case (a committed `.plan.md` beside a new `.plan.yaml`).
11. **[major, correctness] Launch preconditions aren't met.** `~/.dotfiles` is on
    `drafter-pipeline-spec`, not `main`, with `bash/.bashrc` modified (+15 lines, an `auth-data`
    path). `cd ~/Projects/drafter` doesn't stick outside allowed directories. A remote added during
    a session isn't trusted by the auto-mode classifier. Fold: the planner switches `~/.dotfiles` to
    `main`, pulls, and names the `.bashrc` change's owner; the planner creates `~/Projects/drafter`
    and its GitHub repo before launch; launch with `--add-dir ~/Projects/drafter`; name both push
    targets.
12. **[major, correctness] T6's `check-drift` acceptance fails during the pass.** `check-drift`
    reads `$HOME/.dotfiles` (:14-15), not the worktree. Fold: merge T6 into T4; in-pass acceptance is
    `command -v drafter` plus a grep of the worktree manifest; `check-drift` moves to Close.
13. **[major, correctness] New dependencies are unnamed, and `gopkg.in/yaml.v3` is archived**
    (archived April 1, 2025; the YAML org maintains `go.yaml.in/yaml/v3`, same LineComment behavior
    on v3.0.5). Fold: name cobra, `go.yaml.in/yaml/v3`, and heading extraction (goldmark or a
    scanner that skips fenced code and strips inline markup as rehype-slug's `toString` does); drop
    TOML if the override is deferred.
14. **[major, correctness] Absent, empty, malformed, and mixed states have no named report.** An
    empty plan; malformed YAML (exit 1 or 2?); several plans with mixed failures; `--facts` missing or
    empty; a fact id in no file (spec :809 requires this row); a bullet with no or an unknown tag; a
    duplicate fact id across files; the no-facts warning (spec :497); an `https://` link, a same-page
    anchor, a directory target; a malformed `drafter.toml`; the exit code when only warnings remain.
    Fold: one line per state with its report and exit code, the spec's missing rows, and a clean twin
    for each negative row.
15. **[major, optional] T8 is feasible as an Agent dispatch, but its renderer is unnamed.** Name
    `~/.local/share/drafter/spike/chainprompts.mjs` with `job-rotate-current.json` (plus
    `planFormat: "yaml"` and the scratch path) and `rotate-pageinputs.json`; base the scratch worktree
    on `origin/main`; the no-claim file under `~/.cache/docs-page-chain/` is shared with live runs.

## Minors

16. The clock-stop hook reads the git dir from the hook input's `cwd` (`claude-clock-stop:14-17`):
    name one clock-file location.
17. drafter has no adapter: state its gate (`cairn-run-gate 'make -C ~/Projects/drafter check'`, light
    lane), local full-suite home, and a `gitleaks git` scan.
18. T1's skeleton on `main` escapes the whole-branch review: put only `go.mod` and the README on
    `main`, or review from the root commit.
19. Close: two `diff-reviewer` runs; after the drafter merge, switch to `main`, pull, and `make
    install`.
20. (optional) Embed `docs/plan-format.md` with `go:embed` and expose it, so the chain names a
    command, not a checkout path.
21. Estimates: T3 is more like 120-150, T4 80-100; total about 560-600, still under 700.
22. T1's `gh repo create` touches a real GitHub account; creating the repo before launch keeps
    "no live-account" true.
23. (optional) OWNER FORK: defer the `drafter.toml` facts-pattern override; recommendation defer.
24. (optional) `--json` has no consumer: one e2e row, or defer.
25. (optional) Schema sync test: compare field names and `required` sets by reflection, stdlib only.
26. `github-slugger`'s npm package doesn't ship its fixtures: vendor `test/fixtures.json` with its
    ISC notice, or generate with cairn's installed copy; cover a heading with an existing `id`; skip
    fenced code.
27. Record the standing answers for the plan-overrun ceiling and per-task clock stops.
28. (optional) T8 commits nothing, so `ordinary` fits.
29. (optional) List the prose fields; add a plain multi-line value with `# tail` (truncated) as a row.
30. (optional) At Close, tell the cairn sessions the merge time and the `planFormat: "markdown"`
    escape hatch.
