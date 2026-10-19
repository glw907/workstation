"""Tests for proton-mail-read against a fake IMAP server that records every command it receives."""

import importlib.machinery
import importlib.util
import re
import socket
import socketserver
import ssl
import subprocess
import threading
from email.message import EmailMessage
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin/.local/bin/proton-mail-read"
SIEVE = ROOT / "docs/proton/services-filter.sieve"

loader = importlib.machinery.SourceFileLoader("proton_mail_read", str(SCRIPT))
spec = importlib.util.spec_from_loader("proton_mail_read", loader)
pmr = importlib.util.module_from_spec(spec)
loader.exec_module(pmr)

FORBIDDEN = {"SELECT", "STORE", "COPY", "MOVE", "EXPUNGE", "APPEND", "CREATE", "DELETE", "RENAME", "SUBSCRIBE"}


def make_message(subject, sender, body, html=None, date="Mon, 19 Oct 2026 09:00:00 +0000"):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = "someone@example.invalid"
    msg["Subject"] = subject
    msg["Date"] = date
    if html is None:
        msg.set_content(body)
    elif body is None:
        msg.set_content(html, subtype="html")
    else:
        msg.set_content(body)
        msg.add_alternative(html, subtype="html")
    return msg.as_bytes()


MESSAGES = {
    5: make_message("Monitor test alert", "monitor@907.life", "The alert body."),
    9: make_message("Weekly note", "monitor@907.life", "Still watching.", date="Sun, 18 Oct 2026 09:00:00 +0000"),
    7: make_message("Hostile", "x@example.invalid", "before \x1b]52;c;ZXZpbA==\x07 after \u202e reversed"),
    8: b"From: a@example.invalid\r\nDate: Mon, 19 Oct 2026 09:00:00 +0000\r\nSubject: =?utf-8?b?SGVsbG8KOTk5CWZha2UJeA==?=\r\n\r\nbody\r\n",
    12: make_message("Receipt", "billing@hetzner.example", None, html="<html><body><p>Total <b>12 EUR</b></p><script>x()</script></body></html>"),
}


class Handler(socketserver.StreamRequestHandler):
    def send(self, text):
        self.wfile.write(text.encode() + b"\r\n")

    def handle(self):
        log = self.server.log
        self.send("* OK fake bridge ready")
        while True:
            line = self.rfile.readline()
            if not line:
                return
            text = line.decode().rstrip("\r\n")
            tag, _, rest = text.partition(" ")
            verb, _, args = rest.partition(" ")
            log.append(text)
            verb = verb.upper()
            if verb == "CAPABILITY":
                self.send("* CAPABILITY IMAP4rev1" + ("" if self.server.no_tls else " STARTTLS"))
                self.send(f"{tag} OK done")
            elif verb == "STARTTLS":
                self.send(f"{tag} OK begin TLS")
                self.connection = self.server.tls.wrap_socket(self.connection, server_side=True)
                self.rfile = self.connection.makefile("rb")
                self.wfile = self.connection.makefile("wb", 0)
            elif verb == "LOGIN":
                self.send(f"{tag} OK logged in")
            elif verb == "EXAMINE":
                self.send("* 3 EXISTS")
                self.send(f"{tag} OK [READ-ONLY] examined")
            elif verb == "UID":
                sub, _, sargs = args.partition(" ")
                if sub.upper() == "SEARCH":
                    uids = " ".join(str(u) for u in sorted(MESSAGES))
                    self.send(f"* SEARCH {uids}")
                    self.send(f"{tag} OK done")
                elif sub.upper() == "FETCH":
                    self.fetch(tag, sargs)
            elif verb == "LOGOUT":
                self.send("* BYE")
                self.send(f"{tag} OK bye")
                return
            else:
                self.send(f"{tag} BAD unsupported")

    def literal(self, uid, item, payload):
        """Write one FETCH response, placing UID before the literal or after it as Bridge does."""
        if self.server.uid_after:
            self.wfile.write(f"* {uid} FETCH ({item} {{{len(payload)}}}\r\n".encode() + payload + f" UID {uid})\r\n".encode())
        else:
            self.wfile.write(f"* {uid} FETCH (UID {uid} {item} {{{len(payload)}}}\r\n".encode() + payload + b")\r\n")

    def fetch(self, tag, sargs):
        seq, _, items = sargs.partition(" ")
        for uid in (int(u) for u in seq.split(",") if u.isdigit()):
            if uid not in MESSAGES:
                continue
            raw = MESSAGES[uid]
            if "HEADER" in items.upper() and "BODY.PEEK[]" not in items:
                head = raw.split(b"\r\n\r\n", 1)[0] + b"\r\n\r\n"
                self.literal(uid, "BODY[HEADER.FIELDS (DATE FROM SUBJECT)]", head)
            else:
                self.literal(uid, "BODY[]", raw)
        self.send(f"{tag} OK fetched")


class FakeServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def make_tls_context(tmp_path):
    key, crt = tmp_path / "key.pem", tmp_path / "crt.pem"
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "2", "-subj", "/CN=127.0.0.1", "-keyout", str(key), "-out", str(crt)],
        check=True, capture_output=True,
    )
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(crt, key)
    return context


@pytest.fixture(params=["uid-first", "uid-after-literal"])
def bridge(request, tmp_path, monkeypatch):
    server = FakeServer(("127.0.0.1", 0), Handler)
    server.log = []
    server.no_tls = False
    server.uid_after = request.param == "uid-after-literal"
    server.tls = make_tls_context(tmp_path)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    secrets = tmp_path / "secrets"
    secrets.write_text("export PROTON_BRIDGE_USER=tester@example.invalid\nexport PROTON_BRIDGE_PASSWORD='p@ss word'\n")
    secrets.chmod(0o600)
    monkeypatch.setenv("PROTON_MAIL_READ_SECRETS", str(secrets))
    monkeypatch.setenv("PROTON_MAIL_READ_PORT", str(server.server_address[1]))
    monkeypatch.setenv("PROTON_MAIL_READ_PIN", str(tmp_path / "pin"))
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "run"))
    yield server
    server.shutdown()
    server.server_close()


def verbs(log):
    return [line.split(" ", 2)[1].upper() for line in log]


def run(capsys, *argv):
    code = pmr.main(list(argv))
    out = capsys.readouterr()
    return code, out.out, out.err


def test_list_only_examines_and_peeks(bridge, capsys):
    code, out, _ = run(capsys, "list")
    assert code == 0
    assert "EXAMINE" in verbs(bridge.log)
    assert not FORBIDDEN & set(verbs(bridge.log))
    assert "Monitor test alert" in out and "Weekly note" in out
    assert "monitor@907.life" in out


def test_every_fetch_is_a_peek(bridge, capsys):
    run(capsys, "list")
    run(capsys, "read", "5")
    fetches = [line for line in bridge.log if " FETCH " in line.upper()]
    assert fetches
    for line in fetches:
        assert "BODY.PEEK[" in line.upper()
        assert re.search(r"BODY\[", line.upper()) is None
        assert "RFC822" not in line.upper()


def test_examine_names_only_the_services_folder(bridge, capsys):
    run(capsys, "search", "--from", "monitor")
    run(capsys, "read", "9")
    examines = [line for line in bridge.log if " EXAMINE " in line.upper()]
    assert examines
    assert all(line.endswith('"Folders/Services"') or line.endswith("Folders/Services") for line in examines)


def test_other_folder_is_refused_before_connecting(bridge, capsys):
    for folder in ("INBOX", "Folders/Other", "folders/services", "Folders/Services/../INBOX"):
        code, _, err = run(capsys, "list", "--folder", folder)
        assert code != 0
        assert "Folders/Services" in err
    assert bridge.log == []


def test_search_from_and_subject(bridge, capsys):
    code, out, _ = run(capsys, "search", "--from", "monitor@907.life")
    assert code == 0 and "Weekly note" in out
    searches = [line for line in bridge.log if " SEARCH" in line.upper()]
    assert any("FROM" in line for line in searches)
    code, _, _ = run(capsys, "search", "--subject", "alert")
    assert code == 0
    assert any("SUBJECT" in line for line in bridge.log)


