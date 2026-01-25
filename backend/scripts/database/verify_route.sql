-- 验证批量创建钱包路由配置

-- 1. 检查路由是否存在
SELECT '1. 检查路由是否存在' as step;
SELECT id, title, path, component, sort, parent_id
FROM frontend_route
WHERE path = '/project/wallet/batch-create';

-- 2. 检查项目管理下的所有子路由
SELECT '2. 项目管理下的所有子路由' as step;
SELECT r.id, r.title, r.path, r.sort
FROM frontend_route r
WHERE r.parent_id = (SELECT id FROM frontend_route WHERE path = '/project')
ORDER BY r.sort;

-- 3. 检查ADMIN角色是否有此路由权限
SELECT '3. ADMIN角色是否有此路由权限' as step;
SELECT COUNT(*) as has_permission
FROM role_route_rel rr
JOIN role r ON rr.role_id = r.id
JOIN frontend_route fr ON rr.route_id = fr.id
WHERE r.code = 'ADMIN' AND fr.path = '/project/wallet/batch-create';

-- 4. 统计ADMIN角色的路由数量
SELECT '4. ADMIN角色的路由数量' as step;
SELECT r.name, COUNT(rr.route_id) as route_count
FROM role r
LEFT JOIN role_route_rel rr ON r.id = rr.role_id
WHERE r.code = 'ADMIN'
GROUP BY r.id, r.name;
