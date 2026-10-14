# drafter completion plans: fold verification (passes 2 and 5)

Verifier: `claude-opus-5-5`, 2026-10-13, no part in the fold, on branch `drafter-completion-plans`
at `d64a88b`, per `spec-plan-review` "The verification read". Targets: the pass 2 and pass 5 plans
and executor prompts. Read against the fold record, the four P2 and P5 reviews, the completion
design's rulings 1 to 8, the pipeline spec, and the pass 1, 3, and 4 plans' Interfaces.

Citations `P2:N` and `P5:N` are lines of `docs/superpowers/plans/2026-10-13-drafter-p2-money-plan.md`
and `docs/superpowers/plans/2026-10-13-drafter-p5-pipeline-plan.md`.

## Probes run

- SDK v1.80.0 (module cache), a scratch program in `scratchpad/verify/probe/`, client built as P2's
  `New` builds it (`WithoutEnvironmentDefaults`, `WithAPIKey`, `WithBaseURL`, `WithMaxRetries(0)`,
  `WithHeader("anthropic-workspace-id", ...)`):
  - `Batches.New` to a closed port: `*url.Error`, `errors.As` finds `*net.OpError` with `Op` `dial`.
  - The same to `nonexistent.invalid`: `*net.OpError` `Op` `dial` wrapping a `*net.DNSError`.
  - A server that reads the whole `Create` body and resets: one server hit, `*net.OpError` `Op`
    `read`. So P2's "dial or DNS retries, anything after write is `ErrMaybeSent`" is implementable
    with `errors.As` exactly as written.
  - `Models.List(limit 1)` with `option.WithResponseInto`: the client-wide workspace header reached
    the server, and the response's `anthropic-workspace-id` header was readable. P2's
    `CheckWorkspace` mechanism holds.
- `messagebatch.go:346` and `:541`, on `custom_id`: "Must be unique for each request within the
  Message Batch."
- The pricing page (platform.claude.com/docs/en/about-claude/pricing, read 2026-10-13): Opus 5.5
  $4 / $5 / $8 / $0.20 / $20 (footnote 2: cache hits "priced at 0.05x the base input price");
  Haiku 5.5 $0.10 / $0.125 / $0.20 / $0.01 / $0.50 up to 100,000 and $0.50 / $0.625 / $1 / $0.05 /
  $2.50 over. P5.7's cross-check figures (P5:394-396) match.
- drafter `internal/plan` at `73ff07a`: `CheckFile`, `CheckOptions{Root, FactsDir, Outline}`,
  `CheckFactsDir`, `LoadFacts`, `LoadOutline`, `LoadOutlines` exist, as P5 consumes them.

## Question 1: did each blocker and major close where the fold record cites?

Yes for every blocker and major in the four reviews, with one fold that closed its finding's
letter but introduced a new blocker (finding 1 below, from i-2).

- p2m-1 to p2m-9: closed at P2:101-111 (retry discipline, `ErrMaybeSent`), P2:269-274
  (credential rows), P2:86-90 and P2:275-279 (workspace gate), P2:114-117 and P2:289-293 (spend
  limits), P2:101-105, P2:121-128 (5xx, 529, stop reasons), P2:65-69 and P2:299-300 (two timeouts),
  P2:132-134 and P2:168-172 (line schema, file states), P2:228-234 (barrier and no-op twin),
  P2:339-352 (smoke `max_tokens`, `-count=1 -timeout 2h`, recorded batch, `additionalProperties`).
- p5m-1 to p5m-11: closed at P5:68-69, P5:321-323, P5:437-438, P5:121-125 with P5:102-103,
  P5:138-140 with P5:200, P5:449-457, P5:408-410, P5:409 and P5:445-446, P5:391-397, P5:25-29.
- c-1 to c-15: closed at P2:228-234, P2:269-274, P2:139-146 with P2:235-238, P5:408-413,
  P2:303-307, P2:121-128 with P2:294-298, P5:271-273, P5:89-96 with P5:189-191 and P5:286-288,
  P5:264-267, P5:182-188, P5:206-212, P5:213-214 with P5:275 and P5:298-299, P2:106-111 with
  P2:285-288, P2:339-359, P5:245-270.
- i-1 to i-11: closed at P2:101-111, P5:99-101 with P5:87-88 and P5:274 (see finding 1),
  P2:94-99 with P2:303-307, P2:142-143 with P5:259-260, P2:136-146, P5:129-131 with P5:236 and
  P2:164-166, P5:455-456 with P5:249-250, P2:349-350, P2:168-172, P2:119-120 with P4's `gate.Env`,
  P5:405-407.
- c-16, c-17, c-18 and p5m-6, p5m-16, p2m-16: applied per ruling 8 at P5:449-457, P5:52-60,
  P5:458-463, P5:484-485, P2:27-28. The mechanical folds (effective page cap in the meter, a window
  covering every live spend) are in.

## Question 4: open owner forks

