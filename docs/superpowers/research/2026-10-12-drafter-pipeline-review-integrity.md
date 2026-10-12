# drafter pipeline spec: data integrity and failure risk review

Reviewed: `docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md` at commit 1e92788 (branch
`drafter-pipeline-spec`). Lens: crash, concurrent process, partial write, upgrade, restore, and
laptop suspend; loss or silent corruption of the page and brief, the facts store, the ledger, run
state, money, and a git tree another session works in.

Sources checked (cited inline as short names):

- **spec**: the spec above, by line.
- **spike**: `scratchpad/spike/batchchain.py` and the recorded `run-*/` directories.
- **gate**: `~/.local/bin/cairn-run-gate` header, lines 1-90.
- **docs-gate**: `~/Projects/cairn-cms/scripts/checks/docs-gate.mjs`, lines 1-80.
- **chain**: `~/.claude/workflows/docs-page-chain.js`.
- **guards**: `~/.claude/docs/unattended-work-guards.md`.
- **go-conv**: `~/.claude/skills/go-conventions/SKILL.md` "File Writes", lines 208-220.
- **secrets**: `~/.local/secrets` (names only), `~/.bashrc:192-194`, `~/.dotfiles/secrets/registry.md:133,330-336`.
- **batch-docs**: platform.claude.com/docs/en/build-with-claude/batch-processing (fetched 2026-10-12), lines 44-48, 610, 720-722.
- **limits-docs**: platform.claude.com/docs/en/api/rate-limits (fetched 2026-10-12), "Spend limits", "Setting your own spend limit", and "Response headers".

Findings are ranked by consequence. 18 findings: 1 blocker, 8 major, 9 minor.

---

## 1. drafter's key name collides with the workstation's general Anthropic key, so spend can land outside the backstop

- **Severity:** blocker. **Tag:** correctness.
- **Location:** spec:238-241.
- **Defect:** The spec has drafter read `ANTHROPIC_API_KEY` from the environment. That name is
  already taken. `~/.local/secrets` exports `ANTHROPIC_API_KEY`, and `~/.bashrc:194` sources that
  file into every interactive shell. registry.md:330-336 records it as the general key used by
  "Claude CLI, any scripts using the Anthropic SDK, ecxc worker and asc-site worker". Every
  foreground `drafter page` run from a terminal, and every run a Claude Code Bash tool starts,
  inherits that general key, not drafter's own key. The spend then goes to whatever workspace and
  organization that key belongs to. The $160 workspace limit never sees it, and the spend may not
  draw on the Max plan's credits at all. Storing the new key under the same name through
  `secret-set.sh` would overwrite the general key and break both workers' editor Tidy. Pilot
  criterion 4 (spec:307-308) would catch this only after the money is spent.
- **Proposed fold:** Give the key its own name, for example `DRAFTER_ANTHROPIC_API_KEY`. drafter
  reads only that name, passes it to the SDK client explicitly, and refuses to start when it's
  unset. It never falls back to `ANTHROPIC_API_KEY`, since the Go SDK's default client reads that
  name. drafter.toml also records the workspace ID. Every API response carries an
  `anthropic-workspace-id` header (limits-docs, "Response headers"). drafter checks that header on
  its first call of each run and stops on a mismatch, before it submits a batch. Add a test where
  `ANTHROPIC_API_KEY` is set and `DRAFTER_ANTHROPIC_API_KEY` isn't, and assert drafter refuses.

## 2. The caps can be bypassed: in-flight spend isn't reserved, the estimate omits output, and two processes race

