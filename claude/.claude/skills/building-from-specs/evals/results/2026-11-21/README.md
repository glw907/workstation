# Evaluations of 2026-11-21

Each JSON file is one `claude -p` session that `evals/run_evals.py` started. A file holds the query,
the model, whether the skill was on, the skills the session loaded, its final answer, and how long it
took. The raw streams stayed in the session's scratch folder and aren't kept here.

Round 5 is the result of record. It is the first full round on the final `evals.json`, after the
Haiku load-rate check, and it was chosen as the record before it ran.

## Rounds

| Folder | Sessions | What changed before it | Outcome |
| --- | --- | --- | --- |
| `round-1/` | 24 | First queries, written as quizzes about the role | Case 2 missed the load on Haiku and Sonnet, case 3 on Haiku, and case 1 on Haiku and Sonnet never read `spec.md` |
| `round-2/` | 17, stopped | Queries 1 to 3 rewritten as the requests a session receives | Stopped when case 2 still missed on Haiku and Sonnet |
| `round-3/` | 24 | Query 2 asks about the task session in the third person; the skill is copied into the project, not linked | Case 3 missed on Haiku; with the skill off, Haiku and Opus found the copy and read it |
| `round-4/` | 24 | No copy of the skill when it is off; query 3 leads with Geoff's merge request | Case 3 missed on Haiku once more |
| `haiku-case-3-rate/` | 10 | None | Haiku loaded the skill on case 3 in 10 of 10 |
| `round-5/` | 24 | None | Passes |

On the final query, Haiku loaded the skill on case 3 in 14 of 15 sessions: 3 probes, round 4's miss,
the 10 rate sessions, and round 5.

## Round 5

A session loaded the skill when it called Skill on `building-from-specs` or read its `SKILL.md`.
Haiku's loads on cases 1 and 2 were reads of `SKILL.md`, and every other load was a Skill call. Each
quote comes from the named file's `result`.

| Case | Model | Loaded, on / off | Met, on | Met, off | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 launch | Haiku | yes / no | 4 of 4 | 1 of 4 | On, `1-haiku-on`: `claude --bg --name mobile-nav ... --permission-mode auto`, `"worktree":{"baseRef":"fresh"}`, "Or stop after 90 minutes.", "`claude-worktree-busy <checkout>` exits 0". Off, `1-haiku-off`: "I can't give you a verified launch command", `claude -p "<brief>"`; names `claude-worktree-busy` |
| 1 launch | Sonnet | yes / no | 4 of 4 | 1 of 4 | On, `1-sonnet-on`: `claude --bg --name mobile-nav --model sonnet --effort high --permission-mode auto`, `"permissions":{"denyInsteadOfPrompting":true}`, "Or stop after 90 minutes." Off, `1-sonnet-off`: `claude --bg --model sonnet --effort medium --advisor fable`, no permission mode, no settings, no time clause |
| 1 launch | Opus | yes / no | 4 of 4 | 1 of 4 | On, `1-opus-on`: `--permission-mode auto`, `"worktree":{"baseRef":"fresh"}`, "Or stop after 90 minutes.", "`claude-worktree-busy ~/Projects/example-site` exits 0". Off, `1-opus-off`: "it can't run yet... No plan", `--advisor fable` |
| 2 open points | Haiku | yes / no | 3 of 3 | 0 of 3 | On, `2-haiku-on`: "It doesn't stop or ask Geoff", "the side it took, the side it passed over, and what reversing would undo", "the PR body carries the exact hook entry, the file it belongs in, and a check command". Off, `2-haiku-off`: "the session stops that part and asks you" |
| 2 open points | Sonnet | yes / no | 3 of 3 | 0 of 3 | On, `2-sonnet-on`: "asks Geoff nothing and waits for nothing", "takes the option a later commit can undo most cheaply", "puts the change in the pull request as exact text". Off, `2-sonnet-off`: "the hook line is a stop", "calls the advisor once on the question and takes the answer" |
| 2 open points | Opus | yes / no | 3 of 3 | 0 of 3 | On, `2-opus-on`: "doesn't stop for either one, and it doesn't ask", "Passed over: the left. Switching sides changes the button's position", "It writes the exact JSON for the hook entry into the pull request, along with the check". Off, `2-opus-off`: "This one stops the task", "It builds the side the advisor picks" |
| 3 merge | Haiku | yes / no | 4 of 4 | 2 of 4 | On, `3-haiku-on`: `gh pr merge 412 --repo glw907/example-site --merge`, `pull --ff-only`, `worktree remove`, then `branch -d`, then `push origin --delete worktree-mobile-nav`. Off, `3-haiku-off`: `--squash`, and the pull runs after the remote delete |
| 3 merge | Sonnet | yes / no | 4 of 4 | 2 of 4 | On, `3-sonnet-on`: steps 4 to 8, `gh pr merge 412 --repo glw907/example-site --merge` through `push origin --delete worktree-mobile-nav`. Off, `3-sonnet-off`: "`approval-queue land 412`", no remote delete |
| 3 merge | Opus | yes / no | 4 of 4 | 2 of 4 | On, `3-opus-on`: `gh pr merge 412 --repo glw907/example-site --merge`, then `pull --ff-only`, `worktree remove`, `branch -d`, `push origin --delete worktree-mobile-nav`. Off, `3-opus-off`: "`approval-queue land glw907/example-site#412 ...`", no remote delete |
| 4 out of scope | Haiku | no / no | 2 of 2 | 2 of 2 | `4-haiku-on`: `find . -type f -printf '%s\t%p\n' \| sort -rn \| head -n 10 \| numfmt ...`; invoked nothing |
| 4 out of scope | Sonnet | no / no | 2 of 2 | 2 of 2 | `4-sonnet-on`: `find . -type f -printf '%s\t%p\n' \| sort -nr \| head -10 \| numfmt --to=iec --field=1`; invoked nothing |
| 4 out of scope | Opus | no / no | 2 of 2 | 2 of 2 | `4-opus-on`: `find . -type f -printf '%s\t%p\n' \| sort -rn \| head -n 10 \| numfmt --field=1 --to=iec`; invoked nothing |

Case 4's behaviors are met with the skill off as well. It is the query that must not load the skill, so
it shows the skill stays out of the way and shows nothing else about it. With the skill off, cases 1 to 3
each keep only the behaviors that the global `CLAUDE.md` or `pass-core` already give: `claude-worktree-busy`
on case 1, and `git pull --ff-only` and no force flag on case 3.

In round 5, one session took a median of 15.3 seconds, from 3.4 to 39.7. All 24 took 398 seconds, run one
at a time.
