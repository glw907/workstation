#!/usr/bin/env python3
"""Convert `op item get` JSON into a 1PUX archive that Proton Pass imports.

Run it in Geoff's own terminal so no secret reaches a log:

    op item list --format json | op item get - --format json \
        | python3 scripts/migrate/op_to_1pux.py --out /dev/shm/op-export.1pux

The 1Password Linux app's own export fails (file chooser never opens), so this is the
fallback. It prints counts only, never a field value.
"""

import argparse
import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# The 1PUX spec page gives no category codes; these are the codes 1Password's own
# exports and the community importers use.
CATEGORY_UUID = {
    "LOGIN": "001",
    "CREDIT_CARD": "002",
    "SECURE_NOTE": "003",
    "PASSWORD": "005",
}

SHM = "/dev/shm/"
ACCOUNT = {
    "accountName": "Imported",
    "name": "Imported",
    "avatar": "",
    "email": "",
    "uuid": "0" * 26,
    "domain": "https://my.1password.com/",
}


def read_items(text: str) -> list[dict]:
    """Return every item in `text`, whether it holds objects, arrays, or both."""
    decoder = json.JSONDecoder()
    items: list[dict] = []
    pos = 0
    while True:
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos >= len(text):
            return items
        obj, pos = decoder.raw_decode(text, pos)
        items.extend(obj if isinstance(obj, list) else [obj])


def _epoch(stamp: str | None) -> int:
    if not stamp:
        return 0
    return int(datetime.fromisoformat(stamp).timestamp())


def _value(field: dict) -> dict:
    """Wrap a field's value in the typed shape 1PUX uses."""
    kind, value = field.get("type", "STRING"), field["value"]
    if kind == "CONCEALED":
        return {"concealed": value}
    if kind == "OTP":
        return {"totp": value}
    if kind == "URL":
        return {"url": value}
    if kind == "PHONE":
        return {"phone": value}
    if kind == "CREDIT_CARD_NUMBER":
        return {"creditCardNumber": value}
    if kind == "CREDIT_CARD_TYPE":
        return {"creditCardType": value}
    if kind == "MONTH_YEAR" and str(value).isdigit():
        return {"monthYear": int(value)}
    return {"string": value}


def _section_field(field: dict, index: int) -> dict:
    return {
        "title": field.get("label", ""),
        "id": field.get("id", ""),
        "value": _value(field),
        "indexAtSource": index,
        "guarded": field.get("type") in ("CONCEALED", "OTP"),
        "multiline": False,
        "dontGenerate": False,
        "inputTraits": {"keyboard": "default", "correction": "default", "capitalization": "default"},
    }