- **Severity:** major. **Tag:** correctness.
- **Location:** spec:225-228, 232-234, 263-265, 289.
- **Defect:** The spec has four problems with how it counts spend against a cap.
  1. *In-flight spend is invisible.* The ledger gets a line only when a batch result arrives
     (spec:232). drafter submits every page's current stage at once (spec:263). Each pre-submit
     check compares one stage's estimate against a ledger that leaves out every other batch still
     in flight, so N pages' stages can each pass a cap that their sum exceeds.
  2. *The estimate counts input only.* The token-counting endpoint prices input (spec:226-227),
     but output costs several times the input rate. The spike's own formula uses a 5x ratio
     (spike:181-182). In the recorded runs, `draft1-0` used 106,589 input and 31,972 output tokens,
     so output was about 60% of its cost, and every redraft was 40-50%. A cap "that stops a stage
     before the spend" (spec:227-228) can be exceeded by about 2x on a stage.
  3. *Two processes race.* The spec takes no lock around estimate, check, submit, and append.
     Two concurrent drafters can both read the ledger under $160 and both submit: a foreground run
     and a resume, two repos, or later the nightly run from sub-project 2. Concurrent appends to
     `ledger.jsonl` also have no stated serialization.
  4. *A crash miscounts in both directions.* If drafter dies after results come back but before it
     appends to the ledger, and the run is never resumed, that spend never reaches the ledger. If it
     dies after the append but before the state write, a resume fetches the same results and
     appends them again. That double count breaks the 5% match in pilot criterion 4 (spec:307).
     The per-run $40 cap has the same gap. The spec doesn't say whether a resumed run's prior spend
     counts toward its $40.
- **Proposed fold:** Put the ledger behind one lock, `flock` on
  `~/.local/state/drafter/ledger.lock`, held across estimate, check, submit, and append. Write two
  kinds of line:
  - A **reserve** line at submission, written before `batches.create` returns: batch-intent ID,
    run, page, seat, and worst-case cost (counted input plus `max_tokens` at the output rate).
  - A **settle** line when results arrive, keyed by batch ID and `custom_id`. Settling twice is a
    no-op.

  Each cap counts settled lines plus open reserves. The per-page and per-run totals derive from the
  ledger by run ID, not from in-memory counters, so a resumed run's spend comes back with it. Add
  tests for N in-flight pages crossing the run cap, for two processes against one ledger, and for a
  resume that settles a batch twice.

## 3. A crash between `batches.create` and the state write orphans a paid batch, and resume pays for it again

- **Severity:** major. **Tag:** correctness.
- **Location:** spec:257-259.
- **Defect:** The spec writes "the ID of any batch in flight" to state, but that ID exists only
  after `create` returns. The spike shows the window. It writes the request file, calls `create`,
  and only then logs the ID (spike:169-172). If drafter is killed, its HTTP call is cut off by a
  suspend, or the machine dies inside that window, the batch runs and bills, but no state names it.
  `--resume` then sees a stage with no batch and submits it again. That's the "batch paid twice"
  case the spec's resume section says it prevents (spec:258-259). The same window exists for a
  gate-fix turn and for each contract retry, since each is its own batch (spike:239, 412).
- **Proposed fold:** Write an intent record first: run, stage, attempt, a timestamp, and
  `custom_id`s that are unique to run, page, stage, and attempt. Write it atomically, then call
  `create`, then record the ID. On resume, an intent with no ID calls the batch list endpoint
  (batch-docs:610; batches are workspace-scoped, batch-docs:46) for batches created after the
  intent's timestamp. drafter's dedicated workspace keeps that list unambiguous. It waits for each
  candidate to end, then matches it by the `custom_id`s in its results before resubmitting
  anything. Add a resume test with a fake client that "crashes" after `create`.

## 4. Resume can corrupt the page and brief: a non-atomic pair write, edits applied twice, and a baseline held only in memory

