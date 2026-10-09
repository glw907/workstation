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

The friction log `pass-core`'s out-of-scope rule names is `docs/internal/docs-friction-log.md`.
Add each entry under "Open findings" as a `- **\`perspective\`.**` bullet, commit it on `main`
at the checkpoint, and name who found it and the date.

The `main` checkout is shared: another session's pass may hold uncommitted edits to
`docs/STATUS.md` or the friction log there. Before a checkpoint commit on `main`, run
`git diff <file>` and stage only your own hunks (`git add -p`). If a file carries another
session's warm edits, coordinate with that session instead of committing them. (A harvest
checkpoint on 2026-09-29 committed pass C's STATUS edits along with its own.)

Gate notes for the args:

- The per-task gate is the tier `scripts/checks/gate-tier.mjs --range <base>..HEAD` computes
  from the diff, plus the e2e specs the change reaches (Geoff, 2026-10-08). The engine's
  `npm test` runs when the classifier computes the engine tier, which includes `scripts/**`,
  `src/tests/**`, and test files as well as `src/lib` and `packages/`. A `paint` task's e2e is
  the specs its change reaches, with the full suite at segment boundaries.
- The light gate lane (`gateLane: "light"`) is only for a gate that launches no browser:
  `make -C tool check`, a lint-only run, or a Node-only workspace suite such as
  `npm test -w packages/create-cairn-site`. The engine's root `npm test` drives Chromium and is
  never light.
- The `tool` class gate is `make -C tool check`.
- A lone unrelated test-file failure, or a component run printing `Cannot connect to the
  server in 60 seconds`, is a known workstation trap before it is a regression:
  `docs/internal/durable-gotchas.md` carries the rerun rule and the serialized heavy gate.

The chassis (the showcase's `examples/showcase/src/chassis/` and `templates/waymark/`) is the
code a developer copies, so whatever it does becomes their idiom, and its quality bar equals the
engine's (Geoff, 2026-09-01). A chassis task takes the same pass class, review bar, and plan
review an engine change of its kind would take, never a lighter tier: exemplar-grade code and
the full cleanliness treatment.

## Closing a pass

Run `pass-core`'s ritual. The cairn-specific parts of each step:

### Gate (step 2)

`npm test` (exits 0), then `npm run check:close`, which runs `npm run check` (0 errors, 0
warnings) and the rest of the CI check list minus e2e. A `docs` pass skips `npm test` but still
runs `check:close`.

Prove the consumer build, not only `npm test`: the package ships TypeScript inside `.svelte`,
so a consumer-bundler break shows only when a consumer builds. Before calling a pass
releasable, push the branch for a CI `e2e` run, or force a from-scratch showcase build
(`rm -rf examples/showcase/{node_modules,package-lock.json}`, fresh install,
`npm run build`). Local Playwright reuses a stale preview server.

### Live admin smoke (step 4, `auth-data` only)

Run it against a real Worker (`wrangler dev`), minting a session by inserting a D1 session
row directly, then drive the magic-link round trip itself in headless Chromium, reading the
link from wrangler's local `send_email` output (Geoff, 2026-09-21: verification a plan parks for
the owner is Claude's). Follow
`docs/internal/admin-smoke-test.md` and record the results as evidence.

### Documentation (step 5)

Documentation is a pass dimension. Fix every doc the change touched, including inbound
references on other pages.

- A public-behavior change files its bullet in `docs/internal/facts/<arm>.md`, then updates
  the reference page if it is public API. The admin and editors arms and the front door are
  empty, and extend holds only its kept pages until stage 2a; each arm stays that way until its own stage
  rebuilds it. While an arm holds no rebuilt page, a divergence is filed into the facts container.
  A deficiency found on an existing page (reference, a kept extend record, or a rebuilt arm page)
  is fixed on the page in the same pass, with its fact bullet filed alongside. On a published page
  the fix is written to the track's drafting brief, with no register review or polish, and Vale's
  error tier still runs; an edit to a page with a brief updates the brief in the same change (the
  parent spec's "Edits after the chain"). An internal doc's fix is agent-facing. A site pass's docs edits land
  per `site-pass`.
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
  first. Append any new friction the pass surfaced. When the pass ran the page chain, the fold
  agent (never the conductor) first reconciles every stage record's `frictionFiled` entry against
  the log; a promotion to an engine change reads `docs/internal/engine-rulings.md` and runs the
  charter's premise test first; the HISTORY entry counts the entries and their outcomes.
- A docs-stage close runs the engine-pass boundary test over the log's engine entries and the
  `ROADMAP.md` engine-friction entries: fix before the next docs stage an item whose fix would
  change what a written or outlined page tells the reader (a workaround, a caveat, a step); fix
  now an item that blocks a page or a migration step; batch the rest into whichever engine pass
  runs next. The close report and STATUS state the verdict: whether an engine pass is warranted
  before the next stage, and its scope. Engine passes land on `main` and never release (Geoff,
  2026-10-07; `ROADMAP.md`'s standing rule).

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
