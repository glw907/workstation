# Spec: notes search

Written 2026-11-22 from `brief.md`, against `main` at `e3473df`.

This spec adds `bin/notes search <word>` in one task of 40 minutes that ends in one pull request. The design in
the brief is settled and this spec keeps all of it. One thing in it can't be built today: search must print in
the format `notes export` uses, and this checkout has no `export` command. The task therefore waits until
`export` is on `origin/main`, and the spec defines the format by comparing against `export` itself, so nothing
here guesses what that format is. Three things wait for Geoff: that wait, the eight calls listed at the end, and
the note about the README.

## Intent

Geoff's words: "I want to find a note without scrolling through the whole list."

The goals are the brief's settled points.

- `bin/notes search <word>` prints every note that contains the word, oldest first.
- The match ignores case. The word is plain text, never a pattern.
- Each match prints in the format `notes export` uses, so scripts can read both the same way.
- No match prints nothing and exits 1. A missing word exits 2 with the usage line, which names the new command.
- The work changes `bin/notes` and `tests/run.sh`, is one task, and ends in one pull request.

The work does not build or change `export`, add flags or patterns to search, search for several words at once,
or edit the README.

The work has failed if a script that reads `export` output can't read `search` output the same way, if a word
such as `a.c` or `.*` is ever treated as a pattern, if a search test exists that the gate never runs, or if a
test reads or writes the real `~/.notes`.

## `notes export` is not on this checkout

The brief names `notes export` as the format to match. Nothing I could read says what that format is.

| Probe, run 2026-11-22 | Output |
| --- | --- |
| `git grep -n export` | 1 hit, `brief.md:9`, the line quoted above |
| `git show main:bin/notes \| grep -c 'export)'` | `0` |
| `bin/notes export; echo "exit $?"` | `usage: notes add <text> \| notes list`, then `exit 2` |
| `git for-each-ref` | one ref, `refs/heads/main`; no branch, stash, or remote-tracking ref holds other work |
| `git fetch origin` | `fatal: unable to access 'https://github.com/example/notes.git/': CONNECT tunnel failed, response 403` |

The fetch was refused by this session's network sandbox, so the remote itself went unread. `export` may be on
`origin/main` ahead of this checkout, on an unmerged branch, or not started. The task report since 2026-11-01
lists pull requests 12, 15, and 18, and none of them is `export`. This checkout is also not the whole picture in
another way: pull request 18 is "Let notes add read stdin", and `add` at `bin/notes:5` reads no stdin.

I considered four ways to handle this.

| Approach | Trade-off |
| --- | --- |
| Wait for `export` to reach `origin/main`, then build search against it | Search ships later. Nothing is guessed, and the tests compare against the real command. |
| Build `export` inside this task | The brief settles no format for `export`, so the task would invent a public format. It also changes the scope Geoff approved. |
| Build search now, printing raw lines as `list` does, and align it later | Scripts would come to read a format that may not be `export`'s. That breaks a settled point on the day it ships. |
| Start the task from the `export` branch | `building-from-specs` "Launching a task" forbids it: a task starts from the default branch. |

The pick is the first. It follows the same section's rule that a task needing another task's work waits until
that work has merged.

Because the format is unread, this spec states it as a comparison and never as text. `search <word>` prints
exactly what `export` prints for a notes file that holds only the matching notes, in their original order. A
script that reads one reads the other, whatever the format turns out to be, and a later change to `export`
fails the search tests until search follows it. Two consequences follow. If `export` numbers its notes, the
numbers in search output count the matches. If `export` prints anything for an empty file, the brief still wins
for no match: search prints nothing.

That comparison rests on one assumption, which is the least proven thing in this spec: `bin/notes export` takes
no argument, reads `$NOTES_FILE`, writes to stdout, and prints the same output for the same notes whichever
file holds them. It also needs `add <text>` on `origin/main` to still append one line, since pull request 18
changed `add`. No source states either. The first start condition below is the probe for both.

## What search does

A note is one line of the notes file, since `add` appends one line (`bin/notes:5`). Search reads the file that
`$NOTES_FILE` names, with the default the other commands use (`bin/notes:3`). It tests the word against the
note's stored text, not against the text `export` prints for it.

