# Thunderbird 158 styling map: message list, header, body

Source-read map (2026-10-13) of the selectors, attributes and custom properties
that control Thunderbird 158's message list (cards and table), message header,
and message body, as installed with rafaelmardojai/thunderbird-gnome-theme and
this repo's `thunderbird/` overrides. Read from omni.ja (Flatpak build
20261008005236), the installed theme, and comm-central master (libmime,
DBView). "Inference" marks a point read from CSS and not yet verified in a
running Thunderbird.

## Views

- Pref `mail.threadpane.listview`: 0 cards (default, all-thunderbird.js:628), 1 table. `updateThreadView` (about3Pane.js:6109-6123) sets `#threadTree[rows="thread-card"]` or `[rows="thread-row"]`; rows are `tr.card-layout` or `tr.table-layout`.
- `#threadTree.cards-row-compact` when `mail.threadpane.cardsview.rowcount` is 2 (default 3). `#threadTree.is-outgoing`, `.is-unified`. `:root[uidensity=compact|touch]`.
- Row classes: `children`, `collapsed`, `selected`, `current`, `context-menu-target`.

## Card DOM (about3Pane.xhtml:432-484)

```
tr[is="thread-card"].card-layout[data-properties]
  td > div.card-container
    div.thread-card-column.read-status-column > img.read-status
    div.thread-card-column
      div.thread-card-row: span.account-indicator, span.sender, img.state (replied/forwarded/redirected), span.date, button.tree-button-more
      div.thread-card-dynamic-row: span.sort-header-details, button.twisty.thread-card-button (img.replies-icon, span.thread-replies, img.twisty-icon), div.thread-card-subject-container > span.subject, div.thread-card-icon-info (img.attachment-icon, thread-card-tags [shadow: img.tag-icon x3, span.tag-more], button.button-spam, button.button-star)
```

No preview/snippet element in 158. `.sender` holds senderCol (recipientCol in outgoing folders).

## data-properties tokens (dbview.cpp GetRowProperties)

`outgoing`, `tagged`/`untagged`, top tag token `T_24label1`..`T_24label5` (for `$label1..5`; only the top-ordinal tag), `unread`/`read`, `new`, `replied`, `forwarded`, `redirected`, `flagged`, `attach`, `junk`/`notjunk`, `hasUnread`, `hasNew` (thread has unread/new children), `watch`, `ignore`, `ignoreSubthread`, `offline`, `imapdeleted`, `hasimage`, `dummy` (group header), `thread-children` (JS-added on non-top thread rows).

## Stock card styling

- `.sender` 600 weight .95rem; unread bold sender and subject (threadCard.css:80-87, 386-390). `.date` opacity .85.
- `.read-status` dot: `--read-status-fill/-stroke/-icon`; new: sparkle, subject `--new-subject-color`.
- Twisty with unread children: green dot, bold reply count (`--unread-color`); `hasNew` sparkle and `--new-color`.
- Star: `--thread-pane-flag-fill/-stroke` (threadPane.css:270-274). Spam button `--thread-pane-spam-*`. Attachment icon opacity .7. Reply/forward/redirect icons hard-coded purple/blue/orange.
- Junk card remaps `--tree-card-*` to `-spam` variants (threadCard.css:623-632).

## GNOME theme card overrides (theme/parts/mail.css:115-224), all !important

- `#threadTree` background `--gnome-secondary-sidebar-background`.
- `.card-container`: background none, border 0, radius 6px, `grid-template-columns: 1fr`, min-height 60px.
- `.thread-card-column:first-child { display:none }` hides the unread/new dot column (mail.css:145-147).
- `:is(.sender,.date,.subject) { color: var(--gnome-view-color); font-weight: normal }` specificity (1,3,1) (mail.css:156-159). `.subject`, `.date` 9pt; `.date` opacity .8.
- Hover `--gnome-hover-color` (1,4,1); selected `--gnome-selected-color` (1,3,1), same whether focused or not; `.current` unstyled.
- Unread: `[data-properties~="unread"] .card-container :is(.subject,.sender) { font-weight: bold }` (1,4,1).
- Junk: `:is(.sender,.date,.subject) { color: var(--color-red-60) }`.
- Consequence: `--tree-card-*`, `--read-status-*`, `--new-subject-color` are inert in cards. Card unread is bold only. Override with matching specificity plus !important; customChrome.css loads last so a tie wins.

