# Spec: notes search

This spec covers one task that ends in one pull request to `example/notes`. It was written on 2026-11-22 from
`brief.md`, the design Geoff settled in conversation. Nobody could answer a question while it was written, so
each point the brief left open is decided here and listed under "Calls Claude made".

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is a new command, `bin/notes search <word>`, that prints every note containing the word, oldest first.
The match ignores case, and the word is plain text, never a pattern.

These are not goals: patterns or flags, a search for several words at once, a change to `add` or `list`, and a
change to `README.md`.

The work fails if any of these is true when it merges:

- A search prints a note that doesn't contain the word, or leaves out one that does.
- A character in the word, such as `.` or a leading `-`, is read as anything but itself.
- The gate passes without running the search tests. `tests/run.sh:15` runs a hand-written list of test names, so
  a new test function left off that list never runs and the gate still exits 0.

## What the command does

| Case | Output | Exit status |
| --- | --- | --- |
| One or more notes contain the word | Each matching note on stdout, in file order | 0 |
| No note contains the word | Nothing | 1 |
| The notes file doesn't exist | Nothing | 1 |
| No word, an empty word, or more than one argument after `search` | The usage line on stderr | 2 |
| The notes file exists but can't be read | `grep`'s own message on stderr | 2 |

"Contains" means the word appears anywhere in the note, so `rope` finds `Ropewalk hours`. A phrase is one quoted
argument: `bin/notes search "buy rope"`. File order is oldest first, because `add` only appends (`bin/notes:5`).

The usage line becomes `usage: notes add <text> | notes list | notes search <word>`. The script has one usage
line, so `bin/notes bogus` prints the new one too.

Three edges stay as `grep` leaves them and have no test: the unreadable file in the last row, a word that holds
a newline, and case folding outside ASCII, which follows the locale. The command has no size or time limit.

## Approaches

1. Picked, and the one the task builds: `grep -F -i -e "$word" -- "$file"`, behind two checks. The argument
   check comes first, so a missing word exits 2 whether or not the file exists. The file check comes second
   and is `[ -f "$file" ]`, the test `list` uses. Documented in `grep(1)`, GNU grep 3.12: `-F` is "Interpret
   PATTERNS as fixed strings, not regular expressions", `-i` is "Ignore case distinctions in patterns and input
   data", and "the exit status is 0 if a line is selected, 1 if no lines were selected, and 2 if an error
   occurred". It prints lines in file order and gives exit statuses 0 and 1 itself. It needs the file check
   because `grep` exits 2 with a message on a missing file. A probe of a throwaway copy of `bin/notes` with this line printed the "when it holds" output of
   done items 1 to 5 below.
2. Passed over: a bash loop over the file that compares `${line,,}` with the lowered word. It is assembled from
   documented bash pieces and needs no `grep`, but it is more lines and keeps its own exit status.

No assumption is shared between tasks, because there is one task.

## Files

The brief names two files, and the searches agree. Each search ran as `git grep -nE <pattern>` over the tracked
files, leaving out `brief.md`.

