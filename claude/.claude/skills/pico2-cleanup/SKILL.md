---
name: pico2-cleanup
description: Audit ops dashboard CSS for Pico CSS v2 anti-patterns and propose fixes
---

Audit the ops dashboard inline CSS for Pico CSS v2 anti-patterns, report findings, and propose fixes.

## Scope

**File:** `ops/src/templates/layout.js` — the single inline `<style>` block (approximately lines 40-595).

This audit checks CSS **only**. It does not modify HTML structure, JavaScript, or other template files.

## Setup

1. Read `ops/src/templates/layout.js` in full.
2. Extract the content between `<style>` and `</style>` tags for analysis.

## Anti-Pattern Checks

Run these checks in order. For each finding, record the CSS line content, the rule it violates, and a proposed fix.

### Check 1: Direct property assignments on Pico-styled elements

**What to find:** `background:`, `background-color:`, `border-color:`, `color:`, `border:` used as **direct CSS properties** (not variable assignments) on selectors that target `button`, `input`, `select`, `textarea`, `a[role="button"]`, `[role="button"]`, or elements Pico auto-styles.

**Exempt:** Properties inside blocks tagged `CUSTOM` that target non-Pico elements (`.badge`, `.drag-handle`, custom app classes). Status badges, payment icons, and other app-specific elements are not Pico-styled and may use direct colors.

**Correct pattern:** Override via `--pico-background-color`, `--pico-border-color`, `--pico-color`, etc.

**Example violation:**
```css
/* BAD */
button.foo { background-color: #16a34a; }
/* GOOD */
button.foo { --pico-background-color: #16a34a; }
```

### Check 2: Specificity fights on `:root` variable overrides

**What to find:** `--pico-*` variable declarations inside a plain `:root { }` block (specificity 0,1,0).

**Why it matters:** Pico's blue precompiled theme sets variables at `:root:not([data-theme=dark])` (specificity 0,2,0). A plain `:root` override loses silently.

**Correct pattern:**
- Light mode: `:root:not([data-theme=dark]), [data-theme=light] { --pico-var: value; }`
- Dark mode: `[data-theme=dark] { --pico-var: value; }`
- Theme-independent (both modes): A plain `:root` is acceptable **only** for variables that should apply regardless of theme AND that Pico does not set in its theme-specific selectors (e.g., `--pico-spacing`, `--pico-border-radius`, `--pico-form-element-spacing-vertical` which Pico sets at `:root` not in theme selectors).

**How to distinguish:** Check if the variable being set is one Pico defines inside `:root:not([data-theme=dark])` (color-related: `--pico-muted-color`, `--pico-primary`, `--pico-color`, `--pico-background-color`, etc.) vs. one Pico defines at plain `:root` (spacing, radius, line-height). Only color/theme variables need the higher-specificity selector.

### Check 3: `!important` overriding Pico

**What to find:** Any `!important` declaration where the property targets a Pico-styled element or overrides a `--pico-*` variable.

**Exempt:** `!important` on:
- CUSTOM-tagged blocks for app-specific elements (e.g., `.notes-panel-cell` padding reset)
- Non-Pico contexts where specificity from third-party or browser defaults genuinely requires it

**For each hit:** Determine if a higher-specificity selector or Pico variable would work instead.

### Check 4: Uncatalogued PICO-EXTENSION / PICO-OVERRIDE blocks

**Process:**
1. Parse the upgrade checklist comment (top of `<style>` block) for all listed extensions and overrides.
2. Scan the full CSS for all `PICO-EXTENSION` and `PICO-OVERRIDE` comment tags.
3. Cross-reference: report any CSS-tagged blocks **missing from** the checklist, and any checklist items with **no matching CSS tag**.

### Check 5: Hardcoded colors where a `--pico-*` variable exists

**What to find:** Hex (`#xxx`), `rgb()`, or `hsl()` color values used for semantic purposes where an equivalent `--pico-*` variable exists.

