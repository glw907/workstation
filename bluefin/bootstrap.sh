#!/usr/bin/env bash
set -euo pipefail

# Bluefin DX (stable) bootstrap for thinkpad-x1, and for the second
# workstation this same directory provisions later.
#
# Decisions and facts referenced here come from docs/MIGRATION-BRIEF.md, in this
# same directory. Read it before changing this script.
#
# Usage:
#   bootstrap.sh devmode   # run once, right after first boot; reboot after
#   bootstrap.sh layer     # run once, after the reboot from `devmode`
#   bootstrap.sh setup     # run once, right after the reboot from `layer`
#   bootstrap.sh restore   # run once, after `setup` and the 1Password CLI
#                          # toggle; restores the pre-migration R2 backup
#
# Two reboots, and they are not optional. `devmode` rebases the image to
# bluefin-dx (a staged bootc switch that only takes effect on boot), and
# `layer` adds the layered RPMs to whatever image is actually booted. Running
# `layer` before the DX reboot would layer onto the non-DX deployment and
# strand the packages when the rebase lands.
#
# Uses plain `sudo`, not the `sudo -A` / claude-askpass flow: that flow
# depends on the `bin` stow package and ~/.local/secrets, neither of which
# exist yet at this point in a fresh install. Run this script interactively
# so sudo can prompt for the password directly.

BLUEFIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_DIR="$(dirname "$BLUEFIN_DIR")"

# Reads a list file, dropping comment and blank lines.
read_list() {
    grep -vE '^[[:space:]]*(#|$)' "$1"
}

# Shared between setup_stow and restore_place_home, which both pre-create
# these dirs (to keep stow from folding them) and then run the same stow.
# Single-sourced from stow-packages.txt so check-drift cannot drift from
# what this script actually stows.
STOW_PACKAGES=()
mapfile -t STOW_PACKAGES < <(read_list "$BLUEFIN_DIR/stow-packages.txt")
STOW_SHARED_DIRS=("$HOME/.local/bin" "$HOME/.claude" "$HOME/.config/khard" \
    "$HOME/.config/systemd/user")

# Where stow_clear_conflicts parks files it moves out of the way.
STOW_CONFLICT_BACKUP="$HOME/.dotfiles-preexisting"

