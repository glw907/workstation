# Finishing drafter to pilot-ready

## Brief

Approving this builds the rest of drafter in five passes. At the end, cairn's waiting drafting run can send its pages through drafter on your API credits.

Only the plan checker exists today. cairn's stage 2b part 2 has 11 checked plans waiting for a drafter that can draft them, and your monthly credits expire unused until it can.

### What changes

- drafter gains `drafter page`, which drafts, gates, reviews, and redrafts each planned page through batched API calls, plus `drafter config`, `drafter spend`, and `drafter check-prompts`.
- The docs page chain gains a switch that stops after framing and hands the pages to drafter. Without the switch it runs as it does today.
- drafter gets its own docs: a README, the reference pages, and a setup guide.
- The eight open drafter issues (#2 to #5, #7 to #10) close.
- cairn gets a `drafter.toml`, and its docs review page learns to show YAML plans.

### If you approve

1. A planning session writes all five pass plans and has them reviewed, without you.
2. `conductor-drafter` runs the passes in order, unattended. Passes 1 and 4 merge themselves. Passes 2, 3, and 5 come to you as PRs.
3. Before pass 5, you set up drafter's API key (see "Your setup step"). Pass 5 waits for it.
4. Pass 5 ends with one real cairn page run through drafter, then reports it pilot-ready. cairn's own drafting run is the pilot, and cutover stays your call.

### Decide: Risk class for the key and the spend ledger

Code that holds the API key, or decides whether money gets spent, is ordinary by default. That means no test-first and no per-task review. A wrong cap check spends real credits.

Source: pass-core, "only Geoff's ruling raises a class"

- Raise pass 2 to auth-data: test-first, a review per task, and your PR read (recommended)
- Leave it ordinary

### Decide: Live spend during the build

Two runs touch real credits: the smoke test (one Haiku request per seat shape, under $1) and the cairn page run in pass 5 (about $3 to $5 by the spike's figures).

- Approve up to $15 of live spend across the initiative, with a stop past it (recommended)
- Stop and ask before each live run

### Decide: When a plan runs long

Each pass carries a path estimate below. Earlier drafter passes finished well under their plans, so plans tend to overshoot the design.

Source: pass-core, "Design" (the intake-1 overnight stop)

- A plan up to 3x its pass's estimate proceeds without you; past that it stops (recommended)
- Stop at 2x, the default

### Worth knowing

The spike's recorded evidence (`~/.local/share/drafter/`) is gone from disk, and so is the interim format sheet. The tests will use synthetic fixtures and logs regenerated from cairn's real docs gate, which the public repo needed anyway. If you have a copy of the spike directory, point a session at it and the fixtures get richer. Nothing depends on it.

### The five passes

Each pass is one PR in `glw907/drafter`, plus the companion PRs named. Path estimates are in minutes.

1. Foundations, 120, ordinary. `atomicfile`, `config` with its three layers and refusals, `run` (IDs, run directories, locks, retention), `drafter config`, and the eight open issues.
2. Key and money, 180, auth-data if you rule so. `key`, the `batch` client in both modes with the failures table, `ledger` with reserve, settle, caps, and cycle reset, `drafter spend`, and `make smoke` (run live once at close).
3. Prompts and handoff, 180, runner. `prompts` on goja, `handoff` for files and Workflow run files, and `drafter check-prompts`. A dotfiles PR adds `DRAFTER_HOST`, `DRAFTER_SEATS`, `backHalf`, the `handoffFor` block with its node test, and the `check-prompts --expect` leg in the dotfiles gate.
4. Page parts, 180, ordinary. `assemble`, `edits`, `coverage`, and `gate`, each tested against its spec rows.
5. The pipeline, 240, runner. `pipeline` with the stop table, resume, and concurrency, then `drafter page` with `--dry-run`, drafter's docs, and the end-to-end check. A cairn-cms PR adds `drafter.toml` and the review page's YAML plan support.

### The end-to-end check

One real cairn page reaches `accepted` or escalates with an empty `faults` list. In a scratch cairn worktree, the chain runs with `backHalf: "drafter"` on one 2b part 2 page. `drafter page --workflow-run` then takes it through every stage in batch mode. `drafter spend` must match the Console within 5%. The page is thrown away; cairn's drafting run redoes it.

### Your setup step

The Console is the only place to create the workspace, its key, and its spend limit. Before pass 5:

1. Create a Console workspace for drafter and set its spend limit (your install: $160).
2. Create a key in it, then run `secret-receive DRAFTER_API_KEY`.
3. Give the session the workspace ID; the key setup records it in your user config.

### Out of scope

The pilot itself, cutover, and sub-projects 2 to 5. Figure and rework pages stay on the chain, as the spec says. Anything a pass finds goes to its PR's "Found, not done" list.

## Technical notes

- Approved by Geoff, 2026-10-13, with unattended planning and execution. Rulings, each a standing
  approval the planner and conductor apply in place of stopping:
  1. Pass 2 is `auth-data` ("You can use it."): test-first, `diff-reviewer` per task, Geoff's PR read.
  2. Live spend up to $15 across the initiative runs without asking. A run whose next live request
     would take the initiative's ledger total past $15 stops and notifies.
  3. A pass plan whose path minutes stay within 3x its estimate above proceeds. Past 3x it stops,
     with one question in STATUS and `notify-send -u normal`.
  4. Pass 5's live steps wait for the key setup. If `DRAFTER_API_KEY` or the workspace ID is
     missing when pass 5 reaches them, the conductor notifies and waits; the offline tasks run first.
  5. Geoff opts in to one Workflow run: pass 5's end-to-end chain run with `backHalf: "drafter"`
     on one page. No other Workflow run is approved (2026-10-13).
  6. `billing_cycle_day` is 1 (2026-10-13).
  7. This machine is `pavilion`, set up 2026-10-12; `~/.local/share/drafter/` and
     `~/.local/share/cairn/` stayed on `thinkpad-x1`. Both were restored 2026-10-13 by rsync over
     a temporary SSH opening, since closed (28 MB and 90 MB, 69 captures). The spike evidence is
     a reference again; drafter's tests stay synthetic, since the repo is public. `tellgrader` is
     not installed here: pass 5 installs it before its live run.
  8. Plan-review rulings (Geoff, 2026-10-13):
     - Pass 5's reserve-before-submit path and its resume task are `auth-data`.
     - Pass 1's config task stays `ordinary`; its cap, layer-refusal, and ignore-check tests are
       written first and named in the close review's dispatch.
     - The end-to-end check also requires the record to show the round-1 reads ran. An earlier
       escalation gets one rerun if the budget allows; otherwise the PR says "not pilot-ready"
       and why.
     - The $15 stays. A rerun's page cap is set to the budget left, so the ledger itself stops
       at $15; if that is too little to run, the pass stops for Geoff.
     - Pass 2's live smoke moves to pass 5 (no key exists before then), and pass 2's PR brief
       says so up front. The "within 5% of the Console" comparison is done by Geoff at the
       pass 5 PR read; the PR states pilot-ready conditional on it.
     - Pass 4's `assemble` stays `ordinary` on the same footing as pass 1's config task: its
       path-safety rows (`..`, symlinks, separator boundaries) are written first and named in
       the close review. Applied by the planning session from the pass 1 ruling; Geoff may
       overrule at any PR read.
- Spec: `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, reviewed and folded 2026-10-12. No new spec; each pass plans from its sections. `spec-plan-review` sets plan review depth per pass.
- Built so far: Pass 0 (drafter#1, workstation#36) and F1 (drafter#6), `internal/plan` only.
- Recent actuals: Pass 0 ran about 64 minutes of clock against 685 task-minutes; F1 about 35 against 175. The estimates above sit between those actuals and the planned figures.
- Executors run on Sonnet at medium, the conductor on Opus at medium, planning on Opus at high, per `pass-core`.
- Live-account flag: pass 2 (the smoke run) and pass 5 (the cairn page).
