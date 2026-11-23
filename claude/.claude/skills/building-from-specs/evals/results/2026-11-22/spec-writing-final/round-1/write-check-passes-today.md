# Spec: notes search

Written 2026-11-22 from `brief.md`, against commit `7115ad0` of example/notes. The work is one task,
`notes-search`, and ends in one pull request. Nobody could answer questions while this was written, so each
reading the brief left open is closed here and listed under "Calls Claude made".

## Intent

Geoff said: "I want to find a note without scrolling through the whole list."

The goal is one new command, `bin/notes search <word>`, that prints the notes containing the word. Patterns,
whole-word matching, flags, highlighting, and any change to what `add` or `list` do are not goals.

The work has failed if any of these happens: the word is read as a pattern, so that `a.c` finds `abc`; `add` or
`list` behaves differently than it does today; a new test is defined and never runs; or a test or check reads or
writes the real `~/.notes`.

## What search does

| Call | Output | Exit |
| --- | --- | --- |
| `bin/notes search <word>`, and one or more notes contain the word | Each such note on stdout, the whole line as stored, in file order, which is oldest first | 0 |
| No note contains the word, or `$NOTES_FILE` doesn't exist | Nothing on stdout or stderr | 1 |
| No word, or an empty word | The usage line on stderr, nothing on stdout | 2 |

A note contains the word when the word's text appears anywhere in the line, so `rope` finds `ropes`. The match
ignores case. The word is plain text: `.`, `*`, `[`, and a leading `-` match only themselves. Arguments after
`search` are joined with single spaces, as `add` joins them, so `bin/notes search buy rope` looks for
`buy rope`.

Search checks the word before it looks at the notes file. A missing or empty word exits 2 with the usage line
whether or not the file exists.

The usage line becomes `usage: notes add <text> | notes list | notes search <word>`. An unknown command prints
the same line, as it does today.

## Approach

Three ways to match were weighed. The pick is `grep -i -F -e <word>` on the notes file.

- `grep -i -F -e` is one line, and its exit codes for a match and for no match are the brief's 0 and 1. It exits
  2 when the file is missing, which is the usage code, so search checks that the file exists before it runs
  `grep`, as `list` does, and after it has checked the word.
- A Bash loop that lowercases each line and the word needs no outside command. It is more lines, and it has to
  track the exit code itself.
- `awk -v w=<word>` with `index(tolower($0), tolower(w))` changes the word before it matches. The probe
  `awk -v w='a\.c' 'BEGIN{print w}'` printed `a.c` with a warning, so a backslash in the word is lost.

## When it goes wrong

Search has no limit to number: no size cap, timeout, or retry. Three cases stay as `grep` leaves them, and no
done item covers them.

- A notes file that exists and can't be read prints `grep`'s own message and exits 2.
- Case folding outside ASCII follows the locale `grep` runs in. The tests use ASCII.
- A word that holds a newline is read by `grep -F` as two words, either of which matches.

## Sources

`grep`'s flags are documented. `grep --help` on GNU grep 3.12 prints "-F, --fixed-strings PATTERNS are
strings", "-i, --ignore-case ignore case distinctions in patterns and data", and "-e, --regexp=PATTERNS use
PATTERNS for matching". `man grep` says: "Normally the exit status is 0 if a line is selected, 1 if no lines
were selected, and 2 if an error occurred."

A probe on 2026-11-22 ran `grep -i -F -e <word> <file>` on a file holding `Buy rope`, `call Ann`,
`ROPE is 30 m`, `abc`, `a.c`, and `x -v y`. The word `rope` printed `Buy rope` and `ROPE is 30 m` and exited 0.
`a.c` printed only `a.c`. `-v` printed only `x -v y`. `zebra` printed nothing and exited 1. A missing file
printed "No such file or directory" and exited 2. An empty word printed all six lines, which is why an empty
word counts as a missing one.

The work adds no Claude Code mechanism. The launch, the review, and the pull request follow
`building-from-specs`.

