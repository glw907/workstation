# Software-tier policy

Install in this order of preference. Each tier down is a deliberate escalation, not a
default.

1. **mise** — Node and other language runtimes it manages. Replaces nvm.
2. **uv** — Python tools and environments (`uv tool install <name>` for CLI tools like
   yt-dlp).
3. **Homebrew** — CLI tools generally, and Go (`brew install go`). Also the fallback
   for a CLI tool with no mise/uv path.
4. **Flatpak** — GUI applications.
5. **distrobox / devcontainers** — isolated dev environments, or a tool that needs a
   different base OS than Fedora.
6. **rpm-ostree layering (`rpm-ostree install`)** — last resort only. Layering a
   package means it survives on the base image and gets rebuilt on every update,
   which is slower and has more failure modes than any tier above. Reach for it only
   when nothing else can provide the package: a system-level binary, a kernel module,
   or a dependency a layered app needs that isn't itself packaged elsewhere (this is
   why `chromium` is layered — see
   below).

kitty is the exception to all of the above: install via the upstream binary installer
into `~/.local/kitty.app`, never layered, never Flatpak (native messaging and
sandboxing concerns don't apply to a terminal, but the upstream installer is simply
the right tier for a self-contained binary app with its own update mechanism).

Homebrew has no Chromium formula/cask on Linux — confirmed dead end, do not
retry `brew install chromium` or similar.

## Every install updates its manifest, same session

Installing anything through any tier is half the job; the other half is recording it,
in the same session, in the manifest that tier owns: `bluefin/Brewfile` (brew),
`bluefin/flatpaks.txt` (flatpak, deliberate installs only), `bluefin/uv-tools.txt`
(uv tools), `bluefin/layered-packages.txt` (layering, via the change-control rule),
`bluefin/stow-packages.txt` (new stow packages), `bluefin/untracked-bin.txt` (a
deliberately untracked `~/.local/bin` binary), `bluefin/distrobox.txt` (a distrobox
container this workstation deliberately maintains, name, base image, and its recreate
command; not yet reconciled by `check-drift`, so this file is the record of intent
until a probe is added). `/etc` changes stage under
`bluefin/etc/` first, per the drift discipline below. `check-drift` reconciles all
of these against the live machine; a weekly user timer (`check-drift.timer`, the
`upkeep` package) notifies on drift, and a session that installed or reconfigured
anything runs `check-drift` before it closes. Lingering is on for the user on both hosts
(`loginctl enable-linger`, Geoff 2026-10-14), so a user timer fires after a logout or a
reboot with no login; `bootstrap.sh` turns it on and `check-drift` reports it off. An install without its manifest line
is drift you created knowingly.

## layered-packages.txt is the source of truth

`~/.dotfiles/bluefin/layered-packages.txt` is the canonical list of what's layered via
`rpm-ostree install` on this machine. As of the migration brief it holds exactly:

```
chromium
```

Before layering anything new, check this file first — if a package isn't already
listed, adding it is a deliberate escalation past every tier above, not a default
move. **Every addition to the layered set gets recorded in both this file and
`docs/MIGRATION-BRIEF.md`** (append to the Decisions or Platform facts section, whichever
fits). A layered package that isn't in this file is drift — reconcile it in one
direction or the other rather than leaving the mismatch.

If this file doesn't exist yet on a fresh checkout, create it with the package
above before layering anything.
