-- 增加 tokens 表的 token 字段长度
-- 从 VARCHAR(255) 改为 TEXT 类型，用于支持JWT格式的长Token

USE qyd;

-- 修改 token 字段类型为 TEXT
ALTER TABLE tokens MODIFY COLUMN token TEXT NOT NULL COMMENT '访问令牌';

-- 验证修改
DESCRIBE tokens;
