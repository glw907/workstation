I've read the spec and checked it against the repo; here is the report.

## Questions I'd still need answered

1. **What does `notes search rope ladder` do?** The spec only defines one word. `add` joins all its arguments into one note, so joining them into a phrase is the natural mirror, but ignoring the extras or printing usage with exit 2 are equally defensible. The owner will see this the first time they type two words, and the three readings give different output and exit codes. A quoted phrase (`search 'rope ladder'`) works under any reading, since the match is plain text.

2. **Is `origin` a real remote the builder can push to?** The spec ends in a pull request to `github.com/example/notes`, which looks like a placeholder. I couldn't check: the sandbox denied the connection to github.com. If it is not pushable, the last step of the plan has nowhere to land.

One correction that needs no answer: the spec says `git grep -n usage -- bin tests` found 1 hit. It finds 4. The other three are in `tests/run.sh` (`test_usage`, its body, and the `for` list). The spec's conclusion still holds, since only `bin/notes:7` holds the usage text. But the miss hides that `test_usage` checks only the first word, `usage:`, which opens the hole in item 4 below. The spec's other "rests on" claims that I could check hold.

## The done list, item by item

Two problems cut across items 1 to 4:

- **The observable is only the `ok` line.** A test body of `true` prints it; what the test asserts is checkable only by reading it.
- **Unchained assertions pass silently.** `tests/run.sh` has no `set -e`, so a test function returns the status of its last command. I confirmed a function whose first assertion fails and whose second passes prints `ok`. Items 2 and 4 each need two assertions.

I ran the wrong implementations in items 1 and 2 against the spec's four notes; each one gives exactly the output and exit codes the tests expect.

1. **`test_search_finds` can pass on a wrong result.**
   - **Whole-word matching passes** (`grep -iwF`). No fixture note has `rope` inside a longer word, so the `rope` finds `ropes` rule is untested.
   - **One-sided case folding passes.** Lowercasing the note but not the word gets `search rope` right, while `search ROPE` finds nothing and exits 1.
   - **Extra lines can pass.** The item says "prints `Buy rope` then `ROPE ladder`", not "only" as item 2 does, so a containment check lets extra output through.
   - **Order is barely pinned.** File order and alphabetical order agree for these two lines.

2. **`test_search_plain_text` can pass on a wrong result.**
   - **Partial escaping passes.** An implementation that escapes only `.` and `*` and still runs a regex gets both assertions right, but `search '^fix'` prints two notes and `search '[a-z]'` prints all four.
   - **A word starting with `-` is untested.** `search -v` reaches grep as an option unless the builder uses `-e` or `--`.

3. **`test_search_no_match` is sound for what it states**, but the missing-file rule sits beside it with no item at all. `grep` on a missing file prints an error and exits 2, and under `set -e` that becomes the command's result. The spec wants silence and exit 1. That wrong result passes all six items.

4. **`test_search_missing_word` can pass on a wrong result.**
   - **Two usage lines pass.** A builder can add a new usage line inside the `search` branch and leave `bin/notes:7` unchanged. `notes bogus` and bare `notes` then print the old line, and `test_usage` still passes.
   - **A weak comparison passes today.** If the new test copies `test_usage` and checks only the first word, it passes on the unchanged tool, since `search` already exits 2 with a usage line.
   - **Stdout is not checked.** A usage line printed to both streams passes.

5. **`grep -c "notes search" README.md` prints 1 on any single line containing that string**, whatever it says. "TODO: notes search" passes, and so does a line describing the word as a pattern. It also fails a right result: `grep -c` counts lines, so a README that mentions the command on two lines prints 2. A line wrap between `notes` and `search` prints 0.

6. **`bash scripts/gate.sh` exits 0 today, with nothing built.** It also exits 0 if an existing test is dropped from the `for` list or weakened, because nothing requires the three current `ok` lines to still appear. "Nothing about `add` or `list` changes" rests on those two existing tests alone; a regression such as `add` overwriting instead of appending would pass.