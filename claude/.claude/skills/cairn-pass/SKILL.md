---
name: cairn-pass
description: >
  Invoke at the start or end of a plan in the cairn-cms rebuild, the embedded
  magic-link, GitHub-committing CMS library for SvelteKit/Cloudflare sites
  (numbered plans 00 through 08 plus the later named plans). The canonical source is
  the functional spec at cairn-cms/docs/superpowers/specs/2026-05-28-cairn-rebuild-functional-spec.md;
  the plans live in cairn-cms/docs/superpowers/plans/. Trigger on "start/execute/implement
  plan <N or name>", "continue", or "next plan" when the work is cairn-cms; this is also
  the entry point for a fresh session resuming a plan after a context clear. For a site's
  OWN roadmap (ecnordic/907-life numbered passes) use site-pass.
---

# Cairn Pass (cairn-cms rebuild)

The cairn-cms rebuild (numbered plans 00-08) landed long ago; the library publishes to
npm and later engine work runs as named passes on feature worktrees off `main`. The
canonical source of truth is the functional spec (locked decisions) plus `docs/STATUS.md`
(the rolling now); the older writeups live under `docs/internal/history/`.
Each plan is written just-in-time after the prior one lands, under
`cairn-cms/docs/superpowers/plans/`.

The rebuild (plans 00 through 08) has landed and merged to `main`; stable `0.6.0` shipped
and both sites run it. Later engine work (public delivery, the CairnExtension dispatch, the
scaffolder) runs on a feature worktree off `main`. The current state, the branch topology, and
the open decisions live in `cairn-cms/docs/STATUS.md`, which this skill reads at pass-start and
updates at pass-end. Honor `cairn-cms`'s own `CLAUDE.md` and skills.

> **Which skill?** This is for the cairn-cms library rebuild. If the user means a
> site's own numbered passes (ecnordic-ski / 907-life roadmap), use **`site-pass`**.

## Starting a plan

This is the entry point at plan start, whether continuing in the session that wrote the
plan or resuming cold after a clear or a crash. STATUS.md's "immediate next action" line
names the plan to execute and the method; trust it and the plan file rather than
re-deriving the design.

1. **Read `cairn-cms/docs/STATUS.md`** for the current state and open decisions, the
   **functional spec** (sections relevant to the plan) for the locked decisions and
   architecture, and **the plan file in full** for the task-by-task steps and exit criteria.
   Also check `docs/internal/consultations/` for briefs whose verdicts are unrecorded or
   whose accepted items are queued for this pass; STATUS should name them, and an
   unanswered brief is worked before unrelated tasks (the `engine-consult` skill carries
   the protocol).
2. Confirm you are in a feature worktree off `main`, not the `main` checkout itself.
   STATUS.md lists the active worktrees.
3. Each task runs as a chain. `cairn-implementer` (pinned Sonnet for token economy) writes
   or confirms the failing test first, makes it green, clears the full gate (`npm run check`
   0/0, `npm test` exit 0), and returns files touched, the gate result, and anything it could
   not do. The `diff-reviewer` agent (`claude-opus-5`) then reads the diff against the task's
   acceptance criteria and returns accept, fix, or escalate with `file:line` findings; the
   conductor does not read the diff itself. One re-dispatch on `fix`; a second `fix` verdict
   goes to the conductor as a decision. Below six tasks, dispatch the chain per task with the
   Agent tool. At six or more, or when the plan marks tasks independent, run
   `~/.claude/workflows/pass-execute.js` with `{repo: "cairn-cms", gate: "npm run check &&
   npm test", implementer: "cairn-implementer", tasks: [{id, title, criteria, files, notes}]}`.
   Implement a task inline, or upshift the dispatch to `model: opus`, only for novel
   correctness-critical logic the plan does not fully specify; `model: fable` only when an
   Opus verdict itself hedges on something that matters.

