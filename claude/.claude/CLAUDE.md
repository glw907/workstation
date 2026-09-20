# Global Claude Code Patterns -- Workstation: thinkpad-x1

## Work Autonomously Until Done

Do not ask for review or approval until the task is fully complete; keep working
until every quality gate passes. Stop only for a genuine blocker needing
information only the user can provide.

## Search before you spelunk (Geoff, 2026-07-13)

When a symptom looks framework- or library-specific (a form that will not submit, a build that
fails in one runtime, an API rejecting a shaped request), spend one web search on the exact
symptom BEFORE opening an interactive debugging loop: a documented quirk or GitHub issue often
names the cause in one shot that hands-on probing reaches only after many expensive main-model
turns (proven twice 2026-07-13). Both budgets favor the search. Corollary: never read a file's
"current state" to draw conclusions while a background agent is editing it; you will read a
half-applied change. Verify against committed state or wait for the agent.

## One executor per worktree (Geoff, 2026-07-14)

Before launching ANY executor into a repo or worktree (a Workflow, an implementer dispatch,
inline main-loop edits), verify no live executor is already working it: `pgrep -f <worktree
path>`, `git status` for warm uncommitted changes you did not author, other sessions' workflow
journal mtimes, and the status docs (a "fresh session executes this" line means one may
already be running; when in doubt, one sentence to Geoff beats a race). Warm uncommitted code
at dispatch time is a stop-and-investigate signal, never free progress. If a live executor is
found, stand down or coordinate: two conductors never both run a close ritual, merge, or
release on one branch. Mid-flight contention: stop editing contested
files, wait for the other's commit, verify it, report verified. (Born 2026-07-14: two
workflows raced one worktree; ~1.2M duplicated tokens.)

## Machine Environment

- **OS**: Bluefin DX, `stable` stream (Fedora 44 base, bootc/ostree)
- **Desktop**: GNOME (Wayland) | **Shell**: bash | **Terminal**: Ptyxis. kitty exists
  only as the `tui-visual-verify` gate (XWayland-forced for capture); never the
  daily terminal.
- **Key paths**: `~/Projects/` (repos), `~/.dotfiles/` (config), `~/.local/bin/` (scripts)
- **Dev tools**: Node via mise, Python via uv, Go via Homebrew, Java 17 for
  Android tooling (`~/Android/`, `ANDROID_HOME` set in `.bashrc`)

## Browsers: Firefox + Chromium, no Flatpak

Firefox (layered RPM) is the daily browser, with 1Password integration. Chromium
(layered RPM) is the dev/testing browser Claude Code drives (claude-in-chrome,
chrome-devtools MCP, `chromium-shot`); the binary is `chromium-browser`. Never a Flatpak
build of either: the sandbox blocks required native messaging. Read
`~/.claude/docs/bluefin-admin.md` before browser or extension work.

## Sysadmin Preferences

- **Troubleshooting**: Search web after 1-2 failed attempts, with "Bluefin DX"
  or "Universal Blue" in the query
- **sudo**: `sudo -A` via `claude-askpass` (tmpfs cache); stale cache ->
  `claude-sudo-setup` (1Password unlocked); failures -> GID gotcha in
  `bluefin-admin.md`.
- **Software tiers**: mise/uv runtimes, Homebrew CLI, Flatpak GUI,
  distrobox/devcontainers for dev envs, rpm-ostree layering last resort; source
  of truth `~/.dotfiles/bluefin/layered-packages.txt` (additions also recorded
  in `docs/MIGRATION-BRIEF.md`); policy and command map: `bluefin-admin.md`.
- **Destructive ops**: Show dry-run or confirmation step first

## System Organization

- Home dir minimal: scripts -> `~/.local/bin/`, configs -> `~/.config/`;
  check `~/.dotfiles/` first
- `/etc` changes land in `~/.dotfiles/bluefin/etc/` first, then install from
  there; never edit `/etc` directly (see `bluefin-admin.md`)
- micro is the editor; Neovim is not installed, never suggest it.

## Dotfiles Management

- **Location**: `~/.dotfiles`, GNU Stow; packages listed in
  `bluefin/stow-packages.txt`
- **Every install records itself in its tier's manifest, same session**
  (map: `bluefin-admin.md`); `check-drift` reconciles, a weekly timer
  notifies on drift. Repo gate: `scripts/check.sh`. New script:
  `bin/.local/bin/` + `stow -R bin`.

