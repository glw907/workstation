# Claude infrastructure round: the workstation layer, sized to what recurs

**Status:** revision 2, 2026-09-12, drafted against `506772e`
("docs: record the three-lens review of the Claude infra round plan, revision 1"). Awaiting
Geoff's approval. Not yet executed.

> **For agentic workers:** this plan runs through the `pass-execute` workflow for segments A
> and B, and through per-task Agent-tool chains in the main loop for segment C. Each task
> below carries its own Files, outcomes, and acceptance criteria, and the plan section is the
> authority over any condensed criteria string in a dispatch. Do not read another task's
> section. Do not `git add -A` in any repo. Do not touch
> `claude/.claude/agents/cairn-implementer.md`; a live cairn session owns that file. The args
> mapping the conductor passes is fixed below, under "The `pass-execute` args mapping".

**Goal:** land the seven workstation items the 2026-09-12 cross-project survey ruled in scope,
so that every repo that consumes a shared implementer, guard doc, workflow runner, agent, or
site asset reads one correct copy instead of two stale ones.

**Spec:** `docs/superpowers/research/2026-09-12-claude-infra-round-survey.md`, sections "The
ruling", "Out of scope, recorded for the repo that owns each", and "Constraints on execution".
The ruling is fixed. This plan splits and merges its items into tasks and re-litigates none of
them. One bullet of that spec is superseded: its "Constraints on execution" stow bullet says a
new file under `claude/.claude/` appears only after `stow -R claude`, which Correction 1 below
disproves. Follow Correction 1.

**Repos written:** `~/.dotfiles` for every task. `~/Projects/dubplate` for two files (task 1
and task 5). `~/Projects/907-life` and `~/Projects/ecxc-ski` for the duplicated site assets
(tasks 3 and 4). Nothing is written in `~/Projects/cairn-cms`, `~/Projects/poplar`, or any
other repo.

**Format exemplar:** `docs/superpowers/plans/2026-09-08-docs-standard-claude-infra.md`, the
previous infra plan in this repo, whose executor precedent this plan inherits.

---

## Revision note: what revision 2 folded

Revision 2 folds three adversarial reviews of revision 1, recorded at `506772e`:

- `docs/superpowers/research/2026-09-12-claude-infra-round-review-contract.md`, the contract
  and criteria lens: 3 blockers, 6 majors, 7 minors.
- `docs/superpowers/research/2026-09-12-claude-infra-round-review-mechanics.md`, the mechanics
  and feasibility lens: 3 blockers, 7 majors, 9 minors.
- `docs/superpowers/research/2026-09-12-claude-infra-round-review-domain.md`, the domain risk
  lens: 5 blockers, 14 majors, 9 minors.

**Conductor rulings applied as ruled, not re-opened.** Six rulings were handed down with the
fold and are written into the tasks below: the exit-75 wording source is the runner's own
header (ruling 1); displacement keeps every load-bearing sentence inline (ruling 2); the
site-asset hoist splits universal content from repo facts (ruling 3); the args mapping is
fixed in this plan (ruling 4); every gate string is absolute (ruling 5); task 0 gains launch
conditions (ruling 6).

**Structural changes.** Revision 1 carried eight dispatched tasks. Revision 2 carries ten,
because two tasks were split. The site-asset hoist split into the skill (task 3) and the two
instruction files with their repo supplements (task 4), which ruling 3 turned from a verbatim
hoist into an edit across three repos. The CLAUDE.md work split into creating the two
destination documents (task 7) and trimming the file (task 8), which answers contract MAJOR 8
and enforces create-before-delete. The segments re-cut to 3, 4, and 3.

**Where two lenses disagreed.**

1. **How a segment launches the runner.** Mechanics MAJOR 6 says the Workflow tool refuses a
   `~/.claude/workflows` scriptPath, so the runner is invoked by name and no copy is made.
   Domain MAJOR 14 says the plan should state the scratchpad-copy step. **Taken: mechanics.**
   A scratchpad copy would make task 9's edit invisible to every later run, which is the
   failure the copy rule was never meant to cause. The workstation memory
   `pass-execute dispatch mechanics` records invocation by name as the working form.
2. **Which displacement picks apply.** Mechanics MINOR 2 proposes swapping pick 3 for pick 4
   because pick 3's destination lacks the displaced content. Domain MAJOR 12 proposes keeping
   pick 3's two operative sentences inline instead. **Taken: domain**, which is also ruling 2's
   shape. Pick 3 stays in the applied set with its authority grant and its curl caveat
   retained inline, so no content has to move into the inventory first.
3. **Where the exit-75 wording comes from.** Mechanics BLOCKER 3 and domain BLOCKER 2 both say
   the cairn session's uncommitted diff is an unsafe source, and both propose a task 0
   snapshot. Ruling 1 supersedes both: the runner's own header is the source, quoted here as a
   property list, and no snapshot is taken.
4. **How much of the runner's behavior the wording carries.** Ruling 1 names the header as the
   source. Domain MAJOR 5 and MAJOR 6 show the header omits the vanished-status branch, which
   the code carries at `:44-51` and which produces a false red. **Both applied:** the header
   supplies the wording, and the vanished-status branch joins the property list as a sixth
   property sourced from the code. This adds a behavior the ruling's list did not name; it
   does not change the wording source.

Every blocker, major, and minor across the three reviews is answered in a task, a constraint, a
criterion, or this note. The citation corrections are in the pre-flight.

---

## Drafter's pre-flight (staleness is the drafter's job, and task 0 runs no gate)

Every path, byte count, and line reference below was verified at `506772e` during this fold.

**Tree state.** `git -C ~/.dotfiles log -1 --format=%h` reports `506772e`.
`git -C ~/.dotfiles status --short` reports exactly one line, `M
claude/.claude/agents/cairn-implementer.md`, the cairn session's warm file. HEAD moved twice
since revision 1's drafting, from `9034fd3` to `603f667` (this plan) to `506772e` (the three
reviews). No task's Files were affected. Task 0 asserts the warm-file set and the absence of
any task's Files, never a specific HEAD, because HEAD moves whenever a session commits a
document (mechanics MINOR 3, domain MINOR 5).

**Executor check.** `pgrep -af dotfiles` returns only the checking shell. Resolving each
candidate's `/proc/<pid>/cwd` leaves no process with a working directory under `~/.dotfiles`.
That check is blind to the one contended writer this round names, so task 0 carries the
journal check below (domain MAJOR 1).

**The live cairn run, verified during this fold.** Workflow `wf_2d52758e-603` under
`~/.claude/projects/-var-home-glw907-Projects-cairn-cms/4b322bf8-216b-4c56-93da-cc9520102d95/subagents/workflows/`
has a `journal.jsonl` whose last event is a `started` record labeled `impl:2` in phase
`pass-execute-chains #3`, written at 12:22. That session's working directory is
`~/Projects/cairn-cms`, so a cwd-based check reports it absent while it writes the stow source
through the `~/.claude` symlinks. It holds `pass-execute-chains.js`, a different file from the
one task 9 edits.

**Power state, verified during this fold.** `/sys/class/power_supply/AC/online` reads 0 and
`BAT0` reads 33% and `Discharging`. The machine is on battery. Task 0's launch conditions
apply (domain MAJOR 2).

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
The arithmetic is in task 8. The four ranked picks fall short, so task 8 carries a fifth pick
measured during revision 1's drafting.

**Correction 4, revised: two ranked picks still need content that their destinations lack, and
the fold keeps that content inline instead.** Revision 1 claimed
`claude/.claude/docs/cloudflare-estate-inventory.md` and `secrets/registry.md` already carried
their picks in full. Re-reading proves that half wrong. The inventory carries the account id
(`:3`, `:87`) and the ASC Access service-token route, and it does not carry the authority grant
("make routine changes directly; never treat Cloudflare state as read-only") nor the rule that
the MCP token is read-only for Access and Workers-domain writes so those go through curl
(domain MAJOR 12, mechanics MINOR 2). `secrets/registry.md` carries the `secret-set.sh` flow
(`:85-88`), the three input flags (`:98-99`), and `sync.sh --worker NAME` (`:74`), and it does
not carry the ASC per-project store exception nor the worker-only `MAGIC_LINK_SECRET` and
`SESSION_SECRET` carve-out (domain MINOR 8). Under ruling 2, picks 3 and 4 keep their operative
sentences inline as the pointer's own body, so no content moves and nothing is dropped.

**Correction 5: every diverging line in the two duplicated site instruction files is drift or a
repo fact, and none of it is content the workstation copy should carry.** The survey recorded
"one repo-specific deploy command differs". Reading both pairs proves more than that.
`907-life`'s `ai-operational-rules.md:38-42` still names `hugo --minify` and a `public/` build
directory, while `907-life/package.json:7` builds with `vite build` and
`907-life/CLAUDE.md:112` gives the same SvelteKit deploy command `ecxc-ski` carries. That hunk
is stale text. `907-life`'s `ai-operational-rules.md:19` carries a `RESEND_API_KEY` example, and
grepping both source trees finds Resend in eight `ecxc-ski/src` files and nowhere in
`907-life/src`, so the example belongs to `ecxc-ski`. Every remaining hunk in both files is line
wrapping, punctuation, or phrasing. `907-life/.claude/skills/svelte-check/SKILL.md` and
`ecxc-ski`'s are byte-identical at 1,748 bytes.

