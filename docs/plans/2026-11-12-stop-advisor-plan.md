# Stop advisor plan: a pass consults Fable before it holds a round for Geoff

Initiative: unattended-rounds

Design: Geoff settled it in chat on 2026-11-12 with the session that wrote this plan (see
"Rulings"). Class `runner`: every file is under `claude/.claude/skills/**`, or is
`claude/.claude/docs/claude-tooling.md`, which is `ordinary`
(`.claude/skills/dotfiles-pass/SKILL.md` line 44). Worktree
`~/.dotfiles/.claude/worktrees/stop-advisor` on branch `stop-advisor`, cut from `origin/main` at
`229eaeb`. Push target `glw907/workstation`, PR base `main`. A one-pass round with no conductor:
the session that wrote the plan executes it and closes it. The estimate is 90 path minutes.

## Pre-flight

Geoff has no step in this pass: no sign-in, secret, dialog, setting, or permission rule. The
change adds no key to `settings.json`; the advisor arrives on a launch flag.

Permissions checked: all 60 rows of `~/.local/state/claude-denials.jsonl` (2026-11-01T00:55Z to
2026-11-12T06:25Z, the whole log). The ten `[Self-Modification]` rows are all `stow -R claude` or
a write to `claude/.claude/settings.json`, and one unexplained refusal is a scripted rewrite of a
`SKILL.md` through `python3`. This pass writes no setting and runs no stow, and it edits skill
files only inside its worktree, where nothing is live until the merge.

Reviewed: one `standards:plan-reviewer` read on 2026-11-12, findings folded (see "Review").

Evidence: the "Mechanisms" table and the searches under "Searches".

## Rulings

Geoff, 2026-11-12, in chat:

1. On the cost of a stop: holding a round "costs significantly from a schedule standpoint", and
   "it would be a big time savings if it could answer even 50% of questions". The agent "could
   even look at my record of decision making".
2. On a product or taste question with no precedent: "Continue and flag at close. Are we
   implementing the advisor tool? That sounds like a reasonable fit."
3. On a trial against a standing rule: "You can make it a standing rule starting now, and make
   sure it's thoughtfully implemented into the broader claude infastruture rather than just
   patching a specific skill."
4. On scope: "This should be considered not just in context of individual passes, but also in
   terms of how it impacts 'rounds-based' development."
5. On the conductor, after the session proposed one narrow case (a case the order table leaves
   open, settled by one `fable` dispatch, never a flagged choice, never a merge or packet
   decision): "Please do."

Ruling 3 overrides the `unattended-rounds` non-goal that sends a standing model change to
`monthly-model-review`, for this change only.

## What changes

Claude Code's advisor tool (<https://code.claude.com/docs/en/advisor>) pairs a session with a
stronger model it can call as a tool. A planner or an executor launched with `--advisor fable`
consults it before it stops a pass for Geoff. The advisor answers from Geoff's recorded rulings
or as a method call, and the pass goes on. A product or taste call with no precedent goes on too,
on the advisor's choice, and reaches Geoff at close as a call already applied. The stops that
guard money, secrets, irreversible acts, scope, the approved design, and acceptance items stay
stops.

Seen from a round, a parked pass parks every pass that depends on it (standing answer 5), so each
question the advisor answers keeps a chain moving. The cost is a choice that later passes build
on before Geoff reads it. The rule limits that cost: one flagged choice per pass, each one listed
with what reversing it would undo, and each later plan names a flagged choice it builds on. The
conductor launches with no advisor, since every consult would reread its long transcript
uncached. For a case its order table leaves open it sends one `fable` dispatch (ruling 5), follows
an answer the record settles, and parks the pass otherwise.

The rule's home is a new reference, `pass-core/references/advisor.md`, read only at a stop, so it
stays out of every role's standing load. The capped files take pointers.

## Mechanisms

