# The docs-register cadence measures

This is the canonical definition of the two cadence measures the docs-register profile
reports: `hinged_pair_share` and `short_sentence_share`. It exists so a second
implementation, or a reviewer reading a number, has one place to check against instead of
reverse-engineering the scanner's regexes.

`~/Projects/cairn-cms/scripts/checks/measure-prose.mjs` is a consumer, not a second
definition. Where it diverges from this document, this document is the reference, and
cairn's own pass conforms `measure-prose.mjs` to it or retires the script in favor of
`tellgrader`. Every known divergence is named in "Divergences from cairn's
measure-prose.mjs" below.

## The sentence splitter

`internal/tellscan/cadence.go`'s `splitSentences` is the splitter, unchanged for the
docs-register measures: markdown decoration (heading markers, bullet and numbered-list
markers, and `**`/`__` emphasis markers) is stripped first, each paragraph (text between
blank lines) is flattened to one line, and the flattened text is split on runs of `.`,
`!`, or `?` followed by whitespace or end of string. No sentence is dropped for being
short. "Between blank lines" means the literal two-newline run `\n\n`: a line holding
only spaces does not split a paragraph, since it is not itself an empty line.

## The selector: prose

The measures grade `prose` only: paragraphs of running text, never a heading and never a
list item. The selector, `proseOnly`, blanks two kinds of line before the sentence
splitter runs, preserving each line's newline so line numbers still map to the input:

- A **heading line**, recognized by `headingRe`: a line starting with one to six `#`
  markers followed by whitespace, optionally indented. A heading is not a sentence, so its
  whole line is removed, not merely its `#` marker.
- A **list item**, recognized the same way the scanner's other checks recognize one, by
  `bulletRe` (a leading `-`, `*`, or `+` marker) or `numberedListRe` (a leading `1.`-style
  marker), together with every line that continues it. A **continuation line**, matched by
  `continuationRe`, is an indented, non-blank line (leading spaces or tabs followed by a
  non-space character) immediately following a marker line or another continuation line;
  the run ends at a blank line or a non-indented line. A wrapped bullet's second and later
  lines are removed along with its marker line, so neither contributes a sentence.

Because headings and list items are removed entirely, the denominator the two shares divide
by is the **prose-only sentence count**: the number of sentences `splitSentences` returns
after `proseOnly` runs, reported as the JSON `measures.sentences` field. This equals
`CadenceCV`'s own sentence count only on a document with no headings and no list items;
otherwise `CadenceCV` counts more sentences than the docs-register measures do, because it
runs over the whole document (headings and bullets included) while the measures run over
prose alone.

## The hinged-pair rule

A sentence counts as a hinged pair when it joins two clauses by any of:

- a comma followed by one of the coordinating conjunctions `and`, `but`, `or`, `so`, `yet`,
  `nor`, or `for`, subject to the serial-list exclusion below,
- a colon or a semicolon, anywhere in the sentence,
- a spaced dash (a hyphen, en dash, or em dash surrounded by spaces), or
- a chain of relative clauses: two or more occurrences, case-sensitive, of the exact words
  `which` or `who` (in either combination) in the same sentence. A single `which` or `who`
  is not a hinge; two or more are.

**The serial-list exclusion.** A comma-plus-coordinator match does not count as a hinge
when an earlier comma already appears in the same sentence. "The plan covered a, b, and c."
closes a serial list at its final item; the comma before `and` is the list's own separator,
not a hinge. "It ran, and the gate passed." has no earlier comma, so its `, and` joins two
independent clauses and counts. The exclusion applies to the whole coordinator set above,
not only `and`.

**This definition is unsettled.** It moved twice during the proposal that preceded this
scanner, and no number built on it gates anything: it carries no band, and a `fix` verdict
never rests on it alone. Treat a change to this rule as a change to a report-only figure,
not to a check.

## The short-sentence rule

A sentence counts as short when it has fewer than eight words, counted the same way
`cadenceCV` counts them: `strings.Fields` on the flattened sentence text.

## The unit: fractions, not percentages

Both shares are fractions in `[0, 1]`, and the report states this explicitly with a
`"unit": "fraction"` field. `hinged_pair_share: 0.0` on a document with no hinged pair is
reported, not omitted: `Measures` is a pointer field, present or absent as a unit, so a
legitimate zero share never reads as "not measured."

## Divergences from cairn's measure-prose.mjs

