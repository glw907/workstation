---
name: approval-packet
description: >
  The hand-over procedure for a session that puts work before Geoff: sending one packet,
  sorting parts into asks and routine rows, researching asks, checking the file, and acting on
  the decision. Use whenever a session hands a PR, a design, or a plan to Geoff for approval
  ("send this for approval", a PR just opened by a pass, a conductor at a decision point), or
  when `pass-core` or the approval-queue reminder hook points here.
---

# Approval packet

A packet is one Markdown file that `approval-queue packet <initiative> <file>` queues in Design &
PR Approvals. Design: `~/Projects/initiatives/approval-packets/specs/2026-10-14-approval-packets-design.md`
("Who decides what", "Parts", "The packet file", "The command"). Geoff rules on trade-offs; the
gates rule on correctness, so a session certifies its work and cites the evidence for every claim.

The audience is Geoff, deciding from the closed states of the packet, often on a phone. The prose
register is `~/.claude/docs/voice/approval-brief.md`; load it before drafting and follow it. This
skill adds the procedure and never restates the register.

## Procedure

1. **Decide when to send.** Send one packet per hand-over, when the work reaches a decision point.
   A conductor's sweep is one hand-over: one packet for the PRs it holds at that point, never one
   per executor PR. A design brought for approval is a design part in a packet. An executor whose
   conductor hands over sends nothing. An `ordinary` pass merges itself and sends nothing, and
   so does a direct change (`pass-core`, "Close" and "Direct changes").
   Anything that needs Geoff's approval goes to the queue, never as a question in chat ("say merge
   it", "OK to land?"). Chat approval counts only when Geoff gave it before being asked ("merge it",
   "go ahead and land this"); a rule that calls his chat word enough means that case, never a
   reason to ask in chat (Geoff, 2026-10-22).
2. **Gather the parts and give each its canonical ref.** PR `<owner>/<repo>#<n>`, design
   `<owner>/<repo>:<path>`, plan step `step:<n>` of "If you approve". Each PR and design appears
   exactly once. The initiative is a record id in `~/Projects/initiatives`, or `none`.
3. **Sort each part into a lane.** A part is an ask only under one of the seven rules
   (`irreversible`, `public-surface`, `cross-repo`, `owner-call`, `low-confidence`, `gate-failed`,
   `contradicts-ruling`), with at most three asks. Everything else is a routine row carrying your
   verdict. Some asks are forced: a PR with a failing check, or a review verdict of `fix` or
   `escalate`, needs a `gate-failed` ask naming it; a PR whose body has `## Before merge` needs an
   ask naming it, with the choices "The session runs it, then merges" `[approve]` and "I'll run it
   myself" `[hold]`. A PR Geoff held before returns as a `contradicts-ruling` ask, never a routine
   row. More than three asks is unfinished staff work: settle what the facts settle. A PR's
   `## Decisions` entries (`pass-core`, "Judgment calls") go in that part's row, one line each,
   so Geoff can reverse one in his decision note; an entry that meets one of the seven rules is
   an ask. Its `## Planning misses` entries go in the same row, each naming the fix that landed.
   A packet whose approval launches a pass carries the plan's `## Pre-flight` items as
   `[you: <label>]` steps in `## If you approve`, in order. Each step gives the exact commands,
   clicks, or values to enter and the check that shows it done, so Geoff runs the sitting from
   the packet with nothing to look up (`pass-core`, "Lifecycle" step 4). The design's
   `## Brief` lists the plan's standing answers in a `### Standing answers` detail section, so
   approving the design approves what the run will decide without him. Merging an approved PR
   is always a `[session]` step, including a PR that changes permission rules, hooks, or
   autoMode: the approve is the authorization, and a `[you]` step never sends Geoff to GitHub to
   merge (Geoff, 2026-10-22).
4. **Research each ask as completed staff work.** Read the files, PRs, review findings, and logs
   the decision turns on, and cite each fact's source (a path, a PR number, a commit). A question
   the facts settle becomes a routine row. An unchecked fact an ask depends on is checked, or the ask is raised as
   `low-confidence`; the register's third rule says why.
5. **Write the title and description, then the layers.** Once the asks are researched, write the
   description that opens the file: a background paragraph, then one or two summary paragraphs
   that let Geoff decide without opening anything below, per the register's fourth rule. The
   title only names the thing. Then draft each closed state's sentence before its detail, per
   the register. The file grammar is in the design's "The packet file" and the register's `packet`
   exemplars; imitate an exemplar, and let step 6 validate the shape.
6. **Check before sending.** Run `approval-queue packet --check <initiative> <file>`. It runs the
   command's parser and refusals without queuing. Fix each defect it names, then rerun until it
   passes. Send with `approval-queue packet <initiative> <file>` as a background Bash command and
   stay open until it exits with the decision as JSON.
7. **Act on the decision.** An approve is Geoff's merge authorization for the parts whose verdict
   is `approve`. Run "If you approve" in order. Merge each approved PR with `gh pr merge <n> -R
   <owner>/<repo> --merge --match-head-commit <head>`, taking `<head>` from the decision, and
   prefix the command `PREMERGE_DONE=<n>` after running that PR's `## Before merge` steps. Skip a
   step whose part is not approved and a step set to `you` or `skip`. Stop at the first failure and
   run nothing after it, including any `[irreversible]` step. Report what you did with each part
   and send what remains as a new packet. A reject carries a note: fix forward from it. Then pull
   the checkout as `pass-core` "Close" says.

## Blueprints and pages

A docs blueprint and a drafted page are never packet parts, because Geoff reads and edits the
document itself, with the fact-check notes under the lines they concern. Each is its own queue
item: `approval-queue blueprint <worktree> <title> <file> --notes <notes.json>` before the draft,
and `approval-queue page <worktree> <title> <file> --pr <owner/repo#n> --notes <notes.json>` after
it.

When a code PR carries its own blueprint and page edits, queue one `approval-queue change
<owner/repo#n> <title> --notes <notes.json>` review for the whole PR. One exception: an edit that adds or removes a
section, or changes the reader's path, gets its blueprint approved first, as a new page does. The
order of the steps, and when each fact check runs, is in the `blueprint` skill.

## Follow-ups

A follow-up never enters the packet. File each "Found, not done" item worth doing through
`log-issue` in its repo's `BACKLOG.md`, tagged `#initiative:<id>` when a record fits, and list it
in the PR body with its backlog number. An item not worth doing stays in the PR body, marked
dropped. Work the pass would otherwise build on wrongly is fixed in the pass. A backlog triage,
when Geoff asks for one, is the separate `approval-queue triage` kind.

## PR body

A PR body still opens with `## Brief`, the record on GitHub; the packet is the hand-over.
