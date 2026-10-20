# Lean pass cutover plan: fold verification read

Target: `docs/superpowers/plans/2026-10-10-lean-pass-cutover.md` at `bd7525d`, against the pre-fold plan
at `ec14c1e`, the fold record, the three lens reviews, and the spec. Reader: Opus 5.5, 2026-10-10, with
no part in the reviews or the fold. Owner rulings R-A, R-B, and R-C are taken as given. Probes ran in
`/tmp/claude-1000/fold-verify/`, and no repo file other than this one was written.

**Counts:** 0 blocker, 3 major, 8 minor.

## Majors

### V-M1. Every launch line mangles its prompt when pasted as written

- **Where:** plan:303, :763, :914, :1096, :1295 (`claude ... --name <n> "<launch prompt below>"`), with the
  prompts at :308-323, :772-782, :919-931, :1105-1116, and :1300-1307; S1-T5 writes the same shape into
  `pass-core` "Execute" and "Launch prompt" (:449-450, :464-465).
- **Defect:** each prompt is full of backticks, and the 1b prompt also carries inner double quotes. Pasted
  between double quotes, bash runs every backticked span as a command substitution and deletes it. The
  sessions lose the plan path, the branch names, and the push grants that root 3 added
  (`glw907/workstation`, `glw907/dubplate`). The 1b prompt also runs
  `notify-send -u normal "lean cutover: 1b stopped"` at paste time. The errors print just before the
  TUI clears the screen. Before the fold, a session issued the launch and could quote it; Geoff now
  pastes it.
- **Evidence:** `quote-probe.sh` passed the 1a grant through the same quoting. It received
  `[You may commit on  and push it to . Read .]` and printed `lean-cutover: command not found` and
  `glw907/workstation: No such file or directory`. The 1b sample ran its inner command and dropped the
  path.
- **Fix:** commit each launch prompt as a file beside the plan, such as
  `docs/superpowers/plans/2026-10-10-lean-pass-cutover.launch/1a.txt`. Each launch line then reads
  `claude --model sonnet --effort medium --name lean-step1a "$(cat <path>)"`. S1-T5's "Launch prompt"
  section prescribes the same file form for every later pass's STATUS line.

### V-M2. The rollback revert conflicts, so it does not run as written

- **Where:** plan:800-807 (S1-T14 rollback); the cause sits in S1-T15 (:813-817) and S1-T18 (:868-873).
- **Defect:** the merge changes `docs/STATUS.md` (S1-T13 item 4) and `ROADMAP.md` (S1-T12's sweep of
  `ROADMAP.md:17,47,52`). After the merge, 1b rewrites `docs/STATUS.md` in S1-T18 and edits `ROADMAP.md` in
  S1-T15. `git revert -m 1 <merge sha>` therefore stops on a conflict in `docs/STATUS.md`, and possibly in
  `ROADMAP.md` too, before its commit. The `&&` chain then skips the push and the restow. The revert has
  already left the live tree mostly rolled back, but it is uncommitted, and the plan gives Geoff no way
  to finish. Without a conflict, a bare `git revert` opens an editor for the message. The chain also
  pushes before it restows, so a rejected push leaves the dangling link.
- **Evidence:** a scratch repo replayed the sequence: base, a cutover branch that changes STATUS,
  ROADMAP, a bin script, and settings, then a `--no-ff` merge, an S1-T15 commit, and an S1-T18 commit.
  `git revert -m 1 --no-edit <merge>` stopped with `UU docs/STATUS.md`. The recipe below then completed
  it, and `git diff --stat pre -- bin settings.json` came back empty.
- **Fix:** replace the rollback line with:

  ```bash
  git -C ~/.dotfiles revert -m 1 --no-edit <merge sha> || {
    git -C ~/.dotfiles checkout --ours -- docs/STATUS.md ROADMAP.md &&
    git -C ~/.dotfiles add docs/STATUS.md ROADMAP.md &&
    GIT_EDITOR=true git -C ~/.dotfiles revert --continue; }
  cd ~/.dotfiles && stow -R bin && git push origin main
  ```

  Add that the full rollback is clean only before any step 2 to 4 PR merges. Those steps land the lean
  process in other repos, and the revert does not touch them.

