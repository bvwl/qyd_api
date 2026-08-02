"""
修复 XUI 入站账号多对多关系表兼容问题。

只做两件事：
1. 创建 Tortoise 运行时实际查询的 xuiinbound_accounts 表；
2. 如果旧表 xui_inbound_account 存在，将旧关系复制到新表。
"""
import asyncio
import os
import sys
from pathlib import Path

try:
    import aiomysql
except ImportError:
    print("缺少 aiomysql 库，请在后端环境中执行")
    sys.exit(1)


def load_env() -> None:
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


async def table_exists(cursor, table_name: str) -> bool:
    await cursor.execute("SHOW TABLES LIKE %s", (table_name,))
    return await cursor.fetchone() is not None


async def main() -> int:
    load_env()

    conn = await aiomysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "qyd"),
        password=os.getenv("DB_PASSWORD", ""),
        db=os.getenv("DB_NAME", "qyd"),
        charset="utf8mb4",
        autocommit=True,
    )

    try:
        cursor = await conn.cursor()

        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `xuiinbound_accounts` (
              `xuiinbound_id` CHAR(36) NOT NULL COMMENT '入站 ID',
              `serveraccount_id` CHAR(36) NOT NULL COMMENT '账号 ID',
              PRIMARY KEY (`xuiinbound_id`, `serveraccount_id`),
              CONSTRAINT `fk_xuiinbound_accounts_inbound`
                FOREIGN KEY (`xuiinbound_id`) REFERENCES `xui_inbound` (`id`) ON DELETE CASCADE,
              CONSTRAINT `fk_xuiinbound_accounts_account`
                FOREIGN KEY (`serveraccount_id`) REFERENCES `proxy_account` (`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='XUI 入站和账号关系表（Tortoise默认命名兼容）'
            """
        )
        print("已确保 xuiinbound_accounts 表存在")

        if await table_exists(cursor, "xui_inbound_account"):
            await cursor.execute(
                """
                INSERT IGNORE INTO `xuiinbound_accounts` (`xuiinbound_id`, `serveraccount_id`)
                SELECT `xui_inbound_id`, `serveraccount_id`
                FROM `xui_inbound_account`
                """
            )
            print(f"已从 xui_inbound_account 复制 {cursor.rowcount} 条关系")
        else:
            print("旧表 xui_inbound_account 不存在，跳过数据复制")

        await cursor.close()
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
