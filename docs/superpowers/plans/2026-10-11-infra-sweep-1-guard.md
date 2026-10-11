# Infra sweep 1, the guard: implementation plan

**Spec:** `docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`, section "Lean re-plan
(2026-10-11)" (rulings R1 to R4) and, for each check's definition, "Pass A-rest". **Evidence:**
`docs/superpowers/research/2026-10-11-infra-sweep-survivor-ledger.md` (cited below as "ledger").
**Audit:** `claude/.claude/docs/record/2026-09-28-claude-infra-audit.md` section 7 (the check
definitions) and section 5 (the findings by id).

**Outcome.** The dotfiles guard catches the defect classes that still have live instances. GA-03
is fixed. The relative-link, description-cap, and fork-skill checks exist and seed their live
violations as baseline entries for sweep-2. The vendored-skill manifest carries local overlays that
survive `update-skills`. The global CLAUDE.md has a 200-line cap. Sweep-2 (content) plans from the
baseline this pass leaves.

**Pass class:** `runner` (every task touches `scripts/**`, `tests/**`, `claude/.claude/tooling/**`,
`claude/.claude/skills/**`, or `bin/.local/bin/claude-tooling-sync`), with the `live-account` flag:
the session pushes a branch and opens a PR on `glw907/workstation`, and T2's refetch reads GitHub
through `gh api`. No `auth-data` path is touched.

**Out of scope:** duplicate-paragraph and `parity.json`, cross-repo mode, heading-citation,
orphan-doc, `check-drift --only claude` (R2, to ROADMAP Someday); any content fix to an authored
skill, agent, or doc beyond what a task names (sweep-2); cloud routines (R3); poplar (R4); any
other repo.

**End-to-end check.** On the close head, `CAIRN_GATE_LANE=light cairn-run-gate 'bash
scripts/check.sh'` prints `gate exit: 0`; `python3 claude/.claude/tooling/ratchet.py check --root .`
lists the registry ids `dead-reference`, `retired-phrase`, `relative-link`, `description-cap`, and
`fork-skill`; and the baseline holds no GA-03 entry and no entry for `vhs-cli-demos`.

**Clock estimate:** 420 task-minutes (T1 120, T2 150, T3 90, close 60). T1 and T2 run as a pair, so
the path is about 150 + 90 + 60 = 300 minutes.

## Launch

Prompt file: `docs/superpowers/plans/2026-10-11-infra-sweep-1-guard-prompt.txt`. The plan lives on
branch `worktree-infra-sweep-plan` (planning commits). The session continues that branch: its first
act after `EnterWorktree` is `git merge --no-edit worktree-infra-sweep-plan`, so its PR carries the
plan and the build together (pass-core "Execute": a pass that continues an existing branch merges
it first). Launch from the main checkout:

```bash
git -C ~/.dotfiles fetch origin
git -C ~/.dotfiles rev-list --count HEAD..origin/main   # must print 0
claude agents --json                                    # no live session with cwd in ~/.dotfiles/.claude/worktrees/infra-sweep-1
cd ~/.dotfiles && claude --bg --model sonnet --effort medium --name infra-sweep-1 \
  "$(git -C ~/.dotfiles show worktree-infra-sweep-plan:docs/superpowers/plans/2026-10-11-infra-sweep-1-guard-prompt.txt)"
```

The prompt is read with `git show` because the plan is not on `main` until this pass's PR merges.

## Conventions every task follows

- **Gate.** `CAIRN_GATE_LANE=light cairn-run-gate 'bash scripts/check.sh'`, with the Bash tool's
  `timeout: 600000`, re-issued on exit 75 until it prints `gate exit:` (dotfiles-pass). It is also
  the fast lane. A focused leg (`uv run --with pytest --no-project python -m pytest
  tests/test_check_claude_refs.py -q`) may run between edits; the task's acceptance is the gate.
- **Commits.** One commit per task, subject starting with the task id (`T1: Fix GA-03 and add the
  relative-link check`), imperative mood, specific files only. The pre-commit hook runs the
  ratchet's `hook` mode, so a commit that grows the baseline under an id registered in `HEAD` fails.
  Register a new id and seed its entries in the same commit.
- **Ratchet entries.** Each seeded entry carries `check`, `file`, `fingerprint`, `finding`, and
  `pass` (ratchet.py header). `pass` is one of the existing labels (`ratchet.py` `PASS_LABELS`):
  the letter of the audit pass that owned the finding (C for PS ids and docs, D for CS ids and
  DC-10). A violation with no audit id takes the next free `GA-nn` (GA-06 onward) with a one-line
  `defect`.
- **Tool protocol.** A ratchet tool answers `<tool> ratchet-report --root <root>` with the JSON
  `ratchet.emit_report` prints, imports `ratchet` from `Path(__file__).resolve()` (never through
  `~/.claude`), and sets `sys.dont_write_bytecode` first (ratchet.py header, "Tool protocol").
  `ratchet.py check` runs each registered tool as `[str(path), "ratchet-report", "--root", ...]`
  (`ratchet.py:264`), so the tool must be executable with a shebang.
