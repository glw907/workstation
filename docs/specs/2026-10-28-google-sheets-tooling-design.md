# Google Sheets and Apps Script tooling

## Brief

Claude gets two ways into any Google Sheet on your account, from any project. `gws` keeps the
Sheets API as you. Google's `clasp` CLI handles Apps Script as you: push code, run a function, and
read the logs. Trigger code is tested by running it through `clasp` with a built event, so no
helper Google account and no browser sign-in are needed. One workstation skill, `google-sheets`,
carries the procedure, and per-sheet skills such as ecxc-ski's `gear-checkout` build on it. The
first use verifies the gear sheet's sort fix end to end.

Revised 2026-10-29. The first draft added a helper Google account in Claude's Chromium profile to
open sheets and type into them. Google now requires a phone QR check to create any account,
Workspace included, and you have no phone, so you chose to drop the browser layer (Geoff,
2026-10-29).

Approving this sets up a short sitting: two sign-ins that Claude starts and you complete, and one
click per script in the Apps Script editor. No new secret enters the age store. This session then
builds and tests it in one `runner` pass and sends the PR back to you.

### What you give up

Claude can't see a sheet the way you do. It tests what a trigger does to the data, but not a
toast, a menu, a dialog, or how the sheet looks. Claude also can't prove that a real open or edit
fires the trigger, since the test calls the handler directly. When a change touches those, the
skill ends with a short check for you to do in your browser, and the PR names it.

### Decide: the OAuth consent screen's publishing status

`gws-personal` is External and in Testing, so Google expires its sign-ins after 7 days and `gws`
(and now `clasp`) need a fresh sign-in each week.

- Publish it to In production, unverified (recommended). The 100-user cap still applies, and each
  sign-in shows the "Google hasn't verified this app" screen once. Google's help confirms the
  7-day expiry for Testing but not plainly its absence in production, so STATUS carries a check on
  2026-11-05 that `gws` still answers without a new sign-in. You can move it back to Testing.
- Leave it in Testing. The weekly sign-in stays.

## Goal and scope

Claude can build, edit, and test any Google Sheet on geoff@907.life from any project, with no
copy-and-paste from Geoff, across two layers: values, formatting, and structure through the Sheets
API; and Apps Script code, runs, logs, and trigger tests through `clasp`.

Out of scope: a browser view of a sheet (see "What you give up"), Docs and Slides scripts beyond
what the same skill covers for free, installable triggers, web-app deployments, add-ons, a
`check-drift` probe for `mise` tools, and sheets Geoff does not own (`clasp` runs a script in
development mode only for its owner).

Initiative: none applies. This is workstation tooling with no cross-repo record.

## The two layers

**Sheets API: `gws` as Geoff.** No change to the client or project. The sign-in adds
`script.processes` so a failed trigger run is visible (`gws script processes listScriptProcesses`
shows status per run). Scopes, passed explicitly with `--scopes` because `-s ...,script` did not
take: `documents`, `drive`, `spreadsheets`, `script.projects`, `script.processes`. The skill sends
the API's real behavior to the synced `anthropic-skills:google-workspace` skill
(`references/sheets.md`, `scripts/sheets_helper.py`, which reads raw API JSON as well as connector
output) instead of restating it.

**Apps Script: `clasp` as Geoff.** `clasp` 3.4.1 installs through `mise`'s `npm:` backend, pinned
to major 3 in the stowed `mise/.config/mise/config.toml`, so a major bump asks first per the
dependency rule. That is the Node twin of `uv tool install`: tier 1 or 2, never Homebrew, which
has no `clasp` formula. Node 24 LTS meets its `>= 22` floor. The stowed config is the manifest,
and `bootstrap.sh`'s `mise install` brings it to a new host.

