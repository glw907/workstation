# Infra sweep 1 plan review: fold verification (2026-10-11)

Target: the plan `docs/plans/2026-10-11-infra-sweep-1-guard.md` ("plan") and its
prompt ("prompt") at `236f9d7`, read against the three lens reviews and the fold record
`2026-10-11-infra-sweep-1-guard-plan-fold.md`. The reader took no part in the review or the fold.
Probes ran from `~/.claude/jobs/c747c352/tmp/verify/` with `python3 -I` (system Python, PyYAML
6.0.3), never inside the repo:

- `patch_ga03.py`: copies `check-claude-refs.py`, its test file, and `ratchet.py` to scratch and
  patches in the plan's GA-03 rule. It then adds six probe tests: a stow symlink whose target
  exists, a dangling stow symlink, a folded `~/.local/bin` directory link, a regular home file, a
  span absent from both, and an audited run with a stow symlink.
- `seeds_verify.py`: runs the T1 and T3 seeds through `ratchet.parse`, `growth`, and `match`, and
  scans every `SKILL.md` for the fork-skill phrases.
- `desc_verify.py`: measures each description with a line-based reader, checks for a `paths:`
  gate, and runs a strict PyYAML parse.
- `yaml_verify.py`: runs the folded `description: >-` overlay over 13 hostile strings.
- `rl_verify.py`: finds dead relative links in the `dead-reference` scan set, with and without
  fence awareness.
- One `claude -p --model haiku --setting-sources project --output-format stream-json --verbose`
  run from a scratch directory holding one probe skill. It cost $0.0017.

Counts: 0 blockers, 1 major, 4 minor. Owner forks: none.

## Answers to the four questions

1. **Every blocker and major closed, or was refused with a reason.** One fold landing is not
   runnable: mechanics B1's `git -C ~/.dotfiles status` acceptance, finding V-M1 below. The
   locations, by lens:
   - Contract:
     - B1: plan:115-120, 138-142, 152-153.
     - M1: plan:262-267, 279-282.
     - M2: plan:108-114, 146-151.
     - M3: plan:28-34.
     - M4: plan:121-128, 156-158.
     - M5: plan:177-182.
     - M6: plan:215-233.
     - M7: plan:167-170, 183-186, 211-213, 235-238.
     - M8: prompt:16-22.
   - Mechanics:
     - B1: plan:177-182, 205-206, 214.
     - M1: plan:209-210.
     - M2: plan:16-19, 180-182.
     - M3 to M7: at their contract roots.
   - Risk:
     - B1: plan:70-72, 177-182.
     - M1: plan:121-128.
     - M2: plan:180-182. The `fetch_skill` race went to "Found, not done" at plan:319-320, with
       a reason.
     - M3: refused with a reason (fold row). The plan runs no refetch, so the partial-write path
       never runs here. The defect is listed at plan:319-320.
     - M4: plan:115-120.
     - M5: plan:108-114.

   The refusals of contract m9, mechanics m7, mechanics m10, and part of contract M7 are
   reasoned. For mechanics m10, the fold's premise holds: at `cairn-docs-drafter.md:126` the only
   code span is `` `CLAUDE.md` ``, and the link sits outside it.
2. **The fold introduced no contradiction, no order that cannot build, and no implementation
   code.** T1 and T2 stay disjoint: `check.sh` already runs all of `tests/` through pytest, so T2
   needs no `check.sh` line. T3 follows both. The clock sums hold (130 + 120 + 100 + 70 = 420; the
   path is 300). The 15-entry close count matches the probe. One ambiguity was introduced, at the
   trigger check's stop (V-m1).
