# Spec: notes search

`bin/notes search <word>` prints every note that contains a word. This spec is the design in `brief.md`, written
out for the session that builds it. It is one task and one pull request, planned at 40 minutes.

One thing waits for Geoff before approval. The brief and the README disagree about the exit code, and this spec
follows the brief. The next section says how.

## The brief and the README disagree

The brief says: "No match prints nothing and exits 1." `README.md:10-11` says: "Every command exits 0 when it runs,
even when it prints nothing, and 2 on a usage error. Scripts that call `notes` rely on that."

This spec keeps the brief's exit 1, because it is Geoff's own ruling on this command and the README line was
written when `add` and `list` were the only commands. No script that exists today can call `search`, so no
caller breaks. The README line would then be false, so the task rewrites it to name `search` as the one
exception. That adds `README.md` to the two files the brief lists.

If Geoff would rather keep the README's rule, `search` exits 0 whenever it runs. Every line of this spec that
says exit 1 then says exit 0, and the README keeps its paragraph and gains only the sentence that describes the
command. That is an edit to this spec before approval, or one commit to the same three files after the build.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is the command the brief settles, with its tests, and a README that describes it. The work fails if
`search` treats the word as a pattern, if `add` or `list` change what they print or return, or if the gate passes
without running the new tests.

These are not goals: searching for several words at once, matching whole words only, highlighting, a count of
matches, and handling a notes file that can't be read (`list` doesn't handle one either).

## What search does

The brief settles the first four lines. The rest are readings the brief leaves open, each marked in the last
section.

1. `bin/notes search <word>` prints each note that contains the word, on stdout, exactly as stored and in file
   order. File order is oldest first, because `add` appends.
2. The match ignores case and takes the word as plain text. `a.c` matches the note `a.c` and never `abc`.
3. No match prints nothing and exits 1. A match exits 0.
4. A missing word exits 2 and prints the usage line on stderr. The line becomes
   `usage: notes add <text> | notes list | notes search <word>`, and every usage error prints it.
5. The word matches anywhere in a note, so `rope` finds `ROPEWALK`.
6. An empty word (`notes search ""`) counts as missing: exit 2 with the usage line.
7. More than one argument after `search` exits 2 with the usage line. A quoted argument with spaces is one word
   and matches as that exact text.
8. When the notes file doesn't exist, nothing matches: no output, exit 1.
9. A word that contains a newline matches no note, because a note is one line: no output, exit 1.
10. The tests cover ASCII letters for case. Other letters follow the locale and have no test.

## Approaches

| Approach | Trade-off |
| --- | --- |
| `grep -i -F -e "$word" -- "$file"` (the pick) | One line, and its exit codes are the design's 0 and 1. It needs a guard for a missing file and one for a newline in the word. |
| A bash loop with `shopt -s nocasematch` and `[[ $line == *"$word"* ]]` | No guards, but more lines to own, and a plain loop drops a last line that has no newline. |
| `grep -i` with the word escaped as a pattern | The escaping is where the bug would live. The brief rules a pattern out. |

## When it goes wrong

The probes ran on GNU grep 3.12 and bash 5.3.9, against a file holding `Buy rope`, `abc`, `call the ROPEWALK`,
and `a.c`. Each is a trap the pick has to close.

- A missing file makes grep exit 2 with `No such file or directory`, which would read as a usage error. Line 8
  above needs its own guard.
- A newline in the word makes grep read two patterns: `grep -i -F -e $'zebra\nabc'` printed `abc`. Line 9 needs
  its own guard.
- A word that starts with a dash would read as an option. With `-e` it is the word: `grep -i -F -e '-x'` printed
  nothing and exited 1.
- `tests/run.sh:15` lists the tests to run by name, though its comment says it runs every `test_*` function. A
  new test left off that list never runs and the gate still passes. Done item 7 names each new test for that
  reason.

The work has no limits to number: no timeout, no size cap, no retry.

## Sources

Every mechanism here is documented, and each label rests on the quote and on a probe.

- Plain text: `man grep`, "`-F, --fixed-strings` Interpret PATTERNS as fixed strings, not regular expressions."
  Probe: `grep -i -F -e 'a.c'` printed `a.c` alone, and `grep -i -F -e '.*'` printed nothing and exited 1.
