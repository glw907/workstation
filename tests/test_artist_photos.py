"""Tests for artist-photos, the helper that gives each library artist a photo.

Each test builds a Navidrome database and a beets database under tmp_path, replaces the
helper's one fetch function with fixture replies, and points the navidrome binary at a stub
that records its arguments. Nothing reaches the network or the live library.
"""

import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import sqlite3
import stat

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin/.local/bin/artist-photos"
FIXTURES = ROOT / "tests/fixtures/artist-photos"

loader = importlib.machinery.SourceFileLoader("artist_photos", str(SCRIPT))
spec = importlib.util.spec_from_loader("artist_photos", loader)
ap = importlib.util.module_from_spec(spec)
loader.exec_module(ap)

UA = "artist-photos/" + ap.VERSION + " ( glw@907.life )"
NOW = 1_800_000_000.0
DAY = 86400

ALPHA = "11111111-1111-4111-8111-111111111111"
BRAVO = "22222222-2222-4222-8222-222222222222"
CHARLIE = "33333333-3333-4333-8333-333333333333"
DELTA = "44444444-4444-4444-8444-444444444444"
ECHO = "55555555-5555-4555-8555-555555555555"
FOXTROT = "66666666-6666-4666-8666-666666666666"
GOLF = "77777777-7777-4777-8777-777777777777"
HOTEL = "88888888-8888-4888-8888-888888888888"
INDIA = "99999999-9999-4999-8999-999999999999"
JULIET = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
KILO = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
LIMA = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
MIKE = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
NOVEMBER = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"

SCHEMA = """
create table library (id integer primary key, path text not null,
    last_scan_at datetime not null default '0000-00-00 00:00:00');
create table artist (id varchar primary key, name varchar not null default '',
    mbz_artist_id varchar not null default '', missing boolean not null default false);
create table item_artwork (item_kind text not null, item_id text not null,
    image_type text not null default 'primary', source text not null default '',
    source_path text not null default '', primary key (item_kind, item_id, image_type));
create table album (id varchar primary key, name varchar not null default '',
    min_year int not null default 0, missing boolean not null default false,
    participants jsonb not null default '{}');
create table media_file (id varchar primary key, path varchar not null default '',
    title varchar not null default '', album varchar not null default '',
    album_id varchar not null default '', library_id integer not null default 1,
    missing boolean not null default false);
create table media_file_artists (media_file_id varchar not null, artist_id varchar not null,
    role varchar not null default '');
"""


def jpeg(tag):
    return b"\xff\xd8\xff\xe0" + tag.encode() + b"\x00" * 32


def png(tag):
    return b"\x89PNG\r\n\x1a\n" + tag.encode() + b"\x00" * 32


def mb_url(mbid):
    return f"https://musicbrainz.org/ws/2/artist/{mbid}?inc=url-rels+release-groups&fmt=json"


def commons(name):
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{name}?width=1200"


def reply(body, status=200, content_type="application/json", headers=None):
    if isinstance(body, (dict, list)):
        body = json.dumps(body).encode()
    elif isinstance(body, str):
        body = body.encode()
    all_headers = {"content-type": content_type, **(headers or {})}
    return ap.Reply(status, all_headers, body, "")


def image(body, content_type="image/jpeg"):
    return reply(body, content_type=content_type)


def fixture(name, content_type="application/json"):
    return reply((FIXTURES / name).read_bytes(), content_type=content_type)


def mb(mbid, rels):
    return reply({"id": mbid, "relations": [
        {"type": kind, "url": {"resource": url}} for kind, url in rels
    ]})


class Web:
    """Fixture replies by URL; a list is served in turn, its last item repeating. Others are 404."""

    def __init__(self):
        self.routes = {}
        self.requests = []

    def __setitem__(self, url, value):
        self.routes[url] = list(value) if isinstance(value, list) else [value]

    def __call__(self, url, headers):
        assert headers.get("User-Agent") == UA, (url, headers)
        self.requests.append((url, dict(headers)))
        queue = self.routes.get(url)
        if not queue:
            return ap.Reply(404, {"content-type": "text/plain"}, b"not found", url)
        answer = queue.pop(0) if len(queue) > 1 else queue[0]
        return ap.Reply(answer.status, answer.headers, answer.body, url)

    def urls(self):
        return [u for u, _ in self.requests]


