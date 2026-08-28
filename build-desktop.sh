#!/usr/bin/env bash
# 将合并后的 GEO 工作台打包到桌面（支持 macOS 中文「桌面」路径）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
STAMP="$(TZ=Asia/Shanghai date '+%m%d-%H%M')"
DEST_NAME="GEO工作台_${STAMP}_V1"
ALIAS_NAME="GEO工作台"

# macOS 中文系统桌面可能是「桌面」
if [[ -d "${HOME}/Desktop" ]]; then
  DESKTOP="${HOME}/Desktop"
elif [[ -d "${HOME}/桌面" ]]; then
  DESKTOP="${HOME}/桌面"
else
  DESKTOP="${HOME}/Desktop"
  mkdir -p "$DESKTOP"
fi

DEST="${DESKTOP}/${DEST_NAME}"
ALIAS="${DESKTOP}/${ALIAS_NAME}"

rm -rf "$DEST"
mkdir -p "$DEST/seeds"

cp "$ROOT/index.html" "$ROOT/server.py" "$ROOT/recover.py" "$ROOT/start.sh" "$DEST/"
chmod +x "$DEST/start.sh"
cp "$ROOT/seeds/restore-GEO工作台.json" "$DEST/seeds/"

cat > "$DEST/启动.command" << 'LAUNCH'
#!/bin/bash
cd "$(dirname "$0")"
exec ./start.sh
LAUNCH
chmod +x "$DEST/启动.command"

cat > "$DEST/README.txt" << 'README'
GEO 工作台 · 完整项目（合并版）

已将「GEO工作台」与「GEO项目」合并为单一客户。

启动：双击「启动.command」或运行 python3 server.py
访问：http://localhost:8765
侧栏客户：GEO工作台（约 20 个关键词）

依赖：pip3 install anthropic openai
README

cd "$DEST"
python3 -c "
import json, sqlite3
from datetime import datetime
seed = json.load(open('seeds/restore-GEO工作台.json', encoding='utf-8'))
conn = sqlite3.connect('geo.db')
conn.execute('''CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY, owner_id TEXT DEFAULT 'local', data TEXT NOT NULL, updated_at TEXT)''')
conn.execute('''CREATE TABLE IF NOT EXISTS clients_trash (
    id TEXT PRIMARY KEY, owner_id TEXT DEFAULT 'local', data TEXT NOT NULL, deleted_at TEXT NOT NULL)''')
now = datetime.now().isoformat(timespec='seconds')
for cid, cdata in seed['clients'].items():
    conn.execute('INSERT OR REPLACE INTO clients VALUES(?,?,?,?)',
        (cid, 'local', json.dumps(cdata, ensure_ascii=False), now))
conn.commit()
n = conn.execute('SELECT COUNT(*) FROM clients').fetchone()[0]
conn.close()
print(f'geo.db 已写入 {n} 个合并客户')
"

# 桌面快捷入口：固定名 GEO工作台 → 指向本次版本文件夹
rm -rf "$ALIAS"
ln -sf "$DEST" "$ALIAS"

echo ""
echo "════════════════════════════════════════"
echo "✅ 合并版 GEO 工作台已放到桌面"
echo "   文件夹：$DEST"
echo "   快捷入口：$ALIAS"
echo "════════════════════════════════════════"
ls -la "$DEST"
if [[ "$(uname)" == "Darwin" ]]; then
  open "$DESKTOP" 2>/dev/null || true
fi
