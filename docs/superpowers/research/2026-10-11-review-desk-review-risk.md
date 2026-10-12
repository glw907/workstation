Data integrity and failure risk review of `docs/superpowers/plans/2026-10-11-review-desk.md` and its launch prompt, at commit 0fd53f5 (`worktree-review-desk-lean`).

Mechanisms checked from source or a harmless probe, not memory:

- SvelteKit 3.0.1 `src/runtime/server/csrf.js` `is_csrf_forbidden`: a form-content (or no-content-type) mutating request is refused when `Origin` differs from the self origin, a missing `Origin` included. `respond.js:101-133` runs this before `handle`, and only when `!__SVELTEKIT_DEV__`. The plan's CSRF facts hold.
- `~/.claude/settings.json` sets `worktree.baseRef: "head"`, so the launch prompt's "new branch from local HEAD" holds.
- `flock` is on PATH (`/home/linuxbrew/.linuxbrew/bin/flock`).
- Probe: a background Bash command that runs `setsid -f sleep 25` and then exits is reported complete at once (start and exit share the same epoch second). The harness watches the process exit, not EOF on the pipe, so a detached child that keeps the command's stdout cannot hang the wake-up.

No finding is an OWNER FORK. Each fold is plan-level and leaves the design as approved.

## Major

### 1. Raw HTML in a rendered PR body can forge an approve on the same origin, and the CSP does not stop it

- **Severity:** major. **Tag:** correctness.
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:92-98` (Probed facts, "Rendered markdown needs the CSP"), `:183-184` (T1 CSP), `:227` (T2 `markdown.ts`), `:242-243` (T2 markdown test).
- **Defect:** the plan says `marked` passes raw HTML through, and it relies on `script-src 'self'` alone as the defense. That stops scripts. It does not stop injected markup that needs no script. A PR body can carry `<form method="post" action="?/approve"><button class="btn btn-error">Reject</button></form>`. That form posts from the app's own origin, so it passes the CSRF check. The body can also carry a `<style>` that hides the real decision buttons, since `style-src` is open. Geoff clicks what reads as Reject, the command prints `{"decision":"approve"}`, and under T4 the session runs `gh pr merge`. PR bodies are external input. Dependabot bodies, for example, embed upstream release notes. This is the forged-decision path the plan says it closes, and it stays open.
- **Fold:** in `markdown.ts`, render raw HTML tokens as escaped text: `marked.use({ renderer: { html: ({ text }) => escapeHtml(text) } })`, applied to block and inline HTML alike. Keep the CSP, which still blocks `javascript:` links. Add one T2 test: `<form>`, `<style>`, and `<script>` in the input come out as literal text, with no element. Rewrite the Probed-facts paragraph to say the escape is the defense and the CSP is the backstop.

### 2. The command trusts any listener on 7907, so an item can go to an app that cannot see it, and the command then waits forever

- **Severity:** major. **Tag:** correctness.
- **Location:** `:253` (T3 step 2, "Starts the app unless `curl -sf http://127.0.0.1:7907/` succeeds"), `:233-234` (T2 acceptance starts a built app on 7907 with a temp `REVIEW_DESK_STATE` and never stops it), `:303-308` (Close step 3).
- **Defect:** the app reads its state root once, from the environment it started with. The command writes the item under its own `XDG_STATE_HOME`. If whatever answers on 7907 was started with a different root, it serves 404 for the new item. The command never sees a decision and polls with no bound. That can be the T2 subagent's leftover app (temp root), the e2e app (temp root, see finding 3), an old build after a merge (the "Later" case), or an unrelated service. The first real hand-over after the pass is exposed whenever any of these survives.
- **Fold:** in T3, once the app answers (started now or found running), run `curl -sf http://127.0.0.1:7907/item/<id>`. If that fails, exit 1 with "an app on 7907 does not serve this state root; stop it (pkill -f review-desk/build)". Add a test case with a `curl` stub that answers `/` but fails `/item/`. T2 acceptance ends by stopping the app it started. Close step 3 starts by confirming nothing answers on 7907.

### 3. The Close's `pkill` pattern misses the app's real command line, so the e2e app outlives the pass

- **Severity:** major. **Tag:** correctness.
- **Location:** `:254` (app found at `<script dir>/../../../review-desk`, started as `node <app>/build`), `:308` (`pkill -f '<worktree>/review-desk/build'`).
- **Defect:** unless the command normalizes the path, the node process's argv reads `<worktree>/bin/.local/bin/../../../review-desk/build`. The fixed string `<worktree>/review-desk/build` is not a substring of that, so `pkill` matches nothing and the app keeps running. It serves the temp state root, from a worktree that close-out may later delete. When Geoff merges and runs his first hand-over, `curl /` succeeds against this orphan, and finding 2's hang follows.
- **Fold:** T3 resolves the app directory to a canonical path (`app=$(cd -P "$script_dir/../../../review-desk" && pwd)`). Close step 3 then confirms the stop: after `pkill`, `curl -s http://127.0.0.1:7907/` must fail. The "Later" recipe `pkill -f review-desk/build` (`:332`) matches either form and can stay.

