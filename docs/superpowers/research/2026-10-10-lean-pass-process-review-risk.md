# Lean pass process spec review: risk lens

Target: `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md` at `a0fa4b6`. Lens: what breaks
during and after the cutover. Approved rulings are not relitigated. Every claim below was read from
the file it cites on 2026-10-10.

Counts: 2 blocker, 6 major, 2 minor. Owner forks: 2 (B1, M1).

## Blockers

### B1. CI is the full gate in only two of eight repos (OWNER FORK)

- **Location:** spec:80, :85, :98, :120.
- **Defect:** The spec retires the local full gate and lets "CI green on the head" stand in for it.
  Only cairn-cms (`test.yml`, `e2e.yml`, and others) and aksailingclub-org (`ci.yml`) have test CI.
  dubplate, xcathletes-org, and the dotfiles repo have no workflows at all. ecxc-ski, 907-life, and
  cairn-pub have only `deploy.yml`, which runs on `push: branches: [main]` with no check or test step.
  In those six repos no step runs the whole suite before merge. In three of them the merge itself
  deploys to production. Ruling 3 (behavioral, security, contract caught before merge) fails there.
- **Evidence:** dubplate's rung 14a plan says it outright: "dubplate has no CI (`.github/workflows` is
  absent)" (`~/Projects/dubplate/docs/superpowers/plans/2026-10-10-rung-14a-admin-api.md:79`). That
  pass is `auth-data` (`:25`). The dotfiles gate is local only (`scripts/check.sh`, STATUS "Gate").
- **Compounding:** The success test (spec:165-167) scores only cairn pass B, the one repo where the
  CI swap is sound. The riskiest first runs go unmeasured.
- **Options:**
  - (a) Repos without test CI run their local full gate once, on the head, at close, before the PR.
    The adapter names the command, for example `scripts/check.sh` or `npm run check && npm test &&
    npm run test:e2e`.
  - (b) Rollout step 3 adds a test CI workflow to each of the six repos.
  - (c) Do (a) now and file (b) on each repo's ROADMAP.
- **Recommendation:** (c). It costs one gate run per pass, adds no new infrastructure to the
  cutover, and restores ruling 3 at once.

### B2. Cutover edits go live mid-edit, and the rollout order leaves dangling skills

- **Location:** spec:147-157.
- **Defect:** `~/.claude/{skills,agents,workflows,docs}` are whole-directory symlinks into the
  dotfiles working tree. A write "is live machine-wide the instant it lands"
  (`docs/HISTORY.md:122-127`). The resume prompt launches from the `~/.dotfiles` main checkout
  (`docs/STATUS.md`, "Immediate next action"), and dotfiles has no worktree (`git worktree list`). So
  every intermediate state of step 1 reaches every concurrent session: a deleted runner, or a
  half-rewritten `pass-core` or global `CLAUDE.md`.
- **Window one:** After step 1, `cairn-pass` still says "Run the chain per `pass-core`" (`skills/cairn-pass/SKILL.md:33`)
  and `site-pass` says the same (`skills/site-pass/SKILL.md:28`). That chain is gone, and the
  `pass-core` sections those skills cite are gone too.
- **Window two:** Step 2 puts `cairn-pass` "on a cairn branch merged by PR" (spec:154-155), but the
  skill lives in dotfiles (`readlink -f ~/.claude/skills/cairn-pass` resolves to
  `~/.dotfiles/claude/.claude/skills/cairn-pass`).
- **Window three:** Deleting the runners turns the dotfiles gate red. `scripts/check.sh:44` runs
  `tests/pass-execute-runners.test.mjs`.
- **Fold:** Reorder the rollout so additive changes land first and deletions land last, in one
  atomic merge.
  1. Land the backward-compatible changes first: the `cairn-run-gate` fixes, then the cairn PR that
     adds the fast-lane mode and shards CI e2e. Old passes keep working.
  2. Cut one dotfiles branch in a worktree. It carries the global `CLAUDE.md`, `pass-core`,
     `spec-plan-review`, both adapters (they live in dotfiles, so they move from steps 2 and 3 into
     this step), the implementer trims, the doc folds, the runner deletion with its test and its
     `check.sh` line, and the stale-reference sweep (m2).
  3. Before merging, run the one-executor check across every repo. Merge as one commit and tag its
     parent `pre-lean-process`.
  4. Then sweep each repo's `CLAUDE.md` and STATUS.

## Majors

### M1. dubplate's rung 14a plan is written entirely on the deleted machinery (OWNER FORK)

