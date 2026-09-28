# Claude infra audit (2026-09-28)

Read-only audit of the workstation's Claude Code infra: agents, workflows, process skills,
convention skills, workstation docs, and the CLAUDE.md files of the workstation and the in-scope
repos. Four area readers verified their findings against the files. This synthesis dedupes them,
confirms the cross-area restatements by grep, groups root causes, proposes a mechanical guard,
and triages every finding into passes. Nothing was changed.

The owner's instruction for this run: audit first, then execute the style-guide-sync plan
(`~/Projects/cairn-cms/.claude/worktrees/style-guide-sync/docs/superpowers/plans/2026-09-28-style-guide-sync.md`)
on corrected infra. The triage therefore splits the work into what must land before that plan and
what waits until it closes.

## 1. Counts

Raw findings from the four areas: 95 (agents-workflows 24, process-skills 27, convention-skills
16, docs-claudemd 28). Four were refuted by the area verifiers and are not counted.

Seven defects were reported by two or three areas. After merging them, 87 unique findings remain.

| | high | medium | low | total |
|---|---|---|---|---|
| correctness | 4 | 22 | 41 | 67 |
| duplication | 0 | 2 | 8 | 10 |
| efficiency | 0 | 3 | 7 | 10 |
| **total** | **4** | **27** | **56** | **87** |

Eight unique findings are owned by the style-guide-sync plan (section 6). The other 79 are
triaged into passes in section 8.

Cross-area merges (the first ID is canonical below):

| Canonical | Merged | Defect |
|---|---|---|
| DC-01 | PS-13 | code-simplifier per commit (global CLAUDE.md) against once per pass (pass-core) |
| DC-03 | PS-16 | "the repo's full gate" per task against the pass-class per-task gate |
| AW-11 | PS-23 | PASS_CLASSES kept in step by hand across two runners and pass-core |
| DC-21 | PS-24 | global CLAUDE.md "Conducting a pass" restates pass-core |
| DC-22 | PS-26 | visual-fidelity method restated in cairn and site CLAUDE.md files |
| DC-10 | CS-14 | `bubbletea-conventions.md`: duplicate of elm-conventions, dead links, tmux verification |
| AW-24 | DC-26, CS-15 | tell list and em-dash policy restated beside the always-on output style |

DC-24 (`golang-spf13-cobra` absent from the skill listing) is resolved by CS-17's evidence: the
vendored skill carries `paths: ["**/*.go"]`, so it lists only once a `.go` file is in play. The
residual defect is wording: cairn CLAUDE.md calls it mandatory without saying it is path-gated.

## 2. Root causes

**RC1. Rules restated instead of routed.** A rule is written into every file that might need it,
then kept in step by a "keep in sync" comment. The copies drift, and the drift is the defect. The
two runners have diverged on gate normalization, the reduced gate, the severity field, and the
mutation ledger (AW-02, AW-04, AW-05, AW-11, AW-12). The code-simplifier timing, the per-task
gate, and the Fable escalation each exist in an old and a new form at once (DC-01, DC-03, PS-14).
Also AW-20, AW-21, AW-22, AW-24, DC-21, DC-22, PS-25, CS-13, DC-28. Roughly 25 findings.

**RC2. No reference-integrity check.** Nothing verifies that a backticked path, a cited heading,
a cited memory, a vendored skill's sibling name, or a relative link resolves. AW-08, AW-18,
PS-03, PS-12, CS-3, CS-6, DC-08, DC-09, DC-10, DC-12, DC-13, DC-15, DC-17, DC-18, PS-21, and the
path halves of CS-4 and DC-14. About 18 findings.

**RC3. A new ruling lands in one home and the older homes are never swept.** The ruling's own
owner is correct; the superseded text lives on elsewhere. DC-01, DC-03, DC-04, DC-06, DC-16,
DC-30, PS-04, PS-05, PS-11, PS-14, PS-15, PS-18, CS-5, AW-07, AW-17. No ruling ships with a list
of the phrases it retires.

**RC4. cairn-cms shape assumed by workstation-wide infra.** Runners, agents, and skills assume
npm scripts, `docs/superpowers/`, `docs/internal/`, a gate classifier, and a content guide that
only cairn-cms (or only ecxc-ski) has. AW-01, AW-06, AW-13, AW-14, AW-15, AW-19, PS-08, PS-09,
PS-10, PS-21, DC-19, DC-23. AW-01 breaks the style-guide-sync plan's chain W directly.

**RC5. Instructions assume context the executor lacks.** A `context: fork` skill told to ask the
user or use "the file under discussion" (PS-06, PS-20); a zero-context agent told to follow "the
spec" (AW-18); an editor prompt that never receives the register paths its header promises
(AW-10); text report contracts that conflict with the structured schema the runner requests
(AW-19).

**RC6. Vendored skills installed with no local overlay.** The manifest records source and
license but has no way to override a description or record precedence against local rules.
CS-2, CS-6, CS-8, CS-9, CS-10, CS-17.

**RC7. Dated facts written in present tense.** Toolchain versions, repo trees, engine pins,
token ids, and model pins stated as current in files that load on every dispatch. CS-3, CS-4,
CS-12, DC-07, DC-11, DC-14, AW-23.

**RC8. Always-loaded context carries on-demand content.** DC-02 (@-imported STATUS and
architecture over budget), DC-19 (cairn-only sections in the global CLAUDE.md), DC-21, AW-09,
AW-24, PS-28, CS-17, AW-13 (probe dispatches in repos with no classifier).

## 3. Ownership rule applied

