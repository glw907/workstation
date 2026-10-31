# Apps Script through clasp

`clasp` 3.4.1 (github.com/google/clasp). Run it from the script's directory; it reads
`.clasp.json` there.

## Commands

| Need | Command |
| --- | --- |
| Who is signed in | `clasp show-authorized-user` |
| Local and remote files differ? | `clasp show-file-status` |
| Upload the directory | `clasp push` (replaces every remote file; a file missing locally is deleted remotely). After a manifest change it asks before overwriting, and with no terminal to answer it prints "Skipping push." and exits 0; use `clasp push --force` then |
| Download | `clasp pull` (a `.gs` file comes back as `.js`, so diff by content) |
| Start from an existing script | `clasp clone-script <script id>` |
| New bound script | `clasp create-script --parentId <spreadsheet id>` (no `--type`: `--type sheets` makes a new sheet and drops `--parentId`, per clasp 3.4.1's `create-script.js`) |
| Make it API executable | `clasp create-deployment` (after the manifest declares `executionApi`) |
| List deployments | `clasp list-deployments` |
| Run a function | `clasp run-function <name>`, with `--params '[...]'` for JSON arguments |
| Logs | `clasp tail-logs` (Cloud Logging; write with `console.log` and `console.error`) |
| Link logs to the project | `clasp setup-logs`, once per script |

`clasp delete-script` is denied in `settings.json`. Deleting a script is Geoff's.

## The manifest

```json
{
  "timeZone": "America/Anchorage",
  "runtimeVersion": "V8",
  "exceptionLogging": "STACKDRIVER",
  "executionApi": { "access": "MYSELF" },
  "oauthScopes": ["https://www.googleapis.com/auth/spreadsheets"]
}
```

Keep the script's existing `timeZone` and `dependencies`. List every scope the code uses in
`oauthScopes`: the run token "must cover all the scopes used by the script"
(developers.google.com/apps-script/api/how-tos/execute), and clasp's sign-in carries
`spreadsheets`. A scope outside that sign-in needs a new `clasp login` with `--extra-scopes`,
which is Geoff's grant.

## Why a run fails

- `Unable to run script function. Please make sure you have permission`: the script is still on
  its default Cloud project. Geoff switches it (SKILL.md, step 3).
- `Script function not found. Please make sure script is deployed as API executable.`: the name
  ends in `_` (private, not callable through the API), the code wasn't pushed, or no API-executable
  deployment exists.
- `The caller does not have permission`: the token lacks a scope the script declares, or Geoff
  isn't the owner.
- `run-function` runs in development mode by default, so it runs the last pushed code, not the
  deployment's version; the deployment only has to exist.
- A trigger that "does nothing": read `gws script processes list` for a `FAILED` run, then
  `clasp tail-logs`. A `try`/`catch` that only shows a toast hides the error from both, so a
  handler logs with `console.error` too.
