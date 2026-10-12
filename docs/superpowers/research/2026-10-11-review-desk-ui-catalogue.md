# Review desk UI: device and behavior catalogue

Source: the four approved mockups in `docs/superpowers/specs/assets/2026-10-11-review-desk-ui/`
(`pr-b.html`, `design-b.html`, `triage-c2.html`, `empty-b.html`), read in full, against the design
`docs/superpowers/specs/2026-10-11-review-desk-ui-design.md`. Values below are quoted from the
mockup source. Line numbers are the mockup's own.

## Renders

Sixteen full-page PNGs sit in `docs/superpowers/specs/assets/2026-10-11-review-desk-ui/renders/`,
named `<mockup>-<light|dark>-<1440|390>.png`. They were taken in Chromium (`/usr/bin/chromium-browser`
driven by the Playwright npm package, since the Playwright MCP server could not find its Chrome
build), with `colorScheme` emulated, `reducedMotion: reduce`, after `networkidle`, `document.fonts.ready`,
and a 1.5 s settle.

- Every CDN request loaded: no failed request and no page error on any of the 16 loads (DaisyUI 5 and
  `@tailwindcss/browser@4` from jsdelivr, Karla and Spectral from Google Fonts, Monaspace Neon from
  jsdelivr Fontsource).
- Read full-page shots with care. The sticky decision bar and the drawer are captured where they sit
  in the first viewport (y 836 to 900 at 1440x900), so in a tall shot the bar appears part way down
  the page over content, and the queue column ends at y 900. That is a capture artifact, not the
  layout.
- The empty-state shots show "28 s" and a focus ring on Keep this tab open, because the countdown and
  the focus move start on load.
- `pr-b-*-390.png` is 636 px wide, not 390: the mockup itself overflows at phone width. The
  `div.stats.desk-glance` row (`grid-auto-flow: column`, and `.desk-glance { overflow: visible }`) is
  636 px wide and scrolls the page sideways. The other three mockups are 390 px wide at 390. The build
  must fix this (for example `stats-vertical` below `sm`, or a wrapping flex row), since a phone-width
  page must not scroll sideways.

## Shared chrome

All four mockups share the same `<head>` styles (except triage, see Custom CSS), the same shortcut
sheet, the same toast, and the same first `<script>` block, byte for byte.

### Page skeleton

```
div.drawer.lg:drawer-open
  input#queue-toggle.drawer-toggle  type=checkbox aria-label="Queue" tabindex="-1"
  div.drawer-content.flex.min-h-dvh.min-w-0.flex-col
    header.navbar ... lg:hidden          (mobile navbar)
    main#main tabindex="-1"              (item pane)
    div#decision.sticky.bottom-0 ...     (decision bar; PR, design, triage only)
  div.drawer-side.z-30
    label.drawer-overlay for=queue-toggle aria-label="Close the queue"
    nav#queue-nav aria-label="Review queue"
dialog#keys.modal                         (shortcut sheet)
div.sr-only#sr-status role=status aria-live=polite
div.toast.toast-center.bottom-24.z-40#toast-wrap hidden
```

- The drawer stays open at `lg` (1024 px and up) through `lg:drawer-open`. Below `lg` it is closed
  and the mobile navbar shows.
- Drawer width: `nav` has `w-[19rem]` (304 px measured).

### Queue (drawer side)

`nav#queue-nav.flex.min-h-full.w-[19rem].flex-col.border-r.border-base-300.bg-base-200`, top to bottom:

1. Header block: `div.relative.isolate.border-b.border-base-300.px-4.pt-4.pb-3` holding
   `svg.site-contour-texture` (`viewBox="0 0 400 60" preserveAspectRatio="none" aria-hidden="true"`,
   three paths `M160 58c40-18 70-6 110-20s80-22 130-6`, then `M160 48...`, `M160 38...`), a title
   `p.text-[1.05rem].font-bold` with `<i class="site-benchmark"></i>Review desk`, and a count line
   `p#queue-count.mt-0.5.text-sm.desk-muted aria-live="polite"`: "4 waiting, oldest first" (PR),
   "3 waiting, oldest first" (design), "2 waiting, oldest first" (triage), "0 waiting" (empty).
2. List: `ul#queue-list.menu.desk-queue.w-full.gap-0.5.px-2.py-2.text-sm`. Each row is
   `li > a[data-q]` with three spans:
   - `span.desk-q-meta`: kind then repo, for example `<span class="mr-1">PR</span>cairn-cms #113`.
     In `triage-c2.html` only, the kind is a badge:
     `<span class="badge badge-outline badge-xs mr-1.5 align-[1px]">Triage</span>`.
   - `span.desk-q-meta.tabular-nums`: age, for example "52 min".
   - `span.desk-q-title`: the item title, clamped to two lines.
   - Row grid (`.desk-queue a`): `display: grid; grid-template-columns: 1fr auto; row-gap: 2px;
     align-items: baseline; padding-block: 7px`; the title spans `grid-column: 1 / -1`,
     `font-weight: 600; line-height: 1.3`, `-webkit-line-clamp: 2`. Meta `opacity: 0.78`, font size
     `0.76rem` (`0.78rem` in triage, see Custom CSS).
   - Selected (open) row: `class="menu-active" aria-current="page"`. DaisyUI's `menu-active` paints
     the neutral fill (dark ink row in light, `#262e38` in dark) and the mockup adds
     `border-inline-start: 3px solid var(--color-primary)` (`.desk-queue a.menu-active`). Other rows
     carry a transparent 3 px start border so text does not shift.
   - Focused row (j/k): DaisyUI `menu-focus` class plus real focus; `aria-current` does not move.
   - Order: oldest first. PR mockup order: PR cairn-cms #113 (52 min), Design workstation (31 min),
     Triage workstation #13 (12 min), PR workstation #13 (4 min). A decided item leaves the list.
   - Empty list: `li.menu-disabled.px-3.py-2.text-sm.desk-muted` "Nothing waiting."
3. "Decided this session" block (design, triage, empty; absent in PR because nothing is decided yet):
   `div.border-t.border-dashed.border-(--site-rule-color).px-4.py-3`, heading
   `h2.text-sm.font-semibold.desk-muted`, list `ul.mt-1.text-[0.8rem]`, rows
   `li.flex.items-baseline.justify-between.gap-3.py-1` with `span.truncate` (kind and repo) and
   `span.shrink-0` (Approved, Submitted). Triage adds `font-semibold` to the outcome; the others do not.
4. `div.grow` spacer.
5. Footer row: `div.flex.flex-wrap.items-center.gap-x-2.gap-y-1.px-4.py-3.text-[0.8rem].desk-muted`
   with `button#open-keys.btn.btn-sm.btn-ghost.ml-auto` "Keyboard shortcuts" plus a `?` kbd. Triage
   alone adds `span.desk-sk` "j k next and previous" with two kbds before the button.