| Call | Stdout | Stderr | Exit |
| --- | --- | --- | --- |
| `search rope`, some notes contain "rope" in any case | Those notes, oldest first, as `export` prints them | Nothing | 0 |
| `search rope`, no note contains it | Nothing | Nothing | 1 |
| `search rope`, the notes file doesn't exist | Nothing | Nothing | 1 |
| `search` | Nothing | The usage line | 2 |
| `search ""` | Nothing | The usage line | 2 |
| `search buy rope` (two arguments) | Nothing | The usage line | 2 |

The word matches anywhere in a note, so `search rope` finds "new ropes". A quoted word may hold spaces, so
`search "buy rope"` looks for that text. Every character in the word is literal, including `.`, `*`, `[`, a
backslash, and a leading dash.

There is one usage line, printed for a missing word and for an unknown command alike. It is the usage line as it
stands on `origin/main` with ` | notes search <word>` added at the end. On today's checkout that gives
`usage: notes add <text> | notes list | notes search <word>`.

## How it matches

| Approach | Label | Trade-off |
| --- | --- | --- |
| `grep -iF -e "$word"` picks the lines | Documented | One call. The options do what the brief asks, and the probes below show it. grep's exit 2 needs care. |
| A bash loop with `${line,,}` and a quoted `[[ ... == *"$word"* ]]` | Documented, not probed | No outside command, but more lines, and a missed quote turns the word into a glob. |

The pick is grep. GNU grep 3.12 `--help` on this machine says: `-F, --fixed-strings  PATTERNS are strings`,
`-i, --ignore-case  ignore case distinctions in patterns and data`, and `-e, --regexp=PATTERNS  use PATTERNS for
matching`. The probes ran over a six-line file holding `buy rope`, `call Sam`, `Rope ladder`, `a.c`, `abc`, and
`use -v flag`.

| Probe | Output |
| --- | --- |
| `grep -iF -e 'ROPE' p` | `buy rope`, `Rope ladder`, exit 0 |
| `grep -iF -e 'a.c' p` | `a.c` only, exit 0 |
| `grep -iF -e '.*' p` | nothing, exit 1 |
| `grep -iF -e '-v' p` | `use -v flag`, exit 0 |
| `grep -iF -e rope nope` (no such file) | `grep: ...: No such file or directory`, exit 2 |
| `grep -ciF -e '' p` | `6`, exit 0 |

The last two rows are the traps. grep exits 2 for a missing file, which is the usage exit, so search checks for
the file before grep runs. An empty word matches every note, so search refuses it before grep runs. How the
selected notes reach `export`'s printing code is the builder's call once that code can be read.

This spec proposes no new Claude Code mechanism. The launch, the goal, the review, and the pull request are the
ones `building-from-specs` already holds.

## When it goes wrong

Search has three exits: 0 for a match, 1 for none, 2 for a call it can't read. It sets no limit on the size of
the notes file or the length of a note. A notes file that exists but can't be read is outside this work:
whatever grep reports stands, and no test covers it. Case folding for letters outside ASCII follows the locale
grep runs in, and the tests use ASCII.

The repo runs no CI on pull requests (`.workstation/remote.txt`), so the gate on the branch's last commit is its
only full run. A red gate there has nothing behind it to catch it. The task stops at 80 minutes.

## Files

Each search ran over tracked files with `git grep -n` at `e3473df`. Line numbers are for that commit, and the
builder reads the files again in its worktree, where `export` has changed them.

| Search | Hits | Each hit |
| --- | --- | --- |
| `usage` | 5 | `bin/notes:7` changes: the usage line. `tests/run.sh:12`, `:13` stay: `test_usage` reads only the first word. `tests/run.sh:15` changes: the loop. `brief.md:10` dismissed: the brief. |
| `notes add`, `notes list`, `notes search` | 7 | `bin/notes:7`, as above. `tests/run.sh:7`, `:10` stay: tests of `add` and `list`. `README.md:3`, `:4` dismissed: the brief limits the work to two files, see "For Geoff". `brief.md:1`, `:7` dismissed. |
| `test_` | 5 | `tests/run.sh:15` changes: the loop names each test it runs. `tests/run.sh:2`, `:6`, `:9`, `:12` stay. |
| `export` | 1 | `brief.md:9` dismissed. |

