# Workstation Configuration

Dotfiles and machine configuration for two Bluefin DX workstations
(`thinkpad-x1`, a ThinkPad X1 laptop, and `pavilion`, an HP desktop; Fedora 44
base, `bootc`/`ostree`), managed with
[GNU Stow](https://www.gnu.org/software/stow/). The repo tracks two things:
the dotfiles Stow links into `$HOME`, and the machine-provisioning artifacts
that bring a fresh Bluefin install to a working state.

## Layout

| Path | Contents |
|------|----------|
| `bluefin/` | Machine config: `Brewfile`, `flatpaks.txt`, `layered-packages.txt`, staged `/etc` drops, `bootstrap.sh`, `stow-packages.txt` |
| `scripts/` | Repo-maintenance scripts, including the secrets sync pipeline |
| `secrets/` | Age-encrypted secret store and rotation registry |
| `docs/` | Repo documentation, including this file's companions |
| `tests/` | Test suite for the repo's own scripts: pytest for vale-hook, bash fixtures for the vale styles |

The Stow packages are the top-level directories named in
`bluefin/stow-packages.txt`; every other top-level entry is repo
infrastructure. That file is the single source `bluefin/bootstrap.sh` and
`check-drift` read. One context-loaded doc (`docs/STATUS.md`) mirrors the
list for readers and must follow this file, not lead it.

One package needs a warning: `claude/` stows config into `~/.claude`, but that
directory also holds unstowed live state (sessions, credentials, history,
plugins). `~/.claude` is not disposable just because a stow package feeds it;
never remove the directory wholesale.

### Day-to-day Stow usage

    cd ~/.dotfiles
    stow bash              # Install (create symlinks)
    stow -D bash           # Remove (delete symlinks)
    stow -R bash           # Restow (after file changes)
    stow $(cat bluefin/stow-packages.txt | grep -v '^#')   # All packages

## Fresh-machine bring-up

See [bluefin/README.md](bluefin/README.md) for the full bootstrap sequence:
rebasing to the DX image, layering the minimal RPM set, running `setup`, and
restoring from the encrypted backup.

## Secrets

The age store is the source of truth, and Proton Pass holds its key. Secret values are
age-encrypted in
`secrets/values.age` and synced out to `~/.local/secrets` and Cloudflare
Workers by `scripts/secrets/sync.sh`. Architecture, inventory, and rotation:
[secrets/registry.md](secrets/registry.md).

## System maintenance

| Command | Purpose |
|---------|---------|
| `check-drift` | Reconcile the repo against the live machine: stow state, layered RPMs, Brewfile, flatpaks, uv tools, staged /etc drops, stray local binaries, git drift |
| `workstation-update` | Update the tiers `ujust update` does not cover: mise, uv tools, kitty, Android SDK. Run `ujust update` itself separately and interactively |
| `scripts/check.sh` | The repo gate: shell syntax, ruff docstring rules, the test suite, vale fixtures, gitleaks |
| `check-drift.timer` | Weekly systemd user timer (the `upkeep` package) running check-drift; desktop notification only when drift exists |
| `decision-review.timer` | Monthly systemd user timer (the `upkeep` package) running `decision-review-notify`, which only raises a notification to start the approval-packet decision review |
| `update-widevine` | Copy Google's Widevine module out of the Chrome stable RPM into Chromium's profile so DRM sites play; `widevine-update.timer` (the `upkeep` package) runs it weekly and skips the download when the RPM is unchanged |

## Repo status and history

Current state and open items: [docs/STATUS.md](docs/STATUS.md). Per-pass
ledger of what changed and why: [docs/HISTORY.md](docs/HISTORY.md).

## Intentionally untracked local tools

Some tools this workstation relies on are deliberately outside this repo,
because they own their own install or update path:

- **poplar** -- a terminal email client, installed from its own repo via
  `make install`, not Stow or Homebrew.
- **tellgrader** -- the tell-scanner CLI. Its source is tracked in this repo under the
  `claude` package, at `claude/.claude/skills/writing-voice/evals/tellgrader/`, and its own
  `make install` builds the binary to `~/.local/bin`, alongside poplar's entry.
- **Standalone binaries** -- `harper-ls`, `marksman`, `perfspike`,
  `samfusdl`, `odin4`. Each ships as a single binary with no package manager
  of its own; they live in `~/.local/bin` without a tracked source.
- **uv-tool shims** -- Python CLIs (`yt-dlp`, `ruff`,
  `jrnl`, `beets`) installed via `uv tool install` land in `~/.local/bin` as shims.
  `bluefin/bootstrap.sh` installs the set; nothing in this repo tracks the
  shims themselves.
