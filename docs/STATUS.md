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
- **Lean pass process, step 1 merged** (`998859b`, PR #1; tag `pre-lean-process` at its parent
  `deed191`, pushed). The rewritten `pass-core`, the three adapters, the trimmed agents, the
  199-line global `CLAUDE.md`, the `cairn-run-gate` fixes, and the `claude-clock-stop` hook are
  live. The merge check, `claude-tooling-sync verify`, and
  the light-lane gate all passed in the main checkout.
- **Probes, all passed on 2026-10-10.** Pair probe: both `isolation: "worktree"` subagents
  branched from S1-T15's commit `5532034`, not `origin/main` (`998859b`); both gates printed
  `gate exit: 0`; the scratch merge was conflict-free and the gate on it exited 0. Clock stop: the
  call after `cd` into the probe worktree received "Clock stop: task probe has run 10 minutes
  against a 1-minute estimate"; the calls after removal and back in the main checkout carried
  none. Launch probe: `claude --bg` printed id `1d6eed4e`, committed `rd-probe.txt` (`ok`, `0`) on
  `worktree-rd-probe` under `.claude/worktrees/` unattended, pushed nothing, and was cleaned up.
- **Rollback** (Geoff's call only): the plan's S1-T14 "Rollback" block.
## Immediate next action

Steps 2 and 4 run as background sessions (`claude agents` lists them):
`lean-step2` is cairn-cms.
`lean-step4` (docs-chain audit) is PR-ready on `worktree-docs-chain-audit`: all six judged seats
kept (plan read, page structural read, register editor, fact read, figure verifier, final reader); no cut.
Geoff pastes step 3 as `lean-step3` from the plan's "Pre-launch for 3" block (ruling R-C).
Pass B (rollout step 5) starts once steps 1 and 2 have merged. Plan and spec: `docs/superpowers/plans/2026-10-10-lean-pass-cutover.md`, `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`.

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
