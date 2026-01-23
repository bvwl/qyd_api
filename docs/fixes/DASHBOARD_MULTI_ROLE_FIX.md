# 仪表盘多角色显示修复

## 问题
仪表盘只显示用户的一个角色（优先级最高的角色），但用户可能拥有多个角色。

## 修复内容

### 文件: `frontend/src/views/Dashboard/index.tsx`

#### 修改前
```tsx
<p style={{ margin: '8px 0 0', color: '#666' }}>
  当前角色：<Tag color="blue">{ROLE_NAME_MAP[stats.role] || stats.role}</Tag>
  邮箱：{stats.user_email}
</p>
```

只显示一个角色标签。

#### 修改后
```tsx
<p style={{ margin: '8px 0 0', color: '#666' }}>
  当前角色：
  {userInfo?.roles && userInfo.roles.length > 0 ? (
    userInfo.roles.map((role) => (
      <Tag key={role.code} color="blue" style={{ marginLeft: 4 }}>
        {ROLE_NAME_MAP[role.code] || role.name}
      </Tag>
    ))
  ) : (
    <Tag color="blue">{ROLE_NAME_MAP[stats.role] || stats.role}</Tag>
  )}
  <span style={{ marginLeft: 16 }}>邮箱：{stats.user_email}</span>
</p>
```

现在会显示所有角色标签。

## 显示效果

### 修改前
```
当前角色：[技术人员] 邮箱：2201101122@qq.com
```

### 修改后
```
当前角色：[管理员] [技术人员] 邮箱：2201101122@qq.com
```

## 技术细节

### 数据来源
- 从 `useUserStore` 获取 `userInfo.roles` 数组
- 每个角色包含 `code` 和 `name` 字段

### 角色映射
```typescript
const ROLE_NAME_MAP: Record<string, string> = {
  ADMIN: '管理员',
  GM: '项目管理员',
  IT: '技术人员',
  MANUAL: '手动操作员',
}
```

### 降级处理
如果 `userInfo.roles` 不存在或为空，则显示 `stats.role`（主要角色）作为后备。

## 相关功能

虽然显示所有角色，但系统仍然使用"主要角色"（优先级最高的角色）来决定：
- 显示哪些统计数据
- 显示哪些项目
- 显示哪些功能

角色优先级：
1. ADMIN（管理员）- 最高
2. GM（项目管理员）
3. IT（技术人员）
4. MANUAL（手动操作员）- 最低

## 测试

1. 使用拥有多个角色的用户登录
2. 访问仪表盘页面
3. 验证所有角色都显示在"当前角色"行

## 注意事项

- 角色标签按照 `userInfo.roles` 数组的顺序显示
- 每个角色标签都有 4px 的左边距，保持视觉间隔
- 邮箱信息移到角色标签后面，增加 16px 左边距

---

**修复时间**: 2026-01-23  
**修复状态**: ✅ 完成
