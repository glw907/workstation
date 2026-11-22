# Add `notes search` to find a note by a word

This spec turns the settled design in `brief.md` into one task that ends in one pull request. It adds
`bin/notes search <word>`, which prints every note that contains the word, oldest first, and ignores case.
The design is unchanged except in one place: the gate, `bash scripts/gate.sh`, can't pass unless the work also changes
`completions/notes.bash`, a file the brief leaves out. Two things wait for Geoff. He approves this spec with
that third file in it, and he gives the repo a remote, because it has none today and a pull request needs one.

## Intent

Geoff said: "I want to find a note without scrolling through the whole list."

The goals:

- `bin/notes search <word>` prints each note that contains the word, in the order the notes were added.
- The match ignores case.
- The word is plain text. No character in it is read as a pattern or as an option.
- A search that finds nothing prints nothing and exits 1.
- A search with no word prints the usage line and exits 2.

The work leaves these alone:

- `add` and `list` behave as they do today, and their tests stay as written.
- Search takes no flags. It has no whole-word mode, no pattern mode, and no limit on the count of results.
- Search prints the notes as they are stored. It adds no line numbers, colors, or highlights.
- `README.md` stays as it is. "Calls Claude made" says why.

The work has failed if any of these is true when the pull request is ready:

- A word such as `.` or `-i` is read as a pattern or an option.
- A search that finds nothing exits 0, or prints anything.
- `add` or `list` behaves differently, or one of the three tests that pass today was edited or removed.
- The gate fails, or it passes without running the new tests.

## How search behaves

Each row is one case the task builds. The notes file is `$NOTES_FILE`, or `$HOME/.notes` when that is unset, as it is
for `add` and `list`.

| Command | Prints | Exits |
| --- | --- | --- |
| `notes search rope`, with matching notes | Each matching note on standard output, oldest first | 0 |
| `notes search rope`, with no matching note | Nothing | 1 |
| `notes search rope`, with no notes file | Nothing | 1 |
| `notes search the rope` | Each note that contains `the rope` | 0 or 1, by the same rule |
| `notes search` | The usage line on standard error | 2 |
| `notes search ''` | The usage line on standard error | 2 |

A note matches when the word appears anywhere in it, so `rope` finds `ropes` and `tightrope`. Words after the
first join with one space into a single text, the way `add` joins its words. A word made only of spaces is still a word, and search looks for that space. The
usage line becomes, exactly:

```text
usage: notes add <text> | notes list | notes search <word>
```

`bin/notes` prints that same line for an unknown command, as it prints the shorter one today.

## The file the brief leaves out

The brief says the work changes `bin/notes` and `tests/run.sh`, and that the work is done when the gate
passes. Both can't hold. The gate runs `test_completions_match` in `tests/run.sh`, which reads each command
out of the usage line and fails if `completions/notes.bash` doesn't offer it. The new usage line names
`search`, and the completion file offers only `add list`.

This probe runs the test's check against the new usage line and today's completion file:

```bash
for c in add list search; do
  grep -qw "$c" completions/notes.bash && echo "$c offered" || echo "$c NOT offered"
done
```

```text
add offered
list offered
search NOT offered
```

So the task changes three files. The third change is one word: `compgen -W "add list"` becomes
`compgen -W "add list search"`.

## Approaches

Three ways to match plain text without regard to case were weighed.

- **`grep -i -F -e`, the pick.** One line, and the exit status of `grep` is already the one the design asks for: 0 for
  a match and 1 for none. It reads the file once and holds none of it in a shell variable. It costs a
  dependency on `grep`, which every system that runs this bash script carries.
- **A bash loop** that lowers each line with `${line,,}` and tests `[[ $line == *"$word"* ]]`. It needs no
  outside program. It needs bash 4, it is five lines in place of one, and an unquoted `$word` in that test
  turns the word back into a pattern without any error.
- **`awk` with `index(tolower($0), tolower(word))`.** It is as plain as grep. The word has to pass through
  `-v`, which reads backslash escapes, so a word such as `\n` would change on the way in.

The shape of the new branch in `bin/notes`:

```bash
search)
  shift
  # No word, or an empty one: the usage line, exit 2.
  # No notes file: exit 1 with no output.
  grep -i -F -e "$*" -- "$file" ;;
```

The script runs under `set -e`, so a status of 1 from `grep` becomes the script's. `-e` is required: without it a word
such as `-i` is read as an option.

## When it goes wrong

- **No notes file.** `grep` would print an error and exit 2, which is the usage status. The branch checks for
  the file first and exits 1 with no output, because no note contains the word.
