# drafter pass 5 plan: the pipeline

Design: `docs/superpowers/specs/2026-10-13-drafter-completion-design.md`, pass 5, "The end-to-end
check", and "Your setup step", approved by Geoff on 2026-10-13. Spec:
`docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, sections "The pipeline" (stages, stop
rules, the final reader's two turns, projects without facts, shared worktree), "Records", "Run
inputs", "One run per worktree", "Resume", "Concurrency", "Failures", "Models", "The tool" (the
`pipeline` row and `drafter page`), "drafter's own docs", "A server-side backstop" (for the setup
guide), and "Testing" (the pipeline state machine row, the facts-free stage-1 row, the end-to-end
paragraph, and the edit-contract rows pass 4 left to the pipeline).

## Outcome

`drafter page` takes each planned page through every stage, in batch or sync mode, ends it accepted
or escalated with a full record, stops and resumes without paying twice, and never spends past a
cap. drafter carries its own docs. cairn gets a committed `drafter.toml`, and its docs review page
shows YAML plans. One real cairn page goes through the chain's front half and drafter's back half,
on Geoff's API key, and the pass reports drafter pilot-ready.

## Shape

- Risk class: `runner` (the cairn docs-review script, by Geoff's ruling in the design). The drafter
  tasks are `ordinary`.
- `live-account` flag: yes. P5.7 and P5.8 spend real API credit, inside the initiative's $15
  standing approval.
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
- Path estimate: 465 minutes. P5.1 and P5.5 as a pair (150), P5.2 and P5.4 as a pair (90), P5.3 and
  P5.6 as a pair (60), P5.7 (30, not counting the wait), P5.8 (90), Close (45). The design's
  estimate is 240, so the path is 1.9 times it, inside the 3x line (720).
- Standing approvals (design, "Technical notes"):
  - The plan proceeds within 3x.
  - Live spend up to $15 across the initiative runs without asking. Before each live run the session
    reads the meter, `drafter spend --since 2026-10-13 --json`, and stops and notifies when the total
    plus the run's worst case (the smoke, $1; a page, its $10 page cap) would pass $15. Every live
    run also carries `DRAFTER_CYCLE_CEILING=15` in its environment, so the ledger refuses the excess
    itself.
  - The live steps wait for Geoff's setup. Every offline task runs first.
  - Both PRs go to Geoff through the conductor; the executor never merges.
- Depends on: pass 3's dotfiles PR merged and live (the chain's `backHalf`), and cairn's exemplar
  captures on disk, for P5.8 only. P5.8 checks both.
- The approved design's end-to-end check names the chain run with `backHalf: "drafter"`, so it is
  Geoff's opt-in for that one Workflow run; the session runs no other.

## Interfaces

Consumes: from pass 1, `config.Load`, `(*config.Config).Validate`, `(*config.Config).Sources`,
`atomicfile.WriteFile`, every `run` export; from pass 2, `key.Resolve`, `*batch.Client` and its
method set, `batch.Request`, `batch.Result`, `batch.Classify`, `batch.ErrSpendLimit`,
`batch.ErrTransport`, every `ledger` export; from pass 3, `prompts.Load`, `prompts.Context`,
`(*prompts.Module).Render`, `handoff.ReadFiles`, `handoff.ReadWorkflowRun`, `(handoff.Handoff).Verify`;
from pass 4, every `edits`, `coverage`, `gate`, and `assemble` export; from Pass 0 and F1,
`plan.CheckFile`, `plan.LoadFacts`.

Creates:

- `pipeline.API`: the consumer-side interface over `*batch.Client`'s methods (`Workspace`,
  `CheckWorkspace`, `CountTokens`, `Create`, `Get`, `Results`, `List`, `Send`), declared here as
  go-conventions asks, since the fake is its second implementation.
- `pipeline.Options` (the configuration, the handoffs, the API, the resume run ID, dry run, and a
  clock) and `pipeline.Run(ctx, Options) (Summary, error)`. `Summary` holds each page's final status
  and the run's stop reason.
- `run.State` and `run.PageState` gain the intents, batch IDs, saved answers, and write hashes resume
  needs, with `run.StateSchema` bumped.

## Out of scope

The pilot itself, cutover, sub-projects 2 to 5, figure and rework pages, the agentic fact read, a
`claude -p` reader, prompt caching, and every cairn change beyond `drafter.toml`, `.gitignore`, the
review page's YAML plans, and the ledgers.

## Tasks

Every drafter task starts by invoking `go-conventions`. The offline tasks (P5.1 to P5.6) all run
before P5.7.

### P5.1 The pipeline's stages and stop rules (150 min, ordinary)

- Outcome: `internal/pipeline` runs each page through the spec's seven stages, with these rules:
  - Stage 1 runs `plan.CheckFile` with `facts.dir`, counting every page in the run as
    outline-listed (the run's pages are being drafted together, and check-plan's outline exemption
    exists for exactly that). With a facts store, one batched consistency read follows, built by
    `assemble.ConsistencyPrompt`. A markdown plan skips stage 1 and every plan-dependent check, with
    a warning, and the record notes `plan_format: markdown`.
  - Each stage reserves its worst case through `ledger.Worst` and `ledger.Reserve`, after
    `CountTokens` on each request, before it submits; it settles every result.
  - The seat contexts follow pass 3's context object; findings reach a redraft as
    `edits.Render`'s text; declined blocking findings reach that seat's next read through
    `assemble.Input.Declined`.
  - A seat left out of `seats` removes its stages and its stop-table rows, and the record names it.
  - Without a facts store, stage 1 sends no consistency read, coverage skips `fact` items, and the
    record notes `facts: none`.
  - Every row of the stop table and of the failures table, with `retries.gate_fix` and
    `retries.edit_contract` (shared between refusals and red gates after applied edits) as budgets.
  - Shared worktree: a page whose gate is red with nothing of its own holds and is gated again after
    the other pages settle; a foreign red that persists after every other page has settled stops the
    run with `tree red outside drafter's pages`. An escalating page's page and brief go back to
    their pre-run snapshots, or are removed when drafter created them, and the draft stays in the
    record as `final.page.md` and `final.brief.json`.
  - Records: each page's directory holds its requests, responses, edit-contract answers, gate
    excerpts, snapshots, finals with their hashes, and `record.json` with every field the spec's
    "Records" lists. `faults` is computed on every page.
  - Concurrency: up to `pages_in_flight` pages; in batch mode one sequential poll loop over every
    in-flight batch, in sync mode one streamed request at a time; gates one at a time; no goroutines.
