# Calm desktop (Geoff, 2026-09-29)

The desktop is calm and low-distraction by default: nothing interrupts unless
it's critical. Keep it that way in every change.

- Do Not Disturb stays on. GNOME Shell still shows critical-urgency
  notifications, so critical is the only level that interrupts. Nothing shows
  on the lock screen.
- The dock shows no unread badges or notification counters, and no icon
  wiggles for attention.
- A new app gets its own interruptions turned off at install: new-item popups,
  sounds, unread badges, tray nags, and "what's new" or start pages. Record the
  setting where the app's config lives (a Chromium preference goes in
  `bluefin/etc/chromium-policies/`).
- A script that notifies uses normal urgency for routine news, which lands
  silently in the notification list. Reserve `--urgency=critical` for things
  Geoff must act on now, such as a released sleep hold or a failure that loses
  work. Never repeat or loop a notification, and never add sound.
- Colors stay muted: GNOME's palette, with the slate accent as the only
  highlight.
- Desktop settings go in `bluefin/gnome-settings.txt`, applied with
  `/usr/bin/gsettings` (see the next section).
