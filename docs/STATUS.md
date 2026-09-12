# Status

Dotfiles and machine configuration for one Bluefin DX workstation
(`thinkpad-x1`, Fedora 44 base, `bootc`/`ostree`). GNU Stow links tracked
config into `$HOME`; `bluefin/` holds the fresh-machine provisioning
artifacts. github.com/glw907/workstation.

## Current state

Post-migration reorg complete: the repo describes the Bluefin machine as it
actually stands, not the retired Mint 22 desktop setup.

- **Stow packages** (single source: `bluefin/stow-packages.txt`): `bash beets
  bin claude contacts git kitty mise upkeep vale`. `bluefin/bootstrap.sh` and
  `check-drift` both read that file.
- **Layered RPMs** (`bluefin/layered-packages.txt`): `1password
  1password-cli firefox chromium`, kept deliberately minimal and
  change-controlled through `docs/MIGRATION-BRIEF.md`.
- **CLI tools**: Homebrew (`bluefin/Brewfile`) for most formulae; `uv tool
  install` for Python CLIs (`khard`, `vdirsyncer`, `yt-dlp`, `ruff`, `jrnl`,
  `beets`); `mise` for per-project Node.
- **Flatpaks** (`bluefin/flatpaks.txt`): deliberate installs beyond
  Bluefin's stock set only.
- **Secrets**: age-encrypted in `secrets/values.age`, synced by
  `scripts/secrets/sync.sh`; architecture and inventory in
  `secrets/registry.md`. Write-time guards: claude-secret-guard hook,
  gitleaks pre-commit, GitHub push protection.
- **Gate**: `scripts/check.sh` (shell syntax, ruff-D, tests, vale fixtures,
  gitleaks, tellgrader go check).
- **Docs standard, plan one closed**: the tellgrader `docs-register` profile and opt-in
  discovery, `MEASURES.md` as the canonical measure definition, the output-style and voice-file
  updates, the path-grading Vale hook, the four review agents (including the new
  `figure-verifier`), and the two skills (`cairn-figure`; `writing-voice`'s renamed
  author-facing section). Unit 3c stays open: both `CLAUDE.md` files still owe the owner's
  four-line pick, ranked in
  `docs/superpowers/plans/2026-09-08-claude-md-displacement-candidates.md`, batched with the
  docs-standard corpus approval.

## Immediate next action

**The Claude infra round stood down at the battery floor (11%, 2026-09-12 13:56) mid segment B.**
Plan: `docs/superpowers/plans/2026-09-12-claude-infra-round.md` (revision 2). Closed and accepted:
segment A (tasks 1, 2, 3 at `95c65a7`, `f905328`, `dbb653d`; dubplate `a30d32e`), and segment B's
tasks 4 and 5 (`aa20264`, `a2c6463`, with their site-repo and dubplate commits). Task 6 (model-economy
doc) and task 7 (the two displacement destination docs) were in flight in workflow `wf_db12879d-af0`
when it was stopped; check `git status --short` for a warm `claude/.claude/docs/model-economy.md` and
keep or revert it by reading it, never blindly. **Resume prompt:** "Resume the Claude infra round at
tasks 6 and 7 (segment B remainder) from the plan, revision 2, then segment C (8, 9, 10). Task 9 runs
only after the cairn overnight workflow `wf_2d52758e-603` has ended." Segment A spent about 0.38M;
the 80% flag is 1.2M of the 1.5M ceiling. `claude/.claude/agents/cairn-implementer.md` stays
off-limits: a cairn session owns its warm diff.

Carried after the round: plan two of the cairn documentation standard
(`docs/superpowers/plans/2026-09-08-docs-standard-claude-infra-handoff.md`); `cairn-cms/CLAUDE.md`'s
own four-line pick and budget trim; dubplate-implementer's gate example names the main tree, so a
worktree lane must be told the dispatch's own absolute string wins (task 1 review note).

## Open items

Strategic and standing items live in `ROADMAP.md` (history purge decision,
musicbox repo split, devcontainers, kitty-harness replacement, custom uBlue
image, restore split, the cairn documentation standard).

## History

Per-pass ledger: `docs/HISTORY.md`.
