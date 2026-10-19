# Prompt audit, 2026-10-19

## Assumptions

- **Scope.** All Claude Code configuration that loads in `~/.dotfiles` sessions: `claude/.claude/CLAUDE.md`, every skill, agent, and output style under `claude/.claude/` (stowed to `~/.claude`, so each edit affects all projects), and the project skill `.claude/skills/dotfiles-pass`. The installed plugins were audited report-only. Settings files, `.mcp.json`, and `~/.claude.json` were not read.
- **Target model.** `claude-opus-5-5`, the model running the audit. The two implementer agents pin Sonnet and were audited against `claude-sonnet-5-5`.
- **Vendored skills.** `daisyui`, `golang-spf13-cobra`, `vhs-cli-demos`, and the `vale-*` skills come from upstream (`claude/.claude/tooling/vendored-skills.json`). Fixes for them go through the manifest overlays, never the body.
- **Request-building code.** There is none, so Group 4 is not applicable.

## Summary

Three findings have the most impact.

The superpowers plugin's SessionStart hook loads `using-superpowers` into every session. It tells the model "you ABSOLUTELY MUST invoke" a skill at a 1% chance and sends every plan through `brainstorming` and `writing-plans`. Those skills ask Geoff the execution method, offer a local merge menu, and tell the model to delete code written before its test. Each one conflicts with `pass-core`, "Direct changes", or the destructive-ops rule. This is a plugin decision, not an edit.

Several instruction files rule differently on the same point. `CLAUDE.md` names `scripts/check.sh` as the gate, and `dotfiles-pass` names `scripts/gate.sh`. `cairn-release` pushes a feature branch straight to `main`, which skips the packet approval `pass-core` requires. `log-issue` runs an ungated `git push` on whatever branch is checked out, and `pass-core` sends every pass follow-up through it.

Some instructions are stale against the repo. `prose-voice-reviewer` says "flag two things only" over a list of four. `engine-triage` claims "model diversity" with the same model the planner runs. `design-refinement`'s AI-default list claims to be "kept in sync" with a frontend-design list that has since gained a fifth cluster.

| Group | Proposed edits | Flags |
|---|---|---|
| 1, dated prompt text | 6 | 4 |
| 2, brittle configuration files | 23 | 20 |
| 3, tool descriptions | not applicable | — |
| 4, request config | not applicable | — |
| Plugins (report only) | — | 15 |

## Proposed edits

All are proposed. All 30 hunks merged as glw907/workstation#104. Every path is under `claude/.claude/` and affects all projects.

### High confidence

| Location | Pattern | Why | Action |
|---|---|---|---|
| `agents/engine-triage.md:13-14` | 2, stale fact | "model diversity": the agent and its dispatcher both run `claude-opus-5-5` since d09b9ea | rewrite: drop "and model diversity" |
| `agents/prose-voice-reviewer.md:46` | 1d patch accretion | "flag two things only" over four bullets; Opus 5.5 reads the count literally | rewrite: "flag these:" |
| `skills/bubbletea-design/SKILL.md:201-210, 257` | 2, conflict | Mode 2 judges "spacing, density, feel" from a text grid; the newer 7d5bdd0 lines and `tui-visual-verify` say a text capture never shows paint | rewrite Mode 2 to cell counting |
| `skills/go-conventions/references/modern-stdlib.md:93` | 2, stale fact | "`/simplify` Agent 3" exists only in poplar's project skill; `go-ship` says the bundled `/simplify` resolves elsewhere | rewrite to name poplar's skill |
| `skills/design-refinement/SKILL.md:280-285` | 2 stale fact; 1e named defaults | "kept in sync" with frontend-design, which now has five clusters; the list also lacks the Opus 5.5 defaults the guide names | rewrite with the five clusters plus the named defaults |

### Medium confidence

