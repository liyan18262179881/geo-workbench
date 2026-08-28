#!/usr/bin/env bash
# 将合并后的 GEO 工作台打包到桌面
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
STAMP="$(TZ=Asia/Shanghai date '+%m%d-%H%M')"
DEST_NAME="GEO工作台_${STAMP}_V1"
DESKTOP="${HOME}/Desktop"
DEST="${DESKTOP}/${DEST_NAME}"

mkdir -p "$DESKTOP" "$DEST/seeds"

cp "$ROOT/index.html" "$ROOT/server.py" "$ROOT/recover.py" "$DEST/"
cp "$ROOT/seeds/restore-GEO工作台.json" "$DEST/seeds/"

cat > "$DEST/启动.command" << 'LAUNCH'
#!/bin/bash
cd "$(dirname "$0")"
if ! python3 -c "import anthropic, openai" 2>/dev/null; then
  pip3 install anthropic openai
fi
python3 recover.py --restore-preset 2>/dev/null || true
echo ""
echo "✅ 打开浏览器访问 http://localhost:8765"
python3 server.py
LAUNCH
chmod +x "$DEST/启动.command"

cat > "$DEST/README.txt" << 'README'
GEO 工作台 · 完整项目（合并版）

这是可独立运行的 GEO 工作台项目文件夹，已合并原「GEO工作台」与「GEO项目」为单一客户数据。

目录说明：
  index.html   — 主程序
  server.py    — 本地服务
  recover.py   — 数据恢复脚本
  geo.db       — 客户数据库（已预置合并客户）
  seeds/       — 备份种子数据
  启动.command — macOS 双击启动

启动：
  macOS：双击「启动.command」
  终端：python3 server.py
  浏览器：http://localhost:8765

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

echo "✅ 已创建：$DEST"
ls -la "$DEST"
