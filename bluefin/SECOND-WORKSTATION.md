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
| Username | `glw907`, so every `/var/home/glw907` path and Claude memory key carry over unchanged |
| Image | `bluefin-dx-nvidia-open:stable` for the GTX 1660 Super. The install used the Intel/AMD ISO, so Part 1 switches images in place of the `devmode` rebase |
| Lid handling | Not installed. `bluefin/etc/systemd/logind.conf.d/10-lid-ignore.conf` is laptop-only, and no phase installs it |
| Host identity | Shared files name no single host. The global CLAUDE.md and `bluefin-admin.md` cover both machines, and a fact true on one host names that host. The SessionStart hook (`~/.claude/gather-dotfiles.sh`) prints a `## Host` line from `hostname` and the DMI product name, so a session reads its host from the machine, never from a doc. Added 2026-10-13, after a pavilion session took the old "Workstation: thinkpad-x1" header at its word and reasoned about laptop RAM |
| Awake hooks | Kept. `claude-awake-holder` finds no battery and never trips its floor; the inhibitors still block idle suspend |
| GDM auto-login | Off on pavilion since 2026-10-17. The disk unlocks through the TPM so the desktop boots without a cabled keyboard, and the GDM password is the credential gate. The machine is a desktop in Geoff's home office. Install `gdm/custom.conf.pavilion`, never the laptop's `gdm/custom.conf` |
| Laptop-only state | Arrives in an age-encrypted handoff bundle on R2, built on thinkpad-x1 |
| Credentials | Machine-owned ones are minted fresh: SSH key, `gh` login, gws user token. Tokens in the shared age store stay shared |

## Hardware

The machine is an HP Pavilion Gaming Desktop TG01-2xxx: 32 GB of DDR4
in two slots (64 GB maximum, as 2×32 GB), a 512 GB NVMe SSD, a 32 GB Intel Optane module,
and an Nvidia GTX 1660 Super, on BIOS F.24. Three things blocked the
2026-10-12 install, and a fourth hung most boots afterwards. A reinstall hits
all four again.

The add-in Wi-Fi card, an Intel Wireless-AC 7265 on a PCIe slot adapter,
stops answering under Linux. It hangs `lspci`, the installer, shutdown, and
boot, and `pcie_aspm=off` does not help. It stays out of the machine; the
onboard Wi-Fi works.

The SSD was paired with Optane, which hid it from the installer. The fix was
to disable Optane in Windows with the Intel Optane Memory and Storage
Management app. The firmware's SATA Emulation setting stays greyed out on
RAID, and the installer works with it there. UEFI HII Configuration > Intel
Rapid Storage Technology confirms the result: two non-RAID physical disks.

Leftover Windows and Optane signatures then hung the installer's storage
scan. `wipefs -a` on the SSD's partitions, the SSD, and the Optane module
cleared them. Install to the 476.9 GB SSD only and leave the 27.2 GB Optane
module unused.

The BIOS then crashed about seven boots in ten at the Bluefin loading screen.
HP's power-off method for the third LPSS I2C controller, `I2C3._PS3`, calls
`SOD3 (IC03, …)`. `IC03` should be an address from the DSDT's NVS fields, but a
96-byte HP SSDT declares `Device (\_SB.PC00.IC03)`, which shadows it from
I2C3's scope. The method aborts on every boot. On most boots the aborted
method also corrupts the kernel's ACPI object cache, which surfaces as
`kernel BUG at mm/slub.c` from whichever driver evaluates ACPI next. Device
setup then stalls and Wi-Fi never appears. Kernel bugzilla 221847 reports the
same collision on the same model, unfixed as of 2026-10-13.