6. `footer.site-collar`: `<span>127.0.0.1:7907</span><span>Survey</span>`.

### Mobile navbar

`header.navbar.min-h-12.border-b.border-base-300.bg-base-200.px-3.lg:hidden`, holding
`button#queue-open.btn.btn-sm.btn-ghost` (`aria-controls="queue-nav" aria-expanded="false"`, text
"Queue (N)" with the waiting count) and `span.ml-2.text-sm.font-bold` with the benchmark triangle and
"Review desk".

### Top of the item pane

- PR, design, triage: `main#main.flex-1.px-5.pt-5.pb-8.lg:px-8` (design uses `pb-10`).
- `header.relative.isolate.pb-4` containing the same `svg.site-contour-texture`, then a meta line
  `p.flex.flex-wrap.items-center.gap-x-3.gap-y-1.text-sm.desk-muted` of spans, then
  `h1.desk-title.mt-1.text-[1.6rem].leading-tight` starting with `<i class="site-benchmark"></i>`.
- Meta line per kind: PR "cairn-cms #113", "worktree-engine-pass-b into main",
  `a.link` "GitHub"; design "workstation", "review-desk-design.md", "3 min read"; triage
  `span.badge.badge-sm.badge-outline` "Triage", "glw907/workstation #13", "13 found items from the
  close, each with a proposed disposition".

### Sticky decision bar

`div#decision.sticky.bottom-0.z-20.border-t.border-base-300.bg-base-200`, the last child of
`drawer-content`, so it spans the item pane only.

- PR and design: `form.px-5.py-3.lg:px-8 onsubmit="return false" aria-label="Decision"`:
  - `div#note-row.mb-3 hidden`: `label for=note .text-sm.font-semibold` "Rejection note" plus
    `span.font-normal.desk-muted` "(optional; the session reads it as the reason)", then
    `textarea#note.textarea.desk-field.mt-1.w-full.max-w-[88ch].text-sm rows=3`, placeholder "What
    needs to change before this can be approved".
  - Row `div.flex.flex-wrap.items-center.gap-x-4.gap-y-2`:
    - `div#guard.mr-auto.flex.flex-wrap.items-center.gap-x-4.gap-y-1.text-sm`: PR "Checks passed.
      Nothing is blocking."; design "Approved in the doc on 2026-10-11, scoped to lean v1."
    - `div#idle-actions.flex.items-center.gap-2`: `button#reject.btn.btn-outline.btn-error` "Reject"
      plus kbd `r`; `button#approve.btn.btn-primary.min-w-32` "Approve" plus kbd `a`. Default
      button size, not `btn-sm`.
    - `div#reject-actions hidden`: `button#cancel.btn.btn-ghost` "Cancel" plus kbd Esc;
      `button#send.btn.btn-error` "Send rejection" plus kbds Ctrl, Enter.
- Triage: `form.flex.flex-wrap.items-center.gap-x-4.gap-y-2.px-5.py-3.lg:px-8 aria-label="Decision"`
  with `p#tb-status.mr-auto.text-sm role="status"` "13 items, none changed from proposed" and
  `button#submit.btn.btn-primary.min-w-32` "Submit" plus kbds Ctrl, Enter.
- At 390 px the bar wraps: the status or guard line on top, the buttons below.

### Toast and undo region

```
div.sr-only role=status aria-live=polite #sr-status          (always in the DOM, empty at start)
div.toast.toast-center.bottom-24.z-40 #toast-wrap hidden
  div.alert.alert-info.border.border-base-300.text-sm #toast
    span#toast-text
    button#undo.btn.btn-sm  "Undo" + kbd z (desk-sk)
```

Survey's `.alert` override makes it a base-200 field with a 4 px info rule on the left (the
`::before` in components.css), so it reads as a quiet strip with a teal edge, centred, 96 px above the
viewport bottom, over the content and above the decision bar.

### Shortcut sheet (`?`)

`dialog#keys.modal aria-labelledby="keys-title"` >
`div.modal-box.max-w-xl.rounded-box.border.border-base-300.p-5`:

- `h2#keys-title.desk-title.text-xl` "Keyboard shortcuts".
- Settings switch, the only one in the sheet:
  `label.mt-2.flex.cursor-pointer.items-center.gap-3.rounded-box.border.border-base-300.px-3.py-2.text-sm`
  wrapping `input#single-keys.toggle.toggle-sm.toggle-primary checked aria-describedby="single-keys-desc"`,
  label "Single-key shortcuts", description `span#single-keys-desc.desk-muted`: "Letter, number, and
  symbol keys act on their own. Turn off if you use speech input or type stray keys. Esc, arrows, and
  Ctrl+Enter stay on."
- `div.mt-3.grid.gap-x-8.gap-y-4.text-sm.sm:grid-cols-2` with three `section`s, each an
  `h3.mb-1.font-semibold.desk-muted` and a `table.table.table-xs`:
  - Anywhere: j "Next item in the queue"; k "Previous item in the queue"; z "Undo the last decision,
    until the next item loads"; ? "Show or hide this sheet"; Esc "Close the sheet or the note".
  - PR and design: a "Approve"; r "Reject, with the note field focused"; Ctrl Enter "Send the
    rejection"; / "Filter files by path".
  - Triage: ↑ ↓ "Move between rows"; 1 2 3 "Now, defer, or drop the focused row"; Ctrl Enter
    "Submit every row".
- `div.modal-action.mt-4` > `form method=dialog` > `button.btn.btn-sm` "Close" plus kbd Esc; plus
  `form.modal-backdrop method=dialog`.
- Every kbd is `kbd.kbd.kbd-xs.desk-kbd`; single-key ones add `desk-sk` so they hide when the switch is
  off. Esc, Ctrl, Enter, and arrow kbds never carry `desk-sk`.

The auto-close setting is not in the sheet: it is a toggle on the empty page (see Empty).

## Per mockup

### PR (`pr-b.html`)

Top to bottom inside `main`:

1. Header (above). Title "Engine pass B before stage 2b (lean re-plan)".
2. Figures: `div.stats.desk-glance.mt-1 role="group" aria-label="PR at a glance"` with four stats.
   The first is a `div.stat`; the other three are `a.stat` links to `#checks`, `#verdicts`, `#files`.
   Each is `div.stat-title` over `div.stat-value`. Labels and values: Risk "auth-data"; Checks "11
   passed, 1 skipped"; Review "Accepted"; Changes "161 files" then `span.desk-add` "+5,922" and
   `span.desk-del` "−931" (U+2212 minus). `.desk-glance` strips the DaisyUI box: transparent, no
   dividers, `padding: 0 44px 0 0`, title `0.8rem` muted, value `1rem` weight 600.
