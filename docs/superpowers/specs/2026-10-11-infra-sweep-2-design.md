# Infra sweep 2: content and chaining (design)

**Status:** awaiting Geoff's approval of the whole design, brought 2026-10-11 by the conducting
session (`c747c352`). Item E4 is already Geoff's ruling (2026-10-11), and E2 and E3 implement his
choices of the same day. Parent spec: `docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`
"Lean re-plan (2026-10-11)". Evidence: `docs/superpowers/research/2026-10-11-infra-sweep-survivor-ledger.md`.
Both files arrive on `main` with infra sweep 1's merge.

## Outcome

Every surviving content finding is fixed and the ratchet baseline holds no entries. The pass
process drops three of Geoff's attended steps: the planning sitting when a design is approved ahead
of its pass, the launch and the pull, and the PR read on an `ordinary` pass.

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
     merges a dotfiles PR, it pulls a clean `~/.dotfiles` with `git pull --ff-only` and launches the
     next committed prompt.
  3. *Self-merge.* A pass whose highest class is `ordinary` merges its own PR after a green
     full-suite home and an accepted whole-branch review. `runner` and `auth-data` passes keep
     Geoff's read.
  4. *PRs open in Geoff's browser* (Geoff, 2026-10-11). When a PR is ready for Geoff's read, the
     session that hands it over opens it with `gh pr view <n> -R <repo> --web`, which opens the
     system default browser, Firefox. A self-merged pass sends a notification and opens no tab.

B, C, and D touch disjoint files, so they can run as pairs.

## Out of scope

Other repos: dubplate's (356 lines) and aksailingclub-org's (262) CLAUDE.md caps, and DC-23's ECXC
anchors, go to those repos' ROADMAPs. Atomic writes and the head-SHA race in `fetch_skill`, and the
checks deferred by ruling R2.

## End-to-end check

`bash scripts/gate.sh` prints `gate exit: 0`. `ratchet-baseline.json` has an empty `entries` list.
`go-conventions` and `elm-conventions` are each under 500 lines. Each trimmed description passes
its trigger prompts. `pass-watch` passes its fixture tests.

## Risk and size

`runner`, with the `live-account` flag (push and PR). About 705 task-minutes, roughly a 6-hour path
with pairs.

## How it runs

When infra sweep 1 merges, the conductor pulls `~/.dotfiles` and launches an unattended planning
session that continues this branch: plan, three-lens review, fold, verification, then the executor.
Geoff's next touchpoint is sweep 2's PR.
