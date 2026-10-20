# Lean pass cutover plan: failure-risk lens review

Target: `docs/superpowers/plans/2026-10-10-lean-pass-cutover.md` at `ec14c1e`. Lens: failure risk for a
`runner` pass with the `live-account` flag. Every claim below was read or probed on 2026-10-10; no repo
file was edited.

**Counts:** 1 blocker, 6 major, 9 minor. Two are owner forks (F1's dubplate push, F4's deploys).

## What holds (verified, no finding)

- **Live tree before the merge.** No task edits the `~/.dotfiles` main checkout before S1-T14 except the
  plan commit. S1-T2's dubplate STATUS commit is the spec's own requirement (spec:197-198).
- **Stow window.** `~/.claude/{agents,docs,skills,workflows,tooling,instructions}` are directory links
  (`agents -> ../.dotfiles/claude/.claude/agents`), so files added or deleted under `claude/.claude` resolve
  with no restow. Only `bin` is per-file, and S1-T14 runs `pull && stow -R bin && command -v` as one
  command, so the settings never name an unstowed hook across a tool call.
- **Rollback of the links.** `stow -R` prunes a link to a deleted file. Probed with GNU Stow 2.4.1 in the
  scratchpad: after deleting `b` from the package, `stow -R` removed the dangling `b` link. Rolling back
  therefore cleans up `~/.local/bin/claude-clock-stop`.
- **Merge mechanics.** `glw907/workstation` allows merge commits (`"mergeCommitAllowed":true`), has no branch
  protection and no rulesets. The S1-T14 acceptance (`HEAD^1 == pre-lean-process`) catches a tag on the
  wrong commit.
- **Lost rules.** No rule that protects an unattended run loses its executing home. The `claude-awake-touch`
  hooks (`settings.json:56,114,126,138`) stay untouched. The memory caps execute inside `cairn-run-gate`
  (`:248-250`), and the OOM narrative lives in `bluefin-admin.md`, which no task deletes (the only
  `oom-defense` references are `bluefin-admin.md` and the ratchet baseline). The battery, lid, wake-up, and
  restart rules (UG-2 to UG-9) stay in the trimmed guards doc. A spot check of `pass-gate-economy.md`
  (PG-1 to PG-17 against its 15 bullets) and of `model-economy.md` "Current state" found every rule placed
  or deleted by name.
- **Shared gate lock.** `TMPDIR` is empty in sessions, so `gatedir` resolves to the shared
  `/tmp/cairn-gate-1000` and steps 2 to 4 really do share one heavy lock. The S1-T3 tests isolate `TMPDIR`
  (`tests/cairn-run-gate.test.sh:20`), so they never hold the real machine lock.

## Blocker

### F1. Five default branches are ahead of origin, and the plan assumes they are not

- **Where.** `plan:252-253`, `:318-319`, `:692`, `:822`, `:988`, `:992`, `:945`.
- **Defect.** The plan bases steps 2 and 3 on `origin/<default>` and requires local `main` to equal
  `origin/main` at the merge. It never pushes or names the unpushed local commits:

  ```
  ~/.dotfiles   ## main...origin/main [ahead 9]      (spec, plan, fold, catch ledger, 7b40996 ...)
  cairn-cms     ## main...origin/main [ahead 3]      (dea73f7d "Point STATUS at the workstation lean pass process")
  ecxc-ski      ## main...origin/main [ahead 3]      (2026-09-12 docs commits)
  907-life      ## main...origin/main [ahead 3]      (8c2fbc7 rewrites docs/STATUS.md and docs/HISTORY.md)
  dubplate      ## master...origin/master [ahead 33] (gate scope pass code: check.sh --base, the gate-tier shim, the dependency sweep)
  ```

  Each gap has its own consequence:

  1. **Session 1b stops.** S1-T14 checks that "the local `main` equals `origin/main`". Nothing pushes the
     9-plus dotfiles commits, so 1b stops before it merges. If someone pushes by hand instead, the tag
     lands on a commit without the spec. A `revert -m 1` would then also delete the spec and plan, since
     they arrived through the merge.
  2. **Step 2 starts from a base without the block it must correct.** S2-T6 corrects cairn's "Next action
     (lean pass process)" block, but `git grep 'lean pass process' origin/main -- docs/STATUS.md` finds
     nothing. The block exists only in unpushed `dea73f7d`. Once the PR merges, local `main` conflicts with
     it on `docs/STATUS.md`.
  3. **S1-T2 publishes another session's work.** S1-T2 runs `git -C ~/Projects/dubplate push origin master`,
     which pushes all 33 local commits, including code (`bfd33c5`, `ac479ea`, `2af4404`). The plan never
     names that push. It is irreversible without a force-push, and the 1a launch prompt does not cover it
     (see F6).
  4. **Step 3's site bases depend on S1-T17's pushes, and nothing says so.** The bases are correct only
     because S1-T17's ROADMAP pushes also carry the 3 local commits each in ecxc-ski and 907-life. If
     S1-T17 changes (see F4), step 3 branches from stale bases. 907-life's `8c2fbc7` rewrites the same
     STATUS and HISTORY files that S3-T3 edits.
