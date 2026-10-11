# Fold record: review desk plan (fold agent, claude-opus-5-5, 2026-10-11, on 841fd1f)

Inputs: the three lenses (`review-mechanics` M, `review-contract` C, `review-risk` R) against
`docs/superpowers/plans/2026-10-11-review-desk.md` and its launch prompt. The design was not edited
and the revision changes none of its meaning, so no erratum is owed.

**Task minutes:** 315 after the verification findings below (T1 85, T2 80, T3 65, T4 25, close
60), up from 255 and under the 420 cap. Critical path about 250 minutes.

**Counts:** 54 findings: 48 folded (two in part), 6 refused, 0 owner forks.

## Dispositions

| Finding | Disposition | Where the revision carries it, or why not |
| --- | --- | --- |
| M1 (blocker) `svelte.config.js` fails the kit 3 build | folded | Probed facts "SvelteKit 3, the project files", config bullet; T1 `vite.config.ts`; Interfaces "Address"; Conventions "SvelteKit 3" |
| M2 param matcher location | folded | Same probed fact, matcher bullet (with the `~standard.validate` test form the probe needed); T1 Files `src/params.ts` |
| M3 other kit 3 removals | folded | Same probed fact: `#lib` imports, `$app/tsconfig`, `src/env.ts` plus `$app/env/private` (the probe found the build and vitest fail on an unset declared variable; the optional schema fixes both), `Handle` from `@sveltejs/kit/hooks` (found by the probe), `error()` string. `refreshAll` is not carried: the plan uses no `use:enhance` option |
| M4 "Decided" can never render | folded | Root for C4. T2 outcome (decided page loads 200 with no form; unknown id 404; actions on decided or unknown 404) and test; probed fact "After a form action, the page's `load` runs" |
| M5 worktree name collides | folded | Root for C1. Launch block and prompt use `review-desk-v1` |
| M6 Close serves T1's stale build | folded | Root with C2. Close step 3 starts with `rm -rf review-desk/build`; e2e step 2 |
| M7 port 7907 held by T2's leftover | folded | Root with C2 and R2. T2 acceptance stops its app; Close step 3 precondition; T3 step 3 item check |
| M8 `npm ci` only when absent; `marked` unnamed | folded in part | T1 installs every package, `marked` included; T2 and T3 change no `package.json`. Refused: dropping the prompt's T2 `npm ci` line, since a fresh pair worktree has no `node_modules` and its focused legs need one |
| M9 loopback bind and CSP unproven | folded | Root with C5 and C6. e2e step 4 (`ss ... awk '{print $4}'`, CSP header); T2 acceptance CSP header. The probe showed `ss` prints a `0.0.0.0:*` peer column on every listener, so the check reads the local column only |
| M10 built-CSS grep wrong | folded | T1 acceptance (`--color-base-100: ?#f7f7f3`, bundled `.woff2` with no `http`); probed fact "Survey core" quotes the build |
| M11 tellgrader and Vale don't read prose | folded | Root with C9. T4 acceptance names the `PostToolUse` hooks; probed fact "Gate"; "Later" carries the `dotfiles-pass` sentence |
| M12 `stow -R bin` not automatic | folded | Close step 7: Geoff runs it after the pull |
| M13 `created` format | folded | Root with C10. Interfaces "State" |
| M14 T3 test race on firefox record | folded | Root with R14. T3 test: every wait bounded |
| M15 diff classifier has no file | folded | T2 outcome and Files `src/lib/diff.ts` |
| M16 STATUS.md conflict (optional) | refused | Optional; a conflict stop is the existing rule and costs one resolution |
| M17 gate log tail (optional) | folded | Nearly free: T1's acceptance named evidence the 60-line tail may not show; it now reads `cairn-run-gate --records` |
| M18 close review loads `svelte-conventions` (optional) | refused | Optional, adds a load without removing ceremony |
| M19 `dependency-upgrade` for new packages (optional) | folded | One sentence, verified: every pin is its package's newest version (`npm view`, 2026-10-11), so no skill run is owed |
| M20 fold T4 into T3's subagent (optional) | refused | T4's text depends on T3's final interface (`head`) and C7's wait and merge sentences; the session writes it after the pair merges |
| M21 drop T2 screenshots (optional) | folded | Root for C15 and R16. T2 acceptance keeps the curl checks; the Close screenshots are the record |
| C1 (blocker) worktree name taken | folded | Via M5, plus a `worktree list` launch check and an exact-cwd `claude agents` check |
| C2 e2e serves T1's stale build | folded | Via M6 and M7 |
| C3 `Host` refusal never reaches the hook | folded | Probed on the built scaffold. e2e step 4: `Host` as a GET; the origin post asserts the CSRF body and no `decision.json` |
| C4 Decided contradicts 404 | folded | Via M4, with the `load` test |
| C5 loopback bind unchecked | folded | Via M9 |
| C6 CSP has no check | folded in part | Header check in T2 acceptance and e2e step 4. Refused: the Playwright `onerror` check, since R1's escape renders that payload as text and the check would pass with no CSP at all |
| C7 T4 assumes a waiting session | folded | T4 outcome: the session stays open until each command exits; a desk approve is the merge authorization; acceptance greps each behavior. Inside the design ("wakes the waiting session to act on it") |
| C8 diff labels unnamed | folded | T2 test names each label |
| C9 T4 cites a net the gate doesn't run | folded | Via M11; "Later" item with proposed disposition `now` |
| C10 state root and `created` underspecified | folded | Interfaces "State"; T3 test asserts the id pattern and `created` |
| C11 screenshot grading is subjective | folded | e2e step 2 computed-style check. The probe of the Survey core found the body class gap (the core applies `--font-body` to nothing) and the `survey-dark` `prefersdark` theme, so T1's `app.html` body takes the specimen's classes and the check accepts either base-100 |
| C12 Firefox claim has no evidence | folded | e2e step 2: T3's stub test is the evidence; Chromium opens the same URL |
| C13 real PR body may be empty | folded | Close step 2 opens the draft with the body skeleton |
| C14 design hand-over in the wrong section (optional) | folded | Reclassified correctness under Geoff's "a rule lives where it executes": a session at Lifecycle step 1 never reads "Close". T4 puts it in step 1 |
| C15 duplicate visual and library tests (optional) | folded | Via M21; the `markdown.ts` test now tests the escape, not `marked` |
| C16 gate skip branch untested (optional) | refused | Optional; the skip is a one-line `git diff --quiet` and fails safe toward running the legs |
| C17 clock framing (optional) | folded | The clock line was rewritten for the new total anyway |
| R1 raw HTML forges an approve | folded | Probed renderer; probed fact "Rendered markdown"; T2 outcome, acceptance (seeded `<form>` body), and test |
| R2 command trusts any listener | folded | T3 step 3 item check and its test case |
| R3 `pkill` misses the argv | folded | T3 canonical `realpath`; Conventions "Stopping an app". The probe also found `pkill -f <pattern>` from a Bash tool call kills the calling shell (exit 144); every stop uses the bracket form |
| R4 dead waiter leaves a live item | folded | T3 step 1 traps (probed), Interfaces "Waiting items", T3 test. Changed from the lens: the trap removes `item.json` only when no `decision.json` exists, so a decided page still loads and the decision post's own `load` cannot race the removal. "Later" notes SIGKILL |
| R5 approve not bound to the diff seen | folded | Interfaces, T3 (one `gh pr view --json body,headRefOid`, then the diff), T4 `--match-head-commit` (verified in `gh pr merge --help`). The page's short-SHA display is not carried: the binding does not need it |
| R6 first-run build race | folded | T3 step 2 under `flock` (probed); the "Later" start-race item is gone |
| R7 temp files must share the directory | folded | Interfaces "State"; probed fact "Desktop" (`/tmp` is `tmpfs`) |
| R8 build and Firefox output in stdout | folded | Interfaces "Command"; T3 steps 2 and 4 |
| R9 triage rows from disk | folded | T2 `submit` and its 400 tests |
| R10 no `{@html}` for diff and triage | folded | T2 outcome |
| R11 CSRF probe should prove its check (optional) | folded | Convergent with C3, folded at that root; the no-`decision.json` assertion is free |
| R12 exclusive decision write (optional) | refused | Optional; one user, and a decided item's actions already 404 |
| R13 app crash during a wait (optional) | refused | Optional; T3's item check and the stale-build "Later" note already name the recovery |
| R14 T3 test waits unbounded (optional) | folded | Convergent with M14, folded at that root |
| R15 e2e approve is a test decision (optional) | folded | C7's fold puts "a desk approve is the merge authorization" into the worktree's `pass-core`; Close step 3 says the e2e decisions are acted on by no one |
| R16 T2 screenshots duplicate (optional) | folded | Via M21 |

