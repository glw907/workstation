---
name: register-check
description: Run the full cairn three-gate prose review (mechanical slop gate, adversarial register edit, logic and claims check) on a draft and fold the findings. Use on any cairn prose artifact before Geoff reads it, or when Geoff asks for a register check.
context: fork
---

# Register check

The one-command form of cairn's three-gate prose review. Input: one or more file paths
(default: the file under discussion). Run the gates cheapest-first, consolidate, and present
findings as proposals unless Geoff has delegated application.

## Gate 1: mechanical (seconds)

Run Vale on the target(s) from the repo root (the in-tree `.vale.ini` carries the Google
package plus the Cairn slop style: VirtueClaims, Marketing, ContrastFrame, Announcement).
Error-tier findings are defects; fix or flag them before spending agent tokens. Warnings and
suggestions ride along as advisory context only. Also run `tellgrader --register docs <file>`
(the workstation tell scanner) for the classes Vale does not carry: connector openers, the
evidence-tiered slop lexicon, scaffold headers, bold-lead bullets, flat cadence. Its docs
register only approximates cairn's own voice, so treat its findings as advisory candidates for
Gate 2, not automatic defects.

## Gate 2: register (the editor's ear)

Dispatch the `cairn-register-editor` agent on the target(s). Its definition carries the tell
catalogue, the frame rules, the sanctioned-phrase list, and the corpus pointers; give it only
the file paths and any session-specific sanctioned phrases the definition doesn't know yet.
It returns ranked findings with proposed rewrites.

## Gate 3: logic and facts (the Russell and empirical dimension)

Dispatch a read-only Opus `general-purpose` agent to verify the draft's factual claims
against the codebase (both directions: no statement contradicts a checkable fact, and every
substantive statement traces to positive support — code, a measurement, a documented
behavior, or Geoff's testimony), check presupposition-level truth, and check logical
consistency within the draft and against its sibling pages (README, why-cairn,
editor-welcome, the docs index must stay mutually consistent). Skip this gate only for edits
that touch no factual claim.

## Gate 4: links and citations

Audit the linking, in both directions, against two editorial standards: Wikipedia's linking
guideline (link only where relevant and helpful to the reader, first occurrence only, no
overlinking) and the Google developer style guide's link-text rules (descriptive anchors,
never bare URLs or "here").

- **Missing external links:** named entities a reader would plausibly want to follow
  (products, tools, papers, standards, organizations) linked at first mention — Cloudflare,
  iA Writer, a cited paper. A citation-shaped claim (a date, a quote, a figure) should carry
  its source where a verified URL exists; never fabricate a URL to satisfy this.
- **Missing internal links:** references to sibling pages that exist should link them, at the
  point where a reader would actually want to jump.
- **Gratuitous links:** repeated links to the same target, links on common words, decorative
  links that serve credibility theater rather than the reader. When in doubt, cut; a page's
  link density should stay low enough that each link reads as a recommendation.
- **Link text:** descriptive, reading naturally in the sentence.

## Fold and report

Consolidate the four gates into one ranked list: each finding with the exact quoted text,
what it trips, and the proposed fix. Separate MINE-to-fix (apply if delegated) from
GEOFF'S-CALL (his own phrases, product intent, taste forks). Note what was deliberately not
flagged and why, when it would look like a miss. A clean report is a valid outcome; say so
plainly and stop.

## Standing rules

- The living rule set is the register section of
  `docs/superpowers/plans/2026-07-01-docs-rewrite-stage-2.md`; it outranks everything here.
- Findings in Geoff's own words are flagged, never silently applied or silently kept.
- Rewrites are assembly (nearby facts, his fragments), never generated flourish.
- New tells Geoff catches during the session get bound into the plan's rule set and the
  `cairn-register-editor` definition before the session ends, so the system learns.
