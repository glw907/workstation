package tellscan

import (
	"regexp"
	"strings"
)

// appositiveStackRe matches a comma-led appositive noun phrase, opened by an
// article or a possessive, and a later ", which" or ", who" in the same
// sentence: ", a name from the vocabulary, which". The relative pronoun's
// antecedent is then ambiguous between the appositive and the noun it renames
// (Geoff, 2026-10-07).
var appositiveStackRe = regexp.MustCompile(
	`,\s+(?:a|an|the|its|their|his|her|our|your|[A-Za-z]+(?:'|’)s)\s+.+?,\s+(?:which|who)\s`)

// serialListRe matches the comma-coordinator that closes a serial list. A
// comma-led noun phrase followed by one is a list item, not an appositive.
var serialListRe = regexp.MustCompile(`,\s+(?:and|or)\s`)

// parentheticalRe matches one level of parenthesized text, which may hold a
// list of its own ("(a colonless offset, a lowercase Z)").
var parentheticalRe = regexp.MustCompile(`\([^()]*\)`)

// introLeadRe matches a clause segment that opens with a preposition or a
// subordinator. Such a segment before the comma is an introductory phrase
// ("In the admin, a theme reaches ..."), so the comma-led phrase after it is
// the main clause's subject, not an appositive.
var introLeadRe = regexp.MustCompile(`(?i)^(?:about|after|against|along|although|among|as|at|because|before|beside|besides|between|beyond|by|despite|during|except|for|from|given|if|in|inside|instead|like|on|once|outside|over|since|through|throughout|to|under|unless|unlike|until|upon|when|whenever|where|whereas|while|with|within|without)\s`)

// hasAppositiveStack reports whether sentence renames a noun in a comma
// appositive and then hangs a which or who clause after it. Parenthesized
// text is dropped first. The clause before the appositive must carry at least
// minLeadWords words and must not open with a preposition or subordinator, so
// an introductory phrase never reads as the renamed noun, and a later ", and"
// or ", or" marks a serial list rather than an appositive.
func hasAppositiveStack(sentence string) bool {
	sentence = parentheticalRe.ReplaceAllString(sentence, "")
	for _, loc := range appositiveStackRe.FindAllStringIndex(sentence, -1) {
		lead := sentence[:loc[0]]
		if len(strings.Fields(lead)) < minLeadWords {
			continue
		}
		segment := strings.TrimSpace(lead[strings.LastIndex(lead, ",")+1:])
		if introLeadRe.MatchString(segment) || serialListRe.MatchString(sentence[loc[0]:]) {
			continue
		}
		return true
	}
	return false
}

// appositiveFindings returns one appositive-stack finding per offending
// sentence in paras, anchored to the line the sentence starts on, each
// gating when gate is set.
func appositiveFindings(paras []paragraph, gate bool) []Finding {
	var out []Finding
	for _, p := range paras {
		start := 0
		ends := sentenceEnd.FindAllStringIndex(p.text, -1)
		ends = append(ends, []int{len(p.text), len(p.text)})
		for _, end := range ends {
			raw := p.text[start:end[1]]
			offset := start + len(raw) - len(strings.TrimLeft(raw, " \t\n"))
			start = end[1]
			sentence := strings.Join(strings.Fields(mdDecoration.ReplaceAllString(raw, "")), " ")
			if !hasAppositiveStack(sentence) {
				continue
			}
			out = append(out, Finding{
				Check:   "appositive-stack",
				Line:    p.line + strings.Count(p.text[:offset], "\n"),
				Excerpt: clip(sentence),
				Gate:    gate,
			})
		}
	}
	return out
}
