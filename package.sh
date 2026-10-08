#!/usr/bin/env bash
# Build dist/msd-sequence-diagram.zip for upload to claude.ai (Settings → Capabilities → Skills).
# Only the skill itself goes in: SKILL.md, references/, scripts/. Repo files (README, tests,
# this script) stay out. The archive holds one top-level folder named like the skill.
set -euo pipefail
cd "$(dirname "$0")"
name="$(sed -n 's/^name: *//p' SKILL.md | head -1)"
[ -n "$name" ] || { echo "no 'name:' in SKILL.md frontmatter" >&2; exit 1; }
tests/run.sh
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
mkdir -p "$stage/$name" dist
cp SKILL.md "$stage/$name/"
cp -R references scripts "$stage/$name/"
find "$stage" \( -name '__pycache__' -o -name '.DS_Store' -o -name '*.pyc' \) -exec rm -rf {} +
rm -f "dist/$name.zip"
(cd "$stage" && zip -r -X -q "$OLDPWD/dist/$name.zip" "$name")
unzip -l "dist/$name.zip"
echo "built dist/$name.zip"
