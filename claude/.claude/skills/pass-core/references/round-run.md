# Round run

Read after `SKILL.md` and your role's reference. The round design and the conductor prompt's
order table win over this file.

An executor under a conductor enters the pass's worktree with `EnterWorktree` and its `path`,
once, and merges nothing: the branch holds the plan. In a one-pass round the executor sends its
question itself as a `decide` document in place of ending, and its PR carries no `Round:` line.

## Standing answers

1. A pass stops on a question `advisor.md` leaves for Geoff. The executor follows "Stops". The
   conductor waits for the PR's checks, sends one `decide` document, ends the pass's sessions, and
   launches the next pass that doesn't depend on it.
2. Auto mode refuses a command. The session uses the alternative its plan names, once. A second
   refusal is a stop. No session edits a setting to get past one.
3. A task needs a setting, hook, auto-mode entry, or permission rule changed. That is never an
   executor task. The planner writes it as a command for Geoff in a close packet, and a pass that
   can't finish without it parks.
4. The weekly usage reads 85 percent or more before a launch, or the figure can't be read. The
   conductor finishes the pass in flight, starts nothing new, writes the report, and waits for the
   reset.
5. A pass's parent is parked. The pass parks too and never launches.
6. The busy check exits 1. Launches end in that repo, and the report says so.
7. The round passes twice its planned minutes ("Clock"). The pass in flight finishes, nothing new
   starts, and the conductor writes the report.
8. A plan can't go ahead as designed. The planner parks the pass before any code is written, as
   `round.md` says.
9. Geoff answers a `decide` document while the round runs. The conductor appends his ruling under
   `## Rulings` in the pass's plan, commits and pushes it, and relaunches the pass once the one in
   flight finishes. The PR takes the question under `## Planning misses` and the ruling
   under `## Decisions`. Passes that depended on it follow in order.
10. The conductor's session dies or the machine restarts. STATUS names the conductor prompt and
    each open document, and any session can relaunch it to resume ("Resuming").
11. An executor goes idle with its pass unfinished and no stop in STATUS, or a planner goes idle
    with no executor and no draft PR. The conductor relaunches it from its prompt, twice at most.
    A third idle parks the pass, or ends launches where no PR can be opened.
12. An acceptance item can't be met as written, or a shared assumption proves false. The pass
    parks. No session rewrites the item or builds around it.

## The order table

The conductor follows the table in its prompt, and `advisor.md` where it is silent. Passes run
one at a time. Before each launch, in this order:

- Read usage with `claude -p "/usage" --model haiku < /dev/null` and note the "Current week (all
  models)" figure.
- Check the main checkout: it is on the default branch, and after a fetch
  `git rev-list --count HEAD..origin/<default>` prints 0. Pull with `--ff-only` if it doesn't.
- Write the report.
- End each finished or parked session with `claude stop <id>`, run alone. A refusal is reported,
  never retried.
- Run `claude-worktree-busy <checkout>`.
- Cut the worktree: `git -C <checkout> worktree add .claude/worktrees/<pass> -b <branch>
  origin/<base>`. The base is the default branch, or the parent's branch when the parent waits
  for a close packet with its review accepted.
- Launch the pass's planner from its committed prompt.

A pass that depends on another starts only after that pass's whole-branch review is accepted.

## Reading a pass

When the executor idles, read its PR, checks, and review verdict. A pass never counts
as finished on its last message.

- **Land** when the PR is ready, `Review:` reads `accept, open findings 0`, no check fails, every
  acceptance item appears under `## Acceptance`, the table doesn't mark the pass, no earlier pass
  waits for a close packet, and `approval-packet` step 1 lets it land (`Calls: none`, no
  `## Before merge`, not `auth-data`). Land as that step says, then pull the main checkout.
- **Wait for a close packet** when the PR is ready and the land test fails only on
  `approval-packet` step 1, an open finding, the table's mark, or an earlier waiting pass. Later
  passes of its chain join the packet in merge order.
