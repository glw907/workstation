I read `spec.md` against the repo. One question blocks planning, one is minor, and every item in the done list can pass on a wrong result.

## Questions, ranked

**1. Where does the `contains` helper go, given that `lib/strings.sh` must never be edited here?**

The spec's Files section says the task changes `lib/strings.sh`, "which gains a `contains` helper". The repo says the opposite in two places:

- `lib/strings.sh:1`: "copied from the shkit project at v2.3.0. Never edit this copy."
- `README.md:10-11`: "never edited here: a change goes to shkit first and is copied back."

The spec doesn't mention this rule, so I can't tell whether the author knew about it. The answer changes the plan three ways:

- **Keep the helper out of the vendored file** (in `bin/notes` or a new unvendored file): the file list shrinks to three and the task stays one pull request at 30 minutes. This is what I'd do, and "the implementation is the builder's choice" may already allow it, but the Files section reads as a requirement.
- **Go through shkit first:** that is a second repo, a release, and a copy-back that changes the `v2.3.0` header. I have no shkit location or access, and "one task, one pull request" stops being true.
- **Override the rule deliberately:** the README paragraph and the header comment become false and need rewriting, and the next copy from shkit silently drops `contains`.

`bin/notes` does not source `lib/strings.sh` today, so using the helper there also adds new wiring.

**2. What does `search` do with more than one argument, such as `notes search buy rope`?**

`add` joins all its arguments with spaces. The spec says only `<word>`. Joining, ignoring the extras, or exiting 2 are all defensible and each is visible to the owner. I'd default to joining, to mirror `add`, unless told otherwise.

## Done list: items that pass on a wrong result

**Items 1, 2, and 4: the harness only sees the last assertion.** `tests/run.sh` prints `ok` when the test function returns 0, and a bash function returns the status of its last command. Each of these tests has several assertions. Unless they are chained with `&&`, as the existing tests are, a failed early assertion still prints `ok`. Printing `ok   test_name` also proves only that a function with that name returned 0.

**Item 1 (`test_search_finds`)** passes on:
- **Whole-word matching** (`grep -iw`). No fixture note has `rope` inside a longer word, so the `rope` finds `ropes` rule is never exercised.
- **One-sided case folding.** The query is always lowercase, so a version where `search ROPE` finds nothing gets through.
- **Sorted output instead of file order.** `Buy rope` and `ROPE ladder` are already in alphabetical order.

**Item 2 (`test_search_plain_text`)** catches regex and glob matching, but passes on:
- **A word starting with `-`** being read as an option (`search -v` with `grep -iF "$word"` and no `--`).
- **A word containing a backslash** being mangled (for example by `awk -v`).

**Item 3 (`test_search_no_match`)** passes when a missing notes file is handled wrongly. With a plain `grep`, a missing file gives an error on stderr and exit 2, the usage code, not the "no match" the spec requires. No item tests this, and the rule that every new test adds the four notes rules such a test out as written.

**Item 4 (`test_search_missing_word`)** passes on:
- **The new usage line living only in the search branch**, with `bin/notes:7` unchanged. `notes bogus` then still prints the old line, and `test_usage` checks only the `usage:` prefix.
- **Usage printed to stdout as well as stderr.**

**Item 5 (README grep)** counts lines containing "notes search", so any sentence passes, including a wrong one. It also fails a correct README that mentions the command on two lines. It does not notice the README's "never edited here" paragraph becoming false if `lib/strings.sh` is edited.

**Item 6 (gate exits 0)** adds nothing beyond items 1 to 4 plus the three existing tests. It passes with the vendored file edited. "Nothing about `add` or `list` changes" rests on two tests that cover one note and an absent file.