# stow refuses to replace a real file at a target path, and a single conflict
# fails the whole package. On a fresh install that is easy to hit: `gh auth
# login` writes ~/.gitconfig, and anything launched before setup can leave a
# config file behind the same way.
#
# Only files the packages actually provide are considered, so unrelated
# neighbours in a shared target dir (the uv-installed shims in ~/.local/bin,
# say) are never touched. Conflicts are moved rather than deleted: the
# tracked copy supersedes them, but a backup costs nothing and keeps a
# surprise recoverable. Existing symlinks are left alone — they are either
# already ours or something stow should report on its own.
stow_clear_conflicts() {
    local pkg src rel target moved=0
    for pkg in "${STOW_PACKAGES[@]}"; do
        [[ -d "$DOTFILES_DIR/$pkg" ]] || continue
        while IFS= read -r -d '' src; do
            rel="${src#"$DOTFILES_DIR/$pkg/"}"
            target="$HOME/$rel"
            # A target reached through a stow-folded parent symlink resolves
            # to the tracked file inside the repo itself. That is not a
            # conflict, and moving it would gut the repo.
            if [[ -f "$target" && ! -L "$target" ]] \
                && [[ "$(realpath -m "$target")" != "$DOTFILES_DIR"/* ]]; then
                mkdir -p "$(dirname "$STOW_CONFLICT_BACKUP/$rel")"
                mv "$target" "$STOW_CONFLICT_BACKUP/$rel"
                echo "moved aside $target"
                moved=$((moved + 1))
            fi
        done < <(find "$DOTFILES_DIR/$pkg" -type f -print0)
    done
    if [[ $moved -gt 0 ]]; then
        echo "$moved pre-existing file(s) backed up under $STOW_CONFLICT_BACKUP"
    fi
}

# The running image's name, e.g. "bluefin" or "bluefin-dx". Bluefin writes
# this at build time; `ujust devmode` reads the same file to decide which way
# to toggle.
IMAGE_INFO_FILE="${IMAGE_INFO_FILE:-/usr/share/ublue-os/image-info.json}"

current_image_name() {
    jq -rc '."image-name"' "$IMAGE_INFO_FILE" 2> /dev/null || echo unknown
}

# True when the booted deployment is a -dx image. Both `layer` and `setup`
# gate on this: the whole point of the devmode phase is that everything after
# it assumes DX, and silently proceeding on the base image produces a machine
# that looks set up but has no docker, no dx-group, and no DX flatpaks.
on_dx_image() {
    [[ "$(current_image_name)" == *-dx ]]
}

require_dx_image() {
    if on_dx_image; then
        return 0
    fi
    cat >&2 <<EOF
HARD STOP: this is not a Developer Experience image.
  booted image: $(current_image_name)

Run the devmode phase first, then reboot:
  $0 devmode
  sudo systemctl reboot
EOF
    return 1
}

# `ujust devmode` runs `bootc switch --enforce-container-sigpolicy` to the
# matching -dx image tag. It is the project-supported mechanism and is
# preferred over calling bootc directly, so that the image reference stays
# whatever Bluefin says it should be rather than one hardcoded here.
phase_devmode() {
    echo "== devmode: rebase to the Developer Experience image =="
    if on_dx_image; then
        echo "already on $(current_image_name), nothing to do"
        return
    fi

    cat <<'EOF'
`ujust devmode` will prompt three times. Answer:

  "Would you like to enable developer mode?"                 -> yes
  "Do you want to also install the default development
   flatpaks?"                                               -> no
  "Do you want to install extra monospace fonts?"            -> no

The two "no" answers are deliberate. Flatpaks come from flatpaks.txt in this
directory, tracked so the second workstation gets the same set; letting ujust
install its own would put untracked apps on the machine. The fonts are simply
not needed: the base image already ships JetBrains Mono and Symbols Nerd Font
Mono, which is all kitty.conf asks for, and Ptyxis uses the system monospace.

EOF
    ujust devmode

    echo
    echo "Rebase staged. Reboot, then run:"
    echo "  $0 layer"
}

phase_layer() {
    require_dx_image

    echo "== layer: 1Password repo =="
    # No `rpm --import` here: on ostree the rpm database lives under the
    # read-only /usr, so the import fails. Instead the key goes to /etc
    # (mutable) and the repo's gpgkey= points at it; rpm-ostree verifies
    # packages against that file itself at install time.
    # Fetch the signing key and assert its fingerprint before installing it;
    # a repo file with gpgcheck=1 is only as good as the key it points at.
    # Expected fingerprint verified against the key that has validated every
    # 1Password install on thinkpad-x1 since the 2026-08 migration.
    local key_tmp expected_fpr actual_fpr
    expected_fpr="3FEF9748469ADBE15DA7CA80AC2D62742012EA22"
    key_tmp=$(mktemp)
    curl -fsSL https://downloads.1password.com/linux/keys/1password.asc -o "$key_tmp"
    actual_fpr=$(gpg --show-keys --with-colons "$key_tmp" 2>/dev/null \
        | awk -F: '/^fpr:/{print $10; exit}')
    if [[ "$actual_fpr" != "$expected_fpr" ]]; then
        echo "1Password key fingerprint mismatch: got '${actual_fpr}'" >&2
        rm -f "$key_tmp"
        return 1
    fi
    sudo install -m 0644 "$key_tmp" /etc/pki/rpm-gpg/RPM-GPG-KEY-1password
    rm -f "$key_tmp"
    sudo install -m 0644 "$BLUEFIN_DIR/etc/yum.repos.d/1password.repo" \
        /etc/yum.repos.d/1password.repo

    echo "== layer: rpm-ostree install =="
    local list="$BLUEFIN_DIR/layered-packages.txt"
    if [[ ! -f "$list" ]]; then
        echo "layered-packages.txt not found in $BLUEFIN_DIR, nothing to layer" >&2
        exit 1
    fi
    local pkgs=()
    mapfile -t pkgs < <(read_list "$list")
    if [[ ${#pkgs[@]} -eq 0 ]]; then
        echo "layered-packages.txt is empty, nothing to layer" >&2
        exit 1
    fi
    sudo rpm-ostree install --idempotent "${pkgs[@]}"

    echo
    echo "Layering staged. Reboot, then run:"
    echo "  $0 setup"
}

# Every multi-command setup step ends its commands with `|| return 1`.
# phase_setup calls steps inside `if ! "$step"`, and bash suppresses errexit
# for the whole dynamic extent of a condition, so without the explicit
# returns a step reports only its LAST command's status and mid-step
# failures vanish (caught by the 2026-08-30 verification pass).
setup_etc_drops() {
    echo "== setup: /etc drops =="

    sudo mkdir -p /etc/chromium/policies/managed || return 1
    shopt -s nullglob
    local policies=("$BLUEFIN_DIR"/etc/chromium-policies/*.json)
    shopt -u nullglob
    if [[ ${#policies[@]} -eq 0 ]]; then
        echo "no chromium policy files found in $BLUEFIN_DIR/etc/chromium-policies, skipping" >&2
    else
        sudo install -m 0644 "${policies[@]}" /etc/chromium/policies/managed/ || return 1
    fi

    sudo install -m 0644 "$BLUEFIN_DIR/etc/udev/51-android.rules" \
        /etc/udev/rules.d/51-android.rules || return 1
    sudo udevadm control --reload-rules || return 1
    sudo udevadm trigger || return 1
    # The rule grants uaccess via udev TAG+="uaccess" for known Android
    # vendor IDs; no group membership or relogin needed.
}

setup_dx_group() {
    echo "== setup: ujust dx-group =="
    require_dx_image || return 1
    ujust dx-group
}

# Bluefin preinstalls a Flatpak Firefox, and the base image's default browser
# points at it. The brief requires the layered RPM builds instead: Flatpak's
# sandbox blocks the native messaging that 1Password and Claude's browser
# tooling both depend on. Leaving the Flatpak installed means two Firefoxes
# with the sandboxed one still winning every link click.
#
# This sticks. The system Flatpak set is installed by `ujust
# install-system-flatpaks`, which is a manual "for rebasers" recipe, not
# something an image update re-runs. The only automatic hook that touches
# Firefox (privileged-setup.hooks.d/99-flatpaks.sh) writes prefs into an
# extension directory and never installs the app.
setup_remove_conflicting_flatpaks() {
    echo "== setup: remove superseded Flatpaks (layered RPMs, Thunderbird ESR) =="
    local app
    for app in org.mozilla.firefox com.onepassword.OnePassword; do
        if flatpak info "$app" > /dev/null 2>&1; then
            echo "removing $app"
            flatpak uninstall --system -y --delete-data "$app" || return 1
        else
            echo "$app not installed, skipping"
        fi
    done

    # Bluefin's stock set still names org.mozilla.Thunderbird, which Flathub
    # end-of-lifed and rebased to org.mozilla.thunderbird_esr. Thunderbird
    # runs on the monthly channel instead (org.mozilla.thunderbird, in
    # flatpaks.txt; Geoff, 2026-09-29), so drop the ESR the stock set brings.
    for app in org.mozilla.Thunderbird org.mozilla.thunderbird_esr; do
        if flatpak info "$app" > /dev/null 2>&1; then
            echo "removing $app (ESR; the monthly org.mozilla.thunderbird replaces it)"
            flatpak uninstall --system -y --delete-data "$app" || return 1
        fi
    done

    # Hand the default-browser association to the layered RPM. The Fedora 44
    # firefox RPM ships org.mozilla.firefox.desktop, the same desktop id the
    # Flatpak exported, so once the Flatpak is gone the id resolves to the
    # RPM; setting it explicitly covers a system where it pointed elsewhere.
    if [[ -f /usr/share/applications/org.mozilla.firefox.desktop ]]; then
        xdg-settings set default-web-browser org.mozilla.firefox.desktop
        echo "default browser set to org.mozilla.firefox.desktop (layered RPM)"
    else
        echo "WARNING: /usr/share/applications/org.mozilla.firefox.desktop not found;" >&2
        echo "         is the firefox RPM layered? (bootstrap.sh layer)" >&2
    fi
}

setup_flatpaks() {
    echo "== setup: flatpak install =="
    local apps=()
    mapfile -t apps < <(read_list "$BLUEFIN_DIR/flatpaks.txt")
    flatpak install --or-update -y flathub "${apps[@]}"
}

setup_brew() {
    echo "== setup: brew bundle =="
    if ! command -v brew > /dev/null 2>&1; then
        # Bluefin DX ships Homebrew preinstalled; this is a fallback in case
        # that isn't true for this image build. Verify on first boot.
        echo "brew not on PATH, installing Homebrew..."
        NONINTERACTIVE=1 /bin/bash -c \
            "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || return 1
        # The installer does not put brew on PATH; eval by absolute path so
        # the bundle step below works in this same process.
        eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" || return 1
    fi
    eval "$(brew shellenv)" || return 1
    brew bundle --file="$BLUEFIN_DIR/Brewfile"
}

setup_mise_uv() {
    echo "== setup: mise + uv tool installs =="
    eval "$(mise activate bash)" || return 1
    mise use --global node@lts || return 1

    # Python CLI tools ride uv rather than Homebrew. uv-tools.txt is the
    # source of truth; check-drift reconciles `uv tool list` against it.
    local tool
    while IFS= read -r tool; do
        uv tool install "$tool" || return 1
    done < <(read_list "$BLUEFIN_DIR/uv-tools.txt")
}

setup_stow() {
    echo "== setup: stow dotfiles packages =="
    # Pre-create the target dirs that other things also write into, so stow
    # symlinks their direct children instead of folding each dir into one
    # repo symlink. Only the dirs listed here are unfolded; a package's own
    # subdirs (for example ~/.claude/skills) still fold, so anything writing
    # inside one of those lands in ~/.dotfiles.
    mkdir -p "${STOW_SHARED_DIRS[@]}" || return 1
    stow_clear_conflicts || return 1
    (cd "$DOTFILES_DIR" && stow -R "${STOW_PACKAGES[@]}")
}

setup_git_hooks() {
    echo "== setup: repo git hooks =="
    # The pre-commit hook runs gitleaks over staged content; this repo is
    # public, so the hook is the last local line of defense for secrets.
    (cd "$DOTFILES_DIR" && git config core.hooksPath scripts/githooks)
}

setup_vale_styles() {
    echo "== setup: vale style packages =="
    # The Google and Microsoft style trees are deliberately not committed
    # (vale/.gitignore); `vale sync` fetches them into the stowed config.
    # Without this step every Vale run, including the vale-hook Claude hook,
    # errors on an empty StylesPath.
    (cd "$HOME/.config/vale" && vale sync)
}

setup_upkeep_timer() {
    echo "== setup: upkeep timers (weekly drift, monthly model review) =="
    # check-drift.timer arrives via the upkeep stow package; it notifies
    # only when the repo and the live machine disagree.
    systemctl --user daemon-reload || return 1
    systemctl --user enable --now check-drift.timer
    systemctl --user enable --now model-review.timer
}

setup_contacts_timer() {
    echo "== setup: vdirsyncer user timer =="
    # The unit files arrive via the contacts stow package, but a stowed
    # [Install] section is inert until the timer is enabled. The service
    # needs credentials from ~/.local/secrets (fastmail-dav-password), which
    # do not exist until the restore phase or a manual secrets sync, so
    # enabling before then would just fail on every hourly tick.
    systemctl --user daemon-reload || return 1
    if [[ -f "$HOME/.local/secrets" ]]; then
        systemctl --user enable --now vdirsyncer.timer
    else
        echo "skipped enable: no ~/.local/secrets yet. After the secrets"
        echo "sync, run: systemctl --user enable --now vdirsyncer.timer"
    fi
}

# kitty is not the daily terminal on Bluefin -- Ptyxis is, and it ships with
# the image. kitty is installed only as the gate platform for the
# tui-visual-verify skill, whose kitty-shot harness drives a real kitty
# window through kitty's remote control and photographs it. Ptyxis has no
# remote-control equivalent, so nothing else can stand in.
setup_kitty() {
    echo "== setup: kitty upstream installer (TUI verification gate) =="
    local kitty_bin="$HOME/.local/kitty.app/bin/kitty"
    if [[ -x "$kitty_bin" ]]; then
        echo "kitty already installed, skipping"
        return
    fi
    # launch=n keeps the installer from opening a kitty window, which would
    # block a non-interactive run (same fix update-kitty carries).
    curl -fsSL https://sw.kovidgoyal.net/kitty/installer.sh | sh /dev/stdin launch=n || return 1
    if [[ ! -x "$kitty_bin" ]]; then
        echo "kitty install failed: $kitty_bin not found" >&2
        return 1
    fi
    # The installer populates ~/.local/kitty.app only; kitty reaches PATH
    # through these links (the kitty-shot harness invokes bare `kitty`).
    ln -sf "$HOME/.local/kitty.app/bin/kitty" "$HOME/.local/bin/kitty" || return 1
    ln -sf "$HOME/.local/kitty.app/bin/kitten" "$HOME/.local/bin/kitten"
}

# Prints a --schemadir option for a schema that ships inside a GNOME Shell
# extension (dash-to-dock, say), which the global schema cache doesn't
# include. Prints nothing for any other schema. Same function as check-drift's;
# duplicated so each script stays standalone.
schema_dir_opt() {
    [[ "$1" == org.gnome.shell.extensions.* ]] || return 0
    local d
    for d in /usr/share/gnome-shell/extensions/*/schemas \
             "$HOME"/.local/share/gnome-shell/extensions/*/schemas; do
        if grep -qs "id=\"$1\"" "$d"/*.gschema.xml; then
            echo "--schemadir $d"
            return 0
        fi
    done
}

# Always /usr/bin/gsettings: Homebrew's glib puts its own gsettings first on
# PATH, and that build has no dconf module, so it silently falls back to a
# keyfile (~/.config/glib-2.0/settings/keyfile) the desktop never reads.
setup_gnome_settings() {
    echo "== setup: GNOME settings (gnome-settings.txt) =="
    # Manifest values are the serialized form `gsettings get` prints, which
    # `gsettings set` parses back for every key type, so no per-type quoting
    # is needed here.
    local schema key value
    while read -r schema key value; do
        # shellcheck disable=SC2046 # the option is two words on purpose
        /usr/bin/gsettings $(schema_dir_opt "$schema") set "$schema" "$key" "$value" || return 1
    done < <(read_list "$BLUEFIN_DIR/gnome-settings.txt")
}

# Claude Code comes from the Homebrew cask in the Brewfile, installed by
# setup_brew like every other CLI tool. The brief originally called for the
# native installer into ~/.local/bin; the cask is the idiomatic tier for a
# CLI tool here and rides `ujust update` with everything else, so there is no
# separate self-update path to keep track of. Bluefin also ships the cask
# preinstalled, and a native install would shadow it on PATH.
setup_verify_claude_code() {
    echo "== setup: verify Claude Code =="
    if ! command -v claude > /dev/null 2>&1; then
        echo "claude not on PATH after brew bundle" >&2
        return 1
    fi
    echo "claude: $(command -v claude)"
    if [[ -x "$HOME/.local/bin/claude" ]]; then
        echo "WARNING: a native-installer Claude Code at ~/.local/bin/claude" >&2
        echo "         shadows the Homebrew cask. Remove it to keep one" >&2
        echo "         install and one update path." >&2
    fi
}

setup_syncthing() {
    echo "== setup: syncthing user service =="
    brew services start syncthing
}

print_checklist() {
    cat <<'EOF'

== Post-setup verification checklist ==

1Password (brief: known GID mismatch gotcha on ostree):
  - Open 1Password desktop, confirm it unlocks.
  - Confirm `op whoami` works from a terminal.
  - Confirm the browser extension (Firefox and Chromium) connects to the
    desktop app. If it does not: this is the documented helper-tool GID
    mismatch on ostree. Fix script: gist b-/ed2cdc182ae5a92bdcd6b73308832a70.

SELinux (brief: skipping this is a documented cause of broken logins):
  - After restoring anything into /var/home, run:
      sudo restorecon -R -v /var/home/glw907

Browsers:
  - chrome://policy in Chromium shows the three managed policies applied.
  - Firefox 1Password integration connects (needs the RPM build, not flatpak).
  - `flatpak list | grep -iE 'firefox|onepassword'` returns nothing: the
    preinstalled Flatpak builds are gone and the layered RPMs are what runs.
  - `xdg-settings get default-web-browser` prints org.mozilla.firefox.desktop,
    which with the Flatpak gone resolves to the RPM's desktop file under
    /usr/share/applications, not the Flatpak export.
  - `about:support` in Firefox shows an RPM install path, not /app or
    /var/lib/flatpak.

Thunderbird (interim Fastmail client; thunderbird/README.md):
  - `flatpak list | grep -i thunderbird` shows only org.mozilla.thunderbird
    (the monthly channel); the stock ESR build is gone.
  - Launch Thunderbird once and sign in to Fastmail (geoff@907.life, OAuth;
    no app password). Link calendars (caldav.fastmail.com) and contacts
    (carddav.fastmail.com) as thunderbird/README.md describes.
  - Quit Thunderbird, then run `thunderbird-theme-sync`: it installs the GNOME
    theme, the color overrides, and user.js into the new profile.
  - `thunderbird-theme-sync --check` prints "theme and overrides match".

Android:
  - `adb devices` sees a plugged-in device (uaccess tagging applies
    immediately on replug, no login required).

Homebrew / mise / uv:
  - `brew doctor`
  - `mise doctor`
  - `uv tool list` matches bluefin/uv-tools.txt (check-drift verifies)
  - `vale sync` already ran; `vale --version` works and ~/.config/vale/styles
    is populated

Dotfiles:
  - `stow -n $(grep -vE '^[[:space:]]*(#|$)' bluefin/stow-packages.txt)`
    reports no conflicts (already stowed by this script; -n dry-runs to confirm).

Terminal:
  - Ptyxis is the daily terminal and needs no setup; it ships with the image.

TUI verification gate (tui-visual-verify / kitty-shot):
  - `kitty --version` and `xdotool --version` both work.
  - Launch kitty, then confirm `xdotool search --name kitty` finds it. If it
    finds nothing, the `linux_display_server x11` line in kitty.conf did not
    take and kitty is running on native Wayland, where xdotool and
    ImageMagick's `import` are both blind. The harness depends on this.
  - Glyphs render rather than tofu (JetBrains Mono + Symbols Nerd Font Mono,
    both already in the base image; nothing is installed for them).

Claude Code, syncthing:
  - `claude --version`, and `command -v claude` points into
    /home/linuxbrew/.linuxbrew/bin, not ~/.local/bin
  - syncthing web UI reachable at http://127.0.0.1:8384

Image:
  - `rpm-ostree status` shows a bluefin-dx image, and lists 1password,
    1password-cli, firefox, and chromium as layered packages.
  - `docker --version` works (DX ships it; its absence means the devmode
    rebase never landed).

Next: in 1Password, sign in and enable Settings -> Developer -> "Integrate
with 1Password CLI" (GUI-only toggle).

FIRST WORKSTATION ONLY (the 2026-08 Mint migration): open a NEW terminal --
the shell that ran setup never sourced the just-stowed .bashrc, so mise/npx
are not on its PATH -- then run:

  ~/.dotfiles/bluefin/bootstrap.sh restore

It restores the pre-migration R2 backup with the same hard stops. A second
workstation has no backup to restore and is DONE at this point; its home
directory content arrives by other means (git clones, syncthing).
EOF
}

# --- restore phase -----------------------------------------------------------
# Restores the 2026-08 pre-migration backup step for step. The retired
# MIGRATION-RUNBOOK.md section 4 (git history, removed 2026-08-30) was the
# specification; this phase is now the record.
# Fail-fast and rerunnable: completed steps detect their own state and skip.

RESTORE_STAGING="$HOME/restore-staging"
AGE_KEY_CACHE="/dev/shm/.age-key-$UID"
BACKUP_SHA256="db0c2c041d2587ac300421734e4d4f32f436832242d385f20cc913aee0a0dbe1"
AGE_PUBKEY="age197mcd2m3z90t49n9t5v3ujjntw7krfkw5y9sjfc545v28qvezugshg7jgk"

# True once the tarball has been decrypted and extracted (manifest.txt is the
# last thing restore_extract writes), used by restore_reassemble,
# restore_verify_checksum, and restore_extract to skip work already done.
restore_staging_extracted() {
    [[ -f "$RESTORE_STAGING/manifest.txt" ]]
}

restore_preflight() {
    echo "== restore: preflight =="
    local missing=()
    local cmd
    for cmd in npx op age stow rsync git; do
        command -v "$cmd" > /dev/null 2>&1 || missing+=("$cmd")
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "missing commands: ${missing[*]} (run 'bootstrap.sh setup' first)" >&2
        return 1
    fi
}

# Runbook 4.1: one op call, cached in tmpfs. sync.sh reads the same cache, so
# the secrets step below makes no additional op call.
restore_fetch_key() {
    echo "== restore: age identity from 1Password =="
    if [[ -s "$AGE_KEY_CACHE" ]]; then
        echo "key already cached, skipping op call"
    else
        op item get "Workstation age encryption key" --fields notesPlain --reveal \
            | sed 's/^"//;s/"$//' > "$AGE_KEY_CACHE"
        chmod 600 "$AGE_KEY_CACHE"
    fi
    local pubkey
    pubkey="$(age-keygen -y "$AGE_KEY_CACHE")"
    if [[ "$pubkey" != "$AGE_PUBKEY" ]]; then
        echo "age public key mismatch: got $pubkey" >&2
        shred -u "$AGE_KEY_CACHE"
        return 1
    fi
}

# Runbook 4.2.
restore_secrets() {
    echo "== restore: local secrets from the age store =="
    "$DOTFILES_DIR/scripts/secrets/sync.sh" --local
    # shellcheck disable=SC1091
    source "$HOME/.local/secrets"
}

# Runbook 4.3. Existing non-empty chunk files are kept, so a rerun resumes
# rather than refetching.
restore_reassemble() {
    echo "== restore: reassemble tarball from R2 =="
    if restore_staging_extracted; then
        echo "staging already extracted, skipping"
        return
    fi
    if [[ -s "$RESTORE_STAGING/pre-bluefin-backup.tar.age" ]]; then
        echo "tarball already assembled, skipping"
        return
    fi
    mkdir -p "$RESTORE_STAGING"
    export CLOUDFLARE_ACCOUNT_ID=120c269ad6d3dfbe6d63a0bb53758ca0
    local suffixes=(aa ab ac ad ae af ag ah ai aj ak al am an ao ap aq ar as at)
    local s key
    for s in "${suffixes[@]}"; do
        key="pre-bluefin/chunk-$s"
        if [[ -s "$RESTORE_STAGING/chunk-$s" ]]; then
            echo "chunk-$s already present"
            continue
        fi
        if ! npx -y wrangler r2 object get --remote "workstation-backup/$key" \
                --file "$RESTORE_STAGING/chunk-$s" 2> /dev/null; then
            rm -f "$RESTORE_STAGING/chunk-$s"
            break
        fi
        echo "fetched chunk-$s"
    done
    local chunks=("$RESTORE_STAGING"/chunk-*)
    echo "fetched ${#chunks[@]} chunks"
    cat "${chunks[@]}" > "$RESTORE_STAGING/pre-bluefin-backup.tar.age"
    rm -f "${chunks[@]}"
}

# Runbook 4.4: hard stop. Do not decrypt an unverified blob.
restore_verify_checksum() {
    echo "== restore: verify backup checksum =="
    if restore_staging_extracted; then
        echo "staging already extracted, skipping"
        return
    fi
    local sum
    sum="$(sha256sum "$RESTORE_STAGING/pre-bluefin-backup.tar.age" | cut -d' ' -f1)"
    if [[ "$sum" != "$BACKUP_SHA256" ]]; then
        echo "HARD STOP: checksum mismatch: got $sum" >&2
        echo "expected:  $BACKUP_SHA256" >&2
        return 1
    fi
    echo "checksum matches the recorded value"
}

# Runbook 4.5.
restore_extract() {
    echo "== restore: decrypt and extract =="
    if restore_staging_extracted; then
        echo "staging already extracted, skipping"
        return
    fi
    age -d -i "$AGE_KEY_CACHE" "$RESTORE_STAGING/pre-bluefin-backup.tar.age" \
        | tar -x -C "$RESTORE_STAGING"
    rm -f "$RESTORE_STAGING/pre-bluefin-backup.tar.age"
    echo "--- manifest ---"
    cat "$RESTORE_STAGING/manifest.txt"
}

# Runbook 4.6: additive, never destructive. --ignore-existing everywhere so
# the stow symlinks (git-tracked copies) win over the backup copies.
restore_place_home() {
    echo "== restore: selective restore into \$HOME =="
    local home_src="$RESTORE_STAGING/home"
    local d item

    # Unfold any stow-folded directories among the restore targets first, so
    # the rsyncs below write into real directories and never into
    # ~/.dotfiles itself. Parents (.local, .config) can be the folded link
    # when they didn't exist at first stow, so check them too.
    for d in "$HOME/.local" "$HOME/.config" "$HOME/.claude" "$HOME/.local/bin" \
             "$HOME/.config/khard" "$HOME/.config/systemd/user"; do
        if [[ -L "$d" ]]; then
            rm "$d" && mkdir -p "$d"
        fi
    done
    # Pre-create the shared target dirs so the re-stow can't re-fold them.
    mkdir -p "${STOW_SHARED_DIRS[@]}"
    stow_clear_conflicts
    (cd "$DOTFILES_DIR" && stow -R "${STOW_PACKAGES[@]}")

    # Direct restores: plain directories/files, no stow overlap.
    for item in .ssh .contacts .vdirsyncer .android Documents corpus Pictures; do
        if [[ -e "$home_src/$item" ]]; then
            rsync -a --ignore-existing "$home_src/$item" "$HOME/"
        fi
    done
    chmod 700 "$HOME/.ssh" 2> /dev/null || true
    chmod 600 "$HOME/.ssh"/* 2> /dev/null || true

    # .local/share/keyrings: not a stow target, but nested under .local/share
    # so it needs its own destination, not the top-level loop above.
    mkdir -p "$HOME/.local/share"
    if [[ -e "$home_src/.local/share/keyrings" ]]; then
        rsync -a --ignore-existing "$home_src/.local/share/keyrings" "$HOME/.local/share/"
    fi

    # .local/bin: the `bin` stow package also targets this dir, so merge,
    # don't clobber. nvim-journal is excluded: neovim is dropped on Bluefin.
    if [[ -d "$home_src/.local/bin" ]]; then
        rsync -a --ignore-existing --exclude nvim-journal "$home_src/.local/bin/" "$HOME/.local/bin/"
    fi

    # Selected .config subdirs.
    mkdir -p "$HOME/.config"
    # vale is deliberately absent: ~/.config/vale is a stow fold on a fresh
    # machine, an rsync into it would write backup bytes inside the repo,
    # and the styles it held are regenerated by `vale sync` anyway.
    for item in chromium gcloud gh op 1Password poplar khard google-workspace systemd; do
        if [[ -e "$home_src/.config/$item" ]]; then
            rsync -a --ignore-existing "$home_src/.config/$item" "$HOME/.config/"
        fi
    done
    for item in "$home_src"/.config/jrnl*; do
        if [[ -e "$item" ]]; then
            rsync -a --ignore-existing "$item" "$HOME/.config/"
        fi
    done

    # .claude: memory/history/projects are runtime state, not stow-tracked.
    # Every top-level name in the claude stow package is excluded outright:
    # the backup holds Mint-era stow symlinks for those, and recreating them
    # through today's stow-folded dirs loops (ELOOP). The exclude set is
    # derived from the package dir so it cannot drift from what stow places;
    # the git-tracked copies placed by stow above are the canonical ones.
    if [[ -d "$home_src/.claude" ]]; then
        local claude_excludes=() entry
        for entry in "$DOTFILES_DIR/claude/.claude"/*; do
            claude_excludes+=(--exclude="/$(basename "$entry")")
        done
        rsync -a --ignore-existing "${claude_excludes[@]}" \
            "$home_src/.claude/" "$HOME/.claude/"
    fi

    # The age key file the brief documents as asc-key.txt: restore it to the
    # same relative path under $HOME it had in the backup.
    local found rel
    found="$(find "$home_src" -iname 'asc-key.txt' 2> /dev/null | head -1)"
    if [[ -n "$found" ]]; then
        rel="${found#"$home_src"/}"
        mkdir -p "$(dirname "$HOME/$rel")"
        if [[ ! -e "$HOME/$rel" ]]; then
            cp "$found" "$HOME/$rel"
        fi
        echo "asc-key.txt restored to ~/$rel"
    else
        echo "WARNING: asc-key.txt not found in the backup; find it manually" >&2
    fi

    # Assert the unfold + restore above didn't write into the dotfiles repo.
    if [[ -n "$(git -C "$DOTFILES_DIR" status --short)" ]]; then
        echo "HARD STOP: restore dirtied ~/.dotfiles:" >&2
        git -C "$DOTFILES_DIR" status --short >&2
        return 1
    fi
}

# Runbook 4.7.
restore_projects() {
    echo "== restore: projects from the tarball =="
    local item
    mkdir -p "$HOME/Projects"
    # The workstation repo is ~/.dotfiles (stow's home); this link puts it beside the other repos.
    ln -sfn "$HOME/.dotfiles" "$HOME/Projects/workstation"
    for item in aksailingclub-sveltekit cairn-scratch ecxc-ski-agent-memory; do
        if [[ -d "$RESTORE_STAGING/projects/$item" ]]; then
            rsync -a --ignore-existing "$RESTORE_STAGING/projects/$item/" "$HOME/Projects/$item/"
        fi
    done
    if [[ ! -d "$HOME/Projects/smallbusinessak-org" ]]; then
        git clone "$RESTORE_STAGING/projects/smallbusinessak-org.bundle" \
            "$HOME/Projects/smallbusinessak-org"
    fi
}

# Runbook 4.8: interactive sudo (claude-sudo-setup hasn't run yet).
restore_etc() {
    echo "== restore: /etc drops from etc-capture =="
    local android_rule
    android_rule="$(find "$RESTORE_STAGING/etc-capture" -iname '51-android.rules' | head -1)"
    if [[ -n "$android_rule" ]]; then
        sudo cp "$android_rule" /etc/udev/rules.d/
        sudo udevadm control --reload-rules && sudo udevadm trigger
    fi
    sudo mkdir -p /etc/chromium/policies/managed
    find "$RESTORE_STAGING/etc-capture" -iname '*.json' -ipath '*chromium*' -print0 \
        | xargs -0 -r -I{} sudo cp {} /etc/chromium/policies/managed/
}

# Runbook 4.9: mandatory. Bluefin enforces SELinux; the Mint backup carries
# no labels, and skipping this is a documented cause of broken logins.
restore_selinux() {
    echo "== restore: SELinux contexts =="
    sudo restorecon -R -v /var/home/glw907
}

# Runbook 4.11 (4.10 is the on-demand extras archive, not part of restore).
restore_cleanup() {
    echo "== restore: cleanup =="
    shred -u "$AGE_KEY_CACHE"
    rm -rf "$RESTORE_STAGING"
}

restore_checklist() {
    cat <<'EOF'

== Restore done. Remaining judgment items (runbook "verify on first boot") ==

- Diff the restored ~/.local/bin against the bin stow package and delete any
  Mint-only stray.
- Re-authentication and verification checklists remain; the retired
  MIGRATION-RUNBOOK.md (git history, removed 2026-08-30) carries them.

Next: launch Claude Code (first launch asks you to log in), then hand it:

  claude "The Bluefin restore phase is done. Recover the retired
  MIGRATION-RUNBOOK.md from git history and run its re-authentication
  and verification sections."
EOF
}

phase_restore() {
    local steps=(
        restore_preflight
        restore_fetch_key
        restore_secrets
        restore_reassemble
        restore_verify_checksum
        restore_extract
        restore_place_home
        restore_projects
        restore_etc
        restore_selinux
        restore_cleanup
    )
    local step
    for step in "${steps[@]}"; do
        if ! "$step"; then
            echo "phase_restore: stopped at $step (fix and rerun; completed steps skip themselves)" >&2
            exit 1
        fi
    done
    restore_checklist
}

phase_setup() {
    # Bare call, outside any condition, so errexit is live and a non-DX
    # image hard-stops the whole phase (the README promises this).
    require_dx_image

    local steps=(
        setup_etc_drops
        setup_dx_group
        setup_remove_conflicting_flatpaks
        setup_flatpaks
        setup_brew
        setup_mise_uv
        setup_stow
        setup_git_hooks
        setup_vale_styles
        setup_upkeep_timer
        setup_contacts_timer
        setup_kitty
        setup_gnome_settings
        setup_verify_claude_code
        setup_syncthing
    )
    local failed=()
    local step
    for step in "${steps[@]}"; do
        if ! "$step"; then
            echo "FAILED: $step" >&2
            failed+=("$step")
        fi
    done

    print_checklist

    if [[ ${#failed[@]} -gt 0 ]]; then
        echo >&2
        echo "phase_setup: ${#failed[@]} step(s) failed: ${failed[*]}" >&2
        exit 1
    fi
}

case "${1:-}" in
    devmode)
        phase_devmode
        ;;
    layer)
        phase_layer
        ;;
    setup)
        phase_setup
        ;;
    restore)
        phase_restore
        ;;
    *)
        echo "Usage: $0 {devmode|layer|setup|restore}" >&2
        exit 1
        ;;
esac
