# Cloudflare estate + authorization model (glw907 account)

Workstation-wide reference, loaded by any project. Account `120c269ad6d3dfbe6d63a0bb53758ca0`.
**Plan: Workers Paid** (Geoff, 2026-10-25), so D1 allows 1,000 queries per Worker invocation (50 on
free). No token can read the plan (`GET /accounts/{id}/subscriptions` answers code 10000), so
this line and the servers runbook's "Cloudflare" section are the record.
**Values-free by rule** (this file is worth reading in any repo, some public): it records what
EXISTS and HOW to reach it, never a secret's value. Regenerate the live lists with the commands
at the foot; treat the snapshot below as orientation, verify before acting.

## API token scheme (Geoff, 2026-10-18)

Every Cloudflare API token on the account follows this scheme. Read it before you create,
rename, rescope, store, or delete one. Geoff asked for ease of management balanced against
reasonable security, so a token is split only where the split keeps a compromise of one holder
from reaching something it otherwise could.

The rules come from three published sources:

- Cloudflare's API token docs: least privilege, "descriptive token names", "document token
  usage", account-owned tokens for "durable integrations ... like CI/CD" and user tokens "for ad
  hoc tasks like scripting", and limiting a powerful token "via client IP address filtering or
  TTL" (<https://developers.cloudflare.com/fundamentals/api/get-started/account-owned-tokens/>,
  <https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/>). The Workers
  permissions page lists "Automated deployments from CI/CD or agents" as a token with Workers
  Editor at product scope (<https://developers.cloudflare.com/workers/authorization/>).
- The OWASP Secrets Management Cheat Sheet: least privilege (2.3), "limit shared secrets" and no
  CI secret with "a wide blast radius" (3.2.1), and a record of each secret's consumer, purpose,
  and rotation (2.11)
  (<https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html>).
- GitHub's Actions hardening guide: "Any user with write access to your repository has read
  access to all secrets configured in your repository", so workflow credentials get "the least
  privileges required"
  (<https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions>).

The scheme:

1. **One token per holder and job.** The holder is where the value lives: `ws` (this
   workstation), `ci` (GitHub Actions and Workers Builds), or a server (`ward`, `orpheus`). Two
   jobs on the same holder share a token unless a script's bug in one would otherwise reach the
   other's resources.
2. **Ownership.** A new token that a script, a server, or CI depends on is account-owned, so it
   outlives any one person's login. Only `ws-admin`, used interactively as Geoff, is user-owned
   by design. The two older user-owned script tokens (`ws-cairn-read`, `ws-r2-music-ro`) move to
   account ownership at their next rotation.
3. **Scope to the resource.** One zone, one bucket, or Workers Editor (deploy, never delete)
   wherever the job allows. Read-only wherever the job only reads.
4. **Names.** At Cloudflare, `<holder>-<purpose>`, lowercase with hyphens. In the age store,
   `CF_` plus the Cloudflare name in upper snake case plus `_TOKEN`; an R2 token adds the S3
   pair as `_KEY_ID` and `_SECRET`. A name that a tool or existing code already reads keeps its
   store name, and the table records it.
5. **Restrictions.** No IP filter, which breaks when an address changes. No expiry except on a
   temporary token. `ws-admin` and `ci-deploy` carry a rotate-by date in the registry; a
   server's token rotates when the server is rebuilt or compromised.
6. **Token management.** No standing token can manage tokens. When one is needed, Geoff creates
   `tmp-token-setup` (My Profile > API Tokens > Create Token, the "Create Additional Tokens"
   template at the foot of the list, nothing added, a TTL ending tomorrow) and, for account-owned
   tokens, `tmp-account-tokens` (Account > Account API Tokens > Edit, the same TTL) from
   <https://dash.cloudflare.com/?to=/:account/api-tokens&permissionGroupKeys=%5B%7B%22key%22%3A%22account_api_tokens%22%2C%22type%22%3A%22edit%22%7D%5D&name=tmp-account-tokens>.
   Cloudflare refuses to let one make the other: "sub-token is not allowed to have permissions
   to manage other tokens" (error 1001, 2026-10-18). Each arrives in a RAM-only scratch store
   (`VALUES=/dev/shm/tmp-setup-$(id -u).age`, `LOCAL_SECRETS=$XDG_RUNTIME_DIR/self-hosting/secrets-tmp-setup`),
   never the age store, and is deleted through the API when the work ends. If a fresh token
   verifies active but answers `9109 Invalid access token` on the token endpoints, check its
   TTL start date; correcting the TTL fixed it on 2026-10-18.

| Cloudflare name | Owner | Scope | Store name | Holder and job |
|---|---|---|---|---|
| `ws-admin` | user | The scopes in the next section | `CLOUDFLARE_API_TOKEN` (wrangler's variable) | Interactive admin on the workstation |
| `ws-cairn-read` | user | Seven Read groups, below | `CAIRN_CF_READ_TOKEN` (the cairn tool reads it) | The Go `cairn` operator tool |
| `ws-r2-music-ro` | user | R2 object read, `music-library` | `MUSIC_R2_RO_ACCESS_KEY_ID` / `MUSIC_R2_RO_SECRET_ACCESS_KEY` (`music-pull` reads them) | `music-pull` |
| `ws-servers` | account | 907.life DNS, Single Redirect, and Workers Routes edit; Workers Admin (its scripts create and delete Workers), D1, Email Sending; Access apps and policies, Tunnel, Access audit logs read | `CF_WS_SERVERS_TOKEN` | The servers repo's scripts |
| `ws-r2-archive-rw` | account | R2 object read and write, `servers-archive` | `CF_WS_R2_ARCHIVE_RW_TOKEN` + pair | Workstation archive copies |
| `ws-r2-backups-ro` | account | R2 object read, `servers-backup-orpheus` and `servers-backup-ward` | `CF_WS_R2_BACKUPS_RO_TOKEN` + pair | Restores and drills |
| `orpheus-r2-backup-rw` | account | R2 object read and write, `servers-backup-orpheus` | `CF_ORPHEUS_R2_BACKUP_RW_TOKEN` + pair | Orpheus's restic |
| `ward-r2-backup-rw` | account | R2 object read and write, `servers-backup-ward` | `CF_WARD_R2_BACKUP_RW_TOKEN` + pair | Ward's restic |
| `ci-deploy` | account | Workers Editor across all Workers | Each repo's `CLOUDFLARE_API_TOKEN` Actions secret; origin `CF_CI_DEPLOY_TOKEN` | Every site deploy and Workers Builds |

`ci-deploy` is planned, not live. Until it lands, five repos' Actions secrets and the Workers
Builds build token hold `ws-admin`, and `CF_ZT_TOKEN` ("Zero Trust Edit") stays because the
aksailingclub-legacy deploy reads it. That later change swaps the five secrets and the build
token, adds Access identity-provider read to `ws-admin`, repoints `CF_ZT_TOKEN`'s readers, and
deletes it. A per-Worker Editor token can deploy over a configured custom domain or route but
cannot add or change one; that edit goes through `ws-admin`.

## Authorization: how each thing is reached non-interactively

- **Cloudflare API / Wrangler — THE CANONICAL TOKEN-SCOPE RECORD (all projects defer here;
  never restate scopes in a project doc, link to this file).** One read-write token is live:
  `ws-admin` (named "Cloudflare Admin 2026-07" until 2026-10-18), id
  `1d508f1ab69df49d3ef9572dc1917273` (a second, read-only token is recorded below). Its origin store is the workstation `~/.dotfiles/secrets/values.age`;
  `~/.local/secrets` is regenerated from it (`~/.bashrc` sources that file at line ~167, but ONLY
  in interactive shells — its line-5 interactivity guard means a script's
  `source ~/.bashrc` gets NOTHING; scripts must `source ~/.local/secrets` directly).
  GitHub Actions repos hold synced copies as the `CLOUDFLARE_API_TOKEN` secret.
  Scopes, each verified empirically 2026-07-14 (minted 2026-07-14 after dashboard edits to the
  prior token silently failed to persist): Workers scripts + schedules ✓, D1 ✓, R2 ✓,
  Access apps/policies ✓, Access service tokens ✓, Email Sending ✓ (REST + binding),
  Turnstile ✓ (granted, untested), zone read ✓, **Zone.DNS Edit ✓ (proven by live
  record deletions)**, Zone Workers Routes ✓ (added by dashboard edit 2026-07-19 after
  scripted cairn.pub deploys failed on the missing permission; GET verified live on the
  cairn.pub zone, write granted per the edit but untested; recommended grant was
  Edit on ALL zones so a newly registered zone never repeats the gap),
  API-token management ✗ (deliberate: cannot self-extend).
  Rotated into: the workstation age store, `~/.local/secrets`, and the four GH-Actions repos
  (aksailingclub-legacy/-org, ecxc-ski, 907-life). Predecessor deleted:
  "Cloudflare Admin" (`48efe6a4...`). `CF_ZT_TOKEN` was once listed here as deleted too, but
  it is live; its own bullet is below.
  Second credential: the Cloudflare MCP plugin's OAuth (not in the token list; broad
  READ incl. DNS, refuses writes). Maintenance rules: any scope change lands in THIS
  bullet, same session; after a rotation, a RUNNING Claude session's env still holds
  the OLD token (the harness captures env at session start) — prefix commands with
  `source ~/.local/secrets` until the session cycles.
- **Second managed token, read-only: `ws-cairn-read` (minted 2026-09-19 as "cairn tool read")**, stored as
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
  2026-07-14 failure above). Permission-group ids come from `user/tokens/permission_groups`
  and `accounts/{id}/tokens/permission_groups`, which only a temporary token-management token
  (scheme rule 6) can read. Registry entry:
  `~/.dotfiles/secrets/registry.md`.