class Box:
    """A scratch library, its two databases, the photo folder, and the stub navidrome."""

    def __init__(self, tmp_path):
        self.tmp = tmp_path
        self.music = tmp_path / "Music"
        self.music.mkdir()
        self.folder = self.music / ".artist-images"
        self.folder.mkdir()
        self.state_dir = tmp_path / "state"
        self.nd_db = tmp_path / "navidrome/navidrome.db"
        self.nd_db.parent.mkdir()
        self.beets_db = tmp_path / "beets.db"
        self.calls = tmp_path / "navidrome-calls"
        self.stub = tmp_path / "navidrome-stub"
        self.stub.write_text(f'#!/bin/sh\nprintf "%s\\n" "$*" >> "{self.calls}"\n')
        self.stub.chmod(0o755)
        self.secrets = tmp_path / "secrets"
        self.secrets.write_text("export OTHER=1\nexport DISCOGS_TOKEN='fixture-token'\n")
        self.web = Web()
        self.sleeps = []
        self.rows = []
        self.scan_at = "2026-11-24 18:46:32.582002428-09:00"
        self.beets_added = 1795578000.0
        self.n = 0

    def artist(self, mbid, name, *, nd_id=None, stored=None, role="artist", album=None,
               titles=(), cover=None, missing=False):
        """Add one artist; stored is its item_artwork source_path, None for no row."""
        self.n += 1
        nd_id = nd_id or f"nd{self.n:02d}"
        album = album or f"{name} Album"
        self.rows.append(("artist", (nd_id, name, mbid, int(missing))))
        if stored is not None:
            self.rows.append(("art", (nd_id, "folder" if stored else "", stored)))
        al_id = f"al{self.n:02d}"
        rel = f"{name}/{album}/01.mp3"
        participants = {"albumartist": [{"id": nd_id, "name": name}]}
        self.rows.append(("album", (al_id, album, 2000 + self.n, json.dumps(participants))))
        for i, title in enumerate(titles or ("Song",)):
            mf = f"mf{self.n:02d}{i}"
            self.rows.append(("file", (mf, rel, title, album, al_id)))
            self.rows.append(("role", (mf, nd_id, role)))
        if cover is not None:
            path = self.music / name / album / "cover.jpg"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(cover)
        return nd_id

    def state(self, mbid, **entry):
        path = self.folder / "state.json"
        data = json.loads(path.read_text()) if path.exists() else {"artists": {}}
        data["artists"][mbid] = entry
        path.write_text(json.dumps(data))

    def helper_file(self, mbid, body, ext="jpg", **entry):
        """Place a file the helper wrote earlier and record it in state.json."""
        name = f"{mbid}.{ext}"
        (self.folder / name).write_bytes(body)
        fields = {
            "status": "photo", "kind": "photo", "confidence": "sure", "source": "discogs",
            "url": "https://i.discogs.com/old.jpg", "last_try": NOW - 100 * DAY,
            "file": name, "sha256": hashlib.sha256(body).hexdigest(),
        }
        fields.update(entry)
        self.state(mbid, **fields)
        return self.folder / name

    def build(self):
        db = sqlite3.connect(self.nd_db)
        db.executescript(SCHEMA)
        db.execute("insert into library (id, path, last_scan_at) values (1, ?, ?)",
                   (str(self.music), self.scan_at))
        sql = {
            "artist": "insert into artist (id, name, mbz_artist_id, missing) values (?, ?, ?, ?)",
            "art": "insert into item_artwork (item_kind, item_id, source, source_path)"
                   " values ('ar', ?, ?, ?)",
            "album": "insert into album (id, name, min_year, participants) values (?, ?, ?, ?)",
            "file": "insert into media_file (id, path, title, album, album_id) values (?, ?, ?, ?, ?)",
            "role": "insert into media_file_artists (media_file_id, artist_id, role) values (?, ?, ?)",
        }
        for kind, values in self.rows:
            db.execute(sql[kind], values)
        db.commit()
        db.close()
        self.nd_db.chmod(0o444)
        beets = sqlite3.connect(self.beets_db)
        beets.execute("create table items (id integer primary key, added real)")
        beets.execute("insert into items (added) values (?)", (self.beets_added,))
        beets.commit()
        beets.close()

    def run(self, monkeypatch):
        if not self.nd_db.exists():
            self.build()
        before = self.nd_db.read_bytes()
        monkeypatch.setattr(ap, "fetch", self.web)
        monkeypatch.setattr(ap, "sleep", self.sleeps.append)
        monkeypatch.setattr(ap, "now", lambda: NOW)
        monkeypatch.setattr(ap, "monotonic", lambda: 0.0)
        code = ap.main()
        assert self.nd_db.read_bytes() == before, "the Navidrome database changed"
        return code

    def entry(self, mbid):
        return json.loads((self.folder / "state.json").read_text())["artists"].get(mbid, {})

    def files(self, mbid):
        return sorted(p.name for p in self.folder.iterdir() if p.name.lower().startswith(mbid))

    def report(self):
        return (self.state_dir / "report.md").read_text()

    def section(self, title):
        text = self.report()
        start = text.index(f"## {title}\n")
        end = text.find("\n## ", start + 1)
        return text[start:end if end != -1 else None]

    def refreshed(self):
        return self.calls.read_text().splitlines() if self.calls.exists() else []


@pytest.fixture
def box(tmp_path, monkeypatch):
    b = Box(tmp_path)
    for name in ("DISCOGS_TOKEN", "ND_ARTISTIMAGEFOLDER", "ND_DATAFOLDER", "STATE_DIRECTORY"):
        monkeypatch.delenv(name, raising=False)
    for name, path in {"FOLDER": b.folder, "NAVIDROME_DB": b.nd_db, "BEETS_DB": b.beets_db,
                       "NAVIDROME": b.stub, "STATE": b.state_dir, "SECRETS": b.secrets}.items():
        monkeypatch.setenv(f"ARTIST_PHOTOS_{name}", str(path))
    yield b
    for url, headers in b.web.requests:
        assert headers["User-Agent"] == UA, url


def alpha_routes(web):
    web[mb_url(ALPHA)] = fixture("musicbrainz-alpha.json")
    web["https://api.discogs.com/artists/1001"] = fixture("discogs-artist-1001.json")
    web["https://www.wikidata.org/wiki/Special:EntityData/Q1001.json"] = fixture("wikidata-Q1001.json")
    web["https://i.discogs.com/alpha-primary.jpg"] = image(jpeg("alpha-discogs"))
    web["https://i.discogs.com/alpha-second.jpg"] = image(jpeg("alpha-second"))
    web[commons("Alpha_live_2019.jpg")] = image(jpeg("alpha-wikidata"))


