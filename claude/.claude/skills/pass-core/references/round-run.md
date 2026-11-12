# Round run

Read after `SKILL.md` and your role's reference. The round design and the conductor prompt's
order table win where they differ from this file.

An executor under a conductor enters the pass's worktree with `EnterWorktree` and its `path`,
once, and merges nothing: the branch holds the plan. In a one-pass round the executor sends the
`stop` packet itself through `approval-packet`, and its PR carries no `Round:` line.

## Standing answers

1. A pass stops on a question only Geoff can answer. The executor follows "Stops". The conductor
   waits for the PR's checks, sends one `stop` packet, ends the pass's sessions, and launches the
   next pass that doesn't depend on the parked one.
2. Auto mode refuses a command. The session uses the alternative its plan names, once. A second
   refusal is a stop. No session edits a setting to get past a refusal.
3. A task needs a setting, hook, auto-mode entry, or permission rule changed. That is never an
   executor task. The planner writes it as a command for Geoff in a close packet, and a pass that
   can't finish without it parks.
4. The weekly usage reads 85 percent or more before a launch, or the figure can't be read. The
   conductor finishes the pass in flight, starts nothing new, writes the report, and waits for the
   reset.
5. A pass's parent is parked. The pass parks too and never launches.
6. The busy check exits 1. Launches end in that repo, and the report says so.
7. The round passes twice its planned minutes. The pass in flight finishes, nothing new starts,
   and the conductor writes the report.
8. A plan can't go ahead as designed. The planner parks the pass before any code is written, as
   `round.md` says.
9. Geoff answers a stop packet while the round runs. The conductor appends his ruling under
   `## Rulings` in the pass's plan, commits it by path, and pushes. It runs
   the packet's steps, then relaunches the pass once the pass in flight finishes. The PR
   takes the question under `## Planning misses` and the ruling under `## Decisions`. Passes that
   depended on the parked pass follow in order.
10. The conductor's session dies or the machine restarts. STATUS names
    the conductor prompt and each open packet, and any session can relaunch it.
11. An executor goes idle with its pass unfinished and no stop in STATUS, or a planner goes idle
    with no plan. The conductor relaunches it from its prompt, twice at most. A third idle parks
    the pass.
12. An acceptance item can't be met as written, or a shared assumption proves false. The pass
    parks. No session rewrites the item or builds around it.

## The order table

The conductor follows the table in its prompt and decides nothing. Passes run one at a time.
Before each launch, in this order:

- Read usage with `claude -p "/usage" --model haiku < /dev/null` and note the "Current week (all
  models)" figure.
- Check the main checkout: it is on the default branch, and after a fetch
  `git rev-list --count HEAD..origin/<default>` prints 0. Pull with `--ff-only` if it doesn't.
- Write the report.
- End each finished or parked session with `claude stop <id>`, run alone. A refusal goes in the
  report with no retry.
- Run `claude-worktree-busy <checkout>`.
- Cut the worktree: `git -C <checkout> worktree add .claude/worktrees/<pass> -b <branch>
  origin/<base>`. The base is the default branch, or the parent's branch when the parent waits
  for a close packet with its review accepted.
- Launch the pass's planner from its committed prompt.

A pass that depends on another starts only after that pass's whole-branch review is accepted.

## Reading a pass

When the executor goes idle, read its PR, checks, and review verdict. A pass never counts
as finished on the executor's last message.

- **Land** when the PR is ready, `Review:` reads `accept, open findings 0`, `Calls:` reads `none`,
  the body has no `## Before merge` section, no check fails, the class isn't `auth-data`, every
  acceptance item of the design appears under `## Acceptance`, the table doesn't mark the pass as
  waiting for Geoff, and no earlier pass waits for a close packet. Run
  `approval-queue land --round <id> <owner/repo#n> "<claim>"`, then pull the main checkout.
- **Wait for a close packet** when the PR is ready and the land test fails only on a call, a
  `## Before merge` section, an open finding, the `auth-data` class, the table's mark, or an
  earlier pass that waits.
  Every later pass of its chain joins the packet in merge order.
