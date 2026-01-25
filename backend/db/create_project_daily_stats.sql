-- 创建项目每日统计表
CREATE TABLE IF NOT EXISTS `project_daily_stats` (
    `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT '主键ID',
    `date` DATE NOT NULL COMMENT '统计日期',
    `update_count` INT NOT NULL DEFAULT 0 COMMENT '当天更新的账号数量',
    `project_id` CHAR(36) NOT NULL COMMENT '所属项目ID',
    `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
    `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
    KEY `idx_project_daily_stats_date` (`date`),
    KEY `idx_project_daily_stats_project_id` (`project_id`),
    KEY `idx_project_daily_stats_create_time` (`create_time`),
    KEY `idx_project_daily_stats_project_id_date` (`project_id`, `date`),
    UNIQUE KEY `uid_project_daily_stats_project_id_date` (`project_id`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目每日统计';
