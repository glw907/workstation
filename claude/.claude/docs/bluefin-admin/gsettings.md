# gsettings: always /usr/bin/gsettings

Homebrew's `glib` (a dependency of cairo, ffmpeg, and others, so it stays) puts
its own `gsettings` first on PATH. That build has no dconf module, so every
`set` silently lands in a GLib keyfile under `~/.config/glib-2.0/`, which the desktop <!-- host-ok -->
never reads, and every `get` reads the same keyfile back, so a check looks
green while the live desktop is unchanged. Found 2026-09-29, when the manifest's
AC-suspend setting had never applied. Call `/usr/bin/gsettings` by full path.
`bootstrap.sh` and `check-drift` do. To confirm a value really landed, read it
with `dconf read`. A schema that ships inside a GNOME Shell extension, such as
dash-to-dock, also needs `--schemadir` pointing at the extension's `schemas/`
folder; both scripts find it automatically.
