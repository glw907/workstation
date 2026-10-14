# drafter pass 2 plan: key and money

Design: `docs/superpowers/specs/2026-10-13-drafter-completion-design.md`, pass 2, approved by Geoff
on 2026-10-13. Geoff ruled this pass `auth-data` ("You can use it."). Spec:
`docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, sections "The tool" (the `key`,
`batch`, and `ledger` rows, and `drafter spend`), "Caps", "The ledger", "A server-side backstop"
(read only, for the client's spend-limit handling), "The key", "Caching" (no `cache_control` is
sent), "Concurrency" (the client starts no goroutines), "Failures", and "Testing" (the Caps and the
ledger row, the key row, and the `make smoke` paragraph).

## Outcome

drafter resolves its API key without ever touching a credential it wasn't told to use, talks to the
Claude API in both modes through one client that retries only by the spec's failures table, and
keeps a ledger that reserves each stage's worst case before spending and refuses a stage that would
cross a cap. `drafter spend` reports what the ledger holds. `make smoke` proves the whole money path
against the real API for under a dollar.

## Shape

- Risk class: `auth-data` (Geoff's ruling). Every task is test-first: its tests are written and
  seen failing, then committed, before the code that passes them. `diff-reviewer` at task scope
  reads each task's commit range against its acceptance; a `fix` or `escalate` verdict stops the
  line until it is resolved. Never set `RUN_GATE_IF_BUSY`.
- `live-account` flag: yes. P2.5's live smoke run spends real API credit, inside the initiative's
  $15 standing approval.
- Repo: `~/Projects/drafter` (`glw907/drafter`). The executor launches from the main checkout and
  works in the worktree `EnterWorktree` creates (name `p2-money`); pair subagents get worktrees of
  their own.
- Gate, from the worktree root: `DRAFTER_DIR="$PWD" bash ~/.dotfiles/scripts/drafter-gate.sh`.
  Full-suite home: that gate, once, on the close head. No CI.
- Clock file: the pass worktree's git dir.
- Path estimate: 285 minutes. P2.1 and P2.2 as a pair (100), P2.3 and P2.4 as a pair (110), P2.5
  (45), Close (30). The design's estimate is 180, so the path is 1.6 times it, inside the 3x line
  (540).
- Standing approvals (design, "Technical notes"): the plan proceeds within 3x; live spend up to $15
  across the initiative runs without asking, and a run whose next live request could take the
  initiative's ledger total past $15 stops and notifies. The PR goes to Geoff through the
  conductor; this pass never merges itself.
- New dependency: `github.com/anthropics/anthropic-sdk-go` at its newest release, taken in P2.3
  through the `dependency-upgrade` skill's checks. P2.3 also invokes the `claude-api` skill before
  writing the client, since the SDK's batch, token-counting, structured-output, and effort surfaces
  must be read from current documentation, not memory.

## Interfaces

Consumes from pass 1: `config.Config`, `config.Prices`, `config.Price`, `config.Tier`,
`config.Load`, `(*config.Config).Validate`, `atomicfile.WriteFile`, `run.Repo`.

Creates, for passes 4 and 5. Names and purposes are fixed; a signature change that keeps every
caller compiling is allowed and stated in the PR body.

`internal/key`

- `Resolve(c *config.Config) (string, error)`: runs `key_command` through `/bin/sh -c` when it is
  set and returns its trimmed standard output; otherwise reads the variable `key_env` names. A
  nonzero exit, empty output, or an empty or unset variable is an error, and no error text ever
  carries what the command printed.

`internal/batch` (the API seam; pass 5's `pipeline` declares a consumer-side interface with exactly
these `*Client` methods, and its tests fake it)

- `type Options struct`: `Key`, `BaseURL string`, `RequestTimeout`, `WallTime time.Duration`
  (the bound on transport retries).
- `New(o Options) *Client`: built with `option.WithoutEnvironmentDefaults()`,
  `option.WithAPIKey`, `option.WithBaseURL`, `option.WithRequestTimeout`, and
  `option.WithMaxRetries(0)`.
- `type Message struct`: `Role` (`user` or `assistant`), `Text string`.
- `type Request struct`: `CustomID`, `Model`, `System string`, `Messages []Message`, `MaxTokens
  int64`, `Effort string`, `Schema json.RawMessage` (the answer's JSON Schema, sent as the
  request's structured-output format).
- `type Usage struct`: `InputTokens`, `OutputTokens`, `CacheWrite5m`, `CacheWrite1h`, `CacheRead
  int64`.
- `type Result struct`: `CustomID`, `MessageID`, `Kind` (`succeeded`, `errored`, `canceled`, or
  `expired`), `StopReason`, `Text`, `ErrType`, `ErrMessage string`, `Usage Usage`. A sync-mode HTTP
  400, 500, or 529 comes back as an `errored` result with the matching `ErrType`, so both modes
  classify the same way.
- `type Batch struct`: `ID string`, `Ended bool`, `CreatedAt time.Time`.
- `(*Client) Workspace(ctx) (string, error)`: the `anthropic-workspace-id` of the first response
  this client received, making one free call when none has arrived yet.
- `(*Client) CheckWorkspace(ctx, want string) error`: an error naming both IDs when they differ.
- `(*Client) CountTokens(ctx, Request) (int64, error)`.
- `(*Client) Create(ctx, []Request) (Batch, error)`, `Get(ctx, id string) (Batch, error)`,
  `Results(ctx, id string) ([]Result, error)`, `List(ctx, since time.Time) ([]Batch, error)`
  (the workspace's batches created after `since`, for resume's adoption).
- `(*Client) Send(ctx, Request) (Result, error)`: one streamed Messages call.
- `ErrSpendLimit`: wrapped by any method's error on a 429 `enforced_spend_limit_reached` or a 400
  "You have reached your specified workspace API usage limits", with the API's message kept.
- `ErrTransport`: wrapped when transport errors or 429s with `retry-after` outlast `WallTime`.
- `type Action int` and `Classify(Result) Action`: one action per failures-table row that a result
  can reach: accept; resubmit once (`api_error`, `overloaded_error`); resubmit once, then stop as
  infrastructure (`canceled`, `expired`); escalate with the error (`invalid_request_error`); refuse
  the answer and retry once (`stop_reason` `max_tokens`); escalate with the refusal (`stop_reason`
  `refusal`). A parse or schema failure, which only the caller can see, takes the same action as
  `max_tokens`.

`internal/ledger`

- `type Entry struct`: `RunID`, `Repo`, `Page`, `Seat`, `Model`, `Mode string`, on every line.
- `type Reservation struct`: `Entry`, `Intent string`, `Requests int`, `Worst float64`.
- `type Settlement struct`: `Entry`, `Intent`, `Key string` (`<batch-id>/<custom_id>` in batch mode,
  the message ID in sync mode), `Usage batch.Usage`, `Cost float64`, `Kind string` (`actual`;
  `estimated`, a sync request whose response was lost, settled at its share of the reservation; or
  `void`, an intent that never reached the API, settled at zero).
- `type Caps struct`: `Page`, `Cycle float64`, `CycleStart time.Time`.
- `Open(stateDir string) *Ledger`: `ledger.jsonl` and `ledger.lock` in `stateDir`.
- `(*Ledger) Reserve(r Reservation, c Caps) error`: under a blocking `flock` on `ledger.lock`,
  checks the page total (run ID and page) and the cycle total (every line since `CycleStart`) and
  appends the reserve line, or returns `ErrPageCap` or `ErrCycleCap` and appends nothing. An
  intent counts at its `Worst` until every one of its requests has settled, then at its settled
  sum.
- `(*Ledger) Settle(s Settlement) error`: appends under the lock; a key already settled is a no-op.
- `(*Ledger) Spend(since, until time.Time) ([]Row, error)`: `Row` holds `Repo`, `Seat`, `Cost`,
  `Requests`, and `Estimated` (the count of estimated lines).
- `(*Ledger) PageSpend(runID, page string) (float64, error)`.
- `Cost(p config.Prices, model string, u batch.Usage, batchMode bool) (float64, error)` and
  `Worst(p config.Prices, model string, inputTokens, maxTokens int64, batchMode bool) (float64,
  error)`: the price table applied, the long-context tier when input passes its threshold, and the
  batch discount only in batch mode. A model with no entry is an error, never a zero.
- `CycleStart(now time.Time, day int) time.Time`: 00:00 UTC on the most recent `day`, or a short
  month's last day when `day` passes its end.

## Out of scope

Request assembly and the answer schemas production uses (pass 4), the pipeline's intents, resume,
and poll loop (pass 5), prompt caching (the spec's "Caching"), and the key's storage on any machine.

## Tasks

Every task starts by invoking `go-conventions`, writes its tests first, and commits them failing
before the code. Each commit range gets a task-scope `diff-reviewer` read while the next task runs;
a pair's two ranges are read after the merge.

### P2.1 The key (40 min, auth-data)

- Outcome: `internal/key` as listed above.
- Files: `internal/key/` with tests.
- Acceptance, the spec's key row, minus the workspace case (P2.3's):
  - With only `ANTHROPIC_API_KEY` set, and with only an OAuth variable set
    (`CLAUDE_CODE_OAUTH_TOKEN` and `ANTHROPIC_AUTH_TOKEN`, one row each), `Resolve` refuses, and the
    error names `key_env`'s variable as unset.
  - `key_env` naming another variable reads that variable.
  - `key_command` wins when the variable is also set.
  - A `key_command` that prints a sentinel string and exits 1, and one that prints only whitespace,
    each refuse, and neither error's text contains the sentinel.
  - The command runs through `/bin/sh -c` with its standard error discarded from every message.
- Test: the gate.
- Pair: with P2.2.

### P2.2 The ledger (100 min, auth-data)

- Outcome: `internal/ledger` as listed above, with one JSON object per line and `flock` around
  every read-check-append.
- Files: `internal/ledger/` with tests and synthetic price tables in `testdata/`, and
  `internal/batch/usage.go` holding only `batch.Usage`, which the ledger's settlements carry. P2.3
  builds the rest of `internal/batch` around that file.
- Acceptance, the spec's Caps and the ledger row, each negative row with a clean twin:
  - A stage whose input fits under the page cap but whose input plus `max_tokens` at the output
    price doesn't is refused with `ErrPageCap`, through `Worst` and `Reserve`.
  - Several in-flight pages whose open reservations together cross the ceiling: the reservation
    that would cross it gets `ErrCycleCap`; the ones before it pass.
  - Two processes against one ledger: the test re-executes its own binary as a child
    (`os.Args[0]` with a test filter and an environment flag) so two real processes race to
    reserve a sum only one may hold; exactly one succeeds.
  - A settle applied twice leaves one line and one cost.
  - `CycleStart` at the exact reset instant (the new cycle), one nanosecond before it (the old
    cycle), and with `day` 31 in February of a leap and a common year.
  - A cost row for a one-hour cache write and one for a request over the long-context threshold,
    each checked against a figure computed by hand in the test's comment.
  - A model with no price entry is an error from `Cost` and `Worst`.
  - An intent counts at its worst case until its last request settles, then at its settled sum;
    an `estimated` and a `void` settlement each count as written.
  - `PageSpend` after a resumed run's earlier lines carries the earlier spend.
- Test: the gate.
- Pair: with P2.1.

### P2.3 The API client (110 min, auth-data)

- Outcome: `internal/batch` as listed above. Invoke `claude-api` first and record in the PR body
  where the SDK and the API docs state the workspace header, the token-counting call, the batch
  list filter, structured outputs, and effort. A transport error and a 429 with `retry-after`
  retry inside the client, with backoff bounded by `WallTime`; nothing else retries inside it.
  No method starts a goroutine.
- Files: `internal/batch/` with tests, `go.mod`, `go.sum`.
- Acceptance, against an `httptest` server reached through `BaseURL`, with every response
  synthetic:
  - The client never reads `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, or `ANTHROPIC_BASE_URL`:
    with all three set to sentinels, every request reaches the test server with the `Options` key.
  - The SDK's own retries are off: a 500 on `Create` is one request, not three.
  - A mismatched `anthropic-workspace-id` makes `CheckWorkspace` fail, and the test server sees no
    `Create`, `Send`, or count call after it.
  - One row per failures-table row: a transport reset (retried, then `ErrTransport` past
    `WallTime`); 429 with `retry-after` (waited, then success); 429 `enforced_spend_limit_reached`
    and the 400 usage-limit message (each `ErrSpendLimit`, the message kept); batch results
    `errored` with `api_error`, `overloaded_error`, and `invalid_request_error`, `canceled`,
    `expired`, `stop_reason` `max_tokens` and `refusal` (each its `Classify` action); sync HTTP
    500, 529, and 400 (each an `errored` result classified like its batch twin).
  - A batch round trip: `Create`, `Get` until ended, `Results` returning the usage block per
    `custom_id`; `List` returns only batches created after `since`.
  - `Send` streams and returns the message ID, text, stop reason, and usage.
  - `Request.Schema` and `Effort` reach the wire in the form the docs give.
  - The SDK is at its newest release, with the `dependency-upgrade` check in the PR body.
