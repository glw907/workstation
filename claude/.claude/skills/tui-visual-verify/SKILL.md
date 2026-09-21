---
name: tui-visual-verify
description: Verify a terminal UI (bubbletea or any TUI) by driving the REAL terminal and looking at what it paints, never only at a text capture. Use before any claim that a TUI screen, theme, ground, glyph, resize rung, or pointer behavior "works", at every pass gate that demos a TUI, when an owner reports a screen that looks wrong, and whenever goldens and teatest are green but nobody has seen the painted result. Ships the kitty capture harness (keys, clicks, wheel, live resize, PNG plus ANSI per step) and the fresh-context grading shape.
---

# TUI visual verification

Born 2026-08-21 at poplar's pass 2 gate. The pass had 159 green gallery
goldens, a teatest flow suite, tmux smoke checks, and two review rounds
per task, and the first thing Geoff did in his own kitty exposed that
none of those media had ever looked at a painted frame. Every one of
them checks text. A terminal paints grounds, erases to the current
background, drops blank cells from text dumps, and delivers pointer
events only when the app asked for them. Those are the things that
break, and only the painted terminal shows them.

The rule: **a TUI claim is verified when a screenshot of a real
terminal window has been looked at, by a context that did not build
the change, against the ratified reference.** A text capture is
evidence of content, never of paint.

## What the field does, and where it stops

Bubbletea practice (Charm's own guidance, catwalk, teatest, golden
files) drives Update and View deterministically and diffs the rendered
string. Keep all of that; it is fast and it pins content and geometry.
Charm's VHS adds headless stills through xterm.js in Chromium, which is
the right CI layer for docs captures (`vhs-cli-demos` skill). Neither
paints the owner's terminal. For a gate, the gate platform (kitty here)
is the only truthful medium, so this skill drives kitty.

Claude Code's guidance is the same in one line: give Claude a way to
see the result and hand the user the evidence, not the claim.

## The harness

`scripts/kitty-shot` in this skill is the template; copy it into the
repo's `scripts/` and set the app-specific defaults there (poplar's
copy defaults to an isolated XDG store so a second instance never
fights the real one's lock).

**Headless is the default capture mode** (born 2026-09-21: a capture on
the live desktop interrupted the owner mid-session, forcing kitty onto
XWayland and stealing focus for the run's whole duration). By default
the template hands off to `kitty-headless-shot`, a workstation-level
tool (`~/.dotfiles/bin/.local/bin/`, `--help` is the spec) that drives
the SAME real kitty on an Xvfb display that exists only inside a
distrobox (`term-headless`, `bluefin/distrobox.txt`; `kitty-headless-shot
setup` creates it, idempotent). Same real terminal, same painted glyphs,
same font as the owner's own `kitty.conf` (shared into the container
unchanged), both grounds capturable (`-t dark|light`), but nothing
appears on the owner's screen and no focus is stolen, because the
display genuinely isn't the owner's. It also drives a long-running
full-screen program correctly: start it, send keys/clicks/wheel/resize
against the live process across many `shot:` steps, then quit it, all
inside one invocation. Pass `-d` (desktop) to opt into the OLD on-desktop
path instead. It forces kitty onto XWayland and grabs the window with
xdotool/import against the owner's live session, reserved for the rare
case the owner wants to watch the run happen or for debugging the
headless path itself. This workstation's own ImageMagick has no X11
delegate at all, and a GNOME screenshot portal or D-Bus route is denied
or interactive, so `-d` and the headless path are the only two options
that produce anything.

```
kitty-shot [-d] [-o OUTDIR] [-t dark|light] [-s COLSxROWS] [-c CMD] STEP...
  key:K           one character, or a kitty key name (escape, down)
  type:TEXT       literal text
  click:COL,ROW   left click on a cell, 1-based
  wheel:up|down[@COL,ROW]
  resize:COLSxROWS   live resize, in cells, verified against kitty
  sleep:S
  shot:NAME       OUTDIR/NAME.png + NAME.ansi, size appended to sizes.txt
```

Every design choice in it was forced by a failure on the day:

- **Input goes through kitty's remote control into the pty**
  (`kitten @ send-text`, `send-key`), never through X (`xdotool key`,
  `click`). X-level input needs focus; when focus is elsewhere the
  keystrokes land in whatever window has it, which can be the owner's
  live session. Shifted keysyms dropped intermittently even when focus
  was right.
- **A click is the SGR 1006 report bytes** (`ESC [ < 0 ; col ; row M`
  then `m`) written to the pty. Prove once per platform that a real
  click produces exactly those bytes (`printf '\e[?1002h\e[?1006h';
  cat -v` in the window, then a real click) and the injection is a
  faithful stand-in; the app cannot tell the difference. Wheel is
  button 64/65.
- **`window_padding_width=0`.** kitty counts the owner's padding
  inside a cell-unit resize, so 59x24 arrived as 56x22 and every
  rung-boundary label was a lie. Read the true grid back
  (`kitten @ ls`) after each resize and write it beside the capture.
- **Pixels, not the ANSI dump, for grounds.** `kitten @ get-text`
  omits blank cells, so a fully painted base ground reads as empty.
  Sample with `convert shot.png -format '%[pixel:p{x,y}]' info:`.
  An eye on a PNG misjudged the slate base as the terminal's own
  background; the pixel sampler refuted it in one call.
- **Keep the window alive after the app exits** (`$cmd; sleep 600`),
  or the final "did it quit cleanly" shot captures nothing.
- **Never `pkill -f` with a string that appears in your own command
  line.** It kills the shell running the harness (exit 144). Use
  `pkill -x` on the binary name, or iterate `pgrep -x` and spare the
  owner's pid.
- **A stale instance holds the lock.** If the window closes at once,
  check for an earlier instance against the same store before
  blaming the app.
- **Labels come from the screen, never from a key count.** A matrix
  that names captures by how many `n` presses it sent is wrong the
  first time one drops. Read the state off the capture (the app's own
  status row) and fail the run on a mismatch.

## The matrix

A gate run covers: every surface at the owner's real window size;
both themes (launch kitty with the light ground so the app's
background query answers light); every rung boundary pair from the
design language, in both directions; below the floor; the pointer
vocabulary (each advertised click target, one wheel notch, Esc); the
states the live app cannot reach on demand (modal, toast, banner,
offline) through the repo's fixture viewer; the degrade profiles; and
the ratified exemplar painted by the same terminal as the reference
image. Write a manifest that says what each capture claims to show.

## Grading

Follow `visual-fidelity`: the builder never grades. Fan out
fresh-context vision graders (Opus, one per capture group), each
handed the PNGs, the reference images, and the wireframe line ranges,
returning one verdict per visual device per capture, classified
STRUCTURAL, COSMETIC, or DESIGN-QUESTION with the reference cited.
Adversarially verify every STRUCTURAL finding (a refuter reads the
image and the source, defaults to refuted when the reference is silent
or a ruling already sanctions the behavior). Add one auditor whose
question is "is it right, and what will the owner's eye catch", not
"does it conform". The main loop then looks at the decisive PNGs
itself before anything is reported.

## Owner reports

When the owner says a screen looks wrong, reproduce at their exact
size, font, and terminal theme (read their `kitty.conf`) before
theorizing, and if it still does not reproduce, screenshot their
window (`import -window <id>`) rather than guessing. Treat "I see X"
as a capture request, not a question.
