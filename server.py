"""
GEO 工作台本地服务
启动方式：python3 server.py
访问地址：http://localhost:8765
"""
import os, json, sqlite3
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ── SQLite 数据库（数据落盘，不再只存浏览器）──
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'geo.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_conn()
    # 每个客户一行（关键词/文章/检测都在该客户的 data 里，天然按人隔离）
    # owner_id 预留：现在固定 'local'，将来做多账号时直接用它隔离数据
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id         TEXT PRIMARY KEY,
            owner_id   TEXT DEFAULT 'local',
            data       TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 支持的平台配置
PROVIDERS = {
    'deepseek': {
        'name': 'DeepSeek',
        'base_url': 'https://api.deepseek.com/v1',
        'models': ['deepseek-chat', 'deepseek-reasoner'],
        'default_model': 'deepseek-chat',
    },
    'doubao': {
        'name': '豆包 (ByteDance)',
        'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
        'models': ['doubao-pro-32k', 'doubao-pro-4k', 'doubao-lite-32k', 'doubao-lite-4k'],
        'default_model': 'doubao-pro-32k',
    },
    'moonshot': {
        'name': 'Kimi (Moonshot)',
        'base_url': 'https://api.moonshot.cn/v1',
        'models': ['moonshot-v1-32k', 'moonshot-v1-8k', 'moonshot-v1-128k'],
        'default_model': 'moonshot-v1-32k',
    },
    'qwen': {
        'name': '通义千问 (Qwen)',
        'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'models': ['qwen-max', 'qwen-plus', 'qwen-turbo', 'qwen-long'],
        'default_model': 'qwen-plus',
    },
    'anthropic': {
        'name': 'Claude (Anthropic)',
        'base_url': None,
        'models': ['claude-sonnet-4-5', 'claude-opus-4-5', 'claude-haiku-4-5'],
        'default_model': 'claude-sonnet-4-5',
    },
    'openai': {
        'name': 'OpenAI (GPT)',
        'base_url': 'https://api.openai.com/v1',
        'models': ['gpt-4o', 'gpt-4o-mini'],
        'default_model': 'gpt-4o',
    },
}


HUMANIZE_PROMPT = """你是一位中文文字编辑，专门把AI生成的文章改写成更自然的人写风格。

请按以下规则处理文章，不要解释，直接输出改写后的正文：

【必须删掉或替换的AI套话】
- 综上所述 → 直接删掉
- 值得注意的是 → 直接删掉
- 不难发现 → 直接删掉
- 由此可见 → 直接删掉
- 与此同时 → 同时 / 另外
- 不仅如此 → 而且 / 还有
- 更重要的是 → 关键是 / 其实
- 赋能 → 帮助 / 支持
- 助力 → 帮 / 推动
- 彰显 → 体现 / 说明
- 凸显 → 突出 / 显示
- 底层逻辑 → 根本原因 / 本质
- 闭环 → 完整流程 / 形成循环
- 全方位 → 各方面 / 各个环节
- 多维度 → 从多个角度 / 几个方面

【句式改写规则】
1. 打破"首先…其次…最后"的三段式，改成自然过渡
2. 把过于整齐的并列句打散，长短句交替
3. 合并过短的句子，拆开过长的句子
4. 同一个词出现3次以上就换同义词
5. 适当加一两句口语表达或反问句，但不要太多
6. 每段长度不要完全一致，有的2句，有的4-5句

【不能改的内容】
- 品牌名、地名、专业术语保持不变
- 文章结构（各小节标题方向）保持不变
- 核心观点和信息不能删除或歪曲
- 字数保持在原文的90%-110%之间

直接输出改写后的纯文本正文，不加任何说明。"""


