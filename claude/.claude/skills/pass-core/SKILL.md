---
name: pass-core
description: >
  The lean pass process every repo shares: the six-step lifecycle from design to close, risk
  classes, one executing session with pair subagents, the fast gate with CI carrying the whole
  suites, the clock stop, the whole-branch close review, and the score. Use when a repo adapter
  (cairn-pass, site-pass, dotfiles-pass) points here, or when planning, executing, or closing a
  pass.
---

# Pass core

Spec: `~/.dotfiles/docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`. The repo adapter
supplies the gate, fast lane, full-suite home, worktree setup, CI watch, risk-class path map,
checklist globs, and close checklist, and wins where it disagrees with this skill.

## Lifecycle

Each task takes a risk class from the adapter's path map: `auth-data`, `runner`, or `ordinary`.
`runner` covers skills, agents, workflows, the gate tools, `.github/workflows`, and
`scripts/checks`.
Only Geoff's ruling raises a class, stated in the design in one sentence. A pass takes its highest
task's class. A `live-account` flag marks a run that can touch a real Cloudflare, GitHub, or npm
account.
A change that meets "Direct changes" skips this lifecycle.

1. **Design.** Opus at `high` brainstorms in chat. Geoff approves a design of a page or less: the
   outcome, files and interfaces touched, what is out of scope, one end-to-end check, and the risk
   class. A design brought for approval goes to Geoff as a design part in a packet, per `approval-packet`.
   An owner fork in the design is a `### Decide:` block in its brief. A design doc opens with `## Brief` after its title, per
   `~/.claude/docs/voice/approval-brief.md`. The design names its initiative (a record in `~/Projects/initiatives`) or says none applies; cross-repo specs, plans, and research go in `initiatives/<id>/`, and the plan header carries an `Initiative: <id>` line. If the diff fits in one sentence, skip steps 2 to 4. Every planning dispatch prompt
   carries
   these two samples, and extras go in "Later", never built:
   > "Avoid over-engineering. Only make changes that are directly requested or clearly necessary.
   > Keep solutions simple and focused: - Scope: Don't add features, refactor code, or make
   > "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A
   > simple feature doesn't need extra configurability. ... - Defensive coding: Don't add error
   > handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and
   > framework guarantees. Only validate at system boundaries (user input, external APIs). -
   > Abstractions: Don't create helpers, utilities, or abstractions for one-time operations. Don't
   > design for hypothetical future requirements. The right amount of complexity is the minimum
   > needed for the current task."
   > (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>)
   >
   > "Deliver what was asked, at the scope intended. Make routine judgment calls yourself, and check
   > in only when different readings of the request would lead to materially different work. If the
   > request seems mistaken or a better approach exists, say so in a sentence and continue with the
   > task as asked rather than quietly narrowing, widening, or transforming it. Finish the whole
   > task, and stop short of actions that are clearly beyond what was asked."
   > (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>)

   A design Geoff approves ahead of its pass, with unattended planning approved, lets the planning
   session run steps 2 to 4, write the executor's launch prompt, and launch the executor or hand it
   to the project's conductor (see "Execute") after the "Execute" pre-launch checks, without him. A plan over twice the design's estimate, or a finding
   that changes the design, stops it: STATUS carries one question and `notify-send -u normal`
   tells Geoff. Before Geoff leaves the run, the approval batch asks how to answer each stop the
   run can foresee, an estimate overrun up to a named ceiling among them, and the design records
   each answer as a standing approval the planner applies in place of stopping. A stop with no
   standing answer still stops (Geoff, 2026-10-12: the intake-1 overnight run stopped at 01:17 on
   a 995-minute plan against a 780-minute line, and nothing ran until morning). So every stop the
   plan writes (a cap, a line stop, a ceiling) carries a standing answer. A count cap on reads,
   retries, rounds, or reruns is a loop guard, never a stop for Geoff. Past it, the run goes on
   while each retry fixes a cause the session has traced and spend stays inside the ceiling, and
   each fix is a reversible change listed in the PR's `## Decisions`. The run stops only on the
   spend or path ceiling, a cause it cannot trace, the same cause returning after its fix, or a
   change to the design (2026-10-19: B3c stopped at its read cap, then at its escalation rule, each
   time with an in-budget fix to a traced cause as the recommendation, and Geoff took it).
