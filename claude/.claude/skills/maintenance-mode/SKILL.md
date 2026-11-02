---
name: maintenance-mode
description: Puts a finished production project in maintenance mode, where it stays current on its dependencies and otherwise stays out of the way. Use when Geoff says a project is done, is in production, should go quiet, or should go in or come out of maintenance mode, when a maintenance update fails, or when a feature comes up for a project in that mode.
---

# Maintenance mode

A project in maintenance mode is live, finished, and quiet. It keeps taking routine updates, and
nothing else happens to it until Geoff adds a feature. No backlog sweeps, reviews, or cleanup passes
start on their own; an open backlog item waits there for Geoff.

Maintenance mode exists for small personal projects, so a project stays in it on as little machinery
as possible. Prefer the existing timer and gate to anything new.

## What runs

`maintain-projects` runs from the system timer `maintain-projects.timer` on pavilion at 1:00 AM on
the first of each month. For
each repo in `~/.dotfiles/bluefin/maintenance-projects.txt`, it:

1. Takes the in-range updates at least seven days old, plus non-major `npm audit fix` results,
   which skip the wait.
2. Runs `npm run check` in a throwaway worktree.
3. Pushes to `main`, waits for CI to pass and deploy, then updates the main checkout.

A quiet month says nothing. A failure raises one normal notification and leaves its log in
`~/.local/state/maintain-projects/<repo>.log`. A gate failure leaves `main` unchanged. Each
repo's `<repo>.held` file there lists what stayed behind: majors, and anything a `~` range holds. Its
`<repo>.blocked` file names, for each held major, the installed packages whose peer ranges refuse it.

`maintain-projects --status` lists each project, its last run and result, and how many packages
are held. Trust it over silence: after a reboot with no login, the keyring is locked, so the run
fails safely and its notification may not show. The next month's run tries again.

No AI runs in this path, and routine updates carry no release-notes survey (Geoff, 2026-11-01). That
is the one exception to `standards:dependency-upgrade`.

## Enter maintenance mode

A repo qualifies when all of these hold:

- It has a `package.json`, and `npm run check` passes with no credentials.
- A push to `main` deploys through CI, in `glw907/<repo>`.
- The gate is strong enough that Geoff would merge what passes it. A production check after deploy,
  like the phonebook's nightly, counts in its favor.

Then:

1. Run `maintain-projects --dry-run` with `MAINTAIN_LIST` pointing at a file that names the repo.
2. Add the repo to `bluefin/maintenance-projects.txt`.
3. Say so in the repo's `docs/STATUS.md`.
4. Add a dated line to its initiative record and set the status to `done`.

## Handle a failure

Read the log, fix the cause, and take the updates as a normal change in that repo. Handle a CI
failure first: that commit is on `main`. Revert it if it can't be fixed quickly. A repo's STATUS may
limit how far it can roll back, so read that before reverting a deploy.

## Add a feature

Run a normal pass through `pass-core` while the project stays in maintenance mode. Its first task is
a full `standards:dependency-upgrade` sweep, so the feature starts from current dependencies. That
sweep is where the held majors get decided. Offer a major only after reading `<repo>.blocked` and what the framework says it targets, and put both in front of Geoff: a new release number says nothing about whether the stack can use it. TypeScript 7.0 has no stable programmatic API, expected in 7.1, so `svelte-check`, `typescript-eslint`, and `@sveltejs/kit` all stop at 6, and SvelteKit is aiming at 7.1 (Geoff, 2026-11-01). The timer skips a dirty or off-`main` checkout but can't
see a pass in a worktree, so that pass rebases on the update if one lands first.

## Leave maintenance mode

Remove the repo from `bluefin/maintenance-projects.txt` and say so in its `docs/STATUS.md`.

## Projects that aren't npm repos

`maintain-projects` handles npm repos only. The same rules apply elsewhere: a quiet routine update,
a gate, and one notification on failure. A service with a different update path gets its own step
when Geoff brings it in. Don't stretch the npm script to cover it. Stalwart and Bulwark on ward and
orpheus are the likely next ones; their update carries a server deploy, so it starts in `servers`.
