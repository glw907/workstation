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
   (three rows) are each handed over with the worktree's `bin/.local/bin/review-desk`, the first
   with no build present and nothing on port 7907, so the command builds and starts the close
   head's app itself. Each item page, opened in Chromium at the URL the command handed Firefox,
   renders, and on it `getComputedStyle(document.body)` gives a `backgroundColor` of `rgb(247, 247,
   243)` (or `rgb(17, 23, 30)` when the browser prefers dark) and a `fontFamily` naming `Karla
   Variable`. A screenshot of each is the human-readable record. T3's stub test is the evidence that
   the command calls `firefox --new-tab` with the item URL.
3. Approve on the PR, Reject with the note `needs a second pass` on the design, and the triage
   submitted with row 2 changed from its proposed disposition each make the waiting command exit 0
   and print that decision; the PR decision carries the `head` the item was fetched at.
4. Security: `ss -ltnH 'sport = :7907' | awk '{print $4}'` prints exactly `127.0.0.1:7907`;
   `curl -sI` of an item page shows `content-security-policy: script-src 'self' 'nonce-`; a GET
   with `Host: evil.example:7907` gets 403 (the hook); a form post to a live item's `?/approve`
   with the right `Host` and `Origin: http://evil.example` gets 403 with the body `Cross-site POST
   form submissions are forbidden`, and no `decision.json` appears.

**Clock estimate:** 310 task-minutes (T1 85, T2 80, T3 65, T4 20, close 60), against the design's
180 to 210 and under pass-core's twice-the-estimate line of 420. T2 and T3 run as a pair, so the
path is about 85 + 80 + 20 + 60 = 245 minutes.

## Launch

Prompt file: `docs/superpowers/plans/2026-10-11-review-desk-prompt.txt`. The plan lives on branch
`worktree-review-desk-lean` (planning commits, on top of the design branch `worktree-review-desk`).
The executing session works in a new worktree, `review-desk-v1` (the name `review-desk` is taken by
the design worktree, and `EnterWorktree` would reopen it), and its first act after `EnterWorktree`
is `git merge --no-edit worktree-review-desk-lean`. Launch from the main checkout, after every check
prints what its comment names:

