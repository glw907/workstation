# Set a default effort for subagents

## Brief

The workstation sets a default model for subagents but no default effort, so a dispatch that names
no effort inherits the session's level. Claude Code 2.1.316 added a variable that closes this. This
design sets it to `medium`, clears one saved level the review checklist counts as drift, and refiles
an effort sweep that fell out of the backlog. Approving it starts one small `runner` pass.

## Gap

`CLAUDE.md` says "Every dispatch names a model and an effort", and `pass-core` "Models" sets
subagents at `medium`. Both are prompt rules. `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` enforces the model
half in `settings.json`, and nothing enforces the effort half. A missed effort from a planner at
`high` or an adjudication at `max` runs the subagent at that level.

The live `~/.claude/settings.json` also saves `effortLevel: medium` under `claude-opus-5-5`. That
matches Claude Code's default for the model, so it has no effect today. It would outrank a changed
default, and the checklist treats a saved level as drift.

The 2026-09-28 sweep filed an effort sweep to `ROADMAP.md`. The workstation's ROADMAP was later
retired, and `BACKLOG.md` doesn't carry the item.

## Evidence

- Changelog 2.1.316: "Added `CLAUDE_CODE_SUBAGENT_EFFORT` to set the effort level subagents run at
  when nothing else names one, instead of inheriting the session's"
  (<https://code.claude.com/docs/en/changelog>). The env-vars page doesn't list it yet
  (<https://code.claude.com/docs/en/env-vars>), so the pass probes it first.
- Claude Code effort order: settings outrank "the model's default effort", and Opus 5.5, Sonnet 5.5,
  and Haiku 5.5 default to `medium` (<https://code.claude.com/docs/en/model-config>).
- Effort page, on Opus 5.5: "Run an effort sweep on your own evals rather than carrying settings
  over from an earlier model". The Sonnet 5.5 entry asks for the same
  (<https://platform.claude.com/docs/en/build-with-claude/effort>).

## Proposed change

1. Probe: from a session at `high`, dispatch one subagent with no effort and one with an explicit
   effort, with the variable set. Read each level from the session transcript, which records request
   parameters since 2.1.300. Stop the pass if the variable overrides the explicit effort.
2. Add `"CLAUDE_CODE_SUBAGENT_EFFORT": "medium"` to the `env` block of
   `claude/.claude/settings.json`, then run `claude-tooling-sync apply`.
3. Clear the saved level with `/effort auto` on Opus 5.5. The `autoCompactWindow` beside it stays.
4. File the effort sweep in `BACKLOG.md`, noting it needs an eval this machine can't yet run.

Dispatches that name an effort keep it, and frontmatter keeps winning. This is `runner`.

## Audit findings taken

None. This came from the changelog and checklist item 3.
