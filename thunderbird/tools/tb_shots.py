"""Drive the harness Thunderbird over Marionette and write the screenshot set.

tb-shots starts a headless Thunderbird on a scratch profile and then runs this
module. It sets message states by Message-ID, switches light and dark and the
two list views live, and saves each screenshot under the output folder.
"""

import argparse
import sys
import time
from pathlib import Path

from marionette_driver.marionette import Marionette

WIDTH, HEIGHT = 1600, 1000
# The lists get a tall window so every card shows without scrolling.
LIST_HEIGHT = 2000

# Message-IDs of the fixture messages (fixtures/messages/*.eml), no angle
# brackets. UNREAD is every message not listed here that is not read: all
# messages start read, then these are made unread.
UNREAD = ["m01@example.com", "m03@example.com", "m04@example.com", "m08@example.org",
          "m09@example.com", "m12@example.org", "m15@example.com", "m21@example.org"]
FLAGGED = ["m01@example.com", "m16@example.org"]
# Tag keys by message: one tag each on five, two tags on the flagged m01.
TAGS = {
    "m01@example.com": ["$label4", "$label2"],
    "m15@example.com": ["$label1"],
    "m16@example.org": ["$label2"],
    "m17@example.com": ["$label3"],
    "m18@example.org": ["$label4"],
    "m19@example.com": ["$label5"],
}
JUNK = "m20@example.com"
NEW = "m21@example.org"

# Reader cases: file name part -> Message-ID.
READER_CASES = {
    "plain": "m09@example.com",
    "flowed": "m10@example.org",
    "html-cite": "m11@example.com",
    "gmail": "m12@example.org",
    "yahoo": "m13@example.com",
    "outlook": "m14@example.org",
    "flagged-tagged": "m01@example.com",
}

LIST_PREF = "mail.threadpane.listview"
CARDS, TABLE = 0, 1

PRELUDE = """
const { MailServices } = ChromeUtils.importESModule("resource:///modules/MailServices.sys.mjs");
const tabmail = document.getElementById("tabmail");
const a3 = tabmail.currentAbout3Pane;
function inbox() {
  const acct = MailServices.accounts.accounts.find(a => a.incomingServer.type == "none");
  return acct.incomingServer.rootFolder.getChildNamed("Inbox");
}
function hdr(id) { return inbox().msgDatabase.getMsgHdrForMessageID(id); }
"""


