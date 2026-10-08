// Package tellscan scans English prose for the AI-writing tells the
// workstation voice standard bans, grading against a named register so
// that a construction allowed in one audience (the em dash in developer
// docs) still flags in another (a commit message).
package tellscan

import (
	"fmt"
	"path/filepath"
	"slices"
	"strings"
)

// Register names the audience whose rules a scan grades against.
type Register int

const (
	Docs Register = iota
	Editor
	Commit
	Reply
	Agent
	Comments
)

var registerNames = [...]string{
	Docs:     "docs",
	Editor:   "editor",
	Commit:   "commit",
	Reply:    "reply",
	Agent:    "agent",
	Comments: "comments",
}

// ParseRegister maps a register name from the CLI to its Register.
func ParseRegister(s string) (Register, error) {
	i := slices.Index(registerNames[:], s)
	if i < 0 {
		return 0, fmt.Errorf("unknown register %q (want docs, editor, commit, reply, agent, or comments)", s)
	}
	return Register(i), nil
}

func (r Register) String() string {
	if r < 0 || int(r) >= len(registerNames) {
		return "unknown"
	}
	return registerNames[r]
}

// emDashBanned reports whether the register bans the em dash outright
// rather than merely counting it.
func (r Register) emDashBanned() bool {
	return r == Commit || r == Reply || r == Comments
}

// Options configures a Scan. Path selects comment extraction: a .go,
// .ts, or .py file is scanned on its comment text only. Path also
// anchors docs-register profile resolution when Profile is empty.
type Options struct {
	Register Register
	Path     string

	// Profile forces the docs-register profile: ProfileDocsRegister turns
	// it on, ProfileNone turns it off, and "" resolves it from the repo's
	// own .tellgrader.json opt-in.
	Profile string
	// HomeDir is the stop root for the opt-in walk: a session's real home
	// directory in production, and a hermetic stand-in a test controls.
	HomeDir string
}

// Finding is one register violation, anchored to a line of the input.
type Finding struct {
	Check   string `json:"check"`
	Line    int    `json:"line"`
	Excerpt string `json:"excerpt"`
	// Gate marks a finding that fails the run: the CLI exits non-zero when
	// any finding carries it. Only trailing-hinge-run gates, and only under
	// the docs-register profile.
	Gate bool `json:"gate,omitempty"`
}

// Report carries the scan result for one input. Counts records every
// occurrence per check, violations or not; Findings holds only what the
// register treats as a violation, and TellsPer1000Words is their rate.
type Report struct {
	Path              string         `json:"path"`
	Register          string         `json:"register"`
	Words             int            `json:"words"`
	Sentences         int            `json:"sentences"`
	CadenceCV         float64        `json:"cadence_cv"`
	Counts            map[string]int `json:"counts"`
	Findings          []Finding      `json:"findings"`
	TellsPer1000Words float64        `json:"tells_per_1000_words"`

	// Profile and Measures are present only when the docs-register
	// profile applies to this scan; both are absent as a unit otherwise,
	// which keeps a legitimate zero share from reading as omitted.
	Profile  string    `json:"profile,omitempty"`
	Measures *Measures `json:"measures,omitempty"`
}

// Measures carries the docs-register cadence measures for one file:
// report-only figures with no band and no gate. See MEASURES.md next to
// the scanner for their definitions.
type Measures struct {
	Unit               string  `json:"unit"`
	Selector           string  `json:"selector"`
	Sentences          int     `json:"sentences"`
	HingedPairShare    float64 `json:"hinged_pair_share"`
	ShortSentenceShare float64 `json:"short_sentence_share"`
}

// Scan runs every check for the register over the input and returns the
// report. Code files are reduced to their comment text first; markdown
// has fenced code blocks blanked so only prose is graded. Line numbers
// in findings refer to the original input.
func Scan(input string, opts Options) *Report {
	text := input
	switch strings.ToLower(filepath.Ext(opts.Path)) {
	case ".go", ".ts", ".js", ".svelte":
		text = extractComments(input, extractSlash)
	case ".py":
		text = extractComments(input, extractHash)
	}
	prose := blankFencedCode(text)

	// Empty rather than nil so the JSON carries {} and [], not null.
	r := &Report{
		Path:     opts.Path,
		Register: opts.Register.String(),
		Counts:   map[string]int{},
		Findings: []Finding{},
	}

	for _, c := range checks {
		matches := c.find(prose)
		if len(matches) == 0 {
			continue
		}
		r.Counts[c.name] += len(matches)
		if c.violates != nil && !c.violates(opts.Register) {
			continue
		}
		for _, m := range matches {
			r.Findings = append(r.Findings, Finding{
				Check:   c.name,
				Line:    lineOf(prose, m),
				Excerpt: excerpt(prose, m),
			})
		}
	}

	if line, hit := boldLeadBullets(prose); hit {
		r.Counts["bold-lead-bullets"]++
		r.Findings = append(r.Findings, Finding{
			Check:   "bold-lead-bullets",
			Line:    line,
			Excerpt: "half or more of the bullets open with a bolded lead phrase",
		})
	}

	profile := resolveProfile(opts.Path, opts.HomeDir, opts.Profile)
	hingeRuns, uniform := paragraphFindings(prose, profile == ProfileDocsRegister)
	for _, f := range hingeRuns {
		r.Counts[f.Check]++
		r.Findings = append(r.Findings, f)
	}
	if uniform > 0 {
		r.Counts["uniform-paragraph"] = uniform
	}

	sentences := splitSentences(prose)
	r.Words = wordCount(prose)
	r.Sentences = len(sentences)
	r.CadenceCV = cadenceCV(sentences)
	if r.Sentences >= 8 && r.CadenceCV < flatCadenceCV {
		r.Counts["flat-cadence"]++
		r.Findings = append(r.Findings, Finding{
			Check:   "flat-cadence",
			Line:    1,
			Excerpt: fmt.Sprintf("sentence-length CV %.2f over %d sentences", r.CadenceCV, r.Sentences),
		})
	}

	if r.Words > 0 {
		r.TellsPer1000Words = float64(len(r.Findings)) / float64(r.Words) * 1000
	}

	if profile != "" {
		measureSentences, hingedShare, shortShare := measureShares(prose)
		r.Profile = profile
		r.Measures = &Measures{
			Unit:               "fraction",
			Selector:           "prose",
			Sentences:          len(measureSentences),
			HingedPairShare:    hingedShare,
			ShortSentenceShare: shortShare,
		}
	}
	return r
}

// lineOf anchors a match to the line its content starts on: a pattern
// that captures the previous sentence's terminator would otherwise
// report the wrong line across a paragraph break.
func lineOf(s string, m match) int {
	content := strings.TrimLeft(s[m.start:m.end], ".!? \t\n")
	start := m.end - len(content)
	return 1 + strings.Count(s[:start], "\n")
}

// excerpt clips the matched text to a readable window.
func excerpt(s string, m match) string {
	const window = 90
	text := strings.TrimSpace(s[m.start:m.end])
	if runes := []rune(text); len(runes) > window {
		text = string(runes[:window]) + "…"
	}
	return strings.ReplaceAll(text, "\n", " ")
}
