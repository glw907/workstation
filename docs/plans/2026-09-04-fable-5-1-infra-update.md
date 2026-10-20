# Fable 5.1 model, effort, and skill update: implementation plan

**STATUS: APPROVED in principle by Geoff 2026-09-04 ("Go ahead"), then
held for a three-lens adversarial review at his request; this is the revised
plan (49 findings folded, then a verification round of 26 more; provenance
at the end). Executes through the Workflow tool per Geoff's authorization
the same day.**

**Goal:** Tune the workstation's Claude Code configuration for Fable 5.1 by
routing model-less dispatches to Sonnet, writing down the effort policy,
recording the 5.1 economics, auditing the prompts for dated patterns,
de-prescribing one pass skill as a measured experiment, and putting the
whole review on a monthly timer.

**Spec:** `~/.dotfiles/docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md`.
The plan argues from the spec; executors read both. Parent design:
`2026-08-21-fable-conductor-design.md` (the conductor shape is unchanged).

**Budget:** ceiling 1.5M tokens; checkpoint after task 3 and at close.

**Execution (Workflow mode, authorized by Geoff 2026-09-04):** seven
dispatched tasks, at or above the six-task threshold. Tasks 1, 2, 3, 4, 5,
and 7 run in one `~/.claude/workflows/pass-execute.js` invocation with
`parallel: false` (the script has only all-sequential or all-parallel modes,
and two invocations on one working tree would share the index), `repo:
/var/home/glw907/.dotfiles`, `gate: bash scripts/check.sh`, `implementer:
general-purpose`, and an explicit `model` on every task (`sonnet`; task 4
`claude-opus-5`) so no dispatch depends on the variable task 1 changes.
Task 3 is listed only if its file is clean at launch. Task 0 and task 6 stay
in the conductor's hands: task 6 runs as an Agent-tool chain after the
workflow's accepted tasks are committed, because it needs their hashes.
Sequencing forgoes parallelism; clock time is not a budget.

**The chain, per task.** The script forwards only `criteria`, `files`, and
`notes` to the implementer and only `criteria` to the reviewer, so the
staging contract travels in those fields. Every task's `notes` say: read the
plan's task section and execute its steps exactly; stage exactly the task's
paths with `git add`; do not commit. Every task's `criteria` open with:
review only `git diff --staged -- <the task's paths>`; other modified paths
in this repo belong to another live session and are out of scope; then the
task's named checks verbatim. The script marks a task `accepted` only on a
reviewer accept plus a passing gate; the reviewer verifies the named checks
from the implementer's report. After the invocation returns, the conductor
commits each accepted task by path with `git commit -m "<message>" --
<paths>`, in task order. A `needs-decision` record is the conductor's call:
one re-dispatch by Agent tool with the blocking findings, then stop.

## Global constraints (every task)

- Edit stow sources under `~/.dotfiles/`, never the symlinks under
  `~/.claude/` or `~/.bashrc`. Edits to existing files need no `stow -R`;
  new files do (task 7).
- Another live session holds uncommitted edits to
  `claude/.claude/docs/model-economy.md`,
  `claude/.claude/agents/visual-verifier.md`,
  `claude/.claude/skills/vps-conventions/SKILL.md`, `bluefin/flatpaks.txt`,
  `secrets/registry.md`, and `secrets/values.age`. A task starts only when
  none of its own **Files** appears in `git status --short`. Never `git add`
  or commit a path outside the task's own list.
- Prose registers: CLAUDE.md and skills follow
  `~/.claude/docs/voice/agent-facing.md`; the docs follow the Google
  developer-doc register. No em dashes in text this pass writes; existing
  ones outside the edited ranges are out of scope.
- `bash ~/.dotfiles/scripts/check.sh` runs at the end of every task as a
  regression guard. It is nearly insensitive to these edits, so each task's
  acceptance is its own named checks, not the gate.
- Every commit message ends with:

  ```
  Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01U4jBYuUTHmHMR2y3msu3o6
  ```

---

### Task 0: Coordination gate and pre-bake (conductor, no dispatch)

**Files:** none edited.

- [ ] **Step 1: Per-task intersection check.** Run
  `git -C ~/.dotfiles status --short`. For each of tasks 1 through 7,
  compare its **Files** list with the output. Today this clears tasks 1
  (`settings.json`, `.bashrc`), 2 (`CLAUDE.md`), 4 (a new report), 5
  (`site-pass/SKILL.md`), 6 (`docs/`), and 7 (`upkeep/`, `bin/`,
  `bootstrap.sh`, `ROADMAP.md`); task 3 waits on
  `claude/.claude/docs/model-economy.md`. If task 3 is still blocked when
  tasks 1 through 7 are otherwise done, write STATUS naming it blocked and
  report that in the close message rather than stalling the pass.
- [ ] **Step 2: Commit the plan and spec** (pre-bake). STATUS is task 6's
  file and is not touched here.

  ```bash
  cd ~/.dotfiles
  git add docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md \
          docs/superpowers/plans/2026-09-04-fable-5-1-infra-update.md
  git commit -m "Add the Fable 5.1 infra update plan and spec" -- \
          docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md \
          docs/superpowers/plans/2026-09-04-fable-5-1-infra-update.md
  ```

---

### Task 1: Default model-less dispatches to Sonnet through settings

**Files:**
- Modify: `~/.dotfiles/claude/.claude/settings.json` (top level; add an
  `env` block or a key in the existing one)
- Modify: `~/.dotfiles/bash/.bashrc:177-180` (remove the comment and export)

**Interfaces:**
- Produces: `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` for every session, applied
  to running sessions when the file changes. Task 2's CLAUDE.md text states
  this; task 3 records the decision.

Facts the task rests on (Anthropic's env-vars and sub-agents docs, read
2026-09-04): a settings `env` value replaces the shell's value and is
reapplied to a running session when the file changes; a per-dispatch model
or a frontmatter `model:` outranks the variable; the variable does not reach
the built-in `Explore` and `Plan` agents.