def _sections(fields: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for index, field in enumerate(fields):
        section = field.get("section") or {}
        key = (section.get("id", ""), section.get("label", ""))
        grouped.setdefault(key, []).append(_section_field(field, index))
    return [{"title": label, "name": sid, "fields": fs} for (sid, label), fs in grouped.items()]


def _by_purpose(fields: list[dict], purpose: str) -> dict | None:
    return next((f for f in fields if f.get("purpose") == purpose and f.get("value")), None)


def convert_item(item: dict) -> dict:
    """Return the 1PUX item for one `op` item of a converted category."""
    category = item["category"]
    fields = [f for f in item.get("fields", []) if f.get("value") not in (None, "")]
    username = _by_purpose(fields, "USERNAME")
    password = _by_purpose(fields, "PASSWORD")
    notes = _by_purpose(fields, "NOTES")
    rest = [f for f in fields if not f.get("purpose")]

    details: dict = {
        "loginFields": [],
        "notesPlain": notes["value"] if notes else "",
        "sections": _sections(rest),
        "passwordHistory": [],
    }
    if category == "LOGIN":
        if username:
            details["loginFields"].append(
                {"value": username["value"], "id": "username", "name": "username", "fieldType": "T", "designation": "username"}
            )
        if password:
            details["loginFields"].append(
                {"value": password["value"], "id": "password", "name": "password", "fieldType": "P", "designation": "password"}
            )
    elif category == "PASSWORD" and password:
        details["password"] = password["value"]

    urls = [{"label": u.get("label", ""), "url": u["href"]} for u in item.get("urls", [])]
    primary = next((u["href"] for u in item.get("urls", []) if u.get("primary")), urls[0]["url"] if urls else "")
    return {
        "uuid": item["id"],
        "favIndex": 1 if item.get("favorite") else 0,
        "createdAt": _epoch(item.get("created_at")),
        "updatedAt": _epoch(item.get("updated_at")),
        "state": "active",
        "categoryUuid": CATEGORY_UUID[category],
        "overview": {
            "title": item.get("title", ""),
            "subtitle": username["value"] if username else "",
            "url": primary,
            "urls": urls,
            "tags": item.get("tags", []),
            "ps": 0,
            "pbe": 0,
            "pgrng": False,
        },
        "details": details,
    }


def build(items: list[dict], limit: int | None) -> tuple[dict, dict]:
    """Return the export.data tree and a report of counts, skips, and manual follow-ups."""
    vaults: dict[str, dict] = {}
    report: dict = {"converted": {}, "skipped": {}, "attachments": [], "passkeys": []}
    taken = 0
    for item in items:
        vault = item.get("vault", {})
        vname, category = vault.get("name", ""), item.get("category", "")
        if category not in CATEGORY_UUID:
            key = (vname, category)
            report["skipped"][key] = report["skipped"].get(key, 0) + 1
            continue
        if limit is not None and taken >= limit:
            break
        taken += 1
        target = vaults.setdefault(
            vault.get("id", ""),
            {"attrs": {"uuid": vault.get("id", ""), "desc": "", "avatar": "", "name": vname, "type": "U"}, "items": []},
        )
        target["items"].append(convert_item(item))
        key = (vname, category)
        report["converted"][key] = report["converted"].get(key, 0) + 1
        for attachment in item.get("files", []):
            report["attachments"].append((vname, item.get("title", ""), attachment.get("name", "")))
        if any("passkey" in f.get("type", "").lower() + f.get("label", "").lower() for f in item.get("fields", [])):
            report["passkeys"].append((vname, item.get("title", "")))
    data = {"accounts": [{"attrs": ACCOUNT, "vaults": list(vaults.values())}]}
    return data, report


def format_report(report: dict) -> str:
    """Render counts and follow-up names; field values are never included."""
    lines = ["Converted:"]
    lines += [f"  {v} / {c}: {n}" for (v, c), n in sorted(report["converted"].items())] or ["  none"]
    if report["skipped"]:
        lines.append("Skipped (move by hand):")
        lines += [f"  {v} / {c}: {n}" for (v, c), n in sorted(report["skipped"].items())]
    if report["attachments"]:
        lines.append("Attachments not carried (re-attach by hand):")
        lines += [f"  {v} / {t}: {name}" for v, t, name in report["attachments"]]
    if report["passkeys"]:
        lines.append("Passkeys not carried (re-enroll):")
        lines += [f"  {v} / {t}" for v, t in report["passkeys"]]
    return "\n".join(lines)


def write_1pux(path: Path, data: dict) -> None:
    """Write the archive at 0600, refusing to overwrite an existing file."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    attributes = {"version": 3, "description": "1Password Unencrypted Export", "createdAt": int(datetime.now().timestamp())}
    with os.fdopen(fd, "wb") as handle, zipfile.ZipFile(handle, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("export.attributes", json.dumps(attributes))
        archive.writestr("export.data", json.dumps(data))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, help="output path, which must be under /dev/shm")
    parser.add_argument("--limit", type=int, help="convert only the first N items, for a trial import")
    args = parser.parse_args(argv)

    if not os.path.abspath(args.out).startswith(SHM):
        print(f"error: --out must be under {SHM} so the plaintext never touches disk", file=sys.stderr)
        return 2
    items = read_items(sys.stdin.read())
    if not items:
        print("error: no items on stdin", file=sys.stderr)
        return 2
    data, report = build(items, args.limit)
    write_1pux(Path(args.out), data)
    print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
