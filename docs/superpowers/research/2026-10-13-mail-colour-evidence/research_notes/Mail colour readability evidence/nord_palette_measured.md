# Nord palette measured as accent colours on the Thunderbird GNOME-theme backgrounds, and how Nord ports assign roles

Research date 2026-10-13. Everything numeric below was produced by `nord_measure.py` (saved next to these notes, full text reproduced at the end of Question 2). Conventions: ratios to two decimals, APCA Lc to one decimal (absolute value shown; light-on-dark Lc is negative in the reference implementation). "adj" means the theme rule `oklab(from C max(l, 0.85) a b)` in dark mode or `oklab(from C min(l, 0.5) a b)` in light mode. "nord3b" (marked `*` in tables) is `#616e88`, a port-introduced brightened comment grey that is not an official swatch (Question 4).

## 1. What are nord0-nord15 and what roles does the official Nord documentation assign?

### Takeaway
The 16 colours are fixed hex values in four groups, and the official "Colors and Palettes" page gives Frost and Aurora fixed, mode-independent roles: nord8 is the primary accent, nord9 secondary, nord10 tertiary, nord11 error, nord13 warning, nord14 success, with nord12 and nord15 "rarely used" for UI. The page defines no explicit "link" role and no email guidance, and it says Frost and Aurora are "used the same for both dark & bright ambiance designs", which is the opposite of the lightness-adjusting rule the Thunderbird theme applies.

