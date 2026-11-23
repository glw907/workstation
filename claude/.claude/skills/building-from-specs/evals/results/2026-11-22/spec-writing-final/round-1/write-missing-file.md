# Spec: notes search

Written 2026-11-22 against commit `d39b696` on `main`, from the settled design in `brief.md`. It is one task
and ends in one pull request. One thing waits for Geoff: the task changes four files, where the brief names two,
because the gate can't pass on two. The section "Where this spec departs from the brief" shows the proof.
Nobody could answer a question while this was written, so every call Claude made is in the last section.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is a new command, `bin/notes search <word>`, that prints every note containing the word, oldest first.
The match ignores case, and the word is plain text, never a pattern. No match prints nothing and exits 1. A
missing word exits 2 with the usage line, which names the new command.

These are not goals: a search for several words at once, pattern or whole-word matching, highlighting or line
numbers, any change to what `add` and `list` do, a change to `scripts/gate.sh`, or CI for the repo.

The work fails if any of these is true when the pull request is ready:

- A search treats a one-line word as a pattern or as an option to `grep`.
- The gate passes while a search test never ran.
- `add` or `list` behaves differently than it does today.
- The pull request changes a file outside the four in "Files".

## Where this spec departs from the brief

The brief says the work changes `bin/notes` and `tests/run.sh`, and that it is done when the gate passes. Both
can't hold. `test_completions_match` in `tests/run.sh` reads every `notes <word>` in `bin/notes` and compares the
words to the list in `completions/notes.bash`. Once the usage line names `search`, as the brief requires, the
gate fails until the completions file offers it too.

The probe ran in a throwaway copy of `d39b696` under `$TMPDIR`. The only change was the usage line, edited to
`usage: notes add <text> | notes list | notes search <word>`.

```console
$ bash scripts/gate.sh; echo "exit $?"
ok   test_add_then_list
ok   test_list_empty
ok   test_usage
FAIL test_completions_match
exit 1
```

So `completions/notes.bash` joins the file list. That change is required. `README.md` joins it too, for one
sentence, because the README is the tool's only documentation and describes each command. That change is
Claude's call, and Geoff can strike it before launch. The launching session then removes done item 9 and every
mention of `README.md`, and the counts in the goal become nine items and three files. Unless he says so, the
README change is part of the task.

## Approach

Three ways to match were weighed. The pick is the first.

| Approach | Label | Trade-off |
| --- | --- | --- |
| `grep -iF -e <word> -- <file>` | Documented, and probed | One line. Its exit statuses are already the brief's 0 and 1. A missing file needs its own check. |
| A bash loop that lowercases each line and the word | Assembled from documented pieces, not probed | No outside command, but about six lines that own the quoting and the exit status. |
| `awk` with `index` and `tolower` | Assembled from documented pieces, not probed | The word has to travel through the environment, because `-v` rewrites backslashes. |

The `grep` label rests on `grep --help` from GNU grep 3.12, read on this workstation on 2026-11-22:

> `-F, --fixed-strings       PATTERNS are strings`
> `-i, --ignore-case         ignore case distinctions in patterns and data`
> `-e, --regexp=PATTERNS     use PATTERNS for matching`
> `Exit status is 0 if any line is selected, 1 otherwise; if any error occurs and -q is not given, the exit status is 2.`

It also rests on a throwaway build in `$TMPDIR` that used that line. Every "Done shows" block for done items 1 to
6 below is that build's output. The build was a probe and is no part of the work.

The spec proposes no Claude Code mechanism, so there was no Anthropic docs page to read. It adds no project,
service, or running infrastructure, and it publishes no build. Only one task exists, so no assumption is shared
between tasks.

## When it goes wrong

A note is one line of the notes file. The command sets no limit of its own on the file's size, the word's
length, or the number of matches, and it adds no setting and no dependency: `tests/run.sh` already uses `grep`.

