# Update cadence and rollback

Updates are checked automatically every 6 hours; a fetched system image applies at
the next reboot, not immediately. This means "did the update work" is answered after
a reboot, not after `ujust update` returns.

`workstation-sync` runs daily on each host from a `Persistent=true` user timer. GitHub is the hub,
so the hosts never need a route to each other. It fast-forwards `~/.dotfiles` and each repo in
`~/Projects` that sits on its default branch, clean, with no live session. It then applies the
dotfiles, installs what the manifests list and the host lacks (`workstation-install`, GNOME settings and plugins
included), runs `workstation-update`, pairs Syncthing, and ends with `check-drift`. It never
removes anything, and `/etc` drops and layered RPMs stay with the `check-drift` report because a
timer has no sudo. Only a failure notifies; `workstation-sync --status` prints the last result, and
`journalctl --user -u workstation-sync` holds the log. `check-drift --work-only` lists uncommitted,
unpushed, and behind repos and any Syncthing conflict.

Syncthing shares `~/Documents` and each project's Claude memory, and nothing else: transcripts are
plaintext and stay local, and git repos and secrets travel through GitHub. `.stignore` in
`~/.claude/projects` holds that line. Device IDs live in `bluefin/syncthing-devices.txt`. Syncthing
renames the older side of a conflict, so `workstation-syncthing` unions any `MEMORY.md` conflict back
into the index. Other conflict copies wait for a person, and `check-drift` names them.

Rollback playbook:

1. `bootc status` to see the current and previous deployments.
2. `ujust rebase-helper` to pick an earlier date-tagged build, or `bootc rollback` to
   go back one deployment directly.
3. Reboot to apply.
4. If the issue was a layered package, check whether it's still valid on the older
   image before re-layering it — `rpm-ostree install` state travels with each
   deployment.
