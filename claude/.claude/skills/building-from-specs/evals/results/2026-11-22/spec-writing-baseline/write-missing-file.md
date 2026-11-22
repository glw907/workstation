# Spec: notes search

Written 2026-11-22 from `brief.md`, against `main` at `d39b696`. This spec adds one command,
`bin/notes search <word>`, as one task that ends in one pull request, planned at 40 minutes.

It departs from the brief in one place. The brief says the work changes `bin/notes` and
`tests/run.sh`. The gate can't pass with only those two files, so the task changes four. "Where
this spec differs from the brief" has the evidence, and "Calls Claude made" lists every other
decision this spec took without you.

## Intent

Geoff said: "I want to find a note without scrolling through the whole list."

The goal is one command that prints the notes containing a word and nothing else, so the answer
fits on a screen however long the notes file is.

These are not goals: patterns or wildcards, whole-word matching, searching for several words at
once, highlighting or line numbers, a change to how `add` or `list` behave, and a repair of
`test_completions_match` (see "A trap in the existing test").

The work has failed if any of these is true after the merge:

- `search` treats the word as a pattern, so `a.c` finds `abc` or a word that starts with `-` is read
  as an option.
- `search` exits 0 when nothing matched, so a script can't tell a hit from a miss.
- `main` has a red gate.
- `add` or `list` behaves differently than it does today.

## What search does

The first five rows come from the brief and are settled. The rest are readings the brief leaves
open, decided here and listed again under "Calls Claude made".

| Case | Result | Source |
| --- | --- | --- |
| A word that one or more notes contain | Prints each matching note as stored, one per line, oldest first, on stdout. Exits 0. | Brief |
| Letter case | Ignored. `rope` and `ROPE` both find `Rope for the boat`. | Brief |
| Characters that mean something to a pattern or to a command | Plain text. `a.c` finds only `a.c`, `.*` finds only a note with those two characters, and `-n` finds `use the -n flag`. | Brief |
| No note contains the word | Prints nothing on stdout or stderr. Exits 1. | Brief |
| No word, as in `notes search` | Prints the usage line on stderr and nothing on stdout. Exits 2. | Brief |
| An empty word, as in `notes search ''` | The same as no word. An empty text is contained in every note, so it can't mean a search. | Decided here |
| "Contains" | The word may be part of a longer word. `rop` finds `buy rope`. | Decided here |
| A word that is only spaces, as in `notes search ' '` | Searched as given. A space is plain text, so it finds every note that has a space. Only the empty text is refused. | Decided here |
| More than one argument, as in `notes search the boat` | The arguments are joined with single spaces and searched as one text, the way `add` joins its arguments (`bin/notes:5`). `the boat` finds `Rope for the boat`, and `boat the` finds nothing. | Decided here |
| The notes file doesn't exist, or the path is not a regular file | The same as no match: prints nothing, exits 1. `list` already prints nothing for a missing file (`bin/notes:6`). | Decided here |

The usage line becomes exactly this, for every path that prints it:

```text
usage: notes add <text> | notes list | notes search <word>
```

A note is one line of the notes file. "Oldest first" is file order, because `add` only appends
(`bin/notes:5`, `>>`).

## Where this spec differs from the brief

The brief names two files. The file search below found two more that name the tool's commands.

`completions/notes.bash` has to change, or the gate fails. `test_completions_match`
(`tests/run.sh:15-20`) reads every `notes <word>` in `bin/notes` and compares the list with the
words the completion file offers. The brief requires the usage line to name `notes search`, so the
test then reads `add list search` from `bin/notes` and `add list` from the completion file. I
checked this on a throwaway copy of the repo in `$TMPDIR`, with a working `search` in `bin/notes`
and the completion file untouched:

```text
$ bash scripts/gate.sh
ok   test_add_then_list
ok   test_list_empty
ok   test_usage
FAIL test_completions_match
exit 1
```

With line 2 of the completion file changed to `complete -W "add list search" notes`, the same copy
passes all four tests and exits 0. The brief's own last line says the work is done when the gate
passes, so this file is required, and I treated it as part of the approved work.

`README.md` is my call, and you can strike it. Its first paragraph describes each command the tool
has, and it is the only place a person learns them. A README that leaves out `search` is wrong the
day the pull request merges, so the task adds a sentence for it. Striking this removes goal item 11
and one file from item 13, and nothing else changes.

## Approaches