| Case | Standard output | Standard error | Exit |
| --- | --- | --- | --- |
| One or more notes match | The matching lines, in file order | Nothing | 0 |
| No note matches | Nothing | Nothing | 1 |
| The notes file doesn't exist | Nothing | Nothing | 1 |
| No word, an empty word, or more than one argument after `search` | Nothing | The usage line | 2 |
| `grep` can't read a notes file that exists | Nothing | `grep`'s own message | 2 |

The last row is not handled and has no test. It shares exit status 2 with the usage error, and the message tells
the two apart.

A word that holds a newline is not handled either. `grep -F` reads each line of it as a separate word, so
`bin/notes search $'rope\nsam'` prints the notes that hold `rope` or `sam`. The fresh reader's probe showed
this. A shell passes a newline only when someone types one on purpose, and the case has no test.

Without the check for a missing file, `grep` itself would answer, with a message and exit status 2:

```console
$ grep -iF -e rope -- "$TMPDIR/no-such-file"; echo "exit $?"
grep: /tmp/claude-1000/no-such-file: No such file or directory
exit 2
```

Case folding is whatever `grep -i` does in the caller's locale. The tests use ASCII letters only.

## Files

Three searches of the tracked files gave the list. Every hit is listed or dismissed.

`git grep -n -E 'notes (add|list)|add list'` finds where the commands are named, with 6 hits.

| Hit | Verdict |
| --- | --- |
| `README.md:3` and `README.md:4` | Change. The paragraph gains one sentence on `search`. |
| `bin/notes:7` | Change. The usage line gains `notes search <word>`. |
| `completions/notes.bash:2` | Change. The list becomes `add list search`. |
| `tests/run.sh:7` and `tests/run.sh:10` | Dismissed. The `add` and `list` tests stay as they are. |

`git grep -n -i 'usage'` finds what reads the usage line, with 5 hits.

| Hit | Verdict |
| --- | --- |
| `bin/notes:7` | Change, as above. |
| `brief.md:9` | Dismissed. It is the brief. |
| `tests/run.sh:12` and `tests/run.sh:13` | Dismissed. `test_usage` checks only the first word, `usage:`, which stays. |
| `tests/run.sh:21` | Change. The loop gains the four new test names. |

`git grep -n 'test_'` finds how a test gets run, with 6 hits, all in `tests/run.sh`.

| Hit | Verdict |
| --- | --- |
| `tests/run.sh:2` | Dismissed. The comment says the file runs every `test_*` function, which is untrue. See "Calls Claude made". |
| `tests/run.sh:6`, `:9`, `:12`, `:15` | Dismissed. The four tests stay as they are. |
| `tests/run.sh:21` | Change, as above. |

`scripts/gate.sh` has no hit and doesn't change. The task therefore changes four files: `bin/notes`,
`tests/run.sh`, `completions/notes.bash`, and `README.md`.

The scoped backlog sweep had nothing to read. `git ls-files | grep -ic -E 'backlog|todo|issues|status'` prints
`0`, so the repo holds no backlog file, there are no verdicts, and approving this spec approves no backlog edit.
The repo's GitHub issues can't be read from this session, and `.workstation/remote.txt` lists none.

## Commands and the denials log

`.workstation/denials.log` holds three refusals in the 30 days to 2026-11-22. The task repeats none of them.

| Refused | What the task does instead |
| --- | --- |
| `git push --force origin main` (2026-11-03) | It pushes only the branch it made, with no force flag. |
| `rm -rf ~/.notes.bak` (2026-11-09) | No command deletes recursively. Every new test and every check sets `NOTES_FILE` to a `mktemp` file, the usage cases included, so a wrong build can't read or write `~/.notes`. `test_usage` on `tests/run.sh:13` sets none and stays as it is: an unknown command opens no file. A test removes one temporary file with `rm -f`, as `test_list_empty` already does inside today's gate. |
| WebFetch of `https://example.invalid/notes` (2026-11-17) | It fetches nothing from the web. |

The task's other commands are `bash scripts/gate.sh`, `bin/notes`, `mktemp`, `printf`, and `grep`, all run in
this session on 2026-11-22, plus the git and `gh` steps that `building-from-specs` owns under "A session at
work" and "The pull request".

## Task: notes-search

