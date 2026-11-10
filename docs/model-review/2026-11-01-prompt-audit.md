# Prompt audit: Claude Code configuration for `~/.dotfiles`

The configuration has no dated prompting scaffolds and no pressure language, so nearly all findings are stale facts, conflicts, and leftover history. The proposed diff has 26 hunks in 9 files. It passes `git apply --check`, the roadmap guard and the retired-phrase tripwire on a scratch copy. Nothing in the repo has changed, and the working tree is still clean.

**Diff:** `/tmp/prompt-audit-hJkY/proposed.diff`. Apply it from the repo root with `git apply -p1`; `/tmp` is temporary, so take it before a reboot.

## Assumptions

- **Target model:** Claude Opus 5.5 (`claude-opus-5-5`), the model running this audit. `site-implementer` pins `sonnet`, so it is audited against Sonnet 5.5.
- **Scope:** as you listed it, with no settings files, `.mcp.json` or `~/.claude.json` read.
- **All-projects effect:** `~/.claude/{CLAUDE.md,skills,agents,output-styles}` are symlinks into this repo. Every hunk except the `dotfiles-pass` one therefore changes a file under `~/.claude`, and **affects all projects** once merged.
- **Skipped or absent:**
    - No imports, rules, commands or managed-policy `CLAUDE.md` exist.
    - No `AGENTS.md` or `CLAUDE.local.md` exists.
    - Ancestor directories hold no instruction files.
- **Reported by path, unread:** `claude/.claude/instructions/fastmail-api.md` and `ai-operational-rules.md`. Nothing imports them.
- **No non-Anthropic provider markers:** none turned up in the audited files.

## Inventory

| Surface | Files |
|---|---|
| Instructions | `claude/.claude/CLAUDE.md` (the `~/.claude/CLAUDE.md` target) |
| Project skill | `.claude/skills/dotfiles-pass/SKILL.md` |
| User skills | 14 under `claude/.claude/skills/`, plus reference files |
| Subagents | `cairn-register-editor`, `prose-voice-reviewer`, `site-implementer` |
| Output style | `writing-voice.md`, a symlink to the vendored Survey copy |
| Report only | 13 synced skills in `~/.claude/skills/synced/`, plugins `standards`, `cloudflare`, `tui-design`, `code-review`, `frontend-design`, `skill-creator`, `code-simplifier` |

## Summary

1. **`pass-core` carries incident logs inside its rules.** About 18 parentheticals record pass names, minutes and commit ids that no session can act on. The rules stand without them, and the `Geoff, <date>` ruling tags stay.
2. **`site-implementer` tells a subagent to ask questions it has no way to ask.** The same file already defines `NEEDS_CONTEXT` for that case.
3. **Several rules disagree or are stale.** `site-pass` still counts a retired site, and `claude-infra` requires a PR that "Direct changes" waives. `mail-tend` also asks for approval in chat, which `approval-packet` forbids.

`CLAUDE.md`, `cairn-register-editor`, `prose-voice-reviewer`, `cairn-pass`, `google-sheets` and `retire-project` have no findings.

| Group | Findings |
|---|---|
| 1. Dated prompt text | 3 (2 are re-test flags) |
| 2. Brittle configuration | 15 |
| 3. Tool descriptions | not applicable (no tool definitions; routing text is counted in Group 2) |
| 4. Request config | not applicable, no request code; roster check found no redundancy |

## Findings

### High confidence

| Location | Evidence | Pattern | Why it is obsolete | Action |
|---|---|---|---|---|
| `site-pass/SKILL.md:44` | "The other four sites have no watch command." | Volatile specifics | The table has four sites in total. `cf4c26b` removed xcathletes-org and left this count behind. | `rewrite`: "other three" |
| `claude-infra/SKILL.md:48` | "Land the change through a PR" | Contradicting files | Written 2026-10-11. `pass-core:109` (2026-10-18) and `dotfiles-pass:39` allow a direct change with no PR. Assumes `pass-core` is current. | `rewrite`: add "unless it meets `pass-core` "Direct changes"" |

### Medium confidence

