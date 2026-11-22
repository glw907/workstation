# Spec: notes search

Status: awaiting approval. One task, one pull request.

The owner said: "I want to find a note without scrolling through the whole list." The brief in
`brief.md` holds the settled design, and this spec builds it.

## What gets built

`bin/notes search <word>` prints every note that contains the word, oldest first. The match ignores
case, and the word is plain text, never a pattern, so `a.c` matches only `a.c`. A word inside a longer
word counts, so `rope` finds `ropes`. No match prints nothing and exits 1. A missing or empty word
prints the usage line to stderr and exits 2. The usage line becomes
`usage: notes add <text> | notes list | notes search <word>`. Nothing about `add` or `list` changes.

## What it rests on

- The gate is `bash scripts/gate.sh`, which runs `tests/run.sh`. Run on 2026-11-22, it printed `ok` for every test and exited 0.
- A test runs only when its name is in the `for` list at the bottom of `tests/run.sh`, and each test
  prints `ok   <name>` or `FAIL <name>`.
- `bin/notes search rope` prints the usage line and exits 2 today, so each new test fails before the
  work.
- The remote, `example/notes`, is public and runs no CI on pull requests. The gate on the branch's last
  commit is the only full run.

## Files

The task changes `bin/notes` and `tests/run.sh`, and `README.md`, which names the new command. `git grep -n usage` finds `bin/notes:7`, the usage
line, which changes, and three lines of `test_usage` in `tests/run.sh`, which stay: that test checks only
that the message starts with `usage:`.

## The task

One task on Sonnet at medium, reviewed by `standards:diff-reviewer`. Planned at 30 minutes, with a
time limit of 60. The last three tasks in this repo took 34, 12, and 41 minutes against plans of 30,
15, and 30, so 30 holds for a change of this size.

Each new test makes its own notes file with `mktemp` and adds `Buy rope`, `fix a.c`, `fix abc`, and
`ROPE ladder` in that order.

Done when each of these holds on the branch's last commit:

1. `bash tests/run.sh` prints `ok   test_search_finds`. The test asserts that `search rope` prints
   exactly `Buy rope` then `ROPE ladder` and exits 0. Today it prints no such line.
2. `bash tests/run.sh` prints `ok   test_search_plain_text`. The test asserts that `search a.c` prints
   only `fix a.c`, and that `search '.*'` prints nothing. Today it prints no such line.
3. `bash tests/run.sh` prints `ok   test_search_no_match`. The test asserts that `search zzz` gives
   empty stdout and exit 1. Today it prints no such line.
4. `bash tests/run.sh` prints `ok   test_search_missing_word`. The test asserts that `search` and
   `search ''` each exit 2 with the new usage line on stderr. Today it prints no such line.
5. `grep -c notes README.md` prints 1 or more.
6. `bash scripts/gate.sh` exits 0.

## Decisions

- The word is matched with `grep -iF`, so it is never a pattern and a leading dash is read as text
  through `--`.
- A search for two words is a usage error, since the brief names one word.
