package tellscan

import "regexp"

type match struct {
	start, end int
}

// A check pairs a name with the patterns that detect it and the rule for
// when a hit is a violation rather than a neutral count. A nil violates
// func means the hit violates every register.
type check struct {
	name     string
	patterns []*regexp.Regexp
	violates func(Register) bool
}

func (c *check) find(s string) []match {
	var out []match
	for _, re := range c.patterns {
		for _, idx := range re.FindAllStringIndex(s, -1) {
			out = append(out, match{start: idx[0], end: idx[1]})
		}
	}
	return out
}

func res(exprs ...string) []*regexp.Regexp {
	out := make([]*regexp.Regexp, len(exprs))
	for i, e := range exprs {
		out[i] = regexp.MustCompile(e)
	}
	return out
}

var checks = []check{
	{
		name:     "em-dash",
		patterns: res(`\x{2014}`),
		violates: func(r Register) bool { return r.emDashBanned() },
	},
	{
		// Google recommends the em dash with no surrounding spaces, so a
		// spaced em dash is a violation even where the character is allowed.
		name:     "em-dash-spaced",
		patterns: res(`\s\x{2014}\s`),
		violates: func(r Register) bool { return !r.emDashBanned() },
	},
	{
		name: "contrast-frame",
		patterns: res(
			`(?i)\b(?:is|are|was|were)n['’]t (?:just |only |merely |simply |about )[^.!?\n]{1,50}?[,;]\s*(?:it['’]s|they['’]re|but|rather)`,
			`(?i)\bit['’]s not (?:just |only |merely |simply |about )?[^.!?\n]{1,50}?[,;]\s*(?:it['’]s|but)`,
			`(?i)\bnot only\b[^.!?\n]{1,80}?\bbut(?: also)?\b`,
			`(?i)\bless about\b[^.!?\n]{1,50}?\bmore about\b`,
			`(?i)\bnot (?:just|merely|simply) [^.!?\n]{1,50}?\bbut\b`,
		),
	},
	{
		name: "connector-opener",
		patterns: res(
			`(?m)(?:^[ \t]*|[.!?]\s+)(?:Moreover|Furthermore|Additionally|In addition|Notably|Importantly|Crucially|In essence|Essentially|Ultimately|In conclusion|In summary|Overall),?\s`,
			`(?m)(?:^[ \t]*|[.!?]\s+)(?:Building on|Leveraging|Harnessing|Drawing on|Diving into)\b`,
		),
	},
	{
		// The colonless patterns announce a payoff the way a setup colon
		// does, so they grade here rather than under a check of their own.
		name: "setup-colon",
		patterns: res(
			`(?m)^(?:The (?:point|result|goal|key|upshot|answer|takeaway|catch)|Bottom line|The best part|Here['’]s the (?:thing|catch|kicker))\s*:`,
			`\bThe (?:result|best part|catch|kicker)\?`,
			`\bThis matters because\b`,
			`\bThe (?:key|point|idea|insight|important thing) here is\b`,
			`(?i)\bat (?:its|their) core\b`,
			`\bThink of (?:it|this) as\b`,
			`\bThis is where [^.!?\n]{1,40} comes in\b`,
		),
	},
	{
		// Reinhart et al. (PNAS): present participial clauses run at
		// 527% of the 1.7-per-1000-words human rate in tuned models.
		name: "participial-tail",
		patterns: res(
			`,\s+(?:highlighting|emphasizing|ensuring|reflecting|symbolizing|contributing to|cultivating|fostering|encompassing|enhancing|signaling|reinforcing|shaping|driving|demonstrating|illustrating|cementing|solidifying|paving)\b`,
		),
	},
	{
		name: "assistant-voice",
		patterns: res(
			`(?i)\bI hope this helps\b`,
			`(?i)\bLet me know if\b`,
			`(?i)\bFeel free to\b`,
			`(?i)\bWould you like me to\b`,
			`(?i)\bIs there anything else\b`,
			`(?i)\b(?:Great|Excellent|Fantastic) question\b`,
			`(?i)\bI['’]d be happy to\b`,
			`(?i)\bas (?:an AI|a large language model)\b`,
			// Case-sensitive on purpose. A mid-sentence "certainly," is
			// ordinary English; the opener is the tell.
			`\b(?:Certainly|Absolutely)[!,]`,
		),
	},
	{
		name: "hedging-filler",
		patterns: res(
			`(?i)\bit(?:['’]s| is) (?:important|worth) (?:to note|noting)\b`,
			`(?i)\bit should be noted\b`,
			`(?i)\bneedless to say\b`,
		),
	},
	{
		name:     "scaffold-header",
		patterns: res(`(?mi)^#{1,6}\s*(?:Overview|Introduction|Conclusion|Summary|Final Thoughts)\s*$`),
	},
	{
		name:     "slop-hard",
		patterns: hardSlopPatterns,
	},
	{
		name:     "slop-soft",
		patterns: softSlopPatterns,
		violates: func(Register) bool { return false },
	},
	{
		name:     "tricolon",
		patterns: res(`\b[\w'’]+, [\w'’]+, and [\w'’]+\b`),
		violates: func(Register) bool { return false },
	},
	{
		name:     "exclamation",
		patterns: res(`!`),
		violates: func(Register) bool { return false },
	},
}

// warningChecks flag constructions the scan cannot grade with certainty.
// A hit lands in Report.Warnings, never in Counts or Findings, so it
// moves neither the exit code nor the tell rate.
var warningChecks = []check{
	{
		// A contrast keeps "own" legal ("declares its own roles, or uses
		// the default"), and a pattern cannot tell, so this stays a warning.
		name:     "empty-own",
		patterns: res(`(?i)\b(?:'s|’s|its|their|our|your|his|her) own\b`),
	},
	{
		// RE2 has no lookahead, so the pattern spells out the trailing
		// character. Exactly one whitespace rejects a code span Scan has
		// blanked, and the trailing character rejects "its in-flight".
		name:     "dangling-possessive",
		patterns: res(`(?i)\b(?:its|their)(?:[.,;:!?)]|\s(?:the|a|an|and|or|to|in|is|are|when|but)[ \t\n,.;:])`),
	},
}
