# Spec: notes search

Written 2026-11-22 from `brief.md`, the design Geoff settled in conversation. This spec adds one command,
`bin/notes search <word>`, in one task that ends in one pull request, planned at 40 minutes. Nobody could answer
questions while it was written, so every open point is decided here and listed under
[Calls Claude made](#calls-claude-made).

Two things wait for Geoff when he approves. Three of the brief's done checks already pass on today's code, so
this spec keeps his words and adds a check beside each that fails today (call 1). And four edge cases the brief
doesn't cover are product calls that Claude made for him (calls 2 to 5).

## What Geoff asked for

"I want to find a note without scrolling through the whole list."

The goal is one new command that prints every note containing a word, oldest first. The match ignores case, and
the word is plain text, never a pattern. No match prints nothing and exits 1. A missing word exits 2 with the
usage line, and the usage line names the new command. The README names the command too.

These are not goals:

- A change to what `add` or `list` does.
- Patterns, several search terms, line numbers, a count, or highlighted matches.
- A fix to the test runner's hand-kept list of tests (`tests/run.sh:15`), or a new linter in the gate.
- Case folding beyond what `grep -i` does in the user's locale. The tests use ASCII only.
- A grep other than GNU grep. Only GNU grep 3.12 was probed.

The work has failed if any of these is true:

- A character such as `.`, `*`, `[`, or a leading `-` in the word changes what matches.
- `search` writes to the notes file.
- A test or a check reads or writes the real `~/.notes`.
- `add`, `list`, or the unknown-command usage error behaves differently than today.
- The pull request touches a file other than `bin/notes`, `tests/run.sh`, and `README.md`.

## What search does

The first five rows come from the brief. The rest are calls made here, and each has a number in the list of calls.

| Case | Standard output | Standard error | Exit | Source |
| --- | --- | --- | --- | --- |
| Notes contain the word | Each matching note, whole, in file order | Nothing | 0 | Brief |
| The word differs from a note only by case | The note | Nothing | 0 | Brief |
| The word holds pattern characters | Only notes that hold those exact characters | Nothing | 0 | Brief |
| No note contains the word | Nothing | Nothing | 1 | Brief |
| No word after `search` | Nothing | The usage line | 2 | Brief |
| The word is part of a longer word (`rope` in `ropes`) | The note | Nothing | 0 | Call 2 |
| The notes file doesn't exist | Nothing | Nothing | 1 | Call 3 |
| The word is the empty string | Nothing | The usage line | 2 | Call 4 |
| More than one argument after `search` | Nothing | The usage line | 2 | Call 5 |
| One quoted argument with a space (`'rope shop'`) | Notes that hold that text | Nothing | 0 | Call 5 |
| The word holds a newline | Nothing | Nothing | 1 | Call 6 |

The usage line becomes `usage: notes add <text> | notes list | notes search <word>`. It still goes to standard
error and still starts with `usage:`, which the existing `test_usage` checks. Every path that prints the usage
line prints this one.

When two rows apply, a usage error wins. `search` checks the argument count and the empty word first, then
the newline, then the file. So two arguments with no notes file exit 2.

A notes file that exists but can't be read is outside this spec. Whatever error the tool prints stands, and no
test covers it.

## How it matches

Three ways to match were weighed. Each was run on this machine (GNU grep 3.12, bash 5.3.9) against a file
holding `buy rope`, `Call ROPE shop`, `a.c`, `abc`, `-v flag`, `star * here`, `back\slash`, and `[x]`.

| Approach | Label | What the probe showed | Trade-off |
| --- | --- | --- | --- |
| A. `grep -F -i -e "$word" -- "$file"` | Documented | `rope` printed both rope notes in file order, exit 0. `a.c` printed only `a.c`. `-v`, `*`, `\s`, and `[x]` each printed only their own note. `zebra` printed nothing, exit 1. | One line, and grep's exit codes are the brief's. It needs three guards, listed after this table. |
| B. A bash loop that lowercases each line and the word, then tests `[[ ${line,,} == *"$w"* ]]` | Assembled from documented pieces | The same results as A for every word, and a word holding a newline matched nothing. | No guards for the newline case, but it is eight lines where A is one, and the loop keeps the exit code by hand. |
| C. `grep -i -e "$word"` | Documented | `a.c` printed both `a.c` and `abc`. | Fails "never a pattern". Rejected. |

The pick is A. Its source is the GNU grep manual on this machine. `grep --help` says `-F, --fixed-strings
PATTERNS are strings`, `-i, --ignore-case ignore case distinctions in patterns and data`, and `-e,
--regexp=PATTERNS use PATTERNS for matching`. `man grep` says "Normally the exit status is 0 if a line is
selected, 1 if no lines were selected, and 2 if an error occurred."

A needs three guards, and each was probed:

- A missing file. Bare grep printed `No such file or directory` and exited 2, so `search` checks for the file
  first and exits 1.
- An empty word. Bare grep printed every note and exited 0, so `search` treats it as a missing word.
- A word holding a newline. Bare grep read `zebra`, newline, `rope` as two words and printed both rope notes, so
  `search` exits 1 before it calls grep.

A throwaway copy of `bin/notes` with approach A and the three guards, kept outside the repo and deleted after,
produced every row of the table in [What search does](#what-search-does). The fixture file's checksum was the
same before and after the runs. So every check in the goal can be met.

The pick is a method, and the goal's checks are what bind. A session that finds A can't meet a check may use B
and says so under `## Decisions`.

## When it goes wrong

`search` has three exit codes: 0 for a match, 1 for no match, and 2 for a usage error. It sets no limit on the
size of the notes file and reads it once.

The task has one time limit, the goal's clause at 80 minutes. A fix verdict from the reviewer gets one second
read. The remote runs no CI on pull requests (`.workstation/remote.txt`: "The repo runs no CI on pull requests,
so the gate on a branch's last commit is its only full run"), so no CI wait applies, and the gate run quoted in
the pull request is the one on the branch's last commit. Everything else that can come up follows "In place of a
question" in `building-from-specs`.

## Files

The file list comes from four searches run with `git grep`, which reads tracked files only, so this spec and
the `.workstation` stand-ins stay out. `git ls-files` prints five files: `README.md`, `bin/notes`, `brief.md`,
`scripts/gate.sh`, and `tests/run.sh`.

`git grep -n 'usage'` has 5 hits.

- `bin/notes:7`, the usage line. It changes.
- `tests/run.sh:12`, `:13`, and `:15`, the `test_usage` test and the list of tests. Line 15 changes, and lines 12
  and 13 stay.
- `brief.md:9`. Dismissed: it is the brief.

`git grep -nE 'notes (add|list)'` has 5 hits.

- `README.md:3` and `:4`, the sentence that names the commands. The new command goes in this paragraph.
- `bin/notes:7`, the usage line again.
- `tests/run.sh:7` and `:10`. Dismissed: existing tests that stay as they are.

`git grep -n 'test_'` has 5 hits, all in `tests/run.sh`.

- Line 2, the comment "Runs every test_* function". The comment is wrong: line 15 runs a hand-kept list, so a
  new test that isn't added to that list never runs. The comment stays (not a goal), and the list grows.
- Lines 6, 9, and 12. Dismissed: existing test functions.
- Line 15, the list. It changes.

`git grep -ni 'search'` has 3 hits, all in `brief.md`. Dismissed: no code, test, or doc mentions search yet.

`scripts/gate.sh` has no hit and doesn't change. It runs `tests/run.sh`, so new tests join the gate on their own.

So the task changes three files, as the brief says: `bin/notes`, `tests/run.sh`, and `README.md`.

## Commands and the denials log

`.workstation/denials.log` has three entries, all inside the last 30 days (2026-10-23 to 2026-11-22). The task's
commands are the gate, `bin/notes` runs against temp files, `mktemp`, `rm -f` on one temp file, `grep`, `git`
staging by file name, commits, a plain push of the task's own branch, and `gh` for the draft pull request.

| Refused command | Reason logged | What the task does about it |
| --- | --- | --- |
| `git push --force origin main` | Force push to the default branch | The task pushes only its own branch and never forces. A fix after the first push is a new commit, never an amend. |
| `rm -rf ~/.notes.bak` | Recursive delete outside the working folder | Temp files from `mktemp` live outside the worktree. The tests make single files, never a directory, and remove one with `rm -f` as `tests/run.sh:10` does today. No test or check runs `rm -r`. |
| WebFetch to `https://example.invalid/notes` | Unknown host | The task fetches nothing. The grep facts it needs are quoted in this spec. |

## The task: add notes search

Files: `bin/notes`, `tests/run.sh`, `README.md`. It waits for no other task, and its pull request is the only
one, so there is no merge order.

### Goal

Items 1 to 7 run from the repo root against this fixture, made fresh for each run:

```bash
f=$(mktemp); printf '%s\n' 'buy rope' 'Call ROPE shop' 'a.c' 'abc' > "$f"
```

Every command below was run on today's code (commit 7115ad0) on 2026-11-22, and "Today" gives what it printed.

1. `NOTES_FILE=$f bin/notes search rope; echo "exit $?"` prints `buy rope`, then `Call ROPE shop`, then
   `exit 0`, and nothing else.
   Today: `usage: notes add <text> | notes list`, then `exit 2`.
2. `NOTES_FILE=$f bin/notes search a.c; echo "exit $?"` prints `a.c`, then `exit 0`, and nothing else.
   Today: the old usage line, then `exit 2`.
3. `NOTES_FILE=$f bin/notes search zebra; echo "exit $?"` prints `exit 1` and nothing else.
   Today: the old usage line, then `exit 2`.
4. `NOTES_FILE=$f bin/notes search; echo "exit $?"` prints
   `usage: notes add <text> | notes list | notes search <word>`, then `exit 2`.
   Today: `usage: notes add <text> | notes list`, then `exit 2`. The exit code already passes today, because
   any unknown command exits 2. The usage line is the part that fails.
5. `NOTES_FILE=$f bin/notes search bc; echo "exit $?"` prints `abc`, then `exit 0`, and nothing else.
   Today: the old usage line, then `exit 2`. A whole-word match would print nothing here.
6. `NOTES_FILE=$f.none bin/notes search rope; echo "exit $?"` prints `exit 1` and nothing else. No file is at
   `$f.none`.
   Today: the old usage line, then `exit 2`.
7. `NOTES_FILE=$f bin/notes search buy rope; echo "exit $?"` prints
   `usage: notes add <text> | notes list | notes search <word>`, then `exit 2`.
   Today: the old usage line, then `exit 2`. As in item 4, the usage line is the part that fails.
8. `bash scripts/gate.sh; echo "exit $?"`, run on the branch's last commit, prints no `FAIL` line and ends with
   `exit 0`.
   Today: three `ok` lines and `exit 0`. This is the brief's "the gate passes", and it passes today.
9. `bash scripts/gate.sh | grep -c '^ok   test_search_'` prints 4 or more.
   Today: `0`. The tests it counts are listed under [Tests](#tests).
10. `grep -c notes README.md` prints 1 or more.
    Today: `3`. This is the brief's check, word for word, and it passes today.
11. `grep -c 'bin/notes search <word>' README.md` prints 1 or more.
    Today: `0`.
12. `git diff --name-only origin/main...HEAD` prints `README.md`, `bin/notes`, and `tests/run.sh`, and nothing
    else.
    Today: `fatal: ambiguous argument 'origin/main...HEAD'`, because this checkout has never fetched `origin`
    and has no `origin/main` ref. With `main` in its place the command prints nothing and exits 0. The task's
    worktree starts from the remote's default branch, so the ref is there when the session runs it.
13. `standards:diff-reviewer` returns accept on the branch's last commit. It reads the branch against this goal,
    the table in [What search does](#what-search-does), the failure list in
    [What Geoff asked for](#what-geoff-asked-for), and the [Tests](#tests) and [README](#readme) sections. It
    confirms that each row of the table has a test that fails when that row is broken. Items 9 and 11 count
    names and can't show that.
14. One pull request against `main` on `example/notes` holds the work and is marked ready. "The pull request"
    and "Gates and review" in `building-from-specs` own how it is opened, written, and marked ready.

The goal ends with `or stop after 80 minutes`.

### Tests

`tests/run.sh` gains at least four test functions, one for each behavior the brief names. Every new test's
name starts with `test_search_`, and each name is added to the list on line 15, or the test never runs.

- A match: the word finds notes in file order and ignores case.
- Plain text: `a.c` finds `a.c` and not `abc`.
- No match: nothing on standard output or standard error, exit 1.
- A missing word: exit 2, and the usage line on standard error names `notes search <word>`.

The same tests or further ones cover the rest of the table and the failure list:

- A word inside a longer word matches.
- A word that starts with `-`, and a word that holds `*` or `[`, each match only notes holding those characters.
- One quoted argument with a space matches as plain text.
- A missing notes file, an empty word, two arguments after `search`, and a word holding a newline each give
  their row of the table.
- The notes file is byte for byte the same after a search.

Every `bin/notes` call in a new test sets `NOTES_FILE` to a file from `mktemp`, including the calls that exit
before they read the file. The three existing tests stay as they are. `test_usage` sets no `NOTES_FILE`, and it
never reaches the file.

### README

The paragraph that names `add` and `list` also names `bin/notes search <word>` and says what it prints, that
case is ignored, that the word is plain text, and that no match exits 1. The text `bin/notes search <word>`
stays on one line, because item 11 searches for it with grep. The README follows
`~/.claude/docs/voice/written-for-people.md`, the standard the `writing-voice` skill gives for a README in a
shell repo. A session that can't open that file matches the README's existing paragraph (plain sentences, with
commands in backticks) and says so under `## Decisions`.

### Reviewers

`standards:diff-reviewer` reads the branch. No other reviewer is needed: `search` reads one local file and
writes nothing, so this is no sign-in or data work, and it renders no UI.

### Minutes

The task is planned at 40 minutes, so the time clause is 80. `.workstation/task-report.txt` has three measured
tasks in this repo since 2026-11-01.

| Pull request | Title | Planned | Measured | Fix rounds |
| --- | --- | --- | --- | --- |
| 12 | Add notes list | 30 | 34 | 0 |
| 15 | Add the usage test | 15 | 12 | 0 |
| 18 | Let notes add read stdin | 30 | 41 | 1 |

Pull requests 12 and 18 are the like tasks: each added or changed a command, with its tests. Both were planned
at 30 and ran over. This task adds a command as 12 did and carries edge cases as 18 did, so it takes 40, near
the larger of the two. Pull request 15 changed tests only and is no guide. The task drives no CI, timer, or idle
limit, so nothing is added for waits.

### Launch

"Launching a task" in `building-from-specs` owns the launch command. The task session runs on Opus at medium
effort. The goal names this spec by its absolute path in the main checkout, because `spec.md` is not committed
and a fresh worktree doesn't hold it.

The start conditions, as tested on 2026-11-22:

- Sessions working: `claude agents --json` printed `[]`, and `hostname` printed `pavilion`, so fewer than four
  are working.
- Secrets: the task needs none from the store.
- CI: the task needs none. `.workstation/remote.txt` shows the repo is public, its default branch is `main`, and
  it runs no CI on pull requests.
- `claude-worktree-busy`: not run. See [Not checked from here](#not-checked-from-here).
- The remote's `main`: not fetched. Before the launch, the launching session fetches `origin` and confirms that
  `origin/main` is at 7115ad0 or holds it. If the remote lacks that commit, it doesn't launch.

A task session that starts in a worktree with no `bin/notes` builds nothing, writes that in its report, and
ends. The task session needs no file under `.workstation`: that folder is untracked, a fresh worktree lacks it,
and this spec quotes everything it uses from there.

## Backlog sweep

The scoped sweep found nothing to judge. The repo tracks five files, none of them a backlog, and it has no
`docs` folder. No item names a file this task changes, so nothing folds and no backlog edit rides on approval.
With no backlog, no full sweep is due.

## Calls Claude made

Calls 1 to 5 are Geoff's kind of call (product or scope), made because nobody could answer. Each can be
reversed in a later commit. The rest are method calls.

1. **Three of the brief's done checks pass today, so each gets a check beside it that fails today.** The
   brief's words stay in the goal. "The gate passes" (item 8) gains item 9, which counts the new tests.
   "`grep -c notes README.md` prints 1 or more" (item 10) prints 3 today, so it gains item 11, which looks for
   the new command's name. "A missing word exits 2" already holds today for any unknown command, so item 4 checks the
   usage line as well. Item 12, which holds the pull request to the brief's three files, is also new.
2. **"Contains" means the word can be part of a longer word.** `rope` finds `ropes`. The option passed over is
   whole-word matching. Reversing adds one grep flag and changes one test.
3. **A missing notes file counts as no match.** `search` prints nothing and exits 1, in line with `list`, which
   prints nothing when the file doesn't exist. The option passed over is an error message.
4. **An empty word counts as a missing word.** It exits 2 with the usage line. The option passed over is
   matching every note, which is what `list` is for.
5. **More than one argument after `search` is a usage error.** A phrase goes in quotes as one argument and
   matches as plain text. The option passed over is joining the arguments with spaces, as `add` does. An error
   can later be loosened to a join without breaking anyone's use, and the reverse can't.
6. A word holding a newline matches nothing and exits 1, because a note is one line.
7. `search` prints each matching note whole, as stored, on standard output.
8. The usage line reads `usage: notes add <text> | notes list | notes search <word>` and stays on standard
   error.
9. Case folding is whatever `grep -i` does in the user's locale. In `en_US.UTF-8` here, `érable` found
   `Érable`. Under `LC_ALL=C` it did not. The tests use ASCII.
10. The method is `grep -F -i -e`, with three guards.
11. `spec.md` stays out of the pull request. The goal names it by absolute path.
12. The task is planned at 40 minutes, from pull requests 12 and 18.
13. Only `standards:diff-reviewer` reads the work.
14. The task session runs on Opus at medium effort. Every behavior is decided here, so the session's judgment
    goes to the tests and the review, and the change is a few dozen lines.
15. When two rows of the behavior table apply, a usage error wins.
16. The test runner's hand-kept list and its wrong comment stay as they are. `shellcheck` is on this machine
    and warns once about `tests/run.sh:4` today (SC2164), but it is not in the gate, and this task doesn't add
    it. The repo has no backlog to log either point to, so they are named here.

## The fresh read

One fresh reader (Fable at high effort, no context) read this spec against the repo and the brief on
2026-11-22. It re-ran the four searches, the "Today" results, and the grep probes, and all matched. It found no
conflict with the brief. Its 13 findings sort like this.

- Answered already: none.
- Minor calls, made and marked here: the goal exercised none of the edge cases, and a whole-word match passed
  it (items 5 to 7 and the reviewer's wider read in item 13 are new); the tests list left out the substring,
  quoted-phrase, and pattern-character rows; the `NOTES_FILE` rule and the `test_search_` prefix didn't say
  which tests they cover; no order was given when two rows apply (call 15); the searches were written as plain
  `grep`, which also reads this spec; the build session had no rule for a remote without the commit, no
  fallback for the voice file, and no word that `.workstation` is absent from a fresh worktree.
- Questions only Geoff can answer: none beyond calls 1 to 5.

## Not checked from here

The session that launches the task checks these, because this session couldn't.

- `claude-worktree-busy` is not on this session's path, so the main checkout's busy state is untested.
- `origin` was not fetched. Whether `origin/main` is at 7115ad0, the commit every "Today" result was read on,
  is unknown.
- The denials log and the task report were read from the stand-in files under `.workstation`, not from the
  live tools.
- `~/.claude/docs/voice/written-for-people.md` couldn't be opened from here, so the README standard is named by
  the `writing-voice` skill's table and was not read.
- Whether the repo keeps a backlog as GitHub issues was not read from the remote.
