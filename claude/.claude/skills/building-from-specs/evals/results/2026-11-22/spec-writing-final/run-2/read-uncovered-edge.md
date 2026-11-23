I read the spec, checked its claims against the repo, and ran four deliberately wrong implementations against the tests as the spec describes them. All four passed every test.

The spec's stated facts hold: the gate is green, `git grep` finds the 4 hits, `search rope` exits 2 today, and the README count is 0. I could not check that `origin` is reachable, because the sandbox blocks GitHub.

## Questions

1. **What does `notes search fix abc` do with more than one argument?** `add` joins its arguments into one text, but search takes `<word>` and the spec says nothing about extras. The choices are a phrase search for `fix abc`, a usage error with exit 2, or silently searching `fix` only. The last is what a naive build does: it printed both `fix a.c` and `fix abc`. The answer changes the argument handling and adds a test. If no answer comes, I would join the arguments as `add` does.

That is the only question I can't settle myself. For a missing notes file I would treat it as no match (nothing printed, exit 1), and for a word starting with `-` I would treat it as plain text.

## Done list: items that pass on a wrong result

1. **Item 1 (`test_search_finds`)** has three wrong results that get through:
   - **Whole-word matching:** the fixture has no note where `rope` sits inside a longer word, so `grep -iFw` passes, and the spec's own `rope` finds `ropes` rule is untested.
   - **One-way case folding:** a build that lowercases the note but not the word passes, because the only query is lowercase. `search ROPE` then found nothing and exited 1.
   - **Sorted output:** `Buy rope` sorts before `ROPE ladder`, so alphabetical order passes as "oldest first".

   The item also says "prints", not "prints only", so a test that checks containment would satisfy it.

2. **Item 2 (`test_search_plain_text`)** covers only `.` and `*`, which leaves two holes:
   - **Backslash:** an awk build matched `fix a.c` for `search 'a\.c'`, where no note contains that text.
   - **Leading dash:** a grep build without `--` read `search -v` as an option and exited 1 with no output.

3. **Item 3 (`test_search_no_match`)** always runs against an existing file and checks only stdout. With no notes file, the grep build printed `grep: ... No such file or directory` and exited 2, which is the usage error's code. It also repeats the `.*` half of item 2, so it adds no new case.

4. **Item 4 (`test_search_missing_word`)** checks the new usage line only on the search path. A build that leaves `bin/notes:7` alone passes: `notes bogus` still printed `usage: notes add <text> | notes list`. `test_usage` checks only the `usage:` prefix, so nothing catches it.

5. **Item 5 (README grep)** passes on any single line containing `notes search`, including one that describes the command wrongly. It also fails a correct README that mentions the command on two lines.

6. **Item 6 (gate exits 0)** adds nothing beyond items 1 to 4 and the three existing tests, so every wrong result above passes it too.

**Across items 1 to 4:** each check is the `ok` line, and the builder writes the test that prints it. A test body weaker than its description still prints `ok`, so only the reviewer stands between that and done.

**Missing from the list:** no item requires the pull request to exist or the review to accept, though the spec says the work is one pull request.