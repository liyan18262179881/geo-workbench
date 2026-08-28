#!/bin/bash
# 在本机查找 GEO 工作台项目文件夹
echo ""
echo "══════════════════════════════════════════"
echo "  GEO 工作台 · 查找本机项目文件夹"
echo "══════════════════════════════════════════"
echo ""

FOUND_NEW=0
FOUND_OLD=0

check_dir() {
  local dir="$1"
  local idx="$dir/index.html"
  [[ -f "$dir/server.py" && -f "$idx" ]] || return 1
  if grep -qE "词位雷达|引用溯源|久胜云数|客户管理" "$idx" 2>/dev/null; then
    echo "★ 新版（截图界面）"
    echo "   $dir"
    if [[ -f "$dir/start.sh" ]]; then
      echo "   启动：cd \"$dir\" && ./start.sh"
    else
      echo "   启动：cd \"$dir\" && python3 server.py"
    fi
    echo "   浏览器：http://localhost:8765"
    echo ""
    FOUND_NEW=$((FOUND_NEW+1))
    return 0
  fi
  if grep -qE "GEO 工作台|GEO工作台" "$idx" 2>/dev/null; then
    echo "· 仓库版（本地生活老界面）"
    echo "   $dir"
    echo "   启动：cd \"$dir\" && ./start.sh  或 python3 server.py"
    echo ""
    FOUND_OLD=$((FOUND_OLD+1))
    return 0
  fi
  return 1
}

for base in \
  "$HOME/Desktop" "$HOME/桌面" \
  "$HOME/Documents" "$HOME/Downloads" \
  "$HOME/Documents/GEO产品" \
  "/Users/chenbo/Documents/GEO产品" \
  "$HOME/geo-workbench" "$HOME/Developer"
do
  [[ -d "$base" ]] || continue
  while IFS= read -r -d '' sf; do
    check_dir "$(dirname "$sf")" || true
  done < <(find "$base" -maxdepth 7 -name "server.py" -print0 2>/dev/null)
done

echo "──────────────────────────────────────────"
echo "常见路径检查："
for p in \
  "$HOME/Desktop/GEO工作台" \
  "$HOME/桌面/GEO工作台" \
  "$HOME/Documents/GEO产品/GEO工作台" \
  "/Users/chenbo/Documents/GEO产品/GEO工作台"
do
  if [[ -d "$p" ]]; then
    echo "  ✅ $p"
    check_dir "$p" || echo "     （有文件夹但可能不是 GEO 工作台）"
  else
    echo "  · 无：$p"
  fi
done

echo ""
if [[ $FOUND_NEW -eq 0 && $FOUND_OLD -eq 0 ]]; then
  echo "❌ 未找到项目。可从 GitHub 下载到桌面："
  echo ""
  echo "  cd ~/Desktop"
  echo "  git clone -b cursor/restore-deleted-projects-d21a \\"
  echo "    https://github.com/liyan18262179881/geo-workbench.git GEO工作台"
  echo "  cd GEO工作台 && ./start.sh"
fi

echo ""
read -p "按回车关闭…"
