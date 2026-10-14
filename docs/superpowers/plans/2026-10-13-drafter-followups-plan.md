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
  whether money is spent. He ruled pass 2 `auth-data` on the same code. Per task: F1 `ordinary`,
  F2, F3, and F4 `auth-data`.
- Test-first on every task except F2, which changes no behavior: its tests are written and seen
  failing, then committed, before the code that passes them. `diff-reviewer` at task scope reads
  F2, F3, and F4's commit ranges against their acceptance. A `fix` or `escalate` verdict stops the
  line until it is resolved. Never set `RUN_GATE_IF_BUSY`.
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
- Path estimate: 150 minutes. F2 (15), F1 and F3 as a pair (50), F4 (50), Close (35). The design
  states no estimate, so the path is the figure the clock and the score use.
- The PR goes to Geoff through the conductor. This pass never merges itself. The PR body says
  `Closes #12, #17, #18, #19, #20`.

## Interfaces

Public signatures stay as they are, with three changes that passes 4 and 5 can rely on.

- `plan.ErrNotGitTree` is new: `plan.GitRoot` wraps it when git ran and reported that the
  directory is outside a work tree, and only then.
- `batch.Client` has no exported fields. No caller outside `internal/batch` sets `Sleep` or `Now`
  today, and pass 5's plan names neither.
- `ledger.Ledger`'s read methods (`OpenIntents`, `Spend`, `PageSpend`) block while a writer holds
  `ledger.lock`. Writers hold it for one check and one append, never across a network call, so the
  wait is short. The `torn` marker line type is retired: no writer emits it and no reader accepts
  it.

## Out of scope

Everything outside the five issues. Other triage items stay where the triage filed them. The
smoke package's own `Params.Sleep` and `Params.Now` are not part of #17; if they look test-only,
that goes to "Found, not done".

## Tasks

Every task starts by invoking `go-conventions`.

### F2 The batch client's surface (15 min, auth-data)

Runs first, in the session, before the pair.

- Outcome: issues #17 and #18. `Client.Sleep` and `Client.Now` become unexported fields, and the
  in-package tests set them under their new names. The package doc in `internal/batch/types.go`
  states what each kind of error carries. An API failure carries the status, error type, and
  message. A transport failure carries its cause. A request the client can't build (a message role
  that isn't `user` or `assistant`, or a schema that isn't a JSON object) is a plain error naming
  the request. No error holds an SDK error value. The executor reads every error path in the
  package and makes the doc match what it finds, not this list.
- Files: `internal/batch/client.go`, `internal/batch/types.go`, `internal/batch/helpers_test.go`.
- Acceptance: `go doc ./internal/batch Client` lists no exported field. A grep of the repo
  outside `internal/batch` finds no use of the two fields. The `diff-reviewer` read checks every
  `return` of an error in the package against the doc's kinds.
- Test: the gate. Test-first doesn't apply, since nothing new can fail first.

### F1 Accurate git failures (50 min, ordinary)

- Outcome: issue #12, in its two places and in `drafter spend`, which resolves its root the same
  way `drafter config` does.
  - `plan.GitRoot` runs git with `LC_ALL=C`, so git's messages are untranslated, and tells three
    failures apart. Git can't run (not on `PATH`): an error saying git could not run. Git ran and
    reported that the directory is not in a git repository: an error wrapping
    `plan.ErrNotGitTree`, with the message `drafter check-plan` prints today. Any other git failure
    (an exit 128 with another message, such as running inside `.git`): an error carrying git's
    first standard error line. Before coding, probe the installed git's messages for each case and
    record them in the commit message.
  - `drafter config` and `drafter spend` treat only `plan.ErrNotGitTree` as "outside a project"
    and fall back to the user layer. Any other `GitRoot` error exits 1 with that error.
  - `config.checkIgnored` reads `git check-ignore`'s exit status as the man page defines it:
    "0 One or more of the provided paths is ignored. 1 None of the provided paths are ignored.
    128 A fatal error was encountered." (git-check-ignore(1), EXIT STATUS). Exit 1 keeps today's
    "not ignored by git" refusal. Any other exit is refused with git's first standard error line,
    and git that can't run is refused naming that. The refusal still fails closed in every case
    but exit 0.
- Files: `internal/plan/run.go` and its tests, `internal/config/load.go` and its tests,
  `cmd/drafter/config.go`, `cmd/drafter/spend.go`, `e2e/e2e_test.go`.
