# drafter pass 3 plan: prompts and handoff

Design: `~/.dotfiles/docs/superpowers/specs/2026-10-13-drafter-completion-design.md`, pass 3,
approved by Geoff on 2026-10-13. Spec:
`~/.dotfiles/docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, sections "Seat prompts"
("Beside the chain" and "Checking the prompts"; "At cutover" is read for the module contract only),
"The handoff" (all of it), "The tool" (the `prompts` and `handoff` rows and `drafter
check-prompts`), and "Testing" (the handoff row). The dotfiles half builds the chain's three
`DRAFTER_HOST` pieces, `backHalf`, and the `// === HANDOFF ===` block. Fold record:
`~/.dotfiles/docs/superpowers/research/2026-10-13-drafter-completion-plan-fold.md`.

## Outcome

drafter runs the docs page chain's back-half prompt builders in goja and gets, for any seat and
context, the exact prompt the chain itself sends at that point. It decodes a planner's handoff file,
or the chain's Workflow run file, into one handoff struct whose checksum pins the plan and framing.
The chain gains `backHalf: "drafter"`, which stops after framing and returns the handoff, and the
dotfiles gate proves the goja and Node renderings agree byte for byte. With `backHalf` unset, the
chain sends every agent call exactly as it does today.

## Shape

- Risk class: `runner` (the chain and the dotfiles gate). The drafter tasks are `ordinary`.
- No `live-account` flag.
- Repos and branches:
  - `~/Projects/drafter` (`glw907/drafter`): the executor launches from the main checkout and works
    in the worktree `EnterWorktree` creates (name `p3-prompts-handoff`).
  - `~/.dotfiles` (`glw907/workstation`), through the `dotfiles-pass` adapter: the session creates
    `git -C ~/.dotfiles worktree add .claude/worktrees/drafter-prompts-handoff -b
    drafter-prompts-handoff origin/main` and edits only there, by path. `~/.claude/workflows` links
    into the dotfiles main checkout, so an edit there would change the live chain under cairn's
    sessions. Never touch the main checkout's uncommitted files. Dotfiles paths below are relative
    to that worktree.
- Gates: drafter, from the drafter worktree, `DRAFTER_DIR="$PWD" bash
  ~/.dotfiles/scripts/drafter-gate.sh`; dotfiles, `bash
  ~/.dotfiles/.claude/worktrees/drafter-prompts-handoff/scripts/gate.sh`, run with
  `DRAFTER_BIN=<drafter worktree>/drafter` after `make -C <drafter worktree> build`, so the gate's
  new leg uses this branch's binary and the installed one stays untouched. Each full-suite home is
  its gate, once, on the close head. No CI.
- Clock file: the drafter worktree's git dir.
- Path estimate: 315 minutes. P3.1 and P3.2 as a pair (100), P3.3 and P3.4 as a pair (130), P3.5
  (50), Close (35). The design's estimate is 180, so the path is 1.75 times it, inside the 3x line
  (540).
- Standing approvals: the plan proceeds within 3x. Two PRs go to Geoff through the conductor; the
  executor never merges.
- New dependency: `github.com/dop251/goja`, which tags no releases, at the pseudo-version of its
  newest `master` commit, taken in P3.1 through the `dependency-upgrade` skill's checks.
- Pair subagents run on `sonnet` at `medium` with the `description` `p3-prompts-handoff task <n>`.

## The contracts this pass fixes

Five executors build against these, across two repos. Each is fixed here; P3.4 documents the
JavaScript side in the chain's header comment and pass 5's docs task documents the drafter side.

### The seat context object

Every seat builder takes one object. drafter builds it (pass 5); the matrix fixtures carry it.

