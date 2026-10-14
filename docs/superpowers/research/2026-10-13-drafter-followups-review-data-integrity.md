# drafter follow-ups plan review: data integrity and failure risk

Target: `docs/superpowers/plans/2026-10-13-drafter-followups-plan.md` at fe18c81. Lens agent:
Opus at medium. Verdict: sound in its main lines; one major and three correctness minors.

Checked clean: F3 can't deadlock (no public read runs under the exclusive lock:
`ledger.go:107-113,147-153`, `smoke.go:386`; flock(2) per-descriptor semantics, and "A shared or
exclusive lock can be placed on a file regardless of the mode in which the file was opened").
Caps are unchanged by F3 and F4. A dropped fragment never had a successful return. Ordering is
right: open(2) O_APPEND "the modification of the file offset and the write operation are
performed as a single atomic step"; truncate(2) "The file offset is not changed"; fsync(2) "a
change to the file size ... would require a metadata flush". Probe on btrfs: read, ftruncate,
fsync, write on `O_RDWR|O_APPEND` gives clean lines; on plain `O_RDWR` the write lands past the
new end, NUL-padded. F1 leaves no path failing open.

1. major, correctness, F4 (`store.go:140-153,233-260`). Truncation is the ledger's first
   destructive write, and the offset comes from a read on another open. A wrong offset (an
   off-by-one, a file replaced or hand-edited outside the lock) silently deletes acted-on lines,
   and a lost reserve lets a later `Reserve` cross a cap. Fold: read and repair through one
   descriptor opened `O_RDWR|O_APPEND` under the lock; truncate only when the dropped bytes hold
   no `\n` and `Stat().Size()` equals the length read, else fail closed naming the file; a row
   for the refused repair, file unchanged.
2. minor, correctness, F4. The append's descriptor isn't named; without `O_APPEND` the write lands
   past the truncated end (probed). Fold: state it; add "no NUL byte" to the torn-tail test.
3. minor, correctness, F4. Prefix states can't see a missing fsync; the plan doesn't say what a
   failed truncate or sync does. Fold: diff-reviewer brief checks `Sync` after `Truncate` and the
   append after it; a truncate or sync error returns without appending.
4. minor, correctness, Interfaces. Pass 2's File-states contract ("the next append writes a
   newline first") isn't replaced, and "no reader accepts it" is inaccurate (a marker parses and
   `st.add` ignores unknown types, `store.go:205-228`). Fold: restate File states; say a legacy
   marker is ignored and its fragment line fails closed.
5. minor, correctness, F1. A worktree whose main repo moved may report `fatal: not a git
   repository: <gitdir>` (unprobed: the worktree guard blocked git). Matching the bare substring
   would send it to the user layer and a different ledger. Fold: probe it; classify as
   `ErrNotGitTree` only the "(or any of the parent directories)" and "(or any parent up to mount
   point" forms; add a row.
6. minor, optional. An older drafter meeting a torn tail writes a marker the new code fails
   closed on. Fold: pre-check both hosts; merger note says install before any live run.
7. minor, optional, F3. A state dir without `ledger.lock` is unspecified; `O_CREATE` makes a read
   create a file. Fold: open `O_RDONLY` with no create; on ENOENT read unlocked.
8. minor, optional, OWNER FORK (pre-existing). `checkIgnored` and `GitRoot` inherit `GIT_DIR`,
   `GIT_WORK_TREE`, `GIT_INDEX_FILE`; a `GIT_DIR` at another repo can make `check-ignore` accept
   an unignored `drafter.local.toml`. (a) fold into F1, recommended; (b) Found, not done.
9. minor, optional (pre-existing). The ledger's creation doesn't fsync the directory (fsync(2)).
   Found, not done.
10. minor, optional (pre-existing). Mutual exclusion depends on `ledger.lock` keeping its inode.
    Found, not done.
11. minor, optional, over-ceremony. F2's task-scope review costs one dispatch; keep it, since smoke
    voids provable refusals based on batch errors.
