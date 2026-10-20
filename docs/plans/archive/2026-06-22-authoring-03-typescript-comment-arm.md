# TypeScript Comment Arm Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring TypeScript comments under the charter's three layers in a real consumer repo. cairn adopts ESLint with the jsdoc/tsdoc flat config (structure), Vale on `.ts` comment prose through the vendored `glw907` overlay (the em-dash and lexicon net), and a new `ts-conventions` skill plus the expanded `ts-svelte-comments` register (the semantic TS1 through TS15 tells). Proven against cairn `src/lib`.

**Architecture:** Layer 1 is an ESLint 9+ flat config that lints `src/lib/**/*.ts` with `eslint-plugin-jsdoc` on the `flat/recommended-typescript-error` base plus `eslint-plugin-tsdoc`, scoped so it documents the contract and never the type. Layer 2 reuses the Go arm's mechanism: Vale's Code-format support extracts comment text from a `.ts` file and lints it as Markdown, so the `glw907` lexical rules fire on comments and ignore code. Layer 3 is the `ts-conventions` skill (the write-time gate, the copy-in lint config, the TS catalogue) with `ts-svelte-comments` as the prose authority. cairn carries a committed `glw907` copy vendored by the existing `glw907-vendor.sh`, an in-tree `.vale.ini` mapping `[*.ts]` to that overlay, an `eslint.config.js`, and a `check:comments` gate wired into CI. This is the second consumer adoption; poplar was the first, on Go.

**Tech Stack:** Vale 3.15.1 (errata-ai/vale), ESLint 9 with `typescript-eslint` parser, `eslint-plugin-jsdoc` 63, `eslint-plugin-tsdoc` 0.5, bash, the hand-written `glw907` Vale style, the cairn SvelteKit/TS repo, and a new `ts-conventions` skill.

## Global Constraints

- Vale is pinned to `3.15.1`; the binary is `~/.local/bin/vale` and reports that version. The Code-format comment scoping this plan depends on is confirmed present on that build (plan 01 Task 1, plan 02).
- The canonical `glw907` style lives at `~/.dotfiles/vale/.config/vale/styles/glw907`. Every consumer repo carries a committed copy at `<repo>/.vale/styles/glw907`, never a symlink, vendored by `~/.dotfiles/scripts/glw907-vendor.sh <repo> --sync`.
- The TypeScript standard is TSDoc, not JSDoc. Document the contract, never the type: no `@param {type}`, no `@returns {type}`, no `@type`. The signature carries the types.
- ESLint rule tiers, from the comment-standards spec: `jsdoc/no-types` error, `jsdoc/check-tag-names` with `typed: true` error, `tsdoc/syntax` error, `jsdoc/check-param-names` error, `jsdoc/require-jsdoc` with `publicOnly: true` at warn, `jsdoc/informative-docs` at warn. Turn off `require-param`, `require-returns`, and the `*-description` rules (they manufacture the type-restatement the standard forbids) and `require-throws-type` (it wants JSDoc-style `@throws {Type}`, which TSDoc rejects). The `flat/recommended-typescript-error` base also enforces the canonical expanded doc-block shape (`multiline-blocks`, `tag-lines`); an adopting repo conforms its comments to that with `eslint --fix`.
- `require-jsdoc` stays at warn, not error: cairn already runs `check:reference`, which fails on an undocumented export, so the ESLint coverage rule must not double-gate the same ground.
- The em dash stays banned in TypeScript comments. No opt-out section is added for `.ts`; the `glw907.EmDash = NO` toggle exists only for a literary register and never applies to code.
- The pinned plugin versions are `eslint@^9`, `typescript-eslint@^8`, `eslint-plugin-jsdoc@^63`, `eslint-plugin-tsdoc@^0.5`, added to cairn `devDependencies`. They never ship: cairn's `package.json` `files` allowlist is `["dist","src/lib","CHANGELOG.md"]`, so the root `eslint.config.js`, `.vale.ini`, and `.vale/` are not published.
- This plan does not touch `prose-guard`. It stays the active hook until the cutover plan (07).
- dotfiles changes commit to dotfiles `main`, matching plans 01 and 02. cairn changes land on a branch off `main` and merge back when the gate is green. The library source change is comment-only (the doc-comment conformance); svelte-check and the tests confirm no behavior moves. Leave the push to Geoff.
- Commit footer on both repos: `Co-Authored-By: Claude <noreply@anthropic.com>`.

## The plan series

This is plan 03 of the authoring-system build. Each plan is written just-in-time after the prior one lands. Plans 01 (Vale foundation) and 02 (Go comment arm) are done and committed on dotfiles `main`, and poplar carries the Go arm on `master`.

