# Spec: notes search

Written 2026-11-22 from `brief.md`, the design the owner settled in conversation. It is one task and ends in one
pull request to `example/notes`.

## Intent

The owner said: "I want to find a note without scrolling through the whole list."

The goal is one new command, `bin/notes search <word>`, that prints every note containing the word, oldest first.
The match ignores case, and the word is plain text, never a pattern.

The work adds no patterns, no line numbers or highlighting, and no change to what `add` and `list` do.

The work has failed if any character in the word acts as a pattern or an option, if a search test exists that the
gate never runs, or if `add` or `list` behaves differently afterward.

## Behavior

Each line of `$NOTES_FILE` is one note. The word is the one argument after `search`, spaces and all, and a note
matches when the word appears anywhere in it. So `rope` finds `ropes`, and `search 'buy rope'` finds that phrase.

| Call | Standard output | Exit |
| --- | --- | --- |
| `search <word>`, one or more notes match | The matching notes, in file order | 0 |
| `search <word>`, no note matches | Nothing | 1 |
| `search <word>`, the word holds a newline | Nothing | 1 |
| `search <word>`, the notes file doesn't exist | Nothing | 1 |
| `search` with no word, an empty word, or more than one argument | Nothing | 2 |

Every exit 2 prints this line to standard error, and so does an unknown command:

```text
usage: notes add <text> | notes list | notes search <word>
```

A notes file that exists and can't be read is outside this work, and no done item tests it.

## Approach

Two ways were probed on this machine against a four-line file: `buy rope`, `call Ann`, `Coil the ROPE`,
`r.pe is a pattern`.

`grep -iF -e "$word" -- "$file"` is the pick. It is documented: `grep --help` (GNU grep 3.12) says
`-F, --fixed-strings  PATTERNS are strings`, `-i, --ignore-case  ignore case distinctions in patterns and data`,
and `-e, --regexp=PATTERNS  use PATTERNS for matching`. In the probe, `RoPe` printed `buy rope` and
`Coil the ROPE` with exit 0, `r.pe` printed only `r.pe is a pattern`, and `-v` printed nothing with exit 1. It is
one line, and its exits 0 and 1 match the table above. The probe also found two cases the command must catch
before it calls grep. A missing file printed `No such file or directory` with exit 2. A word of `zebra`, a
newline, and `ann` printed `call Ann`, because grep reads each line of the word as its own string.

A Bash loop that compares `${line,,}` with `*"${word,,}"*` is assembled from documented pieces and gave the same
lines in the probe. It needs no outside command, but it is more lines to get wrong and sets its own exit code.

## Files

The list comes from two searches over the five tracked files.

`git grep -n 'notes list'` has 4 hits. `bin/notes:7` is the usage line and changes. `README.md:4` describes
`list`, and the sentence that names `search` goes beside it. `tests/run.sh:7` and `tests/run.sh:10` are the `list`
tests and stay.

`git grep -n 'usage'` has 5 hits. `bin/notes:7` changes. `tests/run.sh:15` is the loop that names each test to
run, and it gains the new names: a test function left out of that list never runs. `tests/run.sh:12` and
`tests/run.sh:13` are `test_usage`, which checks only the first word and stays. `brief.md:9` is the design and
stays.

So the task changes `bin/notes`, `tests/run.sh`, and `README.md`, and nothing else. `scripts/gate.sh` only runs
`tests/run.sh` and stays.

## The task: notes-search

It waits for no other task. One pull request merges, so there is no merge order.

### Goal

Run every command from the repo root, after setting up the test file:

```bash
f=$(mktemp); printf '%s\n' 'buy rope' 'call Ann' 'Coil the ROPE' 'r.pe is a pattern' > "$f"
```

Today, every command in items 1 to 3 and the first four in item 4 print `usage: notes add <text> | notes list`
and `exit 2`.

1. Search prints each note that contains the word, oldest first, whatever the case.

   ```bash
   NOTES_FILE=$f bin/notes search RoPe; echo "exit $?"
   ```

   Holds when it prints `buy rope`, `Coil the ROPE`, `exit 0`.

2. The word is plain text.

   ```bash
   NOTES_FILE=$f bin/notes search r.pe; echo "exit $?"
   NOTES_FILE=$f bin/notes search -v; echo "exit $?"
   NOTES_FILE=$f bin/notes search $'zebra\nann'; echo "exit $?"
   ```

   Holds when the first prints `r.pe is a pattern`, `exit 0` and the other two print only `exit 1`.

3. No match prints nothing and exits 1, and so does a notes file that doesn't exist.

   ```bash
   NOTES_FILE=$f bin/notes search zebra; echo "exit $?"
   g=$(mktemp); rm -f "$g"; NOTES_FILE=$g bin/notes search rope; echo "exit $?"
   ```

   Holds when each prints only `exit 1`.

