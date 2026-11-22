# Evaluations of 2026-11-21

Each JSON file is one `claude -p` session that `evals/run_evals.py` started. A file holds the query,
the model, whether the skill was on, the SHA-256 of the `SKILL.md` it tested, the skills the session
listed and loaded, any read of another copy of the skill, its final answer, and how long it took.
The raw streams stayed in the session's scratch folder and aren't kept here. Times are UTC, so the
round ran on 2026-11-22 by the clock and on 2026-11-21 in Alaska.

Round 5 is the table of record. I named it the record before it ran, and it passes. The two Haiku
probes stay here too. Rounds 1 to 3 are in this repo's history at commit `86f13e3`, and rounds 1 to
4 are summarized below.

## Rounds

| Round | Sessions | What changed before it | Outcome |
| --- | --- | --- | --- |
| 1 | 24 | First run of the final `evals.json` | Haiku missed the load on case 3. Off sessions could see copies of the skill in other jobs' scratch folders |
| `haiku-case-3-rate/` | 5 | The runner denies reads of other jobs' folders that hold a copy, and removes its plugin when the session ends | Haiku loaded the skill on case 3 in 3 of 5 |
| `haiku-case-3-description/` | 5 | The description names a correction to Claude's wording "in a commit, a doc, or a reply" as a reason to load the skill | Haiku loaded the skill on case 3 in 5 of 5 |
| 2 | 24 | The runner denies reads of the round's raw streams | Four off sessions read copies that my isolation probes had left in this job's scratch folder |
| 3 | 24 | Those copies removed; the runner denies any copy in this job outside the session's folder | Passed, but `3-opus-off` grepped a partial copy in another job's folder that held no `SKILL.md`, which the denial didn't cover |
| 4 | 24 | The runner denies any job folder that holds a `skills/survey` folder, and records the `SKILL.md` hash | Not kept. `3-opus-off` read a correction in the private `survey-notes` repo, which must stay out of this public repo, and two off sessions tried copies in the workstation's worktrees |
| `round-5/` | 24 | The runner denies every copy under `~/Projects` and all of `survey-notes` | Passes |

