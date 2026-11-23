# Spec: notes search

This spec writes down the design in `brief.md`, which Geoff approved in conversation. It is one task and
ends in one pull request to `main` of `example/notes`. The last section lists each call Claude made.

## Two files the brief doesn't name

The brief says the work changes `bin/notes` and `tests/run.sh`. The gate can't pass with only those two.
The brief requires the usage line to name the new command, and `test_completions_match` (`tests/run.sh:15`)
fails when the usage line names a command that `completions/notes.bash` doesn't offer. A scratch copy
outside the repo, with only `bin/notes` changed, printed `FAIL test_completions_match` and the gate exited 1.
With `"add list search"` in the completions file, the gate exited 0.

So the task also changes `completions/notes.bash`. The other way out is to weaken the test, and
`building-from-specs` forbids editing a test to match what was built.

The task also adds one sentence to `README.md`. Nothing forces that. If Geoff strikes it, the session he is
talking to removes done item 8 and the README entries under Files before launch. The builder follows the
spec as it finds it.

## Intent

Geoff said: "I want to find a note without scrolling through the whole list."

The goal is a third command, `bin/notes search <word>`, that prints every note containing the word, oldest
first, ignoring case, with the word read as plain text.

The work does not add pattern or whole-word matching, line numbers, highlighting, or a flag. It does not
change `add` or `list`, and it adds no CI.

The work fails if a word is ever read as a pattern or as an option, if the gate passes because a test was
weakened or left out of the run list, or if a test or check reads the real `~/.notes`.

## Behavior

1. `bin/notes search <word>` prints each line of `$NOTES_FILE` that contains the word, in file order, to
   standard output, and exits 0. File order is oldest first, because `add` appends.
2. The match ignores case and is a substring match: `rope` finds `ropes`.
3. The word is plain text. `a.c` doesn't find `abc`, and `-i` finds a note that contains `-i`. A word that
   contains a newline matches nothing and exits 1, because a note is one line.
4. Arguments after `search` join with single spaces into one word, as `add` joins its text.
5. A missing word prints the usage line to standard error and exits 2. A word that is empty or only spaces
   is missing. The word is checked before the notes file. The usage line becomes
   `usage: notes add <text> | notes list | notes search <word>`, for every usage error.
6. No match prints nothing and exits 1. A notes file that doesn't exist, or isn't a regular file, is no
   match, by the same `[ -f ]` test `list` uses.
7. `completions/notes.bash` offers `add list search`.

## Approaches

| Approach | Trade-off |
| --- | --- |
| `grep -aiF -e "$word" -- "$file"` behind the guards in rules 3, 5, and 6 | One line. grep's exit status is already 0 for a match and 1 for none. Needs grep, which the tests already use. **The pick.** |
| A bash loop that lowercases each line and tests `[[ $line == *"$word"* ]]` | No outside tool. About six lines, keeps its own exit status, and one missing quote turns the word into a glob. |
| `awk` with `index(tolower($0), tolower(w))` | Plain text by construction, but `-v w=...` rewrites backslashes in the word. |

## When it goes wrong

- A note with a byte that isn't valid text makes grep print `binary file matches` in place of the note.
  The `-a` flag stops that. Done item 6 is the probe.
- A notes file that exists and can't be read passes through grep's message and its exit status of 2, the
  same number as a usage error. Probe: `grep: <file>: Permission denied`, `exit 2`.
- Case folding follows the locale. Under `en_US.UTF-8`, `école` found `ÉCOLE`. Under `LC_ALL=C` it exited 1,
  because only ASCII letters fold there.
- Without the newline guard, grep reads a word with a newline as two words. Probe on the unguarded scratch
  copy: `search $'sam\nabc'` printed `call Sam` and `abc`.
- `test_completions_match` reads every `notes <lowercase word>` in `bin/notes`, comments included. A comment
  reading `# prints the notes that match` made the gate exit 1. In `bin/notes`, the text `notes ` comes
  before a lowercase letter only in the usage line's command names.
- `tests/run.sh` runs the tests named in its `for t in` line, not every `test_*` function. A new test left
  out of that line never runs.
- There is no size limit. grep reads the file once, a line at a time.

## Sources

Every mechanism is documented in GNU grep 3.12, the grep on this workstation. `grep --help` prints:

