# Second workstation runbook: pavilion

This runbook takes an HP Pavilion desktop from a blank disk to a mirror of
thinkpad-x1. The one deliberate difference is laptop lid handling. It extends
the quick card in `README.md` and replaces the `restore` phase for this
machine; never run `bootstrap.sh restore` here, since it pulls the 2026-08
Mint-era snapshot.

The work splits in two. Part 1 is Geoff at the keyboard: the installer, the
bootstrap phases that need a password or a GUI, and the logins that only a
person can do. Part 2 is a Claude Code session on the new machine, started
from `~/.dotfiles` with the prompt "Follow bluefin/SECOND-WORKSTATION.md part
2." Part 3 returns to Geoff for the browser and app sign-ins.

## Decisions this runbook carries

These were settled with Geoff on 2026-10-12. Follow them, don't reopen them.

| Item | Decision |
|---|---|
| Hostname | `pavilion` |
| Username | `glw907`, so every `/var/home/glw907` path, Claude memory key, and the GDM auto-login file carry over unchanged |
| Image | `bluefin-stable-x86_64.iso`, Intel/AMD build, then the `devmode` rebase to DX |
| Lid handling | Not installed. `bluefin/etc/systemd/logind.conf.d/10-lid-ignore.conf` is laptop-only, and no phase installs it |
| Awake hooks | Kept. `claude-awake-holder` finds no battery and never trips its floor; the inhibitors still block idle suspend |
| GDM auto-login | Mirrored from the laptop (LUKS guards the disk) |
| Laptop-only state | Arrives in an age-encrypted handoff bundle on R2, built on thinkpad-x1 |
| Credentials | Machine-owned ones are minted fresh: SSH key, `gh` login, gws user token. Tokens in the shared age store stay shared |

## The handoff bundle

thinkpad-x1 built the bundle on 2026-10-12. It holds what git and the
bootstrap cannot carry. That includes the Claude memory directories, the
three repos with no remote (`healthy-diet`, `personal-styles`, `pings`), the
local folders `cairn-scratch`, `ecxc-ski-agent-memory`, and
`aksailingclub-sveltekit`, the ASC age key, the `jrnl-md` config, and
`Documents`, `Pictures`, and `corpus`. A `manifest.txt` at the root lists
every path.

The tarball is encrypted to the workstation age key, the same key `restore`
checks (`age197mcd2m3z90t49n9t5v3ujjntw7krfkw5y9sjfc545v28qvezugshg7jgk`).
It is split into four chunks in R2:

```
workstation-backup/pavilion-handoff/chunk-aa
workstation-backup/pavilion-handoff/chunk-ab
workstation-backup/pavilion-handoff/chunk-ac
workstation-backup/pavilion-handoff/chunk-ad
workstation-backup/pavilion-handoff/handoff.sha256
```

The reassembled `handoff.tar.age` has SHA-256
`88caf6651cf0c0c8dd4775e8e5fca6a0f60afa508a6469e344fddbfde50debae`. A
mismatch is a hard stop: never decrypt an unverified blob.

## Part 1: Geoff, installer to first Claude session

1. Boot the installer stick from the Pavilion's USB-C port (F9 at the HP
   logo). Install Bluefin to the whole disk with LUKS encryption. Create the
   user `glw907`.
2. First boot: enroll the MOK with the password `universalblue`.
3. Clone the dotfiles and run the first two bootstrap phases, rebooting after
   each:
   ```bash
   git clone https://github.com/glw907/workstation.git ~/.dotfiles
   ~/.dotfiles/bluefin/bootstrap.sh devmode   # answer: yes, no, no
   sudo systemctl reboot
   ~/.dotfiles/bluefin/bootstrap.sh layer
   sudo systemctl reboot
   ~/.dotfiles/bluefin/bootstrap.sh setup
   ```
   Read the checklist `setup` prints. A failed step there is worth fixing
   before Part 2.
4. Open the 1Password app and sign in. Turn on Settings > Developer >
   "Integrate with 1Password CLI".
5. Open a NEW terminal, so the stowed `.bashrc` is loaded, and run:
   ```bash
   claude-sudo-setup
   gh auth login        # GitHub.com, HTTPS, browser login
   cd ~/.dotfiles && claude
   ```
   Log in to Claude when asked, then give it the prompt "Follow
   bluefin/SECOND-WORKSTATION.md part 2."

## Part 2: Claude on pavilion

Run these in order. Each step is safe to rerun. Use `sudo -A` throughout; if
it fails, rerun `claude-sudo-setup`. Report a failed step and carry on with
the rest unless the step says it is a hard stop.

1. Confirm the starting state. `bootc status` must show a `bluefin-dx`
   image, `sudo -A true` must succeed, and `op whoami` must answer. Any
   failure here is a hard stop: hand it back to Geoff.
2. Set the hostname:
   ```bash
   sudo -A hostnamectl set-hostname pavilion
   ```
3. Write the local secrets and enable the timer that waits on them:
   ```bash
   ~/.dotfiles/scripts/secrets/sync.sh --local
   source ~/.local/secrets
   systemctl --user enable --now vdirsyncer.timer
   ```
