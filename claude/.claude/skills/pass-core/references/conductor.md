# Conductor

Read after `pass-core` `SKILL.md`. The conductor is named `conductor-<project>`, after the repo
whose main checkout launches the executor, and owns every PR its passes open.

## Hand-off

The session that acts on Geoff's approve of the round's design launches the conductor from the
main checkout with
`claude --bg --model sonnet --effort medium --name conductor-<project> "$(cat <file>)"` when
`claude agents --json` lists none. Otherwise it sends the live one the prompt's absolute path with
`SendMessage` and waits for its one-line reply, launching instead if the conductor just ended. A
held or refused message, or no reply within 10 minutes, starts nothing: the session writes the
stall into the repo's `docs/STATUS.md`, never the report file, which would read as a resume.

Each pass's planner launches its executor. A failed executor launch parks the pass as `round.md`
"Parking at planning" says, with the failure as the stop. The conductor only relaunches executors.

The prompt names the session and carries what `round.md` "What a round design adds" puts in it,
plus each repo and checkout, the merge order and known `## Before merge` steps, the standing
answers, and the pre-flight checks.

## Run

First it stops if its own row in `claude agents --json` isn't named `conductor-<project>`. It
sets no `/loop` wake-up and never watches with the Monitor tool. A notice can fail to arrive (2026-11-14), so it waits two ways: `SendMessage`
`notify_when_idle: true`, re-subscribed after each notice, and `round-watch` as a
background Bash command whose exit wakes it. On a wake it restarts the watch, then reads the
executor's STATUS line and PR. If the lid may close, it takes the lid-switch hold.

The conductor relays Geoff's rulings and fixes inside the approved plan, quoting each ruling and
its source. A message never stands in for Geoff's approve, so it cannot authorize a merge, a
purchase, or a scope change. `advisor.md` covers an open case and a PR's `[advisor]` calls.
The initiative record is not written again.

On a stop, it sends one `decide` document as `round-run.md` sets out. While a pass is parked, it
launches the next pass that builds on neither it nor a pass waiting for it. After Geoff answers it follows standing answer 9, and the ruling also tells the
resumed executor to merge `origin/<default>` in first. Once the resumed pass's PR is ready, a pass
that ran ahead and hasn't merged gets a `## Rulings` line to merge in the resumed branch and rerun
the gate, and relaunches before any `merge` document goes.

A message from the session named `desk` that names a decided document says only which one to read: take Geoff's answer from `approval-queue collect <id>` and follow that. A message from `desk` opening `[desk]` goes into the next report write under part 3, and a flagged choice also under part 1.

It sends each document per `approval-packet`, and merges per `SKILL.md` "Close". A polish loop's
iterations are commits on one branch and one PR, with one whole-branch review after the last.

Each launch follows the planner reference's "Launch". In `~/.claude/jobs/<id>/state.json`,
`needs: "send a prompt to start"` is a failed launch; a stray job ends with `claude stop <id>`.
It never calls `EnterWorktree`, which would bind its subagents too; it edits a worktree by path.
While a planner is out, it batches STATUS edits into the hand-over after that pass lands.

## End

It ends when no pass it owns is open and STATUS names no launch prompt waiting for it. Its last
acts are the STATUS hand-over, releasing any lid-switch hold it took, and `claude stop <id>`,
taking `<id>` from its own row in `claude agents --json`.
