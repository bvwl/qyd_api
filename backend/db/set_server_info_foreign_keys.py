"""将代理节点关联外键改为 SET NULL，避免删除关联业务数据。"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

try:
    import aiomysql
except ImportError:
    print("缺少 aiomysql 库，请在后端环境中执行")
    sys.exit(1)


TARGETS = (
    ("project_account", "server_id", "server_info", "fk_project_account_server_set_null"),
    ("email_info", "server_id", "server_info", "fk_email_info_server_set_null"),
)


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


async def get_foreign_key(cursor, table: str, column: str, referenced_table: str):
    await cursor.execute(
        """
        SELECT kcu.CONSTRAINT_NAME, rc.DELETE_RULE
        FROM information_schema.KEY_COLUMN_USAGE AS kcu
        JOIN information_schema.REFERENTIAL_CONSTRAINTS AS rc
          ON rc.CONSTRAINT_SCHEMA = kcu.CONSTRAINT_SCHEMA
         AND rc.TABLE_NAME = kcu.TABLE_NAME
         AND rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
        WHERE kcu.CONSTRAINT_SCHEMA = DATABASE()
          AND kcu.TABLE_NAME = %s
          AND kcu.COLUMN_NAME = %s
          AND kcu.REFERENCED_TABLE_NAME = %s
        """,
        (table, column, referenced_table),
    )
    return await cursor.fetchone()


async def column_is_nullable(cursor, table: str, column: str) -> bool:
    await cursor.execute(
        """
        SELECT IS_NULLABLE
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (table, column),
    )
    row = await cursor.fetchone()
    return bool(row and row[0] == "YES")


async def data_snapshot(cursor, table: str, column: str) -> tuple[int, int, int, int]:
    """获取只读数据快照，用于确认迁移前后现有数据完全未变。"""
    await cursor.execute(
        f"""
        SELECT
          COUNT(*) AS total_rows,
          COUNT(`{column}`) AS linked_rows,
          COALESCE(SUM(CRC32(CONCAT(`id`, ':', COALESCE(`{column}`, '')))), 0) AS checksum_sum,
          COALESCE(BIT_XOR(CRC32(CONCAT(`id`, ':', COALESCE(`{column}`, '')))), 0) AS checksum_xor
        FROM `{table}`
        """
    )
    return await cursor.fetchone()


def get_database_config(prefix: str) -> dict:
    key_prefix = f"{prefix}_"
    return {
        "host": os.getenv(f"{key_prefix}HOST", "127.0.0.1"),
        "port": int(os.getenv(f"{key_prefix}PORT", "3306")),
        "user": os.getenv(f"{key_prefix}USER", "qyd"),
        "password": os.getenv(f"{key_prefix}PASSWORD", ""),
        "db": os.getenv(f"{key_prefix}NAME", os.getenv("DB_NAME", "qyd")),
    }


async def main(config_prefix: str = "DB") -> int:
    load_env()
    database_config = get_database_config(config_prefix)
    conn = await aiomysql.connect(
        **database_config,
        charset="utf8mb4",
        autocommit=True,
    )

    try:
        cursor = await conn.cursor()
        for table, column, referenced_table, new_constraint_name in TARGETS:
            before_snapshot = await data_snapshot(cursor, table, column)
            foreign_key = await get_foreign_key(cursor, table, column, referenced_table)
            if not foreign_key:
                raise RuntimeError(f"未找到外键: {table}.{column} -> {referenced_table}.id")

            constraint_name, delete_rule = foreign_key
            if delete_rule == "SET NULL":
                print(
                    f"已是 SET NULL，跳过: {table}.{column} "
                    f"(总行数={before_snapshot[0]}, 已关联={before_snapshot[1]})"
                )
                continue

            if not await column_is_nullable(cursor, table, column):
                raise RuntimeError(f"字段不可为空，无法使用 SET NULL: {table}.{column}")

            # 表名、字段名来自上方固定白名单；约束名来自 information_schema。
            statement = f"""
                ALTER TABLE `{table}`
                  DROP FOREIGN KEY `{constraint_name}`,
                  ADD CONSTRAINT `{new_constraint_name}`
                    FOREIGN KEY (`{column}`) REFERENCES `{referenced_table}` (`id`)
                    ON DELETE SET NULL
            """
            await cursor.execute(statement)

            after_snapshot = await data_snapshot(cursor, table, column)
            if after_snapshot != before_snapshot:
                raise RuntimeError(
                    f"迁移前后数据快照不一致: {table}.{column}, "
                    f"before={before_snapshot}, after={after_snapshot}"
                )

            print(
                f"已更新为 SET NULL 且数据未变化: {table}.{column} "
                f"(总行数={after_snapshot[0]}, 已关联={after_snapshot[1]})"
            )

        await cursor.close()
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config-prefix",
        choices=("DB", "DB_SLAVE1", "DB_SLAVE2"),
        default="DB",
        help="选择 .env 中的数据库配置前缀",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args.config_prefix)))
