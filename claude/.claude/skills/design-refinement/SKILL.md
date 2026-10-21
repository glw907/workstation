---
name: design-refinement
description: Use when polishing an EXISTING design — a page, app screen, or artifact whose bones are approved — iterating live against a dev server, iterating async via probe pages the owner reviews on their own time, or landing a ratified design toward a benchmark finish. The refinement counterpart to origination skills (frontend-design) and port-matching skills (visual-fidelity).
---

# Design refinement

For the common case no generation tool serves: the design exists, its owner has approved its
bones, and the remaining distance is composition, register, and craft. This is not origination
(inventing an aesthetic) and not porting (matching an external original) — it is closing the
last fifteen percent on your own work, and knowing when to stop.

The failure mode this method exists to prevent has a studied name (arXiv 2605.30335, "locally
coherent, globally incoherent"): element-by-element patches, each locally correct, that
degrade the whole — and the study's key negative result is that adding surrounding-context
prose to narrow patches makes results WORSE, not better. The fix is a different unit of work,
not better patch prompts.

Refinement carries the evaluative design vocabulary (axes, knobs, dose); it does not carry the
generative one. When a genuinely novel aesthetic decision arises inside a refinement arc — a
taste fork, a new element or composition within the approved bones — load the frontend-design
skill for that one decision (its direction-setting method: subject grounding, type pairing,
palette authorship, the signature element), decide, then return here. Deciding a novel
direction from refinement's checklists alone is how template looks slip in.

## Starting up: discover, then ask once

On invocation, do not open with a questionnaire. First DISCOVER what the project already
holds: look for the four persistent artifacts (benchmark captures, audit ledger, decisions
log, recorded dose words — conventionally together, e.g. `docs/design-benchmark/`), the
design's token/style system, the review surface (a dev deployment? a preview URL?), and any
design doc or ruling history. Read what exists; a question whose answer is discoverable
misroutes the owner's attention.

Then ask ONE batched question covering only what is genuinely owner-held and still missing —
typically: the dose level (felt-only / standard / deep), anything off-limits this round, and
the target's priority order if several surfaces compete. If no benchmark exists, pinning one
is the first work item, not a question ("which state should I pin?" is only asked when the
answer is ambiguous). After that, questions during the arc are the exception: batch
mid-round judgment calls rather than stopping per item, and reserve immediate questions for
genuine forks in the owner's own taste — which get answered-then-executed per step 6, never
silently absorbed.

## Three modes — pick by whether taste is still converging, never by where the owner sits

The deciding predicate is the WORK's state, not the owner's presence: while the owner's
design notes are still arriving — taste unconverged — the work is an ARC and iterations must
be cheap; only ratified work runs the full machinery. Routing an iterative round into the
settled-landing pipeline because the owner reviews async is the observed expensive failure
(ASC basic-polish, 2026-07-16: three notes-adjudicate-dispatch-gate-regen cycles before the
owner named it — "it seems to frequently land us in these long, slow, and expensive loops";
his ruling: "we're only running the deep and expensive full rebuild a minimum number of
times"). The full build-gate-baseline cycle runs once per settle, never per iteration.

- **Exploratory arc (live)** — the owner is co-present, reviewing in a localhost tab (dev
  server + HMR), and the notes are probes ("could", "maybe", "try"). Expect 10-15 fast
  iterations; cost and latency per turn are the binding constraints. Run the arc contract
  below; the rounds-and-passes machinery and every per-round gate stay off until settle.
- **Async probe arc** — the owner reviews on their own time and the notes are still design
  iteration (element complaints, taste directions, "needs a redesign"). Same arc economics,
  different medium: instead of a live tab, each round delivers a self-contained PROBE PAGE
  the owner opens whenever (see the probe-page contract below). No builder dispatches, no
  gate, no baseline regeneration per round.
- **Settled landing** — the design is RATIFIED (the owner's verdicts are in, or the round is
  mechanical rollout of an already-ruled vocabulary) and the work is landing or closing it.
  Run the numbered method and agent economy below as written — once per settle.

An arc ends by flowing into a one-time landing: the settle ritual IS the ceremony the
iterations skipped.

## The async probe arc's probe-page contract

A probe page is one self-contained HTML file (data-URI images, the design's REAL tokens and
CSS inlined so the render cannot lie about type, color, or spacing), opened in the owner's
browser (`xdg-open`), holding per region: the CURRENT state beside one or more CANDIDATE
treatments (before/after pairs, or an A/B/C slate for a taste fork), at the design's real
widths, each with a one-line caption naming the change. Candidates render via captured
screenshots plus CSS-injected variants against the deployed or dev surface — never a
production build per candidate. The owner verdicts per region (keep / revert / push
further / pick B); kept verdicts accumulate in the arc log and land as ONE commit batch at
settle, where the full gate, CI-canonical baseline regeneration, and deploy run exactly
once. The ASC register round is the proven exemplar: probe page rendered, verdict in
minutes, one landing commit.

Before a probe page or prototype goes to the owner, `prose-voice-reviewer` reads its fixed UI
copy (headlines, ledes, button and empty-state text) against the register of the content the
screen presents (a docs review screen reads against the docs register), and its
findings go to him beside the layout. A sitting about layout does not read the words, which is
how approval-queue#4's blueprint headline reached Geoff in marketing voice (2026-10-21).

## The exploratory arc

The shape this mode replaces failed its cold trial: live probes translated to axes and
dispatched to builders with per-round gates — correctness ceremony on work whose whole
point is cheap trial and error.

Opening the arc, the directing context bootstraps the review surface itself — the owner
arrives at a live tab, never at instructions. Start the site's dev server as a background
process (its output stream is the tier-one check below), wait until it answers, seed local
media if images 404 (`cairn-media-seed`, or the site's wrapper script), and open the owner's
browser at the page under iteration (`xdg-open <url>` on this workstation). Then the
per-iteration contract:

1. The directing context edits DIRECTLY against the running dev server. No builder
   dispatches for iteration edits: a dispatch costs pre-extraction plus round-trip latency
   exceeding the edit itself, and per-tweak diff review is exactly the ceremony the owner
   banned.
2. Direct editing does not suspend the axis rule, and the iteration unit is the ROUND, not
   the note. Invite grouped feedback and batch the open notes; a note arriving while a pass
   is in flight joins the current round, never spawns its own edit-render cycle. Translate
   each note to its design axis (emphasis, hierarchy, density, rhythm), then answer the
   whole batch with ONE composed pass over the surface: rule the grammar (a ladder, a
   scale, a reservation), state every affected element's treatment before editing, apply it
   everywhere the axes reach, render once. A per-element patch answering a per-element note
   is how the locally-coherent failure mode enters an arc, cheap probes or not. Three live
   tells, all observed (2026-07-15, cairn admin arc; the later two under a weaker version
   of this rule): the owner's next note contradicting your last fix (too loud, then nearly
   invisible); a third note arriving on the same surface (a pill family whose inks diverged
   because it was assembled by accretion, never designed); and the owner having to say
   "grouped feedback, holistic response" out loud. Each means the surface was never
   designed whole — stop editing, write the surface's full spec, then one pass.
3. A note that is a question gets a reasoned answer before any edit. A probe gets rendered,
   and the reply tells the owner exactly what to look at. The iteration ends with the
   owner's verdict: keep, revert, or push further.
4. Each kept iteration gets a one-line commit on the arc branch (`design: <probe>`); a
   reverted probe is a checkout. No pushes and no deploys until settle.
5. One line per iteration lands in an arc log beside the decisions log (probe, verdict,
   why) — insurance against context loss, and the raw material the settle-time decisions
   entry distills before the log is removed.
6. The only dispatch inside an arc is a genuine taste fork: two or three parallel throwaway
   static-HTML candidates generated while the main loop keeps iterating; the owner picks,
   or the directing context does when the owner delegates.

Self-checks run in three tiers, never the full gate:

- **Every iteration:** watch the dev server's output (a background process) for HMR and
  console errors. For pure CSS and copy tweaks that is all — the owner's live eyes are the
  per-iteration visual gate.
- **Structural edits** (splitters, wrappers, `{@html}` segments — anything whose failure is
  invisible in the source): the targeted regression test plus a quick DOM sanity check. A
  hydration-duplication bug once cost a whole round of misread owner notes because this
  tier was missing.
- **Every ~5 iterations,** and before any "ready for your look" on a structural rework: one
  own render read at a narrow and a wide width, catching the global drift that focused
  per-note eyes miss in both parties.

The settle ritual, once, when the owner ratifies (notes go felt-tier or he calls it done):

1. Design gates first: the project's design-probe script, a small fresh-context lens
   fan-out, and a full-width-set render read; findings return to the owner as one batch.
2. Code ceremony second: the simplifier over the arc's whole diff, then the repo's full
   gate.
3. A final quick render read confirming the ceremony changed nothing visible.
4. Artifacts: the decisions-log entry (settled decisions with reasoning, dose words
   quoted), benchmark re-pin if the owner ratified a new one, arc log distilled and
   removed.
5. Merge and push, then the one deploy (the default; a site may settle-and-hold and deploy
   several arcs together), a post-deploy render read, and the owner's before/after where
   the surface is member-facing.
6. Harvest: engine frictions filed upstream, chassis-worthy machinery banked.

Red flags you are in the wrong mode: dispatching a builder for a one-note tweak; running
the simplifier or e2e on iteration 3 of 12; converting a "maybe try…" note into a work
item; deploying mid-arc so the owner can review what localhost already shows; answering
an element complaint with an element edit when the previous iteration's fix drew the
contradicting note — that oscillation means rule the axis's system, not re-tune the value;
shipping a second consecutive single-note edit-render cycle on one surface instead of
batching the round and re-composing the surface once; running the full
build-gate-baseline-regen cycle more than once between owner verdicts — the owner's design
notes are still arriving, so this is an arc, and the cycle belongs at settle; choosing
settled-landing because the owner reviews async rather than because the work is ratified.

## The settled-landing shape: rounds, not a pass

Refinement is inherently iterative — an owner reviews, notes arrive, a round runs, the owner
reviews again — and the method is designed for that loop, not for one heroic pass. Each round:
translate the new notes to axes (step 2), run the scoped passes (step 3), read and gate (step
5), deploy once at readiness, owner reviews. Four artifacts persist BETWEEN rounds and are the
loop's memory:

- **The benchmark captures** (re-pinned deliberately when the owner ratifies a new state).
- **The audit ledger** (already-right verdicts survive rounds; see step 7).
- **The dose words** (the owner's calibration language, quoted verbatim into every round).
- **The decisions log** — every settled design question with its reasoning ("corners:
  group-rounded because the panels form one object; settled round 7"). Later rounds never
  re-litigate a logged decision unless the owner reopens it.

Read convergence from the notes themselves: notes getting smaller and finer-grained
(paragraph-level → pixel-level) means the loop is converging — keep going. The SAME note
recurring after an anchored fix means the unit of work is wrong — widen the pass, don't
re-patch. Notes multiplying in new regions after each round means the rounds are shipping
regressions — stop and audit before continuing. The arc ends when a round's notes are all
felt-tier: run the full felt-refinement audit (step 4) as the closer, then pin the result as
the new benchmark.

## The method

1. **Pin the benchmark.** Refinement needs a reference render, never adjectives. Capture the
   current approved state (or the project's best page) at the design's real widths, commit the
   captures, and grade every pass against them the way a port is graded against its original.
   If the benchmark evolves, re-pin deliberately — new captures, owner sign-off — never let it
   drift. No benchmark exists? Pinning one is step zero, not optional.
2. **Translate every note to an axis, then batch.** Owner notes arrive as element complaints
   ("this list is too loud"). Never dispatch them verbatim. Translate to a named design axis —
   hierarchy, density, rhythm, register, alignment, contrast — batch same-axis notes, and
   re-scope the work to the whole page or section on that axis. A note that recurs after one
   anchored fix is the incoherence signature: WIDEN the regeneration unit; never layer a third
   narrow instruction.
3. **Passes, not patches.** Structure iteration as whole-surface passes: (a) spacing,
   alignment, and hierarchy; (b) type, color, and token conformance; (c) states, interaction,
   and accessibility. Each pass covers everything in scope, so local fixes compose.
4. **The felt-refinement audit** (the endgame): read-only designer lenses — typography and
   rhythm; color, surface, and depth; interaction and motion — audit the DEPLOYED or built
   state against the benchmark and return a LEDGER: every knob evaluated, marked
   already-right / recommend (with the exact change and a felt-impact rating) /
   not-applicable. The calibration is binding and worth quoting verbatim in every lens prompt:
   the burden of proof is on the change, and a mostly already-right ledger is the expected
   outcome of auditing good work — never manufacture recommendations to look useful. A
   directing context adjudicates the ledger; one fixer applies only what survives, with
   interactive proof for anything a static screenshot cannot show (focus rings, selection
   color, hover states, cursor affordances).
5. **Separate who builds from who reads.** The builder's self-screenshot is for its own
   correction, never the gate. A context that did not build the work reads the renders — at
   minimum the directing context reads a full-surface render at every checkpoint, before any
   commit. Builders stop at their best render and wait; deploys to the owner's review surface
   happen at readiness points only, never per-round while a review conversation is open (the
   owner ends up reviewing a moving target, and stale tabs multiply confusion).
6. **The owner's words are calibration data.** Dose statements ("don't overdo it", "this is
   felt refinement", "less designed than the landing page — it's a brochure") are load-bearing
   and travel verbatim into every dispatch. When the owner hasn't stated a dose, ask for it as
   a named level — **felt-only** (invisible-until-touched craft: selection, focus, wrapping,
   optical fixes), **standard** (felt-only plus register and rhythm corrections), or **deep**
   (standard plus composition rework within the approved bones) — one question, before the
   pass. And the owner's design QUESTIONS ("should this have rounded corners?") are questions:
   they get a committed, reasoned answer before any execution. Converting an owner's
   uncertainty into a work item launders an open question into a decision nobody made.
7. **Persist the ledger.** Commit the audit ledger beside the benchmark captures. The next
   pass starts from the recorded already-right verdicts instead of re-auditing and possibly
   re-litigating settled decisions — the ledger is what stops refinement from oscillating.
   An entry is re-opened only when the code it graded has changed or the owner overrules it.

## Agent economy (who runs, on what, and why)

This skill runs in the DIRECTING context — the strongest model in the room, because
adjudication, render reads, and axis translation are the judgment that prevents rework.
Everything else is dispatched, and the dispatch is role-matched:

- **Builders** execute already-decided treatments: a capable mid-tier model is right, because
  the taste decisions travel IN the dispatch — named devices, the benchmark paths, exact
  values where they're settled, the owner's dose words verbatim. Never send a builder the raw
  note ("make it less bland"), this skill's text, or an open aesthetic choice: an
  under-directed builder on any model produces the AI-default looks. If a round contains one
  genuinely novel visual decision, either decide it in the directing context first or upshift
  that single dispatch — not the whole round.
- **Audit lenses** split by what they judge. Taste-heavy lenses (typography and rhythm;
  color, surface, and depth) justify a strong model — misjudged taste findings cost real
  rounds. Mechanically-verifiable lenses (interaction states, reduced motion, focus coverage,
  overflow) run on a cheaper model with computed evidence required (getComputedStyle values,
  measured coordinates), which beats a stronger model's unmeasured impression anyway.
- **Panel economy**: two or three lenses per audit, once per ARC (at the felt-refinement
  closer), not per round. Per-round quality lives in the directing context's own render read,
  which is cheaper and faster than any panel. Refuter agents are spent only on contested
  MAJOR findings — never on minors, and never as votes.
- **Separation is context, not model**: the grader must not share the builder's context —
  a fresh instance of the SAME model out-grades the builder grading itself. When budget
  allows, cross-model diversity between builder and reviewer also counters correlated
  blind spots.
- **Measure, then judge**: anything measurable (row alignment, spacing ratios, contrast,
  dot centering) gets measured by script before any agent opines on it. Agents are for the
  judgments a ruler can't make.
- **Iterate cheap, verify real**: design iteration renders on the cheapest medium that tells
  the truth — a standalone HTML file carrying the design's REAL tokens and CSS (so the render
  can't lie about type, color, or spacing), or the framework's hot-reloading dev server.
  Never a full production build per adjustment; the full build, gate, and deployed-surface
  read run ONCE per round, at readiness. Candidate exploration doubly so: present options as
  throwaway static HTML pages, and build only the winner.

## Hard scope limits

- Refinement never changes the stack: no dependency swaps, no library migrations, no framework
  moves, unless the owner explicitly requests one. (A motion-polish pass that migrates the
  animation library has left refinement.)
- The audit runs at the design's full declared width set (e.g. 320/390/768/1440/2560 for a
  responsive site), plus dark mode where the design ships it, plus interaction states — a
  single-desktop-screenshot audit reliably misses the defects owners find first.
- Every audit includes one explicit coherence question: **does anything here read as
  AI-default?** Use frontend-design's calibration list as the source (its five clusters:
  cream-serif-terracotta; near-black with one acid accent; broadsheet hairlines with zero
  radius; the SaaS-card kit of identical rounded cards, one radius, one grey shadow, and
  gradient washes; template chrome such as ALL-CAPS eyebrows over every heading,
  middle-dot meta strings, monospace data labels, and '→' on link text), plus these
  defaults: one italic or colored accent word in a headline, 01/02/03 markers on content
  that is not a sequence, pill-shaped buttons, and emoji section markers.
  Refinement that installs a template look has failed even if every knob passes.

## Knob calibration (the kinds of thing an audit evaluates — not a checklist to satisfy)

Optical alignment; hanging punctuation; proper typographic characters (curly quotes, real
ellipses, correct dashes); tabular figures where digits column; letter-spacing on caps and
eyebrows; modular-scale conformance; measure control (45–75ch); leading tuned to size and
measure; widow and orphan prevention; text-wrap balance on headings; near-black ink and
near-white grounds; palette constraint with tonal variation; borders via transparency rather
than flat gray; layered low-opacity shadows; radius consistency across every framed element;
selection color; focus-visible consistency across EVERY link family (the ones outside the
main prose class get missed); link underline treatment (rest translucency, hover strengthen);
transition durations and easing; reduced-motion coverage; image aspect intent and frame
consistency; custom list markers; asymmetric spacing that follows hierarchy; heading margins
(tighter above, looser below); cursor affordance on icon-only buttons; font loading versus
layout shift.

## Anti-patterns (each observed to cost a real round)

- Element-by-element prose dispatches, with the owner as the only person reading whole
  compositions.
- Accepting the builder's "looks good" without a fresh-context read (self-grading).
- Hand-tuned optical values — an em-based nudge, a line-count min-height — surviving a type
  change they were calibrated against. Re-measure every optical constant after any type
  change; em units scale with the wrong font when the reference element changes.
- Deploying every merge to the owner's review surface mid-review.
- Treating the owner's design questions as commands (one real page shipped three corner
  treatments before a single design exchange settled the question).
- Inventing copy during refinement. The existing approved text — or the owner's supplied
  text — is the specification; trims are deletion-only (cut whole clauses, never paraphrase)
  so every surviving word stays the author's own.
