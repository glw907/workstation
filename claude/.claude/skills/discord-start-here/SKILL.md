Base directory for this skill: /home/glw907/Projects/aksailingclub-org/.scripts/discord-start-here

Post or update the Boson Bot #start-here embeds in the ASC Discord server.

## Overview

Content lives in `discord-embeds/start-here/embed-1.md` and `embed-2.md` (YAML front matter + Discord markdown body).
The script `post.js` handles Discord API calls — POST on first run, PATCH on subsequent runs.
Message IDs are tracked in `state.json` so edits update in place rather than creating duplicates.

## Authoring Format

Each `embed-N.md` file has:
```
---
content: "The plain message text above the embed box 👇"
title: "⛵ EMBED TITLE IN DISCORD"
color: info
---
Body text goes here. This is verbatim Discord markdown — **bold**, *italic*, `code`.
Use - for bullet lists and 1. 2. 3. for numbered lists.
```

**Color values:** `info` (sky blue, #0ea5e9) · `success` (green, #16a34a) · `danger` (red, #dc2626)

**Formatting conventions:**
- Section headers: `**BOLD ALL-CAPS**`
- Category names: `**Bold**`
- Rule/item names: `**Bold** → plain description`
- Channel names: `` `#code-format` ``
- Notes: `***Note:*** *italic body*`
- Server nickname: `*italic*` on first mention
- UI commands: `` `code` ``
- Mobile/desktop steps: `*Entire line italicized, label included*`

## Workflow

### Step 1: Verify environment

Check that `DISCORD_WEBHOOK_START_HERE` is set:
```bash
WEBHOOK=$(bash -c 'source ~/.bashrc && echo -n $DISCORD_WEBHOOK_START_HERE')
```

If empty, stop and tell the user: "DISCORD_WEBHOOK_START_HERE is not set in ~/.bashrc. Create a webhook in the #start-here channel settings → Integrations → Webhooks, then add it to ~/.bashrc."

### Step 2: Show state context

Read `state.json`. Tell the user which messages have known IDs (will PATCH) and which don't (will POST as new messages).

If any message will be POSTed as new, warn: "This will create a new message. Make sure the old message has been deleted from #start-here first, or state.json has been cleared."

### Step 3: Dry-run preview

Run:
```bash
source ~/.bashrc && node /home/glw907/Projects/aksailingclub-org/.scripts/discord-start-here/post.js --dry-run
```

Show the output to the user. Point out the `description` field for each embed — that's the body the Discord user will see.

### Step 4: Confirm

Ask the user: "Ready to post/update these messages to #start-here?" Do not proceed without an explicit yes.

### Step 5: Post

Run:
```bash
source ~/.bashrc && node /home/glw907/Projects/aksailingclub-org/.scripts/discord-start-here/post.js
```

### Step 6: Report results

Show the script output. If new message IDs were written to `state.json`, remind the user:

"state.json was updated with new message IDs. Commit it now so future runs update in place:
```
git add .scripts/discord-start-here/state.json
git commit -m 'ops: save #start-here message IDs'
```"

## Recovery

**Message was manually deleted in Discord:** Remove the relevant key (`message_1` or `message_2`) from `state.json`. The next run will POST a new message and save the new ID.

**HTTP 404 on PATCH:** Discord can't find the message. Same recovery — clear the ID from `state.json`.

**Front matter parse error:** The dry-run will catch this before any API call. Fix the markdown file and re-run.
