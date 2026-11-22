I read `spec.md` and checked its claims against the repo. Everything under "What it rests on" and "Files" holds except the remote, which I could not reach from this sandbox.

## Questions I'd still need answered

1. **Does a search with no match exit 1 or 0?** The body says "No match prints nothing and exits 1", and item 2 agrees (`search '.*'` exits 1). Item 3 says `search zzz` gives exit 0. No consistent implementation passes both items 2 and 3, so either the tests or the code must bend. The answer also sets the exit code for a missing notes file, which "counts as no match". I'd guess 1, but it is a guess about the contract that scripts will depend on.

2. **Is the spec approved, and does `github.com/example/notes` accept a pull request?** The status line reads "awaiting approval", and the project rules say work is built from an approved spec. The remote URL is configured as the spec says, but network access to GitHub was denied here, so I couldn't confirm it exists. If it doesn't, the task has no way to end in a pull request.

3. **What does `notes search buy rope` do, unquoted?** It could search for the phrase (as `add` joins its arguments), search for `buy` and ignore the rest, or print usage. Silently ignoring the second word would return wrong notes, and the done list checks none of these.

## Done list: items that could pass on a wrong result

All four tests are written by the builder, and `tests/run.sh` treats a test function's last command as its result. Any test with two assertions not chained by `&&` prints `ok` even when the first fails. That applies to items 1, 2 and 4.

- **Item 1 (`test_search_finds`)**
  - Whole-word matching passes: no fixture note has `rope` inside a longer word, so the `rope` finds `ropes` rule is unchecked.
  - Printing every note passes if the test checks only that the two lines appear in order; the item says "prints", not "prints only" as item 2 does.
  - Sorted output passes, because `Buy rope` sorts before `ROPE ladder` anyway, so "oldest first" is unchecked.
  - One-directional case folding passes: `search ROPE` is never tried, so an implementation that lowercases the notes but not the word gets through.

- **Item 2 (`test_search_plain_text`)**
  - A word starting with `-` is untested: `grep -iF "$word"` passes, yet `search -v` would be read as an option.
  - The exit code of `search a.c` isn't asserted.

- **Item 3 (`test_search_no_match`)**
  - As written it passes only on the result the body calls wrong: exit 0 on no match.

- **Item 4 (`test_search_missing_word`)**
  - A second usage string inside the `search` branch passes while `bin/notes:7` keeps the old line. `notes bogus` then still prints the old usage, and `test_usage` checks only the `usage:` prefix.
  - Stdout isn't asserted empty.

- **Item 5 (README grep)**
  - Any single line containing "notes search" passes, including one that describes the command wrongly or says nothing about what it does.
  - It also fails a correct README that mentions the command on two lines, since `grep -c` counts lines and must print exactly 1.

- **Item 6 (gate exits 0)**
  - Beyond items 1–4 it adds only the three old tests. A change to `add` or `list` that those don't catch passes, such as `list` exit status or multi-word `add`.
  - Without items 1–4 it passes with the new tests left out of the `for` list.

One behaviour in the body has no item at all: a missing notes file. Every new test creates its file with `mktemp`, so an implementation that prints a grep "No such file" error and exits 2 passes all six.