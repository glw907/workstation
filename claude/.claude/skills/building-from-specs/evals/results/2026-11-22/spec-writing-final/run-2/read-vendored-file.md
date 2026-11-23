I read `spec.md` against the repo. Its stated facts check out (gate passes, 4 `usage` hits, `search rope` exits 2 today), but one question blocks planning and every item on the done list can pass on a wrong result.

## Questions, ranked

**1. Is the builder allowed to edit `lib/strings.sh`?**
The spec says the file "gains a `contains` helper". `lib/strings.sh:1` says "copied from the shkit project at v2.3.0. Never edit this copy", and `README.md:10-11` says a change goes to shkit first and is copied back. The spec's "What it rests on" never mentions this rule, so I can't tell whether the author is overriding it or missed it. The answer picks one of three plans:
- **Edit in place:** the header and README lines become false and need changing, and the next copy-back from shkit silently deletes `contains` and breaks search.
- **Keep the helper in `bin/notes`:** the Files list shrinks to three, and nothing vendored is touched.
- **shkit first:** this is work in another repo I can't see, and it no longer fits "one task, one pull request".

**2. How is `bin/notes` installed and run?**
`bin/notes` does not source `lib/strings.sh` today, and the README calls it "a one-file notes tool". If the owner copies or symlinks that one file onto their PATH, a new `source ../lib/strings.sh` fails under `set -e` and takes `add` and `list` down with it. The tests always run `bin/notes` from the repo root, so they would not notice. This only matters if question 1 lands on a helper in `lib/`.

**3. What does `notes search buy rope` do, with two unquoted arguments?**
`add` joins its arguments with spaces; the spec only covers a missing or empty word. Joining, ignoring the extras, or printing usage are all defensible, and the owner sees the difference. I would join, to match `add`, but that is a guess.

The spec's status is "awaiting approval", so the build should not start on this text until the owner approves it.

## Done list: items that could pass on a wrong result

All four test items also rest on the reviewer reading each test body: the printed `ok` line alone passes with a test that asserts less than the spec says. Beyond that:

1. **`test_search_finds`** passes on:
   - **Whole-word matching.** No fixture note has `rope` inside a longer word, so `grep -iwF` passes while `rope` fails to find `ropes`, breaking a stated rule.
   - **One-sided case folding.** Every test query is lowercase, so an implementation that lowercases the notes but not the word passes while `search ROPE` finds nothing.
   - **Wrong order.** The two matches are already in file order and nothing reorders them, so "oldest first" is only checked if the test compares the whole output in order.

2. **`test_search_plain_text`** passes on:
   - **A word starting with `-`.** `grep -iF "$word"` without `--` passes, while `search -v` is read as a grep option and prints the non-matching notes.
   - **A word containing a backslash.** `awk -v w="$word"` passes while awk interprets the escapes.
   - **A wrong exit code on `search a.c`.** The item checks only its output.

3. **`test_search_no_match`** passes on:
   - **A missing notes file handled wrongly.** Every test creates its file with `mktemp`, so "a missing notes file counts as no match" is never exercised. `grep` on a missing file prints an error and exits 2, and passes.
   - **Noise on stderr.** Only stdout is checked.

4. **`test_search_missing_word`** passes on:
   - **The old usage line surviving at `bin/notes:7`.** A builder can add a second, new usage line in the `search` branch. `notes bogus` then still prints the old text, and `test_usage` checks only the `usage:` prefix.
   - **Usage also printed to stdout.** That passes unless the test checks stdout is empty.

5. **`grep -c "notes search" README.md` prints 1** passes on:
   - **Any single line containing the phrase**, such as "notes search is not supported" or a description with the wrong behaviour.
   - **A README that still says `lib/strings.sh` is "never edited here"** after this task edits it.

   It also fails a correct README that mentions the command on two lines.

6. **`bash scripts/gate.sh` exits 0** passes on:
   - **Existing tests dropped or weakened.** The task edits `tests/run.sh`, and a test runs only if it is in the `for` list, so "nothing about `add` or `list` changes" is guarded only by two thin tests the builder can alter.
   - **The breakage in question 2.** `add` and `list` fail when run through a symlink, and the gate still passes.

I could not check that `origin` is reachable or pushable: the sandbox blocks github.com.