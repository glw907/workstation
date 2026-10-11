---
name: pass-core
description: >
  The lean pass process every repo shares: the six-step lifecycle from design to close, risk
  classes, one executing session with pair subagents, the fast gate with CI carrying the whole
  suites, the clock stop, the whole-branch close review, and the score. Use when a repo adapter
  (cairn-pass, site-pass, dotfiles-pass) points here, or when planning, executing, or closing a pass.
---

# Pass core

Spec: `~/.dotfiles/docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`. The repo adapter
supplies the gate, fast lane, full-suite home, worktree setup, CI watch, risk-class path map,
checklist globs, and close checklist, and wins where it disagrees with this skill.

## Lifecycle

Each task takes a risk class from the adapter's path map: `auth-data`, `runner`, or `ordinary`.
`runner` covers skills, agents, workflows, the gate tools, `.github/workflows`, and `scripts/checks`.
The design's class is a floor, and a pass takes its highest task's class. A `live-account` flag
marks a run that can touch a real Cloudflare, GitHub, or npm account.

1. **Design.** Opus at `high` brainstorms in chat. Geoff approves a design of a page or less: the
   outcome, files and interfaces touched, what is out of scope, one end-to-end check, and the risk
   class. If the diff fits in one sentence, skip steps 2 to 4.
2. **Spec.** An agent writes the approved design at the length precision needs. Every mechanism
   it states is quoted from source or probed, never recalled.
3. **Spec review.** `spec-plan-review` runs three Opus lenses in parallel, then a probing fold and
   one verification read. A finding that changes the approved design returns to Geoff as one
   batched question; every other finding is folded without him.
4. **Plan.** A task list. Each task carries its outcome, files, risk class, acceptance check, test,
   and a clock estimate in minutes, and never implementation code. Independent tasks are marked as
   pairs. Fold a single-deliverable task into a neighbor. Plan review runs the mechanics lens and a
   verification read; an `auth-data` or `runner` pass, or one with `live-account`, runs all three
   lenses. Skip `writing-plans`' code steps and execution-method question. Test-first applies to
   `auth-data` tasks.
5. **Execute.** See "Execute".
6. **Close.** See "Close". Geoff reads the PR and merges.

## Models

- Design and plan authorship: `claude-opus-5-5` at `high`, since planning may spend more for a
  better result. All other Opus work, reviewers included, runs at `medium`.
