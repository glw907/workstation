# Review desk UI plan: mechanics and feasibility review

The `plan-reviewer` agent (Opus, medium) reviewed `docs/superpowers/plans/2026-10-11-review-desk-ui.md`
at `439f1b0` on 2026-10-11. The planning session saved its reply here verbatim.

---

## Mechanics and feasibility review: `docs/superpowers/plans/2026-10-11-review-desk-ui.md` @ 439f1b0

### What I verified (probes under `/var/home/glw907/.claude/jobs/ebc278e8/tmp/`, and source reads)

I built a scratch copy of the app on port 7917 using the main checkout's SvelteKit 3.0.1 `node_modules`. It had `data-sveltekit-replacestate` on `<body>`, a `/` load that throws `redirect(303)`, and an item page whose `use:enhance` submit function awaits a hold promise and then calls `goto(next, { replace: true, refreshAll: true })`. I drove it with Playwright 1.63.0 and `/usr/bin/chromium-browser`, opening the first page by `location.replace`.

- The first full load of `/` redirects on the server to the oldest item: `history.length` is 1.
- A same-page `#sec` link with the body attribute leaves `history.length` at 1.
- Hold, then post, then `goto` replace: 1.
- `goto('/')` followed by the client-side redirect to a newly seeded item: 1. This confirms `client.js:2026-2042`.
- Undo (resolve false, then enhance `cancel()`) writes no `decision.json`.
- An action on an item already decided elsewhere returns an `error` result. `applyAction` renders a bare "404 Not found" page in place, with history still at 1.
- The empty state's `window.close()` fires the page's `close` event.
- `curl -sf` on a 303 exits 0, so the command's readiness check survives the `/` redirect.

Quoted source:
- `enhance` builds its `FormData` and resolves `formAction` before it awaits `submit` (`src/runtime/app/forms/client.js:121-155`).
- A fallback success whose result `location` is the current page refreshes in place, with no history entry (`:94-104`).
- `set_nearest_error_page` does not touch history.
- `<form method="dialog">` is ignored by the router (`client.js:3268`).
- An external link or a link with `target` other than `_self` is not routed (`:3146-3150`, `:3166`).
- DaisyUI 5.7.47's `countdown` is pure CSS driven by `--value` in a `style` attribute. The dropdown uses the native `popover` API with CSS anchors. The CSP limits only `script-src`, so neither needs anything it blocks.
- `gh pr view --json` lists `number`, `url`, `headRefName`, `baseRefName`, and `statusCheckRollup`.
- `claude --bg`, `--name`, and `--effort` exist.

**Restart probe:** I opened a tab on an item, rebuilt with a changed root page, stopped the app and started it again, then approved. The navigation became a full-page push to `/` with `history.length` 2 (`client.js:1534`, `native_navigation(url)` without `replace`).

**Live state now:** the main checkout's app holds 7907 (`node /var/home/glw907/.dotfiles/review-desk/build`, pid 2820576), `XDG_STATE_HOME` is unset, and 10 item directories exist under `~/.local/state/review-desk/items`.

### Findings, ranked by consequence

**1. blocker, correctness: T3, T4 and T5 cannot run their app acceptances on 7907, and T4 and T5 cannot share it** (plan:171-172, 312-319, 340-346, 359-363, 374-381)
- **Defect:** 7907 is fixed in `paths.origin` and in the `Host` check, so no other port works, the dev server included (the hook returns 403). The live desk holds 7907 now, and the plan stops it only at Close step 3.
  - T3's "built app run per the first plan's acceptance pattern" fails to bind. Its Playwright run then hits the live app, which serves a different state root, so the seeded items 404.
  - T4 and T5 run as worktree-isolated pair subagents. Both need 7907 at once for their screenshot loops.
  - pass-core "Pairs" says "A shared port is an environment variable", which this app cannot honor.
  - While the desk is down, any other session's hand-over restarts the live app on 7907.
- **Fold:**
  - Move the live-desk stop, with its nothing-waiting precondition, to before T3, and leave it stopped through Close.
  - Before every app start, require `curl -s http://127.0.0.1:7907/` to fail. If the live desk came back, apply "Stops".
  - Fold T5 into T4 as one sequential task ("T4: the three views", 55 min). This also meets pass-core's single-deliverable rule, since T5 is one file. The path grows about 25 minutes (to about 200), and task-minutes are unchanged.
  - Update the prompt's `T4+T5` pair lines to match.
  - Alternative to folding: wrap each pair agent's build-run-screenshot-stop cycle in one `flock` on a shared lock file. That is more ceremony.

