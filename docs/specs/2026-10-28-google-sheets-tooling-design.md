# Google Sheets and Apps Script tooling

## Brief

Claude gets three ways into any Google Sheet on your account, from any project. `gws` keeps the
Sheets API as you. Google's `clasp` CLI handles Apps Script as you: push code, run a function, and
read the logs. A new helper Google account, signed in to Claude's Chromium profile, opens sheets
and types into them, so `onOpen` and `onEdit` fire and Claude can read the screen. One workstation
skill, `google-sheets`, carries the procedure, and per-sheet skills such as ecxc-ski's
`gear-checkout` build on it. The first use verifies the gear sheet's sort fix end to end.

Approving this sets up a sitting of about 30 minutes: you create the helper account, sign it in,
share one Drive folder with it, give it two roles on the `gws` Cloud project, and complete two
sign-ins that Claude starts. No new secret enters the age store. This session then builds and
tests it in one `runner` pass and sends the PR back to you.

### Decide: who switches a script's Cloud project

`clasp run-function` and `clasp tail-logs` need each script moved off its hidden default Cloud
project onto a standard one, once per script, and Google offers that switch only in the script
editor's settings.

- The helper account does it in its browser (recommended). You grant it Project Browser and OAuth
  Config Editor on `gws-personal-508705`, the project that already holds the `gws` client. The
  worst a hijacked helper session could do there is edit or break the OAuth client setup, which
  you can rebuild. Nothing in that project reaches your mail or files.
- You click it yourself for each new script, about a minute each. No IAM grant, but every new
  script waits on you.

### Decide: the OAuth consent screen's publishing status

`gws-personal` is External and in Testing, so Google expires its sign-ins after 7 days and `gws`
(and now `clasp`) need a fresh sign-in each week.

- Publish it to In production, unverified (recommended). The 100-user cap still applies, and each
  sign-in shows the "Google hasn't verified this app" screen once. Google's help confirms the
  7-day expiry for Testing but not plainly its absence in production, so STATUS carries a check on
  2026-11-05 that `gws` still answers without a new sign-in. You can move it back to Testing.
- Leave it in Testing and add the helper as a test user. The weekly sign-in stays.

### Decide: the helper account's name

Coaches and anyone else on a shared sheet will see this account in the sharing list and in
version history. The recommendation is a free Google account on a Proton Pass alias on your
masked-address domain (for example `claude-sheets@me.907.life`), created with the login item, so
Google's mail reaches you and no mail-server change is needed. Display name "Claude (Geoff's
assistant)". A Gmail address works the same if you'd rather.

## Goal and scope

Claude can build, edit, and test any Google Sheet on geoff@907.life from any project, with no
copy-and-paste from Geoff, across three layers: values, formatting, and structure through the
Sheets API; Apps Script code, runs, and logs; and verification as a person sees it, including
opens, reloads, clicks, typing, toasts, and errors.

Out of scope: Docs and Slides scripts beyond what the same skill covers for free, installable
triggers, web-app deployments, add-ons, a `check-drift` probe for `mise` tools, and sheets Geoff
does not own (their owner shares them with the helper directly; the skill says so).

Initiative: none applies. This is workstation tooling with no cross-repo record.

## The three layers

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

**Browser: the helper account in Claude's Chromium `Default` profile, through claude-in-chrome.**
The helper has no OAuth grant of its own and no API use. It reaches only the shared folder, and
on that project only the two roles above. Geoff's account never signs in to `Default`.

## Sign-ins

Every sign-in is Geoff's grant. Claude starts it in the background, reads the URL from the
output, fixes `&amp;` to `&`, and hands it over; Geoff completes it in his own profile. Two tracked
`settings.json` allow rules let a session start that step without the classifier, since the
consent screen is the real gate: `Bash(gws auth login *)` and `Bash(clasp login *)`. The same
change allows the routine `clasp` subcommands (`push`, `pull`, `show-file-status`,
`clone-script`, `create-script`, `create-deployment`, `list-deployments`, `run-function`,
`tail-logs`, `setup-logs`, `show-authorized-user`) and denies `clasp delete-script`.

## The helper account and the folder

