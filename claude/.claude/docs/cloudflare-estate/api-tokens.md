# API token scheme (Geoff, 2026-10-18)

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
   to manage other tokens" (error 1001, 2026-10-18). Each arrives in a RAM-only scratch store, never the age store. Create the store empty first
   (`umask 077; mkdir -p "$XDG_RUNTIME_DIR/self-hosting"; printf '' | age -r <RECIP> -o /dev/shm/tmp-setup-$(id -u).age`,
   with `RECIP` from `secret-set.sh`), then receive with the flags, never the `VALUES=`/`LOCAL_SECRETS=`
   variables, which `secret-receive` resets so `secret-set.sh` rebuilds `~/.local/secrets` from the scratch
   store alone: `secret-receive <NAME> --values /dev/shm/tmp-setup-$(id -u).age --local
   "$XDG_RUNTIME_DIR/self-hosting/secrets-tmp-setup"`. Each and is deleted through the API when the work ends. If a fresh token
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
| `ci-phonebook` | account | Individual Workers Editor on `phonebook`; D1 Write | `glw907/phonebook`'s `CLOUDFLARE_API_TOKEN` Actions secret; origin `CF_CI_PHONEBOOK_TOKEN` | The phonebook's CI deploys |
| `ws-cairn-gate` | user (exception to rule 2: Workers Builds accepts only user tokens, "Account-scoped tokens are not supported", <https://developers.cloudflare.com/workers/ci-cd/builds/api-reference/>) | `carin-test.org` only: Zone, DNS, SSL and Certificates Write. Account: Workers Scripts, Email Sending, Workers CI, D1, Workers R2 Storage Write | `CF_WS_CAIRN_GATE_TOKEN` | cairn-cms's release gate; moves to account ownership once Builds allows it |
| `ws-cairn-cleanroom` | account, no IP filter, minted 2026-11-09, ends 2026-12-09 | Account `120c269ad6d3dfbe6d63a0bb53758ca0`: Workers Scripts, D1, Workers R2 Storage, Email Sending Edit; Account Settings Read. `carin-test.org` only: Zone Read, DNS Edit, Workers Routes Edit | `CF_WS_CAIRN_CLEANROOM_TOKEN` | The clean room's setup token and the cairn gate's sweep: the one token for the clean room's setup run, the run site's Actions deploy secret, and the sweep (`ws-cairn-gate` lacks Account Settings Read and Workers Routes). |
| `ci-cairn-build` | user (rule 2's Builds exception, as `ws-cairn-gate`) | Account `120c269ad6d3dfbe6d63a0bb53758ca0`: Workers Scripts, D1, Workers R2 Storage Edit | `CF_CI_CAIRN_BUILD_TOKEN` | **Production-critical.** The Workers Builds deploy token behind the account's shared `cairn-build` registration, used by the cairn release gate and by every cairn site's Builds deploys on the account. Never roll or delete it without re-pointing every trigger that holds the registration. |
| `ci-deploy` | account | Workers Editor across all Workers | Each repo's `CLOUDFLARE_API_TOKEN` Actions secret; origin `CF_CI_DEPLOY_TOKEN` | Every site deploy and Workers Builds |

`ws-cairn-cleanroom` can act on the production account's Workers, D1, and R2, which serve live sites
(Geoff accepted this on 2026-11-09). Its 30-day end date is the limit: Geoff deletes it when the
setup-tooling loop ends, through a step in the end packet.

`ci-deploy` is planned, not live. Until it lands, five repos' Actions secrets and the Workers
Builds build token hold `ws-admin`, and `CF_ZT_TOKEN` ("Zero Trust Edit") stays because the
aksailingclub-legacy deploy reads it. That later change swaps the five secrets and the build
token, adds Access identity-provider read to `ws-admin`, repoints `CF_ZT_TOKEN`'s readers, and
deletes it. A per-Worker Editor token can deploy over a configured custom domain or route but
cannot add or change one; that edit goes through `ws-admin`.
