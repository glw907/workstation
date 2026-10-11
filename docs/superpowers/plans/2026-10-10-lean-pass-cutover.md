# Lean pass cutover: implementation plan

**Spec:** `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md` (authoritative; cited below as
"spec"). **Fold record:** `docs/superpowers/research/2026-10-10-lean-pass-process-fold.md` (its
dispositions stand; no task undoes one).

**Pass class:** `runner`, with the `live-account` flag (every step pushes branches, opens PRs, and
step 1 merges on GitHub). **Scope:** the spec's Rollout steps 1 to 4. Step 5 is the next action
named on the last line.

**Plan review:** three lenses (contract, mechanics, risk) at `a0cdfd5`, folded per
`docs/superpowers/research/2026-10-10-lean-pass-cutover-plan-fold.md`. The verification read runs
next, before step 1 launches (spec Lifecycle step 4).

**Clock estimate:** 1,990 task-minutes in all (step 1: 680, step 2: 510, step 3: 590, step 4: 210).
Steps 2, 3, and 4 launch together after session 1b's probes pass, and the heavy gate lock
serializes their heavy legs (Geoff, ruling R-C). Wall clock is about 680 + 460 = 1,140 minutes
(19 hours), with step 3 binding. That excludes Geoff's PR reads, his launch gaps, and heavy-lock
queueing between the concurrent steps.

**Where each step executes**

| Step | Session | Checkout | Branch | Launched by |
|---|---|---|---|---|
| 1a | build | `~/Projects/.worktrees/dotfiles-lean-cutover` (linked worktree of `~/.dotfiles`) | `lean-cutover` | Geoff, after the pre-launch |
| merge | none: Geoff's terminal | `~/.dotfiles` (main checkout) | `main` | Geoff |
| 1b | tag, probes, filing | `~/.dotfiles` (main checkout), started after the merge | `main` | Geoff, in the merge block |
| 2 | cairn-cms | `~/Projects/cairn-cms/.claude/worktrees/lean-cutover`, made by the session's `EnterWorktree` | the one `EnterWorktree` creates (M2) | 1b, with `claude --bg` (R-D) |
| 3 | sites, cairn-pub, dubplate | started in `~/Projects`; edits land in `~/Projects/.worktrees/<repo>-lean-cutover` | `lean-cutover` per repo | Geoff |
| 4 | docs-chain audit | `~/.dotfiles/.claude/worktrees/docs-chain-audit`, made by the session's `EnterWorktree` | the one `EnterWorktree` creates (M2) | 1b, with `claude --bg` (R-D) |

Every session runs `sonnet` at `medium` under the user's `auto` mode. 1a, 1b, and 3 run interactive
in a terminal tab (M1), since each must sit in an existing checkout (Spec gaps). Steps 2 and 4 run
as self-isolating `claude --bg` sessions that 1b starts from each repo's main checkout (M2; Geoff,
ruling R-D). Every launch reads its prompt from a committed file in
`2026-10-10-lean-pass-cutover-prompts/` beside this plan, as `"$(cat <file>)"`: a prompt pasted
inside double quotes loses each backticked span to command substitution. The `--name` is the
session's recorded handle.

## Conventions every task follows

- **Task fields.** Each task gives its outcome, files, risk class, audit inputs where it rewrites a
  file the infra audit targets, acceptance check, test, and clock estimate in minutes. Acceptance is
  a command or an observable state. A task is done only when its acceptance passes.
- **Commits.** One commit per task, subject starting with the task id (`S1-T5: Rewrite pass-core to
  the lean lifecycle`), imperative mood, specific files only, never `git add -A`. A task with no file
  change makes no commit and says so in its notes.
- **Resume.** A relaunch with the same launch prompt finds the done tasks by `git log --oneline` on
  the step's branch (task ids in subjects) and starts at the first task whose acceptance fails. A
  `--bg` step resumes in its own worktree with `claude --bg --resume <session-id>`, which "continues
  that session in the background under the same ID" (`claude --help`).
- **Gates.** Every gate runs through `cairn-run-gate '<string>'`, re-issued on exit 75 until it
  prints `gate exit:`, with the Bash tool's `timeout: 600000` (source M7). Per-repo gate strings are
  in each step.
- **Stops.** A stop writes the step's `docs/STATUS.md` on its branch (present tense: the task in
  flight, what failed, the one question), runs `notify-send -u normal "lean cutover: <step> stopped"`,
  and waits. Stops are: a live session or a warm unauthored change in a file the task must commit
  (see "One-executor rule"); a red the session cannot fix in two attempts; a whole-branch review
  `escalate`; a finding that would change the approved design (one batched question, spec Lifecycle
  step 3); and, in steps 2 to 4, the clock stop (spec Execution item 6, ruling 13).
- **One-executor rule.** A live session whose `cwd` is in a repo (`claude agents --json`) is a stop
  for any commit in that repo outside the step's own worktree. Before a task commits on a default
  branch in a main checkout, `git -C <repo> diff --quiet HEAD -- <the files it writes>` must pass,
  or it stops. Other uncommitted files, in any checkout, are another session's work: no task
  stages, commits, stashes, or discards them.
- **Pushes.** Every launch prompt names its push targets as `glw907/<repo>`, since auto mode trusts
  the session's start directory and its remotes and blocks a push to any other repository unless
  the user named it (M1). No session pushes a default branch except where a task says so, and no
  session merges a PR.
- **Scope.** A discovered item outside the task goes to the PR body's "Found, not done" list, never
  into the task in flight. cairn friction goes to cairn-cms `docs/internal/docs-friction-log.md` only
  from step 2 (ruling 8: the friction log stays in cairn only). Steps 1, 3, and 4 never write
  cairn-cms, so their PR bodies list the friction they meet as owed to that log.
- **PR body.** Every step's PR body carries: what landed (task id, commit); each `auth-data` verdict
  (none is expected in steps 1 to 4); the whole-branch review verdict with a disposition per finding;
  the audit ids each task took, each marked absorbed, already fixed at HEAD, or superseded; "Found,
  not done"; and the score: the spec's Execution price table rows (Gates on the critical path, Work and
  review, CI waits on the path, Fix rounds and reds, Close, Total) for this step, gate and lock time
  from `cairn-run-gate --records <toplevel> <branch>`, the clock from the first execution commit to
  PR-ready, and the attended events (spec Success test). A HISTORY harvest reports counts per
  disposition (moved, owed, dropped) first, then lists the owed and dropped rows by heading and
  bullet index without quoting the bullet; the full table, one row per bullet with its home, goes
  in a collapsed `<details>` block.
- **Writing.** Prose follows the workstation writing voice; `scripts/check.sh` runs the Vale and
  tellgrader nets in dotfiles. Caps: a `CLAUDE.md` under 200 lines, a skill body under 500 (spec,
  Instruction surface).

## Sources the tasks rely on

Each mechanism below was read or probed on 2026-10-10. Tasks cite them as M1 to M16.

- **M1, interactive launch under auto mode.** `claude --help` (2.1.296): "starts an interactive
  session by default"; positional `prompt` "Your prompt"; `-n, --name <name>` "Set a display name for
  this session"; `--effort <level>` takes "low, medium, high, xhigh, max"; `--model` takes an alias
  such as 'sonnet'. `claude agents --json` (probed) lists interactive sessions with `pid`, `cwd`,
  `kind: "interactive"`, and `name`. `~/.claude/settings.json:11` sets `"defaultMode": "auto"`, which
  applies from user settings (code.claude.com/docs/en/permission-modes). Auto mode allows by default
  "Pushing to any branch of the repository you're working in"; "The classifier trusts your working
  directory and the remotes that were configured for it when the session started"; it blocks
  "pushing to a third-party repository, unless you named that external target" and "Merging a pull
  request no human has approved". Writes under `.claude` and `.git` are protected paths, "Routed to
  the classifier" in auto mode. Both `~/.dotfiles` and `~/Projects` are trusted in `~/.claude.json`.
- **M2, the self-isolating `--bg` launch (Geoff, ruling R-D).** code.claude.com/docs/en/agent-view,
  "How file edits are isolated": "When you dispatch a background session from agent view or start one
  with `claude --bg`, the session starts in your working directory. Before editing files, Claude
  moves the session into an isolated git worktree under `.claude/worktrees/`". There it "commits
  without asking, and pushes the branch when the repository has a remote", and never does "pushing
  to `main` or `master`, force-pushing, and merging". "Your git instructions take precedence: if the
  task, `CLAUDE.md`, or memory says you handle committing or pushing yourself, Claude leaves git to
  you." "A session editing a checkout it didn't isolate itself still asks before committing ... when
  the session started inside a worktree that already existed." Before the move it "can't use the
  `Edit`, `Write`, or `NotebookEdit` tools on the shared checkout"; Bash is not among them, so a
  setup run before the move would write the shared checkout. This harness's `EnterWorktree` tool
  schema: it "creates a new git worktree inside `.claude/worktrees/` on a new branch", and under
  `"head"` it "branches from your current local HEAD" (M4). A `--worktree` branch is
  `worktree-<name>` (worktrees page), and S1-T17b records the name `EnterWorktree` gives. `claude --help`: `--bg` "Start the session in the background and return
  immediately. Prints the id". Changelog v2.1.221: "Changed background sessions to commit and push to
  preserve work, open a draft PR only when the task calls for one, follow your CLAUDE.md git
  instructions". The permissions page: from a script, `claude --bg` in an untrusted directory "exits
  with a `Workspace not trusted` error", and trust "covers the whole repository apart from any git
  repository nested inside it". The agent-view page: "Agent view is in research preview."
- **M3, manual worktrees.** code.claude.com/docs/en/worktrees, "Manage worktrees manually": `git
  worktree add ../project-feature-a -b feature-a`; "A worktree is a fresh checkout, so initialize your
  development environment there."
- **M4, `worktree.baseRef`.** worktrees, "Choose the base branch": `{"worktree": {"baseRef":
  "head"}}`; `"head"`: "branch from your current local `HEAD` ... Use this when isolating subagents
  that need to operate on in-progress work. Inside a worktree, `"head"` resolves to that worktree's
  `HEAD`". "Subagent worktrees use the same base branch as `--worktree`, so they branch from your
  repository's default branch unless `worktree.baseRef` is set to `"head"`." Subagent worktrees are
  removed "when the subagent finishes without changes; a worktree with changes stays on disk".
- **M5, Agent tool.** This harness's Agent tool schema: `isolation: "worktree"` "creates a temporary
  git worktree so the agent works on an isolated copy of the repo"; `model` is one of `sonnet`,
  `opus`, `haiku`, `fable`; `subagent_type` picks the agent.
- **M6, PostToolUse hook output.** code.claude.com/docs/en/hooks: return `{"hookSpecificOutput":
  {"hookEventName": "PostToolUse", "additionalContext": "<text>"}}`; stdout is parsed as JSON output
  when "the whole output is one JSON object"; for PostToolUse, plain stdout goes to the debug log, not
  to Claude. Common input field `cwd`: "Current working directory when the hook is invoked"; "the
  `cwd` field ... is the worktree root after Claude enters a worktree, and the new directory after
  Claude runs `cd`." The stowed `claude/.claude/settings.json:52` already uses `"matcher": "*"`.
- **M7, background Bash.** The harness Bash tool: `run_in_background` "keeps running across turns and
  re-invokes you when it exits"; `timeout` maximum 600000 ms.
- **M8, gh.** `--help` output, gh on this machine: `gh pr create --draft --body-file <file>`, `gh pr
  ready`, `gh pr checks <n> --watch --fail-fast`, `gh pr merge <n> --merge --match-head-commit <sha>`,
  `gh pr list -R <owner/repo> --head <branch> --state merged`.
- **M9, Playwright sharding.** playwright.dev/docs/test-sharding: "pass `--shard=x/y` to the command
  line"; a GitHub Actions matrix of `shardIndex` and `shardTotal` running
  `--shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}`; set the `blob` reporter on CI, "Blob
  report names contain shard number, so they will not clash", then `npx playwright merge-reports`.
- **M10, stow.** Global `CLAUDE.md`: "New script: `bin/.local/bin/` + `stow -R bin`".
  `~/.local/bin/cairn-run-gate` is a per-file link into `~/.dotfiles/bin/.local/bin/`, and
  `~/.claude/{agents,docs,skills,workflows,tooling,settings.json,CLAUDE.md}` are links into
  `~/.dotfiles/claude/.claude/` (`ls -la`), so a merge into the main checkout is live machine-wide at
  once and a new `bin` script needs `stow -R bin`.
- **M11, the ratchet.** `claude/.claude/tooling/ratchet.py` header: "a new entry under an id already
  registered in HEAD fails". `retired-phrases.txt` header: the scanner "fails on any listed phrase
  outside a line also carrying the literal marker `retired-ok`", case-insensitive, wrap-tolerant, over
  `.md` and `.js` in `claude/.claude` (agents, authored and vendored skills except `skills/synced`,
  workflows, `docs` except `docs/record`, output styles, instructions, `CLAUDE.md`). So a newly
  retired phrase must reach zero hits, since it cannot be baselined.
- **M12, nested instruction files.** Observed in the planning session on 2026-10-10: reading a file
  under `claude/` loaded `claude/.claude/CLAUDE.md` and listed `claude/.claude/skills` as
  `claude:<name>` skills. A session in a dotfiles worktree therefore sees that worktree's in-progress
  `CLAUDE.md` and skills once it reads under `claude/`. Until step 1 merges, the spec governs over
  them.
- **M13, dotfiles gate.** `bash scripts/check.sh` at `ca066b1`: green, 75.7 s elapsed, largest process
  105 MB RSS (`/usr/bin/time`, 2026-10-10). It fits the light lane's 3G cap (`cairn-run-gate:29-34`).
- **M14, cairn worktree setup.** cairn-cms `.github/workflows/e2e.yml:47` runs `npm ci` and `:56` runs
  `npm ci --prefix examples/showcase`; `docs/internal/durable-gotchas.md`, "A worktree showcase e2e
  proves MAIN's engine": a worktree's showcase resolves the main checkout's engine "until a
  from-scratch `npm install` in the worktree's showcase repoints both `file:` deps".