Geoff creates the account in the `Default` profile, keeps its password and second factor in his own Proton Pass vault
(Claude never needs the value: a lapsed browser session is a sign-in, so it is Geoff's), and
declines Chromium sync when asked, so the account stays a web sign-in only. `bluefin-admin.md`
records the item's name and vault. He creates a My Drive folder named `Claude`, shares it with the
helper as Editor, and moves in each sheet Claude should test in a browser; a move keeps every
direct share, so the coaches' access to the gear sheet does not change. The skill checks a sheet's
`parents` before a browser test and asks for a move when the sheet sits outside the folder. The
claude-in-chrome extension needs site access to `docs.google.com` and `script.google.com`.

## Per-script steps

Each script lives in its repo as one directory: `.clasp.json` (script ID, `rootDir`, Cloud
`projectId`), `appsscript.json`, and the code files. The directory is the source of truth.

1. A new bound script: `clasp create-script --type sheets --parentId <sheet>` (Claude). An existing
   one: `clasp clone-script <id>` into the directory, then reconcile with the repo copy (Claude).
2. The manifest declares `oauthScopes`, `exceptionLogging: STACKDRIVER`, and
   `executionApi.access: MYSELF` (Claude).
3. Switch the Cloud project to `754967083271` in the editor's Project settings (the helper's
   browser, or Geoff, per the first decision).
4. `clasp setup-logs`, `clasp push`, and `clasp create-deployment`, which the manifest makes an API
   executable (Claude).

## Test procedure (any project)

1. Push, then pull into a scratch directory and diff against the repo copy.
2. `clasp run-function` on a function that touches no UI, then read the result back with `gws`.
3. Read failures with `clasp tail-logs` and `gws script processes listScriptProcesses`.
4. Set a state only a trigger fixes (an API write), then open or reload the sheet as the helper,
   act as a person would, and take a screenshot. The main loop reads the screenshot, never a
   subagent's account of it, and checks the toast and any error banner.
5. Read the values back with `gws`, then undo any test change.

## Where each piece lives

| Piece | Home |
| --- | --- |
| The procedure (three layers, sign-ins, per-script steps, test procedure) | new skill `claude/.claude/skills/google-sheets/`, a `SKILL.md` plus `references/apps-script.md` and `references/browser-check.md` |
| Facts: tools, tokens, scopes, project, helper item | `bluefin-admin.md` "Google Docs / Drive (gws)", renamed "Google Workspace (gws, clasp)"; its Apps Script stopgap paragraph goes |
| `clasp` install | `mise/.config/mise/config.toml` |
| Allow and deny rules | tracked `claude/.claude/settings.json` |
| Global pointer | the CLAUDE.md "Google Docs / Drive / Sheets" line gains `clasp` and the skill name |
| thinkpad-x1 | a STATUS item: pull, `stow -R claude`, `mise install`, `claude-tooling-sync apply`, both sign-ins, the helper's browser sign-in, the extension's site access |
| Gear sheet | ecxc-ski: the script moves into `docs/coach-tools/gear-checkout-sort/`, and `gear-checkout.md` and its skill use the new skill, committed to `main` per that repo's rule |

No hook: nothing here must hold on every turn. No MCP server: `clasp mcp` exists, but a skill
over the CLI reaches every agent, and the global rule keeps Google off MCP.

## End-to-end check

On the gear sheet, after the API write that undoes the sort: the helper opens the sheet, and the
screenshot and a `gws` read both show Rissie between Randall and Sadie on Roster. Retyping an
existing first name (same value, so no data changes) re-sorts through `onEdit`. A Race skis
dropdown, opened in the browser and read through `gws`, offers only A Team athletes not yet on
the tab. If the sort still fails, the fix lands in ecxc-ski and the check runs again.

## Risk, estimate, and execution

Class `runner` (a skill and `settings.json`), touching a live Google account. Path estimate: 210
minutes. Backlog sweep: no open item in `BACKLOG.md` touches Google, Sheets, `gws`, `clasp`, or the
browser profile, so the sweep has no verdicts. This session executes the plan itself after the
sitting, because the request names it as the builder; it hands the PR back through a packet.

Standing answers. If the helper cannot switch a bound script's project, Geoff does that one
click in the sitting and the skill records it as his step. If the 2026-11-05 check finds `gws`
expired, the consent screen goes back to Testing with the helper as a test user. A sort that
still fails after two traced fixes is reported in the PR with the evidence, and the rest of the
pass lands.

## Later

A `check-drift` probe for `mise` tools. A per-sheet test harness, if a second sheet ever needs one.
