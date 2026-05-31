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
        if self.path != '/api/generate':
            self._json(404, {'error': 'Not found'})
            return

        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        prompt   = body.get('prompt', '')
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

        try:
            if provider == 'anthropic':
                text = call_anthropic(api_key, model, prompt)
            else:
                text = call_openai_compat(cfg['base_url'], api_key, model, prompt)
            self._json(200, {'content': text})
        except Exception as e:
            self._json(500, {'error': str(e)})

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
