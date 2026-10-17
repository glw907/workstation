# Status

Dotfiles and machine configuration for two Bluefin DX workstations, the
`thinkpad-x1` laptop and the `pavilion` desktop (Fedora 44 base,
`bootc`/`ostree`). GNU Stow links tracked config into `$HOME`; `bluefin/`
holds the fresh-machine provisioning artifacts. github.com/glw907/workstation.

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
- **Gate**: `scripts/check.sh`, run as `bash scripts/gate.sh`.
- **The lean pass process is fully in place.** Rollout steps 1 to 5 merged; step 5, engine pass B
  (cairn-cms #113), took 6.1 hours of clock against the 9-hour test. Plan and spec:
  `docs/superpowers/plans/2026-10-10-lean-pass-cutover.md`,
  `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`.

## Conductor

Conductor session `4bea6e68` closed the 2026-10-11 infrastructure initiative. Landed: dubplate
alignment (#2, triage #3); cairn-cms alignment (#114, workstation #12, triage #115 and #14); the
found-item triage rule (#11); the approval queue (#13, its UI pass #22 and triage #23, with Geoff's
`autoMode.allow` rule in #15); infra sweep 2 (#16, triage #17, ecxc-ski #2, aksailingclub-org #13);
the merge guard (#18, #20); the conductor lessons in `pass-core` (#21); and poplar's `pass-core`
adapter (poplar #1). The rebuilt app serves #22's UI.

Outside this initiative, each for its own session: `admin-api-1` runs on in dubplate (executor
`6baa2add`, no merge pre-approval; then `claude rm 18bbe825`, a stopped launch sharing its
worktree); poplar's development work in its ROADMAP (2c's re-plan, the Bubble Tea refactor, the gate
and toolchain repairs); the cairn-cms ROADMAP restructure after docs stage 2b. The next conductor
starts from the repos' ROADMAPs.

Escape (conductor, 2026-10-11): merged #16 before its pre-merge settings cutover, so a pull
dropped Geoff's live `model`, `effortLevel`, and `modelSettings`; restored by hand. The merge guard
(#18) now blocks a merge whose PR has a `## Before merge` section until it is acknowledged.

## Drafter

Completion ended 2026-10-14 (drafter#11-#37, workstation#61, cairn-cms#124): **not pilot-ready**, since both real pages escalated in the chain's plan step before drafter ran; no drafter fault, $0.001 spent.
Next: drafter#38 (fix the plan step, then a third page); other "now" items drafter#39-41, workstation#72, cairn-cms#125-126, none launched. thinkpad-x1 runs `make -C ~/Projects/drafter install` before pulling dotfiles.
The repo organization pass (spec ~/Projects/initiatives/repo-organization/specs/2026-10-14-repo-organization-design.md) moves drafter's docs and the docs page chain after pass 5 merges; it owns the local config path and the agent-*-worktree cleanup.

## Approval queue

Merged 2026-10-12 as workstation #43 (`fefe984`): briefs, the rebuilt pages, and the rename to
`approval-queue` (no alias); the After merge steps ran. Deferrals: ROADMAP "Approval queue brief
leftovers".

## Open items

Strategic and standing items live in `ROADMAP.md`. Findings the PR body lists as "Found, not
done" go to `BACKLOG.md` through `log-issue`.
