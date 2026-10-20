# Reading a single message: header block, quoted chains, signatures, links (Thunderbird 158 styling evidence)

Research date: 2026-10-13. Thunderbird source was read at comm-central tip on that date (not at a 158 release tag, which I could not pin; every file cited below was last changed on or before Sep 2026, so it should match 158 closely, but verify against the 158 tag before relying on a line number). Contrast ratios marked "computed" are my own calculations with the [WCAG relative-luminance formula](https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio), not figures from a source.

---

## 1. Typographic hierarchy for a message header (sender, subject, date, recipients, tags)

### Takeaway
Authoritative guidance converges on a small number of steps: NN/g says no more than 3 type sizes and no more than 3 contrast variations, Apple says to vary weight, size and colour together and to avoid light weights, and Material uses a regular/medium weight pair with a 16/14/12 size ladder. Thunderbird's own header already encodes a hierarchy (bold subject, 0.7-opacity labels), and WCAG 1.4.3 sets the floor (4.5:1) below which "secondary" text must not be dimmed. I found no empirical study that measures how many hierarchy levels readers can actually distinguish; the numbers are design heuristics.

### Cited Findings

**NN/g (visual hierarchy)**
- Hierarchy is built from three levers: colour and contrast, scale, grouping (proximity and common regions). "It's not the actual color of an element that creates the hierarchy, but rather the contrast in value and saturation between the element and the context in which it appears." — [NN/g, Visual Hierarchy in UX: Definition (Gordon, 2021)](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/)
- "Don't use too many contrast variations. Use no more than 3 contrast variations for complex designs. If everything is contrasted, then nothing stands out." — [NN/g](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/)
- "Use no more than 3 sizes — small, medium, and large." Suggested web ranges: 14–16px body, 18–22px subheader, up to 32px header. "Limit how many elements are big to a maximum of 2." — [NN/g](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/)
- Type contrast is a hierarchy device: "Typefaces with heavy weight, like bold, stand out against light-weighted or regular typefaces." Do not rely only on colour for hierarchy (colour blindness). — [NN/g](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/)
- Spacing is a hierarchy device: decreased space between a heading and its content creates the heading-to-content relationship; an element with more space around it is perceived as one group and receives more attention. Borders/backgrounds are a fallback "used sparingly" because they add clutter. The "squint test" (blur 5–10px) checks that the intended hierarchy survives. — [NN/g](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/)

