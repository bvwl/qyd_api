# 多阶段构建 - 后端基础镜像
FROM python:3.11-slim as backend-base

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设置工作目录和Python环境变量
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 配置国内镜像源（加速构建）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        python3-dev \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 配置 pip 国内镜像源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set install.trusted-host mirrors.aliyun.com

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 后端 API 服务
FROM backend-base as backend-api

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p logs/api logs/app logs/database logs/scheduler

# 暴露端口
EXPOSE 6080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:6080/docs', timeout=5)" || exit 1

# 启动命令
CMD ["python", "start.py"]

# 队列 Worker 服务
FROM backend-base as queue-worker

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p logs/api logs/app logs/database logs/scheduler

# 启动命令
CMD ["python", "start_queue_worker.py"]

# 日志压缩服务（独立运行）
FROM backend-base as log-compressor

# 复制完整应用代码（避免导入错误）
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 启动命令
CMD ["python", "start_log_compressor.py"]
