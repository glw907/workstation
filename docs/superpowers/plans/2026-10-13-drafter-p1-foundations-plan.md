# drafter pass 1 plan: foundations

Design: `~/.dotfiles/docs/superpowers/specs/2026-10-13-drafter-completion-design.md`, pass 1, approved
by Geoff on 2026-10-13 with unattended planning and execution. Spec:
`~/.dotfiles/docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, sections "The tool" (the
`atomicfile`, `config`, and `run` rows, and `drafter config`), "Configuration" (all of it),
"Records" (run IDs, the run directory, retention), "Run inputs" (the state schema version), "One run
per worktree" (the locks), and "Testing" (the Configuration and Retention rows). The eight open
drafter issues (#2, #3, #4, #5, #7, #8, #9, #10) close here. Fold record:
`~/.dotfiles/docs/superpowers/research/2026-10-13-drafter-completion-plan-fold.md`.

## Outcome

drafter loads its three configuration layers, resolves every setting with the source it came from,
and refuses what the spec refuses. `drafter config` prints the result. The `run` package hands later
passes run IDs, exclusive run directories, a versioned state file, locks, and retention. The plan
checker gains the eight fixes and additions its issues ask for, and `drafter anchors` lists the
anchors a Markdown file offers.

## Shape

- Risk class: `ordinary` for every task. No `live-account` flag: nothing calls an API. Geoff's
  ruling (design, Technical notes 8): P1.2 stays `ordinary`, and its cap, layer-refusal, and
  ignore-check rows are written and committed before the code that passes them, and named in the
  close review's dispatch.
- Repo: `~/Projects/drafter` (`glw907/drafter`, public). The executor launches from its main checkout
  and works in the worktree `EnterWorktree` creates (name `p1-foundations`); pair subagents get
  worktrees of their own with `isolation: "worktree"`, dispatched on `sonnet` at `medium` with the
  `description` `p1-foundations task <n>`.
- Gate, from the worktree root: `DRAFTER_DIR="$PWD" bash ~/.dotfiles/scripts/drafter-gate.sh`. It
  runs `make check` (vet, golangci-lint, tests) on the worktree through `cairn-run-gate --fresh` on
  the light lane, and re-issues on exit 75 the way the wrapper's header says. A pair subagent runs
  the same line from its own worktree.
- Full-suite home: that gate, once, on the close head. There is no CI and no watch command.
- Clock file: the pass worktree's git dir (`git rev-parse --absolute-git-dir` from the worktree).
- Path estimate: 225 minutes. The path is P1.1 and P1.2 as a pair (130), then P1.3 and P1.4 as a
  pair (65), then Close (30). The design's estimate is 120, so the path is 1.9 times it, inside the
  3x line (360) that Geoff's standing approval sets.
- Standing approvals (design, "Technical notes"): a plan within 3x its estimate proceeds. This pass
  is `ordinary`, so it merges its own PR under pass-core's exception when the close review accepts
  and "Found, not done" is empty. A clock stop has no standing answer, so it stops as pass-core says.
- New dependency: `github.com/pelletier/go-toml/v2` at its newest release (v2.4.3 on 2026-10-13),
  taken through the `dependency-upgrade` skill's checks. It wins over `github.com/BurntSushi/toml`
  because the spec needs a line for every refused key. Strict mode returns a `StrictMissingError`
  whose `Errors` are `DecodeError`s, each with `Key()` and a 1-indexed `Position()`, for nested and
  map-of-struct tables; BurntSushi's `MetaData.Undecoded` lists keys with no position (probed by
  the plan review). For a known key that is refused (a disallowed layer, an out-of-project path, a
  bad value), the line comes from one pass of `go-toml/v2/unstable.Parser` over the file
  (`NextExpression`, `Expression().Key()`, `Shape(Range(...)).Start.Line`; `unstable/parser.go` in
  v2.4.3) that builds a key-to-line index, with its own test.

## Interfaces this pass creates

Later passes call these. Names and purposes are fixed; signatures may change only in ways that keep
every caller below compiling, and any change is stated in the PR body.

`internal/atomicfile`

- `WriteFile(path string, data []byte, perm fs.FileMode) error`: the go-conventions atomic write
  (temp file in the same directory, fsync, rename).

`internal/config`

- `type Config struct`: every resolved setting from the spec's settings table, typed. It includes
  `Prices Prices`, `BillingCycleDay int`, `WorkspaceID`, `KeyEnv`, `KeyCommand`, `APIBaseURL string`,
  `PageCap`, `CycleCeiling float64` (US dollars), `Mode string` (`batch` or `sync`), `StateDir
  string`, `RetentionDays int`, `Output string`, `PagesInFlight int`, `Retries Retries` (`GateFix`,
  `EditContract int`), `Gate Gate`, `Prompts string`, `Seats []string` (the seats that run, `draft`
  always among them), `Seat map[string]Seat`, `Facts Facts` (`Dir`, `BulletFormat string`), `Register
  map[string][]string`, `InlineFiles []string`, and `Root string` (the project root, empty outside a
  project). Every path is absolute after load.
- `type Gate struct`: `Command`, `IndexLinkCommand`, `Protocol`, `Lane`, `SectionPattern`,
  `FailurePattern string`. The TOML keys are `gate.command`, `gate.index_link_command`,
  `gate.protocol`, `gate.lane`, `gate.section_pattern`, and `gate.failure_pattern`.
- `type Seat struct`: `Agent string` (an agent definition file, optional), `Model`, `Effort string`,
  `MaxTokens int64`, `Inputs []string` (command templates).
- `type Prices struct`: `Date`, `Source string`, `BatchDiscount float64`, `Models map[string]Price`.
  `BatchDiscount` is the fraction taken off every rate in `batch` mode (0.5 for the published 50%),
  from 0 up to but not including 1; unset means 0, so a missing value overstates cost and never
  understates it. TOML: `[prices]` holds `date`, `source`, and `batch_discount`;
  `[prices.models."<model id>"]` holds `input`, `output`, `cache_write_5m`, `cache_write_1h`, and
  `cache_read`; `[prices.models."<model id>".long_context]` holds `threshold` and the same five rates.
- `type Price struct`: `Input`, `Output`, `CacheWrite5m`, `CacheWrite1h`, `CacheRead float64` (US
  dollars per million tokens), and `LongContext *Tier` for a model with a second tier.
- `type Tier struct`: `Threshold int64` and the same five rates. The tier applies to a request whose
  total input (input, cache-read, and cache-write tokens) is over `Threshold`, and its rates replace
  all five (pricing page, "Long context pricing", read 2026-10-13).
- `type Flags struct`: `Sync`, `JSON bool`, the only two settings with flags.
- `Load(root string, flags Flags) (*Config, error)`: reads the user layer, then, when `root` holds a
  `drafter.toml`, it and `drafter.local.toml` under it, then the environment and flags. Callers pass
  the git top level (`git rev-parse --show-toplevel`), or empty outside a git tree. A `root` with no
  `drafter.toml` is outside a project (`Config.Root` empty). The error is a refusal (see P1.2).
- `type Scope int` with `ScopeMoney` and `ScopeRun`, and `(*Config) Validate(s Scope) error`: one
  error naming every problem in scope. `ScopeMoney` requires `workspace_id`, `page_cap`, and
  `cycle_ceiling`; it serves commands that resolve money settings outside a project (`drafter
  config` outside one, pass 2's smoke). `ScopeRun` adds `gate.command`, `prompts`, and for each
  running seat its `model`, `effort`, `max_tokens`, and a price entry for its model; it serves
  `drafter page`. The `consistency` seat is required only when `facts.dir` is set.
- `(*Config) Sources() []Source`: one row per setting with its value and the layer, variable, or
  flag it came from, and for each cap every source that set it. It never carries a key.

`internal/run`

- `NewID(now time.Time) string`: a UTC timestamp plus 8 hex characters from `crypto/rand`, such as
  `20261013T142233Z-7f3a09c1`.
- `Repo(root string) (string, error)`: the repo name runs and the ledger file under: the base name
  of the main checkout, the parent of `git rev-parse --path-format=absolute --git-common-dir`, so
  every worktree of one repo shares it.
- `PageKey(path string) string`: a page's directory name in a run, its repo-relative path with
  `.md` dropped and each `/` written as `--`.
- `Create(stateDir, repo, id string) (string, error)`: makes `runs/<repo>/<id>/` under `stateDir`
  exclusively and returns its path; an existing directory is an error.
- `type Lock`, `TryLock(path string) (*Lock, error)`, `(*Lock) Release() error`: a non-blocking
  `flock`. `TryLock` opens without truncating, takes the lock, then truncates and writes the
  holder's PID; a busy lock's error names the PID in the file. `Release` unlocks and closes and
  never removes the file. flock(2): descriptors "are treated independently by flock()", so a second
  descriptor in one process is refused.
- `type State struct`: `Schema int`, `DrafterVersion`, `RunID`, `Repo`, `Project`, `Branch`, `Head
  string`, `Stopped string` (the stop reason of a resumable run, empty otherwise), and `Pages
  map[string]*PageState` keyed by `PageKey`. `type PageState struct`: `Status string` (`pending`,
  `running`, `held`, `accepted`, or `escalated`). Pass 5 lists every page of a run as `pending` at
  start, adds fields to both, and bumps `StateSchema`.
- `StateSchema` (a constant), `LoadState(dir string) (*State, error)` (refuses another schema with
  a message naming both versions; a missing or malformed file is an error naming the path), and
  `(*State) Save(dir string) error` (through `atomicfile`).
- `Prune(stateDir string, retentionDays int, now time.Time) ([]string, error)`: deletes run
  directories older than the retention whose state has no `Stopped` reason and whose every page is
  `accepted` or `escalated`, and returns what it deleted. A directory whose name isn't a run ID, or
  whose state is absent, malformed, or of another schema, is kept and skipped, never an error. A
  missing `stateDir` or `runs/` returns nil. It never touches `ledger.jsonl` or `ledger.lock`.

## Out of scope

The key, the API client, the ledger (pass 2); prompts and the handoff (pass 3); everything the
pipeline does with state beyond the fields above (pass 5); and drafter's configuration reference
page (pass 5's docs task). No setting gets a consumer here beyond `drafter config`.

## Tasks

Each task names its outcome, files, class, acceptance, and test. No implementation code; the spec's
sections and go-conventions govern the how. Every task starts by invoking `go-conventions`.

### P1.1 The eight plan-checker issues (95 min, ordinary)

- Outcome, in `internal/plan`, `cmd/drafter`, `schema/plan.schema.json`, and `docs/plan-format.md`:
  1. #2: `page.title` and every section `heading` get the plain-style line-comment refusal prose
     fields have.
  2. #3: a `link` target of just `#` is an error naming the line, with the fix "name an anchor or a
     path".
  3. #4: a `page.path` for which `filepath.IsLocal` is false (absolute, or climbing out, including
     `docs/../../x`) is a decode finding.
  4. #5: `bracketRe` in `facts.go` becomes a `strings` call.
  5. #7: `failure` gains an optional `facts` list, resolved, checked as citable, and covered by the
     disposed-fact error, exactly as F1's `facts` on `reason`.
  6. #8: a `failure` whose `from` names a step that isn't `canFail` gets a warning.
  7. #9: `drafter anchors [--json] <file>...` prints every anchor a Markdown file offers, one per
     line, using check-plan's slugger. Raw HTML `<a id="x">` elements count, in this command and in
     check-plan's anchor check, detected from goldmark's `RawHTML` and `HTMLBlock` nodes, so an
     element inside a code span or fence never counts. `<a name>` does not count: the sanitizer
     cairn's site uses clobbers `id` and `name` with `user-content-`, and cairn.pub's
     `stripAnchorClobberPrefix` (`src/lib/docs/link-policy.ts:93-102`) strips the prefix from `id`
     only, so only `<a id>` anchors work on the rendered page. cairn's reference pages use `<a id>`
     anchors in table cells (39 in its docs on 2026-10-13, none `<a name>`). The reference drops its
     "a raw-HTML heading isn't an anchor" limit for `<a id>` elements and keeps it for raw-HTML
     headings. A missing file is an error naming it (exit 1); a file with no anchors prints nothing
     (`[]` with `--json`) and exits 0.
  8. #10: the outline contract gains its optional parts: `pages[].slug` and a top-level
     `crossLinks` list of `{from, to, why}`. A `from` or `to` is a slug or a repo-relative path, the
     shapes cairn's outlines carry (`extend.json` has `"to": "docs/reference/README.md"`;
     `claude-code.json`'s `to` slugs live in `extend.json`). Slugs resolve across every `--outline`
     given. When the plan's page is an outline page, each cross-link from it that no `link` item
     targets (the `to` page's path, with or without an anchor) is a warning naming the `to`. A `to`
     that resolves to no page is a warning, never an error.
- Files: `internal/plan/{plan,decode,check,facts,outline,slug}.go` and their tests,
  `internal/plan/testdata/`, `schema/plan.schema.json`, `docs/plan-format.md`,
  `cmd/drafter/anchors.go`, `cmd/drafter/root.go`, `e2e/e2e_test.go`, `e2e/testdata/`.
- Acceptance: one failing row and one clean twin per item, with the expected line, for 1, 2, 3
  (including `docs/../../x`), 5, 6, 7 (an `<a id>` target that passes, a misspelled one that fails,
  an `<a id>` inside a fence that doesn't count, and an `<a name>` that doesn't count), and 8 (a
  missing cross-link that warns; a present one, and an outline with no `crossLinks`, that don't; a
  cross-link whose `to` is a repo path; one whose `to` slug lives in a second outline; an
  unresolvable `to` that warns). Item 4 keeps `TestCheckTag` green. An e2e row runs `drafter
  anchors` on a fixture page with a heading, a repeated heading, and an `<a id>` element and matches
  the printed list; `--json` gives the same list as a JSON array; a missing file exits 1. The schema
  sync test and the reference test pass. Each issue number appears in a commit message as
  `Fixes #N`, so the merge closes it.
- Test: the gate.
- Pair: with P1.2 (disjoint files; P1.2 alone touches `go.mod`).

### P1.2 atomicfile and config (130 min, ordinary; refusal rows first)

- Order: the cap, layer-refusal, and ignore-check rows below are written and committed failing before
  the code (Geoff's ruling 8), then the rest.
- Outcome: `internal/atomicfile` and `internal/config` as "Interfaces this pass creates" lists them,
  with these rules from the spec's "Configuration":
  - Layers and order: flag, environment, `drafter.local.toml`, `drafter.toml`, user
    (`~/.config/drafter/config.toml`, honoring `XDG_CONFIG_HOME`). A `root` without a
    `drafter.toml` is outside a project, and a `drafter.local.toml` there is refused naming it.
    Tables merge key by key, each key from the highest source that sets it; a list from a
    higher source replaces a lower one. An empty or malformed TOML file is refused naming the file
    and, for a parse error, the line.
  - Environment: top-level scalars, `retries.*`, `gate.*`, and `facts.*` read `DRAFTER_` plus the
    key upper-cased with dots as `_` (`DRAFTER_GATE_PROTOCOL`, `DRAFTER_RETRIES_GATE_FIX`,
    `DRAFTER_GATE_INDEX_LINK_COMMAND`). The money and credentials scalars (`key_command`, `key_env`,
    `api_base_url`, `state_dir`, `workspace_id`, `billing_cycle_day`, both caps) read theirs too.
    `seat.*`, `prices.*`, `register.*`, and every list read none. An empty variable counts as unset.
    A malformed value (a non-number cap) is refused naming the variable. A relative path from the
    environment resolves from the working directory. Any other `DRAFTER_*` variable is ignored, so
    `DRAFTER_API_KEY` and `DRAFTER_DIR` don't collide.
  - Caps: `page_cap` and `cycle_ceiling` resolve to the lowest value any source sets, environment
    included.
  - Allowed layers per setting as the spec's table gives them. A setting in a layer the table
    doesn't allow is refused naming the key, its line, the file, and the file to move it to. For
    `drafter.toml` that covers every money and credentials setting (`prices`, `billing_cycle_day`,
    `workspace_id`, `key_env`, `key_command`, `api_base_url`, both caps, `state_dir`,
    `inline_files`). `state_dir` is refused in `drafter.local.toml` too.
  - Strict decoding at every layer: an unknown key is refused with the file and line, through
    go-toml's strict mode.
  - Every path in `drafter.toml` (`prompts`, each seat's `agent`, `facts.dir`) must resolve inside
    the project, or it is refused with the key and line. Relative paths resolve from the file's
    directory; `~` expands in the user and local layers.
  - A `drafter.local.toml` for which `git check-ignore -q` exits nonzero is refused. A tracked file
    exits 1 even when `.gitignore` lists it (probed), so a clone that commits both the file and an
    ignore line is refused; `--no-index` is never used.
  - Defaults from the table: `mode` `batch`, `key_env` `DRAFTER_API_KEY`, `api_base_url`
    `https://api.anthropic.com`, `billing_cycle_day` `1`, `retention_days` `30`, `output` `human`,
    `pages_in_flight` `3`, both retries `2`, `gate.protocol` `plain`, `state_dir`
    `~/.local/state/drafter`, `seats` every seat. The seats are `draft`, `structure`, `editor`,
    `fact`, `reader`, `coverage`, and `consistency`; a `seats` list without `draft` is refused.
  - Value checks, each refused with the key and line (or the variable): `mode`, `output`, and
    `gate.protocol` take only their listed values; `billing_cycle_day` is 1 to 31; caps are above 0;
    `pages_in_flight`, `retention_days`, and each seat's `max_tokens` are at least 1; retries are at
    least 0; `prices.batch_discount` is from 0 up to but not including 1; a seat name outside the
    seven is refused; `gate.section_pattern` and `gate.failure_pattern` compile as Go regular
    expressions, and `gate.section_pattern` has at least one capture group. Checks that span
    layers run on resolved values: `gate.lane` is refused unless the resolved protocol is
    `cairn-run-gate`.
  - `facts.bullet_format`: the spec names it without defining values. It accepts one value, `v1`,
    the bullet grammar `docs/plan-format.md` documents and check-plan already reads, and unset
    means the same. Any other value is refused. It exists so a later grammar has a place to go.
  - `register.<track>` is decoded, checked as a list of strings, and printed. No stage in this
    sub-project reads it; the handoff carries each page's register sections.
  - Command templates (`gate.command`, `gate.index_link_command`, each seat's `inputs`) may use the
    placeholders `{page}`, `{brief}`, `{slug}`, and `{baseline}`. A placeholder is `{` plus an
    identifier plus `}` not preceded by `$`, so a shell `${arm}` and an awk `'{print $1}'` are left
    alone; any other identifier in that form is refused at load. Substitution is pass 4's.
  - `Validate(scope)` as the Interfaces section gives it.
- Files: `internal/atomicfile/`, `internal/config/` (with `testdata/`), `go.mod`, `go.sum`.
- Acceptance, the spec's Configuration testing row, each negative row asserting the exact error and
  line and paired with a clean twin:
  - Written first: a cap set at two layers resolves to the lower value whichever layer holds it, and
    `Sources` lists both; a cap set lower in the environment wins; a `drafter.toml` holding
    `key_command`, `key_env`, `workspace_id`, `prices`, or a cap is refused with the key and line; a
    tracked `drafter.local.toml` that `.gitignore` also lists is refused; an untracked, unlisted one
    is refused; an untracked, listed one loads. Tests run `git init` in a temp dir with
    `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, and author and committer variables set.
  - One setting overridden at each layer (user, `drafter.toml`, `drafter.local.toml`, environment,
    flag) resolves to the highest, and `Sources` names that source.
  - A `drafter.toml` path outside the project is refused; an unknown key is refused at each of the
    three layers; a placeholder `{other}` is refused, and a template holding `${arm}` and
    `'{print $1}'` loads.
  - An empty `DRAFTER_PAGE_CAP` counts as unset; `DRAFTER_PAGE_CAP=abc` is refused naming the
    variable; `DRAFTER_API_KEY` set to anything changes no setting.
  - One row per value check above.
  - `Validate(ScopeMoney)` names a missing cap and passes with no `gate.command`;
    `Validate(ScopeRun)` names a missing `prompts` and a running seat whose model has no price, and
    asks for a `consistency` seat only when `facts.dir` is set.
  - A table merged across the project and local layers takes each key from the higher layer.
  - `atomicfile`: a write that fails after the temp file is written (the target is a non-empty
    directory) leaves the old file intact and no temp file behind; a successful write's mode equals
    `perm`.
  - The key-to-line index has its own row: a key in a nested table and one in a quoted
    map-of-struct table (`[prices.models."claude-haiku-5-5"]`) report the right line.
  - The new dependency is at its newest release, and the PR body records the `dependency-upgrade`
    check.
- Test: the gate. Tests set the environment with `t.Setenv`, clear every `DRAFTER_*` variable
  first, and point the user layer at a temp directory through `XDG_CONFIG_HOME`.
- Pair: with P1.1.

### P1.3 The run package (65 min, ordinary)

- Outcome: `internal/run` as "Interfaces this pass creates" lists it.
- Files: `internal/run/` with tests.
- Acceptance, the spec's Retention row and the lock and state rules:
  - A finished run older than `retention_days` is pruned; a run with a `pending`, `running`, or
    `held` page is kept at any age; a run with `Stopped` set is kept at any age, even when every
    page is `accepted`; a run younger than the retention is kept; a directory whose name isn't a
    run ID, and runs whose state is absent, malformed, or of another schema, are kept with no error;
    a missing `stateDir` returns nil; `ledger.jsonl` and `ledger.lock` in the state directory are
    untouched. The age comes from the run ID's timestamp.
  - `Create` on an existing run directory fails.
  - A second `TryLock` on a held lock fails with the holder's PID in the message (the test holds
    the lock from the same process through a second file descriptor), and succeeds after
    `Release`; the lock file still exists after `Release`.
  - `LoadState` on a state written with another `Schema` refuses and names both versions; on a
    missing and on a malformed file it errors naming the path; a round trip through `Save` and
    `LoadState` is lossless.
  - `NewID` matches its documented form; two IDs at the same instant differ.
  - `Repo` returns the same name from the main checkout and from a worktree of it (a temp repo with
    `git worktree add`, under the same git environment as P1.2's tests).
- Test: the gate.
- Pair: with P1.4 (disjoint files).

### P1.4 `drafter config` (50 min, ordinary)

- Outcome: `drafter config [--json] [--sync]` loads the configuration for the project it runs in
  (the git top level when it holds a `drafter.toml`; otherwise, or outside a git tree, the user
  layer alone) and prints each setting as `key = value  (source)`, a cap with every source that set
  it, and `key_command` and `key_env` by value, never a key. Output follows the resolved `output`
  setting; `--json` sets it. JSON prints the same rows as one array of objects (`key`, `value`,
  `source`, and `sources` for a cap). A refusal prints the refusal and exits 1. A problem
  `Validate` finds prints the full table, then the error, and exits 1; inside a project the scope is
  `ScopeRun`, outside one `ScopeMoney`.
- Files: `cmd/drafter/config.go`, `cmd/drafter/root.go`, `e2e/e2e_test.go`, `e2e/testdata/`.
- Acceptance: e2e rows on a synthetic project (a `git init` temp copy of a fixture with a
  `drafter.toml`, an ignored `drafter.local.toml`, and a user config under a temp
  `XDG_CONFIG_HOME`): the value and source of `mode` set at every layer; a cap at two layers
  printed with both sources; `--json` parsing to the same rows; a `drafter.toml` with `key_command`
  printing the refusal with its line and exiting 1; a config missing `cycle_ceiling` exiting 1 and
  naming it; run outside any git tree with a complete user layer, exit 0. The binary is the one
  `TestMain` builds, and the e2e `run` helper passes an environment with every `DRAFTER_*` variable
  stripped and `XDG_CONFIG_HOME` and `HOME` set to temp directories.
- Test: the gate.
- Pair: with P1.3.

### Close (30 min)

The gate, once, on the close head. One whole-branch `diff-reviewer` run against `main`, with
go-conventions for `*.go`; its dispatch names P1.2's written-first rows (caps, layer refusals, the
ignore check) for a read of their own (ruling 8). One batched fix chain if it finds anything, then
the gate again. `gitleaks git` over the branch history.

The cairn regression check: build the branch binary (`make -C <worktree> build`) and run `drafter
check-plan --facts docs/internal/facts` with one `--outline` per file in `docs/internal/outlines/`
(the flag repeats) from `~/Projects/cairn-cms` on each of the 11 `docs/internal/briefs/**/*.plan.yaml`,
read-only, then the same with the installed binary. Any error the branch binary reports that the
installed one doesn't goes to "Found, not done", which blocks the self-merge.

Push the branch to `glw907/drafter` and open the PR. Its body opens with `## Brief`, then what
landed, the review verdict, the issues it closes, that the missing-price check moved into
`Validate`, the score rows pass-core names, and "Found, not done" with a proposed disposition for
each item. Gate time for the score comes from `~/.local/state/cairn-run-gate/runs.jsonl` records
whose `gate` names this worktree's path, since `drafter-gate.sh` runs from `~/.dotfiles` and
`--records <drafter worktree>` finds nothing. The Work and review row puts the 225-minute path
beside the actual.

When the review accepted and "Found, not done" is empty, merge with `gh pr merge <n> -R
glw907/drafter --merge`, then `git -C ~/Projects/drafter pull --ff-only` (the main checkout is on
`main` with no session live in it) and `make -C ~/Projects/drafter install`, and check that `drafter
config --help` and `drafter anchors --help` exit 0. Otherwise stop at PR-ready and name the PR in the
final message; the conductor takes it to Geoff.

## Later

- A `drafter config --explain <key>` that prints a setting's allowed layers and default.
- Real values for `facts.bullet_format` once a second bullet grammar exists.
