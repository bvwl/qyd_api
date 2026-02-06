-- 为 project_wallet 表添加 project_name 字段
-- 用于存储项目名称（用于显示，不用于加密）

ALTER TABLE project_wallet 
ADD COLUMN project_name VARCHAR(100) NULL COMMENT '项目名称（用于显示）' 
AFTER remark;

-- 添加索引以提高查询性能
CREATE INDEX idx_project_name ON project_wallet(project_name);