1. **Vale foundation** (done): the pinned binary, the split `glw907` overlay, the vendored Google and Microsoft baselines, the global config, the fixture suite including a comment-scope proof.
2. **Go comment arm** (done): the reusable `glw907-vendor.sh`, poplar's adoption with an in-tree `.vale.ini` scoping `glw907` to `.go` comments, the live proof, the `make check` gate, and the `/simplify` Go voice lens confirmed.
3. **TypeScript comment arm** (this plan): the ESLint jsdoc/tsdoc flat config, the `ts` Vale format in cairn, the `ts-conventions` skill, the TS1 through TS15 catalogue into the `ts-svelte-comments` register, proven against cairn `src/lib`, with a `check:comments` CI gate.
4. **Svelte comment arm:** the light `eslint-plugin-svelte` config plus the custom `@component` rule, `@component` Vale coverage, the script-block comment extractor, the `svelte-conventions` skill, the S1 through S10 catalogue. Prove against cairn `src/lib/components`.
5. **Python comment arm:** the `ruff` `D` config, the `py` Vale format, the `python-conventions` skill, the `python-comments` register, the T-P1 through T-P13 catalogue.
6. **Prose arm:** the Google and Microsoft baselines applied to docs and content per glob, the prose registers leading on exemplars, the PostToolUse prose Vale hook scoped to changed lines. cairn and poplar gain their `docs/**/*.md` to Google mapping here.
7. **Cutover:** wire the Vale hook in `settings.json`, prove the loop, retire `prose-guard`, rewrite the active output style and the CLAUDE.md writing-voice section, repoint the `prose-voice.md` router. Sequence step 5 (wire the `/simplify` voice lens to name TS, S, and T-P tells by number) lands once the language arms are in.

The source specs are `~/.dotfiles/docs/superpowers/specs/2026-06-22-ai-drafting-prose-system-design.md` (prose arm) and `~/.dotfiles/docs/superpowers/specs/2026-06-22-code-comment-standards-design.md` (comment arm). The umbrella is `~/.claude/docs/authoring-charter.md`.

---

### Task 1: The `ts-conventions` skill

Create the layer-3 skill for TypeScript, mirroring `go-conventions`: the write-time comment-or-not gate, the decision rubric, the TSDoc doc-comment shape, the copy-in ESLint flat config (so a consumer repo copies it in, the way `go-conventions` carries the golangci config), and the TS1 through TS15 catalogue with mechanical avoidance rules. The `ts-svelte-comments` register stays the prose authority and is expanded in Task 2.

**Files:**
- Create: `~/.dotfiles/claude/.claude/skills/ts-conventions/SKILL.md`

**Interfaces:**
- Consumes: nothing built earlier; it is a new authority doc.
- Produces: the `ts-conventions` skill, invocable by name, carrying the §0 gate, the TSDoc shape rules, the exact `eslint.config.js` that Task 4 copies into cairn, and the TS1 through TS15 catalogue the `/simplify` lens will cite by number in a later step.

- [ ] **Step 1: Write the failing check**

The skill does not exist yet. This is the test for the task:

```bash
test -f ~/.dotfiles/claude/.claude/skills/ts-conventions/SKILL.md && echo PASS || echo FAIL
```

Expected: `FAIL`.

- [ ] **Step 2: Create the skill directory and write SKILL.md**

```bash
mkdir -p ~/.dotfiles/claude/.claude/skills/ts-conventions
```

Write `~/.dotfiles/claude/.claude/skills/ts-conventions/SKILL.md` with exactly this content:

````markdown
---
name: ts-conventions
description: >
  Mandatory rules for writing TypeScript comments on this workstation.
  Use before writing, reviewing, or modifying any TypeScript doc comment
  or inline comment. Covers the write-time comment-or-not gate, the TSDoc
  doc-comment shape (document the contract, never the type), the copy-in
  ESLint jsdoc/tsdoc flat config, and the TS1 through TS15 AI-tell
  catalogue. The prose authority is the ts-svelte-comments register.
---

# TypeScript Comment Conventions

The reader is a coder or an agent already looking at the code. A comment carries what the
code cannot: a why, a constraint, a piece of evidence. The type annotation already states
the type, so a doc comment that restates it is noise. This skill is the TypeScript arm of the
authoring charter (`~/.claude/docs/authoring-charter.md`). The deeper prose authority, with
exemplars from the SvelteKit and cairn source, is the `ts-svelte-comments` register at
`~/.claude/docs/voice/ts-svelte-comments.md`; load it before writing or reviewing comments.

## Persona

You write comments the way the SvelteKit and Svelte maintainers do: terse, placed only where
behavior gets surprising, candid about hacks, with links doing the arguing. True prose
commentary runs about 8 to 12 lines per 100 and concentrates where browser behavior, ordering,
or state gets weird. Straightforward plumbing stays silent.

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
test is the primary filter against AI-shaped comments.

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
- One thought per comment. No em dash.

## Linting: the copy-in ESLint flat config

A consumer repo copies this `eslint.config.js` in (cairn is the first). It lints
`src/lib/**/*.ts` on the jsdoc typescript-error base plus tsdoc, with the rule tiers the
charter fixes. Adjust the `files` glob to the repo's source root.

```js
import jsdoc from 'eslint-plugin-jsdoc';
import tsdoc from 'eslint-plugin-tsdoc';
import tseslint from 'typescript-eslint';

export default [
  { files: ['src/lib/**/*.ts'], ...jsdoc.configs['flat/recommended-typescript-error'] },
  {
    files: ['src/lib/**/*.ts'],
    languageOptions: { parser: tseslint.parser },
    plugins: { jsdoc, tsdoc },
    rules: {
      // The contract, never the type. The signature already carries the types.
      'jsdoc/no-types': 'error',
      'jsdoc/check-tag-names': ['error', { typed: true }],
      'tsdoc/syntax': 'error',
      'jsdoc/check-param-names': 'error',
      // A doc on exports only, and at warn: check:reference owns the hard coverage gate.
      'jsdoc/require-jsdoc': ['warn', { publicOnly: true }],
      // The deterministic half of the paraphrase gate.
      'jsdoc/informative-docs': 'warn',
      // These manufacture the type-restatement the standard forbids.
      'jsdoc/require-param': 'off',
      'jsdoc/require-returns': 'off',
      'jsdoc/require-param-description': 'off',
      'jsdoc/require-returns-description': 'off',
    },
  },
];
```

