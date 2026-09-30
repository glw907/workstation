# Thunderbird GNOME theme layer

Thunderbird is the interim desktop mail client for Fastmail until poplar is
ready. It runs as the Flathub Flatpak `org.mozilla.thunderbird`, on the monthly
release channel, and signs in to Fastmail with OAuth. It is styled with the
[Thunderbird GNOME theme](https://github.com/rafaelmardojai/thunderbird-gnome-theme),
a CSS theme that makes it look like a libadwaita app.

This folder holds the local layer on top of that theme. It is data, not a stow
package: `thunderbird-theme-sync` copies it into the Thunderbird profile.

| Path | Contents |
|------|----------|
| `customChrome.css` | Color overrides for the main window, mapping Thunderbird's own colors onto the GNOME palette and the desktop accent |
| `customContent.css` | The same palette for Settings, the address book, and account settings, which load as content pages that `userChrome.css` never reaches |
| `user.js` | Preferences Thunderbird applies at every startup: the two the theme needs, plus the Adwaita tag colors |
| `patches/*.patch` | Fixes carried until the theme merges them upstream; each file's header names its upstream PR |

## How it fits together

The theme is plain CSS. Its installer copies it into the profile's `chrome/`
folder and writes a `user.js`, which the sync replaces with the one here. The
theme imports `customChrome.css`
last and never ships one. It has no such hook for content pages, so the sync
writes the profile's `userContent.css` itself, importing the theme and then
`customContent.css`. `customContent.css` scopes every rule to Thunderbird's own
pages with `@-moz-document`, so email bodies keep their own colors.
Thunderbird updates don't touch the profile at all.

| Location | Role |
|----------|------|
| `~/.dotfiles/thunderbird/` | Source of truth for the local layer (this folder) |
| `~/.local/share/thunderbird-gnome-theme/` | Working clone of the upstream theme; disposable, since the sync resets it |
| `~/.var/app/org.mozilla.thunderbird/.thunderbird/<profile>/chrome/` | What Thunderbird actually loads |

## Setting up a new machine

A Thunderbird profile exists only after the first launch, and the account
itself can't live in dotfiles: it's an OAuth sign-in, and the mail is on
Fastmail. `bootstrap.sh setup` installs the monthly Flatpak from
`bluefin/flatpaks.txt` and removes the ESR build that Bluefin's stock app
list brings. Its checklist then walks through the rest:

1. Launch Thunderbird. Enter `geoff@907.life`, confirm OAuth2, and sign in on
   Fastmail's page with the main password and 2FA.
2. Link calendars: in the Calendar tab, click **Add Calendar…**, choose **On
   the Network**, enter `geoff@907.life` and `caldav.fastmail.com`, click
   **Find Calendars**, then **Subscribe**.
3. Link contacts: in the Address Book tab, choose **New Address Book** > **Add
   CardDAV Address Book**, enter `geoff@907.life` and `carddav.fastmail.com`,
   then **Continue**.
4. Quit Thunderbird (Ctrl+Q; closing the window can leave it running in the
   background) and run `thunderbird-theme-sync`.

## Common tasks

To change a color:

1. Edit `customChrome.css` or `customContent.css` here.
2. Quit Thunderbird.
3. Run `thunderbird-theme-sync`.
4. Start Thunderbird. It reads the CSS only at startup.

To change a preference such as a tag color, edit `user.js` here, quit
Thunderbird, and run `thunderbird-theme-sync`. Thunderbird rereads `user.js`
at every startup, so a value set there wins over a change made in Settings.

To pick up upstream theme fixes, or to repair the look after a Thunderbird
update, quit Thunderbird and run `thunderbird-theme-sync`. It resets the clone
to upstream `main`, applies each carried patch, reinstalls the theme, and copies
both override files and `user.js` in. `workstation-update` runs it too.

To check the install without changing anything, run
`thunderbird-theme-sync --check`. `check-drift` runs the same check weekly.

## Carried patches

When the sync prints `Merged upstream, delete it`, the fix has landed upstream:
delete that patch file and commit. When it prints `Patch no longer applies`,
upstream changed the same lines; rebase the patch on the new `main` or drop it.

## Finding the right variable

Thunderbird's own CSS lives in `omni.ja` inside the Flatpak. To search it:

```sh
omni="$(flatpak info --show-location org.mozilla.thunderbird)/files/lib/thunderbird/omni.ja"
unzip -qo "$omni" '*.css' -d /tmp/tb-css
grep -rn -- '--new-subject-color' /tmp/tb-css
```

Prefer overriding a variable over restyling a selector. Most variables live on
`:root`, but some are set on an inner element, such as a thread row. Override
those on the same element. Shadow-DOM `:host` rules lose to a variable set on
the host element from `customChrome.css`.

To inspect the live UI, open Tools > Developer Tools > Developer Toolbox. It
asks to allow remote debugging the first time.

## Upstream contributions

A fix that belongs in the theme itself, such as an element the theme forgot to
restyle, goes upstream as a pull request. Carry it in `patches/` until it
merges. Taste choices stay in `customChrome.css`.