### 4. A waiting command that dies leaves its item live, and Geoff's decision on it goes nowhere

- **Severity:** major. **Tag:** correctness.
- **Location:** `:260` (T3 step 4, the poll), `:187` (the index lists "an `item.json` and no `decision.json`"), `:334` ("Later": nothing prunes).
- **Defect:** the command is a child of the session. If the session closes, the background task is stopped, the session compacts, or the machine reboots, the command dies and the item stays on the index. Geoff can open it and decide, the app writes `decision.json`, and nobody reads it. The decision is lost without any sign: the page shows "Decided" as usual. Because nothing prunes, these orphans pile up beside live items.
- **Fold:** in T3, once `item.json` exists, set `trap 'rm -f "$dir/item.json"' EXIT` and `trap 'exit 143' TERM HUP INT`. Bash runs the EXIT trap on `exit`, and the signal traps turn a stop into an `exit`. The index then drops the item when its waiter dies. Removing `item.json` after a decision is harmless too, since a decided item is already hidden. SIGKILL and power loss still leave an orphan, which is a fair "Later" note. Add one test: TERM the backgrounded command and assert `item.json` is gone.

### 5. An approve is not bound to the diff Geoff saw

- **Severity:** major (high consequence, low likelihood). **Tag:** correctness.
- **Location:** `:99-101` (gh facts), `:128-138` (Interfaces: `item.json` and the decision carry no head commit), `:280-285` (T4: on approve, `gh pr merge <n> --merge`).
- **Defect:** the merge takes whatever head the PR has at merge time. Several things can make that differ from the diff Geoff approved. A stale or duplicate item for the same PR may still be listed (finding 4, or a re-hand-over after a fix-forward). Something may push to the branch while the command waits. Or the body and diff, fetched by two separate `gh` calls, may straddle a push. In each case an approve can merge code Geoff never saw into `main`, and `main` stows into the live workstation. The approve is the only human gate.
- **Fold:** T3 fetches `headRefOid` in the same `gh pr view --json body,headRefOid` call, stores it in `item.json` as `head`, and has the PR item page show the short SHA. The command prints the decision with `head` merged in (`jq -c --arg h "$head" '. + {head: $h}'`). T4 merges with `gh pr merge <n> --merge --match-head-commit <head>`. Update Interfaces and T3's test (assert `head` in the output).

## Minor

### 6. A first-run build race when T4's PR and triage hand-overs start together

- **Severity:** minor. **Tag:** correctness.
- **Location:** `:254-258` (build when `build/index.js` is absent: `npm ci` then `npm run build`), `:281-283` (T4 hands over the PR, then the triage list, both as background commands), `:335-336` ("Later": start race).
- **Defect:** on the first hand-over after the merge, and after every "Later" rebuild, two commands can both find the build missing. Both then run `npm ci` in `~/.dotfiles/review-desk`. `npm ci` deletes `node_modules` while the other build is reading it. One hand-over fails under `set -e`, and `node_modules` or `build/` can be left half-written. T4 makes this the expected sequence, not a corner case.
- **Fold:** wrap the check, build, and start section in `exec 9>"$state_root/start.lock"; flock 9` and close fd 9 after the start poll. This also settles the "Later" start race, so that item can drop from the list.

### 7. Temp files must live in the target directory, or the writes are not atomic

- **Severity:** minor. **Tag:** correctness.
- **Location:** `:130-132` (Interfaces, temp file and `mv` or rename), `:188` (T1 decision write), `:251-252` (T3 `item.json`).
- **Defect:** `/tmp` is tmpfs on this machine and the state dir is under `$HOME`. An app temp file made with `os.tmpdir()` fails `rename` with `EXDEV`, so the decision write throws. A command temp file made with bare `mktemp` turns `mv` into copy-then-unlink, and the app can list a half-written `item.json`. Both are the obvious defaults for an executor.
- **Fold:** state it in Interfaces: the temp file goes in the item directory itself (`item.json.tmp`, `decision.json.tmp`, or `mktemp -p "$dir"`).

### 8. Build and Firefox output lands in the decision output

- **Severity:** minor. **Tag:** correctness.
- **Location:** `:254-259` (T3 steps 2 and 3), `:127` ("prints the decision JSON on stdout"), `:273-274` (the test asserts "exactly that JSON" with silent stubs).
- **Defect:** `npm ci`, `npm run build`, and `firefox` (Gtk warnings, or a full Firefox when none is running) write to the command's stdout and stderr. The background task's output is then several lines of noise before the JSON, and the stubbed test cannot catch it. The probe shows this is pollution only: a detached child does not delay the wake-up.
- **Fold:** send the build and the `firefox` launch to `"$state_root/server.log"` (`>>"$log" 2>&1`), so the decision is the command's only stdout.

