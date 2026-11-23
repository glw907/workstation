The spec has a done list, and I checked it against the repo. One question blocks a good plan and two smaller ones are worth an answer; five of the six done items can pass on a wrong result.

## Questions, ranked

1. **May the task change `completions/notes.bash`, or is the three-file list a hard limit?**
   - The spec's usage line cannot pass the gate with only the three listed files changed. `test_completions_match` (`tests/run.sh:15`) compares every `notes <word>` in `bin/notes` against the words in `completions/notes.bash`, which the spec's `git grep -- bin tests` never searched.
   - I applied only the usage-line change in a temp copy, and the gate printed `FAIL test_completions_match` and exited 1.
   - The answer decides whether the plan adds `search` to the completion file (a fourth file, which the reviewer may reject as out of scope) or edits or drops an existing test. The second route also satisfies item 6.

2. **What does `search` do with more than one argument, such as `notes search buy rope`?**
   - `add` joins its arguments into one note, so the owner may expect search to join them too.
   - The other options are to search for `buy` only, or to print usage and exit 2.
   - Each is a different visible behavior and a different test, and the spec only covers a single `<word>`.

3. **Is `origin` a real, pushable remote?**
   - `github.com/example/notes` reads like a placeholder, and the sandbox denied my `git ls-remote`, so I could not confirm it.
   - If it is not real, the task cannot end in a pull request as the spec requires.

## Done items that could pass on a wrong result

- **Item 1 (`test_search_finds`)**
  - A whole-word match (`grep -iFw`) passes, because the fixture has no note where the word sits inside a longer word. The `rope` finds `ropes` rule is never exercised.
  - Output sorted alphabetically instead of oldest first passes, because `Buy rope` sorts before `ROPE ladder` anyway.
  - The item says "prints A then B", not "only", so a test written to that wording lets extra lines through.

- **Item 2 (`test_search_plain_text`)**
  - An implementation that escapes only `.` and `*` passes, while `[`, `\`, `^` and `$` still act as patterns.
  - `grep -iF "$word"` without `--` passes, though `notes search -v` would then be read as a grep option.
  - The exit code of `search a.c` is not asserted.

- **Item 3 (`test_search_no_match`)**
  - Only stdout and the exit code are checked, so a "no match" message on stderr passes although the spec says it prints nothing.

- **Item 4 (`test_search_missing_word`)**
  - A second usage string written inside the `search` branch passes while `bin/notes:7` keeps the old text. `notes bogus` then still prints the old usage, and `test_usage` checks only the `usage:` prefix.
  - Usage printed to stdout as well as stderr passes unless the test checks that stdout is empty.

- **Item 5 (README grep)**
  - Any single line containing `notes search` passes, including one that describes the command wrongly or says it is unsupported.
  - `grep -c` counts lines, so a correct README that mentions the command on two lines fails.

- **Item 6 (gate exits 0)**
  - The gate runs only the names in the `for` list, so it exits 0 if `test_completions_match` is removed from the list or weakened. That is the easy way around question 1.

- **No item covers the missing notes file.**
  - The spec requires each new test to create its file with `mktemp` and add four notes, so none can reach this case.
  - A plain `grep -iF -- "$word" "$file"` passes all six items. On a missing file it prints a grep error and exits 2, which the spec reserves for usage, where the spec wants silence and exit 1.

- **Items 1 to 4 as a group.**
  - Each is satisfied by an `ok` line from a test the builder writes. A test body that asserts less than the spec's sentence still prints `ok`, so only the reviewer reading the test bodies catches it.