i-7's fork (drain, exit, or cancel on a resumable stop with batches in flight) is answered by the
spec, as the fold says: the stop table's "the run stops, resumable" (spec "Stop rules", last row)
and "Resume"'s "`--resume` ... settles any ended batch it hasn't ledgered" together read as exit
and settle on resume, and the meter counts open intents at their worst case meanwhile, so the
guard stays conservative. Nothing is left for Geoff. No other fork remains open.

## Findings, ranked by consequence

### 1. Blocker, correctness: the `custom_id` form collides inside every multi-seat batch

- Location: P5:99-101; P5:87-88 (the fake); P5:274 (the only row); P2:144.
- Defect: the form `<run suffix>_<12 hex of page key>_<stage>_<attempt>` has no seat. The spec puts
  several seats in one batch for one page, stage, and attempt: "Round-1 reads. The structural edit,
  register editor, and fact read run in one batch" (spec "The pipeline", stage 4), and stage 7's
  scoped re-reads plus the reader retest. Those requests get identical `custom_id`s, and the API
  requires "unique for each request within the Message Batch" (`messagebatch.go:346`). The live
  stage-4 `Create` fails with a 400 on P5.8's page, after the draft has been paid for, so the page
  escalates before the round-1 reads and misses ruling 8's bar; the rerun hits the same wall. Even
  if the API accepted it, the state's map from `custom_id` to page loses the seat, and the ledger's
  batch key `<batch-id>/<custom_id>` (P2:142) collides, so the second seat's settle is a no-op and
  the intent never closes (P2:144 assumes uniqueness). The fake checks only the pattern, so every
  offline test passes. This came in with i-2's fold, whose proposed form also lacked the seat.
- Fix: P5:99-101 becomes `<run suffix>_<12 hex>_<stage>_<seat>_<attempt>`, with stage and seat
  tokens limited to `[a-z0-9]` (the longest seat, `consistency`, keeps the ID well under 64), and
  the map in state goes from each `custom_id` to its page and seat. The fake rejects a `Create`
  whose `custom_id`s repeat within the batch, as the API does. P5.2's row at P5:274 adds: every
  `custom_id` in one stage-4 and one stage-7 batch is distinct. P2.5's smoke fake rejects
  duplicates too, since its batch holds seven seats.

### 2. Major, correctness: a `Create` that the API refuses outright leaves its reservation open for good

- Location: P5:129-137 (the money path); P5:236-237 (resume voids only intents no state names);
  P5:455-456 (no open intent before a rerun).
- Defect: the money path settles results, voids an unmatched `ErrMaybeSent`, and estimates a lost
  `Send`, but names no settlement for a `Create` that fails definitively and the run carries on: a
  400 `invalid_request_error` (a bad `custom_id`, as in finding 1, or a request-shape error the API
  checks at create), 401, 403, 404, or 413. The intent has a state entry, so resume never voids it;
  the run finishes rather than stops, so there is nothing to resume. The reservation counts at its
  `Worst` (up to the page cap) in the cycle total and in the meter (`total` plus `open.worst`)
  until the cycle resets. That shrinks P5.8's rerun cap, may push it under $5, and makes P5.8's
  "the earlier run's state shows no open intent" impossible to satisfy.
- Fix: P5.1 adds: a `Create` or `Send` error that proves the request was not billed (any 4xx that
  isn't a spend limit, `ErrTransport`, `ErrNoWorkspaceCheck`) settles its intent `void` at once,
  then takes its failures-table action (a 400 escalates the page with the error). One P5.1 row: a
  `Create` 400 escalates the page, leaves one `void` line, and `OpenIntents` is empty after the run.

### 3. Major, correctness: P5.8's rerun on another page needs a Workflow run ruling 5 forbids

- Location: P5:453-454 ("another qualifying page after an input cause"); the executor prompt,
  line 37-38 ("run no other Workflow"); design Technical notes 5.
- Defect: a different page has no handoff until the chain's front half runs on it, which is a
  second `docs-page-chain` Workflow run. Ruling 5: "Geoff opts in to one Workflow run ... on one
  page. No other Workflow run is approved." Ruling 8 grants "one rerun if the budget allows"; it
  doesn't extend ruling 5. The plan and its prompt contradict each other, and the executor either
  breaks a ruling or stalls with no instruction.
- Fix: P5.8's rerun is a drafter-only rerun of the same Workflow run file (the same page, after a
  drafter fix or with the input left as is). An input cause that needs another page ends the pass
  "not pilot-ready", with the cause and one batched question in the PR: approve a second Workflow
  run on a named qualifying page.

### 4. Minor, correctness: an `estimated` settlement's key can differ between the run and its resume

- Location: P2:142-143; P5:136; P5:240-241.
- Defect: a sync key is "the message ID when one arrived, else `<intent>/<custom_id>`". A stream
  lost after `message_start` has a message ID in memory, so an in-run `estimated` settle can key on
  it; a crash before the state records that settle leads resume to settle the same attempt again
  under `<intent>/<custom_id>`, two lines for one attempt.
