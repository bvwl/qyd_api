import os
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


def run_server() -> None:
    """
    使用 uvicorn 启动 FastAPI 后端服务
    """
    load_env_from_file()

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "6080"))
    reload = bool(os.getenv("APP_DEBUG"))

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=1,
        http="httptools",
        limit_concurrency=10000,
        backlog=4096,
        timeout_keep_alive=5,
    )


if __name__ == "__main__":
    run_server()
