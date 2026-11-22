I read `spec.md` against the repo. The spec's stated facts hold: the gate prints `ok` three times and exits 0, `bin/notes search rope` prints the usage line and exits 2, and the `git grep` finds the 4 hits it names. Two questions are left, and five of the six done items can pass on a wrong result.

## Questions

1. **Is the pull request part of this task, and can the builder push to `origin`?** The status line says "one pull request", but no done item mentions one. `origin` is `https://github.com/example/notes.git`, which looks like a placeholder. I could not check it, because this session's sandbox denies `github.com`. The answer decides whether the plan ends at a green gate on a local branch or includes push, PR and review steps, and what the builder does if the push fails.

2. **What does `notes search buy rope` do?** The spec only covers a single `<word>`. `add` joins all its arguments, so someone used to it will type two words unquoted. The options are to join them into one phrase, print usage and exit 2, or silently ignore the extras. The last returns notes that don't match what was typed, and each option needs a different test.

## Done list

The list exists. I treated each item's stated assertions as part of the item.

- **Item 5 passes today with nothing built.** `grep -c notes README.md` prints 3 on the current README, so a README that never mentions `search` gets through. Unlike items 1 to 4, this one carries no "today it prints" line. `grep -c 'notes search' README.md` prints 0 today.

- **Item 1 passes on three wrong results.**
  - **Whole-word match:** the fixture has no note where the word sits inside a longer word, so `grep -iwF` passes. It then fails the spec's own example, `rope` finds `ropes`.
  - **One-sided case folding:** the test only searches with a lowercase word. A build that lowercases the note but not the word passes, and `search ROPE` then finds nothing.
  - **Sorted output:** `Buy rope` sorts before `ROPE ladder`, so alphabetical order looks the same as oldest first. The item also says "prints", not "prints only" as item 2 does, so a containment check would satisfy it.

- **Item 3 passes with the missing-file case wrong.** No item covers "a missing notes file counts as no match". The obvious build, `grep` on the file under `set -e`, exits 2 with a `grep: No such file` error where the spec wants silence and exit 1. That is also the same exit code as a usage error.

- **Item 4 passes with the old usage line still at `bin/notes:7`.** It checks the usage line only on the `search` and `search ''` paths. A builder who adds a second usage `echo` in the search branch leaves `notes bogus` and bare `notes` printing the old line. `test_usage` checks only the `usage:` prefix, so nothing catches it.

- **Item 6 passes today and proves nothing about search on its own.** It is a regression guard, which is fine, but "nothing about `add` or `list` changes" rests on two thin tests. For example, a `list` that breaks on a file with several notes would exit 0.

Item 2 is tight. `search a.c` printing only `fix a.c` rules out a regex match, and `search '.*'` printing nothing rules out both regex and glob matching.