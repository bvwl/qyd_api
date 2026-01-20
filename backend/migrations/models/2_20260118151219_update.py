from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `users` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `email` VARCHAR(128) NOT NULL UNIQUE COMMENT '邮箱',
    `password_hash` LONGTEXT NOT NULL COMMENT '密码哈希',
    `nickname` VARCHAR(64) NOT NULL COMMENT '昵称',
    `avatar` VARCHAR(255) COMMENT '头像',
    `status` SMALLINT NOT NULL COMMENT '用户状态' DEFAULT 1,
    KEY `idx_users_create__915018` (`create_time`),
    KEY `idx_users_email_cd3b26` (`email`, `status`)
) CHARACTER SET utf8mb4 COMMENT='用户信息';
        CREATE TABLE IF NOT EXISTS `proxy_account` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `username` VARCHAR(36) NOT NULL COMMENT '用户名',
    `password` LONGTEXT NOT NULL COMMENT '密码（加密存储）',
    `user_id` CHAR(36) UNIQUE COMMENT '关联用户信息',
    CONSTRAINT `fk_proxy_ac_users_a11d1183` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_proxy_accou_create__02547d` (`create_time`),
    KEY `idx_proxy_accou_usernam_6be5c8` (`username`),
    KEY `idx_proxy_accou_usernam_79e4f1` (`username`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='服务器账号';
        CREATE TABLE IF NOT EXISTS `frontend_routes` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(64) NOT NULL COMMENT '路由名称',
    `path` VARCHAR(128) NOT NULL COMMENT '路由路径',
    `component` VARCHAR(128) NOT NULL COMMENT '前端组件路径',
    `status` SMALLINT NOT NULL COMMENT '状态(枚举) 1正常 2停用 3异常 4封禁' DEFAULT 1,
    KEY `idx_frontend_ro_create__f0144b` (`create_time`),
    KEY `idx_frontend_ro_path_39a387` (`path`, `status`)
) CHARACTER SET utf8mb4 COMMENT='前端路由';
        CREATE TABLE IF NOT EXISTS `permissions` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(64) NOT NULL COMMENT '权限名称',
    `code` VARCHAR(64) NOT NULL UNIQUE COMMENT '权限标识，如 user:create',
    `type` VARCHAR(16) NOT NULL COMMENT '权限类型 api / menu / button',
    `description` VARCHAR(255) COMMENT '权限描述',
    KEY `idx_permissions_create__141006` (`create_time`),
    KEY `idx_permissions_code_0b7aaf` (`code`, `type`)
) CHARACTER SET utf8mb4 COMMENT='权限表';
        CREATE TABLE IF NOT EXISTS `tokens` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `access_token` VARCHAR(255) NOT NULL UNIQUE COMMENT '访问令牌',
    `refresh_token` VARCHAR(255) UNIQUE COMMENT '刷新令牌',
    `expired_at` DATETIME(6) NOT NULL COMMENT '过期时间',
    `is_revoked` BOOL NOT NULL COMMENT '是否已失效' DEFAULT 0,
    `user_id` CHAR(36) NOT NULL COMMENT '所属用户',
    CONSTRAINT `fk_tokens_users_1ace17d9` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_tokens_create__9e2cd7` (`create_time`),
    KEY `idx_tokens_user_id_4b4cd1` (`user_id`, `is_revoked`)
) CHARACTER SET utf8mb4 COMMENT='用户 Token';
        CREATE TABLE IF NOT EXISTS `user_logs` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `action` SMALLINT NOT NULL COMMENT '操作类型(枚举)',
    `description` LONGTEXT NOT NULL COMMENT '操作描述',
    `ip` VARCHAR(64) COMMENT 'IP 地址',
    `user_agent` VARCHAR(255) COMMENT 'User-Agent',
    `user_id` CHAR(36) NOT NULL COMMENT '用户',
    CONSTRAINT `fk_user_log_users_f905f788` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_user_logs_create__07d73e` (`create_time`),
    KEY `idx_user_logs_ip_e138c0` (`ip`),
    KEY `idx_user_logs_user_id_bb65da` (`user_id`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='用户操作日志';
        CREATE TABLE IF NOT EXISTS `user_roles` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(32) NOT NULL COMMENT '角色名称',
    `code` VARCHAR(32) NOT NULL UNIQUE COMMENT '角色标识',
    `description` VARCHAR(255) COMMENT '角色描述',
    KEY `idx_user_roles_create__3690d2` (`create_time`),
    KEY `idx_user_roles_code_db6c83` (`code`, `description`)
) CHARACTER SET utf8mb4 COMMENT='用户角色';
        CREATE TABLE IF NOT EXISTS `project_info` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(100) NOT NULL COMMENT '项目名称',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:未编写,3:编写中,4:项目结束,5:项目跑路,6:项目维护,7:未分配,8:账号不支持,9:ip不支持)' DEFAULT 1,
    `content` VARCHAR(255) COMMENT '项目内容文件路径或存储key',
    KEY `idx_project_inf_create__a010fc` (`create_time`),
    KEY `idx_project_inf_name_735a18` (`name`),
    KEY `idx_project_inf_status_023aaf` (`status`),
    KEY `idx_project_inf_name_3c17b6` (`name`, `status`)
) CHARACTER SET utf8mb4 COMMENT='项目信息';
        CREATE TABLE IF NOT EXISTS `project_account` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `account` VARCHAR(255) NOT NULL COMMENT '账号',
    `password` LONGTEXT COMMENT '密码（加密存储）',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1,
    `account_type` SMALLINT NOT NULL COMMENT '账号类型(1:邮箱,2:钱包,3:x,4:其他1,5:其他2)' DEFAULT 1,
    `data` JSON COMMENT '扩展数据',
    `project_id` CHAR(36) NOT NULL COMMENT '所属项目',
    `server_info_id` CHAR(36) COMMENT '关联服务器信息',
    CONSTRAINT `fk_project__project__74acb881` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_project__server_i_e06e2917` FOREIGN KEY (`server_info_id`) REFERENCES `server_info` (`id`) ON DELETE CASCADE,
    KEY `idx_project_acc_create__90abb4` (`create_time`),
    KEY `idx_project_acc_account_ec909e` (`account`),
    KEY `idx_project_acc_status_16ddb2` (`status`),
    KEY `idx_project_acc_account_26e1b3` (`account_type`),
    KEY `idx_project_acc_account_95c93d` (`account`, `status`)
) CHARACTER SET utf8mb4 COMMENT='项目账号';
        CREATE TABLE IF NOT EXISTS `project_balance` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `balance` DECIMAL(18,6) NOT NULL COMMENT '余额',
    `variable` DECIMAL(18,6) NOT NULL COMMENT '变动余额',
    `history` JSON COMMENT '历史余额（可根据需要拆分为独立流水表）',
    `account_id` CHAR(36) NOT NULL UNIQUE COMMENT '关联账号',
    CONSTRAINT `fk_project__project__ee7ae4c2` FOREIGN KEY (`account_id`) REFERENCES `project_account` (`id`) ON DELETE CASCADE,
    KEY `idx_project_bal_create__15cc90` (`create_time`)
) CHARACTER SET utf8mb4 COMMENT='项目余额';
        CREATE TABLE IF NOT EXISTS `project_wallet` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `private_key` LONGTEXT NOT NULL COMMENT '私钥（AES加密）',
    `public_key` LONGTEXT NOT NULL COMMENT '公钥',
    `mnemonic` LONGTEXT NOT NULL COMMENT '助记词（AES加密）',
    `project_id` CHAR(36) NOT NULL UNIQUE COMMENT '关联项目',
    CONSTRAINT `fk_project__project__cba39da5` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE,
    KEY `idx_project_wal_create__c60e3b` (`create_time`)
) CHARACTER SET utf8mb4 COMMENT='项目钱包';
        ALTER TABLE `email_info` MODIFY COLUMN `auxiliary_email_password` LONGTEXT NOT NULL COMMENT '辅助邮箱密码';
        ALTER TABLE `email_info` MODIFY COLUMN `password` LONGTEXT NOT NULL COMMENT '密码';
        ALTER TABLE `server_info` MODIFY COLUMN `password` LONGTEXT COMMENT '服务器密码（加密存储）';
        ALTER TABLE `server_info` MODIFY COLUMN `password` LONGTEXT COMMENT '服务器密码（加密存储）';
        ALTER TABLE `server_info` MODIFY COLUMN `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1;
        DROP TABLE IF EXISTS `email_auth`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `email_info` MODIFY COLUMN `auxiliary_email_password` VARCHAR(50) NOT NULL COMMENT '辅助邮箱密码';
        ALTER TABLE `email_info` MODIFY COLUMN `password` VARCHAR(50) NOT NULL COMMENT '密码';
        ALTER TABLE `server_info` MODIFY COLUMN `password` VARCHAR(128) COMMENT '服务器密码';
        ALTER TABLE `server_info` MODIFY COLUMN `password` VARCHAR(128) COMMENT '服务器密码';
        ALTER TABLE `server_info` MODIFY COLUMN `status` SMALLINT NOT NULL COMMENT '状态(1:正常,4:异常)' DEFAULT 1;
        DROP TABLE IF EXISTS `user_roles`;
        DROP TABLE IF EXISTS `frontend_routes`;
        DROP TABLE IF EXISTS `tokens`;
        DROP TABLE IF EXISTS `project_balance`;
        DROP TABLE IF EXISTS `user_logs`;
        DROP TABLE IF EXISTS `permissions`;
        DROP TABLE IF EXISTS `users`;
        DROP TABLE IF EXISTS `proxy_account`;
        DROP TABLE IF EXISTS `project_wallet`;
        DROP TABLE IF EXISTS `project_info`;
        DROP TABLE IF EXISTS `project_account`;"""


MODELS_STATE = (
    "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"
)