### V-M3. The fold's open item rests on a wrong premise, and the paste conflicts with ruling 4 and the Success test

- **Where:** plan:1385-1390 (Spec gaps), :884-887, and S1-T5 :449-453, which write "started by Geoff in
  its own terminal tab" into `pass-core`; fold record :104-111.
- **Defect:** the plan and the fold record say "No session can open an interactive one." From that they
  conclude that every future pass costs Geoff a launch paste. The refused alternative they weigh is
  `--bg` inside a pre-made worktree, which does ask before committing. They miss the documented path:
  a `--bg` session started from the repo's main checkout isolates itself, then commits and pushes
  without asking. A session can also open the same interactive launch in a new terminal tab itself. A
  paste on every pass adds an attended event that ruling 4 ("design in chat and the PR") and the
  Success test ("Attended time stays at the design, the PR read, and one event per fired clock stop")
  do not allow. Pass B is scored against that test. Spec gaps records the departure from Execution
  item 1, but not this consequence.
- **Evidence:**
  - agent-view, "How file edits are isolated": "When a background session has made code changes in a
    worktree Claude entered ... **Commit and push**: Claude commits without asking, and pushes the
    branch when the repository has a remote." The ask applies only to "a checkout it didn't isolate
    itself ... when isolation is set to "none", when the worktree move failed, or when the session
    started inside a worktree that already existed." The v2.1.198 changelog row reads: "A background
    session that isolated its work in a worktree commits, pushes its own isolated branch, never `main`
    or `master`, and opens a draft pull request when it finishes instead of asking first."
  - worktrees: a worktree named `<name>` gets "a new branch named `worktree-<name>`".
  - `ptyxis --help-all`: "`--tab` New terminal tab in active window"; "`-d, --working-directory=DIR` Use
    DIR for --tab ... or -x"; "`-x, --execute` Command to execute". Sessions carry `WAYLAND_DISPLAY`,
    `DISPLAY`, and `DBUS_SESSION_BUS_ADDRESS` (probed). A detached tmux session gives its child a TTY:
    the probe printed `/dev/pts/0` and `stdin-stdout-are-tty` from a non-TTY Bash call. Neither path
    was probed with `claude` itself.
- **Fix:** before 1a executes S1-T5, put one batched question to Geoff with three options:
  - (a) A single-repo pass launches as a self-isolating `claude --bg` from the main checkout. The
    session runs the adapter's setup and works on `worktree-<name>`. Under `baseRef: "head"` that branch
    starts from local `HEAD`. A stall shows only while agent view is open.
  - (b) The planning session opens the interactive tab itself:
    `ptyxis --tab -d <worktree> -T <name> -x '<claude line>'`.
  - (c) Keep the paste, and record it in Spec gaps as a departure from ruling 4 and the Success test.

  For (a) or (b), 1b should prove the mechanism live before `pass-core` relies on it, for example by
  having S1-T18 launch steps 2 and 4 that way. 1a, 1b, and step 3's multi-repo session stay interactive
  under every option. 1a's checkout has no `.claude/worktrees/` ignore line until S1-T6, and a `--bg` run
  from `~/Projects` asks before it commits.

## Minors

- **V-m1. One cairn `auth-data` glob fails S1-T6's own acceptance.** plan:496 (`**/preview/[token]/**`),
  acceptance at :537-539; fold record :49-50 says every glob matched. In a git pathspec, `[token]` is a
  character class. `git -C ~/Projects/cairn-cms ls-files -- '**/preview/[token]/**'` prints 0 files,
  while `'**/preview/\[token\]/**'` prints 4. Every other glob in S1-T6 and S3-T7 matched on this read.
  **Fix:** write the glob as `**/preview/\[token\]/**`. A session left to fix the failing check might
  instead drop the preview-token route from the map.
