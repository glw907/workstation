# Email

The household's mail runs on Stalwart on ward, a server built and run from `~/Projects/household-it`.
Clients reach it at `mail.907.life` over JMAP, IMAP, and DAV, and webmail (Bulwark on orpheus) is
`webmail.907.life`. Fastmail is retired: the mailboxes moved in October 2026, and
`~/.claude/instructions/fastmail-api.md` describes the old service only. Ward's sending setup (SPF, DKIM, and the outbound DNS records) is in
`~/Projects/household-it/docs/reference/decisions.md#rulings-and-decisions-from-the-mail-server-pass`,
and its submission ports are in
`~/Projects/household-it/docs/reference/decisions.md#the-technical-mailbox-2026-11-07`. Its JMAP
quirks are in
`~/Projects/household-it/docs/reference/decisions.md#rulings-and-decisions-from-the-mail-filters-pass`,
and its sign-in ban limits are in
`~/Projects/household-it/docs/systems/mail.md#unban-a-client-from-stalwarts-auto-ban`. The
`mail-tend` skill covers mail filing.

poplar, a bubbletea terminal email client in `~/Projects/poplar/`, is in development and not in
daily use.

Hylki (Flatpak `co.hyprlab.Hylki`) is the desktop mail client
(Geoff, 2026-10-18; Thunderbird is retired, its mail filters backed up under
`~/.local/state/browser-mail-retire-2026-10-18/`). Contacts and calendars are GNOME <!-- host-ok -->
Contacts and GNOME Calendar, fed by a CalDAV/CardDAV account for ward (`https://mail.907.life`, user
`geoff@907.life`) in GNOME Online Accounts, since 2026-10-22; vdirsyncer and khard are retired;
Hylki reads the Evolution Data Server address books and adds invitations to the calendar.