3. `div.mt-7.grid.gap-x-12.gap-y-7.xl:grid-cols-2` with two sections side by side at `xl` (1280 px):
   - `section#checks aria-labelledby="checks-h"`: `h2.text-sm.font-semibold` "Checks" plus
     `span.font-normal.desk-muted` "11 passed, 1 skipped, on dc4f964e"; list
     `ul.mt-1.5.grid.gap-x-6.text-[0.84rem].desk-muted.sm:grid-cols-2`, items
     `li.flex.min-w-0.items-center.gap-2.py-0.5` with `span.truncate` name and, for a skipped check,
     `span.ml-auto.shrink-0` "skipped". No icons, no color: every check passed, so the mockup shows no
     failing-check treatment.
   - `section#verdicts`: `h2` "Review" plus muted "accepted after 3 fix rounds; score 6.1 h of 9";
     `table.mt-1.w-full.text-[0.84rem]`, rows of three cells
     (`td.whitespace-nowrap.py-1.pr-4` reviewer, `td.py-1.pr-4` verdict, `td.py-1.desk-muted` note).
     Verdicts "fix", "accept", "pass" are plain text; no blocking-verdict color is shown.
4. `section.mt-8 aria-labelledby="desc-h"`: `h2#desc-h.text-base.font-semibold` "Description", the
   PR body's lead paragraph in `div.desk-md.mt-1`, then `div.desk-plain-list.mt-3` of collapsible
   body sections, one per `##` heading: `details.collapse.collapse-arrow.desk-collapse.rounded-none.border-t.border-base-300`,
   `summary.collapse-title.text-sm`, `div.collapse-content > div.desk-md.px-3.pb-3`. Section titles:
   What landed (open by default, holds a table), auth-data verdicts, Consumer proof, Review, Visual,
   Smoke, Retried tests, Found, not done, Decision 12, Score. Rendered markdown uses `.desk-md`
   (tables, lists, inline `code` on base-200).
5. `section#files.mt-8 aria-labelledby="files-h"`:
   - Toolbar `div.flex.flex-wrap.items-center.gap-x-4.gap-y-2`: `h2#files-h.text-base.font-semibold`
     "Files", `span#file-summary.-ml-2.text-base.desk-muted role="status"` "161 in 10 groups", the
     path filter `label.input.input-sm.ml-auto.w-full.sm:w-72` holding a 16 px search SVG
     (`h-4 w-4 opacity-60`), `input#file-filter.grow type=search placeholder="Filter by path"
     aria-label="Filter files by path"`, and a `/` kbd (`desk-sk`); then
     `button#toggle-groups.btn.btn-sm.btn-ghost` "Open all groups".
   - `div#file-groups.mt-2`: ten groups by top-level directory, in this order: `.github/` (1),
     Repository root (3), `docs/` (28), `examples/` (17), `packages/` (18), `scripts/` (6), `skills/`
     (2), `src/` (64, open by default), `templates/` (21), `tool/` (1). A group is
     `details.collapse.collapse-arrow.desk-collapse.rounded-none.border-t.border-base-300[data-group]`
     whose `summary.collapse-title` holds `span.desk-mono.text-[0.85rem].font-semibold` (directory),
     `span.text-sm.desk-muted[data-count=N]` ("N files"), and
     `span.ml-auto.flex.shrink-0.items-center.gap-3.tabular-nums.text-[0.8rem]` with the group's
     `+adds` (`desk-add`) and `−dels` (`desk-del`).
   - Files: `ul.pl-4 > li[data-path]` (lower-cased path) > nested `details.collapse.collapse-arrow.desk-collapse.rounded-none.border-t.border-base-300`
     whose `summary.collapse-title.text-sm` holds `span.min-w-0.truncate.desk-mono.text-[0.8rem]`
     (directory part in `span.desk-muted`, then the file name in ink), an optional status badge
     `span.badge.badge-xs.badge-outline.desk-add.shrink-0` "new" (22 files) or
     `badge-xs badge-outline desk-del` "deleted" (4 files), and
     `span.ml-auto.shrink-0.tabular-nums.text-[0.8rem]` with `+N −N`. One file
     (`src/lib/render/sanitize-schema.ts`) is open by default.
   - Diff, inside the file's `div.collapse-content`: `table.desk-diff > tbody` of rows with four cells:
     `td.ln` old line number, `td.ln` new line number, `td.sg` sign, `td.cd` code. Row kinds:
     `tr.hunk` (the `@@ -a,b +c,d @@ context` line, empty number cells), `tr.add` (sign "+", old number
     empty), `tr.del` (sign "−" U+2212, new number empty), and plain context rows (empty sign).
     Colors: add rows `color-mix(in oklab, var(--color-success) 13%, var(--color-base-100))` with a
     `--cairn-success-ink` bold sign; del rows `color-mix(in oklab, var(--color-error) 11%, var(--color-base-100))`
     with a `--cairn-error-ink` bold sign; hunk rows base-200 ground in `--cairn-info-ink` with 2 px
     block padding; line numbers muted, tabular, right-aligned, unselectable, with a base-300 rule on
     their end edge. Monaspace Neon at 0.76rem, line height 1.55, `pre-wrap` with `overflow-wrap: anywhere`
     (no horizontal scroll in the diff). No syntax highlighting.
   - `p#no-match.mt-2.hidden.text-sm.desk-muted role="status"` "No file path matches that filter."
6. Decision bar (above) with Reject and Approve.

Before merge: the PR mockup has no `## Before merge` section and no warning anywhere. The only guard
text is `#guard` "Checks passed. Nothing is blocking." The design says a `## Before merge` section
"stays a warning above Approve". The natural home is `#guard` (an `alert alert-warning` there, or a
warning line in that slot), but the mockup does not show it.

Unused in the PR body: `.desk-stat5` (a five-cell diffstat) and `.desk-stats` are defined in the
`<style>` block and never used in the markup.

### Design (`design-b.html`)

1. Header: meta "workstation · review-desk-design.md · 3 min read" (three spans), title
   "Review desk (design)".
2. `article.desk-read`, the rendered document. Its own `h1` is hidden (`.desk-read h1 { display: none; }`)
   because the page header carries the title. Reading measure: `max-width: 68ch` (the later override;
   the base rule says 70ch), Spectral (`--font-display`) at `1.06rem`, `line-height: 1.72`. `h2` is
   weight 500, `1.3rem`, line height 1.25, margin `1.6rem 0 0.4rem`, with a dashed contour rule under
   it (`padding-bottom: 4px; border-bottom: 1px dashed var(--site-rule-color)`). Lists are disc, nested
   lists circle; `strong` 600; inline `code` Monaspace on base-200, 3 px radius.
3. Decision bar with Reject and Approve; guard "Approved in the doc on 2026-10-11, scoped to lean v1."

No figures, no file list, no filter. The shortcut sheet still lists `/` under "PR and design".

