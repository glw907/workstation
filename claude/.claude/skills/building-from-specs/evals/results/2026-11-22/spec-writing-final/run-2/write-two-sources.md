# Spec: notes search

This spec adds `bin/notes search <word>` as one task that ends in one pull request, planned at 40 minutes. It
follows `brief.md`, the design Geoff approved, with one departure he should check before he approves. The brief's
"no match exits 1" contradicts the README's "Every command exits 0 when it runs, even when it prints nothing".
The spec keeps the brief's exit 1, because the brief is the later and more specific decision and no existing
script can call a command that doesn't exist yet. It then corrects the README, which makes three changed files
where the brief names two. Reversing to exit 0 would change one line in `bin/notes`, two tests, and one README
sentence.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is one new command that prints every note containing a word, oldest first, ignoring case, with the word
read as plain text. It exits 0 when it prints a note, 1 when no note matches, and 2 with the usage line when the
word is missing.

Non-goals: patterns or wildcards, a whole-word mode, a search for several words in any order, highlighting, line
numbers, and any change to what `add` and `list` print or return.

The work fails if the word is ever read as a pattern or an option, if `add` or `list` changes its exit status, if
a new test is written but never runs, or if the README still says every command exits 0.

## Behavior

A note is one line of `$NOTES_FILE`, and file order is oldest first, because `add` appends a line
(`bin/notes:5`).

- `search <word>` prints each line that contains the word as a substring, in file order, and exits 0.
- Case is ignored. The word is fixed text: `a.c` doesn't match `abc`, and `-x` is a word, never an option.
- Several arguments are joined with single spaces into one word, as `add` joins its text.
- No matching line prints nothing and exits 1. A notes file that doesn't exist counts as no match.
- No word prints the usage line to stderr and exits 2. So does a word with no characters in it after the join.
  The usage line, for every usage error, is `usage: notes add <text> | notes list | notes search <word>`.

## Approaches

1. Two guards, then `grep -iF -e "$word" -- "$file"`. The guards send an empty word to the usage line and a
   missing file to exit 1. After them grep's exit status is already the brief's 0 and 1. The cost is that a read
   error returns grep's 2, the number the tool uses for a usage error. This is the pick.
2. A bash loop that compares lowercased lines with `[[ ${line,,} == *"${word,,}"* ]]`. It needs no grep, but it
   is more code to test and must build the exit status by hand.
3. `awk` with `index(tolower($0), tolower(w))`. It has grep's reach, but `-v` rewrites backslashes in the word.

All three are documented. For the pick, `grep --help` (GNU grep 3.12, this machine) says "-F, --fixed-strings
PATTERNS are strings", "-i, --ignore-case ignore case distinctions in patterns and data", and "-e,
--regexp=PATTERNS use PATTERNS for matching". `man grep` says "the exit status is 0 if a line is selected, 1 if
no lines were selected, and 2 if an error occurred." A throwaway copy of `bin/notes` with the guards and this
line, run in a temp folder, printed every "holds" output of goal items 1 to 7. For the second, `man bash` lists
`${parameter,,pattern}` under "Case modification". For the third, `man awk` says `index(s, t)` returns "the
index of the string t in the string s, or zero if t is not present", and `awk -v w='a\.c' 'BEGIN{print w}'`
printed `a.c` with a warning.

## When it goes wrong

The command has no size or time limit, because grep streams the file. A notes file that exists but can't be read
passes grep's message and its exit status 2 through. Case folding beyond ASCII follows grep in the caller's
locale, and the tests use ASCII only.

## Assumptions

The spec has one task, so no assumption spans tasks.

## Files

Each search ran with `git grep -n` on `745419b`. The task changes `bin/notes`, `tests/run.sh`, and `README.md`.

- `-i 'usage'`, 6 hits. `bin/notes:7` changes (the usage line). `README.md:10` changes (the exit rule).
  `tests/run.sh:15` changes (the list of tests to run). `tests/run.sh:12-13` stays: `test_usage` reads only the
  first word. `brief.md:9` is the design.
- `'bin/notes'`, 7 hits. `README.md:3-4` stay, and their paragraph gains the search sentence after line 5.
  `tests/run.sh:7,10,13` are the existing tests and stay. `brief.md:7,10` is the design.
- `-i 'exit'`, 5 hits. `README.md:10` and `bin/notes:7` change, as above. `tests/run.sh:2,18` and `brief.md:9`
  stay.
- `'test_'`, 5 hits, all in `tests/run.sh`. Line 15 changes. Lines 2, 6, 9, and 12 stay.
- `-i 'search'`, 3 hits, all in `brief.md`. Nothing else names the command yet.

`scripts/gate.sh` has no hit and doesn't change. `brief.md` stays as it is.

The comment at `tests/run.sh:2` says the file runs every `test_*` function, but the loop at line 15 names three
tests by hand. A new test runs only when its name is in that list. The builder appends the seven new names to
the list in the order goal item 8 prints them.

## Commands and the denials log

`.workstation/denials.log` holds three refusals since 2026-10-23: a force push to `main`, a recursive delete
outside the working folder, and a fetch from an unknown host. The task runs `bin/notes`, `bash scripts/gate.sh`,
`mktemp`, `git add` by file name, `git commit`, `git diff`, a plain push of its own branch, and the `gh pr` steps
that `building-from-specs` "The pull request" owns. None of those matches a refusal. A new test removes a temp
file with `rm -f` on that one file, as `test_list_empty` does, and never with `rm -r`.

## The task: notes-search

Files: `bin/notes`, `tests/run.sh`, `README.md`. Reviewer: `standards:diff-reviewer`, on Opus at high. The build
session runs on Sonnet at high. The task waits for no other task, and with one pull request there is no merge
order.

