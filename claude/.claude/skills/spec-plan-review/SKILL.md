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
5. **The owner sitting**, on the consolidated rulings section.

No prose, register, or conformance review runs on a spec or plan (Geoff, 2026-09-08: specs
are not register-graded). A spec or plan is written in whatever voice is most effective for
Claude Code; the published-docs standards govern public-facing writing only (Geoff,
2026-09-28).

**Review depth scales by pass class** (the table in `pass-core`). `auth-data`,
`engine-logic`, and any spec that introduces new mechanism take the full sequence. A `paint`,
`sweep`, or `docs` plan takes one lens that folds its own findings, with no separate fold
agent; the verification read runs only if that lens found a blocker. Four lenses is a hard
cap, never exceeded (one recent spec drew nine). Evidence: theme identity pass A produced about
3,400 lines of review and fold before any code, and none of its three lenses flagged the
over-ceremony an independent evaluation later found (the full engine gate on every CSS task,
4.4:1 test-to-source lines).

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
the drafter's pre-flight, not a lens. Every plan lens also checks proportionality and the four
planning-miss items:

- The declared pass class, and any per-task override, fits the change's real risk. A CSS task
  classed `auth-data` is a finding; so is a signing change classed `paint`.
- Each task's gate, review bar, test mandate, and settle steps match its class, and the plan
  justifies any deviation.
- Owner time sits where the acceptance criterion is. For `paint`, taste is the criterion, so
  the plan puts an owner glance mid-pass, not only at the end.

- Every library or stdlib behavior a task relies on is quoted from the docs or the source
  (`go doc`, a man page, the module cache), never recalled.
- Every state a check can meet (absent, empty, malformed, many bad) names the report it gives.
- Every privileged field names every channel that may set it.
- Every proof names the fixture state it needs (selected, populated), so the test cannot pass
  vacuously.

**Every reviewer dispatch carries these parts:**

- The target path and commit, and the lens.
- The Anthropic warning above, quoted with its source URL.
- The ask: correctness gaps ranked by consequence, and over-ceremony ranked by its cost in
  clock time and tokens ("full engine gate on nine CSS tasks, ~1.5 h, catches nothing the
  targeted gate misses"), not polish. Each finding carries a severity
  (blocker, major, minor), the location (`file:line`), the defect, and a proposed fold.
- Mark any finding whose resolution is a product or priority choice as **OWNER FORK**, with the
  options and a recommendation. A reviewer never rules a fork. A question with one clearly
  correct answer (a ratified standard, a conformance text, or a proven defect settles it) is
  not a fork: propose that answer as the fold.
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
  one line. A fold that refuses nothing across dozens of findings should say why. An
  over-ceremony finding is weighed by its cost; refusing one names what the extra ceremony
  catches.
- Fix convergent defects (several lenses reaching one root) at the root, not per finding.
- **A fold adds no invented mechanism (Geoff, 2026-09-28: "I want a proven and battle-tested
  system").** A finding whose fix is new machinery (a validator, a registry, a marker scheme, a
  planted-defect control) folds only when the fold record names a team or published source that
  runs that mechanism, and a measured defect, not a hypothetical one, that it answers. Otherwise
  refuse it or take the conventional fix.
- **Never rule an owner fork.** Consolidate every fork into one numbered rulings section in the
  document, each a yes-or-no question with a recommendation and what each answer builds.
- **Never make a ruling out of a settled question.** When one answer is clearly the
  architecturally correct one, the document takes it as its own decision and records why. The
  owner's rulings hold only genuine forks: product or taste choices, trade-offs with no dominant
  answer, and risks only the owner can accept (Geoff, 2026-09-25: "You don't need to ask
  questions for the sake of ceremony").
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
record as owed.

## Commits

The conductor commits each stage after its agents finish: the reviews, the fold (target plus
record), the verification, the second fold. Path-limited commits, never
`git add -A`, because a code lane may hold warm files in the same tree.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Reviewer prompt asks for "all issues" | Ask for correctness gaps ranked by consequence, and quote the warning |
| Fold accepts every finding | Refusal is a valid disposition; cost against risk, one line |
| Fold picks an answer to an owner fork | It consolidates and recommends; the owner rules |
| Mechanics lens reasons from memory | Scratch module, probe, or a quoted doc line, cited |
| Skipping the verification read because the fold "looks complete" | The fold is where new unquoted mechanisms appear |
| Reviewing only for missing rigor | Over-ceremony is a finding too, ranked by its cost |
| Full review set on a `paint`, `sweep`, or `docs` plan | One self-folding lens; depth follows the pass class |
| Reviewers commit into a shared tree | Only the conductor commits |
