# Status

<!-- round-report ws-documents -->
# Round ws-documents, glw907/workstation, written 2026-11-12 21:06 (D0 merged, waiting for queue pass A5)
Round state: running

| Pass | State | PR | Planned min | Actual min | Usage before | Usage after |
| --- | --- | --- | --- | --- | --- | --- |
| D0 | merged | glw907/workstation#235 | 30 | ~21 | week 63%, Fable 0% | week 63% |
| D1 | not started | | 120 | | | |
| D2 | not started | | 120 | | | |
| D3 | not started | | 140 | | | |

Stops: 0. Refusals: 0. Calls sent to Geoff: 0.
Planning misses: none yet.
Two-repo packet: `approval-queue packet --check` accepted a fact file naming a workstation and an approval-queue pull request (snapshot took both), so one close packet is planned.
Waiting for Geoff: nothing. Landed: D0 #235 (the busy check skips its caller). Waiting on the queue round: pass A5 has not merged.
Resume from: ~/Projects/initiatives/.claude/worktrees/unattended-rounds/unattended-rounds/plans/ws-documents-conductor-prompt.txt
Open packets: none.
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

- **thinkpad-x1 owes one step.** After `workstation-sync` brings it the new queue, its first session
  runs `approval-queue restart` (it names any old item still undecided and archives the old files
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
