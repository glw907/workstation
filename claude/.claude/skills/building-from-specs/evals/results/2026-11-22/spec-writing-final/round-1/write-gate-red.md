# Spec: notes search

Written 2026-11-22 from `brief.md`, against commit `18fc5cb` on `main`. One task, one pull request, 40 minutes.

## One thing differs from the brief

The brief says the work "is done when the search works as above and the gate passes." The gate fails on `main`
today, before any work, and for a reason the search doesn't touch:

```text
$ bash scripts/gate.sh; echo "exit=$?"
ok   test_add_then_list
ok   test_list_empty
ok   test_usage
FAIL test_export_csv
exit=1
```

`test_export_csv` (`tests/run.sh:15` to `:17`) runs `bin/notes export`, and `bin/notes` has no `export` command.
`git log --oneline -S'export'` prints one commit, `18fc5cb Add the notes tool`, so the test arrived with the tool
and the command never did. Two runs gave the same output.

Only two changes turn the gate green: build `export`, or remove its test. The first adds a command the brief
doesn't have. The second drops a test whose purpose only you know. Nobody could be asked, so I decided this:

- The task leaves `test_export_csv` as it is. It doesn't build `export`, and it doesn't remove, skip, or edit the
  test.
- The done item for the gate becomes "the gate fails on `test_export_csv` and on nothing else" (item 8).
- The pull request is marked ready with the gate red on that one test. This is a one-time exception to two
  rules: `building-from-specs` "Gates and review", which wants a passing gate first, and `CLAUDE.md`'s "keep
  working until every gate passes". For this task, item 8 is the gate. Approving this spec approves the
  exception. The merge is still yours, by number.

I passed over making the task wait for a green gate, because that stops the search until you rule on a command
the brief never mentions. Reversing my choice costs no code. If you would sooner settle the export test first,
say which way (remove the test, or build `export` under its own spec), and item 8 changes to "the gate exits 0"
before launch.

## Intent

"I want to find a note without scrolling through the whole list."

The goal is a new command, `bin/notes search <word>`, that prints every note containing the word, oldest first.

These are not goals: an `export` command, any change to `test_export_csv`, any change to what `add` and `list`
do, a README change, patterns, whole-word matching, flags, highlighting, and line numbers.

The work fails if the word is ever read as a pattern, if `search` writes to the notes file, if `add` or `list`
change, or if the gate gains a second failing test.

## Behavior

The brief settles the first four rows and the missing word in the fifth. The empty word and the last three rows
are my calls on cases it leaves open, and "Calls Claude made" lists them.

| Case | Result |
| --- | --- |
| One or more notes contain the word | Prints each one, whole and unchanged, in file order. Exits 0. |
| Letter case | Ignored in both the word and the notes. |
| Characters such as `.`, `*`, `[`, `\`, and a leading `-` | Matched as the characters themselves. |
| No note contains the word | Prints nothing on stdout or stderr. Exits 1. |
| No word, or an empty word (`""`) | Prints the usage line on stderr. Exits 2. |
| The word sits inside a longer word | Matches. `rope` finds `ROPES`. |
| More than one argument | Joined with single spaces into one text, as `add` does. |
| The notes file doesn't exist | Same as no match: prints nothing and exits 1. |

The usage line becomes `usage: notes add <text> | notes list | notes search <word>`. It stays one line on stderr
with exit 2, and an unknown command prints the same line.

## Approaches

| Approach | Trade-off |
| --- | --- |
| `grep -iF -e "$word" -- "$file"` behind a file check | One line. Its exit statuses already match the brief's 0 and 1. Needs the file check, because a missing file makes it exit 2. |
| A bash loop that compares `${line,,}` with `${word,,}` | No outside program, but more code, and the word must be quoted inside the comparison or bash reads it as a glob. |
| `awk` with `index(tolower($0), tolower(word))` | Plain text by construction, but `awk -v` rewrites backslashes in the word, so the word has to travel through the environment. |

The pick is `grep`. The task changes approach only if a done item can't be met with it, and records why under
`## Decisions`.

