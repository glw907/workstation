package tellscan

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// The owner-flagged paragraph and its accepted rewrite (Geoff, 2026-10-07).
const (
	hingeRunOriginal = "The workflow runs `npm install`, `npm run check`, and `npm run check:cairn` on every push and pull\n" +
		"request. It pins `node-version: 24`, the only Node version the scaffold names, since it ships\n" +
		"neither an `.nvmrc` nor an `engines` field. Its last step runs `npx cairn-guidance check` under\n" +
		"`continue-on-error: true`, which [The guidance tree](#the-guidance-tree) explains. The workflow\n" +
		"installs no browser, so the `check:cairn:rendered` script cannot run in it.\n"
	hingeRunRewrite = "On every push and pull request, the workflow installs dependencies and runs `npm run check` and\n" +
		"`npm run check:cairn`. It uses Node 24. Nothing else in the scaffold names a version: there's no\n" +
		"`.nvmrc` and no `engines` field. The last step runs `npx cairn-guidance check`, but that step\n" +
		"can't fail the job, for reasons covered in [The guidance tree](#the-guidance-tree). No browser is\n" +
		"installed, so `check:cairn:rendered` can't run in CI.\n"
)

func hingeRunFindings(r *Report) []Finding {
	var out []Finding
	for _, f := range r.Findings {
		if f.Check == "trailing-hinge-run" {
			out = append(out, f)
		}
	}
	return out
}

func TestTrailingHingeRun(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		wantLine int // 0 means no finding
	}{
		{name: "owner-flagged paragraph trips", input: hingeRunOriginal, wantLine: 1},
		{name: "accepted rewrite stays clean", input: hingeRunRewrite},
		{
			name:     "paragraph line follows earlier paragraphs",
			input:    "# Heading\n\nA clean opener.\n\n" + hingeRunOriginal,
			wantLine: 5,
		},
		{
			name:  "single hinge sentence does not trip",
			input: "The guard refuses the request, because the session expired. Sign in again. The editor reopens.\n",
		},
		{
			name: "two hinges in a row do not trip",
			input: "The guard refuses the request, because the session expired. The editor reloads the page, " +
				"which clears the draft. Sign in again.\n",
		},
		{
			name: "three hinges broken by a plain sentence do not trip",
			input: "The guard refuses the request, because the session expired. The editor reloads the page, " +
				"which clears the draft. Sign in again. The draft returns from the branch, since saves commit there.\n",
		},
		{
			name: "list items are excluded",
			input: "- The guard refuses the request, because the session expired.\n" +
				"- The editor reloads the page, which clears the draft.\n" +
				"- The draft returns from the branch, since saves commit there.\n",
		},
		{
			name: "introductory clause is not a tail",
			input: "Since then, the guard refuses stale sessions. As before, the editor reloads the page. " +
				"While it loads, the draft stays on its branch.\n",
		},
		{
			name: "hinges split across paragraphs do not trip",
			input: "The guard refuses the request, because the session expired. The editor reloads the page, " +
				"which clears the draft.\n\nThe draft returns from the branch, since saves commit there.\n",
		},
		{
			name:  "fenced code is not prose",
			input: "```\na = 1, so b runs. c = 2, so d runs. e = 3, so f runs.\n```\n",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := hingeRunFindings(Scan(tt.input, Options{Register: Docs, Profile: ProfileNone}))
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

func TestHasTrailingHinge(t *testing.T) {
	tests := []struct {
		sentence string
		want     bool
	}{
		{"It pins Node 24, the only version named, since it ships no engines field", true},
		{"Its last step runs the check, which the guidance tree explains", true},
		{"The workflow installs no browser, so the rendered check cannot run", true},
		{"The deploy waits, so that the cache warms first", true},
		{"The page loads, whereas the editor stays closed", true},
		{"The workflow runs install, check, and check:cairn on every push", false},
		{"The last step runs the check, but that step cannot fail the job", false},
		{"Since then, the guard refuses stale sessions", false},
		{"It uses a so-called island, and nothing else", false},
	}
	for _, tt := range tests {
		if got := hasTrailingHinge(tt.sentence); got != tt.want {
			t.Errorf("hasTrailingHinge(%q) = %v, want %v", tt.sentence, got, tt.want)
		}
	}
}

// TestTrailingHingeRunGatesOnlyUnderDocsRegister holds the gate rule: the
// finding reports in every register but carries Gate only under the
// docs-register profile.
func TestTrailingHingeRunGatesOnlyUnderDocsRegister(t *testing.T) {
	for _, tt := range []struct {
		profile  string
		wantGate bool
	}{
		{ProfileDocsRegister, true},
		{ProfileNone, false},
	} {
		got := hingeRunFindings(Scan(hingeRunOriginal, Options{Register: Docs, Profile: tt.profile}))
		if len(got) != 1 {
			t.Fatalf("profile %q: findings = %+v, want one", tt.profile, got)
		}
		if got[0].Gate != tt.wantGate {
			t.Errorf("profile %q: Gate = %v, want %v", tt.profile, got[0].Gate, tt.wantGate)
		}
	}
}

func TestUniformParagraphCount(t *testing.T) {
	flat := "The guard reads the session cookie. The store returns the matching row. " +
		"The handler checks the expiry time. The page renders the admin shell.\n"
	if got := Scan(flat, Options{Register: Docs}).Counts["uniform-paragraph"]; got != 1 {
		t.Errorf("Counts[uniform-paragraph] = %d, want 1", got)
	}
	varied := "Sign in. The guard reads the session cookie and asks the store for the row that matches it. " +
		"Then it checks expiry. The page renders.\n"
	if got := Scan(varied, Options{Register: Docs}).Counts["uniform-paragraph"]; got != 0 {
		t.Errorf("Counts[uniform-paragraph] = %d, want 0", got)
	}
}

// TestGateExitCode runs the real binary: a gating finding exits 2 with the
// report still on stdout, and the same file without the profile exits 0.
func TestGateExitCode(t *testing.T) {
	path := filepath.Join(t.TempDir(), "page.md")
	if err := os.WriteFile(path, []byte(hingeRunOriginal), 0o644); err != nil {
		t.Fatal(err)
	}
	out, code := runTellgrader(t, "", "--profile", ProfileDocsRegister, path)
	if code != 2 {
		t.Fatalf("exit code = %d, want 2, output: %s", code, out)
	}
	if !strings.Contains(out, `"gate": true`) {
		t.Errorf("output lacks the gating finding: %s", out)
	}
	if _, code := runTellgrader(t, "", "--profile", ProfileNone, path); code != 0 {
		t.Errorf("exit code without profile = %d, want 0", code)
	}
}
