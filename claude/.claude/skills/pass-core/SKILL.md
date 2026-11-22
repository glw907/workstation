---
name: pass-core
description: >
  The pass process every repo shares, with one reference per role. Use when an adapter
  (cairn-pass, site-pass, dotfiles-pass) points here, or to plan, execute, or close a pass.
---

# Pass core

Spec: `~/.dotfiles/docs/specs/2026-10-10-lean-pass-process-design.md`. The repo adapter
supplies the gate, lanes, CI watch, worktree setup, path map, and close checklist, and wins where
it disagrees with this skill.

Load `standards:running-passes` first; this skill adds Geoff's operation to it. Then read your role's reference:
`references/planner.md` to design or plan, `references/executor.md` to execute, or
`references/conductor.md` to conduct. A planning dispatch cites `references/planning-samples.md`.

## Until cc-desk runs

Geoff stopped reading the Approval Queue and running the `desk` session on 2026-11-17; cc-desk
(`~/Projects/cc-desk`) replaces both. Until then, these rules override every line here, in the
references, or in `approval-packet` that sends him a document:

1. A question or report for Geoff is written in his terminal session. Nothing runs
   `approval-queue send`.
2. A background session writes its report, or a question that stops it, under "Open decisions"
   in the repo's STATUS with a recommendation. After a stopping question it ends.
3. A pull request with no call for him lands as `approval-packet` step 1 says.
4. A pull request that needs his approve waits, named under "Open decisions". Once his message
   in a terminal session approves it by number, that session merges it with `gh pr merge`
   behind the permission prompt. It first runs any `## Before merge` steps and their check and
   removes that section from the PR body, and withdraws any queue document holding the PR.

## Lifecycle

Geoff approves a design in his terminal session ("Until cc-desk runs"). Every design is a
round design of one to six passes in one repo. A planner also reads `references/round.md` and
`references/ready.md`, and a conductor or an executor reads `references/round-run.md`.

1. **Design.** Opus at `high` brainstorms (`standards:brainstorming`); the planner reference holds
   what a design carries. If the diff fits in one sentence, skip steps 2 to 4.
2. **Spec.** Written only if `standards:spec-plan-review`'s depth calls for one, with every
   mechanism quoted from source or probed.
3. **Review.** By class (see "Plan review lens"). A finding that changes the approved design
   returns to Geoff as one batched question while he is at the sitting, and goes through
   `references/advisor.md` once planning runs unattended; the rest are folded.
4. **Plan.** `running-passes` "Plan", opening with a `## Pre-flight` list (planner reference).
5. **Execute.** See "Execute".
6. **Close.** See "Close".

## Plan review lens

`standards:spec-plan-review` holds the method; the class sets the reads.

| Class | Before code | At close |
| --- | --- | --- |
| `ordinary` | None; the plan's `Reviewed:` line says so | One whole-branch `standards:diff-reviewer` |
| `runner` | One `standards:plan-reviewer` read | The same |
| `auth-data` | One `standards:plan-reviewer` read | The same, and one `standards:web-auth-security-reviewer` read |

No review runs on a commit while CI runs.

## Direct changes

A change lands on the default branch with no design, plan, PR, review agent, or packet when all
of these hold (Geoff, 2026-10-17):

- Geoff's request fully specifies it, and the diff fits in one sentence.
- It touches no `auth-data` path and adds no public surface, schema, command, or setting.
- In a `runner` path it changes wording only: the skill or agent tells a session the same thing,
  and no step, rule, trigger, or tool list changes.

At Geoff's request naming the command, a direct change may add one
`permissions.allow` rule for a gate, fast-lane, or test command the repo's adapter names, and the
reply quotes the rule. A second rule, an `autoMode` entry, or any change to a deny rule is a pass.

The session runs the adapter's gate, commits the named files, pushes to the default branch, and
names the commit in its reply. When another session is live in the main checkout, it commits in a
worktree cut from `origin/<default>`, pushes with `git push origin HEAD:<default>`, and brings the
checkout up to date as "Close" sets out. Where a push deploys, as on the sites, the change also
passes the full-page render read of each touched page. A finding past the
one sentence makes it a pass.

## Models

- Design and plan authorship: `claude-opus-5-5` at `high`; other Opus work, reviewers included,
  at `medium`. Reviewers take the model from agent frontmatter.
