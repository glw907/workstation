package tellscan

import (
	"slices"
	"strings"
	"testing"
)

func findingChecks(r *Report) []string {
	var out []string
	for _, f := range r.Findings {
		out = append(out, f.Check)
	}
	return out
}

func TestScanFindings(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		register Register
		want     []string
		absent   []string
	}{
		{
			name:     "contrast frame not only but",
			input:    "This is not only fast but also correct.",
			register: Docs,
			want:     []string{"contrast-frame"},
		},
		{
			name:     "contrast frame its not x its y",
			input:    "It's not just a linter, it's a philosophy.",
			register: Docs,
			want:     []string{"contrast-frame"},
		},
		{
			name:     "connector opener flagged at sentence start",
			input:    "The cache buffers reads. Moreover, it lowers latency.",
			register: Docs,
			want:     []string{"connector-opener"},
		},
		{
			name:     "connector word mid-sentence not flagged",
			input:    "The cache helps, and additionally it buffers reads.",
			register: Docs,
			absent:   []string{"connector-opener"},
		},
		{
			name:     "em dash violates commit register",
			input:    "Fix the retry loop — it never backed off.",
			register: Commit,
			want:     []string{"em-dash"},
		},
		{
			name:     "spaced em dash violates docs register",
			input:    "The cache — a simple map — buffers reads.",
			register: Docs,
			want:     []string{"em-dash-spaced"},
			absent:   []string{"em-dash"},
		},
		{
			name:     "unspaced em dash allowed in docs",
			input:    "The cache buffers reads—and lowers latency.",
			register: Docs,
			absent:   []string{"em-dash", "em-dash-spaced"},
		},
		{
			name:     "hard slop flagged",
			input:    "This library delves into a rich tapestry of options.",
			register: Docs,
			want:     []string{"slop-hard"},
		},
		{
			name:     "the showcase site name is not slop",
			input:    "Open the showcase and read its members channel.",
			register: Docs,
			absent:   []string{"slop-hard"},
		},
		{
			name:     "showcases verb flagged",
			input:    "The page showcases every option.",
			register: Docs,
			want:     []string{"slop-hard"},
		},
		{
			name:     "showcasing verb flagged",
			input:    "The page is showcasing every option.",
			register: Docs,
			want:     []string{"slop-hard"},
		},
		{
			name:     "soft slop counted but not flagged",
			input:    "The check must be robust against comprehensive input.",
			register: Docs,
			absent:   []string{"slop-soft"},
		},
		{
			name:     "scaffold header",
			input:    "## Overview\n\nSome text here.",
			register: Docs,
			want:     []string{"scaffold-header"},
		},
		{
			name:     "setup colon payoff",
			input:    "The point: nobody reads long docs.",
			register: Docs,
			want:     []string{"setup-colon"},
		},
		{
			name:     "hedging filler",
			input:    "It's worth noting that the cache is optional.",
			register: Docs,
			want:     []string{"hedging-filler"},
		},
		{
			name:     "participial tail flagged",
			input:    "The library commits every edit to GitHub, ensuring nothing is lost.",
			register: Docs,
			want:     []string{"participial-tail"},
		},
		{
			name:     "plain gerund without comma not flagged",
			input:    "The hook runs before saving and after loading.",
			register: Docs,
			absent:   []string{"participial-tail"},
		},
		{
			name:     "assistant voice flagged",
			input:    "Set the ORIGIN variable and redeploy. I hope this helps!",
			register: Reply,
			want:     []string{"assistant-voice"},
		},
		{
			name:     "lowercase certainly mid-sentence not flagged",
			input:    "The rewrite is certainly, on balance, an improvement.",
			register: Reply,
			absent:   []string{"assistant-voice"},
		},
		{
			name:     "metacommentary flagged as setup colon",
			input:    "At its core, the library is a commit pipeline.",
			register: Docs,
			want:     []string{"setup-colon"},
		},
		{
			name: "bold lead bullets",
			input: "- **Fast**: does things quickly\n" +
				"- **Safe**: never corrupts data\n" +
				"- **Small**: one binary\n",
			register: Docs,
			want:     []string{"bold-lead-bullets"},
		},
		{
			name:     "fenced code is not graded",
			input:    "Real prose here.\n\n```go\n// Moreover, delve into the tapestry — of pointers.\nx := 1\n```\n",
			register: Docs,
			absent:   []string{"slop-hard", "connector-opener", "em-dash-spaced"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := Scan(tt.input, Options{Register: tt.register})
			got := findingChecks(r)
			for _, w := range tt.want {
				if !slices.Contains(got, w) {
					t.Errorf("Scan() findings = %v, missing %q", got, w)
				}
			}
			for _, a := range tt.absent {
				if slices.Contains(got, a) {
					t.Errorf("Scan() findings = %v, should not contain %q", got, a)
				}
			}
		})
	}
}

