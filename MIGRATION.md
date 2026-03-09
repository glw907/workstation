# Migration Checklist: Ubuntu → Linux Mint

Complete guide for transferring your system to Linux Mint.

## ✅ Already Backed Up (in this repo)

- [x] Shell configuration (.bashrc, .profile)
- [x] Git configuration
- [x] Claude CLI setup (modes and settings)
- [x] Custom scripts (cld, research, android tools)
- [x] VSCodium settings and extensions

## 🔧 Additional Items to Handle

### 1. Package Lists (Optional - for reference)

Generate a list of installed packages:

```bash
# APT packages (2034 installed)
apt list --installed > ~/apt-packages.txt

# Snap packages (23 installed)
snap list > ~/snap-packages.txt

# Manually installed packages (excluding dependencies)
apt-mark showmanual > ~/apt-manual.txt
```

**Note**: Don't restore all packages automatically - Linux Mint may have different defaults. Use these lists as **reference** for what you had installed.

### 2. Desktop Settings (GNOME → Cinnamon)

**Important**: Ubuntu uses GNOME, Mint uses Cinnamon. Settings won't transfer directly.

Export current GNOME settings for reference:

```bash
dconf dump / > ~/gnome-settings.dconf
```

Key settings to manually reconfigure in Mint:
- Wallpaper: `~/Pictures/Wallpapers/nord-gradient.png`
- Keyboard shortcuts
- Theme preferences
- Panel/dock configuration
- Default applications

### 3. Browser Data

You have multiple browsers configured:
- **Google Chrome** (stable, beta, unstable)
- **Brave Browser**
- **Chromium**
- Possibly **Firefox**

**Recommended approach**:
- Use browser's built-in sync (Chrome Sync, Firefox Sync, Brave Sync)
- Or manually backup: `~/.config/google-chrome`, `~/.config/BraveSoftware`, etc.
- Export bookmarks as HTML backup (File → Bookmarks → Export)

### 4. 1Password

Your 1Password config is in `~/.config/1Password/`:
- Most data syncs via cloud
- Local settings/preferences may not transfer
- **Recommended**: Just reinstall 1Password on Mint and sign in
- Cache/database will rebuild automatically

### 5. **Important: 907.life Blog Project**

Your Hugo blog is in `~/Projects/907-life/`:

```bash
# Back up your blog project
cd ~
tar -czf 907-life-backup.tar.gz Projects/907-life/

# Or use git (if it's a git repo)
cd ~/Projects/907-life
git remote -v  # Check if pushed to remote
git status     # Check for uncommitted changes
```

**Critical**: Make sure all blog content is committed and pushed to GitHub/remote!

### 6. GitHub CLI Configuration

Your `gh` CLI is already authenticated. To preserve:

```bash
# Check current auth status
gh auth status

# Export token (save securely!)
gh auth token > ~/gh-token.txt
chmod 600 ~/gh-token.txt

# On new system: gh auth login --with-token < gh-token.txt
```

Or just run `gh auth login` on Mint and re-authenticate.

### 7. SSH Keys

You have no SSH keys currently (`~/.ssh/authorized_keys` is empty).
- Nothing to backup here
- Generate new SSH keys on Mint if needed: `ssh-keygen -t ed25519 -C "your@email.com"`

### 8. GPG Keys

No GPG keys found - nothing to backup.

### 9. Application-Specific Configs

Check `~/.config/` for other apps you care about:
- **kdenlive** (video editor config found)
- **evolution** (email client - if used)
- Any other apps in `~/.config/` worth preserving?

Backup specific app configs:

```bash
# Example: backup kdenlive settings
cp -r ~/.config/kdenlive* ~/kdenlive-backup/
```

### 10. Android SDK

Your Android SDK is in `~/Android/`:
- Self-contained, can be copied as-is
- Or follow `android/README.md` to reinstall fresh on Mint
- Backup: `tar -czf android-sdk-backup.tar.gz ~/Android/`

### 11. Fonts

Check for custom fonts:

```bash
ls ~/.local/share/fonts/
ls ~/.fonts/
```

