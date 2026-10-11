# cairn-cms alignment audit (2026-10-11)

A read-only Opus audit of cairn-cms at `b4cc338` (main, after engine pass B's merge, PR #113)
against the lean pass process, run for the dotfiles conducting session (`c747c352`). Paths are
relative to `~/Projects/cairn-cms` unless they start with `~`. Geoff's rulings on it follow at the
end.

**Short answer.** Step 2 of the cutover cleaned the always-loaded files: CLAUDE.md is 199 lines with
no retired machinery, STATUS is 46 lines, and the repo has no `.claude/agents`, `skills`, `rules`,
or `settings.json`. The misalignment sits one layer down.

## Misalignments, ranked by consequence

1. **Pass B's pipe lesson landed nowhere it runs**, the third occurrence. It was recorded only in
   the PR #113 body and `docs/internal/docs-friction-log.md:76`. The cairn-implementer memory
   already held it twice (`gate-package-race.md:19-26`, 2026-08-30: "Never pipe `npm test` through
   `tail`"; `gate-pipestatus-sh-not-bash.md`). Resolved workstation-wide by dotfiles PR #8, the
   `claude-tail-guard` PreToolUse hook. Still owed in cairn-cms: nothing beyond item 2.
2. **The cairn-implementer memory store holds 52 lessons that never reach pair agents.**
   `~/.claude/agents/cairn-implementer.md:7` sets `memory: project`, and lines 84-86 point the agent
   at `.claude/agent-memory/cairn-implementer/MEMORY.md`. That directory is gitignored
   (`.gitignore:23`) and exists only in the main checkout (52 files, 31 indexed). Pair worktrees
   see none of it. Another 13 lessons exist only inside 7 worktrees (class B below). Some files
   teach retired ritual (`pass-end-ritual-rebase.md`, `pass-end-main-drift-heading-anchor.md`).
   Seven more are committed under `examples/showcase/.claude/agent-memory/` despite the ignore
   rule. Fix: fold the live lessons into `docs/internal/durable-gotchas.md` (which cairn-pass:27-28
   already sends agents to), delete the retired ones, drop `memory: project` from the agent, and
   point it at durable-gotchas.
3. **The project auto-memory teaches retired process**
   (`~/.claude/projects/-var-home-glw907-Projects-cairn-cms/memory/`).
   `plan-for-long-unattended-runs.md:11-15` claims "passes should run 10+ hours unattended" and a
   `pass-core` rule that does not exist. `pairs-by-default.md:13,19` points at deleted runners.
   `docs-rebuild-not-edit.md` (98 lines) reads like a session log, with owed items, a stopped
   reader-test line, and four broken links plus `front-load-into-infrastructure.md:21`.
   `docs-intros-need-framing-step.md` restates `docs-page-chain.js` and `cairn-docs-drafter.md`.
   Fix: delete the first file; cut the other three to the ruling's why, 10 lines or fewer; fix links.
4. **ROADMAP has the wrong shape and contradicts STATUS.** 3,825 lines; tiers Now, Next, Later,
   Considering (`ROADMAP.md:255,984,3057,3704`) against pass-core's Active, Planned, Someday.
   ROADMAP:11-13 names post-mortems as history (ruling 8 says git and PR bodies). ROADMAP:444-445
   says the current step is "finishing stage 2a's close"; STATUS:26 says stage 2b is next. HISTORY
   is cited as live at ROADMAP:438, 445, 456, 477, 1788.
5. **STATUS content.** STATUS:3 ("the past lives in `docs/HISTORY.md`"); STATUS:19-22 narrates the
   gate-economy pass; STATUS:42-43 holds dotfiles work items and a rule that belongs in
   cairn-pass:72-73; STATUS:34-35 lists cleanup of two worktrees already merged and clean.
6. **Friction log.** :34 and :268 name post-mortems as history; :76 and :79 are workstation-tool
   lessons filed in a cairn-only log; :78 asks for a HISTORY field (HISTORY is frozen); :81-265
   ("Triage record") and :266-320 ("Clearings") are about 240 lines of pass history.
7. **Side docs no agent reads.** `docs/internal/public-design-system.md:3-6` ("Read this before any
   work on the public theme") and `docs/internal/code-idioms.md:3-7` have no pointer.
   `docs/internal/dx-backlog-ecnordic-migration.md` (2026-06-04) is a backlog the friction log says
   the repo does not keep. `engine-harvest-candidates.md` and `pre-beta-harvest.md` are cited only by
   CHANGELOG and the README index.
8. **cairn-pass:24** says "The `--fast` flag lands in rollout step 2"; it landed in PR #112 (dotfiles
   edit).
9. **HISTORY** is correctly frozen (`docs/HISTORY.md:3`; last write `ec1262387`), but is cited as live
   at STATUS:3 and `durable-gotchas.md:95`, and `HISTORY.md:5-6` cites a global CLAUDE.md section
   that no longer exists.

## Keep (cairn-specific, with a catch record or ruling)

The friction log (ruling 8 keeps it in cairn only); `engine-rulings.md` (read by `engine-triage`,
`engine-consult`, cairn-pass:76-77, `check-rulings-format.mjs`); the docs page chain (rollout step 4
kept all six seats); `docs-register.md`; visual verification (three STRUCTURAL catches in pass B);
the admin smoke; release discipline; `durable-gotchas.md`; `pass-gate-tiers.md`.

## Worktrees (42 linked plus main; none locked; 53 GB)

| Class | Count | Worktrees |
|---|---|---|
| A. Merged, clean: removable | 26 | admin-motion, admin-motion-8, agent-a271…, agent-aa3c…, agent-ab02…, cairn-tool-b2, chassis-b2, deps-2026-10, docs-to-facts, doctor-cleanup, doctor-engine, doctor-go, doctor-pretask, doctor-retirement, e2e-flakes, engine-pass-b, engine-pre-2b-a, engine-pre-2b-b, extend-2, extend-2-skills, polish-11a, polish-c, pre-cut, sveltekit-3, theme-identity-a, tool-1-1-0 |
| B. Merged, clean, holds memory files not in main: copy out first | 7 | cairn-tool-a (1), chassis-b (5), doctor-records (1), draft-docs-2a (3), draft-docs-a (1), draft-docs-harvest (2), identity-seam (1) |
| C. Merged, with a leftover local file | 3 | gate-tier-tool (modified `package-lock.json`), polish-11b-i and polish-11b-ii (one untracked capture spec each) |
| D. Not an ancestor of main, content landed | 2 | gate-related (`git cherry` 0), theme-b-plan (all 6 files on main) |
| E. Unmerged, unique work | 4 | engine-pre-2b-a-fix2 (1 stray changelog commit, 40fcf6b1), draft-docs-plans (superseded 2026-09-21 plans), experiment-screen (volunteer roster screen, 15 files), docs-reset-dryrun (scratch, 4 uncommitted changes, line stopped by ruling) |

Also in `.claude/worktrees/`: `cairn-scratch/` (six tarballs, 8.5 MB) and a file named `--cwd`.

## Geoff's rulings (2026-10-11)

- Run a cairn-cms alignment pass before docs stage 2b.
- Keep `experiment-screen`. Drop `draft-docs-plans`, `docs-reset-dryrun`, and fix2's stray commit.
  Copy the class-B memory lessons out before removing the 35 merged worktrees (classes A, B, D).
- The full ROADMAP restructure (tiers and triage) is a separate pass after docs stage 2b; the
  alignment pass fixes only the header and the stale entry that contradicts STATUS.
