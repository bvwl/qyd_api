import os


DB_ENGINE = os.getenv("DB_ENGINE", "tortoise.backends.mysql")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "qyd")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "qyd")
DB_MINSIZE = int(os.getenv("DB_MINSIZE", "5"))
DB_MAXSIZE = int(os.getenv("DB_MAXSIZE", "20"))
DB_ECHO = os.getenv("DB_ECHO", "0") == "1"
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))


# ==========================================
# JWT 配置
# ==========================================
JWT = {
    "secret_key": os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-min-32-chars"),
    "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
    "expire_time": int(os.getenv("JWT_EXPIRE_TIME", "86400")),  # 默认24小时
}

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": DB_ENGINE,
            "credentials": {
                "host": DB_HOST,
                "port": DB_PORT,
                "user": DB_USER,
                "password": DB_PASSWORD,
                "database": DB_NAME,
                "minsize": DB_MINSIZE,
                "maxsize": DB_MAXSIZE,
                "charset": "utf8mb4",
                "echo": DB_ECHO,
                "pool_recycle": DB_POOL_RECYCLE,
                "connect_timeout": DB_CONNECT_TIMEOUT,
            },
        },
    },
    "apps": {
        "models": {
            "models": [
                "app.models.mail",
                "app.models.server",
                "app.models.user",
                "app.models.project",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}
