# Global Claude Code Patterns -- Workstation: thinkpad-x1

## Work Autonomously Until Done

Do not ask for review or approval until the task is fully complete; keep working until every
quality gate passes. Stop only for a genuine blocker needing information only the user can
provide.

## Search before you spelunk (Geoff, 2026-07-13)

When a symptom looks framework- or library-specific, spend one web search on the exact symptom
before an interactive debugging loop: a documented quirk or GitHub issue often names the cause
in one shot. Never read a file's "current state" while a background agent edits it; verify
against committed state or wait. Detail: `~/.claude/docs/claude-md-archive.md`.

## One executor per worktree (Geoff, 2026-07-14)

Before launching any executor into a repo or worktree (a Workflow, an implementer dispatch,
inline edits), verify none is already working it: `pgrep -f <worktree path>`, `git status` for
warm uncommitted changes you did not author, other sessions' workflow journal mtimes, and the
status docs (a "fresh session executes this" line may mean one already runs). When in doubt,
ask rather than race. Warm uncommitted code at dispatch time is a stop-and-investigate signal,
never free progress: stand down or coordinate. Two conductors never both run a close ritual,
merge, or release on one branch. Mid-flight contention: stop editing contested files, wait for
the other's commit, verify it, report verified.

## Machine Environment

- **OS**: Bluefin DX, `stable` stream (Fedora 44 base, bootc/ostree)
- **Desktop**: GNOME (Wayland) | **Shell**: bash | **Terminal**: Ptyxis. kitty exists only for
  the `tui-visual-verify` gate, never the daily terminal.
- **Key paths**: `~/Projects/` (repos), `~/.dotfiles/`, `~/.local/bin/` (scripts)
- **Dev tools**: Node via mise, Python via uv, Go via Homebrew, Java 17 for Android
  (`~/Android/`, `ANDROID_HOME` set in `.bashrc`)
- **Browsers**: Firefox (layered RPM) is the daily browser, so every artifact or page Geoff
  opens is built and checked Firefox-first; Chromium (`chromium-browser`) is the one Claude Code
  drives. Never a Flatpak build of either (the sandbox blocks native messaging); read
  `~/.claude/docs/bluefin-admin.md` before browser work.

## Sysadmin Preferences

- **Troubleshooting**: Search web after 1-2 failed attempts, with "Bluefin DX" or "Universal
  Blue" in the query
- **sudo**: `sudo -A` via `claude-askpass` (tmpfs cache); stale cache -> `claude-sudo-setup`
  (1Password unlocked); failures -> GID gotcha in `bluefin-admin.md`.
- **Software tiers**: mise/uv runtimes, Homebrew CLI, Flatpak GUI, distrobox/devcontainers for
  dev envs, rpm-ostree layering last resort; source of truth
  `~/.dotfiles/bluefin/layered-packages.txt`; policy and command map: `bluefin-admin.md`.
- **Destructive ops**: Show dry-run or confirmation step first
- **Home dir minimal**: scripts -> `~/.local/bin/`, configs -> `~/.config/`; check
  `~/.dotfiles/` first. `/etc` changes land in `~/.dotfiles/bluefin/etc/` first, then install
  from there; never edit `/etc` directly. micro is the editor; Neovim is not installed, never
  suggest it.

## Dotfiles Management

`~/.dotfiles`, GNU Stow; packages listed in `bluefin/stow-packages.txt`. **Every install
records itself in its tier's manifest, same session** (map: `bluefin-admin.md`); `check-drift`
reconciles, a weekly timer notifies on drift. Repo gate: `scripts/check.sh`. New script:
`bin/.local/bin/` + `stow -R bin`.

## Git Conventions

- **Before committing code changes, dispatch the `code-simplifier` subagent** over the changed
  code and apply its refinements. Docs-only commits skip it; skip otherwise only when told to.
  (poplar keeps its own Go-aware `simplify` skill.)
- Imperative mood: "Add feature" not "Added feature"
- Co-authored footer: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Commit specific files, not `git add -A`
- Never commit .env files or secrets; never force push to main/master

