# Writing for a person

Every document a session writes for a person is GitHub Flavored Markdown, as the
[specification](https://github.github.com/gfm/) defines it (Geoff, 2026-11-12). Use its forms:
headings, lists, task lists, tables, code fences, quotations, links, and struck text. Four rules
of use:

- A table holds values a reader compares across rows. Prose with three points stays prose.
- A command, a path, or a name a reader would type goes in code marks. A block of commands goes
  in a fence that names its language.
- Reference material a reader doesn't need to decide goes in a folded section, `<details>` with
  its heading in `<summary>`.
- Don't use footnotes, alerts, math, or diagrams. They are GitHub website features outside the
  specification, and the queue shows them as plain text.

A repo whose rules name a different format keeps it.

## The four steps

1. **Write from the standards and the models.** For Geoff, the standards are the Federal Plain
   Language Guidelines, Nielsen Norman Group on web writing, and Google's rules for headings.
   The models in `~/.claude/skills/approval-packet/references/` apply them. His corrections of
   2026-11-12 hold for every page:
   - Use no id you made up. Name the work in ordinary words, and a pull request by what it does.
   - Ask the plain question, never an indirect one.
   - A title names what changed or what is asked, and never counts things.
   - The opening is the whole page made small. A line of status isn't a summary.

   For a reader of a public repo, use the standard the `writing-voice` router names for the file.
2. **Run Vale.** Name a queue document `<name>.queue.md` and write it in the session's job `tmp`
   folder, outside any repo. Run `vale` on it and fix every error. A summary ending
   `in 0 files.` means a wrong name or folder.
3. **Run `tellgrader --register docs`** on the file. Fix what it reports and rerun until it
   prints `"findings": []` and `"warnings": []`.
4. **Give the page alone to a reader with no context.** Dispatch one blocking Agent call,
   `sonnet` at `medium`, with the page's text only. The reader states what the page asks, what
   each answer causes, and each term it couldn't explain. Fix what it missed, and rerun it if a
   question changed. Two rounds is the cap; after that, send and say so in the last section.

If `vale` or `tellgrader` isn't installed, stop and report it. Never skip the step.

## What each kind of writing gets

| Writing | Steps |
| --- | --- |
| A queue document, a round report, a string on a queue page | All four |
| A pull request's opening, STATUS, a hand-over's last message | 1 to 3, and 4 when it asks Geoff for something |
| A reply or a question in chat | 1 |
| Writing a repo already has rules for: cairn's docs, a site's pages and posts | Those rules, unchanged |
| Any other README, doc page, pull request, issue, or release note in a public repo | 1 to 3 under the router's standard, and 4 for a page a visitor lands on first |
| A plan, a launch prompt, a note between sessions, or another file only a session reads | None, in a public repo too |

A file only a session reads is written however is quickest and clearest for that session. Skills
and `CLAUDE.md` stay in the agent-facing register.

## Public repos

Read the public repos from `gh repo list glw907 --visibility public` each time, never from memory.
