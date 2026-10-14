# drafter pass 1 plan: foundations

Design: `docs/superpowers/specs/2026-10-13-drafter-completion-design.md`, pass 1, approved by Geoff
on 2026-10-13 with unattended planning and execution. Spec:
`docs/superpowers/specs/2026-10-12-drafter-pipeline-design.md`, sections "The tool" (the
`atomicfile`, `config`, and `run` rows, and `drafter config`), "Configuration" (all of it),
"Records" (run IDs, the run directory, retention), "Run inputs" (the state schema version), "One run
per worktree" (the locks), and "Testing" (the Configuration and Retention rows). The eight open
drafter issues (#2, #3, #4, #5, #7, #8, #9, #10) close here.

## Outcome

drafter loads its three configuration layers, resolves every setting with the source it came from,
and refuses what the spec refuses. `drafter config` prints the result. The `run` package hands later
passes run IDs, exclusive run directories, a versioned state file, locks, and retention. The plan
checker gains the eight fixes and additions its issues ask for, and `drafter anchors` lists the
anchors a Markdown file offers.

## Shape

- Risk class: `ordinary` for every task. No `live-account` flag: nothing calls an API.
- Repo: `~/Projects/drafter` (`glw907/drafter`, public). The executor launches from its main checkout
  and works in the worktree `EnterWorktree` creates (name `p1-foundations`); pair subagents get
  worktrees of their own with `isolation: "worktree"`.
- Gate, from the worktree root: `DRAFTER_DIR="$PWD" bash ~/.dotfiles/scripts/drafter-gate.sh`. It
  runs `make check` (vet, golangci-lint, tests) on the worktree through `cairn-run-gate` on the light
  lane, and re-issues on exit 75 the way the wrapper's header says. A pair subagent runs the same line
  from its own worktree.
- Full-suite home: that gate, once, on the close head. There is no CI and no watch command.
- Clock file: the pass worktree's git dir (`git rev-parse --absolute-git-dir` from the worktree).
- Path estimate: 175 minutes. The path is P1.1 and P1.2 as a pair (100), then P1.3 and P1.4 as a
  pair (55), then Close (20). The design's estimate is 120, so the path is 1.5 times it, inside
  the 3x line (360) that Geoff's standing approval sets.
- Standing approvals (design, "Technical notes"): a plan within 3x its estimate proceeds. This pass
  is `ordinary`, so it merges its own PR under pass-core's exception when the close review accepts
  and "Found, not done" is empty. A clock stop has no standing answer, so it stops as pass-core says.
- New dependency: `github.com/pelletier/go-toml/v2` at its newest release, taken through the
  `dependency-upgrade` skill's checks. It wins over `github.com/BurntSushi/toml` because the spec
  needs a line for every unknown key: go-toml's `Decoder.DisallowUnknownFields` returns a
  `StrictMissingError` whose `Errors` are `DecodeError`s, each with `Key()` and a 1-indexed
  `Position()`, while BurntSushi's `MetaData.Undecoded` lists keys with no position (pkg.go.dev for
  both, read 2026-10-13).

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
  `FailurePattern string`.
- `type Seat struct`: `Agent string` (an agent definition file, optional), `Model`, `Effort string`,
  `MaxTokens int64`, `Inputs []string` (command templates).
- `type Prices struct`: `Date`, `Source string`, `BatchDiscount float64`, `Models map[string]Price`.
- `type Price struct`: `Input`, `Output`, `CacheWrite5m`, `CacheWrite1h`, `CacheRead float64` (US
  dollars per million tokens), and `LongContext *Tier` for a model with a second tier.
- `type Tier struct`: `Threshold int64` (input tokens above which the tier applies) and the same five
  rates.
- `type Flags struct`: `Sync`, `JSON bool`, the only two settings with flags.
- `Load(root string, flags Flags) (*Config, error)`: reads the user layer, then, when `root` is not
  empty, `drafter.toml` and `drafter.local.toml` under it, then the environment and flags. The error
  is a refusal (see P1.2). `root` empty loads the user layer, environment, and flags only, for
  commands that run outside a project, such as `drafter spend`.
- `(*Config) Validate() error`: names every required setting that is unset and every running seat
  whose model has no price entry, in one error. Commands that spend or plan to spend call it.
