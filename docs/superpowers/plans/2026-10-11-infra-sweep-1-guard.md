# Infra sweep 1, the guard: implementation plan

**Spec:** `docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`, section "Lean re-plan
(2026-10-11)" (rulings R1 to R4) and, for each check's definition, "Pass A-rest". **Evidence:**
`docs/superpowers/research/2026-10-11-infra-sweep-survivor-ledger.md` (cited below as "ledger").
**Audit:** `claude/.claude/docs/record/2026-09-28-claude-infra-audit.md` section 7 (the check
definitions) and section 5 (the findings by id). **Review:** the three lenses and the fold record,
`docs/superpowers/research/2026-10-11-infra-sweep-1-guard-{review-contract,review-mechanics,review-risk,plan-fold}.md`.

**Outcome.** The dotfiles guard catches the defect classes that still have live instances. GA-03
is fixed. The relative-link, description-cap, and fork-skill checks exist and seed their live
violations as baseline entries for sweep-2. The vendored-skill manifest carries local overlays,
applied offline to the installed copies and reapplied by every future fetch. The global CLAUDE.md
has a 200-line cap. Sweep-2 (content) plans from the baseline this pass leaves.

**Pass class:** `runner` (every task touches `scripts/**`, `tests/**`, `claude/.claude/tooling/**`,
`claude/.claude/skills/**`, or `bin/.local/bin/claude-tooling-sync`), with the `live-account` flag:
the session pushes a branch and opens a PR on `glw907/workstation`. No task reads a vendored
skill's upstream. No `auth-data` path is touched.

**Out of scope:** duplicate-paragraph and `parity.json`, cross-repo mode, heading-citation,
orphan-doc, `check-drift --only claude` (R2, to ROADMAP Someday); any content fix to an authored
skill, agent, or doc beyond what a task names (sweep-2); a refetch of any vendored skill or a move of
its pinned `commit` (the next `dependency-upgrade` sweep); cloud routines (R3); poplar (R4); any
other repo, including the CLAUDE.md files of dubplate (356 lines) and aksailingclub-org (262), which
the cap does not reach.

**End-to-end check.** On the close head:

1. `bash scripts/gate.sh` prints `gate exit: 0`.
2. `python3 claude/.claude/tooling/ratchet.py check --root .` exits 0. A clean run prints nothing.
3. `python3 -I -c 'import json; d = json.load(open("claude/.claude/tooling/ratchet-baseline.json")); print(sorted(d["checks"])); print(sorted({e["finding"] for e in d["entries"]})); print([e["file"] for e in d["entries"] if "vhs-cli-demos" in e["file"]])'`
   prints the five ids (`dead-reference`, `description-cap`, `fork-skill`, `relative-link`,
   `retired-phrase`), a finding list with no `GA-03`, and `[]`.

**Clock estimate:** 420 task-minutes (T1 130, T2 120, T3 100, close 70). T1 and T2 run as a pair, so
the path is about 130 + 100 + 70 = 300 minutes.

## Launch

Prompt file: `docs/superpowers/plans/2026-10-11-infra-sweep-1-guard-prompt.txt`. The plan lives on
branch `worktree-infra-sweep-plan` (planning commits). The session continues that branch: its first
act after `EnterWorktree` is `git merge --no-edit worktree-infra-sweep-plan`, so its PR carries the
plan and the build together (pass-core "Execute": a pass that continues an existing branch merges
it first). Launch from the main checkout, after every check prints what its comment names:

