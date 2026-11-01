---
name: engine-consult
description: Use when authoring a pass plan in ecxc-ski, 907-life, aksailingclub-org, cairn-pub, or any other repo whose pass builds against the cairn engine; when a pass starts on a committed plan whose header carries no consultation line; or whenever the work involves a "consultation", an "engine ask", or a request to "consult the engine" before building against a cairn surface.
---

# Engine consultation

The pre-pass exchange between a cairn-consuming site and the engine. The site files what
its pass will press on the engine before the pass builds, the `engine-triage` agent argues
each item against the standard, and accepted work lands ahead of the site task that
needs it. It replaces reactive harvesting, in which a site hand-rolled around an engine
gap and filed a staging doc, and the engine absorbed the finding only after the workaround
had shipped, so the site paid for the workaround and the engine paid again to replace it.

## When it fires (both hooks)

**Authoring-time enumeration.** The engine-contact enumeration runs whenever a site pass's
plan is authored, immediately before the plan is written, in whichever session authors it. For each thing the pass will build, the author
asks whether it presses an engine edge (admin surface, engine CSS, an exported component's
contract, auth, any seam). Exactly two outcomes: a consultation brief, or a recorded
one-line "no engine asks" in the plan header. The null outcome is deliberately cheap.

The plan header carries exactly one of the two engine-consultation lines, plus the
sources-consulted line, so the backstop can match on it:

```markdown
**Engine consultation:** no engine asks.
**Engine consultation:** [<brief filename>](<link to the filed brief>)
**Sources consulted:** <exports and skill references read, or "none">
```

Before the plan is written, the author's pre-plan read names the exports and skill references the
pass builds on (the doc comments under `~/Projects/cairn-cms/src/lib` and the packaged `skills/`, with the code at the commit), and the open engine items in
`~/Projects/cairn-cms/BACKLOG.md`, so a hole the last site could not
close reaches this plan. The plan header's `**Sources consulted:**` line records that read: the
exports and references it covered and the open engine items it found (or "none" for either).

**Pass-start backstop, for the resumed path.** After reading the plan and before the first
implementer dispatch: if the plan header carries neither a consultation-brief link nor the
"no engine asks" line, the enumeration runs now and the line is appended to the committed
plan. The check is a blocking precondition on the first dispatch.

## Repos bound

Any repo whose pass builds against the engine: the three sites (ecxc-ski, 907-life,
aksailingclub-org), cairn-pub, and future consumers, wherever the plan is
authored.

## The brief

One document per consulting pass, filed engine-side at
`~/Projects/cairn-cms/docs/internal/consultations/YYYY-MM-DD-<site>-<pass>.md` (the site
plan links to it; the brief and the engine's verdicts are one document). Per item, four
fields:

```markdown
### <item slug>

1. **What the pass builds:** <the site feature, one paragraph>
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

Dispatch a fresh read-only subagent pinned to `claude-opus-5-5` whose instructions are the body of
`~/Projects/cairn-cms/.claude/agents/engine-triage.md` (a session in a site repo does not load that
repo agent by name), with the absolute paths to the brief, the rulings ledger
(`~/Projects/cairn-cms/docs/internal/engine-rulings.md`), and the site plan. It reads the
ledger first, so a settled ruling is cited rather than re-argued, then argues each item
against the standard. The planning session adjudicates its verdicts, records them in the brief
document itself, and appends one ledger entry per ruled item, copying the entry format
from the fenced template in the ledger's own header rather than reconstructing it (two of
its fields are conditional, audit-tier ones consultation entries usually omit).

## The three verdicts

- **Accept**: with shape notes (the any-site form, re-derived) and a sequencing call (mini
  pass now, or queued engine pass with the fallback sanctioned interim and a retirement
  trigger). An accept's ledger entry stays open until the consuming site task lands; the
  consuming pass closes it with a one-line seam-fit report (fit as designed, or the
  friction found), so a seam landed ahead of its consumer is never left unproven.
- **Decline**: with a recorded reason, into the ledger. The site's declared fallback is
  thereby sanctioned as the proper end state, not debt.
- **Defer**: names the evidence that would reopen it (usually a second consumer) and
  records that trigger.

## Sequencing accepted work

Accepted work sized at a task or two and additive runs as a mini engine pass now, from
the same site session (checklist below). Anything that breaks public surface or adds a
subsystem queues as its own cairn-cms-launched pass; the site's fallback is sanctioned
interim state with a recorded retirement trigger. The size threshold and the session
threshold are the same line.

## Cross-repo mini-pass checklist

A site-launched session does not auto-load cairn's context. In order:

1. **One-executor check** before touching cairn: `pgrep -f` on the worktree path, a
   `git status` check for warm uncommitted changes you did not author, and a read of
   `~/Projects/cairn-cms/docs/STATUS.md` for a claim on the work.
2. **Fresh worktree off cairn `main`**, and register it in cairn `docs/STATUS.md`'s
   active-worktree list before the first commit, so a second session's STATUS read sees
   the claim.
3. **Read `~/Projects/cairn-cms/docs/STATUS.md`** and honor the changelog
   `Consumers must:` convention for any consumer-facing change.
4. **The lean pass loop** per `cairn-pass`: one executing session, pair subagents where files are
   disjoint, the fast lane per task, and the whole-branch close review.
5. **Run the full gate list by name**: cairn-cms's `npm run check:close` runs it, including
   `check:comments`, `check:tiers`, `check:surface`, `check:snippets`,
   `check:transcripts`, and `check:symbols`, which the local ritual once skipped.
6. **The ordered close:** engine merge to `main`, then read and follow
   `~/Projects/cairn-cms/.claude/skills/cairn-releasing/SKILL.md` (the change must be on the registry; a site branch cannot merge on a `file:`
   pin), then `npm run link:consumer -- <site-dir> --restore` from the cairn checkout,
   then the site merge. During development the site consumes via
   `npm run link:consumer -- <site-dir>`.

## The reactive-harvest fallback

Consultation cannot foresee what a pass discovers while building. Mid-pass discoveries
still file, using the same four-field item schema, and their later triage runs through
the same `engine-triage` agent against the same ledger. The paste-then-delete staging
mechanics stay as they are.

## First run

If the rulings ledger carries no protocol post-mortem entry, the first live consultation
appends a short one; the consultation that appends it then deletes this section from this
skill.
