# External-standards refactor (authoring plan 08)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax. This plan is run as a workflow, phase by phase, with the gate between tasks.

**Goal:** Refactor the authoring system to the external-standards model in `2026-06-22-authoring-standards-design.md`. Remove the `glw907` house overlay, the four tell catalogues, the Svelte extractor, and the personal-calibration framing. Re-anchor every register and conventions skill on its published external standard plus canonical exemplars. Then bring cairn's TypeScript and Svelte comments to professional-grade TSDoc.

**Architecture:** Two phases. Phase 1 refactors the dotfiles workstation config (the standard, the linters, the feedforward). Phase 2 refactors cairn and brings its comments to standard. Each phase is a workflow; the main loop reviews and verifies between tasks and between phases.

**Tech Stack:** Vale 3.15.1 with the vendored Google and Microsoft packages (the house `glw907` style is deleted), the language-native comment linters (gofmt/go vet, ESLint jsdoc + tsdoc, ruff `D`), Python 3.12 (the vale-hook and its test), and git in two repos.

## Global Constraints

- **External standards only.** After this refactor, comments and docs follow published external standards (Google, Microsoft, Go Doc Comments, TSDoc, PEP 257), agent-facing files follow Claude Code best practices, and commits follow Conventional Commits. Website content is the sole personal voice and lives in site repos, untouched here. No `glw907`, no tell catalogues, no per-model calibration.
- **dotfiles has no Vale-linted audience.** Its files are agent-facing (CLAUDE.md, skills, registers, planning docs) and Python scripts (comments to ruff `D`). So the dotfiles `.vale.ini`, the `glw907` style, the fixture suite, and `glw907-vendor.sh` are removed. The `vale-hook` stays globally wired; in dotfiles it finds no config and fails open, which is correct.
- **The vale-hook is live this session.** settings.json was re-read, so each Write/Edit is linted. Until Phase 1 task 1 removes the dotfiles `.vale.ini`, writes under `docs/**` and `claude/.claude/**` are still linted by Google + glw907; keep drafts clean (no filler, marketing, slop, or em dash) so the hook does not block.
- **Keep the green gates green.** cairn's `npm run check` (0/0) and `npm test` (exit 0) must pass after Phase 2; the comment changes are comment-only and must not alter behavior.
- Commit footer: `Co-Authored-By: Claude <noreply@anthropic.com>`. Stage only the files each task names.

---

## Phase 1: the dotfiles refactor

### Task 1: Remove the glw907 overlay and the Vale house infrastructure

**Files:**
- Delete: `vale/.config/vale/styles/glw907/` (all seven rule files)
- Delete: `vale/tests/` glw907 fixtures and configs (`*.bad.md`/`*.good.md` for the seven rules, `EmDashAllowed.good.md`, `comment-scope/`, `comment-scope.vale.ini`, `vale/tests/.vale.ini`); keep `microsoft/` and `microsoft.vale.ini` as the Microsoft-package vendor check, and reduce `run-fixtures.sh` to the Microsoft assertion only
- Delete: `scripts/glw907-vendor.sh` (no house overlay to vendor)
- Delete: `.vale.ini` (dotfiles has no Vale-linted audience)
- Modify: `scripts/check-py-comments.sh` (drop the Vale-on-`.py` step; keep ruff `D`)
- Modify: `tests/test_vale_hook.py` (drop the glw907-config integration tests; keep the unit tests for `new_text`, `changed_span`, `config_root`; the hook code itself is generic and unchanged)

- [ ] **Step 1: Remove the style, fixtures, vendor script, and `.vale.ini`**

```bash
cd ~/.dotfiles
git rm -r vale/.config/vale/styles/glw907
git rm vale/tests/.vale.ini vale/tests/comment-scope.vale.ini
git rm -r vale/tests/fixtures/comment-scope
git rm vale/tests/fixtures/BannedPhrases.bad.md vale/tests/fixtures/BannedPhrases.good.md \
  vale/tests/fixtures/EmDash.bad.md vale/tests/fixtures/EmDash.good.md vale/tests/fixtures/EmDashAllowed.good.md \
  vale/tests/fixtures/Filler.bad.md vale/tests/fixtures/Filler.good.md \
  vale/tests/fixtures/Judgment.bad.md vale/tests/fixtures/Judgment.good.md \
  vale/tests/fixtures/Marketing.bad.md vale/tests/fixtures/Marketing.good.md \
  vale/tests/fixtures/Openers.bad.md vale/tests/fixtures/Openers.good.md \
  vale/tests/fixtures/Slop.bad.md vale/tests/fixtures/Slop.good.md
git rm scripts/glw907-vendor.sh .vale.ini
```