- **V-m2. The checks in the pasted blocks do not gate anything.** plan:758-760 (merge block) and
  :909-915, :1086-1097, :1292-1295 (step 2, 3, and 4 pre-launch); also :898-899. Pasted whole, bash runs
  every line regardless of output. The `AHEAD:` line then scrolls past amid `npm ci` before the TUI
  clears the screen, and `gh pr merge` runs even when `claude agents --json` lists a session. When no
  session runs, `claude agents --json` prints `[]` rather than nothing. **Fix:** chain each block's
  remaining lines with `&&` behind a check that returns non-zero, or tell Geoff to paste the check
  alone and continue only on empty output.
- **V-m3. S2-T2's subagent is told to gate but skips setup.** The launch prompt (:925-927) tells each
  pair subagent to gate with the pre-S2-T3 `gate-tier.mjs` string. S2-T2's subagent skips `npm ci`,
  and S1-T8's implementer definition (:575-576) runs setup and the fast lane. That gate cannot run
  without `node_modules`. **Fix:** say that S2-T2's subagent neither sets up nor gates locally, since
  CI on its commit is its gate (:963-966).
- **V-m4. The `CAIRN_GATE_LANE=light` prefix inside a gate string does nothing.** S2-T3 (:989-990, :999)
  puts the prefix on line 1, and S1-T6 (:485-487) has cairn-pass "run in order" the printed lines.
  `cairn-run-gate:247` reads the lane from its own environment, so
  `cairn-run-gate 'CAIRN_GATE_LANE=light ...'` still takes the heavy lock. The measured lane would then
  be silently lost on every later cairn pass. This text predates the fold, but the fold's new
  acceptance ("each line ... run through `cairn-run-gate`") exercises it. **Fix:** state the contract.
  The caller lifts a leading `CAIRN_GATE_LANE=<lane>` onto the `cairn-run-gate` call, and cairn-pass's
  fast-lane field says so.
- **V-m5. Step 3's pair subagents can receive the clock stop.** plan:1057-1059. The session leaves the
  clock file in the worktree of the pair's first task, and that task's subagent works there. The
  hooks page says: "When a subagent calls a tool, tool events such as `PreToolUse` and `PostToolUse`
  fire the same configured hooks as in the main conversation". It also says `cwd` follows `cd`. So
  "the stop cannot fire while the session waits on a pair" fails for step 3, and a subagent may be
  told to write STATUS and wait. The S1-T5 sentence (:458-459) holds only for isolated pairs. **Fix:**
  hold no clock file while a step 3 pair runs, then write it when the pair returns, with `start=` set to
  the dispatch time.
- **V-m6. S1-T17 never tells 1b that its stop line is expected.** The hook's text (:419-421) tells the
  session to "Write STATUS, run `notify-send -u normal`, and wait for Geoff". 1b's prompt (:777-781)
  stops on a failure, and S1-T17 (:854-860) never says that this stop line is the pass result. **Fix:**
  add one sentence to S1-T17: "The stop line in the probe worktree is the expected result. Quote it and
  continue."
- **V-m7. S1-T14's checks are relative to `HEAD`, which breaks a 1b resume.** plan:786-797, with the
  Resume convention at :44-45. After S1-T15 commits, `HEAD^1` is the merge commit, so a relaunched 1b
  reads S1-T14 as failed. Its retag then errors, because the tag already exists. That failure is safe,
  but it costs a stop. S1-T18 must also recover a merge sha that S1-T14 never wrote down. **Fix:**
  S1-T14 records `git rev-parse HEAD` as the merge sha first, and phrases its checks and the rollback
  on that sha.
- **V-m8. The peak measurement can hit the Bash tool's 600-second cap.** plan:985-988. The `flock` on
  `machine.lock` waits behind step 3's heavy full-suite gates, and the plan runs it outside
  `cairn-run-gate`'s exit-75 protocol. **Fix:** run each measurement as a background Bash task (M7).

## Question 1: did each blocker and major close where the fold says?

