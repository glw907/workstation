# Settled decisions for the desk mock-ups (do not re-litigate)

Owner: Geoff. Each was ruled in this arc after a render; a lens may flag a DEFECT in how one is
executed, never propose reversing one.

Dose words (verbatim): "Remember that the purpose of this page is function. Design matters, but
usability is the most important item." / "The whole interface should be built with DaisyUI
components." / "There are design levers you can pull for daisyui elements."

1. Inverted-pyramid page: headline, lede, then "What changes" / "If you approve" inside ONE
   headline block (filled base-200, 4px primary left rail hanging in the margin), then
   "Decide first" (problem PR only), then Details, then Evidence.
2. Headline: serif display face (Spectral, `desk-title`), ~1.75rem, balanced wrap. Lede: sans
   (Karla), ~1.05rem, near full strength, 12px below the headline. Lede must stay sans
   (owner: a serif lede read as busy).
3. Inside the block, under a hairline: two parallel columns. Sub-headings at 0.95rem semibold,
   full ink. List markers start flush with the sub-heading's left edge, text in a second column,
   small marker gap (owner: no outdented markers; tight marker-to-text gap).
4. Importance ladder: L1 headline+lede; L2 must-act (Decide first, triage "Do now") with full-ink
   section heading and the ONLY warning/error color; L3 supporting; L4 Details (small caps
   eyebrow, rows at body size); L5 Evidence (same eyebrow, smaller/lighter rows); lowest: triage
   "Don't do" (dimmed), meta lines, technical detail.
5. Color means "act here": primary blue only for the primary button and the headline rail.
6. Disclosures: leading chevron, points right closed, rotates down open (owner rejected DaisyUI's
   default down-then-up arrow).
7. Triage row: bold action, reason, a Do now / Do later / Don't do join of radio buttons (selected
   one tinted), a "Note" ghost button, then a faint "Technical detail" disclosure that must look
   unlike the choice buttons.
8. "Decide first" items are DaisyUI soft alerts with a choice join; Approve is disabled until each
   has a choice.
9. Decision bar: floating panel, width of the content column, 16px off the bottom, rounded,
   bordered, soft shadow, fade behind it. Left: status dot, bold state line, lighter reason line.
   Right: outlined "Send back" (return icon, R kbd) and primary "Approve and merge" (check icon,
   A kbd). Triage: "Submit calls" with Ctrl Enter.
10. App name "Design & PR Approvals"; no "desk" wording in visible copy except real identifiers
    (branch `desk-hook`, hook `claude-desk-reminder`).
11. Copy is the owner-approved text; a lens never rewrites copy (trims only, and only to flag).

Known, already-accepted leftovers: the selected join button's thin blue outline violates rule 5
and will be neutralized in the build; inline code renders slightly large in mock disclosures and
will use the desk's own code style in the build.