- **Clock.** At each task start write `pass-task-clock` in the worktree's git dir (`git rev-parse
  --absolute-git-dir`) with `task=<id>`, `start=<epoch>`, `estimate=<minutes>`; remove it at the
  task's end (pass-core "Clock stop").
- **Stops.** A red the session cannot fix in two attempts, a merge conflict, or a clock stop: write
  `docs/STATUS.md` on the branch (task in flight, what failed, the one question), run `notify-send
  -u normal "infra-sweep-1: stopped"`, and wait.
- **Scope.** A defect found outside a task goes to the PR body's "Found, not done" list.

## Tasks

### T1. GA-03, the relative-link check, and the CLAUDE.md line cap

- **Outcome.** `check-claude-refs.py` self mode rewrites a `~/.local/bin/<x>` span under the tree
  only when `bin/.local/bin/<x>` is tracked in the tree (`git ls-files`, or the file's presence
  under `<root>/bin/.local/bin`); any other `~/.local/bin` span resolves against `--home`, like
  other tilde spans. A new check id `relative-link` reports every markdown link `[text](target)` in
  a scanned `.md` file whose target is relative (no scheme, no leading `/` or `~`, anchor stripped)
  and does not resolve from the file's directory. A line carrying the literal marker `link-ok` is
  exempt, matching `retired-ok`'s line rule. `claude-context-budget` fails a `CLAUDE.md` over 200
  lines (`CLAUDE_MD_LINE_CAP`, default 200, beside the token budget), and `scripts/check.sh` runs it
  over `claude/.claude/CLAUDE.md`.
- **Files.** `scripts/check-claude-refs.py`, `tests/test_check_claude_refs.py`,
  `claude/.claude/tooling/ratchet-baseline.json`, `claude/.claude/agents/cairn-docs-drafter.md`
  (marker only, line 126), `bin/.local/bin/claude-context-budget`, `scripts/check.sh`.
- **Risk class.** `runner`.
- **Acceptance.** The two GA-03 entries leave the baseline, and `dead-reference` reports no
  violation for `~/.local/bin/poplar`. `relative-link` is registered with tool
  `scripts/check-claude-refs.py`, and its seeded entries are exactly the four
  `claude/.claude/docs/bubbletea-conventions.md` links (ledger, "Probes"), each `finding: DC-10`,
  `pass: D`. `cairn-docs-drafter.md:126` carries `link-ok` and reports nothing.
  `claude-context-budget claude/.claude/CLAUDE.md` exits 0 at 199 lines. The gate prints `gate exit:
  0`.
- **Test.** Fixtures in `tests/test_check_claude_refs.py`: a tracked bin span resolves under the
  tree; an untracked `~/.local/bin` span resolves against an injected home where the file exists
  (no violation) and where it is absent (violation); a dead relative link fails; a live one, an
  `http:` link, a `#anchor`-only link, and a `link-ok` line pass; a vendored skill's dead link is
  not scanned (same scope as `dead-reference`). For the cap, a 201-line fixture `CLAUDE.md` exits 2
  and a 200-line one exits 0, run as `bash bin/.local/bin/claude-context-budget <file>` inside the
  test file or a new `tests/claude-context-budget.test.sh` added to `check.sh`.
- **Pair.** Runs as a pair with T2 (disjoint files).
- **Estimate.** 120 minutes.

### T2. Local overlays for vendored skills

