# Review desk (design)

**Status:** approved by Geoff, 2026-10-11, in the conducting session (`c747c352`), and amended the same day for the SvelteKit stack (see "How it works"), with his answers
to three questions recorded below. It runs before infra sweep 2 (Geoff, same day).

## Why

Geoff wants a clean review environment for everything that needs his approval, not the GitHub
interface: "I'm looking for a clean review environment, not the github interface." The interface
is one and consistent ("The dialog should live with the PR"), it lives locally on each workstation,
and it uses the house 907.life design language, the same one the phonebook uses.

## Outcome

Every item waiting on Geoff (a PR in any repo, or a design) opens in its own review page in Firefox.
He reads it there and decides there. Approve makes the conductor act: merge and pull for a PR,
proceed for a design. Reject records his note and stops the work, and the issue is taken up with
him in the Claude Code terminal session.

## What Geoff sees

- **Arrival:** the item's review page opens as a new Firefox tab the moment a session hands it over
  (Geoff's answer: open a tab right away).
- **Index:** every item waiting, newest first. Each row shows the kind (PR or design), the repo, the
  title, and the risk class.
- **PR page:** a plain-language summary leads: what it does, what goes live on merge, the review
  verdict, and found-not-done. Below it is the full diff: each changed file with its line counts,
  collapsed by default, expanding to a syntax-highlighted diff (Geoff's answer: summary plus full
  diff).
- **Design page:** the design rendered as a clean document at a reading width.
- **Decision bar** at the foot of each item: Approve, or Reject, which opens a short note field.
  These are the only two decisions; a question is a Reject with a note. After the click, the page
  shows live status ("Approved. Merged and pulled.").

## Design language

The Survey theme core, which phonebook uses (`~/Projects/phonebook/CLAUDE.md:59-64`). Sources, all
under `~/Projects/cairn-themes/`:

- `survey-theme/core/theme.css:11-96` for the light and dark color tokens, and `:98-138` for fonts,
  type steps, and spacing;
- `survey-theme/core/components.css` for the signature devices (contour texture, benchmark
  triangle, dashed contour rules, the alert);
- `docs/superpowers/specs/2026-10-07-survey-design.md` for its rules: no shadows, no all-caps
  labels, no gradients, no decorative motion, contour texture at about a quarter opacity, WCAG AA;
- `survey-theme/reference/2026-10-07-approved-specimen.html`, the approved specimen to match.

Karla for UI text, Spectral for page titles, Monaspace Neon for code, all self-hosted (Fontsource). Light and
dark follow the system setting. The page works offline: no CDN or network fetch at view time.

## How it works

- A session hands an item over with one command. The command builds the page's data from git and
  `gh`, opens the tab, and waits in the background until Geoff decides, so his click wakes the
  session (the conductor pattern, run as a background Bash command).
- **Stack (Geoff, 2026-10-11: "use the local sveltekit idiom ... since we're already well-tooled
  for that").** A SvelteKit app in its own repo, `~/Projects/review-desk` (`glw907/review-desk`),
  following phonebook's stack (SvelteKit 3, TypeScript, Tailwind CSS 4, daisyUI 5) with
  `@sveltejs/adapter-node` in place of the Cloudflare adapter. A systemd user service runs the
  built app on `127.0.0.1` only. Dotfiles holds the handing-over command and the unit file, stowed,
  and `bluefin/bootstrap.sh` (or its manifest) installs the app on a fresh workstation. The Survey
  theme core is copied in from `~/Projects/cairn-themes` the way phonebook takes it, with fonts
  self-hosted through Fontsource. This replaces the Python standard-library server the first
  version of this design named.
- Security: a click leads to a merge, and any web page Geoff visits can reach localhost. SvelteKit's
  built-in CSRF check rejects a cross-origin form post. On top of it: a per-start token embedded in
  the page and required on every decision, a Host check against DNS rebinding, and the
  loopback-only bind.
- `pass-core` names the desk as the one way to hand anything to Geoff for approval, at the Design
  step and at Close. The PR #4 rule (open PRs in Firefox) covers him until this lands.

## Out of scope

Line comments, editing from the page, approval by anyone but Geoff, and any hosted or cloud
component.

## End-to-end check

From a scratch session, hand over a real PR and a real design. Each opens in a Firefox tab in the
Survey style, in light and dark. Approve on the PR merges it and the waiting command exits on the
click. Reject on the design records the note and the command exits with it. A cross-origin POST
from another page is refused.

## Risk

`auth-data` in spirit (a click leads to a merge), so tasks are test-first and the close includes
`web-auth-security-reviewer`. The path map still classes the files `runner` or `ordinary`; the plan
records the upshift. About 4 to 5 hours of clock.
