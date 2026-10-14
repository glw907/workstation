# drafter follow-ups plan: the triage "now" items

Design: Geoff's ruling of 2026-10-13 in conductor-drafter's session. The "now" items from the
triage of passes 1 and 2 run as one pass after pass 4 merges and before pass 5, whose live runs
use the spend ledger. The scope is exactly five `glw907/drafter` issues: #12, #17, #18, #19, and
#20. Read each with `gh issue view <n> -R glw907/drafter`. Initiative design, for context only:
`~/.dotfiles/docs/superpowers/specs/2026-10-13-drafter-completion-design.md`. The ledger's
contract is pass 2's plan, `2026-10-13-drafter-p2-money-plan.md`, section "Interfaces", the
`internal/ledger` rows.

## Outcome

Config loading and `drafter config` report the git failure that happened, not a wrong guess at
it. `batch.Client` exports nothing it holds only for tests, and its package doc says truthfully
what its errors carry. Ledger reads wait for a writer, so a read racing an append never sees a
half-written line. A crash at any point in the torn-tail repair leaves a ledger the next call
reads and repairs, never one that fails closed until hand-edited.

## Shape

- Risk class: `auth-data`, Geoff's ruling, since the pass touches `internal/ledger`, which decides
  whether money is spent. He ruled pass 2 `auth-data` on the same code. Every task is `auth-data`.
- Test-first on every task except F2, which changes no behavior: its tests are written and seen
  failing, then committed, before the code that passes them. A row marked "(guard)" passes today
  and stays green; every other row is red first. `diff-reviewer` at task scope reads every task's
  commit range against its acceptance. F1 gets the read because it rewrites `checkIgnored`, the
  fail-closed guard on a file that "can hold a key source and caps" (`internal/config/load.go`).
  A `fix` or `escalate` verdict stops the line until it is resolved. Never set `RUN_GATE_IF_BUSY`.
- No `live-account` flag: nothing calls an API.
- Repo: `~/Projects/drafter` (`glw907/drafter`). The executor, `drafter-followups`, launches from
  the main checkout and works in the worktree `EnterWorktree` creates (name `followups`). The pair
  subagents get worktrees of their own, dispatched on `sonnet` at `medium` with the `description`
  `followups task <n>`.
- Passes 3 and 4 merge between this plan and its launch, and may move nearby code. At launch, read
  each file a task names on current `main`, not as this plan quotes it. Where a name moved, follow
  the interface this plan states and say so in the PR body.
- Gate, from the worktree root: `DRAFTER_DIR="$PWD" bash ~/.dotfiles/scripts/drafter-gate.sh`,
  re-issued on exit 75. Full-suite home: that gate, once, on the close head. No CI.
- Clock file: the pass worktree's git dir.
- Path estimate: 150 minutes. F1 and F3 as a pair (60), with F2 (15) running in the session
  meanwhile, then F4 (55), then Close (35). The design states no estimate, so the path is the
  figure the clock and the score use.
- The PR goes to Geoff through the conductor. This pass never merges itself. The PR body says
  `Closes #12, #17, #18, #19, #20`.

## Interfaces

Public signatures stay as they are, with these changes that passes 4 and 5 can rely on.

- `plan.ErrNotGitTree` is new: `plan.GitRoot` wraps it when git ran and reported that the
  directory is outside a work tree, and only then.
- `plan.GitRoot`'s other failures are errors of their own: git could not run, or git's first
  standard error line (its exit status when stderr is empty). `drafter check-plan` prints today's
  message for `ErrNotGitTree` and the new error for the rest, at the same exit code.
- `batch.Client` has no exported fields. No caller outside `internal/batch` sets `Sleep` or `Now`
  today, and pass 5's plan names neither.
- `ledger.Ledger`'s read methods (`OpenIntents`, `Spend`, `PageSpend`) block while a writer holds
  `ledger.lock`. Writers hold it for one check and one append, never across a network call, so the
  wait is short.
- File states, replacing pass 2's row of that name: an absent or empty ledger reads as zero. A
  read never creates the state directory; in an existing one it creates `ledger.lock` (0600). The
  first append creates `state_dir` (0700) and the ledger (0600). Each append is one `write` on an
  `O_APPEND` descriptor, then `File.Sync`. A reader skips a final line with no newline (a torn
  write) with a warning; a writer truncates it away before appending (F4). Any other line that
  doesn't parse is an error naming the file and line, so `Reserve`, `Settle`, and `Spend` fail
  closed. The `torn` marker line type is retired: no writer emits it. A legacy marker line still
  parses and is ignored like any unknown type (`internal/ledger/store.go`, `state.add`), and the
  fragment line it once excused now fails closed.

## Out of scope

