#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="$ROOT/config.json"
DATE="$(TZ=Asia/Shanghai date +%F)"
REPORT="$ROOT/reports/aihot-crossborder-$DATE.md"
LAST_PUBLISHED="$ROOT/state/last_published_date"
FORCE=0

if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
fi

if [[ ! -f "$CONFIG" ]]; then
  echo "Missing config: $CONFIG" >&2
  exit 1
fi

if [[ "$FORCE" != "1" && -f "$LAST_PUBLISHED" && "$(cat "$LAST_PUBLISHED")" == "$DATE" ]]; then
  echo "Already published for $DATE. Use --force to republish." >&2
  exit 0
fi

python3 "$ROOT/scripts/generate_report.py" \
  --days 3 \
  --sources aihot,hex2077,amazonnews \
  --output "$REPORT" \
  --state-dir "$ROOT/state"

DOC="$(jq -r '.feishu_doc_url // empty' "$CONFIG")"
IDENTITY="$(jq -r '.lark_identity // "bot"' "$CONFIG")"

if [[ -z "$DOC" || "$DOC" == "null" ]]; then
  echo "Missing feishu_doc_url in $CONFIG" >&2
  exit 1
fi

python3 /Users/wesleyzane/.codex/skills/lark-report-publisher/scripts/publish_to_lark.py \
  --input-file "$REPORT" \
  --doc "$DOC" \
  --as "$IDENTITY"

printf "%s" "$DATE" > "$LAST_PUBLISHED"
echo "Published $REPORT to Feishu document."
