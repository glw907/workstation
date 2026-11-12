# Status

<!-- round-report ur-ws -->
Report: ~/Projects/initiatives/.claude/worktrees/unattended-rounds/unattended-rounds/reports/ur-ws-report.md

# Round ur-ws, glw907/workstation, written 2026-11-12 (W5 parked, stop packet sent)
Round state: waiting for Geoff

| Pass | State | PR | Planned min | Actual min | Usage before | Usage after |
| --- | --- | --- | --- | --- | --- | --- |
| W1 | waiting (close packet) | glw907/workstation#230 | 45 | ~50 plan path | week 68%, Fable 15% | week 72%, Fable 22% |
| W2 | waiting (close packet) | glw907/workstation#231 | 60 | ~35 | week 72%, Fable 22% | week 74%, Fable 26% |
| W4 | waiting (close packet) | glw907/workstation#232 | 150 | ~35 | week 81%, Fable 38% | week 83%, Fable 43% | |
| W5 | parked | glw907/workstation#233 (draft) | 100 | ~110 so far | week 83%, Fable 43% | week 85%, Fable 46% (read before relaunch) | |
| W3 | not started | none | 75 | | | |

Stops: 1. W5 parked at its end-to-end check: the plan's search for the initiative id counted two outlines as misses, and a second miss is a stop under standing answer 12. One stop packet sent, one unforced call (narrow the search, recommended). Refusals: 0. Calls sent to Geoff: 1.
Planning misses: W1: 1 design-gap, 1 stale-fact. W2: 1 file-list, 1 design-gap. W4: read from PR #232 (stale-fact line named in its plan; not yet tallied).
Trials: Fable 5.2 planned 4 passes (W5 launching); 6 sessions under /goal; 0 idle before an end line.
Opus seats under rule 6: none.
Waiting for Geoff: the W5 stop packet (queue item 20261112T013106-2940020). W1 #230, W2 #231, and W4 #232 hold for the close packet after the last pass ends. W3 is not started: W5 holds it. Landed: nothing.
Busy check note: claude-worktree-busy exit 1 named only this conductor's own session (bb055eee, conductor-dotfiles); processes none, files clean.
STATUS copy: done, refreshed at each write.
Resume from: ~/Projects/initiatives/.claude/worktrees/unattended-rounds/unattended-rounds/plans/ur-ws-conductor-prompt.txt
Open packets: W5 stop packet, queue item 20261112T013106-2940020.
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
