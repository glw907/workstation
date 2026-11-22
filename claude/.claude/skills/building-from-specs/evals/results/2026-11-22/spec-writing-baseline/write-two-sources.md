# Spec: `notes search`

Written 2026-11-22 from `brief.md`, the design Geoff settled in conversation. Everything here was read or run
against commit `745419b` on `main`.

This spec adds one command, `bin/notes search <word>`, in one task that ends in one pull request. The task is
planned at 41 minutes. Two things in it go beyond the brief, and both need your eye before you approve: the
brief's exit code for "no match" contradicts a promise in the README, and the task changes `README.md`, a file
the brief doesn't name. The next section covers both.

One more thing has to be settled before launch, and it needs no ruling. This checkout may be behind the
remote. `task-report` lists pull request 18, "Let notes add read stdin", but `bin/notes:5` here reads no
stdin, the log holds one commit, and the checkout has no `origin/main` ref to compare with. "Start conditions"
says what the launching session does about it.

## Where the brief and the repo disagree

The brief says: "No match prints nothing and exits 1."

`README.md` lines 10 to 11 say: "Every command exits 0 when it runs, even when it prints nothing, and 2 on a usage
error. Scripts that call `notes` rely on that."

Both can't hold once `search` exists. Nobody could answer while this spec was written, so I decided, and
approving the spec approves the decision.

**What I decided.** The brief wins. `search` exits 1 when nothing matches. The README changes so that it stays
true: it describes `search`, and its sentence about exit codes says that `add` and `list` exit 0 whenever they
run, that `search` exits 1 when nothing matches, and that every command exits 2 on a usage error. The second
sentence, about scripts, stays and is narrowed to `add` and `list`, the two commands it is still true of.

**Why.** The brief is your later and more specific word, and it marks the point "not open". The README's
promise protects scripts that exist today. Today `bin/notes search rope` prints the usage line and exits 2, so
no working script calls it, and none can break. `add` and `list` keep exit 0, and a done item checks that.

**What this adds to the brief.** The brief says "The work changes `bin/notes` and `tests/run.sh`." This spec
adds `README.md` as a third file. Without it the task would merge a README that is false in one sentence and
silent about the new command.

**What reversing costs.** If you want `search` to exit 0 on no match, so the README's promise holds for every
command, that is one line in `bin/notes`, one test, and one README sentence, before or after the build. If you
want the README left alone, the task drops that file and line 10 stays false until someone fixes it.

## Intent

Geoff's words: "I want to find a note without scrolling through the whole list."

The goal is a `search` command that prints the notes containing a word, in the order `list` prints them, and
tells a calling script by its exit code whether it found any.

These are not goals: patterns or wildcards, a search for several separate words, highlighting, line numbers,
any change to how `add` or `list` behave, a change to how `tests/run.sh` finds its tests, and fixing the
warnings `shellcheck` reports today in `tests/run.sh`. The work adds no service, no dependency, and no
release.

The work has failed if any of these is true after it merges:

- A character that means something to `grep` or the shell, such as `.`, `*`, `[`, `\`, or a leading `-`,
  changes what `search` finds.
- A search with no match prints anything, or exits with a code other than 1.
- `add` or `list` exit differently than they do today.
- A new test is written but never runs. The loop at `tests/run.sh:15` lists its tests by name, so a function
  left off that line is silently skipped.
- The README still says every command exits 0.

## What `search` does

The word is everything after `search`, joined with single spaces, the way `add` builds its text. A note is one
line of `$NOTES_FILE`. A note matches when it contains the word as plain text, with upper and lower case
treated alike. Matching notes go to stdout exactly as stored, in file order, which is oldest first because
`add` appends.

| Case | stdout | stderr | Exit |
| --- | --- | --- | --- |
| One or more notes match | The matching notes, oldest first | Nothing | 0 |
| No note matches | Nothing | Nothing | 1 |
| The notes file doesn't exist | Nothing | Nothing | 1 |
| The word contains a newline | Nothing | Nothing | 1 |
| No word, or an empty word (`notes search ""`) | Nothing | The usage line | 2 |
| Any unknown command | Nothing | The usage line | 2 |

The usage line becomes exactly this:

```text
usage: notes add <text> | notes list | notes search <word>
```

The word is checked before the file. A search with no word exits 2 whether or not the notes file exists.

Three edges are decided here and listed again under the calls.

A missing notes file is "no match", because `list` already treats a missing file as no notes (`README.md`
lines 4 to 5). The code must check for the file itself: `grep` on a missing file prints an error and exits 2,
which a caller would read as a usage error.

A word that contains a newline matches nothing, because no one-line note can contain it. The code must guard
for this: `grep -F` reads a newline as "either of these words", which is a pattern, and the brief rules
patterns out.

A notes file that exists but can't be read is left as `grep` reports it: its message on stderr and exit 2. No
test covers it, because a permission test passes falsely when the suite runs as root.

`search` sets no limits. It prints every match with no cap, reads the file once, and holds none of it in
memory. Case matching follows `grep` in the caller's locale: in this machine's `en_US.UTF-8` a search for
`école` found `École visit`, and under `LC_ALL=C` it didn't. The tests use ASCII words only, so they pass in
either locale.

## Approaches considered

All three were run today against a file holding `buy rope`, `Call ROPE shop`, `a.c`, `abc`, and `fix -v flag`.
The probes that use brackets, a star, or a backslash ran after two more lines were added, `cost [est] 5*2` and
`path C:\tmp`.

| Approach | Label | What the probe showed | Trade-off |
| --- | --- | --- | --- |
| `grep -iF -- "$word" "$file"` | Documented | `rope` printed both rope notes, `a.c` printed only `a.c`, `-v` printed only `fix -v flag`, `zebra` printed nothing and exited 1 | One line of code. Needs three guards: missing file, empty word, newline in the word. |
| A bash loop comparing `${line,,}` with `*"${word,,}"*` | Assembled from documented pieces | `ROPE` printed both rope notes | No extra process and no newline guard. One missing pair of quotes turns the word into a wildcard with no error, and the loop is slow on a long file. |
| `awk -v w="$word" 'index(tolower($0), tolower(w))'` | Assembled from documented pieces | `c:\T` printed a warning, "escape sequence `\T' treated as plain `T'", and missed `path C:\tmp`, which `grep -iF` found | `awk -v` rewrites backslashes, so the word stops being plain text. |

The pick is `grep -iF --`. Each of its three guards is one line, and each has a done item that fails without
it. The `awk` form is out because it breaks the brief's "plain text" rule. The done items test what `search`
prints and returns, so a builder who finds a reason to use the loop instead is still held to the same result.

## Sources

Every mechanism in this spec is `grep` or plain bash. Each label below rests on a quote from this machine's
GNU grep 3.12 or on a probe run today under GNU bash 5.3.9.

| Mechanism | Label | Source |
| --- | --- | --- |
| `-F` makes the word plain text | Documented | `grep --help`: "-F, --fixed-strings PATTERNS are strings". Probe: `grep -i -- a.c` printed `a.c` and `abc`; with `-F` it printed only `a.c`. `[EST]`, `5*2`, and `c:\T` each matched only their literal text. |
| `-i` ignores case | Documented | `grep --help`: "-i, --ignore-case ignore case distinctions in patterns and data". |
| `--` stops a word being read as an option | Probe | `grep -iF -- -v "$f"` printed `fix -v flag`. Without `--`, `grep -iF -v "$f"` took `-v` as an option and the file's path as the word, then waited on stdin until the 120-second limit stopped it. |
| Exit codes 0, 1, and 2 | Documented | `man grep`: "Normally the exit status is 0 if a line is selected, 1 if no lines were selected, and 2 if an error occurred." The brief's codes follow the same convention. |
| A missing file needs its own check | Probe | `grep -iF -- rope "$f.missing"` printed "No such file or directory" and exited 2. |
| An empty word needs its own check | Probe | `grep -iF -- '' "$f"` printed all 5 lines and exited 0. |
| A newline in the word needs its own check | Probe | `grep -iF -- $'zebra\nabc' "$f"` printed `abc` and exited 0. |
| `set -e` passes `grep`'s exit 1 through | Probe | A script with `set -euo pipefail` whose `case` arm ran a `grep` with no match exited 1 and ran nothing after it. `bin/notes` has the same `set` line, so the code states its exit codes on purpose and doesn't lean on this. |

The spec proposes no Claude Code mechanism of its own. The build, the review, and the pull request follow the
`building-from-specs` skill as written, so there was no Anthropic docs page to read for a new mechanism.

Only one task exists, so no assumption is shared between tasks.

## Files

The file list comes from five searches of the working tree, with `.git`, `.claude`, `.workstation`,
`brief.md`, `CLAUDE.md`, and this `spec.md` left out. Each `grep -r` also named 11 entries it couldn't read,
such as `.bashrc` and `.idea`. They are untracked device nodes that belong to this sandbox, and they are
dismissed. The third search looked for `notes add` or `notes list`.