### Triage (`triage-c2.html`)

1. Header: badge "Triage", repo, "13 found items from the close, each with a proposed disposition";
   title "Found, not done: review desk lean v1".
2. Hint line `p.mb-2.text-sm.leading-7.desk-muted`: "Each item starts at the session's proposal. ↑↓
   move between items, 1 2 3 set now, defer, or drop; menus take arrows and Esc." The "1 2 3" clause
   is wrapped in `span.desk-sk` so it hides with the switch off.
3. Three sections, Now, Defer, Drop, each
   `section.desk-group aria-labelledby="g-now" data-group="now"` (and `defer`, `drop`):
   - `h2#g-now` with `span.desk-dot aria-hidden="true"`, the label, and `span.desk-count[data-count]`
     (3, 8, 2 at start). Heading: weight 700, `0.95rem`, flex with an 8 px gap, a dashed
     `--site-rule-color` underline, 8 px start padding. Count weight 400, muted.
   - Dot: 8 px circle in `--desk-hue`, set per group: Now `var(--cairn-warning-ink)`, Defer
     `var(--color-info)`, Drop `var(--color-muted)`. Contrast on base-100, computed here: Now 6.24:1,
     Defer 4.42:1, Drop 6.03:1 (light); 11.06, 8.67, 7.59 (dark). Defer on base-200 (a focused or
     current row) is 4.04:1.
   - `ol.desk-v.desk-c aria-labelledby="g-now"` of rows, kept in item-number order within a group.
   - `p.desk-empty[data-empty] hidden` "Nothing here." (48 px start padding, `0.84rem`, muted) when a
     group empties.
4. Row: `li[data-row=N][data-proposed][data-value] tabindex="-1" aria-labelledby="item-N" aria-describedby="was-N"`
   (row 1 starts with `tabindex="0"`). Grid `2rem minmax(0, 1fr)`, gap 16 px, padding
   `10px 12px 10px 8px`, box radius, 2 px between rows. Contents:
   - `span.tb-n aria-hidden="true"` the item number: muted, tabular, right-aligned.
   - `div.min-w-0` > `p.tb-text#item-N` (line height 1.45, `max-width: 80ch`; inline code is
     `code.desk-mono.rounded-[3px].bg-base-200.px-1.text-[0.86em]`) then `div.tb-reason[data-reason]`
     (`0.84rem`, muted, flex-wrap, gap `2px 10px`) holding:
     - `span[data-reason-text]`: the reason, or `<span class="italic">No reason given.</span>`.
     - `button.link.link-hover.min-h-6.text-[0.8rem][data-edit]`: "Edit reason" or "Add a reason",
       `aria-label="Edit reason for item N"` or `"Add a reason for item N"`.
     - `button.link.link-hover.min-h-6.text-[0.8rem][data-trigger]` "Move to",
       `popovertarget="mc-N" aria-haspopup="menu" aria-expanded="false" aria-label="Move item N to another disposition"`.
     - `span.tb-was#was-N[data-was]`: empty, or "was Now" / "was Defer" / "was Drop" after a move
       (`0.78rem`, muted).
     - `input.input.input-sm.w-full.max-w-[80ch][data-reason-input] hidden`, `placeholder="Why this disposition"`,
       `aria-label="Reason for item N"`.
   - The "Move to" menu: `ul.dropdown.desk-menu.menu.menu-sm.w-48.rounded-box.border.border-base-300.bg-base-100.p-1`
     with `popover id="mc-N" role="menu" aria-label="Move item N to"`; three
     `li role=none > button role=menuitemradio aria-checked data-value` items, Now, Defer, Drop,
     each with its kbd (1, 2, 3, `desk-sk`). The checked item has `menu-active`. The proposed item
     carries `span.desk-prop[data-prop]` "proposed" (`0.72rem`, opacity 0.8). Items use
     `justify-content: space-between`.
   - Moved row (`li.is-moved`): a 6 px dot in the target group's hue, absolutely placed to the left
     of the number (`.tb-n::before`, `left: -2px; top: 0.72em`).
   - Current row (`li.is-current`, set on focus-in): base-200 ground. Focus draws the global
     `:focus-visible` ring (2 px primary, 2 px offset).
5. Decision bar: status line and Submit.

No radio groups and no `join` buttons are used in the approved triage; the decision is the section
the row sits in plus the menu.

### Empty (`empty-b.html`)

1. Mobile navbar "Queue (0)".
2. `main#main.relative.isolate.flex.flex-1.items-start.px-5.pt-16.lg:px-8 tabindex="-1"` >
   `div.max-w-[60ch]`:
   - `h1.desk-title.text-[1.6rem].leading-tight` with the benchmark: "Nothing waiting".
   - `p.mt-2`: "All four items are decided, and each waiting session has its answer." then
     `span#close-line` "This tab closes in `<span id="secs" class="tabular-nums font-semibold">30</span>` s."
   - `div.mt-4.flex.flex-wrap.items-center.gap-x-4.gap-y-2`:
     `button#keep.btn.btn-sm.btn-ghost.-ml-3` "Keep this tab open" plus kbd Esc (no `desk-sk`), and
     `label.flex.cursor-pointer.items-center.gap-2.text-sm` with
     `input#auto-close.toggle.toggle-sm.toggle-primary checked` "Close when empty".
   - `p.mt-8.text-sm.desk-muted` "New items open in their own tab."
3. No decision bar, no item header, no contour texture in main.
4. Queue: "0 waiting", the "Nothing waiting." row, and Decided this session with four rows
   (PR workstation #13 Approved, Triage workstation #13 Submitted, Design workstation Approved,
   PR cairn-cms #113 Approved).

The countdown is a plain span, not the DaisyUI `countdown` component.

## Custom CSS

The mockups carry four style blocks: a `text/tailwindcss` `@theme static` block, the Survey tokens as
`:root` variables (light, then dark under `@media (prefers-color-scheme: dark)`), the Survey
`components.css` copied verbatim, and a desk layer.

### Survey parts (already in `review-desk/src/lib/survey/`)

- The `@theme static` block (fonts, `--text-step-1` to `-13`, `--text-step-inline-code`,
  `--spacing-1px` to `--spacing-24px`) matches `theme.css`'s `@theme` block, with one difference:
  the mockup's `--font-body` is `"Karla Variable", "Karla", system-ui, sans-serif` (the extra
  `"Karla"` catches the Google Fonts family); `theme.css` has `"Karla Variable", system-ui, sans-serif`.
  The app self-hosts Fontsource (`fonts.css`), so no change is needed.
- The `:root` token block is "verbatim from review-desk/src/lib/survey/theme.css" and the values
  match the two `@plugin "daisyui/theme"` blocks (`survey`, default; `survey-dark`, `prefersdark: true`).
  The app gets light and dark from DaisyUI's theme switching, not from a `:root` media block.
