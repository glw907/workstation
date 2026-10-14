# drafter completion plans: the fold

Fold agent: `claude-opus-5-5`, 2026-10-13, on branch `drafter-completion-plans` at `d4ace9b`, under
`spec-plan-review` "The fold" and `superpowers:receiving-code-review`. Inputs: the five plans and
executor prompts, the seven review files, the completion design's rulings 1 to 8, and the pipeline
spec.

Facts changed since the reviews, applied throughout: the spike evidence and the 69 exemplar captures
are back on disk (2026-10-13); `tellgrader` is installed in `~/.local/bin`; the plans branch merges
to dotfiles `main` before the conductor launches anything, so prompts cite `~/.dotfiles/docs/...`;
the conductor appends `.claude/worktrees/` to drafter's info/exclude.

Evidence the fold checked itself, beyond the reviews' quotes:

- API docs, read 2026-10-13: batches create (`custom_id` "minLength: 1, maxLength: 64, pattern:
  `^[a-zA-Z0-9_-]{1,64}$`"; the `anthropic-workspace-id` header "if sent, it must match that
  Workspace"); errors (400 on an organization or workspace spend limit; the tier-cap 429 has no
  `retry-after`; mid-stream errors after a 200); rate limits ("Reaching your spend cap":
  `error.details.error_code` `enforced_spend_limit_reached`; "Setting your own spend limit": the 400
  message "begins `You have reached your specified API usage limits`, or `You have reached your
  specified workspace API usage limits`"); API overview (the response header is absent only when the
  credential resolves to no workspace or authentication failed); pricing (Haiku 5.5's tier applies to
  prompts "over 100,000 tokens", counting "all of its input tokens, including cache reads and cache
  writes", every rate changing; the batch discount is 50% on input and output and the cache
  multipliers "stack with ... the Batch API discount"; Opus 5.5 and Haiku 5.5 rates as P5.7 quotes);
  structured outputs ("JSON Schema limitations", quoted in P4).
- SDK v1.80.0 source: `client.go` reads `ANTHROPIC_BASE_URL`, `_API_KEY`, `_AUTH_TOKEN`, `_PROFILE`,
  `_CUSTOM_HEADERS`; `option.WithHeader` (`option/requestoption.go:227`); `WithAPIKey` sets
  `X-Api-Key`; `shouldRetry` retries any request with no response (`requestconfig.go:249-268`); the
  per-attempt timeout is handed to the body reader (`requestconfig.go:546-563, 630-638`); list params
  are only `AfterID`, `BeforeID`, `Limit` (`messagebatch.go:857-867`).
- `cairn-run-gate`: `gate exit:` and the vanish line go to stdout only (lines 410, 439); `--fresh`
  never affects reattaching (header line 14); run records carry `toplevel` and `gate`, so a drafter
  gate run from `~/.dotfiles` is found by its `gate` string. `scripts/drafter-gate.sh` already passes
  `--fresh`; `scripts/gate.sh` lines 3-5 name the worktree-isolation Bash guard.
- go-toml v2.4.3's `unstable.Parser` (`NextExpression`, `Expression`, `Shape`, `Range`) in the module
  cache. drafter's `check-plan --outline` repeats (`StringArrayVar`); `CheckOptions` says callers
  confirm a facts dir with `CheckFactsDir`; `Outline` has only unexported `paths`.
- cairn: outlines' `crossLinks` carry repo paths and cross-outline slugs; 39 `<a id>` anchors and no
  `<a name>` in its docs; cairn.pub's `stripAnchorClobberPrefix` strips `id` only
  (`link-policy.ts:93-102`); 11 YAML plans; `cairn-docs-outline` resolves `exemplarSources` to
  absolute paths under the exemplar root; cairn-pass maps `scripts/docs-review/**` to `ordinary`.
  No `wf_*.json` exists under `~/.claude/projects/` on this machine. `tellgrader --help`: gating only
  "under the docs-register profile", `--profile` resolves from the scanned repo's `.tellgrader.json`
  when omitted.

## Dispositions

Keys: `p1m` to `p5m` are the mechanics reviews (`2026-10-13-drafter-pN-review-mechanics.md`), `c`
the contract review and `i` the integrity review (`2026-10-13-drafter-p2-p5-review-*.md`). "Ruling"
means the design's Technical notes 8. P-numbers are the revised plans' tasks.

### p1m (pass 1 mechanics)

- p1m-1 folded: P1.1 item 8 (slug or repo path, cross-outline slugs, unresolvable `to` warns) and a
  Close regression check over cairn's 11 plans that blocks the self-merge.
- p1m-2 folded: P1.1 item 7 counts `<a id>` only, from `RawHTML`/`HTMLBlock` nodes, with a fenced row.
- p1m-3 folded: `Validate(scope)` with `ScopeMoney` and `ScopeRun` (P1 Interfaces, P1.2, P1.4);
  consumers updated in P2.5, P5.3, P5.5, P5.7, P5.8.
- p1m-4 folded: `Prune` keeps `Stopped` runs and skips unreadable state; `pending` status (P1
  Interfaces, P1.3); P5.2 lists every page `pending`.
- p1m-5 folded: placeholder grammar not preceded by `$` (P1.2); P4's `gate.Command` uses it.
- p1m-6 folded: `gate.index_link_command` (P1 Interfaces, P1.2, P5.7). Erratum 6.
- p1m-7 folded: `unstable.Parser` key-to-line index named in P1 Shape, with its own row in P1.2.
- p1m-8 folded: P1.2's environment rule enumerated.
- p1m-9 folded: P1.2's ignore rows (tracked and listed; untracked and unlisted; untracked and listed).
- p1m-10 owner fork, ruled (ruling 8): P1.2 refusal rows first, named in the Close dispatch.
- p1m-11 folded: P1.2 range checks.
- p1m-12 folded: P1.2 cross-layer checks on resolved values.
- p1m-13 folded: empty or malformed TOML, a top level with no `drafter.toml` (P1.2), `LoadState`
  states (P1 Interfaces, P1.3), `drafter anchors` missing file and no anchors (P1.1 item 7).
- p1m-14 folded: `consistency` required only with `facts.dir` (P1 Interfaces).
- p1m-15 folded: `BatchDiscount` is the fraction off; the price TOML keys named (P1 Interfaces).
- p1m-16 folded: 8 hex from `crypto/rand` (P1 Interfaces).
- p1m-17 folded: `TryLock` and `Release` semantics, flock(2) quoted (P1 Interfaces, P1.3).
- p1m-18 folded: `--path-format=absolute`; git test environment (P1 Interfaces, P1.2, P1.3).
- p1m-19 folded: P1.4's e2e helper strips `DRAFTER_*` and sets `XDG_CONFIG_HOME` and `HOME`.
- p1m-20 folded: P1.2's atomicfile row fails after the temp is written and checks mode and leftovers.
- p1m-21 folded: P1 Close's PR body names the move into `Validate`.
- p1m-22 folded: P1.4 renders by resolved `output`; the every-layer row uses `mode`.
- p1m-23 optional, folded (one call, clearly right): `filepath.IsLocal` in P1.1 item 3.
- p1m-24 folded: every plan's Close reads gate time from `runs.jsonl` filtered on the worktree.
- p1m-25 already resolved: the plans merge before launch, the conductor writes info/exclude, and
  every prompt path is absolute.
- p1m-26 already resolved: `tellgrader` is installed.
- p1m-27 optional, dropped.

### p2m (pass 2 mechanics)

- p2m-1 folded: retry discipline and `ErrMaybeSent` (P2 Interfaces, P2.3 rows), adopted or settled
  in P5.1's money path. Erratum 1. Converges with c-13 and i-1.
- p2m-2 folded: P2.3's per-variable credential rows. Converges with c-2.
- p2m-3 folded: `CheckWorkspace(ctx)` gates spending methods, the free models call, the header on
  every request, absent header as a mismatch (P2 Interfaces, P2.3); run-level rows in P5.2.
  Converges with c-7 and i-18.
- p2m-4 folded: `ErrSpendLimit` by `error_code` and the `You have reached your specified` prefix;
  `ActionSpendLimit` for an errored result (P2 Interfaces, P2.3). Erratum 2.
- p2m-5 folded: idempotent calls retry 5xx and 529; mid-stream errors are `ErrMaybeSent`;
  `model_context_window_exceeded` and unlisted stop reasons mapped (P2 Interfaces, P2.3).
- p2m-6 folded: `RequestTimeout` and `StreamTimeout` (P2 Interfaces, P2.3 row).
- p2m-7 folded: the line schema with `v` and `time`, file states, fail-closed reads (P2 Interfaces,
  P2.2). Converges with i-9.
- p2m-8 folded: the barrier hook and the lock-no-op twin (P2.2). Converges with c-1.
- p2m-9 folded: `max_tokens` 4096, `-count=1 -timeout 2h`, a recorded smoke batch settled by the
  next run, `additionalProperties: false` (P2.5). Converges with i-8.
- p2m-10 folded: the smoke lives in `internal/smoke`, so no test imports `ledger` from `batch`.
- p2m-11 folded: recorded usage equals the API's block field for field, cost above zero (P2.5).
- p2m-12 folded: the env cap binds through `config.Load`; its cycle scope stated (P5 Shape).
- p2m-13 folded: `Action` names, the estimated share `Worst / Requests`, `spend --json` fields, the
  project rule for `drafter spend`, `Schema` conversion, the threshold basis (P2 Interfaces, P2.4).
- p2m-14 folded: P2.1's unset and empty rows, streams, inner whitespace; the test-unique `key_env`.
- p2m-15 optional, refused: after c-14's fold P2.5 holds untagged code tested against a fake, so
  test-first has substance, and Geoff's ruling 1 stands as written.
- p2m-16 owner fork, ruled (ruling 8): P2 has no live step or `live-account` flag, its PR brief says
  so first (P2 Shape, P2.5, Close); P5.7 runs the smoke.
- p2m-17 already resolved: the planning session writes the conductor prompt.

### p3m (pass 3 mechanics)

- p3m-1 folded: adapter mappings fixed (P3 hooks) and the chain-fidelity test (P3.4).
- p3m-2 folded: `handoffFor(args, resolved, worktree, entries)` takes computed fields from its caller.
- p3m-3 folded: `scripts/gate.sh` passes `--fresh` with `DRAFTER_BIN` set; negative rows run the leg
  directly (P3.5, Close).
- p3m-4 folded: containment is `page.path`, `page.brief`, `plan`, `framing`; `exemplarSources` exempt
  (P3 handoff file, P3.2 rows). Erratum 4.
- p3m-5 folded: the default-behavior snapshot of every agent call from two runs (P3.4), replacing the
  reader-only goldens.
- p3m-6 folded: JSON crossing, `Round`, raw `Page` and `Inputs`, promise states (P3 loader, P3
  Interfaces, P3.1 rows).
- p3m-7 folded: `round: "final"` with `afterFinalRead` mapped to round 2 (context table, P3.5 matrix).
- p3m-8 folded with p3m-5: placeholder temp path, `inputs` stubbed per page type.
- p3m-9 folded: refusal after `resolvePages()`, before `reworkProbe()`; recorded calls asserted (P3,
  P3.4).
- p3m-10 folded: `(?m)^export const meta` (P3 loader, P3.1 fixture, P3.5).
- p3m-11 folded: `check-prompts` input states (P3.3) and `ReadWorkflowRun` states (P3 Interfaces,
  P3.2).
- p3m-12 folded: P5.8 confirms the run file's shape and fixes forward the synthetic fixture, never
  copying cairn text into drafter.
- p3m-13 folded: `Load` refuses a host with no `resolved`, naming the missing chain context (P3
  loader, P3.1 row); Later names a context-free host for cutover.
- p3m-14 folded: concept first; type from `pageInputs.pageType || p.pageType` (P3 handoff block).
- p3m-15 folded: the test rewrites `worktree` to the temp root (P3.2).
- p3m-16 optional, folded (one fixture line): P4.5's reader row uses a synthetic prompt naming an
  outline file.
- p3m-17 already resolved: absolute plan paths, merged before launch.
- p3m-18 optional, folded (one row): a handoff with no framing checksums the plan alone (P3, P3.2).
- p3m-19 optional, folded in part: the shared SHA-256 dropped from the PR bodies; P3.5 stays its own
  task, since it can't pair and runs after P3.3 and P3.4 already.

### p4m (pass 4 mechanics)

- p4m-1 blocker folded: the result is read from stdout; the log is parsed for sections only; the fake
  matches (P4.4).
- p4m-2 blocker folded: the session regenerates the logs itself through a no-argument scratch script
  before dispatching the pair (P4.3, executor prompt).
- p4m-3 folded: a fourth log with a Vale error; attribution rows on the recorded patterns (P4.3,
  P4.4).
- p4m-4 folded: `--fresh` on each gate's first call only (P4.4).
- p4m-5 folded: unmatched red log is unparsed, the preamble section (P4.4); a section pattern needs a
  capture group (P1.2).
- p4m-6 folded: the scrub rule stated once, with the Close grep extended to `@glw907` (P4.3, Close).
- p4m-7 folded: current-answer rules and union rules split; 0-based edit indexes named (P4 edits,
  P4.1).
- p4m-8 folded: the `Fact.Sources` extraction rule and cairn-shaped synthetic rows (P4 plan additions,
  P4.5).
- p4m-9 folded: named excerpt blocks, clamped ranges, first declaration, modifiers (P4.5).
- p4m-10 folded: cleaned, symlink-resolved, separator-bounded matching; `InlineFiles` from `Config`
  only; rows written first per ruling 8 (P4.5, Close).
- p4m-11 folded: the token rule and fixed block delimiters (P4.5).
- p4m-12 folded: `ConsistencyPrompt` defined, with its row (P4 Interfaces, P4.5).
- p4m-13 folded: the schemas held to the structured-output limits, quoted, with a schema walk (P4
  Interfaces, P4.5).
- p4m-14 folded: heading matching and missing plan headings (P4 coverage, P4.2).
- p4m-15 folded: the synthetic repo built at test time (P4.5 Files).
- p4m-16 folded: the brief decoder ignores unknown fields; `no-claim` ids (P4 coverage, P4.2).
- p4m-17 folded: `#anchor` and URL link targets (P4 coverage, P4.2).
- p4m-18 folded: `ForPage` path boundary (P4 gate, P4.4).
- p4m-19 folded: POSIX quoting in `gate.Command`; `Build(ctx, in)` with a per-command timeout.
- p4m-20 folded: what `edits` and `reader2` continuations inline (P4.5).
- p4m-21 folded: the slugger dropped from P4's Consumes.
- p4m-22 folded: absolute paths in every plan and prompt.
- p4m-23 optional, folded (measured cheaper, touches no cairn branch): `git clone --shared` and root
  `npm ci` in P4.3.
- p4m-24 already resolved: `tellgrader` is installed.
- p4m-25 optional, no action: it confirms the clocks.
- p4m-26 owner fork, ruled (ruling 8): `assemble` stays `ordinary`, path-safety rows first and named
  in the Close dispatch.

### p5m (pass 5 mechanics)

- p5m-1 already resolved: `tellgrader` is installed (P5 Shape).
- p5m-2 folded: `--profile docs-register` (P5.4).
- p5m-3 folded: commit every `git status --porcelain` path and assert clean (P5.8).
- p5m-4 folded: stage 1's outline from `context.args.outline` plus the run's pages, through a new
  `plan` constructor (P5.1, P5 Interfaces).
- p5m-5 folded: `git hash-object -w` (P5.1) with a two-sided-diff row.
- p5m-6 owner fork, ruled (ruling 8): the bar requires the round-1 reads; one rerun if the budget
  allows (P5.8).
- p5m-7 folded: faults classified; drafter-caused ones fixed forward, model-caused ones recorded. The
  design's "empty `faults`" bar is kept as written, so this changes no approved criterion (P5.8).
- p5m-8 folded: P5.7 always runs the smoke on the production shapes. Converges with c-4.
- p5m-9 folded: `run_in_background` for the smoke and the page run (P5.7, P5.8, prompt).
- p5m-10 folded: `BatchDiscount` defined in P1; P5.7 writes 0.5 and cross-checks every rate.
- p5m-11 owner fork, ruled (ruling 8): P5.1 and P5.2 `auth-data`; P5.5's class restated from
  cairn-pass's path map (P5 Shape).
- p5m-12 folded: files the index-link command changes are drafter's own writes, restored on
  escalation and hashed for resume (P5.1, P5.2).
- p5m-13 folded: the dirty-tree rows on a `git init` copy, untracked included (P5.3).
- p5m-14 folded: passes 1 to 4 checked at launch and in P5.8; none or several run files (P5.8).
- p5m-15 folded: a `run_in_background` until-loop for the key; the workspace ID only from Geoff
  (P5.7, prompt).
- p5m-16 owner fork, ruled (ruling 8): pilot-ready conditional on Geoff's comparison (P5.8, Close).
- p5m-17 folded: the meter and the run use this branch's built binary (P5 Shape, P5.8).
- p5m-18 folded: `CheckOptions.Root` and `CheckFactsDir` (P5.1).
- p5m-19 folded: adoption lists, waits, and matches through `Results` (P5.1, P5.2).
- p5m-20 optional, folded (the rerun ruling 8 adds needs the room): P5.8 at 120.
- p5m-21 optional, folded: ruling 6 settles the cycle day; its Found item is gone.
- p5m-22 optional, folded (free): P5.3 pairs with P5.4, P5.2 with P5.6.
- p5m-23 optional, folded (removes unread config): no `register.<track>` in cairn's file.
- p5m-24 optional, folded (one line each): every plan names the pairs' model, effort, and description.
- p5m-25 already resolved.
- p5m-26 optional, folded (one clause): rebase cairn's STATUS edit at close.

### c (P2 and P5 contract and criteria)

- c-1 folded with p2m-8 (P2.2).
- c-2 folded with p2m-2 (P2.3).
- c-3 folded: settle keys for every kind, `Settle` refuses an empty key (P2 Interfaces, P2.2).
  Erratum 7.
- c-4 folded with p5m-8 (P5.7).
- c-5 folded: the fake ignores filters across three pages (P2.3). Converges with i-3.
- c-6 folded: `ActionInvalid` zero value; unlisted types escalate (P2 Interfaces, P2.3).
- c-7 folded with p2m-3 (P5.2 workspace rows, start and resume).
- c-8 folded: stop reasons listed, all resumable, exit 3 outranks 1 (P5 Interfaces, P5.1, P5.3).
- c-9 folded: the changed-prompt and agent-definition negatives beside the no-op twin (P5.2).
- c-10 folded: one test per trigger, both legs of every budget (P5.1).
- c-11 folded: escalation restore rows and the `record.json` golden (P5.1).
- c-12 folded: key-sentinel searches (P5.1, P5.2, P5.3). Converges with i-10.
- c-13 folded with p2m-1, except its "a reset before headers is retried" row, refused: a reset after
  the body was written is ambiguous, so i-1's stricter rule (dial and DNS failures only) governs
  `Send`.
- c-14 folded: the smoke's body untagged and run in the gate against the fake; seat count and
  line-count asserts (P2.5, P5.6).
- c-15 folded: decoys, twins, double resume, and the refusal rows (P5.2).
- c-16 owner fork, ruled (ruling 8, P5.8).
- c-17 owner fork, ruled (ruling 8): the page cap is the budget left; the meter's worst case is the
  effective page cap (P5 Shape).
- c-18 owner fork, ruled (ruling 8); its mechanical fold, a window covering every live spend, is in
  P5.8.
- c-19 folded: P5.5's `drafter config` row uses a temp local file with `prompts` and expects exit 0.
- c-20 folded: cap boundary and the threshold basis from the pricing page (P2 Interfaces, P2.2).
- c-21 folded: `CycleStart` instants named (P2.2).
- c-22 folded: grouping, estimated marking, open reservations, cycle-relative fixtures (P2.4).
- c-23 folded: twins and edges for transport and 429, injected clock (P2.3).
- c-24 folded: sentinel on both streams; test-unique `key_env` (P2.1, P2 Tasks preamble).
- c-25 folded: the seat, markdown, outline, `pages_in_flight`, and page-cap rows (P5.1).
- c-26 folded: the dry run names its stage, leaves no ledger line or run directory; the exit table
  (P5.3).
- c-27 folded: the nested-key walk and its count, the `setup.md` topic grep (P5.4); the tellgrader
  install part is already resolved.
- c-28 folded: the reduction stated and the empty output expected (P5.5).
- c-29 folded: notify on a `cycle cap` or `spend limit` stop; the cycle-scope note (P5 Shape).
- c-30 optional, folded (one command, no spend): the index-link check before the page run (P5.8).
- c-31 optional, folded (one line): the lock-scope departure in P2 Interfaces. Erratum 3.
- c-32 optional, refused: as p2m-15.

### i (P2 and P5 integrity and failure risk)

- i-1 blocker folded with p2m-1.
- i-2 folded: the `custom_id` form, its pattern row, and a fake that rejects others (P5 Interfaces,
  P5.2).
- i-3 folded: newest-first paging with a 10-minute margin; the lagging-clock row (P2 Interfaces,
  P2.3). Erratum 8.
- i-4 folded with c-3; the resend is a new reserved attempt (P5.1, P5.2).
- i-5 folded: one reservation per submission unit; resubmissions new intents; unbilled results
  settle at zero (P2 Interfaces, P5.1). Erratum 5.
- i-6 folded: `Reserve`, then the state intent, then `Create` (P5.1); resume voids orphans (P5.2);
  `drafter spend` reports `open` (P2.4); the meter is `total` plus `open.worst` (P5 Shape).
- i-7 folded in its mechanical part: no open intent before a rerun or worktree removal (P5.8); a
  `cycle cap` stop with a batch in flight settles on resume (P5.2). Its OWNER FORK (drain, exit, or
  cancel) is answered by the ratified spec, not by this fold: the stop table says the run "stops,
  resumable", and "Resume" says `--resume` "settles any ended batch it hasn't ledgered". The plans
  build that. Listed in the report.
- i-8 folded with p2m-9 (P2.5).
- i-9 folded with p2m-7: the torn final line tolerated and fenced, `File.Sync` per append (P2.2).
- i-10 folded: errors never carry an SDK error struct (P2 Interfaces); `gate.Env` strips the key
  variable and `ANTHROPIC_*` from every child (P4); `key_command` under 30 seconds (P2.1); sentinel
  rows (P2.3, P5.1, P5.2, P5.3); records hold request bodies only (P5.1).
- i-11 folded: P5.7 merges into existing files, reports conflicts by key, writes atomically, and
  cross-checks prices.
- i-12 folded per ruling 8: the page cap is the smaller of 10 and the budget left; the smoke's check
  is meter plus $1 (P5 Shape).
- i-13 folded: the restore is a recorded write; the mixed case resumes (P5.1, P5.2).
- i-14 folded: any `git status --porcelain` line refuses, untracked included (P5.2, P5.3).
- i-15 folded: `CountTokens` takes the identical request (P2 Interfaces); the smoke asserts
  `input_tokens` at most the count (P2.5).
- i-16 folded: open intents count across the reset (P2 Interfaces, P2.2).
- i-17 folded: expired results settle `estimated` (P5.2).
- i-18 optional, folded with p2m-3.
- i-19 optional, dropped; a Later line in P2.
- i-20 optional, dropped: the exact-cap row uses amounts exact in binary instead (P2.2).
- i-21 optional, folded with c-31.
- i-22 optional, folded (one docs sentence): `setup.md` says to finish or resume runs before
  upgrading (P5.4); a Later line in P5.
- i over-ceremony (P2.5's live step): resolved by ruling 8.

### Counts

170 findings: 156 folded (owner forks applied per ruling 8 included), 2 refused (p2m-15, c-32; and
one row of c-13), 8 already resolved, 4 optional dropped. No finding changes the approved design.

## Owed spec errata

None of these edits the spec; each records where the plans narrow or extend
`2026-10-12-drafter-pipeline-design.md`.

1. "Failures", row 1: transport errors retry in place only on idempotent calls and on `Create` or
   `Send` failures that provably came before the request was written. Any other failure of `Create`
   is `ErrMaybeSent`, adopted through `List`; a `Send` that loses its response settles `estimated`
   and resubmits as a new attempt. `stop_reason` `model_context_window_exceeded` takes the
   `max_tokens` row; any unlisted error type or stop reason escalates.
2. "Failures", row 3: the spend limit is recognized by `error.details.error_code`
   `enforced_spend_limit_reached` on a 429, and by a 400 whose message begins `You have reached your
   specified`, which covers the organization's limit as well as the workspace's.
3. "The ledger": the lock covers the cap check and the append, not the submission; the reserve line
   counts before the request goes out.
4. "The handoff file": only `page.path`, `page.brief`, `plan`, and `framing` must resolve inside
   `project`; `inputs.exemplarSources` is exempt and governed by `inline_files`.
5. "Caps": the reservation unit is the submission unit (one batch, or one sync request), every
   resubmission is a new intent, unbilled results settle at zero, and the cycle total counts every
   open intent whenever it was reserved.
6. "Settings": `index_link_command` is spelled `gate.index_link_command`
   (`DRAFTER_GATE_INDEX_LINK_COMMAND`).
7. "The ledger": an `actual` sync settlement keys on its message ID; an `estimated` one always
   keys `<intent>/<custom_id>`; a void settlement's is `<intent>/void` (revised by the verification
   read, finding 4).
8. "Resume": "the workspace's batches created after the intent's timestamp" is a client-side filter
   over newest-first pages, with a 10-minute margin for clock skew.

## Path minutes after the fold

| Pass | Design estimate | Path before | Path after | Ratio | 3x line |
|---|---|---|---|---|---|
| 1 | 120 | 175 | 225 | 1.9 | 360 |
| 2 | 180 | 285 | 355 | 2.0 | 540 |
| 3 | 180 | 275 | 315 | 1.75 | 540 |
| 4 | 180 | 205 | 285 | 1.6 | 540 |
| 5 | 240 | 465 | 620 | 2.6 | 720 |

No plan crosses Geoff's 3x stop line.

## Verification read

Read: `2026-10-13-drafter-completion-fold-verification.md` (passes 2 and 5, at `d64a88b`). Its
probes stand as evidence for the mechanisms they cover; the fold checked its finding 1 itself against
`messagebatch.go:346` ("Must be unique for each request within the Message Batch") and the spec's
stage 4 ("The structural edit, register editor, and fact read run in one batch").

- v-1 blocker folded: the `custom_id` form gains the seat
  (`<suffix>_<12 hex>_<stage>_<seat>_<attempt>`, `[a-z0-9]` tokens) and the state map names page and
  seat (P5 Interfaces); the fake rejects repeated `custom_id`s in one batch (P5 Interfaces, P2.5's
  fake); P5.1 asserts distinct IDs in stage-4 and stage-7 batches.
- v-2 major folded: a `Create` or `Send` error that proves no billing (a 4xx, `ErrSpendLimit`
  included; `ErrTransport`; `ErrNoWorkspaceCheck`) settles its intent `void` at once (P5.1 money
  path), with a row: a `Create` 400 escalates, leaves one `void` line, and `OpenIntents` is empty.
- v-3 major folded, with the coordinator's chosen fix: P5.8's rerun is drafter only, on the same
  Workflow run file and page; an input cause that needs another page ends the pass "not
  pilot-ready", and the PR asks Geoff to approve a second Workflow run (ruling 5 approves one).
  P5.8 and the executor prompt.
- v-4 minor folded: an `estimated` settlement always keys `<intent>/<custom_id>` (P2 Interfaces,
  P2.2 row); erratum 7 revised.
- v-5 minor folded: the intent fields and the `StateSchema` bump move to P5.1's Files
  (`internal/run/`); P5.2 keeps the resume fields.
- v-6 minor folded: a spend-limit 400 or 429 is `ErrSpendLimit` on every call, checked before the
  sync `errored` mapping (P2 Interfaces, P2.3 row).
- v-7 minor folded: P5.8's dry run runs under `bash -c '. ~/.local/secrets && ...'`.
- v-8 minor folded: P5.7 keys the Haiku price entry on the exact model ID the smoke sends, from
  `claude-api`'s model table.
- v-9 optional, folded (a one-row rephrase, clearly right): P2.2's row uses two requests of one
  batch intent, not a multi-request sync intent.

None refused. Path minutes: pass 2 stays 355 (text and row changes inside P2.2, P2.3, P2.5's
estimates); pass 5 rises to 620 (P5.1 from 200 to 210 for the void path, the seat-bearing IDs, and
the state fields moved in), 2.6 times its 240 estimate, under the 720 line. The blocker calls for
one more verification read under spec-plan-review.