Minutes: 40. `task-report --since 2026-11-01` gives the two like tasks in this repo, "Add notes list" at 34
measured minutes and "Let notes add read stdin" at 41. The repo runs no CI on pull requests
(`.workstation/remote.txt`), so the task waits on nothing. The goal's time clause is `or stop after 80 minutes`.

### Goal

Every check ran on 2026-11-22 at `745419b`, twice, with the same output. Items 1 to 7 and 10 run from the repo
root after this line:

```bash
f=$(mktemp); printf '%s\n' 'Buy rope' 'call Ann' 'coil the ROPE' 'a.c' 'abc' '-x marks the spot' > "$f"
```

Today each command in items 1 to 7 prints `usage: notes add <text> | notes list` and `exit 2`, once for each
call to `bin/notes`.

1. Search prints the matching notes, oldest first, ignoring case.
   `NOTES_FILE=$f bin/notes search rope; echo "exit $?"`
   Holds: `Buy rope`, `coil the ROPE`, `exit 0`.
2. The word is plain text.
   `NOTES_FILE=$f bin/notes search a.c; echo "exit $?"`
   Holds: `a.c`, `exit 0`.
3. A word that starts with a dash is searched for.
   `NOTES_FILE=$f bin/notes search -x; echo "exit $?"`
   Holds: `-x marks the spot`, `exit 0`.
4. Several arguments search as one phrase.
   `NOTES_FILE=$f bin/notes search the rope; echo "exit $?"`
   Holds: `coil the ROPE`, `exit 0`.
5. No match prints nothing and exits 1.
   `NOTES_FILE=$f bin/notes search anchor; echo "exit $?"`
   Holds: `exit 1`.
6. A missing notes file is no match.
   `g=$(mktemp); rm -f "$g"; NOTES_FILE=$g bin/notes search rope; echo "exit $?"`
   Holds: `exit 1`.
7. A missing or empty word exits 2 with a usage line on stderr that names the new command.
   `bin/notes search 2>&1 >/dev/null; echo "exit $?"; bin/notes search "" 2>&1 >/dev/null; echo "exit $?"`
   Holds: `usage: notes add <text> | notes list | notes search <word>` and `exit 2`, twice.
8. The gate passes on the branch's last commit, with one test for each of items 1 to 7. Each test asserts its
   item's output and its exit status.
   `git rev-parse --short HEAD; bash scripts/gate.sh; echo "exit $?"`
   Today: `745419b`, `ok   test_add_then_list`, `ok   test_list_empty`, `ok   test_usage`, `exit 0`.
   Holds: the last commit's hash, those three lines, then `ok   test_search_finds`,
   `ok   test_search_plain_text`, `ok   test_search_dash_word`, `ok   test_search_phrase`,
   `ok   test_search_no_match`, `ok   test_search_missing_file`, `ok   test_search_missing_word`, no `FAIL`
   line, and `exit 0`.
9. The three existing test functions are unedited.
   `git diff 745419b -- tests/run.sh`
   Today: nothing. Holds: added lines only, apart from the loop's list at line 15.
10. `list` on a missing file still exits 0. This check passes today and guards the README's rule for `list`.
    `g=$(mktemp); rm -f "$g"; NOTES_FILE=$g bin/notes list; echo "exit $?"`
    Today and when it holds: `exit 0`.
11. The README describes the command and states the exit rule truthfully.
    `grep -c 'Every command exits 0' README.md; grep -n 'search' README.md`
    Today: `1` and nothing more. Holds: `0`, then a line that contains `` `bin/notes search <word>` `` and a
    line that contains `` `search` exits 0 ``.

The README's first paragraph gains this sentence after the one about `list`: "`bin/notes search <word>` prints
every note that contains the word, ignoring case, oldest first." Its last paragraph becomes: "`add` and `list`
exit 0 when they run, even when they print nothing. `search` exits 0 when it prints a note and 1 when no note
matches. Every command exits 2 on a usage error. Scripts that call `notes` rely on that." README text follows
`writing-voice`'s standard for a README in a shell repo, `~/.claude/docs/voice/written-for-people.md`.

## Before the launch

The launching session runs the four checks in `building-from-specs` "Launching a task". None of them could run
where this spec was written. `.workstation/remote.txt` gives the remote's facts: `example/notes` is public, its
default branch is `main`, and it runs no CI on pull requests. The task needs no secret.

`spec.md` is uncommitted. The task's worktree starts from `origin/main`, so the launching session commits and
pushes `spec.md` before the launch.

## Backlog sweep

The repo has no backlog file (`git ls-files`, 5 files). The scoped sweep has no item to read, so there are no
verdicts and no backlog edits.

## Calls Claude made

Nobody could answer a question while this spec was written. Each call below stands unless Geoff changes it.

1. **Exit 1 on no match stays, against the README's rule, for the reasons in the first paragraph.**
2. **`README.md` joins the brief's two files, because leaving it alone would leave its exit rule false.**
3. "Contains the word" means a substring, so `rope` finds `ropes`.
4. Several arguments are joined with spaces instead of being a usage error.
5. An empty word counts as a missing word, because it would match every note and `list` already does that.
6. A notes file that doesn't exist exits 1 without an error message.
7. The usage line's exact text is the one under Behavior.
8. The match uses `grep -iF`, and a read error passes grep's exit status 2 through untested.
9. The seven tests carry fixed names and a fixed order, so the gate's output can be checked line by line.
10. The build runs on Sonnet at high, because the spec fixes the behavior, the texts, and the test names.