```bash
git -C ~/.dotfiles fetch origin
git -C ~/.dotfiles branch --show-current                # must print main
git -C ~/.dotfiles rev-list --count HEAD..origin/main   # must print 0 (not behind)
git -C ~/.dotfiles rev-list --count origin/main..HEAD   # must print 0 (not ahead)
git -C ~/.dotfiles status --porcelain                   # must print nothing
git -C ~/.dotfiles rev-parse worktree-review-desk-lean origin/worktree-review-desk-lean   # two equal lines
git -C ~/.dotfiles worktree list | grep -c '/worktrees/review-desk-v1 '   # must print 0
claude agents --json                                    # no live session whose cwd is exactly ~/.dotfiles/.claude/worktrees/review-desk-v1
cd ~/.dotfiles && claude --bg --model sonnet --effort medium --name review-desk-v1 \
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
  5.3.0. Each is that package's newest production version. `npm` is 11.19.0 with `ignore-scripts`
  false.
- **SvelteKit 3, the project files.** SvelteKit 3 drops several SvelteKit 2 habits; a scaffold of
  exactly this file set, on the stack above, passed `svelte-kit sync && svelte-check` (0 errors),
  `vitest run`, and `vite build` (fold probe, 2026-10-11). Paths cite the `@sveltejs/kit` 3.0.1
  package.
  - **Config lives in `vite.config.ts`; a `svelte.config.js` fails the build.**
    `src/exports/vite/index.js:276-279` throws `config_file_unsupported` ("`svelte.config.js` is no
    longer used. Please pass configuration via the `sveltekit(...)` plugin in your Vite config.",
    `src/messages/build-errors.js:247`) when either `svelte.config.js` or `.ts` exists. The options
    sit flat in the plugin call, with no `kit:` key. The probed file:
    `plugins: [tailwindcss(), sveltekit({ adapter: adapter(), paths: { origin:
    'http://127.0.0.1:7907' }, csp: { directives: { 'script-src': ['self'] } } })]`, importing
    `adapter` from `@sveltejs/adapter-node`, `sveltekit` from `@sveltejs/kit/vite`, and
    `tailwindcss` from `@tailwindcss/vite`.
  - **`$lib` is gone; `#lib` comes from `package.json` `imports`.** `src/exports/vite/index.js:75-79`
    lists `$lib` in `removed_modules` ("`$lib` has been removed. Use `#lib` instead",
    `build-errors.js:527`). The probed `package.json` carries `"type": "module"` and
    `"imports": { "#lib": "./src/lib", "#lib/*": "./src/lib/*" }` (the shape of kit's own
    `src/core/sync/write_tsconfig/test-app/package.json`), and imports name the extension:
    `import { render } from '#lib/markdown.ts'`.
  - **`tsconfig.json` extends `$app/tsconfig`.** `src/core/sync/write_tsconfig/index.js:60` gives
    the expected shape, `extends: '$app/tsconfig', include: ['src', 'test', '*']`; `svelte-kit sync`
    writes the parent file.
  - **Param matchers live in one file, `src/params.ts`, through `defineParams`.**
    `src/core/config/index.js:180` sets `files.params` to `src/params`, resolved as an entry
    (`src/params.ts` or `src/params/index.ts`, `create_manifest_data/index.js:110-111`), and
    `src/core/params.js:58` throws `params_export_missing` unless it exports `params`. The probed
    file: `export const params = defineParams({ id: (param) => (/^\d{8}T\d{6}-\d+$/.test(param) ?
    param : undefined) })`, from `@sveltejs/kit/params`. `defineParams` wraps a function as a
    Standard Schema (`src/exports/params/index.js:40-68`), so a test calls
    `params.id['~standard'].validate(x)`: `{ value: x }` on a match, an object with `issues`
    otherwise.
  - **Environment variables are declared in `src/env.ts` and read from `$app/env/private`.**
    `types/index.d.ts:1156-1157`: variables "can be configured by exporting a `variables` object
    from `src/env.ts`, using `defineEnvVars`"; a non-public one "can be imported from
    `$app/env/private`" (`:1163`). `$env/dynamic/private` still loads but warns
    (`src/runtime/env/dynamic/private.js:7`). A declared variable is validated when the app
    starts, and also during `vite build` (its "Analysing routes" step) and on import under vitest:
    declared as `REVIEW_DESK_STATE: {}`, the probe's build and tests failed with `env_invalid`
    ("Value is missing"). Declared as `REVIEW_DESK_STATE: { schema: (value) => value ?? '' }`
    ("Returning `undefined` is valid", `:1177`), both pass with the variable unset. A module
    reads it as `import { REVIEW_DESK_STATE } from '$app/env/private'`. Setting `process.env` inside
    a test does not reach it; a test that needs a value mocks the module (probed):
    `const state = vi.hoisted(() => ({ root: '' })); vi.mock('$app/env/private', () => ({ get
    REVIEW_DESK_STATE() { return state.root; } }))`.
  - **Types moved.** `Handle` is exported from `@sveltejs/kit/hooks` (`types/index.d.ts:1236-1245`),
    not `@sveltejs/kit`: the probe's `svelte-check` failed on the old import. `error()` takes a
    string message (`error(404, 'Not found')`; an object body is deprecated, `:1008`). `fail`,
    `./$types`' `PageServerLoad` and `Actions` are unchanged.
- **adapter-node 6 host and port.** `src/index.js`: `host = env('HOST', '0.0.0.0')`, `port =
  env('PORT', !path && '3000')`, `httpServer.listen({ path, host, port })`. So the app must start
  with `HOST=127.0.0.1`; the default binds every interface. The `ORIGIN` variable is gone in v6:
  the handler takes `origin` from the build (`export const origin =
  JSON.stringify(builder.config.paths.origin)`), and only without it derives one from the `Host`
  header with the protocol defaulting to `https` (`get_origin`). Left unset, a browser's `Origin:
  http://127.0.0.1:7907` would never match the derived `https://` origin, and every form post would
  fail the CSRF check. Probed: started as `HOST=127.0.0.1 PORT=7907 setsid -f node build`, `ss
  -ltnH 'sport = :7907'` prints `LISTEN 0 511 127.0.0.1:7907 0.0.0.0:*`; the fourth column is the
  local address, and the `0.0.0.0:*` after it is the peer column, present on every listener.
