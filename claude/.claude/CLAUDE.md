# Global Claude Code Patterns -- Workstation: thinkpad-x1

## Work Autonomously Until Done

Do not ask for review or approval until the task is fully complete; keep working until every
quality gate passes. Stop only for a genuine blocker needing information only the user can
provide.

## Search before you spelunk (Geoff, 2026-07-13)

When a symptom looks framework- or library-specific, spend one web search on the exact symptom
before opening an interactive debugging loop: a documented quirk or GitHub issue often names the
cause in one shot. Corollary: never read a file's "current state" while a background agent
edits it; you will read a half-applied change. Verify against committed state or wait for the
agent. Detail: `~/.claude/docs/claude-md-archive.md`.

## One executor per worktree (Geoff, 2026-07-14)

Before launching any executor into a repo or worktree (a Workflow, an implementer dispatch,
inline edits), verify none is already working it: `pgrep -f <worktree path>`, `git
status` for warm uncommitted changes you did not author, other sessions' workflow journal
mtimes, and the status docs (a "fresh session executes this" line may mean one already runs).
When in doubt, ask rather than race. Warm uncommitted code at dispatch time is a
stop-and-investigate signal, never free progress. If found, stand down or coordinate: two
conductors never both run a close ritual, merge, or release on one branch. Mid-flight
contention: stop editing contested files, wait for the other's commit, verify it, report
verified. Detail: `~/.claude/docs/claude-md-archive.md`.

## Machine Environment

- **OS**: Bluefin DX, `stable` stream (Fedora 44 base, bootc/ostree)
- **Desktop**: GNOME (Wayland) | **Shell**: bash | **Terminal**: Ptyxis. kitty exists only for
  the `tui-visual-verify` gate, never the daily terminal.
- **Key paths**: `~/Projects/` (repos), `~/.dotfiles/`, `~/.local/bin/` (scripts)
- **Dev tools**: Node via mise, Python via uv, Go via Homebrew, Java 17 for Android
  (`~/Android/`, `ANDROID_HOME` set in `.bashrc`)

## Browsers: Firefox + Chromium, no Flatpak

Firefox (layered RPM) is the daily browser. Chromium (layered RPM) is the dev/testing browser
Claude Code drives (claude-in-chrome, chrome-devtools MCP, `chromium-shot`), binary
`chromium-browser`. Never a Flatpak build of either: the sandbox blocks required native
messaging. Read `~/.claude/docs/bluefin-admin.md` before browser or extension work.

## Sysadmin Preferences

- **Troubleshooting**: Search web after 1-2 failed attempts, with "Bluefin DX"
  or "Universal Blue" in the query
- **sudo**: `sudo -A` via `claude-askpass` (tmpfs cache); stale cache ->
  `claude-sudo-setup` (1Password unlocked); failures -> GID gotcha in
  `bluefin-admin.md`.
- **Software tiers**: mise/uv runtimes, Homebrew CLI, Flatpak GUI, distrobox/devcontainers for
  dev envs, rpm-ostree layering last resort; source of truth
  `~/.dotfiles/bluefin/layered-packages.txt` (also `docs/MIGRATION-BRIEF.md`); policy and
  command map: `bluefin-admin.md`.
- **Destructive ops**: Show dry-run or confirmation step first

## System Organization

- Home dir minimal: scripts -> `~/.local/bin/`, configs -> `~/.config/`; check `~/.dotfiles/`
  first. `/etc` changes land in `~/.dotfiles/bluefin/etc/` first, then install from there;
  never edit `/etc` directly (see `bluefin-admin.md`). micro is the editor; Neovim is not
  installed, never suggest it.

## Dotfiles Management

- **Location**: `~/.dotfiles`, GNU Stow; packages listed in `bluefin/stow-packages.txt`.
  **Every install records itself in its tier's manifest, same session** (map:
  `bluefin-admin.md`); `check-drift` reconciles, a weekly timer notifies on drift. Repo gate:
  `scripts/check.sh`. New script: `bin/.local/bin/` + `stow -R bin`.

