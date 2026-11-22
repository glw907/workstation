# Spec: notes search

Written 2026-11-22 from `brief.md`, the design Geoff approved in conversation. It follows
`building-from-specs` and its guide, `references/writing-a-spec.md`.

This spec adds one command, `bin/notes search <word>`, in one task that ends in one pull request. The
brief settles the main behavior. It leaves several inputs unsettled, and the brief's two-file list leaves
out the README, which a search of the repo turns up. Nobody could answer a question while this was
written, so each of those is decided here and numbered under "Calls Claude made". Four of them are
product calls that Geoff may want to reverse before launch: calls 1, 2, 3, and 8. Nothing else waits
for him.

## What Geoff asked for

"I want to find a note without scrolling through the whole list."

The goal is a `search` command that prints every note containing a word, oldest first, ignoring case,
with the word read as plain text and never as a pattern. A search that finds nothing prints nothing and
exits 1. A search with no word prints the usage line and exits 2, and the usage line names the new
command.

These are not goals: patterns or wildcards, a whole-word mode, a search for several words at once, line
numbers or highlighting in the output, a README change, a change to the gate, and a rework of the test
runner.

The work has failed if any of these is true after the merge:

- A character in the word acts as a pattern, an option, or a separator.
- `search` writes to the notes file or creates it.
- `add` or `list` behaves differently than today.
- The gate passes while a new test never ran. "The test runner's trap" below shows how that can happen.

## How search behaves

A note is one line of the notes file. The README says `add` "appends a line", and `bin/notes:5` appends
with `>>`, so file order is oldest first. `search` prints each matching line whole, exactly as `list`
prints it, to standard output.

| Input | Standard output | Standard error | Exit | Source |
| --- | --- | --- | --- | --- |
| A word that some notes contain | Those notes, in file order | Nothing | 0 | Brief |
| The same word in another case | The same notes | Nothing | 0 | Brief |
| A word that is part of a longer word, such as `rope` in `tightrope` | That note too | Nothing | 0 | Call 1 |
| A word with pattern or option characters, such as `a.c`, `[`, or `-v` | Only notes that hold those exact characters | Nothing | 0 or 1 | Brief |
| A word no note contains | Nothing | Nothing | 1 | Brief |
| Any word when the notes file doesn't exist | Nothing | Nothing | 1 | Call 4 |
| A word in a note that holds a byte the locale can't read as text | That note, whole | Nothing | 0 | Call 15 |
| A word that holds a line break | Nothing | Nothing | 1 | Call 5 |
| No word | Nothing | The usage line | 2 | Brief |
| An empty word, `""` | Nothing | The usage line | 2 | Call 3 |
| Two or more words, such as `search buy rope` | Nothing | The usage line | 2 | Call 2 |

The usage line is one line, the same for every wrong call, and it goes to standard error as it does
today (`bin/notes:7`):

```text
usage: notes add <text> | notes list | notes search <word>
```

## Approaches considered

Three ways to match were probed on this machine (GNU grep 3.12, GNU bash 5.3.9).

**`grep -a -i -F -e <word> -- <file>`. Documented, and the pick.** `grep --help` says `-F` means "PATTERNS
are strings", `-i` means "ignore case distinctions in patterns and data", `-e` means "use PATTERNS
for matching", and `-a` is "equivalent to --binary-files=text". Probes against a six-note file gave the
exit codes the brief wants with no translation: a match exits 0, no match exits 1. `a.c` matched only
`a.c is a file`, `-v` after `-e` matched only `use -v flag`, and `[` exited 1 with no error. It costs
three guards and the `-a` flag, each shown by a probe:

- A missing file prints `grep: ...: No such file or directory` and exits 2.
- An empty word matches every line.
- A word that holds a line break is read as two words: `$'zzz\nabc'` printed `abc`.
- Without `-a`, a matching note that holds a byte that isn't valid UTF-8 is not printed. grep prints
  `grep: ...: binary file matches` in its place. With `-a` the note is printed.

**A loop in bash that lowercases each line and the word.** Assembled from documented pieces. The probe
`while IFS= read -r line; do [[ ${line,,} == *"${w,,}"* ]] && printf '%s\n' "$line"; done < file`
printed the right notes for `w=ROPE` and for a word with a backslash. It needs no guard for the line break, but it is
more code than one `grep` call, and it reads the file a line at a time in the shell.

