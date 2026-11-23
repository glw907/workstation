# Spec: notes search

Written 2026-11-22 from `brief.md`, for Geoff's approval. One task, one pull request to `main` on
`example/notes`. Nobody could answer a question while this was written, so each place where I would have asked
is a decision, listed under [Calls Claude made](#calls-claude-made).

## Check this before you approve: the brief and the README disagree

The brief says: "No match prints nothing and exits 1." The README says, at lines 10 and 11: "Every command exits
0 when it runs, even when it prints nothing, and 2 on a usage error. Scripts that call `notes` rely on that."
Both can't hold once `search` exists.

**I followed the brief.** A search that finds nothing exits 1. The brief is your ruling on this one command,
and it marks the point "not open". The README's sentence is a general rule, and it describes a tool with two
commands. Nothing in the repo dates one source after the other, since both arrived in commit `745419b`. No
script calls `search` today, because the command doesn't exist, so the scripts the README protects lose
nothing: `add` and `list` keep their output and their exit status.

Following the brief makes the README's sentence false on the day the work merges. So the task also rewrites
that sentence and adds `search` to the README. That makes `README.md` a third changed file, where the brief
names two. Two ways to overrule me, both cheap:

- **You want exit 0 on no match.** Say so instead of approving. Done items 3 and 6 change, and the build
  differs by one line of the tool, one test, and one README sentence.
- **You want the README left alone.** Strike done item 6, and strike `README.md` from the file list and from
  done item 7. The README then states a rule that `search` breaks, until someone fixes it.

## Intent

"I want to find a note without scrolling through the whole list."

The goal is one new command, `bin/notes search <word>`, that prints every note containing the word, oldest
first. The match ignores case, and the word is plain text, never a pattern.

These are not goals: patterns, a search for several words at once, flags such as a case-sensitive mode, line
numbers, highlighting, or any change to `add` and `list`.

The work has failed if a word such as `a.c` or `-v` is read as a pattern or an option, if a search with no
match exits 0 or prints anything, if `add` or `list` changes its output or exit status, or if the README still
tells script authors that every command exits 0.

## Approach

I weighed three ways to match and picked the first. The build uses grep unless grep can't meet a done item.
The done items are what the reviewer reads against, so a build that had to match another way and meets every
item is still correct, and it says why under `## Decisions`.

| Approach | Trade-off |
| --- | --- |
| `grep -iF -- "$word" "$file"`, run only when the file exists | One line. A missing file must be caught first, and a word that holds a newline becomes two words. |
| A bash loop that compares `${line,,}` with `*"${word,,}"*` | No outside program. `read` skips a last line that has no newline unless the loop guards for it, and `${line,,}` needs bash 4. |
| `awk` with `index(tolower($0), tolower(word))` | Portable. It adds a second language to an eight-line bash tool, and the word must go in through `ENVIRON` so awk doesn't read its backslashes. |

The grep mechanism is documented. The labels rest on `man grep` for GNU grep 3.12 on this workstation, and on
probes run on 2026-11-22 against the fixture in the [goal](#goal).

- `-F`: "Interpret PATTERNS as fixed strings, not regular expressions." Probe: `grep -iF -- a.c "$f"` printed
  `a.c` and not `abc`.
- `-i`: "Ignore case distinctions in patterns and input data, so that characters that differ only in case
  match each other." Probe: `grep -iF -- Rope "$f"` printed `Buy rope` and `coil the ROPE`, in file order.
- Exit status: "Normally the exit status is 0 if a line is selected, 1 if no lines were selected, and 2 if an
  error occurred." Probe: `grep -iF -- zebra "$f"` printed nothing and exited 1.
- `--` before the word. Probe: `grep -iF -- -v "$f"` printed `tie -v knot` and exited 0.

The spec proposes no Claude Code mechanism beyond what `building-from-specs` already owns, so no Anthropic docs
page was needed. The work adds no project, service, or running infrastructure, and it publishes no build.

## When it goes wrong

`search` has three exit statuses: 0 when at least one note matches, 1 when none does, and 2 on a usage error.
The first two cases below are requirements. The next three describe what the grep pick does at edges that no
done item covers, so the builder writes no code for them and the reviewer holds nothing against them.

- **The notes file doesn't exist.** No note contains the word, so `search` prints nothing and exits 1. grep
  alone exits 2 here (probe: `grep: ...none: No such file or directory`, exit 2), which would read as a usage
  error, so the tool checks for the file first. Done item 3 covers this.
- **The word is empty, or more than one word follows `search`.** Both are usage errors and exit 2. Done item 4
  covers this.
- **The notes file exists and can't be read.** grep's own message reaches stderr and `search` exits 2 (probe on
  a mode-000 file: `Permission denied`, exit 2). Here 2 means an error that isn't a usage error, and no usage
  line prints. No done item covers it, because a test for it fails when the suite runs as root.
- **The word holds a newline.** grep reads it as two words and prints a note that contains either (probe:
  `$'zebra\nsam'` printed `call Sam`). No note holds a newline, so no caller can mean such a search. No done
  item covers it.
- **Letters outside ASCII.** grep folds case by the caller's locale. No done item covers it.
- **The build runs long.** The goal's time clause ends it at 80 minutes. The session then commits, pushes,
  and writes what is left in the draft pull request, as `building-from-specs` "In place of a question" says.

## Files

The list comes from five searches over the tracked files, run with `git grep -n` on commit `745419b`.

| Search | Hits | Where |
| --- | --- | --- |
| `usage` | 6 | `README.md:10`, `bin/notes:7`, `brief.md:9`, `tests/run.sh:12`, `:13`, `:15` |
| `notes list` | 4 | `README.md:4`, `bin/notes:7`, `tests/run.sh:7`, `:10` |
| `exit`, any case | 5 | `README.md:10`, `bin/notes:7`, `brief.md:9`, `tests/run.sh:2`, `:18` |
| `bin/notes` | 7 | `README.md:3`, `:4`, `brief.md:7`, `:10`, `tests/run.sh:7`, `:10`, `:13` |
| `search`, any case | 3 | `brief.md:1`, `:7`, `:12` |

The task changes three files.

- `bin/notes`: line 7 holds the usage line, and the `case` gains a `search` branch.
- `tests/run.sh`: new test functions, and line 15, the `for` list. The runner runs only the names on that
  list, although its comment at line 2 says it runs every `test_*` function. A new test that isn't added to the
  list never runs and never fails. Lines 7, 10, and 13 are the three tests that exist, and they stay as they are.
- `README.md`: lines 3 and 4 describe the commands, and line 10 states the exit rule.

The other hits are dismissed. `brief.md` is the input to this spec and doesn't change. `tests/run.sh:18` is the
runner's own exit. `scripts/gate.sh` has no hit and doesn't change.

Only one task exists, so no assumption is shared between tasks.

The repo has no backlog file among its five tracked files (`git ls-files`), so the scoped backlog sweep had no
items to read and this spec carries no backlog edits. The misleading comment at `tests/run.sh:2` is outside
this task. With no backlog file to log it in, the task session leaves the comment alone and names it under
`## For Geoff` in the pull request. It adds no file for it.

## Commands and the denials log

`.workstation/denials.log` holds three refusals in the last 30 days, since 2026-10-23. None matches a command
this task runs.

| Refused | Reason | This task |
| --- | --- | --- |
| `git push --force origin main` (2026-11-03) | force push to the default branch | Pushes only the branch it created, with no force flag. It never pushes `main`. |
| `rm -rf ~/.notes.bak` (2026-11-09) | recursive delete outside the working folder | Deletes nothing recursively. Every run of `bin/notes` sets `NOTES_FILE` to a `mktemp` path, so the task never reads or writes `~/.notes`. |
| WebFetch `https://example.invalid/notes` (2026-11-17) | unknown host | Fetches nothing. The grep facts the build needs are quoted above. |

Every command line in the goal ran in Claude Code on 2026-11-22, as written, while this spec was written. Its
output is under the goal. The existing test at `tests/run.sh:10` already runs `rm -f` on one `mktemp` file, and
the gate passed with it today. The commit, push, and pull request commands belong to `building-from-specs` "A
session at work" and "The pull request", and the goal carries none of them. I ran none, because this session
was told to commit nothing and can't reach the remote.

## Task: notes-search

The task waits for no other task, and its pull request is the only one, so there is no merge order.

**Files:** `bin/notes`, `tests/run.sh`, `README.md`.

**Reviewer:** `standards:diff-reviewer`, on Opus at high. The work has no sign-in path and no rendered UI. It
reads the notes file and writes nothing to it, so no second reviewer reads it.

**Minutes:** 40. The goal's time clause is `or stop after 80 minutes`.

The estimate comes from `task-report --since 2026-11-01`:

| PR | Title | Planned | Actual | Fix rounds |
| --- | --- | --- | --- | --- |
| 12 | Add notes list | 30 | 34 | 0 |
| 15 | Add the usage test | 15 | 12 | 0 |
| 18 | Let notes add read stdin | 30 | 41 | 1 |

The like tasks are 12 and 18, the two that changed a command and its tests. They took 34 and 41 minutes, and
both ran over a plan of 30. This task adds a command as 12 did, with three exit paths, four tests, and a README
edit, so I set it near the higher of the two. Nothing adds a wait: `.workstation/remote.txt` says "The repo
runs no CI on pull requests".

**Launch:** by `building-from-specs` "Launching a task", from the main checkout, named `notes-search`, on
Sonnet at high. The condition names this spec by its absolute path in the main checkout, names this task,
lists the done items below, and ends with the time clause.

### Goal

The repo has no CI on pull requests, so "the gate on a branch's last commit is its only full run"
(`.workstation/remote.txt`). Every check below runs on the branch's last commit.

Checks 1 to 4 use this fixture:

```bash
f=$(mktemp); printf '%s\n' 'Buy rope' 'call Sam' 'coil the ROPE' 'a.c' 'abc' 'tie -v knot' > "$f"
```

I ran every check on today's code, twice, on 2026-11-22. The two runs gave the same output. In checks 1 to 3
every command prints `usage: notes add <text> | notes list` and `exit=2` today, because `search` isn't a
command yet. That is the reason the task fixes.

Each item's command shows the behavior. Where an item says more than its command can show, the item says so,
and the reviewer reads that part in the diff.

1. **A search prints every note that contains the word, in any case, oldest first, and exits 0.**

   ```bash
   NOTES_FILE=$f bin/notes search Rope 2>&1; echo "exit=$?"
   ```

   When done, it prints `Buy rope`, then `coil the ROPE`, then `exit=0`.

2. **The word is plain text, never a pattern or an option.**

   ```bash
   NOTES_FILE=$f bin/notes search a.c 2>&1; echo "exit=$?"
   NOTES_FILE=$f bin/notes search -v 2>&1; echo "exit=$?"
   ```

   When done, the first prints `a.c` and `exit=0`, without `abc`. The second prints `tie -v knot` and `exit=0`.

3. **No match prints nothing and exits 1, and so does a notes file that doesn't exist.**

   ```bash
   NOTES_FILE=$f bin/notes search zebra 2>&1; echo "exit=$?"
   NOTES_FILE=$f.none bin/notes search rope 2>&1; echo "exit=$?"
   ```

   When done, each prints only `exit=1`.

4. **A missing word, an empty word, a second word, and an unknown command each print nothing on stdout, print
   the one usage line on stderr, and exit 2. The usage line is
   `usage: notes add <text> | notes list | notes search <word>`.**

   ```bash
   check() { NOTES_FILE=$f bin/notes "$@" 2>/dev/null; echo "exit=$?"; NOTES_FILE=$f bin/notes "$@" 2>&1 >/dev/null; }
   check search; check search ''; check search buy rope; check bogus
   ```

   `check` runs the command twice: once showing only stdout and the exit status, once showing only stderr.
   When done, each of the four calls prints `exit=2` with nothing before it, then that usage line. Today each
   prints `exit=2`, then `usage: notes add <text> | notes list`, so the item fails today only because the
   usage line doesn't name `search`.

5. **The gate passes, and it runs a test for each of items 1 to 4.**

   ```bash
   bash scripts/gate.sh; echo "exit=$?"
   ```

   When done, it prints seven `ok` lines, no `FAIL` line, and `exit=0`. Three lines are for the tests that
   exist, which stay unchanged. Four are for `test_search_match`, `test_search_plain_text`,
   `test_search_no_match`, and `test_search_usage`. Today the gate prints the three existing `ok` lines and
   `exit=0`. Each new test asserts the output and the exit status that its item states. The gate's output
   can't show that, so the reviewer reads the four tests against items 1 to 4.

6. **The README describes `search` and no longer says every command exits 0.** It says what `search` prints,
   that the match ignores case and takes the word as plain text, and that `search` exits 1 when no note
   matches. It keeps the promise that `add` and `list` exit 0 when they run. Its voice standard is the one
   the `writing-voice` skill names for a README in a shell repo, `~/.claude/docs/voice/written-for-people.md`.
   That file couldn't be read where this spec was written, so the task session opens it through the skill.

   ```bash
   grep -c 'notes search <word>' README.md
   grep -c 'Every command exits 0' README.md
   ```

   When done, the first prints `1` or more and the second prints `0`. Today they print `0` and `1`. The two
   commands show that `search` is named and the old sentence is gone. The reviewer reads the rest of the item
   in the README.

7. **The branch changes only the three files.**

   ```bash
   git diff --name-only main...HEAD
   ```

   When done, it prints `README.md`, `bin/notes`, and `tests/run.sh`, and nothing else. Today it prints
   nothing.

8. **The pull request to `main` on `example/notes` quotes the output of checks 1 to 7, with the hash of the
   branch's last commit, where they ran.** The pull request itself shows this. I name no command, because
   none could run today against a remote this session can't reach.

The review and the step that marks the pull request ready are not done items. `building-from-specs` "Gates and
review" and "The pull request" own them, and the reviewer reads the branch against items 1 to 7.

Geoff runs no step in this task. He approves the pull request by number.

## Before launch

`spec.md` is untracked today, and a task's worktree starts from the remote's default branch, so the worktree
won't hold it. The task session and its reviewer read the spec by its absolute path in the main checkout,
which the goal's condition gives them. Nothing is committed to `main` for the launch, because the README says
"Work reaches `main` through a pull request to `origin`." Whether specs belong in this repo's history is
Geoff's to say, and this spec doesn't settle it.

I could not test the start conditions against today's live sessions. `claude-worktree-busy` isn't installed
where this spec was written, and the remote can't be reached from here. The launching session runs the four
checks in "Launching a task" on the day. Two are settled now: the task needs no secret, and it needs no CI.
`.workstation/remote.txt` shows the repo is public with `main` as its default branch.

One fresh reader, on Fable at high, read this spec with no context on 2026-11-22 and reran the checks. It
confirmed the search counts, the quotes, the grep probes, the minutes, and the "today" outputs of checks 1 to
6. Its findings sorted this way:

- **Answered already:** none. Every finding led to a change.
- **Calls I made and marked:** all but one, folded in above. The larger ones: check 4 now shows stdout
  and stderr apart, done item 8 no longer waits on its own review, check 7 uses a ref that exists, the spec
  is read by path where an earlier draft pushed it to `main`, and the stale comment goes to the pull request
  where an earlier draft sent it to a backlog that doesn't exist.
- **Only Geoff can answer:** the exit status on no match, at the top of this spec.

## Calls Claude made

1. **Exit 1 on no match, from the brief, over the README's "every command exits 0".** See the top of this spec.
2. **`README.md` joins the two files the brief names.** The exit rule it states would be false after the
   merge. Striking done item 6 reverses this.
3. **A notes file that doesn't exist is a search with no match: no output, exit 1.** The brief doesn't cover
   it. `list` already treats a missing file as no notes, and exit 2 would look like a usage error.
4. **An empty word is a missing word: usage line, exit 2.** Every note contains the empty string, so the
   search would be `list` under another name.
5. **A second word is a usage error: usage line, exit 2.** The brief says `<word>`. The other option was to
   join the words into one phrase, as `add` joins its text. I took the strict one because loosening it later
   breaks no caller, and tightening it later would. A phrase still works when quoted: `notes search "buy rope"`.
6. **The usage line reads `usage: notes add <text> | notes list | notes search <word>`.** The brief says only
   that it names the new command.
7. **An unknown command prints the same usage line as a missing word.** The tool has one usage line today,
   and done item 4 keeps it that way.
8. **grep is the pick for matching.** Three edges that no done item covers stand as "When it goes wrong"
   describes them: an unreadable file exits 2 with grep's message, a word with a newline matches either part,
   and letters outside ASCII fold by locale.
9. **The non-goals name line numbers, highlighting, and a case-sensitive flag.** The brief asks for none of
   them, and naming them keeps the build from adding one.
10. **Done item 7 holds the branch to the three files.** The brief doesn't ask for the guard.
11. **40 minutes, and an 80-minute time clause**, from the two like tasks in `task-report`.
12. **The task session runs on Sonnet at high.** The spec settles every behavior, which leaves edits to three
    small files. The reviewer runs on Opus at high, as `building-from-specs` "Models" says.
13. **The four new tests have fixed names**, so that done item 5 can be checked from the gate's output.
14. **The spec is read by its path in the main checkout and isn't committed to `main`.** See "Before launch".
15. **No backlog edits.** The repo has no backlog file, so the stale comment at `tests/run.sh:2` goes in the
    pull request's `## For Geoff`.