- **Severity:** major. **Tag:** correctness.
- **Location:** spec:149-152, 165-172, 257-259.
- **Defect:** The spec saves run state per stage, but a stage writes the worktree several times
  inside itself. Four cases break a resume:
  1. *The page and brief aren't written together.* They're two separate writes (spike:207-209,
     401-402). A crash between them leaves an edited page beside an unedited brief, or the reverse.
     The spec doesn't apply go-conv's atomic-write rule to them.
  2. *Edits can be applied twice.* The edit contract applies its edits, then gates, then may retry
     against "the edited text" (spike:428-430). If drafter dies after applying edits but before
     saving state, a resume re-sends the same answer against a page that already holds the edits.
     Each `old` span then occurs zero times. The answer is refused, and the retry costs money.
     Worse, a partial match could apply an edit on top of an edit.
  3. *The round-2 baseline lives in memory.* The narrowed reads' diff comes from a round-1 page
     snapshot that the spike keeps in a variable (spike:480, 302). A resume after the redraft has
     no baseline, so round 2 can't be narrowed correctly.
  4. *External edits get overwritten.* Nothing checks whether the page or brief changed between a
     stop and a resume, such as a Geoff edit or a planning-session fix. Resume silently overwrites
     them.
- **Proposed fold:** Treat the run directory as a write-ahead log. Before any worktree write, save
  the page and brief contents and their SHA-256 under the stage and attempt. Then write both files
  through `atomicfile.WriteFile`, then record "applied" with the post-write hashes. On resume, hash
  the worktree's page and brief:
  - They match the last "applied" hashes: continue.
  - They match the pre-write snapshot: the write never happened, so redo it from the saved answer
    at no cost.
  - Anything else: stop, and name the external change. Never overwrite it.

  Keep the round-1 baseline as a file in the run directory. Add crash-injection tests at each write
  boundary.

## 5. Nothing enforces one executor per worktree, and a queued run can write into the wrong tree

- **Severity:** major. **Tag:** correctness.
- **Location:** spec:128-133, 261-265.
- **Defect:** The planning session writes the handoff records and runs `drafter page` "in the
  foreground or queued for the night" (spec:131-132). The spec takes no worktree lock and checks no
  identity, so three failures are open:
  1. *The planning session races drafter.* It can keep working in the same worktree, planning the
     next pages, retagging facts, or committing. That breaks the global rule "One executor per
     worktree". drafter's fact excerpts, gate fingerprints, and edit spans then shift underneath it.
  2. *Two drafters can run one handoff.* A `--resume` started while the original is still alive
     (one that looked dead after a suspend) drives the same pages and run directory as the
     original.
  3. *A queued run can write into another branch.* It holds a path. If the pass closes and the
     worktree is removed, or the same `.claude/worktrees/<name>` path is recreated on another
     branch, the run writes pages into that other branch's tree. The cairn checkout carries several
     reused-name scratch worktrees, three of them detached (`git worktree list`, 2026-10-12).
- **Proposed fold:** drafter takes a non-blocking `flock` on
  `$(git rev-parse --git-dir)/drafter.lock` for the whole run, and a second one on the run
  directory. Either lock busy means exit with the holder's PID, which also makes the run visible to
  `pgrep`. The handoff records the worktree path, branch, and HEAD. At start and at every resume,
  drafter verifies the branch is the same and HEAD is that commit or a descendant, and stops on any
  mismatch. The spec states that the planning session stops editing the worktree while drafter
  runs, and that it learns drafter is done from the lock and the record, not by guessing.

## 6. One page's gate fails on another page's in-flight state, and an escalated page poisons the rest of the run

- **Severity:** major. **Tag:** correctness.
- **Location:** spec:139-143, 154-155, 261-265.
- **Defect:** docs-gate:7-12 says "every component reads the whole tree except three". Only Vale,
  tellgrader, and provenance narrow to `--page` and `--brief`. The links, snippets, arm-index,
  facts, and option checks see every sibling page. drafter runs several pages in one worktree, so
  three failures follow:
  1. *A sibling's defect fails the page.* A sibling page's broken link or snippet fails this page's
     gate. That spends this page's two gate-fix turns on a failure the prompt tells the model to
     ignore ("Fix every failure that names this page", spike:247), and then escalates this page
     for a fault that isn't its own.
  2. *An escalated page stays red in the tree.* A page that escalates on a red gate (spec:154)
     stays in the worktree, so every later gate in the run fails too.
  3. *The record names the wrong cause.* Pilot criterion 2 (spec:304-305) would count each such
     page as a pipeline fault, and its escalation record would name a cause outside the page.
