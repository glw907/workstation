#!/usr/bin/env python3
"""Measure Nord accents on the Thunderbird theme backgrounds (WCAG 2, APCA, OKLab, CVD)."""

import itertools
import math
import sys

# Palette: https://www.nordtheme.com/docs/colors-and-palettes
NORD = {
    "nord0": "#2e3440", "nord1": "#3b4252", "nord2": "#434c5e", "nord3": "#4c566a",
    "nord4": "#d8dee9", "nord5": "#e5e9f0", "nord6": "#eceff4",
    "nord7": "#8fbcbb", "nord8": "#88c0d0", "nord9": "#81a1c1", "nord10": "#5e81ac",
    "nord11": "#bf616a", "nord12": "#d08770", "nord13": "#ebcb8b",
    "nord14": "#a3be8c", "nord15": "#b48ead",
}
# Port-introduced brightened comment grey (nordtheme/vim colors/nord.vim line 19), not an official swatch.
NORD3_BRIGHT = "#616e88"
CANDIDATES = ["nord3", "nord3b", "nord4", "nord7", "nord8", "nord9", "nord10",
              "nord11", "nord12", "nord13", "nord14", "nord15"]
FROST_AURORA = ["nord7", "nord8", "nord9", "nord10", "nord11", "nord12", "nord13", "nord14", "nord15"]
OKABE_ITO = {"orange": "#e69f00", "skyblue": "#56b4e9", "bluishgreen": "#009e73", "yellow": "#f0e442",
             "blue": "#0072b2", "vermillion": "#d55e00", "reddishpurple": "#cc79a7", "black": "#000000"}

DARK_BG = {"window #222226": (0x22, 0x22, 0x26), "list #1e1e1e": (0x1e, 0x1e, 0x1e),
           "sidebar #28282c": (0x28, 0x28, 0x2c), "sidebar2 #2e2e32": (0x2e, 0x2e, 0x32)}
LIGHT_BG = {"window #fafafb": (0xfa, 0xfa, 0xfb), "list #ffffff": (0xff, 0xff, 0xff),
            "sidebar #ebebed": (0xeb, 0xeb, 0xed), "sidebar2 #f2f2f4": (0xf2, 0xf2, 0xf4)}

