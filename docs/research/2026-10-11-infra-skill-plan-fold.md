# Infra skill plan: fold record (2026-10-11)

Target: `docs/superpowers/plans/2026-10-11-infra-skill.md` at `4c3816e`. Review: the mechanics lens
alone (`2026-10-11-infra-skill-plan-review-mechanics.md`), per the approved design. No other lens
and no verification read ran. The planning session folded in place: the fold only applied the
`correctness` findings and dropped the `optional` ones, per design item 3.

None of the findings changes the approved design. Finding 4 edits one `pass-core` line the design
does not name (step 2). That clause applies design item 3 ("a design of a page or less needs no
separate spec"), so the fold reads it as the same consistency edit as reading 2, not a rewrite
beyond the named lines.

| # | Tag | Disposition |
|---|---|---|
| 1 | correctness | Folded. T3: a stage is guarded only when its command word is a guarded command, after `VAR=value` and `timeout <n>`; three read-only cases added as allowed tests. |
| 2 | correctness | Folded. T3: a regex pre-filter first, unparsable input exits 0, `\|&` counts as a pipe; tests for a two-line command, an apostrophe heredoc, and `\|&`. |
| 3 | correctness | Folded. T2: the budget counts `>` lines; the acceptance names how the edits fit it. |
| 4 | correctness | Folded. Reading 2 and T2 extend to step 2 with one clause; the diff acceptance now allows steps 1 to 4. |
| 5 | correctness | Folded. T4: a test where the `noreply@anthropic.com` trailer alone still warns. |
| 6 | correctness | Folded. T4: any git failure prints the skip line and exits 0; an orphan-base test. |
| 7 | correctness | Folded. "In full" became "as the research quotes it, `...` kept"; the Scope quotes in the plan and the launch prompt regain the elision. |
| 8 | correctness | Folded. "What goes live" names the pull, not the merge; the pull and `stow -R bin` run as one command. |
| 9 | correctness | Folded. T1's trigger runs copy `pass-core` and `dotfiles-pass` beside the skill under test. |
| 10 | optional | Dropped. The launch prompt is committed with this fold. |
| 11 | optional | Dropped. |
| 12 | optional | Dropped. |
| 13 | optional | Dropped. |
| 14 | optional | Dropped. |
| 15 | optional | Dropped. |

The folds of findings 1 and 2 add tests to T3, whose estimate rises from 45 to 55 minutes. The plan
now totals 255 task-minutes, under the 360 tripwire.

## Amendment 3a (after the fold)

Geoff amended the design with item 3a, the `plan-reviewer` agent (`fe26a9b`), after this fold. It
reached the planning session through the post-cutover sweep session, and the branch was merged in.
T2 builds the agent and the `spec-plan-review` dispatch, and T1 adds the agent to
`claude-tooling.md`'s lines. T2 rises from 35 to 50 minutes, and the plan totals 270 task-minutes,
under the 360 tripwire. The agent did not exist on this branch, so this plan's own review stayed
as the planning prompt set it.