- Executing session and pair subagents: `sonnet` at `medium`. A clock stop or CI red traced to
  executor reasoning moves the next pass to `high` (Sonnet 5.5 page: "start at medium for
  well-specified tasks and move to high for harder or longer ones").
- Reserve `xhigh` and `max` for work where you've measured a quality gain (Opus 5.5 page). An
  unsettled decision re-runs at `xhigh`, then `max` (one session-only adjudication), then one
  `fable` dispatch, per dispatch and never a session switch or frontmatter pin. Reviewers take
  `claude-opus-5-5` from agent frontmatter. `haiku` reads and copies, never decides, and stays under
  100k context. `low` effort suits mechanical subagents, never Fable.

## Execute

One session executes. The planning session starts it from the repo's main checkout with `claude
--bg --model sonnet --effort medium --name <name> "$(cat <prompt file>)"`, so Geoff pastes nothing.

Before the launch, run `git -C <repo> fetch origin` and check that the main checkout is on its
default branch and `git -C <repo> rev-list --count HEAD..origin/<default>` prints 0, since
`worktree.baseRef: "head"` branches from local `HEAD`. Where `git -C <repo> check-ignore -q
.claude/worktrees/x` fails, append `.claude/worktrees/` to the file `git -C <repo> rev-parse
--path-format=absolute --git-path info/exclude` names.

The session's first act is `EnterWorktree`, then the adapter's setup command in the new worktree.
It commits without asking, pushes the branch it created, and opens the PR from it. A pass that
continues an existing branch merges or cherry-picks that branch into the new one first. STATUS
records the session's name and id. The launch prompt names the push target as `glw907/<repo>`, since
auto mode blocks a push to a repository the user did not name. The session arms the API-drop
wake-up (`/loop` with no interval) and, if the lid may close, the lid-switch hold, per
`~/.claude/docs/unattended-work-guards.md`, then reads, edits, writes the tests, and commits.

## Pairs

Two tasks whose files are disjoint, generated outputs included, go to two Agent-tool subagents
with `isolation: "worktree"` after the session commits; `worktree.baseRef: "head"` branches them
from that commit. A shared port is an environment variable. Each runs the adapter's setup command
first, commits, and never pushes. The session merges both, runs the fast lane, and pushes. A merge
conflict stops the line.

## Gates

The adapter's classifier selects the fast lane's legs: type check, the selected unit and component
tests, the static checks the diff touches, and the docs gate when docs changed. Run each through
`cairn-run-gate '<string>'` with the Bash tool's `timeout: 600000`, re-issued on exit 75 until it
prints `gate exit:`; never poll a log. An unchanged tree needs no rerun (`cairn-run-gate --receipt
'<string>'`). Non-browser legs may run concurrently on the light lane only where their measured peak
fits its 3G cap; a browser leg runs alone on the heavy lane after them. Shared lanes:
`~/.claude/docs/unattended-work-guards.md` "Shared gate lanes".

CI carries the whole suites off the critical path, where it runs on PRs. The first push opens a
draft PR, and after each push the adapter's watch command runs as a background Bash task
(`run_in_background`), which re-invokes the session on exit. No task waits for CI before the next. A
red stops the line, and the fix goes forward or the commit reverts. Where the full-suite home is
local, there is no watch command. On an `auth-data` task, `diff-reviewer` reads the commit while CI
runs, and a `fix` or `escalate` verdict stops the line like a red. `RUN_GATE_IF_BUSY=defer` leaves
a heavy leg to the push's CI (exit 76) when another run holds the lock; set it only where CI is the
full-suite home, and never on an `auth-data` task.

## Clock stop

At each task start the session writes `pass-task-clock` in the pass worktree's git dir
(`git rev-parse --absolute-git-dir`, from a `cd` into the task's worktree) with three lines:
`task=<id>`, `start=<epoch seconds>`, `estimate=<minutes>`. It removes the file at the task's end,
and after a pair returns once it has checked the pair's overrun. The `claude-clock-stop` hook
returns a stop line past twice the estimate. The session then writes STATUS, runs
`notify-send -u normal`, and waits for Geoff (one attended event, not a failure). A resume rewrites
`start=`, or `estimate=` to the figure Geoff names. Pair worktrees hold no clock file, so the stop
cannot fire while the session waits on a pair.

## Close

The repo's full-suite home is green on the head. One whole-branch Opus review follows:
`diff-reviewer` at whole-branch scope loads the checklists the adapter's globs match, re-derives
each task's class, and gives any unread `auth-data` task its read. `visual-verifier` runs on
rendered UI in a site or the cairn admin. One batched fix chain follows, then the gate again; a
second review only on a blocker. An overruled verdict is stated with its reason in the PR body, and
a correctness-critical overrule re-runs the review at `xhigh`. The adapter's close checklist runs
(the auth smoke on `auth-data`), STATUS and ROADMAP are updated, and the PR body carries what
landed, each `auth-data` verdict, and the score.

## Score

The PR body carries the spec's price table rows: Gates on the critical path, Work and review, CI
waits on the path, Fix rounds and reds, Close, and Total. Gate and lock time come from
`cairn-run-gate --records <toplevel> <branch>`; the clock runs from the first execution commit to
PR-ready. It lists the attended events (the design, the PR read, one per clock stop) and any escape,
a behavioral, security, or contract defect that surfaces through the next pass's close, CI on
`main`, or Geoff's use; an escape also goes into STATUS with its commit. A miss names its row, or
the step that should have caught the escape, and only that changes.

## Ledgers

`docs/STATUS.md` is present tense and 60 lines or fewer: current state, next action, open
decisions. `ROADMAP.md` holds initiatives under `Active`, `Planned`, and `Someday`, managed by
`/log-project`. Git and PR bodies are the history; `docs/HISTORY.md` and post-mortems stop growing
(ruling 8). A lesson lands where it executes: a skill, agent, tool, or repo doc. Memory holds only a
preference or a ruling's why that no file can.

## Scope

A grant authorizes a mechanism or a boundary, never more work. Work found mid-task goes to the PR
body's "Found, not done" list or to ROADMAP, never into the task in flight, unless the task would
otherwise build on something known to be wrong (say so then).

## Launch prompt

A STATUS next action carries the goal, the scope, the plan path, the checkout, and the exact
`claude` line. The prompt text lives in a committed file and is launched as `"$(cat <file>)"`,
since a prompt pasted inside double quotes runs each backticked span as a command substitution.
Close the session when the initiative lands.