| Search | Hits | What each hit means |
| --- | --- | --- |
| `git ls-files` | 5 | `bin/notes`, `tests/run.sh`, and `README.md` change. `scripts/gate.sh` only calls `tests/run.sh` and stays as it is. `brief.md` is the source of this spec and stays as it is. |
| `grep -rn usage` | 5 | `bin/notes:7` is the usage line, and it changes. `README.md:10` is the exit-code sentence, and it changes along with the sentence on line 11 that depends on it. `tests/run.sh:12` and `:13` are `test_usage`, which checks only the first word of the line and stays as it is. `tests/run.sh:15` is the loop's list of tests, and it gains the new names. |
| `grep -rnE` for `notes add` or `notes list` | 5 | `README.md:3` and `:4` describe the commands, and that paragraph gains `search`. `bin/notes:7` is the usage line again. `tests/run.sh:7` and `:10` are existing tests and stay as they are. |
| `grep -rnE 'exits?\b'` | 4 | `README.md:10` and `bin/notes:7`, both covered above. `tests/run.sh:2` is a comment that stays true. `tests/run.sh:18` is the runner's own exit and stays as it is. |
| `grep -rnoE 'test_[a-z_]+'` | 6 | Three test functions, at `tests/run.sh:6`, `:9`, and `:12`, and their three names on the loop line `:15`. No test is found any other way, so every new test must be added to line 15. |

The task changes three files:

- `bin/notes`: a `search` arm in the `case`, and the new usage line.
- `tests/run.sh`: five new test functions and their names on the loop line. The three existing functions stay
  untouched.
- `README.md`: the first paragraph describes `search`, and the last paragraph gives the exit codes as built.
  Its voice standard is `~/.claude/docs/voice/written-for-people.md`, which the `writing-voice` skill names
  for a README in a shell repo.

## Commands and the denials log

`.workstation/denials.log` holds three refusals, and all three fall in the last 30 days, 2026-10-23 to
2026-11-22. Each was read against the commands this task runs.

| Refused | Reason logged | What the task does about it |
| --- | --- | --- |
| 2026-11-03, `git push --force origin main` | Force push to the default branch | The task pushes only the branch it created and never forces. A fix after the first push is a new commit, never an amended one. |
| 2026-11-09, `rm -rf ~/.notes.bak` | Recursive delete outside the working folder | The task never reads, writes, or backs up the real `~/.notes`. Every run of `bin/notes`, in a test or by hand, sets `NOTES_FILE` to a file from `mktemp`. Tests that tidy up remove single files with `rm -f`, as `test_list_empty` does today, and nothing uses `rm -r`. |
| 2026-11-17, WebFetch of `https://example.invalid/notes` | Unknown host | The task fetches nothing. What it needs to know about `grep` is quoted under Sources. |

The task's own commands were all run in Claude Code today: `bash scripts/gate.sh`, `bin/notes` with
`NOTES_FILE` set, `mktemp`, `printf`, and `grep`. The commit, the push, and the pull request belong to the
skill's sections "A session at work" and "The pull request", and this spec copies none of their flags.

## The task: `notes-search`

**Goal.** Geoff can run `bin/notes search <word>` and get the notes that contain the word, and a pull request
against `main` on `example/notes` is ready for him to approve.

**Files.** `bin/notes`, `tests/run.sh`, `README.md`.

**Reviewer.** `standards:diff-reviewer` on Opus at high. The work touches no sign-in or data path and renders
no UI, so no second reviewer reads it.

**Session.** Opus at medium effort, launched as the skill's "Launching a task" says.

**Waits for.** Nothing. It is the only task, so the merge order is its one pull request.

**Minutes.** 41, and the goal's time clause is `or stop after 82 minutes`. `task-report --since 2026-11-01`
lists three tasks in this repo. The two that changed a command are the like ones: "Add notes list" measured 34
minutes, and "Let notes add read stdin" measured 41 with one fix round. Both ran past their planned 30.
`search` has more edge cases than `list`, so the estimate is the higher measured figure. "Add the usage test", at 12 minutes, changed only a test
and isn't a like task. The task waits on nothing: `.workstation/remote.txt` says the repo runs no CI on pull
requests.

### Done items

The checks use one fixture. Each was run today on `745419b`, and today's result is beside it. The gate was run
twice and printed the same output both times.

```bash
f=$(mktemp)
printf '%s\n' 'buy rope' 'Call ROPE shop' 'a.c' 'abc' 'fix -v flag' > "$f"
```

