---
name: backlog-sweep
description: >
  Ground a repo's open backlog items in the current code and give each a verdict (fold, keep,
  done, duplicate, reword, drop), so the backlog stays maintained with thought. Use at every pass
  design (pass-core "Lifecycle" step 1 runs the scoped sweep), and in any repo when Geoff asks to
  "sweep the backlog", "groom the backlog", "clean up the backlog", or "what in the backlog still
  matters". Not for filing a new item (that is log-issue).
---

# Backlog sweep

An item earns nothing by having been filed. Agents file most items as side findings, so a
backlog collects items of uneven value, and a past agent's item may not be worth doing. Each
sweep asks whether an item still deserves doing at all, and drop is as ordinary a verdict as fold
(Geoff, 2026-10-27). The research behind this skill is
`~/.dotfiles/docs/research/2026-10-27-backlog-sweep-research.md`.

## The two sweeps

- **Scoped, at every pass design.** The items tagged with the pass's initiative, and the items
  that name a file the pass will change. Only these can fold. The design lists the verdicts, and
  approving the design approves the backlog edits, which the planning session lands that day.
- **Full, on request or when due.** Every open item, oldest unswept first, at most 40 per run.
  A full sweep is due when a repo's backlog holds more than 15 open items with no `swept` stamp
  from the last 90 days; the pass design's sweep checks this and runs the full sweep beside the
  scoped one. A full sweep folds nothing. It goes to Geoff as an `approval-queue triage` packet
  (`approval-packet`), one row per item, `proposed` set to `defer` for keep and reword
  and `drop` for drop, done, and duplicate.

Inactivity is never a reason to drop: Next.js's issue sweep found "inactivity turned out to be a
poor stand-in for relevance" (<https://nextjs.org/blog/how-we-closed-1500-github-issues>).

## The dispatch

One read-only subagent per repo (`claude-opus-5-5` at `medium`; tools Read, Grep, Glob, and Bash
for `git log` and `git show`). Best practices for Claude Code
(<https://code.claude.com/docs/en/best-practices>): "A fresh reviewer does help". The prompt
carries the backlog path (`backlog_path` in `.claude/project-tracking.json`, else `BACKLOG.md`),
the commit it reads, the sweep's scope, and for a scoped sweep the design's path and the files the
pass changes. It reads only list items under the open sections, never a roadmap or plan section.

For each item it returns the mechanism as it stands at file:line, one verdict, a one-sentence
reason, and for a fold the fix shape and a size in minutes.

| Verdict | Means | Needs |
| --- | --- | --- |
| `fold` | The pass does it | It lives in lines the pass already rewrites, at the pass's risk class |
| `keep` | Real and worth doing, not now | The mechanism still holds |
| `reword` | Partly fixed or misdescribed | The item cut to what is left |
| `done` | Already fixed | The commit or file:line that fixed it |
| `duplicate` | Another item covers it | The item it merges into |
| `drop` | Not worth doing, or no longer true | The strongest case for keeping it, stated and answered |

The fold bar has no "small and cheap" branch. Several small folds break an estimate, and a fold
from outside the pass's files brings scope the design never priced. Nothing folds into an
`auth-data` pass unless it is already in the pass's files.

## Landing the verdicts

The session that ran the sweep edits the backlog in one commit:

- `keep` gains ` *(swept YYYY-MM-DD)*` on its line, replacing an older stamp, so later sweeps go
  to unswept items first.
- `reword` replaces the item's text and gains the stamp.
- `done`, `duplicate`, and `drop` move to `## Done` as `done: <proof>`, `duplicate of <item>`, or
  `dropped: <reason>`, never deleted, so Geoff can reopen one by moving it back.
- `fold` stays open until the pass closes it.

Inside a pass the commit rides the pass branch. Outside one it is a `pass-core` "Direct change"
once Geoff has approved the triage.