A rule lives where it executes, in this order: a tool or its output, a runner, an agent
definition or skill, then CLAUDE.md. A side doc under `~/.claude/docs` reaches nobody and holds
rationale only. Where two executors genuinely need the same text at write time (the two
implementer definitions), the copies are sanctioned and a parity check holds them identical.

## 4. Cross-area duplication table

"Confirmed" marks rows re-checked by grep in this synthesis. Paths abbreviate
`~/.dotfiles/claude/.claude/` as `.claude/`.

| Rule | Owner | Becomes a pointer | Deleted | Confirmed |
|---|---|---|---|---|
| Gates run through cairn-run-gate; exit 75 re-issue; no poll; light lane; vanished run | `cairn-run-gate` output (add the vanished message, AW-17) | one line in each runner prompt; global CLAUDE.md one line; `pass-gate-economy.md` keeps rationale | paragraphs in `cairn-implementer.md:110`, `site-implementer.md:97` | yes (6 files carry "exit 75") |
| Pass-class table (gate, bar, test mandate, reduced-gate eligibility) | runner `PASS_CLASSES` (one copy once runners merge; parity test until then) | `pass-core` table verified against it; `pass-gate-economy.md:15`; `spec-plan-review:37`; global CLAUDE.md:170 | class lists in `cairn-implementer.md:45`, `site-implementer.md:42` ("meet the Test mandate line in your dispatch") | yes |
| Reduced fix-round gate | one runner constant rendered into prompts | `diff-reviewer.md:67` ("the reduced gate the dispatch names"); `pass-core:96` | `cairn-implementer.md:117`; chains no-class prompt string | yes (4 disagreeing strings) |
| Gate-tier classifier protocol | `scripts/checks/gate-tier.mjs` plus runner | none | chains copy once runners merge | from area evidence |
| code-simplifier once per pass at close | `pass-core` close step | `pass-gate-economy.md:72`; `site-pass/plan-template.md:48` | global CLAUDE.md:64 and :261; `ship` switches to `code-simplifier:code-simplifier` | yes |
| Per-task chain, thin conductor, below-six rule, ceiling and checkpoint | `pass-core` | global CLAUDE.md "Conducting a pass" cut to the budgets, the model line, and "invoke pass-core"; `model-economy.md:34` | chain prose in cairn-cms and poplar CLAUDE.md (keep implementer name and gate only) | from area evidence |
| Model seats and escalation (xhigh, max, fable) | agent frontmatter, checked against a machine-readable seat table; global CLAUDE.md model line for the conductor | `model-economy.md` keeps the why; `pass-core:29,121`; cairn CLAUDE.md:82 | seat claims in poplar CLAUDE.md:323 | yes (pass-core and cairn omit `max`) |
| Close gate is `npm run check:close` | cairn-cms `package.json` `check:close` | `cairn-pass`, `cairn-release`, `engine-consult` say "`npm test` and `npm run check:close`" | hand lists in `cairn-release:52`, `engine-consult:147`; the extra `npm run check` in `cairn-pass:60` | yes |
| Release cadence and scheme | `cairn-release` skill | cairn CLAUDE.md and `cairn-pass` one line each | the rest of cairn CLAUDE.md "Releases" | from area evidence |
| STATUS present tense, HISTORY ledger, ROADMAP tiers | `pass-core` close ritual | global CLAUDE.md keeps its short rule | `log-project`'s `## Done` tier; cairn CLAUDE.md:141 "history lives in STATUS"; 907-life "pass table" | yes |
| Visual fidelity and the one-check rule | `visual-fidelity` skill | global CLAUDE.md one-line trigger; cairn CLAUDE.md keeps tiers and the responsive standard | the byte-identical "family lessons" block in ecxc-ski and 907-life; `claude-md-archive.md:38` restatement | yes (7 files) |
| Five-viewport responsive standard | showcase CI width matrix (executes) plus cairn CLAUDE.md | site CLAUDE.md files | none | from area evidence |
| DaisyUI-first | `daisyui-a11y-reviewer` (the check) and the official daisyui skill | one line in each implementer; global rule moves to cairn CLAUDE.md (DC-19) | `claude-tooling.md:95` restatement | from area evidence |
| DaisyUI v5 removed classes | official daisyui skill | none | copies in both implementers and `daisyui-a11y-reviewer:36` reduce to a pointer | yes (3 agents) |
| Implementer pre-flight checklist | both implementer definitions, sanctioned copies under a parity check | none | none | yes (byte-identical) |
| Commit conventions and co-author footer | global CLAUDE.md Git Conventions (subagents load it); harness attribution owns the footer | none | footer bullet in CLAUDE.md:68 (DC-29); copies in both implementers and the chains prompt | yes |
| Engine consultation standard | `engine-triage` agent | `engine-consult` skill ("dispatch engine-triage, which carries the standard"); the spec stays as the record | skill copy | yes (3 files) |
| Narrative-arm freeze and site-docs branch | cairn CLAUDE.md plus `site-pass` | `cairn-pass`; one line in each implementer | longer implementer paragraphs | from area evidence |
| One executor per worktree | global CLAUDE.md | one line in `site-implementer`, `engine-consult` | none | from area evidence |
| Em dash policy, tell catalogue, audience routing, "house voice" | always-on output style plus the ESLint rule | global CLAUDE.md one line; `writing-voice` skill routes | style-guide-sync W2 and W4 | yes |
| tellgrader measures report-only | `tellgrader` output and `MEASURES.md` | one line in `cairn-register-editor`, `prose-voice-reviewer`, `diff-reviewer` | the five `docs/voice/*.md` measures sections (DC-28, style-guide-sync) | yes |
| Magic-link consume is one atomic DELETE RETURNING | `web-auth-security-reviewer` (better: a cairn test) | `cloudflare-workers-reviewer` pointer | none | yes |
| Secrets flow, 1Password, Bash env | `bluefin-admin.md` "Secrets" plus the global CLAUDE.md triggers | `cloudflare-estate-inventory.md` | `instructions/ai-operational-rules.md` (DC-17) | yes |
| Sleep inhibitor and runaway guard | the tools that hold the inhibitor; runner launch NOTE for guard and `/loop` | `unattended-work-guards.md` rationale | stale CLAUDE.md:212 wording | from area evidence |
| Go and bubbletea mandates, cobra precedence | `go-conventions` (declares precedence over cobra), skill descriptions | global CLAUDE.md, cairn and poplar CLAUDE.md | elm-conventions dropped from the cobra `_why` (CS-2) | from area evidence |
| bubbletea rules | `elm-conventions` | none | `~/.claude/docs/bubbletea-conventions.md` moves to poplar as history | from area evidence |
| Fresh-context grader; reviewers report every finding; contrast probe | each executor's own step | none | none (left as is: each is that executor's step) | n/a |

