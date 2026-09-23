---
name: site-pass
description: >
  Invoke at the start or end of a development pass on one of the SvelteKit
  site repos (ecxc-ski, 907-life, …). Covers pass-start (read STATUS,
  read plan, dispatch Sonnet implementers per task) and pass-end consolidation
  (code-simplifier, quality gate, reviewer fan-out, architecture + STATUS
  update, plan archival, commit + push, then roll into the next pass).
  Trigger on "continue development", "next pass", "finish pass", "ship pass",
  or explicit invocation, when the work is the site's own roadmap.
  For the cross-repo cairn-cms library initiative use `cairn-pass` instead; it
  tracks the cairn-cms repo's own `docs/STATUS.md`, not this repo's STATUS.md.
---

# Site Pass

Each site repo develops in numbered passes. A pass has a starter prompt in
this repo's `docs/STATUS.md`, a plan under `docs/superpowers/plans/`, and
(usually) a spec under `docs/superpowers/specs/`. This skill encodes the
ritual at both ends. It is site-agnostic; all paths are relative to the
repo you're working in.

Plan and execution share the session. The starter prompt and the committed
plan are crash insurance, not a handoff; do not run the
`superpowers:writing-plans` "which execution method?" question, and do not
recommend a context clear except after a long, noisy brainstorm (in that
case give the exact resume prompt and the launch directory).

> **Which skill?** This skill is for a *site's own* roadmap. If the user
> means the **cairn-cms** library initiative, stop and use **`cairn-pass`**.
> That work is tracked in the cairn-cms repo's own `docs/STATUS.md` and the
> functional spec, not this repo's STATUS.md.

## Starting a pass

Three things are true before the first implementer dispatch:

- You hold the pass number and starter prompt (from `docs/STATUS.md`) and
  the pass plan. If no plan exists and the starter prompt lists open
  questions, brainstorm first (`superpowers:brainstorming`), then write the
  plan at `docs/superpowers/plans/YYYY-MM-DD-<topic>.md` from
  `plan-template.md`. The brainstorm probes until the plan carries no open
  readings; its length is never a cost to trim (Geoff, 2026-09-04).
- The plan header carries a token ceiling, a checkpoint interval (default
  four tasks), and exactly one of a consultation-brief link or the line
  "no engine asks", produced by the `engine-consult` skill. If it carries
  neither, run the engine-contact enumeration per `engine-consult` now and
  append the resulting line to the committed plan. This is blocking: no
  `site-implementer` dispatch until the header carries one of the two.
- The plan is committed and STATUS.md's starter prompt points at it.

Constraints while executing, in this session regardless of model:

- Each task runs as the chain. `site-implementer` (Sonnet) makes the
  failing check green, clears the repo gate, and returns files touched,
  the gate result, and anything it could not do. `diff-reviewer`
  (`claude-opus-5`) reads the diff against the task's acceptance criteria
  and returns accept, fix, or escalate with `file:line` findings; the
  conductor does not read the diff. One re-dispatch on `fix`; a second
  `fix` is the conductor's decision.
- Below six tasks, dispatch the chain per task with the Agent tool. At six
  or more, or when the plan marks tasks independent, run
  `~/.claude/workflows/pass-execute.js` with `{repo: "<site repo>", gate:
  "<repo's full gate command>", implementer: "site-implementer", tasks:
  [{id, title, criteria, files, notes}]}`.
- Implement a task inline, or upshift a dispatch to `model: opus`, only
  for novel correctness-critical logic the plan does not fully specify;
  `model: fable` only when Opus 5.5 at `xhigh` still falls short on something
  that matters.
- At each checkpoint, at any split, and before any question to the user,
  write STATUS.md (task ledger, decisions taken, spend, next task), then
  continue.

## Ending a pass: the consolidation ritual

Every pass ends here. No pass is done until every step has run.

### 1. Simplify

Dispatch the code-simplifier agent over the code changed this pass. Use the
`Agent` tool's `subagent_type` = **`code-simplifier:code-simplifier`** (the
plugin-namespaced name; the bare `code-simplifier` is not a valid agent type
and will error). Docs-only passes skip this.

### 2. Quality gate

Run the repo's full gate: `npm run check` (svelte-check, 0 errors and 0
warnings), the test suite if the repo has one (`npm test` must **exit 0**,
not just show green assertions), and `npm run build`. Fix every failure
before continuing. Docs-only passes skip this.

### 3. Review gate

Fan out the relevant review subagents in parallel and fold their findings
in before committing. Match the subagent to what the pass touched:
`svelte-reviewer` (any `.svelte` or load/action change),
`daisyui-a11y-reviewer` (components, markup, styles, theme config),
`cloudflare-workers-reviewer` (Worker code, D1, wrangler config),
`web-auth-security-reviewer` (always for auth, session, cookie, or token
changes). For website content the `content-review` skill is the reviewer.
At the review gate of a large pass, suggest a Workflow find-and-verify
sweep instead of the flat fan-out and let the user opt in. Skip for small
or docs-only passes.

