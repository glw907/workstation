---
name: doc-review
description: Review session for documentation opportunities
---

Review this session's transcript for documentation opportunities.

## Guidelines

**Only suggest documenting if ALL these apply:**
1. It's an architectural decision, troubleshooting discovery, or useful pattern
2. It's NOT obvious from code
3. It would help future sessions
4. It can be expressed in 1-2 lines

**Be conservative** - over-documentation wastes tokens and reduces performance.

## Decision Framework

**Where to document:**
- Cross-site patterns (DNS, Cloudflare API, Wrangler) → `~/Projects/cloudflare-sites/CLAUDE.md` or `docs/services/`
- Site-specific architecture → That site's `CLAUDE.md` or `docs/architecture.md`
- Troubleshooting → That site's `docs/operations.md`
- One-off fixes → Don't document

## Process

1. Review the session transcript
2. Identify 0-2 items worth documenting (be strict)
3. For each item, propose:
   - What to document (1-2 lines)
   - Where to add it (specific file and section)
   - Why it's worth documenting

4. Show proposed changes as diffs
5. Ask for approval before making changes
6. Only update files after explicit approval

## Output Format

If you find something worth documenting:
```
Found 1 item worth documenting:

1. [Brief description]
   → Add to: [file path]:[section]
   → Why: [reason]

Proposed change:
[show diff]

Approve? (yes/no)
```

If nothing significant:
```
No significant documentation opportunities found. Session focused on [brief summary].
```
