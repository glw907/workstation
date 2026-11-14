# Runbook agents plan: the `runbook` skill and the move to household-it

Initiative: self-hosting
Round: agents (one pass, no conductor)
Pass: 3 `agents`

Design: "How an agent finds things", "The rename", the pass 3 row under "Passes", its items under
"Acceptance", "The finding test", "How it fails", and "Standing answers" in
`~/Projects/initiatives/self-hosting/specs/2026-11-13-household-it-runbook-design.md` (call it "the
design"), approved by Geoff on 2026-11-13 (Approval Queue item 20261113-230244-df1beb). Its
acceptance list is fixed. Passes 1 and 2 merged in glw907/household-it as PR #36 and PR #38
(`c5ba414`).

Class `auth-data` for task T4 alone, `runner` for the rest. The design calls the pass `runner`,
but the `dotfiles-pass` adapter's path map puts `secrets/**` in `auth-data`, so T4, which edits
`secrets/registry.md`, takes that class ("Decisions", D-1). Worktree `~/.dotfiles/.claude/worktrees/runbook-agents` on
branch `runbook-agents`, cut from `origin/main` at `3c9389a`. Push target `glw907/workstation`, PR
base `main`. Executor `workstation-runbook-agents`, Sonnet at `medium` with the Fable advisor. The
design gives the pass 150 path minutes, and this plan's path is 145 ("Path").

The PR waits for Geoff. It changes the global `CLAUDE.md`, and its packet carries a command block
only he can run. The executor sends that packet through `approval-packet` and merges on his approve.

## Rulings

None yet. The planner parked this plan on two questions ("Park") and appends Geoff's answers here.

## Pre-flight

Before the run, Geoff has one step: the `decide` document in "Park". The executor launches after his answer.
After the merge he has one command block, written in full under T8. No session edits
`claude/.claude/settings.json`, runs `claude-tooling-sync apply`, or runs `stow -R claude`: auto
mode refuses each (M3), and `round-run.md` standing answer 3 makes them Geoff's. No value is read
from any store, and no secret is touched: T4 edits prose that names stores, never a value.

Permissions checked: no new rule, and no deny rule changes. The planner read all 66 rows of
`~/.local/state/claude-denials.jsonl` (2026-11-01T00:55:05Z to 2026-11-14T06:15:18Z) against each
task's commands. Classes: Self-Modification 10, unexplained classifier 10, Interfere With
Workloads 9, Classifier unavailable 6, Merge Without Review 3, Auto-Mode Bypass 3, Destructive or
Unwanted 3, and one or two each of 18 others. The rows that bear on this pass are the refused edits of a
worktree's `claude/.claude/settings.json` (2026-11-01 to 2026-11-11, Self-Modification or
unexplained), one `stow -d ... -R claude` (2026-11-01), and one unexplained refusal of a `python3`
edit to a project `SKILL.md` (2026-11-10). No task edits `settings.json` or runs `stow`. Every
skill edit uses the Edit or Write tool, never `python3` or `sed` (R-1). No row refuses an edit of
`secrets/registry.md`, a doc, `CLAUDE.md`, `BACKLOG.md`, or a unit file, or a nested `claude -p`
session. The trigger test's nested sessions are the probe in M4.

Reviewed: one `standards:plan-reviewer` read (Opus at `medium`) on 2026-11-13; see "Review".

Evidence: the "Mechanisms" table, each row a probe the planner ran on 2026-11-13 or a quoted line,
and the "Searches" section.

## Park

The planner parked this pass before any code, under `round.md` "Parking at planning" and
`round-run.md` standing answer 12, and sends Geoff one `decide` document with two questions.

**Q1. The settings lines.** Acceptance item 1 says the search "prints only the three lines of
`claude/.claude/settings.json` that the packet's command changes", and item 5 names lines 86, 88,
and 431. On `3c9389a` the search prints five lines of that file: 86, 88, 418, 428, and 431. Line
418 is the auto-mode environment text: "built and run from the private repo
github.com/glw907/servers ... through the servers repo's scripts". Line 428 is the ssh allow rule:
"the servers repo's scripts that reach them". The design's evidence table says "3 of its 5 hits
name the repo", but 418 names it outright. No session can edit the file, so on the branch the
search prints five lines however the block is written, and item 1 can't pass as worded. The
advisor confirmed that the park condition holds. Options:

- **Five lines (recommended).** The block edits 86, 88, 418, 428, and 431, and item 1 reads "the
  five lines". All five are auto-mode or permission text, so widening the block is Geoff's call.
- **Three lines.** The block edits 86, 88, and 431. Lines 418 and 428 keep the old name, which
  still means the repo through GitHub's redirect, and go to the backlog. Item 1 reads "the five
  lines, three of which the block changes".