**Correction 6, new in revision 2: `ecxc-ski`'s instruction body carries facts that are false
or local, so a verbatim hoist would install them machine-wide.** Verified by reading
`ecxc-ski/.claude/instructions/ai-operational-rules.md`: `:83` says "All local dev secrets in
`~/.bashrc`", contradicting the global secrets policy, which puts sensitive values in
`~/.local/secrets` from the age store; `:33` names `git push origin main` into GitHub Actions
as the normal deploy; `:35-36` bans `npx wrangler deploy` from the project root, contradicting
the global Cloudflare section, which names that command as the route; `:40` gives the manual
deploy `npm run build && npx pagefind --site .svelte-kit/cloudflare && npx wrangler deploy`,
true of the two pagefind sites and of no other repo (domain BLOCKER 5). Ruling 3 splits these
out. `documentation-standards.md` carries no comparable repo fact. Its only local-looking line
is a `cd myproject` placeholder, and every other divergence between the two copies is wrapping
or punctuation.

**Correction 7, new in revision 2: the `svelte-check` skill's body is wrong for four of the six
SvelteKit repos it becomes visible to.** Its step 2 says a clean run's output ends with
`svelte-check found 0 errors and 0 warnings`. That is true of `ecxc-ski` and `cairn-cms`, whose
`check` script is `svelte-check --tsconfig ./tsconfig.json` alone. It is false of
`xcathletes-org`, whose `check` continues into `npm run lint:openapi`, and of `cairn-pub`,
whose `check` continues into `npm run check:docs-links`. `907-life`, `aksailingclub-org`,
`xcathletes-org`, and `cairn-pub` each prefix `svelte-kit sync`, which the skill's Notes
present as a separate remedy. dubplate's `web/` is SvelteKit and has no `package.json` today,
and dubplate's gate is `bash scripts/check.sh`, so `npm run check` from the dubplate root does
not exist (domain MAJOR 7).

**Citation corrections carried into revision 2.**

| Revision 1 citation | Corrected | Source |
|---|---|---|
| `dubplate-implementer.md` step 5 at `:68-71` | `:67-71`, and `:67` is the "Run the gate once" line | read directly; the contract lens's `:67-70` is also off by one at the end |
| Pick 3 at 702 bytes | 700 bytes (`CLAUDE.md:94-101`) | `wc -c` |
| Pick 4 at 1,038 bytes | 921 bytes (`CLAUDE.md:123-132`) | `wc -c` |
| The four docs-standard lines at 630 bytes | 638 bytes; the candidates document's own 630 is stale | `wc -c` over that document's `:29-38` |
| `registry.md` flow at `:85-99` | `:85-88` for the flow, `:98-99` for the input flags, `:74` for `sync.sh --worker NAME` | read directly; the contract lens's proposed `:84` is a blank line and does not check out |
| `cairn-run-gate:1-14` as the behavior source | `:1-14` is the comment header and is the wording source; `:15-60` is the code and is the behavior source | read directly (domain MAJOR 6) |

---

## Global constraints (every task)

**This whole block is pasted verbatim into every task's `notes` field.** The runner has no
shared-notes field until task 9 lands one, so the conductor copies this block from here into
each task's `notes` (mechanics BLOCKER 1, ruling 4).

- **`claude/.claude/agents/cairn-implementer.md` is off-limits to every task.** The cairn
  overnight session authored its working-tree diff and owns its commit. Never stage it, never
  revert it, never edit it. This round neither reads it as a wording source nor asserts
  anything about whether it is still warm.
- **Edit stow sources under `~/.dotfiles/claude/.claude/`, never the `~/.claude/` symlinks.**
- **Every write under `claude/.claude/` is live in every session on this machine at the moment
  of the write**, with no restow and no staging. Each task touching that tree names in its
  report what a session in another repo now sees differently, and states the one-line revert
  (`git -C ~/.dotfiles checkout -- <path>`).
- **Create before delete.** A task that hoists a file creates the workstation copy, proves the
  symlink with `readlink -f`, and only then removes the repo copy. A half-landed task must
  never leave a consumer with neither copy (domain MAJOR 13).
- **Every deletion uses `git rm`**, so an emptied directory is pruned and a criterion checking
  the directory's absence is deterministic (mechanics MINOR 8).
- **Commit specific files, never `git add -A`, in any repo.** One commit per task per repo. A
  task writing two repos makes two commits and reports both SHAs. In a multi-repo task the
  `~/.dotfiles` commit lands last, so a segment boundary is unambiguous (mechanics MINOR 9).
- **Report every commit SHA per repo.** Acceptance criteria resolve content through the
  reported SHA and its parent, never through `HEAD` or `HEAD~1`, because another session
  commits into `~/.dotfiles` while this round runs (mechanics MAJOR 1).
- **Commit footer**, in every repo, two lines, the model name and session URL being the
  executing session's own:

  ```
  Co-Authored-By: Claude <model> <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_<id>
  ```

  The form is verified from `git -C ~/.dotfiles log -3` and `git -C ~/Projects/dubplate log
  -3`, which agree, and both site repos already use the two-line form.
- **A task starts only when none of its own Files appears in that repo's `git status
  --short`.** A warm file you did not author is a stop-and-report signal, never free progress.
- **A task writing outside `~/.dotfiles` re-checks that repo immediately before it writes.**
  Run `git -C <repo> status --short` and read the repo's STATUS lane registry where one exists
  (dubplate's `docs/STATUS.md` carries one). A live executor is a stop-and-report signal
  (ruling 5, mechanics MAJOR 4, domain MINOR 4).
- **A `.claude/` markdown-only commit in dubplate, 907-life, or ecxc-ski runs no repo gate.**
  Those repos' gates read source, tests, and build output, and none of them reads `.claude/`.
  The dotfiles gate is the only gate this round runs (mechanics MAJOR 4).
- **Register:** every file this round writes is agent-facing, so it follows
  `~/.claude/docs/voice/agent-facing.md`. No em dashes anywhere. One idea per sentence. State
  the reason with the rule. State done in checkable terms.
- **No task invents a fact.** Where a task must write wording, this plan names the source the
  wording comes from. Where the source does not settle a detail, report it in
  `unspecifiedDecisions` rather than filling the gap.
- **Gate:** `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'`, in a
  foreground Bash call with `timeout: 600000`, re-issued unchanged on exit 75 until it prints
  `gate exit:`. Never run the gate with `run_in_background` and never poll its log. A red gate
  is never committed.

## The gate string is absolute in every task (ruling 5)

`cairn-run-gate` runs `bash -c "$gate"` in `$PWD` and keys its state on `$PWD`
(`bin/.local/bin/cairn-run-gate:18,28`). A subagent's working directory resets to the session's
primary working directory on every Bash call, and `~/Projects/dubplate` has its own
`scripts/check.sh`, so a relative gate string can silently run the wrong repo's gate and report
a false green (mechanics BLOCKER 2).

**No gate string in this round is relative.** The dotfiles gate is written exactly as:

```
cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'
```

No task in this round runs another repo's gate, per the markdown-only ruling in Global
constraints. A later revision that adds a task reaching into dubplate, 907-life, or ecxc-ski
names that repo's own gate in the same absolute `cd <absolute path> && <gate>` form.

## The exit-75 reattach protocol, as a property list (ruling 1)

**The source of truth is the runner's own comment header,
`~/.dotfiles/bin/.local/bin/cairn-run-gate:1-14`.** The cairn session's uncommitted diff is not
a source for this round. Every file this round corrects carries these properties, in its own
domain nouns:

1. The first call starts the gate detached, keyed by the gate string and the working directory.
2. It blocks up to `CAIRN_GATE_WAIT` seconds, default 540.
3. When that window expires without a result, it prints "gate still running" and exits 75.
4. The caller re-issues the SAME command, which reattaches to the running gate and waits again.
5. The loop ends when the runner prints "gate exit:" with the status and the last 60 lines. A
   finished gate's result prints once and then clears, so a later call with the same string
   starts a fresh run.
6. The foreground Bash call takes `timeout: 600000`, the tool's ten-minute cap, which the
   runner's 540-second default sits under. `CAIRN_GATE_WAIT` is not raised without lowering
   the wait, because a raise past the cap turns the protocol into a tool timeout with no exit
   status (domain MINOR 6).

**One property comes from the code rather than the header** (`cairn-run-gate:44-51`, domain
MAJOR 5 and MAJOR 6). If the detached gate dies without writing a status, the next re-issue
prints "gate process vanished without a status; treating as failure" and then `gate exit: 1`.
That satisfies property 5 with a failure the gate never produced. The wording must say that a
vanished-status line means the run was lost rather than that the gate failed, so the caller
starts a fresh run rather than reporting red.

`run_in_background` and log polling are forbidden in every file this round corrects.

## The `pass-execute` args mapping (ruling 4, mechanics BLOCKER 1)

