I read `spec.md` and checked its stated facts against the repo. They hold: the gate prints three `ok` lines and exits 0, `search rope` prints usage and exits 2 today, and `git grep` finds the 4 hits. I could not check `origin`, because the sandbox blocks github.com.

## Questions, ranked

1. **Is `tests/run_all.sh` in done item 1 a slip for `tests/run.sh`?** No such file exists; `tests/` holds only `run.sh`, and items 2 to 4 all name `run.sh`. If it is a slip, item 1 as written can never pass and a builder held to the list stalls. If it is meant, the builder creates a fourth file that the Files section doesn't list and the gate never runs. I'd plan on `run.sh`, but a builder following the list literally could go the other way.

2. **What does `notes search buy rope` do, with more than one argument?** `add` joins its arguments with spaces, so the owner will likely type a phrase the same way. The spec says only `<word>`. Joining to search for `buy rope`, searching `buy` and ignoring the rest, and exiting 2 with usage are all defensible, and each needs a different test. It is the first thing a user would hit that the spec doesn't decide.

3. **Does `github.com/example/notes` exist, and can the building session push to it?** The name looks like a placeholder and I could not reach it. If it isn't real, the "one pull request" ending has no path, and the plan needs another way to hand off.

## Done list: items that pass on a wrong result

**Items 1 to 4, all of them.** Each checks only that an `ok` line prints. A test that asserts less than the item describes, or nothing at all, prints the same line. Only the reviewer reading the test body would catch this.

**Item 1 (`test_search_finds`)**
- **Whole-word matching passes.** The fixture has no note where `rope` sits inside a longer word, so `grep -iw` passes while `rope` fails to find `ropes`, which the spec requires.
- **One-sided case folding passes.** The query is always lowercase, so an implementation that lowercases only the note finds nothing for `search ROPE`.
- **Sorted output passes.** `Buy rope` sorts before `ROPE ladder`, so alphabetical output looks the same as oldest first.
- **A test outside the gate passes.** Read literally, a new `tests/run_all.sh` holding this test satisfies the item while the gate never runs it.

**Item 2 (`test_search_plain_text`)**
- **A word starting with a hyphen is untested.** `grep -iF "$word"` without `--` passes both assertions, yet `search -v` is read as an option and prints every non-matching note.
- **Glob characters are untested.** A bash `[[ $line == *$word* ]]` match passes: `a.c` has no glob characters, and `.*` happens to print `fix a.c` and fail correctly. `search '*'` would print every note and `search 'a?c'` would print `fix abc`.

**Item 3 (`test_search_no_match`)**
- **The missing notes file is untested.** Every test makes its file with `mktemp`, so the file always exists. Plain `grep` on a missing file prints an error and exits 2, where the spec wants nothing printed and exit 1.

**Item 4 (`test_search_missing_word`)**
- **The old usage line can survive on `bin/notes:7`.** A builder can put the new line in the `search` branch only. `test_usage` checks just the `usage:` prefix, so `notes bogus` still prints the old line and everything passes.
- **Stdout is not checked.** Usage printed to both streams passes.

**Item 5 (README grep)**
- **Any single line containing `notes search` passes.** That includes a wrong description, or one that omits case-insensitivity and the exit codes.
- **A correct README can fail.** `grep -c` counts lines, so a README that describes the command and also quotes the new usage line on another line prints 2.

**Item 6 (gate exits 0)**
- **It passes today with nothing built.** It also passes if the new tests are left out of the `for` list or an existing test is removed. It only means something alongside items 1 to 4.
- **"Nothing about `add` or `list` changes" has thin cover.** The two existing tests cover one `add` then `list`, and `list` on a missing file. A change to multi-note `list` output or to `add`'s argument joining gets through.