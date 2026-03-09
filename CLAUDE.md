# New Workstation Setup Guide (for Claude)

Step-by-step procedure for bootstrapping this environment on a fresh Linux Mint 22 (Cinnamon) machine.

**Target OS**: Linux Mint 22 "Zena" (Ubuntu 24.04 base, Cinnamon desktop)

---

## Prerequisites

Install base tools before cloning the repo:

```bash
sudo apt update && sudo apt install -y stow git curl micro gh
gh auth login
```

Notes:
- `gh` is in the standard Mint 22 repos — no PPA needed
- Flatpak is pre-installed on Linux Mint — no setup needed

---

## Clone and Stow Core Packages

```bash
git clone https://github.com/glw907/workstation.git ~/.dotfiles
cd ~/.dotfiles
stow bash bin claude vscodium git
source ~/.bashrc
```

**Core packages** (stow these first): `bash bin claude vscodium git`

**Optional packages** (stow as needed): `android themes wallpapers applications browser-bookmarks`

---

## Install VSCodium

VSCodium is not in the standard Ubuntu repos. Add the apt repo for ongoing updates:

```bash
wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg \
  | gpg --dearmor | sudo tee /usr/share/keyrings/vscodium-archive-keyring.gpg > /dev/null
echo 'deb [ signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg ] https://paulcarroty.gitlab.io/vscodium-deb-rpm-repo/debs vscodium main' \
  | sudo tee /etc/apt/sources.list.d/vscodium.list
sudo apt update && sudo apt install -y codium
```

Then install extensions:

```bash
cat ~/.dotfiles/vscodium/extensions.txt | xargs -L 1 codium --install-extension
```

---

## Install Claude CLI

```bash
npm install -g @anthropic-ai/claude-code
# or via curl installer — check https://claude.ai/download for current method
claude   # Opens browser for auth on first run
```

---

## Install NVM (Node Version Manager)

Required for `npx`/wrangler and Claude CLI if installed via npm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/HEAD/install.sh | bash
source ~/.bashrc
nvm install --lts
```

---

## API Credentials

The `.bashrc` (stowed from `bash/.bashrc`) already contains Geoff's API credentials:
- Cloudflare API token and Zero Trust token
- Resend API key
- Google Workspace credentials
- ClouDNS auth
- Stripe keys
- Discord webhook URLs

These are active as soon as `source ~/.bashrc` runs — **no manual step needed**.

**Do not overwrite `.bashrc` with placeholder values.**

---

## Sudo Password Helper (for `cld`)

The `cld` script uses `claude-askpass` to supply sudo passwords without interactive prompts.
After first login, prime the cache:

```bash
claude-sudo-setup   # Retrieves password from system keyring via secret-tool
```

Or manually cache it:

```bash
echo 'password' > ~/.cache/claude-sudo-token && chmod 600 ~/.cache/claude-sudo-token
```

---

## Git Config

Git identity is pre-configured in `~/.dotfiles/git/.gitconfig`. The `stow git` step above
creates `~/.gitconfig` as a symlink — verify it's in place:

```bash
ls -la ~/.gitconfig   # Should be a symlink into ~/.dotfiles/git/.gitconfig
```

---

## Flatpak Applications

Flatpak is pre-installed on Linux Mint. Core apps are not tracked in dotfiles — install manually:

```bash
flatpak install flathub com.discordapp.Discord
flatpak install flathub com.fastmail.Fastmail
flatpak install flathub org.gnome.Apostrophe
flatpak install flathub com.noson.Noson
```

---

## Optional: Android SDK

Follow `~/.dotfiles/android/README.md`. Summary:

- Download command-line tools from developer.android.com
- Extract to `~/Android/cmdline-tools/latest/`
- Run: `sdkmanager --licenses && sdkmanager "platform-tools"`

The `ANDROID_HOME` and `PATH` entries are already set in `.bashrc`.

---

## Optional: Nord Theme

```bash
cd ~/.dotfiles/themes && ./setup-nord.sh
```

---

## Optional: Wallpapers and Desktop Launcher

```bash
cd ~/.dotfiles
stow wallpapers      # → ~/Pictures/Wallpapers/
stow applications    # → ~/.local/share/applications/ (VSCodium Writing profile)

# Set wallpaper in Cinnamon
gsettings set org.cinnamon.desktop.background picture-uri \
  "file://$HOME/Pictures/Wallpapers/nord-gradient.png"
```

---

## Verify Setup

```bash
~/.dotfiles/sync-dotfiles.sh    # Should report all packages in sync
which cld                        # → ~/.local/bin/cld
ls -la ~/.claude/cli-mode.md    # → symlink into ~/.dotfiles
cld "echo hello"                 # Launches Claude in CLI mode
```

---

## Stow Package Reference

| Package | Destination |
|---------|-------------|
| `bash` | `~/.bashrc`, `~/.profile` |
| `bin` | `~/.local/bin/` (cld, cld-arch, claude-askpass, etc.) |
| `claude` | `~/.claude/` (cli-mode.md, settings, keybindings) |
| `vscodium` | `~/.config/VSCodium/User/settings.json` |
| `git` | `~/.gitconfig` |
| `android` | `~/.dotfiles/android/` (README only — SDK itself goes to `~/Android/`) |
| `themes` | `~/.themes/` |
| `wallpapers` | `~/Pictures/Wallpapers/` |
| `applications` | `~/.local/share/applications/` |
| `browser-bookmarks` | `~/.config/` (browser profile configs) |