The two passed-over approaches are assembled from documented pieces, and each trade-off rests on a probe. In
bash, with `line='Coil the ROPES'` and `word='c*s'`, `[[ ${line,,} == *${word,,}* ]]` matches and
`[[ ${line,,} == *"${word,,}"* ]]` doesn't. `awk -v w='a\b' 'BEGIN{print length(w)}'` prints `2`, and the same
word read from `ENVIRON` gives `3`.

## Sources and labels

`grep -iF -e` is documented. `grep --help` on this machine (GNU grep 3.12) says:

```text
  -F, --fixed-strings       PATTERNS are strings
  -e, --regexp=PATTERNS     use PATTERNS for matching
  -i, --ignore-case         ignore case distinctions in patterns and data
```

`man grep` says: "Normally the exit status is 0 if a line is selected, 1 if no lines were selected, and 2 if an
error occurred."

I probed it against the six notes in "The task's goal". `<file>` is that notes file.

```text
$ grep -iF -e rope -- <file>        -> buy rope / Coil the ROPES, exit=0
$ grep -iF -e r.pe -- <file>        -> no output, exit=1
$ grep -iF -e -v -- <file>          -> flag -v means verbose, exit=0
$ grep -iF -e '2*3' -- <file>       -> cost [x] 2*3 a\b, exit=0
$ grep -iF -e '[a-z]' -- <file>     -> no output, exit=1
$ grep -iF -e 'a\b' -- <file>       -> cost [x] 2*3 a\b, exit=0
$ grep -iF -e 'rope buy' -- <file>  -> no output, exit=1
$ grep -iF -e rope -- <missing>     -> "No such file or directory" on stderr, exit=2
$ grep -iF -e "" -- <file>          -> every note, exit=0
$ grep -i -e r.pe -- <file>         -> buy rope / Coil the ROPES, exit=0
$ grep -i -e '2*3' -- <file>        -> tide 5.30 / cost [x] 2*3 a\b, exit=0
```

The probes with a missing file and an empty word are why the file check and the empty-word check come before
`grep`. The last two probes are the pattern reading that item 3 has to catch. The work adds no Claude Code mechanism, so no Anthropic docs
page applies.

## When it goes wrong

Exit statuses are 0 for a match, 1 for no match or no notes file, and 2 for a usage error. `search` only reads,
so a failure can't damage the notes. It has no size limit: `grep` reads the file as a stream. Case folding
follows `grep` and the user's locale, and the tests use ASCII only. Two cases are left undefined and untested: a
word that contains a newline, and a notes file that exists but can't be read.

## Assumptions, hosting, backlog

No assumption spans tasks, because there is one task. The work adds no project, service, or running
infrastructure, so it has no host to choose.

The scoped backlog sweep has nothing to read. `git ls-files` lists five files (`README.md`, `bin/notes`,
`brief.md`, `scripts/gate.sh`, `tests/run.sh`), none of them a backlog, and `git grep -n -i -e backlog -e todo`
has 0 hits. So there are no verdicts and no backlog edits, and no full sweep is due. I dispatched no sweep
reader, because it would have had no file to read. The export test is the one loose end, and it is in "One thing
differs from the brief" instead of a backlog.

## Files

The task changes `bin/notes` and `tests/run.sh`, as the brief says. The searches ran with `git grep -n -e`.

| Search | Hits | Disposition |
| --- | --- | --- |
| `usage` | 5 | `bin/notes:7` changes (the usage line). `tests/run.sh:12` and `:13` stay: `test_usage` checks only the first word, `usage:`, and still passes. `tests/run.sh:18` is the run list, see the `export` row. `brief.md:9` is the design input. |
| `notes list` | 4 | `bin/notes:7` changes (same line). `README.md:4` stays, see below. `tests/run.sh:7` and `:10` stay. |
| `notes add` | 4 | `bin/notes:7` changes (same line). `README.md:3` stays. `tests/run.sh:7` and `:16` stay. |
| `search` | 3 | All three are in `brief.md` (lines 1, 7, 12). Nothing in the code uses the name yet. |
| `export` | 3 | `tests/run.sh:15` and `:16` stay untouched. `:18` is the run list: it changes to gain the new test names, in any order, and keeps `test_export_csv`. |
| `NOTES_FILE` | 5 | `bin/notes:3` stays: `search` reads the same `$file`. `README.md:3` stays. `tests/run.sh:7`, `:10`, and `:16` stay. |