**Apple HIG**
- "Adjust font weight, size, and color as needed to emphasize important information and help people visualize hierarchy." and "Maintain a consistent information hierarchy regardless of the current font size." — [Apple HIG, Typography](https://developer.apple.com/design/human-interface-guidelines/typography) (text read from Apple's published JSON for the page, `developer.apple.com/tutorials/data/design/human-interface-guidelines/typography.json`)
- "In general, avoid light font weights" — prefer Regular, Medium, Semibold or Bold; avoid Ultralight, Thin, Light "which can be difficult to see, especially when text is small." — [Apple HIG, Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- macOS built-in text styles (size/line height in points; emphasised weight): Headline Bold 13/16 (emphasised Heavy); Body Regular 13/16 (Semibold); Callout Regular 12/15; Subheadline Regular 11/14; Footnote Regular 10/13; Caption 1 Regular 10/13 (Medium). The macOS table is the one preceding the tvOS table in the page data, so the platform attribution is by position. — [Apple HIG, Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- Text colour is a four-step ladder on Apple platforms: "Label color — the text of a label containing primary content", secondary label, "Tertiary label color — the text of a label of lesser importance than a secondary label", and "Quaternary label color — … such as watermark text." — [Apple HIG, Color](https://developer.apple.com/design/human-interface-guidelines/color) (page JSON `…/human-interface-guidelines/color.json`)

**Material 3**
- Type tokens (rem; 1rem = 16px): title-medium 1rem / 1.5rem line height, weight medium; title-small 0.875 / 1.25, medium; body-medium 0.875 / 1.25, regular; label-medium 0.75 / 1, medium; body-small 0.75 / 1, regular; label-large 0.875 / 1.25, medium. — [material-web `tokens/versions/v0_192/_md-sys-typescale.scss`](https://github.com/material-components/material-web/blob/main/tokens/versions/v0_192/_md-sys-typescale.scss)

**Contrast floor for de-emphasised text**
- WCAG 1.4.3: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"; large-scale text 3:1; exempt only text that is "part of an inactive user interface component, that are pure decoration, … not visible to anyone", or logotypes. Secondary header text (date, recipients) is real content, so the exemption does not apply. — [WCAG 2.2 Understanding 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)

**What Thunderbird's own header does today (comm-central, Sep 2026)**
- Subject: `#expandedsubjectBox { font-weight: 700; … -webkit-line-clamp: 3; }`. When the "large subject" option is on: `.message-header-large-subject #expandedsubjectBox { font-weight: 500; font-size: 1.35em; line-height: 1.35em; }`. — [mail/themes/shared/mail/messageHeader.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageHeader.css)
- Field labels are dimmed by a single custom property: `--message-header-label-opacity: 0.7;` applied to `.message-header-label` and to `.row-heading:not(#subjectHeading, #fromHeading, #tagsHeading)` (which are also `font-weight: 600; white-space: nowrap`). Subject, From and Tags labels are deliberately exempt from the dimming. — [messageHeader.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageHeader.css)
- Date: `.message-header-datetime { user-select: text; … margin: 0 6px; white-space: nowrap; }` (no weight or colour change of its own). Recipients: `.header-recipient`, `.recipients-list`, with a `:not(:last-child)::after` separator. — [messageHeader.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageHeader.css)
- Header DOM lives in `mail/base/content/msgHdrView.inc.xhtml` (e.g. `<html:div id="headerSubjectSecurityContainer" class="message-header-row">`) and `mail/base/content/widgets/header-fields.js`. — [msgHdrView.inc.xhtml](https://searchfox.org/comm-central/source/mail/base/content/msgHdrView.inc.xhtml), [header-fields.js](https://searchfox.org/comm-central/source/mail/base/content/widgets/header-fields.js)
- The in-body header block used for print/save (`.moz-header-display-name { display: inline; font-weight: bold; }`, `.moz-header-part1/2/3` grey backgrounds) is hidden on screen: `@media screen { .moz-main-header, .moz-main-header + br, .moz-print-only { display: none; } }`. — [mail/themes/shared/mail/messageBody.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageBody.css)

**Computed contrast of the existing opacity steps** (black text on white / white text on #2a2a2e; backgrounds are my assumption)
- opacity 0.7 (header labels): 8.45:1 light, 7.78:1 dark. opacity 0.6 (signatures): 5.74:1 light, 6.16:1 dark. For black on white, 4.5:1 is reached at about opacity 0.55 (4.74:1); opacity 0.5 gives 3.95:1 and fails. (computed)

### Inferences
- A defensible three-step header ladder that matches NN/g's limits and Thunderbird's existing tokens: (1) subject: largest and boldest (HIG Headline/Material title-medium analogue, e.g. 1.15–1.35em, weight 600–700); (2) sender name: body size, medium/semibold weight, full-contrast colour; (3) date, recipients, labels: body-small size or body size at regular weight, dimmed by colour/opacity. Three sizes, two weights, and three text-colour steps stays inside the NN/g "3 and 3" limits.
- Because the label dimming is one custom property (`--message-header-label-opacity`), a designer can retune the whole secondary tier in userChrome.css without selector surgery; the floor is about 0.55 for black-on-white text, so 0.6–0.7 is the safe band. Prefer a computed colour (e.g. a mid-grey chosen to pass 4.5:1) over opacity if the header sits on a tinted background, because opacity contrast depends on whatever is behind it.
- Weight and colour steps are cheaper in pixels than size steps in a dense header; HIG's advice to vary all three "as needed" supports using size only once (subject) and weight/colour for the rest.

### Gaps
- No empirical study (eye-tracking or just-noticeable-difference) of how many weight, size or contrast steps readers distinguish was found; NN/g's "3" figures and Apple's four label colours are guidance, not measured thresholds.
- No published Apple Mail, Gmail or Outlook header type specs were found (Apple's Mail header sizes are not in the HIG). Fastmail's and Gmail's header hierarchies were not documented.
- I did not trace which header rows use `--message-header-label-opacity` beyond the selectors listed above (the Subject, From and Tags headings are explicitly exempt; date and recipient text were not checked for dimming).

---

## 2. Quoted reply chains: how clients distinguish quote levels, and the usability evidence

### Takeaway
Every client that signals depth does it with a left bar or colour per level, usually only 4–5 distinct steps (Thunderbird 5 bar colours, aerc 4 levels plus "x", Apple Mail a user-configurable set, mutt/neomutt unlimited but cycled). Gmail and Mutt also offer collapsing. Thunderbird in 2026 colours the bar by DOM nesting depth and, since Bug 2018015, forces the quoted text itself to the highlight blue with `!important`. I found no controlled usability study on colouring or reading nested quotes.

### Cited Findings

**Thunderbird (messageQuotes.css, shared by message pane and composer)**
- Verbatim rules (comm-central tip, last changed by changeset 734e7f72f685 on 2026-02-27):
  ```css
  body blockquote[type="cite"] {
    margin-block: 1ex;
    margin-inline: 0;
    padding: 0.4ex 1ex;
    color: var(--color-text-highlight) !important; /* override toolkit colors */
    border-inline-start: 2px solid rgb(114, 159, 207); /* Sky Blue 1 */
  }

  blockquote[type="cite"] {
    & & {
      border-inline-start-color: rgb(173, 127, 168); /* Plum 1 */
      & & {
        border-inline-start-color: rgb(138, 226, 52); /* Chameleon 1 */
        & & {
          border-inline-start-color: rgb(252, 175, 62); /* Orange 1 */
          & & {
            border-inline-start-color: rgb(233, 185, 110); /* Chocolate 1 */
          }
        }
      }
    }
  }
  ```
  The file's own comment: "Colorize block quote borders. We only go 5 levels deep." — [mail/themes/shared/mail/messageQuotes.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageQuotes.css); change history via [hg json-log](https://hg.mozilla.org/comm-central/json-log/tip/mail/themes/shared/mail/messageQuotes.css)
- `--color-text-highlight` is `light-dark(#1373d9, #58c9ff)` (`--color-text-highlight-light: #1373d9; --color-text-highlight-dark: #58c9ff;`). — [mail/themes/shared/mail/colors.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/colors.css)
- The `color … !important` line was added by Bug 2018015 "Override the toolkit color for links and blockquotes" (regression "dark mode link colors regressed in 148.0b6"; target milestone 150, uplift approved to beta 149). — [Bug 2018015](https://bugzilla.mozilla.org/show_bug.cgi?id=2018015), [changeset 734e7f72f685](https://hg.mozilla.org/comm-central/rev/734e7f72f685). It is therefore present in 158.
- The same file also sets `body { line-height: initial !important; }` ("workaround for MS Outlook mails where the line-height is set to 0") and dims signatures (see section 5). — [messageQuotes.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageQuotes.css)
- Bar colours labelled in the source (Tango-palette names). Computed contrast of each bar colour against white: Sky Blue 1 2.77:1, Plum 1 3.29:1, Chameleon 1 1.61:1, Orange 1 1.85:1, Chocolate 1 1.81:1; against #2a2a2e: 5.16, 4.34, 8.86, 7.72, 7.92:1. (computed)
- Prefs (defaults from source): `mail.quoted_graphical` true ("Use HTML-style quoting for displaying plain text"); `mail.quoted_style` 0 plain / 1 bold / 2 italic / 3 bolditalic; `mail.quoted_size` 0 normal / 1 big / 2 small; `mail.quoteasblock` true ("Use HTML-style quoting for quoting plain text"). — [mail/app/StaticPrefList.yaml](https://searchfox.org/comm-central/source/mail/app/StaticPrefList.yaml). `mail.citation_color` default `#007cff` (`#000000` in SeaMonkey builds). — [mailnews/mailnews.js](https://searchfox.org/comm-central/source/mailnews/mailnews.js)
- How the prefs reach the page: the plain-text converter writes them as an inline `style` on each `<blockquote type=cite>` (details in section 4). — [mailnews/mime/src/mimetpla.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpla.cpp)
- Graphical vs literal quoting for plain text is a CSS switch on the wrapper: `.moz-text-plain[graphical-quote="false"] blockquote { border-style: none; padding: 0; }` and `.moz-text-plain[graphical-quote="true"] .moz-txt-citetags { display: none; }`. macOS theme override: `&[graphical-quote="true"] blockquote { margin: inherit; border-width: 2px; border-color: gray; }`. — [messageBody.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageBody.css), [osx/mail/messageBody.css](https://searchfox.org/comm-central/source/mail/themes/osx/mail/messageBody.css)
- Thunderbird history: Bug 1627748 (fixed in 77) is "Message pane: when prefers-color-scheme: dark is set use the approriate colours"; its shared-stylesheet work is why the composer and message pane use the same quote rules. Bug 1639249 then disabled the dark message pane ("until we have a solution for incorrect CSS in messages"; the dark `body`/`span[_moz_quote]` rules are commented out in messageQuotes.css). Today the dark styles live in messageBody.css behind `@media (prefers-color-scheme: dark) and -moz-pref("mail.dark-reader.enabled")`. — [Bug 1627748](https://bugzilla.mozilla.org/show_bug.cgi?id=1627748), [messageQuotes.css history](https://hg.mozilla.org/comm-central/json-log/tip/mail/themes/shared/mail/messageQuotes.css), [messageBody.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageBody.css)

**Apple Mail**
- Mail on Mac: Settings > Fonts & Colors has "Color quoted text — Show quoted text in colors"; "To change the colors used, click the color pop-up menu for a level, then choose a different color, or choose Other for additional choices." — [Apple Support, Mail Fonts & Colors](https://support.apple.com/guide/mail/cpmlpreffont)
- The coloured vertical bars remain when "Color quoted text" is unchecked (only the text colour reverts); each added level adds a bar; iOS offers Increase/Decrease quote level but no colour customisation. — [iDownloadBlog, block quote levels in Mail](https://www.idownloadblog.com/2021/04/02/block-quote-levels-mail/)
- Default colours: Laptop Mag says the default is purple and advises "Don't reuse colors" — [Laptop Mag](https://www.laptopmag.com/au/articles/change-default-fonts-apple-mail) (undated; likely older macOS); an Apple Community user asking for "the original default colors, all three levels" believed level 1 is blue and was unsure of the rest, unanswered in the snippet I could read — [Apple Community thread 255773159](https://origin-discussions2-us-dr-prz.apple.com/thread/255773159) (search-result snippet only, page not fetched).

**Gmail**
- Gmail collapses text it recognises as already earlier in the thread behind a three-dot ellipsis; hover tooltip "Show trimmed content"; an identical repeated signature is trimmed too. Android app 6.11 (Nov 2016) adopted the same ellipsis. — [Allegheny College, Show Trimmed Content in Gmail](https://sites.allegheny.edu/library/?p=16642), [Labnol, Gmail trims signatures](https://labnol.org/internet/gmail-trimming-signature/28762), [Android Police](https://www.androidpolice.com/2016/11/18/gmail-v6-11-changes-the-interface-for-quoted-text-in-replies-apk-download/). All third-party; no Google help page found.
- Gmail's own quote bar is a 1px `#ccc` left border (markup in section 3).

**Outlook**
- Microsoft's classic Outlook options for replies/forwards: "Include original message text" (default), "Include and indent original message", "Prefix each line of the original message", "Attach original message", "Do not include original message" (not for forwards). — [Microsoft Support, Change how the original message appears in replies and forwards](https://support.microsoft.com/en-us/office/change-how-the-original-message-appears-in-replies-and-forwards-1207f4ea-f7cf-4cdf-9298-5982fa2e5e2f). The page does not mention a blue bar; a Microsoft Q&A answer (snippet only) says the prefix option indents and adds a blue vertical bar in Classic Outlook, and that "Preface comments with" is unsupported in new Outlook — [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/4600158/how-can-i-prefix-answers-in-reply-in-new-version-o).

**mutt / neomutt**
- Objects: `quoted` ("text matching $quote_regexp in the body of a message"), `quoted1, quoted2, …, quotedN (higher levels of quoting)`, plus `signature`, `hdrdefault`, `markers`. — [Mutt manual source (manual.xml.head)](https://gitlab.com/muttmua/mutt/-/blob/master/doc/manual.xml.head)
- NeoMutt documents `quoted` through `quoted9` ("1 level deeper quoted text, e.g. > > text") with examples `color quoted brightblue default`, `color quoted1 brightgreen default`, `color quoted2 yellow default`; no default colours are listed. — [NeoMutt configuration guide](https://neomutt.org/guide/configuration)
- Cycling is in code: `class->color = ColorQuote[class->index % ColorQuoteUsed];`; levels you leave undefined inherit the `quoted` colour (`ColorQuote[q_level] = ColorDefs[MT_COLOR_QUOTED]`). — [mutt `pager.c`](https://gitlab.com/muttmua/mutt/-/blob/master/pager.c), [mutt `color.c`](https://gitlab.com/muttmua/mutt/-/blob/master/color.c)
- `<toggle-quoted>` (default `T`) toggles display of quoted material, "particularly useful when being interested in just the response and there is a large amount of quoted text in the way." — [Mutt manual source](https://gitlab.com/muttmua/mutt/-/blob/master/doc/manual.xml.head)

**aerc**
- The built-in `colorize` filter styles quote levels with `[viewer]` style objects `quote_1`…`quote_4` and `quote_x` ("Above fourth level quoted text"). Shipped defaults: `quote_1.fg = 6` (palette cyan), `quote_2.fg = 4` (blue), `quote_3.fg = 6` + `dim`, `quote_4.fg = 4` + `dim`, `quote_x.fg = 5` (magenta) + `dim`. — [aerc-stylesets(7) source](https://git.sr.ht/~rjarry/aerc/tree/master/item/doc/aerc-stylesets.7.scd), [filters/colorize.c](https://github.com/rjarry/aerc/blob/master/filters/colorize.c)
- Level is counted from leading `>` characters, with one optional space eaten after each: `while (in[q] == '>') { level++; q++; if (in[q] == ' ') q++; }`. — [colorize.c `quote()`](https://github.com/rjarry/aerc/blob/master/filters/colorize.c)
- Pattern: alternate two hues (cyan/blue) and use `dim` for depth 3+, rather than adding hues.

**Standards / convention**
- RFC 3676 §4.5: "the canonical quote indicator (or quote mark) is one or more close angle bracket (">") characters"; "The number of ">" characters at the start of the line specifies the quote depth." — [RFC 3676](https://datatracker.ietf.org/doc/html/rfc3676#section-4.5)
- Wikipedia: RFC 3676 treats `>>` and `> >` as different depths though most clients treat them as equal; "Some email interfaces recognize this convention and automatically render each level in a different color" (uncited there); the article cites no usability studies. — [Wikipedia, Posting style](https://en.wikipedia.org/wiki/Posting_style)
- An active IETF individual draft (July 2026) states quoting behaviour "is largely unstandardized and differs between mail clients" (where new text goes, how quotes are formatted, whether attribution lines appear) and proposes machine-readable `data-source-id` / `data-id` markers; its examples use `<blockquote type="cite">` and `<hr>`. MUA guidance sections are still TODO. — [draft-ietf-sml-structured-quoted-content-00](https://www.ietf.org/archive/id/draft-ietf-sml-structured-quoted-content-00.html)

**Usability research (weak)**
- No controlled study on colour-coding or reading nested quotes was found. Closest: a CMU dissertation by Susan Harness Regli on how email context representation affects comprehension (abstract: comprehension is likely degraded when related replies are far apart or contexts are interspersed) — [CMU abstract](https://www.cmu.edu/dietrich/english/academic-programs/phd-rhetoric/phd-rhetoric-dissertation_abstracts/Susan%20Regli.html) (abstract only, from a search snippet; quoting is not its subject). W3C WAI and WebAIM list posts on quoting for screen-reader users are opinion and anecdote, not studies — [W3C WAI-IG post](https://lists.w3.org/Archives/Public/w3c-wai-ig/2009OctDec/0020.html).

### Inferences
- Pattern across all clients: depth is signalled by a left bar or hue, rarely more than 4–5 steps, and clients with no collapse rely on colour to let readers skip quotes; Gmail and mutt provide collapse instead or as well.
- Thunderbird's five bar colours span a very wide lightness range on white (computed 1.6:1 to 3.3:1); only Plum 1 clears 3:1. If bars are meant to count as "graphical objects required to understand the content" under WCAG 1.4.11 ([3:1 against adjacent colours](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)), most fail on a white page; if they are treated as redundant to indentation and the attribution line, they are exempt. This is a judgement call, not a ruling.
- The aerc and mutt approach (alternate two hues, then dim) suggests a restrained palette: 2 alternating hues plus lightness reduction would stay within NN/g's "3 contrast variations".
- Since Bug 2018015, Thunderbird renders quoted text itself in the highlight blue in both HTML and plain-text mail, which also overrides the inline `style="color: #007cff;"` that `mail.citation_color` produces (author-origin `!important` beats an inline non-important declaration). I did not run Thunderbird to confirm the visual result; treat as strong inference from the source.
- Quoted-text colour and link colour now share the same token in dark mode (`#58c9ff`), so quotes and links are not distinguishable by colour there (see section 6).

### Gaps
- Apple Mail's default colours per level are not documented by Apple; sources conflict (purple vs "blue for level 1"). The only way to settle it is to open Mail > Settings > Fonts & Colors.
- Gmail web's quote-collapse behaviour has no official Google documentation found; Outlook's blue-bar behaviour is only in a forum answer snippet.
- No data on how new Outlook or OWA show quote levels visually beyond the markup in section 3.
- No peer-reviewed usability evidence on quote colouring, bar width, or maximum useful depth.

---

## 3. HTML markup that marks quoted text in major clients, and what can be targeted safely

### Takeaway
Only some clients wrap the quote in a dedicated element. Thunderbird, Apple Mail (WebKit), Fastmail use `<blockquote type="cite">`; Gmail uses `div.gmail_quote` around `blockquote.gmail_quote` with inline border styles; Yahoo wraps in `div.yahoo_quoted`; Proton uses a `.protonmail_quote` marker; Outlook has no wrapper at all (an `<hr>` plus `#divRplyFwdMsg` header, or an inline `border-top` div, followed by loose siblings). A left bar can only be added safely where there is a wrapper, and where an inline border already exists, the safe move is to override the border colour only.

### Cited Findings

**Thunderbird** (also the `cite=` URL and `moz-cite-prefix` attribution)
- Reply markup in a real Thunderbird HTML reply: `<div class="moz-cite-prefix">On 26.06.2014 14:41, Alexander L wrote:<br></div>` followed by `<blockquote` … `cite="mid:CA+jEWTKBU6qc4OnH5m=-0sfwkAzZhcy0rd+ean2W6bFUVXaO7A@mail.gmail.com"` … `type="cite">`. (2014 test fixture, so old, but Thunderbird still emits `moz-cite-prefix`, which Proton's detector still lists). — [talon `thunderbird.html`](https://github.com/mailgun/talon/blob/master/tests/fixtures/html_replies/thunderbird.html)

**Apple Mail / WebKit**
- WebKit's editing code identifies a "mail blockquote" as a `blockquote` element whose `type` attribute equals `cite`:
  ```cpp
  bool isMailBlockquote(const Node& node)
  {
      auto* htmlElement = dynamicDowncast<HTMLElement>(node);
      if (!htmlElement || !htmlElement->hasTagName(blockquoteTag))
          return false;
      return htmlElement->attributeWithoutSynchronization(typeAttr) == "cite"_s;
  }
  ```
  — [WebKit `Source/WebCore/editing/Editing.cpp`](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/editing/Editing.cpp). WebKit's own UA sheet has only `blockquote { display: block; margin-block: 1__qem 1em; margin-inline: 40px; }` and no `type="cite"` rule, so Apple Mail's bars and colours come from Mail itself, not WebKit defaults. — [WebKit `html.css`](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/html.css)
- I could not obtain a literal Apple Mail reply sample; WebKit editing also leaves `<br class="Apple-interchange-newline">` artefacts (a TinyMCE changelog entry: "WebKit/Blink sometimes produced br elements with the Apple-interchange-newline class"). — [TinyMCE changelog as mirrored in lainchan](https://github.com/lainchan/lainchan/blob/HEAD/js/tinymce/changelog.txt) (weak, indirect; a fork copy).

**Gmail**
- Current Gmail reply (Sep 2026 sample, nested):
  ```html
  <div class="gmail_quote gmail_quote_container"><div dir="ltr" class="gmail_attr">On Fri, Sep 18, 2026, 9:15 AM [name redacted] wrote:<br></div><blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex">
  ```
  A nested reply repeats `<div class="gmail_quote">` (no `_container`) and `<blockquote class="gmail_quote" style="…">` inside. — [GitHub: grqz/grqz `email/0028.md`](https://github.com/grqz/grqz/blob/HEAD/email/0028.md)
- 2014 sample, same inline style on the blockquote: `<div class="gmail_extra"><br><br><div class="gmail_quote">On Thu, Jun 26, 2014 at 2:14 PM, Alexander L <span dir="ltr">…</span> wrote:<br><blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex">`. — [talon `gmail.html`](https://github.com/mailgun/talon/blob/master/tests/fixtures/html_replies/gmail.html)
- Detection logic in clients: Proton uses `.gmail_quote:not(.gmail_quote_container)` and `div.gmail_extra`, with a comment that "Gmail creates both div.gmail_quote and blockquote.gmail_quote. The div version marks text but does not cause indentation, but both should be considered quoted text", and `gmail_quote_container` is "Gmail's compose-time wrapper for forwards". Mailspring queries `.gmail_quote`. Talon checks `div.gmail_quote`, `.gmail_attr`, `blockquote.gmail_quote`. — [Proton `messageBlockquote.ts`](https://github.com/ProtonMail/WebClients/blob/main/applications/mail/src/app/helpers/message/messageBlockquote.ts), [Mailspring `quoted-html-transformer.ts`](https://github.com/Foundry376/Mailspring/blob/master/app/src/services/quoted-html-transformer.ts), [talon `html_quotations.py`](https://github.com/mailgun/talon/blob/master/talon/html_quotations.py)

**Outlook (desktop Word engine, classic)**
- Outlook 2007 separator: `<div style='border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0cm 0cm 0cm'>`; Outlook 2010 header is `<p class="MsoNormal"><b><span style=…>From:</span></b>…<b>Sent:</b> …<b>Subject:</b> …</p>` with no enclosing wrapper; Outlook 2003 uses `<hr size=3 width="100%" align=center tabindex=-1>`. — [talon fixtures `ms_outlook_2007.html`, `ms_outlook_2010.html`, `ms_outlook_2003.html`](https://github.com/mailgun/talon/tree/master/tests/fixtures/html_replies)
- Talon's matcher: `"border:none; ?border-top:solid #(E1E1E1|B5C4DF) 1.0pt; ?"` then `"padding:3.0pt 0(in|cm) 0(in|cm) 0(in|cm)"`; Windows Mail variant `"padding-top: 5px; border-top-color: rgb(229, 229, 229); border-top-width: 1px; border-top-style: solid;"`; `OLK_SRC_BODY_SECTION` id; the old `hr[@size='3' and @width='100%' and @align='center']`. — [talon `html_quotations.py`](https://github.com/mailgun/talon/blob/master/talon/html_quotations.py)
- The classes are Word styles from a `<style>` block in `<head>`: `p.MsoNormal, li.MsoNormal, div.MsoNormal { margin:0in; margin-bottom:.0001pt; font-size:12.0pt; … }`, `a:link, span.MsoHyperlink { color:blue; text-decoration:underline; }`. — [talon `ms_outlook_2010.html`](https://github.com/mailgun/talon/blob/master/tests/fixtures/html_replies/ms_outlook_2010.html)

**Outlook on the web / new Outlook**
- Literal OWA reply, quoted-printable decoded: `<hr tabindex="-1" style="display:inline-block; width:98%">` immediately followed by `<div id="divRplyFwdMsg" dir="ltr"><font face="Calibri, sans-serif" color="#000000" style="font-size:11pt"><b>From:</b> … <br><b>Sent:</b> …`. — observed in a real forwarded message in a public repo text file ([USNavalResearchLaboratory/TrackerComponentLibrary `Terrain/data/Earth2014 License.txt`](https://github.com/USNavalResearchLaboratory/TrackerComponentLibrary/blob/HEAD/Terrain/data/Earth2014%20License.txt)); personal details not reproduced.
- Odoo's mail-quote logic confirms the structure: `is_outlook_auto_message = 'appendonsend' in el_id`, `is_outlook_reply_quote = 'divRplyFwdMsg' in el_id`, with the comment "outlook reply wrapper is preceded with <hr> and a div containing recipient info"; the element after it holds the quoted body. — [odoo `odoo/tools/mail.py`](https://github.com/odoo/odoo/blob/master/odoo/tools/mail.py)
- `#appendonsend` is "an empty marker sitting before the quoted chain" (comment in the Rowboat client's quote splitter, whose boundary selector list is `'#divRplyFwdMsg'` ("Outlook on the web / "new Outlook""), `'#appendonsend'`, `'.moz-cite-prefix'`). — [rowboat `email-quotes.ts`](https://github.com/rowboatlabs/rowboat/blob/HEAD/apps/x/apps/renderer/src/lib/email-quotes.ts). Other marker lists: `id="divRplyFwdMsg"`, `id="appendonsend"`, `id="OLK_SRC_BODY_SECTION"`, `class="OutlookMessageHeader"`, `class="yahoo_quoted"` — [libredesk `quotedContent.js`](https://github.com/abhinavxd/libredesk/blob/HEAD/frontend/shared-ui/utils/quotedContent.js); `'div[id$="divRplyFwdMsg"]'`, `'div[id$="appendonsend"]'` — [inbox-zero `split-email-content.client.ts`](https://github.com/elie222/inbox-zero/blob/HEAD/apps/web/utils/email/split-email-content.client.ts). Proton also lists `div[id="mail-editor-reference-message-container"]`.
- Microsoft does not document these ids; `appendonsend` in Microsoft docs is the unrelated Office.js `appendOnSendAsync` API. — [Office.Body interface](https://learn.microsoft.com/en-us/javascript/api/outlook/office.body)

**Yahoo / AOL**
- `<div class=yahoo_quoted id=yahoo_quoted_0033794750><div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:13px;color:#26282a"><div>On Tuesday, June 4, 2019, 5:41:43 PM PDT, John Smith &lt;jsmith@example.com> wrote:</div>…` — the attribution line is inside the wrapper. — [talon `yahoo.html`](https://github.com/mailgun/talon/blob/master/tests/fixtures/html_replies/yahoo.html)
- Mailspring: "Both Yahoo and AOL wrap their quotes in divs with classes that contain the text yahoo_quoted" (`[class*="yahoo_quoted"]`). Proton adds `blockquote.iosymail` for Yahoo iOS. — [Mailspring](https://github.com/Foundry376/Mailspring/blob/master/app/src/services/quoted-html-transformer.ts), [Proton](https://github.com/ProtonMail/WebClients/blob/main/applications/mail/src/app/helpers/message/messageBlockquote.ts)

**Fastmail**
- A third-party Fastmail CLI that builds replies to match the web client uses, with the code comment "Match Fastmail's exact format with #qt styles": `<!DOCTYPE html><html><head><title></title></head><body>%s<div><br></div><div>%s</div><blockquote type="cite" id="qt">%s</blockquote><div><br></div></body></html>`. — [marckohlbrugge/fastmail-cli `internal/jmap/draft.go`](https://github.com/marckohlbrugge/fastmail-cli/blob/main/internal/jmap/draft.go)
- Corroboration from 2020 mailing-list archives of Fastmail-style mail: `On Fri, Jan 17, 2020, at 3:38 PM, Dave Horsfall wrote:<br></div><blockquote type="cite" id="qt">` and a head style `p.MsoNormal,p.MsoNoSpacing{margin:0}`. — [GitHub code search hits: ewe2/tuhs](https://github.com/ewe2/tuhs), [40ants/lisp-hug docs/2020/15267.html](https://github.com/40ants/lisp-hug/blob/master/docs/2020/15267.html) (indirect; the sender client is inferred from the date format and `#qt`).

**Proton**
- `.protonmail_quote` is the first entry in Proton's own quote detector. I could not confirm which element carries it or its inline styles (a web search for the exact markup returned nothing). — [Proton `messageBlockquote.ts`](https://github.com/ProtonMail/WebClients/blob/main/applications/mail/src/app/helpers/message/messageBlockquote.ts)

**Others in Proton's list** (for coverage): `.tutanota_quote`, `.zmail_extra` (Zoho), `.skiff_quote`, `blockquote[data-skiff-mail]`, `hr[id=replySplit]`, `blockquote[id=isReplyContent]`, `div[id=isForwardContent]`, `[name="quote"]` (GMX), and generic `blockquote[type="cite"]`. Talon also handles Zimbra `//hr[@data-marker="__DIVIDER__"]` and the generic "last non-nested `blockquote` not `gmail_quote`". — same Proton file and [talon](https://github.com/mailgun/talon/blob/master/talon/html_quotations.py)

**Plain-text**
- Plain-text "> " quoting with `format=flowed` is handled by the client, not by markup; Thunderbird turns both into nested `<blockquote type=cite>` (section 4). RFC 3676 §4.5 as quoted in section 2.

**Collisions with Thunderbird's own sheet and sender CSS**
- `body blockquote[type="cite"]` applies to every HTML message blockquote with `type="cite"`, so Fastmail/Apple/Thunderbird-sent quotes receive TB's 2px bar, `padding: 0.4ex 1ex`, and forced text colour; Gmail's `blockquote.gmail_quote` has no `type` attribute and is untouched. — [messageQuotes.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageQuotes.css)
- Documented collision: Slack's `blockquote type="cite"` carried a sender-set "purple-coloured 1px border"; "removing `type="cite"` from blockquote removes that border", and bullet lists inside the quote showed a misaligned bar (Bug 1817295, fixed by "Add removed but needed blockquote styling to Thunderbird styles"). — [Bug 1817295](https://bugzilla.mozilla.org/show_bug.cgi?id=1817295)
- Cascade origins: `userContent.css` is loaded as a **User**-origin sheet (`LoadSheetFile(contentFile, StyleOrigin::User)`) and only when `toolkit.legacyUserProfileCustomizations.stylesheets` is true (default false; Geoff's `~/.dotfiles/thunderbird/user.js` sets it). — [GlobalStyleSheetCache.cpp](https://searchfox.org/mozilla-central/source/layout/style/GlobalStyleSheetCache.cpp), [modules/libpref/init/all.js](https://searchfox.org/mozilla-central/source/modules/libpref/init/all.js)
- Cascade order (CSS Cascade 5 §6.1): transition; important user-agent; important user; important author; animation; normal author; normal user; normal user-agent. "Declarations from origins earlier in this list win over declarations from later origins." — [CSS Cascade Level 5](https://www.w3.org/TR/css-cascade-5/#cascade-sort). So a normal declaration in userContent.css loses to any normal author rule (a sender's `<style>`, a sender's inline `style=""`, and Thunderbird's linked messageBody.css/messageQuotes.css), while an `!important` user declaration beats all normal and important author declarations.
- The message document links its sheet as `<link rel="important stylesheet" href="chrome://messagebody/skin/messageBody.css">` (which `@import`s messageQuotes.css and colors.css). — [nsMimeHtmlEmitter.cpp](https://searchfox.org/comm-central/source/mailnews/mime/emitters/nsMimeHtmlEmitter.cpp), [messageBody.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageBody.css)
- Thunderbird wraps HTML messages in `<div class="moz-text-html" lang="…">` and its own source comment says "Users can configure their HTML display via CSS for .moz-text-html." — [mailnews/mime/src/mimethtm.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimethtm.cpp)

### Inferences
- **Safe to target (wrapper exists, geometry already defined):** `blockquote[type="cite"]` (Thunderbird, Apple, Fastmail; TB already draws a bar), `blockquote.gmail_quote`, `div.yahoo_quoted`/`[class*="yahoo_quoted"]` and `blockquote.iosymail`, `.protonmail_quote`. Nested level for the HTML clients is best counted as nested `blockquote` descendants (`blockquote blockquote …`); Gmail's extra `div.gmail_quote` wrapper is not a level, so count only `blockquote.gmail_quote`.
- **How TB's per-level rules behave:** the source uses CSS nesting, so `& &` should expand to a descendant combinator of two `blockquote[type="cite"]` (inference from CSS Nesting semantics, not verified in a running Thunderbird). The level colour is therefore chosen by DOM nesting depth of `blockquote[type="cite"]` elements, and each deeper rule has higher specificity than the base `body blockquote[type="cite"]` rule (compare (0,2,2) and (0,3,3) to (0,1,2), computed by hand).
- **Gmail's `gmail_quote_container` nuance:** Proton's comment calls it "Gmail's compose-time wrapper for forwards", but the Sep 2026 sample above carries `gmail_quote gmail_quote_container` on an ordinary reply, so do not treat the class as forward-only.
- **Colour-only override rule of thumb:** where the sender already draws a border (Gmail: `border-left:1px #ccc solid`), override only `border-left-color` (or `border-inline-start-color`) with `!important` in userContent.css; do not change width, padding or margin. Colour changes cannot reflow a sender's layout, and the user-origin `!important` beats an inline normal declaration. Setting `border-left` shorthand, padding or margin on someone else's blockquote risks shifting layout and double borders.
- **Do not border `div.gmail_quote`, `div.yahoo_quoted` or `.moz-cite-prefix`:** these wrap or contain the attribution line (`gmail_attr`, "On … wrote:"), so a bar would span the attribution and double up with the inner `blockquote.gmail_quote` bar.
- **Outlook cannot be barred by CSS:** the quote is not wrapped (an `<hr>` or inline `border-top` div, a `#divRplyFwdMsg` header, then sibling paragraphs). Only the separator can be restyled (`hr[tabindex="-1"]`, `#divRplyFwdMsg`), and `.MsoNormal` is every paragraph of the body, so selecting it is unsafe. The inline `border-top:solid #E1E1E1 1.0pt` is also very low contrast (computed 1.31:1 on white), so a separator recolour with `!important` is a safe, cosmetic-only improvement.
- **Thunderbird already owns the geometry for `type="cite"`**, so adding a bar to those costs nothing in layout; the per-level colour is a pure `border-inline-start-color` retune. Because messageQuotes.css is author-origin, userContent.css must use `!important` on every property it wants to change (including `border-inline-start-color` per nesting level; important user declarations ignore specificity versus author ones, but ordering among several user rules still follows specificity and source order).
- Scope HTML-mail rules under `.moz-text-html` and plain-text rules under `.moz-text-plain` / `.moz-text-flowed` to keep each layer's behaviour independent.

### Gaps
- No literal Apple Mail reply HTML sample was obtained; Apple Mail markup is inferred from WebKit's `isMailBlockquote`, Proton's `blockquote[type="cite"]` selector, and the IETF draft's examples.
- Proton's element and inline styles for `.protonmail_quote` are unconfirmed.
- Fastmail's markup is verified only through a third-party CLI and mailing-list archives; check once on a real Fastmail-sent message in Geoff's own mailbox (view source) before relying on `#qt`.
- Whether the `rel="important stylesheet"` token changes the cascade origin of messageBody.css in Gecko was not investigated; the author-origin conclusion is an inference. A one-line test in userContent.css (`blockquote[type="cite"]{border-inline-start-color:red}` with and without `!important`) settles it.
- Outlook for Mac and the new Outlook's exact markup beyond `divRplyFwdMsg`/`appendonsend` markers was not captured. No Google, Microsoft, Yahoo or Fastmail document describes these class names; all evidence is from open-source parsers and sample messages. The Gmail `gmail_quote` markup in the 2014 fixture is old; the Sep 2026 sample shows it unchanged.

---

## 4. How Thunderbird renders plain-text mail (source map)

### Takeaway
Thunderbird's MIME layer converts plain-text mail to HTML on the fly: wrapper classes `moz-text-plain` (fixed) or `moz-text-flowed` (format=flowed), a `<pre wrap class="moz-quote-pre">` body, one nested `<blockquote type=cite>` per `>`, optional `<span class="moz-txt-citetags">` carrying the literal `>` characters (hidden by CSS), and `<div class="moz-txt-sig">` from the `-- ` line to the end. HTML mail is wrapped in `div.moz-text-html`. Flowed and fixed use different converters, and only the fixed one sets `graphical-quote`.

### Cited Findings
- Source files: `mailnews/mime/src/mimetpla.cpp` (text/plain fixed), `mailnews/mime/src/mimetpfl.cpp` (text/plain; format=flowed), `mailnews/mime/src/mimethtm.cpp` (text/html), `netwerk/streamconv/converters/mozTXTToHTMLConv.cpp` (linkification and `*bold*` etc., in mozilla-central), CSS in `mail/themes/shared/mail/messageBody.css` and `messageQuotes.css`. — [mimetpla.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpla.cpp), [mimetpfl.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpfl.cpp), [mimethtm.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimethtm.cpp), [mozTXTToHTMLConv.cpp](https://searchfox.org/mozilla-central/source/netwerk/streamconv/converters/mozTXTToHTMLConv.cpp)
- **Fixed plain text wrapper** (`MimeInlineTextPlain_parse_begin`): `<div class="moz-text-plain"` plus ` wrap=true` or ` wrap=false`, ` graphical-quote=true` or ` graphical-quote=false`, optional `style="<font>"` and `lang`, closed with `><pre wrap class="moz-quote-pre">\n`. — [mimetpla.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpla.cpp)
- **Quote nesting** (`MimeInlineTextPlain_parse_line`): when the cite level rises, `</pre>` is written, then one `<blockquote type=cite>` per added level, then a new `<pre wrap class="moz-quote-pre">`; when it falls, `</pre>`, `</blockquote>` × n, new `<pre>`:
  ```cpp
  if (!plainHTML && !style.IsEmpty()) {
    prefaceResultStr += "<blockquote type=cite style=\"";
    prefaceResultStr += style;
    prefaceResultStr += "\">";
  } else
    prefaceResultStr += "<blockquote type=cite>";
  ```
  — [mimetpla.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpla.cpp)
- **Inline style from prefs** (`MimeTextBuildPrefixCSS`): `mail.quoted_style` 1/2/3 append `font-weight: bold; `, `font-style: italic; `, or both; `mail.quoted_size` 1 appends `font-size: large; ` and 2 `font-size: small; `; a non-empty `mail.citation_color` appends `color: <value>;`. — [mimetpla.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpla.cpp) (same function in [mimetpfl.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpfl.cpp)). With the default `#007cff` the style is non-empty, so default plain-text quotes carry an inline `style="color: #007cff;"`.
- **Literal `>` characters**: for each line with a quote prefix, the prefix is written inside `<span class="moz-txt-citetags">…</span>` (converted with no recognition), then the rest of the line. `.moz-text-plain[graphical-quote="true"] .moz-txt-citetags { display: none; }` hides them; `[graphical-quote="false"] blockquote { border-style: none; padding: 0; }` removes the bar so the literal `>` shows. — [mimetpla.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpla.cpp), [messageBody.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageBody.css)
- **Flowed wrapper** (`MimeInlineTextPlainFlowed_parse_begin`): `<div class="moz-text-flowed"` with optional `style` and `lang`, closed `>`; no `graphical-quote` or `wrap` attributes. Each line is emitted with `<br>`; the `>` prefix is consumed into `<blockquote type=cite>` elements, with no `moz-txt-citetags` span (`grep` of the file finds none), so flowed quotes always show graphical bars. Depth changes follow the RFC 3676 "quote-depth-wins" rule (code comment "We get that behaviour by just going on."). — [mimetpfl.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpfl.cpp)
- **Shared reset**: `.moz-text-flowed blockquote, .moz-text-plain blockquote { margin: 0; }`; `.moz-text-plain pre { margin: 0; font-family: inherit; }`; `[wrap="true"] { white-space: pre-wrap; }`, `[wrap="false"] { white-space: pre; }`, `[wrap="flow"] .moz-txt-sig { white-space: pre-wrap; }`. — [messageBody.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageBody.css)
- **Emphasis and form-feed classes** from the converter: `moz-txt-star` (`*bold*`), `moz-txt-slash` (`/italic/`), `moz-txt-underscore` (`_underline_`, styled `text-decoration: underline`), `moz-txt-verticalline`, `moz-txt-sup`, `moz-txt-formfeed`, `moz-txt-tag` (wraps the marker characters). — [mozTXTToHTMLConv.cpp](https://searchfox.org/mozilla-central/source/netwerk/streamconv/converters/mozTXTToHTMLConv.cpp) (confirmed by `grep` of `hg.mozilla.org/mozilla-central/raw-file/tip/netwerk/streamconv/converters/mozTXTToHTMLConv.cpp`), [messageBody.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageBody.css)
- **Linkification**: `<a class="moz-txt-link-` + one of `rfc1738`, `rfc2396E`, `freetext`, `abbreviated` + `" href="…">`. — [mozTXTToHTMLConv.cpp](https://searchfox.org/mozilla-central/source/netwerk/streamconv/converters/mozTXTToHTMLConv.cpp)
- **HTML mail wrapper**: `<div class="moz-text-html" lang="…">` inserted as the first element after `<body>`. — [mimethtm.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimethtm.cpp)
- **Signature classes**: `moz-txt-sig` (received plain text, section 5) and `moz-signature` (`<div class="moz-signature">` / `<pre class="moz-signature" cols="72">`, written by Thunderbird's own composer: `htmlsigopen[] = "<div class=\"moz-signature\">"`, `_preopen[] = "<pre class=\"moz-signature\" cols=%d>"`). — [mailnews/compose/src/nsMsgCompose.cpp](https://searchfox.org/comm-central/source/mailnews/compose/src/nsMsgCompose.cpp)
- **Header/body stylesheet link**: `<link rel="important stylesheet" href="chrome://messagebody/skin/messageBody.css">`; `mail/base/jar.mn` maps `chrome://messagebody/skin/messageBody.css` to `chrome://messenger/skin/messageBody.css`; per-OS `messageBody.css` files `@import` the shared one. — [nsMimeHtmlEmitter.cpp](https://searchfox.org/comm-central/source/mailnews/mime/emitters/nsMimeHtmlEmitter.cpp), [mail/base/jar.mn](https://searchfox.org/comm-central/source/mail/base/jar.mn)
- **Also relevant**: `:root { overflow: auto !important; }` in messageBody.css; `img[shrinktofit]` / `[overflowing]` rules; Thunderbird font-size UI hook targets `.moz-text-plain, .moz-text-flowed` (`mail/modules/UIFontSize.sys.mjs`). — [messageBody.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageBody.css), [UIFontSize.sys.mjs](https://searchfox.org/comm-central/source/mail/modules/UIFontSize.sys.mjs)
- Recent source churn to be aware of: the plain-text converters were last touched on 2026-09 (Bug 2070022 removed a print output path; Bug 2000815 stops rendering trailing empty lines in plain-text bodies via `mail.body_sanitize_trailing_blank_lines`). — [hg json-log mimetpla.cpp](https://hg.mozilla.org/comm-central/json-log/tip/mailnews/mime/src/mimetpla.cpp)

### Inferences
- A user stylesheet can distinguish the three message types purely by wrapper class: `.moz-text-plain` (also carries `graphical-quote`, `wrap` attributes usable as selectors), `.moz-text-flowed`, `.moz-text-html`. Because plain text and flowed both become `blockquote[type="cite"]`, one `blockquote[type="cite"]` rule colours both, and nested-descendant selectors give the per-level colours without regard to `>` counts.
- Hiding `.moz-txt-citetags` is Thunderbird's decision, not the user's; in a plain-text message with `mail.quoted_graphical = false`, the `>` characters reappear and CSS bars no longer apply (padding and border are zeroed on that wrapper).
- The `moz-txt-tag` span wrapping emphasis markers means CSS could dim `*`/`_` marker glyphs; I did not check whether the marker is hidden by default.

### Gaps
- I did not read mozTXTToHTMLConv.cpp end to end (e.g. whether `moz-txt-link-*` anchors get extra classes for mailto or whether the `whattodo` flags are user-configurable) and did not run Thunderbird to capture a rendered DOM, so the exact output in a live 158 message pane should be confirmed with the DOM inspector.
- Searchfox's web UI is JavaScript-driven; I used its JSON API and `hg.mozilla.org/.../raw-file/tip` for source text, so line numbers in this note come from tip at fetch time.

---

## 5. Signatures: convention and how clients de-emphasise them

### Takeaway
The convention is a line consisting of exactly dash, dash, space ("-- "). RFC 3676 treats it as neither fixed nor flowed. Thunderbird dims received plain-text signatures to 60% opacity only when the `-- ` line is exact and unquoted; aerc dims and recolours them; mutt has a `signature` colour; Gmail instead trims repeated signatures behind the ellipsis. HTML-mail signatures use client-specific wrapper markers that vary.

### Cited Findings
- RFC 3676 §4.3: "This is a special case; an (optionally quoted or quoted and stuffed) line consisting of DASH DASH SP is neither fixed nor flowed."; "Generating agents MUST NOT end a paragraph with such a signature line."; receiving agents test for the signature line "both before the test for a quoted line" and after quote marks and stuffing are removed. — [RFC 3676 §4.3](https://datatracker.ietf.org/doc/html/rfc3676#section-4.3)
- Thunderbird dimming, verbatim:
  ```css
  @media not print {
    div.moz-text-flowed > div.moz-txt-sig,
    div.moz-text-plain > pre > div.moz-txt-sig,
    pre.moz-signature {
      opacity: 0.6;
    }
  }
  ```
  — [messageQuotes.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageQuotes.css)
- Detection (fixed plain text): the line must start with `-- ` and have `\r` or `\n` as the fourth character (`lineSourceStr.First() == '-' && Substring(lineSourceStr, 0, 3).EqualsLiteral("-- ") && (lineSourceStr[3] == '\r' || lineSourceStr[3] == '\n')`); then `text->mIsSig = true` and `<div class="moz-txt-sig">` opens, closed at message end (`parse_eof`: `"</div>"  // .moz-txt-sig`). Because the test runs on the unstripped line, a quoted `> -- ` line is not treated as a signature. — [mimetpla.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpla.cpp)
- Detection (flowed): a signature separator at quote level 0 opens `<div class="moz-txt-sig"><span class="moz-txt-tag">--&nbsp;<br></span>`; a separator inside a quote (or after the sig started) is written plain as `--&nbsp;<br>`. — [mimetpfl.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpfl.cpp)
- `mail.strip_sig_on_reply` (read as `mStripSig`) controls dropping the signature when quoting for a reply, not display. — [mimetpla.cpp](https://searchfox.org/comm-central/source/mailnews/mime/src/mimetpla.cpp)
- `pre.moz-signature` (and `<div class="moz-signature">` for HTML signatures) are written by Thunderbird's composer; only the `pre` form is dimmed by the stylesheet above. — [nsMsgCompose.cpp](https://searchfox.org/comm-central/source/mailnews/compose/src/nsMsgCompose.cpp), [messageQuotes.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageQuotes.css)
- aerc: the `colorize` filter enters a SIGNATURE state on an exact `-- ` line and styles every following line with the `signature` style; shipped default `signature.dim = true`, `signature.fg = 4` (blue). Style description: "Email signatures." — [filters/colorize.c](https://github.com/rjarry/aerc/blob/master/filters/colorize.c), [aerc-stylesets(7)](https://git.sr.ht/~rjarry/aerc/tree/master/item/doc/aerc-stylesets.7.scd)
- mutt/neomutt: a `signature` colour object ("signature lines of an email (.sig)"). — [Mutt manual source](https://gitlab.com/muttmua/mutt/-/blob/master/doc/manual.xml.head), [NeoMutt configuration guide](https://neomutt.org/guide/configuration)
- Gmail: repeated, identical signatures are folded into the trimmed-content ellipsis. — [Labnol](https://labnol.org/internet/gmail-trimming-signature/28762)
- HTML signature markers seen in parsers and samples: Gmail `gmail_signature` class and `data-smartmail`; Outlook `id="Signature"`; Windows Mail `<div data-signatureblock="true">`; Odoo `odoo_signature_wrapper`. — [odoo `mail.py`](https://github.com/odoo/odoo/blob/master/odoo/tools/mail.py), [talon `windows_mail.html`](https://github.com/mailgun/talon/blob/master/tests/fixtures/html_replies/windows_mail.html)
- Contrast of the 0.6 step: computed 5.74:1 for black on white (6.16:1 for white on #2a2a2e); 4.5:1 is reached at about 0.55. WCAG 1.4.3 gives signatures no exemption because they are real content. — [WCAG 2.2 Understanding 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) (ratio computed)

### Inferences
- Thunderbird's existing 0.6 opacity is already near the practical floor for black-on-white (0.55 for 4.5:1). Additional de-emphasis should come from smaller size or colour hue shift, not further opacity reduction; a size step of one notch (to body-small) plus 0.6–0.65 opacity stays above 4.5:1.
- Since opacity also dims any link inside the signature, link affordance (underline) inside `.moz-txt-sig` should be tested separately.
- Plain `--` without the trailing space (a common sender error) is not matched by Thunderbird's detector, so such signatures receive no dimming; CSS cannot repair that. HTML mail signatures from Gmail/Outlook (`.gmail_signature`, `#Signature`, `[data-signatureblock]`) are not dimmed by Thunderbird and can be targeted individually, ideally with colour/size only.

### Gaps
- Apple Mail's signature markup was not obtained, and no Fastmail or Outlook documentation on signature markup was found; the HTML signature markers come from open-source parsers.
- Whether Thunderbird's `moz-txt-sig` dimming applies to a signature that contains a nested quoted section was not tested.

---

## 6. Link affordance: underlines versus colour-only links

### Takeaway
WCAG 1.4.1 requires that colour not be the only way to tell links from surrounding text; the sufficient technique G183 is a 3:1 contrast between link colour and the surrounding text colour (and each still needs 4.5:1 against the background), and F73 says a hover-only cue fails. NN/g's 2004 guidance (underline and colour) now carries a March 2026 editor's note saying underlines are no longer required, with contrast plus hover/focus cues as their own approach. Thunderbird gives its own message-pane links a theme colour only in dark mode, and Outlook mail brings its own blue-underline styles.

### Cited Findings
- SC 1.4.1: "Color is not used as the only visual means of conveying information, indicating an action, prompting a response, or distinguishing a visual element." A link styled to look like neighbouring static text would not fail the criterion, though that styling may hurt usability. — [WCAG 2.2 Understanding 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
- G183 (sufficient technique): applies "when inline text links are only distinguished from static non-link text by color and lightness"; "the contrast ratio between the link text and the static text must be at least 3:1"; link and non-link colours each must also satisfy contrast against the background; "authors may still consider using an alternative or additional way to indicate links, such as an underline or bold text. Especially for dark colors, it can be difficult to visually distinguish between differently colored text even when the link text contrast to surrounding text meets the required ratio of 3:1." Examples: `a { color: #3333FF; text-decoration: none; }` (3:1 against black text and 4.5:1 against white); `#3366CC` against black text is 3.9:1. — [WCAG G183](https://www.w3.org/WAI/WCAG22/Techniques/general/G183)
- F73 (failure): removing the underline and leaving only a colour difference for links in running text is a failure; "If the non-color cue only happens when the mouse hovers over the link or when the link receives focus, it is still a failure."; bold plus a colour change does not fail "because the boldness is not color dependent". — [WCAG F73](https://www.w3.org/WAI/WCAG22/Techniques/failures/F73)
- The 1.4.1 Understanding page keeps visited links in scope: "authors must continue to ensure that all text links meet contrast minimums against the page background." — [WCAG 2.2 Understanding 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
- NN/g (Nielsen, 2004): "To maximize the perceived affordance of clickability, color and underline the link text."; underlines can be dropped in navigation menus and link lists; "underlining is essential if you use link colors such as reds or greens"; underlines matter for low-vision users; "Don't underline any text that's not a link"; use different colours for visited and unvisited links, unvisited "more vivid, bright, and saturated", visited "dull and washed out", both variants of one hue; "Don't use blue for non-link text … Blue is still the color with the strongest perceived affordance of clickability."; no special hover colour needed unless links are less affordant, in which case "an underline appear while hovering." — [NN/g, Guidelines for Visualizing Links](https://www.nngroup.com/articles/guidelines-for-visualizing-links/)
- NN/g editor's note (March 2026): "Most users today can identify links through color, placement, and context without relying on underlines, and many modern designs (including nngroup.com) intentionally omit link underlines." For accessibility it points to WCAG 1.4.1 achieved by "sufficient contrast between link and non-link text, and additional visual indicators on hover and focus (Technique G183)"; the article is kept "for its historical value". — [NN/g](https://www.nngroup.com/articles/guidelines-for-visualizing-links/)
- WebKit's UA default for links: `a:any-link { color: -webkit-link; text-decoration: underline; cursor: auto; }`. — [WebKit `html.css`](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/html.css)
- Thunderbird message pane links: messageBody.css only overrides link colour in the dark-reader path: `@media (prefers-color-scheme: dark) and -moz-pref("mail.dark-reader.enabled") { a:link { color: var(--color-text-highlight-dark); } a:visited { color: VisitedText; } }`. Bug 2018015 changed `a:link` from `LinkText` to the highlight colour. Bug 2011761 had changed the default dark-mode link colour in the toolkit. — [messageBody.css](https://searchfox.org/comm-central/source/mail/themes/shared/mail/messageBody.css), [Bug 2018015](https://bugzilla.mozilla.org/show_bug.cgi?id=2018015)
- Plain-text URLs become `<a class="moz-txt-link-freetext|abbreviated|rfc1738|rfc2396E">`, so they can be styled separately from sender HTML links. — [mozTXTToHTMLConv.cpp](https://searchfox.org/mozilla-central/source/netwerk/streamconv/converters/mozTXTToHTMLConv.cpp)
- Sender-supplied link styles collide: Outlook mail ships `a:link, span.MsoHyperlink { mso-style-priority:99; color:blue; text-decoration:underline; } a:visited, span.MsoHyperlinkFollowed { … color:purple; text-decoration:underline; }` in a `<style>` block. — [talon `ms_outlook_2010.html`](https://github.com/mailgun/talon/blob/master/tests/fixtures/html_replies/ms_outlook_2010.html)
- Computed against black body text: Thunderbird's light highlight `#1373d9` is 4.48:1 (passes G183's 3:1) and 4.69:1 on white; dark highlight `#58c9ff` is 7.63:1 on #2a2a2e. `mail.citation_color`'s `#007cff` is 3.94:1 on white. (computed)

### Inferences
- Pairing G183's 3:1 link-to-text contrast with a persistent underline in running text (or with a thin underline in a lighter tone) is the safest reading of WCAG: G183 permits colour-only, F73 forbids hover-only cues, and the G183 note itself recommends an underline or bold for dark colours. For a mail reader, where links appear in running prose and in signatures at reduced opacity, a default underline (possibly `text-decoration-thickness` 1px, `text-underline-offset`, and a lower-contrast `text-decoration-color`) keeps affordance without relying on hue.
- Because Thunderbird now uses the same highlight token for quoted text and (in dark mode) link text, quoted prose is blue and non-link, contradicting NN/g's "don't use blue for non-link text" (a 2004 rule softened by the 2026 note). A neutral quote text colour with coloured bars would remove that ambiguity.
- Outlook, Gmail and Apple Mail senders may specify their own link colours and underlines (inline or in `<style>`), so a userContent.css link rule needs `!important` to normalise them, and may still want to respect visited/unvisited distinction per NN/g (same hue, lower saturation for visited).
- Restraint: restyling every `a` also restyles mailto and tracking links inside the header/quotes; scoping to `.moz-text-html a[href]`, `.moz-text-plain a`, `.moz-text-flowed a` keeps the chrome document (header, attachment pane) under separate control.

### Gaps
- Gecko's default `a:link` colour in the message pane was not read from source here (`LinkText` is the system colour keyword), so the contrast of the default blue against the actual body text colour is not confirmed.
- No published research comparing underlined versus colour-only links specifically in email reading was found; NN/g (2004, now with a 2026 caveat) and the WCAG techniques are the evidence.
- The Adrian Roselli article "On Link Underlines" (search result) was not read, so I make no claim from it.
