# Files a repo carries

Every repo carries the files below. Each one is sized by the repo, so a small repo's files are short.

| File | What it holds |
| --- | --- |
| `CLAUDE.md` | Only what an agent can't learn from the code: the gate, the stack rules, the safety rails, and pointers to the repo skill and to `docs/decisions/`. Under 200 lines, with no overview or history. |
| `README.md` | What the repo is and how a person runs it. |
| `BACKLOG.md` | Work found and not yet built, logged through `standards:log-issue`. |
| The gate | The one script a task runs before its pull request is ready, named in the repo's pass skill. |
| `docs/STATUS.md` | The repo's state now, kept as "Records" in `SKILL.md` says. |
| `docs/decisions/` | One decision record per binding decision. The folder appears with its first record. |

Anthropic's memory guide sets the 200-line target and says longer files "reduce adherence"
(<https://code.claude.com/docs/en/memory>). "Evaluating AGENTS.md" found that context files don't generally
improve task success and raise inference cost by over 20 percent, and that repository overviews didn't help
(<https://arxiv.org/abs/2602.11988>).

## Decision records

A record follows Nygard's format: a title, `## Status`, `## Context`, `## Decision`, and `## Consequences`
(<https://adr.github.io>). Its status is `Proposed`, `Accepted`, `Deprecated`, or `Superseded by NNNN`. An
accepted record binds every change, a proposed one is context, and a superseded one is history. A change of mind
is a new record that supersedes the old one, which is never edited. A record holds a decision and its reason,
never a copy of the code.

## Rules a tool can check

A rule a tool can check becomes a gate check, and its prose goes from every file that held it.

A check adopted on existing code lists each finding it raises as a named exclusion, one per finding and never a
path-wide one, and the list only shrinks. An excluded finding with a score, such as a function's complexity,
keeps its score at adoption as a ceiling the gate enforces, so excluded code can't get worse. ESLint's bulk
suppressions record counts the same way (<https://eslint.org/blog/2025/04/introducing-bulk-suppressions/>).

A Go repo takes four checks: dupl and gocognit for duplicated and complex code, forbidigo for banned calls such
as `time.Now` in a package that takes its clock, and `go tool deadcode -test ./...` for code that nothing calls.
A repo in another language takes its ecosystem's equivalents, named in that repo's spec.

## The worked example

dubplate carries the pattern: its `CLAUDE.md`, its records in `docs/decisions/`, the four checks in
`.golangci.yml` and `scripts/check.sh`, and the gate legs that hold `CLAUDE.md` to 200 lines and every record to
a valid status.
