# Code-comment standards: per-language, three layers

Status: SUPERSEDED 2026-06-22 by `2026-06-22-authoring-standards-design.md` (the external-standards
redesign). Kept as history; it describes the earlier per-language tell-catalogue design.
Owner: Geoff.
Scope: workstation-wide. This is one arm of the authoring charter
(`~/.claude/docs/authoring-charter.md`), the code-comment audiences. The prose and content audiences
are the other arm, designed in `2026-06-22-ai-drafting-prose-system-design.md`.

## What this is

Code comments are an audience like any other under the charter. A coder or an agent already looking
at the code is the reader, and a comment exists to carry what the code cannot: a why, a constraint, a
piece of evidence. Each language gets the charter's three layers, with the language's own tools in
each slot. Go already proves the shape; this spec brings TypeScript, Svelte, and Python to the same
bar.

The three layers, applied to comments:

1. A structure linter, native to the language. It checks presence, doc-comment syntax,
   type-restatement, parameter-name drift, punctuation, and mood. This is golangci-lint with `godot`
   and `revive` for Go, and the per-language equivalents below.
2. Vale on the comment prose. Given a code format, Vale extracts only the comment text and lints it
   as prose, ignoring the code around it. This is the deterministic home for the em-dash ban and the
   banned-word and marketing lexicon inside comments. It is where the retired `prose-guard` comment
   tier lands.
3. Claude judgment. A per-language AI-tell catalogue and a write-time comment-or-not gate, carried by
   a `<lang>-conventions` skill and a `/simplify` voice lens that names tells by number, exactly as
   Go does today.

## The central rule

A structure linter can force a comment to exist. It cannot suppress a needless one. That asymmetry
held across all four languages and sets the policy: presence rules stay advisory and scoped to the
public API, and Claude's write-time gate owns the decision of whether a comment should exist at all.
This is Go's opt-in-on-unexported rule, generalized. The gate is the same three questions in every
language:

```
(a) Does the name plus the typed signature already say this?
(b) Is the why obvious from the next five lines or fewer?
(c) Would a reader otherwise miss a hidden constraint, invariant, side effect,
    or surprising consequence?
```

Skip on (a) or (b). Write only for (c). If a comment paraphrases the next few lines or restates a
fact the type annotation already carries, delete it.

## Go: the reference

Layer 1 is golangci-lint with `godot` and `revive` plus `go vet`. Layer 3 is the `go-conventions`
skill (the §0 gate, the decision rubric, and the §7 tell catalogue T1 through T43) with the deeper
palette in `go-comment-voice.md`. Layer 2 is the one gap on the proven language: Vale does not yet
scan `.go` comments here. Adding that scope closes it and is part of the sequence below. Nothing else
about Go changes; it is the template the other three follow.

## TypeScript

Standard: TSDoc, not JSDoc. TSDoc is the TypeScript team's specified grammar and a syntactic subset
of JSDoc, and it drops the type machinery that a typed language makes redundant. The load-bearing
rule is to document the contract, never the type. The signature already carries the types; a doc
comment carries only the constraint, the unit, the nil-semantic, or the caller obligation the type
cannot express. No `@param {type}`, no `@returns {type}`, no `@type`.

Layer 1, ESLint flat config (ESLint 9+):

- `eslint-plugin-jsdoc` on the `flat/recommended-typescript-error` base, which pre-disables the
  type-checking rules a typed language does not need.
- `jsdoc/no-types` (error): forbids `{type}` on tags.
- `jsdoc/check-tag-names` with `typed: true`: rejects `@type` and `@returns {T}` in TS.
- `jsdoc/require-jsdoc` with `publicOnly: true` (warn): a doc on exports only, never every symbol.
- `jsdoc/check-param-names`: catches `@param` drift after a rename.
- `jsdoc/informative-docs` (warn): the deterministic half of the paraphrase gate; flags a
  description that only restates the symbol name.
- `eslint-plugin-tsdoc` with `tsdoc/syntax` (error): validates the comment against the TSDoc spec.

