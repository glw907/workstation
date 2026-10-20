# Brief: planning sessions hand off to a conductor

For a brainstorm. Raised by Geoff on 2026-10-12, at the end of the drafter Pass 0 planning
session (dotfiles-5a): "Is there any good reason this shouldn't be default process from a
planning session? It seems easier and more automatic."

## The proposal

When a planning session finishes a plan, it doesn't launch and watch the executor itself. It
hands the pass to a conductor session and closes. The conductor launches the executor, watches it,
puts the PRs on the review desk, merges on Geoff's approval, and pulls the checkout.

## What pass-core says today

`pass-core` "Execute" has the planning session start the executor with `claude --bg`. Under
"Conductor", it describes the conductor as "the session that runs between passes": it watches
unattended passes, puts each PR or design on the review desk, merges after Geoff approves, and
launches the next committed prompt. The skill doesn't say when a planning session should hand a
pass to a conductor instead of watching it itself.

## Why it helps

- Cost. A planning session ends with the longest context of any session, and every check-in while
  it watches re-reads that whole conversation. A fresh conductor carries only the launch prompt,
  the plan, and the spec.
- Closing on time. The planning session can close when the plan lands, per the global rule "Close
  the session when an initiative lands".
- An explicit hand-off. The conductor's prompt has to state the merge order, the standing answers
  to foreseeable stops, and what goes to the desk. Today some of that lives only in the planner's
  context.
- Independence. The session that wrote the plan stays out of watching its execution, which keeps
  the whole-branch review reading work its planner didn't steer.

## Where it shouldn't apply

1. A conductor is already running. Two conductors could watch, merge, or relaunch overlapping
   work, the race the "One executor per worktree" rule exists to stop. The planning session checks
   `ListAgents` (or `claude agents --json`) and hands the pass to the live conductor with
   `SendMessage` if one exists. It launches a new conductor only when none is running.
2. A self-merging pass. An `ordinary` pass with an empty "Found, not done" list merges its own PR
   (`pass-core` "Close"), so a conductor would only watch it finish. The planning session launches
   the executor directly.

## Draft rule

A planning session whose pass needs Geoff's desk read, or runs unattended past about 30 minutes,
hands it to the live conductor, or launches one if none is running, and then closes. A
self-merging `ordinary` pass launches its executor directly.

## Questions for the brainstorm

1. Does a hand-off to an existing conductor need an acknowledgement before the planner closes?
   A cross-session message can sit unread, or a session in another permission mode can hold it.
2. Which model and effort should a conductor run at? Its job is mostly watching and routing, with
   occasional judgment when an executor stops. `pass-core` "Models" puts all non-planning Opus work
   at `medium`.
3. Should the conductor's launch prompt be a fixed template with slots (pass name, repos, merge
   order, standing answers), so every planner writes the same shape?
4. How does a conductor end? One option: it closes when no pass it owns is open and no committed
   launch prompt is waiting.

## Where it lands

A `pass-core` edit, made through the `claude-infra` skill's rules ("A rule lives where it
executes"), as its own small dotfiles change, separate from any feature pass.

## First instance

The drafter Pass 0 hand-off (2026-10-12) is the first time this pattern is used, before any rule
exists. Its conductor prompt, committed beside the plan in `docs/plans/`, is a working
example for question 3.
