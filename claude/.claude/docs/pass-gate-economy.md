# Gate economy on a pass

This holds CLAUDE.md's "Gate economy on a pass" section; CLAUDE.md keeps a pointer to it.

Clock time on a pass is the per-task gate and the fix rounds, not the implementer. Rules, all
approved, all cheap in tokens:
- **The slow suite runs only where it can catch something.** A browser e2e or visual suite
  joins the per-task gate only for tasks that move rendered paint; paint-neutral tasks run the
  check suite and unit tests, and the pass-end gate plus CI on every push run the full suite.
  Across B2's eight tasks the per-task e2e caught nothing the checks, the diff reviewer, and CI
  did not, at a third of each task's hour.
- **Comment-only fix rounds run a reduced gate** (the comment linters, the doc link gate, and
  the touched files' unit tests). The reviewer marks each blocking finding `commentOnly`; the
  chains scripts route on it.
- **The pass class sets the ceremony** (Geoff, 2026-09-27). A plan header declares `Pass class:`
  (`auth-data`, `engine-logic`, `paint`, `sweep`, `docs`, `tool`), a task may override it, and
  the class picks the per-task gate, the review bar, the test mandate, and the close steps; the
  table lives in the `pass-core` skill. Both runners take `passClass` in their args and render
  it: the mandate into the implementer prompt, the bar into the reviewer prompt. Under every
  class but `auth-data`, a fix round whose findings are all `commentOnly` or `testOnly` runs the
  reduced gate, and under `engine-logic`, `paint`, `sweep`, and `docs` a `coverageOnly` finding
  moves to nonBlocking and returns as `batchedNotes` for the segment boundary. Born of the
  theme identity pass A evaluation (2026-09-27): a CSS retheme ran the full engine gate on every
  task (7 to 11 minutes, 5,167 node tests plus about 1,600 serialized browser component tests),
  carried about 4.4 test lines per source line, and reran that full gate on every test-only fix
  round, for a projected 8 to 10 unattended hours. Size alone never scaled the chain down; the
  kind of change now does.
- **Scope the engine test suite to the blast radius.** A task whose Files touch nothing under
  the engine's source runs the consumer's own unit suite, not the engine's.
- **A pre-flight checklist in every task's notes prevents the fix rounds** B2 kept paying for:
  no comment claims what its assertion does not prove; the labeled report block verbatim;
  no process citations in shipped comments; counts found, changed, deferred; re-emit before
  the gate.
- **Task 0 takes no gate** (Geoff, 2026-09-12): a read-only staleness pre-task runs none, and
  the lane's baseline is the conductor's own one `cairn-run-gate` call at lane launch, quoted
  to the reviewer as Task 0's gate evidence.
- **The cross-lane review fires on a disjunction** (Geoff, 2026-09-12): the merge ritual's
  `diff-reviewer` over the merged range runs when the rebase was not a fast-forward **or**
  when the two lanes touched a shared package or contested surface.
- **A scoped gitleaks leg owes a branch-history scan** (Geoff, 2026-09-12): where the gate
  scopes gitleaks to the change set, the merge ritual's in-tree gate adds one `gitleaks
  detect` over the branch's commit range, without `--no-git`.
- **Gates run through `cairn-run-gate '<string>'`** (dotfiles bin; generic despite the name):
  on exit 75, re-issue the same command until it prints `gate exit:`; never poll a log. This
  keeps an implementer's transcript small for the reviewer.
- **Parallel chains where Files are disjoint**, one worktree each, with any shared port made
  an environment variable; overlap a CI baseline regen with the diff review; fold
  single-deliverable tasks into a neighbor (each task pays about thirty minutes of fixed
  overhead).
- **Orchestrator hygiene:** halt agents PREPEND to STATUS, never rewrite it; a merge step brings
  `main` in first with fixed resolution rules (STATUS takes main's, HISTORY keeps both); a
  workstation workflow is invoked by name, never from a scratchpad copy, so every run executes
  the committed script, except after the script changed in the same session: by-name resolution
  can serve a stale copy (2026-10-01, run `wf_55b254af-82a` ran an earlier commit and redrafted six
  pages), so before relying on the run, `cmp` the persisted script the tool returns against the
  committed file, and on a mismatch stop it, copy the committed file over that returned path, and
  relaunch with `scriptPath` (when the tool refuses that path, as it did on 2026-10-03 after the
  session's working directory changed, copy the committed file into the session scratchpad,
  `cmp` it, and relaunch from there); repeated protocol text in args goes in one field the chains script
  appends at prompt time.
- **One full gate per machine at a time, and every gate memory-capped** (born 2026-09-14: the
  motion pass's two chains ran their full gates side by side, each with headless Chromium,
  the kernel OOM-killed a browser six times, and systemd-oomd then killed GNOME Shell, which
  took every open app and both conducting sessions with it). `cairn-run-gate` now runs the
  gate inside a transient user scope capped at 8G (`CAIRN_GATE_MEMORY_MAX`, with
  `CAIRN_GATE_MEMORY_HIGH` 7G and `CAIRN_GATE_SWAP_MAX` 4G), so a runaway browser dies inside
  the gate rather than the desktop, and every gate queues on one machine-wide lock per lane,
  so parallel chains never run two browser gates at once. **A gate that launches no browser
  takes the light lane** (`CAIRN_GATE_LANE=light`; Go's `make check`, a lint-only run): its own
  lock and a 3G cap, so it never waits behind a browser gate, and one light gate beside one
  heavy gate still fits in RAM. Set it in the run's args (`gateLane: "light"`, per run or per
  task), which both runners render into the implementer's gate command; nothing else carries
  it. Born 2026-09-20: the rule lived only in this file as a `CAIRN_GATE_PARALLEL=1` aside, no
  runner, agent definition, or plan carried it, the conductor never read this file, and a
  one-minute Go gate queued behind another session's e2e gates on nearly every task of cairn
  Go tool pass A, two to three hours in all. A resumed pass lands the chain that was nearest
  done first, then launches the rest.
- **code-simplifier runs once per pass or branch, at the close** (Geoff, 2026-09-27), and only
  when the pass changed TypeScript, Svelte, or Go. It no longer runs before every commit: a
  per-commit pass re-reads the same files each task and buys nothing the close run misses.
  Docs-only and CSS-only passes skip it.
- **The close ritual calls one `npm run check:close`** (cairn-cms, 2026-09-27) instead of a
  hand-kept list of check scripts. The script runs CI's check list in CI order, minus the unit
  and e2e suites, so a check added to CI is added to the script in the same change and the close
  can no longer drift behind CI.
