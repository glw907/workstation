# Planning and review checklists

Companion to `elm-conventions`. The rules and their sources are in
`SKILL.md`; this file turns them into questions to answer before the
code and checks to run on the diff.

## Planning questions

Answer these in the plan or spec before writing any UI code.

- Which bubbles component is the closest analogue (viewport, list,
  table, textinput, textarea, spinner, help)? Name the file in the
  bubbles module, and state each deviation and why. "We need a custom
  list because X" is a reason; "we wrote a custom thing" is not.
- What state does each component own, and what does the root hand it
  (method arguments, `SetSize`)?
- How does each component's render enforce its width and height (Rule
  6)?
- Which state changes does the root make by calling a component
  directly, and which results arrive as messages from a `tea.Cmd`
  (Rule 4)?
- How does the root react to `tea.WindowSizeMsg`: store the
  dimensions, call `SetSize`, and pass the message to any bubbles
  model held as a field?
- For async I/O, which `tea.Cmd` wraps it, and does it return an error
  message on failure?
- Are keys declared as `key.Binding` and dispatched with
  `key.Matches` (Rule 7)?
- Does a focusable component expose `Cursor() *tea.Cursor`, with
  `VirtualCursor=false` on its textinput or textarea (Rule 8)?
- Is every terminal feature (alt screen, mouse mode, focus reporting,
  window title) set on the root's `tea.View` and not through a program
  option or command?

## Review checklist

Run against every UI diff at the end of a pass. Each item is checkable
from the diff or from a capture of the real terminal (see
`tui-visual-verify`).

- Every changed or new component renders no line wider and no more rows
  than its assigned size. Confirm with a capture at a normal size and at
  the minimum width the pass touches.
- No state mutation in `View()` or in a `tea.Cmd` closure.
- All blocking I/O sits inside a `tea.Cmd`, and each closure captures
  values, not the model.
- Width math uses `ansi.StringWidth`, never `len()`.
- Width-taking renderers pair wordwrap with hardwrap.
- No parent-side clipping around a child's output.
- No nested `tea.Model` of your own, no message whose only job is to
  carry a child's state to its parent, no callbacks, no parent pointers.
- `tea.WindowSizeMsg` reaches every sized component and every bubbles
  model held as a field.
- Keys are `key.Binding` values dispatched with `key.Matches`.
- Boxes size to the content area (`Width` minus frame), inset with
  `Padding`, join styled segments by concatenation, and cut styled
  strings only through `charmbracelet/x/ansi`.
- The root's `View()` returns `tea.View` with chrome fields set from
  root state, and no imperative chrome commands remain.
- Focusable components expose `Cursor()`, and none paints its own.
- Style tests assert resolved attributes.
- Any deviation from these rules this pass is recorded with its reason;
  a silent deviation is a defect.

## v1-only APIs to reject

Removed or renamed in Bubble Tea v2 and its companions. A hit in new
code is a defect.

- `viewport.HighPerformanceRendering` (gone).
- `tea.Sequentially` (now `tea.Sequence`).
- The package-level no-argument `spinner.Tick()` (use the model's
  `Tick`).
- `*Model.NewModel` constructors (use `New(...)`).
- `tea.WithAltScreen()` and other chrome program options, and the
  `tea.EnterAltScreen`, `tea.HideCursor`, mouse, and focus-reporting
  commands (set fields on `tea.View`).
- `lipgloss.AdaptiveColor` and the `compat.AdaptiveColor` shim
  (resolve themes to concrete `color.Color` values).
- A per-input `cursor.Model` (use the `tea.Cursor` hoist).
- Positional `viewport.New(w, h)` (use the `viewport.With*` options).
- A `tea.KeyMsg{...}` literal (use `tea.KeyPressMsg{...}`).
- Assigning the exported `Width` or `Height` field on textinput,
  textarea, viewport, or help (use `SetWidth` and `SetHeight`).
- The `atotto/clipboard` shim (use `tea.SetClipboard` and
  `tea.ReadClipboard`).

For the v2 changes behind this list, see the announcement at
`https://github.com/charmbracelet/bubbletea/discussions/1374`.

## Other traps

- Do not call `Init()` from inside `Update()`: it re-fires the
  component's start-up commands, such as duplicate spinner ticks. Use a
  reset method that returns only the commands the new state needs.
- Do not use `tea.ExecProcess` for an in-app surface (compose, picker,
  inline editor); render those in the pane. Reserve it for a real
  shell-out.
- Do not define package-level `.Render` closures (`var s =
  NewStyle()....Render`): they bake the style at init and cannot follow
  a runtime theme change. Build a `Styles` struct once the theme is
  known.
