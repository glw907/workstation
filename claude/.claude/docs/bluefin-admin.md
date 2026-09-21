# Bluefin DX admin reference: thinkpad-x1

Standing reference for administering the Bluefin DX system (stable stream, Fedora 44
base). Read this before installing software, editing `/etc`, running an update, or
touching browser configuration on this machine.

The Mint-era `chromium-browser.md` was retired 2026-08-30 (recoverable from git
history); this file's Browsers section is the authority. The old file's
telemetry-policy reasoning still holds, since the same JSON policy files carried
over unchanged.

Decisions record and fact base: `~/.dotfiles/docs/MIGRATION-BRIEF.md`. Treat that
file as authoritative for anything this doc doesn't cover.

## Software-tier policy

Install in this order of preference. Each tier down is a deliberate escalation, not a
default.

1. **mise** — Node and other language runtimes it manages. Replaces nvm.
2. **uv** — Python tools and environments (`uv tool install <name>` for CLI tools like
   khard, vdirsyncer, yt-dlp).
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
   why `1password`, `1password-cli`, `firefox`, and `chromium` are layered — see
   below).

kitty is the exception to all of the above: install via the upstream binary installer
into `~/.local/kitty.app`, never layered, never Flatpak (native messaging and
sandboxing concerns don't apply to a terminal, but the upstream installer is simply
the right tier for a self-contained binary app with its own update mechanism).

Homebrew has no Chromium or Firefox formula/cask on Linux — confirmed dead end, do not
retry `brew install chromium` or similar.

### Every install updates its manifest, same session

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
anything runs `check-drift` before it closes. An install without its manifest line
is drift you created knowingly.

### layered-packages.txt is the source of truth

`~/.dotfiles/bluefin/layered-packages.txt` is the canonical list of what's layered via
`rpm-ostree install` on this machine. As of the migration brief it holds exactly:

```
1password
1password-cli
firefox
chromium
```

Before layering anything new, check this file first — if a package isn't already
listed, adding it is a deliberate escalation past every tier above, not a default
move. **Every addition to the layered set gets recorded in both this file and
`docs/MIGRATION-BRIEF.md`** (append to the Decisions or Platform facts section, whichever
fits). A layered package that isn't in this file is drift — reconcile it in one
direction or the other rather than leaving the mismatch.

If this file doesn't exist yet on a fresh checkout, create it with the four packages
above before layering anything.

## Command map

- `ujust update` — updates system image, Flatpaks, and Homebrew together. The normal
  update path; prefer it over invoking `rpm-ostree upgrade`, `flatpak update`, and
  `brew upgrade` separately.
- `ujust rebase-helper` — switch streams (`gts`/`stable`/`latest`) or roll back to a
  specific date-tagged build. Use this for rollback, not a manual `bootc` invocation,
  unless you need something the helper doesn't expose.
- `ujust dx-group` — adds the user to developer groups (docker, libvirt, etc.). Needed
  on `stable`; not needed on `gts`, which ships them by default. Run once after a
  fresh install if group-gated tools (docker without sudo, for example) fail.
- `ujust devmode` — developer-mode toggle; consult `ujust --list` for what it changes
  before relying on it for anything specific.
- `ujust enroll-secure-boot-key` — re-enroll the MOK if Secure Boot state needs
  repair after a kernel or driver change.
- `bootc status` / `bootc switch` — inspect and change the underlying ostree image
  directly. Both `bootc` and `rpm-ostree` are live in 2026 and community docs mix
  them; `bootc` is the newer, more direct tool, `rpm-ostree` remains standard for
  layering packages (`rpm-ostree install <pkg>`). Use `rpm-ostree install` for
  layering, `bootc status` for a quick "what image am I on" check, and the `ujust`
  wrappers for anything that has one.

Claude Code's Bash tool does not source `~/.bashrc`, so an env var it sets (a Cloudflare
token, for example) comes back empty unless a command sources it explicitly per invocation:
`bash -c 'source ~/.local/secrets && echo -n $VAR'`. Working directory persists between Bash
tool calls; sourced files and exported variables do not.

## Update cadence and rollback

Updates are checked automatically every 6 hours; a fetched system image applies at
the next reboot, not immediately. This means "did the update work" is answered after
a reboot, not after `ujust update` returns.

Rollback playbook:

1. `bootc status` to see the current and previous deployments.
2. `ujust rebase-helper` to pick an earlier date-tagged build, or `bootc rollback` to
   go back one deployment directly.
3. Reboot to apply.
4. If the issue was a layered package, check whether it's still valid on the older
   image before re-layering it — `rpm-ostree install` state travels with each
   deployment.

## /etc drift discipline

Every `/etc` change lands in `~/.dotfiles/bluefin/etc/` first, then gets installed
onto the live system from there. Never edit a file under `/etc` ad hoc, even for a
one-line fix — write the change into the dotfiles copy, then apply it, so the repo
stays the record of what's actually on disk. Current captured files:

- `bluefin/etc/chromium-policies/*.json` → `/etc/chromium/policies/managed/`
- `bluefin/etc/udev/51-android.rules` → `/etc/udev/rules.d/`
- `bluefin/etc/systemd/logind.conf.d/10-lid-ignore.conf` → `/etc/systemd/logind.conf.d/` (lid close never suspends, Geoff 2026-09-12; after a change: `sudo -A systemctl kill -s HUP systemd-logind`)
- `bluefin/etc/systemd/user.conf.d/10-oom-continue.conf` and
  `bluefin/etc/systemd/zram-generator.conf.d/10-larger-zram.conf` → the memory-pressure
  defense; see `docs/oom-defense.md` for why they exist before touching either

`/etc` is writable on Bluefin and persists across image updates (unlike `/usr`), so
there's no technical reason to skip the dotfiles round-trip — treat any direct edit as
a bug to fix, not a shortcut that's sometimes fine.

After installing or changing a udev rule: `sudo -A udevadm control --reload-rules &&
sudo -A udevadm trigger`.

## Browsers

- **Firefox** (layered RPM) — daily browser, with 1Password integration. Needs the
  RPM build specifically; native messaging manifests for 1Password land in the
  standard Mozilla paths and expect a non-sandboxed browser.
- **Chromium** (layered RPM) — development and testing browser. This is what Claude
  Code drives: the claude-in-chrome native-messaging host, chrome-devtools MCP
  automation, and `chromium-shot` all target this browser.
- **Flatpak builds of either browser: never.** Both 1Password's browser integration
  and Claude's native-messaging hosts need to reach into the browser process directly;
  Flatpak's sandbox blocks that for both. This isn't a preference, it's a hard
  incompatibility — don't suggest a Flatpak browser as a fallback for anything that
  needs either integration.

Chromium policy files (telemetry, extensions, 1Password) are captured at
`bluefin/etc/chromium-policies/` and installed to `/etc/chromium/policies/managed/`.
Verify on first boot: `chrome://policy` in the layered Chromium lists all three
managed policies as active. (The retired Mint-era `chromium-browser.md` carried
deeper verification recipes; it lives in git history, removed 2026-08-30.)

## Headless real-terminal capture

`kitty-headless-shot` (`bin/.local/bin/`, stowed) drives a real kitty terminal on an
Xvfb display that exists only inside the `term-headless` distrobox (`bluefin/distrobox.txt`),
so a TUI capture never opens a window on the live desktop or steals focus. It is the
general-purpose primitive; per-repo harnesses such as the `tui-visual-verify` skill's
`kitty-shot` template call it by default and fall back to the on-desktop path only on
an explicit opt-in flag. `kitty-headless-shot --help` is the spec. Run
`kitty-headless-shot setup` once per machine to create the box (idempotent); this is
the first deliberate use of the distrobox tier on this workstation, so it is also the
precedent: a container is the right home for an X/Wayland server, Mesa, and
ImageMagick when the host's own copies can't do the job headless (the host's
ImageMagick has no X11 delegate wired up, and a GNOME screenshot portal or D-Bus route
is denied or interactive).

## SELinux for restored data

Bluefin runs SELinux enforcing; the Mint backup data carries no SELinux labels at all.
**After restoring anything into `/var/home/glw907` (which is what `~/` is on
Bluefin), run:**

```
sudo -A restorecon -R -v /var/home/glw907
```

Skipping this is a documented cause of broken logins and other permission-shaped
failures that look unrelated to SELinux. Run it once after the full restore, and
again after any later restore of additional data (a forgotten directory pulled from
the R2 backup, for example).

## 1Password GID gotcha

Known residual issue on ostree systems: the 1Password helper tool's GID can mismatch
what the browser extension or `op` CLI expects, breaking the desktop-app connection
that `claude-askpass` and the `sudo -A` flow depend on. The pre-July-2026 "updates
fail on ostree" bug itself is fixed upstream (v8.12.30-19); this GID issue is a
separate, narrower, still-open gotcha.

- Symptom: browser extension or `op` CLI can't connect to the 1Password desktop app,
  despite the app running and unlocked.
- Fix: community fix script, gist `b-/ed2cdc182ae5a92bdcd6b73308832a70`. Verify on
  first boot whether this is even needed — it may not reproduce on a fresh install.
- Never use the Homebrew cask for 1Password (`brew install --cask 1password`) as a
  workaround — it's missing setgid and is broken outright, not a milder alternative.
- Layered 1Password updates ride `ujust update` like everything else in the layered
  set; there's no separate self-update path to worry about.

If `claude-sudo-setup` or the `sudo -A` flow fails after a fresh install, check this
gotcha before assuming the askpass script itself is broken.
