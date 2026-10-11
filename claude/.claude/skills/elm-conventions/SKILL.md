---
name: elm-conventions
description: >
  Mandatory rules for Bubble Tea v2 UI code in Go. Use before writing,
  reviewing, or modifying any bubbletea tea.Model, Update, View, or Cmd.
  Keeps the tea loop predictable and auditable: one top-level model,
  components as plain structs with imperative methods, mutations only in
  Update, I/O only in tea.Cmd, shared state hoisted to the root.
---

# Elm Architecture Conventions (Bubble Tea v2)

Rules for the UI layer of a Bubble Tea v2 program. They rest on Charm's
own agent guide for the Crush UI, pinned at one commit:

- The Charm guide: `https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md`
  (FSL-1.1-MIT; cited by line, never copied).
- Secondary sources: the Bubble Tea v2 announcement,
  `https://github.com/charmbracelet/bubbletea/discussions/1374`, and the
  v2.1.0 release, `https://github.com/charmbracelet/bubbletea/releases/tag/v2.1.0`.

Every rule below names the source it follows. Where the house differs
from Charm or Charm is silent, the rule carries a "House departure" line
that says why. Charm wins any conflict a House departure does not record.

## Scope

Applies to code that runs inside the tea loop: models, components,
`Update`, `View`, and `tea.Cmd` constructors. It does not apply to
backend adapters, worker goroutines, stdin/stdout filters, or the
bootstrap wiring that runs before `tea.NewProgram`; goroutines and
mutexes are normal there.

