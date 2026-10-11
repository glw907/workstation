# Lean pass cutover plan: final verification read (second fold)

Target: the second fold, `git diff bd7525d d3ffc29 -- docs/superpowers/plans/`: the plan
`docs/superpowers/plans/2026-10-10-lean-pass-cutover.md` (cited as `plan:N`) and the five files in
`2026-10-10-lean-pass-cutover-prompts/`. Context: the "Second fold" section of the fold record and
the fold verification read. Reader: Opus 5.5, 2026-10-10, with no part in either fold. Unchanged
text was not re-reviewed. Probes ran in `/tmp/claude-1000/final-verify/`. No repo file other than
this one was written.

**Counts:** 0 blocker, 3 major, 8 minor.

## Majors

### F-M1. The rollback fails, and discards edits, when the main checkout is dirty: the 1b-stop case

- **Where:** plan:806-820 (S1-T14 rollback, the `||` fallback at :815-818); the cause sits in
  `1b.txt:8-11` and plan:55-58 (a stop writes `docs/STATUS.md` and waits; nothing commits it).
- **Defect:** the full rollback is Geoff's remedy after 1b stops, and 1b's stop leaves an
  uncommitted `docs/STATUS.md` (the failure and the question) in `~/.dotfiles`. A 1b stopped inside
  S1-T15 may also leave an uncommitted `ROADMAP.md`. `git revert` then refuses ("Your local changes
  ... would be overwritten"). The fallback runs anyway, because `||` fires on any revert failure. On
  a path with no conflict, `git checkout --ours` restores the index version, which silently discards
  the uncommitted edit. `revert --continue` then fails with "no cherry-pick or revert in progress",
  and the chain stops. Nothing is rolled back: the clock-stop hook and its link stay live. A second
  hazard follows the same shape. A post-merge commit that touches any other file the merge changed
  (a Geoff session editing `settings.json`, say) conflicts outside the two named files. The chain
  then stops mid-revert in the live checkout. The live `~/.claude/settings.json` holds conflict
  markers, and `~/.local/bin/claude-clock-stop` dangles. Every running session reloads that
  settings file (M16).
- **Evidence:** a scratch repo shaped like the real one: a bare origin; a stowed `bin` package; a
  `lean-cutover` branch that adds `claude-clock-stop` and changes `cairn-run-gate`, `settings.json`,
  `STATUS`, and `ROADMAP` lines 17, 47, and 52; a `--no-ff` merge made by the stubbed `gh pr merge`;
  then the merge block, run as written. Then the rollback block, extracted verbatim from plan:814-819:
  - R1 (S1-T15 and S1-T18 committed and pushed), R2 (ROADMAP conflicts too), R3 (no later commit),
    and R5 (S1-T15 committed, unpushed) completed with exit 0. In each, `git diff --stat <pre-merge>
    -- bin claude` was empty, no link dangled, and `origin/main` equaled `HEAD`.
  - R7 (push rejected) left the revert committed locally, restowed, with no dangling link. So the
    chain restows before it pushes, as claimed.
  - R4 (S1-T15 committed; an uncommitted stop line appended to STATUS) exited 128 after printing
    `error: Your local changes to the following files would be overwritten by merge:
    docs/STATUS.md` and then `error: no cherry-pick or revert in progress`. Afterward the stop line
    was gone, `git status --short` was empty, `settings.json` and `bin` still differed from the
    pre-merge state, and the `claude-clock-stop` link was live.
  - R6 (a later commit edits the `settings.json` hook) exited 128 with `UU
    claude/.claude/settings.json`, a revert in progress, and one dangling link.

  V-M2's replay ran only on clean trees, so it could not see R4.
- **Fix:** commit any uncommitted stop note first, and build the revert in a scratch worktree. The
  live checkout then moves only by a fast-forward to a finished revert commit. This form passed R1,
  R4 (stop note kept, tree rolled back, exit 0), and R6 (live tree untouched, scratch worktree left
  for Geoff):

  ```bash
  M=$(gh pr view lean-cutover -R glw907/workstation --json mergeCommit -q .mergeCommit.oid) &&
  { git -C ~/.dotfiles diff --quiet HEAD -- docs/STATUS.md ROADMAP.md ||
    git -C ~/.dotfiles commit -q -m "Record the 1b stop before the rollback" -- docs/STATUS.md ROADMAP.md; } &&
  R=$(mktemp -d)/rollback && git -C ~/.dotfiles worktree add -q --detach "$R" HEAD &&
  { git -C "$R" revert -m 1 --no-edit "$M" || {
      git -C "$R" rev-parse -q --verify REVERT_HEAD >/dev/null &&
      git -C "$R" checkout --ours -- docs/STATUS.md ROADMAP.md &&
      git -C "$R" add docs/STATUS.md ROADMAP.md &&
      GIT_EDITOR=true git -C "$R" revert --continue; }; } &&
  git -C ~/.dotfiles merge -q --ff-only "$(git -C "$R" rev-parse HEAD)" &&
  git -C ~/.dotfiles worktree remove "$R" &&
  cd ~/.dotfiles && stow -R bin && git push origin main
  ```

  A shorter form also passed R1 to R5: the same note-commit guard, then the current recipe run in
  `~/.dotfiles` with the `REVERT_HEAD` test added to the fallback. It does not cover R6.

### F-M2. S1-T17b's cleanup calls `claude rm` on a session whose commit is unpushed by design, which the docs say refuses

- **Where:** plan:897-898 (cleanup order), with the acceptance at :901-905 and the stop rule in
  `1b.txt:8-11`.
- **Defect:** the probe's prompt says "do not push", so its commit is unpushed. The cleanup then runs
  `claude stop <id>`, `claude rm <id>`, `git worktree remove --force`, and `git branch -D`. A
  `claude rm` on such a session refuses and keeps the session and the worktree. Under the 1b prompt
  ("If a check or probe fails ... stop"), that refusal is likely a stop on the path that gates the
  launch of steps 2 and 4. That stop costs an attended event and the R-D launch. A session that
  improvises with the printed `--discard-unpushed` value removes the worktree and its branch. The
  plan's next two commands then fail on missing targets. The failure path also names no cleanup, so a
  failed probe can leave a session, a worktree, and a `worktree-*` branch in the live `~/.dotfiles`.
  A pushed branch, which "do not push" should prevent, would also stay on `glw907/workstation`.
- **Evidence:** agent-view, "What deleting a session removes": "When you delete a session whose
  worktree has commits that Claude Code can't confirm are saved elsewhere, Claude Code keeps the
  worktree and the session, and the message names the worktree's branch and how many commits are
  unpushed." And: "A worktree git no longer recognizes, for example after `git worktree prune`,
  doesn't block the delete." `claude rm --help` (2.1.296): `--discard-unpushed
  <commit>@<worktree-id>` "also discard the worktree's unpushed commits ... pass the value a previous
  'claude rm <id>' reported". A smaller timing point: `claude agents --json` prints "active sessions",
  and `--all` "also include[s] completed background sessions". The acceptance's "listed
  `lean-rd-probe` while it ran" then depends on 1b sampling before the probe completes, and the
  15-minute poll checks only git.
- **Fix:** reorder the cleanup: `claude stop <id>`; `git worktree remove --force <probe worktree>`;
  `git branch -D <branch>`; then `claude rm <id>`, which no longer refuses once git has dropped the
  worktree. Say that the cleanup also runs before a failure stop, and that it deletes a remote branch
  if `git ls-remote` shows one. Take the "listed while it ran" evidence in the launch's own Bash
  call, or read it from `claude agents --json --all`.

### F-M3. `pass-core`'s launch branches from local `HEAD` with no freshness check; the fold guarded only this cutover's launches

- **Where:** plan:448-456 (S1-T5, "Execute"), against plan:945-948 and the launch blocks at
  plan:958-961 and :1320-1323.
- **Defect:** S1-T4 sets `worktree.baseRef: "head"` globally (plan:424). Under R-D, every future pass
  starts a `--bg` session in the main checkout, and its `EnterWorktree` branches from that checkout's
  local `HEAD`. The fold saw the hazard and guarded steps 2 and 4: "Steps 2 and 4 assert that the main
  checkout's `HEAD` equals `origin/main` after a fetch, since `"head"` branches from local `HEAD`". It
  did not carry the guard into `pass-core`, the text every later pass runs. The bd7525d launch blocks
  branched each worktree from `origin/main` after a fetch, and R-D's text replaced that. Under the
  lean close, Geoff merges each PR on GitHub, so a main checkout is routinely behind until someone
  pulls. A site repo pushes no plan commit to `main` (a push redeploys, risk review F4), so no
  rejected push exposes the lag. The next pass then builds and gates on a stale base, or on whatever
  branch the main checkout holds.
- **Evidence:** the `EnterWorktree` schema in this harness: "The base ref is governed by the
  `worktree.baseRef` setting: `fresh` (default) branches from origin/<default-branch>; `head`
  branches from your current local HEAD". The spec names no fetch or pull step (grep for `fetch`,
  `pull`, and `origin/main` in the spec finds only the `baseRef` rows).
- **Fix:** S1-T5's "Execute" adds that the planning session first runs `git -C <repo> fetch origin`
  and asserts that the main checkout is on its default branch and not behind (`git -C <repo> rev-list
  --count HEAD..origin/<default>` prints 0), with commits ahead only its own. Add an acceptance grep
  for `origin/` in that section.

## Minors

- **F-m1. The git-ownership grep misses most plausible phrasings, and skips the instruction files
  that later `--bg` passes load.** plan:479-487 (S1-T5), plan:638 (S1-T9). Of nine test sentences,
  the regex caught three ("You handle committing ...", "Leave git to Geoff.", "Commit only when
  asked."). It missed "Geoff commits and pushes the branch.", "The user pushes the branch after
  review.", "Do not commit unless Geoff asks.", "Don't push until Geoff approves.", "Geoff owns git on
  this repo.", and "Let Geoff commit." agent-view says the rule applies when "the task, `CLAUDE.md`,
  or memory says you handle committing or pushing yourself". S2-T1 rewrites cairn's `CLAUDE.md`, and
  step 3 rewrites the site `CLAUDE.md` and `.claude/rules` files. Future `--bg` passes load both sets,
  and neither acceptance runs the grep. **Fix:** append
  `|(user|Geoff) (commits|pushes|owns git)|(do not|don.t|never) (commit|push)[a-z]* (unless|until|without)|let (the user|Geoff) (commit|push)`
  to the pattern. It caught all nine samples. It printed nothing over HEAD's `pass-core`, the five
  prompts, the global `CLAUDE.md`, cairn-cms `CLAUDE.md`, every site's `CLAUDE.md` and
  `.claude/rules`, and the cairn-cms, dotfiles, and site memory directories. It does not flag "Geoff
  merges the PR" or "The session commits without asking". Run it in S2-T1's acceptance and in step
  3's grep list too.
- **F-m2. S1-T17b never exercises a `--bg` session's stop channel.** plan:887-911. Every stop in
  steps 2 and 4, the clock stop included, ends in `notify-send -u normal` (plan:55-58). agent-view
  promises a background session only "the `PATH` of the shell you dispatched it from" plus provider
  variables, and it notifies on its own only "While agent view is open". `~/.claude/jobs/` holds no
  past job, so S1-T17b is this machine's first `--bg` run. **Fix:** the probe prompt also asks the
  session to run `notify-send -u normal "lean cutover: rd probe"` and write its exit status into
  `rd-probe.txt`. The acceptance reads `0` there.
- **F-m3. The `.claude/worktrees/` ignore lands after the first worktree exists.** plan:452-453
  ("added by the plan's first task where missing"). The launch's first act is `EnterWorktree`, so the
  main checkout holds `.claude/worktrees/<name>` before any task runs. The line then lands on the pass
  branch and reaches the main checkout only after the merge. For the whole first pass in each of the
  five site repos, `git status` in the main checkout shows the worktree untracked. That is the state
  S1-T6's stated purpose rules out ("so pair-subagent worktrees under the main checkout stay
  untracked"), and it trips any cleanliness check such as S1-T1's. Committing the line to a site's
  `main` would redeploy (F4). **Fix:** the planning session appends `.claude/worktrees/` to
  `.git/info/exclude` before the launch wherever neither file covers it. cairn-cms already works this
  way (`.git/info/exclude:11`).
- **F-m4. Step 3's clock files outlive their tasks.** plan:1093-1097 and pass-core's "removed at the
  close" (plan:457-461). Each task writes its clock file in its own worktree's git dir, and only S3-T9
  removes the files. S3-T1's file (20-minute estimate) stays in dubplate or cairn-pub. The P1, P2,
  and P3 post-return files stay in one worktree of each pair. S3-T5's and S3-T7's subagents enter
  dubplate, and S3-T9 visits all six worktrees. The hook fires on any tool call whose `cwd` resolves
  to a git dir holding a file past twice its estimate (S1-T4), so a stale file yields a spurious stop
  for a finished task. **Fix:** "A task's end, and a pair's return after its overrun check, removes
  its clock file."
- **F-m5. S1-T18's launches are not idempotent on a resume.** plan:918-925. If launch 4 fails after
  launch 2 started, S1-T18's acceptance fails. A resumed 1b restarts at S1-T18 and runs launch 2
  again, starting a second session on cairn-cms. **Fix:** each launch block first skips when
  `claude agents --json` already lists its `--name`.
- **F-m6. The idempotent tag skips the push along with the creation.** plan:795-797. A resume after
  a failed `git push origin pre-lean-process` finds the tag at `M^1`, skips both commands, and fails
  the `git ls-remote` acceptance. The Bash tool keeps no shell state between calls, so a bare `M^1` in
  a later call is empty. **Fix:** "Create the tag unless it exists at `M^1`; push it unless `git
  ls-remote origin refs/tags/pre-lean-process` prints that sha; re-derive `M` in each Bash call."
- **F-m7. The `--bg` resume line starts the process inside an existing worktree (unprobed).**
  plan:49-51. "Resumes in its own worktree with `claude --bg --resume <session-id>`" can place the new
  process inside an existing worktree, the case agent-view says "still asks before committing". In
  the background, that ask stalls with no notice. The documented path for a stopped or idle
  background session is attach: "the next time you attach or reply, the session resumes where it
  left off". **Fix:** name `claude attach <name>` first. Where `--bg --resume` is needed, run it from
  the repo's main checkout.
- **F-m8. `pass-core` has no launch for a pass that continues an existing branch, and the next
  action is one.** plan:448-456 against plan:1421-1423. Pass B's WIP `dbdc4556` sits in
  `.claude/worktrees/engine-pre-2b-b`. A `--bg` session started there asks before committing (M2),
  and the R-D launch makes a new branch. **Fix:** S1-T5's "Execute" adds that such a pass launches the
  same way, and its first task merges or cherry-picks the existing branch into the new one.

## The six questions

1. **Rollback recipe.** On a clean tree, the single chain runs to completion, restows before it
   pushes, and leaves `bin` and `settings.json` at the pre-merge state: R1, R2, R3, R5, and R7. It
   fails in R4 (F-M1), the dirty-tree case that a 1b stop produces.
2. **Merge, step 3, and launch blocks.** Every block passes `bash -n`. An unreplaced `<HEAD_SHA>` is
   a syntax error (`unexpected token '&&'`), so nothing runs. Neither a placeholder nor any other
   quoting leaves bash waiting. `! pgrep` is safe from history expansion, since `!` precedes a space.
   Stub results:
   - Merge block: a clean run merged once and launched 1b in `~/.dotfiles`. A listed session, a
     `pgrep` hit, an untracked file, and a `main` ahead of origin each stopped it before `gh`. A
     missing `claude-clock-stop` stopped it after the pull and before the launch.
   - Step 3 block: an `AHEAD` line stopped it before any worktree. A failed `worktree add`, `npm
     ci`, fetch, or dubplate `worktree add` stopped it before the launch.
   - Launch 2 and launch 4: a failed fetch or `HEAD` unequal to `origin/main` stopped each before
     `claude --bg`, and a clean run launched in `~/Projects/cairn-cms` and `~/.dotfiles`.

   A partly failed step 3 run leaves the worktrees it made, so a re-paste stops at the first
   `worktree add` until Geoff removes them. That recovery is manual, and it does no harm.
3. **Prompt files.** All five are ASCII, with no `$` and no CR. Each reached the stub byte-for-byte
   through its plan launch line, less the trailing newline that `$(...)` strips. Each names its
   plan path, its branch or its `EnterWorktree` name, and its `glw907/<repo>` push grants. 1a
   carries the spec-overrides line. 1b grants the tag push, the `main` push, and the two `--bg`
   launches. None of the five, and none of the planned `pass-core` text, says the user handles
   commits or pushes. The grep's coverage gap is F-m1.
4. **R-D.** The agent-view quotes in M2 match the page, fetched today:
   - Self-isolation: "When you dispatch a background session from agent view or start one with
     `claude --bg`, the session starts in your working directory. Before editing files, Claude moves
     the session into an isolated git worktree under `.claude/worktrees/`".
   - Commit without asking: "Commit and push: Claude commits without asking, and pushes the branch
     when the repository has a remote"; "Never: pushing to `main` or `master`, force-pushing, and
     merging"; "Your git instructions take precedence: if the task, `CLAUDE.md`, or memory says you
     handle committing or pushing yourself, Claude leaves git to you."
   - The ask case: "A session editing a checkout it didn't isolate itself still asks before
     committing or switching branches. This applies when isolation is set to "none", when the
     worktree move failed, or when the session started inside a worktree that already existed."
   - Trust: "Where no dialog can appear, such as in a script, the command exits with a `Workspace not
     trusted` error instead." `~/.claude.json` trusts `~/.dotfiles`, `~/Projects`, and
     `~/Projects/cairn-cms`.

   The `.gitignore` line reaches dotfiles through the merge (S1-T6). cairn-cms ignores
   `.claude/worktrees/` through `.git/info/exclude`. No `lean-cutover` or `docs-chain-audit`
   worktree or branch exists to collide with. The probe cannot pass vacuously. A session that never
   isolates writes into the shared checkout, which the `git status --short` check catches, or it asks
   and never commits, which the deadline catches. The probe never tests the stop channel (F-m2). Its
   cleanup hits a documented refusal (F-M2).
5. **Merge sha and tag.** `gh pr view --help` (2.102.0) lists `[<number> | <url> | <branch>]`,
   `-R`, `--json` with the `mergeCommit` field, and `-q, --jq`. A branch-name lookup of a merged PR
   works: `gh pr view gate-economy -R glw907/cairn-cms --json mergeCommit -q .mergeCommit.oid`
   printed `4cdb593b...`, and an unknown branch exits 1. `glw907/workstation` has no PR yet, so
   `lean-cutover` cannot match an older one. The tag's resume edge is F-m6.
6. **Contradictions.** F-M3 and F-m8 sit between the new `pass-core` text and the rest of the plan.
   The clock sums hold: 680 + 510 + 590 + 210 = 1,990. Optional wording only: plan:288 still says
   "both probes pass" where three now gate step 1, and cairn-pass's worktree field (plan:502) says
   `.claude/worktrees/<branch>` where the other two adapters now say `<name>`.