The task changes `bin/notes` and `tests/run.sh` and no other file.

The loop at `tests/run.sh:15` is a trap. The comment at line 2 says the script runs every `test_*` function, but
the loop runs only the three it names. A new test that isn't added to the loop never runs, and the gate stays
green.

## Commands and the denials log

The task runs `bin/notes` with `NOTES_FILE` set to a `mktemp` path, `bash scripts/gate.sh`, `git` to stage named
files, commit, and push the branch it created, `gh` for its draft pull request, and one dispatch of the reviewer. The
git and gh steps are the ones `building-from-specs` "A session at work" and "The pull request" own.

`.workstation/denials.log` holds three refusals in the 30 days to 2026-11-22. None is a command this task runs.

| Refused | What it means here |
| --- | --- |
| `git push --force origin main` (2026-11-03) | The task pushes only the branch it created and never with force. |
| `rm -rf ~/.notes.bak` (2026-11-09) | No test deletes recursively or names a path under `~`. The existing `rm -f` on a `mktemp` path at `tests/run.sh:10` ran inside the gate today, exit 0. |
| WebFetch of `https://example.invalid/notes` (2026-11-17) | The task fetches nothing. grep's behavior is sourced from the local `--help` and the probes above. |

## Start conditions

The session Geoff is talking to checks these before launch, with the four checks in `building-from-specs`
"Launching a task". The task needs no secret and no CI.

1. `export` is on `origin/main` and behaves as the comparison assumes. In a checkout of `origin/main`, the
   block below prints `2`, `export exit 0`, a line count above 0, and `stable`. Today on `e3473df` it prints
   `2`, the usage line, `export exit 2`, `0`, and `not stable`.

   ```bash
   f=$(mktemp); g=$(mktemp)
   for n in "buy rope" "call Sam"; do NOTES_FILE=$f bin/notes add "$n"; NOTES_FILE=$g bin/notes add "$n"; done
   wc -l < "$f"
   a=$(NOTES_FILE=$f bin/notes export); echo "export exit $?"; printf '%s' "$a" | grep -c ''
   [ -n "$a" ] && [ "$a" = "$(NOTES_FILE=$g bin/notes export)" ] && echo stable || echo "not stable"
   ```

2. The goal names this spec by absolute path in the main checkout. `spec.md` is uncommitted, and a worktree
   made fresh from `origin/main` doesn't hold an uncommitted file.

If the first condition fails because `add` no longer appends one line, or `export` takes an argument, writes
somewhere else, or prints something that changes between files, this spec's checks are wrong for the code. That is a finding that changes what Geoff
approved, and it goes to him before any launch.

I couldn't test the start conditions against today's live sessions. `claude-worktree-busy` is not on this
session's path (`command not found`, exit 127), and the remote was out of reach.

## Task: notes-search

The task waits for the work that adds `notes export`, which has no pull request number I could read. It is the
only task, so it is also the first, and it rests on the assumption named above.

Its files are `bin/notes` and `tests/run.sh`. Its reviewer is `standards:diff-reviewer`, on Opus at high. It
touches no sign-in or data path and renders no UI, so no other reviewer reads it. The build session runs on Opus
at medium.

### Minutes

The task is planned at 40 minutes, and the goal ends with `or stop after 80 minutes`.

`.workstation/task-report.txt` measures three tasks in this repo since 2026-11-01. Two are like this one, a
command in `bin/notes` with its tests: "Add notes list" took 34 minutes against 30 planned with no fix round,
and "Let notes add read stdin" took 41 against 30 with one. "Add the usage test" took 12 and changed only a
test, so it is no guide. The two like tasks average 37.5 and both ran over their plan. Search has more cases
than either, so the plan is 40. The task drives no CI, timer, or idle limit, so no wait is added.

### Goal

