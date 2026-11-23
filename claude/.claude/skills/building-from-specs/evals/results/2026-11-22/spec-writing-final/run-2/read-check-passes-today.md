I checked the spec's stated facts against the repo and they all hold. One question is left, and all six done items can pass on a wrong result, most seriously item 5, which passes today with nothing built.

## Questions

1. **What does `notes search buy rope` do, with more than one argument?** The spec only describes a single `<word>`, but `add` joins all its arguments, so an owner used to typing `notes add buy rope` unquoted will type this. The candidates are to search for the phrase `buy rope`, to print usage and exit 2, or to silently search for `buy` alone. Each gives different output, and the choice decides the argument handling, the usage wording, and whether a test is needed. I would guess the phrase search, to match `add`, but it is a guess about product behavior.

## Done list

1. **Item 5 passes today.** `grep -c notes README.md` prints 3 on the untouched README. A build that never mentions `search` in the README gets through. The check needs to look for `notes search`, which prints 0 today.

2. **Item 1 cannot tell substring match from whole-word match, and tests only a lowercase query.**
   - The fixture has no note where the word sits inside a longer word, so a whole-word implementation (`grep -w`) passes, and `rope` would not find `ropes`.
   - An implementation that lowercases the notes but not the query also passes, and `search ROPE` would find nothing.

3. **Item 3 does not cover the missing notes file.** No item does. A plain `grep` on a missing file exits 2 with an error on stderr, not 1 and silent, and that gets through.

4. **Item 2 does not cover a word that starts with a dash.** An implementation that passes the word to `grep` without `--` passes the test. `search -v` or `search -e` would then be read as an option, which breaks "plain text, never a pattern".

5. **Item 4 checks the new usage line only on the `search` path.** A build that prints the new line from the `search` branch and leaves `bin/notes:7` unchanged passes. `notes bogus` would still print the old line, since `test_usage` only checks the `usage:` prefix.

6. **Items 2 and 4 each hold two assertions in a runner without `set -e`.** A test function returns the status of its last command. If the two assertions are written as separate statements, not one `&&` chain, the first is ignored. In item 4, `search` with no argument could then die with an unbound-variable error and exit 1, and the test would still print `ok`.

7. **Item 6 passes today.** `bash scripts/gate.sh` exits 0 on the untouched tree. It only guards against regressions in the three existing tests. They barely exercise `add` and `list`, so it is weak evidence that "nothing about `add` or `list` changes".