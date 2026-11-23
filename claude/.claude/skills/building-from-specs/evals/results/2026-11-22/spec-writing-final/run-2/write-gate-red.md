# Spec: notes search

`bin/notes search <word>` prints every note that contains the word. The work is one task and one pull
request, planned at 40 minutes, and it follows `brief.md`, the design Geoff approved in conversation.

One thing here is not in that brief, and Geoff should read it before he approves. The gate is red on `main`
today for a reason that has nothing to do with search, so "the gate passes" can't come from the search work
alone. This spec removes the failing test. The next section gives the evidence, the options, and how to
reverse the call. Approving the spec approves the removal.

## The gate is red before the work starts

`bash scripts/gate.sh; echo "exit=$?"` on `main` at `18fc5cb`, run 2026-11-22, prints:

```text
ok   test_add_then_list
ok   test_list_empty
ok   test_usage
FAIL test_export_csv
exit=1
```

`test_export_csv` (`tests/run.sh:15`) runs `bin/notes export` and wants `1,"buy rope"`. `bin/notes` has no
`export` command: it prints the usage line and exits 2. `git grep -n export -- ':!brief.md'` finds 3 lines,
all in that test and the loop that runs it. The README names two commands, `add` and `list`. This checkout
holds one commit, which says nothing more about `export`. `task-report` lists pull requests 12, 15, and 18 on
the remote, so there is more history than this, and neither it nor the remote's issues could be read from the
session that wrote this spec. Whether an export is wanted is Geoff's to say.

The test, in full, so that removing it loses nothing:

```bash
test_export_csv() {
  local f; f=$(mktemp); NOTES_FILE=$f bin/notes add "buy rope"; [ "$(NOTES_FILE=$f bin/notes export 2>/dev/null)" = '1,"buy rope"' ]
}
```

| Option | What it gives | What it costs |
| --- | --- | --- |
| Remove `test_export_csv` in this task | The gate passes, and the work stays in the brief's two files and one pull request | The repo loses its one trace that an export was wanted |
| Build `export` | The gate passes | It ships a command nobody designed. The test fixes one line of output and nothing about commas, quotes, or an empty file |
| Leave the test and finish with the gate red | No test is touched | It changes the done condition Geoff approved, and under the skill's "Gates and review" the pull request can never be marked ready |

The pick is the first. A removed test comes back cheaply, and a shipped command does not leave as cheaply.
Reversing the call is a small edit: put the function above back and add its name to the list in
`tests/run.sh`. That turns the gate red again until someone builds `export`, which would be its own spec. The
pull request's `## For Geoff` names the removal and points here.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goals are the brief's: one new command, a match that ignores case, a word that is plain text, exit 1 on no
match, and exit 2 with a usage line that names the new command. The non-goals are patterns, whole-word
matching, a search for several words, an `export` command, and a README change.

The work fails if a word acts as a pattern (`a.c` finds `abc`), if a test or check reads or writes `~/.notes`,
or if the gate passes because a new test never ran. The last can happen: `tests/run.sh:18` runs a hand-written
list of names, so a test function left off the list is skipped without a sound.

## What search does

| Call | stdout | stderr | Exit |
| --- | --- | --- | --- |
| `notes search rope`, some notes contain it | Each matching line as stored, in file order | nothing | 0 |
| `notes search rope`, no note contains it | nothing | nothing | 1 |
| `notes search rope`, the notes file doesn't exist | nothing | nothing | 1 |
| `notes search`, `notes search ""`, or `notes search buy rope` | nothing | the usage line | 2 |
| Any unknown command | nothing | the usage line | 2 |

The usage line becomes `usage: notes add <text> | notes list | notes search <word>`. A match is a substring
match, so `rope` finds `ropes`. File order is oldest first, because `add` appends. A word that starts with `-`
is still a word. The rule in the fourth row counts arguments, so `notes search "buy rope"` is one word and
finds that text.

The file check is `[ -f "$file" ]`, the test `list` uses, so a notes path that is a folder also exits 1. A
notes file that can't be read fails with grep's own message and exit 2. No limit applies: search reads the
file once and stores nothing.

