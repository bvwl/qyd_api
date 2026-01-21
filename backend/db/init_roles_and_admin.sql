-- ==========================================
-- 数据库初始化脚本（SQL版本）
-- 初始化角色和管理员账户
-- ==========================================

-- 使用数据库
USE qyd;

-- ==========================================
-- 1. 初始化角色
-- ==========================================

-- 清空现有角色（可选，谨慎使用）
-- DELETE FROM user_roles;

-- 插入角色（如果不存在则插入）
INSERT INTO user_roles (id, name, code, description, create_time, update_time)
VALUES 
    (UUID(), '管理员', 'ADMIN', '系统管理员，拥有所有权限', NOW(), NOW()),
    (UUID(), '项目管理员', 'GM', '项目管理员，负责项目运营和管理', NOW(), NOW()),
    (UUID(), '技术人员', 'IT', '技术人员，负责系统维护和技术支持', NOW(), NOW()),
    (UUID(), '手动操作员', 'MANUAL', '手动操作员，负责日常手动操作', NOW(), NOW())
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    description = VALUES(description),
    update_time = NOW();

-- ==========================================
-- 2. 创建管理员账户
-- ==========================================

-- 注意：密码需要使用bcrypt加密
-- 这里的密码哈希是 "2201101122@qq.com" 的bcrypt加密结果
-- 请运行Python脚本来生成正确的密码哈希

-- 插入管理员用户（如果不存在）
INSERT INTO users (id, email, password, nickname, avatar, status, create_time, update_time)
VALUES (
    UUID(),
    'zhiyu',
    '$2b$12$placeholder_password_hash_here',  -- 需要替换为实际的bcrypt哈希
    '至宇',
    NULL,
    1,  -- 正常状态
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE 
    nickname = VALUES(nickname),
    status = VALUES(status),
    update_time = NOW();

-- ==========================================
-- 3. 分配角色给管理员
-- ==========================================

-- 获取管理员用户ID和ADMIN角色ID，建立关联
INSERT INTO user_role_rel (userrole_id, userinfo_id)
SELECT 
    (SELECT id FROM user_roles WHERE code = 'ADMIN' LIMIT 1) as role_id,
    (SELECT id FROM users WHERE email = 'zhiyu' LIMIT 1) as user_id
WHERE NOT EXISTS (
    SELECT 1 FROM user_role_rel 
    WHERE userrole_id = (SELECT id FROM user_roles WHERE code = 'ADMIN' LIMIT 1)
    AND userinfo_id = (SELECT id FROM users WHERE email = 'zhiyu' LIMIT 1)
);

-- ==========================================
-- 4. 验证初始化结果
-- ==========================================

-- 查看所有角色
SELECT id, name, code, description FROM user_roles;

-- 查看管理员账户
SELECT u.id, u.email, u.nickname, u.status, GROUP_CONCAT(r.code) as roles
FROM users u
LEFT JOIN user_role_rel urr ON u.id = urr.userinfo_id
LEFT JOIN user_roles r ON urr.userrole_id = r.id
WHERE u.email = 'zhiyu'
GROUP BY u.id;

-- ==========================================
-- 说明
-- ==========================================
-- 
-- ⚠️ 重要提示：
-- 1. 此SQL脚本无法直接生成bcrypt密码哈希
-- 2. 请使用Python脚本 init_roles_and_admin.py 来初始化
-- 3. 或者手动生成密码哈希后替换上面的 placeholder_password_hash_here
--
-- 生成密码哈希的方法：
-- python -c "from app.core.tools import hashing; print(hashing.hash('2201101122@qq.com'))"
--
