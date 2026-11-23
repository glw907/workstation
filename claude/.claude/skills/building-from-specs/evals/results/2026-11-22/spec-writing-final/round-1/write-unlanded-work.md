# Spec: notes search

This spec adds `bin/notes search <word>` as one task that ends in one pull request. It follows the design in
`brief.md`, which Geoff approved in conversation. One thing waits for Geoff: the brief says search prints in the
format `notes export` uses, and no `notes export` exists in the code this spec was written against. The task
does not launch until `notes export` is on `origin/main`. "For Geoff" at the end says how to unblock it.

Written 2026-11-22 against commit `e3473df` on `main`, the only commit and the only branch in this checkout.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is one new command that prints the notes containing a word, in a form a script can read the same way
it reads `notes export`. The non-goals are patterns, whole-word matching, several words at once, a README
change, and any change to what `add`, `list`, or `export` print. The work has failed if search treats the word
as a pattern, if its output differs from export's for the same notes, or if a no-match exits with anything
other than 1.

## `notes export` has not landed

The brief settles the output format by pointing at `notes export`. Nothing in this checkout defines it.

- `grep -rn 'export' bin scripts tests README.md` has 0 hits.
- `bin/notes export` prints `usage: notes add <text> | notes list` and exits 2.
- The checkout holds 1 local branch, 0 remote-tracking refs, 0 stashes, and 1 worktree, so no unmerged export
  work is here either.
- The remote is unread. The writing session's sandbox refused the network: `git ls-remote origin` ended with
  "CONNECT tunnel failed, response 403". Export may be on `origin/main`, in an open pull request, or nowhere.
- `task-report` lists no export task. It does list pull request 18, "Let notes add read stdin", and `add` at
  `e3473df` reads only its arguments. The report gives that pull request's minutes and not its state, so
  either it is unmerged or this checkout is behind the remote.

The spec does not guess the format, and it does not add export. A task that needs another task's work waits
until that work has merged (`building-from-specs`, "Launching a task"), so this task waits for export. The done
items compare search with what `notes export` prints on the task's base and copy no format into this spec.

### Start conditions

These add to the four checks in `building-from-specs` "Launching a task". Condition 1 was run against this
checkout and fails. Condition 2 and the four launch checks need the remote, `claude-worktree-busy`, and the
session list, which the writing session could not reach, so the launching session tests them on the day.

1. `notes export` is on `origin/main`, and its output depends only on the notes. From an up-to-date main
   checkout this prints `exit 0`, `exit 0`, and `stable`:

   ```bash
   m=$(mktemp); printf 'Buy rope\nCoil the ROPES\n' > "$m"; m2=$(mktemp); cp "$m" "$m2"
   NOTES_FILE=$m bin/notes export > "$m.1"; echo "exit $?"
   NOTES_FILE=$m2 bin/notes export > "$m.2"; echo "exit $?"
   [ -s "$m.1" ] && cmp "$m.1" "$m.2" && echo stable
   ```

   Today it prints the usage line and `exit 2` twice, and no `stable`. If it prints `exit 0` twice and no
   `stable`, export's output is empty or carries the file's path or the time. Done items 1 and 2 can't be met
   then, and the spec goes back to Geoff instead of launching.
2. No open pull request on `example/notes` changes `bin/notes` or `tests/run.sh`. Such a pull request edits
   the `case` block and the test list that this task edits, so it merges or closes first. Check pull request
   18.
3. The goal names this spec by absolute path. `spec.md` is uncommitted, so a fresh worktree does not hold it.

## Behavior

A note is one line of `$NOTES_FILE`, as the README has it. Search reads the file and never writes it.

| Call | Standard output | Standard error | Exit |
| --- | --- | --- | --- |
| `notes search <word>`, one or more notes contain the word | Those notes, oldest first, in export's format | Nothing | 0 |
| `notes search <word>`, no note contains it | Nothing | Nothing | 1 |
| `notes search <word>`, the notes file doesn't exist | Nothing | Nothing | 1 |
| `notes search` with no word, an empty word, or more than one argument | Nothing | The usage line | 2 |

A note contains the word when the word appears anywhere in the note's own text, so `rope` finds `ropes`. The
match ignores case and reads every character of the word literally, including `.`, `*`, and a leading `-`. A
word with spaces works when the shell passes it as one argument. A word that holds a line break is a no-match,
because no one-line note can contain it. The match runs on the note's text, never on text that export's format
adds around it.

