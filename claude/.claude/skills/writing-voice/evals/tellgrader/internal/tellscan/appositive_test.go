package tellscan

import "testing"

// The owner-flagged sentence and its approved rewrite (Geoff, 2026-10-07).
const (
	appositiveOriginal = "Every person signed in to a cairn admin holds a role, a name from the site's declared role\n" +
		"vocabulary, which is `owner` and `editor` unless the site declares its own.\n"
	appositiveRewrite = "Everyone who signs in to a cairn admin has a role. The site declares its own role names, or\n" +
		"uses the default pair, `owner` and `editor`.\n"
)

func appositiveFindingsOf(r *Report) []Finding {
	var out []Finding
	for _, f := range r.Findings {
		if f.Check == "appositive-stack" {
			out = append(out, f)
		}
	}
	return out
}

func TestAppositiveStack(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		wantLine int // 0 means no finding
	}{
		{name: "owner-flagged sentence trips", input: appositiveOriginal, wantLine: 1},
		{name: "approved rewrite stays clean", input: appositiveRewrite},
		{
			name:     "line is the sentence's own start",
			input:    "# Roles\n\nA clean opener sits on the first line.\n" + appositiveOriginal,
			wantLine: 4,
		},
		{
			name:  "plain which clause without an appositive does not trip",
			input: "The guard reads the session cookie, which the store issued at sign-in.\n",
		},
		{
			name:  "appositive without a relative clause does not trip",
			input: "Every editor holds a role, a name from the site's vocabulary.\n",
		},
		{
			name:  "serial list does not trip",
			input: "The guard checks the cookie, the session row, and the role, which the store returns.\n",
		},
		{
			name:  "introductory phrase is not a renamed noun",
			input: "In the admin, a theme reaches the editor's preview frame, which renders the entry.\n",
		},
		{
			name:  "list inside parentheses does not trip",
			input: "A zone spelling (a colonless offset, a lowercase Z) is normalized first, which keeps parsing stable.\n",
		},
		{
			name:     "who clause trips",
			input:    "The page names its owner, the person on the site's role list, who approves every publish.\n",
			wantLine: 1,
		},
		{
			name:  "list items are excluded",
			input: "- Every editor holds a role, a name from the vocabulary, which the site declares.\n",
		},
		{
			name:  "table rows are excluded",
			input: "| Every editor holds a role, a name from the vocabulary, which the site declares. |\n",
		},
		{
			name:  "HTML lines are excluded",
			input: "<p>Every editor holds a role, a name from the vocabulary, which the site declares.</p>\n",
		},
		{
			name:  "fenced code is not prose",
			input: "```\nEvery editor holds a role, a name from the vocabulary, which the site declares.\n```\n",
		},
		{
			name:  "front matter is excluded",
			input: "---\ndescription: Every editor holds a role, a name from the vocabulary, which the site declares.\n---\n",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := appositiveFindingsOf(Scan(tt.input, Options{Register: Docs, Profile: ProfileNone}))
			if tt.wantLine == 0 {
				if len(got) != 0 {
					t.Fatalf("findings = %+v, want none", got)
				}
				return
			}
			if len(got) != 1 {
				t.Fatalf("findings = %+v, want exactly one", got)
			}
			if got[0].Line != tt.wantLine {
				t.Errorf("line = %d, want %d", got[0].Line, tt.wantLine)
			}
		})
	}
}

// TestAppositiveStackGatesOnlyUnderDocsRegister holds the gate rule: the
// finding reports in every register but carries Gate only under the
// docs-register profile.
func TestAppositiveStackGatesOnlyUnderDocsRegister(t *testing.T) {
	for _, tt := range []struct {
		profile  string
		wantGate bool
	}{
		{ProfileDocsRegister, true},
		{ProfileNone, false},
	} {
		got := appositiveFindingsOf(Scan(appositiveOriginal, Options{Register: Docs, Profile: tt.profile}))
		if len(got) != 1 {
			t.Fatalf("profile %q: findings = %+v, want one", tt.profile, got)
		}
		if got[0].Gate != tt.wantGate {
			t.Errorf("profile %q: Gate = %v, want %v", tt.profile, got[0].Gate, tt.wantGate)
		}
	}
}
