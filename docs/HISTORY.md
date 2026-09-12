# History

Per-pass ledger, newest first. Current state lives in `docs/STATUS.md`;
strategic initiatives spanning passes live in `ROADMAP.md`.

## 2026-09-12 -- Claude infra round

Plan `docs/superpowers/plans/2026-09-12-claude-infra-round.md` (revision 2, ratified at
`1ec5c0a`). Ten dispatched tasks corrected and hoisted Claude-facing infrastructure across the
workstation and its consumer repos. Task 1 fixed the exit-75 reattach protocol in the two
implementers that call `cairn-run-gate` without it (dotfiles `95c65a7`, dubplate `a30d32e`).
Task 2 corrected the unattended-work guards doc (dotfiles `f905328`). Task 3 hoisted the
`svelte-check` skill to the workstation (907-life `9ab912f`, ecxc-ski `b276e0c`, dotfiles
`dbb653d`). Task 4 hoisted and supplemented the two instruction files (907-life `1ec7fd0`,
ecxc-ski `0131ac0` then `7817b36` for a RESEND_API_KEY sourcing-fact fix, dotfiles `aa20264`).
Task 5 hoisted `go-architecture-reader` to the workstation agents (dubplate `f3a55da`, dotfiles
`a2c6463`). Task 6 carried the model-economy update (dotfiles `2059e84` then `a30733e`, one fix
round). Task 7 wrote the two displacement destination documents (dotfiles `12017a4`). Task 8
displaced `claude/.claude/CLAUDE.md` from 27,807 to 23,947 bytes, picking candidates 1, 2, 3,
and 5 (dotfiles `23f8885`). Task 9, the `pass-execute.js` runner edit, deferred: the cairn
overnight workflow `wf_2d52758e-603` was still live at the segment-C boundary, owed to the next
round that touches it.

Every task took 0 fix rounds except task 6, which took 1: the reviewer found `couldNotDo` filed
empty though the unverified Devin/Cognition figures were correctly omitted, and that the plan
named three subsections where the source names four, with four landing. Task 8's reviewer left
one non-blocking note, corrected in this round's own close task: `pass-gate-economy.md` still
said `cairn-run-gate` "blocks to completion" after the exit-75 correction landed in CLAUDE.md.
Segment B's first run stood down at the 11% battery floor mid task 6 (STATUS recorded at
`74807bc`) and resumed on mains. Conductor checkpoints `45fe6d8` (segment A) and `85c8d56`
(segment B and the 80% flag). Spend about 1.55M subagent tokens against the 1.5M ceiling, over
by the interrupted segment-B run; zero planning misses, one execution sitting (the 80% flag
question, task 9's deferral).

**What a later pass would be wrong to rediscover**:

- **Six `~/.claude` directories are whole-directory stow symlinks, not five.**
  `~/.claude/agents`, `docs`, `instructions`, `output-styles`, `skills`, and `workflows` each
  link to `../.dotfiles/claude/.claude/<name>` (so `~/.claude/skills/svelte-check` is reached
  through the `skills` fold, not linked on its own), plus the file-level links `CLAUDE.md`,
  `settings.json`, and `gather-dotfiles.sh`. A later pass never needs to `stow -R claude` for a
  new file inside any of these; the write to the dotfiles source is live machine-wide the
  instant it lands.
- **The dotfiles gate reads repository markdown only through gitleaks** (and vale over its
  fixtures). Every task's acceptance criteria, not a markdown linter, were this round's proof
  that a doc's content was correct.
- **`claude/.claude/CLAUDE.md` grew 3,812 bytes in four days**, from 23,995 bytes on 2026-09-08
  to 27,807 bytes on 2026-09-12. That growth rate is why the four ranked displacement
  candidates from the 2026-09-08 pass stopped being sufficient and task 8 needed a fifth pick.
- **A displacement pointer must keep its section's load-bearing lines inline.** A preserved
  trigger that fires after the decision it guards is already made is not a trigger; task 8's
  reviewer held every pick to that rule before accepting it.

## 2026-09-08 -- docs-standard Claude infrastructure pass (plan one of three)

Plan `docs/superpowers/plans/2026-09-08-docs-standard-claude-infra.md`, spec
`~/Projects/cairn-cms/docs/superpowers/specs/2026-09-08-docs-standard-design.md`. Seven
dispatched tasks landed the workstation half of the cairn documentation standard: task 1a
gave tellgrader a `docs-register` profile and `.tellgrader.json` opt-in discovery (c523f0b);
task 1b added the two cadence measures and `MEASURES.md` (fc143ec, then two fix rounds
c217769 and 064168f on the prose-selector wording, closed by the conductor); task 2 added the
output style's three tells and each voice file's docs-register-measures section (7f63c0e, then
ecf31ab re-sourcing the two-headed-heading tell to the register ruling instead of Google, whose
own headings page recommends two of the forbidden forms); task 3 made the Vale hook's
path-grading visible and tested (019e1e8, then f1a3ec5 re-asserting the tests on the rendered
phrase after review proved them passing against the old hook); task 4 gave the four review
agents the measurement table and the containment rules, and added `figure-verifier` (f32315c,
then e2d1ea7 granting the register editor a Bash tool it lacked); task 5 added the
`cairn-figure` skill and renamed writing-voice's section to `## Author-facing prose` (5a2990d,
then 7436dcb adding the repro fence the figure skill needed); task 6 wrote the ranked
`CLAUDE.md` displacement candidates as a document only, no `CLAUDE.md` touched (3d21e72). Every
dispatched task took exactly one fix round except 1b, which took two, closed by conductor
decision rather than a third dispatch.

