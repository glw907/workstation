# Thunderbird Nord mail layer: message list and reader

## Brief

Thunderbird's message list and reader will use Nord colour where it helps you scan and read, on both machines.

Today unread mail differs from read mail by bold alone, sender names are cut off by their own email addresses, and quoted replies turn blue like links. This pass fixes those three things, grounded in a research report on how people scan lists, contrast and colour vision, and how good mail clients handle each case.

### What changes

- Unread messages get a small Nord blue dot at the left edge, as well as bold text.
- Senders show their name only, so names stop being cut off by email addresses.
- Cards shrink from three rows to two, so about a third more messages fit on screen.
- Unflagged stars hide until you point at a message; flagged ones show in Nord yellow.
- Quoted replies keep normal text colour, with a Nord bar per level that fades as levels deepen.
- Links in plain-text mail are underlined, and signatures recede in both light and dark mode.
- Thunderbird's own junk filter turns off, and Fastmail's server filter handles spam.
- One palette file and a role table let poplar or any other client follow the same map.

### If you approve

1. A session writes the spec and plan, and a Sonnet session builds the pass in its own worktree.
2. It checks the result with screenshots of a test profile in light and dark mode, then opens one PR.
3. After the merge, you quit Thunderbird once, run `thunderbird-theme-sync`, and clear the old junk marks in your inbox.

### Decide: Who merges the PR

The pass only touches Thunderbird's styling, preferences, and its own tools, so the process lets it merge itself once its checks pass. This is a look-and-feel change, though, and you may want to see it first.

- You look at the screenshots in the PR before it merges (recommended)
- It merges itself once the checks pass

### Worth knowing

Turning off Thunderbird's junk filter doesn't clear the junk marks it already set, so the cards it flagged keep their junk icon until you mark them not junk once. The README and the runbook will say how.

### The evidence

The design follows a research report rather than taste alone. The report lives at `docs/research/2026-10-13-mail-colour-evidence/reports/Mail colour readability evidence.md`, with four sets of researcher notes and a styling map of Thunderbird 158 beside it. Its conclusion: let Nord decorate while shape signals. Every meaning gets a cue that survives without colour (a dot, a glyph, weight, position, or an underline), and Nord colour adds speed on top. Where the report found no direct study, as for unread styling and quote colouring, the design rests on general vision science, WCAG 2.2, and what shipping clients do, and says so.

### The role map

One new file, `thunderbird/nord.css`, holds the 16 Nord colours by name and the roles below. Every other rule names a role, never a hex value. Each role colour goes through the GNOME theme's lightness rule, which lightens it in dark mode and deepens it in light mode, so text passes WCAG 4.5:1 in both modes.

Frost marks system state and Aurora marks your own meanings. Under colour-vision deficiency only cool-against-warm pairs stay reliably apart, so no two roles depend on telling two blues, or red and green, apart.

| Role | Nord | Cue that works without colour |
|---|---|---|
| Accent fills (buttons, badges, selection) | nord10, white text | |
| Accent text: unread dot, new sparkle, thread-unread marker, links | nord8 | Dot or sparkle glyph; underline on links |
| Flagged and needs action | nord13 | Star glyph |
| Error, destructive, junk | nord11 | Icon and wording |
| Success | nord14 | Icon and wording |
| Tags: Important, Work, Personal, To Do, Later | nord11, nord12, nord14, nord13, nord15 | Tag glyph and name |
| Sender, subject, body text | neutral | Position, weight, size |
| Secondary text: dates, counts, labels, signature | neutral, dimmed to 4.5:1 or better | Size and position |
| Quote bars | nord8, fading by level | Indent, attribution line, 3 px bar |
| Surfaces | Adwaita neutral, unchanged | |

`thunderbird/README.md` carries this table as the shared role map.

### The message list

Both views carry the same cues. Cards restore the unread dot the GNOME theme hides, in nord8, and keep bold sender and subject; table view's unread column turns nord8 and unread rows stay bold. New mail shows a nord8 sparkle, and a collapsed thread with unread replies marks its expander in nord8. `mail.addressDisplayFormat = 2` shows senders' names only; Thunderbird still shows the real address when a name pretends to be one. Cards drop to two rows (`mail.threadpane.cardsview.rowcount = 2`). Unflagged stars hide until hover or selection, and flagged stars fill nord13. Reply, forward, and redirect icons turn neutral. Junk text loses its red. Tag icons and tag-coloured table rows use the adjusted Nord tag colours. Selection and hover keep the theme's neutral greys.

### The reader

The header keeps the subject as its largest line, shows the sender's name at weight 600 with the address dimmed, and treats date, recipients, and labels as secondary text. Colour appears only on a flagged star (nord13) and on tag pills. In message bodies, every rule is scoped to Thunderbird's mail-body classes, so the sender's HTML design and web pages stay untouched. Quoted text returns to normal text colour. Each quote level gets a 3 px nord8 bar that fades at each deeper level, on `blockquote type=cite` (Thunderbird, Apple Mail, Fastmail, and plain text) and on Gmail's `gmail_quote`, where only the bar's colour and width change. Yahoo and Outlook quotes stay as they are. Signatures dim to 0.6 in light mode and 0.75 in dark. Plain-text links are nord8 and underlined; Thunderbird's dark-mode link cyan becomes the adjusted nord8.

### Files

The pass touches `thunderbird/nord.css` (new), `customChrome.css`, `customContent.css`, `user.js`, and `README.md`; `bin/.local/bin/thunderbird-theme-sync`, which installs and checks `nord.css`; a new `thunderbird/tools/` with test messages, the screenshot harness, and a contrast check; and one line in `bluefin/SECOND-WORKSTATION.md` Part 3 about clearing old junk marks.

### Out of scope

The sender's HTML design, Outlook and Yahoo quote bars, the compose window, the calendar, the folder pane beyond the colours already set, any layout change besides two-row cards, and poplar's own implementation of the role map.

### The end-to-end check

The harness builds a scratch Thunderbird profile from the test messages, installs the theme with `thunderbird-theme-sync`, and runs Thunderbird headless under Marionette. It screenshots two-row cards and table view in light and dark mode, and the reader on a plain-text reply quoted three levels deep, a Gmail reply, a signature, a link, and a flagged, tagged header. The contrast check confirms every role meets its threshold in both modes. The screenshots go in the PR. Real mail is never touched.

### Risk class and estimate

The pass is `ordinary`: every path sits outside the runner and auth-data maps. The estimate is about 300 path minutes, with the test harness built alongside the palette file.
