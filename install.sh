#!/usr/bin/env bash
set -euo pipefail

TARGET="codex"
DEST=""
REF="main"
REPO="WaytoAIC/ai-news-crossborder-skills"
LINK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:?missing --target value}"
      shift 2
      ;;
    --dest)
      DEST="${2:?missing --dest value}"
      shift 2
      ;;
    --ref)
      REF="${2:?missing --ref value}"
      shift 2
      ;;
    --repo)
      REPO="${2:?missing --repo value}"
      shift 2
      ;;
    --link)
      LINK=1
      shift
      ;;
    -h|--help)
      sed -n '1,120p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$DEST" ]]; then
  case "$TARGET" in
    codex)
      DEST="${CODEX_HOME:-$HOME/.codex}/skills"
      ;;
    openclaw)
      DEST="$HOME/.openclaw/skills"
      ;;
    *)
      echo "Unsupported target: $TARGET" >&2
      exit 2
      ;;
  esac
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"
TMP_DIR=""

if [[ ! -d "$WORK_DIR/skills" ]]; then
  TMP_DIR="$(mktemp -d)"
  git clone --depth 1 --branch "$REF" "https://github.com/$REPO.git" "$TMP_DIR/repo"
  WORK_DIR="$TMP_DIR/repo"
fi

mkdir -p "$DEST"

for skill_dir in "$WORK_DIR"/skills/*; do
  [[ -d "$skill_dir" ]] || continue
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  name="$(basename "$skill_dir")"
  target_path="$DEST/$name"
  rm -rf "$target_path"
  if [[ "$LINK" == "1" && "$WORK_DIR" == "$SCRIPT_DIR" ]]; then
    ln -s "$skill_dir" "$target_path"
  else
    cp -R "$skill_dir" "$target_path"
  fi
  echo "Installed $name -> $target_path"
done

if [[ -n "$TMP_DIR" ]]; then
  rm -rf "$TMP_DIR"
fi

echo "Install complete. Restart Codex to pick up newly installed skills."
