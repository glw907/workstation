# Review desk UI: implementation plan

**Design:** `docs/superpowers/specs/2026-10-11-review-desk-ui-design.md` (approved by Geoff
2026-10-11, with unattended planning approved). No separate spec: the design is a page, and
`spec-plan-review` gives a design of a page or less none. **References:** the four approved
mockups in `docs/superpowers/specs/assets/2026-10-11-review-desk-ui/` and their sixteen renders in
`renders/` (`<mockup>-<light|dark>-<1440|390>.png`); the device and behavior catalogue
`docs/superpowers/research/2026-10-11-review-desk-ui-catalogue.md`; the mockups' accessibility
review `docs/superpowers/research/2026-10-11-review-desk-ui-a11y-review.md`. **Review:**
`docs/superpowers/research/2026-10-11-review-desk-ui-review-*.md` and the fold record
`docs/superpowers/research/2026-10-11-review-desk-ui-plan-fold.md`.

**Outcome.** The desk shows every waiting item in a queue beside the open item, each decision is a
key press or a click, a 5-second undo holds every decision in the page, the next item loads in the
same tab, and the empty state closes the tab. Every screen matches its mockup in light and dark.

**Pass class:** `runner` (Geoff, 2026-10-11, for the desk; `tests/review-desk.test.sh` is on the
`runner` map), with the `live-account` flag: the session pushes a branch, opens a PR on
`glw907/workstation`, reads it and cairn-cms #113 through `gh`, and merges its PR on Geoff's desk
approve. No `auth-data` path is touched.

**Out of scope** (design): one shared tab across hand-overs, the desk hardening in ROADMAP
"Someday", and any change to the `review-desk` command's protocol (its arguments, its stdout, its
exit codes). Also any edit to another repo; `~/Projects/cairn-cms` is read only, for its installed
Playwright.

**Judgment calls this plan makes** (none changes the design; each is recorded so the PR read can
see it):

1. **The command and the server change, outside undo.** The PR mockup's figures and meta line need
   the check runs, the PR number, URL, and branches, and the item store has only the body, head,
   and diff. The command's existing `gh pr view` call adds
   `number,url,headRefName,baseRefName,statusCheckRollup` and writes them to a new `pr.json`. The
   design says "Undo holds a decision in the page for 5 seconds before it posts, so the server and
   the `review-desk` command do not change." The plan reads that sentence as scoped to undo, which
   itself needs no server or command change. Read literally, the sentence would forbid the design's
   own Checks figure (only `gh`, in the command, supplies `statusCheckRollup`) and its queue beside
   the item (a layout load on the server). The design's out-of-scope line limits only the command's
   protocol. Every change the plan makes:
   - The command writes `pr.json`, and `number` or `file` in `item.json`.
   - The server gains a layout load of the queue and of `listDecided`, the `/` redirect to the
     oldest waiting item, and `pr.json` reads in the item store.
   - The decision actions return `{ next }`. It is computed on the server because a next item taken
     from the page's queue can be gone or already decided.

   The decision JSON and the command's arguments, stdout, and exit codes do not change.
2. **Class and review come from the PR body**, since nothing structured carries them. Class is the
   first `` class `<auth-data|runner|ordinary>` `` in the body, case-insensitive (workstation #13
   says ``Class `runner` ``, cairn-cms #113 says ``Risk class `auth-data` ``). Review is the
   body's `## Review` section, rendered in the mockup's Review slot. The Review figure shows that
   section's last backticked `` `accept` ``, `` `fix` ``, or `` `escalate` `` (bare words are
   prose: "one batched fix chain" is not a verdict), or "Not stated" when the body has no such
   section or token. Risk shows "Not stated" with no class, and Checks shows "No checks" for an
   empty or absent rollup.
3. **Where the mockup and the design disagree, the design wins.** A `## Before merge` section shows
   as an `alert alert-warning` in the decision bar's guard slot, beside Approve (the mockup has
   none). A failing check and a `fix` or `escalate` verdict take `--cairn-error-ink` (the mockup
   shows neither). Figure labels follow the mockup: Risk, Checks, Review, Changes.
4. **Mockup defects are fixed, never copied** (visual-fidelity's standing sanction). The figures
   row wraps at phone width; the catalogue measured the mockup's row at 636 px on a 390 px screen.
   `?` toggles the sheet, as the sheet says. `/` is listed under PR only. A held decision ignores
   every decision key: `a`, `r`, `1`, `2`, `3`, and Ctrl+Enter (`requestSubmit()` submits even with
   the buttons disabled). `↓` from outside any row focuses the first row. Every kbd takes the
   borderless style of three of the four mockups. The countdown uses DaisyUI `countdown`, and each
   diff table gets an `aria-label` (a11y review findings 14 and 15). The countdown carries no
   `aria-live` or `aria-label`, though the DaisyUI guide adds both: a11y finding 4 keeps the
   per-second count out of any live region, and the one announcement goes through `#sr-status`.
5. **Mockup content without a data source is left out:** the design page's guard text ("Approved
   in the doc on ...") and the hand-written verdict notes. "Decided this session" lists the items
   decided since the app started, which the item store can answer.
6. **What the mockup leaves to a full page load, the build states.** In the mockup a queue click
   during the hold is a full page load, which drops the hold; in the build it is a client
   navigation, so a `beforeNavigate` cancels a hold that is still counting and announces "Undone.
   Nothing was sent." A post that fails (the item was decided in another tab, the app is down)
   unlocks the controls and replaces the toast with "Not sent: <message>", announced, with focus
   back on the deciding button and no navigation. A decided item keeps the existing "Decided"
   state in place of the bar. The next item is computed on the server when the decision is
   posted, so a stale queue in the page never picks it.

**End-to-end check.** On the close head, from the pass worktree (Close step 3), inside "Running
the app":

1. `bash scripts/gate.sh` prints `gate exit: 0`.
2. With a temp `XDG_STATE_HOME` and a `firefox` stub first on `PATH` that records its URL, the
   worktree's `bin/.local/bin/review-desk` hands over `glw907/cairn-cms` #113 (read-only `gh`
   reads; the PR mockup's own subject: `auth-data`, 12 checks with one skipped, a Review section
   ending in `` `accept` ``), the design doc above, and a three-row triage list proposed `now`,
   `now`, `defer`, in that order. Each hand-over runs in the background with its stdout, stderr,
   and exit status written to files in the temp dir, and each starts only after the previous one's
   `item.json` exists and one more second has passed. The first finds no build and nothing on
   7907, so it builds and starts the close head's app.
