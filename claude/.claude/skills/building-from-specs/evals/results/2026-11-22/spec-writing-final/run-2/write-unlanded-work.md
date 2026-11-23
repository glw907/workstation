# Spec: notes search

This spec adds `bin/notes search <word>` as one task that ends in one pull request. The design is settled in
`brief.md`. One fact holds the launch: the brief gives search the output format of `notes export`, and `main`
has no `notes export`. The task waits until the work that adds export has merged. Approving this spec approves
that wait. If export exists nowhere yet, it needs its own spec first.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is a command, `bin/notes search <word>`, that prints every note containing the word, oldest first,
ignoring case, in the format `notes export` uses, "so scripts can read both the same way."

The non-goals are patterns, whole-word matching, flags, a change to `add` or `list`, a change to `README.md`,
building `notes export`, and changing what export prints.

The work fails if search prints a format that differs from export's, treats the word as a pattern or an option,
or ships with the gate red.

## The launch waits for `notes export`

Export is not in this checkout. These probes ran on `main` at `e3473df`, the only ref here:

- `git grep -c export main -- bin/notes` prints nothing and exits 1.
- `bin/notes export` prints `usage: notes add <text> | notes list` and exits 2.
- `git for-each-ref` lists `refs/heads/main` alone, and `git stash list` is empty.

This session could not read the remote's branches or pull requests, so it can't name the one that adds export.

The spec assumes three things about export, which nothing here can show: it takes no argument, it prints to
stdout, and it prints one line for each note with no header or footer. The session Geoff is talking to tests
them before it launches, in the main checkout, with `main` level with `origin/main`:

```bash
f=$(mktemp); printf '%s\n' one two three > "$f"; NOTES_FILE=$f bin/notes export | wc -l; rm -f "$f"
```

Today it prints the usage line and `0`. The task launches when it prints `3` alone. Any other result on a `main`
that has export means the format isn't lines, and the spec goes back to Geoff before any launch. He can also end
the wait by stating export's format in a sentence, which changes done item 2 and so comes back as an edit to
this spec.

## Approaches

1. Search finds the matching notes and takes each one's line from export's code or output. Picked. One format
   lives in one place, so the two commands can't drift. It costs the wait.
2. Search carries its own copy of export's format. It costs the same wait, and the copies drift at export's next
   change.
3. Search ships now with the bare line `list` prints and changes when export lands. No wait. It ships a format
   Geoff didn't choose, takes a second pull request where the brief sets one, and breaks any script written in
   between.
4. This task builds export too. No wait. It invents a format for a command the brief doesn't design.

## Behavior

A note matches when the word's characters appear anywhere in it, in any letter case: `rope` finds `Buy rope` and
`ROPES drying`. The word is literal text. `a.c` finds `a.c` and not `abc`, and a word that starts with `-` is
still a word.

Everything after `search` is joined with single spaces into one word, as `add` joins its text. No word, or an
empty one, exits 2 and prints the usage line on stderr. The usage line names `notes search <word>` beside the
commands it names on `main` that day.

For each matching note, search prints the line that `notes export` prints for that note when it exports the
whole file. Nothing about a printed line changes because other notes were left out. A match exits 0.

No match prints nothing on stdout or stderr and exits 1. A notes file that doesn't exist is no match.

The session may move export's printing into a function both commands call, provided export's output stays the
same byte for byte. Otherwise it leaves export's code alone.

## When it goes wrong

| Case | Result |
| --- | --- |
| The launch probe prints anything but `3` | No launch. |
| The task session finds no `export` in `bin/notes` | It marks done item 2 unmet, invents no format, and finishes the rest by "In place of a question". |
| The notes file exists and can't be read | An error, never a no-match: a status above 1 and the system's message on stderr. No done item checks this, because a permissions test passes falsely under root. |
| The time clause is reached | The session commits, pushes, writes what is left in the draft pull request, and ends. |

The exit codes are 0 for a match, 1 for none, and 2 for a missing word. The time clause is 80 minutes. The notes
file has no size limit.