The parser is `typescript-eslint`'s with no `project` setting: the jsdoc and tsdoc rules read
the comment AST, not the type graph, so type-aware linting is not needed and the run stays
fast.

## §catalogue: the TS1 through TS15 AI-tell catalogue

Each tell: id, name, the mechanical avoidance rule. The full prose, with an AI-shaped example
and a human counter-example, is in the `ts-svelte-comments` register. When a finding triggers
more than one tell, cite the strongest. TS1 (type restatement) outranks TS2 (type narration);
TS7 (paraphrase) outranks a structural tell on the same line.

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

## Tooling and the division of labor

Three layers, three jobs:

- ESLint (jsdoc + tsdoc) owns structure: the `{type}` ban, TSDoc syntax, `@param` drift, the
  coverage warning. It cannot see prose quality.
- Vale on `.ts` comments owns the deterministic lexical net: the em dash, the marketing and
  slop words, the banned phrases. It is the home of the retired `prose-guard` comment tier.
- This skill and the register own the semantic tells Vale and ESLint cannot see: the paraphrase,
  the doc on a self-evident export, the uniform comment rhythm. When a finding is a plain
  lexical or structural hit, expect ESLint or Vale to have caught it; spend the judgment here.

## Output

When reviewing, cite each finding as `TS<n> at file:line` with the one-line avoidance rule.
When writing, run the §0 gate first, then the rubric, then write only what survives.
````

- [ ] **Step 3: Re-run the check from step 1**

```bash
test -f ~/.dotfiles/claude/.claude/skills/ts-conventions/SKILL.md && echo PASS || echo FAIL
```

Expected: `PASS`.

- [ ] **Step 4: Confirm the skill carries the gate, the config, and the catalogue**

```bash
S=~/.dotfiles/claude/.claude/skills/ts-conventions/SKILL.md
grep -q 'Comment-or-not' "$S" && echo "GATE OK" || echo "GATE MISSING"
grep -q "flat/recommended-typescript-error" "$S" && echo "CONFIG OK" || echo "CONFIG MISSING"
grep -qE 'TS1 \|.*TS15|TS15 \|' "$S" && echo "CATALOGUE OK" || echo "CATALOGUE MISSING"
```

Expected: `GATE OK`, `CONFIG OK`, `CATALOGUE OK`.

- [ ] **Step 5: Confirm the skill lints clean through the dotfiles config**

The skill is under `claude/.claude/`, so the dotfiles in-tree `.vale.ini` lints it through `glw907`:

```bash
cd ~/.dotfiles && vale claude/.claude/skills/ts-conventions/SKILL.md | tail -3
```

Expected: a clean or advisory-only run, no `error`-level findings. An `error` here is most likely a real em dash in the prose; fix it in plain voice.

- [ ] **Step 6: Commit**

```bash
cd ~/.dotfiles
git add claude/.claude/skills/ts-conventions/SKILL.md
git commit -m "Add the ts-conventions skill for the TypeScript comment arm" \
  -m "Carries the write-time gate, the TSDoc shape, the copy-in ESLint flat config, and the TS1 through TS15 catalogue. The ts-svelte-comments register stays the prose authority." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: Expand the `ts-svelte-comments` register with the TS catalogue

The register is the prose authority for TS and Svelte comments. It already carries the placement
rules and exemplars. Add the TS1 through TS15 catalogue as prose so the register is the single
home of the expanded tells, and update the em-dash line, which currently credits the
`prose-guard` hook, to name Vale as the net in `.ts` comments.

**Files:**
- Modify: `~/.dotfiles/claude/.claude/docs/voice/ts-svelte-comments.md`

**Interfaces:**
- Consumes: the TS1 through TS15 ids defined in the Task 1 skill catalogue.
- Produces: the register section the `ts-conventions` skill points at for the full tell prose.

- [ ] **Step 1: Update the em-dash line to credit Vale**

In `~/.dotfiles/claude/.claude/docs/voice/ts-svelte-comments.md`, find the sentence in the
"Length scales with distance from the reader" section that reads "cairn does not (the hook
blocks it), so imitate the function, not the punctuation." Replace "the hook blocks it" with
"Vale blocks it on `.ts` comments":

```
plural, candid about hacks and uncertainty. Upstream occasionally drops an em dash in an
inline comment; cairn does not (Vale blocks it on `.ts` comments), so imitate the function,
not the punctuation.
```

- [ ] **Step 2: Append the catalogue section**

Add this section to the end of `~/.dotfiles/claude/.claude/docs/voice/ts-svelte-comments.md`:

````markdown
## The TS tell catalogue (TS1 through TS15)

The numbered tells the `ts-conventions` skill cites. Each is an AI-shaped habit with its
mechanical fix; the worked examples below cover the tells the exemplars above do not already
show.

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
| TS15 | invented label-colon paragraphs in TSDoc | use the real tags, not a `Note:` block |

TS1, type restated from the signature. The annotation already says `string`:

```ts
// off-voice
/**
 * @param name {string} the user's name
 * @returns {string} the greeting
 */