## Approaches

The pick is `grep -iF -- "$word" "$file"`, behind a check that the file exists. Both flags are documented, in
`grep --help` from GNU grep 3.12 on this workstation: "`-F, --fixed-strings` PATTERNS are strings" and
"`-i, --ignore-case` ignore case distinctions in patterns and data". A probe on a file holding `Buy rope`,
`sell boat`, `ROPE wax`, `a.c`, `abc`, and `-x flag` showed the rest:

| Probe | Prints | Exit |
| --- | --- | --- |
| `grep -iF -- -x "$f"` | `-x flag` | 0 |
| `grep -iF -- rope "$f.missing"` | `No such file or directory` on stderr | 2 |
| `grep -iF -- "" "$f"` | all 6 lines | 0 |

grep exits 0 on a match and 1 on none, as the done output of goal items 1 and 3 shows, so its exit codes
already match the brief. The first row is why the call keeps its `--`. The other two are why the command
checks for the file and refuses an empty word itself.

The other approach was a loop in bash that lowercases each line with `${line,,}` and tests it with
`[[ $line == *"$word"* ]]`. It starts no second process, but the word stays plain text only while those quotes
are in place, and without them it becomes a glob pattern. The pick has no such trap.

The work adds no Claude Code mechanism of its own. The launch, the goal, and the review are the skill's.

## Files

`git grep -nE 'usage:|notes (add|list)|test_' -- ':!brief.md'` finds 13 lines in 3 files.

- `bin/notes:7`, 1 hit: the usage line. It changes, and the `search` branch joins the `case`.
- `tests/run.sh`, 10 hits. Lines 15 to 18 change: the export test goes, and the list at line 18 gains the
  new names. Lines 2 to 13 are the header comment and the three other tests, and they stay.
- `README.md:3-4`, 2 hits: the sentences that describe `add` and `list`. They stay, because the brief settles
  the changed files at two. The pull request's `## For Geoff` says the README now lists two of three commands.

`scripts/gate.sh` has no hit. It runs `tests/run.sh` and stays as it is.

## The task: `notes-search`

It waits for no other task, and its pull request is the only one, so there is no merge order. It runs on Sonnet
at medium effort, because this spec settles each judgment call. `standards:diff-reviewer` reads it. It touches
no sign-in or data path and renders no UI, so no other reviewer does.

It removes `test_export_csv` and its name from the list at `tests/run.sh:18`. It adds the command and these
four tests, each named in that list. A test that reaches the notes file uses a `mktemp` file, as
`test_add_then_list` does.

| Test | What it asserts |
| --- | --- |
| `test_search_match` | Item 1 below: both matching lines, in file order, exit 0 |
| `test_search_plain_text` | Item 2 below: `a.c` finds `a.c` and not `abc`. Also, `-x` finds a note `-x flag` |
| `test_search_no_match` | Nothing on stdout and exit 1, for a file with no match and for a file that doesn't exist |
| `test_search_usage` | Exit 2 and the new usage line on stderr, for no word, an empty word, and two words |

### Goal

Each command runs from the worktree's root and ran in Claude Code on 2026-11-22 against `main`. The "done"
output of items 1 to 4 comes from a throwaway copy of `bin/notes` with the grep branch, run in a temp folder.

1. Search prints each matching note, oldest first, ignoring case.
   `f=$(mktemp); printf 'Buy rope\nsell boat\nROPE wax\n' > "$f"; NOTES_FILE=$f bin/notes search rope; echo "exit=$?"`
   Today: `usage: notes add <text> | notes list`, then `exit=2`. Done: `Buy rope`, `ROPE wax`, `exit=0`.
2. The word is plain text, never a pattern.
   `f=$(mktemp); printf 'a.c\nabc\n' > "$f"; NOTES_FILE=$f bin/notes search a.c; echo "exit=$?"`
   Today: `usage: notes add <text> | notes list`, then `exit=2`. Done: `a.c`, `exit=0`.
