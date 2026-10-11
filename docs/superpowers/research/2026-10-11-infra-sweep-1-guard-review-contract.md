# Infra sweep 1 plan review: contract and criteria lens (2026-10-11)

Target: `docs/superpowers/plans/2026-10-11-infra-sweep-1-guard.md` (cited as "plan") and
`docs/superpowers/plans/2026-10-11-infra-sweep-1-guard-prompt.txt` (cited as "prompt"), at
`e223c7e`. Every mechanism below was read from source or probed against the tree with `python3 -I`
(scratch scripts under `~/.claude/jobs/c747c352/tmp/`), never recalled.

Counts: 1 blocker, 8 major, 10 minor. One finding is an OWNER FORK (M4).

## Blocker

### B1. relative-link: the four seeded entries collide into two keys, so the gate exits 2

- **Location.** plan:96-100 (T1 acceptance), plan:83-91 (T1 outcome).
- **Defect.** The plan never names the `relative-link` fingerprint, and it asks for "exactly the
  four `bubbletea-conventions.md` links" as four entries. The probe found two distinct targets,
  each cited twice: `research/2026-04-26-bubbletea-norms.md` at lines 11 and 632, and
  `research/2026-04-26-reference-apps.md` at lines 13 and 636. With the natural fingerprint (the
  target), four entries share two keys. `ratchet.parse` rejects a repeated key ("duplicates an
  earlier entry", `ratchet.py:177-179`) as a ConfigError, so the gate exits 2. A line-number
  fingerprint would avoid the collision, but then any edit above the link would break the
  baseline.
- **Fold.** In T1's outcome, set the fingerprint to the link target as written, anchor stripped.
  In T1's acceptance, ask for two entries, each with `count: 2`, `finding: DC-10`, and `pass: D`.
  Add a test fixture where the same dead link appears twice in one file and the run matches one
  entry carrying `count: 2`.

## Major

### M1. fork-skill: register-check's seeds need a count, and the content-review branch is already resolved

- **Location.** plan:168-174 (T3 acceptance), plan:161-164.
- **Defect.** With "fingerprint is the phrase", `register-check/SKILL.md` reports "delegated"
  twice (lines 11 and 62), so its entry needs `count: 2`. Without the count, `match` fails it
  with "count rose above the baseline" (`ratchet.py:318-319`). Its other hits are "under
  discussion" (line 10) and "during the session" (line 74). The acceptance names neither the
  fingerprints nor the counts. Its conditional ("If the phrase list misses PS-20's line") is
  already settled by a probe: none of the four phrases appears in `content-review/SKILL.md`. Only
  `Ask "apply all, apply some (specify), or skip?"` at line 46 carries the defect, so the
  executor would face an open choice that the planner can close now.
- **Fold.** Name the fifth phrase in the plan. The recommendation is `ask "`, whitespace-tolerant
  and case-insensitive. The probe shows it hits only `content-review:46` across both fork skills,
  and a fork skill quoting a question to put to the user is the audit's defect class. List the
  exact seeds:
  - `register-check`: `under discussion` (1), `delegated` (`count: 2`), and `during the session`
    (1), each `PS-06`, `C`.
  - `content-review`: `ask "` (1), `PS-20`, `C`.

  Drop the conditional sentence.

### M2. The GA-03 rule opens a deletion hole: a bin deleted in the worktree still resolves through home

- **Location.** plan:83-86 (T1 outcome), plan:103-105 (T1 test).
- **Defect.** Under the new rule, a span is rewritten under the tree only when the bin is tracked
  or present there. Any other span resolves against `--home`. Every stowed bin in
  `~/.local/bin` is a symlink into the main checkout (probed:
  `awake -> ../../.dotfiles/bin/.local/bin/awake`). Suppose a worktree deletes
  `bin/.local/bin/foo` while a doc still cites `~/.local/bin/foo`. The span falls through to home,
  which still resolves through the main checkout, so the check passes. Today's rule catches this
  case. The module docstring states that intent ("a worktree that adds or deletes a doc is judged
  on its own tree", `check-claude-refs.py:17-18`), and `test_f1` guards it for docs. The outcome
  also leaves "git ls-files, or the file's presence" open. Under `git ls-files` alone, the
  existing `test_f2` breaks, because `Fixture.write_bin` writes an untracked file
  (`tests/test_check_claude_refs.py:106-110`).
- **Fold.** Decide stowedness from home's entry. When `<home>/.local/bin/<x>` is a symlink whose
  resolved target sits under a `bin/.local/bin/` directory, or when `<root>/bin/.local/bin/<x>`
  exists, judge the span against the tree. Otherwise judge it against home. Drop the
  `git ls-files` alternative. Add a fixture with a stow-style symlink in the fixture home, pointing
  at a bin path that the fixture tree does not contain. That span must report a violation.

### M3. The end-to-end check cannot be observed: `ratchet.py check` prints nothing on success

- **Location.** plan:25-28.
- **Defect.** On a clean run, `report` returns 0 without printing anything (`ratchet.py:331-332`).
  A probe of `ratchet.py check --root .` gave `rc=0` and no output. "Lists the registry ids" is
  therefore not something the run can show.
- **Fold.** State the check as two parts. First, `python3 claude/.claude/tooling/ratchet.py check
  --root .` exits 0. Second, the registry keys read from `ratchet-baseline.json` (a one-line
  `python3 -c` over `["checks"]`) are exactly the five ids. A `jq` filter over `.entries` shows no
  `GA-03` entry and no entry whose `file` contains `vhs-cli-demos`.

### M4. OWNER FORK: the 200-line cap reaches every repo's CLAUDE.md through the write hook

- **Location.** plan:89-91 (T1 outcome), plan:20-23 (out of scope: "any other repo").
- **Defect.** `claude-context-budget` budgets by basename: `budget_for` matches any file named
  `CLAUDE.md` (`claude-context-budget:28`). It also runs as a PostToolUse hook on every write
  (`settings.json:105`), and exit 2 there is blocking feedback. Measured today:
  `~/Projects/dubplate/CLAUDE.md` has 356 lines and `aksailingclub-org/CLAUDE.md` has 262. With
  the cap as written, every edit to those files in their own sessions is blocked. That reaches
  other repos, which the plan's scope excludes. The cross-repo cap was sent to Someday under R2.
- **Options.**
  - (a) The cap applies only to the global file: a path ending in `claude/.claude/CLAUDE.md`, or
    `~/.claude/CLAUDE.md` after realpath. It applies in both hook and file modes.
  - (b) The cap applies to every CLAUDE.md, accepting that dubplate and aksailingclub-org writes
    block until those files are trimmed.
  - (c) The cap runs in file mode only (`check.sh`), never in the hook.
- **Recommendation.** (a). It matches the stated scope and R2, it catches growth of the global
  file at the line that crosses the cap, and it touches no other repo. Add a fixture: a 201-line
  `CLAUDE.md` outside the global path exits 0.

### M5. T2's live refetch is a dependency bump outside `dependency-upgrade`, and its failure path leaves the gate red

- **Location.** plan:124 ("Then `update-skills` refetches every vendored skill"), plan:140-144,
  plan:151-152, plan:17-18.
- **Defect.** The refetch causes three problems.
  - `fetch_skill` takes the branch head, not the pinned commit
    (`claude-tooling-sync:199-213`). That is a dependency bump, and the global CLAUDE.md routes
    every bump through the `dependency-upgrade` skill.
  - The failure path is unspecified. If `gh api` fails, the plan stops the refetch "not the pair".
    T2's commit would still add `description` and `note` to the manifest, while the installed
    files lack them. The new `lint` then fails in the gate after the merge. T3's "none for
    `vhs-cli-demos`" also fails, because the 915-character upstream description is still
    installed.
  - "Upstream changes since the pinned commit" names no command that could verify it.

  A probe of the compare API shows the refetch buys nothing today:
  - `vale-cli/agent-tools`: 0 commits ahead.
  - `saadeghi/daisyui`: 30 commits ahead, none touching `skills/`.
  - `gfargo/skills`: 5 commits ahead, none touching the vhs skill.
  - `samber/cc-skills-golang`: 1 commit ahead, none touching the cobra skill.

  The installed `vale-setup` matches the pinned upstream except for its `name:` line.
- **Fold.** Add an offline mode that applies the overlays and sibling rewrites to the installed
  copies, for example `update-skills --overlay-only` or an `apply-overlays` subcommand. T2 runs it
  instead of a refetch. `fetch_skill` still calls the same overlay function on future refetches.
  The diff acceptance then becomes exact: only the overlays and the sibling rewrites appear. The
  refetch sentence and the `gh api` pair clause are deleted. `live-account` stays for the push and
  the PR only (plan:17-18).

### M6. T2 trims two descriptions without the spec's trigger checks

- **Location.** plan:125-130 (CS-8, CS-17). The rule is in the spec's "Lean re-plan" under
  "Method calls" (`specs/2026-09-28-claude-infra-sweep-design.md:736-739`).
- **Defect.** The spec says each trimmed description gets trigger checks: three should-trigger
  and two should-not prompts, in fresh `claude -p` sessions, before and after the trim. T2
  replaces the `daisyui` and `vhs-cli-demos` descriptions, and nothing in T2's acceptance runs the
  checks or names their prompts.
- **Fold.** Add the checks to T2's acceptance. Name the five prompts per skill in the plan. For
  `daisyui`, the should-not prompts are the ones the narrowing targets, such as plain HTML with no
  DaisyUI and a JSX component with no DaisyUI. Record the before and after results in the commit
  body, and add about 20 minutes to T2. Alternatively, amend the spec line to exempt vendored
  overrides, with the reason. Do not leave the plan silent on it.

### M7. The overlay's written description form is unspecified, and a plain scalar can break the frontmatter

- **Location.** plan:115-117, plan:122-123 (T2 outcome and lint), plan:145-150 (T2 test).
- **Defect.** The plan says how a description is read (single-line or block) but not how the
  overlay writes it. The `vhs-cli-demos` override is free text under 300 characters. Written as a
  plain YAML scalar, a `: ` or ` #` in it makes the frontmatter invalid or truncates it, and
  Claude Code may then drop the skill. No fixture covers this, and nothing in the gate parses the
  result. The lint's "lacks its manifest description" names no comparison rule: exact bytes,
  whitespace-collapsed text, or the block-scalar form.
- **Fold.** The overlay always writes `description: >-` with indented, wrapped lines. The lint
  compares the whitespace-collapsed installed value with the whitespace-collapsed manifest value.
  For the note, it compares the text between the markers, stripped. Add a fixture whose override
  contains `: ` and `#`, and assert that the tool's own frontmatter reader, the one T3's
  description-cap uses, reads the value back intact.

### M8. The pair subagents never receive the plan's conventions

- **Location.** prompt:14-16 ("each given its task's full text from the plan").
- **Defect.** T1's acceptance depends on the "Conventions every task follows" section:
  - the entry fields and the pass-label rule;
  - the `GA-nn` rule and its `defect`;
  - registering an id and seeding its entries in one commit;
  - the commit subject;
  - the tool protocol.

  The prompt hands each subagent only its task block, and subagents start with zero context. The
  prompt also names no `subagent_type`.
- **Fold.** Change the prompt to "its task's full text plus the plan's 'Conventions every task
  follows' section, verbatim". Name the agent type, `general-purpose`, since dotfiles has no
  implementer agent.

## Minor

### m1. T1's 199-line acceptance is vacuous

- **Location.** plan:101.
- **Defect.** `claude-context-budget claude/.claude/CLAUDE.md` exits 0 at 199 lines with or
  without the cap.
- **Fold.** Cite the 200-line and 201-line fixtures as the cap's proof, and keep the global-file
  run only as a gate leg.

### m2. Two relative-link exclusions have no fixture

- **Location.** plan:105-106.
- **Defect.** The `#anchor`-only link is skipped before anchor stripping happens, so no fixture
  proves stripping. An implementation that resolves `foo.md#bar` literally would pass every named
  fixture. No fixture shows that a `/`-leading or `~`-leading link is excluded.
- **Fold.** Add a fixture for a live link with an anchor (`exists.md#section`, which passes) and
  one for an absolute link (`[x](/nonexistent/a.md)`, which is not reported).

### m3. T2's "code-fence line" fixture never exercises fence handling

- **Location.** plan:148-149.
- **Defect.** `git switch -c vale-fix-...` holds no single-backtick span exactly equal to `fix`,
  so it passes whether or not fenced code is skipped. No fixture shows that a skill from a repo
  without a renamed entry (`daisyui` carrying `` `fix` ``) is left alone.
- **Fold.** Decide fence behavior. The recommendation is to rewrite outside fenced blocks only,
  and to make the lint agree. Add a fenced block containing `` `fix` `` and a non-vale fixture
  skill carrying `` `fix` ``.

### m4. T3's fixtures miss the scope and malformed states

- **Location.** plan:157-164, plan:175-179.
- **Defect.** No fixture shows that description-cap reaches a vendored skill. A reuse of
  `scan_files(include_vendored=False)` would pass every named fixture, and after T2 the live tree
  has no over-cap vendored skill to reveal it. No fixture covers `skills/synced` exclusion, a
  phrase wrapped across a line, or a case variant. No report is named for a SKILL.md with no
  frontmatter, an unterminated frontmatter, or no `description`. fork-skill's scope (authored
  only, or authored and vendored) is not stated.
- **Fold.** Add fixtures for a 501-character vendored skill (reported), a `skills/synced` skill
  (not reported), and a wrapped, mixed-case phrase (reported). Name the reports: a missing
  `description` is not a description-cap violation, and an unterminated frontmatter is a
  ConfigError (exit 2). Give fork-skill the same scope as description-cap.

### m5. "Characters" is unpinned, and one skill sits 4 under the cap

- **Location.** plan:160.
- **Defect.** `dependency-upgrade` measures 496 and `log-project` 486. `log-project`'s
  description holds an em dash, so a byte count would differ from a character count. An
  implementation that keeps the `>` indicator, or measures bytes, can drift toward the cap.
- **Fold.** State "Unicode code points after whitespace collapse, block indicator and quotes
  excluded". Add to the acceptance that `dependency-upgrade` (496) is not reported.

### m6. The `link-ok` marker's written form is unnamed

- **Location.** plan:88-89, plan:100.
- **Defect.** The marker goes into an agent definition body (`cairn-docs-drafter.md:126`), which
  is model-facing prompt text. Neither `retired-ok` nor `link-ok` has an in-tree usage to copy
  (probe: zero hits).
- **Fold.** Name `<!-- link-ok -->` at the end of the line.

### m7. Pass labels are vestigial under R1

- **Location.** plan:61-65, plan:168-170, plan:192-193.
- **Defect.** Sweep-2 removes every entry, so the C and D labels decide nothing. GA-06 and GA-07
  are one defect split only by label. Close step 4's "count by pass label" reports a dead
  dimension.
- **Fold.** Cheapest: keep the labels as written, but report the close count by check id. A
  label migration is not worth the commit.

### m8. T1's budget test location is open

- **Location.** plan:107-109.
- **Defect.** The location reads "inside the test file or a new `tests/claude-context-budget.test.sh`",
  and T1's Files list omits the new file.
- **Fold.** Pick `tests/claude-context-budget.test.sh`, following the `claude-clock-stop.test.sh`
  pattern, with a `run` line in `check.sh`, and list it under Files.

### m9. `update_skills` reflows the whole manifest

- **Location.** plan:140-144.
- **Defect.** `json.dump(indent=2)` (`claude-tooling-sync:234-236`) reflows the five one-line
  vale entries. T2's diff acceptance covers the skills only, so the manifest churn goes unnamed.
  This is moot if the M5 fold writes the manifest by hand.
- **Fold.** Expect a reflowed manifest in the diff, or keep the manifest edit manual.

### m10. The GA-03 proof depends on home state the plan does not name

- **Location.** plan:96-97.
- **Defect.** "No violation for `~/.local/bin/poplar`" holds only while the real
  `~/.local/bin/poplar` exists. It does today (probed). GA-05's `~/.local/bin/scoped-test` stays a
  violation, because home lacks it (probed), so its entry correctly survives.
- **Fold.** State both in the acceptance: the poplar binary exists in home, and GA-05 stays.

## Checked and found sound

- **Description-cap seeds.** Once T2 shortens `vhs-cli-demos`, the probe matches T3's acceptance
  exactly: `cairn-release` 849, `visual-fidelity` 672, `svelte-check` 599, `tui-visual-verify`
  534, and `go-conventions` 530. `golang-spf13-cobra` (720) carries `paths:` upstream at the pinned
  commit, so no refetch strips it.
- **Fork skills.** The tree holds exactly two (`content-review`, `register-check`).
- **Relative-link scope.** The probe found five dead links, the same five in both scopes: the four
  bubbletea links and `cairn-docs-drafter.md:126`.
- **New dead-reference violations.** The GA-03 change creates none on today's tree. The untracked
  spans are `~/.local/bin/` and `poplar`, both present in home, and `scoped-test`, already
  baselined as GA-05.
- **vhs.** The CS-17 note's claim holds: `bluefin/Brewfile` has no `vhs`, and `vhs` is not on
  `PATH`.
- **Risk class and flag.** `runner` fits every file touched. `live-account` fits the push and the
  PR.
- **Pairing.** T1 and T2 touch disjoint files, generated outputs included. T3 correctly
  sequences after both.
- **Clock.** Every task and the close carry a clock estimate. No single-deliverable task needs
  folding.
