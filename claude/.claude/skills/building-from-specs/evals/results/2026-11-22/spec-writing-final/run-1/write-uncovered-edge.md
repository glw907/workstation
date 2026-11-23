# Spec: notes search

This spec covers one task that ends in one pull request to `example/notes`. Its source is `brief.md`, the design
Geoff settled in conversation. Where the brief is silent, the spec decides and lists the call at the end.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is a new command, `bin/notes search <word>`, that prints every note that contains the word, oldest
first.

The work leaves out patterns, a search for more than one word, any change to `add` or `list`, and a change to
`README.md`. It tests the match with ASCII letters only, and a word that holds a newline is not handled.

The work fails if a search prints a note that lacks the word or misses one that holds it, if any character of
the word acts as a pattern or an option, or if the gate passes without running the new tests.

## What search does

| Run | Prints | Exit |
| --- | --- | --- |
| A word that some notes contain | Each of those notes, whole and unchanged, oldest first, on stdout | 0 |
| A word that no note contains | Nothing, on either stream | 1 |
| The notes file doesn't exist | Nothing, on either stream | 1 |
| No argument, an empty argument, or more than one argument | The usage line, on stderr | 2 |

The match ignores case. A note contains the word when the word appears anywhere in its line, so `rope` finds
`tightrope walk`. Every character of the word stands for itself, including `.`, `*`, and a leading `-`. The rule
counts arguments, so one quoted argument that holds a space is searched as it stands. Notes are stored oldest
first, so file order is the order printed.

The argument check comes before the file test. The file test is `[ -f ]`, the one `list` uses.

Every usage error, an unknown command included, prints this one line:

```text
usage: notes add <text> | notes list | notes search <word>
```

## Approach

The pick is `grep -a -i -F -e <word> -- <file>`, run only when the notes file exists. It is documented.
`grep --help` (GNU grep 3.12) says "`-F, --fixed-strings  PATTERNS are strings`", "`-i, --ignore-case  ignore
case distinctions in patterns and data`", "`-a, --text  equivalent to --binary-files=text`", and "Exit status is
0 if any line is selected, 1 otherwise; if any error occurs and -q is not given, the exit status is 2." Without
`-a`, one stray byte in a note makes grep print `binary file matches` in place of the notes. Grep exits 2 on a
missing file, which would read as a usage error, so the file test comes first.

Two others were weighed. A bash loop that lowercases each line needs no second program, but it takes more lines
and one unquoted expansion turns the word into a glob. An `awk -v` call rewrites a backslash in the word.

No Claude Code mechanism is proposed, so no Anthropic docs page applies. The work adds no project, service, or
infrastructure, and needs no published build. No assumption spans tasks, because there is one task.

## When it goes wrong

Search sets no limit: it reads the file once, whatever its size. A notes file that exists but can't be read is
outside this work. Grep's own message and its status 2 pass through, and there 2 does not mean a usage error.

## Files

`git grep -n -e 'usage' -e 'notes list' -e 'notes add'` finds 9 hits in 4 files.

- `bin/notes:7` changes. The usage line gains the new command, and the `case` gains a `search` arm.
- `tests/run.sh:15` changes. The loop names each test it runs, so a test function missing from that list never
  runs and the gate still passes. Each new test goes on the list. The loop stays a list.
- `tests/run.sh:7`, `:10`, `:12`, and `:13` are the three tests that exist. They stay as they are, and
  `test_usage` still passes because it reads only the line's first word.
- `README.md:3` and `:4` are dismissed. The brief limits the work to two files, so the README won't name the new
  command when this merges. The task's pull request says so under `## For Geoff`.
- `brief.md:9` is dismissed. It is the brief.

The scoped backlog sweep has nothing to read: `git ls-files | grep -i -c -e backlog -e todo -e status` prints 0
and the repo has no `docs/` folder, so there are no verdicts.

## Commands and the denials log

The task runs `bin/notes`, `bash scripts/gate.sh`, `mktemp`, `grep`, `git add` by file name, `git commit`,
`git diff`, `git status`, a push of its own branch, and the pull request commands that `building-from-specs`
owns. The log holds three refusals since 2026-10-23, and none matches a task command.

- `git push --force origin main` (2026-11-03). The task pushes only its own branch and never forces.
- `rm -rf ~/.notes.bak` (2026-11-09), a recursive delete outside the working folder. The task deletes nothing: the
  missing-file test names a path that was never made, as item 5 does. Without `NOTES_FILE`, `bin/notes` reads
  and writes Geoff's real `~/.notes`, so every new test and every run by hand sets it to a `mktemp` path.
- A fetch of `https://example.invalid/notes` (2026-11-17). The task fetches nothing.

## The task: notes-search

The task changes `bin/notes` and `tests/run.sh`. It waits for no other task, and its pull request is the only
one, so there is no merge order. It runs on Opus at medium effort. `standards:diff-reviewer` reads it; the work
has no sign-in, data, or rendered UI for another reviewer.

