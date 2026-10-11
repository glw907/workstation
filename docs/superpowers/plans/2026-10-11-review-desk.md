# Review desk, lean v1: implementation plan

**Design:** `docs/superpowers/specs/2026-10-11-review-desk-design.md` (approved by Geoff and
re-scoped to lean v1, 2026-10-11). No separate spec: the design is a page, and `spec-plan-review`
gives a design of a page or less none. **Review:** the three lenses, the fold, and the verification
read, `docs/superpowers/research/2026-10-11-review-desk-{review-contract,review-mechanics,review-risk,plan-fold,fold-verification}.md`.

**Outcome.** A session runs `review-desk <kind> <repo> <title> <source>` as a background Bash
command. The item opens in Firefox on a local SvelteKit app styled with the Survey theme. Geoff
approves or rejects a PR or a design, or submits a triage list, and the command exits printing
his decision as JSON, which wakes the session. `pass-core` names the command as the hand-over for a
PR, a design, and found-item triage.

**Pass class:** `runner` (Geoff, 2026-10-11; `scripts/**`, `tests/**`, and
`claude/.claude/skills/pass-core/**` are on the `runner` map, and the rest is `ordinary`), with the
`live-account` flag: the session pushes a branch and opens a PR on `glw907/workstation`, and the
end-to-end check reads a real PR through `gh`. No `auth-data` path is touched. The app makes no
merge or account call.

**Out of scope** (design): a systemd service, an install or bootstrap step, a drift probe, an e2e
suite, a visual-fidelity pass, line comments, syntax highlighting beyond plain diff colors, and
anyone but Geoff. Also any edit to `~/Projects/cairn-themes` or `~/Projects/phonebook` (read only).

**End-to-end check.** On the close head, from the pass worktree, per the Close step 3:

1. `bash scripts/gate.sh` prints `gate exit: 0`.
2. One real PR (this pass's own draft PR), one design (the design doc above), and one triage list
   (three rows) are each handed over with the worktree's `bin/.local/bin/review-desk`. Each opens a
   Firefox tab, and a screenshot of each item page shows the Survey fonts and colors.
3. Approve on the PR, Reject with the note `needs a second pass` on the design, and the triage
   submitted with row 2 changed from its proposed disposition each make the waiting command exit 0
   and print that decision.
4. A form post carrying `Origin: http://evil.example` gets 403, and a request carrying
   `Host: evil.example:7907` gets 403.

**Clock estimate:** 255 task-minutes (T1 75, T2 70, T3 45, T4 15, close 50), inside the design's 3
to 3.5 hours plus 45 minutes of margin. T2 and T3 run as a pair, so the path is about 75 + 70 + 15 +
50 = 210 minutes.

## Launch

Prompt file: `docs/superpowers/plans/2026-10-11-review-desk-prompt.txt`. The plan lives on branch
`worktree-review-desk-lean` (planning commits, on top of the design branch `worktree-review-desk`).
The session continues that branch: its first act after `EnterWorktree` is `git merge --no-edit
worktree-review-desk-lean`. Launch from the main checkout, after every check prints what its
comment names:

```bash
git -C ~/.dotfiles fetch origin
git -C ~/.dotfiles branch --show-current                # must print main
git -C ~/.dotfiles rev-list --count HEAD..origin/main   # must print 0 (not behind)
git -C ~/.dotfiles rev-list --count origin/main..HEAD   # must print 0 (not ahead)
git -C ~/.dotfiles status --porcelain                   # must print nothing
git -C ~/.dotfiles rev-parse worktree-review-desk-lean origin/worktree-review-desk-lean   # two equal lines
claude agents --json                                    # no live session with cwd in ~/.dotfiles/.claude/worktrees/review-desk
cd ~/.dotfiles && claude --bg --model sonnet --effort medium --name review-desk \
  "$(git -C ~/.dotfiles show worktree-review-desk-lean:docs/superpowers/plans/2026-10-11-review-desk-prompt.txt)"
```

The prompt is read with `git show` because the plan is not on `main` until this pass's PR merges.

## Probed facts

Each was read from source or run on 2026-10-11; a task builds on these and never on recall.

- **Stack.** phonebook has no SvelteKit app yet; its `CLAUDE.md` names the stack ("SvelteKit 3,
  TypeScript, Tailwind CSS 4, daisyUI 5") and its `package.json` pins `typescript ~6.0`, `vitest
  ~4.1`, `@types/node ^26.6.4`. The review desk takes those ranges and, from npm on 2026-10-11:
  `@sveltejs/kit` 3.0.1 (peers `vite ^8.0.12`, `svelte ^5.57.1`, `typescript ^6.0.0`,
  `@sveltejs/vite-plugin-svelte ^7.0.0`; `engines.node >=22.17`, and the machine runs Node
  24.20.0), `@sveltejs/adapter-node` 6.0.0, `@sveltejs/vite-plugin-svelte` 7.3.1, `svelte` 5.57.2,
  `vite` 8.3.4, `svelte-check` 4.7.6 (peer `typescript ^5 || ^6`, so not TypeScript 7), `marked`
  18.1.0, and cairn-themes' own pins `tailwindcss` 4.3.3, `@tailwindcss/vite` 4.3.3, `daisyui`
  5.7.47, `@fontsource/spectral` 5.3.0, `@fontsource-variable/karla` 5.3.0, `@fontsource/monaspace-neon`
  5.3.0. `npm` is 11.19.0 with `ignore-scripts` false.
- **adapter-node 6 host and port.** `src/index.js`: `host = env('HOST', '0.0.0.0')`, `port =
  env('PORT', !path && '3000')`, `httpServer.listen({ path, host, port })`. So the app must start
  with `HOST=127.0.0.1`; the default binds every interface. The `ORIGIN` variable is gone in v6:
  the handler takes `origin` from the build (`export const origin =
  JSON.stringify(builder.config.paths.origin)`), and only without it derives one from the `Host`
  header with the protocol defaulting to `https` (`get_origin`). Left unset, a browser's `Origin:
  http://127.0.0.1:7907` would never match the derived `https://` origin, and every form post would
  fail the CSRF check.
- **SvelteKit 3 origin and CSRF.** `kit.paths.origin` ("The origin of your app, used for CSRF
  protection ... the trusted origin for CSRF checks on form submissions", `@since 3.0`). The check
  (`src/runtime/server/respond.js`, `csrf.js`) runs only when `!__SVELTEKIT_DEV__`, so only in the
  built app, and refuses a `POST`/`PUT`/`PATCH`/`DELETE` with a form content type whose `Origin`
  differs from the self origin and is not in `kit.csrf.trustedOrigins` (default `[]`): status 403,
  body `Cross-site POST form submissions are forbidden`. `checkOrigin` is "removed in 3.0". With
  `paths.origin` set, `url.origin` is that value whatever `Host` the request carried, so the `Host`
  check reads `request.headers.get('host')`, never `url.host`.
- **Rendered markdown needs the CSP.** `marked` 18.1.0 passes raw HTML and `javascript:` links
  through (probed: `<script>`, `<img onerror>`, and `[x](javascript:alert(1))` all survive
  `marked.parse`). A PR body is external input, and a script running in the app's origin could post a
  decision past the CSRF check. SvelteKit's `kit.csp` ("`'auto'` will use hashes for prerendered
  pages, and nonces for dynamically rendered pages") with `directives: { 'script-src': ['self'] }`
  blocks inline scripts, inline handlers, and `javascript:` URLs while SvelteKit's own scripts
  carry nonces.
- **gh.** `gh pr view <n> -R <owner>/<repo> --json body --jq .body` prints the body (`body` is a
  listed JSON field); `gh pr diff <n> -R <owner>/<repo>` prints the unified diff (no JSON field
  carries it). Both probed on `glw907/workstation#11`.
- **Desktop.** `firefox` is `/usr/bin/firefox` (layered RPM), the default browser
  (`org.mozilla.firefox.desktop`); `firefox --new-tab <url>` hands the URL to a running instance.
  `setsid -f` ("always fork") detaches a child so it outlives the command. `jq` and `curl` are on
  PATH (Homebrew). Port 7907 had no listener.
- **Survey core.** `~/Projects/cairn-themes/survey-theme/core/` holds `survey.css` (imports the
  other three), `fonts.css`, `theme.css`, `components.css`. Its header: it "does not import
  Tailwind or activate daisyUI; the consumer's entry sheet does both before importing this file".
  The specimen's entry sheet is the model: `@import "tailwindcss"; @plugin "daisyui" { themes:
  false; } @import "../core/survey.css";`. `fonts.css` imports the three Fontsource packages, which
  Vite bundles into the build, so nothing is fetched at view time. The Survey design spec:
  "Consumers copy the core in ... and install the three font packages. Each copy carries a header
  naming its source path and the `cairn-themes` commit it was copied from ... Neither consumer edits
  its copy." It also says a width uses an arbitrary value (`max-w-[72ch]`), never a named size
  such as `max-w-2xl`, because the core's `--spacing-*` keys collide with Tailwind's
  `--container-*` names. A worktree-isolated session's guard refuses `git -C
  ~/Projects/cairn-themes`, so the commit is read with `cat
  /var/home/glw907/Projects/cairn-themes/.git/refs/heads/main` (`dea98397...` at planning).
- **Gate.** `gitleaks dir` honors a `.gitignore` (probed: a fake key under an ignored
  `node_modules/` was not scanned), so `review-desk/.gitignore` listing `node_modules/`, `build/`,
  and `.svelte-kit/` keeps them out of the gate's scan.

## Interfaces

- **Command:** `review-desk <pr|design|triage> <repo> <title> <source>`. `<source>` is the PR
  number (with `<repo>` as `owner/name`), the design file's path, or the triage JSON file's path.
  It prints the decision JSON on stdout and exits 0.
- **State:** `${XDG_STATE_HOME:-$HOME/.local/state}/review-desk/items/<id>/`, `<id>` being
  `<YYYYmmddTHHMMSS>-<pid>`. The command writes the content (`body.md` and `diff.patch` for a PR,
  `doc.md` for a design, `triage.json` for triage) and then `item.json`, `{id, kind, repo, title,
  created}`, by temp file and `mv`, so the app never lists a half-written item. The app writes
  `decision.json` by temp file and rename, so the command never reads a partial one. The app reads
  the state root from `REVIEW_DESK_STATE` (`$env/dynamic/private`).
- **Triage input:** a JSON array of `{item, disposition, reason}`, `disposition` one of `now`,
  `defer`, `drop`.
- **Decision:** `{"decision":"approve"}`, `{"decision":"reject","note":"..."}` (the note may be
  empty), or `{"decision":"submit","rows":[{item, disposition, reason}, ...]}` with every row as
  Geoff left it.
- **Address:** `127.0.0.1:7907`, written in three places (the command, `svelte.config.js`
  `paths.origin`, and the `Host` check).

## Conventions every task follows

- **Gate.** `bash scripts/gate.sh`, with the Bash tool's `timeout: 600000`, re-issued on exit 75
  until it prints `gate exit:`. It is also the fast lane. Never fall back to a bare `bash
  scripts/check.sh` for an acceptance. A focused leg (`npm --prefix review-desk test`, `bash
  tests/review-desk.test.sh`) may run between edits; the task's acceptance is the gate.
- **The main checkout stays untouched.** Every tool runs from the worktree's own path
  (`bin/.local/bin/review-desk`), never as a bare name. No command writes `~/.dotfiles` outside
  `.claude/worktrees/`, and nothing writes `~/Projects/cairn-themes` or `~/Projects/phonebook`.
- **Comments.** `ts-conventions` for `.ts`, `svelte-conventions` for `.svelte`; load the skill
  before writing either. The em dash is banned in code comments.
- **UI.** Stock daisyUI 5 components first (the `daisyui` skill is the reference); widths take
  arbitrary values, per the Survey rule above.
- **Commits.** One commit per task, subject starting with the task id (`T1: Scaffold the review
  desk app`), imperative mood, specific files only, the app's `package-lock.json` included.
- **Clock.** At each task start the session writes `pass-task-clock` in its own pass worktree's git
  dir (`git rev-parse --absolute-git-dir`) with `task=<id>`, `start=<epoch>`, `estimate=<minutes>`,
  and removes it at the task's end. For the pair it writes one file (`task=T2+T3`,
  `estimate=70`) before dispatch, checks the overrun when both return, then removes it. Pair
  subagents write no clock file.
- **Stops.** A red the session cannot fix in two attempts, a merge conflict, or a clock stop: write
  `docs/STATUS.md` on the branch (task in flight, what failed, the one question), run `notify-send
  -u normal "review-desk: stopped"`, and wait. A pair subagent that cannot get its gate green in
  two attempts returns its work uncommitted, and the session applies this rule before merging
  either half.
- **Scope.** Anything beyond a task goes to the PR body's "Found, not done" list with a proposed
  disposition, never into the task. A pair subagent lists such items in its final report.

## Tasks

### T1. The app's shell: scaffold, Survey, item store, and the boundary

- **Outcome.**
  - `review-desk/` holds a SvelteKit 3 app on the stack above, with `@sveltejs/adapter-node`,
    Tailwind 4 through `@tailwindcss/vite`, and daisyUI 5. `package.json` scripts: `build`,
    `check` (`svelte-kit sync && svelte-check`), and `test` (`vitest run`). `review-desk/.gitignore`
    lists `node_modules/`, `build/`, and `.svelte-kit/`.
  - The four Survey core files are copied unedited into `review-desk/src/lib/survey/`, each with a
    first-line comment naming `cairn-themes/survey-theme/core/<file>` and the commit read as above.
    The entry sheet follows the specimen's three lines, and the three Fontsource packages are
    dependencies.
  - `svelte.config.js` sets `kit.paths.origin` to `http://127.0.0.1:7907` and `kit.csp.directives`
    to `{ 'script-src': ['self'] }`, and leaves `kit.csrf` at its default.
  - `src/hooks.server.ts` `handle` returns 403 unless `request.headers.get('host')` is exactly
    `127.0.0.1:7907`.
  - `src/lib/server/items.ts` lists the waiting items (an `item.json` and no `decision.json`),
    newest first by `created`; reads one item with its content; and writes a decision by temp
    file and rename. An item id from the URL passes a param matcher (`src/params/id.ts`,
    `^\d{8}T\d{6}-\d+$`) before it reaches the filesystem.
- **Files.** `review-desk/{package.json,package-lock.json,.gitignore,svelte.config.js,vite.config.ts,tsconfig.json}`,
  `review-desk/src/{app.html,app.css,app.d.ts,hooks.server.ts}`, `review-desk/src/params/id.ts`,
  `review-desk/src/lib/survey/*.css`, `review-desk/src/lib/server/items.ts`,
  `review-desk/src/routes/+layout.svelte`, the tests below, `scripts/check.sh`.
- **Risk class.** `runner` (the `scripts/check.sh` edit).
- **Acceptance.**
  - `scripts/check.sh` runs `npm --prefix review-desk run check` and `npm --prefix review-desk test`
    (after `npm --prefix review-desk ci` when `review-desk/node_modules` is absent) when any file
    under `review-desk/` differs from `git merge-base HEAD origin/main`, untracked files included,
    and prints a one-line skip otherwise.
  - `npm --prefix review-desk run build` writes `review-desk/build/index.js`, and the built CSS
    holds the Survey `--color-base-100: #f7f7f3` and an `@font-face` for Spectral whose `src` is a
    local `/_app/` path.
  - The gate prints `gate exit: 0`, and its log shows the two review-desk legs ran.
- **Test** (vitest, under `review-desk/src`). The `handle` hook passes a request with `host:
  127.0.0.1:7907` to `resolve` and returns 403 for `evil.example:7907`, `localhost:7907`, and a
  missing `Host`. The item store, over a temp state dir: lists two items newest first; skips an item
  holding `decision.json` and a directory with no `item.json`; reads a PR, a design, and a triage
  item's content; writes a decision that reads back as the JSON given, with no temp file left. The
  id matcher accepts `20261011T143000-4242` and refuses `..` and `a/b`.
- **Estimate.** 75 minutes.

### T2. The pages and the decision actions

- **Outcome.**
  - The index lists the waiting items, newest first, each row showing kind, repo, and title and
    linking to its item page.
  - The item page renders by kind. A PR shows its body as rendered markdown, then its diff in a
    `<pre>` with plain colors by line (added, removed, hunk header, file header). A design shows
    its document as rendered markdown at a reading width. A triage item shows one row per entry:
    the item text, a disposition select prefilled with the proposed value, and the reason in an
    editable text field.
  - Form actions: `approve` and `reject` (with an optional `note`, shown when Reject is chosen) on
    PR and design items, and `submit` on a triage item, which sends every row. Each writes the
    decision JSON through the item store and shows a "Decided" state. A decided or unknown id
    returns 404.
  - Markdown renders through `marked` in one module, `src/lib/markdown.ts`.
- **Files.** `review-desk/src/routes/+page.{svelte,server.ts}`,
  `review-desk/src/routes/item/[id=id]/+page.{svelte,server.ts}`, `review-desk/src/lib/markdown.ts`,
  their tests.
- **Risk class.** `ordinary`.
- **Acceptance.**
  - With items seeded under a temp `REVIEW_DESK_STATE`, the built app (`HOST=127.0.0.1 PORT=7907
    node review-desk/build`) answers the index and each item page with 200 to a `curl` carrying the
    right `Host`, and a Playwright MCP screenshot of each item page is read and shows the Survey
    fonts and colors.
  - The gate prints `gate exit: 0`.
- **Test** (vitest). The actions, called with a `Request` carrying form data over a temp state
  dir: `approve` writes `{"decision":"approve"}`; `reject` with `note` writes the note; `submit`
  with three rows, one changed, writes all three rows as sent; an action on a decided item fails
  with 404. The diff classifier labels `+x`, `-x`, `@@ ... @@`, `diff --git`, `+++ b/`, and `--- a/`
  lines, and labels a context line as context. `markdown.ts` renders a heading, a list, and a
  fenced code block.
- **Pair.** Runs as a pair with T3 (disjoint files), after T1 merges.
- **Estimate.** 70 minutes.

### T3. The `review-desk` command

- **Outcome.** `bin/.local/bin/review-desk` (bash, `set -euo pipefail`), per "Interfaces":
  1. Writes the item's content into a new item directory: for `pr`, the `gh` body and diff; for
     `design` and `triage`, a copy of the source file. Then it writes `item.json` by temp file and
     `mv`.
  2. Starts the app unless `curl -sf http://127.0.0.1:7907/` succeeds. It finds the app beside
     its own realpath (`<script dir>/../../../review-desk`), builds it once when `build/index.js`
     is absent (`npm ci` then `npm run build`), starts it with `HOST=127.0.0.1 PORT=7907
     REVIEW_DESK_STATE=<state root> setsid -f node <app>/build`, logging to
     `<state root>/server.log`, and polls `curl` until it answers (10 seconds at most, then exits 1
     naming the log).
  3. Opens `http://127.0.0.1:7907/item/<id>` with `setsid -f firefox --new-tab`.
  4. Polls for `decision.json` once a second, then prints it and exits 0.

  A wrong argument count or an unknown kind prints the usage line and exits 2.
- **Files.** `bin/.local/bin/review-desk` (new, executable), `tests/review-desk.test.sh` (new),
  `scripts/check.sh` (one `run` line for the test).
- **Risk class.** `runner` (`scripts/check.sh`, `tests/**`).
- **Acceptance.**
  - `bash tests/review-desk.test.sh` exits 0, and the gate prints `gate exit: 0` with that leg run.
- **Test** (`tests/review-desk.test.sh`, the `claude-clock-stop.test.sh` pattern, `XDG_STATE_HOME`
  and `PATH` pointed at temp fixtures). Stubs on `PATH`: `curl` that succeeds (the app "running"),
  `firefox` that records its arguments, `setsid` that drops `-f` and runs its command, and `gh`
  that prints a canned body or diff by subcommand. For each kind, the command runs in the
  background; the test waits for `item.json`, asserts it and the content files, checks the
  recorded `firefox` URL names the item id, writes a `decision.json`, and asserts the command exits
  0 printing exactly that JSON. A bad kind and a missing argument each exit 2.
- **Pair.** Runs as a pair with T2.
- **Estimate.** 45 minutes.

### T4. pass-core names the review desk as the hand-over

- **Outcome.** `claude/.claude/skills/pass-core/SKILL.md` "Close" replaces the `gh pr view <n> -R
  <owner>/<repo> --web` sentence. The session that hands a PR to Geoff runs `review-desk pr
  <owner>/<repo> "<title>" <n>` as a background Bash command, then hands the PR body's "Found, not
  done" items over as one `review-desk triage` item; each exit prints Geoff's decision as JSON.
  On approve, that session merges with `gh pr merge <n> --merge` and pulls the checkout as
  "Close" already says; on reject, it fixes forward from the note. It acts on each triage row as
  the existing triage paragraph says. A design brought for approval is handed over with
  `review-desk design`. A pass that merges its own PR still opens nothing. The "Geoff reads the PR
  and merges" line in "Lifecycle" step 6 changes to match.
- **Files.** `claude/.claude/skills/pass-core/SKILL.md`.
- **Risk class.** `runner`.
- **Acceptance.** `grep -n 'review-desk' claude/.claude/skills/pass-core/SKILL.md` shows the PR,
  triage, and design hand-overs; `grep -c 'gh pr view' claude/.claude/skills/pass-core/SKILL.md`
  prints 0; the gate prints `gate exit: 0` (its tellgrader and Vale nets read the prose).
- **Test.** Prose only; the gate is the check.
- **Estimate.** 15 minutes.

### Close

Per pass-core "Close" and dotfiles-pass "Close checklist", in order:

1. `git fetch origin` and merge `origin/main` into the branch (a conflict is a stop). The gate on
   the close head prints `gate exit: 0` (the full-suite home).
2. Push `glw907/workstation` and open the PR as a draft, so step 3 has a real PR.
3. The end-to-end check above, run from the worktree with its own `bin/.local/bin/review-desk`
   and a temp `XDG_STATE_HOME`. The session drives each item page with the Playwright MCP tools
   (Chromium) at the same URL Firefox opened, clicks the decision, and reads each background
   command's output. The cross-origin and `Host` refusals are `curl` posts. It stops the app it
   started (`pkill -f '<worktree>/review-desk/build'`) and records each step's result for the PR
   body.
4. `diff-reviewer` at whole-branch scope reads the branch against this plan, loading
   `ts-conventions`. One batched fix chain follows if it returns `fix`, each finding quoted
   verbatim as the fix's acceptance, then the gate again.
5. `claude-tooling-sync verify` passes; one `gitleaks git` branch-history scan is clean.
6. `docs/STATUS.md` drops the review desk from the conductor queue and names this PR as pending
   Geoff's read.
7. The PR body: what landed (task id, commit), the review verdict, the end-to-end results;
   "What goes live" (at Geoff's merge and pull, `stow -R bin` puts `review-desk` on PATH, and
   `pass-core`'s new hand-over applies to every session; rollback is `git revert -m 1 <merge>`
   then a pull); "Found, not done", each item with a proposed disposition and a one-line reason,
   seeded with the "Later" list below plus anything the tasks found; and the score rows
   (`cairn-run-gate --records <toplevel> <branch>`). Mark the PR ready.

Geoff reads and merges.

- **Estimate.** 50 minutes.

## Later

Not built in this pass; each goes to the PR's "Found, not done" with a proposed disposition.

- A running app keeps serving its old build after a merge changes `review-desk/`; today the fix is
  `pkill -f review-desk/build` and `rm -rf ~/.dotfiles/review-desk/build`, and the next hand-over
  rebuilds.
- Decided items stay in the state directory; nothing prunes them.
- Two hand-overs that both find the app down can race to start it; the second start fails on the
  bound port and its poll finds the first one's app answering.