Turn off `require-param`, `require-returns`, and the `*-description` rules. They would manufacture the
exact type-restatement the standard forbids. Turn off `require-throws-type` too: the cairn pilot found
it wants JSDoc-style `@throws {Type}`, which `tsdoc/syntax` rejects as a malformed inline tag, so the
two collide and TSDoc wins. The `flat/recommended-typescript-error` base also enforces the canonical
expanded doc-block shape (`multiline-blocks`, `tag-lines`), the form the SvelteKit source uses; a repo
whose comments predate the standard conforms them with `eslint --fix`, then hand-fixes the residue
(scoped package names and brace/angle prose spans go in backticks, a `@param` gets its hyphen). Biome
and oxlint carry no doc-comment content rules, so doc linting stays on ESLint.

Layer 2: `[formats] ts = md` in `.vale.ini`, then a `BasedOnStyles` line on `*.{ts,tsx}`. Vale scopes
to comment text on its own. The em dash is the thing it catches that ESLint never will.

Layer 3: the TS tell catalogue (TS1 through TS15, inventory in the appendix), carried by a new
`ts-conventions` skill, with the existing `ts-svelte-comments` register as the prose authority.

## Svelte

Two homes, no overlap, and this is the load-bearing rule. Component-level docs go in the
`<!-- @component -->` HTML comment, which the language server surfaces on hover at the import site.
Prop docs go on the typed `Props` interface members, never in `@component`. The type is the prop
contract; the JSDoc on each member adds only the why or the constraint the type cannot show.
Duplicating props into `@component` creates two sources of truth that drift.

Layer 1: `eslint-plugin-svelte` v3 (flat config, Svelte 5 runes) on the `.svelte` files, kept light:
the recommended reactivity and a11y rules plus one small custom rule. The custom rule, against the
`svelte-eslint-parser` template AST, checks that a component has exactly one `@component` comment (the
LSP uses only the last, so more than one is a silent footgun) and that its body has at least one
sentence of prose. The heavy jsdoc doc-shape rules go on `**/*.ts`, where they fire reliably, not on
`.svelte`. JSDoc rules under-fire inside `.svelte` when types stay in the signature, which is the
house style, so this is the intended split rather than a workaround.

Layer 2 is an extractor, not a Vale format mapping. The cairn pilot disproved the `[formats] svelte =
html` plan: Vale's `html` format does not scan `<!-- -->` comments at all (a planted slop word inside an
HTML comment fired nothing), so it misses the `@component` block, and it does scan the visible markup
text, so it leaks into the component's editor-facing product copy that `check:prose` already owns (it
flagged a real `<option>—</option>` UI em dash). Both behaviors are wrong for the comment arm. The fix
is a single extractor in the shape of `check-admin-prose.mjs`: pull the `@component` HTML comment and the
`//` and `/** */` script-block comments, write them to a temp Markdown buffer, and run Vale `glw907` over
that. One mechanism covers both comment homes, concedes nothing, and never touches product copy.

Layer 3: the Svelte tell catalogue (S1 through S10, appendix), carried by a `svelte-conventions`
skill, sharing the `ts-svelte-comments` register. The S-tells specialize the Go tells they extend (S2
over T1 for reactive lines, S5 over T28 for runes, S4 over T39 for template banners); flag the most
specific.

## Python

Standard: PEP 257 as the baseline, Google-style sections used sparingly, terse one-liners as the
default. The workstation's Python is small scripts in `~/.local/bin`, not a documented library, so a
one-line docstring or none is the common case, and an `Args:` or `Returns:` block is reserved for a
parameter or return contract the signature and the type hints leave unobvious. Type hints carry the
types; the docstring carries the why. Imperative mood, period-terminated.

Layer 1: `ruff`, which has replaced flake8, pydocstyle, isort, and black for this workflow. Set
`convention = "google"` under `[tool.ruff.lint.pydocstyle]` and `select = ["D"]`; ruff disables the
convention-incompatible rules for you. Then ignore the presence rules that fight the house bar
(`D100`, `D104`, `D105`, `D107`), keep the cheap correctness rules (`D200`, `D205`, `D212`, `D402`,
`D415`, `D419`), and re-enable `D401` for imperative mood, which the google convention drops. Exclude
tests via `per-file-ignores`, since a test name is its own documentation.

Layer 2: `[formats] py = md`, then `BasedOnStyles` on `*.py`. Vale scopes to `#` comments and `"""`
docstrings on its own. This is the natural home for the old `prose-guard` lexicon (banned phrases,
marketing words, judgment words, the em dash), now applied to Python comment scopes.

