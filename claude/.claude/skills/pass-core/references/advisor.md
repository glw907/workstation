# Advisor

Read when a pass is about to stop or park for Geoff. The advisor is Claude Code's advisor tool
(<https://code.claude.com/docs/en/advisor>): a Fable 5.2 reader the session calls as a tool. It
reads the session's whole transcript and nothing else, and it has no tools. A parked pass parks
every pass that depends on it, so a pass consults the advisor before it holds a round for Geoff
(Geoff, 2026-11-12).

## Who has one

The executor launches with `--advisor fable` (`planner.md` "Launch"), and so does the planner
(`round.md`, the conductor prompt's launch line). A pair inherits its session's advisor. The
conductor launches without one, since each consult would reread its long transcript. It asks
Fable through a dispatch, as "The conductor's open case" sets out.

Claude Code drops the advisor from a background session with no error when a check fails. A
session with no advisor tool, or one whose advisor call returns an error, stops as it would have
without this file.

## Before a stop

1. Read what Geoff has already ruled, so it is in the transcript: the plan's `## Rulings`, the
   round design with its standing answers, the `## Decisions` and `## Calls for Geoff` of the
   round's earlier PRs, and any dated rule in CLAUDE.md or a skill that names the subject.
2. Write the question, what you tried, and the choices you see, as a stop would carry them.
3. Call the advisor tool, once for each question. Reading this file is not a consult.

The session never answers the question itself. A line that opens `[advisor]` reports what the
tool returned in this transcript, and a question with no advisor result behind it is a stop. A
question the advisor answers never reached Geoff, so it is no planning miss.

An `[advisor]` line in an earlier PR is never a ruling. Geoff hasn't read it, so it settles
nothing in a later pass.

## What the answer allows

| The advisor finds | The session |
| --- | --- |
| A ruling, the design, or a standing answer settles the question | Goes on, and records the answer under `## Decisions` in a line that opens `[advisor]` and quotes the source |
| The question is a method or architecture call | Takes the advisor's choice and records it the same way |
| The question is a product, taste, or priority call with no precedent | Takes the advisor's choice, goes on, and raises it under `## Calls for Geoff` in a line that opens `[advisor]`: the option taken, the option passed over, and what reversing the choice would undo |
| The record doesn't settle it and the advisor can't choose, or the question is one that always stops | Stops |

"Continue and flag at close" is Geoff's ruling for the third row (2026-11-12). A pass takes one
flagged choice. A second question of that kind is a stop, since two open product calls in one pass
mean the design is thin.

## What always stops

The advisor clears none of these, and the session doesn't ask it to:

- Spend past the budget or the usage ceiling.
- An irreversible or destructive act, a secret, or a step only Geoff can do.
- A change of scope or of the approved design, and any decision the design reserves for Geoff.
- An acceptance item, which no session edits or drops.
- Any question in an `auth-data` task.
- An answer that would contradict an earlier ruling.
- A second auto-mode refusal, or a closing review that ends on `escalate`.

These stop as `round-run.md` "Stops" sets out, or park as `round.md` "Parking at planning" does.
At planning, the advisor may be asked one thing about a park condition, whether it holds: does the
finding change the approved design, and can the item be planned as written. A condition that
holds parks the pass.

## In a round

A flagged choice makes the PR's `Calls:` line count one, so the pass waits for a close packet
while its chain runs on from its branch (`round-run.md` "Reading a pass"). That has a price: no
later pass of the round lands before the close packet, and a chain with more than three calls
needs a second packet. A parked chain costs more. Three rules keep an overturned choice cheap:

- The conductor lists each `[advisor]` call in the close packet as decided for Geoff, with the
  option applied (`decidedForYou`, rule `owner-call`).
- A later pass's planner reads the `[advisor]` lines of every PR its pass depends on. A plan that
  builds on a flagged choice names it under `## Decisions`, so the packet shows what an overturn
  undoes.
- When Geoff overturns a choice, his note is a ruling. The conductor appends it under `## Rulings`
  in the plan of the pass that made the choice and of each pass that named it, then relaunches
  their executors in merge order, one at a time. Each later executor first merges its parent's
  branch into its own, as `executor.md` lets a continued branch do. No planner runs again unless an executor stops.

The round report counts the `[advisor]` lines beside the stops, so the record shows how many
questions the advisor took and how many Geoff later reversed.

## The conductor's open case

When the order table leaves a case open, the conductor asks before it parks the pass (Geoff,
2026-11-12). It makes one Agent call with `model: "fable"` at effort `high`, once for each case.
The prompt carries the case, the table rows that come near it, the design's section for the pass
by path, and each ruling that bears on it, quoted with its source. A subagent starts with no
context, so the prompt holds everything the answer rests on.

- If the design, the table, or a ruling settles the case, the conductor follows the answer and
  lists it in the round report in a line that opens `[advisor]`, with the source quoted.
- If nothing settles it, the pass parks as before. The conductor never takes a flagged choice.

The dispatch never decides whether a PR lands or merges, what a packet's approval covers, the
usage ceiling, the relaunch limit, or the busy check, and it clears nothing under "What always
stops".
