# BACKLOG

> Project issue tracker. Managed by `/log-issue`.

## High

- [ ] **#39** Add the kill-only-your-PIDs rule to the read-only agents in glw907/standards `#bug` `#workstation` `#initiative:docs-system` *(2026-10-25)* *(swept 2026-11-03)*
  On 2026-10-25 a `plan-reviewer` probing a `pgrep` pattern cleaned up its fake processes with `pkill -f 'drafter page'` and killed batch 5's live drafting run, which resumed. Add a line to each read-only agent body: a probe kills only PIDs it started, never by pattern. `plan-reviewer`, `diff-reviewer`, and the rest moved to the standards plugin (glw907/standards), so add it there; `cairn-register-editor` and `prose-voice-reviewer` in `claude/.claude/agents/` need it too.
  Record: ~/Projects/initiatives/docs-system/research/2026-10-25-drafter-batch-4-friction-plan-review-mechanics.md (incident note)

## Medium
- [ ] **#51** Make `claude-block-pass` read shell words instead of matching text `#improvement` `#workstation` `#initiative:credential-hygiene` *(2026-11-07)*
  The hook matches each Bash command against regex patterns, so each disguised spelling needs another pattern. Pass A's review rounds found 11 kinds of bypass (globs, ANSI-C quoting, fake heredocs, stdin feeds), and all are folded and tested (glw907/workstation#201). The third round's probes never ran, because a classifier stopped the reviewer, so the fixes in 4c951ef are unprobed. Geoff merged it as it stood ("Merge now", 2026-11-07). Parse the command into words (`shlex` with `punctuation_chars`, or `bashlex`) and decide on command-position words. Also settle whether a bare `proton-pass-cli` should count only after `cd` or `pushd`. It also gives false positives on quoted text: on 2026-11-07 it refused a `git commit -m` whose message held "(pass-cli docs", reading the `(` as a command start.
  False positive (2026-11-08, cairn-setup design session): the read-only `grep -rhoE "from '(remark|rehype|micromark|mdast)[a-z0-9-]*'" src/lib | sort | uniq -c` in ~/Projects/cairn-cms was refused three times with "pass-sitting denied". The bars and the `(` sit inside a quoted grep pattern, which the text matcher reads as command separators. Word parsing would fix this as well; add the command to the tests.
  Second false positive, same session: a `pgrep -fa 'cairn-cms-cairn-new-1|cairn-pub-cairn-pub-docs-md' | grep -v ...` wait loop was refused as "Proton Pass access denied", most likely on the `pub-` or the quoted `|`.
- [ ] **#50** Let an Approval Queue decision reach the auto-mode classifier `#bug` `#workstation` *(2026-11-02)* *(swept 2026-11-03)*
  On 2026-11-02 the classifier refused `gh pr merge 197 --match-head-commit` as "Merge Without Review" after Geoff approved the PR in the queue, and passed once he typed the instruction. It sees only typed messages, so a queue approval is invisible to it; PR glw907/sportsyou-notify#2 merged under the same command, so the refusal isn't consistent. Find a path that doesn't need a typed repeat.
- [ ] **#49** Stop inline comments and quoted operators fooling `claude-merge-guard` `#bug` `#workstation` *(2026-11-01)* *(swept 2026-11-03)*
  Its `stages` copies the two flaws the launch guard review found: `shlex` keeps its `#` commenter, so a comment on the line before `gh pr merge` can merge the stages, and quoted text can pass as an operator. Found by reading only. `claude-launch-guard`'s `mask` is the fix to reuse.
- [ ] **#48** Find why the thinkpad Do Not Disturb drift went unseen `#bug` `#workstation` *(2026-11-01)* *(swept 2026-11-03)*
  Do Not Disturb was off on thinkpad-x1 (`org.gnome.desktop.notifications show-banners` is true), against the calm desktop rule. `check-drift` already reconciles the key (`bluefin/gnome-settings.txt:16`), so find why it did not flag the drift there. Found in the sportsyou-notify design.
- [ ] **#46** Add Email Sending to `retire-project`'s teardown `#improvement` `#workstation` *(2026-11-01)* *(swept 2026-11-03)*
  Found retiring xcathletes-org. Step 4 names Email Routing, but a domain onboarded to Email Sending keeps locked `cf-bounce` records that answer "managed by Email Routing" even with routing off. Disabling the domain under Email Sending removed them. Both are dashboard steps, so the inventory and the packet should name them up front.
