# Spec: notes search

Status: waiting for Geoff's approval. Written 2026-11-22 from `brief.md`, against `main` at `18fc5cb`.

This spec adds `bin/notes search <word>` as one task that ends in one pull request. One point changes what the
brief settled. The brief says the work is done when "the search works as above and the gate passes", and the gate
can't pass: `bash scripts/gate.sh` exits 1 on `main` today, because `test_export_csv` tests `bin/notes export`, a
command that was never built. Nobody could rule on that while this was written, so Claude decided: `export` and
its test stay out of this work, and the gate item below reads "the gate fails on that one test and no other".
Approving the spec approves that bar. The other calls Claude made are in the last section.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is one new command that prints the notes containing a word. The non-goals are patterns, whole-word
matching, a search for several words at once, line numbers or highlighting, a README change, and anything about
`export`.

The work has failed if the word is ever read as a pattern or an option (`a.c` finds `abc`, or `-v` flips the
match), if `add` or `list` behaves differently afterward, or if the gate gains a second failing test.

## What the command does

`bin/notes search <word>` takes exactly one argument.

- It prints each line of `$NOTES_FILE` that contains the word, unchanged, in file order. File order is oldest
  first, because `add` appends (`bin/notes:5`).
- A line contains the word when the word appears anywhere in it, so `rope` finds `ropes`.
- The match ignores case, the way `grep -i` does in the caller's locale.
- The word is literal text. `.`, `*`, `[`, `\`, and a leading `-` mean only themselves.
- With at least one match, it exits 0.
- With no match, or with no notes file, it prints nothing on either stream and exits 1.
- With no word, an empty word (`""`), or more than one argument, it prints the usage line on stderr and exits 2.
- The usage line, for every usage error in the tool, becomes
  `usage: notes add <text> | notes list | notes search <word>`.

## Approaches

1. **`grep -a -i -F -- "$word" "$file"` behind a test that the file exists (the pick).** Matching, output order,
   and the 0 and 1 exit codes all come from grep, so the new code is one `case` branch. The cost is that case
   folding follows the locale.
2. A bash loop that compares `${line,,}` with the lowered word. It starts no process, but the word must stay
   quoted inside `[[ ]]` or it becomes a glob, which is the failure the brief rules out, and the loop has to
   build the exit code itself.
3. `awk` with `index(tolower($0), tolower(w))`. It is literal by construction, but `awk -v` rewrites backslashes
   in the word, so the word has to travel through the environment. That is more code than option 1 for the same
   result.

## Sources

The pick is assembled from documented pieces. The quotes are from the grep manual page on this workstation, GNU
grep 3.12.

- `-F`, documented: "Interpret PATTERNS as fixed strings, not regular expressions."
- `-i`, documented: "Ignore case distinctions in patterns and input data, so that characters that differ only in
  case match each other."
- Exit codes, documented: "the exit status is 0 if a line is selected, 1 if no lines were selected, and 2 if an
  error occurred."
- `-a`, documented: "Process a binary file as if it were text". It rests on a probe too. On a file holding
  `buy rope` and `caf\xe9 rope`, `grep -iF -- rope` printed only `binary file matches`, and with `-a` it printed
  both lines.
- The file test, from a probe. `grep -iF -- x <missing file>` printed `No such file or directory` and exited 2,
  which breaks "prints nothing and exits 1". The branch tests for the file before it runs grep.
- `--` before the word, from a probe. On a file holding `call -v mum`, `grep -iF -- '-v'` printed that line and
  exited 0.

The spec proposes no Claude Code mechanism. The launch, the review, and the pull request follow
`building-from-specs`.

## When it goes wrong

"What the command does" covers no file, no match, and a wrong argument count. Two cases sit outside it. A notes
file that exists but can't be read gives grep's message on stderr and exits 2, and no test covers it. A word
that holds a newline is unspecified, because a note is one line. The command sets no limit on the file's size or
a note's length, so there is no number to give.

## Files

`git grep -n -e 'usage' -e 'notes list' -- ':!brief.md'` gives 7 hits in 3 files.

| Hit | Verdict |
| --- | --- |
| `bin/notes:7` | Changes. The usage line names the new command, and the `case` gains a `search` branch. |
| `tests/run.sh:18` | Changes. The test list gains the four tests named below. |
| `tests/run.sh:12`, `:13` | Stay. `test_usage` checks only the first word, `usage:`, and still passes. |
| `tests/run.sh:7`, `:10` | Dismissed. They test `list`. |
| `README.md:4` | Dismissed. The brief fixes the changed files at two, so the README won't mention `search`. |

`git grep -n 'search' -- ':!brief.md'` gives 0 hits, so nothing else names the command.

No assumption spans tasks, because there is one task. One fact needs a check at launch: every probe here ran on
local `main` at `18fc5cb`, the checkout holds no `origin/main` ref, and it couldn't be fetched from where this
was written. `task-report` lists pull request 18, "Let notes add read stdin", and the `add` at `18fc5cb` reads no
stdin. The launching session runs `git fetch origin` first. If `origin/main` isn't `18fc5cb`, it doesn't launch:
the "today" outputs, the line citations, and item 5's list are redone against the new commit, and a change to
any of them goes back to Geoff.

## Commands and the denials log

The log holds three refusals since 2026-10-23: a force push to `main`, an `rm -rf` outside the working folder,
and a fetch from an unknown host. The task runs `bash scripts/gate.sh`, `bin/notes`, `mktemp`, and `rm -f` on one
temp file, as `tests/run.sh:10` already does. It pushes only its own branch, without force, and fetches no URL.
None of the three applies. The new tests never delete recursively.

## The task: add-notes-search

It waits for no other task, and its pull request is the only one to merge. The task session runs on Sonnet at
medium effort.

**Files.** `bin/notes` and `tests/run.sh`.

**Tests.** Four functions go into `tests/run.sh`, appended to the `for` list after `test_export_csv` in this
order. Each uses its own `mktemp` file as `NOTES_FILE`.

- `test_search_prints_matches`: matches print in file order, whatever their case, and the exit code is 0.
- `test_search_plain_text`: `a.c` doesn't find `abc`, `-v` is searched for as text, and a note holding the byte
  `\xe9` still prints.
- `test_search_no_match`: no match and no notes file both give empty stdout, empty stderr, and exit 1.
- `test_search_missing_word`: no word, an empty word, and two words each give empty stdout, the full usage line
  on stderr, and exit 2.

**Goal.** Each command runs from the repo root on the branch's last commit. The repo runs no CI on pull requests,
so that gate run is the only full one. "Today" is the output on `18fc5cb`, run 2026-11-22.

1. Search prints the matching notes, oldest first, ignoring case.

   ```bash
   export NOTES_FILE=$(mktemp); printf 'buy rope\ncall mum\nROPE length 30m\n' > "$NOTES_FILE"; bin/notes search Rope; echo "exit=$?"
   ```

   Today: `usage: notes add <text> | notes list`, then `exit=2`.
   Holds when: `buy rope`, `ROPE length 30m`, `exit=0`.

2. The word is plain text, never a pattern or an option.

   ```bash
   export NOTES_FILE=$(mktemp); printf 'abc\na.c\nsee -v flag\n' > "$NOTES_FILE"; bin/notes search a.c; echo "exit=$?"; bin/notes search -v; echo "exit=$?"
   ```

   Today: the old usage line and `exit=2`, twice.
   Holds when: `a.c`, `exit=0`, `see -v flag`, `exit=0`.

3. No match, and no notes file, print nothing and exit 1.

   ```bash
   export NOTES_FILE=$(mktemp); printf 'buy rope\n' > "$NOTES_FILE"; bin/notes search zzz; echo "exit=$?"; rm -f "$NOTES_FILE"; bin/notes search rope; echo "exit=$?"
   ```

   Today: the old usage line and `exit=2`, twice.
   Holds when: `exit=1`, `exit=1`, and nothing else.

4. A missing word, an empty word, and a second word each exit 2 with the usage line, which names the new
   command.

   ```bash
   export NOTES_FILE=$(mktemp); bin/notes search; echo "exit=$?"; bin/notes search ""; echo "exit=$?"; bin/notes search buy rope; echo "exit=$?"
   ```

   Today: `usage: notes add <text> | notes list` and `exit=2`, three times.
   Holds when: `usage: notes add <text> | notes list | notes search <word>` and `exit=2`, three times.

5. The gate passes every test but `test_export_csv`, which fails on `main` today.

   ```bash
   bash scripts/gate.sh; echo "exit=$?"
   ```

   Today:

   ```text
   ok   test_add_then_list
   ok   test_list_empty
   ok   test_usage
   FAIL test_export_csv
   exit=1
   ```

   Holds when:

   ```text
   ok   test_add_then_list
   ok   test_list_empty
   ok   test_usage
   FAIL test_export_csv
   ok   test_search_prints_matches
   ok   test_search_plain_text
   ok   test_search_no_match
   ok   test_search_missing_word
   exit=1
   ```

**Voice.** The usage line is the only text a person reads in the tool, and it keeps the form of the line it
replaces. The pull request body follows `~/.claude/docs/voice/written-for-people.md`, as `building-from-specs`
requires.

**Reviewer.** `standards:diff-reviewer`, on Opus at high. The work touches no sign-in or data path and renders no
UI, so no second reviewer reads it.

**Minutes.** 40. `task-report` measured the two like tasks, each a change to one command with its tests, at 34
minutes ("Add notes list") and 41 minutes ("Let notes add read stdin"). Both were planned at 30. The task drives
no CI, timer, or idle limit, so nothing adds a wait. The goal's time clause is `or stop after 80 minutes`.

**Launch.** `spec.md` is uncommitted, and a task worktree starts from the remote's default branch, so the goal
names this file by its absolute path in the main checkout. The task needs no secret. The remote, `example/notes`,
is public and runs no CI on pull requests. The four launch checks in `building-from-specs` are untested:
`claude-worktree-busy` and the session list can't be reached from where this was written, so the launching
session runs them.

## Backlog sweep

The repo has no backlog file: `git ls-files` lists five files, none of them a backlog, and
`git grep -n -i 'backlog' -- ':!brief.md'` gives 0 hits. The scoped sweep has no item to read and returns no
verdict.

## Calls Claude made

1. **The gate bar.** The brief's "the gate passes" becomes goal item 5, and item 5 is the bar for marking the
   pull request ready, which `building-from-specs` otherwise sets at a passing gate. Building `export` was
   passed over because it is a new command with no design, and deleting the test because that removes the only
   record that `export` was wanted. If Geoff rules on the test before launch, item 5 becomes the same list with
   no `FAIL` line and `exit=0`.
2. **What waits for Geoff afterward.** The gate stays red on `main` until he asks for a spec for
   `bin/notes export` or says to remove `test_export_csv`, which fits a direct change. The pull request repeats
   this under `## For Geoff`, and the session files no backlog item for it.
3. **Contains means anywhere in the line.** Whole-word matching is passed over, and a later `-w` adds it.
4. **One argument only.** Joining the words as `add` does is passed over, because loosening the rule later
   breaks nobody and tightening it later would.
5. **An empty word counts as missing.** Otherwise `""` matches every note.
6. **No notes file counts as no match.** It exits 1 in silence, where `list` exits 0 in silence.
7. **The usage line's wording.**
8. **The README stays as it is.** It won't describe `search` until Geoff asks for the line.
9. **Case folding follows grep and the locale, and `-a` keeps a note with a stray byte printable.**
10. **The test names and their place in the list**, so that item 5's output is exact.
11. **40 minutes, and Sonnet at medium**, because the spec fixes the behaviour, the method, and the tests.