- `(*Config) Sources() []Source`: one row per setting with its value and the layer, variable, or
  flag it came from, and for each cap every source that set it. It never carries a key.

`internal/run`

- `NewID(now time.Time) string`: a UTC timestamp plus a short random suffix, such as
  `20261013T142233Z-7f3a`.
- `Repo(root string) (string, error)`: the repo name runs and the ledger file under: the base name
  of the main checkout, the parent of `git rev-parse --git-common-dir`, so every worktree of one
  repo shares it.
- `PageKey(path string) string`: a page's directory name in a run, its repo-relative path with
  `.md` dropped and each `/` written as `--`.
- `Create(stateDir, repo, id string) (string, error)`: makes `runs/<repo>/<id>/` under `stateDir`
  exclusively and returns its path; an existing directory is an error.
- `type Lock`, `TryLock(path string) (*Lock, error)`, `(*Lock) Release() error`: a non-blocking
  `flock` that writes the holder's PID into the file. A busy lock's error names that PID.
- `type State struct`: `Schema int`, `DrafterVersion`, `RunID`, `Repo`, `Project`, `Branch`, `Head
  string`, `Stopped string` (the stop reason of a resumable run, empty otherwise), and `Pages
  map[string]*PageState` keyed by `PageKey`. `type PageState struct`: `Status string` (`running`,
  `held`, `accepted`, or `escalated`). Pass 5 adds fields to both; `StateSchema` is bumped then.
- `StateSchema` (a constant), `LoadState(dir string) (*State, error)` (refuses another schema with
  a message naming both versions), and `(*State) Save(dir string) error` (through `atomicfile`).
- `Prune(stateDir string, retentionDays int, now time.Time) ([]string, error)`: deletes run
  directories older than the retention whose every page is `accepted` or `escalated`, and returns
  what it deleted. It never touches `ledger.jsonl` or `ledger.lock`.

## Out of scope