### 4. Update docs/architecture.md

Add any design decisions made this pass that belong in the long-term record.
Keep it factual: decisions, not narration.

Also keep the site's own docs current for whatever the pass changed (a README
note, a config comment, or an architecture entry). The cairn-cms library carries
the full docs-as-a-pass-dimension rule; for a site this is the light version.

### 5. Update the three ledgers

STATUS is read in full at the start of every session, so anything parked there is a
context cost paid on every session forever. The three files split by read frequency, and
the pass close writes to all three rather than piling everything into STATUS.

**`docs/STATUS.md`** — current state, what exists, the next action, pass-scoped carried
items. Nothing else.

- Mark the current pass `done` in the pass table.
- Write the next starter prompt (see format below).
- **STATUS.md must stay ≤60 lines.** This cap has always been here and every repo blew
  past it (ecxc-ski 173, 907-life 236, cairn-cms 540) because "prune" had no destination.
  It does now: history goes to `docs/HISTORY.md`, standard-setting work to `ROADMAP.md`.
  Pruning means moving, never deleting.

**`docs/HISTORY.md`** — the per-pass ledger, read on demand at a post-mortem or a "when
did this change" question, never at session start. Create it if absent.

- Add this pass's entry, newest first: what landed, what the review gate caught, and
  anything a later pass would be wrong to rediscover from scratch. That last part is what
  makes the file worth keeping rather than a changelog nobody opens.
- STATUS gets NO pass entries. If a `## History` or `## Passes` section is still sitting
  in STATUS, move it here as part of this pass's close.

**`ROADMAP.md`** — strategic initiatives, meaning work spanning passes or setting a
standard other work is measured against. Managed by `/log-project`; `Active` / `Planned` /
`Someday`.

- A carried item that is really an initiative belongs here, not in STATUS's carried list.
  The test: does it set a standard other work is measured against, or span several passes?

### 6. Archive plan + spec

```bash
git mv docs/superpowers/plans/<this-pass>.md docs/superpowers/archive/plans/
# if a spec exists:
git mv docs/superpowers/specs/<this-pass>-design.md docs/superpowers/archive/specs/
```

### 7. Commit and push

Stage the pass's files explicitly (never `git add -A`), then:

```bash
git add <files changed this pass>
git commit -m "Pass <n>: <summary>

Co-Authored-By: Claude <noreply@anthropic.com>"
git push
```

Also refresh the project memory if the initiative's state changed; a cold
session should recall where the roadmap stands from STATUS.md and memory
alone.

### 8. Prep the context clear, then roll into the next pass

**A finished pass always ends by prepping to clear context (Geoff,
2026-08-01). It is a ritual step, not something to offer when the session
felt long.** A pass is an initiative boundary, and every turn of a
continued session re-buys the whole cached conversation, so carrying one
past its pass charges the next pass for context it does not need. The
prep is the same work either way: the artifacts are crash insurance
mid-session and the entire handoff across one.

Prepping means STATUS.md names the next pass, the durable artifacts are
committed and pushed, the tree is clean, and the user's last read is the
exact resume prompt plus the launch directory. The test before declaring
done: **a session starting cold from that prompt reaches the same next
action under the same constraints, having read only the plan, STATUS, and
memory.** Walk the pass's own decisions against it, including ones the
user changed mid-pass and anything about branch topology (a deferred
merge changes where the next pass branches from, and a cold session
branches off the default).

With that done, continuing in the same session is fine for work within
one pass, and if the next starter prompt has open questions, run the
brainstorm while context is warm. A plan drafted here gets the
engine-contact enumeration per the `engine-consult` skill before it is
written, the same as any plan, and carries the consultation line in its
header. Stop when the user wants to stop or the
next pass's direction is unsettled. See the
`cairn-pass-ends-with-context-clear-prep` memory.

## Execution discipline

- **One implementer per dispatch, verified.** Wait for each
  `site-implementer` result and verify its commit (git log and status)
  before depending on it. On an API overload or 5xx, wait and retry once
  deliberately; never fire a second dispatch while one may still be in
  flight.
- **Suggest the Workflow tool at the right moments.** It runs only on the
  user's explicit opt-in ("use a workflow"), so name the moment it would
  pay off (mostly independent tasks, a large review gate, a site-wide
  audit or migration) in one sentence with the shape and rough scale.

## Starter-prompt format

```markdown
### Next starter prompt (Pass <n>)

> **Goal.** One sentence describing what this pass accomplishes.
>
> **Scope.** What's in, what's out.
>
> **Settled (do not re-brainstorm):** Decisions already made.
>
> **Still open, brainstorm these:** Questions the pass must answer before
> coding. Omit section if none.
>
> **Approach.** "Invoke site-pass to start. Standard pass-end checklist applies."
```

## When NOT to use

- The cairn-cms library initiative: use `cairn-pass`.
- Mid-pass debugging or single-file edits.
- Purely doc changes (typo fix, content update): no ritual needed.
