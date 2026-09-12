# Claude infrastructure round: the workstation layer, sized to what recurs

**Status:** revision 1, drafted 2026-09-12 against `~/.dotfiles` at commit `9034fd3`
("docs: record the Claude infra round's cross-project survey and scope ruling"). Awaiting
Geoff's approval. Not yet executed.

> **For agentic workers:** this plan runs through
> `~/.claude/workflows/pass-execute.js` for segments A and B, and through per-task Agent-tool
> chains in the main loop for segment C. Each task below carries its own Files, outcomes, and
> acceptance criteria, and the plan section is the authority over any condensed criteria string
> in a dispatch. Do not read another task's section. Do not `git add -A` in any repo. Do not
> touch `claude/.claude/agents/cairn-implementer.md`; a live cairn session owns that file.

**Goal:** land the seven workstation items the 2026-09-12 cross-project survey ruled in scope,
so that every repo that consumes a shared implementer, guard doc, workflow runner, agent, or
site asset reads one correct copy instead of two stale ones.

**Spec:** `docs/superpowers/research/2026-09-12-claude-infra-round-survey.md`, sections "The
ruling", "Out of scope, recorded for the repo that owns each", and "Constraints on execution".
The ruling is fixed. This plan splits and merges its items into tasks and re-litigates none of
them.

**Repos written:** `~/.dotfiles` for every task. `~/Projects/dubplate` for two files (task 1
and task 4). `~/Projects/907-life` and `~/Projects/ecxc-ski` for six retired duplicate files
(task 3). Nothing is written in `~/Projects/cairn-cms`, `~/Projects/poplar`, or any other repo.

**Format exemplar:** `docs/superpowers/plans/2026-09-08-docs-standard-claude-infra.md`, the
previous infra plan in this repo, whose executor precedent this plan inherits.

---

## Drafter's pre-flight (staleness is the drafter's job, and Task 0 runs no gate)

Every path, byte count, and line reference below was verified at `9034fd3` during drafting. The
pre-flight also produced five corrections that change what the tasks can claim.

**Tree state.** `git -C ~/.dotfiles log -1 --format=%h` reports `9034fd3`.
`git -C ~/.dotfiles status --short` reports exactly one line, `M
claude/.claude/agents/cairn-implementer.md`, the cairn session's warm file. HEAD moved once
during drafting, from `d2c4831` to `9034fd3`, when the conducting session committed the survey
document; no task's Files were affected.

**Executor check.** `pgrep -af dotfiles` returns only the checking shell. Resolving each
candidate's `/proc/<pid>/cwd` leaves no process with a working directory under `~/.dotfiles`.
`git -C ~/Projects/dubplate worktree list` reports one worktree at `3c766b3`, and no process
holds it; 5b-ii has not launched. `~/Projects/907-life` and `~/Projects/ecxc-ski` are each one
clean worktree with no live executor.

**Correction 1: no task in this round needs `stow -R claude`.** All five relevant directories
under `~/.claude` are folded whole-directory symlinks into the stow source: `agents`, `docs`,
`skills`, `instructions`, and `workflows` each `readlink` to
`../.dotfiles/claude/.claude/<name>`. A new file inside any of them is live machine-wide the
instant it is written. Each task that adds a file proves the symlink with `readlink -f` rather
than resting on a restow. Running `stow -R claude` is harmless and may be run; it is not the
proof, and a task that reports it in place of the `readlink` proof has not met its criteria.

**Correction 2: the gate reads almost nothing this round writes.** `bash scripts/check.sh` has
six legs (`scripts/check.sh:37-42`): `bash -n` over tracked files whose shebang names bash, the
tellgrader module's `make check`, `scripts/check-py-comments.sh` for ruff docstring rules, the
vale-hook pytest suite, `tests/vale/run-fixtures.sh`, and `gitleaks dir . --no-banner
--redact`. There is no shellcheck leg, and the vale leg runs against fixtures inside
`tests/vale/` rather than against repository markdown. So a markdown-only task is gated by the
gitleaks working-tree scan alone, with the other five legs proving only that nothing collateral
broke. Every markdown task below therefore carries its own proof in its acceptance criteria,
and a green gate is never offered as evidence that the prose is correct.

**Correction 3: the four ranked displacement candidates no longer clear the budget.**
`claude/.claude/CLAUDE.md` measured 23,995 bytes when
`docs/superpowers/plans/2026-09-08-claude-md-displacement-candidates.md` ranked them. It now
measures 27,807 bytes, after `08c132a` and `d2c4831` baked in the pass gate-economy rulings.
The arithmetic is in task 6. The four ranked picks fall about 1,000 bytes short, so task 6
carries a fifth pick measured during this drafting.

**Correction 4: two of the four ranked picks need no new destination document.**
`claude/.claude/docs/cloudflare-estate-inventory.md` already names the account id twice and
already carries the ASC Access service-token route (`:40`). `secrets/registry.md` already
carries the whole `secret-set.sh` flow (`:74`, `:85-99`), including `--value`, `--file`,
`--b64-file`, and `sync.sh --worker NAME`. Both picks shrink to a pointer with no text moved.

**Correction 5: every diverging line in the two duplicated site instruction files is drift, not
a repo fact.** The survey recorded "one repo-specific deploy command differs". Reading both
pairs proves otherwise, and task 3 records the evidence. `907-life`'s
`ai-operational-rules.md:38-42` still names `hugo --minify` and a `public/` build directory,
while `907-life/package.json:7` builds with `vite build` and `907-life/CLAUDE.md:112` gives the
same SvelteKit deploy command `ecxc-ski` carries. That hunk is stale text. `907-life`'s
`ai-operational-rules.md:19` carries a `RESEND_API_KEY` example, and grepping both source trees
finds Resend in `ecxc-ski/src` and nowhere in `907-life/src`, so the example sits in the wrong
repo and duplicates the `CF_TOKEN` line's pattern. Every remaining hunk in both files is line
wrapping, punctuation, or phrasing. `907-life/.claude/skills/svelte-check/SKILL.md` and
`ecxc-ski`'s are byte-identical at 1,748 bytes.

---

