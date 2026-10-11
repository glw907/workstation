---
name: bubbletea-design
description: >-
  Use when building or modifying bubbletea terminal UI components,
  diagnosing TUI rendering or alignment issues, or reviewing TUI
  layout code for visual correctness. Also use when choosing icons,
  spacing, box-drawing characters, or theme-driven color decisions
  for terminal interfaces.
---

# Bubbletea TUI Design

Design thinking and verification for terminal UIs. Every layout
decision is verifiable. Render first, then fix. Never guess.

## Sources and Departures

Structure, update flow, and width math follow `elm-conventions`, which
rests on Charm's agent guide for the Crush UI
(`https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md`).
Where this skill states a width or ANSI rule it cites that guide. The
visual language below (theme slots, hue budget, box-drawing, density,
iconography) is a House departure: Charm's guide has no visual-design
section, so these rules are the house's own and each is checked against
the real terminal.

## Verify in the Real Terminal

Launch the real terminal and look at what it paints with
`tui-visual-verify`, which owns the capture harness, the resize rungs,
and the fresh-context grading. The headless modes below support that
look; they never replace it.

## TUI Design Language

### Theme-Driven Design

All color decisions reference semantic theme slots (`accent_primary`,
`fg_dim`, `color_error`), never hex values or raw ANSI codes. Every
visual distinction must survive a theme swap.

**Theme survival test:** If two elements differ only by hue, they
collapse when the palette changes. Differentiate by semantic role,
not specific color. Ask: "does this distinction survive switching
from Nord to Solarized?" If not, the design relies on a palette,
not the semantic system.

### Nerd Font Iconography

Nerd Font families have different visual weight and cell widths.
Some icons render as double-width despite being a single codepoint.

Rules:
- Verify icon width with `ansi.StringWidth()`, never `len()` or rune
  count, and confirm it in the real terminal: a glyph's cell width can
  depend on the font (Charm guide L12-18 for the ANSI-safe helpers)
- Match icon visual weight to element importance. A heavy icon on a
  de-emphasized element creates noise.
- Material Design (`nf-md-*`) has the broadest coverage for
  application UIs
- Prefer one icon family per component for visual consistency

### Character Cell Realities

Every glyph occupies 1 or 2 cells. Width assumptions are the #1
source of alignment bugs. Box-drawing characters are always
single-width. CJK, some emoji, and certain Nerd Font icons are
double-width.

**The rule:** All padding and alignment uses display width
(`ansi.StringWidth`, per `elm-conventions` Rule 6), never string length
or rune count. A column
that looks aligned in code may be ragged on screen.

### Box-Drawing Vocabulary

| Family | Characters | Use |
|--------|-----------|-----|
| Single-line | `│ ─ ┬ ┴ ├ ┤ ┼` | Structural borders, panel dividers |
| Rounded | `╭ ╮ ╰ ╯` | Floating elements (tab bubbles, cards) |
| Double-line | `║ ═ ╔ ╗ ╚ ╝` | Heavy emphasis, dialog borders |

Mix families intentionally. Junction connections are the
highest-priority verification target. Every `─` meeting a `│` must
use the correct T-junction or corner piece.

When mixing families (rounded corners meeting single-line frame),
verify that Unicode has the transition glyph. Not all combinations
exist. Some junctions require creative spacing or family consistency
within a region.

### Information Density

The grid is finite. Every cell earns its place. Create visual
layers through theme contrast:

- `fg_bright`: primary information (active tab, selected item)
- `fg_base`: secondary information (body text, labels)
- `fg_dim`: tertiary information (timestamps, read messages)

Bold and underline as texture, not emphasis. Emphasis comes from
color role.

Blank lines cost a full row. Use them deliberately as group
separators, not as filler. Horizontal rules (`─`) separate regions
without consuming a blank line.

### Hue Budget

**Encode state by brightness, not hue. Reserve hue for the one or
two things that need to pop.**

A row in a list (message list, file picker, log viewer) typically
needs to express several distinctions at once: selection, read/unread,
priority/flag, type. The temptation is to give each distinction its
own color (teal for unread, orange for flagged, purple for answered,
blue for cursor). Four hues per row on a muted background fragments
attention. No single element wins the eye, and the whole list reads
as garish even though every individual choice felt principled.

Rules:

1. **Two hues max per row.** Pick the row's most attention-worthy
   state and spend hue on that. Everything else encodes by brightness
   (`fg_bright` vs `fg_base` vs `fg_dim`), bold, or glyph identity.
2. **Read state wins over flag state for color.** If the user has
   already seen and acknowledged an item, dim it completely, including
   the flag glyph. Only the *unread + important* combination earns
   the accent color, so it pops as the single must-handle row.
3. **Glyphs carry distinctions colors don't need to.** A `󰈻` flag
   icon and a `󰑚` reply icon are already visually distinct. They
   don't need different hues. Color the row by importance, not by
   which icon it happens to show.
4. **Brightness alone is enough signal for read/unread.** Apple
   Mail, Fastmail, Gmail, and Mutt all encode read state by
   brightness or weight, not hue. Brightness leaves the hue budget
   free for cursor, selection, and the one or two states that
   demand action.

