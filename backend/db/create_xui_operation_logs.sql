-- 创建 XUI 添加账号失败日志表(简化版)
-- 只记录添加账号失败的情况,方便重试

CREATE TABLE IF NOT EXISTS `xui_operation_logs` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT '主键 UUID',
    `inbound_id` CHAR(36) NOT NULL COMMENT '入站 ID',
    `inbound_info` VARCHAR(255) NOT NULL COMMENT '入站信息(host:port)',
    `account_id` CHAR(36) NOT NULL COMMENT '账号 ID',
    `account_username` VARCHAR(100) NOT NULL COMMENT '账号用户名',
    `error_message` TEXT NOT NULL COMMENT '错误信息',
    `retry_count` INT NOT NULL DEFAULT 0 COMMENT '重试次数',
    `is_resolved` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已解决(0:未解决 1:已解决)',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
    
    INDEX `idx_is_resolved_create_time` (`is_resolved`, `create_time`),
    INDEX `idx_inbound_id_is_resolved` (`inbound_id`, `is_resolved`),
    INDEX `idx_account_id_is_resolved` (`account_id`, `is_resolved`),
    INDEX `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='XUI 添加账号失败日志';
