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

## The packet contract

The command `approval-queue packet <initiative> <file>` refuses a packet that breaks the contract,
exits 2, and names the defect with this register's path. The parser is
`~/Projects/approval-queue/approval-queue/src/lib/packet.ts`. The skeleton below shows every part.

- `# <title>` is a heading of at most 80 characters with no closing punctuation. The
  description follows it: a background paragraph, then one or two summary paragraphs, so two or
  three paragraphs in all.
- The sections come in this order: `## What changed` (a revision only), `## If you approve`,
  `## Not checked`, then zero to three `## Ask: <question>`, then an optional `## Routine`. No
  other `##` heading is allowed outside a code fence. A packet has no `## Background` section; its
  background is the description's first paragraph.
- A packet is a revision when it resends a PR or design that Geoff sent back. The command reads the
  decision log, marks the packet as "Revision N", and refuses it without `## What changed`. It
  refuses the section on a packet that revises nothing. The section is a bulleted list of at least
  one bullet and nothing else. Each bullet answers one call Geoff made on the earlier packet (a
  verdict he set to send back, or an ask he answered) or one point of his note, and says what
  the session did about it. The page shows his earlier note above the bullets, so a bullet does
  not repeat it.
- A plan step is `N. [session] <text>` (the session runs it and can revert it),
  `[irreversible]` (it cannot be undone), or `[you: <label>]` (Geoff runs it; the label is the
  "You'll need to" line on the page).
- An ask carries `Rule`, `Part`, `Recommended`, `Reason`, and `Summary` lines, then a `Background:`
  paragraph, a `Facts:` sentence with bullets each ending in a source in backticks inside
  parentheses, and `Choices:` of at least two, each `- <label>: <consequence>`. The label holds
  no colon. `Evidence:` with a fenced excerpt is optional.
- `Rule` is one of seven: `irreversible`, `public-surface`, `cross-repo`, `owner-call`,
  `low-confidence`, `gate-failed`, `contradicts-ruling`. A PR with a failing check or a `fix` or
  `escalate` review verdict needs a `gate-failed` ask, and a PR whose body has `## Before merge`
  needs an ask naming it.
- `Part` is a canonical ref or `none`. A PR is `<owner>/<repo>#<n>`, a design is
  `<owner>/<repo>:<path>`, and a step is `step:<n>`. Each part appears once, in one ask or one
  routine row. When `Part` names a part, every choice ends in a verdict tag in brackets:
  `[approve]`, `[hold]`, or `[send-back]` for a PR or design, and `[session]`, `[you]`, or `[skip]`
  for a step. When `Part: none`, no choice has a tag.
- `## Routine` is one table with the header `| Part | Verdict | Fact | Why |`. A PR or design
  takes `approve`, `hold`, or `send-back`; a step takes `session`, `you`, or `skip`. The fact is
  the one that changes the verdict.
- A packet holds at least one PR or design.

Because an ask can hold a three-backtick Evidence fence, a packet exemplar sits in a four-backtick
fence below.

### The packet skeleton

The angle-bracket text is a slot.

````markdown
# <A title that names what is being decided>

<The background: the initiative, where this packet sits, what came before, why it is here now,
and a plain meaning for any term a reader would not know.>

<The summary: what is proposed, what each part changes, what approving does, and the shape of the
plan, with any open question and its recommendation.>

<An optional second summary paragraph, when the first runs long.>

## What changed
- <A revision only: what the session did about one call or point of the note.>

## If you approve
1. [session] <A step the session runs that can be reverted.>
2. [irreversible] <A step that cannot be undone.>
3. [you: <label>] <A step you run yourself.>

## Not checked
<What was not verified. Never a fact an ask depends on.>

## Ask: <the question>
Rule: <one of the seven>
Part: <a part ref, or none>
Recommended: <the number of the recommended choice>
Reason: <why, grounded in the facts>
Summary: <one or two sentences carrying the background and the deciding fact>

Background: <one paragraph defining every term and why the question exists>

Facts: <one sentence stating the key fact>
- <a fact> (`<its source>`)

