# Workstation repo reorg for Bluefin DX

Pass header — token ceiling: 3M. Checkpoint interval: 4 tasks. Execution mode:
workflow (Geoff's opt-in this session); tasks run through the implementer →
diff-reviewer → gate chain via `~/.claude/workflows/pass-execute.js`,
**sequentially** — every task works the same live checkout of `~/.dotfiles`
plus live-system state, so no parallel executors (one-executor-per-worktree
rule; serial is also the cheaper path).

## Context

The Mint→Bluefin DX migration completed 2026-08-30. The dotfiles repo
(`~/.dotfiles`, github.com/glw907/workstation) still describes the Mint machine:
the root README documents Cinnamon/apt/nvm and a nonexistent `beautiful-aerc`
package, the aerc email stack and Nord/Cinnamon theming are dead, and `.bashrc`
carries a live nvm block beside its mise replacement. Exploration (three agents:
repo inventory, in-house guidance, live-drift audit) also found real bugs: the
Android udev rule staged in `bluefin/etc/` was never deployed (live `/etc` still
has the Mint `plugdev` rule), `contacts`' vdirsyncer.service points at
`/usr/bin/vdirsyncer` which doesn't exist on Bluefin (uv installs it to
`~/.local/bin`), and two competing vale install paths exist (Brewfile vs
`scripts/install-vale.sh` + a shadowing `~/.local/bin/vale` binary).

**Idiomatic-atomic verdict** (web research + `bluefin-admin.md` +
`bluefin/devenv-research.md`): the tiering is already idiomatic — signed image,
minimal change-controlled layered set (exact match live), Brewfile (no drift),
flatpak manifest concept, mise/uv runtimes, staged `/etc` drops, Stow (fine for
a single machine; chezmoi buys only multi-machine templating). The debt is repo
layout and stale content, not tooling. The one strategic gap — devcontainers
for SvelteKit/Cloudflare repos — is per-project future work, explicitly not
this pass.

Geoff's decisions (AskUserQuestion, this session): delete consumed migration
artifacts (keep MIGRATION-BRIEF.md as the standing decisions record);
flatpaks.txt scopes to deliberate installs only; retire `hx-journal`, `write`,
`journal`; delete all Mint remnants including wallpapers.

## Tasks

### T1 — Purge dead content
Delete: `bluefin/MIGRATION-RUNBOOK.md`, `bluefin/CLAUDE-md-draft.md`,
`bluefin/inventory/` (3 Mint dumps), `docs/email.md`, `docs/aerc-quickref.html`,
`docs/new-machine.md` (superseded by `bluefin/README.md` + bootstrap),
`themes/`, `wallpapers/`, `android/` (whole dir; its only value, SDK setup +
udev, moves to bluefin/README in T8),
`docs/superpowers/plans/2026-04-05-nvim-mail-upgrade.md` + its paired spec,
`bin/.local/bin/{hx-journal,write,journal}`, `scripts/install-vale.sh`.
Then `stow -R bin` so dead `~/.local/bin` symlinks drop.
Accept: files gone, `git status` shows only deletions, no broken symlinks in
`~/.local/bin` (`find ~/.local/bin -xtype l` empty).

### T2 — bash package cleanup
`bash/.bashrc`: remove the nvm block (NVM_DIR export + sourcing, ~lines
169–171), remove dead PATH segments `$HOME/go/bin` and `/usr/local/go/bin`
(both dirs absent; Go is brewed), remove the two "such as Mint" compatibility
comments (~lines 197, 201) and any other Mint references; keep the brew/mise
activation. Do NOT rewrite the whole file.
Accept: `bash -n` clean; a fresh login shell (`bash -lc`) resolves `brew`,
`mise`, `go version`, `node --version` (via mise activation); no
`nvm|NVM|Mint` matches left in the bash package.

### T3 — contacts fix + fastmail token path rename
- `contacts/.config/systemd/user/vdirsyncer.service`: `ExecStart=%h/.local/bin/vdirsyncer sync`
  (uv tool shim path), matching pattern in any other Exec lines. Verify the
  systemd user unit symlinks under `~/.config/systemd/user/` exist post-stow
  (unverified in audit), then `systemctl --user daemon-reload` and confirm
  `vdirsyncer.timer` loads.
- Rename the aerc-era token dir: move `~/.config/aerc/fastmail-*.age` →
  `~/.config/fastmail/`, update `bin/.local/bin/fastmail-password` and
  `fastmail-dav-password` to the new path, remove the empty aerc dir.
Accept: `systemctl --user status vdirsyncer.timer` loaded/active;
`fastmail-dav-password >/dev/null` exits 0; no `aerc` path references remain in
the repo outside MIGRATION-BRIEF.md.

### T4 — Manifests + single stow source of truth
- Regenerate `bluefin/flatpaks.txt`: deliberate installs only. Classify the 33
  live apps against Bluefin's stock set (check ublue-os/bluefin's shipped
  flatpak list; the `org.gnome.*` core apps and Bazaar are stock). Header
  comment states the scoping rule.
