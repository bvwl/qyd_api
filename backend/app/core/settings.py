import os
import random


# ==========================================
# 主库配置（写操作）
# ==========================================
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
# 读写分离配置
# ==========================================
DB_READ_WRITE_SPLIT = os.getenv("DB_READ_WRITE_SPLIT", "0") == "1"

# 从库1配置
DB_SLAVE1_HOST = os.getenv("DB_SLAVE1_HOST", DB_HOST)
DB_SLAVE1_PORT = int(os.getenv("DB_SLAVE1_PORT", DB_PORT))
DB_SLAVE1_USER = os.getenv("DB_SLAVE1_USER", DB_USER)
DB_SLAVE1_PASSWORD = os.getenv("DB_SLAVE1_PASSWORD", DB_PASSWORD)
DB_SLAVE1_NAME = os.getenv("DB_SLAVE1_NAME", DB_NAME)
DB_SLAVE1_MINSIZE = int(os.getenv("DB_SLAVE1_MINSIZE", DB_MINSIZE))
DB_SLAVE1_MAXSIZE = int(os.getenv("DB_SLAVE1_MAXSIZE", DB_MAXSIZE))

# 从库2配置
DB_SLAVE2_HOST = os.getenv("DB_SLAVE2_HOST", DB_HOST)
DB_SLAVE2_PORT = int(os.getenv("DB_SLAVE2_PORT", DB_PORT))
DB_SLAVE2_USER = os.getenv("DB_SLAVE2_USER", DB_USER)
DB_SLAVE2_PASSWORD = os.getenv("DB_SLAVE2_PASSWORD", DB_PASSWORD)
DB_SLAVE2_NAME = os.getenv("DB_SLAVE2_NAME", DB_NAME)
DB_SLAVE2_MINSIZE = int(os.getenv("DB_SLAVE2_MINSIZE", DB_MINSIZE))
DB_SLAVE2_MAXSIZE = int(os.getenv("DB_SLAVE2_MAXSIZE", DB_MAXSIZE))


# ==========================================
# JWT 配置
# ==========================================
JWT = {
    "secret_key": os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-min-32-chars"),
    "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
    "expire_time": int(os.getenv("JWT_EXPIRE_TIME", "86400")),  # 默认24小时
}

# ==========================================
# Redis 配置
# ==========================================
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "1") == "1"
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
REDIS_TIMEOUT = int(os.getenv("REDIS_TIMEOUT", "5"))
REDIS_KEY_PREFIX = os.getenv("REDIS_KEY_PREFIX", "qyd:")

# Redis 队列配置
REDIS_QUEUE_BATCH_SIZE = int(os.getenv("REDIS_QUEUE_BATCH_SIZE", "200"))
REDIS_QUEUE_NUM_WORKERS = int(os.getenv("REDIS_QUEUE_NUM_WORKERS", "4"))
REDIS_QUEUE_CACHE_EXPIRE = int(os.getenv("REDIS_QUEUE_CACHE_EXPIRE", "3600"))

# Redis URL 构建
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# ==========================================
# Tortoise ORM 配置
# ==========================================
def get_tortoise_config():
    """获取Tortoise ORM配置，支持读写分离"""
    
    # 基础连接配置
    connections = {
        "default": {  # 主库（写操作）
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
    }
    
    # 如果启用读写分离，添加从库连接
    if DB_READ_WRITE_SPLIT:
        connections["slave1"] = {  # 从库1（读操作）
            "engine": DB_ENGINE,
            "credentials": {
                "host": DB_SLAVE1_HOST,
                "port": DB_SLAVE1_PORT,
                "user": DB_SLAVE1_USER,
                "password": DB_SLAVE1_PASSWORD,
                "database": DB_SLAVE1_NAME,
                "minsize": DB_SLAVE1_MINSIZE,
                "maxsize": DB_SLAVE1_MAXSIZE,
                "charset": "utf8mb4",
                "echo": DB_ECHO,
                "pool_recycle": DB_POOL_RECYCLE,
                "connect_timeout": DB_CONNECT_TIMEOUT,
            },
        }
        connections["slave2"] = {  # 从库2（读操作）
            "engine": DB_ENGINE,
            "credentials": {
                "host": DB_SLAVE2_HOST,
                "port": DB_SLAVE2_PORT,
                "user": DB_SLAVE2_USER,
                "password": DB_SLAVE2_PASSWORD,
                "database": DB_SLAVE2_NAME,
                "minsize": DB_SLAVE2_MINSIZE,
                "maxsize": DB_SLAVE2_MAXSIZE,
                "charset": "utf8mb4",
                "echo": DB_ECHO,
                "pool_recycle": DB_POOL_RECYCLE,
                "connect_timeout": DB_CONNECT_TIMEOUT,
            },
        }
    
    return {
        "connections": connections,
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


TORTOISE_ORM = get_tortoise_config()


# ==========================================
# 读写分离工具函数
# ==========================================
def get_read_db():
    """获取读数据库连接名称（负载均衡）"""
    if not DB_READ_WRITE_SPLIT:
        return "default"
    
    # 随机选择一个从库，实现简单的负载均衡
    return random.choice(["slave1", "slave2"])


def get_write_db():
    """获取写数据库连接名称"""
    return "default"
