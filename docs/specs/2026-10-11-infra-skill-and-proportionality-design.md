# Infrastructure skill and proportionality rules (design)

**Status:** awaiting Geoff's approval, brought 2026-10-11 by the conducting session (`c747c352`).
Evidence: `docs/superpowers/research/2026-10-11-anthropic-guidance-proportionality.md` (quotes and
verdicts, all fetched that day). Cause: the review desk design was over-engineered (about 12 hours
planned for a one-page local app), and three changes landed the same day without a guidance check.

## Outcome

A session that changes local Claude Code infrastructure checks Anthropic's guidance first and puts
each rule in its strongest home. Designs and plans carry Anthropic's own anti-over-engineering
language, and review effort scales with a design's size. The always-loaded instruction text shrinks
rather than grows.

## What it builds

Each item names the need it traces to.

1. **A `claude-infra` skill** (about 60 lines). It traces to Geoff's rule: "we should be checking
   anthropic guidance before altering local infastructure." Its procedure:
   - cite the Anthropic page the change follows, and prefer a built-in;
   - choose the strongest home: hook, then skill or agent, then CLAUDE.md;
   - keep one home per rule, with its manifest;
   - trace scope to a stated need, using the sample prompts below verbatim;
   - land the change through a PR that cites the guidance;
   - point to `/doctor prompt-audit`, `/skill-doctor`, and Anthropic's skill-creator rather than
     restating them.

   It replaces text rather than adding to it. Global CLAUDE.md's "A rule lives where it executes"
   section shrinks to a one-line pointer, and `claude-tooling.md`'s "Rules" section moves into the
   skill. Its description uses the research's suggested trigger text.
2. **`pass-core` edits:**
   - **Design step:** Anthropic's "Avoid over-engineering ..." sample prompt and the Opus 5 "Deliver
     what was asked, at the scope intended ..." paragraph go in verbatim. Every planning dispatch
     prompt carries them. Extras are listed as "later" and never built.
   - **Risk class:** it comes from the adapter's path map. Raising it takes Geoff's ruling, stated
     in the design in one sentence.
   - **Estimate tripwire:** a plan over twice its design's estimate goes back to Geoff with the
     reason before launch.
3. **`spec-plan-review` edits:**
   - Every lens reports everything and tags each finding as affecting correctness or a stated
     requirement, or as optional. The fold drops the optional ones, in Anthropic's words: "flag only
     gaps that affect correctness or the stated requirements, and treat the rest as optional."
   - Depth: a design of a page or less needs no separate spec. A plan gets the mechanics lens only.
     The three lenses and the verification read are kept for `auth-data` and `live-account` passes.
     This follows the Opus 5 guidance against separate verification steps.
3a. **A `plan-reviewer` agent** (Geoff, 2026-10-11 amendment, "as long as we're following Anthropic
   best practice"). It is an agent definition under `claude/.claude/agents/`, about 40 lines:
   read-only tools, `claude-opus-5-5` at `medium`, and the mechanics lens prompt with the
   correctness-or-optional tagging. `spec-plan-review` stays the procedure and dispatches it, in
   place of the lens prompt each planner retypes. Guidance: "Define a custom subagent when you keep
   spawning the same kind of worker with the same instructions"
   (<https://code.claude.com/docs/en/sub-agents>). A subagent is "an isolated worker with its own
   context", and "a quick, focused worker: research a question, verify a claim, review a file"; and
   "A skill spawns subagents" (<https://code.claude.com/docs/en/features-overview>). The agent adds no
   review: per the Opus 5 guidance against verification subagents, it replaces the prompt for the
   single review this design keeps. Its description stays short, since every agent description
   takes up context.
4. **A `tail` guard:** a check in the existing `PreToolUse` Bash hook chain. It denies (exit 2) a
   gate or CI-watch command (`cairn-run-gate`, `ci-green`, `scripts/check.sh`, `scripts/gate.sh`,
   `npm test`, `npm run check`, `gh pr checks`) piped into `tail` or `head`, and tells the session to
   run it bare or redirect it to a file. The match happens inside the script, since the hook `if`
   filter is best-effort. This traces to three incidents, the latest being the escape in engine
   pass B.
5. **A guidance warning:** `scripts/check.sh` warns, without failing, when the branch's commits
   touch `claude/` skills, agents, hooks, settings, or CLAUDE.md and cite no `anthropic.com`,
   `claude.com`, or `platform.claude.com` URL. It becomes a hard block only if the warning is
   skipped twice.

## Conductor restart (Geoff, 2026-10-11)

When this pass merges, the conducting session hands over and ends, so a fresh conductor runs under
the new rules. It does five things:

1. Pulls `~/.dotfiles`.
2. Writes the conductor's state into `docs/STATUS.md`: work in flight with session names and
   watchers, the next steps in order, decisions pending with Geoff, and post-merge steps owed (for
   example, dubplate's memory prune).
3. Commits a conductor launch prompt beside it.
4. Restores the stowed `settings.json` from Geoff's one-discussion `/effort high`.
5. Stops its loop.

Geoff then starts the new conductor with the STATUS launch line.

## Later, not built here

Estimate calibration from recorded actuals, effort per role, subagent spawn limits, and time budgets
for multi-agent runs. The monthly alignment review (sweep 2, item F) can raise any of these with
evidence.

## Out of scope

Any change to other repos, and any rewrite of `pass-core` beyond the lines named above.

## End-to-end check

- `bash scripts/gate.sh` prints `gate exit: 0`.
- The hook denies `cairn-run-gate 'bash scripts/check.sh' | tail -5`, and allows the bare command
  and a redirect to a file (fixture test).
- In fresh `claude -p` sessions, the skill triggers on three realistic prompts ("add a rule that
  ...", "make a hook for ...", "change the pass process so ...") and not on two unrelated ones.
- Global CLAUDE.md is shorter than its 199 lines, and `pass-core` grows by no more than the quoted
  prompts.

## Risk and size

Class `runner` (skills, settings, scripts), from the path map. About 3 hours of tasks, probably
less in practice. By Geoff's approval of this design, this pass uses the new review depth itself: a
plan with the mechanics lens only.
