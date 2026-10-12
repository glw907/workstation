Contract-and-criteria review of `docs/superpowers/plans/2026-10-11-review-desk.md` and its launch prompt, commit 0fd53f5 (`worktree-review-desk-lean`).

Counts: 1 blocker, 6 major, 10 minor. No OWNER FORK: every finding folds inside the approved design.

Mechanisms checked from source, not from memory: kit 3.0.1 `src/runtime/server/respond.js:101-131` and `csrf.js`, `page/index.js:61-182`, `core/config/options.js:87-96,194-215`, `page/csp.js:20,269`; Survey core `theme.css`; this repo's `scripts/check.sh`, `scripts/gate.sh`, `scripts/githooks/pre-commit`, `claude/.claude/settings.json:93-112`, `.claude/skills/dotfiles-pass/SKILL.md`; `git worktree list`.

## 1. Blocker: the session's worktree name is already taken

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk-prompt.txt:3`, `docs/superpowers/plans/2026-10-11-review-desk.md:55`
- **Defect:** The prompt's first act is `EnterWorktree` with the name `review-desk`. `git worktree list` already shows `/var/home/glw907/.dotfiles/.claude/worktrees/review-desk` on branch `worktree-review-desk` (the design branch, at 9b031f9). The new worktree and branch collide with it, so the session's first act fails or lands in the old design worktree. No launch check catches this. The `claude agents --json` check also matches by prefix: `.../worktrees/review-desk` is a prefix of `.../worktrees/review-desk-lean`, where the planning session is live, so the check reads as failed while it should pass.
- **Fold:** Give the executing worktree a new name, such as `review-desk-v1`. Use it in the prompt's `EnterWorktree` line, the `--name`, the plan's launch check, and the Close's `pkill` path. Add a launch check, `git -C ~/.dotfiles worktree list` (must show no `.../worktrees/review-desk-v1`), and compare the `claude agents` cwd to that exact path.

## 2. Major: the end-to-end check serves T1's stale build

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:201,254-255,304-308`
- **Defect:** T1's acceptance runs `npm --prefix review-desk run build` in the session worktree, which writes `build/index.js` with no item pages yet. T2 builds only in its own pair worktree, and the gate never builds. At Close step 3, T3's command finds `build/index.js` present and skips the build, so it serves the T1 app and every item URL returns 404. The check fails for a reason unrelated to the work. If T2's acceptance app (`node review-desk/build`, started in the pair worktree) is still bound to 7907, the command's `curl -sf` succeeds against the wrong app and the wrong `REVIEW_DESK_STATE`. Close's `pkill` names only the session worktree's path, so it misses the pair worktree's app. Either way the start path, the one the end-to-end check alone exercises, never runs. This is the "Later" stale-build item hitting the pass's own check.
- **Fold:** Close step 3 opens with `rm -rf review-desk/build` and a precondition that `curl -sf http://127.0.0.1:7907/` fails, so the command builds and starts the close head's app itself. T2's acceptance ends by stopping the app it started.

## 3. Major: the `Host` refusal, sent as a curl post, never reaches the `Host` check

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:33-34,306-307`
- **Defect:** Close step 3 makes both refusals "`curl` posts". In the built app, `internal_respond` runs the CSRF check (`respond.js:101-131`) before `handle` runs. `curl -d` sends a form content type and no `Origin`, and `is_csrf_forbidden` refuses a null `Origin` (`request_origin !== self_origin`). So a post with `Host: evil.example:7907` gets SvelteKit's 403 before the hook runs. Step 4 passes even when the `Host` check is missing or wrong. The origin post has the same gap in reverse: a 403 there doesn't show which check refused it.
- **Fold:** Send the `Host` refusal as a GET: `curl -s -o /dev/null -w '%{http_code}' -H 'Host: evil.example:7907' http://127.0.0.1:7907/` must print 403. Assert that the origin post's body is `Cross-site POST form submissions are forbidden`. Step 3's Playwright clicks already provide the positive control: Chromium sends `Origin: http://127.0.0.1:7907`, and the post succeeds.

