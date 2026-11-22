I read the spec and the repo, and checked the spec's stated facts against the code. One question blocks a good plan, a second is worth answering, and all six done items can pass on a wrong result.

## Questions, ranked

1. **Is `completions/notes.bash` in scope, so that it gains `search`?** The spec says the task changes only `bin/notes`, `tests/run.sh`, and `README.md`, but an existing test it never mentions, `test_completions_match`, makes that impossible.
   - **The conflict:** the test (`tests/run.sh:15`) pulls every `notes <word>` out of `bin/notes` and requires the set to equal the words in `completions/notes.bash`, which today offers `add list`. The required usage line adds `notes search`, so the test fails and done item 6 cannot hold.
   - **Why it changes the plan:** the only fix inside the listed files is to weaken or drop that test in `tests/run.sh`, which is the wrong one. The right fix touches a fourth file, which a reviewer holding the diff to the spec's file list would flag.
   - **My assumption if unanswered:** add `search` to the completion and leave the test alone.

2. **What does `notes search buy rope` (two unquoted arguments) do?** The spec covers a missing or empty word but not extra ones.
   - **The options:** `add` joins all its arguments with spaces, so search could treat them as the phrase `buy rope`. It could also search for `buy` only, or print usage and exit 2.
   - **Why it changes the plan:** this is the owner's most likely slip, and each option gives a different visible result and a different test.
   - **My assumption if unanswered:** join them, to match `add`.

## Done list: items that could pass on a wrong result

I ran a deliberately wrong `grep -iwF "$word" "$file"` against the spec's four fixture notes to check items 1 to 3; the rest are from reading the code.

1. **`test_search_finds`** passes on whole-word matching. The wrong implementation printed `Buy rope` then `ROPE ladder` and exited 0, and it did not find `ropes` when I added that note. No fixture note has the word inside a longer word, so the `rope` finds `ropes` rule is untested. Alphabetical output also passes, because the two matches sort the same way they were added.

2. **`test_search_plain_text`** passes when a word that starts with `-` is read as an option. With plain `grep -iF "$word" "$file"`, `search -v` makes grep take the file path as the pattern and wait on stdin. Neither `a.c` nor `.*` exercises that.

3. **`test_search_no_match`** never exercises the missing notes file, because every new test creates its file. On a missing file the wrong implementation printed `grep: … No such file or directory` and exited 2, the usage error's code. No item checks "a missing notes file counts as no match".

4. **`test_search_missing_word`** passes if the new usage line is printed only by the `search` branch while `bin/notes:7` keeps the old text. `notes bogus` would still print the old line, and `test_usage` checks only the `usage:` prefix.

5. **The README grep** counts lines containing `notes search`, not what they say. One line that describes the command wrongly prints 1. A correct README that mentions it on two lines prints 2 and fails.

6. **`bash scripts/gate.sh` exits 0** passes if `test_completions_match` is loosened or removed from the `for` list, which is the in-scope way out of question 1. It also passes if any existing test is dropped, since no item requires the four current `ok` lines to still print.

The spec's other stated facts hold: the gate prints four `ok` lines and exits 0, `bin/notes search rope` prints usage and exits 2, the `usage` grep gives the 4 hits described, and `origin` is `github.com/example/notes`. I did not check push access to `origin`.