- [ ] **#44** Make a conductor's session name match the name its executor trusts `#bug` `#workstation` `#initiative:docs-system` *(2026-10-27)* *(swept 2026-11-03)*
  The docs eval trust conductor prompt opens "You are conductor-cairn-cms", but nothing set that name: the session ran as `initiatives-b1`. The executor takes cross-session messages only from `conductor-cairn-cms`, so it refused Geoff's relayed pause on 2026-10-27, and the pause took a hard `claude stop` instead (glw907/cairn-cms#154, Planning misses). Fix in `pass-core` "Launch prompt": a conductor hand-over carries the exact `claude --name <conductor>` line, and the conductor prompt's first step checks its own row in `claude agents --json` and stops on a mismatch.


- [ ] **#42** Add two executor-permission checks to the plan-reviewer checklist `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-26)* *(swept 2026-11-03)*
  From the docs-as-code cutover's planning misses. A deletion target that is a symlink resolving outside the executor's `--add-dir` set raises an unanswerable prompt overnight, so the plan makes it a morning step. A STATUS or clock file under `.git/worktrees/` is written by a lone Bash command: Write and Edit are refused there in a worktree-isolated session, and a heredoc chained to another command raised a sensitive-file prompt. Record: `~/Projects/initiatives/docs-system/README.md` (2026-10-26 line).