- **Proposed fold.**
  - Add one pre-launch step that runs before 1a. It lists `git rev-list --count @{u}..HEAD` for every
    touched repo, then pushes `~/.dotfiles` `main` (no CI, public repo) and cairn-cms `main`. The cairn push
    runs only CI: `publish.yml` triggers on `release` and `workflow_dispatch`.
  - Make the dubplate push an explicit decision before launch (**OWNER FORK**, below).
  - Add one assertion to the pre-launch blocks for steps 2 and 3: each repo shows `ahead 0` before
    `worktree add`.
  - Add the ahead count as a column in the S1-T1 table.
  - Freeze dotfiles `main` from the 1a worktree creation until S1-T14. A rule landed on `main` by any other
    session during the 11-plus hours conflicts with the rewrites of `CLAUDE.md` and `pass-core`.
- **OWNER FORK (dubplate's 33 commits).**
  - (a) Geoff pushes them before 1a launches. The STATUS says "Master's full gate is green at `f0a2056`".
  - (b) Step 3 bases dubplate on local `master`, and S1-T2 commits without pushing.

  **Recommendation: (a).** Step 3's PR needs a remote base that contains this work, and a deliberate push
  costs one attended minute now, against a silent push buried inside S1-T2.

## Major

### F2. The S1-T1 decision rule stops on stale trees that exist today, so step 1 halts at minute 15

- **Where.** `plan:299-302` (rule), `:295-298` (expected state), re-run at `:691` and `:771`.
- **Defect.** The rule stops on any uncommitted change that is not agent memory or untracked notes, or
  whose newest mtime is newer than the repo's last commit. Today it stops in two repos.
  - **cairn-cms:** four abandoned worktrees carry real edits:
    - `docs-reset-dryrun`: `M docs/admin/dryrun-is-it-working.md` (2026-09-23)
    - `gate-tier-tool`: `M package-lock.json` (2026-09-20)
    - `polish-11b-i` and `polish-11b-ii`: untracked e2e specs (2026-09-13)
  - **dubplate:** `reports/Pi 5 stereo client proven build.md` has mtime 15:27, newer than the last commit
    (`a690718`, 14:45). The untracked `docs/superpowers/research/2026-09-04-*.md` files are not "notes"
    either.

  The plan's "expected" line names only the agent-memory files. The same rule makes S1-T14 never clear,
  so 1b stops as well. The test against the last commit also weakens over time: once S1-T2 commits in
  dubplate, any file written before that commit passes later re-checks.
- **Proposed fold.**
  - Record a snapshot at plan commit time: the path and mtime of every uncommitted file in every main
    checkout and linked worktree.
  - Rewrite the rule. A row is clear when its uncommitted set is a subset of the snapshot, with unchanged
    mtimes, and no session's cwd is in the repo. Anything new or changed is a stop.
  - Pre-record the four cairn worktrees and dubplate's untracked set in the snapshot.
- **Price.** This removes two certain attended events (the 1a stop and the 1b stop) at no cost to safety.

### F3. Session 1c may revert and push `main` on its own, on a loose trigger

- **Where.** `plan:723-726`, `:705-706`.
- **Defect.** The 1c prompt reads: "If the clock-stop hook misfires (a stop line with no clock file, or a
  visible hook error on tool calls), apply S1-T14's rollback at once". A Sonnet session would then revert
  the whole cutover and push `main` without Geoff.
  - "A visible hook error" also matches `vale-hook`, `tellgrader --hook`, or `claude-context-budget`, all of
    which share the PostToolUse list (`settings.json:85-106`).
  - The harm is out of proportion. A misfiring clock-stop hook emits an advisory line, and a hook error is
    non-blocking. A full revert swaps the instruction surface machine-wide again.
  - The rollback command itself is fragile: `revert -m 1 HEAD` names `HEAD`, which stops being the merge
    commit as soon as S1-T17 or S1-T18 commits (see F10).
