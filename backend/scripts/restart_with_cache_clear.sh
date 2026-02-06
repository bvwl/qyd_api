#!/usr/bin/env bash
set -euo pipefail

# ==========================================
# 清除缓存并重启后端服务脚本
# ==========================================
# 功能：
# 1. 清除 Python 缓存文件 (__pycache__, *.pyc)
# 2. 清除 Redis 缓存（可选）
# 3. 重启后端服务
# ==========================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=========================================="
echo "  清除缓存并重启后端服务"
echo "=========================================="
echo ""

# ==========================================
# 1. 清除 Python 缓存
# ==========================================
echo "[1/4] 清除 Python 缓存..."
cd "${BACKEND_DIR}"

# 删除所有 __pycache__ 目录
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "  ✓ 已删除 __pycache__ 目录"

# 删除所有 .pyc 文件
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "  ✓ 已删除 .pyc 文件"

# 删除所有 .pyo 文件
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "  ✓ 已删除 .pyo 文件"

echo ""

# ==========================================
# 2. 清除 Redis 缓存（可选）
# ==========================================
echo "[2/4] 清除 Redis 缓存..."

# 读取 Redis 配置
if [ -f "${BACKEND_DIR}/.env" ]; then
    source "${BACKEND_DIR}/.env"
fi

REDIS_HOST=${REDIS_HOST:-127.0.0.1}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_PASSWORD=${REDIS_PASSWORD:-}
REDIS_DB=${REDIS_DB:-0}

# 询问是否清除 Redis 缓存
read -p "是否清除 Redis 缓存？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -n "$REDIS_PASSWORD" ]; then
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" -n "$REDIS_DB" FLUSHDB 2>/dev/null && \
            echo "  ✓ Redis 缓存已清除" || \
            echo "  ⚠️  Redis 缓存清除失败（可能 Redis 未运行或配置错误）"
    else
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" FLUSHDB 2>/dev/null && \
            echo "  ✓ Redis 缓存已清除" || \
            echo "  ⚠️  Redis 缓存清除失败（可能 Redis 未运行或配置错误）"
    fi
else
    echo "  跳过 Redis 缓存清除"
fi

echo ""

# ==========================================
# 3. 停止旧服务
# ==========================================
echo "[3/4] 停止旧服务..."

# 查找占用端口的进程
PORT=${PORT:-6080}
PID=$(lsof -ti:$PORT 2>/dev/null || echo "")

if [ -n "$PID" ]; then
    echo "  发现进程 $PID 正在使用端口 $PORT"
    echo "  正在停止进程..."
    kill -9 $PID
    sleep 1
    echo "  ✓ 进程已停止"
else
    echo "  端口 $PORT 未被占用"
fi

echo ""

# ==========================================
# 4. 启动新服务
# ==========================================
echo "[4/4] 启动后端服务..."
cd "${BACKEND_DIR}"

# 后台启动服务
nohup python start.py > logs/app.log 2>&1 &
NEW_PID=$!

echo "  服务已启动 (PID: $NEW_PID)"
echo "  等待服务就绪..."
sleep 5

# 检查服务是否启动成功
if curl -s http://127.0.0.1:$PORT/docs > /dev/null 2>&1; then
    echo ""
    echo "=========================================="
    echo "✅ 后端服务启动成功！"
    echo "=========================================="
    echo ""
    echo "服务信息："
    echo "  PID: $NEW_PID"
    echo "  端口: $PORT"
    echo "  API 文档: http://127.0.0.1:$PORT/docs"
    echo ""
    echo "查看日志："
    echo "  tail -f logs/app.log"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "⚠️  服务可能还在启动中"
    echo "=========================================="
    echo ""
    echo "请稍等片刻后访问："
    echo "  http://127.0.0.1:$PORT/docs"
    echo ""
    echo "查看日志："
    echo "  tail -f logs/app.log"
    echo ""
fi
