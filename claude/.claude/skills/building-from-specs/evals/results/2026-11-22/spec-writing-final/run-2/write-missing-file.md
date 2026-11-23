# Spec: notes search

Written 2026-11-22 from `brief.md`, the design Geoff settled in conversation. One task, one pull request.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal: `bin/notes search <word>` prints every note that contains the word, oldest first. The match ignores
case, and the word is plain text, never a pattern. No match prints nothing and exits 1. A missing word exits 2
with the usage line, which names the new command.

Out of scope: patterns, whole-word matching, several search terms, highlighting, line numbers, completions for
other shells, and any change to what `add` or `list` does. The work adds no service, secret, release, or setting.

The work has failed if a character in the word acts as a pattern, if `add` or `list` behaves differently, if a
test reads or writes `~/.notes`, or if the gate is red on the branch's last commit.

## Design

`search` joins its arguments with single spaces, as `add` joins its text, and matches the result as one string
anywhere in a note. The notes file is already oldest first, so matches print in file order.

| Call | Stdout | Stderr | Exit |
| --- | --- | --- | --- |
| `notes search rope`, and a note contains it | Each matching note, in file order | Nothing | 0 |
| `notes search zzz`, and no note contains it, or no notes file exists | Nothing | Nothing | 1 |
| `notes search` or `notes search ""` | Nothing | The usage line | 2 |

The usage line becomes exactly `usage: notes add <text> | notes list | notes search <word>`.

Three ways to match were weighed, each probed on this machine (GNU grep 3.12, bash 5.3.9) against a file that
holds `Buy rope`, `ROPE bag`, `abc`, `a.c`, and `back\nslash`.

| Approach | Label | Trade-off |
| --- | --- | --- |
| `grep -iF -- "$word" "$file"` | Documented | One call gives the plain-text match, the case rule, and exit 1 on no match. It needs a guard for a missing file, where grep exits 2. This is the pick. |
| A bash loop over `[[ ${line,,} == *"${word,,}"* ]]` | Assembled from documented bash pieces | No outside command, but the loop carries its own exit code and more lines to test. The probe printed `a.c` alone for the word `A.C`. |
| `awk -v w="$word" 'index(tolower($0), tolower(w))'` | Assembled from documented awk pieces | `-v` rewrites a backslash in the word, and awk exits 0 on no match. The probe printed nothing for the word `\n` and exited 0, where grep printed `back\nslash`. |