## Global constraints (every task)

- **`claude/.claude/agents/cairn-implementer.md` is off-limits to every task.** The cairn
  overnight session authored its working-tree diff and owns its commit. Never stage it, never
  revert it, never read its diff as anything but the wording template task 1 copies. Its diff
  is warm in `git status` and must still be warm when this round ends.
- **Edit stow sources under `~/.dotfiles/claude/.claude/`, never the `~/.claude/` symlinks.**
- **Every write under `claude/.claude/` is live in every session on this machine at the moment
  of the write**, with no restow and no staging. Each task touching that tree names in its
  report what a session in another repo now sees differently, and states the one-line revert
  (`git -C ~/.dotfiles checkout -- <path>`).
- **Commit specific files, never `git add -A`, in any repo.** One commit per task per repo. A
  task writing two repos makes two commits and reports both SHAs.
- **Commit footer**, in every repo, two lines, the model name and session URL being the
  executing session's own:

  ```
  Co-Authored-By: Claude <model> <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_<id>
  ```

  The form is verified from `git -C ~/.dotfiles log -3` and `git -C ~/Projects/dubplate log
  -3`, which agree.
- **A task starts only when none of its own Files appears in that repo's `git status
  --short`.** A warm file you did not author is a stop-and-report signal, never free progress.
- **Register:** every file this round writes is agent-facing, so it follows
  `~/.claude/docs/voice/agent-facing.md`. No em dashes anywhere. One idea per sentence. State
  the reason with the rule. State done in checkable terms.
- **No task invents a fact.** Where a task must write wording, this plan names the source the
  wording comes from. Where the source does not settle a detail, report it in
  `unspecifiedDecisions` rather than filling the gap.
- **Gate:** `cairn-run-gate 'bash scripts/check.sh'` from `~/.dotfiles`, re-issued on exit 75
  until it prints `gate exit:`. Never run the gate with `run_in_background` and never poll its
  log. A red gate is never committed.

## Executor and execution mode

Fixed by the survey's "Constraints on execution" and the 2026-09-08 plan's precedent
(`:112-118`). The dotfiles repo has no repo-specific implementer agent.

| Role | Agent | Model |
|---|---|---|
| Implementer | `general-purpose` | `sonnet` |
| Reviewer | `diff-reviewer` | `claude-opus-5` |

Eight dispatched tasks means `pass-execute` mode, and this plan names it. Segments A and B run
through `~/.claude/workflows/pass-execute.js`, one invocation per segment, because the runner
has no mid-run conductor hook. **Segment C runs as per-task Agent-tool chains in the main
loop**, because task 7 edits `pass-execute.js` itself and a runner cannot safely rewrite the
script executing it.

## Contested surfaces

| Surface | The cairn session may write | This round writes |
|---|---|---|
| `claude/.claude/agents/cairn-implementer.md` | yes, and owns its commit | **never** |
| `claude/.claude/workflows/pass-execute-chains.js` | yes, it is the cairn variant | never |
| `claude/.claude/skills/cairn-pass/SKILL.md` | yes | never |
| `claude/.claude/skills/register-check/SKILL.md` | yes | never |
| `claude/.claude/workflows/pass-execute.js` | it may be **running** one | task 7, after the precondition check below |
| `claude/.claude/agents/site-implementer.md` | no | task 1 |
| `claude/.claude/agents/diff-reviewer.md` | it may be **dispatching** it | never; this round does not edit the reviewer |
| `claude/.claude/docs/unattended-work-guards.md` | no | task 2 |
| `claude/.claude/CLAUDE.md` | no | task 6 |
| `claude/.claude/docs/model-economy.md` | no | task 5 |

Task 7's precondition: before editing `pass-execute.js`, confirm no live workflow run is
executing it. A cairn session mid-run holds `pass-execute-chains.js`, a different file, so the
check is for `pass-execute.js` alone. If a run holds it, task 7 reports blocked and the
conductor defers it.

## Budget

**Ceiling 1.0M tokens.** No actual is available to derive from.
`docs/HISTORY.md`'s 2026-09-08 entry records the previous infra plan's **ceiling** of 0.6M and
says only that "the pass closed inside it by the per-task reports", with no measured number, so
the derivation is from task count at a stated rate.

The rate comes from that same plan: 0.6M over seven dispatched tasks is about 0.086M per task,
in this repo, with this implementer, reviewer, and gate. This round rounds that to **0.1M per
dispatched task**, because two of its tasks write a second repo and every task pays one Opus
reviewer read. Eight dispatched tasks at 0.1M is 0.8M, plus a 0.2M conductor reserve for the
two `pass-execute` invocations, the three checkpoints, and the fold.

At 80% of the ceiling (0.8M), finish the running task, write STATUS, and ask one combined
question. Check that flag at each segment boundary, the only place a decision can land.

**Checkpoint interval: three tasks**, set below the default of four so that every checkpoint
falls on a segment boundary. Checkpoints land after task 3, after task 6, and at the close.

**Split point, if the round runs past its ceiling: task 6, whole.** It is the only task with no
dependent. Cutting it leaves the CLAUDE.md file over budget exactly as it is today, which is
the pre-round state, and leaves no other edge to repair.

## Segments

Each segment ends on a commit the gate proved green.

| Segment | Tasks | How it runs | Ends on |
|---|---|---|---|
| A | 1, 2, 3 | `pass-execute`, one invocation | task 3's dotfiles commit, gate green |
| B | 4, 5, 6 | `pass-execute`, one invocation | task 6's commit, gate green, `claude-context-budget` green |
| C | 7, 8 | per-task Agent-tool chains in the main loop | task 8's draft commit, then the conductor's fold |

Segment C is two tasks rather than three. The override is named by the rule: task 7 edits the
runner, so it cannot run inside a `pass-execute` invocation, and task 8 is the close, whose
Files are disjoint from every other task's.

---

### Task 0: Coordination check (conductor, no dispatch, no gate)

**Model:** none, the conductor runs it. **Depends on:** nothing. **Deliverables:** 1.
**Independent:** yes.

**Files:** none. This task writes nothing.

**Outcome.** The round starts against a tree whose state matches this plan's pre-flight, and the
lane has one recorded green baseline.

Per the gate-economy rule, a read-only staleness pre-task runs no gate of its own. The lane's
baseline is the conductor's own single `cairn-run-gate 'bash scripts/check.sh'` call at launch,
quoted to every reviewer as Task 0's gate evidence.

**Acceptance criteria.**

1. `git -C ~/.dotfiles status --short` lists no path that appears in any task's Files. One
   warm line, `claude/.claude/agents/cairn-implementer.md`, is expected and is not a blocker.
2. No process has a working directory under `~/.dotfiles`, proved by resolving
   `/proc/<pid>/cwd` for each `pgrep -f dotfiles` hit and excluding the checking shell.
3. `~/Projects/dubplate`, `~/Projects/907-life`, and `~/Projects/ecxc-ski` each report one
   worktree, a tracked-file-clean `git status --short`, and no live executor.
4. One `cairn-run-gate 'bash scripts/check.sh'` run in `~/.dotfiles` prints `gate exit: 0`,
   and that line is recorded as the lane baseline.

---

### Task 1: The exit-75 reattach protocol in the two implementers that lack it

**Model:** `sonnet`. **Depends on:** task 0. **Deliverables:** 2. **Independent:** yes.

**Files:**

- Modify: `claude/.claude/agents/site-implementer.md` (the gate paragraph at `:89-91`)
- Modify: `/var/home/glw907/Projects/dubplate/.claude/agents/dubplate-implementer.md` (step 5
  at `:68-71`, and the `description` frontmatter at `:3` where it calls the runner "blocking")

**Outcome.** Both implementer definitions describe what `cairn-run-gate` actually does, so an
implementer dispatched by either one re-issues the command on exit 75 instead of treating a
75 as a gate failure or reaching for a background poll.

**Constraints.**

- The wording source is the uncommitted working-tree diff of
  `claude/.claude/agents/cairn-implementer.md`, which the cairn session authored at 04:50 on
  2026-09-12. Read that diff with `git -C ~/.dotfiles diff
  claude/.claude/agents/cairn-implementer.md` and adopt its replacement paragraph, adjusting
  only the domain nouns each file needs. Never stage, commit, or alter that file.
- The behavior the wording must carry, verified against `bin/.local/bin/cairn-run-gate:1-14`:
  the runner starts the gate detached keyed by the gate string and the working directory; it
  blocks up to `CAIRN_GATE_WAIT` seconds, default 540; it prints "gate still running" and exits
  75 when the window expires; the caller re-issues the same command, which reattaches and waits
  again; a finished gate prints its exit status and the last 60 lines once, then clears.
- Keep every existing instruction in both files that the paragraph does not replace. This is a
  correction to one paragraph each, not a rewrite.
- `dubplate-implementer.md`'s step 5 currently claims "one call gives you one result". That
  claim is the defect. Its neighboring rules against tailing, sleeping, and polling stay.
- The Bash call shape the template names (`timeout: 600000`, a plain foreground call) is part
  of the adopted wording.

**Commits.** Two, one per repo, each staging only that repo's file, each with that repo's
footer form. The dubplate edit is committed in dubplate by this task.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. Neither modified file contains the string "blocks to completion" any longer, and neither
   contains "one call gives you one result".
2. Each modified file states all four of: exit 75 means still running; the caller re-issues the
   same `cairn-run-gate` command; the loop ends when the runner prints the gate exit and the
   tail; the re-issue is the only permitted wait, with `run_in_background` and log polling
   forbidden.
3. The replacement paragraph in each file is recognizably the cairn template's wording, with
   only domain nouns differing. The reviewer compares against `git -C ~/.dotfiles diff
   claude/.claude/agents/cairn-implementer.md`.
4. `git -C ~/.dotfiles status --short` still shows `claude/.claude/agents/cairn-implementer.md`
   as modified and unstaged, unchanged in content from the drafting-time diff.
5. `git -C ~/.dotfiles show --name-only HEAD` names exactly `site-implementer.md`, and `git -C
   ~/Projects/dubplate show --name-only HEAD` names exactly `dubplate-implementer.md`.
6. Both files' YAML frontmatter still parses, `name` still matches the filename stem, and
   `readlink -f ~/.claude/agents/site-implementer.md` resolves into
   `~/.dotfiles/claude/.claude/agents/`.
7. `cairn-run-gate 'bash scripts/check.sh'` in `~/.dotfiles` prints `gate exit: 0`. This is a
   markdown-only change, so the gate proves only that nothing collateral broke; criteria 1
   through 6 are the proof.

**Note.** `~/Projects/poplar/.claude/agents/poplar-implementer.md` runs `make check` directly
and never calls the runner. It is out of scope by the survey's ruling and is recorded below.

---

### Task 2: The two corrections the unattended window proved in the guards doc

**Model:** `sonnet`. **Depends on:** task 0. **Deliverables:** 2. **Independent:** yes.

**Files:**

- Modify: `claude/.claude/docs/unattended-work-guards.md` (the runaway-guard paragraph, and the
  battery-watchdog clause inside the battery-floor paragraph)

**Outcome.** A session arming either guard from this doc arms one that works. Today the doc
sends the runaway guard past the one signal that tells a finished chain agent from a stalled
one, and sends the battery watchdog to a file that lies on AC.

**Constraints.** Both corrections come from the dubplate window's recorded findings in
`~/.claude/projects/-var-home-glw907-Projects-dubplate/memory/unattended-window-2026-09-12.md`,
section "What the window learned (do not rediscover)". Write each correction with its
mechanism, because the register requires the reason beside the rule and the mechanism is what
stops the next session from reverting it.

- **Correction A, the runaway guard.** The doc currently says `journal.jsonl` "only records
  agent starts and finishes, so a long-running task looks idle there; poll the agent
  transcripts". The finding: the guard **must** read each workflow's `journal.jsonl` for
  completed agents, or every finished chain agent reads as a stall. The corrected rule keeps
  the agent-transcript poll for the idle and size signatures, and adds the journal read as the
  completion filter, so a stall alarm fires only for an agent the journal has not recorded as
  finished. Keep both existing signatures, the 25-minute idle threshold, the 900KB growth
  threshold, and the TaskStop plus `resumeFromRunId` intervention.
- **Correction B, the battery layer.** The doc currently polls
  `/sys/class/power_supply/BAT*/{capacity,status}` and triggers "at 11% while `Discharging`".
  The finding: the battery reports "Not charging" on AC under the charge threshold, so a
  `status`-based discharge test is wrong. The corrected rule gates on
  `/sys/class/power_supply/AC*/online`, treating the watchdog as armed-and-silent whenever that
  file reads 1. Keep the 11% trigger, the 2-minute poll interval, the "silent on AC by design"
  intent, and the whole stand-down sequence.
- Do not change the sleep-inhibitor rules, the restart-recovery checklist, or the
  concurrent-sessions section.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. The file no longer instructs a reader to disregard `journal.jsonl`, and states that the
   runaway guard reads each workflow's `journal.jsonl` for completed agents before alarming.
2. The file states the mechanism for correction A: without the journal read, every finished
   chain agent reads as a stall.
3. The file no longer gates the watchdog on `BAT*/status`, and names
   `/sys/class/power_supply/AC*/online` as the AC test.
4. The file states the mechanism for correction B: the battery reads "Not charging" on AC under
   the charge threshold.
5. Both existing runaway signatures, the 11% trigger, and the full stand-down sequence survive
   the diff. The reviewer names any removed rule as a blocking finding.
6. No em dash appears in the diff.
7. `cairn-run-gate 'bash scripts/check.sh'` prints `gate exit: 0`. Markdown-only, so criteria
   1 through 6 are the proof.

---

### Task 3: One workstation home for each duplicated site asset

**Model:** `sonnet`. **Depends on:** task 0. **Deliverables:** 4. **Independent:** yes.

**Files:**

- Create: `claude/.claude/skills/svelte-check/SKILL.md`
- Create: `claude/.claude/instructions/ai-operational-rules.md`
- Create: `claude/.claude/instructions/documentation-standards.md`
- Delete: `/var/home/glw907/Projects/907-life/.claude/skills/svelte-check/SKILL.md`
- Delete: `/var/home/glw907/Projects/907-life/.claude/instructions/ai-operational-rules.md`
- Delete: `/var/home/glw907/Projects/907-life/.claude/instructions/documentation-standards.md`
- Delete: `/var/home/glw907/Projects/ecxc-ski/.claude/skills/svelte-check/SKILL.md`
- Delete: `/var/home/glw907/Projects/ecxc-ski/.claude/instructions/ai-operational-rules.md`
- Delete: `/var/home/glw907/Projects/ecxc-ski/.claude/instructions/documentation-standards.md`

**Outcome.** Three assets that were maintained twice are maintained once. The retirement of the
repo copies is required rather than optional for the skill: a repo-local skill shadows the
workstation one, so leaving `907-life`'s and `ecxc-ski`'s copies in place would make the hoist a
no-op in exactly the two repos it serves.

**Constraints, and which body each hoisted file takes.**

- `svelte-check/SKILL.md`: the two repo copies are byte-identical at 1,748 bytes. Hoist
  verbatim. Its body names `npm run check` and no repo-specific path, so it is correct for
  every SvelteKit repo on this machine.
- `ai-operational-rules.md` and `documentation-standards.md`: **take `ecxc-ski`'s copy as the
  hoisted body**, because Correction 5 in the pre-flight proves every hunk where the two differ
  is drift, and `ecxc-ski`'s side of each divergent hunk is the correct or equivalent one. The
  implementer verifies that finding before hoisting and reports disagreement in
  `unspecifiedDecisions` rather than choosing differently in silence.
- **No repo pointer is needed for the two instruction files.** Grepping both repos for
  `ai-operational-rules` and `documentation-standards` across `*.md`, `*.json`, and `*.js`
  returns no reference outside the files themselves. Neither repo's `CLAUDE.md` names them.
  They are reached by an agent reading the path, and hoisting does not change that.
- Do not edit either repo's `CLAUDE.md`. Do not touch
  `907-life/.claude/instructions/css-rules.md`, which has one consumer and is recorded below.
- Add nothing to any hoisted body and remove nothing from it beyond the drift hunks the chosen
  side already settles.

**Commits.** Three, one per repo, each staging only that repo's paths.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. `diff claude/.claude/skills/svelte-check/SKILL.md <either retired repo copy at its parent
   commit>` is empty, and the hoisted file is 1,748 bytes.
2. Each hoisted instruction file is byte-identical to `ecxc-ski`'s retired copy at its parent
   commit, proved with `git -C ~/Projects/ecxc-ski show HEAD~1:.claude/instructions/<name> |
   diff - <hoisted path>`.
3. The hoisted `ai-operational-rules.md` contains neither `hugo --minify` nor `RESEND_API_KEY`,
   the two stale hunks Correction 5 names.
4. All three hoisted files resolve through the folded symlinks, proved with `readlink -f
   ~/.claude/skills/svelte-check/SKILL.md`, `readlink -f
   ~/.claude/instructions/ai-operational-rules.md`, and `readlink -f
   ~/.claude/instructions/documentation-standards.md`.
5. `ls ~/Projects/907-life/.claude/skills/svelte-check ~/Projects/ecxc-ski/.claude/skills/svelte-check`
   fails, and `907-life/.claude/instructions/` still contains `css-rules.md` and nothing else.
6. The `svelte-check` skill's frontmatter `name` is `svelte-check` and its `description` still
   names SvelteKit files, so it cannot mis-trigger in the Go repos where it is now visible.
7. Each of the three commits names only its own repo's paths under `--name-only`, and no commit
   used `git add -A`.
8. `cairn-run-gate 'bash scripts/check.sh'` prints `gate exit: 0`.

**Note.** The `ship` skill exists in both `aksailingclub-legacy` and `ecxc-ski` with diverged
bodies. The survey ruled it a note, not a task. It is recorded below.

---

### Task 4: Hoist `go-architecture-reader` to the workstation agents

**Model:** `sonnet`. **Depends on:** task 0. **Deliverables:** 2. **Independent:** yes.

**Files:**

- Create: `claude/.claude/agents/go-architecture-reader.md`
- Delete: `/var/home/glw907/Projects/dubplate/.claude/agents/go-architecture-reader.md`

**Outcome.** Both Go repos on this machine reach the same package-grading agent. dubplate keeps
the behavior it has; poplar gains an agent it lacked.

**Constraints.**

- Hoist the body verbatim from dubplate's copy, 5,260 bytes. It names nothing
  dubplate-specific: its stdlib comparator is chosen by the agent at read time and its dispatch
  contract names the package path only.
- Change no frontmatter field, including `model: opus` and `effort: high`. Normalizing the
  model pin is a separate decision and is not this round's.
- The retirement is committed in dubplate by this task, with dubplate's footer form. No
  dubplate executor is live, verified in task 0.
- dubplate's `CLAUDE.md` names `go-architecture-reader` in its Reviewers section. That
  reference is by agent name, not by path, and stays correct after the hoist. Do not edit
  dubplate's `CLAUDE.md`.

**Commits.** Two, one per repo.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. `git -C ~/Projects/dubplate show HEAD:.claude/agents/go-architecture-reader.md` at the
   parent commit diffs empty against `claude/.claude/agents/go-architecture-reader.md`, and the
   hoisted file is 5,260 bytes.
2. `readlink -f ~/.claude/agents/go-architecture-reader.md` resolves into
   `~/.dotfiles/claude/.claude/agents/`.
3. The hoisted frontmatter carries `name: go-architecture-reader`, `tools: Read, Grep, Glob,
   Bash`, `model: opus`, and `effort: high`, unchanged.
4. `ls ~/Projects/dubplate/.claude/agents/go-architecture-reader.md` fails, and
   `~/Projects/dubplate/.claude/agents/dubplate-implementer.md` still exists.
5. Each commit names exactly one path under `--name-only`.
6. `cairn-run-gate 'bash scripts/check.sh'` prints `gate exit: 0`.

---

### Task 5: The one carried 2026-09-04 item that is a workstation edit

**Model:** `sonnet`. **Depends on:** task 0. **Deliverables:** 2. **Independent:** yes.

**Files:**

- Modify: `claude/.claude/docs/model-economy.md` (the `## Fable 5.1 (noted 2026-09-04)` section
  at `:165-173`)