- [ ] **Step 1: Add the settings entry.** Run
  `grep -c '"env"' ~/.dotfiles/claude/.claude/settings.json`. If it prints
  `0`, insert after the line `  "model": "fable",`:

  ```json
    "env": {
      "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet"
    },
  ```

  If it prints `1`, add `"CLAUDE_CODE_SUBAGENT_MODEL": "sonnet"` as a key
  inside the existing object, keeping the file's indentation. Then:

  ```bash
  python3 -m json.tool ~/.dotfiles/claude/.claude/settings.json > /dev/null && echo JSON-OK
  ```

- [ ] **Step 2: Remove the shell export.** Delete these four lines from
  `.bashrc` (currently 177 to 180) and the blank line that follows them:

  ```bash
  # Claude Code: restore normal subagent model resolution so each
  # agent's frontmatter model: wins (per-dispatch model beats
  # frontmatter beats the main model). Pin cheap roles in frontmatter.
  export CLAUDE_CODE_SUBAGENT_MODEL=inherit
  ```

  ```bash
  bash -n ~/.dotfiles/bash/.bashrc && echo SYNTAX-OK
  grep -c CLAUDE_CODE_SUBAGENT_MODEL ~/.dotfiles/bash/.bashrc
  ```

  Expected: `SYNTAX-OK`, then `0`. A runtime probe of the shell cannot tell
  the two homes apart: a settings `env` value reaches every subprocess,
  including an interactive subshell.

- [ ] **Step 3: Prove the routing with a session-pinned probe.** The probe
  is a nested print-mode session; it works inside a running session, the
  Agent tool is permitted without flags, and it bills the API key set in
  this shell (a few cents), so it uses `sonnet` as the session model. The
  probe's own transcript is found by its `session_id`, never by `ls -t`,
  because other sessions on this machine write to the same tree. If the
  nested session errors, or no `subagents/` directory appears for its id,
  report "could not do" with the error; the conductor then verifies with
  one in-session `general-purpose` dispatch read from this session's own
  transcript.

  ```bash
  cd ~
  out=$(claude -p --model sonnet --output-format json \
    "Use the Agent tool with subagent_type general-purpose to compute 2+2. Reply with the agent's answer only.")
  sid=$(printf '%s' "$out" | python3 -c 'import json,sys;print(json.load(sys.stdin)["session_id"])')
  ls ~/.claude/projects/-var-home-glw907/"$sid"/subagents/agent-*.jsonl
  grep -ho '"model":"[^"]*"' ~/.claude/projects/-var-home-glw907/"$sid"/subagents/agent-*.jsonl | sort | uniq -c
  ```

  Expected: `ls` lists at least one file (zero files is a hard failure, not
  a pass); every model line is `claude-sonnet-5`. Any other model means the
  settings entry is not being honored for a model-less dispatch; report it
  as "could not do" with the transcript path.

- [ ] **Step 4: Confirm a frontmatter pin still wins.** Same shape, a
  trivial task for a pinned agent; the transcript is the evidence, not the
  agent's self-report.

  ```bash
  cd ~
  out=$(claude -p --model sonnet --output-format json \
    "Use the Agent tool with subagent_type diff-reviewer and the prompt: reply with the single word OK. Reply with its answer only.")
  sid=$(printf '%s' "$out" | python3 -c 'import json,sys;print(json.load(sys.stdin)["session_id"])')
  grep -ho '"model":"[^"]*"' ~/.claude/projects/-var-home-glw907/"$sid"/subagents/agent-*.jsonl | sort | uniq -c
  ```

  Expected: `claude-opus-5` on every line.

- [ ] **Step 5: Gate and stage.**

  ```bash
  bash ~/.dotfiles/scripts/check.sh
  cd ~/.dotfiles && git add claude/.claude/settings.json bash/.bashrc
  ```

**Acceptance:** `JSON-OK`, `SYNTAX-OK`, the grep count `0`, step 3 shows only
`claude-sonnet-5`, step 4 shows only `claude-opus-5`; staged paths are
exactly the two files. Conductor's commit message: "Default model-less
Claude subagent dispatches to Sonnet".

---

### Task 2: Write the effort policy into CLAUDE.md, under budget

