---
name: approval-packet
description: >
  The hand-over procedure for a session that puts work before Geoff: writing the fact file,
  dispatching the writer, checking and sending one packet, and acting on the decision. Use
  whenever a session hands a PR, a design, or a plan to Geoff for approval ("send this for
  approval", a PR just opened by a pass, a conductor at a decision point), or when `pass-core`
  or the approval-queue reminder hook points here.
---

# Approval packet

A packet is a fact file the session writes and a text file a separate writer drafts from it. The
register's old packet rules are replaced by the writer's brief.

1. **Decide whether to send.** Send one packet per hand-over, of one of three kinds. A `design`
   packet brings a design for approval. A `close` packet hands over the PRs a pass or a
   conductor's sweep holds. A `stop` packet reports a pass that paused,
   with the cause in `reason`. A pass with
   no call, no `auth-data` path, and no `## Before merge` section sends no packet in any class:
   land each PR with `approval-queue land <owner/repo#n> <claim>` (Geoff's ruling D1, 2026-11-10).
   Anything else needing his approval goes to the queue, never a chat question. A move of mail between folders is the
   exception: it is decided in chat, never a packet (backlog #58).
2. **Write the fact file.** `facts.json` keys: `kind`, `title`, `reason` (stop only), `prs`
   (`owner/repo#n` in merge order), `design` and `plan` (`{repo, path}`, design only), `held`,
   `calls`, `decidedForYou`, `steps`, `notChecked`, and `reviews`. The initiative is the command's
   argument: a record id in `~/Projects/initiatives`, or `none`. A call is `{question, rule,
   forced, options: [{label, consequence}], recommended, evidence: [{text, source}]}`, with
   `recommended` the number of the option, counting from 1. A
   `decidedForYou` entry is a call with `applied` set to the option taken. A step is `{text, who}`, `who` being `session` or `you`. A `notChecked` or `reviews` entry is
   `{text, source}`.
3. **Count the calls.** A call is one of seven rules: `irreversible`, `public-surface`,
   `cross-repo`, `owner-call`, `low-confidence`, `gate-failed`, `contradicts-ruling`. Allow at most
   three unforced calls; settle with facts whatever the facts settle. Forced calls may exceed the
   cap (backlog #59): a failing check or a `fix` or `escalate` verdict is a `gate-failed` call; a
   `## Before merge` section is a call with the choices "The session runs it, then merges"
   `[approve]` and "I'll run it myself" `[hold]`; a PR Geoff held before is `contradicts-ruling`.
   Mark each `forced: true`.
4. **Cite each fact's source.** Every `source` is a path with a line, a URL, or `owner/repo#n`.
   Check a fact a call depends on, or raise it as `low-confidence`.
5. **Take the snapshot.** `approval-queue snapshot <facts.json>` writes `snapshot/` beside the
   fact file.
6. **Dispatch the writer.** Make a fresh Agent call with `model: "fable"` (Fable 5.2,
   `claude-fable-5-2`) at effort `medium`. Give it the fact file, the initiative record, and the
   snapshot directory. Name the file `~/.claude/skills/survey/writing/approval-brief.md` and its
   section "The packet writer's brief", and tell the writer that section is its whole style brief.
   Tell it to write `text.md` beside the fact file, in the shape in `approval-queue`'s README
   ("The text file"), and to report every fact it could not find. State that it has no pass
   context and must not run commands that change anything. Fill each reported gap in the fact
   file, or accept the omission, then rerun the snapshot and the writer if the facts changed.
7. **Check, then send.** Run `approval-queue packet --check <initiative> <facts.json> <text.md>`.
   It reports pending checks and does not wait. Fix each defect and rerun until it accepts. Then
   run `approval-queue packet <initiative> <facts.json> <text.md>` as a background Bash command;
   it waits for the decision and prints it as JSON. Take an item back with
   `approval-queue withdraw <id>`, never by killing the command.
8. **Read the notes, then act.** Answer each of Geoff's notes in `replies.json`, an array of
   `{note, outcome, text, ref}`, `outcome` being `fixed`, `filed`, or `answered`, and `ref` (a
   commit or a backlog item) required for the first two. Store it with `approval-queue reply <id>
   <replies.json>`.
   - **Approve:** run `approval-queue merge [--skip <owner/repo#n>]... [--premerge-done
     <owner/repo#n>]... <id>`. Merging is a `session` step; the approve is the authorization. If
     it stops with exit 2 and prints a `## Before merge` section, run those steps, then rerun
     with `--premerge-done <owner/repo#n>`. Where Geoff chose to run them himself, do not merge;
     report. Run each `session` step in order, stopping at the first failure.
   - **Reject or send-back:** fix forward from each note and call, then resend with
     `approval-queue packet --replies <replies.json> <initiative> <facts.json> <text.md>`. The
     command refuses a resend that leaves a note unanswered.
9. **Clear the queue before handing over.** Run `approval-queue pending` and answer with `reply`
   each note it lists for your repos (`reply digest <replies.json>` for a digest note).
10. **File follow-ups.** A "Found, not done" item worth doing goes through `standards:log-issue`
    into its repo's `BACKLOG.md`, tagged `#initiative:<id>` when a record fits, and into the PR
    body with its number.
