I checked the spec's stated facts against the repo and they hold, except that the sandbox blocked `github.com`, so I could not confirm `origin` is reachable. Two questions remain, and five of the six done items can pass on a wrong result.

## Questions

1. **What does a no-match search exit with: 1 or 0?**
   - "What gets built" says no match prints nothing and exits 1, and done item 2 agrees (`search '.*'` exits 1). Done item 3 says `search zzz` gives exit 0.
   - No consistent implementation satisfies both items 2 and 3, so the builder must either deviate from the done list or special-case.
   - The answer also sets the exit code for a missing notes file, which "counts as no match", and anything scripted around `notes search` depends on it.
   - My guess is that item 3 is a typo for exit 1, but I can't confirm that from the document.

2. **What should `search buy rope` (more than one argument) do?**
   - The spec only covers one word. Three readings are plausible: join the arguments as `add` does, search for the first and ignore the rest, or treat it as a usage error with exit 2.
   - Each gives different user-visible behaviour, and the usage-error reading needs its own test.

## Done list: items that can pass on a wrong result

- **Item 1 (`test_search_finds`)**
  - A whole-word match passes, because no fixture note contains `ropes`. The "`rope` finds `ropes`" rule is never exercised.
  - One-sided case folding passes: an implementation that lowercases the note but not the word works for `search rope` and fails for `search ROPE`.
  - Sorted output passes, because the two expected lines are already in alphabetical order. "Oldest first" is only weakly checked.
- **Item 2 (`test_search_plain_text`)**
  - A regex match that escapes only `.` and `*` passes. `search '^fix'`, `search '['` or `search 'a\c'` would still act as patterns or raise errors.
  - A word starting with `-` (for example `search -v`) can be taken as an option by the underlying tool, and nothing tests it.
  - The `a.c` half asserts no exit code.
- **Item 3 (`test_search_no_match`)**
  - As written it asserts exit 0, so it passes on exactly the result the prose calls wrong.
  - Even with the code corrected, it only uses a file that exists. A missing notes file could print a `grep` error and exit 2, colliding with the usage exit code, and still pass. No item tests the missing-file rule.
- **Item 4 (`test_search_missing_word`)**
  - It checks the new usage line only on the `search` path. `notes bogus` and bare `notes` could still print the old line, because `test_usage` checks only the `usage:` prefix and the spec keeps it that way.
- **Item 5 (README grep)**
  - `grep -c` counts lines containing the string, not correctness. One line such as "notes search: TODO", or one that describes the command wrongly (regex, newest first), prints 1.
  - It also fails a correct README that mentions the command on two lines.
- **Item 6 (gate exits 0)**
  - On its own it passes if the new tests are never added to the `for` list. Items 1 to 4 close that hole.
  - It adds no protection beyond the three existing tests for "nothing about `add` or `list` changes". Because it runs the same tests, it inherits every gap above.