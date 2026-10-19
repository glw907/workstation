# Moving thinkpad-x1 to Proton Pass

Pavilion finished its move from 1Password to Proton Pass on 2026-10-19
(workstation#96 and #97). This page lists the per-host steps that thinkpad-x1
still owes. A Claude session on thinkpad-x1 follows it with Geoff at the
keyboard. Delete the page in the commit that records the last step.

The secret scripts on `main` no longer read 1Password. Until step 3 stores
the host's agent token, `secret-set.sh` and `sync.sh` stop with "run
ws-pass-key --store", and `check-drift` reports `path=none`. Pulling first is
safe because nothing else depends on them, but run the steps in one sitting.

Use `sudo -A` throughout. If it fails, run `claude-sudo-setup`, which now
takes the password in a dialog. Claude never runs `pass-cli`; the
`claude-block-pass` hook denies it.

1. Bring the checkout and tools current:
   ```bash
   cd ~/.dotfiles && git pull --ff-only
   stow -R bin
   claude-tooling-sync apply
   brew bundle --file ~/.dotfiles/bluefin/Brewfile
   flatpak install -y flathub com.belmoussaoui.Authenticator
   ```
   The Brewfile brings `proton-pass-cli`. GNOME Authenticator holds the Proton
   account's second factor, and Geoff ruled that thinkpad-x1 gets it too. Turn
   its notifications off at install, per "Calm desktop" in `bluefin-admin.md`.
   Geoff adds the TOTP entry himself.
2. Clone the servers repo (self-hosting task F6c), so the key check can run
   there:
   ```bash
   git clone https://github.com/glw907/servers.git ~/Projects/servers
   echo '.claude/worktrees/' >> ~/Projects/servers/.git/info/exclude
   ```
   Acceptance: `privacy-check.sh` in that repo exits 0 on a clean file.
3. Geoff creates the host's agent token in a throwaway `pass-cli` session:
   `pass-cli agent create thinkpad-scripts --expiration 3m --vault Workstation`
   (viewer role on that vault only). He then runs `ws-pass-key --store` and
   enters the token in the hidden dialog. `ws-pass-key --status` must print
   `path=proton`.
4. Check the keyring after a reboot. `ws-pass-key` reads the token from GNOME
   Keyring, and thinkpad-x1 logs in automatically (pavilion does not). An
   automatic login may leave the login keyring locked, so the first read can
   raise an unlock prompt or fail. Reboot, then run `ws-pass-key --status`
   before anything else. If it prompts or fails, stop and ask Geoff whether to
   accept the prompt or turn auto-login off as on pavilion.
5. Run the key check (self-hosting task W5). Its full text is in
   `~/Projects/initiatives/self-hosting/plans/2026-10-17-self-hosting-plan.md`.
   Clear the cached age key, fetch it through `ws-pass-key` alone, decrypt the
   age store, and compare the result with `~/.local/secrets` by hash, never
   printing a value. Then do a `secret-set.sh` round trip on a scratch name
   with `VALUES` and `LOCAL_SECRETS` pointed at scratch copies, run
   `sync.sh --local` with the cache cleared, and read the expiry line from
   `check-drift`. Any mismatch is a hard stop: 1Password stays until it is
   resolved.
6. Remove 1Password the way pavilion did:
   - Delete the leftovers: the 1Password autostart entry under
     `~/.config/autostart/`, the 1Password native-messaging manifests in each
     browser's `NativeMessagingHosts` directory, and the 1Password beta app
     folder if one exists. List each with `find` and show Geoff before
     deleting.
   - Remove the `/etc/yum.repos.d/1password.repo` file and its RPM signing key
     from `/etc/pki/rpm-gpg/`.
   - Remove any 1Password Flatpak (`flatpak list | grep -i 1password`).
   - Update this host's Claude memory notes that still name 1Password (grep
     `~/.claude/projects/*/memory/`).
   - Stage the uninstall with
     `sudo -A rpm-ostree uninstall 1password 1password-cli`. Geoff reboots;
     `rpm-ostree rollback` restores it if needed.
   - After the reboot, `rpm-ostree status` shows `LayeredPackages: chromium`
     only, and `check-drift` is clean.
7. Record the result. In `~/Projects/initiatives/self-hosting/plans/STATUS.md`,
   mark W5, F6c, and the agent token done on thinkpad-x1 with the date, and
   note the 1Password removal. Delete this page and its line in
   `docs/STATUS.md` in the same dotfiles commit.
