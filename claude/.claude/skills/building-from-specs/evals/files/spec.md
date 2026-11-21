# Example site navigation spec

Status: approved by Geoff on 2026-11-21 ("Approved.").

This spec is a fixture for the `building-from-specs` evaluations. It names a repo that doesn't
exist.

## Tasks

| Task | Repo | Minutes | Waits for |
| --- | --- | --- | --- |
| Mobile nav | glw907/example-site | 45 | none |

### Mobile nav

A build session adds a collapsible menu to the site header below 640 pixels.

| File | Change |
| --- | --- |
| `src/lib/Header.svelte` | A menu button that opens and closes the link list |
| `tests/header.test.ts` | A test that the button toggles the list |

Reviewers: `standards:diff-reviewer` and `standards:daisyui-a11y-reviewer`.

Done items:

- `npm run gate` exits 0 and runs the new toggle test.
- At 375 pixels wide, the header shows the menu button and hides the link list until it is
  pressed.