- Conductor, executor, and pairs: `sonnet` at `medium`, or Opus where the design calls the work
  judgment. A red traced to executor reasoning moves the next pass to `high`.
- `xhigh` and `max` only where a quality gain is measured: an unsettled decision re-runs at
  `xhigh`, then one `fable` dispatch at `high`, never a session switch or frontmatter pin. `haiku`
  reads and copies, never decides; `low` suits mechanical subagents, never Fable.

## Execute

One session executes, named `<project>-<pass>` (repo basename and plan slug, as in
`dubplate-intake-1`) whoever launches it, and a relaunch keeps the name (Geoff, 2026-10-12).

## Judgment calls

A session goes on past an open question: it takes the advisor's choice and lists it for Geoff at
the close (Geoff, 2026-11-14). It stops only for what `references/advisor.md` "What always stops"
lists, and this overrides `running-passes` "Execute".

A mid-run question to Geoff is a planning miss, recorded in the PR's `## Planning misses`: the
question, his answer, and the plan item that should have answered it. The fix waits for the monthly
prune. A question for Geoff first goes through `references/advisor.md`, which overrides
`running-passes` on an open product or taste call. Under a conductor, the executor writes a stop
to STATUS and ends; the conductor sends the question as a `decide` document.

## Pairs

Pairs run as `running-passes` sets out; the executor reference holds the dispatch.

## Gates

Gates run through `cairn-run-gate`, and CI carries the whole suites off the critical path; the
executor reference holds the rules.

## Conductor

A round of two or more passes has a conductor, whose rules are in the conductor reference. A
one-pass round has none, and its executor closes the pass itself.

## Close

The close steps are `running-passes` "Close", with `standards:visual-verifier` on rendered UI in
a site or the cairn admin. The adapter's close checklist runs, and STATUS is updated. The PR body
opens with a paragraph written per `~/.claude/docs/voice/written-for-people.md`, then carries what
landed, each `auth-data` verdict, `## Decisions`, `## Planning misses`, and the score. Follow-ups
go through `approval-packet` step 7.

A pass's hand-over is the `approval-packet` skill. Its step 1 says when a pass sends nothing and lands. An adapter line that says every PR waits for Geoff yields to step 1.

A PR merges only by `gh pr merge` behind the permission prompt, run by the session Geoff is
talking to, once its checks are green and its whole-branch review is accepted with no open
finding.

A PR must be safe under a plain merge followed by a pull; the executor makes it so where it can.
When it cannot, the PR body carries a `## Before merge` section: the exact commands in order and
the one check that shows they ran. The merging session runs both before it lands the PR.

Whoever merges a PR then brings that repo's main checkout up to date: `git -C <checkout> pull
--ff-only` when the checkout is on its default branch, has no uncommitted change in a file the
merge touches, and has no live session (`claude agents --json`). Otherwise it reports the checkout
as stale, offers to pull it once the blocker clears, and never forces it.

After the pull, the merging session removes the pass's worktree with `git worktree remove <path>`
and its branch with `git branch -d <branch>`, with no force flag. A dirty tree, an unmerged branch,
or a live session in the worktree leaves it in place with one report line. An executor that merges
its own PR leaves through `ExitWorktree` with removal.

## Score

The executor reference sets out the score and its `pass-score` comment.

## Ledgers

`docs/STATUS.md` is present tense and 60 lines or fewer: current state, next action, open
decisions. Initiatives are records managed by `/log-project`, and a repo's backlog is
`BACKLOG.md`. A commit id cited in a ledger survives a merge. Git and PR bodies are the history.

A hand-over (the STATUS update, the next session's launch prompt, and the research records it
carries) changes no behavior, so it takes no PR and no packet (Geoff, 2026-10-11 and 2026-10-31).
The session runs the gate and commits it to the default branch as "Direct changes" sets out.

## Scope

A grant authorizes a mechanism or a boundary, never more work. Work found mid-task is filed
through `standards:log-issue` and listed in the PR body, never sent as a packet item.

## Launch prompt

A launch prompt lives in a committed file, launched as `"$(cat <file>)"`; the planner reference
holds what it carries.

## Pre-flight and owner-only steps

The plan's `## Pre-flight` list holds every step only Geoff can do and every permission the run
needs; the planner reference holds the rules.
