// Thunderbird preferences, applied at every startup.
// thunderbird-theme-sync copies this file over the profile's user.js, so it
// replaces the theme installer's copy. Thunderbird rereads it on each launch
// and it wins over a change made in Settings: change a value here, not in the
// UI, then run thunderbird-theme-sync.

// Required by the GNOME theme: load userChrome.css and userContent.css.
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);
// Required by the GNOME theme: recolor its symbolic icons.
user_pref("svg.context-properties.content.enabled", true);

// Default tag colors from the GNOME (Adwaita) palette.
user_pref("mailnews.tags.$label1.color", "#e01b24"); // Important, red 3
user_pref("mailnews.tags.$label2.color", "#e66100"); // Work, orange 4
user_pref("mailnews.tags.$label3.color", "#26a269"); // Personal, green 5
user_pref("mailnews.tags.$label4.color", "#3584e4"); // To Do, blue 3
user_pref("mailnews.tags.$label5.color", "#9141ac"); // Later, purple 3

// Calm desktop: no new-mail popup or sound. Unread counts stay inside
// Thunderbird's own folder pane; the dock shows none (bluefin/gnome-settings.txt).
user_pref("mail.biff.show_alert", false);
user_pref("mail.biff.play_sound", false);