func TestSoftSlopCounted(t *testing.T) {
	r := Scan("The robust cache gives seamless and comprehensive coverage.", Options{Register: Docs})
	if r.Counts["slop-soft"] != 2 {
		t.Errorf("Counts[slop-soft] = %d, want 2 (robust, comprehensive)", r.Counts["slop-soft"])
	}
	if r.Counts["slop-hard"] != 1 {
		t.Errorf("Counts[slop-hard] = %d, want 1 (seamless)", r.Counts["slop-hard"])
	}
}

func TestCadenceCV(t *testing.T) {
	flat := strings.Repeat("This sentence has exactly six words. ", 10)
	r := Scan(flat, Options{Register: Docs})
	if r.CadenceCV > 0.01 {
		t.Errorf("CadenceCV = %.3f for identical sentences, want ~0", r.CadenceCV)
	}
	if !strings.Contains(strings.Join(findingChecks(r), ","), "flat-cadence") {
		t.Error("flat 10-sentence text did not flag flat-cadence")
	}

	varied := "Short one. This sentence runs quite a bit longer than its neighbor does, on purpose. Tiny. " +
		"Then a medium-length sentence follows it. No. A final sentence closes the paragraph with a moderate word count overall. " +
		"Two more. And here the longest sentence of the whole sample stretches out across many words to raise the variance decisively."
	rv := Scan(varied, Options{Register: Docs})
	if rv.CadenceCV < flatCadenceCV {
		t.Errorf("CadenceCV = %.3f for varied text, want >= %.2f", rv.CadenceCV, flatCadenceCV)
	}
}

func TestFindingLineNumbers(t *testing.T) {
	input := "Clean line.\n\nAnother clean line.\n\nMoreover, this line offends.\n"
	r := Scan(input, Options{Register: Docs})
	if len(r.Findings) != 1 {
		t.Fatalf("Findings = %d, want 1", len(r.Findings))
	}
	if r.Findings[0].Line != 5 {
		t.Errorf("Finding line = %d, want 5", r.Findings[0].Line)
	}
}

func TestExtractGoComments(t *testing.T) {
	src := "package x\n\n// Moreover, the helper delves deep.\nvar url = \"https://example.com//not-a-comment\"\n"
	r := Scan(src, Options{Register: Comments, Path: "f.go"})
	got := strings.Join(findingChecks(r), ",")
	if !strings.Contains(got, "connector-opener") || !strings.Contains(got, "slop-hard") {
		t.Errorf("findings = [%s], want connector-opener and slop-hard from the comment", got)
	}
	for _, f := range r.Findings {
		if strings.Contains(f.Excerpt, "example.com") {
			t.Errorf("string literal leaked into scan: %q", f.Excerpt)
		}
	}
}

func TestExtractPythonDocstrings(t *testing.T) {
	src := "def f():\n    \"\"\"Delve into the tapestry of args.\"\"\"\n    x = \"seamless string literal\"\n    return x\n"
	r := Scan(src, Options{Register: Comments, Path: "f.py"})
	if r.Counts["slop-hard"] != 2 {
		t.Errorf("Counts[slop-hard] = %d, want 2 (delve, tapestry; seamless is in a string literal)", r.Counts["slop-hard"])
	}
}

func TestExtractTSBlockComments(t *testing.T) {
	src := "/**\n * Furthermore, parses the intricate frontmatter.\n */\nexport function f(): void {}\n"
	r := Scan(src, Options{Register: Comments, Path: "f.ts"})
	got := strings.Join(findingChecks(r), ",")
	if !strings.Contains(got, "connector-opener") {
		t.Errorf("findings = [%s], want connector-opener from block comment line", got)
	}
}

func TestParseRegister(t *testing.T) {
	if _, err := ParseRegister("docs"); err != nil {
		t.Errorf("ParseRegister(docs) error: %v", err)
	}
	if _, err := ParseRegister("sonnet-form"); err == nil {
		t.Error("ParseRegister(sonnet-form) = nil error, want error")
	}
}
