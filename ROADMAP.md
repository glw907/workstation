# Roadmap

Strategic initiatives for the workstation repo: work spanning passes, or
standing decisions other work is measured against. Managed by `/log-project`.
Current state lives in `docs/STATUS.md`; the per-pass ledger in
`docs/HISTORY.md`.

## Active

- **Monthly model, effort, and skill review** (Geoff, 2026-09-04): on the
  first of each month `model-review.timer` raises a reminder and a small
  pass runs the "Monthly review checklist" in
  `docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md`:
  model releases against the pins, prices and the plan-usage page, effort
  defaults and saved levels, the usage glance, the open skill experiments,
  and a fresh prompt audit when the target model changed. Standing inputs:
  `claude/.claude/docs/model-economy.md` and
  `docs/superpowers/plans/2026-09-04-prompt-audit-report.md`. Each review
  records its verdicts in `docs/HISTORY.md` and its tokens and interaction
  points per the pass scoring rule. First review due 2026-10-01.

- **cairn documentation standard** (Geoff, 2026-09-08): three plans against the standing spec
  `~/Projects/cairn-cms/docs/superpowers/specs/2026-09-08-docs-standard-design.md`. Plan one,
  the workstation's Claude infrastructure, is closed
  (`docs/superpowers/plans/2026-09-08-docs-standard-claude-infra.md`); its hand-off is
  `docs/superpowers/plans/2026-09-08-docs-standard-claude-infra-handoff.md`. Plan two (cairn's
  own toolset) and plan three (the docs rewrite) build against it next. `claude/.claude/CLAUDE.md`
  now carries the standard's four docs-standard lines (the 2026-09-12 Claude infra round);
  `cairn-cms/CLAUDE.md` still owes its own four-line pick and budget trim. The workstation's
  continuing obligation: the scanner, the voice files, the agents, and the skills this pass
  shipped stay in step with the standard as plan two and plan three exercise them.

## Planned

- **musicbox repo split**: the music-VPS spec, plan, and library design
  (`docs/superpowers/plans/2026-08-30-music-vps-build.md`,
  `docs/superpowers/specs/2026-08-30-music-vps-build-design.md`,
  `docs/superpowers/specs/2026-08-30-music-library-design.md`) describe a
  Hetzner server, another machine's config. They move to their own repo
  before server artifacts accrete; coordinate with the music session that
  owns them.

## Someday

- **Devcontainers** for the SvelteKit/Cloudflare site repos: logged per repo
  (907-life #2, ecxc-ski #39, xcathletes-org #4, the ASC STATUS chore), built
  as each repo matures. Research: `bluefin/devenv-research.md`.
- **kitty harness replacement**: kitty exists only as the `tui-visual-verify`
  capture platform (XWayland-forced). When a Wayland-native or
  terminal-agnostic capture method proves out, the harness moves and kitty
  leaves the machine entirely.
- **Custom uBlue image** for the second workstation: bakes the devmode rebase
  and Flatpak set into the image instead of undoing defaults per machine. An
  explicit later decision, not assumed.
- **bootstrap.sh restore split**: the restore phase is two-thirds of the file
  and a different risk class (destructive, run cold). Split into
  `bluefin/restore.sh` with shared helpers when workstation #2 lands.