def apple_routes(web):
    web["https://itunes.apple.com/search?term=Bravo&entity=musicArtist&limit=25"] = fixture(
        "itunes-search-bravo.json")
    web["https://itunes.apple.com/lookup?id=2001&entity=album&limit=200"] = fixture(
        "itunes-lookup-2001.json")
    web["https://music.apple.com/us/artist/bravo/2001"] = fixture("apple-page-bravo.html", "text/html")
    web["https://is1-ssl.mzstatic.com/image/thumb/Music/bravo-album/1200x630cw.png"] = image(
        png("bravo-og"), "image/png")
    web["https://is1-ssl.mzstatic.com/image/thumb/Music/bravo-album/1200x1200bb.jpg"] = image(
        jpeg("bravo-cover"))


def deezer_routes(web):
    web["https://api.deezer.com/search/artist?q=Charlie"] = fixture("deezer-search-charlie.json")
    web["https://api.deezer.com/artist/3001/albums?limit=100"] = fixture("deezer-albums-3001.json")
    web["https://api.deezer.com/artist/3002/albums?limit=100"] = fixture("deezer-albums-3002.json")
    web["https://e-cdns-images.dzcdn.net/images/artist/wrong/1000x1000-000000-80-0-0.jpg"] = image(
        jpeg("charlie-wrong"))
    web["https://e-cdns-images.dzcdn.net/images/artist/right/1000x1000-000000-80-0-0.jpg"] = image(
        jpeg("charlie-right"))


def test_discogs_image_wins_over_wikidata(box, monkeypatch):
    box.artist(ALPHA, "Alpha")
    alpha_routes(box.web)

    assert box.run(monkeypatch) == 0

    assert (box.folder / f"{ALPHA}.jpg").read_bytes() == jpeg("alpha-discogs")
    entry = box.entry(ALPHA)
    assert entry["source"] == "discogs"
    assert entry["kind"] == "photo"
    assert entry["confidence"] == "sure"
    assert entry["url"] == "https://i.discogs.com/alpha-primary.jpg"
    # The chain stops at the first source that passes, so Wikidata is never asked.
    assert not any("wikidata" in u for u in box.web.urls())
    discogs = [h for u, h in box.web.requests if u.startswith("https://api.discogs.com/")]
    assert discogs and all(h["Authorization"] == "Discogs token=fixture-token" for h in discogs)
    assert all("Authorization" not in h for u, h in box.web.requests
               if not u.startswith("https://api.discogs.com/"))


def test_wikidata_fills_in_without_a_token(box, monkeypatch):
    box.secrets.write_text("export OTHER=1\n")
    box.artist(ALPHA, "Alpha")
    alpha_routes(box.web)

    assert box.run(monkeypatch) == 0

    assert (box.folder / f"{ALPHA}.jpg").read_bytes() == jpeg("alpha-wikidata")
    assert box.entry(ALPHA)["source"] == "wikidata"
    assert not any("discogs" in u for u in box.web.urls())
    assert "Discogs was skipped" in box.report()


def test_token_comes_from_the_environment_first(box, monkeypatch):
    monkeypatch.setenv("DISCOGS_TOKEN", "env-token")
    box.artist(ALPHA, "Alpha")
    alpha_routes(box.web)

    box.run(monkeypatch)

    discogs = [h for u, h in box.web.requests if u.startswith("https://api.discogs.com/")]
    assert discogs[0]["Authorization"] == "Discogs token=env-token"


def test_apple_image_without_amcartistimages_is_passed_over(box, monkeypatch):
    box.artist(BRAVO, "Bravo", album="Bravo Album")
    apple_routes(box.web)

    box.run(monkeypatch)

    entry = box.entry(BRAVO)
    assert entry["source"] == "apple-cover"
    assert entry["kind"] == "fallback"
    assert (box.folder / f"{BRAVO}.jpg").read_bytes() == jpeg("bravo-cover")
    assert not (box.folder / f"{BRAVO}.png").exists()
    assert "https://is1-ssl.mzstatic.com/image/thumb/Music/bravo-album/1200x630cw.png" not in box.web.urls()


def test_apple_image_under_amcartistimages_is_a_low_confidence_photo(box, monkeypatch):
    box.artist(BRAVO, "Bravo", album="Bravo Album")
    apple_routes(box.web)
    photo = "https://is1-ssl.mzstatic.com/image/thumb/AMCArtistImages/bravo/1200x630cw.png"
    box.web["https://music.apple.com/us/artist/bravo/2001"] = reply(
        f'<meta property="og:image" content="{photo}">', content_type="text/html")
    box.web[photo] = image(png("bravo-photo"), "image/png")

    box.run(monkeypatch)

    entry = box.entry(BRAVO)
    assert (entry["source"], entry["kind"], entry["confidence"]) == ("apple", "photo", "low")
    assert (box.folder / f"{BRAVO}.png").read_bytes() == png("bravo-photo")


def test_deezer_takes_only_an_exact_name_with_a_shared_title(box, monkeypatch):
    box.artist(CHARLIE, "Charlie", album="Charlie Songs")
    deezer_routes(box.web)

    box.run(monkeypatch)

    entry = box.entry(CHARLIE)
    assert (entry["source"], entry["kind"], entry["confidence"]) == ("deezer", "photo", "low")
    assert (box.folder / f"{CHARLIE}.jpg").read_bytes() == jpeg("charlie-right")
    urls = box.web.urls()
    # 3001 is an exact name with no shared title, so its picture is never fetched; 3003 isn't
    # an exact name, so its albums aren't either.
    assert "https://api.deezer.com/artist/3001/albums?limit=100" in urls
    assert not any("/wrong/" in u for u in urls)
    assert "https://api.deezer.com/artist/3003/albums?limit=100" not in urls
    assert f"- Charlie (`{CHARLIE}`): deezer," in box.section("Low-confidence photos")