Items 1 to 5 share this setup, run from the root of the task's worktree. `only` prints what `export` prints for
a file holding just the notes it is given. `same` prints `same` only when search printed something and it equals
that.

```bash
f=$(mktemp); h=$(mktemp); m=$(mktemp); rm -f "$m"
for n in "buy rope" "call Sam" "Rope ladder" "new ropes"; do NOTES_FILE=$f bin/notes add "$n"; done
for n in "a.c" "abc" "use -v flag"; do NOTES_FILE=$h bin/notes add "$n"; done
only() { local t n; t=$(mktemp); for n in "$@"; do NOTES_FILE=$t bin/notes add "$n"; done; NOTES_FILE=$t bin/notes export; }
same() { [ -n "$1" ] && [ "$1" = "$2" ] && echo same || echo differ; }
```

I ran every check on `e3473df` on 2026-11-22, twice, and the two runs printed the same bytes. Each row gives
what the check prints when the item is met and what it printed today. Today's failures have two causes. Search
doesn't exist, which the task fixes. `export` doesn't exist, which the task doesn't fix and the first start
condition covers.

1. Search prints every note that contains the word, oldest first, in `export`'s format.

   `same "$(NOTES_FILE=$f bin/notes search rope)" "$(only "buy rope" "Rope ladder" "new ropes")"`

   Met: `same`. Today: the usage line twice on stderr, then `differ`.

2. The match ignores the case of the word and of the note.

   `same "$(NOTES_FILE=$f bin/notes search ROPE)" "$(only "buy rope" "Rope ladder" "new ropes")"`

   Met: `same`. Today: the usage line twice, then `differ`.

3. The word is plain text, never a pattern.

   ```bash
   same "$(NOTES_FILE=$h bin/notes search a.c)" "$(only "a.c")"
   same "$(NOTES_FILE=$h bin/notes search -v)" "$(only "use -v flag")"
   same "$(NOTES_FILE=$f bin/notes search "buy rope")" "$(only "buy rope")"
   out=$(NOTES_FILE=$h bin/notes search '.*' 2>&1); echo "[$out] exit $?"
   ```

   Met: `same`, `same`, `same`, `[] exit 1`. Today: usage lines on stderr, `differ` three times, then
   `[usage: notes add <text> | notes list] exit 2`.

4. No match prints nothing and exits 1, and so does a notes file that doesn't exist.

   ```bash
   out=$(NOTES_FILE=$f bin/notes search zebra 2>&1); echo "[$out] exit $?"
   out=$(NOTES_FILE=$m bin/notes search rope 2>&1); echo "[$out] exit $?"
   ```

   Met: `[] exit 1` twice. Today: `[usage: notes add <text> | notes list] exit 2` twice.

5. A missing word exits 2 with the usage line, which names the new command. An empty word and a second argument
   do the same.

   ```bash
   out=$(NOTES_FILE=$f bin/notes search 2>/dev/null); echo "[$out] exit $?"
   NOTES_FILE=$f bin/notes search 2>&1 >/dev/null | grep -c 'notes search <word>'
   [ "$(NOTES_FILE=$f bin/notes search 2>&1)" = "$(NOTES_FILE=$f bin/notes bogus 2>&1)" ] && echo "one usage line"
   out=$(NOTES_FILE=$f bin/notes search "" 2>/dev/null); echo "[$out] exit $?"
   out=$(NOTES_FILE=$f bin/notes search buy rope 2>/dev/null); echo "[$out] exit $?"
   ```

   Met: `[] exit 2`, `1`, `one usage line`, `[] exit 2`, `[] exit 2`. Today: `[] exit 2`, `0`, `one usage line`,
   `[] exit 2`, `[] exit 2`. Only the count fails today. The other four lines already hold, because today's code
   treats `search` as an unknown command, so they guard against a regression and prove nothing new.

