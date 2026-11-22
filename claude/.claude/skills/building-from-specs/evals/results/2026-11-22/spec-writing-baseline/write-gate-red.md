# Spec: notes search

This spec turns the settled design in `brief.md` into one task that ends in one pull request. The task adds
`bin/notes search <word>` and its tests. One finding changes what the brief approved: the gate fails on `main`
today, for a reason that has nothing to do with search, so "the gate passes" can't be met by the search work
alone. I decided that the task takes the one failing test out of the run, in the open, and leaves its text in
place. Approving this spec approves that call. Nothing else waits for you.

## The gate is red on main today

`bash scripts/gate.sh` on `main` at `18fc5cb`, run three times on 2026-11-22 with the same output each time:

```text
ok   test_add_then_list
ok   test_list_empty
ok   test_usage
FAIL test_export_csv
exit=1
```

`test_export_csv` (`tests/run.sh:15-17`) runs `bin/notes export` and expects `1,"buy rope"`. No `export` command
exists. `bin/notes export` prints the usage line and exits 2. A search for `export` over the tracked files finds
three hits, all in `tests/run.sh`, so no doc, brief, or code says whether an export command is wanted.

The brief says the work is done "when the search works as above and the gate passes", and it names two files and
one task. The process adds that a pull request is ready only when the gate passes, and `.workstation/remote.txt`
says the repo runs no CI on pull requests, so the gate on the branch's last commit is the only full run. A task
that builds search and nothing else would end with a red gate and a pull request that can never be ready.

The four ways out, and what each costs:

| Option | What it does | What it costs |
| --- | --- | --- |
| Skip the test in the open (picked) | The runner stops running `test_export_csv` and prints a `skip` line for it on every run. The test's text stays. | The gate no longer checks export. Two lines to undo. |
| Delete the test | Removes lines 15 to 17 and the name from the run list. | Loses the only record of what export should print. |
| Build `notes export` | Adds a second command so the test passes. | A command nobody asked for, designed from one test line. That is a new spec. |
| Leave the gate red | The task builds search only, and its goal says the gate's one failure is `test_export_csv`. | The pull request can't be marked ready, and a red gate hides the next real failure behind its exit code. |

I picked the skip because it keeps every line of the brief true, a later commit undoes it most cheaply, and the
gate's own output keeps saying that a test is out of the run. To reverse the call, put the name back in the run
list and delete the `skip` line: the test runs again and the gate goes red again until export is built or the
test is deleted. Whether export is wanted is your call, and the pull request carries it under `## For Geoff`.

## Intent

In your words: "I want to find a note without scrolling through the whole list."

The goal is one new command, `bin/notes search <word>`, that prints every note containing the word, oldest
first, ignoring case, with the word read as plain text.

These are not goals: patterns or wildcards, whole-word matching, line numbers or colour in the output, a change
to `add` or `list`, an export command, a README change, or a backlog for this repo.

The work has failed if any of these is true when the pull request is ready:

- A character in the word acts as a pattern or an option, so `search 3.50` finds `3x50` or `search -v` fails.
- A search that finds nothing exits 0, or a search that finds something exits non-zero.
- The gate is green because a test stopped running and nothing says so.
- A test reads or writes the real `~/.notes`.

## How search behaves

The word is everything after `search`, joined by single spaces, the same way `add` joins its text
(`bin/notes:5`). So `bin/notes search locker key` and `bin/notes search "locker key"` are the same search.

| Case | Standard output | Standard error | Exit |
| --- | --- | --- | --- |
| One or more notes contain the word | Each matching note, whole and exactly as stored, in file order | Nothing | 0 |
| No note contains the word | Nothing | Nothing | 1 |
| The notes file doesn't exist | Nothing | Nothing | 1 |
| The word has a newline in it | Nothing | Nothing | 1 |
| No word, or an empty word (`search ""`) | Nothing | The usage line | 2 |
| An unknown command | Nothing | The usage line | 2 |

