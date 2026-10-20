# Fable 5.1 model, effort, and skill update

Design basis for the plan at
`docs/superpowers/plans/2026-09-04-fable-5-1-infra-update.md`. This spec
extends the 2026-08-21 conductor design
(`2026-08-21-fable-conductor-design.md`); the conductor shape is unchanged.
The trigger is the Fable 5.1 release (2026-09-01) and Geoff's move of all
sessions to it on 2026-09-04. Revised the same day after a three-lens
adversarial review and a verification round (49 and 26 findings; provenance
at the end of the plan).

## Why

Fable 5.1 keeps Fable 5's $10/$50 per MTok but cuts cache reads to $0.25 per
MTok, against $1.00 on Fable 5 and $0.50 on Opus 5. Claude Code re-reads
the whole conversation at the cached rate on every request, so a long
conducting session's meter leans on cache reads; the share on this machine
is unmeasured until the monthly `Prompt cache (main)` reading. Fable 5.1 leads Opus 5 on every benchmark Anthropic published for
it, including several that Fable 5 trailed on (Terminal-Bench 4.0: 55.8%
against 52.3%, with Fable 5 at 42.0%). Anthropic nonetheless still
recommends starting with Opus 5 for most workloads, which is one reason the
reviewer pins stay on Opus 5. Two independent per-task cost measurements
point opposite ways on different measures: Cognition measured Fable 5.1 cheaper per completed task than both
Fable 5 and Opus 5; Artificial Analysis measured it 20% dearer than Fable 5
at `max` effort because it emits about 1.7 times the output tokens. The
saving is real and effort-dependent.

Three pieces of guidance bear on this workstation's configuration. Anthropic's
public prompting page says Fable 5 prompts carry over to 5.1 without changes;
the bundled `claude-api` skill's long-running-agent notes add that prompts
and skills written for prior models are often too prescriptive and reduce
output quality. Both are Anthropic sources, and they pull in different
directions, which is why the skill change below is an experiment with a
recorded verdict, not a correction. Effort holds up at lower levels
(`medium` roughly matches Fable 5), but at `low` the model searches less and
answers from memory. Parallel sub-agents are dependable and asynchronous
delegation lowers time to completion at similar cost.

One thing stays unknown. On Max, Fable draws from the shared weekly pool up
to a 50% cap; the support page says Fable models "use them faster than other
Claude models" and that Fable 5 and 5.1 "work the same way on your plan". No
Anthropic page states how the draw is computed, and Claude Code's `/usage`
shows no per-model share, so the question cannot be measured from this
machine. The thin-conductor rule stays as strict as it is.

## What changes

1. **Agents dispatched without a model default to Sonnet.** The shell
   exports `CLAUDE_CODE_SUBAGENT_MODEL=inherit`, so `general-purpose`,
   `claude`, and any Workflow `agent()` or custom agent without a model run
   at the session model, which is Fable. The variable moves to the `env`
   block of `settings.json` with the value `sonnet`: a settings value
   outranks the shell and is reapplied to running sessions when the file
   changes. The `.bashrc` export goes. Per Anthropic's sub-agents doc, a
   per-invocation model or a definition's `model` field takes precedence, so
   every frontmatter pin (`claude-opus-5` reviewers, `sonnet` implementers,
   `claude-fable-5-1` visual-verifier, the plugin `code-simplifier` at
   `opus`) keeps working. The variable does not reach the built-in `Explore`
   and `Plan` agents (`Explore` is already capped at Opus); forcing it onto
   them would also override every pin, which this pass does not want.
2. **Effort policy is written down.** Revised by Geoff on 2026-09-04 after
   the outside evidence (the system card's peak coding score at `medium`,
   CodeRabbit's low-beats-high review eval, and the measured 2x output
   tokens per turn): `effortLevel: medium` is the committed default; raise
   to `high` for plan authorship, adjudication, and research-shaped turns
   rather than lowering, because Fable 5.1 at `low` answers from memory;
   `max` is for one adjudication and is session-only. `/effort` saves the
   level per model into `settings.json` through the stow symlink, so a
   raised session shows as a modified file until reset. Sonnet and Opus
   agent efforts are untouched (the guidance is Fable-specific).
