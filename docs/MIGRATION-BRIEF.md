# Bluefin DX migration brief: thinkpad-x1

Decisions record and context for the Mint 22.3 to Bluefin DX conversion, written
2026-08-29 during Phase 0. Authoritative for all bootstrap artifacts and for the
second workstation arriving a few weeks later. Sources: docs.projectbluefin.io,
Universal Blue Discourse, 1Password release notes, verified 2026-08-29.

## Goal

Maximum-clean, idiomatic atomic setup for daily productivity and coding. The
base image stays stock apart from the four layered RPMs. Every install has one
correct tier, the bootstrap artifacts are the source of truth, and nothing
lands on the system ad hoc. When Mint habit and Bluefin idiom conflict, the
idiom wins unless it breaks a real workflow (the layered browsers are the one
deliberate exception, forced by native messaging).

## Decisions (approved by Geoff)

- One-shot clean install from the official Bluefin ISO on `stable` (Fedora 44
  base), written to USB with Fedora Media Writer. Whole-disk automatic
  partitioning with LUKS full-disk encryption. VERIFIED 2026-08-29: the ISO is
  unified (https://download.projectbluefin.io/bluefin-stable-x86_64.iso, 5.6G,
  no separate -dx ISO); DX is enabled post-install by rebasing to
  bluefin-dx:stable (or ujust devmode; confirm the current mechanism on first
  boot). ISO downloaded to ~/Downloads with upstream CHECKSUM verification.
