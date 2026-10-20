# Svelte Comment Arm Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring Svelte comments under the charter. A single extractor pulls the `@component` block and the `<script>`-block comments from each `.svelte` file and lints that prose through the vendored `glw907` overlay, so the em dash and the lexicon are caught in both comment homes and the component's editor-facing product copy is never touched. The same extractor enforces the structural rule (exactly one `@component`, with prose). A new `svelte-conventions` skill and the S1 through S10 catalogue in the `ts-svelte-comments` register carry the semantic tells. Proven against cairn `src/lib/components`.

**Architecture:** The cairn pilot disproved the spec's `[formats] svelte = html` plan: Vale's `html` format skips `<!-- -->` comments (so it misses `@component`) and scans the visible markup text (so it leaks into product copy that `check:prose` owns). The fix is `scripts/check-svelte-comments.mjs`, an extractor in the shape of the existing `scripts/check-admin-prose.mjs`. For each component it finds the `@component` HTML comment and the `//`, `/*`, and `/**` comments inside `<script>`, writes them to a per-file temp Markdown buffer that preserves line numbers, and runs Vale `glw907` over the buffer through a self-contained temp config. It also asserts each component has at most one `@component` block and that the block carries a sentence. `eslint-plugin-svelte`'s a11y and reactivity rules are a separate concern (cairn already runs svelte-check and a DaisyUI/a11y reviewer) and are out of scope here.

**Tech Stack:** Vale 3.15.1 (errata-ai/vale), Node 22 ESM (the cairn `scripts/*.mjs` convention), the hand-written `glw907` Vale style, the cairn SvelteKit repo, and a new `svelte-conventions` skill.

## Global Constraints

