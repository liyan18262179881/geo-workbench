#!/bin/bash
# 项目文件夹丢失时：从 GitHub 重新下载到桌面并启动
set -euo pipefail

echo ""
echo "══════════════════════════════════════════"
echo "  GEO 工作台 · 恢复到桌面"
echo "══════════════════════════════════════════"
echo ""

# 桌面路径（支持中文「桌面」）
if [[ -d "${HOME}/Desktop" ]]; then
  DESKTOP="${HOME}/Desktop"
elif [[ -d "${HOME}/桌面" ]]; then
  DESKTOP="${HOME}/桌面"
else
  DESKTOP="${HOME}/Desktop"
  mkdir -p "$DESKTOP"
fi

STAMP="$(date '+%m%d-%H%M')"
DEST="${DESKTOP}/GEO工作台_${STAMP}_恢复"
ALIAS="${DESKTOP}/GEO工作台"

if ! command -v git >/dev/null 2>&1; then
  echo "❌ 需要先安装 git"
  echo "   终端执行：xcode-select --install"
  read -p "按回车关闭…"
  exit 1
fi

echo "📥 正在从 GitHub 下载到："
echo "   $DEST"
echo ""

rm -rf "$DEST"
git clone --depth 1 -b cursor/restore-deleted-projects-d21a \
  https://github.com/liyan18262179881/geo-workbench.git "$DEST"

chmod +x "$DEST/start.sh" "$DEST/启动.command" 2>/dev/null || true

# 桌面固定入口
rm -rf "$ALIAS"
ln -sf "$DEST" "$ALIAS"

echo ""
echo "✅ 已恢复到桌面："
echo "   $DEST"
echo "   快捷方式：$ALIAS"
echo ""

open "$DESKTOP"
osascript -e 'display notification "GEO工作台 已恢复到桌面" with title "GEO 工作台"' 2>/dev/null || true

echo "即将启动服务并打开浏览器…"
sleep 1
cd "$DEST"
exec ./start.sh
