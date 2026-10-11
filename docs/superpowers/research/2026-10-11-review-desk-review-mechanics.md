# Mechanics and feasibility review: review desk plan at 0fd53f5 (plan-reviewer agent, saved by the planning session)

Paths are relative to the worktree root; plan = `docs/superpowers/plans/2026-10-11-review-desk.md`,
prompt = `docs/superpowers/plans/2026-10-11-review-desk-prompt.txt`. Each claim was checked against
the unpacked kit 3.0.1 and adapter-node 6.0.0 source, the Claude Code docs, the repo's scripts, or a
probe.

**Verdict:** one blocker and eight majors. The Probed facts are right about CSRF, `paths.origin`,
adapter-node's HOST/PORT, CSP keyword quoting, the peer ranges, and the Survey core, but miss
several SvelteKit 3 breaking changes, and the Close end-to-end check can run against the wrong app.

## Blocker

1. **blocker, correctness. plan:183-184, 191, 139, 84. `svelte.config.js` makes the kit 3 build
   fail.** kit `src/exports/vite/index.js:276` throws `config_file_unsupported` when a
   `svelte.config.js` or `.ts` exists; the doc comment at `:163` says "Prior to SvelteKit 3, config
   lived in a `svelte.config.js` file, which is no longer supported." `src/core/config/index.js`
   `split_config` takes the options flat, passed to `sveltekit({...})` in `vite.config.ts` (no
   `kit:` key). Fold: T1 sets `sveltekit({ adapter: adapter(), paths: { origin:
   'http://127.0.0.1:7907' }, csp: { directives: { 'script-src': ['self'] } } })` in
   `vite.config.ts`; remove `svelte.config.js` from Files; Interfaces' three homes become the
   command, `vite.config.ts`, and the Host check; add a probed fact quoting the two source lines.

## Major

2. **major, correctness. plan:189-190, 192. Param matcher location is the SvelteKit 2 one.** In kit
   3, `resolve_params` resolves one entry file, `src/params.ts` or `src/params/index.ts`;
   `src/core/params.js` requires an exported `params` object, else `params_export_missing` or
   `param_matcher_missing`. Migration guide: "matchers no longer live in `src/params/`. Declare them
   all in `src/params.ts` using `defineParams` from `@sveltejs/kit/params`." Fold: `src/params.ts`
   with `export const params = defineParams({ id: (p) => /^\d{8}T\d{6}-\d+$/.test(p) ? p :
   undefined })`; the test calls that function.
3. **major, correctness. plan:66-121, 133. Other kit 3 removals.** `$lib` is removed (kit vite
   `index.js:75-79`, `removed_modules`, `module_removed_lib`; use `#lib` in `package.json`
   `imports`, with file extensions). `$env/dynamic/private` is deprecated for `$app/env/private`.
   tsconfig extends `$app/tsconfig`. `error()`'s second argument must be a string. `invalidateAll`
   becomes `refreshAll`. Fold: one "SvelteKit 3 breaks" probed fact citing
   `https://svelte.dev/docs/kit/migrating-to-sveltekit-3`; plan:133 to `$app/env/private`.
4. **major, correctness. plan:223-226. The "Decided" state can never render.** After an action,
   SvelteKit re-runs load (no enhance: `src/runtime/server/page/index.js:182`; with `use:enhance`:
   `forms/client.js` `fallback_callback` calls `refreshAll()`), and a decided id returns 404, so
   every successful click lands on a 404. Fold: load returns a decided item with `decided: true` and
   shows "Decided"; only an unknown id 404s; actions refuse a decided item with 404. Or the action
   `redirect(303, '/')`.
5. **major, correctness. prompt:3-4; plan:44, 55. EnterWorktree's name collides.**
   `.claude/worktrees/review-desk` exists on `worktree-review-desk` at 9b031f9. The worktrees doc:
   a name whose directory exists "opens that existing worktree instead of creating a new one", and
   with `worktree.baseRef: "head"` "reopens the worktree at its old tip". Fold: a fresh name such as
   `review-desk-v1`, path updated at plan:55.
6. **major, correctness. plan:201, 255, 303-305. The Close end-to-end check serves T1's stale
   build.** The command skips the build when `build/index.js` exists; T1's build has no item
   route. Fold: Close step 3 starts with `npm --prefix review-desk ci && npm --prefix review-desk
   run build`.
