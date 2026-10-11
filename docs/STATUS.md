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
- **Lean pass process, step 1 PR-ready**: the rewritten `pass-core`, the three adapters
  (`cairn-pass`, `site-pass`, `.claude/skills/dotfiles-pass`), `spec-plan-review`, the trimmed
  agents, the 199-line global `CLAUDE.md`, the `cairn-run-gate` fixes, and the `claude-clock-stop`
  hook. The `pass-execute` runners and the two economy docs are deleted. `docs/HISTORY.md` is
  frozen (ruling 8).

## Immediate next action

Geoff reads the PR (`glw907/workstation`, branch `lean-cutover`) and runs the plan's "Merge
block" in a terminal with no Claude session open:
`docs/superpowers/plans/2026-10-10-lean-pass-cutover.md`. It launches session 1b, which tags
`pre-lean-process`, runs the probes, and starts steps 2 and 4 with `--bg`. Step 3 is Geoff's paste
per the plan's "Pre-launch for 3". Pass B (rollout step 5) follows steps 1 and 2. Dotfiles `main`
stays frozen until the merge. Spec: `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`.

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
