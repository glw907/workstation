# Fold verification: review desk plan and launch prompt at 7246c66 (verification read, claude-opus-5-5, 2026-10-11)

Read: `docs/superpowers/plans/2026-10-11-review-desk.md` (plan), its prompt, the fold record, the
three lenses, and the approved design. Mechanisms checked against the unpacked `@sveltejs/kit`
3.0.1 and `@sveltejs/adapter-node` 6.0.0 sources, the Survey core, this repo's gate scripts, and
probes in `/var/home/glw907/.claude/jobs/c01b6758/tmp/verify/`.

**Verdict:** 1 blocker, 1 major, 2 minor (correctness), 1 minor (optional). No owner fork.

## Answers to the five questions

1. **Blockers and majors closed.** Yes, each at its cited location: M1 (plan:91-99, 289-291,
   237-238, 246-248), M2 (plan:109-117, 300-303), M3 (plan:100-134), M4/C4 (plan:343-345,
   363-364), M5/C1 (plan:52-53, 63-67; prompt:3-4), M6/C2 (plan:447-450), M7 (plan:356-357,
   386-388, 448-450), M8 (plan:280-281), M9/C5 (plan:38-42), C3 and R11 (plan:39-42), C6 header
   check (plan:39-40, 355-356; refusing the Playwright `onerror` check is sound, since the escape
   renders that payload as text and the check would pass with no CSP), C7 (plan:416-432), R1
   (plan:160-170, 336-337, 351-356, 366-367), R2 (plan:386-388, 409-410), R3 (plan:252-253,
   380-381), R4 (plan:376-378, 228-230, 408), R5 (plan:171-175, 233-236, 374-375, 421-423). The
   fold's R6 fix brings in a new defect (finding 1 below).
2. **Contradictions and build order.** The pair is buildable: T2's and T3's files are disjoint,
   generated outputs included (`node_modules/`, `build/`, `.svelte-kit/` are ignored, and
   `npm ci` leaves `package-lock.json` alone). Only T1 and T3 edit `scripts/check.sh`, and T3
   branches from T1's commit (`pass-core` "Pairs", `worktree.baseRef: "head"`). T3's gate gets
   `node_modules` from T1's `npm ci`-when-absent leg. T3's test stubs `curl`, so it does not need
   T2's routes. Each gate leg can pass at the task that adds it. One mechanism fails at run time
   (finding 1), one order contradicts "on the close head" (finding 3), and T4's text conflicts
   with how launch prompts are written (finding 2).
3. **New mechanisms quoted or probed.** Each kit 3 citation checks out by file and line:
   `src/exports/vite/index.js:75-79` (`removed_modules`, `$lib`) and `:276-279` (the
   `svelte.config.{js,ts}` loop calling `config_file_unsupported`); `src/messages/build-errors.js:246-247`
   and `:526-527`; `src/core/config/index.js:180` (`files.params ??= path.join(files.src,
   'params')`); `create_manifest_data/index.js:111` (`resolve_entry(config.files.params, ...)`);
   `src/core/params.js:58` (`params_export_missing`); `src/exports/params/index.js:40-68` (a
   function wrapped as `~standard.validate`, `{ value }` or `{ issues }`);
   `write_tsconfig/index.js:60`; `types/index.d.ts:1156-1157`, `:1177` ("Returning `undefined` is
   valid"), `:1183` (`schema?`), `:1236-1245` (`Handle` in `@sveltejs/kit/hooks`), `:1008` (object
   body deprecated); `src/runtime/env/dynamic/private.js:7` (DEV-only warning);
   `src/runtime/server/page/index.js:182` (`load_server_data` after the action);
   `respond.js:101-131` and `csrf.js` (CSRF before `handle`, body `Cross-site ${method} form
   submissions are forbidden`, gated by `__SVELTEKIT_CSRF_CHECK_ORIGIN__`, which is
   `!trustedOrigins.includes('*')`, `vite/index.js:495`). adapter-node 6: `src/index.js:10-11, 91`
   and `index.js:69` (`export const origin`). Rerun on a copy of the fold's scaffold
   (`verify/app`): `svelte-kit sync && svelte-check` 0 errors, `vitest run` 4 passed, `vite build`
   done, with `REVIEW_DESK_STATE` unset. Added body classes `font-body bg-base-100
   text-base-content` and rebuilt: the CSS holds `.font-body{font-family:var(--font-body)}`,
   `--font-body:"Karla Variable", ...`, `.bg-base-100{background-color:var(--color-base-100)}`,
   and `@media (prefers-color-scheme:dark){:root:not([data-theme]){... --color-base-100:#11171e`,
   so the e2e computed-style check measures a real chain. Node's `Request` keeps a `host` header
   (`new Request(url, {headers:{host:'evil.example:7907'}})` reads it back), so T1's hook unit
   test is feasible. Not proven, and wrong as written: the `flock` start section (finding 1).