- [ ] **Step 2: Reduce `run-fixtures.sh` to the Microsoft assertion**

Rewrite `vale/tests/run-fixtures.sh` to drop the `*.bad.*`/`*.good.*` glw907 loops and the comment-scope assertion, keeping only the Microsoft baseline assertion (the fixture raises `Microsoft.Wordiness`). It proves the vendored Microsoft package resolves.

- [ ] **Step 3: Simplify `check-py-comments.sh` to ruff `D` only**

Remove the `== vale on .py comment and docstring prose ==` block (Vale used glw907, now gone). Keep the ruff `D` block over tracked `.py` files and the extensionless bin scripts. Python comments now follow PEP 257 via ruff alone.

- [ ] **Step 4: Trim `tests/test_vale_hook.py`**

Remove the two `@needs_vale` integration tests (they wrote a glw907 config). Keep the unit tests for `new_text`, `changed_span`, `config_root`, and `non_markdown_is_skipped`. The hook code is unchanged.

- [ ] **Step 5: Verify and commit**

```bash
cd ~/.dotfiles
python3 -m pytest tests/test_vale_hook.py -q
( cd vale/tests && bash run-fixtures.sh )
bash scripts/check-py-comments.sh
grep -rl 'glw907' . | grep -v '\.git/' | grep -vE 'docs/superpowers/(plans|specs)/' || echo "glw907 gone from the active surface (history excepted)"
```

Expected: pytest passes; `fixtures: OK`; `check:py-comments OK`; the remaining glw907 references are only in the historical plans and specs and the prose docs that later tasks rewrite. Commit the deletions and edits.

### Task 2: Re-anchor the conventions skills on their external standards

Rewrite each conventions skill to "follow [the external standard]; the linter enforces structure; here are canonical exemplars," dropping the bespoke tell catalogues.

**Files:**
- Modify: `claude/.claude/skills/go-conventions/SKILL.md` (anchor on Go Doc Comments and Effective Go; the standard library is the exemplar; drop the T1-T43 catalogue references)
- Modify: `claude/.claude/skills/ts-conventions/SKILL.md` (TSDoc; ESLint jsdoc + tsdoc; well-regarded libraries; drop TS1-15)
- Modify: `claude/.claude/skills/svelte-conventions/SKILL.md` (TSDoc for `<script>`, the `@component` convention; drop S1-10)
- Modify: `claude/.claude/skills/python-conventions/SKILL.md` (PEP 257, PEP 8; ruff `D`; the standard library; drop T-P1-13)
- Delete: `claude/.claude/docs/go-comment-voice.md` (the T1-T43 catalogue) and `claude/.claude/docs/voice/ts-svelte-comments.md` and `claude/.claude/docs/voice/python-comments.md` (the catalogues live here), folding a short principles note into each skill: comment the why, document the contract, do not paraphrase the code, with a pointer to the standard and the stdlib

- [ ] **Step 1: Rewrite the four skills, delete the catalogues, verify no catalogue reference dangles, commit.** Each skill: the standard, the linter, the canonical exemplar source, and the short principles note. Confirm with `grep -rlE 'T1-T43|TS1-15|S1-10|T-P1' claude/` returns nothing.

### Task 3: Re-anchor the registers on external standards and canonical exemplars

