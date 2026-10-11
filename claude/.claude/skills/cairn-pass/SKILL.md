---
name: cairn-pass
description: >
  The cairn-cms adapter for the lean pass process: gate, fast lane, full-suite home, worktree
  setup, CI watch, risk-class path map, checklist globs, and close checklist for the
  @glw907/cairn-cms engine and its Go `cairn` tool. Use when planning, executing, resuming, or
  closing a cairn-cms pass, or when a fresh cairn-cms session follows a STATUS launch prompt. For
  a consumer site's pass use site-pass.
---

# Cairn pass

Load `pass-core` first; it holds the lifecycle and the rules this adapter fills in. The sources
are `docs/STATUS.md` (the rolling now) and the functional spec
(`docs/superpowers/specs/2026-05-28-cairn-rebuild-functional-spec.md`, the locked decisions).
STATUS's next action names the plan; trust it. Check `docs/internal/consultations/` for briefs with
unrecorded verdicts first (`engine-consult` carries the protocol).

**Gate**: `cairn-run-gate '<string>'` from the pass worktree, per `pass-core` "Gates".

**Fast lane**: `node scripts/checks/gate-tier.mjs --fast --range <base>..HEAD` prints the legs.
Run them in order, each through `cairn-run-gate` with a leading `CAIRN_GATE_LANE=<lane>` lifted onto
the call (`CAIRN_GATE_LANE=light cairn-run-gate '<rest>'`), since the tool reads the lane from its
own environment. The `--fast` flag lands in rollout step 2. The `tool` class gate is
`make -C tool check` on the light lane; a Node-only workspace suite such as `npm test -w
packages/create-cairn-site` is light, and the engine's root `npm test` drives Chromium and is never
light. A lone unrelated test failure, or `Cannot connect to the server in 60 seconds`, is a known
workstation trap first: `docs/internal/durable-gotchas.md` carries the rerun rule.

**Full-suite home**: CI on the draft PR. Local `TIER_GATES.full` (`npm test`, then `npm run
check:close`, which builds once) runs only on `ci-green` exit 3, with the e2e step run as `--grep-invert
"site home|archive page 2"`. A docs-only local fallback skips `npm test` and runs `check:close`.
The gate runs no gitleaks scan, so there is no branch-history scan to owe.

**Worktree setup**: The launch's `.claude/worktrees/<branch>`, then `npm ci && npm ci --prefix
examples/showcase`, since a worktree's showcase otherwise resolves the main checkout's engine
(`docs/internal/durable-gotchas.md`).

**CI watch**: `ci-green <sha> --pr <n> --wait` as a background Bash task, re-issued on 75; exit 0
is green, 1 red, 2 missing, 3 unavailable. The first push opens a draft PR, since cairn CI fires
on `pull_request` and on push only to `main` and `rebuild`. No task waits for CI before the next; a
red stops the line. Run it from the pass worktree so its CI line lands under the pass branch for
`--records`. List every retried test from its output in the PR body: a retry that passed is flake
evidence, not green.

**Risk-class path map**: `auth-data`: `src/lib/{auth,auth-channel,auth-crypto,auth-store,github}/**`,
`src/lib/sveltekit/{csrf*,auth-*,commit-log}.ts`, `src/lib/admin/{csrf-context.ts,CsrfField.svelte}`,
`migrations*/**`, `examples/showcase/migrations*/**`, `templates/*/migrations*/**`,
`**/hooks.server.ts`, `**/preview/\[token\]/**` (escaped: in a pathspec `[token]` is a character
class), `**/members/login/**`, `**/admin/signups/**`, `tool/internal/secrets/**`,
`packages/create-cairn-site/src/{github,cloudflare}/**`, `wrangler.*`. `runner`: `scripts/checks/**`,
`.github/workflows/**`, `.github/ci-green.json`. `ordinary`: the rest. A chassis task
(`examples/showcase/src/chassis/`, `templates/waymark/`) takes the class an engine change of its
kind would take and the engine's quality bar, since a developer copies that code.

**Checklist globs**: The close review loads `svelte-reviewer` for `**/*.svelte` and load, action, or
hook code; `cloudflare-workers-reviewer` for Worker, D1, and `wrangler.*`;
`web-auth-security-reviewer` for every `auth-data` glob; `daisyui-a11y-reviewer` for markup, styles,
and theme config; `go-conventions` for `tool/**`.

**Close checklist**: Beyond `pass-core` "Close":

- The live admin smoke on `auth-data`, against a real Worker (`wrangler dev`) with a session minted by
  inserting a D1 row, then the magic-link round trip in headless Chromium, reading the link from
  wrangler's local `send_email` output; follow `docs/internal/admin-smoke-test.md`.
- Documentation is a pass dimension: fix every doc the change touched, inbound references included.
  A public-behavior change files its bullet in `docs/internal/facts/<arm>.md` and updates the
  reference page if it is public API. An arm with no rebuilt page files divergences into the facts
  container instead of fixing a page. A fix on a published page is written to the track's drafting
  brief with no register review, and Vale's error tier still runs; an edit to a page with a brief
  updates the brief in the same change (the spec's "Edits after the chain").
- A behavior change updates `CHANGELOG.md` under `## Unreleased` and the per-version record
  (`docs/extend/migration-notes.md`, with `docs/extend/upgrade-cairn.md`); a breaking change carries
  one `Consumers must:` line per consumer action. A removed or renamed symbol is grepped across
  `docs/` and `README.md` and every hit repointed. An intended public-surface change runs `npm run
  check:surface -- --update` and commits `docs/internal/api-surface.md`. A ruling on a consultation
  item updates `docs/internal/engine-rulings.md`.
- Triage `docs/internal/docs-friction-log.md`, complete-or-move: each entry is fixed and deleted,
  promoted to `ROADMAP.md`, or deleted as overtaken, verified against the code first. A promotion to
  an engine change reads `engine-rulings.md` and runs the charter's premise test first. File each
  new friction under "Open findings" as a `- **\`perspective\`.**` bullet naming the finder and
  date, verified against cairn-cms first. The `main` checkout is shared: stage only your own hunk
  (`git add -p`) and leave another session's warm edits alone. UI mechanics follow
  `~/.claude/docs/engine-ui-mechanics.md`.
- A docs-stage close runs the engine-pass boundary test over the log's engine entries and the
  `ROADMAP.md` engine-friction entries, and states in STATUS whether an engine pass is warranted
  before the next stage. Engine passes land on `main` and never release.
- A pass never bumps the version or publishes. It finalizes its `CHANGELOG.md` entry and stops;
  `cairn-release` cuts a release when one is warranted. Never write cairn state into a site's STATUS.
