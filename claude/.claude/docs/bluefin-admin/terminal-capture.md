# Headless real-terminal capture

`kitty-headless-shot` (`bin/.local/bin/`, stowed) drives a real kitty terminal on an
Xvfb display that exists only inside the `term-headless` distrobox (`bluefin/distrobox.txt`),
so a TUI capture never opens a window on the live desktop or steals focus. It is the
general-purpose primitive; the `standards:tui-visual-verify` skill calls it directly.
`kitty-headless-shot --help` is the spec. Run
`kitty-headless-shot setup` once per machine to create the box (idempotent); this is
the first deliberate use of the distrobox tier on this workstation, so it is also the
precedent: a container is the right home for an X/Wayland server, Mesa, and
ImageMagick when the host's own copies can't do the job headless (the host's
ImageMagick has no X11 delegate wired up).

A live-desktop capture does work (verified 2026-09-29): call
`org.freedesktop.portal.Screenshot.Screenshot` with `interactive: false` and wait for
the `Request.Response` signal. The permission store already grants unsandboxed apps
(`flatpak permissions screenshot`), so no prompt appears. It captures the whole screen
and saves a numbered `Screenshot-` PNG in `~/Pictures`, so move the file out
afterward. GNOME focus-stealing prevention stops a script from raising a window, so
ask Geoff to bring the window forward and take one capture after he confirms. Never
run a capture loop: he asked for it to stop.