**What a later pass would be wrong to rediscover**:

- **tellgrader is not a poplar artifact and poplar's `make check` is not its gate.** Its
  source lives in this repo under the `claude` stow package, at
  `claude/.claude/skills/writing-voice/evals/tellgrader/`, a standalone Go module
  (`github.com/glw907/workstation/tellgrader`) with its own `Makefile`. Its gate is
  `make -C ~/.dotfiles/claude/.claude/skills/writing-voice/evals/tellgrader check`, now wired
  into `scripts/check.sh` as the "tellgrader go check" step. The compiled binary is gitignored;
  `check-drift` flags it as an untracked `~/.local/bin` executable, which is expected and not a
  regression.
- **`agents/`, `docs/`, and `skills/` under `~/.claude` are whole-directory stow symlinks
  (folded), so a new file inside them is live machine-wide the instant it is written, with no
  restow.** `figure-verifier.md` and `cairn-figure/SKILL.md` both resolved through
  `~/.claude/...` before any `stow -R claude` ran. Every task edited the stow source under
  `~/.dotfiles/claude/.claude/`, never the `~/.claude/` symlink path, and every write there
  changes what every session in every repo sees at the moment of the commit.
- **Both `CLAUDE.md` files were already at or over the `claude-context-budget` hook's
  24,000-byte ceiling before this pass.** `claude/.claude/CLAUDE.md` sat 5 bytes under;
  `~/Projects/cairn-cms/CLAUDE.md` sat 136 bytes over. Adding the standard's four lines to
  either file needs a displacement pick first, which is why unit 3c cannot close inside this
  pass; the ranked candidates are in
  `docs/superpowers/plans/2026-09-08-claude-md-displacement-candidates.md`, and the edits are
  the owner sitting's, batched with the corpus approval (decision 7).
- **No bands ship.** The hinged-pair definition moved twice during the proposal and no gate
  reads either measure; `MEASURES.md` states both shares as report-only and unbanded. A band
  directory, if wanted, is plan two's to build from a measured corpus, never a placeholder file
  this pass would have shipped.
- **The review agents carry no `--profile` flag and refuse nothing for lack of a corpus
  entry.** Forcing the profile stays a reviewer's explicit, per-invocation act; a repo with no
  corpus manifest still gets a graded report, noting the absence, so no existing dispatch (in
  ecxc-ski or 907-life, on live site content) broke the moment these files were written.

Budget: ceiling 0.6M tokens; the pass closed inside it by the per-task reports. Zero planning
misses, zero execution sittings; every combined question at the task-3 checkpoint was batched
as the plan specified. Human touchpoints: the plan revision-3 approval and the task-3
checkpoint's one combined question.

## 2026-09-04 -- Fable 5.1 model, effort, and skill update

Fable 5.1 (shipped 2026-09-01; same $10/$50, cache reads $0.25/MTok) became
the session model on 2026-09-04. This pass tuned the configuration around
it (plan `docs/superpowers/plans/2026-09-04-fable-5-1-infra-update.md`,
spec `docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md`,
revised after a three-lens adversarial review of 49 findings).
`CLAUDE_CODE_SUBAGENT_MODEL` moved from a `.bashrc` export of `inherit` to
a settings `env` entry of `sonnet`, so dispatches without a model
(general-purpose, claude, Workflow agent() without model) stopped running
at Fable price; pins still win, proven by session-pinned transcript.
CLAUDE.md gained the effort rule (`medium` as the committed default, raised
to `high` for plan authorship, adjudication, and research turns, `max` for
one adjudication; revised to medium the same day on the outside evidence)
and landed at 5,986 tokens under its 6,000 budget. The model-economy doc update (plan
task 3) waits on another session's uncommitted edit to the same file and
is carried in STATUS. An Opus prompt audit wrote
`docs/superpowers/plans/2026-09-04-prompt-audit-report.md` (nothing
applied). `site-pass`'s start and discipline sections were restated as
outcomes and constraints with every rule kept and the pass-end ritual
byte-identical, as a measured experiment. A monthly `model-review.timer`
and a ROADMAP Active entry put the review on a cadence; first due
2026-10-01.

