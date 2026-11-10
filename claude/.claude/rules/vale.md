---
paths:
  - "**/.vale.ini"
  - "**/styles/**"
---

# Vale in a repo on this workstation

A repo here commits its Vale `styles/` directory and pins Vale in CI. This rule replaces the
`standards:vale-setup` and `standards:vale-fix` steps that say otherwise.

1. `vale-setup` step 5 does not apply. Commit the StylesPath and never add it to `.gitignore`.
   Run `vale sync` once, only to populate `styles/` before that commit, and never against a
   directory that is already committed.
2. Leave the CI pin alone. Never edit the Vale version the workflow pins.
3. `vale-fix` steps 3 and 6 do not apply. A fix lands on the current pass branch, in the pass's PR,
   and never gets a separate branch or PR per file.

The workstation `vale-hook` stays the edit hook. Layout and the vendored skills are in
`~/.claude/docs/claude-tooling.md`.