Yes. Each one reads closed at its cited location. V-findings note where a closure has a residual gap.

| Root | IDs | Location in `bd7525d` | Verdict |
|---|---|---|---|
| 1 | X-B1, R-F1, X-M3 | Pre-launch 1a step 2 (:277-288); pre-launch 2, 3, 4 (:909, :1087, :1092, :1292); :898-899 | Closed under R-A. The assertion does not gate when pasted (V-m2). |
| 2 | X-M1 | Header :32-34; M1, M2 (:86-105); S1-T5 (:449-453); Spec gaps (:1385-1390) | Closed. The launch quoting breaks (V-M1), and the open item's premise is wrong (V-M3). |
| 3 | C-M3, R-F6 | 1a prompt (:320-322); Pushes (:60-63); S1-T2 (:359-363) | Closed. The grant is backticked, so a paste strips it (V-M1). |
| 4 | X-M2, R-F2 | S1-T1 (:337-341); One-executor rule (:55-59) | Closed. |
| 5 | C-M2, X-M5, R-F7 | Step 3 "Clock stop" (:1057-1059); launch prompt 3 (:1111-1112); S1-T5 (:456-459) | Closed. Subagent exposure remains (V-m5). |
| 6 | C-M1 | S1-T15 (:813-818); S1-T16 (:840-841) | Closed, and the probe discriminates. worktrees: `"fresh"` branches "from the repository's default branch on the remote", and `refs/remotes/origin/HEAD` resolves to `origin/main` here. |
| 7 | X-M6 | S2-T3 (:981-982, :996-998); launch prompt 2 (:925-927) | Closed. |
| 8 | C-M4 | S2-T3 acceptance (:996-1001) | Closed. The lane prefix is a no-op (V-m4). |
| 9 | C-M5 | S1-T6 (:490-492, :539); S2-T2 (:963-964) | Closed. |
| 10 | C-M6 | :884-887; S1-T18 (:868-873); Spec gaps | Refused with a reason. The attended cost needs Geoff's ruling (V-M3). |
| 11 | C-M7 | Header (:15-19); :884 | Closed under R-C. The wall-clock sum checks: step 3's 460 minutes bind. |
| 12 | X-M7 | S1-T3 item 5 (:386-392); acceptance (:404-405) | Closed. |
| 13 | X-M4 | S1-T17 (:850-856) | Closed. The cwd reset is confirmed in the binary (question 4). |
| 15 | R-F3 | 1b prompt (:777-781); rollback (:798-799) | Closed. |
| 17 | R-F4 | S1-T15 (:817-818); S3-T1, T2, T3, T6; Spec gaps (:1379-1384) | Closed under R-B. All six ruling 11 repos file once. |
| 18 | R-F5 | S1-T6 (:492-524, :537-539); S3-T7 (:1234-1236) | Closed, except one glob (V-m1). |

## Question 2: contradictions and build order

- **Within the plan.**
  - The task-minute sums match the header (660, 510, 590, 210; total 1,970).
  - The merge sha, tag, and probe order in 1b builds: S1-T14, S1-T15, S1-T16, S1-T17, S1-T18.
  - The only task contradiction found is V-m3.
  - S1-T10's dead-reference gate may force it to edit `docs/claude-md-archive.md`, which S1-T12 owns.
    The gate demands that edit, and it is harmless.
- **Plan against spec.**
  - The Execution item 1 departure is recorded, but its effect on ruling 4 and the Success test is not
    (V-M3).
  - The R-B departure and the cross-repo pair departure are recorded with reasons.
  - The spec's preamble says the sessions "launch in `~/.dotfiles`", while 1a launches in a linked
    worktree. Spec Rollout step 1 itself says "on a branch in a worktree", so no defect follows.
- **Pre-launch, 1a, merge block, and 1b.**
  - These hand off cleanly. 1a ends at PR-ready, its STATUS names the merge block, the block launches
    1b, and 1b ends at the steps 2 to 4 handoff.
  - An interactive 1a does not exit when it "ends". The block's "no Claude session open anywhere"
    therefore requires Geoff to `/exit` the 1a tab and every unrelated session.