- Case: `man grep`, "`-i, --ignore-case` Ignore case distinctions in patterns and input data". Probe:
  `grep -i -F -e rope` printed `Buy rope` and `call the ROPEWALK`.
- Exit codes: `man grep`, "the exit status is 0 if a line is selected, 1 if no lines were selected, and 2 if an
  error occurred." Probe: `grep -i -F -e zebra` exited 1.
- The loop that was passed over: on a file whose last line had no newline, it printed one of two matching lines
  and grep printed both.

The spec proposes no Claude Code mechanism, so no Anthropic docs page applies. It adds no service or host. It is
one task, so no assumption spans tasks.

## Files

Each search ran as `git grep -n '<text>' -- . ':!brief.md'`, over every tracked file but the brief.

| Search | Hits | Changes | Stays |
| --- | --- | --- | --- |
| `usage` | 5 | `README.md:10`, `bin/notes:7`, `tests/run.sh:15` (the list of tests) | `tests/run.sh:12-13`: `test_usage` checks only the first word, which stays `usage:` |
| `exit` | 4 | `README.md:10`, `bin/notes:7` | `tests/run.sh:2` (a comment) and `:18` (the runner's own exit) |
| `bin/notes` | 5 | `README.md:3-4` (the paragraph gains a sentence on `search`) | `tests/run.sh:7`, `:10`, `:13`: the existing tests |
| `test_` | 5 | `tests/run.sh:15` | `tests/run.sh:2`, `:6`, `:9`, `:12` |

The task changes `bin/notes`, `tests/run.sh`, and `README.md`. `scripts/gate.sh` has no hit and stays.

## Commands and the denials log

The log holds three refusals since 2026-10-23, and the task's commands meet none of them.

- `git push --force origin main`: the task pushes only its own branch and never with force.
- `rm -rf ~/.notes.bak`: every test and hand check sets `NOTES_FILE` to a `mktemp` path. Nothing reads or writes
  `~/.notes`, and nothing deletes recursively. The tests leave their temp files, as the existing ones do.
- A web fetch from an unknown host: the task fetches nothing. Its sources are quoted above.

Every command in the done items ran in Claude Code today, and its output is beside the item. The push, the pull
request, and the review belong to the skill's sections "A session at work", "The pull request", and "Gates and
review".

## The task: add notes search

It changes `bin/notes`, `tests/run.sh`, and `README.md`. It waits for no other task, so the merge order is this
one pull request to `main` of `example/notes`.

`standards:diff-reviewer` reads it. It has no sign-in or data path and no rendered UI.

It is planned at 40 minutes, so the goal's time clause is `or stop after 80 minutes`. `task-report --since
2026-11-01` gives two like tasks: "Add notes list" took 34 minutes against a plan of 30, and "Let notes add read
stdin" took 41 against 30 with one fix round. This task adds a command, as the first did, and handles input, as
the second did. It has more input cases than either, so the plan is the slower one's minutes, rounded to 40.
"Add the usage test" (12 minutes) was a test alone. Nothing adds a wait: the repo runs no CI on pull requests.

The task starts when the four checks in the skill's "Launching a task" pass. Those checks need the workstation
and did not run for this spec. `spec.md` is untracked, so a fresh worktree won't hold it: the goal names it by
its absolute path in the main checkout. The session runs on Sonnet at high effort.

### Goal

Every item that names `$f` uses this setup line:

```bash
f=$(mktemp); printf '%s\n' 'Buy rope' 'abc' 'call the ROPEWALK' 'a.c' > "$f"
```

1. Search finds a word in any case, oldest first. `NOTES_FILE=$f bin/notes search rope; echo "exit $?"`.
   Today: `usage: notes add <text> | notes list`, `exit 2`. Holds: `Buy rope`, `call the ROPEWALK`, `exit 0`.
2. The word is plain text. `NOTES_FILE=$f bin/notes search a.c; echo "exit $?"`. Today: the old usage line,
   `exit 2`. Holds: `a.c`, `exit 0`.
3. No match prints nothing and exits 1. `NOTES_FILE=$f bin/notes search zebra; echo "exit $?"`. Today: the old
   usage line, `exit 2`. Holds: `exit 1` alone.
4. A missing word exits 2 with the new usage line on stderr.
   `NOTES_FILE=$f bin/notes search >/dev/null; echo "exit $?"`. Today: `usage: notes add <text> | notes list`,
   `exit 2`. Holds: `usage: notes add <text> | notes list | notes search <word>`, `exit 2`.
5. An empty word and a second argument are usage errors. `NOTES_FILE=$f bin/notes search "" >/dev/null; echo
   "exit $?"`, then `NOTES_FILE=$f bin/notes search buy rope >/dev/null; echo "exit $?"`. Today, each: the old
   usage line, `exit 2`. Holds, each: the new usage line, `exit 2`.
6. A missing notes file and a word with a newline match nothing. `NOTES_FILE=$f.absent bin/notes search rope;
   echo "exit $?"`, then `NOTES_FILE=$f bin/notes search $'zebra\nabc'; echo "exit $?"`. Today, each: the old
   usage line, `exit 2`. Holds, each: `exit 1` alone.
7. The gate passes on the branch's last commit and runs the new tests. `bash scripts/gate.sh; echo "exit $?"`.
   Today: `ok   test_add_then_list`, `ok   test_list_empty`, `ok   test_usage`, `exit 0`. Holds: those three
   lines, then `ok   test_search_match`, `ok   test_search_plain_text`, `ok   test_search_no_match`, and
   `ok   test_search_usage`, no `FAIL` line, `exit 0`. The pull request quotes this run, because no CI repeats
   it. Each test asserts the lines of "What search does" that this table gives it, output and exit code both.

   | Test | Lines |
   | --- | --- |
   | `test_search_match` | 1 and 5 |
   | `test_search_plain_text` | 2 and 9, and a word that starts with a dash |
   | `test_search_no_match` | 3 and 8 |
   | `test_search_usage` | 4, 6, and 7 |

8. The README describes `search` and its exit code.
   `tr '\n' ' ' < README.md | grep -o -e 'bin/notes search <word>' -e 'exits 1 when no note matches'`. Today: no
   output, exit 1. Holds: it prints both phrases. The reviewer reads the rest: the paragraph at
   `README.md:10-11` keeps its rule for every other command, keeps its last sentence, and names `search` as the
   one exception. The prose follows `~/.claude/docs/voice/written-for-people.md`.
9. The branch changes three files. `git diff --name-only main...HEAD`. Today: no output. Holds: `README.md`,
   `bin/notes`, `tests/run.sh`, and nothing else.

## Backlog sweep

The repo has no backlog file: `git ls-files` lists five files and none is one. The scoped sweep had no item to
read, so it gives no verdict and no backlog edit. The repo's GitHub issues could not be read from here.

## Calls Claude made

The first four are product calls and are Geoff's to overrule. One later commit reverses any of them.

1. `search` exits 1 on no match, as the brief says, against `README.md:10`. The other option is exit 0.
2. `README.md` joins the brief's two files, so that the README stays true.
3. The word matches anywhere in a note, never whole words only. "Contains the word" allows both readings, and
   this one finds more notes.
4. More than one argument is a usage error, and a quoted argument with spaces is one word. Joining the
   arguments as `add` does was the other option. A later change from error to accepted breaks no caller, and the
   reverse would.
5. The usage line reads `usage: notes add <text> | notes list | notes search <word>`.
6. An empty word counts as a missing word.
7. A missing notes file and a word with a newline both mean no match, exit 1.
8. Case is tested for ASCII letters only.
9. The matcher is `grep -i -F -e`, with the two guards.
10. The four tests have fixed names and a fixed share of the behavior, so that done item 7 can fail.
11. The README check in done item 8 looks for two phrases, and the reviewer reads the rest of the paragraph.
12. The plan is 40 minutes, from the two like tasks.
13. The goal names the spec by absolute path, and nobody commits `spec.md` for this task.
14. The task session runs on Sonnet at high effort: the spec leaves it no design call.
15. The footprint check compares against `main`, because `origin/main` didn't resolve in this checkout.
