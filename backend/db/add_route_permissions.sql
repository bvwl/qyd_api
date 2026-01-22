-- 添加路由权限相关字段
-- 为 frontend_routes 表添加新字段

USE qyd;

-- 添加路由类型字段
ALTER TABLE frontend_routes 
ADD COLUMN route_type SMALLINT NOT NULL DEFAULT 1 COMMENT '路由类型(1:菜单,2:按钮,3:接口)' AFTER status;

-- 添加权限标识字段
ALTER TABLE frontend_routes 
ADD COLUMN permission VARCHAR(128) NULL COMMENT '权限标识（如：user:create, user:edit）' AFTER route_type;

-- 添加API方法字段
ALTER TABLE frontend_routes 
ADD COLUMN api_method VARCHAR(16) NULL COMMENT 'API方法(GET/POST/PUT/DELETE)' AFTER permission;

-- 添加API路径字段
ALTER TABLE frontend_routes 
ADD COLUMN api_path VARCHAR(255) NULL COMMENT 'API路径' AFTER api_method;

-- 添加索引
CREATE INDEX idx_permission ON frontend_routes(permission);
CREATE INDEX idx_route_type ON frontend_routes(route_type);

-- 显示表结构
DESCRIBE frontend_routes;