`README.md` describes `add` and `list` and will not mention `search`. The brief fixes the file list at two files,
so the README stays out of this task, and the pull request names it under `## For Geoff`.

## Commands and the denials log

The log has three entries in the last 30 days (2026-10-23 to 2026-11-22): a force push to `main`, an `rm -rf`
outside the working folder, and a fetch from an unknown host. The task runs `bash scripts/gate.sh`, `bin/notes`
with `NOTES_FILE` set to a `mktemp` path, a plain push of its own branch, and the `gh` pull request commands.
None of them matches an entry. The task needs no web fetch, because the `grep` facts it needs are quoted above.
A new test never runs `rm -r`. Each new test takes its notes path from `mktemp`. The one that needs a path with
no file follows `test_list_empty`: `mktemp`, then `rm -f` on that one file.

## Before launch

- `spec.md` is committed to `main` and pushed. The task's worktree starts from the remote's default branch, and
  today the file exists only in this checkout, uncommitted.
- The four checks in `building-from-specs` "Launching a task" run on launch day. `claude-worktree-busy` isn't
  reachable from where this spec was written, so none has run. The task needs no secret beyond the `gh` sign-in.
- The remote runs no CI on pull requests (`.workstation/remote.txt`: "the gate on a branch's last commit is its
  only full run"). `example/notes` is public and its default branch is `main`. The task waits on no CI.
- The repo has no `docs/STATUS.md`, and the work changes no other repo.

## The task: add `notes search`

It waits for no other task, and its pull request is the only merge. Its files are `bin/notes` and `tests/run.sh`.
`standards:diff-reviewer` reads it, on Opus at high. It touches no sign-in or data path and renders no UI, so it
needs no other reviewer. The task session runs on Sonnet at high: this spec has made the judgment calls.

The plan is 40 minutes. `task-report --since 2026-11-01` shows two like tasks in this repo, each a command
change with its tests: "Add notes list" took 34 minutes with no fix round, and "Let notes add read stdin" took 41
with one. "Add the usage test" took 12 and was a test alone, so it isn't a like task. Nothing the task drives
adds a wait. The goal's time clause is `or stop after 80 minutes`.

### The task's goal

Items 1 to 7 use these six notes. Run from the repo root.

```bash
export NOTES_FILE=$(mktemp)
bin/notes add "buy rope"
bin/notes add "call Sam"
bin/notes add "Coil the ROPES"
bin/notes add "tide 5.30"
bin/notes add "flag -v means verbose"
bin/notes add 'cost [x] 2*3 a\b'
```

I ran every command below on `18fc5cb`. Today each `bin/notes search` command in items 1 to 7 gives the same
result: nothing on stdout, `usage: notes add <text> | notes list` on stderr, and exit 2. Each item fails today
because `search` doesn't exist, which is what the task fixes.

1. `bin/notes search rope; echo "exit=$?"` prints `buy rope`, then `Coil the ROPES`, then `exit=0`. This shows
   containment, oldest first, and a word inside a longer word.
2. `bin/notes search SAM; echo "exit=$?"` prints `call Sam`, then `exit=0`. With item 1, this shows the match
   ignores case in both directions.
3. The word is plain text. `bin/notes search r.pe; echo "exit=$?"` and
   `bin/notes search '[a-z]'; echo "exit=$?"` each print only `exit=1`. `bin/notes search 5.30` prints
   `tide 5.30` alone. `bin/notes search -v` prints `flag -v means verbose` alone. `bin/notes search '2*3'` and
   `bin/notes search 'a\b'` each print `cost [x] 2*3 a\b` alone.
4. `bin/notes search anchor; echo "exit=$?"` prints only `exit=1`, with nothing on stderr.
5. `bin/notes search; echo "exit=$?"` prints nothing on stdout, prints
   `usage: notes add <text> | notes list | notes search <word>` on stderr, and then `exit=2`.
   `bin/notes search ""` and `bin/notes bogus` give the same line and the same exit. Today all three exit 2 with
   the old line, so the item fails on the line's text.
6. `f=$(mktemp); rm -f "$f"; NOTES_FILE=$f bin/notes search rope; echo "exit=$?"; [ -e "$f" ] || echo "no file"`
   prints `exit=1`, then `no file`, with nothing on stderr. Today it prints the old usage line, `exit=2`, and
   `no file`.
7. `bin/notes search buy rope; echo "exit=$?"` prints `buy rope`, then `exit=0`.
   `bin/notes search rope buy; echo "exit=$?"` prints only `exit=1`: no note contains the text `rope buy`, though
   two contain `rope`.
8. `bash scripts/gate.sh; echo "exit=$?"`, run on the branch's last commit, prints an `ok` line for the three
   tests that pass today and for seven new ones, `FAIL test_export_csv` as its only `FAIL` line, and `exit=1`
   last. The test lines come in the run list's order, and any order passes. The seven are `test_search_match`,
   `test_search_case`, `test_search_plain_text`, `test_search_no_match`, `test_search_missing_word`,
   `test_search_no_file`, and `test_search_phrase`, one for each of items 1 to 7, and each asserts every
   command in its item. Each takes its notes path from `mktemp` and never reads `~/.notes`.
   `bash scripts/gate.sh | grep -c '^ok   test_search_'` prints `7`, and today prints `0`.
   `bash scripts/gate.sh | grep -v '^ok   '` prints exactly `FAIL test_export_csv`, today and when done.
9. `git diff --name-only main...HEAD` on the branch prints `bin/notes` and `tests/run.sh` and nothing else. Today
   on `main` it prints nothing. The diff leaves lines 15 to 17 of `tests/run.sh`, the `test_export_csv` function,
   unchanged.
10. One pull request against `main` carries the work, written by `building-from-specs` "The pull request" and
    reviewed by "Gates and review". Its first paragraph says the gate is red on `test_export_csv` alone and that
    the test waits for Geoff's ruling. `## For Geoff` names that test and the README. The body quotes the output
    of items 1 to 9 from the last commit, and the task score carries `"planPathMin": 40`. The body follows the
    voice standard that section names, `~/.claude/docs/voice/written-for-people.md`, and commit messages are
    in the imperative mood.

## The fresh read

One reader with no context read this spec and reran its commands. Its findings fell into three piles.

- Fixed here as minor calls: three done items that couldn't fail or couldn't be checked (3, 6, and 7), the
  order of the run list, one path rule for test files, the labels on the passed-over approaches, the second
  rule the red-gate exception touches, and one wrong line number.
- Answered already: the launch checks belong to launch day, and the backlog sweep had no file to read.
- Only you can answer: whether the export test is removed or `export` is built. Nothing in this spec waits on
  it.

## Calls Claude made

1. The gate item is narrowed and the pull request goes ready with one known red test. The reasons and the way
   to reverse it are in "One thing differs from the brief".
2. A match is containment, so `rope` finds `ROPES`. The brief says "contains the word". I passed over
   whole-word matching. Reversing changes one `grep` flag and one test.
3. An empty word counts as a missing word and exits 2. Without that, `""` would print every note.
4. More than one argument is joined with spaces, because `add` already builds its text that way. I passed over
   exiting 2 on a second argument. Reversing changes one line and one test.
5. A missing notes file is a no-match with exit 1, in line with `list`, which prints nothing when the file
   doesn't exist.
6. The usage line's exact text is the one under "Behavior".
7. The README stays unchanged, because the brief names two files.
8. The method is `grep -iF -e`, and the seven test names are fixed so that item 8 can be checked by count.
9. The plan is 40 minutes, the session model is Sonnet at high, and the reviewer runs on Opus at high.
10. I could not open `~/.claude/docs/voice/written-for-people.md` from here. This spec follows the
    `writing-voice` skill's shape rules instead.