**`awk` with `index(tolower($0), tolower(w))`.** Assembled from documented pieces. Passing the word with
`-v` failed the plain-text rule in a probe: the word `a\tb` didn't match the note `a\tb literal`,
because `-v` read `\t` as a tab. Passing it through `ENVIRON` worked. It adds a second language for no
gain over grep.

The pick is a method call, so the task session may build the match another way if it meets every done
item. A throwaway copy of `bin/notes` built on grep, kept outside the repo and now discarded, met done
items 1 to 9 on 2026-11-22. That shows the items can be met together.

## What happens when it goes wrong

Three exit codes carry meaning: 0 for a match, 1 for no match, 2 for a wrong call. `search` takes
exactly one word.

Case folding is promised for the letters A to Z only. Beyond those it follows the shell's locale: `grep -i -F -e 'éclair' <file>` found the note `Éclair` under `en_US.UTF-8`, and the same command with
`LC_ALL=C` in front missed it. No done
item tests a letter outside A to Z.

A notes file that exists and can't be read is outside the done items. A probe ran `chmod 000` on the notes file and
searched it as an ordinary user. With the grep approach it printed `grep: ...: Permission denied` and
exited 2, the same code as a wrong call. That is recorded so
that it surprises nobody. It is not a requirement, and no test covers it (call 10).

The notes file has no size limit. grep reads it once.

The repo runs no CI on pull requests (`.workstation/remote.txt`), so the gate run on the branch's last
commit is the only full run. A commit made after that run, such as a review fix, needs a new gate run
before the pull request is marked ready.

### The test runner's trap

`tests/run.sh:2` says it "Runs every test_* function". It doesn't. Line 15 loops over a written list of
three names. A probe added a function `test_never_listed() { false; }` to a copy and left the list
alone. The gate printed the same three `ok` lines and exited 0. A new test that isn't added to the list
never runs, and the gate still passes. Done item 10 therefore names each new test and checks for its
`ok` line.

A second trap sits beside it. `tests/run.sh:3` sets no `-e`, so a test function returns the status of
its last command alone. A test whose early checks fail still prints `ok` if its last check passes. Done
item 10 therefore also runs the new tests against today's `bin/notes`, where each one must fail.

The task adds names to the list and leaves the loop as it is (call 9).

## Files

The file list comes from six searches of the tracked files, run as `git grep -nF -- '<text>'` on commit
399e8de.

| Search | Hits | Where |
| --- | --- | --- |
| `notes list` | 4 | `README.md:4`, `bin/notes:7`, `tests/run.sh:7`, `tests/run.sh:10` |
| `notes add` | 3 | `README.md:3`, `bin/notes:7`, `tests/run.sh:7` |
| `usage` | 5 | `bin/notes:7`, `brief.md:9`, `tests/run.sh:12`, `tests/run.sh:13`, `tests/run.sh:15` |
| `bin/notes` | 7 | `README.md:3`, `README.md:4`, `brief.md:7`, `brief.md:10`, `tests/run.sh:7`, `tests/run.sh:10`, `tests/run.sh:13` |
| `search` | 3 | `brief.md:1`, `brief.md:7`, `brief.md:12` |
| `test_` | 5 | `tests/run.sh:2`, `tests/run.sh:6`, `tests/run.sh:9`, `tests/run.sh:12`, `tests/run.sh:15` |

What each hit means for the task:

- `bin/notes:7` changes. It holds the usage line, and the `case` above it gains the `search` branch.
- `tests/run.sh:15` changes. The new test names join the list. New test functions go above it.
- `tests/run.sh:6` to `tests/run.sh:13` stay as they are. Those are today's three tests. `test_usage`
  checks only that the line starts with `usage:`, so it passes with the new line unchanged.
- `tests/run.sh:2` stays as it is. The comment is wrong today, and correcting it belongs with a rework
  of the loop, which is not a goal.
- `README.md:3` and `README.md:4` are dismissed. The README describes `add` and `list` and will not
  mention `search`. The brief fixes the files at two, so the README stays out (call 8).
- `brief.md` is dismissed. It is the design this spec is written from.

`scripts/gate.sh` matched no search. It runs `tests/run.sh` and needs no change.

## Commands and the denials log

