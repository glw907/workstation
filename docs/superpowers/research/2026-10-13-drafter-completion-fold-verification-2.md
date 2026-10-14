# drafter completion plans: second fold verification (passes 2 and 5)

Verifier: `claude-opus-5-5`, 2026-10-13, no part in either fold, on branch `drafter-completion-plans`
at `df7d70d`, per `spec-plan-review` "The verification read". Scope, narrowly: whether the first
verification read's nine findings closed where the fold record cites
(`git diff d64a88b df7d70d -- docs/superpowers/plans/`), whether the fold introduced a contradiction
with passes 1, 3, and 4 or with the completion design's rulings, and whether any new mechanism lacks
a source or probe. The plans were not re-reviewed whole.

Citations `P2:N` and `P5:N` are lines of `docs/superpowers/plans/2026-10-13-drafter-p2-money-plan.md`
and `docs/superpowers/plans/2026-10-13-drafter-p5-pipeline-plan.md` at `df7d70d`.

## Probes run

- `custom_id` length and pattern, a scratch Go program in `scratchpad/verify2/probe/`: the run ID
  suffix is 8 hex (pass 1, `NewID`, example `20261013T142233Z-7f3a09c1`), the page key 12 hex, the
  longest seat `consistency` (pass 1's seat list: `draft`, `structure`, `editor`, `fact`, `reader`,
  `coverage`, `consistency`). The ID's length is 35 plus the stage token plus the attempt's digits;
  with a three-digit attempt, any stage token up to 26 characters fits in 64. Every form built
  (stage `1`, `7`, `finalread`, `roundtworeads`, `consistency`) matched `^[a-zA-Z0-9_-]{1,64}$`, the
  longest at 51 characters. The page path never changes the length, since it's hashed.
- SDK v1.80.0, `messagebatch.go:346` and `:541`: "Must be unique for each request within the
  Message Batch." Uniqueness is per batch only; the API says nothing across batches.

## Question 1: did each finding close at the cited location?

- v-1 (blocker): closed for its letter. The form at P5:101-105 carries the seat, its tokens are
  `[a-z0-9]`, the state map names page and seat, the fake rejects repeats within one `Create`
  (P5:87-90, P2.5 at P2:363-365), and P5.1 asserts distinct IDs in stage-4 and stage-7 batches
  (P5:189-190). The fit inside 64 characters holds (probe above). The ledger key
  `<batch-id>/<custom_id>` is unique, since the batch ID differs between batches. But uniqueness
  within one batch isn't what resume and the state map need: see finding 1.
- v-2 (major): closed for the run that finishes. P5:140-143 voids the intent at once and P5:188-189
  adds the row with `OpenIntents` empty. The void isn't recorded in run state, so a resumed sync run
  settles the same intent a second time: see finding 2. The non-400 4xx actions are unnamed: see
  finding 3.
- v-3 (major): closed. P5:466-473 and the executor prompt's lines 38-40 agree: the rerun is drafter
  only, on the same Workflow run file and page, and a different page ends the pass "not
  pilot-ready" with one question for Geoff. Ruling 5 holds. Ruling 8's "one rerun if the budget
  allows" is narrowed only where ruling 5 forces it, and the PR question surfaces the narrowing.
  The rerun's preconditions hold: an escalated page's files go back to their pre-run snapshots
  (P5:157-160), so the scratch worktree passes P5.2's clean-tree refusal; the run directory lives
  under `state_dir` (pass 1, `run.Create`), not in the tree; a drafter fix lands in the drafter
  worktree and leaves the handoff's checksum intact; the rerun gets a new run ID and so a new
  `custom_id` suffix.
- v-4: closed at P2:143-146 and the P2.2 row at P2:239-242.
- v-5: closed at P5:175-176 (P5.1 Files) and P5:230-232 (P5.2 keeps the resume fields). P5.1 and
  P5.2 sit in different, sequential pairs, so the shared `internal/run/` path causes no conflict.
- v-6: closed at P2:84-85 and the P2.3 row at P2:297-298, consistent with the spec's failures table
  (spend-limit 400 stops, any other sync 400 escalates).
- v-7: closed at P5:454-456.
- v-8: closed at P5:402-403.
- v-9: closed at P2:239-240.

## Question 2: contradictions

None between passes 2 and 5 and passes 1, 3, or 4: the seat names, the run ID suffix, the run
directory's home, and `handoff.Verify` read the same. Against the design's rulings: ruling 5 and
ruling 8 now agree in P5.8 and the executor prompt, and no other plan or the conductor prompt still
mentions a rerun on another page. The path figure (620, 2.6 times 240) appears consistently at P5:46
and P5:499 and stays under the 720 line. Two internal contradictions remain, findings 1 and 2.

## Question 3: new mechanisms

The fold's new mechanisms are the seat-bearing `custom_id` (probed above), the fake's duplicate
check (sourced at `messagebatch.go:346`), and void on a provably unbilled error. That last one rests
on P2's own retry rules: `Create` and `Send` retry only pre-write failures and non-spend 429s
(P2:103-107), and any post-write failure is `ErrMaybeSent` (P2:108-112). So `ErrTransport` from
either call means no attempt reached the model, and a 4xx is a refusal. The reasoning holds and
needs no probe.

## Findings, ranked by consequence

### 1. Major, correctness: `custom_id`s repeat across batches of one run, which resume's adoption and the state map rely on