**Files:**
- Modify: `claude/.claude/docs/voice/technical-doc-go.md` and `technical-doc-web.md` (Google standard; exemplars from Google's own docs; drop glw907 and the personal-calibration framing)
- Modify: `claude/.claude/docs/voice/editor.md` (Microsoft standard; exemplars from Microsoft Learn; drop the "Geoff's passages replace the placeholders" loop)
- Modify: `claude/.claude/docs/voice/agent-facing.md` (Anthropic / Claude Code best practices; exemplars from Anthropic's docs)
- Modify: `claude/.claude/docs/voice/commit-and-pr.md` (Conventional Commits and the git canon; exemplars)
- Delete: `claude/.claude/docs/voice/calibration-2026-06-09.md` (stale, Fable-era, personal)

- [ ] **Step 1: Rewrite the registers to lead on the standard and canonical exemplars, delete the calibration file, commit.** Each register names its external standard and carries three to five canonical exemplars of that standard with a one-line reason, no personal-voice or calibration language.

### Task 4: Update the router, output style, and CLAUDE.md to the external-standards framing

**Files:**
- Modify: `claude/.claude/skills/writing-voice/SKILL.md` (the router points each audience to its external standard and that standard's exemplars; drop the em-dash matrix, since the em dash follows each external standard; drop glw907 references)
- Modify: `claude/.claude/output-styles/writing-voice.md` (the Claude-best-practices feedforward: name the audience, load its standard's exemplars, draft, reread; drop glw907 references and the house-lexicon framing)
- Modify: `claude/.claude/CLAUDE.md` (the "## Writing voice" section to the external-standards framing; drop glw907)

- [ ] **Step 1: Update the three files, commit.** Confirm `grep -rl glw907 claude/` returns nothing.

### Task 5: Update the setup docs

**Files:**
- Modify: `docs/new-machine.md`, `README.md`, `git/.gitconfig`, `secrets/registry.md` (remove the glw907 vendor and house-overlay setup steps; the Vale setup is now `vale sync` of the Google and Microsoft packages per repo)

- [ ] **Step 1: Update the setup references, commit.** Confirm `grep -rl glw907 . | grep -v '\.git/' | grep -vE 'docs/superpowers/(plans|specs)/'` returns nothing (only history retains glw907).

---

## Phase 2: cairn

### Task 6: Refactor cairn's Vale and comment tooling to external standards

**Files (in `~/Projects/cairn-cms`):**
- Modify: `.vale.ini` (developer docs to the Google package, the editor surface to the Microsoft package, drop glw907 and the comment-format scoping)
- Delete: `scripts/check-svelte-comments.mjs` (the Svelte extractor; the `<script>` block follows TSDoc through ESLint, the `@component` block follows the Svelte convention)
- Delete: the vendored `glw907` style copy under `.vale/styles/`
- Modify: `package.json` `check:comments` (ESLint jsdoc + tsdoc only for comments; Vale runs against the docs, not comments)
- Modify: `eslint.config.js`: confirm the tsdoc rule stays, add `eslint-plugin-jsdoc`'s `informative-docs` rule (flags a comment that only restates the name), and add an em-dash-in-comments ban (a small local rule over comment tokens via `no-restricted-syntax` or a tiny custom rule; the one published em-dash plugin is an obscure v1.0.0, so prefer the local rule)
- Modify: `CLAUDE.md` (the authoring section to the external-standards model)

- [ ] **Step 1: Refactor the config, delete the extractor and the vendored overlay, update CLAUDE.md, run the gate (`npm run check`, `npm run check:comments`), commit.**

### Task 7: Bring cairn's TypeScript and Svelte comments to professional-grade TSDoc

This is the fan-out. For each batch of cairn's `src/lib` TypeScript and Svelte files, review the comments against professional TSDoc (and the Svelte `@component` convention), rewrite any that fall short, and verify.

- [ ] **Step 1: Enumerate the files.** `git -C ~/Projects/cairn-cms ls-files 'src/lib/**/*.ts' 'src/lib/**/*.svelte'`.
- [ ] **Step 2: Pipeline each file: review the comments against professional TSDoc, rewrite the substandard ones (comment the contract and the why, drop paraphrase comments, correct TSDoc tags), and confirm `npx eslint` on the file is clean.** Comment-only changes; no behavior change.
- [ ] **Step 3: Run the full cairn gate (`npm run check` 0/0, `npm test` exit 0), then commit in reviewable batches.**

---

## Self-Review

1. `glw907` is gone from both repos' active surface (history excepted), and every register and skill names its external standard.
2. The conventions skills carry the standard, the linter, the exemplar source, and the short principles note, with no tell catalogue.
3. The docs registers carry canonical Google and Microsoft exemplars with no calibration loop.
4. The dotfiles `.vale.ini`, the glw907 style, the fixtures, and `glw907-vendor.sh` are removed; pytest, the Microsoft fixture, and check-py-comments pass.
5. cairn's `npm run check` and `npm test` are green; its comments read as professional-grade TSDoc; the extractor and the vendored overlay are gone.
6. The vale-hook still runs Vale against each repo's external-package config and fails open where there is none.
