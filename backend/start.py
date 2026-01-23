import os
import logging
from pathlib import Path

import uvicorn


def load_env_from_file(env_path: Path | None = None) -> None:
    """
    加载 .env 文件中的环境变量
    """
    if env_path is None:
        env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        # 若环境中已存在同名变量，则保持现有值
        os.environ.setdefault(key, value)


def setup_logging() -> None:
    """
    配置日志系统
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_server() -> None:
    """
    使用 uvicorn 启动 FastAPI 后端服务
    """
    load_env_from_file()
    setup_logging()

    # 读取配置
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "6080"))
    # 修复：正确判断 DEBUG 模式
    reload = os.getenv("APP_DEBUG", "0").lower() in ("1", "true", "yes")
    workers = int(os.getenv("APP_WORKERS", "1"))
    
    # uvicorn 配置
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    logging.info(f"启动服务: {host}:{port}")
    logging.info(f"调试模式: {reload}")
    logging.info(f"工作进程: {workers}")
    logging.info(f"提示: 如需队列处理，请手动运行: python start_queue_worker.py")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level=log_level,
        http="httptools",
        limit_concurrency=int(os.getenv("APP_LIMIT_CONCURRENCY", "10000")),
        backlog=int(os.getenv("APP_BACKLOG", "4096")),
        timeout_keep_alive=int(os.getenv("APP_TIMEOUT_KEEP_ALIVE", "5")),
    )


if __name__ == "__main__":
    run_server()
