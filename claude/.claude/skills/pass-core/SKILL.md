---
name: pass-core
description: >
  The shared pass machinery that cairn-pass and site-pass load: the pass-class table,
  the per-task execution chain, execution discipline, the close ritual skeleton, the
  pre-bake and context-clear handoff, and the resume prompt. Use when a repo-specific
  pass skill points here, or when starting, resuming, or closing a planned pass in a
  repo that has no pass skill of its own.
---

# Pass core

A pass is one plan executed on its own branch, from a committed plan to a closed ritual. This
skill holds what every repo's pass shares. The repo's pass skill (`cairn-pass`, `site-pass`)
supplies the paths, the gate commands, the implementer agent, and any repo-only close step.
Where the two disagree, the repo skill wins for its repo.

## Phases and models

Planning and execution run in separate sessions (Geoff, 2026-09-22, per Anthropic's model
guidance):

- Brainstorm and plan: a `claude-opus-5-5` session at effort `high`.
  `superpowers:brainstorming` settles the open decisions, then `superpowers:writing-plans`
  authors the plan.
- Execute: a fresh `claude-opus-5-5` session at effort `medium`, started from the
  STATUS resume prompt. The conductor stays thin. It never reads a diff, a source file, or a
  gate log; `diff-reviewer` reads the diff.
- Escalate: an unsettled question follows the escalation order in
  `~/.claude/docs/model-economy.md` "Current state", never a session switch.

Brainstorm scope: probe until the plan carries no open readings. On product, taste,
priority, scope, and budget questions, the brainstorm's length is never a cost to trim
(Geoff, 2026-09-04). Method, idiom, and architecture questions are Claude's to decide from
published evidence, the framework's convention, or best practice (Geoff, 2026-09-24/26);
bring them as one design for approval and flag only the contestable points. Design-system
taste is Claude's too, the one exception to "taste goes to Geoff" (2026-09-27: "I'm not a big
UI/UX guy, so I'm counting on you to make the system clean, simple, logical, and flexible"):
token names, lever sets, and theme structure are decided from evidence, such as a harvest of
the sites' real designs. A STATUS resume prompt saying "settle X with Geoff" does not override
this when X is method; decide it, show the whole design, and ask one approval.

Conform to conventions (Geoff, 2026-09-13). When a design fork has a widely used convention or
a published standard on one side, take it unless it conflicts with the charter or a measured
defect, and record the reason whenever the work departs from it. A documented exception beats a bespoke
mechanism: a convention is borrowable by a developer extending the work, survives upgrades,
and needs no local explanation, while a bespoke solution must be documented, enforced, and
re-learned.

