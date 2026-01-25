# XUI 入站同步功能 - 端口过滤与服务器信息同步

## 功能概述

从 XUI 面板同步入站配置到数据库时：
1. 自动过滤特定端口范围，避免导入不需要的入站配置
2. 同步入站信息到 `ServerInfo` 模型
3. 使用入站的 `remark` 作为 `ServerGroup` 名称
4. 自动创建或更新服务器分组和服务器信息

## 服务器信息同步

### 同步逻辑

同步入站配置时，会自动同步到 `ServerInfo` 模型：

1. **提取分组名称**：使用入站的 `remark` 字段作为 `ServerGroup` 名称
2. **查找或创建分组**：
   - 如果分组不存在，自动创建新分组
   - 如果没有国家信息，创建默认国家（UN - 未知）
3. **查找或创建服务器信息**：
   - 使用 `listen_host` 和 `listen_port` 作为唯一标识
   - 如果 `ServerInfo` 已存在，更新分组关联
   - 如果不存在，创建新的 `ServerInfo` 记录

### 数据模型关系

```
ServerCountry (国家)
    ↓
ServerGroup (分组) - 使用入站的 remark 作为名称
    ↓
ServerInfo (服务器信息) - 使用入站的 host:port
```

### 字段映射

| XUI 入站字段 | ServerInfo 字段 | 说明 |
|-------------|----------------|------|
| `remark` | `group.name` | 分组名称 |
| `listen_host` | `host` | 服务器地址 |
| `listen_port` | `port` | 代理端口 |
| `enable` | `status` | 状态（1:正常, 2:异常） |
| - | `is_sale` | 默认为 1（是） |

### 示例

假设 XUI 面板有以下入站：

```json
{
  "listen": "192.168.1.1",
  "port": 22000,
  "protocol": "http",
  "remark": "HK-Premium",
  "enable": true
}
```

同步后会创建：

1. **ServerGroup**:
   - `name`: "HK-Premium"
   - `country_id`: 默认国家 ID

2. **ServerInfo**:
   - `host`: "192.168.1.1"
   - `port`: 22000
   - `group_id`: HK-Premium 分组 ID
   - `status`: 1（正常）
   - `is_sale`: 1（是）

## 端口过滤规则

同步入站配置时，以下端口范围将被**自动跳过**，不会导入到数据库：

- **20000 - 21999**：跳过此范围内的所有端口
- **30000 - 31999**：跳过此范围内的所有端口

### 示例

| 端口  | 是否导入 | 说明 |
|------|---------|------|
| 19999 | ✅ 导入 | 不在过滤范围 |
| 20000 | ❌ 跳过 | 在 20000-21999 范围 |
| 20500 | ❌ 跳过 | 在 20000-21999 范围 |
| 21999 | ❌ 跳过 | 在 20000-21999 范围 |
| 22000 | ✅ 导入 | 不在过滤范围 |
| 29999 | ✅ 导入 | 不在过滤范围 |
| 30000 | ❌ 跳过 | 在 30000-31999 范围 |
| 30500 | ❌ 跳过 | 在 30000-31999 范围 |
| 31999 | ❌ 跳过 | 在 30000-31999 范围 |
| 32000 | ✅ 导入 | 不在过滤范围 |

## 实现细节

### 修改文件

`backend/app/crud/xui/operation.py` - `sync_inbounds_from_panel` 方法

### 核心代码

```python
for inbound_data in inbounds_data:
    try:
        # 提取端口信息
        port = inbound_data.get('port')
        
        # 端口过滤规则：跳过 20000-21999 和 30000-31999 范围的端口
        if (20000 <= port <= 21999) or (30000 <= port <= 31999):
            logger.info(f'跳过端口 {port}（在过滤范围内）')
            skipped_count += 1
            continue
        
        # 继续处理其他端口...
```

### 过滤逻辑

1. **提取端口**：从 XUI 面板返回的入站数据中提取端口号
2. **范围检查**：检查端口是否在过滤范围内
3. **跳过处理**：如果在过滤范围内，记录日志并跳过
4. **统计计数**：将跳过的入站计入 `inbound_skipped`

