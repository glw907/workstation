# Infra sweep spec review: mechanics, feasibility, and failure risk

Target: `docs/superpowers/specs/2026-09-28-claude-infra-sweep-design.md` at dotfiles `3f41deb`.
Lens: can each piece be built as stated, and what breaks on day one. Every claim below was
verified by quoting source or by a prototype run on today's tree (scripts in the session
scratchpad); nothing is from memory.

**Counts:** 2 blockers, 8 majors, 11 minors. No new owner fork.

Ranked by consequence. Over-ceremony findings are marked and ranked by their cost.

## Blockers

### X1. The shrink-only comparison is a no-op on the way this repo is actually committed to

- **Where:** spec:161-163 ("compares the file to its copy at `git merge-base HEAD main` ... entries
  for that id may appear in the same commit that introduces the check, and never later").
- **Defect.** On `main`, `git merge-base HEAD main` is `HEAD`, so the checker compares the
  working copy to the last commit. Once a grown baseline is committed, growth is invisible
  forever. This is the common case, not an edge: `git log --first-parent --since=2026-09-14 main`
  shows 89 direct commits and 0 merges. The dotfiles `pre-commit` hook runs only gitleaks
  (`scripts/githooks/pre-commit:10`), and no pre-push hook or CI exists (`.github/workflows`
  absent), so nothing runs `check.sh` before a direct commit lands. On a branch, a merge-base
  diff is cumulative, so it cannot see *which commit* added an entry. The "same commit that
  introduces the check" rule is unenforceable as written. The spec never says how a new check
  is detected.
- **Fold.** Enforce shrink-only per commit in the pre-commit hook: staged baseline against
  `HEAD:claude/.claude/tooling/ratchet-baseline.json`, which behaves the same on `main`, on a
  branch, and in a worktree. Detect a new check with a `checks` registry inside the baseline
  file. Growth is allowed only for an id absent from `HEAD`'s registry, and a `HEAD` with no
  baseline counts as all-new, which covers pass A's own bootstrap. `check.sh` keeps the
  violation-versus-baseline and stale-entry checks, plus a working-tree-versus-`HEAD` growth
  check. Drop the merge-base clause and the "stale branch" risk (spec:469-470) with it.

### X2. Duplicate-pair fingerprints break on every edit to a baselined paragraph, which chains W and B make

- **Where:** spec:156 (fingerprint "the paragraph pair's shingle hash"), spec:237, and the
  amendments at spec:362-380.
- **Defect.** A hash of the shared shingles changes whenever either paragraph is edited. An edit
  that leaves the pair still duplicated therefore reads as one stale entry plus one added
  entry, and the added entry fails the ratchet with no sanctioned path, since the edit is not a
  new-check commit. The prototype (12-word shingles, paragraphs of 12 or more words, same scope
  as A2) puts the heaviest pairs in exactly the files the next passes edit:
  - `prose-voice-reviewer.md` and `cairn-register-editor.md`: 107 shared shingles. Style-guide-sync
    W3 edits the register editor.
  - `cairn-implementer.md` and `site-implementer.md`: 89, 57, 52, 48, and 40 across five
    paragraph pairs. Pass B2 and B3 edit them, then W5.
  - `docs/voice/{editor,technical-doc-go,technical-doc-web,agent-facing}.md`: one 4-way
    paragraph, 44 shingles, 6 pairs. W4 edits two of them.

  Goal 1 (spec:21) fails at B and again in chain W.
- **Fold.** Key a duplicate entry by (check, sorted file pair) and store the count of
  over-threshold paragraph pairs. Shrink-only means the count may not rise. An edit inside a
  still-duplicated pair keeps the count, and a removal lowers it. Treat an N-way copy as one
  cluster, and let `parity.json` declare N-way groups, not only pairs.

## Majors

### M1. AW-01 as written cannot be built: the runner has no filesystem

- **Where:** spec:115-117, 298, 312, 359-360.
- **Defect.** `pass-execute.js:38-40`: "`repo` is prompt text only: the runner never reads or
  writes that path itself." `pass-execute.js:57-58`: "The workflow runtime has no filesystem or
  exec access." A runner cannot see whether `package.json` exists, so "a checkout with no
  `package.json` ... is rejected at launch" needs a probe agent at launch. The literal fallback,
  requiring `reducedGate` whenever a class is set, breaks today's idiom: 71 plans under
  `~/Projects/*/docs/superpowers/plans` cite the runner, and none sets `reducedGate`.
- **Fold.** AW-01 is one line. `pass-execute-chains.js:164` hardcodes cairn's npm scripts, and
  `pass-execute.js:246` already holds a repo-neutral default ("the repo's type check plus only
  the test files this fix round touched"). Chains adopts that constant. The hardcoded npm
  sentence at `pass-execute-chains.js:249` goes too, which is AW-04's runner side. Nothing is
  rejected, no invocation breaks, and the acceptance at spec:359-360 becomes "renders no npm
  command without a `reducedGate`." The test drops "a no-`package.json` run ... is rejected"
  (spec:312).

### M2. `check.sh` calling `claude-tooling-sync verify` couples the dotfiles gate to machine state and to other repos, and silently false-greens in a worktree

- **Where:** spec:180-182, 201-204, 278.
- **Defect.** There are three problems.
  - `verify` checks live state: `~/.claude.json` MCP servers (`claude-tooling-sync:38-42`) and
    `claude plugin list` (`:94`). A plugin enabled in a branch's `settings.json` before it is
    installed, or a user-scope MCP server added by hand, turns every dotfiles commit's gate red.
  - The collision check globs `~/Projects/*/.claude/skills`. Today that finds three `ship`
    collisions, in `ecxc-ski`, `aksailingclub-sveltekit`, and `aksailingclub-legacy`. The
    dotfiles gate therefore goes red on another repo's change, which contradicts the spec's own
    principle at spec:222-224.
  - `check.sh` calling the tool by `PATH` runs main's copy. Main's `main()` ignores extra
    arguments (`:158-159`, `return verify()`), so `verify --root <worktree>` verifies main's
    tree and exits 0 during pass A. That false-greens pass A's own acceptance line (spec:278).
- **Fold.** `check.sh` invokes `bin/.local/bin/claude-tooling-sync` by repo-relative path and
  runs a tree-only subcommand (`lint --root .`: manifest, seats, descriptions, fork lint, and
  the unmanifested-license check). The machine checks stay in `verify`, which `check-drift`
  runs. The collision check runs in `check-drift` and at closes, with `ship` fixed in A as
  planned. Unknown arguments exit 2.

### M3. Self mode resolves `~/.claude/...` against the live tree, not the tree under test

- **Where:** spec:219-221.
- **Defect.** `~/.claude/{agents,docs,skills,tooling,workflows,...}` are folded symlinks into
  `~/.dotfiles` (main's working tree). In a worktree, a reference to a doc the branch deletes
  still resolves, so the worktree passes and `main` goes red on merge. That hits DC-17's
  deletions, pass E, and the `ship` rename. A reference to a doc the branch adds fails until
  merge. The same applies to `~/.local/bin/<x>`.
- **Fold.** In self mode, rewrite `~/.claude/<stowed dir>` to `<root>/claude/.claude/<dir>` and
  `~/.local/bin/<x>` to `<root>/bin/.local/bin/<x>` before resolving. Add a fixture for each case.

### M4. The bare-path rule seeds a baseline that can never empty

- **Where:** spec:230 ("a bare one fails"), spec:33-35 (E's success test).
- **Defect.** The prototype over agents and authored skills finds 105 bare repo-relative
  backticked paths, 71 of them distinct. Of those, 19 resolve in several repos by design
  (`docs/STATUS.md` in 4, `src/content/`, `.claude/project-tracking.json`, `cmd/`,
  `internal/`), and 8 are placeholders (`docs/internal/facts/<arm>.md`,
  `docs/superpowers/plans/YYYY-MM-DD-<topic>.md`). These are generic conventions in `pass-core`
  and `site-pass` with no absolute form. They can never leave the baseline, which breaks "the
  baseline equals the remaining work" and E's success test. Of the rest, 32 resolve in exactly
  one repo (the real AW-14 and AW-15 class), and 12 resolve nowhere (real dead refs, plus prose
  like `` `\/evil.com` ``).
- **Fold.** A bare path fails only when it resolves in exactly one repo (prefix it) or in none
  (dead). A multi-repo path or one with a placeholder (`<`, `{`, `YYYY`) passes. That keeps
  AW-14, AW-15, and PS-21 and drops about 27 permanent entries.

### M5. Cross-repo entries: the closing repo cannot remove them, the close checks the wrong tree, and 4 repos have no remover

- **Where:** spec:219-224, 266-275, 467-468.
- **Defect.** There are three problems.
  - Repo-scoped entries live in the dotfiles baseline, and stale entries fail. When a site fixes
    its CLAUDE.md, its close goes red on "remove this baseline entry," yet the close "runs the
    checker from the dotfiles `main` checkout, read-only" (spec:467-468). The fix is a dotfiles
    commit, which a site close is not sanctioned to make.
  - `--repo <name>` resolves into `~/Projects/<name>`, which is the main checkout. A cairn-cms
    pass closes on a `.claude/worktrees/<pass>` branch, so the close checks pre-merge `main` and
    misses the break the pass is about to merge. That defeats spec:223-224.
  - `check-drift` covers "every repo under `~/Projects` that has a CLAUDE.md," which is 10 repos.
    Pass F names 6. `dubplate`, `healthy-diet`, `aksailingclub-legacy`, and
    `aksailingclub-sveltekit` would seed entries no pass removes. The seat check alone flags
    their 5 agents (no `effort`, `claude-opus-5` pins).
- **Fold.** Add `--repo-root <path>` so a close points at its worktree. In cross-repo mode, a
  stale entry is a NOTE, and the next dotfiles commit prunes it. Scope cross-repo runs to an
  explicit repo list in the baseline file (the six pass F repos). Anything else is reported,
  never baselined.

### M6. Pass A's acceptance "`check-drift` green on the merged `main`" is unreachable

- **Where:** spec:278-279, 358.
- **Defect.** `check-drift` exits 1 today for reasons outside this sweep. The Brewfile is
  unsatisfied (`claude-code@latest`, `ttyd`, `mise`). The `hcloud` leaf is unmanifested. Plexamp
  is in the flatpak manifest but not installed. `cairn` and `tellgrader` are stray `~/.local/bin`
  executables. Its git-state section also fails on any uncommitted dotfiles file. The weekly
  timer (`check-drift.timer`, next run 2026-10-05) already notifies red, so new Claude-ref
  findings drown in machine drift.
- **Fold.** Accept on the new section(s) only. Add a `check-drift --only claude` section filter
  (a small change) and use it in both pass acceptances.

### M7. The vanished-run exit code cannot be "distinct" from what a gate can exit with

- **Where:** spec:320, 476.
- **Defect.** `cairn-run-gate:129` passes the gate's own status through (`exit $status`). Any
  code chosen for "vanished" can also be a real gate exit: make exits 2, pytest exits 2 to 5,
  and a shell exits 126 or 127. The script already exits 2 for an unknown lane (`:47`). Today the
  vanished path prints "`gate exit: 1`" (`:107-108` then `:126`), which is the very marker every
  prompt treats as terminal, so agents report red. The only consumers of exit codes are LLM
  prompts: 7 files carry "exit 75," and no script branches on it.
- **Fold.** Exit 75 on a vanish with the line "gate vanished; re-issue starts a fresh run," and
  print no `gate exit:`. The existing "on 75, re-issue until `gate exit:`" clause then covers it
  with no prompt edit. Bound the loop with a vanish counter in the state directory: after three
  consecutive vanishes, print `gate exit: 1 (vanished 3 times)`. The test can stage a state
  directory holding a dead pid and no status file.

### M8. The runner-side classifier guard (AW-13) has the same no-filesystem problem

- **Where:** spec:305, 312.
- **Defect.** "Runs once per run, only when the classifier exists" needs a probe to learn that it
  exists. The tier is per task (`resolveGate`, `pass-execute.js:452-474`, over `base..HEAD`), so
  it cannot run once per run.
- **Fold.** One `haiku` existence probe per run, with the result cached. Per-task tier probes
  run only when it exists. Alternatively, take an optional `args.classifier` boolean that skips
  the existence probe.

## Minors

1. **Heading-citation pattern misses the house form** (spec:231). The spec's pattern is the
   parenthesised `` `file.md` ("Heading") ``. The global CLAUDE.md writes
   `` `model-economy.md` "Current state" `` and `` `bluefin-admin.md` "Secrets" ``. In scope, the
   bare-quote form has 5 hits and the parenthesised form 3. Fold: accept both.
2. **Pointerless-spec check is mostly false positives** (spec:235). It matches 13 lines across
   the agents, and about one is a real AW-18. The rest are lines like "you do not read the plan
   file" and "the plan did not cover." Fold: drop the check (C fixes the one row), or match only
   "the spec's" and "per the spec." *Over-ceremony: moderate cost.*
3. **Duplicate-check volume versus the GA-nn review** (spec:158-160, 246-248). Pairs with 3 or
   more shared shingles number 92, across 45 file pairs. At 10 or more, 56 pairs remain across
   21 file pairs. The audit names about 10 rows. Listing every GA-nn "for review" at A's close
   spends attended time on dozens of entries. Fold: A's close summarizes GA-nn counts per check
   and per file pair, and Geoff sees only entries with no plausible owner. *Over-ceremony: high
   cost.*
4. **PASS_CLASSES parity "deep-equal ... and the `pass-core` table"** (spec:307). The
   `pass-core` table (`SKILL.md:84-91`) is prose columns that cannot be deep-equal to the JS
   `mandate` and `bar` strings. The two runners' tables are identical today. The drift lives in
   the helpers: `CLASS_DEFAULT_REDUCED_GATE` and the gate matcher. Fold: extract both tables
   through markers and `new Function`, as `tests/docs-page-chain-derivation.test.mjs:36-51`
   does (runners have a top-level `return`, so they cannot be imported), and deep-equal them.
   Parity-test the helpers too. Hold `pass-core` to the class-name set, the reviewer model, and
   the gate lane.
5. **Seat-check shape unstated** (spec:193-196). `model-economy.md` "Current state" lists seats
   by role, so `seats.json` needs an explicit agent-to-seat map. The spec leaves open whether a
   missing `effort:` fails, and 5 of 8 project agents lack it.
6. **Two tools, one baseline, "unknown check id" fails** (spec:167, 477). Each tool rejects the
   other's ids unless both read a shared registry. X1's `checks` registry resolves this and the
   open item at spec:477.
7. **Pre-commit ruling NOTE** (spec:100-104). It fires on every added `(Geoff, YYYY-MM-DD` under
   `claude/.claude/`. A subagent sees it only in commit stderr, and the tool check plus the
   `pass-core` step already cover supersession. Fold: drop item 2. *Over-ceremony: low cost,
   habituation risk.* If it stays, it must print before the `exec gitleaks`
   (`pre-commit:10`).
8. **Dependency-range check parses prose** (spec:270-271). RC7's own response is "point at the
   source, don't quote the pin." Fold: fail any quoted version range in a repo CLAUDE.md. That
   is simpler, and it needs no `package.json` parse.
9. **No rollback line for A and B.** Folded symlinks make a merge live at once. Chain W records
   its merge SHA for `git revert -m 1`. Fold: A and B do the same.
10. **AW-20 misses one prompt.** `docs-page-chain.js:198` restates the exit-75 protocol, and B1's
    Files omit it. W1 edits that file. Fold: name it in W1's outcomes, or in B.
11. **Short retired phrases.** Two seeded phrases, "sleep 30" and "currently 1.26," are two words
    long, so both must be marked exact (spec:242). This belongs in the seeding step.

## What holds up

- Orphan docs: 3 true orphans out of 20 files, a clean signal.
- Memory citations: 3 hits, all resolvable.
- The fork lint: 4 hits, all in `register-check`, matching PS-06 and PS-20.
- The description cap: 8 skills over 500 characters, matching CS-8, CS-17, and PS-28 plus
  vendored `vhs-cli-demos`.
- The unmanifested-LICENSE check: `vhs-cli-demos`, plus `vale-setup`'s
  `LICENSE.vale-agent-tools`, which is already manifested.
- The retired-phrase list: straightforward.
- Fixture-driven tests: feasible with the existing pytest and node patterns.
- Running A and B per task with an explicit `bash scripts/check.sh` gate avoids today's runner
  defects, as spec:461-464 says.
