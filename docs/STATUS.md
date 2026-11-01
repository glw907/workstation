# Status

Dotfiles and machine configuration for two Bluefin DX workstations, the
`thinkpad-x1` laptop and the `pavilion` desktop (Fedora 44 base,
`bootc`/`ostree`). GNU Stow links tracked config into `$HOME`; `bluefin/`
holds the fresh-machine provisioning artifacts. github.com/glw907/workstation.

## Current state

- **Stow packages** (single source: `bluefin/stow-packages.txt`): `bash beets
  bin claude contacts git kitty mise upkeep vale`. `bluefin/bootstrap.sh` and
  `check-drift` both read that file.
- **Layered RPMs** (`bluefin/layered-packages.txt`): `chromium`, kept minimal
  and change-controlled through
  `docs/MIGRATION-BRIEF.md`.
- **CLI tools**: Homebrew (`bluefin/Brewfile`); `uv tool install` for Python
  CLIs; `mise` for per-project Node. **Flatpaks**: `bluefin/flatpaks.txt`.
- **Secrets**: age-encrypted in `secrets/values.age`, synced by
  `scripts/secrets/sync.sh`; inventory in `secrets/registry.md`.
- **Gate**: `scripts/check.sh`, run as `bash scripts/gate.sh`.
- **The lean pass process is fully in place.** Rollout steps 1 to 5 merged; step 5, engine pass B
  (cairn-cms #113), took 6.1 hours of clock against the 9-hour test. Plan and spec:
  `docs/plans/2026-10-10-lean-pass-cutover.md`,
  `docs/specs/2026-10-10-lean-pass-process-design.md`.

## Conductor

Conductor `4bea6e68` closed the 2026-10-11 infrastructure initiative; its PRs (#11 to #23) carry
the record. Each later initiative runs its own `conductor-<project>`, and the next one starts from
the repos' ROADMAPs and the initiative records.

## Docs system

Docs are code: cairn-cms pages change with the code, and a `docs` review in the Approval Queue puts them before Geoff. The initiative record (`~/Projects/initiatives/docs-system`) holds the current status and the next launch prompt.

## Approval queue

Merged 2026-10-12 as workstation #43 (`fefe984`): briefs, the rebuilt pages, and the rename to
`approval-queue` (no alias); the After merge steps ran. Deferrals: ROADMAP "Approval queue brief
leftovers".

## Google Sheets tooling

Built 2026-10-29, merged 2026-10-31 as #169 (plan `docs/plans/2026-10-29-google-sheets-tooling-plan.md`):
the `google-sheets` skill, `clasp` through `mise`, and trigger tests; the gear sheet passed end
to end (ecxc-ski `f8488b8`). On 2026-11-05, check that `gws drive files list` still answers
without a new sign-in; if it asks, move the `gws-personal` consent screen back to Testing.
thinkpad-x1 owes: pull, `stow -R claude`, `mise install`, `claude-tooling-sync apply`, then the
`gws` and `clasp` sign-ins in `bluefin-admin.md` "Google Workspace (gws, clasp)".

## Open items

Strategic and standing items live in `ROADMAP.md`. Findings the PR body lists as "Found, not
done" go to `BACKLOG.md` through `standards:log-issue`.

thinkpad-x1 also owes Survey 1.2.0 (workstation #138, merged 2026-10-22): on its next session,
pull `~/.dotfiles`, then run `stow -R claude`, `stow -R bin`, and `claude-tooling-sync apply`. The
first wording correction there clones `glw907/survey-notes`; the monthly writing review runs on
pavilion only.

thinkpad-x1 still owes the Proton Pass move that pavilion finished on 2026-10-19. A session there
follows `bluefin/THINKPAD-PROTON.md` with Geoff at the keyboard.
Its step 3 now includes Claude's own agent, `thinkpad-claude`. Pavilion's `pavilion-claude` agent
(created 2026-10-20, three-month expiry) has no expiry entry, so `check-drift` will not warn
before it lapses around 2027-01-20.
