"""
GEO 工作台本地服务
启动方式：python3 server.py
访问地址：http://localhost:8765
"""
import os, json
from http.server import HTTPServer, SimpleHTTPRequestHandler

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
            self._json(200, {'ok': True, 'providers': list(PROVIDERS.keys())})
            return
        if self.path == '/api/providers':
            self._json(200, PROVIDERS)
            return
        super().do_GET()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
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
    print(f'\n✅ GEO 工作台已启动 → http://localhost:{port}\n')
    print('支持平台：' + ' | '.join(p['name'] for p in PROVIDERS.values()))
    print()
    HTTPServer(('', port), GEOHandler).serve_forever()