"Export's format" means this: when at least one note matches, search prints, byte for byte, what `notes
export` prints for a notes file that holds only the matching notes in their original order. A script that
reads one reads the other. When nothing matches, the brief's rule governs and search prints nothing, whatever
export prints for an empty file.

The usage line is the one line `bin/notes` already prints for a bad call. It gains `notes search <word>` and
keeps every command it names on `origin/main`.

## Approaches

- `grep -aiF -- "$word" "$file"`, the pick. Fixed strings and case folding are grep's own flags, and grep
  already exits 0 for a match and 1 for none. It needs three guards: the missing file (grep exits 2), the empty
  word (grep matches every line), and the line break (grep splits the word into two words).
- A bash loop comparing `${line,,}` with `*"${word,,}"*`. It starts no second process, needs bash 4 or later,
  and is more code to get wrong.
- `awk` with `index(tolower($0), tolower(word))`. It is plain text by construction, but `-v` expands
  backslashes in the word, so the word must travel through `ENVIRON`.

How search reaches export's format is the builder's call: shared code, or a call to export on the matching
notes. Either way `test_search_matches_export` compares the two live, so they can't drift, and done item 6
pins export's own output.

## When it goes wrong

- A missing notes file is a no-match: nothing printed, exit 1. `list` already treats a missing file as empty.
- An unreadable notes file ends with the system's error message and a non-zero exit. No done item covers it.
- A note with a byte that isn't valid text is still searched, because of `-a`. Without it grep stops at
  "binary file matches" and drops later matches. No done item covers it.
- Letters outside ASCII fold case as `grep -i` folds them in the caller's locale. The tests use ASCII.
- The work adds no limit. Search reads the file once.
- Every test sets `NOTES_FILE` to a `mktemp` path. A test that forgets reads or writes Geoff's `~/.notes`.
- `tests/run.sh` runs a fixed list of names (line 15 at `e3473df`), though its comment says it runs every
  `test_*` function. A test left out of the list never runs and the gate still passes. Done item 5 names the
  tests it must see.
- If a push or a `gh` call is refused in the task session, `building-from-specs` "In place of a question"
  says what the session does.

## Sources

No Claude Code mechanism is proposed, so no Anthropic docs page applies. The work adds no service and cuts no
release. Only one task exists, so the one assumption is start condition 1.

- `grep -aiF`: documented. `grep --help` (GNU grep 3.12, this workstation) says "-F, --fixed-strings PATTERNS
  are strings", "-i, --ignore-case ignore case distinctions in patterns and data", and "-a, --text equivalent
  to --binary-files=text". Probes, on the four-note file the goal uses:
  - `rope` printed `Buy rope` and `Coil the ROPES`. Each of `.`, `a.b*`, `-x`, and `50 (a` printed only the
    price note.
  - An empty word matched every line. The word `tent`, a line break, `zzz` printed `fix the tent`.
  - A missing file gave "No such file or directory", exit 2.
  - On a file holding `Buy rope` and a second `rope` line with byte 0xFF, `grep -iF` printed one line and
    "binary file matches". `grep -aiF` printed both.
- Search as a whole: assembled from documented pieces.
- Export's format: no label. It has no source in this checkout, which is why the task waits.

## Files

Two searches, run at `e3473df`. `grep -rn 'export' bin scripts tests README.md` has 0 hits.
`grep -rnE 'notes (add|list)|usage' bin scripts tests README.md` has 8 hits:

- `bin/notes:7`, the usage line: changed.
- `tests/run.sh:7`, `:10`, `:12`, `:13`, the three existing tests: not changed. `test_usage` checks only that
  the line starts with `usage:`, so it still passes.
- `tests/run.sh:15`, the test list: changed.
- `README.md:3` and `:4`, the description of `add` and `list`: dismissed. The brief settles the files as
  `bin/notes` and `tests/run.sh`.

The task's base will differ from `e3473df`, since it holds export at least. The task session runs both
searches again on its base before its first edit. It changes hits only in `bin/notes` and `tests/run.sh`, and
it names any other hit in the pull request. `scripts/gate.sh` runs `tests/run.sh` and needs no change.

## Commands and the denials log

The task runs `bin/notes`, `bash scripts/gate.sh`, `mktemp`, `printf`, `cp`, `cmp`, `rm -f` on one temp file,
`git` on the branch it creates, and `gh` for its pull request. The denials log holds three entries since
2026-10-23, and none matches: a forced push to `main` (the task pushes only its own branch, never forced), a
recursive delete under the home folder (the task deletes one `mktemp` file at most, as `test_list_empty`
already does), and a WebFetch to an unknown host (the task fetches nothing).