The usage line is exactly `usage: notes add <text> | notes list | notes search <word>`.

The word is checked before the file. A search with no word exits 2 whether or not the notes file exists.

"Contains" means the word appears anywhere in the note, so `search rope` finds `buy ropes`. File order is oldest
first, because `add` appends. Case is ignored the way `grep -i` ignores it in the user's locale.

## Approaches to the match

| Approach | Label | Trade-off |
| --- | --- | --- |
| `grep -aiF -- "$word" "$file"` (picked) | Documented, and probed below | One line. Its exit status is already 0 for a match and 1 for none. It needs three guards, listed under "When it goes wrong". |
| A bash loop that lowercases each line and the word and compares them | Assembled from documented pieces, not probed | No outside program, but more lines, and the exit status is worked out by hand. |
| `awk` with `index(tolower($0), tolower(word))` | Assembled from documented pieces, not probed | Same result, with a second language in a one-file bash tool and care needed to pass the word unescaped. |

The pick is `grep`. The repo's own practice supplies the rest: a usage line on standard error with exit 2
(`bin/notes:7`), and `"$*"` to join arguments (`bin/notes:5`). The `skip` line is invented: it is one `echo` in
the repo's hand-written test runner, which has no skip feature of its own. The task proposes no Claude Code
mechanism beyond the launch that `building-from-specs` owns.

### Sources and probes

From `man grep` on this machine (GNU grep 3.12):

- `-F`: "Interpret PATTERNS as fixed strings, not regular expressions."
- `-i`: "Ignore case distinctions in patterns and input data, so that characters that differ only in case match
  each other."
- `-a`: "Process a binary file as if it were text; this is equivalent to the --binary-files=text option."
- Exit status: "Normally the exit status is 0 if a line is selected, 1 if no lines were selected, and 2 if an
  error occurred."

The probes ran on 2026-11-22 with GNU grep 3.12, bash 5.3.9, and `LANG=en_US.UTF-8`, against a file holding
`buy rope`, `call Ann`, `Rope locker key`, `cost is 3.50`, `cost is 3x50`, and `use -v flag`, one per line.

| Probe | Command | Output | Exit |
| --- | --- | --- | --- |
| P1 case and order | `grep -iF -- rope "$f"` | `buy rope`, `Rope locker key` | 0 |
| P2 a dot is a dot | `grep -iF -- 3.50 "$f"` | `cost is 3.50` | 0 |
| P3 pattern text | `grep -iF -- '.*' "$f"` | Nothing | 1 |
| P4 leading dash | `grep -iF -- -v "$f"` | `use -v flag` | 0 |
| P5 missing file | `grep -iF -- rope "$f.none"` | `grep: …: No such file or directory` on standard error | 2 |
| P6 empty word | `grep -iF -- '' "$f" \| wc -l` | `6`, every line | 0 |
| P7 newline in the word | `grep -iF -- $'ann\nkey' "$f"` | `call Ann`, `Rope locker key` | 0 |
| P8 under `set -e` | `bash -c 'set -euo pipefail; case x in x) grep -iF -- zzz "$1" ;; esac; echo not-reached' _ "$f"` | Nothing | 1 |
| P9 `É` in a UTF-8 locale | `LC_ALL=en_US.UTF-8 grep -iF -- émile` on `Émile called` | `Émile called` | 0 |
| P10 `É` in the C locale | `LC_ALL=C grep -iF -- émile` on the same line | Nothing | 1 |
| P11 invalid byte, no `-a` | `grep -iF -- rope` on `caf\xe9 rope` and `plain rope` | `plain rope`, then `grep: …: binary file matches` | 0 |
| P12 invalid byte, `-a` | `grep -aiF -- rope` on the same file | Both lines | 0 |

Only GNU grep was probed. It is the `grep` on this machine.

## When it goes wrong

Three of the probes show `grep` alone doing the wrong thing, and the design guards each one.

