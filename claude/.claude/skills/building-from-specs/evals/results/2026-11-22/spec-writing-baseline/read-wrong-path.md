I read `spec.md` and checked its claims against the repo. Every stated fact holds except one path, and I could not verify the `origin` remote because the sandbox blocked the network call.

## Questions, ranked

1. **Is `tests/run_all.sh` in done item 1 meant to be `tests/run.sh`?** The file does not exist; `tests/` holds only `run.sh`, and items 2 through 4 all name `run.sh`. As written, item 1 can never hold unless the builder creates a fourth file, which the Files section rules out. A builder who reads it literally either stalls or adds a second runner the gate never calls. I would assume a typo, but that is a guess at the done condition itself.

2. **What should `notes search buy rope` do with the extra argument?** The spec defines only one `<word>`. `add` joins all its arguments, so a user will type this. Searching for `buy rope`, searching for `buy` alone, and printing usage with exit 2 are three different visible behaviors, and the tests will lock in whichever one I pick.

3. **Does `github.com/example/notes` exist, and can the session push to it?** The remote is configured as the spec says, but the name looks like a placeholder. If it is not real, the work cannot end in a pull request and the plan needs a different last step.

## Done-list items that could pass on a wrong result

- **Item 1 (`test_search_finds`).**
  - As written it cannot pass at all (question 1). A new `tests/run_all.sh` that only echoes the `ok` line would also satisfy it.
  - With the path fixed, whole-word matching still passes: `rope` is a whole word in both `Buy rope` and `ROPE ladder`. The fixture has no `ropes`, so the "inside a longer word" rule is untested by any item.

- **Item 2 (`test_search_plain_text`).** Only `.` and `.*` are probed. Three wrong implementations pass:
  - An unquoted shell glob match, where `search '*'` or `search 'a?c'` acts as a pattern.
  - `grep -iF "$word"` without `--` or `-e`, where `search -v` is read as an option.
  - `awk -v`, which rewrites backslash sequences in the word.

- **Item 3 (`test_search_no_match`).** Every test makes its file with `mktemp`, so the file always exists. The "missing notes file counts as no match" rule is untested. A plain `grep` on a missing file exits 2 with an error on stderr, and that gets through.

- **Item 4 (`test_search_missing_word`).** It checks the usage line only on the `search` path. A build that prints the new line there but leaves the old one at `bin/notes:7` passes, so `notes bogus` and bare `notes` still show the old usage. `test_usage` checks only the `usage:` prefix, so it does not catch this.

- **Item 5 (README `grep -c`).**
  - The count is of lines containing `notes search`, so any one line passes, including one that describes the command wrongly.
  - It also fails a correct README that mentions the command on two lines.

- **Item 6 (gate exits 0).**
  - The gate runs only names in the `for` list, so it exits 0 if an existing test is dropped from the list or weakened. No item requires the three current `ok` lines to still print.
  - "Nothing about `add` or `list` changes" rests on those three tests alone.
  - With item 1 pointing at another file, nothing requires `test_search_finds` to be in the gate.