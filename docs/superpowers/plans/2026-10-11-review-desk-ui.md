# Review desk UI: implementation plan

**Design:** `docs/superpowers/specs/2026-10-11-review-desk-ui-design.md` (approved by Geoff
2026-10-11, with unattended planning approved). No separate spec: the design is a page, and
`spec-plan-review` gives a design of a page or less none. **References:** the four approved
mockups in `docs/superpowers/specs/assets/2026-10-11-review-desk-ui/` and their sixteen renders in
`renders/` (`<mockup>-<light|dark>-<1440|390>.png`); the device and behavior catalogue
`docs/superpowers/research/2026-10-11-review-desk-ui-catalogue.md`; the mockups' accessibility
review `docs/superpowers/research/2026-10-11-review-desk-ui-a11y-review.md`. **Review:**
`docs/superpowers/research/2026-10-11-review-desk-ui-review-*.md` and the fold record beside them.

**Outcome.** The desk shows every waiting item in a queue beside the open item, each decision is a
key press or a click, a 5-second undo holds every decision in the page, the next item loads in the
same tab, and the empty state closes the tab. Every screen matches its mockup in light and dark.

**Pass class:** `runner` (Geoff, 2026-10-11, for the desk; `tests/review-desk.test.sh` is on the
`runner` map), with the `live-account` flag: the session pushes a branch, opens a PR on
`glw907/workstation`, reads it through `gh`, and merges it on Geoff's desk approve. No `auth-data`
path is touched.

**Out of scope** (design): one shared tab across hand-overs, the desk hardening in ROADMAP
"Someday", and any change to the `review-desk` command's protocol (its arguments, its stdout, its
exit codes). Also any edit to another repo; `~/Projects/cairn-cms` is read only, for its installed
Playwright.

**Judgment calls this plan makes** (none changes the design; each is recorded so the PR read can
see it):

1. **The command fetches more PR fields.** The PR mockup's figures and meta line need the check
   runs, the PR number, URL, and branches, and the item store has only the body, head, and diff.
   The command's existing `gh pr view` call adds `number,url,headRefName,baseRefName,statusCheckRollup`
   and writes them to a new `pr.json`. Its arguments, stdout, and exit codes do not change, so its
   protocol does not.
2. **Class and review come from the PR body**, since nothing structured carries them. Class is the
   first `` class `<auth-data|runner|ordinary>` `` in the body, case-insensitive (workstation #13
   says ``Class `runner` ``, cairn-cms #113 says ``Risk class `auth-data` ``). Review is the
   body's `## Review` section, rendered in the mockup's Review slot. The Review figure shows that
   section's last `accept`, `fix`, or `escalate`, or "Not stated" when the body has no such
   section or word.
3. **Where the mockup and the design disagree, the design wins.** A `## Before merge` section shows
   as an `alert alert-warning` in the decision bar's guard slot, beside Approve (the mockup has
   none). A failing check and a `fix` or `escalate` verdict take `--cairn-error-ink` (the mockup
   shows neither). Figure labels follow the mockup: Risk, Checks, Review, Changes.
