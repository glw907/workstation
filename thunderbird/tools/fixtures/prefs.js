// Fixture prefs for the screenshot harness's scratch profile (tb-shots copies
// this to <profile>/prefs.js before the first launch).
//
// A Local Folders-only, offline, wizard-free profile. None of these keys
// appear in thunderbird/user.js: the sync copies that file over the profile's
// user.js, and libpref reads prefs.js first and user.js second
// (Preferences.cpp ReadSavedPrefs, then ReadUserOverridePrefs), so both sets
// survive and the sync's --check still matches.
//
// What each group does, probed on Thunderbird 158 (Flatpak):
//   - The account block alone suppresses the account wizard and points Local
//     Folders at the mbox. It declares account1 as a Local Folders account
//     (server type "none") whose mail directory is <profile>/Mail/Local
//     Folders, and tb-shots writes the mbox to that folder's Inbox file. A
//     profile with an account never opens the wizard, and directory-rel is
//     profile-relative, so the file holds no host path. With no other pref
//     the window opens straight onto the inbox.
//   - mail.rights.version removes the "Know your rights" bar, which otherwise
//     covers the bottom of every screenshot (seen in a run without it).
//   - mailnews.start_page.enabled stops the start page; the update, default
//     client, data-reporting and offline-status keys are defensive: a run
//     without them showed nothing extra, but they keep a first launch quiet if
//     the build changes.
//   - marionette.port is the harness port. The flags that start Marionette
//     are on the command line.

user_pref("mail.account.account1.server", "server1");
user_pref("mail.account.lastKey", 1);
user_pref("mail.accountmanager.accounts", "account1");
user_pref("mail.accountmanager.defaultaccount", "account1");
user_pref("mail.accountmanager.localfoldersserver", "server1");
user_pref("mail.server.server1.type", "none");
user_pref("mail.server.server1.userName", "nobody");
user_pref("mail.server.server1.hostname", "Local Folders");
user_pref("mail.server.server1.name", "Local Folders");
user_pref("mail.server.server1.directory-rel", "[ProfD]Mail/Local Folders");
user_pref("mail.server.server1.storeContractID", "@mozilla.org/msgstore/berkeleystore;1");
user_pref("mail.rights.version", 1);
user_pref("mailnews.start_page.enabled", false);
user_pref("mail.shell.checkDefaultClient", false);
user_pref("app.update.auto", false);
user_pref("datareporting.policy.dataSubmissionPolicyBypassNotification", true);
user_pref("network.manage-offline-status", false);
user_pref("marionette.port", 28282);
// Selecting a message must not mark it read, or the harness's states drift.
user_pref("mailnews.mark_message_read.auto", false);
// Newest first, threaded, so the thread fixture shows its unread reply.
user_pref("mailnews.default_sort_order", 2);
user_pref("mailnews.default_view_flags", 1);
