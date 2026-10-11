# Lean pass cutover plan review: mechanics and feasibility

Lens: mechanics and feasibility. Target: `docs/superpowers/plans/2026-10-10-lean-pass-cutover.md` at
`ec14c1e`. Reviewer: Opus 5.5, 2026-10-10. Every claim below cites a doc page fetched today, the
Claude Code 2.1.296 binary (`strings` of
`/var/home/linuxbrew/.linuxbrew/Caskroom/claude-code@latest/2.1.296/claude`), or a probe run today.
Probes ran read-only against the repos, with scratch output in `/tmp/claude-1000/mech-review/`.

Counts: 1 blocker, 7 major, 8 minor, 3 optional (over-ceremony).

## Answers to the seven flagged items

1. **Unattended commit approval.** A written grant very likely clears the ask, but the launch
   still risks a derail, for a different reason. Use an interactive launch. Details in M1.
2. **Live settings reload.** Yes. Hooks and most settings reach a running session without a
   restart. Details in m9.
3. **`worktree.baseRef: "head"` machine-wide.** Acceptable. Its one hazard comes from unpushed
   local default branches, which M3 removes. Details in m4.
4. **Cross-repo pairs.** Feasible, and no conflict in substance with spec Execution item 2. The
   plan owes the dispatch shape. Details in m7.
5. **Hook and gate fixes.** Buildable, with two correctness gaps (M7, m5) and one test method left
   unspecified (m6). The acceptance checks run as written.
6. **Pre-launch commands.** The commands work, apart from the unpushed `main` (B1). Only
   `stow -R bin` is needed. Details in "Stow" below.
7. **Concurrency.** Memory and disk fit. Two refinements: measure under the lock (m8) and spare
   the heavy lane (o1).

## Blocker

### B1. Local `main` is 9 commits ahead of `origin/main`, so S1-T14 cannot pass