```bash
git -C ~/.dotfiles fetch origin
git -C ~/.dotfiles branch --show-current                # must print main
git -C ~/.dotfiles rev-list --count HEAD..origin/main   # must print 0 (not behind)
git -C ~/.dotfiles rev-list --count origin/main..HEAD   # must print 0 (not ahead)
git -C ~/.dotfiles status --porcelain                   # must print nothing
git -C ~/.dotfiles/.claude/worktrees/infra-sweep-plan status --porcelain   # must print nothing
git -C ~/.dotfiles rev-parse worktree-infra-sweep-plan origin/worktree-infra-sweep-plan   # two equal lines
claude agents --json                                    # no live session with cwd in ~/.dotfiles/.claude/worktrees/infra-sweep-1
cd ~/.dotfiles && claude --bg --model sonnet --effort medium --name infra-sweep-1 \
  "$(git -C ~/.dotfiles show worktree-infra-sweep-plan:docs/superpowers/plans/2026-10-11-infra-sweep-1-guard-prompt.txt)"
```

The prompt is read with `git show` because the plan is not on `main` until this pass's PR merges.
The ahead check matters because `worktree.baseRef: "head"` branches from local `HEAD`, so an
unpushed `main` commit would ride into the PR.

## Conventions every task follows

- **Gate.** `bash scripts/gate.sh`, with the Bash tool's `timeout: 600000`, re-issued on exit 75
  until it prints `gate exit:`. It is also the fast lane. The wrapper runs `cairn-run-gate 'bash
  scripts/check.sh'` on the light lane. A worktree-isolated session's Bash guard refuses that
  wrapped form ("cannot be shown not to be git"; dotfiles #2's "Found, not done") and accepts the
  no-argument wrapper, which keeps the lane lock and the `--records` score (probed 2026-10-11 from
  this plan's worktree: `gate exit: 0`, one record of 112 s). This overrides the dotfiles-pass Gate
  line loaded from `main` until this pass merges. Never fall back to a bare `bash scripts/check.sh`
  for an acceptance. A focused leg (`uv run --with pytest --no-project python -m pytest
  tests/test_check_claude_refs.py -q`) may run between edits; the task's acceptance is the gate.
- **The main checkout stays untouched.** Every tool runs from the worktree's own path
  (`bin/.local/bin/<tool>`, `scripts/<tool>`), never as a bare name: `~/.local/bin/<tool>` is a stow
  link to the main checkout's copy. No command writes `~/.dotfiles` outside `.claude/worktrees/`.
- **Commits.** One commit per task, subject starting with the task id (`T1: Fix GA-03 and add the
  relative-link check`), imperative mood, specific files only. The pre-commit hook runs the
  ratchet's `hook` mode, so a commit that grows the baseline under an id registered in `HEAD` fails.
  Register a new id and seed its entries in the same commit. A seed missed there is fixed by
  amending that unpushed commit, since a later commit cannot add an entry under an id `HEAD`
  registers.
- **Ratchet entries.** Each seeded entry carries `check`, `file`, `fingerprint`, `finding`, and
  `pass` (ratchet.py header), plus `count` when the same key occurs more than once. `pass` is one
  of the existing labels (`ratchet.py` `PASS_LABELS`): the letter of the audit pass that owned the
  finding (C for PS ids and docs, D for CS ids and DC-10). A violation with no audit id takes the
  next free `GA-nn` (GA-06 onward) with a one-line `defect`; one GA id may carry entries with
  different `pass` labels.
- **Tool protocol.** A ratchet tool answers `<tool> ratchet-report --root <root>` with the JSON
  `ratchet.emit_report` prints, and accepts the `--home`, `--projects-root`, and `--memory-root`
  flags `ratchet.py check` forwards (`ratchet.py:377-388`), reading only those it needs. It imports
  `ratchet` from `Path(__file__).resolve()` (never through `~/.claude`) and sets
  `sys.dont_write_bytecode` first (ratchet.py header, "Tool protocol"). `ratchet.py check` runs
  each registered tool as `[str(path), "ratchet-report", "--root", ...]` (`ratchet.py:264`), so
  the tool must be executable with a shebang.
- **Clock.** At each task start the session writes `pass-task-clock` in its own pass worktree's git
  dir (`git rev-parse --absolute-git-dir`) with `task=<id>`, `start=<epoch>`, `estimate=<minutes>`,
  and removes it at the task's end (pass-core "Clock stop"). For the pair, the session writes one
  file (`task=T1+T2`, `estimate=130`) before dispatch, checks the pair's overrun when both return,
  then removes it. Pair worktrees hold no clock file, and the pair subagents write none.
- **Stops.** A red the session cannot fix in two attempts, a merge conflict, or a clock stop: write
  `docs/STATUS.md` on the branch (task in flight, what failed, the one question), run `notify-send
  -u normal "infra-sweep-1: stopped"`, and wait. A pair subagent that cannot get its gate green in
  two attempts, or whose T2 trigger check misses twice, returns its work to the session
  uncommitted. The session then applies this rule before merging either half of the pair.
- **Scope.** A defect found outside a task goes to the PR body's "Found, not done" list. A pair
  subagent lists such defects in its final report, and the session carries them to the PR body.

## Tasks

### T1. GA-03, the relative-link check, and the CLAUDE.md line cap

- **Outcome.**
  - GA-03: `check-claude-refs.py` self mode judges a `~/.local/bin/<x>` span against the tree
    (`<root>/bin/.local/bin/<x>`) when that file exists in the tree, or when the realpath of
    `<home>/.local/bin/<x>` sits in a directory whose last three components are `bin/.local/bin`
    (a stow link, file-level or folded, dangling or not). Any other `~/.local/bin` span resolves
    against `--home`, like other tilde spans. So a branch that deletes a stowed bin still fails on a
    doc that cites it, and an unstowed install such as `poplar` resolves through home. The module
    docstring states the rule and that an unstowed span's red means "install it or re-cite it".
  - `relative-link`, a new check id: every markdown link `[text](target)` in a `.md` file of the
    `dead-reference` scan set whose target is relative (no scheme, no leading `/`, `~`, or `#`) and
    does not resolve from the file's directory once any `#anchor` is stripped. The fingerprint is
    the target as written, anchor stripped; repeated dead links to one target in one file report
    under one key and add up to its count. A line carrying the literal marker `link-ok`, written as
    `<!-- link-ok -->` at the line's end, is exempt, matching `retired-ok`'s line rule.
  - Line cap: `claude-context-budget` fails a `CLAUDE.md` over 200 lines (`CLAUDE_MD_LINE_CAP`,
    default 200) only when the file's realpath ends in `/claude/.claude/CLAUDE.md`: the tree copy,
    any worktree's copy, and `~/.claude/CLAUDE.md` through its stow link (probed: its realpath is
    `~/.dotfiles/claude/.claude/CLAUDE.md`). It applies in file and `--hook` modes, with its own
    message naming lines, the cap, and `~/.claude/docs/claude-md-archive.md` as the place for moved
    detail. Every other `CLAUDE.md` keeps only the token budget. `scripts/check.sh` runs the
    tree's copy, `bash bin/.local/bin/claude-context-budget claude/.claude/CLAUDE.md`, and the new
    test file.
- **Files.** `scripts/check-claude-refs.py`, `tests/test_check_claude_refs.py`,
  `claude/.claude/tooling/ratchet-baseline.json`, `claude/.claude/agents/cairn-docs-drafter.md`
  (marker only, line 126), `bin/.local/bin/claude-context-budget`,
  `tests/claude-context-budget.test.sh` (new), `scripts/check.sh`.
- **Risk class.** `runner`.
- **Acceptance.**
  - The two GA-03 entries leave the baseline, and `dead-reference` reports no violation for
    `~/.local/bin/poplar` (installed in home as a regular file, probed). The GA-05 entry for
    `~/.local/bin/scoped-test` stays, since home lacks it.
  - `relative-link` is registered with tool `scripts/check-claude-refs.py`, and its seeds are
    exactly two entries in `claude/.claude/docs/bubbletea-conventions.md`, fingerprints
    `research/2026-04-26-bubbletea-norms.md` (lines 11 and 632) and
    `research/2026-04-26-reference-apps.md` (lines 13 and 636), each `count: 2`, `finding: DC-10`,
    `pass: D`. Four entries would fail `ratchet.parse` as duplicates (probed).
  - `cairn-docs-drafter.md:126` carries `<!-- link-ok -->` and reports nothing.
  - The gate prints `gate exit: 0`.
- **Test.**
  - In `tests/test_check_claude_refs.py`: a bin present in the fixture tree resolves under the
    tree (the existing `test_f2` stays green); a stow-style symlink in the fixture home
    (`<home>/.local/bin/foo` to a `<tmp>/stow/bin/.local/bin/foo` that exists), with no
    `bin/.local/bin/foo` in the tree, is a violation; a regular file in the fixture home, absent from
    the tree, passes; a span absent from both is a violation. The audited run still reads nothing
    outside the fixture's temp dir.
  - Relative links: a dead link fails; the same dead target twice in one file matches one entry
    with `count: 2`; a live link, a live `exists.md#section` link, an `http:` link, a `#anchor`-only
    link, a `/`-leading and a `~`-leading link, and a `<!-- link-ok -->` line are not reported; a
    vendored skill's dead link is not scanned.
  - In `tests/claude-context-budget.test.sh` (the `claude-clock-stop.test.sh` pattern): a 201-line
    `CLAUDE.md` under a fixture `claude/.claude/` exits 2 with the line message, a 200-line one
    exits 0, and a 250-line `CLAUDE.md` at any other path exits 0 in file mode and under `--hook`.
- **Pair.** Runs as a pair with T2 (disjoint files).
- **Estimate.** 130 minutes.

### T2. Local overlays for vendored skills

- **Outcome.**
  - A `vendored-skills.json` entry may carry `description` and `note`. One overlay function in
    `claude-tooling-sync` applies an entry's overlays to an installed skill directory:
    - the frontmatter `description` value, in any form (single-line, quoted, or block), is replaced
      by the manifest value written as a folded block, `description: >-` followed by indented
      wrapped lines, which stays valid YAML whatever the text holds (probed: a plain scalar with
      `: ` or a leading quote fails a YAML parse, the folded form round-trips);
    - `note` lands as a paragraph directly after the frontmatter, between `<!-- local-overlay -->`
      and `<!-- /local-overlay -->` lines, replacing any marked block already there;
    - CS-6, sibling names: in a skill from a repo that also supplies a renamed entry, a
      single-backtick span exactly equal to a renamed entry's upstream directory name
      (`Path(path).name`) becomes its `rename`, outside fenced code blocks only (for vale:
      `` `setup` `` to `` `vale-setup` ``, and likewise `fix`, `triage`, `vocab`, `ci`).
  - A new `apply-overlays --root TREE` subcommand applies the function to every vendored skill
    installed under TREE, reading TREE's manifest. It makes no network call and writes nothing
    outside TREE. `fetch_skill` calls the same function after its copy, so a future refetch, run
    through `dependency-upgrade`, keeps the overlays. No refetch runs in this pass: no vendored
    path changed upstream since its pin (review probe), and a refetch would revert the local
    `vale-ci` pin bump (`4cb4d62`).
  - `lint --root` fails (exit 1, naming the skill) when an installed vendored `SKILL.md`'s
    whitespace-collapsed `description` differs from the collapsed manifest value, its marked note
    block's stripped text differs from the manifest `note`, or a sibling span remains outside a
    fence. The manifest's `_doc` names the two fields and `apply-overlays`.
  - The overlays, in content:
    - CS-8, `daisyui` `description`: scoped to DaisyUI markup ("Official daisyUI component
      reference. Use when writing or reviewing markup that uses DaisyUI classes or components."),
      never "all HTML and JSX".
    - CS-17, `vhs-cli-demos` `description`: under 300 characters, and the `note` says `vhs` is not
      installed on this workstation (`bluefin/Brewfile` has no `vhs`) and must be installed through
      `dependency-upgrade` first.
    - CS-10, `vale-setup`, `vale-ci`, `vale-fix` `note`: a repo here commits its Vale styles and
      pins Vale in CI, so do not run `vale sync` against a committed `styles/` directory or edit the
      CI pin; a fix lands on a pass branch, never a branch per file.
    - CS-2: `golang-spf13-cobra`'s `_why` drops "and elm-conventions" (cobra has no bubbletea
      surface).
- **Files.** `bin/.local/bin/claude-tooling-sync`, `tests/test_claude_tooling_sync.py`,
  `claude/.claude/tooling/vendored-skills.json` (edited by hand, not reflowed),
  `claude/.claude/skills/{daisyui,vale-ci,vale-fix,vale-setup,vale-triage,vhs-cli-demos}/SKILL.md`
  (the `apply-overlays` output).
- **Risk class.** `runner`.
- **Acceptance.**
  - `bin/.local/bin/claude-tooling-sync apply-overlays --root .`, run from the T2 worktree,
    applies the overlays; a second run leaves `git diff` unchanged.
  - `bin/.local/bin/claude-tooling-sync lint --root .` exits 0.
  - `git diff -- claude/.claude/skills` shows only the description and note overlays and the six
    sibling rewrites (`vale-setup` lines 11, 12, 67; `vale-fix` 20, 114; `vale-triage` 36). The
    `vale-ci` `rev: v3.22.0` line is unchanged.
  - System `python3 -I` with PyYAML (6.0.3, probed present) parses the frontmatter of all eight
    vendored `SKILL.md` files, and each parsed `description` equals its manifest value (or, with no
    override, its prior value) after whitespace collapse.
  - The main checkout is untouched. Any git command aimed at `~/.dotfiles` is refused inside a
    worktree-isolated session (verification probe), so this check uses file times. At task start,
    `mktemp -d /tmp/infra-sweep-1-t2.XXXXXX` makes the task's scratch directory and `touch
    <scratch>/stamp` writes the stamp, with the printed path written literally in every later
    command. At task end, `find /var/home/glw907/.dotfiles/claude/.claude/skills
    /var/home/glw907/.dotfiles/claude/.claude/tooling -path '*/skills/synced' -prune -o -type f
    -newer <scratch>/stamp -print` prints nothing. The probe confirms this `find` runs from inside a
    worktree, and that it lists files when the stamp is older than them. `skills/synced` is pruned
    because it churns on its own.
  - Trigger checks for `daisyui` (spec "Anthropic practice" item 7: a CLAUDE.md rule depends on
    it). There are five prompts, each in a fresh session run from a subdirectory of the scratch
    directory whose `.claude/skills/daisyui/` holds the copy under test. Each run is one plain
    command, `cd <scratch>/<run> && timeout 180 claude -p --model sonnet --setting-sources project
    --output-format stream-json --verbose "<prompt>" > <scratch>/<run>.jsonl`, with no pipe, no
    heredoc, and no inline script. A separate step reads each file with `grep -c
    '"name":"Skill","input":{"skill":"daisyui"'`. The isolation guard refuses a `claude -p` inside a
    compound command and accepts this form (verification probe). `--setting-sources project` hides
    the live personal skills (probed: the scratch skill loads, `daisyui` does not), and a trigger is
    that `Skill` tool use (probed on a scratch skill). The "before" runs use the directory as
    committed at T2's base; the "after" runs use the overlaid copy.
    - Should trigger: "Build a pricing card with a primary button using DaisyUI classes. Reply with
      the markup only."; "Which DaisyUI component fits a dismissible alert, and which classes does
      it take?"; "Review this markup for DaisyUI 5 mistakes: a div with classes card and bordered
      holding a button with classes btn and btn-primary."
    - Should not trigger: "Write a plain HTML contact form with no CSS framework. Reply with the
      markup only."; "Write a React JSX component that lists users, styled with inline styles
      only."
    - After the overlay, all three should-trigger prompts trigger and neither should-not prompt
      does. One reword of the description is allowed. On a second miss, the subagent returns its
      work uncommitted with the trigger table, and the session applies "Stops" before merging
      either half of the pair. The before and after results, one row per prompt, go in T2's commit
      body, and the session copies them into the PR body.
  - The gate prints `gate exit: 0`.
- **Test.** In `tests/test_claude_tooling_sync.py`, driven by subprocess like the existing tests,
  `apply-overlays --root <fixture>` over a fixture tree with its own manifest: a single-line, a
  quoted, and a block-form description each become a folded block; an override holding `: `, `#`,
  and a leading quote passes `lint`; a note lands after the frontmatter once, and a second run does
  not duplicate it; a sibling span is rewritten, while a `` `fix` `` inside a fenced block, a
  plain-text "fix", and a `` `fix` `` in a skill from a repo with no renamed entry are not; a run
  with `HOME` pointed at an empty fixture home leaves it empty; `lint` fails on a missing
  description, a missing note, and a leftover sibling span, and passes on a clean fixture.
- **Pair.** Runs as a pair with T1.
- **Estimate.** 120 minutes.

### T3. The description-cap and fork-skill checks

- **Outcome.**
  - `claude-tooling-sync` gains a `ratchet-report --root <root>` subcommand (the tool protocol
    above, the three forwarded flags accepted and unread) implementing two ids. It sets
    `sys.dont_write_bytecode` and imports `ratchet` inside that subcommand only, so `apply`,
    `verify`, `lint`, and `apply-overlays` never depend on `ratchet.py`.
  - Scope for both ids: `claude/.claude/skills/*/SKILL.md`, authored and vendored, with
    `skills/synced` excluded. The frontmatter reader is line-based standard library, reading a
    single-line, quoted, or block value. It must read `svelte-check`'s single-line value, which a
    strict YAML parse rejects (a `: ` inside a plain scalar, probed). A `SKILL.md` with no
    `description` is not a violation; an unterminated frontmatter is a configuration error
    (exit 2).
  - `description-cap`: a `SKILL.md` whose `description`, measured in Unicode code points after
    whitespace collapse (block indicator and enclosing quotes excluded), is over 500 and whose
    frontmatter has no `paths:` key; fingerprint `description`.
  - `fork-skill`: a `SKILL.md` whose frontmatter sets `context: fork` and whose body contains a
    phrase from the list "under discussion", "during the session", "delegated", "ask the user", and
    `ask "` (case-insensitive, whitespace-tolerant across line wraps); fingerprint is the phrase as
    listed, and repeated hits add up to its count. `ask "` is the audit's defect class (a fork
    skill quoting a question to put to the user) and, among the fork skills, hits only PS-20's
    `content-review/SKILL.md:46` (probed).
  - Both ids are registered with tool `bin/.local/bin/claude-tooling-sync`, and their live
    violations are seeded.