Only one task rests on these facts, so no assumption is shared between tasks.

## Files

The task changes `bin/notes`, `tests/run.sh`, and `README.md`, and nothing else. The searches below ran on
`7115ad0`, where `spec.md` is not tracked. If `spec.md` is ever committed, its own text adds hits to each.

`git grep -n -e 'usage' -e 'notes add' -e 'notes list' -e 'list)' -e 'add)' -- . ':!brief.md'` finds every
place that names a command. It has 10 hits.

- `README.md:3` and `README.md:4` describe `add` and `list`. The sentence on search joins them.
- `bin/notes:5` and `bin/notes:6` are the `add` and `list` branches. The `search` branch joins them, and they
  stay as they are.
- `bin/notes:7` is the usage line. It changes.
- `tests/run.sh:7` and `tests/run.sh:10` are the `add` and `list` tests. Dismissed: they stay as they are.
- `tests/run.sh:12` and `tests/run.sh:13` are `test_usage`. Dismissed: it checks only the first word,
  `usage:`, and still passes.
- `tests/run.sh:15` is the loop's list of tests. The four new names go on it.

`git grep -n 'test_'` has 5 hits, all in `tests/run.sh`: the comment on line 2, the three definitions on lines
6, 9, and 12, and the loop on line 15. The loop runs only the names on its list, so a test left off it never runs.

`scripts/gate.sh` runs `tests/run.sh` and needs no change. `brief.md` and `spec.md` stay as they are.

The repo has no backlog. `git ls-files | grep -ic -e backlog -e todo -e status` printed 0, and
`git grep -n -i -e backlog -e todo` had 0 hits, so the scoped sweep has no item to read and no verdict to list.

## Commands and the denials log

The task runs `bash scripts/gate.sh`, `bin/notes` with `NOTES_FILE` set, `grep -c`, `git diff`,
`git rev-parse`, a commit of three files staged by name, and a push of its own branch. The pull request's
commands are owned by `building-from-specs`, "The pull request".

`.workstation/denials.log` has three refusals since 2026-10-23, and none is a command the task runs.

- `git push --force origin main` on 2026-11-03, a force push to the default branch. The task pushes only the
  branch it made, with no force flag.
- `rm -rf ~/.notes.bak` on 2026-11-09, a recursive delete outside the working folder. The task deletes nothing
  outside its worktree. Its temp files come from `mktemp` and are left for the system, as the existing tests
  leave theirs.
- A WebFetch of `https://example.invalid/notes` on 2026-11-17, an unknown host. The task fetches nothing: the
  `grep` facts it needs are quoted under "Sources".

## Start conditions, tested 2026-11-22

- `claude agents --json` printed `[]`, so no other session is working.
- `git status` showed a clean checkout of `main` at `7115ad0`.
- The task needs no secret.
- The repo is public and runs no CI. `.workstation/remote.txt` gives `"visibility":"PUBLIC"`, default branch
  `main`, and "The repo runs no CI on pull requests, so the gate on a branch's last commit is its only full
  run." The task waits on no CI run.
- `claude-worktree-busy` is not on the PATH of the session that wrote this spec, so it was not run. The
  launching session runs it, per `building-from-specs`, "Launching a task".
- `spec.md` is not committed. `git cat-file -e HEAD:spec.md` exited 128. The task's worktree starts from the
  remote's `main` and so holds no copy, and the task session reads the spec by its absolute path in the main
  checkout. The file has to stay there, unchanged, until the task's session ends.

## Task: notes-search

Files: `bin/notes`, `tests/run.sh`, `README.md`. It waits for no other task, and with one pull request there is
no merge order to give.

The launch follows `building-from-specs`, "Launching a task", with the name `notes-search`, the model Opus, and
the effort high. The condition names `spec.md` by its absolute path in the main checkout, names this task, lists
done items 1 to 7 word for word, and ends `or stop after 80 minutes`. The reviewer's brief gives the same path.

