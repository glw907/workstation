---
name: site-pass
description: >
  The workstation's facts for building work in the SvelteKit site repos (ecxc-ski, 907-life,
  aksailingclub-org, cairn-pub): gate, fast lane, full-suite home, worktree setup, CI watch,
  risk-class path map, checklist globs, and close checklist. Use with building-from-specs when
  building, resuming, or reviewing a task in one of those repos, on "continue development" or
  "build the next piece of work", or when a site's own roadmap drives the work. For the cairn-cms
  engine use cairn-pass.
---

# Site pass

Load `building-from-specs` first; it holds the process, and this skill fills in each site's facts.
Paths are relative to the site repo. The resume prompt is in `docs/STATUS.md`. The spec, archive,
and architecture-doc paths come from the site's `CLAUDE.md` or STATUS; `docs/{plans,specs}/` and
`docs/architecture.md` are the usual case, not the only one. The spec header carries exactly one
of a consultation-brief link or the line "no engine asks", plus a "Sources consulted" line, from
`engine-consult`; a committed spec with neither gets the enumeration run before the first task.

| Site | Gate | Fast lane | Full-suite home | Worktree setup |
|---|---|---|---|---|
| ecxc-ski | `npm run check` | check, plus `npx vitest run <touched test files>` | local, once at close: `npm run check && npm test && npm run build` | `npm ci`, then `npx svelte-kit sync` |
| 907-life | `npm run check` | check, plus `npx vitest run <touched test files>` | local, once at close: `npm run check && npm test && npm run build` | `npm ci`, then `npx svelte-kit sync` |
| aksailingclub-org | `npm run check` | check, plus `npx vitest run <touched test files>` | CI on the PR | `npm ci`, then `npx svelte-kit sync` |
| cairn-pub | `npm run check` | check, plus `npx vitest run <touched test files>` | local, once at close: `npm run check && npm test && npm run build` | `npm ci`, then `npx svelte-kit sync` |

## Gates

**Gate**: `cairn-run-gate '<string>'` on the light lane (`CAIRN_GATE_LANE=light`), since no site gate
launches a browser. `npm run check` must report 0 errors and 0 warnings.

**Fast lane**: The table's column: `npm run check` plus the unit test files the diff touches. A task
that touches no engine source runs the site's own unit suite and nothing from cairn-cms.

**Worktree setup**: The launch's `.claude/worktrees/<name>`, then `npm ci` and `npx svelte-kit
sync`. The sync writes `.svelte-kit/tsconfig.json`, which `npm run check` needs, so a fresh
worktree's first gate fails without it.

## Closing a task

**Full-suite home**: The table's column. No site except aksailingclub-org has PR test CI (ruling
11), so the local close run is the only full run; each site's BACKLOG carries an item for it.
Run the local close once, on the close head. Cross-repo specs, plans, and research live in
`~/Projects/initiatives/<id>/`, not in the site repo.

**CI watch**: Only aksailingclub-org: `gh pr checks <n> --watch --fail-fast` as a background Bash
task after each push. The other three sites have no watch command.

**Risk-class path map**: `auth-data` for every site: `src/hooks.server.ts`, `src/routes/admin/**`,
`wrangler.*`. aksailingclub-org adds `src/member-auth/**`, `src/member-signup/**`,
`src/admin-club/**`, `migrations/**`, and `data/membershipworks/**` (member PII).
cairn-pub adds `migrations/**`. `runner` for `.github/workflows/**` and `scripts/**`; `ordinary`
otherwise.

**Checklist globs**: The close review loads `standards:svelte-reviewer` for `**/*.svelte` and load, action, or
hook code; `standards:cloudflare-workers-reviewer` for Worker, D1, and `wrangler.*`;
`standards:web-auth-security-reviewer` for every `auth-data` glob; `standards:daisyui-a11y-reviewer` for markup and
styles; `standards:content-review` for website content under `src/content/**`. `standards:visual-verifier` reads
rendered pages.

**Close checklist**: Beyond `building-from-specs` "Gates and review":

- The local close run above, where the site has no PR CI. None of these gates scopes gitleaks to a
  change set, so no branch-history scan is owed.
- Add the task's design decisions to the site's architecture doc (decisions, not narration) and keep the
  README and config comments current.
- Archive the spec with `git mv` from the site's specs directory to its archive (usually
  `docs/specs/<name>.md` to `docs/archive/specs/`) once its last task merges.
- List the cairn backlog items the task found under "Cairn backlog" in the PR body, verified against cairn-cms.
  A cairn session files it in cairn-cms's `BACKLOG.md`. A UI mechanic that
  belongs to the engine follows `~/.claude/docs/engine-ui-mechanics.md`.
- Commit specific files only, one commit per step.

## Following cairn-cms docs during a task

A divergence between a cairn-cms docs page and reality is fixed on the page in the same change, per
cairn's fix rule in its `CLAUDE.md`: edit on a `site-docs/<site>-<task>` branch off cairn-cms `main`,
merged by PR under the docs gate before the site task's pull request is marked ready. Never edit cairn-cms `main` directly.
The `cairn-writing-docs` skill loads only in a cairn-cms session, so read its steps from
`~/Projects/cairn-cms/.claude/skills/cairn-writing-docs/SKILL.md` before the edit and follow them there.

## When not to use

The cairn-cms engine's own work (`cairn-pass`), debugging in the middle of a task, and a typo or
content fix.
