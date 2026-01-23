#!/bin/bash

echo "正在重启后端服务器..."

# 查找并杀死旧进程
OLD_PID=$(ps aux | grep "python.*start.py" | grep -v grep | awk '{print $2}')

if [ -n "$OLD_PID" ]; then
  echo "找到旧进程 PID: $OLD_PID"
  kill $OLD_PID
  sleep 2
  
  # 检查是否还在运行
  if ps -p $OLD_PID > /dev/null 2>&1; then
    echo "强制杀死进程..."
    kill -9 $OLD_PID
    sleep 1
  fi
  
  echo "✅ 旧进程已停止"
else
  echo "没有找到运行中的后端进程"
fi

# 启动新进程
echo "正在启动新进程..."
cd backend
nohup conda run -n table_api python start.py > ../logs/app.log 2>&1 &
NEW_PID=$!

sleep 3

# 检查是否启动成功
if ps -p $NEW_PID > /dev/null 2>&1; then
  echo "✅ 后端服务器已启动 (PID: $NEW_PID)"
  echo "查看日志: tail -f logs/app.log"
else
  echo "❌ 启动失败，请检查日志"
  tail -20 logs/app.log
fi
