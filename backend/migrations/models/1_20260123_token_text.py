from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    """
    将 tokens 表的 token 字段从 VARCHAR(255) 改为 TEXT
    以支持长JWT Token（10年有效期的JWT约316字符）
    """
    return """
        ALTER TABLE `tokens` MODIFY COLUMN `token` TEXT NOT NULL COMMENT '访问令牌';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    """
    回滚：将 token 字段改回 VARCHAR(255)
    注意：如果已有超过255字符的token，回滚会失败
    """
    return """
        ALTER TABLE `tokens` MODIFY COLUMN `token` VARCHAR(255) NOT NULL COMMENT '访问令牌';"""