- Vale is pinned to `3.15.1`; the binary is `~/.local/bin/vale`. The em dash stays banned in Svelte comments; no opt-out section is added.
- The canonical `glw907` style lives at `~/.dotfiles/vale/.config/vale/styles/glw907`. cairn already carries a committed copy at `.vale/styles/glw907` (vendored in plan 03); this plan reuses it and adds no new vendoring.
- The extractor lints comments only: the `@component` block and the `<script>`-block comments. It never lints the component's markup text, which is cairn's editor product copy and is `check:prose`'s job. This separation is load-bearing; do not widen the extractor to markup.
- The structural rule: a component has at most one `@component` block (the Svelte LSP surfaces only the last, so a second is a silent footgun), and a present block carries at least one sentence of prose. Zero `@component` blocks is allowed; presence stays a Claude-gate decision, not a hard rule.
- `eslint-plugin-svelte` is deferred. Its recommended rules need the TypeScript sub-parser wired (27 of cairn's 30 components fail to parse without it) and would carry an a11y and reactivity conformance unrelated to comment standards. cairn's svelte-check and the `daisyui-a11y-reviewer` cover that ground; revisit in a later pass if a deterministic a11y gate is wanted.
- The `check:comments` gate gains the Svelte extractor alongside the TypeScript eslint and Vale steps from plan 03. cairn's `package.json` `files` allowlist is `["dist","src/lib","CHANGELOG.md"]`, so `scripts/`, `.vale.ini`, and `.vale/` are not published.
- This plan does not touch `prose-guard`. It stays the active hook until the cutover plan (07).
- dotfiles changes commit to dotfiles `main`. cairn changes land on a branch off `main` and merge back when the gate is green. Leave the push to Geoff.
- Commit footer on both repos: `Co-Authored-By: Claude <noreply@anthropic.com>`.

## The plan series

This is plan 04 of the authoring-system build. Plans 01 (Vale foundation), 02 (Go arm), and 03 (TypeScript arm) are done and committed on dotfiles `main`; poplar carries the Go arm and cairn carries the TypeScript arm.

1. **Vale foundation** (done).
2. **Go comment arm** (done): poplar.
3. **TypeScript comment arm** (done): cairn, the ESLint jsdoc/tsdoc flat config, Vale on `.ts` comments, the `ts-conventions` skill, the TS1 through TS15 catalogue, the `check:comments` gate.
4. **Svelte comment arm** (this plan): the `check-svelte-comments.mjs` extractor (the `@component` and script-block comment net plus the structural rule), the `svelte-conventions` skill, the S1 through S10 catalogue. Prove against cairn `src/lib/components`.
5. **Python comment arm:** the `ruff` `D` config, the `py` Vale format, the `python-conventions` skill, the `python-comments` register, the T-P1 through T-P13 catalogue.
6. **Prose arm:** the Google and Microsoft baselines on docs and content per glob, the prose registers, the PostToolUse prose Vale hook.
7. **Cutover:** wire the Vale hook, retire `prose-guard`, rewrite the output style and the CLAUDE.md writing-voice section, repoint the router. Sequence step 5 (wire `/simplify` to name TS, S, and T-P tells by number) lands here.

The source specs are `~/.dotfiles/docs/superpowers/specs/2026-06-22-ai-drafting-prose-system-design.md` (prose) and `~/.dotfiles/docs/superpowers/specs/2026-06-22-code-comment-standards-design.md` (comments). The umbrella is `~/.claude/docs/authoring-charter.md`.

---

### Task 1: The `svelte-conventions` skill

Create the layer-3 skill for Svelte, mirroring `ts-conventions`: the write-time gate, the two-homes rule (`@component` versus typed props), and the S1 through S10 catalogue. The `ts-svelte-comments` register stays the prose authority and gains the S catalogue in Task 2.

**Files:**
- Create: `~/.dotfiles/claude/.claude/skills/svelte-conventions/SKILL.md`

**Interfaces:**
- Produces: the `svelte-conventions` skill, carrying the §0 gate, the two-homes rule, and the S1 through S10 catalogue the `/simplify` lens will cite by number in a later step.

- [ ] **Step 1: Write the failing check**

```bash
test -f ~/.dotfiles/claude/.claude/skills/svelte-conventions/SKILL.md && echo PASS || echo FAIL
```

Expected: `FAIL`.

- [ ] **Step 2: Create the skill**

```bash
mkdir -p ~/.dotfiles/claude/.claude/skills/svelte-conventions
```

Write `~/.dotfiles/claude/.claude/skills/svelte-conventions/SKILL.md` with exactly this content:

````markdown
---
name: svelte-conventions
description: >
  Mandatory rules for writing Svelte component comments on this workstation.
  Use before writing, reviewing, or modifying any `.svelte` `@component` block
  or script-block comment. Covers the write-time comment-or-not gate, the
  two-homes rule (`@component` carries purpose plus contract plus failure
  mode; props speak through their typed JSDoc), and the S1 through S10
  AI-tell catalogue. The prose authority is the ts-svelte-comments register.
---

# Svelte Comment Conventions

The reader is a coder or an agent already looking at the component. This skill is the Svelte arm
of the authoring charter (`~/.claude/docs/authoring-charter.md`). The deeper prose authority, with
exemplars from the SvelteKit and cairn source, is the `ts-svelte-comments` register at
`~/.claude/docs/voice/ts-svelte-comments.md`; load it before writing or reviewing comments. The
TypeScript tells (TS1 through TS15, the `ts-conventions` skill) apply to the `<script>` block; the
S-tells below specialize them for Svelte.

## §0: Comment-or-not (write-time gate)

```
(a) Does the markup, the rune, or the typed prop already say this?
(b) Is the why obvious from the next 5 lines or fewer?
(c) Would a reader otherwise miss a hidden constraint, an ordering
    requirement, a browser quirk, or a failure mode?
```

Skip on (a) or (b). Write only for (c). Markup nesting, handler names, and `bind:` are visible, so
they get no narration. A rune declares its own dependency; comment only a non-obvious why.

## The two-homes rule

A component has two comment homes, and they do not overlap. This is the load-bearing rule.

- The `@component` HTML comment carries the component's purpose, its contract, and its failure
  mode, in prose. The Svelte language server surfaces it on hover at the import site. Exactly one
  per file: the LSP reads only the last, so a second `@component` is a silent footgun.
- Prop docs live on the typed `Props` interface members as JSDoc, never in `@component`. The type
  states the prop's type; the JSDoc adds only the constraint, the fallback, or the why. Duplicating
  props into `@component` creates two sources of truth that drift.

State behavior and the failure mode in `@component`, never a template walkthrough.

## §catalogue: the S1 through S10 AI-tell catalogue

Each tell: id, name, the mechanical avoidance rule. Full prose is in the `ts-svelte-comments`
register. The S-tells specialize the Go and TS tells they extend; when both apply, cite the most
specific (S2 over a TS paraphrase tell for a reactive line, S5 over it for a rune, S4 for a
template banner). Cite as `S<n> at file:line`.

| id | name | rule |
|---|---|---|
| S1 | `@component` restating every typed prop | `@component` is purpose plus contract plus failure mode; props speak through their JSDoc |
| S2 | narrating a reactive declaration | the rune declares the dependency; comment only a non-obvious why |
| S3 | over-commenting markup structure | markup nesting is visible; a template comment earns its place only for a why |
| S4 | redundant template section banners | delete a `<!-- header -->` banner unless it carries a constraint |
| S5 | commenting standard rune idioms | never explain what a rune does; comment only an unusual use |
| S6 | file-header boilerplate | the editor shows the filename; fold real content into `@component` |
| S7 | prop JSDoc restating the type | the type says the type; the doc adds the why or nothing |
| S8 | narrating handlers and bindings | the handler name and `bind:` are self-describing |
| S9 | `untrack`/snapshot under- or over-commented | one line of why is correct here; not zero, not a paragraph |
| S10 | uniform `@component` shape across the set | vary opener and length with each component's surface |

## Tooling and the division of labor

- `scripts/check-svelte-comments.mjs` (cairn) is the deterministic net: it extracts the `@component`
  block and the `<script>`-block comments and runs Vale `glw907` over them, catching the em dash and
  the banned lexicon, and it enforces the structural rule (at most one `@component`, with prose). It
  never scans the component's markup text, which is `check:prose`'s product-copy surface.
- This skill and the register own the semantic S-tells the extractor cannot see: the paraphrase, the
  prop restated into `@component`, the rune narrated, the uniform shape across the set.

## Output

When reviewing, cite each finding as `S<n> at file:line` with the avoidance rule. When writing, run
the §0 gate, then the two-homes rule, then write only what survives.
````

- [ ] **Step 3: Re-run the check and confirm content**

```bash
S=~/.dotfiles/claude/.claude/skills/svelte-conventions/SKILL.md
test -f "$S" && echo PASS || echo FAIL
grep -q 'two-homes rule' "$S" && echo "TWO-HOMES OK" || echo "MISSING"
grep -qE 'S1 \||S10 \|' "$S" && echo "CATALOGUE OK" || echo "MISSING"
```

Expected: `PASS`, `TWO-HOMES OK`, `CATALOGUE OK`.

- [ ] **Step 4: Lint the skill clean and commit**

```bash
cd ~/.dotfiles && vale --minAlertLevel=error claude/.claude/skills/svelte-conventions/SKILL.md | tail -2
git add claude/.claude/skills/svelte-conventions/SKILL.md
git commit -m "Add the svelte-conventions skill for the Svelte comment arm" \
  -m "Carries the write-time gate, the two-homes rule, and the S1 through S10 catalogue. The ts-svelte-comments register stays the prose authority." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: a clean or advisory-only Vale run, then the commit.

---

### Task 2: Add the S1 through S10 catalogue to the register

The `ts-svelte-comments` register is the shared prose authority for TS and Svelte. It already holds
the cairn `@component` exemplar. Add the S catalogue as prose so the register is the single home of
the expanded Svelte tells.

**Files:**
- Modify: `~/.dotfiles/claude/.claude/docs/voice/ts-svelte-comments.md`

**Interfaces:**
- Consumes: the S1 through S10 ids from the Task 1 skill.
- Produces: the register section the `svelte-conventions` skill points at.

- [ ] **Step 1: Append the catalogue section**

Add this section to the end of `~/.dotfiles/claude/.claude/docs/voice/ts-svelte-comments.md`:

````markdown
## The Svelte tell catalogue (S1 through S10)

The numbered tells the `svelte-conventions` skill cites. The S-tells specialize the TS tells for
Svelte's two comment homes.

| id | name | rule |
|---|---|---|
| S1 | `@component` restating every typed prop | `@component` is purpose plus contract plus failure mode; props speak through their JSDoc |
| S2 | narrating a reactive declaration | the rune declares the dependency; comment only a non-obvious why |
| S3 | over-commenting markup structure | markup nesting is visible; a template comment earns its place only for a why |
| S4 | redundant template section banners | delete a `<!-- header -->` banner unless it carries a constraint |
| S5 | commenting standard rune idioms | never explain what a rune does; comment only an unusual use |
| S6 | file-header boilerplate | the editor shows the filename; fold real content into `@component` |
| S7 | prop JSDoc restating the type | the type says the type; the doc adds the why or nothing |
| S8 | narrating handlers and bindings | the handler name and `bind:` are self-describing |
| S9 | `untrack`/snapshot under- or over-commented | one line of why is correct here; not zero, not a paragraph |
| S10 | uniform `@component` shape across the set | vary opener and length with each component's surface |

S1, the prop restated into `@component`. The type already declares it; `@component` carries the
why, and the prop's own JSDoc carries the constraint:

```svelte
<!-- off-voice: @component lists each prop and its type -->
<!--
@component
A toolbar. Props: actions (an array of Action), compact (a boolean), onpick (a callback).
-->
<!-- in-voice: @component is purpose plus failure mode; props speak through their JSDoc -->
<!--
@component
The editor's formatting toolbar. Renders nothing when actions is empty, which is the
intended empty state, not a bug.
-->
  interface Props {
    /** Falls back to the compact layout under 480px. */
    compact?: boolean;
  }
```

S2, the reactive declaration narrated. The rune already states the dependency:

```svelte
<!-- off-voice -->
// recompute the total when items changes
let total = $derived(items.reduce((a, b) => a + b.price, 0));
<!-- in-voice: silence, or a why the rune cannot show -->
let total = $derived(items.reduce((a, b) => a + b.price, 0));
```

S4, the template section banner. Delete it unless it carries a constraint:

```svelte
<!-- off-voice -->
<!-- Header -->
<header>...</header>
<!-- in-voice: a banner only when it warns -->
<!-- Keep this above the dialog: the focus trap reads the first heading. -->
<header>...</header>
```
````

- [ ] **Step 2: Confirm and commit**

```bash
cd ~/.dotfiles
grep -q 'Svelte tell catalogue' claude/.claude/docs/voice/ts-svelte-comments.md && echo "SECTION OK" || echo "MISSING"
vale --minAlertLevel=error claude/.claude/docs/voice/ts-svelte-comments.md | tail -2
git add claude/.claude/docs/voice/ts-svelte-comments.md
git commit -m "Add the S1 through S10 catalogue to the ts-svelte-comments register" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: `SECTION OK`, a clean Vale run, the commit.

---

### Task 3: The Svelte comment extractor and gate

Build `scripts/check-svelte-comments.mjs`. It extracts the `@component` block and the `<script>`-block
comments from each component, lints that prose through Vale `glw907`, and enforces the structural
rule. Then fold it into `check:comments` so CI runs it. Prove against cairn's real components and a
planted tell.

**Files:**
- Create: `~/Projects/cairn-cms/scripts/check-svelte-comments.mjs`
- Modify: `~/Projects/cairn-cms/scripts/check-comments.sh` (add the Svelte step)

**Interfaces:**
- Consumes: the vendored `glw907` style at `.vale/styles/glw907`; the pinned Vale binary.
- Produces: `node scripts/check-svelte-comments.mjs` exits non-zero on a structural violation or a Vale error in a component comment; `check:comments` runs it after the TypeScript steps.

- [ ] **Step 1: Branch cairn off main**

```bash
cd ~/Projects/cairn-cms
git switch -c authoring/vale-svelte-comment-arm
git status --short
```

Expected: a clean working tree on the new branch.

- [ ] **Step 2: Write the extractor**

Create `~/Projects/cairn-cms/scripts/check-svelte-comments.mjs`:

```js
// cairn-cms: the Svelte comment gate. Vale's .svelte handling reaches neither comment home cleanly
// (the html format skips <!-- --> and the script comments live in a code block), and it leaks into
// the component's product copy, which check:prose owns. So this extractor pulls only the comment
// regions, the @component block and the <script>-block comments, into a per-file Markdown buffer
// that preserves line numbers, and runs Vale glw907 over the buffer. It also enforces the structural
// rule: at most one @component block, and a present block carries a sentence.
//
//   node scripts/check-svelte-comments.mjs    extract, lint, and fail on a structural or Vale error
import { readFileSync, writeFileSync, mkdtempSync, rmSync, readdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';
import { execFileSync } from 'node:child_process';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const COMPONENTS_DIR = join(ROOT, 'src', 'lib', 'components');
const STYLES = join(ROOT, '.vale', 'styles');

// Return the 0-based line spans of comment text to keep, as [line, text] pairs.
function extractComments(src) {
  const lines = src.split('\n');
  const kept = []; // [lineIndex, text]
  let componentBlocks = 0;
  let componentHasProse = false;

  // HTML comments, including @component.
  const htmlRe = /<!--([\s\S]*?)-->/g;
  let m;
  while ((m = htmlRe.exec(src)) !== null) {
    const isComponent = /(^|\s)@component(\s|$)/m.test(m[1]);
    const startLine = src.slice(0, m.index).split('\n').length - 1;
    const body = m[1].split('\n');
    if (isComponent) {
      componentBlocks += 1;
      body.forEach((t, i) => {
        const clean = t.replace(/@component/, '').trim();
        if (clean) { kept.push([startLine + i, clean]); componentHasProse = true; }
      });
    } else {
      body.forEach((t, i) => { if (t.trim()) kept.push([startLine + i, t.trim()]); });
    }
  }

  // Script-block comments: // line, /* */ and /** */ block, inside <script>...</script>.
  const scriptRe = /<script\b[^>]*>([\s\S]*?)<\/script>/g;
  while ((m = scriptRe.exec(src)) !== null) {
    const scriptStart = src.slice(0, m.index).split('\n').length - 1;
    const scriptLines = m[1].split('\n');
    let inBlock = false;
    scriptLines.forEach((line, i) => {
      const lineNo = scriptStart + i; // 0-based source line, consistent with the HTML path
      let text = '';
      if (inBlock) {
        const end = line.indexOf('*/');
        text = (end === -1 ? line : line.slice(0, end)).replace(/^\s*\*?/, '').trim();
        if (end !== -1) inBlock = false;
      } else {
        const lineComment = line.match(/\/\/(.*)$/);
        const blockOpen = line.match(/\/\*\*?(.*)$/);
        if (lineComment) text = lineComment[1].trim();
        else if (blockOpen) {
          const end = blockOpen[1].indexOf('*/');
          text = (end === -1 ? blockOpen[1] : blockOpen[1].slice(0, end)).replace(/^\*?/, '').trim();
          if (end === -1) inBlock = true;
        }
      }
      if (text) kept.push([lineNo, text]);
    });
  }

  return { kept, componentBlocks, componentHasProse };
}

const files = readdirSync(COMPONENTS_DIR).filter((f) => f.endsWith('.svelte')).sort();
const tmp = mkdtempSync(join(tmpdir(), 'cairn-svelte-'));
// The temp config mirrors cairn's .ts policy: glw907.Judgment is advisory (it over-fires on
// legitimate technical vocab, e.g. a "dedicated" icon), so it never gates the comment text.
writeFileSync(join(tmp, '.vale.ini'),
  `StylesPath = ${STYLES}\nMinAlertLevel = suggestion\n[*.md]\nBasedOnStyles = glw907\nglw907.Judgment = suggestion\n`);

let fail = 0;
const lineMaps = {}; // mdFile -> { component, lineForMdLine: {mdLine: srcLine} }

for (const f of files) {
  const src = readFileSync(join(COMPONENTS_DIR, f), 'utf8');
  const { kept, componentBlocks, componentHasProse } = extractComments(src);

  if (componentBlocks > 1) {
    console.error(`STRUCTURE: ${f} has ${componentBlocks} @component blocks; the LSP reads only the last. Keep one.`);
    fail = 1;
  }
  if (componentBlocks === 1 && !componentHasProse) {
    console.error(`STRUCTURE: ${f} has an empty @component block; give it a sentence or remove it.`);
    fail = 1;
  }

  // Build a line-preserving Markdown buffer: each kept comment sits on its source line.
  const total = src.split('\n').length;
  const buf = new Array(total).fill('');
  const md2src = {};
  for (const [lineIdx, text] of kept) { buf[lineIdx] = text; md2src[lineIdx + 1] = lineIdx + 1; }
  const mdName = `${f}.md`;
  writeFileSync(join(tmp, mdName), buf.join('\n'));
  lineMaps[mdName] = { component: f, md2src };
}

// One Vale run over all extracted buffers, error level only.
let valeOut = '';
try {
  valeOut = execFileSync('vale', ['--config', join(tmp, '.vale.ini'), '--minAlertLevel=error', '--output=line', tmp],
    { encoding: 'utf8' });
} catch (e) {
  valeOut = (e.stdout || '') + (e.stderr || ''); // vale exits non-zero when it finds something
}

for (const line of valeOut.split('\n')) {
  const mm = line.match(/([^/\s]+\.svelte\.md):(\d+):\d+:(.+)/);
  if (!mm) continue;
  const map = lineMaps[mm[1]];
  if (!map) continue;
  console.error(`VALE: ${map.component}:${mm[2]} ${mm[3].trim()}`);
  fail = 1;
}

rmSync(tmp, { recursive: true, force: true });
console.log(fail === 0 ? 'check:svelte-comments OK' : 'check:svelte-comments FAILED');
process.exit(fail);
```

- [ ] **Step 3: Proof A, real cairn component comments are clean**

```bash
cd ~/Projects/cairn-cms
node scripts/check-svelte-comments.mjs
echo "exit: $?"
```

Expected at first run: two real Filler findings the pilot already located in
`CairnTidySettings.svelte` comments at lines 11 and 518, each the filler word in `the editor tier is
... ABSENT` and `The convention list is ... absent`. Cut the filler word (it is throat-clearing; the
sentence reads stronger without it), commit the cleanup on its own (`git add
src/lib/components/CairnTidySettings.svelte && git commit -m "Clean two filler tells in a Svelte
comment"`), then re-run until `check:svelte-comments OK`, exit 0. Any other `VALE:` line is a real
finding to clean the same way. A `STRUCTURE:` line means a component has two `@component` blocks or an
empty one; fix the component.

- [ ] **Step 4: Proof B, a planted tell fires on a comment and not on markup**

The extractor scans the components directory top-level, so the proof file lands there directly, then
gets removed. The em dash is written from its bytes so the literal stays out of the repo:

```bash
cd ~/Projects/cairn-cms
printf '<!--\n@component\nA seamless widget %s built for editors.\n-->\n<script lang="ts">\n  // a tapestry of helpers\n  let label = "Delve into your drafts";\n</script>\n<button>Delve into the editor</button>\n' \
  "$(printf '\xe2\x80\x94')" > src/lib/components/ZZProof.svelte
node scripts/check-svelte-comments.mjs 2>&1 | grep 'ZZProof' || true
rm -f src/lib/components/ZZProof.svelte
```

Expected: the run reports an `EmDash` and a `Slop` finding at `ZZProof.svelte:3` (the planted em dash
and slop word in the `@component` block) and a `Slop` finding at `ZZProof.svelte:6` (the script
comment), and reports NOTHING for line 7 (the `label` string) or line 9 (the button text), proving the
extractor lints comments and never the product copy that `check:prose` owns. Remove the proof file.
The pilot ran exactly this and saw those three findings and no markup or string finding.

- [ ] **Step 5: Fold the extractor into `check:comments`**

In `~/Projects/cairn-cms/scripts/check-comments.sh`, add the Svelte step before the final summary
(after the Vale block):

```bash
echo "== svelte comment extractor (@component + script comments) =="
node scripts/check-svelte-comments.mjs || fail=1
```

- [ ] **Step 6: Run the full gate and commit**

```bash
cd ~/Projects/cairn-cms
npm run check:comments
echo "exit: $?"
git add scripts/check-svelte-comments.mjs scripts/check-comments.sh
git commit -m "Add the Svelte comment extractor to the check:comments gate" \
  -m "Extracts the @component block and the script-block comments, lints them through glw907, and enforces the one-@component structural rule; never touches the component's product copy." \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: `check:comments OK`, exit 0, then the commit. If Proof A surfaced a real comment to clean,
its source fix is a separate `git add src/lib/components && git commit` with a "Clean a Svelte comment
tell" message before this commit.

---

### Task 4: Record the Svelte arm as built, and merge

**Files:**
- Modify: `~/.dotfiles/claude/.claude/docs/authoring-charter.md` (the build-state line and the Svelte feedback cell)

**Interfaces:**
- Produces: a charter that names the Svelte arm as live and points the next plan at Python; the cairn branch merged.

- [ ] **Step 1: Confirm the feedforward layer names an S-tell**

Dispatch one `general-purpose` agent: "Read `~/.dotfiles/claude/.claude/skills/svelte-conventions/SKILL.md`
and `~/.dotfiles/claude/.claude/docs/voice/ts-svelte-comments.md`. Review this component as the
svelte-conventions reviewer, citing each finding as `S<n> at file:line`. Component (`Demo.svelte`):
a `@component` block that lists every prop and type, plus a `// recompute when items change` comment
above a `$derived`. Return only the findings." Expected: the agent cites S1 (props restated into
`@component`) and S2 (reactive declaration narrated). Record the outcome.