## Git Conventions

- **Before committing code changes, run Anthropic's official `code-simplifier` agent** over the code you just changed (dispatch the `code-simplifier` subagent). It refines recently-changed code preserving behavior; apply its refinements, then commit. Docs-only commits don't need it. Skip only when explicitly told to. (poplar keeps its own Go-aware `simplify` skill.)
- Imperative mood: "Add feature" not "Added feature"
- Co-authored footer: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Commit specific files, not `git add -A`
- Never commit .env files or secrets; never force push to main/master

## Dependencies (Geoff, 2026-09-13 and 2026-09-14)

Every dependency bump in every repo goes through the `dependency-upgrade` skill: a pre-release
sweep, a bot PR, a single package taken for a feature, or a question like "are we current". Take
every minor and patch by default; always ask before a major. The bump is not done at the lockfile:
each one carries a changelog survey and a refactor decision on every new capability (take now,
file, or propose a formal refactoring pass). The goals are staying current so debt never
accumulates, and letting an upstream improvement improve our own code. A release starts from the
newest production version of everything.

## Go Development

**MANDATORY: Invoke the `go-conventions` skill before writing ANY Go code.** Every Go file, function, test, and error message must conform. (For bubbletea UI work, additionally invoke `elm-conventions`; before claiming any TUI screen works, and at every TUI pass gate, `tui-visual-verify`: goldens and tmux captures check text, only a screenshot of the real terminal is evidence.)

## Cloudflare / Wrangler

**FULL ACCOUNT ACCESS (Geoff, 2026-07-06).** Make routine changes directly; never treat
Cloudflare state as read-only. The MCP token is read-only for Access/Workers-domain writes;
use curl with `$CLOUDFLARE_API_TOKEN` for those. Account id, the ASC Access service-token
route, and the full authorization model: `~/.claude/docs/cloudflare-estate-inventory.md`.

- `npx wrangler deploy` / `dev` / `secret put NAME` / `tail`
- `CLOUDFLARE_API_TOKEN` in `~/.local/secrets` (sourced for interactive shells only; a
  script must `source ~/.local/secrets` itself). Exact scopes: the estate inventory doc
  below, the canonical record every project defers to.

## API-First Policy

Use API or CLI first for external services -- never suggest the web dashboard unless the API cannot do it. Check `.claude/instructions/api-access.md` in each project for the specific access inventory.

## Secrets

- **Never commit**: API tokens, passwords, keys, `.env` files with real values
- **Local dev**: `~/.bashrc` (non-sensitive) or `~/.local/secrets` (sensitive, sourced from 1Password)
- **CI/CD**: GitHub Actions secrets | **Runtime**: Cloudflare Workers secrets
- **1Password: sudo semantics, never a loop.** The first `op` call in a session fires ONE
  desktop approval; that is the session's authentication, and later calls ride it. Fetch
  once (`op item get <id> --format json`) and parse locally. The `claude-block-op` hook
  enforces only the loop half: 3+ `op` calls in a minute deny (ruling 2026-08-16:
  authenticate once per session, like sudo). Passkeys are used, never
  read: a passkey-gated flow routes through the browser, Geoff's touch as approval.
- **Installing a NEW long-lived secret, every project (Geoff, 2026-07-13): the workstation
  age store is the origin, never a loose file and never only `wrangler secret put`.** The flow:
  `~/.dotfiles/scripts/secrets/secret-set.sh NAME --value|--file|--b64-file` (writes
  `values.age`, regenerates `~/.local/secrets`; 1Password holds only the age key, fetched once
  per session), then document scope + rotation in `~/.dotfiles/secrets/registry.md`, add the
  worker to `sync.sh`'s WORKER_SECRETS routing if a Worker consumes it, push with
  `sync.sh --worker NAME`, and confirm with `sync.sh --verify`. Delete any loose key file once
  stored; the upstream issuer (GCP IAM, GitHub App settings, ...) is the mint-a-new-one origin.
  Exception: ASC secrets use the ASC per-project store (`aksailingclub-legacy/secrets/`), and
  per-site rotatable HMAC keys (MAGIC_LINK_SECRET/SESSION_SECRET) stay worker-only by design.
