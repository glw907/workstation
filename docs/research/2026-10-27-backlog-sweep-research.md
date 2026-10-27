# Backlog sweep proposal: research check

Proposal read: `~/.dotfiles/.claude/worktrees/backlog-sweep/claude/.claude/skills/pass-core/SKILL.md` line 31 (commit ab79f16), and `log-issue/SKILL.md` in the same worktree.

## Local facts (measured 2026-10-27, `~/Projects/*/BACKLOG.md`)

Open items: dubplate 88, cairn-cms 44, workstation 35, servers 33, aksailingclub-legacy 29, poplar 26, approval-queue 13, aksailingclub-org 11, ecxc-ski 7, xcathletes-org 7, 907-life 3, cairn-themes 2, cairn-pub 1, phonebook 0, survey 0. About 300 open items in all.
Filed dates: every open item carries one except dubplate (7 of 88 dated; its items use `- [ ] #N` without the log-issue format) and cairn-themes (0 of 2). dubplate's BACKLOG.md also holds a roadmap section ("Path to 0.8") that is not a list of items.

## 1. Anthropic guidance

- Ground in code, never at face value. Supports the file:line requirement. "Never speculate about code you have not opened." Source: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices> (investigate_before_answering). Also: "it's crucial for the agents to gain 'ground truth' from the environment at each step." Source: <https://www.anthropic.com/engineering/building-effective-agents>
- Fresh, read-only reviewer. Supports the read-only dispatch. "A fresh reviewer does help, because it hasn't seen your reasoning." And: "Give a custom subagent in `.claude/agents/` only `tools: Read, Grep, Glob`. Now it's a reviewer that can't edit anything." Source: <https://code.claude.com/docs/en/best-practices>
- Cost of subagents. Argues against sweeping the whole backlog at every pass. "What they cost you is mostly tokens ... a fresh subagent first has to gather context your conversation already had, so it can end up *slower*." Source: <https://code.claude.com/docs/en/best-practices>. "Delegation is worthwhile for genuinely independent, sizeable tracks of work, but it multiplies cost and time when applied to small tasks." Source: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>
- Scope. Argues against the unrelated "15-minute" fold. "Claude Opus 5 can also expand the scope of a task, adding steps that weren't requested". And "Don't add features, refactor code, or make 'improvements' beyond what was asked. A bug fix doesn't need surrounding code cleaned up." pass-core already quotes both. Sources: the Opus 5 page; <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>. Long-running harness work found agents do better "on only one feature at a time", which was "critical to addressing the agent's tendency to do too much at once." Source: <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
- Agents editing their own tracking list. The same harness post had agents edit the feature list "only by changing the status of a passes field", called removing or editing tests "unacceptable", and noted Claude "marks features as done prematurely." That is a caution for the "already done" and "drop" verdicts. Source: same post.
- Simplicity. "finding the simplest solution possible, and only increasing complexity when needed." Source: building-effective-agents.
- Rule count. "keep the enforced set small ... If you ever find yourself at forty of them, most are probably preferences that Claude could have weighed on its own." Source: best-practices. This is about hooks and deny rules, so applying it to pass-core prose is my judgment.

## 2. Industry practice

- Scrum Guide 2020. Refinement is "an ongoing activity to add details, such as a description, order, and size". The Product Owner may delegate the work, but "Regardless, the Product Owner remains accountable." Source: <https://scrumguides.org/scrum-guide.html>. This backs owner sign-off on drops.
- Shape Up. Under "No backlogs": "Backlogs are a big weight we don't need to carry." "Really important ideas will come back to you." "It's easy to overvalue ideas." "There's no time spent grooming a backlog of old ideas." Source: <https://basecamp.com/shapeup/2.1-chapter-07>. This strongly supports "drop is ordinary". It also undercuts any per-pass grooming ritual.
- Next.js (Sep 2026), the closest analog: an agent researching the backlog. Source: <https://nextjs.org/blog/how-we-closed-1500-github-issues>
  - "inactivity turned out to be a poor stand-in for relevance ... A timestamp can't tell those cases apart, so we closed some reports we should have kept."
  - The agent "Looks for evidence that contradicts its initial conclusion." It is "read-only outside its sandbox ... cannot act on its conclusions." Its score was kept "conservative. A failed reproduction alone is not enough to recommend closing."
  - Close reasons: already fixed 37%, duplicate 19%, expected behavior 16%, no longer reproducible 6%, unsupported 5%, other 17%.
  - Humans "read the evidence behind every result". A GitHub Action lets anyone reopen an issue the bot closed.
  - Ongoing work runs on a cadence, not per change: "every Monday, `closability` researches up to 100 open issues with no activity for at least 30 days, starting with the issues it has never reviewed. If an issue gets new activity, we discard the saved research." Before closing, "a second agent looks for evidence that the issue should stay open."
