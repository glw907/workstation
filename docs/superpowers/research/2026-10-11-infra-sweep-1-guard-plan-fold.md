# Infra sweep 1 plan review: fold record (2026-10-11)

Target: `docs/superpowers/plans/2026-10-11-infra-sweep-1-guard.md` and its prompt, reviewed at
`e223c7e` by the contract, mechanics, and risk lenses (`2026-10-11-infra-sweep-1-guard-review-*.md`
beside this file), folded on `217fe4e`. Each finding was checked against the code before it was
taken. Convergent findings fold once, at the root, and the other lens's rows point there. Probes
ran with `python3 -I` from `~/.claude/jobs/c747c352/tmp/`:

- `seeds.py`: the T1 and T3 seeds through `ratchet.parse`, `growth`, and `match`, plus the
  fork-skill phrases over every `SKILL.md`. Two `count: 2` relative-link entries parse, and four
  entries raise "duplicates an earlier entry". T1 and T3 show no growth. The fork skills are
  `content-review` (`ask "` 1) and `register-check` (`under discussion` 1, `delegated` 2, `during
  the session` 1).
- `ga03_rule.py`: the GA-03 rule on the live home. `~/.local/bin` is a real directory, and stowed
  bins resolve into `~/.dotfiles/bin/.local/bin`. `poplar` is a regular file and resolves through
  home. `scoped-test` is absent and stays GA-05. The only spans in the tree are `~/.local/bin/`,
  `poplar` (2), and `scoped-test` (1).
- `yaml_overlay.py`: a folded `description: >-` block of wrapped lines round-trips through PyYAML
  6.0.3 for text holding `: `, `#`, a leading quote, and YAML indicators. The plain-scalar form
  raises `ScannerError` on three of the four cases.
- `siblings.py`: the six sibling spans (`vale-setup` 11, 12, 67; `vale-fix` 20, 114; `vale-triage`
  36) all sit outside fences. No non-vale vendored skill carries one.
- `desclen.py`: description lengths in code points and bytes, `paths:`, and strict-YAML validity.
  `svelte-check` fails a strict YAML parse because a `: ` sits inside a plain scalar.
- Trigger mechanics: `claude -p --setting-sources project` run from a scratch directory loads that
  directory's `.claude/skills` and hides the personal skills (`daisyui` absent). With
  `--output-format stream-json --verbose`, a trigger shows as `"name":"Skill","input":{"skill":...}`.

## Settled, not forks

The planning session settled three items that the reviewers marked OWNER FORK. Each has one
clearly correct answer, so the plan takes it.

1. **The upstream refetch is dropped from T2** (contract M5, mechanics B1, M1, M2, M7-adjacent,
   risk B1, M2, M3). The mechanics lens probed every vendored path and found no upstream change
   since its pin. A refetch would revert the local `vale-ci` pin bump (`4cb4d62`). The global
   CLAUDE.md routes every dependency bump through `dependency-upgrade`. `update-skills` writes
   through `Paths(home)` into the live main checkout. T2 instead gains `apply-overlays --root
   TREE`, an offline application of the description, note, and sibling-rewrite overlays to the
   worktree's own copies, and `fetch_skill` calls the same function after any future fetch.
   Acceptance: `git -C ~/.dotfiles status --porcelain` prints nothing before and after T2, and
   PyYAML parses all eight vendored frontmatters. The overlay writes a folded block (probed).
2. **The line cap applies to the global CLAUDE.md only** (contract M4, mechanics M4, risk M1).
   The realpath must end in `/claude/.claude/CLAUDE.md`, which covers the tree copy, any
   worktree's copy, and `~/.claude/CLAUDE.md` through its stow link (probed), and the cap has its
   own line message. Dubplate (356 lines) and aksailingclub-org (262) are other repos and out of
   scope; they go to the PR body's "Found, not done". A fixture pins that a 250-line `CLAUDE.md`
   at any other path exits 0 in file and hook modes.
3. **Trigger checks apply to `daisyui` only** (contract M6, mechanics M7). Spec "Anthropic
   practice" item 7 limits them to a trimmed skill that a CLAUDE.md rule depends on. The global
   CLAUDE.md names "the official DaisyUI skill" as the reference, so `daisyui` qualifies, and no
   CLAUDE.md rule depends on `vhs-cli-demos`. T2's acceptance names the five prompts, the
   `claude -p` form (probed), the pass rule, and the place the results go: T2's commit body,
   copied by the session into the PR body.

## Dispositions