## Git Conventions

- **`code-simplifier` runs once per pass or branch, at the close,** over changed TS, Svelte, or Go; never per commit or at an intermediate boundary, never for docs. (poplar keeps its own Go-aware `simplify` skill.)
- Imperative mood: "Add feature" not "Added feature"
- Co-authored footer: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Commit specific files, not `git add -A`
- Never commit .env files or secrets; never force push to main/master

## Dependencies (Geoff, 2026-09-13 and 2026-09-14)

Every dependency bump in every repo goes through the `dependency-upgrade` skill: a pre-release
sweep, a bot PR, a single package taken for a feature, or a question like "are we current". Take
every minor and patch by default; always ask before a major. The bump is not done at the
lockfile: each one carries a changelog survey and a refactor decision on every new capability
(take now, file, or propose a refactoring pass), so debt never accumulates and upstream
improvements reach our own code. A release starts from every dependency's newest production
version.

## Go Development

**MANDATORY: invoke `go-conventions` before writing any Go code.** Every Go file, function, test, and error message must conform. For bubbletea UI, also invoke `elm-conventions`; before claiming any TUI screen works, and at every TUI pass gate, invoke `tui-visual-verify`: goldens and tmux captures check text, only a screenshot of the real terminal is evidence.

## Cloudflare / Wrangler

**FULL ACCOUNT ACCESS (2026-07-06).** Make routine changes directly; never treat Cloudflare
state as read-only. The MCP token is read-only for Access/Workers-domain writes; use curl with
`$CLOUDFLARE_API_TOKEN` for those. Account id, the ASC Access route, and the full authorization
model: `~/.claude/docs/cloudflare-estate-inventory.md`.

- `npx wrangler deploy` / `dev` / `secret put NAME` / `tail`
- `CLOUDFLARE_API_TOKEN` in `~/.local/secrets` (sourced for interactive shells only; a
  script must `source ~/.local/secrets` itself). Exact scopes: the estate inventory doc above.

## API-First Policy

Use API or CLI first for external services; never suggest the web dashboard unless the API
cannot do it. Check `.claude/instructions/api-access.md` per project for the access inventory.

## Secrets

- **Never commit**: API tokens, passwords, keys, `.env` files with real values. **Local dev**:
  `~/.bashrc` (non-sensitive) or `~/.local/secrets` (sensitive, sourced from 1Password).
  **CI/CD**: GitHub Actions secrets. **Runtime**: Cloudflare Workers secrets.
- **1Password: sudo semantics, never a loop.** The first `op` call per session authenticates it;
  fetch once (`op item get <id> --format json`) and parse locally. `claude-block-op` denies 3+
  `op` calls in a minute (once per session, like sudo). Passkeys route through the browser for
  Geoff's touch, never read directly.
- **Installing a NEW long-lived secret, every project (2026-07-13): the workstation age store
  is the origin, never a loose file, never only `wrangler secret put`.** Flow:
  `~/.dotfiles/scripts/secrets/secret-set.sh NAME --value|--file|--b64-file` (writes
  `values.age`, regenerates `~/.local/secrets`), document scope and rotation in
  `~/.dotfiles/secrets/registry.md`, add the worker to `sync.sh`'s WORKER_SECRETS routing if it
  consumes one, then `sync.sh --worker NAME` and `sync.sh --verify`. Delete any loose key file;
  the upstream issuer (GCP IAM, GitHub App settings, ...) mints replacements. Exception: ASC
  secrets use `aksailingclub-legacy/secrets/`; per-site rotatable HMAC keys (MAGIC_LINK_SECRET,
  SESSION_SECRET) stay worker-only.
- **Receiving a secret value FROM Geoff (2026-08-31): run `secret-receive NAME [--hint
  …|--op REF]`, a desktop paste dialog (or 1Password read) piped into the age store. Never
  paste-into-chat or hand-run commands.** Wire the name first (manifest, registry `pending`,
  consumer config); flip the registry checkmark after the mint.
