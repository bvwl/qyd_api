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
CREATE TABLE IF NOT EXISTS `project_account` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `account` VARCHAR(255) NOT NULL COMMENT '账号',
    `password` LONGTEXT COMMENT '密码（加密存储）',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1,
    `account_type` SMALLINT NOT NULL COMMENT '账号类型(1:邮箱,2:钱包,3:x,4:其他1,5:其他2)' DEFAULT 1,
    `data` JSON COMMENT '扩展数据',
    `balance` DECIMAL(18,6) NOT NULL COMMENT '余额' DEFAULT 0,
    `variable` DECIMAL(18,6) NOT NULL COMMENT '变动余额' DEFAULT 0,
    `balance_history` JSON COMMENT '历史余额（可根据需要拆分为独立流水表）',
    `project_id` CHAR(36) NOT NULL COMMENT '所属项目',
    `server_id` CHAR(36) COMMENT '关联服务器信息',
    CONSTRAINT `fk_project__project__74acb881` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_project__server_i_12a8ba71` FOREIGN KEY (`server_id`) REFERENCES `server_info` (`id`) ON DELETE CASCADE,
    KEY `idx_project_acc_create__90abb4` (`create_time`),
    KEY `idx_project_acc_account_ec909e` (`account`),
    KEY `idx_project_acc_project_267765` (`project_id`, `status`, `account_type`),
    KEY `idx_project_acc_status_44d572` (`status`, `account_type`, `create_time`),
    KEY `idx_project_acc_server__ff2cd9` (`server_id`, `status`),
    KEY `idx_project_acc_balance_22ccd9` (`balance`)
) CHARACTER SET utf8mb4 COMMENT='项目账号';
CREATE TABLE IF NOT EXISTS `project_wallet` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `private_key` LONGTEXT NOT NULL COMMENT '私钥（AES加密）',
    `public_key` LONGTEXT NOT NULL COMMENT '公钥',
    `mnemonic` LONGTEXT COMMENT '助记词（AES加密）',
    `chain` VARCHAR(255) NOT NULL COMMENT '链',
    `remark` VARCHAR(255) COMMENT '备注',
    `project_id` CHAR(36) COMMENT '所属项目',
    CONSTRAINT `fk_project__project__cba39da5` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE,
    KEY `idx_project_wal_create__c60e3b` (`create_time`),
    KEY `idx_project_wal_chain_c4e717` (`chain`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='项目钱包';
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
)
