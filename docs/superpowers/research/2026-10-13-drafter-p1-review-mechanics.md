# Pass 1 plan review: mechanics and feasibility

Reviewer: `plan-reviewer`, at commit 456b409. Saved by the planning session, every finding kept. `plan:N` is `docs/superpowers/plans/2026-10-13-drafter-p1-foundations-plan.md`.

Verdict: 9 majors, 1 owner fork, 15 minors, no blocker.

Verified: go-toml v2.4.3 newest; strict mode returns `*toml.StrictMissingError` with `Key()` and 1-based `Position()` for nested tables, map-of-struct tables (`[seat.draft]`, `[models."claude-haiku-5.5"]`), and top-level keys; wrong type gives `*DecodeError` with position; pointer fields stay nil when unset. BurntSushi v1.6.0 has no per-key position. `flock` on a second descriptor in one process is refused (EAGAIN) and succeeds after unlock (flock(2): descriptors "are treated independently by flock()"). `git check-ignore -q`: 0 ignored, 1 not, 1 for a tracked file even when listed, 128 outside a repo. `git rev-parse --git-common-dir` is relative unless `--path-format=absolute`. `drafter-gate.sh` works as written. Tools present: `gitleaks`, `gh`, `jq`, the skills, `diff-reviewer`, `claude-clock-stop`; `drafter` is in `bluefin/untracked-bin.txt`. No cairn plan trips the new P1.1 checks. Path 175 (3x line 360).

## Major (correctness)