## 5. Ranked findings, excluding style-guide-sync

Dispositions: **fix** (correct in place), **consolidate to X** (make X the owner, the rest
pointers), **delete**. Pass letters refer to section 8. Evidence is abbreviated; the full
evidence lines are in the area reader outputs.

### High

| # | ID | Location | Defect | Evidence | Disposition | Pass |
|---|---|---|---|---|---|---|
| 1 | AW-01 | `.claude/workflows/pass-execute-chains.js:164` | class-default reduced gate hardcodes cairn npm scripts; chain W runs in `~/.dotfiles`, which has no package.json | `CLASS_DEFAULT_REDUCED_GATE = "npm run check && ..."`; plan W tasks set no `reducedGate` | fix: repo-neutral default, or require per-chain `reducedGate` | B |
| 2 | AW-02 | `pass-execute-chains.js:274` | gate strings compared raw; wrapper, `cd` prefix, and multi-line stdout all register MISMATCH, which the reviewer must block on | chains lacks `gateCore`/`gateMatches` from `pass-execute.js:369-386` | fix: shared matcher, parity-tested | B |
| 3 | DC-01 (+PS-13) | `.claude/CLAUDE.md:64`, `:261`; `skills/ship/SKILL.md:31` | per-commit code-simplifier rule survives the 2026-09-27 once-per-pass ruling | pass-gate-economy.md:72; pass-core:156 | consolidate to pass-core; delete CLAUDE.md copies; ship uses the plugin agent | B |
| 4 | PS-01 | `.claude/skills/ship/SKILL.md:1` | personal `ship` shadows the project `ship` skills in ecxc-ski and the two ASC repos; runs `make check` in a repo with no Makefile | docs: "personal over project" | fix: rename to `go-ship`, drop generic triggers | A |

### Medium