- Modify: `claude/.claude/docs/fable-post-cutoff-system.md:12`

**Outcome.** The model-economy doc records the 5.1 economics and the decisions taken, closing
the one carried item from the 2026-09-04 Fable 5.1 pass that is a workstation edit and whose
blocker has cleared.

**The three carried items, named from `docs/HISTORY.md`'s 2026-09-04 entry and the pre-prune
STATUS at `7c7626c`:**

1. **Plan task 3, the model-economy doc update.** It waited on another session's uncommitted
   edit to the same file. That blocker is cleared, recorded in HISTORY as commit `3345620`, and
   `git status --short claude/.claude/docs/model-economy.md` is empty today. **This is the
   workstation edit, and it is this task.**
2. **The site-pass experiment's verdict**, to be recorded in `docs/HISTORY.md` when the next
   `ecxc-ski` or `907-life` pass closes. Not a workstation edit available now; the input is
   another repo's pass numbers. Recorded below.
3. **The first monthly model review, due 2026-10-01**, from the checklist in
   `docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md`, with
   `model-review.timer` raising the reminder. Date-gated and already an Active ROADMAP entry.
   Recorded below.

**Constraints.**

- The wording source is
  `docs/superpowers/plans/2026-09-04-fable-5-1-infra-update.md`, task 3, steps 1 onward, which
  carries the replacement clause, the section body, the price and benchmark table, the
  decisions-taken subsection, and the behavior-deltas subsection. Follow it as written.