class Harness:
    """A Marionette session on the scratch profile's Thunderbird."""

    def __init__(self, port):
        """Connect to Thunderbird on the given Marionette port."""
        self.m = Marionette(host="127.0.0.1", port=port, socket_timeout=120)
        self.notes = []

    def connect(self, timeout=120):
        """Retry until the Marionette server accepts a session."""
        deadline = time.time() + timeout
        while True:
            try:
                self.m.start_session()
                return
            except Exception as err:  # the server is not listening yet
                if time.time() > deadline:
                    raise SystemExit(f"tb_shots: Marionette never came up: {err}")
                time.sleep(1)

    def js(self, body, *args):
        """Run a chrome-context script with the shared prelude and return its value."""
        return self.m.execute_script(PRELUDE + body, script_args=list(args))

    def wait_for(self, body, timeout=60, what="condition"):
        """Poll a chrome script that returns truthy until it does."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            value = self.js(body)
            if value:
                return value
            time.sleep(0.5)
        raise SystemExit(f"tb_shots: timed out waiting for {what}")

    def shot(self, out, name):
        """Save a screenshot of the whole window as <name>.png."""
        path = out / f"{name}.png"
        path.write_bytes(self.m.screenshot(format="binary"))
        print(f"tb_shots: wrote {path.name}")


def select(h, message_id):
    """Select a message in the thread list by Message-ID so the reader opens it."""
    index = h.js(
        """
        const h = hdr(arguments[0]);
        const i = a3.gDBView.findIndexOfMsgHdr(h, true);
        a3.threadTree.selectedIndex = i;
        return i;
        """,
        message_id,
    )
    if index is None or index < 0:
        raise SystemExit(f"tb_shots: {message_id} is not in the list")
    time.sleep(2.5)


def set_mode(h, mode):
    """Switch the whole app to light or dark."""
    dark = 1 if mode == "dark" else 0
    h.js('Services.prefs.setIntPref("ui.systemUsesDarkTheme", arguments[0]);', dark)
    time.sleep(1.5)


def set_view(h, view):
    """Switch the thread list between cards and table."""
    h.js("Services.prefs.setIntPref(arguments[0], arguments[1]);", LIST_PREF, view)
    time.sleep(1.5)


def set_states(h):
    """Set read, flag, tag, junk and new states by Message-ID."""
    result = h.js(
        """
        const [unread, flagged, tags, junk, newId] = arguments;
        const folder = inbox();
        const db = folder.msgDatabase;
        const out = {};
        for (const hd of db.enumerateMessages()) {
          hd.markRead(!unread.includes(hd.messageId));
          hd.markFlagged(flagged.includes(hd.messageId));
        }
        for (const [id, keys] of Object.entries(tags)) {
          folder.addKeywordsToMessages([hdr(id)], keys.join(" "));
        }
        const j = hdr(junk);
        j.setStringProperty("junkscore", "100");
        j.setStringProperty("junkscoreorigin", "user");
        try {
          const n = hdr(newId);
          n.orFlags(Ci.nsMsgMessageFlags.New);
          db.addToNewList(n.messageKey);
          out.new = (n.flags & Ci.nsMsgMessageFlags.New) ? "set" : "the New flag did not stick";
        } catch (e) {
          out.new = "failed: " + e;
        }
        db.commit(Ci.nsMsgDBCommitType.kLargeCommit);
        return out;
        """,
        UNREAD, FLAGGED, TAGS, JUNK, NEW,
    )
    if result["new"] != "set":
        h.notes.append(f"new state not set ({result['new']}); report it as unverified")
    print(f"tb_shots: new state: {result['new']}")


def hover(h, message_id):
    """Move the pointer over a row; return whether :hover took effect."""
    x, y = h.js(
        """
        const h = hdr(arguments[0]);
        const i = a3.gDBView.findIndexOfMsgHdr(h, true);
        a3.threadTree.scrollToIndex(i, true);
        const row = a3.threadTree.getRowAtIndex(i);
        const fr = a3.frameElement.getBoundingClientRect();
        const rr = row.getBoundingClientRect();
        return [Math.round(fr.left + rr.left + rr.width / 2),
                Math.round(fr.top + rr.top + rr.height / 2)];
        """,
        message_id,
    )
    pointer = h.m.actions.sequence("pointer", "mouse", {"pointer_type": "mouse"})
    pointer.pointer_move(x - 3, y).pointer_move(x, y).perform()
    time.sleep(0.5)
    return h.js(
        """
        const h = hdr(arguments[0]);
        const i = a3.gDBView.findIndexOfMsgHdr(h, true);
        return a3.threadTree.getRowAtIndex(i).matches(":hover");
        """,
        message_id,
    )


def main(argv=None):
    """Run the whole screenshot set."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", required=True, help="scratch profile path inside the sandbox")
    ap.add_argument("--port", type=int, default=28282)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--messages", type=Path, help="fixture messages folder (for the count)")
    ap.add_argument("--probe", action="store_true", help="take only the first reader shot")
    args = ap.parse_args(argv)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    h = Harness(args.port)
    h.connect()
    h.m.set_context(h.m.CONTEXT_CHROME)
    profd = h.m.execute_script(
        'return Services.dirsvc.get("ProfD", Ci.nsIFile).path;')
    if profd.rstrip("/") != args.profile.rstrip("/"):
        raise SystemExit(f"tb_shots: connected to {profd}, not the scratch profile {args.profile}")

    h.wait_for('return !!document.getElementById("tabmail")?.currentAbout3Pane', what="main window")
    h.m.set_window_rect(width=WIDTH, height=HEIGHT)
    count = len(list(args.messages.glob("*.eml"))) if args.messages else 1
    h.js('Services.prefs.setIntPref("ui.systemUsesDarkTheme", 1);')
    h.js("a3.displayFolder(inbox().URI);")
    # Two replies fold into their thread root, so the view holds count - 2 rows.
    h.wait_for(f"return a3.gDBView && a3.gDBView.rowCount >= {count - 2};",
               what="the inbox to index")
    time.sleep(2)

    # Probe: a reader shot must show the body text, or E's proof is empty.
    select(h, READER_CASES["plain"])
    h.shot(out, "probe-reader-plain-dark")
    if args.probe:
        return 0
    (out / "probe-reader-plain-dark.png").unlink()

    set_states(h)
    h.js('a3.commandController.doCommand("cmd_expandAllThreads");')
    time.sleep(1)

    hover_ok = {}
    h.m.set_window_rect(width=WIDTH, height=LIST_HEIGHT)
    time.sleep(1)
    for mode in ("light", "dark"):
        set_mode(h, mode)
        set_view(h, CARDS)
        h.js("a3.threadTree.selectedIndex = -1;")
        h.shot(out, f"list-cards-{mode}")
        select(h, "m03@example.com")
        hover_ok[mode] = hover(h, "m05@example.com")
        time.sleep(0.5)
        h.shot(out, f"list-cards-selected-{mode}")
        set_view(h, TABLE)
        h.js("a3.threadTree.selectedIndex = -1;")
        h.shot(out, f"list-table-{mode}")
        select(h, "m16@example.org")
        h.js("a3.threadTree.table.body.focus();")
        time.sleep(0.5)
        h.shot(out, f"list-table-tagged-{mode}")
        set_view(h, CARDS)
    print(f"tb_shots: hover driven: {hover_ok}")
    h.m.set_window_rect(width=WIDTH, height=HEIGHT)
    time.sleep(1)

    for mode in ("light", "dark"):
        set_mode(h, mode)
        for case, message_id in READER_CASES.items():
            select(h, message_id)
            h.shot(out, f"reader-{case}-{mode}")

    # The dark system with the reader toggled off shows a white body.
    set_mode(h, "dark")
    h.js('Services.prefs.setBoolPref("mail.dark-reader.enabled", false);')
    select(h, "m03@example.com")
    select(h, READER_CASES["plain"])
    h.shot(out, "reader-plain-dark-reader-off")
    h.js('Services.prefs.clearUserPref("mail.dark-reader.enabled");')

    for note in h.notes:
        print(f"tb_shots: NOTE {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
