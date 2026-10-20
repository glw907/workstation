# Post-review fix pass (2026-08-30)

Source: the adversarial three-lens review run at the reorg pass close (findings
in the session record; the review's task list is this plan). Approval: Geoff,
"Start the work", plus "make sure our local claude infra is set up properly to
avoid this mistake in the future" (the mistake: plaintext secrets committed to
the public repo's history in Jan-Apr 2026; the leaked Cloudflare token verified
already-revoked 2026-08-30, the live token verified distinct by hash).

Batches, each gated and committed separately:

A. Security and prevention infra
- GitHub secret scanning + push protection: enabled (done, live).
- New `bin/.local/bin/claude-secret-guard`: PreToolUse deny hook scanning
  Write/Edit content and git-commit Bash commands for secret shapes (provider
  token prefixes, PEM/age private keys, JWTs, high-entropy env assignments);
  wired in claude/.claude/settings.json beside tierguard/block-op.
- gitleaks: add to Brewfile, install, run in the repo gate; pre-commit hook for
  this repo.
- claude-sudo-setup/claude-askpass: cache moves to /dev/shm, umask 077; kill
  the dead .age branch.
- gather-dotfiles.sh: redact export values.
- settings.json: replace the cairn-pub-scoped trust block with an accurate
  machine-level statement; move the cairn-pub specifics to that repo's own
  .claude/settings.json.
- secrets scripts: umask 077 both, mktemp for sync.sh decrypt target, --stdin
  for secret-set.sh (documented default), --verify regex gains 0-9.
- registry.md: routing table gains asc-site/xcathletes columns; leak
  post-mortem note under CLOUDFLARE_API_TOKEN; fix the two overclaims (:296
  ASC key carve-out, :68 fetch+shred parenthetical).
- .gitignore: *.sqlite, *places*, *bookmarks*, .pytest_cache/, .ruff_cache/.

B. Fresh-machine bootstrap repairs
- setup_mise_uv: uv set becomes khard vdirsyncer yt-dlp ruff jrnl
  "beets[fetchart,embedart]".
- setup: add `vale sync` step (styles are deliberately uncommitted); enable
  --now vdirsyncer.timer after stow; kitty installer gains launch=n and a
  ~/.local/bin/kitty+kitten symlink step.
- Quick card + checklist: "open a new terminal" between setup and restore;
  checklist stops routing unconditionally into restore (second-workstation
  path ends at setup).
- 1Password repo/key: stage repo file under bluefin/etc/yum.repos.d/, install
  via the staged-drop path, assert the GPG key fingerprint before tee.
- setup_brew fallback: eval shellenv by absolute path after install.

C. Tooling honesty
- sync-dotfiles.sh becomes bin/.local/bin/check-drift: real per-package stow
  probe (readlink through $HOME targets), no repo write, no `git add -A`
  advice; delete the unreachable gitconfig-copy branch. Root script removed.
- workstation-update: drop the false cron claim; README description matches
  the script (ujust update is separate and interactive).
- Delete update-go (brew owns Go; fold the poplar toolchain-pin note into
  workstation-update). Delete chromium-browser.md after folding still-true
  content into bluefin-admin.md. update-kitty curl gains -f. tierguard stops
  scanning past && / ; / |.
- bashrc: cld comment names only scripts that exist.

D. Organization and docs
- scripts/check.sh: the one gate entrypoint (ruff-D via check-py-comments,
  pytest tests/, bash -n over tracked scripts, vale fixtures, gitleaks);
  PYTHONDONTWRITEBYTECODE=1 inside. README/HISTORY point at it.
- bin/.stow-local-ignore for __pycache__; restow.
- vale/tests -> tests/vale; drop the ^/tests ignore line.
- MIGRATION-BRIEF.md -> docs/ after moving the layered-packages change-control
  rule into layered-packages.txt's header; devenv-research.md ->
  docs/superpowers/specs/; reference edits (bluefin/README, STATUS, HISTORY,
  CLAUDE.md, bluefin-admin.md).
- docs/secrets.md merges into secrets/registry.md (doctrine's absolute path
  wins); README links follow.
- docs/superpowers/plans/archive/ for the completed 2026-06-22 set and
  2026-04-05-era leftovers.
- ROADMAP.md at root: devcontainers, kitty-harness replacement, custom uBlue
  image, bootstrap restore split, history purge decision; STATUS open-items
  slims to a pointer.
- README: package list stops being restated (points at stow-packages.txt),
  garbled sentence fixed, ~/.claude stow/live-state warning line, gate pointer.
- STATUS/HISTORY: correct the reorg grep-criterion claim; record this pass.

Deferred / decisions batched for Geoff at close:
- git history purge (filter-repo + force push to main) for the token line,
  cli-mode.md copy, and browser-bookmarks blobs: force-push to main is
  forbidden by standing convention, so it happens only on Geoff's explicit
  call. Leaked credentials verified dead, so this is privacy hygiene, not
  incident response.
- Music-VPS spec eviction to ~/Projects/musicbox: the music session's active
  work; coordinate, do not race it.

Gate for every batch: scripts/check.sh once it exists (until then: bash -n
changed scripts, check-py-comments.sh, pytest tests/, sync/check-drift green).
