# writing-voice eval corpus

This directory holds the standing benchmark for the workstation voice system. It measures
whether drafting with the `writing-voice` skill (and the register files it routes to)
produces better prose than drafting bare, on the same model and the same tasks.

## Layout

- `evals.json`: twelve drafting tasks, one per register the router names, each with its
  register, its external standard, and four judge-gradeable assertions.
- `tellgrader/`: a Go CLI that scans a draft for the deterministic tells (contrast frames,
  connector openers, em-dash misuse, slop lexicon, scaffold headers, bold-lead bullets,
  flat cadence, trailing-hinge runs) and reports JSON. A trailing-hinge run under the
  docs-register profile gates: the CLI exits 2 (`tellgrader/MEASURES.md`). `make -C
  tellgrader check` is its gate.
- `results/`: one dated directory per benchmark run holding `benchmark.json`,
  `benchmark.md`, and analyst notes. This is the trend line; compare across dates.
- `research/`: the external evidence base behind the grader's checks and lexicon
  (published tell taxonomies, excess-vocabulary ratios, judge-bias numbers), with the
  license-clean source wordlists under `research/data/`.

## How a run works

Each eval runs twice on the same model: a with-skill arm that reads
`writing-voice/SKILL.md` and the register file it routes to before drafting, and a bare
baseline told to draft directly. Three grading layers score every draft:

1. **Tell scan.** `tellgrader --register <name> draft.md`. Register mapping:
   `docs` for the two technical-doc dialects, `editor`, `commit`, `reply`, `agent`, and
   `comments` for the three code-comment evals (the grader extracts comment text from
   `.go`, `.ts`, and `.py` files).
2. **Assertions and rubric.** A fresh-context judge reads the register file and grades the
   four assertions per draft, plus a 1-5 rubric: register fidelity, clarity, structure,
   factual fidelity.
3. **Blind preference.** The same judge sees the two drafts as anonymous A and B (which
   arm is A alternates by eval to cancel position bias) and picks the better piece of
   writing for the audience. Since iteration 3 the judge carries an explicit priority:
   factual fidelity outweighs polish, so a draft that invents facts loses to one that
   does not unless it is otherwise unusable, and deriving an obvious specific from a
   stated fact (a flag name from a named setting) counts as interpolation, not invention.

The primary trend metric is tells per 1000 words from layer 1. The quality verdict is the
blind win rate from layer 3.

## Rerunning

Drive it from a Claude Code session: spawn one subagent per eval per arm with the prompts
in `evals.json` (the baseline arm must not read any skill or register file), run
`tellgrader` over the outputs, dispatch judges, and aggregate with the skill-creator
plugin's `scripts.aggregate_benchmark`. The first run's working layout is the reference:
`writing-voice-workspace/iteration-1/<eval>/{with_skill,without_skill}/outputs/`.