- Files: `internal/pipeline/` with tests and `testdata/` (a synthetic project, handoffs, a
  chain-shaped prompts module, and scripted fake API answers).
- Acceptance, the spec's pipeline state machine row and the rows pass 4 left here, against a fake
  `pipeline.API` whose every fallible method carries an error field:
  - One test per stop-table row and per failures-table row, each asserting the outcome and the
    record's stop rule, seat, and finding numbers.
  - A red gate after applied edits spends the same budget as a refused answer; the failure after the
    budget is spent escalates with `contract`.
  - A refused answer whose problem the answer didn't cause lands in `faults`; a read that returned
    nothing lands in `faults` and never counts as accept.
  - A declined blocking finding and its reason reach that seat's next read.
  - Two pages, where page B's broken link reaches page A's gate: A holds and spends no fix turn.
  - A stage whose reservation would cross the page cap escalates with `cap`; one that would cross
    the ceiling stops the run as `cycle cap`; `ErrSpendLimit` stops it as `spend limit`.
  - Without a facts store, no consistency request is sent and the record notes `facts: none`.
  - A synthetic run reaches `accepted` in batch mode and in sync mode.
- Test: the drafter gate.
- Pair: with P5.5. P5.1 goes to a subagent with `isolation: "worktree"`; P5.5 to a subagent without
  isolation, working the cairn worktree by path as its only writer.

### P5.2 Run inputs and resume (90 min, ordinary)

- Outcome, in `internal/pipeline` and `internal/run`, following the spec's "Run inputs", "One run
  per worktree", and "Resume":
  - At start: `run.Prune`; the worktree lock and the run-directory lock; a refusal of a worktree
    with uncommitted changes; the branch and HEAD in state; the prompts module, each seat's agent
    definition, and the resolved configuration (its sources, no credentials) copied into the run
    directory with their hashes, and every stage built from the copies; `key.Resolve` and
    `CheckWorkspace` before any request.
  - Intents before each batch `create` and each sync request; the batch ID after `create`; the saved
    response and message ID when a stream ends; the saved answer and both hashes around each page or
    brief write through `atomicfile.WriteFile`.
  - `--resume`: reads the caps, the key, and `workspace_id` fresh; refuses another state schema;
    requires the same branch, a HEAD equal to or descended from the recorded one, and no change but
    drafter's own files at their recorded hashes; runs `Verify` on every handoff; adopts an
    in-flight batch through `List` and its `custom_id`s; settles any ended batch not yet ledgered;
    settles a sync intent with no saved response at its reservation as `estimated` and sends it once
    more; continues from post-write hashes, redoes the write from the saved answer at pre-write
    hashes, and stops naming any other changed file.