def test_deezer_match_with_no_shared_title_is_refused(box, monkeypatch):
    box.artist(CHARLIE, "Charlie", album="Something Unrelated")
    deezer_routes(box.web)

    box.run(monkeypatch)

    assert box.files(CHARLIE) == []
    assert box.entry(CHARLIE)["status"] == "none"
    assert not any("dzcdn.net" in u for u in box.web.urls())


def test_manual_file_is_kept_and_never_retried(box, monkeypatch):
    nd = box.artist(ECHO, "Echo", stored=str(box.folder / f"{ECHO}.png"))
    ours = box.helper_file(ECHO, png("echo-ours"), ext="png", status="fallback", kind="fallback",
                           last_try=NOW - 60 * DAY)
    manual = box.folder / f"{ECHO}.JPG"
    manual.write_bytes(jpeg("echo-by-hand"))

    assert box.run(monkeypatch) == 0

    assert not ours.exists(), "the helper's own file for that ID stays"
    assert manual.read_bytes() == jpeg("echo-by-hand")
    assert not any(ECHO in u for u in box.web.urls())
    entry = box.entry(ECHO)
    assert entry["status"] == "manual"
    assert entry["manual_sha256"] == hashlib.sha256(jpeg("echo-by-hand")).hexdigest()
    assert f"- Echo (`{ECHO}`): {ECHO}.JPG" in box.section("Manual files")
    assert box.refreshed() == [f"artwork refresh ar {nd}"]

    # A later run, long after, still leaves it alone.
    box.calls.unlink()
    monkeypatch.setattr(ap, "now", lambda: NOW + 90 * DAY)
    box.web.requests.clear()
    ap.main()
    assert manual.read_bytes() == jpeg("echo-by-hand")
    assert not any(ECHO in u for u in box.web.urls())
    assert box.entry(ECHO)["status"] == "manual"


def test_manual_file_dropped_over_the_helpers_name_is_kept(box, monkeypatch):
    path = box.folder / f"{ALPHA}.jpg"
    nd = box.artist(ALPHA, "Alpha", stored=str(path))
    box.helper_file(ALPHA, jpeg("alpha-ours"))
    path.write_bytes(jpeg("alpha-by-hand"))
    alpha_routes(box.web)

    box.run(monkeypatch)

    assert path.read_bytes() == jpeg("alpha-by-hand")
    assert box.entry(ALPHA)["status"] == "manual"
    assert box.web.urls() == []
    # Same name, new bytes: Navidrome's stored path already matches, so only "new this run"
    # sends it.
    assert box.refreshed() == [f"artwork refresh ar {nd}"]


@pytest.mark.parametrize("bad", [
    reply("<!DOCTYPE html><html><body>Not an image</body></html>", content_type="text/html"),
    image(png("png-bytes-claiming-jpeg"), "image/jpeg"),
    image(jpeg("huge") + b"\x00" * (11 * 1024 * 1024)),
], ids=["html", "wrong-magic", "11MB"])
def test_a_bad_reply_is_not_written(box, monkeypatch, bad):
    box.artist(FOXTROT, "Foxtrot")
    box.web[mb_url(FOXTROT)] = mb(FOXTROT, [
        ("discogs", "https://www.discogs.com/artist/6001-Foxtrot"),
        ("wikidata", "https://www.wikidata.org/wiki/Q6001"),
    ])
    box.web["https://api.discogs.com/artists/6001"] = reply(
        {"images": [{"type": "primary", "uri": "https://i.discogs.com/foxtrot.jpg"}]})
    box.web["https://i.discogs.com/foxtrot.jpg"] = bad
    box.web["https://www.wikidata.org/wiki/Special:EntityData/Q6001.json"] = reply({"entities": {"Q6001": {
        "claims": {"P18": [{"mainsnak": {"datavalue": {"value": "Foxtrot.jpg"}}}]}}}})
    box.web[commons("Foxtrot.jpg")] = image(jpeg("foxtrot-wikidata"))

    box.run(monkeypatch)

    assert "https://i.discogs.com/foxtrot.jpg" in box.web.urls()
    assert box.files(FOXTROT) == [f"{FOXTROT}.jpg"]
    assert (box.folder / f"{FOXTROT}.jpg").read_bytes() == jpeg("foxtrot-wikidata")
    assert box.entry(FOXTROT)["source"] == "wikidata"
    assert not list(box.folder.glob(".*.part"))


