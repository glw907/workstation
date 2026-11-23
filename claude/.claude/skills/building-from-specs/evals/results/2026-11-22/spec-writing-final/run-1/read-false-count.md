I read `spec.md` and checked its stated facts against the repo. Most hold, one is false, and one I could not check.

## Facts in the spec that don't hold

- **The usage count is wrong.** The spec says `git grep -n usage -- bin tests` found 1 hit. It finds 4: `bin/notes:7`, plus `tests/run.sh` lines 12, 13 and 15, which are `test_usage` and the `for` list. `test_usage` checks only that the first word on stderr is `usage:`, so it passes with the old line, the new line, or any line.
- **The remote is unverified.** `origin` is `github.com/example/notes`, as the spec says, but the sandbox blocked the network check, so I can't say whether it exists or accepts a push.

## Questions, ranked

1. **Should `test_usage` be tightened to the full new usage line?** The spec treats `bin/notes:7` as the only place that knows about usage, so it never decides this. If yes, the task edits an existing test. If no, nothing checks the usage line on the `notes bogus` and bare `notes` paths (see item 4 below).
2. **What does `notes search buy rope` do, with two unquoted words?** `add` joins its arguments with spaces, so the owner will likely type search the same way. Joining them, exiting 2 with usage, and searching only `buy` are all defensible, and each is a different behavior the owner sees and a different test.
3. **Is `github.com/example/notes` a real remote the builder can push to?** The name reads like a placeholder. If it is one, the task cannot end in a pull request and the plan's last step changes.

## The done list: items that could pass on a wrong result

All of items 1 to 4 share one weakness: the check is the `ok` line, and the builder writes both the test and the code. A test that asserts less than the spec's sentence still prints `ok`. Beyond that:

- **Item 1 (`test_search_finds`)** passes on three wrong results:
  - **Whole-word matching.** No fixture note has `rope` inside a longer word, so `grep -iwF` passes here and in item 2, while `rope` fails to find `ropes`.
  - **One-sided case folding.** The query is always lowercase, so code that lowercases the notes but not the word passes, and `search ROPE` finds nothing.
  - **Extra output.** The item says "prints `Buy rope` then `ROPE ladder`", not "only", so a test that checks the two lines appear in order passes with other lines around them.
- **Item 2 (`test_search_plain_text`)** covers only `.` and `.*`. These get through:
  - A word starting with `-`, such as `search -v`, read as a grep option.
  - `?` and `[` under a shell-glob implementation: `search 'a?c'` would print both `fix a.c` and `fix abc`.
  - A backslash under an awk implementation.
  - Noise on stderr for `.*`, if "prints nothing" is checked as stdout only.
- **Item 3 (`test_search_no_match`)** never tests the missing notes file, because the fixture always creates one with `mktemp`. `grep` on a missing file exits 2 with "No such file" on stderr and still passes all six items. An empty file is untested too.
- **Item 4 (`test_search_missing_word`)** checks the new usage line only on the `search` path. Code that prints the new line there and leaves `notes bogus` and bare `notes` on the old line passes, since `test_usage` checks only the first word. It also passes if usage goes to stdout as well as stderr.
- **Item 5 (README grep)** passes on any single line containing `notes search`, including one that describes the command wrongly or not at all. It also fails a correct README: `grep -c` counts lines, so a usage block plus a sentence prints 2.
- **Item 6 (gate exits 0)** proves only what the tests assert, so every hole above passes it. It also passes in two further cases:
  - An existing test is weakened or dropped from the `for` list; items 1 to 4 require only the four new `ok` lines.
  - `add` or `list` regress in a way the three existing tests miss. For example, `list` on a missing file starting to exit non-zero, since `test_list_empty` checks only for empty output.