- **Outcome.** A `vendored-skills.json` entry may carry `description` (replaces the frontmatter
  `description` value, single- or multi-line block form) and `note` (a paragraph inserted directly
  after the frontmatter, between `<!-- local-overlay -->` and `<!-- /local-overlay -->` lines).
  `fetch_skill` applies both after the copy, then rewrites sibling names: in a skill fetched from a
  repo that also supplies a renamed entry, a single-backtick span exactly equal to that entry's
  upstream directory name (`Path(path).name`) becomes its `rename` (for vale: `` `setup` `` to
  `` `vale-setup` ``, and likewise `fix`, `triage`, `vocab`, `ci`). `lint --root` fails (exit 1,
  naming the skill) when an installed vendored `SKILL.md` lacks its manifest `description` or
  `note`, or still carries an upstream sibling span. The manifest's `_doc` names the two fields.
  Then `update-skills` refetches every vendored skill. The overlays land, in content:
  - CS-8, `daisyui` `description`: scoped to DaisyUI markup ("Official daisyUI component reference.
    Use when writing or reviewing markup that uses DaisyUI classes or components."), never "all
    HTML and JSX".
  - CS-17, `vhs-cli-demos` `description`: under 300 characters, and the `note` says `vhs` is not
    installed on this workstation (`bluefin/Brewfile` has no `vhs`) and must be installed through
    `dependency-upgrade` first.
  - CS-10, `vale-setup`, `vale-ci`, `vale-fix` `note`: a repo here commits its Vale styles and pins
    Vale in CI, so do not run `vale sync` against a committed `styles/` directory or edit the CI
    pin; a fix lands on a pass branch, never a branch per file.
  - CS-2: `golang-spf13-cobra`'s `_why` drops "and elm-conventions" (cobra has no bubbletea surface).
- **Files.** `bin/.local/bin/claude-tooling-sync`, `tests/test_claude_tooling_sync.py`,
  `claude/.claude/tooling/vendored-skills.json`, `claude/.claude/skills/{daisyui,
  golang-spf13-cobra,vale-ci,vale-fix,vale-setup,vale-triage,vale-vocab,vhs-cli-demos}/**` (the
  refetch output).
- **Risk class.** `runner`.
- **Acceptance.** `bin/.local/bin/claude-tooling-sync lint --root .` exits 0. `grep -rn
  '`\(setup\|fix\|triage\|vocab\|ci\)`' claude/.claude/skills/vale-*/` finds no sibling span. `git
  diff` over the refetched skills shows only the overlays, the sibling rewrites, and upstream
  changes since the pinned commit; each upstream change is listed in the commit body. The gate
  prints `gate exit: 0`.
- **Test.** Fixtures in `tests/test_claude_tooling_sync.py` that call the overlay function on a
  local fixture tree (no network): a block-form and a single-line description are replaced; a
  note lands after the frontmatter once, and a second application does not duplicate it; a sibling
  span is rewritten and a code-fence line (`git switch -c vale-fix-...`) and a plain-text "fix" are
  not; `lint` fails on a missing overlay and on a leftover sibling span, and passes on a clean
  fixture.
- **Pair.** Runs as a pair with T1. If `gh api` fails (offline, rate limit), the refetch step
  stops the task, not the pair; T1 still merges.
- **Estimate.** 150 minutes.

### T3. The description-cap and fork-skill checks

- **Outcome.** `claude-tooling-sync` gains a `ratchet-report --root <root>` subcommand (the tool
  protocol above) implementing two ids. `description-cap`: a `skills/*/SKILL.md` (authored and
  vendored, `skills/synced` excluded) whose frontmatter `description`, whitespace-collapsed, is
  over 500 characters and whose frontmatter has no `paths:` key; fingerprint `description`.
  `fork-skill`: a `SKILL.md` whose frontmatter sets `context: fork` and whose body contains a
  phrase from the audit's list ("under discussion", "during the session", "delegated", "ask the
  user", case-insensitive, whitespace-tolerant); fingerprint is the phrase. Both ids are registered
  with tool `bin/.local/bin/claude-tooling-sync`, and their live violations are seeded.
- **Files.** `bin/.local/bin/claude-tooling-sync`, `tests/test_claude_tooling_sync.py`,
  `claude/.claude/tooling/ratchet-baseline.json`.
- **Risk class.** `runner`.
- **Acceptance.** `description-cap` seeds exactly `cairn-release` and `visual-fidelity` (`PS-28`,
  `C`), `go-conventions` and `tui-visual-verify` (`GA-06`, `D`, defect "description over 500
  characters with no paths: gate"), and `svelte-check` (`GA-07`, `C`, same defect); none for
  `vhs-cli-demos` (T2's override) or `golang-spf13-cobra` (gated). `fork-skill` seeds only
  `register-check` (`PS-06`, `C`) and `content-review` (`PS-20`, `C`) entries. If the phrase list
  misses PS-20's "Ask 'apply all..." line (`content-review/SKILL.md:46-47`), the list gains the
  narrowest phrase that catches it and the commit body says so. The gate prints `gate exit: 0`.
- **Test.** Fixtures: a 501-character ungated description fails; a 500-character one and a
  901-character `paths:`-gated one pass; a block-form description is measured after collapse; a
  fork skill with "under discussion" fails, the same body without `context: fork` passes, and a
  fork skill with none of the phrases passes; `ratchet-report` output parses as the
  `emit_report` JSON with both ids in `implements`.
- **Estimate.** 90 minutes. Starts after the T1 and T2 pair merges (it edits T2's file and T1's
  baseline).

### Close

Per pass-core "Close" and dotfiles-pass "Close checklist", in order:

1. The gate on the close head prints `gate exit: 0` (the full-suite home).
2. `diff-reviewer` at whole-branch scope reads the branch against this plan, loading
   `python-conventions` (the changed `*.py` and the Python tools). One batched fix chain follows if
   it returns `fix`, each finding quoted verbatim as the fix's acceptance, then the gate again.
3. `claude-tooling-sync verify` passes; one `gitleaks git` branch-history scan is clean.
4. `docs/STATUS.md`: the infra sweep section names sweep-2 as next, planned from the baseline this
   pass leaves, with the baseline's entry count by pass label.
5. Push `glw907/workstation`, open the PR (draft until the close is done), and write its body:
   what landed (task id, commit), the review verdict, "Found, not done", and the score rows
   (pass-core "Score"; `cairn-run-gate --records <toplevel> <branch>` for gate and lock time).
   Geoff reads and merges. No `stow -R bin` is owed: the pass adds no new script.
- **Estimate.** 60 minutes.