- **Location:** spec:136, :156-157, and the spec's silence on dubplate's pending plan.
- **Defect:** The plan is waiting on Geoff's approval, and every part of it depends on machinery the
  spec deletes.
  - It names `pass-execute` as its mode, one invocation per segment (`2026-10-10-rung-14a-admin-api.md:107-116`).
  - It cites `pass-execute.js:857` for the executor (`:81`).
  - It arms guards from `unattended-work-guards.md` (`:116`) and runs `code-simplifier` at close
    (`:817`).
  - Its ceiling is 11.8M across four segments (`:26-33`).
- **Missing from the spec:** The file table (spec:136) trims only `cairn-implementer` and
  `site-implementer`. dubplate's own `.claude/agents/dubplate-implementer.md` and its runner shim
  (`scripts/checks/gate-tier.mjs:2`, "The pass-execute shim") are not listed. dubplate has no adapter
  skill, so "Each repo's adapter skill maps paths to classes" (spec:63) has no home there.
- **Live-session signal:** `git status` shows warm uncommitted agent-memory files in dubplate, and its
  last commit landed 66 minutes before this review. A session there may approve the plan and launch
  it into B2's window.
- **Options:**
  - (a) Hold rung 14a and re-plan it in the lean shape after the cutover. Give dubplate an adapter
    section in its `CLAUDE.md` or `.claude/`.
  - (b) Run rung 14a on the old machinery first and delay step 1 until it closes. The plan prices
    that at about 6.8 to 8.3 hours.
- **Recommendation:** (a). The plan is unapproved, so no execution is lost, and (b) holds the
  machine-wide cutover hostage to one repo. Either way, record the hold in dubplate's STATUS before
  step 1 merges.

### M2. An auth change can be classed `ordinary` and skip the per-task read

- **Location:** spec:62-63, :82, :100, :160-161.
- **Defect:** The spec sets the risk class once per pass, at design time (spec:62). The per-task
  review, though, keys on "`auth-data` tasks" (spec:100). Nothing computes a task's class from its
  paths. The "adapter path map" is prose in a skill. Today's classifier takes the class only as a
  flag (`~/Projects/cairn-cms/scripts/checks/gate-tier.mjs:132-133`, `:498`), and its `protected`
  list covers only the gate's own files (`scripts/checks/gate-table.json:288-294`).
- **Live case:** Pass B is classed `engine-logic`, with a Task 2 override to `auth-data`: "it edits
  D1 provisioning beside `AUTH_DB`" (`.claude/worktrees/engine-pre-2b-b/docs/superpowers/plans/2026-10-08-engine-pass-pre-2b-b.md:27`, `:628`).
  Under one class per pass, that override disappears, and the spec re-gates the unreviewed Task 2 WIP
  with no read at all (spec:160-161). The close's auth checklist loads "by the paths the diff touched"
  (spec:80-81). The touched paths, such as `packages/create-cairn-site/src/cloudflare/config.mjs`, are
  not auth-named, so that checklist may not load. The live auth smoke then skips too, since it runs
  only "on `auth-data` passes" (spec:82).
- **Fold:**
  - A task's class is the higher of the declared class and a computed class.
  - The adapter computes the class with a script, extending `gate-tier.mjs` (and dubplate's
    equivalent) with an `authData` path table: `src/lib/auth*/`, `src/lib/admin/csrf*`,
    `migrations/`, `hooks.server.ts`, and `packages/create-cairn-site/src/{github,cloudflare}/`, plus
    each site's equivalents.
  - The session runs the script on every task diff. An unmapped path under `src/lib/` fails closed
    to `auth-data`.
  - On resume, pass B's `dbdc4556` gets the `auth-data` read along with the fast lane.

### M3. Pair commits get no CI, and their merge-back is unspecified

- **Location:** spec:93, :98.
- **Defect:** "The task pushes" assumes the push runs CI. cairn CI triggers only on a push to
  `main`/`rebuild` or on `pull_request` (the `on:` blocks of `test.yml`, `e2e.yml`, `scaffold.yml`,
  and `design.yml`). A pair's Agent-tool worktree branch has no PR, so its pushes run nothing. That
  is the same defect as the catch ledger's top S1 blocker, "Chains have no PR" (ledger:26). The spec
  also never says who merges a pair into the pass branch or who gates the merged result.
- **Fold:** Pair subagents commit on their worktree branch and never push. The executing session
  merges each pair into the pass branch (the one with the draft PR), runs the fast lane on the merged
  head, and pushes that. A merge conflict stops the line.

### M4. Fresh worktrees give false greens, and the setup lesson lives only in HISTORY

