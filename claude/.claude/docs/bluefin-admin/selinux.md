# SELinux for restored data

Bluefin runs SELinux enforcing; the Mint backup data carries no SELinux labels at all.
**After restoring anything into `/var/home/glw907` (which is what `~/` is on
Bluefin), run:**

```
sudo -A restorecon -R -v /var/home/glw907
```

Skipping this is a documented cause of broken logins and other permission-shaped
failures that look unrelated to SELinux. Run it once after the full restore, and
again after any later restore of additional data (a forgotten directory pulled from
the R2 backup, for example).