Segments A and B are launched as `Workflow({ name: "pass-execute", args: {...} })`. The runner
is invoked **by name**. No copy of the script is made, because a copy would make task 9's edit
invisible to every later run (mechanics MAJOR 6; see the revision note's disagreement 1).

Per segment, the args are exactly:

```
{
  repo: "/var/home/glw907/.dotfiles",
  gate: "cd /var/home/glw907/.dotfiles && bash scripts/check.sh",
  implementer: "general-purpose",
  reviewer: "diff-reviewer",
  parallel: false,
  tasks: [ /* one entry per task in the segment, in plan order */ ]
}
```

Each task entry carries:

| Field | Value |
|---|---|
| `id` | the task number as a string, for example `"3"` |
| `title` | the task's heading text |
| `criteria` | a pointer to this plan's task section by heading, then the task's acceptance-criteria list verbatim |
| `files` | the task's Files list, absolute outside `~/.dotfiles` and repo-relative inside it |
| `notes` | the Global constraints block above, verbatim, then the task's own Constraints |

`parallel: false` is explicit on every invocation. Three tasks marked Independent still share
one worktree and one git index, so concurrent implementers would race the index next to
another session's warm file (contract MAJOR 6). The Independent column in the task ledger means
disjoint Files, never concurrent execution.

`criteria` names the plan file's absolute path
(`/var/home/glw907/.dotfiles/docs/superpowers/plans/2026-09-12-claude-infra-round.md`) and the
task's heading, so a zero-context implementer can read its own section and no other.

Task 0's recorded baseline gate line is repeated in every task's `notes`, so the reviewer has
the lane baseline without a conductor round trip.

## Executor and execution mode

Fixed by the survey's "Constraints on execution" and the 2026-09-08 plan's precedent
(`:112-118`). The dotfiles repo has no repo-specific implementer agent.

| Role | Agent | Model |
|---|---|---|
| Implementer | `general-purpose` | `sonnet` |
| Reviewer | `diff-reviewer` | `claude-opus-5` |

Ten dispatched tasks means `pass-execute` mode, and this plan names it. Segments A and B run
through the `pass-execute` workflow, one invocation per segment, because the runner has no
mid-run conductor hook. **Segment C runs as per-task Agent-tool chains in the main loop**,
because task 9 edits `pass-execute.js` itself and a runner cannot safely rewrite the script
executing it.

## Contested surfaces

| Surface | The cairn session may write | This round writes |
|---|---|---|
| `claude/.claude/agents/cairn-implementer.md` | yes, and owns its commit | **never** |
| `claude/.claude/workflows/pass-execute-chains.js` | yes, it is the cairn variant | never |
| `claude/.claude/skills/cairn-pass/SKILL.md` | yes | never |
| `claude/.claude/skills/register-check/SKILL.md` | yes | never |
| `claude/.claude/workflows/pass-execute.js` | it may **invoke** it from a later phase | task 9, after the conductor's precondition check |
| `claude/.claude/agents/site-implementer.md` | no | task 1 |
| `claude/.claude/agents/diff-reviewer.md` | it may be **dispatching** it | never; this round does not edit the reviewer |
| `claude/.claude/docs/unattended-work-guards.md` | no | task 2 |
| `claude/.claude/CLAUDE.md` | no | task 8 |
| `claude/.claude/docs/model-economy.md` | no | task 6 |

**Task 9's precondition is the conductor's, never the implementer's** (mechanics MAJOR 5,
domain MINOR 3). A Workflow run lives inside the harness process, so a subagent sees nothing
distinguishable with `pgrep` and has no visibility into another session's runs. The conductor
performs the check at the segment-C boundary and the dispatch asserts it was cleared. The
mechanism is task 0's criterion 6. It is re-run at the boundary because a nested
`workflow({ scriptPath })` re-reads its script at every invocation, so a run that has not
touched `pass-execute.js` yet may still reach it later.

## Budget

**Ceiling 1.5M tokens**, raised from revision 1's 1.0M (mechanics MAJOR 6). The 1.0M rested on
a rate derived from the previous infra plan's ceiling rather than from any measured spend, and
this round's tasks are not small: task 4 edits across three repos, task 6 reads a large source
plan plus a network fetch, and task 8 iteratively re-measures a 27.8KB file. Every task also
pays one Opus reviewer read, and segment C's three chains land their implementer and reviewer
reports in the conductor's own context rather than a workflow's.

The derivation, stated honestly as an inference: `docs/HISTORY.md`'s 2026-09-08 entry records
the previous infra plan's **ceiling** of 0.6M over seven dispatched tasks with no measured
actual, which is about 0.086M per task. Rounding to 0.12M for this round's larger tasks gives
1.2M over ten dispatched tasks, plus a 0.3M conductor reserve for the two workflow invocations,
the three main-loop chains, the three checkpoints, and the fold.

At 80% of the ceiling (1.2M), finish the running task, write STATUS, and ask one combined
question. Check that flag at each segment boundary, the only place a decision can land.

**The early tripwire.** If segment A alone overruns 0.35M, raise the question at the segment-A
checkpoint rather than waiting for 80% of the ceiling. The rate is inferred, so the first
segment is the round's only real measurement of it.

**Checkpoint interval: three tasks**, and every checkpoint falls on a segment boundary.
Checkpoints land after task 3, after task 7, and at the close.

**Split point, if the round runs past its ceiling: tasks 7 and 8 together.** They are the only
pair with no dependent among the remaining tasks. Cutting them leaves the CLAUDE.md file over
budget exactly as it is today, which is the pre-round state, and leaves no other edge to
repair. Cutting task 8 alone is not permitted: task 7 creates two documents whose only purpose
is to receive task 8's displaced text.

## Segments

Each segment ends on a commit the gate proved green.

| Segment | Tasks | How it runs | Ends on |
|---|---|---|---|
| A | 1, 2, 3 | `Workflow({ name: "pass-execute" })`, one invocation, `parallel: false` | task 3's dotfiles commit, gate green |
| B | 4, 5, 6, 7 | `Workflow({ name: "pass-execute" })`, one invocation, `parallel: false` | task 7's commit, gate green |
| C | 8, 9, 10 | per-task Agent-tool chains in the main loop | task 10's fold commit and its independent review |

Segment B carries four tasks, the upper end of the three-to-four rule, because task 7 must land
before task 8 and task 8 belongs in segment C with task 9. Segment C runs in the main loop
because task 9 edits the runner.

**Segment C's launch condition** (ruling 6). The cairn overnight workflow was live at this
fold. **Segment C waits.** At the segment-B checkpoint the conductor reads
`wf_2d52758e-603`'s `journal.jsonl` and holds segment C until that run's last event is a
run-level completion. If the run is still live when the round reaches its 80% checkpoint, task
9 is deferred to a later round, task 10 records it as owed, and tasks 8 and 10 close the round
without it. Tasks 8 and 10 do not depend on task 9.

---

### Task 0: Coordination check and launch conditions (conductor, no dispatch, no gate)

**Model:** none, the conductor runs it. **Depends on:** nothing. **Deliverables:** 1.
**Independent:** yes.

**Files:** none. This task writes nothing.

**Outcome.** The round starts against a tree whose warm-file set matches this plan's
pre-flight, the lane has one recorded green baseline, and the guards the machine's power state
requires are armed.

Per the gate-economy rule, a read-only staleness pre-task runs no gate of its own. The lane's
baseline is the conductor's own single `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash
scripts/check.sh'` call at launch, quoted to every reviewer as task 0's gate evidence and
pasted into every task's `notes`.

**Acceptance criteria.**

1. `git -C ~/.dotfiles status --short` lists no path that appears in any task's Files. One
   warm line, `claude/.claude/agents/cairn-implementer.md`, is expected and is not a blocker.
   The check is on the warm-file set, never on a specific HEAD.
2. No process has a working directory under `~/.dotfiles`, proved by resolving
   `/proc/<pid>/cwd` for each `pgrep -f dotfiles` hit and excluding the checking shell.
3. **Every live session that may write the stow source is enumerated, by journal rather than by
   cwd** (domain MAJOR 1). Find every `subagents/workflows/wf_*/journal.jsonl` under
   `~/.claude/projects/` whose mtime is within five minutes, and record for each which
   `~/.claude` surfaces it may write. A live run is contention on the shared tree even when its
   working directory is another repo. The known case is `wf_2d52758e-603` under the cairn-cms
   project, which holds `pass-execute-chains.js`.
4. `~/Projects/dubplate`, `~/Projects/907-life`, and `~/Projects/ecxc-ski` each report one
   worktree and a tracked-file-clean `git status --short`. dubplate's live-executor check is
   its STATUS lane registry, never `git worktree list`, per dubplate's own CLAUDE.md.
5. **Launch conditions** (ruling 6, domain MAJOR 2). Either `/sys/class/power_supply/AC/online`
   reads 1, or both battery-layer guards are armed and named per
   `~/.claude/docs/unattended-work-guards.md`: `systemd-inhibit --what=sleep` sized to the
   round's expected end, and the battery watchdog. The conductor records which. A live cairn
   run draws from the same battery with its own watchdog set to stand down at 15%, so a
   stand-down at the floor halts this round before it halts the cairn run, and the conductor
   states that in the record.
6. **The `pass-execute.js` precondition mechanism is established and recorded**, to be re-run
   at the segment-C boundary (mechanics MAJOR 5, domain MINOR 3). Grep every live session's
   workflow journal for a `pass-execute` phase, and confirm no live run passes a `chainsScript`
   or `scriptPath` argument naming `pass-execute.js`. Record that a nested
   `workflow({ scriptPath })` re-reads its script at each invocation, which is why the check is
   repeated at the boundary rather than trusted from launch.
7. One `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` run prints
   `gate exit: 0`, and that line is recorded as the lane baseline.

---

### Task 1: The exit-75 reattach protocol in the two implementers that lack it

**Model:** `sonnet`. **Depends on:** task 0. **Deliverables:** 2. **Independent:** yes.

**Files:**