- **Receiving a secret value FROM Geoff (Geoff, 2026-08-31): Claude runs
  `secret-receive NAME [--hint …|--op REF]` — a desktop paste dialog (or 1Password read)
  piped straight into the age store. Never offer paste-into-chat or hand-run commands.**
  Wire the name first (manifest, registry `pending`, consumer config); flip the registry ✓
  after the mint.
- **Cloudflare estate + how each secret is reached**: `~/.claude/docs/cloudflare-estate-inventory.md`
  (values-free inventory of D1/R2/workers/Access + the authorization model; worker secrets are
  write-only, so a value comes from its origin store, not the worker). Read it before hunting a
  credential or provisioning infra.
- **Check the stores before claiming a secret is missing.** Status docs record intent; the
  stores record what happened. Before telling Geoff a credential is owed, check in order:
  `npx wrangler secret list` (per worker), `~/.local/secrets`, the age registry
  (`~/.dotfiles/secrets/registry.md`), per-project stores (a repo's `secrets/` dir + sync
  script; ASC's is `aksailingclub-legacy/secrets/`), and the estate inventory above. If none
  has it, that is the finding, not "Geoff owes a paste." Name-only checks, never print
  values. (Born 2026-07-07, twice, both false "you still owe me X" reports.)

## Google Docs / Drive (gws)

`gws` (Google Workspace CLI, Homebrew `googleworkspace-cli`) is the path to Google Docs,
Drive, and Sheets; never an MCP server for these. Personal docs: OAuth as Geoff's own Google
account (`gws auth login -s docs,drive`; the Desktop OAuth client pair lives in the age store
as `GOOGLE_WORKSPACE_CLI_CLIENT_ID` / `_CLIENT_SECRET`). ASC docs only: the club service
account via `GOOGLE_APPLICATION_CREDENTIALS`, which `gws` also honors; unset it if it
shadows the personal login. Formatting edits go through `docs documents batchUpdate` after a
`get` for indexes; `--dry-run` first on any write. Patterns: `google-docs-formatting` memory.

## Email (poplar)

poplar, a bubbletea terminal email client from `~/Projects/poplar/`; binary
`~/.local/bin/poplar` (`make install`). Fastmail via JMAP,
`$FASTMAIL_API_TOKEN` in `~/.local/secrets`. API reference:
`~/.claude/instructions/fastmail-api.md`.

## Claude tooling: manifests, scopes, and the DaisyUI-first rule (Geoff, 2026-09-13)

Every skill, agent, MCP server, and plugin on this workstation has one home and one manifest,
and `claude-tooling-sync verify` (run by `check-drift`) reconciles them: layout, rules, and
procedures in `~/.claude/docs/claude-tooling.md`. Read it before adding any of them. Two rules
inline: a skill on disk reaches every agent while an MCP server reaches only the main loop, so
take the skill first; and every cairn-family admin is DaisyUI, so prefer a stock DaisyUI
component over a home-grown one unless the engine's rulings ledger records the defect that
forced it (the official DaisyUI skill is the reference, the licensed Blueprint server the
pre-cut audit; the admin design system wins over both on conflict).

## Visual fidelity (all projects, 2026-07-05)

Any UI work that must MATCH an existing reference (a rebuild, a theme port, a migration)
invokes the `visual-fidelity` skill at the start and gates on the `visual-verifier` agent.
Core rules even without the skill: reference screenshots before any plan (never build from a
verbal description); the context that built the UI never grades it; nothing deploys to
production without a full-page render read in the main loop; user-facing sites get Geoff's
before/after. (Born from two same-day production misses.)

## Engine-level UI mechanics, every cairn site (Geoff, 2026-07-30; consultation 2026-08-26)

A UI **mechanic** belongs to cairn. A design **choice** belongs to the site. A mechanic
recurs in any component of that shape on any cairn site. Patching one in a site's own theme
leaves every sibling site to rediscover it. "This repo has patched this before" is an
automatic filing trigger, never a reason to patch it faster. Full protocol, the
consultation-first path, and the mid-pass filing fallback:
`~/.claude/docs/engine-ui-mechanics.md`.

## Claude Code Agent Usage

No human-scale time estimates; describe relative complexity ("quick",
"multi-step") and focus on sequencing, dependencies, and testing steps.

## Conducting a pass

Two co-equal budgets govern every initiative at the same quality bar: total tokens spent and
Geoff's attended time. Clock time is a watched metric, never a budget. Attended time is spent
front-loaded: understanding requirements and design comes first, and the back-and-forth it
takes is that budget's best use (Geoff, 2026-09-04). After plan approval, tokens buy anything
research, verification, or a retry can resolve; attended time buys only taste, priorities, and
product forks. Parallelize wherever tasks are genuinely independent (Geoff, 2026-09-03);
serialize only under real contention or dependency, and name the contended resource. Plans
mark independent tasks so pass-execute's parallel mode can take them.

Fable conducts coding projects from brainstorm through post-mortem in one session. The
plan-approval gate is the single human gate. **The
conductor is thin:** during execution it never reads a source file, a diff, a test log, or a
gate transcript. It consumes structured agent reports and decides only what needs judgment
(accept, re-dispatch with a correction, split, upshift, stop). A conductor caught reading
diffs or grinding edits inline flags itself and dispatches.

Each plan task runs as a chain. The repo's Sonnet implementer returns a fixed shape (files
touched, gate result, decisions the plan did not cover, anything it could not do). The
`diff-reviewer` agent (`claude-opus-5`) reads the diff against the task's acceptance criteria
and returns accept, fix, or escalate with `file:line` findings. The repo's full gate runs
inside the chain, never in the main loop. One re-dispatch on `fix`; a second `fix` is the
conductor's decision. Domain reviewers still fan out at pass end. Below six tasks, dispatch
the chain per task with the Agent tool; at six or more, or when the plan marks tasks
independent, run `~/.claude/workflows/pass-execute.js` (a plan
naming the mode is the opt-in). A pass's close task is authored by one fold agent, which
commits its draft and then folds, with one independent `diff-reviewer` read over the fold's
diff (Geoff, 2026-09-12). The default plan-review fan-out is three disjoint lenses,
contract-and-criteria, mechanics-and-feasibility, and domain-risk, with staleness moved into
the drafter's own pre-flight and the fold capped at one dispatch (Geoff, 2026-09-12).