**The spec is the owner's gate; a reviewed plan runs (Geoff, 2026-09-27).** Geoff reads every
spec himself, with one standing exception (Geoff, 2026-09-13, reaffirmed 2026-09-28): a pass
that is a local implementation of a chosen published standard (the admin motion pass
transcribing IBM Carbon's productive motion set is the example) skips his spec read. That spec
instead takes an adversarial review for fidelity to the standard's published values,
completeness over its case list, charter fit, and plannability, and the approval gate asks him
only for the plan's task list and ceiling. A plan does not wait for his read: once it clears `spec-plan-review` at its
class's full depth, with blockers and majors closed and the verification read clean, the
conductor executes it and names it in the next sitting's summary. Two things still stop it. A
ruling or product fork in the plan's "Rulings for Geoff" section blocks the tasks it governs,
and a fundamental architectural question the review reveals, one the spec did not settle, halts
the pass for Geoff.

**An owner sitting asks only forks (Geoff, 2026-09-28).** A sitting page or checkpoint question
puts to Geoff only taste, product, priority, and scope calls with no dominant answer. A defect,
an accessibility fix, an in-spec keep, or a restated plan decision is the conductor's call: the
page lists it as decided, with its disposition, and never as a question. A dispatch that builds
a sitting page says so. (S3 of theme identity pass A asked 22 questions where three were forks.)

**A pass meant to run unattended plans out every stop (Geoff, 2026-10-07: a pass should handle a 10+ hour unattended
run).** The plan settles, before execution: a hard token ceiling with a stop-and-write-STATUS rule, so no budget
question arrives mid-run; which verdicts the conductor rules on alone (a runner artifact, a flake the rerun rule covers)
and which stop the run (a real defect after its one fix round, an architectural fork); and owner-gated steps (reads,
smokes, the merge) batched at the end. At launch the conductor arms the fallback `/loop` wake-up (a connection drop
otherwise waits for a human), the lid-switch hold, and the stall guard, in daytime too
(`~/.claude/docs/unattended-work-guards.md`).

**Plans stay outcome-only.** Each task states outcomes, constraints, acceptance criteria,
files, and its pass class, never implementation code. This overrides `writing-plans`'
full-code steps. Skip its "which execution method?" question; this skill answers it.

Every plan header carries a token ceiling, a checkpoint interval (default four tasks), and
`Pass class: <class>`. At each checkpoint, at any split, and before any question to the
user, write STATUS (task ledger, decisions taken, spend, next task), then continue.

## Pass class (Geoff, 2026-09-27)

The ceremony scales by the kind of change, not only its size. The plan header declares the
class; a task that differs carries its own `Pass class:` line. A misfit class is a
plan-review finding in both directions. A mixed pass runs the union of its tasks' classes at
the close.

| Class | Per-task gate | Review and blocking bar | Test mandate | Settle and close |
| --- | --- | --- | --- | --- |
| `auth-data` (auth, signing, sessions, D1, the commit path) | the gate tier its diff computes, plus the e2e specs its change reaches; the full gate at each segment boundary and before merge | Opus; coverage gaps block | test-first, a mutation proof | `web-auth-security-reviewer`, a live auth smoke |
| `engine-logic` (TypeScript behavior) | the gate tier its diff computes, plus the e2e specs its change reaches; the full gate at each segment boundary and before merge | Opus; blocks on behavior defects and unmet outcomes, coverage gaps only on reachable behavior | test-first | none extra |
| `paint` (CSS, theme, visual) | a targeted gate the plan names per task (type check, the touched files' component tests, CSS unit tests); full suite at segment boundaries or on CI | Opus (or Sonnet); blocks only on a behavior defect or unmet outcome, coverage notes batched to the boundary | one cascade test per rule (renders, a utility beats it); state tables only where the framework restates values per state; table-driven | an async owner glance at captures mid-pass, a fresh-context `visual-verifier` read, the owner sitting |
| `sweep` (mechanical markup or rename) | type check plus the component project | Sonnet; grep-based post-conditions | existing tests stay green | spot captures |
| `docs` | the docs tier | the register chain | none | none |
| `tool` (Go) | `make check`, light gate lane | Opus | `go-conventions` | `tui-visual-verify` for a TUI change |

**The per-task gate is the change's blast radius, never the whole suite (Geoff, 2026-10-08).** A
task runs the tier its diff computes (`gate-tier.mjs` where the repo has one) plus the e2e specs its
change can reach; the full gate runs once at each segment boundary and on CI before merge. This
follows presubmit test selection (Google's TAP) and the deployment pipeline's fast commit stage
(Fowler): assurance on a sensitive change comes from its targeted tests and mutation proof, not
from rerunning unrelated suites. The older full-gate-per-task cells were inherited, not researched
(engine pass pre-2b, pass A: Task 1 alone ran four 45-minute full gates). A plan pins a wider tier
only with a named risk the computed tier misses, and never to carry an environment export (put
the export in the task's own gate string).

Superpowers skills yield to the pass class: TDD's write-first applies to `engine-logic` and
`auth-data` only, and plans stay outcome-only.

`~/.claude/workflows/pass-execute.js` renders each class's mandate and bar into the prompts,
demotes coverage-only findings for classes whose coverage does not block (returned as
`batchedNotes`), and reduces the gate on a comment-only or test-only fix round (all classes
but `auth-data`). Its header comment is the spec; `PASS_CLASSES` there must stay in step with
this table. With no class, the runner keeps its pre-class behavior.

## Executing

Before the first dispatch, confirm the plan is committed, STATUS points at it, and you are on
the pass's branch or worktree, never the default branch's checkout.

Each task runs as a chain:

1. The repo's implementer (Sonnet) meets the class's test mandate, clears the class's
   per-task gate through `cairn-run-gate`, and returns files touched, the gate result,
   unspecified decisions, and anything it could not do.
2. `diff-reviewer` reads the diff against the task's acceptance criteria at the class's
   blocking bar and returns accept, fix, or escalate with `file:line` findings.
3. One re-dispatch on `fix`; a second `fix` is the conductor's decision.

Below six tasks, dispatch the chain per task with the Agent tool and paste the class's
mandate and bar into both prompts. At six or more, or when the plan marks tasks independent,
run `pass-execute` by name with `{repo, gate, implementer, passClass, reducedGate?, tasks:
[{id, title, criteria, files, notes, passClass?, gate?}]}`. One invocation runs one segment.
Read `~/.claude/docs/pass-gate-economy.md` before the first segment; its rules reach an
implementer only through the args.

Upshift a dispatch to `model: opus` only for novel correctness-critical logic the plan does
not specify; any further escalation follows `~/.claude/docs/model-economy.md` "Current state".

### Execution discipline

- **Share the heavy gate lock deliberately.** A segment boundary reuses the last task's full gate when `HEAD` has
  not moved since it ran; never re-run a full gate on an unchanged commit. When another live session shares the
  machine (`ListAgents`), send it a one-line heads-up before a heavy gate expected over 15 minutes, and say so when
  your next heavy gate is more than about 30 minutes away. The four rules live in
  `~/.claude/docs/pass-gate-economy.md` ("Sessions sharing the heavy lock coordinate").
- **One implementer per dispatch, verified.** Wait for each result and verify its commit
  (`git log`, `git status`) before depending on it. On an API overload or 5xx, wait and retry
  once; never fire a second dispatch while one may still be in flight.
- **Pre-flight the plan's factual claims.** Before each segment, dispatch one `haiku` or
  `sonnet` pre-flight that lists every checkable claim the segment's tasks make about existing
  code (counts, error meanings, paths, shapes) and checks each at HEAD. Amend the plan, then
  dispatch. A wrong claim found at review costs a full fix round.
- **Read a tool's `--help` once** before a pass relies on it, and act on a tool's NOTE in
  an agent's report before the next dispatch.
- **File every out-of-scope finding the same session (Geoff, 2026-09-29).** A defect any
  dispatch reports outside its task goes into the repo's friction log at the next checkpoint
  commit, verified against the code first. That covers a reviewer's OUT OF SCOPE list, a
  runner's top-level `outOfScope`, and an implementer's or sweep's aside. The repo skill names
  the log; a repo without one files the finding through `log-issue`. STATUS may point at a filed
  entry but never holds a finding alone, and a finding that fails verification is dropped with a
  one-line reason in the checkpoint note. (The draft docs harvest parked four findings in STATUS
  until Geoff asked; one was false.)
- **Harvest cairn friction in every cairn-family repo (Geoff, 2026-10-07).** In cairn-cms,
  the sites, cairn-themes, and cairn-pub, every dispatch also reports friction with cairn itself:
  a docs gap or error, a suggested engine improvement, or a DX snag. `pass-execute` and
  `pass-execute-chains` ask for it whenever the repo path matches the cairn family and return each
  item in `outOfScope` tagged `cairn: true`. A hand-dispatched prompt asks for it in one line.
  The conductor verifies each item against the cairn-cms tree and files it under "Open findings"
  in cairn-cms's `docs/internal/docs-friction-log.md`, whatever the repo's own log, with a
  perspective tag, the finder, and the date. That checkout is shared, so stage only your own hunk.
- **Verification a plan parks "for the owner" is Claude's (Geoff, 2026-09-21).** Run the
  release candidate, the real-terminal check, the flag, or the theme yourself (the real
  binary against Geoff's sites with the stored read credentials, a TUI through
  `tui-visual-verify`), grade it fresh-context, and hand over the evidence. Only what this
  machine cannot run (macOS launchd, Windows Task Scheduler) stays reasoned and disclosed. An
  owner gate keeps the irreversible act (tag push, release, merge) and his go, never test
  labour. Copy and taste questions are asked while he is present, a few at a time with
  rendered previews, never parked for a later "editorial gate"; a string he words himself is
  used verbatim.
- **Verify locked build assumptions** (an export map, a module-resolution mechanism) against
  the real toolchain at the first task that touches them.
- **Vale findings are tiered.** Only an error-tier finding drives a fix; warnings and
  suggestions are advisory.
- **Suggest the Workflow tool at the right moments.** It runs only on the user's explicit
  opt-in, so name the moment it would pay off (a large pass's review gate, where an
  adversarial find-and-verify sweep beats the flat fan-out; mostly independent tasks; a
  repo-wide audit or migration) in one sentence with shape and rough scale.

## Closing: the ritual skeleton

No pass is done until every step has run. The repo skill supplies each step's commands.

1. **Simplify, once per pass.** Dispatch `code-simplifier:code-simplifier` (the bare name
   errors) over the pass's changed code, once at the close, and only when TypeScript
   (JavaScript included: `.js`, `.mjs`), Svelte, or Go changed; Python and bash never take it.
   It never runs at a segment or task boundary, whatever the class; a `paint` pass that
   changed TS or Svelte takes it once at the close, and a `docs` pass never does.
2. **Full gate.** The repo's full gate, including any suite a `paint` or `sweep` pass deferred
   from its tasks. A test run is green only when it exits 0.
3. **Review fan-out by class.** `svelte-reviewer` for Svelte or load/action code,
   `cloudflare-workers-reviewer` for Worker, D1, or wrangler code,
   `web-auth-security-reviewer` always for `auth-data` and any auth, session, cookie, token,
   or signing change, `daisyui-a11y-reviewer` plus `visual-verifier` for `paint`, a
   `go-architecture-reader` per touched package for `tool`. A `docs` pass takes the register
   chain instead.
4. **Class settle steps** from the table (the live auth smoke for `auth-data` only).
5. **Docs** the pass changed, per the repo skill.
6. **Ledgers.** `docs/STATUS.md` is present tense only (current state, next action, open
   decisions, pass-scoped carry-forwards; target 60 lines or fewer). The pass's entry goes to
   `docs/HISTORY.md`, newest first: what landed, what the gates caught, and what a later pass
   would be wrong to rediscover. An initiative or a standard-setting carry goes to
   `ROADMAP.md`; a shipped roadmap item leaves its live tier. Initiative state never goes to
   memory: memory holds only what the repo cannot (preferences, corrections, the why behind a
   ruling no doc records). When the pass's spec or plan had a full-sequence `spec-plan-review`,
   the HISTORY entry names any finding its fold refused that turned out to be a real defect
   during execution, or says none did (the fold-rule trial, Geoff, 2026-09-28).
7. **Commit** specific files, never `git add -A`. Push or merge per the repo skill.
8. **Pre-bake and hand off** (below). Always, not on request.

## Pre-bake and the context-clear handoff (Geoff, 2026-08-01)

A finished pass always ends by prepping the context clear. Every turn of a continued session
re-buys the cached conversation, so a session carried past its pass charges the next one for
context it does not need.

The prep: the plan, STATUS, and ROADMAP are committed, the tree is clean, and the user's last
read is the resume prompt plus the launch directory, with a plain statement that the pass is
closed. The test: a session starting cold from that prompt reaches the same next action under
the same constraints, having read only the plan, the spec, STATUS, ROADMAP, and memory. Walk
the pass's decisions against it, including ones changed mid-pass and any branch topology (a
deferred merge changes where the next pass branches from).

The next plan is drafted in a fresh brainstorm session, never in the closing one. If the next
pass has open questions, STATUS's next action says so and names the brainstorm; a warm
closing context is not a reason to keep the session. Continuing in one session is only for
work within one phase, such as a segment boundary inside an executing pass.

### Resume prompt format

STATUS carries the next action as a prompt a cold session can run:

```markdown
### Next action (Pass <n>)

> **Goal.** One sentence: what this pass produces.
>
> **Scope.** What is in, what is out.
>
> **Settled (do not re-brainstorm):** decisions already made.
>
> **Still open, brainstorm these:** product or taste questions only. Omit if none.
>
> **Approach.** The plan path, the pass class, and the per-task gate. "Invoke <repo pass
> skill> to start." Launch directory: <repo>. Model: `claude --model claude-opus-5-5`.
```