- **Where:** plan:250-253 (pre-launch 1a commits the plan on `main`, never pushes),
  plan:257 (`worktree add ... -b lean-cutover main`), plan:692-693 (S1-T14 requires "the local
  `main` equals `origin/main`"), plan:705-706 (rollback).
- **Defect:** the branch is cut from local `main`, which carries 9 unpushed commits. S1-T14's
  equality check fails, so session 1b stops before merging, by its own prompt (plan:686-687).
  The rollback is also broken: if someone worked around the check by tagging `origin/main`,
  `revert -m 1` would restore a tree that lacks the 9 commits. Those commits include live
  tooling (`claude/.claude/skills/pass-core/SKILL.md`, `claude/.claude/docs/pass-gate-economy.md`,
  `bluefin/bootstrap.sh`), not only the spec and the plan.
- **Evidence:** `git ls-remote origin refs/heads/main` returns `444edf27…`;
  `git rev-list --count origin/main..main` prints `9`;
  `git diff --name-only origin/main..main | grep -v '^docs/'` lists the three tooling files.
- **Fold:** pre-launch 1a step 1 becomes: commit the plan and its review records, then
  `git -C ~/.dotfiles push origin main`. Step 2 adds the check
  `test "$(git -C ~/.dotfiles rev-list --count origin/main..main)" = 0`.

## Major

### M1. The `--bg` system prompt tells 1a and step 4 to isolate themselves (item 1)

- **Where:** plan:23, 28 (1a and step 4 run `claude --bg` in `~/Projects/.worktrees/...`);
  plan:262-267, 1167-1173; plan:81-88 (M2); plan:1256-1259 ("Spec gaps"); S1-T5 "Execute"
  (plan:399-402) bakes `claude --bg` into `pass-core`.
- **Defect:** the "ask before committing" rule is model-level text in the background-session
  system prompt. It is not a permission gate. The same prompt also tells the model to call
  `EnterWorktree` unless the cwd sits under `.claude/worktrees/`. Neither 1a's worktree nor step
  4's matches that test. A session that obeys calls `EnterWorktree(name)`, which creates
  `.claude/worktrees/<random>` on a new branch. Before the merge, `baseRef` is still `fresh`, so
  that branch starts from `origin/main`. Having entered the worktree itself, the session then
  "commits without asking" and pushes a `worktree-*` branch. The work lands off `lean-cutover`,
  and `gh pr view lean-cutover` (plan:665) fails. Step 3 runs from a non-git directory, so the
  call fails and the session continues in place. Step 2's worktree is under `.claude/worktrees/`,
  so it passes the test.
- **Evidence (binary, function `bBo`, gated on `CLAUDE_CODE_SESSION_KIND === "bg"`):**
  - "Before making any code changes, use the EnterWorktree tool ... unless your cwd is already
    under `.claude/worktrees/`, in which case you're already isolated. This is enforced: file
    edits in the shared checkout are rejected until you isolate".
  - "If you made code changes in a worktree you entered, commit before finishing — you don't need
    to ask ... This holds unless the user's instructions, in the task, CLAUDE.md, or memory,
    reserve git for them ... If you didn't enter the worktree yourself this job, or you're in the
    user's own checkout, ask before committing or switching branches."
  - The edit guard itself (`KU`) returns early when the cwd is a linked worktree. The docs and the
    v2.1.251 changelog agree that edits are not rejected. Only the instruction text misdirects.
  - The `EnterWorktree` tool text: "Must not already be in a worktree session" refers to an
    `EnterWorktree` session, not to a cwd inside a linked worktree.
- **Will a written grant suffice?** Probably, for the ask alone. The ask is an instruction, and
  the launch prompt is the user's own message granting standing approval. The agent-view page
  says "Your git instructions take precedence". It never says a grant clears the non-isolated ask
  (WebFetch of `code.claude.com/docs/en/agent-view`). A session that asks anyway sits under
  "Needs input". It notifies only "While agent view is open".
- **Fold (recommended): launch every executing session interactive in auto mode, in the
  worktree:** `claude --model sonnet --effort medium --name lean-step1a "<prompt>"`, in its own
  Ptyxis tab, for 1a, 2, 3, and 4. Evidence that this launch will not stall:
  - An interactive session gets no background-session section, so neither instruction appears.
  - `~/.claude/settings.json:11` sets `"defaultMode": "auto"`, and auto applies from user settings
    (permission-modes, "Which mode a session starts in").
  - Auto mode allows by default "Pushing to any branch of the repository you're working in" and a
    pull request "that matches your request" (permission-modes, "Allowed by default").
  - The one-time prompt for a read outside the working directories is already answered:
    `~/.claude.json` carries `hasSeenAutoModeOutsideReadPrompt: true`, with no
    `blockReadsOutsideWorkingDirectories` set.
  - `claude agents --json` still lists interactive sessions, and `claude-notify` covers idle
    prompts.
  - Cost: the tab must stay open.

  Record this in "Spec gaps" as a departure from spec Execution item 1 (spec:111-118), and write
  the interactive line into S1-T5's "Execute" and "Launch prompt" sections.
- **Fallback, if `--bg` must stay:** create 1a's and step 4's worktrees at
  `~/.dotfiles/.claude/worktrees/<branch>`. First add `.claude/worktrees/` to
  `~/.dotfiles/.git/info/exclude` (pre-launch), since S1-T6's `.gitignore` line lands later.
  Keep the written grant.

### M2. S1-T1's decision rule stops 1a at its first task on today's state

- **Where:** plan:295-302.
- **Defect:** the exception admits only "agent memory or untracked notes" whose newest mtime is
  older than the repo's last commit. Today's state fails it in five places, so the rule forces a
  stop on weeks-old abandoned leftovers. The planning prediction (plan:295-298) names only
  dubplate's agent memory.
- **Evidence:** `git status --short` over every worktree of the nine repos:

  | Repo | Worktree | Uncommitted change | Newest mtime | Last commit |
  |---|---|---|---|---|
  | cairn-cms | `docs-reset-dryrun` | 4 tracked docs and facts files | 09-23 | 10-10 15:47 |
  | cairn-cms | `gate-tier-tool` | tracked `package-lock.json` | 09-20 | 10-10 15:47 |
  | cairn-cms | `polish-11b-i`, `polish-11b-ii` | untracked e2e `.spec.ts` files | 09-13 | 10-10 15:47 |
  | dubplate | main checkout | untracked `reports/Pi 5 stereo client proven build.md` | 10-10 15:27 | 10-10 14:45 |

- **Fold:** key the rule on liveness and contention, not on file class:
  - A row is a stop when a live session's cwd is in the repo.
  - A row is also a stop when an uncommitted file is under 24 hours old and lies in a path this
    plan writes.
  - Otherwise record the row "stale, not staged".

  Move S1-T1 into pre-launch 1a, run by the planning session with Geoff present, so a stop costs
  no relaunch.

### M3. Four other repos carry unpushed default-branch commits that steps 2 and 3 branch around

- **Where:** plan:821-822 and 987-992 (branch from `origin/main` or `origin/master`); plan:944-945
  (S2-T6 corrects cairn STATUS's "Next action (lean pass process)" block); plan:317-319 (S1-T2
  pushes dubplate `master`); plan:772-773 (S1-T17 pushes six default branches).
- **Defect:**

  | Repo | Unpushed commits | Visibility | Effect |
  |---|---|---|---|
  | cairn-cms | 3 | public | `dea73f7d` is the commit that adds the block S2-T6 must correct. A branch from `origin/main` lacks it, so S2-T6 edits a STATUS without the block, and the later push of local `main` conflicts on `docs/STATUS.md`. |
  | 907-life | 3 | public | Includes the STATUS split (292 lines changed), so S3-T3's STATUS rewrite starts from the old file and conflicts later. |
  | ecxc-ski | 3 | public | Branch base is stale. |
  | dubplate | 33 | private | S1-T2's push publishes all 33. |

  S1-T2's push and S1-T17's pushes publish every unpushed commit in their repos. The acceptance
  `show --stat HEAD lists only ROADMAP.md` hides that.
- **Evidence:** `git rev-list --count @{u}..HEAD` per repo; `git grep -n "lean pass process"
  origin/main -- docs/STATUS.md` finds nothing, while the same grep on `main` finds line 42;
  `gh repo view --json visibility`.
- **Fold:** pre-launch 1a, after the one-executor check, pushes each clean default branch that is
  ahead: dotfiles, cairn-cms, ecxc-ski, 907-life, and dubplate. Steps 2 and 3 then branch from an
  `origin` that equals local. **OWNER FORK:** this publishes 9 commits to public `glw907/workstation`
  and 3 each to public cairn-cms, ecxc-ski, and 907-life. Recommendation: push them all up front
  with Geoff's one go. The alternative, branching from local defaults, keeps the PR diffs noisy and
  defers the same push.

### M4. The S1-T16 clock-stop probe cannot see its worktree

- **Where:** plan:749-761.
- **Defect:** session 1c runs in `~/.dotfiles`. Claude Code resets the shell cwd after any `cd`
  outside the allowed working directories. The `cd ~/Projects/.worktrees/dotfiles-clock-probe`
  therefore reverts to `~/.dotfiles`, and the hook's `cwd` never points at the probe's git dir.
  The probe gets no stop line and fails. Session 1c may then read the failure as a broken hook.
- **Evidence:** binary function `Eor`: if the new cwd is outside the allowed directories, it
  resets to the original and returns "Shell cwd was reset to ${se()}". No
  `additionalDirectories` is set (`~/.claude/settings.local.json`, stowed `settings.json`).
- **Fold:** create the probe at `~/.dotfiles/.claude/worktrees/clock-probe`, which S1-T6's
  `.gitignore` line covers. Alternatively, launch 1c with `--add-dir ~/Projects/.worktrees`.

### M5. Step 3's clock stop never fires

- **Where:** plan:957-964 and 1001-1012 (the session runs from `~/Projects`); "Clock stop on"
  (plan:964).
- **Defect:** the hook resolves the git dir from the input `cwd` (spec:137-143).
  - The session's cwd is `~/Projects`, which is not a git repository, so the hook stays silent for
    the whole step: 530 task-minutes.
  - The pair subagents report `~/Projects` too, since "Agent threads always have their cwd reset
    between bash calls" (subagent system prompt in the binary).
  - The plan never says where step 3 writes the task-clock file.
- **Fold:** the step 3 prompt and S1-T5's "Clock stop" section say: the session `cd`s into the
  worktree of the task in flight (inside `~/Projects`, so the `cd` sticks) and writes the file in
  that worktree's git dir. Add one `pass-core` line stating that the stop cannot fire during a pair,
  since the parent session is idle and the subagents' worktrees hold no file (m5).

### M6. S2-T3's acceptance already passes before S2-T3 starts, and the step 2 pair runs the wrong gate

- **Where:** plan:891-894 (acceptance: `gate-tier.mjs --fast --range origin/main..HEAD` prints one
  or two lines); plan:430-432 (S1-T6 writes `--fast` into `cairn-pass`); plan:505-507 (S1-T8 pair
  agents run "the adapter's fast lane"); plan:835-836 and 841-842 (the S2-T1 and S2-T2 pair runs
  before S2-T3).
- **Defect:** `gate-tier.mjs` silently ignores an unknown `--fast`, prints the default targeted
  tier on one line, and exits 0. The acceptance therefore proves nothing. A pair agent that obeys
  its definition runs the full targeted tier (`npm run package && npm run check:close ...`) on the
  heavy lane. That is the same unknown-flag defect S1-T3 fixes in `cairn-run-gate`.
- **Evidence:** in `~/Projects/cairn-cms`,
  `node scripts/checks/gate-tier.mjs --fast --range HEAD~3..HEAD` printed `gate-tier: targeted
  (computed)`, then one line beginning `npm run package && npm run check:close -- ...`, with exit 0.
- **Fold:**
  - S2-T3 adds unknown-flag rejection (exit 2, nothing on stdout).
  - Its unit cases assert that `--fast` output contains neither `npm run package` nor
    `check:close`.
  - The step 2 launch prompt tells the pair's dispatch to pass the pre-S2-T3 gate string
    explicitly.

### M7. `RUN_GATE_IF_BUSY=defer` as specified defers the caller's own running gate

- **Where:** plan:341-345.
- **Defect:** "a heavy-lane gate whose machine lock is held exits 76". A caller that re-issues
  after exit 75 finds the lock held by its own in-flight run. A naive check then exits 76 and
  leaves its own leg to CI. The fix's outcome also leaves `--fresh` unspecified while a run is in
  flight: kill it, reattach, or queue.
- **Evidence:** `cairn-run-gate:244-336`. The lock is taken inside the detached run, and a
  re-issue reattaches through `$pidfile`.
- **Fold:** add two outcome sentences: "defer applies only when this call would start a run; a
  call that reattaches to an in-flight run never defers"; and "`--fresh` with a run in flight
  reattaches; it discards only a finished result". Add one test case: re-issue with `defer` while
  its own heavy run holds the lock, which must reattach, not exit 76.

## Minor

### m1. Step 3's pushes may be judged pushes to external repositories

- **Where:** plan:1003-1012.
- **Evidence:** the auto-mode classifier "trusts your working directory and the remotes that were
  configured for it when the session started". `~/Projects` has no remotes. The block list
  includes "pushing to a third-party repository, unless you named that external target"
  (permission-modes).
- **Fold:** name `glw907/<repo>` for each push and PR target in the step 3 prompt. Name
  `glw907/dubplate` in the 1a prompt for S1-T2, and the six repos in the 1c prompt for S1-T17.

### m2. 1b's merge falls under a default block

- **Where:** plan:679-687.
- **Evidence:** auto mode blocks "Merging a pull request no human has approved" by default. An
  approval clears it only when it names "the action and its specifics" (permission-modes).
- **Fold:** write the 1b prompt's go as "merge PR `lean-cutover` into `main` with `gh pr merge
  --merge`". Session 1b is interactive, so the risk is one prompt.

### m3. The cross-repo pair dispatch shape is missing (item 4)

- **Where:** plan:960-964.
- **Evidence:**
  - The model-visible Agent schema has no `cwd`: binary `GNr()` returns `zo()` or `jn()`, both
    built as `$o().omit({cwd:!0})`.
  - `isolation: "worktree"` from a non-git directory needs `WorktreeCreate` hooks (the
    `EnterWorktree` tool text).
  - Edits inside a linked worktree are allowed for a session and its subagents (agent-view
    changelog, v2.1.251).
- **Fold:** the step 3 prompt says each pair agent works by absolute paths and runs `cd <worktree>
  && ...` in every Bash call. One line under "Spec gaps" records the departure from spec item 2:
  disjoint repos replace worktree isolation, and the merge step does not apply.

### m4. `worktree.baseRef: "head"` applies machine-wide (item 3)

- **Where:** plan:375.
- **Effect:** it changes `claude --worktree`, `EnterWorktree`, agent isolation, and background
  auto-isolation in every repo. Each now branches from local HEAD. With local defaults ahead of
  `origin` (M3), every such branch and PR carries the unpushed commits. A checkout sitting on a
  feature branch seeds that branch's state.
- **Verdict:** acceptable once M3's push lands. Note it in S1-T10's `claude-tooling.md` "Model
  defaults" section.

### m5. Resuming after a clock stop is unspecified

- **Where:** plan:404-405 and 369-371.
- **Defect:** after Geoff says continue, the file still reads over twice the estimate, so every
  later tool call injects the stop line again.
- **Fold:** `pass-core` "Clock stop" says a resume rewrites `start=`, or the `estimate=` Geoff
  names.

### m6. S1-T3's slow-poll test has no stated method

- **Where:** plan:354.
- **Fold:** name the method: a PATH-shimmed `sleep` that sleeps twice its argument, under a small
  `CAIRN_GATE_WAIT`.

### m7. S2-T4's quiet-machine rule polls, and its real reason is RAM safety

- **Where:** plan:900-903.
- **Defect:** `systemd-run ... -P` reports only its own unit's peak, so concurrent gates do not
  skew the number. The measurement runs uncapped and outside `cairn-run-gate`'s lock, though, so
  beside a heavy gate it risks the 2026-09-14 kind of out-of-memory kill.
- **Fold:** run it as `flock "${TMPDIR:-/tmp}/cairn-gate-$(id -u)/machine.lock" systemd-run --user
  --wait -P -d -E PATH="$PATH" bash -c '<line 1>'`. It then queues behind step 3's heavy gates
  instead of polling `pgrep`.

### m8. The 1b and 1c split rests partly on a wrong premise (item 2)

- **Where:** plan:686.
- **Evidence:** "Claude Code watches your settings files and reloads them when they change, so it
  applies most edits to the running session without a restart, including edits to `permissions`,
  `hooks`" (`code.claude.com/docs/en/settings`, "When edits take effect"). From the hooks page:
  "Direct edits to hooks in settings files are normally picked up automatically by the file
  watcher." `model` and `effortLevel` are read only at start.
- **Consequences:** the clock hook and `baseRef` reach every live session the moment `git pull`
  lands. S1-T14 already guards that window: the single Bash command plus the one-executor re-run.
  `CLAUDE.md` still loads only at session start, so a fresh 1c remains the truer test.
- **Fold:** correct the rationale to "1c must load the merged `CLAUDE.md` fresh". See o2.

## Optional (over-ceremony)

- **o1. Step 3's per-task `npm run check` and S3-T1's four baselines** (plan:1014-1026 and each S3
  task's fast lane). The step 3 diffs touch only `.md` and `.claude/**` files, which `svelte-check`
  never reads. S3-T9's local `npm run check && npm test && npm run build` covers each site once.
  These gates run on the heavy lane and queue behind cairn's component legs. Dropping them saves
  about 8 to 10 gate runs, roughly 20 to 40 minutes of lane time, at near-zero catch probability.
  Keep the step 3 grep and the `wc -l` checks as the per-task acceptance.
- **o2. Merge sessions 1b and 1c.** Settings reload live (m8). This saves one Geoff launch, one
  attended event, and a session spin-up. The cost is a probe that relies on the file watcher seeing
  a symlinked `settings.json` change. Keep the split if Geoff values the fresh-session test more.
- **o3. Step 2 pair setup.** Each pair agent runs `npm ci && npm ci --prefix examples/showcase`,
  about 1.2 GB and a few minutes, while S2-T1 edits `CLAUDE.md` and S2-T2 edits CI YAML. Only S2-T1's
  docs gate needs `node_modules`. Let S2-T2's agent skip setup, since its acceptance is CI.

## Stow, and the commands that check out (item 6)

- Only `stow -R bin` is needed.
  - `~/.claude/{agents,docs,skills,workflows,tooling}` are whole-directory links, so files added
    or deleted under them need no restow. `CLAUDE.md` and `settings.json` are per-file links.
  - `stow -n -v -R claude` shows only "reverts previous action" relinks, with no new link.
  - `~/.local/bin` holds per-file links, so the new `claude-clock-stop` needs `stow -R bin`, as
    planned.
  - The rollback's restow after the revert removes the dangling link.
- `git worktree add` creates its parent directories. `~/Projects/.worktrees` exists.
- `~/Projects` and `~/.dotfiles` are trusted in `~/.claude.json`.
- `examples/showcase/package-lock.json` exists, so `npm ci --prefix` works.
- The repo-root `README.md` named in S1-T12's grep exists.
- `jq -e '[...] | index(...)'` exits 0 on a match at index 0, so S1-T4's settings check is sound.
- The S4-T2 journal glob matches 130 files.
- `claude-tooling-sync verify`'s collision check reads `~/Projects/*/.claude/skills`. A new project
  skill named `dotfiles-pass` or `dubplate-pass` collides with no personal skill.

## Concurrency (item 7)

- **RAM:** 15 GiB, with 19 GiB swap (6.8 GiB in use now). One heavy gate (8G max), one light gate
  (3G), and three sessions (about 0.4 GB each by RSS) fit. The heavy lock serializes heavy gates.
  The lock is shared because `TMPDIR` is unset in sessions, so every caller resolves
  `/tmp/cairn-gate-1000`. Claude sets `TMPDIR` only for sandboxed Bash, which is off.
- **Disk:** 30 GB free. Step 2 adds about 3.6 GB (its worktree plus two pair worktrees), and the
  four site installs add 2 to 4 GB.
- **Refinements:** two items need change. m7 puts the peak measurement under the lock. o1 takes
  most of step 3's markdown-only gates off the heavy lane.