### 同步 ServerInfo 逻辑

1. **检查 remark**：只有当入站有 `remark` 时才同步到 ServerInfo
2. **查找分组**：根据 `remark` 查找 `ServerGroup`
3. **创建分组**：如果分组不存在，自动创建（需要关联国家）
4. **创建/更新 ServerInfo**：根据 `host:port` 创建或更新服务器信息
5. **错误处理**：ServerInfo 同步失败不影响入站同步

## API 使用

### 同步入站配置

```bash
POST /v1/xui/operation/sync-inbounds/{server_id}
```

**请求示例**：

```bash
curl -X POST 'http://127.0.0.1:6080/v1/xui/operation/sync-inbounds/{server_id}' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json'
```

**响应示例**：

```json
{
  "success": true,
  "message": "同步完成: 创建 5 个入站，更新 3 个入站，跳过 12 个 | 服务器信息: 创建 4 个，更新 2 个",
  "data": {
    "inbound_created": 5,
    "inbound_updated": 3,
    "inbound_skipped": 12,
    "server_info_created": 4,
    "server_info_updated": 2,
    "errors": []
  }
}
```

### 响应字段说明

- `inbound_created`: 新创建的入站数量
- `inbound_updated`: 更新的入站数量
- `inbound_skipped`: 跳过的入站数量（包含端口过滤和其他原因）
- `server_info_created`: 新创建的 ServerInfo 数量
- `server_info_updated`: 更新的 ServerInfo 数量
- `errors`: 错误列表

## 日志记录

同步过程中会记录详细的日志信息：

```
INFO: 跳过端口 20500（在过滤范围内）
INFO: 跳过端口 30800（在过滤范围内）
INFO: 创建入站: 192.168.1.1:22000
INFO: 更新入站: 192.168.1.1:25000
INFO: 创建服务器分组: HK-Premium
INFO: 创建服务器信息: 192.168.1.1:22000 -> 分组: HK-Premium
INFO: 更新服务器信息: 192.168.1.1:25000 -> 分组: US-Standard
```

## 测试

### 运行测试脚本

```bash
cd backend
python test_xui_sync.py
```

### 测试内容

1. **端口过滤逻辑测试**：验证各种端口是否正确过滤
2. **同步功能测试**：实际从 XUI 面板同步入站配置
3. **结果验证**：检查数据库中是否存在被过滤范围内的端口

### 预期输出

```
============================================================
测试端口过滤逻辑
============================================================

端口过滤测试:
   端口 19999: ✅ 导入
   端口 20000: ❌ 跳过
   端口 20500: ❌ 跳过
   端口 21999: ❌ 跳过
   端口 22000: ✅ 导入
   端口 29999: ✅ 导入
   端口 30000: ❌ 跳过
   端口 30500: ❌ 跳过
   端口 31999: ❌ 跳过
   端口 32000: ✅ 导入

============================================================
测试 XUI 入站同步功能（端口过滤）
============================================================

📡 服务器信息:
   ID: xxx-xxx-xxx
   名称: HK-004
   地址: sd7.0n.lv:10010

🔄 开始同步入站配置...
   端口过滤规则:
   - 跳过 20000-21999 范围
   - 跳过 30000-31999 范围

📊 同步结果:
   成功: True
   消息: 同步完成: 创建 5 个入站，更新 3 个入站，跳过 12 个 | 服务器信息: 创建 4 个，更新 2 个

📈 详细统计:
   入站 - 创建: 5 个
   入站 - 更新: 3 个
   入站 - 跳过: 12 个
   服务器信息 - 创建: 4 个
   服务器信息 - 更新: 2 个

📋 数据库中的入站列表 (共 8 个):
   - 192.168.1.1:22000 [HTTP] [正常] HK-Premium
   - 192.168.1.1:25000 [SOCKS] [正常] US-Standard
   ...

✅ 端口过滤验证:
   ✅ 所有端口都不在过滤范围内

📋 ServerInfo 列表 (共 8 个):
   - 192.168.1.1:22000 [分组: HK-Premium] [正常]
   - 192.168.1.1:25000 [分组: US-Standard] [正常]
   ...

📋 ServerGroup 列表 (共 3 个):
   - HK-Premium (国家: 未知)
   - US-Standard (国家: 未知)
   - SG-Basic (国家: 未知)

✅ 测试完成！
```

