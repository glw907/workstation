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
- **Gate**: `scripts/check.sh`, run as `bash scripts/gate.sh`.
- **The lean pass process is fully in place.** Rollout steps 1 to 5 merged; step 5, engine pass B
  (cairn-cms #113), took 6.1 hours of clock against the 9-hour test. Plan and spec:
  `docs/superpowers/plans/2026-10-10-lean-pass-cutover.md`,
  `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`.
- **Merged since, 2026-10-11:** infra sweep 1, the guard (#5); PRs open in Geoff's browser (#4); a
  repo's checkout is pulled after its PR merges (#7); the `claude-infra` skill, Anthropic's scope
  prompts in `pass-core`, review depth by design size, the `plan-reviewer` agent, the
  `claude-tail-guard` hook, and the guidance-citation warning (#8). Evidence for #8:
  `docs/superpowers/research/2026-10-11-anthropic-guidance-proportionality.md`.

## Conductor

Conductor session `4bea6e68` (2026-10-11). Landed and merged: dubplate alignment (PR #2) and its
triage (#3); cairn-cms alignment (#114, workstation #12) and its triage (#115, #14); the found-item
triage rule (#11); the review desk v1 (#13) and its triage with Geoff's `autoMode.allow` rule (#15);
infra sweep 2 (#16) and its triage (#17, ecxc-ski #2, aksailingclub-org #13); the merge guard (#18,
#20). In flight, each watched:

1. **`admin-api-1`** (dubplate, executor `6baa2add`). Geoff pre-approved its merge: merge only on a
   green gate, every review and the security read accepting, and no `## Before merge` steps
   outstanding; its found items still go to the desk as triage. Then `claude rm 18bbe825` (a
   stopped first launch that shares the executor's worktree).
2. **Review desk UI pass** (planner `ebc278e8`; design and mockups on `worktree-desk-ui-design`).
   Launch its executor when the plan lands under 240 minutes. On merge, stop and rebuild the
   running desk.
3. **Poplar adapter.** Geoff asked for its design next. Its planning prompt runs as `cd
   ~/Projects/poplar && claude --model opus --effort high --name poplar-adapter-plan "$(git -C
   ~/.dotfiles show main:docs/superpowers/plans/2026-10-11-poplar-adapter-planning-prompt.txt)"`.
4. Later, outside this initiative: the cairn-cms ROADMAP restructure after docs stage 2b.

Escape (conductor, 2026-10-11): merged #16 before its pre-merge settings cutover, so a pull
dropped Geoff's live `model`, `effortLevel`, and `modelSettings`; restored by hand. The merge guard
(#18) now blocks a merge whose PR has a `## Before merge` section until it is acknowledged.

## Open items

Strategic and standing items live in `ROADMAP.md`. Findings the PR body lists as "Found, not
done" are owed to the next dotfiles pass.
