---
name: spec-plan-review
description: >
  Use when a design spec or a pass plan is drafted and needs review before the owner approves
  it, in any repo on this workstation (dubplate, cairn-cms, the sites, dotfiles). Triggers include
  "review this spec", "plan review", "adversarial review of the plan", "fan out reviewers on the
  draft", and a plan-approval gate that has no review record yet. Do not use for a code diff
  (that is diff-reviewer) or for published docs pages (that is the docs page chain).
---

# Spec and plan review

A review finds the defects that would cost a build or an owner sitting, and the fold applies
them without over-engineering the document. The reviewers stay wide and the fold stays selective.
Reviewers asked to report only high-severity issues "may follow that instruction literally and
report less; ask it to report everything and filter in a separate pass instead" (Opus 5 prompting
page). Claude Code best practices name the opposite risk: "Chasing every finding leads to
over-engineering ... flag only gaps that affect correctness or the stated requirements."
(https://code.claude.com/docs/en/best-practices). The lenses report everything, ranked by
consequence, and the fold does the filtering.

No prose, register, or conformance review runs on a spec or plan; Vale and `tellgrader` cover
prose (Geoff, 2026-09-08). A spec or plan is written in whatever voice serves Claude Code best.

## The sequence

1. The lenses the depth below names run in parallel, each a fresh-context Opus agent at effort
   `medium`. Their names are contract and criteria, mechanics and feasibility, and data integrity
   and failure risk. The mechanics lens is the `plan-reviewer` agent.
2. One fold agent records a disposition per finding and revises the document.
3. A verification read checks the fold, and the fold agent applies its findings, only on an
   `auth-data` or `live-account` pass. Another read runs only when it finds a blocker.
4. A finding that changes the approved design returns to Geoff as one batched question. Every
   other finding is folded without him.

**Depth scales with risk.** A design of a page or less needs no separate spec. A plan gets the
mechanics lens and the fold only. A spec otherwise takes the three lenses and the fold, with no
verification read: the Opus 5 page says to remove "separate verification steps" and "do not use
subagents to verify or double-check your own work" (Prompting Claude Opus 5,
<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>).
The three lenses and the verification read are kept for `auth-data` and `live-account` passes
(risk classes: `pass-core`).

## The lenses

| Lens | Asks |
| --- | --- |
| Contract and criteria | Is every promise testable? Does each criterion name its fixture and the reason it would fail? Can any criterion pass vacuously? |
| Mechanics and feasibility | The `plan-reviewer` agent holds this lens prompt and the plan checklist. |
| Data integrity and failure risk | What happens on a crash, a concurrent process, a partial write, an upgrade, a restore? Can data be lost or silently corrupted? |

On a plan, the mechanics lens also checks the plan checklist in the `plan-reviewer` agent's body.

Dispatch the mechanics lens as the `plan-reviewer` agent; the dispatching session saves its reply
as `docs/superpowers/research/<date>-<target>-review-mechanics.md`. Every other reviewer dispatch
carries the target path and commit, the lens, and the same ask the agent holds: report every gap
found, ranked by consequence, each with a severity (blocker, major, minor), a tag (`correctness`
if it affects correctness or a stated requirement, `optional` otherwise), the location
(`file:line`), the defect, and a proposed fold. Over-ceremony counts as a finding, ranked by its
cost in clock time and tokens. A finding whose resolution is a product or priority choice is marked
**OWNER FORK**, with the options and a recommendation; a reviewer never rules a fork. Those
reviewers write only their output file,
`docs/superpowers/research/<date>-<target>-review-<lens>.md`.

## The fold

One fold agent (`claude-opus-5-5`) takes every review file. It loads
`superpowers:receiving-code-review`, verifies a finding before acting on it, and never agrees
performatively. It writes a fold record with one disposition per finding: folded (where the
revision carries it), refused (a one-line reason), or owner fork.

- The fold filters. It drops every `optional` finding, in the best-practices page's words: "flag
  only gaps that affect correctness or the stated requirements, and treat the rest as optional"
  (<https://code.claude.com/docs/en/best-practices>). It folds the `correctness` findings, and it
  may refuse a finding whose fix costs more than the risk it removes. Convergent findings from
  several lenses fold once, at the root.
- The fold probes every new mechanism it introduces: it quotes the docs or source, or runs a probe,
  and never states one from memory. The catch ledger found that 8 verification majors were
  mechanisms a fold stated from recollection.
- A finding whose fix is new machinery (a validator, a registry, a marker scheme) folds only when
  the record names a team or published source that runs it and a measured defect it answers
  (Geoff, 2026-09-28: "I want a proven and battle-tested system").
- It never rules an owner fork. It consolidates the forks into one numbered rulings section, each a
  yes-or-no question with a recommendation and what each answer builds. A question with one clearly
  correct answer is not a fork: the document takes it and records why (Geoff, 2026-09-25).
- When the revision silently changes a ratified document's meaning, the fold records an owed
  erratum and does not edit that document.

## The verification read

On an `auth-data` or `live-account` pass, a fresh agent (`claude-opus-5-5`) with no part in the
fold reads the revision against the fold record and the reviews. It asks whether each blocker and
major closed at the cited location,
whether the fold introduced a contradiction or an order that cannot build, whether any new
mechanism is quoted or proven, and whether Geoff can rule each fork on the evidence given. It
writes `<date>-<target>-fold-verification.md` in the finding shape above. The fold agent applies
its findings; minors go to the fold record as owed.

## Commits

The planning session commits each stage after its agents finish, path-limited, never `git add -A`.
Reviewers write only their own file and never commit.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Reviewer prompt filters severity up front | Ask it to report everything, ranked; the fold filters |
| Fold accepts every finding | Refusal is a valid disposition; cost against risk, one line |
| Fold picks an answer to an owner fork | It consolidates and recommends; Geoff rules |
| Mechanics lens or fold reasons from memory | Scratch module, probe, or a quoted doc line, cited |
| Running a verification read on an `ordinary` pass | Only `auth-data` and `live-account` passes take it |
| Full three-lens set on a plan | Mechanics lens and the fold; three lenses only on `auth-data` or `live-account` |
