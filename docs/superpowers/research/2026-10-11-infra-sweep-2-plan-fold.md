# Infra sweep 2 plan review: fold record (2026-10-11)

Target: `docs/superpowers/plans/2026-10-11-infra-sweep-2.md` ("plan") and its launch prompt
`docs/superpowers/plans/2026-10-11-infra-sweep-2-prompt.txt` ("prompt"), reviewed at `cd0b5e4` by
the mechanics lens (`2026-10-11-infra-sweep-2-review-mechanics.md` beside this file, 19 findings),
folded on `2502196`. Each finding was checked against the code or the docs before it was taken.
Every `optional` finding is dropped unless its fold is a one-line correction that removes a real
error. Plan line numbers below are the revised file's.

## Probes

- **Stow folding and the ignore pattern** (`/tmp/fold-stow-probe/`, stow 2.4.1, `stow -n -v`). A
  scratch package `claude/.claude/{settings.json,CLAUDE.md,skills/a}` with `.stow-local-ignore`
  holding `^/\.claude/settings\.json$`. Into an empty home stow prints one `LINK: .claude =>
  ../pkg/claude/.claude`, so the ignored file stays reachable through the folded directory. Into
  a home holding a real `.claude/` it prints links for `CLAUDE.md` and `skills` only. So the
  pattern works and the acceptance needs the real directory. `bluefin/bootstrap.sh:42` lists
  `$HOME/.claude` in `STOW_SHARED_DIRS`, which `setup_stow` pre-creates "to keep stow from folding
  them" (`:36-37`, `:311-318`).
- **Pre-merge cutover** (`/tmp/fold-cutover-probe/`, scratch git repo). A tracked
  `settings.json` with `effortLevel: high`, a home link to it, and a write of `xhigh` through the
  link (status ` M settings.json`). Then `cp --remove-destination <link target> <link>` and `git
  checkout -- settings.json`: the home file is a `regular file` holding `xhigh`, the tracked file
  holds `high`, and `git status --porcelain` prints nothing.
- **`claude-tooling-sync` source.** `Paths.settings` is `home / ".dotfiles" / "claude" /
  ".claude" / "settings.json"` (`:77`); `apply` runs `subprocess.run(["claude", "mcp",
  "add-json", "-s", "user", ...], check=True)` for each manifest server missing from
  `<home>/.claude.json` (`:112-127`). `FORK_PHRASES` is `("under discussion", "during the
  session", "delegated", "ask the user", 'ask "')`, counted with `text.count(phrase)` over the
  lowercased body (`:57-58`, `:494-498`). Today's hits: `register-check:10,11,62,74`,
  `content-review:46`; neither description holds one.
- **Test fixture.** `fixture_home` (`tests/test_claude_tooling_sync.py:107-115`) writes an empty
  servers manifest and a tracked `settings.json` but no `<home>/.claude/settings.json`;
  `test_verify_passes_with_no_collision` (`:141-148`) runs `verify` on it with the stub `claude`.
