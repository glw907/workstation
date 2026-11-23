I read `spec.md` and checked its claims against the repo. Two questions need answers before planning, and every item on the done list can pass on a wrong result.

## Questions, ranked

1. **Is `tests/run_all.sh` in done item 1 a typo for `tests/run.sh`?** The file does not exist; `bash tests/run_all.sh` exits 127 today. Items 2 to 4 use `tests/run.sh`, and the Files section lists only three files, so I would guess typo. If the guess is wrong, a runner script is missing from the plan. If it is right, item 1 still cannot pass as written, and a builder held to it literally either stalls or creates a file outside the list.

2. **What does `notes search buy rope` do with more than one argument?** The spec covers only a single word. `add` joins its arguments with spaces, so joining into a phrase is one reading; a usage error or ignoring the extras are the others. The owner will likely type this unquoted, and each reading gives a different result and exit code.

I could not confirm that `origin` accepts a pull request, because the sandbox blocked the network check. The spec's other premises hold: the gate passes, `search rope` exits 2 today, and the `usage` grep finds the four hits described.

## Done list: items that pass on a wrong result

Three gaps apply across items 1 to 4:

- **Whole-word matching passes.** No fixture has the word inside a longer word, so `grep -w` behavior passes every test while `rope` fails to find `ropes`.
- **One-sided case folding passes.** Every search word in the tests is lowercase, so a build that folds only the note text passes while `search ROPE` finds nothing.
- **An `ok` line can come from a test that asserts less than the spec says.** A function in `tests/run.sh` returns only its last command's status. A test written as separate statements checks only the last one, which matters most for items 2 and 4.

Per item:

1. **Item 1** cannot be checked at all, since the path does not exist. With the path fixed, the two shared matching gaps above apply here.
2. **Item 2** has no gap of its own beyond the shared ones.
3. **Item 3** does not cover the missing notes file. A build that runs `grep` on a missing file prints a `grep` error and exits 2, not 1, and still passes, because the fixture file always exists.
4. **Item 4** checks the usage line only on the `search` path. A build that leaves `bin/notes:7` unchanged passes, so `notes bogus` and bare `notes` still print the old line. `test_usage` checks only the `usage:` prefix.
5. **Item 5** counts lines containing the string "notes search", not a description. "notes search is not available yet" passes. A correct README that mentions the command on two lines prints 2 and fails.
6. **Item 6** adds only the three existing tests to items 1 to 4, so it inherits every gap above. A new test left out of the `for` list would also let the gate pass, though items 1 to 4 catch that.