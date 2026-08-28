#!/usr/bin/env python3
"""
GEO 工作台 · 客户数据恢复工具

用法（在项目目录下运行）：
  python3 recover.py              # 扫描可恢复来源并列出
  python3 recover.py --restore-all # 从回收站 + 最新备份恢复全部
  python3 recover.py --from-backup geo-backup-20260614-140000.json
"""
import argparse
import glob
import json
import os
import sqlite3
import sys
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'geo.db')


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_trash_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clients_trash (
            id         TEXT PRIMARY KEY,
            owner_id   TEXT DEFAULT 'local',
            data       TEXT NOT NULL,
            deleted_at TEXT NOT NULL
        )
    ''')
    conn.commit()


def list_active(conn):
    rows = conn.execute('SELECT id, data, updated_at FROM clients ORDER BY updated_at DESC').fetchall()
    out = []
    for cid, data, updated_at in rows:
        try:
            c = json.loads(data)
            out.append({'id': cid, 'brand_name': c.get('brand_name', cid), 'updated_at': updated_at})
        except Exception:
            out.append({'id': cid, 'brand_name': cid, 'updated_at': updated_at})
    return out


def list_trash(conn):
    init_trash_table(conn)
    rows = conn.execute(
        'SELECT id, data, deleted_at FROM clients_trash ORDER BY deleted_at DESC'
    ).fetchall()
    out = []
    for cid, data, deleted_at in rows:
        try:
            c = json.loads(data)
            kw = len(c.get('keywords') or [])
            arts = len(c.get('articles') or [])
            out.append({
                'id': cid,
                'brand_name': c.get('brand_name', cid),
                'deleted_at': deleted_at,
                'keywords': kw,
                'articles': arts,
                'data': c,
            })
        except Exception:
            pass
    return out


def find_backups():
    base = os.path.dirname(os.path.abspath(__file__))
    files = sorted(glob.glob(os.path.join(base, 'geo-backup-*.json')), reverse=True)
    out = []
    for path in files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            clients = data.get('clients') or {}
            out.append({'path': path, 'count': len(clients), 'clients': clients})
        except Exception as e:
            out.append({'path': path, 'error': str(e)})
    return out


def restore_clients(conn, clients: dict):
    now = datetime.now().isoformat(timespec='seconds')
    for cid, cdata in clients.items():
        conn.execute(
            'INSERT OR REPLACE INTO clients(id, owner_id, data, updated_at) VALUES(?,?,?,?)',
            (cid, 'local', json.dumps(cdata, ensure_ascii=False), now)
        )
    conn.commit()


def restore_from_trash(conn, ids=None):
    trash = list_trash(conn)
    if not trash:
        return []
    target = trash if not ids else [t for t in trash if t['id'] in ids]
    now = datetime.now().isoformat(timespec='seconds')
    restored = []
    for item in target:
        cid = item['id']
        conn.execute(
            'INSERT OR REPLACE INTO clients(id, owner_id, data, updated_at) VALUES(?,?,?,?)',
            (cid, 'local', json.dumps(item['data'], ensure_ascii=False), now)
        )
        conn.execute('DELETE FROM clients_trash WHERE id=?', (cid,))
        restored.append(cid)
    conn.commit()
    return restored


def scan_wal_hints():
    """在 WAL 文件中搜索可能残留的客户 JSON 片段（仅作提示）"""
    base = os.path.dirname(os.path.abspath(__file__))
    hints = []
    for name in ('geo.db-wal', 'geo.db-journal'):
        path = os.path.join(base, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, 'rb') as f:
                raw = f.read()
            text = raw.decode('utf-8', errors='ignore')
            for marker in ('brand_name', 'shiguang', 'c_liyan'):
                if marker in text:
                    hints.append(f'{name} 中检测到 "{marker}" 字样，可尝试用 sqlite3 工具做深度恢复')
                    break
        except Exception:
            pass
    return hints


def main():
    parser = argparse.ArgumentParser(description='GEO 工作台客户数据恢复')
    parser.add_argument('--restore-all', action='store_true', help='从回收站恢复全部 + 合并最新备份')
    parser.add_argument('--from-backup', metavar='FILE', help='从指定备份 JSON 恢复')
    parser.add_argument('--restore-trash', nargs='*', metavar='ID', help='从回收站恢复指定 id（省略则全部）')
    args = parser.parse_args()

    if not os.path.isfile(DB_PATH):
        print(f'❌ 未找到数据库：{DB_PATH}')
        print('请在本机 geo-workbench 项目目录下运行此脚本。')
        backups = find_backups()
        if backups:
            print('\n发现备份文件（可直接导入）：')
            for b in backups:
                if 'count' in b:
                    print(f"  • {os.path.basename(b['path'])} — {b['count']} 个客户")
            if args.from_backup:
                path = args.from_backup
                if not os.path.isabs(path):
                    path = os.path.join(os.path.dirname(DB_PATH), path)
                with open(path, 'r', encoding='utf-8') as f:
                    clients = json.load(f).get('clients') or {}
                print(f'\n备份含 {len(clients)} 个客户。请先启动 server.py 后，在界面点「导入备份」选择该文件。')
        sys.exit(1)

    conn = get_conn()
    active = list_active(conn)
    trash = list_trash(conn)
    backups = find_backups()
    wal_hints = scan_wal_hints()

    print('═══════════════════════════════════════')
    print(' GEO 工作台 · 数据恢复扫描')
    print('═══════════════════════════════════════')
    print(f'\n📂 数据库：{DB_PATH}')
    print(f'✅ 当前客户：{len(active)} 个')
    for c in active:
        print(f"   · {c['brand_name']} ({c['id']})")

    print(f'\n🗑️  回收站：{len(trash)} 个')
    for t in trash:
        print(f"   · {t['brand_name']} — 删除于 {t['deleted_at']} · {t['keywords']}词 {t['articles']}篇")

    print(f'\n💾 备份文件：{len(backups)} 个')
    for b in backups:
        if 'count' in b:
            print(f"   · {os.path.basename(b['path'])} — {b['count']} 个客户")
        else:
            print(f"   · {os.path.basename(b['path'])} — 读取失败")

    if wal_hints:
        print('\n🔍 WAL 线索：')
        for h in wal_hints:
            print(f'   · {h}')

    if args.from_backup:
        path = args.from_backup
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(DB_PATH), path)
        with open(path, 'r', encoding='utf-8') as f:
            clients = json.load(f).get('clients') or {}
        restore_clients(conn, clients)
        print(f'\n✅ 已从备份恢复 {len(clients)} 个客户。请刷新浏览器。')
        return

    if args.restore_trash is not None:
        ids = args.restore_trash if args.restore_trash else None
        restored = restore_from_trash(conn, ids)
        print(f'\n✅ 已从回收站恢复：{", ".join(restored) or "（无）"}')
        print('请刷新浏览器页面。')
        return

    if args.restore_all:
        restored = restore_from_trash(conn)
        if backups and 'clients' in backups[0]:
            restore_clients(conn, backups[0]['clients'])
            print(f'\n✅ 回收站恢复 {len(restored)} 个 + 合并最新备份 {backups[0]["count"]} 个')
        else:
            print(f'\n✅ 回收站恢复 {len(restored)} 个')
        print('请刷新浏览器页面。')
        return

    if trash:
        print('\n👉 恢复回收站全部：python3 recover.py --restore-trash')
    if backups:
        print('👉 从最新备份恢复：python3 recover.py --from-backup ' + os.path.basename(backups[0]['path']))
    if not trash and not backups:
        print('\n⚠️  未发现回收站数据或备份文件。')
        print('若刚删除，请确认是否曾点过顶栏「导出备份」。')
        print('也可尝试：关闭 server.py 后，用 Time Machine / 文件历史版本恢复 geo.db。')


if __name__ == '__main__':
    main()
