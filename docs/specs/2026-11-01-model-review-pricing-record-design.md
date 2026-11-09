# Complete the pricing table

## Brief

The workstation's pricing table leaves three current rates blank, links a renamed support page,
and still prices Fable 5.1. Fable 5.2 became the current Fable model on 2026-11-09. This design fills in the rates
and moves the Fable column to 5.2. The seat question stays closed: Sonnet stays at half Opus's
price on every token class, and Fable holds no seat. Approving it starts one `ordinary` change.

## Gap

The monthly checklist's pricing table moved to `claude/.claude/docs/fable-post-cutoff-system.md`
(lines 98-109) when `model-economy.md` was folded. These entries have gone stale:

- Opus 5.5 cache read reads "not recorded here".
- Sonnet 5.5 and Haiku 5.5 batch read "not recorded here".
- The Fable plan link uses the old slug, and the allowance line names only Max.
- The Fable column, the rates in the doc's opening paragraph (line 9), and the "Fable 5.1's saving"
  note (lines 114-116) describe Fable 5.1.

## Evidence

- Pricing page: Opus 5.5 cache read is $0.20 per MTok. Batch is $1 / $5 on Sonnet 5.5, and $0.05 /
  $0.25 on Haiku 5.5 up to 100k
  (<https://platform.claude.com/docs/en/about-claude/pricing>).
- Claude Fable models on your plan: on Max and Ultra, Fable "can use up to half" of the weekly limit
  (<https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan>). The allowance
  itself is unchanged, and it covers Fable 5.2, 5.1, and 5.
- Pricing page, Fable 5.2: $8 input, $40 output, and $0.20 cache read per MTok, with batch at $4 /
  $20 (<https://platform.claude.com/docs/en/about-claude/pricing>). Fable 5.1 was $10 / $50 and
  $0.25.
- Announcement: on Medium effort Fable 5.2 "can accomplish challenging tasks with fewer tokens than
  Fable 5.1", with no figure given (<https://www.anthropic.com/claude-fable-and-mythos-5-2>).
- Launch offers: a Max subscriber gets one to three Fable limit resets by subscription length, and
  they expire 2027-03-08
  (<https://support.claude.com/en/articles/17506494-claude-fable-5-2-launch-offers>).

The checklist says a cache-read change re-opens the seat question. Opus 5.5 at $0.20 and Sonnet 5.5
at $0.10 hold the 2:1 ratio of their base prices, so it doesn't. Fable 5.2's cache read now equals
Opus 5.5's at $0.20, but Fable is reached only by escalation, so no seat depends on it.

## Proposed change

1. Fill the three cells from the pricing page.
2. Replace the plan link, name Max and Ultra, and date the check 2026-11-09.
3. Retitle the Fable column to Fable 5.2 with its rates, and update the line 9 rates to match.
4. Replace the "Fable 5.1's saving" note with the announcement's unquantified claim, and add the
   launch resets with their expiry.

Checklist item 2 names the retired `model-economy.md`, so the
[open flags design](2026-11-01-model-review-open-flags-design.md) moves that item to this file.

This is `ordinary`, since the doc isn't on the `runner` path map.

## Audit findings taken

None. This came from checklist item 2, and on 2026-11-09 from the Fable 5.2 release.