- **SvelteKit 3 origin and CSRF.** `paths.origin` ("The origin of your app, used for CSRF
  protection ... the trusted origin for CSRF checks on form submissions", `@since 3.0`). The check
  (`src/runtime/server/respond.js`, `csrf.js`) runs only when `!__SVELTEKIT_DEV__`, so only in the
  built app, and before `handle`. It refuses a `POST`/`PUT`/`PATCH`/`DELETE` with a form content
  type whose `Origin` differs from the self origin (a missing `Origin` included) and is not in
  `csrf.trustedOrigins` (default `[]`): status 403, body `Cross-site POST form submissions are
  forbidden`. `checkOrigin` is "removed in 3.0". With `paths.origin` set, `url.origin` is that
  value whatever `Host` the request carried, so the `Host` check reads
  `request.headers.get('host')`, never `url.host`. Probed on the built scaffold: a GET with `Host:
  evil.example:7907` gets the hook's 403; a `curl -d` post with that `Host` gets the CSRF 403
  before the hook runs, so only a GET tests the `Host` check; a post with `Origin:
  http://127.0.0.1:7907` gets 200.
- **After a form action, the page's `load` runs in the same request** (`src/runtime/server/page/index.js`
  runs the action, then `load_server_data` for each node, from line 182), so a page that a decision
  makes unloadable renders as an error page instead of its result.
- **Rendered markdown: escape raw HTML, keep the CSP as the backstop.** `marked` 18.1.0 passes raw
  HTML and `javascript:` links through (probed: `<script>`, `<img onerror>`, and
  `[x](javascript:alert(1))` all survive `marked.parse`). A PR body is external input, and raw
  markup needs no script to forge a decision: a `<form method="post" action="?/approve">` posts from
  the app's own origin and passes the CSRF check, and a `<style>` can hide the real buttons. The
  defense is a renderer that escapes every raw HTML token, block and inline. Probed: `new Marked({
  renderer: { html({ text }) { return escape(text); } } })`, with `escape` replacing `&`, `<`, `>`,
  and `"`, turns `<form>`, `<style>`, and `<script>` input into `&lt;form` text with no element.
  The CSP stays: `csp: { directives: { 'script-src': ['self'] } }` (nonces on dynamically rendered
  pages) blocks inline scripts, inline handlers, and `javascript:` URLs. Probed header:
  `content-security-policy: script-src 'self' 'nonce-...'`.
- **gh.** `gh pr view <n> -R <owner>/<repo> --json body,headRefOid` prints the body and the head
  commit (both listed JSON fields); `gh pr diff <n> -R <owner>/<repo>` prints the unified diff (no
  JSON field carries it). `gh pr merge --match-head-commit SHA` refuses the merge unless the PR head
  is that commit (`gh pr merge --help`). Fetching the head with the body first, then the diff, means
  a push between the two moves the head, so the merge is refused rather than taking unseen code.
- **Desktop.** `firefox` is `/usr/bin/firefox` (layered RPM), the default browser
  (`org.mozilla.firefox.desktop`); `firefox --new-tab <url>` hands the URL to a running instance.
  `setsid -f` ("always fork") detaches a child so it outlives the command. `jq`, `curl`, and `flock`
  are on PATH (Homebrew). Port 7907 had no listener. `/tmp` is `tmpfs` and the state dir is under
  `$HOME`, so a temp file outside the target directory makes `rename` fail with `EXDEV` (Node) or
  turns `mv` into copy-then-unlink.
- **Shell mechanics** (probed with a scratch script). With `trap '<cleanup>' EXIT` and `trap 'exit
  143' TERM HUP INT`, a SIGTERM to a script polling with `sleep 1` runs the cleanup and exits 143
  within the current sleep. `exec 9>"$lock"; flock 9` serializes two shells: the second waits until
  the first closes fd 9. `pkill -f '<path>/review-desk/build'` run from a Bash tool call also
  matches the calling shell, whose command line holds the pattern, and kills it (the probe's call
  died with exit 144); the bracket form `pkill -f '<path>/review-desk/[b]uild'` matches the node
  process and not the shell.
