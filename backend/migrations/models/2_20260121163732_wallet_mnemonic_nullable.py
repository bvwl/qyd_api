from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 修改 project_wallet 表的 mnemonic 字段为可空
        ALTER TABLE `project_wallet` MODIFY COLUMN `mnemonic` LONGTEXT COMMENT '助记词（AES加密）';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 恢复 project_wallet 表的 mnemonic 字段为非空
        ALTER TABLE `project_wallet` MODIFY COLUMN `mnemonic` LONGTEXT NOT NULL COMMENT '助记词（AES加密）';"""