- [ ] **Step 2: Update the charter build-state line and the Svelte cell**

In `~/.dotfiles/claude/.claude/docs/authoring-charter.md`, in the standing-audiences table, change
the Svelte feedback cell to `the check-svelte-comments extractor (Vale on @component + script
comments) + Vale on .ts`. Then replace the build-state bullet that begins "The Vale foundation is
built and the Go and TypeScript comment arms are live" so it names the Svelte arm too: cairn carries
the Svelte arm through `scripts/check-svelte-comments.mjs`, the extractor that lints the `@component`
block and the script-block comments through `glw907` and enforces the one-`@component` rule, with the
`svelte-conventions` skill and the S catalogue for the semantic tells. End with "Python and the prose
arm are the next plans."

- [ ] **Step 3: Lint clean and commit the charter**

```bash
cd ~/.dotfiles
vale --minAlertLevel=error claude/.claude/docs/authoring-charter.md | tail -2
git add claude/.claude/docs/authoring-charter.md
git commit -m "Record the Svelte comment arm as built in the charter" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

- [ ] **Step 4: Run cairn's full gate on the branch, then merge**

```bash
cd ~/Projects/cairn-cms
npm run check:comments && npm run check
git switch main
git merge --no-ff authoring/vale-svelte-comment-arm \
  -m "Merge the Vale Svelte comment arm adoption" \
  -m "Co-Authored-By: Claude <noreply@anthropic.com>"
