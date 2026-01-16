from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `email_auth` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `email` VARCHAR(50) NOT NULL COMMENT '邮箱号',
    `auth_group` SMALLINT NOT NULL COMMENT '授权组',
    `authorization_address` LONGTEXT NOT NULL COMMENT '授权地址',
    `status` SMALLINT NOT NULL COMMENT '状态(1:待授权, 2:授权成功, 3:授权中, 4:授权失败)' DEFAULT 1,
    `back_code` VARCHAR(50) NOT NULL COMMENT '回调code',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    KEY `idx_email_auth_email_a01171` (`email`),
    KEY `idx_email_auth_status_cf71e0` (`status`),
    KEY `idx_email_auth_create__637d10` (`create_time`),
    KEY `idx_email_auth_email_41ba3e` (`email`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='邮箱授权';
CREATE TABLE IF NOT EXISTS `proxy_account` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `username` VARCHAR(36) NOT NULL COMMENT '用户名',
    `password` VARCHAR(36) NOT NULL COMMENT '密码',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    KEY `idx_proxy_accou_usernam_6be5c8` (`username`),
    KEY `idx_proxy_accou_create__02547d` (`create_time`),
    KEY `idx_proxy_accou_usernam_79e4f1` (`username`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='代理账号';
CREATE TABLE IF NOT EXISTS `server_country` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `short_name` VARCHAR(2) NOT NULL UNIQUE COMMENT '国家简称',
    `name` VARCHAR(20) NOT NULL COMMENT '国家名称',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    KEY `idx_server_coun_short_n_186238` (`short_name`),
    KEY `idx_server_coun_create__4e0dcd` (`create_time`),
    KEY `idx_server_coun_short_n_e4b519` (`short_name`, `name`)
) CHARACTER SET utf8mb4 COMMENT='国家信息';
CREATE TABLE IF NOT EXISTS `server_group` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `name` VARCHAR(20) NOT NULL UNIQUE COMMENT '分组名称',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `country_id` CHAR(36) NOT NULL COMMENT '国家',
    CONSTRAINT `fk_server_g_server_c_bba23df9` FOREIGN KEY (`country_id`) REFERENCES `server_country` (`id`) ON DELETE CASCADE,
    KEY `idx_server_grou_create__17c08b` (`create_time`)
) CHARACTER SET utf8mb4 COMMENT='分组信息';
CREATE TABLE IF NOT EXISTS `server_info` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `host` VARCHAR(20) NOT NULL COMMENT '服务器地址',
    `ssh_port` INT COMMENT 'ssh端口',
    `password` VARCHAR(128) COMMENT '服务器密码',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,4:异常)' DEFAULT 1,
    `domain` VARCHAR(50) COMMENT '域名',
    `is_sale` SMALLINT NOT NULL COMMENT '是否销售(1:是,2:否)' DEFAULT 1,
    `port` INT COMMENT '代理端口',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `group_id` CHAR(36) COMMENT '分组',
    CONSTRAINT `fk_server_i_server_g_ae6b48d8` FOREIGN KEY (`group_id`) REFERENCES `server_group` (`id`) ON DELETE CASCADE,
    KEY `idx_server_info_host_7d4234` (`host`),
    KEY `idx_server_info_status_99d9ce` (`status`),
    KEY `idx_server_info_domain_4e5295` (`domain`),
    KEY `idx_server_info_is_sale_2efe35` (`is_sale`),
    KEY `idx_server_info_create__c78a8d` (`create_time`),
    KEY `idx_server_info_host_d4ecc3` (`host`, `status`),
    KEY `idx_server_info_status_169cbe` (`status`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='服务器信息';
CREATE TABLE IF NOT EXISTS `email_info` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `email` VARCHAR(50) NOT NULL UNIQUE COMMENT '邮箱号',
    `password` VARCHAR(50) NOT NULL COMMENT '密码',
    `auxiliary_email` VARCHAR(50) NOT NULL COMMENT '辅助邮箱',
    `auxiliary_email_password` VARCHAR(50) NOT NULL COMMENT '辅助邮箱密码',
    `client_id` VARCHAR(50) COMMENT '客户端id',
    `access_token` LONGTEXT COMMENT 'access_token',
    `refresh_token` LONGTEXT COMMENT 'refresh_token',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1,
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `server_info_id` CHAR(36) COMMENT '代理信息',
    CONSTRAINT `fk_email_in_server_i_d41f3eb4` FOREIGN KEY (`server_info_id`) REFERENCES `server_info` (`id`) ON DELETE CASCADE,
    KEY `idx_email_info_email_622bde` (`email`),
    KEY `idx_email_info_status_86d621` (`status`),
    KEY `idx_email_info_create__b329f5` (`create_time`),
    KEY `idx_email_info_email_b960e6` (`email`, `status`),
    KEY `idx_email_info_status_5d3eec` (`status`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='邮箱信息';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
)
