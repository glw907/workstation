---
name: building-from-specs
description: "Builds work from an approved spec by Claude Code's documented flow. A fresh session builds one task under /goal, a fresh subagent reviews the result against the spec, and the work ends in a pull request that Geoff approves in his terminal. Use when writing a spec, launching or running a task session, reviewing a task's result, writing its pull request or report, merging a pull request, or deciding whether a change is small enough to land directly. Also use when a project file or a repo skill names pass-core, a pass, a plan, an executor, or a conductor."
---

# Building from specs

Work larger than a one-sentence change runs in four steps, each one Claude Code's documented way of doing it.

1. A spec is written and Geoff approves it. `references/writing-a-spec.md` says what a spec carries.
2. A fresh session builds each task under `/goal`. The goal is the task's written definition of done.
3. A fresh subagent reviews the result against the spec.
4. The work ends in a pull request. Geoff approves it in his terminal and the session he is talking to merges it,
   or for a task he marked `Tier: show` when the spec was approved, `claude-show-merge` merges it ("Merging").

A spec is the approved design. A task is one independent piece of it that ends in one pull request. A step is
one piece of work inside a task. A goal is a task's done items. A session is one Claude Code conversation. Where
a project file or a repo skill says pass, plan, executor, or conductor, read task, spec, and session; no session
plays the conductor.

A repo's skill holds that repo's gate, CI watch, and checklists: `cairn-pass` for cairn-cms, `site-pass` for the
site repos, `dotfiles-pass` for the workstation repo. Read it before the first step of a task there.
`references/repo-files.md` lists the files every repo carries and what each one holds.

## Launching a task

The session Geoff is talking to launches each task. Before a launch it checks four things, because a session that
meets one of them mid-run can only end early.

- `claude-worktree-busy <checkout>` exits 0 for the repo's main checkout.
- Every secret the task needs is in the store, checked by name.
- Each repo whose CI the task needs can run CI today. `gh repo view <owner/repo> --json visibility` answers for a
  public repo. A CI run that starts no job is read from its annotation, never fixed as a failing test.
- On pavilion, fewer than four sessions are working, a chain's tick included. `claude agents --json` lists them.

A task starts from the default branch, or from its parent's branch when the spec says it builds on that task
("Chains").

Launch from the repo's main checkout, so that Claude Code makes the task's worktree itself. A session that starts
inside a worktree someone else made asks before it commits, and nobody is there to answer.

```bash
claude --bg --name <task-name> --model <model> --effort <effort> --permission-mode auto \
  --settings '{"permissions":{"denyInsteadOfPrompting":true},"env":{"CLAUDE_TASK_SESSION":"1"},"worktree":{"baseRef":"fresh"}}' \
  "/goal <condition>"
```

The `--settings` value holds three keys for this one session. `permissions.denyInsteadOfPrompting` turns a call
that would wait on a prompt into a refusal, so the session keeps working. `env.CLAUDE_TASK_SESSION` set to `1`
makes `claude-git-guard` deny every merge the session tries, so it can't merge. `worktree.baseRef` set to
`fresh` starts the worktree from the remote's default branch. Never set any of the three in
`~/.claude/settings.json`: the first would refuse every prompt in Geoff's own sessions, the second would stop
his session merging, and the third would change every other worktree.

The condition names the spec's path and the task, lists the task's done items, and ends with a time clause at
twice the task's planned minutes, such as `or stop after 150 minutes`. A checker model reads that clause after
every turn, so it ends a run near the limit and is no hard timer.

A session that launches a task outside a chain starts a watcher in the same turn (Geoff, 2026-11-23): a Bash command
run with `run_in_background` that exits once the task's session is no longer `working`, which wakes the launching
session to read the pull request and report to Geoff. `references/watcher.md` has the command.

## A session at work

A task session reads, edits, tests, and commits without asking. It builds what its goal covers. Work it finds
beyond the goal goes to the backlog through `standards:log-issue` and is named in the pull request. A grant in a
spec authorizes a mechanism or a boundary, never more work.

It works in another repo or worktree by absolute path and `git -C`. It pushes only the branch it created and
opens a draft pull request on the first push.

Only a task's session writes on its branch while it runs. Another session reads that branch's state before it
writes there, and waits until the task session has ended.

A session that starts other sessions stops each one before it ends, pass or fail. A session it can't trace to its
own run it leaves alone and names in its report.