- Location: P5:101-105 (the form; `<attempt>` undefined beyond resubmission); P5:140 and P2:111-112
  ("a new attempt" is used only for a resubmission); P5:189-190 (the row checks within one batch);
  P2:99-100 ("resume adopts only by `custom_id`, so it can't cause a false match"); P5:246-248.
- Defect: the fold made IDs unique within one batch. The run still sends the same page, stage, and
  seat more than once without a failures-table resubmission. Stage 2's gate-fix exchanges are
  successive draft-seat requests (spec "The pipeline", stage 2). Stage 7's final reader read and its
  reader retest are both the `reader` seat. Stage 7's redraft retries under `retries.edit_contract`
  repeat too. Under the plan's only stated meaning of "attempt", each pair gets the same
  `custom_id`. Two things break:
  - The state's map from `custom_id` to page and seat loses an entry.
  - Resume adopts by `custom_id` among batches created within 10 minutes before the intent
    (P2:96-100). Suppose a stop falls after the retest's `Create` and before its batch ID is
    recorded. Resume can then adopt the ended final-read batch as the retest's answer, the false
    match P2:100 says can't happen.
  The ledger is unaffected, since its batch key carries the batch ID. The offline rows all pass,
  because none spans two submissions of one seat in one stage.
- Fix: P5:101-105 defines `<attempt>` as a per-run counter for each page, stage, and seat that
  every submission advances: an exchange, a retry, a retest, or a resubmission. Then a `custom_id`
  is unique across the run, as the spec's "Resume" asks ("unique to run, page, stage, and
  attempt"). Add a P5.1 row: a synthetic run with two gate-fix exchanges and the reader-redraft path
  repeats no `custom_id` in state. Add a P5.2 twin row: a stop after the reader retest's `Create`
  with no batch ID, where `List` also returns the ended final-read batch inside the margin, adopts
  nothing from that batch.

### 2. Major, correctness: a sync intent voided at once is settled again as `estimated` on resume

- Location: P5:140-143 (the void at once); P5:250-251 and the row at P5:269-270 (resume settles
  "a sync intent with no saved response" `estimated`); P2:142-147 and P2:164-165 (`Settle` is a
  no-op only on a repeated key).
- Defect: in sync mode, a `Send` that returns `ErrTransport` or `ErrSpendLimit` voids its intent
  (key `<intent>/void`), then stops the run resumably (`transport` or `spend limit`). The state
  intent remains, with no saved response and no mark that it settled. On `--resume`, P5.2's rule
  settles it `estimated` at its share (key `<intent>/<custom_id>`, a different key). The ledger
  appends that line, so a request the API never billed carries a charge of up to its worst case.
  That inflates the page total, the cycle total, and the spend report that Geoff compares against
  the Console. It also contradicts "void ... one line closing the whole intent" (P2:142-143). The
  error fails safe on money but is wrong. P5.2's row at P5:269-270 would assert the wrong behavior
  for this case. Batch mode is unaffected: resume lists, finds nothing, re-voids under the same
  key (a no-op), and resubmits.
- Fix: P5.1 records each settlement kind in the state intent, so a void at once writes `void`
  there. P5.2's resume settles `estimated` only for a sync intent with no saved response, no
  recorded settlement, and an entry still in `OpenIntents`. Add a P5.2 row: a sync `Send` returns
  `ErrTransport`, the run stops, and resume leaves one `void` line, no `estimated` line, and one
  new reserved attempt.

### 3. Minor, correctness: a 4xx other than 400 has no named action

- Location: P5:140-143 ("then takes its failures-table action (a 400 escalates the page with the
  error)"); the spec's "Failures" table names only 400, 429, 500, and 529.
- Defect: a `Create` or `Send` 401 (`authentication_error`), 403 (`permission_error`), 404, or 413
  is voided but has no row in the failures table. `ErrNoWorkspaceCheck` has no row and no `Summary`
  stop reason either. The executor must guess between escalating every page one by one on a
  revoked key and stopping the run.
- Fix: one clause at P5:142-143. Any other 4xx escalates the page with the error, as `Classify`
  does for an unnamed `ErrType` (P2:126-127). `ErrNoWorkspaceCheck` is a programming error that
  `pipeline.Run` returns, so the run exits 2. A 401 or 403 could instead get its own stop reason;
  that is a design choice, so name whichever is chosen.

### 4. Minor, optional: P2's `void` definition no longer covers every void

- Location: P2:142-143 ("an intent that never reached the API").
- Defect: v-2 now voids intents the API refused with a 4xx, which did reach it. The ledger needs no
  change, but the definition misleads P2's executor and reviewer.
- Fix: "an intent the API never billed (it never reached the API, or the API refused it)".

### 5. Minor, optional: the stage tokens are never named, and the length row varies the wrong input

- Location: P5:102-105; the row at P5:284.
- Defect: the fit inside 64 characters is argued from the seat alone, and no stage token is named.
  The probe shows the margin is wide (26 characters of stage token with a three-digit attempt), so
  this is not a defect today. P5.2's row builds IDs for "the longest fixture page path", but the
  path is hashed and never changes the length.
- Fix: name the stage tokens (for example `s1` to `s7`). The row builds the longest stage token
  with `consistency` and the largest attempt the budgets allow.

## Counts

0 blockers, 2 majors, 3 minors (1 correctness, 2 optional). The blocker from the first read is
closed. Both majors come from that blocker's fold and v-2's fold. Each needs a clause and a row in
P5, with no new mechanism, so a fold that the coordinator checks against this record should
suffice. The skill's rule calls for a further verification read only after a blocker.