def test_five_musicbrainz_503s_defer_that_artist_and_the_rest_run(box, monkeypatch):
    box.artist(GOLF, "Golf")
    box.artist(HOTEL, "Hotel")
    box.web[mb_url(GOLF)] = reply("busy", status=503, content_type="text/plain")
    box.web[mb_url(HOTEL)] = mb(HOTEL, [("wikidata", "https://www.wikidata.org/wiki/Q8001")])
    box.web["https://www.wikidata.org/wiki/Special:EntityData/Q8001.json"] = reply({"entities": {"Q8001": {
        "claims": {"P18": [{"mainsnak": {"datavalue": {"value": "Hotel.jpg"}}}]}}}})
    box.web[commons("Hotel.jpg")] = image(jpeg("hotel"))

    assert box.run(monkeypatch) == 0

    assert box.web.urls().count(mb_url(GOLF)) == 5
    assert [s for s in box.sleeps if s >= 5] == [5, 10, 20, 40]
    assert box.entry(GOLF)["deferred"] is True
    assert box.files(GOLF) == []
    assert box.entry(HOTEL)["status"] == "photo"
    assert f"- Golf (`{GOLF}`)" in box.section("Deferred by a failed request")
    assert "Golf" not in box.section("No file")

    # The next run tries it again at once.
    box.web[mb_url(GOLF)] = reply({}, status=200)
    box.web.requests.clear()
    ap.main()
    assert mb_url(GOLF) in box.web.urls()
    assert box.entry(GOLF)["deferred"] is False


def test_a_fallback_tried_29_days_ago_runs_again_and_27_days_ago_doesnt(box, monkeypatch):
    box.artist(INDIA, "India")
    box.artist(JULIET, "Juliet")
    box.helper_file(INDIA, jpeg("india-cover"), status="fallback", kind="fallback",
                    last_try=NOW - 29 * DAY)
    box.helper_file(JULIET, jpeg("juliet-cover"), status="fallback", kind="fallback",
                    last_try=NOW - 27 * DAY)

    box.run(monkeypatch)

    assert mb_url(INDIA) in box.web.urls()
    assert mb_url(JULIET) not in box.web.urls()
    # The retry found nothing better, so the earlier cover stays.
    assert (box.folder / f"{INDIA}.jpg").read_bytes() == jpeg("india-cover")
    assert box.entry(INDIA)["last_try"] == NOW
    assert box.entry(JULIET)["last_try"] == NOW - 27 * DAY


def test_none_retries_after_28_days_and_a_photo_never_does(box, monkeypatch):
    box.artist(KILO, "Kilo")
    box.artist(LIMA, "Lima")
    box.artist(MIKE, "Mike")
    box.state(KILO, status="none", last_try=NOW - 29 * DAY)
    box.state(LIMA, status="none", last_try=NOW - 27 * DAY)
    box.helper_file(MIKE, jpeg("mike"), last_try=NOW - 400 * DAY)

    box.run(monkeypatch)

    urls = box.web.urls()
    assert mb_url(KILO) in urls
    assert mb_url(LIMA) not in urls
    assert mb_url(MIKE) not in urls


def test_refresh_names_exactly_the_artists_whose_stored_path_isnt_their_file(box, monkeypatch):
    deezer_art = box.artist(ALPHA, "Alpha", stored="")
    box.helper_file(ALPHA, jpeg("alpha"))
    matching = box.artist(BRAVO, "Bravo", stored=str(box.folder / f"{BRAVO}.jpg"))
    box.helper_file(BRAVO, jpeg("bravo"))
    box.artist(CHARLIE, "Charlie")  # no item_artwork row: Navidrome resolves it fresh
    box.helper_file(CHARLIE, jpeg("charlie"))
    old_ext = box.artist(DELTA, "Delta", stored=str(box.folder / f"{DELTA}.png"))
    box.helper_file(DELTA, jpeg("delta"))
    box.artist(ECHO, "Echo", stored="")  # no file in the folder
    box.state(ECHO, status="none", last_try=NOW - DAY)
    lib_file = box.artist(FOXTROT, "Foxtrot", stored=str(box.music / "Foxtrot/artist.jpg"))
    box.helper_file(FOXTROT, jpeg("foxtrot"))

    assert box.run(monkeypatch) == 0

    assert box.web.requests == []
    assert box.refreshed() == [f"artwork refresh ar {deezer_art} {old_ext}"]
    assert matching not in box.refreshed()[0]
    assert lib_file not in box.refreshed()[0]


def test_artist_file_in_the_library_keeps_that_artist_out(box, monkeypatch):
    box.artist(ALPHA, "Alpha", stored=str(box.music / "Alpha/artist.jpg"))
    alpha_routes(box.web)

    box.run(monkeypatch)

    assert box.web.requests == []
    assert box.files(ALPHA) == []
    assert "Alpha" not in box.report()


def test_out_of_scope_artists_are_skipped(box, monkeypatch):
    box.artist(ALPHA, "Alpha", role="composer")
    box.artist(BRAVO, "Bravo", missing=True)
    box.artist("", "Wendy")
    box.artist("not-a-uuid", "Broken")

    box.run(monkeypatch)

    assert box.web.requests == []
    assert list(box.folder.glob("*.jpg")) == []


def test_a_new_file_under_the_same_name_is_refreshed(box, monkeypatch):
    path = box.folder / f"{INDIA}.jpg"
    nd = box.artist(INDIA, "India", stored=str(path))
    box.helper_file(INDIA, jpeg("india-cover"), status="fallback", kind="fallback",
                    last_try=NOW - 29 * DAY)
    box.web[mb_url(INDIA)] = mb(INDIA, [("wikidata", "https://www.wikidata.org/wiki/Q9001")])
    box.web["https://www.wikidata.org/wiki/Special:EntityData/Q9001.json"] = reply({"entities": {"Q9001": {
        "claims": {"P18": [{"mainsnak": {"datavalue": {"value": "India.jpg"}}}]}}}})
    box.web[commons("India.jpg")] = image(jpeg("india-photo"))

    box.run(monkeypatch)

    assert path.read_bytes() == jpeg("india-photo")
    assert box.entry(INDIA)["status"] == "photo"
    assert box.refreshed() == [f"artwork refresh ar {nd}"]


