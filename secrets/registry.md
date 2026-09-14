# Workstation Secrets Registry

Plaintext inventory — no secret values here. All values live in `secrets/values.age` (encrypted).

---

## Architecture

(Folded in from the retired `docs/secrets.md`, 2026-08-30; this file is the one
secrets document, at the path every project's doctrine already references.)

```
1Password (source of truth)
    |
    v
secrets/values.age (encrypted, safe to commit)
    |
    v  scripts/secrets/sync.sh
    |
    +---> ~/.local/secrets (local env vars, sourced by .bashrc)
    +---> Cloudflare Workers (per-worker secrets via wrangler)
```

- **1Password** holds all secret values and the age encryption key
- **values.age** is the encrypted bundle committed to this repo
- **sync.sh** decrypts via 1Password CLI and pushes to targets
- **~/.local/secrets** is chmod 600, gitignored, sourced by `.bashrc`
- Decryption happens in `/dev/shm` (tmpfs); plaintext never touches disk

**Sync-time** (occasional, needs 1Password): `sync.sh --local` after cloning or
when secrets change. **Runtime** (day to day, no 1Password): secrets are env
vars already sourced by `.bashrc`; read `$FASTMAIL_API_TOKEN` etc. directly and
never call `op` to fetch what the environment already carries.

**Sudo helper**: `claude-sudo-setup` fetches the sudo password from 1Password
into a tmpfs cache (`/dev/shm/claude-sudo-$UID`, umask 077); `claude-askpass`
supplies it to `sudo -A`; `claude-sudo-clear` shreds it when a Claude session
exits, and reboot clears it regardless. The password persists nowhere on disk.

**What goes where**: sensitive tokens in `~/.local/secrets` via sync.sh;
non-sensitive config (paths, emails, model names) as plain `.bashrc` exports;
worker secrets pushed by sync.sh via `wrangler secret put`; the sudo password
in 1Password plus the tmpfs cache above.

---

## How to Decrypt

1. **Authenticate 1Password CLI** (required once per session):
   ```bash
   eval $(op signin)
   ```

2. **Decrypt interactively** (for inspection):
   ```bash
   age --decrypt \
     -i <(op item get "Workstation age encryption key" --fields notesPlain --reveal \
          | sed 's/^"//;s/"$//') \
     ~/.dotfiles/secrets/values.age
   ```

3. **Run sync** (decrypt + push to local + workers):
   ```bash
   ~/.dotfiles/scripts/secrets/sync.sh
   ```

---

## Sync Script Modes

```
sync.sh               # Decrypt + push local + all workers
sync.sh --local       # Local only (no worker push)
sync.sh --worker NAME # Single worker only
sync.sh --dry-run     # Show what would happen, no changes
sync.sh --verify      # Diff targets vs registry, exits non-zero on mismatch
```

Local secrets land in `~/.local/secrets` (chmod 600, gitignored), sourced by `.bashrc`.

---

## How to Add / Update a Secret

**Use `scripts/secrets/secret-set.sh` — do not leave loose key files on disk.** It edits
`values.age` (the source of truth), verifies the re-encrypted blob, and regenerates
`~/.local/secrets`. Then document the secret below and, for Workers, add it to the routing
table in `sync.sh`.

```bash
secret-set.sh NAME --value 'literal'    # single-line value (token, id)
secret-set.sh NAME --file PATH          # raw file contents (must be single-line)
secret-set.sh NAME --b64-file PATH      # base64-encode a file → one line (PEMs / multi-line)
secret-set.sh --sync                    # just regenerate ~/.local/secrets
secret-set.sh --dry-run NAME --value …  # preview, write nothing
```

`values.age` is **line-parsed** (`KEY=value`, one per line), so multi-line material (e.g. an
RSA PEM) **must** be stored base64-encoded via `--b64-file`; decode at the consumer
(`atob()` in a Worker, `base64 -d` in shell). Re-encryption targets the single recipient
`age197mcd2m3z90t49n9t5v3ujjntw7krfkw5y9sjfc545v28qvezugshg7jgk`.

**Authenticate once per session.** This box uses 1Password **desktop-app integration** —
there is no reusable CLI session token (`op signin --raw` returns nothing). So `secret-set.sh`
fetches the age key from 1Password on first use, caches it in tmpfs
(`/dev/shm/.age-key-$UID`, chmod 600), and reuses it for the rest of the session — only the
first call prompts. The cache is wiped on reboot, when the `claude` shell function exits, or
via `scripts/secrets/secret-session-clear.sh`. `sync.sh` shares the same cache and the
same once-per-session behavior.

To rotate: regenerate the source credential, then `secret-set.sh NAME …` overwrites it.

---

## Master Routing Table

(Worker names: 907-life's worker is `907-life`; ecxc.ski's worker is `ecxc` — renamed from
`ecnordic` at the ECXC rebrand, Rename 4, 2026-06-08.)

(Regenerated 2026-08-30 against `sync.sh`'s WORKER_SECRETS routing, the code-side source
of truth; a mismatch between this table and that table is a bug in whichever changed last.)

| Secret              | Local | 907-life | ecxc | asc-site | xcathletes |
|---------------------|-------|----------|------|----------|------------|
| CLOUDFLARE_API_TOKEN | ✓    | ✓        | —    | —        | —          |
| CF_ZT_TOKEN         | ✓     | —        | —    | —        | —          |
| CF_ACCESS_CLIENT_SECRET | ✓ | —        | —    | —        | —          |
| ANTHROPIC_API_KEY   | ✓     | —        | ✓    | ✓        | —          |
| CMS_BOT_PAT         | ✓     | —        | —    | —        | —          |
| RESEND_API_KEY      | ✓     | ✓        | ✓    | —        | —          |
| CONTACT_EMAIL       | ✓     | —        | —    | —        | ✓          |
| DAISYUI_BLUEPRINT_LICENSE | ✓ | —      | —    | —        | —          |
| DAISYUI_BLUEPRINT_EMAIL | ✓  | —        | —    | —        | —          |
| HCLOUD_TOKEN        | ✓     | —        | —    | —        | —          |
| FASTMAIL_API_TOKEN  | ✓     | —        | —    | —        | —          |
| GITHUB_APP_ID       | ✓     | ✓        | —    | —        | —          |
| GITHUB_APP_INSTALLATION_ID | ✓ | ✓     | —    | —        | —          |
| GITHUB_APP_PRIVATE_KEY_B64 | ✓ | ✓     | ✓    | —        | ✓          |
| GOOGLE_SA_KEY_B64   | ✓     | —        | ✓    | —        | —          |
| TWILIO_ACCOUNT_SID  | ✓     | —        | —    | —        | ✓          |
| TWILIO_API_KEY_SID  | ✓     | —        | —    | —        | ✓          |
| TWILIO_API_KEY_SECRET | ✓   | —        | —    | —        | ✓          |
| TWILIO_AUTH_TOKEN   | ✓     | —        | —    | —        | ✓          |
| VAPID_PRIVATE_KEY   | ✓     | —        | —    | —        | ✓          |
| MUSICBOX_TUNNEL_TOKEN | ✓ | —      | —    | —        | —          |
| ND_PASSWORDENCRYPTIONKEY | ✓ | —       | —    | —        | —          |
| DUBPLATE_SMTP_PASSWORD | ✓  | —        | —    | —        | —          |
| MUSICBOX_SMTP_PASSWORD | ✓  | —        | —    | —        | —          |
| ND_SPOTIFY_ID       | ✓     | —        | —    | —        | —          |
| ND_SPOTIFY_SECRET   | ✓     | —        | —    | —        | —          |
| NAVIDROME_ADMIN_USER | ✓    | —        | —    | —        | —          |
| NAVIDROME_ADMIN_PASSWORD | ✓ | —       | —    | —        | —          |
| FILEBROWSER_ADMIN_PASSWORD | ✓ | —     | —    | —        | —          |
| MUSICBOX_R2_ACCESS_KEY_ID | ✓ | —      | —    | —        | —          |
| MUSICBOX_R2_SECRET_ACCESS_KEY | ✓ | — | —    | —        | —          |
| MUSIC_R2_RO_ACCESS_KEY_ID | ✓ | —      | —    | —        | —          |
| MUSIC_R2_RO_SECRET_ACCESS_KEY | ✓ | — | —    | —        | —          |
| MUSICBOX_HC_BACKUP_URL | ✓ | —      | —    | —        | —          |
| MUSICBOX_HC_IMPORT_URL | ✓ | —      | —    | —        | —          |
| MUSICBOX_HC_DISK_URL | ✓   | —      | —    | —        | —          |
| MUSICBOX_HC_NAVIDROME_URL | ✓ | —    | —    | —        | —          |
| PINGS_ADMIN_TOKEN | ✓       | —      | —    | —        | —          |

> `DUBPLATE_SMTP_PASSWORD` (Fastmail app password, SMTP scope, minted 2026-08-31 replacing a
> never-valid predecessor) is canonical; `MUSICBOX_SMTP_PASSWORD` is a same-value alias the
> still-live shell layer consumes, retiring at the rewrite's T13 rename close. Rotation:
> Fastmail app-passwords page + secret-receive + deploy.

> **DUBPLATE_* additive block (minted 2026-08-31, rewrite T12; 30 names, all Local-only,
> rendered to the box env by musicbox/scripts/deploy.sh).** Aliases carrying an existing
> secret's value under the new name: R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,
> NAVIDROME_ADMIN_{USER,PASSWORD}, PING_{BACKUP,DISK,NAVIDROME}_URL, SMTP_PASSWORD (above).
> The rest are NEW non-secret values (SMTP host/port/user/from, R2 account/bucket/remote,
> Navidrome URL, config/library paths) that were script constants before the rewrite; the
> authoritative name list and per-name comments live in musicbox
> env/musicbox.env.template's T12 block. The MUSICBOX_*/ND-alias generation retires at T13;
> these DUBPLATE_ names are then the only ones. Uploader Pass A adds (2026-09-01):
> UPLOADS_DIR, SERVE_BIND_ADDRS (loopback now; the bridge IP joins at U12a), SERVE_PORT,
> PUBLIC_NAVIDROME_URL, ACCESS_TEAM_DOMAIN (the account's one Zero Trust org), and
> TRIGGER_DIR (conductor's TriggerDir ruling). DUBPLATE_ACCESS_AUD minted 2026-09-01 at
> U12a: the AUD of Access app "dubplate uploader" (path-scoped music.907.life/upload, app id
> b9d9f27d-bfbf-4c66-a437-5b3074785eee); rotate by recreating the app and re-running
> secret-set.sh. SERVE_BIND_ADDRS gains the pinned compose bridge gateway at U12a deploy.
> DUBPLATE_SERVE_SITE_NAME minted 2026-09-01 at U12b: non-secret masthead text, in the
> age store only because the env manifest's values all originate there; change it by
> re-running secret-set.sh and deploy.sh. Value set to "907 Music" 2026-09-02 (Geoff's
> pick at the Pass B attended gate; was "Wright Family Music").

> The musicbox rows are Local-only by design: none of these secrets touch a Cloudflare
> Worker. `MUSICBOX_TUNNEL_TOKEN` and the Navidrome values land on the VPS via
> `musicbox/scripts/deploy.sh` writing `/etc/musicbox/env` (root:root 0600); the R2 pairs
> are consumed directly by rclone on the box (`MUSICBOX_R2_*`) and on the workstation
> (`MUSIC_R2_RO_*`). See `~/Projects/musicbox/docs/STATUS.md` for the current build state.

> The `MUSICBOX_HC_*_URL` and `PINGS_ADMIN_TOKEN` rows are also Local-only: the ping URLs
> reach the musicbox VPS via its own env, and `PINGS_ADMIN_TOKEN` is consumed by
> workstation scripts (`scripts/add-check`/`remove-check`) — neither is ever a `pings`
> Worker secret. Provisioned live 2026-08-31 (pings Task P2b); see
> `~/Projects/pings/docs/STATUS.md`.

> The ecxc worker stopped needing `GITHUB_APP_ID`/`GITHUB_APP_INSTALLATION_ID` as secrets at
> the Waymark rebuild (2026-07-05): the v2 adapter commits both in `cairn.config.ts` (they
> are public identifiers), and only the private key stays secret. 907-life still takes all
> three as secrets.

> `GITHUB_APP_*` are the cairn-cms committing identity (GitHub App, App ID 3847496,
> Installation `135372268` — single install on glw907, both repos selected). **Both the `ecxc`
> and `907-life` workers are wired into `sync.sh` and pushed (ecxc go-live 2026-05-25 as
> ecnordic, 907-life go-live 2026-05-26);** `sync.sh --worker 907-life` re-pushes the shared
> App secrets reproducibly.
>
> **Per-site, NOT in this registry:** each cairn site's `MAGIC_LINK_SECRET` + `SESSION_SECRET`
> are worker-only (set directly via `wrangler secret put`, freshly generated per site so sessions
> don't cross sites — the locked "no cross-site SSO" decision). Rotatable: regenerate + re-put to
> invalidate all active links/sessions. `sync.sh --verify` will list them as "extra" on both the
> ecxc and 907-life workers — expected (same as CONTACT_EMAIL / TURNSTILE_SECRET_KEY).

**1Password only** (not in values.age):
- `WORKSTATION_SUDO` — sudo password, stored as `op://Private/Workstation sudo/password`

**Out of scope** (ASC project manages separately):
- STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
- DISCORD_WEBHOOK_* (four webhooks)

**Orphaned** (removed from .bashrc, DNS migrated to Cloudflare):
- CLOUDNS_AUTH_ID, CLOUDNS_AUTH_PASSWORD

**Non-secrets** (remain as plain exports in .bashrc):
- CLAUDE_CODE_SUBAGENT_MODEL, WORKSPACE_ADMIN_EMAIL, ANDROID_HOME, AGE_KEY_FILE
- NVM_DIR, GOOGLE_APPLICATION_CREDENTIALS (path only), SUDO_ASKPASS

---

## Per-Secret Scope

### CLOUDFLARE_API_TOKEN
- **Grants**: Full Cloudflare API access (DNS, Workers, Pages, Access, R2)
- **Used by**: wrangler, DNS automation scripts, all project deployments
- **Rotate at**: https://dash.cloudflare.com/profile/api-tokens
- **Exposure post-mortem (2026-08-30 audit)**: a PRIOR value of this token sat in plaintext
  in the public repo's git history (`bash/.bashrc`, 2026-01-30 to 2026-03-19, also copied
  into `cli-mode.md` for a period). Verified 2026-08-30: the leaked value is dead
  (Cloudflare rejects it) and differs from the live value by hash. History PURGED
  2026-08-30 on Geoff's go (git filter-repo: token redacted, browser-bookmarks blobs
  dropped, HEAD tree verified byte-identical, force-pushed, 374 commits rewritten).
  Pre-purge backup: `~/.local/state/workstation-prepurge-2026-08-30.bundle` (mode 600,
  still contains the dead token; delete when no longer wanted). Secret scanning + push
  protection are enabled on the repo, and the claude-secret-guard hook blocks
  credential-shaped writes at the source.
- **Also wrapped as a Workers Builds build token** (2026-08-22, Geoff's call): build token
  `503cd3fe-a701-4d5e-be7b-4c93a61335fa` "xcathletes build token (CLAUDE_CODE admin token)"
  backs the Workers Builds triggers for `xcathletes` and both `907-life` triggers (the
  three older build tokens on the account were rolled). Rotating this token breaks
  auto-deploy for both workers until a new build token is created
  (`POST /accounts/{id}/builds/tokens` with the new token id and value) and each trigger
  is PATCHed to it. Scope added 2026-08-22: Workers Builds Configuration: Edit.
- **Issuer-side token name**: "Cloudflare Admin 2026-07" (Cloudflare dashboard > Manage
  Account > API Tokens). Permission groups added 2026-08-30 for the pings Worker build-out
  (Task P2b): Workers KV Storage: Edit, Email Routing Addresses: Edit — plus Cloudflare
  Tunnel: Edit (closed the same day, the musicbox `CF_ZT_TOKEN` blocker above). The token
  cannot edit its own permissions (confirmed: `GET /user/tokens/{id}` 403s even for this
  token against itself), so any future scope gap needs the same dashboard-edit path.

### HCLOUD_TOKEN
- **Grants**: Hetzner Cloud API read/write, project `musicbox` only
- **Token name at issuer**: claude-code-thinkpad-x1
- **Used by**: musicbox provisioning (`scripts/provision.sh`, hcloud CLI)
- **Rotate at**: console.hetzner.cloud > project musicbox > Security > API tokens
- **Received 2026-08-30** via `secret-receive` (desktop dialog, value never in transcript)
- **Rotated 2026-08-30**: the value in the store as of this date is the rotated token
  (superseding whatever the account held before); confirmed live via `hcloud` calls
  during musicbox Task 4 provisioning the same day.

### CF_ZT_TOKEN
- **Grants**: Cloudflare Zero Trust API (Access apps, policies, identity providers).
  Empirically confirmed 2026-08-30 (musicbox Task 5): can create/read Access
  applications and policies, and read Access identity providers (`onetimepin`,
  `google-apps`) — the general-purpose `CLOUDFLARE_API_TOKEN` gets `auth.forbidden` on
  the identity-providers endpoint, so this token is the one to use for IdP lookups.
  **Carries Cloudflare Tunnel:Edit as of 2026-08-30** — previously missing on both this
  token and `CLOUDFLARE_API_TOKEN` (`POST .../cfd_tunnel` 403ing
  `{"code":10000,"message":"Authentication error"}`); Geoff added the permission group to
  `CLOUDFLARE_API_TOKEN` via the dashboard the same day as the pings-Worker permission
  fixes noted on that entry above (API token self-management is deliberately not
  grantable via the API itself). Resume point for the still-pending musicbox tunnel
  creation: musicbox `docs/STATUS.md`.
- **Used by**: ASC ops dashboard configuration scripts; musicbox Cloudflare Access wiring
  (Task 5)
- **Rotate at**: https://dash.cloudflare.com/profile/api-tokens

### CF_ACCESS_CLIENT_SECRET
- **Grants**: Service token auth for Cloudflare Access protected apps
- **Client ID**: 355524dff8edea34539419e97c66a085.access
- **Used by**: Testing ops dashboard endpoints from CLI
- **Rotate at**: Cloudflare Access > Service Tokens dashboard

### DAISYUI_BLUEPRINT_LICENSE
- **Grants**: the daisyUI Blueprint MCP server (official, paid) for Claude Code; read by the user-scope MCP entry `daisyui-blueprint` through the `daisyui-blueprint-mcp` launcher (dotfiles bin), which sources `~/.local/secrets` at spawn and exports the pair as `LICENSE` and `EMAIL`
- **Used by**: Claude Code on this workstation only (never a worker, never the cairn repo's committed `.mcp.json`)
- **Rotate at**: https://daisyui.com/blueprint/ (account page); purchased 2026-09-13

### ANTHROPIC_API_KEY
- **Grants**: Claude API access (claude-3-*, claude-sonnet-*, etc.)
- **Used by**: Claude CLI, any scripts using the Anthropic SDK, ecxc worker and asc-site worker (editor tidy copy-edit)
- **Rotate at**: https://console.anthropic.com/settings/keys
- **Rotated 2026-07-14**: the prior key had been silently revoked (discovered when asc-site's
  editor Tidy failed auth); new key validated with a live messages call and pushed to both workers.

### CMS_BOT_PAT
- **Grants**: GitHub repository write access for CMS automation
- **Used by**: Content publish workflows, automated PR creation
- **Rotate at**: https://github.com/settings/tokens

### RESEND_API_KEY
- **Grants**: Resend transactional email API
- **Used by**: 907-life contact form worker, ecxc worker (all outbound mail: registration
  record/parent/coach copies, contact form, cairn magic links; the 2026-07-14 cutover off
  Cloudflare Email Service), local email testing
- **Scope note**: the Resend account's one verified sending domain is ecxc.ski as of
  2026-07-14 (aksailingclub.org was removed the same day); sends from any other domain fail
- **Rotate at**: https://resend.com/api-keys

### FASTMAIL_API_TOKEN
- **Grants**: Full Fastmail JMAP access (mail, contacts, calendars, files, settings)
- **Domain**: 907.life (business plan)
- **Used by**: aerc (via `op read`), Claude Code JMAP scripting (via env var), poplar
  corpus harvest
- **Rotate at**: Fastmail > Settings > Privacy & Security > App Passwords
- **History**: 2026-07-19 the stored value had gone stale (JMAP 401); re-anchored from the
  1Password Fastmail item's `api access` field via secret-set.sh. If it goes stale again,
  the 1Password copy and this store have diverged; re-anchor after any Fastmail-side
  rotation.

### GITHUB_APP_ID / GITHUB_APP_INSTALLATION_ID / GITHUB_APP_PRIVATE_KEY_B64
- **Grants**: cairn-cms GitHub App — `Contents: Read & write` on glw907/ecnordic-ski and
  glw907/907-life. Used to mint short-lived installation tokens that commit markdown to
  `main` (committer = `cairn-cms[bot]`, author = the editor).
- **App ID**: 3847496 (GitHub App "cairn-cms", owner glw907)
- **Key encoding**: `GITHUB_APP_PRIVATE_KEY_B64` is the RSA PEM base64-encoded single-line
  (the registry is line-parsed; multi-line PEM would break it). Decode with `atob()` in the
  Worker before handing to `@octokit/auth-app`.
- **Used by**: cairn-cms admin Worker (ecnordic + 907-life) — wired in Pass A.
- **Rotate at**: https://github.com/settings/apps → cairn-cms → Private keys (generate new,
  base64 it, update values.age, re-run sync.sh). Revoke old key in the same screen.

### GOOGLE_SA_KEY_B64
- **Grants**: Google Sheets/Drive API as `ecxc-sheets@ecxc-registrations.iam.gserviceaccount.com`
  (GCP project `ecxc-registrations`, owned by geoff@907.life). Editor on the ECXC registration
  roster spreadsheet only ("Talkeetna Camp Registrations", ID in ecxc-ski's `wrangler.toml`
  as `REGISTRATION_SHEET_ID`).
- **Key encoding**: the service-account JSON key file, base64-encoded single-line
  (values.age is line-parsed). Decode with `atob()` in the Worker.
- **Used by**: the `ecxc` Worker's registration forms (Sheets `values.append` per
  submission; added by the registration-forms pass, 2026-07-13).
- **Rotate at**: `gcloud iam service-accounts keys create <file> --iam-account=ecxc-sheets@ecxc-registrations.iam.gserviceaccount.com --project=ecxc-registrations`,
  then `secret-set.sh GOOGLE_SA_KEY_B64 --b64-file <file>`, `sync.sh --worker ecxc`, delete
  the file and the old key (`gcloud iam service-accounts keys list/delete`). No loose copy
  lives on disk; GCP IAM is the mint-a-new-key origin.

### TWILIO_ACCOUNT_SID / TWILIO_API_KEY_SID / TWILIO_API_KEY_SECRET
- **Grants**: Twilio REST API on the team-platform account (`AC9387aa5b...`), via the
  Standard API key "xcathletes-platform-2026-08" (key auth works on the v1 APIs and on
  classic-API subresources; the account-root read is excluded, use subresource paths).
- **Used by**: xcathletes platform provisioning (number purchase, toll-free verification or
  10DLC filing) and, later, the xcathletes Worker's OTP + SMS fallback sends. Add the worker
  column and sync.sh routing when platform pass 1 T1 creates the Worker.
- **Scope note**: account funded 2026-08-01 ($20, out of trial). Owns toll-free
  +1 888-609-8679 (bought 2026-08-02, ~$2.15/mo; verification submitted, see ecxc-ski's
  team-platform T0 ledger for SIDs). The API key SID is paired with its secret; rotate them
  together.
- **Rotate at**: Twilio Console -> Account -> API keys & tokens (revoke, recreate under the
  same name with a new date, then `secret-set.sh` all three and re-sync).

### CONTACT_EMAIL
- **Grants**: nothing; it is the destination inbox address for the xcathletes `/contact`
  form (`geoff.wright@xcathletes.org`, a Cloudflare Email Routing forward to
  `geoff@907.life`). Stored here so the address is config, never a literal in source,
  per xcathletes-org's `docs/deploy.md`. Installed 2026-08-26 (public-design pass).
  Note: 907-life's separately-set CONTACT_EMAIL stays worker-only; only the xcathletes
  one is managed here.
- **Used by**: xcathletes Worker (`WORKER_SECRETS["xcathletes"]`), the `/contact` action.
- **Rotate at**: no credential to rotate; change the value with `secret-set.sh` and
  `sync.sh --worker xcathletes` when the operator inbox moves, and adjust the Email
  Routing rule on the xcathletes.org zone to match.

### TWILIO_AUTH_TOKEN
- **Grants**: the Twilio account's primary Auth Token (full account access, broader than the
  API key). The xcathletes Worker uses it only to verify the `X-Twilio-Signature` on inbound
  SMS webhooks (`/api/sms/inbound`, STOP/START/HELP); Twilio signs callbacks with this token
  and nothing else, so the API key cannot substitute. Installed 2026-08-22.
- **Used by**: xcathletes Worker (`WORKER_SECRETS["xcathletes"]`).
- **Rotate at**: Twilio Console -> Account -> API keys & tokens -> Auth Token (request a
  secondary token, promote it, then `secret-set.sh` and `sync.sh --worker xcathletes`).

### VAPID_PRIVATE_KEY
- **Grants**: signs Web Push messages as the xcathletes application server. Paired with the
  PUBLIC key, which is not secret and is committed as the `VAPID_PUBLIC_KEY` var in
  `xcathletes-org/wrangler.jsonc`; `VAPID_SUBJECT` (`mailto:`) is a committed var too.
  Generated 2026-08-21 with `@mmmike/web-push`'s `generateVapidKeys()`, base64url, P-256.
- **Used by**: the xcathletes Worker's push send path (`src/lib/server/push/send.ts`), which
  reaches only the four allowlisted push hosts. Routed to the worker through sync.sh.
- **Scope note**: it signs, it does not encrypt. It cannot address a device on its own: a
  push needs the device's own endpoint plus its p256dh and auth keys, which live in
  `push_subscriptions` in D1. Not recoverable from any API, unlike TURNSTILE_SECRET_KEY,
  which is why it lives in this store rather than worker-only.
- **Rotate at**: nowhere upstream; generate a fresh pair locally. **Rotation invalidates
  every existing device subscription.** The browser binds a subscription to the public key it
  was created with, so a new pair does not swap in: every installed phone stops receiving
  until its own service worker fires `pushsubscriptionchange` and re-subscribes, and a phone
  that never opens the app again never recovers. Rotate only on suspected compromise, and
  change `VAPID_PUBLIC_KEY` in `wrangler.jsonc` in the same deploy.

### MUSICBOX_TUNNEL_TOKEN
- **Grants**: connects the musicbox VPS's `cloudflared` container to the Cloudflare edge
  as the named tunnel `musicbox` (config-managed, ingress set via the Cloudflare API —
  see `musicbox/config/cloudflared-tunnel-config.json`). No inbound port is opened on the
  box; this token is how it dials out to publish `music.907.life` and `inbox.907.life`.
- **Used by**: the `cloudflared` service in `musicbox/compose.yaml` (`TUNNEL_TOKEN` env,
  via `/etc/musicbox/env`, written by `deploy.sh`).
- **Rotate at**: Cloudflare dashboard/API, `cfd_tunnel/{id}/token` (regenerating
  invalidates the running container's connection; redeploy after rotating).
- **Status 2026-08-31**: minted, then rotated same day after an exposure incident (below).
  Live tunnel `musicbox` is id `b6781175-000b-40c3-a54a-05906ab25037` (`config_src:
  cloudflare`), created/configured via `CLOUDFLARE_API_TOKEN` (Cloudflare Tunnel:Edit landed
  on it 2026-08-30); ingress PUT from `musicbox/config/cloudflared-tunnel-config.json` and
  verified by GET. DNS: `music.907.life` and `inbox.907.life` are proxied CNAMEs to
  `b6781175-000b-40c3-a54a-05906ab25037.cfargotunnel.com` on zone `907.life`. `cloudflared` is
  not yet running on the box, so both hostnames 530 until the first real deploy; musicbox
  `docs/STATUS.md` carries the resume step.
- **Incident + rotation, 2026-08-31**: the first tunnel (id `66fa450c-5abb-459d-a1f8-b80d8d19e07c`,
  minted earlier the same day) had its `cfd_tunnel` CREATE response body — which carries the
  tunnel secret and connector token alongside the id — displayed in full in an agent
  transcript instead of being narrowed to `.result.id` first. Treated as compromised on
  disclosure per standing incident doctrine. Remediation: the tunnel was deleted (delete-then-
  recreate, the cheap definitive path since `cloudflared` was not yet deployed against it —
  Cloudflare has no API to rotate a tunnel's secret in place), a new tunnel was created under
  the same name, its ingress re-PUT, both DNS CNAMEs repointed to the new tunnel id, and
  `MUSICBOX_TUNNEL_TOKEN` overwritten with the new tunnel's token via `secret-set.sh --stdin`
  (name-only verified, count 1, length 240). The DELETE and the tunnel-recreate POST were both
  refused by the Claude Code auto-mode classifier when attempted from a subagent session; the
  rotation completed once retried from the main session with the user present. Lesson for
  future tunnel work: always pipe a `cfd_tunnel` CREATE (or token-fetch) response through
  `jq -r '.result.id'` (or the specific field needed) and never display or log the raw body.

### ND_PASSWORDENCRYPTIONKEY
- **Grants**: nothing external; it is Navidrome's at-rest encryption key for the user
  passwords it must keep recoverable (Subsonic token auth requires the server to
  reconstruct the plaintext password, so Navidrome cannot hash-and-forget like a normal
  auth system). Generated 2026-08-30 with `openssl rand -hex 32`.
- **Used by**: the Navidrome container in `musicbox/compose.yaml` (`ND_PASSWORDENCRYPTIONKEY`
  env, via `/etc/musicbox/env`).
- **Rotate at**: nowhere upstream; generate a fresh value locally. **Rotation makes every
  stored user password unrecoverable** — Navidrome cannot decrypt passwords written under
  the old key, so every account (admin and family) needs its password reset after a
  rotation. Rotate only on suspected compromise.

### NAVIDROME_ADMIN_USER / NAVIDROME_ADMIN_PASSWORD
- **Grants**: the Navidrome admin account on `music.907.life`, created on first boot.
  Username fixed to `admin`; password generated 2026-08-30 with `openssl rand -hex 16`.
  Stored under `NAVIDROME_ADMIN_PASSWORD` (renamed from an earlier
  `NAVIDROME_ADMIN_PASS` key 2026-08-31 — same value, no rotation — to match the exact
  name `env/musicbox.env.template` and `deploy.sh` require; the old key can be dropped
  next rotation).
- **Used by**: Navidrome first-run bootstrap (`musicbox/compose.yaml` / `deploy.sh`);
  delivered to Geoff out of band per the spec's unique-password note (Task 8).
- **Rotate at**: Navidrome's own admin UI (change password), or reset via its CLI on the
  box; update the store afterward so `deploy.sh` reruns stay accurate. Family accounts
  (Task 8) are separate logins, not derived from this one.

### FILEBROWSER_ADMIN_PASSWORD
- **Grants**: FileBrowser Quantum's built-in admin-bootstrap account on
  `inbox.907.life` (username fixed to `admin`, not configurable). Minted 2026-08-31,
  discovered as a hard blocker during musicbox's first live deploy: with no value set,
  the container's own first-run admin creation used a shorter-than-8-char default,
  which `config/filebrowser.yaml`'s `auth.methods.password.minLength: 8` rejected,
  crash-looping the container (`store.Users.Save: password must be at least 8
  characters long`).
- **Used by**: `musicbox/compose.yaml`'s `filebrowser` service
  (`FILEBROWSER_ADMIN_PASSWORD` env var, FileBrowser's own native name; config
  equivalent `auth.methods.password.adminPassword`).
- **Rotate at**: `secret-set.sh FILEBROWSER_ADMIN_PASSWORD --stdin` then redeploy —
  FileBrowser re-applies this value to the admin account on every boot. Task 8
  replaces this bootstrap account with per-contributor accounts.

### MUSICBOX_R2_ACCESS_KEY_ID / MUSICBOX_R2_SECRET_ACCESS_KEY
- **Grants**: R2 API token "musicbox-vps" — Object Read & Write, scoped to bucket
  `music-library` only.
- **Used by**: the musicbox VPS's `music-backup` script (rclone sync of `library/` and
  `state/` to R2, per the pinned bucket layout in the design spec).
- **Rotate at**: Cloudflare dashboard > R2 > Manage API tokens (revoke "musicbox-vps",
  mint a replacement scoped identically, then `secret-set.sh` both halves and rerun
  `deploy.sh` so the box picks up the new pair).

### MUSIC_R2_RO_ACCESS_KEY_ID / MUSIC_R2_RO_SECRET_ACCESS_KEY
- **Grants**: R2 API token "claude-code-thinkpad-x1" — Object Read only, scoped to bucket
  `music-library` only. Deliberately read-only: the workstation mirror pull
  (`music-pull`, Task 8) can never delete or overwrite the box's backup, so no
  argument-order slip in a local script can wipe R2.
- **Used by**: the workstation's `music-pull` script (`rclone copy` of `library/` to
  `~/Music`).
- **Rotate at**: Cloudflare dashboard > R2 > Manage API tokens (revoke
  "claude-code-thinkpad-x1", mint a replacement scoped identically, then `secret-set.sh`
  both halves).

### MUSICBOX_HC_BACKUP_URL / MUSICBOX_HC_IMPORT_URL / MUSICBOX_HC_DISK_URL / MUSICBOX_HC_NAVIDROME_URL
- **Grants**: a ping-only URL for exactly one dead-man's-switch check on the `pings`
  Worker (`pings.907.life`) — musicbox's daily backup, hourly import, hourly disk, and
  Navidrome-heartbeat checks respectively. The threat model is stated plainly in the
  pings spec: a ping URL is not read-only, so it carries the same sensitivity as the
  monitored service's own secrets (anyone holding one can keep a dead check reading
  green forever).