- Modify: `claude/.claude/agents/site-implementer.md` (the gate paragraph at `:89-91`)
- Modify: `/var/home/glw907/Projects/dubplate/.claude/agents/dubplate-implementer.md` (step 5
  in full, `:67-71`, including the `:67` line "Run the gate once, through the blocking
  runner:", and the `description` frontmatter at `:3` where it calls the runner "blocking")

**Outcome.** Both implementer definitions describe what `cairn-run-gate` actually does, so an
implementer dispatched by either one re-issues the command on exit 75 instead of treating a
75 as a gate failure or reaching for a background poll.

**Constraints.**

- **The wording source is the property list above, "The exit-75 reattach protocol, as a
  property list", which quotes `bin/.local/bin/cairn-run-gate:1-14`.** Do not read, stage, or
  alter `claude/.claude/agents/cairn-implementer.md`. This round makes no claim about that
  file's state.
- The vanished-status property from `cairn-run-gate:44-51` is part of the wording both files
  carry.
- **`:67`'s "Run the gate once" is the phrase that most contradicts the new rule** and must go
  (domain BLOCKER 1). The `description` frontmatter's "blocking runner" is the same defect in
  the file's one-line summary.
- Keep every existing instruction in both files that the paragraph does not replace. This is a
  correction to one step each, not a rewrite. `dubplate-implementer.md`'s neighboring rules
  against tailing, sleeping, and polling stay.
- The Bash call shape is part of the wording: a plain foreground call with `timeout: 600000`.

**Commits.** Two, one per repo, each staging only that repo's file, each with that repo's
footer form. The `~/.dotfiles` commit lands last. The dubplate edit is committed in dubplate by
this task, after the pre-write dubplate re-check in Global constraints.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. Neither modified file contains "blocks to completion", "one call gives you one result", or
   "Run the gate once", and `dubplate-implementer.md`'s `description` no longer calls the
   runner blocking.
2. Each modified file states all six properties: exit 75 means still running; the caller
   re-issues the same `cairn-run-gate` command; the loop ends when the runner prints the gate
   exit and the tail; a vanished-status line means the run was lost rather than that the gate
   failed; the re-issue is the only permitted wait, with `run_in_background` and log polling
   forbidden; the foreground call takes `timeout: 600000`.
3. The gate string each file shows is absolute, in the `cd <absolute path> && <gate>` form.
4. `git show --name-only <the reported dotfiles SHA>` names exactly `site-implementer.md`, and
   `git -C ~/Projects/dubplate show --name-only <the reported dubplate SHA>` names exactly
   `dubplate-implementer.md`. The reviewer resolves both through the reported SHAs, never
   through `HEAD`.
5. Both files' YAML frontmatter still parses, `name` still matches the filename stem, and
   `readlink -f ~/.claude/agents/site-implementer.md` resolves into
   `~/.dotfiles/claude/.claude/agents/`.
6. No em dash appears in the diff.
7. `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` prints `gate exit:
   0`. This is a markdown-only change, so the gate proves only that nothing collateral broke;
   criteria 1 through 6 are the proof.

**Note.** `~/Projects/poplar/.claude/agents/poplar-implementer.md` runs `make check` directly
and never calls the runner. It is out of scope by the survey's ruling and is recorded below.

---

### Task 2: The two corrections the unattended window proved in the guards doc

**Model:** `sonnet`. **Depends on:** task 0. **Deliverables:** 2. **Independent:** yes.

**Files:**

- Modify: `claude/.claude/docs/unattended-work-guards.md` (the runaway-guard paragraph at
  `:11-13`, and the battery-watchdog clause at `:39-40`)

**Outcome.** A session arming either guard from this doc arms one that works. Today the doc
sends the runaway guard past the one signal that tells a finished chain agent from a stalled
one, and sends the battery watchdog to a file that lies on AC.

**Constraints.** Both corrections come from the dubplate window's recorded findings in
`~/.claude/projects/-var-home-glw907-Projects-dubplate/memory/unattended-window-2026-09-12.md`,
section "What the window learned (do not rediscover)" at `:47`. Write each correction with its
mechanism, because the register requires the reason beside the rule and the mechanism is what
stops the next session from reverting it.

- **Correction A, the runaway guard.** The doc says `journal.jsonl` "only records agent starts
  and finishes, so a long-running task looks idle there; poll the agent transcripts". **The
  first half of that sentence is true and stays** (domain MINOR 1). What it must gain is the
  completion filter: the guard reads each workflow's `journal.jsonl` for completed agents, or
  every finished chain agent reads as a stall. The corrected rule reads as journal for
  completion, transcripts for idle and size. Keep both existing signatures, the 25-minute idle
  threshold, the 900KB growth threshold, and the TaskStop plus `resumeFromRunId` intervention.
- **Correction B, the battery layer.** The doc polls
  `/sys/class/power_supply/BAT*/{capacity,status}` and triggers "at 11% while `Discharging`".
  The finding: the battery reports "Not charging" on AC under the charge threshold, so a
  `status`-based discharge test is wrong. **The corrected rule does not gate on AC alone**
  (domain MAJOR 3). Gating solely on a mains reading makes the watchdog silent whenever any
  supply is present, including an underpowered USB-C or dock supply that reads online while the
  battery still drains, which is the one plugged-in case that still reaches 0%. Write the rule
  as a disjunction: alarm at 11% when no mains supply is online **or** capacity has fallen
  across two consecutive polls. State that "Not charging" alone is not a drain signal.
- **The AC test is written by supply type, not by an `AC*` glob** (domain MAJOR 4).
  `/sys/class/power_supply/` on this machine holds `AC` with `type=Mains` plus
  `ucsi-source-psy-USBC000:001` and `:002` with `type=USB`, each carrying its own `online`. The
  test is "any supply whose `type` reads `Mains` reads `online` 1". Add a one-line verification
  step to the doc: run that test once while plugged in over USB-C to confirm the mains adapter
  reflects USB-C power delivery on this laptop, because everything reads 0 while unplugged and
  the question cannot be settled from an unplugged session.
- **Name the working reference implementation** (domain MINOR 2). The guard that actually reads
  the journal lives at `~/.cache/cairn-overnight-2026-09-12/runaway-guard.sh`, a cache path the
  next session will not find. Either name that script in the doc as the reference
  implementation with its cache caveat stated, or report in `unspecifiedDecisions` that copying
  it into `bin/.local/bin/` is a larger change than this task carries.
- Do not change the sleep-inhibitor rules, the restart-recovery checklist, or the
  concurrent-sessions section.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. The file states that the runaway guard reads each workflow's `journal.jsonl` for completed
   agents before alarming, and the existing sentence about starts and finishes survives with
   the completion-filter clause attached.
2. The file states the mechanism for correction A: without the journal read, every finished
   chain agent reads as a stall.
3. The file no longer gates the watchdog on `BAT*/status`, states the mains test by supply
   `type`, and states the alarm as a disjunction of the offline-mains test and the two-poll
   capacity drop.
4. The file states the mechanism for correction B: the battery reads "Not charging" on AC under
   the charge threshold, and a supply reading online does not prove the battery is charging.
5. The file carries the one-line USB-C verification step.
6. Both existing runaway signatures, the 11% trigger, the 2-minute poll interval, the silent
   on AC intent, and the full stand-down sequence survive the diff. The reviewer names any
   removed rule as a blocking finding.
7. The reference-implementation question is either answered in the doc or reported in
   `unspecifiedDecisions`.
8. No em dash appears in the diff.
9. `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` prints `gate exit:
   0`. Markdown-only, so criteria 1 through 8 are the proof.

---

### Task 3: One workstation home for the `svelte-check` skill

**Model:** `sonnet`. **Depends on:** task 0. **Deliverables:** 2. **Independent:** yes.

**Files:**

- Create: `claude/.claude/skills/svelte-check/SKILL.md`
- Delete: `/var/home/glw907/Projects/907-life/.claude/skills/svelte-check/SKILL.md`
- Delete: `/var/home/glw907/Projects/ecxc-ski/.claude/skills/svelte-check/SKILL.md`

**Outcome.** One skill, maintained once, correct in every SvelteKit repo on this machine rather
than in the two it came from. The retirement of the repo copies is required rather than
optional: a repo-local skill shadows the workstation one, so leaving both copies in place would
make the hoist a no-op in exactly the two repos it serves.

**Constraints.**

- The two repo copies are byte-identical at 1,748 bytes. **The hoisted body is an edit, not a
  verbatim copy** (ruling 3, domain MAJOR 7, Correction 7). The body must carry only what is
  true on every Svelte site.
- **The named deltas the hoist must make, each read from the repos during this fold:**
  1. Step 1 reads the repo's own `check` script before running it, rather than asserting what
     `npm run check` expands to. `ecxc-ski` and `cairn-cms` run `svelte-check` alone;
     `xcathletes-org` continues into `npm run lint:openapi`; `cairn-pub` continues into `npm
     run check:docs-links`.
  2. Step 2 interprets the output of whatever legs that script runs. The line `svelte-check
     found 0 errors and 0 warnings` is the svelte-check leg's own clean marker, and a repo
     whose `check` has further legs is clean only when every leg is clean.
  3. The Notes' `svelte-kit sync` remedy states that four repos already prefix it in their
     `check` script (`907-life`, `aksailingclub-org`, `xcathletes-org`, `cairn-pub`), so a
     missing `.svelte-kit/tsconfig.json` is the symptom to look for rather than a step to add
     blindly.
  4. The `description` gains a scope line: this skill is for a repo whose root `package.json`
     has a `check` script, and not for a repo whose web app is a subdirectory under a non-Node
     gate. dubplate is that case: its `web/` is SvelteKit, its gate is `bash scripts/check.sh`,
     and `npm run check` from its root does not exist.
- Change nothing else in the body. Every other line is already repo-neutral.
- Create the workstation file and prove its symlink before either deletion.

**Commits.** Three, one per repo, each staging only that repo's paths. The `~/.dotfiles` commit
lands last.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. `git -C ~/Projects/ecxc-ski show <the reported ecxc-ski SHA>^:.claude/skills/svelte-check/SKILL.md
   | diff - claude/.claude/skills/svelte-check/SKILL.md` shows only the four named deltas above
   and nothing else. The reviewer runs that exact command.
2. The frontmatter `name` is `svelte-check`, and the `description` carries both the SvelteKit
   file types it already named and the new scope line excluding a subdirectory web app under a
   non-Node gate.
3. `readlink -f ~/.claude/skills/svelte-check/SKILL.md` resolves into
   `~/.dotfiles/claude/.claude/skills/`, and the implementer's report shows that this was run
   before either deletion was committed.
4. `ls ~/Projects/907-life/.claude/skills/svelte-check` and `ls
   ~/Projects/ecxc-ski/.claude/skills/svelte-check` both fail, because each deletion used `git
   rm` and the emptied directory was pruned.
5. Each of the three commits names only its own repo's paths under `--name-only`, resolved
   through the reported SHAs.
6. No em dash appears in the diff.
7. `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` prints `gate exit:
   0`.

---

### Task 4: The two duplicated instruction files, split into a workstation home and two repo supplements

**Model:** `sonnet`. **Depends on:** task 0. **Deliverables:** 4. **Independent:** yes.

**Files:**

- Create: `claude/.claude/instructions/ai-operational-rules.md`
- Create: `claude/.claude/instructions/documentation-standards.md`
- Rewrite: `/var/home/glw907/Projects/907-life/.claude/instructions/ai-operational-rules.md`
  (becomes a short supplement)
- Rewrite: `/var/home/glw907/Projects/ecxc-ski/.claude/instructions/ai-operational-rules.md`
  (becomes a short supplement)
- Delete: `/var/home/glw907/Projects/907-life/.claude/instructions/documentation-standards.md`
- Delete: `/var/home/glw907/Projects/ecxc-ski/.claude/instructions/documentation-standards.md`

**Outcome.** Two assets that were maintained twice are maintained once, and the two consumers
keep both their repo facts and their discovery path. Under ruling 3 the hoisted file carries
only what is true on every Svelte site, and each repo-specific fact stays in that repo's own
file as a short supplement that points at the workstation copy.

**Constraints.**

- **`documentation-standards.md` hoists from `ecxc-ski`'s copy with one addition.** Every
  divergence between the two copies is wrapping or punctuation, and the file's only
  local-looking line is a `cd myproject` placeholder. The one addition answers domain MAJOR 8:
  the hoisted file opens with a subordination line stating that it sits under
  `~/.claude/docs/authoring-charter.md` and applies only where the charter and the
  `writing-voice` router name no standard for the audience. Without that line the machine gains
  a second doc standard at the same altitude as the charter, and the two disagree in places.
  Neither repo keeps a supplement for this file.
- **`ai-operational-rules.md` splits.** The hoisted body carries the universal content: the
  Bash tool not loading `~/.bashrc` and the `source ~/.local/secrets` pattern, the working
  directory rule, the `node -e` with CSS selectors rule, the wrangler `--name` flag rule, the
  git safety rules, and the GitHub CLI rules.
- **The lines that are repo facts or wrong facts, each read from
  `ecxc-ski/.claude/instructions/ai-operational-rules.md` during this fold** (domain BLOCKER 5,
  Correction 6):

  | Line | Content | Where it goes |
  |---|---|---|
  | `:33` | "Normal deploy: `git push origin main` into GitHub Actions" | each repo's supplement |
  | `:35-36` | the ban on `npx wrangler deploy` from the project root | each repo's supplement, qualified as "for this Actions-deployed site" |
  | `:40` | `npm run build && npx pagefind --site .svelte-kit/cloudflare && npx wrangler deploy` | each repo's supplement |
  | `:83` | "All local dev secrets in `~/.bashrc`" | **dropped**, and replaced in the hoisted body by a pointer to the global secrets policy: sensitive values live in `~/.local/secrets` from the age store, non-sensitive in `~/.bashrc` |
  | 907-life `:19` | the `RESEND_API_KEY` example | `ecxc-ski`'s supplement only, because Resend appears in eight `ecxc-ski/src` files and in no `907-life/src` file |
  | 907-life `:38-42` | `hugo --minify` and the `public/` build directory | **dropped**, stale text disproved by `907-life/package.json:7` |

- **Each supplement is short and points at the workstation file.** It opens with one line
  naming `~/.claude/instructions/ai-operational-rules.md` as the general rules, then carries
  only that repo's deploy facts. This preserves the discovery path an agent uses today, which a
  plain deletion would remove (mechanics MAJOR 3, domain MAJOR 9).
- **Neither repo's `CLAUDE.md` is edited.** The supplements carry the pointer, so no `CLAUDE.md`
  edit is owed.
- **What this changes for `aksailingclub-org`, `xcathletes-org`, and `cairn-pub`** (ruling 3):
  nothing. None of the three ever had either file, and a workstation instructions file is
  reached by an agent reading the path rather than by automatic load. Nothing changes for them
  unless their `CLAUDE.md` points at the hoisted file, and **this round adds no such pointer.**
  Whether to add one is each repo's own decision in its own pass, recorded below.
- Do not touch `907-life/.claude/instructions/css-rules.md`, which has one consumer and is
  recorded below.
- Create both workstation files and prove their symlinks before any deletion or rewrite in a
  site repo.

**Commits.** Three, one per repo, each staging only that repo's paths. The `~/.dotfiles` commit
lands last.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. `git -C ~/Projects/ecxc-ski show <the reported ecxc-ski SHA>^:.claude/instructions/documentation-standards.md
   | diff - claude/.claude/instructions/documentation-standards.md` shows exactly one addition,
   the charter-subordination line, and no other change.
2. The hoisted `ai-operational-rules.md` contains none of `hugo --minify`, `RESEND_API_KEY`,
   `pagefind`, `git push origin main`, or "All local dev secrets in `~/.bashrc`", and it does
   contain the age-store secrets pointer.
3. Each repo's `ai-operational-rules.md` supplement is under 1,500 bytes, opens with a line
   naming `~/.claude/instructions/ai-operational-rules.md`, and carries that repo's deploy
   facts. `ecxc-ski`'s carries the `RESEND_API_KEY` example and `907-life`'s does not.
4. Both hoisted files resolve through the folded symlinks, proved with `readlink -f
   ~/.claude/instructions/ai-operational-rules.md` and `readlink -f
   ~/.claude/instructions/documentation-standards.md`, and the report shows both were run
   before any site-repo commit.
5. `907-life/.claude/instructions/` contains exactly `css-rules.md` and
   `ai-operational-rules.md`. `ecxc-ski/.claude/instructions/` contains exactly
   `ai-operational-rules.md`.
6. Each of the three commits names only its own repo's paths under `--name-only`, resolved
   through the reported SHAs.
7. No em dash appears in the diff.
8. `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` prints `gate exit:
   0`.

**Note.** The `ship` skill exists in both `aksailingclub-legacy` and `ecxc-ski` with diverged
bodies. The survey ruled it a note, not a task. It is recorded below.

---

### Task 5: Hoist `go-architecture-reader` to the workstation agents

**Model:** `sonnet`. **Depends on:** task 0. **Deliverables:** 2. **Independent:** yes.

**Files:**

- Create: `claude/.claude/agents/go-architecture-reader.md`
- Delete: `/var/home/glw907/Projects/dubplate/.claude/agents/go-architecture-reader.md`

**Outcome.** Both Go repos on this machine reach the same package-grading agent. dubplate keeps
the behavior it has, and **the agent becomes available to poplar** (domain MAJOR 11). poplar
gains nothing that dispatches it: poplar's `CLAUDE.md` enumerates its reviewers
(`poplar-implementer`, `diff-reviewer`, `poplar-reviewer`, `poplar-go-reviewer`) and names no
architecture reader, and this round edits no poplar file. The poplar `CLAUDE.md` amendment is
recorded as owed in task 10's handoff.

**Constraints.**

- dubplate's copy is 5,260 bytes. **The hoist makes a named delta list, not a verbatim copy**
  (domain MAJOR 10). Three passages name dubplate's ladder and dubplate's streamer spec, which
  poplar does not have: `:43-44` ("A 2.0 forward hook is named in a plan and built by the rung
  that consumes it, so 'a later rung will want it' is not a caller") and `:80` ("a wrong
  exported surface hardens with every rung").
- **The named deltas:** replace "rung" with a repo-neutral noun ("task") in all three places,
  and replace the 2.0 forward-hook sentence with a repo-neutral form that requires the dispatch
  to name the repo's own forward-hook rule when it has one. Change nothing else.
- Change no frontmatter field, including `model: opus` and `effort: high`. Normalizing the
  model pin is a separate decision and is not this round's.
- dubplate's `CLAUDE.md` names `go-architecture-reader` in its Reviewers section. That
  reference is by agent name, never by path, and stays correct after the hoist. Do not edit
  dubplate's `CLAUDE.md`.
- Create the workstation file and prove its symlink before the dubplate deletion.
- Re-check dubplate's `git status --short` and its STATUS lane registry immediately before the
  dubplate commit (domain MINOR 4).

**Commits.** Two, one per repo. The `~/.dotfiles` commit lands last.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. `git -C ~/Projects/dubplate show <the reported dubplate SHA>^:.claude/agents/go-architecture-reader.md
   | diff - claude/.claude/agents/go-architecture-reader.md` shows only the named deltas above
   and nothing else. The reviewer runs that exact command, which resolves through the reported
   SHA's parent because `HEAD` no longer carries the path (contract MAJOR 4, mechanics MAJOR 2).
2. The hoisted file contains no occurrence of "rung" and no reference to a 2.0 streamer spec.
3. `readlink -f ~/.claude/agents/go-architecture-reader.md` resolves into
   `~/.dotfiles/claude/.claude/agents/`, and the report shows it was run before the dubplate
   commit.
4. The hoisted frontmatter carries `name: go-architecture-reader`, `tools: Read, Grep, Glob,
   Bash`, `model: opus`, and `effort: high`, unchanged.
5. `ls ~/Projects/dubplate/.claude/agents/go-architecture-reader.md` fails, and
   `~/Projects/dubplate/.claude/agents/dubplate-implementer.md` still exists.
6. Each commit names exactly one path under `--name-only`, resolved through the reported SHAs.
7. The report records the dubplate re-check that ran immediately before the dubplate commit.
8. `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` prints `gate exit:
   0`.

---

### Task 6: The one carried 2026-09-04 item that is a workstation edit

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

- The wording source is `docs/superpowers/plans/2026-09-04-fable-5-1-infra-update.md`, task 3,
  steps 1 onward, which carries the replacement clause, the section body, the price and
  benchmark table, the decisions-taken subsection, and the behavior-deltas subsection. Follow
  it as written.
- The section exists today with `grep -c '^## Fable 5.1'` returning 1, so step 1's first branch
  applies: replace the clause "unpinned subagents inherit the session model, so they follow the
  switch automatically" with the clause that plan names, then rewrap the paragraph.
- No `###` subsection exists under that heading today, so every subsection the plan's later
  steps append is genuinely new.
- The plan's task 3 instructs a one-time fetch to confirm three figures before staging, and to
  report a mismatch as could-not-do rather than writing a number that does not check out. Honor
  that instruction exactly.
- **The `fable-post-cutoff-system.md:12` edit is fully specified at that plan's `:446-449`**
  (contract MINOR 15). Line 12 today contains "(output ~$50/MTok, 2x Opus 5)". It must read
  "(output $50/MTok, 2x Opus 5; cache reads $0.25/MTok on Fable 5.1, half Opus 5's; batch
  $5/$25)".
- The existing paragraph contains an em dash at `:168` ("cut 75%"). Remove it as part of the
  rewrap; this doc is agent-facing.
- This doc follows the Google developer-doc register per the 2026-09-04 plan's own note, so
  Vale's Google package governs its prose.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. The clause "unpinned subagents inherit the session model" no longer appears anywhere in
   `model-economy.md`.
2. The `## Fable 5.1` section carries the three subsections the 2026-09-04 plan's task 3 names,
   and every figure in the price and benchmark table matches that plan's table exactly.
3. No em dash appears in the section after the diff, and none appears anywhere in the diff.
4. `fable-post-cutoff-system.md:12` reads exactly the string named in the constraint above, and
   the reviewer names any figure there that contradicts the new table as a blocking finding.
5. Any figure the implementer could not confirm is reported in `couldNotDo` and is absent from
   the file rather than written unverified.
6. `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` prints `gate exit:
   0`.

---

### Task 7: The two displacement destination documents

**Model:** `sonnet`. **Depends on:** task 2, because `claude/.claude/docs/unattended-work-guards.md`
must be correct before task 8 makes it the sole home for the guard procedures.
**Deliverables:** 2. **Independent:** no.

**Files:**

- Create: `claude/.claude/docs/engine-ui-mechanics.md`
- Create: `claude/.claude/docs/pass-gate-economy.md`

**Outcome.** The two destination documents exist and carry their sections' full text before task
8 trims anything from `claude/.claude/CLAUDE.md`. Splitting the creation from the trim is what
makes create-before-delete enforceable here, and it brings task 8's deliverable count down to
an honest number (contract MAJOR 8, domain MAJOR 13).

**Constraints.**

- `engine-ui-mechanics.md` carries `CLAUDE.md:166-194`, the "Engine-level UI mechanics, every
  cairn site" section, **verbatim**, 2,143 bytes.
- `pass-gate-economy.md` carries `CLAUDE.md:260-298`, the "Gate economy on a pass" section,
  **verbatim**, 2,906 bytes.
- Reformat each only as a standalone document needs: one `#` title, and one opening line saying
  which `CLAUDE.md` section it holds and that `CLAUDE.md` keeps a pointer to it.
- **Write no new rule into either document, and drop none.** The verbatim copy is the whole
  deliverable.
- Do not edit `claude/.claude/CLAUDE.md` in this task. The trim is task 8's.
- Both files are agent-facing. The copied text already contains no em dash; do not introduce
  one in the title or the opening line.

**Commits.** One, naming both files.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. Comparing `claude/.claude/CLAUDE.md:166-194` at the reported SHA against
   `engine-ui-mechanics.md` with its title and opening line skipped shows no difference in rule
   content. The reviewer performs the comparison directly and names any added or dropped rule
   as a blocking finding.
2. The same comparison holds for `pass-gate-economy.md` against `CLAUDE.md:260-298`.
3. Both files resolve through the folded symlink, proved with `readlink -f
   ~/.claude/docs/engine-ui-mechanics.md` and `readlink -f
   ~/.claude/docs/pass-gate-economy.md`.
4. `claude/.claude/CLAUDE.md` is unchanged by this commit, proved by `--name-only` naming only
   the two new files.
5. No em dash appears in the diff.
6. `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` prints `gate exit:
   0`.

---

### Task 8: The CLAUDE.md displacement, and the four docs-standard lines

**Model:** `sonnet`. **Depends on:** task 7, which creates both destination documents, and
through it on task 2. **Deliverables:** 5. **Independent:** no.

**The deliverable count, stated honestly** (contract MAJOR 8). Four applied picks plus the four
docs-standard lines is five deliverables, one over the roughly-four rule. The task is not split
further because all five land in one file against one measurement, and a split would leave
`claude/.claude/CLAUDE.md` over budget between two commits, with the `claude-context-budget`
PostToolUse hook blocking on every write in between. The two created documents that would
otherwise make this seven deliverables are already split out as task 7.

**Files:**

- Modify: `claude/.claude/CLAUDE.md`

**Outcome.** `claude/.claude/CLAUDE.md` measures **under 24,000 bytes** with the four
docs-standard lines landed, every displaced section's full text is reachable through a pointer
that resolves, and every load-bearing sentence the displaced sections carried stays inline. The
cap is not raised.

**The byte target and its arithmetic.** `claude-context-budget`
(`bin/.local/bin/claude-context-budget:18,22`) sets `CLAUDE_MD_BUDGET=6000` approximate tokens
for any file named `CLAUDE.md`, computed as `wc -c` divided by four with integer division. The
gate therefore trips at **24,004 bytes**, and this task's target of under 24,000 is the
conservative form of that (domain MINOR 9).

| Quantity | Bytes | Source |
|---|---|---|
| `claude/.claude/CLAUDE.md` today | 27,807 | `wc -c` at `506772e` |
| The four docs-standard lines to add | +638 | `wc -c` over the candidates document's `:29-38` |
| Subtotal | 28,445 | |
| Picks 1, 2, 3, 5 gross shed | -6,205 | each section plus its trailing blank line: 456, 2,143, 700, 2,906 |
| Subtotal | 22,240 | |
| The retained lines and pointers | +1,526 | measured from drafted blocks during this fold |
| **Projected** | **23,766** | |
| Target | under 24,000 | 234 bytes of headroom |
| Budget trip point | 24,004 | 238 bytes of headroom |

**The retained lines cost 1,526 bytes** (ruling 2). That figure was measured during this fold
from drafted pointer blocks: 361 for pick 1, 297 for pick 2, 389 for pick 3, and 475 for pick
5. It is an estimate the implementer re-measures after each pick, never a number to trust.
**If the retained lines push the total to 24,000 or over, the task takes pick 4 as well.**

**The applied set is picks 1, 2, 3, and 5.** It is a named set, never a rank order to walk
until the file clears (contract BLOCKER 1). Pick 4 is the single fallback, applied only when a
measured total after picks 1, 2, 3, and 5 reads 24,000 or more.

| Pick | Section | Section bytes | Destination for the full text | What stays inline |
|---|---|---|---|---|
| 1 | The unattended-work guards paragraph, under "Multi-agent workflows: suggest, never launch unprompted" | 456 | `~/.claude/docs/unattended-work-guards.md`, corrected by task 2 | **The two arming triggers ("Past ~30 minutes", "On battery"), the word mandatory, and the `journalctl` sentence** |
| 2 | The "Engine-level UI mechanics, every cairn site" section | 2,143 | `~/.claude/docs/engine-ui-mechanics.md`, created by task 7 | The mechanic-versus-choice distinction and the trigger "this repo has patched this before" |
| 3 | The "FULL ACCOUNT ACCESS" paragraph under "Cloudflare / Wrangler" | 700 | `~/.claude/docs/cloudflare-estate-inventory.md`, for the account id and the ASC Access route | **The authority grant ("make routine changes directly; never treat Cloudflare state as read-only") and the curl caveat for Access and Workers-domain writes** |
| 5 | The "Gate economy on a pass" section | 2,906 | `~/.claude/docs/pass-gate-economy.md`, created by task 7 | **The "Gates run through `cairn-run-gate '<string>'`" rule and the Workflow scriptPath refusal** |
| 4 (fallback) | The "Installing a NEW long-lived secret" bullet under "Secrets", `:123-132` | 921 | `secrets/registry.md` | The `secret-set.sh` origin rule; see the constraint below |

**Why those lines stay inline** (ruling 2, domain BLOCKER 3 and BLOCKER 4). A pointer's trigger
has to fire at the moment the rule is needed. Pick 1's preserved trigger, "before arming either
guard", fires only after a session has already decided to arm, so the two triggers that produce
the decision have to stay inline, and so does the `journalctl` diagnostic that prevents a false
stall report. Pick 5's preserved trigger, that a pass's gate is scoped to what it can catch,
fires when choosing a gate and never when launching a workflow or reaching for a gate runner,
so those two rules stay inline. Pick 3's authority grant fires at session start: a session that
does not know it holds write authority reports the estate read-only, which is the exact failure
the paragraph was written to stop.

**Where the four lines go** (contract BLOCKER 3). They land as the final four bullets of the
existing `## Writing voice` section, after the "highest-frequency tells" list. That section
already names `tellgrader` and the authoring charter, which is what the four lines extend. Use
the `claude/.claude/CLAUDE.md` draft **verbatim** from
`docs/superpowers/plans/2026-09-08-claude-md-displacement-candidates.md`, section "The four new
lines and their byte cost", measured here at 638 bytes rather than the 630 that document states.

**Constraints.**

- **Displacement means moving, never deleting.** Every applied pick leaves behind a pointer
  that names the destination file, preserves the section's trigger, and keeps the load-bearing
  lines named in the table above.
- **Every pointer is a plain path reference, never an `@`-import** (mechanics MINOR 1).
  `claude-context-budget:33-51` treats an `@`-referenced `*.md` as a context-loaded import, so
  an `@`-import pointer would load the displaced text at session start and nullify the
  displacement while still passing the byte check. `claude/.claude/CLAUDE.md` uses no
  `@`-imports today, and this task adds none.
- **The retained pick 5 bullet is corrected as it is retained.** The bullet reads "it blocks to
  completion and prints the tail", which is the same false claim task 1 corrects in two agent
  definitions. Retain the rule with its wording replaced by the exit-75 form: re-issue the same
  command on exit 75 until it prints `gate exit:`, and never poll a log. This is a wording
  correction to a retained line, never new content.
- **If pick 4 is reached, two exceptions move into `secrets/registry.md` first** (domain MINOR
  8). `registry.md` carries the flow (`:85-88`), the input flags (`:98-99`), and `sync.sh
  --worker NAME` (`:74`), and it does not carry the ASC per-project store exception nor the
  worker-only `MAGIC_LINK_SECRET` and `SESSION_SECRET` carve-out. Move both sentences into
  `registry.md` and prove the grep hit before trimming the bullet.
- Do not raise `CLAUDE_MD_BUDGET`, and do not edit `claude-context-budget`.
- **The context-budget hook will report over-budget on every intermediate write** (mechanics
  MINOR 6). `claude-context-budget --hook` is registered as a PostToolUse hook
  (`settings.json:87`) and exits 2 with blocking stderr while the file is over budget, so
  expect that feedback after every pick until the last one lands. That feedback is expected and
  is never a reason to raise the budget.
- Do not touch `~/Projects/cairn-cms/CLAUDE.md`. It is 24,873 bytes, over the cap, owes its own
  four lines, and a live session holds that repo. It is recorded below as a handoff.
- `CLAUDE.md` is live in every session at the moment of the write, including the sessions
  running this round's remaining tasks. Report what changes for them.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. `bash bin/.local/bin/claude-context-budget claude/.claude/CLAUDE.md` exits 0, and `wc -c <
   claude/.claude/CLAUDE.md` reports under 24,000. Both outputs are pasted in the report.
2. **No new content appears in `CLAUDE.md` other than the four docs-standard lines and one
   pointer per applied pick** (contract BLOCKER 2). The four lines are byte-identical to the
   candidates document's draft and sit as the final four bullets of `## Writing voice`.
3. Every load-bearing line named in the pick table is still present inline in `CLAUDE.md`,
   checked one by one. The reviewer names any missing one as a blocking finding.
4. The retained pick 5 bullet no longer contains "blocks to completion" and states the exit-75
   re-issue.
5. Every pointer resolves. For each, the implementer pastes a `test -f` result for the named
   destination, and for picks 1 and 3 (and 4 if reached) pastes a `grep` hit proving the
   destination carries the displaced content.
6. No pointer is written as an `@`-import, proved by grepping the diff for a leading `@` on a
   markdown path reference and finding none.
7. The applied set is exactly picks 1, 2, 3, and 5, or that set plus pick 4 with the measured
   total that forced it pasted in the report.
8. `~/Projects/cairn-cms/CLAUDE.md` is untouched, proved by `git -C ~/Projects/cairn-cms status
   --short` showing no change to it.
9. The commit names only `claude/.claude/CLAUDE.md`, resolved through the reported SHA.
10. No em dash appears in the diff.
11. `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` prints `gate exit:
    0`.

---

### Task 9: `pass-execute.js` and its skill text

**Model:** `sonnet`. **Depends on:** task 0, and it runs **last among behavior-changing tasks**,
after task 8, because it edits the runner segments A and B execute. **Deliverables:** 4.
**Independent:** yes, and it must be ordered last.

**Files:**

- Modify: `claude/.claude/workflows/pass-execute.js`

**Precondition, cleared by the conductor before dispatch** (mechanics MAJOR 5, domain MINOR 3).
The implementer does not run this check; a Workflow run lives inside the harness process and a
subagent cannot see another session's runs. The conductor re-runs task 0's criterion 6
mechanism at the segment-C boundary and the dispatch asserts it was cleared. If the check does
not clear, the conductor defers this task per the segment-C launch condition and task 10
records it as owed.

**Outcome.** The runner stops telling every implementer a falsehood about the gate, stops
forcing a plan to paste the same protocol text into every task's `notes`, and documents the
invocation shape that actually works.

**The four changes, each from a recorded finding.**

1. **The gate wording (`pass-execute.js:136`).** The line says the runner "blocks to completion
   and prints the tail". That is the same false claim task 1 corrects in two agent definitions,
   and this line reaches every implementer the runner dispatches. Replace it with the property
   list above, "The exit-75 reattach protocol, as a property list", including the
   vanished-status property. Keep it to one prompt line.
2. **One shared-notes field appended at prompt time.** The finding, from the dubplate window:
   the protocol block every task needs is pasted into every task's `notes` because the script
   has no one field it appends at prompt time. `pass-execute-chains.js` has one,
   `a.paintProtocol`, appended in both `implementPrompt` (`:75`) and `reviewPrompt` (`:104`).
   **The argument is named `commonNotes`** (ruling 4, mechanics MINOR 7). It is a top-level
   optional argument, absent by default, and **appended to every implement prompt after the
   task's own `notes` line** (ruling 4; this placement is deliberate and differs from the
   chains precedent, which appends inside the criteria line, per domain MINOR 7). Follow the
   precedent the file already set for its optional arguments: `reducedGate` (`:16-19`,
   `:144-146`, `:157-159`), `mutationLedger` (`:47-62`), and `severity` (`:85-88`) are each
   absent-by-default, and absence leaves behavior exactly as it is today. Validate nothing new
   in `validateArgs`, since the argument is optional.
