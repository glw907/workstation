# Outline: round design for backlog #63, #69, and #70

Repo: glw907/workstation (`~/.dotfiles`). Default branch: `main`. This is an outline: each part is named and filled in a line or two. Sources read: `pass-core` `SKILL.md`, `references/planner.md`, `references/round.md`, `references/round-run.md`, `references/conductor.md`, `references/planning-samples.md`, the `dotfiles-pass` adapter, `cairn-pass` and `site-pass` (the lines #63 names), and `~/.claude/docs/voice/approval-brief.md`.

## Questions recorded, with the answer assumed

No one answers, so each question carries the answer this outline went on with.

1. **Where does #63's wrapper live?** `scripts/gate.sh` already exists in this repo (and in approval-queue, dubplate, initiatives, and poplar), and none exists in cairn-cms or the four sites (probe M3). The wrapper for those repos is code in repos this round doesn't cover. Assumed: this round edits only the two adapter skills here, wording each so a repo with `scripts/gate.sh` runs `bash scripts/gate.sh` and any other repo keeps the string form, and files one backlog follow-up per repo that lacks the wrapper. No file outside this repo changes.
2. **Which initiative owns the round?** #69 and #70 carry the `#initiative:workstation-refinement` tag and #63 carries `#initiative:monthly-model-review`. Assumed: the round files under the first, as the tag on two of the three items, and names the second in the PR body of the #63 pass. The design writes no initiative record beyond the one `planner.md` "Launch" allows.
3. **Has the freeze that #69 waits on ended?** #69 says to rebuild "once the freeze that follows the workstation refinement ends". A search of `docs/STATUS.md` and `BACKLOG.md` for "freeze" finds only #69's own line (S1), so nothing records an end. Assumed: it ended, and the round starts only after the `ur-ws` round's close packets merge, since its PRs touch `cairn-pass/SKILL.md` too.
4. **Does #69 restore the 166 branch's other half?** The item says direct landing of skill edits is outside it. Assumed: out of scope, and the pass lists it under "Found, not done" only if the code shows it.
5. **Is a fetch inside the SessionStart hook's 10-second timeout?** The hook's `timeout` in `claude/.claude/settings.json` is 10, and the rebuild fetches four remotes. Assumed: the fetches run in parallel under a per-fetch cap, and a slow remote is skipped with a warning line, never a failed hook. The pass's first task probes it (assumption A2).
6. **Does a wording-only edit of `cairn-pass` and `site-pass` take "Direct changes"?** It adds a form to a gate step, so a rule changes. Assumed: no, it is a pass (P3).

## Backlog sweep (scoped)

The three items are the scope. Verdicts, which the design's approval also approves:

| Item | Verdict | Reason |
| --- | --- | --- |
| #63 | reword | `gate.sh` exists in this repo, so the item is the adapter wording in two skills plus a follow-up per repo (question 1) |
| #69 | keep, fold into P1 | The hook still has no checkout fast-forward (`gather-dotfiles.sh` holds the host line and the initiatives section only: M1) |
| #70 | keep, fold into P2 | `shellcheck` still prints SC2140 at line 173 and `scripts/check.sh` still excludes it (M2) |
| #72, #73, #75 | keep | Read for overlap; none shares a file with this round |
| #68 | keep | `cairn-run-gate` and `claude-tail-guard` fixes, a different file set |

A full sweep is due when `standards:backlog-sweep` says so; this outline assumes it is not, and the design checks the stamp dates.

## Round design

**Round id:** `ws-hygiene` (10 characters, lowercase and hyphen).

**Design page** opens with `## Brief` per `~/.claude/docs/voice/approval-brief.md`: one background paragraph (a stale checkout, a suppressed shellcheck finding, an adapter that gives a form the guard refuses), one or two summary paragraphs (what approving does: three passes, one packet for the `auth-data` pass), then the `### Decide:` blocks. It names its published sources: the changesets snapshot rule is not needed (no release), the Anthropic prompting guides in `planning-samples.md`, and ShellCheck's SC2140 wiki page (<https://www.shellcheck.net/wiki/SC2140>).

**Infrastructure:** none added. The design says so in one line, so the Cloudflare against Hetzner weighing doesn't apply.

**Models:** design and plan authors `claude-opus-5-5` at `high`; conductor and executors `sonnet` at `medium`; P2 (auth-data) an executor on Sonnet at `high`, since it edits a guarded file.

### Pass table

| Pass | Outcome | Files | Class | Path min | Depends on | Shares a file with |
| --- | --- | --- | --- | --- | --- | --- |
| P1 `fresh-co` | #69: the hook fast-forwards the shared checkouts | `claude/.claude/gather-dotfiles.sh`, `tests/gather-dotfiles-checkouts.test.sh`, `scripts/check.sh` (one new leg) | runner | 60 | none | P2 (`scripts/check.sh`) |
| P2 `drift-quote` | #70: SC2140 gone from `check-drift`, exclusion removed | `bin/.local/bin/check-drift`, `scripts/check.sh` | auth-data | 30 | P1 | P1 |
| P3 `gate-wrap` | #63: both adapters give the no-argument form | `claude/.claude/skills/cairn-pass/SKILL.md`, `claude/.claude/skills/site-pass/SKILL.md`, `BACKLOG.md` | runner | 35 | the `ur-ws` round's merge (shares `cairn-pass/SKILL.md` with the unmerged W5 PR) | the W5 PR |

Longest chain: P1 then P2, 90 minutes, far under the 600-minute cap. Round total 125 minutes, so answer 7's twice-planned limit is 250.

P1 runs first: its assumptions (the hook timeout, live-session detection, a fast-forward that never forces) are the least proven, so a wrong one costs one pass. P2 waits for P1 because both edit `scripts/check.sh`. P3 shares no file with P1 or P2 and runs third only because the conductor runs one pass at a time.

### Acceptance lists (fixed on approval; each item can fail)

**P1**
1. `bash tests/gather-dotfiles-checkouts.test.sh` exits 0 and prints one pass line for each case: behind and clean (fast-forwards), behind with a live session in it (skips, names the session), behind on a non-default branch (skips), behind with a dirty file the merge touches (skips), diverged (never forces), remote unreachable (hook still exits 0).
2. Run from a scratch repo, the hook's stdout keeps its `## Host` line and the initiatives section, and its exit code is 0 in every case above.
3. The hook finishes in under 10 seconds with one remote that never answers; the command and its timing are in the PR.
4. The four checkouts it handles are dotfiles, approval-queue, servers, and initiatives; the test fails if one is dropped.
5. `bash scripts/gate.sh` prints `gate exit: 0` and the changed-files lane lists the new leg.

**P2**
1. `shellcheck -S warning bin/.local/bin/check-drift` prints nothing and exits 0.
2. `grep -n 'SC2140' scripts/check.sh` prints nothing, and `check_shellcheck` has one `shellcheck` call with no per-file branch.
3. The warning line still prints the same text to a user: the test run of `check-drift` against a stubbed `claude-pass --status` of `path=none` prints `Claude's agent: none on this host yet` and the `bluefin-admin/secrets.md` pointer.
4. `bash tests/check-drift-proton.test.sh` and the rest of `check-drift`'s tests pass unchanged.
5. The PR carries the `auth-data` verdict from one `standards:web-auth-security-reviewer` read.

**P3**
1. `grep -n "cairn-run-gate '<string>'" claude/.claude/skills/cairn-pass/SKILL.md claude/.claude/skills/site-pass/SKILL.md` prints nothing as the only gate form; each file's Gate line names `bash scripts/gate.sh` first and the string form second, under a stated condition.
2. Each file says the string form fails a worktree session's guard and the no-argument form passes (the sentence `dotfiles-pass` already carries, quoted from its source).
3. `claude-pass-load --check` prints its "after" word counts and each is under its cap.
4. Five backlog follow-ups exist (cairn-cms, ecxc-ski, 907-life, aksailingclub-org, cairn-pub), each naming the gate string its wrapper must run, and #63 is marked done with the PR's number.
5. `bash scripts/gate.sh` prints `gate exit: 0`.

Each list is played back to Geoff at the sitting, with no mockup needed since nothing is visual. A planner or an executor may add a check and never edits or drops an item.

### Shared assumptions

| # | Assumption (more than one pass depends on it) | Probe or quoted source |
| --- | --- | --- |
| A1 | `scripts/check.sh` holds one `check_shellcheck` with a per-file `check-drift` branch (P1 adds a leg beside it, P2 edits it) | `grep -n 'SC2140' scripts/check.sh` printed lines 89 and 99 (M2) |
| A2 | The SessionStart hook is `~/.claude/gather-dotfiles.sh` with `timeout: 10` | `grep -n SessionStart -A8 claude/.claude/settings.json` printed `"command": "~/.claude/gather-dotfiles.sh"` and `"timeout": 10` |
| A3 | New test files are picked up by a `run <name> '<path regex>' ...` line in `scripts/check.sh`, and a skill edit moves the `pass-loads` count | `check.sh` lines 140 to 151 list the pattern (M4) |
| A4 | Round `ur-ws` merges before this round launches, so the W5 edits to `cairn-pass/SKILL.md` are on `main` | Not probed at design time: `docs/STATUS.md` shows the passes waiting for the round's close packet. The conductor prompt's first step runs `git rev-list --count HEAD..origin/main` and the order table starts P1 only after the `ur-ws` report reads `Round state: ended` |
| A5 | `claude agents --json` lists live sessions with their `cwd`, which is how P1 decides "no other live session" | `claude-worktree-busy` already uses it; its probe is the record in BACKLOG #75 (a session row's `cwd` in the path reads as busy). P1's first task re-probes and quotes the output |

A4 has no probe yet, so the design isn't ready for the packet until the conductor's check is written into the order table as a gate on P1. That is recorded here as the one open reading.

## Mechanisms (table the plans extend)

| # | Mechanism | Probe run, or quoted source |
| --- | --- | --- |
| M1 | The hook only prints the host line and the initiatives section | `cat claude/.claude/gather-dotfiles.sh`: no `git fetch` or `merge` call in 55 lines |
| M2 | SC2140 fires on line 173 only | `shellcheck -S warning bin/.local/bin/check-drift` printed one finding, `SC2140 (warning): Word is of the form "A"B"C"` at line 173; `scripts/check.sh:99` carries `--exclude=SC2140` |
| M3 | Which repos have a no-argument gate wrapper | `ls ~/Projects/*/scripts/gate.sh` printed approval-queue, dubplate, initiatives, poplar, and workstation; cairn-cms and the sites are absent |
| M4 | How a test joins the gate | `scripts/check.sh` lines 150 to 151 run `gather-dotfiles` with a path regex and `bash tests/gather-dotfiles-initiatives.test.sh` |
| M5 | The wrapper form the guard accepts | `scripts/gate.sh` header: "a worktree-isolated session's Bash guard refuses `cairn-run-gate '<string>'` ... a no-argument wrapper passes" |
| M6 | The old attempt's diff no longer applies | BACKLOG #69: closed PR #166 edited `pass-core` and the `dotfiles-pass` path map, which #228 rewrote; the plan rebuilds from the item's text and the kept `fresh-checkouts` branch read-only |

Each plan adds rows for its own change sites and verifies each against the code as the earlier passes left it. No row says "expected".

## Recorded searches (design time)

| # | Search | Hits | Disposition |
| --- | --- | --- | --- |
| S1 | `grep -rn -i freeze docs/STATUS.md BACKLOG.md` | 1 (BACKLOG #69) | The item's own words; question 3 |
| S2 | `grep -rn "cairn-run-gate '"` over both skill trees and `docs/STATUS.md` | 5 | `cairn-pass:26` and `cairn-pass:31`, `site-pass:34`: P3 edits. `pass-core` `references/executor.md:55`: the form the guard refuses, owned by `pass-core`; left alone and filed as a follow-up, since #63 names the adapters. `dotfiles-pass:22`: already the no-argument form |
| S3 | `grep -rn SC2140` outside plans and `.git` | 4 | BACKLOG #70 (2 lines, closed by P2), `docs/STATUS.md:80` (P2 updates the line), `scripts/check.sh:89` and `:99` (P2 edits) |
| S4 | `grep -rln gather-dotfiles` outside `.git` | 8 | `settings.json`, `scripts/check.sh`, and the existing test are P1's. `bluefin/SECOND-WORKSTATION.md`, `docs/HISTORY.md`, two old plans, BACKLOG: history or prose, dismissed |

Each plan re-runs these and records its own with hit counts.

## Denial-log read

`~/.local/state/claude-denials.jsonl`, 60 rows, 2026-11-01T00:55:05Z to 2026-11-12T06:25:31Z. Classes: Self-Modification 10, Interfere With Workloads 9, Merge Without Review 3, Auto-Mode Bypass 3, Unverifiable Deletion Scope 2, Sensitive-Source Provenance 2, and 10 rows with no class ("classifier judged this dangerous"), plus 4 "Classifier unavailable". The tasks' commands come near three: Self-Modification (P3 must not touch a `settings.json`; every Edit is on a skill file, and none is refused in the log), Interfere With Workloads (P1's live-session test must start and stop only the processes it spawned, and never `pkill` by pattern; the alternative is a fake `claude` stub script on `PATH`), and Merge Without Review (the conductor lands with `approval-queue land`, never `gh pr merge`). One unclassed row refused a Python heredoc edit of a skill file, so executors edit with the Edit tool only. A `check-drift` edit is in `auth-data`: P2's Edit is not in the log, and the alternative if refused is a packet step for Geoff. Each plan repeats the read against its own commands.

## Standing answers

The twelve in `round-run.md` hold. The design adds these:

- **S-A.** P1's probe finds the hook can't fetch inside 10 seconds even in parallel with a cap: the pass parks (answer 12), since a slow hook delays every session start.
- **S-B.** A checkout is dirty in a file the merge touches, or on a non-default branch: skip it with one warning line. This is the behavior, not a stop.
- **S-C.** P2's `shellcheck` finds a second finding in `check-drift` once the first is fixed: the pass fixes it only if the quote change causes it, otherwise files it and keeps a narrow exclusion; the PR's `## Decisions` says which.
- **S-D.** P3 finds a repo already has a `scripts/gate.sh`: the adapter's condition is correct as written, and no follow-up is filed for that repo.
- **S-E.** Usage ceiling: 85 percent of the weekly allowance (answer 4); nothing here sets another.
- **S-F.** An estimate overrun up to twice the pass's minutes continues; past it, answer 7.

No stop says "ask Geoff".

## Merge order and packets

Order: P1, P2, P3, behind the `ur-ws` merges. Every PR's base is `main`, and every fact file and landing carries `--round ws-hygiene`.

- P1: lands with `approval-queue land --round ws-hygiene` when its review reads `accept, open findings 0`, `Calls: none`, and no `## Before merge` section. A new check-drift or test leg is not a call.
- P2: `auth-data`, so the order table marks it as waiting for Geoff; it rides a close packet. P3 doesn't depend on it and lands on its own.
- P3: lands directly under the same test.
- If P1 needs a `## Before merge` step (for example `stow -R claude` so the live hook matches), the PR carries it and the packet raises it; the design assumes the hook is read from the stowed path, so a merge plus a pull makes it live and no step is needed.

## Plan outlines

Every plan opens with `Initiative:`, `Round: ws-hygiene`, and `Pass:` lines, a `## Pre-flight` with `Permissions checked:`, `Reviewed:` (one `standards:plan-reviewer` read), and `Evidence:`, then the parts below. Each plan names its worktree by path, `~/.dotfiles/.claude/worktrees/<pass>`, and `main` as the PR's base. Pre-flight for all three: no step for Geoff, no sign-in or secret, no workspace-trust prompt (the repo's worktrees are already trusted); each task's writes are skill or script files, and none is to a settings file.

