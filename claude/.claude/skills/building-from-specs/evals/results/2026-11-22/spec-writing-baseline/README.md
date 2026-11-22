# Spec-writing baseline of 2026-11-22

This folder holds one full run of the `spec-writing` suite, made with the guide as it stood before
any change: `references/writing-a-spec.md` at blob `e85af74`. Each case has two files. The JSON
file is the evidence: how the session ended, its models, its cost, each tool call, each refused
call, and each check with the judge's quote. The Markdown file is the spec a writing session wrote,
or the report a reader returned. `probe.json` is the sandbox probe that ran first. The raw streams
stayed in the run's scratch folder and aren't kept here.

The run was made with this command, two sessions at a time:

```bash
python3 -I $E/run_evals.py --suite spec-writing --run \
  --out $E/results/2026-11-22/spec-writing-baseline --jobs 2 --max-total-usd 38.27
```

## Result

All 16 sessions finished, on `claude-fable-5-2` at `high`, with the sandbox on. Every trap check
passed. Every writing case failed the length check, and every other check passed.

| Case | Trap | Length (words) | Nothing built | Guide read | Seconds | Cost |
| --- | --- | --- | --- | --- | --- | --- |
| `write-missing-file` | pass | fail (4,084) | pass | pass | 482 | $3.85 |
| `write-gate-red` | pass | fail (4,285) | pass | pass | 674 | $4.86 |
| `write-unlanded-work` | pass | fail (3,671) | pass | pass | 522 | $4.00 |
| `write-check-passes-today` | pass | fail (3,824) | pass | pass | 496 | $3.83 |
| `write-uncovered-edge` | pass | fail (3,903) | pass | pass | 686 | $5.03 |
| `write-two-sources` | pass | fail (4,213) | pass | pass | 780 | $4.83 |
| `read-false-fact` | pass | - | - | - | 78 | $0.80 |
| `read-check-passes-today` | pass | - | - | - | 73 | $0.75 |
| `read-wrong-path` | pass | - | - | - | 58 | $0.69 |
| `read-prints-nothing` | pass | - | - | - | 84 | $0.82 |
| `read-missing-file` | pass | - | - | - | 84 | $0.82 |
| `read-vendored-file` | pass | - | - | - | 70 | $0.69 |
| `read-false-count` | pass | - | - | - | 99 | $0.89 |
| `read-two-parts` | pass | - | - | - | 69 | $0.74 |
| `read-unlanded-work` | pass | - | - | - | 75 | $0.74 |
| `read-uncovered-edge` | pass | - | - | - | 86 | $0.83 |

The run cost $34.24, judges and probe included. The limit for one spec is 1,200 words, and the six
specs ran from 3,671 to 4,285. Each writing session dispatched one fresh reader through Agent
before it finished, as the guide asks.

## What the sessions could not reach

Five of the six writing sessions reached for `~/.claude/docs/voice/written-for-people.md`, which
`building-from-specs` names as the standard for a pull request's body. Three tried to read it,
and two tried to list its folder. The file links into `~/.dotfiles`, which the test hides so that
no session reads the installed skill or the main checkout. The sessions went on without it. A
spec's length doesn't rest on that file, since the guide, which the sessions did read, governs
what a spec carries.

The writing sessions had nine refused calls in all, each in its case's `permissionDenials`.
Eight were those reads and listings. The ninth, in `write-gate-red`, was a Bash call that tried
out a change to `bin/notes` in a copy under `$TMPDIR`. The reader sessions had no refused calls.

## Reading a row again

`python3 -I $E/run_evals.py --summary $E/results/2026-11-22/spec-writing-baseline` prints the
table from the evidence files. It exits 1 once the runner, a case, or a fixture changes, because
the run's hash no longer matches the tree.
