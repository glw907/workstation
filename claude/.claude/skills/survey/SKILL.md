---
name: survey
description: Routes house-tool UI work to the right Survey file, for a daisyUI theme, CSS variables, a recipe for the cairn admin, a cairn site, a plain app, or a theme-limited app. Survey is the house style, and this skill says where each of its pieces lives. It also holds the steps for logging a correction to Claude's wording. Use when building or styling any house tool's UI, when asked where Survey's pieces live, or when the user corrects or rewrites your wording in a commit, a doc, or a reply, before you redo the work.
---

<!-- local-overlay -->
On this workstation, writing for Geoff follows ~/.claude/docs/voice/written-for-people.md.
<!-- /local-overlay -->

# Survey

Survey is the house style for every house tool. The repo is `glw907/survey`; a project pins it by git tag.

## Where each piece is

| For | Read |
| --- | --- |
| Any UI work | `DESIGN.md` first: principles, the token table, the signature details, the icon guidance, one recipe per kind of app, and the motion rules |
| The values themselves | `tokens.json`, the one source. Never edit a built file |
| A daisyUI app | `theme/survey.css`, `theme/components.css`, `theme/fonts.css` |
| An app with no daisyUI | `theme/survey-vars.css` and `theme/fonts.css` |

Run `scripts/build` after editing `tokens.json`, and `scripts/gate` before a commit. A change to a value or a rule is a minor version, and a removed or renamed token is a major. A release is cut only when Geoff asks for one, and `releasing.md` holds its steps.

## Rules for working in a project

Survey is starting guidance, not a set of fixed rules. Depart from it where the project's needs differ, and say why in the change. The WCAG contrast and accessibility floors hold either way.

- Take a value from a token, never a literal.
- Pick the recipe in `DESIGN.md` that matches the app, and say in the change which one you followed.
- Consider motion in every place and keep it only where it helps. `DESIGN.md` says when.
- A value that fails contrast is tuned within its hue, and the change lists the old and new values.
- Report each gap or hole you find in Survey: a value that fails contrast, a state Survey doesn't style, a case its rules don't cover, or a departure other projects would make too. File it in `BACKLOG.md` in `/var/home/glw907/Projects/survey` through `/log-issue`, as a direct commit to `main`, naming the component or rule, what you measured or saw, and the fix you used. Then work around it in the project's CSS, naming the item, until Survey ships the fix.

## Writing

The house writing register lives in `skills/survey/writing/`. Every audience starts from a published external standard, and these files record it.

| Read | For |
| --- | --- |
| `writing-voice.md` | The base rule and the tells that hold for every audience |
| `authoring-charter.md` | Which standard each audience starts from, and who owns an overlay |
| `agent-facing.md` | Prompts, skills, agent definitions, and other text a model reads |
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
