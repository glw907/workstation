# Spec: notes search

Written 2026-11-22 from `brief.md`, against `main` at `e3473df`. Status: waiting for approval, with one question
for Geoff under "Calls Claude made".

This is one task that ends in one pull request. It can't start today: the brief says each match prints "in the
format `notes export` uses", and this checkout has no `notes export`.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

- Goals: the brief's five points about the command, carried as done items 1 to 5.
- Non-goals: adding `export` or changing what it prints, patterns, whole-word matching, search across more than
  one word, any change to `add` or `list`, and any file beyond `bin/notes` and `tests/run.sh`.
- The work fails if search prints a format of its own, so a script needs two parsers; if a character such as
  `.`, `[`, or a leading `-` changes what matches; or if a search test exists and the gate never runs it.

## What the task waits for

The task waits until `notes export` is on `origin/main`. `git grep -c -e export -e search` gives one hit,
`brief.md:4`, and no code. `NOTES_FILE=$g bin/notes export; echo "exit $?"` (fixture under "Goal") prints the
usage line and `exit 2`.

Nothing this session can read names the work that adds `export`. `task-report --since 2026-11-01` lists pull
requests 12, 15, and 18, and none is an export task. The session can't reach the remote, and
`.workstation/remote.txt`, which stands in for it, says nothing about `export`. The checkout holds no `origin`
refs, so `origin/main` may be ahead: `task-report` measures pull request 18, "Let notes add read stdin", and at
`e3473df` `echo x | bin/notes add` stores an empty line.

Before launch, the launching session runs this on `origin/main`:

```bash
NOTES_FILE=$g bin/notes export; echo "exit $?"
```

It launches when the command prints one record for `buy rope`, then one for `coil the ROPE`, then `exit 0`, and
nothing else. A record is what `export` prints for one note. The spec goes back to Geoff, with what `export`
prints, if `export` ignores `$NOTES_FILE`, prints newest first, prints anything that belongs to no note (a
header, an enclosing array), or puts a note's place in the file into its record (a number). In each of those
cases done item 2 can't hold as written.

## Design

Search prints, byte for byte, what `export` prints for a notes file that holds only the matching notes. That is
the whole definition of the format. The code prints each match through the code `export` prints with and keeps
no second copy of the format. Moving that code into a function both commands call is in scope, and the reviewer
reads the diff for a second copy.

| Approach | Trade-off | Verdict |
| --- | --- | --- |
| Select lines of the notes file with `grep -iF -- "$word"`, then print them through `export`'s format code | Needs grep; case folding is grep's | Picked |
| Run `export` and filter its output with grep | Also matches whatever text `export` adds around a note | Rejected |
| A bash loop that compares `${line,,}` with `*"${word,,}"*` | No grep, but hand-rolled matching and one more quoting rule to get wrong | Rejected |

`grep -iF --` is documented. GNU grep 3.12 `--help`: "-F, --fixed-strings PATTERNS are strings" and "-i,
--ignore-case ignore case distinctions in patterns and data". `man grep`: "the exit status is 0 if a line is
selected, 1 if no lines were selected, and 2 if an error occurred." Probes on the fixture: `grep -iF -- a.b "$f"`
printed `a.b` and not `axb`, and `grep -iF -- rope` on a missing file printed an error and exited 2, so the
script handles a missing file itself.

## When it goes wrong

| Case | Standard output | Standard error | Exit |
| --- | --- | --- | --- |
| One or more notes match | The matches, oldest first | Nothing | 0 |
| No note matches, or the notes file doesn't exist | Nothing | Nothing | 1 |
| No word, an empty word, or more than one argument | Nothing | The usage line | 2 |

The task's own limit is its time clause, 90 minutes.

## Files

The searches ran at `e3473df`, and the line numbers are that commit's. The builder reruns them on its own tree,
where `export` adds hits.

- `git grep -n usage`: 5 hits. `bin/notes:7` is the usage line, and it changes. `tests/run.sh:12` and `:13`
  are `test_usage`, which stays as it is: it reads only the first word, `usage:`. `tests/run.sh:15` is the
  `for` list, and it changes. `brief.md:10` is the brief.
- `git grep -n -e 'notes add' -e 'notes list' -e 'notes export' -e 'notes search'`: 8 hits. `bin/notes:7`
  changes. `tests/run.sh:7` and `:10` are the two existing tests, unchanged. `README.md:3` and `:4` name `add`
  and `list` and stay as they are, because the brief limits the work to two files. `brief.md:1`, `:7`, and
  `:9` are the brief.
- `git grep -n test_`: 5 hits, all in `tests/run.sh`. Lines 6, 9, and 12 define the existing tests and line 2
  is a comment. Line 15 is the `for` list that names each test to run. A test left out of that list never
  runs, and the gate still passes.

The repo has no backlog file (`git ls-files` lists `README.md`, `bin/notes`, `brief.md`, `scripts/gate.sh`,
and `tests/run.sh`), so the scoped sweep has no item and no verdict. The work adds no service, secret,
release, or dependency.

## The task: add `notes search`

