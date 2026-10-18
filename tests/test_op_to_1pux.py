import importlib.util
import json
import stat
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "migrate" / "op_to_1pux.py"
spec = importlib.util.spec_from_file_location("op_to_1pux", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

VAULT = {"id": "vault1", "name": "Personal"}


def login(**over):
    item = {
        "id": "item1",
        "title": "Example Site",
        "category": "LOGIN",
        "vault": VAULT,
        "created_at": "2024-01-02T03:04:05Z",
        "updated_at": "2025-06-07T08:09:10Z",
        "favorite": True,
        "tags": ["work"],
        "urls": [
            {"label": "website", "primary": True, "href": "https://example.test/login"},
            {"label": "other", "href": "https://example.test/alt"},
        ],
        "fields": [
            {"id": "username", "type": "STRING", "purpose": "USERNAME", "label": "username", "value": "fake-user"},
            {"id": "password", "type": "CONCEALED", "purpose": "PASSWORD", "label": "password", "value": "fake-pass-1"},
            {"id": "notesPlain", "type": "STRING", "purpose": "NOTES", "label": "notesPlain", "value": "a fake note"},
            {"id": "t1", "type": "OTP", "label": "one-time password", "value": "otpauth://totp/x?secret=FAKESEED", "totp": "123456"},
            {"id": "q1", "type": "CONCEALED", "label": "pin", "value": "fake-pin", "section": {"id": "s1", "label": "Extra"}},
            {"id": "empty", "type": "STRING", "label": "blank", "value": ""},
        ],
    }
    item.update(over)
    return item


def convert(item):
    return mod.convert_item(item)


def test_login_fields_and_designations():
    out = convert(login())
    assert out["categoryUuid"] == "001"
    login_fields = out["details"]["loginFields"]
    assert {"value": "fake-user", "id": "username", "name": "username", "fieldType": "T", "designation": "username"} in login_fields
    assert {"value": "fake-pass-1", "id": "password", "name": "password", "fieldType": "P", "designation": "password"} in login_fields
    assert out["details"]["notesPlain"] == "a fake note"


def test_login_overview_and_timestamps():
    out = convert(login())
    ov = out["overview"]
    assert ov["title"] == "Example Site"
    assert ov["subtitle"] == "fake-user"
    assert ov["url"] == "https://example.test/login"
    assert ov["urls"] == [
        {"label": "website", "url": "https://example.test/login"},
        {"label": "other", "url": "https://example.test/alt"},
    ]
    assert ov["tags"] == ["work"]
    assert out["favIndex"] == 1
    assert out["createdAt"] == 1704164645
    assert out["state"] == "active"


def test_totp_and_sectioned_fields_land_in_sections_and_blanks_drop():
    out = convert(login())
    fields = {f["id"]: f for s in out["details"]["sections"] for f in s["fields"]}
    assert fields["t1"]["value"] == {"totp": "otpauth://totp/x?secret=FAKESEED"}
    assert fields["q1"]["value"] == {"concealed": "fake-pin"}
    assert "empty" not in fields
    titles = {s["title"] for s in out["details"]["sections"]}
    assert "Extra" in titles


def test_password_category_uses_details_password():
    item = {
        "id": "p1", "title": "Router", "category": "PASSWORD", "vault": VAULT,
        "created_at": "2024-01-02T03:04:05Z", "updated_at": "2024-01-02T03:04:05Z",
        "fields": [{"id": "password", "type": "CONCEALED", "purpose": "PASSWORD", "label": "password", "value": "fake-router"}],
    }
    out = convert(item)
    assert out["categoryUuid"] == "005"
    assert out["details"]["password"] == "fake-router"


def test_secure_note_carries_notes_only():
    item = {
        "id": "n1", "title": "Note", "category": "SECURE_NOTE", "vault": VAULT,
        "created_at": "2024-01-02T03:04:05Z", "updated_at": "2024-01-02T03:04:05Z",
        "fields": [{"id": "notesPlain", "type": "STRING", "purpose": "NOTES", "label": "notesPlain", "value": "line one\nline two"}],
    }
    out = convert(item)
    assert out["categoryUuid"] == "003"
    assert out["details"]["notesPlain"] == "line one\nline two"
    assert out["details"]["loginFields"] == []


def test_credit_card_value_shapes():
    item = {
        "id": "c1", "title": "Card", "category": "CREDIT_CARD", "vault": VAULT,
        "created_at": "2024-01-02T03:04:05Z", "updated_at": "2024-01-02T03:04:05Z",
        "fields": [
            {"id": "ccnum", "type": "CREDIT_CARD_NUMBER", "label": "number", "value": "4111111111111111"},
            {"id": "type", "type": "CREDIT_CARD_TYPE", "label": "type", "value": "visa"},
            {"id": "expiry", "type": "MONTH_YEAR", "label": "expiry", "value": "202912"},
            {"id": "cvv", "type": "CONCEALED", "label": "cvv", "value": "123"},
            {"id": "cardholder", "type": "STRING", "label": "cardholder", "value": "Fake Person"},
        ],
    }
    out = convert(item)
    assert out["categoryUuid"] == "002"
    fields = {f["id"]: f["value"] for s in out["details"]["sections"] for f in s["fields"]}
    assert fields["ccnum"] == {"creditCardNumber": "4111111111111111"}
    assert fields["type"] == {"creditCardType": "visa"}
    assert fields["expiry"] == {"monthYear": 202912}
    assert fields["cvv"] == {"concealed": "123"}
    assert fields["cardholder"] == {"string": "Fake Person"}


def test_read_items_accepts_concatenated_objects_and_arrays():
    a, b, c = login(id="a"), login(id="b"), login(id="c")
    text = json.dumps(a) + "\n" + json.dumps([b, c])
    assert [i["id"] for i in mod.read_items(text)] == ["a", "b", "c"]


def test_build_groups_by_vault_counts_and_skips():
    ssh = {"id": "s1", "title": "Key", "category": "SSH_KEY", "vault": {"id": "v2", "name": "Work"}, "fields": []}
    attached = login(id="f1", title="With file", files=[{"id": "x", "name": "scan.pdf", "size": 10}])
    items = [login(), attached, ssh]
    data, report = mod.build(items, limit=None)
    vaults = {v["attrs"]["name"]: v for v in data["accounts"][0]["vaults"]}
    assert set(vaults) == {"Personal"}
    assert len(vaults["Personal"]["items"]) == 2
    assert report["converted"] == {("Personal", "LOGIN"): 2}
    assert report["skipped"] == {("Work", "SSH_KEY"): 1}
    assert report["attachments"] == [("Personal", "With file", "scan.pdf")]


def test_build_flags_passkey_items_by_title_only():
    item = login(id="k1", title="Has passkey")
    item["fields"].append({"id": "pk", "type": "PASSKEY", "label": "passkey", "value": "fake-credential"})
    _, report = mod.build([item], limit=None)
    assert report["passkeys"] == [("Personal", "Has passkey")]


def test_limit_takes_the_first_converted_items():
    items = [login(id=str(n), title=f"T{n}") for n in range(5)]
    data, report = mod.build(items, limit=3)
    assert len(data["accounts"][0]["vaults"][0]["items"]) == 3
    assert sum(report["converted"].values()) == 3


def test_report_text_carries_no_field_value():
    attached = login(id="f1", files=[{"id": "x", "name": "scan.pdf", "size": 10}])
    _, report = mod.build([login(), attached], limit=None)
    text = mod.format_report(report)
    for secret in ("fake-pass-1", "fake-pin", "FAKESEED", "fake-user", "123456"):
        assert secret not in text
    assert "LOGIN" in text and "Personal" in text


def test_write_1pux_layout_and_private_mode(tmp_path):
    data, _ = mod.build([login()], limit=None)
    out = tmp_path / "x.1pux"
    mod.write_1pux(out, data)
    assert stat.S_IMODE(out.stat().st_mode) == 0o600
    with zipfile.ZipFile(out) as z:
        assert set(z.namelist()) == {"export.attributes", "export.data"}
        attrs = json.loads(z.read("export.attributes"))
        assert attrs["version"] == 3
        assert json.loads(z.read("export.data"))["accounts"][0]["vaults"]


def test_main_refuses_output_outside_dev_shm(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps(login())))
    rc = mod.main(["--out", str(tmp_path / "x.1pux")])
    assert rc == 2
    assert "/dev/shm" in capsys.readouterr().err
    assert not (tmp_path / "x.1pux").exists()