**Q2. The live model.** `claude-tooling-sync verify` exits 1 today on one line: the live
`~/.claude/settings.json` holds `model` `fable`, and the tracked file holds `opus` (`29dd97a`,
2026-11-13 12:54 -0900, "Track the live model choice: opus at high effort"). The live file changed
at 13:35. The block's `claude-tooling-sync apply` writes the tracked value, so it would move the
live model back to `opus`. Options:

- **Keep fable (recommended).** The block also sets the tracked `model` to `fable` before it
  applies, in the same commit. The live file changed after the commit, so `fable` reads as the later choice.
- **Restore opus.** The block applies as it stands, and the live model returns to `opus`.

## What changes

The pass adds one skill, `runbook`, that routes any session on the workstation to the household-it
README. It moves every live workstation reference from `~/Projects/servers` and "the servers repo"
to `~/Projects/household-it`, and from `docs/runbook.md` sections to the system pages and headings
passes 1 and 2 made. It adds the laptop's steps to `docs/STATUS.md`. The skills that hold
procedures keep them and change only their links. The global `CLAUDE.md` swaps two lines for two.

Deployed names keep `servers`: `/opt/servers`, `/var/lib/servers`, `/etc/servers`, the
`servers-backup` and `servers-archive` buckets and their units, the Hetzner project `servers`, the
`servers-claude`, `ws-servers`, `servers-orpheus`, and `servers-ward` names, and any line that means
the two machines.

## Acceptance

Each item is the design's, verbatim. The task and the check under it are how the executor shows
it. A ruling under "Rulings" is how an item reads where it says so. No session edits an item.

0. Every pass: the repo's gate passes (`bash scripts/gate.sh` in workstation).
   - T9: `bash scripts/gate.sh`, bare, on the close head, prints `gate exit: 0`.
1. `grep -rnE 'servers repo|servers/scripts|Projects/servers|glw907/servers' claude bin systemd bluefin secrets docs/model-review` prints only the three lines of `claude/.claude/settings.json` that the packet's command changes. The same search on 2026-11-13 printed 42 lines in 12 files.
   - T2 to T5. On the close head the search prints only `claude/.claude/settings.json` lines, and
     they are the lines the T8 block changes, as Q1's ruling counts them.
2. `claude-tooling-sync verify` passes, and `claude/.claude/skills/runbook/SKILL.md` exists.
   - T1 makes the file, shown by `test -f`. `verify` checks vendored skills and name collisions,
     never an authored skill's content (M6). The T8 block runs `verify` after `apply` and `stow`,
     and the PR records the executor's pre-merge run with its one known `model` line (Q2).
3. The skill's `SKILL.md` is 40 lines or fewer and is the skill's only file. `grep -nwiE 'orpheus|ward|hetzner|voip|907\.life|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' SKILL.md` prints nothing.
   - T1: `wc -l`, `find claude/.claude/skills/runbook -type f`, and the grep, in the PR.
