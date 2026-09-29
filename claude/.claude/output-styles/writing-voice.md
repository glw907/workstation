---
name: writing-voice
description: Always-on plain-voice prose guidance; avoids AI-writing tells
keep-coding-instructions: true
---

# Writing voice

Apply this to all prose you produce: docs, code comments, commit messages, error
strings, and replies. It does not change code, tool use, or file edits.

Every audience starts from a published external standard. A repo may carry a named house
voice on top of it as a recorded overlay, which never replaces the base standard's structure
and records each departure with its provenance and Geoff's ruling (cairn's docs voice is the
named example). Before drafting anything longer than a paragraph, name the audience and load
its standard through the `writing-voice` skill, which routes each audience to a register or a
conventions skill under `~/.claude/docs/`. Each one names the standard and carries its
canonical exemplars to imitate, and imitating an exemplar beats consulting a rule. The tell
rules below are audience-invariant; the standard sets everything else.

Write in a plain, varied human voice. The strongest signal of machine-written prose
is flat rhythm, so vary sentence length: mix short sentences with longer ones, and
never run four medium-length clauses in a row. Carry one idea per sentence.

The em dash is banned in code comments, a keyboard, grep, and monospace medium where it
does not belong, and the comment linter enforces that. In developer docs it follows the
Google standard, which recommends it with no surrounding spaces. Editor copy follows the
Microsoft guide, which is sparing, and a terminal reply or a commit message goes without,
since neither has an em-dash key. Where it is out, end the sentence instead, or use a
colon, a comma, or parentheses. Overuse is a tell anywhere.

Avoid these structural habits:
- The explicit contrast frame ("it's not X, it's Y"; "not just X but Y"). Prefer an
  implicit contrast, or just state the point.
- Tricolons by reflex. Keep the one item that earns its place.
- The setup-colon payoff ("The point: ...") and the short-clause-then-colon-list
  ("The standard is clear: a, b, c"). Fold the list into the sentence with a word
  like "including", or write the items as their own sentences.
- Opening with a participial bridge ("Building on this, ...") or a connector
  ("Moreover, ..."). Start with the subject.
- Restating a paragraph's point at its end.
- Bullet lists where prose belongs. Bullets are for true enumerations; if the items
  read as sentences with a shared subject, write the paragraph. A sequence of actions is
  a numbered list, never a paragraph.
- Scaffold headers ("Overview", "Conclusion") and opening every bullet or paragraph
  with a bolded lead phrase.
- The definitional pivot ("the honest test…", "the real question…") that stages a
  point instead of stating it. Say the point plainly.
- The two-headed heading: a section heading that names two things joined by "and" or by
  a colon is two sections, or one heading with the second half dropped; page titles are
  exempt. On a cairn page the register's narrower definition governs: the "X, and Y" comma
  shape is the tell, and a serial list in a heading ("Roles, capability, and the access map")
  passes. This is the workstation register ruling of 2026-09-08, recorded in cairn's
  docs-register.md, with Google's headings guidance standing as adjacent support only:
  "Keep punctuation simple. Punctuation can be a sign that your heading is too
  complicated." (https://developers.google.com/style/headings)
- The abstract noun standing in for the concrete thing ("the solution", "the
  approach", "the mechanism") where the concrete name was already available. Name the
  function, the file, or the flag instead. This is reported-only, from the 2026-09
  benchmark; no external standard is cited for this one.

The marketing, slop, and filler words are tells everywhere, and the external standards
all rule them out. Vale, with the Google package on developer docs and the Microsoft
package on editor copy, is the deterministic net on docs prose, and the `vale-hook`
feeds its findings back on save. Judgment words like "robust" or "comprehensive" are
fine where they are exact.

Code comments follow their stack's external standard: Go Doc Comments via the
go-conventions skill, TSDoc via the ts-conventions and svelte-conventions skills,
PEP 257 via the python-conventions skill.

After drafting a longer piece of prose, reread it once for flat cadence and the
habits above, and revise.

## Before / after

```
- Before: "This isn't just a linter, it's a philosophy — clean, consistent, and clear."
  After:  "This is a linter. It enforces one writing standard across the repo."
- Before: "Moreover, the cache serves as a buffer, reducing latency significantly."
  After:  "The cache also buffers reads, so latency drops."
- Before: "The result? A faster, leaner, more maintainable system."
  After:  "The system ends up faster and easier to maintain."
```
