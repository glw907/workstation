# Fable as the standing conductor

Design for moving the coding-project conductor seat from "Fable plans, a fresh Opus 5
session executes" to "Fable conducts plan through execution in one session, kept thin."
Supersedes the 2026-07-26 ratification recorded in `model-economy.md`.

## Why

Four drivers, all confirmed by Geoff on 2026-08-21. Opus 5 execution sessions made poorer
dispatch and triage calls than the plan quality deserved. The plan-approval handoff (fresh
session, resume prompt, re-reading artifacts) cost attention and tokens. Passes should run
longer without Geoff present. The Fable allowance has not been the constraint in practice.

The allowance fact, verified against the help center on 2026-08-21: on Max, Fable 5 draws
from the same weekly pool as every other model and may consume up to 50% of it; past that,
usage credits or a model switch. The help page states no per-model weighting, and none
could be verified. The binding constraint is therefore the 50% cap on the weekly pool, and
the design treats Fable context size, not API price, as the thing to minimize.

What the research settled (sources in the plan): Anthropic's own production pattern runs the
frontier model as lead with cheaper workers; the lead must never absorb what a worker read.
A fresh (non-fork) subagent returns only its final message. A Workflow keeps intermediate
results in script variables. `effort` on agent frontmatter is cheaper than a model swap.
`maxTurns` is documented but not reliably enforced; the Workflow cost warning is advisory.

## The shape

**One session per pass, Fable conducting.** Brainstorm, spec, plan, approval, execution,
pass-end, post-mortem, all in one session. The plan-approval gate stays the single human
gate; it is no longer a model boundary.

**The conductor is thin.** Fable never reads a source file, a diff, a test log, or a gate
transcript during execution. It consumes structured reports from agents and makes only the
decisions that need judgment: accept, re-dispatch with a correction, split, upshift, stop.
The self-check from the old doctrine inverts: a Fable conductor caught reading diffs or
grinding edits inline flags itself and dispatches.

**The per-task chain.** Each plan task runs implementer, then diff reviewer, then gate.

- The implementer (repo's Sonnet-pinned agent) returns a fixed shape: files touched, gate
  result, decisions the plan did not cover, anything it could not do.
- A new global agent `diff-reviewer` (pinned `claude-opus-5`, effort high, read-only plus
  `git diff`) takes the task's acceptance criteria and the implementer's report, reads the
  diff, and returns: verdict (`accept`, `fix`, `escalate`), blocking findings with
  `file:line`, non-blocking findings, and a one-paragraph summary for the conductor. It does
  not replace the domain reviewers (svelte, a11y, security, workers); those still run at
  pass end. It replaces the conductor's own per-dispatch diff read.
- On `fix`, the implementer gets one re-dispatch carrying the blocking findings. A second
  `fix` verdict goes to the conductor as a decision.
- The gate is the repo's full gate, run by the implementer and confirmed by the reviewer's
  report; the conductor never runs it.

**Two dispatch modes, chosen by pass size.** Below six tasks, the conductor dispatches the
chain per task with the Agent tool. At six or more, or whenever the plan marks tasks as
independent, the conductor runs `~/.claude/workflows/pass-execute.js`, which pipelines the
chain over the task list and returns the per-task reports in one value. The script honors a
token ceiling through the `+Nk` directive and logs what it drops. The Workflow opt-in rule
in CLAUDE.md gets one carve-out: a pass plan that names the workflow mode is the opt-in.

**Budget.** Every pass plan header carries a token ceiling and a checkpoint interval (default
every four tasks). The conductor reports spend against the ceiling at each checkpoint and
in the pass-end score. Near the ceiling (80%), it finishes the current task, writes STATUS,
and asks one combined question rather than continuing.

**Checkpoints and compaction.** At each checkpoint, at any task or pass split, and before
any question to Geoff, the conductor writes STATUS (task ledger, decisions taken, spend,
next task). The session then continues and relies on auto-compaction. A "Compact
instructions" block in CLAUDE.md names what compaction preserves: plan path, task ledger,
open decisions, ceiling and spend, the last reviewer verdict. The runaway guard for
workflows applies unchanged.

**Model pins, unchanged where already right.** Sonnet implements, `claude-opus-5` reviews,
Haiku explores, every dispatch names a model and an effort. Upshift rules stay: `opus` for
novel correctness-critical logic the plan does not specify, `fable` only when an Opus
verdict hedges on something that matters.

## What changes, by file

Global, in `~/.dotfiles/claude/.claude/` (stowed to `~/.claude/`):

- `CLAUDE.md`: rewrite "Model economy" and "Plan execution" as one shorter section
  ("Conducting a pass"); compress "Pass sizing" to its rule and the split-count practice,
  moving the poplar 1b narrative to `model-economy.md`; add the Compact instructions block;
  add the workflow carve-out to the Multi-agent section. Net size must land under the
  6,000-token budget `claude-context-budget` enforces (the file is at ~6,029 today).
- `docs/model-economy.md`: keep pricing; replace the "Opus 5 narrowed Fable's seat" and
  self-check sections with the new seat policy, the allowance fact with its verification
  date, and the moved pass-sizing narrative.
- `docs/fable-post-cutoff-system.md`: header note marking the seat policy superseded, with
  a pointer; the overflow mechanics (batch desk, modes) stay as written.
- `agents/diff-reviewer.md`: new.
- `workflows/pass-execute.js`: new, with a `meta` block, schemas for the implementer and
  reviewer returns, and the retry rule above.
- `skills/cairn-pass/SKILL.md` and `skills/site-pass/SKILL.md`: remove the fresh-Opus
  handoff; describe the chain, the two dispatch modes, the checkpoint ritual, and the
  plan-header fields. Pass-end rituals are unchanged.

Projects:

- `cairn-cms/CLAUDE.md` lines 73 to 84: the subagent-models paragraph drops the Fable-ends-
  at-approval sentence. `cairn-cms/docs/STATUS.md` line 43: "fresh Opus 5 session" becomes
  "this session or a fresh Fable session".
- `poplar/CLAUDE.md`: add a short conductor paragraph pointing at the global rule and the
  poplar implementer and reviewer agents.
- Memory: add a `feedback` memory recording the seat change and its date so a cold session
  does not recall the old split.

## Out of scope

Domain reviewer agents, pass-end rituals, the release skills, the `ship` skill, and the
Workflow runaway guard are unchanged. No settings.json change is needed: `model: fable` is
already the default and `CLAUDE_CODE_SUBAGENT_MODEL=inherit` already lets frontmatter win.

## Acceptance

- `claude-context-budget ~/.claude/CLAUDE.md` exits 0.
- `grep -rn "fresh Opus" ~/.claude/CLAUDE.md ~/.claude/skills ~/.claude/docs
  ~/Projects/cairn-cms/CLAUDE.md ~/Projects/cairn-cms/docs/STATUS.md` returns nothing.
- `~/.claude/agents/diff-reviewer.md` parses (frontmatter has name, description, tools,
  model, effort).
- `pass-execute.js` has a pure-literal `meta` and no `Date.now`/`Math.random`.
- Vale passes on every edited prose file.
- dotfiles committed; cairn-cms and poplar committed separately.
