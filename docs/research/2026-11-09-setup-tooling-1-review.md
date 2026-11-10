# Pass 1 whole-branch review: the clean room

Pass 1 of the cairn-setup setup-tooling run (`setup-tooling-1`, class `runner`), glw907/workstation#215.
Two `standards:diff-reviewer` reads, both Opus at medium: the whole branch at `03ced07`, then
the fix commit `a50073d`.

## Read 1: whole branch at 03ced07. Verdict: fix

The reviewer found the credential handling, the settings template's invariants, the removal
guards, the verdict order, and the docs sound. It found four blocking defects.

| # | Finding | Resolution in a50073d |
| --- | --- | --- |
| 1 | The probe's masked-path grader took any "No such file" containing a "/" as masking. `known` came from every item and matched by substring, so `file://$PWD` produced "/" and `/tmp` matched inside `/var/tmp/...`. The ninth probe's record already showed it (`ls /var/tmp/cleanroom/probe/run` passed on "/tmp"). | Evidence comes only from denied items, a path needs a real segment, and a path matches as a whole token. A unit test grades the shipped list. The tenth run is the one the record rests on. |
| 2 | `watch` wrote `state.json` outside its try block, so a failed write left the session running with no cap. | The whole tick is inside the try, the ledger row is written before `state.json`, and `end_run` and `stop` end the sessions in a `finally`. A live test makes `state.json` a directory. |
| 3 | The `cleanroom` user can write the room's directories (ACL rwx), and `write_atomic` used a guessable temp name. It could plant a link, or swap `run/` for one, and glw907's write would land in a file of Geoff's. | `mkstemp` temp files, sticky room and run directories, and `trusted_dir` before each write glw907 makes there. |
| 4 | A host without the `cleanroom` user quietly ran everything as glw907, and the probe's user check still passed. | A missing user is a refusal. Only `CLEANROOM_USER=` asks for in-process mode, and `@USER@` is the configured user. |

Non-blocking items fixed: `stop` kills the sessions in a `finally`; the watcher stops the run after
a normal exit; the transcript mirror joins every transcript and drops a torn last line; the readers
skip an unparsable line; the drift pairs and their doc are pavilion only; the list's prose states
the masking rule. Items filed as backlog #53: the sudoers wildcard, the env-name denylist, the
untraced cost gap, and the duplicated sudo argument lists.

Out of scope, noted: `bluefin/etc/sudoers.d/cleanroom`'s wildcard lets glw907 run any script under
`~/.dotfiles` as `cleanroom`. That adds no privilege, and the file is Geoff's pre-flight item 6.

## Read 2: fix commit a50073d. Verdict: accept

All four blocking findings are fixed and none of the fixes adds a defect that blocks. The reviewer
ran the three cleanroom test files (43 and 18 passed, the real-user test included) and checked
that the sticky bit leaves every legitimate write alone: the clean user replaces only files it
owns, glw907 owns both sticky directories and can still remove them, and the ACL mask stays rwx.

Notes, all fail-closed and filed in #53: a failed write at a cost stop makes the watcher's `except`
call `end_run` a second time and overwrite the ledger cause; `trusted_dir` does not check the
sticky bit, so a room built before the fixes needs `init --fresh`; `CLEANROOM_USER` is not in
`--preserve-env`; `probes.jsonl` does not record whether a probe ran isolated.

## Challenge to the probe's departures

The first reviewer read each departure in the probe record and found two sound (the python dev
server, the new scratch repository) and two acceptable with a flag: the process count stands in
for the `/proc/*/environ` scan on a proxy (under eight visible processes) and never reads an
environ, and the cost caps are only as honest as the agent, which can rewrite its transcript and
`statusline.json`. Both are asks in packet B.
