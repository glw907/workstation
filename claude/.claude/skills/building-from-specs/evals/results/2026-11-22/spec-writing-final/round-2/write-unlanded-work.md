# Spec: notes search

`bin/notes search <word>` prints every note that contains a word. The work is one task that ends in one pull
request, planned at 40 minutes. One point of the brief can't be built as written, and it is the one thing here
that needs Geoff's eye: `notes export`, whose format search was to copy, isn't on `main`. This spec has search
print each note the way `notes list` prints it. Approving the spec approves that call. If export work exists
somewhere this checkout can't see, the other answer is to name it and have this task wait until it merges. The
next section gives the evidence and what reversing costs.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is the command the brief settled. `bin/notes search <word>` prints each note that contains the word,
oldest first. The match ignores case and treats the word as plain text. No match prints nothing and exits 1. A
missing word exits 2 with a usage line that names the new command.

The work doesn't add patterns, whole-word matching, or a search for several words at once. It doesn't add
`notes export`, change `add` or `list`, or edit `README.md`. It adds no service, release, dependency, or setting.

The work fails if any of these is true after the merge:

- Search reads the word as a pattern or as an option.
- Search prints a note differently from `list`.
- A script can't tell "no match" from "wrong use" by the exit status.
- A search test is defined but never runs.
- A test reads or writes `~/.notes`.

## `notes export` isn't on main

The brief says "Each match prints in the format `notes export` uses, so scripts can read both the same way."
No such command exists in this checkout. `git grep -n -i export` has one hit, the brief's own line 9, and
`git grep -c export main -- bin/notes` prints nothing and exits 1. The repo holds one commit, one branch, no
stash, and no remote-tracking ref. GitHub refused both `git ls-remote origin` and `gh pr list` from the session
that wrote this spec, so an export branch or pull request on `origin` could not be ruled in or out.

A task starts from the default branch and never from unmerged work, so search can't copy a format that isn't
there, and no done item can compare against it. Search therefore prints each matching note as the stored line,
byte for byte, which is what `list` prints. It is the only print format on `main`, and scripts can read `list`
and `search` the same way.

The option passed over is to hold this task until export merges. It was passed over because nothing in reach
shows that export work exists, and the wait would have no end that a session could see. Reversing the call
changes one print line in `bin/notes` and the expected strings in the search tests. A script written against
search's output in the meantime would have to change too.

The call holds only while export is absent from `origin`, merged or not. The launch checks under the task
cover that.

`task-report` also lists pull request 18, "Let notes add read stdin", and `add` on this checkout ignores stdin:
`echo piped | NOTES_FILE=$g bin/notes add` stores an empty line. So pull request 18 is unmerged, or this
checkout is behind `origin`, and the refused fetch would have told them apart. It matters, because the usage
line, the line numbers, and every "today" output below were read at `e3473df`. The launch checks stop the task
if `origin`'s `main` is some other commit.

The work is one task, so no assumption is shared between tasks.

## Approach

Three ways to match were probed on 2026-11-22 against a file that holds `buy rope`, `call the ROPE shop`,
`a.c`, `abc`, `tar -c flag`, and `a\.c`.

| Option | Label | Trade-off |
| --- | --- | --- |
| `grep -iF -- "$word" "$file"` | Documented | One line. Its exit status is already 0 on a match and 1 on none. A missing file exits 2, so the command handles that case itself. |
| A `while read -r` loop that compares `${line,,}` with `*"${word,,}"*` | Probed in bash 5.3.9, no source quoted | It printed the right lines for `Rope`. It needs its own exit status and is five lines where grep is one. |
| `awk -v w="$word" 'index(tolower($0), tolower(w))'` | Probed in GNU Awk 5.3.2, and wrong here | For the word `a\.c` it warned "escape sequence `\.' treated as plain `.'" and printed `a.c`. `-v` rewrites backslashes, so the word isn't plain text. |

