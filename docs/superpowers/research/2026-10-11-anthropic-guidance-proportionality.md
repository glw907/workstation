# Anthropic guidance on proportionality and infrastructure changes (2026-10-11)

An Opus research agent fetched each page on 2026-10-11 and quoted it verbatim, for the conducting
session (`c747c352`). It asked why the review desk design was over-engineered, and which of the
proposed process rules Anthropic's guidance supports. The code.claude.com best-practices page was
modified 2026-10-06. "Building effective agents" was published 2024-12-19 and modified 2026-08-10.

## Over-engineering and scope

- Prompting best practices, "Overeagerness"
  (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>):
  "Claude Opus 4.5 and Claude Opus 4.6 have a tendency to overengineer by creating extra files,
  adding unnecessary abstractions, or building in flexibility that wasn't requested." The page's
  sample prompt: "Avoid over-engineering. Only make changes that are directly requested or clearly
  necessary. Keep solutions simple and focused: - Scope: Don't add features, refactor code, or make
  "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple
  feature doesn't need extra configurability. ... - Defensive coding: Don't add error handling,
  fallbacks, or validation for scenarios that can't happen. Trust internal code and framework
  guarantees. Only validate at system boundaries (user input, external APIs). - Abstractions: Don't
  create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical
  future requirements. The right amount of complexity is the minimum needed for the current task."
- Prompting Claude Opus 5
  (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>;
  the Opus 5.5 page says these patterns "remain a reasonable starting point"): "Claude Opus 5 can
  also expand the scope of a task, adding steps that weren't requested or applying its own judgment
  about what the task should be." Sample prompt: "Deliver what was asked, at the scope intended.
  Make routine judgment calls yourself, and check in only when different readings of the request
  would lead to materially different work. If the request seems mistaken or a better approach
  exists, say so in a sentence and continue with the task as asked rather than quietly narrowing,
  widening, or transforming it. Finish the whole task, and stop short of actions that are clearly
  beyond what was asked." On verification: instructions like these "cause over-verification on
  Claude Opus 5", and "do not use subagents to verify or double-check your own work."
- Prompting Claude Sonnet 5.5
  (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5>):
  "Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would
  help, mention it at the end instead of doing it."
- Building effective agents (<https://www.anthropic.com/engineering/building-effective-agents>):
  "we recommend finding the simplest solution possible, and only increasing complexity when needed";
  "you should consider adding complexity only when it demonstrably improves outcomes."

## Planning and review

- Best practices for Claude Code (<https://code.claude.com/docs/en/best-practices>): "Plan mode is
  useful, but also adds overhead. ... If you could describe the diff in one sentence, skip the plan."
  Specs should "state what is out of scope, and end with an end-to-end verification step". On
  review: "A reviewer prompted to find gaps will usually report some, even when the work is sound
  ... Chasing every finding leads to over-engineering: extra abstraction layers, defensive code, and
  tests for cases that can't happen. Tell the reviewer to flag only gaps that affect correctness or
  the stated requirements, and treat the rest as optional."
- Opus 5 page: if a review prompt says "only report high-severity issues" the model "may follow that
  instruction literally and report less; ask it to report everything and filter in a separate pass
  instead."

## Hooks, CLAUDE.md, and skills

- Extend Claude Code (<https://code.claude.com/docs/en/features-overview>): "An instruction like
  "never edit `.env`" in CLAUDE.md or a skill is a request, not a guarantee. A `PreToolUse` hook that
  blocks the edit is enforcement. If a rule must hold every time, make it a hook rather than a prompt
  instruction." "Use a hook when the action must happen the same way every time and doesn't need
  Claude to think." "Put it in a skill if it's reference material Claude needs sometimes".
- Skills (<https://code.claude.com/docs/en/skills>): "Create a skill when you keep pasting the same
  instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has
  grown into a procedure rather than a fact." "Seeing a skill trigger tells you Claude found it, not
  that it did what you intended." "Keep `SKILL.md` under 500 lines." "Every skill in the skill
  listing adds to your context on every turn". `/doctor`, `/doctor prompt-audit` (memory page,
  v2.1.283+), and `/skill-doctor` audit instructions and skills.
- Memory (<https://code.claude.com/docs/en/memory>): "target under 200 lines per CLAUDE.md file."
- Hooks (<https://code.claude.com/docs/en/hooks>): "Because the `if` filter is best-effort, use the
  permission system rather than a hook to enforce a hard allow or deny." The hooks guide documents a
  `PreToolUse` hook on Bash that "exits 2 to deny when the command contains `rm -rf`".
- Worktrees (<https://code.claude.com/docs/en/worktrees>): Claude Code "blocks a Bash or Monitor
  command when it can't verify from the command text that any git the command runs stays inside the
  worktree ... You can't turn this check off."

## Not found

No Anthropic page covers plan-versus-design estimates or their calibration, risk classes, or a pipe
into `tail` masking a command's exit code.

## Verdicts

| Proposal | Verdict |
|---|---|
| Scope traced to a stated need, extras listed as "later" | Supported; paste the sample prompts verbatim |
| Risk class from the path map, raised only by owner ruling | Partly supported ("say so in a sentence") |
| Estimate tripwire at 2x the design | Local invention, cheap; calibration unsupported |
| Correctness-only review findings | Supported, as "flag only gaps that affect correctness or the stated requirements"; filter at the fold |
| No `tail` or `head` pipe on a background gate or watch | Supported as a hook; the trap itself is undocumented |
| Check Anthropic guidance before changing infrastructure | Supported; a skill step plus a warning, not a blocking hook |
| An infrastructure-change skill | Build it narrowly, as a replacement for CLAUDE.md and `claude-tooling.md` text |
| PR-in-browser; pull after merge; `scripts/gate.sh` | Neutral; supported; legitimate under the documented worktree guard |
| Three lenses, a fold, and a verification read on every runner plan | Likely the "separate verification steps" the Opus 5 page says to remove; scale to design size |
