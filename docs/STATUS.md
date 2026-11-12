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

<!-- round-report ur-ws -->
Report: ~/Projects/initiatives/.claude/worktrees/unattended-rounds/unattended-rounds/reports/ur-ws-report.md

# Round ur-ws, glw907/workstation, written 2026-11-12 (round ended, all five passes merged)
Round state: ended

| Pass | State | PR | Planned min | Actual min | Usage before | Usage after |
| --- | --- | --- | --- | --- | --- | --- |
| W1 | merged | glw907/workstation#230 | 45 | ~50 plan path | week 68%, Fable 15% | week 72%, Fable 22% |
| W2 | merged | glw907/workstation#231 | 60 | ~35 | week 72%, Fable 22% | week 74%, Fable 26% |
| W4 | merged | glw907/workstation#232 | 150 | ~35 | week 81%, Fable 38% | week 83%, Fable 43% | |
| W5 | merged | glw907/workstation#233 | 100 | ~115 plus six hours parked | week 83%, Fable 43% | week 86%, Fable 48% | |
| W3 | merged | glw907/workstation#234 | 75 | ~30 | week 86%, Fable 48% | week 86%, Fable 50% | |

Stops: 1 (answered). W5 parked at its end-to-end check, because the plan's search for the initiative id counted a backlog tag as a miss. Geoff chose to narrow the search, and the relaunch ran clean. Refusals: 0 under rule 4 (the worktree guard refused a few chained commands, each rerun as plain commands). Calls sent to Geoff: 1 stop call, then 5 on two close packets (all answered with the recommended option); two reply notes on close packet 1, both answered.
Planning misses: W1: 1 design-gap, 1 stale-fact. W2: 1 file-list, 1 design-gap. W4: stale-fact (named in its plan). W5: 1 mechanism, 1 stale-fact, 1 conflict, 2 design-gap. W3: 2 stale-fact, 1 file-list, 2 design-gap, 1 mechanism.
Trials: Fable 5.2 planned 5 passes; 11 sessions under /goal; 0 idle before an end line.
Opus seats under rule 6: none.
Waiting for Geoff: nothing. Landed: W1 #230, W2 #231, W4 #232 (close packet 1, item 20261112T081618-3270413), W5 #233 and W3 #234 (close packet 2, item 20261112T083259-3290807). The main checkout is pulled to d323b4e, no stow ran, and the five pass worktrees and branches are removed. Follow-ups: backlog #75, #78, #79, #81, #82. The final usage read is week 89%, Fable 54%.
Busy check note: claude-worktree-busy exit 1 named only this conductor's own session (bb055eee, conductor-dotfiles); processes none, files clean.
STATUS copy: done, refreshed at each write.
Resume from: ~/Projects/initiatives/.claude/worktrees/unattended-rounds/unattended-rounds/plans/ur-ws-conductor-prompt.txt
Open packets: none.
<!-- /round-report -->

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
- **The lean pass process is in place** (spec: `docs/specs/2026-10-10-lean-pass-process-design.md`).

## Workstation refinement

Pass 1 of `workstation-refinement` merged as #225 (`c9d3cfa`) on 2026-11-10, and the after-merge
steps ran: relink and apply, the empty ratchet baseline removed, Blueprint moved to local scope in
the cairn-cms checkout, tellgrader reinstalled, the Fastmail flatpak uninstalled, 169 finished
worktrees removed with Geoff's approval, and `claude-tooling-sync verify` clean. The backlog sweep
stamps landed in one commit on `main`.

Pass 1 is closed. Geoff signed in to the Cloudflare plugin, removed the four claude.ai connectors,
and ran the settings and plugin command, which dropped two deny rules, a retired live-settings key,
and four user-scope plugins; `claude-tooling-sync verify` passes. Poplar's tracked settings still
enable the four removed plugins, which waits for poplar's next pass.

