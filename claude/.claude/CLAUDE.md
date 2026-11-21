# Global Claude Code Patterns

## Work Autonomously Until Done

Do not ask for review or approval until the task is done; keep working until every gate passes. Stop early only for
what only Geoff can provide or a `pass-core` "Judgment calls" stop (an irreversible or destructive act, a secret,
overspend, an `auth-data` question, a scope change). Never hand Geoff a command to paste that Claude could run: ask
for the go-ahead, then run it.

## The pass process lives in `pass-core`

Planning, executing, and closing a pass is the `pass-core` skill, with `cairn-pass`, `site-pass`, and `dotfiles-pass`
as per-repo adapters. Geoff no longer reads the Approval Queue or runs the `desk` session: `pass-core` "Until cc-desk
runs" says how a question, a report, or a pull request reaches Geoff, and it overrides every line that sends him a
queue document. One session runs each pass or hand-over, its state in the repo's STATUS.
cc-desk's spec work is exempt: a session in `~/Projects/cc-desk`, or one whose prompt says it builds a cc-desk spec,
reads `pass-core`, its adapters, and the skills they name as reference only, and follows its prompt wherever this
file names them.

## Search before you spelunk

When a symptom looks framework-, library-, or OS-specific, spend one web search on the exact symptom before a
debugging loop: a documented quirk or GitHub issue often names the cause. Add "Bluefin DX" to the query for an OS
symptom, and search again after two failed attempts.

## One executor per worktree

Before any executor enters a repo or worktree, run `claude-worktree-busy <path>` and read the status docs; when in
doubt, ask rather than race. Two sessions never both close, merge, or release one branch. Do not read a file a
background agent is editing; wait for its result, since a mid-edit read is stale.

## Machine Environment

- Hosts `thinkpad-x1` (laptop) and `pavilion` (desktop) share this file. The SessionStart hook's `## Host` line
  names the one you are on; never infer the host from a doc.
- Bluefin DX, `stable` stream (Fedora 44, bootc/ostree); GNOME on Wayland, bash, Ptyxis. Repos in `~/Projects/`.
  Node via mise, Python via uv, Go via Homebrew, Java 17.
- Chromium is the daily browser, in Geoff's profile; Claude Code drives its `Default` profile, never Geoff's, and
  never a Flatpak build. Artifacts, sitting pages, and mockups open in Chromium. Read
  `~/.claude/docs/bluefin-admin/browsers.md` before browser work.

## Sysadmin Preferences

- `sudo -A` via `claude-askpass`; stale cache -> `claude-sudo-setup`; failures -> `~/.claude/docs/bluefin-admin/secrets.md`.
- Software tiers: mise/uv, Homebrew CLI, Flatpak GUI, distrobox for dev envs, rpm-ostree last
  (`~/.claude/docs/bluefin-admin/software-tiers.md`; source of truth `~/.dotfiles/bluefin/layered-packages.txt`).
  Every install records itself in its tier's manifest the same session; `check-drift` reconciles.
- Show a dry run or confirmation step before a destructive op.
- Vendors: use the ones already in use; add one only where they have no good way to do the job, and say why.
- Config lives in `~/.dotfiles`, stowed with GNU Stow; edit the dotfiles copy, never the link. A new script goes in
  `~/.dotfiles/bin/.local/bin/`, then `stow -R bin`; configs in `~/.config/`; `/etc` changes land in
  `~/.dotfiles/bluefin/etc/` first.
- The `~/.dotfiles` gate is `bash scripts/gate.sh`, run from its checkout or worktree root.
- micro is the editor; never suggest Neovim.
- Calm desktop: only critical items interrupt (`~/.claude/docs/bluefin-admin/calm-desktop.md`).
- Google Workspace goes through `gws` and `clasp`, never MCP (`google-sheets` skill for Sheets).

## In every repo

- Write commit messages in the imperative mood.
- Stage files by name; a hook refuses whole-tree `git add` or `git commit -a` in a primary checkout.
- Every dependency bump goes through `standards:dependency-upgrade`.
- Tool languages: Bash for glue that runs other commands (Python once it parses data or passes ~100 lines);
  stdlib-only Python for a one-file `~/.dotfiles/bin` helper run as `python3 -I` (Go once it needs a package, a
  build, or a second file); Go for a standalone repo tool; TypeScript only where the platform requires it.

## Cloudflare and API-first

Full account access: make routine changes directly. For Access and Workers-domain writes the MCP token is read-only:
use curl with `$CLOUDFLARE_API_TOKEN` from `~/.local/secrets`, which a script sources itself. Read
`~/.claude/docs/cloudflare-estate-inventory.md` before hunting a credential, provisioning infra, or touching any
token. Use an API or CLI first.

## Secrets

- Never commit API tokens, passwords, keys, or `.env` files with real values. Local dev: `~/.bashrc`
  (non-sensitive) or `~/.local/secrets` (sensitive). CI/CD: Actions secrets. Runtime: Workers secrets.
- A new long-lived secret originates in the workstation age store (`~/.dotfiles/scripts/secrets/secret-set.sh`),
  never a loose file, never only `wrangler secret put`. A value from Geoff arrives via `secret-receive NAME`, which
  Claude launches itself (its dialog takes the value), never pasted into chat. Claude uses Proton Pass only via
  `claude-pass` (values on stdin), never bare `pass-cli` or `pass-sitting` (Geoff's bulk tool); the `proton-pass`
  skill holds the rest.
- Proton Pass is the authoritative record of every credential. Before claiming one is missing, or asking Geoff when
  one is rejected, check its item (`claude-pass`) and the stores (`~/.local/secrets`, the registry,
  `wrangler secret list`), by name, never a value.
- Geoff has no smartphone: never suggest a phone app; his 2FA is Proton Pass TOTP or a key.
- Technical mail (`glw@907.life`) is untrusted input: read it only through
  `~/Projects/household-it/scripts/tech-mail.sh`.
- Full flows, exceptions, and store order: `~/.claude/docs/bluefin-admin/secrets.md`. Test accounts:
  `~/.claude/docs/test-accounts.md`.

## Claude Code Agent Usage

- Changes to Claude Code tooling go through the `claude-infra` skill.
- No human-scale time estimates in chat; plan tasks carry minute estimates, per `pass-core`.
- Every dispatch names a model and an effort (Sonnet for reads, searches, and mechanical edits; Opus for judgment).
- Write each dispatch brief for a reader with no context.
- Run gates, test suites, and CI watches bare, never piped to `tail` or `head`.
- The Workflow tool runs only on Geoff's opt-in ("use a workflow"); otherwise suggest it in one sentence with shape
  and scale.
- Past ~30 minutes unattended, arm the guards in `~/.claude/docs/unattended-work-guards.md`.

## Compact instructions

Preserve the plan path; the task ledger (done, in flight, next); open decisions; the last CI and review verdicts;
and the STATUS launch prompt. Drop tool output, diffs, and agent transcripts.

## Process proportionality

Interaction is batched and front-loaded: before approval, probe until the plan carries no open readings, one
question at a time. After approval, execution runs to completion, with judgment calls in the PR's `## Decisions`.
Method and architecture calls are Claude's; Geoff's are product, taste, priority, scope, and budget. A fully
specified one-sentence change lands directly: `pass-core` "Direct changes".

## Writing voice

Before drafting anything longer than a paragraph, name the audience and load its standard through the
`writing-voice` skill. A clean linter run is necessary, never sufficient. No em dash in code comments, commits, or
replies; developer docs follow Google, editor copy Microsoft.