## Sources and labels

- Matching with `grep -i -F -e "$word"` is documented. GNU grep 3.12's `--help` reads "-F, --fixed-strings
  PATTERNS are strings", "-i, --ignore-case ignore case distinctions in patterns and data", and "-e,
  --regexp=PATTERNS use PATTERNS for matching". Probed on the goal's six-note file: `-e rope` printed
  `Buy rope` and `ROPES drying` and exited 0, `-e a.c` printed `a.c` alone, `-e -x` printed `tar -x flag`, and
  `-e zebra` printed nothing and exited 1. On a missing file grep exits 2, so search handles that case itself.
- Taking search's lines from export is invented. It draws on no published practice, and it can't be probed
  until export's code is on `main`. The session records how it did it under `## Decisions`.
- The worktree, the goal, the review, and the pull request are documented, in `building-from-specs`.

No assumption spans more than one task. The task's own assumption, export's shape, has its probe above.

## Files

`git grep -n -e 'usage' -e 'notes list' -e 'notes add' -- . ':!brief.md'` finds 8 lines in 3 files.

| Hit | Verdict |
| --- | --- |
| `bin/notes:7`, the usage line | Changes. The `search` branch goes in the same `case`. |
| `tests/run.sh:12`, `:13`, `test_usage` | Stays. It checks the first word only and must still pass. |
| `tests/run.sh:15`, the test loop | Changes. The loop runs a fixed list of names, so a test left off it never runs. |
| `tests/run.sh:7`, `:10` | Stay. Tests of `add` and `list`. |
| `README.md:3`, `:4` | Dismissed. The brief limits the work to two files. The pull request's `## For Geoff` says the README doesn't mention search. |

`git grep -c export -- . ':!brief.md'` finds 0 lines. The task changes `bin/notes` and `tests/run.sh` and no
other file. The line numbers are from `e3473df` and will move when export lands.

## Commands and the denials log

The task runs `bash scripts/gate.sh`, `bin/notes`, `mktemp`, `rm -f` on one temp file, and the commit, push,
and pull request steps that `building-from-specs` owns. The log holds three refusals since 2026-10-23, and none
of these commands meets one:

- `git push --force origin main` (2026-11-03). The session pushes only its own branch, without force.
- `rm -rf ~/.notes.bak` (2026-11-09). Every new test sets `NOTES_FILE` to a `mktemp` path and removes only that
  one file with `rm -f`, as `tests/run.sh:10` does. No test reads or writes `~/.notes`.
- A fetch of `https://example.invalid/notes` (2026-11-17). The task fetches nothing.

## The task: notes-search

- Waits for: the pull request that adds `notes export`, merged to `main`. Merge order: export first, then this.
- Start conditions: the launch probe prints `3`; `spec.md` is on `origin/main`, because the task's worktree
  starts there; and the four checks in "Launching a task" pass that day. The task needs no secret. The repo is
  public and runs no CI on pull requests, so the gate on the branch's last commit is its only full run.