3. **The segment launch shape, in the skill text.** There is no `SKILL.md` for this workflow;
   `grep -rl "pass-execute" ~/.dotfiles/claude/.claude/skills` returns only `site-pass` and
   `cairn-pass`, which reference it in passing. The skill text is `meta` (`:30-39`, whose
   `name`, `description`, and `whenToUse` are what a session sees in the skill listing) and the
   header comment block (`:1-28`). Record there that the runner has no mid-run conductor hook,
   so a pass carrying conductor boundaries is launched one segment per invocation, with the
   conductor's checkpoint and batched simplifier round falling at each boundary. Record also
   that `repo` is prompt text only and that every gate string is absolute per tree, which is why
   a worktree run passes an absolute gate string.
4. **The header's own invocation example is the refused shape** (mechanics MAJOR 6, domain
   MAJOR 14). `pass-execute.js:8` shows `scriptPath: "~/.claude/workflows/pass-execute.js"`,
   and the Workflow tool refuses a `~/.claude/workflows` scriptPath. Correct the example to
   `Workflow({ name: "pass-execute", args: {...} })`, and state in the header that the runner is
   invoked by name, never by a path and never from a scratchpad copy, because a copy would make
   a later edit to this file invisible to the run.

**Constraints.**

- Change no existing behavior beyond the prompt text in item 1. A run with `commonNotes` absent
  must produce prompts identical to today's except that one corrected sentence.
