# 系统状态总结

## 最后更新时间
2026-01-22

## 系统架构
- **前端**: React + TypeScript + Ant Design (端口: 3000)
- **后端**: FastAPI + Python (端口: 6080)
- **数据库**: MySQL 主从复制 (主库: 3307, 从库: 3308/3309)
- **读写分离**: 已配置，读操作走从库，写操作走主库

## 已完成功能

### 1. RBAC权限管理系统 ✅
- 角色管理（ADMIN、GM、IT、MANUAL等）
- 路由权限管理（路由树、用户路由、角色路由）
- 动态菜单（根据用户角色显示不同菜单）
- 权限验证函数（`backend/app/core/verify.py`）

### 2. 数据权限（行级权限）✅
- ADMIN和GM可以查看所有数据
- 其他角色只能查看自己关联的项目数据
- 实现函数：
  - `check_data_permission()` - 返回None（全部权限）或user_id（仅自己的数据）
  - `check_project_access()` - 检查用户是否可以访问指定项目

### 3. CRUD权限控制 ✅
- **删除权限**: ADMIN可以删除所有，其他角色只能删除自己关联的项目数据
- **创建权限**: ADMIN可以创建任意项目，其他角色只能为自己关联的项目创建
- **查询权限**: ADMIN可以查询所有，其他角色只能查询自己关联的项目
- **修改权限**: ADMIN可以修改所有，其他角色只能修改自己关联的项目

### 4. 批量操作功能 ✅
已在以下页面实现批量选择和批量删除：
- 项目账号列表
- 项目列表
- 用户列表
- 项目钱包列表
- 服务器列表
- 邮箱列表

特性：
- 批量选择（复选框）
- 批量删除（带确认对话框）
- 翻页后保持选中状态

### 5. 列排序功能 ✅
已在以下页面实现列排序：
- 项目账号列表（余额、变动、更新时间）
- 项目列表（创建时间、更新时间）
- 用户列表（创建时间、更新时间）
- 项目钱包列表（链、创建时间）

特性：
- 点击列标题排序
- 升序/降序切换
- 默认排序设置

### 6. 复制ID功能 ✅
已在以下页面实现：
- 项目列表（显示缩略ID：前8位...后8位）
- 项目账号列表（复制按钮）
- 用户列表（复制按钮）

### 7. 项目钱包功能 ✅
- 所有用户都可以创建钱包（移除权限限制）
- 添加公钥查询条件
- 后端支持公钥模糊查询
- 编辑和删除功能仍然只对ADMIN和GM开放

### 8. API 404错误静默处理 ✅
在API拦截器中添加所有列表查询接口的404静默处理：
- 项目信息、项目账号、项目钱包
- 用户列表、用户Token
- 邮箱列表
- 服务器列表、服务器分组、服务器账号、国家列表

查询无数据时不显示错误提示，静默显示空列表。

### 9. 项目账号特殊优化 ✅
- 显示更新时间而不是创建时间
- 默认按更新时间倒序排列
- 余额历史记录（最近7天）
- 变动余额显示（正数绿色，负数红色）

## 管理员账号
- 邮箱: `zhiyu`
- 密码: `2201101122@qq.com`

## 进程状态
- 后端进程: ProcessId 20 (running)
- 前端进程: ProcessId 8 (running)

## 测试脚本
- `test_crud_permission_simple.sh` - CRUD权限测试
- `test_data_permission.sh` - 数据权限测试
- `test_delete_permission.sh` - 删除权限测试

## 关键文件路径

### 后端
- 权限验证: `backend/app/core/verify.py`
- 数据库配置: `backend/app/core/database.py`
- 项目API: `backend/app/apis/v1/project/`
- 用户API: `backend/app/apis/v1/user/`

### 前端
- API拦截器: `frontend/src/api/index.ts`
- 项目账号页面: `frontend/src/views/Project/ProjectAccount.tsx`
- 项目钱包页面: `frontend/src/views/Project/ProjectWallet.tsx`
- 权限管理页面: `frontend/src/views/User/PermissionManageWorking.tsx`

## 最近修复
- ✅ 修复了所有前端API函数的TypeScript类型定义问题
- ✅ 为所有列表查询API添加了完整的参数类型（包括时间范围查询参数）
- ✅ 修复了角色列表和邮箱列表的TypeScript类型错误
- ✅ 移除了未使用的dayjs导入
- ✅ 验证了17个组件文件，全部通过TypeScript类型检查

详细修复记录请查看：`TYPESCRIPT_TYPE_FIX_SUMMARY.md`

## 注意事项
1. 后端没有查到数据就是要抛出404状态码，不要改变这个行为
2. 前端在404的情况下静默处理，不显示错误提示
3. 权限管理在`core/verify.py`中统一管理
4. 数据库和后端在同一台服务器（127.0.0.1）