7. **major, correctness. plan:233-236, 253, 305. Port 7907 can be held by T2's leftover server**,
   started with another `REVIEW_DESK_STATE`; at Close the command skips the start, the page 404s,
   and the command waits forever. Fold: T2's acceptance ends with `pkill -f '<its
   worktree>/review-desk/build'`; Close step 3 first requires `curl -sf http://127.0.0.1:7907/` to
   fail; Later: a running app is pinned to the state root it started with.
8. **major, correctness. plan:175-182, 197-198, 227. `npm ci` runs only when `node_modules` is
   absent**, and T1's dependency list never names `marked`. Fold: T1 installs every package in the
   stack, `marked` included; T2 and T3 change no `package.json`; the prompt's T2 `npm ci` line
   becomes redundant.
9. **major, correctness. plan:24-34. Two security properties have no proof**: loopback bind and the
   CSP header. Fold: end-to-end step 4 adds `ss -ltn 'sport = :7907'` showing only `127.0.0.1:7907`
   and `curl -sI http://127.0.0.1:7907/item/<id>` showing `content-security-policy` with
   `script-src 'self' 'nonce-`.

## Minor

10. **minor, correctness. plan:201-203.** Minified CSS emits `--color-base-100:#f7f7f3` (no space);
    `paths.relative` defaults true, so the font `src` is `url(./spectral-....woff2)`, not `/_app/`.
    Fold: grep `--color-base-100: ?#f7f7f3` and require a bundled `.woff2` URL with no `http`.
11. **minor, correctness. plan:291-293.** The gate's tellgrader (`make check`, Go vet/lint/test) and
    Vale (one fixture) do not read pass-core's prose; `.claude/skills/dotfiles-pass/SKILL.md:45-46`
    makes the same claim (to "Found, not done"). Fold: drop the claim or run `vale` on the file once.
12. **minor, correctness. plan:317.** `~/.local/bin` holds per-file stow links, so `review-desk` is
    not on PATH until `stow -R bin`. Fold: "What goes live" says to run it right after the pull.
13. **minor, correctness. plan:130.** `created` has no format. Fold: ISO 8601 UTC
    (`date -u +%Y-%m-%dT%H:%M:%SZ`), sorted as a string.
14. **minor, correctness. plan:271-273.** T3 test race on the firefox record. Fold: bounded wait for
    the record file.
15. **minor, correctness. plan:228-230, 241.** The diff classifier has no file. Fold:
    `src/lib/diff.ts` in T2's Files.
16. **minor, optional. plan:301; prompt:12.** STATUS.md can conflict on the Close merge. Fold: a
    STATUS.md conflict keeps main's text plus this pass's lines and is not a stop.
17. **minor, optional. plan:204.** cairn-run-gate prints only the last 60 lines; the light lane's
    105 MB peak predates the npm legs. Fold: read legs and peak from `cairn-run-gate --records`.
18. **minor, optional. plan:310-311.** Close review also loads `svelte-conventions`.
19. **minor, optional. plan:66-75.** "A package taken for a feature" goes through
    `dependency-upgrade`. Fold: one sentence that the pins are each package's newest production
    version, or one skill run in T1.
20. **minor, optional, over-ceremony. plan:278-295.** T4 is a single deliverable; fold it into T3's
    subagent (disjoint file).
21. **minor, optional, over-ceremony. plan:233-236.** Survey styling proven three times; drop T2's
    screenshots.

## Checked and correct

CSRF and origin (`is_csrf_forbidden`, `get_self_origin`, the `__SVELTEKIT_DEV__` gate,
`paths.origin`, `checkOrigin` removed); adapter-node HOST default `0.0.0.0` and the https default in
`get_origin`; CSP keyword quoting and `'auto'` nonces; npm peers (vitest 4.1, `@tailwindcss/vite`
4.3.3, vite-plugin-svelte 7.3.1, adapter-node 6.0.0 with vite 8 and kit 3); `setsid -f`; the bg
daemon carries `WAYLAND_DISPLAY`, `DISPLAY`, and the D-Bus address; Playwright MCP configured; the
Survey core's four files; cairn-themes `main` at `dea9839`; `.claude/worktrees/` ignored; 255
task-minutes under the 420 cap. No OWNER FORKs.
