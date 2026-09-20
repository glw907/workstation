// Package posthook adapts the tell scanner to Claude Code's PostToolUse
// hook protocol: read the hook JSON, scan the file just written, and
// return advisory context. The hook never blocks and fails open, since
// a register call is a revision prompt, not an error.
package posthook

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/glw907/workstation/tellgrader/internal/tellscan"
)

type hookInput struct {
	ToolName  string `json:"tool_name"`
	ToolInput struct {
		FilePath  string `json:"file_path"`
		Content   string `json:"content"`
		NewString string `json:"new_string"`
	} `json:"tool_input"`
}

// RegisterFor picks the register a saved file is graded against. Agent-
// facing homes (CLAUDE.md, skills, agents) outrank the extension default;
// code files grade on their comments; other Markdown grades as developer
// docs.
func RegisterFor(path string) (tellscan.Register, bool) {
	switch strings.ToLower(filepath.Ext(path)) {
	case ".go", ".ts", ".js", ".svelte", ".py":
		return tellscan.Comments, true
	case ".md":
		if agentFacing(path) {
			return tellscan.Agent, true
		}
		return tellscan.Docs, true
	}
	return 0, false
}

func agentFacing(path string) bool {
	base := filepath.Base(path)
	return base == "CLAUDE.md" || base == "SKILL.md" ||
		strings.Contains(path, "/.claude/agents/")
}

// scanOptions builds the Scan options for a hook-triggered save. The hook grades one
// register per file and never reports docs-register measures, so the profile is forced
// off rather than resolved: an unforced Options would otherwise walk from path up to home
// on every save, computing a report field the hook's own output never surfaces.
func scanOptions(reg tellscan.Register, path string) tellscan.Options {
	home, _ := os.UserHomeDir()
	return tellscan.Options{
		Register: reg,
		Path:     path,
		Profile:  tellscan.ProfileNone,
		HomeDir:  home,
	}
}

// Run handles one PostToolUse event and returns the advisory JSON for
// stdout, or "" when there is nothing to say. It never asks to block.
func Run(raw []byte) string {
	var in hookInput
	if err := json.Unmarshal(raw, &in); err != nil {
		return ""
	}
	path := in.ToolInput.FilePath
	// Scratch space and once-off planning docs are not governed prose,
	// matching vale-hook's exclusions.
	if strings.HasPrefix(path, "/tmp/") || strings.Contains(path, "/superpowers/") {
		return ""
	}
	reg, ok := RegisterFor(path)
	if !ok {
		return ""
	}
	saved, err := os.ReadFile(path)
	if err != nil {
		return ""
	}
	text := string(saved)
	report := tellscan.Scan(text, scanOptions(reg, path))
	findings := keptFindings(report, text, &in)
	if len(findings) == 0 {
		return ""
	}
	var b strings.Builder
	fmt.Fprintf(&b, "tellgrader advisory (%s register): %d tell finding(s) on the lines just edited in %s. Nothing is blocked; revise if these sit in prose just written.\n",
		reg, len(findings), path)
	for _, f := range findings {
		fmt.Fprintf(&b, "line %d [%s]: %s\n", f.Line, f.Check, f.Excerpt)
	}
	out, err := json.Marshal(map[string]any{"hookSpecificOutput": map[string]any{
		"hookEventName":     "PostToolUse",
		"additionalContext": b.String(),
	}})
	if err != nil {
		return ""
	}
	return string(out)
}

// wholeDocChecks name the checks that judge a document as a whole
// rather than a line of it.
var wholeDocChecks = map[string]bool{"flat-cadence": true, "bold-lead-bullets": true}

// keptFindings scopes the report to the lines the tool call changed, so
// an edit does not resurface every historical finding in a large file.
// Whole-document findings (cadence, bullet shape) survive only on a
// Write, where the model authored the full file.
func keptFindings(r *tellscan.Report, saved string, in *hookInput) []tellscan.Finding {
	changed := changedLines(saved, newText(in))
	var kept []tellscan.Finding
	for _, f := range r.Findings {
		if wholeDocChecks[f.Check] {
			if in.ToolName == "Write" {
				kept = append(kept, f)
			}
			continue
		}
		if changed == nil || changed[f.Line] {
			kept = append(kept, f)
		}
	}
	return kept
}

func newText(in *hookInput) string {
	if in.ToolName == "Write" {
		return in.ToolInput.Content
	}
	return in.ToolInput.NewString
}

// changedLines returns the set of 1-based lines that inserted occupies
// in saved. A nil result means every line qualifies, which is the
// fallback when inserted is empty, absent, or repeats past maxOccurrences
// (a replace_all): surfacing a finding beats missing one.
func changedLines(saved, inserted string) map[int]bool {
	const maxOccurrences = 5
	if inserted == "" {
		return nil
	}
	lines := make(map[int]bool)
	start, hits := 0, 0
	for {
		idx := strings.Index(saved[start:], inserted)
		if idx == -1 {
			break
		}
		idx += start
		hits++
		if hits > maxOccurrences {
			return nil
		}
		first := strings.Count(saved[:idx], "\n") + 1
		for i := first; i <= first+strings.Count(inserted, "\n"); i++ {
			lines[i] = true
		}
		start = idx + len(inserted)
	}
	if len(lines) == 0 {
		return nil
	}
	return lines
}
