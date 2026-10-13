#!/usr/bin/env python3
"""Prove every Nord mail role meets its contrast threshold on every background it lands on.

Reads the palette and the roles from thunderbird/nord.css (or the file --css names), resolves
each role the way Thunderbird will paint it in light and dark mode, and measures it with the
WCAG 2.2 ratio (the gate) and APCA Lc (printed, never gated). The OKLab, WCAG and APCA code is
ported from the research script nord_measure.py.

Exit status: 0 when every gated pair passes, 1 when any prints FAIL, 2 when the CSS file is
missing or a role line cannot be read.
"""

import argparse
import math
import re
import sys
from pathlib import Path

DEFAULT_CSS = Path(__file__).resolve().parent.parent / "nord.css"

TEXT_MIN = 4.5
NON_TEXT_MIN = 3.0

NORD_NAMES = [f"nord{i}" for i in range(16)]

TEXT_ROLES = ["mail-tag-1", "mail-tag-2", "mail-tag-3", "mail-tag-4", "mail-tag-5"]
LIST_NON_TEXT_ROLES = ["mail-accent", "mail-attention", "mail-error", "mail-success"]
HEADER_ROLES = ["mail-attention"] + TEXT_ROLES
REQUIRED_ROLES = (
    ["mail-accent-fill", "mail-accent", "mail-attention", "mail-error", "mail-success"]
    + TEXT_ROLES
    + ["mail-body-accent", "mail-quote-2", "mail-quote-3"]
)

# Theme surfaces: the list paints --gnome-secondary-sidebar-background (light.css:82, :161;
# dark.css:23, :55) and the header paints --gnome-window-background (light.css:74, dark.css:19).
LIST_SURFACES = {
    "light": [("#f3f3f5", (0xF3, 0xF3, 0xF5)), ("#f6f6fa", (0xF6, 0xF6, 0xFA))],
    "dark": [("#28282c", (0x28, 0x28, 0x2C)), ("#252529", (0x25, 0x25, 0x29))],
}
HEADER_SURFACE = {"light": ("#fafafb", (0xFA, 0xFA, 0xFB)), "dark": ("#222226", (0x22, 0x22, 0x26))}

# The theme's hover and selected tints are currentColor at 7% and 10% (light.css:109-111).
HOVER_ALPHA = 0.07
SELECTED_ALPHA = 0.10

# Message bodies: Thunderbird darkens a body only for a dark system with the dark reader on.
# Each entry is (label, body background, which form of the body rule applies).
BODIES = [
    ("light system", (0xFF, 0xFF, 0xFF), "light"),
    ("dark system, reader on", (0x18, 0x18, 0x1B), "dark"),
    ("dark system, reader off", (0xFF, 0xFF, 0xFF), "light"),
]

WHITE = (255, 255, 255)


class CssError(Exception):
    """Raise when nord.css is missing or a role line is not in a form the check reads."""


def hex_to_rgb(h):
    """Convert a #rrggbb string to an 8-bit RGB tuple."""
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """Format an 8-bit RGB tuple as #rrggbb."""
    return "#%02x%02x%02x" % tuple(rgb)


def to_lin(c):
    """Decode one 0-255 sRGB channel with the piecewise IEC 61966-2-1 curve."""
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def from_lin(v):
    """Encode one linear channel to 0-255 sRGB, clipping to the gamut."""
    v = min(1.0, max(0.0, v))
    c = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
    return c * 255.0


