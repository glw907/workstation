# Spec-writing final runs of 2026-11-22

This folder holds task 2's evidence: the two rounds that tried a guide change, and the final pair of
runs. Each case has two files. The JSON file records how the session ended, its models, its cost,
each tool call, each refused call, and each check with the judge's answer. The Markdown file is the
spec a writing session wrote, or the report a reader returned. `probe.json` is the sandbox probe
that ran first.

| Folder | Guide blob | Cases | Cost |
| --- | --- | --- | --- |
| `round-1/` | `7747200`, the spec's length rule word for word | the six writing cases | $25.47 |
| `round-2/` | `341b4f1`, the first rewording | the six writing cases | $22.36 |
| `run-1/` | `3a6fd5d`, the second rewording | all 16 | $31.40 |
| `run-2/` | `3a6fd5d` | all 16 | $30.04, plus $0.83 for one rerun |
| `judge-error/` | `3a6fd5d` | the first `read-wrong-path` attempt in `run-2` | in `run-2` |

The task's sessions cost $110.10 of the $130 cap. Every session ran on `claude-fable-5-2` at
`high`, with the sandbox on, and ended `finished`.

## The rounds

The baseline's six length checks failed at 3,671 to 4,285 words against a mark of 1,200. Every
other check passed. Round 1 ran the writing cases on the spec's length rule, and round 2 and the
final pair each ran on a rewording. Each change is its own commit, which names the checks that
called for it.

| Case | Baseline | Round 1 | Round 2 | Run 1 | Run 2 |
| --- | --- | --- | --- | --- | --- |
| `write-missing-file` | 4,084 | 3,636 | 2,154 | 1,979 | 1,948 |
| `write-gate-red` | 4,285 | 2,814 | 2,047 | 1,950 | 2,199 |
| `write-unlanded-work` | 3,671 | 3,159 | 2,695 | 1,782 | 2,128 |
| `write-check-passes-today` | 3,824 | 2,729 | 2,240 | 1,762 | 1,719 |
| `write-uncovered-edge` | 3,903 | 3,157 | 1,915 | 1,809 | 1,944 |
| `write-two-sources` | 4,213 | 3,337 | 2,266 | 2,110 | 1,891 |

Every length check still failed. Every trap, nothing-built, and guide-read check passed in every
round and run.

## The final pair

| Case | Run 1 | Run 2 |
| --- | --- | --- |
| `write-missing-file` | trap pass, length fail | trap pass, length fail |
| `write-gate-red` | trap pass, length fail | trap pass, length fail |
| `write-unlanded-work` | trap pass, length fail | trap pass, length fail |
| `write-check-passes-today` | trap pass, length fail | trap pass, length fail |
| `write-uncovered-edge` | trap pass, length fail | trap pass, length fail |
| `write-two-sources` | trap pass, length fail | trap pass, length fail |
| `read-false-fact` | pass | pass |
| `read-check-passes-today` | pass | pass |
| `read-wrong-path` | pass | pass, on its rerun |
| `read-prints-nothing` | pass | pass |
| `read-missing-file` | pass | fail |
| `read-vendored-file` | pass | pass |
| `read-false-count` | pass | pass |
| `read-two-parts` | pass | pass |
| `read-unlanded-work` | pass | pass |
| `read-uncovered-edge` | fail | fail |

Three reader checks failed, each with a judge answer of `no` and no error, and none failed in the
baseline:

- `run-1/read-uncovered-edge` and `run-2/read-uncovered-edge` name a missing notes file only as a
  gap in the tests, never as a behavior the spec leaves unsaid.
- `run-2/read-missing-file` asks whether the task may change `completions/notes.bash`, which the
  file list leaves out, and the trap's pattern matched. The judge still answered `no`.

The first `run-2/read-wrong-path` attempt is a judge error. The reader's last message was a note
about a stuck probe in place of its report, so the judge's `answer` is null. That attempt is in
`judge-error/`, and its rerun in `run-2/` passed.

## Reading a row again

`python3 -I $E/run_evals.py --summary $F/run-1 $F/run-2` prints both runs from the evidence files.
With `--require-pass` it exits 1 while a check fails.
