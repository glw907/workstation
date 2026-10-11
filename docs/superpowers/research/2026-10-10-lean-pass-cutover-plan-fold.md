# Lean pass cutover plan: fold record

Target: `docs/superpowers/plans/2026-10-10-lean-pass-cutover.md`, revised in place from `a0cdfd5`.
Reviews: `2026-10-10-lean-pass-cutover-plan-review-{contract,mechanics,risk}.md` beside this file.
IDs: `C-` contract, `X-` mechanics, `R-` risk. 52 findings in 37 roots. Owner rulings R-A, R-B, and
R-C (Geoff, 2026-10-10) are applied, not reopened.

## What the fold verified before acting

Each mechanism the revision states was read or probed on 2026-10-10:

- **Ahead state (R-A).** `git status -sb` in dotfiles, cairn-cms, dubplate, ecxc-ski, 907-life,
  aksailingclub-org, xcathletes-org, and cairn-pub shows each default branch level with `origin`.
- **The `--bg` prompt.** In the 2.1.296 binary strings (`/tmp/claude-1000/mech-review/strings.txt`),
  function `bBo` returns the background-session section only when `CLAUDE_CODE_SESSION_KIND ===
  "bg"`. It says "Before making any code changes, use the EnterWorktree tool ... unless your cwd is
  already under `.claude/worktrees/`" and "If you didn't enter the worktree yourself this job, or
  you're in the user's own checkout, ask before committing or switching branches." The agent-view
  page confirms the ask: "A session editing a checkout it didn't isolate itself still asks before
  committing ... when the session started inside a worktree that already existed." The page's only
  in-place switch is `worktree.bgIsolation: "none"`, and the same sentence says the ask still applies
  then.
- **Interactive launch.** `claude --help`: "starts an interactive session by default", positional
  `prompt`, `-n, --name`. `claude agents --json` printed this session with `kind: "interactive"`,
  `cwd`, and `name`. permission-modes page: `defaultMode: "auto"` applies from
  `~/.claude/settings.json` (set at `:11`); auto allows "Pushing to any branch of the repository
  you're working in"; "The classifier trusts your working directory and the remotes that were
  configured for it when the session started"; it blocks "pushing to a third-party repository, unless
  you named that external target" and "Merging a pull request no human has approved". Writes under
  `.claude` and `.git` are protected paths, "Routed to the classifier" in auto mode.
  `~/.claude.json` has `hasSeenAutoModeOutsideReadPrompt: true`.