// in-voice: state only the contract the type cannot
/** Greets the user. Falls back to "friend" when name is empty. */
```

TS9, the changelog comment. Git carries the task and the fix:

```ts
// off-voice
// added 2026-06 to fix the double-submit bug, see #1422
const token = freshToken();
// in-voice: the why, if it is not obvious; the issue link only if it argues the code
const token = freshToken(); // a reused token trips the guard's single-use check
```

TS13, the bare suppression. The reason rides inline:

```ts
// off-voice
// @ts-expect-error
widget.focus();
// in-voice
// @ts-expect-error the focus shim lands after hydration; types catch up next tick
widget.focus();
```

TS15, the invented label-colon paragraph. Use the tag the grammar provides:

```ts
// off-voice
/** Parses the slug. Note: throws on a trailing slash. */
// in-voice
/**
 * Parses the slug.
 * @throws {RangeError} when the slug carries a trailing slash.
 */
```
````

- [ ] **Step 3: Confirm the catalogue landed and the register lints clean**

```bash
cd ~/.dotfiles
grep -q 'TS tell catalogue' claude/.claude/docs/voice/ts-svelte-comments.md && echo "SECTION OK" || echo "SECTION MISSING"
vale claude/.claude/docs/voice/ts-svelte-comments.md | tail -3
```

Expected: `SECTION OK`, then a clean or advisory-only Vale run with no `error`-level findings.

- [ ] **Step 4: Commit**

```bash
cd ~/.dotfiles
git add claude/.claude/docs/voice/ts-svelte-comments.md
git commit -m "Add the TS1 through TS15 catalogue to the ts-svelte-comments register" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: cairn adopts Layer 2, Vale on `.ts` comments

cairn carries a committed `glw907` copy and an in-tree `.vale.ini` that lints its `.ts` comment
prose. The config maps `[*.ts]` to the overlay only; the `docs/**/*.md` to Google mapping is the
prose arm's job in plan 06, noted in the file. The proof runs Vale over real cairn TypeScript
and over one throwaway file with a planted tell.

**Files:**
- Create: `~/Projects/cairn-cms/.vale.ini`
- Create: `~/Projects/cairn-cms/.vale/styles/glw907/**` (vendored by `glw907-vendor.sh`)

**Interfaces:**
- Consumes: `~/.dotfiles/scripts/glw907-vendor.sh`; the pinned Vale binary; the `glw907` style.
- Produces: a cairn repo where `cd ~/Projects/cairn-cms && vale <file>.ts` lints comment prose through `glw907`. Task 5's gate and the cutover hook resolve this in-tree config.

- [ ] **Step 1: Branch cairn off main**

```bash
cd ~/Projects/cairn-cms
git switch -c authoring/vale-ts-comment-arm
git status --short
```

Expected: a clean working tree on the new branch.

- [ ] **Step 2: Confirm `.vale/` is not ignored, then vendor the style**

```bash
cd ~/Projects/cairn-cms
git check-ignore .vale/styles/glw907/Slop.yml && echo "IGNORED, fix .gitignore" || echo "not ignored, good"
bash ~/.dotfiles/scripts/glw907-vendor.sh ~/Projects/cairn-cms --sync
ls .vale/styles/glw907
```

Expected: `not ignored, good`; then `vendored glw907 -> ...`; then the rule files
(`BannedPhrases.yml`, `EmDash.yml`, `Filler.yml`, `Judgment.yml`, `Marketing.yml`, `Openers.yml`,
`Slop.yml`). cairn's `.gitignore` ignores only `node_modules/`, so `.vale/` is tracked.

- [ ] **Step 3: Write cairn's in-tree audience map**

Create `~/Projects/cairn-cms/.vale.ini`:

```ini
StylesPath = .vale/styles
MinAlertLevel = suggestion

# Comment-scoped linting: extract TypeScript comment text and lint it as Markdown.
[formats]
ts = md

# TypeScript comments: the house overlay. The em dash stays banned (no opt-out section).
# Vale lints only the comment text and ignores code tokens.
[*.ts]
BasedOnStyles = glw907

# Judgment over-fires on legitimate technical vocab; keep it advisory here, as poplar does.
glw907.Judgment = suggestion

# The docs/**/*.md to Google + glw907 mapping and the .svelte coverage arrive with later
# plans (06 prose, 04 Svelte). Left out here on purpose so this arm stays scoped to .ts.
```

- [ ] **Step 4: Confirm the config parses and resolves its styles**

```bash
cd ~/Projects/cairn-cms
vale ls-config | grep -E 'StylesPath|MinAlertLevel'
```

Expected: the resolved `StylesPath` ends in cairn's `.vale/styles`, and `MinAlertLevel` is
`suggestion`. A parse error here means a glob or key is malformed.

- [ ] **Step 5: Proof A, no em dash in real cairn TypeScript comments**

Real cairn `src/lib` carries no em dash in any comment today (verified while scoping this plan).
Vale should agree:

```bash
cd ~/Projects/cairn-cms
n="$(vale --output=line $(git ls-files 'src/lib/**/*.ts') 2>/dev/null | grep -c 'glw907.EmDash')"
echo "em-dash findings in real src/lib TS comments: $n"
[ "$n" -eq 0 ] && echo "PROOF-A PASS" || echo "PROOF-A FAIL"
```

Expected: `0`, then `PROOF-A PASS`. A non-zero count is a real finding to read and fix in plain
voice, not a tooling fault; clean the comment before continuing.

- [ ] **Step 6: Proof B, a planted tell fires on the comment and not the code**

