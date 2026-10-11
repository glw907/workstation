# Review desk (design)

**Status:** approved by Geoff, 2026-10-11, and re-scoped the same day to a lean v1 (Geoff, in the
conductor session `4bea6e68`). He approved planning and executing it unattended from this scope,
added a triage item kind, and moved it into the workstation repo. This version supersedes the
full-size design of the same date (systemd service, own repo, install step, e2e and fidelity
gates), whose plan on `worktree-review-desk-plan` is retired.

## Why

Geoff wants a clean review environment for what needs his decision, not the GitHub interface: "I'm
looking for a clean review environment, not the github interface." It runs locally and uses the
Survey theme the phonebook uses.

## Outcome

A session hands Geoff an item with one command. The item opens in Firefox, Geoff decides there,
and the command exits with his decision, which wakes the waiting session to act on it.

## What Geoff sees

- **Index:** the items waiting, newest first: kind, repo, title.
- **Item page**, one of three kinds:
  - **PR:** the summary (the PR body, rendered), then the diff.
  - **Design:** the design document, rendered at a reading width.
  - **Triage:** a list of found-not-done items, each prefilled with the session's proposed
    disposition (now, defer, or drop) and its one-line reason. Geoff changes any row.
- **Decision:** Approve or Reject on PR and design items; Reject opens a short note field. A triage
  item has one Submit, which sends every row's disposition.

## How it works

- **Home:** `review-desk/` at the top of `~/.dotfiles`, outside Stow (Geoff, 2026-10-11: "it's
  effectively local claude infra"). A SvelteKit app on phonebook's stack (TypeScript, Tailwind CSS 4,
  daisyUI 5) with `@sveltejs/adapter-node`, and the Survey theme core copied in from
  `~/Projects/cairn-themes` the way phonebook takes it. Fonts self-hosted; nothing fetched at view
  time.
- **Hand-over:** `bin/.local/bin/review-desk`, stowed. It writes the item (kind, repo, title, and
  the content: `gh` output for a PR, the file for a design, a JSON list for triage) into a state
  directory, starts the built app on `127.0.0.1` if it isn't running, opens the item in Firefox,
  and waits. It exits when the decision file appears and prints the decision as JSON. A session
  runs it as a background Bash command, so the exit wakes the session.
- **Security**, at the one boundary: the app binds loopback only, rejects a request whose `Host`
  isn't the loopback address and port (DNS rebinding), and keeps SvelteKit's built-in CSRF origin
  check on its form actions. The app never merges anything; the session acts on the decision.
- **Gate:** `scripts/check.sh` runs the app's `npm run check` and unit tests when `review-desk/`
  changes.
- **Process:** `pass-core` names `review-desk` as the hand-over for a PR, a design, and found-item
  triage, replacing the Firefox `gh pr view --web` step.

## Out of scope

A systemd service, an install or bootstrap step, a drift probe, an e2e suite, a visual-fidelity
pass, line comments, syntax highlighting beyond plain diff colors, and anyone but Geoff.

## End-to-end check

From a scratch session, hand over one real PR, one design, and one triage list. Each opens in
Firefox in the Survey style. Approve on the PR, Reject with a note on the design, and a changed
triage row each make the waiting command exit with that decision. A form post from another origin
is refused.

## Risk and estimate

Class `runner` (Geoff, 2026-10-11), not `auth-data`: the app makes no merge or account call. About
3 to 3.5 hours of clock: 2 to 3 for the lean v1 Geoff set, plus 30 to 45 minutes for triage. A
plan over 7 hours comes back to Geoff before launch.
