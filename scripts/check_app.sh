#!/usr/bin/env bash
# Is the Sequence Diagram app installed? Exit 0 and print its path and version, or
# exit 1 with where to get it. MSD_APP_PATH overrides the location (used by tests).
set -uo pipefail
app="${MSD_APP_PATH:-/Applications/Sequence Diagram.app}"
if [ -d "$app" ]; then
  ver="$(defaults read "$app/Contents/Info" CFBundleShortVersionString 2>/dev/null || true)"
  echo "Sequence Diagram: $app${ver:+ (version $ver)}"
  exit 0
fi
echo "Sequence Diagram is not installed at $app." >&2
echo "The .msd files open in Sequence Diagram for Mac: https://www.macsequencediagram.com (Mac App Store)." >&2
exit 1