def test_search_rejects_quote_and_newline_injection(bridge, capsys):
    code, _, err = run(capsys, "search", "--subject", 'x"\r\nA1 STORE 1 +FLAGS (\\Deleted)')
    assert code != 0
    assert bridge.log == []


def test_list_since_and_limit(bridge, capsys):
    code, out, _ = run(capsys, "list", "--since", "2026-10-18", "--limit", "1")
    assert code == 0
    assert any("SINCE 18-Oct-2026" in line for line in bridge.log)
    assert len([row for row in out.splitlines() if row.strip()]) == 1


def test_bad_date_is_a_usage_error(bridge, capsys):
    code, _, err = run(capsys, "list", "--since", "yesterday")
    assert code != 0
    assert bridge.log == []


def test_read_prints_headers_and_plain_text(bridge, capsys):
    code, out, _ = run(capsys, "read", "5")
    assert code == 0
    assert "Subject: Monitor test alert" in out
    assert "From: monitor@907.life" in out
    assert "The alert body." in out


def test_read_html_only_falls_back_to_text(bridge, capsys):
    code, out, _ = run(capsys, "read", "12")
    assert code == 0
    assert "Total" in out and "12 EUR" in out
    assert "<b>" not in out and "<p>" not in out and "x()" not in out


def test_read_rejects_non_numeric_uid(bridge, capsys):
    with pytest.raises(SystemExit) as stop:
        pmr.main(["read", "5 STORE"])
    assert stop.value.code != 0
    assert bridge.log == []


def test_login_uses_the_stored_credentials(bridge, capsys):
    run(capsys, "list")
    login = next(line for line in bridge.log if " LOGIN " in line.upper())
    assert "tester@example.invalid" in login and "p@ss word" in login


def test_missing_credentials_fail_clearly(bridge, tmp_path, monkeypatch, capsys):
    empty = tmp_path / "empty"
    empty.write_text("export OTHER=1\n")
    empty.chmod(0o600)
    monkeypatch.setenv("PROTON_MAIL_READ_SECRETS", str(empty))
    code, _, err = run(capsys, "list")
    assert code != 0
    assert "PROTON_BRIDGE_USER" in err
    assert bridge.log == []


def test_bridge_not_listening_message(tmp_path, monkeypatch, capsys):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    secrets = tmp_path / "secrets"
    secrets.write_text("export PROTON_BRIDGE_USER=u\nexport PROTON_BRIDGE_PASSWORD=p\n")
    secrets.chmod(0o600)
    monkeypatch.setenv("PROTON_MAIL_READ_SECRETS", str(secrets))
    monkeypatch.setenv("PROTON_MAIL_READ_PORT", str(port))
    monkeypatch.setenv("PROTON_MAIL_READ_PIN", str(tmp_path / "pin"))
    code, _, err = run(capsys, "list")
    assert code != 0
    assert "Bridge is not listening" in err
    assert "proton-bridge.service" in err


def test_no_starttls_is_refused_before_login(bridge, capsys):
    bridge.no_tls = True
    code, _, err = run(capsys, "list")
    assert code != 0 and "STARTTLS" in err
    assert not any(" LOGIN " in line.upper() for line in bridge.log)


def test_certificate_is_pinned_on_first_use_and_checked_after(bridge, tmp_path, capsys):
    code, _, _ = run(capsys, "list")
    assert code == 0
    pin = tmp_path / "pin"
    assert re.fullmatch(r"[0-9a-f]{64}", pin.read_text().strip())
    bridge.log.clear()
    pin.write_text("0" * 64 + "\n")
    code, _, err = run(capsys, "list")
    assert code != 0 and "pinned" in err
    assert not any(" LOGIN " in line.upper() for line in bridge.log)


def test_body_control_and_bidi_characters_are_stripped(bridge, capsys):
    code, out, _ = run(capsys, "read", "7")
    assert code == 0
    assert "\x1b" not in out and "\x07" not in out and "\u202e" not in out
    assert "before" in out and "after" in out


