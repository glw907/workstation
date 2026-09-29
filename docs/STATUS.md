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
- **Claude infra round closed**: the exit-75 reattach protocol is correct in every
  implementer that calls `cairn-run-gate`; `svelte-check` and `go-architecture-reader` are
  hoisted to workstation agents; the workstation and dubplate instruction files are hoisted
  with repo-specific supplements; `claude/.claude/CLAUDE.md` displaced to 23,947 bytes and
  picked up the docs standard's four lines. Handoff:
  `docs/superpowers/plans/2026-09-12-claude-infra-round-handoff.md`.
- **Docs standard, plan one closed**: tellgrader's `docs-register` profile, `MEASURES.md`,
  the output-style and voice-file updates, the path-grading Vale hook, the four review agents
  (including `figure-verifier`), and the two skills (`cairn-figure`; `writing-voice`'s
  renamed author-facing section).

- **Spec and plan review skill (2026-09-23)**: `spec-plan-review` encodes the dubplate rung 6
  review process (lenses, a fold that may refuse, a verification read, prose last). The
  dubplate-owed `pass-execute.js` edit is done: `stopOnEscalate` (default true, sequential runs)
  ends a run at the first unaccepted task and marks the rest skipped.

## Immediate next action

Claude infra sweep, passes A-core then B: plan
`docs/superpowers/plans/2026-09-28-infra-sweep-a-core-b.md` (spec
`docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`, audit
`claude/.claude/docs/record/2026-09-28-claude-infra-audit.md`). Conducted from a cairn-cms session
started 2026-09-28; task ledger below. After B merges, the cairn-cms style-guide-sync plan is
re-baselined on the corrected infra, then A-rest, C and D, E, and the per-repo F chores follow.

Ledger: A-core and B merged (fill in: merge SHAs recorded after the conductor's merge); next
action is the cairn-cms style-guide-sync re-baseline (apply the sweep spec's ten amendments to
that plan, run its verification read, then execute on the corrected infra), then A-rest (spec
now includes the monthly drift routine, the release trigger for Anthropic practice, and the
combined context budget), then C and D, E, and the per-repo F chores.

Owed, still open from the infra round's handoff: `cairn-cms/CLAUDE.md`'s own four-line pick and
budget trim; poplar's `go-architecture-reader` adoption; whether the overnight-run runaway guard
should become an armable script in `bin/.local/bin/`; the dubplate-implementer worktree
gate-string note.

## Open items

Strategic and standing items live in `ROADMAP.md` (history purge decision,
musicbox repo split, devcontainers, kitty-harness replacement, custom uBlue
image, restore split, the cairn documentation standard).

## History

Per-pass ledger: `docs/HISTORY.md`.