def test_a_changed_extension_removes_the_earlier_file(box, monkeypatch):
    box.artist(INDIA, "India")
    old = box.helper_file(INDIA, png("india-cover"), ext="png", status="fallback", kind="fallback",
                          last_try=NOW - 29 * DAY)
    box.web[mb_url(INDIA)] = mb(INDIA, [("bandcamp", "https://india.bandcamp.com/")])
    box.web["https://india.bandcamp.com/"] = fixture("bandcamp-page.html", "text/html")
    box.web["https://india.bandcamp.com/img/delta-photo.jpg"] = image(jpeg("india-bandcamp"))

    box.run(monkeypatch)

    assert not old.exists()
    assert box.files(INDIA) == [f"{INDIA}.jpg"]
    assert box.entry(INDIA)["source"] == "bandcamp"
    assert box.entry(INDIA)["confidence"] == "sure"


def test_library_cover_is_the_last_fallback(box, monkeypatch):
    box.artist(KILO, "Kilo", cover=jpeg("kilo-cover"))

    box.run(monkeypatch)

    entry = box.entry(KILO)
    assert (entry["source"], entry["kind"]) == ("library", "fallback")
    assert (box.folder / f"{KILO}.jpg").read_bytes() == jpeg("kilo-cover")


def test_discogs_release_cover_comes_first_among_fallbacks(box, monkeypatch):
    box.artist(KILO, "Kilo", cover=jpeg("kilo-library"))
    box.web[mb_url(KILO)] = mb(KILO, [("discogs", "https://www.discogs.com/artist/7001-Kilo")])
    box.web["https://api.discogs.com/artists/7001"] = reply({"images": []})
    box.web["https://api.discogs.com/artists/7001/releases?sort=year&sort_order=asc&per_page=100"] = reply(
        {"releases": [
            {"id": 71, "type": "release", "role": "Appearance", "year": 1990},
            {"id": 72, "type": "master", "role": "Main", "year": 1998},
            {"id": 73, "type": "release", "role": "Main", "year": 0},
            {"id": 74, "type": "release", "role": "Main", "year": 2004},
        ]})
    box.web["https://api.discogs.com/masters/72"] = reply(
        {"images": [{"type": "primary", "uri": "https://i.discogs.com/kilo-1998.jpg"}]})
    box.web["https://i.discogs.com/kilo-1998.jpg"] = image(jpeg("kilo-1998"))

    box.run(monkeypatch)

    entry = box.entry(KILO)
    assert (entry["source"], entry["kind"]) == ("discogs-release", "fallback")
    assert (box.folder / f"{KILO}.jpg").read_bytes() == jpeg("kilo-1998")


def test_report_lists_each_kind_of_artist(box, monkeypatch):
    box.artist(BRAVO, "Bravo", album="Bravo Album")
    apple_routes(box.web)
    box.artist(CHARLIE, "Charlie", album="Charlie Songs")
    deezer_routes(box.web)
    box.artist(ECHO, "Echo")
    (box.folder / f"{ECHO}.jpg").write_bytes(jpeg("echo-by-hand"))
    box.artist(NOVEMBER, "November Rain")
    box.artist(GOLF, "Golf")
    box.web[mb_url(GOLF)] = reply("busy", status=503, content_type="text/plain")
    box.artist(ALPHA, "Alpha")
    alpha_routes(box.web)

    assert box.run(monkeypatch) == 0

    assert f"- Bravo (`{BRAVO}`): apple-cover," in box.section("Release covers in place of a photo")
    assert f"- Charlie (`{CHARLIE}`): deezer," in box.section("Low-confidence photos")
    assert f"- Echo (`{ECHO}`): {ECHO}.jpg" in box.section("Manual files")
    none = box.section("No file")
    assert f"- November Rain (`{NOVEMBER}`): [MusicBrainz](https://musicbrainz.org/artist/{NOVEMBER})" in none
    assert "site%3Apartyflock.nl+November+Rain" in none
    assert "site%3Ara.co+November+Rain" in none
    assert f"- Golf (`{GOLF}`)" in box.section("Deferred by a failed request")
    assert "Alpha" not in box.report().split("## ", 1)[1]
    assert "Discogs was skipped" not in box.report()


def test_summary_line_goes_to_the_journal(box, monkeypatch, capsys):
    box.artist(ALPHA, "Alpha")
    alpha_routes(box.web)
    box.artist(KILO, "Kilo", cover=jpeg("kilo-cover"))
    box.artist(NOVEMBER, "November")
    box.artist(GOLF, "Golf")
    box.web[mb_url(GOLF)] = reply("busy", status=503, content_type="text/plain")

    box.run(monkeypatch)

    assert capsys.readouterr().out.strip().splitlines()[-1] == (
        "artist-photos: 4 artists tried: 1 photos, 1 fallbacks, 1 none, 1 deferred")