- **E's grep.** `grep -rn -i 'geoff reads the pr\|geoff merges' claude/.claude/skills
  .claude/skills` prints only `pass-core/SKILL.md:60`.
- **Worktrees page** (`curl -sL https://code.claude.com/docs/en/worktrees.md`). `:21`: "on a new
  branch named `worktree-<name>`". `:60`: "Non-interactive runs with `-p` have no exit prompt, so
  Claude doesn't clean up their worktrees, and Claude Code leaves the lock it took on each one at
  creation in place ... if git refuses because the worktree is locked, run `git worktree unlock`
  on it first." `:92`: "Claude Code blocks a Bash or Monitor command that redirects git into the
  main checkout. The redirect can come through `git -C` ...". `:150-164`: `worktree.baseRef:
  "head"` branches from the current work; the tracked `settings.json` sets it.
- **Sub-agents page** (`.../sub-agents.md:915`): "A background subagent can leave a background
  Bash or PowerShell command running past the end of its turn. When that command ends, Claude Code
  sends the subagent a notification." The Bash tool caps a foreground call at 600000 ms (its own
  description: "max 600000 for a foreground command").
- **Settings pages** (`.../settings.md:522-526`, `.../settings-reference.md`). `/config` saves
  "Most options" to `~/.claude/settings.json`. The reference: `tui`, "Running `/tui fullscreen` or
  `/tui default` writes this key for you"; `autoMemoryEnabled`, "toggle it with `/memory` during a
  session, which writes this key to your user settings"; `skipDangerousModePermissionPrompt`,
  "Claude Code writes `true` here in your user settings when you accept that dialog once". All
  three are keys of today's tracked file.
- **`model-review-notify`** starts `set -uo pipefail` (no `-e`), so a refused `git pull` does not
  end the script.
- **pass-core "Launch prompt"**: "The prompt text lives in a committed file and is launched as
  `"$(cat <file>)"`".

## Dispositions

| # | Disposition | Where the revision carries it, or why refused |
|---|---|---|
| 1 | folded | Close step 6 (plan:574-588): the PR body's first line and "What goes live" put `cp --remove-destination` and `git -C ~/.dotfiles checkout -- claude/.claude/settings.json` before the merge, then the merge and its pull, then `apply`. Close step 5 (plan:570-572) puts the two pre-merge commands first in STATUS's next action. The sequence is probed above. |
| 2 | folded | G acceptance and Test (plan:532-546): the manual scratch-home run is dropped, with the reason; `fixture_home` writes a live settings file; the cutover case joins the pytest list. E2E 6 (plan:55-59) now names that test. |
| 3 | folded | G acceptance (plan:528-532): the pattern `^/\.claude/settings\.json$` and a scratch home holding a real `.claude/`, both probed. |
| 4 | folded | G outcome and Files (plan:519-524): a dotfiles-pass "Close checklist" line that a merge touching `claude/.claude/settings.json` is followed by `claude-tooling-sync apply`. E's Files (plan:479-482) drop `dotfiles-pass`, keeping wave 4 disjoint; E's grep never matched it. |
| 5 | folded | F outcome (plan:403-417): the probe claim corrected (one path, 8 turns, $0.78; the whole tree unmeasured until the dry run), and the first call names `--model opus --effort medium`. The same CLAUDE.md rule ("Every dispatch names a model and an effort") applies to the second call, which takes `--effort high`, as the Close's own Opus planning launch does. F acceptance (plan:438-443): the dry run runs with `run_in_background: true` and the pair waits for the documented completion notification. |
| 6 | folded | F acceptance (plan:444-451): branch `worktree-model-review-<YYYY-MM>`, the `ls-remote` pattern `refs/heads/worktree-model-review-*`, and `git worktree unlock` before removal, each quoted from the worktrees page. |
| 7 | folded | F outcome (plan:403-417): the launcher pulls with `git -C "$repo" pull --ff-only` before the calls (outside any Claude guard), a refused pull leaves local `HEAD`, `--dry-run` skips the pull, and the prompt goes as `"$(cat ...)"` text. F acceptance (plan:438-439, 448-449): F commits before the dry run and records the outcome by amending. |
| 8 | folded | B outcome (plan:273-275) names the argument `apply: yes/no`; B acceptance (plan:304-307) states that both fork-skill bodies hold none of the five phrases, with the grep. |
| 9 | refused | Optional. Parallel trigger runs and dropping "before" runs change pace, not correctness; the 175-minute A estimate already holds the serial runs. |
| 10 | folded | E1 (plan:460-463): the planning session also launches the executor after the "Execute" pre-launch checks, quoting design E1. |
| 11 | folded | G outcome (plan:511-518): `claude-tooling.md` says the tracked keys win at `apply`, so a command that writes one (`/tui`, `/memory`, per the settings reference) shows as `verify` drift until committed, and the next `apply` reverts it. A method call: documenting the rule beats moving policy keys such as `autoMemoryEnabled` out of the tracked file, which would lose them on a fresh machine. |
| 12 | refused | Optional, and its fold is three files of comment edits, not one line. The Scope convention routes the `kitty-shot` mentions in `bluefin/Brewfile:31-35`, `bluefin/bootstrap.sh:365,383,499`, and `docs/MIGRATION-BRIEF.md:96-100` to "Found, not done" if A meets them. |
| 13 | refused | Optional. A restore regenerates the settings file through `apply` and loses only the three preference keys, which the next `/model` or `/effort` choice rewrites. |
| 14 | folded | Pass class (plan:19-23): one-line correction; F's files map to `ordinary`, and the class comes from the design ("All are `runner` class") and F's unattended launch. |
| 15 | folded | Conventions (plan:98-100) and prompt (prompt:39-41): one-line correction to "no tracked or configuration file in `~/.claude`", since every `claude -p` run writes a transcript under `~/.claude/projects` and a literal reader could stop on it. |
| 16 | folded | G outcome (plan:511-515): `claude-tooling.md` cited by phrase, since I and D edit it first. One phrase ("`/effort` persists per model into `settings.json` through the stow link") also becomes false after G, so naming it removes a real error. |
| 17 | refused, to Later | Beyond the approved design: the session's scope rule puts it in the plan's "Later", never a task. The "Later" line already carries the spend cap (plan:602-603). |
| 18 | refused | Optional. Each pair's prompt carries F's acceptance verbatim, and it names the `systemd-run --user --wait --collect ... --dry-run` launch, so the classifier already sees the action and its target. |
| 19 | refused | Optional, and the reviewer marks it correct as written: the Conventions' "fix the comma the last remaining entry carries" (plan:104-107) already covers GA-05's `},`. |

## Clock

Folds 2, 3, 4, and 11 add work to G (the dotfiles-pass line, the fixture change, and the doc
rule): 60 to 70 minutes. Folds 5, 6, and 7 add work to F (the pull, the commit-then-amend, the
background wait, and the unlock): 135 to 145 minutes. The total moves from 955 to 975
task-minutes, and the path from 625 to 635 (plan:63-65).

## Rulings

None. No finding changes the approved design: 1 to 8, 10, 11, 14 to 16 are method calls inside
the design's tasks, and 17, the one marked OWNER FORK, is beyond the design and goes to "Later"
by the scope rule.

## Owed errata

None. The revision edits only the plan and its prompt.
