---
name: google-sheets
description: Use when building, editing, or testing a Google Sheet or its Apps Script on Geoff's account from any project, including a bound script's code, its onOpen or onEdit triggers, a run that fails silently, or a per-sheet skill such as ecxc-ski's gear-checkout. Covers the two layers (the Sheets API through gws, Apps Script through clasp), the sign-ins, the per-script setup, trigger tests through clasp run-function, and the browser check Geoff runs.
---

# Google Sheets and Apps Script

Claude works on Geoff's sheets as geoff@907.life through two CLIs. `gws` reads and writes values,
formatting, and structure through the Sheets API. `clasp` pushes Apps Script code, runs functions,
and reads logs. Claude has no browser view of a sheet: no Google identity is signed in to its
Chromium profile, because creating one needs a phone (Geoff, 2026-10-29). Tokens, scopes, and the
Cloud project are in `~/.claude/docs/bluefin-admin.md` "Google Workspace (gws, clasp)".

Sheets API behavior (A1 ranges, `batchUpdate` requests, validation rules, reading raw JSON) is in
the `anthropic-skills:google-workspace` skill's `references/sheets.md` and
`scripts/sheets_helper.py`. Read those before a structural write; this skill doesn't restate them.
Two quirks seen on the gear sheet: a `ONE_OF_RANGE` rule sent with a relative range comes back
absolute, so set per-row rules one row at a time; and a simple trigger never fires on an API write.

## Sign-ins

A sign-in is Geoff's grant. When a call answers `invalid_grant` or an expired token, start the
login in the background with the command in `bluefin-admin.md`, read the URL from its output, fix
`&amp;` to `&`, and hand it over. Never run a login through `!`, which blocks. Never add a scope
without saying which and why.

## A script's directory

Every script lives in its repo as one directory, the source of truth: `.clasp.json`,
`appsscript.json`, the code files, and `tests.gs`. Set it up once per script:

1. A new bound script: `clasp create-script --type sheets --parentId <spreadsheet id>`. An existing
   one: `clasp clone-script <script id>` into the directory, then reconcile with any repo copy.
2. In `appsscript.json`, declare `oauthScopes`, `"exceptionLogging": "STACKDRIVER"`, and
   `"executionApi": {"access": "MYSELF"}`.
3. Ask Geoff to switch the script's Cloud project to 754967083271: in the script editor, Project
   Settings, Change project. Hand him the editor link (`clasp open-script` prints it). Google
   offers the switch nowhere else.
4. `clasp setup-logs`, `clasp push`, then `clasp create-deployment`, which the manifest makes an API
   executable.

Commands, flags, and failure messages: `references/apps-script.md`.

## Test procedure

1. `clasp push`, then `clasp pull` into a scratch directory and diff against the repo copy.
2. Read the cells a test will touch with `gws` and keep the values.
3. Set the state the trigger should fix with an API write, run the matching `tests.gs` function
   with `clasp run-function <name>`, and read the result back with `gws`. The test's return value
   is a summary, never the evidence; the `gws` read is.
4. On a failure, read `clasp tail-logs` and `gws script processes list`, which shows each run's
   status, trigger runs included.
5. Restore the values from step 2.
6. If the change touches anything on screen (a toast, a menu, a dialog, formatting a person
   reads), end with one browser check for Geoff: what to open, what to do, and what he should see.
   Name it in the PR or the reply.

How to write the handlers and `tests.gs` so a test can drive them: `references/trigger-tests.md`.

## Sheets Geoff doesn't own

`clasp run-function` runs a script in development mode only for its owner. For a sheet someone
else owns, Claude can still read and write through `gws` if the sheet is shared with Geoff, but
trigger tests need the owner to transfer the script or run them.
