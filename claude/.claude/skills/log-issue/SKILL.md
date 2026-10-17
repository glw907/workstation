---
name: log-issue
description: >
  Quick-log a bug, feature, or improvement to the project backlog.
  Use when the user says "log issue", "track this", "add to backlog",
  "note this for later", "we should fix", "future work", "TODO",
  or describes a problem/idea they want to capture without acting on it now.
  Also trigger when the user notices a bug or limitation during other work
  and wants to record it rather than fix it immediately.
---

# Log Issue

Quickly capture a bug, feature request, or improvement idea to the project's
backlog file (`backlog_path` in the config, `BACKLOG.md` by default). Infer what you can from context; prompt for anything missing.
The goal is to get the idea written down in under 10 seconds of user effort.

---

## Step 1: Find or create project config

Look for `.claude/project-tracking.json` in the project root.

### Config exists and backlog file exists

Read the config, read the backlog file, proceed to Step 2.

```json
{
  "backlog_path": "BACKLOG.md",
  "domains": ["ops-dashboard", "website", "handbook"],
  "default_priority": "medium"
}
```

Initiatives live in the initiatives repo, managed by `/log-project`; this config does not point at them.

### Config sets `"backlog": false`

The repo keeps no backlog. Create no file, say so in one line, and stop. Offer to put the idea in
the plan or an initiative record instead.

### Config exists but backlog file is missing

Do not create it unasked. Ask: "The configured backlog `<backlog_path>` does not exist. Create it?"
On yes, create it using the template in Step 4 and proceed to Step 2; on no, stop.

### No questions: a session filing a pass follow-up

A session filing a "Found, not done" follow-up (`approval-packet`, "Follow-ups") asks nothing, in a
repo with no backlog too (Geoff, 2026-10-14). It writes `.claude/project-tracking.json` with the
defaults (`BACKLOG.md`, the repo's name as its one domain, `medium`), creates `BACKLOG.md` from the
Step 4 template where it is missing, and files the item.

### Config missing or backlog file isn't in the expected format

This is first-run setup for an interactive request. Ask the user these questions in a single message:

1. **Backlog location:** "Where should the backlog file live? (default: `BACKLOG.md`
   at project root)"
2. **Domains:** "What are the main work areas for this project? These become tags
   for categorizing issues. Examples: `frontend`, `backend`, `api`, `infra`, `docs`"
3. **Default priority:** "What default priority for new issues? (default: `medium`)"

After the user answers:

1. Create `.claude/project-tracking.json` with their answers (create `.claude/` if needed)
2. Create the backlog file at the specified path using the template in Step 4
3. Confirm: "Created backlog config and `BACKLOG.md`. Ready to log issues."
4. If the user triggered this skill with an issue to log, continue to Step 2 with
   that issue. Don't make them repeat it.

### Config validation

The config is valid if it has:
- `backlog_path`: string, path to the backlog file relative to project root
- `domains`: array of strings, at least one entry
- `default_priority`: one of `high`, `medium`, `low`

If any field is missing or malformed, prompt the user for just the broken fields
rather than re-running the full setup.

## Step 2: Gather issue details

Extract what you can from the user's message and current context. You need:

| Field | Required | How to get it |
|-------|----------|---------------|
| **Title** | Yes | Concise, imperative phrasing from the user's description ("Fix modal close on mobile") |
| **Type** | Yes | `bug`, `feature`, or `improvement`; infer from language, confirm if ambiguous |
| **Domain** | Yes | Match against config domains; infer from open files or what the user is working on |
| **Priority** | Yes | `high`, `medium`, or `low`; fall back to config default if user doesn't specify |
| **Description** | No | One or two sentences of context if the title isn't self-explanatory |
| **Initiative** | No | Link to an initiative record in `~/Projects/initiatives` if this issue serves one (tag as `#initiative:<id>`) |
| **Related files** | No | Include if obvious from context (e.g., the file being edited when the issue was noticed) |

If the user gave enough information to fill everything, confirm the entry in one message
rather than prompting field by field:

> Logging: **#4** `(M)` `#bug` `#ops-dashboard` Fix modal close on mobile
> OK?

If key fields are missing (especially domain or type), ask in one prompt:

> Got it. Quick question: is this a bug or a feature? And which area: ops-dashboard, website, or handbook?

## Step 3: Assign an issue number

Read the existing backlog file and find the highest issue number (`**#N**` pattern).
The new issue gets the next sequential number. If the backlog is empty, start at 1.

## Step 4: Add to backlog

The backlog uses GFM checkboxes grouped by priority, with inline tags for type and
domain. This format is readable, GitHub-renders as interactive checkboxes, and is
easy to edit by hand.

### File template

```markdown
# BACKLOG

> Project issue tracker. Managed by `/log-issue`.

## High

- [ ] **#3** Fix modal close on mobile `#bug` `#ops-dashboard` *(2026-03-22)*
  editPersonModal doesn't dismiss on phone viewports. `ops/src/templates/people.js`

## Medium

- [ ] **#2** Add image lazy loading to post pages `#feature` `#website` *(2026-03-20)*

## Low

- [ ] **#1** Consolidate duplicate CSS docs in handbook `#improvement` `#handbook` *(2026-03-19)*

## Done

- [x] **#0** Example completed issue `#bug` `#website` *(2026-03-15 → 2026-03-18)*
```

When creating a new backlog file, use only the header and section headers (no
example items):

```markdown
# BACKLOG

> Project issue tracker. Managed by `/log-issue`.
```

Priority sections are created as needed when issues are added.

### Format rules

- **Priority sections**: `## High`, `## Medium`, `## Low`, `## Done`
- **Issue line**: `- [ ] **#N** Title text \`#type\` \`#domain\` *(YYYY-MM-DD)*`
- **Initiative tag** (optional): append `\`#initiative:<id>\`` to link the issue to an initiative record
- **Optional detail**: indented line(s) below the issue for description and related files
- **New issues**: add at the top of the appropriate priority section (most recent first)
- **Tags**: use backtick-wrapped hashtags for type (`#bug`, `#feature`, `#improvement`)
  and domain (from config, e.g. `#ops-dashboard`, `#website`)
- **Priority sections**: only create a section when it has items; remove empty sections
- **Don't** duplicate section headers or add metadata fields beyond what's shown

## Step 5: Confirm

Tell the user what was logged, briefly:

> Logged **#3** `(H)` `#bug` `#ops-dashboard`: Fix modal close on mobile

## Step 6: Commit and push

After adding, closing, or updating an issue, commit the backlog change and push:

```bash
git add <backlog_path> && git commit -m "Backlog: [brief description of change]" && git push
```

Use a short commit message like "Backlog: add #26 ops max-width" or "Backlog: close #3".

## Closing issues

When the user says "close issue #3", "mark #3 done", or similar:

1. Change `- [ ]` to `- [x]`
2. Move the line (and any detail lines) to the `## Done` section
3. Append the completion date: `*(2026-03-22 → 2026-03-25)*`
4. Confirm: "Closed **#3**: Fix modal close on mobile"

## Changing priority

When the user says "bump #2 to high" or "deprioritize #3":

1. Move the line (and any detail lines) to the new priority section
2. Create the section if it doesn't exist; remove the old section if now empty
3. Confirm the change

## Adding a domain

When the user references a domain that isn't in the config:

1. Ask: "That domain isn't in the config yet. Add `new-domain` to the list?"
2. If yes, update `.claude/project-tracking.json`

---

## Notes

- The backlog lives at `backlog_path`, by default `BACKLOG.md` at the project root (alongside
  `README.md`) so anyone browsing the repo finds it. Commit it to git.
- This is a quick capture tool, not a project management system. If an issue
  needs detailed specs, create a separate document and link to it from the
  issue's detail line.
- If the user is in the middle of other work and mentions something in passing
  ("oh we should also fix X"), offer to log it rather than switching context.
- When the backlog grows large (50+ items), suggest archiving old `## Done`
  items to a separate `BACKLOG-ARCHIVE.md`.
