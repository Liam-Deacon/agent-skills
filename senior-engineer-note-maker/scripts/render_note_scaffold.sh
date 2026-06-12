#!/usr/bin/env bash
set -euo pipefail

TYPE=""
TITLE=""
REPO="your-repo"
DOC_PATH="docs/TODO.md"
DOC_TYPE="documentation"
CATEGORY="engineering"
AUDIENCE="llm-agent"
STATUS="draft"
VISIBILITY="internal"
SYNC="false"
DATE="$(date +%F)"
EMAILS=""
NAMES=""
HANDLES=""

usage() {
  cat <<'USAGE'
Usage: render_note_scaffold.sh --type <doc|pr|issue|comment> --title <title> [options]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type) TYPE="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --path) DOC_PATH="$2"; shift 2 ;;
    --doc-type) DOC_TYPE="$2"; shift 2 ;;
    --category) CATEGORY="$2"; shift 2 ;;
    --audience) AUDIENCE="$2"; shift 2 ;;
    --status) STATUS="$2"; shift 2 ;;
    --visibility) VISIBILITY="$2"; shift 2 ;;
    --sync) SYNC="$2"; shift 2 ;;
    --date) DATE="$2"; shift 2 ;;
    --author-email) EMAILS="$2"; shift 2 ;;
    --author-name) NAMES="$2"; shift 2 ;;
    --author-handle) HANDLES="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$TYPE" || -z "$TITLE" ]]; then
  usage
  exit 1
fi

slugify() { echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'; }
trim() { echo "$1" | sed -E 's/^\s+//; s/\s+$//'; }

emit_authors() {
  local source=""
  if [[ -n "$EMAILS" ]]; then
    source="$EMAILS"
  elif [[ -n "$NAMES" ]]; then
    source="$NAMES"
  elif [[ -n "$HANDLES" ]]; then
    source="$HANDLES"
  else
    source="@unknown-author"
  fi

  IFS=',' read -r -a arr <<< "$source"
  for raw in "${arr[@]}"; do
    v="$(trim "$raw")"
    [[ -n "$v" ]] && printf '  - "%s"\n' "$v"
  done
}

if [[ "$TYPE" == "doc" ]]; then
  slug="$(slugify "$TITLE")"
  cat <<DOC
---
id: ${REPO}/${slug}
title: "${TITLE}"
summary: "TODO: Add concise summary (10-500 chars)."
repo: ${REPO}
path: ${DOC_PATH}
type: ${DOC_TYPE}
category: ${CATEGORY}
intended_audience:
DOC
  IFS=',' read -r -a aud <<< "$AUDIENCE"
  for a in "${aud[@]}"; do
    aa="$(trim "$a")"
    [[ -n "$aa" ]] && printf '  - %s\n' "$aa"
  done
  cat <<DOC2
status: ${STATUS}
visibility: ${VISIBILITY}
created_at: ${DATE}
updated_at: ${DATE}
authors:
DOC2
  emit_authors
  cat <<DOC3
sync: ${SYNC}
---

# ${TITLE}

## Context

TODO

## Decision

TODO

## Comparison Summary

| Option | Complexity | Risk | Rationale |
| ------ | ---------- | ---- | --------- |
| A      | TODO       | TODO | TODO      |
| B      | TODO       | TODO | TODO      |

## Flow

~~~text
Input --> Process --> Output
~~~

## Evidence

- TODO: Add code/repo links

## References

[1]: https://example.com
DOC3
  exit 0
fi

cat <<OTHER
## Summary

TODO

## Details

| Area | Change | Impact |
| ---- | ------ | ------ |
| TODO | TODO   | TODO   |

## Flow

~~~text
Caller --> Component --> Result
~~~

## Evidence

- TODO: Add permalink with line range
<!-- permalink-meta: branch=<branch>, timestamp=$(date -u +%FT%TZ) -->

## References

[1]: https://example.com
OTHER