- **An empty word.** `grep -F -e ''` matches every line. The branch treats an empty word as a missing one and
  exits 2 with the usage line.
- **A notes file that can't be read.** The message and the status 2 that `grep` gives pass through. The branch adds nothing
  for this case.
- **A word that holds a newline.** `grep` reads it as two words and prints notes that match either. A note is one
  line, so no test covers this.
- **Letters outside ASCII.** `grep -i` folds case by the caller's locale. ASCII letters fold in every locale.

The limits and their numbers:

- Search sets no limit on the size of the notes file or the count of notes.
- The exit statuses are 0 for a match, 1 for none, and 2 for a missing word.
- The task runs for 30 planned minutes, and its goal stops it after 60.

## Sources and probes

Every mechanism here is documented. Each label rests on the `grep` manual page on this machine, GNU grep
3.12, and on a probe run on 2026-11-22.

<details>
<summary>The manual's words and the probe output</summary>

The manual page says:

- `-F`: "Interpret PATTERNS as fixed strings, not regular expressions."
- `-i`: "Ignore case distinctions in patterns and input data, so that characters that differ only in case
  match each other."
- `-e PATTERNS`: "Use PATTERNS as the patterns." The page adds that the option "can be used to protect a
  pattern" that begins with a hyphen.
- Exit status: "Normally the exit status is 0 if a line is selected, 1 if no lines were selected, and 2 if an
  error occurred."

The probes ran against a file `$f` holding four notes: `Buy rope`, `call Ann at 3.30`, `pass -i to grep`, and
`coil the ROPE`.

| Probe | Output | Status |
| --- | --- | --- |
| `grep -i -F -e rope -- "$f"` | `Buy rope` and `coil the ROPE` | 0 |
| `grep -i -F -e . -- "$f"` | `call Ann at 3.30` | 0 |
| `grep -i -F -e r.pe -- "$f"` | Nothing | 1 |
| `grep -i -F -e -i -- "$f"` | `pass -i to grep` | 0 |
| `grep -i -F -i "$f" </dev/null`, with no `-e` | Nothing: `-i` is taken as an option and the path as the word | 1 |
| `grep -i -F -e zebra -- "$f"` | Nothing | 1 |
| `grep -i -F -e '' -- "$f"` | All four notes | 0 |
| `grep -i -F -e rope -- "$f.nope"` | `grep:`, the path, then `No such file or directory` | 2 |
| `printf 'ÉCOLE\n' \| grep -i -F -e école`, in `en_US.UTF-8` | `ÉCOLE` | 0 |

The usage line parses the way `test_completions_match` needs:

```bash
echo 'usage: notes add <text> | notes list | notes search <word>' | grep -o 'notes [a-z]*' | cut -d' ' -f2
```

```text
add
list
search
```

</details>

The guide asks for each assumption that more than one task rests on. The work is one task, so it has none.

## Files

The file list comes from four searches of the tracked files, each run as `git grep -n` with `brief.md` left
out.

| Search | Hits | What each hit means |
| --- | --- | --- |
| `-e 'notes add' -e 'notes list'` | 5 | `bin/notes:7` is the usage line and changes. `tests/run.sh:7` and `:14` are today's tests and stay. `README.md:3` and `:4` describe `add` and `list` and stay. |
| `-w -e 'add list'` | 1 | `completions/notes.bash:2` is the list of commands the shell offers. It changes. |
| `-i -e usage` | 2 | `bin/notes:7` again. `tests/run.sh:10` is the comment on `test_completions_match` and stays. |
| `-e search` | 0 | Nothing in the repo names the new command yet. |

`scripts/gate.sh` runs `tests/run.sh` and names no command, so it stays.

The task changes these three files:

- `bin/notes` gets the `search` branch and the longer usage line.
- `tests/run.sh` gets four new tests, and their names join the `for t in` line.
- `completions/notes.bash` gets the word `search`.

`tests/run.sh` opens with the comment "Runs every test_* function", but its loop names each test. A new test
that isn't added to that line never runs, and the gate still passes. The task leaves the comment as it is
and names it in the pull request, so that item 10 of the goal holds.

## The task: add the search command

This is the only task, so it waits for nothing and no merge order applies.

| | |
| --- | --- |
| Task name | `notes-search` |
| Model and effort | `sonnet` at `medium`, because the change is a few lines whose behavior this spec fixes |
| Reviewer | `standards:diff-reviewer`. The work touches no sign-in or data path and renders no UI. |
| Minutes | 30 planned, so the goal's time clause is `or stop after 60 minutes` |

The session launches by the skill's section "Launching a task" and ends by its sections "Gates and review" and
"The pull request". The pull request's body follows `~/.claude/docs/voice/written-for-people.md`.