Nothing is attached to the three LPSS I2C controllers, so the fix keeps their
driver from loading. A PCI device with no driver is never powered down, so
`_PS3` never runs. The driver is built into Fedora's kernel, so it takes
`initcall_blacklist`, not `module_blacklist`. The boot arguments are in Part
1 step 3. The `hp_wmi` blacklist came from an earlier, wrong diagnosis. It
stays because HP's WMI methods also throw AML errors and nothing on the
desktop needs them. A BIOS update is not known to fix the collision; the
bugzilla reporter saw it on F.21 and F.24. To check a new BIOS, dump the
tables and look for `Device (IC03)` in a small SSDT.

## The handoff bundle

thinkpad-x1 built the bundle on 2026-10-12. It holds what git and the
bootstrap cannot carry. That includes the Claude memory directories, the
ASC age key, and `Documents`, `Pictures`, and `corpus`. A `manifest.txt` at
the root lists every path. The repos and folders it once carried besides
these are retired, and the 2026-10-14 repo organization pass archived them.

The 2026-10-12 bundle missed two things, found on pavilion the next day.
A future bundle carries them too:

- `~/.local/share/cairn/`: cairn's 69 exemplar captures (90 MB).
- `~/.config/fastmail/fastmail-dav-token.age`: a token since retired; contacts
  now come from ward through GNOME Online Accounts.

On pavilion they came across on 2026-10-13 with `rsync` from thinkpad-x1
over a temporary SSH opening: a Remote Control session on the laptop
appended pavilion's public key to `~/.ssh/authorized_keys` and ran
`sudo systemctl start sshd`, pavilion pulled, then the laptop stopped sshd
and removed the key. To find other gaps, compare
`ls ~/.local/share ~/.config` on both machines.

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
   user `glw907`. Keep the Keychron K3 on its USB cable until part 2 step 4
   enrolls the TPM: a Bluetooth keyboard can't type the disk passphrase at
   boot.
2. Enroll the Universal Blue signing key so the Nvidia modules still load if
   a BIOS reset turns Secure Boot on. With Secure Boot off, first boot shows
   no prompt, so queue the key by hand. The next boot shows the blue MOK
   screen: choose Enroll MOK, Continue, Yes, and the password `universalblue`.
   ```bash
   ujust enroll-secure-boot-key
   ```