> **Gate economy (Geoff, 2026-09-09).** The per-task gate omits the showcase e2e for
> paint-neutral tasks; paint tasks keep it; the pass-end ritual and CI run the full suite.
> Comment-only fix rounds run the reduced gate; the engine's `npm test` runs only when a task
> touches `src/lib` or `packages/`. Implementers run gates through `cairn-run-gate`. A pass
> whose gate launches no browser (the Go tool's `make -C tool check`) sets `gateLane: "light"`
> in the runner's args, or it queues behind every other session's browser gate. Read
> `~/.claude/docs/pass-gate-economy.md` in full before launching a pass's first segment; it is
> short, and its rules reach an implementer only through what the conductor puts in the args. The
> chains scripts honor per-task `gate` and `model` fields. Rules and evidence: the workstation
> CLAUDE.md, "Gate economy on a pass".

> **Legacy discipline.** The frozen `legacy/` build only ever got smoke tests, not real
> use, so it is an accelerator and a behavioral reference, not a proven artifact to
> preserve. Port pure, framework-agnostic logic from it to move fast, but hold everything
> to the rebuild's current standards (Svelte 5 runes, DaisyUI v5, the a11y bar) and prove
> it with our own tests. Re-derive UI and framework-coupled code clean rather than copying
> legacy markup; copying v4/better-auth-era assumptions forward is what the Plan 05 review
> gate had to undo.

## Ending a plan: consolidation ritual

No plan is done until every step has run.

### 1. Simplify

Dispatch the code-simplifier agent over the code changed this plan. Use
`subagent_type` = **`code-simplifier:code-simplifier`** (the bare name errors).
Docs-only plans skip this.

### 2. Check and test

Run `npm run check` (svelte-check, 0 errors and 0 warnings) and `npm test` (the
unit, integration, and component projects; the integration layer runs in workerd
against a real miniflare D1, the component layer in a real browser). Green is the
bar, and that means `npm test` **exits 0**: a passing assertion count is not enough,
since an unhandled rejection can leave every test green while the process exits 1.
Fix every failure before continuing.

Then run `npm run check:comments` (the ESLint TSDoc + em-dash gate over `src/lib`). The
`cairn-implementer` gate and `npm run check` (svelte-check) do **not** cover it, so a TSDoc structure
slip (a multiline `/**` with text on the first line, a stray `{type}` tag) passes every other gate and
only fails on CI. Run it here, with the from-scratch consumer build, before calling a pass done. This
gate is one of SIX CI-only checks the local ritual skips; the other five are
`check:reference:signatures`, `check:surface`, and `check:snippets`, all in step 5, plus
`check:transcripts` and `check:symbols` below. An `0.62.0`-era pass shipped red on `check:comments`,
and the 2026-08-01 xcathletes seams pass shipped red on `check:snippets`. Treat the six as one list
and run them by name.

Also run `npm run check:transcripts`, `npm run check:symbols`, and `npm run check:arm-indexes` (a new page under any docs arm, `docs/internal/` included, must be linked from that arm's index; the docs-to-facts close missed it, 2026-09-16). `check:transcripts` fails when a
quoted transcript block on an admin doc page has drifted from its recorded fixture; the
newest-toolchain pass (2026-08-21/22) hit this on a hand edit to an admin page that no other local
gate caught. `check:symbols` fails when a backticked dotted token in a code comment reads as an
unresolved log-event reference; the same pass hit this on a new comment and fixed it by adding the
token to that gate's allowlist rather than renaming it.

**Prove the consumer build, not only `npm test`.** The package ships TypeScript inside its `.svelte`
files, so a consumer-bundler incompatibility (a Vite 8 / Rolldown parse failure, an import-resolution
gap) surfaces only when a consumer builds, never in the library's own `npm test`. The showcase e2e is
that gate: `npm --prefix examples/showcase run test:e2e` builds the showcase, then runs Playwright. Off
CI, local Playwright reuses a stale preview server (`reuseExistingServer` is on when `CI` is unset), so a
local "all green" can pass against a stale build. Before calling a pass releasable, either push the
branch for a CI `e2e` run or force a from-scratch consumer build: `rm -rf
examples/showcase/{node_modules,package-lock.json}`, then a fresh install and `npm run build`. This is
how `0.60.0` shipped a broken consumer build; see the `cairn-0-60-e2e-dist-build-failure` memory.

### 3. Review gate

Fan out the relevant review subagents in parallel and fold their findings in
before committing. Match the subagent to what the plan touched:
`svelte-reviewer`, `cloudflare-workers-reviewer`, `web-auth-security-reviewer`
(always for auth, session, cookie, token, or signing changes),
`daisyui-a11y-reviewer`. They complement `/code-review`, not replace it.

### 4. Live admin smoke

For any plan touching the `/admin` surface, run the live admin smoke against a
real Worker (`wrangler dev`). Under the rebuilt self-owned auth, mint a session
by inserting a D1 session row directly (no better-auth cookie, no email loop);
the final magic-link click in a browser stays a user step. Follow
`cairn-cms/docs/internal/admin-smoke-test.md`. Record results as evidence. Skip for plans that do not touch `/admin`.

### 5. Documentation

Documentation is a pass dimension, not a follow-up. Before the pass is done, update the docs for
whatever it changed. The standing principle is that docs stay current and never drift, so a pass
fixes every doc its change touched, including the inbound references on other pages.

- **Container first, reference page second, narrative arms frozen against rewrites, open to
  fixes.** A public-behavior change files its bullet in `docs/internal/facts/<arm>.md`, gated
  by `check:facts`, then updates the reference page if public API. No pass rewrites the admin,
  editors, extend, or why-cairn narrative; a discovered deficiency (missing step, wrong warning,
  stale command) is fixed on the page in the same pass, gated by its own gates, bullet filed
  alongside, agent-facing not register-graded: source, engine version, why, Vale's error tier
  only, no prose review, since the site round rewrites the human page from it.
- Update the relevant `docs/` track: the reference page for any public-API change; the admin,
  editors, or extend narrative only as the freeze bullet above allows (a discovered deficiency
  fixed on the page, never a rewrite). Update `CHANGELOG.md` and the per-version record
  (`docs/extend/migration-notes.md`, outside the freeze and maintained every pass like the
  reference arm) for any **behavior** change, not only a rename, with a short per-version entry.
  (`docs/extend/upgrade-cairn.md` is the same, the short task, bump and verify; the record is the
  other half of that split.) The "Consumers must:" convention below applies to the changelog; a
  behavior change that needs no consumer action still gets an entry that says so, so an upgrader
  who hits it has a reference.
- **Hunt drift on a removed or renamed symbol.** When a pass removes a symbol from the public surface
  or renames it, the reference page is not the only place that names it. `grep -rn` the whole `docs/`
  tree (and `README.md`) for the old name and any reference anchor (`core.md#<oldname>`), and repoint
  or rewrite every hit. The reference-coverage gate does not catch a stale inbound link.
- **Run all five doc gates.** `npm run check:reference` (the export-coverage gate fails on an
  undocumented export), `npm run check:reference:signatures` (the documented signature must match the
  real exported type, so a member added to an exported function's return, like `helpLoad` on
  `createContentRoutes`, fails until the reference signature carries it), `npm run check:package` (the
  entry-point shapes), `npm run check:docs` (the link gate, which fails on a dead relative link or a
  stale `#anchor` anywhere under `docs/`), and `npm run check:facts` (the container gate). All five
  must pass. `check:reference:signatures` is CI-only
  and easy to skip locally, so run it by name here. A public-API change is not done until its reference
  page matches and no doc links to a name the pass removed.
- **Any public-surface change also runs `npm run check:surface`** and, when the drift is intended,
  `npm run check:surface -- --update` with the regenerated `docs/internal/api-surface.md` committed in
  the same pass. This is the third CI-only gate a local ritual skips (the 2026-07-07 harvest pass
  shipped a green local gate and failed CI on exactly this; the ambient `auditSink` addition needed
  the snapshot regen). A type-only change to an augmentation counts as surface.
- **Any pass that adds an export or touches a fenced `ts` block in `docs/extend` or `docs/reference`
  runs `npm run check:snippets`.** It packages the library and typechecks every documented code block
  against the BUILT package, so it catches what no other gate can: a doc importing a symbol from a
  subpath that does not export it, and a guide block calling site-local helper names that are never
  declared (the script only auto-stubs names appearing in an `import` clause; `declare` them in the
  block rather than reaching for `<!-- snippet-check-skip: -->`, since the declaration also tells the
  reader what shape their own helper must return). **This is the fourth CI-only gate a local ritual
  skips, and the worst one to skip: it sits at `.github/workflows/test.yml:35` and short-circuits
  every gate after it** (`check:prose`, `check:version`, `check:dev-package`, `check:consumers`,
  `check:comments`), so one bad snippet hides five other gates' results. The 2026-08-01 xcathletes
  seams pass ran the whole documented gate list green across four implementer dispatches and still had
  `check:snippets` red at 12 problems; three of them were a missing `Manifest` export on the very
  subpath that pass's headline function shipped on. Writing a new export and documenting it is not
  enough, since the export map has to carry every type the signature names.
- A pass that rules on a consultation item or executes an audit verdict updates
  `docs/internal/engine-rulings.md` in the same pass (accepts close with the one-line
  seam-fit report).
- Append any design friction the writing surfaced to `docs/internal/docs-friction-log.md`, one entry
  per finding with its perspective (developer or editor) and a short note.
- **Triage the WHOLE friction log, complete-or-move, every pass (Geoff, 2026-09-01).** The log is a
  staging area measured by what leaves it, so the pass-end sweep reads every open finding, not only
  the ones this pass added. Each entry resolves one of three ways: fixed and deleted (when the fix is
  cheap and in this pass's blast radius), promoted to the `ROADMAP.md` tier where it bites or to the
  pass that first leans on it (with the log entry removed on promotion), or deleted as overtaken.
  Verify against the code before acting; an entry records what was true when written. A ritual that
  only appended has not run this step. This repo keeps no separate backlog file.
- Keep `ROADMAP.md` current, the same as the reference docs. A pass that shipped a roadmap item marks it
  done and removes it from the live tiers; a pass that surfaced a new direction files it into the right
  tier. The roadmap is a forward view, not a changelog: shipped history lives in STATUS and the
  post-mortems. A backlog file only ever appended to drifts heavy and resurfaces dead work (the
  hardening initiative had to prune a stale friction log for exactly this), so prune as you go.

A docs-only pass skips the engine check and test (step 2) but still does this step, including the doc
gates. See the `docs-is-a-pass-dimension` memory.

### 6. Update tracking

**A pass does NOT bump the version or publish — that is the default, not the exception.** A finished pass
finalizes its `CHANGELOG.md` entry under `## Unreleased`, leaves `package.json` untouched, and stops: no
`npm version`, no `gh release create`, no publish. New versions are deliberate and meaningful, never a
per-pass reflex; cutting a release for every small change is the churn to avoid. The post-mortem, STATUS,
and changelog steps below run every pass. The release steps (the version bump and the publish) run ONLY
when a release is independently warranted: a consumer site needs the change now, or a coherent capability
or initiative has landed and is worth publishing. Otherwise hold and batch — `main` stays releasable, so
completed passes accumulate unpublished and a later publish rolls the window. When a cut IS warranted, the
release is its own procedure: invoke the **`cairn-release`** skill, which carries the gate, the free-number
check, the rolled notes, the OIDC publish, and the verify. Do not inline release mechanics here. See also the
"Releases (cadence and scheme)" section in cairn-cms `CLAUDE.md` and the `cairn-release-process-and-versioning`
memory.

Append the post-mortem to the active plan file (what was built, what was verified
with evidence, decisions locked in, blockers). Then update `cairn-cms/docs/STATUS.md`,
the canonical rolling status, with where the work is now, what is next, the open
decisions, and the carried follow-ups. STATUS.md lives on `main`, so update it there as
part of the merge. Durable cross-cutting gotchas stay as focused `cairn-*` memories, and
locked architecture decisions stay in the functional spec. Do **not** write cairn state
into a consumer site's `STATUS.md`; that is the site's own.

**STATUS is present tense only.** It is read in full at the start of every session, so a
finished pass parked there is a context cost paid on every session forever, for something
needed only at a post-mortem. Anything past tense goes to `cairn-cms/docs/HISTORY.md`
(create it if absent): the per-pass ledger, newest first, carrying what landed, what the
gate caught, and what a later pass would be wrong to rediscover. STATUS keeps the current
state, the immediate next action, the open decisions, and the carry-forwards, and nothing
else. This is the workstation-wide split (`~/.claude/CLAUDE.md`, "Project ledgers"); cairn
follows it like every other repo. STATUS reaching for a "what we did in pass N" section is
the signal to move, not to summarize harder.

**Changelog convention (enforced).** If the pass made any breaking change to the public
surface, its `CHANGELOG.md` entry must carry a `Consumers must:` line per breaking change,
stating the concrete consumer action (the rename, the moved import, the new required
argument). A non-breaking change needs no such line. This convention exists so a site
crossing several `0.x` versions reads the actions off the changelog instead of
rediscovering each rename. The `0.x` changes also accumulate in the per-version record
(`docs/extend/migration-notes.md`), one entry each; add the pass's entry there too,
for a behavior change as well as a rename.

**Releasing is a separate skill, not a step here.** When the cadence calls for a publish, invoke
**`cairn-release`**. It owns the whole procedure: the gate (is a cut warranted), the free-number check
(`npm view`; numbers are immutable), the version bump at the cut, the rolled release notes (the changelog
window since the last published tag, carrying every `Consumers must:` line), the `gh release create
v<x.y.z> --target main` that fires the OIDC publish, and the verify. A pass never inlines this.

### 7. Commit

Commit in the cairn-cms feature worktree, following the repo's git conventions.
Simplify first (step 1), commit specific files, and push or merge only when the user
asks.

### 8. Draft the next plan (while context is warm)

Preferred, not skippable lightly. The just-landed pass is fresh now: its patterns,
carried follow-ups, and lessons are in context, and re-deriving them cold next
session is waste. So before stopping, draft the next plan. Run
`superpowers:brainstorming` first to settle the open design decisions with the user
(the spec locks most of it; surface only what it leaves open). Probe until the plan
carries no open readings; the brainstorm's length is never a cost to trim (Geoff,
2026-09-04). Then `superpowers:writing-plans` to author the numbered plan file. Keep the
design-and-approval gate: never auto-write a plan without the user's calls on the
open decisions. The plan stays revisable next session. Skip only when the next pass's
direction is unsettled or the user wants to stop here.

### 9. Pre-bake and prep the context clear (ALWAYS, not on request)

**A finished pass always ends by prepping to clear context (Geoff, 2026-08-01). This is a step of
the ritual, not a thing to do when asked or when the session felt long.** A pass is an initiative
boundary, and every turn of a continued session re-buys the whole cached conversation, so a session
carried past its pass costs the next pass real money for context it does not need. The prep is the
same work whether or not the clear happens next, which is why it is unconditional: the artifacts are
crash insurance mid-session and the entire handoff across one.

Prepping the clear means the durable artifacts below are written, committed, and pushed, the tree is
clean, and the last thing the user reads is the exact resume prompt plus the launch directory. Say
plainly that the pass is closed and context is ready to clear. Anything load-bearing that exists
only in the conversation at that moment is a defect: **the test is that a session starting cold from
the resume prompt reaches the same next action, with the same constraints, having read only the
plan, the spec, STATUS, and memory.** Walk the pass's own decisions against that test before
declaring done, including the ones a reviewer or the user changed mid-pass, and including anything
about branch topology (a deferred merge changes where the next pass branches from, and a cold
session will branch off `main` by default and build against the wrong engine).

Plan and execution share the session regardless of model (revised 2026-08-21; supersedes the
2026-07-26 Opus-executes rule): a plan written here gets executed here. The pre-bake always
happens first, as crash insurance whether or not a clear follows. Do **not** run the
`superpowers:writing-plans` "which execution method?" question (these defaults answer it).

Every plan file's header carries a token ceiling and a checkpoint interval (default four
tasks). At each checkpoint, at any task or pass split, and before any question to the user,
write STATUS.md (task ledger, decisions taken, spend, next task), then continue.

- **Pre-bake the durable artifacts.** Commit the plan (push if the user wants it pushed).
  Update STATUS.md so its **immediate next action** line names the new plan, its path, and
  the method (main-loop execution, test-first, full gate per task, on a worktree off `main`).
  Refresh the relevant `cairn-*` memory so a cold session recalls the initiative. Leave the
  tree clean. Anything load-bearing must live in the plan, the spec, STATUS.md, or memory,
  never only in the conversation.
- **Then proceed straight into "Starting a plan" above**, in this same session. If a context
  clear intervenes anyway, give the exact resume prompt and the launch directory (inside
  `cairn-cms`, so its hooks and memory load). Example: "Execute the component grammar plan
  (`docs/superpowers/plans/<file>.md`)."

Continuing in the same session is for work *within* one pass (a plan drafted here, executed here).
It is not a reason to skip the prep above: prep the clear at the pass boundary either way, then
continue or hand off. See the `clear-context-before-implementing-plans` memory for the
same-session default's history and `cairn-pass-ends-with-context-clear-prep` for this rule.

## Execution discipline (lessons from Plan 07)

- **One implementer per dispatch, verified.** When dispatching `cairn-implementer` (parallel
  independent tasks, or a worktree-isolated change), wait for each result and verify its commit
  (git log and status) before depending on it. On an API overload or 5xx, wait and retry once
  deliberately; never fire a second dispatch while one may still be in flight, because a cleared
  overload fires every queued retry at once. See the `plan-execution-dispatch-discipline` memory.
- **Verify a plan's factual claims about existing code before dispatch, not at review.** A plan
  that ports or mirrors sibling code states facts a grep can check: a count of literals, an error
  code's meaning, which path a CLI writes to, a response's shape. Each one that is wrong costs a
  full fix round (implementer, reviewer, gate) when a reviewer finds it, against a minute when the
  conductor's pre-flight does. Go tool pass A (2026-09-20) paid that five times in seven tasks: a
  step count of eighteen that was nineteen, an error code read as "not connected" that meant
  "no such route", a directory precedence whose second branch was unreachable, a criterion no
  fixture could satisfy, and a permission list one group short. Before launching a segment,
  dispatch one `haiku` or `sonnet` pre-flight over that segment's tasks: list every checkable
  factual claim, check each against the tree at HEAD, and return the ones that fail. Amend the
  plan first, then dispatch.
- **Verify a plan's locked build assumptions.** When a plan locks a packaging, build, or
  module-resolution mechanism (for example `publishConfig.exports`, an export condition, or a
  source-to-`dist` swap), confirm it against the real toolchain at the first task that touches it
  rather than trusting the lock. Plan 07's locked `publishConfig.exports` swap did not work on
  npm 11.
- **Vale findings are tiered.** The `vale-hook` drives a fix only on an error-tier finding (exit 2);
  warnings and suggestions ride along as advisory context. Do not gate commits or spend effort on the
  advisory tier, especially when it sits in a doc's pre-existing body.
- **Suggest the Workflow tool at the right moments.** It runs only on the user's explicit
  opt-in ("use a workflow"), so name the moment when it would pay off, including the review
  gate of a large pass (an adversarial find-and-verify sweep catches more than the flat
  reviewer fan-out), a plan whose tasks are mostly independent, and a repo-wide audit or
  migration. One sentence naming the shape and rough scale is enough.

## When NOT to use

- A site's own numbered passes: use `site-pass`.
- Mid-plan debugging or single-file edits.