- Acceptance, each row with a clean twin:
  - `GitRoot` in a temp directory outside any repo (set `GIT_CEILING_DIRECTORIES`) wraps
    `ErrNotGitTree`. With `PATH` holding no git, it doesn't wrap it, and the error says git could
    not run. Inside a fresh repo's `.git` directory, it doesn't wrap it, and the error holds git's
    message.
  - `Load` with a root holding `drafter.toml` and `drafter.local.toml` that isn't a git tree: the
    error holds git's message and not the words "not ignored". With `PATH` holding no git, the
    error says git could not run. In a real repo with the file unignored: today's message,
    unchanged. Ignored: loads.
  - e2e: `drafter config` and `drafter spend` with `PATH` holding no git each exit 1 with an error
    naming git. Outside a git tree, each exits 0 on the user layer, as today.
  - `drafter check-plan` outside a git tree prints the same message as before.
- Test: the gate.
- Pair: with F3.

### F3 The ledger lock for reads (45 min, auth-data)

- Outcome: issue #19. `OpenIntents`, `Spend`, and `PageSpend` take a shared `flock` (`LOCK_SH`) on
  `ledger.lock` for their read; `Reserve` and `Settle` keep the exclusive lock. The lock goes in
  the public read methods, never inside the internal `read`, which `Reserve` and `Settle` already
  call under the exclusive lock. flock(2): "If a process uses open(2) (or similar) to obtain more
  than one file descriptor for the same file, these file descriptors are treated independently by
  flock(). An attempt to lock the file using one of these file descriptors may be denied by a lock
  that the calling process has already placed via another file descriptor." So a nested lock would
  deadlock the process against itself. A read against an absent state directory returns zero and
  creates nothing.
- Files: `internal/ledger/ledger.go`, `internal/ledger/store.go`, `internal/ledger/ledger_test.go`.
- Acceptance:
  - A writer mid-append: the test opens `ledger.lock` on its own descriptor, takes `LOCK_EX`, and
    writes half a line to the ledger. `Spend` started in a goroutine hasn't returned after 200 ms.
    The test completes the line and unlocks. `Spend` then returns a total that includes that
    line, and `Warn` received nothing. The same row for `OpenIntents` and `PageSpend`.
  - With the read lock removed, that test fails. Seen once as a temporary local edit, and recorded
    in the task's commit message.
  - Readers share: with the test holding `LOCK_SH` on its own descriptor, `Spend` returns at once.
  - `Spend` on a state directory that doesn't exist returns zero, and the directory still doesn't
    exist afterward. The e2e row "a missing ledger prints a zero total and exits 0" stays green.
  - `Reserve` and `Settle` still work, and every existing ledger test passes, the two-process cap
    test included.
- Test: the gate.
- Pair: with F1.

### F4 Crash-safe torn-tail repair (50 min, auth-data)

- Outcome: issue #20. A writer that finds a torn tail (a final fragment with no newline) truncates
  the ledger to the end of its last complete line, syncs the file, and only then appends. No torn
  marker line is written. The sync before the append fixes the order on disk: a crash leaves the
  fragment (the repair runs again), the truncated file (which reads clean), or the truncated file
  with a torn new line (a fresh torn tail, repaired the same way). The warning names the file, the
  line, and the fragment's length in bytes. The reader's exception for a fragment followed by a
  marker goes. Every complete line that doesn't parse fails closed, naming the line, as the
  corrupt-middle-line test already requires.
- Before coding, confirm that no ledger holding a torn marker exists outside tests. No live run has
  happened (pass 5 makes the first), and `drafter config` names the `state_dir` to check. If one
  exists, stop and report it.
- Dropping the fragment is safe. A torn line never had a successful return: `append` returns only
  after its write and `File.Sync`. A torn reserve therefore had no submission behind it, and a torn
  settle is settled again by its caller's idempotent retry. Readers already skip the fragment
  today.
- Files: `internal/ledger/store.go`, `internal/ledger/ledger_test.go`.
- Acceptance:
  - Every crash point: start from a ledger with complete lines `C` and a torn fragment `F`. Run a
    `Reserve` on a copy and take the final file `B`. The starting ledger `C` plus `F`, and a ledger
    holding `B[:k]` for every length `k` from `len(C)` to `len(B)`, each then take a `Reserve`, a
    `Settle`, and a `Spend` without error. The totals are hand-computed: `F` never counts, and the new line counts only at
    `k == len(B)`. Against today's code, this test fails at `k == len(C) + len(F) + 1` (the
    fragment closed by a newline, the marker not yet written), which is #20's failure.
  - A settle torn just before its newline (complete JSON) and then retried counts once. This is
    the existing test, kept.
  - The rewritten torn-tail test: after the repair the fragment is gone from the file, every line
    parses, and the warning names the file, the line, and the byte count.
  - A corrupt middle line still makes `Reserve`, `Settle`, and `Spend` fail naming the line.
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
the merger: after the merge, `make -C ~/Projects/drafter install`. Stop at PR-ready; the conductor
takes it to Geoff.

## Later

- A bounded wait on `ledger.lock`, carried from pass 2's "Later", if a stopped holder ever wedges
  a read or a run.
