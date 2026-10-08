package tellscan

import (
	"fmt"
	"regexp"
	"strings"
)

// trailingHingeRe matches a comma followed by a subordinator or relative
// word that hangs a reason, consequence, or cross-reference off the end of a
// main clause. The coordinators "and", "but", "or", and "for" are left out on
// purpose: they join clauses rather than trail one, and the hinged-pair
// measure already counts them.
//
// The idiom ", as well as" is also left out: it coordinates a second item
// and trails nothing, though its "as" matches the alternation.
var trailingHingeRe = regexp.MustCompile(`,\s+(?:so that|so|since|because|which|while|as|where|whereas|although|though)\s`)

var asWellAsRe = regexp.MustCompile(`^,\s+as\s+well\s+as\s`)

// minHingeRun is the number of consecutive trailing-hinge sentences in one
// paragraph that makes a run. One or two read as ordinary prose; the tell is
// the repetition (Geoff, 2026-10-07).
const minHingeRun = 3

// minLeadWords is the fewest words a main clause must carry before its hinge
// comma, so an introductory phrase ("Since then, ...") never reads as a tail.
const minLeadWords = 3

// uniformParagraphCV is the per-paragraph sentence-length coefficient of
// variation below which a paragraph of four or more sentences reads as
// metronomic. It is tighter than flatCadenceCV because one paragraph has far
// fewer sentences to average over than a whole document. The signal is a
// count, never a finding: four-sentence reference paragraphs trip it too
// often to grade on alone.
const uniformParagraphCV = 0.25

var (
	frontmatterRe = regexp.MustCompile(`\A---\n(?s:.*?)\n---\n`)
	nonProseLine  = regexp.MustCompile(`^\s*(?:\||<)`)
)

// paragraph is one block of running prose and the 1-based line it starts on.
type paragraph struct {
	line      int
	text      string
	sentences []string
}

// proseParagraphs splits prose into paragraphs under the same selector the
// docs-register measures use (headings and list items removed), and also
// drops front matter, table rows, and HTML lines. A whitespace-only line
// ends a paragraph, since blanked code leaves such lines behind.
func proseParagraphs(prose string) []paragraph {
	prose = frontmatterRe.ReplaceAllStringFunc(prose, func(m string) string {
		return strings.Repeat("\n", strings.Count(m, "\n"))
	})
	var out []paragraph
	var buf []string
	start := 0
	flush := func() {
		if len(buf) > 0 {
			text := strings.Join(buf, "\n")
			out = append(out, paragraph{line: start, text: text, sentences: splitSentences(text)})
		}
		buf = nil
	}
	for i, line := range strings.Split(proseOnly(prose), "\n") {
		if strings.TrimSpace(line) == "" || nonProseLine.MatchString(line) {
			flush()
			continue
		}
		if len(buf) == 0 {
			start = i + 1
		}
		buf = append(buf, line)
	}
	flush()
	return out
}

// hasTrailingHinge reports whether sentence hangs a comma-introduced
// subordinate tail off a main clause of at least minLeadWords words.
func hasTrailingHinge(sentence string) bool {
	for _, loc := range trailingHingeRe.FindAllStringIndex(sentence, -1) {
		if asWellAsRe.MatchString(sentence[loc[0]:]) {
			continue
		}
		if len(strings.Fields(sentence[:loc[0]])) >= minLeadWords {
			return true
		}
	}
	return false
}

// longestHingeRun returns the length of the longest run of consecutive
// trailing-hinge sentences in sentences.
func longestHingeRun(sentences []string) int {
	best, run := 0, 0
	for _, s := range sentences {
		if !hasTrailingHinge(s) {
			run = 0
			continue
		}
		run++
		best = max(best, run)
	}
	return best
}

// paragraphFindings returns the trailing-hinge-run findings for paras, each
// gating when gate is set, and the number of uniform-length paragraphs.
func paragraphFindings(paras []paragraph, gate bool) (out []Finding, uniform int) {
	for _, p := range paras {
		cv := cadenceCV(p.sentences)
		if run := longestHingeRun(p.sentences); run >= minHingeRun {
			out = append(out, Finding{
				Check:   "trailing-hinge-run",
				Line:    p.line,
				Excerpt: fmt.Sprintf("%d consecutive sentences end in a comma-hinged tail (paragraph sentence-length CV %.2f)", run, cv),
				Gate:    gate,
			})
		}
		if len(p.sentences) >= 4 && cv < uniformParagraphCV {
			uniform++
		}
	}
	return out, uniform
}