### The four new tests

Each test makes a notes file with `mktemp`, as today's tests do.

- `test_search_ignores_case` adds `Buy rope`, `call Ann`, and `coil the ROPE`, then checks that `search rope`
  prints the first and third in that order and exits 0.
- `test_search_plain_text` checks that `search .` prints only a note that holds a period, that `search r.pe`
  finds nothing in a file that holds `rope`, and that `search -i` prints only a note that holds `-i`.
- `test_search_no_match` checks that a search with no match prints nothing on either stream and exits 1, and
  that the same holds when the notes file doesn't exist.
- `test_search_missing_word` checks that `search` and `search ''` each exit 2, print nothing on standard
  output, and print the new usage line on standard error.

### The goal

The task is done when every item below holds on the branch's last commit. Each item names its command. Items
1 to 5 use this notes file:

```bash
f=$(mktemp)
printf '%s\n' 'Buy rope' 'call Ann at 3.30' 'pass -i to grep' 'coil the ROPE' > "$f"
```

Each command ran on today's code on 2026-11-22. Where an item says "today", that is the output it gave. The
gate ran twice with the same output.

1. **Search finds notes without regard to case, oldest first.**
   `NOTES_FILE=$f bin/notes search rope; echo "exit $?"` prints `Buy rope`, then `coil the ROPE`, then
   `exit 0`. Today it prints `usage: notes add <text> | notes list` and `exit 2`.
2. **The word is plain text.** `NOTES_FILE=$f bin/notes search .; echo "exit $?"` prints `call Ann at 3.30`
   and `exit 0`. With `r.pe` as the word, the same command prints only `exit 1`. With `-i` as the word, it
   prints `pass -i to grep` and `exit 0`. Today all three print the old usage line and `exit 2`.
3. **Words after the first join into one text.** `NOTES_FILE=$f bin/notes search the rope; echo "exit $?"`
   prints `coil the ROPE` and `exit 0`. Today it prints the old usage line and `exit 2`.
4. **No match prints nothing and exits 1.** `NOTES_FILE=$f bin/notes search zebra 2>&1; echo "exit $?"` prints
   only `exit 1`. Today it prints the old usage line and `exit 2`.
5. **No notes file prints nothing and exits 1.** `NOTES_FILE=$f.none bin/notes search rope 2>&1; echo "exit $?"`
   prints only `exit 1`. Today it prints the old usage line and `exit 2`.
6. **A missing word exits 2 with the usage line.** `bin/notes search 2>&1 >/dev/null; echo "exit $?"` prints
   `usage: notes add <text> | notes list | notes search <word>` and `exit 2`, and so does the same command
   with `''` as the word. `bin/notes search 2>/dev/null | wc -c` prints `0`. Today the status is already 2 and
   the count is already 0, but the line printed is the old one, which doesn't name `search`.
7. **The shell offers the command.** This prints `[search]`, and today it prints `[]`:

   ```bash
   bash -c 'source completions/notes.bash; COMP_WORDS=(notes s); COMP_CWORD=1; _notes; echo "[${COMPREPLY[*]}]"'
   ```

8. **The gate passes and runs the new tests.** `bash scripts/gate.sh; echo "exit $?"` prints one `ok` line for
   each of `test_add_then_list`, `test_list_empty`, `test_completions_match`, and the four new tests, prints
   no `FAIL` line, and ends with `exit 0`. `bash scripts/gate.sh | grep -c '^ok   test_search_'` prints `4`.
   Today the gate prints the three `ok` lines and `exit 0`, and the count is `0`.
9. **The branch changes only the three files.** `git diff --name-only origin/main...HEAD` prints
   `bin/notes`, `completions/notes.bash`, and `tests/run.sh`, and nothing else. Today it fails with
   `fatal: ambiguous argument 'origin/main...HEAD'`, because the repo has no remote.
10. **The three tests that pass today are unchanged.** `git diff origin/main...HEAD -- tests/run.sh | grep '^-[^-]'`
    prints one line, the old `for t in` line, because that is the only line of the file the task removes or
    rewrites. It can't run today, for the same reason as item 9.
11. **The pull request is ready.** It is marked ready, its body lists items 1 to 10 word for word, each with the
    output of its command, and it carries an accept verdict from `standards:diff-reviewer` on the last commit.

## Before launch

The start conditions were tested on 2026-11-22 on pavilion.