Pass 2 merged on 2026-11-11: glw907/workstation#227 (`8021d10`), glw907/approval-queue#14
(`1d2cbee`), and Survey 1.6.0 (glw907/survey#12, tag `v1.6.0`). `claude-merge-guard` denies every
`gh pr merge` and names `approval-queue merge <id>` and `approval-queue land`. The allow rule and
auto-mode entry for `approval-queue merge`, the rewritten `approval-packet` skill, and the Survey
packet writer's brief are live on pavilion, and the decision-review timer is disabled. The
existing `Bash(approval-queue *)` allow rule also covers `land` (Geoff left it as it is).

Pass 3 is in review as glw907/workstation#228, with glw907/standards#18 and Survey 1.7.0
(glw907/survey#11). It splits `pass-core` into a core skill and three role references (planner,
executor, conductor), so an executing session loads about 7,100 words where it loaded about
18,300. The global `CLAUDE.md` drops to 120 lines, and the `claude-clock-stop` hook is gone: a task
past twice its estimate gets one line in the PR's `## Decisions`. Reviews follow the pass's risk
class. The gate now checks the skill word caps and each role's load with `claude-pass-load`.
Nothing is live until the merge and the after-merge steps in the PR body.

The stack pilots, workstation part, merged as glw907/workstation#229 and are live on pavilion. The
gate has a changed-files lane (`bash scripts/gate.sh --scope-changed`), a timing line per leg, and a
`shellcheck` leg; `bluefin-admin.md` and the Cloudflare inventory are topic files behind short
indexes; `typescript-lsp` and `gopls-lsp` give the `LSP` tool its servers; and `rules/go.md` loads
the Go skills. The local `svelte-lsp` plugin is removed, since mise refuses its server (backlog
#71). The `check-drift` SC2140 finding is backlog #70. thinkpad-x1 owes the after-merge command.

**thinkpad-x1 owes one step.** `workstation-sync` brings it the guard, skill, settings, and
register, but never rebuilds the queue app or disables the timer. Its first session after the sync
runs `approval-queue pending` (empty, or collect what it lists with the old build first),
`npm ci --prefix ~/Projects/approval-queue/approval-queue`, `npm run build --prefix
~/Projects/approval-queue/approval-queue`, `pkill -f 'approval-queue/[b]uild'`, and `systemctl
--user disable --now decision-review.timer`, then checks that `approval-queue merge` with no id
exits 2. Pass 1 plan:
`~/Projects/initiatives/workstation-refinement/plans/2026-11-10-pass-1-workstation-plan.md`.

## Unattended rounds

Pass W4 of round `ur-ws` is on branch `ur-w4`: `pass-core` gains `references/round.md` and
`references/round-run.md`, which hold the round rules, and an executing session now loads about
8,800 words. Nothing is live until the merge.

Pass W5 is on branch `ur-w5`, cut from `ur-w4`: `approval-packet` and the packet writer's brief
learn the `round` key and the stop packet, `cairn-pass` "Packet" states ruling D1, and
`unattended-work-guards.md` gains the weekly usage ceiling. The brief is a vendored Survey file
edited ahead of its pin, which is a call for Geoff (backlog #79). Its end-to-end check passed on
`docs/plans/2026-11-11-ur-w5-outline.md` after Geoff's ruling on the check's search. The closing
review accepted the branch and left ten findings open on the outline, each a call for Geoff
(backlog #81). The PR is glw907/workstation#233, and it joins the round's close packet behind
#232.

Pass W3 is on branch `ur-w3`, cut from `ur-w5`: `claude-launch-guard` reads a `<slug>-plan.md`
sibling and denies a plan whose `## Pre-flight` lacks an `Evidence:` line, and the `CLAUDE.md`
pass section names the round's five touchpoints. The guard change is not live until Geoff
approves PR #234 and `~/.dotfiles` is pulled.

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

## Workstation sync

`workstation-sync` keeps each host current on a daily timer (`~/.claude/docs/bluefin-admin/update-cadence.md`). Pavilion owes its first start, and pairing waits on it: `bluefin/SECOND-WORKSTATION.md`
"Changes to carry to thinkpad-x1", the 2026-11-01 entry.

## Open items

Strategic and standing items live in `ROADMAP.md`. Findings the PR body lists as "Found, not
done" go to `BACKLOG.md` through `standards:log-issue`.

Neither `<host>-claude` agent has an expiry entry, so `check-drift` will not warn before
`pavilion-claude` lapses around 2027-01-20 or `thinkpad-claude` around 2027-02-01.
