# Chain details

The parts of a chain that `SKILL.md` "Chains" points to: a child's opening lines, a parent sent back or
rejected, and a restart. The tick's steps stay in `SKILL.md`.

## A child's start

The child launches from the main checkout with `worktree.baseRef` set to `fresh`, and its goal opens with these
lines. It merges, since a reset was refused as `[Irreversible Local Destruction]` and a rebase rewrites history.

```text
It builds on pull request #<parent> (branch <parent-branch>, head <parent-sha>). Before any edit, run
`git fetch origin <parent-branch>` and `git merge --no-edit origin/<parent-branch>`. On a conflict, run
`git merge --abort` and end, listing the conflicting files. Stop unless `git merge-base --is-ancestor
<parent-sha> HEAD` exits 0. Open the draft pull request with `gh pr create --draft --base <parent-branch>`,
and make the body's first line `Built on #<parent> at <parent-sha>.` The review reads `<parent-sha>..HEAD`.
```

## A parent sent back or rejected

When Geoff sends a parent back, a fresh session launches on its branch with his words. The tick launches no new
child of it until it is ready again, and a child already built on it goes stale, which the current check in
"Merging" catches. A parent he rejects never merges. His session closes each child's pull request after the
child's session has ended, with `gh pr close <n> --repo <r> --comment "Built on #<parent>, which Geoff
rejected."`, and deletes their branches only with his go-ahead. A child relaunches from the replacement.

## A restart, a dead session, or a pause

A restart stops the tick's session and every task session. At the next sitting, `claude --resume` on the chain's
session restores the loop, or a new session runs the same launch prompt, since each tick rebuilds the chain from
GitHub and `claude agents`. Relaunching a `stopped` task is Geoff's call. Auto mode pauses after 3 blocks in a
row or 20 in all, which halts the chain. A fixed loop expires after 7 days, and a goal holds 4,000 characters,
500 of them the child's.
