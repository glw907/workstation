Quote verification 2026-10-10: 121 quotes checked in the ranked list and sections 1, 2, 4, 5, and 8; 119 verified, 2 corrected, 0 not found.

# Anthropic's current guidance on agentic software development, mapped to a small solo project (2026-10-10)

Method: pages were fetched on 2026-10-10 with WebFetch from anthropic.com/engineering, claude.com/blog, code.claude.com/docs, and platform.claude.com/docs; one WebSearch located the 2026 engineering posts. The docs pages carry no publication date, so they are labelled "live docs, fetched 2026-10-10"; the model-specific pages (Opus 5.5, Sonnet 5.5, Fable 5) are the newest and name those models directly. WebFetch returns text through a small summarizing model, so each quoted string below is as returned by the tool and should be re-checked on the page before it is cited outside this repo. Where a point comes from a search snippet and not a fetched page, it is marked SECONDARY. Where Anthropic gives no guidance on a question, the section says so.

## 1. Start simple; workflows vs agents; orchestrator-workers; evaluator-optimizer

Source: "Building effective agents", anthropic.com/engineering/building-effective-agents, published Dec 19, 2024 (still the cited base in the 2026 posts below).

- "we recommend finding the simplest solution possible, and only increasing complexity when needed." [verified 2026-10-10]
- "you should consider adding complexity only when it demonstrably improves outcomes." [verified 2026-10-10]
- "add multi-step agentic systems only when simpler solutions fall short." [verified 2026-10-10]
- "This might mean not building agentic systems at all." [verified 2026-10-10] and "For many applications, however, optimizing single LLM calls with retrieval and in-context examples is usually enough." [verified 2026-10-10]
- Workflows: "systems where LLMs and tools are orchestrated through predefined code paths." [verified 2026-10-10] Agents: "systems where LLMs dynamically direct their own processes and tool usage" [verified 2026-10-10]. Workflows give "predictability and consistency for well-defined tasks" [verified 2026-10-10]; agents suit "flexibility and model-driven decision-making" [verified 2026-10-10].
- Orchestrator-workers: "a central LLM dynamically breaks down tasks, delegates them to worker LLMs, and synthesizes their results" [verified 2026-10-10]; fits when "subtasks aren't pre-defined".
- Evaluator-optimizer: "particularly effective when we have clear evaluation criteria, and when iterative refinement provides measurable value." [verified 2026-10-10]
- Frameworks: "they often create extra layers of abstraction that can obscure the underlying prompts" [verified 2026-10-10]; "They can also make it tempting to add complexity when a simpler setup would suffice." [verified 2026-10-10]
- Coding: "Code solutions are verifiable through automated tests" [verified 2026-10-10], agents iterate "using test results as feedback" [verified 2026-10-10], and "human review remains crucial for ensuring solutions align with broader system requirements." [verified 2026-10-10]

Reinforced Jan 23, 2026, claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them: "Start with the simplest approach that works, and add complexity only when evidence supports it." [verified 2026-10-10] A well-built single agent "can accomplish far more than many developers expect." [verified 2026-10-10]

Implication for a small solo project: every added reviewer, lens, or ledger needs a measured failure it prevents; the default is one capable agent plus tests.

## 2. Claude Code best practices (loop, plan size, CLAUDE.md, subagents, context, headless, worktrees)

Source: code.claude.com/docs/en/best-practices (live docs, fetched 2026-10-10; anthropic.com/engineering/claude-code-best-practices now 308-redirects here).

