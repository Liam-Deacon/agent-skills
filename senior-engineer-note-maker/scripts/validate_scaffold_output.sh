#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENDER="$DIR/render_note_scaffold.sh"

check_contains() {
  local haystack="$1"
  local needle="$2"
  local msg="$3"
  if ! grep -Fq "$needle" <<<"$haystack"; then
    echo "FAIL: $msg" >&2
    exit 1
  fi
}

out_email="$($RENDER --type doc --title "Test Doc" --author-email "person@example.com" --author-name "Person Name" --author-handle "@person")"
check_contains "$out_email" '  - "person@example.com"' "email priority failed"

out_name="$($RENDER --type doc --title "Test Doc" --author-name "Person Name" --author-handle "@person")"
check_contains "$out_name" '  - "Person Name"' "name priority failed"

out_handle="$($RENDER --type doc --title "Test Doc" --author-handle "@person")"
check_contains "$out_handle" '  - "@person"' "handle fallback failed"

check_contains "$out_email" 'id: your-repo/test-doc' "id generation failed"
check_contains "$out_email" 'sync: false' "sync default missing"

echo "PASS: scaffold output validation succeeded"
