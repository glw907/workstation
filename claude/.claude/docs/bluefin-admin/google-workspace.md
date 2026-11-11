# Google Workspace (gws, clasp)

Moved from the global CLAUDE.md (2026-09-27). `gws` (Google Workspace CLI, Homebrew
`googleworkspace-cli`) is the path to Google Docs, Drive, and Sheets, never an MCP server.
Personal docs: OAuth as Geoff's own Google account. ASC docs only: the club service account via
`GOOGLE_APPLICATION_CREDENTIALS`, which `gws` also honors; unset it if it shadows the personal
login. Formatting edits go through `docs documents batchUpdate` after a `get` for indexes;
`--dry-run` first on any write. Patterns: the `google-docs-formatting` memory.

Apps Script goes through Google's `clasp` 3.x (`mise`, `npm:@google/clasp`, pinned to major 3 in
`mise/.config/mise/config.toml`). The procedure for Sheets and Apps Script work, trigger tests
included, is the `google-sheets` skill (Geoff, 2026-10-29).

The Cloud project is `gws-personal`, number 754967083271. Both tools sign in to it as
geoff@907.life through `gws-thinkpad-x1`, its one Desktop OAuth client. The pair lives in the age
store as `GOOGLE_WORKSPACE_CLI_CLIENT_ID` / `_CLIENT_SECRET`, and `gws` writes it to
`~/.config/gws/client_secret.json`, which `clasp login --creds` reads. Each tool holds its own
token: `gws` encrypted in `~/.config/gws/`, `clasp` in plain `~/.clasprc.json`. The consent screen <!-- host-ok -->
was published to In production, unverified, on 2026-10-29, so sign-ins should no longer lapse
after 7 days; check on 2026-11-05 that `gws` still answers without a new sign-in, and move the
screen back to Testing if it doesn't. A Claude session starts each sign-in in the background and
hands Geoff the URL with `&amp;` fixed to `&`; the consent screen is his grant.

- `gws`: `gws auth login --scopes` with `documents`, `drive`, `spreadsheets`, `script.projects`,
  and `script.processes`, each as a full `https://www.googleapis.com/auth/` URL; `-s ...,script`
  doesn't add the script scope. `script.processes` makes a trigger's run history readable.
- `clasp`: `clasp login --creds ~/.config/gws/client_secret.json --extra-scopes
  https://www.googleapis.com/auth/spreadsheets`, run from `~` because `--creds` takes a relative
  path. clasp's defaults add `cloud-platform`, `service.management`, and `logging.read`.

The Apps Script API is on in Geoff's account settings and enabled in `gws-personal`. A script runs
through `clasp run-function` only once its Cloud project is switched to 754967083271, a click in
the script editor's Project Settings that Geoff makes, once per script.