| Field | Holds |
|---|---|
| `page` | The page's config: the handoff context's `resolved.pages` entry whose `path` matches, else the handoff's `page` object, passed as raw JSON |
| `inputs` | The handoff's `inputs` as raw JSON, with `pageType` set to the handoff page's `type` when the planner gave none |
| `round` | `1`, `2`, or `"final"` (the redraft and scoped reads after the final reader's read) |
| `findings` | The numbered findings text a redraft answers, or `""` |
| `afterFinalRead` | `true` for the redraft after the final reader read, with `round` `"final"` |
| `scope`, `where` | The scope note and its location text for scoped reads, or `""` |
| `narrow` | `null`, or `{ baseline, own }` for a narrowed round-2 read: the round-1 snapshot's object ID and this seat's own round-1 read (`verdict`, `findings`, `summary`), `own` being `null` when the seat accepted with nothing to verify |
| `turn` | The final reader only: `1` for steps 1 and 2 with the page alone, `2` for step 3 with the job |
| `facts` | Whether the project has a facts store |

### The chain's drafter hooks

- `DRAFTER_HOST`, a global drafter defines: `{ resolved: { pages, index } }`.
- `resolvePages()` opens with the spec's line: under `DRAFTER_HOST` it returns `DRAFTER_HOST.resolved`.
- `DRAFTER_SEATS` maps `draft`, `structure`, `editor`, `fact`, and `reader` to functions of the
  context object, each adapting it to its builder with these mappings fixed, so an empty string
  never reaches a builder as a value the chain itself never passes: `where || undefined`,
  `scope || undefined`, and `narrow || undefined`. `draft` calls `draftPrompt` with round
  `c.round === 1 ? 1 : 2`, the findings, and `afterFinalRead` (never the snapshot instruction, since
  drafter keeps the snapshot itself); `structure` calls `structurePrompt` in page mode with
  `narrow`; `editor` and `fact` pass `scope`, `where`, and `narrow`; `reader` returns the first turn
  or the second.
- The reader split: `readerPrompt` is recomposed from two parts, steps 1 and 2, and step 3. The
  chain's own call joins them into exactly the prompt it renders today. Turn 1 is steps 1 and 2
  plus one sentence saying step 3 follows in the next turn. Turn 2 is step 3 with the page's job
  text inlined from `page.job` (the outline entry's job) and the page's path named. This is how
  drafter meets the spec's rule that the reader's first turn holds no job text: with an outline set,
  today's step 3 names the outline file, which drafter would otherwise inline.
- Just before the slot pool, under `DRAFTER_HOST`, the script returns `DRAFTER_SEATS`.

drafter's loader (P3.1) rewrites the line matching `(?m)^export const meta` to `const meta` (the
same anchor the outline test uses, `/^export const meta/m`), so a comment containing the phrase is
never touched. It wraps the script in an async function, adding nothing before line 1's text so line
numbers hold, and defines `args` (the handoff context's `args`), `DRAFTER_HOST`, no-op `phase`, `log`,
`parallel`, and `pipeline`, and an `agent` that fails the load if called. The host and the context
cross into goja as JSON text that the runtime parses (`JSON.parse`), never through `vm.Set` of a Go
struct, which would expose Go field names and turn `json.RawMessage` into a byte array (probed). After
the script runs, the async function's promise is settled: a fulfilled promise's value is the seat
map; a rejected one is a load error carrying the exception's message and its `.stack` line; one
still pending is a load error. A handoff with no `context.resolved` is refused at load with an
error naming the missing chain context, since the beside-the-chain loader can't run the chain
without it. A module written fresh, without the chain, is any script that runs under the same
wrapper and returns such a map; "At cutover"'s plain-script completion-value form is cutover work
and not loaded here (see "Later").

### `backHalf` and the chain's handoff

- `args.backHalf`: unset runs the chain as today; `"drafter"` refuses right after `resolvePages()`
  returns and before `reworkProbe()`, when any resolved page carries `figure: true` or a non-empty
  `rework`, naming each; any other value throws.
- Under `"drafter"`, each page stops after its framing step, and the script returns `{ handoff,
  escalated }`: `escalated` holds the records of pages that escalated before framing ended, and
  `handoff` holds the rest. drafter reads only `.result.handoff`.
- `handoffFor(args, resolved, worktree, entries)`, inside `// === HANDOFF ===` and `// === END
  HANDOFF ===` markers, is pure and self-contained, so a test extracts it alone. Each entry carries
  what the chain already computed for a framed page: the page config, its `pageInputs`, and its
  `brief`, `plan`, `framing`, and `registerSections` (from `briefPathFor`, `planPathFor`,
  `framingPathFor`, and `registerSectionsFor(track, "drafter")`, called by the caller). Its output,
  the chain handoff:

  ```json
  {
    "version": 1,
    "worktree": "/abs/worktree",
    "args": { "...": "the chain's args, verbatim" },
    "resolved": { "pages": ["...resolved page configs..."], "index": "docs/x/README.md" },
    "pages": [
      {
        "page": { "path": "docs/x/a.md", "brief": "docs/internal/briefs/x/a.json", "type": "task-guide" },
        "plan": "docs/internal/briefs/x/a.plan.yaml",
        "framing": "docs/internal/briefs/x/a.framing.md",
        "inputs": {
          "job": "...", "pageType": "task guide",
          "registerSections": ["## ..."], "exemplarSources": ["..."],
          "claimInventory": [{ "claim": "...", "disposition": "carried", "factId": "f:abc123", "section": "..." }],
          "factIds": ["f:abc123"]
        }
      }
    ]
  }
  ```

  `page.type` maps the chain's page type (`pageInputs.pageType || p.pageType`) in the order
  `readerPrompt` already branches: a type matching concept is `concept`; one matching task,
  tutorial, or how-to is `task-guide`; anything else is `reference`. `inputs.pageType` keeps the
  chain's own wording, so the drafter's prompt reads as it does under the chain.

### The handoff file

The spec's field table, with `inputs` fixed as the chain handoff's `inputs` object above
(`pageType` optional, `factIds` optional when the project has no facts store). `context`, when the
handoff came from the chain, is `{ "args": ..., "resolved": ... }`. The paths that must resolve
inside `project` are exactly `page.path`, `page.brief`, `plan`, and `framing`.
`inputs.exemplarSources` is exempt: the chain's are absolute paths under the exemplar root
(`cairn-docs-outline`'s `exemplarFile`), and pass 4's `inline_files` rule governs which of them
reach a request. This narrows the spec's "a path that resolves outside `project`" (owed erratum).
With no framing record, the checksum covers the plan's bytes alone.

## Interfaces

Consumes from pass 1: `config.Config`, `config.Load`.

Creates, for passes 4 and 5:

`internal/prompts`

- `type Host struct`: `Args`, `Resolved json.RawMessage`.
- `type Round`: a value that is `1`, `2`, or `"final"`, encoding and decoding as that JSON.
- `type Context struct`: the seat context object above, with JSON tags of the same names; `Page`
  and `Inputs` are `json.RawMessage`, `Round` is `Round`.
- `Load(name string, src []byte, h Host) (*Module, error)`: the loader above; the error names the
  module file and, for a JavaScript exception, its message and line.
- `(*Module) Render(seat string, c Context) (string, error)`: an unknown seat, a builder that throws,
  or a non-string result is an error.
- `(*Module) Seats() []string`.

`internal/handoff`

- `type Handoff struct`: `Version int`, `Project string`, `Page Page`, `Plan`, `Framing string`,
  `Inputs Inputs`, `Context json.RawMessage`, `Checksum string`, and `File string` (where it was
  read from, for errors; not decoded).
- `type Page struct` (`Path`, `Brief`, `Type`), `type Inputs struct` (`Job`, `PageType`,
  `RegisterSections`, `ExemplarSources`, `ClaimInventory []Claim`, `FactIDs`), `type Claim struct`
  (`Claim`, `Disposition`, `FactID`, `Reason`, `Section`).
- `ReadFiles(paths ...string) ([]Handoff, error)`: strict decode of each, then the refusals.
- `ReadWorkflowRun(path string) ([]Handoff, error)`: `.result.handoff` only, strict against the
  chain handoff's versioned struct, then the conversion the spec's "The chain's Workflow run file"
  gives, computing and recording each checksum. A run file with no `result`, a missing or null
  `.result.handoff`, or an empty `pages` list is refused, each with its own message naming the file.
- `(Handoff) Verify() error`: recomputes the checksum against the files on disk.
- `Checksum(project, plan, framing string) (string, error)`: `sha256:` and the hex SHA-256 of the
  plan's bytes followed by the framing's (the plan's alone when `framing` is empty), the same as
  `cat <plan> <framing> | sha256sum`.

## Out of scope

Request assembly, file inlining, and the answer schemas (pass 4); building the context objects and
running seats (pass 5); the cutover module form; prompt changes beyond the reader split; and any
chain behavior when `backHalf` is unset.

## Tasks

### P3.1 The prompts package (100 min, ordinary)

- Outcome: `internal/prompts` as listed, on goja. Invoke `go-conventions` first.
- Files: `internal/prompts/` with tests, `internal/prompts/testdata/` (a synthetic chain-shaped
  module: an `export const meta`, a header comment containing the words "export const meta", top-level
  `await` on a `resolvePages` that reads `DRAFTER_HOST`, builders with branches, and the early
  `return`), `go.mod`, `go.sum`.
- Acceptance: the synthetic module loads and renders each seat, and its header comment is unchanged;
  a module that calls `agent` at load fails the load naming `agent`; one that references `require`,
  `fetch`, `process`, `console`, or `setTimeout` fails with a `ReferenceError` (one row each,
  matching the spec's probe); a syntax error names its line; a load-time `throw` (a rejected promise)
  names its message and line; a module whose top level awaits a promise that never settles is a load
  error; a host with no `resolved` is refused naming the missing chain context; an unknown seat, a
  throwing builder, and a builder returning a number are each errors with a clean twin. `Render`
  passes the context's fields through unchanged: a builder that echoes `JSON.stringify(c)` returns
  the input, on a fixture that sets every field away from its zero value (`round: "final"`,
  `afterFinalRead: true`, a non-null `narrow` with `own.findings`, a nested `claimInventory`).
  The dependency check is in the PR body.
- Test: the drafter gate.
- Pair: with P3.2.

### P3.2 The handoff package (75 min, ordinary)

- Outcome: `internal/handoff` as listed. Invoke `go-conventions` first.
- Files: `internal/handoff/` with tests and `testdata/`: a synthetic project (a fictional tool's
  page, plan, and framing record, run in tests from a `git init` temp copy), a handoff file for it,
  and `chain-handoff.json`, the bare chain handoff in the shape above for the same page, which the
  test wraps as a Workflow run file (`{"args": ..., "result": {"handoff": ...}}`) in a temp
  directory after rewriting its `worktree` to the temp copy's root. No workstation path and no
  cairn text.
- Acceptance, the spec's handoff row, each refusal naming the file with a clean twin: a handoff file
  decodes; an unknown version, an unknown field, a `page.path`, `page.brief`, `plan`, or `framing`
  that resolves outside `project`, two handoffs naming different projects, and a checksum that
  doesn't match are refused; an `exemplarSources` entry outside `project` is accepted; a plan edited
  after decoding fails `Verify`; a handoff with no framing record checksums the plan alone. The run
  file converts to the same struct as the equivalent handoff file, `File` aside. A run file whose
  resolved page carries `figure: true`, and one whose page carries `rework`, are refused naming the
  page. An unknown field inside `.result.handoff` is refused; an unknown field elsewhere in the run
  file is ignored, since that is Claude Code's format. A run file with no `result`, with a null
  `.result.handoff`, and with empty `pages` are each refused with their own message. `Checksum`
  equals `sha256sum` over the concatenated files.
- Test: the drafter gate.
- Pair: with P3.1.

### P3.3 `drafter check-prompts` (55 min, ordinary)

- Outcome: `drafter check-prompts [--module <file>] --matrix <file> [--expect <file>|-] [--json]`.
  The module defaults to the project's `prompts` setting; with `--module`, no configuration loads.
  The matrix is a JSON object `{ host: { args, resolved }, cases: [{ name, seat, context }] }`. Each
  case renders, and must contain its context's `page.path` and, when the context has findings, the
  `findings` string whole and each `narrow.own.findings[].finding`. With `--expect`, a JSON object
  mapping case names to prompts, every case must equal its expected prompt byte for byte, and a name
  present on one side only fails. A failure prints the case, the check, and for a mismatch the first
  differing line with its number. Exit 0 when every case passes, 1 when any fails, 2 when the
  module, matrix, or expect file can't be read, parsed, or loaded, or the matrix has no cases.
- Files: `cmd/drafter/checkprompts.go`, `cmd/drafter/root.go`, `e2e/e2e_test.go`,
  `e2e/testdata/prompts/` (the synthetic module, a matrix, a matching expect file).
- Acceptance: e2e rows: the matrix passes (exit 0); an expect file with one byte changed fails that
  case and names the line (exit 1); a case whose context's findings the module drops fails the
  findings check (exit 1); a missing module, a malformed matrix, and a matrix with empty `cases` each
  exit 2 naming the problem; `--json` reports the same results.
- Test: the drafter gate.
- Pair: with P3.4. P3.3 goes to a subagent with `isolation: "worktree"`; P3.4 to a subagent without
  isolation, working the dotfiles worktree by path as its only writer, since worktree isolation
  covers only the repo the session launched from.

### P3.4 The chain's drafter hooks and handoff (130 min, runner)

- Outcome, in the dotfiles worktree only: everything "The chain's drafter hooks" and "`backHalf` and
  the chain's handoff" fix, plus the header comment documenting `backHalf`, `DRAFTER_HOST`, the
  context object, the adapter mappings, and the reader split. Before the first edit, record every
  `agent` call (label, prompt, and options) and the return object of two runs of today's chain
  through the outline test's runner, one with an outline and one without, with the temp worktree
  path replaced by a fixed placeholder and the stubbed `inputs` returning each page type in turn;
  save them under `tests/fixtures/docs-page-chain/` as the default-behavior snapshot.
- Files: `claude/.claude/workflows/docs-page-chain.js`, `tests/docs-page-chain-outline.test.mjs`,
  `tests/docs-page-chain-handoff.test.mjs` (new), `tests/fixtures/docs-page-chain/`,
  `tests/fixtures/drafter/chain-handoff.json` (a byte copy of P3.2's), `scripts/check.sh` (the
  handoff test's line).
- Acceptance:
  - With `backHalf` unset, the same two runs after the edits equal the snapshot byte for byte, and
    every existing case in both chain tests passes unchanged.
  - Fidelity: at each point the chain calls a back-half seat (the draft at round 1, round 2, and
    after the final read; the structural edit, register editor, and fact read at round 1, round 2
    narrowed, round 2 whole, and scoped after the final read; the final reader), the test builds the
    equivalent context object and asserts that `DRAFTER_SEATS[seat](context)` equals the prompt the
    chain sent there. Two documented exceptions: the round-2 draft is compared against the chain's
    call without the snapshot instruction, and the reader against its two parts.
  - The handoff test extracts the block by its markers (a missing or reordered marker fails), runs
    `handoffFor` on a recorded synthetic page, and deep-equals `tests/fixtures/drafter/chain-handoff.json`.
  - New runner cases: with `backHalf: "drafter"`, the run stops after framing, no draft, read, or
    reader agent is called, and the return holds `handoff` with one entry per framed page; a page
    escalated in the plan step lands in `escalated` and not in `handoff`; a page with `figure: true`
    and one with `rework` are refused, and the recorded agent calls are exactly `["outline"]` with an
    outline and none without one; `backHalf: "other"` throws.
  - With `DRAFTER_HOST` defined, the script returns an object whose keys are the five seats, and
    `agent` is called zero times.
- Test: the dotfiles gate.
- Pair: with P3.3.

### P3.5 The parity leg (50 min, runner)

- Outcome: the dotfiles gate proves goja renders the chain as Node does.
  `tests/drafter-render-prompts.mjs` loads the chain the way P3.1's loader does (the same anchored
  rewrite, wrapper, and globals) and prints the matrix's renderings as the expect object.
  `tests/fixtures/drafter/matrix.json` holds the spec's matrix: a task-guide, a concept, and a
  reference page, with an outline set, and for each page every seat at every point the chain calls
  it: the draft at round 1, round 2, and after the final read (`round: "final"`, `afterFinalRead:
  true`); the structural edit, register editor, and fact read at round 1, round 2 narrowed, and
  round 2 whole; the register editor and fact read scoped after the final read; and the reader's two
  turns. Every page, path, and finding in it is synthetic. `tests/drafter-prompts-parity.sh` fails
  with a clear message when `${DRAFTER_BIN:-drafter}` is absent, then pipes the renderer's output to
  `check-prompts --module claude/.claude/workflows/docs-page-chain.js --matrix
  tests/fixtures/drafter/matrix.json --expect -`. `scripts/check.sh` runs it. `scripts/gate.sh`
  passes `--fresh` to `cairn-run-gate` when `DRAFTER_BIN` is set: the gate's fingerprint covers the
  tree, lockfiles, lane, `E2E_PORT`, `CI`, and only the `CAIRN_*` names its string mentions
  (`cairn-run-gate` lines 157-180), so a rebuilt binary alone would otherwise replay the last result.
- Files: those three in the dotfiles worktree, `scripts/check.sh`, and `scripts/gate.sh`.
- Acceptance: the dotfiles gate passes with `DRAFTER_BIN` set to this branch's binary. The negative
  rows run `bash tests/drafter-prompts-parity.sh` directly, not through the gate: with `DRAFTER_BIN`
  pointing at a missing path the leg fails naming it; a deliberate one-character edit to a builder
  in a scratch copy makes the leg fail on the cases that builder renders (recorded, then reverted).
  `cmp` shows the two `chain-handoff.json` copies identical.
- Test: both gates.

### Close (35 min)

Both gates once on their close heads (the dotfiles one with `DRAFTER_BIN` set, so it runs fresh).
Two whole-branch `diff-reviewer` runs: drafter's branch against `main` (go-conventions for `*.go`)
and the dotfiles branch against `origin/main` (ts-conventions for `*.js` and `*.mjs`). One batched
fix chain, then the gates again; after any drafter rebuild the dotfiles gate reruns. The dotfiles
close checklist: `claude-tooling-sync verify`, and `gitleaks git` over each branch's history. If
`origin/main` in dotfiles moved `docs-page-chain.js` since the branch was cut, merge it in and rerun
the dotfiles gate before opening the PR.

Push and open two PRs, `glw907/drafter` first, then `glw907/workstation`, each body naming the
other. Each body opens with `## Brief`, then what landed, the review verdict, the score rows (on the
dotfiles PR; gate time from `~/.local/state/cairn-run-gate/runs.jsonl` records whose `gate` names
either worktree; the Work and review row puts the 315-minute path beside the actual), and "Found,
not done" with a proposed disposition each. The dotfiles PR carries a `## Before merge` section: the
drafter PR is merged, then `git -C ~/Projects/drafter pull --ff-only` and `make -C ~/Projects/drafter
install`; the check is `drafter check-prompts --help` exiting 0. The dotfiles merge is live at once
through Stow, and with `backHalf` unset the chain behaves as before. Stop at PR-ready; the conductor
takes both to Geoff.

## Later

- Load the plain-script prompts module form ("At cutover": a script whose completion value is the
  seat map) once a module exists in that form, with a host that needs no chain context.
- A dotfiles gate check that the two `chain-handoff.json` copies stay identical, if they ever drift.
