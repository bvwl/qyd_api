from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `server_country` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `short_name` VARCHAR(2) NOT NULL UNIQUE COMMENT '国家简称',
    `name` VARCHAR(20) NOT NULL COMMENT '国家名称',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1,
    KEY `idx_server_coun_create__4e0dcd` (`create_time`),
    KEY `idx_server_coun_short_n_186238` (`short_name`),
    KEY `idx_server_coun_status_0d5813` (`status`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='国家信息';
CREATE TABLE IF NOT EXISTS `server_group` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(20) NOT NULL UNIQUE COMMENT '分组名称',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1,
    `country_id` CHAR(36) NOT NULL COMMENT '国家',
    CONSTRAINT `fk_server_g_server_c_bba23df9` FOREIGN KEY (`country_id`) REFERENCES `server_country` (`id`) ON DELETE CASCADE,
    KEY `idx_server_grou_create__17c08b` (`create_time`),
    KEY `idx_server_grou_name_385a8d` (`name`),
    KEY `idx_server_grou_country_677948` (`country_id`, `status`, `create_time`),
    KEY `idx_server_grou_status_bc31bd` (`status`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='分组信息';
CREATE TABLE IF NOT EXISTS `server_info` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `host` VARCHAR(20) NOT NULL COMMENT '服务器地址',
    `ssh_port` INT COMMENT 'ssh端口',
    `password` LONGTEXT COMMENT '服务器密码（加密存储）',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1,
    `domain` VARCHAR(50) COMMENT '域名',
    `is_sale` SMALLINT NOT NULL COMMENT '是否销售(1:是,2:否)' DEFAULT 1,
    `port` INT COMMENT '代理端口',
    `group_id` CHAR(36) COMMENT '分组',
    CONSTRAINT `fk_server_i_server_g_ae6b48d8` FOREIGN KEY (`group_id`) REFERENCES `server_group` (`id`) ON DELETE CASCADE,
    KEY `idx_server_info_create__c78a8d` (`create_time`),
    KEY `idx_server_info_host_7d4234` (`host`),
    KEY `idx_server_info_domain_4e5295` (`domain`),
    KEY `idx_server_info_status_5eefca` (`status`, `is_sale`, `create_time`),
    KEY `idx_server_info_group_i_949756` (`group_id`, `status`)
) CHARACTER SET utf8mb4 COMMENT='服务器信息';
CREATE TABLE IF NOT EXISTS `email_info` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `email` VARCHAR(50) NOT NULL UNIQUE COMMENT '邮箱号',
    `password` LONGTEXT NOT NULL COMMENT '密码',
    `auxiliary_email` VARCHAR(50) NOT NULL COMMENT '辅助邮箱',
    `auxiliary_email_password` LONGTEXT NOT NULL COMMENT '辅助邮箱密码',
    `client_id` VARCHAR(50) COMMENT '客户端id',
    `access_token` LONGTEXT COMMENT 'access_token',
    `refresh_token` LONGTEXT COMMENT 'refresh_token',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1,
    `server_id` CHAR(36) COMMENT '代理信息',
    CONSTRAINT `fk_email_in_server_i_7d1a5578` FOREIGN KEY (`server_id`) REFERENCES `server_info` (`id`) ON DELETE CASCADE,
    KEY `idx_email_info_create__b329f5` (`create_time`),
    KEY `idx_email_info_email_622bde` (`email`),
    KEY `idx_email_info_status_2439c1` (`status`, `server_id`, `create_time`),
    KEY `idx_email_info_status_5d3eec` (`status`, `create_time`),
    KEY `idx_email_info_server__0014bb` (`server_id`, `status`),
    KEY `idx_email_info_update__f1678e` (`update_time`)
) CHARACTER SET utf8mb4 COMMENT='邮箱信息';
CREATE TABLE IF NOT EXISTS `frontend_routes` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(64) NOT NULL COMMENT '路由名称（唯一标识）',
    `path` VARCHAR(128) NOT NULL COMMENT '路由路径',
    `component` VARCHAR(128) COMMENT '前端组件路径',
    `title` VARCHAR(64) NOT NULL COMMENT '菜单标题',
    `icon` VARCHAR(64) COMMENT '菜单图标',
    `sort` INT NOT NULL COMMENT '排序（数字越小越靠前）' DEFAULT 0,
    `redirect` VARCHAR(128) COMMENT '重定向路径',
    `is_hidden` BOOL NOT NULL COMMENT '是否隐藏菜单' DEFAULT 0,
    `is_cache` BOOL NOT NULL COMMENT '是否缓存页面' DEFAULT 1,
    `is_affix` BOOL NOT NULL COMMENT '是否固定在标签页' DEFAULT 0,
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1,
    `parent_id` CHAR(36) COMMENT '父级路由',
    CONSTRAINT `fk_frontend_frontend_329cfa62` FOREIGN KEY (`parent_id`) REFERENCES `frontend_routes` (`id`) ON DELETE CASCADE,
    KEY `idx_frontend_ro_create__f0144b` (`create_time`),
    KEY `idx_frontend_ro_status_6c1d4d` (`status`, `parent_id`, `sort`),
    KEY `idx_frontend_ro_parent__3f3e7b` (`parent_id`, `sort`),
    KEY `idx_frontend_ro_path_b958e7` (`path`),
    KEY `idx_frontend_ro_name_d714db` (`name`)
) CHARACTER SET utf8mb4 COMMENT='前端路由/菜单';
CREATE TABLE IF NOT EXISTS `users` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `email` VARCHAR(128) NOT NULL UNIQUE COMMENT '邮箱',
    `password` LONGTEXT NOT NULL COMMENT '密码加密',
    `nickname` VARCHAR(64) NOT NULL COMMENT '昵称',
    `avatar` VARCHAR(255) COMMENT '头像',
    `status` SMALLINT NOT NULL COMMENT '用户状态' DEFAULT 1,
    KEY `idx_users_create__915018` (`create_time`),
    KEY `idx_users_status_a9f08e` (`status`, `create_time`)
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
    KEY `idx_proxy_accou_user_id_6c40b0` (`user_id`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='服务器账号';
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
    KEY `idx_user_logs_user_id_bb65da` (`user_id`, `create_time`),
    KEY `idx_user_logs_user_id_697868` (`user_id`, `action`, `create_time`),
    KEY `idx_user_logs_action_578f52` (`action`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='用户操作日志';
CREATE TABLE IF NOT EXISTS `user_roles` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(32) NOT NULL COMMENT '角色名称',
    `code` VARCHAR(32) NOT NULL UNIQUE COMMENT '角色标识',
    `description` VARCHAR(255) COMMENT '角色描述',
    KEY `idx_user_roles_create__3690d2` (`create_time`),
    KEY `idx_user_roles_code_f2b101` (`code`),
    KEY `idx_user_roles_name_f92b79` (`name`)
) CHARACTER SET utf8mb4 COMMENT='用户角色';
CREATE TABLE IF NOT EXISTS `tokens` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `token` VARCHAR(255) NOT NULL COMMENT '访问令牌',
    `status` SMALLINT NOT NULL COMMENT '是否已失效' DEFAULT 1,
    `user_id` CHAR(36) NOT NULL COMMENT '所属用户',
    CONSTRAINT `fk_tokens_users_1ace17d9` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_tokens_create__9e2cd7` (`create_time`),
    KEY `idx_tokens_user_id_8091ad` (`user_id`, `status`, `create_time`),
    KEY `idx_tokens_status_91feb7` (`status`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='用户 Token';
CREATE TABLE IF NOT EXISTS `project_info` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(100) NOT NULL COMMENT '项目名称',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:未编写,3:编写中,4:项目结束,5:项目跑路,6:项目维护,7:未分配,8:账号不支持,9:ip不支持)' DEFAULT 1,
    `content` VARCHAR(255) COMMENT '项目内容文件路径或存储key',
    KEY `idx_project_inf_create__a010fc` (`create_time`),
    KEY `idx_project_inf_name_735a18` (`name`),
    KEY `idx_project_inf_status_cd6747` (`status`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='项目信息';
CREATE TABLE IF NOT EXISTS `project_wallet` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `private_key` LONGTEXT NOT NULL COMMENT '私钥（AES加密）',
    `public_key` LONGTEXT NOT NULL COMMENT '公钥',
    `mnemonic` LONGTEXT NOT NULL COMMENT '助记词（AES加密）',
    `chain` VARCHAR(255) NOT NULL COMMENT '链',
    `remark` VARCHAR(255) COMMENT '备注',
    KEY `idx_project_wal_create__c60e3b` (`create_time`),
    KEY `idx_project_wal_chain_c4e717` (`chain`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='项目钱包';
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
    `server_id` CHAR(36) COMMENT '关联服务器信息',
    `wallet_id` CHAR(36) COMMENT '关联钱包信息',
    CONSTRAINT `fk_project__project__74acb881` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_project__server_i_12a8ba71` FOREIGN KEY (`server_id`) REFERENCES `server_info` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_project__project__93399a32` FOREIGN KEY (`wallet_id`) REFERENCES `project_wallet` (`id`) ON DELETE CASCADE,
    KEY `idx_project_acc_create__90abb4` (`create_time`),
    KEY `idx_project_acc_account_ec909e` (`account`),
    KEY `idx_project_acc_project_267765` (`project_id`, `status`, `account_type`),
    KEY `idx_project_acc_status_44d572` (`status`, `account_type`, `create_time`),
    KEY `idx_project_acc_server__ff2cd9` (`server_id`, `status`),
    KEY `idx_project_acc_wallet__29c3f9` (`wallet_id`)
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
    KEY `idx_project_bal_create__15cc90` (`create_time`),
    KEY `idx_project_bal_account_8905fa` (`account_id`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='项目余额';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `role_route_rel` (
    `frontend_routes_id` CHAR(36) NOT NULL,
    `userrole_id` CHAR(36) NOT NULL,
    FOREIGN KEY (`frontend_routes_id`) REFERENCES `frontend_routes` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`userrole_id`) REFERENCES `user_roles` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_role_route__fronten_da521e` (`frontend_routes_id`, `userrole_id`)
) CHARACTER SET utf8mb4 COMMENT='路由关联的角色';
CREATE TABLE IF NOT EXISTS `user_role_rel` (
    `user_roles_id` CHAR(36) NOT NULL,
    `userinfo_id` CHAR(36) NOT NULL,
    FOREIGN KEY (`user_roles_id`) REFERENCES `user_roles` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`userinfo_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_user_role_r_user_ro_98a77d` (`user_roles_id`, `userinfo_id`)
) CHARACTER SET utf8mb4 COMMENT='角色关联的用户';
CREATE TABLE IF NOT EXISTS `project_user_rel` (
    `project_info_id` CHAR(36) NOT NULL,
    `userinfo_id` CHAR(36) NOT NULL,
    FOREIGN KEY (`project_info_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`userinfo_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_project_use_project_aaa166` (`project_info_id`, `userinfo_id`)
) CHARACTER SET utf8mb4 COMMENT='项目与用户关联';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "z9YqB6vt8PL8f/lYGmw="
)