### P1 plan: the checkout fast-forward (#69)

- **Mechanisms:** M1, M4, A2, and A5 re-probed with their output; the `fresh-checkouts` branch is read with `git log` and `git show` for design hints, never merged.
- **T1 (15 min):** write `tests/gather-dotfiles-checkouts.test.sh` first, one case per item in acceptance 1, with fake remotes in a temp directory.
- **T2 (25 min):** add the checkout function to `claude/.claude/gather-dotfiles.sh`: fetch each of the four, fast-forward only on the default branch with no other live session, one status line each, exit 0 always.
- **T3 (10 min):** add the `check.sh` leg with its path regex; run the fast lane, then the full gate.
- **T4 (10 min):** the timing probe (acceptance 3) and the closing evidence.
- **Acceptance:** copied verbatim, each mapped to its task and command.
- **Stops:** each with S-A or S-B as its answer.

### P2 plan: the quote fix (#70)

- **Mechanisms:** M2, plus a quoted shellcheck wiki sentence on SC2140.
- **T1 (10 min):** escape the inner quotes at line 173, keeping the text; the alternative (point the text at `bluefin-admin/secrets.md`) is the one the item names, chosen if the escape reads badly in the output.
- **T2 (10 min):** collapse `check_shellcheck`'s branch and drop its comment; run the fast lane.
- **T3 (10 min):** update `docs/STATUS.md` line 80 and close #70 in the backlog; full gate; the `auth-data` review read.
- **Pre-flight note:** the file is `auth-data`, so the plan lists the path map's row and the class decision, and the packet carries the verdict.

### P3 plan: the adapter wording (#63)

- **Mechanisms:** M3, M5, S2's hit list.
- **T1 (15 min):** edit the two Gate lines and `cairn-pass:31`'s lane sentence to the new form, keeping both skills under their word caps.
- **T2 (10 min):** file the five follow-ups through `standards:log-issue` and mark #63.
- **T3 (10 min):** `claude-pass-load --check`, `claude-tooling-sync verify`, the full gate, and the closing review.
- **Acceptance:** verbatim, with the grep and the word counts as evidence.

## Checks before the packet

1. One fresh Opus reader with no context runs the `standards:brainstorming` builder check on this design: could a builder plan every pass, and could any acceptance item pass on a wrong result (the dirty-checkout case and the `check-drift` message case are the two a wrong build could slip past, so each has its own item).
2. Geoff's touchpoints: the design packet and its pre-flight sitting, the `[you: ...]` steps (none foreseen), and one close packet for P2.
3. Launch: the designing session commits one planner prompt per pass and one conductor prompt (`conductor-dotfiles`), whose order table carries each pass, its prompt, its dependency, its minutes, and the mark on P2.
