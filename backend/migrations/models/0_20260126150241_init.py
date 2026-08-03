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
    CONSTRAINT `fk_email_in_server_i_7d1a5578` FOREIGN KEY (`server_id`) REFERENCES `server_info` (`id`) ON DELETE SET NULL,
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
    `route_type` SMALLINT NOT NULL COMMENT '路由类型(1:菜单,2:按钮,3:接口)' DEFAULT 1,
    `permission` VARCHAR(128) COMMENT '权限标识（如：user:create, user:edit）',
    `api_method` VARCHAR(16) COMMENT 'API方法(GET/POST/PUT/DELETE)',
    `api_path` VARCHAR(255) COMMENT 'API路径',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:异常)' DEFAULT 1,
    `parent_id` CHAR(36) COMMENT '父级路由',
    CONSTRAINT `fk_frontend_frontend_329cfa62` FOREIGN KEY (`parent_id`) REFERENCES `frontend_routes` (`id`) ON DELETE CASCADE,
    KEY `idx_frontend_ro_create__f0144b` (`create_time`),
    KEY `idx_frontend_ro_status_6c1d4d` (`status`, `parent_id`, `sort`),
    KEY `idx_frontend_ro_parent__3f3e7b` (`parent_id`, `sort`),
    KEY `idx_frontend_ro_path_b958e7` (`path`),
    KEY `idx_frontend_ro_name_d714db` (`name`),
    KEY `idx_frontend_ro_permiss_6b5e66` (`permission`),
    KEY `idx_frontend_ro_route_t_0860b9` (`route_type`)
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
    `is_all_inbound_added` BOOL NOT NULL COMMENT '是否已添加到所有入站(用于XUI管理)' DEFAULT 0,
    `user_id` CHAR(36) UNIQUE COMMENT '关联用户信息',
    CONSTRAINT `fk_proxy_ac_users_a11d1183` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_proxy_accou_create__02547d` (`create_time`),
    KEY `idx_proxy_accou_usernam_6be5c8` (`username`),
    KEY `idx_proxy_accou_is_all__6b5126` (`is_all_inbound_added`),
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
    `user_id` CHAR(36) COMMENT '用户(可为空,用于系统日志)',
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
    `token` LONGTEXT NOT NULL COMMENT '访问令牌',
    `status` SMALLINT NOT NULL COMMENT '是否已失效' DEFAULT 1,
    `user_id` CHAR(36) NOT NULL COMMENT '所属用户',
    CONSTRAINT `fk_tokens_users_1ace17d9` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_tokens_create__9e2cd7` (`create_time`),
    KEY `idx_tokens_user_id_8091ad` (`user_id`, `status`, `create_time`),
    KEY `idx_tokens_status_91feb7` (`status`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='用户 Token';
CREATE TABLE IF NOT EXISTS `xui_operation_logs` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `inbound_id` CHAR(36) NOT NULL COMMENT '入站 ID',
    `inbound_info` VARCHAR(255) NOT NULL COMMENT '入站信息(host:port)',
    `account_id` CHAR(36) NOT NULL COMMENT '账号 ID',
    `account_username` VARCHAR(100) NOT NULL COMMENT '账号用户名',
    `error_message` LONGTEXT NOT NULL COMMENT '错误信息',
    `retry_count` INT NOT NULL COMMENT '重试次数' DEFAULT 0,
    `is_resolved` BOOL NOT NULL COMMENT '是否已解决' DEFAULT 0,
    KEY `idx_xui_operati_create__6bdd0c` (`create_time`),
    KEY `idx_xui_operati_inbound_bb4f4c` (`inbound_id`),
    KEY `idx_xui_operati_account_9fef3e` (`account_id`),
    KEY `idx_xui_operati_is_reso_151beb` (`is_resolved`),
    KEY `idx_xui_operati_is_reso_5e0b57` (`is_resolved`, `create_time`),
    KEY `idx_xui_operati_inbound_d51914` (`inbound_id`, `is_resolved`),
    KEY `idx_xui_operati_account_329199` (`account_id`, `is_resolved`)
) CHARACTER SET utf8mb4 COMMENT='XUI 添加账号失败日志';
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
    `balance` DECIMAL(38,18) NOT NULL COMMENT '余额' DEFAULT 0,
    `variable` DECIMAL(38,18) NOT NULL COMMENT '变动余额' DEFAULT 0,
    `balance_history` JSON COMMENT '历史余额（可根据需要拆分为独立流水表）',
    `project_id` CHAR(36) NOT NULL COMMENT '所属项目',
    `server_id` CHAR(36) COMMENT '关联服务器信息',
    CONSTRAINT `fk_project__project__74acb881` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_project__server_i_12a8ba71` FOREIGN KEY (`server_id`) REFERENCES `server_info` (`id`) ON DELETE SET NULL,
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
CREATE TABLE IF NOT EXISTS `project_withdrawal` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `platform_coin` DECIMAL(38,18) COMMENT '平台币当前余额',
    `platform_coin_change` DECIMAL(38,18) NOT NULL COMMENT '平台币最近一次变动' DEFAULT 0,
    `platform_coin_history` JSON COMMENT '平台币历史记录（所有记录，格式：{\'2026-01-25 14:30:45\': \'100.500000000000000000\'}）',
    `stable_coin` DECIMAL(38,18) COMMENT '稳定币当前余额',
    `stable_coin_change` DECIMAL(38,18) NOT NULL COMMENT '稳定币最近一次变动' DEFAULT 0,
    `stable_coin_history` JSON COMMENT '稳定币历史记录（所有记录，格式：{\'2026-01-25 14:30:45\': \'100.500000000000000000\'}）',
    `rmb` DECIMAL(20,2) COMMENT '人民币当前余额',
    `rmb_change` DECIMAL(20,2) NOT NULL COMMENT '人民币最近一次变动' DEFAULT 0,
    `rmb_history` JSON COMMENT '人民币历史记录（所有记录，格式：{\'2026-01-25 14:30:45\': \'100.50\'}）',
    `remark` VARCHAR(500) COMMENT '备注',
    `project_id` CHAR(36) NOT NULL COMMENT '所属项目',
    UNIQUE KEY `uid_project_wit_project_d2f1ed` (`project_id`),
    CONSTRAINT `fk_project__project__a660670b` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE,
    KEY `idx_project_wit_create__73955c` (`create_time`),
    KEY `idx_project_wit_project_d2f1ed` (`project_id`),
    KEY `idx_project_wit_project_111232` (`project_id`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='项目提现记录';
CREATE TABLE IF NOT EXISTS `project_daily_stats` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `date` DATE NOT NULL COMMENT '统计日期',
    `update_count` INT NOT NULL COMMENT '当天更新的账号数量' DEFAULT 0,
    `project_id` CHAR(36) NOT NULL COMMENT '所属项目',
    UNIQUE KEY `uid_project_dai_project_a79157` (`project_id`, `date`),
    CONSTRAINT `fk_project__project__ad7c2d6d` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE,
    KEY `idx_project_dai_create__fcb0bf` (`create_time`),
    KEY `idx_project_dai_date_54ef20` (`date`),
    KEY `idx_project_dai_project_e60567` (`project_id`),
    KEY `idx_project_dai_project_a79157` (`project_id`, `date`)
) CHARACTER SET utf8mb4 COMMENT='项目每日统计';
CREATE TABLE IF NOT EXISTS `departments` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `code` VARCHAR(32) NOT NULL UNIQUE COMMENT '部门编码',
    `name` VARCHAR(64) NOT NULL COMMENT '部门名称',
    `description` VARCHAR(255) COMMENT '部门描述',
    `sort` INT NOT NULL COMMENT '排序' DEFAULT 0,
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:停用)' DEFAULT 1,
    `leader_id` CHAR(36) COMMENT '部门负责人',
    `parent_id` CHAR(36) COMMENT '父级部门',
    CONSTRAINT `fk_departme_users_82430b9b` FOREIGN KEY (`leader_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_departme_departme_fb330fa8` FOREIGN KEY (`parent_id`) REFERENCES `departments` (`id`) ON DELETE CASCADE,
    KEY `idx_departments_create__fff5e4` (`create_time`),
    KEY `idx_departments_code_94b59c` (`code`),
    KEY `idx_departments_parent__13b951` (`parent_id`),
    KEY `idx_departments_status_ff820b` (`status`)
) CHARACTER SET utf8mb4 COMMENT='部门表';
CREATE TABLE IF NOT EXISTS `menus_v2` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `code` VARCHAR(64) NOT NULL UNIQUE COMMENT '菜单编码（唯一标识）',
    `title` VARCHAR(64) NOT NULL COMMENT '菜单标题（显示名称）',
    `path` VARCHAR(128) NOT NULL COMMENT '路由路径（如：/user/list）',
    `component` VARCHAR(128) COMMENT '组件路径（如：views/User/List）',
    `icon` VARCHAR(64) COMMENT '图标（如：UserOutlined）',
    `sort` INT NOT NULL COMMENT '排序（数字越小越靠前）' DEFAULT 0,
    `is_hidden` BOOL NOT NULL COMMENT '是否隐藏菜单' DEFAULT 0,
    `is_cache` BOOL NOT NULL COMMENT '是否缓存页面' DEFAULT 1,
    `is_affix` BOOL NOT NULL COMMENT '是否固定在标签页' DEFAULT 0,
    `redirect` VARCHAR(128) COMMENT '重定向路径',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:停用)' DEFAULT 1,
    `parent_id` CHAR(36) COMMENT '父级菜单',
    CONSTRAINT `fk_menus_v2_menus_v2_2c8cbd0c` FOREIGN KEY (`parent_id`) REFERENCES `menus_v2` (`id`) ON DELETE CASCADE,
    KEY `idx_menus_v2_create__9b1201` (`create_time`),
    KEY `idx_menus_v2_code_f6a4ce` (`code`),
    KEY `idx_menus_v2_parent__92adde` (`parent_id`, `sort`),
    KEY `idx_menus_v2_status_dcbda3` (`status`)
) CHARACTER SET utf8mb4 COMMENT='菜单表（v2）';
CREATE TABLE IF NOT EXISTS `permissions_v2` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `code` VARCHAR(64) NOT NULL UNIQUE COMMENT '权限编码（如：user:create）',
    `name` VARCHAR(64) NOT NULL COMMENT '权限名称（如：创建用户）',
    `description` VARCHAR(255) COMMENT '权限描述',
    `resource` VARCHAR(32) NOT NULL COMMENT '资源类型（user/project/server/mail）',
    `action` VARCHAR(32) NOT NULL COMMENT '操作类型（create/edit/delete/view/export）',
    `permission_type` SMALLINT NOT NULL COMMENT '权限类型(1:功能,2:API,3:数据)' DEFAULT 1,
    `api_method` VARCHAR(16) COMMENT 'HTTP方法（GET/POST/PUT/DELETE）',
    `api_path` VARCHAR(255) COMMENT 'API路径（如：/api/v1/user）',
    `group` VARCHAR(32) COMMENT '权限分组（用于前端分组展示）',
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:停用)' DEFAULT 1,
    KEY `idx_permissions_create__7220eb` (`create_time`),
    KEY `idx_permissions_code_f9146d` (`code`),
    KEY `idx_permissions_resourc_8f0768` (`resource`),
    KEY `idx_permissions_permiss_aefa7e` (`permission_type`),
    KEY `idx_permissions_status_487afb` (`status`),
    KEY `idx_permissions_group_0d1573` (`group`)
) CHARACTER SET utf8mb4 COMMENT='权限表（v2）';
CREATE TABLE IF NOT EXISTS `roles_v2` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `code` VARCHAR(32) NOT NULL UNIQUE COMMENT '角色编码（唯一标识）',
    `name` VARCHAR(32) NOT NULL COMMENT '角色名称',
    `description` VARCHAR(255) COMMENT '角色描述',
    `level` INT NOT NULL COMMENT '角色级别（数字越大权限越高，ADMIN=100）' DEFAULT 0,
    `data_scope` SMALLINT NOT NULL COMMENT '数据权限范围(1:全部,2:本部门,3:本部门及下级,4:仅本人,5:自定义)' DEFAULT 4,
    `is_system` BOOL NOT NULL COMMENT '是否系统内置角色（不可删除）' DEFAULT 0,
    `status` SMALLINT NOT NULL COMMENT '状态(1:正常,2:停用)' DEFAULT 1,
    KEY `idx_roles_v2_create__ef45de` (`create_time`),
    KEY `idx_roles_v2_code_79ecd8` (`code`),
    KEY `idx_roles_v2_status_d0522d` (`status`),
    KEY `idx_roles_v2_level_aaf309` (`level`),
    KEY `idx_roles_v2_is_syst_b656a8` (`is_system`)
) CHARACTER SET utf8mb4 COMMENT='角色表（v2）';
CREATE TABLE IF NOT EXISTS `custom_data_scopes_v2` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `resource` VARCHAR(32) NOT NULL COMMENT '资源类型（project/user/server）',
    `resource_id` CHAR(36) NOT NULL COMMENT '资源ID',
    `description` VARCHAR(255) COMMENT '描述',
    `role_id` CHAR(36) COMMENT '角色',
    `user_id` CHAR(36) COMMENT '用户',
    CONSTRAINT `fk_custom_d_roles_v2_400a5cf7` FOREIGN KEY (`role_id`) REFERENCES `roles_v2` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_custom_d_users_42e29c52` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_custom_data_create__8f80d4` (`create_time`),
    KEY `idx_custom_data_role_id_13090a` (`role_id`, `resource`),
    KEY `idx_custom_data_user_id_b15a91` (`user_id`, `resource`),
    KEY `idx_custom_data_resourc_0e12d1` (`resource`, `resource_id`)
) CHARACTER SET utf8mb4 COMMENT='自定义数据权限表（v2）';
CREATE TABLE IF NOT EXISTS `xui_server` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(50) NOT NULL COMMENT '服务器名称',
    `host` VARCHAR(50) NOT NULL COMMENT '服务器地址（IP）',
    `domain` VARCHAR(100) COMMENT '域名（用于 HTTPS 访问）',
    `port` INT NOT NULL COMMENT 'XUI 面板端口' DEFAULT 10010,
    `username` VARCHAR(50) NOT NULL COMMENT 'XUI 登录用户名',
    `password` LONGTEXT NOT NULL COMMENT 'XUI 登录密码（加密存储）',
    `is_ssl` BOOL NOT NULL COMMENT '是否使用 HTTPS' DEFAULT 0,
    `web_path` VARCHAR(50) NOT NULL COMMENT 'Web 路径前缀' DEFAULT '/web3',
    `status` SMALLINT NOT NULL COMMENT '状态' DEFAULT 1,
    `cert_file` VARCHAR(255) COMMENT 'SSL 证书文件路径',
    `key_file` VARCHAR(255) COMMENT 'SSL 私钥文件路径',
    `remark` LONGTEXT COMMENT '备注',
    KEY `idx_xui_server_create__0a6884` (`create_time`),
    KEY `idx_xui_server_host_1c2b82` (`host`),
    KEY `idx_xui_server_domain_8a5869` (`domain`),
    KEY `idx_xui_server_status_1e5493` (`status`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='XUI 服务器配置';
CREATE TABLE IF NOT EXISTS `xui_inbound` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `inbound_id` INT NOT NULL COMMENT 'XUI 面板中的入站 ID',
    `listen_host` VARCHAR(50) NOT NULL COMMENT '监听地址',
    `listen_port` INT NOT NULL COMMENT '监听端口',
    `protocol` SMALLINT NOT NULL COMMENT '协议类型',
    `remark` VARCHAR(100) COMMENT '备注',
    `status` SMALLINT NOT NULL COMMENT '状态' DEFAULT 1,
    `default_username` VARCHAR(50) NOT NULL COMMENT '默认用户名' DEFAULT 'cqrxy',
    `default_password` LONGTEXT COMMENT '默认密码（加密存储）',
    `server_id` CHAR(36) NOT NULL COMMENT '关联的 XUI 服务器',
    UNIQUE KEY `uid_xui_inbound_server__d6841f` (`server_id`, `listen_host`, `listen_port`),
    CONSTRAINT `fk_xui_inbo_xui_serv_84c01329` FOREIGN KEY (`server_id`) REFERENCES `xui_server` (`id`) ON DELETE CASCADE,
    KEY `idx_xui_inbound_create__6652df` (`create_time`),
    KEY `idx_xui_inbound_listen__c59afd` (`listen_port`),
    KEY `idx_xui_inbound_server__3a0410` (`server_id`, `status`),
    KEY `idx_xui_inbound_server__d6841f` (`server_id`, `listen_host`, `listen_port`)
) CHARACTER SET utf8mb4 COMMENT='XUI 入站配置';
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
) CHARACTER SET utf8mb4 COMMENT='项目与用户关联';
CREATE TABLE IF NOT EXISTS `role_menu_v2_rel` (
    `roles_v2_id` CHAR(36) NOT NULL,
    `menu_id` CHAR(36) NOT NULL,
    FOREIGN KEY (`roles_v2_id`) REFERENCES `roles_v2` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`menu_id`) REFERENCES `menus_v2` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_role_menu_v_roles_v_fa1980` (`roles_v2_id`, `menu_id`)
) CHARACTER SET utf8mb4 COMMENT='角色关联的菜单';
CREATE TABLE IF NOT EXISTS `role_permission_v2_rel` (
    `roles_v2_id` CHAR(36) NOT NULL,
    `permission_id` CHAR(36) NOT NULL,
    FOREIGN KEY (`roles_v2_id`) REFERENCES `roles_v2` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`permission_id`) REFERENCES `permissions_v2` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_role_permis_roles_v_84f198` (`roles_v2_id`, `permission_id`)
) CHARACTER SET utf8mb4 COMMENT='角色关联的权限';
CREATE TABLE IF NOT EXISTS `user_role_v2_rel` (
    `roles_v2_id` CHAR(36) NOT NULL,
    `userinfo_id` CHAR(36) NOT NULL,
    FOREIGN KEY (`roles_v2_id`) REFERENCES `roles_v2` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`userinfo_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_user_role_v_roles_v_0742ee` (`roles_v2_id`, `userinfo_id`)
) CHARACTER SET utf8mb4 COMMENT='角色关联的用户';
CREATE TABLE IF NOT EXISTS `xui_inbound_account` (
    `xui_inbound_id` CHAR(36) NOT NULL,
    `serveraccount_id` CHAR(36) NOT NULL,
    FOREIGN KEY (`xui_inbound_id`) REFERENCES `xui_inbound` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`serveraccount_id`) REFERENCES `proxy_account` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_xui_inbound_xui_inb_4b1934` (`xui_inbound_id`, `serveraccount_id`)
) CHARACTER SET utf8mb4 COMMENT='关联的服务器账号';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "z/9vL9/wF+FZFv"
)
