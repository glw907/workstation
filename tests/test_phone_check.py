"""Tests for phone-check's QR payload parsing, code extraction, and decoding."""

import importlib.machinery
import importlib.util
from pathlib import Path
import shutil

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin/.local/bin/phone-check"
loader = importlib.machinery.SourceFileLoader("phone_check", str(SCRIPT))
spec = importlib.util.spec_from_loader("phone_check", loader)
phone_check = importlib.util.module_from_spec(spec)
loader.exec_module(phone_check)


@pytest.mark.parametrize(
    "payload, want",
    [
        ("SMSTO:+16505551234:Verify ABC123", ("6505551234", "Verify ABC123")),
        ("smsto:22000:G-XYZ", ("22000", "G-XYZ")),
        ("sms:+1-650-555-1234?body=Send%20this%20code%20AB12", ("6505551234", "Send this code AB12")),
        ("sms:6505551234;body=hello", ("6505551234", "hello")),
        ("sms:+447700900123?body=x", ("447700900123", "x")),
        ("sms:5550100?body=a+b%20c", ("5550100", "a+b c")),
        ("https://accounts.google.com/x", None),
        ("plain text", None),
    ],
)
def test_parse_sms(payload, want):
    assert phone_check.parse_sms(payload) == want


@pytest.mark.parametrize(
    "message, want",
    [
        ("G-482913 is your Google verification code.", "482913"),
        ("Your code is 7731", "7731"),
        ("Call 907-277-9397 for help", None),
        ("No digits here", None),
    ],
)
def test_find_code(message, want):
    assert phone_check.find_code(message) == want


needs_zbar = pytest.mark.skipif(not shutil.which("zbarimg"), reason="zbarimg not installed")


@needs_zbar
def test_decode_reads_a_qr_code(tmp_path):
    # The gate's pytest has no qrcode package; run with `--with "qrcode[pil]"` to cover this.
    qrcode = pytest.importorskip("qrcode")
    image = tmp_path / "code.png"
    qrcode.make("SMSTO:+16505551234:hi").save(image)
    assert phone_check.decode(image) == "SMSTO:+16505551234:hi"


@needs_zbar
def test_decode_exits_on_an_image_without_a_code(tmp_path):
    pil = pytest.importorskip("PIL.Image")
    image = tmp_path / "blank.png"
    pil.new("L", (64, 64), 255).save(image)
    with pytest.raises(SystemExit, match="no QR code found"):
        phone_check.decode(image)


def test_send_refused_without_a_terminal(monkeypatch):
    monkeypatch.setattr(phone_check.sys.stdin, "isatty", lambda: False)
    sent = []
    monkeypatch.setattr(phone_check.subprocess, "run", lambda *a, **k: sent.append(a))
    with pytest.raises(SystemExit, match="needs a person at a terminal"):
        phone_check.act_on("SMSTO:5550100:hi")
    assert sent == []
