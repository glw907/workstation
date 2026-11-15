# A round goes on past an open question, and Geoff rules at the close

Geoff said on 2026-11-14 that the round process "seems delicate, brittle, and prone to stopping",
read this design in chat, and said "Draft the design and execute directly". He then asked for it
to apply to the rounds already running. It is one pass in the workstation repo, class `runner`.

A round stops today whenever a session meets a question the rules didn't foresee. Each earlier fix
added a rule for the last stop, and the next stop was a different one. This design changes the
default. A session that meets an open question takes the advisor's choice, goes on, and lists the
choice for Geoff at the close. A short fixed list still stops a run. Two smaller changes go with
it: the conductor gets a watcher that wakes it when a pass changes state, and a design runs each
acceptance check once before Geoff reads it.

## What it costs

Geoff rules on flagged choices at the close of a round, where today he rules mid-run. A choice he
overturns means rework in the pass that made it and in each later pass that built on it. A pass
with a flagged choice also waits for the close packet, so a round with one early flag lands
nothing until its end.

## What went wrong in the terminal design round

| What happened | The gap in the rules | The new rule |
| --- | --- | --- |
| Pass 2 parked at planning on two acceptance items. One compared two runs byte for byte while the output held a clock line. The other forbade a colour byte the design's tier rule requires. The advisor had an answer to both. | An acceptance item is frozen, and an unmeetable one parks the pass. The advisor may only be asked whether the park condition holds. | The item's outcome is fixed and its check can be amended through the advisor. The amendment is a flagged choice. |
| Nobody had run either check before Geoff approved the lists. | The fresh reader asks whether an item could pass on a wrong result, never whether it can be met. | The designing session runs each check on the code as it stands and records the output. The fresh reader asks whether each item can be met. |
| The conductor sat about four hours at pass 1's close after an idle notice never arrived. | The conductor waits on a one-shot notice and may set no wake-up. | The conductor also waits on `round-watch`, a background command that exits when a pass changes state while none of its sessions is working. |

## What still stops a run

1. Spend past the path ceiling or the weekly usage ceiling.
2. An irreversible or destructive act.
3. A secret, or a step only Geoff can do.
4. Any question in an `auth-data` task.
5. Work beyond the approved scope: more outcomes, another repo, or a file class the design
   excludes.

Everything else goes through the advisor and on. That includes a second product or taste call in
one pass, an acceptance check that can't be met as written, a false shared assumption, a design
detail the code contradicts, and a closing review that ends short of `accept`. Each is listed
under `## Calls for Geoff` with the option taken, the option passed over, and what reversing it
would undo.

A second auto-mode refusal leaves the task undone and flagged. The session goes on with the tasks
that don't need it, and stops only when none is left.

A pass whose review ends short of `accept` still becomes ready, with the verdict on its PR. The
passes after it cut from its branch and name that verdict, so one doubtful review holds nothing
behind it. The close packet goes once the last pass to run has ended.

The machine limits stay as they are: the clock, the usage ceiling, and a session that dies twice
end launches without asking anything.

## The files that change

- `pass-core` `references/advisor.md`: the answer table, the fixed list, a section on acceptance
  items, and the fallback when a session has no advisor tool (one Fable dispatch).
- `references/round.md`: design rules 1, 3, and 4, the count of fresh-reader questions, and
  "Parking at planning".
- `references/round-run.md`: standing answers 1, 2, 8, and 12, "Reading a pass", and "Stops".
- `references/conductor.md`: the watcher in "Run".
- `references/planner.md`, `SKILL.md`, and the global `CLAUDE.md`: the sentences that restate the
  old default.
- `docs/unattended-work-guards.md`: the sentence that says a waiting session arms nothing.
- `bin/.local/bin/round-watch` with its test.

## The watcher

No Claude Code command lets an outside script send a message to a live session (`claude --help`,
2026-11-14), so a systemd timer can't wake a conductor. A background Bash command can: the harness
re-invokes a session when one exits. `round-watch <session-prefix> <owner/repo> <branch-prefix>`
records the round's sessions and open PRs when it starts, polls every two minutes, and exits with
the changed lines once something differs and no session of the round is working. One real change
gives one wake-up, so a long wait for Geoff costs nothing. It has no check for a session that
hangs while working, since the executor's wake-up already covers that.

On a wake the conductor restarts the watch before it reads the pass. A change that lands during
the read then differs from the new first reading and wakes it again. A read that fails at the
start records nothing, so the first good read becomes the baseline. Each pass slug opens with the
round id, which keeps one round's watch from seeing another's sessions.

## Running rounds

The new rules reach a session launched after the workstation checkout pulls the merge. A session
already running holds the old text, and a round design's standing answers win over `round-run.md`.
So each conductor gets one message that quotes Geoff's instruction, names the changed sections,
and asks it to pass them to its live planner or executor. It starts `round-watch` at its next
wait. A conductor that isn't running gets the same text in its launch prompt.

## How the pass is checked

- A fresh reader gets the changed rules and pass 2's two parked questions as the planner wrote
  them, and nothing else. Asked what the planner does, it answers that the planner consults the
  advisor, amends the check, flags it, and launches the executor.
- `round-watch` exits on a recorded change with no session working, stays up while one works, and
  survives a failed `gh` call. Its test shows each.
- `bash scripts/gate.sh` and `claude-tooling-sync verify` pass.

## What I decided

- The watcher is a background command the conductor starts, and no timer, for the reason above.
- The rules get no hook. Whether a question is on the fixed list is a judgment a hook can't make.
- The practice is Anthropic's: "Make routine judgment calls yourself, and check in only when
  different readings of the request would lead to materially different work"
  (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>),
  with the advisor as the second reader (<https://code.claude.com/docs/en/advisor>).

## The test of this design

The next round reaches Geoff mid-run only for the five stops. If it still stalls on something
else, the fallback is rounds of two passes.
