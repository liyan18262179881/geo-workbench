#!/bin/bash
# 下载 GEO工作台_0828-1426_V1.zip 到 Mac 桌面并解压
set -euo pipefail

if [[ -d "${HOME}/Desktop" ]]; then
  DESKTOP="${HOME}/Desktop"
elif [[ -d "${HOME}/桌面" ]]; then
  DESKTOP="${HOME}/桌面"
else
  DESKTOP="${HOME}/Desktop"
  mkdir -p "$DESKTOP"
fi

ZIP_NAME="GEO工作台_0828-1426_V1.zip"
FOLDER_NAME="GEO工作台_0828-1426_V1"
URL="https://github.com/liyan18262179881/geo-workbench/raw/master/dist/GEO工作台_0828-1426_V1.zip"

cd "$DESKTOP"

echo "📥 正在下载到桌面…"
echo "   $DESKTOP/$ZIP_NAME"

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$ZIP_NAME"
else
  echo "❌ 需要 curl，或浏览器手动下载："
  echo "   $URL"
  read -p "按回车关闭…"
  exit 1
fi

echo "📂 正在解压…"
rm -rf "$FOLDER_NAME"
unzip -o "$ZIP_NAME" -d "$FOLDER_NAME"

chmod +x "$FOLDER_NAME/start.sh" "$FOLDER_NAME/启动.command" 2>/dev/null || true

rm -f "$DESKTOP/GEO工作台"
ln -sf "$DESKTOP/$FOLDER_NAME" "$DESKTOP/GEO工作台"

open "$DESKTOP"
osascript -e 'display notification "GEO工作台 已放到桌面" with title "GEO 工作台"' 2>/dev/null || true

echo ""
echo "✅ 已完成："
echo "   $DESKTOP/$ZIP_NAME"
echo "   $DESKTOP/$FOLDER_NAME"
echo "   $DESKTOP/GEO工作台 → 快捷入口"
echo ""
read -p "按回车启动工作台…" _
cd "$FOLDER_NAME"
exec ./start.sh
