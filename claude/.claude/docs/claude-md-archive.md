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

## Visual fidelity: the full rule set

Moved out of CLAUDE.md 2026-09-27 (CLAUDE.md keeps a two-line pointer; the
`visual-fidelity` skill is the method). Any UI work that must match an existing reference (a
rebuild, a theme port, a migration) invokes the `visual-fidelity` skill at the start and gates
on the `visual-verifier` agent. Core rules even without the skill: reference screenshots before
any plan, never from a verbal description; the context that built the UI never grades it;
nothing deploys to production without a full-page render read in the main loop; user-facing
sites get Geoff's before/after.

## Cloudflare / Wrangler

Trimmed 2026-09-27: the wrangler command cheat sheet (`npx wrangler deploy` / `dev` / `secret
put NAME` / `tail`) left CLAUDE.md as general knowledge. Token scopes and the account id live
in `cloudflare-estate-inventory.md`.

## Conducting a pass: model-selection detail

Moved 2026-09-27 to `model-economy.md`'s "Current state" section, which carries the seat table
(model and effort per seat), the `xhigh`-then-`max`-then-`fable` escalation, reviewer overrules,
the `CLAUDE_CODE_SUBAGENT_MODEL` fallback, `/effort` persistence, and the Fable allowance cap.
The old CLAUDE.md line "reviewers, plan authorship, adjudication, and research at `high`" was
superseded by that doc's reviewer effort `medium` (Anthropic's Opus 5.5 guidance), security
review excepted at `high`.
