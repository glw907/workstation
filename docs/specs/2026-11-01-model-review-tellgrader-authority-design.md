# Settle how much weight tellgrader findings carry

## Brief

Three files in the cairn prose review give `tellgrader` findings three different weights. This
design makes the pipeline agree and needs one ruling from you: whether every finding blocks, or only
the ones the tool marks as gates. Approving it starts one small `runner` pass.

## Gap

All three files are on `main`, and all three sit outside what PR #184 changes.

| File | Rule |
|---|---|
| `register-check/SKILL.md:28-30`, Gate 1 | "treat its findings as advisory candidates for Gate 2, not automatic defects" |
| `cairn-register-editor.md:67-68`, Gate 2 of that same check | "Its findings are facts; carry them into your report without re-litigating them" |
| `prose-voice-reviewer.md:29-30` | "Its findings are facts; carry them into the report as Blockers" |

A draft can pass Gate 1 as advisory and then be graded on the same finding as fact in Gate 2.

`register-check`'s reason is also stale. It says the scanner's docs register "only approximates
cairn's own voice", but `cairn-register-editor` and `prose-voice-reviewer` both describe a
docs-register profile that resolves from the graded repo's opt-in.

## Evidence

- Claude Code memory: "if two instructions contradict each other, Claude may pick one arbitrarily"
  (<https://code.claude.com/docs/en/memory>).
- `git log`: `register-check` took its wording on 2026-09-01 and `cairn-register-editor` took its
  own on 2026-10-07, so the newer file is the agent. This dating comes from the full-tree audit.
- The agents' own text: exit 2 means a finding carries `"gate": true`, which marks a trailing-hinge
  run or an appositive stack. The tool already separates those findings from the rest.

## Proposed change

1. Replace `register-check:28-30` with: "Its findings are facts that Gate 2 carries without
   re-litigating. Gate 2 spends its judgment on what the scanner cannot see."
2. Keep the agents' "facts" line, and change `prose-voice-reviewer:30` so a finding with
   `"gate": true` is a Blocker and any other finding is a Warning.

Step 2 is the ruling I need. I recommend it because the tool's gate flag is the only line it has
drawn for itself, and an ungated finding such as a soft-slop count can be defensible in its register.
The alternative keeps every finding a Blocker, which matches the agent as written and is stricter.

The audit also flagged that `prose-voice-reviewer` and `cairn-register-editor` both claim a published
cairn page. PR #184's audit weighed the same overlap and kept it, since their domains differ, so
this design leaves it alone.

This is `runner` by `dotfiles-pass`.

## Audit findings taken

From the full-tree report: 5, and the "Overlapping reviewers" flag, which this design closes with no
change.
