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
| CAIRN_CF_ACCOUNT_ID | ✓     | —        | —    | —        | —          |
| CAIRN_CF_READ_TOKEN | ✓     | —        | —    | —        | —          |
| CAIRN_GH_READ_TOKEN | ✓     | —        | —    | —        | —          |
| CAIRN_DOCS_READER_OAUTH_TOKEN | ✓ | — | — | — | — |
| CAIRN_SCRATCH_CF_TOKEN | ✓ | — | — | — | — |
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
| GOOGLE_WORKSPACE_CLI_CLIENT_ID | ✓ | —    | —    | —        | —          |
| GOOGLE_WORKSPACE_CLI_CLIENT_SECRET | ✓ | — | —  | —        | —          |
| TWILIO_ACCOUNT_SID  | ✓     | —        | —    | —        | ✓          |
| TWILIO_API_KEY_SID  | ✓     | —        | —    | —        | ✓          |
| TWILIO_API_KEY_SECRET | ✓   | —        | —    | —        | ✓          |
| TWILIO_AUTH_TOKEN   | ✓     | —        | —    | —        | ✓          |
| VAPID_PRIVATE_KEY   | ✓     | —        | —    | —        | ✓          |
| DUBPLATE_SMTP_PASSWORD | ✓  | —        | —    | —        | —          |
| MUSIC_R2_RO_ACCESS_KEY_ID | ✓ | —      | —    | —        | —          |
| MUSIC_R2_RO_SECRET_ACCESS_KEY | ✓ | — | —    | —        | —          |
| PINGS_ADMIN_TOKEN | ✓       | —      | —    | —        | —          |
| DUBPLATE_MAGIC_LINK_SECRET | ✓ | —   | —    | —        | —          |
| DUBPLATE_SESSION_SECRET | ✓ | —      | —    | —        | —          |
| PHONEBOOK_PHONE_ADMIN_KITCHEN | ✓ | — | — | — | — |