Place one throwaway `.ts` inside cairn's tree so the in-tree config governs it, then delete it.
The em dash is written from its bytes so the literal character stays out of the repo:

```bash
cd ~/Projects/cairn-cms
mkdir -p .vale-proof
printf 'export function leverage() {\n  // Build a seamless pipeline %s fast.\n  return 1;\n}\n' \
  "$(printf '\xe2\x80\x94')" > .vale-proof/x.ts
out="$(vale --output=line .vale-proof/x.ts)"
echo "$out"
grep -q 'x.ts:2:.*glw907.EmDash' <<<"$out" && echo "EM-DASH-ON-COMMENT PASS" || echo "EM-DASH FAIL"
grep -q 'x.ts:2:.*glw907.Slop'   <<<"$out" && echo "SLOP-ON-COMMENT PASS"    || echo "SLOP FAIL"
grep -q 'x.ts:1:' <<<"$out" && echo "SCOPE LEAK on code line" || echo "SCOPE-HOLDS PASS"
rm -rf .vale-proof
ls -d .vale-proof 2>&1
```

Expected: `Slop` and `EmDash` both fire on line 2 (the comment); nothing fires on line 1
(`export function leverage`, where `leverage` is a Judgment token sitting in code, and Judgment
is advisory anyway). So `EM-DASH-ON-COMMENT PASS`, `SLOP-ON-COMMENT PASS`, `SCOPE-HOLDS PASS`,
then a "No such file" for `.vale-proof`.

- [ ] **Step 7: Commit on the cairn branch**

```bash
cd ~/Projects/cairn-cms
git add .vale.ini .vale/styles/glw907
git commit -m "Adopt the Vale TypeScript comment arm: in-tree config and vendored glw907" \
  -m "Lints .ts comment prose through the glw907 overlay; the em dash and the banned lexicon now fire on comments and ignore code. Proven against real cairn TS and a planted tell." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: cairn adopts Layer 1, the ESLint jsdoc/tsdoc flat config

cairn has no ESLint today. Add it with the copy-in flat config from the `ts-conventions` skill,
scoped to `src/lib/**/*.ts`. cairn's comments predate the standard, so the base preset surfaces
real deviations: the contract-not-type rules (`no-types`, `check-tag-names`, `check-param-names`)
are already clean, but the canonical block-shape rules (`multiline-blocks`, `tag-lines`) flag
cairn's compact form pervasively, and `tsdoc/syntax` flags scoped package names and brace/angle
prose spans. This task adds the config and conforms cairn's comments to the standard: `eslint
--fix` for the mechanical reformat, then hand-fixes for the residue. After conformance the error
tier is clean.

**Files:**
- Create: `~/Projects/cairn-cms/eslint.config.js`
- Modify: `~/Projects/cairn-cms/package.json` (devDependencies and a `lint` script)
- Modify: `~/Projects/cairn-cms/src/lib/**/*.ts` (doc-comment conformance; comment text only)

**Interfaces:**
- Consumes: the exact `eslint.config.js` content from the Task 1 skill.
- Produces: a `npm run lint` that lints `src/lib` TypeScript through the jsdoc/tsdoc rules, error-clean after conformance, and a positive control proving the `{type}` ban fires.

- [ ] **Step 1: Install the pinned devDependencies**

```bash
cd ~/Projects/cairn-cms
npm install --save-dev --no-audit --no-fund \
  eslint@^9 typescript-eslint@^8 eslint-plugin-jsdoc@^63 eslint-plugin-tsdoc@^0.5
```

Expected: the four packages land in `devDependencies` and `package-lock.json` updates.

- [ ] **Step 2: Write the flat config**

Create `~/Projects/cairn-cms/eslint.config.js` with exactly the config from the `ts-conventions`
skill's "Linting" section:

```js
import jsdoc from 'eslint-plugin-jsdoc';
import tsdoc from 'eslint-plugin-tsdoc';
import tseslint from 'typescript-eslint';

export default [
  { files: ['src/lib/**/*.ts'], ...jsdoc.configs['flat/recommended-typescript-error'] },
  {
    files: ['src/lib/**/*.ts'],
    languageOptions: { parser: tseslint.parser },
    plugins: { jsdoc, tsdoc },
    rules: {
      // The contract, never the type. The signature already carries the types.
      'jsdoc/no-types': 'error',
      'jsdoc/check-tag-names': ['error', { typed: true }],
      'tsdoc/syntax': 'error',
      'jsdoc/check-param-names': 'error',
      // A doc on exports only, and at warn: check:reference owns the hard coverage gate.
      'jsdoc/require-jsdoc': ['warn', { publicOnly: true }],
      // The deterministic half of the paraphrase gate.
      'jsdoc/informative-docs': 'warn',
      // These manufacture the type-restatement the standard forbids.
      'jsdoc/require-param': 'off',
      'jsdoc/require-returns': 'off',
      'jsdoc/require-param-description': 'off',
      'jsdoc/require-returns-description': 'off',
      // require-throws-type wants JSDoc-style `@throws {Type}`, which TSDoc rejects as a
      // malformed inline tag. The charter mandates TSDoc, so @throws stays prose.
      'jsdoc/require-throws-type': 'off',
    },
  },
];
```

- [ ] **Step 3: Add the `lint` script**

In `~/Projects/cairn-cms/package.json`, add a `lint` entry to `scripts`:

```json
    "lint": "eslint src/lib",
