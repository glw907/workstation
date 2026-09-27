# Pass <n>: <topic>

> **For agentic workers:** Execute per the `site-pass` and `pass-core` skills: each task
> runs as the chain (`site-implementer`, then `diff-reviewer`, then the gate); the conductor
> never reads the diff. Tasks state outcomes and acceptance criteria, never implementation code.

**Pass class:** one of `auth-data`, `engine-logic`, `paint`, `sweep`, `docs`, `tool` (see
`pass-core`). A task that differs carries its own `Pass class:` line.

**Token ceiling:** <n>. **Checkpoint interval:** four tasks.

**Goal:** One sentence stating what this pass produces.

**Engine consultation:** link to the filed brief
(`cairn-cms/docs/internal/consultations/YYYY-MM-DD-<site>-<pass>.md`), or
the one line "no engine asks". Required; see the `engine-consult` skill.

**Architecture:** What this pass delivers, including files created/modified
and key decisions locked in.

**Tech Stack:** SvelteKit, TypeScript, Tailwind CSS v4, DaisyUI v5,
mdsvex. Note any new deps.

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `src/...` | Create/Modify | ... |

---

## Task N: <component>

**Files:**
- Create/Modify: `exact/path/to/file`

**Outcome:** what is true when this task is done.

**Acceptance criteria:**
- [ ] ...

---

## Pass-end checklist

- [ ] `code-simplifier` once, only if TS or Svelte changed (see `pass-core` for the class rule)
- [ ] Quality gate: `npm run check` (0/0), `npm test` (exit 0), `npm run build`
- [ ] Review gate: the reviewers the pass class and touched files call for
- [ ] Update `docs/architecture.md`
- [ ] Update `docs/STATUS.md` (present tense, next resume prompt) and `docs/HISTORY.md`
- [ ] Archive plan: `git mv docs/superpowers/plans/<this>.md docs/superpowers/archive/plans/`
- [ ] Archive spec (if one exists): `git mv docs/superpowers/specs/<this>-design.md docs/superpowers/archive/specs/`
- [ ] Commit and push, then hand off with the resume prompt (the next plan is brainstormed in a fresh session)