3. A Playwright script (Chromium) opens the PR's recorded URL in a new page by
   `location.replace` from `about:blank`, so the tab starts with one history entry, and asserts
   `history.length === 1` and the queue's rows in the order PR, design, triage. Then, by key: `a`
   shows the toast with Undo focused; `z` returns focus to Approve, `#sr-status` reads "Undone.
   Nothing was sent.", and no `decision.json` exists at 6 seconds; `a` again leaves no
   `decision.json` and the PR command running at 4 seconds, and by 8 seconds the command has
   exited 0 printing `{"decision":"approve","head":"<sha>"}`; the page then shows the design at
   its item URL with `history.length === 1`. On the design, `r`, a typed note, and Ctrl+Enter post
   a reject that carries the note. On triage, row 2 takes `3`, its reason is edited in place, and
   Ctrl+Enter is pressed from the reason field; the status line reads `3 items, 1 changed from
   proposed` before the post, and the command prints row 2 as `drop` with the typed reason and rows
   1 and 3 as proposed. The page shows the empty state with Keep focused, and after 30 seconds the
   page's `close` event fires.
4. A second round, sequenced the same way on round 1's temp `XDG_STATE_HOME` and app, hands over
   this pass's draft PR, a fresh design, and a fresh triage item of the same three rows, and takes
   each decision by click: Approve; Reject, a note, and Send rejection; row 1's "Move to" menu set to Defer, and Submit. The commands print
   the approve, the reject with the note's text, and row 1 as `defer`.