```

- [ ] **Step 3b: Conform cairn's comments to the standard**

cairn's comments predate the standard, so the first lint run reports the deviations. Reformat the
mechanical ones, then hand-fix the residue. The reformat is comment-only, so behavior is unchanged:

```bash
cd ~/Projects/cairn-cms
npx --no-install eslint src/lib --fix
npx --no-install eslint src/lib -f json 2>/dev/null | python3 -c "import json,sys; from collections import Counter; c=Counter(m.get('ruleId') for f in json.load(sys.stdin) for m in f['messages'] if m['severity']==2); print(dict(c) or 'NONE')"
```

`--fix` clears `jsdoc/multiline-blocks` and `jsdoc/tag-lines` (the compact-to-expanded reformat).
The residue it cannot fix is hand-work, each a real best-practice fix:

- A scoped package name in prose (`@codemirror/view`, `@octokit/auth-app`, `@cloudflare/workers-types`)
  reads to TSDoc as a tag. Wrap it in backticks: `` `@codemirror/view` ``.
- A brace or angle span in prose (`{attrs}`, `{}`, `{ owner, repo }`, `< 128`) reads as an inline
  tag or HTML. Wrap it in backticks.
- An arrow `->` carries a `>` TSDoc reads as HTML. Reword (`gives`, `becomes`).
- A `@param name description` is missing its TSDoc hyphen. Add it: `@param name - description`.

Re-run until the error tier is empty:

```bash
cd ~/Projects/cairn-cms
npx --no-install eslint src/lib --quiet && echo "ERROR TIER CLEAN" || echo "RESIDUE REMAINS"
npm run check 2>&1 | tail -1
```

Expected: `ERROR TIER CLEAN`, then svelte-check reporting `0 ERRORS 0 WARNINGS` (the reformat is
comment-only and changes no behavior).

- [ ] **Step 4: Positive control, the config fires on a planted `{type}` tag**

Place one throwaway file under `src/lib` so the config governs it, then delete it:

```bash
cd ~/Projects/cairn-cms
mkdir -p src/lib/.eslint-proof
printf '/**\n * Adds two numbers.\n * @param {number} a The first addend.\n * @returns {number} the sum\n */\nexport function addProof(a: number, b: number): number { return a + b; }\n' \
  > src/lib/.eslint-proof/x.ts
out="$(npx --no-install eslint src/lib/.eslint-proof/x.ts 2>&1)"
echo "$out"
grep -q 'jsdoc/no-types' <<<"$out" && echo "NO-TYPES PASS" || echo "NO-TYPES FAIL"
grep -q 'tsdoc/syntax'   <<<"$out" && echo "TSDOC PASS"    || echo "TSDOC FAIL"
rm -rf src/lib/.eslint-proof
```

Expected: ESLint reports `jsdoc/no-types` and `tsdoc/syntax` errors on the file, then
`NO-TYPES PASS`, `TSDOC PASS`. The proof file is removed.

- [ ] **Step 5: Confirm the full gate is green**

```bash
cd ~/Projects/cairn-cms
npm run lint && echo "lint exit 0"
```

Expected: ESLint exits 0. `require-jsdoc` and `informative-docs` are at warn, so an undocumented
export surfaces as a warning, not a failure; the error tier is clean after Step 3b's conformance.

- [ ] **Step 6: Commit, infra and conformance separately**

Keep the mechanical reformat in its own commit so the history stays reviewable:

```bash
cd ~/Projects/cairn-cms
git add eslint.config.js package.json package-lock.json
git commit -m "Add the ESLint jsdoc/tsdoc flat config for src/lib TypeScript comments" \
  -m "TSDoc structure on the error tier (no-types, tsdoc/syntax, check-tag-names, check-param-names); coverage and paraphrase rules at warn. require-throws-type is off: it wants JSDoc-style @throws {Type}, which TSDoc rejects." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git add src/lib
git commit -m "Conform src/lib doc comments to TSDoc best practice" \
  -m "Reformat to the canonical expanded block form (eslint --fix), backtick scoped package names and brace/angle prose spans, add the @param hyphen. Comment-only; svelte-check 0/0, Vale 0 errors." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: The `check:comments` gate, CI wiring, and the CLAUDE.md pointer

Wire the two deterministic layers into one gate cairn runs in CI: ESLint for structure, Vale for
the em-dash and lexicon net on `.ts` comments. CI installs the pinned Vale binary before the
gate, since Vale is a system tool, not an npm dependency. Add the authoring pointer to cairn's
CLAUDE.md.

**Files:**
- Create: `~/Projects/cairn-cms/scripts/check-comments.sh`
- Modify: `~/Projects/cairn-cms/package.json` (a `check:comments` script)
- Modify: `~/Projects/cairn-cms/.github/workflows/test.yml` (a Vale setup step and the gate)
- Modify: `~/Projects/cairn-cms/CLAUDE.md` (an authoring pointer)

**Interfaces:**
- Consumes: the `eslint.config.js` from Task 4, the `.vale.ini` and vendored style from Task 3.
- Produces: `npm run check:comments`, green locally and in CI; the gate every future TS comment change clears.

- [ ] **Step 1: Write the gate script**

Create `~/Projects/cairn-cms/scripts/check-comments.sh`:

```bash
#!/usr/bin/env bash
# check-comments.sh: the TypeScript comment gate. ESLint enforces TSDoc structure on
# src/lib; Vale enforces the em-dash ban and the glw907 lexicon on the same comment prose.
# CI installs the pinned vale binary before calling this. The two layers are independent,
# so the script runs both and fails if either does.
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0

echo "== eslint (TSDoc structure on src/lib) =="
npx --no-install eslint src/lib || fail=1

echo "== vale (em dash + lexicon on .ts comments) =="
files="$(git ls-files 'src/lib/**/*.ts')"
vale --minAlertLevel=error $files || fail=1

[ "$fail" -eq 0 ] && echo "check:comments OK" || echo "check:comments FAILED"
exit "$fail"
```

Make it executable:

```bash
chmod +x ~/Projects/cairn-cms/scripts/check-comments.sh
```

- [ ] **Step 2: Add the `check:comments` script**

In `~/Projects/cairn-cms/package.json`, add to `scripts`:

```json
    "check:comments": "bash scripts/check-comments.sh",
```

- [ ] **Step 3: Run the gate locally**

```bash
cd ~/Projects/cairn-cms
npm run check:comments
echo "exit: $?"
```

Expected: both sections run, `check:comments OK`, exit 0. ESLint at error tier is clean and real
`src/lib` carries no em dash, so the gate passes.

- [ ] **Step 4: Wire the gate into CI with a Vale setup step**

In `~/Projects/cairn-cms/.github/workflows/test.yml`, after the `- run: npm run check:version`
line (the last step), append the Vale install and the gate:

```yaml
      - name: Install Vale 3.15.1
        run: |
          curl -sfL https://github.com/errata-ai/vale/releases/download/v3.15.1/vale_3.15.1_Linux_64-bit.tar.gz \
            | sudo tar -xz -C /usr/local/bin vale
          vale --version
      - run: npm run check:comments
```

- [ ] **Step 5: Confirm the workflow YAML parses**

```bash
cd ~/Projects/cairn-cms
python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/test.yml')); print('YAML OK')"
```

Expected: `YAML OK`. A parse error means the indentation of the appended step is wrong.

- [ ] **Step 6: Add the authoring pointer to cairn's CLAUDE.md**

Append this section to `~/Projects/cairn-cms/CLAUDE.md`, after the existing top-level content and
before any closing material:

```markdown
## Authoring

Claude's drafting on this repo follows the workstation authoring charter at
`~/.claude/docs/authoring-charter.md`. The TypeScript comment audience is wired through three
layers: ESLint (`eslint.config.js`, `npm run lint`) enforces TSDoc structure on `src/lib`,
forbidding `{type}` tags and invalid TSDoc; Vale lints `.ts` comment prose through the vendored
`glw907` overlay in `.vale/styles/glw907` (the in-tree `.vale.ini`), catching the em dash and
the banned lexicon; the `ts-conventions` skill and the `ts-svelte-comments` register carry the
semantic TS1 through TS15 tells. `npm run check:comments` runs the deterministic two in CI.
Re-sync the overlay after a canonical change with
`~/.dotfiles/scripts/glw907-vendor.sh ~/Projects/cairn-cms --sync`. This is separate from
cairn's product prose tooling (`check:prose`, spellcheck, tidy), which serves editors, not
Claude. The docs prose mapping arrives with the charter's prose arm.
```

- [ ] **Step 7: Confirm the pointer carries no em dash, then commit**

The new section is in a `.md` file, and cairn's `.vale.ini` has no `[*.md]` section yet, so check
by hand:

```bash
cd ~/Projects/cairn-cms
grep -nP '\xe2\x80\x94' CLAUDE.md && echo "EM-DASH PRESENT, fix it" || echo "CLAUDE.md em-dash clean"
```

Expected: `CLAUDE.md em-dash clean`.

