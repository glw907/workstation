I've read the spec and checked its claims against the repo; here is the report. The spec's stated facts hold (gate output, the 4 `usage` hits, `search rope` exiting 2 today, README count 0). I could not check the remote: the sandbox blocked the request to `github.com`.

## Questions, ranked

1. **Is `passed test_search_finds` in item 1 meant to be `ok   test_search_finds`?** The loop in `tests/run.sh:16` only ever prints `ok   <name>` or `FAIL <name>`, and items 2 to 4 expect the `ok   ` form. As written, item 1 can only be met by having the test echo its own `passed` line, or by changing the loop and breaking items 2 to 4. I would assume a typo, but if it is deliberate the plan includes a harness change the spec never mentions.

2. **What does `notes search buy rope` do?** The spec only defines one `<word>`, while `add` joins all its arguments with `$*`. The three readings are: search for the phrase `buy rope`, ignore the extra argument, or print usage and exit 2. The owner will likely type it this way, and each reading gives a different result and a different test.

3. **Can the builder push to `origin` (`github.com/example/notes`) and open a pull request there?** The spec says the work ends in one pull request, but if that remote is a placeholder or has no credentials, the task cannot finish as described. Nothing in the done list covers the pull request either, so all six items can hold with uncommitted changes.

## Done list: items that pass on a wrong result

One point applies to items 1 to 4: each checks only that a function of that name returned 0. The harness has no `set -e`, so in a test with two assertions written as separate statements, only the last one counts. That matters most for items 2 and 4.

- **Item 1 (`test_search_finds`)**
  - Whole-word matching (`grep -iw`) passes, because no fixture contains `ropes`. The spec's own example, `rope` finds `ropes`, is untested.
  - Alphabetically sorted output passes, because `Buy rope` sorts before `ROPE ladder` anyway. "Oldest first" is untested.
  - One-directional case folding passes: only the note is uppercase (`ROPE ladder`), so `search ROPE` finding nothing would get through.
  - "Prints `Buy rope` then `ROPE ladder`" does not say "only", so a contains-style assertion passes when extra lines are printed.
  - A test that simply echoes `passed test_search_finds` passes (see question 1).

- **Item 2 (`test_search_plain_text`)**
  - A word starting with `-` (taken as a grep option when passed without `-e` or `--`) is untested.
  - A word containing a backslash (mangled by `awk -v`) is untested.
  - If the two assertions are not chained, `search a.c` printing both `fix a.c` and `fix abc` passes whenever the `.*` check passes.

- **Item 3 (`test_search_no_match`)**
  - The missing notes file is never tested, because every test creates its file with `mktemp`. A plain `grep ... "$file"` on a missing file prints an error and exits 2, not the silent exit 1 the spec requires, and all six items still pass.
  - Stderr is not checked, so a "no notes found" message passes.

- **Item 4 (`test_search_missing_word`)**
  - A second usage string added only in the search branch passes, with `bin/notes:7` left unchanged. `notes bogus` then still prints the old line, and `test_usage` checks only the `usage:` prefix.
  - If the assertions are not chained, a bare `search` that dies on an unbound `$2` (exit 1) passes as long as `search ''` is right.
  - Stdout is not checked, so usage printed to both streams passes.

- **Item 5 (README grep)**
  - Any single line containing `notes search` passes, including one that describes the command wrongly (case-sensitive, pattern matching) or not at all.
  - It also fails on right results: a correct README that mentions the command on two lines prints 2, and a line wrap between `notes` and `search` prints 0.

- **Item 6 (gate exits 0)**
  - It exits 0 today with nothing built.
  - It is a regression check with only two thin tests behind "nothing about `add` or `list` changes". Breaking `list` on a non-empty multi-line file, or `add` with several arguments, would not be caught.