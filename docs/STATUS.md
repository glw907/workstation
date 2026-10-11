# Status

Dotfiles and machine configuration for one Bluefin DX workstation
(`thinkpad-x1`, Fedora 44 base, `bootc`/`ostree`). GNU Stow links tracked
config into `$HOME`; `bluefin/` holds the fresh-machine provisioning
artifacts. github.com/glw907/workstation.

## Current state

- **Stow packages** (single source: `bluefin/stow-packages.txt`): `bash beets
  bin claude contacts git kitty mise upkeep vale`. `bluefin/bootstrap.sh` and
  `check-drift` both read that file.
- **Layered RPMs** (`bluefin/layered-packages.txt`): `1password
  1password-cli firefox chromium`, kept minimal and change-controlled through
  `docs/MIGRATION-BRIEF.md`.
- **CLI tools**: Homebrew (`bluefin/Brewfile`); `uv tool install` for Python
  CLIs; `mise` for per-project Node. **Flatpaks**: `bluefin/flatpaks.txt`.
- **Secrets**: age-encrypted in `secrets/values.age`, synced by
  `scripts/secrets/sync.sh`; inventory in `secrets/registry.md`.
- **Gate**: `scripts/check.sh`.
- **Lean pass process live; rollout steps 1 to 4 merged.** Step 1 is dotfiles #1 (`998859b`;
  tag `pre-lean-process` at its parent `deed191`; rollback is Geoff's call only, from the plan's
  S1-T14 block). Step 2 is cairn-cms #112 (merge `aacaa46c`). Step 3 is six PRs: ecxc-ski #1,
  907-life #1, aksailingclub-org #12, xcathletes-org #1, cairn-pub #1, and dubplate #1. Step 4 is
  dotfiles #2, the docs-chain audit, which kept all six judged seats. Dotfiles #3 carried step 3's
  owed dotfiles items. Plan and spec: `docs/superpowers/plans/2026-10-10-lean-pass-cutover.md`,
  `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`.

## Immediate next action

Rollout step 5, engine pass B, runs unattended as background session `engine-pass-b` (id
`0d52ae78`) in cairn-cms. Its plan is `docs/superpowers/plans/2026-10-10-engine-pass-b-lean.md`
on cairn-cms branch `engine-pre-2b-b`. It merges its own PR (Geoff's ruling) and notifies at a
stop or at the merge. While it is live (`claude agents --json`), no other session touches
cairn-cms, its main checkout, or its worktrees.

In dotfiles, the infra sweep is being re-planned as a lean pass (below).

**Infra sweep after the cutover** (decided 2026-10-10; spec
`docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`, audit
`claude/.claude/docs/record/2026-09-28-claude-infra-audit.md`). An audit item is superseded when
the cutover rewrites or deletes the file it targets. Items on files the cutover leaves alone
survive, and their pass is re-planned in the lean format after rollout step 3.

- Style-guide-sync (cairn-cms): chain W's content survives as a lean task list; runner
  amendments are superseded.
- A-rest: the seat check and the `pass-core` close wiring are superseded; the context-budget
  check, remaining reference checks, cross-repo mode, drift routine, and release trigger survive.
- C: findings on `pass-core`, `spec-plan-review`, `cairn-pass`, and `site-pass` are superseded.
  D survives whole. E: AW-11, AW-21, DC-19, and DC-21 are superseded. F: the cairn-cms and site
  rows are superseded by steps 2 and 3; the poplar row survives.

## Open items

Strategic and standing items live in `ROADMAP.md`. Findings the PR body lists as "Found, not
done" are owed to the next dotfiles pass.
