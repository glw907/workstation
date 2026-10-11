---
name: dotfiles-pass
description: >
  The adapter for the lean pass process in the workstation repo (~/.dotfiles): gate, fast lane,
  full-suite home, worktree setup, risk-class path map, checklist globs, and close checklist. Use
  when planning, executing, or closing a pass whose edits land in ~/.dotfiles (skills, agents,
  workflows, scripts, settings, docs).
---

# Dotfiles pass

Load `pass-core` first; it holds the lifecycle and the rules this adapter fills in. Dotfiles is a
GNU Stow repo: `~/.claude` and `~/.local/bin` link into the main checkout, so a merge there is live
on the machine at once, and a new `bin` script needs `stow -R bin`.

**Gate**: `CAIRN_GATE_LANE=light cairn-run-gate 'bash scripts/check.sh'`. The light lane fits: the
gate launches no browser and its measured peak is 105 MB.

**Fast lane**: The same command. It takes about 76 seconds, so no narrower lane exists.

**Full-suite home**: That same command, once on the close head. Dotfiles has no PR test CI (ruling
11; ROADMAP carries the Planned item), so the local close run is the only full run.

**Worktree setup**: The launch's `.claude/worktrees/<name>`; no setup command.

**CI watch**: None.

**Risk-class path map**: `runner`: `claude/.claude/{skills,agents,workflows}/**`,
`claude/.claude/settings.json`, `claude/.claude/tooling/**`, `.claude/skills/**`,
`bin/.local/bin/{cairn-run-gate,ci-green,ci-green-lib.mjs,claude-clock-stop,claude-tooling-sync}`,
`scripts/**`, `tests/**`. `auth-data`: `secrets/**`, `scripts/secrets/**`, `bash/.bashrc` (it sources the
secrets), and `bin/.local/bin/{claude-block-op,claude-secret-guard,claude-tierguard,claude-askpass,
claude-sudo-setup,claude-sudo-clear,secret-receive,fastmail-password,fastmail-dav-password}`.
`ordinary`: everything else. A path in both classes takes the higher (`scripts/secrets/**` is
`auth-data`).

**Checklist globs**: The close review loads `python-conventions` for `*.py`, `go-conventions` for
`*.go`, and `ts-conventions` for `*.{js,mjs,ts}`.

**Close checklist**: Beyond `pass-core` "Close": every new install records itself in its tier's
manifest (`~/.claude/docs/bluefin-admin.md`), and `claude-tooling-sync verify` passes. The gate's gitleaks step scans the working tree, so run
one `gitleaks git` branch-history scan at close. A merge to
`main` is followed by `stow -R bin` when a script was added. Prose follows the workstation writing
voice; `scripts/check.sh` runs the Vale and tellgrader nets.