- Core constraint: "Claude's context window fills up fast, and performance degrades as it fills." [verified 2026-10-10]
- Loop: four phases, Explore, Plan, Implement, Commit. But: "Plan mode is useful, but also adds overhead." [verified 2026-10-10] and "If you could describe the diff in one sentence, skip the plan." [verified 2026-10-10] Planning pays "when you're uncertain about the approach, when the change modifies multiple files, or when you're unfamiliar with the code" [verified 2026-10-10].
- Plan detail: for larger features have Claude interview you, write SPEC.md, then "start a fresh session to execute it." [verified 2026-10-10] "The most useful specs are self-contained: they name the files and interfaces involved, state what is out of scope, and end with an end-to-end verification step that proves the feature works." [verified 2026-10-10] No line count is given; the plan example is a short prompt.
- Verification first: "Give Claude a check it can run: tests, a build, a screenshot to compare. It's the difference between a session you watch and one you walk away from." [verified 2026-10-10] Options ranked by setup: one prompt, a `/goal` condition, a Stop hook as "a deterministic gate" [verified 2026-10-10], or "a verification subagent" [verified 2026-10-10]. "Have Claude show evidence rather than asserting success" [verified 2026-10-10].
- CLAUDE.md: "keep it short" [verified 2026-10-10]. Test per line: "Would removing this cause Claude to make mistakes? If not, cut it. Bloated CLAUDE.md files cause Claude to ignore your actual instructions!" [verified 2026-10-10] "If you emphasize many lines, none of them stands out." [verified 2026-10-10] Failure pattern: "The over-specified CLAUDE.md ... Claude ignores half of it" [verified 2026-10-10]. Memory docs: "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence." [verified 2026-10-10] (code.claude.com/docs/en/memory). Costs docs: move workflow instructions to skills; "Aim to keep CLAUDE.md under 200 lines" [verified 2026-10-10].
- Subagents: "Use subagents to investigate" [verified 2026-10-10] so research stays out of main context; also for post-implementation verification. Sub-agents docs say use the main conversation when "Multiple phases share significant context, such as planning, implementation, and testing" [verified 2026-10-10] or "You're making a quick, targeted change" [verified 2026-10-10], and subagents when "The task produces verbose output you don't need in your main context" [verified 2026-10-10].
- Context: "/clear between unrelated tasks" [verified 2026-10-10]; "If you've corrected Claude more than twice on the same issue ... Run /clear and start fresh" [verified 2026-10-10]. Failure pattern "The kitchen sink session" [verified 2026-10-10].
- Headless and fan-out: `claude -p`; `/batch` splits "across 5 to 30 subagents" [verified 2026-10-10], each in its own worktree; "Test on a few files, then run on all of them" [verified 2026-10-10].
- Parallel and worktrees: separate sessions in git worktrees. Writer/Reviewer: "A fresh context improves code review since Claude won't be biased toward code it just wrote." [verified 2026-10-10]
- Review caution, same page: "A reviewer prompted to find gaps will usually report some, even when the work is sound ... Chasing every finding leads to over-engineering ... Tell the reviewer to flag only gaps that affect correctness or the stated requirements." [verified 2026-10-10]
- Closing: "The patterns in this guide aren't set in stone ... Sometimes you should skip planning" [verified 2026-10-10].

Implication for a small solo project: plan only multi-file or uncertain work, run one fresh-context reviewer filtered to correctness, and keep CLAUDE.md under about 200 lines with the rest in skills.

## 3. Multi-agent cost and when it is worth it

Source A: "How we built our multi-agent research system", anthropic.com/engineering/multi-agent-research-system, published Jun 13, 2025.
- "multi-agent systems use about 15x more tokens than chats." (agents about 4x a chat.)
- "multi-agent systems require tasks where the value of the task is high enough to pay for the increased performance".
- Poor fit: domains needing shared context or many dependencies; "most coding tasks involve fewer truly parallelizable tasks than research".
- Effort scaling embedded in prompts: "Simple fact-finding requires just 1 agent with 3-10 tool calls"; more than 10 subagents only for complex research.

