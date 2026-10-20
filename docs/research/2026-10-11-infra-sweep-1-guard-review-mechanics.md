# Infra sweep 1 plan review: mechanics and feasibility lens (2026-10-11)

Target: `docs/superpowers/plans/2026-10-11-infra-sweep-1-guard.md` (cited "plan") and
`docs/superpowers/plans/2026-10-11-infra-sweep-1-guard-prompt.txt` (cited "prompt"), at `e223c7e`.
Probes ran with `python3 -I` from scratch scripts under `~/.claude/jobs/c747c352/tmp/`, plus
read-only `gh api` calls against the four vendored-skill upstreams.

Counts: 1 blocker, 7 major, 12 minor.

## Blocker

### B1. `update-skills` writes into the main checkout, not the pair's worktree

- **Location.** plan:124 ("Then `update-skills` refetches every vendored skill"), plan:135-138.
- **Defect.** `update-skills` builds its paths from `--home`, never from a tree root. Run from
  T2's pair worktree, it reads the main checkout's manifest, which carries no overlays. It then
  writes the fetched skills and the rewritten manifest into `~/.dotfiles` on `main`. Those files
  are stowed, so the change is live on the machine. The worktree gets nothing, T2's `lint` stays
  red there, and `main` is left dirty, which the prompt forbids.
- **Evidence.** `bin/.local/bin/claude-tooling-sync:52-53`:
  `self.tooling = home / ".dotfiles" / "claude" / ".claude" / "tooling"` and
  `self.skills = home / ".dotfiles" / "claude" / ".claude" / "skills"`; `:288`
  `update.add_argument("--home", type=Path, default=Path.home())`; `:308`
  `return update_skills(Paths(args.home.resolve()), args.names)`. The command has no `--root`.
- **Fold.** Prefer M2: apply the overlays offline to the worktree's installed copies, with a
  subcommand taking `--root` (for example `apply-overlays --root .`). If a refetch stays, T2 first
  adds `--root` to `update-skills` (`Paths` derived from the root), and the plan names the exact
  command `bin/.local/bin/claude-tooling-sync update-skills --root .`. The acceptance adds
  "`git -C ~/.dotfiles status --short` is empty after T2".

## Major

### M1. A refetch silently reverts the local `vale-ci` pin bump