- Files: `bin/notes`, `tests/run.sh`.
- Reviewer: `standards:diff-reviewer`.
- Minutes: 40, and a time clause of 80. `task-report` measured the two like tasks at 34 minutes ("Add notes
  list", planned 30) and 41 ("Let notes add read stdin", planned 30, one fix round). The task drives no CI and no
  timer.
- Model: Opus at medium.

### Goal

Each check runs from the repo root in one Bash call with this setup before it and `rm -f "$f"` after it, because
a shell variable doesn't last between calls and an unset `NOTES_FILE` means `~/.notes`.

```bash
f=$(mktemp); export NOTES_FILE=$f
printf '%s\n' 'Buy rope' 'call Sam' 'ROPES drying' 'a.c' 'abc' 'tar -x flag' > "$f"
```

Every check ran on `e3473df` on 2026-11-22, and "Today" is what it printed. No hold condition depends on what
else `main` gains by launch day.

1. Search prints the notes that contain the word, in any case, oldest first, and no others.

   ```bash
   bin/notes search rope | grep -oF -e 'Buy rope' -e 'ROPES drying' -e 'call Sam' -e abc -e tar
   bin/notes search rope >/dev/null 2>&1; echo "exit $?"
   ```

   Today: the usage line, then `exit 2`. Holds when it prints `Buy rope`, `ROPES drying`, `exit 0`.

2. Search prints each match as the line `notes export` prints for that note.

   ```bash
   out=$(bin/notes search rope) && [ "$(printf '%s\n' "$out" | wc -l)" = 2 ] &&
     [ -z "$(printf '%s\n' "$out" | grep -vxFf <(bin/notes export))" ] && echo same
   ```

   Today: the usage line. Holds when it prints `same`.

3. The word is plain text, never a pattern or an option.

   ```bash
   bin/notes search a.c | grep -oF -e a.c -e abc
   bin/notes search -x </dev/null | grep -oF -e 'tar -x flag'
   ```

   Today: the usage line, twice. Holds when it prints `a.c`, `tar -x flag`.

4. Several arguments make one word.

   ```bash
   bin/notes search y r | grep -oF -e 'Buy rope' -e 'ROPES drying' -e 'tar -x flag'
   ```

   Today: the usage line. Holds when it prints `Buy rope` alone.

5. No match prints nothing and exits 1, and so does a missing notes file.

   ```bash
   bin/notes search zebra 2>&1; echo "exit $?"
   NOTES_FILE=$f.none bin/notes search rope 2>&1; echo "exit $?"
   ```

   Today: the usage line and `exit 2`, twice. Holds when it prints `exit 1`, `exit 1`.

6. A missing or empty word exits 2 with the usage line, which names the new command.

   ```bash
   bin/notes search 2>/dev/null; echo "exit $?"
   bin/notes search '' 2>/dev/null; echo "exit $?"
   bin/notes search 2>&1 >/dev/null | grep -c '^usage:.*notes search <word>'
   bin/notes search '' 2>&1 >/dev/null | grep -c '^usage:.*notes search <word>'
   ```

   Today: `exit 2`, `exit 2`, `0`, `0`. Holds when it prints `exit 2`, `exit 2`, `1`, `1`.

7. `tests/run.sh` holds a test named `test_search_*` for each of items 1 to 6, and the gate passes on the
   branch's last commit.

   ```bash
   bash scripts/gate.sh; echo "exit $?"
   bash scripts/gate.sh | grep -c '^ok   test_search'
   ```

   Today: three `ok` lines, `exit 0`, and a count of `0`. Holds when no line begins `FAIL`, the exit is 0, and
   the count is 6 or more.

## Backlog sweep

`git ls-files | grep -i -c -e backlog -e todo -e status` prints 0, so the repo has no backlog file, and the
remote's issues could not be read from here. The scoped sweep has no item and no verdict.

## Calls Claude made

1. The task waits for export to merge instead of shipping `list`'s bare line now, by the skill's rule that "a
   task that needs another task's work waits until that work has merged."
2. Export is assumed to print one line for each note, and the launch probe tests that before any launch.
3. Search takes its lines from export and keeps no copy of the format.
4. "Contains the word" means the characters appear anywhere in a note, so `rope` finds `ROPES`; whole-word
   matching was passed over, and reversing that is one grep flag and one test.
5. Several arguments join into one word, as `add` joins its text, where the other choice was exit 2.
6. An empty word counts as missing.
7. A notes file that doesn't exist is no match and exits 1, as `list` prints nothing for one.
8. A printed note looks as export prints it in the whole file, so a line number, if export prints one, stays.
9. Case folding follows the session's locale, and the tests use ASCII words.
10. `README.md` stays as it is, by the brief's file list, and the pull request flags that for Geoff.
11. `standards:diff-reviewer` reads alone, because search reads the notes file and writes nothing.
12. The task gets 40 minutes and runs on Opus at medium.