All three keep the tool to one file.

| Approach | Label | Trade-off |
| --- | --- | --- |
| `grep` with fixed-string and ignore-case options | Documented | One line. Its exit status is already 0 for a hit and 1 for a miss. It needs `grep` on the machine, and an unreadable file makes it exit 2. |
| A `while read` loop in bash that lowercases each line and the word, then compares | Assembled from documented pieces | No outside program. More lines, and the comparison treats the word as a pattern unless it is quoted exactly right, which is the failure the brief rules out. |
| `awk` with `index(tolower($0), tolower(word))` | Documented | Also plain text. Passing the word in with `-v` rewrites backslashes, so `a\tb` would search for a tab. |

The pick is `grep`. The label rests on this machine's `grep --help` (GNU grep 3.12):

```text
  -F, --fixed-strings       PATTERNS are strings
  -e, --regexp=PATTERNS     use PATTERNS for matching
  -i, --ignore-case         ignore case distinctions in patterns and data
```

The shape that passed every check below is `grep -iF -e "$word" -- "$file"`, after a test that the
word is not empty and a test that the path is a regular file (`[ -f ]`). `-e` is what keeps a word
such as `-n` from being read as an option. How the session writes it is its call, and the goal
checks the behaviour.
I did not probe another `grep`, such as the BSD one on a Mac.

## When it goes wrong

| What happens | What the tool does | Number |
| --- | --- | --- |
| A hit | Prints the notes | Exit 0 |
| No hit, or no notes file | Prints nothing | Exit 1 |
| No word, an empty word, or an unknown command | Prints the usage line on stderr | Exit 2 |
| The notes file exists and can't be read | Passes on `grep`'s message and status. The probe printed `grep: <path>: Permission denied`. | Exit 2 |

The last row shares exit 2 with the usage error. I left it that way: the message on stderr tells
the two apart, and no test covers it. Case is folded the way `grep -i` folds it in the caller's
locale. The goal checks only the letters a to z.

A word that contains a line break is out of scope. `grep` would read it as two words and print
notes that contain either.

If the session runs out of time, the skill's time clause ends it at 80 minutes with the work
pushed to a draft pull request.

## A trap in the existing test

`test_completions_match` reads command names with `grep -o "notes [a-z]\+" bin/notes`. Any text in
`bin/notes` where `notes` is followed by a space and a lowercase word counts as a command. On the
throwaway copy, one added comment, `# the notes file`, turned the gate red:

```text
FAIL test_completions_match
exit 1
```

The session must keep that shape out of `bin/notes` everywhere except the usage line. That covers
comments and messages alike. This spec leaves the test as it is. Making it stricter is a separate
piece of work, and the repo has no backlog to file it in, so it is named here for you.

A second trap is in the runner. Its header says it runs every `test_*` function, but the loop on
`tests/run.sh:21` names four. A new test that is not added to that line never runs and never fails.
Goal item 9 checks for this.

## Assumptions

There is one task, so no assumption spans two. The task rests on these.

- A note is one line, and file order is oldest first. Source: `bin/notes:5` appends with `>>`, and
  `bin/notes:6` prints with `cat`.
- `grep` is on the path where the tool runs. Probe: `grep --version` prints `grep (GNU grep) 3.12`
  here.
- The repo runs no CI on pull requests. Source: `.workstation/remote.txt`, "The repo runs no CI on
  pull requests, so the gate on a branch's last commit is its only full run." The gate run on the
  final commit is therefore the only proof, and the pull request must quote it.
- The remote is `example/notes`, public, default branch `main`. Source: the same file.

## Files

The list comes from four searches over the tracked files at `d39b696`. Every hit is listed.

`git grep -nw list` has 7 hits.

| Hit | Verdict |
| --- | --- |
| `README.md:4` | Change. The paragraph describes each command. |
| `bin/notes:6` | Read only. The `list` branch stays as it is. |
| `bin/notes:7` | Change. The usage line. |
| `brief.md:3` | Dismissed. Geoff's sentence, which uses the word in its ordinary sense. |
| `completions/notes.bash:2` | Change. The list of commands that completion offers. |
| `tests/run.sh:7` | Read only. An existing test of `list`. |
| `tests/run.sh:10` | Read only. An existing test of `list`. |

`git grep -n usage` has 5 hits.