5. With nothing waiting, `timeout 60 /usr/bin/firefox --headless --no-remote --profile <temp dir>
   http://127.0.0.1:7907/` exits 0, not 124, once the temp dir holds a `user.js` that turns the
   first-run tab off (`browser.aboutwelcome.enabled`, `browser.shell.checkDefaultBrowser`,
   `datareporting.policy.dataSubmissionEnabled`, and `toolkit.telemetry.reportingpolicy.firstRun` false;
   `browser.startup.homepage_override.mstone` "ignore"; `startup.homepage_welcome_url`,
   `startup.homepage_welcome_url.additional`, and `datareporting.policy.firstRunURL` empty). Without
   it a fresh profile opens a welcome tab, closing the empty-state tab leaves that tab open, and the
   run times out at 124 (found at the close of PR #22): real Firefox closes the empty-state tab, and closing
   its only window quits it. The absolute path skips step 2's stub, so the check cannot pass
   against it, and `--no-remote` keeps the run out of Geoff's running Firefox.
6. The bind, CSP, and `Host` checks of the first desk pass still hold: `ss -ltnH 'sport = :7907'`
   prints `127.0.0.1:7907`, `curl -sI` of an item page shows `script-src 'self' 'nonce-`, and a GET
   with `Host: evil.example:7907` gets 403.
7. `visual-verifier` passes each screen against its mockup in light and dark, and
   `daisyui-a11y-reviewer` and the Blueprint quality inspector find no blocker, with every a11y
   finding carried (Close step 4).

**Clock estimate:** 245 task-minutes (T1 20, T2 35, T3 65, T4 55, close 70), against the design's
2 hours: 5 minutes over twice it, the 240 limit, so the plan goes back to Geoff before launch
(pass-core "Plan"). The review folds added about 20 minutes of criteria, folding T5 into T4 saved
one pair subagent's setup and screenshot loop, and the fold verification's per-item state check
added 5 minutes to T3. The first desk pass ran 68 minutes of clock against 315 planned. T1 and T2
run as a pair, so the path is about 35 + 65 + 55 + 70 = 225 minutes.

## Launch

Prompt file: `docs/superpowers/plans/2026-10-11-review-desk-ui-prompt.txt`. The plan lives on
branch `worktree-desk-ui-plan` (planning commits on top of the design branch
`worktree-desk-ui-design`). The executing session works in a new worktree, `desk-ui-build`, and
its first act after `EnterWorktree` is `git merge --no-edit worktree-desk-ui-plan`. Launch from
the main checkout, after every check prints what its comment names:

```bash
git -C ~/.dotfiles fetch origin
git -C ~/.dotfiles branch --show-current                # must print main
git -C ~/.dotfiles rev-list --count HEAD..origin/main   # must print 0 (not behind)
git -C ~/.dotfiles rev-list --count origin/main..HEAD   # must print 0 (not ahead)
git -C ~/.dotfiles status --porcelain                   # must print nothing
git -C ~/.dotfiles rev-parse worktree-desk-ui-plan origin/worktree-desk-ui-plan   # two equal lines
git -C ~/.dotfiles worktree list | grep -c '/worktrees/desk-ui-build '   # must print 0
claude agents --json                                    # no live session whose cwd is ~/.dotfiles/.claude/worktrees/desk-ui-build
cd ~/.dotfiles && claude --bg --model sonnet --effort medium --name desk-ui-build \
  "$(git -C ~/.dotfiles show worktree-desk-ui-plan:docs/superpowers/plans/2026-10-11-review-desk-ui-prompt.txt)"
```

The prompt is read with `git show` because the plan is not on `main` until this pass's PR merges.

## Probed facts

Each was read from source or run on 2026-10-11. A task builds on these, and on the first desk
plan's "SvelteKit 3, the project files", "adapter-node 6 host and port", "SvelteKit 3 origin and
CSRF", "Rendered markdown", and "Shell mechanics" facts
(`docs/superpowers/plans/2026-10-11-review-desk.md`), never on recall.

- **The HTML rule for `window.close()`.** HTML, "script-closable": "A navigable is script-closable
  if it is a top-level traversable, and any of the following are true: its is created by web
  content is true; or its session history entries's size is 1." The `close()` steps act only "If
  all the following are true: thisTraversable is script-closable; ...". A tab that
  `firefox --new-tab` opens is not created by web content, so it stays closable only while its
  session history holds one entry.
- **Firefox keeps the rule** (probe, Firefox 157.0.1, a headless instance on a scratch profile, the
  page loaded as the instance's first page). After three `history.replaceState` calls,
  `history.length` was 1, `window.close()` closed the tab, and Firefox exited 0. With one
  `history.pushState` first, `history.length` was 2, the tab stayed open (`window.closed` false),
  and Firefox ran until `timeout` killed it (124). Remoting `--new-tab` into a headless instance
  fails ("Firefox is already running, but is not responding"), so a probe loads its URL as the
  first page.
- **Chromium under Playwright** (probe, `/usr/bin/chromium-browser` with the Playwright 1.63.0
  package from `~/Projects/cairn-cms/node_modules/playwright`). `page.goto(url)` from a new page
  leaves `history.length` at 2 (`about:blank` stays an entry), and `window.close()` is refused.
  `page.evaluate((u) => location.replace(u), url)` from the new page leaves one entry, and the
  page closes on `window.close()` (the page's `close` event fires). The e2e opens its first page
  that way. The Playwright MCP server cannot drive a browser here: it looks for Chrome at
  `/opt/google/chrome`. The e2e and the renders use the npm package by absolute path:
  `require('/var/home/glw907/Projects/cairn-cms/node_modules/playwright')` and
  `chromium.launch({ executablePath: '/usr/bin/chromium-browser' })`, from a script in the job's
  tmp directory. That reads `~/Projects/cairn-cms` and writes nothing there.
- **SvelteKit 3.0.1 client navigation** (`node_modules/@sveltejs/kit`, quoted):
  - `goto` takes `replace`: "If `true`, replaces the current history entry rather than creating a
    new one" (`types/index.d.ts:2559-2562`). `replaceState` is deprecated ("`@deprecated Use
    replace instead`", `:2563`) and warns in dev (`src/runtime/client/client.js:2621-2623`).
    `refreshAll` "reruns all `load` functions" (`:2580-2583`); `invalidateAll` is deprecated for it.
  - The history write: `const fn = replace_state ? history.replaceState : history.pushState;
    fn.call(history, entry, '', url);` (`client.js:2118-2119`). The first load also calls
    `history.replaceState` (`:520`), never `pushState`.
  - A link click without an option pushes: `replace: options.replace_state ?? !changed`
    (`client.js:3249`). The option comes from a `data-sveltekit-replacestate` attribute on the link
    or any ancestor up to `<html>` (`utils.js:36`, the `while (el && el !== document.documentElement)`
    walk at `:177-192`). A same-page `#hash` link uses the browser default, a push, unless that
    option is set (`client.js:3190-3226`, `if (!options.replace_state) return;`). So the attribute
    goes on `<body>` in `app.html`, which covers the queue links and the figures' `#checks`,
    `#verdicts`, and `#files` links. An external link, or one whose `target` is not `_self`, is not
    routed (`:3146-3150`, `:3166`): a same-tab external link pushes, and `target="_blank"` leaves
    this tab's history alone.
  - A `load` that throws `redirect` during a client navigation re-navigates with the same
    `replace_state` (`client.js:2026-2042`), so `/` may redirect to the oldest waiting item.
  - `applyAction` on a `redirect` result calls `_goto(result.location, { refreshAll: true })`, a
    push (`client.js:2981-2982`). So no action redirects: the page posts through `enhance` and then
    calls `goto(next, { replace: true, refreshAll: true })` itself.
  - `enhance(form, submit)` awaits the submit function before it fetches
    (`src/runtime/app/forms/client.js`: `const callback = (await submit({ action, cancel, ... })) ??
    fallback_callback; if (cancelled) return;`). So the 5-second hold is the submit function
    awaiting a timer, and Undo calls `cancel()`. Without JavaScript the form still posts natively.
    `enhance` builds its `FormData` before it awaits `submit` (`:121-155`), so a value must be in
    the form's inputs when the submit starts.
  - A `failure` or `error` result reaches the callback: the response's `type` is kept with its
    status, and a fetch that throws (the app is down) becomes `{ type: 'error', ... }`
    (`forms/client.js:205-241`).
  - `beforeNavigate` runs "before we navigate to a URL, whether by clicking a link, calling
    `goto(...)`, or using the browser back/forward controls", and "remains active as long as the
    component is mounted" (`types/index.d.ts:2772-2780`); a same-route link click goes through it
    (`client.js:3176`). The callbacks run before the navigation changes `data`, so a callback in
    the keyed `ItemPanel` (T3) still belongs to the item being left.
- **`flock(1)` and the lock fd** (probe, util-linux 2.42.4, a scratch lock in the job's tmp
  directory). Without `-o`, a `setsid -f` child started under `flock <lock> -c ...` kept the lock
  after `flock` exited (a second `flock -w 2` timed out, exit 1); with `-o` ("Close the file
  descriptor on which the lock is held before executing command") the second `flock` got it at
  once, and the command ran with no fd on the lock. The command's own form, `exec 9>"$lock"; flock
  9`, waited about 2.5 seconds behind a `flock -o <lock> -c 'sleep 3'`, then went on.
- **GitHub data.** `gh pr view <n> -R <repo> --json body,headRefOid,number,url,headRefName,baseRefName,statusCheckRollup`
  returns all of these. A `statusCheckRollup` entry is a `CheckRun` (`name`, `workflowName`,
  `status`, `conclusion`, read from cairn-cms #113: `"conclusion":"SUCCESS"`, `"status":"COMPLETED"`,
  `"workflowName":"create-site"`) or a `StatusContext` (`context`, `state`). The mockup's check
  names are `workflowName / name` ("tool / make check (ubuntu-latest)"). A repo with no CI, like
  this one, returns an empty array. cairn-cms #113 is merged and still reads: 12 checks (11
  `SUCCESS`, 1 `SKIPPED`), a `## Review` section, no `## Before merge`, and 161 files in `gh pr
  diff`.
- **Binary files in a diff.** A new binary file is a `diff --git a/<p> b/<p>` header, `new file
  mode`, an `index` line, and `Binary files /dev/null and b/<p> differ`, with no `---`, `+++`, or
  hunk (`git diff origin/main...HEAD` on a render in this branch, which adds 16 PNGs).
- **Per-item state** (Svelte 5.57.2 docs, "{#key ...}"): "Key blocks destroy and recreate their
  contents when the value of an expression changes. When used around components, this will cause
  them to be reinstantiated and reinitialised." SvelteKit's load docs, quoted by the fold
  verification: rerunning `load` "will update the `data` prop ... it does _not_ cause the
  component to be recreated. As a result, internal state is preserved."
- **The EXIT trap under `flock -o`** (probe, a scratch lock and a `setsid` stand-in app). A
  `set -euo pipefail` script whose command failed partway ran its EXIT trap, which stopped the
  stand-in, and the lock was free after. On SIGTERM to the whole tree, `flock` died and freed the
  lock at once, while bash ran the trap only after its current foreground command ended (a 20-second
  `sleep` in the probe). So a run is never killed from outside: the e2e goes in a
  `run_in_background` task, clear of the Bash tool's ceiling.
- **The DaisyUI countdown guide** (`~/.claude/skills/daisyui/components/countdown.md:19`): "Add
  `aria-live="polite"` and `aria-label="{number}"`." Judgment call 4 overrides it.
- **The live desk.** At planning, the main checkout's app ran on 7907 (`node
  /var/home/glw907/.dotfiles/review-desk/build`) with nothing waiting in
  `~/.local/state/review-desk`. Port 7907 is fixed in three places (the command, `paths.origin`, and
  the `Host` check), so every task run and the e2e need the port, under "Running the app". The
  command writes `item.json`, then takes `<root>/start.lock`, starts an app if nothing answers, and
  releases the lock (`bin/.local/bin/review-desk:35-60`).

## Interfaces

Changes to the first desk plan's "Interfaces"; everything else there holds.

- **`item.json`** gains `number` (a PR, from `gh`'s `.number`) and `file` (a design, the source
  file's basename).
- **`pr.json`**, new, written by the command for a PR before `item.json`: the `gh pr view` JSON
  minus `body` and `headRefOid`, so `{number, url, headRefName, baseRefName, statusCheckRollup}`.
  An item written by the old command has no `pr.json`, `number`, or `file`; the app reads their
  absence as no checks, no link, and no number or file name, never an error.
- **Queue order:** waiting items list oldest first by `created`, then by `id`.
- **Next item:** each decision action computes it from the server's waiting list before it writes
  the decision: the item after the current one in queue order; if none follows, the oldest other
  waiting item; with none, null. It returns `{ next }`, and the page goes to `next ?? '/'`.
- **`localStorage`:** `desk.singleKeys` and `desk.autoClose`, each `on` or `off`, absent meaning
  `on`. Every read and write sits in `try`.
- **Decision JSON:** unchanged.

## Conventions every task follows

The first desk plan's "Conventions every task follows" hold (gate, SvelteKit 3, the main checkout
untouched, stopping an app, comments, UI, commits, clock, stops, scope), with these additions:

- **Running the app.** Every run of a worktree app on 7907 (a task's acceptance, its screenshot
  loop, and the e2e) happens inside `flock -o ~/.local/state/review-desk/start.lock bash <script>`,
  the live state root's lock, which the command takes before it starts an app. `-o` keeps the
  lock's fd out of the script, so no app it starts holds the lock (probed). The app is built
  before the lock is taken, so the lock is held only for the run; the e2e is the exception, since
  its step 2 tests the command's first build. A run that may pass the Bash tool's 600-second
  ceiling (the e2e) goes in a `run_in_background` task. The script, in order:
  1. If any item under `~/.local/state/review-desk/items/` waits (an `item.json` with no
     `decision.json`), it exits nonzero having touched nothing. The session waits until none waits
     and runs it again; a long wait ends in the clock stop.
  2. It sets an EXIT trap, with the first desk plan's `trap 'exit 143' TERM HUP INT` beside it,
     that stops the worktree app per "Stopping an app" and kills any hand-over PIDs the script
     recorded, so a failing assertion never leaves 7907 held after the lock is released (probed).
  3. It stops the live app with `pkill -f '/var/home/glw907/.dotfiles/review-desk/[b]uild'` (an
     exception listed below) and checks that `curl -s http://127.0.0.1:7907/` fails. If 7907 still
     answers, the script exits nonzero and the session applies "Stops".
  4. It starts the worktree app on a temp state root (the e2e lets its hand-overs start it) and
     waits until `curl -sf http://127.0.0.1:7907/item/<a seeded id>` answers.
  5. It runs the browser steps; the trap stops the worktree app on the way out.

  A hand-over that arrives meanwhile writes its `item.json`, blocks on the lock, and after the
  release starts the live app itself. The session never restarts the live app; the next hand-over
  does. The live state root is only read.
- **Exceptions to the main checkout staying untouched and to "Stopping an app".** Three, and only
  these: "Running the app" step 3 stops the main checkout's app; "What goes live" (Close step 8)
  stops it, runs `npm ci` and a build in `~/.dotfiles/review-desk`, and starts it, after the merge;
  and Close step 9 hands over with the `review-desk` on `PATH`, the main checkout's command.
- **Visual reference.** A UI task reads the catalogue's sections for its screens and opens the
  matching renders (light and dark, 1440 and 390) before writing markup, then works the canonical
  loop: build, screenshot with the Playwright pattern above, compare to the render, fix. The
  mockups are the reference, never code to copy: the CDN loads become the app's Tailwind build, and
  the desk layer's rules (the catalogue's "Desk layer" table, minus its dead rules) move into
  `src/app.css` or the component's `<style>`.
- **DaisyUI first.** Read the component guide in the `daisyui` skill before using a component
  (`drawer`, `menu`, `modal`, `stat`, `collapse`, `toast`, `alert`, `toggle`, `kbd`, `dropdown`,
  `countdown`, `badge`, `input`, `textarea`). Where a guide and an a11y review finding disagree,
  the finding wins.
- **Svelte.** Load `svelte-conventions` before writing a `.svelte` file, and run the Svelte MCP
  `svelte-autofixer` on each new component until it reports nothing.
- **Phone width.** No page scrolls sideways at 390 px.
- **Test-first** where a task names logic: the test is written and seen failing before the code.

## Tasks

### T1. The item store and the command

- **Outcome.**
  - `listWaiting` returns items oldest first by `created`, then `id`. A new
    `listDecided(root, since)` returns the items whose `decision.json` was written at or after
    `since` (epoch ms, from its mtime), newest first, each with its meta and its decision word
    (approve, reject, submit). A PR item's `readItem` content carries `pr.json`'s fields when the
    file exists.
  - The command's PR branch calls `gh pr view` with the fields in "Interfaces", writes `body.md`
    and `pr.json` from that one call, and adds `number` (from `.number`) to `item.json`; the design
    branch adds `file`. Nothing else in the command changes.
- **Files.** `review-desk/src/lib/server/items.ts` and its test, `bin/.local/bin/review-desk`,
  `tests/review-desk.test.sh`.
- **Risk class.** `runner` (`tests/**`).
- **Acceptance.** `npm --prefix review-desk test` and `bash tests/review-desk.test.sh` pass, then
  the gate prints `gate exit: 0`.
- **Test** (first). The store, over a temp root: three waiting items list oldest first (the
  existing "lists newest first" test at `items.test.ts:22` is flipped, not kept), and two with the
  same `created` list by `id`; two decided items whose `decision.json` mtimes are set with `utimes`,
  one before `since` and one after, list only the later one, with its decision word; a PR item with
  `pr.json` reads its `url` and checks, and an old-format PR item with no `pr.json` and no `number`
  reads with neither and no error. The command test: the `gh` stub's `view` prints canned JSON with
  every new field; the PR item has `pr.json` holding `url` and `statusCheckRollup` and no `body`,
  and `item.json` holds the stub's `number`; a design item's `item.json` holds `file`. The existing
  assertions still pass.
- **Pair.** Runs as a pair with T2 (disjoint files).
- **Estimate.** 20 minutes.

### T2. The page logic, as tested modules

- **Outcome.** Five modules under `review-desk/src/lib/`, each pure, each with its test:
  - `pr-summary.ts`: `riskClass(body)` per judgment call 2; `bodySections(body)` splits the body at
    `## ` headings into a lead and titled sections, leaving out `Before merge` and `Review`;
    `reviewVerdict(body)` per judgment call 2; `checksSummary(rollup)` gives passed, failed,
    skipped, and pending counts, the figure's text ("11 passed, 1 skipped", or "No checks" for an
    empty or absent rollup), and one row per check (`workflowName / name` or `context`, and its
    state: `SUCCESS` and `NEUTRAL` pass, `SKIPPED` skips, an incomplete `status` or a `PENDING` or
    `EXPECTED` state is pending, anything else fails).
  - `diff.ts` grows `fileGroups(diff)`: files grouped by first path segment (top-level files under
    "Repository root"), groups in path order, each file with its path (the `b/` side of its `diff
    --git` header), adds, dels, status (`new` for `new file mode`, `deleted` for `deleted file
    mode`), and rows of kind hunk, add, del, or context with old and new line numbers taken from
    each `@@ -a,b +c,d @@` header. A binary file lists with no rows and counts of 0. The existing
    `classify` stays.
  - `keys.ts`: `keyAction(key, mods, context)` returns the action for a key event, or null, per the
    catalogue's "Global key handler" order and "Key map" table with judgment call 4's fixes.
    `context` carries the page kind, whether the target is a typing target, whether single keys are
    on, whether the sheet is open, whether a decision is held, and whether the note is open.
  - `hold.ts`: `startHold(ms, { tick, fire })` returns `{ cancel }`; `tick` gets the whole seconds
    left once a second, `fire` runs once at the end, and `cancel` stops both.
  - `triage.ts`: `moveRow(rows, index, disposition)` changes only that row's `disposition` and
    never the array's order, `groupRows(rows)` derives the view (each section's rows in item-number
    order), and `changedCount(rows)` counts against each row's `proposed`.
  - `queue.ts`: `nextItem(queue, id)` per "Interfaces".
- **Files.** Those modules and their tests.
- **Risk class.** `ordinary`.
- **Acceptance.** `npm --prefix review-desk test` passes, then the gate prints `gate exit: 0`.
- **Test** (first). `riskClass` reads both real phrasings and returns null with none. `bodySections`
  on a body with a lead, `## What landed`, `## Review`, and `## Before merge` returns the lead and
  one section. `reviewVerdict` returns `accept` for cairn-cms #113's wording ("first ... `fix` ...
  Second whole-branch review after the fix: `accept`"), stays `accept` when prose "fix chain"
  follows the backticked `accept`, returns `fix` when a backticked `fix` comes last, and returns
  null with no Review section. `checksSummary` on 11 successes and 1 skip gives "11 passed, 1
  skipped", a `FAILURE` counts as failed, a `StatusContext` with `state` `FAILURE` fails, and `[]`
  gives "No checks". `fileGroups` on a fixture diff of a top-level file, a new file, a deleted
  file, a two-hunk file, a binary new file, and a rename gives the groups, the paths, the counts,
  and the right line numbers on each side of a hunk. `keyAction`: `a` approves on a PR and not on
  triage; plain Enter on triage returns null; every single key returns null with single keys off
  or while typing; Escape and Ctrl+Enter work with single keys off; `a` and Ctrl+Enter return null
  while a decision is held; `?` returns toggle-sheet with the sheet open. `startHold` under
  `vi.useFakeTimers()` ticks 4, 3, 2, 1, fires once at 5 s, and never fires after `cancel`.
  `moveRow` leaves the array's item order as it was, `groupRows` keeps item-number order inside a
  section, and `changedCount` drops back to 0 when a row returns to its proposal. `nextItem`
  returns the next item, then the oldest other one when the current is last, then null.
- **Pair.** Runs as a pair with T1.
- **Estimate.** 35 minutes.

### T3. The shell: queue, keys, undo, and the empty state

- **Outcome.**
  - `app.html`'s `<body>` carries `data-sveltekit-replacestate`. `+layout.server.ts` loads the
    queue (`listWaiting`) and the decided list (`listDecided` since the server module's start
    time). `+layout.svelte` is the catalogue's page skeleton: the drawer open from `lg`, the queue
    (header, rows with kind, repo and number, age, and title, the selected row, the empty row,
    "Decided this session", the footer with the shortcut button, the collar), the mobile `<header>`
    navbar, the shortcut sheet with the single-keys switch, the `sr-only` status region, and the
    toast. One `keydown` listener on `document` dispatches `keyAction`. The drawer, j/k, the sheet,
    and every focus move follow the catalogue's "Behavior" section. A queue row omits the number
    when the item has none.
  - `src/app.css` carries the desk layer's shared rules: the global `:focus-visible` ring, the
    queue row grid, the kbd style, `.desk-field`, the `desk-no-sk` hide rule, `scroll-padding-bottom`
    from `--desk-bar-pad` (the bar's height plus enough to clear the toast's top edge, which the
    catalogue measured at about 142 px against a 136 px pad), and the reduced-motion rule.
  - The item page `+page.svelte` renders `ItemPanel.svelte` inside `{#key data.meta.id}`. The
    page component stays mounted across items, so state held there would carry to the next item;
    a key block destroys and recreates its contents when the key changes, so every per-item state
    (the note's open flag and text, "Not sent", the path filter, the triage rows seeded from
    `data.rows`) lives in `ItemPanel` or the views and starts fresh for each item. `ItemPanel` keeps
    the header (meta line, title), the sticky decision bar, and the existing "Decided" state in
    place of the bar for a decided item, and mounts `PrView`,
    `DesignView`, or `TriageView` by kind (T4 fills them; T3 leaves each a stub that renders its
    existing content). The bar's form posts with `enhance`, whose submit function awaits
    `startHold(5000, ...)`: the toast text, Undo focused, one announcement, and the locked controls
    follow the catalogue's "Undo hold"; `z` or Undo calls `cancel()` and returns focus to the
    deciding button. A `beforeNavigate` cancels a hold that is still counting, per judgment call 6.
    On a success result the page calls `goto(result.data.next ?? '/', { replace: true, refreshAll:
    true })` and focuses `#main`; on a `failure` or `error` result it follows judgment call 6. The
    PR and design bar has Reject (with the note row, Cancel, Send rejection, and Ctrl+Enter while
    the note is open), Approve, and the guard slot (judgment call 3). The triage bar has the status
    line and Submit, with the row fields as hidden inputs in their original order, and Ctrl+Enter
    submits from anywhere.
  - The `approve`, `reject`, and `submit` actions return `{ next }` per "Interfaces".
  - `/` redirects to the oldest waiting item. With none, it renders the empty state per the
    catalogue's "Empty state", with the DaisyUI `countdown` (no `aria-live` or `aria-label`, per
    judgment call 4), Keep focused, the "Close when empty" toggle, and `window.close()` at 0.
