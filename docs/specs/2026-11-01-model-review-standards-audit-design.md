# Audit the standards plugin every month

## Brief

The monthly audit stopped reading most of the workstation's skills when they moved to the
`standards` plugin on 2026-10-31. PR #184's audit read 14 skills and 3 agents, while the plugin's 29
skills and 9 agents got a grep pass only. This design adds the plugin to the monthly audit and lands
the eight stale items that a pre-cutover audit and this review found there. Approving it starts one
`ordinary` pass in this repo and one `runner` pass in `glw907/standards`.

## Gap

`/doctor prompt-audit` covers `.claude/` and `~/.claude/`, and it treats a plugin as report-only.
PR #184's report says of the plugins, "I checked these two sets by grep signals only, not by reading
each file". Commit `322d136` moved those skills and agents, so the coverage fell without anyone
choosing it.

The second November run started from `e5308fb`, before that commit, so its audit read everything.
Its report is `docs/model-review/2026-11-01-prompt-audit-full-tree.md`. Each finding below was
retested against `glw907/standards` at `af14ad5`.

## Evidence

- Claude Code memory: the audit covers "the rules, skills, commands, subagents, and output styles
  under `.claude/` and `~/.claude/`", and "To audit one file or directory instead, pass its path"
  (<https://code.claude.com/docs/en/memory>).
- Best practices, on caps: "Older models sometimes needed the emphasis. Current ones follow a plainly
  worded line, and piling on emphasis mostly makes Claude over-apply the rule"
  (<https://code.claude.com/docs/en/best-practices>). The 2026-09-28 sweep waived a trimming pass on
  an older, softer sentence that the page no longer carries.
- The same page no longer contains "Chasing every finding", which `spec-plan-review:17` quotes. Its
  closest text is now "If you fix every finding, you end up with extra abstraction layers and tests
  for cases that can't happen."

## Proposed change

**Keep it from recurring (this repo).**

1. In `bin/.local/bin/model-review-notify`, pull `~/Projects/standards`, then run
   `claude -p --model opus --effort medium "/doctor prompt-audit plugins/standards"` from it into a
   second report. Pass both paths to the session. Probe the path form first, since the docs don't
   say how a path treats a plugin's files.
2. In `docs/model-review/prompt.txt`, make step 1 read both reports, and say that a design for the
   plugin lands in `glw907/standards`.

**Land the findings (`glw907/standards`).** Every edit stays portable, as its README requires.

| Audit # | Location | Action |
|---|---|---|
| 2 | `tui-visual-verify:46-48, 53`; `bin/kitty-headless-shot:13` | `-c CMD` is required, since the script exits 2 without it. Show it as required |
| 22 | `tui-visual-verify:63` onward | Move the "forced by a failure" bullets into the script header |
| 15 | `go-conventions:35, 363` | Keep one copy of the "most effective filter" rule, and of the stdlib-exemplar rule |
| 16 | `bubbletea-design:245, 252` | Drop "Never skip verification" and the "Red Flags: Stop" table, and carry 120 columns into the checklist |
| 17 | `elm-conventions:34` | Drop the "now" that compares against a rule the reader never saw |
| 18 | `visual-verifier:19, 29`, `visual-fidelity:45`, `design-refinement:35` and the audit's other lines | Sentence case. Grade tokens such as MATCHED stay in caps |
| 20 | `plan-reviewer:14-18` | Remove the paragraph that justifies the agent's existence |
| new | `spec-plan-review:16-17` | Replace the retired quote with the current sentence, and correct "may follow" to the page's "might follow" |

Finding 18 is the largest and is judgment-free. The rest are small. Findings 1, 7, 19, and 21 no
longer reproduce at `af14ad5`, and the low-confidence list waits for next month's first full audit.

One flag needs your ruling: `go-ship:14` says "No separate review step", which skips the close
review. The skill only runs when invoked, so I'd add a clause saying that invoking it is the choice
to skip.

This is `ordinary` here and `runner` in `glw907/standards`. The plugin's evals for `go-conventions`
run in that pass.

## Audit findings taken

From the full-tree report: 2, 15, 16, 17, 18, 20, and 22, plus the `go-ship` flag and the low-confidence
list. The rest are in the PR body's table.
