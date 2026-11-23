# Spec: notes search

`bin/notes search <word>` prints every note that contains the word. The design is `brief.md`, built as one task
that ends in one pull request. Two points need Geoff's eye at approval: the spec departs from the brief on the
README, next, and its start conditions couldn't be tested from the session that wrote it (see Launch).

## The brief and the README disagree

The brief says "No match prints nothing and exits 1." `README.md:10-11` says "Every command exits 0 when it
runs, even when it prints nothing, and 2 on a usage error. Scripts that call `notes` rely on that." Both can't
hold.

The spec keeps the brief's exit 1. It is Geoff's ruling on this command, where the README states a general rule
and describes only `add` and `list`. No script written before this work can call `search`, so every caller of
`add` and `list` sees what it saw before. The README then has to state the exception, so the task changes three
files where the brief named two: `README.md` joins `bin/notes` and `tests/run.sh`.

To reverse this, make `search` exit 0 after no match, keep the README's exit-code paragraph as it is today, and
change done items 3 and 6 to match.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The non-goals are patterns, whole-word matching, a search for several words, any new flag, any change to what
`add` or `list` do, and any change to how `tests/run.sh` finds its tests.

The work fails if a word is read as a pattern or an option, if `add` or `list` change their output or exit
status, if a test reads or writes the real `~/.notes`, or if the README still says every command exits 0.

## Behaviour

The brief settles what the first two rows print, the exit 1, and the missing word. Exit 0 after a match follows
the README. The rest are Claude's calls, listed at the end.

| Call | Standard output | Standard error | Exit |
| --- | --- | --- | --- |
| One word, and at least one note contains it | Each matching note, whole, in file order | Nothing | 0 |
| One word, and no note contains it | Nothing | Nothing | 1 |
| One word, and the notes file doesn't exist | Nothing | Nothing | 1 |
| No word, an empty word, or more than one word | Nothing | The usage line | 2 |

