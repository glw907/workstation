# proton-pass-cli 2.7.0 to 2.7.1: upgrade survey

Date: 2026-11-17. Host: pavilion. Formula: `proton-pass-cli` in homebrew/core, held with `brew pin`.

This is the `standards:dependency-upgrade` record for one Homebrew bump. The next survey of this formula starts
from here.

## Before and after

| Formula | Before | After | Pinned |
|---|---|---|---|
| `proton-pass-cli` | 2.7.0 | 2.7.1 | yes, before and after |
| `libxml2` | 2.15.4 | 2.15.4 (current) | yes |

`thinkpad-x1` was not measured from this session. The new `check-drift` leg reports it there.

## What changed in the range

Upstream publishes no release body, so this reads `CHANGELOG.md` and the `2.7.0...2.7.1` comparison
(<https://github.com/protonpass/pass-cli/compare/2.7.0...2.7.1>, 21 commits, 68 files).

- `item list` and `item view` gain a last-use time. The JSON item summary gains a `last_use_time` key, null when
  the item was never used. The human-readable list line changes from `(state=Active)` to
  `(state=Active, last_used=...)`, and the human-readable view gains a `- Last used:` line.
- The session lock commands now ask the server for the lock state. Agent and personal-access-token sessions return
  "no lock" without the call.
- The auth store, the cache, and the network dependency were reworked, and the code moved to Rust 1.100.
- The `brew upgrade` instructions in the docs were corrected.

## Against this repo's call sites

| Call site | Call | Effect |
|---|---|---|
| `ws-pass-key` (`--shares`) | `share list --output json` | none |
| `ws-pass-key` (the key read) | `item view pass://VAULT/ITEM/FIELD` | none: a field read prints the bare value, with no `Last used` line |
| `pass-count` | `vault list --output json`, `item list --output json` through `jq` | none: the new key is additive |
| `pass-access` | `share list --output json` through `claude-pass` and `ws-pass-key` | none |
| `claude-pass` | passes `item`, `vault`, `share`, and the rest through | the human-readable list and view lines change shape; nothing parses them |

No script here uses a session lock. `ws-pass-key` and `claude-pass` sign in as agents, which the lock rework
skips. `pass-count` and `pass-sitting` run in Geoff's own session and were not exercised here.

## Rulings

| Item | Ruling |
|---|---|
| `last_use_time` in item listings | Not taken. It could feed a stale-credential report, but no script or backlog item asks for one. |
| Human-readable line shapes | No change needed. Scripts read JSON or a single field. |
| Nothing watched the pin | Taken now: `check-drift` gains a pinned-formula leg (`check_pins`, `--pins-only`). |

No major was in range and none is held.

## Verification on pavilion, on 2.7.1

| Check | Result |
|---|---|
| `brew list --versions proton-pass-cli` | 2.7.1, pinned |
| `ws-pass-key --status` | `path=proton`, exit 0 |
| `check-drift --proton-only` (signs in as both agents and lists their shares) | clean, exit 0 |
| `claude-pass item list --vault-name Infrastructure --output json` | parses; 45 items, each with a `last_use_time` key |
| `claude-pass item view pass://Infrastructure/<item>/password` | exit 0, one line, no `Last used` line |
| `check-drift --pins-only` | `pinned formulae current: libxml2 proton-pass-cli` |

The first two attempts at the field read asked for `username` and then `email`, both empty on that item, and each
answered `Error: Field does not exist: <field>` with exit 1. Whether 2.7.0 answered an empty field the same way was
not checked. `ws-pass-key` reads a field that is always set.