def test_every_request_carries_the_user_agent(box, monkeypatch):
    box.artist(ALPHA, "Alpha")
    alpha_routes(box.web)
    box.artist(BRAVO, "Bravo", album="Bravo Album")
    apple_routes(box.web)
    box.artist(CHARLIE, "Charlie", album="Charlie Songs")
    deezer_routes(box.web)
    box.artist(GOLF, "Golf")
    box.web[mb_url(GOLF)] = reply("busy", status=503, content_type="text/plain")
    box.artist(INDIA, "India")
    box.web[mb_url(INDIA)] = mb(INDIA, [
        ("bandcamp", "https://india.bandcamp.com/"),
        ("social network", "https://social.example/india"),
        ("soundcloud", "https://soundcloud.com/india"),
        ("youtube", "https://www.youtube.com/@india"),
        ("official homepage", "https://india.example/"),
        ("image", "https://commons.wikimedia.org/wiki/File:India%20band.jpg"),
    ])

    box.run(monkeypatch)

    urls = box.web.urls()
    for host in ("musicbrainz.org", "api.discogs.com", "i.discogs.com", "itunes.apple.com",
                 "music.apple.com", "mzstatic.com", "api.deezer.com", "dzcdn.net",
                 "bandcamp.com", "social.example", "soundcloud.com", "youtube.com",
                 "india.example", "commons.wikimedia.org"):
        assert any(host in u for u in urls), host
    assert commons("India_band.jpg") in urls
    assert len(box.web.requests) > 20
    assert {h["User-Agent"] for _, h in box.web.requests} == {UA}
    assert UA.startswith("artist-photos/") and UA.endswith(" ( glw@907.life )")


def test_requests_are_paced_per_host(box, monkeypatch):
    clock = [0.0]
    stamps = []

    def fake_sleep(seconds):
        clock[0] += seconds

    def timed(url, headers):
        stamps.append((url.split("/")[2], clock[0]))
        return box.web(url, headers)

    box.artist(ALPHA, "Alpha")
    box.artist(BRAVO, "Bravo")
    box.build()
    monkeypatch.setattr(ap, "fetch", timed)
    monkeypatch.setattr(ap, "sleep", fake_sleep)
    monkeypatch.setattr(ap, "now", lambda: NOW)
    monkeypatch.setattr(ap, "monotonic", lambda: clock[0])

    ap.main()

    gaps = {}
    last = {}
    for host, at in stamps:
        if host in last:
            gaps.setdefault(host, []).append(at - last[host])
        last[host] = at
    for host, seen in gaps.items():
        assert min(seen) >= ap.PACE.get(host, ap.DEFAULT_PACE) - 1e-9, host
    assert min(gaps["musicbrainz.org"]) == pytest.approx(1.1)
    assert min(gaps["itunes.apple.com"]) == pytest.approx(3.5)


def test_discogs_waits_when_its_limit_is_near(box, monkeypatch):
    box.artist(ALPHA, "Alpha")
    alpha_routes(box.web)
    box.web["https://api.discogs.com/artists/1001"] = reply(
        (FIXTURES / "discogs-artist-1001.json").read_bytes(),
        headers={"x-discogs-ratelimit-remaining": "2"})

    box.run(monkeypatch)

    assert 60 in box.sleeps


def test_waits_for_navidrome_to_scan_a_new_import(box, monkeypatch):
    box.beets_added = 1795578400.0  # after the 18:46:32 AKST scan
    box.artist(ALPHA, "Alpha")
    box.build()
    polls = []

    def scanned_later(seconds):
        polls.append(seconds)
        if len(polls) == 3:
            box.nd_db.chmod(0o644)
            nd = sqlite3.connect(box.nd_db)
            nd.execute("update library set last_scan_at = '2026-11-24 18:50:00.000000000-09:00'")
            nd.commit()
            nd.close()
            box.nd_db.chmod(0o444)

    monkeypatch.setattr(ap, "fetch", box.web)
    monkeypatch.setattr(ap, "sleep", scanned_later)
    monkeypatch.setattr(ap, "now", lambda: NOW)
    monkeypatch.setattr(ap, "monotonic", lambda: 0.0)

    ap.main()

    assert polls[:3] == [15, 15, 15]
    assert mb_url(ALPHA) in box.web.urls()


def test_gives_up_waiting_after_ten_minutes(box, monkeypatch):
    box.beets_added = 1795578400.0
    box.artist(ALPHA, "Alpha")

    box.run(monkeypatch)

    assert box.sleeps.count(15) == 40
    assert mb_url(ALPHA) in box.web.urls()


def test_navidrome_database_is_opened_read_only(box, monkeypatch):
    box.artist(ALPHA, "Alpha", stored="")
    box.helper_file(ALPHA, jpeg("alpha"))
    box.build()
    assert stat.S_IMODE(box.nd_db.stat().st_mode) == 0o444

    assert box.run(monkeypatch) == 0


def test_a_failed_refresh_fails_the_run_after_writing(box, monkeypatch):
    box.artist(ALPHA, "Alpha", stored="")
    alpha_routes(box.web)
    box.stub.write_text("#!/bin/sh\nexit 3\n")

    assert box.run(monkeypatch) == 1

    assert (box.folder / f"{ALPHA}.jpg").exists()
    assert box.entry(ALPHA)["status"] == "photo"


def test_parse_scan_time_reads_navidromes_format():
    assert ap.parse_scan_time("2026-11-24 18:46:32.582002428-09:00") == pytest.approx(1795578392.582002)
    assert ap.parse_scan_time("0000-00-00 00:00:00") == 0.0
    assert ap.parse_scan_time("0001-01-01 00:00:00+00:00") == 0.0
    assert ap.parse_scan_time("") == 0.0


def test_normalize_folds_case_marks_punctuation_and_spaces():
    assert ap.normalize("  Beyoncé!  ") == "beyonce"
    assert ap.normalize("CHARLIE   SONGS (Deluxe)") == "charlie songs deluxe"
    assert ap.normalize("Ｆｕｌｌ") == "full"