| Location | Evidence | Pattern | Why it is obsolete | Action |
|---|---|---|---|---|
| `site-implementer.md:30` | "Ask any clarifying question before you start" | Contradicting passages in one file | A subagent returns one report and its tool list has no asking tool. Lines 76 and 83 already define `NEEDS_CONTEXT`. | `rewrite` |
| `site-implementer.md:44-45` | "read the official skill at the `standards:daisyui` skill" | Volatile specifics | A garbled path replacement from the plugin cutover, `322d136`. | `rewrite` (see the reach flag below) |
| `pass-core/SKILL.md:65-67, 75-77, 85-87, 101-102, 192-193, 211, 278-279, 300-301, 330-332` | "the intake-1 overnight run stopped at 01:17 on a 995-minute plan" | History narratives | The rule's authority is the behavior it prescribes. Each tail names an incident the reader can't use. | `remove` tails, keep ruling tags |
| `pass-core/SKILL.md:344-346, 349-353, 362-369, 370, 380-381, 386, 389` | "(Pass 1, 2026-10-19: the recovery address was already on file)" | History narratives, patch accretion | These lens items already state their mechanism. Lines 344 and 349 also cite `pass-core` from inside `pass-core`. | `remove` tails |
| `pass-core/SKILL.md:309-310` | "`approval-queue triage` survives only for" | Migration-relative phrasing | A diff against an earlier version the reader never saw. | `rewrite` |
| `pass-core/SKILL.md:408` | "stop growing (ruling 8)" | Migration-relative phrasing | Same defect, plus a ruling number the reader can't resolve. | `rewrite` |
| `approval-packet/SKILL.md:132` | "A PR body still opens with" | Migration-relative phrasing | Same defect. | `rewrite` |
| `dotfiles-pass/SKILL.md:50` | "no longer follows a pull" | Migration-relative phrasing | Same defect. | `rewrite` |
| `log-project/SKILL.md:18-19` | "keeps its own until its own pass, and every other repo has retired the file" | Time-sensitive content | Ties the rule to a future event. The rewrite keeps "cairn-cms" on the line because `check-roadmap-refs.sh` requires it. | `rewrite` |
| `log-project/SKILL.md:4-9` | "Trigger on: "log project", "new project", ..." | Trigger-case enumeration | Twelve near-synonyms ride in every request's skill listing. | `rewrite` to intent categories |
| `engine-consult/SKILL.md:123` | "which the local ritual once skipped" | History narrative | A near-copy of a phrase already in `retired-phrases.txt`. | `remove` |
| `engine-consult/SKILL.md:132-135` | "The paste-then-delete staging mechanics stay as they are." | Migration-relative phrasing | Nothing in this repo defines those mechanics. | `rewrite` |
| `vps-conventions/SKILL.md:79-82, 106` | "The servers cutover's stub proof on 2026-10-22 showed it" | History narrative | The rule and its fix are stated without the incident. | `remove` |

### Flags, no edit proposed

| Location | Evidence | Pattern | Confidence | What it needs |
|---|---|---|---|---|
| `output-styles/writing-voice.md:64-65` | "This is reported-only, from the 2026-09 benchmark; no external standard is cited" | History narrative | Medium | This line is always loaded and tells the model nothing. The file is vendored, so a local edit is overwritten. Cut the sentence in the `glw907/survey` repo, which is outside this project. |
| `mail-tend/SKILL.md:61, 88` vs `approval-packet/SKILL.md:29`, `pass-core/SKILL.md:31` | "one line in chat ... Go?" vs "never as a question in chat" | Contradicting files | Medium | Newer `mail-tend` text loosens an older prohibition, so I left both. Decide whether mail moves and rule designs are a standing chat exception. If so, name the exception in `approval-packet`. |
| `pass-core:52-56`, `claude-infra:42-46` | "Deliver what was asked, at the scope intended." | Model-version workaround | Medium | This is the Opus 5 scope instruction, a named re-test candidate on 5.5. Keep it until an eval shows it can go. The other two `prompting-claude-opus-5` citations (`pass-core:193-196`, `440-442`) carry no scope rule. |
| `output-styles/writing-voice.md:80-81` | "reread it once for flat cadence ... and revise" | Self-check instruction | Low | Same re-test class, and it is vendored. |
| `site-implementer.md:4, 44` | tools list has no `Skill` | Unenforced instruction | Medium | `standards:daisyui` no longer has a readable path since the plugin cutover, and the agent can't invoke skills. This contradicts `claude-infra:63`. Decide between adding `Skill` to its tools and preloading the skill; I haven't tested either. |
| `pass-core/SKILL.md:39` | a single paragraph carrying six unrelated rules | Patch accretion | Low | Splitting it changes structure, so it belongs in a pass, not a hunk. |
| `engine-consult/SKILL.md:137-141` | "the consultation that appends it then deletes this section" | Time-sensitive content | Low | Written 2026-08-26. The answer is in cairn-cms's ledger, outside this project and not probed. |
| `dotfiles-pass/SKILL.md:7, 32` | `{skills,agents,workflows}` | Volatile specifics | Low | `claude-tooling.md` says the repo keeps no workflow script. Harmless as written, and removing it narrows a risk-class glob. |
| `claude/.claude/skills/survey/**` | n/a | Out of scope for edits | n/a | Vendored. The agent-facing register has no findings. |

