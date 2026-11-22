---
name: engine-consult
description: Runs the consultation between a cairn-consuming site and the cairn engine before the site builds against an engine surface. Use when writing a spec in ecxc-ski, 907-life, aksailingclub-org, cairn-pub, or another repo that builds against the cairn engine; when a task starts on a spec that fails the consultation check; or when the work involves a "consultation", an "engine ask", or a request to "consult the engine".
---

# Engine consultation

The exchange between a cairn-consuming site and the engine, before the site's spec is built.
The site files what its work will press on the engine, the `engine-triage` agent argues each
item against the standard, and accepted work lands ahead of the site task that needs it.
Specs and tasks follow `building-from-specs`.

## When it fires (both hooks)

**Spec-time enumeration.** The engine-contact enumeration runs whenever a site's spec is
written, immediately before the spec is written, in whichever session writes it. For each thing
the spec will build, the author asks whether it presses an engine edge (admin surface, engine
CSS, an exported component's contract, auth, any seam). Exactly two outcomes: a consultation
brief, or a recorded one-line "no engine asks" in the spec header. The null outcome is
deliberately cheap.

The spec header carries exactly one of the two engine-consultation lines, plus the
sources-consulted line, so the check can match on it:

```markdown
**Engine consultation:** no engine asks.
**Engine consultation:** [<brief filename>](<link to the filed brief>)
**Sources consulted:** <exports and skill references read, or "none">
```

Before the spec is written, the author's read names the exports and skill references the
spec builds on (the doc comments under `~/Projects/cairn-cms/src/lib` and the packaged `skills/`, with the code at the commit), and the open engine items in
`~/Projects/cairn-cms/BACKLOG.md`, so a hole the last site could not
close reaches this spec. The spec header's `**Sources consulted:**` line records that read: the
exports and references it covered and the open engine items it found (or "none" for either).

**The consultation check.** The spec author runs it before the spec goes to Geoff, and lists
it among the done items of the spec's first task, so the task session and its reviewer run it
again. Done item: `grep -c -E '^\*\*(Engine consultation|Sources consulted):\*\* ' <spec>` prints 2.

**Task-start backstop.** A task session whose spec fails the check runs the enumeration
before its first build step, and records the line it would add under its pull request's
`## Decisions`. When the enumeration finds an engine ask, the task session takes the author's
place: it files the brief, runs the triage, and builds on the verdicts without waiting for Geoff.

## Repos bound

Any repo whose work builds against the engine: the three sites (ecxc-ski, 907-life,
aksailingclub-org), cairn-pub, and future consumers, wherever the spec is
written.

## The brief

One document per consulting spec, filed engine-side at
`~/Projects/cairn-cms/docs/internal/consultations/YYYY-MM-DD-<site>-<spec>.md` (the site
spec links to it; the brief and the engine's verdicts are one document). Per item, four
fields:

```markdown
### <item slug>

1. **What the site builds:** <the site feature, one paragraph>
2. **The engine edge it presses:** <surface, `file:line` where known>
3. **Evidence for the any-site case:** <recurrence, measurements, prior instances>
4. **The site's fallback if declined:** <the hand-roll, with its rough size>
```

Field 4 prices the decline for the triage, and on a decline it becomes the sanctioned end
state. When an item disputes a documented fact, the brief cites the page or the `file:line` it
disputes.

## The standard

The codified standard lives once, in the `engine-triage` agent definition
(`.claude/agents/engine-triage.md` in the cairn-cms checkout, "The standard" section). Read it before filing a brief, so
each item is written against the gate it will meet.

## Triage mechanics

Dispatch a fresh read-only Opus subagent whose instructions are the body of
`~/Projects/cairn-cms/.claude/agents/engine-triage.md` (a session in a site repo does not load that
repo agent by name), with the absolute paths to the brief, the rulings ledger
(`~/Projects/cairn-cms/docs/internal/engine-rulings.md`), and the site spec. It reads the
ledger first, so a settled ruling is cited rather than re-argued, then argues each item
against the standard. The session writing the spec adjudicates its verdicts, records them in the brief
document itself, and appends one ledger entry per ruled item, copying the entry format
from the fenced template in the ledger's own header rather than reconstructing it (two of
its fields are conditional, audit-tier ones consultation entries usually omit).

## The three verdicts

- **Accept**: with shape notes (the any-site form, re-derived) and a sequencing call (a small
  engine task now, or a queued engine spec with the fallback sanctioned interim and a retirement
  trigger). An accept's ledger entry stays open until the consuming site task lands; the
  consuming task closes it with a one-line seam-fit report (fit as designed, or the
  backlog items found), so a seam landed ahead of its consumer is never left unproven.
- **Decline**: with a recorded reason, into the ledger. The site's declared fallback is
  thereby sanctioned as the proper end state, not debt.
- **Defer**: names the evidence that would reopen it (usually a second consumer) and
  records that trigger.

## Sequencing accepted work

Accepted work sized at a step or two and additive runs as a small engine task now, from
the same site session (checklist below). Anything that breaks public surface or adds a
subsystem queues as its own cairn-cms spec; the site's fallback is sanctioned
interim state with a recorded retirement trigger. The size threshold and the session
threshold are the same line.

## Cross-repo engine task checklist

A site-launched session does not auto-load cairn's context. In order:

1. **One-session check** before touching cairn: `claude-worktree-busy <worktree path>`, then a
   read of `~/Projects/cairn-cms/docs/STATUS.md` for a claim on the work.
2. **Fresh worktree off cairn `main`**, and register it in cairn `docs/STATUS.md`'s
   active-worktree list before the first commit, so a second session's STATUS read sees
   the claim.
3. **Read `~/Projects/cairn-cms/docs/STATUS.md`** and honor the changelog
   `Consumers must:` convention for any consumer-facing change.
4. **Build by `building-from-specs`**, with `cairn-pass` for the gate and checklists: one
   session, the fast lane per step, and the whole-branch review.
5. **Run the full gate list by name**: cairn-cms's `npm run check:close` runs it, including
   `check:comments`, `check:tiers`, `check:surface`, `check:snippets`,
   `check:transcripts`, and `check:symbols`.
6. **The ordered close:** engine merge to `main`, then read and follow
   `~/Projects/cairn-cms/.claude/skills/cairn-releasing/SKILL.md` (the change must be on the registry; a site branch cannot merge on a `file:`
   pin), then `npm run link:consumer -- <site-dir> --restore` from the cairn checkout,
   then the site merge. During development the site consumes via
   `npm run link:consumer -- <site-dir>`.

## The reactive-harvest fallback

Consultation cannot foresee what a task discovers while building. File each discovery made
mid-task with the same four-field item schema. Its later triage runs through the same
`engine-triage` agent against the same ledger.