def call_anthropic(api_key, model, prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return msg.content[0].text


def call_openai_compat(base_url, api_key, model, prompt):
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        max_tokens=2048,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return resp.choices[0].message.content


def call_llm(provider, base_url, api_key, model, prompt):
    if provider == 'anthropic':
        return call_anthropic(api_key, model, prompt)
    else:
        return call_openai_compat(base_url, api_key, model, prompt)


class GEOHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def end_headers(self):
        # 禁止浏览器缓存静态文件，改动后刷新即可生效
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_GET(self):
        if self.path == '/api/status':
            self._json(200, {'ok': True, 'providers': list(PROVIDERS.keys()), 'db': True})
            return
        if self.path == '/api/providers':
            self._json(200, PROVIDERS)
            return
        # 读取全部客户数据
        if self.path == '/api/db':
            self._json(200, {'clients': self._read_all_clients()})
            return
        # 导出备份（浏览器直接下载 json 文件）
        if self.path == '/api/export':
            payload = json.dumps({'clients': self._read_all_clients()}, ensure_ascii=False, indent=2).encode('utf-8')
            self.send_response(200)
            self._cors()
            fname = 'geo-backup-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.json'
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Disposition', f'attachment; filename="{fname}"')
            self.send_header('Content-Length', len(payload))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()

    def _read_all_clients(self):
        conn = get_conn()
        rows = conn.execute('SELECT id, data FROM clients').fetchall()
        conn.close()
        clients = {}
        for cid, data in rows:
            try:
                clients[cid] = json.loads(data)
            except Exception:
                pass
        return clients

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))

        # 保存全部客户数据（每个客户一行，整体同步）
        if self.path == '/api/db':
            incoming = body.get('clients')
            if not isinstance(incoming, dict) or not incoming:
                # 防呆：空数据不写，避免误清库
                self._json(400, {'error': '客户数据为空，已拒绝写入'})
                return
            try:
                conn = get_conn()
                now = datetime.now().isoformat(timespec='seconds')
                for cid, cdata in incoming.items():
                    conn.execute(
                        'INSERT OR REPLACE INTO clients(id, owner_id, data, updated_at) VALUES(?,?,?,?)',
                        (cid, 'local', json.dumps(cdata, ensure_ascii=False), now)
                    )
                # 删除本次未出现的客户（反映前端的删除操作）
                ids = list(incoming.keys())
                ph = ','.join('?' * len(ids))
                conn.execute(f'DELETE FROM clients WHERE id NOT IN ({ph})', ids)
                conn.commit()
                conn.close()
                self._json(200, {'ok': True, 'count': len(incoming)})
            except Exception as e:
                self._json(500, {'error': str(e)})
            return

        # 图片生成接口独立处理
        if self.path == '/api/generate-image':
            img_api_key = body.get('img_api_key', '').strip()
            prompt = body.get('prompt', '')
            if not prompt:
                self._json(400, {'error': '缺少图片描述'})
                return

            # 没有 API Key → 用 Pollinations.ai（完全免费，无需配置）
            if not img_api_key:
                import urllib.parse, random
                encoded = urllib.parse.quote(prompt)
                seed = random.randint(1000, 9999)
                url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=768&model=flux&nologo=true&seed={seed}"
                self._json(200, {'url': url, 'source': 'pollinations'})
                return

            # 有 API Key → 用 SiliconFlow（免费模型 SDXL）
            try:
                import urllib.request as urlreq
                # 尝试顺序：SDXL（免费）→ Kolors（免费）→ Pollinations 兜底
                models_to_try = [
                    'stabilityai/stable-diffusion-xl-base-1.0',
                    'Kwai-Kolors/Kolors',
                ]
                last_error = ''
                for model_name in models_to_try:
                    try:
                        req_data = json.dumps({
                            'model': model_name,
                            'prompt': prompt,
                            'negative_prompt': 'text, watermark, logo, blurry, distorted, ugly',
                            'image_size': '1024x768',
                            'batch_size': 1,
                            'num_inference_steps': 25,
                            'guidance_scale': 7.5
                        }).encode('utf-8')
                        req = urlreq.Request(
                            'https://api.siliconflow.cn/v1/images/generations',
                            data=req_data,
                            headers={
                                'Authorization': f'Bearer {img_api_key}',
                                'Content-Type': 'application/json'
                            }
                        )
                        with urlreq.urlopen(req, timeout=60) as resp:
                            result = json.loads(resp.read())
                        if 'images' in result and result['images']:
                            self._json(200, {'url': result['images'][0]['url'], 'source': 'siliconflow', 'model': model_name})
                            return
                        last_error = str(result)
                    except Exception as e:
                        last_error = str(e)
                        continue
                # 所有模型都失败 → Pollinations 兜底
                import urllib.parse, random
                encoded = urllib.parse.quote(prompt)
                seed = random.randint(1000, 9999)
                url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=768&model=flux&nologo=true&seed={seed}"
                self._json(200, {'url': url, 'source': 'pollinations_fallback', 'note': last_error})
            except Exception as e:
                self._json(500, {'error': str(e)})
            return

        api_key  = body.get('api_key', '').strip()
        provider = body.get('provider', 'deepseek')
        model    = body.get('model', '')

        if not api_key:
            self._json(400, {'error': '请先在设置里填写 API Key'})
            return

        cfg = PROVIDERS.get(provider)
        if not cfg:
            self._json(400, {'error': f'不支持的平台：{provider}'})
            return
        if not model:
            model = cfg['default_model']

        # 单独去AI味接口
        if self.path == '/api/humanize':
            text = body.get('text', '')
            if not text:
                self._json(400, {'error': '请传入要处理的文章内容'})
                return
            try:
                humanize_input = f"{HUMANIZE_PROMPT}\n\n【需要改写的文章】\n{text}"
                result = call_llm(provider, cfg['base_url'], api_key, model, humanize_input)
                self._json(200, {'content': result})
            except Exception as e:
                self._json(500, {'error': str(e)})
            return

        # 生成文章接口
        if self.path == '/api/generate':
            prompt = body.get('prompt', '')
            humanize = body.get('humanize', True)  # 默认自动去AI味
            try:
                # 第一步：生成文章
                raw = call_llm(provider, cfg['base_url'], api_key, model, prompt)
                if not humanize:
                    self._json(200, {'content': raw})
                    return
                # 第二步：自动去AI味
                humanize_input = f"{HUMANIZE_PROMPT}\n\n【需要改写的文章】\n{raw}"
                result = call_llm(provider, cfg['base_url'], api_key, model, humanize_input)
                self._json(200, {'content': result, 'raw': raw})
            except Exception as e:
                self._json(500, {'error': str(e)})
            return

        self._json(404, {'error': 'Not found'})

    def _json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    port = 8765
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_db()
    print(f'\n✅ GEO 工作台已启动 → http://localhost:{port}\n')
    print(f'🗄️  数据库：{DB_PATH}')
    print('支持平台：' + ' | '.join(p['name'] for p in PROVIDERS.values()))
    print()
    HTTPServer(('', port), GEOHandler).serve_forever()