Everything outside the five issues. Other triage items stay where the triage filed them. The
smoke package's own `Params.Sleep` and `Params.Now` are not part of #17; if they look test-only,
that goes to "Found, not done".

## Tasks

Every task starts by invoking `go-conventions`.

### F2 The batch client's surface (15 min, auth-data)

Runs in the session while the pair runs. Its files are disjoint from F1's and F3's, so the
session dispatches the pair from the launch commit, then does F2.

- Outcome: issues #17 and #18. `Client.Sleep` and `Client.Now` become unexported fields, and the
  in-package tests set them under their new names. The package doc in `internal/batch/types.go`
  states what each kind of error carries. An API failure carries the status, error type, and
  message. A transport failure carries its cause. A request the client can't build (a message role
  that isn't `user` or `assistant`, or a schema that isn't a JSON object) is a plain error naming
  the request. No error holds an SDK error value. The executor reads every error path in the
  package and makes the doc match what it finds, not this list.
- Files: `internal/batch/client.go`, `internal/batch/types.go`, `internal/batch/helpers_test.go`.
- Acceptance: `go doc ./internal/batch Client` lists no exported field; the compiler enforces
  that nothing outside the package sets them. The `diff-reviewer` read checks every `return` of
  an error in the package against the doc's kinds, and that none wraps the `*anthropic.Error`
  that `inspect` unpacks (`internal/batch/failure.go`).
- Test: the gate. Test-first doesn't apply, since nothing new can fail first.

### F1 Accurate git failures (60 min, auth-data)

- Outcome: issue #12, in its two places and in `drafter spend`, which resolves its root the same
  way `drafter config` does.
  - `plan.GitRoot` runs git with `LC_ALL=C`, so git's messages are untranslated, and tells three
    failures apart. Git can't run (not on `PATH`): an error containing the phrase "git could not
    run". Git exits 128 and its first standard error line starts with one of the two
    not-a-repository forms git 2.56 prints, and only these: `fatal: not a git repository (or any of the parent directories)`
    (a ceiling directory) and `fatal: not a git repository (or any parent up to mount point`
    (a filesystem boundary): an error wrapping `plan.ErrNotGitTree`, with the message `drafter
    check-plan` prints today. Any other git failure (inside `.git`, `fatal: this operation must be
    run in a work tree`; a missing directory, `fatal: cannot change to`; a worktree whose
    repository moved): an error carrying git's first standard error line, or its exit status when
    stderr is empty. Before coding, probe the installed git's message for each case, the
    moved-repository worktree included, and record them in the commit message. If the
    moved-repository worktree prints one of the two allowlisted forms, stop and report it before
    coding, since the classifier would then send that worktree to the user layer.
  - `drafter config` and `drafter spend` treat only `plan.ErrNotGitTree` as "outside a project"
    and fall back to the user layer. Any other `GitRoot` error exits 1 with that error. Any other
    `plan.GitRoot(` caller on current `main` that falls back to the user layer does the same.
  - `config.checkIgnored` reads `git check-ignore`'s exit status as the man page defines it:
    "0 One or more of the provided paths is ignored. 1 None of the provided paths are ignored.
    128 A fatal error was encountered." (git-check-ignore(1), EXIT STATUS). It runs git under
    `LC_ALL=C` too. Exit 1 keeps today's "not ignored by git" refusal. Any other exit is refused
    with git's first standard error line (or the exit status when stderr is empty), and git that
    can't run is refused with the same phrase "git could not run". The refusal still fails
    closed in every case but exit 0.
- Files: `internal/plan/run.go`, a new `internal/plan/run_test.go`, `internal/config/load.go` and
  its tests, `cmd/drafter/config.go`, `cmd/drafter/spend.go`, `e2e/e2e_test.go`. Tests that set
  `PATH` or the locale use `t.Setenv`, so they don't call `t.Parallel`, and they build their git
  fixtures before stripping `PATH`.