Reviewer: `standards:diff-reviewer` on Opus at high. Search only reads the notes file and touches no sign-in, so
no second reviewer reads it. Nothing renders, so no visual reviewer does either.

Minutes: 40. `task-report --since 2026-11-01` gives two like tasks in this repo: pull request 12, "Add notes
list", planned 30 and measured 34 with no fix round, and pull request 18, "Let notes add read stdin", planned 30
and measured 41 with one fix round. Pull request 15, "Add the usage test", planned 15 and measured 12, is
dismissed: it added one test and no command. Search carries more cases than `list` did, so the estimate sits
at the top of that range. Nothing the task drives adds a wait, since the repo has no CI.

### Tests

Each new test points `NOTES_FILE` at a file from `mktemp`, as the existing tests do, and goes on the loop's list
at `tests/run.sh:15`.

| Test | What it asserts |
| --- | --- |
| `test_search_match` | A word finds notes that differ from it in case, prints them in file order, leaves out the others, and exits 0. Two arguments are joined with a space. |
| `test_search_plain_text` | `a.c` finds `a.c` and leaves out `abc`. A word that starts with `-` matches as text. |
| `test_search_no_match` | A word in no note prints nothing and exits 1. So does any word when the notes file doesn't exist. |
| `test_search_usage` | `search` with no word, and with an empty word, exits 2, prints nothing on stdout, and prints a usage line on stderr that holds `notes search <word>`. |

### Done items

Every command below ran twice on commit `7115ad0` on 2026-11-22. The two runs printed the same output, which is
given as "Today". Each check sets `NOTES_FILE`, so none touches `~/.notes`. Run them from the root of the
worktree.

1. Search prints the notes that contain the word, ignoring case, oldest first.

   ```bash
   f=$(mktemp); printf '%s\n' 'Buy rope' 'call Ann' 'ROPE is 30 m' > "$f"
   NOTES_FILE=$f bin/notes search rope; echo "exit $?"
   NOTES_FILE=$f bin/notes search buy ROPE; echo "exit $?"
   ```

   Done: prints `Buy rope`, `ROPE is 30 m`, `exit 0`, `Buy rope`, `exit 0`, in that order and nothing else.
   Today: each call prints `usage: notes add <text> | notes list` and `exit 2`.

2. The word is plain text, never a pattern.

   ```bash
   f=$(mktemp); printf '%s\n' 'abc' 'a.c' 'x -v y' > "$f"
   NOTES_FILE=$f bin/notes search a.c; echo "exit $?"
   NOTES_FILE=$f bin/notes search -v; echo "exit $?"
   ```

   Done: prints `a.c`, `exit 0`, `x -v y`, `exit 0`, in that order and nothing else. Today: each call prints
   `usage: notes add <text> | notes list` and `exit 2`.

3. No match prints nothing and exits 1, and so does a notes file that doesn't exist.

   ```bash
   f=$(mktemp); printf '%s\n' 'Buy rope' > "$f"
   out=$(NOTES_FILE=$f bin/notes search zebra 2>&1); echo "exit $? [$out]"
   out=$(NOTES_FILE=$f.missing bin/notes search rope 2>&1); echo "exit $? [$out]"
   ```

   Done: prints `exit 1 []` twice. Today: prints `exit 2 [usage: notes add <text> | notes list]` twice.

4. A missing word exits 2 with the usage line, which names the new command.

   ```bash
   out=$(NOTES_FILE=/dev/null bin/notes search 2>/dev/null); echo "exit $? [$out]"
   NOTES_FILE=/dev/null bin/notes search 2>&1 >/dev/null
   NOTES_FILE=/dev/null bin/notes search '' 2>&1 >/dev/null; echo "exit $?"
   ```

   Done: prints `exit 2 []`, then `usage: notes add <text> | notes list | notes search <word>`, then that usage
   line again, then `exit 2`. Today: the first and last lines already match, and both usage lines read
   `usage: notes add <text> | notes list`, which doesn't name search.

