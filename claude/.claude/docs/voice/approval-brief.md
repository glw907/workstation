# Register: the approval-queue brief

The reader is Geoff, deciding whether to approve a PR, a design, or a triage list in Design & PR
Approvals. The writer is a Claude session. Geoff reads the brief first, often on a phone, and
should be able to decide from it without opening the diff. Applies to every `## Brief` in a PR
body or a design doc, and to the headline, lede, and rows of a triage file.

Three published standards govern it. The **inverted pyramid** from news writing puts the
conclusion first and each later layer under it in falling order of importance, so a reader who
stops early still has the point. The **Federal Plain Language Guidelines**
(<https://www.plainlanguage.gov/guidelines/>) set the sentence-level rules. **Nielsen Norman
Group** supplies the page-level rules: writing for the web
(<https://www.nngroup.com/articles/how-users-read-on-the-web/>,
<https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/>)
and progressive disclosure
(<https://www.nngroup.com/articles/progressive-disclosure/>). This register is the
approval-brief arm of the authoring charter (`~/.claude/docs/authoring-charter.md`).

The `tellgrader` cadence measures are report-only and defined in
`~/.claude/skills/writing-voice/evals/tellgrader/MEASURES.md`.

## What the standards ask for

- Lead with the conclusion. The headline says what the item does and what approving it causes,
  in one sentence. The lede says why it matters now. Everything below is detail for a reader
  who wants it (inverted pyramid).
- Write for the reader who will act. Use "you" for Geoff and the session's own name for
  itself. Say what happens to him or his machine, not what the code does (plain language:
  "address the reader directly", "write for your audience").
- Use short sentences and common words. Put the subject near the verb, use active voice, and
  prefer a verb to a noun built from one (plain language: "write short sentences", "use active
  voice", "use simple words").
- Keep one idea to a paragraph and the paragraph short. Start each with its topic sentence.
  A reader skims, so the first sentence of each detail has to stand alone (NN/g: concise,
  scannable text).
- Disclose in layers. The brief shows the decision and its consequences. Reasoning, evidence,
  commands, and identifiers sit one click down in a detail section, never in the headline
  or the lede (NN/g: progressive disclosure).
- Name a decision as a decision. A choice only Geoff can make goes in a `### Decide:` block
  with its options, not buried in a sentence. Mark the session's pick `(recommended)`.
- Claim only what the diff and the session evidence. A check you did not run, or a motive the
  change does not show, misleads the one reader who trusts the brief.
- Keep identifiers, paths, and flags in backticks and out of the headline and lede. They
  belong in details.

## The naming rule

The app is "Design & PR Approvals", or "approval" in running text. Never "the desk", "review
desk", or any retired name, in a brief or in a triage file. A real identifier that happens to
carry a retired word is renamed, not quoted.

## The contract

The approval-queue command refuses an item that breaks it, exits 2, and prints the message
below with this register's path, `~/.claude/docs/voice/approval-brief.md`. The parser is
`approval-queue/src/lib/brief.ts`.

- The first `## ` heading outside a code fence is `## Brief`. A `# Title` line above it is
  allowed. CRLF line endings are normalized to LF before parsing.
- The first paragraph under `## Brief` is the headline, then the lede: the first sentence of
  that paragraph is the headline and the rest is the lede. If the paragraph has one sentence,
  the next paragraph is the lede.
- Two subsections are required, in this order: `### What changes`, a bulleted list, and
  `### If you approve`, a numbered list.
- Optional subsections follow. Write them in this order, though the parser accepts any order
  after the required two:
  - Zero or more `### Decide: <title>`. Each holds a paragraph, then an optional `Source: <text>`
    line standing as its own paragraph, then a list of at least two choices. At most one
    choice ends in `(recommended)`.
  - At most one `### Worth knowing`: a paragraph.
  - Zero or more `### <label>` detail sections. Each opens with a paragraph whose first
    sentence is the row summary shown while the row is closed. After that paragraph a section
    may hold lists, code blocks, tables, and more paragraphs, and the page shows them all. A
    section may open with a table instead, such as a score; its closed row shows the label
    alone, so prefer a lead sentence whenever one can say what the table shows.
- Headings match their exact spelling, case included.
- The brief ends at the next `## ` heading. Everything after it is the technical notes.
- A triage file is `{headline, lede, rows: [{action, why, detail, proposed}]}`. `detail` is
  optional. `proposed` is `now`, `defer`, or `drop`, and the page labels them Do now, Do
  later, and Don't do.
- A submitted triage returns `{decision: 'submit', rows: [{action, disposition, note}]}`, so
  Geoff's edit arrives as `note` and the session's `why` is never overwritten. An approve
  returns `{decision: 'approve', choices: [{title, choice}]}`, one entry per "Decide first" card:
  the app's own cards (a failed check, a review that asks for a fix, a `## Before merge` step)
  first, then each `### Decide:` block.

### The states

| Input | Result |
| --- | --- |
| Empty body, no `## Brief`, `## Brief` only inside a code fence, or another `## ` heading first | Refuse: "no `## Brief`; it must be the first `##` heading" |
| First block under `## Brief` is not a paragraph | Refuse: "missing headline" |
| One-sentence first paragraph and no paragraph after it | Refuse: "missing lede" |
| `### What changes` absent, or its first block is not a bulleted list | Refuse, naming `What changes` and the list it needs |
| `### If you approve` absent, or its first block is not a numbered list | Refuse, naming `If you approve` and the numbered list it needs |
| A required heading twice, or `### Worth knowing` twice | Refuse, naming the duplicate |
| A heading that matches a contract heading only when case is ignored | Refuse: "write it as `### What changes`" (the exact spelling) |
| `### Decide:` with no title, fewer than two choices, or two `(recommended)` | Refuse, naming the block and the defect |
| A `Source:` line joined to the paragraph above it | Refuse: "`Source:` must stand as its own paragraph" |
| A detail section that opens with neither a paragraph nor a table | Refuse, naming the label |
| A detail section that opens with a table | Accept; the closed row shows the label alone |
| A block after the one list under `### What changes` or `### If you approve`, or after the one paragraph under `### Worth knowing` | Refuse: "holds only its list" (or "paragraph"); move the rest to a detail section |
| CRLF line endings | Accept (normalized) |
| Triage: not valid JSON | Refuse: "not valid JSON" |
| Triage: a JSON array (the old shape) | Refuse: "old triage shape; write `{headline, lede, rows}`" |
| Triage: missing or empty `headline`, `lede`, or `rows` | Refuse, naming the field |
| Triage: a row missing `action` or `why`, or with `proposed` outside now/defer/drop | Refuse, naming the row number and field |
| Triage: a row with no `detail` | Accept |

## Exemplars

Each exemplar is a fenced block. A block whose info string is `brief` is a Markdown brief and a
block whose info string is `brief-triage` is a triage file; the approval-queue tests extract
both and run the parser over them, so each one must satisfy the contract exactly. A block
tagged plain `markdown` is a counter-example or a skeleton and is never parsed.

### The skeleton

Every part of the contract, with a decision block. The angle-bracket text is a slot.

```markdown
# <PR title>

## Brief

<One sentence: what this does and what approving it causes.>

<Why it matters now, in a sentence or two.>

### What changes

- <A change Geoff will notice.>
- <Another.>

### If you approve

1. <The first thing that happens.>
2. <The next.>

### Decide: <the question, as a title>

<One short paragraph naming what is open and why it needs Geoff.>

Source: <where the question came from>

- <First option> (recommended)
- <Second option>

### Worth knowing

<One paragraph of context that changes no decision.>

### <Detail label>

<A first sentence that stands alone as the closed-row summary. Then the detail.>

## Technical notes

<The agent-facing sections: what landed, the review, the score.>
```

### A PR with nothing to decide (PR #40)

The headline names the change and its consequence, the lede names the problem, and the
identifiers wait in the details.

```brief
## Brief

Every PR a session opens will now come to you for approval, and approving one will merge it.

Small fixes were skipping your approval, and Claude Code was blocking merges you had already approved. This fixes both.

### What changes

- Every PR a session opens comes here. Before, only full planned passes sent theirs.
- A merge you approved goes through. Before, Claude Code blocked it, as with PR #38.

### If you approve

1. The PR merges.
2. This machine’s settings rebuild.
3. Sessions follow it on their next command.

### Worth knowing

The merge permission checks the command, not your approval; the merge guard keeps a merge from skipping your approval.

### The reminder

Fires whenever a session opens a PR. A new hook, `claude-approval-queue-reminder`, runs after each shell command. When the command opened a PR, it tells the session to send it here for your approval and wait. It stays quiet for an executor whose conductor hands the PR over, and for a small pass that merges itself.

### The merge permission

Only the exact commit you approved can merge. A permission rule allows `gh pr merge * --match-head-commit *`. GitHub refuses the merge if the branch moved after your approval.

### Testing

A new test covers the reminder; the full check passed. Five cases: a PR opened, one opened inside a longer command, a different `gh` command, a failed open, and unreadable input.
```

### A triage list (drafter Pass 0)

The headline is the one call that needs Geoff now, the lede counts the rest, and each row's
`why` is a plain reason in a sentence. Technical references go in `detail`.

```brief-triage
{
  "headline": "One follow-up needs doing before the next docs run.",
  "lede": "Pass 0’s review found eight small gaps. The session proposes doing one now, four later, and skipping three. Change any call you disagree with.",
  "rows": [
    {
      "action": "Teach cairn’s docs review page to read the new plan format.",
      "why": "Plans now save as YAML; until this lands the review page shows no plan for a new page, and the next docs run depends on it.",
      "detail": "From workstation#36: `scripts/docs-review/embed.mjs` `planPathFor` reads only `<slug>.plan.md`, so it can't show a `.plan.yaml`. Your ruling, 2026-10-12: land before the next YAML chain run.",
      "proposed": "now"
    },
    {
      "action": "Make the plan checker catch a note written after a title or heading.",
      "why": "A note there silently cuts the title short, with the page link built from it. Not seen in a real plan yet.",
      "detail": "From drafter#1: `title` and `heading` are not prose fields, so `title: X # note` is cut at the comment with no finding.",
      "proposed": "defer"
    },
    {
      "action": "Flag a link that points only at “#”.",
      "why": "It passes silently today, and it’s rare.",
      "detail": "From drafter#1: a bare `#` link target passes silently.",
      "proposed": "defer"
    },
    {
      "action": "Check that each plan’s page path points inside the repo.",
      "why": "A path outside the repo sends the link warnings to the wrong place.",
      "detail": "From drafter#1: `page.path` is not validated as repo-relative.",
      "proposed": "defer"
    },
    {
      "action": "Replace a needless pattern match with a plain text search.",
      "why": "Tidier code, no change in behavior.",
      "detail": "From drafter#1: `bracketRe` is a regexp for a literal `[`.",
      "proposed": "defer"
    },
    {
      "action": "Skip the no-facts warning when a facts list is empty.",
      "why": "Harmless as it is; an empty list is rare.",
      "detail": "From drafter#1: a `sentence` with `facts: []` still gets the warning.",
      "proposed": "drop"
    },
    {
      "action": "Read the facts folder once per run, not once per plan.",
      "why": "Only a speed-up, and runs have few plans.",
      "detail": "From drafter#1: `LoadFacts` re-reads the facts directory for each plan.",
      "proposed": "drop"
    },
    {
      "action": "Move the end-to-end test’s program path out of a shared variable.",
      "why": "It’s the standard Go test setup; nothing to gain.",
      "detail": "From drafter#1: `e2e` keeps the built binary path in a package global.",
      "proposed": "drop"
    }
  ]
}
```

### Before and after: a real PR body

The source is the dotfiles PR for the drafter Pass 0 plan
(`docs/superpowers/plans/2026-10-12-drafter-pass0-plan.md`, "Close"). The "before" opens as most
PR bodies open today: a record of the work, in the author's order, for a reader who already
knows the plan. Geoff has to dig for what approving does.

```markdown
## What landed