## Question 3: live tree and rollback, command by command

- **Pre-launch 1a.**
  - The assertion loop parses and prints only `AHEAD:` lines. It does not gate (V-m2).
  - `git worktree add ~/Projects/.worktrees/dotfiles-lean-cutover -b lean-cutover main` succeeds: no
    `lean-cutover` branch exists in any of the eight repos, and neither the worktree path nor
    `.worktrees/dotfiles-docs-chain-audit` exists.
  - The `cd` and the gate share one call, which matches the cwd reset.
  - The launch line fails (V-M1).
- **Merge block.**
  - `gh pr merge lean-cutover -R glw907/workstation --merge --match-head-commit <sha>` is valid in gh
    2.102.0. Its help lists `-m, --merge`, `--match-head-commit SHA`, and `-R, --repo`, and takes a
    branch argument. `origin` is `https://github.com/glw907/workstation.git`.
  - `stow -R bin` from `~/.dotfiles` works. `bin` is in `bluefin/stow-packages.txt`, and no `.stowrc`
    exists, so the target is the parent directory (`~`). `stow -n -v -R bin` exits 0, with only
    "reverts previous action" relinks.
  - A scratch stow tree (GNU Stow 2.4.1) showed `-R` linking a new `claude-clock-stop`, then pruning
    it after the file was deleted.
  - The tag goes on `HEAD^1`, the merge commit's first parent and the pre-merge `main`. That is what
    spec Rollout step 1 asks.
- **Rollback.**
  - As written, it stops on a conflict (V-M2).
  - With V-M2's recipe, the live paths match `pre-lean-process` exactly in the replay. The stow links
    match (probed), and so do the `settings.json` hooks and `baseRef` (reverted, and the file watcher
    reloads them). `~/.local/bin` matches once `stow -R` prunes the link. Gate state is cleared, with
    `machine.lock` and `machine-light.lock` kept: they are files, and `-type d` skips them. Run
    records live in `~/.local/state/cairn-run-gate` and are untouched.
  - The rollback leaves the S1-T2 dubplate commit, the tag, the 1a worktree and branch, and anything
    steps 2 to 4 merged elsewhere.
- **Can `settings.json` name a hook that is not on PATH?** Once, at the merge.
  - Between `git pull` and `stow -R bin`, the merged settings name a command with no link. The window
    is sub-second, or open-ended if stow fails, since the `&&` chain then stops before `command -v`.
  - No session runs then, by the block's precondition. The hooks page says "A hook that can't start is
    a non-blocking error too". S1-T14's `readlink` and 1b's hook-error trigger would both catch a
    missing link.
  - The rollback reverses the order: the revert drops the entry first, and the link dangles
    unreferenced until the restow.
  - During 1a, the edited `claude/.claude/settings.json` is a worktree copy. No settings source reads
    it, because project settings load from `.claude/settings.json` in the primary working directory
    (settings page).

## Question 4: unquoted mechanisms, probed

- **Interactive launch line.** `claude --help` (2.1.296) confirms each part:
  - "starts an interactive session by default"
  - positional `prompt` "Your prompt"
  - `-n, --name <name>` "Set a display name for this session"
  - `--model <model>` "Provide an alias ... (e.g. 'fable', 'opus', or 'sonnet')"
  - `--effort <level>` "(low, medium, high, xhigh, max)"

  The flags are sound. The quoting is not (V-M1).
- **Hot reload.** The settings page, "When edits take effect": "Claude Code watches your settings files
  and reloads them when they change, so it applies most edits to the running session without a
  restart, including edits to `permissions`, `hooks`". `model` and `effortLevel` are read "only once,
  at session start". The hooks page adds: "Direct edits to hooks in settings files are normally picked
  up automatically by the file watcher." The plan never depends on the watcher following the symlinked
  `~/.claude/settings.json`: the merge runs with no session open, 1b starts fresh, and the rollback
  restarts every session.
