# Spec: notes search

This spec adds one command, `bin/notes search <word>`, to the notes tool in `example/notes`. It is
written from `brief.md`, the design Geoff settled in conversation, on 2026-11-22 against `main` at
`399e8de`. It is one task and ends in one pull request.

Nobody could answer a question while it was written. Each point the brief leaves open is decided
here and listed under [Calls Claude made](#calls-claude-made). Calls 1 to 6 are scope and product
calls, which are Geoff's to make, so they are the ones to check before approving. Call 1 is the
only one that departs from the brief's own words: it adds `README.md` to the two files the brief
names.

## Intent

Geoff said: "I want to find a note without scrolling through the whole list."

The goal is a search that prints every note containing a word, oldest first, ignoring case, with
the word read as plain text. The work is a failure if a search prints a note that doesn't contain
the word, misses one that does, treats any character of the word as a pattern, or changes what
`add` and `list` do today.

These are not goals: matching more than one word, patterns or wildcards, highlighting, line
numbers, a count, and any change to how notes are stored. The work adds nothing to host, publish,
or release.

## Behavior

The brief settles the first three rows. The other rows are calls, numbered to the list at the end.

| Invocation | Standard output | Standard error | Exit | Source |
| --- | --- | --- | --- | --- |
| `search <word>`, and a note contains the word | Each note that contains it, whole, in file order | Nothing | 0 | Brief; exit 0 is call 2 |
| `search <word>`, and no note contains it | Nothing | Nothing | 1 | Brief |
| `search` with no word | Nothing | The usage line | 2 | Brief |
| `search <word>`, and nothing exists at the notes file's path | Nothing | Nothing | 1 | Call 3 |
| `search ""` | Nothing | The usage line | 2 | Call 4 |
| `search` with two or more arguments after it | Nothing | The usage line | 2 | Call 5 |
| `search` with a word that contains a newline | Nothing | Nothing | 1 | Call 7 |
| `search <word>`, and the path exists but can't be read as a file | Nothing | An error that is not the usage line | 2 | Call 8 |
| Any unknown command | Nothing | The usage line | 2 | Today's code |

The usage line becomes `usage: notes add <text> | notes list | notes search <word>`. The brief
says only that the line names the new command, so its exact text is call 6.

File order is oldest first, because `add` only appends. "Contains" means the word appears anywhere
in the note, so `rope` finds `coil the ropes`. The word is the one argument after `search`, so a
quoted `"buy rope"` is one word with a space in it. A word that starts with a dash, or holds `.`,
`*`, `[`, or a backslash, is searched for as those characters. Case is folded by the rules of the
user's locale, and the tests use ASCII letters only.

## Approach

Three ways to match were weighed, and the pick is the first.

- `grep -a -i -F -e "$word" -- "$file"`. It is one line, and its exit statuses for a match and for
  no match are already the brief's 0 and 1. It departs from the table in three places, shown under
  [Sources](#sources), and the command needs a guard for each.
- A bash loop that compares `${line,,}` with `${word,,}`. It needs bash 4, its own match flag for
  the exit status, and its own error for a path it can't read.
- `awk` with `index(tolower($0), tolower(w))`. It needs the word passed through the environment to
  keep backslashes literal, and its own exit status.

The done items describe behavior only, so they hold whichever way the code is written. The task
session may leave the pick for a reason it records under `## Decisions`.

## When it goes wrong

Exit 1 means the search ran and found nothing. Exit 2 means it could not run: the word was missing
or empty, there were extra arguments, or the path exists and can't be read as a file. The guard
for a missing notes file therefore tests that nothing exists at the path. It does not test for a
regular file as `list` does, because that would turn a directory into a silent exit 1.

The work adds no limit. `grep` reads the file as a stream, so the file's size is not capped, and
the word's length is bounded only by the system's limit on an argument.

## Sources

`grep` with `-a`, `-i`, `-F`, and `-e` is documented. `grep --help` on this machine (GNU grep 3.12)
prints these lines:

```text
  -F, --fixed-strings       PATTERNS are strings
  -e, --regexp=PATTERNS     use PATTERNS for matching
  -i, --ignore-case         ignore case distinctions in patterns and data
  -a, --text                equivalent to --binary-files=text
```

Each probe ran on 2026-11-22 as `grep -i -F -e <word> -- <file>` on the fixture of the goal.

| Probe | Output | Exit | What it shows |
| --- | --- | --- | --- |
| `Rope` | `buy rope`, `Call ROPE shop`, `coil the ropes` | 0 | Case is ignored, and file order is kept |
| `a.c` | `a.c` | 0 | A dot is a dot: `abc` is not printed |
| `-v` | `x -v y` | 0 | `-e` keeps a leading dash from being read as an option |
| `zebra` | Nothing | 1 | No match is silent and exits 1 |
| `rope`, on a path where nothing exists | `grep: <path>: No such file or directory` | 2 | Guard needed |
| `zebra`, a newline, `cat` | `feed cat` | 0 | Guard needed: `-F` reads a newline as "either of these" |
| The empty string | Every note | 0 | Guard needed |
| `rope`, on a directory | `grep: <path>: Is a directory` | 2 | The table's last-but-one row, with no guard |
| `cat`, on a file where another note holds a NUL byte | `grep: <path>: binary file matches` | 0 | The match is not printed. With `-a` added, the probe printed `feed cat` |

The work proposes no Claude Code mechanism: the launch, the review, and the pull request follow
the `building-from-specs` skill as written. No assumption is shared between tasks, because there
is one task.

## Files

The file list comes from six searches of the tracked files, run as `git grep -n -F -e <text>` with
`brief.md` left out.

| Search | Hits | Where |
| --- | --- | --- |
| `usage` | 4 | `bin/notes:7`; `tests/run.sh:12`, `:13`, `:15` |
| `notes list` | 4 | `README.md:4`; `bin/notes:7`; `tests/run.sh:7`, `:10` |
| `notes add` | 3 | `README.md:3`; `bin/notes:7`; `tests/run.sh:7` |
| `test_` | 5 | `tests/run.sh:2`, `:6`, `:9`, `:12`, `:15` |
| `search` | 0 | Nothing uses the name today |
| `NOTES_FILE` | 4 | `README.md:3`; `bin/notes:3`; `tests/run.sh:7`, `:10` |

Every hit is in one of three files, and the task changes all three. `scripts/gate.sh` had no hit
and needs no change, because it only runs `tests/run.sh`.

- `bin/notes`: line 7 holds the usage line and the `case` that gains the new arm. Line 3, which
  finds the file, stays as it is.
- `tests/run.sh`: gains the search tests. Line 15 is a `for` loop that names each test by hand,
  although the comment on line 2 says the script runs every `test_*` function. A test that is
  defined and not added to that loop never runs, and the gate still passes. The task adds each new
  name to the loop and does not replace the loop (call 9). `test_usage`, on lines 12 and 13,
  checks only the first word of the usage line, and the task makes it compare the whole line.
- `README.md`: lines 3 and 4 describe each command the tool has (call 1).

## Commands and the denials log

`.workstation/denials.log` holds three refusals in the last 30 days: a force push to `main`, an
`rm -rf` outside the working folder, and a web fetch from an unknown host. The task runs
`bin/notes`, the gate, `mktemp`, git commands on its own branch, the pull request commands that
the skill owns, and one review dispatch, and none of these matches a refusal. A test removes a
temporary file with `rm -f` on that one file and a temporary directory with `rmdir`, never with
`rm -rf`. The session has no page to fetch, because the `grep` behavior it rests on is quoted
above.

## The task: notes-search

The task changes `bin/notes`, `tests/run.sh`, and `README.md`. It waits for no other task, so the
merge order is this one pull request. `standards:diff-reviewer` reviews it. It touches no sign-in
or data path and renders no UI, so no other reviewer reads it. The task session runs on `opus` at
`high`.

### Goal

Items 1 to 10 share this setup, run from the repo's root:

```bash
f=$(mktemp); g=$(mktemp); d=$(mktemp -d)
printf '%s\n' 'buy rope' 'feed cat' 'Call ROPE shop' 'coil the ropes' 'a.c' 'abc' 'x -v y' > "$f"
printf 'feed cat\nodd\0note\n' > "$g"
export NOTES_FILE=$f
```

1. `bin/notes search Rope` prints `buy rope`, `Call ROPE shop`, and `coil the ropes`, in that
   order and nothing else, and exits 0.
2. `bin/notes search a.c` prints `a.c` and nothing else, and exits 0.
3. `bin/notes search -v` prints `x -v y` and nothing else, and exits 0.
4. `bin/notes search zebra 2>&1` prints nothing and exits 1.
5. `NOTES_FILE=$f.gone bin/notes search rope 2>&1` prints nothing and exits 1.
6. `bin/notes search $'zebra\ncat' 2>&1` prints nothing and exits 1.
7. `NOTES_FILE=$g bin/notes search cat 2>&1` prints `feed cat` and nothing else, and exits 0.
8. `NOTES_FILE=$d bin/notes search rope 2>/dev/null` prints nothing and exits 2, and
   `NOTES_FILE=$d bin/notes search rope 2>&1 | grep -c -F 'usage:'` prints 0.
9. `bin/notes search`, `bin/notes search ""`, and `bin/notes search buy rope` each exit 2. With
   `2>&1 >/dev/null` each prints exactly `usage: notes add <text> | notes list | notes search <word>`,
   and with `2>/dev/null` each prints nothing.
10. `bin/notes bogus 2>&1 >/dev/null` prints that same usage line, and the command exits 2.
11. On the branch's last commit, `bash scripts/gate.sh` exits 0 and prints `ok   test_add_then_list`,
    `ok   test_list_empty`, and `ok   test_usage`, and `bash scripts/gate.sh | grep -c '^FAIL'`
    prints 0. `bash scripts/gate.sh | grep -c '^ok   test_search_'` and
    `grep -c '^test_search_' tests/run.sh` print the same number, and it is 9 or more.
12. `tests/run.sh` holds at least one `test_search_` test for each of items 1 to 9, each defined
    at the start of a line as today's tests are, and `test_usage` fails unless `bin/notes bogus`
    prints the whole usage line of item 9. The reviewer reads the tests against the items.
13. `grep -c -F 'notes search' README.md` prints 1 or more, and the README's first paragraph says
    in one sentence that `bin/notes search <word>` prints each note that contains the word,
    ignoring case, oldest first, and exits 1 when no note does. The reviewer reads the sentence.
14. `git diff --name-only main...HEAD` prints `README.md`, `bin/notes`, and `tests/run.sh`, and
    nothing else.

The README sentence follows the Federal Plain Language Guidelines. The `writing-voice` skill gives
that standard for a README in a shell repo, which is a narrower rule than the "developer docs
follow Google" line in `CLAUDE.md`.

Each test that reads or writes notes sets `NOTES_FILE` to a `mktemp` path, as the tests do today,
so that no test reads or changes the real `~/.notes`. The reviewer checks this by reading.

The repo runs no CI on pull requests (`.workstation/remote.txt`), so the gate run in item 11 is
the only full run, and the pull request quotes it from the last commit.

### The checks on today's code

Every command in items 1 to 11, 13, and 14 was run twice on 2026-11-22 at `399e8de`, with the same
result both times.

| Item | Today's result | Fails today? |
| --- | --- | --- |
| 1 to 7 | Each prints `usage: notes add <text> \| notes list` and exits 2 | Yes: there is no `search` |
| 8 | Nothing and exit 2, but the count is 1 | Yes: the error is the usage line |
| 9 and 10 | Exit 2 and nothing on standard output, with the old usage line | Yes: the line doesn't name `search` |
| 11 | Exit 0, the three `ok` lines, `FAIL` count 0, and both `test_search_` counts 0 | Yes: 0 is fewer than 9 |
| 12 | No `test_search_` test exists, and `test_usage` reads one word | Yes, by reading |
| 13 | Prints 0 | Yes |
| 14 | Prints nothing on `main` | Can't be judged until the branch exists |

Items 1 to 10 can all be met at once. The same commands, run twice against a throwaway copy of
`bin/notes` outside the repo with the pick and its guards applied, printed what the items say.
The task session writes its own code.

### Minutes

The task is planned at 45 minutes, so its goal's time clause is 90 minutes. `task-report` lists
three tasks here since 2026-11-01. Two are like this one, a change to a command with its tests:
pull request 12, "Add notes list", took 34 minutes with no fix round, and pull request 18, "Let
notes add read stdin", took 41 with one. This task has more cases than either, so the plan sits
just above the longer one. Pull request 15, a test alone, took 12 and is not a like task. Nothing
the task drives adds a wait: there is no CI, no timer, and no idle limit.

### Before the launch

The launch checks belong to the launching session, under "Launching a task" in the skill. Three
facts bear on them.

- The remote's `main` may not be `399e8de`. This copy of the repo has no `origin/main` ref and one
  commit, and nothing here could reach the remote. `task-report` lists pull request 18, "Let notes
  add read stdin", yet `add` at `399e8de` reads only its arguments. The report measures a task up
  to ready, so it does not show that pull request 18 merged. The launching session confirms that
  the remote's `main` is still `399e8de`. If it has moved, the checks above are run again on the
  new commit first, and a usage line there that differs from today's sends this spec back to Geoff.
- This spec is not committed, and a task's worktree starts from the remote's `main`, so `spec.md`
  won't be in it. The goal names the spec by its absolute path in the main checkout, and the task
  session and its reviewer read it there. Item 14 keeps it out of the pull request.
- `claude agents --json` printed `[]` on 2026-11-22. It ran inside this session's sandbox, so it
  may not show every session on the workstation. The worktree check was not run, because its
  command is not installed where this spec was written. The task needs no secret. The remote is
  public, and its default branch is `main`.

## Backlog

The scoped sweep of `standards:backlog-sweep` had nothing to read: the repo tracks five files and
none is a backlog. There are no verdicts, and approving this spec approves no backlog edit.

## Calls Claude made

Calls 1 to 6 are scope and product calls. The rest are method calls.

1. The README is in the task. The brief says the work changes `bin/notes` and `tests/run.sh`, and
   the file search found that `README.md` describes every command. Passed over: leaving the README
   alone, as the brief's words read. To reverse, strike item 13 and take `README.md` out of item
   14 before approval.
2. A search that finds a note exits 0. The brief gives only the 1 and the 2.
3. A missing notes file is "no match": silence and exit 1, because `list` already treats it as no
   notes. Passed over: an error and exit 2, which would make a first search on a new machine look
   like a mistake. Reversing removes one guard and one test.
4. An empty word is a missing word. Passed over: printing every note, which is what `list` does.
5. More than one argument after `search` is a usage error. Passed over: joining the arguments with
   spaces, as `add` does. `search buy rope` could mean the phrase, both words, or either word, and
   the brief settles one word. An error can become a behavior later without breaking anyone's use,
   and the reverse isn't true. Reversing changes one condition and one test.
6. The usage line's exact text is today's line with ` | notes search <word>` added. "Contains"
   means anywhere in the note, never whole words only.
7. A word with a newline in it finds nothing. A note is one line, so none can contain it. Passed
   over: `grep -F`'s reading, which finds notes holding either half.
8. A path that exists and can't be read as a file is an error with exit 2, tested with a directory.
   A file without read permission behaves the same way and has no test, because that test passes
   wrongly when run as root.
9. The task adds its tests to the hand-named loop in `tests/run.sh` and leaves the loop in place.
   Passed over: making the script find its tests, which is work beyond the brief. The pull request
   names the mismatch between the loop and the comment on line 2.
10. A note that holds a NUL byte doesn't hide the other notes from a search, which is why the pick
    carries `-a`. Case folding follows the user's locale, and no locale is forced.
11. `grep -a -i -F -e` is the pick, and the task session may leave it for a recorded reason.
12. The task session runs on `opus` at `high`. The skill names no model for a build, and the
    session makes its own calls unattended, which is judgment work.
13. The plan is 45 minutes, from the two like tasks in `task-report`.
14. Item 14 compares against `main`, since this copy has no `origin/main` ref, and the goal names
    the spec by absolute path, since the spec is uncommitted.
15. The fresh reader's question about whether `399e8de` is the remote's `main` could not be put to
    Geoff. It became the first launch condition under [Before the launch](#before-the-launch).
