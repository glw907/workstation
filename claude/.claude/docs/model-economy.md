# Model economy: pricing, history, and mechanics

The on-demand expansion of CLAUDE.md's `## Model economy` section. Read this
when the inline rule isn't enough context to make a call: why the seat split
exists, what things cost, and how the Fable overflow mechanics work. The
inline section in CLAUDE.md is binding; this doc is background.

## Pricing and rate buckets

Fable output costs $50/MTok (2x Opus 5, ~3x Sonnet 5, 10x Haiku 4.5) on the
tightest rate-limit bucket. That gap is why the seat split exists at all: a
Fable conductor doing execution-shaped work (dispatch grinding, gate-running,
bulk reads) is paying the most expensive tier for work that doesn't need it.

Reviewers pin `claude-opus-5-5` (dated-ID pins repointed 2026-07-26; same price
as 4.8, better recall and precision, separate rate bucket). Beside a Fable
planner and Sonnet implementers, the Opus gate buys cross-model diversity
against correlated self-review blind spots; under a Fable conductor the Opus
reviewer is both the fresh-context gate and the diff reader the thin
conductor never is.

## Fable conducts (revised 2026-08-21)

The 2026-07-26 ratification split the seat: Fable planned and judged, an
Opus 5 conductor executed. The split existed because execution is long,
tool-heavy, and cache-read-dominated, and that cost compounds fastest under
Fable's 2x API price. Routing execution to Opus 5 halved the rate on the
most expensive part of a pass.

Four drivers, all confirmed by Geoff on 2026-08-21, reversed it. Opus 5
execution sessions made poorer dispatch and triage calls than the plan
quality deserved. The plan-approval handoff (fresh session, resume prompt,
re-reading artifacts) cost attention and tokens. Passes should run longer
without Geoff present. The Fable allowance has not been the constraint in
practice.

Fable now conducts a coding project from brainstorm through post-mortem in
one session. The plan-approval gate stays the single human gate; it is no
longer a model boundary. The handoff to a fresh Opus 5 session is gone.

**The conductor is thin.** During execution, Fable never reads a source
file, a diff, a test log, or a gate transcript. It consumes structured
reports from agents and makes only the decisions that need judgment: accept,
re-dispatch with a correction, split, upshift, stop. A conductor caught
reading diffs or grinding edits inline flags itself and dispatches.

**The per-task chain replaces the conductor's own diff read.** Each plan
task runs implementer, then diff reviewer, then gate. The repo's
Sonnet-pinned implementer returns a fixed shape: files touched, gate result,
decisions the plan did not cover, anything it could not do. The
`diff-reviewer` agent (`claude-opus-5-5`) takes the task's acceptance criteria
and the implementer's report, reads the diff, and returns a verdict (accept,
fix, escalate) with blocking findings at `file:line`. One re-dispatch on
`fix`; a second `fix` verdict goes to the conductor as a decision. The
repo's full gate runs inside the chain, never in the main loop. Domain
reviewers (svelte, a11y, security, workers) still fan out at pass end.

## The allowance fact (verified 2026-08-21)

On Max, Fable 5 draws from the same weekly pool as every other model and may
consume up to 50% of it. Past that cap, usage falls to credits at API rates
or a model switch. The help page states no per-model weighting, and none
could be verified
(https://support.claude.com/en/articles/15424964-claude-fable-5-on-your-plan,
verified 2026-08-21).

The 50% cap on the weekly pool is the binding constraint, not API price. The
design that follows from it minimizes Fable's context size, never the
number of Fable turns: a thin conductor that reads structured reports
instead of diffs spends less pool per turn, so it can run more turns before
hitting the cap.

## Beyond the allocation: the overflow playbook

Beyond the weekly allocation, Fable runs on usage credits at API rates
($10/$50). `~/.claude/docs/fable-post-cutoff-system.md` governs this as the
OVERFLOW playbook: batch-first (50% discount), per-dispatch one-shots, and
the SUGGESTION RULES baked there (never silently spend Fable credits, never
silently absorb Fable-tier work; propose job + mode + size in one sentence
and let Geoff decide).

## The self-check, with its origin incident

The self-check inverts under a Fable conductor. A conductor caught reading
a source file, a diff, a test log, or a gate transcript during execution, or
grinding mechanical edits inline, flags itself immediately and dispatches
the work to the appropriate agent instead of continuing to do it inline.

