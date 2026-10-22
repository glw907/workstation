---
name: vps-conventions
description: Use when writing or modifying systemd units (services, timers, path units), cloud-init user-data, provisioning or deploy scripts, or anything that places files, locks, or directories on a Linux VPS (AlmaLinux/RHEL-family). Also use when choosing where a lock file, temp file, or state file lives, or when a unit fails with mount-namespacing or missing-directory errors. Also use when auto mode denies an ssh step to a server, or before adding an ssh allow rule.
---

# VPS conventions

Rules for box-side infrastructure on this workstation's estates (dubplate and
successors). Not a general sysadmin reference — `man systemd.exec` exists.
This skill holds the judgment calls that generic references skip, each one
paid for by a production failure.

## Directory lifetimes decide where things live

| Path | Lifetime | Belongs there | Never there |
|---|---|---|---|
| `RuntimeDirectory=` (`/run/<x>`) | Deleted when the unit stops; tmpfs, gone at boot | Per-run scratch, credential temp files | Locks, anything a second process or unit reads |
| `StateDirectory=` / `/var/lib/<x>` | Persistent | Lock files, ledgers, run reports | Secrets that should die with the run |
| `PrivateTmp=` | Private to the unit, gone at stop | The unit's own `/tmp` use | Anything shared |

- **A lock file in a RuntimeDirectory is a bug.** The directory vanishes
  between runs (interactive tools die on `exec N>` under `set -e`), and
  systemd deletes the lock file at unit stop, so a long-lived holder keeps
  an unlinked inode while the next run locks a fresh file — mutual
  exclusion silently lost. Locks go on a persistent path, and the acquirer
  `mkdir -p`s the parent first (self-healing beats lifecycle coupling).
- **RuntimeDirectory is not reference-counted across units.** Two units
  naming the same directory: the first to stop removes it. Never share one
  expecting persistence.

## Hardening

Every service unit carries `NoNewPrivileges=yes`, `PrivateTmp=yes`, and
`ProtectSystem=strict` with explicit `ReadWritePaths=` for its real write
targets — including template units (`foo@.service`) and OnFailure helpers,
which are the ones that get forgotten. Timers carry `RandomizedDelaySec`;
know that `Persistent=true` fires missed runs at boot.

- **A `ReadWritePaths=` entry must exist on the host before the unit
  starts** or startup fails with "Failed to set up mount namespacing". The
  unit's own script cannot create it; the deploy/provision step pre-creates
  it, and the deploy comment names every unit that depends on it.
- New directories under `/var/lib` on an SELinux-enforcing box inherit
  `var_lib_t` — fine for unconfined services, but verify once on the first
  real deploy rather than assuming.

## Path units and triggers

`PathChanged=` fires on close-after-write; `PathModified=` on every write —
choose deliberately for `touch`-style triggers. The path unit deactivates
while its service runs and re-arms on exit: events coalesce to at most one
follow-up, and events in the re-arm gap are lost. A path-unit trigger is
therefore only acceptable with a timer backstop. The trigger directory must
be writable by every writer under their hardening (`RuntimeDirectory=` on
both, or `MakeDirectory=` on the path unit).

## cloud-init

Runs at **first boot only**. It never converges a live box: a package added
to `user-data.yaml` reaches existing boxes only via a live remediation, and
the change lands in the same commit as the runbook's presence-gate update,
so a fresh provision and the gate can't drift apart. Before adding a
package to a `set -e` first-boot script, prove it exists in the target
repos (`podman run --rm almalinux:10 dnf -q list <pkg>`) — a guessed
package name bricks first boot unattended. Order runcmd so an optional
repo's failure can't take down packages that don't need it.

## Deploy scripts

Idempotent, with a `--check` mode preserved for every step. Know your
manifest semantics: rsync exits 23 on a missing source, so a deleted file
still listed in a manifest array aborts the whole deploy — manifest edits
land in the same commit as the deletion. Stage remote files via `mktemp`,
never fixed `/tmp` names. Pin and checksum anything piped to a root shell.

## Risky remote steps under auto mode

Auto mode ignores ssh allow rules, narrow prefixes included, so the classifier judges every
`ssh` command on its own terms. The servers cutover's stub proof on 2026-10-22 showed it: with
both `Bash(ssh -o BatchMode=yes geoff@ward.907.life *)` and a narrower `... sudo stalwart-jmap *`
rule in place, `stalwart-jmap destroy` over ssh was still denied as Unverifiable Deletion Scope.
Exact rules for repo scripts did run.

A remote step the classifier won't clear, such as a deletion or a DNS change, goes in a
reviewed script in the repo. The script takes its targets as arguments and prints them before
it acts, so the transcript shows exactly what changes. It refuses anything ambiguous, such as a
leading-dash id, a folder, or a pattern, and does one thing. Give it an exact
`permissions.allow` rule per invocation shape, and land the script and its rule through review
together. The servers repo's `scripts/ward-mail-delete.sh` and `scripts/mx-switch.sh` are the
models.

## Gate

`systemd-analyze verify` on every unit in the repo gate. A unit that cannot
be verified in CI is reviewed by reading the scripts it runs and declaring
its write targets — "argued statically" is acceptable, "assumed" is not.

## Common mistakes

| Mistake | Reality |
|---|---|
| "The service creates its RuntimeDirectory, so the path exists" | Only while that unit runs. Anything else reading it races its lifecycle. |
| "`ReadWritePaths` will allow the dir once the script mkdirs it" | Startup fails before the script runs. Pre-create on the host. |
| "The path unit will catch every trigger" | Coalesced while active, lost in the re-arm gap. Timer backstop required. |
| "Add the package to cloud-init and the box has it" | Only the next box. Live boxes need remediation, same commit as the gate update. |
| "`compose up -d` after an ipam change converges the stack" | It recreates the network but reattaches live containers WITHOUT their service aliases, so container-name DNS (`navidrome`) silently dies while static `extra_hosts` routes keep working. Follow any compose network change with `up -d --force-recreate`. (Born 2026-09-01: dubplate subnet pin 502'd Navidrome.) |
| "It's a helper/template unit, hardening is for the main services" | Helpers run with the same privileges. Harden every unit. |
| "An allow rule for `ssh host *` lets the session run that step unattended" | Auto mode ignores ssh allow rules, so the classifier still judges it. Wrap the step in a reviewed script with an exact rule. |