The key, the API client, the ledger (pass 2); prompts and the handoff (pass 3); everything the
pipeline does with state beyond the fields above (pass 5); and drafter's configuration reference
page (pass 5's docs task). No setting gets a consumer here beyond `drafter config`.

## Tasks

Each task names its outcome, files, class, acceptance, and test. No implementation code; the spec's
sections and go-conventions govern the how. Every task starts by invoking `go-conventions`.

### P1.1 The eight plan-checker issues (85 min, ordinary)

- Outcome, in `internal/plan`, `cmd/drafter`, `schema/plan.schema.json`, and `docs/plan-format.md`:
  1. #2: `page.title` and every section `heading` get the plain-style line-comment refusal prose
     fields have.
  2. #3: a `link` target of just `#` is an error naming the line, with the fix "name an anchor or a
     path".
  3. #4: `page.path` that is absolute or climbs out with `..` is a decode finding.
  4. #5: `bracketRe` in `facts.go` becomes a `strings` call.
  5. #7: `failure` gains an optional `facts` list, resolved, checked as citable, and covered by the
     disposed-fact error, exactly as F1's `facts` on `reason`.
  6. #8: a `failure` whose `from` names a step that isn't `canFail` gets a warning.
  7. #9: `drafter anchors [--json] <file>...` prints every anchor a Markdown file offers, one per
     line, using check-plan's slugger. Raw HTML anchors count, in this command and in check-plan's
     anchor check: an `<a id="x">` or `<a name="x">` element anywhere in the file offers `x`. This
     settles the issue's open question on evidence: cairn's reference pages use `<a id>` anchors in
     table cells (for example `docs/reference/auth-channel.md`), and cairn's renderer passes raw
     HTML through, so a link to one works on the rendered page. The reference drops its "a raw-HTML
     heading isn't an anchor" limit for `<a>` elements and keeps it for raw-HTML headings.
  8. #10: the outline contract gains its optional parts: `pages[].slug` and a top-level
     `crossLinks` list of `{from, to, why}` slugs, the shape cairn's outlines carry. When the plan's
     page is an outline page, each cross-link `from` its slug that no `link` item targets (the `to`
     page's path, with or without an anchor) is a warning naming the `to` slug.
- Files: `internal/plan/{plan,decode,check,facts,outline,slug}.go` and their tests,
  `internal/plan/testdata/`, `schema/plan.schema.json`, `docs/plan-format.md`,
  `cmd/drafter/anchors.go`, `cmd/drafter/root.go`, `e2e/e2e_test.go`, `e2e/testdata/`.
- Acceptance: one failing row and one clean twin per item, with the expected line, for 1, 2, 3, 5,
  6, 7 (an `<a id>` target that passes and a misspelled one that fails), and 8 (a missing
  cross-link that warns; a present one, and an outline with no `crossLinks`, that don't). Item 4
  keeps `TestCheckTag` green. An e2e row runs `drafter anchors` on a fixture page with a heading,
  a repeated heading, and an `<a id>` element and matches the printed list; `--json` gives the same
  list as a JSON array. The schema sync test and the reference test pass. Each issue number appears
  in a commit message as `Fixes #N`, so the merge closes it.
- Test: the gate.
- Pair: with P1.2 (disjoint files; P1.2 alone touches `go.mod`).

### P1.2 atomicfile and config (100 min, ordinary)

- Outcome: `internal/atomicfile` and `internal/config` as "Interfaces this pass creates" lists them,
  with these rules from the spec's "Configuration":
  - Layers and order: flag, environment, `drafter.local.toml`, `drafter.toml`, user
    (`~/.config/drafter/config.toml`, honoring `XDG_CONFIG_HOME`). The project root is the `root`
    argument; callers pass `git rev-parse --show-toplevel`. Tables merge key by key, each key from
    the highest source that sets it; a list from a higher source replaces a lower one.
  - Environment: each scalar reads `DRAFTER_` plus its key upper-cased with dots as `_`
    (`DRAFTER_GATE_PROTOCOL`, `DRAFTER_RETRIES_GATE_FIX`). Tables and lists read none.
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
  - A `drafter.local.toml` that `git check-ignore -q` doesn't report as ignored is refused.
  - Defaults from the table: `mode` `batch`, `key_env` `DRAFTER_API_KEY`, `api_base_url`
    `https://api.anthropic.com`, `billing_cycle_day` `1`, `retention_days` `30`, `output` `human`,
    `pages_in_flight` `3`, both retries `2`, `gate.protocol` `plain`, `state_dir`
    `~/.local/state/drafter`, `seats` every seat. The seats are `draft`, `structure`, `editor`,
    `fact`, `reader`, `coverage`, and `consistency`; a `seats` list without `draft` is refused.
  - Value checks at load: `mode`, `output`, and `gate.protocol` take only their listed values;
    `gate.lane` is refused unless the protocol is `cairn-run-gate`; `billing_cycle_day` is 1 to 31;
    `gate.section_pattern` and `gate.failure_pattern` compile as Go regular expressions; a seat name
    outside the seven is refused.
  - `facts.bullet_format`: the spec names it without defining values. It accepts one value, `v1`,
    the bullet grammar `docs/plan-format.md` documents and check-plan already reads, and unset
    means the same. Any other value is refused. It exists so a later grammar has a place to go.
  - `register.<track>` is decoded, checked as a list of strings, and printed. No stage in this
    sub-project reads it; the handoff carries each page's register sections.
  - Command templates (`gate.command`, `index_link_command`, each seat's `inputs`) may use
    `{page}`, `{brief}`, `{slug}`, and `{baseline}`; any other `{name}` is refused at load.
    Substitution is pass 4's.
  - `Validate` requires `workspace_id`, `page_cap`, `cycle_ceiling`, `gate.command`, `prompts`, and
    for each running seat its `model`, `effort`, and `max_tokens`, and a price entry for each
    running seat's model. A seat's `agent` is optional, since the chain's structural edit, fact
    read, and final reader run on no agent definition.
- Files: `internal/atomicfile/`, `internal/config/` (with `testdata/`), `go.mod`, `go.sum`.
- Acceptance, the spec's Configuration testing row, each negative row asserting the exact error and
  line and paired with a clean twin:
  - One setting overridden at each layer (user, `drafter.toml`, `drafter.local.toml`, environment,
    flag) resolves to the highest, and `Sources` names that source.
  - A cap set at two layers resolves to the lower value whichever layer holds it, and `Sources`
    lists both.
  - A `drafter.toml` holding `key_command`, `key_env`, `workspace_id`, `prices`, or a cap is
    refused with the key and line.
  - A `drafter.toml` path outside the project is refused; a `drafter.local.toml` git doesn't ignore
    is refused (tests run `git init` in a temp dir); an unknown key is refused at each of the
    three layers.
  - `Validate` names a missing cap and a running seat whose model has no price.
  - A table merged across the project and local layers takes each key from the higher layer.
  - An `atomicfile` test shows a failed write leaves the old file intact.
  - The new dependency is at its newest release, and the PR body records the `dependency-upgrade`
    check.
- Test: the gate. Tests set the environment with `t.Setenv` and point the user layer at a temp
  directory through `XDG_CONFIG_HOME`.
- Pair: with P1.1.

### P1.3 The run package (55 min, ordinary)

- Outcome: `internal/run` as "Interfaces this pass creates" lists it.
- Files: `internal/run/` with tests.
- Acceptance, the spec's Retention row and the lock and state rules:
  - A finished run older than `retention_days` is pruned; a run with a `running` or `held` page is
    kept at any age; a run younger than the retention is kept; `ledger.jsonl` and `ledger.lock` in
    the state directory are untouched. The age comes from the run ID's timestamp.
  - `Create` on an existing run directory fails.
  - A second `TryLock` on a held lock fails with the holder's PID in the message (the test holds
    the lock from the same process through a second file descriptor), and succeeds after
    `Release`.
  - `LoadState` on a state written with another `Schema` refuses and names both versions; a round
    trip through `Save` and `LoadState` is lossless.
  - `NewID` matches its documented form; two IDs at the same instant differ.
  - `Repo` returns the same name from the main checkout and from a worktree of it (a temp repo with
    `git worktree add`).
- Test: the gate.
- Pair: with P1.4 (disjoint files).

### P1.4 `drafter config` (45 min, ordinary)

- Outcome: `drafter config [--json] [--sync]` loads the configuration for the project it runs in
  (`git rev-parse --show-toplevel`; outside a git tree, the user layer alone) and prints each
  setting as `key = value  (source)`, a cap with every source that set it, and `key_command` and
  `key_env` by value, never a key. `--json` prints the same rows as one array of objects (`key`,
  `value`, `source`, and `sources` for a cap). A refusal prints the refusal and exits 1. A missing
  required setting prints the full table, then `Validate`'s error, and exits 1.
- Files: `cmd/drafter/config.go`, `cmd/drafter/root.go`, `e2e/e2e_test.go`, `e2e/testdata/`.
- Acceptance: e2e rows on a synthetic project (a `git init` temp copy of a fixture with a
  `drafter.toml`, an ignored `drafter.local.toml`, and a user config under a temp
  `XDG_CONFIG_HOME`): the value and source of one setting set at every layer; a cap at two layers
  printed with both sources; `--json` parsing to the same rows; a `drafter.toml` with `key_command`
  printing the refusal with its line and exiting 1; a config missing `cycle_ceiling` exiting 1 and
  naming it. The binary is the one `TestMain` builds.
- Test: the gate.
- Pair: with P1.3.

### Close (20 min)

The gate, once, on the close head. One whole-branch `diff-reviewer` run against `main`, with
go-conventions for `*.go`. One batched fix chain if it finds anything, then the gate again.
`gitleaks git` over the branch history. Push the branch to `glw907/drafter` and open the PR. Its body
opens with `## Brief`, then what landed, the review verdict, the issues it closes, the score rows
pass-core names (the Work and review row puts the 175-minute path beside the actual), and "Found, not
done" with a proposed disposition for each item.

When the review accepted and "Found, not done" is empty, merge with `gh pr merge <n> -R
glw907/drafter --merge`, then `git -C ~/Projects/drafter pull --ff-only` (the main checkout is on
`main` with no session live in it) and `make -C ~/Projects/drafter install`, and check that `drafter
config --help` and `drafter anchors --help` exit 0. Otherwise stop at PR-ready and name the PR in the
final message; the conductor takes it to Geoff.

## Later

- A `drafter config --explain <key>` that prints a setting's allowed layers and default.
- Real values for `facts.bullet_format` once a second bullet grammar exists.
