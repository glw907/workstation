# drafter follow-ups plan review: fold record

Target: `docs/superpowers/plans/2026-10-13-drafter-followups-plan.md` and its executor prompt at
4c9c544, against the three lens files of 2026-10-13 (mechanics, contract, data integrity). Fold
agent: Opus. Each finding was checked against drafter `main` before its disposition. Convergent
findings fold once, at the first lens that raised them.

## Decisions on contested points

- Lock open mode for readers (contract #1 and mechanics #2 against data integrity #7): readers open
  `ledger.lock` with `O_CREATE|O_RDONLY`. If the read opened with no create and read unlocked on
  `ENOENT`, the first write would race the read: a reader that finds no lock file reads with no
  lock while a writer creates the lock and appends, which reopens #19 for that window. With
  `O_CREATE`, reader and writer open the same inode (`lock` in `store.go` opens with `O_CREATE`
  and no `O_EXCL`), so the lock excludes them. The e2e spend fixtures (`e2e/spend_test.go`,
  `newSpendProject`) and `TestFileStates` build a state directory with no lock file, and the
  create handles that shape. The cost is an empty 0600 file in an existing state directory. A
  read-only state directory isn't a real case on this workstation. flock(2) allows a lock on a
  read-only open: "A shared or exclusive lock can be placed on a file regardless of the mode in
  which the file was opened."
- Truncation guard (data integrity #1): folded in part. The repair truncates at the byte after the
  last newline in the bytes the writer read under the same exclusive lock. That makes the
  newline-in-dropped-bytes check free: it holds by construction. The size check against
  `Stat().Size()` is refused. A mismatch can come only from a writer outside `ledger.lock`, and
  every drafter append runs under it (`Reserve` and `Settle` call `l.lock()` before `l.read()`,
  `ledger.go:107-112,147-152`). The branch can't be tested without a test-only seam. The
  off-by-one risk it names is caught by F4's every-crash-point sweep, which checks each prefix
  length `k` byte for byte.

## Dispositions

Mechanics:

1. F1 class and review: folded. F1 is now `auth-data` with a task-scope `diff-reviewer` read
   (Shape, F1 heading). The "F2 may drop to `ordinary`" part is refused: data integrity #11 and
   contract #14 keep F2's read, since smoke voids provable refusals based on batch errors.
2. State dir without a lock: folded at the root with contract #1 (F3 outcome, new acceptance row,
   Interfaces "File states"). See the lock-mode decision above.
3. Not-a-repo detection: folded. Exit 128 plus a first stderr line starting with one of the two
   quoted forms; a classifier table row; `checkIgnored` under `LC_ALL=C` too (F1).
4. Other `GitRoot` callers: folded. An outcome line and a PR-body row listing every caller (F1).
5. "No reader accepts" a marker: folded with contract #6 and data integrity #4 (Interfaces).
6. Vacuous or hanging proofs: folded with contract #3, #4, and #7. F3 names the line per method,
   seeds one complete line, and bounds the wait at 5 s. F4's `F` is a complete, nonzero-cost
   settle, and its follow-ups use fresh intents.
7. fsync quote and prefix assumption: folded (F4 outcome).
8. check-plan's message on other failures: folded with contract #12 (Interfaces, one line).
9. Executor prompt plan path exists only on the plan branch: refused. The planning session merges
   this branch to dotfiles `main` before handoff, so the path resolves.
10. F2 in the session while the pair runs: folded (Shape, F2 note, executor prompt). Path drops
    from 50+15 to 60 for that stage.
11. Per-task `go test` instead of the gate: refused. `drafter-gate.sh` runs through
    `cairn-run-gate` on the light lane, which queues contending runs (exit 75, re-issued), so
    contention costs a wait, not a failure. Moving vet and lint to close only would push their
    findings into the close fix chain.
12. F3's removed-lock proof duplicates the red commit: folded. The commit message cites the
    red-first commit instead (F3).
13. One warning per repair, quoting the fragment: refused. It isn't free: the reader's warning
    fires inside `read`, which writers share, so one warning per repair needs new plumbing. The
    warning already names the file, the line, and the byte count.
14. No `run_test.go`; `t.Setenv` rules out `t.Parallel`: folded with contract #9 (F1 files).

Contract:

1. State dir without a lock: folded (root, with mechanics #2).
2. `LC_ALL=C` with no catching test: folded. A German-locale row, with a comment that it's vacuous
   on a host with no German catalog (F1).
3. Line per method: folded (with mechanics #6).
4. Sweep fixture: folded. `Reserve(i2)` swept, follow-ups on `i3`, figures from `PageSpend` and
   `Spend.Open`, and a `C` empty variant (F4).
5. No test sees a missing sync: folded with data integrity #3. An item in F4's reviewer brief.
6. Marker wording: folded (with mechanics #5).
7. Unbounded "returns at once": folded (with mechanics #6).
8. e2e fixture exits 1 on an unset setting: folded. The e2e rows use `completeUser` (F1).
9. `GIT_CEILING_DIRECTORIES` on the `Load` row, fixtures before stripping `PATH`: folded (F1).
10. Empty stderr gives an empty refusal: folded. Falls back to the exit status (F1, Interfaces).
11. Optional, mark red-first rows: folded, since it's free and helps test-first. Rows that pass
    today carry "(guard)".
12. Optional, check-plan's no-git message: folded (with mechanics #8).
13. Optional, record the F4 marker check in the PR body: folded, free (F4).
14. Optional, over-ceremony: folded in part. F2's grep is dropped, since the compiler enforces
    unexported fields. F2's reviewer brief checks that no returned error wraps
    `*anthropic.Error` (`failure.go`, `inspect`). F3's removed-lock step is dropped (mechanics
    #12). F2's review is kept.

Data integrity:

1. Truncation guard: folded in part. See the decision above.
2. The append's descriptor and NUL bytes: folded. `O_APPEND` is named with open(2) and
   truncate(2) quotes, and the torn-tail test asserts no NUL byte (F4).
3. Truncate or sync failure and reviewer check: folded (with contract #5). A truncate or sync
   error returns without appending (F4 outcome and brief).
4. File states restated, legacy marker behavior: folded (Interfaces "File states").
5. Moved-repository worktree message: folded. Only the two quoted forms classify as
   `ErrNotGitTree`, so an unprobed form falls to the fail-closed branch. F1 probes the
   moved-repository case and adds it to the classifier table. Not probed here: this agent may not
   run git outside its worktree.
6. Optional, older binary writes a marker: folded, free. The merger note says to install on each
   host before its first live run (Close).
7. Optional, readers open with no create: refused. See the lock-mode decision above.
8. Optional, `GIT_DIR` inheritance: found, not done. Outside the five issues by Geoff's ruling.
   Proposed: a backlog issue for the next pass that touches config loading (Close).
9. Optional, no directory fsync on ledger creation: found, not done (Close), with the fsync(2)
   quote. Proposed: a backlog issue, low priority.
10. Optional, the lock's inode: found, not done (Close). Proposed: one sentence in the ledger's
    doc comment.
11. Optional, keep F2's review: folded (kept).

Counts: 39 findings. 32 folded (3 of them in part: mechanics #1, contract #14, data integrity
#1), 4 refused (mechanics #9, #11, #13; data integrity #7), 3 found, not done.

## Path

Pair F1 (60) and F3 (50), with F2 (15) in the session meanwhile: 60. F4: 55. Close: 35. Path: 150
minutes. The Shape figure, the Close score sentence, and the executor prompt's order match it.