Choices:
- <label>: <what happens, and whether it can be undone> [approve]
- <label>: <what happens> [hold]

Evidence: <one sentence stating what the excerpt shows>
```text
<a short excerpt>
```

## Routine
| Part | Verdict | Fact | Why |
|---|---|---|---|
| <owner>/<repo>#<n> | approve | <the verdict-changing fact> | <one line> |
````

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
exactly. The four packet exemplars show a packet with two asks, a routine-only packet, a
packet with a `gate-failed` ask, and a revision. A block
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

### A packet with two asks (scribe link checker)

The title names the thing, and the two summary paragraphs carry the decision: what ships, what
cannot be undone, the weak spot, and both open questions with the recommendation. The first ask
is bound to a PR and tagged, and the second is a call with no part. Each ask's `Summary:` carries
the deciding fact, so the closed card decides.

````packet
# Scribe link checker and version 0.3.0

The scribe initiative gives the docs writer a tool that checks a page before a person reads it. This packet carries the link checker, the third of four stages. A package registry keeps every published version for good, so a release can be replaced but never removed.

The link checker reads every link on a docs page and reports each one that no longer resolves. It ships in two PRs: PR 51 adds the checker and publishes version 0.3.0, and PR 52 adds its changelog entry. Every check passes and the review verdict is accept. The checker has run only on the sample pages, where it found eleven broken links.

Approving merges both PRs in order, and the merge of PR 51 publishes 0.3.0, which cannot be undone. Before it goes out, you choose whether a broken link warns or fails the build. The session recommends a warning first, so authors can clear the old links.

## If you approve
1. [session] Merge glw907/scribe#51, then glw907/scribe#52.
2. [irreversible] Publishing version 0.3.0 to the package registry runs when #51 merges.
3. [you: confirm the registry login] Check the version page once the publish ends.

## Not checked
The checker was run on the sample pages only, not on the full docs set.

## Ask: Publish version 0.3.0 with the link checker on?
Rule: irreversible
Part: glw907/scribe#51
Recommended: 1
Reason: All checks pass and the review verdict is accept, and the package version is new.
Summary: PR 51 publishes 0.3.0 to the registry, and a published version cannot be taken back. Every check passes.

Background: The registry refuses a second upload of the same version number. A mistake in 0.3.0 would need a 0.3.1 to correct it.

Facts: The version number is unused and the checks are green.
- Version 0.3.0 is not in the registry list (`docs/releases.md`)
- All four checks pass (`glw907/scribe#51`)

Choices:
- Publish: merges the PR and publishes 0.3.0; a later release can replace it but never remove it [approve]
- Wait: leaves the PR open with nothing published [hold]
- Send back: returns the PR to the session to change and send again [send-back]

## Ask: Should the link checker fail the build by default?
Rule: owner-call
Part: none
Recommended: 2
Reason: Docs authors have not seen the checker yet, so a warning gives them time to fix old links.
Summary: The checker can warn or fail the build on a broken link. Warning first lets authors fix the backlog of old links.

Background: A failing build blocks every docs change until the broken link is fixed. A warning prints the link and lets the change through.

Facts: The sample run found eleven broken links.
- The sample run printed eleven broken links (`docs/link-check-sample.txt`)

Choices:
- Fail the build: a broken link blocks the change until it is fixed
- Warn only: a broken link prints and the change goes through

## Routine
| Part | Verdict | Fact | Why |
|---|---|---|---|
| glw907/scribe#52 | approve | The change is a changelog entry and the checks pass. | Nothing in it needs a call. |
| step:1 | session | A merge can be reverted. | The order is fixed by the plan. |
````

### A routine-only packet (scribe docs fixes)

When the facts settle every part, the packet has no ask. The change is simple, so one short
summary paragraph is enough, and the reader approves from the description and the table.

````packet
# Scribe guide corrections

The scribe initiative keeps its guide current as the tool grows. This packet carries small corrections found while the link checker was built. A changelog is the list of changes a release made.

PR 53 fixes a three-word typo in the guide, and PR 54 adds a missing changelog line for the last release. Both change text only and every check passes. Approving merges them, and nothing about how scribe runs changes.