3. Clone the dotfiles, switch to the Nvidia DX image, and run the bootstrap
   phases, rebooting where shown. The `rpm-ostree rebase` line replaces
   `bootstrap.sh devmode`, which would rebase to the non-Nvidia DX image. It
   keeps layered packages, so it also works after `layer` has run. The
   `kargs` line adds two sets of boot arguments. The first four come from the
   Nvidia image's `/usr/lib/bootc/kargs.d/00-nvidia.toml`, which `bootc
   switch` applies and `rpm-ostree rebase` ignores. The last two are the BIOS
   workarounds from Hardware above. The rebase, `layer`, and `kargs` all stage
   onto the same pending deployment, so one reboot covers them:
   ```bash
   git clone https://github.com/glw907/workstation.git ~/.dotfiles
   sudo rpm-ostree rebase ostree-image-signed:docker://ghcr.io/ublue-os/bluefin-dx-nvidia-open:stable
   ~/.dotfiles/bluefin/bootstrap.sh layer
   sudo rpm-ostree kargs \
       --append-if-missing=rd.driver.blacklist=nouveau \
       --append-if-missing=modprobe.blacklist=nouveau \
       --append-if-missing=nvidia-drm.modeset=1 \
       --append-if-missing=initcall_blacklist=simpledrm_platform_driver_init \
       --append-if-missing=module_blacklist=hp_wmi,hp_bioscfg \
       --append-if-missing=initcall_blacklist=intel_lpss_pci_driver_init
   rpm-ostree kargs     # confirm all six are staged
   sudo systemctl reboot
   ~/.dotfiles/bluefin/bootstrap.sh setup
   ```
   After the reboot, `journalctl -b -k | grep -c SOD3` should print 0. Read
   the checklist `setup` prints. A failed step there is worth fixing before
   Part 2.

   Don't install or launch Claude Code before `setup`. A `claude-code` cask
   installed by hand blocks the Brewfile's `claude-code@latest`. A first
   launch also creates a real `~/.claude/skills` directory, which stops stow
   linking the repo's skills as one directory. If either happened, uninstall
   the cask, move `~/.claude/skills` aside, and rerun `setup`.
4. Create the host's Proton agent token. In a throwaway `pass-cli` session, Geoff
   runs `pass-cli agent create pavilion-scripts --expiration 3m --vault
   Workstation` (viewer role on that vault only), then runs
   `ws-pass-key --store` and enters the token in the hidden dialog. In the
   same session he creates Claude's own agent with `pass-cli agent create
   pavilion-claude --expiration 3m` and grants it each vault Claude may edit
   with `pass-cli agent access grant pavilion-claude --vault-name V --role
   editor` (`Servers emergency` and `Workstation` to start). He stores its
   token with `secret-tool store --label "Proton Pass claude agent" service
   proton-pass-agent-claude host pavilion`. Claude then reaches Proton Pass
   only through `claude-pass` (Geoff, 2026-10-20).
5. Open a NEW terminal, so the stowed `.bashrc` is loaded, and run:
   ```bash
   claude-sudo-setup
   gh auth login --hostname github.com --git-protocol https --web \
       --scopes admin:public_key
   cd ~/.dotfiles && claude --chrome
   ```
   `gh` prints a one-time code in the terminal; enter it at the page the
   browser opens. The extra scope lets Part 2 register the SSH key without a
   second login. Starting Claude with `--chrome` writes the native-messaging
   host that the Chromium extension needs in Part 3. Log in to Claude when
   asked, then give it the prompt "Follow bluefin/SECOND-WORKSTATION.md
   part 2."

## Part 2: Claude on pavilion

Run these in order. Each step is safe to rerun. Use `sudo -A` throughout; if
it fails, rerun `claude-sudo-setup`. Report a failed step and carry on with
the rest unless the step says it is a hard stop.

1. Confirm the starting state. `rpm-ostree status` must show the booted
   deployment on `bluefin-dx-nvidia-open`, `sudo -A true` must succeed, and
   `ws-pass-key --status` must print `path=proton`. Any failure here is a hard
   stop: hand it back to Geoff. `bootc status` shows no image once packages
   are layered.
2. Set the hostname:
   ```bash
   sudo -A hostnamectl set-hostname pavilion
   ```
3. Write the local secrets, then add ward as a GNOME Online Accounts account for contacts and
   calendars: Settings, Online Accounts, Calendar, Contacts and Files, server
   `https://mail.907.life`, user `geoff@907.life`, the password from `907.life mail: geoff` in
   the Workstation vault, then turn Files off. Leave only Personal (contacts and calendar) and
   Global Address Book enabled.
   ```bash
   ~/.dotfiles/scripts/secrets/sync.sh --local
   ```
