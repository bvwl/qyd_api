# 删除项目余额菜单项

## 更新时间
2026-01-21

## 背景

项目余额功能已经完全集成到项目账号页面中，不再需要独立的余额页面和菜单项。

## 修改内容

### 1. 删除菜单项

**文件**: `frontend/src/components/Layout/index.tsx`

**修改前**:
```tsx
{
  key: '/project',
  icon: <ProjectOutlined />,
  label: '项目管理',
  children: [
    { key: '/project/list', label: '项目列表' },
    { key: '/project/account', label: '项目账号' },
    { key: '/project/wallet', label: '项目钱包' },
    { key: '/project/balance', label: '项目余额' },  // ← 删除这一行
  ],
},
```

**修改后**:
```tsx
{
  key: '/project',
  icon: <ProjectOutlined />,
  label: '项目管理',
  children: [
    { key: '/project/list', label: '项目列表' },
    { key: '/project/account', label: '项目账号' },
    { key: '/project/wallet', label: '项目钱包' },
  ],
},
```

### 2. 已删除的相关文件

- ✅ `frontend/src/views/Project/ProjectBalance.tsx` - 余额页面组件
- ✅ `frontend/src/App.tsx` 中的余额路由配置
- ✅ `backend/app/apis/v1/project/balance.py` - 余额 API
- ✅ `backend/app/crud/project/balance.py` - 余额 CRUD
- ✅ `backend/app/schemas/project/balance.py` - 余额 Schema
- ✅ `backend/app/models/project.py` 中的 `ProjectBalance` 模型

### 3. 余额功能现在的位置

余额功能已经完全集成到 **项目账号** 页面中：

- 余额列：显示当前余额
- 变动列：显示变动余额（带颜色）
- 历史按钮：查看最近7天的余额历史

## 菜单结构

### 修改前

```
项目管理
├── 项目列表
├── 项目账号
├── 项目钱包
└── 项目余额  ← 删除
```

### 修改后

```
项目管理
├── 项目列表
├── 项目账号  ← 包含余额功能
└── 项目钱包
```

## 用户影响

### 对用户的影响

1. **菜单简化**: 项目管理菜单从4个子项减少到3个子项
2. **功能不变**: 所有余额功能都在项目账号页面中可用
3. **体验提升**: 账号和余额信息在同一页面，无需切换

### 迁移指南

如果用户之前使用 **项目余额** 菜单：

1. 现在请使用 **项目账号** 菜单
2. 在项目账号页面中可以看到：
   - 余额列（显示当前余额）
   - 变动列（显示变动余额）
   - 历史按钮（查看历史余额）

## 优势

### 1. 菜单更简洁

- ✅ 减少了一个菜单项
- ✅ 项目管理菜单更清晰
- ✅ 避免功能重复

### 2. 功能更集中

- ✅ 账号和余额信息在同一页面
- ✅ 无需切换页面查看余额
- ✅ 操作更便捷

### 3. 维护更简单

- ✅ 减少了一个页面组件
- ✅ 减少了路由配置
- ✅ 代码更简洁

## 相关文档

- ✅ `docs/fixes/MERGE_BALANCE_INTO_ACCOUNT.md` - 合并余额表到账号表
- ✅ `docs/fixes/BALANCE_AUTO_CALCULATION.md` - 余额自动计算逻辑
- ✅ `docs/fixes/FRONTEND_ACCOUNT_WITH_BALANCE.md` - 前端账号页面集成余额功能
- ✅ `docs/fixes/PROJECT_ACCOUNT_BALANCE_ENHANCEMENT.md` - 项目账号余额功能增强
- ✅ `docs/fixes/REMOVE_PROJECT_BALANCE_MENU.md` - 本文档

## 测试清单

- [ ] 项目管理菜单不再显示"项目余额"
- [ ] 点击"项目账号"菜单正常跳转
- [ ] 项目账号页面显示余额和变动列
- [ ] 历史按钮功能正常
- [ ] 没有控制台错误
- [ ] 路由正常工作

## 总结

✅ 删除了项目余额菜单项
✅ 余额功能完全集成到项目账号页面
✅ 菜单结构更简洁
✅ 用户体验更好
✅ 代码维护更简单

现在用户可以在项目账号页面中直接查看和管理余额，无需单独的余额页面！