Source B: "Building multi-agent systems: When and how to use them", claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them, Jan 23, 2026.
- "multi-agent implementations typically use 3-10x more tokens than single-agent approaches for equivalent tasks."
- Wins in three cases: when "context pollution degrades performance," when "tasks can run in parallel," when "specialization improves tool selection or task focus." "Outside these situations, the coordination costs typically exceed the benefits."
- "adopt a context-centric view rather than a problem-centric view when decomposing work"; "an agent handling a feature should also handle its tests."
- Role split experiment (planner, implementer, tester, reviewer): "the subagents spent more tokens on coordination than on actual work"; a "telephone game" at each handoff.
- Verification subagents: "The most significant failure mode ... is marking outputs as passing without thorough testing."

Source C: costs and agent-teams docs (live docs). "Agent teams use approximately 7x more tokens than standard sessions". "Keep teams small." "Start with 3-5 teammates"; "Three focused teammates often outperform five scattered ones." "For sequential tasks, same-file edits, or work with many dependencies, a single session or subagents are more effective." Anthropic gives no recommended count of review subagents per task.

Implication for a small solo project: a chain of implementer, reviewer, and four domain reviewers is the role-based split Anthropic measured as coordination-dominated; keep feature and tests together and use at most one reviewer.

## 4. Long-running agents and harness design

Source A: "Effective harnesses for long-running agents", anthropic.com/engineering/effective-harnesses-for-long-running-agents, Nov 26, 2025.
- Initializer session sets up the environment; later sessions work "on only one feature at a time" [verified 2026-10-10], "critical to addressing the agent's tendency to do too much at once." [verified 2026-10-10]
- State: a feature list (JSON, initially all "failing"), chosen because "the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files" [verified 2026-10-10]; a `claude-progress.txt` log; descriptive git commits to revert and recover.
- Each session starts: "Read the git logs and progress files to get up to speed" [verified 2026-10-10].
- Testing: "Claude mostly did well at verifying features end-to-end once explicitly prompted to use browser automation tools" [verified 2026-10-10].
- Failure modes: "Claude declares victory on the entire project too early" [verified 2026-10-10], "marks features as done prematurely" [verified 2026-10-10], leaves undocumented bugs.
- Open question: "it's still unclear whether a single, general-purpose coding agent performs best across contexts" [verified 2026-10-10].

Source B: "Harness design for long-running application development", anthropic.com/engineering/harness-design-long-running-apps, Mar 24, 2026. Planner, generator, evaluator architecture. "every component in a harness encodes an assumption about what the model can't do on its own." [verified 2026-10-10] Results: solo run 20 min and $9 against the full harness at 6 hr and $200, "over 20x more expensive." [verified 2026-10-10] On Opus 4.5 "I was able to drop context resets from this harness entirely" [verified 2026-10-10]; the sprint construct was removed and the evaluator moved to one pass at the end. See section 8 for the evaluator quote.

Source C: prompting best practices, platform.claude.com (live docs): "Starting fresh versus compacting" [verified 2026-10-10] ... "Claude's latest models are extremely effective at discovering state from the local filesystem." [verified 2026-10-10] State: "Use structured formats for state data" [verified 2026-10-10], "unstructured text for progress notes" [verified 2026-10-10], "Use git for state tracking" [verified 2026-10-10], "Emphasize incremental progress" [verified 2026-10-10]. Suggested start-up: "Review progress.txt, tests.json, and the git logs." [verified 2026-10-10]

Implication for a small solo project: carry state in one progress file, one structured task list, and git, and start each unit in a fresh session; STATUS, HISTORY, ROADMAP, post-mortems, and a friction log are far more ledger than any Anthropic harness uses.

## 5. Verification and review