## Task: notes-search

Add the `search` command to `bin/notes` and its tests to `tests/run.sh`.

- Waits for: the work that adds `notes export`, merged to `origin/main`. This spec found no spec, task, or
  pull request for that work.
- Files: `bin/notes`, `tests/run.sh`.
- Reviewer: `standards:diff-reviewer`. Search only reads the notes file and renders no UI, so no second
  reviewer.
- Session: Opus at high effort.
- Minutes: 45. The like tasks in `task-report --since 2026-11-01` are the two that added behavior with tests.
  Both were planned at 30 and ran over: "Add notes list" took 34 and "Let notes add read stdin" took 41 with
  one fix round. Search has more cases than either. "Add the usage test", at 12, added a test and no behavior.
  The repo runs no CI on pull requests (`.workstation/remote.txt`), so nothing adds a wait. The goal's time
  clause is `or stop after 90 minutes`.
- Merge order: after the export work and after any open pull request that changes the same two files. Nothing
  waits on this task.

### Goal

Each check was run at `e3473df` on 2026-11-22, and its output then is beside it. Items 1, 2, and 6 fail today
partly because export is missing, so their passing output has not been seen on any code. Start condition 1
covers that half. Items 1 to 4 and 6 share this setup:

```bash
f=$(mktemp); printf 'Buy rope\nfix the tent\nCoil the ROPES\nprice: 3.50 (a.b*) -x\n' > "$f"
m=$(mktemp); printf 'Buy rope\nCoil the ROPES\n' > "$m"
p=$(mktemp); printf 'price: 3.50 (a.b*) -x\n' > "$p"
```

1. Search prints every note that contains the word, oldest first, ignoring case, in export's format. This
   prints `exit 0`, `exit 0`, and `same`:

   ```bash
   NOTES_FILE=$f bin/notes search rope > "$f.out"; echo "exit $?"
   NOTES_FILE=$m bin/notes export > "$m.out"; echo "exit $?"
   [ -s "$f.out" ] && cmp "$f.out" "$m.out" && echo same
   ```

   Today: the usage line and `exit 2` twice, and no `same`.

2. The word is plain text, never a pattern. Each of four words finds only the price note. This prints
   `exit 0`, then `exit 0` and `same` four times:

   ```bash
   NOTES_FILE=$p bin/notes export > "$p.out"; echo "exit $?"
   for w in . 'a.b*' -x '50 (a'; do
     NOTES_FILE=$f bin/notes search "$w" > "$f.out"; echo "exit $?"
     [ -s "$f.out" ] && cmp "$f.out" "$p.out" && echo same
   done
   ```

   Today: the usage line and `exit 2` five times, and no `same`.

3. No match prints nothing and exits 1. So does a word with a line break, and so does a notes file that
   doesn't exist. Each line prints only `exit 1`:

   ```bash
   NOTES_FILE=$f bin/notes search zzz 2>&1; echo "exit $?"
   NOTES_FILE=$f bin/notes search $'tent\nzzz' 2>&1; echo "exit $?"
   NOTES_FILE=$f.missing bin/notes search rope 2>&1; echo "exit $?"
   ```

   Today: each prints the usage line and `exit 2`.

4. A missing word exits 2 with the usage line on standard error, and the usage line names the new command.
   The first three lines each print one line that starts with `usage:` and then `exit 2`. The last prints `1`:

   ```bash
   NOTES_FILE=$f bin/notes search 2>&1 >/dev/null; echo "exit $?"
   NOTES_FILE=$f bin/notes search '' 2>&1 >/dev/null; echo "exit $?"
   NOTES_FILE=$f bin/notes search buy rope 2>&1 >/dev/null; echo "exit $?"
   NOTES_FILE=$f bin/notes search 2>&1 >/dev/null | grep -c 'notes search <word>'
   ```

   Today: the last line prints `0`, and that is the line the task fixes. The first three already print
   `usage: notes add <text> | notes list` and `exit 2`, because every unknown call does. They are here so the
   new command keeps that result.