4. **Inside the design and the scope samples; minutes.** Yes. Every addition beyond the design's
   text sits at a boundary the design names or is needed for its outcome: the markdown escape and
   CSP (a PR body is external input), the id matcher, the `head` binding, the traps, the item
   check, and the start lock. Task minutes are 310 (85 + 80 + 65 + 20 + 60), under 420, and under
   360, twice the design's low estimate.
5. **Owner forks.** None. T4's "an approve on the desk is the merge authorization" falls under
   the design's "wakes the waiting session to act on it" and "the session acts on the decision".

## Findings, ranked by consequence

### 1. Blocker: the detached app inherits the start lock's fd, so every hand-over after the first hangs

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:379-385` (T3 step 2), `:389`
  (T3 step 4), `:184-185` (probed fact "Shell mechanics")
- **Defect:** T3 step 2 takes `exec 9>"$lock"; flock 9` and, still under the lock, starts the
  app with `setsid -f node <app>/build`. Bash does not mark fd 9 close-on-exec, so the detached
  node process inherits it. A `flock` lock belongs to the open file description, so it stays held
  while any process has that fd open. Node runs until someone stops it, so the next
  `review-desk` call blocks at `flock 9` with no bound. The plan never says when the lock is
  released, so the command also holds it through its own decision poll, and through
  `setsid -f firefox` if that starts while fd 9 is open (a cold Firefox start then becomes a
  long-lived lock holder). The fold's probe (`trapprobe/driver.sh`) serialized two subshells and
  started no detached child, so it did not catch this. **Probe**
  (`verify/flock/first.sh`, `second.sh`): the first script takes the lock, runs `setsid -f sleep
  20`, closes fd 9, and exits. A second script's `flock -w 2 9` then prints "lock still held
  after 2 s". After the sleep is killed it gets the lock. With `9>&-` on the `setsid` line it
  gets the lock at once. As written, the Close's e2e step 2 cannot pass: the PR hand-over starts
  the app, and the design hand-over hangs at the lock. After the merge, the second hand-over of
  any day hangs too (T4's PR-then-triage pair).
- **Proposed fold:** T3 step 2: start the app with fd 9 closed in the child (`HOST=127.0.0.1
  PORT=7907 REVIEW_DESK_STATE=<root> setsid -f node <app>/build 9>&- >>"$log" 2>&1`), and release
  the lock with `exec 9>&-` as soon as the start poll answers, before steps 3 and 4. Add the probe
  result to the "Shell mechanics" fact. The e2e's second hand-over is the check. A T3 test case
  is optional, since `curl` is stubbed as already running there.

### 2. Major: T4's wait-and-merge rule fights the launch prompt that pass-core has sessions write

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:416-432` (T4),
  `claude/.claude/skills/pass-core/SKILL.md:193-197` ("Launch prompt")