- Files: `internal/pipeline/`, `internal/run/`, their tests.
- Acceptance, the spec's resume rows against the fake API: a stop after `create` with no recorded
  ID (no second `create`); a stop after a batch ended but before ledgering (one settle line per
  `custom_id`); a stop between the pre-write record and the write; a resume whose page file changed
  by hand (stops and names it); a resume with earlier page spend (the cap counts it); a sync intent
  with no saved response (settled as `estimated`, then sent once more); a plan edited between a stop
  and a resume (refused by the checksum); a mid-run edit to the prompts module that changes no
  prompt of the run; a dirty worktree refused at start; a busy worktree lock naming its holder.
- Test: the drafter gate.
- Pair: with P5.4.

### P5.3 `drafter page` (60 min, ordinary)

- Outcome: `drafter page [--workflow-run <wf-file>] [--resume <run-id>] [--dry-run] [--sync]
  [--json] [<handoff-file>...]`. It loads the configuration at the handoffs' project root, runs
  `Validate`, and calls `pipeline.Run`. `--dry-run` assembles the first stage's requests, counts
  their tokens, prints each request's size and the stage's estimated cost (`ledger.Worst`), and
  submits nothing. Exit 0 when every page ended accepted, 1 when any escalated, 2 when the run
  couldn't start (usage, a refusal, a dirty tree, a busy lock), and 3 when it stopped resumable,
  printing the `--resume` line.
- Files: `cmd/drafter/page.go`, `cmd/drafter/root.go`, `e2e/e2e_test.go`, `e2e/testdata/`.
- Acceptance, the spec's end-to-end paragraph: e2e tests build the binary and run `check-plan`,
  `check-prompts`, and `page --dry-run` on fixtures. The dry run reaches an `httptest` server
  through `api_base_url` that returns a fixed `input_tokens` and the expected workspace header, and
  the printed estimate equals a figure computed by hand in the test; the server sees no `create`.
  `--workflow-run` on a synthetic run file prints the same estimate as the equivalent handoff file.
  A worktree with an uncommitted change exits 2.
- Test: the drafter gate.
- Pair: with P5.6.

### P5.4 drafter's own docs (60 min, ordinary)

- Outcome: the spec's "drafter's own docs", in the Google developer documentation style, assuming
  nothing about any workstation: the README (what drafter is, install, each command), and
  `docs/configuration.md` (the three layers, precedence, the caps' lowest-wins rule, the refusals,
  and every setting with its layers, default, and environment variable), `docs/handoff.md` (the
  handoff file, the chain's Workflow run file, the checksum), `docs/prompts-module.md` (the loader,
  the seat names, the context object, what the runtime lacks), and `docs/setup.md` (the key source,
  the Console workspace and its own key, the spend-limit trade between a calendar month and the
  billing cycle, and confirming the organization has no payment method or auto-reload when the
  credit should be the hard stop). `docs/plan-format.md` exists; the README links it.
- Files: `README.md`, `docs/configuration.md`, `docs/handoff.md`, `docs/prompts-module.md`,
  `docs/setup.md`, `internal/config/docs_test.go`.
- Acceptance: a Go test fails when a setting `config` decodes is missing from
  `docs/configuration.md`; `tellgrader --register docs` reports no gating finding on each page;
  a grep of `docs/` and `README.md` for `/var/home`, `glw907/workstation`, and `~/.local/secrets`
  finds nothing.
- Test: the drafter gate.
- Pair: with P5.2.

### P5.5 cairn's `drafter.toml` and YAML plans on the review page (45 min, runner)