- **Park** when STATUS on the branch holds a `## Stop`, or the PR is a plan-only draft (answer 1).
- **Relaunch** when none of these holds (answer 11).

## Queue rules

- Every fact file carries the `round` key with the round id, and every landing takes `--round`.
- Every PR's base is the default branch. `packet`, `merge`, and `land` refuse any other base.
- A `stop` packet names the parked pass's PR. If the branch has none, open a draft first,
  with the stop in its body. The packet carries a forced `gate-failed` call on a red
  check or a `fix` or `escalate` verdict, and a forced call on a `## Before merge` section. Its
  `steps` list what the session runs after the answer.
- Never run `approval-queue merge` on an approved `stop` packet: the queue refuses it.
- A sent-back packet is fixed forward and resent with `--replies`, and every note gets a reply.
  When a note asks for a change to a PR, append it under `## Rulings` in that pass's plan and
  relaunch its executor.
- Close packets go out after the round's last pass ends, three unforced calls to a packet at
  most, split by dependency chain. A second packet of one chain merges only after the first, and
  is resent if the first was sent back. On an approve, run `approval-queue merge <id>` and pull.
- A pass that resumes after the close packets went out lands or gets its own close packet.
- Run `approval-queue packet` as a background command with no `timeout`, and never kill it. If
  the answer doesn't wake the session, `approval-queue collect <id>` recovers it. Other long
  commands run under `timeout`.

## Stops

A stop is a question only Geoff can answer, a second refusal, an unmet acceptance item, a false
shared assumption, or a closing review that ends on `escalate` or a second read short of `accept`.
The executor does four things and tries nothing else:

- Commit and push the work.
- Open the draft PR if none exists.
- Write the stop under `## Stop` at the end of `docs/STATUS.md` on the branch: the question, what
  it tried, and the choices it sees.
- Push and end. Never ask Geoff in chat, and never run `notify-send`.

Stop your background commands with `TaskStop`, never `kill` or `pkill`.

## Evidence

The PR body carries four lines, each on its own line: `Round: <id>`, `Pass: <name>`,
`Review: <accept|fix|escalate>, open findings <n>`, and `Calls: none` or `Calls: <n>` with each
call under `## Calls for Geoff`.

`## Acceptance` lists every acceptance item verbatim, each followed by its evidence: the command
and its output, or a screenshot.

The closing `standards:diff-reviewer` dispatch names the acceptance list, and the
reviewer checks each item against its evidence. A finding left unfixed after the fix chain becomes
a call for Geoff, and a `fix` verdict gets one second read by a fresh reviewer. `Review:` holds
the last verdict and the open findings.

## Miss tags

Each line under `## Planning misses` opens with one tag: `[mechanism]`, `[file-list]`,
`[permission]`, `[design-gap]`, `[stale-fact]`, `[owner-call]`, `[no-answer]`, `[conflict]`,
`[estimate]`, or `[ambiguous]`. `round.md` defines each.

## Report

The conductor writes the round report before every launch and every wait on a packet, and at
the end. Its fields, in order:

- A `# ` heading with the round, the repo, and the time written.
- `Round state: running`, `Round state: waiting for Geoff`, or `Round state: ended`.
- A table with one row per pass, under the header `Pass`, `State`, `PR`, `Planned min`,
  `Actual min`, `Usage before`, `Usage after`. `State` reads `not started`, `planning`, `running`,
  `merged`, `waiting`, `parked`, or `skipped`, exactly: the queue's headline counts the `merged`
  cells.
- Stops, refusals, and calls sent to Geoff, each counted and listed.
- Planning misses by tag, read from the PR bodies.
- What waits for Geoff, with the queue item id of each open packet, and what landed.
- `Resume from:` with the conductor prompt's path.

After each write, copy the report into the main checkout's `docs/STATUS.md` under the title line,
between `<!-- round-report <id> -->` and `<!-- /round-report -->`, only while the checkout is
level with its remote. Commit that file by path and push. After a failed push, undo the commit,
copy no more this round, and report it. Then run
`approval-queue report <initiative> <round> <report.md>`. An executor edits STATUS below that
block only.
