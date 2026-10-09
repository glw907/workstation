# Model economy: current rules, pricing, and history

The on-demand expansion of CLAUDE.md's "Conducting a pass", "Process proportionality", and
"Pass sizing" sections. CLAUDE.md states the rules; this doc records the current state in one
place, the reasons behind it, and the history a later decision would be wrong to rediscover.
Where the two disagree, CLAUDE.md wins and this doc is stale.

## Current state (2026-10-07)

Seats, per Anthropic's model guidance (Geoff, 2026-09-23):

| Seat | Model | Effort |
|---|---|---|
| Brainstorm | `claude-opus-5-5` | `high` |
| Plan authorship | `claude-opus-5-5` | `high` |
| Conducting execution (the main session) | `claude-opus-5-5` | `medium` |
| Implementers (`cairn-implementer`, `site-implementer`) | `sonnet` | `high` |
| Reviewers (`diff-reviewer`, domain reviewers, verifiers, graders) | `claude-opus-5-5` | `medium` |
| Security review (`web-auth-security-reviewer`) | `claude-opus-5-5` | `high` |
| Published docs drafts (`docs-page-chain.js` `drafterModel`) | `claude-opus-5-5` | `high` |
| Docs chain plan seat (`docs-page-chain.js` `planEffort`) | `claude-opus-5-5` | `high` (Anthropic's effort guidance positions `xhigh` for 30+ minute agentic runs, https://platform.claude.com/docs/en/build-with-claude/effort; Geoff, 2026-10-08) |
| Docs chain framing seat (`framingEffort`) | `claude-opus-5-5` | `xhigh` (Geoff, 2026-10-05; an A/B against `high` is scheduled at stage 2b's start) |
| Mechanical search | `haiku` (alias resolves to `claude-haiku-5-5`, verified 2026-10-07) | `low` |
| Gate runner (pass workflows) | `haiku` (Haiku 5.5) | `low` |
| Escalation only | Fable 5.1 | `high` or above |

- **Fable 5.1 is reached only after Opus 5.5 at `xhigh`, then `max`, falls short.** It is one
  per-dispatch escalation, never a session model switch and never a frontmatter pin. The
  session model changes only at a pass boundary, from the STATUS resume prompt.
- **Reviewer effort is `medium`.** Anthropic's Opus 5.5 prompting guide says the default
  `medium` matches Opus 5 at `high`, and reserves higher effort for measured gains
  (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5).
  Security review keeps `high`: a missed auth defect costs more than the extra tokens.
- **Reviewer overrules.** Reviewers and the conductor share a model, so an overruled verdict is
  stated with its reason in STATUS, and a correctness-critical overrule takes the
  `xhigh`-then-`fable` path.
- **The conductor is thin.** During execution it never reads a source file, a diff, a test log,
  or a gate transcript. It rules on structured reports: accept, re-dispatch with a correction,
  split, upshift, or stop.
- **The per-task chain replaces the conductor's diff read.** Implementer, then `diff-reviewer`
  against the task's acceptance criteria, then the pass class's per-task gate (table:
  `pass-core`), all inside the chain. One re-dispatch on `fix`; a second `fix` is the
  conductor's decision. Domain reviewers fan out at pass end.
- **The pass class sets the ceremony** (commit `319c2a8`, Geoff 2026-09-27). A plan header
  declares `Pass class:` (`auth-data`, `engine-logic`, `paint`, `sweep`, `docs`, `tool`), and a
  task may override it. The class sets the per-task gate, the reviewer's blocking bar, the test
  mandate, and the settle and close steps. The table lives in the `pass-core` skill.
  `pass-execute.js` and `pass-execute-chains.js` take `passClass` and render the mandate and
  the bar into the prompts; this doc never delivers the rule.
- **The Haiku seat reads and copies, never decides.** The gate runner reports the exit code as
  printed and copies failing lines verbatim; judgment stays with the Opus reviewer. Keep any
  Haiku dispatch under 100k tokens of context, because Haiku 5.5's price is 5x above 100k. A
  bigger job goes to Sonnet or is split.
- **Undeclared dispatches fall to `sonnet`.** `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` sits in
  `~/.claude/settings.json` `env`. It reaches only dispatches with no model of their own:
  `general-purpose`, `claude`, unpinned custom agents, and Workflow `agent()` without `model`.
  Frontmatter pins and per-dispatch `model` both win over it.
- **`low` effort is for mechanical subagents only, never Fable 5.1.** `max` is for one
  adjudication, and it is session-only. `/effort` persists per model into `settings.json`
  through the stow symlink, so reset it at session end.
- **Brainstorm length is never a cost to trim, for product and taste questions.** Scope,
  priority, product forks, taste, and budget get extended front-loaded back-and-forth. Method,
  idiom, and architecture calls are Claude's, decided from published evidence, a framework's
  documented convention, or an architectural best practice (Geoff, 2026-09-24 and 2026-09-26).
  Bring those as one design for approval and flag only the contestable points.

### The pass-end score

Score both budgets at every close. Tokens are measured against the plan's ceiling (`/cost`).
Attended time is measured as two counts:

- **Planning misses:** each ambiguity that surfaced after approval that a planning question
  would have caught. A rising count reopens the Opus-authors-plans rule.
- **Execution sittings:** each time Geoff was pulled in after approval. One combined
  checkpoint question counts once.

Planning questions never count against the score. Record the numbers even when they look bad.

## Pricing and the allowance

| Measure | Fable 5.1 | Opus 5.5 | Opus 5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|---|
| Input / output, per MTok | $10 / $50 | $4 / $20 | $5 / $25 | $2 / $10 | $0.10 / $0.50 up to 100k context, $0.50 / $2.50 above |
| Cache read, per MTok | $0.25 | not recorded here (claude.com/pricing) | $0.50 | $0.10 (halved from $0.20 on 2026-10-07) | $0.01 up to 100k, $0.05 above |
| Batch | half of base | half of base | half of base | not recorded here | not recorded here |

Haiku 5.5 source: https://www.anthropic.com/claude-haiku-5-5.

- **The Max allowance (verified 2026-08-21, unchanged for 5.1).** Fable draws from the same
  weekly pool as every model and may take up to 50% of it; past that, usage falls to credits at
  API rates. Anthropic publishes no per-model draw rate, and `/usage` shows no per-model
  share, so the metering cannot be measured here
  (https://support.claude.com/en/articles/15424964-claude-fable-5-on-your-plan). The design
  therefore minimizes Fable's context, never its turns.
- **Overflow.** Beyond the allocation, Fable runs on credits. `fable-post-cutoff-system.md` is
  the overflow playbook: batch-first, per-dispatch one-shots, and never silently spend or
  silently absorb Fable-tier work. Propose job, mode, and size in one sentence and let Geoff
  decide.
- **Fable 5.1's saving is effort-dependent.** Anthropic estimates 25% to 45% below Fable 5.
  Artificial Analysis measured 5.1 at `max` about 20% more per task, from roughly 1.7 times the
  output tokens (https://artificialanalysis.ai/articles/claude-fable-5-1).

## The self-check, with its origin incident

A conductor caught reading a source file, a diff, a test log, or a gate transcript during
execution, or grinding mechanical edits inline, flags itself and dispatches. Root incident: an
ecxc session silently burned about 1M tokens on 2026-07-13 doing execution-shaped work in the
main loop, and Geoff caught it before the conductor did. That order is the defect the
self-check closes.

## Pass sizing: the poplar 1b narrative

CLAUDE.md's Pass sizing rule states the practice; this is the incident that produced it. Geoff
sees per-item summaries in which every addition reads as small; the orchestrator holds the
whole dispatch list, so detecting accumulation is its duty. Three failure modes, all from
poplar pass 1b:

- **A grant is not headroom.** "Use a workflow", "spread this over several passes", or "you
  have latitude" authorize a mechanism or a boundary, never more work. Restate what a grant
  authorizes before acting on it.
- **Accretion by adjacency.** Pass 1b's conformance task took a coverage ledger, an unowned
  method, two doc corrections, and two late defect fixes on top of a full plate. Geoff raised
  the size question twice before the orchestrator did.
- **Splitting tasks instead of the pass (Geoff, 2026-07-30).** Pass 1b split tasks 6, 7, and 11,
  turning twelve tasks into fifteen. Each split was correct alone; none prompted a pass split
  until Geoff asked. A task split keeps work inside the pass; only a pass split lets it leave.

Practice: count your own splits before answering "is this pass too long". A second task split
is the prompt to propose a pass split; a third means it is overdue. A pass born of a burst
predecessor gets watched harder. When proposing, name the cut point, what each half carries,
and the follow-up pass's number. State each task's deliverable count at dispatch, and say so
when it passes about four or grows after dispatch. Route discovered work to the pass that first
leans on it. Never add scope to a task in flight unless it would otherwise build against
something known wrong, and say so when you do.

## History

Compressed; newest first. Each entry keeps what a later decision would be wrong to rediscover.

- **2026-10-07, the gate run moved to a Haiku runner.** The `diff-reviewer` was told to
  reproduce the gate, so every task and every fix round put the full gate transcript into Opus
  context. `pass-execute.js` and `pass-execute-chains.js` now dispatch a Haiku 5.5 runner at
  `low` effort after `resolveGate`, on the first round and on every fix round. It runs the gate
  the reviewer would have reproduced and returns the command, exit code, result, and a capped
  verbatim excerpt of failing output. The reviewer treats that record as the gate result and
  reruns only on a specific reason to doubt it. The runner runs the reduced gate only in a
  class-reduced round of `pass-execute.js`; elsewhere it runs the resolved gate, so coverage
  never shrinks. A class-default reduced gate (prose only) and a gate carrying a `<placeholder>`
  skip the runner, so the reviewer reproduces the gate as before; so does a runner that returns
  nothing, a "not run" record, or a record whose result contradicts its exit code.
- **2026-09-27, ceremony scales by kind of change.** Theme identity pass A, a CSS retheme, ran
  the full engine gate on every task (7 to 11 minutes each), carried about 4.4 test lines per
  source line, reran the full gate on every test-only fix round, and projected 8 to 10
  unattended hours. The diff reviewer also blocked on coverage granularity. Size alone had
  never scaled the chain down, so the pass class was added. `pass-gate-economy.md` records the
  gate side.
- **2026-09-23, aligned with Anthropic's model guidance.** Anthropic's "Choosing the right
  model" says to start with Opus 5.5 for most workloads and reach Fable 5.1 "when your evals on
  Claude Opus 5.5 at higher effort still fall short", and that tuning effort is often a better
  lever than switching models. Opus 5.5 took the brainstorm; `visual-verifier` moved from Fable
  to Opus 5.5; implementers pinned effort `high`; the no-`low` rule narrowed to Fable.
- **2026-09-23, Opus 5.5 authors plans.** After adversarial spec review the hard reasoning lives
  in the spec, and turning it into tasks is the agentic work Opus 5.5 was measured on. The
  check is the planning-miss count, against the Fable-authored draft-docs pass A (three misses).
- **2026-09-22, Opus 5.5 conducts execution.** The conductor's context is re-bought every loop
  tick, making it a pass's largest single spend; Opus 5.5 has a published meter and 1M context,
  where Fable's Max metering is unpublished. First run: cairn retire-2b.
- **2026-09-22, Opus 5.5 drafts published docs pages.** Draft-docs pass A's three Sonnet drafts
  all escalated after two rounds and each needed a conductor-directed third round, so a Sonnet
  draft cost more in review than it saved. Agent-facing prose (facts bullets, HISTORY entries,
  post-mortems) stays with the Sonnet implementer.
- **2026-09-04, Fable 5.1 and the subagent default.** `CLAUDE_CODE_SUBAGENT_MODEL` moved from a
  `.bashrc` export of `inherit` to a `settings.json` `env` value of `sonnet`, because a settings
  value outranks the shell and reapplies to running sessions. Forcing it onto `Explore` or
  `Plan` would also override every frontmatter pin. At `low` effort 5.1 searches less and
  answers from memory, which is why research-shaped turns raise effort.
- **2026-09-04, interaction is front-loaded, never minimized.** The earlier score counted every
  question as a defect, which pushed the conductor to guess at planning time, the one place a
  wrong guess costs a whole pass. Geoff retracted it; the score now separates planning misses
  from execution sittings.
- **2026-08-21, Fable conducts.** The 2026-07-26 split (Fable plans, an Opus 5 session executes)
  was reversed because Opus 5 execution made poor dispatch and triage calls and the
  plan-approval handoff cost attention. That rule held until 2026-09-22. The thin-conductor
  rule and the per-task chain date from it and survive every later change.
- **2026-07-26, reviewers pin Opus.** Beside Sonnet implementers, an Opus reviewer buys
  cross-model diversity against correlated self-review blind spots, and is the diff reader the
  thin conductor never is.

## Research basis

- Multi-agent research system
  (https://www.anthropic.com/engineering/multi-agent-research-system): the lead runs on the
  frontier model and workers run cheaper, yet the pattern costs about 15 times a single
  agent's tokens.
- When to use multi-agent systems
  (https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them): split work
  by information boundary, not by task count.
- Sub-agents (https://code.claude.com/docs/en/sub-agents): a fresh subagent returns only its
  final message.
- Workflows (https://code.claude.com/docs/en/workflows): intermediate results stay in script
  variables; the cost warning is advisory.
- Model config (https://code.claude.com/docs/en/model-config): `effort` is set per agent and is
  cheaper to tune than a model swap.
- GitHub issue 41143 (https://github.com/anthropics/claude-code/issues/41143): `maxTurns` is
  documented but not reliably enforced.
- Opus 5.5 prompting guide
  (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5):
  default `medium` effort; higher effort only for measured gains.
