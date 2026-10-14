# drafter P2 and P5 plan review: data integrity and failure risk

Reviewer lens: integrity and failure risk. Targets at `456b409`:
`docs/superpowers/plans/2026-10-13-drafter-p2-money-plan.md` (P2) and
`docs/superpowers/plans/2026-10-13-drafter-p5-pipeline-plan.md` (P5), read against the completion
design and the pipeline spec's "Operations". Line references are to those files at that commit.

## Verdict

Not ready to execute as written. One blocker (the client's in-place transport retry can pay twice
for a `Create` or `Send` with no reservation behind it) and ten majors, most of them gaps where a
crash or stop between two steps leaves money spent and not recorded, or a reservation open and not
visible. Every fold is a plan-text change plus one or two test rows; none changes the design.

## Evidence probed

- **SDK retry and error shape** (`anthropic-sdk-go@v1.80.0`, in the module cache).
  - `internal/requestconfig/requestconfig.go:249-268`: `shouldRetry` returns true whenever there is
    no response ("that indicates that there is a connection error so we retry the request"),
    whatever the method. drafter's own retry by this rule repeats the SDK's hazard.
  - `internal/apierror/apierror.go:24`: `*apierror.Error` carries `Request *http.Request`, which
    includes the `x-api-key` header. `Error()` (line 65) prints only the method, URL, and status,
    and `DumpRequest` (lines 78-80) redacts headers. So the string is safe, but the struct is not.
- **The `anthropic-workspace-id` request header.** The API reference and the SDK
  (`messagebatch.go:850-853`) say: "Only needed for credentials that can act on more than one
  Workspace. A credential that belongs to a specific Workspace may omit it; if sent, it must match
  that Workspace."
- **The batch list endpoint** (platform.claude.com/docs/en/api/messages/batches/list). It says "Most
  recently created batches are returned first", and its only query parameters are `after_id`,
  `before_id`, and `limit`. There is no created-after filter, so `List(since)` must filter on the
  client.
- **`custom_id`** (API reference, create batch): "minLength: 1, maxLength: 64, pattern:
  `^[a-zA-Z0-9_-]{1,64}$`".
- **The batch guide** (platform.claude.com/docs/en/build-with-claude/batch-processing):
  - Results come "when processing has ended for all requests".
  - `errored`, `canceled`, and `expired` requests: "You will not be billed for these requests."
  - "Batch results are available for 29 days after creation".
  - "most batches finishing in less than 1 hour"; batches "can take up to 24 hours".
- **write(2)**: with `O_APPEND`, "the adjustment of the file offset and the write operation are
  performed as an atomic step", but "a successful write() may transfer fewer than count bytes".
  Atomic placement is no guarantee of a whole line, and a crash or power loss can leave a torn tail.
- **flock(2)**: locks belong to the open file description and are released when its last fd
  closes, so a dead process frees the lock. Over NFS they are emulated as `fcntl` locks. Both fit
  a local `state_dir`. A blocking `LOCK_EX` has no timeout.
- **`go help testflag`**: "-timeout d: If a test binary runs longer than duration d, panic." The
  default is 10 minutes.
- **The drafter repo** is public (`gh repo view glw907/drafter`: `PUBLIC`). Pass 1 is unbuilt
  (`internal/plan` only).
- **cairn's docs gate** (`scripts/checks/docs-gate.mjs`) makes no Claude API call, so a gate can't
  spend on another key. Its briefs are tracked (`docs/internal/briefs/**`).

## Findings, ranked by consequence

### 1. Blocker, correctness: an in-client transport retry of `Create` or `Send` can pay twice, outside any reservation

- Location: P2:89, P2:181-182, P2:192-193 (spec "Failures", row 1).
- Defect: after a reset or timeout, the client retries every call inside itself. `Create` and
  `Send` are non-idempotent POSTs, and the Messages API has no idempotency key. A batch the server
  created before the connection dropped runs anyway, and the retry creates a second batch. In the
  same way, a stream cut mid-body has already been billed when it is resent.
  - Neither repeat has an intent, a reservation, or a ledger line, so a cap can be crossed by up
    to 2x a stage, and the spend is unrecorded.
  - P5's resume adoption, the designed remedy for exactly this case, is bypassed because the
    client hides the ambiguity.
