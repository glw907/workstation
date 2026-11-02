# sportsYou desktop alerts

## Brief

This builds a small program that shows a GNOME alert when sportsYou mail reaches ward, and clicking the alert opens the exact post or event in your sportsYou window.

sportsYou has no public API and sends you alerts only by email, and you have no phone app. A live connection to ward lets the alert appear when ward files the mail, without waiting on Hylki.

### What changes

- A new private repo, `glw907/sportsyou-alerts`, holds one Go program with tests, a README, and a backlog.
- Each workstation runs it as a systemd user service. It watches only the SportsYou folder and uses a read-only app password.
- GNOME Settings gains a sportsYou entry, which turns the alerts off or down.
- The `sportsyou` launcher learns to open a given link, and its desktop entry moves to the app ID `ski.ecxc.SportsYou` with a real icon.

### If you approve

1. The session finishes the folder change, which this design depends on.
2. A pass creates the repo, builds and tests the program, and installs it on this laptop.
3. The pass creates the app password, stores it in the age store, and adds the install to the manifests, so pavilion gets it from the daily sync.
4. You run one test with a real post and a real chat.

### Worth knowing

The app password can read your whole mailbox, because Stalwart scopes a password by permission and never by folder. The program asks for the SportsYou folder only, and the password can't send, change, or delete mail.

### Alert rules

Every alert follows the GNOME notification guidelines. The title is a short summary in header capitalization, and the body is one sentence with no closing period. Clicking is the only action, so an alert has no buttons, and the click dismisses it and opens the place named below.

| Mail | Title | Body | Click opens |
| --- | --- | --- | --- |
| A post | New Post From Amy Purevsuren | The start of the post | That post |
| A new event | New Event in East XC Ski 26-27 | Event name and time | That event |
| A changed event | Event Updated | Event name | That event |
| A removed event | Event Removed | Event name | The calendar |
| More than three at once | 4 New sportsYou Updates | None | The home page |
| Anything else | sportsYou Update | The email subject | The best link in the email |

An alert disappears when its email is marked read, as the guidelines require for a message that is no longer new. Mail that arrived while the service was off appears as one summary, never as a replay. The sportsYou window still shows everything, so a missed alert loses nothing.

### How it works

The program holds a JMAP event stream to `mail.907.life`. On each mail change it queries the SportsYou folder for unread messages it has not shown, reads each one, and builds the alert from the subject and body. It keeps the IDs it has shown in `~/.local/state/sportsyou-alerts/`, so a restart repeats nothing. It reconnects with a backoff after sleep or a network drop, and a read timeout catches a dead connection.

Posts link to `team/teamPosts.html` and events to `calendar?eventId=`, both read from real mail on 2026-11-01. The program never follows a link. It hands the link to the sportsYou window only after you click.

### Where it runs

It runs on the workstations, because a desktop alert can only appear on the desktop. Cloudflare, orpheus, and ward gain nothing, and ward serves one more JMAP connection per host. If ward is down, alerts stop and mail is unaffected. The only state is the list of shown IDs, which needs no backup. The password lives in the age store and reaches each host through `sync.sh --local`.

### Language

The program is Go, the house default for a standalone repo tool. It talks to GNOME over D-Bus through `godbus`, using the same service `GNotification` uses, so it needs no C build on Bluefin. The first task proves that a click reaches the program on GNOME 50. If it doesn't, the program falls back to the standard notification service, which also supports a click and a withdrawal.

### Hosts

thinkpad-x1 gets the service in this pass. pavilion gets it from `workstation-sync`, and needs its first sign-in to the sportsYou window. Each host alerts on its own. Reading the email clears both, and clicking clears only that host's alert.

### Standing answers

The run decides these without you, within an estimate of 90 path minutes. A sportsYou email the parser doesn't recognize takes the "anything else" row, and the run adds a parser case only for a shape seen in real mail. If a deep link fails in the window, the click opens the home page and the failure goes in the PR's `## Decisions`. If the read-only permissions refuse the event stream, the run adds the fewest permissions that make it work and lists them there. It stops only if the event stream needs a permission that can change mail.

### Backlog sweep

No item in `BACKLOG.md` here or in ecxc-ski mentions sportsYou alerts, so nothing changes in either backlog. The ecxc rebuild's non-goal of no sportsYou integration stands, because this touches your desktop and mailbox and never the site.
