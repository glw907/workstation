---
name: revise-claude-md
description: Audit and clean up CLAUDE.md for bloat and staleness
---

Review the current project's CLAUDE.md for hygiene and maintainability.

## Purpose

This is a **maintenance skill** - it cleans up existing documentation, not adds new content.
(Use `/doc-review` to add new documentation after work sessions.)

## What to Check

### 1. Bloat and Redundancy
- Duplicate information (same thing said multiple ways)
- Content that belongs in docs/ instead
- Verbose prose where a table would suffice
- Documentation of obvious behavior

### 2. Staleness
- Commands that fail when run
- File paths that don't exist
- TODOs completed long ago
- References to removed features
- Outdated version numbers

### 3. Structure
- Quick reference table points to correct docs/ files
- Critical constraints are actually critical
- Common operations are still common
- File is under 400 lines (if over, suggest moving content to docs/)

### 4. Accuracy
- Cross-references work (files/sections exist)
- Commands are copy-paste ready
- Links aren't broken

## Process

1. Read CLAUDE.md
2. Read relevant docs/ files to check for duplication
3. Test a sample of commands (if safe to run)
4. Identify issues in order of severity:
   - **High**: Broken commands, wrong paths, false information
   - **Medium**: Bloat, redundancy, poor organization
   - **Low**: Minor wording improvements

5. Propose changes as diffs
6. Ask for approval before making changes

## Output Format

```
CLAUDE.md Audit for [project name]

Current status:
- Length: X lines (target: <400)
- Last modified: [date from git]

Issues found:

HIGH PRIORITY:
1. [Issue with impact]
   → Proposed fix: [specific change]

MEDIUM PRIORITY:
2. [Bloat/redundancy issue]
   → Suggested: [consolidation approach]

LOW PRIORITY:
3. [Minor improvement]

Proposed changes:
[show diffs for HIGH priority items]

Approve HIGH priority fixes? (yes/no)
```

If no issues:
```
CLAUDE.md looks healthy:
- Length: X lines (within target)
- No broken references
- No obvious bloat
- Commands tested successfully

No changes needed.
```

## Guidelines

- **Be conservative**: Only flag real problems, not style preferences
- **Show impact**: Explain why each change matters
- **Prioritize**: Fix broken things before trimming prose
- **Respect decisions**: If something seems odd but is documented in architecture.md as intentional, leave it
