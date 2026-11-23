# Spec: notes search

Written 2026-11-22 from `brief.md`, the design Geoff settled in conversation. It waits for his approval. The
work is one task and one pull request to `example/notes`. Nobody could answer a question while this was
written, so each open reading was decided and is listed under "Calls Claude made".

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is a new command, `bin/notes search <word>`, that prints every note containing the word, oldest
first. The match ignores case, and the word is plain text, never a pattern.

The work leaves these out: patterns, whole-word matching, more than one search word, flags, highlighted or
numbered output, any change to `add` or `list`, and CI for the repo.

The work fails if a word is ever read as a pattern or as an option, if `add` or `list` behave differently
afterward, or if a call in the table below exits with a different code.

## What search does

| Call | Prints | Exit |
| --- | --- | --- |
| `search <word>`, and one or more notes contain the word | Each matching note on stdout, in file order | 0 |
| `search <word>`, and no note contains it | Nothing | 1 |
| `search <word>`, and the notes file doesn't exist | Nothing | 1 |
| `search` with no word, an empty word, or more than one word | The usage line on stderr, nothing on stdout | 2 |

The usage line becomes `usage: notes add <text> | notes list | notes search <word>`. File order is oldest
first, because `add` appends. A note contains the word when the word appears anywhere in it, so `rope` finds
`ropes`.

## Approaches

Three ways to match were weighed, and the pick is the first.

- `grep -i -F -e "$word" "$file"`. It is one line, and grep's exit codes for a match and for no match are
  already the ones the brief asks for. Its cost is that grep exits 2 with an error when the file is missing,
  which would collide with the usage exit, so the command checks for the file first, as `list` does.
- A Bash loop that lowercases each line with `${line,,}`. It needs no other program, but it is longer and
  needs Bash 4.
- `awk` with `index(tolower($0), tolower(word))`. It works, but passing the word in safely takes more care
  than `-e` does.

## When it goes wrong

- A word with pattern characters, such as `a.b` or `a?b`, matches only that text. A word that starts with
  `-`, such as `-x`, is searched for and never read as an option. `-F` and `-e` do both.
- A missing notes file prints nothing and exits 1, with nothing on stderr.
- Two cases are left to grep, and no goal item covers them. A notes file that exists but can't be read
  prints grep's error and exits 2. A word that holds a newline is read as two words, and notes with either
  one print.
- The exit codes are the only limits: 0 for a match, 1 for none, 2 for a usage error. Nothing caps the
  number of notes or the length of the word.
- `tests/run.sh` runs only the tests named in its loop on line 15, though its comment says it runs every
  `test_*` function. A new test left out of that loop never runs and the gate still passes, so goal item 5
  names each new test's `ok` line.
- The repo runs no CI on pull requests (`.workstation/remote.txt`), so the gate on the branch's last commit
  is the only full run. The pull request quotes that run.

## Sources

`grep -i -F -e` is documented. GNU grep 3.12 on this workstation prints these lines from `grep --help`:

```text
  -F, --fixed-strings       PATTERNS are strings
  -e, --regexp=PATTERNS     use PATTERNS for matching
  -i, --ignore-case         ignore case distinctions in patterns and data
```

`man grep` says: "Normally the exit status is 0 if a line is selected, 1 if no lines were selected, and 2 if
an error occurred." A probe on 2026-11-22 confirmed each case on a six-line file: `grep -iF -e rope` and
`-e RoPe` each printed `Buy rope` and `coil the ROPE` and exited 0, `-e a.b` printed only `a.b`, `-e -x`
printed only `use -x here`, `-e 'a?b'` and `-e sail` printed nothing and exited 1, and a missing file printed
an error and exited 2.

The spec adds no Claude Code mechanism, so no Anthropic docs page was read. It adds no project, service, or
infrastructure and publishes no build.

## Assumptions

The work is one task, so no assumption is shared between tasks.

## Files

The list comes from three searches on commit `7115ad0`.

`git ls-files` has 5 hits. `bin/notes`, `tests/run.sh`, and `README.md` change. `scripts/gate.sh` only calls
`tests/run.sh` and stays as it is. `brief.md` is the design's source and stays as it is.