3. No match prints nothing and exits 1.
   `f=$(mktemp); printf 'Buy rope\n' > "$f"; NOTES_FILE=$f bin/notes search anchor; echo "exit=$?"`
   Today: `usage: notes add <text> | notes list`, then `exit=2`. Done: `exit=1` and no other line.
4. A missing word exits 2 with a usage line that names the new command.
   `bin/notes search 2>&1 >/dev/null; echo "exit=$?"`
   Today: `usage: notes add <text> | notes list`, then `exit=2`. Done:
   `usage: notes add <text> | notes list | notes search <word>`, then `exit=2`.
5. The gate passes on the branch's last commit and runs the new tests.
   `bash scripts/gate.sh; echo "exit=$?"`
   Today: the five lines quoted in the first section, ending `exit=1`. Done: seven `ok` lines, for
   `test_add_then_list`, `test_list_empty`, `test_usage`, `test_search_match`, `test_search_plain_text`,
   `test_search_no_match`, and `test_search_usage`, then `exit=0`, with no `FAIL` line.
6. The branch changes only the brief's two files.
   `git diff --name-only main...HEAD`
   Today: nothing. Done: `bin/notes` and `tests/run.sh`.

The remote runs no CI on pull requests (`.workstation/remote.txt`), so item 5 is the only full run.

### Minutes

40, and the goal's time clause is 80. `task-report --since 2026-11-01` shows the two tasks that changed a
command: "Add notes list" was planned at 30 and took 34 with no fix round, and "Let notes add read stdin" was
planned at 30 and took 41 with one. This task is a command with four tests and a test removal, so it sits by
the larger of the two. The task drives no timer or idle limit, so nothing adds a wait.

### Commands and the denials log

The log holds 3 refusals since 2026-10-23: a force push to `main`, an `rm -rf` outside the working folder, and
a web fetch to an unknown host. The task runs the gate, `bin/notes` with `NOTES_FILE` set, `git` on its own
branch, `gh` for its pull request, and the review dispatch. None of those is a force push, a recursive delete,
or a fetch. Two rules keep it so: each run of `bin/notes` that reaches the notes file sets `NOTES_FILE` to a
`mktemp` file, and nothing clears a folder outside the worktree.

### Before launch

`claude-worktree-busy` is not on the path of the session that wrote this spec (`command not found`, exit 127),
so the start conditions are untested. The launching session runs the checks in the skill's "Launching a task".
The task needs no secret. `example/notes` is public with default branch `main`.

Two more things hold before launch. This spec is committed to `main` and pushed, because the task's worktree
starts from the remote's `main` and goal item 6 counts the spec as already there. And the remote's `main` is
at `18fc5cb`, the commit every "today" output here was read from. If it has moved, the launching session
reruns the six commands first.

## Backlog sweep

`standards:backlog-sweep`, scoped. A search for files named `BACKLOG`, `backlog`, `STATUS`, or `TODO` finds
none, so there are no items and no verdicts, and no full sweep is due. GitHub issues on `example/notes` were out
of reach of the session that wrote this spec.

## Calls Claude made

1. `test_export_csv` is removed, in place of building `export` or leaving the gate red.
2. No backlog entry records the export idea. The repo has no backlog file and the brief settles the changed
   files at two, so this spec carries the test's text and the pull request names the removal.
3. "Contains the word" means a substring: `rope` finds `ropes`.
4. Search takes exactly one argument. An empty word or a second argument exits 2 with the usage line, as a
   missing word does. A quoted phrase is one argument. Loosening the rule later breaks nobody.
5. A notes file that doesn't exist is no match: nothing printed, exit 1. `list` already prints nothing for it.
   A word that starts with `-` is searched like any other.
6. The usage line reads `usage: notes add <text> | notes list | notes search <word>`.
7. Case is folded as `grep -i` folds it in the caller's locale. The tests cover ASCII letters only.
8. `README.md` stays as it is, and the pull request names the gap for Geoff.
9. `grep -iF` is the mechanism, over a loop in bash.
10. The task is planned at 40 minutes and runs on Sonnet at medium effort.
