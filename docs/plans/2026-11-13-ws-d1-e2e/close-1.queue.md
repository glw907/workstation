---
kind: merge
prs:
  - glw907/workstation#231 | the busy check and the pass report, with their plans
approve: I merge the pull request and pull `~/.dotfiles`.
sendback: Nothing merges.
---

# Stop the busy check refusing on a finished session, and count planning misses in the pass report

One workstation pull request is ready to merge, and it carries no open question for you. It narrows `claude-worktree-busy` so a finished session and the two background services no longer make a checkout look busy. It also gives `pass-report` a table of planning misses by class. Both changes come with their plans and tests, and the backlog gains two items.

## What the busy check does differently

`claude-worktree-busy <directory>` keeps its contract: exit 0 and no output when the directory is free, exit 1 and one line when it is busy.

The session check now skips a `claude agents --json` row whose state is `done`, `stopped`, or `failed`. A row with no state, which is how an interactive session looks, still counts, and so does a running background session.

The process check skips two command lines: `claude daemon run`, and the approval queue's server, `node <path>/approval-queue/build`. Any other process with the path in its command line is still a hit, including another `node` process and a `claude` process that isn't `daemon run`. The skip matches the server's filename exactly, so a file named `build.old` is still a hit.

Before this change the daemon and the queue's server made `~/Projects/approval-queue` and any checkout the daemon had spawned for report busy every time, and every finished session row did the same. The test file gains the cases for each of those, and each case that expects exit 1 also checks which check fired: the process check, the session check, or the third, which looks for a file edited in the last hour.

## What the pass report adds

`pass-report` prints a new `## Planning misses` section after the last repo section and before `## Notes`. It reads the `## Planning misses` section of each merged pull request's body and counts its miss lines by class: the ten tags `mechanism`, `file-list`, `permission`, `design-gap`, `stale-fact`, `owner-call`, `no-answer`, `conflict`, `estimate`, and `ambiguous`, plus `untagged` for a line with none. The table shows each class as a count and as misses per 100 merged pull requests, the unit the approved design uses for its baseline of 33 misses.

A miss line is a list item in column 1, or a bare line that opens with a tag. A `None.` item counts nothing, and a tag may be written with backticks around it. The plan settled these rules from 647 real pull request bodies, because the design left them open. A body with no such section adds nothing, and the repo tables and `## Notes` lines don't change. A window with no miss lines prints `No miss lines in the window.` and divides by nothing.

The change adds a fixture file, `tests/fixtures/pass-report/misses.json`, as a third file beyond the two the design named, and new tests in `tests/test_pass_report.py`. The 20 earlier tests keep their asserts unedited, which shows the old output didn't change.

## What the pull request also holds

The diff adds the two pass plans, `2026-11-11-ur-w1-plan.md` and `2026-11-11-ur-w2-plan.md`, and a launch prompt for each, under `docs/plans/`. Each plan records the probes behind its facts and a plan review whose findings were folded.

It files two backlog items. Item #75 asks the busy check to skip the row of the session that runs it. Today a conductor that checks the checkout it sits in gets exit 1 every time, and the first pass left it that way on purpose, since its acceptance list says a running session in the path stays a hit. The item asks for a narrower fix that tells the caller's row apart from another session's. Item #76 covers a gap in `pass-report`: it prints no notice when a repo's pull request listing reaches the 300 cap. A window of about six weeks would pass that cap in this repo, and the oldest pull requests would drop from every table.

## What I could not check from here

I had the diff and nothing else. It holds no gate output, no whole-branch review verdict, and no pull request body, so this packet makes no claim that the gate is green or that the review ended on accept. Check the Review line on the pull request and its gate result before you approve.


## After the merge

Pass reports gain the misses table, which gives the first measure for the unattended-rounds goal. The busy check stops refusing for the daemon, the queue server, and finished rows. Until #75 lands, a session that checks the checkout it sits in still gets exit 1.