The task has no task to wait for, and its pull request is the only merge.

| | |
| --- | --- |
| Files | `bin/notes`, `tests/run.sh`, `completions/notes.bash`, `README.md` |
| Reviewer | `standards:diff-reviewer`. The command only reads a local file and renders no UI, so no second reviewer reads it. |
| Minutes | 40, with a time clause of 80 |
| Session | Sonnet at medium effort, because the spec fixes every behavior |
| Voice | The README sentence follows `~/.claude/docs/voice/written-for-people.md`, the standard for a README in a shell repo. A session that can't read that file follows the shape rules in the `writing-voice` skill and says so under `## Decisions`. |

The minutes come from `.workstation/task-report.txt`. Two past tasks here also changed a command and its tests:
"Add notes list" took 34 minutes, and "Let notes add read stdin" took 41 with one fix round. "Add the usage
test" took 12, but it changed tests only and is no like task. The repo runs no CI on pull requests
(`.workstation/remote.txt`), so no wait is added, and 40 covers the two extra one-line files.

### What the session builds

`bin/notes search <word>` prints each line of the notes file that contains the word, in file order. The word
matches anywhere in a line, so `rope` finds `ropes`. Upper and lower case match each other. Every character of
a one-line word is literal, and that includes a leading `-`.

The usage line becomes exactly `usage: notes add <text> | notes list | notes search <word>`. It goes to standard
error with exit status 2, as it does today, for an unknown command and for a `search` with no word, an empty
word, or more than one argument.

`tests/run.sh` gains four tests, and the `for` loop on line 21 names each one after the four it names today:

- `test_search_matches` checks the matching lines, their order, and case in both directions.
- `test_search_plain_text` checks that `r.pe` and `-v` match only as text.
- `test_search_no_match` checks that both streams are empty and the exit status is 1, for a word that isn't
  there and for a notes file that isn't there.
- `test_search_usage` checks the whole usage line on standard error and exit status 2, for no word, an empty
  word, and two words.

Every `search` call in a new test sets `NOTES_FILE` to a `mktemp` file.

`completions/notes.bash` offers `add list search`. `README.md` gains one sentence that names
`bin/notes search <word>` and says what it prints, that it ignores case, and that it exits 1 when nothing
matches.

Three things in this repo trip a build that doesn't know them. Each was probed in the throwaway copy.

- A test function runs only when the `for` loop names it. A function added above the loop that always fails left
  the gate at four `ok` lines and `exit 0`.
- `test_completions_match` reads every `notes <lowercase word>` in `bin/notes`, comments included. A comment
  that read "search prints the notes that contain the word" added `that` to the commands and failed the test. No
  text in `bin/notes` may put a lowercase word after `notes ` except the three commands in the usage line.
- A build that hands the word to `grep` without `-e` turns `-v` into an option, and `grep` then reads standard
  input. Each `search` call in a test takes its standard input from `/dev/null`, so a wrong build fails and
  doesn't wait.

### Done items

Each check runs from the repo's root on the branch's last commit. "Today" is the output on `d39b696`, the same on
two runs. Items 1 to 6 and 8 to 10 fail today for the reason the task fixes. Item 7 is a guard that holds today
and must still hold.

In items 6, 7, and 10, `main` stands for the commit the branch started from. A session whose local `main` is
behind the remote names that commit in its place.

1. A search prints every note that contains the word, oldest first, ignoring case.

   ```bash
   f=$(mktemp); printf '%s\n' 'Buy rope' 'call Sam' 'coil the ROPE' > "$f"
   NOTES_FILE=$f bin/notes search Rope </dev/null 2>&1; echo "exit $?"
   ```

   Done shows `Buy rope`, then `coil the ROPE`, then `exit 0`. Today: `usage: notes add <text> | notes list`,
   then `exit 2`.