- The section exists today with `grep -c '^## Fable 5.1'` returning 1, so step 1's first branch
  applies: replace the clause "unpinned subagents inherit the session model, so they follow the
  switch automatically" with the clause the plan names, then rewrap the paragraph.
- No `###` subsection exists under that heading today, so every subsection the plan's later
  steps append is genuinely new.
- The plan's task 3 instructs a one-time fetch to confirm three figures before staging, and to
  report a mismatch as could-not-do rather than writing a number that does not check out. Honor
  that instruction exactly.
- The existing paragraph contains an em dash ("cut 75% —"). Remove it as part of the rewrap;
  this doc is agent-facing.
- This doc follows the Google developer-doc register per the 2026-09-04 plan's own note, so
  Vale's Google package governs its prose.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. The clause "unpinned subagents inherit the session model" no longer appears anywhere in
   `model-economy.md`.
2. The `## Fable 5.1` section carries the three subsections the 2026-09-04 plan's task 3 names,
   and every figure in the price and benchmark table matches the plan's table exactly.
3. No em dash appears in the section after the diff, and none appears anywhere in the diff.
4. `fable-post-cutoff-system.md:12` is updated per the plan's Files line, and the reviewer
   names any figure there that now contradicts the new table as a blocking finding.
5. Any figure the implementer could not confirm is reported in `couldNotDo` and is absent from
   the file rather than written unverified.