- **Files.** `bin/.local/bin/claude-tooling-sync`, `tests/test_claude_tooling_sync.py`,
  `claude/.claude/tooling/ratchet-baseline.json`.
- **Risk class.** `runner`.
- **Acceptance.**
  - `description-cap` seeds exactly five entries: `cairn-release` and `visual-fidelity` (`PS-28`,
    `C`); `go-conventions` and `tui-visual-verify` (`GA-06`, `D`); `svelte-check` (`GA-06`, `C`);
    each GA-06 entry with defect "description over 500 characters with no paths: gate". None for
    `vhs-cli-demos` (T2's override), `golang-spf13-cobra` (gated), `dependency-upgrade` (496), or
    `log-project` (486).
  - `fork-skill` seeds exactly four entries, each `pass: C`: `register-check` with `under
    discussion`, `delegated` (`count: 2`), and `during the session`, each `PS-06`; `content-review`
    with `ask "`, `PS-20`. These seeds and the description-cap seeds pass `ratchet.parse` and show
    no growth against T1's baseline (probed).
  - The gate prints `gate exit: 0`.
- **Test.** Fixtures: a 501-code-point ungated description fails; a 500-code-point one and a
  901-character `paths:`-gated one pass; a block-form description is measured after collapse; a
  501-code-point vendored skill is reported and one under `skills/synced` is not; a description
  holding `: ` in a plain scalar is measured; a missing `description` is not reported and an
  unterminated frontmatter exits 2; a fork skill with "under discussion" fails, the same body
  without `context: fork` passes, a fork skill with none of the phrases passes, and a fork skill
  with "Under\n  Discussion" wrapped across lines fails; `ratchet-report` with `--home`,
  `--projects-root`, and `--memory-root` passes, and its output parses as the `emit_report` JSON
  with both ids in `implements`.
- **Estimate.** 100 minutes. Starts after the T1 and T2 pair merges (it edits T2's file and T1's
  baseline).

### Close

Per pass-core "Close" and dotfiles-pass "Close checklist", in order:

1. `git fetch origin` and merge `origin/main` into the branch (a conflict is a stop), so another PR
   that moved the baseline or the registry is caught here. Then the gate on the close head prints
   `gate exit: 0` (the full-suite home).
2. `diff-reviewer` at whole-branch scope reads the branch against this plan, loading
   `python-conventions` (the changed `*.py` and the Python tools). One batched fix chain follows if
   it returns `fix`, each finding quoted verbatim as the fix's acceptance, then the gate again.
3. `claude-tooling-sync verify` passes (it reads the main checkout, so it is a machine-state check,
   not a check of this branch); one `gitleaks git` branch-history scan is clean.
4. `docs/STATUS.md`: the infra sweep section names sweep-2 as next, planned from the baseline this
   pass leaves, with the baseline's entry count by check id (15 expected: `dead-reference` 2,
   `retired-phrase` 2, `relative-link` 2, `description-cap` 5, `fork-skill` 4). Its next action is
   the sweep-2 planning session, an attended session with Geoff, launched after this PR merges
   with the exact line `cd ~/.dotfiles && claude --model opus --effort high --name
   infra-sweep-2-plan "$(cat docs/superpowers/plans/2026-10-11-infra-sweep-2-planning-prompt.txt)"`.
   The prompt file is already committed (planning commits). If the close changed the sweep-2
   scope, it updates that file in the same commit.
5. Push `glw907/workstation`, open the PR (draft until the close is done), and write its body:
   - what landed (task id, commit), the review verdict, and T2's trigger-check table;
   - "What goes live": at Geoff's pull into `~/.dotfiles` after the merge, the global-CLAUDE.md line
     cap in the write hook, the stricter `lint`, and the overlaid vendored skills take effect in
     every session; rollback is `git revert -m 1 <merge>` on `main`, then a pull, with no `stow`
     needed;
   - "Found, not done": dubplate's and aksailingclub-org's CLAUDE.md over 200 lines (other repos);
     `claude-context-budget`, a live hook, is absent from dotfiles-pass's `runner` path map;
     `fetch_skill` reads the tree and files by branch name after resolving the head SHA (a race)
     and writes files and the manifest non-atomically; the vendored pins wait for the next
     `dependency-upgrade` sweep; `svelte-check`'s frontmatter fails a strict YAML parse; plus
     anything the tasks found;
   - the score rows (pass-core "Score"; `cairn-run-gate --records <toplevel> <branch>` for gate and
     lock time).

   Geoff reads and merges. No `stow -R bin` is owed: the pass adds no new script.
- **Estimate.** 70 minutes.
