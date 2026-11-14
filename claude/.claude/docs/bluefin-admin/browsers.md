# Browsers

- **Chromium** (layered RPM) — the daily browser (Geoff, 2026-10-18; Firefox is
  retired). Two profiles split the roles: Geoff browses in his own profile, and
  Claude Code drives the `Default` profile (the claude-in-chrome native-messaging
  host, chrome-devtools MCP automation, and `chromium-shot`), so automation never
  runs beside his sessions or password manager.
- **Extensions are installed by hand, per profile.** Chromium policy is browser-wide
  with no per-profile scope, so no policy force-installs an extension. Geoff's
  profile carries the Proton Pass extension (Chrome Web Store id
  `ghmbeldphafepmbegfdlkpapadhbakde`) and Floccus, the bookmark sync to his share on
  orpheus (id `fnaicdffflnofjppbagibeoednhnbjhg`, set up per
  `~/Projects/household-it/docs/systems/bookmarks.md#set-up-floccus-on-a-device`; on pavilion since 2026-10-21), and never Claude's; the `Default` profile
  carries only the Claude extension. No Chromium profile carries a 1Password
  extension (no workstation runs 1Password since 2026-10-19).
- **Flatpak builds of a browser: never.** Claude's native-messaging hosts need to
  reach into the browser process directly; Flatpak's sandbox blocks that. This isn't
  a preference, it's a hard incompatibility — don't suggest a Flatpak browser as a
  fallback.

## Showing Geoff a visual (Geoff, 2026-09-13, every repo)

Before-and-after renders, mockups, screenshots, and HTML pages built for a visual decision
open in the desktop browser by default, one tab per state, so he can tab between states, zoom,
and compare at full size. Send them as files in the conversation as well only when he is away
from the workstation. Artifacts are one-off tools: they open in Chromium and get no
cross-browser work. Sitting pages and mockups open in Chromium too (Geoff, 2026-10-18). For a page Claude
must drive itself through claude-in-chrome: the extension connects only once Chromium is running,
and it refuses `file://` URLs, so serve the directory from the scratchpad with
`python3 -m http.server <port> --bind 127.0.0.1` and open `http://127.0.0.1:<port>/...`, one
`navigate` plus `tabs_create_mcp` per state. `tabs_create_mcp` can fail transiently while a
tab is being dragged; retry it alone.

Chromium policy files (Kagi search and homepage, the built-in password manager and
autofill turned off, telemetry) are captured at
`bluefin/etc/chromium-policies/` and installed to `/etc/chromium/policies/managed/`.
Verify on first boot: `chrome://policy` in the layered Chromium lists all
managed policies as active. (The retired Mint-era `chromium-browser.md` carried
deeper verification recipes; it lives in git history, removed 2026-08-30.)