3. **Every new mechanism has a source or a probe, and every load-bearing one re-probed true:**
   - **Relative-link seeds.** Two entries with `count: 2` parse and show no growth against HEAD.
     Four observed hits match the two entries (`match` returns `[]`). Four separate entries
     raise "duplicates an earlier entry".
   - **Dead relative links.** The live set is exactly five, none of them inside a fence. Four are
     the `bubbletea-conventions.md` links at lines 11, 13, 632, and 636, and the fifth is at
     `cairn-docs-drafter.md:126`. The plan's open fence behavior therefore changes nothing on the
     live tree.
   - **The GA-03 rule.** The 12 existing tests stay green. A stow symlink is a violation, both
     with its target present and dangling, and so is a folded `~/.local/bin` directory link. A
     regular home file passes, and a span absent from both is a violation. The audited run reads
     nothing outside the fixture.
   - **GA-03 on the live tree.** The rule leaves `dead-reference` with exactly GA-04 and GA-05:
     `poplar` passes and `scoped-test` stays a violation. No `~/.local/bin` link points into
     another repo's `bin/.local/bin`.
   - **Fork skills.** The tree holds exactly two, `content-review` and `register-check`.
     `ask "` (case-insensitive, `ask\s+"`) hits only `content-review` once. `register-check`
     hits `under discussion` 1, `delegated` 2, and `during the session` 1, and `ask the user`
     hits nothing. The T3 seeds parse, show no growth against the T1 baseline, and total 15
     entries (`dead-reference` 2, `retired-phrase` 2, `relative-link` 2, `description-cap` 5,
     `fork-skill` 4).
   - **Description lengths.** The over-cap skills are `cairn-release` 849, `visual-fidelity`
     672, `svelte-check` 599, `tui-visual-verify` 534, and `go-conventions` 530. `vhs-cli-demos`
     measures 915 and `golang-spf13-cobra` 720 (gated by `paths:`). `dependency-upgrade` (496)
     and `log-project` (486) sit under the cap. All eight vendored frontmatters parse under
     PyYAML today, and `svelte-check` raises `ScannerError`.
   - **The folded `>-` overlay.** All 13 hostile strings round-trip after whitespace collapse:
     `: `, `#`, both leading quotes, a leading `- `, YAML indicators, an over-width word, tabs,
     an em dash, and a leading `---`. The plain-scalar form fails on three of the cases. Claude
     Code also loads a `>-` description holding `: ` and `#`: the probe skill, written that way,
     loaded and triggered.
   - **`claude -p --setting-sources project`.** The init event's `skills` list held the scratch
     project skill and Claude Code's built-ins, with no `daisyui` and no MCP servers. The stream
     carried `{"name": "Skill", "input": {"skill": "zz-verify-probe"}}`.
   - **The line cap's path suffix.** `readlink -f ~/.claude/CLAUDE.md` resolves to
     `.../.dotfiles/claude/.claude/CLAUDE.md`, 199 lines. `check()` already applies `realpath -m`
     (`claude-context-budget:56`).
   - **The cited sources.** The forwarded flags (`ratchet.py:264`, `:377-388`) match the plan's
     citation. `claude-md-archive.md`, `claude-clock-stop.test.sh`, and a `Brewfile` without
     `vhs` all exist.
   - **The end-to-end check.** It is observable. The one-liner prints, and
     `ratchet.py check` exits 0 silently.
   - **The launch checks.** Every check prints what its comment names, except plan:54, which
     fails today (V-m2).
4. **Owner forks.** None are presented, and none are needed. Spec item 7 (spec:661-664) limits
   trigger checks to a trimmed skill that a CLAUDE.md rule depends on, and the lean re-plan's
   "Method calls" cite item 7. The global-only cap follows R2, and dropping the refetch follows
   the `dependency-upgrade` rule.

## Findings

### V-M1 (major). T2's main-checkout cleanliness check cannot run inside a worktree-isolated subagent

- **Location.** plan:214 (T2 acceptance). The fold's provenance is mechanics B1, at fold:41-42.
- **Defect.** T2 runs as an Agent subagent with `isolation: "worktree"` (prompt:16-17). Its
  acceptance requires `git -C ~/.dotfiles status --porcelain` to print nothing before and after
  the task. In a worktree-isolated session, the harness refuses any git command aimed at the
  shared checkout. The executor then either fails an acceptance line two times running and
  returns a spurious failure, or skips the line silently. The line is the only check of the
  "writes nothing outside TREE" guarantee.
- **Evidence.** From this worktree-isolated reader, `git -C /var/home/glw907/.dotfiles ...` was
  refused: "this command redirects git to the shared checkout via -C. Refusing to run it". The
  form `cd /var/home/glw907/.dotfiles && git status --porcelain` was refused as well: "changes
  directory to the shared checkout ... before running git". A non-git
  `find /var/home/glw907/.dotfiles ... -newer <file> -print` ran. It listed churn under
  `claude/.claude/skills/synced/`, so any file-time check must prune that directory.
- **Proposed fix.** Replace the line with a non-git check scoped to the paths T2 could reach.
  - At task start, write a stamp file in the T2 worktree's git dir.
  - At task end, `find ~/.dotfiles/claude/.claude/skills ~/.dotfiles/claude/.claude/tooling -path
    '*/skills/synced' -prune -o -type f -newer <stamp> -print` must print nothing.
  - Alternatively, move the `git -C ~/.dotfiles status --porcelain` check to a step that runs
    outside isolation: Geoff's launch block already runs it before launch, and the PR body can
    carry it as a post-merge line.

  The fixture test "a run with `HOME` pointed at an empty fixture home leaves it empty"
  (plan:241) stays as the code-level proof.

