---
name: bluefin-admin
description: Routes workstation admin work on Bluefin DX to the one reference doc it needs. Use before installing software, updating or rolling back the image, editing /etc, changing gsettings, quieting the desktop, fixing an SELinux denial or a restored file's label, capturing a terminal headlessly, checking a phone code, setting up mail clients, or using gws or clasp, on thinkpad-x1 or pavilion.
---

# Bluefin admin

The admin reference for both workstations is an index and 14 leaves. Read the index,
`~/.claude/docs/bluefin-admin.md`, then the one leaf under `~/.claude/docs/bluefin-admin/` that
covers the task. The index gives each leaf a line that says what it covers.

A fact that holds on one host names that host. The SessionStart hook's `## Host` line says which
host this session is on, so never infer it from a doc.

`~/.dotfiles/docs/MIGRATION-BRIEF.md` is the decisions record. It is the authority for anything
the leaves don't cover.