- Do not touch `pass-execute-chains.js`. It is the cairn variant and a live cairn session holds
  it.
- Add no dependency, and keep the file's existing shape: `main()` holds every `await`, and the
  top level only calls and returns `main()` (`:270-272`).
- Comments in this file are JavaScript comments, so no em dash.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. `pass-execute.js` no longer contains "blocks to completion", and its gate line states exit
   75, the re-issue of the same command, the end condition, the vanished-status branch, and the
   ban on background runs and log polling.
2. `commonNotes` is optional. The reviewer confirms `validateArgs` does not require it, and
   that `implementPrompt` appends it only when present, immediately after the `notes` line,
   matching how `reducedGate` is handled at `:144` and `:157`.
3. With `commonNotes` absent, the diff changes no prompt line other than the gate sentence. The
   reviewer verifies this by reading both prompt builders, never by running the workflow.
4. `meta.whenToUse` or `meta.description` states the segment launch shape, and the header
   comment's invocation block documents `commonNotes` by name and shape.
5. The header comment's invocation example uses `name: "pass-execute"` and contains no
   `scriptPath`, and the header states that the runner is invoked by name and never from a
   scratchpad copy.
6. The header comment records that `repo` is prompt text only and that every gate string is
   absolute per tree.
7. `node --check claude/.claude/workflows/pass-execute.js` exits 0. The repo gate has no
   JavaScript leg, so this check is the syntax proof and is pasted in the report.