- P5: a missing notes file makes `grep` print an error and exit 2. Search checks for the file before it calls
  `grep`, prints nothing as `list` does for a missing file (`bin/notes:6`), and exits 1.
- P6: an empty word matches every note. Search treats an empty word as a missing word.
- P7: `grep -F` reads a newline in the word as "either of these words". A note is one line, so a word with a
  newline can't be in one. Search exits 1 before it calls `grep`.

P11 shows a quieter failure: one invalid byte in the notes file makes `grep` drop that note and print a warning.
`-a` prevents it (P12).

P8 shows that `bin/notes` runs under `set -euo pipefail` and that a `grep` status of 1 ends the script with
status 1 and prints nothing more. That is the exit the brief asks for, so no handling is needed around it.

P9 and P10 show that case folding for letters outside ASCII depends on the locale. The design accepts that and
the tests use ASCII words only.

A notes file that exists but can't be read is outside the goal. `grep` prints its own error and exits 2, the
same number as a usage error, and standard error tells the two apart. No test covers it.

The limits are the exit codes above (0, 1, 2) and the task's time clause (82 minutes). Search sets no limit on
the size of the notes file or the length of a note.

Every test that runs `add`, `list`, or `search` sets `NOTES_FILE` to a path from `mktemp`. A test without it
would use `~/.notes`, which is your real notes file.

## Assumptions

The spec has one task, so no assumption carries across tasks. The task rests on two, both checked today:
`grep` is GNU grep 3.12 with the behaviour probed above, and `bash scripts/gate.sh` runs in Claude Code (it ran
in this session, with the output shown at the top).

## Files

The task changes `bin/notes` and `tests/run.sh`, as the brief says. The list comes from these searches over the
tracked files (`git grep -n -e <text>`), run at `18fc5cb`.

| Search | Hits | Each hit |
| --- | --- | --- |
| `usage` | 5 | `bin/notes:7` changes: the usage line. `tests/run.sh:12`, `:13` stay: `test_usage` checks only the first word, and still passes. `tests/run.sh:18` changes: the run list. `brief.md:9` dismissed: the brief. |
| `notes list` | 4 | `bin/notes:7` changes, as above. `README.md:4` dismissed, see below. `tests/run.sh:7`, `:10` stay: existing tests. |
| `notes add` | 4 | `bin/notes:7` changes, as above. `README.md:3` dismissed, see below. `tests/run.sh:7`, `:16` stay: existing tests. |
| `search` | 3 | `brief.md:1`, `:7`, `:12` dismissed: the brief. Nothing in the code uses the name yet. |
| `export` | 3 | `tests/run.sh:15`, `:16` stay word for word. `tests/run.sh:18` changes: the name leaves the run list. |
| `test_` | 6 | `tests/run.sh:2` stays, and is why goal item 7 counts functions: the comment says the runner runs every `test_*` function, but line 18 is a hand-kept list. `:6`, `:9`, `:12`, `:15` stay. `:18` changes. |
| `NOTES_FILE` | 5 | `bin/notes:3` stays. `README.md:3` dismissed. `tests/run.sh:7`, `:10`, `:16` stay. |

`README.md` describes `add` and `list` and will not describe `search`. The brief fixed the files at two, so the
README stays as it is and the gap goes in the pull request under `## For Geoff`. `scripts/gate.sh` has no hit
and doesn't change.

## Commands and the denials log

`.workstation/denials.log` holds three refusals, all inside the last 30 days (since 2026-10-23).

| Refused | Why | What the task does |
| --- | --- | --- |
| `git push --force origin main` (2026-11-03) | Force push to the default branch | Pushes only the branch it created, with no force flag. A rejected push gets no force. |
| `rm -rf ~/.notes.bak` (2026-11-09) | Recursive delete outside the working folder | Runs no recursive delete. A test may remove its own `mktemp` file with `rm -f`, as `tests/run.sh:10` does today inside the gate, which ran here without a refusal. |
| WebFetch `https://example.invalid/notes` (2026-11-17) | Unknown host | Fetches nothing. The `grep` facts it needs are quoted above. |