- **Reload and cwd.** settings page: "Claude Code watches your settings files and reloads them when
  they change ... including edits to `permissions`, `hooks`"; `model` and `effortLevel` load only at
  start. memory page: CLAUDE.md and auto memory "are loaded at the start of every conversation".
  Binary function `Eor` resets the shell cwd after a `cd` outside the allowed directories ("Shell cwd
  was reset to ..."); the subagent prompt says "Agent threads always have their cwd reset between
  bash calls".
- **`gate-tier.mjs --fast`.** In cairn-cms, `node scripts/checks/gate-tier.mjs --fast --range
  HEAD~3..HEAD` printed the default targeted tier (`npm run package && npm run check:close ...`) and
  exited 0. `parseArgs` (`:635-656`) has no `--fast` case.
- **`cairn-run-gate`.** A run starts only when no `pidfile` exists (`:240`); otherwise the call
  reattaches. The heavy lock is `flock "$gatedir/machine.lock"` (`:270`) with
  `gatedir="${TMPDIR:-/tmp}/cairn-gate-$(id -u)"` (`:232`). The wait loop calls `sleep "$poll_s"` by
  name (`:332`).
- **dubplate `--base`.** `scripts/check.sh:142-144` (usage: "any other value runs the full form"),
  `:274-276` (a full 40-hex id only), and `:300-302` (a branch defaults to `git merge-base master
  HEAD`). dubplate `scripts/checks/gate-tier.mjs:2` reads "The pass-execute shim", and only
  `CLAUDE.md:251` and dated plans name it.
- **`auth-data` globs.** `git ls-files -- '<glob>'` matched tracked files for every cairn-cms,
  aksailingclub-org, xcathletes-org, and cairn-pub glob the risk lens listed, for each site's
  `src/hooks.server.ts`, `src/routes/admin/**`, and `wrangler.*`, for dubplate's seven paths, and for
  dotfiles' `bash/.bashrc`, `secrets/**`, `scripts/secrets/**`, and the nine named helpers in
  `bin/.local/bin/`.
- **Sweep reach.** `scripts/check-claude-refs.py` scans only `claude/.claude` (`:93-109`).
  `skills/go-ship/SKILL.md` carries `disable-model-invocation: true`. `code-simplifier` appears in
  skills only in `go-ship`, `pass-core`, and `site-pass/plan-template.md`; `cairn-release` names
  HISTORY 5 times. `actionlint` is not installed. `git pull -h` lists `--[no-]autostash`.

## Dispositions

| Root | IDs | Disposition | Where |
|---|---|---|---|
| 1. Unpushed default branches | X-B1, X-M3, R-F1 | Owner ruling R-A: resolved by Geoff's pushes. Kept a pre-launch ahead-0 assertion for every touched repo, the frozen dotfiles `main`, and the same assertion in each step's pre-launch block. R-F1's dubplate fork is moot under R-A. | Pre-launch 1a step 2; pre-launch 2, 3, 4; "Steps 2 to 4" |
| 2. `--bg` leaves the pass branch | X-M1 | Folded. Every session runs interactive under auto mode, launched by Geoff. X-M1's fallback (`--bg` with worktrees under `.claude/worktrees/`) refused: the commit ask stays, by the docs' own sentence. | Header; M1, M2; S1-T5 "Execute"; Spec gaps |
| 3. 1a lacks the dubplate grant | C-M3, R-F6, X-m1 | Folded: the 1a prompt grants S1-T2's commit and push and names `glw907/dubplate`; every prompt names its `glw907/<repo>` targets. R-F6's `--no-autostash` is superseded: a rejected push is now a stop, with no pull or rebase. | 1a prompt; Conventions "Pushes"; S1-T2 |
| 4. One-executor rule stops on stale trees | X-M2, R-F2, R-F11, C-m7 (re-run part) | Folded at the root: S1-T1 runs pre-launch with Geoff present, under a live-session-and-age rule limited to the main checkouts the plan commits on. Later checks are a `diff --quiet` on the files a task commits, which replaces the S1-T14 and S1-T17 re-runs. No task touches another session's file. | S1-T1; Conventions "One-executor rule"; S1-T2; S1-T15 |
| 5. Step 3's clock stop is inert | C-M2, X-M5, R-F7 | Folded: the session `cd`s into each task's worktree (the `cd` holds under `~/Projects`) and writes the file there; a pair writes one file; the stop cannot fire during a pair. R-F7's S3-T1 hook check refused: S1-T17 already proves the hook, and the `cd` rule fixes the cwd. | Step 3 "Clock stop"; launch prompt 3; S1-T5 "Clock stop" |
| 6. Pair probe passes without `baseRef` | C-M1 | Folded: S1-T15's dotfiles ROADMAP commit stays local, and S1-T16 asserts the merge base equals it and differs from `origin/main`. | S1-T15, S1-T16 |
| 7. `--fast` silently accepted | X-M6 | Folded: unknown flags exit 2; cases assert `--fast` output carries neither `npm run package` nor `check:close`; the step 2 pair gates on the pre-S2-T3 string. | S2-T3; launch prompt 2 |
| 8. S2-T3 never runs its own lane | C-M4 | Folded: each printed line runs through `cairn-run-gate` to `gate exit: 0`, and a case proves a failing leg fails line 1. | S2-T3 acceptance |
| 9. Protected-path CI wait | C-M5 | Folded: the wait leaves `cairn-pass` (no catch record; a red still stops the line, spec Execution item 4). S2-T4 merges into S2-T3. | S1-T6; S2-T2; S2-T3 |
| 10. Who launches steps 2 to 4 | C-M6, C-m9 (session ids) | Folded by the spec: it names the planning session with `claude --bg`. Under root 2 no session can open an interactive one, so Geoff launches all three in one sitting after S1-T18. C-M6's fold (1c launches with `--bg`) refused for root 2's reason. The `--name` is the recorded handle. | "Steps 2 to 4"; S1-T18; Spec gaps |
| 11. Step 4 on the critical path | C-M7 | Owner ruling R-C: steps 2, 3, and 4 launch together; the heavy lock serializes heavy legs. | Header estimate; "Steps 2 to 4" |
| 12. `defer` defers the caller's own run | X-M7 | Folded: `defer` applies only to a call that would start a run; a reattach never defers; `--fresh` mid-run reattaches. One test case added. | S1-T3 item 5 and acceptance |
| 13. Clock probe cwd resets | X-M4 | Folded: the probe worktree moves to `~/.dotfiles/.claude/worktrees/clock-probe`, inside the session's working directory. | S1-T17 |
| 14. 1b and 1c split | X-m8, X-o2, X-m2 | Folded: Geoff merges in his terminal (the spec's Close has him merge, and auto mode blocks an unapproved merge). One post-merge session 1b loads the merged `CLAUDE.md` fresh and runs the tag, filing, and probes. The tag lands on `HEAD^1` after the merge. | Merge block; S1-T14 to S1-T18; Spec gaps |
| 15. 1c auto-reverts | R-F3 | Folded: 1b stops and notifies on any failure; the trigger names `claude-clock-stop`; rollback is Geoff's call, with the one-entry settings removal as the smaller remedy. | 1b prompt; S1-T14 rollback |
| 16. Rollback | R-F10, R-F9 | Folded: the revert names the merge sha S1-T18 records, clears persisted gate state (keeping lock files, listed first), restarts sessions, and notes the revert of the revert. | S1-T14 rollback |
| 17. ROADMAP pushes redeploy sites | R-F4 | Owner ruling R-B: ecxc-ski, 907-life, xcathletes-org, and cairn-pub file in their step 3 PRs; dotfiles and dubplate file in step 1. Recorded as a departure from spec Rollout step 1. | S1-T2; S1-T15; S3-T1, S3-T2, S3-T3, S3-T6; Spec gaps |
| 18. `auth-data` maps are prose | R-F5, R-F15 | Folded: real globs for cairn-cms, each site, dotfiles, and dubplate, each verified to match tracked files, with a glob-match acceptance. R-F5's fixed probe list refused: every probe path sits inside a verified glob. | S1-T6; S3-T7 |
| 19. dubplate `--base origin/master` | C-m1 | Folded: no `--base`; the branch default is the merge base. | Step 3 "Gates"; S3-T1; S3-T5; S3-T7 |
| 20. Reviewer bar unchecked | C-m2 | Folded: acceptance greps `auth-data` and `coverage gap` in `diff-reviewer.md`. | S1-T8 |
| 21. Sweep misses two concepts | C-m3 | Folded: a `code-simplifier` listing and a `cairn-release` HISTORY grep; `go-ship` named as on-request. | S1-T12 |
| 22. Harvest estimates starved | C-m4 | Folded: S2-T5 and S3-T8 at 180 minutes. | S2-T5; S3-T8 |
| 23. Harvest tables bloat the PR | C-m5, R-F14 | Folded: counts first, owed and dropped rows by heading and index, the full table in `<details>`. | Conventions "PR body"; S2-T5; S3-T3, S3-T4, S3-T8 |
| 24. Pass B start gate | C-m6 | Folded: pass B starts once steps 1 and 2 merge (spec Rollout step 5). | S1-T18; S2-T6; Next action |
| 25. Repeated checks | C-m7 (other parts), X-o1 | Folded: the S1-T17 re-run goes (root 4); S3-T1's site baselines go; a step 3 task runs its fast lane only when its diff leaves `*.md` and `.claude/**`. Refused: folding S1-T18 into S1-T17, since STATUS must follow the probes and the ROADMAP commit must precede them. | S3-T1; step 3 "Gates" |
| 26. `dotfiles-pass` outside the scan | C-m8 | Folded: the S1-T12 greps cover `.claude/skills`; the scanner gap is stated and accepted. | S1-T12 |
| 27. Small unverifiables | C-m9 | Folded: the close review checks the `update_snapshots` path (no `actionlint`); the pair runs "from the branch head". | S2-T2; launch prompt 2 |
| 28. Cross-repo pair shape | X-m3 | Folded: no `isolation`, `cd <worktree> && ...` per call; departure recorded. | Step 3 "Pairs"; Spec gaps |
| 29. `baseRef` is machine-wide | X-m4 | Folded: one line in `claude-tooling.md`. Its hazard is gone under R-A. | S1-T10 |
| 30. Resume after a clock stop | X-m5 | Folded: a resume rewrites `start=` or `estimate=`. | S1-T5 "Clock stop" |
| 31. Slow-poll test method | X-m6 | Folded: a PATH-shimmed `sleep` under a small `CAIRN_GATE_WAIT`. | S1-T3 acceptance |
| 32. Peak measurement polls | X-m7, R-F12 | Folded: it runs under the heavy `machine.lock`, so it queues and runs beside no heavy gate; the `pgrep` precondition goes. | S2-T3 |
| 33. S2-T2 setup cost | X-o3 | Folded: S2-T2's subagent skips setup. | Launch prompt 2 |
| 34. 1a runaway guard | R-F8 | Refused: a commit-time self-check misses a loop that never commits, and the spec rules step 1 out of the clock stop. | None |
| 35. Friction from steps 3 and 4 | R-F13 | Folded: steps 1, 3, and 4 list friction as owed in the PR body. | Conventions "Scope" |
| 36. Guarded hook command | R-F16 | Refused: the merge block runs with no live session and pulls, restows, and checks in one line, so no session sees the window. | None |
| 37. dubplate runner shim | R-out-of-lens | Folded: S3-T5 deletes `scripts/checks/gate-tier.mjs` and its `CLAUDE.md:251` line. | S3-T5 |

Counts by ID: 45 folded (6 of them with a refused part), 2 refused, 5 owner rulings (R-A 3, R-B 1,
R-C 1).

## Open for Geoff

- **Future passes now cost one launch paste each.** Root 2 moves every executing session to an
  interactive launch, and S1-T5 writes that into `pass-core`. No session can open an interactive
  session, so Geoff pastes the STATUS launch line once per pass, outside ruling 4's two touchpoints.
  The alternative is `claude --bg` from a worktree under `<repo>/.claude/worktrees/` with a written
  git grant; the docs say such a session "still asks before committing", and a background ask
  notifies only while agent view is open. Recommendation: accept the paste, as the plan now reads.

## Measures

- Plan lines: 1,266 before, 1,400 after. The growth is the merge block and post-merge tasks, the
  explicit `auth-data` globs, cairn-pub's step 3 branch (R-B), the rollback, and M16; S2-T4's merge
  into S2-T3 and the 1b and 1c merge cut some of it.
- Total estimate: 1,850 task-minutes before, 1,970 after (the harvests' +120, S2-T3's checks, step
  3's sixth repo; less the S1-T1 re-runs, the site baselines, and one CI wait).
- Wall clock: 1,260 minutes before, 1,120 after (R-C's concurrent launch, with step 3 now binding).
- New mechanisms: 14 folded, each quoted or probed above (interactive launch, terminal merge block,
  post-merge tag, ahead-0 assertion, per-call `cd`, clock-probe path, `flock` peak measurement,
  `gate-tier` unknown-flag rejection, `defer` reattach, the `sleep` shim, rollback state clear,
  dubplate's base-free scope, the `auth-data` globs, the scratch merge worktree). 5 refused (R-F16's
  wrapper, R-F8's self-timed check, C-M6's `--bg` launcher, X-M1's `--bg` fallback, R-F6's
  `--no-autostash`).

## Second fold

Input: `2026-10-10-lean-pass-cutover-plan-fold-verification.md` (3 major, 8 minor) and Geoff's
ruling R-D (2026-10-10), with the coordinator's R-D addendum. Probes ran in `/tmp/claude-1000/rd-fold/`.

**What this fold verified before acting:**

- **agent-view, "How file edits are isolated"** (fetched 2026-10-10): a `claude --bg` session "starts
  in your working directory. Before editing files, Claude moves the session into an isolated git
  worktree under `.claude/worktrees/`"; it "commits without asking, and pushes the branch"; "Your git
  instructions take precedence: if the task, `CLAUDE.md`, or memory says you handle committing or
  pushing yourself, Claude leaves git to you"; before the move it "can't use the `Edit`, `Write`, or
  `NotebookEdit` tools on the shared checkout". The page also says "Agent view is in research preview."
- **Changelog.** The verification's v2.1.198 quote is not verbatim. The row reads "Background agents
  launched from `claude agents` now commit, push, and open a draft PR when they finish code work in a
  worktree, instead of stopping to ask". The plan cites v2.1.221 instead: "Changed background
  sessions to commit and push to preserve work, open a draft PR only when the task calls for one,
  follow your CLAUDE.md git instructions".
- **Trust.** The permissions page: a scripted `claude --bg` in an untrusted directory "exits with a
  `Workspace not trusted` error", and trust "covers the whole repository apart from any git repository
  nested inside it". `~/.claude.json` trusts `~/.dotfiles` and `~/Projects/cairn-cms`, not a fresh
  scratch repo.
- **`EnterWorktree`** (harness schema): "creates a new git worktree inside `.claude/worktrees/` on a
  new branch"; `"head"` "branches from your current local HEAD".
- **Quoting.** A stub `claude` received a backticked, double-quoted, `$`-bearing prompt intact through
  `"$(cat ~/<file>)"`, with the tilde expanded.
- **Gating.** The step 3 block, run with shimmed `git`, `npm`, and `claude`, launched on a clean run,
  stopped before any worktree on an `AHEAD` line, and stopped before launch on a failed worktree add.
- **Rollback.** Replayed in two scratch repos (STATUS and ROADMAP both conflicting; STATUS alone):
  the chained recipe committed the revert, and `git diff --stat pre -- bin settings.json` was empty.
- **Other probes.** `gh pr view <n> --json mergeCommit -q .mergeCommit.oid` printed a sha on a merged
  cairn-cms PR. `git ls-files` matched 0 files for `**/preview/[token]/**` and 4 for the escaped form.
  `cairn-run-gate:247` reads `lane="${CAIRN_GATE_LANE:-heavy}"`. `.claude/worktrees/` is ignored in
  cairn-cms and dubplate only.

**Dispositions:**

| ID | Disposition | Where |
|---|---|---|
| V-M1 | Folded: five prompt files in `2026-10-10-lean-pass-cutover-prompts/`, each launched as `"$(cat <file>)"`; the inline prompts became pointers; S1-T5's "Launch prompt" section prescribes the file form. | Header; pre-launch 1a; merge block; launches 2, 3, 4; S1-T5 |
| V-M2 | Folded, one deviation: the verification's two lines ran the restow and push even when `revert --continue` failed, so the recipe is now one `&&` chain. It restows before it pushes, and it is clean only before any step 2 to 4 PR merges. | S1-T14 rollback |
| V-M3 | Settled by R-D (below). The open item is closed. | M2; S1-T5; Spec gaps |
| V-m1 | Folded: the glob is now `**/preview/\[token\]/**`. | S1-T6 |
| V-m2 | Folded: the merge block and the step 3 block chain every line behind their checks with `&&`; the merge check compares `claude agents --json` to `[]`. `<HEAD_SHA>` replaces a placeholder whose apostrophe would leave bash waiting for a closing quote. | Merge block; "Steps 2 to 4"; launches 2, 3, 4 |
| V-m3 | Folded: S2-T2's subagent neither runs setup nor gates locally. | Prompt 2 |
| V-m4 | Folded: cairn-pass lifts a leading `CAIRN_GATE_LANE=<lane>` onto the `cairn-run-gate` call, and S2-T3's acceptance runs each line that way. | S1-T6; S2-T3 |
| V-m5 | Folded: no clock file while a step 3 pair runs; it is written when the pair returns, with `start=` the dispatch time. S1-T5's sentence now says "isolated pair worktrees". | Step 3 "Clock stop"; prompt 3; S1-T5 |
| V-m6 | Folded: S1-T17 says the stop line is the expected result. | S1-T17 |
| V-m7 | Folded: S1-T14 derives `M` from `gh pr view lean-cutover --json mergeCommit` first, which a resumed 1b re-derives, and tags only if the tag is absent. S1-T18 and the rollback use `M`. | S1-T14; S1-T18 |
| V-m8 | Folded: each peak measurement runs as a background Bash task. | S2-T3 |
| R-D | Applied. S1-T5 writes the launch into `pass-core`: the planning session runs `claude --bg` from the main checkout, the session calls `EnterWorktree` and runs the setup in the new worktree, and its PR comes from the branch it creates. A plan's first task adds `.claude/worktrees/` to `.gitignore` where missing; five site repos lack it today. S1-T6's site and dotfiles worktree fields follow. Spec gaps records the departure from Execution item 1, the research-preview status, the probe gate, and the paste fallback. New S1-T17b probes the launch live (20 minutes). It deviates on one point: it runs in trusted `~/.dotfiles`, not a scratch repo, since a fresh scratch repo is an untrusted nested repo and a scripted `--bg` there exits `Workspace not trusted`; the prompt says "do not push", so nothing reaches a remote. On failure 1b stops, and the paste fallback is Geoff's call. | M2; S1-T5; S1-T6; S1-T17b; S1-T18; Spec gaps |
| R-D addendum | Applied: S1-T5's acceptance runs a git-ownership grep over `pass-core` and every prompt file, and S1-T9's runs it over the global `CLAUDE.md`. Both print nothing at HEAD today. | S1-T5; S1-T9 |

**Which steps launch how:**

- 1a: interactive, pasted by Geoff. It works in a linked worktree before `.claude/worktrees/` is
  ignored or `baseRef` is set.
- 1b: interactive, pasted in the merge block. It commits on `main` in the main checkout.
- Step 2: `claude --bg`, started by 1b in S1-T18 from `~/Projects/cairn-cms`. Nothing in S2-T1 to
  S2-T6 needs an existing worktree.
- Step 3: interactive, pasted by Geoff. It starts in `~/Projects`, which is no repository, over six
  existing worktrees.
- Step 4: `claude --bg`, started by 1b in S1-T18 from `~/.dotfiles`. Nothing in S4-T1 to S4-T4
  needs an existing worktree.
- Steps 2 and 4 first assert that the main checkout's `HEAD` equals `origin/main`, since `"head"`
  branches from local `HEAD`.

**Measures:** plan 1,400 lines before, 1,423 after. Total estimate 1,990 task-minutes (S1-T17b adds
20). Wall clock is about 1,140 minutes.
