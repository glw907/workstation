# Workstation Secrets Registry

Plaintext inventory — no secret values here. All values live in `secrets/values.age` (encrypted).

---

## Architecture

(Folded in from the retired `docs/secrets.md`, 2026-08-30; this file is the one
secrets document, at the path every project's doctrine already references.)

```
Proton Pass Workstation vault (age key only)
    |
    v  ws-pass-key
    |
    v
secrets/values.age (encrypted, safe to commit)
    |
    v  scripts/secrets/sync.sh
    |
    +---> ~/.local/secrets (local env vars, sourced by .bashrc)
    +---> Cloudflare Workers (per-worker secrets via wrangler)
```

- **Proton Pass** holds the age encryption key, in the `Workstation` vault (one item); a paper copy exists too
- **claude-pass** is Claude's own route into Proton Pass (Geoff, 2026-10-20): the `<host>-claude` agent, editor on `Servers emergency` and `Workstation`, creates and edits items there. Because it is editor on `Workstation`, the vault that holds the age-key item, Claude can read or change that item too, per Geoff's ruling. It plays no part in the age-key path above
- **values.age** is the encrypted bundle committed to this repo and holds all secret values
- **sync.sh** decrypts with the age key from `ws-pass-key` (the host's Proton agent token; a host with no token fails and is told to run `ws-pass-key --store`) and pushes to targets
- **~/.local/secrets** is chmod 600, gitignored, sourced by `.bashrc`
- Decryption happens in `/dev/shm` (tmpfs); plaintext never touches disk

**Sync-time** (occasional, needs the agent token): `sync.sh --local` after cloning or
when secrets change. **Runtime** (day to day, no key needed): secrets are env
vars already sourced by `.bashrc`; read `$FASTMAIL_API_TOKEN` etc. directly and
never fetch what the environment already carries.

**Sudo helper**: `claude-sudo-setup` asks Geoff for the sudo password in a
hidden-entry dialog and caches it in tmpfs (`/dev/shm/claude-sudo-$UID`, umask 077); `claude-askpass`
supplies it to `sudo -A`; `claude-sudo-clear` shreds it when a Claude session
exits, and reboot clears it regardless. The password persists nowhere on disk.

**What goes where**: sensitive tokens in `~/.local/secrets` via sync.sh;
non-sensitive config (paths, emails, model names) as plain `.bashrc` exports;
worker secrets pushed by sync.sh via `wrangler secret put`; the sudo password
nowhere but the tmpfs cache above (`claude-sudo-setup` takes it from a dialog).

---

## How to Decrypt

1. **Fill the key cache** (once per session; no prompt when the host's agent token is stored):
   ```bash
   ws-pass-key
   ```

2. **Decrypt interactively** (for inspection):
   ```bash
   age --decrypt \
     -i /dev/shm/.age-key-$UID \
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

**Authenticate once per session.** The host's Proton agent token sits in GNOME Keyring, so
`secret-set.sh` fetches the age key through `ws-pass-key` on first use, caches it in tmpfs
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
| CF_ZT_TOKEN         | ✓     | —        | —    | —        | —          |
| ACCESS_GITHUB_CLIENT_ID / _SECRET | ✓ | — | — | — | — |
| CF_ACCESS_CLIENT_SECRET | ✓ | —        | —    | —        | —          |
| ANTHROPIC_API_KEY   | ✓     | —        | ✓    | ✓        | —          |
| CMS_BOT_PAT         | ✓     | —        | —    | —        | —          |
| RESEND_API_KEY      | ✓     | ✓        | ✓    | —        | —          |
| CONTACT_EMAIL       | ✓     | —        | —    | —        | ✓          |
| DAISYUI_BLUEPRINT_LICENSE | ✓ | —      | —    | —        | —          |
| DAISYUI_BLUEPRINT_EMAIL | ✓  | —        | —    | —        | —          |
| HCLOUD_TOKEN_SERVERS | ✓    | —        | —    | —        | —          |
| CF_WS_SERVERS_TOKEN | ✓     | —        | —    | —        | —          |
| CF_WS_R2_ARCHIVE_RW_TOKEN / _KEY_ID / _SECRET | ✓ | — | — | — | — |
| CF_WS_R2_BACKUPS_RO_TOKEN / _KEY_ID / _SECRET | ✓ | — | — | — | — |
| CF_ORPHEUS_R2_BACKUP_RW_TOKEN / _KEY_ID / _SECRET | ✓ | — | — | — | — |
| CF_WARD_R2_BACKUP_RW_TOKEN / _KEY_ID / _SECRET | ✓ | — | — | — | — |
| MONITOR_READ_TOKEN | ✓ | — | — | — | — |
| HEARTBEAT_TOKEN_ORPHEUS / HEARTBEAT_TOKEN_WARD | ✓ | — | — | — | — |
| IMMICH_DB_PASSWORD | ✓ | — | — | — | — |
| RESTIC_PASSWORD_ORPHEUS | ✓ | — | — | — | — |
| TUNNEL_TOKEN_ORPHEUS | ✓ | — | — | — | — |
| RESTIC_PASSWORD_WARD | ✓ | — | — | — | — |
| TUNNEL_TOKEN_WARD | ✓ | — | — | — | — |
| STALWART_ADMIN_PASSWORD | ✓ | — | — | — | — |
| STALWART_PASSWORD_GEOFF / _OPERATOR2 / _TEST / _TEST2 | ✓ | — | — | — | — |
| PIKAPODS_SFTP_HOST / _USER / _PASSWORD | ✓ | — | — | — | — |
| FASTMAIL_API_TOKEN  | ✓     | —        | —    | —        | —          |
| FASTMAIL_DAV_PASSWORD | ✓   | —        | —    | —        | —          |
| FASTMAIL_OPERATOR2_PASSWORD | ✓ | — | — | — | — |
| FASTMAIL_OPERATOR2_API_TOKEN | ✓ | — | — | — | — |
| SPAMHAUS_DQS_KEY | ✓ | — | — | — | — |
| TEST_YAHOO_ADDRESS | ✓ | — | — | — | — |
| TEST_YAHOO_PASSWORD | ✓ | — | — | — | — |
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
| DRAFTER_API_KEY   | ✓       | —      | —    | —        | —          |
| DUBPLATE_MAGIC_LINK_SECRET | ✓ | —   | —    | —        | —          |
| DUBPLATE_SESSION_SECRET | ✓ | —      | —    | —        | —          |
| PHONEBOOK_PHONE_ADMIN_KITCHEN | ✓ | — | — | — | — |
| VOIPMS_API_USERNAME | ✓ | — | — | — | — |
| VOIPMS_API_PASSWORD | ✓ | — | — | — | — |
| IMMICH_PIKAPODS_API_KEY | ✓ | — | — | — | — |
| TPLINK_ROUTER_PASSWORD | ✓ | — | — | — | — |

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
> `MUSIC_R2_RO_*`, the SMTP rows, and the two HMAC keys. The pings Worker and its admin token
> were retired later, in the 2026-10-14 repo organization pass.

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

**Not in values.age:** the sudo password. `claude-sudo-setup` takes it from a dialog into the
tmpfs cache; no password manager holds it for scripts.

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
- **Issuer-side token name**: `ws-admin`, renamed from "Cloudflare Admin 2026-07" on
  2026-10-18 under the API token scheme in `~/.claude/docs/cloudflare-estate-inventory.md`
  (My Profile > API Tokens; user-owned). The scheme replaces its CI and Workers Builds copies
  with `ci-deploy`, which is still planned. **Rotate by 2027-10-18.** Permission groups added 2026-08-30 for the pings Worker build-out
  (Task P2b): Workers KV Storage: Edit, Email Routing Addresses: Edit — plus Cloudflare
  Tunnel: Edit (closed the same day, the musicbox `CF_ZT_TOKEN` blocker above). The token
  cannot edit its own permissions (confirmed: `GET /user/tokens/{id}` 403s even for this
  token against itself), so any future scope gap needs the same dashboard-edit path.

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
- **CAIRN_CF_READ_TOKEN**: Cloudflare token `ws-cairn-read` ("cairn tool read" until
  2026-10-18; user-owned, moves to account ownership at its next rotation). Seven Read groups: Workers
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

### HCLOUD_TOKEN_SERVERS
- **Grants**: Hetzner Cloud API read/write, project `servers` only (self-hosting initiative)
- **Token name at issuer**: servers-claude
- **Used by**: the servers repo's `infra/provision.sh` and `scripts/dry-run.sh`, which pass it to
  `hcloud` as `HCLOUD_TOKEN` through the environment. No `hcloud context` exists, because
  `hcloud context create` writes the token to `~/.config/hcloud/cli.toml`.
- **Rotate at**: console.hetzner.cloud > project servers > Security > API tokens
- **Received 2026-10-17** via `secret-receive` (desktop dialog, value never in transcript);
  verified with an empty `hcloud server list` and an SSH key created then deleted.

### CF_WS_SERVERS_TOKEN
- **Grants**: Cloudflare account-owned token `ws-servers` (id `6a5623b2...`). Zone 907.life
  only: DNS Write, Dynamic URL Redirects Write (Single Redirect), Workers Routes Write, Zone
  Read. Account: Workers Admin (the scripts create and delete Workers), D1 Write, Email Sending
  Write, Access: Apps and Policies Write, Cloudflare Tunnel Write, Access: Audit Logs Read.
- **Used by**: the servers repo's `cloudflare/dns.sh`, `access.sh`, `deploy.sh`, and
  `scripts/dry-run.sh`.
- **Minted 2026-10-18** through the API under the API token scheme
  (`~/.claude/docs/cloudflare-estate-inventory.md`); the value went from the response into the
  store unseen. Smoke-tested: 907.life DNS read 200, ecxc.ski DNS read 403, R2 403.
- **Rotate**: the scheme's temporary token procedure (rule 6), then the servers runbook's
  "Rotating a Cloudflare token".

### MONITOR_READ_TOKEN
- **Grants**: read access to the monitor Worker's `/alerts` endpoint: the open conditions, their
  severity, and the time of the last completed check. It writes nothing and posts no heartbeat.
- **Used by**: the servers repo's monitor Worker (a Worker secret, put by `cloudflare/deploy.sh
  monitor`) and the workstation's `monitor-subscribe` user service, which reads it from
  `~/.local/secrets`.
- **Generated** on the workstation (32 random bytes, hex-encoded), distinct from both heartbeat
  tokens; the value never appears in a transcript.
- **Rotate**: generate a new value, store it, redeploy the monitor, and restart
  `monitor-subscribe` on each workstation.

### IMMICH_DB_PASSWORD
- **Grants**: the password of orpheus's Immich Postgres role. Immich cannot start without it, and the restored database expects the role to exist with it.
- **Used by**: the servers repo's `roles/immich` compose file, rendered to `/etc/immich/immich.env` on orpheus only.
- **Generated 2026-10-19** on pavilion (40 random alphanumeric characters), in Pass 2 (M3).
- **Rotate**: store a new value, re-render orpheus's secrets, and change the role's password inside Postgres.

### TUNNEL_TOKEN_ORPHEUS
- **Grants**: the right to run the `servers-orpheus` Cloudflare Tunnel connector, which carries orpheus's Access browser terminal at `ssh-orpheus.907.life`. Anyone holding it can attach a connector to that tunnel. It replaced the media tunnel's token, which the rename pass retired.
- **Used by**: the servers repo's `roles/cloudflared`, rendered to `/etc/cloudflared/token` on orpheus only.
- **Generated 2026-10-20** by `cloudflare/access.sh --token orpheus` (the tunnel is created by `access.sh --apply`) and stored with `secret-set.sh`, in the rename pass (R6).
- **Rotate**: rotate the tunnel's token in Cloudflare (or recreate the tunnel with `access.sh`), store the new value, and re-render orpheus's secrets.

### RESTIC_PASSWORD_ORPHEUS
- **Grants**: the right to open the orpheus restic repository in `servers-backup-orpheus`. Losing it makes every orpheus backup unreadable. It replaced the media server's restic password, which the rename pass retired.
- **Used by**: the servers repo's `roles/backup` (rendered to `/etc/servers/restic-password` on orpheus) and the restore drill.
- **Generated 2026-10-20** on pavilion (32 random bytes, base64url), in the rename pass (R3), stored and pushed before `restic init`. The bucket's lock rules land only after this commit is on `origin/main`.
- **Rotate**: changing a restic password removes the old key file, which the `keys/` lock rule refuses, so a rotation needs Geoff to lift the rule.

### RESTIC_PASSWORD_WARD
- **Grants**: the right to open the ward restic repository in `servers-backup-ward`. Losing it makes every ward backup unreadable, and a regenerated value orphans the repository.
- **Used by**: the servers repo's `roles/backup` (rendered to `/etc/servers/restic-password` on ward) and the restore drill.
- **Generated 2026-10-21** on pavilion (40 random alphanumerics), in the mail server pass (L3), stored and pushed before `restic init`. The bucket's lock rules land only after this commit is on `origin/main`.
- **Rotate**: changing a restic password removes the old key file, which the `keys/` lock rule refuses, so a rotation needs Geoff to lift the rule.

### TUNNEL_TOKEN_WARD
- **Grants**: the right to run the `servers-ward` Cloudflare Tunnel connector, which carries ward's Access browser terminal and the Stalwart admin page. Anyone holding it can attach a connector to that tunnel.
- **Used by**: the servers repo's `roles/cloudflared`, rendered to `/etc/cloudflared/token` on ward only.
- **Generated 2026-10-21** by `cloudflare/access.sh --token ward` (the tunnel is created by `access.sh --apply`) and stored with `secret-set.sh`, in the mail server pass (L3).
- **Rotate**: rotate the tunnel's token in Cloudflare (or recreate the tunnel with `access.sh`), store the new value, and re-render ward's secrets.

### STALWART_ADMIN_PASSWORD
- **Grants**: the password of Stalwart's administrator account on ward. It manages every account, domain, and setting.
- **Used by**: the servers repo's `roles/stalwart` (the plan application and the bootstrap) and `roles/health` (queue and mailbox counts), rendered to root-only files on ward.
- **Generated 2026-10-21** on pavilion (40 random alphanumerics), in the mail server pass (L3).
- **Rotate**: store a new value and apply the Stalwart role again, which sets the account's password from the store.

### STALWART_PASSWORD_GEOFF / _OPERATOR2 / _TEST / _TEST2
- **Grants**: the passwords of four Stalwart accounts on ward: Geoff's and the second operator's mailboxes, and the two rehearsal test accounts. The mailbox passwords let their holders read that mail.
- **Used by**: the servers repo's `roles/stalwart` (the plan sets each account's password from the store) and the rehearsal scripts (`vandelay-run.sh`, L6's sends). The second operator's also goes into `Servers emergency` for him.
- **Generated 2026-10-21** on pavilion (40 random alphanumerics), in the mail server pass (L3). Each is shared with its owner in Pass 6; until then only the rehearsal uses them.
- **Rotate**: store a new value and apply the Stalwart role again.

### HEARTBEAT_TOKEN_ORPHEUS / HEARTBEAT_TOKEN_WARD
- **Grants**: the right to post one server's health heartbeat to the monitor Worker. Each token writes only its own server's row. They replaced the media and mail keys, which the rename pass retired.
- **Used by**: the monitor Worker (Worker secrets) and, rendered by the servers repo's `secrets/render.sh` as `HEARTBEAT_TOKEN`, that server's health timer only. Ward's health timer reads it from L3 of the mail server pass.
- **Generated 2026-10-20** on pavilion (32 random bytes, base64url), in the rename pass (R3).
- **Rotate**: store a new value, redeploy the monitor, and re-render the server's secrets.

### CF_ORPHEUS_R2_BACKUP_RW_* / CF_WARD_R2_BACKUP_RW_*
- **Grants**: two account-owned R2 tokens, `orpheus-r2-backup-rw` and `ward-r2-backup-rw`, each stored as `_TOKEN` plus its S3 pair (`_KEY_ID` is the token id, `_SECRET` the SHA-256 of the value). Each reads and writes its own backup bucket, `servers-backup-orpheus` or `servers-backup-ward`, and nothing else. They replace the media and mail tokens.
- **Used by**: orpheus's restic (ward's waits for Pass 5) and `scripts/dry-run.sh`. Readers per name: the servers repo's `secrets/registry.md`.
- **Minted 2026-10-20** in the rename pass (R3) through a temporary token-management token, with the old tokens' policies and the bucket swapped. `ws-r2-backups-ro` was re-scoped in place to add both new buckets; its value did not change.
- **Rotate**: as for `CF_WS_SERVERS_TOKEN`; a server's token also rotates when that server is rebuilt or compromised.

### CF_WS_R2_ARCHIVE_RW_* / CF_WS_R2_BACKUPS_RO_*
- **Grants**: two account-owned R2 tokens, each stored as `_TOKEN` plus its S3 pair
  (`_KEY_ID` is the token id, `_SECRET` the SHA-256 of the value, per
  https://developers.cloudflare.com/r2/api/tokens/). `ws-r2-archive-rw` (`9ab3b968...`): object
  read and write on `servers-archive`. `ws-r2-backups-ro` (`d76af5a1...`): object read on
  `servers-backup-orpheus` and `servers-backup-ward` (the rename pass re-scoped it from the two old buckets).
- **Used by**: workstation archive copies; restores, drills, and the restore kit. Readers per name: the servers repo's
  `secrets/registry.md`.
- **Minted 2026-10-18** as above. Smoke-tested over S3: each lists its own bucket (200) and is
  refused another (403); the read-only token lists both backup buckets.
- **Rotate**: as for `CF_WS_SERVERS_TOKEN`; a server's token also rotates when that server is
  rebuilt or compromised.

### PIKAPODS_SFTP_HOST / PIKAPODS_SFTP_USER / PIKAPODS_SFTP_PASSWORD
- **Grants**: SFTP into the PikaPods Immich pod's storage (`photos/` holds Immich's six data
  directories, `config/` and `libraries/` the rest). The host and user are private, not secret:
  they live here and in the servers repo's privacy patterns, never in a public file.
- **Used by**: the self-hosting Immich cutover (Pass 3), which copies the six directories, and
  the servers repo's `scripts/dry-run.sh`. Log in with `sshpass -e` so the password stays off
  the command line.
- **Received 2026-10-18**: the password through a desktop dialog; verified with an SFTP listing.
- **Rotate at**: PikaPods > the pod > Settings > SFTP. Dies with the pod when PikaPods is retired.

### ACCESS_GITHUB_CLIENT_ID / ACCESS_GITHUB_CLIENT_SECRET
- **Issuer**: the GitHub OAuth app "Wright Family Access" on Geoff's GitHub account, callback
  `https://907wrights.cloudflareaccess.com/cdn-cgi/access/callback`.
- **Grants**: signing in to Cloudflare Access as a GitHub user. The secret lets Access exchange a
  sign-in code for the user's identity; it grants nothing in GitHub itself.
- **Used by**: the Access GitHub identity provider (id `916192d5-ba81-48ae-be48-002abf1be8ef`),
  set with `CF_ZT_TOKEN` on 2026-10-19. No script reads them at run time; they are kept for a
  rotation or a rebuild of the provider.
- **Received** through `secret-receive` (the Client ID re-stored with `secret-set.sh --value`; it
  is not secret).
- **Rotate**: generate a new client secret on the OAuth app, store it, `PUT` the provider's config
  with `CF_ZT_TOKEN`, run the provider's Test in Zero Trust, then delete the old secret on GitHub.

### CF_ZT_TOKEN
- **Issuer-side token name**: "Zero Trust Edit" (user-owned). Also the aksailingclub-legacy
  Actions secret. The API token scheme retires it once `ci-deploy` lands and `ws-admin` gains
  Access identity-provider read.
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
- **Used by**: aerc, Claude Code JMAP scripting (via env var), poplar
  corpus harvest
- **Rotate at**: Fastmail > Settings > Privacy & Security > App Passwords
- **History**: 2026-07-19 the stored value had gone stale (JMAP 401); re-anchored from the
  1Password Fastmail item's `api access` field via secret-set.sh (1Password has since left
  the workstations). If it goes stale again, re-anchor after any Fastmail-side rotation.

### FASTMAIL_DAV_PASSWORD
- **Grants**: Fastmail app password with mail, calendar, and contacts access (IMAP, SMTP,
  CalDAV, CardDAV)
- **Used by**: vdirsyncer's CardDAV sync, through `fastmail-dav-password`
- **Rotate at**: Fastmail > Settings > Privacy & Security > App Passwords
- **History**: minted 2026-10-13 and received on pavilion, replacing the loose
  `~/.config/fastmail/fastmail-dav-token.age` the helper read before. Revoke the old app
  password and delete that loose file once thinkpad-x1 pulls this and runs
  `sync.sh --local`.

### FASTMAIL_OPERATOR2_PASSWORD
- **Grants**: the second operator's Fastmail app password "Migration", with IMAP and DAV
  access to his mailbox, contacts, and calendars
- **Used by**: the self-hosting mail migration (Pass 5's rehearsal import, Pass 6's sweeps)
- **Rotate at**: created by Geoff as the account's admin, in the member's own Fastmail
  settings (Privacy & Security). Revoke it once the Fastmail account closes after cutover
- **History**: received on pavilion 2026-10-20; IMAP, CalDAV, and CardDAV logins pass

### FASTMAIL_OPERATOR2_API_TOKEN
- **Grants**: the second operator's Fastmail API token "Migration": JMAP read and write on
  his mail, contacts, and masked email, plus sending (`submission`); not read-only
- **Used by**: the self-hosting mail migration (Pass 5's size and mask counts) and, later,
  his masked-address work
- **Rotate at**: created by Geoff as the account's admin, in the member's own Fastmail
  settings (Privacy & Security). Revoke it once the Fastmail account closes after cutover
- **History**: received on pavilion 2026-10-20; its JMAP session is his account

### SPAMHAUS_DQS_KEY
- **Grants**: queries to Spamhaus's free Data Query Service (the `zen` and `dbl` blocklists
  through `<key>.<zone>.dq.spamhaus.net`), for non-commercial use, renewing yearly
- **Used by**: the self-hosting mail server ward (Stalwart's blocklist checks, a `File`
  secret on the host) and the servers dry run's `spamhaus-dqs` row
- **Rotate at**: the Spamhaus Customer Portal (login in Geoff's Proton Pass), Products >
  Blocklists via DNS Query > Generate a new Query key; then `secret-receive SPAMHAUS_DQS_KEY`.
  A new key takes several minutes to answer
- **History**: received on pavilion 2026-10-21 in the Pass 5 sitting, rotated twice the same
  day after a copy reached chat; the dry run's test point answers `127.0.0.4`

### TEST_YAHOO_ADDRESS
- **Grants**: nothing on its own; the address of the throwaway Yahoo Mail test account
- **Used by**: the self-hosting Pass 5 rehearsal's delivery tests, which send to it and read
  it through Yahoo webmail in Claude's Chromium profile
- **Rotate at**: not rotated; the account's login is in the Workstation vault
- **History**: stored from the Workstation vault 2026-10-21; it replaces the plan's Gmail test
  account on Geoff's ruling (Google's sign-up needs a smartphone)

### TEST_YAHOO_PASSWORD
- **Grants**: the Yahoo test account's sign-in password; two-step verification texts Geoff's
  phone, so a new browser sign-in needs him
- **Used by**: the Pass 5 rehearsal's webmail sign-in in Claude's Chromium profile. Yahoo
  withholds app passwords from new accounts, so no IMAP or SMTP use
- **Rotate at**: Yahoo > Account security > Change password, then the Workstation vault item
  `login.yahoo.com`, then store it again from the vault
- **History**: stored 2026-10-21. A fragment of the first password reached that session's
  transcript, because `~/.local/secrets` is written unquoted and the value held shell
  separators. Geoff changed it the same day to letters and digits only, which keep the file
  loadable until the writer quotes values

### DRAFTER_API_KEY
- **Grants**: Anthropic API access in the Console workspace created for drafter, under that
  workspace's spend limit
- **Used by**: `drafter`, which reads it through its `key_env` setting (default
  `DRAFTER_API_KEY`) for batched drafting and review of docs pages
- **Rotate at**: the Anthropic Console, in the drafter workspace's API keys; then
  `secret-receive DRAFTER_API_KEY`
- **History**: received on pavilion 2026-10-13 with `secret-receive`, per the drafter
  completion design's setup step; this entry and the store commit landed 2026-10-14.
  thinkpad-x1 picks it up on its next pull and `sync.sh --local`.

### IMMICH_PIKAPODS_API_KEY
- **Grants**: an Immich API key on the PikaPods instance at photos.907.life, minted from
  Geoff's admin account with full permissions
- **Used by**: the hetzner-mail-host initiative, to read library statistics and later to
  drive the Immich migration off PikaPods
- **Rotate at**: photos.907.life, Account Settings > API Keys; then
  `secret-receive IMMICH_PIKAPODS_API_KEY`
- **History**: received on pavilion 2026-10-17 with `secret-receive`. Revoke it in Immich and
  drop it from the store once the migration retires the PikaPods instance.

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
- **Grants**: R2 API token `ws-r2-music-ro` (id `1de499ec...`; "Claude Code ThinkPad X1"
  until 2026-10-18): Object Read only, scoped to bucket `music-library` only. Deliberately
  read-only: the workstation mirror pull (`music-pull`, Task 8) can never delete or overwrite
  the bucket, which has been the library's only copy since musicbox was deleted on 2026-10-17.
- **Used by**: the workstation's `music-pull` script (`rclone copy` of `library/` to
  `~/Music`).
- **Rotate at**: My Profile > API Tokens (user-owned today; its replacement is account-owned
  under the API token scheme in `~/.claude/docs/cloudflare-estate-inventory.md`). Mint it scoped
  identically, then `secret-set.sh` both halves.

---

### PHONEBOOK_PHONE_ADMIN_KITCHEN
- **Grants**: web UI admin login on both Yealink T54Ws, kitchen (192.168.1.181) and office
  (192.168.1.118), which share one password (Geoff, 2026-10-07). Received through
  `secret-receive`; the name predates learning the office phone shares it. Used by the phonebook project's conductor to drive
  the phone's web UI (exports, provisioning URL) without a password in the transcript.
- **Scope**: local only. Phase 2 of `~/Projects/phonebook` may also serve a phone admin password
  as a Worker secret; that will be its own entry.
- **Rotation**: change it in the phone's web UI (Security), then `secret-receive` the new value.

### VOIPMS_API_USERNAME / VOIPMS_API_PASSWORD
- **Grants**: the voip.ms REST/JSON API (`https://voip.ms/api/v1/rest.php`) for Geoff's account,
  set up 2026-10-07 for `~/Projects/phonebook` phase 2 (sub-accounts). The username is the
  account login email. The password is the typed **API Password** on the portal's SOAP and
  REST/JSON API page, not the login password and not the page's **Bearer Token**; `rest.php`
  ignores a bearer header (`missing_credentials`). Verified with `getIP`, 2026-10-07.
- **Constraints**: the API answers only whitelisted IPs (the home IP, 206.162.90.105 on
  2026-10-07; a DHCP change breaks it). Credentials travel as GET query parameters; pass them to
  curl through `-K -` on stdin. `getSubAccounts` returns SIP passwords, so never print its output.
- **Rotation**: type a new API Password, click Save API Password, then `secret-receive
  VOIPMS_API_PASSWORD`.

### TPLINK_ROUTER_PASSWORD
- **Grants**: the local admin password of the house router (TP-Link Archer C4000 v3.0 at
  192.168.1.1). **Pending (BACKLOG #26)**: the value stored 2026-10-20 is the TP-Link ID
  (cloud) password for geoff-login@907.life, received by mistake; the router's local password
  is unknown and a bound router can't change it without a factory reset. Replace the value
  when the local password exists; nothing consumes the stored one. Read by the
  `tplinkrouterc6u` client for LAN-side router management: status, clients, band toggles, DHCP
  reservations, reboot. Local only; no Worker consumes it. The router's WAN "Remote Management"
  stays off; this credential never leaves the LAN.
- **Rotate**: change it on the router's admin page, then `secret-receive TPLINK_ROUTER_PASSWORD`.
  A scripted login shares the router's single admin session, so a run logs Geoff's browser out.


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
- **Private key storage**: Proton Pass > `Workstation` vault > "Workstation age encryption key"
  (the only item in that vault), plus a paper copy checked 2026-10-19 against the recipient
  with `age-keygen -y`. Each host reads it with its own agent token (`pavilion-scripts`, later
  `thinkpad-scripts`; viewer role on that vault only). The ASC age key stays in its own key
  file; Geoff restores it by hand from Proton Pass when that file is missing.
- **No persistent copy of THIS store's key on disk** — it is fetched through `ws-pass-key` at
  decrypt time and cached only in tmpfs. (The separate ASC project key at
  `~/.config/age/asc-key.txt` is a different key for a different store and does live on
  disk, mode 600, by that project's own design.)