| Location | Pattern | Action |
|---|---|---|
| `CLAUDE.md:71-72` | 2, conflict with `dotfiles-pass` (newer) | gate is `bash scripts/gate.sh` |
| `CLAUDE.md:5-7` | 2, conflict with `pass-core` "Judgment calls" and the destructive-ops line | add the `pass-core` stops to "Stop only for" |
| `CLAUDE.md:12-13` | 2, conflict with `pass-core` step 4 (today) | touchpoints include the pre-flight sitting |
| `CLAUDE.md:94` | 1a | "FULL ACCOUNT ACCESS" at normal volume |
| `skills/cairn-release/SKILL.md:36-39` | 2, conflict with `pass-core` "Close" | confirm each pass merged by PR; never push a pass branch to `main` |
| `skills/cairn-release/SKILL.md:108-141` | 1a | lowercase FULL, NEW SUBSYSTEM, HERE, PUBLISHED, EACH, EVERY |
| `skills/cairn-release/SKILL.md:170-181` | 1d migration-relative | drop the "before that" and "old override was removed" clauses |
| `skills/log-issue/SKILL.md:175-181` | 2, conflict with "Direct changes" and one-executor | commit the backlog file alone; push only as a direct change |
| `agents/diff-reviewer.md:20-25` | 2, wrong degrees of freedom (add) | it has no Skill tool: read each checklist from its file |
| `agents/cairn-register-editor.md:41` | 1d migration-relative | "No July plan" becomes "Load no voice corpus" |
| `agents/cairn-register-editor.md:17, 80-81, 140` | 1a; also uses the contrast frame it bans | plain statement, lowercase |
| `output-styles/writing-voice.md:59-64` | 2, cairn-only rule in an always-on file | "A repo's register may narrow this (cairn's does)." |
| `skills/content-draft/SKILL.md:9-10` | 2, stale ("the technical voice" resolves nowhere) | point at the `writing-voice` skill |
| `skills/cairn-figure/SKILL.md:72-74` | 2, dangling "diagram bullet above" | point below |
| `skills/vale-setup` overlay in `vendored-skills.json` | 2, conflict: overlay says commit styles, body says gitignore them | overlay names the override |
| `skills/vale-fix` overlay in `vendored-skills.json` | 2, description still says "a pull request per file" | add a `description` overlay |
| `skills/go-conventions/SKILL.md:43-44` | 1a trait claim ("Claude's default Go output drifts") | "Reject these forms, which carry habits from other languages into Go:" |
| `skills/go-conventions/SKILL.md:146-148` | 2, internal ambiguity on stdout and stderr | name which form is cobra's and which is the house rule |
| `skills/bubbletea-design/SKILL.md:260-262` | 2 history narrative | remove the tab-bar story |
| `skills/tui-visual-verify/SKILL.md:8-15` | 2 history narrative | keep the reason, drop the counts |
| `skills/visual-fidelity/SKILL.md:14-15` | 2 pinned model name ("Fable 5 prompting guide") | "Anthropic's prompting guidance" |
| `skills/visual-fidelity/SKILL.md:21-39` | 1a, 1c | step 1 rewritten at normal volume, in two paragraphs |

## Flags (no edit proposed)

Each of these needs a ruling from Geoff, loosens a prohibition, or is low confidence.