Every dispatch names a model and an effort: `sonnet` by default, `haiku` for mechanical
search, `claude-opus-5` for reviewers (cross-model diversity). A dispatch without a model
falls to `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` (settings `env`); a frontmatter pin or a
per-dispatch model wins, so upshifts pass `model` explicitly: `opus` for novel
correctness-critical logic the plan does not specify, `fable` only when an Opus verdict
hedges on something that matters. Effort defaults to `medium` (settings, Geoff 2026-09-04);
raise it to `high` for plan authorship, adjudication, and research turns, never lower it to
`low` (Fable 5.1 at `low` answers from memory); `max` is for one adjudication. `/effort`
persists to settings.json; reset it at session end. Subagents start with zero context:
pre-extract what the task needs. When a dispatch runs slow, expensive, or weak, check which
model ran.

Every pass plan header carries a token ceiling and a checkpoint interval (default four
tasks). At each checkpoint, at any split, and before any question to Geoff, write STATUS
(task ledger, decisions taken, spend, next task), then continue and rely on compaction. At
80% of the ceiling, finish the task, write STATUS, and ask one combined question; check that
flag at each segment boundary, the only place a decision can land (Geoff, 2026-09-12).
Segment a pass at three to four tasks, every boundary on a commit the gate proved green; the
count, never the placement, is overridden by an irreversible task, a second `fix` verdict, or
a seam where a task's Files are disjoint from the next's (Geoff, 2026-09-12). At a window's
end with the next work hours away, close the session rather than re-prime it after the idle
gap (Geoff, 2026-09-12). Pre-bake
before executing: commit the plan, point STATUS at it, refresh memory; anything load-bearing
lives in an artifact, never only in the conversation. Do not run the `writing-plans` "which
execution method?" question. Fable on Max draws from the weekly pool up to a 50% cap; its
metering is unpublished, so minimize Fable context, never Fable turns
(`~/.claude/docs/model-economy.md`).

## Gate economy on a pass (Geoff, 2026-09-09; evidence from cairn chassis-B2)

