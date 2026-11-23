# Spec: notes search

`brief.md` holds the design Geoff settled in conversation. This spec adds what a session needs to build
it with nobody to ask. Each addition is listed under [Calls Claude made](#calls-claude-made), and two of
them widen the brief's file list.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is one new command, `bin/notes search <word>`, that prints every note containing the word,
oldest first.

The work adds no patterns, no whole-word matching, no second search term, no line numbers or
highlighting, and no CI. It leaves `add`, `list`, and the way `tests/run.sh` finds its tests as they are.

The work has failed if a pattern leaks through (`search a.b` prints `axb`), if `add` or `list` behaves
differently, if the gate is red on the branch's last commit, or if a search test exists and never runs.

## What search does

Rules 1, 2, 5, and 7 come from the brief. Rules 3, 4, and 6, and the parts marked as calls, are Claude's.

1. `bin/notes search <word>` prints each line of `$NOTES_FILE` that contains the word. It prints them in
   file order, which is oldest first because `add` appends.
2. The match ignores case. The word is plain text: `.`, `*`, `[`, and `\` stand for themselves, and so
   does a leading `-` (call).
3. "Contains" means a substring, so `rop` finds `buy rope` (call).
4. Extra arguments join with single spaces, the way `add` joins its text, so `search the rope` looks for
   `the rope` (call).
5. A match exits 0. No match prints nothing and exits 1.
6. A notes file that doesn't exist counts as no match: nothing on stdout or stderr, and exit 1 (call).
   `list` already prints nothing for a missing file.
7. A missing word prints the usage line on stderr and exits 2. An empty word, `search ''`, counts as
   missing (call). A word made only of spaces is still a word (call). Every usage error prints this one
   line (wording is a call):
   `usage: notes add <text> | notes list | notes search <word>`

## Approach

The pick is `grep -iF -- "$word" "$file"`, behind a check that the word is non-empty and the file exists.
It is documented: `grep --help` (GNU grep 3.12, the one on this workstation) says `-F, --fixed-strings
PATTERNS are strings` and `-i, --ignore-case  ignore case distinctions in patterns and data`. Run today
against the fixture in the goal, `grep -iF -- a.b` printed `a.b` and not `axb`, `grep -iF -- -v` printed
`-v flag`, and `grep -iF -- zebra` printed nothing and exited 1, which is already the exit code the brief
asks for. `grep -iF -- ''` printed all five lines, which is why rule 7 turns an empty word away first.
How `-i` folds letters outside ASCII follows the locale.

Two other ways were weighed, and each is assembled from documented pieces. A bash loop over the file
with `[[ ${line,,} == *"${word,,}"* ]]` needs no outside program, but it has to build the exit status
itself, and without the inner quotes the word is a glob pattern: with the word `a.?b` and the line
`a.xb`, the unquoted test matched and the quoted one didn't. An awk `index(tolower($0), tolower(w))` is
also plain text, but `awk -v w='a\tb'` rewrites the backslash (the probe printed `a`, a tab, `b`), so
the word would need to travel another way.

The work adds no Claude Code mechanism, so there is no Anthropic docs page to read. With one task, no
assumption is shared between tasks.

## When it goes wrong

The exit codes are the only numbers: 0 for a match, 1 for none, and 2 for a usage error. There is no size
limit, because grep reads the file as a stream.

The repo sets three traps. Each was probed today in a scratch copy.

- Changing the usage line alone turns the gate red. `test_completions_match` collects every
  `notes <lowercase word>` in `bin/notes` and compares the set with `completions/notes.bash`. With only
  the usage line changed, the gate printed `FAIL test_completions_match` and exited 1.
- The same test reads comments. With `# prints notes that match` added to `bin/notes`, it found a
  command named `that` and failed. So `bin/notes` carries no `notes ` followed by a lowercase word
  outside the usage line.
- `tests/run.sh:21` runs tests from a list of names, although its header comment says it runs every
  `test_*` function. A `test_search_x() { false; }` left off that list never ran, and the gate exited 0.

Two cases stay out of scope. A word that holds a newline is read by grep as two words: `search
$'zebra\nrope'` printed both rope notes. A notes file that exists and can't be read fails with grep's
own message and grep's exit code, which is also 2.

## Files

`git grep -n -w list` gives 7 hits, and `git grep -n usage` gives 5.

| File | Hits | What changes |
| --- | --- | --- |
| `bin/notes` | `:6` list arm, `:7` usage line | Gains the `search` arm. The usage line becomes rule 7's. |
| `tests/run.sh` | `:7`, `:10`, `:12`, `:13`, `:21` | Gains four tests, each named in the list at `:21`. The other lines stay, and `test_usage` still passes because it reads only the first word. |
| `completions/notes.bash` | `:2` | Becomes `complete -W "add list search" notes`. The brief doesn't name this file. The gate fails without it. |
| `README.md` | `:4` | Gains one sentence on `bin/notes search <word>`. The brief doesn't name this file, and no gate reads it. |
| `brief.md` | `:3`, `:9` | Nothing. Both hits are the brief's own prose. |

`scripts/gate.sh` has no hit and doesn't change.

The repo has no backlog file: `git ls-files` lists six files and `git grep -i backlog` gives 0 hits. The
scoped `standards:backlog-sweep` therefore has no items and no verdicts.

## Commands and the denials log

The task runs `bash scripts/gate.sh`, `bin/notes`, `mktemp`, `rm -f` on one `mktemp` file as
`test_list_empty` does, `git add` by file name, `git commit`, a push of its own branch, and the pull
request and review steps that `building-from-specs` owns.

`.workstation/denials.log` holds three refusals from the last 30 days, 2026-10-23 to 2026-11-22. None
matches a command the task runs.

- `git push --force origin main`: the task pushes only its own branch and never forces.
- `rm -rf ~/.notes.bak`: the tests' temp files sit outside the working folder, so a test removes one
  with `rm -f` and never with `rm -r`. No test or check touches `~/.notes`: each sets `NOTES_FILE`.
- A WebFetch of an unknown host: the task fetches nothing.

## Task: notes-search

The spec has one task and one pull request, against `main` on `example/notes`. It waits for no other
task, so there is no merge order.

### Goal

Run the checks from the repo root after this setup:

```bash
f=$(mktemp); printf '%s\n' 'buy rope' 'a.b' 'axb' 'Call the ROPE shop' '-v flag' > "$f"
export NOTES_FILE=$f
s() { bin/notes search "$@" 2>&1; echo "exit $?"; }
```

Today each of checks 1 to 8 prints `usage: notes add <text> | notes list` and then `exit 2`.

1. A word matches as a substring, ignoring case, oldest first. `s ROP` prints `buy rope`,
   `Call the ROPE shop`, `exit 0`.
2. A dot is a dot. `s a.b` prints `a.b`, `exit 0`, and never `axb`.
3. A leading dash is text. `s -v` prints `-v flag`, `exit 0`.
4. Extra arguments join. `s the rope` prints `Call the ROPE shop`, `exit 0`.
5. No match prints nothing and exits 1. `s zebra` prints `exit 1` alone.
6. A missing notes file is no match. `NOTES_FILE=$f.gone s rope` prints `exit 1` alone.
7. A missing word is a usage error. `s` prints
   `usage: notes add <text> | notes list | notes search <word>`, `exit 2`.
8. An empty word is a usage error. `s ''` prints the same two lines as check 7.
9. Completion offers the command. `grep -c 'complete -W "add list search" notes' completions/notes.bash`
   prints `0` today and `1` when the item holds.
10. The README names the command. `grep -c 'bin/notes search <word>' README.md` prints `0` today and `1`
    when the item holds. The sentence follows `~/.claude/docs/voice/written-for-people.md`.
11. The gate passes on the branch's last commit and runs the search tests. `bash scripts/gate.sh; echo
    "exit $?"` prints four `ok` lines and `exit 0` today. When the item holds it prints eight `ok` lines,
    no `FAIL`, and `exit 0`, and `bash scripts/gate.sh | grep -c '^ok   test_search_'` prints `4` where
    it prints `0` today.

The four tests are `test_search_matches` (checks 1 and 4), `test_search_plain_text` (2 and 3),
`test_search_no_match` (5 and 6), and `test_search_usage` (7 and 8).

`.workstation/remote.txt` says the repo runs no CI on pull requests, so check 11 is the only full run.
The pull request quotes its output and names the commit it ran on.

### Files, review, and minutes

The task's files are the four that change in the [Files](#files) table.

`standards:diff-reviewer` reads the branch. The work has no sign-in or data path and no rendered UI, so
no other reviewer reads it.

The task is planned at 40 minutes, and the goal's time clause is `or stop after 80 minutes`.
`task-report --since 2026-11-01` shows two like tasks, each a change to a command with its tests: pull
request 12, "Add notes list", took 34 minutes against 30 planned, and pull request 18, "Let notes add
read stdin", took 41 against 30 with one fix round. Pull request 15 added only a test, in 12 minutes, and
is no guide. The task waits on no CI and no timer.

The task session runs on Sonnet at medium effort, because the rules and checks above leave it no design
call.

## Before launch

The start conditions have not been tested against the day's sessions: `claude-worktree-busy` and
`claude agents` can't be reached from where this spec was written. The launching session runs the checks
in `building-from-specs`, "Launching a task", on the day. Two of the four are answered already: the task
needs no secret, and the remote is public with `main` as its default branch.

`spec.md` is untracked today. The task's worktree starts from `origin/main`, so the task session can't
read the spec until it is there. The session Geoff is talking to puts it there once he approves it.

## Calls Claude made

1. `completions/notes.bash` joins the brief's two files. The brief asks for a green gate, and the gate
   fails without it.
2. `README.md` gains one sentence, because it describes every command today. Nothing forces this one.
   Striking check 10 and the README row removes it.
3. A word matches as a substring, never only as a whole word.
4. Extra arguments join with single spaces, as `add` joins its text.
5. An empty word counts as a missing word and exits 2.
6. A missing notes file counts as no match and exits 1 in silence.
7. A word that starts with `-` is text.
8. The usage line reads `usage: notes add <text> | notes list | notes search <word>`, for every usage
   error.
9. The match is `grep -iF --`, over a bash loop or awk, and how case folds outside ASCII is left to the
   locale.
10. The work adds four tests with fixed names to the list at `tests/run.sh:21`, and leaves alone the
    header comment that claims more than the list does.
11. A word holding a newline and an unreadable notes file stay out of scope.
12. The task is planned at 40 minutes with an 80-minute time clause.
13. The task runs on Sonnet at medium effort, and `standards:diff-reviewer` is its only reviewer.
14. The backlog sweep has no verdicts, because the repo has no backlog file.