- **Survey core.** `~/Projects/cairn-themes/survey-theme/core/` holds `survey.css` (imports the
  other three), `fonts.css`, `theme.css`, `components.css`. Its header: it "does not import
  Tailwind or activate daisyUI; the consumer's entry sheet does both before importing this file".
  The specimen's entry sheet is the model: `@import "tailwindcss"; @plugin "daisyui" { themes:
  false; } @import "../core/survey.css";`, and its body is `<body class="font-body bg-base-100
  text-base-content">`; the core defines `--font-body` but applies it to nothing, so without that
  class the page keeps the browser's font. `theme.css` defines `survey` (`default: true`, base-100
  `#f7f7f3`) and `survey-dark` (`prefersdark: true`, base-100 `#11171e`). `fonts.css` imports the
  three Fontsource packages, which Vite bundles into the build, so nothing is fetched at view time;
  the probed build's CSS holds `--color-base-100:#f7f7f3` (minified, no space) and Spectral
  `@font-face` sources `url(./spectral-....woff2)` (relative, beside the CSS under `_app/`). The
  Survey design spec: "Consumers copy the core in ... and install the three font packages. Each copy
  carries a header naming its source path and the `cairn-themes` commit it was copied from ...
  Neither consumer edits its copy." A width uses an arbitrary value (`max-w-[72ch]`), never a named
  size such as `max-w-2xl`, because the core's `--spacing-*` keys collide with Tailwind's
  `--container-*` names. A worktree-isolated session's guard refuses `git -C
  ~/Projects/cairn-themes`, so the commit is read with `cat
  /var/home/glw907/Projects/cairn-themes/.git/refs/heads/main` (`dea98397...` at planning).
- **Gate.** `gitleaks dir` honors a `.gitignore` (probed: a fake key under an ignored
  `node_modules/` was not scanned), so `review-desk/.gitignore` listing `node_modules/`, `build/`,
  and `.svelte-kit/` keeps them out of the gate's scan. The gate's `tellgrader go check` and `vale
  style fixtures` legs test those tools and read no skill prose (`scripts/check.sh:38,41`); prose is
  checked by the `PostToolUse` `vale-hook` and `tellgrader --hook` on each `Write` or `Edit`
  (`claude/.claude/settings.json:93-107`).

## Interfaces

- **Command:** `review-desk <pr|design|triage> <repo> <title> <source>`. `<source>` is the PR
  number (with `<repo>` as `owner/name`), the design file's path, or the triage JSON file's path.
  Its only stdout is the decision JSON, and it exits 0 on a decision. Build, server, and Firefox
  output go to `server.log`.
- **State:** the state root is `${XDG_STATE_HOME:-$HOME/.local/state}/review-desk`, passed to the
  app as `REVIEW_DESK_STATE`. Items live in `<root>/items/<id>/`, `<id>` being
  `<YYYYmmddTHHMMSS>-<pid>` (it matches the `id` param matcher); `server.log` and `start.lock` sit
  in the root. The command writes the content (`body.md` and `diff.patch` for a PR, `doc.md` for a
  design, `triage.json` for triage) and then `item.json`, `{id, kind, repo, title, created}` plus
  `head` for a PR, where `created` is ISO 8601 UTC (`date -u +%Y-%m-%dT%H:%M:%SZ`), sorted as a
  string. The app writes `decision.json`. Every write goes through a temp file in the item directory
  itself (`item.json.tmp`, `decision.json.tmp`) and a rename, so neither side reads a partial file.
- **Waiting items:** an item is waiting while it has `item.json` and no `decision.json`. The
  command removes `item.json` when it exits without a decision (a stop, a closed session), so the
  index drops an item nobody waits for.
- **Triage input:** a JSON array of `{item, disposition, reason}`, `disposition` one of `now`,
  `defer`, `drop`.
- **Decision:** `{"decision":"approve"}`, `{"decision":"reject","note":"..."}` (the note may be
  empty), or `{"decision":"submit","rows":[{item, disposition, reason}, ...]}` with every row as
  Geoff left it. For a PR the command prints it with the item's `head` added (`{"decision":
  "approve","head":"<sha>"}`).
- **Address:** `127.0.0.1:7907`, written in three places (the command, `vite.config.ts`
  `paths.origin`, and the `Host` check).

## Conventions every task follows

- **Gate.** `bash scripts/gate.sh`, with the Bash tool's `timeout: 600000`, re-issued on exit 75
  until it prints `gate exit:`. It is also the fast lane. Never fall back to a bare `bash
  scripts/check.sh` for an acceptance. A focused leg (`npm --prefix review-desk test`, `bash
  tests/review-desk.test.sh`) may run between edits; the task's acceptance is the gate.
- **SvelteKit 3.** Every app file follows the "SvelteKit 3, the project files" probed facts: no
  `svelte.config.js`, no `$lib`, no `src/params/` directory, no `$env/dynamic/private`. A SvelteKit
  2 habit that fails is checked against those facts before any other fix.
- **The main checkout stays untouched.** Every tool runs from the worktree's own path
  (`bin/.local/bin/review-desk`), never as a bare name. No command writes `~/.dotfiles` outside
  `.claude/worktrees/`, and nothing writes `~/Projects/cairn-themes` or `~/Projects/phonebook`.
- **Stopping an app.** Only by its worktree path in bracket form, `pkill -f
  '<worktree>/review-desk/[b]uild'`, then `curl -s http://127.0.0.1:7907/` must fail.
