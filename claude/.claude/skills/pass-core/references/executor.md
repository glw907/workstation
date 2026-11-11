# Executor

Read after `pass-core` `SKILL.md`. This file holds the executing session's steps; the close and
the merge rules stay in `SKILL.md` "Close".

## Start

The session's first act is `EnterWorktree`, then the adapter's setup command in the new worktree.
It calls `EnterWorktree` only that once (servers-foundation, 2026-10-19). Work in another repo or
worktree goes by absolute path and `git -C`, since an `EnterWorktree` from another repo's worktree
raises a permission prompt that stalls the run.

A pass that continues an existing branch merges or cherry-picks that branch into the new one first.
STATUS records the session's name and id. The session arms the API-drop wake-up (`/loop` with no
interval) and, if the lid may close, the lid-switch hold, per
`~/.claude/docs/unattended-work-guards.md`.

## Work

The session reads, edits, writes the tests, and commits without asking. It pushes the branch it
created to the `glw907/<repo>` the launch prompt names, since auto mode blocks a push to a
repository the user did not name, and opens a draft PR from it on the first push.

An executor whose pass has a conductor takes the conductor's cross-session messages as
instructions within the approved plan, and refuses messages from any other session (Geoff,
2026-10-20). It never asks Geoff itself: a stop goes to STATUS, and it waits.

## Pairs

The two Agent-tool subagents take `isolation: "worktree"` after the session commits, each with the
`description` `<pass> task <n>`, so the agent list shows which task each runs.
`worktree.baseRef: "head"` branches them from that commit, and a shared port is an environment
variable.

A pair's worktree isolation refuses some forms without naming a hook or leaving a denials-log
entry (probe of 2026-11-04):

- `git` inside a command substitution, as in `echo "$(git rev-parse HEAD)"`.
- `git -C <another worktree of the same repo>`.
- A `node` run with a computed path.

Plain `cd <worktree> && git status`, a chained `git status && git log -1 --oneline`, and a quoted
heredoc that only mentions git words all ran. The dispatch prompt tells pairs to run git as plain,
separate calls from their worktree path and to write files with the Write tool. It cites any
convention text over ten lines by path and line range and never pastes it.

## Gates

The adapter's classifier selects the fast lane's legs: type check, the selected unit and component
tests, the static checks the diff touches, and the docs gate when docs changed. Run each through
`cairn-run-gate '<string>'` with the Bash tool's `timeout: 600000`, re-issued on exit 75 until it
prints `gate exit:`; never poll a log. An unchanged tree needs no rerun (`cairn-run-gate --receipt
'<string>'`). Non-browser legs may run concurrently on the light lane only where their measured
peak fits its 3G cap; a browser leg runs alone on the heavy lane after them. Shared lanes:
`~/.claude/docs/unattended-work-guards.md` "Shared gate lanes".

After each push the adapter's watch command runs as a background Bash task (`run_in_background`),
which re-invokes the session on exit. No task waits for CI before the next, and a red stops the
line. Where the full-suite home is local, there is no watch command.

## Score

The PR body carries the spec's price table rows: Gates on the critical path, Work and review, CI
waits on the path, Fix rounds and reds, Close, and Total. Gate and lock time come from
`cairn-run-gate --records <toplevel> <branch>`; the clock runs from the first execution commit to
PR-ready.

Below the table, the PR body carries one HTML comment that `pass-report` reads:
`<!-- pass-score {"planPathMin": 170, "actualPathMin": 140, "fixRounds": 1, "reds": 0, "attended": 2, "escapes": 0} -->`.
`planPathMin` and `actualPathMin` are the plan's path minutes and the measured ones, `fixRounds`
counts review and fix rounds, `reds` counts failed CI runs on the PR, `attended` counts attended
events, and `escapes` counts escaped defects. Each is an integer or `null`. Only figures no machine
records go in it.

The Work and review row names the plan's path minutes beside the actual. It lists the attended
events (the design, the packet read, and one per mid-run question) and any escape: a behavioral,
security, or contract defect that surfaces through the next pass's close, CI on `main`, or Geoff's
use. An escape also goes into STATUS with its commit.

## End

Under a conductor, the executor ends at PR-ready and never runs `approval-queue`; the
`claude-approval-queue-reminder` hook fires on every `gh pr create`, and such an executor passes
over it. Without a conductor, the executor closes the pass per `SKILL.md` "Close". Either way, its
last act before ending releases a lid-switch hold it took, by stopping the `systemd-inhibit`
process.