- **Location.** plan:124, plan:140-143 (acceptance: "only the overlays, the sibling rewrites, and
  upstream changes since the pinned commit").
- **Defect.** The vendored `vale-ci/SKILL.md` carries a local edit: `rev: v3.22.0`, from commit
  `4cb4d62` ("apply the 2026-09-19 docs-infra audit's small tier"). Upstream at the pin, and at its
  head (the pin equals the head), still reads `v3.17.0`. A refetch reverts the edit. The plan's
  acceptance has no category for that diff line, and no overlay field can preserve it.
- **Evidence.** The upstream diff probe at the pin shows `vale-ci: 48c48 <     rev: v3.17.0 --- >
  rev: v3.22.0`. `vale-cli/agent-tools head=5e8704f5c07a pin=5e8704f5c07a ahead_by=0`.
- **Fold. OWNER FORK.**
  - (a) Accept upstream's `v3.17.0` and put the version advice in the `vale-ci` `note` ("pin the
    current Vale release; upstream's example is older"). No new mechanism.
  - (b) Add a third overlay kind (literal `replace` pairs) to carry the bump.
  - (c) Skip the refetch for now (M2), keep the edit, and log the gap in "Found, not done".
  - **Recommendation:** (c) for this pass, then (a) when a refetch next runs. Either way, the plan
    names the line.

### M2. The refetch adds failure modes and no content

- **Location.** plan:124, plan:151-152 ("If `gh api` fails ... the refetch step stops the task,
  not the pair; T1 still merges"), plan:16-17 (`live-account` because of the refetch).
- **Defect.** No vendored skill path changed upstream since its pin, so a refetch only moves the
  commit pins. It still adds three costs:
  - **Network failure.** The task fails if `gh api` cannot reach GitHub.
  - **A broken failure branch.** If the refetch fails after T2's lint and manifest fields land,
    the new lint fails on every skill that lacks its overlay. T2 then cannot commit green, and
    "stops the task" leaves the pair half-done.
  - **An unrouted bump.** A pin move is a dependency bump that skips `dependency-upgrade`, which
    the global CLAUDE.md requires.

  It also brings the B1 hazard and the M1 revert.
- **Evidence.** The compare probe filtered `compare/<pin>...<branch>` files to each skill path:
  - `saadeghi/daisyui`: 30 commits ahead, 0 files under `skills/daisyui`.
  - `gfargo/skills`: 5 ahead, 0 files under the vhs path.
  - `samber/cc-skills-golang`: 1 ahead, 0 files.
  - `vale-cli/agent-tools`: 0 ahead.

  Every local file except `vale-ci/SKILL.md:48` and the rename `name:` lines is byte-identical to
  upstream at the pin.
- **Fold.**
  - T2 builds the overlay function and applies it offline to the installed copies, through the
    same function `fetch_skill` calls. The plan's idempotence test already covers a second
    application.
  - Drop the refetch and its failure clause. Drop the `gh api` clause from `live-account`; the push
    and PR keep the flag.
  - Leave the pin moves to the next `dependency-upgrade` sweep.
  - T2's estimate falls to about 100 minutes.

### M3. The four relative-link seeds collide as duplicate entries

- **Location.** plan:97-100 ("its seeded entries are exactly the four
  `claude/.claude/docs/bubbletea-conventions.md` links").
- **Defect.** The four links have only two distinct targets: lines 11 and 632 share one, and
  lines 13 and 636 share the other. If the fingerprint is the link target (the natural choice,
  and the plan names none), four entries produce two duplicate keys, and `parse` raises
  `ConfigError` (exit 2). The plan never states the fingerprint either.
- **Evidence.** The relative-link probe found hits at `bubbletea-conventions.md` lines 11, 13, 632,
  and 636, with two targets (`research/2026-04-26-bubbletea-norms.md`,
  `research/2026-04-26-reference-apps.md`). `ratchet.py:178-179`: `if k in keyed:
  found.append("duplicates an earlier entry")`. Probe: four entries give `ConfigError: [... entry 6
  ...: duplicates an earlier entry', ... entry 7 ...]`. Two entries with `"count": 2` pass
  `parse`, and growth against HEAD returns `[]`.
- **Fold.** Name the fingerprint (the raw link target, anchor kept). Change the acceptance to
  "two entries, one per target, each `count: 2`, `finding: DC-10`, `pass: D`".

### M4. The line cap would block edits to every repo's CLAUDE.md, not only the global one

- **Location.** plan:89-91 ("`claude-context-budget` fails a `CLAUDE.md` over 200 lines"), plan:12
  ("The global CLAUDE.md has a 200-line cap").
- **Defect.** `budget_for` budgets any file whose basename is `CLAUDE.md`. The script also runs as
  a PostToolUse hook on every Write or Edit, in every project. A cap added beside the token budget
  would return exit 2 on each edit to dubplate's and aksailingclub-org's `CLAUDE.md` as soon as
  this merges. That changes behavior in other repos, which the plan's scope excludes.
- **Evidence.** `claude-context-budget:28`: `if [ "$base" = "CLAUDE.md" ]; then echo
  "$CLAUDE_MD_BUDGET"; return; fi`. `claude/.claude/settings.json:103-107` wires
  `claude-context-budget --hook` as a PostToolUse command. `wc -l`: dubplate 356,
  aksailingclub-org 262, cairn-cms 199.
- **Fold.** Apply the line cap only when the realpath is the global file (it ends in
  `/claude/.claude/CLAUDE.md` or equals `$HOME/.claude/CLAUDE.md` resolved). Add a test that a
  250-line repo `CLAUDE.md` still exits 0. OWNER FORK only if per-repo caps are wanted now; the
  old spec lettered them F, and the lean re-plan dropped cross-repo work. **Recommendation:**
  global only.

### M5. Pair subagents never receive the Conventions

- **Location.** prompt:14-16 ("each given its task's full text from the plan").
- **Defect.** A subagent starts with zero context. The task text alone leaves out the rules T1
  and T2 need:
  - the gate command and its exit-75 rule;
  - one commit per task with the task-id subject;
  - the ratchet entry shape, the pass labels, and the GA-nn rule;
  - registering an id and seeding its entries in the same commit;
  - the tool protocol;
  - the "Found, not done" scope rule.

  T1's baseline edit fails the pre-commit hook or the gate without them.
- **Fold.** The prompt dispatches each subagent with the task text plus the plan's "Conventions
  every task follows" section, verbatim, minus "Clock" and "Stops", which belong to the session.
  It adds one line saying no command may write `~/.dotfiles` (B1).

### M6. The end-to-end check expects output the ratchet never prints

- **Location.** plan:26-28 ("`ratchet.py check --root .` lists the registry ids ...").
- **Defect.** A clean `check` prints nothing, so nobody can observe the registry ids being
  "listed". The executor either reports a check it could not see or spends time hunting for it.
- **Evidence.** `ratchet.py:331-332`: `if not found: return 0` (no print).
- **Fold.** Replace the clause with two checks. First, `python3 claude/.claude/tooling/ratchet.py
  check --root .` exits 0. Second, `python3 -c 'import json; print(sorted(json.load(open(
  "claude/.claude/tooling/ratchet-baseline.json"))["checks"]))'` prints the five ids.

### M7. The trigger checks the spec requires for trimmed descriptions are missing

- **Location.** Spec "Lean re-plan", "Method calls": "Each trimmed description gets trigger checks
  (three should-trigger and two should-not prompts in fresh `claude -p` sessions, before and
  after)". Plan T2 (plan:125-130) trims `daisyui` and `vhs-cli-demos` and has no such step.
- **Defect.** The plan silently drops a mechanism the spec states. A pair subagent nesting
  `claude -p` is also a cost and permission question the plan does not address.
- **Fold. OWNER FORK.**
  - (a) Add the check to the session's post-merge step for the two trimmed descriptions, not to
    the subagent: five prompts each, before and after, recorded in the PR body.
  - (b) Amend the spec so trigger checks apply to sweep-2's authored-skill trims only. Vendored
    descriptions are scoped by their overlay text.
  - **Recommendation:** (a) for `daisyui`, whose scope change is the point of CS-8, and (b) for
    `vhs`, whose tool is not installed anyway.

## Minor

### m1. The fork-skill seed counts and the PS-20 phrase are settled already

- **Location.** plan:171-174.
- **Defect.**
  - In `register-check`, "delegated" occurs twice (lines 11 and 62), so its entry needs `count:
    2`. Three of the four phrases hit, which makes three entries, all `PS-06`.
  - `content-review` has 0 hits on all four phrases, so the plan's "if the phrase list misses" is
    certain, not conditional.
- **Evidence.** Probe: `fork register-check 'under discussion' hits=1`, `'during the session'
  hits=1`, `'delegated' hits=2`; `fork content-review ... hits=0` for each phrase.
  `content-review/SKILL.md:46`: `Ask "apply all, apply some (specify), or skip?"`.
- **Fold.** Name the added phrase in the plan (`ask "apply all`, case-insensitive). State the
  seeds: `register-check` gets three entries (one with `count: 2`), and `content-review` gets one.

### m2. The GA-03 fix lets a worktree delete a stowed bin unnoticed

- **Location.** plan:83-86.
- **Defect.** Suppose a worktree deletes `bin/.local/bin/<x>` while a doc still cites it. Under
  the presence-or-`ls-files` rule, the span falls back to home, where the stow symlink into the
  main checkout still resolves. The check misses the very case the self-mode rewrite exists for:
  "a worktree that adds or deletes a doc is judged on its own tree" (`check-claude-refs.py:17-18`).
- **Fold.** Treat a span as tree-owned when `bin/.local/bin/<x>` is tracked at `HEAD` (`git
  ls-tree HEAD`) or present in the working tree. Fall back to home otherwise. A fixture covers it:
  a tracked-at-HEAD file deleted from the tree is a violation. The probe found only `poplar` (two
  spans) and `scoped-test` (GA-05) outside the tree, and `scoped-test` stays a violation because
  it is absent from home.

### m3. The replaced description must be written as a YAML-safe scalar

- **Location.** plan:115-116.
- **Defect.** A plain scalar containing `: ` or a leading quote breaks the frontmatter, and Claude
  Code then drops the skill. The new lint compares text and would not catch it.
- **Fold.** Emit the replaced value JSON-quoted (`description: ` + `json.dumps(value)`, which is a
  valid YAML double-quoted scalar). Add a fixture whose description contains `: `.

### m4. "Call the overlay function" needs a stated loading method

- **Location.** plan:145-150.
- **Defect.** The tool is an extensionless script, and the existing tests drive it through a
  subprocess (`tests/test_claude_tooling_sync.py:24-28`). Importing it needs
  `importlib.machinery.SourceFileLoader`, and that import writes `__pycache__` into the stowed
  `bin/.local/bin` outside `check.sh` unless `sys.dont_write_bytecode` is set first. `check.sh:10`
  sets `PYTHONDONTWRITEBYTECODE`, but the focused leg does not.
- **Fold.** Test through the M2 subcommand by subprocess, like the existing tests. Otherwise, the
  plan names the loader and the bytecode guard.

### m5. `ratchet-report` must take the injected root flags and import lazily

- **Location.** plan:157 ("a `ratchet-report --root <root>` subcommand").
- **Defect.** The protocol forwards `--home`, `--projects-root`, and `--memory-root` to every tool
  (`ratchet.py:26-27`, `:264`). A subparser that takes only `--root` exits 2 when any of them is
  passed. A top-level `import ratchet` would also make `apply` and `verify` depend on
  `ratchet.py`.
- **Path resolution is sound.** `~/.local/bin/claude-tooling-sync` is a symlink to
  `../../.dotfiles/bin/.local/bin/claude-tooling-sync`, and `resolve().parents[3]` is the repo
  root. A check run invokes the worktree path. The file mode is `100755` with a
  `python3` shebang.
- **Fold.** Accept the three flags, which may be ignored, as `check-claude-refs.py:266-269` does.
  Set `sys.dont_write_bytecode` and import `ratchet` inside the `ratchet-report` branch.

### m6. A missed seed cannot land as a second commit

- **Location.** plan:57-60.
- **Defect.** Once a task's commit registers an id, a later commit that adds an entry under it
  fails the hook.
- **Evidence.** Probe: `late seed under relative-link: [('relative-link', 'new entry under
  registered id: x.md: y')]`.
- **Fold.** One line: a missed seed is fixed by amending the unpushed registering commit.

### m7. `update-skills` reflows the manifest

- **Location.** `claude-tooling-sync:234-236` (`json.dump(manifest, f, indent=2)`).
- **Defect.** The five one-line vale entries would expand to multi-line, which makes for a noisy
  diff. A round-trip probe returns `False`.
- **Fold.** This matters only if a refetch is kept (M2). Accept the reflow, or edit the manifest
  by hand.

### m8. The plan and pass-core disagree on the pair's clock

- **Location.** plan:71-73 versus pass-core:101-108 ("Pair worktrees hold no clock file").
- **Fold.** State the rule: the session holds no clock while the pair runs, the subagents write
  none, and the session checks the pair's overrun on return (estimate 150, or about 100 after
  M2). T3 and the close write clocks in the session worktree.

### m9. `claude-tooling-sync verify` at close checks `main`, not the branch

- **Location.** plan:191.
- **Defect.** `verify` reads `~/.dotfiles` (B1's `Paths`), so on an unmerged branch it re-verifies
  `main`. It passes today (probe rc=0).
- **Fold.** Keep it as the adapter requires, and note that it is a machine-state check, or move it
  to a post-merge line in the PR body.

### m10. The `link-ok` marker puts noise into an agent prompt

- **Location.** plan:88-89 and plan:93-94 (`cairn-docs-drafter.md:126`).
- **Defect.** The false positive is a link quoted inside an inline-code span in the agent's
  instructions. The marker becomes text the drafter reads on every run.
- **Fold.** Skip link syntax inside inline-code spans and fenced blocks, which catches the case
  with no marker and no agent edit. Keep `link-ok` as the escape hatch only.

### m11. Launch-time STATUS is missing

- **Location.** plan:33-49.
- **Defect.** pass-core "Execute" says "STATUS records the session's name and id". The plan writes
  STATUS only on a stop and at close.
- **Fold.** The session writes a one-line in-flight STATUS after its first commit.

### m12. GA-06 and GA-07 differ only by pass label (over-ceremony, low cost)

- **Location.** plan:168-170.
- **Defect.** `parse` does not tie a GA id to one pass label (`ratchet.py:162-173`), so one GA-06
  carrying a per-entry `pass` covers all three skills.
- **Fold.** Optional: one GA id.

## Verified as the plan states

- **Launch flags.** `claude --bg`, `--model`, `--effort`, and `-n/--name` all exist in `claude
  --help`, and `claude agents --json` exists.
- **Prompt delivery.** `worktree-infra-sweep-plan` is a local branch in the shared ref store, so
  `git show <branch>:<path>` works from the main checkout. `main` is at `4231a67`, an ancestor of
  the branch, so the merge fast-forwards. A `$(...)` substitution's output is not re-evaluated, so
  the prompt's backticks are safe.
- **Worktree base.** `worktree.baseRef: "head"` is set (`claude/.claude/settings.json:6-7`), and
  `.claude/worktrees/` is ignored.
- **Pair disjointness.** T1 and T2 touch disjoint files. T2 touches neither the baseline, nor
  `tests/test_check_claude_refs.py`, nor `check.sh`. Vendored skills sit outside `dead-reference`
  and `relative-link` scope.
- **Ratchet rules.**
  - Removing the GA-03 entries and registering `relative-link` with seeds return growth `[]`.
  - T3's `description-cap` seeds, with GA-06 and GA-07 carrying `defect`, return `[]` against the
    T1 baseline.
  - GA-06 and GA-07 match `FINDING_ID`, and `C` and `D` are in `PASS_LABELS`.
- **Seed counts.** `description-cap` live hits match the plan: `cairn-release` 849,
  `visual-fidelity` 672, `go-conventions` 530, `tui-visual-verify` 534, `svelte-check` 599, and
  `vhs-cli-demos` 915. `golang-spf13-cobra` 720 is gated by an upstream `paths:` key, so a
  refetch keeps it.
- **Line cap.** The global `CLAUDE.md` is 199 lines and 11159 bytes, and `claude-context-budget`
  exits 0 on it.
- **GA-03.** `~/.local/bin/poplar` exists at home.
- **Sibling spans.** The only sibling spans are `vale-setup:11,12,67`, `vale-fix:20,114`, and
  `vale-triage:36`.
- **Risk class.** `runner` is right for every path, and no `auth-data` path is touched.
- **Clock.** T1 120 and T3 90 look realistic. T2 150 is high once M2 removes the refetch.
