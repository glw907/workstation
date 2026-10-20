# Infra sweep 2 plan: mechanics review (2026-10-11)

The `plan-reviewer` agent (Opus, effort `medium`) reviewed
`docs/superpowers/plans/2026-10-11-infra-sweep-2.md` at `cd0b5e4`. The dispatching session saved its
reply verbatim below.

---

**Mechanics and feasibility review of the infra sweep 2 plan** (`docs/superpowers/plans/2026-10-11-infra-sweep-2.md` at `cd0b5e4`)

I found no blocker. I found 8 major and 11 minor or optional gaps. Most are in G's cutover and fixtures and in F's dry run. Two things hold up as written:

- **Pair disjointness and baseline merges hold.** I ran a scratch git merge of A's edit (old lines 14-16 and 40-47 deleted) against I's (26-32, and the 27-33 variant). Both merge cleanly and leave 10 entries. In waves 2 to 4 only one side touches `ratchet-baseline.json` (B, then D, then neither), so those merges cannot conflict. B must also drop the trailing comma on the GA-05 entry, which becomes the last remaining entry. That is legal, since D runs one wave later. Wave 4 is disjoint only while E leaves `.claude/skills/dotfiles-pass/SKILL.md` alone (see finding 4).
- **Mechanisms that check out:**
  - `systemd-run`: everything after the command passes through to it (man page, "All command line arguments after the first non-option argument…"), and with `--wait` it returns the service's exit code ("EXIT STATUS").
  - `Type=oneshot` has no start timeout by default (`man systemd.service`).
  - `claude agents --json`, `--bg`, `--name`, `--effort`, `-w` and `--max-budget-usd` all exist (`claude --help`).
  - `worktree.baseRef: "head"` is set in the tracked settings.
  - Stow does not link `.stow-local-ignore` itself (probed with stow 2.4.1).
  - `cp --remove-destination "$(readlink -f link)" link` turns a relative link into a real file and leaves the target untouched (probed).
  - Sweep 1's trigger method (`--setting-sources project`) is reused as its plan records.

## Major

1. **[major, correctness] G's cutover order collides with the automatic pull after a merge** (`plan:539-545`; `pass-core/SKILL.md:155-160`). Whoever merges, Geoff or the conductor, runs `git pull --ff-only` right away.
   - If the checkout is clean, the pull succeeds while `~/.claude/settings.json` is still a link. The link now shows the new tracked file with no `model`, `effortLevel` or `modelSettings`, so the cp step that should keep them never gets the chance.
   - If a `/effort` change made during the pass left `claude/.claude/settings.json` dirty, git refuses the pull: the merge changes that file.
   - **Fold:** run the cp step before the merge (it is harmless then). Follow it with `git -C ~/.dotfiles checkout -- claude/.claude/settings.json`. Put both in STATUS's next action and as the first line of the PR body, so the merger runs them before pulling. `apply` follows the pull.

2. **[major, correctness] G's manual fixture run is underspecified, unsafe, and partly vacuous** (`plan:499-504`, E2E 6 at `plan:54-55`).
   - `apply` reads the tracked file from `<home>/.dotfiles/claude/.claude/settings.json` (`claude-tooling-sync:77`), not from the worktree. It also runs the real `claude mcp add-json -s user` for every manifest server missing from `<home>/.claude.json` (`:118-122`). In a bare scratch home that writes the real `~/.claude.json`, or crashes under `check=True` when the server already exists.
   - The `git diff --quiet` check cannot fail, because `apply` never writes the worktree's file.
   - The existing `test_verify_passes_with_no_collision` fixture has no live `<home>/.claude/settings.json`, so the new "missing live file is drift" rule will break it.
   - **Fold:** drop the manual run. Add the old-tracked-copy case to the pytest list on `fixture_home`, which has an empty servers manifest and the stub `claude` (`tests/test_claude_tooling_sync.py:107-124`). Have `fixture_home` write a live settings file. Replace E2E 6 with that test.

3. **[major, correctness] G's stow check folds `.claude` whole in an empty scratch home** (`plan:497-498`). I probed this: with no `.claude` directory in the target, stow prints a single `LINK: .claude => …`. The settings file is still reachable through that folded link, and "still lists every other `claude/.claude` entry" fails.
   - **Fold:** the scratch home holds a real `.claude/` directory, which is the live layout (`bootstrap.sh:42,317` creates it before stowing). Name the pattern as `^/\.claude/settings\.json$`.

4. **[major, correctness] After G, a merged change to `settings.json` no longer goes live on pull.** The live file is generated, so new hooks or permissions, including the secret-guard wiring, need `apply`. Nothing in the plan tells future passes this.
   - **Fold:** G adds one line to dotfiles-pass "Close checklist" (`.claude/skills/dotfiles-pass/SKILL.md:42-46`): a merge that touches `claude/.claude/settings.json` is followed by `claude-tooling-sync apply`. Move that file from E's conditional list to G. E's grep pattern currently matches only `pass-core:60`, so E would not edit it anyway.

5. **[major, correctness] F's dry run cannot finish inside a foreground Bash call** (`plan:424-425`). The Bash tool caps a call at 600 s. The run has no state file, so it re-fetches every page. The first call audits the whole of `~/.claude` (36 skills and 15 agents) plus the repo's `.claude/`.
   - `plan:397-398` calls the no-path form "the form probed unattended". The facts probe actually passed one path (`facts:213-217`, 8 turns, $0.78), so the whole-tree cost and duration are unmeasured.
   - **Fold:** run `systemd-run` with `run_in_background: true` and wait for its exit, then read the hand-over. Correct the probe claim. Give the first call `--model opus --effort medium`; CLAUDE.md asks every dispatch to name both.

