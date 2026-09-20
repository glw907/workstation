# Cloudflare estate + authorization model (glw907 account)

Workstation-wide reference, loaded by any project. Account `120c269ad6d3dfbe6d63a0bb53758ca0`.
**Values-free by rule** (this file is worth reading in any repo, some public): it records what
EXISTS and HOW to reach it, never a secret's value. Regenerate the live lists with the commands
at the foot; treat the snapshot below as orientation, verify before acting.

## Authorization: how each thing is reached non-interactively

- **Cloudflare API / Wrangler — THE CANONICAL TOKEN-SCOPE RECORD (all projects defer here;
  never restate scopes in a project doc, link to this file).** ONE managed token exists:
  "Cloudflare Admin", id `48efe6a43d660d3fc649c799ec6c0892`. It lives in `~/.local/secrets`
  (regenerated from the ASC age store; `~/.bashrc` sources that file at line ~167, but ONLY
  in interactive shells — its line-5 interactivity guard means a script's
  `source ~/.bashrc` gets NOTHING; scripts must `source ~/.local/secrets` directly).
  GitHub Actions repos hold synced copies as the `CLOUDFLARE_API_TOKEN` secret.
  Scopes, each verified empirically 2026-07-14 (token "Cloudflare Admin 2026-07",
  id `1d508f1ab69df49d3ef9572dc1917273`, minted 2026-07-14 after dashboard edits to the
  prior token silently failed to persist): Workers scripts + schedules ✓, D1 ✓, R2 ✓,
  Access apps/policies ✓, Access service tokens ✓, Email Sending ✓ (REST + binding),
  Turnstile ✓ (granted, untested), zone read ✓, **Zone.DNS Edit ✓ (proven by live
  record deletions)**, Zone Workers Routes ✓ (added by dashboard edit 2026-07-19 after
  scripted cairn.pub deploys failed on the missing permission; GET verified live on the
  cairn.pub zone, write granted per the edit but untested; recommended grant was
  Edit on ALL zones so a newly registered zone never repeats the gap),
  API-token management ✗ (deliberate: cannot self-extend).
  Rotated into: the ASC age store, `~/.local/secrets`, and the four GH-Actions repos
  (aksailingclub-legacy/-org, ecxc-ski, 907-life). Predecessors both deleted:
  "Cloudflare Admin" (`48efe6a4...`) and `CF_ZT_TOKEN` / "Cloudflare Agent Token -
  2026-05-25" (only consumers were verify-keys.sh health checks).
  Second credential: the Cloudflare MCP plugin's OAuth (not in the token list; broad
  READ incl. DNS, refuses writes). Maintenance rules: any scope change lands in THIS
  bullet, same session; after a rotation, a RUNNING Claude session's env still holds
  the OLD token (the harness captures env at session start) — prefix commands with
  `source ~/.local/secrets` until the session cycles.
