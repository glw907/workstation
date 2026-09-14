# The Fable overflow system (reframed 2026-07-26; originally the post-cutoff plan of 2026-07-07)

**Note (2026-08-21):** this doc's original seat policy (Opus 5 holds the execution-conductor
seat) was superseded by the global CLAUDE.md "Conducting a pass" section and
`model-economy.md`; Fable now conducts plan through execution in one session, and that
section has been removed from here. The overflow mechanics below (the access modes, the
batch desk, the suggestion rules) remain in force for Fable use beyond the 50% weekly cap.

There is no cutoff anymore: as of 2026-07-20 Fable 5 is permanently included on the Max plan
at ~50% of regular usage limits. This doc now governs Fable use BEYOND that allocation, where
Fable runs on usage credits at API rates (output $50/MTok, 2x Opus 5; cache reads $0.25/MTok on Fable 5.1, half Opus 5's; batch $5/$25). Token efficiency is
the design constraint: credit-metered Fable is a scheduled specialist with three access
modes, batch-first.

## Mode 1 — THE BATCH DESK (default; 50% discount)

Non-interactive Fable jobs go through the Batch API (async, <24h, usually minutes-hours):
- A queue directory of self-contained job files: task + ALL context pre-extracted (the
  dispatch discipline is now economic law — a job that needs a follow-up question wasted
  its round trip).
- The Opus conductor submits, polls, folds results back.
- Shared-prefix caching across jobs in one batch: N verifications against one spec share
  the spec as a cached prefix — write it once, read it cheap.
- Fits: plan drafts from prepared briefs, review verdicts, triage rankings, post-mortem
  synthesis, register/prose passes. (Most of what Fable did this arc, honestly.)

## Mode 2 — PER-DISPATCH (one-shot judgment from a live session)

A single `model: fable` subagent dispatch from the Opus 5-conducted session, for judgments
that gate immediate next steps. Rules: the brief is a prepared file; context <30k; output
capped (ask for a verdict/decision table, not prose); never inside a loop.

## Mode 3 — CACHED INTERACTIVE (rare; the design sitting)

A live Fable session ONLY for true interactive judgment with Geoff (a design sitting, a
brainstorm). Structured for cache economics:
- Fresh session, pre-baked brief file, context kept <50k. NEVER >150k (the mega-session
  lesson: 1.3B cache reads = the tax).
- The stable prefix (brief + exhibits) enters ONCE at the top; turns stay inside the
  5-minute cache TTL (the 1h extended TTL where a sitting has natural pauses — higher
  write cost, still beats cold reads).
- A declared turn budget before starting; the sitting ENDS when the decision lands
  (artifacts + picks recorded, session closed).

## Governance

- Fable-credits are budget #3 (with tokens-at-large and Geoff's attended time): every
  invocation logged (purpose, mode, tokens) in the session's post-mortem.
- A weekly credit ceiling Geoff sets; the conductor asks before exceeding it, never after.
- Verify current Batch/caching terms at first use (50% batch discount and 5min/1h TTLs
  are the standing terms as designed; pricing pages govern).

## Mechanics to build (Sonnet job)

`fable-batch` — a small CLI in ~/.local/bin wrapping the Batch API with $ANTHROPIC_API_KEY:
`fable-batch add <job.md>` (queues), `submit` (batches the queue, shared-prefix aware),
`poll`, `collect` (results to files + a digest). Job files carry YAML frontmatter
(purpose, max_tokens, cache_prefix: <path>) so the ledger writes itself.

## The conductor's suggestion rules (Opus-side, baked in)

Opus NEVER silently spends Fable credits and never silently absorbs Fable-tier work into
a worse output. When work crosses a trigger, Opus proposes — one sentence naming the job,
the mode, and the rough size — and Geoff decides. The triggers:

- **Propose a BATCH job when:** a major plan/spec needs authorship; a pass-end review has
  accumulated (a diff Geoff will rely on, a release gate); a post-mortem closes an arc; a
  register/prose pass covers user-facing text; multiple verdicts share one spec (batch
  them with a shared cached prefix). Shape: "This is Fable-batch work — [job], ~[N]k
  tokens, results by [when]. Queue it?"
- **Propose a PER-DISPATCH when:** a single verdict gates the next step and Opus's own
  confidence is genuinely low (say so plainly: "I'd trust Fable's judgment over mine
  here"); or a design synthesis must reconcile conflicting constraints in one shot.
- **Propose a SITTING when:** an interactive design/brainstorm session with Geoff is
  itself the work (candidates + picks). Never for anything a batch job could do.
- **Do NOT propose when:** Opus can verify the answer mechanically; the work is
  execution-shaped (Sonnet's); the gain is stylistic; or the same question was already
  Fable-answered this initiative (reuse the recorded answer).
- **Self-check against theater:** proposing Fable to hedge responsibility is a defect;
  the proposal must name what Fable adds that Opus lacks, or it doesn't get made.

## The pattern principle (Geoff, 2026-07-06)

"Opus will do a much better job if it has a strong pattern to start with." Fable's
highest-leverage output for an Opus-executed future is not verdicts but EXEMPLARS: a
scaffold whose structure teaches its own extension (stand-ins with swap comments, one
screen fully worked as the model for the rest), a mockup set that IS the design language,
a manifest whose first ten lines teach the next ninety, a worked pass that becomes the
template for its siblings. When queuing Fable batch jobs, prefer "produce the pattern +
one worked instance" over "decide the question" — Opus extends strong patterns reliably;
it re-derives designs from prose unevenly. Every Fable job spec should name what pattern
it leaves behind. Geoff's formulation, the system's headline: **"I want to give it a
setup where it just needs to color inside the lines. Fable draws the lines."** Fable's
job is the lines — the structure, the acceptance, the worked instance; Opus's job is
faithful, verified coloring. A Fable invocation that doesn't leave lines behind was
probably the wrong invocation.
