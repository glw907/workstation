# drafter pass 2 plan: key and money

Design: `~/.dotfiles/docs/superpowers/specs/2026-10-13-drafter-completion-design.md`, pass 2,
approved by Geoff on 2026-10-13. Geoff ruled this pass `auth-data` ("You can use it."), and ruled
that its live smoke moves to pass 5, since no key exists before then (Technical notes 8). Spec:
`~/.dotfiles/docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, sections "The tool" (the
`key`, `batch`, and `ledger` rows, and `drafter spend`), "Caps", "The ledger", "A server-side
backstop" (read only, for the client's spend-limit handling), "The key", "Caching" (no
`cache_control` is sent), "Concurrency" (the client starts no goroutines), "Failures", and "Testing"
(the Caps and the ledger row, the key row, and the `make smoke` paragraph). Fold record:
`~/.dotfiles/docs/superpowers/research/2026-10-13-drafter-completion-plan-fold.md`.

## Outcome

drafter resolves its API key without ever touching a credential it wasn't told to use, talks to the
Claude API in both modes through one client that never repeats a request that may have been billed,
and keeps a ledger that reserves each submission's worst case before spending and refuses one that
would cross a cap. `drafter spend` reports what the ledger holds, open reservations included. `make
smoke` exists and its assertions run offline against a fake API; its first live run is pass 5's.

## Shape

- Risk class: `auth-data` (Geoff's ruling). Every task is test-first: its tests are written and
  seen failing, then committed, before the code that passes them. `diff-reviewer` at task scope
  reads each task's commit range against its acceptance; a `fix` or `escalate` verdict stops the
  line until it is resolved. Never set `RUN_GATE_IF_BUSY`.
- No `live-account` flag: this pass spends nothing. The PR's brief says so in its first lines: the
  live smoke moved to pass 5 by Geoff's ruling.
- Repo: `~/Projects/drafter` (`glw907/drafter`). The executor launches from the main checkout and
  works in the worktree `EnterWorktree` creates (name `p2-money`); pair subagents get worktrees of
  their own, dispatched on `sonnet` at `medium` with the `description` `p2-money task <n>`.
- Gate, from the worktree root: `DRAFTER_DIR="$PWD" bash ~/.dotfiles/scripts/drafter-gate.sh`.
  Full-suite home: that gate, once, on the close head. No CI.
- Clock file: the pass worktree's git dir.
- Path estimate: 355 minutes. P2.1 and P2.2 as a pair (130), P2.3 and P2.4 as a pair (150), P2.5
  (45), Close (30). The design's estimate is 180, so the path is 2.0 times it, inside the 3x line
  (540).
- Standing approvals (design, "Technical notes"): the plan proceeds within 3x. The PR goes to Geoff
  through the conductor; this pass never merges itself.
- New dependency: `github.com/anthropics/anthropic-sdk-go` at its newest release (v1.80.0 on
  2026-10-13), taken in P2.3 through the `dependency-upgrade` skill's checks. P2.3 also invokes the
  `claude-api` skill before writing the client, since the SDK's batch, token-counting,
  structured-output, and effort surfaces must be read from current documentation, not memory.

## Interfaces

Consumes from pass 1: `config.Config`, `config.Prices`, `config.Price`, `config.Tier`,
`config.Load`, `(*config.Config).Validate` with `config.ScopeMoney`, `atomicfile.WriteFile`,
`run.Repo`, `run.NewID`.

Creates, for passes 4 and 5. Names and purposes are fixed; a signature change that keeps every
caller compiling is allowed and stated in the PR body.

`internal/key`

- `Resolve(c *config.Config) (string, error)`: runs `key_command` through `/bin/sh -c` under a
  30-second timeout when it is set, with its standard error discarded, and returns its trimmed
  standard output; otherwise reads the variable `key_env` names. A nonzero exit, a timeout, empty
  output, output holding inner whitespace, or an unset or empty variable is an error naming the
  source, and no error text ever carries what the command printed.

`internal/batch` (the API seam; pass 5's `pipeline` declares a consumer-side interface with exactly
these `*Client` methods, and its tests fake it)

- `type Options struct`: `Key`, `BaseURL`, `WorkspaceID string`; `RequestTimeout` (each unary call),
  `StreamTimeout` (a whole `Send` stream or `Results` download), and `WallTime time.Duration` (the
  bound on in-place retries). `WithRequestTimeout` covers the body read too
  (`internal/requestconfig/requestconfig.go:546-563, 630-638` in v1.80.0), so the client passes the
  right one per call.
- `New(o Options) *Client`: built with `option.WithoutEnvironmentDefaults()`,
  `option.WithAPIKey`, `option.WithBaseURL`, `option.WithMaxRetries(0)`, and
  `option.WithHeader("anthropic-workspace-id", o.WorkspaceID)`, so every request names the
  workspace. The API reference: "A credential that belongs to a specific Workspace may omit it; if
  sent, it must match that Workspace" (batches create page, read 2026-10-13).
- `type Message struct`: `Role` (`user` or `assistant`), `Text string`.
- `type Request struct`: `CustomID`, `Model`, `System string`, `Messages []Message`, `MaxTokens
  int64`, `Effort string`, `Schema json.RawMessage` (the answer's JSON Schema; the client decodes it
  into the SDK's `map[string]any` for the request's structured-output format).
- `type Usage struct`: `InputTokens`, `OutputTokens`, `CacheWrite5m`, `CacheWrite1h`, `CacheRead
  int64`.
- `type Result struct`: `CustomID`, `MessageID`, `Kind` (`succeeded`, `errored`, `canceled`, or
  `expired`), `StopReason`, `Text`, `ErrType`, `ErrMessage string`, `Usage Usage`. A sync-mode HTTP
  400, 500, or 529 comes back as an `errored` result with the matching `ErrType`, so both modes
  classify the same way. A spend-limit 400 or 429 is `ErrSpendLimit` on every call, checked before
  that mapping.
- `type Batch struct`: `ID string`, `Ended bool`, `CreatedAt time.Time`.
- `(*Client) CheckWorkspace(ctx) error`: one `GET /v1/models?limit=1` (free) whose
  `anthropic-workspace-id` response header must equal `Options.WorkspaceID`; an absent header is a
  mismatch (the API overview: absent only when the credential resolves to no workspace or
  authentication failed). The error names both IDs. `CountTokens`, `Create`, and `Send` return
  `ErrNoWorkspaceCheck` and send nothing until it has passed.
- `(*Client) CountTokens(ctx, Request) (int64, error)`: counts the identical request, system prompt,
  schema, and effort included, so a worst case never undercounts what is sent.
- `(*Client) Create(ctx, []Request) (Batch, error)`, `Get(ctx, id string) (Batch, error)`,
  `Results(ctx, id string) ([]Result, error)`, and `List(ctx, since time.Time) ([]Batch, error)`. The
  list endpoint takes only `after_id`, `before_id`, and `limit` and returns the newest first
  (`messagebatch.go:857-867`; the batches list page), so `List` filters on the client: it pages until
  a page's oldest batch was created more than 10 minutes before `since`, and returns every batch
  created at or after `since` minus that margin. The margin absorbs a local clock ahead of the
  server's; resume adopts only by `custom_id`, so it can't cause a false match.
- `(*Client) Send(ctx, Request) (Result, error)`: one streamed Messages call.
- Retries inside the client, with backoff bounded by `WallTime`: the idempotent calls
  (`CountTokens`, `Get`, `Results`, `List`, and the models probe) retry a transport error, a 429
  with `retry-after`, a bare 429, a 500, and a 529. `Create` and `Send` retry only a failure that
  provably came before the request was written (a DNS error, or a `*net.OpError` whose `Op` is
  `dial`) and a 429 that isn't a spend limit. Nothing else retries inside the client.
- `ErrMaybeSent`: the request may have reached the API and its outcome is unknown. `Create` returns
  it for a failure after the request was written (a reset, a timeout, a 500 or 529, an unparseable
  response); pass 5 adopts through `List` before it resubmits anything. `Send` returns it when the
  response is lost after the request was written (a reset or timeout mid-stream, or an SSE `error`
  event after the 200, whose type the error keeps); pass 5 settles that attempt `estimated` and
  resubmits it as a new attempt.
- `ErrTransport`: in-place retries outlasted `WallTime`, or a `retry-after` is longer than the
  `WallTime` left, which returns at once without sleeping.
- `ErrSpendLimit`: a 429 whose `error.details.error_code` is `enforced_spend_limit_reached`, read
  from `(*anthropic.Error).RawJSON()`, or a 400 whose message begins `You have reached your
  specified` (the organization and the workspace wordings both; rate-limits page, "Reaching your
  spend cap" and "Setting your own spend limit", read 2026-10-13). The API's message is kept.
- `ErrNoWorkspaceCheck`.
- Errors carry the status, error type, and message only, never an SDK error struct, whose `Request`
  field holds the key header (`internal/apierror/apierror.go:24`).
- `type Action int`, with the zero value `ActionInvalid`, never accept, and `ActionAccept`,
  `ActionResubmit` (`api_error`, `overloaded_error`), `ActionResubmitThenStop` (`canceled`,
  `expired`), `ActionEscalate` (`invalid_request_error`, and every `ErrType` not named here,
  `billing_error` and an empty type included), `ActionRetryAnswer` (`stop_reason` `max_tokens` or
  `model_context_window_exceeded`; a parse or schema failure, which only the caller sees, takes the
  same action), `ActionRefusal` (`stop_reason` `refusal`), and `ActionSpendLimit` (an `errored`
  result whose message begins with either spend-limit wording). Any other stop reason but
  `end_turn` escalates. `Classify(Result) Action`.

`internal/ledger`

- Each line is one JSON object: `v` (1), `type` (`reserve` or `settle`), `time` (RFC 3339 UTC,
  stamped by the ledger under the lock), the `Entry` fields, and the reservation's or settlement's
  own. Readers ignore unknown fields.
- `type Entry struct`: `RunID`, `Repo`, `Page`, `Seat`, `Model`, `Mode string`.
- `type Reservation struct`: `Entry`, `Intent string`, `Requests int`, `Worst float64`. One
  reservation covers one submission unit: one batch (a stage in `batch` mode) or one sync request.
  Every resubmission is a new intent with a reservation of its own.
- `type Settlement struct`: `Entry`, `Intent`, `Key string`, `Usage batch.Usage`, `Cost float64`,
  `Kind string`: `actual`; `estimated` (a sync request whose response was lost, at its share of the
  reservation, `Worst / Requests`); or `void` (an intent the API never billed: it never reached
  the API, or the API refused it; at zero, one line closing the whole intent). The key is `<batch-id>/<custom_id>` in `batch` mode. An `actual` sync
  settlement keys on its message ID; an `estimated` one always keys `<intent>/<custom_id>`, whatever
  arrived, so a settle made in the run and repeated on resume is the same line; a `void` one keys
  `<intent>/void`. `custom_id`s are unique per request and attempt (pass 5), so no two settlements
  share a key. Unbilled results
  (`errored`, `canceled`, `expired`; the batch guide: "You will not be billed for these requests")
  settle `actual` at zero, so their intent closes.
- `type Caps struct`: `Page`, `Cycle float64`, `CycleStart time.Time`.
- `Open(stateDir string) *Ledger`: `ledger.jsonl` and `ledger.lock` in `stateDir`. `Ledger.Now`
  (default `time.Now`) stamps each line, so tests inject a clock.
- `(*Ledger) Reserve(r Reservation, c Caps) error`: under a blocking `flock` on `ledger.lock`,
  checks the page total (run ID and page) and the cycle total and appends the reserve line, or
  returns `ErrPageCap` or `ErrCycleCap` and appends nothing. A total plus `Worst` equal to a cap
  passes; above it is refused. An intent counts at its `Worst` until its settled lines reach
  `Requests` (or a `void` line), then at its settled sum. The cycle total is settled cost whose
  settle line's `time` is at or after `CycleStart`, plus every open intent whenever it was reserved.
  The lock is held for the check and the append only, never across a network call; the reserve line
  counts before the submission it covers, so two processes still can't both pass a cap. The spec's
  "Every cap check, submission, and append happens under `flock`" is narrowed by this (owed
  erratum).
- `(*Ledger) Settle(s Settlement) error`: appends under the lock; a key already settled is a no-op;
  an empty `Key` is an error.
- `(*Ledger) OpenIntents(runID string) ([]Reservation, error)`: the run's reservations not yet
  closed, for pass 5's resume.
- `(*Ledger) Spend(since, until time.Time) (Report, error)`: `Report` holds `Rows` (`Repo`, `Seat`,
  `Cost`, `Requests`, and `Estimated`, the count of estimated lines), `Total`, and `Open` (the count
  of open intents and the sum of their `Worst`).
- `(*Ledger) PageSpend(runID, page string) (float64, error)`: settled plus open.
- File states: an absent or empty ledger reads as zero. The first append creates `state_dir` (0700)
  and the ledger (0600). Each line is one `write` on an `O_APPEND` descriptor, then `File.Sync`. A
  final line with no newline (a torn write) is skipped with a warning naming it, and the next
  append writes a newline first. Any other line that doesn't parse is an error naming the file and
  line, so `Reserve`, `Settle`, and `Spend` fail closed.
- `Cost(p config.Prices, model string, u batch.Usage, batchMode bool) (float64, error)` and
  `Worst(p config.Prices, model string, inputTokens, maxTokens int64, batchMode bool) (float64,
  error)`: the price table applied; the long-context tier when total input (input, cache-read, and
  cache-write tokens) is over its threshold, its rates replacing all five; and every rate times
  `1 - BatchDiscount` in batch mode only (the pricing page: the batch discount covers input and
  output, and the cache multipliers "stack with other pricing modifiers, including the Batch API
  discount"). A model with no entry is an error, never a zero.
- `CycleStart(now time.Time, day int) time.Time`: 00:00 UTC on the most recent `day`, or a short
  month's last day when `day` passes its end.

## Out of scope

Request assembly and the answer schemas production uses (pass 4), the pipeline's intents, resume,
and poll loop (pass 5), every live API call (pass 5), prompt caching (the spec's "Caching"), and the
key's storage on any machine.

## Tasks

Every task starts by invoking `go-conventions`, writes its tests first, and commits them failing
before the code. Each commit range gets a task-scope `diff-reviewer` read while the next task runs;
a pair's two ranges are read after the merge. Every test that touches the key clears
`DRAFTER_API_KEY` and every `ANTHROPIC_*` variable first, and sets `key_env` to a variable unique to
the test.

### P2.1 The key (45 min, auth-data)

- Outcome: `internal/key` as listed above.
- Files: `internal/key/` with tests.
- Acceptance, the spec's key row, minus the workspace case (P2.3 and pass 5):
  - With only `ANTHROPIC_API_KEY` set, and with only an OAuth variable set
    (`CLAUDE_CODE_OAUTH_TOKEN` and `ANTHROPIC_AUTH_TOKEN`, one row each), `Resolve` refuses, and the
    error names `key_env`'s variable as unset.
  - `key_env`'s variable unset, and set to the empty string, are separate rows, each refused.
  - `key_env` naming another variable reads that variable.
  - `key_command` wins when the variable is also set.
  - A `key_command` that writes a sentinel string to both standard output and standard error and
    exits 1, one that prints only whitespace, one that prints two words, and one that sleeps past
    the timeout each refuse; neither the error's text nor the test process's captured standard
    error holds the sentinel.
- Test: the gate.
- Pair: with P2.2.

### P2.2 The ledger (130 min, auth-data)

- Outcome: `internal/ledger` as listed above.
- Files: `internal/ledger/` with tests and synthetic price tables in `testdata/`, and
  `internal/batch/usage.go` holding only `batch.Usage`, which the ledger's settlements carry. P2.3
  builds the rest of `internal/batch` around that file.
- Acceptance, the spec's Caps and the ledger row, each negative row with a clean twin:
  - A reservation whose input fits under the page cap but whose input plus `max_tokens` at the
    output price doesn't is refused with `ErrPageCap`, through `Worst` and `Reserve`.
  - A total exactly at the page cap passes; a quarter-dollar over is refused (amounts exactly
    representable in binary, so the row can't flake).
  - Several in-flight pages whose open reservations together cross the ceiling: the reservation
    that would cross it gets `ErrCycleCap`; the ones before it pass.
  - Two processes against one ledger: the test re-executes its own binary as a child (`os.Args[0]`
    with a test filter and an environment flag). `Reserve` calls an unexported hook between its
    check and its append, nil in production; each child sets it to touch `ready-<n>` and wait up to
    500 ms for its peer's file, then continue. Under the lock the second child blocks in `flock`,
    never reaches its hook, and is refused after the first appends; exactly one succeeds. With the
    lock call replaced by a no-op, both succeed and the test fails: seen once as a temporary local
    edit, and recorded in the task's commit message.
  - A settle applied twice leaves one line and one cost; `Settle` with an empty `Key` errors.
  - Two requests of one batch intent, each `errored` and keyed `<batch-id>/<custom_id>`, leave two
    lines, and the intent drops to its settled sum; an `estimated` sync settlement whose stream
    carried a message ID keys `<intent>/<custom_id>`, and settling it again after a resume is a
    no-op; an `estimated` and a `void` settlement each
    count once as written; an `errored` result settled at zero closes its intent.
  - An intent counts at its worst case until its last request settles, then at its settled sum.
  - An intent reserved before `CycleStart` and still open counts in the new cycle; a settle line
    before `CycleStart` doesn't.
  - `CycleStart` with `day` 31: `now` 2028-03-10 gives 2028-02-29 00:00 UTC; 2027-03-10 gives
    2027-02-28; 2027-02-15 gives 2027-01-31; 2027-02-28 00:00 exactly gives 2027-02-28; one
    nanosecond earlier gives 2027-01-31.
  - Cost rows, each against a figure computed by hand in the test's comment: a one-hour cache write;
    a Haiku-shaped request at exactly 100,000 total input tokens (standard rates) and at 100,001
    counting cache tokens (every rate from the tier, output included); the same usage in batch and
    sync mode.
  - A model with no price entry is an error from `Cost` and `Worst`.
  - `PageSpend` after a resumed run's earlier lines carries the earlier spend.
  - `OpenIntents` lists a run's unclosed reservations and no other run's.
  - File states: an absent and an empty ledger read as zero; the first append creates the directory
    at 0700; a ledger whose last line is torn still reserves, and the file then has the fragment on
    its own line; a corrupt middle line makes `Reserve`, `Settle`, and `Spend` fail naming the line;
    a line with an unknown field reads.
  - Every line carries `v`, `type`, and a `time` from the injected clock.
- Test: the gate.
- Pair: with P2.1.

### P2.3 The API client (150 min, auth-data)

- Outcome: `internal/batch` as listed above. Invoke `claude-api` first and record in the PR body
  where the SDK and the API docs state the workspace header, the token-counting call, the batch
  list's cursor parameters (a client-side filter, since the API has none by date), structured
  outputs, effort, and the spend-limit shapes. No method starts a goroutine.
- Files: `internal/batch/` with tests, `go.mod`, `go.sum`.
- Acceptance, against an `httptest` server reached through `BaseURL`, with every response
  synthetic and the backoff clock injected so retry rows run in milliseconds:
  - Credentials: one row per variable set alone to a sentinel (`ANTHROPIC_API_KEY`,
    `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_PROFILE` naming a missing profile,
    `ANTHROPIC_CUSTOM_HEADERS`). Each request reaches the test server, `X-Api-Key` equals the
    `Options` key, no `Authorization` header is present, and no header value holds the sentinel.
    Deleting `option.WithoutEnvironmentDefaults()` from `New` fails the `ANTHROPIC_AUTH_TOKEN` row:
    seen once, recorded in the commit message.
  - Workspace: `CountTokens`, `Create`, and `Send` before `CheckWorkspace` return
    `ErrNoWorkspaceCheck` and the server sees nothing; `CheckWorkspace` makes exactly one models
    call; a mismatched header, and an absent one, each fail naming both IDs, and a `Create` after
    the failed check still sends nothing; every request carries `anthropic-workspace-id` equal to
    `Options.WorkspaceID`.
  - The SDK's own retries are off: a 500 on `Create` is one request, and returns `ErrMaybeSent`.
  - In-place retries: a `Get` reset then success (at least 2 server hits); resets past `WallTime`
    (`ErrTransport`); a `retry-after` longer than the `WallTime` left (`ErrTransport` at once); a 429
    with `retry-after`, then success; a bare 429 on `Get`, retried; a 500 and a 529 on `Get`,
    `Results`, and `List`, retried; a `Create` to a closed port, retried as a dial failure.
  - Maybe sent: a server that reads the whole `Create` body and resets the connection sees exactly
    one `Create`, and the error is `ErrMaybeSent`; a `Send` reset mid-stream returns `ErrMaybeSent`
    after one server hit; an SSE `error` event (`overloaded_error`) after the 200 returns
    `ErrMaybeSent` carrying that type.
  - Spend limits: a 429 with `details.error_code` `enforced_spend_limit_reached` and no
    `retry-after` is `ErrSpendLimit` after one hit, message kept; the 400s beginning `You have
    reached your specified API usage limits` and `You have reached your specified workspace API
    usage limits` are each `ErrSpendLimit`, on `Create` and on `Send` alike (never an `errored`
    result); an `errored` batch result with either message is `ActionSpendLimit`.
  - Classify, one row per action: `errored` with `api_error`, `overloaded_error`,
    `invalid_request_error`, `billing_error`, and an empty type; `canceled`; `expired`;
    `stop_reason` `max_tokens`, `model_context_window_exceeded`, `refusal`, `pause_turn`, and
    `end_turn`; sync HTTP 500, 529, and 400 (each an `errored` result classified like its batch
    twin). No input yields `ActionInvalid` except a zero `Result`.
  - Timeouts: a stream slower than `RequestTimeout` but within `StreamTimeout` completes; a unary
    call past `RequestTimeout` fails.
  - A batch round trip: `Create`, `Get` until ended, `Results` returning the usage block per
    `custom_id`.
  - `List`: the fake ignores every filter parameter and serves newest first across at least three
    pages (`limit` 2, a `has_more` and `last_id` chain), with batches on both sides of `since`, one
    exactly at it, and one whose `created_at` lags `since` by 30 seconds. `List` returns exactly the
    batches within the margin, the lagging one included, and stops paging once a page's oldest batch
    predates the margin (the fake counts page requests).
  - `Send` streams and returns the message ID, text, stop reason, and usage.
  - `Request.Schema` and `Effort` reach the wire in the form the docs give, and `CountTokens` sends
    the same system prompt, schema, and effort as `Create` for one request.
  - Error text: with the key a sentinel, every error from a 400, a 500, a reset, and a spend limit
    holds no sentinel under `%v` or `%+v`.
  - The SDK is at its newest release, with the `dependency-upgrade` check in the PR body.
- Test: the gate.
- Pair: with P2.4.

### P2.4 `drafter spend` (45 min, auth-data)

- Outcome: `drafter spend [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--json]` loads the
  configuration (the user layer, plus the project's layers when the git top level holds a
  `drafter.toml`; it calls no `Validate`), reads the ledger in `state_dir`, and prints cost by repo
  and seat with a total, for the current billing cycle by default or for the UTC dates given
  (`--until` inclusive). Estimated lines are counted and marked. Open reservations are a line of
  their own (count and worst-case sum), never in the cost. `--json` prints one object: `rows`
  (`repo`, `seat`, `cost`, `requests`, `estimated`), `total`, and `open` (`count`, `worst`).
- Files: `cmd/drafter/spend.go`, `cmd/drafter/root.go`, `e2e/e2e_test.go`, `e2e/testdata/`.
- Acceptance: e2e rows on a synthetic ledger under a temp `state_dir` (set through a temp user
  config): two repos by two seats with hand-computed rows; one estimated line shown with its mark and
  `estimated: 1` in JSON; one reserve line with no settle, out of the cost and in `open`; the
  default window, with fixture lines written relative to `ledger.CycleStart(time.Now(), day)`, one
  just before and one just after; a `--since`/`--until` window that includes a line at 23:59 UTC on
  `--until` and excludes one at 00:00 the next day; `--json` sums equal the human total; a missing
  ledger prints a zero total and exits 0; a corrupt middle line exits 1 naming it.
- Test: the gate.
- Pair: with P2.3.

### P2.5 `make smoke` (45 min, auth-data)

- Outcome: the smoke's body lives in `internal/smoke`, untagged: given `batch.Options`, a state
  directory, and a shape table, it checks the workspace, reserves and submits one batch holding one
  request per seat shape plus one sync request, polls to the end, settles every result through the
  real ledger under repo `drafter-smoke`, and returns what it saw. A seat shape is a seat's answer
  schema (every object with `additionalProperties: false`), effort, system prompt, and a
  `max_tokens` of 4096, since Haiku 5.5's thinking counts toward `max_tokens`. Until pass 4 builds
  the production schemas, the table holds one synthetic shape per seat (the seven of pass 1); pass 5
  points it at the production builders. Before polling it writes the batch ID and its intents to
  `<state_dir>/smoke/<run-id>.json` (through `atomicfile`); a later smoke first settles any batch
  recorded there and not yet settled, through `Results` and the ledger's idempotent `Settle`, and
  voids recorded intents that never reached the API. The `smoke` target runs `go test -tags smoke
  -count=1 -timeout 2h -run Live ./internal/smoke/`, kept out of `check`; the tagged test loads the
  user configuration, runs `Validate(ScopeMoney)`, resolves the key, and calls the body on Haiku 5.5
  (the model ID from `claude-api`'s model table, the price from the user config).
- Files: `internal/smoke/` (the body, its untagged test against an `httptest` fake, and the tagged
  live test), `Makefile`, `CLAUDE.md` (one line naming the target and that it spends money).
- Acceptance, offline, in the gate against the fake: the shape table holds exactly the seven seats;
  each result parses to its schema; the ledger gains `len(shapes) + 1` settle lines, not zero; each
  line's recorded usage equals the fake's usage block field for field and its cost is above zero;
  each result's `input_tokens` is at most its counted figure; the batch's seven `custom_id`s are
  distinct, and the fake rejects a `Create` whose `custom_id`s repeat, as the API does
  (`messagebatch.go:346`: "Must be unique for each request within the Message Batch"); a recorded, unsettled smoke batch is
  settled by the next run, once. `go vet -tags smoke ./...` passes.
- Test: the gate.

### Close (30 min)

The gate, once, on the close head. One whole-branch `diff-reviewer` run against `main`, with
go-conventions for `*.go`; it re-derives each task's class and confirms each task-scope verdict is
recorded. One batched fix chain if needed, each fix quoting its finding verbatim, then the gate
again, and a second review only on a blocker. `gitleaks git` over the branch history, plus a check
that no fixture, test, or log in the diff holds anything shaped like an `sk-ant-` key.

Push the branch to `glw907/drafter` and open the PR. The body opens with `## Brief`, whose first
lines say the live smoke moved to pass 5 by Geoff's ruling and this pass spent nothing. Then what
landed, each task's `diff-reviewer` verdict, the `claude-api` sources from P2.3, the spec departures
(the transport-retry narrowing, the lock scope, the sync settle key, and the reservation unit, each
an owed erratum in the fold record), the score rows (gate time from
`~/.local/state/cairn-run-gate/runs.jsonl` records whose `gate` names this worktree; the Work and
review row puts the 355-minute path beside the actual), and "Found, not done" with a proposed
disposition each. It notes for the merger: after the merge, `make -C ~/Projects/drafter install`.
Stop at PR-ready; the conductor takes it to Geoff.

## Later

- A `drafter spend --by page` breakdown for the pilot's per-page cost criterion, if reading the
  ledger lines by hand proves slow.
- A bounded wait on `ledger.lock`, if a stopped holder ever wedges a run.