def wcag_ratio(fg, bg):
    """Return the WCAG 2.2 contrast ratio of two RGB tuples."""
    def lum(rgb):
        r, g, b = (to_lin(c) for c in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    a, b = lum(fg), lum(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def apca_y(rgb):
    """Return APCA screen luminance (0.0.98G-4g constants, Myndex apca-w3.js:143-172)."""
    return (0.2126729 * (rgb[0] / 255) ** 2.4 + 0.7151522 * (rgb[1] / 255) ** 2.4
            + 0.0721750 * (rgb[2] / 255) ** 2.4)


def apca_lc(txt, bg):
    """Return signed APCA Lc, negative for light text on a dark background."""
    ty, by = apca_y(txt), apca_y(bg)
    if ty <= 0.022:
        ty += (0.022 - ty) ** 1.414
    if by <= 0.022:
        by += (0.022 - by) ** 1.414
    if abs(by - ty) < 0.0005:
        return 0.0
    if by > ty:
        s = (by ** 0.56 - ty ** 0.57) * 1.14
        out = 0.0 if s < 0.1 else s - 0.027
    else:
        s = (by ** 0.65 - ty ** 0.62) * 1.14
        out = 0.0 if s > -0.1 else s + 0.027
    return out * 100.0


def rgb_to_oklab(rgb):
    """Convert an 8-bit sRGB tuple to OKLab (Ottosson, bottosson.github.io/posts/oklab)."""
    r, g, b = (to_lin(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


def oklab_to_rgb(lab):
    """Convert OKLab to 8-bit sRGB by per-channel clipping, as the browser does at paint."""
    big_l, a, b = lab
    l_ = big_l + 0.3963377774 * a + 0.2158037573 * b
    m_ = big_l - 0.1055613458 * a - 0.0638541728 * b
    s_ = big_l - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    lin = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    return tuple(round(from_lin(v)) for v in lin)


def composite(fg, alpha, bg):
    """Paint fg at the given alpha over an opaque bg."""
    return tuple(round(f * alpha + b * (1 - alpha)) for f, b in zip(fg, bg))


def adjust(rgb, rule):
    """Apply a lightness rule ((op, value) with op max or min) to a colour, keeping hue and chroma."""
    op, value = rule
    lightness, a, b = rgb_to_oklab(rgb)
    lightness = max(lightness, value) if op == "max" else min(lightness, value)
    return oklab_to_rgb((lightness, a, b))


def self_test():
    """Assert the ported colour maths against known values."""
    assert abs(wcag_ratio((0, 0, 0), WHITE) - 21) < 1e-9
    assert abs(apca_lc((0, 0, 0), WHITE) - 106.04) < 0.05, apca_lc((0, 0, 0), WHITE)
    assert abs(apca_lc(WHITE, (0, 0, 0)) + 107.88) < 0.05, apca_lc(WHITE, (0, 0, 0))
    big_l, a, b = rgb_to_oklab((255, 0, 0))
    assert abs(big_l - 0.62796) < 1e-4 and abs(a - 0.22486) < 1e-4 and abs(b - 0.12585) < 1e-4
    big_l, a, b = rgb_to_oklab(WHITE)
    assert abs(big_l - 1) < 1e-4 and abs(a) < 1e-3 and abs(b) < 1e-3
    for rgb in [(0x88, 0xC0, 0xD0), (0x5E, 0x81, 0xAC), (0x2E, 0x34, 0x40)]:
        assert oklab_to_rgb(rgb_to_oklab(rgb)) == rgb, rgb
    assert composite((0, 0, 0), 0.5, WHITE) == (128, 128, 128)


def strip_comments(text):
    """Remove CSS block comments."""
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def parse_css(path):
    """Parse nord.css into the palette, the two lightness rules and the role specs.

    Raises CssError when the file is missing or a line is not in a form this check reads.
    """
    try:
        text = strip_comments(Path(path).read_text())
    except OSError as err:
        raise CssError(f"cannot read {path}: {err.strerror}") from err

    palette = {}
    for name in NORD_NAMES:
        m = re.search(rf"--{name}:\s*(#[0-9a-fA-F]{{6}})\s*;", text)
        if not m:
            raise CssError(f"--{name} is missing or not a #rrggbb value")
        palette[name] = hex_to_rgb(m.group(1))

    rules = {}
    for kind in ("text", "body"):
        found = re.findall(rf"--mail-oklab-{kind}:\s*(max|min)\(l,\s*([0-9.]+)\)\s*a\s+b\s*;", text)
        forms = {op: (op, float(val)) for op, val in found}
        if set(forms) != {"max", "min"}:
            raise CssError(f"--mail-oklab-{kind} needs one max(l, X) a b form and one min(l, X) a b form")
        rules[kind] = {"dark": forms["max"], "light": forms["min"]}

    roles = {}
    for name, value in re.findall(r"--(mail-(?!oklab-)[a-z0-9-]+):\s*([^;]+);", text):
        value = " ".join(value.split())
        m_raw = re.fullmatch(r"var\(--(nord\d+)\)", value)
        m_adj = re.fullmatch(r"oklab\(from var\(--(nord\d+)\) var\(--mail-oklab-(text|body)\)\)", value)
        m_mix = re.fullmatch(r"color-mix\(in srgb, var\(--(mail-[a-z0-9-]+)\) (\d+)%, transparent\)", value)
        if m_raw and m_raw.group(1) in palette:
            roles[name] = ("raw", m_raw.group(1))
        elif m_adj and m_adj.group(1) in palette:
            roles[name] = (m_adj.group(2), m_adj.group(1))
        elif m_mix:
            roles[name] = ("mix", m_mix.group(1), int(m_mix.group(2)) / 100)
        else:
            raise CssError(f"cannot read the role line --{name}: {value}")
    for name in REQUIRED_ROLES:
        if name not in roles:
            raise CssError(f"role --{name} is missing")
    for name, spec in roles.items():
        if spec[0] == "mix" and spec[1] not in roles:
            raise CssError(f"--{name} mixes unknown role --{spec[1]}")
    return palette, rules, roles


def resolve(name, mode, form, palette, rules, roles):
    """Return (rgb, alpha) for a role.

    mode picks the text rule's form and form picks the body rule's form.
    """
    spec = roles[name]
    if spec[0] == "raw":
        return palette[spec[1]], 1.0
    if spec[0] in ("text", "body"):
        pick = mode if spec[0] == "text" else form
        return adjust(palette[spec[1]], rules[spec[0]][pick]), 1.0
    rgb, alpha = resolve(spec[1], mode, form, palette, rules, roles)
    return rgb, alpha * spec[2]


class Report:
    """Collect measured pairs, print them, and count gated failures."""

    def __init__(self):
        """Start with no rows and no failures."""
        self.failures = 0

    def row(self, mode, where, role, fg, bg, need):
        """Print one pair; a gated pair below its threshold prints FAIL and counts."""
        ratio = wcag_ratio(fg, bg)
        lc = abs(apca_lc(fg, bg))
        if need is None:
            verdict = "info"
        elif ratio >= need:
            verdict = "ok"
        else:
            verdict = "FAIL"
            self.failures += 1
        gate = "-" if need is None else f"{need:.1f}"
        print(f"{verdict:<5} {mode:<5} {where:<34} {role:<18} {rgb_to_hex(fg)} on {rgb_to_hex(bg)}"
              f"  {ratio:5.2f}:1 (need {gate})  Lc {lc:5.1f}")


def check(palette, rules, roles):
    """Measure every role on every background in both modes and return the failure count."""
    rep = Report()

    def res(name, mode, form=None):
        rgb, alpha = resolve(name, mode, form or mode, palette, rules, roles)
        return rgb, alpha

    print("== message list ==")
    for mode in ("light", "dark"):
        neutral = (0x00, 0x00, 0x06) if mode == "light" else WHITE
        neutral_text_alpha = 0.8 if mode == "light" else 1.0
        for sname, surface in LIST_SURFACES[mode]:
            where = f"list {sname}"
            hover_n = composite(neutral, HOVER_ALPHA, surface)
            selected_n = composite(neutral, SELECTED_ALPHA, surface)
            for role in LIST_NON_TEXT_ROLES:
                fg, _ = res(role, mode)
                for label, bg in (("", surface), (" +hover", hover_n), (" +selected", selected_n)):
                    rep.row(mode, where + label, role, fg, bg, NON_TEXT_MIN)
            for role in TEXT_ROLES:
                fg, _ = res(role, mode)
                for label, alpha in (("", 0.0), (" +hover", HOVER_ALPHA), (" +selected", SELECTED_ALPHA)):
                    bg = composite(fg, alpha, surface)
                    rep.row(mode, where + label, role, fg, bg, TEXT_MIN)
            text = composite(neutral, neutral_text_alpha, selected_n)
            rep.row(mode, where + " +selected", "neutral-text", text, selected_n, TEXT_MIN)

    print("== reader header ==")
    for mode in ("light", "dark"):
        sname, surface = HEADER_SURFACE[mode]
        for role in HEADER_ROLES:
            fg, _ = res(role, mode)
            rep.row(mode, f"header {sname}", role, fg, surface, NON_TEXT_MIN)

    print("== reader body ==")
    for label, body, form in BODIES:
        mode = "dark" if form == "dark" else "light"
        link, _ = res("mail-body-accent", mode, form)
        rep.row(mode, f"body {label}", "link text", link, body, TEXT_MIN)
        rep.row(mode, f"body {label}", "quote 1 bar", link, body, NON_TEXT_MIN)
        for role in ("mail-quote-2", "mail-quote-3"):
            fg, alpha = res(role, mode, form)
            rep.row(mode, f"body {label}", role, composite(fg, alpha, body), body, None)

    print("== accent fill ==")
    fill, _ = res("mail-accent-fill", "light")
    rep.row("any", "fill with white text", "mail-accent-fill", WHITE, fill, None)
    return rep.failures


def main(argv=None):
    """Run the self-test or the contrast check and return the exit status."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--css", default=str(DEFAULT_CSS), help="palette file to check (default: thunderbird/nord.css)")
    parser.add_argument("--self-test", action="store_true", help="check the colour maths and exit")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        print("self-test ok (WCAG 21:1, APCA +106.04/-107.88, OKLab red, white and round trips)")
        return 0
    self_test()
    try:
        palette, rules, roles = parse_css(args.css)
    except CssError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    failures = check(palette, rules, roles)
    if failures:
        print(f"{failures} gated pair(s) FAIL")
        return 1
    print("every gated pair passes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