@pytest.mark.parametrize("port", ["abc", "80", "70000"])
def test_bad_port_is_a_clear_error(bridge, monkeypatch, capsys, port):
    monkeypatch.setenv("PROTON_MAIL_READ_PORT", port)
    code, _, err = run(capsys, "list")
    assert code != 0 and "PROTON_MAIL_READ_PORT" in err
    assert bridge.log == []


def test_group_writable_secrets_file_is_ignored(bridge, tmp_path, capsys):
    (tmp_path / "secrets").chmod(0o664)
    code, _, err = run(capsys, "list")
    assert code != 0 and "PROTON_BRIDGE_USER" in err


def test_overlay_supplies_names_the_main_file_lacks(bridge, tmp_path, monkeypatch, capsys):
    (tmp_path / "secrets").write_text("export OTHER=1\n")
    overlay = tmp_path / "run/self-hosting"
    overlay.mkdir(parents=True)
    (overlay / "secrets-mailread").write_text("export PROTON_BRIDGE_USER=ov\nexport PROTON_BRIDGE_PASSWORD=ovpw\n")
    (overlay / "secrets-mailread").chmod(0o600)
    code, _, _ = run(capsys, "list")
    assert code == 0
    assert any(" LOGIN " in line.upper() and "ovpw" in line for line in bridge.log)


def test_encoded_header_cannot_forge_rows(bridge, capsys):
    code, out, _ = run(capsys, "list")
    assert code == 0
    rows = [row for row in out.splitlines() if row.strip()]
    assert len(rows) == len(MESSAGES)
    assert all(len(row.split("\t")) == 4 for row in rows)


def test_script_has_no_write_path():
    source = SCRIPT.read_text()
    for word in ("STORE", "APPEND", "EXPUNGE", "COPY", "MOVE", "SMTP", "smtplib", "conn.store(", "conn.append(", "conn.copy(", "conn.expunge(", "conn.delete("):
        assert word not in source, word
    assert "readonly=True" in source


def parse_sieve(text):
    """Return whether braces, parentheses, and quotes balance in the Sieve file."""
    no_comments = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    return no_comments.count("{") == no_comments.count("}") and no_comments.count("(") == no_comments.count(")") and no_comments.count('"') % 2 == 0


def test_sieve_filter_shape():
    text = SIEVE.read_text()
    assert text.startswith("#")
    assert parse_sieve(text)
    assert re.search(r'require\s*\[[^\]]*"fileinto"', text)
    assert 'fileinto "Services"' in text
    assert "monitor@907.life" in text
    for sender in ("cloudflare", "github", "hetzner", "fastmail", "pikapods", "proton"):
        assert sender in text.lower(), sender
    for word in ("reset", "password", "code", "verify", "verification", "sign in", "sign-in", "login", "log in", "new device", "security alert", "2FA", "two-factor", "recovery", "confirm your"):
        assert f'"{word}"' in text, word
    # The exclusion must come before any fileinto so an access-marking subject stays in the inbox.
    assert text.index("stop") < text.index('fileinto "Services"')
    # Subdomain senders (notify.cloudflare.com) must match, so each domain is listed as a wildcard too.
    assert ":matches" in text
    for domain in ("cloudflare.com", "github.com", "hetzner.com", "fastmail.com", "pikapods.com", "proton.me", "protonmail.com"):
        assert f'"*.{domain}"' in text, domain
    # A person can write from their own Proton or Fastmail address, so those domains file only
    # together with an automated local part.
    assert "allof" in text and ":localpart" in text
    guarded = text[text.index("allof"):]
    for domain in ("proton.me", "fastmail.com"):
        assert f'"{domain}"' in guarded, domain
        assert f'"{domain}"' not in text[:text.index("allof")], domain


def test_fetch_without_uid_fails_closed():
    class Conn:
        def uid(self, *args):
            return "OK", [(b"1 (BODY[HEADER.FIELDS (DATE FROM SUBJECT)] {9}", b"Subject: x\r\n"), b")"]

    with pytest.raises(pmr.ReadError, match="no UID"):
        pmr.summaries(Conn(), [1])