4. Install the staged `/etc` drops that `setup` leaves out. Skip the lid
   file.
   ```bash
   E=~/.dotfiles/bluefin/etc
   sudo -A install -m 644 "$E/gdm/custom.conf.pavilion" /etc/gdm/custom.conf
   sudo -A install -D -m 644 "$E/systemd/user.conf.d/10-oom-continue.conf" \
       /etc/systemd/user.conf.d/10-oom-continue.conf
   sudo -A install -D -m 644 "$E/systemd/zram-generator.conf.d/10-larger-zram.conf" \
       /etc/systemd/zram-generator.conf.d/10-larger-zram.conf
   sudo -A ln -sf /dev/null /etc/systemd/system/systemd-remount-fs.service
   sudo -A install -m 644 "$E/bluetooth/main.conf" /etc/bluetooth/main.conf
   sudo -A install -m 644 "$E/modprobe.d/btusb-no-autosuspend.conf" \
       /etc/modprobe.d/btusb-no-autosuspend.conf
   sudo -A systemctl daemon-reload
   ```
   The zram size formula scales with RAM and caps at 20 GB, so it needs no
   change for the desktop. The new size takes effect at the next boot.
   The two Bluetooth files are pavilion-only. They keep the Keychron K3's
   reconnect after idle sleep fast (Geoff, 2026-10-17).
   Then enroll the TPM so the disk unlocks without a keyboard. It asks for
   the disk passphrase, so Geoff runs it in a terminal:
   ```bash
   sudo systemd-cryptenroll --tpm2-device=auto --tpm2-pcrs=7 \
       "/dev/disk/by-uuid/$(xargs -n1 -a /proc/cmdline | sed -n 's/^rd.luks.uuid=luks-//p')"
   ```
   The passphrase keyslot stays as the fallback. A BIOS update or a Secure
   Boot change alters PCR 7, and the next boot asks for the passphrase on a
   cabled keyboard. Re-run the command after that boot.
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
            cairn-themes dubplate ecxc-ski phonebook poplar; do
       [ -d "$r" ] || git clone "https://github.com/glw907/$r.git"
   done
   ln -sfn ~/.dotfiles ~/Projects/workstation
   ```
   On the laptop `dubplate` uses an SSH remote. Step 7 switches it once the
   new key is registered.

   Claude Code trusts each project directory separately, and a background
   session (`claude --bg`) can't show the trust prompt: it exits with
   "Workspace not trusted". Geoff runs `claude` once in each repo a
   background session will start in, accepts the prompt, and exits. On
   2026-10-13 this blocked the drafter conductor's first launch.
7. Mint this machine's SSH key and register it with GitHub:
   ```bash
   [ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519 -C "glw907@pavilion" -N "" -f ~/.ssh/id_ed25519
   gh ssh-key add ~/.ssh/id_ed25519.pub --title pavilion
   git -C ~/Projects/dubplate remote set-url origin git@github.com:glw907/dubplate.git
   ```
   If `gh` lacks the `admin:public_key` scope, ask Geoff to run
   `gh auth refresh -h github.com -s admin:public_key` and retry.
8. Build the local binaries the laptop carries outside the stow tree:
   ```bash
   make -C ~/Projects/poplar install
   make -C ~/.dotfiles/claude/.claude/skills/writing-voice/evals/tellgrader install
   ```
   `tellgrader` matters more than it looks: the writing-voice hook runs it on
   every Edit and Write, and cairn's docs gate skips its check without it.
   If either repo has no `install` target, read its README for the build
   step. Leave the rest of `bluefin/untracked-bin.txt` (NumberLink, harper-ls,
   marksman, odin4, perfspike, samfusdl) uninstalled unless Geoff asks for
   them. check-drift only flags unlisted binaries, never missing ones.
9. Turn on the remaining user services:
   ```bash
   systemctl --user enable --now cairn-tripwire.timer
   systemctl --user enable --now monitor-subscribe.service
   kitty-headless-shot setup
   ```
   The second line builds the `term-headless` distrobox that the
   `standards:tui-visual-verify` gate uses. Clone the standards repository, so `claude-tooling-sync update-skills` has a place to
   write: `git clone https://github.com/glw907/standards ~/Projects/standards`. Then install the
   Claude Code plugins that `settings.json` enables, adding the two third-party marketplaces first:
   ```bash
   claude plugin marketplace add cloudflare/skills
   claude plugin marketplace add gfargo/tui-design-skill
   claude plugin marketplace add glw907/standards
   for p in $(jq -r '.enabledPlugins | keys[]' ~/.claude/settings.json); do
       claude plugin install "$p"
   done
   ```
10. Verify. Run `check-drift` and `claude-tooling-sync verify`, then confirm
    each of these: `gh auth status`, `systemctl --user list-timers` shows
    check-drift, model-review, decision-review, and cairn-tripwire,
    `systemctl --user is-active monitor-subscribe` prints `active`,
    `hostnamectl` shows `pavilion`, a new Claude session opens with
    `## Host: pavilion`, and `ls ~/.claude/projects/*/memory` lists the
    carried memory. Fix any drift that a step above should have
    covered. Report the rest to Geoff with the Part 3 list.

    Then confirm the auto-mode rules reached the live settings.
    `claude auto-mode config` should list the github.com/glw907 Source
    control entry, the `~/Projects` and `~/.dotfiles` Trusted repo entry, and
    the `allow` rules for worktree rebases and directed PR merges. All of
    them live in the tracked `claude/.claude/settings.json`. Only
    `claude-tooling-sync apply` writes them into `~/.claude/settings.json`,
    and a pull or `stow` alone does not. A session can't add a missing rule
    itself, because the classifier blocks that as Self-Modification, so a
    missing rule means rerunning `apply`, not editing settings by hand.

    Also confirm Homebrew's `git` can reach GitHub over HTTPS:
    ```bash
    /home/linuxbrew/.linuxbrew/bin/git ls-remote https://github.com/glw907/workstation HEAD
    ```
    On 2026-10-13 this failed with "unable to get local issuer
    certificate". Homebrew 6.0.1 could not run the `ca-certificates`
    post-install (`unknown install step: run`), so no CA bundle existed, and
    `brew update` stopped on a broken third-party cask. The fix runs the
    formula's own script and links the bundle where Homebrew's OpenSSL 4
    looks (`openssl version -d` names the directory):
    ```bash
    B=/home/linuxbrew/.linuxbrew; K=$(echo $B/Cellar/ca-certificates/*)
    bash $K/libexec/post-install $K/share/ca-certificates/cacert.pem $B/etc/ca-certificates/cert.pem
    mkdir -p $B/etc/openssl@4 && ln -sf ../ca-certificates/cert.pem $B/etc/openssl@4/cert.pem
    ```

    Running the repo gate (`bash scripts/gate.sh`) on a fresh machine fails
    for a reason unrelated to any change. The
    ratchet flags documented paths that don't exist yet, such as `~/Android`
    and the laptop-only lid folder. A path that belongs on only one host
    carries a `host-ok` marker on its line. `~/.contacts/` is not one of
    those: it appears after the first contacts sync, which needs the DAV
    token above.

## Part 3: Geoff, sign-ins

1. Open a NEW terminal and run `gws auth login -s docs,drive`. This mints
   the machine's own gws user token. The OAuth client pair comes from
   `~/.local/secrets`, which Part 2 step 3 wrote. A terminal opened before
   then never loaded it, and `gws` reports "No OAuth client configured".
2. In Chromium's `Default` profile (Claude's), install the Claude extension
   and confirm it connects to Claude Code. In Geoff's own profile, install
   the Proton Pass extension (`ghmbeldphafepmbegfdlkpapadhbakde`). Install
   each by hand: Chromium policy is browser-wide, so neither extension is
   force-installed, and no profile carries a 1Password extension. If the
   Claude extension can't connect, check for
   `~/.config/chromium/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`.
   A Claude session started without `--chrome` doesn't write it, and
   neither does `/chrome` inside a session that started before setup.
   Start a fresh `claude --chrome` and quit it. Don't use `--continue`
   while another session on the same conversation is open.
