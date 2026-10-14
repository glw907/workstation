# drafter follow-ups plan: fold verification

Target: the plan and executor prompt at 5ac520a against 4c9c544, checked on drafter `main` at
e72081b. Fresh Opus agent at medium, no part in the fold. No blocker. Every review major closed
at its cited location; every refusal's reason holds; the counts (39: 32 folded, 4 refused, 3
found-not-done) add up. The classifier can't send `fatal: not a git repository: <gitdir>` to
`ErrNotGitTree`: both allowlisted prefixes continue "repository (", that one "repository:". Path
150 (pair at 60 with F2 inside it, F4 55, Close 35) matches Shape, Close, and the fold record. The
executor prompt matches the plan's order and review set. `checkprompts.go:87` on current main
exits cannot-run and never falls back to the user layer.

1. major, correctness, plan:213-221. The fold made `F` a complete, nonzero-cost settle, so today's
   code at `k == len(C)+len(F)+1` reads `F` as a valid line and counts it instead of failing
   closed; the red-first no longer shows #20. Fix: add a variant whose `F` is unparseable (like
   `ledger_test.go:584`), which fails closed at that `k` today (#20); restate the complete-`F`
   variant's red as "`F` counts from that `k` on"; on the new code both assert no error at any
   `k` and `F` never counts.
2. minor, correctness, plan:111-113, 128-129. The moved-repository message is unprobed. Fix: if
   the probe shows it printing an allowlisted form, stop and report.
3. minor, correctness, plan:23-25. Rows that pass today carry no "(guard)" mark: F3 readers share
   (:175-176), absent dir (:177-178), Reserve and Settle still work (:182-183), F4's kept settle
   test (:222-223). F1's Load no-git row (:138-139) is ambiguous, since `load.go:120` already names
   git's exec error. Fix: mark the four; name `GitRoot`'s could-not-run phrase in the Load row.
4. minor, optional, plan:130-133. The German row should also clear `LC_ALL` and `LC_MESSAGES`.