- **The cwd reset.** Binary function `Eor` (from the `strings` dump) holds
  `if(h||r!==s&&!Kg(r,n)){try{sp(s,e)}...}`. When the shell cwd `r` differs from the original `s` and
  lies outside the allowed directories, or when flag `h` is set, it resets to the original. A `cd` that
  stays inside the start directory therefore holds. This supports S1-T17 (`~/.dotfiles/.claude/...`)
  and step 3 (`~/Projects/.worktrees/...`). The claim holds as the plan uses it.
- **`git rev-parse --git-dir` from a linked worktree.** Probed:
  - The linked root prints the absolute `<main>/.git/worktrees/linked`, and so does a subdirectory.
  - A nested `.claude/worktrees/probe` prints `<main>/.git/worktrees/probe`.
  - The main checkout prints the relative `.git`.
  - A non-git directory fails.
  - With no ignore line, the nested probe shows in the main checkout as `?? .claude/`, so S1-T6's
    `.gitignore` line is needed, and it is there.
  - S1-T4's "main checkout while the file sits in a linked worktree's git dir" case is well-defined.
- **Side note on M2.** agent-view says a background session skips isolation inside any linked
  worktree, "whether Claude created it under `.claude/worktrees/` or you created it with
  `git worktree add` somewhere else". The binary prompt that M2 quotes says only `.claude/worktrees/`.
  The commit ask applies either way, so M2's conclusion stands.

## Question 5: owner touchpoints

Geoff acts at these points:

1. Pre-launch 1a, with the planning session: he rules on any S1-T1 stop and reads the `AHEAD:` output
   (:276-288).
2. He opens a tab and pastes the 1a launch (:299-304).
3. He answers any 1a stop: a one-executor stop, a red after two attempts, a review `escalate`, or a
   design question (:49-54).
4. He reads the step 1 PR (S1-T13).
5. The merge block (:751-764):
   - He exits every Claude session, including the idle 1a tab.
   - He runs the checks, `gh pr merge`, and the pull and restow line.
   - He pastes the 1b launch.
6. He answers any 1b stop and owns the rollback decision (:777-781, :798-807).
7. After S1-T18 he runs three pre-launch blocks and pastes three launches (:906-915, :1083-1097,
   :1289-1296).
8. He answers stops in steps 2 to 4. Each fired clock stop counts as one event.
9. He reads and merges eight PRs: cairn-cms, six from step 3, and dotfiles step 4. The ecxc-ski,
   907-life, and xcathletes-org merges deploy production, as R-B intends.
10. He pastes step 5's launch for pass B, under `pass-core` as S1-T5 writes it.

That makes five launch pastes in this plan, plus one terminal merge and eight PR merges.

On the fold's open item:

- **Right for this cutover.** 1a, 1b, and step 3 need an interactive session.
- **Wrong as a general premise.** A single-repo pass can be launched with no paste: a self-isolating
  `--bg` session started from the main checkout "commits without asking, and pushes the branch"
  (agent-view). A session can also open the interactive tab itself through `ptyxis --tab ... -x`, or
  host it in tmux. Neither path was probed with `claude`.
- **Costs of `--bg`.** The branch is named `worktree-<name>`, setup runs inside the session, and a stall
  surfaces only in agent view.
- **The departure.** A paste on every pass is an attended event outside ruling 4 and the Success test.
  It needs Geoff's ruling and a recorded departure before S1-T5 writes it into `pass-core` (V-M3).

## Question 6: over-folding

No added text costs more than the risk it removes. The plan grew 134 net lines (478 added, 344
removed). The largest additions each carry a probed mechanism that a reviewer asked for:

- the merge block and the 1b prompt
- the `auth-data` globs
- the rollback
- M16

One optional trim: M2 cites a strings dump under `/tmp/claude-1000/mech-review/`, which a reboot
clears. The executing sessions never need it, so it could become a one-line citation of the agent-view
sentence alone.