| Hit | Verdict |
| --- | --- |
| `bin/notes:7` | Change. Counted above. |
| `brief.md:9` | Dismissed. The brief is the record of the conversation and doesn't change. |
| `tests/run.sh:12` | Read only. `test_usage` stays. |
| `tests/run.sh:13` | Read only. It checks only that the line starts with `usage:`, so it passes before and after. |
| `tests/run.sh:21` | Change. The loop that names each test gains the new ones. |

`git grep -n 'bin/notes'` has 9 hits.

| Hit | Verdict |
| --- | --- |
| `README.md:3`, `README.md:4` | Change. Counted above. |
| `brief.md:7`, `brief.md:10` | Dismissed. The brief doesn't change. |
| `completions/notes.bash:1` | Read only. The comment stays true. |
| `tests/run.sh:7`, `tests/run.sh:10`, `tests/run.sh:13` | Read only. Existing tests. |
| `tests/run.sh:17` | Read only. This is the line that makes the completion file part of the work. |

`git grep -n -i search` has 3 hits, `brief.md:1`, `brief.md:7`, and `brief.md:12`. All three are
dismissed: nothing in the code is named `search` today, so the new command collides with nothing.

That leaves four files to change and two the task doesn't touch.

| File | What changes |
| --- | --- |
| `bin/notes` | The `search` branch, and the usage line. |
| `tests/run.sh` | New `test_search_*` functions, and their names on the loop line. |
| `completions/notes.bash` | Line 2 offers `add list search`. |
| `README.md` | A sentence for `search`. |
| `scripts/gate.sh` | Nothing. It had no hit, and it runs `tests/run.sh` whatever that holds. |
| `brief.md` | Nothing. |

## Commands and the denials log

The denials log holds three entries in the last 30 days (2026-10-23 to 2026-11-22).

| Refused | Reason logged | Does the task run it? |
| --- | --- | --- |
| `git push --force origin main` | Force push to the default branch | No. The session pushes only the branch it made, with no force flag. |
| `rm -rf ~/.notes.bak` | Recursive delete outside the working folder | No. See below. |
| WebFetch of `https://example.invalid/notes` | Unknown host | No. The task fetches nothing. |

The second entry is the one to watch, because the tests make scratch files outside the worktree.
The existing tests use `mktemp` and at most `rm -f` on one file, inside the test script. New tests
do the same: `NOTES_FILE` always points at a `mktemp` file, never at `~/.notes`, and the session
never runs a recursive delete on a path outside its worktree. Scratch files left in the temp
folder are fine.

The task's own commands are these. Each ran in this Claude Code session today, on `main` or on the
throwaway copy.

- `bash scripts/gate.sh`
- `bin/notes search`, `bin/notes list`, and `bin/notes bogus`, with `NOTES_FILE` set to a `mktemp`
  file
- `grep -c` over `completions/notes.bash`, `README.md`, and `tests/run.sh`
- `git diff main...HEAD --name-only`
- `git show main:tests/run.sh | sed -n '6,20p' | grep -cvxF -f tests/run.sh`

Branch, commit, push, the draft pull request, and marking it ready follow `building-from-specs`,
"A session at work" and "The pull request". This spec carries none of those command lines.

## The task: notes-search

| | |
| --- | --- |
| Goal | The 13 items below |
| Files | `bin/notes`, `tests/run.sh`, `completions/notes.bash`, `README.md` |
| Reviewer | `standards:diff-reviewer`, on Opus at high, as `building-from-specs` "Gates and review" requires before the pull request is ready. No sign-in or data path and no rendered UI, so no second reviewer. |
| Session | Opus at high |
| Minutes | 40. The time clause is `or stop after 80 minutes`. |
| Waits for | Nothing |
| Merge order | One pull request, so there is no order to give. |

### Minutes