## Dependencies (Geoff, 2026-09-13 and 2026-09-14)

Every dependency bump in every repo goes through the `dependency-upgrade` skill: a pre-release
sweep, a bot PR, a single package taken for a feature, or "are we current". Take every minor
and patch by default; always ask before a major. Each bump carries a changelog survey and a
refactor decision on every new capability (take now, file, or propose a refactoring pass). A
release starts from every dependency's newest production version.

## Go Development

**MANDATORY: invoke `go-conventions` before writing any Go code.** For bubbletea UI, also
invoke `elm-conventions`; before claiming any TUI screen works, and at every TUI pass gate,
invoke `tui-visual-verify`: only a screenshot of the real terminal is evidence.

## Cloudflare

**FULL ACCOUNT ACCESS (2026-07-06).** Make routine changes directly; never treat Cloudflare
state as read-only. The MCP token is read-only for Access/Workers-domain writes; use curl with
`$CLOUDFLARE_API_TOKEN` for those. The token lives in `~/.local/secrets`, sourced for
interactive shells only, so a script must `source ~/.local/secrets` itself. Account id, token
scopes, D1/R2/workers/Access, and how each secret is reached:
`~/.claude/docs/cloudflare-estate-inventory.md`; read it before hunting a credential or
provisioning infra.

## API-First Policy

Use API or CLI first for external services; never suggest the web dashboard unless the API
cannot do it. Check `.claude/instructions/api-access.md` per project for the access inventory.

## Secrets

- **Never commit**: API tokens, passwords, keys, `.env` files with real values. **Local dev**:
  `~/.bashrc` (non-sensitive) or `~/.local/secrets` (sensitive). **CI/CD**: GitHub Actions
  secrets. **Runtime**: Cloudflare Workers secrets.
- **A new long-lived secret originates in the workstation age store** (`secret-set.sh`), never
  a loose file, never only `wrangler secret put`. **A value from Geoff arrives via
  `secret-receive NAME`**, never pasted into chat. **1Password has sudo semantics**: fetch once
  per session, parse locally, never loop `op`.
- **Check the stores before claiming a secret is missing**: `wrangler secret list`,
  `~/.local/secrets`, the age registry, per-project stores, the estate inventory. None found is
  the finding. Name-only checks, never print values.
- Full flows, exceptions, and store order: `bluefin-admin.md` "Secrets".

## Other workstation services

- **Google Docs / Drive / Sheets**: `gws` CLI, never an MCP server. Auth modes and write
  patterns: `bluefin-admin.md` "Google Docs / Drive (gws)".
- **Email**: poplar (`~/Projects/poplar/`, Fastmail via JMAP); API reference
  `~/.claude/instructions/fastmail-api.md`.

## Claude tooling: manifests, scopes, and the DaisyUI-first rule (Geoff, 2026-09-13)

Every skill, agent, MCP server, and plugin has one home and one manifest, reconciled by
`claude-tooling-sync verify` (run by `check-drift`): layout and rules in
`~/.claude/docs/claude-tooling.md`, read before adding any. Every cairn-family admin is
DaisyUI: prefer a stock component over a home-grown one unless the rulings ledger records the
defect that forced it (the official DaisyUI skill is the reference, the licensed Blueprint
server the pre-cut audit; the admin design system wins over both on conflict).

## cairn-family UI work

- **Visual fidelity (2026-07-05)**: UI work that must match a reference invokes the
  `visual-fidelity` skill at the start and gates on `visual-verifier`; nothing deploys to
  production without a full-page render read in the main loop.
- **Engine-level UI mechanics (Geoff, 2026-07-30, 2026-08-26)**: a UI mechanic belongs to
  cairn, a design choice to the site; "this repo has patched this before" is a filing trigger,
  never a reason to patch faster. Protocol: `~/.claude/docs/engine-ui-mechanics.md`.

## Claude Code Agent Usage

