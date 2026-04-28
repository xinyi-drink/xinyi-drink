#!/bin/sh
set -eu

SKILL_NAME="xinyi-drink"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PLATFORM=""
DRY_RUN=false

while [ $# -gt 0 ]; do
  case "$1" in
    --platform)
      if [ $# -lt 2 ]; then
        echo "--platform 需要指定平台名称" >&2
        exit 1
      fi
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
  claude-code   -> ~/.claude/skills/
  cursor        -> .cursor/rules/
  codex         -> ~/.agents/skills/
  openclaw      -> ~/.openclaw/skills/
  hermes        -> ~/.hermes/skills/
  qclaw         -> ~/.agents/skills/
  lobsterai     -> ~/.agents/skills/
  workbuddy     -> ~/.agents/skills/
  universal     -> ~/.agents/skills/

说明：
  - openclaw 安装到 ~/.openclaw/skills/
  - hermes 安装到 ~/.hermes/skills/
  - qclaw / lobsterai / workbuddy / codex / universal 安装到 ~/.agents/skills/
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
  if [ -d "$HOME/.openclaw" ]; then
    PLATFORM="openclaw"
  elif [ -d "$HOME/.hermes" ]; then
    PLATFORM="hermes"
  elif [ -d "$HOME/.claude" ]; then
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
  openclaw)
    DEST="$HOME/.openclaw/skills/$SKILL_NAME"
    ;;
  hermes)
    DEST="$HOME/.hermes/skills/$SKILL_NAME"
    ;;
  universal|codex|qclaw|lobsterai|lobsterAI|workbuddy)
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

case "$DEST" in
  ""|"/"|"$HOME"|"$HOME/")
    echo "安装目标路径异常，已拒绝覆盖: $DEST" >&2
    exit 3
    ;;
esac

if $DRY_RUN; then
  echo "[DRY-RUN] 平台: $PLATFORM"
  echo "[DRY-RUN] 将安装 $SKILL_NAME 到: $DEST"
  echo "[DRY-RUN] 不会发起网络请求，不会读取或写入手机号状态"
  exit 0
fi

mkdir -p "$(dirname "$DEST")"
if [ -e "$DEST" ]; then
  BACKUP="$DEST.backup.$(date +%Y%m%d%H%M%S)"
  if [ -e "$BACKUP" ]; then
    BACKUP_INDEX=1
    while [ -e "$BACKUP.$BACKUP_INDEX" ]; do
      BACKUP_INDEX=$((BACKUP_INDEX + 1))
    done
    BACKUP="$BACKUP.$BACKUP_INDEX"
  fi
  mv "$DEST" "$BACKUP"
  echo "已备份旧版本到 $BACKUP"
fi
cp -R "$SCRIPT_DIR" "$DEST"
find "$DEST" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "$DEST" -name '.DS_Store' -delete
cat <<EOF
已安装 $SKILL_NAME 到 $DEST

安装完成后，你可以在新会话中这样使用：
  /xinyi-drink 给我推荐一杯适合当下午茶的饮品。

如果当前平台支持自然触发，也可以直接问：
  某某饮品热量多少？
  新一咖啡有哪些门店？
  望京店目前有多少杯待做，等待时间多久？

隐私提示：
  - 普通推荐、门店和菜单查询不会自动复用缓存手机号。
  - 参与活动、查询活动状态、活动总览、订单摘要或口味偏好分析时，手机号会发送到配置的后端；默认后端见 config/defaults.json。
  - 可通过 XINYI_API_BASE_URL 指向你信任的后端。
  - 本地手机号状态默认保存到 ~/.xinyi-drink/state.json。
  - 清空缓存可运行：python3 "$DEST/scripts/recommend_drink.py" --clear-mobile
EOF
