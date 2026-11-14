---
name: runbook
description: Use for a question about household infrastructure (a DNS record, a mail route, a server, a backup, a phone, an account, an alert, or a credential one of those systems uses), and after a session changed one of those systems or was asked to document it. Routes to the household-it repo's README. Holds no facts.
---

# Runbook

The household's infrastructure is documented in one repo, `~/Projects/household-it`. This skill
holds no facts about it, so never answer from this skill or from memory: read the pages.

## Answer a question

1. Read `~/Projects/household-it/README.md`. It is the only map of the repo.
2. Follow its link to the system page under `docs/systems/`, or to a page under `docs/reference/`.
   Read the heading that holds the answer.
3. Answer from that page. Name its repo path and the heading in your answer.

A session already inside the repo also has the repo's `CLAUDE.md`. The checkout can lag
`origin/main`; for a page that matters, `git show origin/main:<path>` is the current text.

## After a change or a documenting request

A change to a system updates that system's page in the same pull request.

1. Read `docs/contributing.md` in the repo.
2. Work in a worktree of the repo, as the repo's `CLAUDE.md` "Working in this repo" says.
3. Run the repo's gate before the pull request: `bash scripts/check.sh < /dev/null`.

## Procedures that have their own skill

`mail-tend` sorts the mailbox, `proton-pass` handles vault items, `vps-conventions` covers units
and server scripts, and `maintenance-mode` covers finished projects. Each keeps its procedure and
links to a page in the repo.