The grep label rests on `grep --help` ("`-F, --fixed-strings  PATTERNS are strings`", "`-i, --ignore-case  ignore
case distinctions in patterns and data`"), on `man grep` ("the exit status is 0 if a line is selected, 1 if no
lines were selected, and 2 if an error occurred"), and on the probe: `rope` printed `Buy rope` and `ROPE bag` and
exited 0, `a.c` printed `a.c` alone, `zzz` printed nothing and exited 1, and a missing file exited 2 with
`No such file or directory`.

## What goes wrong

- `test_completions_match` reads every `notes <lowercase word>` in `bin/notes` as a command and compares the set
  with `completions/notes.bash`. With the new usage line and the completions file unchanged, a throwaway copy of
  the repo printed `FAIL test_completions_match` and the gate exited 1. With `complete -W "add list search" notes`
  it passed. A comment in `bin/notes` that held "the notes that contain" failed it again, so `bin/notes` carries
  no `notes <lowercase word>` phrase outside the usage line.
- The `for` loop in `tests/run.sh` names each test. A test function left out of that list never runs, and the
  gate still passes.
- For a missing notes file grep exits 2 and prints an error, so `search` checks for the file first and exits 1
  without output.
- The `--` keeps grep from reading a word that starts with `-` as an option. In the throwaway copy,
  `notes search -v` printed `use -v here` and exited 0.
- `$NOTES_FILE` defaults to `~/.notes`, Geoff's real notes. Every call to `bin/notes search`, in a test or a
  check, sets `NOTES_FILE` to a `mktemp` path.
- The repo has no CI. `.workstation/remote.txt`: "The repo runs no CI on pull requests, so the gate on a
  branch's last commit is its only full run." The pull request quotes that run.

The limits are the three exit codes above and the 80-minute time clause. `search` sets no cap on the size of the
file or the count of matches.

## Files

The brief names `bin/notes` and `tests/run.sh`. The searches add two files.

`git grep -n -e 'notes add' -e 'notes list' -e 'add list'` gives 6 hits.

- `bin/notes:7`, the usage line: changes.
- `completions/notes.bash:2`: changes to `complete -W "add list search" notes`.
- `README.md:3` and `README.md:4`, the sentences that describe each command: the paragraph gains one sentence
  at its end, which follows `~/.claude/docs/voice/written-for-people.md`. It reads: "`bin/notes search <word>`
  prints each note that contains the word, ignoring case, and exits 1 when no note does."
- `tests/run.sh:7` and `tests/run.sh:10`, the `add` and `list` tests: stay as they are.

`git grep -n usage` gives 5 hits.

- `bin/notes:7`: the same line as above.
- `tests/run.sh:21`, the test list: gains the four new tests.
- `tests/run.sh:12` and `tests/run.sh:13`, `test_usage`: stay. The test checks only the first word of the line.
- `brief.md:9`: dismissed, the brief itself.

`scripts/gate.sh` has no hit and stays as it is. The task changes `bin/notes`, `tests/run.sh`,
`completions/notes.bash`, and `README.md`, and no other file.

No assumption spans tasks, because there is one task. The repo tracks no backlog file
(`git ls-files | grep -ic -e backlog -e todo -e STATUS` prints 0), so the scoped backlog sweep has no item and no
verdict.

## Commands and the denials log

The task runs the commands in its goal: `bin/notes` with `NOTES_FILE` set, `bash scripts/gate.sh`, two `grep -c`
checks, and one copy of the tree into a `mktemp -d` folder. All of them ran in Claude Code on 2026-11-22 without
a refusal. Its git and pull request steps are the ones `building-from-specs` owns under "A session at work" and
"The pull request". It stages its four files by name.

`.workstation/denials.log` holds three refusals in the last 30 days, and the task does none of them.

- 2026-11-03, `git push --force origin main`: the task pushes only its own branch, with no force flag.
- 2026-11-09, `rm -rf ~/.notes.bak`: the task deletes nothing recursively and nothing under the home folder.
- 2026-11-17, a web fetch to an unknown host: the task fetches nothing.

## Task: Add notes search

- Files: `bin/notes`, `tests/run.sh`, `completions/notes.bash`, `README.md`.
- Reviewer: `standards:diff-reviewer`. `search` only reads the notes file and draws no screen, so no second
  reviewer reads it.
- Minutes: 40. `task-report --since 2026-11-01` shows the two like tasks, each a command change with its
  tests, at 34 minutes (#12, Add notes list) and 41 minutes (#18, Let notes add read stdin, one fix round). #15
  took 12 minutes and was a test alone. No CI, timer, or idle limit adds a wait. The time clause is
  `or stop after 80 minutes`.
- Waits for: nothing. It is the only task, so there is no merge order.
- Launch: by `building-from-specs` "Launching a task", named `notes-search`, on Sonnet at high effort. The
  task needs no secret and no CI. The worktree starts from the remote's `main`, and the session that wrote this
  spec committed nothing. After Geoff approves the spec, the launching session commits `spec.md` to `main` and
  pushes it before the launch, as a record and no product change. The worktree and session checks could not run
  from the session that wrote this spec, so the launching session runs them that day.

### Goal

Items 1 to 8 use this fixture, run from the repo root.

```bash
f=$(mktemp); printf 'Buy rope\nfix sail\nROPE bag\nabc\na.c\nuse -v here\n' > "$f"
```

Every "today" line is the output on commit `d39b696`, run 2026-11-22. For items 1 to 8 that output is
`usage: notes add <text> | notes list` and `exit=2`, so each item gives only what it prints when it holds.

1. Search prints each note that contains the word, oldest first, ignoring case.
   `NOTES_FILE=$f bin/notes search rope; echo "exit=$?"`
   Holds: `Buy rope`, `ROPE bag`, `exit=0`.
2. The word is plain text.
   `NOTES_FILE=$f bin/notes search a.c; echo "exit=$?"`
   Holds: `a.c`, `exit=0`.
3. A word that starts with `-` is plain text too.
   `NOTES_FILE=$f bin/notes search -v < /dev/null; echo "exit=$?"`
   Holds: `use -v here`, `exit=0`.
4. Several arguments match as one phrase.
   `NOTES_FILE=$f bin/notes search rope bag; echo "exit=$?"`
   Holds: `ROPE bag`, `exit=0`.
5. No match prints nothing and exits 1.
   `NOTES_FILE=$f bin/notes search zzz; echo "exit=$?"`
   Holds: `exit=1`.
6. No notes file is no match.
   `NOTES_FILE=$f.none bin/notes search rope; echo "exit=$?"`
   Holds: `exit=1`.
7. A missing word exits 2 with the usage line, which names the new command.
   `NOTES_FILE=$f bin/notes search; echo "exit=$?"`
   Holds: `usage: notes add <text> | notes list | notes search <word>`, `exit=2`.
8. An empty word counts as missing.
   `NOTES_FILE=$f bin/notes search ""; echo "exit=$?"`
   Holds: the same two lines as item 7.
9. The completions offer `search`.
   `grep -c 'complete -W "add list search" notes' completions/notes.bash`
   Today: `0`. Holds: `1`.
10. The README carries the sentence given under "Files".
    `grep -c 'notes search <word>' README.md`
    Today: `0`. Holds: `1`.
11. The gate passes on a clean tree at the branch's last commit and runs the new tests.
    `bash scripts/gate.sh; echo "exit=$?"`
    Today: `ok   test_add_then_list`, `ok   test_list_empty`, `ok   test_usage`, `ok   test_completions_match`,
    `exit=0`. Holds: those four lines, then `ok   test_search_matches`, `ok   test_search_plain_text`,
    `ok   test_search_no_match`, `ok   test_search_usage`, no `FAIL` line, and `exit=0`.
12. Each new test fails against today's `bin/notes`.
    `d=$(mktemp -d); cp -r bin tests completions scripts "$d"/; git show d39b696:bin/notes > "$d/bin/notes"; bash "$d/scripts/gate.sh"; echo "exit=$?"`
    Today: the four `ok` lines of item 11 and `exit=0`. Holds: `ok` for `test_add_then_list`, `test_list_empty`,
    and `test_usage`, `FAIL` for `test_completions_match` and for each of the four new tests, and `exit=5`.

`test_search_matches` asserts the output and exit code of items 1 and 4, `test_search_plain_text` of items 2 and
3, `test_search_no_match` of items 5 and 6, and `test_search_usage` of items 7 and 8.

## Calls Claude made

Nobody could answer a question while this spec was written. Each call below stands unless Geoff strikes it.
Calls 1 and 2 change the file list the brief settled.

1. `completions/notes.bash` joins the brief's two files, because the gate the brief requires fails without it.
2. `README.md` gains one sentence for `search`, worded under "Files", though the brief does not name the file.
   Striking done item 10 and the file from the task leaves it out.
3. The match is anywhere in a note, so `rope` finds `ropes`.
4. Several arguments join with single spaces and match as one phrase, as `add` joins its text.
5. An empty word counts as a missing word and exits 2.
6. A missing notes file counts as no match and exits 1, though `list` exits 0 there.
7. Matches go to stdout and the usage line to stderr, as the usage line goes today.
8. The usage line's wording and the four test names are fixed above.
9. `grep -iF --` does the match, over a bash loop or awk.
10. The task is 40 minutes on Sonnet at high effort, with `standards:diff-reviewer` as its one reviewer.
11. The launching session commits `spec.md` straight to `main` after approval, with no pull request, so the task's
    worktree and its reviewer can read it.