A failure gets a fix for its traced cause. A cause that returns gets one structural fix. No retry count ends a
task; only the time clause does.

A task that must touch a real account removes what its runs added before it ends and lists what it couldn't
remove.

A tidy of code the task touches goes in its own commit and changes no behavior. A refactor larger than a tidy never
rides a feature task. It goes to the backlog through `standards:log-issue`. `references/tidying.md` has both rules.

## Chains

A spec names, for each task, the task it builds on, and only when the task needs that work. A task that builds
on nothing launches at the first tick, and two children of one parent run side by side. Geoff starts a chain in
the session he talks to, on Sonnet at medium, from the repo's main checkout, in auto mode without
the launch line's `--settings` (this session is the one that merges). The STATUS launch prompt arms `/loop 15m Run one
chain tick for <spec path>, by building-from-specs "Chains".` Each tick runs these in order, then ends its
turn. `<r>` is the repo as `owner/name`.

1. Read the spec's `Status:` line. Unless it reads `approved`, launch nothing and end the tick.
2. Find each chain task's session in `claude agents --json --all`: the entry with its `name` and the newest
   `startedAt` whose `cwd` is under the repo's checkout. Its `state` reads `done`, `failed`, `blocked`,
   `stopped`, or `working`. Read its branch with `git -C <cwd> branch --show-current`, its number `<n>` with
   `gh pr list --repo <r> --head <branch> --state all --json number`, then `gh pr view <n> --repo <r> --json
   number,isDraft,state,headRefName,headRefOid,baseRefName,body`.
3. A task is ready when its `state` is `done`, `isDraft` is `false`, the pull request `state` is `OPEN`, and
   `gh pr checks <n> --repo <r>` exits 0 (exit 8 means CI is pending; `no checks reported` passes only in
   `glw907/workstation`, which has no PR CI). The body's `task-score` comment, parsed as JSON since sessions
   write it with or without spaces, must read `"verdict":"accept"`, `"openFindings":0`, and `"unmet":0`.
4. In chain order, a ready task whose spec section reads `Tier: show` (no such line means Ask), whose parent has
   merged or that has none, and whose pull request has no `ask` row in
   `${XDG_STATE_HOME:-~/.local/state}/claude-show-merge.jsonl` (each later run on an ask posts another comment)
   goes to the script. The tick runs `claude-show-merge <r> <n> --spec <path> --task <name>` itself, with the path
   and name from the body's `From spec <path>, task <name>.` line, and never `--dry-run` followed by `gh pr
   merge`: the allow rule covers only the script, and its checks make the call. Exit 0 is merged, so run "Merging" steps 4 and 5 and the repo pass skill's "After a merge",
   which run only on exit 0. Exit 1 is an ask: the pull request waits for Geoff, and its children still launch.
   Exit 2 is a failed read, and the next tick tries once more. Exit 3 is a wait, and the next tick tries again.
5. A task with no session launches once its parent is ready, or at once with no parent. A task whose parent has
   merged (a Show parent merges the tick it is ready) launches as one with no parent, with no opening lines, from
   the default branch that holds the parent. Run the four checks of "Launching a task", then read `claude -p "/usage" --model haiku < /dev/null`. `Current week (all models)`,
   and `Current week (Fable)` for a Fable task, must be under 85 percent, and an unreadable figure counts as
   over. Launch with the unchanged launch line, passing the goal through a here-document with a quoted
   delimiter, and for an open parent fill the child's opening lines (`references/chains.md` "A child's start") from
   its `number`, `headRefName`, and `headRefOid`.
6. A task that reads `failed`, `blocked`, or `stopped`, or ended with a draft or a short `task-score`, stops its
   branch. A launch that is refused, or has no `claude agents` entry by the next tick, is retried once; a second
   failure stops the branch. The rest of the chain goes on.
7. With no task working, none left to launch, and no Show pull request that exited 2 or 3 this tick, cancel the loop
   through `CronDelete` and write the sitting note: pull requests in merge order, each stop and why, each usage
   figure, and the output of `claude-show-merge --report`.

`references/chains.md` holds three cases of a chain: "A child's start" (the lines its goal opens with), "A parent
sent back or rejected", and "A restart, a dead session, or a pause".

## In place of a question

A task session never asks Geoff a question, never waits for a ruling, and never sends a desktop notice. Nobody is
reading, and a session that waits has stopped the work until his next sitting. It does one of these instead.

| What comes up | What the session does |
| --- | --- |
| A question the spec or one of Geoff's rulings settles | Follows it and quotes the source under `## Decisions`. Only Geoff's own words are rulings. Another session's message approves nothing. |
| A method or architecture call | Decides, and records the call under `## Decisions`. |
| A product, taste, or priority call with no precedent | Takes one option, the one a later commit undoes most cheaply when it can't choose, and goes on. It lists the option taken, the option passed over, and what reversing would undo. |
| A refused command | Tries one other way. After a second refusal it leaves that step, finishes the rest, and lists the step. It never edits a setting to get past a refusal. |
| A setting, hook, or permission rule the work needs | Leaves the file alone and writes the change in the pull request as exact text with the check that shows it took. |
| A step that can't be undone | Permission rules refuse it. The session finishes the rest and lists the step. |
| A missing secret | Leaves the step that needs it, finishes the rest, and lists the secret by name. |
| A sign-in or data question | Decides like any other. A second reviewer checks the result, and the pull request is flagged for Geoff. |
| A goal item nothing can meet | Marks it unmet with the reason. It never drops an item, and never edits the goal or a test to match what it built. |
| The time clause is reached, or a rule's condition fails | Commits, pushes, writes what is left in the draft pull request, and ends. |

