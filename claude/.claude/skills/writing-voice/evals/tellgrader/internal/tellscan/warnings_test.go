package tellscan

import (
	"encoding/json"
	"slices"
	"strings"
	"testing"
)

func warningChecksOf(r *Report) []string {
	var out []string
	for _, w := range r.Warnings {
		out = append(out, w.Check)
	}
	return out
}

func scanWarnings(input string) *Report {
	return Scan(input, Options{Register: Docs, Path: "x.md", Profile: ProfileNone})
}

// remnantLines are the removed lines of cairn-cms 3960d4913 that held a
// possessive with its noun swept away. The commit's diff has 16 removed
// lines; two only wrap the clause ("keeps a `5rem` minimum width" and
// "listeners are delegation"), and the "block whose ground" line sits in
// two files, which leaves 14 cases.
var remnantLines = []string{
	"`<html data-theme>`) keeps it by sequencing the engine guard after its:",
	"of its, so a dense table column (a publish-state cell, an alt/usage cell) budgets the chip's",
	"caller doesn't add a second live region of its.",
	"selection of its, so the caller owns what a pick does next.",
	"directly folds where it is written. A site that reads the global needs no declaration of its.",
	"A theme that needs a tuned ink sets its in its daisyUI block, and in both blocks when both schemes need it.",
	"    // Scoped to the header: the footer reuses the `.site-nav` class for its, separate nav.",
	"     block whose ground differs from its, but a band that directly precedes the footer",
	"     block whose ground differs from its, but a band that directly precedes the footer",
	"     their an AT user should be told about, matching ToolbarDisclosure's containing",
	"    // parent) has no selector of its and inherits.",
	" * with no fill of its is skipped rather than compared.",
	"    // the tappable area rather than the link glyph alone. A link with no text of its is not in",
	"// carry the weight, and each is a finding of its when it fails: a directive names a reason, a",
}

func TestDanglingPossessiveRecall(t *testing.T) {
	if len(remnantLines) != 14 {
		t.Fatalf("remnantLines = %d, want the 14 remnants of 3960d4913", len(remnantLines))
	}
	for _, line := range remnantLines {
		t.Run(line, func(t *testing.T) {
			if got := warningChecksOf(scanWarnings(line)); !slices.Contains(got, "dangling-possessive") {
				t.Errorf("warnings = %v, want dangling-possessive", got)
			}
		})
	}
}

func TestWarnings(t *testing.T) {
	tests := []struct {
		name  string
		input string
		want  []string
	}{
		{
			name:  "own after a possessive noun",
			input: "The site's own role names stay as they are.",
			want:  []string{"empty-own"},
		},
		{
			name:  "own in a contrast warns by design",
			input: "The site declares its own role names, or uses the default pair.",
			want:  []string{"empty-own"},
		},
		{
			name:  "own without a possessive is clean",
			input: "Each file has an own-goal check.",
		},
		{
			name:  "its in-flight is clean",
			input: "The request is its in-flight copy until the reply lands.",
		},
		{
			name:  "its before a noun is clean",
			input: "The cache keeps its entries for an hour.",
		},
		{
			name:  "blanked code span is clean",
			input: "The guard runs after `its` setup and `their` teardown.",
		},
		{
			name:  "dangling before a comma",
			input: "The chip carries no minimum of its, so the column budgets.",
			want:  []string{"dangling-possessive"},
		},
		{
			name:  "both on one line",
			input: "Each site has its own, and the theme sets their.",
			want:  []string{"empty-own", "dangling-possessive"},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := scanWarnings(tt.input)
			got := warningChecksOf(r)
			slices.Sort(got)
			want := slices.Clone(tt.want)
			slices.Sort(want)
			if !slices.Equal(got, want) {
				t.Errorf("warnings = %v, want %v", got, want)
			}
			if len(r.Findings) != 0 {
				t.Errorf("Findings = %v, want none: a warning is not a finding", r.Findings)
			}
			if r.Counts["empty-own"] != 0 || r.Counts["dangling-possessive"] != 0 {
				t.Errorf("Counts = %v, want warnings kept out of counts", r.Counts)
			}
			if r.TellsPer1000Words != 0 {
				t.Errorf("TellsPer1000Words = %v, want 0", r.TellsPer1000Words)
			}
		})
	}
}

func TestWarningsJSONCarriesEmptyList(t *testing.T) {
	out, err := json.Marshal(scanWarnings("A clean sentence."))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(out), `"warnings":[]`) {
		t.Errorf("JSON = %s, want \"warnings\":[]", out)
	}
}
