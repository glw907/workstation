I've read the spec, checked its claims against the repo, and tried the done list against a few wrong implementations. Two questions block a good plan, and all six done items can pass on a wrong result.

The spec's checkable claims about today's repo all hold: the gate passes, `search rope` prints usage and exits 2, the grep finds 4 hits, and the README count is 0.

## Questions, ranked

1. **What format does `notes export` use, and where is `export`?**
   - The spec says each match prints "in the format `notes export` uses", but `export` appears nowhere in `bin/notes`, the README or the tests. The repo has one commit on `main`, no other branches, stashes or worktrees, and I could not reach `origin` from here.
   - Every test that asserts output depends on this (items 1 and 2). If I guess bare lines like `list` prints, I write the tests to my guess and they pass on the wrong format.
   - If the format carries a number, I also need to know whether it is the note's position in the full list (1 and 4) or among the matches (1 and 2).

2. **If `export` is unlanded work, does search build on top of it or on `main`, and what is the usage line once both land?**
   - The spec fixes the usage line as `usage: notes add <text> | notes list | notes search <word>`, with no `export`, and item 4 asserts it.
   - Built on `main`, this task collides with the export work at `bin/notes:7`, and whichever merges second has a wrong usage line or a failing test.
   - Built on the export branch, the base, the "4 hits" file survey and the usage text all change, and search should reuse export's formatter instead of copying it.

3. **What does `notes search buy rope` do (lowest)?**
   - `add` joins its arguments, so a user will type this. The spec covers only a missing or empty word.
   - Joining into a phrase, exiting 2, and ignoring `rope` are three different behaviours, and the third silently returns wrong matches.

## Done list: every item can pass on a wrong result

The `ok` line reflects only the last command in a test function, because `tests/run.sh` runs without `set -e`. Items 1, 2 and 4 each hold two assertions, so if they are not chained with `&&` the first can fail and the test still prints `ok`.

1. **`test_search_finds`**
   - Whole-word matching passes: `grep -iwF` gives the same output on this fixture, because no note contains `ropes`. The spec's own example, "`rope` finds `ropes`", is untested.
   - One-sided case folding passes: every test word is lowercase, so an implementation that lowercases only the notes passes while `search ROPE` finds nothing.
   - Sorted output passes, because `Buy rope` sorts before `ROPE ladder` anyway.
   - Any format passes: "in that format" is undefined (question 1).
   - Extra lines pass: the item does not say "only", so a containment check would accept every note being printed.

2. **`test_search_plain_text`**
   - A word starting with `-` is not covered: without `--`, `search -c` is read as a grep option.
   - Other pattern characters are not covered: a glob-based match would let `search 'a?c'` return both `fix a.c` and `fix abc`.
   - A word containing a backslash is not covered: an `awk -v` implementation mangles it.

3. **`test_search_no_match`**
   - A missing notes file is untested, because every test creates its file with `mktemp`. Plain `grep` on a missing file prints an error and exits 2, which is the usage exit code, where the spec wants silence and exit 1.
   - Only stdout is checked, so a "no matches" message or a grep error on stderr passes.

4. **`test_search_missing_word`**
   - A stale usage line passes: a builder can print the new line only in the search branch and leave `bin/notes:7` unchanged. `notes bogus` then still prints the old usage, and `test_usage` checks only the `usage:` prefix.
   - Usage on stdout passes if the test captures with `2>&1`, as `test_usage` does today.

5. **README grep**
   - `grep -c "notes search" README.md` counts lines, so any single line containing those two words passes. That includes a description that is wrong, for example one calling the word a pattern, or one that omits the exit codes.

6. **`bash scripts/gate.sh` exits 0**
   - Dropping an existing test passes: nothing requires the three existing `ok` lines to still print, so a test removed from the `for` list or weakened leaves the gate green.
   - "Nothing about `add` or `list` changes" rests on two thin tests, and `test_list_empty` only covers the missing-file case.