git branch -d authoring/vale-svelte-comment-arm
```

Expected: the gate green and svelte-check 0/0, then a clean merge and the branch deleted. Leave the
push to Geoff.

---

## Self-Review

Run after the last task.

1. **Skill present:** `svelte-conventions/SKILL.md` carries the §0 gate, the two-homes rule, and the S1 through S10 catalogue (Task 1).
2. **Register expanded:** the `ts-svelte-comments` register carries the S catalogue (Task 2).
3. **Extractor scopes correctly:** the planted-tell proof fires on the `@component` block and the script comment and NOT on the markup text or a code string (Task 3 Step 4); real cairn component comments are clean (Step 3).
4. **Structural rule holds:** the extractor fails a component with two `@component` blocks or an empty one (Task 3 Step 2 logic, exercised by the proof).
5. **Gate wired:** `check:comments` runs the extractor after the TypeScript steps and is green (Task 3 Step 6).
6. **Feedforward usable:** an agent given the skill and register names S-tells by number (Task 4 Step 1).
7. **Charter accurate:** the build-state line names the Svelte arm as live and points at Python; the branch is merged (Task 4).
8. **Nothing else moved:** `eslint-plugin-svelte` is deliberately deferred; the extractor never lints markup; cairn's `check:prose`, spellcheck, and tidy are unchanged; `prose-guard` is untouched.
