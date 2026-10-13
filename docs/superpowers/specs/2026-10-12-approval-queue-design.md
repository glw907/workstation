# Approval queue: briefs, page redesign, and rename

## Brief

Every item a session sends you will open with a plain-language brief, and the page will lead with it.

Today a session hands you its agent-facing notes: file paths, hook names, and a list of what landed. This pass gives every item a headline, a short lede, what approving sets off, and any decision you must make first, all written for you. The page puts that brief on top and moves the checks, diff, and technical notes below it. The tool is also renamed from `review-desk` to `approval-queue`, and the window becomes "Design & PR Approvals".

### If you approve

1. A session plans the pass from this design and hands it to the dotfiles conductor.
2. The executor builds it and opens one PR, which comes to you for approval.
3. After that PR merges, every new item arrives with a brief, and an item without one is refused.

### Needs your attention

The rename leaves no `review-desk` alias. The cairn-cms and dubplate passes now running call that name, so the merge waits until their sessions have handed over, or until each has been told the new name.

### The brief contract

A PR body, a design doc, and a triage list each open with the brief. In a PR or design, `## Brief` holds the headline as its first sentence, then the lede. `### What changes` and `### If you approve` follow as short lists. `### Needs your attention` comes only when something does. Then one `### <label>` per detail, whose first sentence is the one-line summary shown while the row is closed. The PR body's existing sections stay below as the technical notes.

A triage file becomes `{headline, lede, rows}`. Each row carries `action` (the plan in plain words), `why` (what's at stake and why it got this call), `detail` (today's technical text), and `proposed`. Geoff's edit returns as a separate `note`, so the session's reason is never overwritten.

### The writing rules

A new register, `~/.claude/docs/voice/desk-brief.md`, is built on three standards: the inverted pyramid from news writing, the Federal Plain Language Guidelines (<https://www.plainlanguage.gov/guidelines/>), and Nielsen Norman Group's guidance on writing for the web and on progressive disclosure. Its exemplars are this session's two mock-up briefs (PR #40 and the drafter Pass 0 triage) and a before-and-after pair from a real PR body. The visible copy calls the app "Design & PR Approvals" or "approval", never "the desk".

### Enforcement

`approval-queue` refuses an item whose brief is missing or incomplete (exit 2). The refusal names the missing part and the register's path. The same pointer goes in the places sessions read: the hook text, `pass-core` Close, and the commit-and-PR register.

### The page

The page follows the approved mock-ups in `2026-10-12-approval-queue-mockups/`: the generator, the rendered pages and screenshots, the settled decisions log, and the three audit ledgers. Highlights:

- **Headline block:** one filled block holds the serif headline, the sans lede, and "What changes" and "If you approve".
- **Decide first:** cards with choice buttons, and Approve stays locked until each card has a choice. The app itself promotes a failing check, a "fix" or "escalate" review, and a `## Before merge` step into these cards.
- **Details and Evidence:** quieter disclosure rows below the block.
- **Triage:** rows with Do now / Do later / Don't do choices, a Note button, and a Technical detail toggle.
- **Decision bar:** a floating bar with a status summary.

The build is all DaisyUI components, and every surviving audit fix is applied.

### The rename

| From | To |
|---|---|
| `review-desk` command | `approval-queue` |
| `review-desk/` app | `approval-queue/` |
| `~/.local/state/review-desk` | `~/.local/state/approval-queue` |
| `claude-desk-reminder` hook | `claude-approval-queue-reminder` |
| "Review desk" window title | "Design & PR Approvals" |

Every live reference goes, with no alias left behind (Geoff, 2026-10-12: "Make sure the review-desk references are fully expunged from the claude infa."). That covers all 16 dotfiles files that name the desk: `pass-core`, `settings.json`, the command and the hook, `scripts/check.sh`, the tests, STATUS, and ROADMAP. A new leg in `scripts/check.sh` fails the gate if `review-desk` or `claude-desk-reminder` appears anywhere in the repo outside `docs/superpowers/` and `docs/HISTORY.md`, so the name cannot come back. Plans and prompts that have already run, in any repo, are history and stay as written.

The PR's `## Before merge` section carries two steps. First, confirm that no live session in cairn-cms or dubplate still needs `review-desk`, or send each one the new command. Second, move the state folder while no item is waiting.

### Out of scope

- Changing the server, the port (7907), or how decisions are returned.
- Generating briefs with a model.
- A fallback layout for items without a brief.

### Check, end to end

Put this design in the queue with the built tool and confirm three things: it renders with its brief on top, a copy with the brief removed is refused, and the drafter triage file in the new shape renders as the mock-up does.

### Class and estimate

`runner` (settings, skills, scripts, tests), no live-account flag. About 420 path minutes.