This section compares the measured *pipeline*, `Scan`'s prose-preparation steps feeding
`measureShares`, against `measure-prose.mjs` end to end, not either implementation's
individual functions in isolation.

`measure-prose.mjs` (`/var/home/glw907/Projects/cairn-cms/scripts/checks/measure-prose.mjs`)
is a separate implementation, not generated from this one. Every place it diverges from the
definition above:

- **Unit.** `measure-prose.mjs` emits integer percentages (`hingePct: 31`, `shortPct: 12`),
  rounded from `100 * count / n`. `tellgrader` emits fractions in `[0, 1]`
  (`hinged_pair_share: 0.31`).
- **The splitter drops short sentences.** `measure-prose.mjs`'s `splitSentences` filters out
  any chunk under three words (`.filter((x) => x.split(/\s+/).length >= 3)`). `tellgrader`'s
  `splitSentences` drops no sentence for being short, so the two denominators differ on any
  document containing a sub-three-word fragment.
- **The sentence-boundary test.** `measure-prose.mjs`'s `splitSentences` splits only at
  ``(?<=[.!?])\s+(?=[A-Z"'(`])``: a sentence-ending mark followed by whitespace counts as a
  boundary only when the next character is a capital letter or an opening quote or
  parenthesis. `tellgrader`'s `sentenceEnd` is `[.!?]+(?:\s+|$)`, with no such lookahead, so
  it splits on every run of `.`, `!`, or `?` followed by whitespace or end of string
  regardless of what follows. "Version 1.0. the gate ran fine here today." is one sentence
  under `measure-prose.mjs` (lowercase `the` fails its lookahead) and two under `tellgrader`
  (`1.0.` alone satisfies `sentenceEnd`).
- **The coordinator set.** `measure-prose.mjs` splits the coordinator test across two
  patterns: `HINGE_SUB` unconditionally hinges a comma followed by `but`, `so`, `yet`,
  `which`, `where`, `while`, `because`, `since`, `although`, `though`, or `as` (no
  serial-list exclusion applies to these), while `HINGE_AND` hinges a comma followed by
  `and` or `or`, with the serial-list exclusion. It never matches `nor` or `for`.
  `tellgrader` hinges a single coordinator set, `and`, `but`, `or`, `so`, `yet`, `nor`, `for`,
  with the serial-list exclusion applying uniformly to all seven.
- **The colon/semicolon test.** `measure-prose.mjs` requires a colon or semicolon followed
  by whitespace and a non-space character (`[;:]\s+\S`), so a colon at the end of a sentence
  or followed directly by a non-whitespace character does not count. `tellgrader` hinges on
  any colon or semicolon anywhere in the sentence (`strings.ContainsAny(sentence, ":;")`).
- **The relative-clause rule.** `measure-prose.mjs` has no "two or more" chain rule: it
  hinges unconditionally on a single comma followed by `which` or `where` (via `HINGE_SUB`),
  or on `, which` / `, that` followed by two more words. `tellgrader` requires two or more
  occurrences of `which` or `who` (case-sensitive, not `where` or `that`) anywhere in the
  sentence, with no comma required and no single occurrence counted.
- **The continuation-indent test.** `measure-prose.mjs` recognizes a list item's wrapped
  continuation line with `^\s{2,}\S`, requiring two or more leading spaces. `tellgrader`'s
  `continuationRe` is `^[ \t]+\S`, matching a single leading space or tab. A line indented by
  exactly one space after a bullet is a continuation under `tellgrader` (blanked out of the
  prose selector, along with its marker line) and a new prose block under `measure-prose.mjs`
  (contributing its own sentence). This is a choice to revisit if the two are meant to
  converge, not a settled difference.
- **Emphasis stripping.** `tellgrader`'s `mdDecoration` strips both `**` and `__` before
  counting words or splitting sentences. `measure-prose.mjs` strips only `**`
  (`text.replace(/\*\*([^*]+)\*\*/g, '$1')`); a `__bold__` span survives with its markers
  intact.
- **Selector differences that remain after the heading and list-continuation fix.** Fenced
  code is not a divergence: `Scan` blanks it (`blankFencedCode`, `scan.go:123`) before the
  prose-only selector or the measures ever run, and `measure-prose.mjs` strips it too. Inline
  code is a divergence in kind rather than in scope: both implementations remove the span,
  but `tellgrader` blanks it to whitespace while `measure-prose.mjs` substitutes the literal
  word `Code` (``text.replace(/`[^`]*`/g, 'Code')``, line ~116), so the word contributes to
  `measure-prose.mjs`'s word and sentence-length counts and not to `tellgrader`'s.
  `measure-prose.mjs` also strips tables and link targets before building its blocks, neither
  of which `tellgrader`'s `proseOnly` or `splitSentences` strip, and its list-item
  recognition (`^\s*(?:[-*]|\d+\.)\s+`) does not match a `+` bullet, where `tellgrader`'s
  `bulletRe` does.

The serial-list exclusion is a divergence for every coordinator but `and`/`or`.
`measure-prose.mjs` applies the exclusion only within `HINGE_AND`; its `HINGE_SUB` pattern
(`but`, `so`, `yet`, and the subordinators) hinges on the first match regardless of an
earlier comma. `tellgrader` applies the exclusion to its whole coordinator set. The two
implementations agree only on the `and`/`or` case: "It listed a, b, and c." excludes under
both, but "It listed a, b, but the plan failed." hinges under `measure-prose.mjs` and does
not hinge under `tellgrader`, because the earlier comma excludes it there.

## The trailing-hinge run (a gating tell)

**Provenance.** Geoff, 2026-10-07, ruling on a cairn docs paragraph he called "really awkward AI
cadence": the pattern, "or at least excessive, repetitive use of it", lives in the writing
infrastructure. The `hinged_pair_share` measure above missed most of that paragraph and gates
nothing, so this check is separate from it.

**The tell.** Sentence after sentence carries one fact in a main clause, then a tail hung off the
end by a comma and a hinge word: a reason, a consequence, or a cross-reference. The sentences run
to about the same length, and none gives the reader a break. One such sentence is fine. The defect
is the run.

**The rule** (`internal/tellscan/hinge.go`):

- A sentence has a **trailing hinge** when it contains a comma, whitespace, and then one of `so
  that`, `so`, `since`, `because`, `which`, `while`, `as`, `where`, `whereas`, `although`, or
  `though`, followed by whitespace, and at least three words precede that comma. The three-word
  floor keeps an introductory clause ("Since then, ...") from reading as a tail. The coordinators
  `and`, `but`, `or`, and `for` are excluded on purpose. They join two clauses rather than trail
  one, and the hinged-pair measure already counts them. No appositive heuristic runs: telling
  ", the only X the Y names," from an introductory phrase takes a parser.
- A **trailing-hinge run** is three or more consecutive trailing-hinge sentences in one paragraph.
  A plain sentence between them resets the count, and a paragraph break ends it.
- **Paragraphs** come from the prose selector above (headings and list items removed), with front
  matter, table rows (a line starting with `|`), and HTML lines (starting with `<`) also dropped. A
  blank or whitespace-only line ends a paragraph. Sentences are `splitSentences`' own.
- The finding reports as `trailing-hinge-run` at the paragraph's first line. Its excerpt names the
  run length and the paragraph's sentence-length coefficient of variation.

**Gating.** The finding reports in every register. Under the docs-register profile it carries
`"gate": true`, and the CLI exits 2 after printing the report (1 stays a usage or read error). It
is the only gating tell. The `--hook` path forces the profile off, so the hook stays advisory.

**The uniform-paragraph count.** Alongside the run, `counts.uniform-paragraph` counts paragraphs of
four or more sentences whose sentence-length coefficient of variation falls below 0.25. It is a
count with no finding and no line, since four-sentence reference paragraphs trip it too often to
grade on alone.

**The fixtures.** `hinge_test.go` carries the flagged paragraph, which must trip, and Geoff's
accepted rewrite, which must not, plus single hinges, two-hinge runs, list items, introductory
clauses, and fenced code, none of which trip.

## The `~/.claude` symlink caveat

`~/.claude` is a symlink into this dotfiles repo, so a file edited through it resolves home
first and never walks into `~/.dotfiles`; a `.tellgrader.json` committed here does not
govern files edited that way.

## The report shape

```json
"profile": "docs-register",
"measures": {
  "unit": "fraction",
  "selector": "prose",
  "sentences": 148,
  "hinged_pair_share": 0.31,
  "short_sentence_share": 0.12
}
```

`sentences` counts the prose-only sentences the two shares are computed over, which can
differ from the report's top-level `sentences` field when the document contains headings or
list items.