- [ ] **#40** Let a pass executor run its gate through cairn-run-gate from an isolated worktree `#bug` `#workstation` `#initiative:docs-system` *(2026-10-25)* *(swept 2026-11-03)*
  The approval-queue batch 4 executor (glw907/approval-queue#10) was refused `cairn-run-gate '<cmd>'` and inline env-prefixed command lines in its `EnterWorktree` session, so it ran `bash scripts/gate.sh` bare and wrapped the plan's env-prefixed lines in scripts. pass-core "Gates" says every gate runs through `cairn-run-gate`. Either allow it from a pass worktree, or have `plan-reviewer` check that a plan's gate and env-prefix lines pass the isolated session's guard.
- [ ] **#38** Catch an edit made only in a vendored skill's copy `#bug` `#workstation` *(2026-10-25)* *(swept 2026-11-03)*
  Three commits (`b01f85f`, `8a629f6`, `5296043`) edited `claude/.claude/skills/survey/writing/approval-brief.md` in place, so the next vendor from Survey would have reverted them; the Survey v1.5.0 release found it by hand and took the text back into Survey (glw907/survey#6). `claude-tooling-sync lint` checks manifest shape, licenses, and overlays, never content. Add a check that each vendored skill matches its source at the manifest's `commit`, overlays applied, and fails with the files that drifted. `bin/.local/bin/claude-tooling-sync` (`lint`).

- [ ] **#37** Name the framework version in the register editor's and docs fact-checker's briefs `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-25)* *(swept 2026-11-03)*
  Both agents raised `#lib` imports as defects. They are SvelteKit 3's subpath-import convention, which the migration notes record. The agents' briefs should name the framework version. `claude/.claude/agents/cairn-register-editor.md`, and `docs-fact-checker` in cairn-cms (`.claude/agents/docs-fact-checker.md`).
  Record: ~/Projects/initiatives/docs-system/research/2026-10-24-extend-blueprints-batch-4/friction.md (P9)

- [x] **#36** Exclude the facts store from the tellgrader PostToolUse hook `#bug` `#workstation` `#initiative:docs-system` *(2026-10-24)*
  The hook flagged "empty-own" on fact bullets ("Svelte's own mount()"), which aren't page prose.
  Record: ~/Projects/initiatives/docs-system/research/2026-10-24-extend-blueprints-batch-4-friction.md (workstation 3)
  Dropped: the docs-as-code cutover retired the system it served.

- [ ] **#33** Keep the workstation secrets out of apps a Claude session launches `#bug` `#security` `#initiative:self-hosting` *(2026-10-24)* *(swept 2026-11-03)*
  On thinkpad-x1 the running Hylki Flatpak carried every `~/.local/secrets` value in its environment, along with `CLAUDE_CODE_SESSION_ID=82707928-…`, so a Claude session launched it and it inherited that session's exported secrets. Any process listing shows them: a `pgrep -af claude` on 2026-10-24 matched Hylki's web process and printed them all into a session transcript. A GUI app started from a session should get a clean environment (`env -i` with the display variables, or `systemd-run --user`/`gio launch`), and Hylki should be restarted from the desktop. Source: servers session of 2026-10-24.

- [ ] **#27** pass-core's launch checks read the job state after a `claude --bg` launch `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-20)* *(swept 2026-11-03)*
  After "Execute" or "Conductor" launches a session, read `~/.claude/jobs/<id>/state.json`: `needs: "send a prompt to start"` is a failed launch. A listed session, or the TUI banner in `claude logs`, proves only that the process is up. Two notes for the same lines: `--add-dir` is variadic, so the prompt goes before it; a stray job is stopped with `claude stop <id>`, since the daemon respawns a bare kill. On 2026-10-20 the blueprint-first planner sat idle 80 minutes after a launch with the prompt after `--add-dir`. `claude/.claude/skills/pass-core/SKILL.md`

- [ ] **#26** Get API access to the house router once its local admin password exists `#improvement` `#workstation` *(2026-10-20)* *(swept 2026-11-03)*
  The TP-Link Archer C4000 v3.0 at 192.168.1.1 is bound to a TP-Link ID, and its local admin password is unknown; TP-Link's forum says a bound router can't change or reset it short of a factory reset. The `tplinkrouterc6u` client (auto-detects its C1200-family driver on this firmware; test script in the 2026-10-20 session) needs the local password and rejects TP-Link ID login. `TPLINK_ROUTER_PASSWORD` in the age store currently holds the TP-Link ID password by mistake, registry marked pending. To finish: factory-reset and re-set-up the router, record the local password in Proton Pass, `secret-receive TPLINK_ROUTER_PASSWORD --pass <ref>`, run a read-only status call, flip the registry checkmark. Until then, router changes go through the browser in the Claude Chromium profile with a TP-Link ID sign-in. Side note: the router's login page carries TP-Link's leftover weinre debug script tag pointing at 192.168.1.101:1070; nothing answered there on 2026-10-20. `secrets/registry.md`

- [ ] **#25** pass-core's design step says what a session does after a pass misses its bar `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-19)* *(swept 2026-11-03)*
  Read the pass's final artifacts, not the record's table; compare by word count, since live pages are hard-wrapped; dispatch one fact-check agent per artifact against the code with a file:line evidence bar; trace each wrong claim to its source (draft, page, code comment) before designing the next pass. This turned B3c's 0 of 8 into a diagnosis of the acceptance machinery: `~/Projects/initiatives/docs-system/research/2026-10-19-drafter-b3c-draft-review.md`. `claude/.claude/skills/pass-core/SKILL.md`

- [ ] **#23** Vale lints no file of `docs/voice/` `#improvement` `#workstation` `#initiative:approval-packets` *(2026-10-17)* *(swept 2026-11-03)*
  `vale claude/.claude/docs/voice/approval-brief.md` scopes the register out (0 files linted), so only the `tellgrader` register gate reads it. Decide whether the register belongs in `.vale.ini`'s scope.

- [ ] **#22** `ci-green` cannot watch a `master` repo `#improvement` `#workstation` `#initiative:approval-packets` *(2026-10-17)* *(swept 2026-11-03)*
  `bin/.local/bin/ci-green` merge-bases against `origin/main`, so `ci-green <sha> --pr <n> --wait` exits 3 ("couldn't find remote ref main") in poplar and dubplate, whose default branch is `master`. Read the default branch from the repo. The pass watched poplar PR 3 with `gh pr checks --watch` instead.

- [ ] **#1** Check the pavilion gate baseline on Homebrew Python 3.15 `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **Check the pavilion gate baseline on Homebrew Python 3.15** (Geoff, 2026-10-13, triage of PR #49): the gate's baseline on pavilion has four ratchet lines and 22 pytest failures that read Homebrew's Python 3.15 paths (a `runner` pass). The Thunderbird items left with PR #93.

- [ ] **#2** Move the music-VPS spec, plan, and library design from dubplate to servers `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **Move the music-VPS spec, plan, and library design from dubplate to servers**: `~/Projects/dubplate/docs/plans/2026-08-30-music-vps-build.md`, `~/Projects/dubplate/docs/specs/2026-08-30-music-vps-build-design.md`, and `~/Projects/dubplate/docs/specs/2026-08-30-music-library-design.md` describe a Hetzner server, another machine's config. The servers repo now hosts the dubplate role, so they have a home there; coordinate with the music session that owns them.

- [ ] **#3** claude-wf-guard alarms on a run that finished cleanly `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **`claude-wf-guard` alarms on a run that finished cleanly.** Its idle alarm cannot tell a finished workflow from a stalled one (its own message says "a clean finish looks identical"), so every completed run ends with exit 2 and an ALARM, ten minutes after the run's real completion notification. Cairn Go tool pass A (2026-09-19/20) ran ten workflows and paid one session turn per run to confirm each alarm was false. The fix is not in `journal.jsonl`, which records only `launched`, `started`, and `result` and has no run-level completion event, and the guard already avoids journal idle on purpose. It needs a completion signal from outside the journal: the workflow task's own output file (`tasks/<task-id>.output` is written when the run completes) passed as an optional fourth argument, on whose appearance the guard exits 0 silently. Until then a session treats an idle ALARM that arrives AFTER the run's completion notification as expected, checks only that any live run still has a guard, and moves on.

- [x] **#5** Document the brief's local field in cairn-docs-drafter.md `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-14)*
  **Document the brief's `local` field in `cairn-docs-drafter.md`** (PR #25, triage 2026-10-12). The chain's `draftPrompt` tells the drafter about the brief's top-level `"local"` array, but the agent definition does not, so a drafter dispatched outside the chain never sees it. PR #25 left the definition untouched because definitions load from the stowed main checkout. With #25 merged, add the field and its one-writer sentence to `claude/.claude/agents/cairn-docs-drafter.md`.
  Dropped: the docs-as-code cutover retired the system it served.

- [x] **#6** Docs page chain follow-ups from drafter Pass 0 `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-14)*
  **Docs page chain follow-ups from drafter Pass 0** (deferred in Geoff's triage of glw907/workstation#36, 2026-10-12). Remove the `planFormat: "markdown"` escape hatch once no markdown plans remain. Add goldens for the markdown `replan:` and rework prompts if either is edited. Make the nonzero-`checkPlan` replan test assert `status === "escalate"` beside `reason` (`tests/docs-page-chain-outline.test.mjs:1452`). Truncate the validator output in the escalation reason, or move it to its own field (`docs-page-chain.js:2018`).
  Dropped: the docs-as-code cutover retired the system it served.

- [x] **#7** The plan read checks code before it asserts behavior `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-14)*
  **The plan read checks code before it asserts behavior** (cairn's 11-plan test, 2026-10-12). On debug-your-site, the plan-mode structural read said refusals log no event, but `section-action.ts:216` logs `auth.access.refused`. Tell the plan-mode `structurePrompt` in `docs-page-chain.js` to check the code before stating a behavior, and to mark such a finding as a lead. The same test suggests a cross-plan anchor check for the drafter pipeline's consistency read: a link's anchor against the target page's plan headings.
  Dropped: the docs-as-code cutover retired the system it served.

- [ ] **#8** PR test CI for dotfiles `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **PR test CI for dotfiles.** Add a workflow that runs `bash scripts/check.sh` on `pull_request`. Until it lands, the full-suite home is the local close gate (ruling 11 of the lean pass process spec).

- [ ] **#9** Release the lid-switch hold when a session ends `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **Release the lid-switch hold when a session ends** (PR #34 triage, 2026-10-12). Neither an executor nor a conductor releases a running `systemd-inhibit ... sleep NNN` lid hold before it ends, so the hold can outlive its session until NNN runs out. Add the release step to `~/.claude/docs/unattended-work-guards.md` and to the ending of `pass-core`'s "Execute" and "Conductor".

## Low

- [ ] **#57** Run an effort sweep on the 5.5 models before carrying effort settings forward `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-11-10)*
  For Opus 5.5 and Sonnet 5.5, the effort page says to "Run an effort sweep on your own evals rather than carrying settings over from an earlier model" (<https://platform.claude.com/docs/en/build-with-claude/effort>). The 2026-09-28 sweep filed this to the retired ROADMAP, and it fell out. It needs an eval this machine can't run yet: a fixed task set graded the same way at each level. Record: `docs/specs/2026-11-01-model-review-subagent-effort-design.md`.

- [ ] **#58** Name mail moves as a standing chat exception in `approval-packet` `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-11-10)*
  `mail-tend:61, 88` sends a mail move or rule design to chat, and `approval-packet:29` forbids that. Add one clause to `approval-packet` that names mail moves as a standing chat exception, since they are small and reversible. Record: `docs/specs/2026-11-01-model-review-open-flags-design.md`.

- [ ] **#59** Let forced asks exceed `approval-packet`'s three-ask cap `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-11-10)*
  `approval-packet:38` says "at most three asks", which can't hold when four PRs each carry a forced ask. Keep the cap and say in that line that forced asks may exceed it. Record: `docs/specs/2026-11-01-model-review-open-flags-design.md`.

- [ ] **#60** Tighten `visual-verifier` to 4.5:1 for a CTA pair in glw907/standards `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-11-10)*
  `visual-verifier:30` flags a call-to-action pair under 3:1, while `daisyui-a11y-reviewer:72` uses 4.5:1 for text. Raise the verifier to 4.5:1, WCAG's floor for button labels. The agent lives in glw907/standards, so the edit lands there. Record: `docs/specs/2026-11-01-model-review-open-flags-design.md`.

- [ ] **#61** Narrow `prose-voice-reviewer`'s docs-tier em dash flag `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-11-10)*
  `prose-voice-reviewer:50-51` flags a docs-tier em dash, and the writing-voice output style allows Google's no-space form in developer docs. Narrow the flag to overuse or a spaced dash. Record: `docs/specs/2026-11-01-model-review-open-flags-design.md`.

- [ ] **#62** State who pushes and merges at `site-implementer:70` `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-11-10)*
  `site-implementer:15` says it never pushes, yet `:70` merges a cairn-cms docs branch by PR. Say at line 70 that the dispatching session pushes and merges. Record: `docs/specs/2026-11-01-model-review-open-flags-design.md`.

- [ ] **#63** Add a no-argument `gate.sh` wrapper to the cairn-cms and site adapters `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-11-10)*
  `pass-core`, `cairn-pass:20`, and `site-pass:28` give the `cairn-run-gate '<string>'` form that `dotfiles-pass` says the worktree guard refuses, and a `-w` session's guard refused compound commands too. Add a no-argument `gate.sh` wrapper to each repo's adapter the next time that adapter changes. Record: `docs/specs/2026-11-01-model-review-open-flags-design.md`.

- [ ] **#64** Add a cross-repo clause to `spec-plan-review`'s review records line in glw907/standards `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-11-10)*
  `spec-plan-review:55` sends review records to `docs/research/`, while `pass-core` sends cross-repo research to `initiatives/<id>/`. Keep repo-scoped records in `docs/research/` and add a clause for cross-repo work. The skill lives in glw907/standards. Record: `docs/specs/2026-11-01-model-review-open-flags-design.md`.

- [ ] **#65** Narrow CLAUDE.md's "prefer dispatching reads" to reads across several files `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-11-10)*
  The best practices page retired "Use subagents to protect your context window" because each subagent "costs extra tokens" (<https://code.claude.com/docs/en/best-practices>). Keep the "Initiative-scoped sessions" rule, since it is about cache re-reads, and narrow it to reads across several files. Record: `docs/specs/2026-11-01-model-review-open-flags-design.md`.

- [ ] **#66** Cut `writing-voice.md:64-65` and `:80-81` and re-test in glw907/survey `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-11-10)*
  `output-styles/writing-voice.md` is vendored from glw907/survey, so the cut of those two passages and the re-test of the style land in glw907/survey. Record: `docs/specs/2026-11-01-model-review-open-flags-design.md`.

- [ ] **#54** Clamp token counts and keep the first turn in `cleanroom`'s transcript cost `#bug` `#workstation` `#initiative:cairn-setup` *(2026-11-09)*
  `usage_cost` does not clamp negative token counts, and `transcript_totals` lets a later line that reuses a message id replace the real turn, so a transcript the agent can write could lower the dollar figure the cap reads. Both predate the cost-unknown change (glw907/workstation#218), and the agent already holds a simpler path through `cleanroom statusline`. Clamp each count at zero and keep the first line seen for an id.
  Placement: with the next `cleanroom` change.
- [ ] **#55** Unit-test `cleanroom`'s `verdict()` directly `#improvement` `#workstation` `#initiative:cairn-setup` *(2026-11-09)*
  `verdict()` decides when a run stops, and only the live tests in `tests/test_cleanroom_live.py` cover it, which skip when tmux, dbus, the keyring, or `script` is missing. A table-driven test of the four combinations (statusline stale or fresh, transcript advancing or not, priced or not), plus the two caps, would run on every gate.
  Placement: with #54.
- [ ] **#56** Prove the dollar cap fires from the transcript alone with a stale statusline `#improvement` `#workstation` `#initiative:cairn-setup` *(2026-11-09)*
  The live test for a stale statusline with a priced transcript shows the time cap fires, and the dollar cap's behavior in that case rests on reading `observe()`: `cost` is the max of both figures. A live case where the transcript's cost passes `cap_usd` while the statusline is stale would prove it.
  Placement: with #54.
- [ ] **#53** Tighten `cleanroom`'s trust edges `#improvement` `#workstation` `#initiative:cairn-setup` *(2026-11-09)*
  Found in pass 1's whole-branch review (glw907/workstation#215). (1) The sudoers rule's `*` after `~/.dotfiles/` also matches `/` and spaces, so glw907 can run any script under `~/.dotfiles` as `cleanroom`, wider than the "only `_child`" in `bluefin-admin.md`; it adds no privilege, since glw907 owns those files. (2) The probe's `env | cut -d= -f1` item is a six-name denylist; an allowlist of the expected names would test "no workstation variable" directly. (3) The statusline and transcript costs differed by 55% in the last probe ($0.2067 against $0.3209); the cause is untraced, and the caps use the higher figure. (4) `run_child` and `launch` build the same sudo argument list, and `cmd_shell` builds its plan twice. (5) The re-review's notes, all fail-closed: a failed write at a cost stop makes the watcher's `except` call `end_run` a second time and overwrite the ledger cause with `stopped:watcher`; `trusted_dir` does not check the sticky bit, so a room built before pass 1's fixes needs `init --fresh`; `CLEANROOM_USER` is not in `--preserve-env`, so a non-default user breaks `@USER@`; and `probes.jsonl` does not record whether a probe ran isolated or in-process. (6) `cleanroom shell` leaves its `gnome-keyring-daemon` running after the command exits (it daemonizes out of `dbus-run-session`); `stop` kills it, so a `run` or `probe` is clean, but a bare `shell` is not. Do (1) with the next change to the sudoers file; the rest when a later pass touches `cleanroom`.
  Record: `~/Projects/initiatives/cairn-setup/research/cleanroom-probe-1.md`
- [ ] **#47** Require a prior-art and vendor-guidance check at the design step `#improvement` `#workstation` *(2026-11-01)* *(swept 2026-11-03)*
  The workstation-sync design reached approval before anyone checked published practice or Anthropic's docs, and Geoff had to ask for both mid-build (2026-11-01). That check caught a real data-loss case in `MEMORY.md` and two gaps. Add the check to the `pass-core` design step or `brainstorming`, so a design names what it took from each source. `claude/.claude/skills/pass-core/SKILL.md`

- [x] **#32** Have `ci-green` report `action_required` as held, not red `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-24)*
  A run triggered by a bot-pushed commit (cairn-cms's baseline regen pushes as `github-actions[bot]`) sits in `action_required`, and `ci-green` reports it as red. Name it held and print the release command, `gh api -X POST repos/<owner>/<repo>/actions/runs/<id>/approve`. Moved from cairn-cms #52. Record B3-11.
  Done: PR #146.
- [x] **#31** Hold the fact-checker agent to its JSON array, or give it a notes field `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-22)*
  One of eight runs appended prose after the array, which broke a verbatim save of the findings. `claude/.claude/agents/fact-checker.md` (record 23).
  Record: `~/Projects/initiatives/docs-system/research/2026-10-22-extend-blueprints-pilot-friction.md`
  Batch 2: the agent hands back through `SubagentHandback`, so saving its array verbatim needs a transcript parser. Give the save a sanctioned path, or have the agent write its array to a named file (record 18).
  Done: PR #146 (the agent writes its array to the path the dispatch names).
- [ ] **#10** Give cairn-run-gate per-leg timing in its run records `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **Give `cairn-run-gate` per-leg timing in its run records**, deferred by Geoff's triage of cairn-cms PR #114 (2026-10-11). The stale `gateMatches` comment went with `pass-execute.js`. Also fix `cairn-run-gate --records`, which prints epoch-sized values instead of durations.

- [ ] **#11** Move the CSP and queue items to the approval-queue backlog `#improvement` `#workstation` `#initiative:approval-queue` *(2026-10-14)* *(swept 2026-11-03)*
  **Move to the approval-queue backlog**, where the code lives (`~/Projects/approval-queue`), deferred by Geoff's triage of workstation PR #13 (2026-10-11). A running app keeps serving its old build after a merge changes `~/Projects/approval-queue/approval-queue/`. Nothing prunes decided items from the state directory. A SIGKILL or power loss leaves the item on the index. The CSP limits only `script-src`, so a remote image in a PR body loads at view time (`img-src 'self' data:` closes it). `~/Projects/approval-queue/tests/approval-queue.test.sh` never runs the 10-second "did not answer" exit or the lock release.

- [ ] **#12** Infra-sweep 2 leftovers `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-10-14)* *(swept 2026-11-03)*
  **Infra-sweep 2 leftovers**, deferred by Geoff's triage of workstation PR #16 (2026-10-11). The model review's nine design topics (guard-fail-closed, saved-effort, dispatch-effort, superpowers-pressure, agent-definitions, claude-md-style, convention-skills, vendored-overlays, process-skills); re-run the review after the merge. Each monthly review worktree keeps its lock under the main checkout, so `prompt.txt` or the script should unlock and remove it after the merge. Stale "kitty-shot harness" wording at `bootstrap.sh`, `Brewfile`, the `kitty-headless-shot` header comments, and the `tui-visual-verify` intro. `engine-consult` hand-lists the `check:close` set, and `cairn-figure` and `figure-verifier` copy the register's `repro` caption and diagram exemption text. A `verify` skill could carry the repo gate; three skills dispatch without `effort`; `register-check` has no `argument-hint`. Poplar's icon-width and JoinHorizontal rules from the deleted `bubbletea-conventions.md` (poplar's refactor pass re-homes them).

- [ ] **#13** Move the UI leftovers to the approval-queue backlog `#improvement` `#workstation` `#initiative:approval-queue` *(2026-10-14)* *(swept 2026-11-03)*
  **Move to the approval-queue backlog**, deferred by Geoff's triage of workstation PR #22 (2026-10-11). `ItemPanel`'s teardown clears every key handler, including the ones its views registered; each component should remove only its own. The undo toast sits at a fixed `bottom-24` and can cover a tall decision bar, and a failed-post toast cannot be dismissed. The shortcut hints inside colored buttons are estimated near 4:1 (Reject lowest) and need a measurement in both themes. Below `lg` the open drawer has no focus trap and `j` and `k` do nothing while it is closed. Verify whether `beforeNavigate` fires for the same-page `#` figure links, which would undo a decision held in the page. Smaller: the toast's "Opening X" can name a different item than the server picks; a queue click while a post is in flight is not cancelled; the triage arrows fire from outside `main`; the empty page can stick at "Closing this tab." when `window.close()` is refused; `classifyDiff` has no caller; a triage move speaks through two live regions; the unchecked toggle's edge is unmeasured at 3:1. Cosmetic: the PR and design bar buttons sit right at 390 px, the file-row `+N` and `-N` gap is wider than the mockup's, an opened file header takes a fill, and the triage reason text is about 1 px large.

- [ ] **#14** Move the brief leftovers to the approval-queue backlog `#improvement` `#workstation` `#initiative:approval-queue` *(2026-10-14)* *(swept 2026-11-03)*
  **Move to the approval-queue backlog**, deferred by Geoff's triage of workstation PR #43 (2026-10-12). Smart quotes in rendered session copy (`marked-smartypants`, through `dependency-upgrade`). A component test for the effect that registers key handlers, once the app has a component harness. Four small a11y items: the "Decide X" link scrolls without moving focus, ages read as "12m", the bar's fade catches clicks, and button labels carry kbd names. A link inside a Details summary nests interactive content in `<summary>`; it needs a summary-only renderer. `listItems` in `brief.ts` reads `- 2. foo` as `foo` and a nested bullet as top level. Approving a design item drops its `### Decide:` picks: the repo organization design (2026-10-14) came back as `{"decision":"approve"}` with no `choices`, though `approval-brief.md` promises one per block, so either the design page renders no Decide cards or its approve omits them (logged at Geoff's request, 2026-10-14). A pass plan never reaches the queue: `pass-core` hands a `runner` or `auth-data` plan straight to its conductor, so Geoff can't read the plan of a pass that deletes repos or opens 16 PRs before it runs. Give the queue a plan item, readable before launch, whose choices survive the approve (Geoff, 2026-10-14).

- [ ] **#15** Tell pair subagents the worktree guard refuses compound commands `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **Tell pair subagents the worktree guard refuses compound commands**, from the same triage: the pair-dispatch template should say the worktree Bash guard refuses compound commands, so a subagent uses plain calls and the Write tool. The guard also refuses a `node` run with a computed path.

- [ ] **#16** The deferred infra-sweep checks `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **The deferred infra-sweep checks** (ruling R2 of the 2026-10-11 re-plan: a check is built when it has a live catch). These are duplicate-paragraph with `parity.json`, plus cross-repo mode with heading-citation, orphan-doc, and `check-drift --only claude`. Definitions: `docs/specs/2026-09-28-claude-infra-sweep-design.md` "Pass A-rest". Build one when a defect of its class surfaces, which is its first catch.

- [ ] **#17** Devcontainers `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **Devcontainers** for the SvelteKit/Cloudflare site repos: logged per repo (907-life #2, ecxc-ski #39, xcathletes-org #4, the ASC STATUS chore), built as each repo matures. Research: `bluefin/devenv-research.md`.

- [ ] **#18** kitty harness replacement `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **kitty harness replacement**: kitty exists only as the `tui-visual-verify` capture platform (XWayland-forced). When a Wayland-native or terminal-agnostic capture method proves out, the harness moves and kitty leaves the machine entirely.

- [ ] **#19** Custom uBlue image `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **Custom uBlue image** for the second workstation: bakes the devmode rebase and Flatpak set into the image instead of undoing defaults per machine. An explicit later decision, not assumed.

- [ ] **#20** Decide whether bootstrap.sh restore retires or splits out `#improvement` `#workstation` *(2026-10-14)* *(swept 2026-11-03)*
  **Decide whether `bootstrap.sh restore` retires or splits out**: the restore phase is two-thirds of the file and a different risk class (destructive, run cold). It now serves no machine, since `SECOND-WORKSTATION.md` says never to run it there. Retire it, or split it into `bluefin/restore.sh` with shared helpers.

- [ ] **#29** tellgrader posthook tests fail in a worktree under /tmp `#bug` `#workstation` *(2026-10-22)* *(swept 2026-11-03)*
  **Three `internal/posthook` tests fail when the dotfiles checkout sits under `/tmp`** (`TestRunFlagsChangedLineOnly`, `TestRunSkipsUngovernedPaths`, `TestWholeDocFindingsOnlyOnWrite` return no advisory), so the gate goes red in a scratchpad worktree while the same tests pass in `~/.dotfiles` and in `.claude/worktrees/`. The hook likely treats a `/tmp` path as ungoverned. Make the tests use a path independent of where the checkout lives.

## Done
- [x] **#52** Make the clean-room site-rebuild tool reusable and unattended `#feature` `#workstation` `#initiative:907-rebuild` `#initiative:cairn-setup` *(2026-11-08 → 2026-11-09)*
  done: `bin/.local/bin/cleanroom` (stdlib Python) has `init`, `run`, `shell`, `cost`, `capture`, `scan`, `stop`, and `probe`, with its settings template in `bin/.local/share/cleanroom/`; `signin` and `turn` were dropped and `teardown` becomes cairn's run sweep. The probe record is `~/Projects/initiatives/cairn-setup/research/cleanroom-probe-1.md` (glw907/workstation#215).
- [x] **#45** Move the Proton Pass procedure into a workstation skill `#improvement` `#workstation` *(2026-10-28 → 2026-11-03)*
  done: the `proton-pass` skill (`claude/.claude/skills/proton-pass/`) holds the procedure and states `m.907.life`, and CLAUDE.md and `bluefin-admin.md` point at it.
- [x] **#4** Poplar adopts pass-core `#improvement` `#workstation` `#initiative:poplar-refounding` *(2026-10-14 → 2026-11-03)*
  done: `~/Projects/poplar/CLAUDE.md:59` loads `poplar-pass`, then `pass-core`.
- [x] **#28** Create the Survey house style `#feature` `#workstation` *(2026-10-21 → 2026-11-03)*
  done: glw907/survey exists (`README.md:8` installs it), and the workstation vendors it as `claude/.claude/skills/survey`.
- [x] **#34** Cap a fact-checker proposal at the register's sentence length `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-24 → 2026-11-03)*
  done: `.claude/agents/docs-fact-checker.md:75` in cairn-cms caps `proposed` under 26 words with no stacked `, which` or `, so` tails.
- [x] **#35** Have the register editor quote its target text `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-24 → 2026-11-03)*
  done: `claude/.claude/agents/cairn-register-editor.md:172` requires the exact quoted text; added in 4461c1f.
- [x] **#24** Add a `workstation-sync` script that brings a machine current `#feature` `#workstation` *(2026-10-17 → 2026-11-01)*
  `workstation-sync` runs daily from a user timer on each host; `check-drift --work-only` watches every checkout, approval-queue included. The `/etc/firefox` gap went with Firefox. A path only one host holds carries a `host-ok` marker, which clears the ratchet on the other.
- [x] **#41** Clear drafter from thinkpad-x1 after its next pull `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-25 → 2026-10-31)*
  thinkpad-x1 may carry `~/.local/bin/drafter`, `~/.config/drafter/`, `~/.local/state/drafter/`, `~/.local/share/drafter/`, and links into a drafter clone. Nothing run on pavilion reaches it. After its next `~/.dotfiles` pull, `check-drift` there lists `drafter` as an unlisted bin: remove those paths, the clone, and the `drafter-page-hook` and `docs-page-chain.js` links.

- [x] **#43** Make `cairn-docs-cycle` refuse an unknown argument `#bug` `#workstation` `#initiative:docs-system` *(2026-10-26 → 2026-10-27)*
  Any argument other than `--dry-run` is ignored, so a stray `--help` started a real cycle on 2026-10-26 at 18:51. Print a usage line and exit 2 instead. `bin/.local/bin/cairn-docs-cycle`

- [x] **#21** secret-set.sh writes values unquoted `#bug` `#workstation` `#initiative:self-hosting` *(2026-10-19 → 2026-10-23)*
  `secret-set.sh` and `sync.sh` now write each line as `export NAME=<value quoted with printf %q>`, so sourcing `~/.local/secrets` returns every value byte-exact; `monitor-subscribe` reads the token through a subshell source instead of a raw `sed`. `tests/secret-set-quoting.test.sh` round-trips a value with spaces, `$`, backticks, quotes, a backslash, and a trailing `=`. Existing files regenerate on the next `secret-set.sh --sync`.

- [x] **#30** Retire vdirsyncer and khard now that contacts sync to ward `#improvement` `#workstation` `#initiative:self-hosting` *(2026-10-22 → 2026-10-22)*
  GNOME Contacts and Calendar read ward over a GOA WebDAV account since 2026-10-22, and `vdirsyncer.timer` is stopped and disabled. Remove the `contacts` stow package and its `stow-packages.txt` line; drop khard and vdirsyncer from `uv-tools.txt` and uninstall them; remove `bootstrap.sh`'s timer setup and its `.contacts`, `.vdirsyncer`, and khard paths; have `SECOND-WORKSTATION.md` add the ward GOA account instead; retire `fastmail-dav-password` and the `FASTMAIL_DAV_PASSWORD` registry entry once nothing else reads it (check poplar); drop the two `vdirsyncer.timer` allow rules in `settings.json`; update `bluefin-admin.md`, `fastmail-api.md`, the README, and the Brewfile comment. Keep `~/.contacts/` as the Fastmail-era snapshot. One short `ordinary` pass.