def test_main_refuses_empty_input(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(""))
    assert mod.main(["--out", "/dev/shm/never.1pux"]) == 2
    assert "no items" in capsys.readouterr().err


def test_write_1pux_never_overwrites(tmp_path):
    data, _ = mod.build([login()], limit=None)
    out = tmp_path / "x.1pux"
    mod.write_1pux(out, data)
    before = out.read_bytes()
    with pytest.raises(FileExistsError):
        mod.write_1pux(out, data)
    assert out.read_bytes() == before


def test_main_writes_under_the_shm_root(tmp_path, monkeypatch, capsys):
    shm = tmp_path / "shm"
    shm.mkdir()
    monkeypatch.setattr(mod, "SHM", str(shm) + "/")
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps(login())))
    assert mod.main(["--out", str(shm / "x.1pux")]) == 0
    assert (shm / "x.1pux").exists()
    assert "LOGIN" in capsys.readouterr().out


def test_main_refuses_a_symlinked_parent_that_leaves_the_shm_root(tmp_path, monkeypatch, capsys):
    shm, disk = tmp_path / "shm", tmp_path / "disk"
    shm.mkdir()
    disk.mkdir()
    (shm / "link").symlink_to(disk)
    monkeypatch.setattr(mod, "SHM", str(shm) + "/")
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps(login())))
    assert mod.main(["--out", str(shm / "link" / "x.1pux")]) == 2
    assert not (disk / "x.1pux").exists()


def test_main_refuses_dotdot_that_leaves_the_shm_root(tmp_path, monkeypatch):
    shm = tmp_path / "shm"
    shm.mkdir()
    monkeypatch.setattr(mod, "SHM", str(shm) + "/")
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps(login())))
    assert mod.main(["--out", str(shm / ".." / "x.1pux")]) == 2


def test_month_year_accepts_slash_form():
    item = {
        "id": "c2", "title": "Card", "category": "CREDIT_CARD", "vault": VAULT,
        "fields": [{"id": "expiry", "type": "MONTH_YEAR", "label": "expiry", "value": "03/2031"}],
    }
    fields = {f["id"]: f["value"] for s in convert(item)["details"]["sections"] for f in s["fields"]}
    assert fields["expiry"] == {"monthYear": 203103}


def test_null_label_does_not_abort_the_passkey_scan():
    item = login()
    item["fields"].append({"id": "n", "type": "STRING", "label": None, "value": "x"})
    mod.build([item], limit=None)


def test_limit_marks_the_report_truncated():
    items = [login(id=str(n)) for n in range(4)]
    _, report = mod.build(items, limit=2)
    assert report["truncated"] is True
    assert "first 2" in mod.format_report(report)
    _, full = mod.build(items, limit=None)
    assert full["truncated"] is False
