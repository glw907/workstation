I read the spec and checked its claims against the repo. Two questions remain, and four done items
can pass on a wrong result.

## Questions, ranked

1. **What does `search buy rope`, with two words, do?** It could join the words as `add` does, search
   only the first, or print the usage line. Each gives the user a different result, and it decides
   whether a fifth test is needed.
2. **Does a word that starts with a dash count as text?** `search -v` handed to grep is read as an
   option. The plan needs `--` or a test that pins it.

## Done list: items that can pass on a wrong result

1. **`test_search_finds`.** "Prints X then Y" doesn't say "only", so extra lines get through. Both hits
   are whole words, so the rule that `rope` finds `ropes` is never tested.
2. **`test_search_plain_text`.** The exit code of `search a.c` isn't asserted.
3. **`test_search_no_match`.** Stderr isn't checked, so a "no match" message there gets through.
4. **`test_search_missing_word`.** A test that captures with `2>&1` passes with the usage line on stdout.
5. **Item 5 already passes.** `grep -c notes README.md` prints 2 today with nothing
   built, so the item can't show that the README names the new command.
