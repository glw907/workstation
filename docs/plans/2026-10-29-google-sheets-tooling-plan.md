# Google Sheets tooling plan

Design: `docs/specs/2026-10-28-google-sheets-tooling-design.md` (approved 2026-10-29, Approval
Queue item `20261029T170653-332715`; consent screen: publish). Initiative: none. Class: `runner`,
`live-account`. Branch: `google-sheets-tooling`, executed by this session in the main checkout.
Push target: `glw907/workstation`. Path estimate 160 minutes; this plan's path is 140.

## Pre-flight

All four happen in the sitting before T3.

1. Publish the consent screen: console.cloud.google.com, project `gws-personal`, Google Auth
   Platform, Audience, Publish app. Check: the page reads In production.
2. `gws` sign-in. The session runs `gws auth login --scopes` with `documents`, `drive`,
   `spreadsheets`, `script.projects`, `script.processes` in the background and hands over the URL.
   Check: `gws script processes listScriptProcesses` answers.
3. `clasp` sign-in. The session runs `clasp login --creds ~/.config/gws/client_secret.json
   --extra-scopes https://www.googleapis.com/auth/spreadsheets` in the background and hands over
   the URL. clasp 3.4.1's defaults (`build/src/commands/login.js`, `DEFAULT_SCOPES`) include
   `cloud-platform`, `service.management`, and `logging.read`, which the hand-over names. Check:
   `clasp show-authorized-user` prints geoff@907.life.
4. Switch the gear script's Cloud project to `754967083271` in its editor's Project Settings.
   Check: `clasp run-function` reaches the script after T3 creates the deployment (a wrong
   project answers with a permission error naming the project).

## Tasks

T1 and T2 are a pair in effect (disjoint files), run in sequence by this session.

**T1. Record `clasp` and the facts (20 min, `runner`).** Commit
`mise/.config/mise/config.toml` (the `npm:@google/clasp = "3"` line, already installed).
Rewrite `bluefin-admin.md` "Google Docs / Drive (gws)" as "Google Workspace (gws, clasp)": tools,
tokens and where each lives, the scopes of each sign-in, the shared client and project, the
published consent screen, and the 2026-11-05 expiry check; drop the 2026-10-28 stopgap
paragraph. Extend the global CLAUDE.md line with `clasp` and the skill name. Accept:
`claude-context-budget` passes and no reference to the helper account remains.

**T2. Write the `google-sheets` skill (50 min, `runner`).** `claude/.claude/skills/google-sheets/`
with `SKILL.md` (when to use, the two layers, sign-ins, per-script steps, the test procedure, the
browser check for Geoff), `references/apps-script.md` (`clasp` commands, the manifest keys, logs
and process reads), and `references/trigger-tests.md` (thin handlers, the `tests.gs` shape, built
event objects, no trailing underscore, UI calls stay in handlers). It points at the synced
`google-workspace` skill for Sheets API behavior instead of restating it. Register it per
`claude-infra` and `claude-tooling.md`. Accept: `claude-tooling-sync verify` passes and the skill
appears in the session's skill list after `apply`.

**T3. Gear sheet end to end (50 min, `runner`, after the sitting).** In ecxc-ski, move the script to
`docs/coach-tools/gear-checkout-sort/` through `clasp clone-script`, reconcile with the repo copy,
add the manifest keys and `tests.gs` (an `onEdit` case on a Roster first name; a Race skis picker
case), then `setup-logs`, `push`, `create-deployment`. Undo the sort with an API write, run the
cases, and read Roster and Race skis back with `gws`. Accept: the moved row lands back in
first-name order, and each Race skis picker offers only A Team athletes not yet on the tab. Update
`gear-checkout.md` and the `gear-checkout` skill to use the new skill; commit to ecxc-ski `main`.

**T4. Close (20 min).** STATUS: the thinkpad-x1 item (pull, `stow -R claude`, `mise install`,
`claude-tooling-sync apply`, both sign-ins) and the 2026-11-05 check; drop the Next action. Gate,
`gitleaks git` branch scan, whole-branch `diff-reviewer`, PR with `## Brief`, packet.

## Standing answers

From the design: a handler that can't be split from its UI calls gets a test of its work function
only, named in the PR. A `gws` expiry found on 2026-11-05 moves the consent screen back to
Testing. A sort that still fails after two traced fixes is reported in the PR with the evidence,
and the rest lands. Added here: if the project switch in pre-flight 4 isn't done when T3 starts,
T3 waits on it as the sitting's last item rather than reordering.