## 使用场景

### 场景 1：初次同步

首次从 XUI 面板同步入站配置时：
- 自动过滤不需要的端口范围
- 根据入站的 `remark` 创建服务器分组
- 创建对应的 `ServerInfo` 记录

```bash
# 同步服务器的入站配置
POST /v1/xui/operation/sync-inbounds/{server_id}
```

### 场景 2：定期同步

定期同步以保持数据库与 XUI 面板的一致性：
- 过滤规则始终生效
- 更新已存在的入站和服务器信息
- 自动关联新的分组

### 场景 3：批量服务器同步

对多个服务器进行同步时：
- 每个服务器都会应用相同的过滤规则
- 每个服务器的入站会同步到各自的 `ServerInfo`
- 分组名称相同的会共享同一个 `ServerGroup`

## 注意事项

1. **过滤范围固定**：端口过滤范围是硬编码的，如需修改需要更新代码
2. **跳过计数**：被过滤的端口会计入 `inbound_skipped`
3. **日志记录**：所有跳过的端口和同步操作都会记录到日志中
4. **不影响现有数据**：过滤只影响新同步的数据，不会删除数据库中已存在的入站
5. **其他跳过原因**：除了端口过滤，未知协议类型的入站也会被跳过
6. **remark 必需**：只有当入站有 `remark` 时才会同步到 `ServerInfo`
7. **默认国家**：如果没有国家信息，会自动创建默认国家（UN - 未知）
8. **分组唯一性**：`ServerGroup` 的 `name` 是唯一的，相同名称会共享同一个分组
9. **ServerInfo 唯一性**：使用 `host:port` 作为唯一标识
10. **错误隔离**：`ServerInfo` 同步失败不会影响入站同步

## 修改过滤规则

如需修改端口过滤范围，编辑 `backend/app/crud/xui/operation.py`：

```python
# 修改这一行来调整过滤范围
if (20000 <= port <= 21999) or (30000 <= port <= 31999):
    # 例如：添加新的过滤范围
    # if (20000 <= port <= 21999) or (30000 <= port <= 31999) or (40000 <= port <= 41999):
```

## 相关文件

- `backend/app/crud/xui/operation.py` - 同步逻辑实现
- `backend/app/apis/v1/xui/operation.py` - API 接口
- `backend/app/models/xui.py` - XUI 模型定义
- `backend/app/models/server.py` - Server 模型定义
- `backend/test_xui_sync.py` - 测试脚本
- `backend/app/utils/logs.py` - 日志工具

## 数据库表关系

```sql
-- 国家表
server_country (id, short_name, name, status)

-- 分组表（关联国家）
server_group (id, name, country_id, status)

-- 服务器信息表（关联分组）
server_info (id, host, port, group_id, status, is_sale)

-- XUI 服务器表
xui_server (id, name, host, domain, port, ...)

-- XUI 入站表（关联 XUI 服务器）
xui_inbound (id, server_id, listen_host, listen_port, remark, ...)
```

## 完成状态

✅ 端口过滤逻辑已实现
✅ 支持 20000-21999 范围过滤
✅ 支持 30000-31999 范围过滤
✅ ServerInfo 同步已实现
✅ ServerGroup 自动创建
✅ 默认国家自动创建
✅ 日志记录完整
✅ 测试脚本已更新
✅ 文档已完善

## 下一步

1. 运行测试脚本验证功能
2. 在实际环境中测试同步功能
3. 根据需要调整过滤范围
4. 考虑将过滤规则配置化（可选）