5. The gate passes, and it runs the four tests named under "Tests".

   ```bash
   bash scripts/gate.sh; echo "exit $?"
   bash scripts/gate.sh | grep -c '^ok   test_search_'
   ```

   Done: the first command prints an `ok` line for `test_add_then_list`, `test_list_empty`, `test_usage`,
   `test_search_match`, `test_search_plain_text`, `test_search_no_match`, and `test_search_usage`, prints no
   `FAIL` line, and ends `exit 0`. The second prints 4 or more. Today: the first prints the three existing `ok`
   lines and `exit 0`, and the second prints `0`. The gate alone passes today, so the count is the part of this
   item that the task has to change.

6. The README names the new command.

   ```bash
   grep -c 'bin/notes search <word>' README.md
   ```

   Done: prints 1 or more. The README says, in the manner of its sentences on `add` and `list`, that search
   prints the notes that contain the word, oldest first, that the match ignores case and the word is plain text,
   and that no match prints nothing and exits 1. Its voice standard is the one the `writing-voice` skill names
   for a README in a shell repo, `~/.claude/docs/voice/written-for-people.md`. Today: prints `0`.

7. One pull request to `main` of example/notes carries the work, and it changes only the three files.

   ```bash
   git diff --name-only main...HEAD
   git rev-parse HEAD
   ```

   Done: the first command prints `README.md`, `bin/notes`, and `tests/run.sh` and nothing else. The pull
   request's body follows `building-from-specs`, "The pull request", and quotes the output of item 5's two
   commands beside the hash that `git rev-parse HEAD` printed when they ran. That hash is the branch's last
   commit. The repo has no CI, so this quoted run is the only full run the pull request has. The pull request
   itself is shown by its URL in the session's report and is read on GitHub. This spec names no `gh` command for
   it, because the session that wrote the spec couldn't reach the remote to run one. Today: the first
   command prints nothing, the second prints `7115ad021bffe0c8d0633d27d79b2af24df22e77`, and no pull request
   exists.

## Calls Claude made

The first six are product calls that Geoff would have been asked about. Each one is reversed by a small later
commit.

1. The brief's README check is replaced. `grep -c notes README.md` prints `3` on today's code, so it passes
   before any work is done and can't show that the README names search. Item 6 uses
   `grep -c 'bin/notes search <word>' README.md`, which prints `0` today. Any README that passes item 6 also
   passes the brief's check.
2. "Contains the word" means the word's text appears anywhere in the line, so `rope` finds `ropes`. The option
   passed over is a whole-word match. Reversing adds one flag and changes one test.
3. Arguments after `search` are joined with spaces, as `add` joins them. The option passed over is a usage error
   for a second argument.
4. An empty word counts as a missing word and exits 2. Passed straight to `grep`, it would print every note.
5. A notes file that doesn't exist counts as no match: nothing printed, exit 1. This follows `list`, which
   prints nothing when the file doesn't exist.
6. `spec.md` stays uncommitted, and the task session reads it by absolute path in the main checkout. Two options
   were passed over. Committing it straight to `main` goes against the README, which says "Work reaches `main`
   through a pull request to `origin`". A pull request for the spec alone goes against the brief's one pull
   request. Whether and how `spec.md` is ever committed is left to Geoff.
7. The usage line's exact text is `usage: notes add <text> | notes list | notes search <word>`.
8. The match uses `grep -i -F -e`, and the three cases under "When it goes wrong" stay as `grep` leaves them.
9. "The gate passes" is paired with a count of the search tests the gate ran, because the gate alone passes
   today.
10. Four tests are named, and `test_usage` stays as it is.
11. The estimate is 40 minutes, and the time clause is 80.
12. The task session runs on Opus at high. Only `standards:diff-reviewer` reads the branch.
13. The README's voice standard is named from the `writing-voice` skill's table. This session's two tries to
    read `~/.claude/docs/voice/written-for-people.md` were refused, and so was the fresh reader's, so the spec
    quotes nothing from it. The four facts item 6 lists are what the reviewer checks the README against.