### 9. Triage rows should keep their item text from disk, not from the form

- **Severity:** minor. **Tag:** correctness.
- **Location:** `:223-225` (T2 `submit` "sends every row"), `:137-138` (decision rows "as Geoff left it").
- **Defect:** if `submit` rebuilds rows by zipping parallel form arrays (`item[]`, `disposition[]`, `reason[]`), a missing or reordered field moves a disposition onto the wrong item. A posted `disposition` outside the enum also reaches the session as-is. The form is the system boundary, where validation belongs.
- **Fold:** `submit` reads `triage.json` and takes the item text from it by index. From the form it takes only `disposition` (refused unless it is `now`, `defer`, or `drop`) and `reason`. If the posted row count differs from the file's, it returns 400.

### 10. Diff and triage text must render through text interpolation

- **Severity:** minor. **Tag:** correctness.
- **Location:** `:218-222` (T2 diff `<pre>` with colors by line, and the triage rows).
- **Defect:** colored diff lines are easy to build as an HTML string and print with `{@html}`. A diff is external input, so that reopens finding 1 through a second channel.
- **Fold:** one sentence in T2: diff lines and triage text render with `{line}` in a classed element, never `{@html}`. Only `markdown.ts` output, escaped as finding 1 folds it, goes through `{@html}`.

### 11. The e2e CSRF probe should prove which check refused it

- **Severity:** minor. **Tag:** optional.
- **Location:** `:33-34` (e2e step 4), `:307` (Close step 3).
- **Defect:** "gets 403" also passes if the `Host` hook, a 404 path, or some other error refuses the post. The CSRF check itself would go unproven.
- **Fold:** post form-encoded data (`curl -d`) with the correct `Host` to a live item's `?/approve`. Assert the body `Cross-site POST form submissions are forbidden`, and assert that no `decision.json` appeared.

### 12. The decision write is check-then-rename, not exclusive

- **Severity:** minor. **Tag:** optional.
- **Location:** `:188` (T1 write), `:225-226` (a decided id returns 404).
- **Defect:** two POSTs (a double click on a plain form, or two tabs) can both pass the "not decided" check. The second rename can then replace the first after the command has already read and printed it. Only one person uses the app, so the cost is low.
- **Fold:** publish with `fs.link(tmp, decisionPath)` and then unlink the temp file. `link` fails with `EEXIST` when a decision exists, so the action returns 404 and the first decision stands. It costs the same as `rename`.

### 13. An app crash during the wait has no recovery short of another hand-over

- **Severity:** minor. **Tag:** optional.
- **Location:** `:260` (T3 step 4).
- **Defect:** if the app dies while a command waits, the item is safe on disk, but Geoff's tab shows connection refused. The only restart is another hand-over.
- **Fold:** add it to "Later", not to the build. A one-line note is enough: re-running any `review-desk` hand-over restarts the app, and the waiting command then picks up the decision.

### 14. The T3 test's waits have no bound

- **Severity:** minor. **Tag:** optional.
- **Location:** `:268-274` (T3 test: "waits for `item.json`").
- **Defect:** a command bug that never writes `item.json`, or never exits, hangs the test. The gate then runs into the Bash tool's 10-minute timeout on every attempt, and two attempts burn about 20 minutes before the stop rule fires.
- **Fold:** bound each wait (for example 50 tries of `sleep 0.1`). On timeout, kill the background job and fail.

### 15. Say that the e2e approve is a test decision

- **Severity:** minor. **Tag:** optional.
- **Location:** `:303-306` (Close step 3), `:280-285` (T4's new "on approve, merge" text, which the worktree's `pass-core` will then carry).
- **Defect:** the session approves its own draft PR in the e2e, and the `pass-core` in its worktree, after T4, says "on approve, merge". The launch prompt's "never merge the PR" covers this, but one sentence at the point of action costs nothing.
- **Fold:** in Close step 3, add: "The e2e decisions are test decisions; the session acts on none of them."

### 16. Over-ceremony: T2's screenshot read duplicates the Close's

- **Severity:** minor. **Tag:** optional.
- **Location:** `:233-236` (T2 acceptance: a Playwright screenshot of each item page), against `:29` and `:303-306` (e2e step 2 screenshots of the same three pages).
- **Defect:** the subagent reads three image screenshots, and the Close reads three more of the same pages on the final head. The Close read is the binding one. The T2 read costs about 5 to 10 minutes and the image tokens of three reads, and catches nothing the Close would miss, since a styling defect found at T2 would also show at the Close.
- **Fold:** T2 acceptance keeps the `curl` 200 checks plus the built-CSS assertion T1 already has, and drops its screenshots. The Close's e2e screenshots are the visual check.
