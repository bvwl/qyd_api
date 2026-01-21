# GM角色名称修正

## 修正时间
2026-01-21

## 问题描述
GM角色被错误地标注为"游戏管理员"，实际应该是"项目管理员"。

## 修正范围

### 1. 数据库
✅ 已更新 `user_roles` 表中GM角色的名称和描述

**修正前**:
- 名称: 游戏管理员
- 描述: 游戏管理员，负责游戏运营和管理

**修正后**:
- 名称: 项目管理员
- 描述: 项目管理员，负责项目运营和管理

### 2. 后端文件

✅ **backend/db/init_roles_and_admin.py**
- 角色配置中的名称和描述

✅ **backend/db/init_roles_and_admin.sql**
- SQL初始化脚本中的INSERT语句

✅ **backend/db/README.md**
- 角色说明表格
- 示例输出

✅ **backend/db/INITIALIZATION_SUMMARY.md**
- 角色列表

✅ **backend/README.md**
- 角色权限说明

✅ **backend/app/utils/jwt_tool.py**
- 权限检查错误提示信息

### 3. 前端文件

✅ **frontend/src/views/Dashboard/index.tsx**
- ROLE_NAME_MAP 映射

✅ **frontend/src/views/User/UserList.tsx**
- 角色说明列表

### 4. 文档文件

✅ **docs/fixes/DASHBOARD_IMPLEMENTATION.md**
- 角色权限说明

✅ **docs/fixes/DASHBOARD_USE_EXISTING_API.md**
- 角色示例代码注释

✅ **docs/fixes/README_NEW.md**
- 默认角色列表

## 修正方法

### 数据库更新
使用专门的更新脚本：

```bash
python backend/db/update_gm_role_description.py
```

脚本功能：
- 连接数据库
- 查找GM角色
- 更新名称和描述
- 验证更新结果

### 文件更新
使用批量替换：
- "游戏管理员" → "项目管理员"
- "负责游戏运营和管理" → "负责项目运营和管理"

## 角色定义

### 完整角色列表

| 代码 | 名称 | 描述 |
|------|------|------|
| ADMIN | 管理员 | 系统管理员，拥有所有权限 |
| GM | 项目管理员 | 项目管理员，负责项目运营和管理 |
| IT | 技术人员 | 技术人员，负责系统维护和技术支持 |
| MANUAL | 手动操作员 | 手动操作员，负责日常手动操作 |

### 权限说明

**项目管理员 (GM)**:
- 可以查看和管理所有项目
- 可以查看和管理所有项目账户
- 可以查看项目相关的服务器信息
- 不能管理用户和角色
- 不能修改系统配置

## 验证

### 数据库验证
```sql
SELECT code, name, description FROM user_roles WHERE code='GM';
```

预期结果：
```
+------+--------------+----------------------------------------+
| code | name         | description                            |
+------+--------------+----------------------------------------+
| GM   | 项目管理员   | 项目管理员，负责项目运营和管理         |
+------+--------------+----------------------------------------+
```

### 前端验证
1. 登录系统
2. 进入用户管理页面
3. 查看角色说明，应显示"项目管理员"
4. 进入仪表盘，角色标签应显示"项目管理员"

### 后端验证
```bash
# 查看初始化脚本输出
python backend/db/init_roles_and_admin.py

# 应该看到：
# ✓ 创建角色: GM - 项目管理员
```

## 影响范围

### 不影响
- ✅ 角色代码 (GM) 保持不变
- ✅ 权限逻辑保持不变
- ✅ API接口保持不变
- ✅ 数据库关联保持不变

### 影响
- ✅ 用户界面显示的角色名称
- ✅ 文档中的角色描述
- ✅ 错误提示信息

## 相关文件

### 数据库脚本
- `backend/db/init_roles_and_admin.py` - 初始化脚本
- `backend/db/init_roles_and_admin.sql` - SQL初始化脚本
- `backend/db/update_gm_role_description.py` - 更新脚本（新增）

### 后端代码
- `backend/app/utils/jwt_tool.py` - JWT权限验证
- `backend/app/models/user.py` - 用户模型

### 前端代码
- `frontend/src/views/Dashboard/index.tsx` - 仪表盘
- `frontend/src/views/User/UserList.tsx` - 用户列表

### 文档
- `backend/README.md` - 后端文档
- `backend/db/README.md` - 数据库文档
- `docs/fixes/` - 修复记录

## 总结

✅ 数据库已更新
✅ 所有代码文件已修正
✅ 所有文档已修正
✅ 不影响现有功能
✅ 角色权限保持不变

GM角色现在正确地标识为"项目管理员"，更准确地反映了其在系统中的职责。
