---
name: visual-fidelity
description: >
  The method for UI work that must match an existing reference: site rebuilds, theme ports, design
  migrations. Invoke at the START of any port or rebuild, and when a result must match a reference rather
  than merely look good. Also invoke, for the "ink, not boxes" section alone, on any vertical-alignment or
  optical-centring judgment (an icon, chip, or control beside text).
---

# Visual fidelity (ports, rebuilds, migrations)

Born from two production visual misses (2026-07-05: 907.life typography, ecxc.ski structure)
whose mechanical gates were all green. The failure class: verbal specs lose the design,
and the builder's own context grades its work "close" (Anthropic's prompting guidance:
fresh-context verifiers outperform self-critique). This skill is the countermeasure stack,
each step traced to evidence in docs/internal/pre-beta-harvest.md (cairn-cms) and the
2026-07-05 research report.

## The method, in order

1. **The original manifest is the backbone** (Geoff, 2026-07-06: "much more aggressive about
   reviewing the original and matching ALL features and content"). The original is the
   specification. Before any plan, capture every page (full-page, at the family widths) and
   enumerate the original into a committed checklist: every page and section; every image
   with its identity (which asset, its crop and focal treatment, and where it appears),
   because the original's image choices are the club's content decisions, so a substituted
   hero or a bad re-crop is the same defect as a missing section; every data element; every
   interactive behavior; every feed, redirect, and error page. No design plan is authored
   from a verbal inventory alone.

   The build is done when every line is graded MATCHED, IMPROVED, or DEFERRED-WITH-SANCTION
   (named in the spec). Standing sanction (Geoff, 2026-07-06): fix the original's defects
   (typos, broken behaviors, responsive failures, a11y violations, weaker CSS) and grade
   them IMPROVED without per-item approval, recording what was fixed. Verifiers grade
   against the manifest, not the plan, because the plan is a lossy compression of the
   original and three builds under-matched by checking the compression.
2. **Device catalogue.** An agent (vision-capable, Opus+) READS the references plus the
   source CSS and produces the structural + typographic device catalogue: chrome anatomy,
   composition per page template, card/band recipes, every typographic device (wordmark,
   stamps, links, quotes, code), color PLACEMENT (where each hue actually lands). Exact
   values from the source, never paraphrase.
3. **Build with the canonical loop.** The builder gets reference IMAGES (not descriptions)
   plus the catalogue, and works Anthropic's canonical loop: implement, screenshot the
   result, compare to the reference, list differences, fix. Tokens transfer color and
   faces; STRUCTURE requires building the structure — a theme layer over a mismatched
   scaffold cannot reach a different composition.
4. **Fresh-context verifier gate — a LOOP, not a line.** A verifier agent that did NOT
   build grades each page: reference and render as SEPARATE LABELED image blocks (Anthropic
   vision docs; composite images are unproven), per width, verdict per visual device,
   differences classified COSMETIC vs STRUCTURAL. On FAIL: a fix agent works the list, and
   then a FRESH verifier grades the fixed state — a fix agent confirming its own fixes is
   the self-grading failure one level down (all three slate ports' fix agents did exactly
   this, 2026-07-06, and each needed an independent recheck). The loop exits only on a
   fresh PASS. In workflow scripts: while-not-PASS around verify->fix, never verify->fix->
   done.
5. **The one-check rule (deploy gate).** The main loop READS the final renders itself, and
   a member/user-facing site gets the owner's before/after approval. Nothing deploys
   unlooked-at. Deploy watchers verify the run's exact head sha (stale greens happen).
6. **Pixel-diff CI rider.** After fidelity is achieved, freeze it: Playwright
   `toHaveScreenshot` specs at the family widths in the site's own CI, baselines rendered
   by the canonical CI runner (never trust a local render as canonical; regen by FILE PATH,
   not title grep — a grep that can't fail verifies nothing).

7. **Iterate the chassis after every use (Geoff, 2026-07-05).** Each theme or site built
   on the chassis ends with a harvest step: every friction, missing seam, needed recipe,
   exposed coupling, and lying removal note folds back into the STARTING CHASSIS (the
   canonical copy the next theme receives) as landed improvements, and into the engine
   where the lesson runs deeper. The chassis gets better with every consumer; a build is
   not done until its harvest is banked.

## Known anti-patterns (each cost a real deploy)

- The official frontend-design skill is for ORIGINAL aesthetics; it has no
  reference-comparison step. Do not reach for it on a port.
- "Zero chrome edits needed" on a non-blog design is a failure signature, not a win.
- Instrumental goals (test the seams) never outrank the terminal goal (the site looks
  right); frame experiments as measurements, not constraints.
- Acceptance criteria containing "looks like X" cannot be graded by the context that
  built X.

## Ink, not boxes (the vertical-alignment blind spot)

Born 2026-08-07, the cairn vertical-alignment pass: three audit rounds, a probe condemned
three times, and the same root error in two disguises. Read this section for ANY vertical
alignment judgment, not only a port. This defect class is authored, not ported: the three
admin rows the pass finally confirmed had been 2.5px wrong since the day they were written,
through every green test run.

**Why this one is different from every other visual defect.** Horizontal alignment is
box-level, and boxes are what CSS talks about and what `getBoundingClientRect` returns, so
reasoning from source lands close to reality. Vertical alignment is INK-level: the eye
centres a glyph's visual mass, CSS centres its line box, and an SVG's drawn art sits wherever
it sits inside a viewBox that centres perfectly. Every layer of the stack is box-shaped and
the judgment is ink-shaped. There is no doubt signal, because `items-center` reads as its own
confirmation, which is why this survives review and gets fixed instantly once someone points.

**The four rules, each one earned:**

1. **Compare against what the composition DECLARED.** Both major errors in that pass were the
   same shape: measuring a member against a target the CSS never asked for (a wrapping block's
   first line, then a baseline) on rows that declared `align-items: center` and ACHIEVED it.
   Read the container's alignment before judging any vertical relationship. The defect is
   deviation from the declared intent, never from an assumed one.
2. **Measure ink where the eye is the judge.** `getBBox()` is the GEOMETRY box, not the
   painted box, so a `fill="none"` spacer path inflates it to the full viewBox. Union only
   what actually paints, map through the screen CTM, and MARK any element-box fallback so it
   is never passed off as ink.
3. **A padded chip is a BOX, not a text run.** Scoring one `text-beside-text` and comparing
   BASELINES manufactures a defect equal to the cap-height ratio. The converse of the
   mixed-size rule is equally true and is the half everyone forgets: a mixed-size pair sharing
   a CENTRE has baselines that diverge by design.
4. **Read type metrics off the element that OWNS THE LINE BOX**, never an ancestor container
   and never the first text node's parent. A 10px `<span>` leading a 24px `<h2>` will resolve
   every font metric wrong and report a broken row as clean.

**The image settles what arithmetic cannot.** Three rounds of numeric correction moved that
pass 37 rows to 13 to 10 without resolving a single row's truth. One grader opening the PNGs
at 4x to 8x zoom resolved all ten definitively in one pass, and caught a "reviewed" decline
citing a crop nobody had looked at. So: NO row gets a disposition without its crop being seen,
and that belongs in the measuring tool's contract rather than an auditor's discretion.

**Two gate lessons that generalize past alignment:**

- **An approved snapshot baseline certifies STABILITY, never correctness.** A defect that
  ships before the baseline is written becomes the baseline, and no amount of green can ever
  surface it. Never cite a passing visual suite as evidence a composition is right.
- **Conformance verification cannot find a wrong premise.** Three adversarial verifiers found
  14 real defects, 8 in the reports-green-on-broken direction, and ALL THREE missed the
  premise error, because each was handed the spec's traps as ground truth and asked "does this
  conform?" Only the auditor asked "is this trustworthy?" and only the auditor caught it. Any
  verification fan-out needs at least one agent whose question is whether the whole thing is
  RIGHT, not whether it matches the brief that produced it.