**What a later pass should not rediscover**:

- **The `.bashrc` comment was wrong about precedence.** It claimed a
  global `CLAUDE_CODE_SUBAGENT_MODEL` would override frontmatter. The
  documented order is per-dispatch model, then frontmatter, then the
  variable, then the session model. The variable never reaches `Explore`
  or `Plan`, and forcing it onto them would override every pin.
- **A settings `env` value beats the shell and reaches running
  sessions.** `.bashrc` was the weakest home for this variable.
- **`/usage`'s plan-limit breakdown has no per-model share.** Plan bars
  are shared across models; attribution is by skill, subagent, plugin, and
  MCP server. The Session block's per-model token counts are session API
  totals, not plan draw. Do not plan a per-model pool measurement from it.
- **`/effort` persists per model into `settings.json`** through the stow
  symlink, so an interactive effort change is dotfiles drift.
- **CLAUDE.md sits at the budget edge.** `claude-context-budget` was
  already failing (6,034) before this pass; any addition is paid for in
  the same file.
- **The site-pass experiment is open.** Its verdict comes from the next
  ecxc-ski or 907-life pass's HISTORY numbers, recorded here when known.
  A worse result reverts commit 8a958fe.

Budgets: roughly 2.2M subagent tokens against a 1.5M ceiling. The plan's own
execution (the workflow run, the close-out, and one report fix) took about
1.0M; Geoff's same-day additions after the ceiling was set took the rest
(two adversarial review rounds, about 1.0M, and the outside-evidence
research, about 0.25M). Human touchpoints: the approval, the review
request, and the Workflow and monthly-cadence grants. One question (a
`/usage` baseline percentage) went unanswered and turned out to measure
nothing; the review round removed it. That question is the pass's one
interaction defect.

Same day, on the outside evidence (`docs/superpowers/plans/2026-09-04-fable-5-1-outside-evidence.md`),
Geoff moved the committed Fable effort default from `high` to `medium`, with
`high` raised deliberately for plan authorship, adjudication, and research
turns. The evidence: the system card's peak FrontierCode score at `medium`,
CodeRabbit's review eval where `low` beat `high`, and transcript measurements
of about 2x output tokens per turn against Fable 5.

## 2026-08-30 -- Post-review fix pass

The adversarial three-lens review at the reorg close (correctness,
organization, secrets/idiom; findings in the session record, plan at
`docs/superpowers/plans/2026-08-30-post-review-fix-pass.md`) drove a same-day
fix pass. Security: the sudo cache moved to tmpfs, session context now
redacts export values, the auto-mode trust block scoped to the machine, and
three write-time guards landed (claude-secret-guard PreToolUse hook, gitleaks
pre-commit via `core.hooksPath`, GitHub secret scanning + push protection).
Fresh-machine: bootstrap gained the full uv tool set, `vale sync`, timer
enable, git-hook config, a fingerprint-checked 1Password key, a fixed kitty
install, and stopped routing workstation #2 into the migration restore.
Tooling: `check-drift` (a real stow probe) replaced sync-dotfiles.sh;
update-go and chromium-browser.md retired; tierguard's chained-command false
positive fixed. Organization: `scripts/check.sh` is now the one gate;
MIGRATION-BRIEF.md moved to `docs/`; docs/secrets.md merged into
`secrets/registry.md`; vale's tests joined `tests/`; completed plans moved to
`plans/archive/`; `ROADMAP.md` created.

**What a later pass should not rediscover**:

- **The 2026-01 token leak and its post-mortem** live in
  `secrets/registry.md` under CLOUDFLARE_API_TOKEN. The leaked value is dead
  (verified against the API). The history purge ran the same day on Geoff's
  go: git filter-repo over a mirror clone, HEAD tree verified identical,
  force-pushed (all commit SHAs before 2026-08-30 changed; the pre-purge
  bundle in `~/.local/state/` is the only place the old SHAs and the token
  still exist).
