# 路由测试清单

## 已添加的 XUI 路由

### App.tsx 中的路由配置

```tsx
<Route path="xui/server" element={<XuiServerList />} />
<Route path="xui/inbound" element={<XuiInboundList />} />
<Route path="xui/account" element={<XuiAccountManage />} />
```

### Layout 中的菜单配置

```tsx
{
  key: '/xui',
  icon: <CloudServerOutlined />,
  label: 'XUI管理',
  children: [
    { key: '/xui/server', label: '服务器列表' },
    { key: '/xui/inbound', label: '入站列表' },
    { key: '/xui/account', label: '账号管理' },
  ],
}
```

## 测试步骤

1. ✅ 确认 App.tsx 中已添加路由
2. ✅ 确认 Layout 中已添加菜单
3. ✅ 确认组件文件已创建
4. ⏳ 重启前端开发服务器
5. ⏳ 清除浏览器缓存
6. ⏳ 测试访问路由

## 可能的问题

### 问题 1: 前端未重新编译

**解决方案**:
```bash
# 停止前端服务
# Ctrl+C

# 重新启动
cd frontend
npm run dev
```

### 问题 2: 浏览器缓存

**解决方案**:
- 硬刷新: Cmd+Shift+R (Mac) 或 Ctrl+Shift+R (Windows)
- 或清除浏览器缓存

### 问题 3: 组件导入路径错误

**检查**:
- XuiServerList 组件路径: `./views/Xui/XuiServerList`
- XuiInboundList 组件路径: `./views/Xui/XuiInboundList`
- XuiAccountManage 组件路径: `./views/Xui/XuiAccountManage`

## 直接访问测试

尝试直接在浏览器地址栏访问:
- http://localhost:5173/xui/server
- http://localhost:5173/xui/inbound
- http://localhost:5173/xui/account

如果直接访问可以，说明路由配置正确，问题在菜单点击事件。
如果直接访问也不行，说明路由配置有问题。
