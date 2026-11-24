---
name: building-from-specs
description: "Builds work from an approved spec by Claude Code's documented flow. A fresh session builds one task under /goal, a fresh subagent reviews the result against the spec, and the work ends in a pull request that Geoff approves in his terminal. Use when writing a spec, launching or running a task session, reviewing a task's result, writing its pull request or report, merging a pull request, or deciding whether a change is small enough to land directly. Also use when a project file or a repo skill names pass-core, a pass, a plan, an executor, or a conductor."
---

# Building from specs

Work larger than a one-sentence change runs in four steps, each one Claude Code's documented way of doing it.

1. A spec is written and Geoff approves it. `references/writing-a-spec.md` says what a spec carries.
2. A fresh session builds each task under `/goal`. The goal is the task's written definition of done.
3. A fresh subagent reviews the result against the spec.
4. The work ends in a pull request. Geoff approves it in his terminal and the session he is talking to merges it.

A spec is the approved design. A task is one independent piece of it that ends in one pull request. A step is
one piece of work inside a task. A goal is a task's done items. A session is one Claude Code conversation. Where
a project file or a repo skill says pass, plan, executor, or conductor, read task, spec, and session; no session
plays the conductor.

A repo's skill holds that repo's gate, CI watch, and checklists: `cairn-pass` for cairn-cms, `site-pass` for the
site repos, `dotfiles-pass` for the workstation repo. Read it before the first step of a task there.

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
  --settings '{"permissions":{"denyInsteadOfPrompting":true},"worktree":{"baseRef":"fresh"}}' \
  "/goal <condition>"
```

The `--settings` value holds two keys for this one session. `permissions.denyInsteadOfPrompting` turns a call
that would wait on a prompt into a refusal, so the session keeps working and can't merge. `worktree.baseRef`
set to `fresh` starts the worktree from the remote's default branch. Never set either key in
`~/.claude/settings.json`: the first would remove Geoff's merge prompt, and the second would change every other
worktree.

The condition names the spec's path and the task, lists the task's done items, and ends with a time clause at
twice the task's planned minutes, such as `or stop after 150 minutes`. A checker model reads that clause after
every turn, so it ends a run near the limit and is no hard timer.

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

## Chains

A spec names, for each task, the task it builds on, and only when the task needs that work. A task that builds
on nothing launches at the first tick, and two children of one parent run side by side. Geoff starts a chain in
the session he talks to, on Sonnet at medium, from the repo's main checkout, in auto mode without
`denyInsteadOfPrompting` (his merge prompt needs prompting). The STATUS launch prompt arms `/loop 15m Run one
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
4. A task with no session launches once its parent is ready, or at once with no parent. Run the four checks of
   "Launching a task", then read `claude -p "/usage" --model haiku < /dev/null`. `Current week (all models)`,
   and `Current week (Fable)` for a Fable task, must be under 85 percent, and an unreadable figure counts as
   over. Launch with the unchanged launch line, passing the goal through a here-document with a quoted
   delimiter, and fill the child's opening lines below from the parent's `number`, `headRefName`, and
   `headRefOid`.
5. A task that reads `failed`, `blocked`, or `stopped`, or ended with a draft or a short `task-score`, stops its
   branch. A launch that is refused, or has no `claude agents` entry by the next tick, is retried once; a second
   failure stops the branch. The rest of the chain goes on.
6. With no task working and none left to launch, cancel the loop through `CronDelete` and write the sitting note:
   pull requests in merge order, each stop and why, each usage figure.

### A child's start

The child launches from the main checkout with `worktree.baseRef` set to `fresh`, and its goal opens with these
lines. It merges, since a reset was refused as `[Irreversible Local Destruction]` and a rebase rewrites history.

```text
It builds on pull request #<parent> (branch <parent-branch>, head <parent-sha>). Before any edit, run
`git fetch origin <parent-branch>` and `git merge --no-edit origin/<parent-branch>`. On a conflict, run
`git merge --abort` and end, listing the conflicting files. Stop unless `git merge-base --is-ancestor
<parent-sha> HEAD` exits 0. Open the draft pull request with `gh pr create --draft --base <parent-branch>`,
and make the body's first line `Built on #<parent> at <parent-sha>.` The review reads `<parent-sha>..HEAD`.
```

### A parent sent back or rejected

When Geoff sends a parent back, a fresh session launches on its branch with his words. The tick launches no new
child of it until it is ready again, and a child already built on it goes stale, which the current check in
"Merging" catches. A parent he rejects never merges. His session closes each child's pull request after the
child's session has ended, with `gh pr close <n> --repo <r> --comment "Built on #<parent>, which Geoff
rejected."`, and deletes their branches only with his go-ahead. A child relaunches from the replacement.

### A restart, a dead session, or a pause

A restart stops the tick's session and every task session. At the next sitting, `claude --resume` on the chain's
session restores the loop, or a new session runs the same launch prompt, since each tick rebuilds the chain from
GitHub and `claude agents`. Relaunching a `stopped` task is Geoff's call. Auto mode pauses after 3 blocks in a
row or 20 in all, which halts the chain. A fixed loop expires after 7 days, and a goal holds 4,000 characters,
500 of them the child's.

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
5. `## For Geoff`: each choice he must see, each step left, and each unmet goal item.
6. One HTML comment that `task-report` reads for the measured minutes:
   `<!-- task-score {"planPathMin": 75, "actualPathMin": 60, "fixRounds": 1, "reds": 0, "attended": 0, "escapes": 0, "verdict": "accept", "openFindings": 0, "unmet": 0} -->`.
   `planPathMin` is the spec's minutes for the task and `actualPathMin` the measured ones, from the first commit
   to ready. Each of those is an integer or `null`. The last three repeat the review's verdict and counts, for a
   chain's tick ("Chains").

A pull request is safe under a plain merge and pull. One that isn't carries `## Before merge` with the exact
commands and the one check that shows they worked.

When the work is done or the time clause is reached, the session writes its report and ends in the same turn.

## Merging

Geoff approves a merge in his terminal, in the session he is talking to. That session asks about each ready pull
request by what merging it changes, in plain words, with its CI and review results, and shows the number only as
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
   hashes. An `ask` rule stops it at a prompt that Geoff answers once for each pull request.
4. Run `git pull --ff-only` in the main checkout, only when it is on the default branch, has no uncommitted
   change in a merged file, and `claude-worktree-busy` exits 0.
5. List the open children with `gh pr list --repo <r> --base <branch> --state open` and retarget each with
   `gh pr edit <child> --repo <r> --base <default>`, since a plain delete of a child's base closes it (step 1,
   2026-11-23). Then remove the worktree, the local branch, and the remote branch with
   `git push origin --delete <branch>`, none with a force flag. A refusal means work is still there.

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
