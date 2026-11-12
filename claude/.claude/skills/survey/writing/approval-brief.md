# Register: the approval-queue brief

The reader is Geoff, deciding what to approve in the Approval Queue. The writer is a Claude
session. The unit he decides on is the **packet**: one file that carries every PR, design, and plan
step a session hands over at a decision point, with the questions only he can answer. Geoff reads at
a desk in a desktop browser, never on a phone, and he reads closed states first. He should be able to
decide from them without opening a diff. Applies
to every packet. The older kinds still exist and keep their contract below: the `## Brief` of a PR
body or a design doc, and a triage file.

Three published standards govern it. The **inverted pyramid** from news writing puts the
conclusion first and each later layer under it in falling order of importance, so a reader who
stops early still has the point. The **Federal Plain Language Guidelines**
(<https://www.plainlanguage.gov/guidelines/>) set the sentence-level rules. **Nielsen Norman
Group** supplies the page-level rules: writing for the web
(<https://www.nngroup.com/articles/how-users-read-on-the-web/>,
<https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/>)
and progressive disclosure
(<https://www.nngroup.com/articles/progressive-disclosure/>). A packet's title follows the
**Google developer documentation style guide** for headings
(<https://developers.google.com/style/headings>): sentence case and no closing punctuation. This
register is the approval-brief arm of the authoring charter (`~/.claude/docs/authoring-charter.md`).

The `tellgrader` cadence measures are report-only and defined in
`~/.claude/skills/writing-voice/evals/tellgrader/MEASURES.md`.

## The four rules

The packet adds four rules to the standards. They are what separates a packet that decides from
one that only reports.

1. **Layer, summary first.** Every block a reader can open has a closed state that states its
   point as a full sentence. Draft that sentence first and the detail second. Most decisions
   should be possible from the closed states alone.
2. **Completed staff work.** An ask arrives researched. Read the files, PRs, review findings, and
   logs the decision turns on, and cite each fact's source. A question the facts settle is a
   routine part, not an ask. A PR Geoff held before comes back as an ask under
   `contradicts-ruling`, never as a routine row. A PR he sent back and the session fixed
   returns as a revision, which may be a routine row.
3. **Not checked never hides a deciding fact.** When an ask turns on an unchecked fact, check it,
   or raise the ask as `low-confidence` and say why the fact is out of reach. `## Not checked`
   holds only what no ask depends on.
4. **The description decides.** The title names the packet, and the description under it is
   what Geoff decides from, about nine times in ten, without opening anything below it. It opens
   with a background paragraph, then one or two summary paragraphs that say what is proposed,
   what approving does, and how the work gets built or carried out. A summary of a sentence or
   two is for a change that really is that simple.

Aim for about 400 words from the title through `## Not checked`, counted as whitespace-separated
tokens outside code fences. The command does not enforce it; the monthly review reports packets
over it.

### House departure: background before the summary

The inverted pyramid puts the conclusion first. A packet's description puts its background
paragraph first and the summary after it (Geoff, 2026-10-21). He reads the context first, so the
summary lands, and the background is one short paragraph, so the decision still comes early. The
departure covers the description only: every block below it keeps its summary first.

### The title and the description

The title is a Google-style heading: sentence case, no closing punctuation, and at most 80
characters. It names the thing being decided, usually as a noun phrase ("Proton Pass
folder-deletion fix"). It never narrates the packet ("This packet merges...") or says what
approving causes; the summary carries both.

The background paragraph places the packet in its initiative, says what came before and why it is
in front of Geoff now, and gives a plain meaning for any term he would not know.

The summary carries the decision. It says what each part changes, in words he would use, and
what approving does, including anything that cannot be undone and anything he runs himself. It
gives the shape of the plan, enough to judge whether the work is sensible without reading it.
When an ask is open, it names the question and the session's recommendation. When the work
has a known weak spot, such as a check that failed or a test that ran on samples only, it says
so here.

## What the standards ask for

- Lead with the conclusion. In a packet, the description holds the conclusion, after the one
  background paragraph the house departure above allows. On the older kinds, the headline says
  what the item does and what approving it causes, in one sentence, and the lede says why it
  matters now. Everything below is detail for a reader who wants it (inverted pyramid).
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
  commands, and identifiers sit one click down in a detail section, never in a title, a
  headline, or a lede (NN/g: progressive disclosure).
- Name a decision as a decision. A choice only Geoff can make goes in a `### Decide:` block
  with its options, not buried in a sentence. Mark the session's pick `(recommended)`.
- Claim only what the diff and the session evidence. A check you did not run, or a motive the
  change does not show, misleads the one reader who trusts the brief.
- Keep identifiers, paths, and flags in backticks and out of the title, headline, and lede. They
  belong in details. A packet's summary may name a PR by number.

## The naming rule

The app is "the Approval Queue" in a sentence and "Approval Queue" on its own, as in a page
title. Never "Design & PR Approvals", "the desk", "review
desk", or any retired name, in a brief or in a triage file. A real identifier that happens to
carry a retired word is renamed, not quoted.

## The packet writer's brief

A packet is written by a fresh agent from a fact file. This brief is its whole style brief, and
nothing else in this file governs a packet. Its first part is the text block in "Make reports easy
to follow" on Anthropic's page [Prompting Claude Fable 5.2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2#make-reports-easy-to-follow):

```text
# Communicating clearly
Write for an intelligent but low-context reader. The person reading has not seen your tool calls, your reasoning or the files you opened, and may be switching in from other work. Messages should generally be self-contained: the reader should understand what you mean without having to dig for other context. Put the key points in the first few sentences. Practice progressive disclosure in your sentence order, and do not use undefined references and ideas in line 1 that won't make sense until the reader reaches line 12.

Use plain words, and write in clear, understandable full sentences. Do not use a term or abbreviation that you made up during the work. Say what the thing is in a way any reader would understand. Write mostly in the style of ASD-STE100 Simplified Technical English: short sentences, one idea per sentence, active voice, and consistently using the same word for the same thing. Use a paragraph of flowing prose where ideas connect, and keep bullets for lists of separate items. Leave out unnecessary details unless the reader asks and practice concision, but do ensure that your messages have the key context. Aim to make your user-facing text as human-readable and clear as possible.
```

Six lines follow the block.

- This is technical writing. Use literal terms and the real names of tools, files, and settings. No metaphor and no personification.
- No filler. Every sentence states a fact or tells the reader what to do.
- Name a thing by what it is. A project nickname is a term made up during the work.
- Write the opening as paragraphs.
- Keep session names, commit hashes, task numbers, and risk-class names out of the opening and the calls.
- Approving a stop packet answers its question. The session runs the listed steps and resumes the pass, and the approval merges nothing. Say so where the packet says what approving does.

The same page says the model follows style rules closely and that stacked rules make its prose
choppy. The brief therefore stands alone: it replaces the packet rules this file once held, and
no style rule is added to it. The sixth line states a fact about the queue.

## The brief contract

The approval-queue command refuses a `pr`, `design`, or `triage` item that breaks it, exits 2, and prints the message
below with this register's path, `~/.claude/docs/voice/approval-brief.md`. The parser is
`~/Projects/approval-queue/approval-queue/src/lib/brief.ts`.

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
- A packet's fact file may carry a `round` key, the id of the round the packet belongs to:
  lowercase letters, digits, and hyphens, starting with a letter, 12 characters at most.
  `approval-queue packet --check` refuses any other value and names the rule.

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

Each exemplar is a fenced block. A block whose info string is `brief` is a Markdown brief, a block
whose info string is `brief-triage` is a triage file, and a block whose info string is `packet` is
a packet in a four-backtick fence; the approval-queue tests extract all three, close each at a
fence of the opening width, and run the parser over them, so each one must satisfy its contract
exactly. A block
tagged plain `markdown` is a counter-example or a skeleton and is never parsed.

### The brief skeleton

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

Only the exact commit you approved can merge. A permission rule allows `Bash(approval-queue merge *)`. The command merges the PR at the commit you approved, and GitHub refuses the merge if the branch moved after your approval.

### Testing

A new test covers the reminder; the full check passed. Five cases: a PR opened, one opened inside a longer command, a different `gh` command, a failed open, and unreadable input.
```

### A triage list (scribe config pass)

The headline is the one call that needs Geoff now, the lede counts the rest, and each row's
`why` is a plain reason in a sentence. Technical references go in `detail`.

```brief-triage
{
  "headline": "One follow-up needs doing before the next run.",
  "lede": "The config pass’s review found eight small gaps. The session proposes doing one now, four later, and skipping three. Change any call you disagree with.",
  "rows": [
    {
      "action": "Teach the review page to read the new settings format.",
      "why": "Settings now save as YAML; until this lands the review page shows no settings for a new report, and the next run depends on it.",
      "detail": "From scribe#2: `scripts/review/embed.mjs` `settingsPathFor` reads only `<slug>.settings.md`, so it can't show a `.settings.yaml`. Your ruling, 2026-10-12: land before the next YAML run.",
      "proposed": "now"
    },
    {
      "action": "Make the settings checker catch a note written after a title or heading.",
      "why": "A note there silently cuts the title short, with the report link built from it. Not seen in real settings yet.",
      "detail": "From scribe#1: `title` and `heading` are not prose fields, so `title: X # note` is cut at the comment with no finding.",
      "proposed": "defer"
    },
    {
      "action": "Flag a link that points only at “#”.",
      "why": "It passes silently today, and it’s rare.",
      "detail": "From scribe#1: a bare `#` link target passes silently.",
      "proposed": "defer"
    },
    {
      "action": "Check that each report’s output path points inside the repo.",
      "why": "A path outside the repo sends the link warnings to the wrong place.",
      "detail": "From scribe#1: `report.path` is not validated as repo-relative.",
      "proposed": "defer"
    },
    {
      "action": "Replace a needless pattern match with a plain text search.",
      "why": "Tidier code, no change in behavior.",
      "detail": "From scribe#1: `bracketRe` is a regexp for a literal `[`.",
      "proposed": "defer"
    },
    {
      "action": "Skip the no-sources warning when a sources list is empty.",
      "why": "Harmless as it is; an empty list is rare.",
      "detail": "From scribe#1: a `section` with `sources: []` still gets the warning.",
      "proposed": "drop"
    },
    {
      "action": "Read the sources folder once per run, not once per report.",
      "why": "Only a speed-up, and runs have few reports.",
      "detail": "From scribe#1: `LoadSources` re-reads the sources directory for each report.",
      "proposed": "drop"
    },
    {
      "action": "Move the end-to-end test’s program path out of a shared variable.",
      "why": "It’s the standard Go test setup; nothing to gain.",
      "detail": "From scribe#1: `e2e` keeps the built binary path in a package global.",
      "proposed": "drop"
    }
  ]
}
```

### Before and after: a PR body

The example is a PR for the scribe config pass. The "before" opens as most
PR bodies open today: a record of the work, in the author's order, for a reader who already
knows the plan. Geoff has to dig for what approving does.

```markdown
## What landed

- T1 through T7 and the close, per the plan.
- Runner change in T6, end-to-end run on one report in T7.
- `scribe check-config` added in glw907/scribe; see that PR.

## Review

Whole-branch `diff-reviewer` run on the branch.

## Found, not done

- Review-page follow-up (now).
- `settingsFormat: "markdown"` escape hatch for in-flight runs.
```

The "after" opens with the decision and its consequences. The record of the work moves below
the brief, into the technical notes, where it was already.

```brief
## Brief

Authors can now write a report’s settings as YAML and check them with `scribe check-config`, and the runner’s setup step now writes YAML settings and runs that check until it passes.

The review page reads only Markdown settings, so YAML settings show nothing there until a follow-up lands. That follow-up has to land before the next run that uses YAML settings.

### What changes

- An author writes `<report>.settings.yaml` and runs `scribe check-config`. Every finding prints as `file:line` with the fix.
- The runner’s setup step writes YAML settings and reruns the check until it exits 0. The rest of the runner reads YAML settings unchanged.

### If you approve

1. The scribe PR in `glw907/scribe` merges first, and scribe installs from its `main`.
2. This PR merges and the checkout pulls.
3. The session runs `check-drift` and tells the sessions that use scribe the merge time and the escape hatch.

### Worth knowing

The review-page follow-up is the one item proposed for now, on your ruling of 2026-10-12.

### The escape hatch

The `settingsFormat: "markdown"` setting keeps in-flight runs on Markdown settings. A run already under way can finish on the old format.

### The two PRs

Two PRs carry this pass. The scribe PR holds the tool and this one holds the runner change; each body names the other.

## What landed

- T1 through T7 and the close, per the plan.
```

The trailing `## What landed` stands for the technical notes that follow the brief; the parser
stops at it.

## Off-voice contrast

A packet title that carries the whole decision, over a description that only says why now.
The title narrates the packet and what approving causes, and the summary that should hold both is
missing.

```markdown
# This packet merges a fix that stops Claude deleting Proton Pass folders, and approving re-pins the upgraded Proton Pass CLI.

The CLI on pavilion moved to 2.5.1 today. That version added folders, and Claude's wrapper let folder deletion through until this fix.
```

A headline and lede written the way the work felt to the author, not the way the decision
looks to the reader: process narration, identifiers up front, and no consequence.

```markdown
## Brief

Refactored the hook so that claude-approval-queue-reminder now matches gh pr create via PREFILTER and emits additionalContext.

In this PR I went ahead and updated the hook and the settings manifest and added tests, which should make things more robust going forward.
```
