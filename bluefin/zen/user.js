// Prefs the Adwaita theme needs (ClixTW/zen-gnome-theme, linked in by
// bootstrap.sh setup_zen). policies.json cannot carry them: its Preferences
// policy accepts no zen. or svg. pref. Zen reapplies this file at every start.

// Loads <profile>/chrome/userChrome.css, which is the theme.
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);
// Lets the theme's Adwaita icons take the light or dark text color.
user_pref("svg.context-properties.content.enabled", true);
// The theme's layout assumes no gap around the page.
user_pref("zen.theme.content-element-separation", 0);