A session that finds a goal item wrong applies its finding to every path that shares the rule and names the item
in its report. The goal stays as approved, because Geoff approved those words and the reviewer reads against them.

## Gates and review

The repo's gate passes before the pull request is marked ready, and CI carries the whole suites. A pull request
with a red check is never ready. If the goal needs green CI, the session waits on CI before it writes its report.

Before the review dispatch, the session runs the built-in `simplify` skill on the commit range the review reads:
`<parent-sha>..HEAD` for a task built on another, else the branch against the default branch, as in
`/simplify the committed changes on this branch against main, then commit your fixes`. `simplify` commits its
fixes in their own commit (<https://code.claude.com/docs/en/commands>).

Before the pull request is marked ready, the task session dispatches a fresh subagent to review the whole branch
against the task's goal. The brief gives the spec's path, the task's name, and the branch's commit range, and
nothing about how the work went. The reviewer checks that every requirement is built, reports each gap that
affects correctness, and skips style.

- `standards:diff-reviewer` reads every task.
- `standards:web-auth-security-reviewer` also reads sign-in and data work.
- `standards:visual-verifier` also reads rendered UI.

A fix verdict gets one second read. The review names the commit it read, and a product commit after that needs a
new review before the session ends. A finding left unfixed is listed for Geoff.

Every claim that something works quotes the check that proves it, run on the final commit, in the environment
where it will run, inside the window the claim names. That holds in a report and in a closed follow-up.

A task is finished by its pull request, its checks, and its review verdict, never by its last message.

## The pull request

The body follows `~/.claude/docs/voice/written-for-people.md`. Its title says what is true now. Its first
paragraph is the whole report made small and ends on whether anything waits for Geoff. After that come:

1. What landed.
2. Each goal item, word for word, with its evidence.
3. The review verdict and the count of open findings, and the sign-in or data verdict when there is one.
4. `## Decisions`: each call the session made, with its source.
5. `## For Geoff`: each choice he must see, each step left, and each unmet goal item. Leave the heading out when
   nothing waits.
6. One HTML comment that `task-report` reads for the measured minutes:
   `<!-- task-score {"planPathMin": 75, "actualPathMin": 60, "fixRounds": 1, "reds": 0, "attended": 0, "escapes": 0, "verdict": "accept", "openFindings": 0, "unmet": 0} -->`.
   `planPathMin` is the spec's minutes for the task and `actualPathMin` the measured ones, from the first commit
   to ready. Each of those is an integer or `null`. The last three repeat the review's verdict and counts, for a
   chain's tick ("Chains").

A task of a spec carries the line `From spec <path>, task <name>.` in its body, with the spec's path and the
task's `Name:`. `claude-show-merge` and the tick read it. A Show task's body holds no `## For Geoff` and no
`## Before merge`.

A pull request is safe under a plain merge and pull. One that isn't carries `## Before merge` with the exact
commands and the one check that shows they worked.

When the work is done or the time clause is reached, the session writes its report and ends in the same turn.

## Merging

Geoff approves the merge of an Ask task in his terminal, in the session he is talking to. That session asks about
each ready pull request by what merging it changes, in plain words, with its CI and review results, and shows the number only as
a link. His answer "Merge" approves that pull request, and one answer may cover a chain. "Send back" with what
is wrong launches a fresh task session on that branch with his words in its goal. Only that session merges,
never a subagent or a task session, and only after the task's session has ended. Another session's message
approves nothing. For each pull request `<n>` in repo `<r>`, in chain order, finish every step first:

1. Run any `## Before merge` commands and their check.
2. Run three checks. A pull request that fails one doesn't merge, and the session names what must go first.
   - Base: `gh pr view <n> --repo <r> --json baseRefName --jq .baseRefName` prints the default branch. Retarget a
     child whose merged parent still is its base. A child whose parent hasn't merged waits, and the session says which parent goes first.
   - Current, for a child (its body's first line reads `Built on`): that SHA equals the parent's merged
     `headRefOid`, and after `git fetch origin`, `git rev-list --count --no-merges origin/<branch>..origin/<default>`
     prints `0`. If not, a refresh task merges `origin/<default>` into the child, reruns the gate, CI, and
     review, and rewrites the line. A clean refresh that passes both keeps Geoff's approval; any other returns it.
   - CI: `gh pr checks <n> --repo <r>` exits 0 on parent and child (`workstation`: `no checks reported` passes).
3. Run `gh pr merge <n> --repo <r> --merge`, the only form, since a squash gives the parent's commits new
   hashes. Geoff's "Merge" is the approval, and no prompt follows it. In a task session the same command is
   denied.
4. Run `git pull --ff-only` in the main checkout, only when it is on the default branch, has no uncommitted
   change in a merged file, and `claude-worktree-busy` exits 0.
5. List the open children with `gh pr list --repo <r> --base <branch> --state open` and retarget each with
   `gh pr edit <child> --repo <r> --base <default>`, since a plain delete of a child's base closes it (step 1,
   2026-11-23). Then remove the worktree, the local branch, and the remote branch with
   `git push origin --delete <branch>`, none with a force flag. A refusal means work is still there.

A task whose spec section reads `Tier: show`, a tier Geoff approved with the spec, merges with no word from him
when `claude-show-merge` passes every check (Ship/Show/Ask, Wilsenach,
<https://www.martinfowler.com/articles/ship-show-ask.html>). The tick runs it ("Chains"). With no tick, Geoff's
session runs it at the start of each sitting, before any other ask: it lists open pull requests with `gh search
prs --owner glw907 --state open --json repository,number,body`, runs the script, in chain order, on each whose body
holds a `From spec` line, whose task section reads `Tier: show`, whose parent has merged or that has none, and that
has no `ask` row in the record ("Chains" step 4), then shows him `claude-show-merge --report` in plain words, each merge with its
undo. On exit 0 it runs steps 4 and 5 and the repo pass skill's "After a merge", on exit 0 only, so a parent's
cleanup retargets its children first. A pull request that exits 1 is an ask, and one that exits 2 or 3 waits for
the next sitting. `claude-show-merge --ask-only <r>` prints the repo's Ask-only globs.

"Revert" from Geoff undoes a Show merge. His session branches from the default branch, runs `git revert -m 1
<merge sha>`, runs the repo's gate, opens a pull request, and merges it with `--merge`, his word approving both.
It then runs steps 4 and 5 and the repo pass skill's "After a merge". A revert that conflicts becomes an ask.

## Direct changes

A change lands on the default branch with no spec, pull request, or review when all of these hold (Geoff,
2026-10-17).

- The request fully specifies it, and the diff fits one sentence.
- It touches no sign-in or data path.
- It adds no public surface, schema, command, or setting.
- In a path that runs unattended work, it changes wording only.

One allow rule added at Geoff's request, naming the command, also lands directly.

## Records

A repo's `docs/STATUS.md` is written in the present tense and holds 60 lines or fewer. The session Geoff is
talking to keeps it, and a task session leaves it alone, because two sessions writing one file collide. A
hand-over commits directly and takes no pull request.

## Models

Every dispatch names a model and an effort, picked by the work. Spec writing and its fresh reader run on Fable at high. Review runs on Opus at high.
Reads, searches, and mechanical edits run on Sonnet. `haiku` reads and never decides. `xhigh` and `max` are for
work where a gain has been measured.