- **A stow package is pure payload**: the gate's own pytest run once wrote
  `__pycache__` into `bin/` and stow linked it into `~/.local/bin`.
  `PYTHONDONTWRITEBYTECODE=1` in check.sh plus `bin/.stow-local-ignore`
  prevent it; anything a tool generates inside a package will be stowed.
- **Hook bypass must be inline**: a PreToolUse hook cannot see per-command
  environment variables, so claude-secret-guard's bypass is the
  `secret-guard-allow` marker on the flagged line, not only the env var.
- **tierguard denies via JSON permissionDecision and exits 0**; testing it
  by exit code alone reads a deny as a pass.
- **devenv-research.md stays in `bluefin/`** deliberately: four site-repo
  backlog entries point at that path (2026-08-30).

Budgets: this pass ran inline (small cross-referenced edits; a chain would
have re-encoded the whole review into every dispatch), roughly 400k tokens
including the three-lens review itself. Human touchpoints: "start the work"
plus two mid-flight refinements (prevention infra, friction preference).

## 2026-08-30 -- Bluefin repo reorg pass

Rewrote the repo end to end for the Mint-to-Bluefin DX migration completed
the same day: purged dead Mint-desktop, apt, Node-version-manager, and aerc
content and consumed migration artifacts (`MIGRATION-RUNBOOK.md`,
`CLAUDE-md-draft.md`, `inventory/`, `themes/`, `wallpapers/`, `android/`),
cleaned `.bashrc` of the Node-version-manager block and dead PATH segments,
fixed the `contacts` package's
`vdirsyncer.service` path and the aerc-era Fastmail token directory,
rescoped `bluefin/flatpaks.txt` to deliberate-only installs, single-sourced
the Stow package list into `bluefin/stow-packages.txt`, adopted `mise` and
`planner` as tracked packages, deduped the vale install path onto Homebrew,
rewrote `workstation-update` for the `ujust`-based Bluefin update flow,
deployed the staged Android udev rule live, and rewrote the root README,
`bluefin/README.md`, the CLAUDE.md Dotfiles Management section, and
`tui-testing.md` to match.

**What the gate caught**: the Python comment gate (`ruff` D rules via
`scripts/check-py-comments.sh`) and `bash -n` syntax checks on every touched
script; the `test_vale_hook.py` suite confirming vale-hook still passed
after the install-path change; a repo-wide grep sweep for stale Mint-era
terms catching leftover references the manual pass missed on the first
sweep. (Correction, same day: the sweep was incomplete — chromium-browser.md
and update-go still carried apt/dpkg content; the post-review fix pass above
retired both.)

**What a later pass should not rediscover**:

- **The vale dual-install-path bug**: `scripts/install-vale.sh` and the
  Brewfile `vale` formula both installed a `vale` binary, and an untracked
  copy at `~/.local/bin/vale` shadowed the Homebrew one on PATH ahead of it.
  Brewfile wins; `install-vale.sh` is deleted, and the untracked binary
  removed. If `vale` behaves unexpectedly again, check `command -v vale`
  resolves to the linuxbrew path before assuming a config problem.
- **The vdirsyncer.service `/usr/bin` bug**: the unit's `ExecStart` pointed
  at `/usr/bin/vdirsyncer`, which does not exist on Bluefin -- `uv tool
  install` puts CLI shims in `~/.local/bin`, not `/usr/bin`. Any systemd
  user unit wrapping a uv-tool binary needs the `~/.local/bin` (or `%h/.local/bin`)
  path, never an assumed system path.
- **The udev rule that was staged but never deployed**: `bluefin/etc/udev/51-android.rules`
  existed in the repo from the migration but was never installed to
  `/etc/udev/rules.d/`; the live system still ran the old Mint `plugdev`
  rule until this pass ran `setup_etc_drops` for real. A file present under
  `bluefin/etc/` is not evidence it is live -- check `/etc` directly.
- **`ruff` missing from the uv tool set post-migration**: the Python
  comment gate depends on it, and the migration's `uv tool install` pass had
  not covered it. Installed via `uv tool install ruff`; `bootstrap.sh`'s
  `setup_mise_uv` now lists it alongside `khard`, `vdirsyncer`, `yt-dlp`.

Budgets: roughly 1.3M tokens of a 3M ceiling (exploration fan-out ~250k, the
execution workflow ~850k over 8 tasks with 16 agent dispatches, plus the
close-out remainder). Human touchpoints: the plan approval and one batched
four-question decision round; two implementer dispatches (T5, T7) were
blocked by the tool-permission classifier over live-system deletions and
finished in the main loop, with the deletion targets parked in
`~/.local/state/trash-2026-08-30/` instead of destroyed.
