-- XUI 管理系统数据库表创建脚本
-- 创建时间: 2026-01-25

-- 1. 创建 xui_server 表（XUI 服务器配置）
CREATE TABLE IF NOT EXISTS `xui_server` (
  `id` CHAR(36) NOT NULL COMMENT '主键 UUID',
  `name` VARCHAR(50) NOT NULL COMMENT '服务器名称',
  `host` VARCHAR(50) NOT NULL COMMENT '服务器地址（IP）',
  `domain` VARCHAR(100) DEFAULT NULL COMMENT '域名（用于 HTTPS 访问）',
  `port` INT NOT NULL DEFAULT 10010 COMMENT 'XUI 面板端口',
  `username` VARCHAR(50) NOT NULL COMMENT 'XUI 登录用户名',
  `password` TEXT NOT NULL COMMENT 'XUI 登录密码（加密存储）',
  `is_ssl` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否使用 HTTPS',
  `web_path` VARCHAR(50) NOT NULL DEFAULT '/web3' COMMENT 'Web 路径前缀',
  `status` INT NOT NULL DEFAULT 1 COMMENT '状态(1:正常,2:停用,3:异常)',
  `cert_file` VARCHAR(255) DEFAULT NULL COMMENT 'SSL 证书文件路径',
  `key_file` VARCHAR(255) DEFAULT NULL COMMENT 'SSL 私钥文件路径',
  `remark` TEXT DEFAULT NULL COMMENT '备注',
  `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `idx_status_create_time` (`status`, `create_time`),
  INDEX `idx_host` (`host`),
  INDEX `idx_domain` (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='XUI 服务器配置';

-- 2. 创建 xui_inbound 表（XUI 入站配置）
CREATE TABLE IF NOT EXISTS `xui_inbound` (
  `id` CHAR(36) NOT NULL COMMENT '主键 UUID',
  `server_id` CHAR(36) NOT NULL COMMENT '关联的 XUI 服务器 ID',
  `inbound_id` INT NOT NULL COMMENT 'XUI 面板中的入站 ID',
  `listen_host` VARCHAR(50) NOT NULL COMMENT '监听地址',
  `listen_port` INT NOT NULL COMMENT '监听端口',
  `protocol` INT NOT NULL COMMENT '协议类型(1:HTTP,2:SOCKS)',
  `remark` VARCHAR(100) DEFAULT NULL COMMENT '备注',
  `status` INT NOT NULL DEFAULT 1 COMMENT '状态(1:正常,2:停用,3:异常)',
  `default_username` VARCHAR(50) NOT NULL DEFAULT 'cqrxy' COMMENT '默认用户名',
  `default_password` TEXT DEFAULT NULL COMMENT '默认密码（加密存储）',
  `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`server_id`) REFERENCES `xui_server` (`id`) ON DELETE CASCADE,
  INDEX `idx_server_status` (`server_id`, `status`),
  INDEX `idx_listen_port` (`listen_port`),
  UNIQUE KEY `uk_server_host_port` (`server_id`, `listen_host`, `listen_port`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='XUI 入站配置';

-- 3. 创建 xui_inbound_account 表（入站和账号的多对多关系表）
CREATE TABLE IF NOT EXISTS `xui_inbound_account` (
  `xui_inbound_id` CHAR(36) NOT NULL COMMENT '入站 ID',
  `serveraccount_id` CHAR(36) NOT NULL COMMENT '账号 ID',
  PRIMARY KEY (`xui_inbound_id`, `serveraccount_id`),
  FOREIGN KEY (`xui_inbound_id`) REFERENCES `xui_inbound` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`serveraccount_id`) REFERENCES `proxy_account` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='XUI 入站和账号关系表';

-- 完成
SELECT 'XUI 表创建完成！' AS message;