- Tests are the oracle. Best practices (live docs): "If you can't verify it, don't ship it." [verified 2026-10-10] Building effective agents: "Code solutions are verifiable through automated tests" [verified 2026-10-10].
- Grade outcomes. "Demystifying evals for AI agents", anthropic.com/engineering/demystifying-evals-for-ai-agents, Jan 9, 2026: "it's often better to grade what the agent produced, not the path it took." [verified 2026-10-10]; code graders fit coding ("does the code run and do the tests pass?") [verified 2026-10-10]; "LLM-as-judge graders should be closely calibrated with human experts" [verified 2026-10-10]; once robust, "it's sufficient to use human review only occasionally." [verified 2026-10-10] Start with "20-50 simple tasks drawn from real failures" [verified 2026-10-10]; "take the 80/20 approach in the beginning" [verified 2026-10-10].
- Separate Claude as reviewer: best practices recommends a fresh-context reviewer ("A fresh context improves code review") [verified 2026-10-10] and a subagent adversarial pass "before treating a task as done" [verified 2026-10-10], with the correctness-only caveat quoted in section 2. Multi-agent blog: verification subagents fail by passing outputs without real testing.
- Newer models self-verify. Opus 5 prompting page (live docs): "Claude Opus 5 verifies its own work without being told to. If your prompt contains explicit verification instructions ('include a final verification step for any non-trivial task,' 'use a subagent to verify'), remove them: instructions like these cause over-verification on Claude Opus 5, and removing them reduces wasted tokens with no loss in quality. The same applies to legacy harness scaffolding that adds separate verification steps." [verified 2026-10-10]
- Reviews at a given effort: Opus 5 "reviews code with high precision and recall" [verified 2026-10-10]; "If your review prompt says 'only report high-severity issues' or 'be conservative,' the model may follow that instruction literally and report less; ask it to report everything and filter in a separate pass instead." [verified 2026-10-10]
- Gates: Claude Code best practices lists a Stop hook as "a deterministic gate" [verified 2026-10-10]; its CLAUDE.md example says "Prefer running single tests, and not the whole test suite, for performance" [verified 2026-10-10]. Auto mode post, Mar 25, 2026: "Manual prompts sit in the middle, and in practice users accept 93% of them anyway." [corrected 2026-10-10] and that leads to "approval fatigue" [verified 2026-10-10]; it is "not a drop-in replacement for careful human review on high-stakes infrastructure." [verified 2026-10-10] Anthropic gives no guidance on a per-task full-suite gate plus CI wait.

Implication for a small solo project: one fast targeted test run per task as the oracle, one fresh-context correctness review at the end of the pass, the full gate once per pass, and occasional human spot checks.

## 6. Context engineering and skills

- "Effective context engineering for AI agents", anthropic.com/engineering/effective-context-engineering-for-ai-agents, Sep 29, 2025: "find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome." Right altitude: avoid "hardcoding complex, brittle logic in their prompts" and equally "vague, high-level guidance". "bloated tool sets" are a common failure. Just-in-time context via "lightweight identifiers (file paths ...)". Structured note-taking: "the agent regularly writes notes persisted to memory outside of the context window". Closing advice: "do the simplest thing that works".
- "Equipping agents for the real world with Agent Skills", anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills, Oct 16, 2025 (updated Dec 18, 2025): "Progressive disclosure is the core design principle". "When the SKILL.md file becomes unwieldy, split its content into separate files and reference them." Build from observed gaps: "Identify specific gaps ... by running them on representative tasks."
- Skill authoring best practices (platform.claude.com, live docs): "The context window is a public good." "Default assumption: Claude is already very smart." "Keep SKILL.md body under 500 lines for optimal performance." Keep references "one level deep". "Create evaluations BEFORE writing extensive documentation ... Write minimal instructions: Create just enough content to address the gaps". Use low freedom only for fragile operations ("Narrow bridge with cliffs on both sides"); "Open field with no hazards: ... trust Claude to find the best route". "Test with all models you plan to use" (Opus: "Does the Skill avoid over-explaining?").
- Prefer hooks for must-happen rules: "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic".

Implication for a small solo project: write a skill only after observing a failure it fixes, keep each under 500 lines, and move must-always-happen rules into hooks.

## 7. Model and effort selection (planning, execution, review)

