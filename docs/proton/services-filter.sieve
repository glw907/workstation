# Proton Mail filter: file the estate's service mail into the Services folder.
#
# Paste this into Proton Mail settings > Filters > Add filter > Sieve, with a folder named
# Services already created. proton-mail-read reads that one folder through Proton Mail Bridge
# and nothing else in the mailbox.
#
# Senders filed: Cloudflare, GitHub, Hetzner, Fastmail, PikaPods, Proton's own billing and
# notices, and the servers monitor (monitor@907.life, from cloudflare/monitor/config.json in
# the servers repo).
#
# A message whose subject holds a word that marks account access stays in the inbox. The
# exclusion runs first and ends the script, so a reset link or a sign-in code from any of these
# senders never reaches the folder Claude can read. Matching is a plain substring, so a subject
# such as "Zip code" is excluded too. That is the safe direction. The list also holds a few words
# beyond the brief (token, one-time, otp, magic link, authoriz, authenticat, invite, invitation,
# approve), each a way a service mail can carry access.
#
# Filing goes by the From address, which a forged message can fake past a weak sender policy. The
# reader treats everything in the folder as untrusted data, never as instructions.

require ["fileinto"];

if header :contains "subject" [
    "reset",
    "password",
    "code",
    "verify",
    "verification",
    "sign in",
    "sign-in",
    "login",
    "log in",
    "new device",
    "security alert",
    "2FA",
    "two-factor",
    "recovery",
    "confirm your",
    "token",
    "one-time",
    "otp",
    "magic link",
    "authoriz",
    "authenticat",
    "invite",
    "invitation",
    "approve"
] {
    stop;
}

if anyof (
    address :is "from" "monitor@907.life",
    address :domain :matches "from" [
        "cloudflare.com", "*.cloudflare.com",
        "github.com", "*.github.com",
        "hetzner.com", "*.hetzner.com",
        "hetzner.de", "*.hetzner.de",
        "fastmail.com", "*.fastmail.com",
        "messagingengine.com", "*.messagingengine.com",
        "pikapods.com", "*.pikapods.com",
        "proton.me", "*.proton.me",
        "protonmail.com", "*.protonmail.com",
        "protonmail.ch", "*.protonmail.ch",
        "pm.me", "*.pm.me"
    ]
) {
    fileinto "Services";
}