3. Add the Fastmail CalDAV/CardDAV account in Settings > Online Accounts
   (GNOME Contacts and Calendar read it), then launch Hylki and sign in to
   Fastmail.
4. Set the desktop background to `01-bluefin.xml`, the winter dinosaur in
   Nord tones:
   ```bash
   for k in picture-uri picture-uri-dark; do
       gsettings set org.gnome.desktop.background $k 'file:///usr/share/backgrounds/bluefin/01-bluefin.xml'
   done
   ```
   Bluefin ships its artwork in the image and renumbered it between builds.
   On 2026-10-13 the laptop's older build shows this picture as
   `10-bluefin.xml`, while pavilion's build shows October's swamp under that
   name. So `gnome-settings.txt` doesn't track the background until both
   machines run artwork with the same numbering.

   The dock needs no step here. `setup` applies it from `gnome-settings.txt`:
   Files, Terminal, Chromium, Hylki, Discord, noson, Rufin, Steam,
   then Trash. Before that line existed, pavilion kept Bluefin's
   stock dock, including the installer and a dead link to the removed
   Thunderbird ESR (Thunderbird is retired). If an icon is missing, check that its app installed and
   that `check-drift` reports `favorite-apps` matching.

   Then relax the screen lock. pavilion is a desktop in the home office, so
   it never locks and blanks after 15 idle minutes. The laptop keeps its
   lock, so these stay out of the shared `gnome-settings.txt`:
   ```bash
   gsettings set org.gnome.desktop.screensaver lock-enabled false
   gsettings set org.gnome.desktop.session idle-delay 'uint32 900'
   ```