- The components block is byte-identical to `components.css` (one trailing blank line differs).
  It supplies `.alert` (base-200 field, 4 px status rule), `.alert-*` ink, `.site-contour-rule`,
  `.site-benchmark`, `.site-contour-texture`, `.site-collar`, `.card-border`, field and control edges,
  `.list` dividers, `.input`/`.select` ground and size, `a:focus-visible`, `.btn` line height and focus
  color, and `.site-index-rail` (unused by the desk).

### Desk layer (mockup-only: none of these exist in Survey or the app)

| Rule | What it styles | Survey or DaisyUI home? |
|---|---|---|
| `html, body { background-color: var(--color-base-100); color: var(--color-base-content); }` | page ground | DaisyUI's theme sets this on `:root`; drop it. |
| `body { font-family: var(--font-body); font-size: 1rem; line-height: 1.5; }` | body face | Tailwind `font-body` on `body` or the layout; no Survey rule sets it. |
| `:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }` | every focus ring | Survey covers only `a` and `.btn`; this generalises it. Mockup-only. |
| `.desk-title { font-family: var(--font-display); font-weight: 500; letter-spacing: -0.005em; }` | page h1, sheet title | Tailwind `font-display font-medium tracking-[-0.005em]`; uses Survey tokens. |
| `.desk-muted { color: var(--color-muted); }` | secondary text | Tailwind `text-(--color-muted)`; Survey token. |
| `.desk-mono { font-family: var(--font-mono); }` | paths, code | Tailwind `font-mono`. |
| `.desk-add { color: var(--cairn-success-ink); }`, `.desk-del { color: var(--cairn-error-ink); }` | diff counts, new/deleted badges | Survey tokens; mockup-only classes. |
| `.desk-kbd` (two rules; the later wins) | kbd hints in buttons and rows: `background: transparent; color: inherit; font-family: var(--font-body); border-color: transparent; min-width: 0; padding-inline: 2px; font-size: 0.7rem; opacity: 0.7` | Overrides DaisyUI `kbd`. Mockup-only. In triage only the first rule applies (bordered at 45% currentColor, `min-width: 1.4em`, no opacity, 10 px). |
| `.desk-queue a { display: grid; ... padding-block: 7px; border-inline-start: 3px solid transparent }`, `.desk-q-title {...}`, `.desk-q-meta { opacity: 0.78; font-size: 0.78rem }` then `.desk-q-meta { font-size: 0.76rem; }`, `.desk-queue a.menu-active { border-inline-start-color: var(--color-primary); }` | queue rows | Mockup-only, over DaisyUI `menu`. |
| `.input input:focus-visible { outline: none; }` | inner search input, so the `label.input` draws the only ring | Mockup-only; needed because of the global `:focus-visible`. |
| `.desk-stats .stat {...}` and children | not used in any body | Dead; skip. |
| `.desk-collapse > .collapse-title { min-height: 2.25rem; padding-block: 6px; padding-inline: 12px 40px; display: flex; align-items: center; gap: 12px; }`, `.desk-collapse.collapse-arrow > .collapse-title::after { top: 50%; inset-inline-end: 18px; }`, `.desk-collapse > .collapse-content { padding-inline: 0; }`, `.desk-collapse[open] > .collapse-content, .desk-collapse:focus-within > .collapse-content { padding-bottom: 0; }`, `.desk-collapse > .collapse-title:hover { background-color: var(--color-base-200); }` | compact body sections, file groups, files | Mockup-only override of DaisyUI `collapse`. |
| `.desk-diff` and `td`, `.ln`, `.sg`, `.cd`, `tr.add`, `tr.del`, `tr.hunk` | the diff table (values in PR above) | Mockup-only; colors from Survey tokens. |
| `.desk-stat5` and `i`, `i.a`, `i.d` | five-cell diffstat | Defined, never used. |
| `.desk-md` (font `0.9rem`; line height `1.62` after override; `p, li` `max-width: 72ch` after override; `h2`, `h3`, lists, `strong`, `a`, `code`, `table`, `th`, `td`) | rendered PR body markdown | Mockup-only prose styles; tokens from Survey. |
| `.desk-read` (Spectral `1.06rem`; final `line-height: 1.72; max-width: 68ch`; `h1` hidden; `h2` with dashed `--site-rule-color` rule; lists; `strong`; `code`) | design document | Mockup-only; the dashed rule matches Survey's `.site-contour-rule` look. |
| `.desk-triage ...`, `.is-focused` | not used | Dead. |
| `.desk-field { background-color: var(--site-field-bg); border-color: var(--site-field-border); }` | the rejection textarea | Survey's field rules cover `.input` and `.select` but not `.textarea`; this fills that gap. Mockup-only. |
| `html { scroll-padding-bottom: var(--desk-bar-pad, 9rem); }` | keeps focused controls clear of the bar and toast | Mockup-only; JS sets `--desk-bar-pad`. |
| `main[tabindex="-1"]:focus { outline: none; }` | main as a focus landing spot | Mockup-only. |
| `html.desk-no-sk .desk-sk { display: none; }` | hides single-key hints when the switch is off | Mockup-only. |
| `@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition: none !important; animation: none !important; scroll-behavior: auto !important; } }` | motion | Mockup-only. |
| `.desk-glance { background: transparent; overflow: visible; }`, `.desk-glance .stat { border: 0; padding: 0 44px 0 0; row-gap: 2px; }`, `.stat-title { color: var(--color-muted); font-size: 0.8rem; }`, `.stat-value { font-size: 1rem; font-weight: 600; line-height: 1.4; }` | PR figures | Mockup-only override of DaisyUI `stats`; the `overflow: visible` causes the 390 px overflow. |
| `.desk-plain-list > * + * { border-top: 1px solid var(--color-base-300); }` | between body sections | Mockup-only. |

Triage-only rules (in `triage-c2.html`, replacing the last ten lines of the other three):

