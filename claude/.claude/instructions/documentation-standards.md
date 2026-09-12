# Documentation Standards

This file sits under `~/.claude/docs/authoring-charter.md` and applies only where the charter and the `writing-voice` router name no standard for the audience.
Standards for technical documentation in this project. Drawn from production experience. These rules exist to prevent the most common failure modes: vague instructions, silent stale content, and docs that describe the wrong thing.

---

## Diátaxis: Know the type before you write

All technical documentation falls into one of four types. Mixing types in one document
creates confusion.

| Type | Question it answers | When to use |
|------|---------------------|-------------|
| **Tutorial** | "How do I get started?" | First-time setup walkthrough |
| **How-to guide** | "How do I accomplish X?" | Adding a route, deploying, migrating data |
| **Reference** | "What are all the values/options?" | Config tables, schema, env vars, routing tables |
| **Explanation** | "Why does it work this way?" | Architecture decisions, tradeoffs, ADRs |

Do not put step-by-step procedures in a reference doc. Do not put exhaustive option tables
in a how-to guide. Decide the type, then write only that type.

---

## Architecture first

Every document covering a system should open with an architectural orientation before any
procedural or reference content. Even one paragraph:

- **What this system is** and its role in the stack
- **How it connects** to other systems (data flows, triggers, auth)
- **What it does not do** (explicit scope boundaries prevent confusion)
- **Key decisions and tradeoffs** (why this approach over alternatives)

---

## Inline Architecture Decision Records (ADRs)

When a document describes a significant design choice, record it explicitly inline:

```markdown
**Decision:** Use Cloudflare Workers for the API layer rather than a separate server.
**Rationale:** Co-location with CDN eliminates cold-start latency; no infrastructure to manage.
**Tradeoffs:** CPU time limits (10ms free, 50ms paid); no long-running processes; limited SQL (no full-text search).
**Date:** 2026-01-15
```

No formal ADR template required. Inline records in explanation documents are sufficient.
Include a date so future readers can evaluate whether circumstances have changed.

---

## Precision and naming

Be precise. Vague technical documentation is worse than no documentation.

| Instead of | Write |
|---|---|
| Set up the environment | Run `source ~/.bashrc`; the Bash tool shell does not load profile files automatically |
| Deploy the worker | `cd myproject && npx wrangler deploy` (specify the directory; running from the wrong one sets secrets on the wrong Worker) |
| The webhook validates the signature | Compute HMAC-SHA256 over the raw body using the full secret string as UTF-8 bytes |

**Name things exactly.** Use the exact name of the Cloudflare Worker, GitHub Actions job,
environment variable, or config key, not a generic description.

**Include the "why" for non-obvious choices.** If a config option has a specific value for
a non-obvious reason, say so. If a workaround exists because of a third-party limitation,
say so.

---

## Page titles and filenames

**Titles:** Include a type suffix ("Guide", "Reference") only when it does disambiguation
work (when sibling pages cover the same system from different angles). Omit it when
the content type is already clear from context.

**Filenames:** Reflect the subject, not the full title. Drop leading gerunds
("Managing", "Configuring") and use the noun. Omit type suffixes from slugs.
Short slugs are preferred when unambiguous in context.

---

## Code and configuration examples

- Show complete, runnable examples, not pseudocode
- Include context: file path, function name, working directory for CLI commands
- Use fenced code blocks with language hints
- For API calls: full URL, method, required headers, expected response shape
- Use actual values from this project, not invented placeholders

---

## Document structure (most stable → most volatile)

1. **Overview / purpose:** what this system does
2. **Architecture:** how it is built
3. **Configuration and setup:** what values are set where
4. **Operations:** how to deploy, debug, maintain
5. **Reference tables:** routes, schema, env vars (put these last; they change most)

---

## Keeping docs current

Update the relevant doc in the same commit as the code change it describes.

If a document is known to be out of date, add a visible warning at the top. Do not leave silent stale content. Readers trust what they read.

---

## What to avoid

- Describing code that already documents itself
- Invented examples (use real Worker names, real env var names, real values)
- Copying official docs (link instead)
- Version numbers without dates ("Hugo 0.155.1 (January 2026)" ages better than just a version)
- One massive doc per subsystem (split reference from explanation)
