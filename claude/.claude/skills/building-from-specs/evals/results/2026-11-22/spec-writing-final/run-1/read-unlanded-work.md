Three questions are left, and all six items on the done list can pass on a wrong result. The spec's other stated facts check out against the repo: the gate passes, the `usage` grep gives 4 hits, and `search rope` exits 2 today.

## Questions, ranked

1. **What format does `notes export` use, and where is it?** The spec says each match prints in that format, but there is no `export` anywhere in this repo. `bin/notes` has only `add` and `list`, `main` is the only branch, and I could not reach `origin` from here. The answer changes the plan in three ways:
   - It sets the expected strings in tests 1 and 2, so a guess gets baked into the tests and passes.
   - If the format carries a number or date, I need to know whether a number is the note's position in the full list or among the matches, and whether the match runs on the note text alone.
   - If the format has a wrapper such as a header row or brackets, "no match prints nothing" conflicts with it.

2. **Does this task build on the unlanded export work or on `main` as it stands?** Both would edit the same `case` block, usage line, test list and README. The usage line the spec dictates has no `export` in it, and test 4 asserts that line exactly. Landing after export would either remove export from the usage line or fail test 4, so the base branch and the usage text both depend on the answer.

3. **What does `notes search buy rope` do?** The spec covers a single word only. Joining the arguments as `add` does, searching only the first, or exiting 2 are all defensible, and a user will see the difference. The first two also pass the done list.

## Done list: items that pass on a wrong result

1. **`test_search_finds`**
   - A whole-word match passes, because no fixture note has `rope` inside a longer word, so the `ropes` rule is untested.
   - Sorted output passes, because `Buy rope` sorts before `ROPE ladder` anyway.
   - Lowercasing only the notes passes, so `search ROPE` could find nothing.
   - A wrong guess at the export format passes, because the builder writes the expected string.

2. **`test_search_plain_text`**
   - Escaping only `.` and `*` passes, so `^`, `$`, `[` and `\` could still act as patterns.
   - A word starting with `-` is untested; with an unguarded grep, `search -v` inverts the match.
   - The exit code of `search a.c` is not asserted.

3. **`test_search_no_match`**
   - The fixture file always exists, so the "missing notes file counts as no match" rule is never run. A plain grep there exits 2 with an error, which looks like a usage failure.
   - Only stdout is checked, so a "no matches" message on stderr passes.

4. **`test_search_missing_word`**
   - A second usage string inside the search branch passes while `bin/notes:7` keeps the old text. `test_usage` checks only the `usage:` prefix, so `notes bogus` could still print the old line.
   - Usage printed to stdout as well as stderr passes unless the test also asserts empty stdout.

5. **README grep**
   - `grep -c` counts lines, so any one line containing `notes search` passes, including one that describes the command wrongly.
   - It also fails on a correct README that mentions the command on two lines.

6. **Gate exits 0**
   - A new test left out of the `for` list never runs, so the gate alone passes with no search tests at all. Only items 1 to 4 catch that.
   - The three existing tests are thin on "nothing about `add` or `list` changes": one note added and listed, and an empty list. A change to multi-note order or to how `add` joins its arguments passes.

Nothing in the list requires the pull request to exist or the reviewer to have accepted it, although the spec says the task ends in one.