- **Files.** `review-desk/src/app.html`, `src/app.css`, `src/routes/+layout.{svelte,server.ts}`,
  `src/routes/+page.{svelte,server.ts}`, `src/routes/page.server.test.ts` (new),
  `src/routes/item/[id=id]/+page.{svelte,server.ts}`, `src/routes/item/[id=id]/page.server.test.ts`,
  `src/lib/components/ItemPanel.svelte`, and `src/lib/components/{PrView,DesignView,TriageView}.svelte`
  (stubs).
- **Risk class.** `ordinary`.
- **Acceptance.** The gate prints `gate exit: 0`. Then, per "Running the app", with items seeded
  under a temp state root (two PRs, then two triage items with the same row count) and a
  Playwright page opened by `location.replace`:
  - `/` lands on the older item with `history.length` 1; `j` then Enter opens the newer one,
    `history.length` still 1.
  - With the reject note open and text typed on the first PR, `j` and Enter open the second PR with
    the note closed and empty. A row moved on the first triage item does not follow to the second:
    after `j` and Enter the second shows its own proposals and its status line reads 0 changed.
  - `a` and `z` show and undo the hold with no `decision.json` written. `a`, then `j` and Enter
    within the hold, loads the other item, and no `decision.json` exists after 6 seconds.
  - With the open item's `decision.json` written behind the page (as another tab would), `a` and 5
    seconds show "Not sent", the controls unlocked, and the URL unchanged. The item is reseeded.
  - `a` and 5 seconds write the decision and load the next item: the decided item has left the
    queue and shows under "Decided this session", and `aria-current` sits on the open item.
  - `?` opens the sheet. With the single-keys switch off, `a` starts no hold and shows no toast,
    and after `page.reload()` the switch still reads off; it is then turned back on.
  - Deciding the last item shows the empty state with Keep focused. Escape stops the count: no
    `close` event after 35 seconds, and the close line reads "This tab stays open." Reloaded with
    `desk.autoClose` set to `off`, the empty state shows no count and does not focus Keep.
  - Screenshots of the empty state at 1440 and 390, light and dark, sit beside `renders/empty-b-*`
    with no structural difference the session can see.
