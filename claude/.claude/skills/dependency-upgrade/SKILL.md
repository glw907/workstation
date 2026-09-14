---
name: dependency-upgrade
description: >
  Use when taking any dependency bump in any repo on this workstation: a pre-release sweep, a
  Dependabot or Renovate PR, a single package taken for a feature, a major Geoff has approved,
  or a question like "are we current", "what's outdated", "should we upgrade X", "any new
  capabilities in the new version". Also use when a release is being prepared, since a cut
  starts from current dependencies. Do not use for adding a brand-new dependency (that is a
  design question for the pass that needs it).
---

# Dependency upgrade

Two goals drive this. Staying current over time, so technical debt never accumulates into a
migration. And continuous improvement: as a dependency improves, it often offers the repo's own
code a chance to improve, by deleting a workaround, adopting a primitive, or retiring a
home-grown component. An upgrade that only moves the lockfile has taken the first goal and
missed the second.

A bump is not done when the lockfile moves. It is done when the release notes for exactly the
bumped range have been read against how this repo uses the package, every new capability has
been ruled take-now or filed, the held majors carry a trigger, and the full gate is green.

Geoff's standing rules (2026-09-13, 2026-09-14): take every minor and patch and the non-major
`npm audit fix` results without asking; always ask before a major; every bump carries a
survey; every upgrade carries a refactor decision; a release starts from the newest production
version of everything.

## Procedure

Run the steps in order. Each produces a named artifact; the report at the end lists all of them.

### 1. Measure every manifest

List the manifests first, then measure each. A repo can carry more than the root: `examples/*`,
`packages/*` workspaces, `templates/*`. Every directory with its own `package.json` and lockfile
is a manifest in scope, including an example that consumes the root by `file:`. At the root use `npm outdated --workspaces
--include-workspace-root` and `npm audit`; run both again in every non-workspace manifest
directory. Record the before table: package, current, wanted, latest, manifest.

A caret range that already admits the newer version still counts as a bump. It moves only when
the lockfile is regenerated, so it is where most of the risk sits.

### 2. Survey the bumped range

If a survey record already exists for this release window (the same `## Unreleased` block, or
the same held-major set), extend it in place with the packages that moved since; start a new
dated file only for a new window. Dispatch one research agent (Sonnet, or Opus for a large
sweep) with the before table and the prior record's path when one exists. For each
package it reads the release notes for exactly `current..target`, against the repo's actual call
sites, and returns three lists per package: features to leverage (code the repo hand-rolls that
the package now provides), practices to change (deprecations, changed defaults, new lint rules,
consumer-visible behavior), and gate risks (a fix that lands on a shape the repo has, with the
file:line to re-test). A package with nothing in range gets one line saying so.

For a design-system package (DaisyUI in the cairn family) the survey also inventories the
current component set against the repo's home-grown components and recipes, each with its
coverage gap and whether a swap is a consumer-visible change.

Record the survey as a dated file under the repo's records directory (cairn family:
`docs/internal/record/`), since the next sweep starts from it.

### 3. Rule the refactor decision

This is the deliverable the survey exists for. For every feature-to-leverage item, name the code
that hand-rolls it and rule one of:

- Take now: A small, safe change with an existing test; it lands in this upgrade's own task.
- File: A ROADMAP line naming the code, the capability, and the pass that first leans on it.
- Refactoring pass: When the take-now list outgrows a small task, or several items touch one
  subsystem, propose a formal refactoring pass with its own plan instead of folding the work into
  the sweep. Say so in the report and file the pass; do not quietly widen the sweep.

Practices-to-change items are ruled the same way. Gate-risk items become named verification
steps in step 5.

### 4. Take the bumps

Rewrite each dependency and devDependency range to `^<newest non-major>` in every manifest so
the declared floors track the install. Peer ranges do not move unless the survey found a reason.
Delete `node_modules` and the lockfile in every manifest directory from step 1 that has its own
lockfile (workspace members share the root's and need nothing separate), then `npm install` in
dependency order (the root whose `prepare` builds the package installs before an example that
consumes it by `file:`).
Never `npm ci` after deleting a lockfile. Diff the regenerated lockfiles against the pre-sweep
copies and record every resolved-version change, since caret-satisfied packages moved silently.

For each major: present the change, its peer blockers, and the consumer-visible effect, then
wait for Geoff. An `npm audit fix` that needs `--force`, or that downgrades a package to clear an
advisory, is a major for this purpose and waits the same way; note whether the vulnerable path is
runtime or dev-only, since that sets the urgency. Held majors are recorded with the exact condition that unblocks them.

### 5. Gate

The repo's full gate, plus the consumer or example build and its e2e suite, plus CI on a pushed
branch. Run each gate-risk verification from step 3 by name and report its result. Visual
baselines that a bump moves are declared before the run as intended moves, regenerated by file
path, and read; an undeclared move is a stop.

### 6. Record

- CHANGELOG entry with a `Consumers must:` line when anything the consumer compiles or renders
  moved (a packaged stylesheet, a bundled icon set, a peer range).
- Held majors with their unblock conditions in the release record, and a scheduled tripwire
  (the `schedule` skill) for each machine-detectable condition, pinging only when it trips.
- ROADMAP lines for every filed item and any proposed refactoring pass.

## The report

One message: the before-and-after table from the lockfile delta; the refactor-decision table
(capability, code, ruling); held majors with conditions; verification results by name; gate
result; the record paths.

## Common misses

| Miss | Fix |
| --- | --- |
| Only the root measured | List every manifest first; examples and workspaces carry their own. |
| "Bump and gate" with no survey | The survey is the input; the refactor decision is the point. |
| `npm update` or `npm install pkg@x` in place | Rewrite ranges, delete lockfiles, reinstall, diff. |
| Gate without the consumer build or CI | A library's own tests never see a consumer-bundler break. |
| Held major with no trigger | A hold without a condition is forgotten; record it and schedule it. |
| Take-now list quietly grows | Past a small task, propose the refactoring pass. |
