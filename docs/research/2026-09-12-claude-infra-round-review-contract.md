# Adversarial plan review: CONTRACT AND CRITERIA lens

Plan: `docs/superpowers/plans/2026-09-12-claude-infra-round.md`, revision 1.
Reviewed 2026-09-12 against `~/.dotfiles` at `9034fd3`, the commit the plan names.
Lens: outcomes, constraints, and falsifiable acceptance criteria; Files completeness;
deliverable counts; the close task's draft-versus-fold contract; citation accuracy.
Read-only review. Nothing was edited.

Conductor-ruled items were not re-litigated: the site-repo deletions in task 3, the fifth
displacement pick, the hoisted model pin, the dropped RESEND example, the commit footer.

**Counts: 3 BLOCKER, 6 MAJOR, 7 MINOR.**

## What verified clean

Worth recording, because most of the plan's citations hold.

- Tree state: `9034fd3`, one warm line `claude/.claude/agents/cairn-implementer.md`.
- `scripts/check.sh:37-42` is exactly the six legs the pre-flight names, with no shellcheck
  leg and the vale leg running fixtures. Correction 2 is right.
- All five `~/.claude` directories are folded whole-directory symlinks. Correction 1 is right.
- `claude-context-budget:18,22`; `cairn-run-gate:1-14`; `site-implementer.md:89`;
  `pass-execute.js:16-19, 47-62, 85-88, 136, 144-146, 157-159, 30-39, 1-28, 270-272`;
  `pass-execute-chains.js:75,104`; `model-economy.md:165-173` with its em dash at `:168`;
  the 2026-09-08 exemplar at `:112-118`; HISTORY's 0.6M-over-seven derivation. All accurate.
- Byte counts: `CLAUDE.md` 27,807; `go-architecture-reader.md` 5,260; both `svelte-check`
  copies 1,748 and byte-identical; `cairn-cms/CLAUDE.md` 24,873; pick 1 456; pick 2 2,143;
  pick 5 2,906. The 3,812-byte growth figure in task 8 checks out (23,995 to 27,807).
- Correction 5's evidence holds: `907-life`'s `ai-operational-rules.md:38-42` names
  `hugo --minify` and `public/` while `package.json:7` builds with `vite build` and
  `CLAUDE.md:112` carries the same pagefind deploy command `ecxc-ski`'s instruction file does.
- Every SHA the plan cites resolves: `3345620`, `8a958fe`, `7c7626c`, `08c132a`, `d2c4831`.
- Task 2's four quoted strings all exist in `unattended-work-guards.md` at `:11-13` and
  `:39-40`, and the memory file's "What the window learned" section exists at `:47`.

**The arithmetic question, recomputed.** The displacement does reach the target, with wide
headroom. 27,807 + 638 (the four lines, measured; see MINOR 12) = 28,445. Picks 1, 2, 3 and 5
shed 6,205 gross bytes as measured here, landing 22,240 before pointers, so the pointers may
total up to 1,759 bytes before the file re-crosses 24,000. `claude-context-budget` fails only
at 24,004 bytes or more (`toks -gt 6000`, integer division at `:61`), so the plan's "under
24,000" is conservative and correct. What does not hold is the path the plan tells the
implementer to walk there; see BLOCKER 1.

---

## BLOCKER

**1. Line 559 and lines 571-574: task 6's pick-application rule contradicts its own pick set
and cannot reach the target by the order it prescribes.** Line 559 says "Apply in rank order
until the file measures under 24,000 with the four lines landed, then stop", while line 571
says picks 1, 2, 3 and 5 are the set and line 573 makes pick 4 "the fallback"; recomputed,
picks 1 through 4 shed only 4,220 gross bytes against the 4,437 net the plan needs, so rank
order never stops before pick 5 and an obedient implementer lands all five while the prose
names four, and no acceptance criterion distinguishes the two diffs.
*Fix:* delete the rank-order sentence and state the fixed set {1, 2, 3, 5} as the work, with
pick 4 applied only if a measured shed leaves the file at or over 24,000.

**2. Line 600: task 6's criterion 2 forbids the very content its own constraints require, so
every correct diff fails it.** "The four lines appear in `CLAUDE.md` byte-identical to the
candidates document's draft, and no other new content was added" contradicts lines 578-582
and criterion 5 (line 607), which require a pointer naming the destination and preserving the
trigger phrase for every applied pick, and a pointer is new content.
*Fix:* rewrite criterion 2 as "no new content beyond the four lines and one pointer per
applied pick".

**3. Lines 531 and 552-555: task 6 never names where in `CLAUDE.md` the four lines go.** The
Files line says only "Modify", the outcome says only that they are "landed", and the
candidates document names no host section either; criterion 2 checks byte-identity of the
lines and nothing about placement, so a diff appending the four bullets under "Machine
Environment" passes every row.
*Fix:* name the host section in the task's outcome, or state that the four lines form a new
named section and give its heading.

---

## MAJOR