# Machado, Oliveira, Fernandes 2009, Table 1, severity 1.0 (applied to linear sRGB).
CVD = {
    "deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "tritanopia": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}

KEY_PAIRS = [("nord11", "nord14"), ("nord12", "nord13"), ("nord8", "nord9"), ("nord9", "nord10"),
             ("nord8", "nord10"), ("nord10", "nord15"), ("nord11", "nord12"), ("nord13", "nord14"),
             ("nord11", "nord15"), ("nord7", "nord14"), ("nord12", "nord14"), ("nord7", "nord8")]


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(rgb)


def get(name):
    if name == "nord3b":
        return NORD3_BRIGHT
    return NORD[name]


def to_lin(c):
    """Decode one 0-255 sRGB channel with the piecewise IEC 61966-2-1 curve."""
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def from_lin(v):
    v = min(1.0, max(0.0, v))
    c = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
    return c * 255.0


def wcag_lum(rgb):
    r, g, b = (to_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag_ratio(fg, bg):
    a, b = wcag_lum(fg), wcag_lum(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


# APCA 0.0.98G-4g constants from Myndex/apca-w3 src/apca-w3.js lines 143-172.
def apca_y(rgb):
    return 0.2126729 * (rgb[0] / 255) ** 2.4 + 0.7151522 * (rgb[1] / 255) ** 2.4 + 0.0721750 * (rgb[2] / 255) ** 2.4


def apca_lc(txt, bg):
    """Return signed APCA Lc (negative for light text on dark), matching apca-w3 APCAcontrast."""
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


def composite(fg_rgb, alpha, bg_rgb):
    return tuple(round(f * alpha + b * (1 - alpha)) for f, b in zip(fg_rgb, bg_rgb))


# OKLab per Ottosson, bottosson.github.io/posts/oklab (linear sRGB in code form, 2021-01-25 matrices).
def lin_to_oklab(r, g, b):
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


def oklab_to_lin(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def rgb_to_oklab(rgb):
    return lin_to_oklab(*(to_lin(c) for c in rgb))


def oklab_to_rgb_clip(lab):
    """Convert to 8-bit sRGB by per-channel clipping; also report whether clipping occurred."""
    lin = oklab_to_lin(*lab)
    out_of_gamut = any(v < -1e-6 or v > 1 + 1e-6 for v in lin)
    return tuple(round(from_lin(v)) for v in lin), out_of_gamut


def oklab_to_oklch(lab):
    L, a, b = lab
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def oklch_to_oklab(L, C, h):
    return L, C * math.cos(math.radians(h)), C * math.sin(math.radians(h))


def de_ok(l1, l2):
    return math.dist(l1, l2)


def gamut_map(lab):
    """CSS Color 4 14.2.1 binary-search chroma reduction with local MINDE (JND 0.02, epsilon 0.0001)."""
    L, C, h = oklab_to_oklch(lab)
    if L >= 1:
        return (255, 255, 255)
    if L <= 0:
        return (0, 0, 0)
    rgb, oog = oklab_to_rgb_clip(lab)
    if not oog:
        return rgb
    lo, hi, lo_in = 0.0, C, True
    clipped = rgb
    while hi - lo > 0.0001:
        c = (lo + hi) / 2
        cur = oklch_to_oklab(L, c, h)
        clipped, oog = oklab_to_rgb_clip(cur)
        if lo_in and not oog:
            lo = c
            continue
        # compare against the unrounded clip so 8-bit rounding does not distort the JND test
        clip_lin = tuple(min(1.0, max(0.0, v)) for v in oklab_to_lin(*cur))
        e = de_ok(lin_to_oklab(*clip_lin), cur)
        if e < 0.02:
            if 0.02 - e < 0.0001:
                return clipped
            lo_in = False
            lo = c
        else:
            hi = c
    return clipped


def adjust(rgb, mode, how="clip"):
    """Apply the theme rule oklab(from C max(l,0.85) a b) in dark or min(l,0.5) in light."""
    L, a, b = rgb_to_oklab(rgb)
    L2 = max(L, 0.85) if mode == "dark" else min(L, 0.5)
    lab = (L2, a, b)
    clip, oog = oklab_to_rgb_clip(lab)
    return (clip if how == "clip" else gamut_map(lab)), oog, lab


# CIEDE2000, Sharma, Wu, Dalal 2005; Lab from D65 XYZ.
def rgb_to_lab(rgb):
    r, g, b = (to_lin(c) for c in rgb)
    x = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
    xn, yn, zn = 0.95047, 1.0, 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def de2000(lab1, lab2):
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    c1, c2 = math.hypot(a1, b1), math.hypot(a2, b2)
    cb = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(cb ** 7 / (cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    C1, C2 = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1 = math.degrees(math.atan2(b1, a1p)) % 360 if C1 else 0.0
    h2 = math.degrees(math.atan2(b2, a2p)) % 360 if C2 else 0.0
    dL, dC = L2 - L1, C2 - C1
    if C1 * C2 == 0:
        dh = 0.0
    else:
        dh = h2 - h1
        dh = dh - 360 if dh > 180 else dh + 360 if dh < -180 else dh
    dH = 2 * math.sqrt(C1 * C2) * math.sin(math.radians(dh / 2))
    Lb, Cb = (L1 + L2) / 2, (C1 + C2) / 2
    if C1 * C2 == 0:
        hb = h1 + h2
    elif abs(h1 - h2) <= 180:
        hb = (h1 + h2) / 2
    else:
        hb = (h1 + h2 + 360) / 2 if h1 + h2 < 360 else (h1 + h2 - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hb - 30)) + 0.24 * math.cos(math.radians(2 * hb))
         + 0.32 * math.cos(math.radians(3 * hb + 6)) - 0.20 * math.cos(math.radians(4 * hb - 63)))
    dth = 30 * math.exp(-(((hb - 275) / 25) ** 2))
    rc = 2 * math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7))
    sl = 1 + 0.015 * (Lb - 50) ** 2 / math.sqrt(20 + (Lb - 50) ** 2)
    sc, sh = 1 + 0.045 * Cb, 1 + 0.015 * Cb * T
    rt = -math.sin(math.radians(2 * dth)) * rc
    return math.sqrt((dL / sl) ** 2 + (dC / sc) ** 2 + (dH / sh) ** 2 + rt * (dC / sc) * (dH / sh))


def simulate(rgb, kind):
    lin = [to_lin(c) for c in rgb]
    m = CVD[kind]
    out = [sum(m[i][j] * lin[j] for j in range(3)) for i in range(3)]
    return tuple(round(from_lin(v)) for v in out)


def self_test():
    assert abs(wcag_ratio((0, 0, 0), (255, 255, 255)) - 21) < 1e-9
    assert abs(apca_lc((0, 0, 0), (255, 255, 255)) - 106.04) < 0.05, apca_lc((0, 0, 0), (255, 255, 255))
    assert abs(apca_lc((255, 255, 255), (0, 0, 0)) + 107.88) < 0.05, apca_lc((255, 255, 255), (0, 0, 0))
    L, a, b = rgb_to_oklab((255, 0, 0))
    assert abs(L - 0.62796) < 1e-4 and abs(a - 0.22486) < 1e-4 and abs(b - 0.12585) < 1e-4, (L, a, b)
    L, a, b = rgb_to_oklab((255, 255, 255))
    assert abs(L - 1) < 1e-4 and abs(a) < 1e-3 and abs(b) < 1e-3
    for l1, l2, want in [((50, 2.6772, -79.7751), (50, 0, -82.7485), 2.0425),
                         ((50, 3.1571, -77.2803), (50, 0, -82.7485), 2.8615),
                         ((50, 2.5, 0), (50, 0, -2.5), 4.3065),
                         ((50, 2.5, 0), (73, 25, -18), 27.1492),
                         ((60.2574, -34.0099, 36.2677), (60.4626, -34.1751, 39.4387), 1.2644)]:
        assert abs(de2000(l1, l2) - want) < 1e-4, (l1, l2, de2000(l1, l2), want)


def fmt_pass(v, thr):
    return "Y" if v >= thr else "n"


def contrast_tables(mode, bgs):
    """Print WCAG/APCA tables for raw and adjusted colours against every background in this mode."""
    names = list(bgs)
    rows = []
    for n in CANDIDATES:
        raw = hex_to_rgb(get(n))
        adj_c, oog, lab = adjust(raw, mode, "clip")
        adj_m = gamut_map(lab)
        rows.append((n, raw, adj_c, adj_m, oog))
    for label, idx in [("RAW", 1), ("ADJUSTED (clip)", 2), ("ADJUSTED (gamut-map)", 3)]:
        if label == "ADJUSTED (gamut-map)" and not any(r[4] for r in rows):
            continue
        print(f"\n#### {mode} mode, {label}: WCAG 2 ratio (R) and APCA |Lc| per background\n")
        print("| colour | hex | " + " | ".join(f"R {b}" for b in names) + " | " + " | ".join(f"Lc {b}" for b in names) + " |")
        print("|---|---|" + "---|" * (2 * len(names)))
        for r in rows:
            rgb = r[idx]
            if label == "ADJUSTED (gamut-map)" and not r[4]:
                continue
            cells_r = " | ".join(f"{wcag_ratio(rgb, bgs[b]):.2f}" for b in names)
            cells_l = " | ".join(f"{abs(apca_lc(rgb, bgs[b])):.1f}" for b in names)
            print(f"| {r[0]} | {rgb_to_hex(rgb)} | {cells_r} | {cells_l} |")
    print(f"\n#### {mode} mode: worst-case (minimum over all four backgrounds) and thresholds\n")
    print("| colour | variant | hex | min R | min |Lc| | R>=4.5 | R>=3 | Lc>=60 | Lc>=75 | OKLab L raw->adj | out of sRGB gamut |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        for var, rgb in [("raw", r[1]), ("adj-clip", r[2])] + ([("adj-map", r[3])] if r[4] else []):
            mr = min(wcag_ratio(rgb, bgs[b]) for b in names)
            ml = min(abs(apca_lc(rgb, bgs[b])) for b in names)
            lraw = rgb_to_oklab(r[1])[0]
            ladj = rgb_to_oklab(rgb)[0]
            print(f"| {r[0]} | {var} | {rgb_to_hex(rgb)} | {mr:.2f} | {ml:.1f} | {fmt_pass(mr, 4.5)} | {fmt_pass(mr, 3)} | "
                  f"{fmt_pass(ml, 60)} | {fmt_pass(ml, 75)} | {lraw:.3f}->{ladj:.3f} | {'yes' if r[4] else 'no'} |")


def main():
    self_test()
    print("self-tests passed (WCAG 21:1, APCA +106.04/-107.88, OKLab red/white, CIEDE2000 Sharma vectors)")
    card = composite((255, 255, 255), 0.08, (0x1e, 0x1e, 0x1e))
    dark_bg = dict(DARK_BG)
    dark_bg[f"card {rgb_to_hex(card)}"] = card
    print(f"\ncard rgba(255,255,255,0.08) over #1e1e1e = {rgb_to_hex(card)}")

    print("\n### 1. Palette in OKLCH (L, C, h) and CIELAB L*\n")
    print("| colour | hex | OKLab L | C | h | CIELAB L* |")
    print("|---|---|---|---|---|---|")
    for n in ["nord0", "nord1", "nord2", "nord3", "nord3b", "nord4", "nord5", "nord6"] + FROST_AURORA:
        rgb = hex_to_rgb(get(n))
        L, C, h = oklab_to_oklch(rgb_to_oklab(rgb))
        print(f"| {n} | {get(n)} | {L:.3f} | {C:.3f} | {h:.1f} | {rgb_to_lab(rgb)[0]:.1f} |")

    print("\n### 2. Main-text baselines\n")
    print("| mode | text | background | R | |Lc| |")
    print("|---|---|---|---|---|")
    for b, bg in dark_bg.items():
        print(f"| dark | #ffffff | {b} | {wcag_ratio((255,255,255), bg):.2f} | {abs(apca_lc((255,255,255), bg)):.1f} |")
    for b, bg in LIGHT_BG.items():
        t = composite((0, 0, 6), 0.8, bg)
        print(f"| light | rgba(0,0,6,0.8) -> {rgb_to_hex(t)} | {b} | {wcag_ratio(t, bg):.2f} | {abs(apca_lc(t, bg)):.1f} |")

    print("\n### 3. Contrast tables")
    contrast_tables("dark", dark_bg)
    contrast_tables("light", LIGHT_BG)

    print("\n### 4. Adjustment detail (OKLab, hue and chroma held, L moved)\n")
    print("| colour | mode | L raw | L adj | C | h | ideal out of gamut | clip hex | clip dE_OK from ideal | gamut-map hex |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for mode in ("dark", "light"):
        for n in CANDIDATES:
            raw = hex_to_rgb(get(n))
            clip, oog, lab = adjust(raw, mode, "clip")
            ideal_lin = oklab_to_lin(*lab)
            clip_lab = lin_to_oklab(*(min(1, max(0, v)) for v in ideal_lin))
            L0, C0, h0 = oklab_to_oklch(rgb_to_oklab(raw))
            print(f"| {n} | {mode} | {L0:.3f} | {lab[0]:.3f} | {C0:.3f} | {h0:.1f} | {'yes' if oog else 'no'} | "
                  f"{rgb_to_hex(clip)} | {de_ok(lab, clip_lab):.3f} | {rgb_to_hex(gamut_map(lab))} |")

    print("\n### 5. CVD simulation (Machado 2009, severity 1.0, linear sRGB)\n")
    sets = {"raw": lambda rgb: rgb,
            "dark-adjusted (clip)": lambda rgb: adjust(rgb, "dark")[0],
            "light-adjusted (clip)": lambda rgb: adjust(rgb, "light")[0]}
    for sname, fn in sets.items():
        print(f"\n#### Simulated swatches, {sname}\n")
        print("| colour | normal | deuteranopia | protanopia | tritanopia |")
        print("|---|---|---|---|---|")
        for n in FROST_AURORA:
            base = fn(hex_to_rgb(get(n)))
            print(f"| {n} | {rgb_to_hex(base)} | " + " | ".join(rgb_to_hex(simulate(base, k)) for k in CVD) + " |")

    def dist(rgb_a, rgb_b, kind):
        if kind != "normal":
            rgb_a, rgb_b = simulate(rgb_a, kind), simulate(rgb_b, kind)
        return de2000(rgb_to_lab(rgb_a), rgb_to_lab(rgb_b)), de_ok(rgb_to_oklab(rgb_a), rgb_to_oklab(rgb_b))

    kinds = ["normal"] + list(CVD)
    for sname, fn in sets.items():
        print(f"\n#### Key pairs, {sname}: dE2000 / dE_OK / dL_OK (normal vision L difference in OKLab)\n")
        print("| pair | normal dE00 | deut dE00 | prot dE00 | trit dE00 | normal dE_OK | deut dE_OK | prot dE_OK | trit dE_OK | dL_OK normal | dL_OK deut | dL_OK prot |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for a, b in KEY_PAIRS:
            ra, rb = fn(hex_to_rgb(get(a))), fn(hex_to_rgb(get(b)))
            d = {k: dist(ra, rb, k) for k in kinds}
            dl = [abs(rgb_to_oklab(ra)[0] - rgb_to_oklab(rb)[0])] + [
                abs(rgb_to_oklab(simulate(ra, k))[0] - rgb_to_oklab(simulate(rb, k))[0]) for k in ("deuteranopia", "protanopia")]
            print(f"| {a} vs {b} | " + " | ".join(f"{d[k][0]:.1f}" for k in kinds) + " | "
                  + " | ".join(f"{d[k][1]:.3f}" for k in kinds) + " | " + " | ".join(f"{x:.3f}" for x in dl) + " |")

    print("\n#### Closest pairs among the 9 Frost+Aurora colours (all 36 pairs), by dE2000\n")
    for sname, fn in sets.items():
        for k in kinds:
            ranked = sorted(((dist(fn(hex_to_rgb(get(a))), fn(hex_to_rgb(get(b))), k), a, b)
                             for a, b in itertools.combinations(FROST_AURORA, 2)), key=lambda t: t[0][0])
            print(f"- {sname}, {k}: " + "; ".join(f"{a}-{b} {d[0]:.1f} (OK {d[1]:.3f})" for d, a, b in ranked[:6]))

    print("\n#### Pair matrices: dE2000 in normal vision (upper right) and worst case over the three CVD types (lower left)\n")
    for sname, fn in sets.items():
        print(f"\n{sname}\n")
        print("| | " + " | ".join(n.replace("nord", "n") for n in FROST_AURORA) + " |")
        print("|---|" + "---|" * len(FROST_AURORA))
        for i, a in enumerate(FROST_AURORA):
            cells = []
            for j, b in enumerate(FROST_AURORA):
                ra, rb = fn(hex_to_rgb(get(a))), fn(hex_to_rgb(get(b)))
                if i == j:
                    cells.append("-")
                elif j > i:
                    cells.append(f"{dist(ra, rb, 'normal')[0]:.1f}")
                else:
                    cells.append(f"{min(dist(ra, rb, k)[0] for k in CVD):.1f}")
            print(f"| {a.replace('nord', 'n')} | " + " | ".join(cells) + " |")

    print("\n### 6. Reference: raw Nord accents on Nord's own backgrounds (dark nord0, bright nord6)\n")
    print("| colour | hex | R on nord0 | |Lc| on nord0 | R on nord6 | |Lc| on nord6 |")
    print("|---|---|---|---|---|---|")
    n0, n6 = hex_to_rgb(NORD["nord0"]), hex_to_rgb(NORD["nord6"])
    for n in CANDIDATES:
        rgb = hex_to_rgb(get(n))
        print(f"| {n} | {get(n)} | {wcag_ratio(rgb, n0):.2f} | {abs(apca_lc(rgb, n0)):.1f} | "
              f"{wcag_ratio(rgb, n6):.2f} | {abs(apca_lc(rgb, n6)):.1f} |")

    print("\n#### Benchmark: Okabe-Ito palette minimum pair distance in the same pipeline (excluding black)\n")
    oi = {n: hex_to_rgb(h) for n, h in OKABE_ITO.items() if n != "black"}
    for k in kinds:
        ranked = sorted(((dist(oi[a], oi[b], k), a, b) for a, b in itertools.combinations(oi, 2)), key=lambda t: t[0][0])
        print(f"- {k}: " + "; ".join(f"{a}-{b} {d[0]:.1f} (OK {d[1]:.3f})" for d, a, b in ranked[:3]))
    nm = {n: hex_to_rgb(get(n)) for n in FROST_AURORA}
    print("\nNord Frost+Aurora raw, minimum pair per vision type for comparison:")
    for k in kinds:
        ranked = sorted(((dist(nm[a], nm[b], k), a, b) for a, b in itertools.combinations(nm, 2)), key=lambda t: t[0][0])
        print(f"- {k}: " + "; ".join(f"{a}-{b} {d[0]:.1f} (OK {d[1]:.3f})" for d, a, b in ranked[:3]))


if __name__ == "__main__":
    sys.exit(main())