- Fold:
  - Retry transport errors inside the client only on idempotent calls (`Get`, `Results`, `List`,
    `CountTokens`, the workspace probe), and on `Create` and `Send` only when the failure is
    provably before the request was written (a dial or DNS error: `*net.DNSError`, or a
    `*net.OpError` with `Op == "dial"`). A 429 with `retry-after` stays retryable everywhere.
  - Any other `Create` failure (a reset after write, a timeout, a 5xx, or an unparseable response)
    returns a new `ErrUnknownOutcome`. P5 treats it as an intent with no batch ID and adopts
    through `List` before it resubmits anything.
  - A `Send` failure after write is a lost response: settle it `estimated` and move to a new
    attempt (see finding 4).
  - Test rows:
    - P2.3: a server that reads the `Create` body and then resets the connection sees exactly one
      `Create`, and the error is `ErrUnknownOutcome`.
    - P5.2: a `Create` that errors after the fake records the batch is adopted, with no second
      `Create`.
  - State the narrowing of the spec's row 1 in the P2 PR body.

### 2. Major, correctness: `custom_id`s as specified overflow the API's 64-character limit

- Location: P5:146 ("custom_ids unique to run, page, stage, and attempt"); P1's `PageKey` (the
  repo-relative path with each `/` as `--`).
- Defect: a run ID such as `20261013T142233Z-7f3a` is 21 characters. A cairn page key such as
  `docs--guides--extend--act-on-newly-published-entries` passes 50. With the stage and attempt
  added, the ID exceeds the documented `maxLength: 64`, and a key with `.` fails the pattern.
  - The whole `Create` then fails with `invalid_request_error`, and every page escalates or the
    run stops, live, on the P5.8 page.
  - Neither plan names a format or tests the limit. The fake API accepts anything.
- Fold: fix the format in P5.2 as `<run-suffix>_<12 hex of sha256(page key)>_<stage>_<attempt>`,
  with the map from ID to page in state. Add a test that every `custom_id` built for the longest
  fixture path matches `^[a-zA-Z0-9_-]{1,64}$`. Make the fake `pipeline.API` reject IDs that
  don't match.

### 3. Major, correctness: resume adoption filters on the local clock against the server's `created_at`, and the API has no such filter

- Location: P2:84-85 (`List(ctx, since)`), P2:181 ("the batch list filter"), P5:152.
- Defect: the intent's timestamp comes from drafter's clock and `created_at` from the server's.
  With the local clock ahead by even a second, the batch drafter created falls before `since`. It
  isn't adopted, so it is created again: double spend.
  - P2.3 also expects a documented "batch list filter" that doesn't exist. The endpoint has only
    the cursor parameters and returns the newest first.
- Fold:
  - `List` pages newest-first and stops at the first batch older than `since` minus a fixed
    margin (10 minutes).
  - Adoption matches only on `custom_id`, which is unique, so the margin can't cause a false
    match.
  - P2.3 records "client-side filter" in place of a doc citation for a filter.
  - Test row: a fake whose server clock lags the intent's timestamp by 30 seconds still adopts.

### 4. Major, correctness: an `estimated` settlement has no defined key, and its resend has no reservation

- Location: P2:101-104 (`Key` is the message ID in sync mode), P2:112, P5:153.
- Defect: a lost sync response has no message ID.
  - An empty `Key` makes "a key already settled is a no-op" collapse every later estimated
    settlement into the first, so spend goes under-recorded.
  - A fresh key on each resume double-counts when a crash comes between the estimate and the
    resend.
  - "Sent once more" names no new `Reserve`, so the resend spends with no cap check.