5. The gate passes on the branch's last commit and runs the new tests. The first line prints an `ok` line for
   every test, no `FAIL` line, and `exit 0`. The second prints `5`:

   ```bash
   bash scripts/gate.sh; echo "exit $?"
   bash scripts/gate.sh | grep -cE '^ok   test_search_(matches_export|plain_text|no_match|missing_file|usage)$'
   ```

   `test_search_matches_export` holds item 1, `test_search_plain_text` item 2, `test_search_no_match` the
   first two lines of item 3, `test_search_missing_file` its third, and `test_search_usage` item 4. More
   `test_search_` tests are welcome. Every test is in the list that the loop runs.

   Today: three `ok` lines and `exit 0`, and the count prints `0`.

6. The branch changes only `bin/notes` and `tests/run.sh`, and export prints what it printed before. The
   first line prints those two paths and no other. The rest prints `exit 0`, `exit 0`, and `unchanged`:

   ```bash
   git diff --name-only origin/main...HEAD
   git show origin/main:bin/notes > "$m.base"
   NOTES_FILE=$f bash "$m.base" export > "$m.before"; echo "exit $?"
   NOTES_FILE=$f bin/notes export > "$m.after"; echo "exit $?"
   [ -s "$m.after" ] && cmp "$m.before" "$m.after" && echo unchanged
   ```

   Today: this checkout has no `origin/main` ref, so the first line ends with "fatal: ambiguous argument".
   Run with `main` in its place, the first line prints nothing, and the rest prints the usage line and
   `exit 2` twice and no `unchanged`. The task's worktree starts from the remote's default branch
   (`building-from-specs`, "Launching a task"), so the ref is there.

7. The pull request is marked ready with the gate's output on the last commit quoted in it and an accept
   verdict from the reviewer. `building-from-specs` "Gates and review" and "The pull request" own the steps
   and the body.

## Backlog sweep

The scoped sweep has nothing to read. A glob for `*backlog*`, `*BACKLOG*`, `*TODO*`, and `*STATUS*` across the
repo has 0 hits, and none of the five tracked files is a backlog. No full sweep is due with 0 open items.
There are no verdicts and no backlog edits to approve.

## Fresh read

One reader with no context read this spec on 2026-11-22 and returned 15 findings. One was answered already:
the skill sections that item 7 and the start conditions name do exist. One is Geoff's alone: where `notes
export` is. The other thirteen were minor calls, made in the text. Those that changed a call are marked
(reader) in the list below. The reader reran the first draft's searches, probes, and "Today" outputs, and they
matched. The writing session reran every check that changed after that read. The spec has had no second read.

## Claude's calls

Each of these is a call the brief left open. Geoff can overturn any of them before approval.

1. The task waits for `notes export` to merge. It invents no format and doesn't add export itself.
2. "The format `notes export` uses" is read as: search's output equals export's output for a file holding only
   the matching notes. If export numbers its notes, search numbers the matches from the start. The reading
   fails only if export's output depends on something besides the notes, and start condition 1 tests for
   that (reader).
3. "Contains the word" is read as a substring. `rope` finds `ropes`.
4. A notes file that doesn't exist is a no-match with exit 1, as `list` treats it as empty.
5. An empty word is a missing word, because an empty string matches every note.
6. More than one argument is a usage error with exit 2. `add` joins its arguments, and search could have done
   the same. The strict form was taken because turning an error into a behavior later breaks no script, and
   the reverse would.
7. A word with a line break is a no-match with exit 1, never a usage error (reader).
8. "Prints nothing" on no match covers standard error as well as standard output.
9. The match runs on the note's own text, never on export's added text.
10. Search passes `-a` to grep, so a stray byte in the notes file hides no match (reader).
11. The builder chooses how search reaches export's format. Export's output must not change, and done item 6
    checks it (reader).
12. Five tests are named, and the builder may add more (reader).
13. The README stays unchanged, by the brief's file list. After this task it still describes only `add` and
    `list`, unless the export work changed it.
14. The test list in `tests/run.sh` stays a fixed list. Making it find tests by itself is outside the brief.
15. The minutes are 45, the session is Opus at high effort, and the one reviewer is `standards:diff-reviewer`.
16. The task doesn't launch while an open pull request changes either of its two files.
17. The task session reruns the file searches on its own base, because this checkout may be stale (reader).

## For Geoff

- Where is `notes export`? If its work is merged or in flight, the task launches once the start conditions
  pass. If export is still to be designed, it needs its own spec first. If you meant `notes list`, say so and
  the spec is revised to compare against `list` before it launches. That version's checks all run on today's
  code.
- The README won't mention `search` (call 13).
- Start condition 2 and the four launch checks were not tested on the day this was written.