- Outcome, in the cairn worktree, per cairn-pass:
  - `drafter.toml`: `gate.command` `npm run check:docs-gate -- --page {page} --brief {brief}`,
    `gate.protocol` `cairn-run-gate`, `gate.lane` `light`, the section and failure patterns pass 4's
    PR recorded for cairn's `== component ==` logs, `facts.dir` `docs/internal/facts`; every seat on
    `claude-opus-5-5`, the `draft` seat at `high` effort with `max_tokens` 64000, `structure`,
    `editor`, `fact`, and `reader` at `medium` with 32000, and `coverage` and `consistency` at `low`
    with 32000; the `editor` seat's inputs `vale {page}`; the `fact` seat's inputs the page's pending
    option-map rows (`grep -n 'pending {slug}' docs/internal/option-map.json`); the narrowed diff
    `git cat-file blob {baseline} | diff -u --label round-1 --label round-2 - {page}` on
    `structure`, `editor`, and `fact`; and `register.<track>` for each of the chain's six tracks,
    copied from `registerSectionsFor(track, "drafter")`. No path outside the repo, no money, no
    credentials, and no prompts module or agent definition, which live outside cairn until cutover.
  - `.gitignore` gains `drafter.local.toml`.
  - `scripts/docs-review/embed.mjs`: `planPathFor` resolves `<slug>.plan.yaml` first and falls back
    to `<slug>.plan.md`; a YAML plan reaches the review page as a fenced `yaml` code block, so the
    page's existing renderer shows it readably.
  - `ROADMAP.md`: the entry "The docs review page can't show a YAML page plan" is closed.
    `docs/STATUS.md`: the drafting run's next action gains the setup step for drafter (copy Geoff's
    `drafter.local.toml` into the drafting worktree; see P5.7).
- Files: `drafter.toml`, `.gitignore`, `scripts/docs-review/embed.mjs`,
  `src/tests/unit/docs-review-embed.test.ts`, `ROADMAP.md`, `docs/STATUS.md`.
- Acceptance: `drafter config` run in the cairn worktree with this branch's binary and a temp user
  config prints every committed value with source `drafter.toml` and no refusal; `drafter.local.toml`
  is ignored by git. The embed test gains a page with only `.plan.yaml` (shown as a `yaml` block),
  one with both (the YAML wins), and one with only `.plan.md` (unchanged). The fast lane passes and
  CI on the draft PR is green.
- Test: cairn's fast lane, then the CI watch.
- Pair: with P5.1.

### P5.6 Smoke on production shapes (25 min, ordinary)

- Outcome: `make smoke`'s shape table builds each request through `assemble.Build` with each seat's
  production answer schema, effort, and system prompt, on Haiku 5.5 and a small `max_tokens`, over a
  synthetic context; pass 2's synthetic shapes go.
- Files: `internal/batch/smoke_test.go` or a new `internal/assemble/smoke_test.go` (build tag
  `smoke`), whichever avoids an import cycle; `Makefile` if the target's path changes.
- Acceptance: `go vet -tags smoke ./...` passes and the gate stays green without the tag.
- Test: the drafter gate.
- Pair: with P5.3.

### P5.7 Geoff's setup and the user configuration (30 min, ordinary; live)

- Outcome: drafter is configured to spend on Geoff's key. Check, by name only, printing no value:
  1. `grep -c '^export DRAFTER_API_KEY=' ~/.local/secrets` prints 1;
  2. the Console workspace ID is known (Geoff gives it to the session; it is an identifier, not a
     secret).
  When either is missing, remove the clock file, run `notify-send -u normal` naming what is missing
  and pointing at the design's "Your setup step", print the same as the session's message, and
  wait. drafter carries no STATUS file, so that message and the notification are the record; the
  conductor relays them.
  When both hold:
  - Write `~/.config/drafter/config.toml`: `workspace_id` as given, `page_cap` 10, `cycle_ceiling`
    160, `key_env` `DRAFTER_API_KEY`, and `prices` for `claude-opus-5-5` and Haiku 5.5 (both tiers)
    from the published pricing page, read that day, with its URL and date. `billing_cycle_day`
    stays at its default of 1 unless Geoff names his cycle day.
  - Write `~/.config/drafter/cairn-cms.local.toml`, the source copy of cairn's
    `drafter.local.toml`: `prompts` `~/.claude/workflows/docs-page-chain.js`, the `draft` seat's
    `agent` `~/.claude/agents/cairn-docs-drafter.md`, the `editor` seat's
    `~/.claude/agents/cairn-register-editor.md`, `inline_files` `["~/.local/share/cairn/exemplars"]`,
    and `index_link_command` running `cairn-docs-outline link --worktree "$PWD" --outline
    docs/internal/outlines/<arm>.json --page {page}`, with the arm taken from the page path in the
    shell, so one command serves both of cairn's outlines.
  - Neither file is committed anywhere.
  - Read the meter. When pass 2's PR recorded "smoke not yet run", run `bash -c '.
    ~/.local/secrets && DRAFTER_CYCLE_CEILING=15 make smoke'` from the drafter worktree and record
    the result.
