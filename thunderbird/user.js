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
user_pref("mailnews.tags.$label4.color", "#5e81ac"); // To Do, nord10
user_pref("mailnews.tags.$label5.color", "#b48ead"); // Later, nord15

// Calm desktop: no new-mail popup or sound. Unread counts stay inside
// Thunderbird's own folder pane; the dock shows none (bluefin/gnome-settings.txt).
user_pref("mail.biff.show_alert", false);
user_pref("mail.biff.play_sound", false);