## Probes run

All in `/var/home/glw907/.claude/jobs/c01b6758/tmp/` (scratch, nothing left in the worktree; the
probe app is stopped and port 7907 is free).

1. **kit 3.0.1 source reads**, cited line by line in the plan's "SvelteKit 3, the project files":
   `config_file_unsupported` (`src/exports/vite/index.js:276-279`, `build-errors.js:247`), `$lib`
   removal (`:75-79`, `build-errors.js:527`), `files.params` (`src/core/config/index.js:180`,
   `create_manifest_data/index.js:110-111`, `src/core/params.js:58`), `defineParams` as a Standard
   Schema (`src/exports/params/index.js`), `$app/tsconfig` (`write_tsconfig/index.js:60`), env
   (`types/index.d.ts:1156-1177`, `src/runtime/env/dynamic/private.js:7`), `Handle`
   (`types/index.d.ts:1236-1245`), `error()` (`:1008`), load after action
   (`src/runtime/server/page/index.js:182`). Peers: `@opentelemetry/api` and `typescript` are
   optional.
2. **Scaffold probe** (`scaffold/`): `npm install` of the exact stack; the plan's file set
   (`package.json` with `imports`, `vite.config.ts`, `tsconfig.json`, `src/{app.html,app.css,env.ts,params.ts,hooks.server.ts}`,
   the Survey core, `#lib` modules, an item route with a matcher, `error` and `fail`).
   `svelte-kit sync && svelte-check`: first 5 errors (`Handle` not in `@sveltejs/kit`; the matcher
   not callable), then 0 after the fixes the plan records. `vitest run` and `vite build`: failed
   `env_invalid` with `REVIEW_DESK_STATE: {}` unset; passed with `schema: (value) => value ?? ''`.
   `vi.mock('$app/env/private', ...)` with a hoisted getter passed; `process.env` set before a
   dynamic import did not reach the module.