6. `cairn-run-gate 'bash scripts/check.sh'` prints `gate exit: 0`.

---

### Task 6: The CLAUDE.md displacement, and the four docs-standard lines

**Model:** `sonnet`. **Depends on:** task 2, because pick 1 makes
`claude/.claude/docs/unattended-work-guards.md` the sole home for the guard procedures and that
doc must be correct first. **Deliverables:** 4. **Independent:** no.

**Files:**

- Modify: `claude/.claude/CLAUDE.md`
- Create: `claude/.claude/docs/engine-ui-mechanics.md`
- Create: `claude/.claude/docs/pass-gate-economy.md`

**Outcome.** `claude/.claude/CLAUDE.md` measures **under 24,000 bytes** with the four
docs-standard lines landed, and every displaced section's full text is reachable through a
pointer that resolves. The cap is not raised.

**The byte target and its arithmetic.** `claude-context-budget`
(`bin/.local/bin/claude-context-budget:18,22`) sets `CLAUDE_MD_BUDGET=6000` approximate tokens
for any file named `CLAUDE.md`, computed as `wc -c` divided by four, so the byte ceiling is
24,000.

| Quantity | Bytes |
|---|---|
| `claude/.claude/CLAUDE.md` today | 27,807 |
| The four docs-standard lines to add | +630 |
| Total before displacement | 28,437 |
| Ceiling | 24,000 |
| **Net bytes that must leave the file** | **4,437** |

