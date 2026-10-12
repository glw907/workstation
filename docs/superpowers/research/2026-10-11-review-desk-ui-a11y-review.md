# Review desk UI: accessibility review of the mockups

The `daisyui-a11y-reviewer` agent (Opus, medium) reviewed the second-round mockups in the conductor
session `4bea6e68` on 2026-10-11. The mockup builder then folded the findings into the approved
mockups in `docs/superpowers/specs/assets/2026-10-11-review-desk-ui/`. The design says every
finding carries into the build. This file copies the reviewer's final report verbatim from the
conductor transcript (`4bea6e68-41c7-44c2-8635-1cf9b88f0358.jsonl`), so the build and its close
review can cite it. File names in the report are the earlier mockups' names (`triage.html`,
`empty.html`, `pr.html`).

---

I reviewed all four mockups in `/var/home/glw907/.claude/jobs/4bea6e68/tmp/desk-mockups/`. I found
no problems with the Tailwind 4 syntax, the DaisyUI 5 class names, shadows, all-caps labels,
gradients or motion. Contrast passes in both themes: muted text is 5.5:1 or better, the diff signs
6:1 or better on their tinted rows, and the primary focus ring 6.2:1 or better.

**Blockers**

1. **All files, shared keydown script.** j, k, z, a, r, ?, /, 1, 2 and 3 work anywhere on the page,
   and nothing lets you turn them off or remap them (2.1.4). A stray a, or a speech command,
   approves a merge. Fix: add a persisted "Single-key shortcuts" switch to the ? sheet, or require a
   modifier key.
2. **`triage.html`, `Enter` handler.** Enter submits every row from any focused element, including
   queue links, Undo and radios. That breaks normal activation (2.1.1) and makes it easy to submit
   by mistake. Fix: only submit from the Submit button, or use Ctrl+Enter.
3. **`empty.html`, `#close-line`.** The tab closes after 10 s, and the only way to keep it open is
   offered after the timer has started (2.2.1 asks for at least 20 s to extend). Fix: run the
   countdown for at least 20 s, move focus to Keep on load, and add a setting that turns auto-close
   off.

**Warnings**

4. **Toast, all files.** The `role="status"` region sits inside a container that starts out
   `hidden`, so screen readers may miss its first message. It also re-renders every second, which
   floods announcements, and so does `#close-line` (4.1.3). Fix: keep an `sr-only` status region in
   the DOM, announce once ("Approved X. Opening Y in 5 seconds. Press z to undo."), and keep the
   visible countdown outside the live region.
5. **Focus after a decision.** `lock(true)` disables the button that has focus, so focus falls to
   the body (2.4.3). Fix: move focus to Undo, and put it back on Approve or Submit after an undo.
6. **`moveQueue`.** j and k move `aria-current="page"` and `menu-active` to a link that is not the
   open page (4.1.2). Fix: only move focus (`menu-focus`) and leave `aria-current` where it is.
7. **Triage 1, 2 and 3 keys.** These set the radio value on row `fi` while focus may be elsewhere,
   so nothing is announced (4.1.3). Fix: use roving focus on each row's checked radio instead of the
   `tr tabindex="-1"`, and tie "Changed from …" to the group with `aria-describedby`. Make `#tally`
   a live region.
8. **Sticky `#decision` bar and `bottom-24` toast.** They can completely hide a focused summary
   underneath them (2.4.11). Fix: `html { scroll-padding-bottom: <bar height> }`.
9. **Drawer.** `#queue-toggle` has no accessible name. On small screens, opening it moves no focus
   and Escape does nothing (4.1.2, 2.4.3). Fix: add `aria-label="Queue"`, move focus to the first
   queue link, and close on Escape.
10. **`pr.html` `#file-summary` and `#no-match`.** Filter results are not announced (4.1.3). Fix:
    `role="status"`.

**Suggestions**

11. **Triage, "Reason" inputs.** All 13 have the same accessible name (2.4.6). Fix:
    `aria-label="Reason for item N"`.
12. **Mobile `.navbar`.** It sits outside any landmark (1.3.1). Fix: wrap it in a `<header>`.
13. **Toast style.** It uses `alert-success` even for a rejection. Fix: use `alert-info`.
14. **`#secs`.** DaisyUI's `countdown` component could replace it.
15. **Diff tables.** They have no `<caption>` or `aria-label`, and no DaisyUI component replaces
    them.

Verdict: three blockers (2.1.4, global Enter, 2.2.1). The DaisyUI and Tailwind usage is sound.
