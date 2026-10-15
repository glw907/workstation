---
name: log-project
description: >
  Create or update an initiative record in `~/Projects/initiatives`. Use when
  the user wants to track a multi-issue effort or initiative, bigger than a
  single backlog item. Trigger on: "log project", "new project", "start an initiative", "add
  to roadmap", "track this effort", "we need a project for", or when the user
  describes a multi-step effort that spans several backlog items. Also trigger
  on "close project", "finish project", "project status", or "update roadmap".
---

# Log Project

Create or update a strategic initiative as a record in the initiatives repo
(`~/Projects/initiatives`, GitHub `glw907/initiatives`). An initiative groups
related work across one or more repos under a shared goal. The record tells the
story of where the work is going; each repo's `BACKLOG.md` tracks the individual
pieces. Never create a `ROADMAP.md`: cairn-cms keeps its own until its own pass,
and every other repo has retired the file.

## Step 1: Place the work

The initiatives README states the placement rule. Read it, then decide:

1. The work belongs to an existing initiative when it serves one of that
   initiative's goals and no non-goal excludes it. Update that record.
2. When no record fits, the work is either ordinary backlog work for its repo
   or the start of a new initiative. A new initiative gets a record with
   `status: proposed`.
3. A fix with no larger purpose needs no initiative. Say so and stop.

## Step 2: Determine the action

| User intent | Action |
|-------------|--------|
| "Log project", "new initiative", describes a multi-step effort | **Create** a record |
| "Update project X", "add progress to X" | **Update** the record |
| "Close project X", "project X is done" | **Close** the record |
| "Project status", "show roadmap" | **Report**: read the records and summarize |

## Step 3: Gather the details (for create)

| Field | Required | How to get it |
|-------|----------|---------------|
| **id** | Yes | Kebab-case slug from the title (for example `mobile-redesign`); it is the directory name and the `#initiative:<id>` tag on backlog items |
| **title** | Yes | Short name for the initiative |
| **summary** | Yes | One or two sentences: what, why, and what success looks like |
| **status** | Yes | `proposed`, `active`, `paused`, `done`, or `withdrawn`; default `proposed` |
| **owner** | Yes | Who answers for it; default `glw907` |
| **created** | Yes | Today's date, `YYYY-MM-DD` |
| **repos** | Yes | GitHub repo names the work touches |

When the user gave enough, confirm in one message before writing:

> Creating initiative **mobile-redesign** (proposed), repos: ops-dashboard.
> "Redesign the dashboard for mobile-first use."
> Related backlog items: #13, #14
> OK?

## Step 4: Write the record

Each record is a directory `<id>/` in the initiatives clone with two files.

`initiative.yaml`:

```yaml
id: mobile-redesign
title: Mobile-first ops dashboard redesign
summary: Redesign the ops dashboard for mobile-first use.
status: proposed
owner: glw907
created: 2026-10-14
repos:
  - ops-dashboard
```

`README.md` carries six sections in this order, after a title line: Summary,
Motivation, Goals, Non-goals, Where the work lives, and Records. Goals and
non-goals are what the placement rule reads, so write them as testable
statements. "Where the work lives" names the repos and their backlogs. "Records"
links the specs, plans, and research under `<id>/specs/`, `<id>/plans/`, and
`<id>/research/`.

## Step 5: Update, close, and tag

On a status change, set `status` in `initiative.yaml` and add a dated status
line to the README, such as `Status: active (2026-10-14), planning approved.`
Closing sets `done` (or `withdrawn`); the record stays, since the repo is the
history. Then check the backlog of each listed repo: tag related open items
`#initiative:<id>`, and when a closed initiative leaves an open tagged item,
decide with the user whether to keep the tag or drop it.

When every backlog item tagged `#initiative:<id>` is checked off, mention that
the initiative may be done and offer to close it. Don't close automatically:
the user may add items, and some work isn't tracked as individual issues.

## Step 6: Check and commit

In the initiatives clone, run `scripts/check` to validate the record, then
regenerate the index with `scripts/index`. Commit the record and the index
together on a branch, and open a PR rather than pushing to main. If backlog items
changed in another repo (new `#initiative:<id>` tags), commit that file there.

## Notes

- Records are lightweight: a paragraph per section and links out. Detailed specs
  and plans live in `<id>/specs/` and `<id>/plans/`, never in the README.
- When creating a record, scan the listed repos' backlogs for items that
  obviously belong and offer to tag them.