- **Comments.** `ts-conventions` for `.ts`, `svelte-conventions` for `.svelte`; load the skill
  before writing either. The em dash is banned in code comments.
- **UI.** Stock daisyUI 5 components first (the `daisyui` skill is the reference); widths take
  arbitrary values, per the Survey rule above.
- **Commits.** One commit per task, subject starting with the task id (`T1: Scaffold the review
  desk app`), imperative mood, specific files only, the app's `package-lock.json` included.
- **Clock.** At each task start the session writes `pass-task-clock` in its own pass worktree's git
  dir (`git rev-parse --absolute-git-dir`) with `task=<id>`, `start=<epoch>`, `estimate=<minutes>`,
  and removes it at the task's end. For the pair it writes one file (`task=T2+T3`,
  `estimate=80`) before dispatch, checks the overrun when both return, then removes it. Pair
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
  - `review-desk/` holds a SvelteKit 3 app on the stack above, laid out per the "SvelteKit 3, the
    project files" facts, with `@sveltejs/adapter-node`, Tailwind 4 through `@tailwindcss/vite`,
    and daisyUI 5. Every package in the stack is installed here, `marked` included, so T2 and T3
    change no `package.json`. `package.json` scripts: `build` (`vite build`), `check` (`svelte-kit
    sync && svelte-check`), and `test` (`vitest run`). `review-desk/.gitignore` lists
    `node_modules/`, `build/`, and `.svelte-kit/`.
  - The four Survey core files are copied unedited into `review-desk/src/lib/survey/`, each with a
    first-line comment naming `cairn-themes/survey-theme/core/<file>` and the commit read as above.
    The entry sheet follows the specimen's three lines, the three Fontsource packages are
    dependencies, and `app.html`'s body carries the specimen's `font-body bg-base-100
    text-base-content`.
  - `vite.config.ts` passes `sveltekit({...})` the adapter, `paths.origin`
    `http://127.0.0.1:7907`, and `csp.directives` `{ 'script-src': ['self'] }`, and leaves `csrf` at
    its default.
  - `src/env.ts` declares `REVIEW_DESK_STATE` with the probed `schema: (value) => value ?? ''`.
  - `src/hooks.server.ts` `handle` returns 403 unless `request.headers.get('host')` is exactly
    `127.0.0.1:7907`.
  - `src/lib/server/items.ts` takes the state root as an argument (the routes pass
    `REVIEW_DESK_STATE`) and lists the waiting items, newest first by `created`; reads one item
    with its content and whether it is decided; and writes a decision by temp file in the item
    directory and rename. An item id from the URL passes the `id` matcher in `src/params.ts`
    before it reaches the filesystem.
- **Files.** `review-desk/{package.json,package-lock.json,.gitignore,vite.config.ts,tsconfig.json}`,
  `review-desk/src/{app.html,app.css,env.ts,params.ts,hooks.server.ts}`,
  `review-desk/src/lib/survey/*.css`, `review-desk/src/lib/server/items.ts`,
  `review-desk/src/routes/+layout.svelte`, the tests below, `scripts/check.sh`.
