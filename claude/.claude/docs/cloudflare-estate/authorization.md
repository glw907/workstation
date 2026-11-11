# Authorization: how each thing is reached non-interactively

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
  own agent (editor on `Infrastructure`, `Projects`, `ASC`, `Test accounts`, and `Age key`) through `claude-pass`, and can
  create and edit items there; it never calls bare `pass-cli`. A value from any other vault
  arrives through `secret-receive NAME --pass REF`, which runs Geoff's own login in a
  throwaway session. See the global CLAUDE.md Secrets rule and `~/.claude/docs/bluefin-admin/secrets.md`.