- **Test.** The load and action tests stay green, the decided case included; each action's test
  asserts `next`, which skips an item whose `item.json` was removed and is null for the last item;
  `/`'s load test redirects with a waiting item and returns the empty state's data without one; the
  T2 modules carry the logic.
- **Estimate.** 65 minutes.

### T4. The PR, design, and triage views

- **Outcome.**
  - `PrView.svelte` per the catalogue's "PR" section: the four figures (wrapping at phone width,
    with judgment call 2's empty texts), Checks and Review side by side from `xl`, the description
    lead and the body's sections as compact collapses with "What landed" open, then Files with the
    path filter (`role="status"` summary and no-match line, `/` focuses it, Escape clears it),
    "Open all groups", groups and files as collapses with their counts and badges, and each file's
    diff table (`aria-label` naming the file) with the gutter, signs, and row colors the catalogue
    quotes. Failing checks and a `fix` or `escalate` verdict take `--cairn-error-ink`.
  - The item header's meta line shows `<repo name> #<number>`, `<head> into <base>`, and a GitHub
    link with `target="_blank" rel="noopener noreferrer"` when `pr.json` exists, and omits the
    number when the item has none.
  - `DesignView.svelte` renders the document as `.desk-read` at a 68-character measure with its own
    `h1` hidden, and the header's meta line shows the repo, the file name when present, and the
    read time (words divided by 230, rounded up).
  - `TriageView.svelte` per the catalogue's "Triage" section: the hint line, the Now, Defer, and
    Drop sections with dots, counts, and "Nothing here.", rows with roving `tabindex`, `↑`/`↓`,
    `1`/`2`/`3`, the "Move to" popover menu (menuitemradio items, the "proposed" marker, arrows,
    Home, End, and Escape), the "was X" note tied by `aria-describedby`, the moved-row dot, focus
    following a moved row, one announcement per move, and the reason edited in place. It binds its
    rows to `ItemPanel`, which renders the hidden inputs and the status line from `changedCount`.
    Ctrl+Enter commits an open reason edit before it submits.
