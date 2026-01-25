# XUI 操作日志和重试功能

## 功能概述

为了方便追踪 XUI 账号添加失败的情况并支持一键重试,我们实现了完整的操作日志系统。

## 数据库变更

### 1. 修改 user_logs 表
- 将 `user_id` 字段改为可空,支持记录系统操作日志
- SQL: `backend/db/update_user_log_nullable.sql`

### 2. 新增 xui_operation_logs 表

专门用于记录 XUI 操作的详细日志,包含以下字段:

```sql
CREATE TABLE `xui_operation_logs` (
    `id` CHAR(36) PRIMARY KEY,
    `operation_type` SMALLINT NOT NULL,  -- 操作类型
    `status` SMALLINT NOT NULL DEFAULT 4,  -- 操作状态
    `inbound_id` CHAR(36) NULL,  -- 入站 ID
    `account_id` CHAR(36) NULL,  -- 账号 ID
    `inbound_info` VARCHAR(255) NULL,  -- 入站信息(host:port)
    `account_username` VARCHAR(100) NULL,  -- 账号用户名
    `error_message` TEXT NULL,  -- 错误信息
    `retry_count` INT NOT NULL DEFAULT 0,  -- 重试次数
    `last_retry_time` DATETIME(6) NULL,  -- 最后重试时间
    `user_id` CHAR(36) NULL,  -- 操作用户
    `create_time` DATETIME(6) NOT NULL,
    `update_time` DATETIME(6) NOT NULL
)
```

## 枚举定义

### 操作类型 (XuiOperationType)
- `1` - ADD_ACCOUNT: 添加账号
- `2` - REMOVE_ACCOUNT: 移除账号
- `3` - BATCH_ADD: 批量添加
- `4` - SYNC_INBOUND: 同步入站

### 操作状态 (XuiOperationStatus)
- `1` - SUCCESS: 成功
- `2` - FAILED: 失败
- `3` - RETRYING: 重试中
- `4` - PENDING: 待处理

## 后端实现

### 模型 (backend/app/models/user.py)

新增 `XuiOperationLog` 模型:
- 记录每次 XUI 操作的详细信息
- 支持关联入站和账号
- 记录错误信息和重试次数
- 支持按状态、操作类型、入站等多维度查询

### CRUD 方法 (backend/app/crud/xui/user.py)

#### 1. add_account_to_inbound
- 添加账号时自动记录日志
- 成功记录 SUCCESS 状态
- 失败记录 FAILED 状态,包含详细错误信息

#### 2. batch_add_accounts
- 批量添加账号
- 记录每个账号的成功/失败状态
- 返回详细的成功和失败列表

#### 3. get_failed_logs
- 查询失败的操作日志
- 支持按入站ID、操作类型筛选
- 支持分页

#### 4. retry_failed_log
- 重试单个失败的操作
- 更新重试次数和时间
- 自动更新状态

#### 5. batch_retry_failed_logs
- 批量重试失败的操作
- 可指定入站ID,或重试所有失败操作
- 返回成功和失败统计

### API 端点 (backend/app/apis/v1/xui/user.py)

#### 1. POST /v1/xui/account/batch-add
批量添加账号到入站

**请求体:**
```json
{
  "inbound_id": "uuid",
  "account_ids": ["uuid1", "uuid2", ...]
}
```

**响应:**
```json
{
  "code": 200,
  "message": "批量添加完成: 成功 X 个, 失败 Y 个",
  "data": {
    "total": 10,
    "success": 8,
    "failed": 2,
    "success_list": [
      {"account_id": "uuid", "username": "user1"}
    ],
    "failed_list": [
      {"account_id": "uuid", "username": "user2", "error": "错误信息"}
    ]
  }
}
```

#### 2. GET /v1/xui/account/failed-logs
获取失败的操作日志

**查询参数:**
- `inbound_id`: 入站ID(可选)
- `operation_type`: 操作类型(可选)
- `page`: 页码
- `limit`: 每页数量
- `res_count`: 是否返回总数

**响应:**
```json
{
  "code": 200,
  "message": "成功",
  "count": 10,
  "num": 5,
  "data": [
    {
      "id": "uuid",
      "operation_type": 1,
      "status": 2,
      "inbound_id": "uuid",
      "account_id": "uuid",
      "inbound_info": "192.168.1.1:8080",
      "account_username": "user1",
      "error_message": "解密密码失败",
      "retry_count": 0,
      "last_retry_time": null,
      "create_time": "2026-01-25 12:00:00"
    }
  ]
}
```

#### 3. POST /v1/xui/account/retry-failed/{log_id}
重试单个失败的操作