- **Defect:** The fold's C7 text puts "stays open until each command exits" and "an approve on
  the desk is Geoff's merge authorization, the one a launch prompt's 'never merge' otherwise
  withholds" in pass-core "Close". The launch prompt is the session's user message, though, and
  current prompts (this pass's own, prompt:44-46) say "Never ... merge the PR" and "notify Geoff
  ... and end". A Sonnet session that holds a user instruction never to merge, against a skill
  sentence saying a desk approve overrides it, can refuse the merge or end before the decision
  arrives. Auto mode's action check reads the user's "never merge" as well. That is C7's defect
  again, one layer up. Under "a rule lives where it executes", the merge clause belongs where
  prompts are written: pass-core "Launch prompt" (no skill or template on this workstation
  carries "never merge" text; a grep of `claude/.claude/skills`, `.claude/skills`, and
  `claude/.claude/docs` finds none, so each planning session writes it fresh).
- **Proposed fold:** T4 also adds one sentence to pass-core "Launch prompt": a prompt for a pass
  that hands its PR over says the session waits for the desk, merges only on Geoff's desk approve
  with `--match-head-commit`, and ends after acting on the decision, never "never merge" or "end"
  outright. T4's acceptance greps that sentence. About 5 minutes. This pass's own prompt keeps
  "never merge", since `review-desk` is not on PATH until the merge and `stow -R bin`.

### 3. Minor: the e2e runs before the close review's fix chain, so it may not run on the close head

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:24` ("On the close head"),
  `:447-458` (Close steps 3 and 4)
- **Defect:** Step 3 runs the end-to-end check, then step 4's `diff-reviewer` can start a fix
  chain that edits `review-desk/` or `bin/.local/bin/review-desk`. The gate reruns after the
  fix, but the e2e does not, so the PR body's e2e results would describe a head that no longer
  ships.
- **Proposed fold:** Close step 4 adds: if the fix chain touches `review-desk/` or
  `bin/.local/bin/review-desk`, rerun step 3 on the new head before step 5.

### 4. Minor: the `src/env.ts` fact does not quote the file it probed

- **Tag:** correctness
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:118-130`, `:292`
- **Defect:** The params fact quotes its probed file, but the env fact gives only the entry
  (`REVIEW_DESK_STATE: { schema: ... }`) and never the module or export name. The conventions say
  "build on these and never on recall", and `defineEnvVars` is new in kit 3.
- **Proposed fold:** Quote the probed file (`verify/app/src/env.ts`, copied from the fold's
  scaffold): `import { defineEnvVars } from '@sveltejs/kit/env'; export const variables =
  defineEnvVars({ REVIEW_DESK_STATE: { schema: (value) => value ?? '' } });` (module
  `@sveltejs/kit/env`, `types/index.d.ts:1153`; `variables` export, `:1156-1157`).

### 5. Minor: this pass's own Close uses the old hand-over without saying why

- **Tag:** optional
- **Location:** `docs/superpowers/plans/2026-10-11-review-desk.md:467-469`; prompt:44-46
- **Defect:** After T4, the worktree's pass-core tells the handing-over session to run
  `review-desk pr` and wait. This pass marks its PR ready, sends `notify-send`, and ends instead.
  That is correct, since the tool is live only after the merge and `stow -R bin`, and the session
  loads skills from the main checkout, but an executor that reads its own edited pass-core may
  stop to ask.
- **Proposed fold:** One clause in Close step 7: "this pass hands over by `notify-send`, since
  `review-desk` goes live only after the merge and `stow -R bin`".

## Probes run (all under `/var/home/glw907/.claude/jobs/c01b6758/tmp/verify/`)

1. `app/`: a copy of the fold's scaffold with `build/` and `.svelte-kit/` removed. `npm run
   check` gave 0 errors, `npm test` gave 2 files and 4 tests passing, and `npm run build` finished.
   Rebuilt with the specimen's body classes and no `data-theme`, then grepped the built CSS as
   quoted above.
2. `flock/`: the lock-inheritance probe in finding 1, with the leftover `sleep` processes killed.
3. `gl/`: `gitleaks dir` over the scaffold's `package-lock.json` reported no leaks.
4. `node -e`: an undici `Request` keeps a caller-set `host` header and has none by default.