- **Files.** `review-desk/src/lib/components/{PrView,DesignView,TriageView}.svelte`,
  `src/lib/components/ItemPanel.svelte` (the meta line), and the PR and design parts of the item
  page's `load`.
- **Risk class.** `ordinary`.
- **Acceptance.** The gate prints `gate exit: 0`. Then, per "Running the app", over a temp state
  root seeded with: cairn-cms #113, from `gh pr view 113 -R glw907/cairn-cms` and `gh pr diff 113
  -R glw907/cairn-cms` (read only) in the layout T1's command writes; a guard variant of it, whose
  body adds a `## Before merge` section and ends its Review section with a backticked `fix`, and
  whose `pr.json` holds one `FAILURE` and one `SUCCESS` CheckRun; the design doc above; and a
  13-row triage item:
  - #113, the design, and the triage item, screenshotted at 1440 and 390 in light and dark, show each
    device of `renders/pr-b-*`, `renders/design-b-*`, and `renders/triage-c2-*` (content aside),
    and the 390 px PR page's `document.documentElement.scrollWidth` is 390.
  - On the guard variant, an `alert alert-warning` sits in the guard slot beside Approve, and the
    failed check's row and the Review figure compute to `--cairn-error-ink`.
  - On triage: "Move to" opens its menu with `aria-expanded="true"` and focus on the checked item,
    and Escape returns focus to "Move to"; a pick puts the row in item-number order in its new
    section, focuses it, sets "was X", and updates the counts and the status line; a reason typed
    in place and followed by Ctrl+Enter from the field reaches `decision.json` after the hold.
