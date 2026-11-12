# Round

Read after `pass-core` `SKILL.md` and `references/planner.md`, to design a round or to plan one of
its passes. A conductor and an executor read `references/round-run.md` in its place.

A round is one approved design that covers one to six passes in one repo. Its passes run one at a
time while Geoff is away, and rounds run one at a time unless a design says otherwise. A pass stays
what `standards:running-passes` defines: one plan, one executor, one worktree, and one PR. Geoff
approves the design once, and that approval also approves unattended planning for every pass in
it. The design and planner seats take the models `SKILL.md` "Models" names.

## What a round design adds

A round design of two or more passes carries these on top of what `planner.md` "Design" asks:

- **A round id.** Lowercase letters, digits, and hyphens, starting with a letter, 12 characters at
  most, as in `site-forms`. The queue refuses any other form. Every PR body, packet fact file, and
  landing of the round carries it.
- **A pass table.** Each row names a pass with its outcome, acceptance list, files, class, path
  minutes, the passes it depends on, and the passes it shares a file with.
- **The shared assumptions.** Each assumption that more than one pass depends on, with a probe run
  and its output, or a quoted source.
- **The merge order.**
- **The usage ceiling.** 85 percent of the weekly allowance, unless Geoff set another.
- **The standing answers.** The twelve in `round-run.md` hold in every round. The design adds one
  for each further stop it can foresee and says so where it replaces one of the twelve.

Two rules set the order. A pass that shares a file with an unmerged pass counts as depending on
it, because a pass cut from the default branch would conflict at merge. Where the dependencies
allow, the pass that rests on the least-proven assumption runs first, so a wrong assumption costs
one pass and never the round. The longest chain of passes holds about 600 planned path minutes at
most.

The designing session commits a planner prompt for each pass and one conductor prompt. The
conductor prompt holds the order table: each pass, its planner prompt, what it depends on, its
planned minutes, and a mark on any pass whose PR waits for Geoff whatever its review says. The
conductor decides nothing, so a case the table leaves open parks a pass. Each pass is planned just
before it runs, and its plan reads the code as the earlier passes left it.

## Design rules

A wrong design costs more in a round than in one pass, since later passes build on it before Geoff
reads anything. A round design of two or more passes follows four rules.

1. Each pass carries an acceptance list: what Geoff would see or run when the pass is done, each
   item able to fail. The designing session plays every list back to him at the sitting, with a
   mockup for anything he will look at. His approval fixes the lists. A planner or an executor may
   add a check and never edits or drops an item.
2. The design lists each shared assumption with its probe or quoted source, as above. An
   assumption with neither is an open reading, and the design isn't ready for the packet.
3. One fresh reader checks the design before it reaches Geoff, whatever its class: the
   `standards:brainstorming` builder check, run by one Opus reader with no context. It asks whether
   a builder could plan every pass from the design, and whether any acceptance item could pass on
   a wrong result.
4. Each PR shows evidence for every acceptance item: the command and its output, or a screenshot.
   The closing reviewer checks each item against that evidence. An item that can't be met as
   written parks the pass.

A one-pass round is today's pass, with no conductor, no order table, and no round id. Geoff ruled
on 2026-11-11 what it takes from the four rules: "The acceptance list and its evidence in the PR".
Its design carries rule 1's list, its PR carries rule 4's evidence, and rules 2 and 3 don't apply.

## Planner rules

These four apply to every plan, in a round of any size. Each leaves something the plan reviewer
can check, and each answers one of the largest classes of planning miss.

1. The plan carries a mechanism table. Each row names a probe you ran with its output, or a quoted
   source with its line or URL. No row says "expected" or cites nothing.
2. The file list comes from searches. The plan records each search with its hit count, and lists
   or dismisses every hit with a reason.
3. `Permissions checked:` cites your read of the last 30 days of
   `~/.local/state/claude-denials.jsonl` against each task's commands. It names the log's date
   range and each class found, and the plan names an alternative for each command the log shows
   refused.
4. Every stop the plan writes has a standing answer or parks the pass. No stop says "ask Geoff".

The `Evidence:` line of `## Pre-flight` names the mechanism table and the recorded searches.

## A plan inside a round

A round's planner starts at `SKILL.md` "Lifecycle" step 4, since the round design's section for
the pass is the approved design.

- Work in the pass's worktree by path. The conductor cut it, and `EnterWorktree` belongs to the
  executor.
- Verify each change site against the code as the earlier passes left it. The design's line
  numbers have moved.
- Open the plan with an `Initiative:` line, a `Round:` line, and a `Pass:` line.
- Copy every acceptance item verbatim under `## Acceptance`, each mapped to the task that meets it
  and the command or screenshot that will show it.
- Get one `standards:plan-reviewer` read, whatever the class, and fold its findings.
- Name the default branch as the PR's base, even when the worktree was cut from a parent's branch.
  The queue refuses to merge a PR based anywhere else.

Then commit the plan and the executor prompt on the pass's branch, push, run the launch checks in
`planner.md` "Launch", and launch the executor.

## Miss tags

Each line under a PR's `## Planning misses` opens with one tag, so `pass-report` can count misses
by class with no sorting. A plan's own miss lines use the same ten.

| Tag | The miss |
| --- | --- |
| `[mechanism]` | A mechanism was assumed and never probed. |
| `[file-list]` | The file or consumer list was incomplete. |
| `[permission]` | A permission, auto-mode, or isolation block wasn't foreseen. |
| `[design-gap]` | The design or plan lacked a part or missed prior art. |
| `[stale-fact]` | A fact the design or plan stated was no longer true. |
| `[owner-call]` | A decision that was Geoff's was left open. |
| `[no-answer]` | A stop had no standing answer. |
| `[conflict]` | Two rules, or two passes' changes, collided. |
| `[estimate]` | The estimate missed the work by more than double. |
| `[ambiguous]` | An instruction could be read two ways. |

## Parking at planning

Park the pass before any code is written when one of these holds:

- The plan's path comes out over twice the design's estimate for the pass.
- The plan review finds something that changes the approved design.
- An acceptance item can't be planned for as written.

To park, commit the plan on the pass's branch, push it, and open a draft PR against the default
branch that holds the plan alone. Put the stop in the PR's body: the question, what you tried, and
the choices you see. Then end. The draft PR matters because the queue refuses a `stop` packet that
names no PR. Never ask Geoff in chat and never run `notify-send`: the conductor sends the packet.
In a one-pass round the planner sends the `stop` packet itself, through `approval-packet`.
