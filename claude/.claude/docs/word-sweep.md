# Running a word sweep

A word sweep removes one word or phrase from a repo's live prose and comments, such as the empty
"own" that cairn-cms PR #137 took out. This page gives the method and the two checks to run
before any gate. The slice prompt from PR #137 is the template for the agents' brief.

## Method

Split the repo into slices that do not overlap, and give each slice to one agent in its own
worktree. Run at most two agents at once. Each agent finds its hits with `git grep` and judges
every one in its sentence. Delete the word when the sentence means the same without it. Keep it
in three cases: when it sets one party against another and the reader would lose the contrast, in
an idiom such as "on its own", and in identifiers. If you have to argue that the contrast is there,
remove the word.

In code files, change comment text only. Where the sweep changes nothing the program emits, prove
that with a compile-equivalence check: the build output before and after must match. Skip the
check only where runtime text changes on purpose, and then update every test and doc quote that
asserts the old text. Merge the slices into one branch and close with a whole-branch review.

## Before any gate

Two failures can slip past the gate and the reviewer: a slice can empty a file, and a deletion can
leave a possessive with nothing after it. Because a word sweep keeps each line's count, a line-count
check catches the first. Run both commands on the merged branch before the gate.

To list every file whose added and removed line counts differ, run this against the branch's base:

```
git diff --numstat <base>...HEAD | awk '$1 != $2'
```

Any row is a file that gained or lost lines. A word sweep should print nothing, or only the files
you reworded on purpose. An emptied file shows at once as a row with zero added lines.

To list every dangling possessive in the changed files, run:

```
tellgrader <files> | jq '[.. | objects | select(has("warnings")) | .path as $p | .warnings[] | select(.check == "dangling-possessive") | {path: $p, line, excerpt}]'
```

`tellgrader` prints one object for one file and an array for several, and the filter reads both.
It returns an array of `{path, line, excerpt}` rows, empty when the branch is clean. Repair each
row by hand; the reading that fits the sentence decides the fix.

## Why both

The sources slice of the second "own" sweep emptied `scripts/checks/gate-tier.mjs` (cairn-cms #55).
The line-count check shows that at once. The same sweep left 14 dangling possessives, repaired after
the merge in cairn-cms `3960d4913`. The possessive scan finds each one.
