// Thunderbird preferences, applied at every startup.
// thunderbird-theme-sync copies this file over the profile's user.js, so it
// replaces the theme installer's copy. Thunderbird rereads it on each launch
// and it wins over a change made in Settings: change a value here, not in the
// UI, then run thunderbird-theme-sync.

// Required by the GNOME theme: load userChrome.css and userContent.css.
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);
// Required by the GNOME theme: recolor its symbolic icons.
user_pref("svg.context-properties.content.enabled", true);

// Default tag colors from the Nord palette (Aurora and Frost).
user_pref("mailnews.tags.$label1.color", "#bf616a"); // Important, nord11
user_pref("mailnews.tags.$label2.color", "#d08770"); // Work, nord12
user_pref("mailnews.tags.$label3.color", "#a3be8c"); // Personal, nord14
user_pref("mailnews.tags.$label4.color", "#ebcb8b"); // To Do, nord13
user_pref("mailnews.tags.$label5.color", "#b48ead"); // Later, nord15

// Message list: show senders' names without their addresses (2 is the name
// only; Thunderbird still shows the address when a name spoofs one).
user_pref("mail.addressDisplayFormat", 2);
// Thunderbird caches each formatted sender per version; bump this number
// again whenever the format above changes, or old rows keep the old text.
user_pref("mail.displayname.version", 1);
// Cards show two rows (sender and subject) instead of three.
user_pref("mail.threadpane.cardsview.rowcount", 2);
// Fastmail's server filter handles spam, so the adaptive junk filter stays
// off for every account (a per-account setting in the UI would turn it back on).
user_pref("mail.server.default.spamLevel", 0);

// Calm desktop: no new-mail popup or sound. Unread counts stay inside
// Thunderbird's own folder pane; the dock shows none (bluefin/gnome-settings.txt).
user_pref("mail.biff.show_alert", false);
user_pref("mail.biff.play_sound", false);
