# Global Claude Code Patterns -- Workstation: thinkpad-x1

## Work Autonomously Until Done

Do not ask for review or approval until the task is fully complete; keep working until every
quality gate passes. Stop only for a genuine blocker needing information only the user can
provide.

## The pass process lives in `pass-core`

Planning, executing, and closing a pass is the `pass-core` skill, with `cairn-pass`, `site-pass`,
and `dotfiles-pass` as per-repo adapters. Invoke it for any planned pass. Geoff's touchpoints are
the design in chat and the PR.

## Search before you spelunk (Geoff, 2026-07-13)

When a symptom looks framework- or library-specific, spend one web search on the exact symptom
before an interactive debugging loop: a documented quirk or GitHub issue often names the cause.
Never read a file's "current state" while a background agent edits it. Detail:
`~/.claude/docs/claude-md-archive.md`.

## One executor per worktree (Geoff, 2026-07-14)

Before launching any executor into a repo or worktree (a Workflow, an agent dispatch, inline
edits), verify none is already working it: `pgrep -f <worktree path>`, `git status` for warm
uncommitted changes you did not author, other sessions' workflow journal mtimes, and the status
docs. When in doubt, ask rather than race. Warm uncommitted code at dispatch time is a
stop-and-investigate signal, never free progress. Two sessions never both close, merge, or release
one branch. Mid-flight contention: stop editing contested files, wait for the other's commit,
verify it, report verified.

## Machine Environment

- **OS**: Bluefin DX, `stable` stream (Fedora 44 base, bootc/ostree)
- **Desktop**: GNOME (Wayland) | **Shell**: bash | **Terminal**: Ptyxis. kitty exists only for
  the `tui-visual-verify` gate, never the daily terminal.
- **Key paths**: `~/Projects/` (repos), `~/.dotfiles/`, `~/.local/bin/` (scripts)
- **Dev tools**: Node via mise, Python via uv, Go via Homebrew, Java 17 for Android
  (`~/Android/`, `ANDROID_HOME` set in `.bashrc`)
- **Browsers**: Firefox is the daily browser; Claude Code drives Chromium (`chromium-browser`).
  Artifacts open in Chromium; sitting pages and mockups open in Firefox, so a rendering issue
  there surfaces (Geoff, 2026-09-28). Never a Flatpak build of either (the sandbox blocks native
  messaging); read `~/.claude/docs/bluefin-admin.md` before browser work.

## Sysadmin Preferences

- **Troubleshooting**: Search the web after 1-2 failed attempts, with "Bluefin DX" in the query
- **sudo**: `sudo -A` via `claude-askpass` (tmpfs cache); stale cache -> `claude-sudo-setup`
  (1Password unlocked); failures -> GID gotcha in `bluefin-admin.md`.
- **Software tiers**: mise/uv runtimes, Homebrew CLI, Flatpak GUI, distrobox/devcontainers for
  dev envs, rpm-ostree layering last resort (`bluefin-admin.md`; source of truth
  `~/.dotfiles/bluefin/layered-packages.txt`).
- **Destructive ops**: Show a dry run or confirmation step first
- **Home dir minimal**: scripts -> `~/.local/bin/`, configs -> `~/.config/`; check
  `~/.dotfiles/` first. `/etc` changes land in `~/.dotfiles/bluefin/etc/` first, then install
  from there; never edit `/etc` directly. micro is the editor; Neovim is not installed, never
  suggest it.

## Calm desktop (Geoff, 2026-09-29)

Only critical items interrupt: Do Not Disturb stays on, the dock shows no badges, and a new app
gets its popups, sounds, and badges off at install. A notifying script uses normal urgency unless
Geoff must act now (`bluefin-admin.md` "Calm desktop").

## Dotfiles Management

`~/.dotfiles`, GNU Stow (`bluefin/stow-packages.txt`). **Every install records itself in its
tier's manifest, same session** (`bluefin-admin.md`); `check-drift` reconciles. Repo gate:
`scripts/check.sh`. New script: `bin/.local/bin/` + `stow -R bin`.

## Git Conventions

- Imperative mood: "Add feature" not "Added feature"
- Commit specific files, not `git add -A`
- Never commit .env files or secrets; never force push to main/master

## Dependencies (Geoff, 2026-09-13 and 2026-09-14)

Every dependency bump in every repo goes through the `dependency-upgrade` skill (a sweep, a bot PR,
a package taken for a feature, "are we current"). Take every minor and patch by default; always ask
before a major. A release starts from every dependency's newest production version.

## Go Development

**MANDATORY: invoke `go-conventions` before writing any Go code.** For bubbletea UI, also
invoke `elm-conventions`; before claiming any TUI screen works, and at every TUI pass gate,
invoke `tui-visual-verify`: only a screenshot of the real terminal is evidence.

## Cloudflare and API-first

**FULL ACCOUNT ACCESS (2026-07-06).** Make routine changes directly; never treat Cloudflare state
as read-only. The MCP token is read-only for Access/Workers-domain writes; use curl with
`$CLOUDFLARE_API_TOKEN` for those. The token lives in `~/.local/secrets`, sourced for interactive
shells only, so a script must `source ~/.local/secrets` itself. Account id, token scopes,
D1/R2/workers/Access, and how each secret is reached: `~/.claude/docs/cloudflare-estate-inventory.md`;
read it before hunting a credential or provisioning infra. Use an API or CLI first for external
services, and never suggest a web dashboard unless the API cannot do it.

## Secrets