- Create `bluefin/stow-packages.txt` (one package per line) as the single
  source: `bash bin claude contacts git kitty mise vale`. Rework
  `bluefin/bootstrap.sh`'s `STOW_PACKAGES` and `sync-dotfiles.sh`'s check loop
  to read it (fixes sync-dotfiles' stale `bash bin claude git` list).
Accept: every flatpaks.txt entry is installed live; `bash -n` on both scripts;
`sync-dotfiles.sh` exits 0 mentioning all packages.

### T5 — Adoptions and vale dedupe
- New `mise` stow package: move live `~/.config/mise/config.toml` into
  `mise/.config/mise/config.toml`, stow it (adopt carefully: move file, stow,
  verify symlink).
- Adopt `~/.local/bin/planner` into `bin/.local/bin/` (move + `stow -R bin`);
  run `scripts/check-py-comments.sh` if it's Python.
- Vale: Brewfile is the single install path. Delete the untracked
  `~/.local/bin/vale` binary (it shadows brew's); confirm `command -v vale` →
  linuxbrew and `vale sync` works in `~/.config/vale`. Note the sync step in
  bootstrap.sh where install-vale.sh was referenced (if anywhere).
Accept: `mise ls` still shows node lts; `planner --help` (or equivalent smoke)
works via symlink; `command -v vale` is the brew path; `vale-hook` still
passes `tests/test_vale_hook.py`.

### T6 — Bluefin-native update tooling
Rewrite `bin/.local/bin/workstation-update`: drop the `--apt` branch and apt
comments; Bluefin flow is `ujust update` (system + flatpak + brew per
bluefin-admin.md) plus the non-ujust tiers it already covers (mise upgrade, uv
tool upgrade, kitty via update-kitty). Keep flags/structure consistent with the
script's existing style.
Accept: `bash -n`; `workstation-update --help` (or head-of-script usage) shows
no apt; dry-run-able paths verified where the script supports it.

### T7 — Live-system reconciliation
- Deploy the udev rule per the /etc rule in bluefin-admin.md: `sudo -A install
  -m 0644 bluefin/etc/udev/51-android.rules /etc/udev/rules.d/51-android.rules`
  then `sudo -A udevadm control --reload`. (adb device check stays on Geoff's
  manual tail — needs a plugged-in phone.)
- Delete `~/.dotfiles-preexisting/` (pre-stow conflict backups +
  mint-bin-strays; contents reviewed this session — nothing living; `planner`
  adopted in T5, `prose-guard` exists only as stale .pyc with no references).
- `kitty/.config/kitty/kitty.conf`: check `tab_title_template`'s hardcoded
  `/home/glw907` against Bluefin's `/var/home/glw907`; fix if it doesn't match
  live `$PWD` resolution.
Accept: `/etc/udev/rules.d/51-android.rules` matches the repo file (`diff -q`);
`~/.dotfiles-preexisting` gone; kitty config verified.

### T8 — Docs rewrite
- Root `README.md`: full Bluefin rewrite — what the repo is, actual layout
  (stow packages from stow-packages.txt, `bluefin/` machine config, `scripts/`,
  `secrets/`, `docs/`), pointer to `bluefin/README.md` for fresh-machine
  bring-up and `docs/secrets.md` for secrets. Note intentionally-untracked
  local tools (`poplar` via its repo's make install; standalone binaries
  harper-ls, marksman, perfspike, samfusdl, odin4).
- `bluefin/README.md`: drop runbook/draft references; add a short Android
  section (SDK via `update-android-sdk`, udev via `etc/udev/51-android.rules`,
  no plugdev on Bluefin).
- `claude/.claude/CLAUDE.md` Dotfiles Management section: update package list
  (adds mise, vale) and stow-packages.txt as the source; fix
  `sync-dotfiles.sh` description if behavior changed.
- `claude/.claude/docs/tui-testing.md`: remove the orphaned aerc-specific
  section.
- Create `docs/STATUS.md` (≤60 lines, present tense: repo purpose, package
  set, manifests, open items — devcontainer gap, kitty-harness retirement
  watch) and `docs/HISTORY.md` (first entry: this reorg pass — what landed and
  what a later pass shouldn't rediscover: the vale dual-path story, the
  vdirsyncer /usr/bin bug, the udev deploy).
Docs follow the Google developer-docs standard via the writing-voice router;
vale-hook must pass on every touched .md.

## Pass-end (conductor)

1. `code-simplifier` over the changed shell scripts (T4–T6); docs-only changes
   skip it.
2. Gate: `sync-dotfiles.sh` exits 0; `stow -R` every package in
   stow-packages.txt with no conflicts; `bash -n` all changed scripts;
   `tests/test_vale_hook.py` passes; `scripts/check-py-comments.sh` passes;
   `find ~/.local/bin -xtype l` empty; `git status` clean after commits.
3. Commits: imperative mood, specific files, Claude co-author footer; logical
   grouping (purge / fixes / manifests / tooling / docs) rather than one blob.
   Push to origin.
4. Update memory: `bluefin-migration-status.md` — reorg pass done,
   `.dotfiles-preexisting` cleared, remaining manual tail shrinks to the GUI
   items + adb device check.
5. Score both budgets (tokens vs 3M ceiling; interaction points) in the
   HISTORY.md entry.

## Verification (end-to-end)

Fresh login shell resolves brew/mise/node/go/vale correctly; `systemctl --user
status vdirsyncer.timer` healthy; `sudo -A udevadm` rule deployed and matching;
repo greps clean for `apt |nvm|aerc|cinnamon|Mint` outside MIGRATION-BRIEF.md
and HISTORY.md; sync-dotfiles.sh green; GitHub push green.

## Out of scope (recorded, not done here)

- Devcontainers for SvelteKit/Cloudflare repos (per-project, as repos mature).
- kitty/tui-visual-verify harness replacement (separate initiative per
  tui-testing-terminal-preference memory).
- Custom uBlue image for workstation #2 (explicit later decision point per
  MIGRATION-BRIEF.md).