## 4. Major: "shows a Decided state" contradicts "a decided id returns 404"

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:223-226`
- **Defect:** SvelteKit re-runs the page's `load` after an action. `page/index.js:61-182` runs the action, then `load_server_data`, and `use:enhance` invalidates after it too. If a decided id returns 404 from `load`, the post that decides the item renders a 404 page, never the "Decided" state. The executor has to pick one promise and break the other. The test (line 240) only covers the action ("an action on a decided item fails with 404"), so the conflict goes unseen until Geoff clicks.
- **Fold:** Restate the outcome. An unknown id returns 404 from `load`. A decided item's page loads with 200 and shows the "Decided" state with no form. An action on a decided or unknown id returns 404. Add one test: `load` on a decided item returns its decided state.

## 5. Major: the loopback bind, the design's first security promise, is never checked

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:76-78,253-258,268-274,24-34`
- **Defect:** A probed fact says adapter-node defaults to `0.0.0.0`, and the design promises "binds loopback only". T3's test stubs `curl` as already running, so the `HOST=127.0.0.1` start line is never run or asserted. The end-to-end check tests `Host` and `Origin` but not the bind. Drop `HOST` and every criterion still passes.
- **Fold:** Add an end-to-end step after the command starts the app: `ss -ltnH 'sport = :7907'` shows `127.0.0.1:7907` and no `0.0.0.0` or `*` listener.

## 6. Major: the CSP has no acceptance check and no test

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:92-98,183-184,232-243`
- **Defect:** The plan sets `kit.csp.directives` to block script that a PR body (external input) could inject past CSRF. No criterion checks that the policy is sent or works. A typo, or a config that doesn't apply to the rendered pages, passes every gate. The `'self'` spelling itself is fine: `csp.js:20,269` quotes `self`.
- **Fold:** Add to T2's acceptance: `curl -sI` of an item page shows a `content-security-policy` header with `script-src 'self' 'nonce-`. Seed one PR item whose `body.md` holds `<img src=x onerror="document.title='pwned'">`, and confirm with Playwright that the title stays unchanged, or that the console reports a CSP violation.

## 7. Major: T4's hand-over assumes a waiting session, and its acceptance can't tell

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:280-293`
- **Defect:** The design's outcome needs the handing-over session to still be alive when the command exits. Pass prompts, this one included (prompt `:44-45`), end the session after `notify-send`, which strands the background command, and they say "Never merge the PR". T4's text doesn't say that the session stays open until the command exits, or that approving on the desk is what authorizes the session's merge. The acceptance greps only for the string `review-desk` and for zero `gh pr view`. A text that names the command once in each place, with no wait, merge, or reject behavior, still passes.
- **Fold:** T4's outcome adds one sentence: the handing-over session stays open until the command exits, and an approve on the desk is the merge authorization that the launch prompt's "never merge" otherwise withholds. The acceptance greps for each behavior by a stable phrase: the wait, `gh pr merge`, fix forward on reject, and acting on the triage rows.

## 8. Minor: the diff classifier test doesn't name the labels it expects

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:240-242`
- **Defect:** "labels `+x`, `-x`, ... `+++ b/`, and `--- a/` lines" never says which label each line gets. A classifier that labels `+++ b/` as added and `--- a/` as removed, the usual ordering bug, passes.
- **Fold:** Name the expected labels: `+x` added, `-x` removed, `@@ ... @@` hunk, and `diff --git`, `+++ b/`, `--- a/` all file header. A context line gets context.

## 9. Minor: T4 cites a prose net the gate doesn't run

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:293`
- **Defect:** "its tellgrader and Vale nets read the prose" is false. `scripts/check.sh` runs `make -C .../tellgrader check` (go vet, lint, and test) and `tests/vale/run-fixtures.sh` (style fixtures), and neither reads `SKILL.md`. The prose nets are the `PostToolUse` hooks (`settings.json:93-112`: `vale-hook`, `tellgrader --hook`), which fire on the edit. `dotfiles-pass` "Close checklist" makes the same claim.
- **Fold:** T4's acceptance reads "the `PostToolUse` Vale and tellgrader hooks report nothing on the edit". Add the adapter's wrong sentence to "Found, not done" with the disposition `now`.

## 10. Minor: the pair contract leaves the state root and `created` underspecified

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:128-133,256-257`
- **Defect:** "State root" could mean `.../review-desk` or `.../review-desk/items`. T3 passes it as `REVIEW_DESK_STATE` and puts `server.log` there, while T1's store reads items under it. The format of `created`, which T1 sorts on and T3 writes, is never fixed. T2 and T3 are built in parallel against this text, and only the end-to-end check would catch a mismatch.
- **Fold:** State that `REVIEW_DESK_STATE` is `${XDG_STATE_HOME:-$HOME/.local/state}/review-desk`, items live under `items/`, and `server.log` sits beside them. State that `created` is an ISO 8601 UTC string (`date -u +%Y-%m-%dT%H:%M:%SZ`). T3's test asserts the item id matches `^\d{8}T\d{6}-\d+$`, the matcher in `src/params/id.ts`.

