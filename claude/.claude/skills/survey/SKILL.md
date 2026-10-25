---
name: survey
description: Use when building or styling any house tool's UI (a daisyUI theme, CSS variables, a recipe for the cairn admin, a cairn site, a plain app, or a theme-limited app), when asked where Survey's pieces live, or when Geoff corrects your wording. Survey is the house style; this skill says which file to read for the task.
---

# Survey

Survey is the house style for every house tool. The repo is `glw907/survey`; a project pins it by git tag.

## Where each piece is

| For | Read |
| --- | --- |
| Any UI work | `DESIGN.md` first: principles, the token table, the signature details, the icon guidance, one recipe per kind of app, and the motion rules |
| The values themselves | `tokens.json`, the one source. Never edit a built file |
| A daisyUI app | `theme/survey.css`, `theme/components.css`, `theme/fonts.css` |
| An app with no daisyUI | `theme/survey-vars.css` and `theme/fonts.css` |

Run `scripts/build` after editing `tokens.json`, and `scripts/gate` before a commit. A change to a value or a rule is a minor version, and a removed or renamed token is a major. `scripts/release <version>` tags and publishes once the changelog entry and `package.json` version are merged.

## Rules for working in a project

Survey is starting guidance, not a set of fixed rules. Depart from it where the project's needs differ, and say why in the change. The WCAG contrast and accessibility floors hold either way.

- Take a value from a token, never a literal.
- Pick the recipe in `DESIGN.md` that matches the app, and say in the change which one you followed.
- Consider motion in every place and keep it only where it helps. `DESIGN.md` says when.
- A value that fails contrast is tuned within its hue, and the change lists the old and new values.
- Report each gap or hole you find in Survey: a value that fails contrast, a state Survey doesn't style, a case its rules don't cover, or a departure other projects would make too. Add an entry to `FRICTION.md` in `/var/home/glw907/Projects/survey` as a direct commit to `main`, naming the component or rule, what you measured or saw, and the fix you used. Then work around it in the project's CSS until Survey ships the fix.

## Writing

The house writing register lives in `skills/survey/writing/`. Every audience starts from a published external standard, and these files record it.

| Read | For |
| --- | --- |
| `writing-voice.md` | The base rule and the tells that hold for every audience |
| `authoring-charter.md` | Which standard each audience starts from, and who owns an overlay |
| `agent-facing.md` | Prompts, skills, agent definitions, and other text a model reads |
| `approval-brief.md` | The brief that opens a design, plan, or PR for approval |
| `commit-and-pr.md` | Commit messages and pull request bodies |
| `editor.md` | End-user and editor docs for a non-technical reader |
| `technical-doc-go.md` | Developer docs for Go repos (Go comments take the go-conventions skill) |
| `technical-doc-web.md` | Developer docs for web code |

The workstation's `writing-voice` skill picks a file for an audience. Code comments take the go-conventions, ts-conventions, svelte-conventions, or python-conventions skill, which stay workstation skills. Edit the writing files in the Survey repo only. A workstation edit to a vendored copy is overwritten by the next update.

## Corrections

When Geoff corrects your wording in chat (he rewrites a sentence, strikes a phrase, or names a tell), log it before going on. A correction to a commit message or a comment's wording counts. A code correction does not.

Write one file to `/var/home/glw907/Projects/survey-notes/corrections/`, named from `date +%FT%H%M%S` and `hostname -s` as `<YYYY-MM-DD>T<HHMMSS>-<host>.md`. It opens with frontmatter holding `date`, `host`, `repo`, and `audience`, plus the register file's name when one applies. Four sections follow: Before, After, Context, and Reason.

- Before and After quote the wording verbatim.
- Context is the surrounding sentence only. It never holds a secret, a token, mail content, or a third party's personal data.
- Reason quotes Geoff, or says "not stated". Never supply a reason of your own.

Then run these in the same turn, exactly as written, so the allow rules match:

1. `git -C /var/home/glw907/Projects/survey-notes add corrections/<file>`
2. `git -C /var/home/glw907/Projects/survey-notes commit -m "Log a correction" -- corrections/<file>`
3. `git -C /var/home/glw907/Projects/survey-notes pull --rebase`
4. `git -C /var/home/glw907/Projects/survey-notes push`

A failed pull or push leaves the commit local. Go on; the next correction's push carries it.

If `/var/home/glw907/Projects/survey-notes` is missing, run `gh repo clone glw907/survey-notes /var/home/glw907/Projects/survey-notes` first. If the clone or the write fails, say so and skip the log. Never write the file anywhere else.

A Survey file, a PR body, or `CHANGELOG.md` never quotes a correction file, its Context, a private repo's name, a path, or a person. Write any example there fresh, to show the same pattern.

## Releasing a change

Use this sequence for a release and for the monthly review. `<version>` is the new version.

1. In the Survey PR, run `npm version <version> --no-git-tag-version` and add a dated `CHANGELOG.md` entry.
2. Build the workstation PR in its own worktree: `git -C /var/home/glw907/.dotfiles fetch -q origin && git -C /var/home/glw907/.dotfiles worktree add .claude/worktrees/survey-<version> -b survey-<version> origin/main`. Then vendor the skill there:
   1. Push the Survey PR's branch. `fetch_skill` reads GitHub at the manifest's `branch`, so an unpushed fix vendors a stale head.
   2. Make a scratch home: `S=$(mktemp -d); mkdir "$S/home"; ln -s <worktree> "$S/home/.dotfiles"`.
   3. Run `rm -rf <worktree>/claude/.claude/skills/survey`, since `fetch_skill` never removes a file upstream dropped.
   4. Set the `survey` entry's `branch` in `<worktree>/claude/.claude/tooling/vendored-skills.json` to the Survey PR's branch, run `<worktree>/bin/.local/bin/claude-tooling-sync update-skills --home "$S/home" survey`, then set `branch` to `v<version>`. The `commit` field keeps the head the files came from.
   5. Check that `diff -r <survey worktree>/skills/survey <worktree>/claude/.claude/skills/survey` prints nothing.
3. After approval, merge the Survey PR: `gh pr merge <n> -R glw907/survey --merge --match-head-commit <head>`.
4. Release from a fresh clone, never the main checkout: `R=$(mktemp -d); gh repo clone glw907/survey "$R/survey"`, then `npm ci` and `scripts/release <version>` in `$R/survey`. A fresh clone is on `main`, clean, and at `origin/main`, as `scripts/release` requires. Worktree isolation covers only the repo a session launched from and that repo's main checkout, so an isolated session can still release from the clone.
5. Run the workstation PR's `## Before merge` check: `git -C "$R/survey" diff --quiet <vendored commit> v<version> -- skills/survey`. Then merge it with `PREMERGE_DONE=<n> gh pr merge <n> -R glw907/workstation --merge --match-head-commit <head>`.
6. Pull `~/.dotfiles` and run `stow -R claude`. Check that `claude -p "/output-style"`, run from `/tmp`, lists `writing-voice (current)`. Then remove the worktree: `git -C /var/home/glw907/.dotfiles worktree remove .claude/worktrees/survey-<version>`.

To roll back, pin the vendored entry to the previous tag and rerun the fetch in step 2.