## If you approve
1. [session] Merge glw907/scribe#53, then glw907/scribe#54.

## Not checked
The guide was not rebuilt on the live site; the build runs after the merge.

## Routine
| Part | Verdict | Fact | Why |
|---|---|---|---|
| glw907/scribe#53 | approve | The diff changes three words in the guide and the checks pass. | A typo fix. |
| glw907/scribe#54 | approve | The diff adds one changelog line and the checks pass. | The line matches the merged release. |
| step:1 | session | A merge can be reverted. | The order does not matter. |
````

### A packet with a gate-failed ask (scribe note template)

A failing check is always an ask, and it names the PR. The evidence excerpt shows the failure
itself, so the reader need not open the log.

````packet
# Scribe note template

The scribe initiative replaces hand-written release notes with generated ones. This packet carries the template the notes are built from. A gate is the set of checks and the review a PR must pass.

PR 61 adds the template and the notes file it generates, and PR 62 adds the template's tests. PR 62 passes its gate. PR 61 fails one lint check, on a long line in the generated file. The repo's style policy exempts generated files, but the check's config predates the policy.

Approving merges both PRs in order. Merging PR 61 with the check red is your call, and the session recommends it because the failure sits only in the exempt file. A revert PR undoes either merge.

## If you approve
1. [session] Merge glw907/scribe#61, then glw907/scribe#62.

## Not checked
The generated notes were not read on the live project page.

## Ask: Merge the note template with its lint check red?
Rule: gate-failed
Part: glw907/scribe#61
Recommended: 1
Reason: The only failure is in a generated file that the repo exempts from the style rule.
Summary: PR 61 fails one lint check, and the failure is in a generated file. The repo waives that rule for generated files.

Background: A lint check scans files for style rules. The repo's policy exempts generated files, but the check's config predates the policy and still scans them.

Facts: The one error is in a generated file.
- The lint check reports one error, in `notes.generated.ts` (`glw907/scribe#61`)
- The style policy exempts generated files (`docs/style.md`)

Choices:
- Merge anyway: merges the PR with the lint check red; a revert PR undoes it [approve]
- Hold: leaves the PR open with nothing done [hold]
- Send back: returns the PR to the session to fix the check and send again [send-back]

Evidence: The lint output names the generated file only.
```text
notes.generated.ts:12:1  error  line too long (max-len)
```

## Routine
| Part | Verdict | Fact | Why |
|---|---|---|---|
| glw907/scribe#62 | approve | All checks pass and the review verdict is accept. | Nothing in it needs a call. |
| step:1 | session | A merge can be reverted. | The order is fixed by the plan. |
````

### A revision (scribe note template, resent)

A packet that resends a part Geoff sent back carries `## What changed`. Each bullet answers one
call or one point of his note, in the order he made them. The page puts his note above the
bullets, so the bullets say what the session did and never quote him.

````packet
# Scribe note template, revised

The scribe initiative replaces hand-written release notes with generated ones. You sent the first packet back on PR 61, which adds the note template. You sent it back because the lint check still scanned the generated file, and you asked for the check's config to change instead of merging past the red.

The session fixed the check, so PR 61 now passes its gate and the revised packet has no ask. PR 62, which adds the template's tests, gains a test of the skip and passes. Approving merges both PRs in order, and a revert PR undoes either merge.

## What changed
- You set PR 61 to send back: the lint config now skips generated files, so the check passes.
- You asked for a test of the skip: PR 62 gains a case that lints a generated file and expects no error.

## If you approve
1. [session] Merge glw907/scribe#61, then glw907/scribe#62.

## Not checked
The generated notes were not read on the live project page.

## Routine
| Part | Verdict | Fact | Why |
|---|---|---|---|
| glw907/scribe#61 | approve | The lint check passes after the config change. | The failure you sent it back for is gone. |
| glw907/scribe#62 | approve | All checks pass and the new test covers the skip. | Nothing in it needs a call. |
| step:1 | session | A merge can be reverted. | The order is fixed by the plan. |
````

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
