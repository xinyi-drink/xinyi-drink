#!/bin/sh
set -eu

SKILL_NAME="xinyi-drink"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PLATFORM=""
DRY_RUN=false

while [ $# -gt 0 ]; do
  case "$1" in
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -h|--help)
      cat <<EOF
用法：
  ./install.sh [--platform 平台] [--dry-run]

支持的平台：
  claude-code
  cursor
  universal
  codex
  openclaw
  hermes
  qclaw
  lobsterai
  workbuddy

说明：
  - openclaw / hermes / qclaw / lobsterai / workbuddy / codex 统一安装到 ~/.agents/skills/
  - claude-code 安装到 ~/.claude/skills/
  - cursor 安装到 .cursor/rules/
EOF
      exit 0
      ;;
    *)
      echo "未知参数: $1" >&2
      exit 1
      ;;
  esac
done

if [ -z "$PLATFORM" ]; then
  if [ -d "$HOME/.claude" ]; then
    PLATFORM="claude-code"
  elif [ -d "$HOME/.agents" ]; then
    PLATFORM="universal"
  else
    PLATFORM="universal"
  fi
fi

case "$PLATFORM" in
  claude-code)
    DEST="$HOME/.claude/skills/$SKILL_NAME"
    ;;
  universal|codex|openclaw|hermes|qclaw|lobsterai|lobsterAI|workbuddy)
    DEST="$HOME/.agents/skills/$SKILL_NAME"
    ;;
  cursor)
    DEST=".cursor/rules/$SKILL_NAME"
    ;;
  *)
    echo "不支持的平台: $PLATFORM" >&2
    exit 2
    ;;
esac

if $DRY_RUN; then
  echo "[DRY-RUN] 平台: $PLATFORM"
  echo "[DRY-RUN] 将安装 $SKILL_NAME 到: $DEST"
  exit 0
fi

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -R "$SCRIPT_DIR" "$DEST"
echo "已安装 $SKILL_NAME 到 $DEST"
