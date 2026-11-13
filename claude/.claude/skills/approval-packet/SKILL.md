---
name: approval-packet
description: >
  The hand-over procedure for a session that puts work before Geoff: writing one document for
  the Approval Queue, checking it, sending it, and acting on his answer. Use whenever a session
  hands a PR, a design, or a plan to Geoff for approval ("send this for approval", a PR just
  opened by a pass, a conductor at a decision point), or when `pass-core` or the approval-queue
  reminder hook points here.
---

# Approval packet

A packet is one Markdown document that the session which did the work writes for Geoff. The queue
shows it as a page with buttons, and `approval-queue send` returns his answer. The opening puts
the decision first, so the house departure of 2026-10-21 (background before the summary) is
withdrawn.

1. **Decide whether to send.** A pass with no call for Geoff, no `auth-data` path, and no
   `## Before merge` section sends nothing: land each pull request with
   `approval-queue land <owner/repo#n> <sentence>`, one plain sentence on what it does (Geoff,
   2026-11-10). Anything that needs his decision is a document, and nothing that belongs in the
   queue is asked in chat. A paused pass asks its question as a `decide` document; under a
   conductor, the conductor sends it. A conductor's round report is a document of kind `report`.
   A move of mail between folders is the one exception: it is decided in chat (backlog #58).
2. **Write the document.** Name it `<name>.queue.md` and write it in the session's job tmp folder,
   outside any repo, so the workstation's Vale config reaches it. The title names what changed or what
   is asked, and never counts. The first paragraph is the whole page made small. Ask each question
   where the reader meets it, with its options and a recommendation. Put the detail after, under
   headings a reader can navigate by. Give reasons in the text. Use no id you made up, and name a
   pull request by what it does.
3. **Imitate the models.** `references/model-close-packet.md` and `references/model-report.md` are
   two documents Geoff accepted. Copy their shape, their order, and their plainness, never their
   facts. Each carries one `tellgrader` `empty-own` warning, kept because the words are his; a new
   document fixes the warning. The queue reads this much beyond plain Markdown:
   - A header between `---` lines. `kind` is `merge` (pull requests to merge), `design` (a design
     to approve), `decide` (questions only), or `report` (nothing to decide).
   - `prs`, required for `merge`: a list in merge order, each item `owner/repo#n | a few plain
     words`.
   - `approve` and `sendback`, required for every kind but `report`: one sentence each on what
     the session does next. The page prints them on the two buttons, as inline Markdown.
   - The title line, `# ` and the title, right after the header, then a paragraph.
   - `:::question <label>` after the paragraph that asks the question, then two to six options as
     `- ` lines, then a `:::` line. The label is a few plain words, unique in the
     document. An option's bold text is its name, and one option at most ends `{recommended}`.
   - `:::decide`, at most once, where the approve and send-back buttons go. Left out, they go at
     the end.

   A document holds 30 questions at most and stays under 200 KB. The forms the queue can't show
   are listed in `written-for-people.md`.
4. **Check the writing.** Follow `~/.claude/docs/voice/written-for-people.md`, all four steps.
5. **Check, then send.** Run `approval-queue check <doc>` and fix each fault it prints until it
   prints `no faults`. A check still running on a pull request is a line, never a fault, and
   `send` refuses until it finishes. Then run `approval-queue send <doc>` as a background Bash
   command. It stores the document, waits for the answer, and prints it on stdout; a `report`
   prints its id and exits at once. Take a document back with `approval-queue withdraw <id>`,
   never by killing the command. If the command is gone, as after a reboot,
   `approval-queue collect <id>` recovers the answer.
6. **Act on the answer.**
   - On approve, run `approval-queue merge <id>`. It merges each pull request at the head Geoff
     read, in the document's order; the approve is the authorization. Then pull the checkout as
     `pass-core` "Close" describes. On a `decide` or `design` document, take the answers and carry
     on with the work.
   - On send-back, read the notes with `approval-queue notes <id>`, which prints each thread with
     its id. Answer each note in its thread with `approval-queue reply <id> <thread> <text.md>`;
     a file without a thread opens a new one and must start with a blockquote of the passage.
     Fix forward, then return the revision with `approval-queue send --returns <id> <doc>`, which
     keeps the kind. Write no change marks: the queue shows what changed between versions.
7. **File follow-ups.** A "Found, not done" item worth doing goes through `standards:log-issue`
   into its repo's `BACKLOG.md`, tagged `#initiative:<id>` when a record fits, and into the PR
   body with its number (Geoff, 2026-10-11). An initiative-sized one becomes a record
   (`log-project`).

The command's forms are `check|send <doc.md>`, `send --returns <id> <doc.md>`,
`collect|withdraw|merge <id>`, `notes <id>`, `reply <id> [thread] <text.md>`,
`land <owner/repo#n> <sentence>`, and `restart`.
