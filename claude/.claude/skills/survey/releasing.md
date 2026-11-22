# Releasing Survey

A release starts only when Geoff asks for one, for a change or for the monthly review. Never start one
on your own, and never cut one from a task's pull request. The session Geoff is talking to runs these
steps, because only that session merges. `<version>` is the new version.

1. In the Survey PR, run `npm version <version> --no-git-tag-version` and add a dated `CHANGELOG.md`
   entry.
2. Build the workstation PR in its own worktree: `git -C /var/home/glw907/.dotfiles fetch -q origin && git -C /var/home/glw907/.dotfiles worktree add .claude/worktrees/survey-<version> -b survey-<version> origin/main`.
   Then vendor the skill there:
   1. Push the Survey PR's branch. `fetch_skill` reads GitHub at the manifest's `branch`, so an
      unpushed fix vendors a stale head.
   2. Make a scratch home: `S=$(mktemp -d); mkdir "$S/home"; ln -s <worktree> "$S/home/.dotfiles"`.
   3. Run `rm -rf <worktree>/claude/.claude/skills/survey`, since `fetch_skill` never removes a file
      upstream dropped.
   4. Set the `survey` entry's `branch` in `<worktree>/claude/.claude/tooling/vendored-skills.json`
      to the Survey PR's branch, run `<worktree>/bin/.local/bin/claude-tooling-sync update-skills --home "$S/home" survey`,
      then set `branch` to `v<version>`. The `commit` field keeps the head the files came from.
   5. Check that `diff -r <survey worktree>/skills/survey <worktree>/claude/.claude/skills/survey`
      prints nothing.
3. After Geoff approves the Survey PR by number, merge it:
   `gh pr merge <number> --repo glw907/survey --merge`.
4. Release from a fresh clone, never the main checkout: `R=$(mktemp -d); gh repo clone glw907/survey "$R/survey"`,
   then `npm ci` and `scripts/release <version>` in `$R/survey`. A fresh clone is on `main`, clean,
   and at `origin/main`, as `scripts/release` requires. Worktree isolation covers only the repo a
   session launched from and that repo's main checkout, so an isolated session can still release
   from the clone.
5. Run the workstation PR's `## Before merge` check:
   `git -C "$R/survey" diff --quiet <vendored commit> v<version> -- skills/survey`. Then, after Geoff
   approves the workstation PR by number, merge it:
   `gh pr merge <number> --repo glw907/workstation --merge`.
6. Pull `~/.dotfiles` and run `stow -R claude`. Check that `claude -p "/output-style"`, run from
   `/tmp`, lists `writing-voice (current)`. Then remove the worktree:
   `git -C /var/home/glw907/.dotfiles worktree remove .claude/worktrees/survey-<version>`.

To roll back, pin the vendored entry to the previous tag and rerun the fetch in step 2.