- Acceptance, each row with a clean twin:
  - The classifier, as a table over git's first stderr line: both quoted not-a-repository forms
    wrap `ErrNotGitTree`; the work-tree, cannot-change-to, and moved-repository lines don't.
  - `GitRoot` in a temp directory outside any repo (set `GIT_CEILING_DIRECTORIES`) wraps
    `ErrNotGitTree`, and still does with `LANG=de_DE.UTF-8` and `LANGUAGE=de` set and `LC_ALL`
    and `LC_MESSAGES` cleared (git prints German on this host without `LC_ALL=C`; a comment says
    the row is vacuous on a host with no German catalog). With `PATH` holding no git, it doesn't wrap it, and the error says git could
    not run. Inside a fresh repo's `.git` directory, it doesn't wrap it, and the error holds git's
    message.
  - `Load` with a root holding `drafter.toml` and `drafter.local.toml` that isn't a git tree
    (`GIT_CEILING_DIRECTORIES` set): the error holds git's message and not the words "not
    ignored". With `PATH` holding no git, the error holds the phrase "git could not run" (today's
    error names the exec failure instead, `load.go`'s `check that %s is ignored`). In a real repo
    with the file unignored: today's message, unchanged (guard). Ignored: loads (guard).
  - e2e, on the complete user fixture (`completeUser`, so no unset setting exits 1 first):
    `drafter config` and `drafter spend` with `PATH` holding no git each exit 1 with `GitRoot`'s
    could-not-run phrase. Outside a git tree, each exits 0 on the user layer, as today (guard).
  - `drafter check-plan` outside a git tree prints the same message as before (guard).
  - The PR body lists every `plan.GitRoot(` caller on current `main` and how it treats
    `ErrNotGitTree`.
- Test: the gate.
- Pair: with F3.

### F3 The ledger lock for reads (50 min, auth-data)

- Outcome: issue #19. `OpenIntents`, `Spend`, and `PageSpend` take a shared `flock` (`LOCK_SH`) on
  `ledger.lock` for their read; `Reserve` and `Settle` keep the exclusive lock. The lock goes in
  the public read methods, never inside the internal `read`, which `Reserve` and `Settle` already
  call under the exclusive lock. flock(2): "If a process uses open(2) (or similar) to obtain more
  than one file descriptor for the same file, these file descriptors are treated independently by
  flock(). An attempt to lock the file using one of these file descriptors may be denied by a lock
  that the calling process has already placed via another file descriptor." So a nested lock would
  deadlock the process against itself. The read path never runs `MkdirAll`. It opens `ledger.lock`
  with `O_CREATE|O_RDONLY` (0600) and takes `LOCK_SH`; flock(2): "A shared or exclusive lock can be
  placed on a file regardless of the mode in which the file was opened." If the state directory
  is absent, the open fails with `ENOENT` and the read returns empty and creates nothing, since no
  ledger exists without its directory. Any other open error names the lock path. A present
  directory with no `ledger.lock` is the shape every e2e spend fixture and `TestFileStates` build;
  the read creates the lock there, so a writer that starts next locks the same file.
- Files: `internal/ledger/ledger.go`, `internal/ledger/store.go`, `internal/ledger/ledger_test.go`.
- Acceptance:
  - A writer mid-append: the ledger holds one complete line. The test opens `ledger.lock` on its
    own descriptor, takes `LOCK_EX`, and writes half a line to the ledger. The read, started in a
    goroutine, hasn't returned after 200 ms. The test completes the line and unlocks. The read
    then returns within 5 s (a `select` that fails with "blocked" otherwise), with a figure that
    includes that line, and `Warn` received nothing. The half-written line is a settle for `Spend`,
    whose `Total` counts only settles, and a reserve for `OpenIntents` and `PageSpend`. The
    red-first commit is the proof that the test fails without the read lock; the commit message
    cites it.
  - Readers share: with the test holding `LOCK_SH` on its own descriptor, `Spend` returns within
    5 s (the same bounded `select`) (guard).
  - `Spend` on a state directory that doesn't exist returns zero, and the directory still doesn't
    exist afterward (guard). The e2e row "a missing ledger prints a zero total and exits 0" stays
    green (guard).
  - `Spend` on a state directory that exists with no lock and no ledger returns zero, and
    `ledger.lock` then exists at 0600.
  - `Reserve` and `Settle` still work, and every existing ledger test passes, the two-process cap
    test included (guard).
- Test: the gate.
- Pair: with F1.

### F4 Crash-safe torn-tail repair (55 min, auth-data)

- Outcome: issue #20. A writer that finds a torn tail (a final fragment with no newline) truncates
  the ledger to the end of its last complete line, syncs the file, and only then appends. The offset
  is the byte after the last newline in the ledger the writer read under the same exclusive lock,
  so the dropped bytes hold no newline. The append goes on an `O_APPEND` descriptor. open(2): "the
  modification of the file offset and the write operation are performed as a single atomic step";
  truncate(2): "The file offset is not changed". A descriptor without `O_APPEND` writes past the
  new end and leaves NUL bytes (probed on btrfs). A truncate or sync error returns without
  appending. No torn marker line is written. The sync before the append fixes the order on disk.
  fsync(2): "a change to the file size (st_size, as made by say ftruncate(2)), would require a
  metadata flush". Assuming a crash leaves a prefix of the last append, it leaves the fragment
  (the repair runs again), the truncated file (which reads clean), or the truncated file with a
  torn new line (a fresh torn tail, repaired the same way). The warning names the file, the line,
  and the fragment's length in bytes. The reader's exception for a fragment followed by a
  marker goes. Every complete line that doesn't parse fails closed, naming the line, as the
  corrupt-middle-line test already requires.
