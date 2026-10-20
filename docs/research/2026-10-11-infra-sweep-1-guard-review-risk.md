# Infra sweep 1 plan review: data integrity and failure risk

Lens: crash, concurrency, partial write, upgrade, restore, live-machine breakage. Target:
`docs/plans/2026-10-11-infra-sweep-1-guard.md` (cited as "plan") and its prompt
(cited as "prompt"), at `e223c7e`. All probes read-only; the one scratch script is
`/var/home/glw907/.claude/jobs/c747c352/tmp/desc.py`, run with `python3 -I`.

Counts: 1 blocker, 5 major, 8 minor. Two findings are OWNER FORKs (M1, M2).

## Blocker

### B1. `update-skills` writes into the live main checkout, not the T2 worktree

- **Location:** plan:124 ("Then `update-skills` refetches every vendored skill"), plan:135-138,
  plan:140-144; `bin/.local/bin/claude-tooling-sync:47-55`, `:204`, `:225`, `:234`.
- **Defect:** `update-skills` takes only `--home` (default the real home) and builds every write
  path from it: `self.skills = home / ".dotfiles" / "claude" / ".claude" / "skills"` (`:53`) and
  `manifest_path = paths.tooling / "vendored-skills.json"` (`:225`). Run from the T2 worktree,
  with no flag, it overwrites `~/.dotfiles/claude/.claude/skills/*` and the main checkout's
  manifest. `~/.claude` is a Stow link into that checkout (dotfiles-pass: "a merge there is live on
  the machine at once"), so untested upstream skill content and the overlays go live in every
  session on the machine, before any review, and the main checkout is left with warm uncommitted
  changes the idle `~/.dotfiles` session will see (the "one executor" rule's stop signal). The T2
  worktree itself gets no refetch output, so its acceptance (`git diff` over the refetched skills)
  reads an empty diff or tempts the executor to copy files across. No `--home` value can point at
  the worktree: the worktree path has no `<home>/.dotfiles/claude/...` shape. A second trap: a bare
  `claude-tooling-sync update-skills` resolves through `~/.local/bin`, a Stow link to the main
  checkout's old code, which has no overlay step at all.
- **Evidence:** `ls -la ~/.local/bin/claude-tooling-sync` ->
  `../../.dotfiles/bin/.local/bin/claude-tooling-sync`; `Paths.__init__` quoted above; plan:124
  names no flag or invocation path.
- **Fold:** T2's outcome adds `--root TREE` to `update-skills` (as `lint` already has: `:291-292`),
  writing skills and manifest under `TREE/claude/.claude/...`, and makes it the only documented
  form. T2's acceptance states the exact invocation, `bin/.local/bin/claude-tooling-sync
  update-skills --root .` run from the T2 worktree, and adds a check that
  `git -C ~/.dotfiles status --short` is empty after the refetch. A test asserts `--root` writes
  only under the fixture root (the overlay tests can share the fixture). If M2's recommended fold
  is taken, this blocker shrinks to the same `--root` flag on the offline overlay command.

## Major

### M1. The CLAUDE.md line cap fires machine-wide on repo CLAUDE.md files already over 200 lines (OWNER FORK)

- **Location:** plan:89-91 ("`claude-context-budget` fails a `CLAUDE.md` over 200 lines");
  `bin/.local/bin/claude-context-budget:25-28`, `:62`, `:68-73`; `claude/.claude/settings.json:105`.
- **Defect:** `budget_for` budgets every file whose basename is `CLAUDE.md`, and the script is the
  live `PostToolUse` hook on `Write|Edit` for every session. A line cap added inside `check` applies
  to every repo's CLAUDE.md (and their worktree copies) once the merge is pulled into the main
  checkout. The spec and plan:12 scope the cap to the global CLAUDE.md only. Two repo files already
  exceed it, so any edit to them returns exit 2 with blocking feedback that today says "Trim it
  before this turn ends ... Do not raise the budget": an agent in dubplate or aksailingclub-org
  will cut content from that repo's CLAUDE.md, unasked, mid-task. Two more sit at 199 lines, so the
  next one-line addition by any session trips it.
- **Evidence (read-only `wc -l`):** `dubplate/CLAUDE.md` 356, `aksailingclub-org/CLAUDE.md` 262,
  `cairn-cms/CLAUDE.md` 199, `~/.claude/CLAUDE.md` 199, `aksailingclub-sveltekit/CLAUDE.md` 182; the
  rest are under 175. Token budgets are all under 6000 today (dubplate ~5524).
- **Options:** (a) scope the line cap to the global file only (realpath ending
  `claude/.claude/CLAUDE.md`), with its own message naming lines rather than tokens; (b) apply it
  to every CLAUDE.md and trim dubplate and aksailingclub-org first (another repo's content, so out
  of this pass's scope); (c) global cap in the hook, repo files reported only in manual mode.
- **Recommendation:** (a). It matches the spec's ruling, touches no other repo, and the test pins
  it: a 201-line `CLAUDE.md` at a non-global path exits 0 under `--hook`. Whatever is chosen, the
  line-cap message must be distinct from the token message so a session is not told to "archive
  superseded entries" from a repo CLAUDE.md.

### M2. The refetch is an untested upstream bump taken outside `dependency-upgrade` (OWNER FORK)

- **Location:** plan:124, plan:140-144, plan:168-171; `claude-tooling-sync:196-213`.
- **Defect:** `update-skills` refetches every vendored skill at the tip of its default branch, so
  T2 lands an unbounded set of upstream content changes (third-party prose loaded into every
  session's context) alongside the overlays. The global CLAUDE.md routes "every dependency bump
  in every repo" through `dependency-upgrade`; the plan does not. The tip is also
  non-deterministic: T3's "exactly" acceptance for `description-cap` (plan:168-171) assumes no
  vendored skill other than `vhs-cli-demos` crosses 500 characters after the refetch, which depends
  on what upstream pushed that day. And the pin is raced: `head` comes from
  `commits/{branch}` (`:199`), but the tree and each file are read by branch name (`:200`,
  `:211`), so a push between calls records a commit whose files did not land, or vice versa.
- **Evidence:** probe of current descriptions: `vhs-cli-demos` 917 and `golang-spf13-cobra` 722
  (gated) are the only vendored ones over 500; `dependency-upgrade` 496 and `log-project` 486 sit
  just under the cap. Code quoted above.
- **Options:** (a) apply the overlays offline to the installed copies (an `apply-overlays --root`
  mode reusing the overlay function `fetch_skill` will call), no network, no upstream change; the
  tip refetch moves to the next `dependency-upgrade` sweep; (b) refetch at the pinned `commit`
  rather than the branch, so only the overlays change; (c) keep the tip refetch but run it
  through `dependency-upgrade` with the upstream diff reviewed.
- **Recommendation:** (a), with (b)'s fix folded into `fetch_skill` regardless: resolve the head
  SHA once and read the tree and every file at `ref=<sha>`. (a) removes T2's network dependency
  (and with it most of M3), makes T3's acceptance deterministic, and drops the `live-account`
  read from T2.

### M3. The refetch failure path leaves partial state and breaks the pair's gate

- **Location:** plan:57-59 (one commit per task), plan:151-152 ("If `gh api` fails ... the refetch
  step stops the task, not the pair; T1 still merges"), plan:180-181 (T3 starts after the pair);
  `claude-tooling-sync:192`, `:205-213`, `:229-236`.
- **Defect:** `gh_json` and the content fetch run with `check=True`, so a failure mid-loop raises
  an uncaught `CalledProcessError`: earlier skills' files are already overwritten, the file being
  copied may be half-written across its directory, and the manifest (written only after the loop,
  `:234`) keeps the old pins for files that changed. Files deleted upstream are never removed
  (`dest.mkdir(exist_ok=True)` then per-file writes), so a "successful" refetch can also leave
  stale files beside new ones. On the plan side: if T2's manifest gains `description`/`note` but
  the refetch fails, T2's own new `lint` check fails ("lacks its manifest description"), and that
  lint runs in `check.sh`, so the post-pair gate is red and T1 cannot "still merge" cleanly. The
  plan also does not say what T3 does when T2 stopped (T3's `vhs-cli-demos` exclusion depends on
  T2's overlay).
- **Fold:** split T2 into two commits: (1) the tool, tests, and `_doc` change, with no manifest
  overlay fields; (2) the manifest overlay fields together with the refetch (or offline overlay)
  output. On any refetch failure the T2 worktree runs `git restore --source=HEAD --
  claude/.claude/skills claude/.claude/tooling/vendored-skills.json` (worktree only), commit (1)
  merges, and the session stops per "Stops" before T3 rather than running T3 with a wrong
  `description-cap` expectation. In the tool, write the manifest atomically (temp file plus
  `os.replace`) and fetch each skill into a temp directory, then swap it in, preserving local-only
  files such as `vale-setup/LICENSE.vale-agent-tools`.

### M4. The `relative-link` fingerprint is unspecified, and the four seeded links collide

- **Location:** plan:86-88, plan:97-99 ("its seeded entries are exactly the four
  `claude/.claude/docs/bubbletea-conventions.md` links"); `ratchet.py:77-81`, `:177-179`,
  `:216-222`.
- **Defect:** the entry key is `(check, repo, file, fingerprint)`. The four links are two targets,
  each cited twice: lines 11 and 632 both link `research/2026-04-26-bubbletea-norms.md`, lines 13
  and 636 both link `research/2026-04-26-reference-apps.md`. If the fingerprint is the target,
  four entries are two duplicate pairs and `parse` raises "duplicates an earlier entry" (a gate
  config error, exit 2); the correct seed is two entries with `count: 2`. If the executor instead
  puts the line number in the fingerprint to keep four entries, every edit above line 11 changes
  the keys, the re-key partner match (`:216-218`) fails on the new fingerprint, and the pre-commit
  hook rejects any commit that edits that file's top: sweep-2's own DC-10 fix path is then
  blocked by the baseline.
- **Evidence:** `grep -n "](" claude/.claude/docs/bubbletea-conventions.md` -> lines 11, 13, 632,
  636 as above. The ledger's "`:11,13` (four links)" undercounts the lines.
- **Fold:** T1's outcome states the fingerprint as the link target as written (anchor stripped),
  and the acceptance becomes "two entries, each `count: 2`, `finding: DC-10`, `pass: D`". Add a
  test that two dead links to one target in one file report as one key with count 2.

### M5. The GA-03 rewrite rule makes a deleted stowed script pass silently

- **Location:** plan:83-86 ("only when `bin/.local/bin/<x>` is tracked in the tree (`git ls-files`,
  or the file's presence under `<root>/bin/.local/bin`); any other `~/.local/bin` span resolves
  against `--home`"); `check-claude-refs.py:13-18` (the rewrite exists "so a worktree that adds
  or deletes a doc is judged on its own tree").
- **Defect:** a branch that deletes `bin/.local/bin/foo` while a doc still cites
  `~/.local/bin/foo` no longer has `foo` tracked or present in the tree, so the span falls to
  `--home`, where `~/.local/bin/foo` is still the Stow link into the main checkout and resolves.
  The check reports nothing for exactly the defect the self-mode rewrite was built to catch. The
  "or presence" clause also makes the `git ls-files` clause redundant.
- **Evidence:** `ls -la ~/.local/bin/claude-tooling-sync` (a Stow symlink into
  `~/.dotfiles/bin/.local/bin`), against `ls -la ~/.local/bin/poplar` (a regular 28 MB file).
- **Fold:** decide by the home entry's nature, not the tree's: rewrite under the tree when
  `<home>/.local/bin/<x>` is a symlink whose target lies in a `bin/.local/bin/` package (stowed),
  or when the tree holds `bin/.local/bin/<x>`; resolve against home only when neither holds. Add
  the fixture "a stowed (symlinked) bin deleted from the tree is a violation".

## Minor

### m1. A `description` overlay can break frontmatter and unload the skill silently

- **Location:** plan:115-117.
- **Defect:** the overlay replaces a YAML value by text substitution. A description carrying
  `: `, a leading quote, or `#` written in single-line form produces invalid YAML, and the skill
  drops out of every session's skill list with no gate failing (`lint` checks text presence, not
  parse).
- **Fold:** always emit the overlay as a folded block (`description: >` with indented lines), and
  add a fixture with a colon-bearing description that round-trips.

### m2. `dead-reference` now depends on machine state the baseline cannot absorb

- **Location:** plan:84-86, plan:96-97.
- **Defect:** `~/.local/bin/poplar` passes only because the binary is installed here. Uninstall
  it, or run the gate under another home, and `dead-reference` reports a new violation under an id
  registered in `HEAD`, which the ratchet cannot take as a baseline entry. Correct behavior, but
  the gate is no longer a pure function of the tree.
- **Fold:** one sentence in the `check-claude-refs.py` docstring naming that unstowed
  `~/.local/bin` spans resolve against the real home, so a red there means "install or re-cite".

### m3. The launch preflight misses an ahead check and the plan branch's state

- **Location:** plan:41-47; prompt:3-5.
- **Defect:** `rev-list --count HEAD..origin/main` catches a main checkout behind origin but not
  ahead of it; with `baseRef: head` (`claude/.claude/settings.json:6-7`), unpushed local commits on
  main would ride into the PR. The merge reads the local `worktree-infra-sweep-plan` ref, so review
  folds (this file and its siblings sit uncommitted in the plan worktree) are lost if the launch
  precedes their commit.
- **Fold:** add `git -C ~/.dotfiles rev-list --count origin/main..HEAD` (must print 0), `git -C
  <plan worktree> status --short` (empty), and `git rev-parse worktree-infra-sweep-plan` equal to
  `origin/worktree-infra-sweep-plan`.

### m4. No re-merge of `origin/main` before the PR is marked ready

- **Location:** plan:183-197.
- **Defect:** dotfiles has no PR CI (dotfiles-pass "Full-suite home"). If another PR moves the
  baseline or the registry during this pass (for example a GA-04 fix removing its entry), GitHub
  merges the JSON cleanly or with a trivial conflict and `main`'s gate goes red with nothing
  catching it.
- **Fold:** close step 5 merges `origin/main` into the branch and re-runs the gate before the PR
  leaves draft.

### m5. Go-live and rollback are not named

- **Location:** plan:194-197.
- **Defect:** the go-live moment is the main-checkout pull after Geoff's merge, not the merge
  itself: at that pull the hook line cap, the stricter `lint`, and the refetched skills change for
  every session at once, and other open dotfiles worktrees inherit the stricter `lint` on their
  next merge of `main`. The PR body names none of this, nor the rollback.
- **Fold:** the PR body's "what lands live" paragraph names the three changes and the rollback
  (`git revert -m 1 <merge>` on main, then pull in `~/.dotfiles`; no `stow` needed, since no file
  is added or removed under a Stow package root).

### m6. `check.sh` must call the tree's copy of `claude-context-budget`

- **Location:** plan:90-91.
- **Defect:** "`scripts/check.sh` runs it" does not say how. A bare `claude-context-budget`
  resolves through `~/.local/bin` to the main checkout's old copy, which has no line cap, so the
  check passes vacuously in the worktree.
- **Fold:** state the line as `run "... line cap" bash bin/.local/bin/claude-context-budget
  claude/.claude/CLAUDE.md`, as plan:108 already does for the test.

### m7. `claude-context-budget` is a live hook but outside the runner path map

- **Location:** dotfiles-pass "Risk-class path map" (`bin/.local/bin/{cairn-run-gate,ci-green,
  ci-green-lib.mjs,claude-clock-stop,claude-tooling-sync}`).
- **Defect:** the class is right for this pass only because T1 also touches `scripts/**`. A future
  pass editing just the hook would be `ordinary`.
- **Fold:** the PR body's "Found, not done" list names it (out of this plan's scope).

### m8. The risk class and `live-account` flag fit; the flag adds nothing here

- **Location:** plan:15-18.
- **Judgment:** `runner` is correct (every task touches the map). `live-account` is justified by
  the push and the `gh api` reads, but every pass pushes a branch, and `runner` already requires
  all three plan lenses, so the flag costs nothing and buys nothing. If M2's option (a) is taken,
  T2 makes no API reads and the flag rests on the push alone. No over-ceremony finding carries a
  real cost: the close review and guards match pass-core for a roughly 300-minute unattended run.
