---
name: cairn-figure
description: The production path for a figure (diagram, screenshot, or reproduction) on any cairn-family docs page. Use when adding, editing, or reviewing a figure in cairn-cms, ecxc-ski, 907-life, aksailingclub-org, xcathletes-org, or cairn-pub, or when a page needs a diagram, screenshot, or illustration and you are deciding whether it earns its place.
---

# cairn-figure

A figure is a diagram, a screenshot, or a hand-drawn reproduction on a cairn-family docs
page, and pages rarely need one. This skill holds the production path: whether a figure
earns its place, which of the two tools to reach for, what must ship alongside it, and how it
gets verified before a human reads the page.

## The two figure tests

Apply both before drawing anything and again to any figure already on the page.

1. **Remove it.** Delete the figure and read the surrounding prose alone. If the prose still
   makes the point, the figure earns nothing the words did not already carry.
2. **Read for the missing figure.** Read each paragraph and ask whether it is the text
   alternative of a diagram nobody drew: enumerable content forced into prose, or a spatial or
   branching relation described in a sentence a reader has to re-read to trace. A paragraph
   that fails this test wants a figure the page does not have.

A set of items is a table, not a figure. A linear sequence is a numbered list, not a figure.
Code the reader will type is a code block, not a figure.

## The two-lane routing rule

See the register's Visuals section
(`~/Projects/cairn-cms/docs/internal/docs-register.md`) for the current rules; this section
only restates what a builder needs at hand.

Mermaid in the page is the default: a diagram that is text in the same commit as its prose
renders in the corpus's own docs theme and in a plain GitHub view, and it cannot go stale
without the diff showing it. Hand-authored SVG is the exception, reached for only when a
themed mermaid render cannot carry the diagram at the corpus's polish bar. There is no third
tool.

Every figure, mermaid or SVG, ships its generating source committed alongside the page that
uses it: the mermaid block in the page itself, or the SVG's source file and the script that
generated it. A figure with no committed source is a finding on its own, independent of
whether it earns its place.

A diagram carries a complexity budget of about 15 nodes; split or simplify a diagram past it.
Diagrams render in cairn's own theme: the stock `neutral` mermaid render never ships, and a
diagram the themed render cannot carry at the polish bar is hand-authored SVG, never a
drawing-tool screenshot.

## The text-alternative and containment rules

See the register's Visuals section
(`~/Projects/cairn-cms/docs/internal/docs-register.md`) for the current rules; this section
only restates what a builder needs at hand.

Every image and diagram carries alt text, capped at 150 characters: the kind first (diagram,
screenshot, reproduction), never "Image of", stating what the reader learns rather than what
the pixels show. A decorative image gets `alt=""`, never an omitted attribute, and is authored
as HTML (`<img alt="" ...>`) so the empty alt is visibly deliberate; markdown image syntax
(`![...]`) always carries real alt text. A complex diagram carries a two-part alternative, a
short alt plus the essential information in body text, not only in the alt. Every authored
diagram and every live reproduction carries a caption in complete sentences, never redundant
with the alt and never referring to the figure spatially ("the image above").

A `repro` fence carries its caption a different way: the caption lives INSIDE the fence body,
as the `caption` key, not as an emphasis paragraph after the fence, because the body must be
self-describing where the mermaid plugin does not run (GitHub, the tarball). The fence's
`width` key is what satisfies the 320/390 bar the diagram bullet above is exempt from; a live
reproduction stays bound by that bar. The key shape, as the register states it:

```repro
caption: "..."
width: 390
```

Authored docs diagrams are exempt from the family's 320/390 responsive bar (WCAG 1.4.10
exempts diagrams from reflow by name): they scroll inside their own `overflow-x: auto` figure
at narrow widths instead of shrinking. A live reproduction stays bound by the bar. The full
ruling record is the cairn-cms docs register, Visuals section
(`~/Projects/cairn-cms/docs/internal/docs-register.md`) and the sitting behind it
(`~/Projects/cairn-cms/docs/internal/record/2026-08-15-docs-visual-layer-rulings.md`).

## The gates do not exist yet

`check:figures` and `check:visuals` are cairn-cms's mechanical floor for this standard:
`check:figures` is meant to grow from today's staleness check to seven assertions covering
the routing rule, the committed-source requirement, and the alt/caption rules, and
`check:visuals` is meant to close the hole where an image with no alt attribute passes
unseen. **Neither exists today.** Both are pass 2a's work (the cairn documentation standard's
second plan), and this skill names them as the standard they will enforce, not as a gate you
can run now. Do not go looking for `npm run check:figures` before pass 2a lands it.

## Verification: the figure-verifier agent

Until the gates land, and after, the judgment layer for a figure is the `figure-verifier`
agent (`~/.claude/agents/figure-verifier.md`, `model: claude-opus-5-5`, read-only). Dispatch it
after a page carrying a figure is drafted or edited, before a human reads the page. It grades
every figure on the page against the two figure tests above and the register's visual-layer
rulings, and returns one of five verdicts per figure, each with a `file:line`: earns its
place, decoration, should be a table, should be a numbered list, or missing figure. It also
flags a missing source, alt, or caption as a separate, fixable finding even on a figure that
earns its place.