**响应:**
```json
{
  "code": 200,
  "message": "重试成功",
  "data": {
    "success": true,
    "message": "重试成功",
    "result": {
      "username": "user1"
    }
  }
}
```

#### 4. POST /v1/xui/account/batch-retry-failed
批量重试失败的操作

**查询参数:**
- `inbound_id`: 入站ID(可选,不传则重试所有)

**响应:**
```json
{
  "code": 200,
  "message": "批量重试完成: 成功 X 个, 失败 Y 个",
  "data": {
    "total": 10,
    "success": 8,
    "failed": 2
  }
}
```

## 前端实现

### API 接口 (frontend/src/api/xui.ts)

新增以下接口:
- `getFailedLogs`: 获取失败的操作日志
- `retryFailedLog`: 重试单个失败的操作
- `batchRetryFailedLogs`: 批量重试失败的操作
- `batchAddAccountsToInbound`: 批量添加账号到入站

### 数据类型

```typescript
interface XuiOperationLog {
  id: string
  operation_type: number  // 1:添加账号 2:移除账号 3:批量添加 4:同步入站
  status: number  // 1:成功 2:失败 3:重试中 4:待处理
  inbound_id?: string
  account_id?: string
  inbound_info?: string
  account_username?: string
  error_message?: string
  retry_count: number
  last_retry_time?: string
  create_time: string
}
```

## 使用流程

### 1. 批量添加账号

```typescript
// 前端调用
const result = await batchAddAccountsToInbound(inboundId, accountIds)

// 查看结果
console.log(`成功: ${result.data.success}, 失败: ${result.data.failed}`)
console.log('失败列表:', result.data.failed_list)
```

### 2. 查看失败日志

```typescript
// 获取失败的操作日志
const logs = await getFailedLogs({
  inbound_id: inboundId,  // 可选,筛选特定入站
  operation_type: 1,  // 可选,筛选操作类型
  page: 1,
  limit: 10,
  res_count: true
})

// 显示失败日志列表
logs.data.forEach(log => {
  console.log(`${log.account_username}: ${log.error_message}`)
})
```

### 3. 重试失败的操作

```typescript
// 重试单个
const result = await retryFailedLog(logId)
if (result.data.success) {
  message.success('重试成功')
} else {
  message.error(result.data.message)
}

// 批量重试
const batchResult = await batchRetryFailedLogs(inboundId)
message.info(`批量重试完成: 成功 ${batchResult.data.success} 个`)
```

## 日志记录时机

### 添加账号 (add_account_to_inbound)
1. **解密密码失败** → 记录 FAILED 日志
2. **XUI 面板返回失败** → 记录 FAILED 日志
3. **其他异常** → 记录 FAILED 日志
4. **添加成功** → 记录 SUCCESS 日志

### 批量添加 (batch_add_accounts)
1. 每个账号的添加都会记录独立的日志
2. 批量操作本身也会记录一条汇总日志

### 重试操作 (retry_failed_log)
1. 开始重试 → 更新状态为 RETRYING,增加重试次数
2. 重试成功 → 更新状态为 SUCCESS,清空错误信息
3. 重试失败 → 更新状态为 FAILED,记录新的错误信息

## 数据库索引

为了提高查询性能,创建了以下索引:
- `idx_status_create_time`: 按状态和时间查询(查找失败的操作)
- `idx_operation_type_status`: 按操作类型和状态查询
- `idx_inbound_id_status`: 按入站查询
- `idx_account_id_status`: 按账号查询
- `idx_create_time`: 时间范围查询

## 优势

1. **完整的操作追踪**: 每次操作都有详细记录
2. **结构化数据**: 便于查询和统计
3. **一键重试**: 失败的操作可以轻松重试
4. **批量处理**: 支持批量添加和批量重试
5. **错误分析**: 详细的错误信息帮助定位问题
6. **重试统计**: 记录重试次数和时间

## 下一步

前端需要实现:
1. 失败日志列表页面
2. 批量添加账号功能
3. 一键重试按钮
4. 批量重试按钮
5. 错误信息展示

## 相关文件

### 后端
- `backend/app/models/user.py` - 日志模型定义
- `backend/app/crud/xui/user.py` - CRUD 方法
- `backend/app/apis/v1/xui/user.py` - API 端点
- `backend/db/create_xui_operation_logs.sql` - 建表 SQL
- `backend/db/apply_xui_operation_logs.py` - 迁移脚本

### 前端
- `frontend/src/api/xui.ts` - API 接口定义

### 数据库
- `xui_operation_logs` - 操作日志表
- `user_logs` - 用户日志表(user_id 改为可空)