4. **Mockup defects are fixed, never copied** (visual-fidelity's standing sanction). The figures
   row wraps at phone width; the catalogue measured the mockup's row at 636 px on a 390 px screen.
   `?` toggles the sheet, as the sheet says. `/` is listed under PR only. A held decision ignores
   `a`, `r`, `1`, `2`, and `3`. `↓` from outside any row focuses the first row. Every kbd takes the
   borderless style of three of the four mockups. The countdown uses DaisyUI `countdown`, and each
   diff table gets an `aria-label` (a11y review findings 14 and 15).
5. **Mockup content without a data source is left out:** the design page's guard text ("Approved
   in the doc on ...") and the hand-written verdict notes. "Decided this session" lists the items
   decided since the app started, which the item store can answer.

**End-to-end check.** On the close head, from the pass worktree (Close step 3):

1. `bash scripts/gate.sh` prints `gate exit: 0`.
2. With a temp `XDG_STATE_HOME` and a `firefox` stub first on `PATH` that records its URL, the
   worktree's `bin/.local/bin/review-desk` hands over this pass's draft PR, the design doc above,
   and a three-row triage list, in that order. The first finds no build and nothing on 7907, so it
   builds and starts the close head's app.
3. A Playwright script (Chromium) opens the PR's recorded URL in a new page by
   `location.replace` from `about:blank`, so the tab starts with one history entry, and asserts
   `history.length === 1`. Then, by key: `a` shows the toast with Undo focused; `z` undoes, sends
   nothing, and returns focus to Approve; `a` again posts after 5 seconds, the PR command exits 0
   printing `{"decision":"approve","head":"<sha>"}`, and the page shows the design at its item URL
   with `history.length === 1`. On the design, `r`, a typed note, and Ctrl+Enter post a reject that
   carries the note. On triage, row 2 takes `3`; the status line reads `3 items, 1 changed from
   proposed`; Ctrl+Enter posts, and the command prints row 2 as `drop`. The page shows the empty
   state with Keep focused, and after 30 seconds the page's `close` event fires.
4. A second round hands over a fresh PR, design, and triage item and takes each decision by click:
   Approve; Reject, a note, and Send rejection; a row's "Move to" menu and Submit. Each command
   prints its decision.
5. With nothing waiting, `timeout 60 firefox --headless --profile <temp dir> http://127.0.0.1:7907/`
   exits 0, not 124: real Firefox closes the empty-state tab, and closing its only window quits it.
6. The bind, CSP, and `Host` checks of the first desk pass still hold: `ss -ltnH 'sport = :7907'`
   prints `127.0.0.1:7907`, `curl -sI` of an item page shows `script-src 'self' 'nonce-`, and a GET
   with `Host: evil.example:7907` gets 403.
7. `visual-verifier` passes each screen against its mockup in light and dark, and
   `daisyui-a11y-reviewer` and the Blueprint quality inspector find no blocker (Close steps 4 and 5).

**Clock estimate:** 220 task-minutes (T1 20, T2 30, T3 45, T4 30, T5 25, close 70), against the
design's 2 hours and under twice it, 240. The first desk pass ran 68 minutes of clock against 315
planned, so these figures are already the tighter ones. T1 and T2 run as a pair, then T4 and T5,
so the path is about 30 + 45 + 30 + 70 = 175 minutes.

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
    `#verdicts`, and `#files` links.
  - A `load` that throws `redirect` during a client navigation re-navigates with the same
    `replace_state` (`client.js:2026-2042`), so `/` may redirect to the oldest waiting item.
  - `applyAction` on a `redirect` result calls `_goto(result.location, { refreshAll: true })`, a
    push (`client.js:2981-2982`). So no action redirects: the page posts through `enhance` and then
    calls `goto(next, { replace: true, refreshAll: true })` itself.
  - `enhance(form, submit)` awaits the submit function before it fetches
    (`src/runtime/app/forms/client.js`: `const callback = (await submit({ action, cancel, ... })) ??
    fallback_callback; if (cancelled) return;`). So the 5-second hold is the submit function
    awaiting a timer, and Undo calls `cancel()`. Without JavaScript the form still posts natively.
- **GitHub data.** `gh pr view <n> -R <repo> --json body,headRefOid,number,url,headRefName,baseRefName,statusCheckRollup`
  returns all of these. A `statusCheckRollup` entry is a `CheckRun` (`name`, `workflowName`,
  `status`, `conclusion`, read from cairn-cms #113: `"conclusion":"SUCCESS"`, `"status":"COMPLETED"`,
  `"workflowName":"create-site"`) or a `StatusContext` (`context`, `state`). The mockup's check
  names are `workflowName / name` ("tool / make check (ubuntu-latest)"). A repo with no CI, like
  this one, returns an empty array.
- **The live desk.** At planning, the main checkout's app ran on 7907 (`node
  /var/home/glw907/.dotfiles/review-desk/build`) with nothing waiting in
  `~/.local/state/review-desk`. Port 7907 is fixed in three places (the command, `paths.origin`, and
  the `Host` check), so the e2e must stop the live app first, and only when nothing waits.

## Interfaces

Changes to the first desk plan's "Interfaces"; everything else there holds.

- **`item.json`** gains `number` (a PR, the `<source>` argument as a number) and `file` (a design,
  the source file's basename).
- **`pr.json`**, new, written by the command for a PR before `item.json`: the `gh pr view` JSON
  minus `body` and `headRefOid`, so `{number, url, headRefName, baseRefName, statusCheckRollup}`.
  An item written by the old command has no `pr.json`; the app reads its absence as no checks and
  no link, never an error.
- **Queue order:** waiting items list oldest first by `created`.
- **Next item:** after a decision, the item after the current one in queue order; if none follows,
  the oldest other waiting item; with none, `/`.
- **`localStorage`:** `desk.singleKeys` and `desk.autoClose`, each `on` or `off`, absent meaning
  `on`. Every read and write sits in `try`.
- **Decision JSON:** unchanged.

## Conventions every task follows

The first desk plan's "Conventions every task follows" hold (gate, SvelteKit 3, the main checkout
untouched, stopping an app, comments, UI, commits, clock, stops, scope), with these additions:

- **Visual reference.** A UI task reads the catalogue's sections for its screens and opens the
  matching renders (light and dark, 1440 and 390) before writing markup, then works the canonical
  loop: build, screenshot with the Playwright pattern above, compare to the render, fix. The
  mockups are the reference, never code to copy: the CDN loads become the app's Tailwind build, and
  the desk layer's rules (the catalogue's "Desk layer" table, minus its dead rules) move into
  `src/app.css` or the component's `<style>`.
- **DaisyUI first.** Read the component guide in the `daisyui` skill before using a component
  (`drawer`, `menu`, `modal`, `stat`, `collapse`, `toast`, `alert`, `toggle`, `kbd`, `dropdown`,
  `countdown`, `badge`, `input`, `textarea`).
- **Svelte.** Load `svelte-conventions` before writing a `.svelte` file, and run the Svelte MCP
  `svelte-autofixer` on each new component until it reports nothing.
- **Phone width.** No page scrolls sideways at 390 px.
- **Test-first** where a task names logic: the test is written and seen failing before the code.

## Tasks

### T1. The item store and the command

- **Outcome.**
  - `listWaiting` returns items oldest first. A new `listDecided(root, since)` returns the items
    whose `decision.json` was written at or after `since` (epoch ms, from its mtime), newest first,
    each with its meta and its decision word (approve, reject, submit). A PR item's `readItem`
    content carries `pr.json`'s fields when the file exists.
  - The command's PR branch calls `gh pr view` with the fields in "Interfaces", writes `body.md`
    and `pr.json` from that one call, and adds `number` to `item.json`; the design branch adds
    `file`. Nothing else in the command changes.
- **Files.** `review-desk/src/lib/server/items.ts` and its test, `bin/.local/bin/review-desk`,
  `tests/review-desk.test.sh`.
- **Risk class.** `runner` (`tests/**`).
- **Acceptance.** `npm --prefix review-desk test` and `bash tests/review-desk.test.sh` pass, then
  the gate prints `gate exit: 0`.
- **Test** (first). The store, over a temp root: three waiting items list oldest first; two decided
  items, one before `since` and one after, list only the later one, with its decision word; a PR
  item with `pr.json` reads its `url` and checks, and one without it reads with none and no error.
  The command test: the `gh` stub's `view` prints canned JSON with every new field; the PR item has
  `pr.json` holding `url` and `statusCheckRollup` and no `body`, and `item.json` holds `number`; a
  design item's `item.json` holds `file`. The existing assertions still pass.
- **Pair.** Runs as a pair with T2 (disjoint files).
- **Estimate.** 20 minutes.

### T2. The page logic, as tested modules

- **Outcome.** Five modules under `review-desk/src/lib/`, each pure, each with its test:
  - `pr-summary.ts`: `riskClass(body)` per judgment call 2; `bodySections(body)` splits the body at
    `## ` headings into a lead and titled sections, leaving out `Before merge` and `Review`;
    `reviewVerdict(body)` per judgment call 2; `checksSummary(rollup)` gives passed, failed,
    skipped, and pending counts and one row per check (`workflowName / name` or `context`, and its
    state: `SUCCESS` and `NEUTRAL` pass, `SKIPPED` skips, an incomplete `status` or a `PENDING` or
    `EXPECTED` state is pending, anything else fails).
  - `diff.ts` grows `fileGroups(diff)`: files grouped by first path segment (top-level files under
    "Repository root"), groups in path order, each file with its path, adds, dels, status (`new`
    for `new file mode`, `deleted` for `deleted file mode`), and rows of kind hunk, add, del, or
    context with old and new line numbers taken from each `@@ -a,b +c,d @@` header. The existing
    `classify` stays.
  - `keys.ts`: `keyAction(key, mods, context)` returns the action for a key event, or null, per the
    catalogue's "Global key handler" order and "Key map" table with judgment call 4's fixes.
    `context` carries the page kind, whether the target is a typing target, whether single keys are
    on, whether the sheet is open, whether a decision is held, and whether the note is open.
  - `hold.ts`: `startHold(ms, { tick, fire })` returns `{ cancel }`; `tick` gets the whole seconds
    left once a second, `fire` runs once at the end, and `cancel` stops both.
  - `triage.ts`: `moveRow(rows, index, disposition)`, `groupRows(rows)` (each section's rows in
    item-number order), and `changedCount(rows)` against each row's `proposed`.
  - `queue.ts`: `nextItem(queue, id)` per "Interfaces".
- **Files.** Those modules and their tests.
- **Risk class.** `ordinary`.
- **Acceptance.** `npm --prefix review-desk test` passes, then the gate prints `gate exit: 0`.
- **Test** (first). `riskClass` reads both real phrasings and returns null with none. `bodySections`
  on a body with a lead, `## What landed`, `## Review`, and `## Before merge` returns the lead and
  one section. `reviewVerdict` returns `accept` for cairn-cms #113's wording ("first ... `fix` ...
  Second whole-branch review after the fix: `accept`"). `checksSummary` on 11 successes and 1
  skip gives "11 passed, 1 skipped", and a `FAILURE` counts as failed. `fileGroups` on a fixture
  diff of a top-level file, a new file, a deleted file, and a two-hunk file gives the groups, the
  counts, and the right line numbers on each side of a hunk. `keyAction`: `a` approves on a PR and
  not on triage; every single key returns null with single keys off or while typing; Escape and
  Ctrl+Enter work with single keys off; `a` returns null while a decision is held; `?` returns
  toggle-sheet with the sheet open. `startHold` under `vi.useFakeTimers()` ticks 4, 3, 2, 1, fires
  once at 5 s, and never fires after `cancel`. `moveRow` keeps item-number order inside a section,
  and `changedCount` drops back to 0 when a row returns to its proposal. `nextItem` returns the next
  item, then the oldest other one when the current is last, then null.
- **Pair.** Runs as a pair with T1.
- **Estimate.** 30 minutes.

### T3. The shell: queue, keys, undo, and the empty state

- **Outcome.**
  - `app.html`'s `<body>` carries `data-sveltekit-replacestate`. `+layout.server.ts` loads the
    queue (`listWaiting`) and the decided list (`listDecided` since the server module's start
    time). `+layout.svelte` is the catalogue's page skeleton: the drawer open from `lg`, the queue
    (header, rows with kind, repo and number, age, and title, the selected row, the empty row,
    "Decided this session", the footer with the shortcut button, the collar), the mobile `<header>`
    navbar, the shortcut sheet with the single-keys switch, the `sr-only` status region, and the
    toast. One `keydown` listener on `document` dispatches `keyAction`. The drawer, j/k, the sheet,
    and every focus move follow the catalogue's "Behavior" section.
  - `src/app.css` carries the desk layer's shared rules: the global `:focus-visible` ring, the
    queue row grid, the kbd style, `.desk-field`, the `desk-no-sk` hide rule, `scroll-padding-bottom`
    from `--desk-bar-pad` (the bar's height plus enough to clear the toast's top edge, which the
    catalogue measured at about 142 px against a 136 px pad), and the reduced-motion rule.
  - The item page `+page.svelte` keeps the header (meta line, title) and the sticky decision bar,
    and mounts `PrView`, `DesignView`, or `TriageView` by kind (T4 and T5 fill them; T3 leaves each a
    stub that renders its existing content). The bar's form posts with `enhance`, whose submit
    function awaits `startHold(5000, ...)`: the toast text, Undo focused, one announcement, and the
    locked controls follow the catalogue's "Undo hold"; `z` or Undo calls `cancel()` and returns
    focus to the deciding button; on the action's success the page calls
    `goto(nextItem(...) ?? '/', { replace: true, refreshAll: true })` and focuses `#main`. The PR
    and design bar has Reject (with the note row, Cancel, Send rejection, and Ctrl+Enter while the
    note is open), Approve, and the guard slot (judgment call 3). The triage bar has the status line
    and Submit, with the row fields as hidden inputs in their original order, and Ctrl+Enter submits
    from anywhere.
  - `/` redirects to the oldest waiting item. With none, it renders the empty state per the
    catalogue's "Empty state", with the DaisyUI `countdown`, Keep focused, the "Close when empty"
    toggle, and `window.close()` at 0.
- **Files.** `review-desk/src/app.html`, `src/app.css`, `src/routes/+layout.{svelte,server.ts}`,
  `src/routes/+page.{svelte,server.ts}`, `src/routes/item/[id=id]/+page.{svelte,server.ts}`,
  `src/lib/components/{PrView,DesignView,TriageView}.svelte` (stubs), and
  `src/routes/item/[id=id]/page.server.test.ts` where the load's shape changes.
- **Risk class.** `ordinary`.
- **Acceptance.** The gate prints `gate exit: 0`. With two items seeded under a temp state root,
  the built app run per the first plan's acceptance pattern, and a Playwright page opened by
  `location.replace`: `/` lands on the older item with `history.length` 1; `j` then Enter opens the
  newer one, `history.length` still 1; `a` and `z` show and undo the hold with no `decision.json`
  written; `a` and 5 seconds write it and load the other item; deciding that one shows the empty
  state with Keep focused. Screenshots of the empty state at 1440 and 390, light and dark, sit
  beside `renders/empty-b-*` with no structural difference the session can see. The app is stopped
  after.
- **Test.** The load and action tests stay green, `/`'s load test redirects with a waiting item and
  returns the empty state's data without one, and the T2 modules carry the logic.
- **Estimate.** 45 minutes.

### T4. The PR and design views

- **Outcome.** `PrView.svelte` per the catalogue's "PR" section: the four figures (wrapping at
  phone width), Checks and Review side by side from `xl`, the description lead and the body's
  sections as compact collapses with "What landed" open, then Files with the path filter
  (`role="status"` summary and no-match line, `/` focuses it, Escape clears it), "Open all groups",
  groups and files as collapses with their counts and badges, and each file's diff table
  (`aria-label` naming the file) with the gutter, signs, and row colors the catalogue quotes.
  Failing checks and a `fix` or `escalate` verdict take `--cairn-error-ink`. The item header's meta
  line shows `<repo name> #<number>`, `<head> into <base>`, and a GitHub link when `pr.json` exists.
  `DesignView.svelte` renders the document as `.desk-read` at a 68-character measure with its own
  `h1` hidden, and the header's meta line shows the repo, the file name, and the read time (words
  divided by 230, rounded up).
- **Files.** `review-desk/src/lib/components/{PrView,DesignView}.svelte`, and the PR and design
  parts of the item page's `load`.
- **Risk class.** `ordinary`.
- **Acceptance.** The gate prints `gate exit: 0`. Seeded with workstation #13's body and diff and
  with the design doc above, the PR and design pages, screenshotted at 1440 and 390 in light and
  dark, show each device of `renders/pr-b-*` and `renders/design-b-*` (content aside), and the
  390 px PR page's `document.documentElement.scrollWidth` is 390.
- **Test.** The T2 modules carry the logic; the load test checks the PR data's shape (figures,
  sections, groups) for one seeded item.
- **Pair.** Runs as a pair with T5 (disjoint files), after T3 commits.
- **Estimate.** 30 minutes.

### T5. The triage view

- **Outcome.** `TriageView.svelte` per the catalogue's "Triage" section: the hint line, the Now,
  Defer, and Drop sections with dots, counts, and "Nothing here.", rows with roving `tabindex`,
  `↑`/`↓`, `1`/`2`/`3`, the "Move to" popover menu (menuitemradio items, the "proposed" marker,
  arrows, Home, End, and Escape), the "was X" note tied by `aria-describedby`, the moved-row dot,
  focus following a moved row, one announcement per move, and the reason edited in place. It binds
  its rows to the page, which renders the hidden inputs and the status line from `changedCount`.
- **Files.** `review-desk/src/lib/components/TriageView.svelte`.
- **Risk class.** `ordinary`.
- **Acceptance.** The gate prints `gate exit: 0`. A seeded 13-row triage item, screenshotted at
  1440 and 390 in light and dark, shows each device of `renders/triage-c2-*`, and the menu, a moved
  row, and an edited reason each match the catalogue's description in a Playwright run.
- **Test.** The T2 `triage.ts` tests carry the logic.
- **Pair.** Runs as a pair with T4.
- **Estimate.** 25 minutes.

### Close

Per pass-core "Close" and dotfiles-pass "Close checklist", in order:

1. `git fetch origin` and merge `origin/main` into the branch (a conflict is a stop). The gate on
   the close head prints `gate exit: 0`.
2. Push to `glw907/workstation` and open the PR as a draft whose body is the step 9 skeleton, so
   the e2e's PR item has headings, a `## Review` section, and a list to render.
3. The end-to-end check above. Before it: if any item waits in `~/.local/state/review-desk` (an
   `item.json` with no `decision.json`), apply "Stops"; otherwise stop the live app with `pkill -f
   '/var/home/glw907/.dotfiles/review-desk/[b]uild'` and confirm `curl -s http://127.0.0.1:7907/`
   fails. Then `rm -rf review-desk/build` in the worktree. The run screenshots each item page
   before deciding it, and the empty state, at 1440x900 and 390x844 in light and dark (16 PNGs,
   named like the reference renders, in the job's tmp directory). The e2e decisions are test
   decisions, acted on by nobody. Stop the worktree app after, and leave the live app stopped; the
   next hand-over starts it.
4. `visual-verifier`, a fresh agent, grades each of the 16 build renders against its reference
   render, the two as separate labeled image blocks, per visual device, COSMETIC or STRUCTURAL, with
   content differences (titles, counts, paths) out of scope and judgment calls 3 to 5 as sanctioned
   departures. On FAIL, a fix agent works its list verbatim, step 3's renders are retaken, and a new
   fresh verifier grades again; the loop exits only on a fresh PASS.
5. In parallel, on the branch: `daisyui-a11y-reviewer` over `review-desk/src` against the a11y
   review record; the Blueprint quality inspector from the session's own loop
   (`daisyui_setup_expert` with workflowId `review-desk-ui` and projectRoot `review-desk`, then
   `daisyui_rules_enforcer`, then `daisyui_quality_inspector` with `auditIntent: "fix_changes"` and
   every changed `.svelte` file by path relative to `review-desk`); and `diff-reviewer` at
   whole-branch scope against this plan, loading `ts-conventions`. One batched fix chain follows,
   each finding quoted verbatim as its acceptance, then the gate. A chain that touches
   `review-desk/` or `bin/.local/bin/review-desk` reruns steps 3 and 4 on the new head.
6. `claude-tooling-sync verify` passes; one `gitleaks git` branch-history scan is clean.
7. `docs/STATUS.md` drops the desk UI from the conductor queue and names this PR as waiting on
   Geoff's desk.
8. ROADMAP needs no change unless step 5 defers an item there.
9. The PR body: what landed (task id, commit), the judgment calls above, the review verdicts, the
   e2e results, "What goes live", "Found, not done" (each item with a proposed disposition and a
   one-line reason, seeded with "Later" below), and the score rows (`cairn-run-gate --records
   <toplevel> <branch>`). "What goes live": after the merge and the main checkout's pull, the
   merger stops the running desk with `pkill -f '/var/home/glw907/.dotfiles/review-desk/[b]uild'`,
   rebuilds it with `npm --prefix ~/.dotfiles/review-desk ci` and `npm --prefix
   ~/.dotfiles/review-desk run build`, and starts it again with the command's own start line
   (`HOST=127.0.0.1 PORT=7907 REVIEW_DESK_STATE=$HOME/.local/state/review-desk setsid -f node
   ~/.dotfiles/review-desk/build >>$HOME/.local/state/review-desk/server.log 2>&1`), so open tabs
   reload into the new desk. No `stow` run is needed. Rollback is `git revert -m 1 <merge>`, a pull,
   and the same rebuild. Mark the PR ready.
10. Hand the PR over per pass-core "Close": `review-desk pr glw907/workstation "<title>" <n>` as a
    background Bash command, then the "Found, not done" items as one `review-desk triage` item, and
    wait for both. On approve, merge with `gh pr merge <n> --merge --match-head-commit <head>`,
    pull the main checkout per pass-core, and run "What goes live". On reject, fix forward from the
    note, rerun the gate (and steps 3 and 4 if `review-desk/` changed), and hand over again. Act on
    each triage row as pass-core says.

- **Estimate.** 70 minutes.

## Later

Not built in this pass; each goes to the PR's "Found, not done" with a proposed disposition.

- A link in a rendered PR body or design doc opens in the same tab. After one, the tab holds two
  history entries and the empty state cannot close it.
- The Playwright MCP server looks for Chrome at `/opt/google/chrome` and cannot start here; the
  pass drove Chromium through the npm package instead.
- The design page's guard slot stays empty; the mockup filled it with hand-written text.
- Turning "Close when empty" back on does not restart the countdown (the mockup's behavior, kept).
