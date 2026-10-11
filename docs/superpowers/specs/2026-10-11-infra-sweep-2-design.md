# Infra sweep 2: content, chaining, and alignment (design)

**Status:** re-checked against main at `5d35c35`, 2026-10-11, awaiting Geoff. First brought that day
by the conducting session (`c747c352`). E implements Geoff's choices of that day, F is his request
("please add the monthly review"), and H is his "now" ruling on dubplate PR #2's found-not-done
list. Parent spec: `docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md` "Lean re-plan
(2026-10-11)". Evidence: `docs/superpowers/research/2026-10-11-infra-sweep-survivor-ledger.md`.

**Already landed, so dropped here.** PR #8 (`01a562b`) landed the review depth by design size and
the scope rules (`spec-plan-review/SKILL.md:36-42`, `pass-core/SKILL.md:26-47,187-191`), including
E1's rule that only a design-changing finding stops for Geoff (`pass-core/SKILL.md:51-53`). PR #7
(`ea7aeb3`) landed the pull after a merge (`pass-core/SKILL.md:155-160`). PR #9 (`42ef0f4`) put the
conductor role in a launch prompt (`docs/superpowers/plans/2026-10-11-conductor-prompt.txt`), and
PR #10 (`81af5cc`) lets a hand-over merge itself (`pass-core/SKILL.md:180-185`).

## Outcome

Every surviving content finding is fixed and the ratchet baseline holds no entries. The conductor
role and pre-approved planning live in `pass-core` instead of a launch prompt, and an `ordinary`
pass merges its own PR. The workstation checks itself against Anthropic's guidance every month
without anyone starting the check. Three dubplate process facts reach the skills that execute them.

## Tasks

All are `runner` class and land in dotfiles. Minutes are rough.

- **A. Go and TUI skills.** CS-1 to CS-5, CS-7, CS-11 to CS-13, and DC-10. Split `go-conventions`
  (592 lines) and `elm-conventions` (582) under 500, as a pair, with reference material one level
  down. Retire `claude/.claude/docs/bubbletea-conventions.md`, which clears its two `relative-link`
  entries. Trigger checks for `go-conventions`. About 240.
- **B. Cairn-facing skills and agents.** PS-02, PS-03, PS-05, PS-06, PS-17, PS-18, PS-19, PS-28's
  trims, AW-14, AW-15, and AW-22. Trigger checks for `visual-fidelity` and `cairn-release`. About 135.
- **C. Site and generic skills.** PS-08, PS-10, PS-20, PS-21, the PS-09 and PS-11 residuals, and
  `svelte-check`'s description, whose unquoted `Scope:` fails a strict YAML parse. About 75.
- **D. Docs and agents.** DC-07, DC-16, DC-22, DC-23 (generic anchors only), GA-04, GA-05, the
  DC-06 residual, the AW-21 measures, and `prose-voice-reviewer.md:3` ("the workstation tell
  catalogue"). `omitClaudeMd` on `cairn-docs-drafter`, `diff-reviewer`, `visual-verifier`, and
  `figure-verifier`. `claude-context-budget` joins dotfiles-pass's `runner` path map. About 105.
- **E. Chaining, in `pass-core`.** About 60.
  1. *Pre-approved designs.* A design Geoff approves ahead of its pass lets the planning session
     run plan, review, fold, and the executor's launch unattended.
  2. *Conductor role.* The conductor prompt's role moves into a `pass-core` section: watch with the
     Monitor tool over `claude agents --json`, merge after Geoff approves, pull, and launch the next
     committed prompt. The `pass-watch` script is dropped, since a built-in already watches
     (`claude-infra` step 1).
  3. *Self-merge.* A pass whose highest class is `ordinary` merges its own PR after a green
     full-suite home and an accepted whole-branch review, when its "Found, not done" list is
     empty. A non-empty list, or a `runner` or `auth-data` pass, keeps Geoff's read.
- **F. A monthly alignment review that runs itself.** `model-review.timer` only raises a reminder
  (`bin/.local/bin/model-review-notify`). It now launches an unattended Opus session from a
  committed prompt that runs `/doctor prompt-audit` over `~/.claude` (the plan probes that it runs
  unattended). On a change in models or Claude Code version since the last run, it re-fetches the
  pages the parent spec's "Anthropic practice" section cites and the release notes, and grades the
  workstation's rules against them. It folds in the "Monthly review checklist"
  (`docs/superpowers/specs/2026-09-04-fable-5-1-infra-update-design.md`) and the ROADMAP's
  release-trigger line. A gap goes to Geoff as a design. A quiet month adds one line to a review
  log. A committed state file holds each run's model ids, version, and page digests. About 120.
- **G. `/effort` no longer dirties the repo.** `~/.claude/settings.json` is still a stow link into
  `~/.dotfiles`, so each `/effort` choice leaves an uncommitted change that blocks the clean-checkout
  launch checks. Machine-local preference writes move out of the tracked file, by a method the plan
  takes from Claude Code's settings documentation and probes. About 45.
- **H. Three dubplate facts land where they execute** (Geoff, 2026-10-11, "now"). None is in the
  tree today. (a) `go-ship` step 2 "Simplify", which dispatches `code-simplifier`: the dispatch
  says "no sub-agents, work serially, one gate, one commit". (b) `pass-core` "Ledgers": cite a
  commit id that survives a merge, a merge commit or an id on the default branch, since a squash or
  rebase rewrites ids. (c) the `prose-voice-reviewer` agent: on a spec, review prose once per
  revision, facts and contradictions first. About 30.

B, C, and D touch disjoint files, so they can run as pairs. F and G touch disjoint files too. H's
`pass-core` line rides with E.

## Out of scope

Other repos: DC-23's ECXC anchors go to ecxc-ski's ROADMAP. Atomic writes and the head-SHA race in
`fetch_skill`, and the checks deferred by ruling R2. A per-rule basis record and a quarterly prune;
F's review surfaces them as it runs.

## End-to-end check

`bash scripts/gate.sh` prints `gate exit: 0`. `ratchet-baseline.json` has an empty `entries` list.
`go-conventions` and `elm-conventions` are each under 500 lines. Each trimmed description passes
its trigger prompts. A dry run of F's review on today's tree completes unattended and hands over
either a design or a quiet-month line. A `/effort` change leaves
`git -C ~/.dotfiles status --porcelain` empty. `grep` finds each of H's three facts in its target.

## Risk and size

`runner`, from the path map. The `live-account` flag is dropped: a branch push and a PR are every
dotfiles pass's normal path, so review depth is the plan's mechanics lens and the fold. About 810
task-minutes, roughly a 6-hour path with pairs.

## How it runs

After the review desk lands, sweep 2's approval goes through the desk. The conductor then launches
an unattended planning session that merges `main` into this branch and continues it: plan,
`plan-reviewer`, fold, then the executor. Geoff's next touchpoint is sweep 2's PR.
