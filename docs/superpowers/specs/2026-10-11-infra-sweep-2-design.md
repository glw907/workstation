# Infra sweep 2: content, chaining, and alignment (design)

**Status:** awaiting Geoff's approval of the whole design, brought 2026-10-11 by the conducting
session (`c747c352`). E2 and E3 implement Geoff's choices of that day. F is his request of the same
day ("please add the monthly review"). Parent spec:
`docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md` "Lean re-plan (2026-10-11)".
Evidence: `docs/superpowers/research/2026-10-11-infra-sweep-survivor-ledger.md`. Sweep 2 runs
after the review desk (Geoff, 2026-10-11), so its approvals go through the desk.

## Outcome

Every surviving content finding is fixed and the ratchet baseline holds no entries. The pass
process drops three of Geoff's attended steps: the planning sitting when a design is approved ahead
of its pass, the launch and the pull, and the PR read on an `ordinary` pass. The workstation's
Claude Code setup checks itself against Anthropic's current guidance every month without anyone
starting the check.

## Tasks

All are `runner` class and land in dotfiles. Minutes are rough.

- **A. Go and TUI skills.** CS-1 to CS-5, CS-7, CS-11 to CS-13, and DC-10. Split `go-conventions`
  and `elm-conventions` under 500 lines, as a pair, with reference material one level down. Retire
  `claude/.claude/docs/bubbletea-conventions.md`, which clears its two `relative-link` entries.
  Trigger checks for `go-conventions`. About 240.
- **B. Cairn-facing skills and agents.** PS-02, PS-03, PS-05, PS-06, PS-17, PS-18, PS-19, PS-28's
  trims, AW-14, AW-15, and AW-22. Trigger checks for `visual-fidelity` and `cairn-release`. About 135.
- **C. Site and generic skills.** PS-08, PS-10, PS-20, PS-21, the PS-09 and PS-11 residuals, and
  `svelte-check`'s description and its frontmatter, which fails a strict YAML parse. About 75.
- **D. Docs and agents.** DC-07, DC-16, DC-22, DC-23 (generic anchors only), GA-04, GA-05, the
  DC-06 residual, the AW-21 measures, and `prose-voice-reviewer.md:3` ("the workstation tell
  catalogue"). `omitClaudeMd` on `cairn-docs-drafter`, `diff-reviewer`, `visual-verifier`, and
  `figure-verifier`. `claude-context-budget` joins dotfiles-pass's `runner` path map. About 105.
- **E. Chaining,** in `pass-core` and the three adapters. About 150.
  1. *Pre-approved designs.* A design Geoff approves ahead of its pass lets the planning session run
     spec, review, fold, verification, and the executor's launch unattended. It stops only for a
     finding that changes the approved design.
  2. *Conductor role.* The session that launches a pass keeps conducting. It watches with a new
     `pass-watch` tool (`bin/.local/bin/`, with fixture tests; `stow -R bin` at merge). After Geoff
     approves a dotfiles PR, it merges, pulls a clean `~/.dotfiles` with `git pull --ff-only`, and
     launches the next committed prompt.
  3. *Self-merge.* A pass whose highest class is `ordinary` merges its own PR after a green
     full-suite home and an accepted whole-branch review. `runner` and `auth-data` passes keep
     Geoff's read.

  The rule that PRs open in Geoff's browser landed in PR #4, and the review desk supersedes it.
- **F. A monthly alignment review that runs itself** (Geoff, 2026-10-11). `model-review.timer`
  fired on 2026-10-01, but it only raises a reminder, and no review followed. It now launches an
  unattended Opus session from a committed prompt. That session:
  - runs Anthropic's own prompt audit (`/doctor prompt-audit`) over `~/.claude`, where it can run
    unattended (the plan probes this);
  - compares the current Claude models and Claude Code version against those recorded at the last
    run. On a change it re-fetches the Anthropic pages the parent spec's "Anthropic practice"
    section cites, reads the release notes for a built-in that could retire a home-grown tool
    (the conductor's watcher and `scripts/gate.sh` included), and grades the workstation's rules
    against them, as the parent spec's Anthropic-practice lens did;
  - folds in the existing "Monthly review checklist"
    (`docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md`) and the ROADMAP's
    release-trigger line, so one review replaces both;
  - hands any gap to Geoff as a design through the review desk. A quiet month hands over nothing
    and adds one line to the review log.

  It records each run's model ids, Claude Code version, and page digests in a committed state file
  for the next comparison. It costs one Opus session a month. About 120.
- **G. `/effort` no longer dirties the repo.** `/effort` saves its default into
  `~/.claude/settings.json`, which is a stow link into `~/.dotfiles`. So each choice leaves an
  uncommitted change, which blocks the clean-checkout launch checks and the conductor's pull. It
  happened twice on 2026-10-11. Machine-local preference writes move out of the tracked file, by a
  method the plan takes from Claude Code's settings documentation and probes. About 45.

B, C, and D touch disjoint files, so they can run as pairs. F and G touch disjoint files too.

## Out of scope

Other repos: dubplate's (356 lines) and aksailingclub-org's (262) CLAUDE.md caps, and DC-23's ECXC
anchors, go to those repos' ROADMAPs. Atomic writes and the head-SHA race in `fetch_skill`, and the
checks deferred by ruling R2. Recording each rule's basis (an Anthropic page or a catch record) and
a quarterly prune by catch record are not in this pass; F's review surfaces them as it runs.

## End-to-end check

`bash scripts/gate.sh` prints `gate exit: 0`. `ratchet-baseline.json` has an empty `entries` list.
`go-conventions` and `elm-conventions` are each under 500 lines. Each trimmed description passes
its trigger prompts. `pass-watch` passes its fixture tests. A dry run of F's review on today's tree
completes unattended and hands over either a design or a quiet-month line. A `/effort` change
leaves `git -C ~/.dotfiles status --porcelain` empty.

## Risk and size

`runner`, with the `live-account` flag (push and PR). About 870 task-minutes, roughly a 7-hour path
with pairs.

## How it runs

After the review desk lands, the conductor launches an unattended planning session that merges
`main` into this branch and continues it: plan, three-lens review, fold, verification, then the
executor. Geoff's next touchpoint is sweep 2's PR, in the review desk.
