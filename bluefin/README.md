# Bluefin bootstrap

Provisioning artifacts for a Bluefin DX (stable) workstation: everything a
fresh install needs to reach the working state this repo describes. Decisions
record and fact base: `../docs/MIGRATION-BRIEF.md` (born in the 2026-08 Mint
migration). Read that file first; this directory implements it and does not
repeat its reasoning.

## Quick card: fresh Bluefin to working machine

Every command to type on the new system, in order.

```bash
git clone https://github.com/glw907/workstation.git ~/.dotfiles
~/.dotfiles/bluefin/bootstrap.sh devmode   # answer: yes, no, no
sudo systemctl reboot
~/.dotfiles/bluefin/bootstrap.sh layer
sudo systemctl reboot
~/.dotfiles/bluefin/bootstrap.sh setup
# 1Password app: sign in, then Settings -> Developer -> "Integrate with 1Password CLI"
# FIRST WORKSTATION ONLY, and in a NEW terminal (setup's shell never sourced
# the just-stowed .bashrc, so mise/npx are missing from its PATH):
~/.dotfiles/bluefin/bootstrap.sh restore
claude   # first launch asks you to log in
```

A second workstation stops after `setup`; there is no backup for it to
restore (see "Second workstation" below).

Two reboots, both required. The official ISO installs the non-DX `bluefin`
image; `devmode` rebases to `bluefin-dx` and only takes effect on boot, and
`layer` must run against the image that is actually booted. `layer` and
`setup` both hard-stop if they find themselves on a non-DX image.

`setup` prints a verification checklist at the end; read it before moving on
to `restore`.

## Contents

| File | Purpose |
|------|---------|
| `../docs/MIGRATION-BRIEF.md` | Decisions, verified platform facts, backup state |
| `bootstrap.sh` | `devmode`, `layer`, `setup`, and `restore` phases, run in order below |
| `layered-packages.txt` | The minimal rpm-ostree layered set |
| `flatpaks.txt` | Flatpak app IDs to install |
| `Brewfile` | CLI tool formulae for `brew bundle` |
| `stow-packages.txt` | The Stow packages this repo manages, single source of truth |
| `etc/` | Captured `/etc` drops: chromium policies, android udev rule, 1Password repo |
| `devenv-research.md` | Dev-environment tiering research (devcontainers, distrobox); kept here because site-repo backlogs point at this path |

## Order of operations, fresh install

1. Write the Bluefin ISO with Fedora Media Writer, install to `stable` with
   whole-disk LUKS. Enable "Allow Microsoft 3rd Party UEFI CA" in BIOS
   first. There is no separate DX ISO — the image is unified and installs
   non-DX `bluefin`; DX comes from the `devmode` rebase in step 4.
2. First boot: enroll the MOK (password `universalblue`).
3. Clone dotfiles:
   ```
   git clone https://github.com/glw907/workstation.git ~/.dotfiles
   ```
4. Rebase to the Developer Experience image:
   ```
   ~/.dotfiles/bluefin/bootstrap.sh devmode
   ```
   This wraps `ujust devmode`, which prompts three times: answer **yes** to
   enabling developer mode, then **no** to the default development flatpaks
   and **no** to the extra monospace fonts. Both declines are deliberate.
   Flatpaks come from `flatpaks.txt`, so the second workstation gets the same
   tracked set. The fonts are simply not needed: the base image already ships
   JetBrains Mono and Symbols Nerd Font Mono, which is all `kitty.conf` asks
   for, and Ptyxis uses the system monospace.
5. Reboot into the DX image.
6. Layer packages and add the 1Password repo:
   ```
   ~/.dotfiles/bluefin/bootstrap.sh layer
   ```
7. Reboot (the layered packages need the new deployment applied).
8. Run the rest of setup:
   ```
   ~/.dotfiles/bluefin/bootstrap.sh setup
   ```
   Read the verification checklist it prints at the end before moving on.
9. Selective restore from the encrypted backup:
   ```
   ~/.dotfiles/bluefin/bootstrap.sh restore
   ```
   This decrypts the backup, verifies its checksum, and selectively restores
   `$HOME` content, with hard stops on a dirty dotfiles checkout or a
   checksum mismatch. It prints a checklist at the end covering the judgment
   calls that remain: re-authentication, verification, and diffing the
   restored `~/.local/bin` against the `bin` Stow package.

## Second workstation

This same directory provisions the second workstation arriving a few weeks
after thinkpad-x1: same ISO, same `bootstrap.sh devmode` / `layer` / `setup`
sequence, same package lists. A custom uBlue image is a later decision point,
not assumed here — though note that a custom image is the standard way to
avoid the devmode rebase and the Flatpak removals below, by baking both into
the image instead of undoing them per machine.

The second workstation is `pavilion`, an HP desktop. `SECOND-WORKSTATION.md`
is its runbook: the human steps, the Claude-run steps that stand in for
`restore`, and the handoff bundle that carries laptop-only state.

## Changing the layered package set

`layered-packages.txt` stays minimal by design. Before adding a package to
it, record the reason in `../docs/MIGRATION-BRIEF.md`. That file is the source the
list is curated from, not the other way around.

## Android

The SDK lives in `~/Android/`, outside this repo, and is not Stow-managed.
`bin/.local/bin/update-android-sdk` checks it for platform-tools, build-tools,
and platform updates via `sdkmanager`. `workstation-update` runs its own
equivalent `sdkmanager --update` step; the two do not invoke each other.

USB device access (adb, fastboot) is granted through `etc/udev/51-android.rules`,
staged here and installed to `/etc/udev/rules.d/` by `setup_etc_drops` during
`bootstrap.sh setup`. It tags matching devices `uaccess` rather than adding a
`plugdev` group membership: Bluefin has no `plugdev` group, and `uaccess` is
the systemd-native equivalent, granting access to the user at the active
console session.
