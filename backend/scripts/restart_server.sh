#!/usr/bin/env bash
set -euo pipefail

# 重启后端服务脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${BACKEND_DIR}"

echo "正在检查端口 6080..."

# 查找占用端口的进程
PID=$(lsof -ti:6080 || echo "")

if [ -n "$PID" ]; then
    echo "发现进程 $PID 正在使用端口 6080"
    echo "正在停止进程..."
    kill -9 $PID
    sleep 1
    echo "✅ 进程已停止"
else
    echo "端口 6080 未被占用"
fi

echo ""
echo "正在启动后端服务..."
python start.py &

sleep 3

# 检查服务是否启动成功
if curl -s http://127.0.0.1:6080/docs > /dev/null 2>&1; then
    echo "✅ 后端服务启动成功！"
    echo "📝 API文档: http://127.0.0.1:6080/docs"
else
    echo "⚠️  服务可能还在启动中，请稍等片刻"
    echo "📝 API文档: http://127.0.0.1:6080/docs"
fi