- **M15, memory peak.** `systemd-run --user --wait -P -d <command>` prints `Memory peak: <n>` for the
  whole unit on exit (probed with systemd 259). The service gets the user manager's environment, so
  pass `-E PATH="$PATH"`.
- **M16, cwd and reload.** The binary resets the shell cwd after a `cd` that leaves the allowed
  working directories ("Shell cwd was reset to ...", function `Eor`), and its subagent prompt says
  "Agent threads always have their cwd reset between bash calls". code.claude.com/docs/en/settings,
  "When edits take effect": "Claude Code watches your settings files and reloads them when they
  change, so it applies most edits to the running session without a restart, including edits to
  `permissions`, `hooks`"; `model` and `effortLevel` are read only at session start.
  code.claude.com/docs/en/memory: CLAUDE.md and auto memory "are loaded at the start of every
  conversation". So a merge into the main checkout reaches every live session's settings and hooks
  at once, and only a session started after it carries the merged `CLAUDE.md`.

## Rules inventory for the three process docs

The spec's table requires this plan to list every rule in `model-economy.md` (227 lines),
`pass-gate-economy.md` (116), and `unattended-work-guards.md` (142), each with a home or a deletion by
name. S1-T5, S1-T8, and S1-T10 carry it out. After S1-T10, `model-economy.md` and
`pass-gate-economy.md` no longer exist and `unattended-work-guards.md` holds only the rows homed there.

**`model-economy.md`**

| Id | Rule | Home or deletion |
|---|---|---|
| ME-1 | Seat table | `pass-core` "Models": design and plan authorship `claude-opus-5-5` at `high`; the executing session `sonnet` at `medium`; pair subagents `sonnet` at `medium` (spec Lifecycle preamble: medium unless stated); reviewers `claude-opus-5-5` through agent frontmatter. Deleted: the conducting-execution seat (spec, Retired: the conductor) and the gate-runner seat (its runners are deleted). The docs-chain seats stay as defaults in `docs-page-chain.js`'s header args, where they execute. |
| ME-2 | Fable 5.1 only after Opus 5.5 at `xhigh`, then `max`; per dispatch, never a session switch or frontmatter pin | `pass-core` "Models" |
| ME-3 | Reviewer effort `medium`, security review `high` | Agent frontmatter (executes); rationale deleted (the spec's guidance file holds it) |
| ME-4 | An overruled verdict is stated with its reason; a correctness-critical overrule takes `xhigh` | `pass-core` "Close": stated with its reason in the PR body; a correctness-critical overrule re-runs the review at `xhigh` |
| ME-5 | The conductor is thin | Deleted (spec, Retired) |
| ME-6 | The per-task chain replaces the conductor's diff read | Deleted (spec, Retired; per-task review only on `auth-data`, Execution item 5) |
| ME-7 | The six pass classes set the ceremony | Deleted; replaced by risk classes (spec Lifecycle preamble) in `pass-core` "Lifecycle" |
| ME-8 | The Haiku seat reads and copies, never decides; keep a Haiku dispatch under 100k context (5x price above) | `pass-core` "Models" |
| ME-9 | Undeclared dispatches fall to `sonnet` through `CLAUDE_CODE_SUBAGENT_MODEL` in `settings.json` `env`; frontmatter and per-dispatch `model` win; a settings value outranks the shell | `claude/.claude/docs/claude-tooling.md`, new short "Model defaults" section |
| ME-10 | `low` effort only for mechanical subagents, never Fable; `max` is one session-only adjudication; `/effort` persists into `settings.json` through the stow link, so reset it | `low` and `max`: `pass-core` "Models". The `/effort` persistence fact: `claude-tooling.md` "Model defaults" |
| ME-11 | Brainstorm length is never trimmed for product and taste; method calls are Claude's | Global `CLAUDE.md` "Process proportionality" (stays) |
| ME-12 | The pass-end score (tokens against the ceiling, planning misses, sittings, clock rows) | `pass-core` "Score": the spec's five rows, attended events, and escapes (spec Close and Success test). Deleted: the token ceiling (spec, Retired) and the planning-miss count. |
| ME-13 | Pricing table, the Max allowance, overflow to credits, Fable 5.1's effort-dependent saving | `claude/.claude/docs/fable-post-cutoff-system.md`, new "Pricing and allowance" section |
| ME-14 | The conductor self-check and its origin incident | Deleted (spec, Retired) |
| ME-15 | Pass sizing: a grant is not headroom; accretion by adjacency; split counting; deliverable counts; route discovered work; never add scope to a task in flight | `pass-core` "Scope": a grant authorizes a mechanism or a boundary, never more work; discovered work goes to the PR body or ROADMAP, never into a task in flight unless the task would otherwise build on something known wrong (say so). Deleted: the split-count ladder and the deliverable count (task clock estimates and the clock stop replace them, spec Execution item 6). |
| ME-16 | The dated History entries | Deleted (ruling 8: git holds history). Each surviving fact already executes elsewhere: subagent default (ME-9 home), Opus docs drafter (`docs-page-chain.js` `drafterModel`), reviewer Opus pins (frontmatter), front-loaded interaction (`CLAUDE.md` "Process proportionality"). |
| ME-17 | Research basis links | Deleted; `docs/superpowers/research/2026-10-10-anthropic-agentic-guidance.md` is the record |

**`pass-gate-economy.md`**

| Id | Rule | Home or deletion |
|---|---|---|
| PG-1 | The per-task gate is the blast radius; the full gate is CI green where a command exists; measured baselines | `pass-core` "Gates" (spec Execution items 3 and 4) and each adapter's fast lane and full-suite home (ruling 11). Baseline numbers deleted (in the spec's evidence). |
| PG-2 | Reduced fix rounds by `commentOnly`, `testOnly`, `coverageOnly` | Deleted with the runners |
| PG-3 | The pass class sets the ceremony | Deleted (risk classes replace it) |
| PG-4 | A task touching no engine source runs the consumer's own unit suite | `site-pass` "Fast lane" |
| PG-5 | Gate receipts replace reruns on an unchanged tree | `cairn-run-gate` header (executes) and one line in `pass-core` "Gates" |
| PG-6 | The pre-flight checklist in task notes | Implementer definitions keep two items: no comment claims more than its assertion proves; no process citations in shipped comments. Deleted: the labeled report block, the counts, and re-emit (the chain report shape goes, spec table). |
| PG-7 | Task 0 takes no gate; the lane baseline is the conductor's call | Deleted (lanes and the conductor retired) |
| PG-8 | The cross-lane review fires on a disjunction | Deleted; the whole-branch close review reads merged pair work (spec Close) |
| PG-9 | A gate that scopes gitleaks to the change set owes one branch-history `gitleaks detect` | The close checklist of each adapter whose gate scopes gitleaks; S1-T6 checks cairn's and the sites' gates, S3-T7 checks dubplate's |
| PG-10 | Gates run through `cairn-run-gate`; re-issue on 75; never poll a log | `cairn-run-gate`'s exit-75 output (executes; S1-T3 adds the timeout) and one line in `pass-core` "Gates" |
| PG-11 | Parallel work where files are disjoint; a shared port as an environment variable; fold single-deliverable tasks into a neighbor; overlap a CI baseline regen with review | `pass-core` "Pairs" (disjoint files, generated outputs included; a shared port is an environment variable) and `pass-core` "Lifecycle" plan step (fold a single-deliverable task into a neighbor). The regen overlap is deleted. |
| PG-12 | Orchestrator hygiene: halt agents prepend STATUS; merge resolution rules; workflows by name with the stale-copy `cmp`; one protocol field | By-name invocation and the stale-copy `cmp` procedure: `claude-tooling.md` "Workflows". The rest deleted (runners and HISTORY retired; a pair conflict stops the line, spec Execution item 2). |
| PG-13 | Sessions sharing the heavy lock coordinate (four rules) | Trimmed `unattended-work-guards.md`, new "Shared gate lanes" section; one pointer line in `pass-core` "Gates" |
| PG-14 | One full gate per machine; memory caps; the light lane for browserless gates; the `gateLane` arg; a resumed pass lands the nearest chain first | Caps and lanes: `cairn-run-gate` header (executes) and "Shared gate lanes" (light only when a measured peak fits the 3G cap, spec Execution item 3). The `gateLane` arg and the chain-resume rule are deleted. |
| PG-15 | `code-simplifier` once per pass at the close | Deleted (spec table: removed from the process); the phrase is retired in S1-T12 |
| PG-16 | The cairn close calls one `npm run check:close` | `cairn-pass` "Close checklist" |
| PG-17 | Never edit a script a running gate executes | "Shared gate lanes" |

**`unattended-work-guards.md`** (rows stay in the trimmed file unless noted)