- Test: the gate.
- Pair: with P2.4.

### P2.4 `drafter spend` (35 min, auth-data)

- Outcome: `drafter spend [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--json]` loads the
  configuration (the project's when inside one, else the user layer alone), reads the ledger in
  `state_dir`, and prints cost by repo and seat with a total, for the current billing cycle by
  default or for the UTC dates given (`--until` inclusive). Estimated lines are counted and marked.
  `--json` prints the rows and the total as one object.
- Files: `cmd/drafter/spend.go`, `cmd/drafter/root.go`, `e2e/e2e_test.go`, `e2e/testdata/`.
- Acceptance: e2e rows on a synthetic ledger under a temp `state_dir` (set through a temp user
  config): the default window starts at the cycle start for a fixed `billing_cycle_day`; a
  `--since`/`--until` window includes a line at 23:59 UTC on `--until` and excludes one at 00:00 the
  next day; `--json` sums equal the human total; a missing ledger prints a zero total and exits 0.
- Test: the gate.
- Pair: with P2.3.

### P2.5 `make smoke` (45 min, auth-data; the live run is the last step)

- Outcome: a `smoke` Makefile target, kept out of `check`, that runs a Go test behind a `smoke`
  build tag. It loads the user configuration, resolves the key, checks the workspace, and submits
  one batch holding one request per seat shape on Haiku 5.5, then one sync request. A seat shape is
  a seat's answer schema, effort, and system prompt; until pass 4 builds the production schemas,
  the smoke's shape table holds one synthetic entry per seat (the seven seats of pass 1), each a
  short prompt with a small `max_tokens`, and pass 5 points the table at the production builders.
  Every request is reserved and settled through the real ledger in `state_dir`, under repo
  `drafter-smoke`. The test asserts that each result parses to its schema, that the ledger gained
  one settle line per request, and that each line's cost equals `ledger.Cost` over its usage
  block. The model ID comes from `claude-api`'s model table and the price from the user config.
- Files: `Makefile`, `internal/batch/smoke_test.go` (build tag `smoke`), `CLAUDE.md` (one line
  naming the target and that it spends money).
- Acceptance, offline: `go vet -tags smoke ./...` passes, and the gate stays green without the tag.
- The live run, last in the pass. Check, by name only and printing no value:
  1. `~/.config/drafter/config.toml` exists and sets `workspace_id`, both caps, and a price for the
     smoke model;
  2. `grep -c '^export DRAFTER_API_KEY=' ~/.local/secrets` prints 1;
  3. the meter: `go run ./cmd/drafter spend --since 2026-10-13 --json` from the worktree shows a
     total that, plus $1, stays at or under $15.
  When all three hold, run `bash -c '. ~/.local/secrets && make smoke'` from the worktree, with
  `DRAFTER_CYCLE_CEILING=15` in its environment so the ledger itself enforces the initiative's
  limit, and record the result, the requests, and the ledger lines' total in the PR body. When any
  check fails, don't wait: the PR body records "smoke not yet run" and which check failed, and pass
  5 runs the smoke first among its live steps.
- Test: the live run when it happens; otherwise the offline acceptance.

### Close (30 min)

The gate, once, on the close head. One whole-branch `diff-reviewer` run against `main`, with
go-conventions for `*.go`; it re-derives each task's class and confirms each task-scope verdict is
recorded. One batched fix chain if needed, each fix quoting its finding verbatim, then the gate
again, and a second review only on a blocker. `gitleaks git` over the branch history, plus a check
that no fixture, test, or log in the diff holds anything shaped like an `sk-ant-` key.

Push the branch to `glw907/drafter` and open the PR. The body opens with `## Brief`, then what landed,
each task's `diff-reviewer` verdict, the smoke result or "smoke not yet run" with the reason, the
`claude-api` sources from P2.3, the score rows (the Work and review row puts the 285-minute path
beside the actual), and "Found, not done" with a proposed disposition each. It notes for the merger:
after the merge, `make -C ~/Projects/drafter install`. Stop at PR-ready; the conductor takes it to
Geoff.

## Later

- A `drafter spend --by page` breakdown for the pilot's per-page cost criterion, if reading the
  ledger lines by hand proves slow.