- Before coding, confirm that no ledger holding a torn marker exists outside tests. No live run has
  happened (pass 5 makes the first), and `drafter config` names the `state_dir` to check. If one
  exists, stop and report it. The PR body records what the check found.
- Dropping the fragment is safe. A torn line never had a successful return: `append` returns only
  after its write and `File.Sync`. A torn reserve therefore had no submission behind it, and a torn
  settle is settled again by its caller's idempotent retry. Readers already skip the fragment
  today.
- Files: `internal/ledger/store.go`, `internal/ledger/ledger_test.go`.
- Acceptance:
  - Every crash point: start from a ledger with complete lines `C` and a torn fragment `F`. Run
    `Reserve(i2)` on a copy and take the final file `B`. The starting ledger `C` plus `F`, and a
    ledger holding `B[:k]` for every length `k` from `len(C)` to `len(B)`, each then take
    `Reserve(i3)`, `Settle(i3)`, and a `Spend` without error. The figures are hand-computed: `F`
    never counts, and `i2` shows in `PageSpend` and `Spend.Open` only at `k == len(B)`. The sweep
    runs over three variants:
    - `F` unparseable, a cut-off line like the torn-tail test's fragment. Against today's code
      this fails closed at `k == len(C) + len(F) + 1` (the fragment closed by a newline, the marker
      not yet written), which is #20's failure.
    - `F` a complete settle line with nonzero cost and no newline, so that "`F` never counts"
      shows in `Spend.Total`. Against today's code `F` parses once a newline closes it, so it
      counts from `k == len(C) + len(F) + 1` on, and the figures fail there.
    - The unparseable `F` with `C` empty.
  - A settle torn just before its newline (complete JSON) and then retried counts once. This is
    the existing test, kept (guard).
  - The rewritten torn-tail test: after the repair the fragment is gone from the file, the file
    holds no NUL byte, every line parses, and the warning names the file, the line, and the byte
    count.
  - A corrupt middle line still makes `Reserve`, `Settle`, and `Spend` fail naming the line
    (guard).
  - No test sees a missing sync, so the task-scope `diff-reviewer` brief names it: `Sync` follows
    `Truncate`, the append follows the `Sync`, and a truncate or sync error returns before the
    append.
- Test: the gate.

### Close (35 min)

The gate, once, on the close head. One whole-branch `diff-reviewer` run against `main`, with
go-conventions for `*.go`. It re-derives each task's class and confirms each task-scope verdict is
recorded. One batched fix chain if needed, each fix quoting its finding verbatim, then the gate
again, and a second review only on a blocker. `gitleaks git` over the branch history.

Push the branch to `glw907/drafter` and open the PR. The body opens with `## Brief`, written to
`~/.claude/docs/voice/approval-brief.md` (it must pass that contract). Below the brief come what
landed per issue, each task's `diff-reviewer` verdict, the git messages probed in F1, any name
that moved since this plan, and the score rows. Gate time comes from
`~/.local/state/cairn-run-gate/runs.jsonl` records whose `gate` names this worktree, and the Work
and review row puts the 150-minute path beside the actual. "Found, not done" carries a proposed
disposition on each item, and the body ends with `Closes #12, #17, #18, #19, #20`. It notes for
the merger: after the merge, `make -C ~/Projects/drafter install` on each host before its first
live run, since an older binary that meets a torn tail writes a marker this code fails closed on.
Stop at PR-ready; the conductor takes it to Geoff.

"Found, not done" starts with three items the plan review found, each outside the five issues:

- `GitRoot` and `checkIgnored` inherit `GIT_DIR`, `GIT_WORK_TREE`, and `GIT_INDEX_FILE` from the
  environment, so a `GIT_DIR` that points at another repo can make `check-ignore` accept an
  unignored `drafter.local.toml`. Proposed: a backlog issue, taken by the next pass that touches
  config loading.
- The ledger's first append doesn't fsync the state directory. fsync(2): "Calling fsync() does not
  necessarily ensure that the entry in the directory containing the file has also reached disk."
  Proposed: a backlog issue, low priority while one workstation is the only writer.
- Mutual exclusion depends on `ledger.lock` keeping its inode: removing or replacing the lock file
  while a holder runs splits the lock. Proposed: a sentence in the ledger's doc comment that
  nothing may remove the lock file, and no code change.

## Later

- A bounded wait on `ledger.lock`, carried from pass 2's "Later", if a stopped holder ever wedges
  a read or a run.
