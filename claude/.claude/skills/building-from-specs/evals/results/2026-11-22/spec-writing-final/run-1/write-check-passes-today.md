# Spec: notes search

Source: `brief.md`, the design Geoff settled in conversation. One task, one pull request.

## Intent

Geoff: "I want to find a note without scrolling through the whole list."

The goal is a new command, `bin/notes search <word>`, that prints every note containing the word, oldest
first. The match ignores case, and the word is plain text, never a pattern.

Non-goals: patterns, whole-word matching, matching several terms separately, highlighting, line numbers,
any change to `add` or `list`, and any change to how `tests/run.sh` picks the tests it runs.

The work fails if a word such as `r.pe` is read as a pattern, if the gate passes without running the search
tests, or if the README still says nothing about `search`.

## Approach

| Option | Trade-off |
| --- | --- |
| `grep -iF -e "$*" -- "$file"` | One line. grep's exit status is already the brief's: 0 on a match, 1 on none. It needs a guard for a missing file, where grep exits 2. |
| A bash loop comparing `${line,,}` with `${word,,}` | No external command, but more code and a hand-kept exit status. |
| `awk` with `index(tolower($0), tolower(w))` | Plain text by construction, but the word must travel through `ENVIRON` to dodge awk's escape handling. |

The pick is grep. Its labels:

- `-F` is documented. grep(1), GNU grep 3.12: "Interpret PATTERNS as fixed strings, not regular expressions."
- `-i` is documented. `grep --help`: "ignore case distinctions in patterns and data".
- The exit status is documented. grep(1): "the exit status is 0 if a line is selected, 1 if no lines were
  selected, and 2 if an error occurred."
- The branch as a whole is assembled from documented pieces. A scratch copy of `bin/notes` outside the repo,
  with the branch `search) shift; [ -n "$*" ] || usage; [ -f "$file" ] || exit 1; grep -iF -e "$*" -- "$file"`
  and the usage line moved into a `usage` function, printed the "when done" output of done items 1 to 5.
- `-e` and `--` keep a word that starts with a dash from being read as an option. The same copy without
  them printed grep's version text and exited 0 on done item 2's second command.

## When it goes wrong

- With no notes file, a search is a search with no match: it prints nothing and exits 1. Without the guard,
  grep would print an error and exit 2.
- A notes file that exists and can't be read passes grep's message and its exit 2 through unchanged, so
  exit 2 then means either a usage error or a read error.
- An empty word (`bin/notes search ""`) counts as a missing word. Passed to grep, it would match every note.
- Case folding is whatever `grep -i` does in the caller's locale. The tests use ASCII only.
- A word that holds a newline, and several empty words (`search "" ""`), are outside this work.
- The work sets no size limit. The one number is the goal's time clause, 80 minutes.

## Files

`grep -rn usage bin tests scripts README.md` prints 4 hits.

- `bin/notes:7`, the usage line: changes, and moves into a function, because two branches now print it.
- `tests/run.sh:12` and `:13`, `test_usage`: unchanged. It checks only that the first word is `usage:`.
- `tests/run.sh:15`, the `for` list of tests: changes. The runner runs only the names in this list, so each
  new test is added here. The comment on line 2, which says it runs every `test_*` function, stays.

`grep -rnE 'notes (add|list)' bin tests scripts README.md` prints 5 hits.

- `bin/notes:7`: listed above.
- `tests/run.sh:7` and `:10`, the two existing tests: unchanged.
- `README.md:3` and `:4`, the paragraph that describes the commands: gains the `search` sentences.

The task therefore changes `bin/notes`, `tests/run.sh`, and `README.md`, and adds `spec.md` unchanged (see
"Start conditions"). `scripts/gate.sh` only runs `tests/run.sh` and stays as it is. `brief.md` stays as it is.

## Commands against the denials log

The log holds three refusals from the last 30 days (2026-10-23 to 2026-11-22): a force push to `main`, an
`rm -rf` outside the working folder, and a web fetch to an unknown host. The task runs `bin/notes`,
`bash scripts/gate.sh`, `grep`, `mktemp`, `rm -f` on a test's own `mktemp` file, and the git and `gh` steps
that `building-from-specs` owns. It pushes only its own branch without force, deletes nothing recursively,
and fetches nothing from the web, so none of the three applies. Every test that reaches the notes file sets
`NOTES_FILE` to a `mktemp` path, so no test reads or writes `~/.notes`.

## Start conditions

`building-from-specs` "Launching a task" owns the four launch checks. The task needs no secret and no CI:
`.workstation/remote.txt` shows `example/notes` is public and runs no CI on pull requests.
`claude-worktree-busy` and `claude agents --json` could not run from the session that wrote this spec, so
the launching session runs them. This checkout has no `origin/main` ref (`git rev-parse origin/main` fails),
so the launching session also confirms that the remote's `main` holds commit `7115ad0`.

`spec.md` is untracked in the main checkout, and the task's worktree starts from the remote's `main`, so
the worktree won't hold it. The launch condition names the spec by its absolute path in the main checkout.
The task's first commit copies that file, unchanged, to `spec.md` at the root of its branch, where the
reviewer reads it and beside the tracked `brief.md`.

