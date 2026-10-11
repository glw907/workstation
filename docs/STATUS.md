# Status

Dotfiles and machine configuration for one Bluefin DX workstation
(`thinkpad-x1`, Fedora 44 base, `bootc`/`ostree`). GNU Stow links tracked
config into `$HOME`; `bluefin/` holds the fresh-machine provisioning
artifacts. github.com/glw907/workstation.

## Current state

- **Stow packages** (single source: `bluefin/stow-packages.txt`): `bash beets
  bin claude contacts git kitty mise upkeep vale`. `bluefin/bootstrap.sh` and
  `check-drift` both read that file.
- **Layered RPMs** (`bluefin/layered-packages.txt`): `1password
  1password-cli firefox chromium`, kept deliberately minimal and
  change-controlled through `docs/MIGRATION-BRIEF.md`.
- **CLI tools**: Homebrew (`bluefin/Brewfile`) for most formulae; `uv tool
  install` for Python CLIs (`khard`, `vdirsyncer`, `yt-dlp`, `ruff`, `jrnl`,
  `beets`); `mise` for per-project Node.
- **Flatpaks** (`bluefin/flatpaks.txt`): deliberate installs beyond
  Bluefin's stock set only.
- **Secrets**: age-encrypted in `secrets/values.age`, synced by
  `scripts/secrets/sync.sh`; architecture and inventory in
  `secrets/registry.md`. Write-time guards: claude-secret-guard hook,
  gitleaks pre-commit, GitHub push protection.
- **Gate**: `scripts/check.sh` (shell syntax, ruff-D, tests, vale fixtures,
  gitleaks, tellgrader go check).
- **Claude infra round closed**: the exit-75 reattach protocol is correct in every
  implementer that calls `cairn-run-gate`; `svelte-check` and `go-architecture-reader` are
  hoisted to workstation agents; the workstation and dubplate instruction files are hoisted
  with repo-specific supplements; `claude/.claude/CLAUDE.md` displaced to 23,947 bytes and
  picked up the docs standard's four lines. Handoff:
  `docs/superpowers/plans/2026-09-12-claude-infra-round-handoff.md`.
- **Docs standard, plan one closed**: tellgrader's `docs-register` profile, `MEASURES.md`,
  the output-style and voice-file updates, the path-grading Vale hook, the four review agents
  (including `figure-verifier`), and the two skills (`cairn-figure`; `writing-voice`'s
  renamed author-facing section).

- **Spec and plan review skill (2026-09-23)**: `spec-plan-review` encodes the dubplate rung 6
  review process (lenses, a fold that may refuse, a verification read, prose last). The
  dubplate-owed `pass-execute.js` edit is done: `stopOnEscalate` (default true, sequential runs)
  ends a run at the first unaccepted task and marks the rest skipped.

## Immediate next action

**Lean pass process cutover** (Geoff approved the design 2026-10-10). Spec:
`docs/superpowers/specs/2026-10-10-lean-pass-process-design.md`; evidence beside it in
`docs/superpowers/research/2026-10-10-{anthropic-agentic-guidance,pass-catch-ledger}.md`. The cutover
runs on the new process from its first step. Resume prompt, launched from `~/.dotfiles` with
`claude --model claude-opus-5-5 --effort high`:

> Read `docs/superpowers/specs/2026-10-10-lean-pass-process-design.md` and the two research files it
> cites. It is a `runner`-class pass. Run its spec review as the spec itself defines it (three
> parallel Opus lenses: contract, mechanics, risk; a fold that probes every new mechanism; one
> verification read), bringing Geoff only findings that change the approved design. Then write the
> plan per the spec's Lifecycle step 4 (three plan lenses, since `runner`), covering Rollout steps 1
> to 4, and execute it per the spec's Execution section. Before the plan, decide which items of the
> infra sweep below the cutover supersedes and record that here. Pass B in cairn-cms (Rollout step 5)
> resumes only after steps 1 to 4 merge.

**Infra sweep after the cutover** (decided 2026-10-10; spec
`docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`, audit
`claude/.claude/docs/record/2026-09-28-claude-infra-audit.md`; A-core `c3e709c` and B `7de1210`
merged). The rule: an item is superseded when the cutover rewrites or deletes the file it targets,
and the rewriting task takes that item's audit ids as inputs. An item on a file the cutover leaves
alone survives, and its pass is re-planned in the lean format after rollout step 3.

- Style-guide-sync (cairn-cms): the runner amendments 1 to 4, 7, 9, and 10 are superseded. The
  content (chain W's tasks, amendments 5, 6, and 8) survives as a lean task list, and any W edit to
  a file the cutover rewrites (the implementers, the global `CLAUDE.md`, `docs-page-chain.js`)
  moves into that rewrite.
- A-rest: the seat check (`seats.json`) and the `pass-core` close wiring are superseded. The
  context-budget check (it holds ruling 6), the remaining reference checks, cross-repo mode, the
  monthly drift routine, and the release trigger survive. The duplicate-paragraph check and
  `parity.json` wait for a catch record on the shrunken surface (ruling 2).
- C: findings on `pass-core`, `spec-plan-review`, `cairn-pass`, and `site-pass` (PS-11 and
  PS-15 among them) are superseded; findings on every other skill and doc survive.
- D survives whole.
- E: AW-11 (runner merge), AW-21 (implementer parity), and DC-19 and DC-21 (global CLAUDE.md
  routing) are superseded. `omitClaudeMd` and `.claude/rules/` survive as options.
- F: the cairn-cms and site rows are superseded by rollout steps 2 and 3. The poplar row survives.
- Owed from the infra round: cairn-cms's CLAUDE.md trim (step 2), the runaway-guard script
  question (the unattended-guards fold), and the dubplate-implementer gate-string note (step 3)
  are superseded. Poplar's `go-architecture-reader` adoption stays poplar's call.

## Open items

Strategic and standing items live in `ROADMAP.md` (history purge decision,
musicbox repo split, devcontainers, kitty-harness replacement, custom uBlue
image, restore split, the cairn documentation standard).

- `cairn-run-gate` runs an unknown `--` flag as a gate string (2026-10-10). The cutover's
  Execution item 6 fixes it.

## History

Per-pass ledger: `docs/HISTORY.md`.