def test_a_deleted_helper_file_is_searched_again(box, monkeypatch):
    box.artist(ALPHA, "Alpha")
    box.helper_file(ALPHA, jpeg("alpha-old")).unlink()
    alpha_routes(box.web)

    box.run(monkeypatch)

    assert mb_url(ALPHA) in box.web.urls()
    assert (box.folder / f"{ALPHA}.jpg").read_bytes() == jpeg("alpha-discogs")


def test_a_deleted_helper_file_with_nothing_found_is_reported(box, monkeypatch):
    box.artist(KILO, "Kilo")
    box.helper_file(KILO, jpeg("kilo-old")).unlink()

    box.run(monkeypatch)

    assert box.entry(KILO)["status"] == "none"
    assert f"- Kilo (`{KILO}`)" in box.section("No file")


def test_connect_ro_refuses_a_write_to_a_writable_database(tmp_path):
    path = tmp_path / "rw.db"
    db = sqlite3.connect(path)
    db.execute("create table t (x)")
    db.commit()
    db.close()
    ro = ap.connect_ro(path)
    with pytest.raises(sqlite3.OperationalError):
        ro.execute("insert into t values (1)")
    ro.close()


def test_a_redirect_to_another_host_drops_the_discogs_token():
    handler = ap._NoOddRedirects()
    req = ap.urllib.request.Request("https://api.discogs.com/artists/1", headers={
        "User-Agent": UA, "Authorization": "Discogs token=fixture-token"})

    elsewhere = handler.redirect_request(req, None, 302, "Found", {}, "https://other.example/x")
    same = handler.redirect_request(req, None, 302, "Found", {}, "https://api.discogs.com/artists/2")

    assert not elsewhere.has_header("Authorization")
    assert elsewhere.get_header("User-agent") == UA
    assert same.get_header("Authorization") == "Discogs token=fixture-token"
    with pytest.raises(ap.FetchError):
        handler.redirect_request(req, None, 302, "Found", {}, "file:///etc/passwd")


@pytest.mark.parametrize("error", [
    ap.http.client.IncompleteRead(b"partial"),
    ap.http.client.InvalidURL("URL can't contain control characters"),
    ap.http.client.BadStatusLine("garbage"),
], ids=["incomplete-read", "invalid-url", "bad-status-line"])
def test_an_http_client_error_is_a_fetch_error(monkeypatch, error):
    class Opener:
        def open(self, request, timeout):
            raise error

    monkeypatch.setattr(ap, "_opener", Opener())
    with pytest.raises(ap.FetchError):
        ap.fetch("https://example.invalid/a.jpg", {"User-Agent": UA})
    monkeypatch.setattr(ap, "sleep", lambda s: None)
    assert ap.Client(None).ok("https://example.invalid/a.jpg") is None


def test_a_failed_refresh_of_a_same_name_file_runs_again_next_time(box, monkeypatch):
    path = box.folder / f"{INDIA}.jpg"
    nd = box.artist(INDIA, "India", stored=str(path))
    box.helper_file(INDIA, jpeg("india-cover"), status="fallback", kind="fallback",
                    last_try=NOW - 29 * DAY)
    box.web[mb_url(INDIA)] = mb(INDIA, [("wikidata", "https://www.wikidata.org/wiki/Q9001")])
    box.web["https://www.wikidata.org/wiki/Special:EntityData/Q9001.json"] = reply({"entities": {"Q9001": {
        "claims": {"P18": [{"mainsnak": {"datavalue": {"value": "India.jpg"}}}]}}}})
    box.web[commons("India.jpg")] = image(jpeg("india-photo"))
    good_stub = box.stub.read_text()
    box.stub.write_text(f'#!/bin/sh\nprintf "%s\\n" "$*" >> "{box.calls}"\nexit 3\n')

    assert box.run(monkeypatch) == 1
    assert box.refreshed() == [f"artwork refresh ar {nd}"]

    box.calls.unlink()
    box.stub.write_text(good_stub)
    assert ap.main() == 0
    assert box.refreshed() == [f"artwork refresh ar {nd}"]

    box.calls.unlink()
    assert ap.main() == 0
    assert box.refreshed() == []
    assert "refresh" not in box.entry(INDIA)


def test_a_failed_refresh_of_a_new_manual_file_runs_again_next_time(box, monkeypatch):
    path = box.folder / f"{ALPHA}.jpg"
    nd = box.artist(ALPHA, "Alpha", stored=str(path))
    box.helper_file(ALPHA, jpeg("alpha-ours"))
    path.write_bytes(jpeg("alpha-by-hand"))
    good_stub = box.stub.read_text()
    box.stub.write_text("#!/bin/sh\nexit 3\n")

    assert box.run(monkeypatch) == 1

    box.stub.write_text(good_stub)
    assert ap.main() == 0
    assert box.refreshed() == [f"artwork refresh ar {nd}"]
    assert box.entry(ALPHA)["status"] == "manual"


def test_a_truncated_error_body_still_gives_its_status(monkeypatch):
    class Body:
        def read(self, n=-1):
            raise ap.http.client.IncompleteRead(b"part")

        def close(self):
            pass

    class Opener:
        def open(self, request, timeout):
            raise ap.urllib.error.HTTPError(request.full_url, 503, "Service Unavailable", {}, Body())

    monkeypatch.setattr(ap, "_opener", Opener())
    got = ap.fetch("https://musicbrainz.org/ws/2/artist/x", {"User-Agent": UA})

    assert got.status == 503
    assert got.body == b""
