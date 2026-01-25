# XUI 服务器同步功能增强 - 域名和 SSH 端口

## 问题描述

XUI 管理下的服务器列表同步功能会将入站信息同步到服务器管理下的服务器列表（`ServerInfo` 模型），但是：
1. ❌ 没有同步域名字段
2. ❌ 没有设置 SSH 端口默认值
3. ❌ 分组名称超长导致同步失败（ServerGroup.name 限制 20 字符）

## 修复内容

### 文件：`backend/app/crud/xui/operation.py`

在 `sync_inbounds_from_panel()` 方法中添加了域名、SSH 端口的同步逻辑，并修复了分组名称超长的问题。

### 修改前

```python
if remark:
    # 查找或创建 ServerGroup（使用 remark 作为分组名称）
    group = await ServerGroup.get_or_none(name=remark)
    
    if not group:
        # 创建新分组
        group = await ServerGroup.create(
            name=remark,  # ❌ 可能超过 20 字符限制
            country_id=default_country.id,
            status=1
        )
    
    if server_info:
        server_info.group_id = group.id
        server_info.status = 1 if enable else 2
        # ❌ 没有同步域名
        # ❌ 没有设置 SSH 端口
        await server_info.save()
    else:
        await ServerInfo.create(
            host=listen_host,
            port=port,
            # ❌ 没有 ssh_port
            # ❌ 没有 domain
            group_id=group.id,
            status=1 if enable else 2,
            is_sale=1
        )
```

### 修改后

```python
if remark:
    # 截断分组名称（ServerGroup.name 最大长度为 20）
    group_name = remark[:20] if len(remark) > 20 else remark  # ✅ 截断处理
    
    # 查找或创建 ServerGroup
    group = await ServerGroup.get_or_none(name=group_name)
    
    if not group:
        # 创建新分组
        group = await ServerGroup.create(
            name=group_name,  # ✅ 使用截断后的名称
            country_id=default_country.id,
            status=1
        )
    
    if server_info:
        server_info.group_id = group.id
        server_info.status = 1 if enable else 2
        # ✅ 同步域名
        if server.domain:
            server_info.domain = server.domain
        # ✅ 设置 SSH 端口默认值
        if not server_info.ssh_port:
            server_info.ssh_port = 9527
        await server_info.save()
    else:
        await ServerInfo.create(
            host=listen_host,
            port=port,
            ssh_port=9527,  # ✅ 默认 SSH 端口
            domain=server.domain,  # ✅ 同步域名
            group_id=group.id,
            status=1 if enable else 2,
            is_sale=1
        )
```

## 同步失败原因分析

### 问题：分组名称超长

**错误信息**：
```
同步 ServerInfo 失败 (port=32009): name: Length of '202.155.155.237-socks' 21 > 20
```

**原因**：
- `ServerGroup.name` 字段限制为 `max_length=20`
- 入站的 `remark` 可能超过 20 个字符（如 `202.155.155.237-socks` 有 21 个字符）
- 直接使用 remark 作为分组名称会导致数据库约束错误

**解决方案**：
- 对分组名称进行截断：`group_name = remark[:20]`
- 只保留前 20 个字符，确保不超过数据库限制
- 示例：`202.155.155.237-socks` → `202.155.155.237-soc`

## 同步逻辑说明

### 数据流向

```
XUI 服务器 (XuiServer)
    ↓
XUI 入站 (XuiInbound)
    ↓
服务器信息 (ServerInfo)
```

### 同步的字段

| 字段 | 来源 | 说明 |
|------|------|------|
| `host` | XuiInbound.listen_host | 服务器 IP 地址 |
| `port` | XuiInbound.listen_port | 代理端口 |
| `domain` | XuiServer.domain | 域名（新增） |
| `ssh_port` | 固定值 9527 | SSH 端口（新增） |
| `group_id` | 根据 remark 创建/查找 | 服务器分组 |
| `status` | XuiInbound.status | 状态（1=正常，2=异常） |
| `is_sale` | 固定值 1 | 是否可以出售 |

### 同步规则

1. **域名同步**：
   - 如果 XUI 服务器配置了域名，则同步到 ServerInfo
   - 更新时：如果 XUI 服务器有域名，则更新 ServerInfo 的域名
   - 创建时：直接使用 XUI 服务器的域名

2. **SSH 端口**：
   - 创建时：默认设置为 9527
   - 更新时：如果 ServerInfo 的 ssh_port 为空，则设置为 9527
   - 如果已有值，则不修改（保留用户自定义的值）

3. **端口过滤**：
   - 跳过 20000-21999 范围的端口
   - 跳过 30000-31999 范围的端口

4. **分组创建**：
   - 使用入站的 `remark` 作为分组名称
   - 如果分组不存在，自动创建
   - 如果没有国家，创建默认国家"未知"

## 使用方法

### 前端操作

1. 进入 **XUI 管理** → **服务器列表**
2. 点击某个服务器的 **同步** 按钮
3. 系统会自动：
   - 从 XUI 面板获取入站配置
   - 同步到 XuiInbound 表
   - 同步到 ServerInfo 表（包含域名和 SSH 端口）

### API 调用

```bash
POST /v1/xui/operation/sync-inbounds/{server_id}
```

### 返回示例

```json
{
  "success": true,
  "message": "同步完成: 创建 10 个入站，更新 90 个入站，跳过 0 个 | 服务器信息: 创建 5 个，更新 95 个",
  "data": {
    "inbound_created": 10,
    "inbound_updated": 90,
    "inbound_skipped": 0,
    "server_info_created": 5,
    "server_info_updated": 95,
    "errors": []
  }
}
```

## 日志示例

### 创建服务器信息

```
INFO - 创建服务器信息: 202.155.155.88:22000 -> 分组: 美国-洛杉矶, 域名: us-la.example.com
```

### 更新服务器信息

```
INFO - 更新服务器信息: 202.155.155.88:22001 -> 分组: 美国-洛杉矶, 域名: us-la.example.com
```

## 验证方法

### 1. 检查 XUI 服务器配置

```sql
SELECT id, name, host, domain, port FROM xui_server;
```

### 2. 执行同步操作

通过前端或 API 执行同步

### 3. 检查 ServerInfo 数据

```sql
SELECT host, port, domain, ssh_port, group_id, status 
FROM server_info 
WHERE host = '202.155.155.88';
```

应该看到：
- `domain` 字段已填充（如果 XUI 服务器有域名）
- `ssh_port` 字段为 9527

## 注意事项

1. **域名优先级**：
   - XUI 客户端连接时优先使用域名（如果有）
   - 如果没有域名，则使用 IP 地址

2. **SSH 端口保护**：
   - 更新时不会覆盖已有的 ssh_port 值
   - 只在 ssh_port 为空时设置默认值 9527

3. **分组管理**：
   - 分组名称来自入站的 remark 字段
   - 建议在 XUI 面板中为入站设置有意义的 remark

4. **端口过滤**：
   - 某些端口范围会被跳过，不会同步到 ServerInfo
   - 这些端口通常用于特殊用途

## 相关文件

- `backend/app/crud/xui/operation.py` - XUI 操作 CRUD（同步逻辑）
- `backend/app/models/xui.py` - XUI 模型定义
- `backend/app/models/server.py` - 服务器模型定义
- `frontend/src/views/Xui/XuiServerList.tsx` - XUI 服务器列表页面

## 完成时间

2026-01-25 23:08
