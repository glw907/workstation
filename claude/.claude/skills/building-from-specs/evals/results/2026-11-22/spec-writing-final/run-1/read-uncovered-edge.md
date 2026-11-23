The spec has a done list, and its factual claims check out against the repo (gate green, 4 `usage` hits, `search rope` exits 2 today, README count 0). One question is left, and every done item can pass on a wrong result.

## Question

**1. What does `notes search buy rope` do, with more than one argument after `search`?**
The spec only says `<word>` and covers the missing and empty cases. There are three defensible readings:
- **Join:** treat the arguments as one phrase `buy rope`, the way `add` joins its arguments with `$*`.
- **Reject:** print the usage line and exit 2.
- **Ignore:** search for `buy` and drop the rest.

Each gives a different result, a different test, and arguably a different usage line. The owner is likely to type it unquoted, and under the third reading they get silently wrong results.

## Done list: items that can pass on a wrong result

I built deliberately wrong variants and ran the spec's described assertions against them; each variant below passed all of items 1 to 4.

**Item 1 (`test_search_finds`)**
- **Whole-word matching gets through.** The spec requires `rope` to find `ropes`, but the fixture has `rope` only as a whole word. A `grep -iwF` variant passes all four tests and then skips a `two ropes` note.
- **Sorted or de-duplicated output gets through.** The two expected lines are already in alphabetical order and unique, so `| sort -u` passes even though the spec says oldest first.
- **Extra output may get through.** The item says "prints `Buy rope` then `ROPE ladder`", not "prints only", so a test written as a contains-check also satisfies it.

**Item 2 (`test_search_plain_text`)**
- **Partial escaping gets through.** A variant that escapes only `.` and `*` and then does a regex match passes. `search 'a[.b]c'` then prints both `fix a.c` and `fix abc`.
- **A word starting with `-` is untested.** Without a `--` guard the word is read as a grep option: `search -c` printed `0`, and `search -v` hung waiting on stdin.
- **The exit code of `search a.c` is not asserted.**

**Item 3 (`test_search_no_match`)**
- **A missing notes file is untested.** The fixture file always exists. A grep-based variant given a file that does not exist prints `grep: …: No such file or directory` and exits 2, the usage-error code, instead of printing nothing and exiting 1.
- **Stderr is not checked.** A "no matches" message on stderr passes.

**Item 4 (`test_search_missing_word`)**
- **The old usage line can survive on the fallback path.** The item checks the new line only for `search` and `search ''`. A variant that adds a second usage string for `search` and leaves `bin/notes:7` unchanged passes everything, because `test_usage` checks only the `usage:` prefix. `notes bogus` then still prints the old line.
- **Stdout is not asserted empty.**

**Items 1 to 4 together**
- **An `ok` line only means the test function returned 0.** `tests/run.sh` runs without `set -e`, so a test with its assertions on separate lines returns only the last one's status. Items 1, 2 and 4 each have several assertions and would print `ok` with the earlier ones failing, unless they are chained with `&&` as the existing tests are.

**Item 5 (README)**
- **Any one line containing "notes search" passes.** `grep -c` counts lines, so a stub or a wrong description (case-sensitive, a pattern, whole words) gets through.
- **A correct README can fail.** One that mentions the command on two lines, such as a description and an example, prints 2.

**Item 6 (gate)**
- **Exit 0 does not show that `add` and `list` are unchanged.** It only shows that the tests still in the `for` list pass. Dropping or weakening an existing test passes, and the two existing tests are thin.
- **Nothing checks the pull request.** The spec says "one pull request", but no item requires that it exists.