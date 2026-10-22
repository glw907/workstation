# Fastmail API Access

## Credentials

- **Token env var**: `FASTMAIL_API_TOKEN` (sourced from `~/.local/secrets`)
- **DAV app password**: `FASTMAIL_DAV_PASSWORD` (age store, sourced from `~/.local/secrets`)
- **Account**: geoff@907.life (Fastmail business plan)
- **Domain**: 907.life

## JMAP Endpoints

- **Session**: GET `https://api.fastmail.com/jmap/session` with Bearer auth to discover the account ID and capabilities
- **API**: POST `https://api.fastmail.com/jmap/api/` with Bearer auth for all JMAP method calls

## Authentication

All JMAP requests use Bearer token auth:
```
Authorization: Bearer $FASTMAIL_API_TOKEN
```

CardDAV/CalDAV uses Basic auth with the DAV app password (`$FASTMAIL_DAV_PASSWORD` in `~/.local/secrets`).

## Available Capabilities

| Capability | JMAP Method Prefix | What It Manages |
|---|---|---|
| Mail | `Email/`, `Mailbox/`, `Thread/` | Read, search, send, organize mail |
| Identities | `Identity/` | Send-as addresses, signatures |
| Filters | `Filter/` | Server-side mail rules (Sieve) |
| Contacts | `ContactCard/` | Address book (CardDAV via JMAP) |
| Calendars | `CalendarEvent/` | Calendar events (CalDAV via JMAP) |

## Example: Discover Account ID

```bash
curl -s -H "Authorization: Bearer $FASTMAIL_API_TOKEN" \
  https://api.fastmail.com/jmap/session | python3 -m json.tool
```

The `primaryAccounts` object maps capability URIs to account IDs.

## Example: List Mailboxes

```bash
curl -s -X POST \
  -H "Authorization: Bearer $FASTMAIL_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
    "methodCalls": [
      ["Mailbox/get", {"accountId": "ACCOUNT_ID"}, "0"]
    ]
  }' \
  https://api.fastmail.com/jmap/api/
```

## Local Clients

- **poplar** terminal mail client (`~/Projects/poplar/`, installed at `~/.local/bin/poplar`)
  talks JMAP with `$FASTMAIL_API_TOKEN`
- Contacts and calendars moved to ward on 2026-10-22; vdirsyncer and khard are retired, and
  `~/.contacts/` is a frozen Fastmail-era snapshot
