# 🚀 用户角色管理 - 快速开始

## ⚡ 立即开始

### 1. 重启后端服务

```bash
# 停止当前服务（如果正在运行）
# 按 Ctrl+C

# 启动服务
cd backend
python start.py
```

### 2. 测试功能

```bash
# 运行自动化测试
python backend/test_user_role_management.py
```

### 3. 前端使用

1. 登录管理员账户：
   - 邮箱：`zhiyu`
   - 密码：`2201101122@qq.com`

2. 进入用户管理页面

3. 点击任意用户的"角色"按钮

4. 在弹窗中选择角色并保存

## 📌 关键变更

### 后端

- ✅ 新增：`backend/app/apis/v1/user/user_role.py` - 角色管理 API
- ✅ 修改：`backend/app/apis/v1/user/auth.py` - 注册时分配 MANUAL 角色
- ✅ 修改：`backend/app/apis/v1/user/__init__.py` - 注册路由

### 前端

- ✅ 修改：`frontend/src/api/user.ts` - 添加角色管理 API
- ✅ 修改：`frontend/src/views/User/UserList.tsx` - 添加角色管理界面

## 🎯 核心功能

1. **默认角色**：新用户注册自动获得 MANUAL 角色
2. **角色管理**：管理员可以为用户分配/移除角色
3. **权限控制**：只有 ADMIN 角色可以管理角色
4. **可视化**：用户列表显示彩色角色标签

## 📖 详细文档

查看完整文档：`backend/USER_ROLE_MANAGEMENT_SUMMARY.md`

## ⚠️ 注意事项

**必须重启后端服务才能使用新功能！**
