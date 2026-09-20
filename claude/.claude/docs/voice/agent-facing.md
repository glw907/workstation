# Register: agent-facing instructions

The reader is Claude or another model: a CLAUDE.md, a skill, an agent definition, a hook
message. Applies to every file whose audience is a model executing a task, not a human reading
prose.

The standard is **Anthropic's Claude Code and prompt-engineering best practices**
(https://code.claude.com/docs/en/best-practices and
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview). There is no
deterministic linter; the standard is guidance plus Anthropic's own published examples. This
register is the agent-facing arm of the authoring charter
(`~/.claude/docs/authoring-charter.md`).

The best-practices page's own lead practice: give an agent a check it can run, tests, a build,
a screenshot to compare, rather than leaving it to stop when the work merely "looks done."

## What the standard asks for

- Be clear and direct. State the instruction explicitly. A model follows a precise directive
  far better than an implied one, so spell out what to do rather than hinting at it.
- Give the reason with the rule. Anthropic's guidance is that explaining why a constraint
  matters makes a model apply it more reliably and generalize it to new cases.
- State what done looks like in concrete, checkable terms: exit codes, counts, the exact
  command to run, the artifact to produce. Avoid adjectives like "thorough" or "robust".
- Make the rule testable. Convert a judgment call into a mechanical check the model can run.
- Use examples. Anthropic's strongest single lever is a worked example of the wanted behavior;
  show the shape of a correct result, and where it helps, a contrasting wrong one.
- Name the trap and its mechanism. A known failure mode, stated with the bug it causes, is more
  durable than a vague caution.
- Keep it short. Every retained sentence must change behavior; cut anything a competent agent
  would do anyway. Length dilutes the instructions that matter.
- State only facts you were given or verified. An instruction that names a command, path, or
  behavior the repo does not have sends the agent confidently down a wrong path, and the
  agent cannot tell the invented detail from the real ones. Omit what you do not know.

## Exemplars

Each passage is written as agent-facing instruction in the Claude Code best-practice style. The
one-line note says which practice it shows.

A verification contract: states the done condition in exit-code terms and names the likely
shortcut to forbid (be explicit; define done concretely):

```
A passing targeted test is not the gate. The browser test can pass while type-checking fails,
because esbuild does not type-check, and the full run can still exit non-zero on an unhandled
rejection. Before you report done, all three must hold: the targeted test passes, the
type-check is clean, and the full suite exits 0. Paste the evidence. If you cannot satisfy all
three, report blocked with the failing output rather than committing a red gate.
```

A judgment call turned into a mechanical test, with the default named (make the rule testable;
state the reason):

```
Mechanical test: if a comment paraphrases the next five lines or fewer, delete it. The code
already states what it does, so a paraphrase comment adds nothing and ages badly. Comment only
when the name and signature leave something a competent reader would not already know. Silence
is the default.
```

An example-driven instruction: shows the wanted shape directly (use examples to set the
format):

```
Write the commit subject in the imperative mood, under 50 characters, with no trailing period.
For example: "Add retry to the upload handler" or "Fix off-by-one in the date parser". Do not
write "Added retry..." or "This commit fixes...".
```

A load-bearing rule that carries its evidence, the mechanism then the fix (name the trap and
its mechanism):

```
Put the theme attribute on a bare wrapper, never on an element that also has styled classes.
Every scoped rule is a descendant selector, so a class on the themed element itself never
matches. Wrap the styled layout one level in. Skipping this broke the drawer and both auth
pages in shipped builds.
```

A rule with its reason in the same breath, no hedging (be clear and direct; give the why):

```
When a pass adds a diagnosable code path, give it a named log event rather than a bare console
call, and update the reference table in the same pass. The logger is internal and its API is
free to grow, but the event names are the public contract, so they must stay in sync with the
docs.
```

## The docs-register measures

For a file in a repo that has opted in, `tellgrader` reports two cadence measures,
`hinged_pair_share` and `short_sentence_share`, whose definitions live in
`~/.claude/skills/writing-voice/evals/tellgrader/MEASURES.md`.

The measures are report-only. They carry no band and gate nothing, and the hinged-pair
definition is unsettled; no number here is a threshold. The corpus for this audience is
held by the consuming repo and reaches a review through the dispatching brief. No file in
this directory names a cairn corpus entry id.

## Off-voice contrast

The same content in the register this file exists to prevent (hedging, warmth, process
narration, no concrete done condition):

```
It's important to remember that testing is a crucial part of the workflow! Before reporting
that you're done, you'll want to make sure all the various checks pass. Generally speaking,
it's a good idea to run the full suite, as this helps ensure everything works as expected.
```
