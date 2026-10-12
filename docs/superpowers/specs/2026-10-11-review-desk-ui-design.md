# Review desk UI (design)

**Status:** approved by Geoff, 2026-10-11, for unattended planning. Geoff chose the direction across three mockup rounds
in the conductor session (`4bea6e68`): a queue and item split, keyboard first, a dense PR summary
with diffs on demand, triage grouped by decision with a gentle color cue, and a clean, quiet,
readable treatment throughout.

## Outcome

The desk becomes a productive daily tool: everything waiting in one place, each decision a key
press away, and the screen calm enough to read for long stretches. It matches the approved
mockups in `docs/superpowers/specs/assets/2026-10-11-review-desk-ui/` (`pr-b.html`,
`design-b.html`, `triage-c2.html`, `empty-b.html`).

## What Geoff sees

- **Layout.** A narrow queue on the left (a DaisyUI drawer that stays open on wide screens) lists
  every waiting item, oldest first; the selected item fills the right. A decision loads the next
  item in the same tab. With nothing left, the page says so, counts 30 seconds with Keep open
  focused, and closes the tab; a saved setting turns auto-close off.
- **Keys.** `j`/`k` move the queue, `a` approves, `r` rejects with a note, `1`/`2`/`3` set a
  triage decision, `z` undoes within 5 seconds, `?` opens the shortcut sheet. A saved switch in
  the sheet turns single-key shortcuts off (WCAG 2.1.4), and no shortcut fires while typing.
- **PR.** Four plain figures (class, checks, review, files), the checks and review verdicts, the
  body in collapsible sections, then files grouped by top-level directory with a path filter and
  diffs opened in place. Color only where it means something: a failing check, a blocking verdict,
  diff signs. A `## Before merge` section stays a warning above Approve.
- **Design.** The document at a 68-character measure.
- **Triage.** Now, Defer, and Drop sections with counts; `1`/`2`/`3` or a "Move to" menu moves an
  item, with focus following it. A small dot by each heading, and by a moved item, carries one
  muted color per section (Now `--cairn-warning-ink`, Defer `--color-info`, Drop `--color-muted`,
  each at least 4:1); the headings carry the meaning, never the color alone. One calm status line ("13 items, 2 changed from proposed"); reasons edit in place;
  Submit by button or Ctrl+Enter.

## How it works

- Svelte and DaisyUI 5 components in `review-desk/`, on the Survey theme. The mockups are the
  visual reference, not code to copy: their CDN loads become the app's existing Tailwind build.
- Undo holds a decision in the page for 5 seconds before it posts, so the server and the
  `review-desk` command do not change.
- The next item loads by client-side navigation with `history.replaceState`, so the tab keeps one
  history entry and stays script-closable for the empty-state close (HTML "script-closable").
- Every finding of the 2026-10-11 accessibility review of the mockups carries into the build.

## Out of scope

One shared tab across hand-overs (each hand-over still opens its own tab), the deferred desk
hardening in ROADMAP "Someday", and any change to the `review-desk` command's protocol.

## End-to-end check

Hand over one real PR, one design, and one triage list. Each renders like its mockup in light and
dark (graded by `visual-verifier`); each decision works by key and by click; `z` undoes; the next
item loads in place; the empty state closes the tab; `daisyui-a11y-reviewer` and the Blueprint
quality inspector find no blocker.

## Risk and estimate

Class `runner` (Geoff, 2026-10-11, for the desk). About 2 hours of clock; the first desk pass took
68 minutes. A plan over 4 hours comes back to Geoff. On merge, the running app is stopped and
rebuilt, since a running desk keeps serving its old build.