This rule's root incident predates the inversion but still names the
failure mode it guards against: an ecxc session silently burned ~1M tokens
on 2026-07-13 doing execution-shaped work in the main loop. The flag came
from Geoff, not the conductor. That order, Geoff catching it instead of the
conductor self-reporting, is the defect the self-check exists to close.

## Pass sizing: the poplar 1b narrative

CLAUDE.md's Pass sizing rule states the practice; this is the incident that
produced it. Geoff has no direct insight into when a pass is overloading.
He sees per-item summaries in which every addition reads as small and
adjacent; the orchestrator holds the whole dispatch list. Detecting
accumulation and raising it unprompted is the orchestrator's duty, and a
pass that quietly doubles costs far more than one split early. Three
failure modes, all named from poplar pass 1b:

- **A grant is not headroom.** "Use a workflow", "we can spread this over
  several passes", "you have latitude" authorize a mechanism or a boundary,
  never more work. Restate what a grant does and does not authorize before
  acting on it.
- **Accretion by adjacency.** Work joins a task because it sits next to what
  that task already does. Each addition is defensible alone and none is
  weighed against the total. Pass 1b's conformance task took a coverage
  ledger, an unowned method, two doc corrections and two late defect fixes
  on top of a full plate, and Geoff had to raise the size question twice
  before the orchestrator said anything.
- **Splitting tasks instead of splitting the pass (Geoff, 2026-07-30).** A
  pass can be split at a logical point, and repeated task splits are the
  signal that it should be. Pass 1b split task 6 into 6a/6b, task 7 into
  7a/7b and task 11 into 11a/11b, turning twelve planned tasks into fifteen.
  Every split was individually correct; each was made because that task had
  outgrown its own written boundary. The orchestrator read them as three
  separate incidents and never considered splitting the pass, until Geoff
  asked whether it had run too long. Splitting a task keeps the work inside
  the pass; only splitting the pass lets work leave, which is why
  task-splitting is the more comfortable move: it looks like sizing
  discipline while changing nothing about the commitment.

Practice: count your own splits before answering "is this pass too long".
The count is the evidence and it is sitting in your dispatch history. A
second task split inside one pass is the prompt to propose splitting the
pass; a third means the proposal is overdue. A pass that exists because its
predecessor burst its scope is already on notice and gets watched harder,
not less. When proposing, name the cut point (usually the last clean
self-contained task), name what each half carries, and give the follow-up
pass a number rather than leaving its work homeless. Also: state a task's
deliverable count when dispatching it, and say plainly when it passes
roughly four distinct deliverables or when anything is added after
dispatch. Route discovered work to the pass that first leans on it, not the
pass that found it. Prefer turning a discovered artifact into a standing
input that later passes consume over making it a task now. Never add scope
to a task already in flight unless it would otherwise build against
something known wrong, and say so explicitly when doing it. Closing out and
refreshing beats pushing a long session further: both output quality and
token cost favor the clean boundary.

## Research basis (2026-08-21)