- **Risk class.** `runner` (the `scripts/check.sh` edit).
- **Acceptance.**
  - `scripts/check.sh` runs `npm --prefix review-desk run check` and `npm --prefix review-desk test`
    (after `npm --prefix review-desk ci` when `review-desk/node_modules` is absent) when any file
    under `review-desk/` differs from `git merge-base HEAD origin/main`, untracked files included,
    and prints a one-line skip otherwise.
  - `npm --prefix review-desk run build` writes `review-desk/build/index.js`; `grep -E
    -- '--color-base-100: ?#f7f7f3'` finds the Survey value in the built CSS under
    `review-desk/build/client/_app/`, and its Spectral `@font-face` `src` is a bundled `.woff2`
    URL with no `http`.
  - The gate prints `gate exit: 0`, and its records (`cairn-run-gate --records`) show the two
    review-desk legs ran.
- **Test** (vitest, under `review-desk/src`). The `handle` hook passes a request with `host:
  127.0.0.1:7907` to `resolve` and returns 403 for `evil.example:7907`, `localhost:7907`, and a
  missing `Host`. The item store, over a temp state root: lists two items newest first; skips an
  item holding `decision.json` and a directory with no `item.json`; reads a PR, a design, and a
  triage item's content; writes a decision that reads back as the JSON given, with no temp file
  left. The id matcher accepts `20261011T143000-4242` and refuses `..` and `a/b`.
- **Estimate.** 85 minutes.

### T2. The pages and the decision actions

- **Outcome.**
  - The index lists the waiting items, newest first, each row showing kind, repo, and title and
    linking to its item page.
  - The item page renders by kind. A PR shows its body as rendered markdown, then its diff in a
    `<pre>` with plain colors by line, classified in `src/lib/diff.ts`: added, removed, hunk header,
    file header, context. A design shows its document as rendered markdown at a reading width. A
    triage item shows one row per entry: the item text, a disposition select prefilled with the
    proposed value, and the reason in an editable text field. Diff lines and triage text render
    with `{text}` interpolation in a classed element, never `{@html}`; only `markdown.ts` output
    goes through `{@html}`.
  - Markdown renders through `marked` in one module, `src/lib/markdown.ts`, with the probed
    renderer that escapes every raw HTML token.
  - Form actions: `approve` and `reject` (with an optional `note`, shown when Reject is chosen) on
    PR and design items, and `submit` on a triage item. `submit` takes each row's item text from
    `triage.json` by index and only `disposition` and `reason` from the form; a posted row count
    that differs from the file's, or a disposition outside `now`, `defer`, `drop`, fails with 400.
    Each action writes the decision JSON through the item store.
  - `load` returns 404 for an unknown id (no `item.json`). A decided item's page loads with 200 and
    shows a "Decided" state with no form, so the page that answers a decision post shows
    "Decided". An action on a decided or unknown id fails with 404.
- **Files.** `review-desk/src/routes/+page.{svelte,server.ts}`,
  `review-desk/src/routes/item/[id=id]/+page.{svelte,server.ts}`, `review-desk/src/lib/markdown.ts`,
  `review-desk/src/lib/diff.ts`, their tests.
- **Risk class.** `ordinary`.
- **Acceptance.**
  - With items seeded under a temp `REVIEW_DESK_STATE` (one PR body holding `<form
    method="post" action="?/approve"><button>Reject</button></form>`), the built app
    (`HOST=127.0.0.1 PORT=7907 REVIEW_DESK_STATE=<temp> node review-desk/build`) answers the index
    and each item page with 200 to a `curl` carrying the right `Host`; the PR page's HTML holds
    `&lt;form` and no `<form method="post" action="?/approve"><button>Reject`; `curl -sI` of an item
    page shows `content-security-policy` with `script-src 'self' 'nonce-`. The subagent then stops
    the app it started, per "Stopping an app".
  - The gate prints `gate exit: 0`.
- **Test** (vitest; the route tests mock `$app/env/private` per the probed facts). The actions,
  called with a `Request` carrying form data over a temp state root: `approve` writes
  `{"decision":"approve"}`; `reject` with `note` writes the note; `submit` with three rows, one
  changed, writes all three rows with the file's item text; `submit` with two rows, or with
  disposition `later`, fails with 400; an action on a decided item fails with 404. `load` on a
  decided item returns its decided state, and on an unknown id throws 404. The diff classifier
  labels `+x` added, `-x` removed, `@@ -1 +1 @@` hunk, and `diff --git a/x b/x`, `+++ b/x`, and
  `--- a/x` each file header, and a line starting with a space context. `markdown.ts` turns
  `<form>`, `<style>`, and `<script>` input, block and inline, into escaped text with no element.