## Theme icon rules (theme/parts/icons.css)

- :5-77 forces `fill: var(--gnome-toolbar-icon-fill) !important` on attachment icons, tag icons, table images, `.button-star`, `#attachmentToggle`, `#starMessageButton`, `.twisty`.
- :205-217 (`:not(#hack)`): flagged star fill `--gnome-toolbar-star-button`; table unread dot fill `--gnome-accent`; junk spam icon `--gnome-palette-red-2`.
- Header flagged star: the theme's fill beats stock orange (inference).

## Table view (thread-row.mjs, threadPane.css)

- Cells `td.<columnid>-column`: selectcol, threadcol, flaggedcol, attachmentcol, subjectcol (div.thread-container > twisty + div.subject-line > img + span), unreadbuttoncolheader, sendercol / recipientcol / correspondentcol, junkstatuscol, datecol, receivedcol, statuscol, sizecol, tagscol, accountcol, prioritycol, unreadcol, totalcol, locationcol, idcol, deletecol.
- `.table-layout { color: var(--tag-color, currentColor) }`. Unread row bold; untagged unread `color: var(--unread-color)`. Collapsed read thread with unread children: 600 weight, underline.
- Selected/focused: `--listbox-*`; tagged selected focused row background becomes `--tag-color` with `--tag-contrast-color` text (threadPane.css:185-190).
- Variables: `--listbox-hover`, `--listbox-selected-bg`, `--listbox-focused-selected-bg`, `--listbox-selected-color`, `--unread-color`, `--tree-view-bg`, `--tree-view-color`, `--tag-color`, `--tag-contrast-color`, `--thread-pane-flag-*`, `--thread-pane-unread-*`, `--thread-pane-spam-*`. Theme maps `--listbox-*` to gnome hover/selected/view colours (variables.css:333-346).

## Tags

- `tagColors.css` is a dead stub. Live: `setUpTagStyles()` (about3Pane.js:5203-5227), re-run on any `mailnews.tags.*` change: inserts `tr[data-properties~="T_24label1"] { --tag-color; --tag-contrast-color }` and sets `body` style `--tag-<key>-backcolor/-forecolor`.
- Table: whole row text is the tag colour; selected focused row uses it as background. Cards: `--tag-color` unused; up to 3 shadow-DOM tag icons coloured from `--tag-\$label1-backcolor` (inline on body; override needs user !important). threadCardTags.css: `.tag-icon { fill: color-mix(in srgb, light-dark(white,black) 50%, var(--tag-color,currentColor)); stroke: var(--tag-color,currentColor) }`.
- Header tag pills: `li.tag` with inline black/white text and tag background (header-fields.js:1005-1022).

## Message header (about:message, a chrome document)

- aboutMessage.xhtml links chrome stylesheets; embedded without `type="content"`, so userChrome.css applies (theme mail.css:49-57 relies on it).
- `header#messageHeader.message-header-container` (classes message-header-large-subject, -hide-label-column, -show-recipient-avatar, -show-sender-full-address). From: `#expandedfromRow > #expandedfromBox[is=multi-recipient-row]`. To/Cc rows `#expandedtoRow` etc. Date `time#dateLabel.message-header-datetime` (and `#dateLabelSubject`). Subject `#expandedsubjectBox` (span child). Tags `#expandedtagsBox > ol.tags-list > li.tag`. Star `button#starMessageButton.email-action-flagged(.flagged)`. Buttons `.message-header-view-button`.
- Recipient: `li.header-recipient` > `div.recipient-avatar`, `span.recipient-single-line`, `span.recipient-multi-line` (`.recipient-multi-line-name` 500 weight 105%, `.recipient-multi-line-address` opacity .9), `button.recipient-address-book-button(.in-address-book)`.
- Variables: `--message-header-label-opacity` (.7), `--recipient-avatar-color/-background-color`, `--selected-item-color/-text-color` (theme: neutral `--gnome-active-color`), `--layout-*`, `--color-text-base`. Subject large: 500 weight 1.35em. Flagged star stock `--color-orange-30/-60`.
- Attachment bar `#attachmentBar`, list `#attachmentList .attachmentItem`. Theme: `#messageHeader` window bg, `#messagePane` view bg, `#attachmentBar` toolbar bg.

