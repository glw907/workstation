# drafter pass 5 plan: the pipeline

Design: `~/.dotfiles/docs/superpowers/specs/2026-10-13-drafter-completion-design.md`, pass 5, "The
end-to-end check", "Your setup step", and Technical notes 1 to 8, approved by Geoff on 2026-10-13.
Spec: `~/.dotfiles/docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, sections "The
pipeline" (stages, stop rules, the final reader's two turns, projects without facts, shared
worktree), "Records", "Run inputs", "One run per worktree", "Resume", "Concurrency", "Failures",
"Models", "The tool" (the `pipeline` row and `drafter page`), "drafter's own docs", "A server-side
backstop" (for the setup guide), and "Testing" (the pipeline state machine row, the facts-free
stage-1 row, the end-to-end paragraph, the `make smoke` paragraph, and the edit-contract rows pass 4
left to the pipeline). Fold record:
`~/.dotfiles/docs/superpowers/research/2026-10-13-drafter-completion-plan-fold.md`.

## Outcome

`drafter page` takes each planned page through every stage, in batch or sync mode, ends it accepted
or escalated with a full record, stops and resumes without paying twice, and never spends past a
cap. drafter carries its own docs. cairn gets a committed `drafter.toml`, and its docs review page
shows YAML plans. The smoke runs live on the production request shapes, and one real cairn page goes
through the chain's front half and drafter's back half on Geoff's API key. The pass reports drafter
pilot-ready, conditional on Geoff's Console comparison at the PR read.

## Shape

- Risk class: P5.1 (its reserve-before-submit path) and P5.2 (resume) are `auth-data` by Geoff's
  ruling (Technical notes 8): test-first, a task-scope `diff-reviewer` read per task, Geoff's PR
  read, and never `RUN_GATE_IF_BUSY`. The other drafter tasks are `ordinary`. P5.5 is `ordinary`:
  cairn-pass's path map puts `scripts/docs-review/**` under `ordinary`. The pass takes its highest
  class, `auth-data`.
- `live-account` flag: yes. P5.7 and P5.8 spend real API credit, inside the initiative's $15
  standing approval. P5.8 runs the one Workflow run Geoff opted in to (ruling 5).
- Repos and branches:
  - `~/Projects/drafter` (`glw907/drafter`): the executor launches from the main checkout and works in
    the worktree `EnterWorktree` creates (name `p5-pipeline`).
  - `~/Projects/cairn-cms` (`glw907/cairn-cms`), through the `cairn-pass` adapter: the session
    creates `git -C ~/Projects/cairn-cms worktree add .claude/worktrees/drafter-pipeline -b
    drafter-pipeline origin/main` and runs cairn-pass's setup command there. The e2e's scratch
    worktree (P5.8) is a second one, never pushed.
- Gates: drafter, from the drafter worktree, `DRAFTER_DIR="$PWD" bash
  ~/.dotfiles/scripts/drafter-gate.sh`, whose full-suite home is that gate once on the close head;
  cairn, cairn-pass's fast lane (`node scripts/checks/gate-tier.mjs --fast --range <base>..HEAD`,
  each leg through `cairn-run-gate`), with CI on the draft PR as the full-suite home and `ci-green
  <sha> --pr <n> --wait` as a background watch.
- Clock file: the drafter worktree's git dir. A wait on Geoff (P5.7 or P5.8) removes the clock
  file first, so the wait never trips the clock stop, and writes a new `start=` when it ends.
- Path estimate: 610 minutes. P5.1 and P5.5 as a pair (200), P5.2 and P5.6 as a pair (130), P5.3 and
  P5.4 as a pair (70), P5.7 (40, not counting the wait), P5.8 (120), Close (50). The design's
  estimate is 240, so the path is 2.5 times it, inside the 3x line (720).
- Pair subagents run on `sonnet` at `medium` with the `description` `p5-pipeline task <n>`.
- Standing approvals (design, "Technical notes"):
  - The plan proceeds within 3x.
  - Live spend up to $15 across the initiative runs without asking. The meter is this branch's
    `drafter spend --since 2026-10-13 --json`, built by `make -C <drafter worktree> build`: its
    `total` plus `open.worst`. The smoke runs when the meter plus $1 stays at or under $15. A page
    run carries `DRAFTER_PAGE_CAP` set to the smaller of 10 and 15 minus the meter (ruling 8, so the
    ledger itself stops at $15) and `DRAFTER_CYCLE_CEILING=15`; caps resolve lowest-wins with the
    environment included (pass 1). When that page cap would be under $5, the spike's top page cost
    rounded up, the pass stops for Geoff. `DRAFTER_CYCLE_CEILING` counts from the cycle start
    (billing day 1, ruling 6), so it guards the initiative only while it stays in one cycle; the
    meter's `--since 2026-10-13` guards it across a reset.
  - A live run that exits 3 with `cycle cap` or `spend limit` runs `notify-send -u normal` and stops
    for Geoff (ruling 2).
  - The live steps wait for Geoff's setup (ruling 4). Every offline task runs first.
  - Both PRs go to Geoff through the conductor; the executor never merges.
- Depends on, checked at launch by the conductor and again by P5.8: passes 1 to 4 merged on drafter's
  `origin/main` (`internal/{config,run,key,batch,ledger,smoke,prompts,handoff,assemble,edits,coverage,gate}`
  all present); pass 3's dotfiles PR merged and live (the chain's `backHalf`); and cairn's exemplar
  captures on disk under `~/.local/share/cairn/exemplars/` (restored 2026-10-13). `tellgrader` is
  installed in `~/.local/bin` (2026-10-13).

## Interfaces

Consumes: from pass 1, `config.Load`, `(*config.Config).Validate` with `config.ScopeRun`,
`(*config.Config).Sources`, `atomicfile.WriteFile`, every `run` export; from pass 2, `key.Resolve`,
`*batch.Client` and its method set, `batch.Request`, `batch.Result`, `batch.Classify` and its
`Action` constants, `batch.ErrSpendLimit`, `batch.ErrTransport`, `batch.ErrMaybeSent`,
`batch.ErrNoWorkspaceCheck`, every `ledger` export, and `internal/smoke`; from pass 3,
`prompts.Load`, `prompts.Context`, `prompts.Round`, `(*prompts.Module).Render`,
`handoff.ReadFiles`, `handoff.ReadWorkflowRun`, `(handoff.Handoff).Verify`; from pass 4, every
`edits`, `coverage`, `gate`, and `assemble` export; from Pass 0 and F1, `plan.CheckFile`,
`plan.CheckOptions`, `plan.CheckFactsDir`, `plan.LoadFacts`, `plan.LoadOutlines`.

Creates:

- `pipeline.API`: the consumer-side interface over `*batch.Client`'s methods (`CheckWorkspace`,
  `CountTokens`, `Create`, `Get`, `Results`, `List`, `Send`), declared here as go-conventions asks,
  since the fake is its second implementation. The fake rejects a `custom_id` that doesn't match
  `^[a-zA-Z0-9_-]{1,64}$` (the batches create reference, read 2026-10-13).
- `pipeline.Options` (the configuration, the handoffs, the API, the resume run ID, dry run, and a
  clock) and `pipeline.Run(ctx, Options) (Summary, error)`. `Summary` holds each page's final status
  and the run's stop reason, one of: none (the run finished), `cycle cap`, `spend limit`,
  `transport` (`batch.ErrTransport`; no page's state changes), `infrastructure` (`canceled` or
  `expired` a second time, or the gate's vanish), and `tree red outside drafter's pages`. Every stop
  reason is resumable and escalates no page. `drafter page` maps a `Summary` to its exit code: 3
  when the run stopped, which outranks 1; 1 when it finished with any page escalated; 0 when every
  page was accepted.
- `run.State` and `run.PageState` gain the intents (stage, attempt, timestamp, the ledger intent ID,
  `custom_id`s and the map from each to its page), batch IDs, saved answers, and write hashes resume
  needs, with `run.StateSchema` bumped. A `custom_id` is `<run ID's random suffix>_<first 12 hex of
  the SHA-256 of the page key>_<stage>_<attempt>`, inside the API's 64-character pattern for any
  page path.
- `internal/plan` gains one exported constructor that builds an `Outline` from outline files plus a
  list of repo-relative page paths, for stage 1.

## Out of scope

The pilot itself, cutover, sub-projects 2 to 5, figure and rework pages, the agentic fact read, a
`claude -p` reader, prompt caching, and every cairn change beyond `drafter.toml`, `.gitignore`, the
review page's YAML plans, and the ledgers.

## Tasks

Every drafter task starts by invoking `go-conventions`. The offline tasks (P5.1 to P5.6) all run
before P5.7. Every pipeline test sets the key variable to a sentinel shaped like an `sk-ant-` key.

### P5.1 The pipeline's stages and stop rules (200 min, auth-data)

- Order: the money rows (marked "money" below) are written and committed failing first, then the
  rest of the tests, then the code.
- Outcome: `internal/pipeline` runs each page through the spec's seven stages, with these rules:
  - Stage 1 runs `plan.CheckFile` with `CheckOptions` `Root` (the project), `FactsDir` (`facts.dir`,
    after `plan.CheckFactsDir`), and an `Outline` built from the outline file the handoff's
    `context.args.outline` names (repo-relative; the chain passes the same flag to `drafter
    check-plan`) plus every page of the run, so a link to an outline page not yet on disk warns
    and doesn't escalate. A handoff with no context uses the run's pages alone. With a facts store,
    one batched consistency read follows, built by `assemble.ConsistencyPrompt`. A markdown plan
    skips stage 1 and every plan-dependent check, with a warning, and the record notes
    `plan_format: markdown`.
  - The money path: each submission unit (one batch, or one sync request) runs `CountTokens` on each
    of its requests, sums `ledger.Worst`, calls `ledger.Reserve`, writes the state intent with the
    reservation's intent ID, and only then calls `Create` or `Send`. `ErrPageCap` escalates the page
    with `cap` and sends nothing; `ErrCycleCap` stops the run with `cycle cap`. Every result
    settles: unbilled ones at zero. An `ErrMaybeSent` from `Create` lists, waits on (`Get` until
    ended), and matches batches by `custom_id` through `Results` before anything is resubmitted; an
    unmatched intent settles `void` and its resubmission is a new intent. An `ErrMaybeSent` from
    `Send` settles that attempt `estimated` and resubmits it as a new attempt. Every resubmission
    counts against its failures-table budget.
  - The round-1 snapshot is written to the run directory and stored with `git hash-object -w --
    <snapshot>`, as the chain does (`docs-page-chain.js:1463`), so a seat input's `git cat-file blob
    {baseline}` reads it.
  - The seat contexts follow pass 3's context object; findings reach a redraft as
    `edits.Render`'s text; declined blocking findings reach that seat's next read through
    `assemble.Input.Declined`.
  - A seat left out of `seats` removes its stages and its stop-table rows, and the record names it.
  - Without a facts store, stage 1 sends no consistency read, coverage skips `fact` items, and the
    record notes `facts: none`.
  - Every row of the stop table and of the failures table, with `retries.gate_fix` and
    `retries.edit_contract` (shared between refusals and red gates after applied edits) as budgets,
    and every stop reason in `Summary`. An action pass 2 names beyond the spec's table
    (`ActionSpendLimit` on a result, an unlisted error type, an unlisted stop reason) takes the action
    pass 2 gives it.
  - The index-link command runs through `gate.Run` with `Protocol` `plain`. The files it changes
    (`git status --porcelain` before and after) count as drafter's own writes: snapshotted before,
    hashed after, restored on escalation.
  - Shared worktree: a page whose gate is red with nothing of its own holds and is gated again after
    the other pages settle; a foreign red that persists after every other page has settled stops the
    run with `tree red outside drafter's pages`. An escalating page's page and brief go back to
    their pre-run snapshots, or are removed when drafter created them, recorded as a write with its
    pre- and post-write hashes, and the draft stays in the record as `final.page.md` and
    `final.brief.json`.
  - Records: each page's directory holds its request bodies, responses, edit-contract answers, gate
    excerpts, snapshots, finals with their hashes, and `record.json` with every field the spec's
    "Records" lists. A record never holds an SDK error struct or an HTTP request. `faults` is
    computed on every page.
  - Concurrency: up to `pages_in_flight` pages; in batch mode one sequential poll loop over every
    in-flight batch, in sync mode one streamed request at a time; gates one at a time; no goroutines.
- Files: `internal/pipeline/` with tests and `testdata/` (a synthetic project, handoffs, a
  chain-shaped prompts module, and scripted fake API answers); `internal/plan/outline.go` and its
  test.
- Acceptance, the spec's pipeline state machine row and the rows pass 4 left here, against a fake
  `pipeline.API` whose every fallible method carries an error field:
  - Money: a stage whose `CountTokens` puts input under the page cap and input plus `max_tokens`
    over it escalates with `cap`, and the fake records zero `Create` and `Send` calls; its twin with
    a smaller `max_tokens` proceeds. A reservation that would cross the ceiling stops the run as
    `cycle cap`; `ErrSpendLimit`, and an `errored` result classified `ActionSpendLimit`, stop it as
    `spend limit`; each prints the resume line and escalates no page. Every `Create` and `Send` the
    fake records follows a reserve line and a state intent for it. Every result leaves one settle
    line. A `Create` that returns `ErrMaybeSent` after the fake recorded the batch is adopted with no
    second `Create`; its twin, where the fake recorded nothing, resubmits once and voids the first
    intent. A `Send` that returns `ErrMaybeSent` leaves one `estimated` line and one new reserved
    attempt.
  - One test per trigger, not per row: the draft's truncated answer, unparseable answer, and
    non-JSON brief; the final read's coverage miss, scoped re-read fix, and retest fix; a round-2
    read missing and one unreadable; a final read missing and one unreadable; `api_error`,
    `overloaded_error`, sync 500, and sync 529; `canceled` and `expired`; `max_tokens` and a schema
    failure. Each "once" or budgeted row tests both the retry that succeeds (the clean twin) and the
    second failure that takes the terminal action. Each asserts the outcome and the record's stop
    rule, seat, and finding numbers.
  - One test per stop reason (`transport`, `infrastructure` from `expired` twice, `infrastructure`
    from a gate vanish, `tree red outside drafter's pages`), each asserting `Summary`'s reason, no
    page escalated for it, and the resume line printed.
  - A red gate after applied edits spends the same budget as a refused answer; the failure after the
    budget is spent escalates with `contract`.
  - A refused answer whose problem the answer didn't cause lands in `faults`; a read that returned
    nothing lands in `faults` and never counts as accept.
  - A declined blocking finding and its reason reach that seat's next read.
  - Two pages, where page B's broken link reaches page A's gate: A holds and spends no fix turn.
  - Stage 1: a run of pages A and B where A's plan links B passes; A alone escalates `plan`; a link
    to a page the context's outline lists but no run page writes warns and doesn't escalate.
  - A round-2 request inlines a real two-sided diff from the stored baseline.
  - A seat left out of `seats`: its stages and stop rows are gone, and the record names it.
  - A markdown plan: stage 1 skipped with a warning, `plan_format: markdown`.
  - `pages_in_flight` 1: page B's first `Create` follows page A's end. `pages_in_flight` 3: all three
    stage-2 creates precede the first `Get`.
  - Without a facts store, no consistency request is sent and the record notes `facts: none`.
  - Escalation restore: a page that existed before the run escalates, and its page and brief equal
    their pre-run bytes, while the record holds `final.page.md` and `final.brief.json` with matching
    hashes; a page drafter created escalates, and both files are gone; an index file the link
    command changed is restored.
  - A synthetic run reaches `accepted` in batch mode and in sync mode; the batch-mode run's
    `record.json` matches a golden that names every field "Records" lists, with `cost` equal to the
    ledger's total for that page.
  - After a run that drives a 400, a 500, a reset, and a spend limit, a byte search of the run
    directory, the ledger, and captured stdout and stderr finds no key sentinel.
- Test: the drafter gate.
- Pair: with P5.5. P5.1 goes to a subagent with `isolation: "worktree"`; P5.5 to a subagent without
  isolation, working the cairn worktree by path as its only writer.

### P5.2 Run inputs and resume (130 min, auth-data)

- Outcome, in `internal/pipeline` and `internal/run`, following the spec's "Run inputs", "One run
  per worktree", and "Resume":
  - At start: `run.Prune`; the worktree lock and the run-directory lock; a refusal of a worktree
    with any `git status --porcelain` line, untracked files included; every page listed as
    `pending`; the branch and HEAD in state; the prompts module, each seat's agent definition, and
    the resolved configuration (its sources; no `key_command` value and no key) copied into the run
    directory with their hashes, and every stage built from the copies; `key.Resolve` and
    `CheckWorkspace` before any request.
  - Intents before each batch `create` and each sync request, with `custom_id`s in the Interfaces
    form; the batch ID after `create`; the saved response and message ID when a stream ends; the
    saved answer and both hashes around each page or brief write through `atomicfile.WriteFile`.
  - `--resume`: reads the caps, the key, and `workspace_id` fresh and runs `CheckWorkspace` again;
    refuses another state schema; requires the same branch, a HEAD equal to or descended from the
    recorded one, and no change but drafter's own files at their recorded hashes (an escalating
    page's pre-run snapshot hash, or its absence, included); runs `Verify` on every handoff; voids
    this run's open reservations that no state intent names (a stop between `Reserve` and the intent
    write); adopts an in-flight batch through `List`, `Get` until each candidate ends, and `Results`
    matched on its `custom_id`s; settles any ended batch not yet ledgered; settles a batch whose
    results have expired (29 days after creation, per the batch guide) at its reservation share as
    `estimated`; settles a sync intent with no saved response at its share as `estimated` and sends
    it again as a new reserved attempt; continues from post-write hashes, redoes the write from the
    saved answer at pre-write hashes, and stops naming any other changed file.
- Files: `internal/pipeline/`, `internal/run/`, their tests.
- Acceptance, the spec's resume rows against the fake API, each with its twin:
  - A stop after `create` with no recorded ID: no second `create`, with the fake's `List` also
    returning a decoy created after the intent with other `custom_id`s and one created before it;
    twin: no batch carries the intent's `custom_id`s, so it resubmits once.
  - A stop after a batch ended but before ledgering, resumed twice: one settle line per `custom_id`.
  - A stop for `cycle cap` with another page's batch in flight: the run exits resumable, and the
    resume settles that batch once.
  - A stop between the pre-write record and the write: the write is redone from the saved answer
    with zero fake calls and no new ledger line; twin: files at the post-write hashes continue with
    no rewrite.
  - A crash between restoring an escalating page and restoring its brief resumes and finishes the
    restore.
  - A resume whose page file changed by hand stops and names it.
  - A resume with earlier page spend: the cap counts it. A `page_cap` tightened between the stop and
    the resume escalates `cap` where the first run would not.
  - A sync intent with no saved response: one `estimated` line, then a new reserved attempt; two
    crash-and-resume cycles leave one `estimated` line for that attempt.
  - An open reservation with no state intent is voided on resume.
  - A batch whose results have expired settles `estimated`.
  - A plan edited between a stop and a resume is refused by the checksum.
  - The run directory's copies win: a mid-run edit to the prompts module that changes no prompt
    passes (the clean twin); an edit that changes the `editor` seat's text leaves the resumed
    `editor` request byte for byte the original and the run directory's module hash unchanged; the
    same for an agent-definition edit.
  - Refusals: a resume on another branch; a HEAD reset to the recorded commit's parent; a state of
    another schema; a dirty worktree at start, and one with only an untracked file; a busy worktree
    lock naming its holder.
  - Workspace: the fake's `CheckWorkspace` fails, and `pipeline.Run` returns the mismatch error
    naming both IDs with zero `CountTokens`, `Create`, and `Send` calls; the same on `--resume`
    after `workspace_id` changed in the user config between the stop and the resume.
  - Every `custom_id` built for the longest fixture page path matches `^[a-zA-Z0-9_-]{1,64}$`.
  - The copied configuration holds no `key_command` value and no key sentinel.
- Test: the drafter gate.
- Pair: with P5.6.

### P5.3 `drafter page` (70 min, ordinary)

- Outcome: `drafter page [--workflow-run <wf-file>] [--resume <run-id>] [--dry-run] [--sync]
  [--json] [<handoff-file>...]`. It loads the configuration at the handoffs' project root, runs
  `Validate(ScopeRun)`, and calls `pipeline.Run`. `--dry-run` assembles the first stage's requests
  (the consistency read when the project has a facts store, else the draft), counts their tokens,
  prints each request's size and the stage's estimated cost (`ledger.Worst`), and submits nothing,
  writing no ledger line and no run directory. Exit 0 when every page ended accepted, 1 when any
  escalated, 2 when the run couldn't start (usage, a refusal, a dirty tree, a busy lock), and 3 when
  it stopped resumable, printing the `--resume` line; 3 outranks 1.
- Files: `cmd/drafter/page.go`, `cmd/drafter/root.go`, `e2e/e2e_test.go`, `e2e/testdata/`.
- Acceptance, the spec's end-to-end paragraph: e2e tests build the binary and run `check-plan`,
  `check-prompts`, and `page --dry-run` on fixtures. The dry run reaches an `httptest` server
  through `api_base_url` that returns a fixed `input_tokens` and the expected workspace header, and
  the printed estimate for the named first stage equals a figure computed by hand in the test; the
  server sees no `create`; the ledger and the runs directory are unchanged. `--workflow-run` on a
  synthetic run file prints the same estimate as the equivalent handoff file. On a `git init` temp
  copy of `e2e/testdata/project` with one commit, a clean dry run exits 0, a touched tracked file
  exits 2 naming it, and an untracked file exits 2. A unit table maps `Summary` to the exit code,
  including stopped-with-an-escalated-page (3). With the key a sentinel, the dry run's stdout and
  stderr hold none of it.
- Test: the drafter gate.
- Pair: with P5.4.

### P5.4 drafter's own docs (65 min, ordinary)

- Outcome: the spec's "drafter's own docs", in the Google developer documentation style, assuming
  nothing about any workstation: the README (what drafter is, install, each command), and
  `docs/configuration.md` (the three layers, precedence, the caps' lowest-wins rule, the refusals,
  and every setting with its layers, default, and environment variable), `docs/handoff.md` (the
  handoff file, the chain's Workflow run file, the checksum, which paths must stay inside the
  project), `docs/prompts-module.md` (the loader, the seat names, the context object, what the
  runtime lacks), and `docs/setup.md` (the key source, the Console workspace and its own key, the
  spend-limit trade between a calendar month and the billing cycle, confirming the organization has
  no payment method or auto-reload when the credit should be the hard stop, and finishing or
  resuming every run before upgrading drafter, since a new state schema refuses an old run).
  `docs/plan-format.md` exists; the README links it.
- Files: `README.md`, `docs/configuration.md`, `docs/handoff.md`, `docs/prompts-module.md`,
  `docs/setup.md`, `internal/config/docs_test.go`.
- Acceptance: a Go test fails when a setting `config` decodes is missing from
  `docs/configuration.md`, walking nested keys in their dotted forms (`retries.*`, `gate.*`,
  `seat.<name>.*`, `prices.*`) and asserting the walked count is at least the spec's settings table
  rows; `tellgrader --register docs --profile docs-register` exits 0 on `README.md` and each
  `docs/*.md` page (without `--profile` it resolves from the scanned repo's `.tellgrader.json`, which
  drafter lacks, and nothing gates); a grep finds each of `setup.md`'s topics; a grep of `docs/` and
  `README.md` for `/var/home`, `glw907/workstation`, and `~/.local/secrets` finds nothing.
- Test: the drafter gate.
- Pair: with P5.3.

### P5.5 cairn's `drafter.toml` and YAML plans on the review page (50 min, ordinary)

- Outcome, in the cairn worktree, per cairn-pass:
  - `drafter.toml`: `gate.command` `npm run check:docs-gate -- --page {page} --brief {brief}`,
    `gate.protocol` `cairn-run-gate`, `gate.lane` `light`, the section and failure patterns pass 4's
    PR recorded for cairn's `== component ==` logs, `facts.dir` `docs/internal/facts`; every seat on
    `claude-opus-5-5`, the `draft` seat at `high` effort with `max_tokens` 64000, `structure`,
    `editor`, `fact`, and `reader` at `medium` with 32000, and `coverage` and `consistency` at `low`
    with 32000; the `editor` seat's inputs `vale {page}`; the `fact` seat's inputs the page's pending
    option-map rows (`grep -n 'pending {slug}' docs/internal/option-map.json`), a deliberate
    reduction of the chain's rule, which also selects rows whose value is one of the page's fact
    IDs: a command template can't name fact IDs, and on 2026-10-13 the map held no `pending ` row,
    so an empty output with exit 1 is the expected case; and the narrowed diff `git cat-file blob
    {baseline} | diff -u --label round-1 --label round-2 - {page}` on `structure`, `editor`, and
    `fact`. No `register.<track>`, which nothing reads. No path outside the repo, no money, no
    credentials, and no prompts module, agent definition, or index-link command, which live in the
    local layer until cutover.
  - `.gitignore` gains `drafter.local.toml`.
  - `scripts/docs-review/embed.mjs`: `planPathFor` resolves `<slug>.plan.yaml` first and falls back
    to `<slug>.plan.md`; a YAML plan reaches the review page as a fenced `yaml` code block, so the
    page's existing renderer shows it readably.
  - `ROADMAP.md`: the entry "The docs review page can't show a YAML page plan" is closed.
    `docs/STATUS.md`: the drafting run's next action gains the setup step for drafter (copy Geoff's
    `drafter.local.toml` into the drafting worktree; see P5.7). At close the STATUS edit is rebased
    onto `origin/main`, since cairn's drafting sessions also edit it.
- Files: `drafter.toml`, `.gitignore`, `scripts/docs-review/embed.mjs`,
  `src/tests/unit/docs-review-embed.test.ts`, `ROADMAP.md`, `docs/STATUS.md`.
- Acceptance: `drafter config` run in the cairn worktree with this branch's binary, a temp
  `drafter.local.toml` (ignored, never committed) setting `prompts` to an existing temp file, and a
  temp user config holding `workspace_id`, both caps, and a `claude-opus-5-5` price, exits 0 and
  prints every committed value with source `drafter.toml`; `git check-ignore -q drafter.local.toml`
  exits 0. The embed test gains a page with only `.plan.yaml` (shown as a `yaml` block), one with
  both (the YAML wins), and one with only `.plan.md` (unchanged). The fast lane passes and CI on the
  draft PR is green.
- Test: cairn's fast lane, then the CI watch.
- Pair: with P5.1.

### P5.6 Smoke on production shapes (30 min, ordinary)

- Outcome: `internal/smoke`'s shape table builds each request through `assemble.Build` with each
  seat's production answer schema, effort, and system prompt, on Haiku 5.5 with `max_tokens` 4096,
  over a synthetic context; pass 2's synthetic shapes go.
- Files: `internal/smoke/` and its tests.
- Acceptance: the offline smoke test in the gate passes against the fake with the production shapes,
  the table holds exactly the seven seats, and `go vet -tags smoke ./...` passes.
- Test: the drafter gate.
- Pair: with P5.2.

### P5.7 Geoff's setup, the user configuration, and the live smoke (40 min, ordinary; live)

- Outcome: drafter is configured to spend on Geoff's key, and the smoke has passed live on the
  production shapes. Check, by name only, printing no value:
  1. `grep -c '^export DRAFTER_API_KEY=' ~/.local/secrets` prints 1;
  2. the Console workspace ID is known (Geoff gives it to the session; it is an identifier, not a
     secret).
  When either is missing, remove the clock file, run `notify-send -u normal` naming what is missing
  and pointing at the design's "Your setup step", print the same as the session's message, and
  wait. For the key, a `run_in_background` Bash until-loop re-runs check 1 every few minutes and
  re-invokes the session when it passes; the workspace ID comes only in Geoff's own message. drafter
  carries no STATUS file, so that message and the notification are the record; the conductor relays
  them.
  When both hold:
  - Write `~/.config/drafter/config.toml`: `workspace_id` as given, `page_cap` 10, `cycle_ceiling`
    160, `key_env` `DRAFTER_API_KEY`, `billing_cycle_day` 1 (ruling 6), and `prices`
    (`batch_discount` 0.5, and `claude-opus-5-5` and Haiku 5.5 with both its tiers) from the
    published pricing page, read that day, with its URL and date. Cross-check each figure against
    the page as read on 2026-10-13: Opus 5.5 $4 input, $20 output, $5 and $8 cache writes, $0.20
    cache read per million tokens; Haiku 5.5 $0.10, $0.50, $0.125, $0.20, $0.01 up to 100,000 prompt
    tokens and $0.50, $2.50, $0.625, $1, $0.05 over; the batch discount 50% on input and output. A
    difference is recorded in the PR, never silently taken.
  - Write `~/.config/drafter/cairn-cms.local.toml`, the source copy of cairn's
    `drafter.local.toml`: `prompts` `~/.claude/workflows/docs-page-chain.js`, the `draft` seat's
    `agent` `~/.claude/agents/cairn-docs-drafter.md`, the `editor` seat's
    `~/.claude/agents/cairn-register-editor.md`, `inline_files` `["~/.local/share/cairn/exemplars"]`,
    and `gate.index_link_command` running `cairn-docs-outline link --worktree "$PWD" --outline
    docs/internal/outlines/${arm}.json --page {page}`, with `arm` taken from the page path in the
    shell, so one command serves both of cairn's outlines.
  - When either file already exists, keep every value it sets, add only the missing keys, report
    each conflict by key name without its value, and write through `atomicfile`. Neither file is
    committed anywhere.
  - Read the meter, then run `bash -c '. ~/.local/secrets && DRAFTER_CYCLE_CEILING=15 make smoke'`
    from the drafter worktree as a `run_in_background` Bash task, and record the result, the
    requests, and the ledger lines' total.
- Acceptance: `drafter config` (this branch's binary) run outside any project resolves the user
  layer and passes `Validate(ScopeMoney)` with no refusal; the production-shape smoke passed in this
  pass; the meter after the smoke is under $5.
- Test: the smoke run.

### P5.8 One real cairn page (120 min, live)

- Outcome: the design's end-to-end check, held to Geoff's ruling 8.
  - First check, the same way P5.7 checks and waits: passes 1 to 4 on drafter's `origin/main`; pass
    3's dotfiles PR merged and live (`grep -c DRAFTER_HOST ~/.claude/workflows/docs-page-chain.js`
    is nonzero); and every exemplar `source` in the extend outline's entry for the chosen page
    resolves under `~/.local/share/cairn/exemplars/`, since the chain's outline probe fails the run
    on a missing capture.
  - Create a scratch cairn worktree on a scratch branch from `drafter-pipeline`, run cairn-pass's
    setup command, and copy `~/.config/drafter/cairn-cms.local.toml` in as `drafter.local.toml`.
    `drafter config` there (this branch's binary) resolves with no refusal and passes
    `Validate(ScopeRun)`.
  - Choose one stage 2b part 2 extend page whose outline entry has `figure: false`, preferring a
    task guide (`restrict-admin-access`, `add-a-second-sign-in-group`, and `rotate-the-github-app-key`
    qualified on 2026-10-13), from the plans `docs/STATUS.md` names. Run the index-link command once
    on a page already linked, from the scratch worktree, and check it exits 0 with no change: a
    quoting bug surfaces here before any spend.
  - Take the chain's arguments from the last chain run's plan,
    `docs/superpowers/plans/2026-10-11-draft-docs-2b-part1.md` in cairn (gate, lane, outline, Vale
    rules), with the page's own entry, `backHalf: "drafter"`, and `worktree` set to the scratch
    worktree, and run the `docs-page-chain` Workflow on that one page.
  - Commit every path `git status --porcelain` lists on the scratch branch (the plan, the framing
    record, the option map and facts files the front half wrote), and confirm the status is empty.
  - Find the run's Workflow run file under `~/.claude/projects/` by its `args.worktree`: none stops
    and notifies; several takes the newest by mtime, recorded in the PR. No such file existed on this
    machine at planning time, so confirm its `.result.handoff` shape against pass 3's; where it
    differs, fix forward the synthetic fixture and the decoder, with no cairn text in drafter.
  - Run `drafter page --dry-run --workflow-run <wf-file>` for the first stage's estimate. Read the
    meter and set the page cap as "Standing approvals" says. Then run, from the scratch worktree, as
    a `run_in_background` Bash task, `bash -c '. ~/.local/secrets && DRAFTER_CYCLE_CEILING=15
    DRAFTER_PAGE_CAP=<cap> <drafter worktree>/drafter page --workflow-run <wf-file>'` in batch mode.
    On exit 3, follow the stop reason: `cycle cap` or `spend limit` notifies and stops for Geoff;
    `transport` or `infrastructure` resumes once with the printed `--resume` line.
  - The bar (ruling 8): the page ends `accepted`, or escalated with an empty `faults` list and a
    record that shows the round-1 reads ran. When it misses the bar, classify each fault: a
    drafter-caused one (a refusal the answer didn't cause, a parse failure of a schema-valid answer)
    is fixed forward in the drafter worktree with a test; a model-caused one, and an escalation
    before the round-1 reads, are recorded with their cause. Then one rerun, when the budget allows
    (the page cap rule above): the same page after a drafter fix, another qualifying page after an
    input cause. Before a rerun or the worktree's removal, the earlier run's state shows no open
    intent; a stopped run is resumed to settle first. A second miss, or no budget, ends the pass
    with the PR saying "not pilot-ready" and why.
  - Record in the drafter PR body: the page, its final status, the stop rule if any, `faults` with
    each one's class, the stages reached, and `drafter spend --since <first live date> --until <last
    live date>` by seat, covering every live drafter-workspace spend of the initiative (the smoke
    included), with those UTC dates, so Geoff compares the Console's cost for drafter's workspace
    over the same window at his PR read (ruling 8; the session holds no admin key to read the
    Console's cost itself).
  - Remove the scratch worktree and its branch. The page is thrown away; cairn's drafting run
    redoes it.
- Acceptance: the bar above, with the record excerpts in the PR body.
- Test: the live run.

### Close (50 min)

The drafter gate once on its close head; cairn's CI green on its head. Two whole-branch
`diff-reviewer` runs: drafter's branch against `main` (go-conventions for `*.go`; it re-derives each
task's class and confirms P5.1's and P5.2's task-scope verdicts are recorded), and cairn's against
`origin/main` per cairn-pass's checklist globs. One batched fix chain, the gates again. `gitleaks
git` over drafter's branch history, and a grep of drafter's `testdata/` and `docs/` for workstation
paths and for anything shaped like an `sk-ant-` key that finds nothing. Rebase cairn's STATUS edit
onto `origin/main` if it moved.

Push and open the PRs, `glw907/drafter` and `glw907/cairn-cms` (draft until CI is green, then ready),
each body naming the other. Each opens with `## Brief`. The drafter PR carries what landed, the
review verdicts, P5.8's record, the smoke result, the score rows (gate time from
`~/.local/state/cairn-run-gate/runs.jsonl` records whose `gate` names this worktree; the Work and
review row puts the 610-minute path beside the actual, the wait for Geoff's setup listed as an
attended event), and the pilot-ready statement: pilot-ready conditional on Geoff's Console
comparison within 5%, the one open acceptance item, or "not pilot-ready" with the reason. Its "Found,
not done" carries a proposed disposition each, including: the user configuration living outside the
dotfiles repo (proposed: defer, stow it with sub-project 3's rollout), and `secrets/registry.md`'s
entry for `DRAFTER_API_KEY` (proposed: defer to sub-project 3). It notes for the merger: after the
merge, `make -C ~/Projects/drafter install`. The cairn PR carries what landed and its CI line. Stop at
PR-ready; the conductor takes both to Geoff.

## Later

- Prompt caching, if the pilot's ledger shows more than one continuation per page on average.
- A per-arm `index_link_command` setting, if the shell expression in Geoff's local file proves
  fragile.
- A settle-only resume across state schemas, if an upgrade ever lands between a stop and its resume.