The task's other commands are `bash scripts/gate.sh` and `bin/notes` with `NOTES_FILE` set, both run in this
session, and the `git` and `gh` steps that `building-from-specs` owns under "A session at work" and "The pull
request". None matches a refusal.

One refusal happened while this spec was written and is not in the log: a single long command that copied the
repo to a scratch folder and built a throwaway `search` there. I dropped it. So no goal check has run against
a build of search. The probes show the mechanism for each one.

## Before launch

`building-from-specs`, "Launching a task", owns the launch command and its checks. These are the facts for this
task, with what could be tested today.

- The spec is not on the remote. `git status --short spec.md` prints `?? spec.md`, because this session was
  told to commit nothing. The task's worktree starts from the remote's default branch, so after approval the
  session you are talking to commits `spec.md` to `main` and pushes it before it launches.
- `claude-worktree-busy` and the count of working sessions were not checked. `command -v claude-worktree-busy`
  prints nothing in this session. The launching session runs both.
- The task needs no secret.
- The task needs no CI. `.workstation/remote.txt` gives the repo as public with default branch `main` and says
  it runs no CI on pull requests.
- The run is planned at 41 minutes and may reach 82, so the launching session arms the guards in
  `~/.claude/docs/unattended-work-guards.md`.

## The task: notes-search

The task session runs on Opus at high effort. It waits for no other task, and with one task there is no merge
order to give. The launch condition names `spec.md` and the task `notes-search`, lists the eight done items
below word for word, and ends `or stop after 82 minutes`.

It changes `bin/notes` and `tests/run.sh`. One reviewer reads the branch: `standards:diff-reviewer`, on Opus at
high. The work touches no sign-in or data path and renders no UI, so no second reviewer reads it.

### Minutes

`task-report --since 2026-11-01` (`.workstation/task-report.txt`) gives three past tasks in this repo.

| Pull request | Title | Planned | Measured | Fix rounds |
| --- | --- | --- | --- | --- |
| 12 | Add notes list | 30 | 34 | 0 |
| 15 | Add the usage test | 15 | 12 | 0 |
| 18 | Let notes add read stdin | 30 | 41 | 1 |

The two like tasks are 12 and 18: by their titles each added or changed a command, each was planned at 30,
and both ran over. The report gives titles and minutes only. This task is planned at 41 minutes, the slower of the two, because it also changes the usage line and the
run list. It drives no CI, timer, or idle limit, so nothing is added for waits. The time clause is 82 minutes.

### Done items

Each check runs from the repo's root. Items 1 to 4 use the setup below. The setup and an item's commands run
in one shell command, because each Bash call in Claude Code starts a new shell and a search without `NOTES_FILE`
reads the real `~/.notes`.

```bash
export NOTES_FILE=$(mktemp)
bin/notes add "buy rope"
bin/notes add "call Ann"
bin/notes add "Rope locker key"
bin/notes add "cost is 3.50"
bin/notes add "cost is 3x50"
bin/notes add "use -v flag"
```

Every `bin/notes` and gate check below ran twice today on `main` at `18fc5cb`, and the two runs matched byte
for byte. The `grep` checks on `tests/run.sh` and the `git` check ran once. Each `bin/notes search …` command printed `usage: notes add <text> | notes list` on standard error and exited 2,
because `search` falls to the unknown-command arm at `bin/notes:7`. That is the reason the task fixes. Where
today's result differs from that, the item says so.

**1. `bin/notes search <word>` prints every note that contains the word, oldest first, and exits 0, and the
match ignores case.**

```bash
bin/notes search rope; echo "exit=$?"
bin/notes search ROPE; echo "exit=$?"
bin/notes search locker key; echo "exit=$?"
```

