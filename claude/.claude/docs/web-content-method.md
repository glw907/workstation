# Web-content authoring method

The shared, site-agnostic method for drafting and reviewing website content. Each site supplies
its own voice and facts in its local `content-guide.md`. This doc supplies the process, the
catalog, and the rubric. Both the `content-draft` and `content-review` skills load it.

The guiding principle: a website article is not a code comment. Website content starts from the
audience. The substance levers (audience, concreteness, exemplars, an independent rubric review)
do the real work. The avoidance levers (the banned list) are backstops, best left to
the deterministic Vale check.

## 1. The brief-first drafting method

1. Build the brief, first, as a durable file at the site's `docs/content-briefs/<piece>.md`. It
   holds four things and no prose: the verifiable facts (every place, time, date, name, cost, and
   rule the piece will state), the audience questions the piece must answer, the one next step,
   and the container plan (which UI containers the prose renders into). A redraft starts from the
   brief, not from the old prose.
2. Mark gaps as `[ASK: question]` in the brief and carry them into the draft verbatim. Never pad
   around a missing fact; a visible question is cheaper to fix than a paragraph of filler, and
   fact-starved abstraction is where slop enters. Drafting never blocks on the user.
3. Load the site's generative guide. The site `content-guide.md` carries the load-bearing rules,
   the container budgets, and a recipe per content type, each recipe with a real exemplar. The
   site's voice corpus carries the wider exemplar library. Exemplars are the primary style
   control; the banned list is a backstop.
4. Draft each section as a reply. Pick the section's imagined reader and their question from the
   brief, and answer them in conversation order, pulling facts from the brief as the answer
   needs them. Spend words unevenly: more where the worry is, less where it is not, and a brief
   fact that serves no question stays in the brief. Small opinions and hedges are allowed, one
   or two per page. Containers keep their budgets. Writing *about* the subject instead of *to*
   a reader is the failure mode; even coverage of a fact sheet reads as marketing copy whatever
   the sentences do.