- **Pair.** Runs as a pair with T3 (disjoint files), after T1 merges.
- **Estimate.** 80 minutes.

### T3. The `review-desk` command

- **Outcome.** `bin/.local/bin/review-desk` (bash, `set -euo pipefail`), per "Interfaces":
  1. Writes the item's content into a new item directory: for `pr`, the body and `headRefOid` from
     one `gh pr view --json body,headRefOid`, then the `gh pr diff`; for `design` and `triage`, a
     copy of the source file. Then it writes `item.json` by temp file and `mv`, and sets the probed
     traps: on exit without a `decision.json` it removes `item.json`, and TERM, HUP, and INT exit
     143.
  2. Under `flock` on `<root>/start.lock`, starts the app unless `curl -sf
     http://127.0.0.1:7907/` succeeds. It finds the app at the canonical path `realpath "<script
     dir>/../../../review-desk"`, `<script dir>` taken from its own realpath; builds it when
     `build/index.js` is absent (`npm ci` then `npm run build`); starts it with `HOST=127.0.0.1
     PORT=7907 REVIEW_DESK_STATE=<root> setsid -f node <app>/build`; and polls `curl` until it
     answers (10 seconds at most, then exits 1 naming the log). Build and server output go to
     `<root>/server.log`.
  3. Checks `curl -sf http://127.0.0.1:7907/item/<id>`; if the running app does not serve the item
     (an app started on another state root or an old build), it exits 1 with "an app on 7907 does
     not serve this state root; stop it with pkill -f 'review-desk/[b]uild'".
  4. Opens `http://127.0.0.1:7907/item/<id>` with `setsid -f firefox --new-tab`, output to the log.
  5. Polls for `decision.json` once a second, then prints it (with `head` added for a PR, `jq -c
     --arg h "$head" '. + {head: $h}'`) and exits 0.

  A wrong argument count or an unknown kind prints the usage line and exits 2.
- **Files.** `bin/.local/bin/review-desk` (new, executable), `tests/review-desk.test.sh` (new),
  `scripts/check.sh` (one `run` line for the test).
- **Risk class.** `runner` (`scripts/check.sh`, `tests/**`).
- **Acceptance.**
  - `bash tests/review-desk.test.sh` exits 0, and the gate prints `gate exit: 0` with that leg run.
- **Test** (`tests/review-desk.test.sh`, the `claude-clock-stop.test.sh` pattern, `XDG_STATE_HOME`
  and `PATH` pointed at temp fixtures). Stubs on `PATH`: `curl` that succeeds (the app "running"),
  `firefox` that records its arguments, `setsid` that drops `-f` and runs its command, and `gh`
  that prints a canned `{"body":...,"headRefOid":"abc123"}` or diff by subcommand. Every wait is
  bounded (50 tries of `sleep 0.1`, then the test kills the background job and fails). For each
  kind, the command runs in the background; the test waits for `item.json`, asserts it (the id
  matches `^[0-9]{8}T[0-9]{6}-[0-9]+$`, `created` is ISO 8601 UTC, a PR carries `head`) and the
  content files, waits for the `firefox` record and checks it is `--new-tab` with the item URL,
  writes a `decision.json`, and asserts the command exits 0 printing exactly that JSON (with
  `"head":"abc123"` for the PR). A TERM to a waiting command exits 143 and leaves no `item.json`. A
  `curl` stub that answers `/` but fails `/item/` makes the command exit 1. A bad kind and a
  missing argument each exit 2.
- **Pair.** Runs as a pair with T2.
- **Estimate.** 65 minutes.

### T4. pass-core names the review desk as the hand-over

