The spec has a done list, and it contradicts the prose on one behavior, so that is the first question. I could not open the plain-language guide (read denied), so this follows the router's shape rules only.

I checked the spec's claims against the repo, and they hold: the gate prints three `ok` lines and exits 0, `git grep` finds the 4 hits, and `search rope` prints the usage line and exits 2 today. I did not test push access to `origin`.

## Questions

1. **What does a search with no match exit with, 1 or 0?** The prose says "No match prints nothing and exits 1", and item 2 asserts exit 1 for `search '.*'`. Item 3 asserts exit 0 for `search zzz`. Both are no-match cases, so no honest implementation passes items 2 and 3 together. The answer also sets the exit code for a missing notes file, which "counts as no match". I would guess 1, two statements against one, but a wrong guess ships the wrong contract to any script that calls the tool.

2. **What happens with more than one argument, as in `notes search buy rope`?** `add` joins its arguments, but the usage line says `<word>`. Searching the phrase, searching only `buy`, and exiting 2 with usage are all defensible, and each needs a different test. The stakes are lower than question 1, but the owner is likely to type this.

## Done list, item by item

Items 1 to 4 share one weakness. Each check sees only an `ok` line carrying the test's name, and the builder writes the test. A test body of `true` prints that line, so only the reviewer's reading stands between an empty test and done.

1. **`test_search_finds`** passes on three wrong results even when written as described.
   - Whole-word matching passes, because no fixture note has `rope` inside a longer word. The `rope` finds `ropes` rule is untested.
   - Lowercasing only the note passes, because the query is always lowercase. `search ROPE` could find nothing.
   - Printing extra notes passes if the test checks only that the two lines appear in order. The item lacks the "only" that item 2 has.

2. **`test_search_plain_text`** passes on an implementation that escapes only `.` and `*`. A word such as `[a-z]`, `^fix`, or `a\.c` would still act as a pattern. A word that starts with `-`, such as `-v`, is also untested and could be read as an option.

3. **`test_search_no_match`** as written requires exit 0, which the prose calls wrong. That is question 1. No item tests a missing notes file, because every new test creates its file first. A `grep` on the missing file that prints "No such file" to stderr and exits 2 gets through all six items.

4. **`test_search_missing_word`** passes when the builder puts the new usage line only in the `search` branch and leaves `bin/notes:7` stale. `notes bogus` would then print the old line, and `test_usage` checks only the `usage:` prefix. It also passes if the usage line goes to stdout as well, unless the test checks that stdout is empty.

5. **The README check** passes on any single line containing `notes search`, including one that describes the command wrongly, such as calling it case-sensitive or a pattern. It also fails a correct README that mentions the command on two lines, because `grep -c` counts lines.

6. **`bash scripts/gate.sh` exits 0** passes today with nothing built. It adds only the three existing tests, which guard "nothing about `add` or `list` changes" thinly. A change to how `add` joins several arguments would get through.