**2. major, correctness: "What goes live" can kill the desk under Geoff's pending triage, and its claim that tabs reload is wrong** (plan:402-415; prompt:55-62)
- **Defect:**
  - Close step 10 hands over the PR and the triage item. Geoff approves the PR and lands on the triage item in the same tab.
  - The session wakes on the PR exit, then merges and runs the `pkill`, `npm ci`, and build. That takes a minute or more.
  - Geoff's triage Submit then posts to a dead server. The result is an `error`, rendered as an error page in place, and his in-page row edits are lost.
  - Even after the restart, my probe shows an old tab's next navigation is a full-page push (`history.length` 2). That tab cannot auto-close, so "so open tabs reload into the new desk" is false.
- **Fold:**
  - Run "What goes live" only after both hand-over commands have exited. Say so in step 10 and in the prompt.
  - Delete the "open tabs reload" clause.
  - Add a Later item: a tab left open across a rebuild loads its next item by a full-page push and stays open at the empty state.
  - Optional: a 2-line fix in the post callback. Use `if (await updated.check()) location.replace(target)`, with `updated` from `$app/state`, before `goto`.

**3. major, correctness: the e2e's item order is not deterministic** (plan:57-60, 65-66)
- **Defect:**
  - The command writes `item.json` before it takes the start lock (`bin/.local/bin/review-desk:35-44`).
  - The PR item lands after two `gh` calls. The design and triage items land after a `cp`, and `created` has 1-second resolution.
  - Launched back to back, the design (or triage) item can be older than the PR, or tie with it. Then "approve the PR, then the page shows the design" fails.
- **Fold:** start each hand-over only after the previous one's `item.json` exists, plus `sleep 1`. Apply the same to round 2.

**4. major, correctness: the PR renders cannot show the mockup's check devices** (plan:61-66, 340-343, 377-386)
- **Defect:**
  - The e2e PR is this pass's own workstation PR. The plan itself says this repo has no CI, so `statusCheckRollup` is `[]`.
  - The four PR PNGs the visual-verifier grades will lack the Checks list and a real Checks figure that `pr-b-*` shows (12 checks). That is a structural difference beyond "titles, counts, paths". It risks a fail loop, or a vacuous pass on those devices.
  - The failing-check `--cairn-error-ink` path is never rendered at all.
  - The plan also never names what the Checks and Risk figures read for an empty or absent rollup, or for no class.
- **Fold:**
  - Take T4's acceptance and Close step 3's four PR screenshots from a seeded item built from cairn-cms #113. That is the mockup's subject, with 12 checks and a `## Review` section, fetched read-only with `gh pr view 113 -R glw907/cairn-cms --json ...` and `gh pr diff`.
  - Keep the e2e decisions on this pass's PR.
  - Name the empty text, for example "None" for Checks and "Not stated" for Risk, and add one T2 test for `checksSummary([])`.

**5. major, correctness: file boundaries between T3, T4 and T5 are incomplete** (plan:293-310, 332-338, 355-357)
- **Defect:**
  - T4 owns the header meta line (`#<number>`, branches, GitHub link, read time), but the header lives in the item `+page.svelte`, which only T3 lists.
  - T5 "binds its rows to the page, which renders the hidden inputs and the status line from `changedCount`". That works only if T3's page already holds `$state` rows bound to the stub.
  - pass-core needs disjoint files, and a conflict is a stop.
- **Fold:**
  - T3 fixes each stub's props contract (`PrView {data}`, `DesignView {data}`, `TriageView bind:rows`).
  - T3 renders the hidden inputs and the status line from the bound rows.
  - T3 builds the meta line from load data, or T4 lists `+page.svelte`.
  - If finding 1 folds T5 into T4, only the meta-line ownership remains.

**6. minor, correctness: the plan's own GitHub link breaks auto-close** (plan:333)
- **Defect:** an external link is not routed by SvelteKit (`client.js:3166`), so a same-tab click pushes history, and `data-sveltekit-replacestate` does not apply to external links.
- **Fold:** `target="_blank" rel="noopener noreferrer"` on the meta-line link. The router bails on `target` other than `_self` (`:3147-3150`). Markdown links stay in Later.