`.workstation/denials.log` holds three refusals in the 30 days to 2026-11-22. Each was read against
what the task does.

| Refused | What the task does instead |
| --- | --- |
| `git push --force origin main` | It pushes only the branch it created, with no force flag. A fix after a push is a new commit, never an amended one. |
| `rm -rf ~/.notes.bak`, a recursive delete outside the working folder | Every test and every check sets `NOTES_FILE` to a `mktemp` file and never touches `~/.notes`. New tests use no recursive delete. Today's `test_list_empty` runs `rm -f` on one `mktemp` file, and the gate ran in Claude Code on 2026-11-22 without a refusal. |
| WebFetch of `https://example.invalid/notes`, an unknown host | The task needs no web page. grep's behavior is read from `grep --help` on the machine. |

Every command line in the done items was run in Claude Code on 2026-11-22: the two `mktemp` files, each
`bin/notes search` call, `cmp`, `bash scripts/gate.sh`, and the `cp` and `git show` of item 10. The
spec gives the task session no other command line to run. The branch, the push, the draft pull
request, and the review are owned by `building-from-specs`, in "A session at work", "Gates and review",
and "The pull request". This session could not run those: it was told to commit nothing, and the
sandbox refused `api.github.com`.

## The task: notes-search

There is one task, so there is no merge order and nothing it waits for. No assumption is shared between
tasks.

**Goal.** `bin/notes search <word>` behaves as the table in "How search behaves" says, the new tests
run in the gate and can fail, and the gate passes on the branch's last commit.

**Files.** `bin/notes` and `tests/run.sh`, and no others.

**Reviewer.** `standards:diff-reviewer`, on Opus at high. The task touches no sign-in path, writes no
data, and renders no UI, so no second reviewer reads it (call 14).

**Model.** The task session runs on Sonnet at high (call 12).

**Minutes.** 40. `.workstation/task-report.txt` lists three merged tasks in this repo since 2026-11-01.
The two that changed a command are the like ones: "Add notes list" took 34 minutes against 30 planned,
and "Let notes add read stdin" took 41 against 30, with one fix round. "Add the usage test" took 12 and
is not like this task, because it changed no command. Both like tasks ran past 30, so this one takes
the slower figure, rounded. The task drives no CI, timer, or idle limit, so no wait is added. The
goal's time clause is `or stop after 80 minutes`.

### Done items

Every command runs from the repo root on the branch's last commit. Items 1 to 9 use two files of notes
and a copy of the first:

```bash
f=$(mktemp)
printf '%s\n' 'buy rope' 'Call the ROPE shop' 'a.c is a file' 'abc' 'tightrope walk' 'use -v flag' > "$f"
cp "$f" "$f.orig"
g=$(mktemp)
printf 'caf\xe9 rope\nbuy rope\n' > "$g"
```

1. `NOTES_FILE=$f bin/notes search rope` prints `buy rope`, `Call the ROPE shop`, and `tightrope walk`,
   one per line in that order, prints nothing on standard error, and exits 0.
   `NOTES_FILE=$f bin/notes search ROPE` does the same.
2. Run as `NOTES_FILE=$f bin/notes search <word>`, each of these prints only the note named and exits 0:
   `a.c` prints `a.c is a file`, `-v` prints `use -v flag`, and `'the rope'` prints `Call the ROPE shop`.
   Each of `'['`, `'*'`, and `'a?c'` prints nothing on either stream and exits 1.
3. `NOTES_FILE=$f bin/notes search zzz` prints nothing on either stream and exits 1.
4. `NOTES_FILE=$f.gone bin/notes search rope`, where no file `$f.gone` exists, prints nothing on either
   stream and exits 1, and `$f.gone` still doesn't exist afterward.
5. `NOTES_FILE=$f bin/notes search` prints nothing on standard output, prints exactly
   `usage: notes add <text> | notes list | notes search <word>` on standard error, and exits 2.
   `bin/notes bogus` prints the same line and exits 2.
6. `NOTES_FILE=$f bin/notes search ""` and `NOTES_FILE=$f bin/notes search buy rope` each do what item 5
   says.