| Id | Rule | Home or deletion |
|---|---|---|
| UG-1 | Runaway guard for a workflow run past ~30 minutes (`claude-wf-guard`, journal then transcripts, TaskStop and `resumeFromRunId`, prompt-side prevention) | Stays (it still guards `docs-page-chain` runs; fold root 5) |
| UG-2 | The sleep inhibitor is tool-held (lease, `cairn-run-gate`'s own hold, `awake`) | Stays |
| UG-3 | Both channels; inhibit `suspend`, never `suspend:idle` | Stays |
| UG-4 | Verify, never arm | Stays |
| UG-5 | Battery floor; the 11% stand-down | Stays; the stand-down names "the executing session or workflow" |
| UG-6 | The API-drop wake-up (`/loop`, dynamic pacing, 1200 to 1800 s fallback) | Stays, retargeted from the conductor to the executing session; `pass-core` "Execute" names it (spec Execution item 1) |
| UG-7 | Restart recovery re-arms the full set | Stays; the set gains the `/loop` wake-up and the lid-switch hold |
| UG-8 | Concurrent sessions: guards stack; name each inhibitor; touch only your own | Stays |
| UG-9 | The lid switch ignores the sleep inhibitor; hold `handle-lid-switch` | Stays; `pass-core` "Execute" names it (spec Execution item 1) |

## Audit inputs

The rule (dotfiles `docs/STATUS.md`, "Infra sweep after the cutover"): an audit item is superseded
when the cutover rewrites or deletes the file it targets, and the rewriting task takes that item's ids
as inputs. Audit: `claude/.claude/docs/record/2026-09-28-claude-infra-audit.md`. A task verifies each
id at HEAD, folds what still applies, and records each as absorbed, already fixed, or superseded in
the PR body. A file the cutover only sweeps (edits retired wording in) keeps its audit items for their
own pass; the sweep task takes none of them except PS-11, named in S1-T12.

| Task | File | Audit ids |
|---|---|---|
| S1-T3 | `cairn-run-gate` | AW-17, AW-20 (the tool owns the protocol text) |
| S1-T5 | `pass-core` | PS-13 (with DC-01), PS-14, PS-16 (with DC-03), PS-23 (with AW-11), PS-24 (with DC-21); A-rest's `pass-core` close wiring (superseded, not carried) |
| S1-T6 | `cairn-pass`, `site-pass`, `plan-template.md` | PS-02 (the `cairn-pass` pointer row), PS-09, PS-17 (template half), PS-22, PS-25 (`cairn-pass` half), DC-03 (`site-pass:28`), the audit's code-simplifier row (`plan-template.md:48`) |
| S1-T7 | `spec-plan-review` | PS-12, PS-15 |
| S1-T8 | `diff-reviewer`, both implementers, `go-architecture-reader` | AW-04, AW-05, AW-18, AW-19, AW-20, AW-21, AW-23; the audit section 4 rows for the DaisyUI v5 copies, the commit-footer copies, and the pre-flight parity list |
| S1-T9 | global `CLAUDE.md` | DC-01, DC-03, DC-04, DC-08, DC-19, DC-21, DC-27, DC-29, DC-30, AW-24 (its `CLAUDE.md` part) |
| S1-T10 | the three process docs | DC-04 (guards half), DC-06 (the `fable-post-cutoff-system.md` pointer it gains), PS-14 (model-economy half), A-rest's seat check `seats.json` (superseded, not carried), the owed runaway-guard script question (superseded) |
| S1-T11 | `pass-execute.js`, `pass-execute-chains.js` | AW-01, AW-02, AW-03, AW-04, AW-05, AW-06, AW-11, AW-12, AW-13; DC-04's runner-launch NOTE half |
| S1-T12 | `log-project` (sweep) | PS-11, read under ruling 8 (no HISTORY close) |
| S2-T1 | cairn-cms `CLAUDE.md` | DC-03 (line 73), PS-14 (line 82), DC-18, DC-22 (repo side), DC-24, PS-25 (repo side); the owed cairn `CLAUDE.md` trim |
| S3-T2 | ecxc-ski | DC-02, DC-13, DC-17 (stub), DC-22, DC-23 (ecxc half; its dotfiles half is pass C's, so record it deferred) |
| S3-T3 | 907-life | DC-02, DC-13, DC-14, DC-17 (stub), DC-22 |
| S3-T4 | aksailingclub-org | DC-09 (pointer), DC-15, DC-22 |
| S3-T5 | dubplate | the owed `dubplate-implementer` gate-string note (superseded by the file's deletion) |
| S3-T6 | xcathletes-org | DC-03 (line 95) |
| S4-T3 | `docs-page-chain.js` | AW-10 (landed in style-guide-sync W1r; verify) |

Chain W of style-guide-sync merged into dotfiles (`fc53c6e`, `53c5b09`, `d97d9d0`). Its lines in
files this plan rewrites must survive: the implementers' "track's drafting brief" lines
(`cairn-implementer.md:67`, `site-implementer.md:60`), `site-implementer.md:111`'s
`npm run check:docs-gate -- --page <page>`, and the global `CLAUDE.md` "Writing voice" naming the
developer brief in `docs-register.md`.

## Step 1: workstation repo

The spec's Rollout step 1: every spec table row that lives in `~/.dotfiles`, both adapters included,
plus the sweep. It runs serially, with no pairs and no clock stop (the new settings and gate go live
only at the merge). Done when `scripts/check.sh` is green, the one-executor check is clear in every
repo, the merge is live, and both probes pass.

### Pre-launch for 1a (the planning session, with Geoff present)

1. Run S1-T1 below and settle any stop with Geoff before going on.
2. Commit this plan, its prompt files, its review records, and `docs/STATUS.md` carrying S1-T1's table on `main`, and
   push. Assert that every touched repo's default branch is at ahead 0 (Geoff, ruling R-A: all were
   pushed on 2026-10-10; this re-checks for anything landed since). Any output line is a stop for
   Geoff, now:

   ```bash
   for r in ~/.dotfiles ~/Projects/{cairn-cms,ecxc-ski,907-life,aksailingclub-org,xcathletes-org,cairn-pub}; do
     [ "$(git -C "$r" rev-list --count origin/main..main)" = 0 ] || echo "AHEAD: $r"; done
   [ "$(git -C ~/Projects/dubplate rev-list --count origin/master..master)" = 0 ] || echo "AHEAD: dubplate"
   ```

   From here until the merge block, dotfiles `main` is frozen: no session commits to it.
3. Create the worktree and confirm a green baseline (no setup command is needed, M13). The `cd`
   leaves the session's working directory, so it resets after each call (M16): run the `cd` and the
   gate in one Bash call, and repeat both on exit 75.

   ```bash
   git -C ~/.dotfiles worktree add ~/Projects/.worktrees/dotfiles-lean-cutover -b lean-cutover main
   cd ~/Projects/.worktrees/dotfiles-lean-cutover
   CAIRN_GATE_LANE=light cairn-run-gate 'bash scripts/check.sh'
   ```

4. Geoff opens a new terminal tab and launches 1a (M1); the planning session then ends.

   ```bash
   cd ~/Projects/.worktrees/dotfiles-lean-cutover &&
   claude --model sonnet --effort medium --name lean-step1a "$(cat ~/.dotfiles/docs/superpowers/plans/2026-10-10-lean-pass-cutover-prompts/1a.txt)"
   ```

**Launch prompt (1a):** `2026-10-10-lean-pass-cutover-prompts/1a.txt`.

### S1-T1. One-executor check across every repo (pre-launch)

- **Outcome.** The planning session, with Geoff present, builds a table with one row per repo:
  `cairn-cms`, `ecxc-ski`, `907-life`, `aksailingclub-org`, `xcathletes-org`, `cairn-pub`, `dubplate`,
  `poplar`, and `~/.dotfiles`. Columns: live Claude sessions whose `cwd` is in the repo
  (`claude agents --json`, excluding the planning session); uncommitted files in the main checkout
  and each linked worktree (`git -C <path> status --short` over `git worktree list`), with the newest
  mtime; and the `docs/STATUS.md` next action, flagged if it names a pass in flight. Known at planning
  time: cairn-cms worktrees `docs-reset-dryrun`, `gate-tier-tool`, `polish-11b-i`, and
  `polish-11b-ii` carry September edits; engine pass B is paused in `.claude/worktrees/engine-pre-2b-b`;
  dubplate's main checkout carries agent-memory edits and untracked research, `reports/`, and
  `research_notes/` files.
- **Decision rule.** A live session in a repo is a stop. An uncommitted file under 24 hours old in a
  main checkout this plan commits on is a stop: dotfiles `main` (other than the planning session's
  own plan and review records) and dubplate's `docs/STATUS.md` and `ROADMAP.md`. Geoff settles
  either stop before launch. Every other row is recorded "stale, not touched"; steps 2 and 3 branch
  fresh worktrees from `origin`, so stale files elsewhere never contend. No task stages, commits, stashes, or discards another session's file.
- **Files.** Dotfiles `docs/STATUS.md` (the table, committed with the plan in pre-launch step 2; S1-T13
  moves it into the PR body).
- **Risk.** `ordinary`.
- **Acceptance.** All nine rows exist; every row is clear or "stale, not touched"; any stop has
  Geoff's ruling.
- **Test.** None (read-only).
- **Clock.** 15.

### S1-T2. Record rung 14a's hold and file ruling 11's item in dubplate

- **Outcome.** dubplate's `docs/STATUS.md` "Next action" and its lane-registry row for lane 1 say:
  rung 14a is held (ruling 12, lean pass process spec at
  `~/.dotfiles/docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`); its plan
  `docs/superpowers/plans/2026-10-10-rung-14a-admin-api.md` is re-planned as a lean task list in a
  fresh dubplate session after rollout steps 1 to 3 merge; the old plan stays as evidence.
  dubplate's `ROADMAP.md` gains one Planned item: add PR test CI that runs `bash scripts/check.sh` on
  `pull_request`; until it lands, the full-suite home is the local close gate (ruling 11).
- **Files.** `~/Projects/dubplate/docs/STATUS.md` and `~/Projects/dubplate/ROADMAP.md`, in one commit
  on dubplate `master` in its main checkout, after the One-executor rule's `diff --quiet` check on
  both files passes and `git -C ~/Projects/dubplate rev-list --count origin/master..master` prints 0.
  Then `git -C ~/Projects/dubplate push origin master`. A rejected push is a stop (never pull or
  rebase over the dirty agent-memory files).
- **Risk.** `ordinary`, `live-account`.
- **Acceptance.** `git -C ~/Projects/dubplate show --stat HEAD` lists exactly those two files;
  `grep -n 'ruling 12' ~/Projects/dubplate/docs/STATUS.md` prints the hold line; `grep -i 'PR test CI'
  ~/Projects/dubplate/ROADMAP.md` prints the item; `git -C ~/Projects/dubplate status -sb` shows no
  `ahead`; `git -C ~/Projects/dubplate status --short` lists the same files S1-T1 recorded.
- **Test.** None.
- **Clock.** 15.

### S1-T3. `cairn-run-gate` fixes

- **Outcome.** The spec's Execution item 7, in `bin/.local/bin/cairn-run-gate`:
  1. A finished run's status and log persist with the run's start fingerprint (`gate_fingerprint`,
     `cairn-run-gate:138`). A repeat call or a concurrent waiter reprints that result, with `gate
     exit:`, while the current fingerprint equals the start one; it never reports a vanish for a run
     that finished. A changed tree starts a new run. A new `--fresh` flag reruns on the same tree.
  2. The wait loop's deadline uses bash `$SECONDS`, so one call returns within its wait budget plus
     one poll interval, inside the Bash tool's 600-second cap (today's loop counts nominal seconds at
     `:333`).
  3. Any argument that starts with `--` and is not a known flag (`--receipt`, `--records`, `--fresh`)
     exits 2 with the usage line and starts nothing (today `:119` takes it as the gate string).
  4. The exit-75 text tells the caller to re-issue the same command with the Bash tool's
     `timeout: 600000`.
  5. With `RUN_GATE_IF_BUSY=defer`, a heavy-lane call that would start a run while the machine
     lock is held exits 76 with one line saying the leg is left to the push's CI, and starts
     nothing. A call that reattaches to its own in-flight run (its `pidfile` exists, `:240`) never
     defers. `--fresh` with a run in flight reattaches; it discards only a finished result. The light
     lane ignores the variable. The script cannot know a repo's full-suite home or a task's risk
     class, so the header says the caller must not set it where the full-suite home is local or on an
     `auth-data` task (`pass-core` and the adapters repeat that).
  6. The header comment matches the new behavior (it no longer says a result "is printed once and
     then cleared"), and the lock-wait NOTE no longer tells the reader to report to a conductor.
- **Files.** `bin/.local/bin/cairn-run-gate`, `tests/cairn-run-gate.test.sh`.
- **Risk.** `runner`.
- **Audit inputs.** AW-17, AW-20.
- **Acceptance.** `bash tests/cairn-run-gate.test.sh` exits 0 and its output names a passing case
  for each of: two concurrent waiters both print `gate exit:`; a repeat call on an unchanged tree
  reprints without a new run (the run records gain no `exit` line); a changed tree starts a new run;
  `--fresh` reruns; a call with a slow poll returns inside its deadline (a PATH-shimmed `sleep` that
  sleeps twice its argument, under a small `CAIRN_GATE_WAIT`; the wait loop calls `sleep` by name,
  `:332`); `--bogus` exits 2 and starts nothing; the exit-75 text contains `timeout: 600000`;
  `RUN_GATE_IF_BUSY=defer` with the heavy lock held by another run exits 76 and starts nothing; a
  `defer` re-issue while its own heavy run holds the lock reattaches and never exits 76; every
  pre-existing vanish case still passes. `grep -c 'printed once' bin/.local/bin/cairn-run-gate`
  prints 0. The dotfiles gate is green.
- **Test.** The cases above, added to `tests/cairn-run-gate.test.sh` beside its vanish cases (it
  already stages a temporary `TMPDIR` and short poll intervals).
- **Clock.** 65.

### S1-T4. Clock-stop hook and settings

- **Outcome.** The spec's Execution item 6 and its table's settings row.
  - A new script `bin/.local/bin/claude-clock-stop`: a PostToolUse hook that reads the hook input
    JSON from stdin, takes `cwd` (M6), and resolves `git -C "$cwd" rev-parse --absolute-git-dir`. If
    the file `pass-task-clock` exists in that git dir, it holds three lines, `task=<id>`,
    `start=<epoch seconds>`, `estimate=<minutes>`. When now minus start exceeds twice the estimate,
    the hook prints one JSON object (M6) whose `additionalContext` reads, in substance: "Clock stop:
    task <id> has run <m> minutes against a <e>-minute estimate. Write STATUS, run `notify-send -u
    normal`, and wait for Geoff (ruling 13)." In every other case (no file, under the threshold, a
    malformed file, a non-git cwd, a missing tool) it prints nothing and exits 0. It never exits
    non-zero. The file lives in the git dir, outside the work tree, so the gate fingerprint holds
    (spec Execution item 6).
  - `claude/.claude/settings.json` gains `"worktree": {"baseRef": "head"}` (M4) and a PostToolUse
    entry with `"matcher": "*"` running `claude-clock-stop` with a 5-second timeout, beside the
    existing `Write|Edit` entry.
- **Files.** `bin/.local/bin/claude-clock-stop` (new, executable), `tests/claude-clock-stop.test.sh`
  (new), `scripts/check.sh` (one `run` line for the new test), `claude/.claude/settings.json`.
- **Risk.** `runner`.
- **Acceptance.** `bash tests/claude-clock-stop.test.sh` exits 0, with a passing case for each of: no
  file, silent; under twice the estimate, silent; over twice, exactly one JSON object whose
  `.hookSpecificOutput.hookEventName` is `PostToolUse` and whose `additionalContext` names the task;
  a malformed file, silent; a non-git cwd, silent; a cwd in the main checkout while the file sits in
  a linked worktree's git dir, silent; each run under one second. `jq -e '.worktree.baseRef ==
  "head"' claude/.claude/settings.json` and `jq -e '[.hooks.PostToolUse[] | select(.matcher == "*") |
  .hooks[].command] | index("claude-clock-stop")' claude/.claude/settings.json` both exit 0. The
  dotfiles gate is green.
- **Test.** The new test file, which feeds the script JSON on stdin against temporary repos and
  linked worktrees.
- **Clock.** 45.

### S1-T5. Rewrite `pass-core`

- **Outcome.** `claude/.claude/skills/pass-core/SKILL.md` (312 lines today) holds the lean process in
  about 120 lines, sections in this order: "Lifecycle" (the spec's six steps, risk classes as a
  floor, the `live-account` flag, the one-sentence-diff skip, the plan's task fields with pairs
  marked, folding a single-deliverable task into a neighbor); "Models" (ME-1, ME-2, ME-8, ME-10's
  `low` and `max`); "Execute" (one session, which the planning session starts from the repo's main
  checkout as `claude --bg --model sonnet --effort medium --name <name> "$(cat <prompt file>)"`, so
  Geoff pastes nothing (ruling R-D, M2); its first act is `EnterWorktree`, and its first act in the
  new worktree is the adapter's setup command; it commits without asking and pushes the branch it
  created, and its PR comes from that branch; the repo's `.gitignore` carries `.claude/worktrees/`,
  added by the plan's first task where missing; its name and id recorded in STATUS; the launch prompt
  names its `glw907/<repo>` push target, M1; the API-drop wake-up and the lid-switch hold; it writes
  code and tests and commits); "Pairs" (spec Execution item 2, PG-11's port rule); "Gates" (spec
  Execution items 3, 4, and 5; the CI watch as a background Bash task; PG-5, PG-10, PG-13's pointer;
  `RUN_GATE_IF_BUSY=defer` limits); "Clock stop" (the task-clock file's path and three lines,
  written at each task start from a `cd` into the task's worktree, removed at the close; ruling 13's
  response; a resume after a stop rewrites `start=`, or `estimate=` to the figure Geoff names; the
  stop cannot fire while the session waits on a pair, since isolated pair worktrees hold no clock
  file);
  "Close"
  (spec Lifecycle step 6, ME-4); "Score" (the five rows and their sources, attended events, escapes,
  ME-12); "Ledgers" (STATUS present tense and 60 lines or fewer; ROADMAP tiers; git and PR bodies are
  history; `HISTORY.md` and post-mortems stop growing; a lesson lands where it executes; ruling 8);
  "Scope" (ME-15's home); "Launch prompt" (the shape a STATUS next action takes: goal, scope, the
  plan path, the checkout, the exact `claude` line; the prompt lives in a committed file, launched
  as `"$(cat <file>)"`, never inline in double quotes). Superpowers skills yield: plans stay
  outcome-only and skip `writing-plans`' code steps and its execution-method question; test-first
  applies to `auth-data` tasks (the 2026-09-27 ruling's `auth-data` half; its `engine-logic` class
  no longer exists).
- **Files.** `claude/.claude/skills/pass-core/SKILL.md`.
- **Risk.** `runner`.
- **Audit inputs.** PS-13, PS-14, PS-16, PS-23, PS-24; A-rest close wiring (superseded).
- **Acceptance.** `wc -l < claude/.claude/skills/pass-core/SKILL.md` prints 150 or less; `grep -c
  -E '^## (Lifecycle|Models|Execute|Pairs|Gates|Clock stop|Close|Score|Ledgers|Scope|Launch prompt)$'`
  on the file prints 11; `grep -c -i -E 'pass-execute|token ceiling|checkpoint interval|thin
  conductor|segment boundar'` prints 0 unless the line carries `retired-ok`; the description in the
  frontmatter names the lean lifecycle and no retired mechanism; this git-ownership grep prints
  nothing over the file and every prompt file this plan names (M2: such wording would leave git to
  Geoff):

  ```bash
  grep -n -i -E '(user|Geoff|you) (handles?|makes?|does|runs?) (the |all |every )?(git|commit|push)|(commit|push)(es|s)? (only )?(when|if) (the user|Geoff|asked)|only when (the user|Geoff) asks|leave (git|commit|push)[a-z]* to|never (commit|push) (unless|without)' \
    claude/.claude/skills/pass-core/SKILL.md docs/superpowers/plans/2026-10-10-lean-pass-cutover-prompts/*.txt
  ```

  The dotfiles gate is green.
- **Test.** The gate's reference and retired-phrase checks.
- **Clock.** 60.

### S1-T6. Rewrite the adapters

- **Outcome.** Three thin adapters, each with the eight fields the spec's table names, as bold labels
  in this order: **Gate**, **Fast lane**, **Full-suite home**, **Worktree setup**, **CI watch**,
  **Risk-class path map**, **Checklist globs**, **Close checklist**. Each loads `pass-core` first.
  - `cairn-pass`: gate `cairn-run-gate`; fast lane `node scripts/checks/gate-tier.mjs --fast --range
    <base>..HEAD`, whose printed lines are run in order, each through `cairn-run-gate` with a leading
    `CAIRN_GATE_LANE=<lane>` lifted onto the call (`CAIRN_GATE_LANE=light cairn-run-gate '<rest>'`),
    since the tool reads the lane from its own environment (`cairn-run-gate:247`) (the flag lands
    in rollout step 2, S2-T3; no cairn pass runs before step 2 merges); full-suite home CI on the
    draft PR; worktree `.claude/worktrees/<branch>` with setup `npm ci && npm ci --prefix examples/showcase` (M14); CI
    watch `ci-green <sha> --pr <n> --wait`, re-issued on 75, as a background Bash task (M7); local
    `TIER_GATES.full` and `npm run check:close` only on `ci-green` exit 3 (PG-16); no task waits for
    CI before the next one (the 2026-10-09 protected-path wait has no catch record, and a red still
    stops the line, spec Execution item 4); `auth-data` globs `src/lib/{auth,auth-channel,auth-crypto,
    auth-store,github}/**`, `src/lib/sveltekit/{csrf*,auth-*,commit-log}.ts`,
    `src/lib/admin/{csrf-context.ts,CsrfField.svelte}`, `migrations*/**`,
    `examples/showcase/migrations*/**`, `templates/*/migrations*/**`, `**/hooks.server.ts`,
    `**/preview/\[token\]/**` (escaped: in a pathspec `[token]` is a character class),
    `**/members/login/**`, `**/admin/signups/**`, `tool/internal/secrets/**`,
    `packages/create-cairn-site/src/{github,cloudflare}/**`, `wrangler.*`; the four domain reviewers'
    globs plus `go-conventions` for `tool/**`; the close checklist keeps the live admin smoke on `auth-data`,
    the documentation dimension, the CHANGELOG and facts rules, the release hand-off to
    `cairn-release`, and drops HISTORY entries, post-mortems, and the simplifier. PG-9: say whether
    cairn's gate scopes gitleaks to the change set and, if so, add the branch-history scan.
  - `site-pass`: one table with a row per site (ecxc-ski, 907-life, aksailingclub-org,
    xcathletes-org, cairn-pub): gate, fast lane (`npm run check` plus the unit test files the diff
    touches, PG-4), full-suite home (aksailingclub-org: CI on PR, watched with `gh pr checks <n>
    --watch --fail-fast`; the other four: one local `npm run check && npm test && npm run build` at
    the close, since they have no PR test CI, ruling 11), worktree the launch's `.claude/worktrees/<name>`
    (`pass-core` "Execute") with setup `npm ci`, and `auth-data` globs: every site `src/hooks.server.ts`,
    `src/routes/admin/**`, `wrangler.*`; aksailingclub-org adds `src/member-auth/**`,
    `src/member-signup/**`, `src/admin-club/**`, `migrations/**`, `data/membershipworks/**` (member
    PII); xcathletes-org adds `src/lib/server/{auth,db}/**`, `src/routes/team/{login,tokens}/**`,
    `migrations*/**`; cairn-pub adds `migrations/**`. Plan and spec paths are read from each site's
    `CLAUDE.md` or STATUS (PS-09); the cairn-docs editing rules that the current skill carries stay,
    shortened.
    `site-pass/plan-template.md` is deleted: the plan's task fields live in `pass-core` alone.
  - A new project skill for the workstation repo, `.claude/skills/dotfiles-pass/SKILL.md` at the
    repo root (tracked; not a stow package): gate and fast lane `CAIRN_GATE_LANE=light cairn-run-gate
    'bash scripts/check.sh'` (M13); full-suite home that same command once on the close head, since
    dotfiles has no PR test CI (ruling 11); worktree the launch's `.claude/worktrees/<name>`, no
    setup; no CI watch; risk map `runner` for `claude/.claude/{skills,agents,workflows}/**`,
    `claude/.claude/settings.json`, `bin/.local/bin/{cairn-run-gate,ci-green,ci-green-lib.mjs,claude-clock-stop}`,
    `scripts/**`, `tests/**`; `auth-data` for `secrets/**`, `scripts/secrets/**`, `bash/.bashrc`
    (it sources the secrets), and `bin/.local/bin/{claude-block-op,claude-secret-guard,
    claude-tierguard,claude-askpass,claude-sudo-setup,claude-sudo-clear,secret-receive,
    fastmail-password,fastmail-dav-password}`; `ordinary` otherwise;
    checklist globs `*.py` to `python-conventions`, `*.go` to `go-conventions`, `*.{js,mjs,ts}` to
    `ts-conventions`.
  - `.gitignore` gains `.claude/worktrees/`, so pair-subagent worktrees under the main checkout stay
    untracked (M4).
- **Files.** `claude/.claude/skills/cairn-pass/SKILL.md`, `claude/.claude/skills/site-pass/SKILL.md`,
  `claude/.claude/skills/site-pass/plan-template.md` (deleted), `.claude/skills/dotfiles-pass/SKILL.md`
  (new), `.gitignore`.
- **Risk.** `runner`.
- **Audit inputs.** PS-02, PS-09, PS-17, PS-22, PS-25, DC-03, the code-simplifier row.
- **Acceptance.** For each of the three adapter files, `grep -c -E '^\*\*(Gate|Fast lane|Full-suite
  home|Worktree setup|CI watch|Risk-class path map|Checklist globs|Close checklist)\*\*'` prints 8;
  `site-pass`'s table has five site rows; `test ! -e claude/.claude/skills/site-pass/plan-template.md`;
  `grep -qx '.claude/worktrees/' .gitignore`; each adapter is under 120 lines (`wc -l`); every
  `auth-data` glob, braces expanded, matches at least one tracked file in its repo (`git -C <repo>
  ls-files -- '<glob>'` is non-empty; all matched on 2026-10-10); `grep -c 'wait for CI green' claude/.claude/skills/cairn-pass/SKILL.md`
  prints 0. The dotfiles gate is green.
- **Test.** The gate's reference and retired-phrase checks, and the glob check above.
- **Clock.** 70.

### S1-T7. Rewrite `spec-plan-review`

- **Outcome.** `claude/.claude/skills/spec-plan-review/SKILL.md` (169 lines) holds the spec's
  Lifecycle steps 3 and 4: three parallel Opus spec lenses named "contract and criteria", "mechanics
  and feasibility", and "data integrity and failure risk"; a fold that probes every new mechanism it
  introduces and may refuse a finding with a reason; one verification read whose findings the fold
  agent applies, with another read only on a blocker; a design-changing finding goes to Geoff as one
  batched question; plan review runs the mechanics lens plus a verification read by default, and all
  three lenses for an `auth-data` or `runner` pass or one with the `live-account` flag. The
  consistency and prose lenses are gone (Vale and `tellgrader` cover prose). Reviewer effort is
  `medium` (spec Lifecycle preamble).
- **Files.** `claude/.claude/skills/spec-plan-review/SKILL.md`.
- **Risk.** `runner`.
- **Audit inputs.** PS-12, PS-15.
- **Acceptance.** `wc -l` prints 120 or less; the three lens names each appear (`grep -c` per name
  prints at least 1); `grep -c -i -E 'consistency lens|prose lens'` prints 0 unless the line carries
  `retired-ok`; ``grep -c '`high`'`` prints 0 (the skill names no `high` effort; design and plan
  authorship effort lives in `pass-core`). The dotfiles gate is green.
- **Test.** The gate's checks.
- **Clock.** 30.

### S1-T8. Agents

- **Outcome.**
  - `diff-reviewer.md` (91 lines) is rewritten to carry the `auth-data` bar itself (coverage gaps
    block, cosmetic citations never do), to take either a task scope (one commit or range plus its
    task's acceptance) or a whole-branch scope (the branch diff plus the checklists the adapter's
    globs name), and to return accept, fix, or escalate with `file:line` findings. It drops the
    conductor, the implementer's report input, and the severity routing field (AW-05). Frontmatter
    stays `claude-opus-5-5` at `medium`.
  - `cairn-implementer.md` (173) and `site-implementer.md` (155) become pair-subagent definitions:
    the subagent runs in its own worktree, runs the adapter's setup command first, writes code and
    tests, runs the adapter's fast lane through `cairn-run-gate`, commits, and never pushes. Dropped:
    the chain report shape, the gate protocol paragraphs (the tool's output carries it, AW-20), the
    dated compatibility note (AW-23), and the conductor. Kept: the repo conventions, PG-6's two
    comment rules, the escalation path, the DaisyUI pointer reduced to the official skill, and chain
    W's lines listed under Audit inputs. AW-18: the bare "the spec's" citation at
    `site-implementer.md:104` names its path or is inlined. Effort `medium` (ME-1).
  - `go-architecture-reader.md`: description and body say it runs on request, never at a pass's
    merge and never by a conductor.
- **Files.** `claude/.claude/agents/diff-reviewer.md`, `claude/.claude/agents/cairn-implementer.md`,
  `claude/.claude/agents/site-implementer.md`, `claude/.claude/agents/go-architecture-reader.md`.
- **Risk.** `runner`.
- **Audit inputs.** AW-04, AW-05, AW-18, AW-19, AW-20, AW-21, AW-23, the section 4 rows named above.
- **Acceptance.** `grep -c -i -E 'conductor|Report format|exit 75'` over the four files prints 0 per
  file; `grep -c -E 'whole-branch'` on `diff-reviewer.md` prints at least 1, and `grep -q 'auth-data'`
  and `grep -qi 'coverage gap'` both succeed on it; `grep -q "track's drafting
  brief"` succeeds on both implementers and `grep -q 'check:docs-gate -- --page'` on
  `site-implementer.md`; `grep -E '^effort:'` prints `medium` for both implementers. The dotfiles gate
  is green.
- **Test.** The gate's checks.
- **Clock.** 45.

### S1-T9. Rewrite the global `CLAUDE.md`

- **Outcome.** `claude/.claude/CLAUDE.md` (301 lines) at 200 or fewer. Leave for `pass-core`:
  "Conducting a pass" (157-202), "Gate economy on a pass" (203-208), "Pass sizing" (254-261), the
  model-seat paragraph, "Project ledgers" (239-253), and the scoring sentences of "Process
  proportionality"; one line names `pass-core` as the home of the pass process. Keep, trimmed where
  a sentence changes nothing the model would do: everything else. Specific changes: "Git Conventions"
  loses the simplifier bullet (DC-01); "API-First Policy" points at
  `~/.claude/docs/cloudflare-estate-inventory.md` in place of a per-project `api-access.md` (DC-08);
  "cairn-family work" keeps a one-line visual-fidelity trigger, and its engine-mechanics and
  friction-harvest pass mechanics move to `cairn-pass` and `site-pass` (DC-19; edit those two
  adapters in this task if S1-T6 did not carry them); "Claude Code Agent Usage" keeps "no human-scale
  time estimates in conversation" and adds that plan tasks carry clock estimates in minutes per
  `pass-core`; "A rule lives where it executes" routes state to STATUS or ROADMAP (no HISTORY);
  "Compact instructions" preserves the plan path, the task in flight and its clock file, the last CI
  and review verdicts, and the STATUS launch prompt (no token ceiling); "Multi-agent workflows" keeps
  the suggest-never-launch rule and points at the guards doc for the wake-up (DC-04);
  "Initiative-scoped sessions" drops the post-mortem; "One executor per worktree" says sessions in
  place of conductors; "Writing voice" keeps chain W's content (DC-27, AW-24).
- **Files.** `claude/.claude/CLAUDE.md`, and `claude/.claude/skills/{cairn-pass,site-pass}/SKILL.md`
  only for DC-19's moved lines.
- **Risk.** `ordinary`.
- **Audit inputs.** DC-01, DC-03, DC-04, DC-08, DC-19, DC-21, DC-27, DC-29, DC-30, AW-24.
- **Acceptance.** `wc -l < claude/.claude/CLAUDE.md` prints 200 or less; `grep -c -E '^## (Conducting a
  pass|Gate economy|Pass sizing|Project ledgers)'` prints 0; `grep -c 'pass-core'` prints at least 1;
  `grep -c 'developer brief'` prints at least 1; `grep -c 'api-access.md'` prints 0; S1-T5's
  git-ownership grep prints nothing over `claude/.claude/CLAUDE.md`. The dotfiles gate is green.
- **Test.** The gate's checks; the `claude-context-budget` PostToolUse hook stays quiet on the edit.
- **Clock.** 45.

### S1-T10. Fold the three process docs

- **Outcome.** Every row of the Rules inventory is at its named home. `model-economy.md` and
  `pass-gate-economy.md` are deleted. `unattended-work-guards.md` keeps UG-1 to UG-9 (retargeted as
  their rows say) and gains "Shared gate lanes" (PG-13, PG-14's lane rule, PG-17).
  `claude-tooling.md` gains "Model defaults" (ME-9, ME-10's `/effort` fact) and the by-name workflow
  procedure (PG-12) in its "Workflows" row or a short section, plus one line that
  `worktree.baseRef: "head"` applies in every repo, so subagent and `--worktree` branches start from
  the local `HEAD` (M4), and its lines 50-55 seat paragraph
  loses the deleted runners. `fable-post-cutoff-system.md` gains "Pricing and allowance" (ME-13) and
  its note at line 3-5 no longer points at `model-economy.md` (DC-06).
- **Files.** `claude/.claude/docs/model-economy.md` (deleted), `claude/.claude/docs/pass-gate-economy.md`
  (deleted), `claude/.claude/docs/unattended-work-guards.md`, `claude/.claude/docs/claude-tooling.md`,
  `claude/.claude/docs/fable-post-cutoff-system.md`, and `pass-core` or an adapter only where a row's
  home was not yet written by S1-T5 or S1-T6.
- **Risk.** `ordinary`.
- **Audit inputs.** DC-04, DC-06, PS-14, A-rest `seats.json` (superseded), the runaway-guard script
  question (superseded).
- **Acceptance.** `test ! -e claude/.claude/docs/model-economy.md && test ! -e
  claude/.claude/docs/pass-gate-economy.md`; `grep -c '^## Shared gate lanes'
  claude/.claude/docs/unattended-work-guards.md` prints 1; `grep -c 'CLAUDE_CODE_SUBAGENT_MODEL'
  claude/.claude/docs/claude-tooling.md` prints at least 1; `grep -c -i 'Pricing and allowance'
  claude/.claude/docs/fable-post-cutoff-system.md` prints 1; the PR body's inventory section lists each
  row id with the file and section it landed in. The dotfiles gate is green.
- **Test.** The gate's dead-reference check (it fails on any surviving `~/.claude/docs/` path span to
  a deleted file).
- **Clock.** 45.

### S1-T11. Delete the runners

- **Outcome.** `claude/.claude/workflows/pass-execute.js` (1,265 lines),
  `claude/.claude/workflows/pass-execute-chains.js` (931), and `tests/pass-execute-runners.test.mjs`
  are deleted; `scripts/check.sh:44` is removed; `tests/cairn-run-gate.test.sh` lines 342-357 no
  longer name the deleted runner files. Any path span the deletion leaves dangling is fixed in the
  same commit.
- **Files.** The three deleted files, `scripts/check.sh`, `tests/cairn-run-gate.test.sh`, and any file
  the gate names as dangling.
- **Risk.** `runner`.
- **Audit inputs.** AW-01 to AW-06, AW-11, AW-12, AW-13; DC-04's runner-launch NOTE half.
- **Acceptance.** `test ! -e` for each deleted file; `grep -c pass-execute scripts/check.sh
  tests/cairn-run-gate.test.sh` prints 0 per file. The dotfiles gate is green.
- **Test.** The gate.
- **Clock.** 15.

### S1-T12. Sweep and retire phrases

- **Outcome.** No skill, agent, workflow, doc, test, or script in the repo names a deleted file or
  teaches a retired mechanism (the spec's Retired list: the conductor, the simplifier as a standing
  step, the per-task local full gate, HISTORY entries, post-mortems, the close fold and its review,
  token ceilings, checkpoint STATUS writes, pass segmenting; plus the six pass classes, the runners,
  and the two deleted docs). Known homes at planning time: `skills/engine-consult/SKILL.md:109,146`,
  `agents/engine-triage.md:93`, `docs/fable-post-cutoff-system.md:21,49,60`,
  `docs/claude-md-archive.md:52`, `docs/claude-tooling.md:50-55,116-118` (seat paragraph and the
  review line's "prose review" and "Conducting a pass"), `workflows/docs-page-chain.js`
  (comment and prompt wording only, no seat change, so step 4 inherits clean text),
  `skills/cairn-release/SKILL.md:79-100,165` (its HISTORY yield record moves to the PR body, ruling 8),
  `skills/log-project/SKILL.md` (a shipped item leaves ROADMAP; PS-11's HISTORY close is superseded),
  `bin/.local/bin/cairn-run-gate`, and `ROADMAP.md:17,47,52`. `skills/go-ship/SKILL.md:28-35` keeps its
  simplifier step: the skill is user-invoked (`disable-model-invocation: true`), which is the
  on-request use the spec keeps. Each
  superseded phrase joins `claude/.claude/tooling/retired-phrases.txt` with a comment naming the
  spec, at least: `pass-execute`, `model-economy.md`, `pass-gate-economy.md`, `token ceiling`,
  `checkpoint interval`, `thin conductor`, `code-simplifier runs once per pass`, `Pass class:`, and
  `go-architecture-reader per touched`. A line that must name a retired phrase (a retirement note)
  carries `retired-ok`. Dated records (`docs/record/`, dated paths, `docs/HISTORY.md`, the spec and
  plans) are history and stay as written.
- **Files.** The files above and any other hit the grep below finds;
  `claude/.claude/tooling/retired-phrases.txt`.
- **Risk.** `runner`.
- **Audit inputs.** PS-11.
- **Acceptance.** This prints nothing, and the dotfiles gate is green (the gate's retired-phrase check
  proves zero hits for every listed phrase, M11):

  ```bash
  grep -rIn -i -E 'pass-execute|model-economy|pass-gate-economy|token ceiling|checkpoint interval|thin conductor|segment boundar|reducedGate|batchedNotes|implementer-review-gate|per-task chain|post-mortem to the plan|HISTORY entry' \
    claude/.claude bin/.local/bin scripts tests ROADMAP.md README.md .claude/skills \
    --exclude-dir=record --exclude-dir=synced --exclude-dir=research --exclude=retired-phrases.txt \
    | grep -v retired-ok
  grep -rIn -i -w 'conductor' claude/.claude bin/.local/bin scripts tests ROADMAP.md README.md .claude/skills \
    --exclude-dir=record --exclude-dir=synced --exclude-dir=research --exclude-dir=tellgrader \
    --exclude=retired-phrases.txt | grep -v retired-ok
  grep -rIl -i 'code-simplifier' claude/.claude/skills claude/.claude/agents claude/.claude/workflows \
    claude/.claude/CLAUDE.md .claude/skills --exclude-dir=synced | grep -v -x 'claude/.claude/skills/go-ship/SKILL.md'
  grep -n -i 'HISTORY' claude/.claude/skills/cairn-release/SKILL.md | grep -v retired-ok
  ```

  At planning time the first grep hit 17 files and the second 20, every one a file this step
  rewrites, deletes, or names above (`tellgrader` is excluded because its Go test fixtures use the
  word as sample prose). The new `.claude/skills` tree sits outside the gate's own scan
  (`scripts/check-claude-refs.py` reads only `claude/.claude`), so these greps are its only
  retired-phrase check; that gap is accepted.
- **Test.** The gate's retired-phrase and dead-reference checks.
- **Clock.** 60.

### S1-T13. Close

- **Outcome.** The spec's Lifecycle step 6 for this branch:
  1. Full-suite home: `CAIRN_GATE_LANE=light cairn-run-gate 'bash scripts/check.sh'` green on the head.
  2. One whole-branch Opus review. The rewritten `diff-reviewer` is not live until the merge (M10), so
     dispatch the Agent tool with `subagent_type: "general-purpose"` and `model: "opus"` (M5), whose
     prompt tells it to read and act as this worktree's `claude/.claude/agents/diff-reviewer.md` at
     whole-branch scope over `git diff main...lean-cutover`, against the spec and this plan's
     acceptance checks, loading the checklists `dotfiles-pass`'s globs name for the changed files. It
     re-derives each task's risk class from the adapter's path map.
  3. One batched fix chain over its findings, then the gate again. A second review only on a blocker.
  4. `docs/STATUS.md` on the branch: present tense, 60 lines or fewer; the current state names the
     cutover's step 1 as PR-ready; the next action is Geoff's merge block (this plan, "Merge block");
     S1-T1's table moves to the PR body; the infra-sweep block stays; the open item about
     `cairn-run-gate` flags is removed (fixed in S1-T3). `docs/HISTORY.md` gains one top line saying
     it is frozen as of 2026-10-10 (ruling 8). `ROADMAP.md` gets no new entry here (S1-T15 files
     ruling 11 after the merge).
  5. Push `lean-cutover`, then `gh pr create -R glw907/workstation --base main --head lean-cutover
     --body-file <file>` (M8) with the Conventions' PR body, including S1-T1's table, the inventory
     placements, and a `Head: <sha>` line naming the pushed head. Not a draft: dotfiles has no CI to
     shadow.
  6. `notify-send -u normal "lean cutover: step 1 PR ready"` and end.
- **Files.** `docs/STATUS.md`, `docs/HISTORY.md` (one line), and the fix chain's files.
- **Risk.** `runner` (the pass's highest).
- **Acceptance.** The gate is green on the pushed head (`gate exit: 0` from `cairn-run-gate`);
  `gh pr view lean-cutover --json state,isDraft` shows `OPEN` and `false`; the PR body has the review
  verdict, the score section, and the `Head:` line; `wc -l < docs/STATUS.md` prints 60 or less.
- **Test.** The gate.
- **Clock.** 75.

### Merge block (Geoff, after reading the PR)

Geoff's merge is his touchpoint (ruling 4, spec Lifecycle step 6). He runs these in a terminal, with
no Claude session open anywhere, since a pull into the main checkout reaches every running session's
settings and hooks at once (M16):

```bash
[ "$(claude agents --json)" = "[]" ] && ! pgrep -a -x claude &&
git -C ~/.dotfiles fetch origin &&
[ "$(git -C ~/.dotfiles status -sb)" = "## main...origin/main" ] &&
gh pr merge lean-cutover -R glw907/workstation --merge --match-head-commit <HEAD_SHA> &&
cd ~/.dotfiles && git pull --ff-only && stow -R bin && command -v claude-clock-stop &&
claude --model sonnet --effort medium --name lean-step1b "$(cat ~/.dotfiles/docs/superpowers/plans/2026-10-10-lean-pass-cutover-prompts/1b.txt)"
```

Geoff replaces `<HEAD_SHA>` with the PR body's `Head:` sha. Every line is chained with `&&`, so a
failed check (a live session, a dirty or diverged `main`) runs nothing after it, and the merged
settings never name a hook whose link is missing (M10). Session 1b starts after the pull, so it
loads the merged `CLAUDE.md`, skills, and settings (M16), and one session covers the tag, the
probes, the filing, and the launch of steps 2 and 4.

**Launch prompt (1b):** `2026-10-10-lean-pass-cutover-prompts/1b.txt`.

### S1-T14. Verify the merge and tag its parent

- **Outcome.** First take the merge sha, `M=$(gh pr view lean-cutover -R glw907/workstation --json
  mergeCommit -q .mergeCommit.oid)`; every check below, S1-T18, and the rollback name `M`, so a
  resumed 1b re-derives it after later commits move `HEAD`. The merge is one merge commit on the
  frozen `main`: `git merge-base M^1 M^2` equals `M^1` (the branch was cut from the merge parent, so
  `main` did not move) and `git rev-list --count --first-parent M^1..M` prints 1. Then, unless the tag
  already exists at `M^1` (a resume), `git tag pre-lean-process M^1 && git push origin
  pre-lean-process`, so the merge commit's parent carries the tag (spec Rollout step 1).
  `readlink -f ~/.local/bin/claude-clock-stop` resolves into `~/.dotfiles/bin/.local/bin/`;
  `claude-tooling-sync verify` and `CAIRN_GATE_LANE=light cairn-run-gate 'bash scripts/check.sh'`
  exit 0 in the main checkout.
- **Files.** None authored (the tag only).
- **Risk.** `runner`, `live-account`.
- **Acceptance.** The two merge checks above; `git rev-parse pre-lean-process` equals `git rev-parse
  M^1`; `git ls-remote origin refs/tags/pre-lean-process` prints that sha; the readlink, verify,
  and gate results above.
- **Rollback (Geoff's call, never a session's).** The smaller remedy for a clock-stop misfire is to
  delete the one `claude-clock-stop` PostToolUse entry from `claude/.claude/settings.json`. The full
  rollback is clean only before any step 2 to 4 PR merges, since those land the lean process in other
  repos and the revert leaves them. It restows before it pushes, and it keeps the live
  `docs/STATUS.md` and `ROADMAP.md` where S1-T15 and S1-T18 make the revert conflict (replayed in a
  scratch repo, fold verification V-M2):

  ```bash
  M=$(gh pr view lean-cutover -R glw907/workstation --json mergeCommit -q .mergeCommit.oid) &&
  { git -C ~/.dotfiles revert -m 1 --no-edit "$M" || {
      git -C ~/.dotfiles checkout --ours -- docs/STATUS.md ROADMAP.md &&
      git -C ~/.dotfiles add docs/STATUS.md ROADMAP.md &&
      GIT_EDITOR=true git -C ~/.dotfiles revert --continue; }; } &&
  cd ~/.dotfiles && stow -R bin && git push origin main
  ```

  `stow -R` prunes the link to the deleted `claude-clock-stop` (risk review, probed with GNU Stow
  2.4.1). Then clear the gate state the new `cairn-run-gate` persisted, keeping the lock files, since
  the old script reprints a stored status whenever a `pidfile` exists (`cairn-run-gate:240`): list
  `find /tmp/cairn-gate-$(id -u) -mindepth 1 -maxdepth 1 -type d` first, then rerun it with `-exec rm
  -rf {} +`. Restart every Claude session, since `CLAUDE.md` loads only at session start (M16).
  Re-landing the cutover later takes a revert of the revert.
- **Test.** The acceptance commands.
- **Clock.** 15.

### S1-T15. File ruling 11's item in dotfiles, unpushed

- **Outcome.** Dotfiles `ROADMAP.md` gains one Planned item: add PR test CI that runs
  `bash scripts/check.sh` on `pull_request`; until it lands, the full-suite home is the local close
  gate (ruling 11). It is committed alone on `main`, after the One-executor rule's `diff --quiet`
  check on `ROADMAP.md`, and stays unpushed until S1-T18, so S1-T16 has a local `HEAD` ahead of
  `origin/main`. dubplate filed in S1-T2; ecxc-ski, 907-life, xcathletes-org, and cairn-pub file in
  their step 3 PRs (ruling R-B, see Spec gaps).
- **Files.** `ROADMAP.md`.
- **Risk.** `ordinary`.
- **Acceptance.** `git show --stat HEAD` lists only `ROADMAP.md`; `git rev-list --count
  origin/main..main` prints 1.
- **Test.** None.
- **Clock.** 10.

### S1-T16. Live pair probe

- **Outcome.** The spec's Execution item 2 shown live with the merged settings. From `~/.dotfiles`,
  dispatch two Agent-tool subagents in one message, each with `isolation: "worktree"` and `model:
  "sonnet"` (M5). Each one writes every Bash call as `cd <its worktree> && ...` (M16), prints `git
  rev-parse HEAD` and `git merge-base HEAD <S1-T15 sha>`, runs `CAIRN_GATE_LANE=light cairn-run-gate
  'test -f .claude/skills/dotfiles-pass/SKILL.md && bash -n bin/.local/bin/cairn-run-gate'` until
  `gate exit:`, writes one file `probe/<agent letter>.txt`, commits it, never pushes, and returns its
  branch name and commit. The session then adds a scratch worktree `git worktree add
  .claude/worktrees/pair-probe -b pair-probe main` (M3), merges both branches there, runs the same
  light gate, and removes the scratch worktree, `pair-probe`, both agent branches, and both agent
  worktrees.
- **Files.** None kept.
- **Risk.** `runner`.
- **Acceptance.** Both subagents report a merge base equal to S1-T15's commit, which differs from
  `git rev-parse origin/main` (M4: `"head"`; without the setting they would branch from the default
  branch); both gates print `gate exit: 0`; the scratch merge is conflict-free; afterward `git worktree
  list` and `git branch --list 'pair-probe*' 'worktree-*'` match their state before the probe, and
  `git status --short` is empty.
- **Test.** The acceptance observations, quoted in STATUS by S1-T18.
- **Clock.** 25.

### S1-T17. Clock-stop probe

- **Outcome.** The spec's Execution item 6 shown live. `git worktree add --detach
  ~/.dotfiles/.claude/worktrees/clock-probe` (inside the session's working directory, so a `cd` there
  holds, M16; S1-T6's `.gitignore` line covers it); write `pass-task-clock` into `git -C
  ~/.dotfiles/.claude/worktrees/clock-probe rev-parse --absolute-git-dir` with `task=probe`, `start=`
  ten minutes ago, `estimate=1`; run one Bash call that `cd`s into the probe worktree (M6: `cwd`
  follows `cd`) and then one more Bash call there. Then remove the file, run one more call, `cd` back
  to `~/.dotfiles`, run one more call, and `git worktree remove` the probe.
- **Files.** None kept.
- **Risk.** `runner`.
- **Acceptance.** The stop line in the probe worktree is the expected result: quote it and continue.
  The session quotes the stop line it received after the call in the probe worktree,
  naming task `probe`; the calls after removal, and the call back in the main checkout, carry no stop
  line; `notify-send -u normal "lean cutover: clock-stop probe"` exits 0; `git worktree list` no
  longer shows the probe.
- **Test.** The acceptance observations.
- **Clock.** 15.

### S1-T17b. Self-isolating launch probe (ruling R-D)

- **Outcome.** The R-D launch shown live before `pass-core` relies on it. From `~/.dotfiles`, one
  Bash call runs `claude --bg --model sonnet --effort medium --name lean-rd-probe 'Create the file
  rd-probe.txt containing the word ok, commit it, and do not push.'` and records the printed id. The
  probe runs in trusted `~/.dotfiles`, since a fresh scratch repo is an untrusted nested repository
  and the launch would exit `Workspace not trusted` (M2); "do not push" keeps the throwaway branch
  off `glw907/workstation`. A background Bash task (M7) then polls for at most 15 minutes until `git
  worktree list` shows a new worktree under `~/.dotfiles/.claude/worktrees/` whose branch carries a
  commit adding `rd-probe.txt`. Nobody attaches, so that commit proves the session committed without
  asking. Then `claude stop <id>`, `claude rm <id>`, `git worktree remove --force` on the probe
  worktree, and `git branch -D` on its branch.
- **Files.** None kept.
- **Risk.** `runner`.
- **Acceptance.** `claude --bg` exits 0 and prints an id; `claude agents --json` listed
  `lean-rd-probe` while it ran; the commit appeared under `.claude/worktrees/` within the deadline;
  `git status --short` in `~/.dotfiles` stayed empty; `git ls-remote origin` shows no new branch;
  afterward `git worktree list` and `git branch --list` match their state before the probe. The
  session records the branch name `EnterWorktree` gave (M2) for S1-T18. A failure is a stop under
  the 1b prompt. The remedy is then Geoff's: `pass-core`'s launch falls back to the interactive
  paste, recorded in Spec gaps as a departure, and steps 2 and 4 launch as 3 does, with the same
  lines less `--bg`, pasted from each repo's main checkout.
- **Test.** The acceptance observations, quoted in STATUS by S1-T18.
- **Clock.** 20.

### S1-T18. STATUS, push, and the launches

- **Outcome.** Dotfiles `docs/STATUS.md` on `main`: step 1 merged (`M`, tag), the three probe
  results quoted, S1-T14's rollback, and the next action: steps 2 and 4 run as `lean-step2` and
  `lean-step4`, and Geoff pastes step 3 as `lean-step3` from its pre-launch block (ruling R-C); step 5
  (pass B) starts once steps 1 and 2 have merged (spec Rollout step 5: its branch merges `main` after
  step 2). Commit that file alone, then push `main`, which carries S1-T15's commit. Then run "Launch
  for 2" and "Launch for 4" below, one Bash call each. Notify Geoff and end.
- **Files.** `~/.dotfiles/docs/STATUS.md`.
- **Risk.** `ordinary`, `live-account`.
- **Acceptance.** `git show --stat HEAD` lists only `docs/STATUS.md`; `wc -l` prints 60 or less;
  `grep -c 'lean-step2\|lean-step3\|lean-step4'` prints at least 3; `git status -sb` shows no
  `ahead`; each launch block exits 0 with a printed id, and `claude agents --json` lists `lean-step2`
  and `lean-step4`.
- **Test.** None.
- **Clock.** 10.

## Steps 2 to 4: order and concurrency

Steps 2, 3, and 4 launch together at session 1b's S1-T18 (Geoff, ruling R-C): 1b starts steps 2
and 4 with `claude --bg` from each repo's main checkout (M2, ruling R-D), and Geoff pastes step 3,
which must sit in existing worktrees (Spec gaps). Each is a fresh session, so it loads the merged
`CLAUDE.md` and skills.

- **No shared file forces an order.** Step 2 writes only cairn-cms; step 3 writes only ecxc-ski,
  907-life, aksailingclub-org, xcathletes-org, cairn-pub, and dubplate; step 4 writes only dotfiles
  (`docs-page-chain.js`, its tests, and that branch's STATUS). Steps 2 and 3 never write dotfiles:
  a lesson whose executing home is a dotfiles file is listed in the PR body as owed (S2-T5, S3-T8).
  Step 4 never writes cairn-cms. cairn-pub's step 3 branch carries only its new `ROADMAP.md`
  (ruling R-B).
- **Shared resources.** The machine's heavy gate lock and memory, shared by every session's gates
  (`cairn-run-gate` serializes heavy gates; PG-13's heads-up rule applies); S2-T3's peak measurement,
  which queues on that lock; and Geoff's PR reads (step 3 opens six PRs).
- **Pre-launch assertion.** Each block below first checks its repos' default branches (ruling R-A),
  and every later line is chained behind that check with `&&`, so a failed check runs nothing after
  it (probed with shimmed `git`, `npm`, and `claude`). Steps 2 and 4 assert that the main checkout's
  `HEAD` equals `origin/main` after a fetch, since `"head"` branches from local `HEAD` (M4).

## Step 2: cairn-cms

The spec's Rollout step 2, plus the cairn half of the retired-machinery sweep and the HISTORY
harvest. Clock stop on (each task writes its task-clock file at start, per `pass-core`).

### Launch for 2 (1b runs it in S1-T18)

```bash
git -C ~/Projects/cairn-cms fetch origin &&
[ "$(git -C ~/Projects/cairn-cms rev-parse HEAD)" = "$(git -C ~/Projects/cairn-cms rev-parse origin/main)" ] &&
cd ~/Projects/cairn-cms &&
claude --bg --model sonnet --effort medium --name lean-step2 "$(cat ~/.dotfiles/docs/superpowers/plans/2026-10-10-lean-pass-cutover-prompts/2.txt)"
```

The session enters its worktree, then runs the setup there (M2, M14).

**Launch prompt (2):** `2026-10-10-lean-pass-cutover-prompts/2.txt`.

Gate strings: until S2-T3 lands, the per-task gate is the string `node scripts/checks/gate-tier.mjs
--range <base>..HEAD` prints (today's targeted tier, run through `cairn-run-gate`); from S2-T3 on, the
fast lane.

### S2-T1. cairn `CLAUDE.md` (pair with S2-T2)

- **Outcome.** `CLAUDE.md` (335 lines) at 200 or fewer. The charter, docs tracks, releases, admin
  design, and gotchas stay as short pointers (spec table); pass and gate content leaves (it lives in
  `cairn-pass`; a cairn-specific rule missing there is listed in the PR body as owed to dotfiles);
  `HISTORY.md` is described as a frozen record (ruling 8); no line names a retired mechanism.
- **Files.** `CLAUDE.md`.
- **Risk.** `ordinary`.
- **Audit inputs.** DC-03, PS-14, DC-18, DC-22, DC-24, PS-25, the owed trim.
- **Acceptance.** `wc -l < CLAUDE.md` prints 200 or less; the step 2 grep (S2-T5) prints nothing for
  `CLAUDE.md`; every relative link target exists: `grep -oE '\]\([^)#]+' CLAUDE.md | cut -c3- | while
  read -r p; do test -e "$p" || echo "MISSING $p"; done` prints nothing.
- **Test.** The gate's docs checks on the change.
- **Clock.** 60.

### S2-T2. Shard the CI e2e job (pair with S2-T1)

- **Outcome.** `.github/workflows/e2e.yml`'s `e2e` job runs as a Playwright shard matrix (M9) with a
  merge job that combines the blob reports into the HTML report and keeps the retries notice working.
  The shard count is the smallest whose projected per-shard time is at or under the median `test`
  job time over the last five `main` runs (`gh run list --workflow test.yml --branch main --limit 5`
  and the same for `e2e.yml`); the PR body records the numbers. The `update_snapshots` dispatch keeps
  working (run it unsharded, in one job). `norms` stays. The workflow file name stays, so
  `.github/ci-green.json` still expects it.
- **Files.** `.github/workflows/e2e.yml`, `examples/showcase/playwright.config.ts` (CI reporter),
  `scripts/ci/retries-notice.mjs` only if it must read merged output.
- **Risk.** `runner`. Its acceptance is CI on its own commit; the session goes on to S2-T3 while that
  CI runs, and a red stops the line.
- **Acceptance.** On the PR, the `e2e` workflow run for this commit shows one job per shard plus the
  merge job, all `success` (`gh run view <id> --json jobs`); `ci-green <sha> --pr <n> --wait` exits 0.
  The whole-branch review confirms the `update_snapshots` dispatch path still routes to one
  unsharded job (no `actionlint` is installed).
- **Test.** The CI run itself.
- **Clock.** 75.

### S2-T3. The fast lane, measured

- **Outcome.** `scripts/checks/gate-tier.mjs --fast --range <base>..HEAD` prints the spec's Execution
  item 3 legs as one or two lines, each a complete `cairn-run-gate` gate string: line 1 runs the
  non-browser legs (the type check, the unit tests related to the diff, the static checks the diff's
  buckets select, and the docs gate when docs changed) concurrently, failing if any leg fails; line 2,
  present only when the diff reaches component tests, runs the related component tests alone and is
  always heavy. It runs no whole node projects and no e2e (CI carries them, spec Execution item 4).
  Fail closed as today: an empty range or a git failure prints nothing and exits non-zero. Any
  unknown flag exits 2 with nothing on stdout (today `--fast` is silently ignored and the default
  targeted tier prints, exit 0; probed 2026-10-10). The default, `--pin`, and `--protected` modes are
  unchanged. The header no longer names `pass-execute.js` and documents `--fast` and its lane rule;
  `docs/internal/pass-gate-tiers.md` documents the fast lane.
  Line 1's lane is then measured: run it for a representative `src/lib` range three times, each as a
  background Bash task (M7, since the lock wait can pass the 600-second cap), as `flock
  "${TMPDIR:-/tmp}/cairn-gate-$(id -u)/machine.lock" systemd-run --user --wait -P -d -E PATH="$PATH"
  bash -c '<line 1>'` (M15; the heavy lock `cairn-run-gate:270` takes, so it queues behind other
  sessions' heavy gates and runs beside none), and take the largest `Memory peak`. If it fits the
  light lane's 3G cap (`cairn-run-gate:29-34`), line 1 gains the `CAIRN_GATE_LANE=light` prefix;
  otherwise it stays heavy. The PR body records the three peaks and that the light lane's 2G
  `MemoryHigh` throttles above 2G; the header and `pass-gate-tiers.md` record the measurement, date,
  and range.
- **Files.** `scripts/checks/gate-tier.mjs`, `scripts/checks/gate-table.json` only if a bucket needs a
  fast-lane field, `src/tests/unit/gate-tier.test.ts`, `docs/internal/pass-gate-tiers.md`.
- **Risk.** `runner`.
- **Acceptance.** `npx vitest run src/tests/unit/gate-tier.test.ts` exits 0 with new cases for a
  docs-only diff, a `src/lib` diff, a component diff, an empty range, an unknown flag (exit 2, empty
  stdout), `--fast` output that contains neither `npm run package` nor `check:close`, line 1 exiting
  non-zero when one of its legs fails, and line 1's prefix matching the measured lane; each line `node
  scripts/checks/gate-tier.mjs --fast --range origin/main..HEAD` prints, run through `cairn-run-gate`
  with its lane prefix lifted onto the call (S1-T6), prints `gate exit: 0`; `grep -c pass-execute scripts/checks/gate-tier.mjs` prints 0; the PR body
  lists three `Memory peak` values and the chosen lane; CI green on the commit.
- **Test.** The unit cases above.
- **Clock.** 135.

### S2-T5. Harvest HISTORY and sweep cairn's executing homes

- **Outcome.** Every bullet under a "What a later pass would be wrong to rediscover" heading in
  `docs/HISTORY.md` (51 headings, about 155 bullets) gets one disposition in the PR body's table:
  moved to an executing home in cairn-cms (a test or check, a script header,
  `docs/internal/durable-gotchas.md`, the internal doc that governs the area, or a `CLAUDE.md`
  pointer), owed to a dotfiles home (listed, not edited), or dropped as stale with a one-line reason.
  `docs/HISTORY.md` gains one top line saying it is frozen as of 2026-10-10 (ruling 8) and no other
  change. The grep below prints nothing over cairn's executing homes.
- **Files.** The homes the harvest writes, `docs/HISTORY.md` (one line), `ROADMAP.md`, `CLAUDE.md` only
  through pointers, `docs/internal/durable-gotchas.md`, `docs/internal/pass-gate-tiers.md`.
- **Risk.** `ordinary`.
- **Acceptance.** The PR body states the count and carries the harvest report per Conventions; `git diff origin/main --
  docs/HISTORY.md` adds only the frozen line; this prints nothing:

  ```bash
  grep -n -i -E 'pass-execute|conductor|code-simplifier|go-architecture-reader|token ceiling|checkpoint interval|segment boundar|Pass class|per-task chain|implementer-review-gate|model-economy|pass-gate-economy|wrong to rediscover|post-mortem to the plan|plan.s post-mortem' \
    CLAUDE.md ROADMAP.md docs/STATUS.md docs/internal/pass-gate-tiers.md docs/internal/durable-gotchas.md scripts/checks/gate-tier.mjs
  ```

  (At planning time: `CLAUDE.md` 3 hits, `ROADMAP.md` 10, `gate-tier.mjs` 4.)
- **Test.** The gate's docs checks on the change.
- **Clock.** 180.

### S2-T6. Close

- **Outcome.** The spec's Lifecycle step 6: CI green on the head (`ci-green <sha> --pr <n> --wait`,
  re-issued on 75); one whole-branch review by the live `diff-reviewer` (Agent tool, `model:
  "opus"`) at whole-branch scope with the checklists `cairn-pass`'s globs name; one batched fix chain;
  `docs/STATUS.md` present tense and 60 lines or fewer, with its "Next action (lean pass process)"
  block corrected (the adapters landed in step 1, not here) and pass B named as rollout step 5,
  starting once this PR merges (spec Rollout step 5: its branch merges `main` after step 2); remove
  the task-clock file; the PR body per Conventions; `gh pr ready`; notify Geoff; end.
- **Files.** `docs/STATUS.md` and the fix chain's files.
- **Risk.** `runner`.
- **Acceptance.** `ci-green <head> --pr <n> --wait` exits 0; `gh pr view --json isDraft` shows
  `false`; `wc -l < docs/STATUS.md` prints 60 or less; `test ! -e "$(git rev-parse
  --absolute-git-dir)/pass-task-clock"`.
- **Test.** CI.
- **Clock.** 60.

## Step 3: sites, cairn-pub, and dubplate

The spec's Rollout step 3, plus the ROADMAP filings for ecxc-ski, 907-life, xcathletes-org, and
cairn-pub (ruling R-B). One session, started in `~/Projects`, edits the six linked worktrees created
before launch. Every worktree sits under `~/Projects`, so a `cd` into one holds (M16).

- **Pairs.** Two Agent-tool subagents dispatched together, each confined to one repo's worktree,
  with no `isolation` parameter: the disjoint repos isolate them. Each writes every Bash call as
  `cd <its worktree> && ...`, since a subagent's cwd resets between calls (M16). They commit on their
  repo's `lean-cutover` branch and never push; the session then pushes.
- **Clock stop.** At each task start the session `cd`s into that task's worktree and writes the
  task-clock file in its `git rev-parse --git-dir`. A pair's subagents work in those worktrees, and
  hooks fire on a subagent's tool calls too (hooks page), so while a pair runs the session holds no
  clock file; when the pair returns it writes one, with the longer estimate and `start=` set to the
  dispatch time.
- **Gates.** A task runs its repo's fast lane only when its diff touches a file outside `*.md` and
  `.claude/**` (`svelte-check` reads neither; S3-T9 runs each full-suite home once). dubplate's scoped
  gate is `bash scripts/check.sh --scope-changed` with no `--base`: on a branch it measures from the
  merge base with `master` (`scripts/check.sh:300-302`), and a `--base` other than a full 40-hex id
  silently runs the full form (`:142-144`).

The step 3 grep list (the spec's "named grep list per repo"), run from each worktree over that repo's
executing homes (`CLAUDE.md`, `README.md`, `ROADMAP.md`, `docs/STATUS.md`, every file under `.claude/`
except `agent-memory/` and `worktrees/`, and the undated top-level `docs/*.md` other than `HISTORY.md`
and `status-archive.md`):

```bash
P='pass-execute|conductor|code-simplifier|simplifier-brief|go-architecture-reader|token ceiling|checkpoint interval|segment boundar|Pass class|per-task chain|implementer-review-gate|dubplate-implementer|model-economy|pass-gate-economy|wrong to rediscover|post-mortem to the plan|plan.s post-mortem'
files=$( { ls CLAUDE.md README.md ROADMAP.md docs/STATUS.md 2>/dev/null; find .claude -type f -not -path '*/agent-memory/*' -not -path '*/worktrees/*' -not -name '*.lock'; find docs -maxdepth 1 -type f -name '*.md' | grep -v -E '/[0-9]{4}-[0-9]{2}-[0-9]{2}|HISTORY|status-archive'; } | sort -u )
grep -I -n -i -E "$P" $files
```

Hits at planning time (2026-10-10): ecxc-ski `.claude/rules/development-workflow.md` 1,
`.claude/skills/ship/SKILL.md` 2; 907-life `.claude/rules/development-workflow.md` 1;
aksailingclub-org `docs/page-review-protocol.md` 1, `ROADMAP.md` 5; xcathletes-org 0; dubplate
`.claude/instructions/simplifier-brief.md` 1, `CLAUDE.md` 7, `.claude/agents/dubplate-implementer.md`
11, `docs/roster-walk.md` 1, `ROADMAP.md` 1.

### Pre-launch for 3

```bash
ok=1
for r in ecxc-ski 907-life aksailingclub-org xcathletes-org cairn-pub; do
  [ "$(git -C ~/Projects/$r rev-list --count origin/main..main)" = 0 ] || { echo "AHEAD: $r"; ok=0; }; done
[ "$(git -C ~/Projects/dubplate rev-list --count origin/master..master)" = 0 ] || { echo "AHEAD: dubplate"; ok=0; }
[ "$ok" = 1 ] && (
  for r in ecxc-ski 907-life aksailingclub-org xcathletes-org cairn-pub; do
    git -C ~/Projects/$r fetch origin &&
    git -C ~/Projects/$r worktree add ~/Projects/.worktrees/$r-lean-cutover -b lean-cutover origin/main &&
    (cd ~/Projects/.worktrees/$r-lean-cutover && npm ci) || exit 1
  done
  git -C ~/Projects/dubplate fetch origin &&
  git -C ~/Projects/dubplate worktree add ~/Projects/.worktrees/dubplate-lean-cutover -b lean-cutover origin/master
) && cd ~/Projects &&
claude --model sonnet --effort medium --name lean-step3 "$(cat ~/.dotfiles/docs/superpowers/plans/2026-10-10-lean-pass-cutover-prompts/3.txt)"
```

dubplate has no adapter until S3-T7, so its setup is discovered in S3-T1. Its step 3 changes are
instruction files and docs, which its own `CLAUDE.md` allows in a worktree (the beets venv matters
only to the oracle legs).

**Launch prompt (3):** `2026-10-10-lean-pass-cutover-prompts/3.txt`.

### S3-T1. Baseline dubplate, file cairn-pub's ROADMAP

- **Outcome.** dubplate's gate legs for a docs-only change are known: `bash scripts/check.sh
  --scope-changed --dry-run` in its worktree, and any setup that dry run says it needs is run and
  recorded for S3-T7. The step 3 grep's counts per repo are recorded for the PR bodies. cairn-pub's
  worktree gains `ROADMAP.md`, created through the `log-project` skill with the `Active`, `Planned`,
  and `Someday` tiers and one Planned item: add PR test CI that runs `npm run check && npm test &&
  npm run build` on `pull_request`; until it lands, the full-suite home is the local close gate
  (ruling 11).
- **Files.** cairn-pub `ROADMAP.md` (new), one commit on its `lean-cutover`.
- **Risk.** `ordinary`.
- **Acceptance.** dubplate's dry-run output and a count table for six repos in the session's notes;
  `git -C ~/Projects/.worktrees/cairn-pub-lean-cutover show --stat HEAD` lists only `ROADMAP.md`, which
  carries the three tiers and the item.
- **Test.** None.
- **Clock.** 20.

### S3-T2. ecxc-ski (pair P1 with S3-T3)

- **Outcome.** The step 3 grep prints nothing in ecxc-ski. The project `ship` skill and
  `.claude/rules/development-workflow.md` no longer teach the retired per-commit or per-task machinery
  (spec step 3); `ship` either points at `site-pass` or is deleted if it adds nothing over it.
  `docs/STATUS.md` (173 lines) is present tense and 60 lines or fewer, its pass history dropped since
  git holds it (DC-02 under ruling 8). The audit ids are folded or recorded. `ROADMAP.md` gains
  ruling 11's Planned item: add PR test CI that runs `npm run check && npm test && npm run build` on
  `pull_request`; until it lands, the full-suite home is the local close gate (ruling R-B).
- **Files.** `.claude/skills/ship/SKILL.md`, `.claude/rules/development-workflow.md`, `CLAUDE.md`,
  `docs/STATUS.md`, `ROADMAP.md`, and the stub DC-17 names if present.
- **Risk.** `runner` (a skill).
- **Audit inputs.** DC-02, DC-13, DC-17, DC-22, DC-23 (deferred: its dotfiles half is pass C's).
- **Acceptance.** The step 3 grep prints nothing; `wc -l < docs/STATUS.md` prints 60 or less;
  `grep -i 'PR test CI' ROADMAP.md` prints the item; the fast lane is green if the step's Gates rule
  calls for it.
- **Test.** The fast lane, per the step's Gates rule.
- **Clock.** 45.

### S3-T3. 907-life (pair P1 with S3-T2)

- **Outcome.** The step 3 grep prints nothing in 907-life. `.claude/rules/development-workflow.md`
  stops teaching retired machinery. `CLAUDE.md:5`'s over-budget `@`-imports are reduced (DC-02).
  `docs/HISTORY.md`'s one rediscover section is harvested as in S2-T5 (homes inside 907-life; dotfiles
  homes listed as owed) and the file gains the frozen line. The audit ids are folded or recorded.
  `ROADMAP.md` gains ruling 11's item, worded as in S3-T2 (ruling R-B).
- **Files.** `.claude/rules/development-workflow.md`, `CLAUDE.md`, `docs/STATUS.md`, `docs/HISTORY.md`
  (one line), `ROADMAP.md`, the harvest's homes.
- **Risk.** `ordinary`.
- **Audit inputs.** DC-02, DC-13, DC-14, DC-17, DC-22.
- **Acceptance.** The step 3 grep prints nothing; the PR body carries the harvest report per
  Conventions; `grep -i 'PR test CI' ROADMAP.md` prints the item; the fast lane is green if the step's
  Gates rule calls for it.
- **Test.** The fast lane, per the step's Gates rule.
- **Clock.** 40.

### S3-T4. aksailingclub-org (pair P2 with S3-T5)

- **Outcome.** The step 3 grep prints nothing. `CLAUDE.md` (262 lines) at 200 or fewer (spec step 3).
  `docs/page-review-protocol.md` and `ROADMAP.md` stop teaching retired machinery. `docs/HISTORY.md`'s
  six rediscover sections are harvested as in S2-T5, with the frozen line. The audit ids are folded or
  recorded.
- **Files.** `CLAUDE.md`, `docs/page-review-protocol.md`, `ROADMAP.md`, `docs/HISTORY.md` (one line),
  the harvest's homes.
- **Risk.** `ordinary`.
- **Audit inputs.** DC-09, DC-15, DC-22.
- **Acceptance.** `wc -l < CLAUDE.md` prints 200 or less; the step 3 grep prints nothing; the PR body
  carries the harvest report per Conventions; the fast lane is green if the step's Gates rule calls
  for it.
- **Test.** The fast lane, per the step's Gates rule.
- **Clock.** 70.

### S3-T5. dubplate sweep (pair P2 with S3-T4)

- **Outcome.** dubplate's conducting loop (`CLAUDE.md:123` onward), the merge-time
  `go-architecture-reader` dispatch (`:305`), and the simplifier rules (`:135`, `:308`) are gone;
  `.claude/agents/dubplate-implementer.md` and `.claude/instructions/simplifier-brief.md` are deleted
  (spec step 3 names both as retired machinery). The tracked
  `.claude/agent-memory/dubplate-implementer/` directory is left alone, including S1-T1's warm files.
  Live dubplate rules that are not pass machinery (the lane registry as its executor check, the
  planning-miss rules at `:138`, ranked findings at `:147`, the refused-features list) stay, moved to
  the adapter in S3-T7 where they are pass rules. `CLAUDE.md` (356 lines) at 200 or fewer.
  `ROADMAP.md` and `docs/roster-walk.md` stop naming retired machinery. `scripts/checks/gate-tier.mjs`,
  "The pass-execute shim" (its own line 2), is deleted with the runners it served, and `CLAUDE.md:251`
  stops naming it (the step 3 grep does not scan `scripts/`, so this is named here).
- **Files.** `CLAUDE.md`, `.claude/agents/dubplate-implementer.md` (deleted),
  `.claude/instructions/simplifier-brief.md` (deleted), `scripts/checks/gate-tier.mjs` (deleted),
  `ROADMAP.md`, `docs/roster-walk.md`.
- **Risk.** `runner` (an agent).
- **Audit inputs.** The owed `dubplate-implementer` gate-string note (superseded).
- **Acceptance.** `wc -l < CLAUDE.md` prints 200 or less; `test ! -e .claude/agents/dubplate-implementer.md
  && test ! -e .claude/instructions/simplifier-brief.md && test ! -e scripts/checks/gate-tier.mjs`;
  `git grep -n gate-tier -- CLAUDE.md` prints nothing; the step 3 grep prints nothing; `git status
  --short .claude/agent-memory` in the worktree is empty; dubplate's scoped gate is green.
- **Test.** `bash scripts/check.sh --scope-changed` through `cairn-run-gate`.
- **Clock.** 60.

### S3-T6. xcathletes-org (pair P3 with S3-T7)

- **Outcome.** `CLAUDE.md:95`'s per-task "full gate" wording follows `site-pass` (DC-03); `CLAUDE.md:61`
  describes `docs/HISTORY.md` as a frozen record; the one rediscover section is harvested as in S2-T5,
  with the frozen line. `ROADMAP.md` gains ruling 11's item, worded as in S3-T2 (ruling R-B).
- **Files.** `CLAUDE.md`, `docs/HISTORY.md` (one line), `ROADMAP.md`, the harvest's homes.
- **Risk.** `ordinary`.
- **Audit inputs.** DC-03.
- **Acceptance.** `grep -n -i 'full gate' CLAUDE.md` shows no per-task full gate; the step 3 grep prints
  nothing; `grep -i 'PR test CI' ROADMAP.md` prints the item; the fast lane is green if the step's
  Gates rule calls for it.
- **Test.** The fast lane, per the step's Gates rule.
- **Clock.** 30.

### S3-T7. dubplate adapter (pair P3 with S3-T6; after S3-T5)

- **Outcome.** A project skill `.claude/skills/dubplate-pass/SKILL.md` with the eight fields S1-T6
  names, loading `pass-core`: gate `cairn-run-gate 'bash scripts/check.sh'`; fast lane `bash
  scripts/check.sh --scope-changed` (no `--base`; see the step's Gates rule); full-suite home one local `bash scripts/check.sh`
  on the close head (no PR CI, ruling 11), plus the `go vet -tags oracle ./cmd/harness/...
  ./internal/harness/...` residue when a lane touches those files; worktree rules (which work may
  leave the main tree, given the gitignored beets venv) and the setup S3-T1 found; no CI watch;
  `auth-data` for `internal/auth/**`, `internal/serve/**`, `internal/engine/store/migrations/**`,
  `cmd/dubplate-server/**`, `web/src/routes/{login,members}/**`, and `systemd/**` (each matched
  tracked files on 2026-10-10), `runner` for `scripts/` and `.claude/`, `ordinary` otherwise;
  checklist globs (`web/**` to `svelte-reviewer` and `daisyui-a11y-reviewer`, the `auth-data` paths
  to `web-auth-security-reviewer`, `*.go` to `go-conventions`); a close
  checklist; PG-9 if its scoped gate scopes gitleaks; the moved dubplate pass rules from S3-T5. Pair
  subagents use the workstation `site-implementer` definition or `general-purpose` with the
  `go-conventions` skill named in the dispatch, as the adapter states.
- **Files.** `.claude/skills/dubplate-pass/SKILL.md` (new), `CLAUDE.md` (one pointer line).
- **Risk.** `runner`.
- **Acceptance.** `grep -c -E '^\*\*(Gate|Fast lane|Full-suite home|Worktree setup|CI watch|Risk-class
  path map|Checklist globs|Close checklist)\*\*' .claude/skills/dubplate-pass/SKILL.md` prints 8;
  every `auth-data` glob, braces expanded, matches a tracked file (`git ls-files -- '<glob>'`); the
  scoped gate is green.
- **Test.** The scoped gate.
- **Clock.** 45.

### S3-T8. dubplate HISTORY harvest

- **Outcome.** Every bullet under a rediscover heading in dubplate's `docs/HISTORY.md` (47 headings,
  196 bullets) gets one disposition, reported as in S2-T5, with homes inside dubplate (a
  test, `scripts/check.sh`, a script header, the adapter, `CLAUDE.md` pointers, the governing doc) or
  listed as owed to dotfiles. The file gains the frozen line and no other change.
- **Files.** The homes the harvest writes, `docs/HISTORY.md` (one line).
- **Risk.** `ordinary`.
- **Acceptance.** The PR body states the count and carries the harvest report per Conventions; `git
  diff origin/master -- docs/HISTORY.md` adds only the frozen line; `wc -l < CLAUDE.md` still prints
  200 or less; the scoped gate is green.
- **Test.** The scoped gate.
- **Clock.** 180.

### S3-T9. Close

- **Outcome.** For each of the six repos: its full-suite home green on the head (aksailingclub-org:
  open its PR as a draft at its first push, then `gh pr checks <n> --watch --fail-fast` as a background
  Bash task; ecxc-ski, 907-life, xcathletes-org, cairn-pub: `cairn-run-gate 'npm run check && npm test
  && npm run build'`; dubplate: `cairn-run-gate 'bash scripts/check.sh'`). One whole-branch review by
  the live `diff-reviewer` (Agent tool, `model: "opus"`) across the six branch diffs, with the checklists each
  repo's adapter globs name; one batched fix chain. Each repo's `docs/STATUS.md` present tense, 60
  lines or fewer; dubplate's next action: once this PR merges, re-plan rung 14a as a lean task list in
  a fresh dubplate session (ruling 12); cairn-pub's STATUS is left as it is (its branch adds only
  `ROADMAP.md`). One PR per repo per Conventions, ready for review; remove the task-clock files;
  notify Geoff with the six links; end.
- **Files.** Five `docs/STATUS.md` files and the fix chain's files.
- **Risk.** `runner`.
- **Acceptance.** Six green full-suite results (`gate exit: 0`, or `gh pr checks` exit 0 for
  aksailingclub-org); `gh pr list -R glw907/<repo> --head lean-cutover --json isDraft` shows one
  non-draft PR in each of the six repos; each touched STATUS at 60 lines or fewer.
- **Test.** The full-suite homes.
- **Clock.** 100.

## Step 4: docs-chain audit

The spec's Rollout step 4 under rulings 7 and 14, before docs stage 2b. Clock stop on.

### Launch for 4 (1b runs it in S1-T18)

```bash
git -C ~/.dotfiles fetch origin &&
[ "$(git -C ~/.dotfiles rev-parse HEAD)" = "$(git -C ~/.dotfiles rev-parse origin/main)" ] &&
cd ~/.dotfiles &&
claude --bg --model sonnet --effort medium --name lean-step4 "$(cat ~/.dotfiles/docs/superpowers/plans/2026-10-10-lean-pass-cutover-prompts/4.txt)"
```

**Launch prompt (4):** `2026-10-10-lean-pass-cutover-prompts/4.txt`.

### S4-T1. Inventory the seats

- **Outcome.** A table of every `agent(` call in `claude/.claude/workflows/docs-page-chain.js`, each
  marked generative (page inputs, plan, framing, drafter, redrafts), mechanical (the outline and rework
  probes at `model: "sonnet"`, `effort: "low"`), or model-judged (the plan's structural read, the
  page's structural edit, the register editor, the fact read, the figure verifier, and the final
  reader with its retest). Only model-judged seats are audited (ruling 7). Beside it, the
  deterministic gates the chain runs (the docs gate string, Vale's error tier, and whatever else the
  gate string runs).
- **Files.** None (no commit).
- **Risk.** `ordinary`.
- **Acceptance.** The table names every `agent(` call `grep -n 'agent(' claude/.claude/workflows/docs-page-chain.js`
  prints, with its line.
- **Test.** None.
- **Clock.** 20.

### S4-T2. Audit each judged seat's catch record

- **Outcome.** For each model-judged seat, the recorded runs are read: stage 2a's workflow journals
  (`~/.claude/projects/-var-home-glw907-Projects-cairn-cms*/*/subagents/workflows/wf_*/journal.jsonl`
  whose agents carry the chain's labels, `structure:`, `editor:`, `facts:`, `figure:`, `reader:`) and
  the plan ledgers (cairn-cms `docs/superpowers/plans/2026-09-30-draft-docs-stage-2a.md`,
  `2026-10-07-2a-unattended-finish.md`, `2026-10-07-2a-close-finish.md`, and
  `2026-09-28-style-guide-sync.md` J2), with the catch ledger
  (`docs/superpowers/research/2026-10-10-pass-catch-ledger.md`) for severity mapping. A seat keeps its
  place when the record shows at least one unique catch at REAL or above that the deterministic gates
  passed on the same round; a register catch on a published docs page counts (ruling 14). A seat with
  no record is cut (spec step 4). Each verdict cites the ledger line or journal entry.
- **Files.** None (no commit; the verdict table goes in the PR body).
- **Risk.** `ordinary`.
- **Acceptance.** A verdict table with one row per judged seat: keep or cut, the citing record, and
  the catch's severity and uniqueness.
- **Test.** None.
- **Clock.** 90.

### S4-T3. Cut the seats the audit cuts

- **Outcome.** `docs-page-chain.js` runs only the kept judged seats; its header comment, args list,
  and round logic match; the derivation and outline tests cover the new seat set. Agent definition
  files stay: `cairn-register-editor` and `figure-verifier` serve the `register-check` and
  `cairn-figure` skills.
- **Files.** `claude/.claude/workflows/docs-page-chain.js`, `tests/docs-page-chain-derivation.test.mjs`,
  `tests/docs-page-chain-outline.test.mjs`.
- **Risk.** `runner`.
- **Audit inputs.** AW-10 (verify landed).
- **Acceptance.** `grep -c -E 'label: `(<cut labels>)'` over the file prints 0 for each cut seat;
  `node tests/docs-page-chain-derivation.test.mjs` and `node tests/docs-page-chain-outline.test.mjs`
  exit 0; the dotfiles gate is green.
- **Test.** The two test files.
- **Clock.** 60.

### S4-T4. Close

- **Outcome.** The spec's Lifecycle step 6: the dotfiles gate green on the head; one whole-branch
  review by the live `diff-reviewer` (Agent tool, `model: "opus"`); one batched fix chain; this
  branch's `docs/STATUS.md` records step 4 as PR-ready with the kept and cut seats; remove the
  task-clock file; push; `gh pr create` with the verdict table in the body; notify Geoff; end.
- **Files.** `docs/STATUS.md` and the fix chain's files.
- **Risk.** `runner`.
- **Acceptance.** `gate exit: 0` on the pushed head; `gh pr view <the session's branch> --json isDraft`
  shows `false`; `wc -l < docs/STATUS.md` prints 60 or less.
- **Test.** The gate.
- **Clock.** 40.

## Spec gaps this plan resolves

- **Ruling 11 names cairn-pub's ROADMAP, which does not exist.** S3-T1 creates it through
  `log-project`.
- **Ruling 11 needs every repo's adapter to name a full-suite home; the spec names adapters only for
  cairn-cms, the sites, and dubplate.** S1-T6 adds `dotfiles-pass` for the workstation repo.
- **Departure from spec Rollout step 1 ("Step 1 also files ruling 11's PR test CI items on each named
  repo's ROADMAP"), by Geoff's ruling R-B.** dotfiles (S1-T15) and dubplate (S1-T2) file in step 1.
  ecxc-ski, 907-life, xcathletes-org, and cairn-pub file inside their step 3 PRs, because a push to
  their `main` redeploys production (`deploy.yml` on push for the first three, Workers Builds on
  `main` for xcathletes-org; risk review F4), so a ROADMAP commit pushed in step 1 would redeploy four
  sites with no code change. Geoff's merge of each step 3 PR then deploys once, as expected.
- **Departure from spec Execution item 1 (a linked worktree on the pass branch, setup already run),
  by Geoff's ruling R-D.** `pass-core` (S1-T5) launches every future pass with `claude --bg` from the
  repo's main checkout, started by the planning session. The session isolates itself into
  `.claude/worktrees/`, runs the setup there, and commits and pushes the branch it creates (M2), so
  Geoff pastes nothing (ruling 4, the Success test). A `--bg` session started inside an existing
  worktree asks before committing (M2), which is the item's own checkout. Agent view "is in research
  preview" (M2), so S1-T17b's live probe gates the launch, and the interactive paste is the fallback.
  In this cutover 1a, 1b, and step 3 stay interactive: 1a works in a linked worktree before
  `.claude/worktrees/` is ignored or `baseRef` is set, 1b commits on `main` in the main checkout, and
  step 3 starts in `~/Projects`, outside any one repository, over existing worktrees.
- **Departure from spec Execution item 2 for step 3's cross-repo pairs.** The two subagents work in
  different repos' worktrees with no `isolation` parameter, so worktree isolation and the merge step
  do not apply; the disjoint repos isolate them.
- **The merge is Geoff's, in a terminal.** The spec's Close has Geoff merge; auto mode also blocks a
  session from "Merging a pull request no human has approved" (M1). The tag goes on the merge commit's
  parent after the merge (S1-T14), which is what spec Rollout step 1 asks.

Next action: rollout step 5, engine pass B in cairn-cms, re-planned as a lean task list outside the
clock once steps 1 and 2 have merged, its branch merging `main` after step 2, its WIP `dbdc4556`
re-gated through the fast lane, and Task 2 given the `auth-data` read.