## Message body (content document; userContent.css only)

- libmime links `chrome://messagebody/skin/messageBody.css` as an author sheet; it imports messageQuotes.css and colors.css. Overrides need user-origin `!important` (beats author !important and inline non-important styles).
- Scope by body class, never bare `blockquote`: `div.moz-text-plain[wrap][graphical-quote]` (contains `pre.moz-quote-pre`), `div.moz-text-flowed`, `div.moz-text-html`. Quotes: nested `blockquote[type="cite"]`. Cite prefixes `span.moz-txt-citetags` (hidden when graphical-quote). Signature `div.moz-txt-sig` (with `span.moz-txt-tag` for `-- `), `pre.moz-signature`, `div.moz-signature`. Links `a.moz-txt-link-freetext|-abbreviated|-rfc2396E|-rfc1738`.
- messageQuotes.css:75-83: `body blockquote[type="cite"] { margin-block:1ex; margin-inline:0; padding:.4ex 1ex; color: var(--color-text-highlight) !important; border-inline-start: 2px solid rgb(114,159,207) }`; nested levels (`& &`): 2 #ad7fa8, 3 #8ae234, 4 #fcaf3e, 5 #e9b96e, 6+ repeats 5. Quote text is one colour at every level: `--color-text-highlight` = `light-dark(#1373d9, #58c9ff)` from colors.css `:root` inside the message document (customChrome.css's value does not reach it).
- messageBody.css: `.moz-text-flowed blockquote, .moz-text-plain blockquote { margin:0 }`; `.moz-text-plain[graphical-quote="false"] blockquote { border-style:none; padding:0 }`; signature `opacity:.6` (messageQuotes.css:64-70); `body { line-height: initial !important }`.
- Dark reader (`mail.dark-reader.enabled` default true, toggle shown): `html { background-color: var(--color-gray-90) }` (#18181b), `color: var(--color-text-base-dark)` (#eeeef0), links `var(--color-text-highlight-dark)` (#58c9ff), `:root { color-scheme: dark }`. Light mode: no author background or link colour.
- Prefs: `mail.quoteasblock` true; `mail.quoted_graphical` true; `mail.quoted_style` 0; `mail.quoted_size` 0; `mail.citation_color` "#007cff" (inline, beaten by the author !important; inference).
- Gmail replies use `blockquote.gmail_quote` (often without `type=cite`) with an inline `border-left:1px #ccc solid`; not covered by messageQuotes.css.

## Current repo overrides (thunderbird/customChrome.css)

- Nord block on `:root`: `--gnome-accent-bg` nord10, success nord14, warning nord13, error and destructive nord11; drives every `--gnome-accent`/`--gnome-warning`/`--gnome-error` consumer.
- `--color-text-highlight: var(--gnome-accent)` (chrome only).
- `--new-subject-color`, `--new-color` accent (first inert in cards); `--read-status-*` on unread/new (inert in cards); twisty `hasUnread`/`hasNew` accent (live).
- `--thread-pane-flag-*` warning (fill inert under the theme; stroke live), spam/junk tokens, `--unread-color: var(--gnome-view-color)` (live in table rows).
- Junk card text `--gnome-error` (live).
- customContent.css: Nord block and tokens inside `@-moz-document url-prefix("about:…")` only; no message-body or header rules.
