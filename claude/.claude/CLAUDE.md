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

## Go Development

**MANDATORY: Invoke the `go-conventions` skill before writing ANY Go code.** Every Go file, function, test, and error message must conform. (For bubbletea UI work, additionally invoke `elm-conventions`; before claiming any TUI screen works, and at every TUI pass gate, `tui-visual-verify`: goldens and tmux captures check text, only a screenshot of the real terminal is evidence.)

## Cloudflare / Wrangler

**FULL ACCOUNT ACCESS (Geoff, 2026-07-06): the CLAUDE_CODE Cloudflare API token + the MCP
plugin cover the whole glw907 account (120c269ad6d3dfbe6d63a0bb53758ca0) — zones, DNS,
Workers, Access, D1, R2 — holding BOTH the cairn-family sites AND the aksailingclub.org
estate. Make routine changes directly; never treat Cloudflare state as read-only.** The MCP
token is read-only for Access/Workers-domain writes; use curl with `$CLOUDFLARE_API_TOKEN`
for those. Access-protected ASC sites are reachable non-interactively via the service token
in `~/.local/secrets` (`ASC_ACCESS_CLIENT_ID`/`SECRET`, CF-Access-Client-* headers; full
process: the `asc-cloudflare-access` memory in the cairn project).

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

## Email (poplar)

poplar, a bubbletea terminal email client from `~/Projects/poplar/`; binary
`~/.local/bin/poplar` (`make install`). Fastmail via JMAP,
`$FASTMAIL_API_TOKEN` in `~/.local/secrets`. API reference:
`~/.claude/instructions/fastmail-api.md`.

## Visual fidelity (all projects, 2026-07-05)

Any UI work that must MATCH an existing reference (a rebuild, a theme port, a migration)
invokes the `visual-fidelity` skill at the start and gates on the `visual-verifier` agent.
Core rules even without the skill: reference screenshots before any plan (never build from a
verbal description); the context that built the UI never grades it; nothing deploys to
production without a full-page render read in the main loop; user-facing sites get Geoff's
before/after. (Born from two same-day production misses.)

## Engine-level UI mechanics, every cairn site (Geoff, 2026-07-30; consultation 2026-08-26)

Every cairn-cms site (aksailingclub-org, ecxc-ski, 907-life, later consumers), not one repo. A
UI **mechanic** belongs to cairn; a design **choice** belongs to the site. A mechanic recurs in
any component of that shape on any cairn site: how a padded label optically centers its text,
which element a two-part row drops when space runs out, a framework default rendering an
invisible control on a dark ground. Patching one in a site's theme or a route's scoped `<style>`
leaves every sibling site to rediscover it.

**The primary path is consultation, before the pass builds.** Engine edges are enumerated at
plan-authoring time through the `engine-consult` skill (both pass skills carry the hook), and
accepted work lands ahead of the site task that needs it.

**Mid-pass filing stays as the fallback, default behavior, never a response to being asked.**
Consultation cannot foresee what a pass discovers while building: a pass carrying UI work ends
by enumerating what it built, asking of each item whether it is a mechanic, and filing what
qualifies BEFORE reporting the pass done. A mid-pass staging doc uses the consultation brief's
four-field item schema, and its triage runs through `engine-triage` against the rulings ledger
(`cairn-cms/docs/internal/engine-rulings.md`). **A repeated local
workaround is the loudest signal that something sits at the wrong altitude**: "this repo has
patched this before" is an automatic filing trigger, not a reason to patch it faster. (Born
2026-07-30: a third repeat patch of the same DaisyUI edge, filed only when Geoff asked.)

Two qualifications. A mechanic that is always right becomes a silent default (`text-box-trim`
for optical centering); one whose answer depends on what the content means makes the choice
explicit at the call site (which element a row drops). The mechanically detectable half belongs
in `cairn-audit`, never a consuming site's own probe script. Worked example with the evidence
and measurement methods: `aksailingclub-org/docs/2026-07-30-assets-substrate-harvest-findings.md`.

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
naming the mode is the opt-in).

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
80% of the ceiling, finish the task, write STATUS, and ask one combined question. Pre-bake
before executing: commit the plan, point STATUS at it, refresh memory; anything load-bearing
lives in an artifact, never only in the conversation. Do not run the `writing-plans` "which
execution method?" question. Fable on Max draws from the weekly pool up to a 50% cap; its
metering is unpublished, so minimize Fable context, never Fable turns
(`~/.claude/docs/model-economy.md`).

## Gate economy on a pass (Geoff, 2026-09-09; evidence from cairn chassis-B2)

Clock time on a pass is the per-task gate and the fix rounds, not the implementer. Rules, all
approved, all cheap in tokens:
- **The slow suite runs only where it can catch something.** A browser e2e or visual suite
  joins the per-task gate only for tasks that move rendered paint; paint-neutral tasks run the
  check suite and unit tests, and the pass-end gate plus CI on every push run the full suite.
  Across B2's eight tasks the per-task e2e caught nothing the checks, the diff reviewer, and CI
  did not, at a third of each task's hour.
- **Comment-only fix rounds run a reduced gate** (the comment linters, the doc link gate, and
  the touched files' unit tests). The reviewer marks each blocking finding `commentOnly`; the
  chains scripts route on it.
- **Scope the engine test suite to the blast radius.** A task whose Files touch nothing under
  the engine's source runs the consumer's own unit suite, not the engine's.
- **A pre-flight checklist in every task's notes prevents the fix rounds** B2 kept paying for:
  no comment claims what its assertion does not prove; the labeled report block verbatim;
  no process citations in shipped comments; counts found, changed, deferred; re-emit before
  the gate.
- **Gates run through `cairn-run-gate '<string>'`** (dotfiles bin; generic despite the name):
  it blocks to completion and prints the tail, so an implementer never polls a log and its
  transcript stays small for the reviewer.
- **Parallel chains where Files are disjoint**, one worktree each, with any shared port made
  an environment variable; overlap a CI baseline regen with the diff review; fold
  single-deliverable tasks into a neighbor (each task pays about thirty minutes of fixed
  overhead).
- **Orchestrator hygiene:** halt agents PREPEND to STATUS, never rewrite it; a merge step brings
  `main` in first with fixed resolution rules (STATUS takes main's, HISTORY keeps both); the
  Workflow tool refuses a `~/.claude/workflows` scriptPath (copy to the session scratchpad);
  repeated protocol text in args goes in one field the chains script appends at prompt time.

## Compact instructions

Preserve the plan path and pass number; the task ledger (done, in flight, next); open
decisions and the last `diff-reviewer` verdict; the token ceiling and spend so far; and the
STATUS resume prompt. Drop tool output, diffs, and agent transcripts.

## Multi-agent workflows: suggest, never launch unprompted

Outside a pass plan that names the workflow mode, the Workflow tool runs only on Geoff's
explicit opt-in ("use a workflow"). When a task would clearly benefit (a large adversarial
review gate, a repo-wide audit or migration, deep research) suggest it in one sentence with
the shape and rough scale.

**Guards on long unattended work, both mandatory; procedures in
`~/.claude/docs/unattended-work-guards.md` (read before arming either).** Past ~30 minutes,
arm the runaway guard, a transcript-dir watcher; intervene with TaskStop plus
`resumeFromRunId`. On battery, arm `systemd-inhibit --what=sleep` plus the battery watchdog
(save state by 10%). GNOME suspends after 15 idle minutes on battery; check `journalctl` for
suspends before calling it stalled.

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