Sources: effort docs and per-model prompting pages (platform.claude.com, live docs, fetched 2026-10-10), costs doc.
- Opus 5.5: "Start at medium, the default"; "in Anthropic's testing, Claude Opus 5.5 at medium matches or exceeds Claude Opus 5 at high on coding and knowledge-work evaluations, and on several coding evaluations low comes close to it at much lower cost." "Reserve xhigh and max for work where you've measured a quality gain." "To get less thinking, lower the effort level first." Capabilities: at default medium it matched or beat Opus 5 at high on repository tasks, "in fewer steps and with fewer tokens."
- Sonnet 5.5: "For agentic coding and multistep tool use, start at medium for well-specified tasks and move to high for harder or longer ones." Reserve xhigh and max for work where you've measured a quality gain". At low it "can skip verifying a change." "For the hardest long-horizon work, an Opus model is the better choice."
- Haiku 5.5: "Start with medium for most work, including agentic coding"; low "the cheapest and fastest level". Effort table: low suits "Simpler tasks that need the best speed and lowest costs, such as subagents"; xhigh suits "Long-running agentic and coding tasks (over 30 minutes) with token budgets in the millions".
- Costs doc: "Sonnet handles most coding tasks well and costs less than Opus. Reserve Opus for complex architectural decisions or multi-step reasoning." Agent teams: "Use Sonnet for teammates." Costs doc (not the sub-agents page): "For simple subagent tasks, specify model: haiku".
- Review: Opus 5 review "accuracy holds at lower effort settings, which supports a fast pass at review time and a more thorough pass later." 
- Fable 5 prompting page: "Separate, fresh-context verifier subagents tend to outperform self-critique" on long-running tasks; "Start at the top of your difficulty range" (use it for the hardest problems). Anthropic does not publish a "plan on X, execute on Y, review on Z" matrix; the above is the closest.

Implication for a small solo project: run the session on one model at medium, use Sonnet or Haiku for narrow subagents, and spend xhigh or Fable only on a task where a lower tier measurably failed.

## 8. Warnings against process overhead and over-scaffolding