2. **Spec.** An agent writes the approved design at the length precision needs, only if
   `spec-plan-review`'s depth calls for one. Every mechanism it states is quoted from source or
   probed.
3. **Spec review.** `spec-plan-review` sets spec and plan review depth. A finding that changes
   the approved design returns to Geoff as one batched question; every other finding is folded
   without him.
4. **Plan.** A task list. Each task carries its outcome, files, risk class, acceptance check, test,
   and a clock estimate in minutes, and never implementation code. Independent tasks are marked as
   pairs. Fold a single-deliverable task into a neighbor. A plan whose path minutes exceed twice its
   design's estimate goes back to Geoff with the reason before launch. The path is the longest chain
   of tasks that run in sequence, a pair counting once at its larger estimate; the sum over every
   task counts the pairs twice and never sets the stop (Geoff, 2026-10-12: intake-1 stopped on a
   995-minute task sum whose path was 725, under its 780 line). The design states its estimate in
   path minutes, set from the actual-against-planned path in recent passes' scores, never from a
   share of a spec's figure. Skip `writing-plans`' code
   steps and execution-method question. Test-first applies to `auth-data` tasks.

   The plan opens with a `## Pre-flight` list: every step only Geoff can do, such as a sign-in, a
   value through `secret-receive`, a dialog, a permission rule, a browser or app action, or a
   physical touch. The design's packet carries the list as its `[you: ...]` steps
   (`approval-packet`), and the planner runs it with Geoff in one sitting right after he
   approves. The executor launches only once each item is done and checked (a sign-in that
   answers, a store name present, a rule in `settings.json`). A step that needs the pass's own
   output is moved earlier or given a path without Geoff where it can be. Whatever remains goes
   into one named sitting at a set point in the plan, and the design approval says when. A run
   that waits on Geoff for a step the list left out is a planning miss (2026-10-19: Pass 1's mail
   reader waited 40 minutes on a Proton Bridge sign-in that needed nothing the pass built).
5. **Execute.** See "Execute".
6. **Close.** See "Close". Geoff decides the packet in Design & PR Approvals, except that a pass whose highest
   class is `ordinary` merges its own PR (see "Close").

## Direct changes

A change lands on the default branch with no design, plan, PR, review agent, or packet when all
of these hold (Geoff, 2026-10-17):

- Geoff's request fully specifies it, and the diff fits in one sentence.
- It touches no `auth-data` path and adds no public surface, schema, command, or setting.
- In a `runner` path it changes wording only: the skill or agent tells a session the same thing,
  and no step, rule, trigger, or tool list changes.