Layer 3: the Python tell catalogue (T-P1 through T-P13, appendix), carried by a `python-conventions`
skill, with a new `python-comments` register as the prose authority.

## The four decisions

Em dash in code comments. Banned, enforced deterministically. All three research sweeps classified it
as a blocking tell, and it is the clearest machine-authored signal in a code file, since a programmer
at a keyboard has no key for it. Vale enforces it on `.go`, `.ts`, and `.py`. The Svelte script-block
dead zone gets a tiny extractor (below). This resolves the matrix row the prose spec left open: in
code comments, the em dash is out.

Presence enforcement. The structure linters' "require a doc comment" rules stay at warn and scoped to
exports, and Claude's gate owns presence. Cairn already runs a `check:reference` gate that fails on an
undocumented export, so the ESLint coverage rule does not also gate at error there; the two would
double-cover the same ground.

Packaging. One `<lang>-conventions` skill per language (`ts-conventions`, `svelte-conventions`,
`python-conventions`), each mirroring `go-conventions`: the write-time gate, the tell catalogue, and a
copy-in lint config. The voice registers stay the prose authority. `ts-svelte-comments` already exists
and absorbs the TS and S catalogues; Python needs a new `python-comments` register; Go keeps
`go-comment-voice.md`.

Spec scope. This arm is its own spec, companion to the prose-system spec, because four languages
across three layers with roughly fifty tells and four skills does not fold cleanly into a doc that
also has to hold the prose and content audiences. The two specs share Vale and the charter's
feedforward-plus-feedback model, and they cover different files.

## The Svelte comment extractor

Vale's `.svelte` handling reaches neither comment home cleanly: the `html` format skips `<!-- -->`,
so it misses `@component`, and the `//` and `/** */` comments live inside `<script>`, which it skips
as code. The cairn pilot settled the design: one extractor in the shape of the existing
`scripts/check-admin-prose.mjs` pulls both regions, the `@component` HTML comment and the script-block
comments, into a temp Markdown buffer, then runs Vale `glw907` over that. A custom ESLint rule is the
heaviest option and conceding the surface to Claude judgment loses the deterministic guarantee, so the
extractor is the chosen path. It is small, it matches a pattern already in the repo, it keeps the
em-dash and lexicon net uniform across all four languages, and it never scans the component's product
copy, which is `check:prose`'s job.

## The cairn boundary

Cairn the product does no voice management. It ships editor spellcheck and tidy and nothing else, and
those are unrelated to this system. Cairn the repo is an ordinary consumer of these standards for its
own TypeScript and Svelte comments and its developer docs, the same as any other repo. The two never
merge, and cairn's `check:prose` admin gate, spellcheck, and tidy stay where they are.

## Verification flags

Carried from the research, to settle before the affected step ships:

- The claim that jsdoc rules under-fire inside `.svelte` when types stay in the signature is reasoned
  from the parser architecture, not quoted from one canonical doc. Pilot before relying on it.
- The `svelte = html` Vale mapping may trip on `{#if}` and `{@const}` mustache regions as if they were
  prose. Pilot on three components and measure the false-positive rate before wiring it into CI.
