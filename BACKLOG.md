# BACKLOG

> Project issue tracker. Managed by `/log-issue`.

## High

- [ ] **#39** Forbid pattern signals in the read-only review agents `#bug` `#workstation` `#initiative:docs-system` *(2026-10-25)*
  On 2026-10-25 a `plan-reviewer` probing a `pgrep` pattern cleaned up its fake processes with `pkill -f 'drafter page'` and killed batch 5's live drafting run, which resumed. Add a line to each read-only agent body (`plan-reviewer`, `diff-reviewer`, `fact-checker`, and the rest): a probe kills only PIDs it started, never by pattern. `claude/.claude/agents/`.
  Record: ~/Projects/initiatives/docs-system/research/2026-10-25-drafter-batch-4-friction-plan-review-mechanics.md (incident note)

## Medium

- [ ] **#38** Catch an edit made only in a vendored skill's copy `#bug` `#workstation` *(2026-10-25)*
  Three commits (`b01f85f`, `8a629f6`, `5296043`) edited `claude/.claude/skills/survey/writing/approval-brief.md` in place, so the next vendor from Survey would have reverted them; the Survey v1.5.0 release found it by hand and took the text back into Survey (glw907/survey#6). `claude-tooling-sync lint` checks manifest shape, licenses, and overlays, never content. Add a check that each vendored skill matches its source at the manifest's `commit`, overlays applied, and fails with the files that drifted. `bin/.local/bin/claude-tooling-sync` (`lint`).

- [ ] **#37** Name the framework version in the register editor's and fact-checker's briefs `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-25)*
  Both agents raised `#lib` imports as defects. They are SvelteKit 3's subpath-import convention, which the migration notes record. The agents' briefs should name the framework version. `claude/.claude/agents/cairn-register-editor.md`, `claude/.claude/agents/fact-checker.md`.
  Record: ~/Projects/initiatives/docs-system/research/2026-10-24-extend-blueprints-batch-4/friction.md (P9)

- [ ] **#36** Exclude the facts store from the tellgrader PostToolUse hook `#bug` `#workstation` `#initiative:docs-system` *(2026-10-24)*
  The hook flagged "empty-own" on fact bullets ("Svelte's own mount()"), which aren't page prose.
  Record: ~/Projects/initiatives/docs-system/research/2026-10-24-extend-blueprints-batch-4-friction.md (workstation 3)

- [ ] **#35** Have the register editor quote its target text, and avoid the `exhaustive` words `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-24)*
  Its line numbers drifted from the file at the named commit; the author matched on text. It should also avoid the words drafter's `exhaustive` lint flags, or say a count is fact-backed. `claude/.claude/agents/cairn-register-editor.md`.
  Record: ~/Projects/initiatives/docs-system/research/2026-10-24-extend-blueprints-batch-4-friction.md (workstation 2)

- [ ] **#34** Cap a fact-checker proposal at the register's sentence length `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-24)*
  Proposed fixes ran past 26 words or stacked ", which" and ", so" tails, so none could be pasted, and one proposal was itself wrong (`toggleTheme` where the scaffold calls `toggleThemeWithTransition`). `claude/.claude/agents/fact-checker.md`.
  Record: ~/Projects/initiatives/docs-system/research/2026-10-24-extend-blueprints-batch-4-friction.md (workstation 1)

- [ ] **#33** Keep the workstation secrets out of apps a Claude session launches `#bug` `#security` `#initiative:self-hosting` *(2026-10-24)*
  On thinkpad-x1 the running Hylki Flatpak carried every `~/.local/secrets` value in its environment, along with `CLAUDE_CODE_SESSION_ID=82707928-…`, so a Claude session launched it and it inherited that session's exported secrets. Any process listing shows them: a `pgrep -af claude` on 2026-10-24 matched Hylki's web process and printed them all into a session transcript. A GUI app started from a session should get a clean environment (`env -i` with the display variables, or `systemd-run --user`/`gio launch`), and Hylki should be restarted from the desktop. Source: servers session of 2026-10-24.

- [ ] **#28** Create the Survey house style `#feature` `#workstation` *(2026-10-21)*
  Geoff ruled on 2026-10-21 that Survey is the house style for every house tool, beyond its role as a cairn theme, and that it is implemented differently by context: a cairn site, a SvelteKit and DaisyUI tool such as the approval queue or the phonebook, and a third-party app that takes only tokens and marks, such as Bulwark webmail (servers BACKLOG #13). Describe it once across those contexts. Its spec today (`cairn-themes/docs/specs/2026-10-07-survey-design.md`) covers only 907.life and the phonebook. Survey's core has never been committed to `cairn-themes`: the only copy is `approval-queue/src/lib/survey/`, whose header cites a commit, `dea9839`, that no branch holds. Pull the approval queue's reusable styling back into Survey first, as `cairn-themes` BACKLOG #1 (motion tokens) and #2 (focus ring, fields, key hints, toast, float shadow, frame, scrollbars) set out. Bulwark's theming waits for this. The rule's line is in `claude/.claude/CLAUDE.md`, under the DaisyUI-first rule.

- [ ] **#27** pass-core's launch checks read the job state after a `claude --bg` launch `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-20)*
  After "Execute" or "Conductor" launches a session, read `~/.claude/jobs/<id>/state.json`: `needs: "send a prompt to start"` is a failed launch. A listed session, or the TUI banner in `claude logs`, proves only that the process is up. Two notes for the same lines: `--add-dir` is variadic, so the prompt goes before it; a stray job is stopped with `claude stop <id>`, since the daemon respawns a bare kill. On 2026-10-20 the blueprint-first planner sat idle 80 minutes after a launch with the prompt after `--add-dir`. `claude/.claude/skills/pass-core/SKILL.md`

- [ ] **#26** Get API access to the house router once its local admin password exists `#improvement` `#workstation` *(2026-10-20)*
  The TP-Link Archer C4000 v3.0 at 192.168.1.1 is bound to a TP-Link ID, and its local admin password is unknown; TP-Link's forum says a bound router can't change or reset it short of a factory reset. The `tplinkrouterc6u` client (auto-detects its C1200-family driver on this firmware; test script in the 2026-10-20 session) needs the local password and rejects TP-Link ID login. `TPLINK_ROUTER_PASSWORD` in the age store currently holds the TP-Link ID password by mistake, registry marked pending. To finish: factory-reset and re-set-up the router, record the local password in Proton Pass, `secret-receive TPLINK_ROUTER_PASSWORD --pass <ref>`, run a read-only status call, flip the registry checkmark. Until then, router changes go through the browser in the Claude Chromium profile with a TP-Link ID sign-in. Side note: the router's login page carries TP-Link's leftover weinre debug script tag pointing at 192.168.1.101:1070; nothing answered there on 2026-10-20. `secrets/registry.md`

- [ ] **#25** pass-core's design step says what a session does after a pass misses its bar `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-19)*
  Read the pass's final artifacts, not the record's table; compare by word count, since live pages are hard-wrapped; dispatch one fact-check agent per artifact against the code with a file:line evidence bar; trace each wrong claim to its source (draft, fact, blueprint, live page, code comment) before designing the next pass. This turned B3c's 0 of 8 into a diagnosis of the acceptance machinery: `~/Projects/initiatives/docs-system/research/2026-10-19-drafter-b3c-draft-review.md`. `claude/.claude/skills/pass-core/SKILL.md`

- [ ] **#24** Add a `workstation-sync` script that brings a machine current `#feature` `#workstation` *(2026-10-17)*
  The thinkpad-x1 sync on 2026-10-17 was all mechanical steps: fast-forward `~/.dotfiles` and its tool repos (approval-queue, initiatives), `claude-tooling-sync apply`, `stow -R` each package, enable the timers `bootstrap.sh` enables, and install what the manifests list but the machine lacks. Script those, end with `check-drift`, and add a runbook line that points at it; adopt-or-remove calls stay with the `check-drift` report. Close three gaps that sync exposed. `check-drift` watches only the initiatives clone, so the approval-queue checkout sat 19 commits behind with no `packet` command. It skips `/etc/firefox/policies/policies.json` as "unreadable without sudo", which hid a policy never installed on this laptop. The ratchet's dead-reference check resolves paths on the live filesystem, so `scripts/check.sh` failed on main on a machine missing that policy.

- [ ] **#23** Vale lints no file of `docs/voice/` `#improvement` `#workstation` `#initiative:approval-packets` *(2026-10-17)*
  `vale claude/.claude/docs/voice/approval-brief.md` scopes the register out (0 files linted), so only the `tellgrader` register gate reads it. Decide whether the register belongs in `.vale.ini`'s scope.

- [ ] **#22** `ci-green` cannot watch a `master` repo `#improvement` `#workstation` `#initiative:approval-packets` *(2026-10-17)*
  `bin/.local/bin/ci-green` merge-bases against `origin/main`, so `ci-green <sha> --pr <n> --wait` exits 3 ("couldn't find remote ref main") in poplar and dubplate, whose default branch is `master`. Read the default branch from the repo. The pass watched poplar PR 3 with `gh pr checks --watch` instead.

- [ ] **#1** Thunderbird Nord mail follow-ups `#improvement` `#workstation` *(2026-10-14)*
  **Thunderbird Nord mail follow-ups** (Geoff, 2026-10-13, triage of PR #49): one pass for the six items he marked "now": (1) fix the gate's baseline on pavilion, the four ratchet lines and 22 pytest failures that read Homebrew's Python 3.15 paths (a `runner` pass); (2) add a `.vale.ini` so `vale thunderbird/README.md` lints something; (3) find the white strip beside the message list in the dark reader shots; (4) derive `--color-text-highlight-dark` in `customContent.css` from `nord.css`; (5) gate white text on `--mail-accent-fill` (4.03:1); (6) brighten the card tag icons. Two items are deferred until Geoff has run `thunderbird-theme-sync` on his live profile: recolour the header tag pills with the Nord tag roles (needs a contrast check, since Thunderbird picks pill text from the raw hex), and check the tag colours on the live profile (the test profile reads back Thunderbird's defaults). Harness: `thunderbird/tools/tb-shots`.

- [ ] **#2** musicbox repo split `#improvement` `#workstation` *(2026-10-14)*
  **musicbox repo split**: the music-VPS spec, plan, and library design (`~/Projects/dubplate/docs/plans/2026-08-30-music-vps-build.md`, `~/Projects/dubplate/docs/specs/2026-08-30-music-vps-build-design.md`, `~/Projects/dubplate/docs/specs/2026-08-30-music-library-design.md`) describe a Hetzner server, another machine's config. They move to their own repo before server artifacts accrete; coordinate with the music session that owns them.

- [ ] **#3** claude-wf-guard alarms on a run that finished cleanly `#improvement` `#workstation` *(2026-10-14)*
  **`claude-wf-guard` alarms on a run that finished cleanly.** Its idle alarm cannot tell a finished workflow from a stalled one (its own message says "a clean finish looks identical"), so every completed run ends with exit 2 and an ALARM, ten minutes after the run's real completion notification. Cairn Go tool pass A (2026-09-19/20) ran ten workflows and paid one session turn per run to confirm each alarm was false. The fix is not in `journal.jsonl`, which records only `launched`, `started`, and `result` and has no run-level completion event, and the guard already avoids journal idle on purpose. It needs a completion signal from outside the journal: the workflow task's own output file (`tasks/<task-id>.output` is written when the run completes) passed as an optional fourth argument, on whose appearance the guard exits 0 silently. Until then a session treats an idle ALARM that arrives AFTER the run's completion notification as expected, checks only that any live run still has a guard, and moves on.

- [ ] **#4** Poplar adopts pass-core `#improvement` `#workstation` `#initiative:poplar-refounding` *(2026-10-14)*
  **Poplar adopts `pass-core`** (Geoff, 2026-10-11, ruling R4 of the infra sweep re-plan). After infra sweep 2, a poplar PR gives poplar a small adapter like dubplate's and replaces `poplar/CLAUDE.md`'s "Conducting a pass" section, which defers to a deleted global rule. It also repins `poplar-reviewer` (`claude-opus-5` at `high`) and `poplar-implementer` (no effort), and drops the missing `glw907-vendor.sh` re-sync line (DC-11, DC-12).

- [ ] **#5** Document the brief's local field in cairn-docs-drafter.md `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-14)*
  **Document the brief's `local` field in `cairn-docs-drafter.md`** (PR #25, triage 2026-10-12). The chain's `draftPrompt` tells the drafter about the brief's top-level `"local"` array, but the agent definition does not, so a drafter dispatched outside the chain never sees it. PR #25 left the definition untouched because definitions load from the stowed main checkout. With #25 merged, add the field and its one-writer sentence to `claude/.claude/agents/cairn-docs-drafter.md`.

- [ ] **#6** Docs page chain follow-ups from drafter Pass 0 `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-14)*
  **Docs page chain follow-ups from drafter Pass 0** (deferred in Geoff's triage of glw907/workstation#36, 2026-10-12). Remove the `planFormat: "markdown"` escape hatch once no markdown plans remain. Add goldens for the markdown `replan:` and rework prompts if either is edited. Make the nonzero-`checkPlan` replan test assert `status === "escalate"` beside `reason` (`tests/docs-page-chain-outline.test.mjs:1452`). Truncate the validator output in the escalation reason, or move it to its own field (`docs-page-chain.js:2018`).

- [ ] **#7** The plan read checks code before it asserts behavior `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-14)*
  **The plan read checks code before it asserts behavior** (cairn's 11-plan test, 2026-10-12). On debug-your-site, the plan-mode structural read said refusals log no event, but `section-action.ts:216` logs `auth.access.refused`. Tell the plan-mode `structurePrompt` in `docs-page-chain.js` to check the code before stating a behavior, and to mark such a finding as a lead. The same test suggests a cross-plan anchor check for the drafter pipeline's consistency read: a link's anchor against the target page's plan headings.

- [ ] **#8** PR test CI for dotfiles `#improvement` `#workstation` *(2026-10-14)*
  **PR test CI for dotfiles.** Add a workflow that runs `bash scripts/check.sh` on `pull_request`. Until it lands, the full-suite home is the local close gate (ruling 11 of the lean pass process spec).

- [ ] **#9** Release the lid-switch hold when a session ends `#improvement` `#workstation` *(2026-10-14)*
  **Release the lid-switch hold when a session ends** (PR #34 triage, 2026-10-12). Neither an executor nor a conductor releases a running `systemd-inhibit ... sleep NNN` lid hold before it ends, so the hold can outlive its session until NNN runs out. Add the release step to `~/.claude/docs/unattended-work-guards.md` and to the ending of `pass-core`'s "Execute" and "Conductor".

## Low

- [x] **#32** Have `ci-green` report `action_required` as held, not red `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-24)*
  A run triggered by a bot-pushed commit (cairn-cms's baseline regen pushes as `github-actions[bot]`) sits in `action_required`, and `ci-green` reports it as red. Name it held and print the release command, `gh api -X POST repos/<owner>/<repo>/actions/runs/<id>/approve`. Moved from cairn-cms #52. Record B3-11.
  Done: PR #146.
- [x] **#31** Hold the fact-checker agent to its JSON array, or give it a notes field `#improvement` `#workstation` `#initiative:docs-system` *(2026-10-22)*
  One of eight runs appended prose after the array, which broke a verbatim save of the findings. `claude/.claude/agents/fact-checker.md` (record 23).
  Record: `~/Projects/initiatives/docs-system/research/2026-10-22-extend-blueprints-pilot-friction.md`
  Batch 2: the agent hands back through `SubagentHandback`, so saving its array verbatim needs a transcript parser. Give the save a sanctioned path, or have the agent write its array to a named file (record 18).
  Done: PR #146 (the agent writes its array to the path the dispatch names).
- [ ] **#10** Two gate-tool cleanups `#improvement` `#workstation` *(2026-10-14)*
  **Two gate-tool cleanups**, deferred by Geoff's triage of cairn-cms PR #114 (2026-10-11): simplify `cairn-docs-outline`'s lock and fix `gateMatches`' stale doc comment; and give `cairn-run-gate` per-leg timing in its run records.

- [ ] **#11** Approval queue hardening `#improvement` `#workstation` `#initiative:approval-queue` *(2026-10-14)*
  **Approval queue hardening**, deferred by Geoff's triage of workstation PR #13 (2026-10-11). A running app keeps serving its old build after a merge changes `~/Projects/approval-queue/approval-queue/`. Nothing prunes decided items from the state directory. A SIGKILL or power loss leaves the item on the index. The CSP limits only `script-src`, so a remote image in a PR body loads at view time (`img-src 'self' data:` closes it). `~/Projects/approval-queue/tests/approval-queue.test.sh` never runs the 10-second "did not answer" exit or the lock release. The approval-packets pass delivered the rest: the board skips an unreadable `item.json` or `decision.json` and names it, and the shell tests exercise the start-the-app branch.

- [ ] **#12** Infra-sweep 2 leftovers `#improvement` `#workstation` `#initiative:monthly-model-review` *(2026-10-14)*
  **Infra-sweep 2 leftovers**, deferred by Geoff's triage of workstation PR #16 (2026-10-11). The model review's nine design topics (guard-fail-closed, saved-effort, dispatch-effort, superpowers-pressure, agent-definitions, claude-md-style, convention-skills, vendored-overlays, process-skills); re-run the review after the merge. Each monthly review worktree keeps its lock under the main checkout, so `prompt.txt` or the script should unlock and remove it after the merge. Stale "kitty-shot harness" wording at `bootstrap.sh`, `Brewfile`, the `kitty-headless-shot` header comments, and the `tui-visual-verify` intro. `engine-consult` hand-lists the `check:close` set, and `cairn-figure` and `figure-verifier` copy the register's `repro` caption and diagram exemption text. A `verify` skill could carry the repo gate; three skills dispatch without `effort`; `register-check` has no `argument-hint`. Poplar's icon-width and JoinHorizontal rules from the deleted `bubbletea-conventions.md` (poplar's refactor pass re-homes them). `registry.md` has no entry id for the Cloudflare token.

- [ ] **#13** Approval queue UI leftovers `#improvement` `#workstation` `#initiative:approval-queue` *(2026-10-14)*
  **Approval queue UI leftovers**, deferred by Geoff's triage of workstation PR #22 (2026-10-11). `cairn-run-gate --records` prints epoch-sized values instead of durations. `ItemPanel`'s teardown clears every key handler, including the ones its views registered; each component should remove only its own. The undo toast sits at a fixed `bottom-24` and can cover a tall decision bar, and a failed-post toast cannot be dismissed. The shortcut hints inside colored buttons are estimated near 4:1 (Reject lowest) and need a measurement in both themes. Below `lg` the open drawer has no focus trap and `j` and `k` do nothing while it is closed. Verify whether `beforeNavigate` fires for the same-page `#` figure links, which would undo a decision held in the page. Smaller: the toast's "Opening X" can name a different item than the server picks; a queue click while a post is in flight is not cancelled; the triage arrows fire from outside `main`; the empty page can stick at "Closing this tab." when `window.close()` is refused; `classifyDiff` has no caller; a triage move speaks through two live regions; the unchecked toggle's edge is unmeasured at 3:1. Cosmetic: the PR and design bar buttons sit right at 390 px, the file-row `+N` and `-N` gap is wider than the mockup's, an opened file header takes a fill, and the triage reason text is about 1 px large.

- [ ] **#14** Approval queue brief leftovers `#improvement` `#workstation` `#initiative:approval-queue` *(2026-10-14)*
  **Approval queue brief leftovers**, deferred by Geoff's triage of workstation PR #43 (2026-10-12). Smart quotes in rendered session copy (`marked-smartypants`, through `dependency-upgrade`). A component test for the effect that registers key handlers, once the app has a component harness. Four small a11y items: the "Decide X" link scrolls without moving focus, ages read as "12m", the bar's fade catches clicks, and button labels carry kbd names. A link inside a Details summary nests interactive content in `<summary>`; it needs a summary-only renderer. `listItems` in `brief.ts` reads `- 2. foo` as `foo` and a nested bullet as top level. `dotfiles-pass` should name `gitleaks detect --source . --log-opts main..HEAD`, the form the worktree guard allows. Approving a design item drops its `### Decide:` picks: the repo organization design (2026-10-14) came back as `{"decision":"approve"}` with no `choices`, though `approval-brief.md` promises one per block, so either the design page renders no Decide cards or its approve omits them (logged at Geoff's request, 2026-10-14). A pass plan never reaches the queue: `pass-core` hands a `runner` or `auth-data` plan straight to its conductor, so Geoff can't read the plan of a pass that deletes repos or opens 16 PRs before it runs. Give the queue a plan item, readable before launch, whose choices survive the approve (Geoff, 2026-10-14).

- [ ] **#15** Two worktree-guard notes `#improvement` `#workstation` *(2026-10-14)*
  **Two worktree-guard notes**, from the same triage: the pair-dispatch template should tell a subagent that the worktree Bash guard refuses compound commands, so it uses plain calls and the Write tool; and the guard refuses `gitleaks git` and a `node` run with a computed path.

- [ ] **#16** The deferred infra-sweep checks `#improvement` `#workstation` *(2026-10-14)*
  **The deferred infra-sweep checks** (ruling R2 of the 2026-10-11 re-plan: a check is built when it has a live catch). These are duplicate-paragraph with `parity.json`, plus cross-repo mode with heading-citation, orphan-doc, and `check-drift --only claude`. Definitions: `docs/specs/2026-09-28-claude-infra-sweep-design.md` "Pass A-rest". Build one when a defect of its class surfaces, which is its first catch.

- [ ] **#17** Devcontainers `#improvement` `#workstation` *(2026-10-14)*
  **Devcontainers** for the SvelteKit/Cloudflare site repos: logged per repo (907-life #2, ecxc-ski #39, xcathletes-org #4, the ASC STATUS chore), built as each repo matures. Research: `bluefin/devenv-research.md`.

- [ ] **#18** kitty harness replacement `#improvement` `#workstation` *(2026-10-14)*
  **kitty harness replacement**: kitty exists only as the `tui-visual-verify` capture platform (XWayland-forced). When a Wayland-native or terminal-agnostic capture method proves out, the harness moves and kitty leaves the machine entirely.

- [ ] **#19** Custom uBlue image `#improvement` `#workstation` *(2026-10-14)*
  **Custom uBlue image** for the second workstation: bakes the devmode rebase and Flatpak set into the image instead of undoing defaults per machine. An explicit later decision, not assumed.

- [ ] **#20** bootstrap.sh restore split `#improvement` `#workstation` *(2026-10-14)*
  **bootstrap.sh restore split**: the restore phase is two-thirds of the file and a different risk class (destructive, run cold). Split into `bluefin/restore.sh` with shared helpers when workstation #2 lands.

- [ ] **#29** tellgrader posthook tests fail in a worktree under /tmp `#bug` `#workstation` *(2026-10-22)*
  **Three `internal/posthook` tests fail when the dotfiles checkout sits under `/tmp`** (`TestRunFlagsChangedLineOnly`, `TestRunSkipsUngovernedPaths`, `TestWholeDocFindingsOnlyOnWrite` return no advisory), so the gate goes red in a scratchpad worktree while the same tests pass in `~/.dotfiles` and in `.claude/worktrees/`. The hook likely treats a `/tmp` path as ungoverned. Make the tests use a path independent of where the checkout lives.

## Done

- [x] **#21** secret-set.sh writes values unquoted `#bug` `#workstation` `#initiative:self-hosting` *(2026-10-19 → 2026-10-23)*
  `secret-set.sh` and `sync.sh` now write each line as `export NAME=<value quoted with printf %q>`, so sourcing `~/.local/secrets` returns every value byte-exact; `monitor-subscribe` reads the token through a subshell source instead of a raw `sed`. `tests/secret-set-quoting.test.sh` round-trips a value with spaces, `$`, backticks, quotes, a backslash, and a trailing `=`. Existing files regenerate on the next `secret-set.sh --sync`.

- [x] **#30** Retire vdirsyncer and khard now that contacts sync to ward `#improvement` `#workstation` `#initiative:self-hosting` *(2026-10-22 → 2026-10-22)*
  GNOME Contacts and Calendar read ward over a GOA WebDAV account since 2026-10-22, and `vdirsyncer.timer` is stopped and disabled. Remove the `contacts` stow package and its `stow-packages.txt` line; drop khard and vdirsyncer from `uv-tools.txt` and uninstall them; remove `bootstrap.sh`'s timer setup and its `.contacts`, `.vdirsyncer`, and khard paths; have `SECOND-WORKSTATION.md` add the ward GOA account instead; retire `fastmail-dav-password` and the `FASTMAIL_DAV_PASSWORD` registry entry once nothing else reads it (check poplar); drop the two `vdirsyncer.timer` allow rules in `settings.json`; update `bluefin-admin.md`, `fastmail-api.md`, the README, and the Brewfile comment. Keep `~/.contacts/` as the Fastmail-era snapshot. One short `ordinary` pass.
