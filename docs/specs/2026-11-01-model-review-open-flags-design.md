# Rule on the open prompt-audit flags

## Brief

The October and November audits left flags that need a ruling, a repo outside this one, or an eval.
The October report says each monthly review starts from this list. Two have closed, and this design
gives a recommendation for each one left, so one approval settles them. Approving it files the
follow-ups in `BACKLOG.md`. It starts no pass.

## Closed since October

- **Engine passes and releases.** `cairn-pass` no longer says "never release", and `engine-consult`
  no longer invokes `cairn-release`.
- **Incident narratives in `pass-core`.** The
  [audit fixes design](2026-11-01-model-review-audit-fixes-design.md) takes them. The same narratives
  in other files stay in the low-confidence list.

## Rulings wanted

| Flag | Recommendation |
|---|---|
| `mail-tend:61, 88` against `approval-packet:29`: a mail move or rule design goes to chat, and packets forbid that | Name mail moves as a standing chat exception in `approval-packet`. They're small and reversible. |
| `approval-packet:38`: "at most three asks" can't hold when four PRs carry forced asks | Keep the cap and let forced asks exceed it. |
| `visual-verifier:30` flags a CTA pair under 3:1, and `daisyui-a11y-reviewer:72` uses 4.5:1 for text | Tighten the verifier to 4.5:1, WCAG's floor for button labels. The agent lives in `glw907/standards`. |
| `prose-voice-reviewer:50-51` flags a docs-tier em dash, and the output style allows Google's form | Narrow the flag to overuse or spaced dashes. |
| `site-implementer:15` never pushes, yet `:70` merges a cairn-cms docs branch by PR | The dispatching session pushes and merges. State that at line 70. |
| `pass-core:224`, `cairn-pass:20`, and `site-pass:28` give the `cairn-run-gate '<string>'` form that `dotfiles-pass:17` says the worktree guard refuses | Add a no-argument `gate.sh` wrapper to each repo's adapter when it next changes. This session's guard refused compound commands too, so the risk is real in a `-w` session. |
| `spec-plan-review:55` sends review records to `docs/research/`, and `pass-core` sends cross-repo research to `initiatives/<id>/` | Keep repo-scoped records in `docs/research/` and add a clause for cross-repo work. |
| `CLAUDE.md` "prefer dispatching reads" against best practices, which retires "Use subagents to protect your context window" because each subagent "costs extra tokens" (<https://code.claude.com/docs/en/best-practices>) | Keep the rule, since it's about cache re-reads, but narrow it to reads across several files. New this month. |

## No ruling needed

- **`output-styles/writing-voice.md:64-65` and `:80-81`.** The file is vendored, so file the cut and
  the re-test in `glw907/survey`.
- **Opus 5 quotes at `pass-core:52-56` and `claude-infra:42-46`.** Keep them. The Opus 5.5 guide says
  the Opus 5 patterns "remain a reasonable starting point"
  (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5>),
  and removal needs an eval. The migration guide's advice to "Re-evaluate model-specific prompt
  instructions" is general.
- **`pass-core:39`, `engine-consult:137-141`, `dotfiles-pass:7, 32`, and October's low-confidence
  list.** Leave them until a pass touches those lines.
- **Monthly checklist.** Item 2 names the retired `model-economy.md`, and item 7's HISTORY entry and
  project memory no longer exist. Add one line to the prompt: item 2 reads
  `fable-post-cutoff-system.md`, and item 7 is skipped.

## Audit findings taken

The November flags `mail-tend`, `pass-core:52-56`, `writing-voice:64-65`, `writing-voice:80-81`,
`pass-core:39`, `engine-consult:137-141`, and `dotfiles-pass:7, 32`. The November flag on
`site-implementer:4, 44` goes to its own design. All open October flags are carried here.
