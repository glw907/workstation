---
name: dotfiles-pass
description: >
  The workstation repo's facts (~/.dotfiles): its gate, its checks, which paths run unattended work
  or touch secrets, and how a merged change reaches the live machine, settings included. Use with
  building-from-specs when building, reviewing, or merging a task whose edits land in ~/.dotfiles
  (skills, agents, scripts, settings, docs).
---

# Dotfiles pass

Load `building-from-specs` first; it holds the process. This skill holds the repo's facts.
Dotfiles is a GNU Stow repo: files under `~/.claude` and `~/.local/bin` link into the main
checkout, so a change to a linked file is live once the main checkout pulls. An added or removed
script or skill needs a restow, and the settings need a sync ("After a merge").

## Gate

`bash scripts/gate.sh`, run from the checkout or worktree root. It runs `CAIRN_GATE_LANE=light
cairn-run-gate 'bash scripts/check.sh'`. A worktree-isolated session's Bash guard refuses the
wrapped string and accepts the no-argument wrapper. The light lane fits: the gate launches no
browser, and its measured peak is 105 MB.

The fast lane is `bash scripts/gate.sh --scope-changed`. It runs only the legs the working tree's
changes touch, plus the legs that always run, and its receipt never stands for the whole gate.

The repo has no PR test CI, so the gate on the branch's last commit is the only full run. The
task's worktree is the launch's `.claude/worktrees/<name>`, with no setup command.

## Checks

- `scripts/check.sh` lists every leg. The `pytest` leg's list names each script whose change
  runs it, so a new tested script adds its name there.
- The gate's gitleaks leg scans the working tree. At close, run one `gitleaks git` scan of the
  branch history, because the repo is public.
- `claude-tooling-sync verify` passes.
- A review loads `standards:python-conventions` for `*.py`, `standards:go-conventions` for `*.go`,
  and `standards:ts-conventions` for `*.{js,mjs,ts}`.
- Every new install records itself in its tier's manifest
  (`~/.claude/docs/bluefin-admin/software-tiers.md`).
- Prose follows the workstation writing voice. Vale and tellgrader run as `PostToolUse` hooks on
  each edit, and `scripts/check.sh` runs only their test suites.

## Paths

These paths run unattended work, so `building-from-specs` "Direct changes" lets only a wording
edit land there without a pull request: `claude/.claude/{skills,agents}/**`,
`claude/.claude/settings.json`, `claude/.claude/tooling/**`, `.claude/skills/**`, `scripts/**`,
`tests/**`, and
`bin/.local/bin/{cairn-run-gate,ci-green,ci-green-lib.mjs,claude-context-budget,claude-git-guard,claude-show-merge,claude-tooling-sync,claude-worktree-busy,task-report}`.

A task of a spec can be Show (`building-from-specs` "Merging") only outside the paths that
`claude-show-merge --ask-only glw907/workstation` prints, one glob per line. Run it before a spec marks a task Show.

These paths touch secrets, so a change there is sign-in or data work: a second reviewer reads it,
and the pull request is flagged for Geoff. They are `secrets/**`, `scripts/secrets/**`,
`bash/.bashrc` (it sources the secrets), and
`bin/.local/bin/{claude-block-pass,claude-pass,ws-pass-key,pass-count,pass-access,pass-sitting,check-drift,claude-secret-guard,claude-tierguard,claude-askpass,claude-sudo-setup,claude-sudo-clear,secret-receive}`.
A path in both lists takes the second.

## After a merge

The session Geoff is talking to pulls the main checkout, then runs these in order.

1. `stow -R bin` when the merge added, renamed, or removed a script, so `~/.local/bin` links it
   or drops its link. `find ~/.local/bin -xtype l` prints nothing after.
2. `stow -R claude` when the merge added, renamed, or removed a skill. Each skill is its own link
   under `~/.claude/skills/`. `find ~/.claude/skills -xtype l` prints nothing after.
3. `claude-tooling-sync apply`, then `claude-tooling-sync verify`, when the merge touched
   `claude/.claude/settings.json` or `claude/.claude/tooling/`. The live `~/.claude/settings.json`
   is a generated file, never stowed, so it doesn't follow a pull. `apply` writes each tracked
   top-level key over the live one and removes nothing, so delete from the live file each
   top-level key the merge removed.
