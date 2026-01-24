# 发送邮件菜单无法显示问题修复

## 问题描述
二级菜单"发送邮件"无法正常显示

## 问题分析

### 1. 路由配置检查
- ✅ 后端数据库中有"发送邮件"路由配置（`backend/db/init_routes.py`）
- ❌ 前端路由配置缺少 `mail/send` 路由
- ❌ 前端默认菜单配置缺少"发送邮件"菜单项

### 2. 根本原因
1. 前端 `frontend/src/router/index.tsx` 中没有导入和配置 `MailSend` 组件的路由
2. 前端 `frontend/src/components/Layout/index.tsx` 中的默认菜单配置（`DEFAULT_MENU_ITEMS`）缺少"发送邮件"菜单项
3. 管理员用户使用的是默认菜单配置，而不是从后端获取，所以即使后端有配置也不会显示

## 修复方案

### 1. 添加路由导入和配置
在 `frontend/src/router/index.tsx` 中：
```typescript
// 添加导入
import MailSend from '@/views/Mail/MailSend'

// 添加路由配置
{
  path: 'mail/send',
  element: <MailSend />,
},
```

### 2. 添加默认菜单项
在 `frontend/src/components/Layout/index.tsx` 中：
```typescript
{
  key: '/mail',
  icon: <MailOutlined />,
  label: '邮箱管理',
  children: [
    { key: '/mail/list', label: '邮箱列表' },
    { key: '/mail/viewer', label: '邮件查看器' },
    { key: '/mail/send', label: '发送邮件' },  // ✅ 新增
  ],
},
```

## 修复步骤

### 已完成 ✅
1. ✅ 在 `frontend/src/router/index.tsx` 中导入 `MailSend` 组件
2. ✅ 在路由配置中添加 `mail/send` 路由
3. ✅ 在默认菜单配置中添加"发送邮件"菜单项
4. ✅ 验证无TypeScript错误

### 需要用户操作
1. 刷新浏览器页面（Ctrl+Shift+R 或 Cmd+Shift+R）
2. 如果还是不显示，清除浏览器缓存后重新登录

## 验证步骤

### 1. 刷新页面
按 Ctrl+Shift+R (Windows/Linux) 或 Cmd+Shift+R (Mac) 强制刷新页面

### 2. 检查菜单
应该能看到邮箱管理菜单下有三个子菜单：
- 邮箱列表
- 邮件查看器
- 发送邮件 ✅

### 3. 测试功能
点击"发送邮件"菜单，应该能正常跳转到 `/mail/send` 页面

## 为什么会出现这个问题？

### 管理员用户的菜单加载逻辑
在 `frontend/src/components/Layout/index.tsx` 中：
```typescript
// 管理员用户直接使用默认菜单，不从后端获取
if (isAdmin) {
  console.log('管理员用户，使用默认完整菜单')
  setMenuItems(DEFAULT_MENU_ITEMS)  // 使用硬编码的默认菜单
  return
}

// 非管理员从后端获取路由权限
const routes = await getUserRoutes()
const items = buildMenuItems(routes)
setMenuItems(items)
```

这意味着：
- **管理员用户**：使用前端硬编码的 `DEFAULT_MENU_ITEMS`
- **普通用户**：从后端API获取路由权限

所以即使后端数据库中有"发送邮件"路由配置，管理员用户也看不到，因为前端的默认菜单配置中没有。

## 修复的文件

### 1. frontend/src/router/index.tsx
- 添加了 `MailSend` 组件的导入
- 添加了 `mail/send` 路由配置

### 2. frontend/src/components/Layout/index.tsx
- 在 `DEFAULT_MENU_ITEMS` 中添加了"发送邮件"菜单项

## 相关文件

- `frontend/src/router/index.tsx` - 前端路由配置
- `frontend/src/components/Layout/index.tsx` - 布局和菜单配置
- `frontend/src/views/Mail/MailSend.tsx` - 发送邮件组件
- `backend/db/init_routes.py` - 后端路由初始化脚本

## 总结

问题已修复！现在刷新页面后，应该能看到"发送邮件"菜单了。

**修复内容**：
1. ✅ 添加了前端路由配置
2. ✅ 添加了默认菜单项
3. ✅ 验证无错误

**下一步**：
- 刷新浏览器页面验证菜单是否显示
- 测试"发送邮件"功能是否正常工作
