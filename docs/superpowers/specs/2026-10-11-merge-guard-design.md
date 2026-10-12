# Merge guard (design)

**Status:** for Geoff's approval, 2026-10-11. Geoff chose the scope in the conductor session
(`4bea6e68`): the `pass-core` rule, the hook, and the desk banner, as one small pass.

## Why

Workstation PR #16 was correct only if two commands ran before its merge. The body said so in
prose, the conductor merged and pulled first, and the pull dropped Geoff's live `model`,
`effortLevel`, and `modelSettings`. A rule the merging session must remember failed the first
time it mattered. Anthropic's features overview
(<https://code.claude.com/docs/en/features-overview>): "If a rule must hold every time, make it a
hook rather than a prompt instruction."

## Outcome

A PR is safe under a plain merge and pull, or its merge is refused until the merger confirms the
steps it needs.

## Changes

1. **`pass-core` Close.** A PR must be safe under a plain merge followed by a pull; the executor
   makes it so where it can (PR #16's cutover could have kept the keys across a plain pull). When
   it cannot, the PR body carries a `## Before merge` section: the exact commands, in order, and
   the one check that shows they ran.
2. **`claude-merge-guard`**, a `PreToolUse` hook on `Bash`, beside `claude-tail-guard` in
   `bin/.local/bin/`, registered in `claude/.claude/settings.json`, with a test in `tests/`. On a
   `gh pr merge <n>` command it reads the PR body with `gh pr view`. If the body has a
   `## Before merge` section and the command does not start with `PREMERGE_DONE=<n>`, it blocks
   and returns the section's text, so the session sees the steps. It never runs text from a PR
   body, since some of these repos are public. Any other command, and any PR without the section,
   passes untouched.
3. **Review desk.** A PR item whose body has a `## Before merge` section shows it as a warning
   above Approve, so Geoff knows the PR needs extra steps before he approves.

## Out of scope

Merges made outside Claude Code (the GitHub web button), merge commands other than `gh pr merge`,
and the review desk UI pass, which builds on this.

## End-to-end check

On a scratch PR whose body has a `## Before merge` section, `gh pr merge` is blocked with the
section's text, and `PREMERGE_DONE=<n> gh pr merge` goes through. A PR without the section merges
with no prompt. The desk shows the section above Approve on the scratch PR.

## Risk and estimate

Class `runner` (a hook and `pass-core`). About 30 minutes. It touches a handful of files and this
page specifies it fully, so it skips the plan and goes straight through the gate (the global
CLAUDE.md "Process proportionality"); the conductor builds it in one worktree and hands the PR to
the desk.