- **Zero Trust token `CF_ZT_TOKEN`**, "Zero Trust Edit" at Cloudflare (workstation age store,
  and the aksailingclub-legacy Actions secret; registry entry `CF_ZT_TOKEN`). The scheme
  retires it once `ci-deploy` lands. **Use it, not `CLOUDFLARE_API_TOKEN`, for anything touching Access identity
  providers.** It reads `accounts/{id}/access/identity_providers` (two IdPs: `onetimepin` and
  `google-apps` "Google Workspace"), verified live 2026-10-10. Per the registry's 2026-08-30
  note it also creates and reads Access apps and policies. The general token got
  `auth.forbidden` on that endpoint on 2026-08-30. On 2026-10-10 the general token answers
  `success: true` with an empty list, which reads as "no IdPs" and is wrong (verified live,
  statuses and names only).
- **Worker secrets are WRITE-ONLY**: `wrangler secret list` returns NAMES, never values; a value
  set with `wrangler secret put` cannot be read back. To learn a secret's value you need its
  origin store, not the worker.
- **Access-protected ASC hosts: the `asc-cloudflare-access` recipe** (verified live 2026-10-10,
  statuses and names only). It replaces a cairn memory of that name, which never existed.
  - Hosts. `staging.aksailingclub.org` sits behind the "ASC Staging" app.
    `dev.aksailingclub.org` is not behind Access: no app covers it, and it answers 200 with no
    token.
  - Credential. Service token `claude-capture-asc-ref` (token id `aa9f1b5b-…`, 2160-hour
    duration). The ASC Staging policy "claude-capture service token" admits it (decision
    `non_identity`, include `service_token`), and that app's "Service token (CI)" policy admits
    any valid service token. The ops hosts admit only "Automated Testing - Ops Dashboard"
    (`CF_ACCESS_CLIENT_SECRET` in the registry).
  - Use. `source ~/.local/secrets`, then send `CF-Access-Client-Id: $ASC_ACCESS_CLIENT_ID` and
    `CF-Access-Client-Secret: $ASC_ACCESS_CLIENT_SECRET` (curl `-H`, Playwright
    `extraHTTPHeaders`). A 302 to the Access login means Access refused the token.
  - State on 2026-10-10: broken. The token expired on 2026-10-04, and neither variable is in
    `~/.local/secrets` or the age registry. Access shows a client secret once, at create or
    rotate, so the old secret is unrecoverable.
  - Restore (a live-account write: Geoff's go first). `POST
    accounts/{id}/access/service_tokens/{token_id}/refresh` extends the expiry. `POST
    .../{token_id}/rotate` issues a new client secret and revokes the old one, so call it once.
    Capture its single response in a shell variable, never displaying it. Run `jq -r
    .result.client_id` and `jq -r .result.client_secret` on that variable, piping each into
    `secret-set.sh ASC_ACCESS_CLIENT_ID --stdin` and `secret-set.sh ASC_ACCESS_CLIENT_SECRET
    --stdin`. Then add both to `~/.dotfiles/secrets/registry.md`.
  - A new token. `POST accounts/{id}/access/service_tokens` with `name` and `duration` answers
    201 with the same two fields; store them the same way. Then add an app policy with decision
    `non_identity` and include `{"service_token":{"token_id":"<id>"}}`.
- **The workstation registry** `~/.dotfiles/secrets/values.age` and `~/.local/secrets`: the
  workstation's own secrets (the GitHub App key, among others; the ASC Access service token has
  been absent since 2026-10-04, see the recipe's Restore step). Its
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
- **Proton Pass** (Geoff's vaults): the home for a value in no scripted store, such as a
  dashboard login or a rarely needed credential. Claude reaches the vaults Geoff granted its
  own agent (`Servers emergency` and `Workstation` to start) through `claude-pass`, and can
  create and edit items there; it never calls bare `pass-cli`. A value from any other vault
  arrives through `secret-receive NAME --pass REF`, which runs Geoff's own login in a
  throwaway session. See the global CLAUDE.md Secrets rule and `bluefin-admin.md` "Secrets".

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

**Zero Trust organization:** "Wright Family", team domain `907wrights.cloudflareaccess.com` (renamed 2026-10-18 from "Alaska Sailing Club" and `aksailingclub`). Each identity provider's callback is `https://907wrights.cloudflareaccess.com/cdn-cgi/access/callback`; the Google Workspace provider's OAuth client (`450617487145-hqf3h2ge…`, the club's Google Cloud project) must list it.

**Access apps** (live 2026-10-10): ASC Staging, ASC Handbook (+ its CMS), Ops Dashboard (ops +
staging), the Ops Schema API (public, consumed cross-origin by the handbook — do not lock it),
and `phonebook` (+ `phonebook-prov`) on phonebook.907.life. The ASC CMS Admin app on
dev.aksailingclub.org/admin is gone.
phonebook.907.life itself is a proxied `AAAA 100::` placeholder until the phonebook Worker
deploys; the `phonebook-probe` Worker, its route, and its D1 were deleted 2026-10-25.

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
