# Conductor

Read after `pass-core` `SKILL.md`. A round of two or more passes has a conductor. This replaces
the 2026-10-12 ruling of one per `runner` or `auth-data` pass. The conductor is named
`conductor-<project>`, after the repo whose main checkout launches the executor, and owns every PR
its passes open.

## Hand-off

The session that acts on Geoff's approve of the round's design launches the conductor from the
main checkout with
`claude --bg --model sonnet --effort medium --name conductor-<project> "$(cat <file>)"` when
`claude agents --json` lists none. Otherwise it sends the live one the prompt's absolute path with
`SendMessage` and waits for its one-line reply, launching instead if the conductor just ended. A
held or refused message, or no reply within 10 minutes, starts nothing: the session writes the
stall into the repo's `docs/STATUS.md`, never the report file, which would read as a resume.

The conductor launches each pass's planner (`round-run.md` "The order table"), and the planner
launches its executor. A failed executor launch parks the pass as `round.md` "Parking at
planning" says, with the failure as the stop. The conductor never launches an executor.

The prompt names the session and carries what `round.md` "What a round design adds" puts in it,
plus each repo and checkout, the merge order and known `## Before merge` steps, the standing
answers, and the pre-flight checks.

## Run

Its first step checks its own row in `claude agents --json` and stops if the name is not
`conductor-<project>`, since its executor trusts that name alone. It sets no `/loop` wake-up and
never watches with the Monitor tool. It waits on each executor with `SendMessage`
`notify_when_idle: true`, which is one-shot, so it re-subscribes after each notice, and reads the
executor's STATUS line and PR. If the lid may close, it takes the lid-switch hold.

An executor takes its conductor's messages as instructions (Geoff, 2026-10-20). The conductor
relays Geoff's rulings and fixes inside the approved plan, quoting each ruling and its source. A
message never stands in for Geoff's approve in the queue, so it cannot authorize a merge, a
purchase, or a scope change. On a stop, it sends one `decide` document as `round-run.md` sets
out, and launches the next pass that doesn't wait for the parked one. After Geoff answers, it
follows standing answer 9 there. `advisor.md` covers an open case and a PR's `[advisor]` calls.
The initiative record is not written again.

It sends each document per `approval-packet`, and merges per `SKILL.md` "Close". A polish loop's
iterations are commits on one branch and one PR, with one whole-branch review after the last.

Before it launches the next committed prompt, `claude-worktree-busy <path>` must exit 0; a
non-zero exit ends launches in that repo. It also runs the planner reference's launch checks. After
`claude --bg` it reads `~/.claude/jobs/<id>/state.json`: `needs: "send a prompt to start"` is a
failed launch, and a stray job ends with `claude stop <id>`. It never calls `EnterWorktree`,
which would bind its subagents too; it edits a worktree by path. While a planner is out, it
batches STATUS edits into the hand-over after that pass lands.

## End

It ends when no pass it owns is open and STATUS names no launch prompt waiting for it. Its last
acts are the STATUS hand-over, releasing any lid-switch hold it took, and `claude stop <id>`,
taking `<id>` from its own row in `claude agents --json`.