> `DUBPLATE_MAGIC_LINK_SECRET` and `DUBPLATE_SESSION_SECRET` (minted 2026-10-05, dubplate rung
> 5d's first-deploy sitting): the greenfield server's two HMAC keys, 48 random bytes each
> (`openssl rand -base64 48`). Local-only and box-only: `dubplate/scripts/deploy.sh` renders them
> into `/etc/dubplate/server.env`. Not Worker secrets, so neither joins `sync.sh`'s
> `WORKER_SECRETS`. Rotation: mint the new value, move the old one to the matching `_PREVIOUS`
> name for the overlap window (the count doubles during rotation), deploy, then drop `_PREVIOUS`.
> Rotating the session key signs every member out.

> `DUBPLATE_SMTP_PASSWORD` (Fastmail app password, SMTP scope, minted 2026-08-31) is canonical
> and rendered into dubplate-server's `/etc/dubplate/server.env`. Rotation: Fastmail
> app-passwords page + secret-receive + deploy.

> **The musicbox stack is retired (Geoff, 2026-10-05).** Navidrome, the cloudflared tunnel,
> the box's beets, and the old `dubplate` binary's units are gone from the box, and 42 names
> that only they used were deleted from the store (`secret-set.sh NAME --delete`; dotfiles
> git keeps the history): the `MUSICBOX_*` and `ND_*` aliases, `NAVIDROME_ADMIN_*`,
> `FILEBROWSER_ADMIN_PASSWORD`, the tunnel tokens, the `DUBPLATE_PING_*` and `MUSICBOX_HC_*`
> URLs, and the incumbent `DUBPLATE_*` path and Navidrome rows rendered to the retired
> `/etc/dubplate/env`. Kept: the `DUBPLATE_R2_*` credentials (the bucket still exists),
> `MUSIC_R2_RO_*`, the SMTP rows, the two HMAC keys, and `PINGS_ADMIN_TOKEN` (the pings
> Worker still runs; it holds no dubplate checks now).

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

### CAIRN_SCRATCH_CF_TOKEN
- **Grants**: Cloudflare account-owned token "cairn-scratch-b docs readers", minted by Geoff
  2026-09-23 (token id `f3598b65…`) for the cairn-cms docs-reset operator reader. One policy:
  Individual Workers, `cairn-scratch-b` only, role Metadata Read-only. Verified 2026-09-23:
  200 on the Worker's settings, 403 on another Worker's settings and on its own script content,
  401 on D1. The account-level Workers Logs telemetry query returned 403; docs reset pass 1
  Task 3 confirms whether `cairn logs` works under it. Local only; no Worker consumes it.
- **Rotate or revoke**: no TTL (the dashboard's TTL edit set a one-day window; recreated without
  one). Deleted at the close of the last docs reset drafting pass that runs `docs-and-binary`
  readers, with the scratch site's teardown, which replaces an expiry. Replace by minting a new
  account-owned token with the same single policy and `secret-receive CAIRN_SCRATCH_CF_TOKEN`.

### CAIRN_DOCS_READER_OAUTH_TOKEN
- **Grants**: a long-lived Claude Code OAuth token minted by Geoff with `claude setup-token`
  (2026-09-23) on his own plan, for the cairn-cms docs-reset reader agents only. The reader
  runner passes it into each podman container as `CLAUDE_CODE_OAUTH_TOKEN`; no credential file
  is mounted, so readers never see `~/.claude/.credentials.json` or its MCP tokens, and nothing
  refreshes. Local only; no Worker consumes it.
- **Rotate or revoke**: run `claude setup-token` again and re-store with
  `secret-receive CAIRN_DOCS_READER_OAUTH_TOKEN`; revoking it does not touch Geoff's own login.
  Revoke it if a reader transcript is ever found carrying it.

### CAIRN_CF_READ_TOKEN / CAIRN_CF_ACCOUNT_ID / CAIRN_GH_READ_TOKEN
- **Grants**: the Go `cairn` operator tool's read-only credentials (cairn-cms `tool/`), minted
  2026-09-19 as the tool's Task 10 verification set. Local only; no Worker consumes them.
- **CAIRN_CF_READ_TOKEN**: Cloudflare token "cairn tool read". Seven Read groups: Workers
  Scripts, Workers Builds Configuration, Workers Observability, Zone, Zone Settings, DNS, Email
  Sending; account `glw907`, all zones. Zone Settings was added by dashboard edit the same day
  (the HTTPS-forced check reads `always_use_https` and `security_header`; the edit persisted).
  Every endpoint the checks use verified 200; a DNS write and a settings write both verified 403.
  No expiry. Rotate at https://dash.cloudflare.com/profile/api-tokens.
- **CAIRN_CF_ACCOUNT_ID**: the account id the tool pins. A public identifier, stored so the
  tool's three names resolve from one place.
- **CAIRN_GH_READ_TOKEN**: GitHub fine-grained token "cairn-tool-read". Contents: Read and
  Metadata: Read on glw907/ecxc-ski, 907-life, aksailingclub-org, xcathletes-org, and cairn-cms.
  **Expires 2026-10-19; rotate before then** at https://github.com/settings/personal-access-tokens
  (regenerating keeps the scope; re-store with `secret-receive CAIRN_GH_READ_TOKEN`).
  Verified 200 on `commits/main` and `contents/package.json` for the four sites and
  `contents/CHANGELOG.md` on cairn-cms; a contents write verified 403.
- **Gotcha (born at the mint)**: four of the five repositories are public, and a fine-grained
  token reads a public repository with NO permissions at all. The first mint carried no
  Contents permission and still probed 200 on all four; only private `xcathletes-org` exposed
  it (404). Verify any re-mint against `xcathletes-org`.
- **Symptom of expiry**: every GitHub-backed check in `cairn health` turns unknown at once.

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

### GOOGLE_WORKSPACE_CLI_CLIENT_ID / GOOGLE_WORKSPACE_CLI_CLIENT_SECRET
- **Grants**: nothing by themselves; the Desktop OAuth client `gws-thinkpad-x1` in GCP project
  `gws-personal` (id `gws-personal-508705`, owned by geoff@907.life). `gws auth login` uses the
  pair to mint a user token stored encrypted in `~/.config/gws/`; that token carries Docs and
  Drive scopes as geoff@907.life. Consent screen is External/Testing with geoff@907.life as the
  only test user, so the refresh token expires after 7 days and `gws auth login` re-runs.
- **Used by**: `gws` (Google Workspace CLI) from Claude Code sessions, personal Google Docs
  formatting work (2026-09-14). `gws` reads both names straight from the environment.
- **Rotate at**: console.cloud.google.com → gws-personal → Google Auth Platform → Clients →
  gws-thinkpad-x1 (reset secret or create a new Desktop client), then `secret-receive` each
  value. Delete `~/.config/gws/client_secret.json` if a downloaded copy exists.

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

### PINGS_ADMIN_TOKEN
- **Grants**: the `pings` Worker's `/admin/checks` endpoints (register/deregister a
  check) — a workstation-only credential, never held by any monitored service.
- **Used by**: workstation scripts only (`~/Projects/pings/scripts/add-check`,
  `remove-check`).
- **Rotate at**: re-run `~/Projects/pings/scripts/provision.sh` (idempotent by design;
  every run rotates `ADMIN_TOKEN` into both the Worker secret and this store, invalidating
  any prior copy).

---

### PHONEBOOK_PHONE_ADMIN_KITCHEN
- **Grants**: web UI admin login on both Yealink T54Ws, kitchen (192.168.1.181) and office
  (192.168.1.118), which share one password (Geoff, 2026-10-07). Received through
  `secret-receive`; the name predates learning the office phone shares it. Used by the phonebook project's conductor to drive
  the phone's web UI (exports, provisioning URL) without a password in the transcript.
- **Scope**: local only. Phase 2 of `~/Projects/phonebook` may also serve a phone admin password
  as a Worker secret; that will be its own entry.
- **Rotation**: change it in the phone's web UI (Security), then `secret-receive` the new value.

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