This is Tufte's data-ink principle applied to color: spend ink (hue)
on the data that demands attention, withhold it everywhere else.
When everything is highlighted, nothing is.

**Test it:** look at a screen full of rows. Can you instantly point
to the most attention-worthy one? If the answer is "no, several
things compete," your hue budget is over-spent.

### Spatial Composition

- `lipgloss.JoinHorizontal`/`JoinVertical` for panel layout
- Dividers connect to borders (verify junction checks)
- Floating elements break the grid intentionally
- Alignment columns create vertical rhythm: a divider position
  must be consistent from header through content to footer
- `lipgloss.Place` for centering within a region

### Aesthetic Intentionality

Commit to a direction and execute precisely. The choice shapes
every spacing, icon, and density decision. "Better Pine",
brutalist terminal, maximalist dashboard, minimal zen. Pick one
and follow through.

Don't mix aesthetics. A rounded-corner bubble tab bar with a
brutalist status line creates visual dissonance.

## Headless Analysis Protocol

Three modes for inspecting TUI layout.
This is the defined method that prevents "guess and ship."

### Mode 1: Render-and-Inspect

Structural correctness: connections, alignment, borders.

```
1. Instantiate model with known dimensions (e.g., 80x24)
2. model.View() -> strip ANSI:
   regexp: \x1b\[[0-9;]*[a-zA-Z]
3. Split into lines, iterate as rune slices
4. Positional checks:
   - Junction: ┬ on row N aligns with │ on rows N+1..M
   - Border continuity: every content row ends with same char
   - Column alignment: elements line up across rows
   - Width: ansi.StringWidth(line) == expected terminal width
```

Write checks as Go test assertions. This is the regression safety
net.

**When:** After any layout code change. Always.

For golden-file assertions on a rendered `View()` string,
`github.com/charmbracelet/x/exp/golden` is the light option. For
full-program assertions, `teatest/v2`
(`github.com/charmbracelet/x/exp/teatest/v2`) runs the whole tea
program against in-memory buffers. Both live under `x/exp` with no
tagged releases, so treat the API as movable. Pin terminal size and
color profile in every golden test, or the files flap in CI.

### Mode 2: Render-and-Snapshot

Aesthetic judgment: spacing, density, feel.

Same render + strip pipeline. Paste the stripped plain-text grid
(or relevant rows) into the conversation. Scan for ragged
alignment, inconsistent padding, visual weight imbalance.

**When:** Building a new component, user reports a visual issue,
or positional checks pass but something looks off.

### Mode 3: Real Terminal

The running binary in a real terminal is the primary reference. Look at
what the user sees, through `tui-visual-verify`; reference the painted
screen, not wireframes, code, or text captures, when discussing issues.

**When:** Always. This is the default mode.

### Priority

The real terminal is the source of truth. Start with Mode 3. Use Mode 1
for structural regression tests and Mode 2 when you need to count cells
precisely. Never reason about the layout from code alone when the binary
can be run.

## Iteration Loop

```
Identify -> Analyze -> Fix -> Verify -> Report
```

**Analyze before touching code.** Know exactly what character is
at what position and why.

Good: "Row 3 has `─` at column 30 where `┬` is expected because
`dividerCol` is off by one."

Bad: "The lines look wrong."

**Verify with the same mode that found the issue.** If Mode 1 found
it, run the test again. If Mode 2 found it, paste the new grid.
Never skip verification.

**Report matched to context:**
- Verification summary (terse) when confirming a fix
- Visual snippet when the user needs to see the layout
- Both when closing out a visual issue

### Red Flags: Stop

| Thought | Reality |
|---------|---------|
| "I'll just change this character" | Render first. Know what's there now. |
| "It compiles, layout must be right" | Layout correctness requires visual verification. |
| "Looks fine at 80 columns" | Also check 120 and minimum viable (40). |
| "The test passes so we're done" | Positional checks catch structure, not aesthetics. Use Mode 2. |
| "I can see from the code it'll work" | Render it. Code-reading is not verification. |

Every row in this table is a rationalization that led to a
multi-attempt fix in practice. The chrome shell tab bar took 3
iterations because of "I can see from the code it'll work."

## Quality Checklist

Verify on any component before declaring it done:

- [ ] **Junction connections**: every `─` meeting `│` has the correct
  T-junction or corner piece
- [ ] **Border continuity**: edge characters are consistent across
  all content rows
- [ ] **Column alignment**: divider position is consistent from
  header through footer
- [ ] **Width budget**: `ansi.StringWidth(line)` matches the expected
  terminal width for every row
- [ ] **Theme survival**: visual distinctions hold across palette
  swaps (not just the active theme)
- [ ] **Icon width**: measured with `ansi.StringWidth()`, not rune
  count or `len()`
- [ ] **Minimum viable width**: no crash or garble at 40 columns
- [ ] **Nerd Font weight**: icons match element importance, not
  arbitrary selection
- [ ] **Whitespace budget**: every padding space and blank row is
  deliberate, not default