`clasp` signs in with the existing `gws` Desktop client (`~/.config/gws/client_secret.json`, an
`installed`-type file `clasp login --creds` accepts), so both tools share one client in
`gws-personal-508705` and hold separate tokens: `gws` its encrypted store in `~/.config/gws/`,
`clasp` the plain `~/.clasprc.json` its 3.x line requires (the `--auth` path option is
deprecated). Same client means the Execution API's rule holds: "Ensure that the script and the
calling application's OAuth2 client share a common Google Cloud project"
(developers.google.com/apps-script/api/how-tos/execute). `clasp` runs as Geoff because "Only the
owner of the script can execute it in development mode", and Geoff owns the sheets that matter
(the gear sheet's owner is geoff@907.life, read 2026-10-28). The login takes `clasp`'s default
scopes plus `--extra-scopes` for `spreadsheets`, since `run-function`'s token "must cover all the
scopes used by the script". The plan reads the exact default list from the installed source and
puts it in the sign-in hand-over.

## Trigger tests

Simple triggers never fire on an API write, so a test runs the handler itself. Each script keeps
its handlers thin: `onEdit(e)` and `onOpen(e)` check the event and call a named function that does
the work on a sheet, such as `sortRoster(sheet)`. UI calls (`SpreadsheetApp.getUi()`, menus,
dialogs) stay in the handler, because they throw when the script runs through the Execution API.

A `tests.gs` file in the script directory holds one public function per case, such as
`testOnEditRosterName()`. Each builds the event object Google documents for that trigger
(`source`, `range`, `value`, `oldValue`) from the live sheet, calls the real handler, and returns
what it changed. Names carry no trailing underscore, because the Execution API cannot call a
private function. Claude runs a test with `clasp run-function`, then reads the cells with `gws`.
The file ships with the script, so coaches see it in the editor. It changes nothing unless someone
runs it.

## Sign-ins

Every sign-in is Geoff's grant. Claude starts it in the background, reads the URL from the
output, fixes `&amp;` to `&`, and hands it over; Geoff completes it in his own profile. Two tracked
`settings.json` allow rules let a session start that step without the classifier, since the
consent screen is the real gate: `Bash(gws auth login *)` and `Bash(clasp login *)`. The same
change allows the routine `clasp` subcommands (`push`, `pull`, `show-file-status`,
`clone-script`, `create-script`, `create-deployment`, `list-deployments`, `run-function`,
`tail-logs`, `setup-logs`, `show-authorized-user`) and denies `clasp delete-script`.

## Per-script steps

Each script lives in its repo as one directory: `.clasp.json` (script ID, `rootDir`, Cloud
`projectId`), `appsscript.json`, the code files, and `tests.gs`. The directory is the source of
truth.

1. A new bound script: `clasp create-script --type sheets --parentId <sheet>` (Claude). An existing
   one: `clasp clone-script <id>` into the directory, then reconcile with the repo copy (Claude).
2. The manifest declares `oauthScopes`, `exceptionLogging: STACKDRIVER`, and
   `executionApi.access: MYSELF` (Claude).
3. Switch the Cloud project to `754967083271` in the editor's Project settings (Geoff, about a
   minute; Google offers the switch only there). The skill hands over the editor link and the
   project number.
4. `clasp setup-logs`, `clasp push`, and `clasp create-deployment`, which the manifest makes an API
   executable (Claude).

## Test procedure (any project)

1. Push, then pull into a scratch directory and diff against the repo copy.
2. Note the cells a test will touch, read them with `gws`, and keep the values.
3. Set the state the trigger should fix with an API write, run the matching `tests.gs` function
   with `clasp run-function`, and read the result back with `gws`.
4. Read failures with `clasp tail-logs` and `gws script processes listScriptProcesses`.
5. Restore the values from step 2.
6. If the change touches anything on screen (a toast, a menu, a dialog, formatting a person
   reads), end with one browser check for Geoff, stated as what to open, what to do, and what he
   should see.

## Where each piece lives

| Piece | Home |
| --- | --- |
| The procedure (two layers, trigger tests, sign-ins, per-script steps, test procedure) | new skill `claude/.claude/skills/google-sheets/`, a `SKILL.md` plus `references/apps-script.md` and `references/trigger-tests.md` |
| Facts: tools, tokens, scopes, project | `bluefin-admin.md` "Google Docs / Drive (gws)", renamed "Google Workspace (gws, clasp)"; its Apps Script stopgap paragraph goes |
| `clasp` install | `mise/.config/mise/config.toml` |
| Allow and deny rules | tracked `claude/.claude/settings.json` |
| Global pointer | the CLAUDE.md "Google Docs / Drive / Sheets" line gains `clasp` and the skill name |
| thinkpad-x1 | a STATUS item: pull, `stow -R claude`, `mise install`, `claude-tooling-sync apply`, both sign-ins |
| Gear sheet | ecxc-ski: the script and its `tests.gs` move into `docs/coach-tools/gear-checkout-sort/`, and `gear-checkout.md` and its skill use the new skill, committed to `main` per that repo's rule |

No hook: nothing here must hold on every turn. No MCP server: `clasp mcp` exists, but a skill
over the CLI reaches every agent, and the global rule keeps Google off MCP.

## End-to-end check

On the gear sheet, after an API write that undoes the sort, a `tests.gs` case calls `onEdit` with
a built edit to a Roster first name. A `gws` read then shows Rissie between Randall and Sadie. A
second case checks that a Race skis dropdown, read through `gws`, offers only A Team athletes not
yet on the tab. If the sort still fails, the fix lands in ecxc-ski and the check runs again.
Geoff's browser check opens the sheet and retypes one first name (the same value, so no data
changes), to confirm a real edit fires the trigger.

## Risk, estimate, and execution

Class `runner` (a skill and `settings.json`), touching a live Google account. Path estimate: 160
minutes. Backlog sweep: no open item in `BACKLOG.md` touches Google, Sheets, `gws`, `clasp`, or the
browser profile, so the sweep has no verdicts. This session executes the plan itself after the
sitting, because the request names it as the builder; it hands the PR back through a packet.

Standing answers. If a handler can't be split from its UI calls, its test covers the work function
alone, and the PR names the gap. If the 2026-11-05 check finds `gws` expired, the consent screen
goes back to Testing. A sort that still fails after two traced fixes is reported in the PR with
the evidence, and the rest of the pass lands.

## Later

A `check-drift` probe for `mise` tools. A per-sheet test harness, if a second sheet ever needs one.
A browser layer, if a second Google identity ever becomes available.
