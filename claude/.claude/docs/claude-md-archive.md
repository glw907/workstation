# CLAUDE.md archive

Narrative and incident detail trimmed out of the global `CLAUDE.md` to keep it under its
`claude-context-budget` token budget. Each entry backs one rule that stayed in `CLAUDE.md`,
tagged there with a short `(Geoff, YYYY-MM-DD)` date; this file holds the story, not a new rule.

## Search before you spelunk

Examples of the framework- or library-specific symptoms this covers: a form that will not
submit, a build that fails in one runtime, an API rejecting a shaped request. Proven twice,
2026-07-13: a documented quirk or GitHub issue named the cause in one shot that hands-on probing
reached only after many expensive main-model turns. Both budgets, tokens and attended time,
favor the search.

## One executor per worktree

Born 2026-07-14: two workflows raced one worktree, producing roughly 1.2M duplicated tokens.

## Secrets: check the stores before claiming one is missing

Born 2026-07-07, twice: both were false "you still owe me X" reports, where the credential was
already sitting in a store Claude had not checked.

## Visual fidelity

Born from two same-day production misses, where UI shipped to production without a full-page
render read.

## Project ledgers: the STATUS line-cap history

`site-pass` has always carried the STATUS.md line cap, and every repo blew past it anyway because
"prune" had no destination: ecxc-ski reached 173 lines, 907-life 236, cairn-cms 540.
