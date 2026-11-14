---
kind: design
approve: I make the rule changes in one workstation pass today. It merges with no further step from you, once its gate is green and a review agent accepts it.
sendback: Nothing changes. I revise the design from your notes.
---

# Make a round ready to run before its design reaches you?

The terminal design round for `cairn` lost most of a day between its design and its first line of code, for three reasons. It was approved while it still waited on other work, its launch prompts named queue commands that had been retired, and its start carried a backlog cleanup that wasn't part of the round. This design adds one section to the round rules, called "Ready to run", and makes three smaller edits beside it. It is one pass in the workstation repo, about 45 path minutes, and the pass asks nothing of you after this page. One question needs your answer, and it sets the wording of one rule.

**Should a design reach you while its round still waits on other work?** Last night the round waited on the close of the setup tooling pass, and the design never said so. Under the new rule, the designing session runs the round's launch checks before it sends the design, and fixes what it can. Some waits it can't end, such as your answer on another document. Your choice here decides what the rule says for those.

:::question A design whose round can't start yet
- **Send it, and say so first.** The rule goes in as written below. The opening paragraph says the round won't start on your approve, what it waits for, and who ends the wait. You can read the design while the other work finishes. {recommended}
- **Hold it** until the round can start. I change the second rule below to say the design isn't sent while a launch check fails. Your approve then always starts the work, but your read waits, and a held design goes stale. The terminal round's design was held for a day and had to be checked against the code a second time.
:::

:::decide

## What went wrong, and the rule that answers each

| What happened | The gap in the rules | The new rule |
| --- | --- | --- |
| The design said the round starts "after pass 3 merges". Every pull request of pass 3 had merged, but the pass hadn't closed. Nobody had placed the round against the theme round either, so that order came to you as a late question. | A design names no start condition, and nobody runs the launch checks until after you approve. | The design names its start condition as a state a command can read, and the designing session runs the launch checks before it sends. |
| The start prompt and the conductor prompt named `approval-queue snapshot`, `packet`, and `land --round`. The queue had retired all three that day. | Nothing stops a prompt from copying a command, and a pass that retires a command searches only the repo it works in. | A prompt points at the skill that owns a command. A pass that retires a command searches every skill and prompt for it. |
| The start ran a sweep of all 137 backlog items, and two side fixes, before the design reached you. | The planning rules tell every design to run the full backlog sweep when one is due. | A due full sweep runs as a separate session. A fix the round needs is a task in one of its passes. |

The rules weren't broken in any of the three. Each time the rules had nothing to say, so a new rule closes each gap.

One wait was real and stays real. The setup tooling pass had to close before the terminal round could start, and that close took until this morning. The new rule wouldn't have shortened it. It would have put that wait in the first paragraph you read.

## The words that change

<details>
<summary>A new section in <code>round.md</code>, the rules for designing a round</summary>

> **Ready to run**
>
> A round is ready to run when its design reaches Geoff: his approve starts it, or the packet's first paragraph says what else it waits for (Geoff, 2026-11-14). A round puts the planning up front so its passes run without a break, so the designing session clears the ground on the day it sends the packet. This holds for a round of any size.
>
> 1. **The start line.** The design names what must be true for the first planner to launch. Each part is a state a command reads: a line in the repo's `docs/STATUS.md`, an answered document, a row in `claude agents --json`. A merged PR is never that state, since a pass can merge every PR before its closing steps are done. The line places the round against every other round approved or running in the repo.
> 2. **The launch checks, run early.** The designing session runs the checks that come before the first launch (`round-run.md` "The order table" and the checks in the conductor prompt, or `planner.md` "Launch" in a one-pass round) and records each command and its output under the start line. It fixes a failed check before the packet goes. When a check waits for something outside the session, the packet's first paragraph says the round won't start on approve, what it waits for, and who ends that wait. The repo's STATUS then names the conductor prompt as the next launch, and the session that ends the wait hands the round over (`conductor.md` "Hand-off").
> 3. **Prompts point at a skill.** A launch prompt names a tool's command by the skill section that owns it, as in "land as `approval-packet` step 1 says". It never copies a subcommand, a flag, or a `--help` list. A command line a prompt has to carry, such as a `claude --bg` launch, is run or probed with `--help` that day, and the design records the probe.
> 4. **No side work in the round's way.** Work the design turns up that isn't the round's is placed before the packet goes. A fix a pass needs is a task in that pass or a row in the order table, and anything else is a backlog item. Nothing runs between Geoff's approve and the first launch but the hand-off.

