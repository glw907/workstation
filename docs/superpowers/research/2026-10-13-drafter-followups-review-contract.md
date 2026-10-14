# drafter follow-ups plan review: contract and criteria

Target: `docs/superpowers/plans/2026-10-13-drafter-followups-plan.md` at fe18c81. Lens agent:
Opus at medium. Verdict: no blockers, 2 majors, 12 minors, no owner forks. Every issue has a
criterion that catches its defect (#18 by the reviewer's read, since a doc can't be unit-tested).

Probes (git 2.x, this host): outside a repo under `GIT_CEILING_DIRECTORIES`, `rev-parse
--show-toplevel` and `check-ignore -q` both exit 128 with `fatal: not a git repository (or any of
the parent directories): .git`. Inside `.git`, both exit 128 with `fatal: this operation must be
run in a work tree`. With `LANG=de_DE.UTF-8` git prints German; `LC_ALL=C` and `LC_ALL=C.UTF-8`
override `LANGUAGE=de` and `LANG=de_DE.UTF-8`.

1. major, correctness, F3. A state dir that exists without `ledger.lock` is unspecified; every e2e
   spend fixture is that shape (`e2e/spend_test.go:21,34,222`). Opening the lock without create
   breaks them; skipping the lock reopens #19. Fold: absent dir returns zero, locks and creates
   nothing; present dir opens `ledger.lock` with `O_CREATE|O_RDONLY, 0o600` and takes `LOCK_SH`.
   Row: dir present, no lock or ledger, `Spend` returns zero and `ledger.lock` exists at 0600.
2. major, correctness, F1. `LC_ALL=C` is promised but nothing catches it missing. Fold: a GitRoot
   row outside a repo with `LANG=de_DE.UTF-8` and `LANGUAGE=de` still wraps `ErrNotGitTree`
   (fails here without `LC_ALL=C`; vacuous on a host with no German catalog, so say so in a
   comment). Optionally run `checkIgnored` under `LC_ALL=C` too.
3. minor, correctness, F3. Name the line per method: `Spend.Total` counts only settle lines
   (`ledger.go:189-205`); `OpenIntents` and `PageSpend` need a reserve line.
4. minor, correctness, F4. Sweep fixture underspecified: re-reserving the swept intent fails at
   `k == len(B)` (`ledger.go:117`). Fold: swept op `Reserve(i2)`, follow-ups `Reserve(i3)`,
   `Settle(i3, k3)`, `Spend`; expected figures `PageSpend` and `Spend.Open`; add a `C = ""`
   variant.
5. minor, correctness, F4. No test catches a missing sync between truncate and append. Fold: an
   explicit item in F4's diff-reviewer brief.
6. minor, correctness, Interfaces. "No reader accepts it" is wrong: a marker line parses and
   `st.add` ignores unknown types (`store.go:181-227`). Fold: reword.
7. minor, correctness, F3. "Returns at once" has no bound, and a nested-lock deadlock hangs to the
   10-minute test timeout. Fold: goroutine plus 5-second `select`, `t.Fatal("blocked")`.
8. minor, correctness, F1 e2e. With an empty user config, `drafter config` already exits 1 on
   "cycle_ceiling is not set" (`e2e_test.go:557-562`). Fold: use the complete user fixture
   (`e2e_test.go:570-580`) and assert GitRoot's exact phrase.
9. minor, correctness, F1. The not-a-tree `Load` row needs `GIT_CEILING_DIRECTORIES`
   (`e2e_test.go:60`). Build git fixtures before stripping `PATH`; `t.Setenv` rules out
   `t.Parallel`.
10. minor, correctness, F1. Empty stderr gives an empty refusal. Fold: fall back to the exit
    status.
11. minor, optional. Some rows are regression guards that pass today; say which rows are red-first.
12. minor, optional. check-plan's no-git message changes with no row (`checkplan.go:60`).
13. minor, optional. Record the F4 marker check's result in the PR body.
14. minor, optional, over-ceremony. F3's remove-the-lock step repeats the red-first evidence; F2's
    grep is enforced by the compiler; F2's task-scope review is defensible under the ruling, and
    its brief should check no returned error wraps `*anthropic.Error` (`failure.go:38`).
