---
name: spec-plan-review
description: >
  Use when a design spec or a pass plan is drafted and needs review before the owner approves
  it, in any repo on this workstation (dubplate, cairn-cms, the sites). Triggers include
  "review this spec", "plan review", "adversarial review of the plan", "fan out reviewers on
  the draft", and a plan-approval gate that has no review record yet. Do not use for a code
  diff (that is diff-reviewer) or for published docs pages (that is the docs page chain).
---

# Spec and plan review

A review exists to find the defects that would cost a build or an owner sitting, and to fold
them without over-engineering the document. Two forces pull against each other. Reviewers who
are asked for gaps always find some, and a fold that accepts every finding bloats the document
and buries the real fixes. This process keeps the reviewers wide and the fold selective.

Anthropic's Claude Code best practices (https://code.claude.com/docs/en/best-practices) state
the risk this process is built around:

> "A reviewer prompted to find gaps will usually report some, even when the work is sound,
> because that is what it was asked to do. Chasing every finding leads to over-engineering."

## The sequence

1. **Lenses, in parallel.** Each reviewer is a fresh-context agent with one lens.
2. **One fold.** A single agent records a disposition per finding and revises the document.
3. **One verification read.** A fresh agent checks the fold.
4. **A narrow second fold**, only when the verification read finds a blocker or a major.
5. **A prose review, last.**
6. **The owner sitting**, on the consolidated rulings section.

The conductor dispatches every step and commits every file. It reads the reports, never the
review files in full, unless a verdict hedges.

## Step 1: the lenses

**A spec gets four lenses:**

| Lens | Asks |
| --- | --- |
| Contract and criteria | Is every promise testable? Does each criterion name its fixture and the reason it would fail? Can any criterion pass vacuously? |
| Mechanics and feasibility | Does every mechanism behave as stated? Verify empirically (a scratch module, a probe run) or by quoting the docs or source. Never from memory. |
| Data integrity and failure risk | What happens on a crash, a concurrent process, a partial write, an upgrade, a restore? Can data be lost or silently corrupted? |
| Consistency | Does the draft contradict a ratified document (earlier specs, rulings ledgers, the repo's CLAUDE.md)? Spot-check its citations: does each cited line say what the draft claims? |

**A plan gets three lenses**, the disjoint set in the global CLAUDE.md: contract-and-criteria,
mechanics-and-feasibility, and domain-risk. Staleness (does the plan still match the tree) is
the drafter's pre-flight, not a lens. Every plan lens also checks the four planning-miss items:

- Every library or stdlib behavior a task relies on is quoted from the docs or the source
  (`go doc`, a man page, the module cache), never recalled.
- Every state a check can meet (absent, empty, malformed, many bad) names the report it gives.
- Every privileged field names every channel that may set it.
- Every proof names the fixture state it needs (selected, populated), so the test cannot pass
  vacuously.

**Every reviewer dispatch carries these parts:**

- The target path and commit, and the lens.
- The Anthropic warning above, quoted with its source URL.
- The ask: correctness gaps ranked by consequence, not polish. Each finding carries a severity
  (blocker, major, minor), the location (`file:line`), the defect, and a proposed fold.
- Mark any finding whose resolution is a product or priority choice as **OWNER FORK**, with the
  options and a recommendation. A reviewer never rules a fork.
- The output file: `docs/superpowers/research/<date>-<target>-review-<lens>.md` (or the repo's
  equivalent). The reviewer writes only that file.
- When a code lane shares the tree: write your own file only, never commit, never touch any
  other path.
- `model: "claude-opus-5-5"`, effort `high`.

## Step 2: the fold

One fold agent (`claude-opus-5-5`, effort `high`) takes every review file. Its dispatch says:

- Load `superpowers:receiving-code-review` first. Verify a finding before acting on it; do not
  agree performatively.
- Write a fold record with **one disposition per finding**: folded (where the revision carries
  it), refused (a one-line reason), or owner fork (the numbered ruling it became). Duplicate
  findings across lenses fold once and list every ID.
- **A fold may refuse** a finding whose fix costs more than the risk it removes. The reason is
  one line. A fold that refuses nothing across dozens of findings should say why.
- Fix convergent defects (several lenses reaching one root) at the root, not per finding.
- **Never rule an owner fork.** Consolidate every fork into one numbered rulings section in the
  document, each a yes-or-no question with a recommendation and what each answer builds.
- When the revision silently changes a ratified document's meaning, record it as an owed
  erratum in the fold record. The fold does not edit the ratified document.
- Write only the target and the fold record. Never commit when a code lane shares the tree.

## Step 3: the verification read

A fresh agent (`claude-opus-5-5`, effort `high`) with no part in the fold reads the revision
against the fold record and the reviews. Its questions:

- Did each blocker and major actually close, at the cited location?
- Did the fold introduce a contradiction between sections, or a pass order that cannot build?
- Did the fold state a new mechanism from memory? Every new mechanism must be quoted or proven.
- Can the owner rule each fork on the evidence given?

It writes `<date>-<target>-fold-verification.md` with the same finding shape. On a blocker or
major, dispatch **one narrow second fold** limited to those findings. Minors go to the fold
record as owed, or to the prose review if they are wording.

## Step 4: the prose review

Dispatch `prose-voice-reviewer` last, once per revision. Ask it to check invented or misquoted
specifics and cross-section contradictions before style. The agent is read-only and returns the
file content in its report, so the conductor saves it to
`<date>-<target>-prose-review.md` and folds it (or dispatches a small fold).

## Commits

The conductor commits each stage after its agents finish: the reviews, the fold (target plus
record), the verification, the second fold, the prose review. Path-limited commits, never
`git add -A`, because a code lane may hold warm files in the same tree.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Reviewer prompt asks for "all issues" | Ask for correctness gaps ranked by consequence, and quote the warning |
| Fold accepts every finding | Refusal is a valid disposition; cost against risk, one line |
| Fold picks an answer to an owner fork | It consolidates and recommends; the owner rules |
| Mechanics lens reasons from memory | Scratch module, probe, or a quoted doc line, cited |
| Skipping the verification read because the fold "looks complete" | The fold is where new unquoted mechanisms appear |
| Prose review run first | Facts settle before style, so prose runs last |
| Reviewers commit into a shared tree | Only the conductor commits |