Existing nested-model code (poplar's `internal/ui/`, for one) migrates in its repo's own refactor pass; new code follows these rules now.

## Rule 1: One Model, Components Are Plain Structs

Source: `https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md`, lines 8 ("do not nest models"), L58-77.

The root is the only type that implements `tea.Model`. Every other
component is a struct with imperative methods that the root calls
directly. A method that needs a side effect returns a `tea.Cmd`. The
component renders through `Render(width int) string` or a draw method,
and the root decides when and how to call it.

Keep routing, focus, layout, and dialog orchestration in the root. No
package-level mutable variables and no singletons.

Components from the bubbles module (`textarea`, `viewport`, `list`) are
held as fields on the root or on a component, and their `Update` is
called explicitly by the code that owns them. That is delegation to a
library type, not a nested model of your own.

**Right:**
```go
type Sidebar struct {
    folders []Folder
    cursor  int
    width   int
}

func (s *Sidebar) MoveCursor(delta int)  { /* clamp and set */ }
func (s *Sidebar) Selected() Folder      { return s.folders[s.cursor] }
func (s *Sidebar) Render(width int) string { /* ... */ }
```

**Wrong:**
```go
var currentFolders []Folder // package-level mutable state

func (s Sidebar) Update(msg tea.Msg) (Sidebar, tea.Cmd) // a second model
```

## Rule 2: Update Is the Only Mutation Point

Source: `https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md`, lines 10-11 ("Never change the model state inside of a
command").

State changes in the root's `Update` and in the methods it calls. `View`
and `Init` never mutate, and a `tea.Cmd` closure never touches the
model: it computes a result and returns a message, and `Update` applies
it.

**Right:**
```go
case foldersLoadedMsg:
    m.sidebar.SetFolders(msg.folders)
    return m, nil
```

**Wrong (mutation in a Cmd closure):**
```go
func fetchFolders(s *Sidebar, b Backend) tea.Cmd {
    return func() tea.Msg {
        s.folders, _ = b.ListFolders() // races the render loop
        return nil
    }
}
```

**Wrong (mutation in View):**
```go
func (m App) View() tea.View {
    m.lastRendered = time.Now()
    return tea.NewView(m.render())
}
```

### The one recorded exception: a `tea.WithFilter` input coalescer

House departure: Charm's guide does not address program filters, and
the house permits exactly one pure shape.

A program-construction `tea.WithFilter` may collapse a burst of input
messages before they reach `Update`; the motivating case is mouse-wheel
input, where an unfiltered burst costs one store round trip per tick.
The filter samples over a short window (about 16 ms), accumulates signed
deltas, resets on a direction change, and emits one message per burst.

It is legal only because it is pure: no model state, no decision the
model could make differently, message volume changed rather than
meaning. A filter that reads model state, drops messages conditionally
on application state, or performs I/O violates Rules 2 and 3. Record
the window and reset semantics where the program is constructed, since
the filter sits outside the loop a reader follows.

## Rule 3: I/O Only in tea.Cmd

Source: `https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md`, lines 9 ("Never do IO or expensive work in `Update`").

Blocking calls (backend methods, file and network I/O) run inside a
`tea.Cmd`, never in `Update` or `View`. `Update` returns at once.
Prefer a method on the owning type that returns the `tea.Cmd` over an
inline closure (Charm guide L222).

**Right:**
```go
case folderSelectedMsg:
    return m, fetchHeaders(m.backend, msg.name)

func fetchHeaders(b Backend, folder string) tea.Cmd {
    return func() tea.Msg {
        headers, err := b.FetchHeaders(folder)
        if err != nil {
            return errMsg{err}
        }
        return headersLoadedMsg{headers}
    }
}
```

**Wrong:**
```go
case folderSelectedMsg:
    headers, _ := m.backend.FetchHeaders(msg.name) // blocks the UI
    m.headers = headers
```

### Cmd closures capture values, not pointers

Source: follows from Charm guide L10-11.

A closure runs after `Update` returns, so a captured pointer to the
model reads stale or concurrently mutated state. Extract the values the
command needs before returning it, as `fetchHeaders(m.backend,
msg.name)` does above. A closure that reads `m.activeFolder` at run
time is the wrong form.

## Rule 4: Mutate Children Directly, Reserve Messages for Results

Source: `https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md`, lines 5-6 ("Never use commands to send messages when you
can directly mutate children or state"), L71-77.

The root calls the child and reads what it needs from the child's
return values or accessors. A child never sends a message to its parent
to report a state change the parent can observe by calling it.

Messages exist for work that finishes outside `Update`: results of a
`tea.Cmd`, terminal events, and timers. A message type that only
carries a child's state up to its parent is the pattern to remove.
Callbacks stored in a child and parent pointers are also out; they
couple the child to its caller.

**Right:**
```go
case tea.KeyPressMsg:
    if key.Matches(msg, m.keys.Open) {
        folder := m.sidebar.Selected()
        return m, fetchHeaders(m.backend, folder.Name)
    }
```

**Wrong:**
```go
// child emits a command whose only job is to tell the parent
return s, func() tea.Msg { return folderSelectedMsg{s.Selected().Name} }

type Sidebar struct {
    onSelect func(string) // callback couples child to parent
}
```

## Rule 5: State Ownership, Not Duplication

Source: `https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md`, lines 49-54 ("Keep most logic and state here").

House departure: Charm's guide names the root as the owner but gives no
rule for read-only dependencies; this rule adds one.

Shared state lives in the root and reaches children as method arguments
or constructor parameters. A child holds only data it controls
exclusively. A child may keep a reference to a read-only dependency (a
backend handle) when it builds `tea.Cmd` values that call it; it never
mutates the dependency or caches its results as owned state. Results
return as messages through the normal `Update` flow.

**Right:**
```go
type App struct {
    backend Backend // owned by the root
    styles  Styles  // computed once, read-only
    sidebar Sidebar
}

func (m App) View() tea.View { return tea.NewView(m.sidebar.Render(m.styles, m.sidebarWidth)) }
```

**Wrong:**
```go
type Sidebar struct{ backend Backend } // each child holds its own copy
type MsgList struct{ backend Backend } // who is authoritative?
```

## Rule 6: Components Own Their Size Contract

Source: `https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md`, lines 219 ("Always account for padding/borders in width
calculations"), L12-18 (ANSI-safe width).

House departure: Charm's guide states the width rules but not the
exact-size contract below. The contract is the house's, and it is
stricter than Charm's.

A component's render returns content at exactly its assigned width and
height, no wider and no taller. The parent joins the pieces and trusts
them; a child that overflows makes the joined output exceed the
terminal, the terminal soft-wraps, and neighbors are displaced. That is
always the child's bug, never the parent's.

- Enforce the contract inside the child: pad to the width and height,
  truncate past them (lipgloss `Width`, `Height`, `MaxWidth`,
  `MaxHeight`, or an equivalent helper).
- A renderer that takes a width returns lines no wider than it. Pair
  `ansi.Wordwrap` with `ansi.Hardwrap`: wordwrap alone lets a single
  long URL or token overflow.
- Measure with `ansi.StringWidth`, never `len()` or a rune count.
  Wide glyphs (CJK, emoji, some Nerd Font icons) occupy two cells, and
  a glyph's width can depend on the terminal font, so confirm icon
  widths in the real terminal with `tui-visual-verify`.
- A parent-side `MaxWidth` clip around a child's output papers over a
  contract violation. Fix the child.
- On `tea.WindowSizeMsg` the root stores the dimensions, computes
  chrome margins, and calls `SetSize(w-wm, h-hm)` on each sized
  component. A bubbles model held as a field also receives the message
  through its own `Update`, because `SetSize` alone does not reset its
  internal scroll and cursor state.

**Right:**
```go
func (c Component) Render(width, height int) string {
    out := c.compose(width)
    return lipgloss.NewStyle().Width(width).Height(height).
        MaxWidth(width).MaxHeight(height).Render(out)
}

func render(text string, width int) string {
    return ansi.Hardwrap(ansi.Wordwrap(text, width, ""), width, false)
}
```

**Wrong:**
```go
text = ansi.Wordwrap(text, width, "") // a long URL overflows

// parent clipping a child that ignores its width
child := lipgloss.NewStyle().MaxWidth(m.width).Render(m.child.Render(m.width))
```

## Rule 7: Key Bindings via `key.Binding` and `key.Matches`

Source: none in Charm's guide; the bubbles `key` package is the
mechanism.

House departure: Charm's guide says nothing about key dispatch. The
house declares actionable keys as `key.Binding` values in a `KeyMap`
struct and dispatches with `key.Matches`, because `bubbles/help` reads
the bindings and `Enabled()` makes per-state activation declarative; a
raw `switch msg.String()` is invisible to help and cannot be disabled or
rebound.

**Right:**
```go
type GlobalKeys struct{ Help, Quit key.Binding }

func NewGlobalKeys() GlobalKeys {
    return GlobalKeys{
        Help: key.NewBinding(key.WithKeys("?"), key.WithHelp("?", "help")),
        Quit: key.NewBinding(key.WithKeys("q"), key.WithHelp("q", "quit")),
    }
}

if k, ok := msg.(tea.KeyPressMsg); ok {
    switch {
    case key.Matches(k, m.keys.Help):
        return m.openHelp(), nil
    case key.Matches(k, m.keys.Quit):
        return m, tea.Quit
    }
}
```

**Wrong:**
```go
switch msg.String() { // invisible to help, cannot be disabled per state
case "?":
    return m.openHelp(), nil
}
```

## Rule 8: Declarative View and Cursor Hoist

Source: Bubble Tea v2 announcement,
`https://github.com/charmbracelet/bubbletea/discussions/1374` ("Declarative, Not
Imperative" and "An Actual Cursor"); Charm guide L58-61 for the root as
the one model.

In v2 the root's `View()` returns `tea.View`, and terminal features
(alt screen, mouse mode, focus reporting, window title, cursor) are
fields on it, computed from root state. No `tea.EnterAltScreen`-style
commands and no program options for them.

A focusable component does not paint its own cursor into its string. It
exposes `Cursor() *tea.Cursor`, non-nil only when focused, and the root
copies the active one into `tea.View.Cursor`. One blink phase lives at
the root. Set `VirtualCursor=false` on every `textinput` and `textarea`
so the root is the cursor authority.

**Right:**
```go
func (c Compose) Cursor() *tea.Cursor {
    if c.focus != focusBody {
        return nil
    }
    cur := tea.NewCursor(c.cursorX, c.cursorY)
    cur.Style = c.styles.Cursor
    return cur
}

func (m App) View() tea.View {
    v := tea.NewView(m.render())
    v.AltScreen = true
    if m.compose != nil {
        v.Cursor = m.compose.Cursor()
    }
    return v
}
```

**Wrong:**
```go
// paints a fake cursor and defeats root-level blink coordination
line := before + c.styles.Cursor.Render("█") + after
```

## Rule 9: Compose Commands with `tea.Batch`

Source: `https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md`, lines 220 ("Use `tea.Batch()` when returning multiple
commands").

When one `Update` pass produces several commands, collect them in a
slice and return `tea.Batch(cmds...)`. Never drop a returned `tea.Cmd`:
a discarded command is a silently lost message.

**Right:**
```go
var cmds []tea.Cmd
if cmd := m.chat.Animate(); cmd != nil {
    cmds = append(cmds, cmd)
}
cmds = append(cmds, fetchHeaders(m.backend, name))
return m, tea.Batch(cmds...)
```

## Rule 10: Lipgloss v2 Box Math and Styled Strings

Source: `https://github.com/charmbracelet/crush/blob/f02ffbcec15a9f95cb9bcff895833df10f829aae/internal/ui/AGENTS.md`, lines 165-191 ("Dialog rendering rules"), L12-18.

These hold anywhere a box is rendered or styled segments are joined.

- **`Width(n)` is the total box width.** Border and padding live inside
  it. Size content to the content area, not the outer width:
  `w := width - style.GetHorizontalFrameSize()`. Sizing to the full width
  makes the content a column or two too wide, and the frame re-wraps its
  last characters.
- **Inset with `Padding`, never `Margin`.** Margin sits outside the
  declared width and pushes the block past the frame; padding sits inside
  and applies to every wrapped line.
- **Render styled segments individually, then concatenate.** Never nest
  a rendered segment inside another style's input: the inner reset code
  ends the outer style for everything after it.
- **Cut styled strings only through `charmbracelet/x/ansi`**
  (`ansi.Truncate`, `ansi.Strip`, `ansi.Cut`). Never slice a string that
  may carry escape codes at the byte or rune level.
- **Clamp to the drawable area** so boxes stay inside small terminals.

**Right:**
```go
w := width - childStyle.GetHorizontalFrameSize()
inner := ansi.Hardwrap(ansi.Wordwrap(content, w, ""), w, false)
box := childStyle.Width(width).Padding(0, 1).Render(inner)

line := label.Render("From: ") + value.Render(msg.From) + label.Render(" (verified)")
trimmed := ansi.Truncate(styled, width, "…")
```

**Wrong:**
```go
inner := ansi.Wordwrap(content, width, "")          // ignores the frame
box := childStyle.Width(width).Margin(0, 1).Render(inner) // margin escapes width
line := outer.Render("From: " + value.Render(msg.From) + " (verified)")
trimmed := styled[:width]                           // slices mid-escape
```

## Rule 11: Style Tests Assert Resolved Attributes

Source: none in Charm's guide.

House departure: Charm's guide has no testing section. A zero-value
`lipgloss.Style{}` renders its argument unchanged, so
`style.Render("test") != ""` passes for an unstyled style and proves
nothing. A style smoke test asserts the attributes the style sets:

**Right:**
```go
if styles.HelpKey.GetForeground() == nil {
    t.Error("HelpKey has no foreground color")
}
if !styles.HelpKey.GetBold() {
    t.Error("HelpKey is not bold")
}
```

**Wrong:**
```go
if styles.HelpKey.Render("test") == "" { // passes against Style{}
    t.Error("HelpKey rendered empty string")
}
```

## Checklists

Before writing UI code, answer the planning questions; at the end of a
UI pass, run the review checklist against the diff. Both live in
[references/checklists.md](references/checklists.md), with the list of
v1-only APIs to reject.
