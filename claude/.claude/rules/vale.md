---
paths:
  - "**/.vale.ini"
  - "**/styles/**/*.yml"
  - "**/styles/config/vocabularies/**/*.txt"
---

# Vale in a repo on this workstation

A repo here commits its Vale `styles/` directory and pins Vale in CI. This rule replaces the
`standards:vale-setup` steps that say otherwise.

1. `vale-setup` step 5 and its "do not commit the `StylesPath` directory" bullet do not apply. Commit the StylesPath and never add it to `.gitignore`.
   Run `vale sync` once, only to populate `styles/` before that commit, and never against a
   directory that is already committed.
2. Leave the CI pin alone. Never edit the Vale version the workflow pins.
3. A Vale fix lands on the current task's branch, in the task's pull request, and never gets a
   separate branch or pull request per file.

The workstation `vale-hook` stays the edit hook. Layout and the vendored skills are in
`~/.claude/docs/claude-tooling.md`.