**4. Lines 446-448: task 4's criterion 1 names a command that cannot run.** `git -C
~/Projects/dubplate show HEAD:.claude/agents/go-architecture-reader.md` resolves to nothing
once the task's own dubplate commit deletes that path, and the criterion's trailing "at the
parent commit" contradicts the `HEAD:` it just wrote, leaving the reviewer to invent the form.
*Fix:* write `HEAD~1:` explicitly, matching the exact form task 3's criterion 2 already uses.

**5. Lines 702-703 and 747-749 against `claude/.claude/CLAUDE.md:226`: task 8's fold contract
diverges from the standing rule without saying so.** The rule is that a pass's close task is
"authored by one fold agent, which commits its draft and then folds"; the plan keeps the
agent's draft commit and the one independent `diff-reviewer` read, but moves the fold itself to
the conductor and asserts "The conductor owns the ledgers" as if that were the rule.
*Fix:* either follow the rule and let the fold agent fold, or state on line 702 that this
round departs from `CLAUDE.md:226` and why, so the divergence is a decision and not a drift.

**6. Line 194 with lines 758-760: three tasks marked Independent share one worktree and each
commits, and the plan never pins `parallel`.** Segment A runs tasks 1, 2 and 3 in one
`pass-execute` invocation, all three carry "Independent: yes", and the workstation rule treats
that marking as the opt-in for parallel mode; three concurrent implementers each staging and
committing in `~/.dotfiles` would race one index, next to another session's warm file.
*Fix:* state `parallel: false` for both `pass-execute` invocations in the Executor section, or
qualify the Independent column as disjoint-Files-only and say so.

**7. Lines 372-379 against lines 794-796: task 3 guards the hoisted skill against cross-repo
mis-trigger and leaves the two hoisted instruction files unguarded.** The plan argues the
`svelte-check` body names no repo-specific path and pins that with criterion 6, but makes no
neutrality claim for `ai-operational-rules.md` or `documentation-standards.md` and sets no
criterion for them; `ecxc-ski`'s bodies, which criterion 2 locks in byte-for-byte, carry `npm
run build && npx pagefind --site .svelte-kit/cloudflare`, `cd myproject && npx wrangler
deploy`, and "in this project", and after the hoist a dubplate or poplar session reads them at
`~/.claude/instructions/`.
*Fix:* add a criterion that each hoisted instruction body either carries no repo-specific
command or opens with one line scoping it to the SvelteKit site repos.

**8. Line 529: task 6's deliverable count of 4 is not honest.** The task lands four
docs-standard lines, applies four displacement picks, and creates two standalone documents,
which is about seven deliverables against the roughly-four rule, and the count of 4 appears to
be the Files count rather than the work.
*Fix:* restate the count honestly, and split the two created documents into their own task if
the honest number is over four.

**9. Lines 393 and 409: two of task 3's criteria cannot be checked.** Criterion 1 leaves its
comparison as a prose placeholder, `diff claude/.claude/skills/svelte-check/SKILL.md <either
retired repo copy at its parent commit>`, so no two reviewers run the same check; criterion
7's "no commit used `git add -A`" is not recorded anywhere in git history, so nothing could
falsify it.
*Fix:* give criterion 1 the exact `git -C <repo> show HEAD~1:<path> | diff - <hoisted path>`
form, and drop the add -A clause, which the `--name-only` half of the same criterion already
covers.

---

## MINOR

**10. Line 239: the `dubplate-implementer.md` step 5 citation is off by one at both ends.**
Step 5 runs `:67-70`, not `:68-71`.
*Fix:* correct to `:67-70`.

**11. Line 568: pick 4's measured size is 921 bytes, not 1,038.** The "Installing a NEW
long-lived secret" bullet is `CLAUDE.md:123-132` and measures 921, which makes line 561's
"picks 1 through 4 fall about 1,000 bytes short" right only by coincidence.
*Fix:* correct the table row to 921 and recompute the shortfall sentence from it.

**12. Lines 548 and 553: the four lines measure 638 bytes, not 630.** The candidates
document's own draft block at `:29-38` is 638 bytes by `wc -c`, so "Total before displacement"
on line 549 is 28,445 and the net that must leave is 4,445.
*Fix:* correct both figures, and note the candidates document's 630 is itself stale.

**13. Line 567: pick 3's measured size is 700 bytes, not 702.**
*Fix:* correct the table row.

**14. Lines 78 and 568: `registry.md`'s `secret-set.sh` flow starts at `:84`, not `:85`.** The
content claim is correct; only the anchor is off.
*Fix:* cite `:84-99`.

**15. Lines 515-516: task 5's criterion 4 delegates the whole substance of the
`fable-post-cutoff-system.md:12` edit to "the plan's Files line", which names only a file and
a line number and nothing about the change.** The reviewer is left with nothing to verify
against, while the 2026-09-04 plan does state the requirement in its own step at `:447`.
*Fix:* name in the criterion what line 12 must read after the edit, citing `:447` in the plan
rather than the Files line.

**16. Line 744: task 8's criterion 6 proves less than it claims.** Grepping the round's
touched files for the plan's filename catches a path citation and misses every citation of the
form "task 3, step 1" or a bare line range, which is the shape the rule actually bans.
*Fix:* grep for the citation shapes (`task \d`, `rung`, `:\d+-\d+`) rather than the filename.
