---
name: cc-desk-work
description: How a session that cc-desk launched (a pass executor, a conductor, or a design writer) reports a pull request ready, files a follow-up, writes a question for Geoff, stops, and records a round's report. Load it whenever a launch prompt names cc-desk-work, and before any step where pass-core would send Geoff a document, write to STATUS for him, or ask him in chat.
---

# Working under cc-desk

cc-desk launched this session and reads its records to decide what happens next. Geoff reads
nothing a session writes to STATUS or the Approval Queue, so every hand-over goes through one of
the commands below. `pass-core` still holds how to plan, build, review, and close a pass.

## Run the command lines as the prompt prints them

Your launch prompt prints each command with its binary path and `--state-dir`. Copy those lines
exactly and fill in only the parts in angle brackets. Only the prompt knows which binary and
which state folder this run uses, and the session's allow rules match those exact prefixes. A
shortened `cc-desk ...` line runs against the wrong state, or stops on a permission prompt.

## Where pass-core sends Geoff something

| `pass-core` says | Do this instead |
| --- | --- |
| Write a question for Geoff under "Open decisions" in STATUS | Write it with `question add`, if it is about a pass that hasn't started. Otherwise a pass session stops |
| Write a stop to STATUS and end | Run your stop or finish line, then end |
| A pull request waits for Geoff's approve | Report it with `pass ready`. The check merges it, or asks Geoff a merge question |
| Send a report or a packet | A conductor records the round's report with `report add` |
| Ask Geoff in chat | Never. No one reads a launched session's chat |

No session runs `approval-queue send` or `notify-send`.

## Report a pull request ready

A pass session reports its pull request once it is pushed and its whole-branch review has a
verdict. Run the prompt's ready line:

```text
<ready line> --pr <number> --commit <sha> --verdict <accept|fix|escalate> --design <inside|outside> [--calls <n>]
```

- `--pr` is the pull request's number.
- `--commit` is its last commit. The check merges only that commit, so push before you report.
- `--verdict` is the review's verdict: `accept`, `fix`, or `escalate`. Report `escalate` when the review raised a point it left for Geoff's call, and say how many with `--calls <n>`. With one or more calls, the check asks Geoff before it merges. `--calls` defaults to 0.
- `--design` is `inside` when the change stays within the approved design. Use `outside` when
  it adds something the design didn't name, drops something it named, or changes a ruling's
  outcome. The check then asks Geoff whether to merge, so an honest `outside` costs one
  question while a wrong `inside` merges work he never approved.

## File a follow-up

Write the body to a file in the worktree or the job's `tmp` folder, then run the prompt's
follow-up line with a title. The command refuses a body file anywhere else, an empty body,
and a title whose file already exists. It writes `docs/follow-ups/<slug>.md` in your worktree,
so commit that file with the rest of your work.

## Write a question

A pass or design session asks Geoff about a pass of its round that hasn't started. The command
refuses a question about a pass that has started, so never ask about the pass you are building.
Stop instead (see below).

Write the question as one JSON file, for example:

```json
{
  "id": "backup-second-copy",
  "text": "Should the nightly backup also copy the scans to the second disk?",
  "options": ["yes", "no"],
  "recommended": "yes",
  "background": ["The scans live on one disk today, and the second disk has 30 GB free."],
  "causes": {"yes": "Each backup runs 15 minutes longer.", "no": "One failed disk loses every scan."},
  "reason": "The scans can't be made again.",
  "never_guess": true,
  "passes": ["copy-scans"]
}
```

`passes` names the passes that rest on the answer. `never_guess` is true when no pass may start
on a guess at it. Geoff reads the text, the background, the causes, and the reason, so write
them in plain words with no ids.

Before you run `question add`, test the file on a reader with no context. Make one `Agent`
call, Sonnet at medium effort, whose prompt is the question's text, background, options, and
causes alone, with "State the question this asks, and what each answer would cause." If the
reply misses the question or an answer's cause, rewrite the file and ask a new reader. A
question Geoff can't follow costs him a round trip at the desk. Then run the prompt's question
line with the file.

## Stop

A pass session stops with one of the prompt's `pass stop` lines, then ends. Pick the reason
that fits:

- `usage`: a usage limit stopped the work. The check relaunches the pass after the reset.
- `irreversible`: the next step can't be undone, such as deleting data or publishing a release.
- `secret`: the work needs a secret no store holds, or would put one in a file or a log.
- `auth_data`: the work reaches sign-in, sessions, tokens, or other `auth-data` paths in a way
  the plan didn't approve.
- `scope`: the work needs something outside the plan, or a choice only Geoff can make about
  the pass you are building.

Before you stop, commit and push what you have, so a relaunch carries on from the branch. A
stop for any cause outside these five isn't yours to make: take the advisor's choice, carry on,
and list it under `## Decisions` in the pull request.

A conductor or a design writer has no `pass stop`. It ends with its prompt's `session finish`
line, once its work is recorded.

## Record a report

A conductor records each round's report, and the release's report at the end. The check starts
a conductor for one report when it is due, and the launch prompt names it. Write that report,
record it, finish, and do nothing else. A relaunched conductor runs the brief first, and writes
no second report when the one it was started for is recorded. Write one JSON file with all
four keys:

```json
{
  "title": "Round r1: the first build",
  "summary": "The first round landed with every check green.",
  "calls": [{"call": "Name of the verb", "chosen": "report", "other": "handoff", "why": "The desk already says report."}],
  "misses": [{"miss": "The plan left out the empty-list case.", "cost": "Five minutes."}]
}
```

`calls` and `misses` may be empty lists, `[]`. A missing or null key is refused, and so is a
call with an empty part. Then run the prompt's report line with the file, and add
`--round <round>` for a round's report. Leave it off for the release's report.
