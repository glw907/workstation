# sportsYou desktop indicator

## Brief

This builds a small top-bar indicator that counts unread sportsYou mail and opens each item in the exact spot in your sportsYou window, and it gives that window a custom theme that follows your GNOME style.

sportsYou has no public API and reaches you only by email, and you have no phone. A live connection to ward updates the count when ward files the mail, without waiting on Hylki. All reading, posting, and chatting stay in the web app.

### What changes

- A new private repo, `glw907/sportsyou-indicator`, holds one Go program with tests, a README, and a backlog, plus the theme stylesheet.
- Each workstation runs the program as a systemd user service. It watches only the SportsYou folder.
- A sportsYou icon stays in the top bar, with a count beside it when anything is unread. GNOME sends no notifications for this mail.
- The sportsYou window follows your GNOME light or dark style, in Adwaita's colors with your accent color.

### If you approve

1. A pass creates the repo, builds and tests the program and theme, and installs them on this laptop.
2. The pass creates the mail password, stores it in the age store, and adds the install to the manifests, so pavilion gets it from the daily sync.
3. You run one test with a real post and a real chat, and look over the theme.

### Worth knowing

The mail password can read and update your whole mailbox, because Stalwart scopes a password by permission and never by folder. Marking mail read needs the update permission, which also allows moving mail. The password can't send mail or permanently delete it, and the program touches only the SportsYou folder.

### The indicator

The menu lists unread items, newest first, up to ten, with times. An "and N more" row opens the home page. Below them sit Mark All Read and Open sportsYou.

- Clicking an item opens its spot and marks that email read. A post opens its post page, an event its calendar page, and anything else the best link in the email. A removed event opens the calendar.
- Every unread email in the folder counts, login warnings included.
- Marking an email read in Hylki clears it here too. Reading in the web app can't, because the program sees only the mail, so Mark All Read covers that case.
- The icon changes when the connection to ward fails, so a broken service never looks like a quiet day.
- At setup, emails older than one day are marked read, so the count starts near zero.

### The GNOME guidelines

The indicator is your deliberate exception to the GNOME guidelines, which discourage status icons, and to the calm desktop rule against unread counters (Geoff, 2026-11-01). The dock stays free of badges, because a dock badge would turn on for every app and couldn't reach the exact spot. Menu labels follow GNOME's writing style: header capitalization for commands and no closing periods.

### How it works

The program holds a JMAP event stream to `mail.907.life`. On each mail change it queries the folder for unread mail and rebuilds the menu. It reconnects with a backoff after sleep or a network drop, and a read timeout catches a dead connection. It keeps no state, because the mailbox holds the unread list, so a restart loses nothing and the two hosts agree. It reads links from each email and never follows one until you click.

Real links opened correctly on a signed-in copy of the window's profile on 2026-11-01. They reached the post page and the event page with the address intact. Scrolling to the exact post is unconfirmed.

### The theme

A small local extension, loaded only in the sportsYou profile, injects one stylesheet. It uses `prefers-color-scheme` for light and dark. It changes only what your own screen shows, and it may need a touch-up when sportsYou changes its design. The pass proves first that Chromium 156 still loads it and that the page follows the GNOME setting. If the flag no longer loads it, the run installs the extension through the profile's developer mode instead.

### Where it runs

It runs on the workstations, because a top-bar icon can only live on the desktop. Cloudflare, orpheus, and ward gain nothing, and ward serves one more JMAP connection per host. If ward is down, the icon shows it and mail is unaffected. There's no state to back up. The password lives in the age store and reaches each host through `sync.sh --local`.

### Language

The program is Go, the house default for a standalone repo tool, using a pure Go status-icon library, so it needs no C build on Bluefin. The AppIndicator extension is already enabled on this laptop. If the library can't show a text count, the program draws the count into the icon.

### Hosts

thinkpad-x1 gets the service in this pass. pavilion gets it from `workstation-sync`, and needs its first sign-in to the sportsYou window. Both hosts read the same mailbox, so reading an item on one clears it on the other.

### Standing answers

The run decides these without you, within an estimate of 150 path minutes. A sportsYou email the parser doesn't recognize shows its subject and opens its best link. If a deep link fails in the window, the item opens the home page and the failure goes in the PR's `## Decisions`. If the update permissions refuse the event stream, the run adds the fewest permissions that make it work and lists them there. It stops only if the program would need permission to send or destroy mail.

### Backlog sweep

No item in `BACKLOG.md` here or in ecxc-ski mentions sportsYou. Approving adds one item to this repo's backlog: Do Not Disturb is off on thinkpad-x1, against the calm desktop rule, and `check-drift` doesn't catch it. The ecxc rebuild's non-goal of no sportsYou integration stands, because this touches your desktop and mailbox and never the site.