- Fix: P2:142-143 says an `estimated` settlement always keys `<intent>/<custom_id>`, whatever
  arrived; only an `actual` sync settlement keys on the message ID.

### 5. Minor, correctness: P5.1's money path writes state intents whose fields P5.2 owns

- Location: P5:97-101 (Interfaces), P5:129-131 and P5:177 (P5.1 writes "the state intent"),
  P5:167-169 (P5.1 Files omit `internal/run`), P5:243 (P5.2 Files hold it).
- Defect: P5.1's money rows need the intent fields in `run.PageState` and the `StateSchema` bump,
  but only P5.2 lists `internal/run`. The P5.1 subagent either strays outside its Files or keeps a
  second intent store P5.2 must reconcile; the task-scope review then reads against the wrong Files.
- Fix: move the intent fields and the schema bump into P5.1's Files (`internal/run/state.go` and
  its test); P5.2 keeps the resume fields (saved answers, write hashes).

### 6. Minor, correctness: a spend-limit 400 on `Send` has two specified outcomes

- Location: P2:82-84 (a sync 400 "comes back as an `errored` result") against P2:114-117 and
  P2:289-292 (`ErrSpendLimit`).
- Defect: the spend-limit 400's row doesn't say which call it covers, and on `Send` both rules
  apply. Both end in a `spend limit` stop in P5.1, so no money is at risk, but P2.3's executor must
  guess and the row can pass either way.
- Fix: one clause at P2:82-84: a spend-limit 400 or 429 is `ErrSpendLimit` on every call, checked
  before the `errored`-result mapping.

### 7. Minor, correctness: P5.8's dry run runs without the key in its environment

- Location: P5:443 against P5:445-446.
- Defect: the page run sources `~/.local/secrets` in its `bash -c`; the dry run, which also resolves
  the key and calls `CheckWorkspace` and `CountTokens`, doesn't. The secrets file is sourced for
  interactive shells only (workstation CLAUDE.md), so the dry run can exit 2 on `key.Resolve`.
- Fix: run the dry run under the same `bash -c '. ~/.local/secrets && ...'` form.

### 8. Minor, correctness: P5.7 doesn't name the Haiku model ID its price entry keys on

- Location: P5:390-397; P2:351-352.
- Defect: the smoke takes Haiku 5.5's ID from `claude-api`'s table, and P5.7 writes a price entry
  for "Haiku 5.5" without naming the TOML key. A mismatch fails safe (`Cost` errors on a missing
  entry) but costs a live smoke attempt.
- Fix: P5.7 names the key as the exact model ID the smoke sends, read from the same table.

### 9. Minor, optional: P2.2's "two errored sync results under one intent" row tests a state pass 5 never builds

- Location: P2:236-237 against P2:136-138 (one reservation per sync request).
- Defect: a sync intent covers one request, so the row exercises a shape the contract forbids. It
  does no harm but reads as permission for multi-request sync intents.
- Fix: phrase it as two requests of one batch intent, each `errored`, keyed `<batch-id>/<custom_id>`.

## Question 2: contradictions and build order

Findings 1, 3, and 5 above. Otherwise none: path sums check (P2 355, P5 610), pair file sets are
disjoint, P2.2's `internal/batch/usage.go` lets the ledger build before P2.3, and every name passes
2 and 5 consume exists in passes 1, 3, and 4's Interfaces (`config.ScopeMoney`, `ScopeRun`,
`Sources`, `run.NewID`'s 8-hex suffix, `prompts.Round`, `handoff.Verify`, `assemble.Input.Declined`
and `CustomID`, `assemble.ConsistencyPrompt`, `edits.Render`, `gate.Env`, `gate.Run`,
`gate.ErrInfra`) or in drafter's `internal/plan` today. Ruling 2's $15 cap, ruling 4's wait,
ruling 6's cycle day, and ruling 8's page cap, bar, and class assignments all read the same in the
plans and prompts.

## Question 3: new mechanisms

Each is quoted or now probed: the dial and DNS classification and the post-write `read` error,
the client-wide workspace header and the readable response header (probes above); the per-attempt
timeout (`requestconfig.go:546-563, 630-638`, quoted by p2m-6); spend-limit shapes (rate-limits
page, quoted in the fold record); list cursor parameters (`messagebatch.go:857-867`); the
`custom_id` pattern (batches create reference) and uniqueness (`messagebatch.go:346`, which the
plan missed: finding 1); `git hash-object -w` (`docs-page-chain.js`); `tellgrader --profile`
(probed by p5m-2); prices (probed above). The 10-minute list margin and the 500 ms barrier are
design choices with stated reasons, not borrowed facts.

## Over-ceremony

None found. The test-first and per-task review load on P2 and on P5.1 and P5.2 is Geoff's ruling.

## Counts

1 blocker, 2 majors, 6 minors (5 correctness, 1 optional). By the skill's rule the blocker calls for
one more verification read after it is folded.