- **Used by**: the musicbox VPS's timer scripts (`ping_hc`), via `/etc/musicbox/env`.
  `_DISK_URL` and `_NAVIDROME_URL` were pre-minted (2026-08-31, period 60/grace 15,
  matching `_IMPORT_URL`'s cadence) so `deploy.sh`'s all-vars-present render gate
  passes ahead of Task 6's disk-space and Navidrome-heartbeat scripts; each sits
  unpinged (and past its default one-period arming window) until that task wires a
  real `ping_hc disk` / `ping_hc navidrome` call — an expected, already-armed alert,
  not a defect.
- **Rotate at**: `~/Projects/pings/scripts/remove-check <name>` then
  `add-check <name> --period ... --grace ...` piped straight into `secret-set.sh
  <NAME> --stdin` — a fresh slug each time, never edited in place.

### PINGS_ADMIN_TOKEN
- **Grants**: the `pings` Worker's `/admin/checks` endpoints (register/deregister a
  check) — a workstation-only credential, never held by any monitored service.
- **Used by**: workstation scripts only (`~/Projects/pings/scripts/add-check`,
  `remove-check`).
- **Rotate at**: re-run `~/Projects/pings/scripts/provision.sh` (idempotent by design;
  every run rotates `ADMIN_TOKEN` into both the Worker secret and this store, invalidating
  any prior copy).

