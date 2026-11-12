# Conductor

Read after `pass-core` `SKILL.md`. A round of two or more passes has a conductor. That
rule replaces the 2026-10-12 ruling that every `runner` or `auth-data` pass gets one. The
conductor is named `conductor-<project>`, after the repo whose main checkout launches the
executor, and owns every PR its passes open.

## Hand-off

The planner commits `<plan>-conductor-prompt.txt` and checks `claude agents --json` for a live
`conductor-<project>`:

1. If none is listed, the planner launches it from that main checkout with the exact line
   `claude --bg --model sonnet --effort medium --name conductor-<project> "$(cat <file>)"` and
   closes.
2. If one is listed, the planner sends it the prompt file's absolute path with `SendMessage`, waits
   for its one-line reply naming the pass, and closes. A send that fails because the conductor just
   ended falls back to step 1.
3. If the message is held or refused, or no reply comes within 10 minutes, the planner stays open,
   writes the stall into STATUS, and runs `notify-send -u normal`. It never launches the executor
   itself.

The prompt names the session, then carries the executor's `claude` line and prompt file, the
plan path, each repo and checkout, the merge order and known `## Before merge` steps, the standing
answers, the pre-flight checks, and the packet's contents.

## Run

Its first step checks its own row in `claude agents --json` and stops if the name is not
`conductor-<project>`, since its executor trusts that name alone. It sets no `/loop` wake-up and
never watches with the Monitor tool. It waits on each executor with `SendMessage`
`notify_when_idle: true`, which is one-shot, so it re-subscribes after each notice, and reads the
executor's STATUS line and PR. If the lid may close, it takes the lid-switch hold.

An executor takes its conductor's messages as instructions (Geoff, 2026-10-20). The conductor
relays Geoff's rulings and fixes inside the approved plan, quoting each ruling and its source. A
message never stands in for a packet's approval, so it cannot authorize a merge, a purchase, or a
scope change. On a stop, the conductor sends one `stop` packet as `round-run.md` sets out, and
launches the next pass that doesn't wait for the parked one. After Geoff answers, it follows
standing answer 9 there. The initiative record is not written again.

At each decision point it sends one packet for the PRs and designs it holds, per
`approval-packet`, and merges per `SKILL.md` "Close" after Geoff approves. A polish loop's
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