| Rule | What it styles |
|---|---|
| `.desk-v { list-style: none; }`, `.desk-v > li { display: grid; grid-template-columns: 2rem minmax(0, 1fr) auto; column-gap: 16px; padding: 10px 12px 10px 8px; border-radius: var(--radius-box); }`, `.desk-v > li + li { margin-top: 2px; }`, `.desk-v > li.is-current { background-color: var(--color-base-200); }` | rows |
| `.desk-c > li { grid-template-columns: 2rem minmax(0, 1fr); }` | the two-column row actually used |
| `.desk-v .tb-n`, `.tb-text`, `.tb-reason`, `.tb-was` | number, text, reason line, "was" note |
| `.desk-menu { position: fixed; inset: auto; margin: 0; position-area: none; }`, `.desk-menu [role=menuitemradio] { justify-content: space-between; }`, `.desk-menu .desk-prop { font-size: 0.72rem; color: inherit; opacity: 0.8; }` | the popover menu, placed by script |
| `.desk-group + .desk-group { margin-top: 18px; }`, `.desk-group h2 {...}`, `.desk-group h2 .desk-count {...}`, `.desk-group .desk-empty {...}` | sections |
| `.desk-group[data-group=now] { --desk-hue: var(--cairn-warning-ink); }`, `[data-group=defer] { --desk-hue: var(--color-info); }`, `[data-group=drop] { --desk-hue: var(--color-muted); }` | per-section hue |
| `.desk-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--desk-hue); align-self: center; }` | heading dot |
| `.desk-c > li.is-moved .tb-n { position: relative; }`, `.desk-c > li.is-moved .tb-n::before { content: ""; position: absolute; left: -2px; top: 0.72em; width: 6px; height: 6px; border-radius: 50%; background: var(--desk-hue); }` | moved-row dot |
| `.desk-e .tb-ctl`, `.desk-e .tb-dec` | dead (an earlier variant) |

Because triage lacks the ten override lines, its `.desk-kbd` is bordered and 10 px (others 11.2 px,
borderless, 70% opacity), its `.desk-q-meta` is `0.78rem` (others `0.76rem`), and its `.desk-md` and
`.desk-read` overrides are absent (unused there). Pick one kbd treatment for the build; the PR, design,
and empty mockups (borderless) are three of four.

### Custom properties used

| Property | Defined in `review-desk/src/lib/survey/*.css`? |
|---|---|
| `--color-base-100`, `-200`, `-300`, `--color-base-content`, `--color-primary`, `--color-primary-content`, `--color-secondary`, `--color-info`, `--color-success`, `--color-error` | yes, `theme.css` (DaisyUI theme blocks) |
| `--color-muted` | yes, `theme.css` (custom Survey token) |
| `--cairn-info-ink`, `--cairn-success-ink`, `--cairn-warning-ink`, `--cairn-error-ink` | yes, `theme.css` |
| `--site-field-bg`, `--site-field-border` | yes, `theme.css` |
| `--radius-box`, `--radius-field`, `--border` | yes, `theme.css` |
| `--font-display`, `--font-body`, `--font-mono` | yes, `theme.css` `@theme` |
| `--text-step-1`, `-2`, `-8`, `--text-step-inline-code` | yes, `theme.css` `@theme` |
| `--spacing-1px` ... `--spacing-24px` | yes, `theme.css` `@theme` |
| `--site-contour`, `--site-contour-opacity`, `--site-rule-color` | yes, `components.css` `:root` |
| `--site-alert-ink` | yes, `components.css` (set per `.alert-*`) |
| `--alert-color`, `--input-color` | DaisyUI internals, read or set by `components.css` |
| `--desk-bar-pad` | no; mockup-only, set by script, default `9rem` |
| `--desk-hue` | no; mockup-only, set per triage group |

## Behavior

### Global key handler (shared script)

Order of checks on every `keydown` on `document`:

1. `Escape` while the drawer checkbox is checked: close the drawer (focus returns to `#queue-open`),
   stop.
2. Sheet open (`sheet.open`): stop. The native `<dialog>` handles Esc. So `?` does not close the
   sheet, although the sheet says "Show or hide this sheet".
3. Page handler `desk.handlers.any(e)`: if it returns true, stop. This runs before the typing check,
   so Escape and Ctrl+Enter inside fields reach it.
4. Typing target: stop. "Typing" is `isContentEditable`, `TEXTAREA`, `SELECT`, or `INPUT` whose type
   is not radio, checkbox, button, or submit. A toggle is not a typing target.
5. Single key with the switch off: stop. A single key is `e.key.length === 1` with no Ctrl, Meta, or
   Alt (Shift is allowed, so `?` counts).
6. Dispatch: `?` toggles the sheet; `j` next queue item; `k` previous; `z` undo; else
   `desk.handlers[e.key]` if present and no Ctrl, Meta, Alt.

### Key map

| Key | Where | Does | Suppressed by |
|---|---|---|---|
| `j` / `k` | any page | moves focus to the next / previous queue link; adds `menu-focus`, removes it on blur; clamps at the ends (no wrap); starts from the focused queue link, else from the `aria-current` item; `aria-current` never moves; Enter on the focused link opens it | typing, switch off, sheet open |
| `?` | any page | opens the sheet (`showModal`) | typing, switch off |
| `z` | any page | undo, only while a decision is held | typing, switch off |
| `Esc` | drawer open | closes the drawer, focus to `#queue-open` | nothing |
| `Esc` | sheet | native dialog close | nothing |
| `Esc` | PR/design note field | closes the note, shows Reject/Approve, focus to `#reject` | nothing |
| `Esc` | file filter | clears the filter, re-applies, blurs the input | nothing |
| `Esc` | triage reason input | restores the old reason, closes the edit, focus to the edit button (stops propagation) | nothing |
| `Esc` / `Tab` | triage menu | closes the menu, focus to its "Move to" trigger | nothing |
| `Esc` | empty page | Keep this tab open (handler returns true even after the countdown stopped) | nothing |
| `a` | PR, design | Approve | typing, switch off |
| `r` | PR, design | opens the note (shows `#note-row`, swaps to Cancel/Send), focus to `#note` | typing, switch off |
| `Ctrl+Enter` | PR, design | sends the rejection, but only when focus is in `#note` | sheet open |
| `/` | PR | focuses `#file-filter` | typing, switch off |
| `↑` / `↓` | triage | moves focus to the previous / next row in DOM order (Now rows, then Defer, then Drop), clamped; only when the target is inside `main` and not a typing target; `preventDefault` stops the page scroll | typing, sheet open (not by the switch) |
| `1` / `2` / `3` | triage | moves the row that holds focus (`activeElement.closest('[data-row]')`, so the row, its edit button, or its "Move to" button) to Now / Defer / Drop | typing, switch off |
| `1` / `2` / `3` | triage menu open | picks that disposition (checks `html.desk-no-sk` itself) | switch off |
| `↑` `↓` `Home` `End` | triage menu | move among the three items, wrapping | nothing |
| `Ctrl+Enter` or `Meta+Enter` | triage, anywhere including the reason input | Submit | sheet open |
| `Enter` | triage reason input | keeps the edit (no Ctrl/Meta) | nothing |

Quirk to fix rather than copy: in triage, `↓` with focus outside any row starts from the first row
and steps once, landing on the second row. Another: the `a`, `r`, `1`, `2`, `3` handlers do not check
for a held decision, so a second `a` during the hold calls `decide` again (the buttons are disabled
but the key is not).

### Undo hold

