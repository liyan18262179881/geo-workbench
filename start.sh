#!/usr/bin/env bash
# GEO 工作台 · 一键启动（先起服务，再开浏览器）
set -euo pipefail
cd "$(dirname "$0")"
PORT=8765
URL="http://localhost:${PORT}"

echo "══════════════════════════════════════"
echo "  GEO 工作台 启动中…"
echo "══════════════════════════════════════"

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ 未找到 python3，请先安装 Python 3"
  read -p "按回车关闭…"
  exit 1
fi

if ! python3 -c "import anthropic, openai" 2>/dev/null; then
  echo "📦 正在安装依赖 anthropic openai …"
  pip3 install anthropic openai || python3 -m pip install anthropic openai
fi

# 若端口已被占用，尝试结束旧进程
if lsof -ti:"$PORT" >/dev/null 2>&1; then
  echo "⚠️  端口 ${PORT} 已被占用，正在结束旧进程…"
  lsof -ti:"$PORT" | xargs kill -9 2>/dev/null || true
  sleep 1
fi

echo "🚀 启动服务 ${URL}"
python3 server.py &
PID=$!

# 等待服务就绪（最多 15 秒）
READY=0
for i in $(seq 1 30); do
  if curl -sf "${URL}/api/status" >/dev/null 2>&1; then
    READY=1
    break
  fi
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "❌ 服务启动失败，请查看上方错误信息"
    read -p "按回车关闭…"
    exit 1
  fi
  sleep 0.5
done

if [[ "$READY" -ne 1 ]]; then
  echo "❌ 服务未能在 15 秒内启动"
  kill "$PID" 2>/dev/null || true
  read -p "按回车关闭…"
  exit 1
fi

echo "✅ 服务已就绪"
open "$URL" 2>/dev/null || xdg-open "$URL" 2>/dev/null || echo "请手动打开：$URL"

echo ""
echo "  浏览器：$URL"
echo "  按 Ctrl+C 停止服务"
echo "══════════════════════════════════════"

wait "$PID"
