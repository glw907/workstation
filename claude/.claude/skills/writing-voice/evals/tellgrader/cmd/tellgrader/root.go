package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"

	"github.com/glw907/workstation/tellgrader/internal/posthook"
	"github.com/glw907/workstation/tellgrader/internal/tellscan"
	"github.com/spf13/cobra"
)

type flags struct {
	register string
	hook     bool
	profile  string
}

func newRootCmd() *cobra.Command {
	var f flags

	cmd := &cobra.Command{
		Use:   "tellgrader --register <name> file...",
		Short: "Scan prose for AI-writing tells and report cadence statistics as JSON",
		Long: "Scan prose for AI-writing tells and report cadence statistics as JSON.\n\n" +
			"Exit status: 0 when no finding gates, 1 on a usage or read error, and 2 when a\n" +
			"finding gates (\"gate\": true). Only trailing-hinge-run and appositive-stack gate,\n" +
			"and only under the docs-register profile; the JSON report is printed either way.",
		Args:          cobra.ArbitraryArgs,
		RunE:          func(cmd *cobra.Command, args []string) error { return run(args, &f) },
		SilenceUsage:  true,
		SilenceErrors: true,
	}
	cmd.Flags().StringVar(&f.register, "register", "docs",
		"register to grade against: docs, editor, commit, reply, agent, comments")
	cmd.Flags().BoolVar(&f.hook, "hook", false,
		"read a Claude Code PostToolUse event on stdin and emit advisory context")
	cmd.Flags().StringVar(&f.profile, "profile", "",
		"docs-register measures profile: docs-register forces it on, none forces it off, "+
			"omit to resolve from the scanned repo's .tellgrader.json")
	return cmd
}

func run(paths []string, f *flags) error {
	if f.hook {
		runHook()
		return nil
	}
	if len(paths) == 0 {
		return errors.New("no files to scan")
	}
	reg, err := tellscan.ParseRegister(f.register)
	if err != nil {
		return err
	}
	switch f.profile {
	case "", tellscan.ProfileDocsRegister, tellscan.ProfileNone:
	default:
		return fmt.Errorf("unknown profile %q (want %s or %s)", f.profile, tellscan.ProfileDocsRegister, tellscan.ProfileNone)
	}
	home, _ := os.UserHomeDir()

	reports := make([]*tellscan.Report, 0, len(paths))
	for _, p := range paths {
		data, err := os.ReadFile(p)
		if err != nil {
			return fmt.Errorf("read %s: %v", p, err)
		}
		reports = append(reports, tellscan.Scan(string(data), tellscan.Options{
			Register: reg,
			Path:     p,
			Profile:  f.profile,
			HomeDir:  home,
		}))
	}

	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	var out any = reports
	if len(reports) == 1 {
		out = reports[0]
	}
	if err := enc.Encode(out); err != nil {
		return err
	}
	return gateFailures(reports)
}

// gateError reports gating findings. The JSON report is already on stdout,
// so main exits with gateExitCode rather than the usage-error code 1, letting
// a caller tell a failed gate from a failed run.
type gateError struct{ count int }

const gateExitCode = 2

func (e gateError) Error() string {
	return fmt.Sprintf("tellgrader: %d gating finding(s); see \"gate\": true in the report", e.count)
}

func gateFailures(reports []*tellscan.Report) error {
	n := 0
	for _, r := range reports {
		for _, f := range r.Findings {
			if f.Gate {
				n++
			}
		}
	}
	if n == 0 {
		return nil
	}
	return gateError{count: n}
}

// runHook is advisory-only and fails open: it returns no error, so a
// hook problem exits 0 and never disrupts the session.
func runHook() {
	raw, err := io.ReadAll(os.Stdin)
	if err != nil {
		return
	}
	if out := posthook.Run(raw); out != "" {
		fmt.Println(out)
	}
}