**Common substitutions:**
- Primary blue → `var(--pico-primary)`
- Primary hover → `var(--pico-primary-hover)`
- Muted text → `var(--pico-muted-color)`
- Border → `var(--pico-muted-border-color)`
- Background → `var(--pico-background-color)`
- Card section bg → `var(--pico-card-sectioning-background-color)`

**Exempt:**
- Semantic action colors (green `#16a34a`, red `#dc2626`) in `PICO-EXTENSION` button variants — these are intentionally hardcoded because Pico has no success/danger color system
- Status badge colors (the entire `CUSTOM` badge block) — app-specific, no Pico variable maps to these
- `rgba()` used for opacity variations (e.g., box-shadows, semi-transparent borders)
- `hsl()` values in the `PICO-OVERRIDE` muted-color block (these ARE the override values)

### Check 6: Missing `margin-bottom: 0` on buttons in compact contexts

**What to find:** Buttons used inside table cells, nav bars, card headers, `[role="group"]` containers, or flex layouts where Pico's default `margin-bottom: 1rem` would break alignment.

**Check selectors:** Any `button` or `[role="button"]` styled for compact use (table actions, nav icons, reorder buttons, icon-only buttons) — verify they either set `margin-bottom: 0` directly or inherit it from a parent rule that zeros it (e.g., `table td > [role="group"] { margin-bottom: 0; }`).

### Check 7: Nonexistent `--pico-*` variable names

**What to find:** References to `var(--pico-*)` where the variable name does not exist in Pico CSS v2.

**Known valid variables (non-exhaustive):**
- `--pico-spacing`, `--pico-border-radius`, `--pico-border-width`, `--pico-line-height`
- `--pico-color`, `--pico-background-color`, `--pico-muted-color`, `--pico-muted-border-color`
- `--pico-primary`, `--pico-primary-hover`, `--pico-primary-background`, `--pico-primary-border`, `--pico-primary-inverse`
- `--pico-primary-underline`, `--pico-primary-hover-underline`
- `--pico-card-background-color`, `--pico-card-border-color`, `--pico-card-sectioning-background-color`
- `--pico-table-border-color`
- `--pico-form-element-border-color`, `--pico-form-element-spacing-vertical`, `--pico-form-element-spacing-horizontal`
- `--pico-tooltip-background-color`, `--pico-tooltip-color`
- `--pico-box-shadow`

**If a variable looks plausible but is not on this list:** Flag it for manual verification against the Pico v2 source. Do not auto-fix — silent fallback to browser default is worse than a false positive.

## Report Format

Present findings grouped by check number, in priority order:

```
## Pico v2 CSS Audit — ops/src/templates/layout.js

### Check 1: Direct property assignments
[findings or "Clean — no issues found"]

### Check 2: Specificity fights
[findings or "Clean — no issues found"]

### Check 3: !important overriding Pico
[findings or "Clean — no issues found"]

### Check 4: Upgrade checklist sync
[findings or "Clean — checklist matches CSS tags"]

### Check 5: Hardcoded colors
[findings or "Clean — no substitutable colors found"]

### Check 6: Missing margin-bottom: 0
[findings or "Clean — all compact buttons covered"]

### Check 7: Nonexistent variable names
[findings or "Clean — all variable names valid"]

---

**Summary:** X issues found across Y checks. Z are high priority.
```

For each finding, include:
- The CSS rule (quoted)
- Why it is an anti-pattern
- Proposed fix (show before/after)
- Priority: **high** (silent breakage or specificity loss), **medium** (maintainability/consistency), **low** (stylistic)

## After Reporting

1. Present the full report.
2. Ask for approval before making any changes.
3. If approved, apply fixes to `ops/src/templates/layout.js` one check at a time, showing each change.
4. After all fixes, update the upgrade checklist comment if any PICO-EXTENSION/PICO-OVERRIDE tags were added or removed.
5. Do NOT deploy. The user will deploy when ready.