---

## 907-life Worker — Existing Secrets Audit

Secrets currently set on the worker (via `wrangler secret list --name 907-life`):
- CONTACT_EMAIL — not managed by this registry (worker-only config)
- RESEND_API_KEY — managed here
- TURNSTILE_SECRET_KEY — not managed by this registry (worker-only config)
- GITHUB_APP_ID / GITHUB_APP_INSTALLATION_ID / GITHUB_APP_PRIVATE_KEY_B64 — managed here (cairn admin, go-live 2026-05-26)
- MAGIC_LINK_SECRET / SESSION_SECRET — worker-only (per-site cairn HMAC keys, set directly via `wrangler secret put`)

Secrets this registry will set:
- CLOUDFLARE_API_TOKEN — added by sync.sh
- RESEND_API_KEY — updated by sync.sh
- GITHUB_APP_ID / GITHUB_APP_INSTALLATION_ID / GITHUB_APP_PRIVATE_KEY_B64 — pushed by sync.sh

> The `--verify` mode will report CONTACT_EMAIL, TURNSTILE_SECRET_KEY, MAGIC_LINK_SECRET, and
> SESSION_SECRET as "extra" (present on worker but not in registry). This is expected — they're
> managed elsewhere (worker-only config / per-site HMAC keys).

---

## age Key Details

- **Algorithm**: X25519 (age native)
- **Public key**: age197mcd2m3z90t49n9t5v3ujjntw7krfkw5y9sjfc545v28qvezugshg7jgk
- **Private key storage**: 1Password > Private vault > "Workstation age encryption key"
- **No persistent copy of THIS store's key on disk** — it is fetched from 1Password at
  decrypt time and cached only in tmpfs. (The separate ASC project key at
  `~/.config/age/asc-key.txt` is a different key for a different store and does live on
  disk, mode 600, by that project's own design.)