## The task: `notes-search`

It waits for no other task. Its one pull request merges on its own, so there is no merge order. The build
runs on Sonnet at medium effort, because every call that needs judgment is settled here.

Reviewer: `standards:diff-reviewer`, on Opus at high. The work has no sign-in, data, or rendered UI.

Minutes: 40. `task-report --since 2026-11-01` gives two like tasks, each one command with its tests: pull
request 12, "Add notes list", measured 34 minutes, and pull request 18, "Let notes add read stdin", measured
41 minutes with one fix round. Their mean is 38, rounded up to 40. Pull request 15 only added a test and is
left out. No CI or timer adds a wait. The time clause is `or stop after 80 minutes`.

### Goal

Items 1 to 4 use this fixture. Run it in the same shell command as the item, because `$f` does not last
from one Bash call to the next.

```bash
f=$(mktemp); for n in "Buy rope" "call the vet" "ROPE is 10m"; do NOTES_FILE=$f bin/notes add "$n"; done
```

Today each command in items 1 to 5 prints `usage: notes add <text> | notes list` and then `exit 2`.

1. A search prints the notes that hold the word anywhere in their text, oldest first, whatever their case.
   `NOTES_FILE=$f bin/notes search rop; echo "exit $?"`
   When done: `Buy rope`, `ROPE is 10m`, `exit 0`.
2. A word that no note contains as plain text prints nothing and exits 1, pattern characters and a leading
   dash included.
   `NOTES_FILE=$f bin/notes search r.pe; echo "exit $?"` and
   `NOTES_FILE=$f bin/notes search --version; echo "exit $?"`
   When done, each prints `exit 1` and nothing else.
3. The words after `search` join with one space, as `add` joins its text.
   `NOTES_FILE=$f bin/notes search rope is; echo "exit $?"`
   When done: `ROPE is 10m`, `exit 0`.
4. A missing notes file is no match.
   `NOTES_FILE=$f.none bin/notes search rop; echo "exit $?"`
   When done: `exit 1` and nothing else.
5. A missing or empty word prints the usage line, which names the new command, on stderr and exits 2.
   `bin/notes search 2>&1 >/dev/null; echo "exit $?"` and `bin/notes search "" 2>&1 >/dev/null; echo "exit $?"`
   When done, each prints `usage: notes add <text> | notes list | notes search <word>`, then `exit 2`.
6. The gate passes and runs five search tests, one for each item above: `test_search_match`,
   `test_search_plain_text`, `test_search_phrase`, `test_search_no_file`, and `test_search_missing_word`.
   `bash scripts/gate.sh | grep -c '^ok   test_search_'`
   Today: `0`. When done: `5`.
   `bash scripts/gate.sh; echo "exit $?"`
   Today and when done, the last line is `exit 0`. The pull request quotes this run from the branch's last
   commit.
7. The README names the new command. The reviewer reads that it also says the match ignores case, the word
   is plain text, and no match exits 1. Its voice standard is the one the `writing-voice` router gives a
   README in a shell repo, `~/.claude/docs/voice/written-for-people.md`.
   `grep -c 'bin/notes search <word>' README.md`
   Today: `0`. When done: 1 or more.
   `grep -c notes README.md`
   Today: `3`. When done: 1 or more.
8. The branch carries the spec.
   `git ls-files spec.md`
   Today: nothing. When done: `spec.md`.

The review, the pull request, and its report follow `building-from-specs` "Gates and review" and "The pull
request".

## Other points

The work adds no project, service, or running infrastructure, so it has no hosting choice to make.

The backlog sweep has nothing to read. `git ls-files | grep -icE 'backlog|todo|issues'` prints 0, so the
repo tracks no backlog file, and the remote's issues could not be read from the session that wrote this
spec. There are no verdicts.

No assumption spans tasks.

## Calls Claude made

1. The brief's two last done checks pass on today's code (`bash scripts/gate.sh` exits 0 and
   `grep -c notes README.md` prints 3), so each stays, as the brief names it, beside a check that fails
   today, in done items 6 and 7.
2. "Contains the word" means the note holds that text anywhere, so `rop` finds `Buy rope`; whole-word
   matching, one `-w` away, was passed over.
3. The words after `search` join with one space, as `add` joins its text, where a second word could have
   been a usage error.
4. An empty word counts as a missing word.
5. A missing notes file is no match and exits 1, in line with `list`, which prints nothing for it.
6. An unreadable notes file passes grep's message and exit 2 through.
7. A word that starts with a dash is searched as text.
8. The usage line reads `usage: notes add <text> | notes list | notes search <word>`.
9. The README also says how the match works and what no match exits with, beyond naming the command.
10. grep is the mechanism, over a bash loop or awk.
11. The five tests carry the names in done item 6.
12. `spec.md` rides the task's branch as its first commit, because the README says work reaches `main`
    through a pull request.
13. The task is planned at 40 minutes and builds on Sonnet at medium effort.
