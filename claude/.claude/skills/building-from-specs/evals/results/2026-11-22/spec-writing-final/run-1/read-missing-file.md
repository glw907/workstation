I found one blocking contradiction, two smaller questions, and every one of the six done items can pass on a wrong result. I probed these against a throwaway copy of the repo; the spec's "rests on" claims about the gate and `search rope` today check out.

## Questions, ranked

1. **Is `completions/notes.bash` in scope?** The spec's file list and done item 6 cannot both hold.
   - `test_completions_match` in `tests/run.sh` compares every `notes <word>` in `bin/notes` against the completion list, which is `add list`.
   - With the required usage line and only the three listed files changed, the gate prints `FAIL test_completions_match` and exits 1.
   - The spec's grep covered only `bin` and `tests`, so it never saw this file.
   - The plan either adds a fourth file (`complete -W "add list search"`) or weakens an existing test. I would assume the fourth file, but the spec excludes it.

2. **What does `notes search buy rope` do?** The spec covers only one word or none.
   - `add` joins its arguments, so the owner will likely type an unquoted phrase.
   - The options are to join into a phrase, reject with usage and exit 2, or silently ignore the extra words.
   - Each gives different output and needs a different test.

3. **Is `origin` a real, pushable remote?** `github.com/example/notes` reads like a placeholder, and the sandbox denied network access, so I could not check. If it is not real, the pull request step has no destination.

## Done list: items that pass on a wrong result

One weakness cuts across items 1 to 4. `tests/run.sh` has no `set -e`, so a test function returns only its last command's status. A test with several assertions not chained by `&&` prints `ok` when an early one fails.

1. **`test_search_finds`**
   - Whole-word matching passes: `rope` is a whole word in both fixture notes. `grep -iwF` printed the expected two lines, while `search rop` printed nothing. No fixture note covers "`rope` finds `ropes`".
   - Sorted output passes too, since the fixture's file order is also its alphabetical order.
   - "Prints X then Y" does not demand exact stdout, so a contains-check would let extra lines through.

2. **`test_search_plain_text`**
   - A word starting with `-` is not covered. With `grep -iF "$1" "$file"` and no `--`, `search -v` treated the notes file as the pattern and hung on stdin, yet both asserted cases passed.
   - The exit code for `search a.c` is not asserted.

3. **`test_search_no_match`**
   - The file exists in this fixture, so "a missing notes file counts as no match" is tested by no item. A plain grep on a missing file prints `No such file or directory` and exits 2. Copying the `list` idiom exits 0.
   - Stderr is not asserted, so error noise alongside empty stdout passes.

4. **`test_search_missing_word`**
   - It covers the usage line only on the `search` path. An implementation can give `search` its own usage string and leave `bin/notes:7` unchanged. Then `notes bogus` and bare `notes` still print the old line, and `test_usage` checks only the `usage:` prefix.
   - If the new test copies that prefix check, the old line passes here too. It needs exact equality.

5. **`grep -c "notes search" README.md` prints 1**
   - This counts lines containing the string, not whether the description is right. "notes search takes a regex" passes.
   - It also fails a correct README that mentions the command on two lines.

6. **`bash scripts/gate.sh` exits 0**
   - The gate runs only what is in the `for` list, and `tests/run.sh` is a file the task edits.
   - Dropping or loosening `test_completions_match`, the test from question 1, gets exit 0 with completions still offering only `add list`.
   - No item requires the four existing tests to still print `ok` unmodified.