- **Test.** The T2 modules carry the logic; the load test checks the PR data's shape (figures,
  sections, groups) for one seeded item.
- **Estimate.** 55 minutes.

### Close

Per pass-core "Close" and dotfiles-pass "Close checklist", in order:

1. `git fetch origin` and merge `origin/main` into the branch (a conflict is a stop). The gate on
   the close head prints `gate exit: 0`.
2. Push to `glw907/workstation` and open the PR as a draft whose body is the step 8 skeleton, so
   the e2e's second-round PR item has headings, a `## Review` section, and a list to render.
3. The end-to-end check above, inside "Running the app", after `rm -rf review-desk/build` in the
   worktree. The run screenshots each first-round item page before deciding it, and the empty
   state, at 1440x900 and 390x844 in light and dark (16 PNGs, named like the reference renders, in
   the job's tmp directory). The e2e decisions are test decisions, acted on by nobody.
4. In parallel, on the branch: `visual-verifier`, a fresh agent, grades each of the 16 build renders
   against its reference render, the two as separate labeled image blocks, per visual device,
   COSMETIC or STRUCTURAL, with content differences (titles, counts, paths) out of scope and
   judgment calls 3 to 6 as sanctioned departures; `daisyui-a11y-reviewer` over `review-desk/src`
   against the a11y review record, returning one row per finding (15 rows), each carried with a
   file:line or not carried, where a not-carried row is a finding; the Blueprint quality inspector
   from the session's own loop (`daisyui_setup_expert` with workflowId `review-desk-ui` and
   projectRoot `review-desk`, then `daisyui_rules_enforcer`, then `daisyui_quality_inspector` with
   `auditIntent: "fix_changes"` and every changed `.svelte` file by path relative to
   `review-desk`); and `diff-reviewer` at whole-branch scope against this plan, loading
   `ts-conventions`. One batched fix chain follows, each finding quoted verbatim as its acceptance,
   then the gate. A chain that touches `review-desk/` or `bin/.local/bin/review-desk` reruns step 3
   on the new head and one fresh `visual-verifier` grade; a second FAIL is a "Stops" event.