- T1 through T7 and the close, per the plan.
- Chain change in T6, end-to-end run on one cairn page in T7.
- `drafter check-plan` added in glw907/drafter; see that PR.

## Review

Whole-branch `diff-reviewer` run on the branch.

## Found, not done

- cairn review-page follow-up (now).
- `planFormat: "markdown"` escape hatch for in-flight runs.
```

The "after" opens with the decision and its consequences. The record of the work moves below
the brief, into the technical notes, where it was already.

```brief
## Brief

Planners can now write a docs page’s plan as YAML and check it with `drafter check-plan`, and the docs page chain’s plan step now writes YAML plans and runs that check until it passes.

Cairn’s docs review page reads only Markdown plans, so a YAML plan shows nothing there until a follow-up lands. That follow-up has to land before the next chain run that uses YAML plans.

### What changes

- A planner writes `<page>.plan.yaml` and runs `drafter check-plan`. Every finding prints as `file:line` with the fix.
- The chain’s plan step writes YAML plans and reruns the check until it exits 0. The back half of the chain drafts from a YAML plan unchanged.

### If you approve

1. The drafter PR in `glw907/drafter` merges first, and the drafter installs from its `main`.
2. This PR merges and the checkout pulls.
3. The session runs `check-drift` and tells the cairn docs sessions the merge time and the escape hatch.

### Worth knowing

The cairn review-page follow-up is the one item proposed for now, on your ruling of 2026-10-12.

### The escape hatch

The `planFormat: "markdown"` setting keeps in-flight runs on Markdown plans. A run already under way can finish on the old format.

### The two PRs

Two PRs carry this pass. The drafter PR holds the tool and this one holds the chain change; each body names the other.

## What landed

- T1 through T7 and the close, per the plan.
```

The trailing `## What landed` stands for the technical notes that follow the brief; the parser
stops at it.

## Off-voice contrast

A headline and lede written the way the work felt to the author, not the way the decision
looks to the reader: process narration, identifiers up front, and no consequence.

```markdown
## Brief

Refactored the hook so that claude-approval-queue-reminder now matches gh pr create via PREFILTER and emits additionalContext.

In this PR I went ahead and updated the hook and the settings manifest and added tests, which should make things more robust going forward.
```
