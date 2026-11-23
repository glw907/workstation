I read `spec.md` and checked its claims against the repo. The gate, the `git grep` count, and today's `search rope` behaviour all match what it says. The spec does have a done list; five of its six items can pass on a wrong result, and item 5 passes today with no work done.

## Questions I'd still need answered

1. **Does `origin` exist, and can the builder push to it?** The remote is `github.com/example/notes`, which reads like a placeholder, and the sandbox blocked my attempt to reach it. If it isn't real, the task cannot end in a pull request and the plan needs a different final step.
2. **What should `notes search buy rope` (more than one argument) do?** The spec covers only a missing or empty word. Joining the arguments into a phrase as `add` does, rejecting them with usage and exit 2, or silently using the first word are all user-visible behaviours, and each needs a different test.

Everything else I could decide myself.

## Done-list items that could pass on a wrong result

Two harness problems apply to items 1 to 4:

- **Only the last command counts.** `tests/run.sh` calls each test as `if "$t"`, so a test function returns only the status of its last command. A test that writes its assertions on separate lines, rather than chaining them with `&&`, passes when only the final one holds.
- **The `ok` line proves little.** The check is the printed `ok` line, not the test body, so a test that asserts less than the spec describes still prints it.

Item by item:

1. **`test_search_finds`** has three gaps.
   - **Whole-word matching passes.** No fixture note has `rope` inside a longer word, so `grep -w` gets through, though the spec says `rope` finds `ropes`.
   - **Uppercase search words are untested.** Only the note side has uppercase, so a build that lowercases the notes but not the word passes while `search ROPE` finds nothing.
   - **Sorted output passes.** `Buy rope` sorts before `ROPE ladder`, so alphabetical order is indistinguishable from oldest first.
2. **`test_search_plain_text`** has two gaps.
   - **A word starting with `-` is untested.** `grep -iF "$word"` without `--` passes, though `search -v` would then be read as a grep option.
   - **The exit code of `search a.c` is not asserted.** A build that prints the match but exits non-zero passes.
3. **`test_search_no_match`** has two gaps.
   - **The missing-file case is untested.** The file always exists in the test, so a bare `grep` on a missing file, which prints an error and exits 2, passes all six items. The spec requires no output and exit 1.
   - **Stderr is not checked.** A no-match that writes noise to stderr passes.
4. **`test_search_missing_word`** exercises only the `search` path. A build that adds a second usage string for `search` and leaves `bin/notes:7` alone passes, so `notes bogus` and bare `notes` still print the old line. `test_usage` checks only the `usage:` prefix and won't catch it.
5. **`grep -c notes README.md` prints 1 or more.** It prints 3 today, so an untouched README that never mentions `search` passes. The check needs to look for `notes search` and currently print 0.
6. **`bash scripts/gate.sh` exits 0.** It exits 0 today. It also exits 0 if a new test is never added to the `for` list, or if an existing test is dropped from it, so a regression in `add` or `list` could go unnoticed. No item requires the three existing `ok` lines to still appear.