5. Humanize and skeptic pass, run as an independent critic. Dispatch a fresh subagent that sees
   only the draft, the brief, the site's voice calibration set (negative and positive examples;
   ECXC's is `docs/voice-calibration.md`), and the nearest corpus entries. Two hunts. Style: the
   sentences that match a negative example or could appear on any organization's site. Logic:
   read as the most knowledgeable, least charitable reader the piece will ever get and flag any
   claim or implication that reader knows to be false, plus any frame whose reasoning does not
   follow. Externally checkable third-party claims get verified online against a primary,
   careful source (an org's FAQ or legal page over its marketing copy), never from model memory,
   even when the user supplied the fact; the source's wording wins. Rewrite only what the critic
   flags.
   Self-critique inside the drafting context is the weak form, the same reason reviews run
   fresh. Without a calibration doc, do the hunt inline as a second read with that single job.
   Then run the section-6 self-check plus the brief checks: facts landed once, every `[ASK]`
   visible, budgets held.
6. Offer the gate check. Offer to run `content-review` before saving or committing.

Draft-off, optional, for a high-stakes page on request: generate two or three candidates from
deliberately different stances (FAQ-flat, trailhead-spoken, letter-home), judge each against the
site's corpus exemplars, and splice the strongest sections into the offered draft.

The learning loop runs on the user's feedback, routed the moment it arrives. The strongest
channel is the rewrite delta: the user replies to a drafted passage with their own improved
version; diff the two sentence by sentence, record the pair in the site's calibration set
(theirs positive, the draft negative) and their version in the site corpus's first-party gold,
state the one generalization the delta teaches, and encode it in the site guide. Inline flags
and praise go to the calibration set with the pattern named; shipped edits get harvested in
batch (the corpus carries the procedure); and any change to the system itself gets
regression-checked against the calibration set before it is trusted. First-party gold outranks
the third-party corpus, which outranks the guide's recipes. The site guide carries the full
routing (for ECXC: `docs/content-guide.md`, "How the system learns").

## 2. The exemplar library

The primary style control. Each pair shows the slop version and the on-voice version of the same
idea. Each site adds its own pairs in its local `content-guide.md`. The off-voice halves sit in a
fenced block so Vale skips the banned words they carry.

```
Off-voice (AI or program marketing): "East Community Nordic offers a comprehensive summer training
experience that empowers young athletes to navigate their journey toward elite Nordic skiing
performance, fostering a vibrant community of passionate skiers."

Off-voice: "Whether you're a beginner or a seasoned racer, our experienced volunteer coaches
provide expert guidance in a supportive environment, helping you take your skiing to the next level."
```

On-voice (a coach): "We run, ride mountain bikes, and roller-ski together through the summer.
Tuesday evenings we usually meet at the Service High parking lot. Most weeks include one strength
session when the gym is open."

On-voice: "Returning racers and first-summer kids both come. The pace is whatever the group can
hold together. Bring trail shoes, a water bottle, and bug spray."

## 3. The Signs-of-AI-writing catalog

The full set, sourced from Wikipedia's "Signs of AI writing" page and the user's standard. It lives
in a fenced block so Vale skips it.

```
Vocabulary to skip: delve, dive into, navigate (as metaphor), unlock, embark, foster, cultivate,
empower, leverage, harness, unpack, underscore, bolster, shed light on, pave the way, robust,
comprehensive, vibrant, dynamic, seamless, holistic, intricate, nuanced (as empty praise),
multifaceted, journey (as metaphor), passion, passionate, vital, crucial, essential, pivotal,
transformative, groundbreaking, cutting-edge, innovative, foundational, testament.

Constructions to skip: "It's not just X. It's Y." and every negative-parallelism form;
"Whether you're a beginner or a seasoned racer..."; "More than just..."; "In today's world...";
"It's worth noting / It's important to note"; "When it comes to / At its core / At the end of the
day"; "Join us as we... / Discover the joy of..."; "Take it to the next level"; opening with a
rhetorical question; closing with a motivational tag; sentences ending in an "-ing" editorial tag.

Structural patterns to skip: three-item lists where two or four fit equally; stacked parallel
sentence openings; every paragraph ending on a punchy line; paragraphs all the same length;
decorative em-dashes; excessive bolding; "Bold term: explanation" list formatting; bullets for
content that reads better as prose; closing summaries.

Tonal patterns to skip: promotional or tourism-website tone; performative enthusiasm; unsolicited
reassurance; phrases that promise standards of care or safety guarantees.

Wikipedia adds, beyond the user's list: copula avoidance (swapping plain is/are for fancier
being-verbs), formulaic upbeat conclusion sections, and vague attribution openers.
```

## 4. The rubric

Audience-first, with hard gates that override the score.

Hard gates. Any hit blocks publish, whatever the score:
- A banned word or phrase from the catalog (also caught by Vale).
- An unverified or false factual claim, a false implication carried by the framing (true
  sentences can still assert a falsehood together), or fabricated social proof.
- A safety or standard-of-care promise that carries legal risk.
- A cost misstatement, for sites where cost is a fact (training is free; donations optional).

Scored dimensions. Each scores 0 to 5, weighted, then normalized to 100:

| Dimension | Weight |
|---|---|
| Audience fit | x3 |
| Concreteness and local specificity | x2 |
| Voice fidelity | x2 |
| AI-tell freedom | x2 |
| Cadence and burstiness | x1 |
| Structure and scannability | x1 |
| Key-fact and next-step clarity | x1 |

The weights sum to twelve sub-scores. Maximum raw score is sixty. Normalized score is the raw score
times 100 divided by 60.

Scoring is on-request only. A review's default output is the hard-gate status plus a findings
list ordered by edit cost; the band and number appear only when the user asks for a score. When
scored, the band is the verdict and the number a secondary signal:
- Publish at 80 or above, with no hard-gate hit.
- Hold from 60 to 79. One revision pass, then re-score.
- Redraft below 60. Return to the brief.

Cadence and AI-tell freedom are inputs, never gates. Only the four hard gates block.

## 5. Per-dimension level anchors

What a 0, a 1, a 3, and a 5 look like, so a score means the same thing across sessions.

Audience fit:
- 5: speaks to each audience the site names at once, answers their real questions, reads at a level
  that fits each, respects where they read it.
- 3: serves one named audience well and the others thinly, mostly answers the real questions.
- 1: generic, addresses no specific reader, misses the questions they actually have.
- 0: wrong audience, an institutional or marketing voice.

Concreteness and local specificity:
- 5: names real places, dates, workouts, gear, cost, with nothing abstract.
- 3: some specifics, some filler abstraction.
- 1: mostly abstract, few real details.
- 0: brochure copy, no real details.

Voice fidelity:
- 5: the site's voice throughout, as its content guide sets it, matches the guide.
- 3: mostly on-voice with a few off-register lines.
- 1: a corporate or cheerleader voice creeping in.
- 0: an institutional or marketing voice throughout.

AI-tell freedom:
- 5: clean against the catalog.
- 3: one or two tells.
- 1: several tells.
- 0: saturated with tells.

Cadence and burstiness:
- 5: varied sentence and paragraph length, no low-burstiness flag from the sweep.
- 3: some variation, one flat stretch.
- 1: uniform cadence, the sweep flags low burstiness.
- 0: metronomic.

Structure and scannability:
- 5: clear headings, short paragraphs, tables or bullets where they earn their place.
- 3: readable, a wall in places.
- 1: poor structure, hard to scan.
- 0: an unstructured block.

Key-fact and next-step clarity:
- 5: cost, schedule, safety, sign-up clear, with an obvious next step where relevant.
- 3: most facts clear, the next step vague.
- 1: key facts missing or buried.
- 0: misleading on a key fact.

## 6. The self-check before delivering

1. Read it out loud. Anything that sounds like a school brochure or a tourism page gets rewritten.
2. Search for the banned vocabulary and the negative-parallelism frame.
3. Scan for em dashes. For each, confirm it does work a comma, period, or parentheses cannot. If
   not, replace it.
4. Check for sentences ending in an "-ing" editorial tag.
5. Check for participial and formal-connector openers, and for paragraphs that restate themselves.

## 7. The calibration gold set

Re-anchor scoring against these from time to time, so the same piece lands in the same band. The
slop sample sits in a fenced block because it carries banned words.

Sample A, expected band Publish (about 88):

"Summer training starts the first week of June. We meet Tuesday and Thursday evenings at the Service
High parking lot, plus a Saturday morning long session. Most weeks we run, roller-ski, or ride
mountain bikes, and we add one strength session when the gym is open. Bring trail shoes, a water
bottle, and bug spray. Training is free. If you have questions, reach a coach through the contact
form."

Sample B, expected band Redraft (about 40):

```
"East Community Nordic is a vibrant, comprehensive program that empowers passionate young athletes
to embark on a transformative journey. Whether you're a beginner or a seasoned racer, our dedicated
coaches foster a dynamic environment. It's not just training. It's a community. Take your skiing to
the next level. Your summer starts here."
```
