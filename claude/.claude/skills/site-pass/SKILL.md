---
name: site-pass
description: >
  Starts, resumes, or closes a development pass on one of the SvelteKit site repos
  (ecxc-ski, 907-life, aksailingclub-org, xcathletes-org, cairn-pub). Use on "continue
  development", "next pass", "finish pass", "ship pass", or explicit invocation, when the
  work is the site's own roadmap. Loads pass-core for the shared machinery. For the
  cairn-cms engine's own passes use cairn-pass.
---

# Site pass

**Load `pass-core` first.** It holds the pass-class table, the execution chain, execution
discipline, the close ritual skeleton, and the handoff. This skill adds only what a site
repo owns. Paths are relative to the site repo.

A pass has a resume prompt in `docs/STATUS.md`, a plan under `docs/superpowers/plans/`, and
usually a spec under `docs/superpowers/specs/`.

## Starting a pass

- If no plan exists, brainstorm per `pass-core`, then write the plan at
  `docs/superpowers/plans/YYYY-MM-DD-<topic>.md` from `plan-template.md`.
- The plan header carries exactly one of a consultation-brief link or the line "no engine
  asks", produced by the `engine-consult` skill. If it carries neither, run the engine-contact
  enumeration now and append the line to the committed plan. This blocks every
  `site-implementer` dispatch.
- Run the chain per `pass-core` with `implementer: "site-implementer"` and the pass class's
  per-task gate (table: `pass-core`).

## Following cairn-cms docs during the round

The draft-docs initiative deleted the cairn-cms admin, editors, and extend arms after the
harvest; each stays empty until its own stage rebuilds it (cairn-cms `CLAUDE.md`, "Documentation
is a pass dimension"). Where an arm is empty, a divergence between the docs and reality is filed
into the cairn-cms facts container (`docs/internal/facts/`), never fixed on a page. Where a
rebuilt arm page exists, follow it as written, and fix a divergence between the page and reality
on the page, under the spec's "Edits after the chain" rule (cairn-cms
`docs/superpowers/specs/2026-09-26-draft-docs-approach-design.md`): the page's brief is updated in
the same change, the fact bullet is filed alongside, and `check:provenance` in CI is the
tripwire. An arm whose stage is in flight is the exception: a divergence there is filed, never
fixed, and feeds that stage's page inputs.

Edit on a `site-docs/<site>-<pass>` branch off cairn-cms `main`, merged by PR under the docs
gate before the site pass closes; never edit cairn-cms `main` directly. Changed sentences get both
chain reviews, scoped to those sentences, except a pure term or link substitution.

## Closing a pass

Run `pass-core`'s ritual. The site-specific parts:

- **Gate (step 2):** `npm run check` (0 errors, 0 warnings), `npm test` if the repo has one
  (exits 0), and `npm run build`.
- **Review (step 3):** for website content, the `content-review` skill is the reviewer.
- **Docs (step 5):** add this pass's design decisions to `docs/architecture.md` (decisions,
  not narration), and keep the README and config comments current.
- **Archive (after step 6):**
  `git mv docs/superpowers/plans/<this-pass>.md docs/superpowers/archive/plans/`, and the
  spec to `docs/superpowers/archive/specs/` if one exists.
- **Commit and push (step 7):** `Pass <n>: <summary>`, specific files only, then `git push`.

## When not to use

- The cairn-cms engine's own passes: `cairn-pass`.
- Mid-pass debugging, single-file edits, or a typo or content fix.