1. plan:136-139. The crossLinks shape claim is wrong: in `~/Projects/cairn-cms/docs/internal/outlines/*.json` some `from`/`to` are repo paths (`docs/reference/guidance.md`, `docs/extend/upgrade-cairn.md -> debug-your-site`, `architecture -> docs/reference/README.md`), and `claude-code.json` has `to` slugs only in `extend.json`. A strict shape check exits 2 on cairn's real outlines and breaks the live chain's plan loop (`docs-page-chain.js:1121`). Fold: `from`/`to` are a slug or a repo-relative path; resolve slugs across every `--outline`; an unresolvable `to` is a warning, never an error; a row each for a path entry and a cross-outline slug; a Close step runs the branch binary over cairn's 11 plans with the chain's flags, and any new error goes to Found, not done (blocking the self-merge).
2. plan:131-135. The `<a id>`/`<a name>` evidence is wrong: hast-util-sanitize's default schema clobbers `id` and `name` with `user-content-` (lib/schema.js:139-140); cairn.pub's `src/lib/docs/link-policy.ts` `stripAnchorClobberPrefix` strips it from `id` only, so `<a name>` anchors are broken. Fold: count `<a id>` only, citing link-policy.ts; detect from goldmark `RawHTML` and `HTMLBlock` nodes, never inside code; a row with `<a id>` inside a fence that doesn't count.
3. plan:78-79, 193-196, 244-245. `Validate` has no scope outside a project: it requires `gate.command` and `prompts` (project and local only), so pass 2's smoke and `drafter spend`, `drafter config` outside a git tree, and P5.7's "outside any project resolves the user layer with no refusal" all fail. Fold: split into a money part (`workspace_id`, caps, prices for named models) and a run part (`gate.command`, `prompts`, seats), or a scope argument; `drafter config` outside a project checks money only; state in Interfaces.
4. plan:96-104, 223-225. `Prune` can delete a resumable run (rule "every page accepted or escalated", no pending status; a `cycle cap` stop with unstarted pages is pruned, against the spec's "a stopped run of any age is kept"), and a missing, malformed, or other-schema state breaks every later start. Fold: keep any run whose `Stopped` is set; pass 5 lists every page at start, add `pending`; skip and keep runs with absent, malformed, other-schema state or a non-run-ID directory, never erroring; missing `stateDir` or `runs/` returns nil; rows for each, plus "Stopped set, every page accepted: kept".
5. plan:190-192. Placeholder grammar collides with shell `${...}` (P5.7's `${arm}`, P5.5's `$PWD`). Fold: placeholders `\{(page|brief|slug|baseline)\}` only where not preceded by `$`; other `{identifier}` not preceded by `$` refused; clean-twin row with `${arm}` and awk `'{print $1}'`.
6. plan:64-65, 190. TOML spelling of `index_link_command` undefined (pass 5.7 writes a bare key). Fold: fix it as `gate.index_link_command`, same in 5.7.
7. plan:165-174, 198-199. No mechanism for the line of a known key (a disallowed-layer key, an out-of-project path, every value check). Probed: `go-toml/v2/unstable.Parser` (`NextExpression`, `Expression().Key()`, `Shape(Range(n.Data)).Start.Line`) yields a line per key. Fold: name the mechanism (one `unstable.Parser` pass building a key-to-line index, pinned version, its own test; or per-layer structs for the disallowed case).
8. plan:161-169. Env reading unstated: table scalars (`seat.draft.model`, `prices.*` with hyphenated IDs, `register`); privileged scalars (`key_command`, `api_base_url`, `state_dir`, `workspace_id`) do read env per spec; empty values (`DRAFTER_PAGE_CAP=` as 0 refuses every stage); relative paths; unknown `DRAFTER_*` (`DRAFTER_DIR`, `DRAFTER_API_KEY`). Fold: enumerate: top-level scalars, `retries.*`, `gate.*`, `facts.*` read env; `seat`, `prices`, `register`, lists don't; privileged scalars do, said explicitly; empty means unset; malformed refused naming the variable; relative path from the working directory; unknown `DRAFTER_*` ignored.
9. plan:175, 207. The check-ignore proof can pass on the unsafe implementation: the dangerous case is a clone committing both `drafter.local.toml` and a `.gitignore` listing it (plain `check-ignore -q` refuses it; `--no-index` would accept). Fold: the refusal row uses a tracked, listed `drafter.local.toml`; the untracked unlisted case is a second row.

## Owner fork

10. plan:21, 153. Risk class of P1.2 (cap resolution, `key_command` out of the committed file). (a) raise P1.2 to `auth-data` (loses the self-merge); (b) keep `ordinary`, write the P1.2 cap, layer-refusal, and check-ignore rows first and name them in the close review's dispatch. Recommend (b).

## Minor

11. plan:181-184. Range checks: caps > 0, `pages_in_flight` >= 1, retries >= 0, `retention_days` >= 1, `max_tokens` >= 1, refused with key and line.
12. plan:181-184. Cross-layer value checks (`gate.lane` vs `gate.protocol`) run on resolved values.
13. plan:74-77, 100, 129. Name the report and exit code for: a git root with no `drafter.toml` (or a local file without one); empty or malformed TOML; `LoadState` absent or malformed; `drafter anchors` on a missing file and on a file with no anchors (`[]`, exit 0).
14. plan:193. Require the `consistency` seat only when `facts.dir` is set.
15. plan:68-72. Define `Price.BatchDiscount` units and the price TOML keys (`cache_write_5m`, `long_context.threshold`, …).
16. plan:85, 232. `NewID` with 4 hex chars collides 1 in 65,536; use 8 from `crypto/rand`.
17. plan:94-95. `TryLock` opens without `O_TRUNC`, truncates and writes the PID after locking; `Release` unlocks and closes, never removes; quote flock(2).
18. plan:87-89, 233. `Repo` uses `git rev-parse --path-format=absolute --git-common-dir`; git tests set `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, and author/committer vars.
19. plan:247-252. The e2e `run` helper passes `os.Environ()`; config rows strip `DRAFTER_*` and set `XDG_CONFIG_HOME` and `HOME`.
20. plan:211. The atomicfile proof passes vacuously on a `CreateTemp` failure. Fold: fail after the temp is written (target is a non-empty directory); assert no temp left and final mode equals `perm`.
21. plan:78, 193. Moving the missing-price check into `Validate` is reasonable; say so in the PR body.
22. plan:240-252. `drafter config` renders by the resolved `output`; pin the every-layer row to `mode`.
23. Optional. plan:124. `docs/../../x` climbs out; use `filepath.IsLocal`.
24. plan:262. Score gate time can't come from `--records <drafter worktree>` (the gate runs from `~/.dotfiles`; `cairn-run-gate` lines 205-206); read `runs.jsonl` filtered on the worktree path.
25. Optional. Executor prompt:7. Plan not on dotfiles `main` yet; `~/Projects/drafter` doesn't ignore `.claude/worktrees/`. Fold: merge the plan branch first; conductor appends to info/exclude.
26. Optional. `tellgrader` missing on pavilion; its PostToolUse hook exits 127 on every edit. Fold: install before launch.
27. Optional. `drafter config --sync` exists only to test the flag layer; keep or test through `Load`.

## Cross-pass interfaces

Pass 2 consumes `Config`, `Prices`, `Price`, `Tier`, `Load`, `Validate`, `atomicfile.WriteFile`, `Repo` (breaks on findings 3 and 15). Pass 3 matches. Pass 4 matches. Pass 5 needs `run.Prune`, locks, `State.Stopped`, `StateSchema` (findings 3 to 6).
