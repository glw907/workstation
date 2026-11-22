# Evaluations of 2026-11-21

Each JSON file is one `claude -p` session that `evals/run_evals.py` started. A file holds the query,
the model, whether the skill was on, the skills the session loaded, its final answer, and how long it
took. The raw streams stayed in the session's scratch folder and aren't kept here.

Round 5 is the table of record. Rounds 4 and 5 both ran the final `evals.json` under the same
conditions. Round 4 missed one cell: Haiku didn't load the skill on case 3. I changed nothing after
it, measured that cell's rate, and named round 5 the record before it ran. Round 5 passes. Round 4
stays here in full.

## Rounds

| Folder | Sessions | What changed before it | Outcome |
| --- | --- | --- | --- |
| `round-1/` | 24 | First queries, written as quizzes about the role | Case 2 missed the load on Haiku and Sonnet, case 3 on Haiku, and case 1 on Haiku and Sonnet never read `spec.md` |
| `round-2/` | 17, stopped | Queries 1 to 3 rewritten as the requests a session receives | Stopped when case 2 still missed on Haiku and Sonnet |
| `round-3/` | 24 | Query 2 asks about the task session in the third person; the skill is copied into the project, not linked | Case 3 missed on Haiku; with the skill off, Haiku and Opus found the copy and read it |
| `haiku-case-3-probes/` | 3 | Query 3 takes its final form | Haiku loaded the skill in 3 of 3 |
| `round-4/` | 24 | No copy of the skill when it is off; `evals.json` is final from here on | Fails one cell: Haiku missed the load on case 3 |
| `haiku-case-3-rate/` | 10 | None | Haiku loaded the skill on case 3 in 10 of 10 |
| `round-5/` | 24 | None | Passes |
| `haiku-case-1-hidden/` | 3 | The skill copy sits in a gitignored `.claude/`, out of Glob's view | Haiku called Skill on case 1 in 3 of 3 |

On the final query, Haiku loaded the skill on case 3 in 14 of 15 sessions: the 3 probes, round 4's
miss, the 10 rate sessions, and round 5.

## How a load is counted

A session loaded the skill when it called Skill on `building-from-specs` or read its `SKILL.md`. In
round 5, Haiku's loads on cases 1 and 2 were reads, and every other load was a Skill call. The raw
streams show how Haiku reached the file. On case 2 it searched `~/.claude` for
`**/building-from-specs/**/*.md`, by the skill's name, so the listed description led it there. On
case 1 it first listed the project with `**/*`, which showed it the copy. To rule out that the
listing alone drew the read, `haiku-case-1-hidden/` reran case 1 three times with the copy hidden
from Glob. Each session read `spec.md` and then called Skill on `building-from-specs`.

## Round 5

Behaviors are numbered as in `evals.json`. Each quote comes from the named file's `result`.
Each Load quote comes from that file's `invoked` and `readSkillFile` fields.

