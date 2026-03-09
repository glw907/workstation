# Workstation Configuration

Ubuntu/Linux Mint workstation configuration — shell setup, custom scripts, Claude CLI tools, and VSCodium settings.

Managed with [GNU Stow](https://www.gnu.org/software/stow/) for automatic symlink management.

## Contents

- **bash/**: Shell configuration (.bashrc, .profile)
- **bin/**: Custom scripts (`cld`, `claude-askpass`, `claude-sudo-clear`, `update-android-sdk`)
- **claude/**: Claude CLI configuration (cli-mode.md system prompt, gather scripts, skills)
- **git/**: Git configuration (.gitconfig)
- **vscodium/**: VSCodium editor settings and extension list
- **android/**: Android SDK setup documentation
- **themes/**: Nord theme setup and installation scripts
- **wallpapers/**: Nord-themed desktop wallpapers
- **sync-dotfiles.sh**: Health check script for tracking drift

## Quick Setup on New System

```bash
# Install GNU Stow
sudo apt install -y stow

# Clone this repository
git clone https://github.com/glw907/workstation.git ~/.dotfiles
cd ~/.dotfiles

# Install desired packages (creates symlinks)
stow bash bin claude vscodium

# Reload shell configuration
source ~/.bashrc
```

## Using Stow

Stow creates symlinks from `~/.dotfiles/` to your home directory automatically:

```bash
cd ~/.dotfiles

# Install a package (create symlinks)
stow bash              # Links .bashrc and .profile
stow bin               # Links scripts to ~/.local/bin/
stow vscodium          # Links VSCodium settings.json

# Install multiple packages at once
stow bash bin vscodium

# Remove a package (remove symlinks)
stow -D bash

# Restow (useful after updates)
stow -R bash
```

## Manual Setup (Alternative)

If you prefer not to use Stow, you can manually copy files:

### 1. Shell Configuration

```bash
cp bash/.bashrc ~/.bashrc
cp bash/.profile ~/.profile
source ~/.bashrc
```

### 2. Git Configuration

```bash
cp git/.gitconfig ~/.gitconfig
```

### 3. Custom Scripts

```bash
mkdir -p ~/.local/bin
cp bin/.local/bin/* ~/.local/bin/
chmod +x ~/.local/bin/*
```

### 4. VSCodium Setup

```bash
# Install VSCodium first
# Visit: https://vscodium.com/

# Copy settings
mkdir -p ~/.config/VSCodium/User
cp vscodium/settings.json ~/.config/VSCodium/User/

# Install extensions
cat vscodium/extensions.txt | xargs -L 1 codium --install-extension
```

### 5. Android SDK Setup

See `android/README.md` for detailed Android SDK installation instructions.

### 6. Nord Theme Setup

Install Nord theme across system (GTK, icons, terminal, VSCodium):

```bash
# Automated installation
cd ~/.dotfiles/themes
./setup-nord.sh

# Or see themes/NORD.md for manual installation steps
```

This will install:
- Nordic GTK theme
- Papirus icon theme (Nord-compatible)
- Nord GNOME Terminal colors
- Nord wallpapers
- VSCodium Nord theme extension

## Key Features

### Shell Aliases & Functions

- `blog` - Quick access to Hugo blog development (`cd ~/Projects/907-life && codium . && hugo server -D`)
- `newpost` - Create new blog post with date prefix
- `blogpush` - Commit and push blog changes
- `blogdeploy` - Deploy blog to Cloudflare

### CLI Mode (`cld`)

The `cld` command launches Claude in system administration mode — for package management, dotfiles, services, and workstation configuration. Tracked in the **bin** and **claude** Stow packages:

**Scripts (bin package → `~/.local/bin/`):**
- `cld` - CLI mode launcher
- `claude-askpass` - SUDO_ASKPASS helper for cached sudo
- `claude-sudo-clear` - Clears cached sudo password

**Claude config (claude package → `~/.claude/`):**
- `cli-mode.md` - System prompt for CLI mode
- `gather-dotfiles.sh` - Injects shell config into context
- `gather-scripts.sh` - Injects script inventory into context

### System Utility Scripts

Scripts tracked in this repository:
- **update-android-sdk**: Android SDK component updater

## System Information

This configuration was created on:
- OS: Ubuntu 24.04 LTS
- Shell: bash
- Editor: VSCodium

Compatible with Ubuntu, Linux Mint, and other Debian-based distributions.

## Blog Configuration

The .bashrc includes shortcuts for managing the 907.life Hugo blog:
- Blog directory: `~/Projects/907-life`
- Hugo server with drafts: `blog`
- Create posts: `newpost YYYY-MM-DD-title`
- Deploy: `npx wrangler deploy`

## What Lives Here

All workstation configuration and personal tooling is tracked in this repo:
- Shell config (bash)
- Editor settings (vscodium)
- Git configuration
- System utilities (`update-android-sdk`)
- Claude CLI mode launcher and system prompt (`cld`, `cli-mode.md`)

## Maintenance

Run the sync script to check for drift and update tracked files:
```bash
~/.dotfiles/sync-dotfiles.sh
```

This checks:
- Stow package symlink status
- Git config changes (auto-copies if changed)
- VSCodium extension changes
- Uncommitted changes in the repository

CLI mode automatically runs this when making configuration changes.

## Notes

- VSCodium settings.json is Stow-managed (symlinked)
- Extensions are listed in `vscodium/extensions.txt` (manual sync via script)
- Git config is NOT stowed - manually synced via `sync-dotfiles.sh`
- CLI mode scripts (`cld`, helpers, system prompt) tracked in bin and claude packages

## License

Personal configuration files - use as you wish.