| Lens | Id | Disposition | Where folded, or why refused |
|---|---|---|---|
| contract | B1 | folded | T1 outcome (fingerprint is the target, anchor stripped; repeated hits add to the count), T1 acceptance (two entries, `count: 2`, line numbers named), T1 test (same target twice matches one `count: 2` entry). Probed with `seeds.py`. Root for mechanics M3 and risk M4. |
| contract | M1 | folded | T3 outcome (fifth phrase `ask "`, with the reason it is the defect class) and T3 acceptance (four exact entries with counts). The conditional sentence is deleted. Probed. Root for mechanics m1. |
| contract | M2 | folded | T1 outcome: the span is judged against the tree when the file is in the tree, or when the realpath of the home entry sits in a `bin/.local/bin` directory (a stow link, file-level or folded); otherwise against home. The `git ls-files` alternative is dropped. Fixtures: a stow symlink with no tree file is a violation, and `test_f2` stays green. Probed with `ga03_rule.py`. Root for mechanics m2 and risk M5. |
| contract | M3 | folded | End-to-end check rewritten in three observable parts: gate exit, ratchet exit 0, and a `python3 -I -c` print of the registry ids, the finding ids, and the vhs entries. Root for mechanics M6. |
| contract | M4 | folded (settled) | "Settled, not forks" item 2. |
| contract | M5 | folded (settled) | "Settled, not forks" item 1. |
| contract | M6 | folded (settled) | "Settled, not forks" item 3. |
| contract | M7 | folded | T2 outcome (folded-block write, probed), T2 lint (whitespace-collapsed comparison; the note compared stripped between markers), T2 acceptance (PyYAML parse of the eight vendored frontmatters), T2 test (an override holding `: `, `#`, and a leading quote). Root for mechanics m3 and risk m1. The T3-reader assertion is not taken, since T3 lands after T2; the PyYAML acceptance covers it. |
| contract | M8 | folded | Prompt: `subagent_type: "general-purpose"`, the task text plus the Conventions section verbatim, Clock and Stops reserved to the session, and the no-main-checkout-writes rule. Root for mechanics M5. |
| contract | m1 | folded | The vacuous 199-line acceptance is removed. The cap's proof is the fixtures in `tests/claude-context-budget.test.sh`, and the global-file run stays a gate leg. |
| contract | m2 | folded | T1 test: a live `exists.md#section` link and `/`-leading and `~`-leading links. |
| contract | m3 | folded | T2 outcome: rewrite outside fenced blocks only, and lint agrees. Tests: a fenced `` `fix` ``, plain-text "fix", and a skill from a repo with no renamed entry are left alone. Probe: every live span is outside a fence. |
| contract | m4 | folded | T3 outcome (shared scope, a missing description is not reported, an unterminated frontmatter exits 2) and T3 test (vendored over-cap reported, `skills/synced` excluded, a wrapped mixed-case phrase). |
| contract | m5 | folded | T3 outcome ("Unicode code points after whitespace collapse") and acceptance (`dependency-upgrade` 496 and `log-project` 486 not reported). |
| contract | m6 | folded | T1 outcome: `<!-- link-ok -->` at the line's end. |
| contract | m7 | folded | Close step 4 counts by check id (15 entries expected). The labels are kept as written, since migrating them buys nothing. |
| contract | m8 | folded | T1 Files and Test: `tests/claude-context-budget.test.sh` (new), run from `check.sh`. |
| contract | m9 | refused | Moot. No `update-skills` run happens, and T2 edits the manifest by hand ("not reflowed" in Files). |
| contract | m10 | folded | T1 acceptance: `poplar` is installed in home (probed), and the GA-05 entry stays. |
| mechanics | B1 | folded (settled) | "Settled, not forks" item 1 (`apply-overlays --root`, main checkout clean). |
| mechanics | M1 | folded (settled) | "Settled, not forks" item 1. With no refetch, the pin bump survives. T2 acceptance: the `vale-ci` `rev: v3.22.0` line is unchanged. |
| mechanics | M2 | folded (settled) | "Settled, not forks" item 1. The `gh api` failure clause and the GitHub read under `live-account` are deleted, and the T2 estimate is recomputed (120 with the trigger check). |
| mechanics | M3 | folded | At contract B1. |
| mechanics | M4 | folded (settled) | "Settled, not forks" item 2. |
| mechanics | M5 | folded | At contract M8. The lens's carve-out is taken: Clock and Stops stay with the session, and a subagent returns its failure uncommitted. |
| mechanics | M6 | folded | At contract M3. |
| mechanics | M7 | folded (settled) | "Settled, not forks" item 3. The T2 subagent runs the check. A nested `claude -p` from a subagent's Bash works (this fold agent ran the probes that way). |
| mechanics | m1 | folded | At contract M1. `ask "` is chosen over `ask "apply all`: both hit only `content-review:46` among the fork skills, and `ask "` names the defect class rather than one sentence. |
| mechanics | m2 | folded | At contract M2. The lens's `git ls-tree HEAD` rule is not taken: after the deleting commit, `HEAD` no longer tracks the bin, so the span falls through to home and passes. The realpath rule catches the deletion committed or not. |
| mechanics | m3 | folded | At contract M7. A folded block is chosen over a JSON-quoted scalar: both parse, and the folded form matches the vendored `vhs-cli-demos` form and reads cleanly. |
| mechanics | m4 | folded | T2 test is driven by subprocess through `apply-overlays --root <fixture>`, like the existing tests, so there is no module import and no bytecode concern. |
| mechanics | m5 | folded | Conventions "Tool protocol" (the forwarded flags, `ratchet.py:377-388`) and T3 outcome (flags accepted and unread, lazy import with `sys.dont_write_bytecode`). |
| mechanics | m6 | folded | Conventions "Commits": a missed seed amends the unpushed registering commit. |
| mechanics | m7 | refused | Moot, as contract m9. |
| mechanics | m8 | folded | Conventions "Clock" now matches pass-core: one session clock for the pair (`task=T1+T2`, `estimate=130`), none in pair worktrees, the overrun checked on return. The prompt repeats it. |
| mechanics | m9 | folded | Close step 3 says `verify` reads the main checkout and is a machine-state check. |
| mechanics | m10 | refused | The premise fails: at `cairn-docs-drafter.md:126` the link sits outside any code span (the line's only span is `` `CLAUDE.md` ``), so a code-span skip would not exempt it. The marker stays, in its named form (contract m6). |
| mechanics | m11 | folded | Prompt: the session records its name and id in STATUS and commits before the pair, which also gives the pair its base commit (pass-core "Pairs"). |
| mechanics | m12 | folded | T3 acceptance: one `GA-06` for the three skills, each entry with its own `pass` label. Conventions "Ratchet entries" allows this. `seeds.py` probed that `parse` accepts it. This deletes ceremony. |
| risk | B1 | folded (settled) | "Settled, not forks" item 1. The stow-link trap (a bare `claude-tooling-sync` runs main's copy) is folded as the Conventions rule "The main checkout stays untouched". |
| risk | M1 | folded (settled) | "Settled, not forks" item 2. The distinct line message is in the T1 outcome. |
| risk | M2 | folded (settled) | "Settled, not forks" item 1. Option (b)'s fix (resolve the head SHA once and read at it) is refused for this pass: `fetch_skill` does not run here, and the race has no observed failure. It is listed in the Close's "Found, not done". |
| risk | M3 | refused | Dropping the refetch removes the failure branch, and `apply-overlays` makes no network call. The temp-directory swap and atomic manifest write are new machinery for a path this pass never runs, with no measured defect. Listed in the Close's "Found, not done". |
| risk | M4 | folded | At contract B1. |
| risk | M5 | folded | At contract M2. |
| risk | m1 | folded | At contract M7. |
| risk | m2 | folded | T1 outcome: the module docstring names that an unstowed span resolves against the real home and that a red there means install or re-cite. |
| risk | m3 | folded | Plan "Launch": a branch check, both ahead and behind counts, a clean main checkout, a clean plan worktree, and the plan branch equal to its origin. |
| risk | m4 | folded | Close step 1 merges `origin/main` and then runs the gate. |
| risk | m5 | folded | Close step 5, "What goes live", names the three changes and the rollback. |
| risk | m6 | folded | T1 outcome: `check.sh` runs `bash bin/.local/bin/claude-context-budget`. Conventions: every tool runs from the worktree's own path. |
| risk | m7 | folded | Close step 5, "Found, not done" (out of this plan's scope). |
| risk | m8 | folded | Pass class line: `live-account` rests on the push and the PR, and no task reads upstream. |
| fold | F1 | folded | Found by the `desclen.py` probe. `svelte-check`'s description holds a `: ` in a plain scalar, so its frontmatter fails a strict YAML parse. Claude Code still lists the skill. T3's reader must be line-based and measure it (T3 outcome and test). The content fix goes to the Close's "Found, not done". |

Counts: 54 rows (contract 19, mechanics 20, risk 14, fold 1). 30 folded directly, 9 folded at a
root in another row, 11 folded as settled items, and 4 refused. Zero owner forks.

## Owner forks

None. Each OWNER FORK the lenses raised (contract M4, M5, M6; mechanics M1, M7; risk M1, M2) has
one correct answer, recorded under "Settled, not forks".

## Clock

T1 130 (from 120: the GA-03 symlink fixtures, the count fixture, and the line-cap test file), T2 120
(from 150: no refetch, plus about 20 for the trigger check), T3 100 (from 90: the scope and
malformed-state fixtures and the forwarded flags), and the close 70 (from 60: the `origin/main` merge
and the go-live paragraph). Total 420 task-minutes, with a pair path of about 300 minutes
(130 + 100 + 70).