**Deliberately kept:**
- The `Geoff, <date>` ruling tags, which are provenance.
- The output style's prohibition list, which traces to external standards and Geoff's rulings.
- The em-dash rule's three copies, which agree.
- The copied scope quote in `pass-core` and `claude-infra`, which also agree.
- Exact commands in `mail-tend`, `retire-project` and `survey`, which are fragile operations.
- Incident tails that carry a mechanism or a quoted ruling, such as `pass-core:376-377`.
- The two reviewer agents, whose overlap is real but whose domains differ.

## Plugins and synced skills (report only)

The scanned plugin and synced files contain no retired model IDs, no `budget_tokens`, and no thinking scaffolds. `standards` pins `claude-opus-5-5` throughout, and `code-simplifier` uses the `opus` alias. Pressure language is rare: 2 or fewer hits per file, except `code-simplifier` at 4 lines or fewer. Superpowers is installed but not in this session's skill list, so I skipped it.

I checked these two sets by grep signals only, not by reading each file, so a subtler pattern could remain there.

## Proposed diff

These are the changed lines by file, at the line numbers above. The applyable form, with context, is the diff file named at the top.

**`site-pass/SKILL.md`**
```diff
-task after each push. The other four sites have no watch command.
+task after each push. The other three sites have no watch command.
```

**`claude-infra/SKILL.md`**
```diff
-5. **Land the change through a PR** whose commit messages and body cite the guidance URL.
+5. **Land the change through a PR** whose commit messages and body cite the guidance URL, unless
+   it meets `pass-core` "Direct changes".
```

**`agents/site-implementer.md`**
```diff
-1. Ask any clarifying question before you start if the task or its boundaries are unclear.
+1. If the task or its boundaries are unclear, report NEEDS_CONTEXT before you change anything.
```
```diff
-  Tailwind values. Before writing admin or DaisyUI markup, read the official skill at
-  the `standards:daisyui` skill and prefer the stock component. The engine's admin design
+  Tailwind values. Before writing admin or DaisyUI markup, read the `standards:daisyui`
+  skill and prefer the stock component. The engine's admin design
```

**`log-project/SKILL.md`**
```diff
-  Create or update an initiative record in `~/Projects/initiatives`. Use when
-  the user wants to track a multi-issue effort or initiative, bigger than a
-  single backlog item. Trigger on: "log project", "new project", "start an initiative", "add
-  to roadmap", "track this effort", "we need a project for", or when the user
-  describes a multi-step effort that spans several backlog items. Also trigger
-  on "close project", "finish project", "project status", or "update roadmap".
+  Create, update, close, or report on an initiative record in
+  `~/Projects/initiatives`. Use when the user wants to track a multi-step effort
+  bigger than a single backlog item, or asks about a project's or roadmap's status.
```
```diff
-pieces. Never create a `ROADMAP.md`: cairn-cms keeps its own until its own pass,
-and every other repo has retired the file.
+pieces. Never create a `ROADMAP.md`; only cairn-cms keeps one.
```

**`engine-consult/SKILL.md`**
```diff
-   `check:transcripts`, and `check:symbols`, which the local ritual once skipped.
+   `check:transcripts`, and `check:symbols`.
```
```diff
-Consultation cannot foresee what a pass discovers while building. Mid-pass discoveries
-still file, using the same four-field item schema, and their later triage runs through
-the same `engine-triage` agent against the same ledger. The paste-then-delete staging
-mechanics stay as they are.
+Consultation cannot foresee what a pass discovers while building. File each mid-pass
+discovery with the same four-field item schema. Its later triage runs through the same
+`engine-triage` agent against the same ledger.
```

**`vps-conventions/SKILL.md`**
```diff
-`ssh` command on its own terms. The servers cutover's stub proof on 2026-10-22 showed it: with
-both `Bash(ssh -o BatchMode=yes geoff@ward.907.life *)` and a narrower `... sudo stalwart-jmap *`
-rule in place, `stalwart-jmap destroy` over ssh was still denied as Unverifiable Deletion Scope.
-Exact rules for repo scripts did run.
+`ssh` command on its own terms. Exact rules for repo scripts do run.
```
The second hunk at line 106 drops only the closing `(Born 2026-09-01: dubplate subnet pin 502'd Navidrome.)`.

