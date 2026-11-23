I read `spec.md` and checked its claims against the repo. One claim it rests on is false, and that is the top question.

## Questions, ranked

1. **What should happen to `test_export_csv`, given the gate is red today?**
   - The spec says the gate "printed `ok` for every test and exited 0" on 2026-11-22. I ran it today and it prints `FAIL test_export_csv` and exits 1.
   - That test calls `bin/notes export`, which doesn't exist, and it is in the `for` list at `tests/run.sh:18`.
   - Done item 6 therefore cannot hold with the three named files changed as described. The options are to build `export`, drop the test from the list, or redefine item 6 as "no failures other than `test_export_csv`".
   - Each is a different plan. Building `export` is a second feature whose only specification is one expected string, `1,"buy rope"`. Dropping the test deletes someone's intent. Redefining item 6 changes the done list.

2. **Has the spec been approved, and is the remote real?**
   - The status line reads "awaiting approval", and `CLAUDE.md` says a build starts from an approved spec.
   - I could not reach `github.com/example/notes` from this sandbox (network blocked), so I can't confirm the pull request has somewhere to land. The repo has only a local `main` and no remote-tracking branch.
   - If either answer is no, the plan stops before the build or ends somewhere other than a pull request.

3. **Should `notes bogus` and bare `notes` print the new usage line too?**
   - The spec says "the usage line becomes…", which reads as yes, but only the `search` and `search ''` paths are checked.
   - If yes, the plan needs an assertion for it, and `test_usage` "stays as it is" cannot supply one.

## Done list: items that could pass on a wrong result

1. **`test_search_finds`** passes on three wrong results:
   - **Whole-word matching.** No fixture note contains `rope` inside a longer word, so `grep -iwF` produces the same output and "`rope` finds `ropes`" is never exercised.
   - **Sorted output instead of oldest first.** `Buy rope` sorts before `ROPE ladder`, so file order and alphabetical order coincide.
   - **De-duplicated output.** The fixture has no repeated note.

2. **`test_search_plain_text`** probes only `.` and `*`:
   - An implementation that escapes just those two passes while `[`, `\`, `^` and `$` still act as a pattern or error out.
   - A word starting with `-`, such as `search -v`, is taken as an option by a naive `grep -iF "$word"`.
   - The exit code of `search a.c` is not asserted.

3. **`test_search_no_match`** runs against a notes file that exists:
   - "A missing notes file counts as no match" is untested. A plain `grep` on a missing file prints an error to stderr and exits 2, and all four tests still pass.
   - Stderr isn't checked, so a "no match" message there also gets through.

4. **`test_search_missing_word`** covers only the two `search` paths:
   - A builder can add a second usage `echo` inside the `search` branch and leave `bin/notes:7` unchanged.
   - `notes bogus` then still prints the old line, and `test_usage` passes because it checks only the `usage:` prefix.

5. **`grep -c "notes search" README.md` prints 1** counts lines, not meaning:
   - Any single line containing the string passes, including a wrong description or "notes search is not supported".
   - It also fails on a correct result: a README that mentions the command on two lines prints 2, and one that wraps between `bin/notes` and `search` prints 0.

6. **`bash scripts/gate.sh` exits 0** is satisfied by removing tests:
   - Deleting `test_export_csv`, or any existing test, from the `for` list makes the gate exit 0 with no feature behind it. The spec itself notes a test runs only when it is in that list.
   - Nothing requires the four pre-existing names to stay in the list or still print `ok`.