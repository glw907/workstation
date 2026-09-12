# Claude infra round handoff

Plan revision 2 at `1ec5c0a`, drafted against `9034fd3`, three-lens review recorded at
`506772e`. Executed 2026-09-12 by the dubplate session; implementer general-purpose at sonnet,
reviewer diff-reviewer at opus, gate `cd /var/home/glw907/.dotfiles && bash scripts/check.sh`
through cairn-run-gate; baseline green at `bbcc6cb`.

Task results: task 1 accepted, 0 fix rounds, dotfiles `95c65a7`, dubplate `a30d32e`. Task 2
accepted, 0 fix rounds, dotfiles `f905328`. Task 3 accepted, 0 fix rounds, 907-life `9ab912f`,
ecxc-ski `b276e0c`, dotfiles `dbb653d`. Task 4 accepted, 0 fix rounds, 907-life `1ec7fd0`,
ecxc-ski `0131ac0` then `7817b36`, dotfiles `aa20264`. Task 5 accepted, 0 fix rounds, dubplate
`f3a55da`, dotfiles `a2c6463`. Task 6 accepted after 1 fix round, dotfiles `2059e84` then
`a30733e`. Task 7 accepted, 0 fix rounds, dotfiles `12017a4`. Task 8 accepted, 0 fix rounds,
dotfiles `23f8885`. Task 9 deferred by Geoff's ruling at the 80% flag: the cairn overnight
workflow `wf_2d52758e-603` was still live at the segment-C boundary. Conductor checkpoints
`45fe6d8` and `85c8d56`. Measured spend about 1.55M subagent tokens against the 1.5M ceiling,
over by the battery-interrupted first run of segment B. Attended time: zero planning misses,
one execution sitting, the 80% flag question.

## Draft for docs/STATUS.md

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
- **Claude infra round closed**: the exit-75 reattach protocol is correct in
  every implementer that calls `cairn-run-gate`; the unattended-work guards
  doc is corrected; `svelte-check` and `go-architecture-reader` are hoisted
  to workstation agents; the workstation and dubplate instruction files are
  hoisted with repo-specific supplements; the model-economy doc carries the
  three 2026-09-04 carries; `claude/.claude/CLAUDE.md` displaced to 23,947
  bytes and picked up the docs standard's four lines. Handoff:
  `docs/superpowers/plans/2026-09-12-claude-infra-round-handoff.md`.
- **Docs standard, plan one closed**: the tellgrader `docs-register` profile and opt-in
  discovery, `MEASURES.md` as the canonical measure definition, the output-style and voice-file
  updates, the path-grading Vale hook, the four review agents (including `figure-verifier`),
  and the two skills (`cairn-figure`; `writing-voice`'s renamed author-facing section).

## Immediate next action

Plan two of the cairn documentation standard: its handoff is
`docs/superpowers/plans/2026-09-08-docs-standard-claude-infra-handoff.md`. Once the cairn
overnight workflow has ended, also run the infra round's deferred task 9 (`pass-execute.js`
and its skill text).

Owed, from the infra round's handoff: `cairn-cms/CLAUDE.md`'s own four-line pick and budget
trim; poplar's `go-architecture-reader` adoption; whether `aksailingclub-org`, `xcathletes-org`,
or `cairn-pub` wants a `CLAUDE.md` pointer at `~/.claude/instructions/`; whether the
overnight-run runaway guard should become an armable script in `bin/.local/bin/`; the
dubplate-implementer worktree gate-string note (a worktree lane must be told the dispatch's own
absolute string wins).

## Open items

Strategic and standing items live in `ROADMAP.md` (history purge decision,
musicbox repo split, devcontainers, kitty-harness replacement, custom uBlue
image, restore split, the cairn documentation standard).

## History

Per-pass ledger: `docs/HISTORY.md`.

## Draft for docs/HISTORY.md

### 2026-09-12 -- Claude infra round

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
one non-blocking note, corrected in this round's own task 10: `pass-gate-economy.md` still said
`cairn-run-gate` "blocks to completion" after the exit-75 correction landed in CLAUDE.md.
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

## Draft for ROADMAP.md

No Active entry changes ownership. The cairn documentation standard's Active entry gains one
line: the workstation `CLAUDE.md` now carries the standard's four docs-standard lines (task 8),
so that entry's "continuing obligation" note should say `claude/.claude/CLAUDE.md` is done and
only `cairn-cms/CLAUDE.md` still owes its own pick and budget trim. Nothing from this round
belongs in Planned or Someday: every landed task was a correction or a hoist to existing
infrastructure, not a new multi-pass initiative.

## Owed follow-ups

- Task 9 (`pass-execute.js` and its skill text), deferred by the segment-C launch condition;
  runs once the cairn overnight workflow has ended.
- poplar's `CLAUDE.md` names no architecture reader, so `go-architecture-reader` is available
  to poplar and dispatched by nothing. Poplar's own pass adopts it.
- `~/Projects/cairn-cms/CLAUDE.md` is over its cap (24,873 bytes) and owes its own four
  docs-standard lines.
- Whether `aksailingclub-org`, `xcathletes-org`, or `cairn-pub` wants a `CLAUDE.md` pointer at
  `~/.claude/instructions/`; this round deliberately did not add one.
- Whether `~/.cache/cairn-overnight-2026-09-12/runaway-guard.sh` should be copied into
  `bin/.local/bin/` as an armable form.
- The dubplate-implementer worktree gate-string note: its gate example names the main tree, so
  a worktree lane must be told the dispatch's own absolute string wins.
- The out-of-scope notes recorded verbatim in the plan's "Out of scope, recorded" section:
  dubplate's `check.sh` forms (`--scope-changed`, `--reduced`, `--merge`) and its two staged
  legs (`CHECK_CITATIONS`, `CHECK_EXPORTED_UNUSED`), one consumer each; dubplate's
  `simplifier-brief.md` and `tools/close-evidence`, one consumer each; `STATUS.md` over the
  60-line cap in six repos (907-life 236, cairn-pub 183, ecxc-ski 173, cairn-cms 100,
  xcathletes-org 69, aksailingclub-org 68), already each repo's own close-out chore; poplar has
  no `docs/STATUS.md`, `HISTORY.md`, or `ROADMAP.md`, poplar's own chore; poplar's implementer
  runs `make check` directly and never calls `cairn-run-gate`, so item 1's correction does not
  apply there, adoption is poplar's own decision; `cairn-cms/CLAUDE.md`'s ranked displacement
  candidates are already measured in
  `docs/superpowers/plans/2026-09-08-claude-md-displacement-candidates.md`; the `ship` skill in
  `aksailingclub-legacy` and `ecxc-ski` share a name and have diverged, convergence is whichever
  repo next touches its own copy; `907-life/.claude/instructions/css-rules.md` has one consumer
  and stays there; the site-pass experiment's verdict goes into `docs/HISTORY.md` when the next
  `ecxc-ski` or `907-life` pass closes, with commit `8a958fe` reverted on a worse result; the
  first monthly model review is due 2026-10-01, already an Active ROADMAP entry with
  `model-review.timer`.
