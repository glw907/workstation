The spec has a done list, and I checked its claims about today's state against the repo: all hold. Two questions remain, and every one of the six done items can pass on a wrong result.

## Questions

1. **Is `passed test_search_finds` in item 1 a typo for `ok   test_search_finds`?** The runner in `tests/run.sh` prints only `ok   <name>` or `FAIL <name>`, and items 2 to 4 expect the `ok` form. Read literally, item 1 forces either a change to the runner's output, which breaks items 2 to 4, or a one-off `echo` inside the test. I would assume a typo, but a reviewer checking the list literally would then fail the build.

2. **What does `notes search buy rope` do with more than one argument?** `add` joins its arguments with spaces, so the owner may expect search to do the same. The options are to join them into one phrase, to print the usage line, or to ignore the extras. The answer changes the argument handling and adds a test, and a wrong guess gives either a surprise usage error or results for `buy` alone.

## Done list: items that pass on a wrong result

1. **Item 1 (`test_search_finds`)**
   - No runner line produces `passed ...`, so the line must come from a separate `echo`, which prints whether or not the assertions hold or the test is in the `for` list.
   - A whole-word match passes, because no fixture note has the word inside a longer word; the `rope` finds `ropes` rule is never exercised.
   - Folding case on the note side only passes, because every search word in the tests is lowercase; `search ROPE` could find nothing.

2. **Item 2 (`test_search_plain_text`)**
   - Only `.` and `*` are tested. A word starting with `-`, such as `search -v`, can be taken as an option by the underlying tool.
   - A word with a backslash can be reinterpreted by an awk-based build.

3. **Item 3 (`test_search_no_match`)**
   - The missing-notes-file rule is untested, because every test creates its file with `mktemp`. The obvious `grep` build exits 2 with a "No such file" error there instead of exiting 1 silently.
   - Only stdout is checked, so noise on stderr passes.

4. **Item 4 (`test_search_missing_word`)**
   - It checks the new usage line only on the `search` path. `notes bogus` and bare `notes` could keep the old line, since `test_usage` checks only the `usage:` prefix and stays as it is.

5. **Item 5 (README)**
   - Any single line containing `notes search` passes, whatever it says, including a wrong description or no description.
   - It also fails a correct README that mentions the command on two lines.

6. **Item 6 (gate exits 0)**
   - The gate runs only tests named in the `for` list. With item 1 as written, `test_search_finds` can be defined, left out of the list, and the gate still exits 0.
   - "Nothing about `add` or `list` changes" rests on two thin existing tests.

The list also has no item for the pull request or the review, so all six can hold with nothing pushed and no reviewer verdict.