| Search | Hits | Verdict on each hit |
| --- | --- | --- |
| `notes (add\|list)`, where `\|` stands for a plain `|` | 5 | `bin/notes:7` changes (the usage line). `tests/run.sh:7` and `:10` stay, they are the `add` and `list` tests. `README.md:3` and `:4` are dismissed, see call 6. |
| `usage` | 4 | `bin/notes:7` and `tests/run.sh:15` change. `tests/run.sh:12` and `:13` stay: `test_usage` checks only that the first word is `usage:`, which still holds. |
| `test_` | 5 | `tests/run.sh:15` changes (the loop's list of names). `:2`, `:6`, `:9`, and `:12` stay. |
| `search` (`-i`) | 0 | Nothing in the repo names the command yet. |

The task changes `bin/notes` and `tests/run.sh`. `scripts/gate.sh` only calls `tests/run.sh` and stays as it is.

The scoped backlog sweep has nothing to read: the repo has no backlog file (`git grep -il backlog` prints
nothing, and there is no `docs/` folder).

## Commands and the denials log

The task runs `bash scripts/gate.sh`, `bin/notes`, `mktemp`, and `rm -f` on a file `mktemp` made, and then the
commit, push, and pull request commands that `building-from-specs` owns. The first four ran in Claude Code
today. The push and pull request commands could not run from the session that wrote this spec.

The denials log holds three entries from the last 30 days (2026-10-23 to 2026-11-22): a force push to `main`, an
`rm -rf` outside the working folder, and a fetch from an unknown host. None of the task's commands matches one.
The tests remove a temporary file with `rm -f`, as `tests/run.sh:10` does, and never with `rm -rf`.

## Task: Add notes search

The task changes `bin/notes` and `tests/run.sh`. `standards:diff-reviewer` reads it. No second reviewer is
needed, because the search reads the notes file, writes nothing, and renders no UI. The task waits for no other
task, and its pull request is the only one to merge.

It is planned at 40 minutes. The like tasks in `task-report` are "Add notes list" at 34 measured minutes and
"Let notes add read stdin" at 41, each a command change with its tests. "Add the usage test" at 12 was tests
only. The task drives no wait, because the repo runs no CI on pull requests. The goal's time clause is
`or stop after 80 minutes`.

The session is named `notes-search` and runs on Sonnet at medium effort. `building-from-specs` "Launching a
task" owns the launch command and its four checks. On 2026-11-22, on pavilion, `claude agents --json` printed
`[]`. `claude-worktree-busy` could not run from the session that wrote this spec, so the launch runs it first.
The task needs no secret and no CI. `spec.md` is not committed and the task's worktree starts from the remote's
`main`, so the goal and the reviewer's brief name this file by its absolute path in the main checkout. It stays
out of the pull request.

### Goal

Run each check from the repo root, in one command that starts with this setup line. A check run without it
would read `~/.notes`.

```bash
f=$(mktemp); printf '%s\n' 'buy rope' 'fix a.c' 'Ropewalk hours' 'abc' 'tar -x file' > "$f"
```

Today, every `bin/notes search` command below prints `usage: notes add <text> | notes list` on stderr and
exits 2.

1. A search prints every note that contains the word, oldest first, whatever the case.

   ```bash
   NOTES_FILE=$f bin/notes search ROPE; echo "exit $?"
   ```

   When it holds: `buy rope`, `Ropewalk hours`, `exit 0`.

2. The word is plain text.

   ```bash
   NOTES_FILE=$f bin/notes search a.c; echo "exit $?"
   NOTES_FILE=$f bin/notes search -x; echo "exit $?"
   NOTES_FILE=$f bin/notes search 'a*c'; echo "exit $?"
   ```

   When it holds: `fix a.c`, `exit 0`, `tar -x file`, `exit 0`, `exit 1`.

3. No match prints nothing and exits 1.

   ```bash
   NOTES_FILE=$f bin/notes search zebra; echo "exit $?"
   ```

   When it holds: `exit 1` and nothing else.

4. A missing notes file is no match.

   ```bash
   NOTES_FILE=$f.gone bin/notes search rope; echo "exit $?"
   ```

   When it holds: `exit 1` and nothing else.

5. A missing word exits 2 with the usage line on stderr, which names the new command, whether or not the notes
   file exists.

   ```bash
   NOTES_FILE=$f.gone bin/notes search >/dev/null; echo "exit $?"
   NOTES_FILE=$f.gone bin/notes search "" >/dev/null; echo "exit $?"
   NOTES_FILE=$f.gone bin/notes search buy rope >/dev/null; echo "exit $?"
   ```

   Today: `usage: notes add <text> | notes list` and `exit 2`, three times.
   When it holds: `usage: notes add <text> | notes list | notes search <word>` and `exit 2`, three times.

6. The gate passes on the branch's last commit and runs one test for each item above.

   ```bash
   bash scripts/gate.sh; echo "exit $?"
   ```

   Today: `ok   test_add_then_list`, `ok   test_list_empty`, `ok   test_usage`, `exit 0`.
   When it holds: those three lines, then `ok   test_search_match`, `ok   test_search_plain_text`,
   `ok   test_search_no_match`, `ok   test_search_no_file`, `ok   test_search_usage`, no `FAIL` line, `exit 0`.

7. No test function is left off the loop's list.

   ```bash
   grep -c '^test_[a-z_]*()' tests/run.sh; bash scripts/gate.sh | grep -c '^ok '
   ```

   Today: `3`, `3`. When it holds: `8`, `8`.

Each new test checks the output and the exit status of every command in its item, on a notes file it makes
with `mktemp`. `test_search_usage` reads stderr alone, as `tests/run.sh:13` does, and checks that the usage line
holds `notes search <word>`.

The repo runs no CI on pull requests, so the gate on the branch's last commit is its only full run. The pull
request quotes the output of items 1 to 7 from that commit, and a commit after that run needs a new run.
`building-from-specs` "Gates and review" and "The pull request" own the review and the report. Under
`## For Geoff` the pull request names the README sentence in call 6.

## Calls Claude made

1. "Contains" is a substring match, so `rope` finds `ropes`. The brief says "contains the word" and names no
   word boundary.
2. A missing notes file counts as no match: nothing printed, exit 1. `list` already prints nothing for a missing
   file.
3. An empty word counts as a missing word and exits 2, because an empty plain-text word matches every note.
4. More than one argument after `search` exits 2 with the usage line. The option passed over joins the
   arguments with spaces, as `add` does. Allowing more arguments later breaks nobody, and reversing this call
   changes one check in `bin/notes` and one case in `test_search_usage`.
5. An unreadable notes file passes through `grep`'s message and exit status 2, with no test. Today `list` prints
   `cat`'s message for the same file and exits 0, and this task leaves that alone.
6. `README.md` stays as it is, because the brief sets the files at two. It describes `add` and `list` and will
   not mention `search` after the merge. This sentence is ready to land as a direct change if Geoff wants it:
   "`bin/notes search <word>` prints the notes that contain the word, oldest first, and exits 1 when none does."
7. The new tests join the hand-written list at `tests/run.sh:15`, and done item 7 guards it. The option passed
   over makes the loop find every `test_*` function itself, which changes how the runner works.
8. The five test names in done item 6 are fixed here so that the gate's output can be checked line by line.
9. The usage line's wording is fixed as written under "What the command does".
10. The task is planned at 40 minutes and runs on Sonnet at medium effort, because every behaviour call is made
    above and the change is small.
11. The goal names `spec.md` by absolute path, and the file stays out of the pull request.
