# Bluefin DX admin reference

Standing reference for administering the Bluefin DX system (stable stream, Fedora 44
base). Read this before installing software, editing `/etc`, running an update,
touching browser configuration, installing or receiving a secret, or using `gws` on
either workstation. It covers both `thinkpad-x1` (laptop) and `pavilion` (desktop); a fact
that holds on one host only names that host, and `bluefin/SECOND-WORKSTATION.md` records
pavilion's differences.

The Mint-era `chromium-browser.md` was retired 2026-08-30 (recoverable from git
history); this file's Browsers section is the authority. The old file's
telemetry-policy reasoning still holds, since the same JSON policy files carried
over unchanged.

Decisions record and fact base: `~/.dotfiles/docs/MIGRATION-BRIEF.md`. Treat that
file as authoritative for anything this doc doesn't cover.

The sections below moved word for word into one file each under `~/.claude/docs/bluefin-admin/`. Read the file for
your task; a reference by old section name (`bluefin-admin.md "Secrets"`) finds it in this list.

- Software-tier policy: `~/.claude/docs/bluefin-admin/software-tiers.md`. Covers the install-tier order, the rule that every install updates its manifest the same session, and layered-packages.txt as the source of truth.
- Command map: `~/.claude/docs/bluefin-admin/command-map.md`. Covers which command updates, installs, and inspects the system image, Flatpaks, and Homebrew.
- /tmp is a quota'd tmpfs: `~/.claude/docs/bluefin-admin/tmp.md`. Covers the 8G tmpfs quota and what to keep out of it.
- Calm desktop (Geoff, 2026-09-29): `~/.claude/docs/bluefin-admin/calm-desktop.md`. Covers the rule that only critical items interrupt, and how to keep the desktop quiet.
- gsettings: always /usr/bin/gsettings: `~/.claude/docs/bluefin-admin/gsettings.md`. Covers why Homebrew's gsettings has no dconf module and which binary to call.
- Update cadence and rollback: `~/.claude/docs/bluefin-admin/update-cadence.md`. Covers the 6-hour update check, applying at reboot, and rollback.
- /etc drift discipline: `~/.claude/docs/bluefin-admin/etc-drift.md`. Covers landing every `/etc` change in `bluefin/etc/` first, then installing it.
- Browsers: `~/.claude/docs/bluefin-admin/browsers.md`. Covers Chromium profiles, policy files, extensions, and showing a visual.
- Headless real-terminal capture: `~/.claude/docs/bluefin-admin/terminal-capture.md`. Covers `kitty-headless-shot` and the `term-headless` distrobox.
- SELinux for restored data: `~/.claude/docs/bluefin-admin/selinux.md`. Covers relabeling data restored into the home directory.
- Secrets: installing, receiving, and Proton Pass: `~/.claude/docs/bluefin-admin/secrets.md`. Covers installing and receiving secrets, `claude-pass`, and the store-check order.
- Phone checks without a phone (Geoff, 2026-10-29): `~/.claude/docs/bluefin-admin/phone-checks.md`. Covers `phone-check` and the voip.ms number that stands in for a phone.
- Google Workspace (gws, clasp): `~/.claude/docs/bluefin-admin/google-workspace.md`. Covers `gws` and `clasp`: tools, tokens, scopes, and sign-ins.
- Email: `~/.claude/docs/bluefin-admin/email.md`. Covers the household's Stalwart mail on ward and how clients reach it.
