-- 为 proxy_account 表添加 is_all_inbound_added 字段
-- 用于标记账号是否已添加到所有 XUI 入站

ALTER TABLE `proxy_account` 
ADD COLUMN `is_all_inbound_added` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已添加到所有入站(用于XUI管理)' AFTER `password`,
ADD INDEX `idx_is_all_inbound_added` (`is_all_inbound_added`);