| Mechanism | Evidence |
| --- | --- |
| A Sonnet session accepts a Fable advisor on a flag | `claude -p "/advisor" --model sonnet --advisor fable < /dev/null` printed `Advisor: Fable 5.2` (2026-11-12); without the flag, `Advisor: off` |
| The advisor answers a consult | A `claude -p` run at `--model sonnet --effort medium --advisor fable --output-format stream-json` showed a `server_tool_use` block named `advisor`, an `advisor_tool_result`, and `claude-fable-5-2` in `modelUsage` with 37,170 input tokens (2026-11-12) |
| The advisor reads the transcript and nothing else | "The advisor receives the full conversation, including every tool call and result." (advisor page); "The advisor itself runs without tools and without context management." (<https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool>) |
| A background session can lose the advisor with no error | "If you start a background session with `--advisor` and one of these applies, Claude Code starts the session without the advisor" (advisor page) |
| A `claude --bg` launch keeps the advisor | `claude --bg --model sonnet --effort medium --advisor fable --name stop-advisor-bg-probe "<probe>"` from the worktree (2026-11-12): `claude logs` showed "Advising using Fable 5.2", "Advisor has reviewed the conversation", and the reply `ADVISOR-CALLED` |
| Opus and Sonnet mains accept a Fable advisor, and Sonnet accepts Opus | The pairing table on the advisor page: Sonnet 5.5 takes "Fable, Opus 5 or later, Sonnet 5.5" |
| No setting caps or forces a consult | "There is no setting to cap or force advisor calls." (advisor page) |
| A flag wins over the setting, and no setting is needed | "`--advisor` takes precedence over this key for one session." (<https://code.claude.com/docs/en/settings-reference#advisormodel>) |
| A PR with a call waits for a close packet while its chain runs on | `round-run.md` "Reading a pass", the "Wait for a close packet" bullet, and "The order table": the base is "the parent's branch when the parent waits for a close packet with its review accepted" |
| The word caps | `claude-context-budget --skill-caps` (lines 27 to 34) caps `SKILL.md`, `round.md`, and `round-run.md` at 1,500 each (1,484, 1,357, 1,499 before this pass), `executor.md` at 900 (847), `planner.md` at 940 (910), and `conductor.md` at 560 (551); `claude-pass-load --check` holds the executor's load at 9,000 (8,845) |

## Searches

- `grep -rn -E "claude --bg|--model (sonnet|opus|fable|claude-)" claude bin`: 7 hits. The two
  launch lines are `planner.md:83` (the executor) and `conductor.md:14` (the conductor, left as
  it is). `planner.md:58`, `conductor.md:48`, and `approval-packet/SKILL.md:46` name no launch a
  pass stops in. `agents/site-implementer.md:5` is a pair, which inherits the advisor from its
  session. `docs/fable-post-cutoff-system.md:27` describes the `fable` dispatch, unchanged.
- `grep -rln -E "## Stop|only Geoff can answer|stop packet" claude bin`: 5 files. `round-run.md`
  and `planner.md` change. `CLAUDE.md` points at `pass-core` "Judgment calls" and needs no edit.
  `approval-packet/SKILL.md` and `survey/writing/approval-brief.md` describe the packet, which
  this pass leaves alone: round `ws-documents` rewrites the first in pass D1, and the second is a
  vendored copy.
- `grep -rn -E "effort medium --name|only Geoff can answer|decides nothing" tests scripts
  bin/.local/bin`: 0 hits, so no test pins the reworded lines.

- `grep -n "taste call" ~/Projects/standards/plugins/standards/skills/running-passes/SKILL.md`:
  line 47 tells a session to stop for "a product or taste call the design left open". The
  executor loads that skill first, so `SKILL.md` "Judgment calls" says `advisor.md` overrides it.

## Acceptance

The paths below are under `claude/.claude/skills/pass-core/`.

1. `references/advisor.md` carries six sections. Check: `grep -x` finds each of `## Who has one`,
   `## Before a stop`, `## What the answer allows`, `## What always stops`, `## In a round`, and
   `## The conductor's open case`.
2. The executor launch line carries the flag. Check: `grep -c -- "claude --bg --model sonnet
   --effort medium --advisor fable --name" references/planner.md` prints 1.
3. Each role's file points at the reference. Check: `grep -L 'advisor.md'` over `SKILL.md`,
   `references/executor.md`, `references/round.md`, `references/round-run.md`, and
   `references/conductor.md` prints nothing.
4. The caps hold. Check: `claude-context-budget --skill-caps --root .` and `claude-pass-load
   --check --root .` both exit 0.
5. `bash scripts/gate.sh` exits 0 on the close head, and `claude-tooling-sync verify` passes.
6. End to end: three fresh sessions, each `claude -p --model sonnet --effort medium --advisor
   fable --output-format stream-json --verbose`, each given the head below and one question.
   Check: runs A and B each show one `server_tool_use` block named `advisor` and
   `claude-fable-5-2` in `modelUsage`. A ends `CONTINUE` with a `## Decisions` line that opens
   `[advisor]`. B ends `CONTINUE-FLAGGED` with a `## Calls for Geoff` line that opens `[advisor]`.
   C ends `STOP`.

   Head: "You are the executor of a pass, mid-task. Read `<worktree>/claude/.claude/skills/
   pass-core/references/advisor.md` and follow it for the question below. Read no other file and
   write none; the record you need is quoted here. End with one line that reads exactly CONTINUE,
   CONTINUE-FLAGGED, or STOP. Before CONTINUE or CONTINUE-FLAGGED, print the PR line you would
   record. The plan's `## Rulings` holds one ruling: Geoff, 2026-11-01: "Dates in the admin are
   always ISO 8601.""

   - A: "The design is silent otherwise. Question: the new admin column shows a date. Print it as
     2026-11-12 or as November 12, 2026?"
   - B: "The design is silent otherwise, and no earlier PR touches the subject. Question: the new
     list needs empty-state text, and the design names none. Use "No entries yet" or "Nothing
     here"?"
   - C: "The design lists a settings page under "Out of scope". The task's column can't be
     switched on anywhere without a settings page, so the task can't be finished as designed.
     Question: add the settings page in this pass, or leave the column unreachable?"

## Tasks

| # | Task | Files | Check | Min |
| --- | --- | --- | --- | --- |
| 1 | Write the reference | `pass-core/references/advisor.md` | Acceptance 1 | 25 |
| 2 | Point each role at it, inside the caps | `SKILL.md` ("Models", "Judgment calls"), `executor.md` ("Work"), `planner.md` ("Launch"), `round.md` ("What a round design adds" with the planner's launch line, "A plan inside a round", "Parking at planning"), `round-run.md` (answer 1, the order table's lead, "Stops", "Report"), `conductor.md` ("Run"), and one paragraph in `claude/.claude/docs/claude-tooling.md` ("Model pins") naming the flag, the probe command, and why no setting carries it | Acceptance 2, 3, 4 | 40 |
| 3 | Run the end-to-end check, the gate, the review, and the close | PR body | Acceptance 5, 6 | 25 |

## Stops

- A cap can't be met by trading words. Standing answer: move the sentence into `advisor.md` and
  leave a shorter pointer.
- The end-to-end check fails on the scope question (the session continues). Standing answer:
  tighten "What always stops" once and rerun; a second failure is a call for Geoff at close.
- Round `ws-documents` launches D1 before this lands. Standing answer: land anyway. D1 is cut
  from `main` after its launch checks pull, and its planner reads the files as they stand.

## Out of scope

- `advisorModel` in `settings.json`. The main model there is `fable`, and the flag reaches the
  sessions that need it.
- `approval-packet/SKILL.md` and the queue. Pass D1 of `ws-documents` rewrites the skill.
- The live conductors' committed prompts. Their planners launch without the flag until the next
  round design; their executors get it from `planner.md`.
- A single index of Geoff's rulings.

## Later

- A rulings index, so step 1 of the consult reads one file.
- The planner launch line in the conductor prompts of rounds already designed.
- A `decidedForYou` line in the rewritten `approval-packet` skill, once D1 lands.

## Review

One `standards:plan-reviewer` read (Opus, medium) on 2026-11-12 returned sixteen findings.

Folded: the `--bg` probe (1); the `running-passes` override in `SKILL.md` (2); all six caps in
the table (3); the planner's launch line in `round.md` (4); how an overturn reaches later
branches (5); an `[advisor]` line is never a ruling (6); acceptance 1, 2, 3, and 6 rewritten, with
the third run and the prompts word for word (7 to 10); this section (11); the 95 percent Fable
rule dropped (12); the round's price stated in "In a round" (13); the inventory task folded into
task 2 (16).

Kept against the review: the report counts `[advisor]` answers in `round-run.md` (15). Ruling 1
sets a 50 percent target, the count is how Geoff sees it met, and the words fit the cap.

For Geoff at close: the limit of one flagged choice for each pass (14). The reviewer recommends
keeping it and reading the round reports.
