# Apps Script through clasp

`clasp` 3.4.1 (github.com/google/clasp). Run it from the script's directory; it reads
`.clasp.json` there.

## Commands

| Need | Command |
| --- | --- |
| Who is signed in | `clasp show-authorized-user` |
| Local and remote files differ? | `clasp show-file-status` |
| Upload the directory | `clasp push` (replaces every remote file; a file missing locally is deleted remotely) |
| Download | `clasp pull` |
| Start from an existing script | `clasp clone-script <script id>` |
| New bound script | `clasp create-script --type sheets --parentId <spreadsheet id>` |
| Make it API executable | `clasp create-deployment` (after the manifest declares `executionApi`) |
| List deployments | `clasp list-deployments` |
| Run a function | `clasp run-function <name>`, with `--params '[...]'` for JSON arguments |
| Logs | `clasp tail-logs` (Cloud Logging, so `console.log`, never `Logger.log`) |
| Link logs to the project | `clasp setup-logs`, once per script |

`clasp delete-script` is denied in `settings.json`. Deleting a script is Geoff's.

## The manifest

```json
{
  "timeZone": "America/Anchorage",
  "runtimeVersion": "V8",
  "exceptionLogging": "STACKDRIVER",
  "executionApi": { "access": "MYSELF" },
  "oauthScopes": ["https://www.googleapis.com/auth/spreadsheets.currentonly"]
}
```

Keep the script's existing `timeZone` and `dependencies`. List every scope the code uses in
`oauthScopes`: the run token "must cover all the scopes used by the script"
(developers.google.com/apps-script/api/how-tos/execute), and clasp's sign-in carries
`spreadsheets`. A scope outside that sign-in needs a new `clasp login` with `--extra-scopes`,
which is Geoff's grant.

## Why a run fails

- A permission error naming a Cloud project: the script is still on its default project. Geoff
  switches it (SKILL.md, step 3).
- `Script function not found`: the name ends in `_` (private, not callable through the API), or
  the code wasn't pushed.
- `The caller does not have permission`: the token lacks a scope the script declares, or Geoff
  isn't the owner.
- No deployment: `run-function` needs an API-executable deployment; development mode then runs
  the last pushed code.
- A trigger that "does nothing": read `gws script processes list` for a `FAILED` run, then
  `clasp tail-logs`. A `try`/`catch` that only shows a toast hides the error from both, so a
  handler logs with `console.error` too.