3. **The economy docs carry the 5.1 facts.** `model-economy.md` gets the
   price table with primary sources, the benchmark delta with its caveats,
   both per-task cost measurements, the pool-metering unknown as unknown,
   the behavior deltas that matter to conducting, and the decisions with
   their dates. The overflow doc gets the 5.1 prices.
4. **A prompt audit inventories the dated patterns.** An Opus agent runs
   Anthropic's `prompt-audit` guide over CLAUDE.md, the agents, the skills,
   and the voice docs, target model Fable 5.1, and writes a report. Rules
   born from a named incident are marked keep by default. The report is a
   standing input; nothing is applied in this pass.
5. **One skill is de-prescribed as a measured experiment.** `site-pass`'s
   "Starting a pass" and "Execution discipline" sections are restated as
   outcomes and constraints with every rule, path, and agent name kept. The
   pass-end ritual (steps 1 through 8) stays byte-identical because its
   steps are required outputs. The next site pass runs on the rewritten
   skill and its HISTORY entry records gate catches, interaction points, and
   tokens against the previous pass.
6. **The review recurs monthly.** A `model-review.timer` in the upkeep stow
   package raises a desktop reminder on the first of each month, and a
   ROADMAP "Active" entry names the checklist below as the template. The
   review is a small pass: it reads this spec, runs the checklist, folds
   what changed, and records verdicts and numbers in HISTORY.

## Constraints

- CLAUDE.md must exit 0 from `claude-context-budget` when the pass closes.
  It is at ~6,034 tokens today against a 6,000 budget, and the review
  measured the first draft's edits at 6,053. The replacement text is paid
  for by wording-only compressions, measured to land at 5,986 within
  "Conducting a pass" alone, with two further process sections in reserve.
  Every rule and every attribution date survives.
- Every edit lands in the stow sources under `~/.dotfiles/`, never in the
  symlinks under `~/.claude/` or `~/.bashrc`.
- The dotfiles repo has another live session's uncommitted edits in
  `claude/.claude/docs/model-economy.md`,
  `claude/.claude/agents/visual-verifier.md`, and
  `claude/.claude/skills/vps-conventions/SKILL.md`. A task starts only when
  none of its own files is dirty; only task 3 waits today. No commit from
  this pass includes a path outside the task's own file list.