- `desk.decide(text, next, from)`: holds for 5 s. Shows the toast (`#toast-wrap` unhidden, Undo
  shown), sets `#toast-text` to "`text` `where` in `N` s." with `where` "Opening `next.label`" or
  "Closing the queue" when there is no next, and re-renders it every second (5, 4, 3, 2, 1).
  Example: "Approved cairn-cms #113. Opening Review desk (design) in 4 s."
- Focus moves to `#undo` at the start.
- The live region announces once: "Approved cairn-cms #113. Opening Review desk (design) in 5
  seconds. Press z or the Undo button to undo." The per-second text is not in a live region.
- The page locks its controls: PR/design disable `#decision button` and `#note`; triage disables
  `#decision button`, `main button`, `main input`.
- `z` or the Undo button within the hold: clears the timer, hides the toast, re-enables controls
  (`handlers.undone`), announces "Undone. Nothing was sent.", and returns focus to `from` (the
  Approve, Send rejection, or Submit button).
- At 0: Undo hides, the toast text becomes "`text` Opening `label`." and is announced, focus moves to
  `#main` (`tabindex="-1"`, no ring), and the next item loads (`location.href` in the mockup;
  `history.replaceState` client navigation in the design). The decision posts at this point, not
  before.
- Toast text strings: "Approved `subject`.", "Rejected `subject`." or "Rejected `subject` with a
  note." (when the note is non-blank), "Submitted 13 items." Subjects: "cairn-cms #113", "the review
  desk design".

### What a decision loads next

Each page hard-codes `next`: PR to the design, design to the triage list, triage to "workstation #13"
(no mockup). That is the next item in queue order (oldest first), the item below the current one.
There is no wrap; with nothing left the toast says "Closing the queue" and the empty state follows.
The design and PR mockups point at `triage-b.html` (an earlier round) rather than `triage-c2.html`.

### Triage moves

- By key (`1`/`2`/`3`) or menu pick, `moveTo(row, value)`:
  1. Same value: focus the row, nothing else.
  2. Otherwise set `data-value`, re-insert the `li` into the target group's `ol` in item-number order,
     recount every section's `[data-count]`, show or hide each `[data-empty]`, set `[data-was]` to
     "was `Proposed`" when the value differs from the proposal (empty when moved back), toggle
     `is-moved`, sync the menu's `aria-checked` and `menu-active`.
  3. Update `#tb-status` (role=status) to "13 items, N changed from proposed" or "13 items, none
     changed from proposed"; written only when the text changes.
  4. Focus follows the row: roving `tabindex` moves to it (0 on that row, -1 on the rest), it gets
     `is-current`, it scrolls into view (`block: 'nearest'`).
  5. Announce "Item 2 moved to Drop. Drop has 3 items." (`tri.set` also announces "Item N set to X"
     or "..., as proposed"; the second announcement replaces it because `announce` clears and writes
     after 50 ms).
- "Changed from": `span.tb-was#was-N` is referenced by the row's `aria-describedby="was-N"`.
- Menu: a native popover. Opening sets the trigger's `aria-expanded="true"`, places the menu with JS
  (fixed, right-aligned to the trigger, 4 px below; flipped above the trigger if it would reach within
  8 px of the decision bar; clamped 8 px from the viewport edges), and focuses the checked item. Light
  dismiss is the popover default. Picking closes the menu and runs `moveTo`, so focus goes to the
  moved row, not back to the trigger.
- Reason edit in place: "Add a reason"/"Edit reason" hides the reason text and both buttons, shows the
  input, focuses and selects it. Enter or blur keeps; Escape restores. Closing writes the text (or
  the italic "No reason given."), renames the button and its `aria-label`, and returns focus to the
  button. No announcement.

### Path filter (PR)

- Input event, term = trimmed, lower-cased value; a row matches when `data-path` (stored lower case)
  contains the term as a substring. Case-insensitive; no glob.
- Non-matching `li[data-path]` get `hidden`; a group with no hits is hidden; groups with hits open
  while a term is set; clearing restores each group's remembered open state.
- Each group count reads "`n` of `N` files" while filtering, else "`N` file(s)".
- `#file-summary` (role=status) reads "`n` match(es) in `m` group(s)", for example "2 matches in 1
  group" for "Sanitize", else the original "161 in 10 groups". It updates on every input event.
- `#no-match` (role=status) unhides "No file path matches that filter." when nothing matches.
- "Open all groups" / "Close all groups" toggles every visible group and records the state.

### Diffs in place

Each file is its own `<details>` with no `name` attribute, so any number can be open at once; nothing
closes another. Diffs are in the markup up front (no lazy load in the mockup).

### Empty state

- On load with auto-close on: `#secs` shows 30, Keep is shown and focused, and the live region
  announces once "Nothing waiting. This tab closes in 30 seconds. Press Escape or Keep this tab open
  to stop it." The number then counts down each second in `#secs`, which is not a live region.
- At 0: `#close-line` reads "Closing this tab. (The mockup stays open.)"; the build calls
  `window.close()`.
- Keep (button or Esc): stops the timer, sets `#close-line` to "This tab stays open.", hides Keep,
  announces the same text.
- Toggle "Close when empty" off: saves `desk.autoClose=off`, and if counting, stops with "Auto-close
  is off. This tab stays open." Turning it back on saves `on` but does not restart the count.
- Loaded with the setting off: no count, `#close-line` "Auto-close is off. This tab stays open.",
  Keep hidden, no focus move, no announcement.
- The 30 s is more than the 20 s floor the review asked for.

### Drawer (below `lg`)

`#queue-open` click: checks the drawer, sets `aria-expanded="true"`, and focuses the first queue link
(`[data-q]`), or `#open-keys` when the queue is empty, retrying each animation frame up to 60 times
because the panel becomes visible part way through DaisyUI's transition. Overlay click or Escape:
unchecks, sets `aria-expanded="false"`, focuses `#queue-open`. No focus trap.

### Scroll padding

`--desk-bar-pad` = `#decision` height + 72 px, kept current by a `ResizeObserver`; read by
`html { scroll-padding-bottom }`. Default `9rem` when there is no bar.

### localStorage

| Key | Values | Read where |
|---|---|---|
| `desk.singleKeys` | `on`, `off` (absent means on) | every page; toggles `html.desk-no-sk` and the sheet switch |
| `desk.autoClose` | `on`, `off` (absent means on) | empty page |

Both reads and writes sit in `try {}`.

### Live regions

| Element | Kind | Announces |
|---|---|---|
| `#sr-status` | `div.sr-only role=status aria-live=polite`, present and empty at load | every `desk.announce(msg)`: decision held, final toast text, "Undone. Nothing was sent.", triage moves, empty-state start and stop. `announce` blanks the text, then writes after 50 ms, so a repeat message is re-read. |
| `#queue-count` | `aria-live="polite"` | static in the mockup; would announce if the count text changed |
| `#file-summary` | `role="status"` | filter result counts |
| `#no-match` | `role="status"` | the no-match line |
| `#tb-status` | `role="status"` | the triage tally |

