# Status

<!-- round-report ws-documents -->
# Round ws-documents, glw907/workstation, ended 2026-11-13 (all four pull requests merged, queue switched on pavilion)
Waiting for Geoff: nothing. The round report is in the new queue.
Resume from: ~/Projects/initiatives/.claude/worktrees/unattended-rounds/unattended-rounds/plans/ws-documents-conductor-prompt.txt
<!-- /round-report -->

Dotfiles and machine configuration for two Bluefin DX workstations, the `thinkpad-x1` laptop and
the `pavilion` desktop (Fedora 44 base, `bootc`/`ostree`). GNU Stow links tracked config into
`$HOME`; `bluefin/` holds the fresh-machine provisioning artifacts. github.com/glw907/workstation.

## Current state

- **Stow packages** (`bluefin/stow-packages.txt`): `bash beets bin claude contacts git kitty mise
  upkeep vale`. The one layered RPM is `chromium` (`docs/MIGRATION-BRIEF.md`).
- **CLI tools**: Homebrew (`bluefin/Brewfile`), `uv tool` for Python, `mise` for Node. **Flatpaks**:
  `bluefin/flatpaks.txt`. **Secrets**: `secrets/values.age`, inventory in `secrets/registry.md`.
- **Gate**: `bash scripts/gate.sh`. The lean pass process is in place
  (`docs/specs/2026-10-10-lean-pass-process-design.md`).

## Open steps

- **thinkpad-x1 owes one step.** Its first session pulls `~/.dotfiles` and `~/Projects/approval-queue`,
  then runs `approval-queue restart` (it names any old item still undecided and archives the old files
  into `archive-2026-11.tar.gz`; see the queue's README, "Restart and the archive"), disables the
  old timer with `systemctl --user disable --now decision-review.timer`, and checks that
  `approval-queue merge` with no id exits 2.
- **Google Sheets check.** `gws drive files list` should still answer without a new sign-in; if it
  asks, move the `gws-personal` consent screen back to Testing (the 2026-11-05 check is open;
  `docs/plans/2026-10-29-google-sheets-tooling-plan.md`).
- **Workstation sync.** Pavilion owes its first timer start, and pairing waits on it
  (`bluefin/SECOND-WORKSTATION.md`, "Changes to carry to thinkpad-x1", the 2026-11-01 entry).
- **Poplar's tracked settings** still enable four removed plugins; that waits for poplar's next pass.
- **Open items.** Strategic items live in `ROADMAP.md`; findings a PR lists as "Found, not done"
  go to `BACKLOG.md` through `standards:log-issue`.
- **Agent expiry.** Neither `<host>-claude` agent has an expiry entry, so `check-drift` will not warn
  before `pavilion-claude` lapses around 2027-01-20 or `thinkpad-claude` around 2027-02-01.