```bash
cd ~/Projects/cairn-cms
git add scripts/check-comments.sh package.json .github/workflows/test.yml CLAUDE.md
git commit -m "Wire the TypeScript comment gate into CI and document the adoption" \
  -m "check:comments runs ESLint (structure) and Vale (em dash + lexicon) on src/lib .ts comments; CI installs the pinned Vale binary first." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: Confirm an agent names TS tells, and record the division of labor

Vale and ESLint give TS comments a deterministic net. The skill and register are the semantic
layer. This task proves an agent given the skill and register names a TS tell by number, the
feedforward proof, and confirms the division-of-labor note reads correctly. The `/simplify`
voice-lens wiring for TS, S, and T-P tells is sequence step 5, after the language arms land; this
task does not wire it, it proves the catalogue is usable.

**Files:**
- None modified; this is a verification task. (The division-of-labor note was written into the
  skill in Task 1 and the register em-dash line in Task 2; this task confirms both.)

**Interfaces:**
- Consumes: the `ts-conventions` skill and the `ts-svelte-comments` register from Tasks 1 and 2.
- Produces: a recorded confirmation that an agent names a TS tell by number from the catalogue.

- [ ] **Step 1: Confirm the skill and register carry the gate, catalogue, and note**

```bash
S=~/.dotfiles/claude/.claude/skills/ts-conventions/SKILL.md
R=~/.dotfiles/claude/.claude/docs/voice/ts-svelte-comments.md
grep -q 'Comment-or-not' "$S" && echo "GATE OK" || echo "GATE MISSING"
grep -q 'division of labor' "$S" && echo "NOTE OK" || echo "NOTE MISSING"
grep -q 'TS tell catalogue' "$R" && echo "REGISTER CATALOGUE OK" || echo "REGISTER CATALOGUE MISSING"
grep -q 'Vale blocks it on' "$R" && echo "EM-DASH LINE OK" || echo "EM-DASH LINE MISSING"
```

Expected: `GATE OK`, `NOTE OK`, `REGISTER CATALOGUE OK`, `EM-DASH LINE OK`.

- [ ] **Step 2: Empirically confirm an agent names a TS tell**

Dispatch one `general-purpose` agent with this prompt:

> Read `~/.dotfiles/claude/.claude/skills/ts-conventions/SKILL.md` and
> `~/.dotfiles/claude/.claude/docs/voice/ts-svelte-comments.md` to load the §0 gate and the TS
> catalogue. Then review this TypeScript snippet as the `ts-conventions` reviewer would, citing
> each finding as `TS<n> at file:line` with the one-line avoidance rule. Snippet (`demo.ts`):
> ```ts
> /**
>  * This function adds two numbers.
>  * @param a {number} the first number
>  * @returns {number} the sum
>  */
> export function add(a: number, b: number): number { return a + b; }
> ```
> Return only the findings.

Expected: the agent cites TS1 (the `{type}` restatement) and TS3 (the "This function" opener),
each with its avoidance rule. The exact set is secondary; the point is the agent names tells by
number from the catalogue.

- [ ] **Step 3: Record the outcome**

No file changes. Note in the task's review that the agent returned numbered TS findings, which
confirms the feedforward layer is usable. If the agent returned prose without numbers, the
catalogue is not discoverable enough; revisit the skill's Output section before proceeding.

---

### Task 7: Record the TS arm as built, and merge the cairn branch

**Files:**
- Modify: `~/.dotfiles/claude/.claude/docs/authoring-charter.md` (the build-state line)

**Interfaces:**
- Consumes: everything above.
- Produces: a charter build-state line that names the TypeScript arm as live and points the next
  plan at Svelte; the cairn branch merged to `main`.

- [ ] **Step 1: Update the charter build-state line**

In `~/.dotfiles/claude/.claude/docs/authoring-charter.md`, in the Pointers section, replace the
bullet that begins "The Vale foundation is built and the Go comment arm is live" with:

```markdown
- The Vale foundation is built and the Go and TypeScript comment arms are live. The pinned
  binary, the split `glw907` overlay, the vendored baselines, the global config, and the fixture
  suite came first. poplar carries the Go arm; cairn is the first TypeScript adopter, with an
  in-tree `.vale.ini` linting `.ts` comment prose through a committed `glw907` copy, an
  `eslint.config.js` enforcing TSDoc structure on `src/lib`, and a `check:comments` CI gate. The
  `ts-conventions` skill and the expanded `ts-svelte-comments` register carry the TS1 through
  TS15 semantic tells. Svelte, Python, and the prose arm are the next plans.
```

- [ ] **Step 2: Confirm the charter still lints clean**

```bash
cd ~/.dotfiles
vale claude/.claude/docs/authoring-charter.md | tail -3
```

Expected: a clean or advisory-only run, no `error`-level findings.

- [ ] **Step 3: Commit the dotfiles change**

```bash
cd ~/.dotfiles
git add claude/.claude/docs/authoring-charter.md
git commit -m "Record the TypeScript comment arm as built in the charter" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

- [ ] **Step 4: Run cairn's full gate on the branch before merging**

The library source change is the comment-only conformance, so confirm the new gate, the existing
checks, and the type-check pass together:

```bash
cd ~/Projects/cairn-cms
npm run check:comments && npm run lint && npm run check
echo "exit: $?"
```

Expected: both green, exit 0.

- [ ] **Step 5: Merge the cairn branch to main**

```bash
cd ~/Projects/cairn-cms
git switch main
git merge --no-ff authoring/vale-ts-comment-arm \
  -m "Merge the Vale TypeScript comment arm adoption" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git branch -d authoring/vale-ts-comment-arm
```

Expected: a clean merge, the branch deleted. Leave the push to Geoff.

---

## Self-Review

Run after the last task.

1. **Skill present:** `ts-conventions/SKILL.md` carries the §0 gate, the TSDoc shape, the copy-in
   ESLint config, and the TS1 through TS15 catalogue (Task 1).
2. **Register expanded:** the `ts-svelte-comments` register carries the TS catalogue and the
   updated em-dash line crediting Vale (Task 2).
3. **Layer 2 holds:** the planted-tell proof fires `EmDash` and `Slop` on the comment line and
   nothing on the code line; real cairn TS carries no em dash in comments (Task 3).
4. **Layer 1 holds:** ESLint fires `no-types` and `tsdoc/syntax` on a planted `{type}` tag, and
   after the doc-comment conformance (Step 3b) the error tier is clean on real `src/lib`; the
   conformance is comment-only and svelte-check stays 0/0 (Task 4).
5. **Gate wired:** `npm run check:comments` runs ESLint and Vale, is green locally, and CI
   installs the pinned Vale binary before it (Task 5).
6. **Feedforward usable:** an agent given the skill and register names TS tells by number (Task 6).
7. **Charter accurate:** the build-state line names the TS arm as live and points at Svelte next;
   the cairn branch is merged to `main` (Task 7).
8. **Nothing else moved:** cairn's `check:prose`, spellcheck, and tidy are unchanged; the published
   `files` allowlist (`dist`, `src/lib`, `CHANGELOG.md`) excludes `eslint.config.js`, `.vale.ini`,
   and `.vale/`; `prose-guard` is untouched; the global Vale config is unchanged.