```text
  -F, --fixed-strings       PATTERNS are strings
  -e, --regexp=PATTERNS     use PATTERNS for matching
  -i, --ignore-case         ignore case distinctions in patterns and data
  -a, --text                equivalent to --binary-files=text
... Exit status is 0 if any line is selected,
1 otherwise; if any error occurs and -q is not given, the exit status is 2.
```

`man grep` says `-e` "can be used to protect a pattern" that begins with `-`. The design uses no Claude
Code mechanism and nothing invented. No assumption spans tasks, because there is one task.

## Files

Two searches found the files, run with `git grep -n` over everything but `brief.md`.

`-e 'notes list' -e 'add list'` finds where the commands are named, with 5 hits:

| Hit | Verdict |
| --- | --- |
| `bin/notes:7` | Changes: the usage line. The `search` branch goes above it. |
| `completions/notes.bash:2` | Changes: `"add list"` becomes `"add list search"`. |
| `README.md:4` | Changes: one sentence for `search` joins this paragraph. |
| `tests/run.sh:7` | Dismissed: a test of `add` and `list`. |
| `tests/run.sh:10` | Dismissed: a test of `list`. |

`-e 'completions'` finds what reads the completions file, with 3 hits:

| Hit | Verdict |
| --- | --- |
| `tests/run.sh:15`, `tests/run.sh:18` | Dismissed: `test_completions_match` stays as written. It is why the completions file changes. |
| `tests/run.sh:21` | Changes: the run list gains the four new tests. |

`scripts/gate.sh` runs `tests/run.sh` and doesn't change.

## Commands against the denials log

The log holds three refusals in the last 30 days, and none blocks the task. A force push to `main` was
refused on 2026-11-03: the task pushes only its own branch, without force. `rm -rf ~/.notes.bak` was refused
on 2026-11-09: the task deletes nothing recursively, and the gate's one `rm -f` (`tests/run.sh:10`) removes a
single `mktemp` file from inside the gate script. A web fetch of an unknown host was refused on 2026-11-17:
the task fetches nothing.

The task's own commands are `bash scripts/gate.sh`, `bin/notes`, `mktemp`, `printf`, `grep`, `tr`, `wc`,
`bash -c` with `source` and `complete -p`, and the git and `gh` steps that `building-from-specs` owns.
Every new test and check that reaches the notes file sets `NOTES_FILE` to a `mktemp` path.

## The task: add notes search

**Files:** `bin/notes`, `tests/run.sh`, `completions/notes.bash`, `README.md`.

**Reviewers:** `standards:diff-reviewer`. The work has no sign-in or data path and no rendered UI.

**Minutes:** 41, and the time clause is `or stop after 82 minutes`. `task-report --since 2026-11-01` shows two
like tasks: "Add notes list" took 34 minutes and "Let notes add read stdin" took 41 with one fix round.
This task takes the larger. The repo runs no CI on pull requests, so nothing adds a wait.

**Waits for:** nothing. It is the only task, so its pull request is the whole merge order.

**Launch:** Opus at high. `spec.md` is untracked, and the task's worktree starts from `origin`'s `main`, so the
launch gives the spec's absolute path in the main checkout. The repo is public, and the task needs no
secret and no CI. `claude-worktree-busy` isn't on the machine this spec was written on
(`command not found`), so the launching session runs the checks in `building-from-specs`, "Launching a
task".

### Goal

Items 1 to 5 use this notes file.

```bash
f=$(mktemp); printf '%s\n' 'Buy rope' 'call Sam' 'ROPE for the dinghy' 'abc' 'a.c' 'use -i here' > "$f"
```

1. Search prints each note that contains the word, oldest first, ignoring case.
   `NOTES_FILE=$f bin/notes search rope; echo "exit $?"`
   - Today: `usage: notes add <text> | notes list`, `exit 2`.
   - Done: `Buy rope`, `ROPE for the dinghy`, `exit 0`.
2. The word is plain text, never a pattern or an option.
   `NOTES_FILE=$f bin/notes search a.c; echo "exit $?"; NOTES_FILE=$f bin/notes search -i; echo "exit $?"; NOTES_FILE=$f bin/notes search $'sam\nabc'; echo "exit $?"`
   - Today: the old usage line and `exit 2`, three times.
   - Done: `a.c`, `exit 0`, `use -i here`, `exit 0`, `exit 1`.
