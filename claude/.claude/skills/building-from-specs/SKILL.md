---
name: building-from-specs
description: "Builds work from an approved spec by Claude Code's documented flow. A fresh session builds one task under /goal, a fresh subagent reviews the result against the spec, and the work ends in a pull request that Geoff approves by number. Use when writing a spec, launching or running a task session, reviewing a task's result, writing its pull request or report, merging a pull request, or deciding whether a change is small enough to land directly. Also use when a project file or a repo skill names pass-core, a pass, a plan, an executor, or a conductor."
---

# Building from specs

Work larger than a one-sentence change runs in four steps, each one Claude Code's documented way of doing it.

1. A spec is written and Geoff approves it. `references/writing-a-spec.md` says what a spec carries.
2. A fresh session builds each task under `/goal`. The goal is the task's written definition of done.
3. A fresh subagent reviews the result against the spec.
4. The work ends in a pull request. Geoff approves it by number and the session he is talking to merges it.

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
- On pavilion, fewer than four sessions are working. `claude agents --json` lists them.

A task starts from the default branch, never from another task's branch. A task that needs another task's work
waits until that work has merged.

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
   `<!-- task-score {"planPathMin": 75, "actualPathMin": 60, "fixRounds": 1, "reds": 0, "attended": 0, "escapes": 0} -->`.
   `planPathMin` is the spec's minutes for the task and `actualPathMin` the measured ones, from the first commit
   to ready. Each value is an integer or `null`.

A pull request is safe under a plain merge and pull. One that isn't carries `## Before merge` with the exact
commands and the one check that shows they worked.

When the work is done or the time clause is reached, the session writes its report and ends in the same turn.

## Merging

Only Geoff's typed words approve a merge, and they name the pull request by number. Only the session he is
talking to merges, never a subagent and never a task session. It merges only after that task's session has ended.

1. Run any `## Before merge` commands and their check.
2. Run `gh pr merge <number> --repo <owner/repo> --merge`. An `ask` rule stops it at a permission prompt, and
   Geoff answers that prompt once for each pull request.
3. Pull the main checkout with `git pull --ff-only`, and only when it is on the default branch, has no
   uncommitted change in a merged file, and `claude-worktree-busy` exits 0.
4. Remove the worktree, then the local branch, then the remote branch with `git push origin --delete <branch>`,
   none with a force flag. A refusal means work is still there, so read it.

To send a pull request back, Geoff says what is wrong in his terminal. His session launches a fresh task session
on the same branch with his words in its goal.

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

Every dispatch names a model and an effort, picked by the work. Spec writing and review run on Opus at high.
Reads, searches, and mechanical edits run on Sonnet. `haiku` reads and never decides. `xhigh` and `max` are for
work where a gain has been measured.