4. Install the staged `/etc` drops that `setup` leaves out. Skip the lid
   file.
   ```bash
   E=~/.dotfiles/bluefin/etc
   sudo -A install -m 644 "$E/gdm/custom.conf" /etc/gdm/custom.conf
   sudo -A install -D -m 644 "$E/systemd/user.conf.d/10-oom-continue.conf" \
       /etc/systemd/user.conf.d/10-oom-continue.conf
   sudo -A install -D -m 644 "$E/systemd/zram-generator.conf.d/10-larger-zram.conf" \
       /etc/systemd/zram-generator.conf.d/10-larger-zram.conf
   sudo -A ln -sf /dev/null /etc/systemd/system/systemd-remount-fs.service
   sudo -A systemctl daemon-reload
   ```
   The zram size formula scales with RAM and caps at 20 GB, so it needs no
   change for the desktop. The new size takes effect at the next boot.
5. Fetch, verify, and unpack the handoff bundle:
   ```bash
   S=~/handoff-staging; mkdir -p "$S"
   export CLOUDFLARE_ACCOUNT_ID=120c269ad6d3dfbe6d63a0bb53758ca0
   for c in aa ab ac ad; do
       [ -s "$S/chunk-$c" ] || npx -y wrangler r2 object get --remote \
           "workstation-backup/pavilion-handoff/chunk-$c" --file "$S/chunk-$c"
   done
   cat "$S"/chunk-a? > "$S/handoff.tar.age"
   echo "88caf6651cf0c0c8dd4775e8e5fca6a0f60afa508a6469e344fddbfde50debae  $S/handoff.tar.age" \
       | sha256sum -c -
   ```
   Stop here if the checksum fails. Otherwise decrypt with the cached key
   that step 3 left in tmpfs, then place the files without overwriting
   anything that already exists:
   ```bash
   mkdir -p "$S/x"
   age -d -i /dev/shm/.age-key-$UID "$S/handoff.tar.age" | tar -x -C "$S/x"
   cat "$S/x/manifest.txt"
   rsync -a --ignore-existing --exclude=manifest.txt "$S/x/" ~/
   chmod 600 ~/.config/age/asc-key.txt
   sudo -A restorecon -R /var/home/glw907
   rm -rf "$S"
   ```
6. Clone the GitHub repos into `~/Projects` and link the dotfiles under their
   repo name:
   ```bash
   cd ~/Projects
   for r in 907-life aksailingclub-legacy aksailingclub-org cairn-cms cairn-pub \
            cairn-themes displaywidth drafter dubplate ecxc-ski phonebook poplar \
            xcathletes-org; do
       [ -d "$r" ] || git clone "https://github.com/glw907/$r.git"
   done
   ln -sfn ~/.dotfiles ~/Projects/workstation
   ```
   On the laptop `dubplate` uses an SSH remote. Step 7 switches it once the
   new key is registered.
7. Mint this machine's SSH key and register it with GitHub:
   ```bash
   [ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519 -C "glw907@pavilion" -N "" -f ~/.ssh/id_ed25519
   gh ssh-key add ~/.ssh/id_ed25519.pub --title pavilion
   git -C ~/Projects/dubplate remote set-url origin git@github.com:glw907/dubplate.git
   ```
   If `gh` lacks the `admin:public_key` scope, ask Geoff to run
   `gh auth refresh -s admin:public_key` and retry.
8. Build the local binaries the laptop carries outside the stow tree:
   ```bash
   make -C ~/Projects/poplar install
   make -C ~/Projects/drafter install
   ```
   If either repo has no `install` target, read its README for the build
   step. Leave the rest of `bluefin/untracked-bin.txt` (NumberLink, harper-ls,
   marksman, odin4, perfspike, samfusdl) uninstalled unless Geoff asks for
   them. check-drift only flags unlisted binaries, never missing ones.
9. Turn on the remaining user services:
   ```bash
   systemctl --user enable --now cairn-tripwire.timer
   kitty-headless-shot setup
   ```
   The second line builds the `term-headless` distrobox that the
   `tui-visual-verify` gate uses.
10. Verify. Run `check-drift` and `claude-tooling-sync verify`, then confirm
    each of these: `gh auth status`, `systemctl --user list-timers` shows
    check-drift, model-review, vdirsyncer, and cairn-tripwire,
    `hostnamectl` shows `pavilion`, and `ls ~/.claude/projects/*/memory`
    lists the carried memory. Fix any drift that a step above should have
    covered. Report the rest to Geoff with the Part 3 list.

## Part 3: Geoff, sign-ins

1. `gws auth login -s docs,drive`. This mints the machine's own gws user
   token; the OAuth client pair came from the age store in step 3.
2. In Chromium, sign in, install the Claude extension, and confirm it
   connects to Claude Code. Confirm the 1Password extension connects too. If
   it doesn't, see the GID gotcha in `bluefin-admin.md`.
3. In Thunderbird, sign in to Fastmail with OAuth, then run
   `thunderbird-theme-sync`.
4. Optional: install the Android SDK (see `README.md`, Android) and pair
   Syncthing at `http://127.0.0.1:8384`.
5. Reboot once, so the zram and OOM drops take effect, and confirm GDM logs
   straight in.

## After pavilion is up

Delete the handoff bundle from R2. It holds a copy of the ASC age key.

```bash
for k in chunk-aa chunk-ab chunk-ac chunk-ad handoff.sha256; do
    npx -y wrangler r2 object delete --remote "workstation-backup/pavilion-handoff/$k"
done
```