`.workstation/task-report.txt` has two like tasks, each a change to one command with its tests.
"Add notes list" (#12) was planned at 30 and took 34 with no fix round. "Let notes add read stdin"
(#18) was planned at 30 and took 41 with one fix round. Both ran over 30, and their mean is 37.5.
"Add the usage test" (#15, 12 minutes) changed only the test file and is not a like task. The task
drives no CI, timer, or idle limit, so nothing is added for waits. I rounded 37.5 up to 40.

### Goal

Items 1 to 8 use this fixture. Run it from the repo root first.

```bash
f=$(mktemp)
printf '%s\n' 'buy rope' 'call mum' 'Rope for the boat' 'a.c' 'abc' 'use the -n flag' > "$f"
export NOTES_FILE=$f
```

Each item gives its check, what the check printed on `main` today, and what it printed on the
throwaway copy that has a working `search`. Every check ran twice on each and printed the same
thing both times. Today, every `search` check prints the old usage line and exits 2, because
`bin/notes` has no `search` branch. That is the gap the task closes.

1. `bin/notes search rope` prints `buy rope` and then `Rope for the boat`, and exits 0.
   `bin/notes search rop` prints the same two lines, because the word may be part of a longer one.
   Today: `usage: notes add <text> | notes list`, exit 2, for both. Copy: the two lines in that
   order, exit 0, for both.
2. `bin/notes search ROPE` prints the same two lines and exits 0.
   Today: the old usage line, exit 2. Copy: `buy rope`, `Rope for the boat`, exit 0.
3. The word is plain text. `bin/notes search a.c` prints only `a.c`. `bin/notes search '.*'` prints
   nothing and exits 1. `bin/notes search -n` prints `use the -n flag`.
   Today: the old usage line and exit 2 for all three. Copy: `a.c`, exit 0; nothing, exit 1;
   `use the -n flag`, exit 0.
4. `bin/notes search zebra` prints nothing on stdout or stderr and exits 1.
   Today: the old usage line, exit 2. Copy: nothing, exit 1, and
   `bin/notes search zebra 2>&1 | wc -c` prints `0`.
5. With no notes file, `NOTES_FILE=$f.gone bin/notes search rope` prints nothing on stdout or
   stderr and exits 1. With a folder in its place, `NOTES_FILE=$(mktemp -d) bin/notes search rope`
   does the same.
   Today: the old usage line, exit 2, for both. Copy: nothing, exit 1, for both.
6. `bin/notes search`, `bin/notes search ''`, and `bin/notes bogus` each print exactly
   `usage: notes add <text> | notes list | notes search <word>` on stderr, print nothing on
   stdout, and exit 2.
   Today: `usage: notes add <text> | notes list`, exit 2, for all three. Copy: the new line, exit
   2, for all three, and `bin/notes search 2>/dev/null | wc -c` prints `0`.
7. `bin/notes search the boat` prints `Rope for the boat` and exits 0. `bin/notes search boat the`
   prints nothing and exits 1. `bin/notes search ' '` prints the four notes that have a space,
   `buy rope`, `call mum`, `Rope for the boat`, and `use the -n flag`, and exits 0.
   Today: the old usage line, exit 2, for all three. Copy: `Rope for the boat`, exit 0; nothing,
   exit 1; the four notes, exit 0.
8. `add` and `list` are unchanged. `bin/notes list` prints the six fixture lines in order and exits
   0. The four existing test functions stay word for word:
   `git show main:tests/run.sh | sed -n '6,20p' | grep -cvxF -f tests/run.sh` prints `0`. It counts
   the lines of today's four functions that the new file no longer holds.
   Today: the six lines, exit 0, and the count is `0`. This item is a guard, so it passes today. It
   fails if the session rewrites a test to fit what it built: with the body of `test_usage`
   changed to `true` in a scratch copy, the count was `1`.
9. `tests/run.sh` has a `test_search_*` function for each of items 1 to 7, and every test defined
   runs. `bash scripts/gate.sh | grep -c '^ok   test_search_'` prints `7` or more, and
   `grep -c '^test_[a-z_]*() {' tests/run.sh` prints the same number as
   `bash scripts/gate.sh | grep -c '^ok '`. New functions open the way the existing four do, with
   `test_name() {` at the start of a line, so the first count sees them.
   Today: `0`, and `4` against `4`.
10. `grep -c 'complete -W "add list search" notes' completions/notes.bash` prints `1`.
    Today: `0`. Copy: `1`.
11. `README.md` says what `search` does: it finds the word inside a note, ignores case, takes the
    word as plain text, prints the oldest first, and exits 1 when nothing matches.
    `grep -c 'notes search' README.md` prints `1` or more, and the reviewer reads the sentence
    against those five facts. The prose follows `~/.claude/docs/voice/written-for-people.md`, the
    `writing-voice` standard for a README in a shell repo. A session that can't read that file
    matches the README's existing paragraph and says so under `## Decisions`.
    Today: `0`.
12. On the branch's final commit, `bash scripts/gate.sh` exits 0 and prints no `FAIL` line. The
    pull request quotes the whole output with the commit's hash, because no CI will run it.
    Today on `main`: four `ok` lines, exit 0. Copy, with only `bin/notes` and the completion file
    changed: four `ok` lines, exit 0.
13. One pull request against `main` of `example/notes` changes exactly `README.md`, `bin/notes`,
    `completions/notes.bash`, and `tests/run.sh`. `git diff main...HEAD --name-only` prints those
    four paths and no other.
    Today: prints nothing, exit 0.

The goal's condition names this spec by the absolute path of `spec.md` in the main checkout. This
spec is not committed, so a worktree made from the remote's `main` doesn't hold it.

## Start conditions

`building-from-specs` "Launching a task" lists four checks. Two can be answered from here.

- No secret is needed.
- No CI is needed, and the repo is public (`.workstation/remote.txt`).

Two could not run from this session and fall to the session that launches the task:
`claude-worktree-busy` on the main checkout, and the count of working sessions on pavilion.
Neither `claude-worktree-busy` nor `task-report` is on this session's path.

One more check belongs to the launch. Items 8 and 13 compare against the local `main`. This
checkout has no `origin/main` ref, so I could not run them against the remote. The launching
session confirms that local `main` and the remote's `main` are the same commit before it launches.

## Backlog sweep

The scoped sweep found no backlog to read. `git grep -n -i -e backlog -e todo -e fixme` has 0 hits,
the repo has no `docs/` folder, and no tracked file is a backlog. There are no verdicts and no
backlog edits to approve. The repo is below the 15 open items that make a full sweep due.

## Calls Claude made

Nobody could answer a question while this was written. Each of these is where I would have asked.

1. The task changes `completions/notes.bash`, which the brief doesn't name. The gate fails
   without it, and the brief requires the gate to pass.
2. The task changes `README.md`, which the brief doesn't name. This one is optional, and striking
   it costs goal item 11.
3. "Contains the word" means the word may sit inside a longer word. Whole-word matching would be a
   change to one option later. A word of only spaces is searched as given.
4. Extra arguments join into one text, as `add` joins them. The other reading was to refuse them
   with exit 2.
5. An empty word counts as a missing word and exits 2.
6. A missing notes file, or a path that is not a regular file, counts as no match: nothing
   printed, exit 1.
7. An unreadable notes file passes on `grep`'s message and its exit 2, with no test.
8. The mechanism is `grep` with fixed strings, picked over a bash loop and `awk`.
9. `test_completions_match` stays as fragile as it is, and no existing test is edited. The session
   works around the trap.
10. The task is planned at 40 minutes, and its session runs on Opus at high.
11. `spec.md` stays uncommitted, and the goal names it by absolute path. If you want specs kept in
    the repo, that is a commit to `main` before the launch.

## The fresh reader's questions

One reader with no context read this spec against the repo on 2026-11-22. It reran the four
searches, the citations, and every "Today" output, and they held. Its nine questions sort this way.

Answered already: none.

Minor calls, made and marked. Each is now in the text above.

- Nothing checked that a word may sit inside a longer one. A whole-word build passed every item.
  Item 1 now runs `search rop`.
- The rule for a path that is not a regular file had no check, and the hint said "the file
  exists". Item 5 now runs against a folder, and the hint names `[ -f ]`.
- Item 8's diff count passed a rewritten test and failed an honest second loop. It also said it
  passed today when it printed `0` against a required `1`. The check is replaced.
- Item 9's count broke when the loop line wrapped. It now counts function definitions.
- Item 11 named a voice standard this session couldn't read. It now says what a session does if
  it can't read the file either.
- An item that required the review's own verdict was circular for the reviewer. It is gone from
  the goal. The skill still requires the review before the pull request is ready.
- A word of only spaces was undecided. It is searched as given, and item 7 checks it.
- "The first four rows" introduced five rows from the brief. It now says five.

Only Geoff can answer: none new. The two files beyond the brief stand as calls 1 and 2.

The reader could not check the skill's section names, the time clause, or push access to
`example/notes`.

## Not run from here

- Nothing was fetched from GitHub. The remote's facts come from `.workstation/remote.txt`.
- The measured minutes come from `.workstation/task-report.txt`, which stands in for `task-report`.
- The denials come from `.workstation/denials.log`, which stands in for the workstation's log.
- `~/.claude/docs/voice/written-for-people.md` could not be read from this session. This spec
  follows the `writing-voice` skill's shape rules.