**`approval-packet/SKILL.md`**
```diff
-A PR body still opens with `## Brief`, the record on GitHub; the packet is the hand-over.
+A PR body opens with `## Brief`, the record on GitHub; the packet is the hand-over.
```

**`dotfiles-pass/SKILL.md`**
```diff
-touched `claude/.claude/settings.json`, since the live file no longer follows a pull. Prose follows the workstation writing
+touched `claude/.claude/settings.json`, since the live file doesn't follow a pull. Prose follows the workstation writing
```

**`pass-core/SKILL.md`** (17 hunks)
```diff
-   standing answer still stops (Geoff, 2026-10-12: the intake-1 overnight run stopped at 01:17 on
-   a 995-minute plan against a 780-minute line, and nothing ran until morning). Past a count cap
+   standing answer still stops (Geoff, 2026-10-12). Past a count cap
```
```diff
-   escalation the plan doesn't allow, which would change the design (2026-10-19: B3c stopped at its
-   read cap, then at its escalation rule, then on a returning cause, each time with an in-budget
-   fix as the recommendation, and Geoff took it).
+   escalation the plan doesn't allow, which would change the design (Geoff, 2026-10-19).
```
```diff
-   counts pairs twice and never sets the stop (Geoff, 2026-10-12: intake-1 stopped on a 995-minute
-   task sum whose path was 725, under its 780 line). The design states its estimate in path minutes,
+   counts pairs twice and never sets the stop (Geoff, 2026-10-12). The design states its estimate in path minutes,
```
```diff
-   that waits on Geoff for a step the list left out is a planning miss (2026-10-19: Pass 1's mail
-   reader waited 40 minutes on a Proton Bridge sign-in that needed nothing the pass built).
+   that waits on Geoff for a step the list left out is a planning miss.
```
```diff
-clock stop. In the three days to 2026-10-19, Geoff took the recommended option on 24 of 36 questions, five of
-them mid-run calls inside approved scope. Prompting Claude Opus 5
+clock stop. Prompting Claude Opus 5
```
```diff
-branch first (2026-10-19: both sessions asked Geoff B3c's read-cap question).
+branch first.
```
```diff
-executor's merge of the plan branch then conflicts in STATUS (twice on 2026-10-11); it batches its
-STATUS changes into the hand-over after that pass lands (conductor `4bea6e68`, 2026-10-11).
+executor's merge of the plan branch then conflicts in STATUS; it batches its STATUS changes into
+the hand-over after that pass lands.
```
```diff
-record. A merged PR body is history no session reads (Geoff, 2026-10-11: dubplate PR #2 left 14
-items there).
+record. A merged PR body is history no session reads (Geoff, 2026-10-11).
```
```diff
-pass that merges its own PR sends nothing (Geoff, 2026-10-11). `approval-queue triage` survives
-only for an explicit backlog triage.
+pass that merges its own PR sends nothing (Geoff, 2026-10-11). `approval-queue triage` is only for
+an explicit backlog triage.
```
```diff
-session there: on 2026-10-11 six repos still ran the pre-cutover process a day after their lean
-PRs merged.
+session there.
```
```diff
-  asks Geoff only what the plan could not foresee (`pass-core`, "Lifecycle" step 1 and "Judgment
-  calls"). Each item
-  below this one was added from a past pass's planning miss.
+  asks Geoff only what the plan could not foresee ("Lifecycle" step 1 and "Judgment calls").
```
```diff
-  its own. Each carries the traced-cause standing answer in `pass-core` "Lifecycle" step 1, so only
+  its own. Each carries the traced-cause standing answer in "Lifecycle" step 1, so only
...
-  its structural fix (B3c, 2026-10-19: a five-read cap, an escalation traced to a blueprint, then
-  a rollback handler that kept looping after its patch).
+  its structural fix.
```
```diff
-  value no file holds is asked at design time (Pass 1, 2026-10-19: the recovery address was
-  already on file).
+  value no file holds is asked at design time.
...
-  pre-launch packet (Pass 1, 2026-10-19: a Proton Bridge sign-in surfaced mid-run).
+  pre-launch packet.
```
The next hunk also drops ` (agent-first pass 1, 2026-10-31: `.claude/settings.json` and a container's `oauth.env`)` from line 370.
```diff
-  and accepts it, checked by a launch that no longer prints "Workspace not trusted" (Survey Pass
-  1, 2026-10-22: the launch refused until Geoff accepted it).
+  and accepts it, checked by a launch that doesn't print "Workspace not trusted".
```
```diff
-  gets, including a host that lacks a prerequisite (Pass W, 2026-10-19: the thinkpad question).
+  gets, including a host that lacks a prerequisite.
```
```diff
-  cleanup (2026-10-19: the 1Password cache and the dock pin).
+  cleanup.
```
```diff
-`docs/HISTORY.md` and post-mortems stop growing (ruling 8). A lesson lands where it executes: ...
+nothing is appended to `docs/HISTORY.md` or to a post-mortem. A lesson lands where it executes: ...
```

## Landing

The `log-project` description hunk changes a trigger, and the `site-implementer` step 1 hunk changes a step. Neither qualifies as a direct change, so this diff goes through a `runner` pass with a packet. The `claude-infra` hunk needs your read in that packet because it records the "Direct changes" exception in the skill that governs these edits.

Each hunk here is a fact or wording change, so I checked them against the repository, not with before-and-after behavior probes. The flagged re-test items need your evals before any removal.
