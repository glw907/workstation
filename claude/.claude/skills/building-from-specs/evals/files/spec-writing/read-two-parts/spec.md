# Spec: notes search

Status: awaiting approval. One task, one pull request.

The owner's words: "I want to find a note without scrolling through the whole list."

## What gets built

`bin/notes search <word>` prints every note that contains the word, oldest first. The match ignores
case, and the word is plain text, never a pattern. A word that appears inside a longer word counts, so
`rope` finds `ropes`. No match prints nothing and exits 1. A missing or empty word prints the usage line
to stderr and exits 2. The usage line becomes `usage: notes add <text> | notes list | notes search <word>`.
A missing notes file counts as no match. Nothing about `add` or `list` changes.

## What it rests on

- The gate is `bash scripts/gate.sh`, which runs `tests/run.sh`. Run on 2026-11-22, it printed `ok` for
  every test and exited 0.
- A test runs only when its name is in the `for` list at the bottom of `tests/run.sh`.
- `bin/notes search rope` prints the usage line and exits 2 today, so the name is free.
- Work reaches `main` through a pull request to `origin`, `github.com/example/notes`.

## Files

The task changes `bin/notes`, `tests/run.sh`, and `README.md`. `git grep -n usage -- bin tests` found
4 hits. `bin/notes:7` holds the usage line, which changes. The other three are `test_usage` in
`tests/run.sh`, which stays as it is, since it checks only that the message starts with `usage:`.

## The task

Sonnet at medium, 30 minutes, reviewed by `standards:diff-reviewer`, an agent in the `standards`
plugin installed on the workstation. The implementation is the builder's choice. Each new test makes
its own notes file with `mktemp` and adds `Buy rope`, `fix a.c`, `fix abc`, and `ROPE ladder` in that
order.

Done when each of these holds:

1. `bash tests/run.sh` prints `ok   test_search_finds`. The test asserts that `search rope` prints
   `Buy rope` then `ROPE ladder` and exits 0. Today it prints no such line.
2. `bash tests/run.sh` prints `ok   test_search_plain_text`. The test asserts that `search a.c` prints
   only `fix a.c`, and that `search '.*'` prints nothing and exits 1. Today it prints no such line.
3. `bash tests/run.sh` prints `ok   test_search_no_match`. The test asserts that `search zzz` gives empty
   stdout and exit 0. Today it prints no such line.
4. `bash tests/run.sh` prints `ok   test_search_missing_word`. The test asserts that `search` and
   `search ''` each give exit 2 and the new usage line on stderr. Today it prints no such line.
5. The README names the new command: `grep -c "notes search" README.md` prints 1. Today it prints 0.
6. `bash scripts/gate.sh` exits 0.