- **Second managed token, read-only: "cairn tool read" (minted 2026-09-19)**, stored as
  `CAIRN_CF_READ_TOKEN` (age store, local only) for the Go `cairn` operator tool in cairn-cms
  `tool/`. Seven Read permission groups, by their dashboard names: Workers Scripts, Workers
  Builds Configuration, Workers Observability, Zone, Zone Settings, DNS, Email Sending; account
  `glw907`, all zones. A read-level Builds group EXISTS (the tool's plan had allowed for none).
  Probe results 2026-09-19, statuses only: `user/tokens/verify` active; 200 on
  `workers/scripts`, `zones`, `dns_records`, `settings/always_use_https`,
  `settings/security_header`, `email/sending/subdomains`, `builds/tokens`,
  `builds/workers/{tag}/builds`, `builds/workers/{tag}/triggers`, and
  `workers/observability/telemetry/keys`; 403 on a DNS record POST and a zone-setting PATCH.
  `accounts/{id}/tokens/verify` answers error 1000 for this user-owned token; use the `user/`
  path. The Zone Settings group was added by a dashboard edit that DID persist (contrast the
  2026-07-14 failure above). Permission-group ids are not recorded: listing them needs
  token-management scope, which neither token carries. Registry entry:
  `~/.dotfiles/secrets/registry.md`.
- **Worker secrets are WRITE-ONLY**: `wrangler secret list` returns NAMES, never values; a value
  set with `wrangler secret put` cannot be read back. To learn a secret's value you need its
  origin store, not the worker.
- **Access-protected sites (ASC dev/staging)**: the service token in `~/.local/secrets`
  (`ASC_ACCESS_CLIENT_ID` / `ASC_ACCESS_CLIENT_SECRET`), sent as `CF-Access-Client-Id` /
  `CF-Access-Client-Secret` headers. Full recipe: the cairn `asc-cloudflare-access` memory.
- **The workstation registry** `~/.dotfiles/secrets/values.age` and `~/.local/secrets`: the
  workstation's own secrets (GitHub App key, the ASC Access service token, etc.). Its
  `registry.md` marks some entries "ASC-managed separately" — those live in the ASC store below,
  not nowhere.
- **The ASC project store** `~/Projects/aksailingclub-legacy/secrets/values.age` (age key
  `~/.config/age/asc-key.txt`, the same `AGE_KEY_FILE` in `.bashrc`): the club's own secrets —
  Stripe keys, the seven `DISCORD_WEBHOOK_*` URLs, Resend, Turnstile, `CMS_BOT_PAT`. Its
  `scripts/secrets/sync.sh` holds the per-worker secret map (`WORKER_SECRETS[...]`) and pushes
  from the store to every target; its own `secrets/registry.md` documents each entry. To set one
  secret without a full sync: `age -d -i $AGE_KEY_FILE values.age | grep '^NAME=' | cut -d= -f2- |
  npx wrangler secret put NAME` (value piped, never printed). A per-project store like this is
  the pattern: any repo with a `secrets/` dir + sync script is its own origin store — check it
  before declaring a credential unmanaged.
- **1Password** (interactive, `op` CLI): the fallback for a value in no scripted store — a
  dashboard LOGIN, a rarely-needed credential. **Each `op` call can prompt a desktop approval, so
  batch them: one `op item get --format json` and parse locally, never a loop of calls.** See the
  global CLAUDE.md Secrets rule.

## What's installed (snapshot 2026-07-07; verify live before acting)

**D1 databases:** asc-club (the phase-2 club domain — members/assets/classes/events/email),
asc-ops + asc-ops-staging (the legacy ops stack, READ-ONLY during absorption, retiring),
asc-staging (the retired sveltekit shell), cairn-asc-auth (the ASC site's magic-link auth),
cairn-907-auth, cairn-ecxc-auth (+ the old cairn-ecnordic-auth pending delete), cairn-pub-auth,
cairn-pub-app, daily-tracker.

**R2 buckets:** asc-site-media (the ASC site's media library), asc-event-images (+ -staging, the
legacy ops event photos), 907-life-media, ecxc-media, cairn-pub-media.

**Workers:** asc-site (the NEW cairn ASC site, served at dev.aksailingclub.org; the apex is the
legacy site until cutover), aksailingclub-org (build worker), asc-ops (+ -dev, -staging; the
retiring dashboard), asc-handbook, asc-uptime, 907-life, ecxc, cairn-pub, eudaimonia.

**Access apps:** ASC CMS Admin (dev.aksailingclub.org/admin), ASC Staging, ASC Handbook (+ its
CMS), Ops Dashboard (ops + staging), the Ops Schema API (public, consumed cross-origin by the
handbook — do not lock it).

**asc-site worker secrets (names):** GITHUB_APP_ID, GITHUB_APP_INSTALLATION_ID,
GITHUB_APP_PRIVATE_KEY_B64, STRIPE_SECRET_KEY + STRIPE_WEBHOOK_SECRET (Stripe SANDBOX test keys,
set 2026-07-07; the sandbox webhook endpoint `we_...` targets /api/stripe/webhook). **Not yet
set:** TURNSTILE_SECRET_KEY, CONTACT_EMAIL.

## Regenerate the live inventory

```bash
AID=120c269ad6d3dfbe6d63a0bb53758ca0; T="Authorization: Bearer $CLOUDFLARE_API_TOKEN"
curl -s -H "$T" "https://api.cloudflare.com/client/v4/accounts/$AID/d1/database"          # D1
curl -s -H "$T" "https://api.cloudflare.com/client/v4/accounts/$AID/r2/buckets"           # R2
curl -s -H "$T" "https://api.cloudflare.com/client/v4/accounts/$AID/workers/scripts"      # Workers
curl -s -H "$T" "https://api.cloudflare.com/client/v4/accounts/$AID/access/apps"          # Access
cd <a repo bound to the worker> && npx wrangler secret list                               # secret NAMES
```
