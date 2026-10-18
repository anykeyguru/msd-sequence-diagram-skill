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

echo "app check (scripts/check_app.sh)"
appdir="$(mktemp -d)"; mkdir -p "$appdir/Sequence Diagram.app"
if MSD_APP_PATH="$appdir/Sequence Diagram.app" scripts/check_app.sh >/dev/null 2>&1; then echo "  ok    installed app found"
else echo "  FAIL  installed app not found"; fail=1; fi
if MSD_APP_PATH="$appdir/missing.app" scripts/check_app.sh >/dev/null 2>&1; then echo "  FAIL  missing app reported as installed"; fail=1
else echo "  ok    missing app reported"; fi
rm -rf "$appdir"

echo "self-update (scripts/update.sh)"
tests/test_update.sh || fail=1

echo "release metadata"
lint_ver="$(python3 -c "import sys; sys.path.insert(0,'scripts'); import lint_msd; print(lint_msd.__version__)")"
if [ "$(cat VERSION)" = "$lint_ver" ]; then echo "  ok    VERSION $lint_ver = lint_msd.__version__"
else echo "  FAIL  VERSION $(cat VERSION) != lint_msd.__version__ $lint_ver"; fail=1; fi
desc_len="$(python3 - <<'PY'
import re
fm = open("SKILL.md").read().split("---")[1]
m = re.search(r"description: >-\n((?:  .*\n)+)", fm)
print(len(" ".join(l.strip() for l in m.group(1).splitlines())) if m else -1)
PY
)"
if grep -q '^name: msd-sequence-diagram$' SKILL.md && [ "$desc_len" -gt 0 ] && [ "$desc_len" -le 1024 ]; then
  echo "  ok    SKILL.md frontmatter: name, description $desc_len/1024 chars"
else echo "  FAIL  SKILL.md frontmatter: name or description ($desc_len chars, max 1024)"; fail=1; fi

[ "$fail" -eq 0 ] && echo "all passed" || { echo "FAILED"; exit 1; }
