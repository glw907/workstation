---
name: style-review
description: >
  Periodic review of recent ASC blog posts against the content style guide, with edit pattern
  analysis when AI first drafts are available in the draft log. Use this skill when the user
  wants to review a batch of recent posts against the style guide, analyze editing patterns
  across posts, evolve the style guide based on accumulated writing data, or do a voice audit.
  Trigger on "style review", "voice audit", "review recent posts against the guide", "update
  the style guide from recent posts", "time for a style check", or when the user mentions
  they've published several new posts and want to check voice consistency.
---

# Style Review Skill

Periodic review of Alaska Sailing Club blog posts against `docs/site/content-style-guide.md`.
Run after every 4–5 new posts, or whenever the author wants a check. Analyzes the batch as a
corpus to identify voice patterns, style guide violations, and opportunities to evolve the guide.

## Draft Log

AI first drafts are appended to `docs/site/draft-log.md` before the author edits them. The file
is append-only with a simple structure:

```markdown
# Draft Log

---

## 2026-02-27 — Welcome to the New Website

[full AI draft text]

---

## 2026-03-10 — Racing Pages Overview

[full AI draft text]

---
```

Not every post will have a draft log entry. Some posts the author writes from scratch. The skill
works with whatever pairs exist and reviews unpaired posts on their own.

## Workflow

### Step 1: Gather the Corpus

1. **Read the style guide.** Read `docs/site/content-style-guide.md` in full. Internalize the
   blog post rules (Tone and Voice, Sentence Structure, What to Avoid) and the relevant
   Primary/Secondary Pages rules (Punctuation, What to Avoid). Do this before reading any posts.

2. **Identify the posts to review.** Ask the author which posts, or look for posts published since
   the last review. A typical batch is 4–5 posts. Confirm the set before proceeding.

3. **Read the draft log.** Read `docs/site/draft-log.md` and match entries to the posts being
   reviewed by title and date. Note which posts have drafts and which don't.

4. **Read all posts and their drafts.** Read the full corpus before producing any analysis. You
   need everything in context to see patterns across posts, not just within a single post.

### Step 2: Corpus Voice Analysis

Before checking individual violations, characterize the voice of the batch. This is the part
a per-post review can't do.

**Sentence-level rhythm.** How does the author move between ideas? What connective devices appear?
What's the typical sentence length? How do paragraphs open and close?

**What's absent.** Which "What to Avoid" patterns are actually absent from the posts? (Confirms
the guide is working.) Which patterns not in the avoid list are also absent? (Possible candidates
for the avoid list, or natural voice traits worth documenting.)

**Consistency across posts.** Are there voice characteristics that appear in some posts but not
others? Inconsistency might mean a guest author, a different content type, or a pattern the
author is still developing.

**Comparison to the style guide's positive descriptions.** Does the Tone and Voice section
accurately describe what these posts actually sound like? Where is the guide precise and where
is it vague enough that an AI could misinterpret it?

Write this analysis up as a narrative summary. Keep it concrete — quote from the posts.

### Step 3: Post Issues

Patterns in the reviewed posts that conflict with the style guide. Group by pattern rather than
by post (if three posts all have the same issue, that's one finding, not three).

For each issue:
- **Quote the text** from the post(s)
- **Name the rule** with enough context to find it in the guide
- **Suggest a fix** or note if cutting is the right move
- **Frequency** — how many of the reviewed posts contain this pattern

Skip nitpicks. Focus on patterns that a reader would notice or that indicate the guide isn't
being followed consistently.

### Step 4: Edit Patterns (only for posts with draft log entries)

For each post that has a matching draft log entry, diff the AI draft against the published
version. Then look across all the diffs for recurring changes.

**What was cut.** Sentences or phrases the author removed entirely. Categorize: framing sentences,
benefit restatements, editorializing, hedging, meta-commentary, filler, etc.

**What was rewritten.** Constructions the author changed. Show before → after. Look for consistent
transformations: formal → casual, abstract → concrete, two sentences → one, etc.

**What was left alone.** Patterns from the AI draft that survived editing. Positive signal that
the guide works for these.

**What was added.** Content the author wrote from scratch that wasn't in the AI draft. Reveals
voice characteristics the AI isn't producing.

After cataloging, identify **candidate rules** — edit patterns consistent enough to become style
guide entries. For each:

- State the pattern as it would appear in the style guide
- Provide examples from the diffs
- Rate confidence:
  - **High** — appeared in 3+ diffs, or appeared in 2 diffs and is clearly a voice issue
  - **Medium** — appeared in 2 diffs, suggestive but not definitive
  - **Low** — appeared once, might be contextual

### Step 5: Proposed Style Guide Updates

Combine findings from Steps 2–4 into concrete proposals. Two types:

**New rules** (from high-confidence edit patterns or consistent post issues):
- Draft the text as it would appear in the style guide
- Specify where it goes (which section)
- Use the guide's formatting conventions (bold pattern name, explanation, ✗/✓ examples)

**Revisions to existing descriptions** (from the corpus voice analysis):
- If the Tone and Voice or Sentence Structure sections don't accurately describe what the
  posts actually sound like, propose revised text
- Show the current text and the proposed replacement
- Explain what the current text gets wrong or misses

Present these as a list the author can accept, reject, or modify. Don't rewrite sections
that are working. The goal is incremental convergence, not periodic overhauls.

## Principles

**The author's edits are ground truth.** When the author changes something, the author is right.
The question is whether the style guide should have prevented the issue.

**Be conservative about new rules.** Every rule constrains future drafting. Wait for repetition.
A pattern that appears in one diff is an observation. A pattern that appears in three diffs is
a rule.

**Positive descriptions matter more than anti-patterns.** The style guide's biggest leverage is
in accurately describing the voice so that AI drafts are closer to right on the first pass. An
expanded avoid list helps, but precise positive descriptions prevent more problems.

**The guide should get shorter over time, not longer.** As positive descriptions get more precise,
specific anti-pattern rules can be consolidated or removed. A long avoid list is a sign that the
positive descriptions aren't doing their job.