1. **A match prints the notes, oldest first, whatever their case.** `NOTES_FILE=$f bin/notes search rope`
   prints `buy rope` and then `Call ROPE shop`, nothing on stderr, and exits 0.
   `NOTES_FILE=$f bin/notes search ROPE` prints the same two lines. Today each prints the old usage line on
   stderr and exits 2, as do the commands in items 2 to 5.
2. **The word is plain text.** `NOTES_FILE=$f bin/notes search a.c` prints only `a.c`.
   `NOTES_FILE=$f bin/notes search -v` prints only `fix -v flag`. Both exit 0. Each of
   `NOTES_FILE=$f bin/notes search 'b*e'`, `NOTES_FILE=$f bin/notes search '[a-z]'`, and
   `NOTES_FILE=$f bin/notes search $'zebra\nabc'` prints nothing and exits 1.
3. **No match is silent and exits 1.** `NOTES_FILE=$f bin/notes search zebra` prints nothing on stdout or
   stderr and exits 1. So does `NOTES_FILE=$f.missing bin/notes search rope`, where the file doesn't exist.
4. **A missing word is a usage error.** `NOTES_FILE=$f bin/notes search` and `NOTES_FILE=$f bin/notes search ""`
   each print nothing on stdout, print exactly `usage: notes add <text> | notes list | notes search <word>` on
   stderr, and exit 2. So does `NOTES_FILE=$f.missing bin/notes search`, because the word is checked before
   the file. `NOTES_FILE=$f bin/notes bogus` prints the same line and exits 2. `test_search_usage` sets
   `NOTES_FILE` the same way, so no run can reach the real `~/.notes`.
5. **Several words make one phrase.** `NOTES_FILE=$f bin/notes search buy rope` prints only `buy rope` and
   exits 0.
6. **`add` and `list` behave as before.** `NOTES_FILE=$f.missing bin/notes list` prints nothing and exits 0,
   and `NOTES_FILE=$f bin/notes list` prints the five notes and exits 0. With `g=$(mktemp)`,
   `NOTES_FILE=$g bin/notes add buy rope` prints nothing and exits 0, and `NOTES_FILE=$g bin/notes list` then
   prints `buy rope`. All four do the same today. The diff leaves every test function that exists on
   `origin/main` unchanged.
7. **The gate passes and runs the new tests.** On the branch's last commit, `bash scripts/gate.sh` exits 0,
   prints no `FAIL` line, and prints an `ok` line for every test it runs on `origin/main` plus one each for
   `test_search_match`, `test_search_plain_text`, `test_search_no_match`, `test_search_usage`, and
   `test_search_phrase`. Those five tests assert items 1 to 5 in that order, including each exit code. Today
   the gate prints three `ok` lines and exits 0, and `bash scripts/gate.sh | grep -c '^ok   test_search_'`
   prints `0` where the finished branch prints `5`. The repo has no CI, so this run is the only full one, and
   the session quotes its output in the pull request.
8. **The README matches the tool.** `cat README.md` shows a description of `bin/notes search <word>` and
   exit-code sentences that agree with items 1 to 6. No sentence says every command exits 0, and the sentence
   about scripts names only `add` and `list`. Today the file is 11 lines, and lines 10 to 11 stop being true
   once `search` exists.
9. **Only the three files change.** `git diff --name-only origin/main...HEAD` prints `README.md`, `bin/notes`,
   and `tests/run.sh`, and nothing else. This checkout has no `origin/main` ref, so today I ran the same
   command with `main`; it printed nothing and exited 0. The task's worktree starts from `origin/main` and has
   the ref.
10. **The pull request is ready.** The session checks this item itself, after the review. The pull request
    opened as a draft on the first push, the reviewer read items 1 to 9 on the branch's last commit and
    returned accept, and only then was it marked ready against `main` on `example/notes`. Its body follows the
    skill's section "The pull request", with `planPathMin` set to 41.

### Start conditions

Before launch, the launching session fetches `origin` and compares `origin/main` with `745419b`, the commit
this spec was checked against. If they match, the spec stands as written. If `origin/main` is ahead, the
session reads the commits between them against this spec's line numbers, usage line, and "today" results, and
corrects the spec before it launches. The done items describe what `search` does, so they hold either way,
except where they quote today's output. I couldn't fetch from this sandbox.

`spec.md` is not committed, because this session was told to commit nothing, and the task's worktree starts
from the remote's `main`. So the worktree won't hold the spec. The goal names the spec by its absolute path in
the main checkout, and the reviewer's brief does the same. `brief.md` is tracked and will be in the worktree.