A note is one line of `$NOTES_FILE`. It matches when the word appears anywhere in it, so `rope` finds
`ropes`. Case is ignored. Every character of the word is literal, including `.`, `*`, `[`, `\`, and a leading
`-`. File order is oldest first, because `add` appends.

The usage line becomes this, for every usage error in the tool:

```
usage: notes add <text> | notes list | notes search <word>
```

Three cases are outside this work, and no done item covers them. A notes file that exists and can't be read
passes the read's own message and exit status through. A word that holds a newline does whatever `grep` does
with it. Case folding beyond ASCII follows the caller's locale, and the tests use ASCII.

Nothing is capped: not the file's size, the word's length, or the count of matches.

## Approach

1. `grep -iF -- "$word" "$file"`, behind the same `[ -f "$file" ]` test that `list` uses. One line, and its exit
   status already is the brief's 0 and 1. This is the pick.
2. A bash loop over the file that tests `[[ ${line,,} == *"${word,,}"* ]]`. It runs no other program, and it
   takes a loop to do what two `grep` flags do.
3. `awk` with `index(tolower($0), tolower(word))`. The word has to arrive through `ENVIRON`, because `-v`
   rewrites its backslashes.

Option 1 is documented, in GNU grep 3.12 on this workstation. `grep --help` says "-F, --fixed-strings PATTERNS
are strings" and "-i, --ignore-case ignore case distinctions in patterns and data". `man grep` says "the exit
status is 0 if a line is selected, 1 if no lines were selected, and 2 if an error occurred." Options 2 and 3 are
assembled from documented pieces and rest on probes. The loop printed only `a.c` for the word `A.C`.
`awk -v w='a\.c' 'BEGIN{print w}'` printed `a.c` with a warning, where `ENVIRON` kept `a\.c`.

One probe carries a decision. `grep -iF -- rope "$f.gone"`, on a file that doesn't exist, printed
`grep: ...gone: No such file or directory` and exited 2, which is the usage status. So the script tests for the
file before it runs `grep`.

No assumption spans tasks, because there is one task.

## Files

The searches ran with `git grep` over the five tracked files, before `spec.md` existed.

- `git grep -n usage`: 6 hits. `bin/notes:7` changes (the usage line). `README.md:10` changes. `tests/run.sh:15`
  changes (the loop). `tests/run.sh:12` and `:13` stay: `test_usage` checks only the first word and still
  passes. `brief.md:9` is this spec's source.
- `git grep -n -e 'notes list' -e 'notes add'`: 5 hits. `README.md:3` and `:4` change (the paragraph gains
  `search`). `bin/notes:7` is listed above. `tests/run.sh:7` and `:10` stay.
- `git grep -n exit -- . ':!brief.md'`: 4 hits. `README.md:10` and `bin/notes:7` are listed above.
  `tests/run.sh:2` and `:18` stay.
- `git grep -n test_`: 5 hits, all in `tests/run.sh`. Line 15 changes. Lines 6, 9, and 12 stay. Line 2 is a
  comment that says the file "Runs every test_* function", but line 15 names each test, so a test left out of
  that loop never runs. The comment stays as it is.

`scripts/gate.sh` appears in no search and doesn't change.

## Commands and the denials log

`.workstation/denials.log` holds three refusals in the last 30 days (2026-10-23 to 2026-11-22): a force push to
`main`, `rm -rf` on a path outside the working folder, and a WebFetch to an unknown host.

The task runs `bash scripts/gate.sh`, `bin/notes`, `grep`, `mktemp`, `printf`, `rm -f` on one temp file,
`git add` by file name, `git commit`, a push of its own branch, and the pull request steps that
`building-from-specs` owns. None of them matches a refusal. Three rules keep it that way: never force a push,
never use `rm -rf` on a temp path (`mktemp` files live outside the working folder, and `rm -f` on one of them
ran today inside the gate), and fetch nothing from the web (`man grep` is local).

## Task: notes-search

The task waits for no other task, and its pull request is the only merge.

### Goal

Items 1 to 4 use this fixture, and each command was run today on commit `745419b`:

```bash
f=$(mktemp); printf '%s\n' 'buy rope' 'Call ROPE shop' 'a.c' 'abc' 'use -v flag' > "$f"
```

Today every command in items 1 to 4 prints `usage: notes add <text> | notes list` and then `exit 2`.

1. Search prints the matching notes, oldest first, whatever their case.
   `NOTES_FILE=$f bin/notes search rope; echo "exit $?"`
   Done: it prints `buy rope`, `Call ROPE shop`, `exit 0`, in that order.
2. The word is plain text.
   `NOTES_FILE=$f bin/notes search a.c; echo "exit $?"` and `NOTES_FILE=$f bin/notes search -v; echo "exit $?"`
   Done: the first prints `a.c`, `exit 0` and never `abc`. The second prints `use -v flag`, `exit 0`.
3. No match prints nothing and exits 1, and so does a missing notes file.
   `NOTES_FILE=$f bin/notes search zebra 2>&1; echo "exit $?"` and
   `NOTES_FILE=$f.gone bin/notes search rope 2>&1; echo "exit $?"`
   Done: each prints only `exit 1`.
4. A missing word, an empty word, and a second word each print the new usage line on standard error and exit 2.
   `NOTES_FILE=$f bin/notes search; echo "exit $?"`, then the same with `search ""`, then with
   `search buy rope`.
   Done: each prints `usage: notes add <text> | notes list | notes search <word>`, then `exit 2`. With
   `2>/dev/null` before the semicolon, each prints only `exit 2`, as it does today.
5. The tests cover items 1 to 4, and the gate passes on the branch's last commit.
   `bash scripts/gate.sh; echo "exit $?"`
   Today: `ok   test_add_then_list`, `ok   test_list_empty`, `ok   test_usage`, `exit 0`.
   Done: those three lines, then `ok   test_search_matches` (item 1), `ok   test_search_plain_text` (item 2),
   `ok   test_search_no_match` (item 3), `ok   test_search_usage` (item 4), no `FAIL` line, and `exit 0`. Each
   new test asserts its item's output and exit status. Each sets `NOTES_FILE` to a `mktemp` file, or to a
   `mktemp` path removed with `rm -f` as `test_list_empty` does.
6. The README describes `search` and no longer says every command exits 0.
   `grep -c 'Every command exits 0' README.md` and `grep -n -e search -e exit README.md`
   Today: the first prints `1`. The second prints one line,
   `10:Every command exits 0 when it runs, even when it prints nothing, and 2 on a usage error.`
   Done: the first prints `0`. The second prints the `search` sentence in the first paragraph and the three
   lines of the exit-code paragraph under Files.
7. One pull request to `main` on `example/notes` is ready, by "Gates and review" and "The pull request" in
   `building-from-specs`. Its body quotes item 5's output from the branch's last commit. The repo runs no CI
   on pull requests (`.workstation/remote.txt`), so that run is the only full one and nothing waits on CI.

### Files

- `bin/notes`: the `search` branch and the usage line.
- `tests/run.sh`: the four tests named in item 5, each added to the loop on line 15.
- `README.md`: the first paragraph gains one sentence saying that `bin/notes search <word>` prints the notes
  that contain the word, ignoring case, oldest first. The last paragraph becomes the text below. The README
  follows `~/.claude/docs/voice/written-for-people.md`, which the `writing-voice` skill names for a README in a
  shell repo.

```
`add` and `list` exit 0 when they run, even when they print nothing. Scripts that call `notes`
rely on that. `search` exits 0 when it prints a note and 1 when no note matches. Every command
exits 2 on a usage error.
```

### Reviewers

`standards:diff-reviewer` reads the branch. The work has no sign-in path, no stored-data change, and no rendered
UI, so no second reviewer reads it.

### Minutes

40 minutes, so the goal's time clause is `or stop after 80 minutes`. `task-report --since 2026-11-01` gives
three tasks in this repo. The two that changed a command are the like ones: "Add notes list" measured 34
minutes against 30 planned, and "Let notes add read stdin" measured 41 against 30 with one fix round. "Add the
usage test" measured 12 and changed only a test. The task drives no timer or idle limit, so no wait is added.

### Launch

"Launching a task" in `building-from-specs` owns the command and the four checks. Three facts for it:

- The task's worktree starts from the remote's `main`, and `spec.md` is uncommitted today. The launching session
  commits `spec.md` to `main` and pushes it first, or the task session can't read its own spec. The commit goes
  directly, as a record does under "Records", and approving this spec approves it.
- The task needs no secret.
- `claude-worktree-busy` isn't on this session's path, and `claude agents` wasn't run from it, so the start
  conditions weren't tested against today's sessions. The launching session runs both.

## Backlog sweep

The scoped sweep found no items. `git ls-files` lists `README.md`, `bin/notes`, `brief.md`, `scripts/gate.sh`,
and `tests/run.sh`, none of them a backlog, and `git grep -il -e backlog -e todo` has 0 hits.

## Calls Claude made

Product calls:

1. Exit 1 after no match stands against `README.md:10-11`, and `README.md` joins the two files the brief named.
2. The word matches anywhere in a note, never only as a whole word.
3. A missing notes file counts as no match, as `list` already prints nothing for one.
4. No match prints nothing on standard error as well as standard output.
5. An empty word counts as a missing word, because `search ""` would otherwise print every note.
6. A second word is a usage error, because turning an error into a phrase search later breaks no caller.
7. The usage line's exact text.
8. The README's exact exit-code paragraph, and "ignoring case" in its new first-paragraph sentence.
9. An unreadable notes file, a word with a newline, and case folding beyond ASCII stay outside the work.
10. `spec.md` goes to `main` directly before the launch, with no pull request.

Method calls:

11. `grep -iF --` over a bash loop or `awk`.
12. Four named tests join the existing loop, and the comment on `tests/run.sh:2` stays.
13. 40 minutes, from the two like tasks.
14. `standards:diff-reviewer` alone.
