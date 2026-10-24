package posthook

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/glw907/workstation/tellgrader/internal/tellscan"
)

func TestRegisterFor(t *testing.T) {
	tests := []struct {
		path string
		want tellscan.Register
		ok   bool
	}{
		{"/home/g/repo/README.md", tellscan.Docs, true},
		{"/home/g/repo/CLAUDE.md", tellscan.Agent, true},
		{"/home/g/.claude/skills/foo/SKILL.md", tellscan.Agent, true},
		{"/home/g/.claude/agents/reviewer.md", tellscan.Agent, true},
		{"/home/g/repo/main.go", tellscan.Comments, true},
		{"/home/g/repo/app.svelte", tellscan.Comments, true},
		{"/home/g/repo/data.json", 0, false},
	}
	for _, tt := range tests {
		t.Run(tt.path, func(t *testing.T) {
			got, ok := RegisterFor(tt.path)
			if ok != tt.ok || (ok && got != tt.want) {
				t.Errorf("RegisterFor(%q) = %v, %v; want %v, %v", tt.path, got, ok, tt.want, tt.ok)
			}
		})
	}
}

func TestScanOptionsForcesProfileOff(t *testing.T) {
	opts := scanOptions(tellscan.Docs, "docs/extend/seam.md")
	if opts.Profile != tellscan.ProfileNone {
		t.Errorf("Profile = %q, want %q: the hook never reports docs-register measures", opts.Profile, tellscan.ProfileNone)
	}
	if opts.HomeDir == "" {
		t.Error("HomeDir = \"\", want the session's home directory")
	}
}

func event(t *testing.T, tool, path, newStr, content string) []byte {
	t.Helper()
	raw, err := json.Marshal(map[string]any{
		"tool_name": tool,
		"tool_input": map[string]any{
			"file_path":  path,
			"new_string": newStr,
			"content":    content,
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	return raw
}

// writeDoc places fixtures beside the package rather than in
// t.TempDir(), because Run deliberately skips /tmp as ungoverned
// scratch space and would silence them.
func writeDoc(t *testing.T, name, body string) string {
	t.Helper()
	dir, err := os.MkdirTemp(".", "fixture-*")
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() {
		if err := os.RemoveAll(dir); err != nil {
			t.Errorf("clean fixture dir: %v", err)
		}
	})
	abs, err := filepath.Abs(filepath.Join(dir, name))
	if err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Dir(abs), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(abs, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
	return abs
}

func TestRunFlagsChangedLineOnly(t *testing.T) {
	body := "Old text delves into the tapestry.\n\nFresh clean sentence here.\n"
	path := writeDoc(t, "doc.md", body)
	out := Run(event(t, "Edit", path, "Fresh clean sentence here.", ""))
	if out != "" {
		t.Errorf("Run() = %q, want no advisory for a clean edited line", out)
	}
	out = Run(event(t, "Edit", path, "Old text delves into the tapestry.", ""))
	if !strings.Contains(out, "slop-hard") {
		t.Errorf("Run() = %q, want slop-hard advisory when the edited line offends", out)
	}
	if !strings.Contains(out, "additionalContext") {
		t.Errorf("Run() output is not hook-shaped JSON: %q", out)
	}
}

func TestRunSkipsUngovernedPaths(t *testing.T) {
	body := "This delves into a rich tapestry.\n"
	if out := Run(event(t, "Write", "/tmp/scratch/x.md", "", body)); out != "" {
		t.Errorf("Run() on /tmp path = %q, want silence", out)
	}
	path := writeDoc(t, "notes.txt", body)
	if out := Run(event(t, "Write", path, "", body)); out != "" {
		t.Errorf("Run() on .txt = %q, want silence", out)
	}
	for _, dir := range []string{"specs", "plans", "research", "archive"} {
		path := writeDoc(t, "docs/"+dir+"/x.md", body)
		if out := Run(event(t, "Write", path, "", body)); out != "" {
			t.Errorf("Run() on docs/%s = %q, want silence", dir, out)
		}
	}
	path = writeDoc(t, "docs/extend/x.md", body)
	if out := Run(event(t, "Write", path, "", body)); out == "" {
		t.Error("Run() on docs/extend = silence, want an advisory outside the planning folders")
	}
}

func TestRunFailsOpenOnBadInput(t *testing.T) {
	if out := Run([]byte("not json")); out != "" {
		t.Errorf("Run(bad json) = %q, want empty", out)
	}
	if out := Run(event(t, "Write", "/nonexistent/dir/x.md", "", "hi")); out != "" {
		t.Errorf("Run(missing file) = %q, want empty", out)
	}
}

func TestWholeDocFindingsOnlyOnWrite(t *testing.T) {
	bullets := "- **Fast**: quick\n- **Safe**: sound\n- **Small**: tiny\n"
	path := writeDoc(t, "list.md", bullets)
	if out := Run(event(t, "Write", path, "", bullets)); !strings.Contains(out, "bold-lead-bullets") {
		t.Errorf("Write advisory = %q, want bold-lead-bullets", out)
	}
	if out := Run(event(t, "Edit", path, "- **Fast**: quick", "")); strings.Contains(out, "bold-lead-bullets") {
		t.Errorf("Edit advisory = %q, want whole-doc finding suppressed on Edit", out)
	}
}

func TestRunWarnsOnChangedLineOnly(t *testing.T) {
	body := "The chip has no minimum of its, so tables budget.\n\nThe site sets its own roles.\n"
	path := writeDoc(t, "warn.md", body)
	out := Run(event(t, "Edit", path, "The site sets its own roles.", ""))
	if !strings.Contains(out, "warning empty-own") {
		t.Errorf("Run() = %q, want an empty-own warning on the edited line", out)
	}
	if strings.Contains(out, "dangling-possessive") {
		t.Errorf("Run() = %q, want no warning for the unchanged dangling line", out)
	}
	out = Run(event(t, "Edit", path, "The chip has no minimum of its, so tables budget.", ""))
	if !strings.Contains(out, "warning dangling-possessive") || strings.Contains(out, "empty-own") {
		t.Errorf("Run() = %q, want only the dangling-possessive warning", out)
	}
}