7. `NOTES_FILE=$f bin/notes search $'zzz\nabc'` prints nothing on either stream and exits 1.
8. `NOTES_FILE=$g bin/notes search rope` prints nothing on standard error and exits 0, and
   `NOTES_FILE=$g bin/notes search rope | wc -l` prints 2. The first note in `$g` holds a byte that isn't
   valid UTF-8, and it is printed like the second.
9. After the commands of items 1 to 7, `cmp "$f" "$f.orig"` prints nothing and exits 0.
10. `bash scripts/gate.sh` exits 0 and prints no `FAIL` line. It prints an `ok` line for each of today's
    three tests and for each of these eight, which test items 1 to 8 in order:
    `test_search_finds_any_case_oldest_first`, `test_search_is_plain_text`, `test_search_no_match`,
    `test_search_missing_file`, `test_search_missing_word`, `test_search_empty_or_extra_word`,
    `test_search_newline_word`, and `test_search_odd_bytes`.
    `bash scripts/gate.sh | grep -c '^ok   test_search_'` prints 8 or more. The check below runs the same
    tests against today's `bin/notes` and prints the same number, because every new test fails there.
    The pull request quotes both outputs beside the hash of the commit they ran on.

```bash
d=$(mktemp -d); cp -r bin tests scripts "$d"; git show 399e8de:bin/notes > "$d/bin/notes"
bash "$d/scripts/gate.sh" | grep -c '^FAIL test_search_'
```

Each test checks standard output, standard error, and the exit code, and joins its checks so that one
failed check fails the test. The task may add more tests, each on the list at `tests/run.sh:15`.

### The same checks on today's code

All of these were run on commit 399e8de on 2026-11-22. The commands the first draft carried were run
twice, and the two runs printed the same output.

Every `search` command in items 1 to 8 printed nothing on standard output, printed
`usage: notes add <text> | notes list` on standard error, and exited 2. The `wc -l` in item 8 printed 0.
Items 1 to 4, 7, and 8 fail today because there is no `search` command. Items 5 and 6 already exit 2
today, and they fail on the text of the line, which doesn't name `search`. Both are what the task fixes.

Item 9 passes today, because today's code writes nothing on `search`. It can't fail for the reason the
task fixes. It is kept as a guard, since a search that changes the notes file is one of the failures
named at the top.

Item 10 fails today on both counts:

```console
$ bash scripts/gate.sh; echo "exit $?"
ok   test_add_then_list
ok   test_list_empty
ok   test_usage
exit 0
$ bash scripts/gate.sh | grep -c '^ok   test_search_'
0
$ d=$(mktemp -d); cp -r bin tests scripts "$d"; git show 399e8de:bin/notes > "$d/bin/notes"
$ bash "$d/scripts/gate.sh" | grep -c '^FAIL test_search_'
0
```

## Before launch

"Launching a task" in `building-from-specs` owns the launch command and its four checks. This is what
was true on 2026-11-22 and what is still owed.

- No session was working. `claude agents --json` printed `[]` at 22:28 UTC.
- `claude-worktree-busy` is not installed where this spec was written (`command not found`). The
  launching session runs it on the main checkout.
- The task needs no secret beyond the `gh` sign-in that pushes and opens pull requests.
- The remote is `example/notes` on GitHub, public, with `main` as its default branch, and it runs no CI
  on pull requests. That comes from `.workstation/remote.txt`. The live `gh repo view` was refused by
  the sandbox. The task needs no CI, so the launch has no CI to check.
- `spec.md` is not committed, because this session was told to commit nothing. A task worktree starts
  from `origin/main` and will not hold it. The goal's condition names the spec by the absolute path of
  the copy in the main checkout, and the review brief gives the same path (call 13).
- The repo's open GitHub issues were not read, because the sandbox refused `api.github.com`. The
  launching session reads them for any that names `bin/notes` or `tests/run.sh`, and brings a hit to
  Geoff before launch.

The task adds no project, service, or running infrastructure.

## Backlog sweep

The scoped sweep had nothing to read. The repo tracks five files, none of them a backlog, and has no
`docs` folder. GitHub issues could not be read from here, and "Before launch" lists that read as owed. There are no
verdicts and no backlog edits to approve.

## Calls Claude made

Calls 1, 2, 3, and 8 are product calls. The rest are method calls.

1. **A word matches inside a longer word.** `search rope` finds `tightrope walk`. The brief says
   "contains the word" and "plain text", and a search that shows one note too many serves "find a note"
   better than one that hides a note. Passed over: whole words only. Reversing adds grep's `-w` and
   changes one line of done item 1.
