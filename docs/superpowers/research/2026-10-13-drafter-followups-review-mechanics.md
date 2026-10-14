# drafter follow-ups plan review: mechanics and feasibility

Target: `docs/superpowers/plans/2026-10-13-drafter-followups-plan.md` at fe18c81, and its executor
prompt. Lens: the `plan-reviewer` agent, Opus at medium, reading drafter `main` at bcb1a13. No
blocker, four majors, ten minors, no owner fork.

Probes (git 2.56.0, `LC_ALL=C`): under `GIT_CEILING_DIRECTORIES`, `fatal: not a git repository
(or any of the parent directories): .git` (128). Without it, in tmpfs `/tmp`: `fatal: not a git
repository (or any parent up to mount point /)` then `Stopping at filesystem boundary
(GIT_DISCOVERY_ACROSS_FILESYSTEM not set).` (128). Inside `.git` or a bare repo: `fatal: this
operation must be run in a work tree` (128). A missing directory: `fatal: cannot change to
'<dir>': No such file or directory` (128). `check-ignore` outside a repo: the first message (128);
unignored, tracked file included: rc 1, no output. `LANGUAGE=de LC_ALL=C` prints English;
without `LC_ALL=C`, German.

## Major

1. correctness, F1 class (plan :22-23, :97-102). `checkIgnored` (`load.go:106-121`) is a
   fail-closed guard on a file that "can hold a key source and caps"; F1 rewrites its branching
   with no task-scope review. Fold: F1 takes a task-scope `diff-reviewer` read; F2 may drop to
   `ordinary`.
2. correctness, F3 (:129-130, :141). A present state dir without `ledger.lock` is unspecified;
   `TestFileStates` "absent and empty read as zero" (`ledger_test.go:521-539`) builds that state.
   Fold: the read path skips `MkdirAll`, opens `ledger.lock` `O_CREATE|O_RDONLY`; ENOENT (dir
   absent) returns empty; present dir creates the lock and takes `LOCK_SH` (flock(2): "A shared or
   exclusive lock can be placed on a file regardless of the mode in which the file was opened");
   any other open error names the lock path. One row per state.
3. correctness, F1 (:88-93, :106-109). Detection isn't named and git prints two not-a-repo forms.
   Fold: `ErrNotGitTree` on exit 128 when the first stderr line starts `fatal: not a git
   repository`, both variants quoted; a classifier table test on both strings; `checkIgnored`'s
   git under `LC_ALL=C` too.
4. correctness, F1 (:33-35, :95-96). Passes 3 and 4 may add callers with the same fallback. Fold:
   a row: every `plan.GitRoot(` caller on current `main` that falls back to the user layer does so
   only on `ErrNotGitTree`; list the callers in the PR body.

## Minor, correctness

5. Interfaces (:54-55). "No reader accepts" a marker is false (`store.go:181-228`). Reword.
6. Vacuous or hanging proofs. F3: name the line per method, seed one complete line, bound the wait
   at 5 s. F4: make `F` complete, nonzero-cost JSON with no newline so "F never counts" is
   observable (the fragment at `ledger_test.go:590` doesn't parse); the follow-up `Reserve` uses a
   fresh intent.
7. F4 (:149-153). Quote fsync(2): "a change to the file size (st_size, as made by say
   ftruncate(2)), would require a metadata flush"; state the prefix-consistent append assumption
   (btrfs default, ext4 `data=ordered`).
8. check-plan (:116). A plan in a missing directory now prints git's `cannot change to` line.
   Record it, or add a row (exit code unchanged).
9. Executor prompt :7. The plan path exists only on the plan branch until it merges.

## Minor, optional

10. Run F2 in the session while the pair runs; path 150 to 135.
11. The gate is `make check` (the whole suite), so per-task gate runs already run everything, and
    the pair contends on the light lane. Fold: per-task `go test` on touched packages plus `./e2e/`,
    the gate once at close.
12. F3's removed-lock proof duplicates the red commit; cite it instead.
13. A torn tail warns twice after F4; truncation deletes bytes the marker scheme kept. Fold: one
    warning per repair, quoting the dropped fragment.
14. `internal/plan` has no `run_test.go`; `t.Setenv` rules out `t.Parallel`.

Checked sound: the flock nesting rationale; flock restarts under `SA_RESTART` (signal(7));
`Sleep`/`Now` set only in `helpers_test.go:173-174`; `state_dir` comes only from the user layer or
the environment (`layer.go:31`, `env.go:44`); e2e already sets `GIT_CEILING_DIRECTORIES`
(`e2e_test.go:60`); F4's claimed failure point matches `store.go:164-171`.
