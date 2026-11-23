I read the spec, checked its claims against the repo, and ran a few wrong implementations against the spec's four-note fixture. One question is left, and all six done items can pass on a wrong result.

## Question

1. **What does `notes search buy rope` do when the word arrives as more than one argument?** The spec only covers a missing or empty word. `add` joins its arguments, so the owner will likely type this. The three readings are: join into the phrase `buy rope`, exit 2 with usage, or search `buy` and ignore the rest. Each gives a different argument check and a different test, and the last one silently returns wrong matches.

## Done list

The worst gaps are the untested promises in items 1 and 3 and the loose usage check in item 4.

1. **`test_search_finds`** passes on three wrong results:
   - **Whole-word matching:** `grep -iwF` prints `Buy rope` then `ROPE ladder`, yet misses `ropes`. No fixture note has the word inside a longer word, so the `rope` finds `ropes` rule is never tested.
   - **One-way case folding:** an implementation that lowercases the notes but not the word passes, yet `search ROPE` finds nothing. The test only searches a lowercase word.
   - **Wrong order:** sorted output passes, because `Buy rope` sorts before `ROPE ladder` anyway.
   
   Also, the item says "prints … then …", not "only", so a containment check would pass with extra lines.

2. **`test_search_plain_text`** only tests `.` and `.*`. Three wrong results get through:
   - **Leading dash:** `grep -iF "$word"` without `--` passes, but `search -x` is taken as a grep option.
   - **Backslash:** `awk -v w=…` passes, but a word with a backslash is mangled (`a\b` does not find the note `a\b`).
   - **Glob match:** an unquoted glob match fails only because `fix a.c` happens to contain a dot; `search '*'` would print every note.

3. **`test_search_no_match`** never tests "a missing notes file counts as no match". Every test creates its file with `mktemp` and fills it. A plain `grep` on a missing file prints an error and exits 2, which looks like a usage error, and passes. Stderr is also not asserted, so a "no matches" message passes.

4. **`test_search_missing_word`** can pass on unchanged code. `bin/notes search` already exits 2 with a usage line today. If the test follows the existing `test_usage` (first word is `usage:`), the old line passes. It needs a full-line comparison. Two more gaps:
   - A separate usage string in the search branch passes while `notes bogus` and bare `notes` still print the old line.
   - Stdout is not asserted empty.

5. **`grep -c "notes search" README.md` prints 1** counts lines and checks nothing about content. A line saying "notes search is not supported", or one describing regex matching, passes. It also fails a correct README: mentions on two lines print 2, and a hard wrap between `bin/notes` and `search` prints 0. The README wraps its prose.

6. **`bash scripts/gate.sh` exits 0** is true today with nothing built. It also passes if an existing test is dropped from the `for` list or weakened. That is the only guard on "nothing about `add` or `list` changes".

## One false claim in the spec

The spec says `git grep -n usage -- bin tests` found 1 hit. It finds 4: `bin/notes:7` and `tests/run.sh:12`, `:13`, `:15`. The three extra hits are `test_usage`, which only checks the `usage:` prefix, so nothing else needs to change. The spec's other claims checked out.