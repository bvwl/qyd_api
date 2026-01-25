#!/bin/bash

# Redis 队列处理启动脚本

cd backend

echo "启动 Redis 队列处理..."
python start_queue_worker.py