`grep -rn 'usage' README.md bin scripts tests` has 4 hits.

- `bin/notes:7` changes: the usage line gains the new command, and the `search` branch goes above it.
- `tests/run.sh:15` changes: the loop gains the new tests' names.
- `tests/run.sh:12` and `:13` stay. `test_usage` checks only that the line starts with `usage:`.

`grep -rn 'notes list' README.md bin scripts tests` has 4 hits.

- `README.md:4` changes: the first paragraph gains a sentence about `bin/notes search <word>`.
- `bin/notes:7` is the usage line already listed.
- `tests/run.sh:7` and `:10` stay. They are the existing `add` and `list` tests.

## Commands and the denials log

`.workstation/denials.log` holds three refusals since 2026-10-23, and none matches a command this task runs.

- `git push --force origin main` was refused as a force push to the default branch. The task pushes only the
  branch it created, with no force flag.
- `rm -rf ~/.notes.bak` was refused as a recursive delete outside the working folder. The tests remove only
  single files that `mktemp` made, with `rm -f` as `tests/run.sh:10` already does. No test uses `rm -r`, and
  every test that reads or writes notes sets `NOTES_FILE`, so none touches `~/.notes`.
- A WebFetch of `https://example.invalid/notes` was refused as an unknown host. The task fetches nothing.

The commands in the goal below ran in Claude Code on 2026-11-22, and each records what it printed. The
commit, push, pull request, and review commands belong to `building-from-specs`, and the goal points there.

## Start conditions

On 2026-11-22 the main checkout was on `main` at `7115ad0` with no change to a tracked file. The task needs
no secret and waits on no CI run. The remote is public, and its default branch is `main`.

Three checks could not run from the session that wrote this spec, so the session that launches the task
runs them first. `claude-worktree-busy` and `claude agents --json` are the checks in "Launching a task" in
`building-from-specs`. The third is a fetch: the checkout has no `origin/main` ref
(`git rev-parse --verify origin/main` prints `fatal: Needed a single revision`), and the task's worktree
starts from the remote's `main`, so the launching session confirms that `origin/main` is `7115ad0`.

`spec.md` is not committed, so the task's worktree won't hold it. The launch goal names this spec by its
absolute path in the main checkout, and the reviewer's brief does the same.

## The task: add notes search

The task waits for no other task, and its pull request is the only one, so there is no merge order to set.
It changes `bin/notes`, `tests/run.sh`, and `README.md`. Its session is named `notes-search` and runs on
Opus at medium.

`standards:diff-reviewer` reviews it, on Opus at high. The work has no sign-in or data path and no rendered
UI, so no second reviewer reads it.

The task takes 41 minutes, and its time clause is `or stop after 82 minutes`. `task-report --since
2026-11-01` shows two like tasks, each one command with its tests: "Add notes list" measured 34 minutes
against 30 planned, and "Let notes add read stdin" measured 41 against 30 with one fix round. The estimate is
the higher of the two. Nothing adds a wait, because the gate is the only run and it finishes in under a
second.

### Goal

Each command runs from the worktree's root on the branch's last commit.

1. Search prints each note that contains the word, oldest first, ignoring case.

   ```bash
   f=$(mktemp); printf '%s\n' 'Buy rope' 'call Sam' 'coil the ROPE' > "$f"; NOTES_FILE=$f bin/notes search RoPe; echo "exit $?"
   ```

   Today: `usage: notes add <text> | notes list`, then `exit 2`.
   Holds: `Buy rope`, `coil the ROPE`, `exit 0`, and nothing else.

2. The word is plain text, never a pattern or an option.

   ```bash
   f=$(mktemp); printf '%s\n' 'axb' 'a.b' 'use -x here' > "$f"; NOTES_FILE=$f bin/notes search a.b; echo "exit $?"; NOTES_FILE=$f bin/notes search -x; echo "exit $?"; NOTES_FILE=$f bin/notes search 'a?b'; echo "exit $?"
   ```

   Today: `usage: notes add <text> | notes list` and `exit 2`, three times.
   Holds: `a.b`, `exit 0`, `use -x here`, `exit 0`, `exit 1`, and nothing else.