- `ruff` `D417` under `convention = "google"` has a reported non-firing bug (astral-sh/ruff #16477).
  Verify against the installed ruff version.
- Vale's native code-comment parsing is current in 3.x and covers the pinned 3.15.1; the exact
  release that added it was not pinned down. Confirm on the installed binary.

## Sequence

1. Add the `.go` comment scope to Vale and prove it against poplar, closing the one Go-side gap. This
   validates the Vale-on-comments mechanism on the proven language first.
2. TypeScript: the ESLint flat config, the Vale `ts` format, the `ts-conventions` skill, the TS
   catalogue into the register. Prove against cairn `src/lib`.
3. Svelte: the light `.svelte` ESLint config plus the custom `@component` rule, the `@component` Vale
   coverage, the script-comment extractor, the `svelte-conventions` skill, the S catalogue. Prove
   against cairn `src/lib/components`.
4. Python: the `ruff` `D` config, the Vale `py` format, the `python-conventions` skill, the
   `python-comments` register, the T-P catalogue. Prove against a `~/.local/bin` script.
5. Wire the `/simplify` voice lens to name TS, S, and T-P tells by number, matching the Go behavior.
6. Update the charter's build-state line and the `prose-voice.md` router once each language lands.

## Appendix: the tell-catalogue inventories

The full prose for each tell, with an AI-shaped example and a human counter-example, lands in the
`<lang>-conventions` skill and the register during the build. The inventories below preserve the
research: id, name, and the mechanical avoidance rule.

### TypeScript (TS1 through TS15)

| id | name | rule |
|---|---|---|
| TS1 | `@param {type}` restating the signature | never write a `{type}` in a tag; if the line only names the type, delete it |
| TS2 | type-narration in prose | state the constraint, not the type the annotation already shows |
| TS3 | "This function" opener | start with the behavior; vary the opener across a file |
| TS4 | every export documented reflexively | a self-evident export gets no doc, even when public |
| TS5 | `/** */` on a trivial internal | internals are opt-in; a one-line private helper gets a `//` at most |
| TS6 | uniform density across files | density follows complexity, not a fixed shape |
| TS7 | comment restating the next line | the paraphrase test; delete it |
| TS8 | section-boundary narration | comment where understanding fails, not where structure changes |
| TS9 | changelog or task-framing | no `// added for X`, `// fixes #N`; the commit carries it |
| TS10 | file-header banner repeating the path | a header earns its place only for a cross-cutting invariant |
| TS11 | over-documenting typed props | a prop doc adds a constraint or fallback, never the type |
| TS12 | `@component` narrating markup | state behavior and the failure mode, not a template walkthrough |
| TS13 | suppression without an inline reason | every `@ts-expect-error` carries its why, unless the line above argues it |
| TS14 | em dash and multi-clause comment rhythm | no em dash; one thought per comment |
| TS15 | invented label-colon paragraphs in TSDoc | use `@remarks`, `@throws`, `@defaultValue`, not `Note:` blocks |

### Svelte (S1 through S10)

| id | name | rule |
|---|---|---|
| S1 | `@component` restating every typed prop | `@component` is purpose plus contract plus failure mode; props speak through their JSDoc |
| S2 | narrating a reactive declaration | the rune declares the dependency; comment only a non-obvious why (extends T1) |
| S3 | over-commenting markup structure | markup nesting is visible; a template comment earns its place only for a why |
| S4 | redundant template section banners | the HTML-comment form of T39; delete unless it carries a constraint |
| S5 | commenting standard rune idioms | never explain what a rune does; comment only an unusual use (extends T28) |
| S6 | file-header boilerplate | the editor shows the filename; fold real content into `@component` |
| S7 | prop JSDoc restating the type | the type says the type; the doc adds the why or nothing |
| S8 | narrating handlers and bindings | the handler name and `bind:` are self-describing |
| S9 | `untrack`/snapshot under- or over-commented | one line of why is correct here; not zero, not a paragraph |
| S10 | uniform `@component` shape across the set | vary opener and length with each component's surface |

### Python (T-P1 through T-P13)

| id | name | rule |
|---|---|---|
| T-P1 | docstring restating the signature | if it is the signature in English, delete it |
| T-P2 | reflexive docstring on a trivial helper | a private helper gets a docstring only for unobvious behavior |
| T-P3 | `Args:`/`Returns:` duplicating type hints | document a constraint, not a type the hint declares |
| T-P4 | `# This function` / restating the next line | the paraphrase test; comment the surprise |
| T-P5 | module or class docstring banner | one prose sentence; no banner art, no metadata git tracks |
| T-P6 | type info in the docstring | annotate the signature; the docstring states intent |
| T-P7 | hedging or apologetic docstring | state the invariant; a real gap is a concrete `# TODO(glw907):` |
| T-P8 | uniform docstring rhythm | length follows complexity |
| T-P9 | uniform "Foo does X" shape | imperative mood, varied sentence shape across neighbors |
| T-P10 | speculative `Raises:` entries | document only an exception a caller must handle |
| T-P11 | over-explaining Python idioms | never explain `with` or a comprehension to a Python reader |
| T-P12 | task-framing or changelog comments | git carries the task and the fix |
| T-P13 | restated-annotation `#` comment | the annotation is the type statement; delete the comment |
