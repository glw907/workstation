# Phone checks without a phone (Geoff, 2026-10-29)

Geoff has no mobile phone. His voip.ms number, 907-277-9397, stands in for one. `phone-check`
(`~/.local/bin`, stdlib Python, Super+Shift+P) waits for a Print Screen of a QR code and decodes
it with `zbarimg` (Homebrew `zbar`). An `sms:` or `SMSTO:` code is texted from the voip.ms number
after one Enter, and a web link opens in the browser. Then it watches the inbox and copies any
code that arrives to the clipboard. `phone-check --code` only watches, for a site that texts a
code. Both go through `voipms-sms` (`status`, `inbox [--json]`, `send`).

Geoff runs `phone-check` and `voipms-sms send` himself: a phone check confirms a person is acting,
so a Claude session never completes one. Claude may run `voipms-sms status` and `inbox`; `send`
asks every time. SMS must be on for the number (voip.ms portal, DID Numbers, Manage DIDs).

Google's sign-up QR is an `accounts.google.com/devicephoneverification` link, a check that a
physical phone is present. Opening it on the desktop does not pass it, and faking a phone to pass
it is out of bounds (auto mode refused it as bot-check circumvention, 2026-10-29). Choose Google's
"text me a code" option or "Try another way" instead, and run `phone-check --code`. Google refuses
some VoIP numbers in these checks, so a check can still fail.