- **Contrast floors.** `visual-verifier.md:29-31` flags a CTA pair under 3:1, and `daisyui-a11y-reviewer.md:72` flags text under 4.5:1. Button labels are normal text, so WCAG's floor is 4.5:1. Aligning the verifier tightens it; the guide flags because the newer line is the looser one.
- **The em dash in docs.** `prose-voice-reviewer.md:50-51` flags any em dash in a docs file, while the output style and `writing-voice` allow Google's unspaced form. The fix loosens a prohibition.
- **`site-implementer.md:14-15` against `:74-77`.** The agent may never push, yet it must merge a cairn-cms docs branch by PR. Who pushes?
- **Engine passes and releases.** `cairn-pass:89` says engine passes "never release", and `engine-consult:123-125` invokes `cairn-release` after the engine merge.
- **`approval-packet:33-39`.** "At most three asks" can't hold when four PRs carry forced asks.
- **The gate form under the worktree guard.** `pass-core:221-222`, `cairn-pass`, and `site-pass` say `cairn-run-gate '<string>'`, which `dotfiles-pass` says the guard refuses. Whether the guard applies in cairn and site worktrees is not settled by the repo.
- **`spec-plan-review:55`.** Review records go to `docs/superpowers/research/`, and `pass-core:31` sends cross-repo research to `initiatives/<id>/`.
- **`plan-reviewer.md:33-54`.** The checklist states the stop rule twice and grows one incident item per miss. A consolidated three-item form is in reader A's notes; it was held back because it rewrites lessons landed today.
- **Incident narratives** past the house "(Geoff, date)" tag, in `pass-core` (eleven places), `plan-reviewer`, `cairn-release`, `visual-fidelity`, `design-refinement`, `visual-verifier`, `cairn-docs-drafter`, `cairn-register-editor`, and `cairn-figure`. The guide's history-narratives row is in tension with the house convention. The strongest cut is `pass-core:188-189`, a rolling statistic.
- **Opus 5 citations** in `pass-core`, `claude-infra`, and `spec-plan-review`. The Opus 5.5 migration notes name Opus 5's scope and verification prompts as re-test candidates.
- **Low confidence.** `CLAUDE.md:88` "MANDATORY" (a routing line, keep-list item 6). `daisyui-a11y-reviewer` migration lists. `svelte-reviewer` says SvelteKit 2 while cairn-cms is on Kit 3. The implementers' "ask any clarifying question" (no channel back). `elm-conventions:34` "now". `svelte-check:100`. `cairn-figure:55-58` and `:88-94`. The `cairn-docs-drafter` track list. `cairn-figure` and `figure-verifier` on alt text "about" against "capped at" 150 characters. `dotfiles-pass` gate timings from before the drafter leg. `plan-reviewer:14-18` justification paragraph. Output style `:16-17` path and `:67-68` metadata. Two dispatches with no effort (`content-draft`, `register-check`). The vendored `daisyui` body says "each time you write HTML or JSX", against its narrowed description.
- **Dropped.** Reader A proposed renaming `/doctor prompt-audit` in `claude-infra` to `/claude-api prompt-audit`. `/doctor prompt-audit` is how this audit ran and what `model-review-notify` calls, so the line is correct.

## Plugins (report only)

The superpowers findings closed with glw907/workstation#105: the plugin is disabled, and `brainstorming` and `receiving-code-review` are vendored.

- **superpowers 7.0.0.** `using-superpowers` loads into every session through the SessionStart hook, at a pressure register ("1% chance", "YOU DO NOT HAVE A CHOICE"). `writing-plans` asks Geoff to choose the execution method. `brainstorming` allows "no other skill" after it. `finishing-a-development-branch` presents a merge menu and waits. `test-driven-development` says "Delete means delete". `using-git-worktrees` commits a `.gitignore` change. `subagent-driven-development` caps narration at one line. `writing-skills` says to stop and push to a fork. Each conflicts with `pass-core`, "Direct changes", `approval-packet`, or the destructive-ops rule. The workstation already overrides several of these ("Skip `writing-plans`' code steps and execution-method question"), but the session-start injection still loads in every session.
- **code-simplifier.** It cites another project's CLAUDE.md standards (ES modules, React) and runs "proactively ... without requiring explicit requests".
- **cloudflare 1.0.2.** `cf-cli` puts secrets in with `wrangler secret put` alone, and `nextjs-on-cloudflare` installs third-party skills with `npx skills add`. The `basin` and `k2` skills hinge on open PRs.
- **skill-creator.** "we are trying to create billions a year in economic value here! ... take your time and really mull things over" steers thinking depth by prose. It also conflicts with `writing-skills` on how to write a description.
- **code-review.** It pins Haiku and Sonnet by name, uses a 0-100 score with a cutoff of 80, and shares its name with the built-in `/code-review`.
- **frontend-design.** It says "take aesthetic risk", which conflicts with DaisyUI-first in cairn admins (low). Its named-defaults list is the 1e exception and stays.

## Cadence

Anthropic's guide says to re-audit at every model release, and the best-practices page says to review CLAUDE.md "when things go wrong, prune it regularly". This audit already runs monthly. `model-review.timer` fires `model-review-notify` on the 1st, which runs `/doctor prompt-audit` headless and passes the report to the review session. The next run is 2026-11-01.

## Open flags

The flags above wait for Geoff's ruling. The next monthly review starts from this list and drops each one that has been ruled on.