Clock time on a pass is the per-task gate and the fix rounds, not the implementer. Gates run
through `cairn-run-gate '<string>'` (dotfiles bin; generic despite the name): on exit 75,
re-issue the same command until it prints `gate exit:`; never poll a log. A gate that
launches no browser (a Go `make check`, a lint-only run) sets `CAIRN_GATE_LANE=light`: its own
lock and a 3G cap, so it never queues behind another session's browser gate (2026-09-20). The Workflow tool
refuses a `~/.claude/workflows` scriptPath (copy to the session scratchpad). Full rule set:
`~/.claude/docs/pass-gate-economy.md`.

## A rule lives where it executes (Geoff, 2026-09-20)

A rule reaches an agent only through what that agent is given: its definition, its dispatch
prompt, the runner that builds the prompt, or the tool's own output. A rule written only in a
side doc reaches nobody, because subagents start with zero context and a conductor reads a side
doc only if something sends it there. Cairn Go tool pass A lost two to three hours this way: the
light-gate opt-out existed, in an uncommitted paragraph of `pass-gate-economy.md`, and no runner,
agent definition, plan, or skill carried it. So when a rule is written or learned, land it in the
execution path in the same session, strongest form first: the tool enforces or announces it
(`cairn-run-gate` now prints a NOTE when a heavy gate waits on the lock); else the runner renders
it into the prompt (`gateLane`); else the agent definition or the skill states it; a doc alone is
the record, never the delivery. Two habits follow. Before relying on a workstation tool for a
whole pass, read its header or `--help` once, since the tool is the spec and the summary in this
file is not. And when an agent's report carries a tool's NOTE, act on it before the next dispatch.

## Compact instructions

Preserve the plan path and pass number; the task ledger (done, in flight, next); open
decisions and the last `diff-reviewer` verdict; the token ceiling and spend so far; and the
STATUS resume prompt. Drop tool output, diffs, and agent transcripts.

## Multi-agent workflows: suggest, never launch unprompted

Outside a pass plan that names the workflow mode, the Workflow tool runs only on Geoff's
explicit opt-in ("use a workflow"). When a task would clearly benefit (a large adversarial
review gate, a repo-wide audit or migration, deep research) suggest it in one sentence with
the shape and rough scale.

**Guards on long unattended work, both mandatory.** Past ~30 minutes, arm the runaway guard.
On battery, arm the battery watchdog. GNOME suspends after 15 idle minutes on battery; check
`journalctl` for suspends before calling it stalled. Full procedures:
`~/.claude/docs/unattended-work-guards.md` (read before arming either).

## Initiative-scoped sessions

One session per initiative, not one per week: every turn re-reads the whole cached
conversation, so a long session's meter compounds even with disciplined steps. When an
initiative lands (pass
shipped, post-mortem recorded, STATUS pointed at the next action), close the session; the
artifacts are the handoff. The same force argues for dispatching reads within a session:
each extra turn re-buys the context.

## Project ledgers: STATUS is present tense (Geoff, 2026-08-21)

Every project repo splits its written state across three files by how often each is read.
The whole rule follows from one fact: **`docs/STATUS.md` is read in full at the start of
every session**, so anything parked there is a context cost paid on every session forever.

- **`docs/STATUS.md`** — present tense only: current state, what exists, the immediate next
  action, open decisions, and pass-scoped carry-forwards. Target ≤60 lines.
- **`docs/HISTORY.md`** — the per-pass ledger, newest first, read on demand at a post-mortem
  or a "when did this change" question. Each entry carries what landed, what the gate caught,
  and **what a later pass would be wrong to rediscover from scratch**. That last clause is
  what makes the file worth keeping rather than a changelog nobody opens.
- **`ROADMAP.md`** — strategic initiatives: work spanning passes, or setting a standard other
  work is measured against. `Active` / `Planned` / `Someday`, managed by `/log-project`. A
  carried item that sets a standard belongs here, not in STATUS's carried list.

The ≤60-line cap is not new; `site-pass` has always carried it and every repo blew past it
(ecxc-ski 173, 907-life 236, cairn-cms 540) because "prune" had no destination. It has one
now, so **pruning means moving, never deleting.** A STATUS reaching for a `## History` or
`## Passes` section is the signal to move it, not to summarize harder.

Applies to every repo in the clade, cairn-cms included. Migrating an existing repo is a
close-out chore, not a standalone pass: when a pass closes in a repo whose STATUS still
carries history, move it as part of that close.

## Pass sizing is the orchestrator's job (Geoff, 2026-07-29)