- **Proposed fold.**
  - On a misfire, 1c stops and notifies; it does not roll back.
  - The proportionate first remedy is Geoff's call: drop the one PostToolUse entry for `claude-clock-stop`,
    or revert the whole merge.
  - Narrow the trigger to output that names `claude-clock-stop`.

### F4. S1-T17's ROADMAP pushes redeploy four production sites

- **Where.** `plan:766-778`.
- **Defect.** S1-T17 commits and pushes to the default branches of ecxc-ski, 907-life, cairn-pub, and
  xcathletes-org:
  - The first three run `deploy.yml` on `push: branches: [main]` with no paths filter, ending in
    `npx wrangler deploy`.
  - xcathletes-org has Workers Builds connected to `main` (52 builds, the latest on commit `959643a`).

  So a ROADMAP edit redeploys four production sites. ecxc-ski and 907-life also ship their 3 unpushed local
  commits. The task's risk line says only `live-account`; no person expects a ROADMAP item to redeploy
  production.
- **Proposed fold (OWNER FORK).**
  - (a) Keep S1-T17 in step 1 and put `[skip ci]` in each commit subject. GitHub Actions honors it on push.
    That skips the three Actions deploys. It is unverified for Workers Builds, so xcathletes still builds
    (my search found no Workers Builds support for a commit-message skip, only build watch paths).
  - (b) Carry each step 3 repo's ROADMAP item inside its step 3 PR. Geoff's merge then deploys once, as
    expected, and only dotfiles (no CI) and cairn-pub (with `[skip ci]`) are pushed in 1c. This departs from
    the spec's "Step 1 also files" (spec:207-208).

  **Recommendation: (b).** It removes three unnecessary deploys and a race with step 3's base. If Geoff
  wants the spec's letter, take (a) and accept one unchanged-code xcathletes build.

### F5. Steps 2 and 3 leave auth and session paths out of the `auth-data` map

- **Where.** `plan:437-438` (cairn-pass), `:442-448` (site-pass), and the S1-T6 acceptance at `:467-471`.
- **Defect.** Under the lean process a task's class comes from the adapter's path map, and the close review
  re-derives it. The same map decides whether the auth e2e specs, the per-task Opus read, and the
  `RUN_GATE_IF_BUSY=defer` ban apply.
  - **cairn-pass:** the map is the prose "auth, signing, sessions, D1, the commit path", which an executing
    Sonnet must interpret. cairn has no existing glob list to inherit: `gate-table.json` `protected` lists
    only gate files, and `authData` is a spec list keyed by the plan-declared class.
  - **site-pass:** the outcome gives the site table no risk-map content at all. The acceptance checks only
    that the bold label exists, so an empty field passes.
  - The real surfaces exist:
    - cairn: `src/lib/{auth,auth-channel,auth-crypto,auth-store,github}/**`,
      `src/lib/sveltekit/{csrf,csrf-required-page,auth-routes,auth-error-codes,commit-log}.ts`,
      `src/lib/admin/{csrf-context.ts,CsrfField.svelte}`, `migrations*/**`,
      `examples/showcase/migrations*/**`, `templates/*/migrations*/**`, `**/hooks.server.ts`,
      `**/preview/[token]/**`, `**/members/login/**`, `**/admin/signups/**`, `tool/internal/secrets/**`,
      `packages/create-cairn-site/src/{github,cloudflare}/**`, and `wrangler.*`.
    - aksailingclub-org: `src/member-auth/**`, `src/member-signup/**`, `src/admin-club/**`, `migrations/**`,
      and `data/membershipworks/**` (member PII).
    - xcathletes-org: `src/lib/server/{auth,db}/**`, `src/routes/team/{login,tokens}/**`, and
      `migrations*/**`.
    - cairn-pub: `src/routes/admin/signups/**` and `migrations/**`.
