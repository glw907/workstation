I read `spec.md` against the repo and ran the gate. The spec's claims about today's state hold: the gate prints three `ok` lines and exits 0, `git grep` finds the 4 hits, and `search rope` exits 2. I could not check `origin`, because the sandbox blocks github.com.

## Questions, ranked

1. **Is `passed test_search_finds` in item 1 a typo for `ok   test_search_finds`?** `tests/run.sh:16` prints only `ok   <name>` or `FAIL <name>`, and items 2 to 4 expect the `ok` form. If it is a typo, the runner loop only gains four names. If it is meant literally, the builder has to change the runner's output or echo the string from inside the test, which nothing else in the spec asks for.

2. **What does `search` do with more than one argument, such as `notes search buy rope`?** `add` joins its arguments with `$*`, so joining into the phrase `buy rope` is one reading. Ignoring the extras or exiting 2 with usage are the others. Each gives a different result for the most likely slip at the keyboard, and no test pins it.

3. **Does a push to `origin` (`github.com/example/notes`) work for the builder?** The URL looks like a placeholder. If it is, the task cannot end in a pull request and the plan needs the real remote.

## Done list: items that pass on a wrong result

The spec has a done list with six items. Every one can pass on a wrong result.

- **Item 1** cannot pass on a correct build with the current runner, as in question 1. The cheapest ways to make it pass, an `echo` in the test or a special-cased runner line, print the string whether or not the assertion holds. Its assertion also misses these:
  - **Whole-word matching:** `grep -iwF rope` prints the same two lines, and no fixture note has `ropes`, so the "inside a longer word" rule is untested.
  - **Sorted output:** alphabetical order is the same as insertion order for these two lines, so sorting instead of oldest-first passes.

- **Item 2** passes on an implementation that mishandles words the two probes don't cover:
  - **Leading dash:** `search -v` with `grep -iF "$word"` and no `--` is read as an option.
  - **Backslash:** a word with a backslash passed through `awk -v` is unescaped before it is matched.

- **Item 3** checks only stdout and only a notes file that exists:
  - **Stderr message:** a "no notes found" line on stderr passes, though the spec says no match prints nothing.
  - **Missing notes file:** `mktemp` always creates the file, so the "missing file counts as no match" rule is never run. A plain `grep -iF -- "$word" "$file"` passes all four tests, then prints a grep error and exits 2 on a fresh machine.

- **Item 4** checks the new usage line only on the `search` path. A build that adds a separate message for `search` and leaves `bin/notes:7` unchanged passes. `notes bogus` then still prints the old line, and `test_usage` checks only the `usage:` prefix.

- **Item 5** counts lines containing the string, not correct content. A README line that says `notes search` and describes it wrongly passes, as does one that says nothing else. It also fails a correct README that mentions the command on two lines.

- **Item 6** exits 0 today with nothing built, so on its own it shows only that the old tests still pass. Those tests are thin: a build that changes `list` on a non-empty multi-line file passes, so "nothing about `add` or `list` changes" is barely held.

- **Items 1 to 4 together:** an `ok` line shows only that the test function's last command succeeded (`tests/run.sh:16`). Items 2 and 4 each carry several assertions. If they are written as separate statements rather than chained with `&&`, only the last one counts. For example, `search ''` could match every note and exit 0, and the test would still print `ok` if the bare `search` check comes last.