**7. minor, correctness: `reviewVerdict` can read prose as a verdict** (plan:37-39, 264-265)
- **Defect:** "the last `accept`, `fix`, or `escalate`" as bare words matches prose such as "one batched fix chain". Close step 9's own body ("review verdicts" plus a fix chain) would then show `fix` in error ink on a clean PR.
- **Fold:** match only backticked tokens. Add a T2 test where prose "fix" follows a backticked `accept` and the result stays `accept`.

**8. minor, correctness: the non-success post state is unnamed** (plan:296-299)
- **Defect:** "on the action's success" says nothing about `failure` or `error`.
  - The probe shows an item decided in another tab, which is plausible because each hand-over opens its own tab, renders a bare "404 Not found" page in place.
  - A server that is down gives the same.
- **Fold:** pick the report: on a 404, go to the next item as on success; otherwise announce "Not sent" and re-enable the controls. Add one line to T3's acceptance.

**9. minor, correctness: the e2e cannot observe the command's exit as written** (plan:64-71)
- **Defect:** "the PR command exits 0 printing ..." mid-script needs each background hand-over's stdout and exit code in files the script can read.
- **Fold:** `bin/.local/bin/review-desk pr ... >"$T/pr.out" 2>"$T/pr.err"; echo $? >"$T/pr.rc"` per hand-over. The script polls for `pr.rc`.

**10. minor, correctness: vacuous fixtures**
- plan:67-68: name the triage fixture so row 2 is proposed `now`. If it were proposed `drop`, "prints row 2 as drop" passes trivially. Round 2's "Move to" target must also differ from that row's proposal.
- plan:227-229 (T1): name the fixture: set the decided items' `decision.json` mtimes with `utimes`, one before `since` and one after. Note that the existing "lists newest first" test (`items.test.ts:22`) is flipped, not kept.

**11. minor, correctness: T3 Files omit the root route's test** (plan:307-310, 320-321)
- **Defect:** `/`'s load test needs `src/routes/page.server.test.ts`, which is not listed.
- **Fold:** add it.

**12. minor, optional: queue navigation during a hold** (plan:296-298)
- **Defect:** `j`, then Enter, or a queue click is not locked during the 5 s hold.
  - The post still targets the original item (`formAction` is captured at submit, `forms/client.js:121-126`), so nothing is misdirected.
  - Then `goto(next)` pulls Geoff off the item he just opened.
- **Fold:** add the queue links to the locked controls (the catalogue's lock list), so no new behavior is needed.

**13. minor, optional: T3's estimate is the likeliest clock stop** (plan:322)
- **Defect:** 45 minutes covers the layout, queue, drawer, sheet, toast and hold, key dispatch, both bars, the empty state, the `/` redirect, the layout load, three stubs, the CSS layer, tests, and a Playwright acceptance with four screenshots.
- **Fold:** 60. The total of 235 stays at or under 240.

**14. minor, optional: Firefox remoting in e2e step 5** (plan:73-74)
- **Defect:** I did not probe whether `firefox --headless --profile <tmp>` remotes into Geoff's running Firefox. I avoided the probe because it could open a tab in his browser.
- **Fold:** add `--no-remote`. It is cheap, and it removes the question.

**15. minor, optional: privileged-field note** (plan:34-39)
- **Defect:** the Risk, Review and Before-merge displays come from the PR body. Their only channel is whoever writes the body, usually the executing session, so they are self-reported and inform a merge approval.
- **Fold:** one clause in judgment call 2 saying so. No code.

**16. minor, optional: over-ceremony in Close step 5's rerun rule** (plan:393-394)
- **Defect:** any fix-chain touch of `review-desk/` reruns the whole e2e and the visual loop. That is two rounds with 5 s holds, a 30 s countdown, a 60 s Firefox run, and 16 renders, roughly 10 to 15 minutes each time.
- **Fold:** a style-only fix reruns the 16 renders and step 4. A behavior fix reruns step 3 too.

No OWNER FORK: none of the folds changes the approved design.

Probe artifacts:
- `/var/home/glw907/.claude/jobs/ebc278e8/tmp/app/` (the scratch app)
- `/var/home/glw907/.claude/jobs/ebc278e8/tmp/probe.cjs` and `probe2.cjs` (the Playwright probes)
- `/var/home/glw907/.claude/jobs/ebc278e8/tmp/probe2.out` (the restart probe's output)

The probe app is stopped and 7917 is free. The live desk on 7907 was not touched.
