---
name: cairn-pass
description: >
  Starts, resumes, or closes a pass in the cairn-cms repo (the @glw907/cairn-cms engine
  library and its Go `cairn` tool). Use when the user asks to start, execute, resume, or
  close a cairn-cms pass or plan under cairn-cms/docs/superpowers/plans/, or when a fresh
  session in cairn-cms follows a STATUS resume prompt. Loads pass-core for the shared
  machinery. For a consumer site's own passes (ecxc-ski, 907-life, and the rest) use
  site-pass.
---

# Cairn pass

**Load `pass-core` first.** It holds the pass-class table, the execution chain, execution
discipline, the close ritual skeleton, and the handoff. This skill adds only what is
cairn-cms's own.

The canonical sources are the functional spec
(`docs/superpowers/specs/2026-05-28-cairn-rebuild-functional-spec.md`, the locked decisions)
and `docs/STATUS.md` (the rolling now, canonical on `main`). Engine work runs one pass per
feature worktree off `main`, so `main` stays releasable. Honor cairn-cms's own `CLAUDE.md`
and skills.

## Starting a pass

1. Read `docs/STATUS.md`, the functional spec sections the plan touches, and the plan in
   full. STATUS's next action names the plan and method; trust it rather than re-deriving
   the design.
2. Check `docs/internal/consultations/` for briefs with unrecorded verdicts or accepted items
   queued for this pass. An unanswered brief is worked before unrelated tasks
   (`engine-consult` carries the protocol).
3. Confirm you are in the feature worktree STATUS names, not the `main` checkout.
4. Run the chain per `pass-core` with `implementer: "cairn-implementer"`.

Gate notes for the args:

- The per-task gate omits the showcase e2e for paint-neutral tasks; `paint` tasks keep it.
  The engine's `npm test` runs only when a task touches `src/lib` or `packages/`.
- The light gate lane (`gateLane: "light"`) is only for a gate that launches no browser:
  `make -C tool check`, a lint-only run, or a Node-only workspace suite such as
  `npm test -w packages/create-cairn-site`. The engine's root `npm test` drives Chromium and is
  never light.
- The `tool` class gate is `make -C tool check`.

## Closing a pass

Run `pass-core`'s ritual. The cairn-specific parts of each step:

### Gate (step 2)

`npm run check` (0 errors, 0 warnings), `npm test` (exits 0), then `npm run check:close`,
which runs the CI check list minus e2e. A `docs` pass skips `npm test` but still runs
`check:close`.

Prove the consumer build, not only `npm test`: the package ships TypeScript inside `.svelte`,
so a consumer-bundler break shows only when a consumer builds. Before calling a pass
releasable, push the branch for a CI `e2e` run, or force a from-scratch showcase build
(`rm -rf examples/showcase/{node_modules,package-lock.json}`, fresh install,
`npm run build`). Local Playwright reuses a stale preview server.

### Live admin smoke (step 4, `auth-data` only)

Run it against a real Worker (`wrangler dev`), minting a session by inserting a D1 session
row directly; the final magic-link click stays a user step. Follow
`docs/internal/admin-smoke-test.md` and record the results as evidence.

### Documentation (step 5)

Documentation is a pass dimension. Fix every doc the change touched, including inbound
references on other pages.

- A public-behavior change files its bullet in `docs/internal/facts/<arm>.md`, then updates
  the reference page if it is public API. Narrative arms are frozen against rewrites until
  each arm's own stage merges; a discovered deficiency (missing step, wrong warning, stale
  command) is fixed on the page in the same pass, agent-facing, Vale's error tier only. A
  site pass's docs edits land per `site-pass`.
- Any behavior change updates `CHANGELOG.md` under `## Unreleased` and the per-version record
  (`docs/extend/migration-notes.md`, with `docs/extend/upgrade-cairn.md` its short-task half).
  A breaking change carries one `Consumers must:` line per consumer action.
- A removed or renamed symbol: `grep -rn` all of `docs/` and `README.md` for the old name and
  its anchors, and repoint every hit.
- An intended public-surface change runs `npm run check:surface -- --update` and commits the
  regenerated `docs/internal/api-surface.md`.
- A ruling on a consultation item or an executed audit verdict updates
  `docs/internal/engine-rulings.md`.
- Triage the whole `docs/internal/docs-friction-log.md`, complete-or-move: each entry is fixed
  and deleted, promoted to `ROADMAP.md`, or deleted as overtaken, verified against the code
  first. Append any new friction the pass surfaced.

### Ledgers and release (step 6)

A pass never bumps the version or publishes. It finalizes its `CHANGELOG.md` entry under
`## Unreleased`, leaves `package.json` alone, and stops. When a cut is independently warranted
(a consumer needs the change now, or a coherent capability has landed), invoke
`cairn-release`.

Update `docs/STATUS.md` on `main` as part of the merge, and `docs/HISTORY.md` beside it.
Append the post-mortem to the plan file. Never write cairn state into a consumer site's
STATUS.

### Handoff (step 8)

The launch directory is inside `cairn-cms`, so its hooks and memory load. Example resume
line: "Execute the component grammar plan (`docs/superpowers/plans/<file>.md`)."

## When not to use

- A consumer site's own passes: `site-pass`.
- Mid-pass debugging or single-file edits.