8. No em dash appears in the diff.
9. `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` prints `gate exit:
   0`.

---

### Task 10: Close, one fold agent drafting and then folding the ledgers

**Model:** `sonnet`. **Depends on:** tasks 1 through 9. **Deliverables:** 3. **Independent:** no.

**Files:**

- Create: `docs/superpowers/plans/2026-09-12-claude-infra-round-handoff.md`
- Modify: `docs/STATUS.md`
- Modify: `docs/HISTORY.md`
- Modify: `ROADMAP.md`

**Outcome.** The round's three ledgers are current, and the handoff document records what the
round left owed.

**The fold contract follows the standing rule** (contract MAJOR 5). `claude/.claude/CLAUDE.md`
at `:226` states that a pass's close task is authored by one fold agent, which commits its draft
and then folds, with one independent `diff-reviewer` read over the fold's diff. Revision 1
moved the fold to the conductor and asserted that the conductor owns the ledgers, which is a
divergence the plan did not name. Revision 2 follows the rule. This task makes **two commits**:
the handoff draft first, then the fold. The conductor dispatches one independent `diff-reviewer`
at `claude-opus-5` over the fold's diff, capped at one dispatch.

**What the conductor supplies in the dispatch.** The fold agent cannot see the round's spend or
the per-task reviewer verdicts. The dispatch `notes` carry the per-task reports, every commit
SHA per repo, each task's fix-round count and reviewer verdict, and the measured spend against
the 1.5M ceiling.