Geoff sees per-item summaries in which every addition reads as small; the orchestrator holds
the whole dispatch list, so detecting accumulation and raising it unprompted is its duty. A
pass that quietly doubles costs more than one split early. Three failure modes, all named from
poplar pass 1b (narrative in `model-economy.md`): **a grant is not headroom** ("use a
workflow", "you have latitude" authorize a mechanism, never more work; restate what a grant
authorizes before acting on it); **accretion by adjacency** (work joins a task because it
sits next to it, each addition defensible alone and none weighed against the total); and
**splitting tasks instead of the pass** (a task split keeps work inside the pass; only a pass
split lets work leave, which is why task splits feel like discipline while changing nothing).

Practice: count your own splits before answering "is this pass too long". A second task split
in one pass is the prompt to propose splitting the pass; a third means the proposal is
overdue. When proposing, name the cut point, what each half carries, and the follow-up pass's
number. State a task's deliverable count at dispatch and say plainly when it passes roughly
four or when anything is added after dispatch. Route discovered work to the pass that first
leans on it; prefer turning a discovered artifact into a standing input over making it a task
now. Never add scope to an in-flight task unless it would otherwise build against something
known wrong, and say so when doing it.

## Process proportionality

Interaction is batched and front-loaded, never minimized (Geoff, 2026-09-04). Before plan
approval, probe requirements and design until the plan carries no open readings; a long
brainstorm is the budget working as intended. Ask one question at a time by default, group
only a few tightly related ones, and lead each with a recommendation. After approval,
execution runs to completion with no per-task check-ins; the per-task chain, the quality
gates, and the pass-end reviewer fan-out replace the mid-loop human. Batch mid-execution
judgment calls into one combined question at a checkpoint; stop early only for a genuine
blocker or scope change.

Plans specify outcomes, constraints, and acceptance criteria per task, never implementation
code. Small tasks skip the ceremony: a change touching a handful of files, fully specified by
the request or existing tests, adding no new public surface, schema, or auth behavior, goes
straight to implementation through the gates and code-simplifier.

Score both budgets at pass end: tokens against the plan's ceiling (`/cost`), and attended
time as two counts. A planning miss is an ambiguity that surfaced after
approval and a planning question would have caught. An execution sitting is each pull-in after
approval, one combined question counting once. Planning questions never count against the
score. Record the numbers even when they look bad; the trend is the signal.

## Writing voice

Claude writes to a published external standard per audience, not a house voice. The
`writing-voice` output style (always on) carries the audience-invariant core; the
`writing-voice` skill is the on-demand router to each standard; the authoring charter
(`~/.claude/docs/authoring-charter.md`) is the umbrella. **Audience first**: before drafting,
name the audience and load its standard through the skill — developer docs follow Google,
editor copy Microsoft, agent-facing files Anthropic's Claude Code best practices, commits
Conventional Commits, code comments their language standard (Go Doc Comments via
go-conventions, TSDoc via ts-/svelte-conventions, PEP 257 via python-conventions). Site
content is the one personal voice, in the site repo's own content guide. Imitate the
standard's canonical exemplars. Vale (Google package on developer docs, Microsoft on editor
copy), the native comment linters, and `tellgrader` (see the writing-voice skill) are the
deterministic net, all fed back on save; a clean run is necessary, never sufficient. Draft
clean the first time.

The highest-frequency tells, inline so they are unmissable:
- One idea per sentence. Do not bridge two or three clauses into one.
- No "not X but Y" contrast frame. No reflexive three-item lists. No setup-colon payoff.
- No participial or connector openers ("Building on this", "Moreover", "Additionally").
- The em dash is banned in code comments (linter-enforced). Developer docs follow Google (no
  spaces); editor copy Microsoft; replies and commits go without. Overuse is a tell anywhere.
- The cairn documentation standard governs every published docs page; see
  `~/Projects/cairn-cms/docs/superpowers/specs/2026-09-08-docs-standard-design.md`.
- Any page an outside reader opens leads with a one-paragraph brief and carries one section
  per read; do not make a reader assemble the page's point from its parts.
- A claim about the owner, or about cairn's own stance, resolves to a line in an owner brief,
  never to an inference from other prose.
- `tellgrader --profile docs-register` reports cadence measures for an opted-in repo; every
  number is report-only and gates nothing (see the scanner's `MEASURES.md`).