No human-scale time estimates; describe relative complexity ("quick", "multi-step") and focus
on sequencing, dependencies, and testing.

## Conducting a pass

Two co-equal budgets govern every initiative: total tokens and Geoff's attended time (clock
time is watched, never budgeted). After
approval, tokens buy research, verification, and retries; attended time buys only taste,
priorities, and product forks. Parallelize genuinely independent tasks (Geoff, 2026-09-03),
serializing only under named contention or dependency; plans mark independent tasks.

**Models (Geoff, 2026-09-23, per Anthropic's guidance):** Opus 5.5 brainstorms and authors
plans at `high` and conducts execution on `claude-opus-5-5` at `medium`; an unsettled decision
re-runs at `xhigh`, then `max`, then one `fable` dispatch, never a session switch. Every
dispatch names a model and an effort: `sonnet` by default, `haiku` for mechanical search,
`claude-opus-5-5` for reviewers. Seat table, effort per seat, overrules, and the Fable
allowance: `~/.claude/docs/model-economy.md` "Current state". Subagents start with zero
context: pre-extract what they need. Slow, expensive, or weak: check which model ran.

**The conductor is thin:** it never reads a source file, a diff, a test log, or a gate
transcript during execution, deciding only accept, re-dispatch with a correction, split,
upshift, or stop; one caught reading diffs or grinding edits inline flags itself and
dispatches. The spec read is the human gate; a reviewed plan runs.

Each plan task runs as a chain: the repo's Sonnet implementer returns a fixed shape (files
touched, gate result, uncovered decisions, anything it could not do); `diff-reviewer` reads the
diff against the task's acceptance criteria and returns accept, fix, or escalate with
`file:line` findings; the repo's full gate runs inside the chain. One re-dispatch on `fix`; a
second is the conductor's decision. A plan header's `Pass class:` sets the per-task gate,
review bar, test mandate, and close (table in the `pass-core` skill; Geoff, 2026-09-27).
Domain reviewers fan out at pass end. Below six tasks, dispatch the chain per task with the
Agent tool; at six or more, or when the plan marks tasks independent, run
`~/.claude/workflows/pass-execute.js`. One fold agent authors the close, with one independent
`diff-reviewer` read over its diff. Spec and plan reviews run through `spec-plan-review`.

Every plan header carries a token ceiling and a checkpoint interval (default four tasks);
write STATUS at each checkpoint, at any split, and before any question to Geoff. At 80% of the
ceiling, finish the task, write STATUS, and ask one combined question at the next segment
boundary. Segment a pass at three to four tasks, every boundary on a green commit; override
only for an irreversible task, a second `fix` verdict, or a disjoint Files seam (Geoff,
2026-09-12). Pre-bake before executing (commit the plan, point STATUS at it, refresh memory); anything
load-bearing lives in an artifact;
skip the `writing-plans` "which execution method?" question. Close the session rather than
re-prime it after an idle gap.

## Gate economy on a pass (Geoff, 2026-09-09)

Gates run through `cairn-run-gate '<string>'`: on exit 75, re-issue until it prints `gate
exit:`, never poll a log; a browserless gate sets `CAIRN_GATE_LANE=light`. Invoke a workstation
workflow by name, never a scratchpad copy. Full rule set: `~/.claude/docs/pass-gate-economy.md`.

## A rule lives where it executes (Geoff, 2026-09-20)

A rule reaches an agent only through its definition, its dispatch prompt, the runner that
builds the prompt, or a tool's own output; a side doc alone reaches nobody. Land a new rule in
the execution path in the same session, strongest form first: the tool enforces it, else the
runner renders it into the prompt, else the agent definition or skill states it. Read a tool's
`--help` once before relying on it for a whole pass, and act on a tool's NOTE in an agent's
report before the next dispatch.

## Compact instructions

Preserve the plan path and pass number; the task ledger (done, in flight, next); open decisions
and the last `diff-reviewer` verdict; the token ceiling and spend so far; and the STATUS resume
prompt. Drop tool output, diffs, and agent transcripts.