The session runs the adapter's gate, commits the named files, pushes to the default branch, and
names the commit in its reply. When another session is live in the main checkout, it commits in a
worktree cut from `origin/<default>`, pushes with `git push origin HEAD:<default>`, and brings the
checkout up to date as "Close" sets out. Where a push to the default branch deploys, as on the
sites, the change also passes what the repo requires before a deploy: the full-page render read of
each touched page. A finding past the one sentence makes it a pass. Best practices for Claude Code
(<https://code.claude.com/docs/en/best-practices>): "For tasks where the scope is clear and the fix
is small ... ask Claude to do it directly."

## Models

- Design and plan authorship: `claude-opus-5-5` at `high`, since planning may spend more for a
  better result. All other Opus work, reviewers included, runs at `medium`.
- Conductor: `claude-opus-5-5` at `medium`. Its rare merge and relaunch calls carry the risk, and
  it mostly waits.
- Executing session and pair subagents: `sonnet` at `medium`. A clock stop or CI red traced to
  executor reasoning moves the next pass to `high` (Sonnet 5.5 page: "start at medium for
  well-specified tasks and move to high for harder or longer ones").
- Reserve `xhigh` and `max` for work where you've measured a quality gain (Opus 5.5 page). An
  unsettled decision re-runs at `xhigh`, then `max` (one session-only adjudication), then one
  `fable` dispatch, per dispatch and never a session switch or frontmatter pin. Reviewers take
  `claude-opus-5-5` from agent frontmatter. `haiku` reads and copies, never decides, and stays under
  100k context. `low` effort suits mechanical subagents, never Fable.

## Execute

One session executes. For an `ordinary` pass, the planning session starts it from the repo's main
checkout with `claude --bg --model sonnet --effort medium --name <project>-<pass> "$(cat <prompt
file>)"`, so Geoff pastes nothing.

Every executor is named `<project>-<pass>`, whoever launches it. `<project>` is the repo basename
the conductor's name uses, and `<pass>` is the plan's slug: `dubplate-intake-1`,
`cairn-cms-draft-docs-2b-part2`. Geoff finds a session in `claude agents` by that name and attaches
or sends to it, so a relaunch keeps the name (Geoff, 2026-10-12).

A `runner` or `auth-data` pass goes to Geoff for approval, so its planner hands it to the project's
conductor and closes instead of watching it (Geoff, 2026-10-12). Best practices for Claude Code
(<https://code.claude.com/docs/en/best-practices>): "Once the spec is complete, start a fresh session
to execute it." The conductor is `conductor-<project>`, where `<project>` is the basename of the repo
whose main checkout launches the executor. The planner commits `<plan>-conductor-prompt.txt` (see
"Launch prompt") and checks `claude agents --json` for a live `conductor-<project>`:

1. If none is listed, the planner launches it from that main checkout with `claude --bg --model
   claude-opus-5-5 --effort medium --name conductor-<project> "$(cat <file>)"` and closes.
2. If one is listed, the planner sends it the prompt file's absolute path with `SendMessage`, waits
   for its one-line reply naming the pass, and closes. A send that fails because the conductor
   just ended falls back to step 1.
3. If the conductor holds or refuses the message, or no reply comes within 10 minutes, the planner
   stays open, writes the stall into STATUS, and runs `notify-send -u normal`. It never launches
   the executor itself, which would put two watchers on one pass. Cross-session messaging
   (<https://code.claude.com/docs/en/cross-session-messaging>): a message is "Delivered", "Held", or
   "Refused", and a held one can expire unread.

Before the launch, every `## Pre-flight` item is done and checked (see "Lifecycle" step 4). Run
`git -C <repo> fetch origin` and check that the main checkout is on its
default branch and `git -C <repo> rev-list --count HEAD..origin/<default>` prints 0, since
`worktree.baseRef: "head"` branches from local `HEAD`. Where `git -C <repo> check-ignore -q
.claude/worktrees/x` fails, append `.claude/worktrees/` to the file `git -C <repo> rev-parse
--path-format=absolute --git-path info/exclude` names.

The session's first act is `EnterWorktree`, then the adapter's setup command in the new worktree.
It calls `EnterWorktree` only that once. Work in another repo or worktree goes by absolute path
and `git -C`, because an `EnterWorktree` made from another repo's worktree raises a permission
prompt that stalls the run (servers-foundation, 2026-10-19).
It commits without asking, pushes the branch it created, and opens the PR from it. A pass that
continues an existing branch merges or cherry-picks that branch into the new one first. STATUS
records the session's name and id. The launch prompt names the push target as `glw907/<repo>`, since
auto mode blocks a push to a repository the user did not name. The session arms the API-drop
wake-up (`/loop` with no interval) and, if the lid may close, the lid-switch hold, per
`~/.claude/docs/unattended-work-guards.md`, then reads, edits, writes the tests, and commits.

## Judgment calls

The plan answers the calls its run can foresee, and the session answers the rest and records them
in the PR. Mid-run, it takes its own recommendation without asking when the choice stays inside
the approved design, budget, and path ceiling and can be undone after the merge. Each such call
goes in the PR body's `## Decisions` section: the call, the choice, the alternative, and the
reason. The session stops for Geoff only on spend past the budget, an irreversible or destructive
act, a secret, a change of scope or design, a product or taste call the design leaves open, a
stop the plan writes once its standing answer runs out (see "Lifecycle" step 1), or a clock stop. In the three days to 2026-10-19, Geoff took the recommended option on 24 of 36 questions, five of
them mid-run calls inside approved scope. Prompting Claude Opus 5
(<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>):
"Make routine judgment calls yourself, and check in only when different readings of the request
would lead to materially different work."

A mid-run question to Geoff is a planning miss, even when the session had to ask. Some will
happen, and each one improves the planning step that missed it. The session that asked records
the miss in the PR body's `## Planning misses` section: the question, Geoff's answer, and the plan
item that should have answered it. Under a conductor, the conductor is that session: it adds the
entry and the fix after the executor reports PR-ready and before its packet. Before the hand-over
the session lands the fix where planning executes,
usually a new item in the `plan-reviewer` checklist, else the adapter or this skill. The fix goes
in the same PR when it is in this repo, and otherwise in a dotfiles PR the packet names. A miss
the fix cannot generalize stays in the PR body, marked one-off.

A stop has one asker. An executor whose pass has a conductor never asks Geoff itself: it writes
the stop to STATUS and waits, with no `notify-send`. The conductor asks once, commits the ruling
to the plan branch, then stops and relaunches the executor per "Conductor", which merges the plan
branch first (2026-10-19: both sessions asked Geoff B3c's read-cap question).

## Pairs

Two tasks whose files are disjoint, generated outputs included, go to two Agent-tool subagents
with `isolation: "worktree"` after the session commits, each with the `description` `<pass> task
<n>` so the session's agent list shows which task each runs; `worktree.baseRef: "head"` branches
them from that commit. A shared port is an environment variable. Each runs the adapter's setup command
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
`notify-send -u normal`, and waits for Geoff (one attended event, not a failure). Under a
conductor, the executor writes STATUS and waits, and the conductor asks per "Judgment calls". A resume rewrites
`start=`, or `estimate=` to the figure Geoff names. Pair worktrees hold no clock file, so the stop
cannot fire while the session waits on a pair.

## Conductor

The conductor is the session that runs between passes. One runs per project, named
`conductor-<project>` (see "Execute"), and it owns every PR its passes open, merged in the order its
prompt names. Its first act is the API-drop wake-up (`/loop` with no interval) and, if the lid
may close, the lid-switch hold, per `~/.claude/docs/unattended-work-guards.md`, as an executor's
are (Geoff, 2026-10-12). It watches unattended passes with the Monitor tool over `claude agents
--json --all`, which keeps a background session listed after its process exits. The Monitor event
is the primary signal; each fallback tick re-arms the Monitor and checks the pass's sessions and
PRs, since an event lost to an API drop leaves the conductor asleep. At each decision point it sends one packet for the PRs and designs it holds, never one per
executor PR, per `approval-packet`. It merges and pulls the checkout per "Close" after he approves, and launches
the next committed prompt from the main checkout after the "Execute" pre-launch checks. For a pass
it owns, the conductor is the session that hands the packet over in "Close", so the executor's prompt
ends at PR-ready and never runs `approval-queue`. It brings Geoff only packets and product
or priority calls.

An executor refuses the conductor's cross-session messages, rightly: a peer's message carries no
approval from Geoff. When an executor stops on a cause the conductor can fix, the conductor fixes
it at the source (the plan branch, a merge from the default branch), then stops and relaunches the
executor; otherwise Geoff attaches to it. The conductor never calls `EnterWorktree`, because the
isolation would apply to its subagents too; it edits a worktree by path instead.
A watch over `claude agents --json --all` reads each field with `.get`, since a row can lack `id`.
While a planner is out, the conductor merges no STATUS edit to the default branch, because the
executor's merge of the plan branch then conflicts in STATUS (twice on 2026-10-11); it batches its
STATUS changes into the hand-over after that pass lands (conductor `4bea6e68`, 2026-10-11).

On a hand-off message, the conductor replies with one line naming the pass before anything else.
It ends when no pass it owns is open (each PR merged or closed, the packet's decision acted on, the checkout
pulled or reported stale) and its project's STATUS names no launch prompt waiting for it. Its last
acts are the STATUS hand-over (see "Ledgers") and `claude stop <id>`, taking `<id>` from its own row
in `claude agents --json`. An idle conductor stays listed and keeps its name, so the next planner
would hand a new pass to a session carrying the last initiative's context.

## Close

The repo's full-suite home is green on the head. One whole-branch Opus review follows:
`diff-reviewer` at whole-branch scope loads the checklists the adapter's globs match, re-derives
each task's class, and gives any unread `auth-data` task its read. `visual-verifier` runs on
rendered UI in a site or the cairn admin. One batched fix chain follows, then the gate again; a
second review only on a blocker. A fix dispatch quotes each reviewer finding verbatim (location,
finding, and fix) as the task's acceptance criteria, never a summary. In dubplate, verbatim criteria
landed at zero fix rounds and paraphrased ones averaged one. An overruled verdict is stated with its
reason in the PR body, and a correctness-critical overrule re-runs the review at `xhigh`. The
adapter's close checklist runs (the auth smoke on `auth-data`), STATUS is updated, and
the PR body opens with a `## Brief` per `~/.claude/docs/voice/approval-brief.md` and carries,
below it, what landed, each `auth-data` verdict, the `## Decisions` and `## Planning misses`
sections (see "Judgment calls"), and the score. Each "Found, not done" item worth doing is
filed through `log-issue` in its repo's `BACKLOG.md`, tagged `#initiative:<id>` when a record fits,
and listed in the PR body with its backlog number; an item not worth doing stays in the PR body,
marked dropped. No follow-up is sent to Geoff as its own item, and an initiative-sized one becomes a
record. A merged PR body is history no session reads (Geoff,
2026-10-11: dubplate PR #2 left 14 items there).

When the work is ready for Geoff's read, the session that hands it over sends one packet with
`approval-queue packet <initiative> <file>`, following `approval-packet`, and stays open until the
command exits with Geoff's decision as JSON. An approve is Geoff's merge authorization for each part
whose verdict is `approve`, the authorization a launch prompt's "never merge" otherwise withholds:
the session merges as `approval-packet` step 7 sets out, with `--match-head-commit <head>` taken
from the decision, and pulls the checkout as below. On reject, it fixes forward from the note. A
pass that merges its own PR sends nothing (Geoff, 2026-10-11). `approval-queue triage` survives
only for an explicit backlog triage.

A pass whose highest class is `ordinary` merges its own PR with `gh pr merge <n> --merge` after a
green full-suite home and an accepted whole-branch review. Its follow-ups go to `BACKLOG.md` and the
PR body as above, never to a packet (Geoff, 2026-10-17). A `runner` or `auth-data` pass sends a
packet for Geoff's read and merge. An
adapter line that says every PR waits for Geoff yields to this exception.

A PR must be safe under a plain merge followed by a pull; the executor makes it so where it can.
When it cannot, the PR body carries a `## Before merge` section: the exact commands in order and
the one check that shows they ran. `claude-merge-guard` refuses `gh pr merge <n>` until the
command is prefixed `PREMERGE_DONE=<n>`, after the merger has run those steps. The packet raises the
section as an ask naming the PR, and the choice picked says who runs them: "The session runs it, then merges" sends the session through the steps and then
the merge; "I'll run it myself" means the session does not merge, and it reports that Geoff runs
the steps and will say when they are done. A `[approve]` choice on a failed check or a fix review
means merge as approved.

Whoever merges a PR then brings that repo's main checkout up to date: `git -C <checkout> pull
--ff-only` when the checkout is on its default branch, has no uncommitted change in a file the
merge touches, and has no live session (`claude agents --json`). Otherwise it reports the checkout
as stale and never forces it. A stale checkout loads the old CLAUDE.md and skills into the next
session there: on 2026-10-11 six repos still ran the pre-cutover process a day after their lean
PRs merged.

## Score

The PR body carries the spec's price table rows: Gates on the critical path, Work and review, CI
waits on the path, Fix rounds and reds, Close, and Total. Gate and lock time come from
`cairn-run-gate --records <toplevel> <branch>`; the clock runs from the first execution commit to
PR-ready. The Work and review row names the plan's path minutes beside the actual, the figure the
next design's estimate is set from. It lists the attended events (the design, the packet read, one per clock stop, and one per
mid-run question, which names the plan item that should have answered it) and any escape,
a behavioral, security, or contract defect that surfaces through the next pass's close, CI on
`main`, or Geoff's use; an escape also goes into STATUS with its commit. A miss names its row, or
the step that should have caught the escape, and only that changes.

## Ledgers

`docs/STATUS.md` is present tense and 60 lines or fewer: current state, next action, open
decisions. Initiatives are records in the initiatives repo, managed by `/log-project`; a repo's own backlog is `BACKLOG.md`. A commit id cited in a ledger is one that survives a merge: a merge commit, or an
id on the default branch, since a squash or rebase rewrites ids. Git and PR bodies are the history;
`docs/HISTORY.md` and post-mortems stop growing (ruling 8). A lesson lands where it executes: a skill, agent, tool, or repo doc. Memory holds only a
preference or a ruling's why that no file can.

A hand-over (the STATUS update, the next session's launch prompt, and the research records it
carries) changes no behavior, so it is never brought to Geoff as a PR (Geoff, 2026-10-11). The
handing-over session commits it on a branch, runs the gate, opens the PR, and merges it itself with
`gh pr merge <n> --merge`, then pulls the checkout. Best practices for Claude Code
(<https://code.claude.com/docs/en/best-practices>): "For tasks where the scope is clear and the fix
is small ... ask Claude to do it directly."

## Scope

A grant authorizes a mechanism or a boundary, never more work. Work found mid-task is filed in BACKLOG through `log-issue` and listed in the PR body, never sent to the packet as an item, never put into the task in flight, unless the task would
otherwise build on something known to be wrong (say so then).

## Launch prompt

A STATUS next action carries the goal, the scope, the plan path, the checkout, and the exact
`claude` line. The prompt text lives in a committed file and is launched as `"$(cat <file>)"`,
since a prompt pasted inside double quotes runs each backticked span as a command substitution.
The prompt for a pass that hands its PR over says the session sends its packet through `approval-packet`, waits for the decision, merges only a part Geoff approved with `--match-head-commit`, and ends after acting on the decision; it never
says "never merge" or "end" outright. Close the session when the initiative lands.

A conductor prompt opens with one line naming the session `conductor-<project>`, then carries the
executor's `claude` line and its prompt file; the plan path and each repo and checkout the pass
touches; the merge order across its PRs, with any `## Before merge` steps known at plan time; the
standing answers from the design; and what goes in its packet to Design & PR Approvals. It restates nothing this skill
already says. Prompting Claude Opus 5
(<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>):
the model "performs best when given the complete task specification up front and left to run".