2. **Two or more words is a wrong call, exit 2.** The brief names one `<word>`. A phrase still works in
   quotes: `search "buy rope"`. Passed over: joining the words into one phrase, as `add` joins its text.
   The refusal is the cheaper one to reverse, because nobody comes to rely on an error, while joining
   would fix what several words mean.
3. **An empty word counts as no word, exit 2.** Otherwise `search ""` would print every note, which is
   `list`.
4. **No notes file means no match: nothing printed, exit 1.** This follows the brief's rule for a word
   no note contains, and `list` is already silent when the file doesn't exist. `search` never creates
   the file.
5. **A word that holds a line break matches nothing, exit 1.** No one-line note can contain it. Passed
   over: treating it as a wrong call.
6. **The usage line reads `usage: notes add <text> | notes list | notes search <word>`.** It extends
   today's line in today's form.
7. **Case folding is promised for A to Z only.** Other letters follow the locale.
8. **The README stays as it is.** The brief says the work changes `bin/notes` and `tests/run.sh`, and
   it marks that as not open, so the search hits in `README.md` are dismissed rather than added to the
   task. The README will describe two of three commands until it is changed. After the merge, one
   sentence fits "Direct changes" if Geoff asks for it: "`bin/notes search <word>` prints the notes
   that contain the word, ignoring case, and exits 1 when none does." The task session names this in
   the pull request's `## For Geoff` and files nothing, because the repo has no backlog file and making
   one would be a third changed file.
9. **The test runner's loop stays as it is.** The task adds names to the list. Done item 10 guards the
   trap for this task only. Making the loop find every `test_*` function would close it for good, and
   it is left for Geoff to ask for.
10. **An unreadable notes file is left to the tool.** No done item covers it.
11. **grep is the pick over a bash loop or awk**, and the task session may choose otherwise.
12. **The task session runs on Sonnet at high and the reviewer on Opus at high.** The spec settles each
    design question, which leaves edits and tests for the build. The skill sets the reviewer's model.
13. **The goal names the spec by absolute path.** Passed over: committing `spec.md` to `main` before
    launch, which the README's rule that work reaches `main` through a pull request speaks against.
14. **One reviewer.** `search` reads the notes file and writes nothing, so this is not data work.
15. **A note with a byte the locale can't read as text is still printed.** The fresh reader found that
    plain grep hides such a note behind `binary file matches`, and a search that hides a matching note
    misses what Geoff asked for. With grep the fix is `-a`.

## The fresh reader's questions

One reader with no context read this spec against the repo on 2026-11-22, on Fable at high. It re-ran
the searches, the line references, and the quoted outputs, and they held. Its findings fall in three
piles.

Answered already: where the README note goes in the pull request (`## For Geoff`, by "The pull
request" in `building-from-specs`, which the reader's sandbox couldn't open), and who runs
`claude-worktree-busy` (the launching session, by "Launching a task").

Minor calls, made and now in the spec:

- No done item searched with a capital word, so a build that folded only the notes would pass. Item 1
  gained `search ROPE`.
- Item 2 tried too few pattern characters for a build that drops grep. It gained `*` and `a?c`, and a
  phrase in quotes, which call 2 promises.
- A listed test can print `ok` with a failed check inside it. Item 10 gained the run against today's
  `bin/notes`.
- Nothing checked that `search` leaves the notes file alone. Item 9 is new.
- A note with a byte that isn't valid UTF-8 was hidden. Call 15 and item 8 are new.
- Every test now checks standard error, where the draft said only some did.
- Two sentences were wrong and are corrected: a count of unsettled inputs, and a claim that the spec
  names only two command lines.
- Three probes lacked their command lines, and the GitHub issues read was not listed as owed. Both
  are added.

Questions only Geoff can answer: none beyond calls 1, 2, 3, and 8.

The items the reader's findings added were run on today's code and on the throwaway copy after the
read. The spec has had no second fresh read since those edits.

One step was not done. `CLAUDE.md` asks that prose Geoff reads follow
`~/.claude/docs/voice/written-for-people.md`. Reading that file was refused twice, so this spec was
written to the `writing-voice` skill's shape rules alone.
