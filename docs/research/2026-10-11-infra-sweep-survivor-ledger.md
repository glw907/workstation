# Infra sweep survivor ledger (2026-10-11)

Re-derivation of the 2026-09-28 infra sweep against the tree after the lean pass cutover. Inputs:
the sweep spec (`docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md`), the audit
(`claude/.claude/docs/record/2026-09-28-claude-infra-audit.md`), and dotfiles `main` at `4231a67`.
Rule from STATUS (2026-10-10): an item is superseded when the cutover rewrote or deleted the file
it targets. Evidence came from `git diff --stat 998859b^1 998859b` (step 1), `998859b..4231a67`
(PRs #2 and #3), the style-guide-sync merges, and reads of each target. An Opus agent built the
ledger, and the planning session spot-checked the load-bearing rows.

## Already landed before the cutover

A-core merged at `c3e709c` and B at `7de1210`. Style-guide-sync merged into dotfiles at `fc53c6e`,
`53c5b09`, `d97d9d0`, and `32a30a7`. Its cairn-cms side merged at `c84a7d40`, and its eight owned
audit ids (PS-07, DC-25, AW-08, AW-09, AW-10, DC-27, DC-28, AW-24) verify fixed. The STATUS line
"chain W's content survives as a lean task list" was wrong. The ratchet baseline held 6 entries
at `4231a67`: PS-05 (C), CS-4 (D), GA-03 x2 (A-rest), GA-04 and GA-05 (C).

## Superseded or done

| Item | Verdict | Evidence |
|---|---|---|
| B1 runners, AW-11 | superseded | `pass-execute*.js` deleted in `998859b` |
| B2 AW-17, AW-20 | superseded | `cairn-run-gate` rewritten (S1-T3) |
| B3 AW-19, AW-23, AW-18 | superseded | implementers and `diff-reviewer` rewritten (S1-T8) |
| B4 DC-01, DC-03, DC-04, DC-29, DC-30, DC-08, DC-19, DC-21, Git trim, 200-line test | superseded | global `CLAUDE.md` rewritten at `bb41823`, 199 lines |
| PS-12, PS-14, PS-15, PS-22, PS-25 (workstation side) | superseded | `pass-core`, `cairn-pass`, `spec-plan-review` rewritten |
| Seat check and `seats.json`, `pass-core` close wiring | superseded | S1-T10 and `998859b` |
| AW-07 | done | deleted in B4 |
| PS-04 | done | `e9aebc2` points `engine-consult` at `check:close` |
| DC-09 (inventory side) | done | `3a58ba6` (PR #3) |
| PS-11, DC-06, PS-09 | superseded, with residuals | `log-project:98-104` example still shows `## Done`; `fable-post-cutoff-system.md:45`; `site-pass:15,64` hardcode `docs/superpowers/` |
| GA-01, GA-02 | done | `cc118a5`, `4461c1f` |
| F rows for cairn-cms and the sites | superseded | cairn-cms #112; step-3 PRs merged |
| DC-14 quoted-version check | dropped | its only instance was fixed by S3-T3 |
| DC-17 orphan disposition | stale | the sites cite `instructions/ai-operational-rules.md` as general rules; the file stays |

## Survives

| Item | Target now | Evidence |
|---|---|---|
| GA-03 | `scripts/check-claude-refs.py:159-160` | rewrites every `~/.local/bin/<x>` under the tree; `~/.local/bin/poplar` is a real, unstowed binary |
| Relative-link check (DC-10) | same script | not built; live hits at `docs/bubbletea-conventions.md:11,13` (four links) |
| Context budget line cap | `bin/.local/bin/claude-context-budget:18-22` | bytes/4 budgets only, no line cap |
| CS-6, CS-8, CS-10, CS-17 | `bin/.local/bin/claude-tooling-sync`, `tooling/vendored-skills.json` | `MANIFEST_FIELDS` (`:36`) has no description field; `fetch_skill` rewrites only `name:` (`:214-219`) |
| Description cap, fork lint (PS-28, PS-06, PS-20) | same tool | not built |
| PS-02, PS-03, PS-05, PS-06, PS-17, PS-18, PS-19, PS-28, AW-14, AW-15, AW-22 | cairn-facing skills and agents | each quoted at its line in the agent ledger; unchanged since 2026-09-28 |
| PS-08, PS-10, PS-20, PS-21 | site and generic skills | unchanged |
| DC-07, DC-16, DC-22, DC-23, GA-04, GA-05 | workstation docs | `cloudflare-estate-inventory.md:11-13` still names the deleted token id as live |
| AW-21 (measures half) | `cairn-register-editor.md:65-81` and `prose-voice-reviewer.md:24-44` | neither agent touched by the cutover |
| CS-1 to CS-5, CS-7, CS-11 to CS-13, DC-10, size caps | Go and TUI skills | `go-conventions` 592 lines, `elm-conventions` 582; no `SilenceErrors` |
| `omitClaudeMd` | `agents/*.md` | no agent sets it |
| Poplar DC-11, DC-12 | `poplar/CLAUDE.md:57-63`, `:89` | defers to the deleted global "Conducting a pass" rule; cites missing `glw907-vendor.sh` |

## Probes run by the planning session (2026-10-11)

A scratch prototype of three candidate checks ran over `claude/.claude` at `710abf9`:

- Relative links: five unresolved. Four are DC-10's `research/` links. One is
  `agents/cairn-docs-drafter.md:126`, a sample link quoted inside example docs prose (a false
  positive that needs an exemption marker).
- Heading citations: eight found, four resolve, two do not resolve to one file, and two fail.
  Both failures are false positives: a heading wrapped across a line break
  (`claude-md-archive.md:53-54`), and a citation of cairn-cms's own `CLAUDE.md` from
  `cairn-release`. Self mode has no true catch. The audit's targets (DC-13, DC-15, DC-18) live in
  repo CLAUDE.md files, which is cross-repo mode.
- Orphan docs: one hit, `instructions/ai-operational-rules.md`, which the sites cite.

Skill descriptions over 500 characters with no `paths:` gate: `cairn-release` 849,
`vhs-cli-demos` 917, `visual-fidelity` 672, `svelte-check` 599, `tui-visual-verify` 534,
`go-conventions` 530. `svelte-check` is new (no audit id). Fork skills: `content-review` and
`register-check`.