- Files: `bin/notes`, `tests/run.sh`.
- Waits for: `notes export` on `origin/main`. Merge order: the pull request that adds `export`, then this one.
- Reviewer: `standards:diff-reviewer`. The work has no sign-in or data path and no rendered UI.
- Minutes: 45, and the time clause is 90. `task-report --since 2026-11-01` gives two like tasks: "Add notes
  list" took 34 minutes against 30 planned, and "Let notes add read stdin" took 41 against 30 with one fix
  round. This task also reads `export`'s code. The repo runs no CI on pull requests, so nothing adds a wait.
- Build session: Opus at high effort, launched as `building-from-specs` "Launching a task" says.

### Goal

Each check runs from the repo root after this fixture. "Today" is the output at `e3473df`.

```bash
f=$(mktemp); printf '%s\n' 'buy rope' 'Call Ann' 'coil the ROPE' 'a.b' 'axb' > "$f"
g=$(mktemp); printf '%s\n' 'buy rope' 'coil the ROPE' > "$g"
h=$(mktemp); printf '%s\n' 'a.b' > "$h"
export NOTES_FILE=$f
```

1. Search prints every note that contains the word, in either case, oldest first.
   `bin/notes search rope; echo "exit $?"`
   Today: the usage line, then `exit 2`. Holds: the record for `buy rope`, then the one for `coil the ROPE`,
   then `exit 0`.
2. Each match prints in the format `export` uses.
   `s=$(bin/notes search rope) && e=$(NOTES_FILE=$g bin/notes export) && [ "$s" = "$e" ]; echo "exit $?"`
   Today: the usage line, then `exit 2`. Holds: `exit 0`.
3. The word is plain text, never a pattern.
   `s=$(bin/notes search a.b) && e=$(NOTES_FILE=$h bin/notes export) && [ "$s" = "$e" ]; echo "exit $?"`
   Today: the usage line, then `exit 2`. Holds: `exit 0`.
   `bin/notes search '[' 2>&1 | wc -c; echo "exit ${PIPESTATUS[0]}"`
   Today: `37`, then `exit 2`. Holds: `0`, then `exit 1`.
4. No match prints nothing and exits 1.
   `bin/notes search zebra 2>&1 | wc -c; echo "exit ${PIPESTATUS[0]}"`
   Today: `37`, then `exit 2`. Holds: `0`, then `exit 1`.
5. A missing word exits 2 with the usage line, and the usage line names the new command.
   `bin/notes search 2>&1 >/dev/null | grep -cF 'notes search <word>'; echo "exit ${PIPESTATUS[0]}"`
   Today: `0`, then `exit 2`. Holds: `1`, then `exit 2`.
6. The gate runs six search tests and passes on the branch's last commit.
   `bash scripts/gate.sh | grep -c '^ok   test_search'`
   Today: `0`. Holds: `6`.
   `bash scripts/gate.sh; echo "exit $?"`
   Today: three `ok` lines, then `exit 0`. Holds: an `ok` line for every test, no `FAIL` line, then `exit 0`.
   The pull request quotes this run with the commit it ran on, because the repo has no CI to run it again.

The six tests, each defined in `tests/run.sh` and named in its `for` list:

- `test_search_matches`: done item 1.
- `test_search_ignores_case`: `ROPE` and `Rope` print what `rope` prints.
- `test_search_plain_text`: done item 3. Also, with standard input from `/dev/null`, the word `-x` finds a
  note that holds `-x`.
- `test_search_format`: done item 2.
- `test_search_no_match`: done item 4, and the same result when the notes file doesn't exist.
- `test_search_missing_word`: done item 5, and the same result for an empty word and for two arguments.

## Commands and the denials log

The denials log holds three refusals in the last 30 days: a force push to `main`, `rm -rf` outside the working
folder, and a web fetch of an unknown host. The task runs `bin/notes`, `bash scripts/gate.sh`, and the push and
pull request steps of `building-from-specs` "A session at work", which push only the task's branch and never
force. It fetches nothing from the web. A test makes its files with `mktemp` and leaves them, as today's tests
do, and no test runs `rm -rf`.

The launch checks of `building-from-specs` "Launching a task" were not run: `claude-worktree-busy` isn't on
this session's path. The launching session runs them on the day.

## Calls Claude made

Nobody could answer a question while this spec was written. Geoff can overturn any call at approval.

1. The task waits for `export`, and the spec names no pull request for it because it found none. This is the
   one question only Geoff can answer: which work adds `notes export`? Passed over: printing each match as its
   stored line, which is what `list` prints and would let the task start today, and adding `export` in this
   task. Each changes what the brief settles, so each is Geoff's to choose.
2. "The format `export` uses" means the output of `export` for a file that holds only the matches.
3. "Contains" is a substring match, so `rope` finds `ropes`.
4. Search takes exactly one argument. An empty word or a second argument exits 2 with the usage line. A later
   change can accept more words without breaking a script, and the reverse would break one.
5. A notes file that doesn't exist is no match: nothing printed, exit 1.
6. The usage line gains ` | notes search <word>` at its end, whatever it says on `origin/main` by then.
7. `README.md` keeps naming only `add` and `list`. The pull request lists that under `## For Geoff`.