**The four lines.** Use the `claude/.claude/CLAUDE.md` draft verbatim from
`docs/superpowers/plans/2026-09-08-claude-md-displacement-candidates.md`, section "The four new
lines and their byte cost", measured there at 630 bytes. Write no other new content into
`CLAUDE.md`.

**The ranked picks, by name, with their destinations.** Apply in rank order until the file
measures under 24,000 with the four lines landed, then stop. Picks 1 through 4 are the ranked
candidates from the 2026-09-08 document, re-measured at `9034fd3`. Pick 5 is new, measured
during this drafting, and is required because picks 1 through 4 fall about 1,000 bytes short of
4,437 once each is replaced by a pointer.

| Rank | Pick | Section bytes | Destination for the full text |
|---|---|---|---|
| 1 | The unattended-work guards paragraph, under "Multi-agent workflows: suggest, never launch unprompted" | 456 | `claude/.claude/docs/unattended-work-guards.md`, which already states it in full. No text moves. |
| 2 | The "Engine-level UI mechanics, every cairn site" section | 2,143 | **Create** `claude/.claude/docs/engine-ui-mechanics.md`, carrying the displaced text verbatim. |
| 3 | The "FULL ACCOUNT ACCESS" paragraph under "Cloudflare / Wrangler" | 702 | `claude/.claude/docs/cloudflare-estate-inventory.md`, which already carries the account id and the ASC Access route (`:40`). No text moves. |
| 4 | The "Installing a NEW long-lived secret" bullet under "Secrets" | 1,038 | `secrets/registry.md`, which already carries the whole flow (`:74`, `:85-99`). No text moves. |
| 5 | The "Gate economy on a pass" section | 2,906 | **Create** `claude/.claude/docs/pass-gate-economy.md`, carrying the displaced text verbatim. |

Applying picks 1, 2, 3, and 5 sheds about 5,032 net bytes and lands the file near 23,400,
which clears the target with headroom and leaves the secrets flow inline where an agent meets
it. Pick 4 is the fallback if any earlier pick sheds less than estimated. The implementer
measures after each pick rather than trusting these estimates.

**Constraints.**

- **Displacement means moving, never deleting.** Every pick leaves behind a pointer that names
  the destination file and preserves the section's trigger, so a session still knows the rule
  exists and where to read it. Pick 1's trigger is "before arming either guard". Pick 2's is
  "this repo has patched this before". Pick 5's is that a pass's gate is scoped to what it can
  catch.
- For picks 2 and 5, the created doc carries the displaced text **verbatim**, reformatted only
  as a standalone document needs (one `#` title and an opening line saying which CLAUDE.md
  section it holds). Write no new rules into either doc, and drop none.
- For picks 1, 3, and 4, verify the destination carries the displaced content in full **before**
  trimming. If it does not, report it in `unspecifiedDecisions` and move to the next rank
  rather than dropping content.
- Do not raise `CLAUDE_MD_BUDGET`, and do not edit `claude-context-budget`.
- Do not touch `~/Projects/cairn-cms/CLAUDE.md`. It is 24,873 bytes, over the cap, owes its own
  four lines, and a live session holds that repo. It is recorded below as a handoff.