- **Never commit**: API tokens, passwords, keys, `.env` files with real values. **Local dev**:
  `~/.bashrc` (non-sensitive) or `~/.local/secrets` (sensitive). **CI/CD**: GitHub Actions
  secrets. **Runtime**: Cloudflare Workers secrets.
- **A new long-lived secret originates in the workstation age store** (`secret-set.sh`), never
  a loose file, never only `wrangler secret put`. **A value from Geoff arrives via
  `secret-receive NAME`**, never pasted into chat. **1Password has sudo semantics**: fetch once
  per session, parse locally, never loop `op`.
- **Check the stores before claiming a secret is missing**: `wrangler secret list`,
  `~/.local/secrets`, the age registry, per-project stores, the estate inventory. Name-only
  checks, never print values.
- Full flows, exceptions, and store order: `bluefin-admin.md` "Secrets".

## Other workstation services

- **Google Docs / Drive / Sheets**: `gws` CLI, never an MCP server. Auth modes and write
  patterns: `bluefin-admin.md` "Google Docs / Drive (gws)".
- **Email**: poplar (`~/Projects/poplar/`, Fastmail via JMAP; API reference
  `~/.claude/instructions/fastmail-api.md`). Thunderbird is interim; its theme changes go only
  through `~/.dotfiles/thunderbird/`.

## Claude tooling: manifests, scopes, and the DaisyUI-first rule (Geoff, 2026-09-13)

Every skill, agent, MCP server, and plugin has one home and one manifest, reconciled by
`claude-tooling-sync verify` (run by `check-drift`): layout and rules in
`~/.claude/docs/claude-tooling.md`, read before adding any. Every cairn-family admin is DaisyUI:
prefer a stock component over a home-grown one unless the rulings ledger records the defect that
forced it (the official DaisyUI skill is the reference, the licensed Blueprint server the pre-cut
audit; the admin design system wins over both on conflict).

## cairn-family work

- **Visual fidelity (2026-07-05)**: UI work that must match a reference invokes the
  `visual-fidelity` skill at the start and gates on `visual-verifier`; nothing deploys to
  production without a full-page render read in the main loop.
- Cairn friction and engine-level UI mechanics (a UI mechanic belongs to cairn, a design choice
  to the site) follow `cairn-pass` and `site-pass`.

## Claude Code Agent Usage

No human-scale time estimates in conversation; describe relative complexity ("quick",
"multi-step") and focus on sequencing, dependencies, and testing. Plan tasks carry clock estimates
in minutes, per `pass-core`. Every dispatch names a model and an effort, and subagents start with
zero context: pre-extract what they need.

## A rule lives where it executes (Geoff, 2026-09-20)

A rule reaches an agent only through its definition, its dispatch prompt, its runner, or a
tool's output; a side doc reaches nobody. Land a rule the same session, strongest form first:
tool, agent definition or skill, then CLAUDE.md (Geoff, 2026-09-27). Anything recorded routes
by default: initiative state to STATUS or ROADMAP; a repo fact to its docs; a workstation fact
to `~/.claude/docs`. Memory holds only a preference or a ruling's why that no file can. Act on
a tool's NOTE before the next dispatch.

## Compact instructions

Preserve the plan path; the task ledger (done, in flight, next) and the task in flight with its
clock file; open decisions; the last CI and review verdicts; and the STATUS launch prompt. Drop
tool output, diffs, and agent transcripts.

## Multi-agent workflows: suggest, never launch unprompted

The Workflow tool runs only on Geoff's explicit opt-in ("use a workflow"); when a task would
clearly benefit, suggest it in one sentence with shape and scale. Past ~30 minutes of unattended
work, arm the wake-up and guards `~/.claude/docs/unattended-work-guards.md` names.

## Initiative-scoped sessions

One session per initiative: every turn re-reads the whole cached conversation. Close the session
when an initiative lands, and prefer dispatching reads.

## Process proportionality

Interaction is batched and front-loaded (Geoff, 2026-09-04). Before approval, probe requirements
and design until the plan carries no open readings, one question at a time with a recommendation.
After approval, execution runs to completion with no per-task check-ins; batch judgment calls into
one question and stop early only for a genuine blocker or scope change.

Method, idiom, and architecture calls are Claude's (Geoff, 2026-09-24 and 2026-09-26): decide them
from published evidence, the framework's documented convention, or architectural best practice,
bring the whole design for one approval, and flag only contestable points. Questions to Geoff are
for product, taste, priority, scope, and budget.

A change touching a handful of files, fully specified by the request or existing tests, with no new
public surface, schema, or auth behavior, goes straight through the gates.

## Writing voice

Every audience starts from a published external standard, and a repo may carry a named house voice
as a recorded overlay that never replaces the base's structure, each departure with provenance and
Geoff's ruling. The `writing-voice` output style carries the core, the `writing-voice` skill routes
to each standard, and `~/.claude/docs/authoring-charter.md` holds the map. **Name the audience and
load its standard before drafting**; site content uses the site repo's own content guide. Cairn's
docs voice is the named overlay: every published cairn page, and cairn.pub's own prose, follows the
developer brief (editor docs, the editor brief) in
`~/Projects/cairn-cms/docs/internal/docs-register.md`. Vale, the comment linters, and `tellgrader`
are the deterministic net; clean is necessary, never sufficient.

The em dash is banned in code comments (linter-enforced); developer docs follow Google (no
spaces), editor copy Microsoft, replies and commits go without. Overuse is a tell anywhere.