### Focus moves, all

- Decision: to `#undo`; after undo, back to the button that decided; after the hold, to `#main`.
- `r`: to `#note`; Esc or Cancel: to `#reject`.
- `/`: to `#file-filter`; Esc there: blur.
- j/k: to the queue link.
- Drawer open: first queue link (or `#open-keys`); close: `#queue-open`.
- Triage arrows: the row; move: the moved row; menu open: the checked item; menu Esc/Tab: the trigger;
  menu pick: the moved row; reason edit: the input, then back to the edit button.
- Empty page load: `#keep`.

## Accessibility carry-over (the fifteen findings of 2026-10-11)

| # | Finding | How the approved mockup handles it |
|---|---|---|
| 1 | Single-key shortcuts need an off switch (2.1.4) | Handled. `input#single-keys.toggle.toggle-sm.toggle-primary` in the sheet, saved as `desk.singleKeys`; with it off every printable key without a modifier is ignored and `html.desk-no-sk .desk-sk { display: none; }` hides their hints. |
| 2 | Enter submitting triage from anywhere (2.1.1), now Ctrl+Enter | Handled. `if (e.key === 'Enter' && (e.ctrlKey \|\| e.metaKey)) { e.preventDefault(); submit(); return true; }`; plain Enter only commits a reason edit. Ctrl+Enter also fires from inside a reason input. |
| 3 | Empty-state auto-close: at least 20 s, focus on Keep, a setting to turn it off (2.2.1) | Handled. `let s = 30`, `keepBtn.focus()`, Esc keeps, and `input#auto-close` "Close when empty" saved as `desk.autoClose`. The setting lives on the empty page, not in the sheet. |
| 4 | Toast live region hidden at start and re-rendered every second | Handled. `<div class="sr-only" role="status" aria-live="polite" id="sr-status"></div>` is always present; one announcement per decision; the per-second `#toast-text` is outside it, inside the hidden-then-shown `#toast-wrap`. |
| 5 | Focus after a decision goes to Undo, and back after undo | Handled. `undoBtn.focus()` in `decide`; `returnTo && returnTo.focus()` in `undo`; `#main` focus after the hold. |
| 6 | j/k move focus only (`menu-focus`), not `aria-current` | Handled. `q.forEach((a, i) => a.classList.toggle('menu-focus', i === qi)); q[qi].focus();`; comment "aria-current stays on the open item". |
| 7 | Triage 1/2/3: roving focus on each row's checked radio, "Changed from" by aria-describedby, tally as a live region | Partly reshaped. There are no radios in the approved triage; roving `tabindex` sits on the row `li` (`tabindex="0"` on one row, `-1` on the rest, moved by `focusRow`). "Changed from" is `span.tb-was#was-N` referenced by `aria-describedby="was-N"`. Tally: `p#tb-status role="status"`. |
| 8 | Sticky bar and toast hiding focus: scroll-padding-bottom | Handled. `html { scroll-padding-bottom: var(--desk-bar-pad, 9rem); }` with the bar height + 72 px from a `ResizeObserver`. The toast sits at `bottom-24` (96 px) and is about 46 px tall, so its top is near 142 px from the viewport bottom against a pad of about 136 px; worth a check in the build. |
| 9 | Drawer toggle `aria-label="Queue"`, focus first queue link on open, Escape closes | Handled. `input#queue-toggle ... aria-label="Queue" tabindex="-1"`; the visible control is `button#queue-open aria-controls="queue-nav" aria-expanded`; `focusIn` targets `q[0]`; Escape calls `setDrawer(false)`. |
| 10 | Path filter results `role="status"` | Handled. `span#file-summary role="status"` and `p#no-match role="status"`. |
| 11 | Reason inputs `aria-label="Reason for item N"` | Handled. `aria-label="Reason for item 4"` on every `[data-reason-input]`. |
| 12 | Mobile navbar inside `<header>` | Handled. `<header class="navbar min-h-12 border-b border-base-300 bg-base-200 px-3 lg:hidden">`. |
| 13 | Toast uses `alert-info`, not `alert-success`, for a rejection | Handled. `div.alert.alert-info` for every decision. |
| 14 | Countdown could use DaisyUI `countdown` | Not handled in the mockup: `<span id="secs" class="tabular-nums font-semibold">30</span>`. |
| 15 | Diff tables have no caption or `aria-label` | Not handled in the mockup: `<table class="desk-diff">` carries neither. |

## In the mockup, not in the design

- The "Decided this session" list in the queue column, with each item's outcome.
- The queue header's contour texture and benchmark triangle, and the `site-collar` footer
  "127.0.0.1:7907 / Survey".
- The "j k next and previous" hint row in the queue footer (triage only).
- The item header meta line (repo, branch, GitHub link; file name and "3 min read"; the Triage badge
  and item count).
- The kind badge in queue rows (triage mockup only; the others use plain text).
- PR: the stat labels read Risk, Checks, Review, Changes (the design says class, checks, review,
  files); three stats are links to their sections.
- PR: the checks list in two columns with "skipped" right-aligned; the review verdict table with
  notes; the "What landed" body section open by default.
- PR: "Open all groups" / "Close all groups"; per-group and per-file `+N −N` counts; "new" and
  "deleted" badges on files; the "Repository root" group name; hunk header rows; old and new line
  number gutters; the `/` kbd inside the filter; Escape clears the filter.
- PR and design: the guard text in the decision bar ("Checks passed. Nothing is blocking.",
  "Approved in the doc on 2026-10-11, scoped to lean v1."); the rejection note label "(optional; the
  session reads it as the reason)" and placeholder; Cancel and Send rejection buttons.
- Design: the document's own `h1` hidden in favour of the page header.
- Triage: the hint line above the sections; "Nothing here." for an empty section; the "proposed"
  marker inside the menu; "Add a reason" vs "Edit reason" and the italic "No reason given."; the
  "was Now" text; the moved-row dot by the item number.
- Empty: "New items open in their own tab."; the toggle label "Close when empty" on the page.
- The undo toast's wording, its per-second count, and the "Closing the queue" text when nothing is
  next.
- The reduced-motion rule.

## Mockup and design disagreements

- Before merge: the design wants a `## Before merge` warning above Approve; the PR mockup has none.
- Color where it means something: the design names a failing check and a blocking verdict; the PR
  mockup has neither case, so their treatment is unspecified.
- `?` "Show or hide this sheet": the script cannot hide it with `?` (the sheet-open guard returns
  first); only Esc, Close, or the backdrop close it.
- The sheet lists `/` under "PR and design"; the design page has no file list.
- Ctrl+Enter for the rejection works only with focus in the note field.
- The PR mockup scrolls sideways at 390 px (the figures row).
- The kbd style differs in triage (bordered) from the other three (borderless).