**Files:**
- Modify: `~/.dotfiles/claude/.claude/CLAUDE.md` (the "Conducting a pass"
  section, lines 229-247; compressions also permitted in "Multi-agent
  workflows: suggest, never launch unprompted" and "Initiative-scoped
  sessions")

**Interfaces:**
- Consumes: task 1's decision (settings `env`, value `sonnet`).
- Produces: the effort rule task 3's doc points at.

Read `~/.claude/docs/voice/agent-facing.md` before editing. CLAUDE.md is
~6,034 tokens against a 6,000 budget. The review measured the first draft's
edits at 6,053 and this draft's steps 1 and 2 at 6,038; the step 3
compressions in "Conducting a pass" alone measured 5,986, exit 0, so the
later targets are a reserve. Capture the date inventory first:

```bash
S=/tmp/claude-1000/-var-home-glw907/430691a1-0af3-4b53-946c-5645057adb27/scratchpad
grep -o "2026-0[0-9]-[0-9][0-9]" ~/.dotfiles/claude/.claude/CLAUDE.md | sort | uniq -c > "$S/claude-md-dates.before"
```

- [ ] **Step 1: Replace the dispatch paragraph.** It begins at line 229
  with "Every dispatch names a model and an effort" and ends at line 236
  with "check which model ran." Replace the whole paragraph with:

  ```markdown
  Every dispatch names a model and an effort: `sonnet` by default, `haiku` for mechanical
  search, `claude-opus-5` for reviewers (cross-model diversity). A dispatch without a model
  falls to `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` (settings `env`); a frontmatter pin or a
  per-dispatch model wins, so upshifts pass `model` explicitly: `opus` for novel
  correctness-critical logic the plan does not specify, `fable` only when an Opus verdict
  hedges on something that matters. Effort stays `high`; raise it for research-shaped turns
  rather than lowering it (Fable 5.1 at `low` answers from memory), and `max` is for one
  adjudication. Subagents start with zero context: pre-extract what the task needs. When a
  dispatch runs slow, expensive, or weak, check which model ran.
  ```

- [ ] **Step 2: Replace the allowance sentences.** Lines 243 to 247 hold,
  wrapped across lines, the text from `Do not run the \`writing-plans\`
  "which execution method?" question.` through the
  `~/.claude/docs/model-economy.md` path. Keep the `writing-plans` sentence
  and replace everything after it, rewrapping the paragraph, with:

  ```markdown
  Fable on Max draws from the weekly pool up to a 50% cap (verified 2026-08-21); how the pool
  meters Fable tokens is unpublished, so minimize Fable context, never Fable turns
  (`~/.claude/docs/model-economy.md`).
  ```

- [ ] **Step 3: Compress, wording only, keeping every rule and every
  date.** Permitted targets, in this order until the budget passes:
  - In "Conducting a pass": "The plan-approval gate is the single human
    gate and is no longer a model boundary." becomes "The plan-approval gate
    is the single human gate."; "(Geoff, 2026-09-03: a standing goal;
    parallel dispatch of independent work costs the same tokens and none of
    his attention)" becomes "(Geoff, 2026-09-03)"; "run
    `~/.claude/workflows/pass-execute.js`, which pipelines the chain and
    returns one report per task. A plan that names the workflow mode is the
    opt-in." becomes "run `~/.claude/workflows/pass-execute.js` (a plan
    naming the mode is the opt-in)."
  - In "Multi-agent workflows: suggest, never launch unprompted": shorten
    the guards paragraph to its rule and its doc pointer; the two guards,
    their thresholds (30 minutes, 11% and 10% battery, 15 idle minutes), and
    the `journalctl` note must survive.
  - In "Initiative-scoped sessions": shorten the parenthetical example to a
    clause; keep the rule and its date.

- [ ] **Step 4: Check the budget and the dates.**

  ```bash
  claude-context-budget ~/.dotfiles/claude/.claude/CLAUDE.md; echo "exit=$?"
  grep -o "2026-0[0-9]-[0-9][0-9]" ~/.dotfiles/claude/.claude/CLAUDE.md | sort | uniq -c | diff - "$S/claude-md-dates.before" && echo DATES-OK
  grep -c 'CLAUDE_CODE_SUBAGENT_MODEL=sonnet' ~/.dotfiles/claude/.claude/CLAUDE.md
  ```

  Expected: `exit=0`, `DATES-OK`, `1`. If the budget still fails after all
  permitted targets, stop and report the count as "could not do"; the
  conductor decides what stays loaded.

- [ ] **Step 5: Gate and stage.**

  ```bash
  bash ~/.dotfiles/scripts/check.sh
  cd ~/.dotfiles && git add claude/.claude/CLAUDE.md
  ```

**Acceptance:** `exit=0`, `DATES-OK`, the grep count `1`; the reviewer
confirms no rule was dropped from any compressed paragraph. Commit message:
"Write the Fable 5.1 effort policy into CLAUDE.md".

---

### Task 3: Record the 5.1 economics

**Files:**
- Modify: `~/.dotfiles/claude/.claude/docs/model-economy.md`
- Modify: `~/.dotfiles/claude/.claude/docs/fable-post-cutoff-system.md:12`

**Interfaces:**
- Consumes: the decisions from tasks 1 and 2.

Google developer-doc register. This task starts only when
`git -C ~/.dotfiles status --short claude/.claude/docs/model-economy.md`
prints nothing.

- [ ] **Step 1: Find or create the 5.1 section.** Run
  `grep -c '^## Fable 5.1' ~/.dotfiles/claude/.claude/docs/model-economy.md`.
  If `1`, the other session's paragraph is present: in it, replace the
  clause "unpinned subagents inherit the session model, so they follow the
  switch automatically" with "a dispatch without a model now falls to
  `sonnet` through the settings `env` entry (decisions below)"; the clause
  wraps across two lines, so rewrap the paragraph after replacing. If `0`,
  append this section heading and paragraph to the end of the file:

  ```markdown
  ## Fable 5.1 (noted 2026-09-04)

  Fable 5.1 shipped 2026-09-01 (Mythos 5.1 alongside; no Opus or Sonnet
  5.1). Same $10/$50 per MTok as Fable 5, with cache reads cut to a quarter
  of Fable 5's rate. Claude Code re-reads the conversation at the cached
  rate on every request (costs doc), so the cut lands on long conducting
  sessions; the cache share on this machine is unmeasured until the monthly
  `Prompt cache (main)` reading. Geoff moved sessions to 5.1 on 2026-09-04.
  Reviewer pins stay `claude-opus-5` and implementer pins stay `sonnet`; a
  dispatch without a model now falls to `sonnet` through the settings `env`
  entry (decisions below).
  ```

- [ ] **Step 2: Append these subsections to the 5.1 section.**

  ```markdown
  ### Prices and benchmarks (verified 2026-09-04)

  | Measure | Fable 5.1 | Fable 5 | Opus 5 |
  |---|---|---|---|
  | Input / output, per MTok | $10 / $50 | $10 / $50 | $5 / $25 |
  | Cache read, per MTok | $0.25 | $1.00 | $0.50 |
  | Batch input / output, per MTok | $5 / $25 | $5 / $25 | $2.50 / $12.50 |
  | Terminal-Bench 4.0 | 55.8% | 42.0% | 52.3% |

  Prices: the 5.1 row from Anthropic's announcement and the "What's new"
  page (cache reads at 0.025 times base input; batch at half); the Fable 5
  and Opus 5 rows from claude.com/pricing (batch is 50% off base). The
  benchmark row is Anthropic's own table from the announcement; effort
  levels are not published, and the margin is effort-sensitive. Anthropic
  estimates Fable 5.1 costs about 25% less than Fable 5 for typical
  workloads and up to about 45% less for highly agentic work. Two independent
  per-task measurements point opposite ways on different measures.
  Cognition's FrontierCode 1.1 Extended, completed tasks inside Devin's
  harness, put Fable 5.1 at $2.68 per task against $5.84 for Fable 5 and
  $3.51 for Opus 5 (Devin blog; fetch the page once and confirm the three
  figures and the benchmark name before staging, and report a mismatch as
  "could not do"). Artificial Analysis measured $3.76 per Intelligence Index
  task at `max` effort against Fable 5's $3.14, about 20% more, because 5.1
  emits roughly 1.7 times the output tokens. The saving is effort-dependent,
  which is why the effort rule keeps `high` as the standing level.

  ### The pool-metering unknown

  The support page says Fable models "draw from your plan's regular weekly
  usage limits and use them faster than other Claude models" and that Fable
  5 and 5.1 "work the same way on your plan". No Anthropic page states how
  the draw is computed, and Claude Code's `/usage` shows plan bars shared
  across all models plus attribution by skill, subagent, plugin, and MCP
  server, with no per-model share. The question cannot be measured from this
  machine, so the thin-conductor rule stays as strict as under Fable 5. The
  monthly review records the overall 7-day bar and the behavior flags as a
  trend (spec checklist, item 4); if Anthropic publishes the metering basis,
  that item is replaced.

  ### Decisions taken 2026-09-04

  - `CLAUDE_CODE_SUBAGENT_MODEL` moved from a `.bashrc` export of `inherit`
    to a `settings.json` `env` entry of `sonnet`. A settings value outranks
    the shell and is reapplied to running sessions when the file changes. It
    reaches only dispatches that carry no model of their own:
    `general-purpose`, `claude`, custom agents without a pin, and Workflow
    `agent()` without `model`. It does not reach the built-in `Explore`
    (already capped at Opus) or `Plan`; forcing it onto them would also
    override every frontmatter pin. The plugin `code-simplifier` is pinned
    `opus` in its own frontmatter and was never at Fable price.
  - Effort: `medium` is the committed default (Geoff, 2026-09-04, on the
    outside evidence in `2026-09-04-fable-5-1-outside-evidence.md`); raise
    to `high` for plan authorship, adjudication, and research-shaped turns
    rather than lowering, because Fable 5.1 at `low` searches less and
    answers from memory; `max` only for one adjudication, and it is
    session-only. `/effort` saves the level per model into `settings.json`
    through the stow symlink, so a raised session is visible drift until
    reset.
  - Reviewer pins stay `claude-opus-5`: half the output price, fresh-context
    work that is not cache-heavy, cross-model diversity, and Anthropic's own
    recommendation to start with Opus 5 for most workloads. Implementers
    stay `sonnet`; `pass-execute.js` implementers fall to the variable only
    when a plan omits `t.model`, and both repo implementer agents are pinned.
    Collapsing the upshift ladder (Fable at `medium` instead of Opus for a
    novel-logic task) needs a per-task cost measurement this machine cannot
    yet make.

  ### 5.1 behavior deltas that matter to conducting

  Anthropic's "What's new" page lists seven behavior differences from Fable
  5; four bear on this workstation. In long agent loops 5.1 may issue one
  tool call per turn where implied reads could be batched. It writes fewer
  user-facing progress updates during long tool-calling turns. At `low`
  effort it calls a search or retrieval tool less often and answers from
  memory, which is the premise of the "raise effort for research-shaped
  turns" rule. It is more likely to rewrite a whole file where a targeted
  edit would do, which matters only when the conductor edits inline. The
  prompting page adds that at `xhigh` and `max` it can draft a long
  deliverable in its thinking and write it out again in the reply, costing
  extra output tokens and time; that is the `max` adjudication turn the
  effort rule allows. Claude Code's own turn prompts appear to carry
  equivalent batching and progress reminders (observed in-session
  2026-09-04; not documented, and not verified as the same text). The
  public prompting page expects Fable 5 prompts to carry
  over unchanged; the bundled `claude-api` skill's long-running-agent notes
  say prior-model prompts and skills are often too prescriptive and reduce
  output quality. The prompt-audit report at
  `~/.dotfiles/docs/superpowers/plans/2026-09-04-prompt-audit-report.md`
  and the site-pass experiment (HISTORY 2026-09-04) test which reading holds
  here.

  Sources: https://www.anthropic.com/claude-fable-and-mythos-5-1;
  https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1;
  https://platform.claude.com/docs/en/models/fable-5-1/migration-guide;
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1;
  https://claude.com/pricing;
  https://support.claude.com/en/articles/15424964-claude-fable-5-on-your-plan;
  https://code.claude.com/docs/en/sub-agents; https://code.claude.com/docs/en/env-vars;
  https://code.claude.com/docs/en/costs; https://artificialanalysis.ai/articles/claude-fable-5-1;
  https://devin.ai/blog/fable-5-1; the `claude-api` skill's
  `shared/model-migration.md` (Fable 5.1 sections).
  ```

- [ ] **Step 3: Update the overflow doc's price line.** In
  `fable-post-cutoff-system.md`, line 12 contains "(output ~$50/MTok, 2x
  Opus 5)". Change it to "(output $50/MTok, 2x Opus 5; cache reads
  $0.25/MTok on Fable 5.1, half Opus 5's; batch $5/$25)".

- [ ] **Step 4: Checks, gate, stage.**

  ```bash
  f=~/.dotfiles/claude/.claude/docs/model-economy.md
  grep -c '^## Fable 5.1' "$f"; grep -c 'follow the switch automatically' "$f"
  grep -c '^### ' "$f"
  bash ~/.dotfiles/scripts/check.sh
  cd ~/.dotfiles && git add claude/.claude/docs/model-economy.md claude/.claude/docs/fable-post-cutoff-system.md
  ```

  Expected: `1`, `0`, and `4` (the file has no `###` headings today).

**Acceptance:** the three counts as expected; the reviewer confirms the
prices match the table in this task and nothing contradicts task 1's
decision. Commit message: "Record Fable 5.1 economics and decisions".

**Checkpoint:** write STATUS (task ledger, decisions, spend, next task)
after this task, or after task 7 if task 3 is blocked.

---

### Task 4: Prompt audit report (independent; dispatch to Opus)

**Files:**
- Create: `~/.dotfiles/docs/superpowers/plans/2026-09-04-prompt-audit-report.md`

The implementer is `general-purpose` with `model: "claude-opus-5"`: the
audit is judgment over prose written for earlier models. Read-only against
the config; the only write is the report.

- [ ] **Step 1 (conductor): stage the guide and snapshot the dirty set.**

  ```bash
  S=/tmp/claude-1000/-var-home-glw907/430691a1-0af3-4b53-946c-5645057adb27/scratchpad
  g=$(ls -t /tmp/claude-1000/bundled-skills/*/*/claude-api/shared/prompt-audit.md | head -1)
  cp "$g" "$S/prompt-audit.md" && echo "guide: $S/prompt-audit.md"
  git -C ~/.dotfiles status --short claude/ > "$S/claude-dirty.before"
  ```

  If the glob finds nothing, invoke the `claude-api` skill and copy
  `shared/prompt-audit.md` from the base directory it reports.

- [ ] **Step 2: Dispatch with this prompt** (fill the scratchpad path):

  > Read `<SCRATCHPAD>/prompt-audit.md` in full and execute it, not
  > summarize it. Scope: `~/.dotfiles/claude/.claude/CLAUDE.md`, every
  > `*.md` under `~/.dotfiles/claude/.claude/agents/`, every `SKILL.md`
  > under `~/.dotfiles/claude/.claude/skills/`, and every file under
  > `~/.dotfiles/claude/.claude/docs/voice/`. Target model: Claude Fable 5.1
  > (`claude-fable-5-1`), the session model on this workstation. Produce the
  > audit report only; do not edit any scoped file and do not produce a
  > diff. Write the report to
  > `~/.dotfiles/docs/superpowers/plans/2026-09-04-prompt-audit-report.md`.
  > Format each finding as one list item that begins with `- ` and contains
  > the location in backticks as `path:line`, then the pattern, why it is
  > dated for Fable 5.1, and a confidence, and ends with the literal tag
  > `[keep]` or `[trim]`. Tag `[keep]` by default any rule that cites a
  > person and a date, a "Born" incident, or a named failure; those are
  > incident-born and out of scope for trimming. Tag `[trim]` only
  > step-by-step scaffolding that enumerates how to work where a goal and
  > constraints would do. End the report with one line `Tally: keep N, trim
  > M` and then the three highest-confidence `[trim]` findings restated.
  > Google developer-doc register; no em dashes.

- [ ] **Step 3: Verify the report shape and that nothing else changed.**

  ```bash
  S=/tmp/claude-1000/-var-home-glw907/430691a1-0af3-4b53-946c-5645057adb27/scratchpad
  f=~/.dotfiles/docs/superpowers/plans/2026-09-04-prompt-audit-report.md
  k=$(grep -c '\[keep\]$' "$f"); t=$(grep -c '\[trim\]$' "$f")
  n=$(grep -cE '^- .*`[^`]+:[0-9]+`' "$f")
  echo "keep=$k trim=$t findings=$n"; [ $((k+t)) -eq "$n" ] && [ "$n" -ge 1 ] && echo SHAPE-OK
  grep -c '^Tally: keep [0-9]*, trim [0-9]*$' "$f"
  git -C ~/.dotfiles status --short claude/ | diff - "$S/claude-dirty.before" && echo NO-SCOPED-EDITS
  ```

  Expected: `SHAPE-OK`, `1`, `NO-SCOPED-EDITS`.

- [ ] **Step 4: Gate and stage.**

  ```bash
  bash ~/.dotfiles/scripts/check.sh
  cd ~/.dotfiles && git add docs/superpowers/plans/2026-09-04-prompt-audit-report.md
  ```

**Acceptance:** step 3's three expected outputs; the reviewer spot-checks
that dated or incident-cited rules carry `[keep]`. Commit message: "Add the
Fable 5.1 prompt audit report".

---

### Task 5: Restate site-pass start and discipline (independent experiment)

**Files:**
- Modify: `~/.dotfiles/claude/.claude/skills/site-pass/SKILL.md:34-72`
  ("Starting a pass") and `:198-210` ("Execution discipline")

Read `~/.claude/docs/voice/agent-facing.md` first. Every section outside the
two ranges, including the whole "Ending a pass" ritual, the starter-prompt
format, and "When NOT to use", is byte-identical before and after. Each
replacement block below ends with one blank line so the next heading does
not abut it.

- [ ] **Step 1: Capture the untouched sections.**

  ```bash
  S=/tmp/claude-1000/-var-home-glw907/430691a1-0af3-4b53-946c-5645057adb27/scratchpad
  cd ~/.dotfiles/claude/.claude/skills/site-pass
  sed -n '73,197p' SKILL.md > "$S/site-pass-ritual.before"
  sed -n '211,$p' SKILL.md > "$S/site-pass-tail.before"
  head -1 "$S/site-pass-ritual.before"; head -1 "$S/site-pass-tail.before"
  ```

  Expected first lines: `## Ending a pass: the consolidation ritual` and
  `## Starter-prompt format`.

- [ ] **Step 2: Replace lines 34 to 72 ("Starting a pass") with:**

  ```markdown
  ## Starting a pass

  Three things are true before the first implementer dispatch:

  - You hold the pass number and starter prompt (from `docs/STATUS.md`) and
    the pass plan. If no plan exists and the starter prompt lists open
    questions, brainstorm first (`superpowers:brainstorming`), then write the
    plan at `docs/superpowers/plans/YYYY-MM-DD-<topic>.md` from
    `plan-template.md`.
  - The plan header carries a token ceiling, a checkpoint interval (default
    four tasks), and exactly one of a consultation-brief link or the line
    "no engine asks", produced by the `engine-consult` skill. If it carries
    neither, run the engine-contact enumeration per `engine-consult` now and
    append the resulting line to the committed plan. This is blocking: no
    `site-implementer` dispatch until the header carries one of the two.
  - The plan is committed and STATUS.md's starter prompt points at it.

  Constraints while executing, in this session regardless of model:

  - Each task runs as the chain. `site-implementer` (Sonnet) makes the
    failing check green, clears the repo gate, and returns files touched,
    the gate result, and anything it could not do. `diff-reviewer`
    (`claude-opus-5`) reads the diff against the task's acceptance criteria
    and returns accept, fix, or escalate with `file:line` findings; the
    conductor does not read the diff. One re-dispatch on `fix`; a second
    `fix` is the conductor's decision.
  - Below six tasks, dispatch the chain per task with the Agent tool. At six
    or more, or when the plan marks tasks independent, run
    `~/.claude/workflows/pass-execute.js` with `{repo: "<site repo>", gate:
    "<repo's full gate command>", implementer: "site-implementer", tasks:
    [{id, title, criteria, files, notes}]}`.
  - Implement a task inline, or upshift a dispatch to `model: opus`, only
    for novel correctness-critical logic the plan does not fully specify;
    `model: fable` only when an Opus verdict itself hedges on something that
    matters.
  - At each checkpoint, at any split, and before any question to the user,
    write STATUS.md (task ledger, decisions taken, spend, next task), then
    continue.

  ```

- [ ] **Step 3: Replace "Execution discipline"** (locate by heading after
  step 2; originally lines 198 to 210) with:

  ```markdown
  ## Execution discipline

  - **One implementer per dispatch, verified.** Wait for each
    `site-implementer` result and verify its commit (git log and status)
    before depending on it. On an API overload or 5xx, wait and retry once
    deliberately; never fire a second dispatch while one may still be in
    flight.
  - **Suggest the Workflow tool at the right moments.** It runs only on the
    user's explicit opt-in ("use a workflow"), so name the moment it would
    pay off (mostly independent tasks, a large review gate, a site-wide
    audit or migration) in one sentence with the shape and rough scale.

  ```

- [ ] **Step 4: Byte check and anchor check.**

  ```bash
  S=/tmp/claude-1000/-var-home-glw907/430691a1-0af3-4b53-946c-5645057adb27/scratchpad
  cd ~/.dotfiles/claude/.claude/skills/site-pass
  a=$(grep -n '^## Ending a pass' SKILL.md | cut -d: -f1)
  b=$(grep -n '^## Execution discipline' SKILL.md | cut -d: -f1)
  c=$(grep -n '^## Starter-prompt format' SKILL.md | cut -d: -f1)
  sed -n "${a},$((b-1))p" SKILL.md | diff - "$S/site-pass-ritual.before" && echo RITUAL-OK
  sed -n "${c},\$p" SKILL.md | diff - "$S/site-pass-tail.before" && echo TAIL-OK
  for k in engine-consult pass-execute.js diff-reviewer site-implementer "no engine asks" "token ceiling" "checkpoint interval" '"use a workflow"' "Implement a task inline"; do
    grep -qF -- "$k" SKILL.md && echo "anchor ok: $k" || echo "MISSING: $k"; done
  wc -l SKILL.md
  ```

  Expected: `RITUAL-OK`, `TAIL-OK`, nine `anchor ok` lines, and a line
  count of `231`.

- [ ] **Step 5: Gate and stage.**

  ```bash
  bash ~/.dotfiles/scripts/check.sh
  cd ~/.dotfiles && git add claude/.claude/skills/site-pass/SKILL.md
  ```

**Acceptance:** step 4's expected output in full; the reviewer compares the
two replaced sections rule by rule against `git diff --staged` and confirms
no rule, path, or agent name is lost. Commit message: "Restate site-pass
start and discipline as outcomes and constraints".

**Experiment protocol (recorded by task 6, run by the next site pass):** the
next pass in ecxc-ski or 907-life, whichever runs first, executes on the
rewritten skill. Its HISTORY entry already records tokens against the
ceiling, human interaction points, and what the gate caught. Compare those
three against the repo's previous pass entry and record the comparison in
the dotfiles HISTORY under the 2026-09-04 entry. A worse result on any of
the three reverts this task's commit (hash derived in task 6); a
same-or-better result opens `cairn-pass` to the same treatment in a later
pass.

---

### Task 6: Close out the ledgers and memory

**Files:**
- Modify: `~/.dotfiles/docs/HISTORY.md` (new entry under the intro)
- Modify: `~/.dotfiles/docs/STATUS.md` ("Immediate next action")
- Modify: `~/.claude/projects/-var-home-glw907/memory/monthly-model-review.md`
  (outside the repo; the reviewer must Read it directly)

**Interfaces:**
- Consumes: the CLAUDE.md token count from task 2, and task 5's commit hash
  via `git -C ~/.dotfiles log -1 --format=%h -- claude/.claude/skills/site-pass/SKILL.md`.

Runs after every other task's commit (task 3 excepted if blocked; then the
HISTORY entry says so).

- [ ] **Step 1: Add the HISTORY entry** directly under the four-line intro,
  before the 2026-08-30 entry. Fill the bracketed values.

  ```markdown
  ## 2026-09-04 -- Fable 5.1 model, effort, and skill update

  Fable 5.1 (shipped 2026-09-01; same $10/$50, cache reads $0.25/MTok) became
  the session model on 2026-09-04. This pass tuned the configuration around
  it (plan `docs/superpowers/plans/2026-09-04-fable-5-1-infra-update.md`,
  spec `docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md`,
  revised after a three-lens adversarial review of 49 findings).
  `CLAUDE_CODE_SUBAGENT_MODEL` moved from a `.bashrc` export of `inherit` to
  a settings `env` entry of `sonnet`, so dispatches without a model
  (general-purpose, claude, Workflow agent() without model) stopped running
  at Fable price; pins still win, proven by session-pinned transcript.
  CLAUDE.md gained the effort rule (conducting at `high`, raise for research
  turns, `max` for one adjudication, no standing `medium`) and landed at
  [N] tokens under its 6,000 budget. `model-economy.md` carries the 5.1
  prices with primary sources, both per-task cost measurements, and the
  pool-metering question recorded as unmeasurable from this machine. An
  Opus prompt audit wrote `docs/superpowers/plans/2026-09-04-prompt-audit-report.md`
  (nothing applied). `site-pass`'s start and discipline sections were
  restated as outcomes and constraints with every rule kept and the
  pass-end ritual byte-identical, as a measured experiment. A monthly
  `model-review.timer` and a ROADMAP Active entry put the review on a
  cadence; first due 2026-10-01.

  **What a later pass should not rediscover**:

  - **The `.bashrc` comment was wrong about precedence.** It claimed a
    global `CLAUDE_CODE_SUBAGENT_MODEL` would override frontmatter. The
    documented order is per-dispatch model, then frontmatter, then the
    variable, then the session model. The variable never reaches `Explore`
    or `Plan`, and forcing it onto them would override every pin.
  - **A settings `env` value beats the shell and reaches running
    sessions.** `.bashrc` was the weakest home for this variable.
  - **`/usage`'s plan-limit breakdown has no per-model share.** Plan bars
    are shared across models; attribution is by skill, subagent, plugin, and
    MCP server. The Session block's per-model token counts are session API
    totals, not plan draw. Do not plan a per-model pool measurement from it.
  - **`/effort` persists per model into `settings.json`** through the stow
    symlink, so an interactive effort change is dotfiles drift.
  - **CLAUDE.md sits at the budget edge.** `claude-context-budget` was
    already failing (6,034) before this pass; any addition is paid for in
    the same file.
  - **The site-pass experiment is open.** Its verdict comes from the next
    ecxc-ski or 907-life pass's HISTORY numbers, recorded here when known.
    A worse result reverts commit [hash].
  ```

- [ ] **Step 2: Set STATUS.md's next action.** Replace the body of
  "Immediate next action" (currently "None. Steady state: ..." through "No
  pass is in flight.") with:

  ```markdown
  Two items are open from the 2026-09-04 Fable 5.1 pass. Record the
  site-pass experiment's verdict in `docs/HISTORY.md` when the next
  ecxc-ski or 907-life pass closes. Run the first monthly model review on
  2026-10-01 from the checklist in
  `docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md`
  (`model-review.timer` reminds). Otherwise steady state: routine
  `workstation-update` runs; `check-drift` reconciles every manifest
  against the live machine (weekly `check-drift.timer` notifies on drift;
  every install records itself in its tier's manifest same-session, per
  bluefin-admin.md).
  ```

  Then `wc -l ~/.dotfiles/docs/STATUS.md`: at or under 60.

- [ ] **Step 3: Align the project memory.** The file
  `~/.claude/projects/-var-home-glw907/memory/monthly-model-review.md`
  already exists. Replace its body paragraph's last sentence, from "the
  ROADMAP" to the period, with: "the ROADMAP "Active" entry points at it.
  The pool-metering question is recorded as unmeasurable from this machine;
  checklist item 4 is a trend glance, not a per-model measure." In the Why
  line, replace `[[fable-5-1-pool-measurement]]` with
  `[[geoff-works-autonomously]]`; that memory was never created. Leave the
  frontmatter and the rest as they are. Then:

  ```bash
  claude-context-budget ~/.claude/projects/-var-home-glw907/memory/MEMORY.md; echo "exit=$?"
  ```

  Expected: `exit=0`.

- [ ] **Step 4: Gate and stage.**

  ```bash
  bash ~/.dotfiles/scripts/check.sh
  cd ~/.dotfiles && git add docs/HISTORY.md docs/STATUS.md
  ```

**Acceptance:** HISTORY entry present with no bracketed placeholders; STATUS
at or under 60 lines and naming 2026-10-01; memory file updated and
MEMORY.md within budget; the reviewer reads the memory file directly. Commit
message: "Close the Fable 5.1 infra update pass".

---

### Task 7: Put the review on a monthly timer (independent)

**Files:**
- Create: `~/.dotfiles/upkeep/.config/systemd/user/model-review.timer`
- Create: `~/.dotfiles/upkeep/.config/systemd/user/model-review.service`
- Create: `~/.dotfiles/bin/.local/bin/model-review-notify`
- Modify: `~/.dotfiles/bluefin/bootstrap.sh:327-333` (`setup_upkeep_timer`)
- Modify: `~/.dotfiles/ROADMAP.md` (new "Active" section above "Planned")

**Interfaces:**
- Consumes: the spec's "Monthly review checklist" as the template.
- Produces: a desktop notification on the first of each month; the ROADMAP
  entry task 6's HISTORY text points at.

The pattern is `check-drift.timer`, `check-drift.service`, and
`check-drift-notify`, which already live in these packages. Unlike the drift
check, this notification always fires: it is a reminder, not an alarm.

- [ ] **Step 1: Write the timer.**

  ```ini
  [Unit]
  Description=Monthly Claude model, effort, and skill review reminder

  [Timer]
  OnCalendar=monthly
  Persistent=true
  RandomizedDelaySec=1h

  [Install]
  WantedBy=timers.target
  ```

- [ ] **Step 2: Write the service.**

  ```ini
  [Unit]
  Description=Remind Geoff that the monthly Claude model review is due

  [Service]
  Type=oneshot
  ExecStart=%h/.local/bin/model-review-notify
  ```

- [ ] **Step 3: Write the notify script** and make it executable.

  ```bash
  #!/usr/bin/env bash
  set -uo pipefail

  # model-review-notify: timer-facing reminder for the monthly Claude model,
  # effort, and skill review. Always notifies; the review itself runs in a
  # Claude Code session from the spec named below. Logs to the journal so
  # a missed notification is still recorded.

  export PATH="$HOME/.local/bin:/usr/bin:$PATH"

  spec="$HOME/.dotfiles/docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md"
  echo "monthly model review due; template $spec"
  notify-send --urgency=normal "Monthly Claude model review due" \
      "Open Claude Code and say: run the monthly model review. Checklist: ROADMAP.md, Active." \
      2>/dev/null || true
  exit 0
  ```

  ```bash
  chmod +x ~/.dotfiles/bin/.local/bin/model-review-notify
  bash -n ~/.dotfiles/bin/.local/bin/model-review-notify && echo SYNTAX-OK
  ```

  Expected: `SYNTAX-OK` (the repo gate only syntax-checks tracked files).

- [ ] **Step 4: Stow the new files and enable the timer.**

  ```bash
  cd ~/.dotfiles && stow -R upkeep bin
  ls -l ~/.local/bin/model-review-notify ~/.config/systemd/user/model-review.timer
  systemctl --user daemon-reload && systemctl --user enable --now model-review.timer
  systemctl --user list-timers model-review.timer --no-pager
  ~/.local/bin/model-review-notify
  ```

  Expected: both paths are symlinks into `~/.dotfiles`; `list-timers` shows
  a NEXT of 2026-10-01; the manual run prints the journal line and raises
  one desktop notification.

- [ ] **Step 5: Teach bootstrap to enable it.** In `setup_upkeep_timer`,
  after the line `systemctl --user enable --now check-drift.timer`, add:

  ```bash
      systemctl --user enable --now model-review.timer
  ```

  and change the function's echo to
  `echo "== setup: upkeep timers (weekly drift, monthly model review) =="`.

- [ ] **Step 6: Add the ROADMAP entry.** Insert a new section between the
  intro paragraph and `## Planned`:

  ```markdown
  ## Active

  - **Monthly model, effort, and skill review** (Geoff, 2026-09-04): on the
    first of each month `model-review.timer` raises a reminder and a small
    pass runs the "Monthly review checklist" in
    `docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md`:
    model releases against the pins, prices and the plan-usage page, effort
    defaults and saved levels, the usage glance, the open skill experiments,
    and a fresh prompt audit when the target model changed. Standing inputs:
    `claude/.claude/docs/model-economy.md` and
    `docs/superpowers/plans/2026-09-04-prompt-audit-report.md`. Each review
    records its verdicts in `docs/HISTORY.md` and its tokens and interaction
    points per the pass scoring rule. First review due 2026-10-01.
  ```

- [ ] **Step 7: Gate and stage.**

  ```bash
  bash ~/.dotfiles/scripts/check.sh
  check-drift
  cd ~/.dotfiles && git add upkeep/.config/systemd/user/model-review.timer \
          upkeep/.config/systemd/user/model-review.service \
          bin/.local/bin/model-review-notify bluefin/bootstrap.sh ROADMAP.md
  ```

  Expected: gate green; `check-drift` reports clean (stowed symlinks are
  never flagged).

**Acceptance:** `systemctl --user is-enabled model-review.timer` prints
`enabled`; `list-timers` shows the 2026-10-01 fire; the manual run
notifies; `grep -c model-review.timer bluefin/bootstrap.sh` is 1; ROADMAP
has an "Active" section with the entry. Commit message: "Add the monthly
Claude model review timer".

---

## Pass-end scoring

Record tokens spent against the 1.5M ceiling and count human interaction
points (target: the approval message and the close report). A question that
did not change the outcome is a defect.

## Self-review against the spec

- Spec change 1 (subagent default): task 1, documented in tasks 2 and 3.
- Spec change 2 (effort policy): task 2, documented in task 3.
- Spec change 3 (economics): task 3.
- Spec change 4 (prompt audit): task 4.
- Spec change 5 (site-pass experiment): task 5, protocol recorded by task 6.
- Spec change 6 (monthly cadence): task 7; the checklist lives in the spec.
- Spec constraints: budget (task 2 step 4), stow sources (global), the other
  session's dirty files (task 0 and global), stage-then-review chain
  (header), registers (global), pins untouched (no task edits an agent).
- Spec acceptance items map one-to-one onto task acceptance blocks.

## Review provenance

Three `claude-opus-5` reviewers read the first draft on 2026-09-04 with
distinct lenses (harness mechanics, sourced claims, process and fidelity)
and returned 49 findings: 7 blocking, 20 fix, 22 note. All blocking and fix
findings were folded. Declined, with reasons:

- Compressing the "Secrets" or "Engine-level UI mechanics" sections of
  CLAUDE.md to make budget: both are incident-born rules; the two process
  sections named in task 2 were opened instead.
- Summing local transcript tokens by model as a pool proxy: it cannot
  answer how the server meters the pool, so the protocol was dropped rather
  than replaced with a number that looks like an answer.
- A floor of ten findings on the prompt-audit report: arbitrary; the shape
  check requires at least one and internal consistency.
- Keeping the `.bashrc` export as a fallback beside the settings entry: two
  homes for one value is the confusion the pass removes.

Two reviewer claims were checked against each other. The mechanics reviewer
said the bundled migration guide has no whole-file-rewrite item; it does, in
the "from Claude Fable 5" section, and the "What's new" page lists it too,
so the delta stays. The claims reviewer read "Claude Code injects reminders"
as unsourced; the snippets appear in this session's own turn prompts, so the
sentence stays with that provenance and the "not documented" caveat.

The same three reviewers then verified the folded text and returned 26
further findings (3 blocking, all on fitting the pass-execute workflow, which
Geoff authorized between rounds). All were folded: the workflow's prompts
forward only `criteria`, `files`, and `notes`, so the staging contract now
travels in those fields; every task carries an explicit `model`; the run is
one sequential invocation; the `bash -ic` probe in task 1 became a
source-file grep because a settings `env` value reaches every subprocess;
the behavior-delta paragraph was re-sourced item by item; and the
CLAUDE.md token math was measured to pass (5,986) on the first compression
group alone.
