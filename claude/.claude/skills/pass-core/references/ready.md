# Ready

Read after `references/round.md`, before a design goes to Geoff.

## Ready to run

A round is ready to run when its design reaches Geoff: his approve starts it, or the packet's first
paragraph says what else it waits for (Geoff, 2026-11-14). A round puts the planning up front so
its passes run without a break, so the designing session clears the ground on the day it sends the
packet. This holds for a round of any size.

1. **The start line.** The design names what must be true for the first planner to launch. Each
   part is a state a command reads: a line in the repo's `docs/STATUS.md`, an answered document, a
   row in `claude agents --json`. A merged PR is never that state, since a pass can merge every PR
   before its closing steps are done. The line places the round against every other round approved
   or running in the repo.
2. **The launch checks, run early.** The designing session runs the checks that come before the
   first launch (`round-run.md` "The order table" and the checks in the conductor prompt, or
   `planner.md` "Launch" in a one-pass round) and records each command and its output under the
   start line. It fixes a failed check before the packet goes. When a check waits for something
   outside the session, the packet's first paragraph says the round won't start on approve, what it
   waits for, and who ends that wait. The repo's STATUS then names the conductor prompt as the next
   launch, and the session that ends the wait hands the round over (`conductor.md` "Hand-off").
3. **Prompts point at a skill.** A launch prompt names a tool's command by the skill section that
   owns it, as in "land as `approval-packet` step 1 says". It never copies a subcommand, a flag, or
   a `--help` list. A command line a prompt has to carry, such as a `claude --bg` launch, is run or
   probed with `--help` that day, and the design records the probe.
4. **No side work in the round's way.** Work the design turns up that isn't the round's is placed
   before the packet goes. A fix a pass needs is a task in that pass or a row in the order table,
   and anything else is a backlog item. Nothing runs between Geoff's approve and the first launch
   but the hand-off.

## A retired form

A pass that removes or renames a command, a subcommand, a flag, or a document kind also searches
for the old form in `~/.dotfiles/claude`, in each repo's `.claude/` and `skills/` under
`~/Projects`, and in the prompts in `~/Projects/initiatives`. The plan lists every hit, and the
pass doesn't land while one is open.

## A due full sweep

A full sweep that is due never rides a design. It runs as a separate session, reaches Geoff as a
separate document, and holds no packet and no launch (Geoff, 2026-11-14). This overrides
`standards:backlog-sweep`.
