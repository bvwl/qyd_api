# XUI 同步功能修复 - 使用服务器名称作为分组

## 问题描述

XUI 服务器同步功能原本使用入站的 `remark` 作为服务器分组名称，但这导致了以下问题：

1. ❌ 分组名称不统一（每个入站的 remark 可能不同）
2. ❌ 分组名称可能超过 20 字符限制
3. ❌ 不符合业务逻辑（应该按 XUI 服务器分组，而不是按入站）

## 正确的逻辑

服务器分组应该使用 **XUI 服务器的名称**（`XuiServer.name`），而不是入站的 remark。

### 数据关系

```
XUI 服务器 (XuiServer)
  ├── name: "sd7"  ← 用作服务器分组名称
  ├── domain: "sd7.0n.lv"
  └── 入站列表 (XuiInbound)
      ├── 入站1: remark="202.155.155.88-http"
      ├── 入站2: remark="202.155.155.88-socks"
      └── ...

同步后 ↓

服务器分组 (ServerGroup)
  └── name: "sd7"  ← 来自 XuiServer.name

服务器信息 (ServerInfo)
  ├── 服务器1: host=202.155.155.88, port=22000, group="sd7"
  ├── 服务器2: host=202.155.155.88, port=32000, group="sd7"
  └── ...
```

## 修复内容

### 文件：`backend/app/crud/xui/operation.py`

#### 修改前（错误）

```python
# 使用入站的 remark 作为分组名称
if remark:
    group_name = remark[:20]  # ❌ 每个入站的 remark 不同
    group = await ServerGroup.get_or_none(name=group_name)
    # ...
```

**问题**：
- 同一个 XUI 服务器的不同入站会创建不同的分组
- 例如：`202.155.155.88-http` 和 `202.155.155.88-socks` 会创建两个分组
- 不符合业务逻辑

#### 修改后（正确）

```python
# 使用 XUI 服务器名称作为分组名称
group_name = server.name[:20]  # ✅ 所有入站使用同一个分组
group = await ServerGroup.get_or_none(name=group_name)
# ...
```

**优点**：
- 同一个 XUI 服务器的所有入站使用同一个分组
- 分组名称有意义（如 "sd7"）
- 符合业务逻辑

## 完整修改

```python
async def sync_inbounds_from_panel(self, server_id: UUID) -> XuiOperationResponse:
    """
    从 XUI 面板同步入站配置到数据库
    
    同时同步到 ServerInfo 模型：
    - 使用 XUI 服务器的名称作为 ServerGroup 名称  ← 修改点
    - 创建或更新 ServerInfo 记录
    """
    # 获取服务器信息
    server = await XuiServer.get_or_none(id=server_id)
    
    # ... 处理入站 ...
    
    # 同步到 ServerInfo 模型
    try:
        # 使用 XUI 服务器名称作为分组名称（截断到 20 字符）
        group_name = server.name[:20] if len(server.name) > 20 else server.name
        
        # 查找或创建 ServerGroup
        group = await ServerGroup.get_or_none(name=group_name)
        
        if not group:
            # 创建新分组
            group = await ServerGroup.create(
                name=group_name,
                country_id=default_country.id,
                status=1
            )
            logger.info(f'创建服务器分组: {group_name}')
        
        # 创建或更新 ServerInfo
        # ...
    except Exception as e:
        logger.error(f'同步 ServerInfo 失败: {str(e)}')
```

## 同步效果

### 修改前

```
XUI 服务器: sd7
  ├── 入站1: remark="202.155.155.88-http"  → 分组: "202.155.155.88-htt"
  ├── 入站2: remark="202.155.155.88-socks" → 分组: "202.155.155.88-soc"
  └── 入站3: remark="202.155.155.237-http" → 分组: "202.155.155.237-htt"

结果：创建了 3 个不同的分组 ❌
```

### 修改后

```
XUI 服务器: sd7
  ├── 入站1: remark="202.155.155.88-http"  → 分组: "sd7"
  ├── 入站2: remark="202.155.155.88-socks" → 分组: "sd7"
  └── 入站3: remark="202.155.155.237-http" → 分组: "sd7"

结果：所有入站使用同一个分组 "sd7" ✅
```

## 同步的字段

| 字段 | 来源 | 说明 |
|------|------|------|
| `host` | XuiInbound.listen_host | 服务器 IP 地址 |
| `port` | XuiInbound.listen_port | 代理端口 |
| `domain` | XuiServer.domain | 域名 |
| `ssh_port` | 固定值 9527 | SSH 端口 |
| `group_id` | XuiServer.name | **服务器分组（修改点）** |
| `status` | XuiInbound.status | 状态 |
| `is_sale` | 固定值 1 | 是否可以出售 |

## 日志示例

### 创建分组

```
INFO - 创建服务器分组: sd7
```

### 同步服务器信息

```
INFO - 创建服务器信息: 202.155.155.88:22000 -> 分组: sd7, 域名: sd7.0n.lv
INFO - 创建服务器信息: 202.155.155.88:32000 -> 分组: sd7, 域名: sd7.0n.lv
INFO - 更新服务器信息: 202.155.155.88:22001 -> 分组: sd7, 域名: sd7.0n.lv
```

## 验证方法

### 1. 查看 XUI 服务器配置

```sql
SELECT id, name, host, domain FROM xui_server;
```

示例结果：
```
id   | name | host            | domain
-----|------|-----------------|------------
xxx  | sd7  | 202.155.155.88  | sd7.0n.lv
```

### 2. 执行同步操作

通过前端 XUI 管理 → 服务器列表 → 点击"同步"按钮

### 3. 查看服务器分组

```sql
SELECT id, name FROM server_group WHERE name = 'sd7';
```

应该只有一个分组

### 4. 查看服务器信息

```sql
SELECT host, port, domain, ssh_port, group_id 
FROM server_info 
WHERE host = '202.155.155.88'
LIMIT 5;
```

所有记录的 `group_id` 应该相同（都指向 "sd7" 分组）

## 注意事项

1. **分组名称来源**：
   - 使用 `XuiServer.name` 字段
   - 自动截断到 20 字符（如果超长）

2. **分组唯一性**：
   - 同一个 XUI 服务器的所有入站使用同一个分组
   - 不同 XUI 服务器使用不同分组

3. **向后兼容**：
   - 旧的分组不会自动删除
   - 重新同步后会使用新的分组逻辑

## 相关文件

- `backend/app/crud/xui/operation.py` - XUI 操作 CRUD（同步逻辑）
- `backend/app/models/xui.py` - XUI 模型定义
- `backend/app/models/server.py` - 服务器模型定义
- `XUI_SYNC_DOMAIN_SSH_PORT.md` - 域名和 SSH 端口同步文档

## 完成时间

2026-01-25 23:17
