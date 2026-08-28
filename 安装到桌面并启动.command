#!/bin/bash
# 双击运行：把合并版 GEO 工作台复制到 Mac 桌面并启动
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
STAMP="$(date '+%m%d-%H%M')"
DEST_NAME="GEO工作台_${STAMP}_V1"

if [[ -d "${HOME}/Desktop" ]]; then
  DESKTOP="${HOME}/Desktop"
elif [[ -d "${HOME}/桌面" ]]; then
  DESKTOP="${HOME}/桌面"
else
  DESKTOP="${HOME}/Desktop"
  mkdir -p "$DESKTOP"
fi

DEST="${DESKTOP}/${DEST_NAME}"
ALIAS="${DESKTOP}/GEO工作台"

echo "正在复制到桌面…"
rm -rf "$DEST"
mkdir -p "$DEST"
cp "$ROOT/index.html" "$ROOT/server.py" "$ROOT/recover.py" "$ROOT/start.sh" "$DEST/"
cp -R "$ROOT/seeds" "$DEST/"

# 写入合并客户数据库
python3 -c "
import json, sqlite3, os
from datetime import datetime
os.chdir('$DEST')
seed = json.load(open('seeds/restore-GEO工作台.json', encoding='utf-8'))
conn = sqlite3.connect('geo.db')
conn.execute('CREATE TABLE IF NOT EXISTS clients (id TEXT PRIMARY KEY, owner_id TEXT DEFAULT \"local\", data TEXT NOT NULL, updated_at TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS clients_trash (id TEXT PRIMARY KEY, owner_id TEXT DEFAULT \"local\", data TEXT NOT NULL, deleted_at TEXT NOT NULL)')
now = datetime.now().isoformat(timespec='seconds')
for cid, cdata in seed['clients'].items():
    conn.execute('INSERT OR REPLACE INTO clients VALUES(?,?,?,?)', (cid, 'local', json.dumps(cdata, ensure_ascii=False), now))
conn.commit(); conn.close()
print('geo.db OK')
"

cat > "$DEST/启动.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
exec ./start.sh
EOF
chmod +x "$DEST/启动.command"
cp "$ROOT/start.sh" "$DEST/"
chmod +x "$DEST/start.sh"

rm -rf "$ALIAS"
ln -sf "$DEST" "$ALIAS"

open "$DESKTOP"
osascript -e "display notification \"桌面已出现 GEO工作台 文件夹\" with title \"GEO 工作台\""

echo ""
echo "✅ 已放到桌面：$ALIAS"
echo "   双击「GEO工作台/启动.command」启动"
read -p "按回车立即启动…" _
open "$DEST/启动.command"