### Cited Findings
- The official page is a "living document" ("work in progress ... can change at any time"), version footer v0.23.0, and its guidelines are described as "soft" recommendations that "may be used in a modified form" — [Nord docs: Colors and Palettes](https://www.nordtheme.com/docs/colors-and-palettes)
- Group descriptions (verbatim fragments): Polar Night is "four darker colors that are commonly used for base elements like backgrounds or text color in bright ambiance designs"; Snow Storm is "three bright colors that are commonly used for text colors or base UI elements in bright ambiance designs"; Frost is "the heart palette of Nord, a group of four bluish colors that are commonly used for primary UI component and text highlighting and essential code syntax elements"; Aurora is "five colorful components reminiscent of the Aurora borealis" — [Nord docs: Colors and Palettes](https://www.nordtheme.com/docs/colors-and-palettes)
- "All colors of this palette are used the same for both dark & bright ambiance designs" is stated for both Frost and Aurora. Polar Night and Snow Storm roles swap between dark and bright ambiance — [Nord docs: Colors and Palettes](https://www.nordtheme.com/docs/colors-and-palettes)
- Hex values and roles, transcribed from the page text (UI role first, syntax role second; "dark"/"bright" = dark/bright ambiance design):

| colour | hex | group | official role (condensed from the page) |
|---|---|---|---|
| nord0 | #2e3440 | Polar Night | Dark: background and area colouring (not used for syntax). Bright: plain text, caret, reserved characters such as brackets. Rarely used for passive UI like borders. |
| nord1 | #3b4252 | Polar Night | Dark: elevated, prominent or focused UI (status bars, gutters, panels, modals, popups, buttons, text/select fields, checkboxes), also borders and drop shadows. Bright: more subtle UI text that needs little attention; also hover/active/focus text states. |
| nord2 | #434c5e | Polar Night | Dark: active editor line, selection and text highlight. Both: a brighter variant for nord1's targets. |
| nord3 | #4c566a | Polar Night | Dark: indent and wrap guide markers; syntax: comments and invisible characters. Bright: with nord1/nord2 as darker variants, "the most subtle/inconspicuous UI text elements that do not need so much visual attention". |
| nord4 | #d8dee9 | Snow Storm | Dark: caret; syntax: variables, constants, attributes, fields. Bright: elevated/prominent UI backgrounds (status bars, panels, form components) and borders. |
| nord5 | #e5e9f0 | Snow Storm | Dark: subtle UI text, hover/active/focus text. Bright: active line, selection and highlight. |
| nord6 | #eceff4 | Snow Storm | Dark: elevated UI text needing more attention; syntax: plain text and brackets. Bright: background and area colouring. |
| nord7 | #8fbcbb | Frost | "A calm and highly contrasted color reminiscent of frozen polar water." UI elements that should "next to the primary accent color nord8, stand out and get more visual attention". Syntax: classes, types, primitives. |
| nord8 | #88c0d0 | Frost | "The bright and shiny primary accent color." Primary UI elements with main usage purposes that "require the most visual attention". Syntax: declarations, calls and execution statements of functions, methods, routines. |
| nord9 | #81a1c1 | Frost | "More darkened and less saturated." Secondary UI elements that "also require more visual attention than other elements". Syntax: reserved keywords, operators, tags, units, punctuation. |
| nord10 | #5e81ac | Frost | "A dark and intensive color." Tertiary UI elements requiring more attention than default elements. Syntax: pragmas, comment keywords, pre-processor statements. |
| nord11 | #bf616a | Aurora | UI elements "rendering error states like linter markers and the highlighting of Git diff deletions". Syntax: overrides highlighting of elements detected as errors. |
| nord12 | #d08770 | Aurora | "Rarely used for UI elements, but it may indicate a more advanced or dangerous functionality." Syntax: annotations and decorators. |
| nord13 | #ebcb8b | Aurora | UI elements "rendering warning states like linter markers and the highlighting of Git diff modifications". Syntax: warning overrides, escape characters, regular expressions. |
| nord14 | #a3be8c | Aurora | UI elements "rendering success states and visualizations and the highlighting of Git diff additions". Syntax: strings. |
| nord15 | #b48ead | Aurora | "Rarely used for UI elements, but it may indicate a more uncommon functionality." Syntax: numbers. |

  Source for the whole table: [Nord docs: Colors and Palettes](https://www.nordtheme.com/docs/colors-and-palettes) (page fetched as raw HTML and stripped, not via a summariser; hex values match [nord.vim lines 15-31](https://github.com/nordtheme/vim/blob/main/colors/nord.vim#L15-L31) and [nord-theme.el lines 101-116](https://github.com/nordtheme/emacs/blob/main/nord-theme.el#L101-L116)).
- Snow Storm has two shading styles: "bright to dark" (recommended; nord6 base, highlights with nord5 and nord4) and "dark to bright" (semi-light; nord4 base) — [Nord docs: Colors and Palettes](https://www.nordtheme.com/docs/colors-and-palettes)
- nord0 text on a nord6 background is the page's bright-ambiance pairing; nord1, nord2, nord3 are the sanctioned darker "subtle text" tones in bright ambiance. Measured nord3 on nord6: ratio 6.40, Lc 76.0 (table in Question 2).
- An older documentation snapshot, quoted in code comments by Joplin's Nord theme ("DOCUMENTATION of Nord as of Oct 3"), says nord3 was "In the UI scope used as pseudoclass color for disabled elements" and nord13 "In the UI scope used for warnings and git/diff renamings"; the current page no longer says the disabled-element line — [Joplin themes/nord.ts lines 6-47](https://cdn.jsdelivr.net/npm/@joplin/lib@3.5.1/themes/nord.ts); compare the current page above
- Unrelated project warning: nordhealth.design is a different "Nord" (a healthcare design system with functional colour roles and a 4.5:1 text requirement); its guidance must not be mixed with the Arctic Ice Studio / nordtheme palette — [nordhealth.design colors](https://nordhealth.design/colors)

### Inferences
- The official roles are keyed to code editors and generic UI chrome: the closest thing to a "link/accent/primary" role is nord8 (primary accent, "most visual attention"), with nord9/nord10 as secondary/tertiary, but nothing says "link". A mail client mapping (unread, flagged, quoted, link) would be an extension of the docs, not a citation of them.
- The error/warning/success trio is the only Aurora semantic triple that is explicit and stable across the docs (nord11/nord13/nord14). nord12 and nord15 are explicitly the "rarely used" slots, so they are the natural free slots for decorative or low-priority categories.
- The docs treat Frost and Aurora as fixed colours independent of ambiance. The Thunderbird theme's OKLab rule overrides that by design (it moves every accent to L>=0.85 on dark or L<=0.5 on light), so Nord's own raw-colour guidance cannot be assumed to survive the adjustment (see Questions 2 and 3).

### Gaps
- No "link", "unread", "selected", "quoted text" or email-specific role exists on the official page; nothing found on nordtheme.com about mail clients.
- The docs index lists "Installation & Usage" but I found no separate nordtheme.com "usage / UI element guidance" page beyond this one; the "Syntax Highlighting" doc page was not fetched.
- The page lists hex only (no RGB/HSL); OKLCH values in this note are computed.

## 2. Contrast of each Nord accent on the actual backgrounds, raw and after the theme's OKLab adjustment

### Takeaway
Raw Nord accents are not safe as small text on the light backgrounds (only nord3 passes 4.5:1; nord10 and nord11 reach 3:1 but not 4.5:1) and nord10/nord11 also fail 4.5:1 on dark. After the theme's OKLab rule every accent passes 4.5:1 and APCA Lc 60 on every background in both modes, but none reaches Lc 75 on all backgrounds, and the rule flattens every accent to nearly the same lightness (dark L 0.83-0.86, light L 0.50), leaving hue and chroma as the only differences between colours.

### Cited Findings

#### Method and validation
- WCAG 2 contrast: relative luminance with the sRGB threshold 0.04045 (WCAG 2.2 notes that "Before May 2021 the value of 0.04045 in the definition was different (0.03928)" with "no practical effect"); ratio (L1+0.05)/(L2+0.05); thresholds 4.5:1 for text (SC 1.4.3) and 3:1 for UI components (SC 1.4.11) — [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- APCA: 0.0.98G-4g constants (mainTRC 2.4; sRco/sGco/sBco 0.2126729/0.7151522/0.0721750; normBG 0.56, normTXT 0.57, revTXT 0.62, revBG 0.65; blkThrs 0.022, blkClmp 1.414; scale 1.14; offsets 0.027; deltaYmin 0.0005; loClip 0.1) taken from the reference source — [Myndex/apca-w3 src/apca-w3.js lines 143-172 and 195-253](https://github.com/Myndex/apca-w3/blob/master/src/apca-w3.js). I cross-checked 7 text/background pairs against the reference JS run in Node (stubbing its colour-parser import); the Python values matched to two decimals (for example #8fbcbb on #222226 = -59.11, #ffffff on #2e2e32 = -103.15, #4c566a on #ebebed = 73.87). The script's self-test also reproduces black on white = 106.04 and white on black = -107.88.
- APCA threshold meanings used for the pass columns: "Lc 75: minimum level for columns of body text with a font no smaller than 18px/400"; "Lc 60: minimum level recommended for content text that is not body, column, or block text ... 24px normal weight (400) or 16px/700"; Lc 45 for large headlines; Lc 30 for placeholder/disabled text; Lc 15 for non-text — [sass-apca README (summarising the Myndex Bronze levels)](https://unpkg.com/sass-apca@1.2.0/README.md). A web search found the size floors disagree between sources (18px vs 16px for Lc 75), so treat sizes as unsettled, see Gaps.
- OKLab conversion uses Ottosson's published linear-sRGB code and 2021-01-25 matrices (`linear_srgb_to_oklab` / `oklab_to_linear_srgb`) — [Ottosson, A perceptual color space for image processing](https://bottosson.github.io/posts/oklab/). Script self-tests reproduce red = L 0.62796, a 0.22486, b 0.12585 and white = L 1.
- The theme rule is defined upstream as `--gnome-standalone-color-oklab: max(l, 0.85) a b;` (dark) and `min(l, 0.5) a b;` (light) — [thunderbird-gnome-theme colors/dark.css](https://github.com/rafaelmardojai/thunderbird-gnome-theme/blob/main/theme/colors/dark.css) and [colors/light.css](https://github.com/rafaelmardojai/thunderbird-gnome-theme/blob/main/theme/colors/light.css) (found via `gh search code`; the local `~/.dotfiles/thunderbird/customChrome.css` lines 108-117 apply it as `oklab(from <hex> var(--gnome-standalone-color-oklab))`). In CSS `l` is 0-1 so 0.85 means OKLab L 0.85. a and b are held, so OKLCH hue and chroma are preserved except where clipping to sRGB changes them.
- Out-of-gamut handling: the adjusted OKLab point can lie outside sRGB. I report two renderings, a per-channel clip and the CSS Color 4 section 14.2.1 binary-search chroma reduction with local MINDE (JND 0.02, epsilon 0.0001) — [CSS Color 4 14.2.1](https://www.w3.org/TR/css-color-4/#binsearch). Only nord10, nord11, nord12 in dark mode are out of gamut (none in light mode). Only nord11 differs materially between the two renderings. Which one Gecko applies to relative-colour `oklab()` was not verified (see Gaps). Tables below use the clip result unless stated.
- Colours are rounded to 8-bit sRGB before contrast is computed, because that is what is painted.

#### Backgrounds and baselines
Dark card = rgba(255,255,255,0.08) over #1e1e1e composited to `#303030`. Light main text rgba(0,0,6,0.8) composited per background (no light card background was supplied, so none was measured).

| mode | text | background | WCAG 2 ratio | APCA |Lc| |
|---|---|---|---|---|
| dark | #ffffff | window #222226 | 15.85 | 105.4 |
| dark | #ffffff | list #1e1e1e | 16.67 | 106.0 |
| dark | #ffffff | sidebar #28282c | 14.68 | 104.4 |
| dark | #ffffff | sidebar2 #2e2e32 | 13.52 | 103.1 |
| dark | #ffffff | card #303030 | 13.20 | 102.8 |
| light | rgba(0,0,6,0.8) = #323237 | window #fafafb | 12.22 | 95.9 |
| light | rgba(0,0,6,0.8) = #333338 | list #ffffff | 12.56 | 98.6 |
| light | rgba(0,0,6,0.8) = #2f2f34 | sidebar #ebebed | 11.18 | 88.0 |
| light | rgba(0,0,6,0.8) = #303036 | sidebar2 #f2f2f4 | 11.73 | 91.8 |

#### Palette in OKLCH (L, C, h) and CIELAB L*

| colour | hex | OKLab L | OKLab C | OKLCH h (deg) | CIELAB L* |
|---|---|---|---|---|---|
| nord0 | #2e3440 | 0.324 | 0.023 | 264.2 | 21.6 |
| nord1 | #3b4252 | 0.379 | 0.029 | 266.5 | 27.9 |
| nord2 | #434c5e | 0.416 | 0.032 | 264.1 | 32.2 |
| nord3 | #4c566a | 0.452 | 0.035 | 264.1 | 36.4 |
| nord3b (port-brightened) | #616e88 | 0.537 | 0.044 | 264.1 | 46.3 |
| nord4 | #d8dee9 | 0.899 | 0.016 | 262.7 | 88.3 |
| nord5 | #e5e9f0 | 0.933 | 0.010 | 261.8 | 92.2 |
| nord6 | #eceff4 | 0.951 | 0.007 | 260.7 | 94.4 |
| nord7 | #8fbcbb | 0.763 | 0.048 | 194.5 | 73.1 |
| nord8 | #88c0d0 | 0.775 | 0.062 | 217.5 | 74.5 |
| nord9 | #81a1c1 | 0.697 | 0.059 | 248.7 | 65.0 |
| nord10 | #5e81ac | 0.594 | 0.077 | 254.0 | 53.0 |
| nord11 | #bf616a | 0.606 | 0.121 | 15.3 | 52.6 |
| nord12 | #d08770 | 0.693 | 0.096 | 38.2 | 63.3 |
| nord13 | #ebcb8b | 0.855 | 0.089 | 84.1 | 83.0 |
| nord14 | #a3be8c | 0.768 | 0.075 | 131.1 | 73.9 |
| nord15 | #b48ead | 0.692 | 0.062 | 332.7 | 63.4 |

Raw Frost+Aurora lightness spans L 0.594 (nord10) to 0.855 (nord13).

#### Dark mode, raw hex: cells are "WCAG ratio / APCA |Lc|"

| colour | hex | window #222226 | list #1e1e1e | sidebar #28282c | sidebar2 #2e2e32 | card #303030 |
|---|---|---|---|---|---|---|
| nord3 | #4c566a | 2.15 / 13.9 | 2.26 / 14.6 | 1.99 / 12.9 | 1.83 / 11.7 | 1.79 / 11.3 |
| nord3b* | #616e88 | 3.09 / 23.9 | 3.25 / 24.5 | 2.86 / 22.8 | 2.64 / 21.6 | 2.57 / 21.2 |
| nord4 | #d8dee9 | 11.73 / 83.9 | 12.34 / 84.5 | 10.87 / 82.9 | 10.01 / 81.6 | 9.77 / 81.3 |
| nord7 | #8fbcbb | 7.61 / 59.1 | 8.00 / 59.7 | 7.05 / 58.1 | 6.49 / 56.8 | 6.33 / 56.5 |
| nord8 | #88c0d0 | 7.92 / 61.2 | 8.33 / 61.8 | 7.34 / 60.2 | 6.76 / 58.9 | 6.60 / 58.6 |
| nord9 | #81a1c1 | 5.89 / 47.2 | 6.19 / 47.8 | 5.46 / 46.1 | 5.02 / 44.9 | 4.90 / 44.5 |
| nord10 | #5e81ac | 3.93 / 31.7 | 4.14 / 32.3 | 3.64 / 30.7 | 3.36 / 29.4 | 3.28 / 29.0 |
| nord11 | #bf616a | 3.87 / 31.5 | 4.08 / 32.1 | 3.59 / 30.5 | 3.31 / 29.2 | 3.23 / 28.9 |
| nord12 | #d08770 | 5.57 / 45.0 | 5.86 / 45.6 | 5.16 / 44.0 | 4.75 / 42.7 | 4.64 / 42.3 |
| nord13 | #ebcb8b | 10.15 / 74.9 | 10.68 / 75.6 | 9.40 / 73.9 | 8.66 / 72.7 | 8.45 / 72.3 |
| nord14 | #a3be8c | 7.78 / 60.2 | 8.18 / 60.8 | 7.20 / 59.2 | 6.63 / 57.9 | 6.47 / 57.5 |
| nord15 | #b48ead | 5.60 / 45.0 | 5.89 / 45.6 | 5.18 / 44.0 | 4.77 / 42.8 | 4.66 / 42.4 |

#### Dark mode, after `max(l, 0.85)` (clip rendering)

| colour | hex | window #222226 | list #1e1e1e | sidebar #28282c | sidebar2 #2e2e32 | card #303030 |
|---|---|---|---|---|---|---|
| nord3 | #c2cee6 | 10.01 / 74.1 | 10.53 / 74.7 | 9.28 / 73.0 | 8.54 / 71.8 | 8.34 / 71.4 |
| nord3b* | #bfceeb | 10.00 / 74.0 | 10.51 / 74.6 | 9.26 / 72.9 | 8.53 / 71.7 | 8.32 / 71.3 |
| nord4 | #d8dee9 | 11.73 / 83.9 | 12.34 / 84.5 | 10.87 / 82.9 | 10.01 / 81.6 | 9.77 / 81.3 |
| nord7 | #aad8d7 | 10.20 / 75.2 | 10.73 / 75.8 | 9.45 / 74.2 | 8.70 / 72.9 | 8.49 / 72.5 |
| nord8 | #a0d8e9 | 10.19 / 75.1 | 10.71 / 75.8 | 9.44 / 74.1 | 8.69 / 72.9 | 8.48 / 72.5 |
| nord9 | #b0d2f3 | 10.08 / 74.5 | 10.61 / 75.1 | 9.34 / 73.5 | 8.60 / 72.2 | 8.40 / 71.9 |
| nord10 | #abd1ff | 10.04 / 74.2 | 10.56 / 74.9 | 9.30 / 73.2 | 8.56 / 72.0 | 8.36 / 71.6 |
| nord11 | #ffadb4 | 8.97 / 67.9 | 9.44 / 68.6 | 8.31 / 66.9 | 7.66 / 65.7 | 7.47 / 65.3 |
| nord12 | #ffb8a0 | 9.52 / 71.3 | 10.02 / 71.9 | 8.82 / 70.2 | 8.12 / 69.0 | 7.93 / 68.6 |
| nord13 | #ebcb8b | 10.15 / 74.9 | 10.68 / 75.6 | 9.40 / 73.9 | 8.66 / 72.7 | 8.45 / 72.3 |
| nord14 | #bdd8a5 | 10.21 / 75.3 | 10.74 / 75.9 | 9.46 / 74.2 | 8.71 / 73.0 | 8.50 / 72.6 |
| nord15 | #e7bfe0 | 9.76 / 72.6 | 10.26 / 73.2 | 9.04 / 71.5 | 8.32 / 70.3 | 8.12 / 69.9 |

#### Light mode, raw hex

| colour | hex | window #fafafb | list #ffffff | sidebar #ebebed | sidebar2 #f2f2f4 |
|---|---|---|---|---|---|
| nord3 | #4c566a | 7.07 / 82.7 | 7.38 / 85.6 | 6.20 / 73.9 | 6.60 / 78.0 |
| nord3b* | #616e88 | 4.92 / 72.4 | 5.13 / 75.4 | 4.31 / 63.6 | 4.59 / 67.7 |
| nord4 | #d8dee9 | 1.30 / 14.3 | 1.35 / 17.2 | 1.13 / 0.0 | 1.21 / 9.6 |
| nord7 | #8fbcbb | 2.00 / 37.7 | 2.08 / 40.7 | 1.75 / 28.9 | 1.86 / 33.0 |
| nord8 | #88c0d0 | 1.92 / 35.7 | 2.00 / 38.7 | 1.68 / 26.9 | 1.79 / 31.0 |
| nord9 | #81a1c1 | 2.58 / 49.3 | 2.69 / 52.2 | 2.26 / 40.5 | 2.41 / 44.6 |
| nord10 | #5e81ac | 3.86 / 64.5 | 4.03 / 67.5 | 3.38 / 55.7 | 3.60 / 59.8 |
| nord11 | #bf616a | 3.92 / 64.7 | 4.09 / 67.7 | 3.44 / 55.9 | 3.66 / 60.0 |
| nord12 | #d08770 | 2.73 / 51.4 | 2.84 / 54.4 | 2.39 / 42.6 | 2.54 / 46.7 |
| nord13 | #ebcb8b | 1.50 / 22.7 | 1.56 / 25.7 | 1.31 / 13.9 | 1.40 / 18.0 |
| nord14 | #a3be8c | 1.95 / 36.7 | 2.04 / 39.7 | 1.71 / 27.9 | 1.82 / 32.0 |
| nord15 | #b48ead | 2.72 / 51.4 | 2.83 / 54.3 | 2.38 / 42.6 | 2.53 / 46.7 |

#### Light mode, after `min(l, 0.5)`

| colour | hex | window #fafafb | list #ffffff | sidebar #ebebed | sidebar2 #f2f2f4 |
|---|---|---|---|---|---|
| nord3 | #4c566a | 7.07 / 82.7 | 7.38 / 85.6 | 6.20 / 73.9 | 6.60 / 78.0 |
| nord3b* | #57637d | 5.77 / 77.1 | 6.02 / 80.1 | 5.06 / 68.3 | 5.39 / 72.4 |
| nord4 | #5e636d | 5.78 / 77.2 | 6.03 / 80.2 | 5.07 / 68.4 | 5.39 / 72.5 |
| nord7 | #416c6b | 5.62 / 76.3 | 5.86 / 79.2 | 4.92 / 67.5 | 5.24 / 71.6 |
| nord8 | #356c7b | 5.62 / 76.2 | 5.86 / 79.2 | 4.92 / 67.4 | 5.24 / 71.5 |
| nord9 | #486684 | 5.74 / 76.9 | 5.98 / 79.9 | 5.03 / 68.1 | 5.35 / 72.2 |
| nord10 | #43658f | 5.76 / 77.0 | 6.01 / 79.9 | 5.04 / 68.1 | 5.37 / 72.3 |
| nord11 | #9c424c | 6.11 / 78.2 | 6.37 / 81.1 | 5.35 / 69.3 | 5.70 / 73.4 |
| nord12 | #914e39 | 6.00 / 77.9 | 6.26 / 80.9 | 5.26 / 69.1 | 5.60 / 73.2 |
| nord13 | #7b5e1d | 5.82 / 77.2 | 6.07 / 80.2 | 5.10 / 68.4 | 5.43 / 72.5 |
| nord14 | #546c3e | 5.61 / 76.3 | 5.85 / 79.2 | 4.91 / 67.4 | 5.23 / 71.6 |
| nord15 | #795673 | 5.94 / 77.9 | 6.19 / 80.8 | 5.20 / 69.0 | 5.54 / 73.2 |

#### Worst case over all backgrounds in the mode, and threshold flags
Flag columns read "R>=4.5, R>=3, Lc>=60, Lc>=75" with Y/-. "min" is the minimum over every listed background in that mode (dark: 5 backgrounds including the card; light: 4).

Dark mode:

| colour | raw hex | raw min R | raw min Lc | raw 4.5/3/Lc60/Lc75 | adj hex | adj min R | adj min Lc | adj 4.5/3/Lc60/Lc75 | OKLab L raw -> adj | ideal outside sRGB |
|---|---|---|---|---|---|---|---|---|---|---|
| nord3 | #4c566a | 1.79 | 11.3 | - - - - | #c2cee6 | 8.34 | 71.4 | Y Y Y - | 0.452 -> 0.850 | no |
| nord3b* | #616e88 | 2.57 | 21.2 | - - - - | #bfceeb | 8.32 | 71.3 | Y Y Y - | 0.537 -> 0.849 | no |
| nord4 | #d8dee9 | 9.77 | 81.3 | Y Y Y Y | #d8dee9 | 9.77 | 81.3 | Y Y Y Y | 0.899 -> 0.899 | no |
| nord7 | #8fbcbb | 6.33 | 56.5 | Y Y - - | #aad8d7 | 8.49 | 72.5 | Y Y Y - | 0.763 -> 0.850 | no |
| nord8 | #88c0d0 | 6.60 | 58.6 | Y Y - - | #a0d8e9 | 8.48 | 72.5 | Y Y Y - | 0.775 -> 0.849 | no |
| nord9 | #81a1c1 | 4.90 | 44.5 | Y Y - - | #b0d2f3 | 8.40 | 71.9 | Y Y Y - | 0.697 -> 0.850 | no |
| nord10 | #5e81ac | 3.28 | 29.0 | - Y - - | #abd1ff | 8.36 | 71.6 | Y Y Y - | 0.594 -> 0.849 | yes |
| nord11 | #bf616a | 3.23 | 28.9 | - Y - - | #ffadb4 | 7.47 | 65.3 | Y Y Y - | 0.606 -> 0.828 | yes |
| nord12 | #d08770 | 4.64 | 42.3 | Y Y - - | #ffb8a0 | 7.93 | 68.6 | Y Y Y - | 0.693 -> 0.843 | yes |
| nord13 | #ebcb8b | 8.45 | 72.3 | Y Y Y - | #ebcb8b | 8.45 | 72.3 | Y Y Y - | 0.855 -> 0.855 | no |
| nord14 | #a3be8c | 6.47 | 57.5 | Y Y - - | #bdd8a5 | 8.50 | 72.6 | Y Y Y - | 0.768 -> 0.849 | no |
| nord15 | #b48ead | 4.66 | 42.4 | Y Y - - | #e7bfe0 | 8.12 | 69.9 | Y Y Y - | 0.692 -> 0.849 | no |

Light mode:

| colour | raw hex | raw min R | raw min Lc | raw 4.5/3/Lc60/Lc75 | adj hex | adj min R | adj min Lc | adj 4.5/3/Lc60/Lc75 | OKLab L raw -> adj | ideal outside sRGB |
|---|---|---|---|---|---|---|---|---|---|---|
| nord3 | #4c566a | 6.20 | 73.9 | Y Y Y - | #4c566a | 6.20 | 73.9 | Y Y Y - | 0.452 -> 0.452 | no |
| nord3b* | #616e88 | 4.31 | 63.6 | - Y Y - | #57637d | 5.06 | 68.3 | Y Y Y - | 0.537 -> 0.500 | no |
| nord4 | #d8dee9 | 1.13 | 0.0 | - - - - | #5e636d | 5.07 | 68.4 | Y Y Y - | 0.899 -> 0.499 | no |
| nord7 | #8fbcbb | 1.75 | 28.9 | - - - - | #416c6b | 4.92 | 67.5 | Y Y Y - | 0.763 -> 0.500 | no |
| nord8 | #88c0d0 | 1.68 | 26.9 | - - - - | #356c7b | 4.92 | 67.4 | Y Y Y - | 0.775 -> 0.500 | no |
| nord9 | #81a1c1 | 2.26 | 40.5 | - - - - | #486684 | 5.03 | 68.1 | Y Y Y - | 0.697 -> 0.499 | no |
| nord10 | #5e81ac | 3.38 | 55.7 | - Y - - | #43658f | 5.04 | 68.1 | Y Y Y - | 0.594 -> 0.500 | no |
| nord11 | #bf616a | 3.44 | 55.9 | - Y - - | #9c424c | 5.35 | 69.3 | Y Y Y - | 0.606 -> 0.501 | no |
| nord12 | #d08770 | 2.39 | 42.6 | - - - - | #914e39 | 5.26 | 69.1 | Y Y Y - | 0.693 -> 0.500 | no |
| nord13 | #ebcb8b | 1.31 | 13.9 | - - - - | #7b5e1d | 5.10 | 68.4 | Y Y Y - | 0.855 -> 0.499 | no |
| nord14 | #a3be8c | 1.71 | 27.9 | - - - - | #546c3e | 4.91 | 67.4 | Y Y Y - | 0.768 -> 0.500 | no |
| nord15 | #b48ead | 2.38 | 42.6 | - - - - | #795673 | 5.20 | 69.0 | Y Y Y - | 0.692 -> 0.500 | no |

#### Adjusted hex values (what the theme actually paints)

| colour | raw | dark adj (clip) | dark adj (CSS gamut-map) | light adj |
|---|---|---|---|---|
| nord3 | #4c566a | #c2cee6 | same | #4c566a |
| nord3b* | #616e88 | #bfceeb | same | #57637d |
| nord4 | #d8dee9 | #d8dee9 | same | #5e636d |
| nord7 | #8fbcbb | #aad8d7 | same | #416c6b |
| nord8 | #88c0d0 | #a0d8e9 | same | #356c7b |
| nord9 | #81a1c1 | #b0d2f3 | same | #486684 |
| nord10 | #5e81ac | #abd1ff | #abd1ff | #43658f |
| nord11 | #bf616a | #ffadb4 | #ffb1b7 | #9c424c |
| nord12 | #d08770 | #ffb8a0 | #ffb8a0 | #914e39 |
| nord13 | #ebcb8b | #ebcb8b | same | #7b5e1d |
| nord14 | #a3be8c | #bdd8a5 | same | #546c3e |
| nord15 | #b48ead | #e7bfe0 | same | #795673 |

nord11 in dark mode: ideal point is outside sRGB; clip gives #ffadb4 (OKLab L 0.828, 0.033 dE_OK from the ideal point, above the 0.02 JND), CSS gamut mapping gives #ffb1b7 (min ratio 7.68, min |Lc| 66.8 against 7.47 and 65.3 for the clip). nord10 and nord12 give identical results either way.

#### Reference: raw accents on Nord's own backgrounds (nord0 dark, nord6 bright)
This is the pairing the Nord palette was designed around. Compared with it, the theme's dark backgrounds (#1e1e1e-#303030) give each raw accent somewhat more contrast (for example nord10 3.10 on nord0 vs 3.28-4.14 here), while the theme's light backgrounds give about the same as nord6 (nord11 3.55 on nord6 vs 3.44-4.09 here; #ebebed is the lowest).

| colour | hex | R on nord0 #2e3440 | |Lc| on nord0 | R on nord6 #eceff4 | |Lc| on nord6 |
|---|---|---|---|---|---|
| nord3 | #4c566a | 1.69 | 10.3 | 6.40 | 76.0 |
| nord3b* | #616e88 | 2.43 | 20.3 | 4.45 | 65.7 |
| nord4 | #d8dee9 | 9.25 | 80.3 | 1.17 | 7.6 |
| nord7 | #8fbcbb | 5.99 | 55.5 | 1.81 | 31.0 |
| nord8 | #88c0d0 | 6.24 | 57.6 | 1.74 | 29.0 |
| nord9 | #81a1c1 | 4.64 | 43.6 | 2.34 | 42.6 |
| nord10 | #5e81ac | 3.10 | 28.1 | 3.50 | 57.8 |
| nord11 | #bf616a | 3.05 | 27.9 | 3.55 | 58.0 |
| nord12 | #d08770 | 4.39 | 41.4 | 2.47 | 44.7 |
| nord13 | #ebcb8b | 8.00 | 71.3 | 1.35 | 16.0 |
| nord14 | #a3be8c | 6.13 | 56.6 | 1.77 | 30.0 |
| nord15 | #b48ead | 4.41 | 41.4 | 2.46 | 44.7 |

Key observations (all from the tables above):
- Raw dark: nord10 (min 3.28) and nord11 (min 3.23) fail 4.5:1 on all five dark backgrounds but pass 3:1 on all five. nord12 (min 4.64) and nord15 (min 4.66) pass 4.5:1 with under 0.2 margin on the card (#303030). nord3 (1.79-2.26) fails even 3:1 on dark; nord3b (2.57-3.25) reaches 3:1 only on #222226 (3.09) and #1e1e1e (3.25).
- Raw dark APCA: only nord4 (min 81.3) and nord13 (min 72.3) reach Lc 60 on all five backgrounds. nord7 is below 60 everywhere (56.5-59.7); nord8 is 58.6-61.8 (above 60 on window, list, sidebar); nord14 is 57.5-60.8; nothing except nord4 reaches Lc 75 everywhere.
- Raw light: nord4 is invisible (1.13-1.35; Lc 0.0 on #ebebed). nord7, nord8, nord13, nord14 are below 2.1:1 (nord13 1.31-1.56). nord9, nord12, nord15 are 2.26-2.84. nord10 (3.38-4.03) and nord11 (3.44-4.09) pass 3:1 but never reach 4.5:1 (best case 4.09 on #ffffff). Only nord3 passes 4.5:1 raw (6.20-7.38); nord3b (#616e88) passes 4.5:1 on #fafafb, #ffffff, #f2f2f4 (4.92, 5.13, 4.59) but not on #ebebed (4.31).
- Adjusted dark: every accent passes 4.5:1 (min 7.47, nord11) and Lc 60 (min 65.3, nord11). Lc 75 is met on some backgrounds only: for example on #1e1e1e nord7 75.8, nord8 75.8, nord9 75.1, nord13 75.6, nord14 75.9 pass while nord10 74.9, nord11 68.6, nord12 71.9, nord15 73.2 do not; on the card (#303030) none pass (max 72.6).
- Adjusted light: every accent passes 4.5:1 (min 4.91, nord14; nord7 and nord8 4.92, both on #ebebed) and Lc 60 (min 67.4). Lc 75 is met on #fafafb (76.2-78.2) and #ffffff (79.2-81.1) but not on the two sidebar backgrounds (#f2f2f4 71.5-73.4, #ebebed 67.4-69.3). The 4.5:1 margin is thinnest on #ebebed: nord14 0.41, nord7 and nord8 0.42, nord9 0.53, nord10 0.54, nord13 0.60.
- nord3 on light (L 0.452 < 0.5) is untouched by the rule: 6.20-7.38, Lc 73.9-85.6. In dark the rule moves nord3 (the comment/muted swatch) to #c2cee6 (L 0.85, 8.34-10.53:1), only 0.05 L below nord4 itself and level with every adjusted accent. The rule therefore cannot produce a "muted" tone in dark mode from nord3.
- Lightness after the rule: dark adjusted L is 0.828-0.855 for all nine Frost+Aurora colours (nord11 is lowest because of the clip); light adjusted L is 0.499-0.501 for all nine.

#### Script (also saved as nord_measure.py)

```python
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
```

### Inferences
- A designer who keeps the theme's OKLab rule gets legible text from any Nord accent in both modes (4.5:1 and Lc 60 everywhere) but loses lightness as a cue: after the rule, accents differ only by hue and chroma. Role distinctions that rely on "brighter vs dimmer" (for example nord8 primary vs nord10 tertiary) vanish.
- Raw colours are a different design problem: on dark they are acceptable for large/bold or non-text use (3:1) but nord10 and nord11 are weak as small text; on light only nord3 (and nord0-nord2) work as raw text, every Frost/Aurora colour needs darkening, which is what `min(l, 0.5)` does.
- For a "muted" role in dark mode, the rule must be bypassed (nord3 raw is 1.79-2.26:1 and nord3b is 2.57-3.25:1, both below 4.5:1 for small text and mostly below 3:1), so a muted text tone would come from opacity or a dedicated lightness, not from nord3 passing through the rule. In light mode nord3 is fine unmodified (6.20+).
- Margin on light backgrounds is thin: ~0.4-0.5 above 4.5:1 on #ebebed means a translucent or antialiased rendering on a selected/hovered row could dip under the threshold; selected-row backgrounds were not measured.
- In dark mode nord11 is the weakest adjusted accent (lowest ratio and Lc), and its pixel value depends on whether the engine clips or gamut-maps.

### Gaps
- Gecko's treatment of out-of-gamut relative `oklab()` colours (clip vs CSS gamut mapping) was not confirmed. A web search surfaced a W3C thread saying Firefox and Safari clip a specific example and a Gecko source branch that gamut-maps only behind a pref (possibly Nightly-only), but the pages I could open (a W3C thread about `hsl()` saturation) did not confirm it, so both renderings are tabulated.
- Selected/hovered/unread row backgrounds, link hover states, and translucent overlays were not provided and are not measured. No light-mode card colour was provided.
- APCA Lc 60/75 apply to specific font sizes and weights; the thread-list and message-pane font sizes are unknown, and sources disagree on the Lc 75 size floor (sass-apca README: 18px/400; a Myndex Bridge-PCA draft cited by a search snippet: 16px), so the pass flags are mechanical, not a size-aware verdict.
- WCAG 2 and APCA were computed on solid 8-bit sRGB values; text anti-aliasing, subpixel rendering and font weight are not modelled.

## 3. Colour-vision-deficiency confusability of the Frost and Aurora colours

### Takeaway
Raw Nord Frost+Aurora is already tight (closest pair ΔE2000 6.9 in normal vision, 4.7 under protanopia, 3.5 under tritanopia, versus 21.7 / 12.3 / 11.1 for the Okabe-Ito benchmark). After the theme's lightness flattening the key pairs collapse: nord11 vs nord14 falls from 47.8 (normal vision) and 15.2 (raw, deuteranopia) to 5.6 (dark-adjusted) or 2.4 (light-adjusted) under deuteranopia, nord12 vs nord14 to 1.6 / 3.0, nord9 vs nord10 is only 3.0 even with normal vision (ΔE_OK 0.019 or 0.020, at or under the 0.02 JND), nord15 collapses into the Frost blues under protan/deutan vision, while blue-vs-yellow pairs (nord8/9/10 vs nord13) and nord14 vs nord15 stay far apart.

### Cited Findings

#### Method
- Simulation: Machado, Oliveira and Fernandes (2009), Table 1 matrices at severity 1.0 (full dichromacy); the source page labels them "Protanomaly / Deuteranomaly / Tritanomaly" with severity 1.0 as the dichromacy case — [Machado et al. CVD simulation page](https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html). Matrices used: protan `[0.152286 1.052583 -0.204868; 0.114503 0.786281 0.099216; -0.003882 -0.048116 1.051998]`, deutan `[0.367322 0.860646 -0.227968; 0.280085 0.672501 0.047413; -0.011820 0.042940 0.968881]`, tritan `[1.255528 -0.076749 -0.178779; -0.078411 0.930809 0.147602; 0.004733 0.691367 0.303900]`. The page does not state the colour space; I applied them to linear sRGB (decode, multiply, clamp to 0-1, re-encode), which is the common implementation.
- Distance: CIEDE2000 (Sharma, Wu, Dalal 2005, Color Research & Application 30(1); the paper itself was not fetched, but the implementation reproduces five of its supplementary test pairs, recalled as 2.0425, 2.8615, 4.3065, 27.1492 and 1.2644, to four decimals) on CIELAB from D65 XYZ, and ΔE_OK (Euclidean distance in OKLab; CSS Color 4 section 20.3). CSS Color 4 gives one just-noticeable difference as 0.02 in ΔE_OK and says "using deltaE2000, one JND is 2" — [CSS Color 4 14.2.1](https://www.w3.org/TR/css-color-4/#binsearch). Those JNDs are for adjacent patches; separating coloured text tokens by category needs more. Working bands used below are my convention, not a standard: ΔE2000 < 5 hard to tell apart, 5-10 weak, >= 10 adequate.
- Benchmark: the Okabe-Ito palette (orange #e69f00, sky blue #56b4e9, bluish green #009e73, yellow #f0e442, blue #0072b2, vermillion #d55e00, reddish purple #cc79a7; black excluded) run through the same pipeline, hex values from [Siegal lab colour-palette page (secondary source)](https://siegal.bio.nyu.edu/color-palette/); the palette is attributed to Masataka Okabe and Kei Ito in a web search result set (see also their Jfly colour universal design guide, [jfly.uni-koeln.de/color](https://jfly.uni-koeln.de/color/), whose palette table did not parse out of the HTML I fetched, so the hex values rest on the secondary source).
- Three colour sets are analysed because the theme changes what is on screen: raw hex, dark-adjusted (clip) and light-adjusted (clip).

#### Simulated swatches (hex after simulation)

Raw:

| colour | normal | deuteranopia | protanopia | tritanopia |
|---|---|---|---|---|
| nord7 | #8fbcbb | #adb1bb | #b6b7bb | #80bfbc |
| nord8 | #88c0d0 | #aab3d0 | #b5bcd1 | #6ec6c5 |
| nord9 | #81a1c1 | #8d9bc0 | #95a1c3 | #6da8ab |
| nord10 | #5e81ac | #677bab | #7183ae | #3f8b90 |
| nord11 | #bf616a | #8c8568 | #74726a | #ce5565 |
| nord12 | #d08770 | #aa9f6f | #99906e | #e07c81 |
| nord13 | #ebcb8b | #e2d28d | #daca86 | #f9c0bb |
| nord14 | #a3be8c | #beb58e | #c3b789 | #a4bab1 |
| nord15 | #b48ead | #969bac | #8e96ae | #b89098 |

Dark-adjusted:

| colour | normal | deuteranopia | protanopia | tritanopia |
|---|---|---|---|---|
| nord7 | #aad8d7 | #c9ccd8 | #d2d3d7 | #9cdbd8 |
| nord8 | #a0d8e9 | #c1cbe9 | #cdd4ea | #87dedd |
| nord9 | #b0d2f3 | #bdcbf2 | #c5d2f5 | #9ddadd |
| nord10 | #abd1ff | #b6cafe | #c0d2ff | #91dbe0 |
| nord11 | #ffadb4 | #cfc9b3 | #bbbab4 | #ffa5b0 |
| nord12 | #ffb8a0 | #dacea0 | #c9c09e | #ffadb2 |
| nord13 | #ebcb8b | #e2d28d | #daca86 | #f9c0bb |
| nord14 | #bdd8a5 | #d9cfa7 | #ddd1a2 | #bfd3ca |
| nord15 | #e7bfe0 | #c7cddf | #bec8e1 | #ebc1ca |

Light-adjusted:

| colour | normal | deuteranopia | protanopia | tritanopia |
|---|---|---|---|---|
| nord7 | #416c6b | #5f626b | #67686b | #2f6e6c |
| nord8 | #356c7b | #58617b | #62697c | #007171 |
| nord9 | #486684 | #536183 | #5a6785 | #306d70 |
| nord10 | #43658f | #4b608e | #546791 | #1c6e74 |
| nord11 | #9c424c | #6d664a | #56544c | #aa3546 |
| nord12 | #914e39 | #6f6638 | #5f5737 | #9e4249 |
| nord13 | #7b5e1d | #716520 | #6a5e14 | #865551 |
| nord14 | #546c3e | #6c6441 | #70663b | #556861 |
| nord15 | #795673 | #5e6372 | #565e74 | #7c5860 |

#### Requested pairs and neighbours: ΔE2000 and ΔE_OK in normal vision (normal), deuteranopia (deut), protanopia (prot), tritanopia (trit)

Raw hex:

| pair | dE00 normal | dE00 deut | dE00 prot | dE00 trit | dE_OK normal | dE_OK deut | dE_OK prot | dE_OK trit |
|---|---|---|---|---|---|---|---|---|
| nord11 vs nord14 | 47.8 | 15.2 | 25.9 | 42.9 | 0.233 | 0.156 | 0.232 | 0.240 |
| nord12 vs nord13 | 24.7 | 14.3 | 18.1 | 16.8 | 0.177 | 0.163 | 0.189 | 0.170 |
| nord8 vs nord9 | 12.6 | 7.7 | 8.8 | 8.7 | 0.085 | 0.079 | 0.088 | 0.083 |
| nord9 vs nord10 | 11.1 | 11.6 | 10.5 | 10.5 | 0.104 | 0.107 | 0.101 | 0.102 |
| nord8 vs nord10 | 22.1 | 19.1 | 19.0 | 17.9 | 0.186 | 0.186 | 0.188 | 0.181 |
| nord10 vs nord15 | 25.7 | 15.0 | 9.0 | 46.1 | 0.132 | 0.117 | 0.070 | 0.160 |
| nord11 vs nord12 | 15.1 | 10.0 | 14.8 | 10.4 | 0.100 | 0.088 | 0.107 | 0.094 |
| nord13 vs nord14 | 18.8 | 9.9 | 6.7 | 33.1 | 0.109 | 0.097 | 0.064 | 0.126 |
| nord11 vs nord15 | 18.9 | 22.9 | 20.6 | 17.7 | 0.121 | 0.102 | 0.133 | 0.134 |
| nord7 vs nord14 | 17.4 | 21.0 | 18.8 | 9.6 | 0.069 | 0.069 | 0.069 | 0.042 |
| nord12 vs nord14 | 35.9 | 6.9 | 12.1 | 38.2 | 0.146 | 0.072 | 0.127 | 0.165 |
| nord7 vs nord8 | 6.9 | 7.2 | 7.3 | 3.5 | 0.029 | 0.029 | 0.030 | 0.023 |

Dark-adjusted:

| pair | dE00 normal | dE00 deut | dE00 prot | dE00 trit | dE_OK normal | dE_OK deut | dE_OK prot | dE_OK trit |
|---|---|---|---|---|---|---|---|---|
| nord11 vs nord14 | 41.8 | 5.6 | 14.6 | 36.9 | 0.148 | 0.030 | 0.090 | 0.135 |
| nord12 vs nord13 | 18.8 | 5.1 | 8.4 | 6.4 | 0.069 | 0.030 | 0.052 | 0.044 |
| nord8 vs nord9 | 9.4 | 2.7 | 4.3 | 4.4 | 0.031 | 0.013 | 0.020 | 0.023 |
| nord9 vs nord10 | 3.0 | 3.3 | 2.8 | 2.0 | 0.019 | 0.020 | 0.015 | 0.012 |
| nord8 vs nord10 | 11.8 | 6.0 | 7.0 | 3.2 | 0.044 | 0.033 | 0.035 | 0.014 |
| nord10 vs nord15 | 25.2 | 9.9 | 6.1 | 44.9 | 0.089 | 0.051 | 0.043 | 0.122 |
| nord11 vs nord12 | 11.6 | 7.1 | 10.4 | 2.5 | 0.044 | 0.035 | 0.043 | 0.019 |
| nord13 vs nord14 | 17.6 | 6.6 | 5.0 | 31.5 | 0.066 | 0.037 | 0.034 | 0.088 |
| nord11 vs nord15 | 13.7 | 18.5 | 14.6 | 10.2 | 0.068 | 0.058 | 0.064 | 0.069 |
| nord7 vs nord14 | 17.4 | 21.4 | 18.7 | 10.3 | 0.069 | 0.071 | 0.069 | 0.043 |
| nord12 vs nord14 | 33.6 | 1.6 | 5.4 | 35.9 | 0.118 | 0.008 | 0.055 | 0.121 |
| nord7 vs nord8 | 7.0 | 6.5 | 7.4 | 3.4 | 0.027 | 0.027 | 0.026 | 0.021 |

Light-adjusted:

| pair | dE00 normal | dE00 deut | dE00 prot | dE00 trit | dE_OK normal | dE_OK deut | dE_OK prot | dE_OK trit |
|---|---|---|---|---|---|---|---|---|
| nord11 vs nord14 | 44.0 | 2.4 | 13.9 | 38.1 | 0.166 | 0.012 | 0.081 | 0.176 |
| nord12 vs nord13 | 19.3 | 4.8 | 9.3 | 8.4 | 0.072 | 0.023 | 0.048 | 0.058 |
| nord8 vs nord9 | 10.6 | 2.8 | 4.2 | 4.3 | 0.033 | 0.014 | 0.021 | 0.023 |
| nord9 vs nord10 | 3.0 | 3.4 | 3.5 | 2.1 | 0.020 | 0.021 | 0.021 | 0.013 |
| nord8 vs nord10 | 13.2 | 6.2 | 7.7 | 3.6 | 0.046 | 0.036 | 0.040 | 0.014 |
| nord10 vs nord15 | 23.1 | 10.4 | 7.2 | 44.9 | 0.090 | 0.055 | 0.047 | 0.123 |
| nord11 vs nord12 | 11.5 | 5.2 | 9.6 | 3.3 | 0.048 | 0.024 | 0.037 | 0.030 |
| nord13 vs nord14 | 19.2 | 7.7 | 6.9 | 31.9 | 0.067 | 0.037 | 0.041 | 0.089 |
| nord11 vs nord15 | 16.3 | 21.3 | 16.3 | 14.9 | 0.086 | 0.068 | 0.063 | 0.105 |
| nord7 vs nord14 | 17.5 | 20.4 | 18.6 | 9.8 | 0.068 | 0.067 | 0.068 | 0.042 |
| nord12 vs nord14 | 34.9 | 3.0 | 6.2 | 36.6 | 0.125 | 0.015 | 0.055 | 0.146 |
| nord7 vs nord8 | 7.2 | 7.2 | 7.6 | 3.3 | 0.027 | 0.028 | 0.027 | 0.021 |

For the raw set the OKLab L difference between nord11 and nord14 is 0.162 (0.156 under deutan) which is why raw nord11/nord14 survive deuteranopia (ΔE2000 15.2); after the rule the L difference is 0.021 (dark) / 0.001 (light), so the only remaining cue is a hue/chroma difference that red-green dichromacy removes.

#### Pair matrices, ΔE2000: upper right triangle = normal vision, lower left triangle = worst case over the three CVD types (columns/rows n7 = nord7, and so on)

Raw hex:

|  | n7 | n8 | n9 | n10 | n11 | n12 | n13 | n14 | n15 |
|---|---|---|---|---|---|---|---|---|---|
| n7 | - | 6.9 | 16.5 | 25.0 | 44.7 | 37.2 | 28.6 | 17.4 | 33.6 |
| n8 | 3.5 | - | 12.6 | 22.1 | 48.6 | 42.8 | 33.6 | 25.6 | 35.4 |
| n9 | 6.9 | 7.7 | - | 11.1 | 37.0 | 34.0 | 40.2 | 33.4 | 25.0 |
| n10 | 16.9 | 17.9 | 10.5 | - | 35.0 | 36.0 | 44.9 | 40.5 | 25.7 |
| n11 | 23.2 | 28.1 | 25.2 | 22.7 | - | 15.1 | 39.6 | 47.8 | 18.9 |
| n12 | 20.0 | 27.6 | 29.8 | 32.5 | 10.0 | - | 24.7 | 35.9 | 22.1 |
| n13 | 23.3 | 31.5 | 38.0 | 44.7 | 24.0 | 14.3 | - | 18.8 | 38.8 |
| n14 | 9.6 | 12.8 | 11.7 | 20.6 | 15.2 | 6.9 | 6.7 | - | 43.5 |
| n15 | 7.1 | 8.2 | 4.7 | 9.0 | 17.7 | 12.1 | 15.4 | 25.2 | - |

Dark-adjusted:

|  | n7 | n8 | n9 | n10 | n11 | n12 | n13 | n14 | n15 |
|---|---|---|---|---|---|---|---|---|---|
| n7 | - | 7.0 | 14.8 | 17.6 | 39.8 | 35.8 | 27.8 | 17.4 | 32.6 |
| n8 | 3.4 | - | 9.4 | 11.8 | 43.4 | 40.9 | 33.2 | 25.8 | 34.1 |
| n9 | 2.5 | 2.7 | - | 3.0 | 34.0 | 33.6 | 37.8 | 32.5 | 25.6 |
| n10 | 3.3 | 3.2 | 2.0 | - | 33.8 | 34.5 | 37.8 | 36.3 | 25.2 |
| n11 | 8.2 | 14.6 | 18.3 | 20.8 | - | 11.6 | 29.9 | 41.8 | 13.7 |
| n12 | 16.3 | 24.6 | 28.8 | 31.5 | 2.5 | - | 18.8 | 33.6 | 21.7 |
| n13 | 22.8 | 31.6 | 36.1 | 39.0 | 8.8 | 5.1 | - | 17.6 | 36.2 |
| n14 | 10.3 | 13.4 | 10.4 | 12.3 | 5.6 | 1.6 | 5.0 | - | 42.7 |
| n15 | 2.5 | 3.3 | 3.9 | 6.1 | 10.2 | 9.0 | 6.5 | 24.1 | - |

Light-adjusted:

|  | n7 | n8 | n9 | n10 | n11 | n12 | n13 | n14 | n15 |
|---|---|---|---|---|---|---|---|---|---|
| n7 | - | 7.2 | 16.0 | 19.0 | 41.3 | 36.6 | 29.1 | 17.5 | 32.7 |
| n8 | 3.3 | - | 10.6 | 13.2 | 44.5 | 41.5 | 34.4 | 26.0 | 33.9 |
| n9 | 2.5 | 2.8 | - | 3.0 | 34.5 | 33.7 | 35.8 | 33.2 | 24.0 |
| n10 | 3.6 | 3.6 | 2.1 | - | 34.4 | 34.7 | 39.2 | 37.1 | 23.1 |
| n11 | 9.8 | 16.6 | 20.1 | 23.2 | - | 11.5 | 31.1 | 44.0 | 16.3 |
| n12 | 17.1 | 25.4 | 29.4 | 33.1 | 3.3 | - | 19.3 | 34.9 | 22.5 |
| n13 | 24.0 | 33.0 | 37.4 | 38.8 | 9.9 | 4.8 | - | 19.2 | 36.5 |
| n14 | 9.8 | 12.9 | 9.9 | 11.9 | 2.4 | 3.0 | 6.9 | - | 42.6 |
| n15 | 2.8 | 4.3 | 4.3 | 7.2 | 14.9 | 12.4 | 6.6 | 23.6 | - |

#### Six closest pairs among the nine Frost+Aurora colours, by ΔE2000 (ΔE_OK in brackets)

Raw:

- normal: nord7-nord8 6.9 (OK 0.029); nord9-nord10 11.1 (OK 0.104); nord8-nord9 12.6 (OK 0.085); nord11-nord12 15.1 (OK 0.100); nord7-nord9 16.5 (OK 0.083); nord7-nord14 17.4 (OK 0.069)
- deuteranopia: nord9-nord15 6.8 (OK 0.031); nord12-nord14 6.9 (OK 0.072); nord7-nord15 7.1 (OK 0.070); nord7-nord8 7.2 (OK 0.029); nord8-nord9 7.7 (OK 0.079); nord8-nord15 8.2 (OK 0.080)
- protanopia: nord9-nord15 4.7 (OK 0.039); nord13-nord14 6.7 (OK 0.064); nord7-nord8 7.3 (OK 0.030); nord8-nord9 8.8 (OK 0.088); nord10-nord15 9.0 (OK 0.070); nord9-nord10 10.5 (OK 0.101)
- tritanopia: nord7-nord8 3.5 (OK 0.023); nord7-nord9 6.9 (OK 0.070); nord8-nord9 8.7 (OK 0.083); nord7-nord14 9.6 (OK 0.042); nord11-nord12 10.4 (OK 0.094); nord9-nord10 10.5 (OK 0.102)

Dark-adjusted:

- normal: nord9-nord10 3.0 (OK 0.019); nord7-nord8 7.0 (OK 0.027); nord8-nord9 9.4 (OK 0.031); nord11-nord12 11.6 (OK 0.044); nord8-nord10 11.8 (OK 0.044); nord11-nord15 13.7 (OK 0.068)
- deuteranopia: nord12-nord14 1.6 (OK 0.008); nord7-nord15 2.5 (OK 0.009); nord8-nord9 2.7 (OK 0.013); nord9-nord10 3.3 (OK 0.020); nord8-nord15 4.2 (OK 0.018); nord12-nord13 5.1 (OK 0.030)
- protanopia: nord9-nord10 2.8 (OK 0.015); nord8-nord15 3.3 (OK 0.039); nord9-nord15 3.9 (OK 0.035); nord8-nord9 4.3 (OK 0.020); nord13-nord14 5.0 (OK 0.034); nord12-nord14 5.4 (OK 0.055)
- tritanopia: nord9-nord10 2.0 (OK 0.012); nord11-nord12 2.5 (OK 0.019); nord7-nord9 2.5 (OK 0.009); nord8-nord10 3.2 (OK 0.014); nord7-nord10 3.3 (OK 0.015); nord7-nord8 3.4 (OK 0.021)

Light-adjusted:

- normal: nord9-nord10 3.0 (OK 0.020); nord7-nord8 7.2 (OK 0.027); nord8-nord9 10.6 (OK 0.033); nord11-nord12 11.5 (OK 0.048); nord8-nord10 13.2 (OK 0.046); nord7-nord9 16.0 (OK 0.051)
- deuteranopia: nord11-nord14 2.4 (OK 0.012); nord8-nord9 2.8 (OK 0.014); nord7-nord15 2.8 (OK 0.011); nord12-nord14 3.0 (OK 0.015); nord9-nord10 3.4 (OK 0.021); nord8-nord15 4.4 (OK 0.019)
- protanopia: nord9-nord10 3.5 (OK 0.021); nord8-nord9 4.2 (OK 0.021); nord8-nord15 4.3 (OK 0.039); nord9-nord15 4.3 (OK 0.034); nord12-nord14 6.2 (OK 0.055); nord13-nord14 6.9 (OK 0.041)
- tritanopia: nord9-nord10 2.1 (OK 0.013); nord7-nord9 2.5 (OK 0.008); nord7-nord8 3.3 (OK 0.021); nord11-nord12 3.3 (OK 0.030); nord8-nord10 3.6 (OK 0.014); nord7-nord10 3.6 (OK 0.016)

#### Benchmark: Okabe-Ito, three closest pairs per vision type (ΔE2000; ΔE_OK)

- normal: orange-yellow 21.7 (OK 0.170); orange-vermillion 22.2 (OK 0.156); skyblue-blue 22.3 (OK 0.204)
- deuteranopia: orange-yellow 11.5 (OK 0.146); orange-vermillion 12.5 (OK 0.131); skyblue-reddishpurple 15.5 (OK 0.096)
- protanopia: blue-reddishpurple 12.3 (OK 0.095); skyblue-reddishpurple 14.1 (OK 0.137); orange-yellow 15.3 (OK 0.183)
- tritanopia: orange-reddishpurple 11.1 (OK 0.086); bluishgreen-blue 12.1 (OK 0.084); skyblue-bluishgreen 12.2 (OK 0.113)

Nord Frost+Aurora raw, the three closest pairs per vision type for comparison: normal nord7-nord8 6.9, nord9-nord10 11.1, nord8-nord9 12.6; deuteranopia nord9-nord15 6.8, nord12-nord14 6.9, nord7-nord15 7.1; protanopia nord9-nord15 4.7, nord13-nord14 6.7, nord7-nord8 7.3; tritanopia nord7-nord8 3.5, nord7-nord9 6.9, nord8-nord9 8.7.

### Inferences
- Requested pairs, using the dark-adjusted / light-adjusted ΔE2000 numbers: nord11 vs nord14 is the classic failure under deuteranopia (5.6 dark / 2.4 light) but adequate under protanopia (14.6 / 13.9) and tritanopia (36.9 / 38.1); nord12 vs nord13 is hard-to-weak under deuteranopia (5.1 / 4.8) and weak under protanopia (8.4 / 9.3) and tritanopia (6.4 / 8.4); nord8 vs nord9 is hard for every CVD type (2.7-4.4) and only 9.4 / 10.6 in normal vision; nord9 vs nord10 is not separable by anyone once lightness is flattened (2.0-3.5 for all four vision types, at or near one JND); nord8 vs nord10 is weak under deuteranopia and protanopia (6.0-7.7) and hard under tritanopia (3.2 / 3.6); nord10 vs nord15 is fine in normal vision and tritanopia (23-45) but weak under protanopia (6.1 / 7.2) and deuteranopia (9.9 / 10.4).
- A Frost trio (nord8, nord9, nord10) cannot carry three distinct meanings under the theme rule, even for normal vision. At most one or two Frost colours should be used as separate roles, and nord7 vs nord8 (6.9-7.2 in normal vision) is similarly redundant.
- Pairs that stay separated in all three CVD types and both adjusted sets (worst-case matrix value >= ~14): blue-family vs yellow (nord8/nord9/nord10 vs nord13: 31.6, 36.1, 39.0 dark; 33.0, 37.4, 38.8 light), blue-family vs orange (nord8/9/10 vs nord12: 24.6, 28.8, 31.5 dark; 25.4, 29.4, 33.1 light), nord14 vs nord15 (24.1 dark, 23.6 light), nord11 vs the blues (nord11-nord8 14.6, -nord9 18.3, -nord10 20.8 dark; 16.6, 20.1, 23.2 light) and nord7 vs nord13 (22.8 / 24.0). The worst-case values include tritanopia, so these separations hold under all three CVD types; they sit on the blue versus yellow/orange axis that red-green CVD preserves.
- Pairs to avoid as the only distinction: nord11-nord14 and nord12-nord14 (red/orange vs green), nord12-nord11 (2.5-3.3 worst, tritan), nord12-nord13 (4.8-5.1), nord13-nord14 (5.0-6.9), nord15 vs nord7/nord8/nord9 (2.5-4.3 under protan/deutan), nord9-nord10, nord7-nord8.
- If the theme rule is kept, any mapping that puts "error" (nord11) and "success" (nord14) on a single screen should add a non-colour cue (icon, weight, text label) because deuteranopes get ΔE2000 2.4-5.6 between them.
- Nord is a "dimmed pastel" palette (OKLCH chroma 0.048-0.121 in the raw set, Question 1 table) so the CVD margins are narrower than a saturated categorical palette; the Okabe-Ito minimum under CVD (11.1-12.3) is 2.6-3.2 times Nord's raw minimum under protanopia and tritanopia (4.7, 3.5) and 1.7 times under deuteranopia (11.5 vs 6.8).

### Gaps
- Severity 1.0 is full dichromacy. Milder deficiencies (Machado severity below 1.0) were not run; Viénot 1999 (the alternative the brief allowed) was not run.
- The Machado page does not state the working colour space; the linear-sRGB choice is mine. Simulated swatches are not a substitute for testing with CVD users.
- Distances are between solid swatches; small anti-aliased text reduces effective chroma and will make every ΔE here optimistic. The 5/10 bands are my convention, not a published threshold; only the 2.0 / 0.02 JND figures are cited.
- Okabe-Ito hex values come from a university lab page that republishes them (the Jfly page cited as the origin yielded no parseable palette table); treated as a secondary source for the hex values only.

## 4. How established Nord ports assign colours to semantic roles

### Takeaway
Across the official vim, emacs, VS Code and terminal ports and the third-party Joplin, Thunderbird, aerc, neomutt and Nordic GTK themes, error is nord11 (red) and success/added is nord14 (green), warning/modified is nord13 (yellow), primary accent/link/focus is nord8 (VS Code, Joplin, Thunderbird, vim markdown), muted/comment text is a brightened nord3 (#616e88) rather than nord3 itself, and quoted/nested levels are made by cycling Frost (and sometimes Aurora) hues or by dimming, with nord11 excluded from decorative cycles. Deviations: Nordic GTK uses nord10 for links and success and nord12 for warning, Joplin uses nord12 for warning, and Thunderbird Nord Hardt uses nord14 (green) for starred.

### Cited Findings

#### Cross-port role table (colour per port; sources in the per-port lists below)

| role | official docs | nord-vim | nord-emacs | VS Code | terminal ANSI | Nordic GTK | Joplin | Thunderbird Nord Hardt | aerc | neomutt-nord |
|---|---|---|---|---|---|---|---|---|---|---|
| link / accent / primary | nord8 primary accent | nord8 (markdown link text, Directory, MoreMsg); htmlLink and markdownUrl nord4 | link faces underline only; markdown-link and button text nord8 | textLink nord8; button, badge, progress nord8 | blue nord9, cyan nord8 | link nord10; selection nord7 (default build) or nord9 | url nord8; selected nord9 | primary, tab line, unread dot nord8 | tab selected #64A6B3 (off-palette) | URLs brightblue (nord9 in a Nord terminal) |
| error | nord11 | nord11 (diagnostics, SpellBad); Error bg nord11 | nord11 bold | nord11 | red nord11 | nord11 | nord11 | spam nord11 | ANSI red | brightred |
| warning | nord13 | nord13 (diagnostics, Todo, SpellCap); WarningMsg bg nord13 | nord13 bold | nord13 (editor); nord12 (input validation) | yellow nord13 | nord12 | nord12 (text); nord13 (background) | none | ANSI yellow | yellow used for search/flagged |
| success / added | nord14 | nord14 (strings, DiffAdd) | nord14 | nord14 | green nord14 | nord10 ($success = $cyan) | none | new-mail dot nord14 | ANSI green; flagged #a3be8c | brightgreen (message) |
| muted / comment | nord3 | #616e88 (brightened nord3) | #616e88 | #616e88 | bright black nord3 | n/a | colorFaded nord4 | read-row text #74818e (off-palette) | dim attribute | n/a |

#### nord-vim (official port, v0.19.0): syntax, UI and diagnostics assignments
- nord-vim 0.19.0 syntax: Comment `nord3_gui_bright` #616E88 (line 258), String and Character nord14 (281, 257), Number and Float nord15 (272, 266), Boolean nord9 (256), Keyword, Statement, Conditional, Type, Operator nord9 (270, 279, 260, 285, 273), Function nord8 (267), Constant, Identifier, Special, Tag nord4 (261, 268, 276, 283), Delimiter nord6 (264), Todo nord13 (284) — [nord.vim](https://github.com/nordtheme/vim/blob/main/colors/nord.vim)
- nord-vim UI/diagnostics: Error and ErrorMsg = nord4 text on nord11 background (134, 217); WarningMsg = nord0 on nord13 (232); DiagnosticError nord11, DiagnosticWarn nord13, DiagnosticInfo nord8, DiagnosticHint nord10 (183-186; the same four for LspDiagnostics at 571-574); SpellBad nord11 and SpellCap nord13 undercurl (145-146); ALEError nord11 and ALEWarning nord13 (552-555); diff DiffAdd nord14, DiffChange nord13, DiffDelete nord11, DiffText nord9 (370-378); GitGutter add nord14, change nord13, delete nord11 (588-591); Search nord1 on nord8 (237); IncSearch nord6 on nord10 (236); Directory nord8 (213); MatchParen nord8 on nord3 (137); Folded nord3 on nord1 (208) — [nord.vim](https://github.com/nordtheme/vim/blob/main/colors/nord.vim)
- nord-vim markdown: markdownBlockquote and markdownCode nord7 (438-439), markdownH1 and markdownLinkText nord8 (444-445), markdownUrl nord4 (446), htmlLink nord4 (402) — [nord.vim](https://github.com/nordtheme/vim/blob/main/colors/nord.vim)
- Comments are deliberately brighter than nord3: nord.vim defines `nord3_gui_bright = "#616E88"` (line 19) and states "The comment color brightness has been increased by 10% by default" referencing nordtheme/vim issue 145 (lines 86-92); nord-emacs does the same, picking the 11th entry of a 21-step brightening ramp, #616e88, and references nordtheme/emacs issue 73 (nord-theme.el lines 50-62, 78, 86) — [nord.vim](https://github.com/nordtheme/vim/blob/main/colors/nord.vim), [nord-theme.el](https://github.com/nordtheme/emacs/blob/main/nord-theme.el). The official docs page still says nord3 for comments. Measured: #616e88 is 3.25:1 on #1e1e1e and 2.43:1 on nord0 (Question 2), so even the brightened comment colour is below 4.5:1.
- nord-vim terminal fallback numbers (lines 33-45): nord12 maps to cterm 11 and nord10 to cterm 12, but see the terminal ports below, where ANSI 11 and 12 are nord13 and nord9, so on a 16-colour Nord terminal nord12 renders as nord13 and nord10 as nord9.

#### nord-emacs (includes email faces)
- Core faces: error nord11 bold (line 149), warning nord13 bold (170), success nord14 (288), font-lock-warning nord13 (166), shadow nord3 (168), comment faces = brightened #616e88 (152-155 via line 86), string nord14, type nord7, function nord8, keyword nord9, preprocessor nord10 bold, escape-glyph nord12 (150) — [nord-theme.el](https://github.com/nordtheme/emacs/blob/main/nord-theme.el)
- Diff: diff-added nord14, diff-changed nord13, diff-removed nord11, refine variants the same (177-191); hunk header nord9, file header nord8, function nord7 — [nord-theme.el](https://github.com/nordtheme/emacs/blob/main/nord-theme.el)
- Links: `link` and `link-visited` are underline only with no colour (228-229); `markdown-link-face` nord8 (431); `org-link` underline only (676); mu4e `mu4e-link-face` underline only (608) — [nord-theme.el](https://github.com/nordtheme/emacs/blob/main/nord-theme.el)
- Email faces, message-mode: message-header-name nord7, message-header-subject nord8, message-header-to and message-header-cc nord9, message-header-newsgroup nord14, message-header-xheader nord13, message-header-other nord4, message-cited-text nord4, message-separator inherits shadow (nord3) (233-242) — [nord-theme.el](https://github.com/nordtheme/emacs/blob/main/nord-theme.el)
- Email faces, mu4e: mu4e-unread-face nord13 bold, mu4e-flagged-face nord13, mu4e-header-marks-face nord9, mu4e-title-face and mu4e-header-key-face nord8 (602-608) — [nord-theme.el](https://github.com/nordtheme/emacs/blob/main/nord-theme.el)
- Multi-level nesting: rainbow-delimiters depth 1-8 = nord7, nord8, nord9, nord10, nord12, nord13, nord14, nord15, unmatched = nord11 (437-445); org headings level 1-4 = nord7 (extra-bold), nord8 (bold), nord9 (semi-bold), nord10 (normal), levels 5-8 repeat level 4 (645-652) — [nord-theme.el](https://github.com/nordtheme/emacs/blob/main/nord-theme.el). nord11 is skipped in the delimiter cycle and reserved for the error case. I found no gnus-cite or notmuch faces in the file (grep returned none).

#### Terminal ports (ANSI mapping)
- Alacritty `normal`: black nord1, red nord11, green nord14, yellow nord13, blue nord9, magenta nord15, cyan nord8, white nord5; `bright`: black nord3, red/green/yellow/blue/magenta same as normal, cyan nord7, white nord6; `dim` block derived values (#94545d dim red, #809575 dim green, #b29e75 dim yellow, #68809a dim blue, #8c738c dim magenta, #6d96a5 dim cyan); foreground nord4, background nord0, selection bg nord3, search match bg nord8 (src/nord.yaml lines 4-51) — [nordtheme/alacritty](https://github.com/nordtheme/alacritty/blob/main/src/nord.yaml)
- Xresources: color0 nord1, color1/9 nord11, color2/10 nord14, color3/11 nord13, color4/12 nord9, color5/13 nord15, color6 nord8, color14 nord7, color7 nord5, color8 nord3, color15 nord6 (lines 27-42) — [nordtheme/xresources](https://github.com/nordtheme/xresources/blob/develop/src/nord)
- GNOME Terminal palette: nord1, nord11, nord14, nord13, nord9, nord15, nord8, nord5 then nord3, nord11, nord14, nord13, nord9, nord15, nord7, nord6 (src/nord.sh line 47) — [nordtheme/gnome-terminal](https://github.com/nordtheme/gnome-terminal/blob/develop/src/nord.sh)
- nord10 and nord12 have no slot in any of the three terminal palettes: the 16 ANSI colours fold Frost into three (nord7, nord8, nord9) and Aurora into four (red/yellow/green/magenta), same three files.

#### VS Code (official, develop branch, themes/nord-color-theme.json)
- UI: textLink.foreground and activeForeground nord8 (299-300); button.background nord8 at 93% alpha, badge and progress bar nord8 (14-17, 231); focusBorder nord1 (6); errorForeground nord11 (132); editorError nord11 (76), editorWarning nord13 (78), editorHint nord13 (48); editorGutter modified nord13, added nord14, deleted nord11 (98-100); inputValidation error nord11, info nord9, warning nord12 (148-153); charts red nord11, blue nord9, yellow nord13, orange nord12, green nord14, purple nord15 (23-28) — [nord-color-theme.json](https://github.com/nordtheme/visual-studio-code/blob/develop/themes/nord-color-theme.json)
- Git decorations: modified nord13, deleted nord11, untracked nord14, conflicting nord10, submodule nord7, ignored nord4 at 40% alpha (133-140). diffEditor inserted text background is nord9 at 20% alpha and removed text background nord11 at 30% (40-41), so the diff editor shows additions in blue, not green (same file).
- Brackets: editorBracketHighlight.foreground1-6 = nord7, nord8, nord9, nord10, nord7, nord8 (82-87) (same file).
- Muted: comments and comment punctuation #616E88; markdown blockquote text #616E88; textBlockQuote.border nord9 on nord1 background (296-297); debugConsole.sourceForeground #616e88 (34) (same file).
- Terminal ANSI identical to the Alacritty mapping (279-294).
- Token colours: markup.inserted nord14, markup.changed nord13, markup.deleted nord11, markup.heading nord8, inline raw nord7, numerics nord15, tags nord9 (same file).

#### Joplin Nord theme (third-party app theme, derived from an older docs snapshot)
- colorError nord11, colorWarn nord12, warningBackgroundColor nord13, colorFaded (less important text) nord4, urlColor nord8, selectedColor nord9, dividerColor nord10, raisedColor nord7, text nord5 on nord0 background — [Joplin themes/nord.ts lines 50-81](https://cdn.jsdelivr.net/npm/@joplin/lib@3.5.1/themes/nord.ts)

#### Nordic GTK theme (third-party GTK3/4 theme by EliverLara, 2,736 GitHub stars at fetch time; not an official nordtheme port)
- Palette variables: $lime nord7, $red nord11, $orange nord12, $yellow nord13, $purple nord15, $blue nord10, $cyan nord10, $teal nord14 (gtk-3.0/_colors.scss lines 16-25); link colour $blue = nord10 (33); text nord4, base nord1, bg nord2 (5-8) — [Nordic gtk-3.0/_colors.scss](https://github.com/EliverLara/Nordic/blob/master/gtk-3.0/_colors.scss)
- Selection and accent: selected_fg nord0, selected_bg = nord9 if accent is blue, otherwise nord7 (27-28); the shipped gtk.scss sets `$accent: 'green'` (so selection is nord7 in that source) — [gtk.scss](https://github.com/EliverLara/Nordic/blob/master/gtk-3.0/gtk.scss)
- Semantic: warning = orange nord12 (darkened 10% in dark), error = red nord11 (darkened 5% in dark), success = $cyan = nord10 (darkened 10% in dark), destructive = red darkened, suggested = selection colour; infobar info = nord7, question = nord10; drop target = teal nord14 (49-53, 73, 76-77) — [Nordic gtk-3.0/_colors.scss](https://github.com/EliverLara/Nordic/blob/master/gtk-3.0/_colors.scss)
- Email client: Geary list rows reuse the selection colours (gtk-3.0/apps/_geary.scss) — [Nordic _geary.scss](https://github.com/EliverLara/Nordic/blob/master/gtk-3.0/apps/_geary.scss)

#### Thunderbird: Nord Hardt (artrz, 10 GitHub stars, active 2026-09), the closest direct analogue
- Hex palette and `nord_between_2_n_9 = #627790` (off-palette) in src/themeConfig.js lines 3-19 — [thunderbird-nord-hardt-theme](https://github.com/artrz/thunderbird-nord-hardt-theme/blob/main/src/themeConfig.js)
- Folder icon colours: inbox nord9, drafts nord15, sent nord7, archive nord13, spam nord11, trash nord3, generic folder #627790 (lines 99-104, 109); template, newsletter, rss, outbox left unset  (same file)
- Thread pane: starred flag nord14, spam/junk nord11, unread nord8 (lines 120-124); folder-pane unread-count text nord8 on nord0, new-count background nord8 (115-117); NEW-mail subject colour in card view nord4 (87)  (same file)
- Row styling in src/styles/colors.scss: unread rows text nord5 (lines 88-90), read rows text #74818e (off-palette, 113-115), unread card dot nord8 (103-105), new-message dot nord14 (108-110), "new" spark icon nord13 (82-85); selected-item colour nord9 (themeConfig.js line 80) — [colors.scss](https://github.com/artrz/thunderbird-nord-hardt-theme/blob/main/src/styles/colors.scss) and themeConfig.js
- Chrome: toolbar and frame nord0, tab line nord8 (line 42), primary colour nord8 (66-67), primary button border nord10 and background nord2 (69-70), hover nord3 (themeConfig.js)
- Local reference (not a port): the current uncommitted local theme maps folder icons inbox nord8, draft nord13, sent nord14, archive nord9, spam nord12, trash nord11, template nord15, newsletter and rss nord7, outbox nord12 through the OKLab rule, `/var/home/glw907/.dotfiles/thunderbird/customChrome.css` lines 108-117 (git status showed the file modified, uncommitted).

#### aerc (styleset `nord` ships in the aerc repository)
- Semantic: error.fg=red, warning.fg=yellow, success.fg=green (ANSI names, so they resolve through the terminal palette to nord11/nord13/nord14 in a Nord terminal); msglist_unread.fg #8fbcbb (nord7); msglist_flagged.fg #a3be8c (nord14) bold; msglist_marked.bg #81a1c1 (nord9); selected bg #394353, border and statusline #49576b, statusline_error #94545d, tab selected bg and dirlist unread/recent fg #64A6B3, tab text #e4e9f0, all off-palette (lines 12-14, 23-48) — [aerc stylesets/nord](https://git.sr.ht/~rjarry/aerc/blob/master/stylesets/nord)
- Viewer: url underline, signature dim, diff_add fg=2 (green), diff_del fg=1 (red), diff_chunk dim, code fg=4 (blue); quote levels: `quote_*.fg=6` (ANSI cyan) with `quote_*.dim=true` then `quote_1.dim=false`, so every nesting level is cyan and only level 1 is full strength (lines 56-70)  (same file)
- `#94545d` equals Alacritty's `dim.red` (nord alacritty/src/nord.yaml line 45), so the aerc styleset borrows a dim-palette colour from the Nord terminal port.

#### neomutt-nord (unofficial, 1 GitHub star; low authority)
- Uses ANSI names only: error brightred; message brightgreen; status white on blue; search yellow; attachment brightmagenta; signature cyan; headers From/To/Cc brightcyan, Subject brightblue, Date brightwhite; index read white, new brightblue, unread brightcyan, flagged yellow, tagged brightmagenta; quoted levels 0-3 = blue, cyan, magenta, brightmagenta (hue cycle); body URLs brightblue; body e-mail addresses magenta — [nord.muttrc lines 4-35](https://github.com/fauzymadani/neomutt-nord/blob/HEAD/nord.muttrc). Resolved through the Nord terminal ports above: brightblue = nord9, brightcyan = nord7, cyan = nord8, blue = nord9, magenta and brightmagenta = nord15, yellow = nord13, brightred = nord11, brightgreen = nord14 (derived, not stated in the file).
- No official nordtheme neomutt/mutt port exists in the organisation's repository list (the org lists vim, emacs, terminals, visual-studio-code, jetbrains, slack, etc.) — [nordtheme GitHub org](https://github.com/nordtheme) (listed via the GitHub API).

#### Firefox
- No official nordtheme Firefox or Thunderbird port exists in the org list above. Third-party Firefox themes found: Bootools/Nord-Firefox-Theme (1 star) uses RGB [139,192,208] = #8bc0d0 (3 off nord8 in red) for tab_line, icons_attention, popup/sidebar/toolbar-field highlight and focus border, nord0 for frame, nord1 for toolbar, nord2 for fields and sidebars — [manifest.json](https://github.com/Bootools/Nord-Firefox-Theme/blob/HEAD/manifest.json)

### Inferences
- Consensus mapping across independent ports: error = nord11, warning/modified = nord13, success/added = nord14, accent/focus/link = nord8, secondary = nord9. That agrees with the official docs and has no contradiction among the official ports; deviations come from third-party GTK/app themes (Nordic: success = nord10, warning = nord12; Joplin: warning = nord12), and VS Code itself uses nord12 for input-validation warnings.
- Muted text is never raw nord3 in the official editor ports; both nord-vim and nord-emacs lighten it 10% to #616e88 and VS Code uses the same value, which implies nord3 is below the legibility the maintainers wanted for text (consistent with the 1.79-2.26:1 raw measurement on dark in Question 2). The Thunderbird theme goes the other way for read mail (#74818e, off-palette) and keeps nord5 for unread.
- Unread/new/flag semantics in the mail-client ports are less uniform: unread is nord7 (aerc) / nord8 (Thunderbird Nord Hardt dot, neomutt brightcyan via nord7) / nord13 bold (mu4e); flagged/starred is nord14 (aerc, Thunderbird Nord Hardt) or nord13 (mu4e, neomutt yellow); "new" is nord14 (Thunderbird dot) or nord13 (spark icon, mu4e unread). There is no consensus, so a mapping is a design decision backed by precedent in both directions; nord13 or nord14 for "flagged" both have precedent.
- Nesting precedents: Frost-only cascades (nord7 to nord10) for headings and the first bracket levels; Aurora joins only in the 8-level delimiter cycle, with nord11 reserved for "unmatched/error"; email quote levels are either one hue with dimming (aerc) or a four-hue cycle (neomutt-nord). Hue cycling for quoted mail would run into the Frost-pair collisions measured in Question 3 (nord8/9/10 and nord9/15 are nearly identical after the theme rule), whereas same-hue dimming conflicts with the theme rule flattening lightness.
- The terminal ports only distinguish three Frost colours and four Aurora colours; nord10 and nord12 are the "free" colours in a 16-colour world, which matches the docs calling nord12 and nord15 rarely used.

### Gaps
- No official or well-known neomutt/mutt Nord port was found; the only one is a 1-star repo (`gh search repos` for mutt/neomutt nord returned only that). The nordtheme org has no Thunderbird or Firefox repo.
- The aerc styleset resolves red/yellow/green through the user's terminal palette, so its actual hex depends on the terminal theme (assumed Nord here).
- A Nord Slack theme exists (nordtheme/slack colors.txt: #2E3440,#3B4252,#88C0D0,#2E3440,#3B4252,#D8DEE9,#A3BE8C,#81A1C1,#2E3440,#D8DEE9), whose positions 7 and 8 (nord14, nord9) would be "active presence" and "mention badge" under Slack's usual field order, but I could not confirm the order from a Slack source, so it is excluded from the findings.
- Dracula/other-palette mail themes and the Nord JetBrains, Xcode, Sublime, Atom and tmux ports were not surveyed; the official VS Code, vim, emacs and terminal ports are the only ones read in full for bracket, diff and comment assignments.
- Nord-gtk beyond Nordic (for example the GNOME "Nordzy" or libadwaita recolours) was not checked.
