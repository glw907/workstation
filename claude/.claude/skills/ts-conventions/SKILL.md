---
name: ts-conventions
description: >
  Mandatory rules for writing TypeScript comments on this workstation.
  Use before writing, reviewing, or modifying any TypeScript doc comment
  or inline comment. Covers the write-time comment-or-not gate, the TSDoc
  doc-comment shape (document the contract, never the type), the copy-in
  ESLint jsdoc/tsdoc flat config, and the standard's principles and
  exemplars.
---

# TypeScript Comment Conventions

Comments follow **TSDoc** (https://tsdoc.org). The reader is a coder or an agent already
looking at the code. A comment carries what the code cannot: a why, a constraint, a piece of
evidence. The type annotation already states the type, so a doc comment that restates it is
noise. The linter is **ESLint with the jsdoc and tsdoc plugins**; the exemplar is **well-regarded
TypeScript libraries** (the TypeScript compiler, VS Code, and the SvelteKit and Svelte sources
are all strong). This skill is the TypeScript arm of the authoring charter
(`~/.claude/docs/authoring-charter.md`).

## Principles

- **Comment the why, not the what.** The code and the type say what. A comment earns its place
  when it carries a reason, a constraint, or a piece of evidence the code cannot.
- **Document the contract.** A doc comment states what a caller must know: the invariant, the
  unit, the nil-semantic, the ordering requirement. Never the type the signature already carries.
- **Do not paraphrase the code.** If removing the comment leaves a competent reader no worse off,
  the comment should not exist.

When a comment's shape is in doubt, read how a well-run TypeScript library documents the same
kind of API and match it.

## §0: Comment-or-not (write-time gate)

Before writing any comment, run the three-question gate:

```
(a) Does the name plus the typed signature already say this?
(b) Is the why obvious from the next 5 lines or fewer?
(c) Would a reader otherwise miss a hidden constraint, invariant, side
    effect, or surprising consequence?
```

Skip on (a) or (b). Write only for (c). Mechanical test: if the comment paraphrases the next
few lines or restates a fact the type annotation already carries, delete it. The paraphrase
test is the primary filter against a machine-shaped comment.

A doc comment on an exported symbol is the one presence default, and even then only when the
name plus signature leaves the contract unobvious. Internal helpers are opt-in: a one-line
private helper gets a `//` at most, and most get nothing.

## Decision rubric

```
1. Exported symbol whose contract is fully implied by name + signature?
   YES → no doc, or one sentence if a caller obligation hides in it.
   NO  → one sentence stating the constraint, unit, nil-semantic, or
         caller obligation the type cannot express. No type restatement.

2. Internal symbol with unobvious behavior the name does not convey?
   YES → short // line.   NO → no comment.

3. Inside a function: does this block differ from what the name and
   control flow imply?
   YES → one-line why-comment with evidence (issue URL, spec, symptom).
   NO  → no comment.

4. A suppression (@ts-expect-error, eslint-disable)?
   YES → carry the reason inline, unless the line above already argues it.
```

## TSDoc doc-comment shape

- TSDoc, not JSDoc. No `{type}` on any tag. The signature carries the types; the doc carries
  the why.
- Document the contract: the constraint, the unit, the nil-semantic, the caller obligation.
  Not the type, not the parameter list in English.
- Use the real tags for structured notes: `@remarks`, `@throws`, `@defaultValue`, `@param name -
  description`. Never invent `Note:` or `Important:` label-colon paragraphs.
- Public API gets full sentences with periods and links to MDN or the spec where they help.
  Internal helpers get a terse fragment, no period.
- Vary the opener across a file. Never lead every doc with "This function".
- One thought per comment.

## Linting: the copy-in ESLint flat config

A consumer repo copies `~/Projects/cairn-cms/eslint.config.js` in as its `eslint.config.js`
(cairn is the first consumer; that file is the single source, so a copy here would drift). It
lints `src/lib/**/*.ts` on the jsdoc typescript-error base plus tsdoc, carries the
`house/no-em-dash-in-comments` rule, and has a `.svelte` block. Adjust the `files` globs to the
repo's source root.

The base preset enforces the canonical expanded doc-block shape (`jsdoc/multiline-blocks`,
`jsdoc/tag-lines`), the form a well-run TypeScript codebase uses. A repo whose comments predate
the standard runs `eslint src/lib --fix` once to reformat to it, then hand-fixes the residue
`--fix` cannot: scoped package names go in backticks (`` `@codemirror/view` ``, not a bare
`@codemirror/view` that TSDoc reads as a tag), brace and angle spans in prose go in backticks,
and a `@param` gets its hyphen.

The parser is `typescript-eslint`'s with no `project` setting: the jsdoc and tsdoc rules read
the comment AST, not the type graph, so type-aware linting is not needed and the run stays
fast.

## Note on coverage-gated repos

ESLint and a TSDoc-syntax gate own the mechanical standard; they cannot see whether a comment
is worth its space. Where a repo also enforces export-doc coverage (a `check:reference`-style
gate plus `jsdoc/require-jsdoc` with `publicOnly`), every exported symbol keeps a minimal
one-line doc by design, so a terse doc on a self-evident export is correct there, not a
redundancy to delete. Spend the judgment on internal helpers and on prose quality: the
paraphrase, the type narrated in English, the uniform comment rhythm across a file. These are
what the linter cannot catch and the exemplars teach.

## Output

When writing, run the §0 gate first, then the rubric, then write only what survives. When
reviewing, cite each finding at `file:line` with the principle it breaks and, where it helps,
the well-run-library comment it should resemble.
