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

Load `standards:running-passes` first; this skill adds Geoff's operation to it. Then read the one reference for your role:
`references/planner.md` to design or plan, `references/executor.md` to execute, or
`references/conductor.md` to conduct. A planning dispatch cites `references/planning-samples.md`.

## Lifecycle

Geoff approves a design as a design part in an approval-queue packet
(`approval-packet`), never through a question in chat (Geoff, 2026-10-28).

1. **Design.** Opus at `high` brainstorms (`standards:brainstorming`); the planner reference holds
   what a design carries. If the diff fits in one sentence, skip steps 2 to 4.
2. **Spec.** Written only if `standards:spec-plan-review`'s depth calls for one, with every
   mechanism quoted from source or probed.
3. **Review.** By class (see "Plan review lens"). A finding that changes the approved design
   returns to Geoff as one batched question; the rest are folded.
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

Beyond `running-passes` "Execute", the session stops for a stop the plan writes once its standing
answer runs out.

A mid-run question to Geoff is a planning miss, recorded in the PR's `## Planning misses`: the
question, his answer, and the plan item that should have answered it. The fix waits for the monthly
prune. Under a conductor, the executor writes a stop to STATUS and waits, and the conductor asks.

## Pairs

Pairs run as `running-passes` sets out; the executor reference holds the dispatch.

## Gates

Gates run through `cairn-run-gate`, and CI carries the whole suites off the critical path; the
executor reference holds the rules.

## Clock stop

No clock file is written, and nothing stops on time. At a task's end, an actual over twice the
estimate (from commit times) adds one line to the PR's `## Decisions` naming both. A session whose
prompt says to write `.pass-task-clock` may skip it.

## Conductor

A conductor runs only when the design asks for one; otherwise the executor closes the pass itself.
Its rules are in the conductor reference.

## Close

The close steps are `running-passes` "Close", with `standards:visual-verifier` on rendered UI in
a site or the cairn admin. The adapter's close checklist runs, and STATUS is updated. The PR body opens with a `## Brief` per
`~/.claude/docs/voice/approval-brief.md`, then carries what landed, each `auth-data` verdict,
`## Decisions`, `## Planning misses`, and the score. Follow-ups go through `approval-packet`
"File follow-ups".

When the work is ready for Geoff's read, the session that hands it over sends one packet: it writes
the fact file, runs `approval-queue snapshot <facts.json>`, has the writer produce `text.md` (per
`approval-packet`), then runs `approval-queue packet <initiative> <facts.json> <text.md>` and stays
open until the command exits with Geoff's decision as JSON. An approve is Geoff's merge
authorization, the authorization a launch prompt's "never merge" otherwise withholds: the session merges with `approval-queue merge <id>`, which merges each
approved PR at the head Geoff read, and pulls the checkout as below. `claude-merge-guard` denies
every GitHub CLI merge stage and names `approval-queue merge` and `approval-queue land` as the
replacements. On a send-back, the session fixes forward from the note. `approval-queue triage` is only
for an explicit backlog triage.

A pass with no call for Geoff, no `auth-data` path, and no `## Before merge` step lands its PRs with
`approval-queue land <owner/repo#n> <claim>` and sends no packet, in every class, once its checks
are green and its whole-branch review is accepted with no open finding; the app lists each on the
digest page (Geoff, 2026-11-10). Its follow-ups go to `BACKLOG.md` and the PR body as above, never
to a packet (Geoff, 2026-10-17). A pass with a call, an `auth-data` path, or a `## Before merge`
step sends a packet. An adapter line that says every PR waits for Geoff yields to this exception.

A PR must be safe under a plain merge followed by a pull; the executor makes it so where it can.
When it cannot, the PR body carries a `## Before merge` section: the exact commands in order and
the one check that shows they ran. `approval-queue merge` stops with exit 2 at a PR whose body has
`## Before merge` and prints the section; after the merger runs those steps it reruns with
`--premerge-done <owner/repo#n>`. The packet raises the section as a call, and `approval-packet`
says who runs the steps for each choice.

Whoever merges a PR then brings that repo's main checkout up to date: `git -C <checkout> pull
--ff-only` when the checkout is on its default branch, has no uncommitted change in a file the
merge touches, and has no live session (`claude agents --json`). Otherwise it reports the checkout
as stale and never forces it.

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