3. No match, or no notes file, prints nothing and exits 1.

   ```bash
   f=$(mktemp); printf '%s\n' 'Buy rope' > "$f"; NOTES_FILE=$f bin/notes search sail; echo "exit $?"; rm -f "$f"; NOTES_FILE=$f bin/notes search rope; echo "exit $?"
   ```

   Today: `usage: notes add <text> | notes list` and `exit 2`, twice.
   Holds: `exit 1`, `exit 1`, and nothing else.

4. A missing word, an empty word, or a second word exits 2 with the usage line on stderr, and that line
   names the new command. The command discards stdout, so the lines it prints came from stderr.

   ```bash
   bin/notes search 2>&1 >/dev/null; echo "exit $?"; bin/notes search "" 2>&1 >/dev/null; echo "exit $?"; bin/notes search buy rope 2>&1 >/dev/null; echo "exit $?"
   ```

   Today: `usage: notes add <text> | notes list` and `exit 2`, three times.
   Holds: `usage: notes add <text> | notes list | notes search <word>` and `exit 2`, three times.

5. The gate passes and runs four new tests.

   ```bash
   bash scripts/gate.sh; echo "exit $?"
   ```

   Today: `ok   test_add_then_list`, `ok   test_list_empty`, `ok   test_usage`, `exit 0`.
   Holds: those three lines, then `ok   test_search_match`, `ok   test_search_plain_text`,
   `ok   test_search_no_match`, `ok   test_search_usage`, then `exit 0`, with no `FAIL` line. Each test
   asserts every output its item shows, items 1 to 4 in that order, and the reviewer reads the four test
   bodies against those items.

6. The README names the new command. Its prose follows the `writing-voice` skill's standard for a README in
   a shell repo, `~/.claude/docs/voice/written-for-people.md`.

   ```bash
   grep -c 'bin/notes search <word>' README.md
   ```

   Today: `0`.
   Holds: `1` or more.

7. Geoff's check from the brief holds.

   ```bash
   grep -c notes README.md
   ```

   Today: `3`.
   Holds: `1` or more.

8. One pull request to `main` on `example/notes` is marked ready. Its body quotes the output of items 1 to 7
   from the branch's last commit and carries a `standards:diff-reviewer` verdict of accept that names that
   commit. "Gates and review" and "The pull request" in `building-from-specs` own the commands. Today the
   branch and the pull request don't exist.

## Backlog sweep

The scoped sweep has no items. The repo has no backlog file: `ls docs BACKLOG* TODO*` found none of the
three on 2026-11-22. Approving this spec approves no backlog edit.

## Calls Claude made

Calls 1 to 9 add to what the brief settled or change how its done items are checked, so they are Geoff's
to overrule. Calls 10 to 14 are method.

1. The brief's check `grep -c notes README.md` prints 3 today and can't show that the task did anything, so
   it stays word for word as item 7 and item 6 adds a check that prints 0 today.
2. "The gate passes" is also true today, so item 5 ties it to four named tests that don't exist yet.
3. "Contains the word" means the word appears anywhere in a note, so `rope` finds `ropes`; whole-word
   matching was passed over, and reversing takes one grep flag and one test.
4. A second word exits 2 with the usage line; joining the words into a phrase, as `add` joins its text, was
   passed over, and accepting phrases later breaks no one who uses `search` as built.
5. An empty word counts as a missing word; matching every note, which is what grep does with an empty
   string, was passed over.
6. A missing notes file gives the no-match result, as `list` already treats a missing file as an empty list.
7. A word that starts with `-` is text, which follows from "plain text, never a pattern".
8. An unreadable notes file and a word that holds a newline are left to grep and are untested.
9. The usage line's wording and the list of what the work leaves out, beyond what the brief names, are
   Claude's.
10. The match uses `grep -i -F -e`, picked over a Bash loop and `awk`.
11. The four test names in item 5 are fixed here so that the gate's output can be checked.
12. The task takes 41 minutes, the higher of the two like tasks.
13. The task session runs on Opus at medium, and `standards:diff-reviewer` alone reviews it on Opus at high.
14. The launch goal names `spec.md` by its absolute path in the main checkout; committing the spec to `main`
    first was passed over, because the README says work reaches `main` through a pull request.
