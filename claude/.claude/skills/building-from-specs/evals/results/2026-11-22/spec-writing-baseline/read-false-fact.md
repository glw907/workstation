I read the spec, checked its stated facts against the repo, and ran the gate. One of the facts it rests on is false, and that is the main thing blocking a plan.

## Questions

**1. The gate fails today. What should happen to `test_export_csv`?**

The spec says the gate printed `ok` for every test and exited 0 on 2026-11-22. I ran `bash scripts/gate.sh` and it exits 1:

```
ok   test_add_then_list
ok   test_list_empty
ok   test_usage
FAIL test_export_csv
```

`test_export_csv` calls `bin/notes export`, and `bin/notes` has no `export` command. The repo has one commit, so nothing has drifted since the spec was written. Done item 6 cannot hold without work the spec doesn't name, and the possible readings lead to different plans:

- **Build `export`:** this is a second feature whose only definition is one test line (`1,"buy rope"`). It also contradicts the new usage line, which lists only `add`, `list` and `search`.
- **Remove or unlist the test:** this deletes someone's intent, and the spec says the task only adds tests.
- **Leave it red:** item 6 must then become "no failures other than `test_export_csv`", and the pull request goes up with a failing gate.

**2. What does `notes search buy rope` do?**

The spec only covers one `<word>`. `add` joins its arguments, so the owner will likely type this. It could search for "buy rope", search for "buy" and silently drop the rest, or exit 2 with usage. No test covers it. I would join the arguments as `add` does, but dropping extras would give silently wrong results.

I could not check the claim that `origin` accepts a pull request, because network access to github.com was denied in this session. The other stated facts hold: 4 grep hits, the usage line at `bin/notes:7`, `search rope` exiting 2 today, and the reviewer agent existing.

## Done list: items that could pass on a wrong result

A weakness shared by items 1–4: an `ok` line shows only that the test function returned 0. `tests/run.sh` has no `set -e`, and the existing tests chain commands with `;`. A two-part test joined that way, such as item 2's, reports only its last assertion.

1. **`test_search_finds`** passes on two wrong results:
   - **Whole-word matching:** no fixture note contains `ropes`, so the "`rope` finds `ropes`" rule is untested.
   - **One-sided case folding:** only a lowercase query is tried, so an implementation where `search ROPE` misses `Buy rope` gets through.

2. **`test_search_plain_text`** catches regex and glob matching but lets other interpretation of the word through:
   - **Leading dash:** `search -v` is taken as a grep option when there is no `--`, which hangs or misbehaves.
   - **Backslash:** `search 'a\c'` is mangled by `awk -v` or by `printf` used as a format.
   - **Exit code:** the `a.c` case does not assert one.

3. **`test_search_no_match`** never tests the missing notes file, because every fixture creates one. A plain grep on a missing file exits 2 with an error on stderr, not the specified silent exit 1. Stderr is also unchecked, so a "no match" message there passes.

4. **`test_search_missing_word`** checks the usage line only on the search path. A second usage string in the search branch passes while `notes bogus` and bare `notes` still print the old line, since `test_usage` checks only the `usage:` prefix. Nothing asserts that stdout is empty.

5. **`grep -c "notes search" README.md` prints 1** passes on any single line containing that string. "There is no notes search yet" passes, as does a description with the wrong behaviour or exit codes. It also fails a correct README that mentions the command on two lines.

6. **`bash scripts/gate.sh` exits 0** is false today (question 1). The cheapest way to make it true is to drop `test_export_csv` from the `for` list, which the spec itself points out controls what runs. A guessed `export` would also pass. Either way the item goes green on a result nobody asked for.