| Condition | Result today |
| --- | --- |
| The checkout is free | `claude-worktree-busy "$PWD"` exits 0. |
| Fewer than four sessions are working | `claude agents --json` prints `[]`. |
| Secrets | The task needs none. |
| CI | The repo has no workflow, so the gate is the only check and the task waits on no CI run. |
| A remote | The repo has none. `git remote -v` prints nothing, and `gh repo view` prints `no git remotes found`. |
| The spec is on the default branch | It isn't. `spec.md` is written but not committed. |

Two of these stop a launch today, and both are for the session Geoff is talking to:

- **The repo needs a remote.** The task's worktree starts from the remote's default branch, and the work ends
  in a pull request. Where the repo lives, and whether it is public, is Geoff's choice. Items 9 and 10 of the goal
  name the remote `origin` and its default branch `main`, so the remote takes those names.
- **`spec.md` needs to be on the remote's default branch.** A worktree that starts there holds only what was
  pushed, and the goal names the spec by its path.

The repo has no `docs/STATUS.md` and no other session works in it, so nothing else needs reading.

## The task's commands and the denials log

`~/.local/state/claude-denials.jsonl` holds 149 refusals. Its first line is dated 2026-11-01, so it covers 22
days. The commands the task runs were searched in it.

| Command | Refusals | What they were |
| --- | --- | --- |
| `bash scripts/gate.sh`, `bin/notes`, `tests/run.sh` | 0 | |
| `gh pr create`, `gh pr ready` | 0 | |
| `git push` | 4 | One deleted a remote branch. Three pushed `HEAD:main`. None pushed the branch its task created. |
| `git commit` | 5 | One carried `--no-verify`. One changed `CLAUDE.md`. One was chained to a push to `main`. One was chained to commands that looked for running processes. One came while the classifier was down. |

None of these is a command this task runs. It pushes only the branch it creates and commits with no bypass flag.

## Backlog sweep

The scoped sweep of `standards:backlog-sweep` has nothing to read. The repo has no `BACKLOG.md` and no
`.claude/project-tracking.json`, so there are no items, no verdicts, and no backlog edits to approve.

## Calls Claude made

Each of these is already in the spec. Geoff can strike any one before he approves.

1. **The task changes `completions/notes.bash`.** The brief names two files. The gate can't pass without the
   third. This is the one place the spec differs from the brief.
2. **`README.md` stays as it is.** It describes `add` and `list`, and a line for `search` would belong there.
   The brief names the files and the gate doesn't force this one, so the spec leaves it out. Adding the line
   later is one sentence and can land directly.
3. **"Contains the word" means the word appears anywhere in the note.** `rope` finds `ropes`. The other
   reading, whole words only, would need a flag the brief rules out by calling the word plain text.
4. **Words after the first join with one space**, as they do for `add`. The other option was to exit 2 on a
   second word. Reversing this changes one line and one test.
5. **An empty word counts as a missing word.** Otherwise `search ''` would print every note.
6. **A missing notes file counts as no match**, exit 1, with nothing printed.
7. **The usage line's new wording**, given under "How search behaves". The completion test reads command names out of it.
8. **The four test names**, so the gate's count of new tests can fail.
9. **`sonnet` at `medium` builds the task.**
10. **The task is planned at 30 minutes, and that figure is not measured.** `task-report` couldn't run: the
    sandbox refused its call to `api.github.com`. Its cache holds seven scored pull requests whose measured
    minutes run from 11 to 155, and nothing there says which of them are like this one. The session that
    launches the task runs `task-report` first and changes the minutes if the like tasks say otherwise.
11. **A word made only of spaces is searched as a space.** The other option was to count it as missing.
12. **The comment at the top of `tests/run.sh` stays**, though it is wrong. Fixing it is outside the brief.

## What the fresh reader asked

One reader with no context read this spec against the repo on 2026-11-22, as the session that would build
it. It found no statement that the repo or the brief contradicts. It also built the feature in a scratch copy
with a local remote, outside this repo, and reports that items 1 to 10 of the goal each printed what the item
says. This session didn't see that output.

Answered already in the spec:

- Part of item 6 passes today. The item says so, and it still fails today on the usage line.
- The spec names no `gh` command for the task. It points at the skill's sections, which hold them.

Minor calls, made and marked:

- A word made only of spaces: call 11.
- Whether to fix the wrong comment in `tests/run.sh`: call 12.
- Items 9 and 10 assume a remote named `origin` with `main` as its default branch. "Before launch" now says so.
- The probe with no `-e` read the path as the word. Its row now says so.
- Item 6 doesn't use the notes file, and item 11 asked for the output of a command it doesn't have. Both
  are fixed.

For Geoff only:

- Where the repo's remote lives, and whether it is public.
- Whether 30 unmeasured minutes is enough. Items 9 and 10 have never failed for the reason the task fixes,
  because they can't run until the remote exists.
