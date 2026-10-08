#!/usr/bin/env bash
# Linter regression tests. Each case's prefix states the expected verdict:
#   ok-*    no ERROR and no WARN
#   warn-*  at least one WARN, no ERROR
#   err-*   at least one ERROR
# Also lints the "Minimal shape to copy" example from SKILL.md: it must be clean.
set -uo pipefail
cd "$(dirname "$0")/.."
lint=scripts/lint_msd.py
fail=0
check() {  # check <file> <expected ok|warn|err> [label]
  local out errs warns got
  out="$(python3 "$lint" "$1")"
  errs=$(grep -c '^ERROR' <<<"$out"); warns=$(grep -c '^WARN' <<<"$out")
  if [ "$errs" -gt 0 ]; then got=err; elif [ "$warns" -gt 0 ]; then got=warn; else got=ok; fi
  local label="${3:-$(basename "$1")}"
  if [ "$got" = "$2" ]; then printf '  ok    %-45s %s\n' "$label" "$got"
  else printf '  FAIL  %-45s expected %s, got %s\n%s\n' "$label" "$2" "$got" "$out"; fail=1; fi
}
echo "lint_msd.py regression tests"
for f in tests/cases/*.msd; do check "$f" "$(basename "$f" | cut -d- -f1)"; done
shape="$(mktemp)"; trap 'rm -f "$shape"' EXIT
python3 - "$shape" <<'PY'
import sys, pathlib
s = pathlib.Path("SKILL.md").read_text()
block = s.split("## Minimal shape to copy", 1)[1].split("```", 2)[1]
pathlib.Path(sys.argv[1]).write_text(block.lstrip("\n"))
PY
check "$shape" ok "SKILL.md: minimal shape example"
[ "$fail" -eq 0 ] && echo "all passed" || { echo "FAILED"; exit 1; }