5. Gaming. Steam is the Flathub build from `flatpaks.txt`. Check that its
   Nvidia GL extensions match the driver: `flatpak list | grep GL.nvidia`
   should show `GL.nvidia` and `GL32.nvidia` with the version
   `/proc/driver/nvidia/version` reports. Flatpak updates replace them when
   the image's driver changes. Then add the MangoHud and gamescope Vulkan
   layers for the Steam runtime's branch, and keep Nvidia's shader cache from
   being pruned:
   ```bash
   flatpak install --system -y flathub \
       org.freedesktop.Platform.VulkanLayer.MangoHud//26.08 \
       org.freedesktop.Platform.VulkanLayer.gamescope//26.08
   flatpak override --user --env=__GL_SHADER_DISK_CACHE_SKIP_CLEANUP=1 com.valvesoftware.Steam
   ```
   `flatpak info com.valvesoftware.Steam` names the runtime branch, 26.08 on
   2026-10-13. The layers are runtimes, which `check-drift` doesn't list,
   so they live here rather than in `flatpaks.txt`. The image already
   carries controller udev rules, `/dev/uinput` access, GameMode, and
   `vm.max_map_count` at 1048576. In Steam, Proton covers every title by
   default; Settings > Compatibility only picks the default tool (Proton
   Experimental on 2026-10-13), and Settings > Downloads keeps shader
   pre-caching on. Per game, `gamemoderun %command%` in the launch options
   turns on GameMode, and `mangohud %command%` shows the overlay.
6. Peripherals. The Logitech M720 mouse and the Keychron K3 keyboard pair
   over the onboard Bluetooth. `bluetoothctl pair` needs an agent in the
   same session, or it fails with `AuthenticationFailed` and bluetoothd logs
   "No agent available". Pipe the commands into one session:
   ```bash
   { echo "agent NoInputNoOutput"; echo default-agent; echo "pair $MAC"; sleep 12
     echo yes; sleep 3; echo "trust $MAC"; echo "connect $MAC"; sleep 5; echo quit; } | bluetoothctl
   ```
   The K3 pairs from Bluetooth mode by holding fn + 1 for 4 seconds, until
   the light blinks fast. It is then the only keyboard, so start the pairing
   before switching it over. The M720's thumb button sends Super through a
   remap stored on the mouse, which Solaar (`flatpaks.txt`) set, so a
   reinstall doesn't need it again.

   Once step 4 has enrolled the TPM, the machine boots to the GDM login
   screen with no cable, and the K3 types the password there over
   Bluetooth. Two boots still need the cable: the passphrase fallback after
   a BIOS update or a Secure Boot change, and any visit to the BIOS or the
   GRUB menu. The K3 drops its link after 10 idle minutes. Step 4's
   Bluetooth files make the reconnect fast, and holding fn + S + O (plain
   keys, no Shift) for about 3 seconds in Bluetooth mode turns that sleep
   off.

   Both batteries show in the top bar through the UPower Battery extension.
   It has no manifest tier, so install it here. It loads at the next login:
   ```bash
   curl -sL -o /tmp/upower-battery.zip \
       "https://extensions.gnome.org/download-extension/upower-battery@codilia.com.shell-extension.zip?shell_version=50"
   gnome-extensions install --force /tmp/upower-battery.zip
   cur=$(/usr/bin/gsettings get org.gnome.shell enabled-extensions)
   /usr/bin/gsettings set org.gnome.shell enabled-extensions "${cur%]}, 'upower-battery@codilia.com']"
   ```