The pick is grep. Its label rests on `grep --help` from GNU grep 3.12 on this machine, which says
"`-F, --fixed-strings  PATTERNS are strings`" and "`-i, --ignore-case  ignore case distinctions in patterns and
data`", and on these runs:

| Command | Printed | Exit |
| --- | --- | --- |
| `grep -iF -- Rope "$f"` | `buy rope`, `call the ROPE shop` | 0 |
| `grep -iF -- a.c "$f"` | `a.c` | 0 |
| `grep -iF -- 'a\.c' "$f"` | `a\.c` | 0 |
| `grep -iF -- -c "$f"` | `tar -c flag` | 0 |
| `grep -iF -- zebra "$f"` | nothing | 1 |
| `grep -iF -- rope "$f.gone"` | `grep: …: No such file or directory` | 2 |

The `--` matters. Without it grep reads a word such as `-c` as an option, takes the file's path as the pattern,
and waits on stdin.

## When it goes wrong

| Case | stdout | stderr | Exit |
| --- | --- | --- | --- |
| One or more notes match | The matching lines, in file order | Nothing | 0 |
| No note matches | Nothing | Nothing | 1 |
| The notes file doesn't exist | Nothing | Nothing | 1 |
| No word, an empty word, or more than one argument after `search` | Nothing | The usage line | 2 |

The usage line is `usage: notes add <text> | notes list | notes search <word>`. A phrase in quotes is one
argument, so `notes search "buy rope"` searches for that text.

A notes file that exists and can't be read is outside this work: grep's message and status pass through, as
cat's do for `list`. Case matching beyond ASCII follows the locale, and the goal tests ASCII only. The work
sets no limit on size, count, or time. grep reads the file once.

## Files

Two searches, run at `e3473df`, give the list.

`git grep -n -e usage -e 'notes list' -e 'list)'` has 9 hits in 4 files.

- `bin/notes:6` is the `list` branch. The `search` branch goes beside it.
- `bin/notes:7` is the usage line. It changes.
- `tests/run.sh:7` and `:10` are the two `list` tests. They stay as they are.
- `tests/run.sh:12` and `:13` are `test_usage`. It checks only that the first word is `usage:`, so it stays and
  still passes.
- `tests/run.sh:15` is the loop that names each test. It changes.
- `README.md:4` describes `list`. Dismissed: the brief names the two files the work changes.
- `brief.md:10` is the brief. Dismissed.

`git grep -n 'test_'` has 5 hits, all in `tests/run.sh`. Line 2's comment says the script "Runs every test_*
function", but line 15 runs only the three it names. A new test that isn't added to line 15 never runs, and the
gate still passes.

The task changes `bin/notes` and `tests/run.sh` and no other file. `scripts/gate.sh` runs `tests/run.sh` and
needs no change.

## Commands and the denials log

The task runs `bin/notes`, `bash scripts/gate.sh`, `mktemp`, `git diff`, `git add` by file name, `git commit`,
a push of its own branch, and the `gh` commands that the skill's "The pull request" section owns. The launch
adds `git fetch`, `git rev-parse`, `git ls-remote`, and `gh pr list`.

The denials log holds three refusals in the last 30 days: a force push to `main` on 2026-11-03, `rm -rf
~/.notes.bak` on 2026-11-09, and a fetch of `example.invalid` on 2026-11-17. The task pushes only its own
branch and never with force, removes nothing outside the working folder with a recursive delete, and fetches
no web page. None of its commands matches a refusal.

The repo has no backlog file (`git ls-files` lists `README.md`, `bin/notes`, `brief.md`, `scripts/gate.sh`,
and `tests/run.sh`), so the scoped backlog sweep has no item to judge and no full sweep is due.

## Task: add notes search

The task waits for nothing, and with one pull request there is no merge order. It doesn't wait for export.

### Launch

The session Geoff is talking to launches the task by "Launching a task" in `building-from-specs`, on Opus at
high. The four checks there could not run from the session that wrote this spec, where `claude-worktree-busy`
isn't installed and GitHub is refused, so they run at launch. The task needs no secret and no CI:
`.workstation/remote.txt` shows the repo is public and runs no CI on pull requests.

Two checks are added, because this spec was probed at one commit and could not see `origin`.

1. After `git fetch origin`, `git rev-parse origin/main` prints `e3473dfd0df8477c17ae3d3d7cfb7060ad708a35`.
   `git rev-parse main` prints that here today.
2. No branch and no open pull request on `origin` carries export. `git ls-remote origin` and
   `gh pr list --repo example/notes --state all` show them, and GitHub refused both here.

If either check fails, the session doesn't launch. It brings what it found to Geoff, because the format call
or the probed strings are stale.

`spec.md` is uncommitted, so a fresh worktree doesn't hold it. The goal names the absolute path of `spec.md`
in the main checkout, and the task session and its reviewer read it there.

### Goal

Items 1 to 8 share one notes file, and each command runs from the repo root:

```bash
f=$(mktemp); printf '%s\n' 'call the ROPE shop' 'buy rope' 'feed cat' 'a.c' 'abc' 'a\.c' 'tar -c flag' > "$f"
```

Today, at `e3473df`, every command in items 1 to 8 prints `usage: notes add <text> | notes list` and then
`exit 2`, once for each `bin/notes` call, because `search` falls through to the usage branch.

1. Search ignores case and prints each matching note as stored, oldest first.
   `NOTES_FILE=$f bin/notes search Rope; echo "exit $?"`
   Holds when it prints `call the ROPE shop`, `buy rope`, `exit 0`, in that order.
2. The word is plain text, never a pattern.
   `NOTES_FILE=$f bin/notes search a.c; echo "exit $?"`
   Holds when it prints `a.c`, `exit 0`, and neither `abc` nor `a\.c`.
3. A backslash in the word is text.
   `NOTES_FILE=$f bin/notes search 'a\.c'; echo "exit $?"`
   Holds when it prints `a\.c`, `exit 0`, and not `a.c`.
4. A word that starts with a dash is text, never an option.
   `NOTES_FILE=$f bin/notes search -c </dev/null; echo "exit $?"`
   Holds when it prints `tar -c flag`, `exit 0`.
5. No match prints nothing and exits 1.
   `NOTES_FILE=$f bin/notes search zebra; echo "exit $?"`
   Holds when it prints only `exit 1`.
6. A notes file that doesn't exist is no match.
   `NOTES_FILE=$f.gone bin/notes search rope; echo "exit $?"`
   Holds when it prints only `exit 1`.
7. A missing word exits 2 with the usage line on stderr, and the line names the new command.
   `NOTES_FILE=$f bin/notes search 2>&1 >/dev/null; echo "exit $?"`
   Holds when it prints `usage: notes add <text> | notes list | notes search <word>`, `exit 2`.
8. An empty word and a second argument are wrong use.
   `NOTES_FILE=$f bin/notes search '' 2>&1 >/dev/null; echo "exit $?"; NOTES_FILE=$f bin/notes search buy rope 2>&1 >/dev/null; echo "exit $?"`
   Holds when it prints the usage line of item 7 and `exit 2`, twice.
9. The gate passes on the branch's last commit and runs one test for each of items 1 to 8.
   `bash scripts/gate.sh; echo "exit $?"`
   Today it prints `ok   test_add_then_list`, `ok   test_list_empty`, `ok   test_usage`, `exit 0`.
   Holds when it prints those three lines, an `ok` line for each test named under "Rules for the build", no
   line that starts `FAIL`, and `exit 0`. The repo runs no CI on pull requests, so this run is the only full
   run, and the pull request quotes its output with the commit it ran on.
10. The branch changes `bin/notes` and `tests/run.sh` and nothing else.
    `git diff --name-only origin/main...HEAD`
    Today the same command against `main` prints nothing, and this checkout has no `origin/main` ref to run it
    against. Holds when it prints `bin/notes` and `tests/run.sh` and no other line.
11. The work is one pull request to `main` on `example/notes`, written by "The pull request" in
    `building-from-specs` and marked ready only after item 9 holds and the review by "Gates and review" is
    done. The pull request's page shows it, and its body names the commit the review read.

### Rules for the build

The task adds eight tests, one for each of items 1 to 8 in order: `test_search_ignores_case`,
`test_search_plain_text`, `test_search_backslash`, `test_search_dash_word`, `test_search_no_match`,
`test_search_missing_file`, `test_search_usage`, and `test_search_wrong_use`. Each test checks its item's
output and its exit status, and each name is added to the loop on `tests/run.sh:15`.

Each new test sets `NOTES_FILE` to a `mktemp` path, and no test reads or writes `~/.notes`. The test for item
4 gives `bin/notes` its stdin from `/dev/null`, so a build that drops the `--` fails at once instead of waiting
on stdin until the time clause.

### Files, reviewer, minutes

The files are `bin/notes` and `tests/run.sh`.

`standards:diff-reviewer` reads the branch, on Opus at high. The work has no sign-in or data path and no
rendered UI, so no second reviewer reads it.

The task is planned at 40 minutes. `task-report` measures the two like tasks, each of which changed one
command in `bin/notes` with its tests: "Add notes list" took 34 minutes with no fix round, and "Let notes add
read stdin" took 41 with one. Their mean is 37.5, and search carries more tests than either. "Add the usage
test" took 12 minutes and changed tests only, so it isn't a like task. Nothing adds a wait: no CI runs, and the
gate ran in 0.015 seconds today. The goal's time clause is `or stop after 80 minutes`.

## Calls Claude made

1. Search prints each match as the stored line, as `list` does, because `notes export` isn't on `main`. Waiting
   for export was passed over. Reversing changes one print line, the tests' expected strings, and any script
   written against search in the meantime.
2. The launching session checks that `origin`'s `main` is still `e3473df` and that no branch or open pull
   request there carries export, and takes what it finds back to Geoff if either fails.
3. "Contains the word" means the text appears anywhere in the note, so `rope` finds `ropes`. Whole-word
   matching was passed over.
4. A notes file that doesn't exist is no match: nothing printed, exit 1. This follows `list`, which prints
   nothing for a missing file.
5. An empty word exits 2 with the usage line, because an empty text matches every note.
6. More than one argument after `search` exits 2. Joining the arguments as `add` does was passed over, because
   loosening this later breaks no script and tightening it later would.
7. The usage line reads `usage: notes add <text> | notes list | notes search <word>` and stays on stderr.
8. The match is `grep -iF --`, picked over a bash loop and awk for the reasons under "Approach".
9. `README.md` stays as it is, because the brief names the two files. After the merge it describes two of the
   three commands.
10. New tests join the named loop in `tests/run.sh`. Changing the runner to find tests by itself was passed
    over as work the brief doesn't cover.
11. The task is planned at 40 minutes and runs on Opus at high, with `standards:diff-reviewer` on Opus at high.
12. The goal names `spec.md` by its absolute path in the main checkout, because this session was told to commit
    nothing.