- **Cloudflare estate and how each secret is reached**: `~/.claude/docs/cloudflare-estate-inventory.md`
  (D1/R2/workers/Access; secrets are write-only, so a value comes from its origin). Read it
  before hunting a credential or provisioning infra.
- **Check the stores before claiming a secret is missing.** Check in order: `npx wrangler
  secret list` (per worker), `~/.local/secrets`, the age registry
  (`~/.dotfiles/secrets/registry.md`), per-project stores (a repo's `secrets/` dir plus sync
  script; ASC's is `aksailingclub-legacy/secrets/`), and the estate inventory above. None found
  is the finding, not "Geoff owes a paste." Name-only checks, never print values.
  (Archive: `~/.claude/docs/claude-md-archive.md`.)

## Google Docs / Drive (gws)

`gws` (Google Workspace CLI, Homebrew `googleworkspace-cli`) is the path to Google Docs, Drive,
and Sheets, never an MCP server. Personal docs: OAuth as Geoff's own Google account (`gws auth
login -s docs,drive`; the Desktop OAuth client pair lives in the age store as
`GOOGLE_WORKSPACE_CLI_CLIENT_ID` / `_CLIENT_SECRET`). ASC docs only: the club service account
via `GOOGLE_APPLICATION_CREDENTIALS`, which `gws` also honors; unset it if it shadows the
personal login. Formatting edits go through `docs documents batchUpdate` after a `get` for
indexes; `--dry-run` first on any write. Patterns: `google-docs-formatting` memory.

## Email (poplar)

poplar, a bubbletea terminal email client from `~/Projects/poplar/`; binary
`~/.local/bin/poplar` (`make install`). Fastmail via JMAP,
`$FASTMAIL_API_TOKEN` in `~/.local/secrets`. API reference:
`~/.claude/instructions/fastmail-api.md`.

## Claude tooling: manifests, scopes, and the DaisyUI-first rule (Geoff, 2026-09-13)

Every skill, agent, MCP server, and plugin has one home and one manifest, reconciled by
`claude-tooling-sync verify` (run by `check-drift`): layout and rules in
`~/.claude/docs/claude-tooling.md`, read before adding any. The DaisyUI-first rule stays here:
every cairn-family admin is DaisyUI, so prefer a stock component over a home-grown one unless
the rulings ledger records the defect that forced it (the official DaisyUI skill is the
reference, the licensed Blueprint server the pre-cut audit; the admin design system wins over
both on conflict).

## Visual fidelity (2026-07-05)

Any UI work that must match an existing reference (a rebuild, a theme port, a migration)
invokes the `visual-fidelity` skill at the start and gates on the `visual-verifier` agent. Core
rules even without the skill: reference screenshots before any plan, never from a verbal
description; the context that built the UI never grades it; nothing deploys to production
without a full-page render read in the main loop; user-facing sites get Geoff's before/after.
Detail: `~/.claude/docs/claude-md-archive.md`.

## Engine-level UI mechanics, every cairn site (Geoff, 2026-07-30, 2026-08-26)

A UI **mechanic** belongs to cairn; a design **choice** belongs to the site. Patching a
mechanic in a site's theme leaves every sibling site to rediscover it; "this repo has patched
this before" is an automatic filing trigger, never a reason to patch it faster. Full protocol
and the filing fallback: `~/.claude/docs/engine-ui-mechanics.md`.

## Claude Code Agent Usage

No human-scale time estimates; describe relative complexity ("quick", "multi-step") and focus
on sequencing, dependencies, and testing.

## Conducting a pass

Two co-equal budgets govern every initiative: total tokens and Geoff's attended time (clock
time is watched, never budgeted; attended time front-loads, per Process proportionality below).
After approval, tokens buy research, verification, and retries, while attended time buys only
taste, priorities, and product forks. Parallelize wherever tasks are genuinely independent
(Geoff, 2026-09-03), serializing only under named contention or dependency. Plans mark
independent tasks so pass-execute's parallel mode can take them.

Per Anthropic's model guidance (Geoff, 2026-09-23), **Opus 5.5 brainstorms, authors plans, and
conducts execution; Fable 5.1 escalates only after Opus 5.5 at `xhigh` or `max` falls short.**
Opus 5.5 at `high` runs the brainstorm and authors the plan; planning misses at pass close are
the check. Execution runs on `claude-opus-5-5` at `medium`: dispatch chains, read structured
reports, rule on escalations, run the close; a new pass starts as a fresh Opus 5.5 session from
the STATUS resume prompt. An unsettled decision re-runs at `xhigh` then `max`, then one `fable`
dispatch, never a session switch. Reviewers pin Opus 5.5 too: an overrule states why in STATUS,
and a correctness-critical one takes the same `xhigh`-then-`fable` path. The plan-approval gate
is the single human gate. **The conductor is thin:** it never reads a source file, a diff, a
test log, or a gate transcript during execution, deciding only accept, re-dispatch with a
correction, split, upshift, or stop; one caught reading diffs or grinding edits inline flags
itself and dispatches.

Each plan task runs as a chain: the repo's Sonnet implementer returns a fixed shape (files
touched, gate result, uncovered decisions, anything it could not do); `diff-reviewer`
(`claude-opus-5-5`) reads the diff against the task's acceptance criteria and returns accept,
fix, or escalate with `file:line` findings; the pass class's gate runs inside the chain, never in
the main loop. Pass machinery lives in the `pass-core` skill. One re-dispatch on `fix`; a second is the conductor's decision. Domain reviewers
still fan out at pass end. Below six tasks, dispatch the chain per task with the Agent tool; at
six or more, or when the plan marks tasks independent, run `~/.claude/workflows/pass-execute.js`
(naming the mode is the opt-in). A pass's close task is authored by one fold agent, which
commits its draft, then folds, with one independent `diff-reviewer` read over the fold's diff.
Spec and plan reviews run through `spec-plan-review` (three disjoint lenses, staleness in the
drafter's pre-flight); findings rank by consequence, and a fold may refuse one whose fix costs
more than the risk it removes.

Every dispatch names a model and an effort: `sonnet` by default, `haiku` for mechanical search,
`claude-opus-5-5` for reviewers. A dispatch without a model falls to
`CLAUDE_CODE_SUBAGENT_MODEL=sonnet` (settings `env`), though a frontmatter or per-dispatch
`model` wins; upshifts pass it explicitly: `opus` for novel correctness-critical logic the plan
does not specify, then higher effort, then `fable` only when Opus 5.5 at `xhigh` still falls
short. Effort follows each model's Anthropic default: the Opus 5.5 main session at `medium`;
Sonnet implementers, reviewers, plan authorship, adjudication, and research at `high`; `low`
for mechanical subagents only, never Fable 5.1; `max` for one adjudication.
`/effort` persists to settings.json; reset it at session end. Subagents start with zero
context: pre-extract what they need. Slow, expensive, or weak: check which model ran.

Every pass plan header carries a token ceiling and a checkpoint interval (default four tasks);
write STATUS at each checkpoint, at any split, and before any question to Geoff, then continue,
relying on compaction. At 80% of the ceiling, finish the task, write STATUS, and ask one
combined question at the next segment boundary, the only place this decision can land.
Segment a pass at three to four tasks, every boundary on a commit the gate proved green;
override the count only for an irreversible task, a second `fix` verdict, or a disjoint Files
seam (Geoff, 2026-09-12). Close the session rather than re-prime it after an idle gap. Pre-bake
before executing: commit the plan, point STATUS at it, refresh memory; anything load-bearing
lives in an artifact. Skip the `writing-plans` "which execution method?" question. Fable on Max
caps at 50% of the weekly pool with unpublished metering; minimize its context, never its turns
(`~/.claude/docs/model-economy.md`).

## Gate economy on a pass (Geoff, 2026-09-09)

Clock time on a pass is the per-task gate and fix rounds, not the implementer. Gates run
through `cairn-run-gate '<string>'`: on exit 75, re-issue until it prints `gate exit:`, never
poll a log; a browserless gate (a Go `make check`, a lint-only run) sets
`CAIRN_GATE_LANE=light`. Invoke a workstation workflow by name, never a scratchpad copy. Full
rule set: `~/.claude/docs/pass-gate-economy.md`.

## A rule lives where it executes (Geoff, 2026-09-20)

A rule reaches an agent only through its definition, its dispatch prompt, the runner that
builds the prompt, or a tool's own output. A side doc alone reaches nobody, since subagents
start with zero context (incident: `~/.claude/docs/pass-gate-economy.md`). Land a new rule in
the execution path in the same session, strongest form first: the tool enforces or announces
it; else the runner renders it into the prompt; else the agent definition or skill states it. A
doc alone is the record, never the delivery. Two habits follow: read a tool's `--help` once
before relying on it for a whole pass, since the tool is the spec; and act
on a tool's NOTE in an agent's report before the next dispatch.

## Compact instructions

Preserve the plan path and pass number; the task ledger (done, in flight, next); open decisions
and the last `diff-reviewer` verdict; the token ceiling and spend so far; and the STATUS resume
prompt. Drop tool output, diffs, and agent transcripts.

## Multi-agent workflows: suggest, never launch unprompted

Outside a pass plan that names the workflow mode, the Workflow tool runs only on Geoff's
explicit opt-in ("use a workflow"); when a task would clearly benefit (a large review gate, a
repo-wide audit or migration, deep research), suggest it in one sentence with shape and scale.

**Guards on long unattended work.** Past ~30 minutes, arm the runaway guard. Sleep is
tool-held (a hook-fed lease for every Claude session, 10% battery floor; `cairn-run-gate`;
`awake --` for other work): verify with `systemd-inhibit --list`, `journalctl -t claude-awake`.
Procedures: `~/.claude/docs/unattended-work-guards.md`.

## Initiative-scoped sessions

One session per initiative, not one per week: every turn re-reads the whole cached
conversation, so a long session's meter compounds even with disciplined steps. Close the
session when an initiative lands (pass shipped, post-mortem recorded, STATUS pointed at the
next action); the artifacts are the handoff. The same force favors dispatching reads, since
each extra turn re-buys the context.

## Project ledgers: STATUS is present tense (Geoff, 2026-08-21)

Every project repo splits its written state across three files by how often each is read:
**`docs/STATUS.md` is read in full at the start of every session**, so anything parked there
costs context every session forever.

- **`docs/STATUS.md`** — present tense only: current state, what exists, the immediate next
  action, open decisions, and pass-scoped carry-forwards. Target ≤60 lines.
- **`docs/HISTORY.md`** — the per-pass ledger, newest first, read on demand at a post-mortem or
  a "when did this change" question, carrying what landed, what the gate caught, and **what a
  later pass would be wrong to rediscover from scratch**, the clause that keeps it a ledger, not
  a changelog.
- **`ROADMAP.md`** — strategic initiatives (spanning passes, or setting a standard other work
  is measured against), tiered `Active` / `Planned` / `Someday`, managed by `/log-project`; a
  carried item that sets a standard belongs here, not in STATUS's carried list.

**Pruning means moving, never deleting** (history: `~/.claude/docs/claude-md-archive.md`). A
STATUS reaching for a `## History` or `## Passes` section is the signal to move it, not to
summarize harder.

Applies to every repo; migrating an existing STATUS is a close-out chore, not a standalone
pass, done at the first close that still carries history.

## Pass sizing is the orchestrator's job (Geoff, 2026-07-29)

The orchestrator holds the whole dispatch list, so detecting accumulation and raising it
unprompted is its duty; a pass that quietly doubles costs more than one split early. Three
failure modes, named in `~/.claude/docs/model-economy.md`'s poplar pass 1b narrative: **a grant
is not headroom** (restate what a grant authorizes before acting on it, never treat it as more
work); **accretion by adjacency** (each addition to a task is defensible alone, never weighed
against the total); **splitting tasks instead of the pass** (a task split keeps work inside the
pass; only a pass split lets work leave).

Practice: count your own splits before answering "is this pass too long"; a second task split
is the prompt to propose splitting the pass, a third means the proposal is overdue. When
proposing, name the cut point, what each half carries, and the follow-up pass's number. Full
practice detail: `~/.claude/docs/model-economy.md`.

## Process proportionality

Interaction is batched and front-loaded, never minimized (Geoff, 2026-09-04). Before approval,
probe requirements and design until the plan carries no open readings; ask one question at a
time by default, grouping only a few tightly related ones, each with a recommendation. After
approval, execution runs to completion with no per-task check-ins: the per-task chain, quality
gates, and pass-end reviewer fan-out replace the mid-loop human. Batch judgment
calls into one combined checkpoint question; stop early only for a genuine blocker or scope
change.

Method, idiom, and architecture calls are Claude's (Geoff, 2026-09-24 and 2026-09-26). This covers
an evaluation method, a framework's authoring form, and a compile or layering strategy. When
published evidence, the framework's documented convention, or an architectural best practice
settles one, decide it from that evidence. Bring the whole design for one approval, and flag only
the points a reasonable reviewer might contest. Questions to Geoff are for product, taste,
priority, scope, and budget.

Plans specify outcomes, constraints, and acceptance criteria per task, never implementation
code. Ceremony scales by kind as well as size: a plan declares a pass class (`auth-data`,
`engine-logic`, `paint`, `sweep`, `docs`, `tool`) that sets each task's gate, review bar, test
mandate, and close steps (table: `pass-core`). Superpowers skills yield to it: TDD's write-first
applies to `engine-logic` and `auth-data` only, and plans stay outcome-only. Small tasks skip the ceremony: a change touching a handful of files, fully specified by
the request or existing tests, adding no new public surface, schema, or auth behavior, goes
straight through the gates.

Score both budgets at pass end: tokens against the plan's ceiling (`/cost`), and attended time
as planning misses and execution sittings, defined in `~/.claude/docs/model-economy.md`. Record
the numbers even when they look bad; the trend is the signal.

## Writing voice

Claude writes to a published external standard per audience, not a house voice: the
`writing-voice` output style carries the audience-invariant core, the `writing-voice` skill
routes to each standard, and the authoring charter (`~/.claude/docs/authoring-charter.md`)
holds the full map. **Audience first**: before drafting, name the audience and load its
standard through the skill; site
content is the one personal voice, in the site repo's own content guide. Imitate the standard's
canonical exemplars. Vale (Google on developer docs, Microsoft on editor copy), the native
comment linters, and `tellgrader` are the deterministic net, fed back on save; clean is
necessary, never sufficient. Draft clean the first time.

The highest-frequency tells, inline so they are unmissable:
- One idea per sentence, never bridging two or three clauses into one; no "not X but Y"
  contrast frame, no reflexive three-item lists, no setup-colon payoff, no participial or
  connector openers ("Building on this", "Moreover", "Additionally").
- The em dash is banned in code comments (linter-enforced); developer docs follow Google (no
  spaces), editor copy Microsoft, replies and commits go without. Overuse is a tell anywhere.
- The cairn documentation standard, including the front-door brief and the owner-brief
  provenance rule, governs every published docs page:
  `~/Projects/cairn-cms/docs/superpowers/specs/2026-09-08-docs-standard-design.md`.
- `tellgrader --profile docs-register` reports cadence measures for an opted-in repo,
  report-only and gating nothing (`MEASURES.md`).
