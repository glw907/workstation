#!/usr/bin/env bash
# run-fixtures.sh: prove the Microsoft style package resolves and fires. The
# fixture is wordy copy that must raise Microsoft.Wordiness; a miss means the
# styles are not synced. Styles live in ~/.config/vale/styles, populated by
# `vale sync` (bootstrap's setup_vale_styles step), not in the repo, so the
# config is generated here against the live path. Vale exits non-zero
# whenever it finds alerts, so capture its output before grepping.
set -uo pipefail
cd "$(dirname "$0")" || exit 1
fail=0

ini="$(mktemp)"
trap 'rm -f "$ini"' EXIT
cat > "$ini" <<EOF
StylesPath = $HOME/.config/vale/styles
MinAlertLevel = suggestion

[*.md]
BasedOnStyles = Microsoft
EOF

ms="fixtures/microsoft/copy.md"
ms_out="$(vale --config="$ini" --output=line "$ms")"
if ! grep -q 'Microsoft.Wordiness' <<<"$ms_out"; then
  echo "FAIL: $ms did not raise Microsoft.Wordiness; run 'vale sync' in ~/.config/vale"; fail=1
fi

[ "$fail" -eq 0 ] && echo "fixtures: OK" || echo "fixtures: FAILED"
exit "$fail"
