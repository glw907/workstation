I checked the spec against the repo. One of its stated facts is false, and all six done items can pass on a wrong result.

## Questions

**1. The gate fails today, so what should happen to `test_export_csv`?**
The spec says `bash scripts/gate.sh` printed `ok` for every test and exited 0 on 2026-11-22. Run today it prints `FAIL test_export_csv` and exits 1. That test calls `bin/notes export`, a command that does not exist, and expects `1,"buy rope"`.

Done item 6 therefore cannot hold through the three files and the behaviour the spec describes. The plan depends on which of these the author wants:
- **Build `export`:** this is a second feature with an unspecified CSV format, and it changes the usage line again.
- **Remove or unlist the test:** this deletes someone's stated intent and conflicts with "nothing else changes".
- **Leave it failing:** item 6 then has to be rewritten, for example "no failures other than `test_export_csv`".

It also raises whether the spec was written against a different checkout. The other facts I checked do match this one: the four `usage` hits, `search rope` exiting 2 today, the origin URL, and the README count of 0.

**2. What does `notes search buy rope` do?**
`add` joins its arguments, so the owner will likely type this. The spec only defines one word. It could join into the phrase `buy rope`, search for `buy` and ignore the rest, or be a usage error. This is cheap to change later but user-visible, and no test pins it.

## Done list: items that can pass on a wrong result

1. **`test_search_finds`** passes on three wrong results:
   - **Whole-word matching:** no fixture has `ropes`, so the "`rope` finds `ropes`" rule is never tested.
   - **One-way case folding:** lowercasing the notes but not the word passes, and `search ROPE` then finds nothing.
   - **Sorted output:** alphabetical order instead of file order passes, because `Buy rope` sorts before `ROPE ladder` anyway.

2. **`test_search_plain_text`** passes on two wrong results:
   - **Glob matching:** an unquoted `[[ $line == *$word* ]]` passes both assertions, yet `search 'a?c'` would match `fix abc`.
   - **Word read as an option:** `grep -F "$word"` without `-e` or `--` passes, yet `search -v` is taken as a flag.

3. **`test_search_no_match`** only runs against a populated file. The "missing notes file counts as no match" rule has no test anywhere. A plain `grep` on a missing file exits 2 with an error on stderr and still passes all six items. Stderr is not checked in the populated case either.

4. **`test_search_missing_word`** only exercises the `search` path. A builder can print the new usage line there and leave `bin/notes:7` unchanged, so `notes bogus` still prints the old line. `test_usage` checks only the `usage:` prefix, so nothing catches it. Stdout is also unchecked, so the usage line could go to both streams.

5. **`grep -c "notes search" README.md` prints 1** counts lines, not accuracy. One line reading "notes search takes a regex" passes. A correct README that mentions the command on two lines fails.

6. **`bash scripts/gate.sh` exits 0** can only be reached today by going outside the spec (question 1). The cheapest route is dropping `test_export_csv` from the `for` list, which the spec itself notes stops a test running. The item would then pass with a test silently disabled.