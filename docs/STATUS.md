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

## Immediate next action

Start a fresh conductor, so the work ahead runs under #8's rules (Geoff, 2026-10-11):
`cd ~/.dotfiles && claude --model opus --effort high --name conductor "$(cat docs/superpowers/plans/2026-10-11-conductor-prompt.txt)"`.

## Conductor

Handed over by session `c747c352` after #8 merged. In flight: the dubplate alignment executor,
session `dubplate-alignment` (id `394cf8c0`), unwatched until the new conductor arms a watch. The
queue, in order, with each item's detail in the launch prompt:

1. **Dubplate alignment PR.** After Geoff merges it, the conductor fast-forwards dubplate, backs up
   and then prunes dubplate's auto-memory per the PR body's dry run, and trashes the untracked
   `reports/` originals. Then dubplate's `admin-api-1` re-plan.
2. **cairn-cms alignment.** Approved by Geoff. Evidence and rulings:
   `docs/superpowers/research/2026-10-11-cairn-cms-alignment-audit.md`.
3. **Infra sweep 2.** The design on `worktree-infra-sweep-2-design` waits for Geoff. Re-check it
   against #8 first.
4. **Poplar adapter**, then the cairn-cms ROADMAP restructure after docs stage 2b.

Pending with Geoff: the review desk PR (#13), the sweep-2 design, and the dubplate alignment PR.
After #13 merges and the checkout is pulled, `stow -R bin` puts `review-desk` on PATH.

## Open items

Strategic and standing items live in `ROADMAP.md`. Findings the PR body lists as "Found, not
done" are owed to the next dotfiles pass.