- Harness post (Mar 24, 2026): "every component in a harness encodes an assumption about what the model can't do on its own." [verified 2026-10-10] The evaluator "is worth the cost when the task sits beyond what the current model does reliably solo." [verified 2026-10-10] "for tasks within that boundary, the evaluator became unnecessary overhead." [verified 2026-10-10] "On 4.6, the model's raw capability increased, so the boundary moved outward." [verified 2026-10-10] Advice: "stripping away pieces that are no longer load-bearing to performance" [verified 2026-10-10] with each new model, and "read its traces on realistic problems." [verified 2026-10-10]
- Managed Agents post, anthropic.com/engineering/managed-agents, Apr 8, 2026: "Harnesses encode assumptions that go stale as models improve." [verified 2026-10-10] Context resets "had become dead weight" [verified 2026-10-10] on Opus 4.5.
- Fable 5 prompting page: "Capability improvements at this level are also a good prompt to re-evaluate which instructions, tools, and guardrails are still needed." [verified 2026-10-10] "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality. Review and consider removing older instructions if default performance is better." [verified 2026-10-10] "Instruction-following is improved enough that you can steer most behaviors with a brief instruction rather than enumerating each behavior by name." [verified 2026-10-10]
- Emphasis: "The fix is to dial back any aggressive language. Where you might have said 'CRITICAL: You MUST use this tool when...', you can use more normal prompting like 'Use this tool when...'." [verified 2026-10-10] Also: "If you emphasize many lines, none of them stands out." [verified 2026-10-10] (best practices).
- Overeagerness: Opus 4.5/4.6 "tendency to overengineer by creating extra files, adding unnecessary abstractions" [verified 2026-10-10]; the sample damping prompt says "The right amount of complexity is the minimum needed for the current task." [verified 2026-10-10] Fable 5 sample: "do the simplest thing that works well." [verified 2026-10-10]
- Subagent overuse: Opus 5 "delegates to subagents more readily than prior models ... it multiplies cost and time when applied to small tasks" [verified 2026-10-10]; sample prompt: "do not use subagents to verify or double-check your own work. If one subagent can complete the task, use one rather than several" [verified 2026-10-10]. Deterministic caps: `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, `max_budget_usd`.
- Sonnet 5.5 at xhigh or max "can start its own rounds of review and verification, sometimes with subagents" [verified 2026-10-10]; adding "don't launch reviewer sub-agents unless the user asked for a review" [verified 2026-10-10] "stopped the model from launching reviewer subagents and cut session cost by about a third, with no change in quality." [verified 2026-10-10]
- Opus 5: "Avoid instructing re-checks it already performs ('double-check your answer,' 're-verify before responding') ... add cost without improving results." [verified 2026-10-10]
- Sonnet 5.5: "Don't add features, tests, files, docs or refactors that weren't asked for." [verified 2026-10-10]
- Closing line of best practices: "The patterns in this guide aren't set in stone." [verified 2026-10-10]

Implication for a small solo project: treat each gate, reviewer, and ledger as a stale assumption to retest against the current model, and delete any that a trace shows is not load-bearing.

## Ranked: the 8 guidance points most at odds with the described process

1. Review layering. Opus 5 page: remove "use a subagent to verify" and legacy separate verification steps (over-verification, no quality gain); Sonnet 5.5: no reviewer subagents unless asked (about a third cheaper, same quality). Current process: per-task diff-reviewer, four domain reviewers, and a simplifier at close.
2. Complexity must "demonstrably improves outcomes" [corrected 2026-10-10] (Building effective agents; Jan 2026 blog: "add complexity only when evidence supports it" [verified 2026-10-10]); an evaluator within the model's reliable range is "unnecessary overhead" [verified 2026-10-10] (Mar 2026). Current process: 26 adversarial review rounds with no recorded evidence of defects each caught that tests would not.
3. Role-based multi-agent splits cost more in coordination than work (planner, implementer, tester, reviewer experiment; 3-10x tokens; "an agent handling a feature should also handle its tests" [verified 2026-10-10]). Current process: thin conductor, implementer, reviewer chain.
4. Plan and spec size and ceremony: "If you could describe the diff in one sentence, skip the plan" [verified 2026-10-10]; a self-contained spec names files, interfaces, out-of-scope items, and one end-to-end check, then a fresh session executes it. Opus 5 "performs best when given the complete task specification up front and left to run." [verified 2026-10-10] Current process: 1,200 to 1,700-line plans plus four-lens review, fold, and fold verification. No Anthropic source found that recommends multi-lens adversarial review of plans.
5. Instruction volume and emphasis: CLAUDE.md "under 200 lines" [verified 2026-10-10] with the rest in skills, skills under 500 lines, "Bloated CLAUDE.md files cause Claude to ignore your actual instructions" [verified 2026-10-10], dial back aggressive language, and older prescriptive skills "can degrade output quality" [verified 2026-10-10] on newer models. Current process: very long global and project CLAUDE.md plus many mandatory skills.
6. Harness assumptions go stale each model: strip what is "no longer load-bearing" [verified 2026-10-10] and retest with traces. Current process: the pass machinery was built for earlier model limits and is carried forward, not re-justified against Opus 5.5 and Sonnet 5.5.
7. Gate economy: tests as the oracle, but fast and incremental ("Prefer running single tests" [verified 2026-10-10], "Test incrementally" [verified 2026-10-10], Stop hook as the deterministic gate [verified 2026-10-10]); human review only "occasionally" [verified 2026-10-10] once robust. Current process: a 20 to 36 minute full gate plus CI wait on every task; a 28-hour pass.
8. State carried in one progress file, a structured task list, and git, with each unit started in a fresh session ("Review progress.txt, tests.json, and the git logs" [verified 2026-10-10]). Current process: STATUS, HISTORY, ROADMAP, post-mortems, and a friction log updated by ritual at every close.