The task needs no secret from the store. It pushes and opens its pull request with the GitHub sign-in the
workstation already has, which I couldn't check from this sandbox.

The skill's four launch checks were tested today as far as this sandbox reaches. `claude agents --json`
printed `[]`, so no session was working that it could see. `claude-worktree-busy` isn't on this sandbox's
path, so the busy check for the main checkout wasn't run. The repo is public and runs no CI, so no CI check
applies. The session that launches the task runs all four checks again on the day. A push or a pull request
that is refused mid-run follows the skill's "In place of a question".

## Backlog sweep

The scoped sweep had no items in scope, so it lists no verdicts. The repo tracks no backlog file:
`git ls-files | grep -iE 'backlog|todo|status|issues'` returned 0 hits, and there is no `docs` folder. With no
items, there was no file to hand a sweep reader, so none was dispatched, and no full sweep is due. If the repo
keeps its backlog as GitHub issues, they weren't readable from here. An issue that names one of the three
files would need its own verdict from you, since approving this spec approves no backlog edit.

## Calls Claude made

The first two change or add to what the brief settled. They are the ones to check.

1. **Exit 1 on no match stands, against `README.md` line 10.** Passed over: exit 0, which keeps the README's
   promise for every command. Reversing means one line of code, one test, and one README sentence.
2. **`README.md` joins the file list.** Passed over: leaving it alone, as the brief's file list reads.
   Reversing means dropping one file from the task.

The next seven are product calls the brief left open. Each took the reading closest to what the tool already
does.

3. **Several words after `search` join into one phrase.** `add` joins its arguments the same way. Passed over:
   a usage error for more than one word. Reversing changes one line and one test.
4. **An empty word counts as a missing word** and exits 2. Passed over: letting it match every note, which is
   what `grep` does and what `list` is for.
5. **A word with a newline matches nothing** and exits 1. Passed over: letting `grep` treat it as two words.
6. **A missing notes file is "no match"**: silent, exit 1. Passed over: an error message and exit 2.
7. **An unreadable notes file is left as `grep` reports it**, with its message and exit 2, and has no test.
8. **The usage line's exact text** is `usage: notes add <text> | notes list | notes search <word>`.
9. **Output is the stored line and nothing else.** No line numbers, no highlighting, no count.

The rest are method calls.

10. `grep -iF --` is the mechanism, with three guards. Case matching follows the caller's locale, and the
    tests use ASCII.
11. New tests are added to the loop line by name. The runner keeps its hand-written list.
12. The five test names in done item 7 are fixed here so the gate's output can be checked.
13. The task is planned at 41 minutes, the higher of the two measured command tasks.
14. The task session runs on Opus at medium, and `standards:diff-reviewer` is the only reviewer.
15. `spec.md` stays untracked and the goal names it by absolute path. If you want the spec in the repo, it
    needs its own pull request, since the README says work reaches `main` that way.
16. The backlog sweep lists no verdicts, because the repo has no backlog file.
17. The `shellcheck` warnings in `tests/run.sh` today (SC2164 and SC2329) are left alone. `shellcheck` isn't
    part of the gate.
18. The spec was checked against local `745419b` and the launching session compares it with `origin/main`
    before launch. Passed over: holding the spec until the remote could be read.
19. The word is checked before the file, so a search with no word exits 2 even when the notes file is missing.

## The fresh reader's findings

One fresh reader on Fable at high read this spec against the repo and returned 12 findings. It confirmed 45 of
the spec's stated facts and couldn't check 6 from its sandbox.

**Answered already (3).** The README's voice standard comes from the `writing-voice` skill's table, which the
reader couldn't open. `planPathMin` and the section names come from the `building-from-specs` skill, which it
also couldn't open. A refused push is covered by the skill's "In place of a question", and the spec now says
so.

**Minor calls, made and marked (9).** Done items 1 and 2 gained an upper-case word and two wildcard words,
because a build with an unquoted comparison passed the first draft. Done item 4 now sets `NOTES_FILE` and
fixes the order of the word and file checks. Done item 6 gained a run of `add`. Done item 7 no longer counts
on three existing tests. Done item 8 reads the whole README, and the spec says what happens to line 11. Done
item 10 no longer asks the reviewer to check its own verdict. The estimate moved from 40 to 41. The search
table, two probe descriptions, and the backlog wording were corrected.

**For Geoff (0 new).** The reader found the mismatch between `task-report` and this checkout. It is a start
condition the launching session settles, and it changes nothing you are asked to approve. The two questions at
the top of this spec are still the only ones that are yours.
