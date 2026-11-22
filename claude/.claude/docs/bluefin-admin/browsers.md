# Browsers

- **Zen Browser** (upstream tarball in `~/.local/zen`) is Geoff's daily browser on
  both hosts (Geoff, 2026-11-21). It is a Firefox fork, so Firefox add-ons install from
  addons.mozilla.org. `bluefin/zen/policies.json`, linked into the install's
  `distribution/` directory, carries every Chromium policy that has a Firefox equivalent
  (the home button, spell-check service, and background mode have none) and installs Proton
  Pass and Floccus. Zen's updater keeps the tarball current and leaves `distribution/`
  alone. `bootstrap.sh` (`setup_zen`) installs it. Claude never
  drives Zen, since Anthropic ships no Firefox build of the Claude extension.
- **Zen's Adwaita theme** is
  [ClixTW/zen-gnome-theme](https://github.com/ClixTW/zen-gnome-theme) (MIT), a userChrome
  stylesheet (Geoff asked for an existing theme, 2026-11-21). Stock Zen already follows the
  desktop's dark scheme, accent, and font; the theme adds Adwaita's surfaces, icons, and
  controls. `setup_zen_theme` clones it to `~/.local/share/zen-gnome-theme` at a pinned
  commit, then links `chrome/userChrome.css`, `chrome/theme`, and `user.js` (from
  `bluefin/zen/user.js`, the three prefs the theme needs) into each Zen profile, replacing a
  `user.js` already there. A profile exists only after Zen's first launch, so a new host
  runs `bootstrap.sh setup` once more after it. Zen updates itself and the pin does not:
  when Zen's chrome looks broken after an update, move the pin (the comment in
  `setup_zen_theme` says how). To go back to stock Zen, take the `setup_zen_theme` call out
  of `setup_zen`, delete each profile's two `chrome/` links and its `user.js` link, and
  reset `zen.theme.content-element-separation` in `about:config`. When icons turn dark on a
  dark background, set the Zen workspace's light or dark mode to match the desktop's.
- **Chromium** (layered RPM) is the development browser and the one Claude Code drives on
  both hosts (Geoff, 2026-11-21). It was pavilion's daily browser from 2026-10-18 until
  then, and Firefox is retired. Its user data directory, `~/.config/chromium`, has one
  profile, `Default`, for development and testing: Geoff checks his development work there
  and Claude Code drives it (the claude-in-chrome native-messaging host and chrome-devtools
  MCP automation). The profile holds no password manager and none of Geoff's daily sign-ins,
  which live in Zen, so automation never runs beside them. Pavilion has had this profile
  since 2026-11-21, when Geoff had his `Geoff` profile removed. On thinkpad-x1 Chromium
  still holds one profile, `Profile 1` (2026-11-21), which carries Proton Pass and Floccus
  beside the Claude extension from before the move to Zen. Until it is replaced the same way
  (BACKLOG #109), a check there that needs a real Chromium click is a `[you]` step.
- **Chromium extensions are installed by hand.** Chromium policy is browser-wide and would
  reach every Chromium on the machine, test browsers included, so no policy force-installs
  an extension. The `Default` profile carries only the Claude extension (Chrome Web Store id
  `fcoeoabgfenejglbffodgkkbkcdhcgfn`). Proton Pass and Floccus live in Zen, where
  `policies.json` installs them. Floccus is the bookmark sync to Geoff's share on orpheus,
  set up per `~/Projects/household-it/docs/systems/bookmarks.md#set-up-floccus-on-a-device`.
  No Chromium profile carries a password manager (no workstation runs 1Password since
  2026-10-19).
- **Flatpak builds of a browser: never.** Claude's native-messaging hosts need to
  reach into the browser process directly; Flatpak's sandbox blocks that. This isn't
  a preference, it's a hard incompatibility — don't suggest a Flatpak browser as a
  fallback.

## Showing Geoff a visual (Geoff, 2026-09-13, every repo)

Before-and-after renders, mockups, screenshots, and HTML pages built for a visual decision
open in Chromium by default, on both hosts, one tab per state, so he can tab between states, zoom,
and compare at full size. Send them as files in the conversation as well only when he is away
from the workstation. Artifacts are one-off tools: they open in Chromium and get no
cross-browser work. Sitting pages and mockups open in Chromium too (Geoff, 2026-10-18). For a page Claude
must drive itself through claude-in-chrome: the extension connects only once Chromium is running,
and it refuses `file://` URLs, so serve the directory from the scratchpad with
`python3 -m http.server <port> --bind 127.0.0.1` and open `http://127.0.0.1:<port>/...`, one
`navigate` plus `tabs_create_mcp` per state. `tabs_create_mcp` can fail transiently while a
tab is being dragged; retry it alone.

Chromium policy files (Kagi search and homepage, the built-in password manager and
autofill turned off, telemetry, and no default-browser prompt, since Zen is the default) are
captured at
`bluefin/etc/chromium-policies/` and installed to `/etc/chromium/policies/managed/`.
Verify on first boot: `chrome://policy` in the layered Chromium lists all
managed policies as active. (The retired Mint-era `chromium-browser.md` carried
deeper verification recipes; it lives in git history, removed 2026-08-30.)
