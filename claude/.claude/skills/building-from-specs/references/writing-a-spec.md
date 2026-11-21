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

## What a spec carries

- The intent in Geoff's words, with goals, non-goals, and what would make the work a failure.
- The approaches considered, what each trades off, and the pick.
- The published practice and vendor docs it draws on, with a label on each mechanism. Each label rests on a
  quoted source or on a probe and its output. Nothing says "expected".
- Each assumption that more than one task rests on, with its probe or source.
- A file list that comes from searches. Each search is given with its hit count, and every hit is listed or
  dismissed.
- Each task's commands, read against the last 30 days of the denials log, so a refusal shows before the run.
- The tasks. Each has a goal, its files, the reviewers it needs, its minutes, and the task it waits for when it
  has one. The task that rests on the least-proven assumption goes first. The spec gives the merge order.
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
