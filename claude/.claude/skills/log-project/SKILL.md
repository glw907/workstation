---
name: log-project
description: >
  Create or update a strategic initiative in ROADMAP.md. Use when the user
  wants to track a multi-issue effort, larger project, or initiative — something
  bigger than a single backlog item. Trigger on: "log project", "new project",
  "start an initiative", "add to roadmap", "track this effort", "we need a
  project for", or when the user describes a multi-step effort that spans
  several backlog items. Also trigger on "close project", "finish project",
  "project status", or "update roadmap".
---

# Log Project

Create or update a strategic initiative in the project's `ROADMAP.md`.
Projects are multi-issue efforts that group related backlog items under
a shared goal. The roadmap tells the story of *where we're going*;
the backlog (`BACKLOG.md`) tracks the individual pieces of work.

---

## Step 1: Read project config

Look for `.claude/project-tracking.json` in the project root. This config is
shared with the `/log-issue` skill.

```json
{
  "backlog_path": "BACKLOG.md",
  "roadmap_path": "ROADMAP.md",
  "domains": ["ops-dashboard", "website", "handbook"],
  "default_priority": "medium"
}
```

If the config file doesn't exist, run the `/log-issue` first-run setup
(it creates the shared config). Then return here.

If `ROADMAP.md` doesn't exist yet, create it with the template from Step 4.

## Step 2: Determine the action

| User intent | Action |
|-------------|--------|
| "Log project", "new initiative", describes a multi-step effort | **Create** a new project |
| "Update project X", "add progress to X" | **Update** an existing project |
| "Close project X", "project X is done" | **Close** a project |
| "Project status", "show roadmap" | **Report**: read ROADMAP.md and summarize |

## Step 3: Gather project details (for create)

| Field | Required | How to get it |
|-------|----------|---------------|
| **Title** | Yes | Short name for the initiative |
| **Slug** | Yes | Kebab-case identifier derived from title (e.g., `mobile-redesign`). Used in `#project:slug` tags on backlog items |
| **Description** | Yes | 1-3 sentences: what, why, and what success looks like |
| **Status** | Yes | `Active`, `Planned`, or `Someday`; infer from urgency, default to `Planned` |
| **Related issues** | No | Scan `BACKLOG.md` for items that belong to this project |
| **Domains** | No | Which areas this project touches (from config domains) |

If the user gave enough information, confirm in one message:

> Creating project **mobile-redesign** (Active):
> "Redesign ops dashboard for mobile-first usability. Fix layout, tables,
> and navigation on phone viewports."
> Related backlog items: #13, #14
> OK?

## Step 4: Write to ROADMAP.md

### File template

```markdown
# ROADMAP

> Strategic initiatives. Managed by `/log-project`. Issues tracked in `BACKLOG.md`.

## Active

### Mobile-first ops dashboard redesign `mobile-redesign`
Redesign ops dashboard for mobile-first usability. Fix layout, tables,
and navigation on phone viewports.
Related: #13, #14

## Planned

### Photo gallery integration `photo-gallery`
Add member photo sharing via Immich. Requires hosting decision before
development can begin.
Related: #20, #21

## Someday

### Race results platform `race-results`
Research and build a solution for recording and displaying race results.
Related: #18

## Done

### Infrastructure coherence improvement `infra-coherence`
Standardized patterns across all services: error handling, logging, CSS
architecture, notification routing, documentation sync. 16 sessions.
Completed: 2026-03-22
```

When creating a new roadmap file, use only the header; sections are
created as needed:

```markdown
# ROADMAP

> Strategic initiatives. Managed by `/log-project`. Issues tracked in `BACKLOG.md`.
```

### Format rules

- **Status sections**: `## Active`, `## Planned`, `## Someday` (a `## Done` only where the file already has one)
- **Project heading**: `### Title \`slug\``
- **Body**: 1-3 sentences of description, then `Related: #N, #N` linking to backlog items
- **Slug**: appears in backticks after the title; this is the identifier used
  in `#project:slug` tags on backlog items
- **New projects**: add at the top of the appropriate section
- **Only create sections that have items**; remove empty sections

## Updating a project

When updating an existing project:

1. Add or update the description text
2. Update the `Related:` line if new backlog items were added
3. Move between sections if status changed (e.g., Planned → Active)
4. Remove the old section if now empty

## Commit and push

After creating, updating, or closing a project, commit and push:

```bash
git add ROADMAP.md && git commit -m "Roadmap: [brief description]" && git push
```

If backlog items were also modified (e.g., adding `#project:slug` tags), include `BACKLOG.md` in the commit.

## Closing a project

When closing a project:

1. Remove the project block from `ROADMAP.md`: git history and the closing PR body hold the record
   (lean pass process, ruling 8), so a shipped item leaves ROADMAP. Read the file's existing
   sections first and never seed a tier it does not already have. A repo whose ROADMAP already
   keeps a `## Done` section may append the block there with `Completed: YYYY-MM-DD`.
2. Put a one-line outcome summary in the commit message
3. Check `BACKLOG.md` for any open items tagged `#project:slug`:
   - If they're truly done, close them (change `- [ ]` to `- [x]`, move to Done)
   - If they're still open but no longer part of this project, remove the project tag
4. Confirm: "Closed project **slug**: Title"

## Auto-closing

When all backlog items tagged `#project:slug` are checked off (`- [x]`),
mention to the user that the project may be complete:

> All backlog items for **mobile-redesign** are done. Want me to close the project?

Don't close automatically. The user may want to add more items, or the
project may have work that isn't tracked as individual issues.

---

## Notes

- `ROADMAP.md` lives at the project root alongside `BACKLOG.md`. Commit it to git.
- Projects are lightweight: a title, a paragraph, and links to backlog items.
  Don't turn them into detailed project plans. If a project needs detailed
  planning, use Plan mode or a separate document and link to it.
- The `Related:` line is a convenience, not a constraint. Not every backlog
  item in a project needs to be listed, and not every listed item needs a
  `#project:slug` tag. Both are useful but neither is required.
- When creating a project, scan the existing backlog for items that obviously
  belong and offer to tag them with `#project:slug`.