- **Proposed fold.**
  - S1-T6 writes each map as explicit globs, starting from the lists above.
  - Each site row gets its own `auth-data` globs.
  - Acceptance adds: every glob matches at least one tracked file (`git -C <repo> ls-files '<glob>'` is
    non-empty), and a fixed probe list maps to `auth-data`: `src/lib/github/signing.ts`,
    `src/lib/auth-crypto/index.ts`, and `migrations/` in cairn, plus `src/member-auth/` in aksailingclub-org.

### F6. The 1a launch prompt does not approve S1-T2's commit and push on dubplate `master`

- **Where.** `plan:282-284`, `:317-319`.
- **Defect.** The prompt grants "standing approval to commit on `lean-cutover` ... and to push `lean-cutover`
  ... never push `main`". S1-T2 commits on dubplate `master` and pushes it. That falls outside the grant,
  and only the branch name dodges the prohibition. M2 says a session editing a checkout it did not isolate
  "still asks before committing", so the background session asks and blocks. The auto-mode classifier may
  also refuse a push to another repo's default branch.
- **Proposed fold.** Grant it in writing: "and, for S1-T2 only, to commit `docs/STATUS.md` alone on dubplate
  `master` and push it". This presumes F1's fork is settled as (a). Add `--no-autostash` to S1-T2's
  rebase-retry: today the retry refuses safely, because the tracked `MEMORY.md` is dirty and no autostash is
  configured, but a global setting could change that.

### F7. Step 3's clock stop never fires

- **Where.** `plan:959-964`, `:994`.
- **Defect.** Step 3 launches in `~/Projects`, which is not a git repository. The hook resolves the git dir
  from the hook input's `cwd` (M6). The plan never tells the session to `cd` into a task's worktree, and
  `git -C` calls leave `cwd` at `~/Projects`. So every check runs against a non-git directory and stays
  silent by design (`plan:371-372`). The spec's clock stop (spec:137-143; ruling 13) is lost for the
  longest step, 530 task-minutes with a 198-bullet harvest.
- **Proposed fold.** Step 3's launch prompt says: at each task's start, `cd` into that task's worktree and
  write `pass-task-clock` into its git dir; a pair task writes it in the session's current worktree. S3-T1
  quotes one silent hook check from inside a worktree to confirm the hook can see the file.

## Minor

### F8. Step 1a runs 11 unattended hours with no runaway guard

- **Where.** `plan:244-245`.
- **Defect.** The spec rules out the clock-stop hook for step 1, and UG-1's guard covers workflows only.
  Nothing bounds a looping 1a session, for example in S1-T12's grep-to-zero against the ratchet.
- **Fold.** Add one prompt line, which does not contradict the spec's reason: "at each commit, compare
  `date` against the task's start; past twice its clock estimate, take the stop".

### F9. The persisted gate results can feed a false green to the old script after a rollback

- **Where.** `plan:330-333` and the S1-T14 rollback.
- **Defect.** S1-T3 keeps the status and pid files in `/tmp/cairn-gate-1000/<key>`. The reverted script
  skips the start when `$pidfile` exists (`cairn-run-gate:240`) and prints the stored status. So after a
  rollback, the first call per PWD and gate string can print an old result for a changed tree.
- **Fold.** The rollback adds: clear the state directories under `/tmp/cairn-gate-$(id -u)/`, keeping the
  `*.lock` files.

### F10. The rollback names `HEAD` and does not say what it leaves behind

- **Where.** `plan:705-706`.
- **Defect.** `revert -m 1 HEAD` fails after S1-T17 or S1-T18 commits, since `HEAD` is then not a merge.
  That failure is safe but makes the rollback unusable. The rollback also leaves several things unsaid:
  live sessions keep the new instructions until they restart; the dubplate STATUS and the ROADMAP commits
  stay, which is fine; and re-landing the cutover later needs a revert of the revert.
- **Fold.** Use `git revert -m 1 <merge sha>`, with the sha recorded in STATUS by S1-T18. Add the F9
  cleanup, "restart every Claude session", and one line on the revert-of-revert.