**The three drafts, each as its own section of the handoff document, then folded.**

1. **The `docs/STATUS.md` draft.** Present tense only, and it must keep the file under the
   60-line cap after folding. It restates the gate line if any task changed what the gate
   covers, records the hoisted homes and the two new docs, and points the immediate next action
   at whatever this round left owed.
2. **The `docs/HISTORY.md` draft.** One entry, newest first, naming what landed with each
   task's commit SHA, what the gate and the reviewer caught, the fix rounds each task took, and
   the budget outcome against the 1.5M ceiling. Its "What a later pass would be wrong to
   rediscover" list is the entry's reason for existing, and must carry at least: the five
   folded `~/.claude` directory symlinks, so no later pass plans a `stow -R claude` it does not
   need; that the dotfiles gate reads repository markdown only through gitleaks; that
   `claude/.claude/CLAUDE.md` grew 3,812 bytes in four days, which is why the four ranked
   displacement candidates stopped being sufficient; and that a displacement pointer must keep
   its section's load-bearing lines inline, because a preserved trigger that fires after the
   decision is already made is not a trigger.
3. **The `ROADMAP.md` draft.** Whether any item this round touched belongs in Active, Planned,
   or Someday, and whether the cairn documentation standard's Active entry needs amending now
   that the workstation `CLAUDE.md` carries its four lines.

**The owed follow-ups the handoff must record.**

- poplar's `CLAUDE.md` names no architecture reader, so `go-architecture-reader` is available
  to poplar and dispatched by nothing. The amendment is poplar's own pass (domain MAJOR 11).
- `~/Projects/cairn-cms/CLAUDE.md` is over the cap and owes its own four docs-standard lines.
- Whether `aksailingclub-org`, `xcathletes-org`, or `cairn-pub` wants a `CLAUDE.md` pointer at
  `~/.claude/instructions/`, which this round deliberately did not add.
- Whether the working runaway guard at `~/.cache/cairn-overnight-2026-09-12/runaway-guard.sh`
  should be copied into `bin/.local/bin/` as an armable form.
- Task 9, if the segment-C launch condition deferred it.

**Constraints.**

- Every SHA, count, and byte figure in the drafts and the fold is quoted from the per-task
  reports the dispatch supplies, or measured directly. Report any figure you could not source
  in `couldNotDo` rather than estimating it.
- Cite no plan line numbers in any file this round shipped. Process citations belong in the
  handoff document, never in a shipped comment or agent definition.
- The handoff commit and the fold commit are separate, in that order.

**Acceptance criteria a diff-reviewer verifies from the diff.**

1. The handoff document carries exactly three draft sections, one per ledger, each labeled with
   the file it is for, plus the owed-follow-ups list.
2. Two commits exist. The first names only the handoff document. The second names only
   `docs/STATUS.md`, `docs/HISTORY.md`, and `ROADMAP.md`.
3. Every commit SHA the drafts name resolves with `git cat-file -e`, and the reviewer checks
   each one.
4. `docs/STATUS.md` is at or under 60 lines after the fold, proved with `wc -l`.
5. The HISTORY entry's "wrong to rediscover" list carries the four findings named above.
6. **No process citation appears in any file this round shipped**, proved by grepping the
   round's touched files for the citation shapes rather than the plan's filename: `task [0-9]`,
   `rung`, `plan`, and a bare `:[0-9]+-[0-9]+` line range (contract MINOR 16).
7. The owed-follow-ups list carries every item named in this task's constraints.
8. No em dash appears in the diff.
9. `cairn-run-gate 'cd /var/home/glw907/.dotfiles && bash scripts/check.sh'` prints `gate exit:
   0`.

---

## Task ledger

| # | Title | Model | Depends on | Deliverables | Independent | Segment |
|---|---|---|---|---|---|---|
| 0 | Coordination check and launch conditions | conductor, no dispatch | none | 1 | yes | pre-A |
| 1 | Exit-75 reattach protocol in two implementers | `sonnet` | 0 | 2 | yes | A |
| 2 | The two guards-doc corrections | `sonnet` | 0 | 2 | yes | A |
| 3 | The `svelte-check` skill hoist | `sonnet` | 0 | 2 | yes | A |
| 4 | The two instruction files, hoisted and supplemented | `sonnet` | 0 | 4 | yes | B |
| 5 | Hoist `go-architecture-reader` | `sonnet` | 0 | 2 | yes | B |
| 6 | The carried model-economy update | `sonnet` | 0 | 2 | yes | B |
| 7 | The two displacement destination documents | `sonnet` | 2 | 2 | no | B |
| 8 | CLAUDE.md displacement and the four lines | `sonnet` | 7 | 5 | no | C |
| 9 | `pass-execute.js` and its skill text | `sonnet` | 0, ordered last | 4 | yes | C |
| 10 | Close, one fold agent's drafts and fold | `sonnet` | 1 to 9 | 3 | no | C |

Ten dispatched tasks against seven ruled items, plus one conductor task. Two ruled items split
into two tasks each: the site-asset hoist (tasks 3 and 4) and the CLAUDE.md budget (tasks 7 and
8), both splits named in the revision note with their reasons. The remaining extra is the close
task. No task carries work the ruling did not name. Every reviewer dispatch is `diff-reviewer`
at `claude-opus-5`. **Independent means disjoint Files, never concurrent execution**; every
`pass-execute` invocation passes `parallel: false`.

## Item coverage

| Survey ruling item | Task |
|---|---|
| 1. The gate runner's reattach protocol in every implementer that uses it | 1 |
| 2. The unattended-work guards doc | 2 |
| 3. `pass-execute.js` and its skill text | 9 |
| 4. The global `CLAUDE.md` budget | 7, 8 |
| 5. Duplicated site assets hoisted to the workstation | 3, 4 |
| 6. `go-architecture-reader` to the workstation agents | 5 |
| 7. The three items carried from the 2026-09-04 Fable 5.1 pass | 6, which names all three and carries the one that is a workstation edit |

## Risks

- **`~/.claude` is live and this round has no feature flag.** Every task from 1 through 9
  changes what every session on this machine sees at the instant of the write. The mitigations
  are the live-surface rule in Global constraints, the requirement that `commonNotes` be
  absent-by-default, and the requirement that tasks 1 and 2 correct one step each rather than
  rewriting a file.
- **A half-landed round is additive only where a task adds.** Revision 1 claimed additive state
  across the round, which is false for tasks 3, 4, and 5, each of which deletes or rewrites a
  repo file (domain MAJOR 13). The mitigation is the create-before-delete rule in Global
  constraints, made a criterion in all three tasks, so a half-landed task leaves the consumer
  with the workstation copy rather than with neither.
- **Task 8 rewrites the file every later dispatch reads at session start.** It is ordered
  second-to-last among behavior-changing tasks for that reason, its displaced text stays
  reachable through a pointer, and every load-bearing line stays inline.
- **Task 3 makes a `svelte-check` skill visible in every project session.** Six SvelteKit repos
  gain it (`ecxc-ski`, `907-life`, `aksailingclub-org`, `xcathletes-org`, `cairn-pub`,
  `cairn-cms`), and dubplate's session sees it although dubplate's root has no `npm run check`.
  The mitigation is the four named deltas in task 3, which make the body read the repo's own
  `check` script and add the scope line the description needs.
- **Task 4 installs instruction files machine-wide.** The mitigation is ruling 3's split: the
  workstation body carries only universal content, the wrong secrets line is replaced by the
  global policy, and each repo's deploy facts stay in a supplement that also preserves the
  discovery path.
- **Task 9's precondition can defer it.** The cairn overnight run was live at this fold. The
  segment-C launch condition holds the segment until that run ends, and defers task 9 to a
  later round if it is still live at the 80% checkpoint. Tasks 8 and 10 do not depend on it.
- **The ceiling is derived, not measured.** No actual token spend is recorded for the
  comparable 2026-09-08 pass, so the 0.12M per-task rate is an inference from that plan's
  ceiling. The segment-A tripwire at 0.35M is the round's first real measurement of it.
- **The machine is on battery.** Task 0's launch conditions are the mitigation, and a
  stand-down at the battery floor halts this round before it halts the live cairn run.

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