6. The gate passes on the branch's last commit and runs a test for each of items 1 to 5.

   `bash scripts/gate.sh; echo "exit $?"`

   Met: an `ok` line for `test_add_then_list`, `test_list_empty`, `test_usage`, and every `test_search_*` test,
   no `FAIL` line, and `exit 0`. Today: the three existing `ok` lines and `exit 0`, with no search test.

   `grep -c '^test_search_' tests/run.sh; bash scripts/gate.sh | grep -c '^ok   test_search_'`

   Met: the same number twice, 5 or more, which shows every search test defined is in the loop. Today: `0`, `0`.

   `d=$(mktemp -d); HOME=$d bash scripts/gate.sh; echo "exit $?"; ls -A "$d" | wc -l`

   Met: the same `ok` lines, `exit 0`, and `0`, which shows no test depends on or writes a notes file under the
   home folder. Today: the three `ok` lines, `exit 0`, `0`. This one is a guard and passes today.

   The reviewer reads the search tests against items 1 to 5 and confirms that each item has one and that the
   test for item 1 compares against `export` as the check above does. The pull request quotes the gate's output
   with the hash of the commit it ran on.

7. The branch changes `bin/notes` and `tests/run.sh` and nothing else.

   `git diff --name-only origin/main...HEAD`

   Met: those two paths. I ran it today as `git diff --name-only main...HEAD`, since this checkout has no
   `origin/main`; it printed nothing.

8. The pull request is ready, written by `building-from-specs` "The pull request", with an accept verdict from
   the review in "Gates and review" on the branch's last commit.

The session runs the first start condition's block in its worktree before it writes anything. If the block
prints anything other than what that condition says, the condition has failed. The session then builds no search
in a format it chose, and ends by the row "a rule's condition fails" in `building-from-specs` "In place of a
question".

### Merge order

There is one pull request. It merges after the `export` work has merged, which the first start condition already
forces, and by `building-from-specs` "Merging".

## Backlog sweep

The scoped sweep reads backlog items that name a file the task changes. The repo has no backlog:
`git ls-files | grep -ci -e backlog -e todo -e status` printed `0`, and there is no `docs` folder. The sweep has
nothing to read, returns no verdict, and lands no edit. A full sweep is not due with no open items.

## Fresh reader

One fresh reader on Fable at high read this spec with no context and re-ran the searches, the probes, the start
block, and goal checks 1 to 7. It found no claim the repo contradicts. Its questions fell into three piles.

Answered already: the task is blocked on work nobody has located (call 1), checks 1 to 4 fail today for two
causes, and four lines of check 5 pass today.

Minor calls, made and marked in the text: no match prints nothing even if `export` prints a wrapper for an empty
file; numbering, if `export` has any, counts the matches; the start block now also probes that `add` appends
one line and that `export` doesn't depend on which file it reads; check 3 gained the quoted word with a space;
item 6 gained the empty-home run and says what the reviewer reads.

Only Geoff can answer: where the `export` work is, and whether search should wait for it.

## Calls Claude made

Nobody could answer a question while this spec was written. Each call below is mine, and Geoff can overturn any
of them before approval.

1. The task waits for `export` to merge. The alternatives are in the table near the top.
2. The format is defined by comparison with `export`, and the spec never states it as text.
3. The word matches anywhere in a note, so `rope` finds "ropes". The brief says "contains". Matching whole words
   only would be one grep option later.
4. Exactly one argument is a word. A second argument exits 2. The option passed over joins the arguments with
   spaces, as `add` does at `bin/notes:5`. I took the strict one because loosening it later breaks no script,
   and tightening the other would.
5. An empty word counts as a missing word and exits 2. grep would otherwise match every note.
6. A notes file that doesn't exist counts as no match: nothing printed, exit 1. `list` already prints nothing
   for it, and grep's own exit 2 would read as a usage error.
7. No match prints nothing on stderr as well as stdout.
8. The build session runs on Opus at medium, and the plan is 40 minutes.

## For Geoff

The README describes `add` and `list` and will not mention `search`, because the brief limits the work to two
files. The task's pull request names that gap. Adding the line is a direct change by `building-from-specs`
"Direct changes" if you want it.

`~/.claude/docs/voice/written-for-people.md` was refused to this session, so this spec follows the shape rules in
the `writing-voice` skill and has not been read against that guide.