3. **Built app** on `HOST=127.0.0.1 PORT=7907`: `ss` local `127.0.0.1:7907` (peer column
   `0.0.0.0:*`); index 200; item page header `content-security-policy: script-src 'self'
   'nonce-...'`; raw `<img onerror>` rendered as `&lt;img`; bad id 404; GET with a foreign `Host`
   403 (hook); post with a foreign `Host` 403 with the CSRF body (runs before the hook); post with
   a foreign `Origin` 403 with the CSRF body; post with `Origin: http://127.0.0.1:7907` 200.
4. **Built CSS**: `--color-base-100:#f7f7f3` (no space), Spectral `src:url(./spectral-....woff2)`.
5. **`marked` 18.1.0 renderer**: `new Marked({ renderer: { html({ text }) { return escape(text) } } })`
   escapes block and inline `<form>`, `<style>`, `<script>` (vitest).
6. **Shell**: EXIT trap plus `trap 'exit 143' TERM` removes the file and exits 143 in 0.5 s;
   `flock` on fd 9 serializes two subshells. `pkill -f '<path>/build'` from a Bash tool call
   killed the calling shell (exit 144); `pkill -f '<path>/[b]uild'` stopped the app and left the
   shell.
7. **Environment**: `git worktree list` (shows `review-desk` on `worktree-review-desk`; no
   `review-desk-v1` worktree or branch); `findmnt /tmp` is `tmpfs`; `flock` at
   `/home/linuxbrew/.linuxbrew/bin/flock`; `gh pr merge --help` lists `--match-head-commit`;
   `gh pr view --help` lists `headRefOid`; `npm view` shows every pinned package at its newest
   version; the Survey core's `theme.css` (`survey` default, `survey-dark` `prefersdark`) and the
   specimen's body class; `scripts/check.sh:38,41` and `claude/.claude/settings.json` `PostToolUse`.