The first two each print `buy rope`, `Rope locker key`, `exit=0`. The third prints `Rope locker key`, `exit=0`.

**2. The word is plain text: no character in it acts as a pattern or an option.**

```bash
bin/notes search 3.50; echo "exit=$?"
bin/notes search '.*'; echo "exit=$?"
bin/notes search -v; echo "exit=$?"
bin/notes search $'ann\nkey'; echo "exit=$?"
```

In order: `cost is 3.50` and `exit=0`; nothing and `exit=1`; `use -v flag` and `exit=0`; nothing and `exit=1`.

**3. A search that matches nothing prints nothing and exits 1, and so does a search when the notes file doesn't
exist.**

```bash
bin/notes search zebra; echo "exit=$?"
NOTES_FILE="$NOTES_FILE.none" bin/notes search rope; echo "exit=$?"
```

Each prints `exit=1` and nothing else, on either stream.

**4. `bin/notes search` with no word exits 2 and prints
`usage: notes add <text> | notes list | notes search <word>` on standard error, and an unknown command prints
the same line.**

```bash
bin/notes search; echo "exit=$?"
bin/notes search ""; echo "exit=$?"
bin/notes bogus; echo "exit=$?"
```

Each prints that line on standard error, nothing on standard output, and `exit=2`. Today the exit is already 2
and the check fails on the line's text, which doesn't name `search`.

**5. `tests/run.sh` has at least one passing `test_search_` test for each of items 1 to 4.**

```bash
bash scripts/gate.sh | grep -c '^ok   test_search_'
```

It prints 4 or more. Today it prints `0`. The reviewer reads that the tests assert the commands and outputs
given under items 1 to 4, and that each sets `NOTES_FILE` to a `mktemp` path.

**6. `test_export_csv` is unchanged and out of the run: the gate prints
`skip test_export_csv (notes export is not built)` in its place.**

```bash
grep -c '^test_export_csv() {' tests/run.sh
grep -c 'bin/notes export' tests/run.sh
bash scripts/gate.sh | grep -cxF 'skip test_export_csv (notes export is not built)'
```

Each prints `1`. Today they print `1`, `1`, `0`. The reviewer reads the branch's diff of `tests/run.sh` and
confirms that lines 15 to 17 are untouched.

**7. `bash scripts/gate.sh`, run on the branch's last commit, exits 0 with no `FAIL` line, and every `test_`
function in `tests/run.sh` shows in its output as `ok` or `skip`.**

```bash
bash scripts/gate.sh; echo "exit=$?"
bash scripts/gate.sh | grep -c -E '^(ok  |skip) test_'
grep -c -E '^test_[a-z0-9_]+\(\) \{' tests/run.sh
```

The gate prints `exit=0` and the two counts are equal. Today the gate prints `FAIL test_export_csv` and
`exit=1`, and the counts are `3` and `4`. This item fails today because the export test is in the run, which
item 6 fixes. Item 5 is the one that fails for the missing search tests.

**8. The branch changes `bin/notes` and `tests/run.sh` and no other file.**

```bash
git diff --name-only origin/main...HEAD
```

It prints `bin/notes` and `tests/run.sh`. This checkout has never fetched, so it has no `origin/main` ref and
the command fails here with "unknown revision". It ran today as `git diff --name-only main...HEAD` and printed
nothing, since the branch is `main`. The task's worktree starts from the remote's default branch and has the
ref.

### What goes in the pull request

`building-from-specs`, "The pull request", owns the body. Under `## For Geoff` this task lists two things this
spec found and did not do: no `notes export` command exists and its test is skipped, and `README.md` doesn't
name `search`. Anything else the session finds beyond the goal goes in the same section, with its file and
line. The session starts no backlog file.

The pull request body follows `~/.claude/docs/voice/written-for-people.md`, as that section says. Commit
messages are in the imperative mood and follow `~/.claude/docs/voice/commit-and-pr.md`.

