#!/usr/bin/env bash
# A session that kept to its brief: it wrote spec.md and nothing else.
set -euo pipefail
printf '# Spec\n\nThe search command.\n' > spec.md