### V-m1 (minor). The trigger check's stop path is ambiguous for a pair subagent

- **Location.** plan:230-233 ("One reword ... a second miss is a stop"); prompt:19-21.
- **Defect.** The prompt reserves Stops to the session. It tells the subagent what to do only
  when its gate stays red after two attempts: return the failure uncommitted. A second
  trigger-check miss is not a gate failure. The subagent can therefore commit and report, return
  uncommitted, or try to stop the pass itself. The session's next move is also open, including
  whether T1 merges alone.
- **Evidence.** The prompt's carve-out is gate-only at prompt:19-21. The plan's "Stops" names
  only a red, a merge conflict, and a clock stop (plan:97-100).
- **Proposed fix.** Add one sentence to T2: on a second miss, the subagent returns its work
  uncommitted with the trigger table, and the session applies "Stops" before merging either half
  of the pair.

### V-m2 (minor). Launch check plan:54 fails until the plan branch is pushed, and no step names the push

- **Location.** plan:54 (`git rev-parse worktree-infra-sweep-plan
  origin/worktree-infra-sweep-plan`).
- **Defect.** The check requires the two refs to be equal, and today they differ. No step in the
  plan or the prompt says who pushes the branch, or that this verification file and any fold of it
  are committed first. Plan:53 also requires the plan worktree to be clean.
- **Evidence.** `worktree-infra-sweep-plan` is at `236f9d7`, and
  `origin/worktree-infra-sweep-plan` is at `e223c7e`.
- **Proposed fix.** Add a planning-close line before the launch block: commit the verification
  record and any fold, then `git push origin worktree-infra-sweep-plan`.

### V-m3 (minor). The nested `claude -p` runs may trip the isolation guard if written as compound commands

- **Location.** plan:215-222 (T2 trigger checks).
- **Defect.** The T2 subagent runs the ten or more `claude -p` sessions from a worktree-isolated
  Bash. In this reader's isolated session, the guard refused `claude -p` inside a compound
  command (a pipeline with an inline `python3 -c`, and a `printf` heredoc build). It accepted the
  plain form.
- **Evidence.** Refused: `cd <scratch> && timeout 180 claude -p ... > out.jsonl 2> err.txt; ...
  | python3 -c '...'`. The refusal read "runs claude with the text ... inside a construct too
  complex to verify". Accepted: `cd <scratch> && timeout 180 claude -p --model haiku
  --setting-sources project --output-format stream-json --verbose "<prompt>" > out.jsonl`,
  followed by a separate `python3 -I <script> out.jsonl`.
- **Proposed fix.** In T2, name the accepted shape: one `claude -p` per command, with output
  redirected to a file in the scratch directory, and the `"name":"Skill"` match read by a separate
  `python3 -I` script or `grep -c`. Name the scratch directory too (`mktemp -d` under `/tmp`).

### V-m4 (minor). Pair subagents have no route for the "Scope" rule

- **Location.** plan:101 ("A defect found outside a task goes to the PR body's 'Found, not done'
  list"); prompt:16-22.
- **Defect.** The subagents receive the Conventions verbatim, but they never write the PR body.
  A defect a subagent finds outside its task, such as a T2 note on `fetch_skill`'s signature
  needing the whole manifest for sibling names, has no stated return path.
- **Proposed fix.** Add one clause to the prompt's list of three things: the subagent's final
  report lists any found-not-done defect, and the session carries it to the PR body.

## Checked and sound

- The settled items are not owner forks.
  - The no-refetch call matches the global `dependency-upgrade` rule and the plan's out-of-scope
    line.
  - The global-only cap matches R2.
  - The daisyui-only trigger check matches spec item 7, which the lean re-plan's "Method calls"
    cites.
- The clock-file handling for the pair matches pass-core "Clock stop". `claude-clock-stop`
  resolves the git dir from the hook's `cwd`, so pair worktrees with no clock file cannot fire.
- `retired-phrase` scans vendored skills. The planned notes and the daisyui description hold no
  phrase from `retired-phrases.txt`, so T2 adds no `retired-phrase` violation.
- The `runner` class holds: `scripts/**`, `tests/**`, `claude/.claude/tooling/**`,
  `claude/.claude/skills/**`, and `claude-tooling-sync` are all in the dotfiles-pass path map,
  and `claude-context-budget` is not, as "Found, not done" says.
