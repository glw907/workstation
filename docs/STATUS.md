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

In dotfiles, infra sweep 1 (the guard) is built and awaits Geoff's read of its PR (branch
`worktree-infra-sweep-1`, session `infra-sweep-1`, job id `661df253`). Its gate is green and the
whole-branch review accepted it. After the merge, the next action is the sweep-2 planning
session, attended with Geoff, planned from the baseline sweep-1 leaves: 15 entries by check id
(`dead-reference` 2, `retired-phrase` 2, `relative-link` 2, `description-cap` 5, `fork-skill` 4).
Launch it with:
`cd ~/.dotfiles && claude --model opus --effort high --name infra-sweep-2-plan "$(cat docs/superpowers/plans/2026-10-11-infra-sweep-2-planning-prompt.txt)"`.

**Infra sweep after the cutover** (re-planned 2026-10-11; spec
`docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md` "Lean re-plan", evidence
`docs/superpowers/research/2026-10-11-infra-sweep-survivor-ledger.md`). A-core, B, and
style-guide-sync are merged. Geoff's rulings R1 to R4 split what survives into sweep-1 (the
guard's tools) and sweep-2 (skill and doc content). Poplar's `pass-core` adapter follows sweep-2.

**Infra skill build** (executing): background session `infra-skill-build`, id `7ff5a620`, branch
`worktree-infra-skill-build`. Plan: `docs/superpowers/plans/2026-10-11-infra-skill.md`. Two pairs
(T1+T2, then T3+T4), then the close.

## Open items

Strategic and standing items live in `ROADMAP.md`. Findings the PR body lists as "Found, not
done" are owed to the next dotfiles pass.