- `CLAUDE.md` is live in every session at the moment of the write, including the sessions
  running this round's remaining tasks. Report what changes for them.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. `bash bin/.local/bin/claude-context-budget claude/.claude/CLAUDE.md` exits 0, and `wc -c <
   claude/.claude/CLAUDE.md` reports under 24,000. Both outputs are pasted in the report.
2. The four lines appear in `CLAUDE.md` byte-identical to the candidates document's draft, and
   no other new content was added.
3. Every pointer left behind resolves. For each, the implementer pastes a `test -f` or
   `readlink -f` result for the named destination, and for picks 1, 3, and 4 pastes a `grep`
   hit proving the destination carries the displaced content.
4. For picks 2 and 5, diffing the created doc's body against the removed section at the parent
   commit shows no rule added and no rule dropped. The reviewer performs this comparison
   directly against `git show HEAD~1:claude/.claude/CLAUDE.md`.
5. Each surviving pointer names the destination path and preserves its section's trigger phrase.
6. `~/Projects/cairn-cms/CLAUDE.md` is untouched, proved by `git -C ~/Projects/cairn-cms status
   --short` showing no change to it.
7. The commit names only the three Files above.
8. `cairn-run-gate 'bash scripts/check.sh'` prints `gate exit: 0`.

---

### Task 7: `pass-execute.js` and its skill text

**Model:** `sonnet`. **Depends on:** task 0, and it runs **last among behavior-changing tasks**,
after task 6, because it edits the runner segments A and B execute. **Deliverables:** 3.
**Independent:** yes, and it must be ordered last.

**Files:**

- Modify: `claude/.claude/workflows/pass-execute.js`

**Precondition, checked before any edit.** Confirm no live workflow run is executing
`pass-execute.js`. A cairn session mid-run holds `pass-execute-chains.js`, a different file, so
the check is for `pass-execute.js` alone. If a run holds it, report blocked and change nothing.

**Outcome.** The runner stops telling every implementer a falsehood about the gate, and stops
forcing a plan to paste the same protocol text into every task's `notes`. Its documented
invocation shape says how a pass with conductor boundaries is launched.

**The three changes, each from a recorded finding.**

1. **The gate wording (`pass-execute.js:136`).** The line says the runner "blocks to completion
   and prints the tail". That is the same false claim task 1 corrects in two agent definitions,
   and this line reaches every implementer the runner dispatches. Replace it with the exit-75
   reattach protocol, from the same template task 1 uses. The behavior it must describe is
   verified in `bin/.local/bin/cairn-run-gate:1-14`.
2. **One shared-notes field appended at prompt time.** The finding, from the dubplate window:
   "the protocol block every task needs is pasted into every task's `notes` because the script
   has no one field it appends at prompt time". `pass-execute-chains.js` has one, `a.paintProtocol`,
   appended to the criteria line in both `implementPrompt` (`:75`) and `reviewPrompt` (`:104`).
   Give `pass-execute.js` an equivalent optional top-level argument, appended to every task's
   prompt at prompt time. Follow the precedent the file already set for its optional arguments:
   `reducedGate` (`:16-19`, `:144-146`, `:157-159`), `mutationLedger` (`:47-62`), and
   `severity` (`:85-88`) are each absent-by-default, and absence leaves behavior exactly as it
   is today. Name the argument, its shape, and where it lands in the header comment's
   invocation block. Validate nothing new in `validateArgs`, since the argument is optional.
3. **The segment launch shape, in the skill text.** There is no `SKILL.md` for this workflow;
   `grep -rl "pass-execute" ~/.dotfiles/claude/.claude/skills` returns only `site-pass` and
   `cairn-pass`, which reference it in passing. The skill text is `meta` (`:30-39`, whose
   `name`, `description`, and `whenToUse` are what a session sees in the skill listing) and the
   header comment block (`:1-28`). Record there that the runner has no mid-run conductor hook,
   so a pass carrying conductor boundaries is launched one segment per invocation, with the
   conductor's checkpoint and batched simplifier round falling at each boundary. Record also
   that `repo` is prompt text only and every gate string is absolute per tree, which is why a
   worktree run passes an absolute gate string. Both findings come from the dubplate window
   memo's "What the window learned" section.

**Constraints.**

- Change no existing behavior beyond the prompt text in item 1. A run with none of the new
  argument supplied must produce prompts identical to today's except that one corrected
  sentence.
- Do not touch `pass-execute-chains.js`. It is the cairn variant and a live cairn session may
  hold it.
- Add no dependency, and keep the file's existing shape: `main()` holds every `await`, and the
  top level only calls and returns `main()` (`:270-272`).
- Comments in this file are JavaScript comments, so no em dash.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. `pass-execute.js` no longer contains "blocks to completion", and its gate line states exit
   75, the re-issue of the same command, the end condition, and the ban on background runs and
   log polling.
2. The new argument is optional. The reviewer confirms `validateArgs` does not require it, and
   that the prompt builders append it only when present, matching how `reducedGate` is handled
   at `:144` and `:157`.
3. With the argument absent, the diff changes no prompt line other than the gate sentence. The
   reviewer verifies this by reading both prompt builders, not by running the workflow.
4. `meta.whenToUse` or `meta.description` states the segment launch shape, and the header
   comment's invocation block documents the new argument by name and shape.
5. The header comment records that `repo` is prompt text only and that every gate string is
   absolute per tree.
6. `node --check claude/.claude/workflows/pass-execute.js` exits 0. The repo gate has no
   JavaScript leg, so this check is the syntax proof and is pasted in the report.
7. No em dash appears in the diff.
8. `cairn-run-gate 'bash scripts/check.sh'` prints `gate exit: 0`.

---

### Task 8: Close, one fold agent drafting the ledger updates

**Model:** `sonnet`. **Depends on:** tasks 1 through 7. **Deliverables:** 3. **Independent:** no.

**Files:**

- Create: `docs/superpowers/plans/2026-09-12-claude-infra-round-handoff.md`

**Outcome.** The conductor has three ledger drafts it can fold without re-deriving the round's
narrative. **The conductor owns the ledgers**, so this task writes drafts in the handoff
document and edits none of `docs/STATUS.md`, `docs/HISTORY.md`, or `ROADMAP.md`.

**The three drafts, each as its own section of the handoff document.**

1. **The `docs/STATUS.md` draft.** Present tense only, and it must keep the file under the
   60-line cap after folding. It restates the gate line if task 3 or task 7 changed what the
   gate covers, records the three hoisted homes and the two new docs, and points the immediate
   next action at whatever this round left owed.
2. **The `docs/HISTORY.md` draft.** One entry, newest first, naming what landed with each
   task's commit SHA, what the gate and the reviewer caught, the fix rounds each task took, and
   the budget outcome against the 1.0M ceiling. Its "What a later pass would be wrong to
   rediscover" list is the entry's reason for existing, and must carry at least: the five
   folded `~/.claude` directory symlinks, so no later pass plans a `stow -R claude` it does not
   need; that the dotfiles gate reads repository markdown only through gitleaks; and that
   `claude/.claude/CLAUDE.md` grew 3,812 bytes in four days, which is why the four ranked
   displacement candidates stopped being sufficient.
3. **The `ROADMAP.md` draft.** Whether any item this round touched belongs in Active, Planned,
   or Someday, and whether the cairn documentation standard's Active entry needs amending now
   that the workstation `CLAUDE.md` carries its four lines.

**Constraints.**

- Every SHA, count, and byte figure in the drafts is quoted from the per-task reports or
  measured directly. Report any figure you could not source in `couldNotDo` rather than
  estimating it.
- Cite no plan line numbers in any file this round shipped. Process citations belong in the
  handoff document, never in a shipped comment or agent definition.
- Write only the handoff document. A diff that touches a ledger file is a blocking finding.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. The handoff document carries exactly three draft sections, one per ledger, each labeled with
   the file it is for.
2. `git show --name-only HEAD` names only the handoff document. Neither `docs/STATUS.md`,
   `docs/HISTORY.md`, nor `ROADMAP.md` appears.
3. Every commit SHA the drafts name resolves with `git cat-file -e`, and the reviewer checks
   each one.
4. The STATUS draft, folded into the current file, would leave it at or under 60 lines. The
   draft states its own projected line count.
5. The HISTORY draft's "wrong to rediscover" list carries the three findings named above.
6. No plan-line citation appears in any file this round shipped, proved by grepping the round's
   touched files for the plan's filename.
7. `cairn-run-gate 'bash scripts/check.sh'` prints `gate exit: 0`.

**After this task the conductor folds the drafts**, commits the three ledger files by path, and
dispatches one independent `diff-reviewer` at `claude-opus-5` over the fold's diff. The fold is
capped at one dispatch.

---

## Task ledger

| # | Title | Model | Depends on | Deliverables | Independent | Segment |
|---|---|---|---|---|---|---|
| 0 | Coordination check | conductor, no dispatch | none | 1 | yes | pre-A |
| 1 | Exit-75 reattach protocol in two implementers | `sonnet` | 0 | 2 | yes | A |
| 2 | The two guards-doc corrections | `sonnet` | 0 | 2 | yes | A |
| 3 | One home for each duplicated site asset | `sonnet` | 0 | 4 | yes | A |
| 4 | Hoist `go-architecture-reader` | `sonnet` | 0 | 2 | yes | B |
| 5 | The carried model-economy update | `sonnet` | 0 | 2 | yes | B |
| 6 | CLAUDE.md displacement and the four lines | `sonnet` | 2 | 4 | no | B |
| 7 | `pass-execute.js` and its skill text | `sonnet` | 0, ordered last | 3 | yes | C |
| 8 | Close, one fold agent's ledger drafts | `sonnet` | 1 to 7 | 3 | no | C |

Eight dispatched tasks against seven ruled items, plus one conductor task and one close. The
extra count is the close task and nothing else; no ruled item was split into two tasks, and no
task carries work the ruling did not name. Every reviewer dispatch is `diff-reviewer` at
`claude-opus-5`.

## Item coverage

| Survey ruling item | Task |
|---|---|
| 1. The gate runner's reattach protocol in every implementer that uses it | 1 |
| 2. The unattended-work guards doc | 2 |
| 3. `pass-execute.js` and its skill text | 7 |
| 4. The global `CLAUDE.md` budget | 6 |
| 5. Duplicated site assets hoisted to the workstation | 3 |
| 6. `go-architecture-reader` to the workstation agents | 4 |
| 7. The three items carried from the 2026-09-04 Fable 5.1 pass | 5, which names all three and carries the one that is a workstation edit |

## Risks

- **`~/.claude` is live and this round has no feature flag.** Tasks 1, 2, 3, 4, 5, 6, and 7
  each change what every session on this machine sees at the instant of the write. The
  mitigations are the live-surface rule in Global constraints, the requirement that task 7's
  new argument be absent-by-default, and the requirement that task 1 and task 2 correct one
  paragraph each rather than rewriting a file. A half-landed round leaves additive state.
- **Task 6 rewrites the file every later dispatch reads at session start.** It is ordered
  second-to-last among behavior-changing tasks for that reason, and its displaced text stays
  reachable through a pointer rather than being deleted.
- **Task 3 makes a `svelte-check` skill visible in every project session**, including the Go
  repos. Its description names SvelteKit file types, which is the guard against a mis-trigger,
  and criterion 6 checks that the description survived the hoist.
- **The cairn session's warm file is a standing hazard.** A `git add -A` in `~/.dotfiles` would
  stage another session's uncommitted work. The specific-file rule is stated three times in this
  plan for that reason, and task 1's criterion 4 checks the file is still warm and unstaged
  when the round's first task ends.
- **Task 7's precondition can block it.** If a cairn or dubplate session is mid-run on
  `pass-execute.js`, the task reports blocked and the conductor defers it to a later round. The
  other seven tasks do not depend on it.
- **The ceiling is derived, not measured.** No actual token spend is recorded for the
  comparable 2026-09-08 pass, so the 0.1M per-task rate is an inference from that plan's
  ceiling. If the first segment overruns 0.3M, raise the question at the segment-A checkpoint
  rather than at 80% of the ceiling.

## Out of scope, recorded

The survey's out-of-scope notes, verbatim, so each owning repo can find them.

> - dubplate's `check.sh` forms (`--scope-changed`, `--reduced`, `--merge`) and the two
>   staged legs (`CHECK_CITATIONS`, `CHECK_EXPORTED_UNUSED`): one consumer. poplar is the
>   plausible second for the two legs and adopts them in its own pass if it wants them.
> - dubplate's `simplifier-brief.md` and `tools/close-evidence`: one consumer each.
> - `STATUS.md` over the 60-line cap in six repos (907-life 236, cairn-pub 183, ecxc-ski
>   173, cairn-cms 100, xcathletes-org 69, aksailingclub-org 68): the ledger rule already
>   makes the move a close-out chore in each repo.
> - poplar has no `docs/STATUS.md`, `HISTORY.md`, or `ROADMAP.md`: poplar's own chore.

Four more notes, from the ruling's in-scope items and from this drafting.

- **poplar's implementer.** `~/Projects/poplar/.claude/agents/poplar-implementer.md` runs `make
  check` directly and never calls `cairn-run-gate`, so item 1's correction does not apply to
  it. Adopting the runner is poplar's own decision in its own pass.
- **`cairn-cms/CLAUDE.md`.** 24,873 bytes, over the 24,000-byte cap, and it owes the same four
  docs-standard lines. That is cairn's repo and a live session holds it. Its ranked
  displacement candidates are already measured in
  `docs/superpowers/plans/2026-09-08-claude-md-displacement-candidates.md`, section "Ranked
  candidates: `cairn-cms/CLAUDE.md`". This round edits nothing there.
- **The `ship` skill.** `aksailingclub-legacy/.claude/skills/ship/SKILL.md` and `ecxc-ski`'s
  share a name and have diverged in substance, so the survey ruled it a note. Whichever repo
  next touches its own copy decides whether the two should converge.
  `907-life/.claude/instructions/css-rules.md` has one consumer and stays in that repo.
- **The other two carried 2026-09-04 items.** The site-pass experiment's verdict goes into
  `docs/HISTORY.md` when the next `ecxc-ski` or `907-life` pass closes, and a worse result
  reverts commit `8a958fe`. The first monthly model review is due 2026-10-01 and is already an
  Active ROADMAP entry with `model-review.timer` raising the reminder. Neither is a workstation
  edit this round can make.