It is planned at 41 minutes. `task-report --since 2026-11-01` has three rows. Two added behavior to `bin/notes`:
"Add notes list" took 34 minutes and "Let notes add read stdin" took 41, with one fix round. "Add the usage
test", at 12 minutes, added one test and is not a like task. Search has more edge cases than `list`, so the
slower figure stands. Nothing adds a wait, because the repo runs no CI on pull requests. The goal ends with
`or stop after 82 minutes`.

Three things hold before the launch, and the launching session checks each that day.

- `spec.md` is not committed, and a task worktree starts from the remote's `main`. The goal names this spec by
  its absolute path in the main checkout the launch runs from.
- Every "today" output below was recorded on local `main` at `399e8de`. This checkout has no `origin/main` ref,
  and the task report lists "Let notes add read stdin", which `bin/notes:5` doesn't show. After a fetch,
  `git rev-parse main origin/main` prints one hash twice. If it prints two, the "today" outputs and the line
  numbers are read again before the launch.
- The four launch checks in `building-from-specs`, "Launching a task", pass. They could not be run from the
  session that wrote this spec. The task needs no secret.

### Goal

Items 1 to 6 share this setup, run from the worktree's root. `out` shows stdout and the status, and `err` shows
stderr and the status.

```bash
f=$(mktemp); printf '%s\n' 'buy rope' 'Call ROPE shop' 'tightrope walk' 'a.c' 'abc' 'fix -v flag' > "$f"
out() { NOTES_FILE=$f bin/notes "$@" 2>/dev/null; echo "exit $?"; }
err() { NOTES_FILE=$f bin/notes "$@" 2>&1 >/dev/null; echo "exit $?"; }
```

Today every `out` command prints only `exit 2`. Every `err` command, and item 5's command, prints
`usage: notes add <text> | notes list` and `exit 2`.

1. Search finds the word in any case, anywhere in a note, oldest first. `out search rope` and `out search ROPE`
   each print `buy rope`, `Call ROPE shop`, `tightrope walk`, and `exit 0`.
2. The word is plain text. `out search a.c` prints `a.c` and `exit 0`. `out search 'a*c'` prints only `exit 1`.
   `out search 'buy rope'` prints `buy rope` and `exit 0`.
3. A word that starts with a dash is text. `out search -v` prints `fix -v flag` and `exit 0`.
4. No match prints nothing and exits 1. `out search zebra` and `err search zebra` each print only `exit 1`.
5. A missing notes file is no match. `NOTES_FILE=$f.gone bin/notes search rope; echo "exit $?"` prints only
   `exit 1`.
6. Every usage error prints the new usage line on stderr and exits 2. `err search`, `err search ''`,
   `err search buy rope`, and `err bogus` each print `usage: notes add <text> | notes list | notes search <word>`
   and `exit 2`. `out search` prints only `exit 2`, as it does today.
7. The gate passes on the branch's last commit and runs one new test for each of items 1 to 6:
   `test_search_match`, `test_search_plain_text`, `test_search_dash`, `test_search_no_match`,
   `test_search_no_file`, and `test_search_usage`. `bash scripts/gate.sh; echo "exit $?"` prints three `ok`
   lines and `exit 0` today. When the item holds it prints nine `ok` lines, one for each of those six names
   among them, no `FAIL` line, and `exit 0`. `bash scripts/gate.sh | grep -c '^ok   test_search_'` prints `0`
   today and `6` when the item holds. `git status --porcelain bin tests` prints nothing at that run, as it does
   today, so the run is of the commit.
8. The branch changes only the two files. `git diff --name-only main...HEAD` prints nothing today. When the item
   holds it prints `bin/notes` and `tests/run.sh`.

## Calls Claude made

The first five are product calls on points the brief leaves open.

1. "Contains the word" means the word appears anywhere in the note, never only as a whole word.
2. A missing notes file is no match, as `list` treats it as empty: nothing printed, exit 1.
3. An empty word counts as a missing word and exits 2, because it would otherwise match every note.
4. More than one argument after `search` exits 2, the stricter of two options and the one a later change to
   phrase search breaks no one on.
5. One quoted argument that holds a space is searched as it stands.
6. `README.md` stays as it is, because the brief limits the work to two files; a sentence there naming `search`
   fits a direct change if Geoff asks for one.
7. The usage line is the exact text above, and every usage error prints it.
8. With no word and no notes file, the usage error wins and the exit is 2.
9. The method is `grep -a -i -F` behind a `[ -f ]` test.
10. The test loop stays an explicit list, and item 7 names the six new tests so that none goes unrun.
11. The task is planned at 41 minutes and runs on Opus at medium effort.
12. An unreadable notes file, a word that holds a newline, and non-ASCII case folding are outside the work.