5. `claude-tooling-sync verify` passes; one `gitleaks git` branch-history scan is clean.
6. `docs/STATUS.md` drops the desk UI from the conductor queue and names this PR as waiting on
   Geoff's desk.
7. ROADMAP needs no change unless step 4 defers an item there.
8. The PR body: what landed (task id, commit), the judgment calls above, the review verdicts, the
   e2e results, "What goes live", "Found, not done" (each item with a proposed disposition and a
   one-line reason, seeded with "Later" below), and the score rows (`cairn-run-gate --records
   <toplevel> <branch>`). "What goes live": after the merge and the main checkout's pull, once
   every hand-over command of this close has exited, the merger runs inside `flock -o
   ~/.local/state/review-desk/start.lock`, and only when no item waits there (if one waits, it
   exits the lock at once and retries a minute later, since a hand-over blocked on the lock has
   already written its item, so waiting inside the lock would deadlock): it stops the running
   desk with `pkill -f '/var/home/glw907/.dotfiles/review-desk/[b]uild'`, rebuilds it with `npm
   --prefix ~/.dotfiles/review-desk ci` and `npm --prefix ~/.dotfiles/review-desk run build`,
   starts it again with the command's own start line (`HOST=127.0.0.1 PORT=7907
   REVIEW_DESK_STATE=$HOME/.local/state/review-desk setsid -f node ~/.dotfiles/review-desk/build
   >>$HOME/.local/state/review-desk/server.log 2>&1`), and checks that `curl -sf
   http://127.0.0.1:7907/` answers. An open desk tab loads the new desk on its next navigation. No
   `stow` run is needed. Rollback is `git revert -m 1 <merge>`, a pull, and the same rebuild. Mark
   the PR ready, and remove the Close's clock file, so the clock stop cannot fire while the session
   waits on the desk.
9. Hand the PR over per pass-core "Close": `review-desk pr glw907/workstation "<title>" <n>` as a
   background Bash command, then the "Found, not done" items as one `review-desk triage` item, and
   wait for both. On approve, merge with `gh pr merge <n> --merge --match-head-commit <head>`, pull
   the main checkout per pass-core, and run "What goes live" once both commands have exited. On
   reject, fix forward from the note, rerun the gate (and steps 3 and 4 if `review-desk/` changed),
   and hand over again. Act on each triage row as pass-core says.

- **Estimate.** 70 minutes.

## Later

Not built in this pass; each goes to the PR's "Found, not done" with a proposed disposition.

- Some navigations push a second history entry, and then the empty state cannot close the tab
  though it still counts and says "Closing this tab": a same-tab link in a rendered PR body or
  design doc, a client navigation while the app is down or after a rebuild (SvelteKit falls back to
  a full-page push, `client.js:1534` and `:1682`), and a decision posted before hydration. A tab
  left open across "What goes live" is one of these.
- An orphaned item (its command killed by SIGKILL or a reboot, ROADMAP "Review desk hardening") now
  sits in the queue beside live items, and approving it writes a decision no session reads. The
  design keeps the hardening out of scope.
- The Playwright MCP server looks for Chrome at `/opt/google/chrome` and cannot start here; the
  pass drove Chromium through the npm package instead.
- The design page's guard slot stays empty; the mockup filled it with hand-written text.
- Turning "Close when empty" back on does not restart the countdown (the mockup's behavior, kept).