3. Arguments after `search` join into one word.
   `NOTES_FILE=$f bin/notes search buy rope; echo "exit $?"`
   - Today: the old usage line, `exit 2`.
   - Done: `Buy rope`, `exit 0`.
4. No match, or no notes file, prints nothing and exits 1.
   `NOTES_FILE=$f bin/notes search anchor; echo "exit $?"; NOTES_FILE=$f.gone bin/notes search rope; echo "exit $?"`
   - Today: the old usage line and `exit 2`, twice.
   - Done: `exit 1`, `exit 1`, and nothing else.
5. A missing word exits 2 with a usage line that names the new command, whether or not the notes file
   exists.
   `NOTES_FILE=$f bin/notes search; echo "exit $?"; NOTES_FILE=$f bin/notes search ' '; echo "exit $?"; NOTES_FILE=$f.gone bin/notes search ''; echo "exit $?"`
   - Today: `usage: notes add <text> | notes list`, `exit 2`, three times.
   - Done: `usage: notes add <text> | notes list | notes search <word>`, `exit 2`, three times.
6. A note with a byte that isn't valid text still prints.
   `g=$(mktemp); printf 'caf\xe9 rope\n' > "$g"; LC_ALL=C.UTF-8 NOTES_FILE=$g bin/notes search rope 2>/dev/null | wc -l`
   - Today: `0`.
   - Done: `1`.
7. The completions offer the new command.
   `bash -c 'source completions/notes.bash; complete -p notes'`
   - Today: `complete -W 'add list' notes`.
   - Done: `complete -W 'add list search' notes`.
8. The README says what `search` does, in one sentence beside the ones for `add` and `list`: what it prints,
   that it ignores case, and that it exits 1 when nothing matches. Its voice standard is
   `~/.claude/docs/voice/written-for-people.md`. The check finds the sentence, and the reviewer reads it for
   the three facts.
   `tr '\n' ' ' < README.md | grep -c 'bin/notes search <word>'`
   - Today: `0`.
   - Done: `1`.
9. The gate passes and runs four new tests.
   `bash scripts/gate.sh; echo "exit $?"`
   - Today: `ok` for `test_add_then_list`, `test_list_empty`, `test_usage`, and `test_completions_match`, then
     `exit 0`.
   - Done: those four lines, then `ok` for `test_search_matches`, `test_search_plain_text`,
     `test_search_no_match`, and `test_search_usage`, then `exit 0`. The four existing tests are unchanged.
10. One pull request to `main` of `example/notes` is ready. Its body quotes the output of items 1 to 9 from
    the branch's last commit, because the repo runs no CI and that gate run is the only full run. It carries
    a `standards:diff-reviewer` verdict of accept on that commit. `building-from-specs`, "Gates and review" and
    "The pull request", own the steps. Not run today: no branch exists yet.

Each new test asserts what its items' commands print. `test_search_matches` covers items 1, 3, and 6,
`test_search_plain_text` item 2, `test_search_no_match` item 4, and `test_search_usage` item 5, where it
compares the whole usage line and the exit status for all three commands.

## Backlog sweep

The repo has no backlog file (`git ls-files` lists six files, none a backlog), so the scoped sweep has no
items and no verdicts.

## Calls Claude made

1. `completions/notes.bash` joins the task's files, because the brief's own done condition forces it.
2. `README.md` gains one sentence, so that it doesn't describe two of three commands.
3. The match is a substring. Whole-word matching would be one flag, `grep -w`.
4. Arguments after `search` join into one word. The option passed over is a usage error for a second
   argument, and reversing changes one line and one test.
5. A word that is empty or only spaces is missing, since grep would match every note with it.
6. A word with a newline matches nothing.
7. A notes file that is absent or not a regular file is no match, as `list` treats it.
8. grep runs with `-a`.
9. An unreadable notes file keeps grep's message and exit status 2, because a new exit status would be new
   surface.
10. One usage line serves every usage error, with the wording in rule 5.
11. The four test names.
12. 41 minutes, from the larger of two like tasks.
13. The launch runs on Opus at high, because the session makes its own calls and dispatches its review.
14. The pull request quotes the checks from the last commit, in place of the CI the repo doesn't run.