6. **[major, correctness] F's "nothing was pushed" check can never fail** (`plan:426-427`). The worktrees doc says `--worktree` creates "a new branch named `worktree-<name>`", so the branch is `worktree-model-review-<YYYY-MM>` and `refs/heads/model-review-*` never matches.
   - The same doc says a `-p` run's worktree keeps its lock: "Claude doesn't clean up their worktrees … leaves the lock". Removing it at `plan:428-429` therefore needs `git worktree unlock` first.
   - **Fold:** use the pattern `'refs/heads/worktree-model-review-*'` and add the unlock step.

7. **[major, correctness] F's worktree base and state file go stale.** With `baseRef: "head"`, each monthly `-w` branches from the local checkout's `HEAD`.
   - The quiet-month self-merge's pull of `~/.dotfiles` (pass-core "Ledgers") comes from inside the `-w` session. The worktree isolation checks refuse that ("blocks a Bash … command that redirects git into the main checkout … `git -C`"). Unless some other pass pulls in between, next month's worktree has no `state.json`, so every run takes the full re-fetch path and reviews a stale tree.
   - In the dry run, `-w` branches from the pair worktree's `HEAD`. F's files are still uncommitted at that point, because the outcome goes in the commit body.
   - **Fold:** the launcher runs `git -C "$repo" pull --ff-only` before the two calls (it is not under the guard). It passes the prompt text as `"$(cat "$repo/docs/model-review/prompt.txt")"`, not as a path. F commits before the dry run and records the outcome by amending.

8. **[major, correctness] B's PS-06 wording trips the fork-skill check** (`plan:270-272`). `claude-tooling-sync:494-498` counts each phrase as a lowercase substring of the body, and "delegated" is one of the phrases. The plan has the new text take "whether application is delegated" as an argument. Written that way, the gate reports "lower this baseline entry's count to 1" instead of clearing the entry.
   - **Fold:** state that the rewritten `register-check` and `content-review` bodies contain none of `under discussion`, `during the session`, `delegated`, `ask the user` or `ask "`. Name the argument something like "apply: yes/no".

## Minor

9. **[minor, optional] Over-ceremony in the trigger checks** (`plan:106-118`). There are 50 `claude -p` runs: 25 "before" and 25 "after". The design asks only that "each trimmed description passes its trigger prompts" (`design:97-98`). At up to 180 s each, A's 20 serial runs can cost 60 minutes on the critical path.
   - **Fold:** run each set as parallel background commands, and keep "before" runs only for should-trigger prompts.

10. **[minor, correctness] E1 drops the executor's launch** (`plan:440-443`). The design says pre-approval covers the executor's launch too (`design:42-43`, "and the executor's launch unattended"); the plan stops at "write the executor's launch prompt".
    - **Fold:** "…writes the launch prompt and launches the executor."

11. **[minor, correctness] G's preference-key list is narrow** (`plan:481-483`). The tracked file also holds keys Claude Code's own commands write: `outputStyle`, `voiceEnabled`, `tui` and `autoMemoryEnabled`. After the cutover, toggling one makes `verify` report drift, and the next `apply` silently reverts it.
    - **Fold:** treat those keys as live-only too, or have `claude-tooling.md` say so. This is a method call, not a fork.

12. **[minor, optional] Stale kitty-shot prose survives A** (`plan:168-173`). `bluefin/Brewfile:31-35`, `bluefin/bootstrap.sh:365,383,499` and `docs/MIGRATION-BRIEF.md:96-100` still describe the `kitty-shot` harness. No gate leg scans them.
    - **Fold:** add the comment lines to A, or list them under "Found, not done".

13. **[minor, optional] Restore drops the settings preferences.** The restore excludes every top-level name in the `claude` package (`bootstrap.sh:726-731`), so a backup's real settings file is skipped and `apply` regenerates it without the preferences.
    - **Fold:** a line under "Found, not done".

14. **[minor, optional] Pass-class wording** (`plan:19-21`). The line says every task touches a `runner` path, but F's files are all `ordinary` under the path map. F's class comes from the design ("All are `runner`", `design:27`).
    - **Fold:** cite that.

15. **[minor, optional] A convention the plan's own runs break** (`plan:96-97`). "No command writes `~/.claude`" is breached by every `claude -p` run, which writes its transcript under `~/.claude/projects`.
    - **Fold:** "no tracked or configuration file in `~/.claude`".

16. **[minor, optional] Stale line citations in G** (`plan:490-491`). G cites `claude-tooling.md:17,45,51,56`, but I and D edit that file first.
    - **Fold:** cite by phrase.

17. **[minor, optional, OWNER FORK] Spend cap on the unattended Opus review** (`plan:559`, "Later"). The monthly run has no cap, and its first run takes the full re-fetch path.
    - Options: (a) leave it in Later; (b) add `--max-budget-usd` to the second call now.
    - Recommendation: (b). It is one flag on an unattended monthly spend, but it is beyond the design, so it is Geoff's call.

18. **[minor, optional] Auto-mode classifier risk for the dry run.** The executor prompt should name the dry run's `systemd-run` launch explicitly, so the pair's classifier sees an authorized action. The docs say "your message has to name the action and the specific thing".

19. **[minor, optional] Ratchet edit note** (`plan:101-105`). This is correct as written. In wave 2, B must change GA-05's `},` to `}`, because that entry becomes the last one. Name it in B's acceptance so the "fix the comma" rule is not missed.

Sources: Claude Code docs pages `worktrees` and `permission-modes`; `man systemd-run`; `man systemd.service`; stow, cp and git probes in `/tmp`; `claude-tooling-sync:57,77,112-127,163-209,482-498`; `tests/test_claude_tooling_sync.py:107-150`; `bluefin/bootstrap.sh:36-42,310-319,715-731`; `pass-core/SKILL.md:155-160,180-185`.
