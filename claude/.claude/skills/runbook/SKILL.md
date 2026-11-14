---
name: runbook
description: Use before reading workstation docs for any question about household infrastructure: a DNS record, a mail route, a server, a backup, a phone, an account, an alert, or which credential, token, or key a household system or deploy uses and what it is called in the store. Also use after a session changed one of those systems or was asked to document it. Routes to the household-it repo's README.
---

# Runbook

The household's infrastructure is documented in one repo, `~/Projects/household-it`. This skill
holds no facts about it, so never answer from this skill or from memory: read the pages.

## Answer a question

1. Read `~/Projects/household-it/README.md`. It is the only map of the repo.
2. Follow its link to the system page under `docs/systems/`, or to a page under `docs/reference/`.
   Read the heading that holds the answer.
3. Answer from that page. Name its repo path and the heading in your answer.

A session already inside the repo also has the repo's `CLAUDE.md`.

## After a change or a documenting request

A change to a system updates that system's page in the same pull request.

1. Read `docs/contributing.md` in the repo.
2. Run the repo's gate before the pull request: `bash scripts/check.sh < /dev/null`, as the repo's
   `CLAUDE.md` "Working in this repo" says.
