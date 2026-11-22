I've read the spec, checked its stated facts against the repo (they all hold), and run a few deliberately wrong implementations against the spec's fixture. One question is left, and the done list lets several wrong results through.

## Questions I'd still need answered

1. **What does `notes search buy rope` do, with two unquoted arguments?** The spec only defines a single `<word>` and the missing or empty case. `add` joins its arguments with spaces, so the owner may expect search to do the same. The options are: join into the phrase `buy rope`, reject with usage and exit 2, or search the first word and ignore the rest. Each is a different user-visible behavior and a different test, and no done item covers it. Silently ignoring the extra words is the one that would do damage, and nothing would catch it.

Nothing else needs the author.

## Done list: items that pass on a wrong result

One point applies to items 1 to 4: each is satisfied by the `ok` line printing, and the builder writes the test. A test with a weaker body than the spec describes still prints `ok`, so only the reviewer's read stands between the description and the check.

**Item 1 (`test_search_finds`)**
- **Whole-word matching passes.** No fixture note has `rope` inside a longer word, so `grep -iwF` passes all four tests yet fails the spec's own example, `rope` finds `ropes`. I ran this.
- **One-sided case folding passes.** The fixture only searches a lowercase word. An implementation that lowercases the note but not the word passes, and `search ROPE` then finds nothing. I ran this.
- **Alphabetical order passes.** `Buy rope` sorts before `ROPE ladder`, so output sorted by text instead of by age gets through.
- **Extra output may pass.** The item says "prints `Buy rope` then `ROPE ladder`", not "only" as item 2 does, so a contains-style assertion satisfies the wording.

**Item 2 (`test_search_plain_text`)**
- **A word starting with `-` is taken as an option.** `grep -iF "$word"` without `--` passes. I ran this. `search -v` then treats the word as a grep flag.
- **Backslashes are untested.** An `awk -v` implementation mangles `a\.c` and passes.
- **Exit status is unchecked for `search a.c`.** The item asserts only the output.

Plain regex and unquoted glob implementations are caught; I ran both.

**Item 3 (`test_search_no_match`)**
- **A crash passes.** Empty stdout and exit 1 is also what a `set -e` script dying looks like, and stderr is not asserted.
- **The missing notes file is uncovered.** A plain `grep` on a missing file prints `No such file or directory` and exits 2, which reads as a usage error. `list` treats a missing file as empty, and the spec never says what search does.

**Item 4 (`test_search_missing_word`)**
- **The old usage line can survive on the fallback branch.** The new line could be printed only in the search branch while `notes bogus` still prints the old one. `test_usage` checks only the `usage:` prefix, so nothing fails.
- **Usage on stdout may pass.** Stdout is not asserted empty, so a test that captures `2>&1` accepts usage printed to the wrong stream.

**Item 5 (README grep)**
- **Any line containing the string passes.** `grep -c "notes search"` prints 1 for "notes search is not supported yet", or for a description that gets the behavior wrong.
- **It also fails a correct README.** `grep -c` counts lines, so a description plus an example line prints 2.

**Item 6 (gate exits 0)**
- **It adds only the three existing tests to items 1 to 4.** "Nothing about `add` or `list` changes" rests on two single-case tests, so a change to how `add` joins several arguments passes.
- **A changed exit code for an unknown command passes.** `test_usage` never checks the exit status.