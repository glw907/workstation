---
name: proton-pass
description: Use for any work on Proton Pass vaults, items, grants, or credentials on this workstation: which vault an item belongs in, how to name it and write its note, reading or writing an item through claude-pass, a sign-in throttle, the grant map and check-drift's legs, the item-title lint, a new credential or mask, or a bulk vault edit that Geoff runs through pass-sitting.
---

# Proton Pass

Proton Pass is the authoritative record of every credential (Geoff, 2026-10-27). Claude reaches it
only through `claude-pass`, never bare `pass-cli` (`claude-block-pass` denies it). The facts on the
agents and tokens are in `~/.claude/docs/bluefin-admin/secrets.md`; this skill holds the vault
map, the naming rules, and the procedures.

## The vaults

A vault is the unit Proton grants access on, so each vault holds one set of readers. Projects get
folders, not vaults.

| Vault | Holds | Readers |
|---|---|---|
| `Private` | accounts only Geoff signs in to | Geoff |
| `Cathy & Geoff` | accounts the two run as a household | Geoff, Cathy |
| `Family` | accounts the adult kids use or would need | Geoff, the kids |
| `Parents` | the parents' accounts | Geoff, Cathy |
| `Proton recovery` | Proton's recovery material | Geoff; no agent |
| `Infrastructure` | servers, backups, mail, phones, voip.ms, Cloudflare, the registrar | Geoff, the second operator, Claude (editor) |
| `Age key` | the workstation age key alone | Claude (editor); the scripts agents (viewer) |
| `Projects` | cairn, the sites, npm, Anthropic, Resend, Twilio, the technical identity's vendor accounts; one folder per project | Geoff, Claude (editor) |
| `ASC` | the club's credentials and its age key | Geoff, Claude (editor), officers later |
| `Test accounts` | the test GitHub account, the probe mailboxes, test logins | Claude (editor) |

Claude's agents see only the last five rows' vaults (`Infrastructure`, `Age key`, `Projects`,
`ASC`, `Test accounts`). Tiebreaker: an item goes in the narrowest vault that holds everyone who
signs in to it, and money or medical accounts lean to `Cathy & Geoff` unless a kid uses them.

## Naming and notes

A title is the service's name as people say it, never a domain. A qualifier goes in one trailing
parenthesis, only when one vault holds more than one account at the service, usually the username
or whose it is. A key or secret is named system, then secret, then scope. No generic titles.
A custom field's title is sentence case, as Proton Pass shows its own fields ("Token",
"Recovery codes"), never lowercase or a variable name (Geoff, 2026-11-07).

Technical vaults carry the full note template, each line only where a source supports it: `For`,
`Used by`, `Rotate`, `Recovery`, `Mask`, `Reviewed`. Personal and family vaults carry only the lines
that help, chiefly `Mask` and `Recovery`. A new note goes above an existing one, never over it.
`check-drift --titles` lints the five Claude vaults monthly (the model review runs it); it prints a
count and writes titles to a private findings file, so no title reaches a transcript.

## Using claude-pass

- `claude-pass <pass-cli args>` runs one command as `<host>-claude`. Verbs: item (list, view,
  create, update, trash, untrash, move), vault list, folder (list, create, update, move), share
  list, and password, totp, info, user. Anything else is refused before the token is read.
- A value goes in on stdin (`item create login --vault-name V --from-template -`), never in argv.
  A secret read with `item view` goes to a file or a pipe, never the transcript. A custom field
  with a secret value goes in through the template's `extra_fields` array (`{"kind": "hidden",
  "title": "Token", "value": ...}`), piped to `item create ... --from-template -`, because `item
  update --field` takes its value in argv. To add one to an existing item, create the item again
  from a template carrying every field, check it, then trash the old one. Read the item's
  current fields first (names and types only), so nothing is added twice (pass-cli docs,
  "Custom fields in templates"; Geoff, 2026-11-07).
- Set `CLAUDE_PASS_REASON` to say why; the default names the host and verb.
- Proton throttles an agent's logins after about four quick calls. "Agent login failed" with a
  good token is the throttle: wait 25 minutes, then space calls 150 seconds apart. Run any chain
  longer than a few minutes in the background, and write output to a file.
- A value Geoff must supply arrives through `secret-receive NAME` (or `secret-receive --pass` for
  a vault the agent cannot reach), which Claude launches; it is never pasted into chat.
- `pass-cli agent renew` keeps the agent's grants (pass-cli docs, "agent"), so a renewed token
  needs no regrant; update the expiry in the grant map.

## The grant map

`secrets/proton-grants.tsv` records each agent, vault, role, and token expiry. `pass-access` lists
what this host's agents can reach, each through the agent's token. `check-drift` fails when the two
differ, warns when a failed sign-in blocks the comparison, and warns within 30 days of an expiry
and fails once past (`PASS_ACCESS_SKIP=1` skips the sign-ins on a rerun). Change a grant only by
Geoff's hand, then update the map in the same PR.

## Bulk edits are Geoff's

Moves, renames, notes, trashes, grants, revokes, and the grant audit run through `pass-sitting`,
under Geoff's login after a dry run. Claude never runs it (`claude-block-pass` refuses every
form). Claude writes the JSON-lines sitting file (the header of `bin/.local/bin/pass-sitting` shows
the shape) and tells Geoff the two commands: `pass-sitting FILE`, then `pass-sitting --apply FILE`,
in a Ptyxis terminal, not through `!`.

A `revoke` line carries the agent-side `share_id`, read from that agent's `vault list --output
json`. The owner's share id for the same vault is rejected by `agent access revoke`.

## Aliases

Masked and alias addresses use `m.907.life` (backlog #45, Geoff 2026-10-28). The servers repo's
decisions file spells it `me.907.life`; this skill follows the ruling.
