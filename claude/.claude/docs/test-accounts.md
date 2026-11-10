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
- Proton Pass: the `Test accounts` vault item "GitHub (glw907-test)" holds the
  same login and password, the TOTP in the login's 2FA slot, and two hidden fields, "Token"
  and "Recovery codes" (rebuilt 2026-11-07 from a template on stdin, per the `proton-pass`
  skill).

### Driving it

- API: `GITHUB_TEST_TOKEN` as a bearer token. `GET /user` answers `glw907-test`, and the
  `x-oauth-scopes` header lists the scopes.
- Browser: for pages no API reaches (creating or installing a GitHub App, settings), drive
  Playwright with a persistent profile at `~/.local/state/github-test/profile` (mode 0700), which <!-- host-ok -->
  keeps the session between runs. Fill the password from the store. A fresh device or sudo prompt
  asks for a TOTP code: compute it from `GITHUB_TEST_TOTP_SECRET` (RFC 6238, SHA-1, 30 s, 6
  digits). A new-device email code arrives in the test mailbox.
- Page gotchas (2026-11-03): GitHub pages hold live connections, so wait on `load` plus a
  short pause, never `networkidle`. The classic token form's expiration is a menu button, not a
  `<select>`. 2FA turns on only after step 2's recovery codes are downloaded and confirmed.
  The "Confirm access" (sudo) page needs the TOTP code typed and then a click on Verify;
  filling the field alone doesn't submit it.
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
store. Read it over JMAP: `GET https://ward.907.life/.well-known/jmap` (`907.life` answers 308 to it) with basic auth for the session,
then `Email/query` and `Email/get` against its `apiUrl`. Select a message by sender, subject, and a
received time after the request that caused it, never "the newest message". Ward logs every
inbound SMTP connection (`smtp.ehlo` in its journal), so a missing message can be traced.

Geoff's aliases are on `m.907.life`; `me.907.life` is Oliver's. Neither is a test address.

## Cloudflare

- Token: `ws-cairn-gate`, user-owned (Workers Builds accepts only user tokens), store name
  `CF_WS_CAIRN_GATE_TOKEN`. Scopes and the ownership exception: `cloudflare-estate-inventory.md`.
- Domain: `carin-test.org`, the test zone for site installs, with Email Sending on.
- Workers Builds: `glw907-test` is connected (the Cloudflare Workers and Pages GitHub App,
  All repositories). This was verified on 2026-11-03 by connecting a throwaway repo through
  `PUT /accounts/<id>/builds/repos/connections`.
- To reconnect, sign in to GitHub as `glw907-test` first. The docs' "Pages > Connect to Git"
  path no longer exists. Use Workers & Pages > Create application > Continue with GitHub,
  then add the account from the GitHub account menu.
- A half-linked install shows "Error connecting to git account" in the dashboard and code
  `8000008` from that API route. Uninstall the app at
  <https://github.com/settings/installations> as `glw907-test`, then reconnect.

## Clean room

A clean room is a home directory that holds nothing from this workstation, where a naive Claude
Code session runs as the `cleanroom` Unix user. It tests cairn's setup path and later site
rebuilds. The tool is `bin/.local/bin/cleanroom`; `cleanroom --help` and its module docstring are
its doc.

- Cloudflare token: `ws-cairn-cleanroom`, store name `CF_WS_CAIRN_CLEANROOM_TOKEN`. Scopes, owner,
  and the production exposure: `cloudflare-estate-inventory.md`. Geoff deletes it when the
  setup-tooling loop ends (end date 2026-12-09), through a step in the end packet.
- Claude credential: the subscription token from `claude setup-token`, store name
  `CLAUDE_CLEANROOM_OAUTH_TOKEN`, handed to a run as `CLAUDE_CODE_OAUTH_TOKEN`. An API key would
  have stopped the first run (the Console org held $1.13 in credits). The loop's dollar caps are
  Claude Code's client-side cost estimates, and runs draw on the subscription's usage limits.
- A run gets the Cloudflare token and the Claude token. It gets `GITHUB_TEST_TOKEN` (above) only
  for the probe, never for a naive run.

## npm

Releases publish from GitHub Actions through npm trusted publishing (OIDC), with no stored npm
token. Promotion between dist-tags runs in the same workflow once "Allow npm dist-tag" is ticked on
each package's trusted publisher. The release procedure is each repo's (cairn-cms: the
`cairn-releasing` skill).
