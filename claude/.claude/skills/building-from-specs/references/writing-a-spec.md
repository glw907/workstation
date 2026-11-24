# Writing a spec

A spec is the design Geoff approves. A fresh session builds each of its tasks without asking him anything, so the
spec has to answer what that session would have asked.

## Before the design

Read Anthropic's docs page for a mechanism before proposing one. Label each option documented, community (with
its source), assembled from documented pieces, or invented. Where a docs page makes a question go away, say so and
leave the question out.

When Geoff states a constraint, test what already exists against it and show him the result before designing
additions. A concern he repeats hasn't been answered, so stop designing and ask what was missed.

A session designing a replacement for a process asks, before it designs, whether that process should govern the
build.

After a task misses its bar, the next spec reads that task's final artifacts against the code and traces each
wrong claim to its source.

When a brainstorm ends in a written design, that design is the spec. Write it once, by this guide, and bring
it to Geoff once.

## What a spec carries

Match a spec's length to what its work needs. Cover the substance, and leave out filler sections, a summary that
repeats another section, and boilerplate. A spec for a change that is one task covers each point of this list in a
line or two, and each rule in this guide keeps to that size: a search is its command, its count, and the hits that
change, a label names its source, and each call Claude made is one sentence. Its goal gives each done item as one
claim, its command, and what that command prints today and when the item holds, with no commentary. A step another
skill owns is named and never restated. A point with nothing to say gets one line. A probe's output is quoted only
where a done item or a label rests on it. A fresh reader's finding is fixed where it lands, and the spec carries no
account of the read. Before the fresh reader sees the spec, the author cuts each sentence a builder would not miss.

- The intent in Geoff's words, with goals, non-goals, and what would make the work a failure.
- The approaches considered, what each trades off, and the pick.
- What happens when it goes wrong, and the number for each limit.
- The published practice and vendor docs it draws on, with a label on each mechanism. Each label rests on a
  quoted source or on a probe and its output. Nothing says "expected".
- Each assumption that more than one task rests on, with its probe or source, so the least-proven one can be
  named.
- A file list that comes from searches. Each search is given with its hit count, and every hit is listed or
  dismissed.
- Each task's commands, read against the last 30 days of the denials log, so a refusal shows before the run.
- The tasks. Each has a goal, its files, the reviewers it needs, its minutes, and the task it builds on when it
  has one. The spec gives the merge order, and a chain merges parent before child ("Chains").

  The heading of each task's section is followed by these lines, which Geoff approves with the spec:

  ```text
  Name: <the task's launch name>
  Tier: show
  Files: `<glob>`, `<glob>`
  ```

  `Tier:` reads `show` or `ask`, and a task with no `Tier: show` line is Ask. A Show task's `Files:` line has
  backticked globs that cover every path it will change, and none of them reaches into its repo's Ask-only list.
  A repo with no list has no Show task. `claude-show-merge --ask-only <owner/repo>` prints the list, one glob per
  line, and exits 1 for a repo with none. A task's section runs from the heading above its `Name:` line to the next
  heading of the same or higher level. Only the spec's author sets a tier, and Geoff approves it with the spec: a
  task session never picks its own.

  Tasks run setup first, then the foundation every feature needs, then one phase per feature in priority order
  (Spec Kit, <https://github.github.com/spec-kit/>). A task that builds on nothing is Spec Kit's parallel mark,
  so a spec adds no other mark. A new project's first task is a walking skeleton: the thinnest build that carries
  one function end to end through every major part (Cockburn,
  <https://henricodolfing.com/2018/04/start-your-project-with-walking-skeleton.html>). Among tasks free to go
  next, the one resting on the least-proven assumption goes first.

  A decision that binds later work becomes a record in the repo's `docs/decisions/`
  (<https://adr.github.io>), written in the task that first builds on it. When a feature task must change code
  under a check's exclusion, the spec puts a task that changes no behavior right before it. That task
  restructures the code and removes the exclusion, and the feature task builds on it (Fowler's preparatory
  refactoring, <https://martinfowler.com/articles/preparatory-refactoring-example.html>).
- The calls Claude made, in one list Geoff can check.

A spec that adds a project, a service, or running infrastructure names where it runs and why, after weighing
Cloudflare against the Hetzner servers orpheus and ward: what fails together, what the host already carries,
cost, and how backup and restore cover it. It never defaults to the host at hand (Geoff, 2026-10-22).

Every spec runs the `standards:backlog-sweep` scoped sweep, never a due full sweep. The spec lists the verdicts,
and approving the spec approves those backlog edits (Geoff, 2026-10-27 and 2026-10-25).

A test never cuts a release candidate (Geoff, 2026-11-09). A run that needs a published build publishes a
snapshot: a `dev` prerelease under a test dist-tag, with no GitHub release, rc tag, or changelog heading
(<https://github.com/changesets/changesets/blob/main/docs/snapshot-releases.md>).

## A task's goal

A goal lists what Geoff would see or run when the task is done. Each item can fail, and each names the command
or screenshot that shows it. Work a person reads names its voice standard.

Before approval, the author runs every check that can run on today's code and records the command and its output
beside the item. A good check is stable between two runs and fails today for the reason the task fixes. Most
checks nothing can meet show up here (Geoff, 2026-11-14).

A goal points at the skill section that owns a command and never copies its flags. A command line the goal must
carry is checked with `--help` that day. A spec names no command for a session to run until that command has been
run once in Claude Code. No goal says "ask Geoff".

A step Geoff will run is rehearsed from his login shell (`bash -lic`), never from a job's shell.

## Minutes

A task's minutes come from the measured minutes of like tasks, read with `task-report`, plus the waits of
everything the task drives: CI, timers, and idle limits. An outline is no source for an estimate. The goal's time
clause is twice those minutes.

## Before approval

A spec's start conditions are tested against the day's live sessions. A spec that changes another repo's work
names the sessions working there and reads that repo's STATUS on the day it is approved.

One fresh reader with no context checks the spec before Geoff sees it. Its questions are sorted into three
piles: answered already, minor calls Claude makes and marks, and questions only Geoff can answer.

A finding that changes what Geoff approved goes to him as one batched question at his sitting. A change of scope
is a new spec that he approves.