</details>

<details>
<summary>Three smaller edits</summary>

In `round.md`, the fresh reader who checks a design before you see it gets a third question: could the round launch the moment you approve?

In `round.md`, the rule that a plan's file list comes from searches gains this:

> A pass that removes or renames a command, a subcommand, a flag, or a document kind also searches for the old form in `~/.dotfiles/claude`, in each repo's `.claude/` and `skills/` under `~/Projects`, and in the prompts in `~/Projects/initiatives`. The plan lists every hit, and the pass doesn't land while one is open.

In `planner.md`, "Every design runs the scoped sweep, and its full sweep when one is due" becomes:

> Every design runs the `standards:backlog-sweep` scoped sweep. A full sweep that is due never rides a design. It runs as a separate session, reaches Geoff as a separate document, and holds no packet and no launch (Geoff, 2026-11-14). This overrides `standards:backlog-sweep`.

</details>

The last edit changes your rulings of 2026-10-25 and 2026-10-27, which put the full sweep inside the design. Approving this design approves that change too. If you want the sweep to stay in the design, send this back with a note.

## How the pass is checked

The pass is done when each of these holds:

- A fresh reader gets the changed rules and the terminal round's design and prompts as they stood on 2026-11-13, and nothing else. Asked what must change before the design is sent, it names all three faults: the start condition that is a merge, the copied queue commands, and the full sweep in the start. The reader's answer goes in the pull request.
- The same reader, given this design, finds the start line and the launch checks.
- `bash scripts/gate.sh` and `claude-tooling-sync verify` pass in the workstation repo.
- The launch guard is unchanged, so no prompt that launches today is refused.

## When this pass can start

It can start on your approve. I ran the launch checks at 09:50 on 2026-11-14:

| Check | Result |
| --- | --- |
| The workstation checkout is level with GitHub | 0 commits behind |
| Another pull request edits the same files | None of the three open ones does |
| Weekly usage | 4 percent |
| A session is live in the checkout | One, so this pass works in a separate worktree |

That live session finished the runbook work and is waiting for you to run a block of commands, which is a separate matter from this pass. It doesn't hold this pass, but it does hold the last step. After this pass merges on GitHub, the new rules reach other sessions only when the workstation's main folder pulls the merge, and a folder with a live session in it isn't pulled. If that session is still there when the pass merges, I'll tell you the rules are merged and not yet in effect, and pull the folder once it has gone.

## What I decided

- The rules get no hook. A hook could check that a start line is present and couldn't check that it is true. The fresh reader's third question checks the substance.
- The rule on copied commands goes in the round rules, where prompts are written. The search rule goes beside the other rules for writing a plan, where a pass that retires a command is planned.
- The `standards` plugin still says the full sweep runs beside the design. The pass files a backlog item there, and the workstation rule wins until it is fixed.
- The practice behind this is Anthropic's guidance to put a rule where the session that needs it reads it (<https://code.claude.com/docs/en/features-overview>).

## What is left out

- The design packet that sat unseen for you last night had a different cause, a queue rewrite that dropped a side effect. That is fixed, and the rule to prevent it is workstation backlog item 90.
- The terminal round itself isn't touched. Its first pass is in review now, and its three later passes run under the rules it started with.
- The round log has fifteen more entries, each with a proposed fix. They wait for the monthly prune.
