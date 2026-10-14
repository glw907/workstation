# drafter P2 and P5 plans: contract-and-criteria review

Reviewer lens: contract and acceptance criteria. Targets at `456b409`:
`docs/superpowers/plans/2026-10-13-drafter-p2-money-plan.md` (P2) and
`docs/superpowers/plans/2026-10-13-drafter-p5-pipeline-plan.md` (P5), against the completion design
(`docs/superpowers/specs/2026-10-13-drafter-completion-design.md`) and the pipeline spec
(`docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, "Operations" and "Testing").

Probes run: the SDK source at `~/go/pkg/mod/github.com/anthropics/anthropic-sdk-go@v1.80.0`, the
chain script at `~/.claude/workflows/docs-page-chain.js`, cairn-cms's main checkout, the P1 and P4
plans, `secret-receive`, and `tellgrader`.

Verdict: neither plan is ready as written. 3 findings are vacuous criteria in the auth-data pass's
headline promises: the flock race, the SDK environment isolation, and the settle key. 2 are spec
Testing rows nobody owns: the workspace mismatch at run level, and the production-shape smoke run
live. 3 are OWNER FORKs on the end-to-end check. Everything else folds into the plans as written.

## Findings, ranked by consequence

### 1. The two-process ledger race passes with no lock (major, correctness)

P2:162-164. "Two processes ... race to reserve a sum only one may hold; exactly one succeeds." That
outcome also holds without `flock` whenever the two processes don't interleave between read-check
and append. The second process then reads the first one's reserve line and refuses on its own. Two
re-executed test binaries almost never interleave inside a microsecond window, so the test passes
with the lock deleted. This is the spec's whole concurrency promise ("two drafter processes can't
both pass a cap", spec:621-622).

Fold: force the overlap. Give `Reserve` an unexported hook called between the check and the append
(`var afterCheck func()`, nil in production). Each child sets it to wait on a barrier: it touches
`ready-<n>` and spins until both ready files exist, with a 5 s timeout that fails the test. Under
the lock, the second child blocks in `flock` and never reaches its hook, so the barrier must not
deadlock it. Make the barrier "wait up to 500 ms for the peer, then continue". Add the criterion:
"with the lock call replaced by a no-op (a temporary local edit, recorded in the task's commit
message as run), both children succeed and the test fails." Seeing the failure once is the bar,
the same as test-first.

### 2. The environment-isolation test can't see `ANTHROPIC_AUTH_TOKEN` (major, correctness)

P2:187-188. "with all three set to sentinels, every request reaches the test server with the
`Options` key." The SDK's default chain stops at the first variable it finds
(`client.go:63-75`):

```go
if v, ok := os.LookupEnv("ANTHROPIC_API_KEY"); ok && v != "" {
    defaults = append(defaults, option.WithAPIKey(v))
    return defaults
}
...
if v, ok := os.LookupEnv("ANTHROPIC_AUTH_TOKEN"); ok && v != "" {
    defaults = append(defaults, option.WithAuthToken(v))
```

With all three set, `ANTHROPIC_AUTH_TOKEN` is never read, so the test can't detect it. The
explicit `option.WithAPIKey` and `option.WithBaseURL` are applied after the defaults
(`client.go:212`, `opts = append(defaults, opts...)`), so the key and base-URL legs pass even
without `WithoutEnvironmentDefaults`. Without that option, an `ANTHROPIC_AUTH_TOKEN` set alone adds
`authorization: Bearer <token>` beside the `X-Api-Key` (`option/requestoption.go:641-645`). That is
the OAuth-billing path the spec forbids (spec:663-664), and "reaches the server with the Options
key" still passes, because it checks only `X-Api-Key`.

Fold: one row per variable, each set alone: `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`,
`ANTHROPIC_BASE_URL`, and `ANTHROPIC_PROFILE` naming a missing profile. Each asserts the request
reached the test server, `X-Api-Key` equals the `Options` key, no `authorization` header is
present, and no header value contains the sentinel. Add: "deleting
`option.WithoutEnvironmentDefaults()` from `New` fails the `ANTHROPIC_AUTH_TOKEN` row" (seen once).

### 3. A settlement with no message ID collides on an empty key (major, correctness)

P2:101-104, 112. `Settle` dedupes by `Key`, which is "the message ID in sync mode". Three
settlements have no message ID:

- a sync HTTP 500, 529, or 400 (P2:75-77 makes each an `errored` result, and no message exists)
- an `estimated` settlement, whose response was lost
- a `void` settlement

The second such settlement under one key is dropped as "already settled". The intent then never
reaches "every one of its requests has settled" (P2:110-111) and counts at `Worst` forever. Each
lost-response sync request inflates the page and cycle totals until caps refuse good work. P5.2's
estimated-then-resend path (P5:153-154) hits this on every resume.

Fold: the interface states the key for every kind. Batch mode keeps `<batch-id>/<custom_id>`. A
sync request with a message ID uses that ID. Anything else uses `<intent>/<custom_id>`, with the
`custom_id` unique per attempt as the spec requires (spec:724-726). `Settle` refuses an empty key.
Criteria:

- Two errored sync results under one intent leave two lines, and the intent drops to its settled sum.
- An `estimated` and a `void` settlement in one intent each count once.
- `Settle` with `Key: ""` returns an error.

### 4. The production-shape smoke never runs against the API (major, correctness)

P5:237-246 and P5:271-273. P5.6 rebuilds the smoke on production schemas, and its only acceptance
is `go vet -tags smoke`. P5.7 runs the smoke only "when pass 2's PR recorded 'smoke not yet run'".
So if P2's live run happened, nothing ever sends the production answer schemas, efforts, and
system prompts to the real API. The spec's smoke paragraph (spec:860-865: "schema, effort, and
system prompt as production builds them") is never exercised. The first real test of pass 4's
schemas becomes P5.8's $10-capped page.

Fold: P5.7 always runs `make smoke` on the P5.6 shapes, after the meter check. It costs under $1,
and both smokes plus the $10 page worst case stay inside $15 if each smoke stays under $1. Make
P5.7's acceptance "the production-shape smoke passed in this pass".

### 5. The batch list API has no created-after filter, and the fake can hide that (major, correctness)

P2:83-85 and P2:198-199 ("`List` returns only batches created after `since`"). In the SDK, the list
parameters are only `AfterID`, `BeforeID`, and `Limit` (`messagebatch.go:857-867`), so filtering
by time is client-side over pages. If the `httptest` fake filters by a query parameter, the test
passes on a client that sends a parameter the real API ignores. Resume would then adopt by scanning
only the first page of 20.

Fold: the fake ignores every filter parameter and serves newest first across at least 3 pages
(`limit` 2, a `has_more` and `last_id` chain), with batches on both sides of `since` and one
exactly at it. Assert:

- the client walks pages until it passes `since`
- it returns exactly the later batches
- it stops paging once a page's oldest batch predates `since` (the fake counts page requests)

### 6. `Classify` has no action for an unlisted error type (major, correctness)

P2:90-95. The failures table names `api_error`, `overloaded_error`, and `invalid_request_error`.
An `errored` result can also carry `authentication_error`, `permission_error`, `billing_error`,
`not_found_error`, `request_too_large`, or `rate_limit_error`. The plan defines no default, so the
executor picks one, and a zero-value `Action` could be "accept".

Fold: make the `Action` zero value an invalid sentinel, never accept. An unlisted `ErrType`
escalates with the error, like `invalid_request_error`. Add a row with `billing_error` and a row
with an empty `ErrType` on an `errored` result.

### 7. Run-level workspace mismatch is in no task (major, correctness)

The spec's key row ends "a mismatched `anthropic-workspace-id` stops the run before any request"
(spec:836-837). P2.1 hands it to P2.3 (P2:138). P2.3 tests `CheckWorkspace` at the client
(P2:190-191), where "the test server sees no `Create` ... after it" is vacuous: the test itself
decides whether to call `Create`. P5.2 orders `CheckWorkspace` before any request (P5:144-145), but
its acceptance (P5:157-163) has no workspace row.

Fold: add a P5.2 row. The fake API's `Workspace` returns another ID. `pipeline.Run` returns the
mismatch error naming both IDs, and the fake records zero `CountTokens`, `Create`, and `Send`
calls. Add the same on `--resume` with `workspace_id` changed in the user config between the stop
and the resume, which the "read fresh" rule requires (P5:149).

### 8. Pipeline stop reasons past the stop table are unmapped (major, correctness)

P5:72-74 and P5:173-175. `Summary` holds "the run's stop reason", and exit 3 means "stopped
resumable". The plan never maps these to outcomes or exit codes:

- `batch.ErrTransport` (the wall time spent): the spec says only that state doesn't change, spec:778
- `canceled` or `expired` twice ("stop the run as infrastructure", spec:783)
- `gate.ErrInfra`, the vanish case
- "tree red outside drafter's pages" (spec:517)

A run where some pages escalated and the run then stopped resumable has two exit codes, 1 and 3,
and no precedence.

Fold: list the stop reasons (`cycle cap`, `spend limit`, `transport`, `infrastructure`,
`tree red outside drafter's pages`) with resumable-or-not and exit code for each. Rule that exit 3
outranks 1. Add one P5.1 row per reason, each asserting `Summary`'s reason, no page escalated for
it, and the resume line printed.

### 9. The prompts-module resume row passes even when drafter reads the live module (major, correctness)

P5:161-162. "a mid-run edit to the prompts module that changes no prompt of the run". An edit that
changes no prompt yields identical requests whether drafter builds from the run-directory copy
(spec:702-705) or from the live file, so the row can't fail. A no-op edit is a fair resume row for
proving the handoff checksum ignores the module, but it doesn't test the copy.

Fold: keep it as the clean twin, and add the negative. Between the stop and the resume, edit the
module so the `editor` seat's prompt text changes. The resumed run's `editor` request carries the
original text byte for byte, and the run directory's module hash is unchanged. Do the same for an
agent-definition edit.

### 10. Rows naming several triggers can pass on one (major, correctness)

P5:119-122. "One test per stop-table row and per failures-table row." Several rows carry more than
one trigger or a two-step budget, and one test per row passes with the other trigger unhandled:

- Draft "unreadable": truncated, unparseable, or a brief that isn't JSON (spec:397)
- Final read: coverage miss, scoped re-read fix, or retest fix (spec:404)
- Round 2 or final read: missing or unreadable (spec:403)
- the failures table's `api_error` or `overloaded_error` or sync 500 or 529; `canceled` or
  `expired`; and the "once" rows, where the first failure resubmits and the second takes the
  terminal action (spec:781-785)

Fold: one test per trigger. Each "once" or budgeted row tests both the retry and the terminal
failure. The budgeted row's clean twin succeeds on the retry.

### 11. Escalation restore and the record have no criterion (major, correctness)

P5:107-114 promises restoring an escalated page's page and brief to their snapshots, or removing
them when drafter created them, with `final.page.md` and `final.brief.json` kept. It also promises
`record.json` with every field "Records" lists (spec:686-688). The acceptance (P5:119-132) tests
neither, except `faults`, the stop rule, the seat, and the finding numbers. The pilot's cutover
criteria read cost, faults, and escalation causes from these records (spec:873-882).

Fold: add rows.

- A page that existed before the run escalates: its file and brief equal their pre-run bytes, and
  the record holds `final.page.md` and `final.brief.json` with matching hashes.
- A page drafter created escalates: both files are gone from the worktree.
- The accepted batch-mode synthetic run's `record.json` matches a golden that names every
  spec:686-688 field (stages, verdicts, findings, resolutions, faults, friction, escalation, cost,
  mode, plan format, facts store, seats not run, input hashes, final status), with `cost` equal to
  the run's ledger total for that page.

### 12. No test that the key never lands in output or the run directory (major, correctness)

The spec promises "drafter never prints the key" (spec:663) and that the resolved configuration is
copied "without credentials" (spec:702-704). P5.2 copies the configuration (P5:142-144), and no
criterion in P2 or P5 checks it.

Fold: in P5.2 and P5.3, set the key variable to a sentinel. After a synthetic run and after
`page --dry-run`, a byte search of the run directory, the ledger, stdout, and stderr finds no
sentinel. The copied configuration holds no `key_command` value.

### 13. A transport failure mid-stream drops billed usage (major, correctness)

P2:86, 89, and 181-182. Transport errors retry inside the client. A sync stream that fails after
the response headers has already been billed for its input, and maybe part of its output. A silent
retry loses that usage from the ledger, which the pilot's 5% Console match needs (spec:881-882).

Fold: `Send` retries only failures before a response status arrives. After that, `Send` returns a
distinct `ErrStreamLost` wrapping `ErrTransport`, and the pipeline settles the attempt as
`estimated` at its share of the reservation, then resubmits by the failures table. Add P2.3 rows:

- a reset before headers is retried
- a reset mid-stream returns `ErrStreamLost` after one server hit
- an SSE `error` event (`overloaded_error`) mid-stream is an `errored` result with that `ErrType`

### 14. The smoke's assertions are only compile-checked offline (major, correctness)

P2:229-235. The live run is the only execution of the smoke's assertion code: parse to schema, one
settle line per request, cost equality. A filter bug, such as counting lines for the wrong run ID,
compares 0 with 0 and passes. A shape table that came out empty submits nothing and passes.

Fold: put the body in an untagged function that takes an `Options` and a state dir, and run it in
the normal gate against the `httptest` fake. The tagged test only supplies the real configuration.
Add two asserts: the shape table holds exactly the seven seats, and the settle-line count equals
`len(shapes)+1` and is not zero.

### 15. Resume rows miss decoys, twins, and several refusals (major, correctness)

P5:157-163 against P5:149-155.

- Adoption: the fake's `List` must also return a decoy created after the intent with other
  `custom_id`s, and one created before the intent. Add the clean twin: no batch carries the
  intent's `custom_id`s, so it resubmits once.
- Redo-the-write: assert zero fake calls and no new ledger line. Add the twin: files at the
  post-write hashes continue without rewriting.
- A stop after the batch ended, resumed twice, still leaves one settle line per `custom_id`.
- No rows for a branch mismatch, a HEAD that isn't a descendant (reset to the parent), another
  state schema at the pipeline level (P1 tests `LoadState` alone), or a `page_cap` tightened between
  the stop and the resume that escalates `cap` where the first run would not (spec:706-707). Add
  them.

### 16. OWNER FORK: the end-to-end check passes on an early escalation

P5:301-303 against design:65 ("takes it through every stage in batch mode"). "Accepted, or
escalated with an empty `faults` list" passes on a stage-1 `plan` escalation, a `cap`, or an
`unreadable draft`. In each case drafter's back half never ran, and the pass still reports
pilot-ready.

- (a) Keep it as written.
- (b) Require the record to reach stage 4 (round-1 reads). An earlier escalation with empty faults
  counts as "input cause", and the pass picks another page if the meter allows. (recommended)
- (c) Require `accepted`.

Recommendation (b): it holds the design's "every stage" intent without making a model verdict the
pass condition.

### 17. OWNER FORK: the $15 meter rule allows about one real page

P5:46-48 and P5:298-303. The rule is "total plus $10 at or under $15". After two smokes and one
page at the spike's $3 to $5, the total is near $5, so any rerun after a fix-forward is blocked.
P5.8's "rerun only when the meter allows" is then dead, and any `faults` finding ends the pass at
"stop and notify".

- (a) Keep $15. A fault stops the pass for Geoff. (recommended for a cautious first live)
- (b) For a rerun, set `DRAFTER_PAGE_CAP` to `15 - total`, so the meter's worst case shrinks with
  the remaining budget. The ledger enforces it, since caps resolve lowest-wins with the environment
  included (P1 plan:163). A rerun may then escalate `cap`.
- (c) Raise the initiative cap, for example to $25.

Mechanical fold, whatever the fork: the meter rule's worst case is the effective page cap, not a
literal $10.

### 18. OWNER FORK: the design's 5% Console match moves to Geoff's PR read

P5:304-307 against design:65 ("`drafter spend` must match the Console within 5%"). The session
can't read the Console, so the pass reports pilot-ready with a design criterion unverified.

- (a) Defer to Geoff's PR read. The pilot-ready statement says it is conditional on that check.
  (recommended)
- (b) Give the session a Usage and Cost Admin API key to check it itself.
- (c) Drop it here and leave it to pilot criterion 4.

Mechanical fold, whatever the fork: the comparison window must cover every live drafter-workspace
spend. P2's smoke may fall on another date, so report `drafter spend --since <first live date>
--until <last>` and the matching Console window. Don't use the run's dates alone.

### 19. P5.5's `drafter config` criterion contradicts `Validate` (minor, correctness)

P5:229-230: "prints every committed value with source `drafter.toml` and no refusal". `prompts` is
required (P1 plan:193), but the setting is project-and-local only (spec:222), and cairn's
`drafter.toml` deliberately omits it (P5:218-219). With only a temp user config, P1.4 prints the
table and exits 1 (P1 plan:244-245).

Fold: use a temp `drafter.local.toml` (gitignored) that sets `prompts` to a fixture path, with a
temp user config holding `workspace_id`, the caps, and a `claude-opus-5-5` price. Expect exit 0.
Alternatively, expect exit 1 with `Validate` naming only `prompts`.

### 20. Cap boundary, float sums, and the long-context threshold basis are open (minor, correctness)

P2:107-119 and P2:158-172.

- "Cross" doesn't say whether a total exactly equal to the cap passes.
- Is the tier threshold `InputTokens` alone, or input plus cache read and cache write? Is it `>` or
  `>=`? Does the tier change the output rate too?

The hand-computed test figures just encode whichever the executor picks.

Fold: state each answer from the pricing page that the `claude-api` skill cites. Add a row at
exactly the cap (passes) and one cent over (refused). Add a row at the threshold and one token over.

### 21. `CycleStart` rows don't pin their instants (minor, correctness)

P2:166-167: "with `day` 31 in February of a leap and a common year". This doesn't say what `now`
is.

Fold: name the instants:

- `now` 2028-03-10 with day 31 gives 2028-02-29 00:00 UTC.
- `now` 2027-03-10 gives 2027-02-28.
- `now` 2027-02-15 gives 2027-01-31.
- `now` 2027-02-28 00:00 exactly gives 2027-02-28.
- one nanosecond earlier gives 2027-01-31.

### 22. `drafter spend` criteria miss marking, grouping, and reservations (minor, correctness)

P2:208-217.

- "Estimated lines are counted and marked" has no row.
- "By repo and seat" has no row; "`--json` sums equal the human total" passes with wrong grouping.
- Whether open reservations count toward spend is unspecified. The plans use spend as the live
  meter (P2:240, P5:46), so this matters.
- The default-window row depends on today's date.

Fold:

- Two repos by two seats, with hand-computed rows.
- One estimated line, shown with its mark and `Estimated: 1` in JSON.
- A reserve line with no settle, excluded from cost, with the decision stated.
- Fixtures written relative to `ledger.CycleStart(time.Now(), day)`: one line just before it, one
  just after.

### 23. Transport and 429 rows lack twins and edges (minor, correctness)

P2:192-194.

Fold:

- Add the clean twin, a reset then success, asserting at least 2 server hits.
- Add a `retry-after` longer than the remaining `WallTime`, which returns `ErrTransport` without
  sleeping it out.
- Add a 429 `rate_limit_error` with no `retry-after`, treated as a transport retry.
- Inject the clock or backoff so these rows run in milliseconds.

### 24. Key-command sentinel goes only to stdout (minor, correctness)

P2:144-146. The sentinel is printed but its stream isn't named, and "standard error discarded" has
no observable check. The rows also rely on the ambient `DRAFTER_API_KEY` being absent, and that
variable exists on this machine once P2.5 or P5.7 sets it up.

Fold: the failing command writes the sentinel to both streams. Assert the error and the test
process's captured stderr hold no sentinel. Every row sets `key_env` to a test-unique variable
name.

### 25. P5.1's remaining outcome bullets have no row (minor, correctness)

P5:91-116 against P5:119-132. These have no row:

- a seat left out of `seats`, whose stages and stop rows go and which the record names
- the markdown-plan skip, with its warning and `plan_format: markdown`
- the outline exemption: a run of pages A and B where A's plan links B passes stage 1, and A alone
  escalates `plan`
- `pages_in_flight`: with 1, B's first `Create` follows A's end; with 3, all three stage-2 creates
  precede the first `Get`
- the page-cap row's fixture

Fold: add each. For the page-cap row, the fixture is the spec's (spec:829-830): `CountTokens`
puts input under the cap and input plus `max_tokens` over it. The clean twin uses a smaller
`max_tokens`, and the refused stage records zero `Create` or `Send` calls.

### 26. P5.3's dry run doesn't pin its stage, ledger, or exit codes (minor, correctness)

P5:177-182.

- With a facts store, the "first stage" is the consistency read, not the draft. The fixture should
  name which one the hand-computed figure prices.
- Assert the dry run leaves no ledger line and no run directory.
- Exits 0, 1, and 3 have no row. Test the `Summary`-to-exit mapping as a unit table, including the
  1-versus-3 precedence from finding 8.

### 27. P5.4's docs checks can pass hollow, and `tellgrader` isn't installed (minor, correctness)

P5:199-202.

- A reflection walk that misses nested keys (`retries.*`, `gate.*`, `seat.<name>.*`) passes the
  settings test. Assert the walked key count is at least the spec table's rows (spec:203-227), and
  check the dotted forms.
- `tellgrader` is not on `PATH`. The probe `which tellgrader` found none, though its source is at
  `~/.claude/skills/writing-voice/evals/tellgrader`, with an `install` target. Name `make -C
  ~/.claude/skills/writing-voice/evals/tellgrader install` as a step. Its `--register` flag
  defaults to `docs` (`cmd/tellgrader/root.go:36`).
- `setup.md` has four required topics (spec:633-642, P5:193-196) and no check. Add a reviewer
  checklist line, or a grep for each topic.

### 28. The fact seat's input takes half the chain's row rule (minor, correctness)

P5:214-216 uses `grep -n 'pending {slug}' docs/internal/option-map.json`. The chain's rule is the
`"pending <slug>"` rows and also every row whose value is one of the page's fact IDs
(`docs-page-chain.js:893-897`). Today the map has no `pending ` row at all: the probe `grep -c` gave
0, beside `"pendingCount": 2`. So the command prints nothing and exits 1 on most pages.

Fold: state the reduction as intended, or widen the input. In both cases, note in P5.5 that a
nonzero exit with empty output is expected.

### 29. The `$15` ledger guard is cycle-scoped and notifies no one mid-run (minor, correctness)

P2:242-244 and P5:47-49. `DRAFTER_CYCLE_CEILING=15` counts spend since the cycle start, not since
the initiative began. If the initiative crosses `billing_cycle_day`, the guard silently resets. A
mid-run `cycle cap` stop exits 3, but the plans name `notify-send` only for the pre-run meter
check, while design ruling 2 asks for "stops and notifies".

Fold: on exit 3 with `cycle cap` or `spend limit`, run `notify-send -u normal`. Note the
cycle-scope limit in the shape bullet.

### 30. `index_link_command`'s shell expression is first tested with money on the line (minor, optional)

P5:266-269. Fold: in P5.7, run the command once on a known page per arm in a cairn worktree, check
exit 0, and spend nothing. This is cheaper than finding a quoting bug in P5.8.

### 31. The ledger no longer holds the lock across submission, unlike the spec (minor, optional)

The spec puts "every cap check, submission, and append" under `flock` (spec:621). P2's reserve-then-
submit (P2:107-111) is the better design, since a lock held across network I/O would serialize
processes, but nothing records the departure. Fold: one line in P2's Interfaces naming it and why.

### 32. Over-ceremony: test-first and per-task review on P2.5 (minor, optional)

P2:130-132 applies "commit tests failing first" and a task-scope `diff-reviewer` to P2.5, whose
code is the test itself plus a Makefile target. A failing-first commit means nothing there. The
cost is about 10 minutes and one reviewer run of tokens. Fold: exempt P2.5 from the failing-first
commit and fold its review into the Close review. Geoff ruled the pass auth-data, and this keeps
that ruling's substance.

## Spec Testing rows for these packages

| Spec row (spec line) | Assigned | Gap |
|---|---|---|
| Caps and ledger: input-plus-max_tokens refused (829-830) | P2.2, P5.1 | P5.1 fixture unnamed (25) |
| Several in-flight pages crossing the ceiling (830) | P2.2 | Boundary (20) |
| Two processes, one ledger (831) | P2.2 | Vacuous (1) |
| Settle applied twice (831) | P2.2 | Empty key (3) |
| Reset instant, day 31 in February (831-832) | P2.2 | Instants (21) |
| One-hour cache write; Haiku over 100,000 (832-833) | P2.2 | Threshold basis (20) |
| Seat with no price (833) | P2.2 (and P1 at load) | none |
| Key: `ANTHROPIC_API_KEY` only, OAuth only (834-835) | P2.1, P2.3 | SDK leg vacuous (2) |
| `key_env`, `key_command` precedence, refusal without printing (835-837) | P2.1 | stderr (24) |
| Workspace mismatch stops before any request (837) | none at run level | Unassigned (7) |
| Projects without facts: no consistency read, `facts: none` (844-846) | P5.1 | none |
| Edit contract: red gate after applied edits shares budget (806) | P5.1 | none |
| Edit contract: declined blocking finding to next read (807) | P4.4 assembly, P5.1 flow | none |
| Gate: page B's broken link reaches A without A's fix turns (826-827) | P5.1 | none |
| Handoff: plan edited between stop and resume (821) | P5.2 | none |
| Pipeline: every stop-table and failures-table row (849-850) | P5.1 | Per-trigger (10), stop reasons (8) |
| Resume rows (850-855) | P5.2 | Decoys and twins (15), prompts (9) |
| Synthetic run accepted in each mode (855) | P5.1 | Record golden (11) |
| e2e: `check-plan`, `check-prompts`, `page --dry-run` estimate (857-860) | P5.3 | Stage and ledger (26) |
| `make smoke` on production shapes (860-865) | P2.5 synthetic, P5.6 vet only | Never run live (4), hollow asserts (14) |
| Parsing tests on spike responses (857) | none; the spike is gone | Accepted by the design (design:51). Optional: save the P2.5 smoke's raw batch results and stream as scrubbed `internal/batch/testdata` fixtures. |