- Anthropic's multi-agent research system
  (https://www.anthropic.com/engineering/multi-agent-research-system): the
  lead runs on the frontier model, workers run cheaper, and the pattern
  still costs about 15x a single agent's tokens.
- When and how to use multi-agent systems
  (https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them):
  split work by information boundary, not by task count.
- Sub-agents docs (https://code.claude.com/docs/en/sub-agents): a fresh
  (non-fork) subagent returns only its final message to the caller.
- Workflows docs (https://code.claude.com/docs/en/workflows): intermediate
  results stay in script variables rather than the caller's context; the
  tool's cost warning is advisory, not a hard limit.
- Model config docs (https://code.claude.com/docs/en/model-config): `effort`
  is set per agent and is cheaper to tune than a model swap.
- GitHub issue 41143
  (https://github.com/anthropics/claude-code/issues/41143): `maxTurns` is
  documented but not reliably enforced.

## Fable 5.1 (noted 2026-09-04)

Fable 5.1 shipped 2026-09-01 (Mythos 5.1 alongside; no Opus or Sonnet
5.1). Same $10/$50 per MTok as Fable 5, with cache reads cut 75%. This
favors long conducting sessions, whose meters are dominated by
cache-read compounding. Geoff moved sessions to 5.1 on 2026-09-04.
Reviewer pins stay `claude-opus-5-5` and implementer aliases stay
`sonnet` (both still their tiers' heads); a dispatch without a model
now falls to `sonnet` through the settings `env` entry (decisions
below).

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
benchmark row is Anthropic's own table from the announcement. Effort
levels are not published, and the margin is effort-sensitive. Anthropic
estimates Fable 5.1 costs about 25% less than Fable 5 for typical
workloads and up to about 45% less for highly agentic work. One
independent per-task measurement points the other way. Artificial
Analysis measured $3.76 per Intelligence Index task at `max` effort
against Fable 5's $3.14, about 20% more, because 5.1 emits roughly 1.7
times the output tokens. The saving is effort-dependent, which is why
the effort rule keeps `high` as the standing level.

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
- Reviewer pins stay `claude-opus-5-5`: half the output price, fresh-context
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
the `claude-api` skill's `shared/model-migration.md` (Fable 5.1 sections).

## Opus 5.5 conducts execution (Geoff, 2026-09-22)

The 2026-08-21 "Fable conducts" rule above is narrowed to the phases that need Fable. Fable
runs the brainstorm, authors the plan, and takes the one adjudication an Opus verdict hedges
on. The executing session runs on `claude-opus-5-5` at effort `medium`. Why: during execution
the conductor consumes structured reports and rules on escalations, which is the workload
Anthropic's own guidance routes to Opus 5.5 by default, while every loop tick re-buys the
whole conversation, so the conductor's context is the largest single Fable spend a pass has;
Opus 5.5 is $4/$20 per MTok with a published meter, where Fable's Max metering is not
published (see "The pool-metering unknown"). Opus 5.5 also carries 1M context and the
documented long-run behavior the pass shape needs. Geoff confirmed this against his own
research on 2026-09-22; the first execution under it is retire-2b in cairn-cms, scored the
usual way plus a count of `fable` upshifts.

Two guards. Reviewers pin Opus 5.5 as well, so a conductor overruling a reviewer verdict
states why in STATUS and upshifts the decision to `fable` when the overruled finding is
correctness-critical. And a decision that needs more than Opus 5.5 gives it is one dispatch
to `fable`, never a session model switch; the session model changes only at a pass boundary,
from the STATUS resume prompt.

## Opus 5.5 drafts published docs pages (Geoff, 2026-09-22)

The docs page chain's drafter defaults to `claude-opus-5-5` (`drafterModel` in
`docs-page-chain.js`); the editor, grader, and fact read stay on Opus 5.5 in fresh contexts.
Evidence: draft docs pass A's Sonnet drafts escalated all three pages after two rounds and each
needed a conductor-directed third round, so a Sonnet draft cost more in Opus review rounds and
Fable attention than it saved. Agent-facing prose (facts bullets, HISTORY entries, stale-step
fixes on frozen pages, post-mortems) stays with the Sonnet implementer; it is gated, not
register-graded. Fable never drafts a page routinely; its docs role is the adjudication of a
page the chain escalates twice. First run under it: draft docs pass B; if its redraft rate does
not drop, revisit drafter-and-editor sharing one model.

## Interaction is front-loaded, never minimized (Geoff, 2026-09-04)

Until 2026-09-04 the pass-end score counted every question, approval, and
correction as an interaction point and called a question that did not change
the outcome a defect. Geoff retracted that framing as too blunt. The goal was
always interaction that is batched and, preferably, front-loaded. Extended
back-and-forth on requirements and design is wanted, and it is worth the time
to remove every ambiguity before a plan is approved.

The old rule carried the wrong incentive. A defect-per-question score pushed
the conductor toward guessing at planning time, the one place a wrong guess
costs a whole pass, while the questions it discouraged were the cheap ones.
The score now separates the phases. Planning misses count each ambiguity that
surfaced after approval and a planning question would have caught. Execution
sittings count each time Geoff was pulled in after approval, with one combined
checkpoint question counting once. Planning questions never count against the
score.

Cadence follows the same split. Before approval, ask one question at a time
by default, with a recommendation attached; a few tightly related questions
may share a message. After approval, judgment calls batch into one combined
question at a checkpoint, and only a genuine blocker or scope change stops the
pass early. CLAUDE.md carries the rule in "Conducting a pass" and "Process
proportionality"; the `geoff-works-autonomously` memory carries the standing
preference.