### F11. S1-T17 can commit another session's ROADMAP edit

- **Where.** `plan:771-773`.
- **Defect.** The acceptance checks that `show --stat HEAD` lists only `ROADMAP.md`. It does not check that
  `ROADMAP.md` was clean before the edit.
- **Fold.** Run `git diff --quiet HEAD -- ROADMAP.md` before the edit, and treat a failure as a stop.

### F12. The "no other gate running" precondition in S2-T4 fights the concurrency the plan recommends

- **Where.** `plan:900-901`.
- **Defect.** With steps 3 and 4 running, `pgrep -af cairn-run-gate` is rarely empty, so S2-T4 waits and can
  trip its own clock stop. The `Memory peak` of a `systemd-run` unit is that unit's own peak, so other
  gates barely affect it.
- **Fold.** Drop the precondition, or require only that no heavy gate is running.
- **Price.** It avoids a likely clock-stop event, about 10 to 40 minutes of waiting.

### F13. Friction from steps 3 and 4 has no destination

- **Where.** `plan:55-56`.
- **Defect.** The rewritten `site-pass` (DC-19) may carry the rule to file cairn friction in cairn-cms. The
  step 3 and step 4 prompts forbid writing cairn-cms. The executing session meets the conflict.
- **Fold.** Add to the Conventions: friction found in steps 3 and 4 goes to the PR body as owed to cairn's
  friction log.

### F14. A harvest table could exceed GitHub's PR body limit

- **Where.** `plan:917-921`, `:1132-1135`.
- **Defect.** GitHub caps a PR body at 65,536 characters. dubplate's rediscover sections hold at least 139
  top-level bullets, about 12,000 characters of first lines alone. A table that quotes the bullets, plus
  the score and inventory sections, can make `gh pr create` fail at the close. It also costs Geoff an
  attended read of 150 to 200 rows.
- **Fold.** Rows cite the heading and bullet index, never quote the text. The body leads with counts per
  disposition and lists only the "owed" and "dropped" rows. The full table goes in a collapsed
  `<details>` block.

### F15. The adapter maps for dubplate and dotfiles are incomplete

- **Where.** `plan:1116` (dubplate) and `:456-457` (dotfiles).
- **Defect.**
  - dubplate: "the serve and JWT surface" omits `internal/auth/**`, `internal/engine/store/migrations/**`,
    `cmd/dubplate-server/**`, `web/src/routes/{login,members}/**`, and `systemd/**`.
  - dotfiles: the map should name the PreToolUse security guards `claude-block-op`, `claude-secret-guard`,
    and `claude-tierguard`, plus `claude-askpass`, `claude-sudo-*`, `secret-receive`,
    `fastmail-*password`, and `bash/.bashrc` (which sources the secrets).
- **Fold.** List these by name in S3-T7 and S1-T6.

### F16. Optional: a guarded hook command removes the stow window entirely

- **Where.** `plan:375-377`.
- **Defect.** None today. S1-T14's one-command pull and stow already closes the window.
- **Fold.** Register the hook as `sh -c 'command -v claude-clock-stop >/dev/null && exec claude-clock-stop || true'`.
  The PATH timing then no longer matters, either at the merge or on a machine that pulls without
  restowing.

## Over-ceremony

Little is excess. The pair and clock-stop probes (40 minutes) and the re-run one-executor checks are cheap
insurance on a `live-account` cutover. The real cost of the plan is attended events it never priced, all
of which the folds above remove:

- F2: two certain stops.
- F1: one certain stop at 1b.
- F6: a likely approval prompt.
- F12: a likely clock stop.
- F14: Geoff reading about 350 harvest rows across the step 2 and step 3 PRs.

## Out of lens, noted once

dubplate `scripts/checks/gate-tier.mjs` names `pass-execute` (`git grep -l pass-execute master`). The step 3
grep never scans `scripts/`, so the reference survives the sweep.

Sources: [Workers Builds troubleshooting](https://developers.cloudflare.com/workers/ci-cd/builds/troubleshoot/),
[Workers Builds docs](https://codex-container-api-docs.previews.developers.cloudflare.com/workers/ci-cd/builds/index.md).
