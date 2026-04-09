#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <youtube-url> [language]" >&2
  exit 1
fi

url="$1"
lang="${2:-en}"

tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

# Convert via markitdown, write to temp file
python3 "$SCRIPT_DIR/yt2md.py" "$url" -l "$lang" -o "$tmpfile"

# Extract video title from the first h2 heading (h1 is just "YouTube")
title=$(head -10 "$tmpfile" | grep -m1 '^## ' | sed 's/^## //')

if [ -z "$title" ]; then
  echo "Error: could not extract video title from transcript" >&2
  exit 1
fi

# Sanitize: spaces to underscores, strip anything not alphanumeric/underscore/hyphen
filename=$(echo "$title" | sed 's/ /_/g; s/[^a-zA-Z0-9_-]//g')

mv "$tmpfile" "${filename}.md"
echo "Written to ${filename}.md" >&2
