---
name: cairn-release
description: >
  Cut and publish the cairn-cms npm package (`@glw907/cairn-cms`, "cairn") to the registry, the deliberate
  act that gets a cairn version onto npm. Invoke on any intent to publish, ship, cut, release, tag, or push
  out cairn (for example "publish cairn", "ship it to npm", "cut a cairn release", "tag it on github"), when
  merged-and-green cairn work on `main` is ready to go out, when held cairn changes should batch into one
  publish, when picking the next version, finalizing the CHANGELOG, or firing the publish workflow, or when
  a consumer site (ecxc-ski, 907.life) is blocked on a new cairn export and needs it on the registry before
  its dependency range bumps. Do not invoke it for a finished cairn dev pass that just holds unpublished
  (that is `cairn-pass`), or for a SvelteKit site's own deploy; this skill publishes the cairn-cms package
  itself.
---

# Cairn release

A cairn-cms release is a deliberate, occasional act. A finished pass finalizes its `CHANGELOG.md` entry
under `## Unreleased`, leaves `package.json` alone, and holds. `main` stays releasable, so completed work
accumulates unpublished until a release is warranted, and this skill is that separate publish step. The
governing scheme lives in cairn-cms `CLAUDE.md` ("Releases") and the `cairn-release-process-and-versioning`
memory; this skill is the executable procedure.

Run it from inside the cairn-cms repo so its hooks and memory load.

## 1. Gate: is a release warranted?

Stop here unless one of two triggers holds:

1. A consumer site needs a published export now (this also forces the publish-before-push ordering: a
   site's `main` must never reference an export the registry lacks).
2. A coherent capability or initiative has landed and is worth making available, at its natural boundary.

A finished pass is not itself a trigger. An internal-only change a consumer never imports (for example the
admin idiomatic re-expression, which re-expresses admin CSS and components) does not warrant a release; it
rides the next consumer-facing cut. If neither trigger holds, do not release: confirm the work sits under
`## Unreleased` and stop. A version number is a public, immutable signal, so cutting one for every small
change just burns numbers. When in doubt, hold.

## 2. Confirm the window is on `main` and the gate is green

The release publishes from `main`. Get the held work onto `main` first: one worktree per pass off `main`,
so fast-forward `main` from the feature branch (`git push origin HEAD:main`, never force) or confirm it is
already merged. The branch must be a clean fast-forward of `origin/main` (`git merge-base --is-ancestor
origin/main HEAD`).

Dependencies are current before the gate runs. A release starts from the newest production version of
everything, so the last merge before the cut is the `dependency-upgrade` skill's sweep on `main` with no
worktree live (its lockfiles collide with a live branch): every minor and patch taken, every major held
with its unblock trigger recorded, the survey and the refactor decision on record. Skip this only when the
window already contains such a sweep and `npm outdated` at every manifest returns only the held majors.

The full gate must be green at the release commit. Run it (sequentially; `npm test` and
`check:custom-surface` both repackage `dist`, so do not run them concurrently):

- `npm run check` (svelte-check, 0 errors and 0 warnings)
- `npm test` (exit 0, not just a passing count)
- `npm run check:custom-surface` (PASS both trees)
- `npm run check:comments` (the TSDoc + em-dash gate)
- the four doc gates: `npm run check:reference`, `check:reference:signatures`, `check:docs`, `check:package`
- the consumer-build proof: a CI `e2e` run, or a from-scratch showcase build (`rm -rf
  examples/showcase/{node_modules,package-lock.json}` then a fresh install and `npm run build`). Local
  Playwright reuses a stale preview off CI, so do not trust a local "all green" alone.

## 3. Pick the version (immutable; verify free)

Published numbers are global and immutable. The pre-rebuild history already burned `0.1`–`0.68`, so never
assume the next number is free. List the full set and pick the first free one:

```bash
npm view @glw907/cairn-cms versions --json   # the FULL list, not the `latest` tag
```

Size the bump under SemVer. In `0.x` a minor (`0.X.0`) is reserved for a NEW SUBSYSTEM OR PUBLIC SURFACE
that did not exist before; everything else (refinement, fix, DX, internal, even new optional exports on an
existing surface) is a patch. The number signals scale, not compatibility: the changelog carries
compatibility via `Consumers must:` lines. A minor must carry a `<!-- release-size: minor -->` marker in
its CHANGELOG section (the `check:version` gate requires it). When unsure, it is a patch.

**Derive the size HERE, at the cut, against this rule and the actual `## Unreleased` window — never
inherit it from the conversation.** A number or size named earlier (in the launch prompt, a plan, or by
Geoff in passing: "minor point release", "this'll be 0.90") is a hypothesis to re-derive, not an
instruction; phrases like "point release" are ambiguous and a passing size call predates the window's
final content anyway. When the derived size disagrees with what was said earlier, state the rule, name
the derived number, and confirm the mismatch in one sentence. (Born 2026-07-16: a polish pass was
launched as "a minor point release" and nearly cut as `0.88.0`; the window was UI polish with no new
subsystem or surface, a patch by this rule, and Geoff had to catch it.)

Set the version only now, at the cut (never pre-number a held pass, which mints a phantom like the
`0.77.0` that rolled into `0.78.0`):

```bash
npm version <x.y.z> --no-git-tag-version   # bumps package.json + the lockfile, no git tag
```

## 4. Finalize the CHANGELOG and compose the notes

Rename the held heading `## Unreleased` to `## <x.y.z>` (no date; match the repo's finalized-section
format, which is the heading then a blank line then the `<!-- release-size: ... -->` marker). Scrub any
stale "stays unpublished until then" or "set at release time" phrasing from the finalized section.

The release body is the changelog window since the last PUBLISHED tag. When several held minors roll into
one publish (the common case in this initiative, because passes hold and batch), the body summarizes EACH
held section in the window and carries EVERY `Consumers must:` line from the breaking ones. Compose it into
a notes file rather than by hand at the `gh` prompt. Add the matching per-version entry to
`docs/guides/upgrade-cairn.md` if the pass did not already.

A window touching an admin surface (`src/lib/components/*.svelte`, `cairn-admin.css`) also earns a
re-read of the reproduction stories and docs pages the change reaches: check every affected story's
caption against what it now renders, and, on a page carrying a keyed callout list, that the list still
matches. A reproduction pictures a live render, so an admin change can silently falsify the prose
sitting next to it, and this is the last point before the change ships where the mismatch is still
cheap to catch.

Beware the Tailwind-scans-docs gotcha: an arbitrary-value class written in CHANGELOG or doc prose with a
non-value placeholder inside the brackets (an ASCII `...`, a `*`, or a `|`) compiles to malformed CSS and
breaks `npm run package`. Write the concrete token. A quick check:
`grep -rnE '[a-z-]+-\[[^]]*(\||\*|\.\.\.)[^]]*\]' docs/ CHANGELOG.md ROADMAP.md`.

## 5. Commit, land on `main`, cut the release

Commit the version bump plus the finalized CHANGELOG (plus the post-mortem and STATUS if they are part of
this cut). Land it on `main` (fast-forward push, never force). Then:

```bash
gh release create v<x.y.z> --target main \
  --title "v<x.y.z>: <one-line summary of the window>" \
  --notes-file <notes-file>
```

This fires `publish.yml` (OIDC trusted publishing, `npm publish --access public`). The workflow derives
the dist-tag from the version: a stable number goes to `latest`, and any version carrying a prerelease
suffix goes to `next`, so a candidate never reaches a bare `npm install` (wired 2026-08-05 for the
`0.94.0-rc.1` cut; before that the workflow passed no `--tag` and npm's `latest` default applied to
everything). Pass `--prerelease` to `gh release create` on a candidate so the GitHub "Latest" badge
follows suit. A prerelease also has to clear `check:version`, which sizes an entry against the nearest
earlier heading whose numeric core differs, so `0.94.0-rc.1` and the `0.94.0` it promotes into declare
their shared `<!-- release-size: minor -->` marker once, on whichever heading is current.

**A consumer cannot reach a prerelease through its caret range.** A `^0.93.0` dependency does not resolve
`0.94.0-rc.1`, by SemVer's own rule, so a site testing against a candidate pins the exact version
(`"@glw907/cairn-cms": "0.94.0-rc.1"`) and moves back to a caret when the stable lands. The workflow runs `npm install -g npm@latest` first because trusted publishing needs npm >= 11.5.1.
Under trusted publishing the `--provenance` flag is unnecessary: provenance is automatic (the repo went
public 2026-07-03 and the old `NPM_CONFIG_PROVENANCE=false` override was removed with it).

## 6. Verify the publish

```bash
gh run watch <run-id> --exit-status     # publish.yml must finish green
npm view @glw907/cairn-cms version      # serves the new number on `latest`
```

Then update `docs/STATUS.md` to the shipped state.

If the publish job fails on authorization (an OIDC error rather than a code failure), the trusted-publisher
config on npmjs.org is the suspect, not the code: the org/user, repository, workflow filename
(`publish.yml`), and environment must match the running workflow exactly, and a trusted-publisher config
created after 2026-05-20 must have at least one allowed action selected (older configs default to
publish-allowed, so a long-standing one needs no change). Do not bump the version again to retry; fix the
config and re-run the same release's workflow.

## 7. Hand-off

The sites pin `@glw907/cairn-cms` by range and run `npm ci`, so the publish must precede any site code that
imports new exports. Order: publish, verify on the registry, repoint each site and regenerate its
standalone lockfile (in an isolated temp dir so it resolves from the registry, not the workspace symlink),
then push the sites. Flag any deferred live admin smoke tied to a site cutover.

## References

- The scheme, the 0.x-vs-1.0 reasoning, and the comparables: the `cairn-release-process-and-versioning`
  memory.
- npm auth and Trusted Publishing specifics: the `npm-publishing-constraints` memory.
- The path to 1.0 and its readiness checklist: `ROADMAP.md` ("Toward 1.0").
- The pass that produces the held window: `cairn-pass` (which holds unpublished by default and points
  here when a cut is warranted).
