# Complete the pricing table

## Brief

The workstation's pricing table leaves three current rates blank and links a renamed support page.
This design fills them in. The seat question stays closed: the new rates keep Sonnet at half Opus's
price on every token class, so nothing about the seats changes. Approving it starts one `ordinary`
change.

## Gap

The monthly checklist's pricing table moved to `claude/.claude/docs/fable-post-cutoff-system.md`
(lines 98-109) when `model-economy.md` was folded. These entries have gone stale:

- Opus 5.5 cache read reads "not recorded here".
- Sonnet 5.5 and Haiku 5.5 batch read "not recorded here".
- The Fable plan link uses the old slug, and the allowance line names only Max.

## Evidence

- Pricing page: Opus 5.5 cache read is $0.20 per MTok. Batch is $1 / $5 on Sonnet 5.5, and $0.05 /
  $0.25 on Haiku 5.5 up to 100k
  (<https://platform.claude.com/docs/en/about-claude/pricing>).
- Claude Fable models on your plan: on Max and Ultra, Fable "can use up to half" of the weekly limit
  (<https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan>). The allowance
  itself is unchanged.

The checklist says a cache-read change re-opens the seat question. Opus 5.5 at $0.20 and Sonnet 5.5
at $0.10 hold the 2:1 ratio of their base prices, so it doesn't.

## Proposed change

1. Fill the three cells from the pricing page.
2. Replace the plan link, name Max and Ultra, and date the check 2026-11-01.

Checklist item 2 names the retired `model-economy.md`, so the
[open flags design](2026-11-01-model-review-open-flags-design.md) moves that item to this file.

This is `ordinary`, since the doc isn't on the `runner` path map.

## Audit findings taken

None. This came from checklist item 2.
