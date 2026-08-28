#!/bin/bash
# 在本机查找「新版 GEO 工作台」（含词位雷达 / 久胜云数 等特征）
echo "正在搜索新版 GEO 工作台…"
echo ""

FOUND=0
for base in \
  "$HOME/Documents" \
  "$HOME/Desktop" \
  "/Users/chenbo/Documents/GEO产品" \
  "$HOME/Documents/GEO产品"
do
  [[ -d "$base" ]] || continue
  while IFS= read -r -d '' f; do
    if grep -q "词位雷达\|引用溯源\|久胜云数\|客户管理" "$f" 2>/dev/null; then
      dir="$(dirname "$f")"
      echo "✅ 找到新版：$dir"
      echo "   启动：cd \"$dir\" && python3 server.py"
      echo "   浏览器：http://localhost:8765"
      FOUND=$((FOUND+1))
    fi
  done < <(find "$base" -maxdepth 5 -name "index.html" -print0 2>/dev/null)
done

if [[ $FOUND -eq 0 ]]; then
  echo "❌ 未在本机找到新版界面文件。"
  echo ""
  echo "当前 GitHub 仓库 geo-workbench 是「本地生活版」老界面。"
  echo "你截图里的新版（词位雷达、久胜云数）只在本机某目录，尚未同步到 GitHub。"
  echo ""
  echo "请回忆新版保存在哪个文件夹，或把该文件夹里的 index.html 发我合并进仓库。"
fi