- **Park** when STATUS on the branch holds a `## Stop`, or the PR is a plan-only draft (answer 1).
- **Relaunch** when none of these holds (answer 11).

## Queue rules

- Every PR's base is the default branch. `merge` and `land` refuse any other base.
- A stop goes to Geoff as a `decide` document. A parked pass with no PR opens a draft holding the
  stop, which the conductor reads.
- The close packet is one `merge` document per round, sent after its last pass ends, PRs in merge
  order. Each call, `fix` or `escalate` verdict, and `## Before merge` section is a question in
  it. The queue won't send a PR with a red check, so the conductor has it fixed or sends a stop.
- A note asking a PR change goes under `## Rulings` in that pass's plan, and its executor
  relaunches.
- A pass that resumes after the close packet went out lands or gets its own close packet.
- `approval-queue send` and `collect` run in the background, never under `timeout` and never
  killed; other long commands take a `timeout`.

## Stops

A stop is a question `advisor.md` leaves for Geoff, a second refusal, an unmet acceptance item, a
false shared assumption, or a closing review that ends on `escalate` or a second read short of
`accept`. The executor then:

- Commit and push the work.
- Open the draft PR if none exists.
- Write the stop under `## Stop` at the end of `docs/STATUS.md` on the branch: the question, what
  it tried, and the choices it sees.
- Push and end. Never ask Geoff in chat, and never run `notify-send`.

Stop your background commands with `TaskStop`, never `kill` or `pkill`.

## Evidence

The PR body carries four lines: `Round: <id>`, `Pass: <name>`, `Review: <accept|fix|escalate>,
open findings <n>`, and `Calls: none` or `Calls: <n>` with each call under `## Calls for Geoff`.

`## Acceptance` lists every acceptance item verbatim, each with its evidence: the command
and its output, or a screenshot.

The closing `standards:diff-reviewer` checks each acceptance item against its evidence. A finding
left unfixed after the fix chain becomes a call for Geoff, and a `fix` verdict gets one second
read by a fresh reviewer.

## Miss tags

Each line under `## Planning misses` opens with one tag: `[mechanism]`, `[file-list]`,
`[permission]`, `[design-gap]`, `[stale-fact]`, `[owner-call]`, `[no-answer]`, `[conflict]`,
`[estimate]`, or `[ambiguous]`. `round.md` defines each.

## Report

The round report is a `report` document at `reports/<round>-report.md` in the initiative record.
The conductor rewrites it before each launch and wait, and at the end: the last pass
read, a stop, the usage ceiling, or the clock. It then runs `approval-queue check` and `send` on
it once: a sent report can't be revised. Its parts, in order:

1. A title saying what is true now, and a first paragraph that is the whole report made small,
   ending on whether anything waits for Geoff. A report takes no answer: the first section names
   each waiting question, `[advisor]` calls included, by what it decides, and the close packet or
   `decide` document that holds it.
2. What behaves differently now: what landed.
3. What went wrong: stops, refusals, and planning misses by tag.
4. What it cost: minutes planned and taken, and weekly usage before and after.
5. What is left for later, as backlog items named by what they do.

After each write, copy the title, the first paragraph, each open document's id, and `Resume
from:` with the conductor prompt's path into the main checkout's `docs/STATUS.md`, between
`<!-- round-report <id> -->` and `<!-- /round-report -->`, while it is level with its remote.
Commit by path and push. After a failed push, undo the commit and copy no more this round. An
executor edits STATUS below the block only.

## Clock

The clock runs from the first planner's launch to the conductor's read of the last PR. It
stops while the conductor waits on the usage reset, another round, or Geoff's answer to a
`decide` document. The planned minutes are the order table's sum.

## Resuming

A report file in the record means a conductor is resuming. It reads the file and its STATUS
block, takes each pass's state from its PR and branch, never from the report, re-subscribes to
the round's live sessions in `claude agents --json`, recovers each open document's answer with
`approval-queue collect <id>` in the background, and goes on from the first unfinished pass.