4. A missing word exits 2 with the usage line on standard error, and the line names the new command.

   ```bash
   NOTES_FILE=$f bin/notes search; echo "exit $?"
   NOTES_FILE=$f bin/notes search ''; echo "exit $?"
   NOTES_FILE=$f bin/notes search buy rope; echo "exit $?"
   bin/notes bogus; echo "exit $?"
   NOTES_FILE=$f bin/notes search 2>&1 >/dev/null | grep -c 'notes search <word>'
   ```

   Today the last prints `0`. Holds when each of the first four prints
   `usage: notes add <text> | notes list | notes search <word>`, `exit 2` and the last prints `1`.

5. The gate passes, and it runs every search test. Each of items 1 to 4 has one or more tests named
   `test_search_*` that fail when the item doesn't hold.

   ```bash
   bash scripts/gate.sh; echo "exit $?"
   bash scripts/gate.sh | grep -c '^ok   test_search'
   grep -c '^test_search' tests/run.sh
   ```

   Today the first prints `ok   test_add_then_list`, `ok   test_list_empty`, `ok   test_usage`, `exit 0`, and the
   other two print `0`. Holds when the first prints those three lines, no `FAIL` line, and `exit 0`, and the other
   two print the same number, `4` or more.

6. The README names the new command.

   ```bash
   grep -c 'notes search' README.md
   ```

   Today it prints `0`. Holds when it prints `1` or more. The README follows the standard that `writing-voice`
   gives for a README in a shell repo.

The repo runs no CI on pull requests (`.workstation/remote.txt`), so the gate on the branch's last commit is the
only full run. The pull request quotes that run.

### Commands and the denials log

The log holds 3 refusals since 2026-10-23: a force push to `main`, an `rm -rf` outside the working folder, and a
fetch from an unknown host. The task runs `bin/notes`, `bash scripts/gate.sh`, `mktemp`, `printf`, `grep`,
`rm -f` on a file `mktemp` just made, `git` on its own branch, and the pull request steps that
`building-from-specs` owns. None of them matches a refusal. A test removes a temp file only the way
`tests/run.sh:10` does, and never with `rm -rf`.

### Reviewers, model, and minutes

`standards:diff-reviewer` reads the branch. The work has no sign-in or data path and no rendered UI, so no second
reviewer reads it.

The task session runs on Sonnet at high, because this spec settles each call and leaves a short edit and its
tests.

The task is 40 minutes. `task-report --since 2026-11-01` lists two tasks that, by their titles, each changed one
command: pull request 12, "Add notes list", took 34 minutes, and pull request 18, "Let notes add read stdin",
took 41 with one fix round. Pull request 15 added only a test and is no guide. The task waits on nothing. The
goal's time clause is `or stop after 80 minutes`.

### Before launch

The task needs no secret. `claude-worktree-busy` and `claude agents --json` could not be run where this spec was
written, so the launching session runs the checks in `building-from-specs`, "Launching a task", on the day.

`spec.md` is untracked today, and the task's worktree starts from the remote's `main`. The goal names the spec by
its absolute path in the main checkout.

## Points with nothing to add

Search has no retry, timeout, or size limit to give a number for. The work adds no project, service, or running
infrastructure, and no release. One task rests on each assumption, so none is shared. The repo has no backlog
file among its five tracked files (`git ls-files`), so the scoped `standards:backlog-sweep` has no item to rule
on and no full sweep is due.

## Calls Claude made

Nobody could answer a question while this was written. Each line below is a call to check at approval.

1. The design's last done item, `grep -c notes README.md` prints 1 or more, prints `3` today, so it can't fail.
   Item 6 replaces it with `grep -c 'notes search' README.md`, which prints `0` today and implies the original.
2. "The gate passes" also holds today. Item 5 keeps it and adds two counts of search tests, both `0` today.
3. A match exits 0. The design gives exits only for no match and a missing word.
4. The usage line reads `usage: notes add <text> | notes list | notes search <word>`.
5. An empty word counts as missing and exits 2, because plain-text matching of nothing matches every note.
6. More than one argument exits 2 with the usage line. Joining them with spaces, as `add` does, was passed over.
   A later commit can widen this without breaking a call that works now.
7. One argument is the word even when it holds spaces, so a quoted phrase is searched as it stands.
8. A word that holds a newline matches nothing and exits 1, because no note spans two lines.
9. A notes file that doesn't exist counts as no match: nothing printed, exit 1. `list` already prints nothing
   then.
10. A notes file that exists and can't be read is left out of this work.
11. A match is the word anywhere in a note, with no whole-word rule.
12. The search tests are named `test_search_*`, so item 5 can count them.
13. `grep -iF -e` over a Bash loop, for the reasons under Approach.
14. Sonnet at high for the build, and 40 minutes.
15. The goal names `spec.md` by absolute path, so that nothing lands on `main` outside a pull request.
