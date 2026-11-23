I'd need three questions answered before planning this, and every item on the done list can pass on a wrong result. The spec's stated facts all held when I checked them: the gate passes, the usage grep gives 4 hits, `search rope` exits 2 today, and the README count is 0.

## Questions, ranked

**1. May the task edit `lib/strings.sh`, given that the repo says never to?**
The spec's Files section says `lib/strings.sh` gains a `contains` helper. The file's own header says "copied from the shkit project at v2.3.0. Never edit this copy", and `README.md:10-11` says a change goes to shkit first and is copied back. The spec doesn't mention this rule, and shkit's location isn't given anywhere. The plan differs for each reading:
- **Edit the copy here:** this breaks the repo's rule, leaves the README false, and the next copy-back from shkit silently deletes `contains` and breaks search.
- **Land it in shkit first:** this is a second repo and a second pull request, outside "one task, one pull request", in a project I can't locate.
- **Put the helper in `bin/notes` or a new non-vendored file:** this contradicts the Files list, though "the implementation is the builder's choice" may allow it.

**2. How is `bin/notes` invoked in real use: from the checkout, or copied or symlinked onto `PATH`?**
`bin/notes` sources nothing today, and the README calls it a one-file tool. If search depends on a file in `lib/`, a copied `bin/notes` fails on `add` and `list` too, because a failed `source` under `set -e` kills the script. A symlinked one needs path resolution. The answer decides whether the helper can live outside `bin/notes` at all.

**3. What does `notes search buy rope` (two unquoted arguments) do?**
The spec says `<word>` and is silent on extra arguments. `add` joins its arguments with spaces. Joining, searching only the first word, and a usage error give three different results and need different tests. Silently ignoring the second word would return wrong matches for a likely first use.

## Done list: items that pass on a wrong result

**Item 1, `test_search_finds`**
- **Whole-word matching passes.** No fixture has `ropes`, so `grep -iw` gets through although the spec says `rope` finds `ropes`.
- **Lowercasing only the notes passes.** The query is already lowercase, so `search ROPE` or `search Rope` could find nothing.
- **Order is only checked if the test compares full stdout.** A test that greps for each line separately would pass on newest-first.

**Item 2, `test_search_plain_text`**
- **A word starting with `-` is untested.** `grep -iF "$word"` without `--` passes, yet `search -v` would be read as a grep option.
- **A word containing a backslash is untested.** An `awk -v` implementation, which processes escapes, passes.
- **The exit status of `search a.c` is not asserted.**

**Item 3, `test_search_no_match`**
- **The missing-file case is untested.** Every test creates its file with `mktemp`. An implementation that greps a nonexistent file passes, yet it prints a grep error and exits 2, which collides with the usage exit code.

**Item 4, `test_search_missing_word`**
- **Two diverging usage strings pass.** A builder can print the new line from the `search` branch and leave `bin/notes:7` unchanged. `notes bogus` then prints the old usage, and `test_usage` checks only the `usage:` prefix.
- **Usage on stdout passes if the test captures `2>&1`.** The item doesn't require stdout to be empty.

**Items 1 to 4 together**
- **A cwd-relative `source lib/strings.sh` passes.** `tests/run.sh` does `cd` to the repo root and calls `bin/notes` by relative path, so the tool would break for all three commands when run from any other directory.
- **Each item only requires an `ok` line.** A test function with a weaker body than described prints the same line, so only the reviewer catches it.

**Item 5, README grep**
- **Any single line containing "notes search" passes.** That includes an inaccurate description.
- **A stale vendoring claim passes.** If the task edits `lib/strings.sh`, the README's "never edited here" line becomes false and the grep doesn't notice.
- **A correct README can fail.** `grep -c` counts lines, so a correct README that mentions the command on two lines prints 2.

**Item 6, gate exits 0**
- **Dropping or weakening an existing test passes.** The gate runs only what is in the `for` list, so removing `test_usage` or the `add` and `list` tests still exits 0.
- **"Nothing about `add` or `list` changes" rests on two thin tests.** Nothing else checks it.
- **The vendoring rule and the `contains` helper are unchecked.** The gate passes whether or not the copy was edited and whether or not the helper exists or is used.