## 11. Minor: "a screenshot shows the Survey fonts and colors" is self-graded and subjective

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:28-29,234-236`
- **Defect:** The session grades its own screenshot. A page whose theme failed to load, but which looks plausible, passes. T1's built-CSS check shows the theme was bundled, not that the page uses it.
- **Fold:** Add a Playwright `evaluate` at the close: `getComputedStyle(document.body).backgroundColor` is `rgb(247, 247, 243)` and its `fontFamily` names Karla or Spectral. Keep the screenshot as the human-readable record.

## 12. Minor: "Each opens a Firefox tab" names no evidence

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:28-29,305-306`
- **Defect:** The session drives Chromium and cannot see Firefox, so step 2's Firefox claim has no observation behind it.
- **Fold:** State the evidence: T3's stub test records `firefox --new-tab <item url>`, and in the end-to-end run a wrapper or `pgrep -a firefox` shows the call. Or reword the criterion to "the command invoked `firefox --new-tab` with the item URL".

## 13. Minor: the real PR's body may be empty

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:27,303`
- **Defect:** Close step 2 opens the draft PR with no stated body. With an empty or one-line body, "the summary, rendered" passes on nothing.
- **Fold:** Open the draft with the PR body skeleton (headings plus the "Found, not done" list), so the hand-over renders a heading and a list.

## 14. Minor: the design hand-over goes in the wrong pass-core section

- **Tag:** optional
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:286-288`
- **Defect:** Design approval happens at pass-core "Lifecycle" step 1 ("Geoff approves a design ... brainstorms in chat"), but T4 adds the `review-desk design` sentence to "Close". A session at the design step never reads it.
- **Fold:** Put the design hand-over sentence in Lifecycle step 1, and keep the PR and triage hand-overs in "Close".

## 15. Minor (over-ceremony, about 10 minutes): visual and library tests that duplicate other checks

- **Tag:** optional
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:233-236,242-243`
- **Defect:** T2's subagent takes a Playwright screenshot of each item page, and Close step 3 repeats the same evidence on the close head, which is the only head that ships. The `markdown.ts` test (heading, list, fenced code) tests `marked`, not this code.
- **Fold:** T2's acceptance keeps the curl 200s plus the CSP header from finding 6 and drops its screenshots. Replace the `markdown.ts` test with nothing, or with the CSP test from finding 6.

## 16. Minor: the gate's skip branch has no check

- **Tag:** optional
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:197-200`
- **Defect:** Every gate run in this pass has a `review-desk/` diff, so the "prints a one-line skip otherwise" branch never runs before main.
- **Fold:** At the close, run the condition once against a commit whose tree matches `origin/main` under `review-desk/` (`git diff --quiet <merge-base> -- review-desk` on a clean ref), or accept it as untested and say so in the PR body.

## 17. Minor: the clock framing

- **Tag:** optional
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:36-38`
- **Defect:** The plan calls 255 task-minutes "inside the design's 3 to 3.5 hours plus 45 minutes of margin". That is the design's upper bound plus margin, not inside the estimate. It sits well under pass-core's twice-the-estimate return line, so nothing has to change but the wording.
- **Fold:** Say "255 task-minutes against the design's 180 to 210, under the 2x line".

## Delivered against the design

Covered: the index, the three item kinds, the decisions (Approve, Reject with a note, Submit), the home outside Stow, the stack and the Survey copy, self-hosted fonts, the command's write, start, open, wait, and print, the `Host` check, the CSRF default, the gate leg, and pass-core's hand-over. Missing a working check: loopback (finding 5), the `Host` refusal (finding 3), and the waiting session (finding 7). Beyond the design but needed: the CSP (it blocks the probed `marked` script path) and the id matcher (validation at the URL boundary). Neither is over-scope. The design's "from a scratch session" runs from the pass session instead; the commands are the same, so this is not a finding.