## Multi-agent workflows: suggest, never launch unprompted

Outside a pass plan that names the workflow mode, the Workflow tool runs only on Geoff's
explicit opt-in ("use a workflow"); when a task would clearly benefit, suggest it in one
sentence with shape and scale. Past ~30 minutes of unattended work, arm the runaway guard and
the sleep inhibitor: `~/.claude/docs/unattended-work-guards.md`.

## Initiative-scoped sessions

One session per initiative: every turn re-reads the whole cached conversation, so a long
session's meter compounds. Close the session when an initiative lands (pass shipped,
post-mortem recorded, STATUS pointed at the next action). The same force favors dispatching
reads.

## Project ledgers: STATUS is present tense (Geoff, 2026-08-21)

Every project repo splits its written state by how often each file is read:

- **`docs/STATUS.md`**, read in full every session: present tense only (current state, the
  immediate next action, open decisions, pass-scoped carry-forwards). Target ≤60 lines.
- **`docs/HISTORY.md`**: the per-pass ledger, newest first, read on demand, carrying what
  landed, what the gate caught, and **what a later pass would be wrong to rediscover**.
- **`ROADMAP.md`**: strategic initiatives, tiered `Active` / `Planned` / `Someday`, managed by
  `/log-project`; a carried item that sets a standard belongs here, not in STATUS.

**Pruning means moving, never deleting.** A STATUS reaching for a `## History` section is the
signal to move it. Migrating an existing STATUS is a close-out chore at the first close that
still carries history.

## Pass sizing is the orchestrator's job (Geoff, 2026-07-29)

The orchestrator holds the whole dispatch list, so it raises accumulation unprompted. Three
failure modes: **a grant is not headroom**; **accretion by adjacency**; **splitting tasks
instead of the pass**. A second task split is the prompt to propose splitting the pass, a
third means it is overdue; name the cut point, what each half carries, and the follow-up
pass's number. Detail: `model-economy.md`.

## Process proportionality

Interaction is batched and front-loaded, never minimized (Geoff, 2026-09-04). Before approval,
probe requirements and design until the plan carries no open readings, one question at a time
with a recommendation. After approval, execution runs to completion with no per-task
check-ins; batch judgment calls into one combined checkpoint question and stop early only for
a genuine blocker or scope change.

Method, idiom, and architecture calls are Claude's (Geoff, 2026-09-24 and 2026-09-26): decide
them from published evidence, the framework's documented convention, or architectural best
practice, bring the whole design for one approval, and flag only contestable points. Questions
to Geoff are for product, taste, priority, scope, and budget.

Plans specify outcomes, constraints, and acceptance criteria per task, never implementation
code. Small tasks skip the ceremony: a change touching a handful of files, fully specified by
the request or existing tests, adding no new public surface, schema, or auth behavior, goes
straight through the gates and code-simplifier. Score both budgets at pass end (tokens against
the ceiling via `/cost`; attended time as planning misses and execution sittings, defined in
`model-economy.md`), recording the numbers even when they look bad.

## Writing voice

Claude writes to a published external standard per audience, not a house voice: the
`writing-voice` output style carries the core, the `writing-voice` skill routes to each
standard, and `~/.claude/docs/authoring-charter.md` holds the map. **Name the audience and load
its standard before drafting**; site content uses the site repo's own content guide. Vale,
the comment linters, and `tellgrader` are the deterministic net; clean is necessary, never
sufficient. Draft clean the first time.

The highest-frequency tells:
- One idea per sentence; no "not X but Y" contrast frame, no reflexive three-item lists, no
  setup-colon payoff, no participial or connector openers ("Building on this", "Moreover").
- The em dash is banned in code comments (linter-enforced); developer docs follow Google (no
  spaces), editor copy Microsoft, replies and commits go without. Overuse is a tell anywhere.
- Every published cairn docs page follows the cairn documentation standard:
  `~/Projects/cairn-cms/docs/superpowers/specs/2026-09-08-docs-standard-design.md`.