4. The skill loads when it should. Before the merge, the skill is copied into three scratch folders as a project skill. In a fresh session in each, questions 1, 2, 4, 5, and 6 of "The finding test" are each asked twice. Every run loads the skill and gets an answer that names a page under `docs/systems/` or `docs/reference/`. Each of three unrelated questions the plan names (a Svelte question, a Go question, a question about a club site's content) doesn't load it. The transcripts are the evidence.
   - T7: 30 positive runs and 3 negative runs, each a saved transcript; a table in the PR.
5. The merge packet carries one command block for you. It edits lines 86, 88, and 431 of the tracked `claude/.claude/settings.json` to the new path and name, runs `claude-tooling-sync apply` and `stow -R claude`, and removes the link at `~/Projects/servers`. Its check, run from `~`: `/var/home/glw907/Projects/household-it/scripts/tech-mail.sh` runs with no prompt, a session in `~/Projects/phonebook` loads the skill on question 1, and `git -C ~/Projects/household-it worktree list` shows no worktree as prunable.
   - T8 writes the block into the PR body and the packet, with the lines Q1's ruling names.
6. `claude/.claude/CLAUDE.md` has no more lines than it has today.
   - T3: `wc -l claude/.claude/CLAUDE.md` prints 120 or less (120 on `3c9389a`).
7. Every link from a workstation skill or doc into the repo names a file that exists there, and a heading that exists in it: a script in the pull request prints nothing. The pull request also lists each line that mentions "runbook" in prose, with the page it now means.
   - T6: the script's text and its empty output in the PR, and the "runbook" table.

Person-read text in this pass (`docs/STATUS.md`, `BACKLOG.md`, the PR's opening, and the merge
packet) follows `~/.claude/docs/voice/written-for-people.md`, all four steps (Geoff,
2026-11-13). The skill and `CLAUDE.md` are agent-facing and follow Claude Code's skill guidance
(<https://code.claude.com/docs/en/skills>).

## Tasks

Commit per task, by path, never `git add -A`. Run `bash scripts/gate.sh --scope-changed` after each,
bare. Start T7's runs in the background as soon as T1 is committed, and do T2 to T6 while they run.

Every reference into household-it uses one of two forms, so T6's script can read it:

- A path under `~/Projects/household-it/` (or `/var/home/glw907/Projects/household-it/`, or
  `%h/Projects/household-it/` in a unit), optionally with `#<anchor>`.
- A backticked repo path on a line that names `household-it`, such as "household-it's
  `roles/stalwart`". Only a token that holds a `/`, holds no space, and starts with neither `/`
  nor `~` counts, and trailing arguments drop (`scripts/apply.sh ward --apply` reads as
  `scripts/apply.sh`). A reference never wraps across a line break.

A reference to a `.md` file carries `#<anchor>`, the heading's GitHub slug: lowercase, punctuation
other than `-` dropped, spaces as `-`, as the household-it README's links are written (M7).

### T1. The `runbook` skill (20 minutes)

File: `claude/.claude/skills/runbook/SKILL.md`, the skill's only file.

1. Read <https://code.claude.com/docs/en/skills> for the frontmatter and the description's job,
   and `claude/.claude/skills/mail-tend/SKILL.md` as a house model of a description.
2. Frontmatter: `name: runbook` and a `description` that names the design's two moments. The
   first is a question about household infrastructure: a DNS record, a mail route, a server, a
   backup, a phone, an account, an alert, or a credential a household system uses. The second is
   a session that changed one of those systems or was asked to document it. Name no host, address, domain, or credential (item 3's grep). The gate's `claude-tooling-sync lint` caps a description at 500 characters.
3. Body: the repo is `~/Projects/household-it`. Read its `README.md`, the only map, and follow
   its links to the system page or reference page. A session inside the repo also has the repo's
   `CLAUDE.md`. For a change, read `docs/contributing.md` and run the gate,
   `bash scripts/check.sh < /dev/null`, as the repo's `CLAUDE.md` "Working in this repo" says. Say that the skill holds no
   facts, so a session never answers from the skill. Hold no fact the README holds. Tell the
   session to name the page's repo path and heading in its answer (T7 passes on the path).
4. Check item 3: `test -f` first, then `wc -l` 40 or less, one file, the grep prints nothing.

Test: item 3's checks.

### T2. The procedure skills (15 minutes)

Files: `claude/.claude/skills/{mail-tend,maintenance-mode,proton-pass,vps-conventions}/SKILL.md`.
Links and the repo's name only; no step, rule, or trigger changes.

- `mail-tend` lines 9 to 11: `~/Projects/household-it/roles/mail-filters/`; the reference is
  `~/Projects/household-it/docs/systems/mail.md#mail-filters`, and the landing is
  `#the-quick-lane`; "a worktree of household-it". Line 86: "the household-it checkout". Line
  118: `docs/reference/decisions.md#rulings-and-decisions-from-the-mail-filters-pass`, fact 12.
  Line 99's `servers-backup.service` stays.
- `maintenance-mode` line 76: "starts in `household-it`".
- `proton-pass` line 92: household-it's decisions file,
  `docs/reference/decisions.md#rulings-of-2026-10-24`. Line 25 means the machines and stays.
- `vps-conventions` line 86: household-it's `scripts/ward-mail-delete.sh` and
  `scripts/mx-switch.sh`. Line 61's "runbook" is a VPS project's runbook and stays.

Test: `grep -nE 'servers repo|Projects/servers|docs/runbook|servers checkout|in .servers.|servers runbook' ` on the four files prints nothing.

### T3. `CLAUDE.md` and the docs (15 minutes)

Files: `claude/.claude/CLAUDE.md`, `claude/.claude/docs/{bluefin-admin/email.md,bluefin-admin/browsers.md,test-accounts.md,cloudflare-estate/api-tokens.md,cloudflare-estate-inventory.md}`.

- `CLAUDE.md` lines 49 and 50 become two lines: the new path `~/Projects/household-it`, one clause
  naming the `runbook` skill, and `household-it/scripts/tech-mail.sh`, with the untrusted-input
  rule kept word for word. Item 6: 120 lines or fewer.
- `email.md` line 3: `~/Projects/household-it`. Line 7: household-it's
  `docs/reference/decisions.md#rulings-and-decisions-from-the-mail-server-pass`. Read that section
  and `docs/systems/mail.md` first, and name the heading that holds the JMAP quirks, sending setup, and ban
  limits, more than one if they split.
- `test-accounts.md` line 57: household-it's `docs/reference/addresses.md#test-account`.
- `api-tokens.md` line 65: "household-it's scripts". The token name `ws-servers` stays.
- `browsers.md` line 12: `~/Projects/household-it/docs/systems/bookmarks.md#set-up-floccus-on-a-device`.
- `cloudflare-estate-inventory.md` line 6: household-it's
  `docs/systems/cloudflare.md#vendor-docs`, where the plan line now is (M7).

Test: item 6, and the T2 grep on these files.

### T4. `secrets/registry.md` (15 minutes, `auth-data`)

File: `secrets/registry.md`. Wording only: no store name, item, vault, grant, or rotation step
changes, and no value is read.

- The 20 "the servers repo's" lines (321 to 606) become "household-it's". Lines 474, 481, and
  488's "in the servers repo" become "in household-it". Lines 504 and 514 cite household-it's
  `secrets/registry.md`, whose one heading is "Secrets registry": write
  `secrets/registry.md#secrets-registry`, and join 514 and 515 so the reference sits on one line.
- Line 768: `~/Projects/household-it`, `roles/caddy`.
- Line 395: household-it's `docs/systems/cloudflare.md#rotating-a-cloudflare-token`. Line 426's
  servers `docs/runbook.md`, "Bookmark sync", becomes household-it's
  `docs/systems/bookmarks.md#rotate-a-members-password`. Line 636: "the household-it dry run's
  `spamhaus-dqs` row". Line 425's `(servers#21)` is a dated deletion record and stays.
- Lines 319 to 324 (Hetzner project `servers`, token `servers-claude`), 386 (`ws-servers`), the
  `servers-orpheus` and `servers-ward` tunnels, the `servers-backup-*` and `servers-archive`
  buckets, and `/etc/servers` stay.

Any question in this task stops (`advisor.md` "What always stops").

Test: `grep -nE 'servers repo|Projects/servers|glw907/servers|servers runbook|servers dry run|docs/runbook' secrets/registry.md` prints nothing, and `git diff --stat` shows the one file.

### T5. The unit, the Brewfile, the review prompt, and the backlog (10 minutes)

- `systemd/.config/systemd/user/monitor-subscribe.service` line 3:
  `Documentation=file://%h/Projects/household-it/docs/systems/monitoring.md#the-alerts-on-the-workstation`.
  Line 2 means the machines and stays. Run `systemd-analyze --user verify` on the file.
- `bluefin/Brewfile` line 30: "the household-it repo's gate and scripts".
- `docs/model-review/prompt.txt` lines 66 and 67: "run the household-it monthly review", and
  `/var/home/glw907/Projects/household-it/docs/prompts/monthly-review.txt`.
- `BACKLOG.md` #2: "from dubplate to household-it", through `standards:log-issue`'s edit rules.
  Line 32 is closed history and stays.

Test: the recorded search (item 1) prints only `settings.json` lines.

### T6. The link check (15 minutes)

1. Write a stdlib Python script with the Write tool, in the job tmp folder, never the repo, and run
   it as `python3 -I <file>` in a Bash call of its own (the worktree guard refuses a heredoc
   compound). It reads `claude bin systemd bluefin secrets docs/model-review BACKLOG.md docs/STATUS.md` in the
   worktree and finds each reference in the two forms under "Tasks". It checks each against
   household-it at `origin/main`, read with `git -C /var/home/glw907/Projects/household-it show
   origin/main:<path>` and `ls-tree`, never the checkout (M5). The guard refuses `git -C` with a
   `~` path, so every path is absolute. It prints one line for each path
   that doesn't exist, each `.md` reference with no anchor, and each anchor that matches no
   heading's slug. Dated records (`docs/model-review/20*`, `docs/plans/`, `docs/specs/`) are out.
2. Run it until it prints nothing. Put its text and its empty output in the PR.
3. Rerun `grep -rniE 'runbook' claude bin systemd bluefin secrets docs/model-review/prompt.txt BACKLOG.md docs/STATUS.md`
   and put each line in the PR's "runbook" table with the page it now means. The table starts
   from "Searches", S-3.

Test: item 7.

### T7. The trigger test (30 minutes)

1. Make three scratch folders under the job tmp folder, each with a copy of the T1 file at
   `.claude/skills/runbook/SKILL.md`: `a` empty, `b` a `git init` with a one-line README for a
   SvelteKit site, and `c` a `git init` with a `go.mod` for `example.com/tool`. Copy the file
   with `cp`, never through a script that writes `SKILL.md` (R-1).
2. In each folder, ask questions 1, 2, 4, 5, and 6 of "The finding test", twice each, each run a
   fresh session:
   `claude -p "<question>" --model sonnet --effort medium --disallowedTools Bash --output-format stream-json --verbose --max-turns 12 < /dev/null > <transcript>`.
   The skill needs only Read, and `--disallowedTools Bash` keeps an unattended session off the
   servers, which the ssh allow rule would otherwise let it reach.
   Run the three folders side by side as background Bash commands and end them with `TaskStop`,
   never `kill`.
3. Ask each negative once, one per folder:
   - `a`: "In Svelte 5, how do I make a value derived from a prop update when the prop changes?"
   - `b`: "In Go, how do I wrap an error with %w and check for it later with errors.Is?"
   - `c`: "What should the ski club website's home page say to invite families to the junior
     program sign-up?"
4. A small parser in the job tmp folder reads each transcript. A run loads the skill when an
   `assistant` event holds a `tool_use` named `Skill` whose `input.skill` is `runbook` (M4). Its
   answer is the `result` event's text, and it passes when that text names a path matching
   `docs/(systems|reference)/[a-z0-9-]+\.md`. A negative passes only when its `result` event has
   `subtype` `success` and the transcript holds no `Skill` call for `runbook`; a session that
   errored or ran out of turns is rerun.
5. A failed run is traced from its transcript. A fix changes only `SKILL.md`, still inside item
   3, and reruns all 33. The spend ceiling for this task is 20 dollars, summed from each
   `result` event's `total_cost_usd`; one round costs about $5 (M4). The nested sessions load the
   live, pre-merge global `CLAUDE.md` and skills, which still name `~/Projects/servers` and
   `docs/runbook.md`. A failure traced to that text is recorded as its cause, never "fixed" in
   `SKILL.md`, and T8's phonebook check is the proof after the merge. A run that read a
   household-it file differing from `origin/main` (the live session there edited it) is rerun
   once.
6. Keep every transcript of the final round in `~/.local/state/runbook-trigger-test/<run date>/`,
   outside git. The PR gets a table with one row per run: folder, question, run, skill loaded,
   page named, cost. The answers stay out of the public PR.

Test: item 4.

### T8. STATUS and the command block (15 minutes)

1. `docs/STATUS.md`, under "Open steps": fold the laptop's steps into its thinkpad-x1 item. Keep
   it to 60 lines. The first session on thinkpad-x1, after it pulls `~/.dotfiles`, runs:
   ```
   git -C ~/Projects/servers remote set-url origin https://github.com/glw907/household-it.git
   mv ~/Projects/servers ~/Projects/household-it
   git -C ~/Projects/household-it worktree repair ~/Projects/household-it/.claude/worktrees/*
   mkdir -p ~/.claude/projects/-var-home-glw907-Projects-household-it
   cp -r ~/.claude/projects/-var-home-glw907-Projects-servers/memory ~/.claude/projects/-var-home-glw907-Projects-household-it/
   ```
   It makes no link at the old path ("Decisions", D-3). Geoff then opens `claude` in
   `~/Projects/household-it` once and accepts the trust prompt (the design's first planning miss),
   and runs `claude-tooling-sync apply` and `stow -R claude` there. A session can't run those two.
2. Write the command block into the PR body under `## After merge` and into the packet. It runs
   after the merge, from `~`, in a child shell that stops at the first failure and leaves Geoff's
   terminal open. Every step can run again after a partial failure:
   ```bash
   bash -euo pipefail <<'BLOCK'
   cd ~/.dotfiles && git pull --ff-only
   test -f claude/.claude/skills/runbook/SKILL.md   # the merge has landed
   python3 -I - <<'EOF'
   import pathlib
   p = pathlib.Path.home() / ".dotfiles/claude/.claude/settings.json"
   s = p.read_text()
   pairs = [
       ("/var/home/glw907/Projects/servers/scripts/tech-mail.sh", "/var/home/glw907/Projects/household-it/scripts/tech-mail.sh"),
       ("/var/home/glw907/Projects/servers/scripts/claude-mail.sh", "/var/home/glw907/Projects/household-it/scripts/claude-mail.sh"),
       ("the private repo github.com/glw907/servers", "the private repo github.com/glw907/household-it"),
       ("through the servers repo's scripts", "through household-it's scripts"),
       ("the servers repo's scripts that reach them", "household-it's scripts that reach them"),
       ("from a checkout or worktree of github.com/glw907/servers is routine", "from a checkout or worktree of github.com/glw907/household-it is routine"),
   ]
   for old, new in pairs:
       assert s.count(old) == 1 or s.count(new) == 1, old
       s = s.replace(old, new)
   p.write_text(s)
   EOF
   grep -q '^  "model": "fable",$' claude/.claude/settings.json || { test "$(grep -c '^  "model": "opus",$' claude/.claude/settings.json)" = 1 && sed -i 's/^  "model": "opus",$/  "model": "fable",/' claude/.claude/settings.json; }
   git diff --quiet -- claude/.claude/settings.json || git commit -m "Point the household rules at household-it" claude/.claude/settings.json
   git push origin main
   cd ~/Projects/initiatives && claude-worktree-busy ~/Projects/initiatives && git pull --ff-only
   sed -i '17s|github.com/glw907/servers|github.com/glw907/household-it|' 907-rebuild/tools/automode-allow.py
   git diff --quiet -- 907-rebuild/tools/automode-allow.py || git commit -m "Name household-it in the DNS auto-mode rule" 907-rebuild/tools/automode-allow.py
   git push origin main
   claude-tooling-sync apply
   cd ~/.dotfiles && stow -R claude
   test -L ~/Projects/servers && rm ~/Projects/servers || true
   claude-tooling-sync verify
   BLOCK
   ```
   The pairs hold the five lines Q1's first option names; under the second option, the third,
   fourth, and fifth pairs go. The `model` line is Q2's first option; under the second it goes.
   The check follows, run from `~`, with no `set -e`:
   ```bash
   cd ~
   claude -p "Run this exact command and nothing else: /var/home/glw907/Projects/household-it/scripts/tech-mail.sh list 1" --permission-mode default --output-format stream-json --verbose < /dev/null | jq -s '[.[] | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use" and .name=="Bash" and (.input.command | startswith("/var/home/glw907/Projects/household-it/scripts/tech-mail.sh")))] | length > 0 and ([.[] | select(.type=="result")][0].permission_denials | length) == 0'   # prints true
   (cd ~/Projects/phonebook && claude -p "How do I add a DNS record to 907.life?" --disallowedTools Bash --output-format stream-json --verbose --max-turns 12 < /dev/null) | jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use" and .name=="Skill") | .input.skill' | grep -x runbook
   git -C ~/Projects/household-it worktree list --porcelain | grep -c prunable   # prints 0 (and exits 1, which is the pass)
   claude-worktree-busy ~/Projects/household-it && git -C ~/Projects/household-it pull --ff-only || echo "household-it has a live session: pull it when that session ends"
   ```
   The executor checks every line it can on the branch: the Python against a copy of the file
   in the job tmp folder, whose `assert`s all pass and whose result the recorded search then
   matches only on the new names; the `sed` on a copy of `automode-allow.py`; and each `jq`
   filter against a saved transcript. It also runs the Python a second time on the changed copy,
   to show the rerun passes.

Test: item 5, by the dry runs on copies.

### T9. Close (25 minutes)

1. `bash scripts/gate.sh` and `claude-tooling-sync verify` on the close head, bare. Record
   `verify`'s output; its `model` line is Q2's, and any other failing line is the executor's to fix inside its files.
2. `gitleaks git --log-opts=origin/main..HEAD`.
3. One whole-branch `standards:diff-reviewer` against `origin/main`, the design, and this plan,
   and one `standards:web-auth-security-reviewer` read of T4's diff. Then one batched fix chain,
   and `bash scripts/gate.sh` again, bare, on the PR head. A second read's Low findings are folded
   once or filed, and never start another round.
4. Open the PR, out of draft, with `Round: agents`, `Pass: 3`, the `Review:` line, the `Calls:`
   line, `## Acceptance` with each item's evidence, `## After merge` (the T8 block),
   `## Decisions`, `## Planning misses` (Q1 and Q2 with Geoff's answers, per standing answer 9),
   "Found, not done", and the score. The opening follows the two model documents in
   `claude/.claude/skills/approval-packet/references/`.
5. Send the `merge` packet through `approval-packet`, with the command block and its check. On
   approve, run `approval-queue merge <id>`, pull the main checkout as `pass-core` "Close" says,
   and leave through `ExitWorktree` with removal.

### Path

T1 20, then T2 15, T3 15, T4 15, T5 10, and T6 15 run beside T7's 30, so that stretch counts 70.
Then T8 15 and T9 25. The path is 130, plus 15 for one T7 rerun: 145, under the design's 150.

## Mechanisms

| # | Mechanism | Probe or source |
| --- | --- | --- |
| M1 | The recorded search | On `3c9389a`: 42 lines in 12 files, as the design says. `settings.json` 86, 88, 418, 428, 431; `secrets/registry.md` 24 lines (321 to 768); `CLAUDE.md` 49 and 50; `email.md` 3 and 7; `mail-tend` 9 and 11; one each in `test-accounts.md` 57, `api-tokens.md` 65, `proton-pass` 92, `vps-conventions` 86, `prompt.txt` 67, `monitor-subscribe.service` 3, `Brewfile` 30. |
| M2 | Lines 418 and 428 name the repo | Line 418: "built and run from the private repo github.com/glw907/servers ... through the servers repo's scripts". Line 428: "the servers repo's scripts that reach them". Line 431: "from a checkout or worktree of github.com/glw907/servers is routine". |
| M3 | A session can't edit `settings.json` or link a skill | The denial rows under "Permissions checked", and `round-run.md` standing answer 3. |
| M4 | A project skill in a scratch folder loads in a `claude -p` session | In a job tmp folder with a stub `.claude/skills/probe-house/SKILL.md`, `claude -p "<Q1>" --model sonnet --output-format stream-json --verbose --max-turns 8 < /dev/null` exited 0 in auto mode. The `init` event listed `probe-house`, the session called `Skill {"skill":"probe-house"}`, read household-it's `README.md` and `docs/systems/cloudflare.md` with no `--add-dir` and no trust prompt, and named "Zone records". Cost $0.13. The plan review's Sonnet `medium` probe on question 4 with a stub told to cite the page path took 11.1 seconds, 5 turns, and $0.158, and named `docs/systems/backups.md`. A round of 33 runs is about $5. A `-p` run that launches a background Agent exits with no `result` event (#73453). |
| M5 | The household-it checkout is behind | `~/Projects/household-it` is at `8ad5d05`, 11 commits behind `origin/main` (`c5ba414`), with session `household-it-bd` live in it. Between the two, nine files differ: `BACKLOG.md`, `CLAUDE.md`, `README.md`, the new `docs/contributing.md`, `scripts/check-docs.{py,sh}`, `scripts/check.sh`, and two tests. No page under `docs/systems/` or `docs/reference/` differs, so the pages the finding test needs read the same. No session pulls it while the session lives. |
| M6 | What `verify` reads | `claude-tooling-sync` `Paths`: the tracked settings and the skills under `~/.dotfiles/claude/.claude/`, the main checkout. It checks vendored skills against `vendored-skills.json` and name collisions against `~/Projects/*/.claude/skills`; no project has a `runbook` skill. `apply` merges `{**live, **tracked}`, so the tracked `model` wins. `verify` exits 1 today on the live `model` (`fable`) against the tracked `opus`. |
| M7 | The link targets | At `origin/main`: `docs/systems/mail.md` has "Mail filters", "The quick lane", "Technical mailbox"; `cloudflare.md` "Zone records", "Deploy a Worker", "Rotating a Cloudflare token", "Vendor docs" (line 59 holds the Workers Paid line); `bookmarks.md` "Set up Floccus on a device", "Rotate a member's password"; `monitoring.md` "The alerts on the workstation"; `docs/reference/decisions.md` "Rulings and decisions from the mail filters pass" (fact 12), "Rulings of 2026-10-24" (the `me.907.life` line), "Rulings and decisions from the mail server pass"; `addresses.md` "Test account"; `docs/prompts/monthly-review.txt`; `docs/contributing.md`. Every path the registry cites exists. The README links as `cloudflare.md#zone-records`. |
| M8 | `scripts/claude-mail.sh` | Absent at `origin/main` and in all history; line 88's rule names a script that never existed. |
| M9 | `automode-allow.py` | Adds its rules only when they are missing. Only line 17 names the repo: "Publishing 907.life DNS from a checkout or worktree of github.com/glw907/servers is routine ". `~/Projects/initiatives` is on `main`, level with origin, and free. |
| M10 | The unit is a stow link | `~/.config/systemd/user/monitor-subscribe.service` links into the main checkout, so the pull makes it live; `Documentation=` needs no restart. |
| M11 | Trust | `~/.claude.json` marks `~/Projects/household-it`, `~/Projects/servers`, and `~/Projects/phonebook` trusted. |
| M12 | The gate | `bash scripts/gate.sh` on `3c9389a`, run by the executor first as its baseline. |

## Searches

- S-1. The recorded search (M1), rerun on `3c9389a`: 42 lines in 12 files.
- S-2. Prose the pattern misses, all live, all in the tasks: `cloudflare-estate-inventory.md:6`,
  `browsers.md:12`, `mail-tend:10`, `:86`, `:118`, `maintenance-mode:76`, `registry.md:395`,
  `:426`, `:636`, `prompt.txt:66`, `BACKLOG.md` #2, and the stale paths in `email.md:7`
  (`docs/decisions.md`) and `test-accounts.md:57` (`docs/addresses.md`). No `household-infra`
  reference exists.
- S-3. "runbook" lines: `cloudflare-estate-inventory.md:6`, `browsers.md:12`, `mail-tend:9-10`,
  `monitor-subscribe.service:3`, `registry.md:395` and `:426` mean household-it pages (T2 to T5).
  `vps-conventions:61` means a VPS project's runbook (household-it has no presence gate).
  `written-for-people.md:53` and `writing-voice:25,59` use the word in general.
  `bluefin/README.md:105`, `SECOND-WORKSTATION.md`, and `bluefin/bootstrap.sh` mean the
  workstation's own runbooks. `BACKLOG.md:170` names the design as history. All stay.
- S-4. Kept lines that say `servers` and mean something else: `mail-tend:99`,
  `monitor-subscribe.service:2`, `bin/monitor-subscribe:4`, `proton-pass:25`, `retire-project:35`,
  `pass-core` `planner.md:18` and `executor.md:10`, `BACKLOG.md:32`, MCP and language-server
  "servers", and the dated `docs/model-review/2026-11-01-*`.
- S-5. Found, not done, for the PR: household-it's `docs/guides/phonebook-operations.md:166`
  still says "runbook, "Cloudflare""; line 88's rule names `claude-mail.sh`, which never existed
  (M8). Each goes through `standards:log-issue`, the first into household-it's backlog by a
  worktree commit, the second into this repo's.
- S-6. The design swept household-it's backlog, not this repo's. The planner grepped
  `BACKLOG.md` for the repo, the path, and "runbook": only #2 bears on the pass, and T5 folds it.

## Refusals

- R-1. An edit of a `SKILL.md`, `CLAUDE.md`, or a file under `claude/.claude/docs/` is refused.
  Retry once with the Edit or Write tool if the refused call was a shell command. Auto mode's
  allow entries cover a skill edit a plan Geoff approved names, and cover `CLAUDE.md` and the docs
  only with Geoff's approval in the session, so T3 is the likely refusal. On a second refusal of
  a T3 file, write its change as exact replacement pairs in the T8 block, as `settings.json` is,
  and list it in the PR. A second refusal elsewhere is a stop under standing answer 2.
- R-2. A nested `claude -p` run is refused. Rerun it once without `--effort`; a second refusal
  stops T7, and T8 and T9 run on the other items, with the stop in the PR.

## Stops

`round-run.md` "Stops" and its standing answers hold, with the design's five. This pass adds three:

- S-1. T7's spend passes 20 dollars, or a question still fails after a fix of a traced cause and
  one structural rewrite of the description. Stop T7, with the failing transcripts; T8 and T9 run
  on the other items, with the stop in the PR. A cause T7 step 5 traces to the pre-merge global
  text takes no rerun.
- S-2. A link target in T2 to T5 has no matching heading at `origin/main`. Name the nearest
  heading if one holds the fact, and list it in the PR. If none does, it is a household-it
  page gap: file it through `standards:log-issue` there, point at the page without an anchor,
  and list it. T6's script then allows that one line, named in the PR.
- S-3. Any question in T4. Stop.

## Review

One `standards:plan-reviewer` read (Opus at `medium`), 2026-11-13, against `3c9389a` and
household-it `c5ba414`. It confirmed every anchor, line number, replacement string, `sed` target,
`jq` shape, and both questions' premises. It found one blocker and eleven fixes, all folded:

- The T8 block runs in a child shell (`bash -euo pipefail <<'BLOCK'`), so `set -e` can't close
  Geoff's terminal on the check's `grep -c` exit.
- The tech-mail check requires a Bash call of the script and no denial, so it can't pass on a
  session that never ran it.
- Every block step can run again after a partial failure.
- T6's form 2 counts only path-shaped tokens, T4 anchors lines 504 and 514 and joins 515, and
  T6's commands use absolute paths in a script written by the Write tool.
- T4's count is 20 lines, plus 474, 481, and 488; `servers#21` is on 425 and stays.
- The laptop's `worktree repair` names the moved worktrees.
- T1 asks the session to name the page path, which T7 tests for.
- R-1 covers T3's files, with the T8 block as the second-refusal route.
- A negative passes only on a successful `result`.
- T9 reruns the gate after its fix chain.
- T7 records a failure traced to the pre-merge global text instead of fixing `SKILL.md` for it.

Of its notes, these are folded: S-1 names what still runs, M4 carries the measured run, T7 runs
with `--disallowedTools Bash`, M5 and M6 are corrected, the greps catch the prose lines, T1
checks `test -f` and the 500-character cap, a second review's Low findings start no round, the
model `sed` replaces the JSON round trip, the initiatives step has a busy check, and S-6 records
this repo's backlog sweep.

## Decisions

- D-1. [advisor] The class is `auth-data` for T4 and `runner` for the rest, with a
  `standards:web-auth-security-reviewer` read at close. The adapter's path map puts
  `secrets/**` in `auth-data`.
- D-2. T7's sessions run Sonnet at `medium`, the executor's model, and the cheaper of the two the
  workstation runs; Geoff's own check in T8 runs his default model.
- D-3. The laptop gets no link at `~/Projects/servers`. Its dotfiles pull already carries the
  settings with the new path once Geoff's block has run on pavilion, so a link there would need a
  removal step of its own. A laptop that opens before then gets a plain failing path, as the design's "How it fails" says.
- D-4. The link check runs from the job tmp folder and its text goes in the PR. The design's
  file list adds no script to the repo.
- D-5. The trigger transcripts stay out of git, in `~/.local/state/`, since the answers quote
  household pages into a public repo.
