I'd still need three answers before planning, and every one of the six done items can pass on a wrong result.

I checked the spec's premises against the checkout: the gate passes, the four `usage` hits are as described, and `search rope` prints usage and exits 2 today. I could not reach `origin` (the sandbox denied github.com).

## Questions, ranked

1. **What does `notes export` print, and where does it live?**
   - `bin/notes` has only `add` and `list`; `bin/notes export` prints the usage line and exits 2.
   - There is no export code locally: one commit, one branch, no stash, no worktree, no dangling objects.
   - The answer sets the output of every match and the expected strings in item 1. If the format carries a number or a date, I also need to know whether a match shows its position in the full list or among the matches.
   - Guessing "the raw line, as `list` prints it" is the obvious move, and it is wrong the moment export does anything else.

2. **Does search land before or after export, and what is the usage line then?**
   - The spec's new usage line names `add`, `list`, and `search`, but not `export`.
   - If export is unlanded work, it edits the same `bin/notes:7`, and item 4 asserts a usage string that one of the two branches makes stale.
   - The answer decides whether this task branches from `main` or from the export work, whether search reuses an export formatter or duplicates it, and what string item 4 checks.

3. **What does `notes search buy rope` (two arguments) do?**
   - `add` joins its arguments, so a user will try this.
   - Joining into one phrase, searching only the first word, and exiting 2 are all defensible. Each is visible behavior, and the spec covers only missing and empty words.

## Done list: items that pass on a wrong result

1. **Item 1 (`test_search_finds`)**
   - "In that format" has no definition (question 1), so the builder writes both the format and the test that checks it; any format passes.
   - No fixture note has the word inside a longer word. A whole-word match (`grep -iwF`) passes all four tests while `rope` fails to find `ropes`, which the spec requires.

2. **Item 2 (`test_search_plain_text`)**
   - It covers `.` and `.*` only. A word starting with `-` taken as an option, or a backslash mangled by `awk -v`, gets through.
   - The exit code of `search a.c` is not asserted.
   - A test function in this harness returns its last command's status. If the two assertions are written as separate statements, the `a.c` check can fail and the test still prints `ok`. The same applies to the two-part tests in items 1 and 4.

3. **Item 3 (`test_search_no_match`)**
   - Every test creates its file with `mktemp`, so "a missing notes file counts as no match" is never exercised. A plain `grep` on a missing file exits 2 with an error on stderr, and this item still passes.
   - Stderr is not asserted, so a "no matches" message gets through.

4. **Item 4 (`test_search_missing_word`)**
   - It checks the usage line only on the `search` path. A builder can add the new string inside the search branch and leave `bin/notes:7` alone. Then `notes bogus` still prints the old usage line, and `test_usage` passes because it only checks the `usage:` prefix.
   - Usage text also going to stdout would pass.

5. **Item 5 (README grep)**
   - `grep -c` counts lines containing the string. One line saying anything passes, including a wrong syntax or "notes search is not supported".
   - It also fails a correct README that mentions the command on two lines, which pushes the builder toward a single thin mention.

6. **Item 6 (gate exits 0)**
   - The gate runs only names in the `for` list, and no item requires the three existing `ok` lines to still print. Dropping or weakening an existing test passes.
   - "Nothing about `add` or `list` changes" rests on two thin tests. For example, a changed default file path passes, because every test sets `NOTES_FILE`.

**Across items 1 to 4:** "today it prints no such line" is true only because the test does not exist yet. Nothing requires seeing each test fail against a wrong implementation, so a vacuous test moves from no line to `ok` just as a real one does.