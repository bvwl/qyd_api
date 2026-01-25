-- 添加 XUI 操作日志路由

-- 1. 查找 XUI 管理父路由 ID
SET @xui_parent_id = (SELECT id FROM frontend_routes WHERE path = '/xui' AND parent_id IS NULL LIMIT 1);

-- 2. 获取下一个排序值
SET @next_sort = (SELECT COALESCE(MAX(sort), 0) + 1 FROM frontend_routes WHERE parent_id = @xui_parent_id);

-- 3. 插入操作日志路由
INSERT INTO frontend_routes (
    id,
    name,
    path,
    component,
    title,
    icon,
    parent_id,
    sort,
    status,
    route_type,
    permission,
    create_time,
    update_time
) VALUES (
    UUID(),
    'XuiOperationLog',
    '/xui/log',
    'views/Xui/XuiOperationLog',
    '操作日志',
    'FileTextOutlined',
    @xui_parent_id,
    @next_sort,
    1,
    1,
    'xui:log:view',
    NOW(),
    NOW()
);

-- 4. 获取新创建的路由 ID
SET @log_route_id = (SELECT id FROM frontend_routes WHERE path = '/xui/log' LIMIT 1);

-- 5. 绑定到 ADMIN 角色
INSERT INTO role_route_rel (role_id, route_id)
SELECT r.id, @log_route_id
FROM user_roles r
WHERE r.code = 'ADMIN'
AND NOT EXISTS (
    SELECT 1 FROM role_route_rel 
    WHERE role_id = r.id AND route_id = @log_route_id
);

-- 6. 绑定到 GM 角色
INSERT INTO role_route_rel (role_id, route_id)
SELECT r.id, @log_route_id
FROM user_roles r
WHERE r.code = 'GM'
AND NOT EXISTS (
    SELECT 1 FROM role_route_rel 
    WHERE role_id = r.id AND route_id = @log_route_id
);

-- 7. 查看结果
SELECT 
    fr.id,
    fr.name,
    fr.path,
    fr.title,
    fr.sort,
    fr.permission,
    COUNT(DISTINCT rr.role_id) as role_count
FROM frontend_routes fr
LEFT JOIN role_route_rel rr ON fr.id = rr.route_id
WHERE fr.path = '/xui/log'
GROUP BY fr.id, fr.name, fr.path, fr.title, fr.sort, fr.permission;
