#!/bin/bash
# 在本机查找 GEO 工作台项目文件夹（新版 + 老版 + 桌面副本）
set -euo pipefail

echo ""
echo "══════════════════════════════════════════════════"
echo "  GEO 工作台 · 本机项目查找"
echo "══════════════════════════════════════════════════"
echo ""

FOUND_NEW=0
FOUND_OLD=0
FOUND_ANY=0

mark() {
  local dir="$1"
  local kind="$2"
  FOUND_ANY=$((FOUND_ANY+1))
  echo "────────────────────────────────────────"
  echo "📁 $dir"
  echo "   类型：$kind"
  if [[ -f "$dir/start.sh" ]]; then
    echo "   启动：cd \"$dir\" && ./start.sh"
  else
    echo "   启动：cd \"$dir\" && python3 server.py"
  fi
  echo "   地址：http://localhost:8765"
}

search_in() {
  local base="$1"
  [[ -d "$base" ]] || return 0
  while IFS= read -r -d '' f; do
    local dir
    dir="$(dirname "$f")"
  if grep -q "词位雷达\|引用溯源图\|久胜云数\|客户管理" "$f" 2>/dev/null; then
      mark "$dir" "新版（词位雷达 / 久胜云数）"
      FOUND_NEW=$((FOUND_NEW+1))
    elif grep -q "GEO 工作台\|GEO工作台" "$f" 2>/dev/null && [[ -f "$dir/server.py" ]]; then
      mark "$dir" "GEO 工作台（本地生活版 / 仓库版）"
      FOUND_OLD=$((FOUND_OLD+1))
    fi
  done < <(find "$base" -maxdepth 6 \( -name "index.html" -o -name "server.py" \) -print0 2>/dev/null | while IFS= read -r -d '' p; do
    [[ "$p" == *server.py ]] && echo -n "${p%/*}"$'\0' || true
  done)
  # also find by index.html
  while IFS= read -r -d '' f; do
    local dir="$(dirname "$f")"
    [[ -f "$dir/server.py" ]] || continue
    if grep -q "词位雷达\|引用溯源图\|久胜云数\|客户管理" "$f" 2>/dev/null; then
      : # already counted
    elif grep -q "GEO 工作台\|GEO工作台" "$f" 2>/dev/null; then
      : # already counted  
    fi
  done < <(find "$base" -maxdepth 6 -name "index.html" -print0 2>/dev/null)
}

# 用 server.py 精确查找（最可靠）
for base in \
  "$HOME/Desktop" \
  "$HOME/桌面" \
  "$HOME/Documents" \
  "$HOME/Downloads" \
  "$HOME/Documents/GEO产品" \
  "/Users/chenbo/Documents/GEO产品" \
  "$HOME/geo-workbench" \
  "$HOME/Developer" \
  "$HOME/Projects"
do
  [[ -d "$base" ]] || continue
  while IFS= read -r -d '' sf; do
  dir="$(dirname "$sf")"
  idx="$dir/index.html"
  [[ -f "$idx" ]] || continue
  if grep -q "词位雷达\|引用溯源图\|久胜云数\|客户管理" "$idx" 2>/dev/null; then
    mark "$dir" "★ 新版（你截图里的界面）"
    FOUND_NEW=$((FOUND_NEW+1))
  elif grep -q "GEO 工作台\|GEO工作台" "$idx" 2>/dev/null; then
    mark "$dir" "仓库版 / 本地生活版"
    FOUND_OLD=$((FOUND_OLD+1))
  fi
  done < <(find "$base" -maxdepth 7 -name "server.py" -print0 2>/dev/null)
done

echo ""
if [[ $FOUND_NEW -gt 0 ]]; then
  echo "✅ 找到 $FOUND_NEW 个新版项目，请用上面「★ 新版」路径启动。"
elif [[ $FOUND_OLD -gt 0 ]]; then
  echo "⚠️  只找到仓库老版（不是截图里的新版）。"
  echo "   新版可能在其他磁盘或未保存，见下方「重新下载」。"
else
  echo "❌ 本机未找到 GEO 工作台文件夹。"
fi

echo ""
echo "══════════════════════════════════════════════════"
echo "  常见位置（可直接在 Finder 前往文件夹粘贴）"
echo "══════════════════════════════════════════════════"
for p in \
  "$HOME/Desktop/GEO工作台" \
  "$HOME/桌面/GEO工作台" \
  "$HOME/Documents/GEO产品/GEO工作台" \
  "/Users/chenbo/Documents/GEO产品/GEO工作台" \
  "$HOME/Documents/geo-workbench"
do
  if [[ -d "$p" ]]; then
    echo "  ✅ 存在：$p"
  else
    echo "  · 不存在：$p"
  fi
done

echo ""
echo "══════════════════════════════════════════════════"
echo "  没有项目？一键下载到桌面"
echo "══════════════════════════════════════════════════"
read -p "是否从 GitHub 下载到桌面？(y/n) " yn
if [[ "${yn,,}" == "y" || "${yn,,}" == "yes" ]]; then
  DESKTOP="${HOME}/Desktop"
  [[ -d "$HOME/桌面" ]] && DESKTOP="$HOME/桌面"
  DEST="${DESKTOP}/GEO工作台_下载版"
  rm -rf "$DEST"
  echo "正在下载…"
  if command -v git >/dev/null 2>&1; then
    git clone --depth 1 -b cursor/restore-deleted-projects-d21a \
      https://github.com/liyan18262179881/geo-workbench.git "$DEST"
    chmod +x "$DEST/start.sh" "$DEST/启动.command" 2>/dev/null || true
    open "$DEST"
    echo "✅ 已下载到：$DEST"
    echo "   双击「启动.command」或运行 ./start.sh"
  else
    echo "❌ 需要安装 git，或浏览器打开："
    echo "   https://github.com/liyan18262179881/geo-workbench"
  fi
fi

echo ""
read -p "按回车关闭窗口…"
