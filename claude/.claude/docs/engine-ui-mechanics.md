# Engine-level UI mechanics, every cairn site

This holds CLAUDE.md's "Engine-level UI mechanics, every cairn site" section; CLAUDE.md keeps a pointer to it.

Every cairn-cms site (aksailingclub-org, ecxc-ski, 907-life, later consumers), not one repo. A
UI **mechanic** belongs to cairn; a design **choice** belongs to the site. A mechanic recurs in
any component of that shape on any cairn site: how a padded label optically centers its text,
which element a two-part row drops when space runs out, a framework default rendering an
invisible control on a dark ground. Patching one in a site's theme or a route's scoped `<style>`
leaves every sibling site to rediscover it.

**The primary path is consultation, before the pass builds.** Engine edges are enumerated at
plan-authoring time through the `engine-consult` skill (both pass skills carry the hook), and
accepted work lands ahead of the site task that needs it.

**Mid-pass filing stays as the fallback, default behavior, never a response to being asked.**
Consultation cannot foresee what a pass discovers while building: a pass carrying UI work ends
by enumerating what it built, asking of each item whether it is a mechanic, and filing what
qualifies BEFORE reporting the pass done. A mid-pass staging doc uses the consultation brief's
four-field item schema, and its triage runs through `engine-triage` against the rulings ledger
(`cairn-cms/docs/internal/engine-rulings.md`). **A repeated local
workaround is the loudest signal that something sits at the wrong altitude**: "this repo has
patched this before" is an automatic filing trigger, not a reason to patch it faster. (Born
2026-07-30: a third repeat patch of the same DaisyUI edge, filed only when Geoff asked.)

Two qualifications. A mechanic that is always right becomes a silent default (`text-box-trim`
for optical centering); one whose answer depends on what the content means makes the choice
explicit at the call site (which element a row drops). The mechanically detectable half belongs
in `cairn-audit`, never a consuming site's own probe script. Worked example with the evidence
and measurement methods: `aksailingclub-org/docs/2026-07-30-assets-substrate-harvest-findings.md`.