- Secure Boot: enable in BIOS before install ("Allow Microsoft 3rd Party UEFI
  CA" must be ON, a ThinkPad gotcha). Bluefin enrolls its MOK at first boot;
  password is the string `universalblue`.
- Fresh home directory, selective restore from the encrypted backup. Nothing
  restored wholesale; ~/Downloads abandoned.
- Browsers: Firefox (Fedora RPM, layered) is the daily browser. Chromium (Fedora RPM, layered) is the development and testing
  browser used by Claude Code (claude-in-chrome native host, DevTools
  automation, chromium-shot). Flatpak builds of either are ruled out:
  Claude's native-messaging hosts cannot reach sandboxed browsers.
- Node via mise (replacing nvm). Python tools via uv. Go via Homebrew.
- Neovim is dropped entirely; Geoff does not use it. micro is the terminal
  editor. The eudaimonia project is dead: do not carry its cron entries or
  config.
- Layered RPM set, kept deliberately minimal: `firefox`, `chromium`
  (1Password was removed on 2026-10-19 in favor of Proton Pass, Geoff 2026-10-18,
  with pass-cli from Homebrew). Everything else lives in Homebrew, Flatpak, mise/uv,
  or the home directory.
- Enforcement: the `claude-tierguard` PreToolUse hook (dotfiles bin package,
  wired in claude/.claude/settings.json) denies any Claude-run `rpm-ostree
  install` of a package not in layered-packages.txt. No-op on machines
  without rpm-ostree. Additions go list-first, then install.
- Second workstation: provisioned from a stock Bluefin DX ISO plus these
  bootstrap artifacts. A custom uBlue image is an explicit later decision
  point, not a commitment.

### Amendments (2026-08-30, verified against the installed system)

These four supersede the corresponding decisions above. All were found by
checking the running Bluefin install rather than the docs, and each is
implemented in `bootstrap.sh`.

- DX enablement is its own bootstrap phase, `bootstrap.sh devmode`, run
  before `layer`. VERIFIED: the ISO installs `ghcr.io/ublue-os/bluefin:stable`
  (non-DX) — the unified ISO does not ask, and the resulting system has no
  docker and no VS Code. The mechanism is `ujust devmode`, which runs
  `bootc switch --enforce-container-sigpolicy` to the matching `-dx` tag.
  Preferred over calling `bootc` directly so the image reference stays
  whatever Bluefin says it is. This adds a second mandatory reboot: `layer`
  must run against the booted image, so layering before the DX reboot would
  strand the RPMs on the deployment being replaced. `layer` and `setup` both
  hard-stop on a non-DX image rather than proceeding.
- Preinstalled Flatpak Firefox and 1Password are removed in `setup`, before
  anything depends on them. VERIFIED: the base image ships
  `org.mozilla.firefox` as a system Flatpak and sets it as the default
  browser; `com.onepassword.OnePassword` was also present. Both collide with
  the layered RPMs this brief already requires, and the sandboxed builds are
  precisely the ones ruled out above for native messaging. Removal sticks:
  the system Flatpak set comes from `ujust install-system-flatpaks`, a manual
  "for rebasers" recipe that no image update re-runs. `setup` also reassigns
  the default-browser association to `firefox.desktop`, which otherwise keeps
  pointing at the removed Flatpak.
- Claude Code comes from the Homebrew cask (`cask "claude-code"` in the
  Brewfile), not the native `~/.local/bin/claude` installer this brief
  originally specified. Bluefin ships the cask preinstalled, Homebrew is the
  CLI tier here, and the cask updates under `ujust update` with everything
  else instead of self-updating on its own schedule. A native install would
  also shadow the cask on PATH, leaving two installs and two update paths.
  This is the brief's own "idiom wins" rule applied to a decision made before
  the system was available to check. `setup` warns if both exist.
- No fonts are installed at all (Geoff, 2026-08-30: "happy to work with
  bluefin fonts"). `kitty.conf` asked for Monaspace Neon, which Bluefin does
  not ship; rather than add a cask, kitty now uses **JetBrains Mono**, and its
  `symbol_map` now points at **Symbols Nerd Font Mono**. VERIFIED: both are
  already in the base image. The old symbol_map named `JetBrainsMonoNL Nerd
  Font`, the patched variant, which is NOT installed here — the glyph mapping
  was silently falling through to tofu. Ptyxis uses the system monospace.
  Decline ujust's font prompt: there is nothing to add.
- Ptyxis is the daily terminal, not kitty (Geoff, 2026-08-30: use the default
  terminal unless there is a real deficiency). Ptyxis ships with the image and
  needs no setup. kitty stays installed but is demoted to one job: the gate
  platform for the `tui-visual-verify` skill, whose `kitty-shot` harness
  drives a real kitty window through kitty's remote control. Ptyxis has no
  remote-control equivalent, so nothing else can stand in for that.
- The TUI verification gate needed repair independent of the terminal choice.
  VERIFIED: `kitty-shot` locates the window with `xdotool` and captures it
  with ImageMagick's `import`, both X11-only, and Bluefin's GNOME session is
  Wayland (`XDG_SESSION_TYPE=wayland`) where they are blind. Mint/Cinnamon was
  X11, so this never came up before. Two fixes: `linux_display_server x11` in
  `kitty.conf` forces XWayland, and `xdotool` joins the Brewfile (it was not
  installed and not listed anywhere).

### Amendments (2026-08-30, restore day)

Found while executing setup and restore on the installed system.

- The Fedora 44 firefox RPM ships `org.mozilla.firefox.desktop`, not
  `firefox.desktop`. It is the same desktop id the Flatpak exported, so the
  default-browser association survives the Flatpak removal and lands on the
  RPM by itself; `setup` now sets that id explicitly instead of the
  nonexistent `firefox.desktop`.
- `stow_clear_conflicts` in bootstrap.sh followed paths through stow-folded
  parent symlinks (e.g. `~/.claude/skills` -> repo) and moved the repo's own
  tracked files aside as "conflicts", gutting the working tree. The
  `restore_place_home` git-status assertion caught it; the helper now skips
  any target whose realpath resolves inside the dotfiles repo.
- The backup's `.claude` carries Mint-era stow output for the stow-tracked
  names (a real `docs/` dir of per-file symlinks into the repo, folded
  `skills`), which collides with today's stow-folded dirs when rsynced back
  (symlink loops, ELOOP). The `.claude` restore rsync now excludes every
  top-level name in the claude stow package, derived from the package dir
  itself so the set cannot drift; the git-tracked copies placed by stow are
  canonical and runtime state is all the backup should contribute.

## Platform facts (verified 2026-08-29)

- Streams: `gts` / `stable` / `latest`; DX is its own image tag
  (`bluefin-dx:stable`). `stable` is the daily-driver recommendation, weekly
  builds, gated kernel. VERIFIED 2026-08-30 on the installed system: the ISO
  lands you on non-DX `bluefin:stable` and DX is a post-install rebase, per
  the devmode amendment above.
- `ujust devmode` also offers to install DX flatpaks and extra monospace
  fonts. Decline both: those sets are tracked in `flatpaks.txt` and the
  `Brewfile` instead, so the two workstations stay identical. Bluefin's DX
  flatpak list (`system-dx-flatpaks.Brewfile`) is Clapgrep, embellish, Podman
  Desktop, devtoolbox, and GNOME Builder — none of which are in use here.
- Bluefin manages its preinstalled Flatpaks through Brewfiles at
  `/usr/share/ublue-os/homebrew/system-flatpaks.Brewfile` (+ the `-dx`
  variant), applied by the manual `ujust install-system-flatpaks` recipe.
  Nothing re-runs it on update, so removing a preinstalled Flatpak is
  durable. The one automatic hook that mentions Firefox
  (`privileged-setup.hooks.d/99-flatpaks.sh`) is version-gated and only
  writes prefs into an extension dir; it never installs the app.
- bootc and rpm-ostree are BOTH live in 2026. `bootc switch`/`status` for
  rebases and inspection, `rpm-ostree install` still standard for layering.
  Docs and community guidance mix the two; this is normal. Note `bootc
  status` needs root (`sudo bootc status`); unprivileged it errors out on
  "Querying root privilege". `rpm-ostree status` does not, and is the easier
  reflex for a quick look at deployments and layered packages.
- Software tiers: Flatpak for GUI, Homebrew for CLI, distrobox/devcontainers
  for dev environments, rpm-ostree layering as last resort. Bluefin DX ships
  Docker Engine, Podman, distrobox, VS Code out of the box.
- Key ujust commands: `ujust update` (system + flatpak + brew), `ujust
  rebase-helper` (stream switch / rollback to date-tagged builds), `ujust
  dx-group` (adds user to dev groups; needed on stable, not gts), `ujust
  devmode`, `ujust enroll-secure-boot-key`.
- Updates check every 6 hours automatically; system image applies at reboot.
- `/etc` is writable and persists across image updates; `/home` symlinks to
  `/var/home` (stow works unchanged).
- 1Password was removed on 2026-10-19 in favor of Proton Pass (Geoff, 2026-10-18), with
  pass-cli from Homebrew; nothing 1Password is layered.
- Homebrew Chromium/Firefox do not exist on Linux (casks are macOS-only for
  browsers; no formulae). Confirmed dead end, do not revisit.
- Chromium policies: /etc/chromium/policies/managed/*.json works identically
  to Mint for the layered RPM. Captured policies: password-manager.json, kagi-search.json,
  no-google-telemetry.json (in etc/chromium-policies/).
- Native messaging manifests for the RPM (non-sandboxed) Firefox land in the standard
  Mozilla paths.
- Android: Bluefin ships no adb udev rules. 51-android.rules is captured in
  etc/udev/, install to /etc/udev/rules.d/ + udevadm reload. SDK reinstalls
  via cmdline-tools into ~/Android; adb keys restored from backup (~/.android).
- SELinux: Bluefin enforces; Mint data carries no labels. After ANY restore
  into /var/home, run `sudo restorecon -R -v /var/home/glw907`. Skipping this
  is a documented cause of broken logins.

## Backup state (Phase 0, complete as of this writing)

- All repos pushed to GitHub, including backup/pre-bluefin-* stash refs
  (907-life, aksailingclub-org, asc-site). EXCEPTION: cairn-cms had a live
  Claude session; Geoff pauses and pushes it himself before the wipe. Verify
  before wiping: `cd ~/Projects/cairn-cms && git status && git log
  --branches --not --remotes --oneline` must be clean/empty, including
  .claude/worktrees/*.
- smallbusinessak-org has NO GitHub remote (gh repo create was pending);
  full git bundle is in the backup at projects/smallbusinessak-org.bundle.
- Encrypted backup: pre-bluefin-backup.tar.age, 2.5G,
  sha256 db0c2c041d2587ac300421734e4d4f32f436832242d385f20cc913aee0a0dbe1.
  Copies: USB stick (/media/glw907/writable/pre-bluefin/, until the stick is
  reflashed with the Bluefin ISO) and R2 bucket `workstation-backup` under
  pre-bluefin/ as 250M chunks (chunk-aa, chunk-ab, ...; reassemble with
  `cat chunk-* > pre-bluefin-backup.tar.age`, verify sha256).
- Gotcha for future R2 work: `wrangler r2 object put` writes to the LOCAL
  Miniflare simulator unless `--remote` is passed. The first upload pass hit
  this; always verify with the R2 objects API listing, never trust "Upload
  complete" alone.
- Encrypted to the workstation age recipient
  age197mcd2m3z90t49n9t5v3ujjntw7krfkw5y9sjfc545v28qvezugshg7jgk. The
  identity key lives in Proton Pass and is fetched through `ws-pass-key`.
  Decrypt: `age -d -i <keyfile> pre-bluefin-backup.tar.age | tar -x`.
- Tarball contents: home/ (.dotfiles, .ssh, .contacts, .vdirsyncer, .android,
  Documents, corpus, Pictures, .local/bin, .local/share/keyrings, selected
  .config including chromium profile, gcloud, gh, op, 1Password, poplar,
  jrnl*, khard, vale, google-workspace, age key asc-key.txt, systemd user
  units; .claude with memory, settings, skills, docs, agents, workflows,
  history), projects/ (aksailingclub-sveltekit minus node_modules,
  cairn-scratch minus artifacts, ecxc-ski-agent-memory,
  smallbusinessak-org.bundle), etc-capture/ (chromium policies, 51-android
  udev rule, crontab.txt), manifest.txt.

## Current-machine facts the artifacts must honor

- Active services to re-establish: syncthing (systemd user service, active on
  Mint; on Bluefin, `brew services start syncthing` generates and manages the
  service unit itself, no manual `systemctl --user enable --now` step needed).
- Crontab: only the weekly workstation-update line concept carries forward
  (Bluefin auto-updates; the script likely becomes unnecessary; eudaimonia
  lines are dead).
- CLI estate observed in use on Mint (curate Brewfile from this, not from the
  full apt dump): age gh git jq yq micro stow tmux pandoc hugo sqlite3
  imagemagick ffmpeg yt-dlp socat ttyd rsync khard vdirsyncer vale syncthing
  go gofumpt golangci-lint chafa. Java 17 (openjdk@17) for Android tooling.
  khard/vdirsyncer/yt-dlp are Python: prefer `uv tool install`.
- npm globals in use: browser-sync, markdownlint-cli, prettier (via mise
  node, or per-project).
- kitty was the terminal on Mint (config stowed); install via upstream binary
  installer into ~/.local/kitty.app, not layered. Superseded by the amendment
  above: on Bluefin, Ptyxis is the terminal and kitty is kept only as the
  tui-visual-verify gate platform. The installer path is unchanged.
- Claude Code via the Homebrew cask (see the amendment above; this line
  originally said the native installer to ~/.local/bin/claude). ~/.claude is
  restored from backup before first launch either way.
- Askpass flow: SUDO_ASKPASS=~/.local/bin/claude-askpass (script in
  dotfiles bin package); takes the sudo password from a zenity dialog,
  never a password manager; `claude-sudo-setup` refreshes the tmpfs cache (updated
  2026-08-30; the original age-file cache design was never built).
- Stow packages: the list in `bluefin/stow-packages.txt` (updated 2026-08-30;
  this line originally froze a six-package set that has since grown).
- GNOME on Bluefin replaces Cinnamon; no desktop config carries over (Geoff
  explicitly does not need desktop defaults preserved).
