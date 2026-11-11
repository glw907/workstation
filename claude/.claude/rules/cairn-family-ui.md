---
paths:
  - "**/*.svelte"
---

# Cairn-family UI on this workstation

**DaisyUI first (Geoff, 2026-09-13).** Every cairn-family admin is DaisyUI. Prefer a stock
component over a home-grown one unless the rulings ledger records the defect that forced it. The
official DaisyUI skill (`standards:daisyui`) is the reference and the licensed Blueprint server
the pre-cut audit; the admin design system wins over both on conflict.

**Visual fidelity (2026-07-05).** UI work that must match a reference invokes the
`standards:visual-fidelity` skill at the start and gates on `standards:visual-verifier`. Nothing
deploys to production without a full-page render read in the main loop.

Cairn backlog items and engine-level UI mechanics follow `cairn-pass` and `site-pass`: a UI
mechanic belongs to cairn, a design choice to the site.