- **Location:** spec:93-97, plus ruling 8 (spec:40-41).
- **Defect:** Every pair runs in a fresh worktree, so every pair hits the worktree-setup trap.
  - The setup steps are recorded only as HISTORY prose: "`npm run check` in a worktree needs
    `NODE_OPTIONS=--max-old-space-size=6144`" and "A fresh worktree needs `npm ci`, or vitest resolves
    the main checkout's install" (`~/Projects/cairn-cms/docs/HISTORY.md:219-220`, also `:512`,
    `:812`).
  - The worst case: "a worktree showcase e2e proves MAIN's engine" until a reinstall
    (`docs/internal/durable-gotchas.md:32-38`).
  - The catch ledger counts this lesson among three re-hit inside 48 hours (ledger:114).
- **Consequence:** In cairn, CI catches the false green at the cost of a red cycle. In repos without
  CI, it escapes (B1).
- **Fold:** The adapter's fast lane opens with an idempotent worktree-prep step: `npm ci` at the
  root and in the showcase, `npm run package`, `svelte-kit sync`, and `NODE_OPTIONS` for the type
  check. Step 1 also harvests the last passes' "wrong to rediscover" bullets into executing homes
  before HISTORY freezes. Another example is the `pgrep` self-match (`docs/HISTORY.md:88`), which the
  one-executor rule needs.

### M5. Unattended runs lose the outside watcher, and the clock stop is self-enforced

- **Location:** spec:101, :141.
- **Defect:** "A task past twice its estimate stops" asks the executing session to notice that it
  is stuck. The guard doc holds the opposite: "Nothing intervenes unless the main loop watches from
  outside" (`claude/.claude/docs/unattended-work-guards.md:9`).
- **What spec:141 would delete:** "Fold what still executes ... delete the rest" names no list. The
  session-armed guards that remain at risk are:
  - the API-drop wake-up (`:97-109`, five hours lost on 2026-09-20);
  - the lid-switch hold (`:135-142`);
  - the battery stand-down (`:90-95`).
- **What survives on its own:** The sleep inhibitor is hook-enforced (`claude-awake-touch`, four
  hits in `settings.json`), so it stays.
- **Tool mismatch:** `claude-wf-guard` is built for Workflow runs (its header comment), and the new
  executor is a single session.
- **Fold:** `pass-core` has every execution session arm two guards at launch.
  - A dynamic `/loop` tick with a 1200-to-1800-second fallback. It reads the current task's start
    time and estimate from STATUS, enforces the clock stop from outside, and resumes after an API
    drop.
  - The lid-switch hold, whenever the laptop may close.

  The battery stand-down moves into `pass-core`. Retarget `claude-wf-guard` at pair subagent
  transcripts, or retire it by name.

### M6. Concurrent fast-lane legs can exhaust memory with pairs and two projects running

- **Location:** spec:95-97.
- **Defect:** The fast lane's legs "run concurrently" and take a lock only for e2e. The machine has
  15 GB of RAM (`free -g`), and cairn's type check alone needs a 6 GB heap (HISTORY:219). Two pair
  fast lanes, each running svelte-check and vitest, beside another project's heavy gate (8 GB scope,
  `bin/.local/bin/cairn-run-gate:249`) overcommit the machine.
- **Consequence:** The kernel OOM killer has twice killed whole Ptyxis scopes, along with the Claude
  sessions inside them (`claude/.claude/docs/oom-defense.md:3-15`).
- **Fold:** The fast lane runs inside `cairn-run-gate`'s light-lane memory scope. Its type-check leg
  takes the light lock. Measure one fast lane's peak RSS before pairs become the default.

## Minors

### m1. No rollback path

- **Location:** spec:163-167.
- **Defect:** A miss changes "only that row". If the new machinery itself fails, for example a
  broken `pass-core` after the cutover, nothing restores the old machinery.
- **Fold:** B2's single merge commit and its `pre-lean-process` tag make rollback a single revert.
  State that in the spec.

### m2. The step 1 sweep covers skills and agents but not docs or consumer repos

- **Location:** spec:152.
- **Defect:** Stale references remain in places the sweep does not reach: `docs/claude-tooling.md:52-55`,
  `docs/fable-post-cutoff-system.md:5`, `docs/claude-md-archive.md:52`, dubplate `CLAUDE.md:123`
  and `:252`, and the cairn `scripts/checks/gate-tier.mjs:2` header.
- **Fold:** Widen the sweep to `claude/.claude/docs/` and run `tests/test_check_claude_refs.py` as
  the step's check.

## Checked, no finding

- **CI minutes:** both CI repos are public (`gh repo view`).
- **cairn CI coverage:** cairn CI runs every local close-gate check, the docs checks through
  `check:docs-gate` (`test.yml:135-144`).
- **Pass B:** it is paused with a recorded resume path (cairn `docs/STATUS.md:25-28`).
- **Other in-flight passes:** no site repo has a pass in flight on the runners.
- **Over-ceremony:** none found within this lens.