## Backlog sweep

The repo has no backlog. `git ls-files | grep -i -E 'backlog|todo|status|docs/'` prints nothing, so the scoped
sweep of `standards:backlog-sweep` has no item to read and returns no verdict. A full sweep is not due, since
there are no open items. Approving this spec approves no backlog edit.

## Calls Claude made

Only the first changes what the brief approved. Calls 3 and 12 are product calls you may want the other way.
Each can be changed by a sentence at approval.

1. The task skips `test_export_csv` in the open. Passed over: deleting the test, building export, and leaving
   the gate red. Reversing it is a two-line edit in `tests/run.sh`.
2. "Contains" means anywhere in the note, never whole words only. The brief says "contains the word" and "plain
   text".
3. Words after `search` are joined by single spaces, following `add` (`bin/notes:5`). Passed over: a usage
   error for more than one word. Reversing it would break `search locker key` for anyone who had started to
   type it.
4. An empty word counts as a missing word and gets the usage line, because P6 shows it would match every note.
5. A missing notes file counts as no match: search prints nothing, as `list` does, and exits 1. `list` exits 0
   there, and search doesn't follow it in that, because the brief gives 1 for no match.
6. A word with a newline in it matches nothing and exits 1, because P7 shows `grep` would read it as two words.
7. Search passes `-a` to `grep`, because P11 shows one invalid byte would hide a note.
8. Case folding outside ASCII follows the locale. No test covers it.
9. An unreadable notes file is outside the goal. `grep`'s error and status 2 pass through.
10. The usage line's text is `usage: notes add <text> | notes list | notes search <word>`.
11. "Prints nothing" on no match means nothing on standard error either.
12. `README.md` doesn't change, because the brief names two files. The gap is listed for you in the pull
    request.
13. The task starts no backlog. `standards:log-issue` would add `BACKLOG.md` and `.claude/project-tracking.json`
    to a repo that has neither, and that is yours to start.
14. Output is each matching note exactly as stored, with no line number and no colour.
15. New tests are named `test_search_…`, so one `grep` counts them.
16. The plan is 41 minutes, the task session runs on Opus at high, and `standards:diff-reviewer` is the one
    reviewer.
17. `~/.claude/docs/voice/written-for-people.md` could not be read from this session (two refusals). This spec
    follows the standards that `writing-voice` names for it: the Federal Plain Language Guidelines, Nielsen
    Norman Group on web writing, and Google's rules for headings.
18. After approval, `spec.md` goes to `main` as a direct commit, although `README.md:7-8` says work reaches
    `main` through a pull request. `building-from-specs`, "Records", lets a hand-over commit directly, and I
    read the approved spec as a hand-over. Passed over: a pull request for the spec alone.

## The fresh read

One fresh reader on Fable at high read this spec with the brief, the code, and the guide, and nothing else. It
raised 13 points, sorted here into the guide's three piles.

Answered already, two points. The launch checks that need `claude-worktree-busy` and the session count are
stated as not run under "Before launch". The `origin/main` command is stated as run with `main` in place.

Minor calls I made and marked, eleven points. The setup and an item's commands share one shell. Item 6 no
longer asks for a commit of its own, because the skip and the search tests both edit the run list on line 18,
so a revert would conflict; reversing is now a two-line edit. Item 7's count accepts a digit in a test name.
The word is checked before the file. Item 7 fails today for one reason and says so. Call 5 no longer says `list`
exits 1. The minutes rest on titles and say so. The pull request and commits name their voice standards. Call 18
marks the direct commit of the spec. One point was about the missing `origin/main` ref, now explained under
item 8.

Questions only you can answer: none new. The one that was yours before the read is the first call, the skipped
test.

The reader could not open the `building-from-specs` skill file, so it did not check this spec's pointers to
"Launching a task", "A session at work", "The pull request", and "Records". I read those sections when I wrote
the pointers.
