---
name: issue-review
description: Review session for GitHub issue updates (close, comment, create)
---

Review this session's work and suggest GitHub issue actions.

## Guidelines

**Be conservative** - only suggest actions you are confident about. Missing an update is less harmful than a false close or duplicate issue.

**Confidence thresholds:**
- **Close:** High confidence only. Clear evidence the issue is fully resolved AND tested.
- **Comment:** Medium confidence. Meaningful progress or decisions worth recording.
- **Create:** Deliberate. A concrete task was identified, not a vague idea.

**Testing requirement for closure:**
- **build issues:** Must have browser/end-user testing verification, not just deployment
- **fix issues:** Must verify the fix actually resolves the reported problem
- **ops issues:** Depends on task - configuration changes should be verified working

## GitHub CLI Constraints

`gh issue view` fails due to GitHub Projects Classic deprecation. Use these instead:
- `gh issue list --search "keyword"` - Find issues
- `gh issue list --state open --limit 50` - List open issues
- `gh issue comment NUMBER --body "text"` - Add comment
- `gh issue close NUMBER --comment "text"` - Close with comment
- `gh issue create --title "..." --body "..." --label "fix|build|ops"` - Create

## Process

### Step 1: Gather Context

1. Review the session transcript for:
   - What work was completed (commits, file changes, deployments)
   - What bugs were found or fixed
   - What decisions were made
   - What follow-up work was identified

2. List open issues:
   ```
   gh issue list --state open --limit 50
   ```

3. Search for issues related to session work:
   ```
   gh issue list --search "relevant keywords"
   ```

### Step 2: Match Session Work to Issues

For each open issue, assess:
- Was this issue's goal **fully achieved AND tested** in this session? → Suggest close
- Was **meaningful progress** made (code written, deployed, but not tested)? → Suggest comment
- Was the issue **discussed but no action taken**? → Skip (no action)

**"Fully achieved" means:**
- Code/config is written, committed, and deployed
- Functionality has been tested in the target environment (browser, CLI, etc.)
- Issue's acceptance criteria are demonstrably met
- No known bugs or incomplete work remain

### Step 2b: Check for Roadmap Updates

After matching issues, ask: **does any suggested closure complete a workstream phase?**

The roadmap (`docs/implementation-roadmap.md`) tracks phases, not individual issues. Most closures don't require a roadmap update. But when a phase-completing issue is closed, update the roadmap alongside it.

**Phase-completing signals:**
- Issue title includes "Phase N", "WS1", "WS2", etc.
- Issue was the last blocker for a phase (e.g., final test or final feature)
- A workstream section in the roadmap still says "In Progress" or "Not Started" but the work is now done

**If a roadmap update is needed:**
- Update the phase status and completion date in `docs/implementation-roadmap.md`
- Update the Summary table at the bottom
- Update the "Current focus" line if it has shifted
- Include the roadmap file in the commit alongside the issue closure

### Step 3: Identify New Issues

Review session for:
- Bugs discovered but not fixed in this session
- Follow-up tasks explicitly identified
- Prerequisites discovered for future work
- Scope explicitly split from existing issues

**Do NOT create issues for:**
- Work already completed (commit message is sufficient)
- Vague ideas mentioned in passing
- Things already covered by an existing open issue

### Step 4: Present Suggestions

Group by action type. For each suggestion, show the evidence.

## Output Format

```
GitHub Issue Review
==================

Session summary: [1-2 sentence description of work done]

CLOSE (N issues):

  #42 - [Issue title]
  Evidence: [specific commits/changes that resolve this]
  Closing comment: "[proposed comment text]"

COMMENT (N issues):

  #55 - [Issue title]
  Evidence: [what progress was made]
  Comment: "[proposed comment text]"

CREATE (N issues):

  Title: [proposed title]
  Label: [fix|build|ops]
  Body: "[proposed body text]"
  Why: [what in the session identified this need]

NO ACTION (N issues reviewed, no match):
  [Listed only if helpful for transparency]

Approve? (all / select by number / none)
```

If nothing to do:
```
GitHub Issue Review
==================

Session summary: [brief summary]

No issue actions needed. Session work was either:
- Already tracked and no progress to report
- Completed work that doesn't map to any open issue
- Exploratory/discussion with no actionable outcomes
```

## Closing Comment Style

When composing closing comments, follow the project convention:
- Brief explanation of what was done
- Reference relevant commits if helpful
- Keep it to 1-3 sentences

Example: "Implemented contact form with Turnstile validation, Resend email delivery, and category-based routing. Worker deployed and tested end-to-end."

## Issue Creation Style

When suggesting new issues, follow `docs/infrastructure/github-issues.md`:
- Clear, specific title
- Exactly one label: `fix`, `build`, or `ops`
- Body with context and (for build) acceptance criteria
- Check `launch` milestone applicability

## Execution

After user approves:
1. Execute approved close actions
2. Execute approved comment actions
3. Execute approved create actions
4. Show confirmation of each action taken