- Stale bots. Kubernetes marks an issue stale after 90 days, rotten after 30 more, and closes it 30 days after that. A Dec 2022 RFC proposed exempting triaged issues and re-triaging anything untouched for over a year. Sources: <https://groups.google.com/a/kubernetes.io/g/dev/c/GjAn5qLwA64>, <https://github.com/kubernetes/community/pull/6512>. Whether the RFC landed is unverified. Drew DeVault: "There is no shame in having a lot of open issues". He sees issues as "A space for the community to work". Source: <https://drewdevault.com/blog/stalebot/>. That critique concerns community trackers. It barely applies to a private, agent-filed backlog (my judgment).
- Agent-filed volume. Agents are making noisy issues and PRs a known problem. Maintainers asked to block Copilot-generated issues (<https://socket.dev/blog/oss-maintainers-demand-ability-to-block-copilot-generated-issues-and-prs>), and Hugging Face reports most agent PRs to transformers were noise or duplicates (<https://huggingface-open-source-agent-contributions.hf.space/>). Both are secondary accounts; I read them only through search summaries.

## 3. Recommendations

(a) Cadence. Split the sweep in two. At each pass design, a scoped sweep covers only items tagged with the pass's initiative or naming files the pass touches. Only these can fold. A full sweep runs on request or when a repo has unreviewed items past a threshold, oldest-unreviewed first, as Next.js does. A full file:line sweep of dubplate's 88 items at every pass costs too much for what it returns (Anthropic cost quotes; the rest is my judgment).

(b) Provenance and expiry. Keep the filed date and add provenance (filing pass or PR). Set no automatic expiry: Next.js and Kubernetes both found inactivity a poor proxy. Instead stamp each item `swept YYYY-MM-DD: keep (reason)`, so the next sweep skips fresh verdicts and re-reviews stale ones. Normalize dubplate's 81 undated items first.

(c) Intake bar. Make it light and structural, not a value judgment. Each item needs a mechanism (file:line or a reproducible symptom), the consequence if it is left alone, and a duplicate check against open items. The "Found, not done" path skips confirmation, so most agent noise enters there; apply the bar there. A strict value bar would fight Anthropic's advice to "ask it to report everything and filter in a separate pass instead" (Opus 5 page, on review findings; applying that to intake is my judgment).

(d) Approval of the design approves the backlog edits. This is sound, given Scrum's owner accountability and the human review in Next.js, if two conditions hold. First, drops appear in their own compact table (item, verdict, one-line evidence), not inside the prose. Second, a dropped item moves to Done marked "dropped: reason" rather than being deleted, which is the reopen window Next.js built. Git history alone is a weak reopen path (my judgment).

(e) Fold bar. "Lives in lines the pass already rewrites" is sound. Drop the second branch, "~15 minutes and low risk", or confine it to the same files or test surface. Otherwise it is the scope expansion Anthropic warns about, and many small folds add up and break pass estimates (my judgment). A fold also inherits the pass's risk class: no fold into or out of `auth-data` unless it is in scope.

(f) What the rule misses or over-engineers.
- Missing: a duplicate verdict (19% of Next.js closes). Drops need a contrary-evidence step, as in Next.js's second agent, or at least the rule "a failed reproduction alone is not enough". "Already done" needs the commit or line that did it.
- Missing: what to do with non-item sections such as dubplate's roadmap, and items from initiatives that span repos.
- Over-engineered: a whole-backlog sweep at every design, and "covered by the design" kept as a verdict separate from fold. The rule also sits inside an already overloaded paragraph about Cloudflare hosting in pass-core; give it its own bullet.
