-- 创建项目提现表
CREATE TABLE IF NOT EXISTS `project_withdrawal` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'UUID主键',
    `project_id` CHAR(36) NOT NULL COMMENT '所属项目ID',
    
    -- 平台币字段（支持18位小数）
    `platform_coin` DECIMAL(38, 18) NULL COMMENT '平台币当前余额',
    `platform_coin_change` DECIMAL(38, 18) NOT NULL DEFAULT 0 COMMENT '平台币最近一次变动',
    `platform_coin_history` JSON NULL COMMENT '平台币历史记录',
    
    -- 稳定币字段（支持18位小数）
    `stable_coin` DECIMAL(38, 18) NULL COMMENT '稳定币当前余额',
    `stable_coin_change` DECIMAL(38, 18) NOT NULL DEFAULT 0 COMMENT '稳定币最近一次变动',
    `stable_coin_history` JSON NULL COMMENT '稳定币历史记录',
    
    -- 人民币字段（2位小数）
    `rmb` DECIMAL(20, 2) NULL COMMENT '人民币当前余额',
    `rmb_change` DECIMAL(20, 2) NOT NULL DEFAULT 0 COMMENT '人民币最近一次变动',
    `rmb_history` JSON NULL COMMENT '人民币历史记录',
    
    `remark` VARCHAR(500) NULL COMMENT '备注',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
    
    UNIQUE KEY `uk_project_id` (`project_id`),
    KEY `idx_project_create` (`project_id`, `create_time`),
    KEY `idx_create_time` (`create_time`),
    
    CONSTRAINT `fk_withdrawal_project` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目提现记录';

-- 修改项目账号表的余额字段精度（支持18位小数）
ALTER TABLE `project_account` 
    MODIFY COLUMN `balance` DECIMAL(38, 18) NOT NULL DEFAULT 0 COMMENT '余额',
    MODIFY COLUMN `variable` DECIMAL(38, 18) NOT NULL DEFAULT 0 COMMENT '变动余额';