Backup any custom fonts for transfer.

## 📋 Migration Day Checklist

### Before Leaving Ubuntu

1. [ ] Run dotfiles setup (already done ✓)
2. [ ] Generate package lists for reference
3. [ ] Export browser bookmarks (HTML backup)
4. [ ] Verify `~/Projects/907-life` is pushed to git
5. [ ] Backup any other `~/Projects/*` directories
6. [ ] Export GNOME settings for reference
7. [ ] Backup Android SDK (or note to reinstall)
8. [ ] Save any files from `~/Documents`, `~/Downloads`, `~/Pictures`
9. [ ] Export `gh` token or note to re-authenticate
10. [ ] Double-check `~/.config/` for app configs to preserve

### On Linux Mint

1. [ ] Install base applications:
   - VSCodium: https://vscodium.com/
   - Claude CLI: https://docs.claude.ai/docs/claude-code
   - 1Password: https://1password.com/downloads/linux/
   - GitHub CLI: `sudo apt install gh`

2. [ ] Restore dotfiles:
   ```bash
   git clone https://github.com/glw907/workstation.git ~/.dotfiles
   cd ~/.dotfiles
   stow bash bin claude vscodium git
   source ~/.bashrc
   ```

3. [ ] Authenticate services:
   - `gh auth login`
   - Install and sign into 1Password
   - Sign into browser(s) for sync

4. [ ] Restore projects:
   ```bash
   mkdir -p ~/Projects
   cd ~/Projects
   git clone <your-blog-repo> 907-life
   ```

5. [ ] Install Android SDK (if needed):
   - Follow `~/dotfiles/android/README.md`

6. [ ] Configure desktop settings:
   - Set wallpaper
   - Configure keyboard shortcuts
   - Set up panels/applets
   - Install themes if desired

7. [ ] Selectively install packages:
   - Review `~/apt-packages.txt`
   - Install only what you actually use

## 🎯 Recommended Backup Script

Create a quick backup of everything not in dotfiles:

```bash
#!/bin/bash
# Save as: ~/create-migration-backup.sh

BACKUP_DIR=~/ubuntu-migration-backup
mkdir -p "$BACKUP_DIR"

echo "Creating migration backup in $BACKUP_DIR..."

# Package lists
apt list --installed > "$BACKUP_DIR/apt-packages.txt"
snap list > "$BACKUP_DIR/snap-packages.txt"
apt-mark showmanual > "$BACKUP_DIR/apt-manual.txt"

# Desktop settings
dconf dump / > "$BACKUP_DIR/gnome-settings.dconf"

# GitHub token
gh auth token > "$BACKUP_DIR/gh-token.txt"
chmod 600 "$BACKUP_DIR/gh-token.txt"

# Check for projects
if [ -d ~/Projects ]; then
    echo "Checking Projects directory..."
    ls -la ~/Projects > "$BACKUP_DIR/projects-list.txt"
fi

echo "✓ Backup complete: $BACKUP_DIR"
echo ""
echo "Remember to also backup:"
echo "  - Browser bookmarks (export as HTML)"
echo "  - ~/Projects/* (use git push or manual backup)"
echo "  - Any files in ~/Documents, ~/Pictures, ~/Downloads"
```

## 💡 Tips

- **Linux Mint vs Ubuntu**: Mint is Ubuntu-based, so most things work identically
- **Cinnamon vs GNOME**: Different desktop environment - embrace the differences!
- **Don't over-restore**: Fresh start is good - only install packages you actually use
- **Use cloud sync**: Browsers, 1Password, and git handle most data automatically
- **Test the dotfiles setup**: Run `sync-dotfiles.sh` to verify all Stow packages are in sync

## ⚠️ Don't Forget

1. **Blog project**: Ensure `~/Projects/907-life` is safely in git
2. **Browser data**: Export bookmarks, verify sync is working
3. **Personal files**: Documents, Pictures, Downloads folders
4. **Screenshots**: Any temporary files you want to keep

---

Good luck with the migration! 🚀
