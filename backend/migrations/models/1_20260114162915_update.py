from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `server_country` ADD `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1;
        ALTER TABLE `server_group` ADD `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1;
        ALTER TABLE `server_country` ADD INDEX `idx_server_coun_status_40b03d` (`status`);
        ALTER TABLE `server_group` ADD INDEX `idx_server_grou_status_03ab0c` (`status`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `server_country` DROP INDEX `idx_server_coun_status_40b03d`;
        ALTER TABLE `server_group` DROP INDEX `idx_server_grou_status_03ab0c`;
        ALTER TABLE `server_group` DROP COLUMN `status`;
        ALTER TABLE `server_country` DROP COLUMN `status`;"""


MODELS_STATE = (
    "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"
    "yjYC"
)
