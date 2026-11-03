# Test accounts

The workstation's standing accounts for automated testing. Geoff set the goal on 2026-11-03:
testing and releases, npm included, run as automated as possible. Any project's session may use
these accounts for tests, never for real work. Each section names where its credentials live,
by name and never by value.

## GitHub: `glw907-test`

A machine account, created 2026-11-03. GitHub's terms allow one free machine account per person
besides the personal account ("You may maintain no more than one free machine account in addition
to your free Personal Account", <https://docs.github.com/en/site-policy/github-terms/github-terms-of-service>),
so this is the only one, shared by every project. Test repositories, GitHub Apps, and App
installations live here, never on `glw907`.

- Email: `cairn-gate@probe.907.life`, the test mailbox below, so a session reads GitHub's
  codes and notices itself.
- 2FA: an authenticator-app (TOTP) secret; recovery codes regenerated 2026-11-03.
- Token: a classic personal access token, scopes `repo` and `delete_repo`, no expiry. Mint a
  separate token for a wider scope rather than widening this one.
- Age store (`~/.local/secrets`): `GITHUB_TEST_LOGIN`, `GITHUB_TEST_PASSWORD`,
  `GITHUB_TEST_TOTP_SECRET`, `GITHUB_TEST_TOKEN`, `GITHUB_TEST_RECOVERY_CODES` (space-separated).
- Proton Pass: the Workstation vault item "GitHub test account (glw907-test)" holds the same
  login, password, TOTP, and, in its note, the token and recovery codes.

### Driving it

- API: `GITHUB_TEST_TOKEN` as a bearer token. `GET /user` answers `glw907-test`, and the
  `x-oauth-scopes` header lists the scopes.
- Browser: for pages no API reaches (creating or installing a GitHub App, settings), drive
  Playwright with a persistent profile at `~/.local/state/github-test/profile` (mode 0700), which
  keeps the session between runs. Fill the password from the store. A fresh device or sudo prompt
  asks for a TOTP code: compute it from `GITHUB_TEST_TOTP_SECRET` (RFC 6238, SHA-1, 30 s, 6
  digits). A new-device email code arrives in the test mailbox.
- Page gotchas (2026-11-03): GitHub pages hold live connections, so wait on `load` plus a
  short pause, never `networkidle`. The classic token form's expiration is a menu button, not a
  `<select>`. 2FA turns on only after step 2's recovery codes are downloaded and confirmed.
- Never screenshot a page that shows a secret (a setup key, recovery codes, a new token): a
  screenshot read into a session puts the value in its transcript. Extract the value from the
  DOM and store it unseen.
- The maintained driver is cairn-cms's release gate harness (`scripts/gate/browser.mjs`, from the
  setup-fix pass).

### Rotate

Password: change it on GitHub, then `secret-set.sh GITHUB_TEST_PASSWORD --stdin` and the vault
item. Token: generate a new classic token with the same scopes, store it, delete the old one in
Settings > Developer settings. Lost TOTP: sign in with a recovery code and set up 2FA again.

## Mail: `cairn-gate@probe.907.life`

A ward mailbox in the `probe.907.life` test domain. Its mail never touches a real 907.life
mailbox (servers repo, `docs/addresses.md`). Password `STALWART_PASSWORD_CAIRN_GATE` in the age
store. Read it over JMAP: `GET https://907.life/.well-known/jmap` with basic auth for the session,
then `Email/query` and `Email/get` against its `apiUrl`. Select a message by sender, subject, and a
received time after the request that caused it, never "the newest message". Ward logs every
inbound SMTP connection (`smtp.ehlo` in its journal), so a missing message can be traced.

Geoff's aliases are on `m.907.life`; `me.907.life` is Oliver's. Neither is a test address.

## Cloudflare

- Token: `ws-cairn-gate`, user-owned (Workers Builds accepts only user tokens), store name
  `CF_WS_CAIRN_GATE_TOKEN`. Scopes and the ownership exception: `cloudflare-estate-inventory.md`.
- Domain: `carin-test.org`, the test zone for site installs, with Email Sending on.

## npm

Releases publish from GitHub Actions through npm trusted publishing (OIDC), with no stored npm
token. Promotion between dist-tags runs in the same workflow once "Allow npm dist-tag" is ticked on
each package's trusted publisher. The release procedure is each repo's (cairn-cms: the
`cairn-releasing` skill).
