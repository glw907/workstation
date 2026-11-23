# Spec: notes search

Written 2026-11-22 from `brief.md`, against `main` at 399e8de. One task, one pull request.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is a new command, `bin/notes search <word>`, that prints every note containing the word, oldest
first. The non-goals are patterns, whole-word matching, searching for several words at once, any change to
`add` or `list`, and any file beyond `bin/notes` and `tests/run.sh`.

The work is a failure if any of these is true:

- A one-line word acts as a pattern or as an option to the tool underneath.
- A test or a check reads or writes `~/.notes`.
- The new tests exist but the gate never runs them. The loop at `tests/run.sh:15` is a fixed list of names,
  so a test left out of it passes by never running.
- `add` or `list` behaves differently afterward.

## Behavior

The first three rows are the brief's. The fourth is today's behavior with the new usage line. The last three
are edges the brief leaves open, decided here and listed under [Calls Claude made](#calls-claude-made).

| Case | Standard output | Standard error | Exit |
| --- | --- | --- | --- |
| One or more notes contain the word | Each matching line, whole and unchanged, in file order | Nothing | 0 |
| No note contains the word | Nothing | Nothing | 1 |
| No word given | Nothing | The usage line | 2 |
| Any other unknown command | Nothing | The same usage line | 2 |
| The notes file doesn't exist, or is empty | Nothing | Nothing | 1 |
| The word is the empty string, `search ""` | Nothing | The usage line | 2 |
| More than one argument, `search buy rope` | Nothing | The usage line | 2 |

- A note contains the word when the word's characters appear anywhere in its line, so `rope` finds
  `Mend the ROPES`. Case is ignored on both sides.
- Every character of a one-line word is literal, so `a.c` doesn't find `abc`, and `-i` finds `use -i here`.
  One quoted argument with a space in it, `search "buy rope"`, is one word.
- File order is oldest first, because `add` only appends (`bin/notes:5`).
- The script prints one usage line, and it becomes exactly
  `usage: notes add <text> | notes list | notes search <word>`.

## Approach

Three ways to match were probed on 2026-11-22 against the goal's fixture with the word `Rope`. Each printed
`buy rope` and `Mend the ROPES`.

| Option | Label | Trade-off |
| --- | --- | --- |
| `grep -F -i -e "$word" -- "$file"` | Documented: GNU grep 3.12 `man grep`, quoted below | One line, and its exit status is already the brief's 0 and 1. A missing file exits 2, so an exists test goes in front. |
| A bash loop over `[[ ${line,,} == *"${word,,}"* ]]` | Documented: `man bash`, "Case modification" | No second process, but the exit status is built by hand. |
| `awk 'index(tolower($0), tolower(ENVIRON["W"]))'` | Assembled from documented awk functions | The exit status is built by hand: it exits 0 with or without a match. |

The pick is `grep`, behind a test that the file exists. `man grep` says of `-F`: "Interpret PATTERNS as fixed
strings, not regular expressions." Of `-i`: "Ignore case distinctions in patterns and input data". Of `-e`:
"This option can be used to protect a pattern beginning with “-”." Of its status: "the exit status is 0 if a
line is selected, 1 if no lines were selected, and 2 if an error occurred."

The work uses no Claude Code mechanism beyond the `building-from-specs` flow, and adds no project, service,
or running infrastructure.

## When it goes wrong

- The exit codes are the only limits: 0 for a match, 1 for none, 2 for usage. There is no size limit,
  because `grep` reads the file as a stream.
- Three cases are outside this task, left as `grep` does them, with no test. A notes file that exists but
  can't be read prints `grep`'s error and exits 2. A word that contains a newline is read as two words.
  Case outside ASCII folds by the caller's locale.

## Files

The searches ran over tracked files, leaving out `brief.md`. Only this one task rests on them.

- `git grep -n usage`: 4 hits. `bin/notes:7` changes: it is the usage line. `tests/run.sh:12` and `:13` are
  `test_usage`, which stays as is: it checks only the first word, `usage:`, so it still passes.
  `tests/run.sh:15` is the loop, which changes.
- `git grep -n -e 'notes list' -e 'notes add'`: 5 hits. `bin/notes:7` is the same line. `tests/run.sh:7` and
  `:10` are the `add` and `list` tests, which stay. `README.md:3` and `:4` describe `add` and `list`, stay
  true, and are not in this task: see call 6.
- `git grep -n test_`: 5 hits, all in `tests/run.sh`. Line 15, the loop, gains the five new names. Lines 6,
  9, and 12 are the existing tests and line 2 is the header comment. Those four stay.
- `git grep -n -i search`: 0 hits. Nothing in the repo uses the name yet.

The repo has no backlog file: `git ls-files` lists five files and none is one. The scoped
`standards:backlog-sweep` has no item to read and no verdict to list, and no full sweep is due.

## Commands and the denials log

`.workstation/denials.log` holds three refusals since 2026-10-23: a force push to `main`, `rm -rf` on a path
outside the working folder, and a web fetch of an unknown host. The task runs `bash scripts/gate.sh`,
`bin/notes`, `mktemp`, `printf`, `git diff`, and the commit, push, and pull request steps that the skill
owns. None of those matches a refusal, as long as no test or step runs `rm -r`. The task needs nothing from
the web.

## Task: notes-search

**Files:** `bin/notes`, `tests/run.sh`. The session adds neither `spec.md` nor any other file to its branch.

**Tests:** five new functions in `tests/run.sh`, each added to the loop on line 15 after the three existing
names. Each test sets `NOTES_FILE` to a path that `mktemp` made. A test that needs a missing file removes
that one file with `rm -f` first, as `test_list_empty` does today. Each test asserts everything its done
items state: the exact standard output, the exact standard error or its emptiness, and the exit status.

| Test | Asserts |
| --- | --- |
| `test_search_match` | Done item 1 |
| `test_search_plain_text` | Done items 2 and 3, all three commands |
| `test_search_no_match` | Done item 4 |
| `test_search_no_file` | Done item 5, both commands |
| `test_search_usage` | Done item 6, all four commands |

**Goal.** Every check below ran on 2026-11-22 at 399e8de. Items 1 to 6 use this fixture:

```bash
f=$(mktemp); printf '%s\n' 'buy rope' 'call mum' 'Mend the ROPES' 'fix a.c' 'abc' 'use -i here' > "$f"
```

Today each command in items 1 to 6 prints `usage: notes add <text> | notes list` and then `exit 2`.

1. Search finds every note that contains the word, in any case, oldest first.
   `NOTES_FILE=$f bin/notes search Rope; echo "exit $?"` prints `buy rope`, `Mend the ROPES`, `exit 0`.
2. The word is plain text, with or without a space in it.
   `NOTES_FILE=$f bin/notes search a.c; echo "exit $?"` prints `fix a.c`, `exit 0`.
   `NOTES_FILE=$f bin/notes search "buy rope"; echo "exit $?"` prints `buy rope`, `exit 0`.
3. A word that starts with a dash is still a word.
   `NOTES_FILE=$f bin/notes search -i; echo "exit $?"` prints `use -i here`, `exit 0`.
4. No match prints nothing and exits 1.
   `NOTES_FILE=$f bin/notes search zebra; echo "exit $?"` prints only `exit 1`.
5. A missing or empty notes file is no match. Each of these prints only `exit 1`:

   ```bash
   NOTES_FILE=$f.gone bin/notes search rope; echo "exit $?"
   NOTES_FILE=$(mktemp) bin/notes search rope; echo "exit $?"
   ```

6. A missing word, an empty word, a second argument, and an unknown command each send the new usage line to
   standard error and exit 2. Each of these prints
   `usage: notes add <text> | notes list | notes search <word>`, `exit 2`:

   ```bash
   NOTES_FILE=$f bin/notes search 2>&1 >/dev/null; echo "exit $?"
   NOTES_FILE=$f bin/notes search "" 2>&1 >/dev/null; echo "exit $?"
   NOTES_FILE=$f bin/notes search buy rope 2>&1 >/dev/null; echo "exit $?"
   NOTES_FILE=$f bin/notes bogus 2>&1 >/dev/null; echo "exit $?"
   ```

7. The gate passes and runs the new tests. `bash scripts/gate.sh; echo "exit $?"`, run on the branch's last
   commit, prints the eight lines below and `exit 0`. Today it prints the first three and `exit 0`.

   ```text
   ok   test_add_then_list
   ok   test_list_empty
   ok   test_usage
   ok   test_search_match
   ok   test_search_plain_text
   ok   test_search_no_match
   ok   test_search_no_file
   ok   test_search_usage
   ```

8. The branch changes the two files and no other. `git diff --name-only main...HEAD` prints `bin/notes` and
   `tests/run.sh`. Today it prints nothing.

The repo runs no CI on pull requests (`.workstation/remote.txt`), so the item 7 run on the last commit is
the branch's only full run. The pull request quotes that run and waits on no check. The session then
follows the skill's "Gates and review" and "The pull request".

**Reviewer:** `standards:diff-reviewer`. The task reads one local file, writes none, and renders no UI, so it
needs no second reviewer.

**Minutes:** 40. `task-report` gives two like tasks in this repo: "Add notes list", a new command, measured
34 minutes, and "Let notes add read stdin" measured 41 with one fix round. The task drives no CI, timer, or
idle limit, so nothing is added for waits. The time clause is `or stop after 80 minutes`.

**Model:** Opus at medium effort for the task session.

**Order:** the task waits for nothing, and its pull request is the only merge.

## Before launch

- `spec.md` is uncommitted, because the sitting that wrote it was told to commit nothing. The task's
  worktree starts from `main` on `origin`, so `spec.md` has to reach `origin`'s `main` before the launch, or
  the task session can't read it.
- The start conditions were not tested against today's live sessions: `claude-worktree-busy` and
  `task-report` are not installed where this spec was written. The minutes come from
  `.workstation/task-report.txt`, and the launch checks in the skill's "Launching a task" are still owed.
  The task needs no secret.

## Calls Claude made

Calls 1 to 6 are product calls Geoff would normally have been asked. Each takes the option a later commit
undoes most cheaply.

1. A missing or empty notes file is no match, exit 1, because `list` already treats a missing file as an
   empty list. Passed over: exit 0.
2. "Contains" means anywhere in the line, so `rope` finds `ROPES`. Passed over: whole-word matching.
3. An empty word counts as a missing word, exit 2. Passed over: matching every note.
4. A second argument is a usage error, exit 2, because allowing it later breaks nobody's use. Passed over:
   joining the arguments into a phrase, as `add` does.
5. The usage line reads `usage: notes add <text> | notes list | notes search <word>`.
6. `README.md` stays unchanged, because the brief names the two files, so it won't mention `search`. One
   sentence there fits the skill's "Direct changes" if Geoff wants it.
7. Method calls, each stated where it applies: `grep` behind an exists test, the five fixed test names, the
   three cases left as `grep` does them, 40 minutes, and Opus at medium effort.
8. Done item 8 compares against local `main`, because this checkout has no `origin/main` ref.
