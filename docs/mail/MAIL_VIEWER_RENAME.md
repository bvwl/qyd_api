# 邮件查看器重命名为邮件查看

## 修改时间
2026-01-25

## 修改内容

将二级菜单"邮件查看器"改为"邮件查看"

## 修改的文件

### 1. 前端默认菜单配置
**文件**: `frontend/src/components/Layout/index.tsx`

**修改前**:
```typescript
{ key: '/mail/viewer', label: '邮件查看器' },
```

**修改后**:
```typescript
{ key: '/mail/viewer', label: '邮件查看' },
```

### 2. 后端路由初始化脚本
**文件**: `backend/db/init_routes.py`

**修改前**:
```python
{
    "name": "mail-viewer",
    "path": "/mail/viewer",
    "title": "邮件查看器",
    "component": "MailViewer",
    "sort": 2,
},
```

**修改后**:
```python
{
    "name": "mail-viewer",
    "path": "/mail/viewer",
    "title": "邮件查看",
    "component": "MailViewer",
    "sort": 2,
},
```

## 生效方式

### 管理员用户
- **立即生效**：刷新页面即可看到新名称
- 管理员使用前端默认菜单，修改前端配置后立即生效

### 普通用户
- **需要更新数据库**：需要运行初始化脚本更新数据库中的路由标题
- 普通用户从后端获取路由，需要更新数据库数据

## 更新数据库（可选）

如果需要让普通用户也看到新名称，运行以下命令：

```bash
cd backend
python db/init_routes.py
```

**注意**：这会重新初始化所有路由，如果你手动修改过其他路由，可能会被覆盖。

### 或者手动更新数据库

```sql
UPDATE frontend_route 
SET title = '邮件查看' 
WHERE name = 'mail-viewer';
```

## 验证

刷新浏览器页面后，邮箱管理菜单下应该显示：
- 邮箱列表
- 邮件查看 ✅ (原来是"邮件查看器")
- 发送邮件

## 相关文件

- `frontend/src/components/Layout/index.tsx` - 前端默认菜单配置
- `backend/db/init_routes.py` - 后端路由初始化脚本
