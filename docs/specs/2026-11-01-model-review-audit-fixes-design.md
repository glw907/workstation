# Apply the November prompt audit's fixes

## Brief

Anthropic's `/doctor prompt-audit` found 15 stale facts, conflicts, and leftover incident history
in the workstation's skills and agents. This design lands its proposed diff with two amendments.
Approving it starts one `runner` pass and changes no behavior except the two rules named below.

## Gap

The audit's three main findings are these:

- `pass-core` carries about 18 incident tails that no session can act on.
- `site-implementer` tells a subagent to ask questions it has no channel to ask.
- `site-pass` and `claude-infra` have gone stale against newer rules.

## Evidence

The report and the applyable diff are kept in `docs/model-review/2026-11-01-prompt-audit.md` and
`docs/model-review/2026-11-01-proposed.diff`. The launcher deletes the report and `/tmp` clears on a
reboot, so these copies are the record. `git apply --check -p1` passed on this branch, and the
commit ids the audit cites (`cf4c26b`, `322d136`) resolve to the changes it describes.

- Skill authoring best practices: "Don't include information that will become outdated"
  (<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>).
- Claude Code memory: "if two instructions contradict each other, Claude may pick one arbitrarily"
  (<https://code.claude.com/docs/en/memory>).

## Proposed change

1. Apply `docs/model-review/2026-11-01-proposed.diff` from the repo root with `git apply -p1`.
2. Amend the `site-implementer` DaisyUI hunk to match the
   [skill reach design](2026-11-01-model-review-site-implementer-skill-design.md), so the
   corrected sentence names something the agent can do.
3. Run the trigger check on `log-project`, since its description hunk changes a trigger: three
   should-trigger and two should-not prompts in fresh `claude -p` sessions, before and after. The
   rule comes from the 2026-09-28 sweep and <https://code.claude.com/docs/en/skills>.

Two hunks change a rule, and both need your read in the packet. The `site-implementer` step 1 hunk
replaces a clarifying question with `NEEDS_CONTEXT`. The `claude-infra` hunk records the "Direct
changes" exception in the skill that governs these edits. The `Geoff, <date>` ruling tags stay
everywhere.

This is `runner` by `dotfiles-pass`, because it edits skills and agents. It isn't a direct change,
since two hunks change a step or a trigger.

## Audit findings taken

All 15 rows of the audit's High and Medium tables:

- `site-pass:44`
- `claude-infra:48`
- `site-implementer:30` and `:44-45`
- `pass-core` lines 65-330, 344-389, 309-310, and 408
- `approval-packet:132`
- `dotfiles-pass:50`
- `log-project:4-9` and `:18-19`
- `engine-consult:123` and `:132-135`
- `vps-conventions:79-82, 106`