7. Install the Android SDK (Geoff, 2026-10-13: both hosts carry it). Take
   the Linux command-line tools archive and its SHA-256 from
   developer.android.com/studio, check it with `sha256sum -c`, and unzip its
   `cmdline-tools` folder to `~/Android/cmdline-tools/latest`. Then run
   `yes | sdkmanager --licenses` and `sdkmanager platform-tools
   "platforms;android-36" "build-tools;37.0.0"` (the newest stable at the
   time). `.bashrc` sets `JAVA_HOME` to Homebrew's keg-only `openjdk@17`,
   which `sdkmanager` needs. Done on pavilion 2026-10-13. Optionally, pair
   Syncthing at `http://127.0.0.1:8384`.
8. Shut down fully and power on, so the zram and OOM drops take effect, and
   confirm GDM logs straight in. A cold start also tests the BIOS
   workaround: `journalctl -b -k | grep -c SOD3` should print 0.

## Gaps found after setup

Each row is something a session hit on pavilion that thinkpad-x1 already had, with the fix for the
next setup.

| Missing | Why it mattered | Fix |
|---|---|---|
| Claude Code workspace trust for `~/Projects/cairn-cms` (found 2026-10-14, drafter pass 5) | `claude --bg` refuses to launch in an untrusted folder, so the conductor couldn't start the cairn executor until Geoff ran `claude` there | In Part 3, run `claude` once in each repo under `~/Projects/` and accept the trust prompt |
| Auto-mode trust and allow rules in the live `~/.claude/settings.json` (found 2026-10-17) | The classifier blocked cross-repo pushes, a worktree rebase onto main, and a merge Geoff had directed, and each fix needed his approval mid-task | The rules now ship in the tracked `settings.json` (workstation fbf3919 and #89). Run `claude-tooling-sync apply` after every pull, then check `claude auto-mode config` as Part 2 step 10 says |
| A Playwright browser for cairn-cms (found 2026-10-14, drafter pass 5) | Two of cairn's fast-lane suites skipped locally; CI still ran them | Run `npx playwright install chromium` in `~/Projects/cairn-cms` after `npm ci` |

## Changes to carry to thinkpad-x1

Pavilion picked up these changes after setup. Each needs a step on thinkpad-x1, because a pull alone does not install, enable, or restart anything.

On 2026-10-24, Netflix in Chromium needed two fixes. Fedora's `chromium` ships without Google's Widevine module, so `update-widevine` installs it from the Chrome stable RPM and a weekly timer keeps it current (workstation #144). On pavilion, Widevine video then played black under Wayland on the NVIDIA card, a Chromium 151+ regression. `chromium-launch` adds `--ozone-platform=x11` on NVIDIA only, so thinkpad-x1's Intel graphics stays on Wayland.

1. Pull `~/.dotfiles`, then run `stow -R bin upkeep applications` and `claude-tooling-sync apply`.
2. Run `rpm -q chromium` and confirm Fedora's package is installed. `update-widevine` assumes it.
3. Run `update-widevine`, then `systemctl --user daemon-reload` and `systemctl --user enable --now widevine-update.timer`.
4. Quit every Chromium window and start Chromium from the dock. `chrome://components` should list "Widevine Content Decryption Module" with a version.
5. Play a Netflix title. If the picture is black with no sound, `chromium-launch`'s NVIDIA check is too narrow for this laptop: start a session with the `chrome://media-internals` log for the watch-page player.
6. Run `check-drift` and expect it clean.

## After pavilion is up

Delete the handoff bundle from R2. It holds a copy of the ASC age key.

```bash
for k in chunk-aa chunk-ab chunk-ac chunk-ad handoff.sha256; do
    npx -y wrangler r2 object delete --remote "workstation-backup/pavilion-handoff/$k"
done
```