2. The word is plain text, never a pattern or an option.

   ```bash
   f=$(mktemp); printf '%s\n' 'buy rope' 'r.pe is a pattern' 'pass -v to grep' > "$f"
   NOTES_FILE=$f bin/notes search r.pe </dev/null 2>&1; echo "exit $?"
   NOTES_FILE=$f bin/notes search -v </dev/null 2>&1; echo "exit $?"
   ```

   Done shows `r.pe is a pattern`, `exit 0`, `pass -v to grep`, `exit 0`. Today: the old usage line and `exit 2`,
   twice.

3. No match prints nothing and exits 1, and so does a notes file that doesn't exist.

   ```bash
   f=$(mktemp); printf '%s\n' 'buy rope' > "$f"
   NOTES_FILE=$f bin/notes search anchor </dev/null 2>&1; echo "exit $?"
   rm -f "$f"; NOTES_FILE=$f bin/notes search rope </dev/null 2>&1; echo "exit $?"
   ```

   Done shows `exit 1`, twice, and nothing else. Today: the old usage line and `exit 2`, twice.

4. A missing word exits 2 with the usage line, which names the new command. An empty word and a second word do
   the same.

   ```bash
   f=$(mktemp)
   NOTES_FILE=$f bin/notes search 2>&1 >/dev/null; echo "exit $?"
   NOTES_FILE=$f bin/notes search "" 2>&1 >/dev/null; echo "exit $?"
   NOTES_FILE=$f bin/notes search buy rope 2>&1 >/dev/null; echo "exit $?"
   ```

   Done shows `usage: notes add <text> | notes list | notes search <word>` and `exit 2`, three times. Today:
   `usage: notes add <text> | notes list` and `exit 2`, three times.

5. The gate passes and runs the four new tests.

   ```bash
   bash scripts/gate.sh; echo "exit $?"
   ```

   Done shows these nine lines. Four tests written to the list above gave this output against the throwaway
   build. Today: the first four lines and `exit 0`.

   ```text
   ok   test_add_then_list
   ok   test_list_empty
   ok   test_usage
   ok   test_completions_match
   ok   test_search_matches
   ok   test_search_plain_text
   ok   test_search_no_match
   ok   test_search_usage
   exit 0
   ```

6. The new tests fail against today's `bin/notes`, so none of them is hollow. The check copies the branch into
   a temporary folder, puts `main`'s `bin/notes` in the copy, and runs the copy's gate. It deletes nothing.

   ```bash
   d=$(mktemp -d); git archive HEAD | tar -x -C "$d"; git show main:bin/notes > "$d/bin/notes"
   bash "$d/scripts/gate.sh"; echo "exit $?"
   ```

   Done shows `ok` for `test_add_then_list`, `test_list_empty`, and `test_usage`, `FAIL` for
   `test_completions_match` and for each of the four search tests, and `exit 5`. The throwaway tests gave that
   result. Today, on `main`, it shows four `ok` lines and `exit 0`.

7. `add` and `list` behave as they do today. The repo's evidence for that is thin: item 5's first two lines are
   the only tests of them, and this check adds that the diff removes neither command's line from `bin/notes`
   and removes one line from `tests/run.sh`, the loop line it rewrites. The reviewer reads the rest of the
   `bin/notes` diff for a change to either command.

   ```bash
   git diff main...HEAD -- bin/notes | grep -c -E '^-  (add|list)\)'
   git diff main...HEAD -- tests/run.sh | grep -c '^-[^-]'
   ```

   Done shows `0`, then `1`. Today, on `main`, it shows `0`, then `0`.

8. Completion offers the new command.

   ```bash
   grep -c '^complete -W "add list search" notes$' completions/notes.bash
   ```

   Done shows `1`. Today: `0`.

9. The README names the new command.

   ```bash
   grep -c 'bin/notes search <word>' README.md
   ```

   Done shows `1`. Today: `0`. The reviewer reads the sentence against "What the session builds".

10. The pull request changes the four files and no other.

    ```bash
    git diff --name-only main...HEAD
    ```

    Done shows `README.md`, `bin/notes`, `completions/notes.bash`, `tests/run.sh`. Today, on `main`, it prints
    nothing.

The repo has no CI, so the output of item 5 on the last commit, quoted in the pull request, is the only full
run.

### The goal