## Owner forks

No owner forks. C7's wait-and-merge text sits inside the design's "wakes the waiting session to act
on it" and "the session acts on the decision".

## Verification findings

From `2026-10-11-review-desk-fold-verification.md` (on 7246c66): 5 findings, all 5 folded, none
refused, no owner fork. T4 goes from 20 to 25 minutes; the total is 315.

| Finding | Disposition | Where the revision carries it, or why not |
| --- | --- | --- |
| V1 (blocker) the detached app inherits the start lock's fd 9 | folded | Reproduced (probe 1 below). T3 step 2 starts the app with `9>&-` and releases the lock with `exec 9>&-` once the app answers, before the item check and Firefox; probed fact "Shell mechanics" records the inheritance; e2e step 2 makes the second and third hand-overs the check. No T3 test case, since `curl` is stubbed as already running there |
| V2 (major) T4's merge rule must reach pass-core "Launch prompt" | folded | Verified: that section holds no merge or end text, and no skill or doc carries a "never merge" template, so each planner writes it fresh from that section. T4 outcome adds the sentence, and its acceptance greps it. This pass's own prompt keeps "never merge", since the tool is not live until the merge |
| V3 (minor) the e2e can miss the close head | folded | Close step 4: a fix chain touching `review-desk/` or `bin/.local/bin/review-desk` reruns step 3 on the new head |
| V4 (minor) the env fact does not quote its file | folded | Probed fact "Environment variables" quotes the probed `src/env.ts` with its module (`@sveltejs/kit/env`, `types/index.d.ts:1153`) |
| V5 (minor, optional) this pass's Close uses the old hand-over unexplained | folded | Nearly free, and it heads off a stop to ask: one clause in Close step 7 and one sentence at the end of the launch prompt, where the executor's authority sits |

### Probes run

1. `/var/home/glw907/.claude/jobs/c01b6758/tmp/fold2/flock/driver.sh`: a first subshell takes
   `flock` on fd 9, runs `setsid -f sleep 6`, closes fd 9, and exits; a second subshell's `flock -w
   2 9` printed "lock still held after 2 s". The same with `9>&-` on the `setsid` line and `exec
   9>&-` after: the second subshell "got lock" at once. The sleeps exit by themselves.
2. `grep -n` of `claude/.claude/skills/pass-core/SKILL.md` "Launch prompt" (line 193: goal, scope,
   plan path, checkout, `claude` line, prompt file; nothing on merging or ending) and of
   `claude/.claude/skills`, `.claude/skills`, and `claude/.claude/docs` for "never merge" (no hit).
3. `types/index.d.ts:1153` is `declare module '@sveltejs/kit/env'`; the scaffold's `src/env.ts` is
   the quoted file.

## S1 disposition

S1 (minor, optional): folded by the planning session. T4's acceptance searches a wrapped phrase with whitespace collapsed (`tr -s ' \n' ' ' | grep -c`), so a rewrap cannot fail correct text.