| Case | Model | Loaded, on / off | Met, on | Met, off | Evidence, skill on | Evidence, skill off |
| --- | --- | --- | --- | --- | --- | --- |
| 1 launch | Haiku | yes / no | 4 of 4 | 1 of 4 | `1-haiku-on`. 1: `claude --bg --name mobile-nav --model claude-sonnet-5-5 --effort medium`, `--permission-mode auto`. 2: `"denyInsteadOfPrompting":true`, `"baseRef":"fresh"`. 3: "Or stop after 90 minutes." 4: "`claude-worktree-busy <checkout>` exits 0". Load: `"readSkillFile": true` (a Read of `.claude/skills/building-from-specs/SKILL.md`) | `1-haiku-off`. "I can't give you a verified launch command"; gives `claude -p "<brief>"`. Meets 4 only: `claude-worktree-busy <worktree-path>`. Load: `"invoked": []`, `"readSkillFile": false` |
| 1 launch | Sonnet | yes / no | 4 of 4 | 1 of 4 | `1-sonnet-on`. 1: `claude --bg --name mobile-nav --model sonnet --effort high --permission-mode auto`. 2: `"denyInsteadOfPrompting":true`, `"baseRef":"fresh"`. 3: "Or stop after 90 minutes." 4: "`claude-worktree-busy <checkout>` exits 0". Load: `"invoked": ["building-from-specs"]` | `1-sonnet-off`. `claude --bg --model sonnet --effort medium --advisor fable`, with no permission mode, settings, or time clause. Meets 4 only. Load: `"invoked": ["pass-core"]`, `"readSkillFile": false` |
| 1 launch | Opus | yes / no | 4 of 4 | 1 of 4 | `1-opus-on`. 1: `claude --bg --name mobile-nav --model opus --effort medium --permission-mode auto`. 2: `"denyInsteadOfPrompting":true`, `"baseRef":"fresh"`. 3: "Or stop after 90 minutes." 4: "`claude-worktree-busy ~/Projects/example-site` exits 0". Load: `"invoked": ["building-from-specs"]` | `1-opus-off`. "it can't run yet", "No plan", `--advisor fable`. Meets 4 only. Load: `"invoked": ["pass-core"]`, `"readSkillFile": false` |
| 2 open points | Haiku | yes / no | 3 of 3 | 0 of 3 | `2-haiku-on`. 1: "It doesn't stop or ask Geoff." 2: "The session takes the side that a later commit could undo most cheaply", "it records the side it took, the side it passed over, and what reversing would undo". 3: "The session doesn't edit `~/.dotfiles/claude/.claude/settings.json`", "the PR body carries the exact hook entry, the file it belongs in, and a check command". Load: `"readSkillFile": true` (a Read of `.claude/skills/building-from-specs/SKILL.md`) | `2-haiku-off`. "the session stops that part and asks you". Load: `"invoked": []`, `"readSkillFile": false` |
| 2 open points | Sonnet | yes / no | 3 of 3 | 0 of 3 | `2-sonnet-on`. 1: "The task session asks Geoff nothing and waits for nothing." 2: "takes the option a later commit can undo most cheaply", "names the side taken, the side passed over, and what reversing would undo". 3: "The session leaves that file alone", "puts the change in the pull request as exact text", "Beside it goes the check that shows the hook took". Load: `"invoked": ["building-from-specs"]` | `2-sonnet-off`. "the hook line is a stop", "calls the advisor once on the question and takes the answer". Load: `"invoked": ["pass-core"]`, `"readSkillFile": false` |
| 2 open points | Opus | yes / no | 3 of 3 | 0 of 3 | `2-opus-on`. 1: "The task session doesn't stop for either one, and it doesn't ask." 2: "take the option a later commit undoes most cheaply", "Passed over: the left. Switching sides changes the button's position". 3: "The session leaves `~/.dotfiles/claude/.claude/settings.json` alone", "It writes the exact JSON for the hook entry into the pull request, along with the check". Load: `"invoked": ["building-from-specs"]` | `2-opus-off`. "This one stops the task", "It builds the side the advisor picks". Load: `"invoked": ["pass-core", "cc-desk-work"]`, `"readSkillFile": false` |
| 3 merge | Haiku | yes / no | 4 of 4 | 2 of 4 | `3-haiku-on`. 1: `gh pr merge 412 --repo glw907/example-site --merge`. 2: `git -C <main-checkout> pull --ff-only`. 3: `worktree remove .claude/worktrees/mobile-nav`, then `branch -d worktree-mobile-nav`, then last `push origin --delete worktree-mobile-nav`. 4: "**Remove the worktree.** No force flag.". Load: `"invoked": ["building-from-specs"]` | `3-haiku-off`. `gh pr merge 412 --repo glw907/example-site --squash`, and `git pull --ff-only origin main` after the remote delete. Meets 2 and 4. Load: `"invoked": []`, `"readSkillFile": false` |
| 3 merge | Sonnet | yes / no | 4 of 4 | 2 of 4 | `3-sonnet-on`. 1: "4. `gh pr merge 412 --repo glw907/example-site --merge`". 2: "5. `git -C <main> pull --ff-only`". 3: "6. `git -C <main> worktree remove .claude/worktrees/mobile-nav`", "7. `git -C <main> branch -d worktree-mobile-nav`", "8. `git -C <main> push origin --delete worktree-mobile-nav`". 4: "None of these use a force flag.". Load: `"invoked": ["building-from-specs"]` | `3-sonnet-off`. "6. `approval-queue land 412`", no remote delete. Meets 2 and 4. Load: `"invoked": ["pass-core"]`, `"readSkillFile": false` |
| 3 merge | Opus | yes / no | 4 of 4 | 2 of 4 | `3-opus-on`. 1: `gh pr merge 412 --repo glw907/example-site --merge`. 2: `git -C ~/Projects/example-site pull --ff-only`. 3: `worktree remove .claude/worktrees/mobile-nav`, then `branch -d worktree-mobile-nav`, then last `push origin --delete worktree-mobile-nav`. 4: "Cleanup (no force flags)". Load: `"invoked": ["building-from-specs"]` | `3-opus-off`. `approval-queue land glw907/example-site#412`, no remote delete. Meets 2 and 4. Load: `"invoked": ["site-pass", "pass-core", "approval-packet"]`, `"readSkillFile": false` |
| 4 out of scope | Haiku | no / no | 2 of 2 | 2 of 2 | `4-haiku-on`. 1: `find . -type f -printf '%s\t%p\n' \| sort -rn \| head -n 10 \| numfmt --to=iec --delimiter=$'\t' --field=1`. 2: `invoked` is empty, `readSkillFile` false | `4-haiku-off`. `find . -type f -printf '%s\t%p\n' \| sort -nr \| head -n 10 \| numfmt --field=1 --to=iec --delimiter=$'\t'`; `invoked` is empty |
| 4 out of scope | Sonnet | no / no | 2 of 2 | 2 of 2 | `4-sonnet-on`. 1: `find . -type f -printf '%s\t%p\n' \| sort -nr \| head -10 \| numfmt --to=iec --field=1`. 2: `invoked` is empty, `readSkillFile` false | `4-sonnet-off`. `find . -type f -printf '%s\t%p\n' \| sort -rn \| head -n 10 \| numfmt --field=1 --to=iec`; `invoked` is empty |
| 4 out of scope | Opus | no / no | 2 of 2 | 2 of 2 | `4-opus-on`. 1: `find . -type f -printf '%s\t%p\n' \| sort -rn \| head -n 10 \| numfmt --field=1 --to=iec`. 2: `invoked` is empty, `readSkillFile` false | `4-opus-off`. `find . -type f -printf '%s\t%p\n' \| sort -rn \| head -n 10 \| numfmt --field=1 --to=iec`; `invoked` is empty |

Case 4 is the query that must not load the skill. Its behaviors are met with the skill off as well, so
it shows the skill stays out of the way and nothing more. With the skill off, cases 1 to 3 keep only
the behaviors that the global `CLAUDE.md` or `pass-core` already give: `claude-worktree-busy` on case
1, and `git pull --ff-only` and no force flag on case 3.

In round 5, one session took a median of 15.3 seconds, from 3.4 to 39.7. All 24 took 398 seconds, run one
at a time.