The launching session puts the absolute path of this file in place of `<spec>`. `building-from-specs`
"Launching a task" owns the launch command.

```text
/goal Build the task notes-search from the spec at <spec>. It is done when all ten done items in that spec's
"Done items" hold on the branch's last commit, each shown by the check the spec names: (1) a search prints every
note that contains the word, oldest first, ignoring case; (2) the word is plain text, never a pattern or an
option; (3) no match and a missing notes file print nothing and exit 1; (4) a missing word, an empty word, and a
second word exit 2 with the usage line that names search; (5) the gate passes and runs the four new tests; (6)
the new tests fail against main's bin/notes; (7) add and list behave as today; (8) completion offers search; (9)
the README names the command; (10) the pull request changes only the four files; and the pull request is ready
with its review verdict, or stop after 80 minutes.
```

## Start conditions

`spec.md` is not committed, and a task's worktree starts from the remote's `main`, so the session can't find the
spec by a path inside its worktree. The goal names it by its absolute path in the main checkout. The spec stays
out of the pull request, which done item 10 enforces.

Two of the four launch checks couldn't run today: `claude-worktree-busy` is not on this session's `PATH`, and
the live session list is out of its reach. The launching session runs both at launch. The other two are
answered. The task needs no secret beyond the `gh` sign-in that pushes the branch, and CI can't block the task,
because the repo runs none on pull requests.

This checkout holds no `origin/main` ref:

```console
$ git rev-parse --verify origin/main
fatal: Needed a single revision
```

The launching session confirms that ref exists before it launches, since the worktree starts from it.

## Calls Claude made

The first two change what the brief settled. The next three are product calls with no precedent, and each took
the option a later commit undoes most cheaply.

1. `completions/notes.bash` joins the files. The gate can't pass without it, as the probe shows.
2. `README.md` joins the files, for one sentence. The other option was to leave the command undocumented.
   Reversing drops one sentence and done item 9.
3. More than one argument after `search` is a usage error. The other option was to join the arguments into a
   phrase, the way `add` joins its text. The brief says `<word>` where `add` says `<text>`, and a later commit
   can accept a phrase without breaking any call that works. A phrase still works today inside quotes.
4. An empty word, `bin/notes search ""`, counts as a missing word. The other option was to match every note,
   which is `list`.
5. A notes file that doesn't exist counts as no match: nothing printed, exit 1. The other option was exit 0, as
   `list` gives. No note contains the word, so the brief's rule for no match applies.
6. "Contains the word" means the word appears anywhere in the line, so `rope` finds `ropes`. Whole-word matching
   is a non-goal.
7. An unreadable notes file is left to `grep`: its message and exit status 2, with no test.
8. The match uses `grep -iF -e`, picked over a bash loop and `awk`.
9. The tests carry the four names in "What the session builds", so the gate's output shows that each one ran.
10. The untrue comment on `tests/run.sh:2` and the hand-kept test loop stay as they are. Making the loop find
    its own tests is work beyond this task, and the repo has no backlog file to hold it. It is named here for
    Geoff.
11. The task is planned at 40 minutes, and its session runs on Sonnet at medium effort.
12. The goal names the spec by absolute path, and the spec stays out of the pull request.
13. `~/.claude/docs/voice/written-for-people.md` couldn't be read from this session. This spec follows the shape
    rules in the `writing-voice` skill.
14. A word that holds a newline is left to `grep`, with no test. The other option was to count it as no match,
    since no one-line note can hold it.
15. Done item 6 was added after the fresh read, so that a test with an empty body can't pass the gate item.

One fresh reader, on Fable at high effort, read this spec with no context and reran its checks. It raised eight
points. None needed Geoff: every one was a minor call, and each is folded in above. They were the incomplete
strike instruction for the README, the voice file a session may not reach, the newline word, a done item for
`add` and `list` that couldn't fail, tests that could be hollow, a `FAIL` count that depended on an unstated
file, checks that named `main` without saying which commit, and usage checks that didn't set `NOTES_FILE`. It
found no departure from the brief that this spec leaves unnamed.