- **Outcome.** `claude/.claude/skills/pass-core/SKILL.md`:
  - "Close" replaces the `gh pr view <n> -R <owner>/<repo> --web` sentence. The session that hands
    a PR to Geoff runs `review-desk pr <owner>/<repo> "<title>" <n>` as a background Bash command,
    then hands the PR body's "Found, not done" items over as one `review-desk triage` item, and
    stays open until each command exits with Geoff's decision as JSON. An approve on the desk is
    Geoff's merge authorization, the one a launch prompt's "never merge" otherwise withholds: the
    session merges with `gh pr merge <n> --merge --match-head-commit <head>`, `<head>` from the
    decision, and pulls the checkout as "Close" already says. On reject, it fixes forward from the
    note. It acts on each triage row as the existing triage paragraph says. A pass that merges its
    own PR still opens nothing.
  - "Lifecycle" step 1 hands a design brought for approval over with `review-desk design`, and
    step 6's "Geoff reads the PR and merges" changes to match "Close".
- **Files.** `claude/.claude/skills/pass-core/SKILL.md`.
- **Risk class.** `runner`.
- **Acceptance.** `grep -c 'gh pr view' claude/.claude/skills/pass-core/SKILL.md` prints 0, and
  `grep -n` finds each behavior: `review-desk pr`, `review-desk triage`, and `review-desk design`
  (the last in "Lifecycle"); `stays open until`; `--match-head-commit`; `fixes forward`. The
  `PostToolUse` `vale-hook` and `tellgrader --hook` report nothing on the edit, and the gate prints
  `gate exit: 0`.
- **Test.** Prose only; the greps and the hooks are the check.
- **Estimate.** 20 minutes.

### Close

Per pass-core "Close" and dotfiles-pass "Close checklist", in order:

1. `git fetch origin` and merge `origin/main` into the branch (a conflict is a stop). The gate on
   the close head prints `gate exit: 0` (the full-suite home).
2. Push `glw907/workstation` and open the PR as a draft whose body is the step 7 skeleton (its
   headings and the "Found, not done" list as seeded so far), so step 3's PR item renders headings
   and a list.
3. The end-to-end check above, run from the worktree with its own `bin/.local/bin/review-desk`
   and a temp `XDG_STATE_HOME`. It starts with `rm -rf review-desk/build`, and `curl -s
   http://127.0.0.1:7907/` must fail (stop any leftover app per "Stopping an app" first), so the
   first hand-over builds and starts the close head's app. The session drives each item page with
   the Playwright MCP tools (Chromium) at the URL the command handed Firefox, reads the computed
   style, clicks the decision, and reads each background command's output. The security checks are
   the `ss` and `curl` lines in step 4. The e2e decisions are test decisions: the session acts on
   none of them, and never merges. It stops the app per "Stopping an app" and records each step's
   result for the PR body.
4. `diff-reviewer` at whole-branch scope reads the branch against this plan, loading
   `ts-conventions`. One batched fix chain follows if it returns `fix`, each finding quoted
   verbatim as the fix's acceptance, then the gate again.
5. `claude-tooling-sync verify` passes; one `gitleaks git` branch-history scan is clean.
6. `docs/STATUS.md` drops the review desk from the conductor queue and names this PR as pending
   Geoff's read.
7. The PR body: what landed (task id, commit), the review verdict, the end-to-end results;
   "What goes live" (after Geoff merges and pulls, he runs `stow -R bin` to put `review-desk` on
   PATH, and `pass-core`'s new hand-over applies to every session; rollback is `git revert -m 1
   <merge>` then a pull); "Found, not done", each item with a proposed disposition and a one-line
   reason, seeded with the "Later" list below plus anything the tasks found; and the score rows
   (`cairn-run-gate --records <toplevel> <branch>`). Mark the PR ready.

Geoff reads and merges.

- **Estimate.** 60 minutes.

## Later

Not built in this pass; each goes to the PR's "Found, not done" with a proposed disposition.

- A running app keeps serving its old build after a merge changes `review-desk/`; today the fix is
  `pkill -f 'review-desk/[b]uild'` and `rm -rf ~/.dotfiles/review-desk/build`, and the next
  hand-over rebuilds. The command's item check (T3 step 3) names the stop when a new item 404s.
- Decided items stay in the state directory; nothing prunes them.
- A command killed by SIGKILL or a power loss leaves its item on the index; its traps cover only
  TERM, HUP, and INT.
- `dotfiles-pass` "Close checklist" says `scripts/check.sh` runs the Vale and tellgrader nets; it
  runs their test suites, and the prose nets are the `PostToolUse` hooks (proposed: now).
