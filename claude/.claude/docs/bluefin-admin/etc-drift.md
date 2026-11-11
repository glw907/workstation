# /etc drift discipline

Every `/etc` change lands in `~/.dotfiles/bluefin/etc/` first, then gets installed
onto the live system from there. Never edit a file under `/etc` ad hoc, even for a
one-line fix — write the change into the dotfiles copy, then apply it, so the repo
stays the record of what's actually on disk. Current captured files:

- `bluefin/etc/chromium-policies/*.json` → `/etc/chromium/policies/managed/` (includes `kagi-search.json`: Kagi as the default search engine and homepage, Geoff 2026-10-13, moved from Firefox 2026-10-18)
- `bluefin/etc/udev/51-android.rules` → `/etc/udev/rules.d/`
- `bluefin/etc/systemd/logind.conf.d/10-lid-ignore.conf` → `/etc/systemd/logind.conf.d/` (thinkpad-x1 only; pavilion has no lid and never installs it; lid close never suspends, Geoff 2026-09-12; after a change: `sudo -A systemctl kill -s HUP systemd-logind`) <!-- host-ok -->
- `bluefin/etc/systemd/user.conf.d/10-oom-continue.conf` and
  `bluefin/etc/systemd/zram-generator.conf.d/10-larger-zram.conf` → the memory-pressure
  defense; see `docs/oom-defense.md` for why they exist before touching either
- `bluefin/etc/gdm/custom.conf` → `/etc/gdm/custom.conf` on thinkpad-x1 (auto-login on),
  `bluefin/etc/gdm/custom.conf.pavilion` → the same path on pavilion (auto-login off: the disk
  unlocks through the TPM bound to PCR 7, so the GDM password is the credential gate; Geoff
  2026-10-17). A BIOS update or Secure Boot change on pavilion alters PCR 7: that boot asks for
  the disk passphrase on a cabled keyboard, then re-enroll per `SECOND-WORKSTATION.md` part 2
  step 4 <!-- host-ok -->
- `bluefin/etc/bluetooth/main.conf` → `/etc/bluetooth/` and
  `bluefin/etc/modprobe.d/btusb-no-autosuspend.conf` → `/etc/modprobe.d/` (pavilion only,
  Geoff 2026-10-17): `FastConnectable` and no adapter autosuspend, so the Keychron K3
  reconnects quickly after its idle sleep. The main.conf is a whole copy of the stock file;
  diff it against `/usr/etc/bluetooth/main.conf` after a BlueZ upgrade. After a change:
  `sudo -A btmgmt fast-conn on` applies the first live, the second takes effect at boot <!-- host-ok -->
- `bluefin/etc/systemd/system/phonebook-nightly.{timer,service}` and
  `phonebook-gate.{timer,service}` → `/etc/systemd/system/` (pavilion only, phonebook automation
  pass, 2026-10-26): system timers at 04:00 (checks, firmware rollout, kitchen cleanup) and 10:00
  (the staged rollout's gate) `America/Anchorage`, with `WakeSystem=true` so a suspended pavilion
  wakes. Each service carries `ConditionHost=pavilion`, so the files may sit in the dotfiles on both
  hosts. `ExecStart=` runs the main checkout's `scripts/check/nightly.sh`, so the checkout needs
  `npm ci` after a pull that changes its dependencies. After installing: `sudo -A systemctl daemon-reload && sudo -A systemctl enable --now
  phonebook-nightly.timer phonebook-gate.timer` <!-- host-ok -->
- `bluefin/etc/systemd/resolved.conf.d/10-cloudflare-dns.conf` → `/etc/systemd/resolved.conf.d/`
  (pavilion, Geoff 2026-11-10: "The home router is a lousey place for a DNS lookup."): every lookup
  goes to Cloudflare's resolvers over DNS-over-TLS, ahead of each link's DNS. The router's forwarder
  dropped about 1 lookup in 200 and failed cairn's clean-room runs. thinkpad-x1 does not install it,
  because a captive portal can block DNS-over-TLS until sign-in. After a change:
  `sudo -A systemctl restart systemd-resolved`, then `resolvectl status` shows `+DNSOverTLS` <!-- host-ok -->
- `bluefin/etc/systemd/system/maintain-projects.{timer,service}` → `/etc/systemd/system/` (pavilion
  only, Geoff 2026-11-01): the monthly `maintain-projects` run at 01:00 `America/Anchorage`, built
  like the phonebook units so it wakes pavilion and finishes before the 04:00 nightly. After
  installing: `sudo -A systemctl daemon-reload && sudo -A systemctl enable --now
  maintain-projects.timer` <!-- host-ok -->
  Pavilion is a desktop that stays awake on AC power. Orpheus, the always-available utility server,
  takes a job that truly must stay up (Geoff, 2026-11-01).
- `bluefin/etc/sysusers.d/cleanroom.conf` → `/etc/sysusers.d/` and
  `bluefin/etc/sudoers.d/cleanroom` → `/etc/sudoers.d/` (pavilion only, where the clean room
  runs; thinkpad-x1 skips both and `cleanroom` refuses to run there; mode 0440; Geoff 2026-11-09): the
  `cleanroom` system user (no login) that runs a clean-room session, and the rule that lets glw907
  run only the tool's internal `_child` form as that user, never as root. After installing:
  `sudo -A install -m 0440 bluefin/etc/sudoers.d/cleanroom /etc/sudoers.d/`, then
  `sudo -A install -m 0644 bluefin/etc/sysusers.d/cleanroom.conf /etc/sysusers.d/`
  and `sudo -A systemd-sysusers` to create the user

`/etc` is writable on Bluefin and persists across image updates (unlike `/usr`), so
there's no technical reason to skip the dotfiles round-trip — treat any direct edit as
a bug to fix, not a shortcut that's sometimes fine.

After installing or changing a udev rule: `sudo -A udevadm control --reload-rules &&
sudo -A udevadm trigger`.