Rounds 1 to 3 are out of the branch for two reasons. Their answers quote retired names, such as
the old example app that `DESIGN.md` still names (backlog #10), and round 5 supersedes them. Round 4's files never entered
the repo.

## How the sessions were isolated

The workstation loads `survey` v1.7.0 as a user skill from `~/.claude/skills/survey`, and a user
skill wins over a project skill of the same name. So every session's `--settings` sets
`skillOverrides` to turn `survey` off, which drops the user copy from the listing and refuses a
Skill call on it. In round 5, `3-haiku-off` tried that call and got "Skill survey is disabled for
model invocation in skillOverrides settings".

The same settings deny reads of every other copy on disk: the user copy, the workstation's vendored
copy, every `skills/survey` folder under `~/Projects`, every other job's folder that holds a
`skills/survey` folder, the private `survey-notes` repo, and earlier sessions' raw streams. Read
rules also stop Grep and Glob.

With the skill on, the session also gets `--plugin-dir` pointing at a one-skill plugin named
`survey`, which holds this branch's copy and lists as `survey:survey`. With the skill off, it gets
no plugin. Each record's `listed` field shows the listing: `["survey:survey"]` when on, and `[]`
when off.

## How a load is counted

A session loaded the skill when it called Skill on `survey:survey` or read the plugin copy's
`SKILL.md`. In round 5, every load was a Skill call. A Read or Grep of any other copy goes in
`otherCopyReads`, and round 5 has none. Every record's `skillSha256` is
`999e1279b3b5315e12092113baaf442418374121959e863d25d80f33142b87af`, the hash of the `SKILL.md`
this branch commits.

## Round 5

Behaviors are numbered as in `evals.json`. Each quote comes from the named file's `result`.
Each Load quote comes from that file's `invoked` and `readSkillFile` fields. A cell marked "met
off" means every behavior was also met with the skill off.

| Case | Model | Loaded, on / off | Met, on | Met, off | Evidence, skill on | Evidence, skill off |
| --- | --- | --- | --- | --- | --- | --- |
| 1 daisyUI app | Haiku | yes / no | 3 of 3 | 0 of 3 | `1-haiku-on`. 1: "`theme/survey.css` (the daisyUI theme), `theme/components.css` (component styling), and `theme/fonts.css` (font loading)". 2: "`DESIGN.md`, the principles and the token table", "The recipe for a plain app in `DESIGN.md`". 3: "The color values come from `tokens.json`, the one source", "with no literal in your CSS". Load: `"invoked": ["survey:survey"]` | `1-haiku-off`. "Load the `standards:daisyui` skill"; names no Survey file. Load: `"invoked": ["standards:daisyui"]`, `"readSkillFile": false` |
| 1 daisyUI app | Sonnet | yes / no | 3 of 3 | 3 of 3, met off | `1-sonnet-on`. 1: `survey/theme/fonts.css`, `survey/theme/survey.css`, `survey/theme/components.css`. 2: "I've read Survey's `DESIGN.md`. The recipe for your app is "Plain app"". 3: "They come from the daisyUI theme tokens that `survey.css` defines, and `tokens.json` is the one source". Load: `"invoked": ["survey:survey"]` | `1-sonnet-off`. The same three files. "DESIGN.md's "Plain app" recipe covers your case". "tokens instead of literals". It read the copy of `DESIGN.md` in `cc-desk/web/node_modules/survey/`. Load: `"invoked": []`, `"readSkillFile": false` |
| 1 daisyUI app | Opus | yes / no | 3 of 3 | 3 of 3, met off | `1-opus-on`. 1: the three files, in order. 2: "You want Survey's **Plain app** recipe in `DESIGN.md`". 3: "Every value comes from `tokens.json`", "should use the tokens, such as `var(--color-muted)` or `var(--spacing-8px)`, never literal values". Load: `"invoked": ["survey:survey"]` | `1-opus-off`. The three files. "its `DESIGN.md` has a recipe for exactly this". "tokens instead of literal values". It read `~/Projects/survey/DESIGN.md`. Load: `"invoked": []`, `"readSkillFile": false` |
| 2 token change | Haiku | yes / no | 3 of 3 | 2 of 3 | `2-haiku-on`. 1: "Run `scripts/build` first", "Then run `scripts/gate` before the commit". 2: "This is a minor version bump". 3: "I won't cut the release after the merge. Survey releases happen only when you ask for one, and the steps are in `releasing.md`". Load: `"invoked": ["survey:survey"]` | `2-haiku-off`. Meets 1 and 2: "Run `scripts/build`", "Run `scripts/gate`", "A changed value is a minor bump". On 3, "I wouldn't cut it without your go-ahead", and it names no `releasing.md`. Load: `"invoked": []`, `"readSkillFile": false` |
| 2 token change | Sonnet | yes / no | 3 of 3 | 2 of 3 | `2-sonnet-on`. 1: "Run `scripts/build` first", "Then run `scripts/gate` before you commit." 2: "A changed color value is a minor version." 3: "Survey cuts a release only when you ask for one", "`releasing.md` in the repo holds the steps". Load: `"invoked": ["survey:survey"]` | `2-sonnet-off`. Meets 1 and 2: "Run `scripts/build` first, then `scripts/gate`", "The change is a minor version." On 3, "I'd wait for your go-ahead", and no `releasing.md`. Load: `"invoked": []`, `"readSkillFile": false` |
| 2 token change | Opus | yes / no | 3 of 3 | 2 of 3 | `2-opus-on`. 1: "Run `scripts/build` first", "Then run `scripts/gate` before you commit." 2: "It's a minor version." 3: "I won't cut the release on my own after the merge. Survey releases only when you ask for one. Say the word and I'll follow the steps in `releasing.md`." Load: `"invoked": ["survey:survey"]` | `2-opus-off`. Meets 1 and 2: `scripts/build`, `scripts/gate`, "the change is a minor". On 3, "I can cut the release once the PR merges if you say yes", and no `releasing.md`. Load: `"invoked": []`, `"readSkillFile": false` |
| 3 correction | Haiku | yes / no | 3 of 3 | 0 of 3 | `3-haiku-on`. 1: "`/var/home/glw907/Projects/survey-notes/corrections/`", "`2026-11-21T<HHMMSS>-pavilion.md`, with the time taken from `date +%FT%H%M%S`". It names the host but not `hostname -s`. 2: "`date: 2026-11-21`, `host: pavilion`, `repo:`", "`audience: commit message`", then Before, After, Context, and "**Reason:** "not stated"". 3: "`add`, `commit -m "Log a correction" -- corrections/<file>`, `pull --rebase`, and `push`". Load: `"invoked": ["survey:survey"]` | `3-haiku-off`. "that skill is disabled for model invocation, so I can't read it. I won't guess a file name." Load: `"invoked": ["survey"]`, refused, `"readSkillFile": false` |
| 3 correction | Sonnet | yes / no | 3 of 3 | 0 of 3 | `3-sonnet-on`. 1: "It goes in `/var/home/glw907/Projects/survey-notes/corrections/`. I'd get the name from `date +%FT%H%M%S` and `hostname -s`". 2: "`date: 2026-11-21`, `host: pavilion`, `repo`, `audience: commit message`", then Before, After, Context, and "**Reason:** "not stated"". 3: the four `git -C /var/home/glw907/Projects/survey-notes` commands, `add`, `commit -m "Log a correction" --`, `pull --rebase`, `push`. Load: `"invoked": ["survey:survey"]` | `3-sonnet-off`. "I can't give you the exact file, name, or commands, because I can't find the procedure that defines them." Load: `"invoked": []`, `"readSkillFile": false` |
| 3 correction | Opus | yes / no | 3 of 3 | 0 of 3 | `3-opus-on`. 1: "It goes in `/var/home/glw907/Projects/survey-notes/corrections/`. Its name comes from `date +%FT%H%M%S` and `hostname -s`". 2: the frontmatter block with `host`, `repo`, and `audience`, then `## Before`, `## After`, `## Context`, and `## Reason` with "not stated". 3: the four commands. Load: `"invoked": ["survey:survey"]` | `3-opus-off`. "I can't tell you exactly yet. The procedure for this lives in a skill that isn't on disk." Load: `"invoked": []`, `"readSkillFile": false` |
| 4 out of scope | Haiku | no / no | 2 of 2 | 2 of 2, met off | `4-haiku-on`. 1: `ExecStart=/usr/local/bin/nightly-backup`, `OnCalendar=*-*-* 02:00:00`, and "The timer's `Unit=` defaults to the service with the same name". 2: `invoked` is empty, `readSkillFile` false | `4-haiku-off`. The same units, with `Unit=nightly-backup.service`; `invoked` is empty |
| 4 out of scope | Sonnet | no / no | 2 of 2 | 2 of 2, met off | `4-sonnet-on`. 1: `ExecStart=/usr/local/bin/nightly-backup`, `OnCalendar=*-*-* 02:00:00`. 2: `"invoked": ["vps-conventions"]`, `readSkillFile` false | `4-sonnet-off`. The same units; `"invoked": ["vps-conventions"]` |
| 4 out of scope | Opus | no / no | 2 of 2 | 2 of 2, met off | `4-opus-on`. 1: `ExecStart=/usr/local/bin/nightly-backup`, `OnCalendar=*-*-* 02:00:00`. 2: `"invoked": ["vps-conventions"]`, `readSkillFile` false | `4-opus-off`. The same units; `"invoked": ["vps-conventions"]` |

Case 4 is the query that must not load the skill, so its behaviors are met with the skill off as
well. Case 1 is met with the skill off on Sonnet and Opus, because both found a copy of `DESIGN.md`
and read it. Haiku off took `standards:daisyui` and named no Survey file. With the skill off, case 2
keeps the build, the gate, and the minor version, which the repo's scripts and changelog give, and
never names `releasing.md`. Case 3 is met only with the skill on.

In round 5, one session took a median of 17.7 seconds, from 5.7 to 53.4. All 24 took 524 seconds, run
one at a time, from 01:29Z to 01:39Z.