- Execution runs through `pass-execute.js` in one sequential invocation
  (Geoff's Workflow authorization, 2026-09-04). Implementers stage and do
  not commit; the reviewer reads the staged diff for the task's paths and
  any out-of-repo file the task names; the conductor commits on accept. The
  script forwards only `criteria`, `files`, and `notes`, so that contract
  travels in those fields.
- Prose registers: CLAUDE.md and skills follow the agent-facing register
  (`~/.claude/docs/voice/agent-facing.md`); the docs follow the Google
  developer-doc register. No em dashes in text this pass writes; existing
  ones outside the edited ranges are out of scope.
- Nothing here changes the reviewer pins, implementer pins, or the
  pass-execute workflow. `settings.json` changes only by gaining the `env`
  entry.

## Monthly review checklist

Run on the first of each month, from a fresh session, as a small pass with
its own token ceiling and one approval. Each item names what to read and
what a change triggers.

1. **Model releases.** Anthropic's news page and the platform model
   overview since the last review. A new head of a tier changes the matching
   pin: `sonnet` implementers, `claude-opus-5` reviewers, the `fable` session
   model, the `CLAUDE_CODE_SUBAGENT_MODEL` value. Re-run the pin-precedence
   probe from task 1 after any change.
2. **Prices and plan terms.** The pricing page (input, output, cache read,
   batch) and the "Fable on your plan" support page. Update the table in
   `model-economy.md`; a cache-read or cap change re-opens the seat question.
3. **Effort.** Claude Code's per-model effort defaults and the saved
   `modelSettings` in `settings.json` (a saved level is drift). Re-run the
   effort sweep only when the session model changed; level names do not
   mean the same amount of thinking across models.
4. **Usage glance.** The overall 7-day plan bar in `/usage`, its behavior
   flags (long context, cache misses), and the Session block's
   `Prompt cache (main)` share of input tokens from cache in a conducting
   session, recorded with the date in `model-economy.md` as a trend. This is not a per-model measure; if
   Anthropic publishes how the pool meters models, replace this item.
5. **Skill experiments.** Verdicts due from the passes that ran on a
   rewritten skill; revert or extend per the recorded protocol; pick at most
   one next candidate.
6. **Prompt audit.** When the target model changed, re-run the audit (task
   4's dispatch) and diff the report against the previous one; otherwise
   skip.
7. **Close.** HISTORY entry with verdicts and the two budget numbers;
   STATUS next action; the project memory's due date moved one month.

## Out of scope

Collapsing the upshift ladder (Fable at `medium` instead of Opus for
novel-logic implementer tasks) needs a per-task cost measurement this
machine cannot yet make. Changing Sonnet or Opus agent effort levels needs
its own evals. Forcing the subagent model onto `Explore` and `Plan` is not
wanted. Project CLAUDE.md files (cairn-cms, poplar, the sites) are
untouched; they defer to the global rule.

## Acceptance

- `settings.json` carries `"CLAUDE_CODE_SUBAGENT_MODEL": "sonnet"` under
  `env`, `.bashrc` no longer exports it, and a `general-purpose` dispatch in
  a print-mode probe records `"model":"claude-sonnet-5"` in that probe's
  own session transcript under
  `~/.claude/projects/<project>/<session-id>/subagents/`.
- `claude-context-budget ~/.claude/CLAUDE.md` exits 0, and the count of
  attribution dates in CLAUDE.md is unchanged.
- `model-economy.md` has one "Fable 5.1" section, no contradiction with the
  subagent decision, and primary sources first.
- The prompt-audit report exists with `file:line` findings, each tagged
  `keep` or `trim`, and a closing tally.
- `site-pass/SKILL.md` still names `engine-consult`, `pass-execute.js`,
  `diff-reviewer`, `site-implementer`, "no engine asks", the token ceiling,
  and the checkpoint interval; its pass-end ritual and tail are
  byte-identical to today's.
- `systemctl --user is-enabled model-review.timer` prints `enabled`;
  ROADMAP.md has an "Active" entry naming the checklist and 2026-10-01.
- HISTORY.md carries the pass entry; STATUS.md's next action names the
  open experiment and the first monthly review; the project memory matches.
- `bash ~/.dotfiles/scripts/check.sh` is green as a regression guard; it is
  not the acceptance signal for any task.

## Sources

Primary:

- Anthropic, Claude Fable 5.1 and Mythos 5.1 announcement:
  https://www.anthropic.com/claude-fable-and-mythos-5-1
- What's new in Claude Fable 5.1:
  https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1
- Fable 5.1 migration guide:
  https://platform.claude.com/docs/en/models/fable-5-1/migration-guide
- Prompting Claude Fable 5.1:
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
- Pricing: https://claude.com/pricing
- Fable on your plan: https://support.claude.com/en/articles/15424964-claude-fable-5-on-your-plan
- Claude Code sub-agents (model precedence, Explore and Plan):
  https://code.claude.com/docs/en/sub-agents
- Claude Code environment variables (settings `env` outranks the shell):
  https://code.claude.com/docs/en/env-vars
- Claude Code model configuration (effort persistence):
  https://code.claude.com/docs/en/model-config
- Claude Code costs (`/usage` contents): https://code.claude.com/docs/en/costs
- The `claude-api` skill's `shared/model-migration.md`, sections "Migrating
  to Claude Fable 5.1" and "Migrating to Claude Fable 5.1 from Claude Fable
  5" (bundled with Claude Code; the "too prescriptive" guidance lives here).

Secondary:

- Artificial Analysis, Fable 5.1 cost per task at `max`:
  https://artificialanalysis.ai/articles/claude-fable-5-1
- Cognition (Devin), FrontierCode 1.1 Extended cost per task:
  https://devin.ai/blog/fable-5-1
