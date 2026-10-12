## Found (wave 1)
A1 bluefin/bootstrap.sh:365,383,499 and Brewfile:31 still say "kitty-shot harness" - defer
A2 docs/MIGRATION-BRIEF.md:96,100 historical kitty-shot mention - drop
A3 kitty-headless-shot header comments (~37,100) say "on-desktop harness" present tense - defer
A4 tui-visual-verify intro still says "the template", mixed wording - defer
A5 vendored golang-spf13-cobra contradictions untouched (by plan) - drop
I1 poplar ADR refs (ADR-0084 etc.) from deleted bubbletea-conventions.md not carried over; poplar refactor pass re-homes - defer
I2 hook bubbletea-conventions-lint.sh: grep finds no live file (only the deleted doc) - drop
I3 audit record and plan docs still mention bubbletea-conventions.md (historical) - drop
## Found (wave 2, C)
C1 plan acceptance 'grep ## Done log-project prints nothing' is stricter than scope: lines 110,144 are the already-fixed close procedure text, left in place - drop (reword acceptance)
C2 log-project:75 header template and log-issue Step 4 templates still say BACKLOG.md as defaults - drop
C3 worktree skill dirs leak into the skills list as duplicate scoped variants - defer
## Found (wave 2, B)
B1 cairn-figure and figure-verifier still copy the register's repro-fence caption and diagram 320/390 exemption text - defer
B2 engine-consult names check:close with a hand-listed set (check:comments, ...) that can go stale like PS-02 - defer
B3 register-check has no argument-hint (not verified allowed by claude-tooling-sync) - defer
## Found (wave 3, D)
D1 DC-23 ECXC anchors to file to ecxc-ski ROADMAP: audience-fit 5 ("speaks to both audiences at once, reading level fits a teen and a parent"), audience-fit 3 ("serves one audience well and the other thinly"), voice-fidelity 5 ("coach voice, warm and plain") - now (filing only)
D2 other "ASC" age-store mentions in cloudflare-estate-inventory.md may be stale, unaudited - defer
D3 secrets/registry.md (auth-data) has no id entry for the Cloudflare token; the record's id rests on the live verify (1d508f1a... verified active) - defer
D4 worktree Bash guard refuses `source` and brace expansion in git commands - drop
## Found (wave 3, F)  [dry run: exit 0, 25m03s wall, 5m28s CPU, 632 MB peak; not a quiet month; 18 pages fetched; 9 designs generated then deleted per acceptance]
F0 F added a failure notify-send beyond the task; removed at merge (scope). The mise-shims PATH addition stays (the dry run's gate needed node).
F1 review's nine design topics (guard-fail-closed, saved-effort, dispatch-effort, superpowers-pressure, agent-definitions, claude-md-style, convention-skills, vendored-overlays, process-skills) are real gaps beyond F - defer; re-run the review after merge. saved-effort overlaps G (reads effortLevel / Fable entry)
F2 guard-fail-closed: secret guard fails open although hooks can block on failure since 2.1.295 - defer
F3 three skills dispatch without an effort parameter - defer
F4 a `verify` skill (runs before each commit since 2.1.286) could carry the repo gate - defer
F5 `claude -w` makes its worktree under the main checkout's .claude/worktrees - drop
F6 dry-run's own gate run failed on node-not-found (mise shims); fixed in script, not re-exercised by a second dry run - note
## Found (wave 4)
E1 auto-mode classifier flagged E's report ("Instruction Poisoning") after denying its Python edit script; E's diff reviewed in full and clean - drop
G1 restore_place_home in bootstrap.sh (~l.679) re-stows claude but does not run apply, so ~/.claude/settings.json stays missing after a restore - defer
G2 first live stow -R claude after merge: order is stow, then apply (PR "What goes live") - now (PR note)
## Found (whole-branch review: accept, no blockers)
R1 claude/.stow-local-ignore README/LICENSE/COPYING were unanchored, widening stow's defaults; anchored at close - fixed
R2 G1 raised to now: restore_place_home re-stows claude without apply, so a restore leaves Claude Code without its guard hooks (secret, tierguard, block-op) until apply runs - now (one line in bootstrap.sh)
R3 each monthly `-w model-review-<YYYY-MM>` worktree keeps its lock under the main checkout and builds up month by month - defer (prompt.txt or the script should unlock and remove after the merge)
R4 the mise-shims PATH fix in model-review-notify is first exercised by the first live timer fire - note
R5 G and D commit bodies do not record the stow -n check; D has no body - drop
R6 stale "kitty-shot harness" wording at bootstrap.sh:365,383,504 and Brewfile:31 (A1) - defer
