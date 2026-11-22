#!/usr/bin/env bash
# A session that built the work: it wrote spec.md, changed bin/notes, and committed.
set -euo pipefail
printf '# Spec\n\nThe search command.\n' > spec.md
printf '\n# search: not built yet\n' >> bin/notes
git add bin/notes
git -c user.name=sample -c user.email=sample@example.invalid commit -q -m "Start the search command"