| # | ID | Location | Defect | Evidence | Disposition | Pass |
|---|---|---|---|---|---|---|
| 5 | AW-11 (+PS-23) | `pass-execute.js:86`, `pass-execute-chains.js:118`, `pass-core:96` | two runners duplicate PASS_CLASSES and every helper; kept in step by comment; already drifted | "Keep in step with ..." in both | consolidate to one runner (chains as a mode); interim parity test | test in B, merge in E |
| 6 | AW-04 | `diff-reviewer.md:67`, `pass-execute.js:246`, chains `:164`, `:249` | four disagreeing definitions of the reduced gate | four strings quoted | consolidate to the runner constant | B |
| 7 | AW-13 | `pass-execute.js:437`, chains `:317` | two probe subagents per task and fix round, no `model:`, even in repos with no classifier; classifier paragraph always rendered | `agent(...)` with no model; settings default sonnet | fix: probe once per run, skip when absent, `model: "haiku"` | B |
| 8 | DC-04 | `.claude/CLAUDE.md:212` | tells sessions to arm the sleep inhibitor (tool-held since 2026-09-23); omits the required `/loop` wake-up | unattended-work-guards.md:35, :105 | fix CLAUDE.md line; runner launch prints the NOTE | B |
| 9 | DC-02 | `907-life/CLAUDE.md:5`; ecxc-ski STATUS | @-imported STATUS and architecture over the 4000-token budget; STATUS carries pass history; no HISTORY.md | claude-context-budget output; 236 and 173 lines | fix: move history to HISTORY.md, drop the architecture import; budget check at close | F |
| 10 | DC-10 (+CS-14) | `.claude/docs/bubbletea-conventions.md` | 648-line poplar doc in workstation docs; relative `research/` links dead; cites a missing tmux doc and lint hook; duplicates elm-conventions and verifies by tmux | find results; doc:584 | delete from workstation docs (move to poplar as history); fold checklists into elm-conventions pointing at tui-visual-verify | D |
| 11 | DC-07 | `.claude/docs/cloudflare-estate-inventory.md:10` | canonical token record names a deleted token as the one live token; wrong origin store | lines 10, 27, 36; secret-set.sh:33 | fix | C |
| 12 | DC-09 | `cloudflare-estate-inventory.md:56`; `aksailingclub-org/CLAUDE.md:134` | cites an `asc-cloudflare-access` memory that exists nowhere | grep over all memory dirs empty | fix: write the recipe into the inventory | C (inventory), F (ASC pointer) |
| 13 | DC-11 | `poplar/CLAUDE.md:323`; poplar agents | says both reviewers are Opus; go-reviewer pins sonnet, reviewer pins `claude-opus-5` high; implementer has no effort | frontmatter vs seat table | fix: repin to seats; CLAUDE.md says "per model-economy" | F |
| 14 | DC-14 | `907-life/CLAUDE.md:79`, `:80`, `:155` | save "commits to main" (branch-and-publish since 0.62); pin ^0.81.0 vs ^0.84.4; launches from a missing repo | CHANGELOG 0.62.2; package.json:37 | fix; drop the version from prose | F |
| 15 | PS-02 | `.claude/skills/cairn-release/SKILL.md:52` | release gate is a hand subset; omits `check:version` (required for a minor), `check:facts`, `check:vale`, and about 22 more | check:close chains 38 scripts | consolidate to `npm run check:close` | C |
| 16 | PS-03 | `cairn-release/SKILL.md:105` | dead path `docs/guides/upgrade-cairn.md` | exists at `docs/extend/` | fix | C |
| 17 | PS-04 | `engine-consult/SKILL.md:147` | six checks called "CI-only"; all run in `check:close` | check:close contents | consolidate to check:close | C |
| 18 | PS-05 | `cairn-figure/SKILL.md:120` | "gates do not exist yet"; `check:visuals` exists; restated alt rules omit mermaid `accTitle:`/`accDescr:` | commit 7b20aedd; check-visuals.mjs header | fix; rules become a pointer to docs-register.md Visuals | C |
| 19 | PS-06 | `register-check/SKILL.md:4` | `context: fork` skill relies on "the file under discussion", delegation, and session tells | skills docs on fork | fix: explicit args; caller binds tells (after style-guide-sync W4 edits this file) | C |
| 20 | PS-08 | `content-draft/SKILL.md:12`, `content-review/SKILL.md:13` | require `docs/content-guide.md`, which only ecxc-ski has | ls across sites | fix: absent-guide branch | C |
| 21 | PS-09 | `site-pass/SKILL.md:17`, `:55` | hardcodes `docs/superpowers/` plans and archive and `docs/architecture.md`; ASC and cairn-pub differ | ls results | fix: read paths from the site's CLAUDE.md or STATUS | C |
| 22 | PS-10 | `log-issue/SKILL.md:39`, `:168` | creates BACKLOG.md in repos whose doctrine forbids one; hardcodes `git add BACKLOG.md` | ASC project-tracking note; cairn CLAUDE.md:113 | fix: honor a `backlog: false` field; use `backlog_path` | C |
| 23 | CS-1 | `go-conventions/SKILL.md:221` | cobra root template lacks `SilenceErrors: true`; every error prints twice | cobra command.go:1159; cairn root.go:195 | fix | D |
| 24 | CS-2 | `golang-spf13-cobra/SKILL.md:132`; `tooling/vendored-skills.json` | vendored cobra skill contradicts go-conventions on four points with no precedence; elm-conventions wrongly mandated for the cairn tool | quotes from both skills; tool/go.mod | fix: precedence line in go-conventions; drop elm from the `_why` | D |
| 25 | CS-4 | `go-conventions/SKILL.md:592`, `:84`, `:363`, `:335`, `:408` | Go 1.26 pinned (installed 1.27.1); cites dead `check-deep` and ADR-0230; blanket build-tag ban contradicts poplar's gate | `go version`; poplar Makefile | fix: no pinned version; narrow the tag rule | D |
| 26 | CS-5 | `bubbletea-design/SKILL.md:18`, `:216`, `:54` | launches kitty on the live desktop; treats tmux text as verification; `lipgloss.Width` for SPUA glyphs | tui-visual-verify:19, :42; elm-conventions:297 | fix: cut Live Preview and Mode 3; point at tui-visual-verify and elm Rule 6 | D |
| 27 | CS-7 | `tui-visual-verify/SKILL.md:37`, `:61`, `:144` | copy-in kitty-shot drifts (poplar's copy drives the live desktop); `-d` path needs an X11 ImageMagick the host lacks | diff; `magick -list configure` | fix: call `kitty-headless-shot` directly; retire copy-in and `-d` | D |
| 28 | CS-8 | `daisyui/SKILL.md:3` | vendored description orders DaisyUI for all HTML and JSX, against cairn's design-agnostic public output and the artifact contract | description text; cairn charter | fix: manifest description override applied on fetch | D |

### Low

| # | ID | Location | Defect | Disposition | Pass |
|---|---|---|---|---|---|
| 29 | AW-03 | `pass-execute.js:387`, chains `:272` | no-class reduced round gets MISMATCH-blocking and "reduced is expected" together | fix: exempt any reduced round | B |
| 30 | AW-05 | `diff-reviewer.md:60`; `pass-execute.js:170` | severity label documented as routing; nothing reads it | delete the field and the claim | B |
| 31 | AW-06 | `pass-execute-chains.js:226`, header | "committed in this repo" false for chain W; requires a "Ruled inputs" section most plans lack; header describes one past pass | fix: "absolute path"; section optional; general header | B |
| 32 | AW-07 | `.claude/workflows/cairn-overnight-to-release.js` | spent one-off workflow in every skill listing; polls with sleep, bypasses cairn-run-gate, auto-releases | delete | B |
| 33 | AW-12 | `pass-execute-chains.js:40` | auth-data mandate requires `mutationLedger`; chains IMPL_SCHEMA lacks it | fix (then merge, E) | B |
| 34 | AW-17 | `.local/bin/cairn-run-gate:107` | vanished gate reported as failure; prompts say re-run; `cairn-implementer` lacks the clause | fix: distinct exit code and message; drop prompt clauses | B |
| 35 | AW-19 | `agents/cairn-implementer.md:23`, `:147`; `diff-reviewer.md:54` | done = npm check and npm test regardless of dispatched gate; text report shapes conflict with runner schemas | fix: done = the dispatched gate; schema replaces text shape | B |
| 36 | AW-20 | seven homes (see section 4) | gate protocol restated, drifted (cd form, vanished clause, 20 vs 60 lines) | consolidate to cairn-run-gate output | B |
| 37 | AW-23 | `cairn-implementer.md:11`, `site-implementer.md:11` | dated compatibility note loads on every dispatch | delete | B |
| 38 | DC-03 (+PS-16) | `.claude/CLAUDE.md:169`; `site-pass:28`; cairn-cms CLAUDE.md:73; xcathletes CLAUDE.md:95 | "full gate" per task against the class table | fix: "the class's per-task gate (pass-core)" | B (workstation), F (repos) |
| 39 | PS-14 | `pass-core/SKILL.md:29`, `:121`; cairn CLAUDE.md:82 | escalation skips `max` | fix: point to model-economy "Current state" | B (pass-core), F (cairn) |
| 40 | PS-22 | `cairn-pass/SKILL.md:60` | svelte-check runs twice at close | fix: drop the separate `npm run check` | B |
| 41 | DC-29 | `.claude/CLAUDE.md:68` | co-author footer rule conflicts with the harness's model-named trailer | delete the bullet; harness owns it | B |
| 42 | DC-30 | `.claude/CLAUDE.md:182` | pre-bake "refresh memory" contradicts the memory rule | fix | B |
| 43 | AW-16 | `.local/bin/claude-tooling-sync:27` | verify reads the dotfiles main checkout; docstring says `~/.claude/tooling`; a worktree cannot be verified | fix: `--root` flag defaulting to the script's repo | A |
| 44 | CS-9 | `skills/vhs-cli-demos/` | third-party skill with no manifest entry; verify never flags unlisted dirs | fix: manifest entry; verify flags unlisted licensed dirs | A |
| 45 | AW-14 | `daisyui-a11y-reviewer.md:85` | repo-relative ledger paths exist only in cairn-cms | fix: absolute cairn-cms paths | C |
| 46 | AW-15 | `figure-verifier.md:15` | main-checkout register path grades a worktree page against stale rules | fix: resolve against the dispatch's checkout | C |
| 47 | AW-18 | `site-implementer.md:110` | "the spec's rule" with no path | fix: inline the rule | C |
| 48 | PS-11 | `log-project/SKILL.md:148`, `:117` | closes into ROADMAP `## Done`; seeds foreign tiers | fix: close to HISTORY.md; read existing tiers | C |
| 49 | PS-12 | `spec-plan-review/SKILL.md:60` | cites a lens set "in the global CLAUDE.md" that is not there | delete the pointer | C |
| 50 | PS-15 | `spec-plan-review/SKILL.md:95`, `:124` | reviewers at `high` against the seat table's `medium` | fix, or add a seat row with its reason | C |
| 51 | PS-17 | `engine-consult/SKILL.md:30`, `:36`; `site-pass/plan-template.md` | two definitions of "Facts consulted"; template omits it | fix: one definition; add to template | C |
| 52 | PS-18 | `engine-consult/SKILL.md:18` | allows a pass-end draft plan; pass-core forbids | delete the clause | C |
| 53 | PS-19 | `register-check/SKILL.md:3` | "three-gate" review runs four gates | fix (after style-guide-sync) | C |
| 54 | PS-20 | `content-review/SKILL.md:46` | fork skill told to ask and apply | fix: end at the report | C |
| 55 | PS-21 | `dependency-upgrade/SKILL.md:60` | records dir named family-wide exists only in cairn-cms | fix | C |
| 56 | PS-28 | `cairn-release/SKILL.md:3`, `visual-fidelity` | 849- and 672-char always-listed descriptions | fix: trim to about 300 | C |
| 57 | DC-06 | `.claude/docs/fable-post-cutoff-system.md:3` | says Fable conducts; "budget #3" | fix: point to model-economy | C |
| 58 | DC-08 | `.claude/CLAUDE.md:99` | per-project `api-access.md` exists in no in-scope repo | fix: point to the estate inventory | C |
| 59 | DC-16 | `.claude/docs/claude-tooling.md:43` | every addition must add a CLAUDE.md line, against "strongest form first" | fix | C |
| 60 | DC-17 | `.claude/instructions/ai-operational-rules.md` | orphan; reaches no agent; restates CLAUDE.md; wrong wrangler assumption | delete (and the two site stubs, F); move the `--name` fact to the inventory | C, F |
| 61 | DC-23 | `.claude/docs/web-content-method.md:155` | "site-agnostic" rubric anchored on ECXC audiences | fix: generic anchors; ECXC anchors to its content guide | C (+ ecxc in F) |
| 62 | DC-24 | cairn-cms `CLAUDE.md` Tooling | cobra skill "mandatory" but path-gated, so invisible until a `.go` file is touched | fix wording: "loads once a Go file is open" | F |
| 63 | CS-3 | `elm-conventions/SKILL.md:18`, `:271`, `:300` | names poplar paths and helpers that no longer exist | fix: current tree or generic | D |
| 64 | CS-6 | `vale-fix`, `vale-setup`, `vale-triage` | cross-references use upstream names; rename rewrites only `name:` | fix in `claude-tooling-sync fetch_skill`, then refetch | D |
| 65 | CS-10 | `vale-setup:52`, `vale-ci:48`, `vale-fix:62` | generic Vale advice conflicts with committed styles, pinned CI, and pass branches | fix: local overlay note applied by the manifest | D |
| 66 | CS-11 | `ts-conventions/SKILL.md:92` | copy-in ESLint config lacks the em-dash rule and the `.svelte` block | consolidate to cairn's `eslint.config.js` as the copy-in source | D |
| 67 | CS-12 | `elm-conventions/SKILL.md:203`, `:26` | root `View() string` in a v2 example; Rule 1 against the delegation rules | fix | D |
| 68 | CS-13 | `go-conventions/SKILL.md:558`, `:552` | error-string rules stated three times, godoc default twice | consolidate to Error Handling | D |
| 69 | CS-17 | `vhs-cli-demos/SKILL.md:3` | 923-char description for an uninstalled tool | fix: trim or `paths:` gate via manifest override | D |
| 70 | AW-21 | both implementers; `cairn-register-editor.md:51`; `prose-voice-reviewer.md:30` | pre-flight checklist and DaisyUI section duplicated; measures paragraph duplicated | implementer copies: sanctioned under a parity check; measures: consolidate to MEASURES.md | E |
| 71 | AW-22 | `engine-triage.md:33`; `engine-consult:78` | engine standard quoted verbatim in three places | consolidate to engine-triage | E |
| 72 | DC-19 | `.claude/CLAUDE.md:122-138`, `:187` | cairn-only sections load in every repo | consolidate to cairn and site CLAUDE.md, pass-core | E |
| 73 | DC-21 (+PS-24) | `.claude/CLAUDE.md:145-185` | "Conducting a pass" restates pass-core (about 747 tokens a session) | consolidate to pass-core | E |
| 74 | DC-22 (+PS-26) | ecxc-ski CLAUDE.md:97; 907-life:158; cairn:215; ASC:74; archive:38 | visual-fidelity rules in seven places | consolidate to visual-fidelity | E (dotfiles), F (repos) |
| 75 | PS-25 | cairn CLAUDE.md:150; `cairn-release`; `cairn-pass:101` | release cadence stated three times | consolidate to cairn-release | E, F |
| 76 | DC-12 | `poplar/CLAUDE.md:351`; `poplar/.vale.ini` | re-sync script and canonical glw907 style both missing | fix: restore or retire the overlay (coordinate with DC-25) | F |
| 77 | DC-13 | ecxc-ski CLAUDE.md:22, :109, :27; 907-life:119, :170 | dead cairn headings, moved post-mortem path, missing STATUS entries | fix | F |
| 78 | DC-15 | `aksailingclub-org/CLAUDE.md:207`, `:216` | credentials pointer and global heading both stale | fix | F |
| 79 | DC-18 | cairn-cms `CLAUDE.md:141`, `:147` | "history lives in STATUS"; cites a missing cairn-pub heading | fix | F |

## 6. Owned by the style-guide-sync plan

These are fixed by the plan's chain W or its join, not by the passes below. The plan's task is
named; two gaps need a conductor ruling before segment B.

| ID | Sev | Location | Defect | Plan task |
|---|---|---|---|---|
| PS-07 | medium | `register-check/SKILL.md:69` | a July plan's register section "outranks everything" and sets a contrary register | W4 (explicit outcome) |
| DC-25 | medium | `.claude/docs/authoring-charter.md:17` | "no house voice, no tell catalogue" contradicts the output style, CLAUDE.md, and poplar's glw907 overlay | W4, ruling 12. **Gap:** poplar's glw907 overlay is not in W4's Files; rule it into W4 or leave it to pass F with DC-12 |
| AW-09 | medium | `agents/cairn-register-editor.md:25` | loads a 485-line July plan each run, against the chain's own prompt | W1 and W3 |
| AW-08 | low | `cairn-register-editor.md:19` | cites a ratified exemplar that exists nowhere | W3 |
| AW-10 | low | `workflows/docs-page-chain.js:32` | `registerPaths` never reaches the editor prompt | W1 (renderer test) |
| DC-27 | low | `.claude/CLAUDE.md:279` | names a write-once spec as the docs standard | W4 (CLAUDE.md "Writing voice" is in its Files) |
| DC-28 | low | `.claude/docs/voice/*.md`, `technical-doc-go.md:5` | measures section in five files; Go register names a missing repo and wrong linter | W4. **Gap:** W4's Files cover only `technical-doc-web.md` and `editor.md`; the other three voice files are outside it |
| AW-24 (+DC-26, CS-15) | low | output style `:30`; CLAUDE.md "Writing voice"; `writing-voice/SKILL.md:80`; drafter; reviewer | tells and em-dash policy restated beside the always-on style | W2 (drafter) and W4 (style, CLAUDE.md, skill) |

Plan amendments this audit implies, for the conductor's pre-flight:

1. Once pass B lands, chain W needs no `reducedGate` workaround (AW-01) and the W task `notes`
   no longer need to override the implementer's definition of done (AW-19).
2. W6 should add its phrases to the retired-phrase list and check that pass A creates, instead
   of adding a second check to `scripts/check.sh`.
3. With AW-16's `--root`, W6's acceptance can run `claude-tooling-sync verify --root <worktree>`
   inside the chain instead of deferring it to the boundary.
4. The plan invokes `pass-execute-chains` by name. Pass B keeps that name; the runner merge
   (AW-11) waits for pass E, after the plan closes.

## 7. Mechanical guard

Two homes. `claude-tooling-sync verify` owns tooling-shape checks and already runs in
`check-drift`. `scripts/check.sh` owns content checks over the dotfiles tree, gating every
dotfiles pass. Checks that read other repos run from `check-drift` weekly and from the
`cairn-pass` and `site-pass` close steps on the repo being closed, because a dotfiles gate
should not fail on another repo's state.

Every check lands green through a **ratchet baseline**: a committed file listing today's known
violations, each keyed to its finding ID. A new violation fails; a baseline entry may only be
removed; the file failing when empty-but-present is not an error. This satisfies the plan's own
review rule against a tripwire that is red on today's tree or vacuous.

| Check | Home | Rule | Catches |
|---|---|---|---|
| Dead reference scan | `scripts/check.sh` (new `scripts/check-claude-refs.py`) | every backticked path in `agents/`, `skills/` (authored), `workflows/`, `docs/` (excluding `record/`), `output-styles/`, `CLAUDE.md` must resolve. Absolute and `~/` paths resolve as written. A repo-relative path in an agent or skill must be written absolute or prefixed with its repo (`cairn-cms/docs/...`), and then must resolve under `~/Projects/<repo>` | AW-08, AW-14, AW-15, PS-03, PS-21, CS-3 (paths), CS-4 (paths), DC-08, DC-12, DC-13 (paths) |
| Heading citation | same script | a quoted phrase following a cited file (`file.md` ("Heading")) must match a heading in that file | DC-13, DC-15, DC-18 |
| Memory citation | same script | "`<name>` memory" must resolve to `~/.claude/projects/*/memory/<name>.md` | DC-09 |
| Relative markdown links | same script | every `[x](relative)` in `~/.claude/docs` resolves | DC-10 |
| Orphan docs | same script | each file under `docs/` (excluding `record/`) and `instructions/` is cited by at least one CLAUDE.md, skill, agent, or workflow | DC-17 |
| Pointerless "the spec" | same script | "the spec" or "the plan" in an agent definition needs a path on the same line | AW-18 |
| Retired phrases | same script, list at `claude/.claude/tooling/retired-phrases.txt` (header names the cairn-cms twin from R8) | a listed phrase fails outside lines marked `retired-ok`; missing or empty list fails. Every ruling that supersedes text adds the old phrase here in the same commit | DC-01, DC-04, DC-06, DC-30, PS-04, PS-05, AW-07 ("sleep 30"), CS-4 ("currently 1.26"), and the style-guide-sync phrases (W6 appends) |
| Duplicate paragraphs | same script | 12-word shingle overlap above a threshold between any two of: agents, authored SKILL.md files, output styles, CLAUDE.md, docs (excluding `record/`). Pairs in the baseline pass; sanctioned copies are declared in a `parity` list and must be byte-identical | AW-04, AW-20, AW-21, AW-22, AW-24, CS-13, DC-21, DC-22, DC-28, PS-25, and future drift of the implementer checklists |
| Runner parity and schema tests | `tests/pass-execute-*.test.mjs`, run by check.sh (pattern: the existing docs-page-chain test) | PASS_CLASSES deep-equal across runners until merged; every field a mandate cites exists in IMPL_SCHEMA; every REVIEW_SCHEMA field is read; gate matcher accepts wrapper, `cd`, and multi-line forms; a no-class reduced round has no MISMATCH line; a no-classifier run spawns no probes; no `agent(` call lacks `model:`; a repo with no package.json and no `reducedGate` is rejected | AW-01, AW-02, AW-03, AW-05, AW-12, AW-13, AW-11 interim |
| Skill name collision | `claude-tooling-sync verify` | a personal skill name equal to any `~/Projects/*/.claude/skills/<name>` fails | PS-01 |
| Unmanifested third-party skill | verify | a `skills/<dir>` carrying a `LICENSE*` with no manifest entry fails | CS-9 |
| Vendored sibling names | verify, plus a `fetch_skill` rewrite | a backticked "`<name>` skill" in a vendored skill must name an installed skill | CS-6 |
| Description override and cap | verify | a manifest `description` override must match the installed file; a non-`paths:`-gated description over 500 characters fails | CS-8, CS-17, PS-28 |
| Fork-skill lint | verify | a `context: fork` skill body may not contain "under discussion", "during the session", "delegated", or an instruction to ask the user | PS-06, PS-20 |
| Seat check | verify, seat table at `claude/.claude/tooling/seats.json` (model-economy.md points to it) | every user and project agent's `model` and `effort` match its seat | DC-11, PS-15 (if the seat is recorded), and the model half of DC-21 |
| Worktree root | verify | `--root` selects the tree; default is the script's own repo | AW-16 |
| Context budget over imports | `check-drift` and the close steps | `claude-context-budget` over every `@`-imported file of each repo CLAUDE.md, not only on write | DC-02 |
| Quoted version pins | close steps | a dependency range quoted in a repo CLAUDE.md must match package.json | DC-14 |

Not mechanizable, left to review: AW-09, AW-17, AW-19, PS-02 (partly: a lint could flag a
`npm run check:` list longer than two items outside `check:close`), PS-10, PS-11, PS-13, PS-16,
PS-17, PS-18, PS-19, CS-1 (a Go-repo test can assert one error line), CS-2, CS-5, CS-7, CS-10,
CS-11 (a rules-block diff is possible), CS-12, DC-03, DC-07, DC-16, DC-23, DC-29.

Tool-output routing, by the rule-lives-where-it-executes principle: `cairn-run-gate` prints the
vanished-run instruction (AW-17); the runners print the runaway-guard and `/loop` NOTE at launch
(DC-4).

## 8. Pass triage

All workstation passes run in a `~/.dotfiles` worktree and merge to dotfiles `main`, because a
workflow invoked by name reads the stowed copy on `main`. Check for another executor first (the
style-guide-sync chain W worktree at `~/Projects/.worktrees/dotfiles-style-guide-sync` must not
exist yet, or must be recreated from the new `main`).

### Pass A: the guard (dotfiles; lands first)

Class `engine-logic`. Tasks, sequential:

1. `claude-tooling-sync`: `--root` (AW-16); the collision, unmanifested-skill, sibling-name,
   description, fork-lint, and seat checks; `seats.json`. Fix PS-01 (rename `ship`) and CS-9
   (manifest `vhs-cli-demos`) in the same task so those checks start green.
2. `scripts/check-claude-refs.py`: dead references, headings, memory citations, relative links,
   orphans, pointerless "the spec", retired phrases, duplicate paragraphs with parity list, all
   with the ratchet baseline; wired into `scripts/check.sh`. Fixtures prove each rule fires,
   passes, and fails on a missing list.
3. Close-step hooks: `cairn-pass` and `site-pass` close run the reference checker and
   `claude-context-budget` over the closing repo's CLAUDE.md and imports; `check-drift` runs them
   across `~/Projects`.

Findings closed: PS-01, CS-9, AW-16. Every other finding with a mechanical rule enters the
baseline and leaves it when its pass fixes it.

### Pass B: execution path (dotfiles; before style-guide-sync)

Everything the style-guide-sync conductor, runner, implementers, or reviewers would hit.

1. Runners (`engine-logic`, with the parity and schema tests): AW-01, AW-02, AW-03, AW-04
   (runner side), AW-05, AW-06, AW-12, AW-13, plus the launch NOTE (DC-04 tool half).
2. `cairn-run-gate` vanished exit code and the prompt clauses it retires: AW-17, AW-20.
3. Agent definitions (`docs`): AW-19, AW-23, AW-04 and AW-05 in `diff-reviewer.md`.
4. Global CLAUDE.md and pass skills (`docs`): DC-01 (+PS-13, including `ship`), DC-03 (+PS-16,
   workstation and `site-pass`), DC-04, PS-14 (pass-core), PS-22, DC-29, DC-30.
5. Delete `cairn-overnight-to-release.js` (AW-07).

Findings: 20. Implementer-definition edits land here so W5 later branches from them.

### Then: the style-guide-sync plan

Run it with the section 6 amendments. It closes the eight owned findings and extends the
retired-phrase list.

### Pass C: process skills and workstation docs (dotfiles; after style-guide-sync)

Waits for the plan because PS-06 and PS-19 touch `register-check/SKILL.md`, which W4 edits.

Findings (fix unless noted): PS-02 and PS-04 (consolidate to `check:close`), PS-03, PS-05,
PS-06, PS-08, PS-09, PS-10, PS-11, PS-12 (delete), PS-15, PS-17, PS-18 (delete clause), PS-19,
PS-20, PS-21, PS-28, AW-14, AW-15, AW-18, DC-06, DC-07, DC-08, DC-09 (inventory side), DC-16,
DC-17 (delete), DC-23. Twenty-seven findings: split at the natural seam into C1 (cairn-facing
skills: PS-02 to PS-06, PS-17, PS-18, PS-19, PS-28, AW-14, AW-15) and C2 (site and generic
skills plus docs: the rest).

### Pass D: convention skills and the vendored manifest (dotfiles)

Independent of pass C (disjoint files), so C and D may run in parallel after the plan.
`claude-tooling-sync` changes here (CS-6 rewrite, CS-8 and CS-10 overlays) must not overlap
pass A's work; A lands first.

Findings: CS-1, CS-2, CS-3, CS-4, CS-5, CS-6, CS-7, CS-8, CS-10, CS-11 (consolidate to cairn's
ESLint config), CS-12, CS-13 (consolidate), CS-17, DC-10 (+CS-14; delete from workstation docs,
fold checklists into elm-conventions). Fourteen findings.

### Pass E: consolidation to owners (dotfiles; after C and D)

The routing work, done last so it moves settled text. Shrinks the duplicate-paragraph baseline.

Findings: AW-11 (+PS-23; merge the chains runner into `pass-execute.js` as a mode and update the
skill listing and plan template), AW-21 (parity list for the implementer copies; measures to
MEASURES.md), AW-22 (engine-triage owns the standard), DC-19, DC-21 (+PS-24), DC-22 (+PS-26,
workstation side), PS-25 (workstation side). Seven findings.

### Pass F: repo CLAUDE.md files (one small chore per repo)

Each repo gets its own chore under its own one-executor check; they are small tasks and go
straight through each repo's gate. cairn-cms waits for the style-guide-sync merge, since R8
scans its CLAUDE.md.

| Repo | Findings |
|---|---|
| cairn-cms | DC-03 (line 73), PS-14 (line 82), DC-18, DC-24, DC-22 and PS-25 (repo sides) |
| 907-life | DC-02, DC-13, DC-14, DC-22, DC-17 stub |
| ecxc-ski | DC-02, DC-13, DC-22, DC-23 (receive ECXC anchors), DC-17 stub |
| aksailingclub-org | DC-09 (pointer), DC-15, DC-22 |
| xcathletes-org | DC-03 (line 95) |
| poplar | DC-11, DC-12 (with DC-25's ruling) |

### Order

A, then B, then style-guide-sync, then C and D in parallel, then E. F runs per repo any time
after A, except cairn-cms after the style-guide-sync merge. Each pass closes by removing its
findings from the ratchet baseline, so the baseline's size is the remaining work.

## Erratum (2026-09-28, after review)

Section 1's DC-01 row, "code-simplifier per commit (global CLAUDE.md) against once per pass", was
not stale text: `0a2e391` ("Slim the global CLAUDE.md") was written from a base older than
`a7dd5ad` and reverted that ruling, DC-03's, and the "superpowers skills yield" ruling (TDD
write-first only for `engine-logic` and `auth-data`), which this audit missed. Pass B4 of the
sweep restores them.
