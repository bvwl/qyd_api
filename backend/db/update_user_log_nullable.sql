-- 修改 user_logs 表,让 user_id 可以为空
-- 用于记录系统操作日志(如 XUI 自动同步失败等)

ALTER TABLE user_logs MODIFY COLUMN user_id CHAR(36) NULL COMMENT '用户(可为空,用于系统日志)';