- Fold:
  - The estimated key is `est/<custom_id>` (the sync intent's ID), so repeated crash and resume
    cycles leave one line per lost attempt.
  - The resend is a new attempt, with a new `custom_id`, a new intent, and a new `Reserve`.
  - Test row: two crash and resume cycles on one sync request leave exactly one `estimated` line
    for the first attempt, and the resend reserved before it went out.

### 5. Major, correctness: the reservation's unit doesn't match the intent's unit

- Location: P2:100 (`Reservation` has one `Intent` and a `Requests` count), P2:110-111, P5:97-98,
  P5:146-147.
- Defect:
  - The spec reserves per stage, but writes one intent per batch and, in sync mode, one intent
    per request.
  - Resubmits (`api_error`, `overloaded_error`, `canceled`, `expired`, the `max_tokens` retry)
    don't say whether they reuse the intent. Reuse overruns `Requests`, so the intent never
    resolves to its settled sum, or resolves early.
  - Errored, canceled, and expired results are unbilled, but nothing says they settle. If they
    don't, the intent stays at `Worst` forever.
- Fold: one `Reserve` per submission unit, meaning one batch or one sync request. Every
  resubmission is a new intent with its own reservation. Every result settles, and unbilled kinds
  settle `actual` at $0, so the intent closes. State this in P2's `Reservation` contract and
  P5.1's stage rule.

### 6. Major, correctness: orphan reservations are invisible and permanent in the cycle

- Location: P2:107-113, P2:208-212 (`drafter spend`), P2:240-241, P5:45-48, P5:271, P5:298.
- Defect: the reservation lives in the ledger and the intent in the run's state, two stores
  written in sequence.
  - A crash between them, or a stopped run that is never resumed, leaves a reserve line that
    counts at `Worst` for the rest of the cycle.
  - `drafter spend` reports only settled and estimated cost, so the meter the session reads
    before each live run can't see open reservations. In the other direction, under the $15
    ceiling a few leaked reservations can wedge every later run, and the visible meter won't say
    why.
- Fold:
  - Write in this order: `Reserve`, then the state intent with the reservation's intent ID, then
    `Create`.
  - `--resume` voids this run's open reservations that have no state intent.
  - `drafter spend` adds an `open` column (the count and the worst-case sum) to the human and
    `--json` output.
  - Every meter check in both plans (P2.5 check 3, P5's standing-approval rule, P5.7, P5.8)
    compares the settled total plus the open total.

### 7. Major, correctness: a stop or rerun can leave billed batches unsettled for good

- Location: P5:149-155, P5:301-303 (fix forward, then rerun), P5:308 (remove the scratch worktree).
- Defect:
  - A resumable stop (`cycle cap`, `spend limit`, a foreign red tree, Ctrl-C) exits with other
    pages' batches in flight. Those finish and bill.
  - P5.8's fix-forward path starts a new run rather than resuming. The close then deletes the
    scratch worktree, and with it the only place a `--resume` can run, since resume requires the
    branch and HEAD.
  - The earlier run's batches are never adopted or settled, so the spend is unrecorded and the
    Console 5% check fails for a reason nobody can trace.
- Fold:
  - Before a rerun or worktree removal, P5.8 requires the earlier run's state to show no open
    intent. It runs `drafter page --resume <id>` to settle, or does the drain the owner fork
    below picks.
  - P5.2 gains a row: a run stopped for `cycle cap` with one batch in flight ends with that batch
    settled (under fork option a) or resumable and settled on resume (under b).

**OWNER FORK: a resumable stop with batches in flight.**

- (a) Drain: submit nothing new, keep polling the in-flight batches until they end, settle them,
  then exit. The cost is wall time, usually under an hour and at worst 24.
- (b) Exit at once and rely on `--resume` to settle. That is fast, but the spend goes unrecorded
  until someone resumes.
- (c) Cancel in-flight batches. Unprocessed requests aren't billed, but finished work is lost and
  processed requests still bill.

Recommendation: (a) for `cycle cap`, `spend limit`, and foreign red; (b) for a signal (Ctrl-C or
SIGTERM).

### 8. Major, correctness: `make smoke` dies at `go test`'s 10-minute default with a batch in flight

- Location: P2:221-232, P5:271-273.
- Defect: the smoke polls a real batch from inside `go test`. A batch that takes longer than 10
  minutes (the docs say most finish in under an hour) makes the binary panic.
  - The reservation stays open and the batch bills. There is no resume path for a test, so the
    spend is never settled.
  - A Go test cache hit can also report a stale `ok` without calling the API.
- Fold:
  - The target runs `go test -tags smoke -count=1 -timeout 2h`.
  - The test writes its batch ID and intents to `state_dir/smoke-<run-id>.json` before polling.
  - A rerun first settles any recorded unsettled smoke batch through the ledger's idempotent
    `Settle`.

### 9. Major, correctness: the ledger line has no time, no version, and no torn-line rule

- Location: P2:99-112, P2:152-153, P2:208-217.
- Defect:
  - `Entry` has no timestamp, yet the cycle total ("every line since `CycleStart`"), `Spend`'s
    window, and P2.4's e2e lines at 23:59 and 00:00 all need one.
  - Lines carry no format version. P5's binary reads lines written by P2's installed binary, and
    a strict decoder breaks on any field P5 adds.
  - A partial write or a crash mid-append (write(2) above) leaves a fragment with no newline, and
    the next append glues onto it. Skipping the bad line silently drops a reservation or
    settlement. Failing on it wedges every run with no message.
  - Nothing is fsynced, so a kernel crash or power loss can drop settle lines for spend that
    already happened.
- Fold:
  - Fix the line schema in P2.2's contract: `{"v":1,"type":"reserve"|"settle","time":<RFC 3339
    UTC>,...}`, with `time` set by the ledger from an injected clock.
  - Decode leniently on unknown fields.
  - Under the lock, before appending, write a `\n` when the file doesn't end in one, so a torn
    fragment stands on its own line.
  - Readers fail closed on any unparseable line except a final unterminated fragment, naming the
    line in the error. `drafter spend` prints the same warning.
  - `File.Sync` after each append.
  - Test rows: a ledger whose last line is torn, which still reserves, and one with a corrupt
    middle line, which refuses and names the line.

### 10. Major, correctness: the key can reach records, logs, child processes, or fixtures in a public repo

- Location: P2:53-58, P2:177-202, P5:112-114, P5:141-145, P5:299-300.
- Defect:
  - The SDK error's `Request` field carries the key header (see "Evidence probed"). A `%+v`, a
    `json.Marshal` of the error into `record.json`, or a `t.Logf("%#v")` in the smoke would write
    it out.
  - Live runs start with `. ~/.local/secrets`, so drafter's environment holds
    `DRAFTER_API_KEY`, `ANTHROPIC_API_KEY`, and every other exported secret. Gate, index-link, and
    seat-input commands inherit all of it, and their output is logged to the run directory and
    inlined into prompts.
  - `key_command` has no timeout, so a hung helper hangs the run.
  - The only planned leak check is `gitleaks` plus an `sk-ant-` grep at close. It covers the diff,
    not runtime artifacts.
- Fold:
  - P2.3 and P5.1 each gain a sentinel row. Run with key `sk-ant-api03-SENTINEL…`, drive every
    error path (a 400, a 500, a reset, a spend limit), then grep every returned error string
    (`%v` and `%+v`), captured stdout and stderr, the run directory, and the ledger for the
    sentinel. Expect no hit.
  - Records save request bodies only, never an `*http.Request` or an SDK error struct.
  - `gate`, index-link, and seat-input commands run with `key_env`'s variable and every
    `ANTHROPIC_*` variable removed from their environment.
  - `key_command` runs under a 30-second context timeout.

### 11. Major, correctness: P5.7 overwrites user config files

- Location: P5:259-269, against P2:237 (P2.5 assumes `~/.config/drafter/config.toml` may already
  exist).
- Defect: "Write `~/.config/drafter/config.toml`" is unconditional. A file Geoff wrote between
  passes (his cycle day, his own prices, a tighter cap) is silently replaced. `cairn-cms.local.toml`
  has the same exposure.
- Fold:
  - When a file exists, keep every value already set and add only the missing keys.
  - Report each conflict by key name, without values, and print no value.
  - Write through an atomic write.
  - Cross-check the price figures against the `claude-api` skill's pricing table. A unit slip
    (per token against per million tokens) makes every cap meaningless, and only the Console
    comparison at PR time would catch it.

### 12. Minor, correctness: P5.8's $10 precheck makes its fix-forward rerun unreachable

- Location: P5:298-303.
- Defect: after the smoke (under $1) and one page (about $3 to $5), the meter sits near $5. Then
  $5 plus the $10 page cap passes $15, so every fault ends in stop-and-notify. The "rerun only
  when the meter allows" branch never fires, and the plan's success path depends on the first run
  being clean.
- Fold: because caps resolve lowest-wins, run with `DRAFTER_PAGE_CAP=<15 − (settled + open)>`
  beside `DRAFTER_CYCLE_CEILING=15`, and make the precheck "settled + open + $1 ≤ $15". The ledger
  then bounds the rerun itself, and an overrun escalates with `cap` instead of spending.

### 13. Minor, correctness: escalation's restore runs outside the write-intent protocol

- Location: P5:108-111, P5:147-148, P5:154-155.
- Defect: the restore to the pre-run snapshot, or the removal of a page drafter created, is a
  worktree write with no pre- and post-write hashes. A crash between restoring the page and
  restoring the brief leaves files at hashes that are "anything else", so resume stops and won't
  continue. That is a dead end, not a loss.
- Fold:
  - Record the restore as a write, and accept the pre-run snapshot hash (or absence) as a valid
    state for an escalating page.
  - Add the mixed case (page at its post-write hash, brief at its pre-write hash) as a resume row.

### 14. Minor, correctness: "uncommitted changes" must include untracked files

- Location: P5:141-142, P5:182.
- Defect: when the dirty check reads only tracked changes, an untracked, non-ignored file at a
  page's path is overwritten on accept. It isn't in git, so it is lost.
- Fold: refuse on any `git status --porcelain` line, and add an e2e row with an untracked file
  that exits 2.

### 15. Minor, correctness: the worst case must count the same request that's sent

- Location: P2:82, P5:97-98.
- Defect: a `CountTokens` built without the schema, the system prompt, or effort under-counts the
  input, so `Worst` sits below real cost and a cap can be crossed by the gap.
- Fold: `CountTokens` takes the identical `Request`. The smoke asserts each result's
  `usage.input_tokens` is at most the counted figure; when it isn't, record the gap and reserve
  with that margin.

### 16. Minor, correctness: an open reservation drops out of the cycle at the reset

- Location: P2:108-111.
- Defect: "every line since `CycleStart`" excludes an intent reserved before the reset and still
  open after it.
- Fold: the cycle total counts every open intent regardless of when it was reserved, and settled
  cost by the settle line's time.

### 17. Minor, correctness: results expire 29 days after creation

- Location: P5:149-153.
- Defect: a resume after 29 days can't fetch results to settle.
- Fold: when `Results` reports the batch archived, settle each `custom_id` at its share of the
  reservation as `estimated`, and add a row.

### 18. Minor, optional: send `anthropic-workspace-id` on every request

- Location: P2:65-67, P2:79-81.
- Defect: the response-header check runs once per run. A key swapped to another workspace
  between a stop and a resume is caught only because resume re-checks. The `Workspace` method
  also needs its own free probe call.
- Fold: add `option.WithHeader("anthropic-workspace-id", workspace_id)` at `New`. Per the API
  reference, a mismatch is then refused by the server on every request. Keep the
  response-header check the spec names as the first-call assertion, and drop the separate probe
  when `CountTokens` always comes first. P2.3 probes the mismatch response's shape through
  `claude-api`. Saves about 10 minutes and one method.

### 19. Minor, optional: `ledger.lock` waits without a bound

- Location: P2:107.
- Defect: a holder that is stopped (SIGSTOP or Ctrl-Z) blocks every other drafter process forever.
- Fold: poll `LOCK_NB` for up to 30 seconds, then fail with an error naming the lock path.

### 20. Minor, optional: dollars as `float64`

- Location: P2:100-105, P2:116-119.
- Defect: sums of float costs compared against a cap drift at the edge, and `--json` totals can
  differ from the human total in the last digit, which P2.4's equality row would then flake on.
- Fold: store integer micro-dollars and format at print time.

### 21. Minor, optional: state the deviation from the spec's lock scope

- Location: P2:107-111.
- Defect: the spec says "every cap check, submission, and append happens under `flock`". P2 holds
  the lock only for the check and the append, which is better because the reservation counts
  before submission and no network call runs under the lock. The difference is unstated.
- Fold: one line in P2.2's outcome and the PR body.

### 22. Minor, optional: an upgrade between stop and resume orphans batches

- Location: P5:75-76, P5:149.
- Defect: P5 bumps `StateSchema`. A run stopped under the old binary is refused by the new one,
  and its in-flight batches are never settled.
- Fold: `docs/configuration.md` or `docs/setup.md` (P5.4) says to finish or resume runs before
  upgrading. Add a "Found, not done" entry for a settle-only resume across schemas.

## Over-ceremony

- **The P2.5 live step is almost surely dead** (P2:236-246; minor, optional; about 10 minutes and
  a PR section). No task writes the user config before P5.7, and the design puts Geoff's key setup
  "before pass 5". The three checks will fail, and the pass records "smoke not yet run", which
  P5.7 already plans for. Fold: keep the offline acceptance, and make the live run a single
  conditional line ("if the key and the user config already exist").
- **Nothing else qualifies.** The test-first commits, per-task `diff-reviewer` reads, and Geoff's
  PR read are his `auth-data` ruling, not ceremony.

## Questions answered

- **A crash between two steps:** findings 1, 4, 6, 7, 8, 13.
- **A concurrent drafter process:** sound for caps. The blocking `flock` around read, check, and
  append serialises reservations across processes, and the two-process re-exec test proves it. A
  stopped holder can wedge others (finding 19).
- **A partial or torn ledger line:** finding 9.
- **A batch that ends while drafter is down:** handled by resume, unless resume never happens
  (finding 7), comes after 29 days (finding 17), or the batch came from the smoke (finding 8).
- **An upgrade between stop and resume:** finding 9 (the ledger format) and finding 22 (state).
- **A key leak:** finding 10.
- **Money spent twice:** findings 1 and 3. **Spent past a cap:** findings 1, 4, and 15.
  **Unrecorded:** findings 1, 6, 7, 8, and 9.
- **A page or brief lost or silently overwritten:** finding 14 (untracked files) and finding 11
  (user config). Tracked pages are safe: the clean-tree refusal means git holds every original.
