# Cloudflare estate + authorization model (glw907 account)

Workstation-wide reference, loaded by any project. Account `120c269ad6d3dfbe6d63a0bb53758ca0`.
**Plan: Workers Paid** (Geoff, 2026-10-25), so D1 allows 1,000 queries per Worker invocation (50 on
free). No token can read the plan (`GET /accounts/{id}/subscriptions` answers code 10000), so
this line and the servers runbook's "Cloudflare" section are the record.
**Values-free by rule** (this file is worth reading in any repo, some public): it records what
EXISTS and HOW to reach it, never a secret's value. Regenerate the live lists with the commands
at the foot; treat the snapshot below as orientation, verify before acting.

The sections below moved word for word into one file each under `~/.claude/docs/cloudflare-estate/`. Read the file for
your task; a reference by old section name finds it in this list.

- API token scheme (Geoff, 2026-10-18): `~/.claude/docs/cloudflare-estate/api-tokens.md`. Covers the scheme every Cloudflare API token follows, the numbered steps, and the token table.
- Authorization: how each thing is reached non-interactively: `~/.claude/docs/cloudflare-estate/authorization.md`. Covers the canonical token-scope record and how each Cloudflare thing is reached without a prompt.
- What's installed (snapshot 2026-07-07; verify live before acting): `~/.claude/docs/cloudflare-estate/installed.md`. Covers the D1 databases, Zero Trust organization, and other resources as of the snapshot.
- Regenerate the live inventory: `~/.claude/docs/cloudflare-estate/regenerate.md`. Covers the commands that rebuild the live lists.
