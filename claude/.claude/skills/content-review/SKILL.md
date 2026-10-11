---
name: content-review
description: "Gate-check website content (pages, posts, form copy): the four hard gates plus findings ordered by edit cost. Scores only on request. Use after drafting or editing site content, before committing, or when the user says \"/content-cleanup\", \"clean up this content\", \"check for AI tells\", \"editorial pass\", \"review this page\", \"score this copy\". For website content only. Takes a file path."
context: fork
---

# Content Review

Gate-check a website-content file and report findings ordered by edit cost. Run this as a fresh
review of the file, not as a continuation of the context that drafted it. Independent review is
the reliable form; self-critique in the drafting context is not.

Load the shared method at `~/.claude/docs/web-content-method.md` (the gates, the catalog, the
rubric for when a score is requested) and the site's `docs/content-guide.md` (the load-bearing
rules, budgets, and recipes the draft was written against). When the site has no
`docs/content-guide.md`, run on the shared method alone, skip step 4, and open the report by
saying the site guide was absent.

## Steps

1. **Read** the target file, the site guide (when present), and the method. If the piece has a brief in
   `docs/content-briefs/`, read it; brief facts are the claim baseline.

2. **Run Vale** on the file for the machine signals (the site's `.vale.ini` selects the content
   baseline): `vale <file>`
   It reports banned words, structural tells, and the advisory sweep. Inputs, never
   the verdict.

3. **Check the four hard gates:** a banned word or phrase, an unverified or false claim
   (check stated facts against the brief where one exists, and check implications too: read as
   the most knowledgeable, least charitable reader and flag any frame that asserts a falsehood
   no single sentence states; verify externally checkable third-party claims online against a
   primary, careful source rather than model memory, even when the user supplied the fact), a
   safety or standard-of-care promise, a cost misstatement. Any hit blocks publish. An `[ASK]`
   marker is a tracked gap, not a gate hit; list the markers so none ships unnoticed.

4. **Check the site guide's load-bearing rules and budgets:** facts said once, people doing
   things, containers within budget, no tagline endings.

5. **Report, gates first.** Lead with the gate status and the `[ASK]` inventory. Then the
   findings, ordered by edit cost (cheapest fix first). Each finding quotes the sentence, names
   the specific rule or pattern, proposes a replacement, and gives a one-line reason. If nothing
   is flagged, say so.

6. **Score only on request.** When the user asks for a score, apply the method's rubric (seven
   dimensions, level anchors, gold-set calibration) and report the band first, the number second.

## Hard rules

- The report is the whole job: this skill edits nothing. The caller decides which proposed replacements to apply.
- Gates and findings are the default deliverable; the score appears only when asked for.
- Cite a named rule or pattern or leave the sentence alone. No "improved the flow" rewrites.
- Re-check each proposed replacement against the catalog before presenting it.
- This is website content. Do not apply it to code, docs, specs, or commits.