- Acceptance: `drafter config` (this branch's binary) run outside any project resolves the user
  layer with no refusal; the smoke passed, here or in pass 2; the meter after the smoke is under
  $5.
- Test: the smoke run.

### P5.8 One real cairn page (90 min, runner; live)

- Outcome: the design's end-to-end check.
  - First check, the same way P5.7 checks and waits: pass 3's dotfiles PR is merged and live
    (`grep -c DRAFTER_HOST ~/.claude/workflows/docs-page-chain.js` is nonzero); and every exemplar
    `source` in the extend outline's entry for the chosen page resolves under
    `~/.local/share/cairn/exemplars/`, the root cairn's outline helper reads, since the chain's
    outline probe fails the run on a missing capture. On 2026-10-13 that directory did not exist on
    this machine.
  - Create a scratch cairn worktree on a scratch branch from `drafter-pipeline`, run cairn-pass's
    setup command, and copy `~/.config/drafter/cairn-cms.local.toml` in as `drafter.local.toml`.
    `drafter config` there (this branch's binary) resolves with no refusal and passes `Validate`.
  - Choose one stage 2b part 2 extend page whose outline entry has `figure: false`, preferring a
    task guide, from the plans `docs/STATUS.md` names. Take the chain's arguments from the last
    chain run's plan, `docs/superpowers/plans/2026-10-11-draft-docs-2b-part1.md` (gate, lane,
    outline, Vale rules), with the page's own entry, `backHalf: "drafter"`, and `worktree` set to
    the scratch worktree, and run the `docs-page-chain` Workflow on that one page.
  - Commit the plan and framing record on the scratch branch, so the tree is clean. Find the run's
    Workflow run file under `~/.claude/projects/` by its `args.worktree`.
  - Read the meter: the total plus $10 must stay at or under $15. Then run, from the scratch
    worktree, `bash -c '. ~/.local/secrets && DRAFTER_CYCLE_CEILING=15 <drafter worktree>/drafter
    page --workflow-run <wf-file>'` in batch mode.
  - The page must end `accepted`, or escalated with an empty `faults` list. A non-empty `faults`
    list is a drafter defect: fix it forward in the drafter worktree with a test, and rerun only when
    the meter allows; otherwise stop and notify.
  - Record in the drafter PR body: the page, its final status, the stop rule if any, `faults`, the
    stages, and `drafter spend --since 2026-10-13` by seat, plus the run's UTC dates, so Geoff can
    compare the Console's cost for drafter's workspace over those dates at his PR read (the 5%
    check; the session holds no admin key to read the Console's cost itself).
  - Remove the scratch worktree and its branch. The page is thrown away; cairn's drafting run
    redoes it.
- Acceptance: the outcome's status condition, with the record excerpts in the PR body.
- Test: the live run.

### Close (45 min)

The drafter gate once on its close head; cairn's CI green on its head. Two whole-branch
`diff-reviewer` runs: drafter's branch against `main` (go-conventions for `*.go`), and cairn's against
`origin/main` per cairn-pass's checklist globs. One batched fix chain, the gates again. `gitleaks
git` over drafter's branch history, and a grep of drafter's `testdata/` and `docs/` for workstation
paths that finds nothing.

Push and open the PRs, `glw907/drafter` and `glw907/cairn-cms` (draft until CI is green, then ready),
each body naming the other. Each opens with `## Brief`. The drafter PR carries what landed, the
review verdicts, P5.8's record, the smoke result, the score rows (the Work and review row puts the
465-minute path beside the actual, the wait for Geoff's setup listed as an attended event), the
pilot-ready statement, and "Found, not done" with a proposed disposition each, including: the
exemplar captures' state, the user configuration living outside the dotfiles repo (proposed: defer,
stow it with sub-project 3's rollout), `secrets/registry.md`'s entry for `DRAFTER_API_KEY`
(proposed: defer to sub-project 3), and confirming `billing_cycle_day`. It notes for the merger:
after the merge, `make -C ~/Projects/drafter install`. The cairn PR carries what landed and its CI
line. Stop at PR-ready; the conductor takes both to Geoff.

## Later

- Prompt caching, if the pilot's ledger shows more than one continuation per page on average.
- A per-arm `index_link_command` setting, if the shell expression in Geoff's local file proves
  fragile.