- **Proposed fold:** Attribute gate failures by page. Gate extraction already splits the log by
  component, so it can also tag each failure line by whether it names this page or this brief.
  - A red gate with no failure naming the page is a **foreign** failure. drafter spends no fix turn
    on it. The page holds, and drafter re-gates it after the other pages settle.
  - A foreign failure that persists stops the run with "tree red outside drafter's pages". It
    doesn't escalate the page.
  - When a page escalates on a red gate, drafter moves the page and brief out of the worktree into
    its run record and restores the pre-run versions (finding 4's snapshot). The tree stays green
    for the remaining pages, and the planning session reads the failed draft from the record.

  Test with a fixture where page B's broken link reaches page A's gate.

## 7. Errors are misclassified: a spend limit, a transport fault, an expiry, or a truncation each takes the wrong path

- **Severity:** major. **Tag:** correctness.
- **Location:** spec:267-270, 149-152.
- **Defect:** The spec names three error classes: a server-side error retried once, and an invalid
  request or a refusal, which escalates. The API and the runtime produce more than that:
  1. **Spend limit reached.** A workspace limit returns HTTP 400 `invalid_request_error`, "You have
     reached your specified workspace API usage limits". An organization cap returns 429
     `enforced_spend_limit_reached` with no `retry-after` (limits-docs). Under the spec's rules,
     the first escalates every page with a false reason, and the second is retried once and then
     escalates.
  2. **Transport errors while polling.** DNS failure, a reset after resume from suspend, or a
     timeout aren't "request errors", and the spec doesn't say what they do. If they abort the run,
     resume handles it. If they escalate the page, a batch that's still running and already paid
     for is abandoned.
  3. **`expired` and `canceled` results.** The 24-hour expiry (batch-docs:44, 47, 722) and a
     cancellation (batch-docs:721) aren't billed, but the spec has no path for them.
  4. **A truncated answer.** A message with `stop_reason: max_tokens` has no stated handling. The
     spike refused a missing `</page>` only through its regex (spike:204-206). The spike also
     crashed outright on a draft brief that isn't valid JSON (spike:208), and the spec's
     broken-brief rule covers only the edit contract (spec:171-172).
- **Proposed fold:** Specify a classification table that the state machine tests cover:
  - Spend limit (either form): stop the whole run, write state, escalate nothing, and print the
    limit message.
  - Transport error: retry with backoff, bounded by wall time, never by attempts. It never changes
    a page's state.
  - 429 with `retry-after`: wait and retry.
  - `errored` with `api_error` or `overloaded`: resubmit once.
  - `errored` with `invalid_request`: escalate.
  - `expired` or `canceled`: resubmit once at no charge, then escalate as infrastructure.
  - `stop_reason` of `max_tokens` or `refusal`: refuse the answer and never write it to the
    worktree. For `max_tokens`, one contract-style retry, then escalate.
  - A draft brief that isn't JSON goes through the same refusal path as the edit contract.

## 8. OWNER FORK: the server backstop counts calendar months, not billing cycles, and batches can overshoot it

- **Severity:** major. **Tag:** correctness.
- **Location:** spec:225-228, 233-241, 321-322.
- **Defect:** The backstop has four gaps:
  1. *It runs on a different clock.* limits-docs says spend caps are per calendar month, with
     access resuming "00:00 UTC on the first day of the next month". drafter's ceiling resets on
     the billing-cycle date (spec:233-234). A credit cycle that spans a month boundary has two
     $160 workspace windows. So if drafter's own accounting fails, the backstop allows up to $320
     against $200 of credit, which is the exact fault it exists to catch. In the other direction,
     the workspace limit can block legitimate spend early in a cycle.
  2. *It isn't hard.* batch-docs:48: "batches may go slightly over your Workspace's configured
     spend limit".
  3. *The overrun destination is unknown.* The spec never says what happens to spend beyond the
     $200 credit, whether the organization has a payment method or auto-reload that would bill a
     card, or whether requests simply fail.
  4. *The local clock is undefined.* The spec doesn't say whether the billing-cycle date is in UTC
     or local time.
- **Options:**
  - (a) Set the workspace limit to $100 a month, so any two calendar months stay at or under $200.
    This is simple, but it halves the most drafter can spend in a single month.
  - (b) Keep $160 and accept that the backstop guards a month, not a cycle. It stays a
    coarse guard against runaway spend, not a credit guard.
  - (c) If the Admin API can set a workspace limit (the spec's open item), have drafter set it at
    each cycle reset to the credit still unspent. Fall back to (a) if it can't.
- **Recommendation:** (c) with (a) as the fallback. Also verify during the build that the
  organization has no auto-reload or payment method that turns an overrun into a charge, record
  that in the estate inventory, and state the cycle date in UTC.

## 9. OWNER FORK: drafter's output is uncommitted with no durable copy, and the spike deleted an existing page before drafting

- **Severity:** major. **Tag:** correctness.
- **Location:** spec:130-133, 248-253; spike:462-464.
- **Defect:** The spec never says who commits a page that drafter accepted or escalated, or when.
  Until someone does, the only copy of the page is an untracked or modified file in a shared
  worktree, through a night run and into the next morning. A cleanup, a `git checkout .`, a stash,
  or a worktree removal by any session destroys it. The records list requests, responses, and
  answers (spec:250-252), not the final page and brief, so a lost page can only be rebuilt by
  replaying edits by hand. The spike also unlinked the existing page and brief before drafting
  (spike:462-464, "The drafter must not see the page it rebuilds"). Ported to a rework page, that
  deletes published content in the worktree, along with any uncommitted edits to it, before any
  model call.
- **Options:**
  - (a) drafter commits each page's final page and brief on the worktree branch, files named
    explicitly, with a record-ID trailer. A durable resume point and an easy diff, but drafter
    becomes a committer on a branch the planning session owns.
  - (b) drafter never commits. It writes `final.page.md` and `final.brief.json` with their hashes
    into the run record, and the planning session commits after reading the record.
- **Recommendation:** (b). It keeps one committer per branch, which matches "Two sessions never
  both close, merge, or release one branch". Pair it with finding 5's lock, so nothing touches the
  tree until the run releases. Independent of the fork, state that drafter never deletes a file:
  it keeps the old page out of the drafter's inputs, snapshots the page and brief before the run
  into the record, and refuses to start when they hold uncommitted changes it didn't make.

## 10. Prompts, agent definitions, config, or the binary can change mid-run or between stop and resume

- **Severity:** minor. **Tag:** correctness.
- **Location:** spec:120-124, 99-102, 257-259.
- **Defect:** drafter builds each stage's prompt when that stage runs, from `docs-page-chain.js`,
  the agent definitions in `~/.claude/agents/`, and `drafter.toml`. The chain took 28 commits in a
  month (spec:108), and other sessions edit agent definitions. A run that spans the night, or a
  resume days later, can draft round 1 under one set of builders and redraft under another, and the
  record doesn't say so. A gate-fix continuation then extends a conversation whose system prompt
  has changed. A drafter upgrade that changes the state schema can misread an old run's state.
  This is the same hazard as the guards rule "Never edit a script a running gate executes".
- **Proposed fold:** At run start, copy the prompts module, each seat's agent definition, and
  `drafter.toml` into the run directory with their hashes, and build every stage from those copies.
  State carries a schema version and the drafter version. A resume under a different schema refuses
  with a clear message, and the record names every input hash.

## 11. Cost computation drifts from the Console: no price table rule, and cache writes are priced at one rate

- **Severity:** minor. **Tag:** correctness.
- **Location:** spec:226-228, 243-246, 307.
- **Defect:** The spike prices every cache write at 1.25 times the input rate (spike:181), the
  five-minute rate. The spec itself observed that a one-hour write doubles input cost
  (spec:245-246). The spec doesn't say where prices live or what happens for a model without a
  price. If a pilot moves a seat to Haiku 5.5 through config (spec:274-276, 323) without a price
  entry, the cost could compute as zero, every cap would pass, and the 5% ledger match would fail.
- **Proposed fold:** Keep a price table keyed by model, with input, output, cache-read, 5-minute
  write, and 1-hour write rates and the 50% batch discount. drafter refuses at config load any seat
  whose model has no entry. Cost uses the cache-creation breakdown by TTL from `usage`. A unit test
  prices one recorded response of each cache shape.

## 12. Run identity is undefined, and record paths collide

- **Severity:** minor. **Tag:** correctness.
- **Location:** spec:94, 251-252.
- **Defect:** `--resume <run>` names no run ID format. Records live at
  `runs/<repo>/<date>-<page>/`, so two runs of the same page on one day overwrite each other's
  records: a rerun after an escalation, or two worktrees of the same repo. A run that crosses
  midnight, or resumes the next day, has an ambiguous `<date>`.
- **Proposed fold:** Assign a run ID at start, for example a UTC timestamp plus a short random
  suffix. Lay out records as `runs/<repo>/<run-id>/<page>/` and create the directory exclusively,
  so drafter refuses one that already exists. `--resume` takes that ID, and the ledger's reserve and
  settle lines carry it.

## 13. Friction entries the seats would file are dropped

- **Severity:** minor. **Tag:** correctness.
- **Location:** spec:159-163, 248-252.
- **Defect:** In the chain, the drafter, page inputs, and the fact read file friction entries in
  `docs/internal/docs-friction-log.md` (chain:197-204, 834-840). In drafter, seats can't edit
  files, so "any edit it would make becomes a finding" (spec:162). But friction never blocks a
  page, and the spike wrote it only to a scratch file (spike:210). The spec's record list doesn't
  include friction, so the design-flaw signal the chain collects is lost.
- **Proposed fold:** Put friction in `record.json` as its own list per seat. The planning session
  then files it into the friction log at commit time, under the same single-committer rule as
  finding 9.

## 14. Handoff records written into the worktree change the gate's fingerprint and can be committed by accident

- **Severity:** minor. **Tag:** correctness.
- **Location:** spec:130-131.
- **Defect:** "The planning session writes the records into the worktree". Untracked files are
  part of `cairn-run-gate`'s tree fingerprint (gate:59-61), so each record invalidates receipts. The
  records can also reach whole-tree docs checks, depending on where they sit, and they invite a
  stray commit.
- **Proposed fold:** Write handoffs under the git directory (`$(git rev-parse --git-dir)/drafter/`)
  or under `~/.local/state/drafter/handoffs/<run-id>/`, outside the tree. The handoff names the
  worktree path, branch, and HEAD, per finding 5.

## 15. The `cairn-run-gate` protocol and suspend behavior aren't specified for a non-Claude caller

- **Severity:** minor. **Tag:** correctness.
- **Location:** spec:139-143, 263-265.
- **Defect:** The spec doesn't specify how drafter, a caller outside Claude, handles the gate
  wrapper's protocol or a suspend:
  1. *Exit 75* means "still running, re-issue the same command" (gate:5-9).
  2. *Exit 76* means a deferred gate. It happens when `RUN_GATE_IF_BUSY=defer` is inherited from
     the calling environment (gate:41-46), and drafter would read it as a red gate.
  3. *"gate exit: 1 (vanished 3 times)"* is a terminal infrastructure failure (gate:20-22), not a
     page defect.
  4. *The lane is unset.* The spike used `CAIRN_GATE_LANE=light` (spike:217), and the docs gate
     launches no browser, but the spec leaves the lane unspecified. On the default heavy lane, a
     night run queues behind other sessions' e2e gates.
  5. *A suspend mid-poll* is otherwise benign, since batches run server-side for up to 24 hours and
     results last 29 days (batch-docs:44-45). But an HTTP call in flight across a suspend can hang
     without a client timeout (Go's `http.DefaultClient` sets none).
- **Proposed fold:** In the gate package, loop on 75, clear `RUN_GATE_IF_BUSY` from the gate's
  environment, map the vanish and 76 outcomes to "infrastructure, stop the run" (never a page
  escalation), and take the lane from `drafter.toml`, light for cairn. Give the API client an
  explicit per-request timeout. Holding a sleep inhibitor through polling isn't needed; finding 7's
  transport-error retry covers the resume after a suspend.

## 16. Input assembly can inline any file a prompt names, including untracked, ignored, and out-of-repo files

- **Severity:** minor. **Tag:** optional.
- **Location:** spec:82, 159-161.
- **Defect:** "Every repository file the prompt names" is unbounded. The spike's regex also read
  absolute paths under `~/.local/share/cairn/` (spike:64). An ignored local file named in a prompt,
  such as `.dev.vars`, would be inlined into a request, sent to the API, and kept in the records
  for 30 days.
- **Proposed fold:** Inline only paths that `git ls-files` lists in the worktree, plus an explicit
  allowlist in `drafter.toml` for out-of-repo register files. Report anything else as "not inlined"
  in the request.

## 17. Over-ceremony: pruning records at 30 days adds a deletion path that can destroy pilot and escalation evidence

- **Severity:** minor. **Tag:** optional.
- **Location:** spec:252-253.
- **Defect:** The records are small text files. Pruning them is a new deletion path. It can remove
  an escalated page's record that the planning session hasn't acted on yet, or pilot evidence that
  cutover depends on (spec:299-312). And a run still holding resumable state shouldn't be pruned at
  all.
- **Proposed fold:** Drop pruning from sub-project 1. If it's needed later, prune only finished
  runs that have been committed or acknowledged, never one that holds open state.

## 18. Over-ceremony: a token-count call before every request adds a network dependency without making the cap accurate

- **Severity:** minor. **Tag:** optional.
- **Location:** spec:226-228.
- **Defect:** The counting endpoint prices input exactly, but output is about half the cost
  (finding 2). A precise input count therefore doesn't make the cap estimate precise. Each count
  call is also one more network round trip that can fail and block a stage.
- **Proposed fold:** Reserve a worst case from a local upper bound: request bytes divided by 3 for
  input, plus `max_tokens` for output. Settle against `usage` (finding 2). Keep the counting
  endpoint only for `--dry-run`'s printed estimate.

---

## Checked and sound

- **The facts store.** drafter seats have no tools, and the no-tools note turns every retag into a
  finding (spec:161-163; spike:119-126). drafter doesn't write facts, so the facts store has no
  write path to corrupt. What remains is concurrent edits by the planning session, which finding 5
  covers.
- **Batches through a suspend.** Batches keep running server-side while the laptop sleeps, with a
  24-hour processing window and 29 days of results (batch-docs:44-45). A suspend delays a run
  without losing one, provided findings 3, 7, and 15 hold.
- **Unbilled outcomes.** `errored`, `canceled`, and `expired` requests aren't billed
  (batch-docs:720-722), so resubmitting them under finding 7 can't pay twice.
- **The outline's shared index.** The index link's read-insert-write already holds a lock keyed by
  the index path (chain:96-103).
