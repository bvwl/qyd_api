# XUI 账号管理功能完成

## 功能概述

新增 XUI 账号管理页面,显示所有服务器账号,支持一键添加到所有 XUI 入站或从所有入站删除。

## 实现的功能

### 1. 数据库更新

#### ServerAccount 模型新增字段
- **字段名**: `is_all_inbound_added`
- **类型**: `TINYINT(1)` (Boolean)
- **默认值**: `0` (False)
- **索引**: 是
- **说明**: 标记账号是否已添加到所有 XUI 入站

#### 数据库迁移
```sql
ALTER TABLE `proxy_account` 
ADD COLUMN `is_all_inbound_added` TINYINT(1) NOT NULL DEFAULT 0 
COMMENT '是否已添加到所有入站(用于XUI管理)' AFTER `password`,
ADD INDEX `idx_is_all_inbound_added` (`is_all_inbound_added`);
```

### 2. 后端实现

#### 模型更新 (`backend/app/models/server.py`)
```python
class ServerAccount(BaseModel):
    username = fields.CharField(max_length=36, index=True, description='用户名')
    password = fields.TextField(description='密码（加密存储）')
    is_all_inbound_added = fields.BooleanField(
        default=False, 
        index=True, 
        description='是否已添加到所有入站(用于XUI管理)'
    )
    # ...
```

#### CRUD 新增方法 (`backend/app/crud/xui/user.py`)

**1. 添加到所有入站**
```python
async def add_account_to_all_inbounds(self, account_id: UUID) -> Dict[str, Any]:
    """将账号添加到所有入站"""
    # 1. 获取账号
    # 2. 获取所有入站
    # 3. 逐个添加到入站
    # 4. 如果全部成功,更新 is_all_inbound_added = True
    # 5. 返回详细结果
```

**2. 从所有入站删除**
```python
async def remove_account_from_all_inbounds(self, account_id: UUID) -> Dict[str, Any]:
    """从所有入站删除账号"""
    # 1. 获取账号
    # 2. 获取所有入站
    # 3. 逐个从入站删除
    # 4. 如果全部成功,更新 is_all_inbound_added = False
    # 5. 返回详细结果
```

**返回数据结构**:
```json
{
  "total": 10,           // 总入站数
  "success": 9,          // 成功数
  "failed": 1,           // 失败数
  "failed_list": [       // 失败详情
    {
      "inbound_id": "xxx",
      "inbound_info": "host:port",
      "error": "错误信息"
    }
  ],
  "is_all_added": false,    // 是否全部添加成功
  "is_all_removed": false   // 是否全部删除成功
}
```

#### API 新增端点 (`backend/app/apis/v1/xui/user.py`)
- **添加**: `POST /v1/xui/account/add-to-all-inbounds/{account_id}`
- **删除**: `DELETE /v1/xui/account/remove-from-all-inbounds/{account_id}`
- **权限**: ADMIN
- **说明**: 批量添加或删除账号与所有入站的关联

### 3. 前端实现

#### 新页面 (`frontend/src/views/Xui/XuiAccountList.tsx`)

**功能特性**:
1. ✅ 显示所有服务器账号列表
2. ✅ 显示账号的入站添加状态(已全部添加/未全部添加)
3. ✅ 支持一键添加到所有入站
4. ✅ 支持一键从所有入站删除
5. ✅ 添加/删除过程中显示 loading 状态
6. ✅ 操作完成后显示详细结果
7. ✅ 分页、刷新功能

**表格列**:
- 用户名
- 用户 ID
- 入站状态 (Tag 显示)
- 创建时间
- 更新时间
- 操作按钮

**状态标签**:
- ✅ 已全部添加: 绿色 Tag + CheckCircleOutlined 图标
- ⭕ 未全部添加: 灰色 Tag + CloseCircleOutlined 图标

**操作按钮**:
- 未全部添加: 显示"添加到所有入站"按钮(蓝色,PlusOutlined 图标)
- 已全部添加: 显示"从所有入站删除"按钮(红色,MinusOutlined 图标)

#### API 更新 (`frontend/src/api/xui.ts`)
```typescript
// 将账号添加到所有入站
export const addAccountToAllInbounds = (accountId: string) => {
  return api.post(`/v1/xui/account/add-to-all-inbounds/${accountId}`)
}

// 从所有入站删除账号
export const removeAccountFromAllInbounds = (accountId: string) => {
  return api.delete(`/v1/xui/account/remove-from-all-inbounds/${accountId}`)
}
```

#### 类型更新 (`frontend/src/types/index.ts`)
```typescript
export interface ServerAccount {
  id: string
  username: string
  password: string
  user_id: string
  user?: User
  is_all_inbound_added: boolean  // 新增字段
  create_time: string
  update_time: string
}
```

#### 路由更新
- `frontend/src/router/index.tsx`: 更新 `xui/account` 路由使用 `XuiAccountList`
- `frontend/src/App.tsx`: 更新路由配置

### 4. 业务逻辑

#### 添加流程
1. 用户点击"添加到所有入站"按钮
2. 前端调用 API: `POST /v1/xui/account/add-to-all-inbounds/{account_id}`
3. 后端获取所有入站列表
4. 逐个调用 `add_account_to_inbound` 方法
5. 记录成功和失败的入站
6. 如果全部成功,更新 `is_all_inbound_added = True`
7. 返回详细结果给前端
8. 前端显示结果消息并刷新列表

#### 删除流程
1. 用户点击"从所有入站删除"按钮
2. 前端调用 API: `DELETE /v1/xui/account/remove-from-all-inbounds/{account_id}`
3. 后端获取所有入站列表
4. 逐个调用 `remove_account_from_inbound` 方法
5. 记录成功和失败的入站
6. 如果全部成功,更新 `is_all_inbound_added = False`
7. 返回详细结果给前端
8. 前端显示结果消息并刷新列表

#### 失败处理
- 添加失败会自动记录到 `xui_operation_logs` 表
- 可以在"操作日志"页面查看失败原因
- 支持重试失败的操作

#### 状态更新
- 只有当账号成功添加到**所有**入站时,`is_all_inbound_added` 才会设置为 `True`
- 只有当账号成功从**所有**入站删除时,`is_all_inbound_added` 才会设置为 `False`
- 如果有任何一个入站操作失败,状态保持不变
- 用户可以重新点击按钮重试

## 使用流程

### 1. 查看账号列表
1. 进入"XUI 管理" -> "账号管理"
2. 查看所有服务器账号
3. 查看每个账号的入站添加状态

### 2. 添加账号到所有入站
1. 找到状态为"未全部添加"的账号
2. 点击"添加到所有入站"按钮
3. 确认操作
4. 等待添加完成
5. 查看结果消息

### 3. 从所有入站删除账号
1. 找到状态为"已全部添加"的账号
2. 点击"从所有入站删除"按钮
3. 确认操作
4. 等待删除完成
5. 查看结果消息

### 4. 处理失败情况
1. 如果部分入站操作失败,会显示警告消息
2. 进入"操作日志"页面查看失败详情
3. 可以使用"重试"功能重新添加
4. 或者重新点击操作按钮

## API 端点

### 添加到所有入站
```
POST /v1/xui/account/add-to-all-inbounds/{account_id}
```

**权限**: ADMIN

**路径参数**:
- `account_id`: 账号 ID (UUID)

**响应**:
```json
{
  "code": 200,
  "message": "批量添加完成: 成功 9 个, 失败 1 个",
  "data": {
    "total": 10,
    "success": 9,
    "failed": 1,
    "failed_list": [
      {
        "inbound_id": "xxx",
        "inbound_info": "192.168.1.1:1080",
        "error": "连接超时"
      }
    ],
    "is_all_added": false
  }
}
```

### 从所有入站删除
```
DELETE /v1/xui/account/remove-from-all-inbounds/{account_id}
```

**权限**: ADMIN

**路径参数**:
- `account_id`: 账号 ID (UUID)

**响应**:
```json
{
  "code": 200,
  "message": "批量删除完成: 成功 10 个, 失败 0 个",
  "data": {
    "total": 10,
    "success": 10,
    "failed": 0,
    "failed_list": [],
    "is_all_removed": true
  }
}
```

## 文件清单

### 后端文件
```
backend/
├── app/
│   ├── models/server.py                    # ServerAccount 模型更新
│   ├── crud/xui/user.py                    # 新增添加和删除方法
│   └── apis/v1/xui/user.py                 # 新增 API 端点
└── db/
    ├── add_is_all_inbound_added_field.sql  # 数据库迁移 SQL
    └── apply_is_all_inbound_added.py       # 迁移执行脚本
```

### 前端文件
```
frontend/src/
├── views/Xui/XuiAccountList.tsx            # 新页面(支持添加和删除)
├── api/xui.ts                              # API 更新
├── types/index.ts                          # 类型更新
├── router/index.tsx                        # 路由更新
└── App.tsx                                 # 路由更新
```

## 技术细节

### 并发处理
- 逐个添加/删除入站,不使用并发
- 避免同时大量请求 XUI 面板
- 保证操作的可靠性

### 错误处理
- 每个入站操作失败都会记录到日志
- 不会因为一个失败而中断整个流程
- 返回详细的失败列表

### 状态管理
- 使用 `is_all_inbound_added` 字段标记状态
- 只有全部成功才更新状态
- 前端根据状态显示不同的按钮

### 性能优化
- 使用索引加速查询
- 分页显示账号列表
- 操作过程显示 loading 状态

## UI 设计

### 按钮样式
- **添加按钮**: 
  - 类型: `primary` (蓝色)
  - 图标: `PlusOutlined`
  - 文字: "添加到所有入站"
  
- **删除按钮**:
  - 类型: `danger` (红色)
  - 图标: `MinusOutlined`
  - 文字: "从所有入站删除"

### 状态标签
- **已全部添加**:
  - 颜色: `success` (绿色)
  - 图标: `CheckCircleOutlined`
  
- **未全部添加**:
  - 颜色: `default` (灰色)
  - 图标: `CloseCircleOutlined`

### 确认对话框
- 添加操作: "添加到所有入站？" + "将此账号添加到所有 XUI 入站"
- 删除操作: "从所有入站删除？" + "将此账号从所有 XUI 入站删除"

## 注意事项

1. **权限要求**: 只有 ADMIN 用户可以执行添加和删除操作
2. **网络要求**: 需要能够连接到所有 XUI 服务器
3. **时间消耗**: 如果入站数量多,操作过程可能需要一些时间
4. **失败重试**: 失败的操作会记录到日志,可以在操作日志页面重试
5. **状态更新**: 状态只在全部成功时更新,部分成功不会更新
6. **删除确认**: 删除操作使用红色按钮,需要二次确认

## 测试建议

1. ✅ 测试添加到所有入站功能
2. ✅ 测试从所有入站删除功能
3. ✅ 测试部分入站操作失败的情况
4. ✅ 测试状态标签显示
5. ✅ 测试按钮切换(添加后显示删除按钮)
6. ✅ 测试权限控制
7. ✅ 测试分页功能
8. ✅ 测试刷新功能

## 后续优化建议

1. 添加批量操作(选择多个账号批量添加/删除)
2. 添加进度条显示操作进度
3. 添加筛选功能(按状态筛选)
4. 添加搜索功能(按用户名搜索)
5. 添加导出功能(导出账号列表)
6. 添加操作历史记录

## 总结

XUI 账号管理功能已完成,主要特性:
- ✅ 显示所有服务器账号
- ✅ 显示入站添加状态
- ✅ 一键添加到所有入站
- ✅ 一键从所有入站删除
- ✅ 详细的结果反馈
- ✅ 失败日志记录
- ✅ 权限控制
- ✅ 响应式 UI
- ✅ 状态自动更新

系统现在可以方便地管理服务器账号与 XUI 入站的关联关系,支持完整的添加和删除操作,大大提高了运维效率。

## 实现的功能

### 1. 数据库更新

#### ServerAccount 模型新增字段
- **字段名**: `is_all_inbound_added`
- **类型**: `TINYINT(1)` (Boolean)
- **默认值**: `0` (False)
- **索引**: 是
- **说明**: 标记账号是否已添加到所有 XUI 入站

#### 数据库迁移
```sql
ALTER TABLE `proxy_account` 
ADD COLUMN `is_all_inbound_added` TINYINT(1) NOT NULL DEFAULT 0 
COMMENT '是否已添加到所有入站(用于XUI管理)' AFTER `password`,
ADD INDEX `idx_is_all_inbound_added` (`is_all_inbound_added`);
```

### 2. 后端实现

#### 模型更新 (`backend/app/models/server.py`)
```python
class ServerAccount(BaseModel):
    username = fields.CharField(max_length=36, index=True, description='用户名')
    password = fields.TextField(description='密码（加密存储）')
    is_all_inbound_added = fields.BooleanField(
        default=False, 
        index=True, 
        description='是否已添加到所有入站(用于XUI管理)'
    )
    # ...
```

#### CRUD 新增方法 (`backend/app/crud/xui/user.py`)
```python
async def add_account_to_all_inbounds(self, account_id: UUID) -> Dict[str, Any]:
    """将账号添加到所有入站"""
    # 1. 获取账号
    # 2. 获取所有入站
    # 3. 逐个添加到入站
    # 4. 如果全部成功,更新 is_all_inbound_added = True
    # 5. 返回详细结果
```

**返回数据结构**:
```json
{
  "total": 10,           // 总入站数
  "success": 9,          // 成功添加数
  "failed": 1,           // 失败数
  "failed_list": [       // 失败详情
    {
      "inbound_id": "xxx",
      "inbound_info": "host:port",
      "error": "错误信息"
    }
  ],
  "is_all_added": false  // 是否全部添加成功
}
```

#### API 新增端点 (`backend/app/apis/v1/xui/user.py`)
- **路径**: `POST /v1/xui/account/add-to-all-inbounds/{account_id}`
- **权限**: ADMIN
- **说明**: 将指定账号添加到所有 XUI 入站

### 3. 前端实现

#### 新页面 (`frontend/src/views/Xui/XuiAccountList.tsx`)

**功能特性**:
1. ✅ 显示所有服务器账号列表
2. ✅ 显示账号的入站添加状态(已全部添加/未全部添加)
3. ✅ 支持一键添加到所有入站
4. ✅ 添加过程中显示 loading 状态
5. ✅ 添加完成后显示详细结果
6. ✅ 分页、刷新功能

**表格列**:
- 用户名
- 用户 ID
- 入站状态 (Tag 显示)
- 创建时间
- 更新时间
- 操作按钮

**状态标签**:
- ✅ 已全部添加: 绿色 Tag + CheckCircleOutlined 图标
- ⭕ 未全部添加: 灰色 Tag + CloseCircleOutlined 图标

**操作按钮**:
- 未全部添加: 显示"添加到所有入站"按钮
- 已全部添加: 显示"已添加" Tag

#### API 更新 (`frontend/src/api/xui.ts`)
```typescript
// 将账号添加到所有入站
export const addAccountToAllInbounds = (accountId: string) => {
  return api.post<any, {
    code: number
    message: string
    data: {
      total: number
      success: number
      failed: number
      failed_list: Array<{ inbound_id: string; inbound_info: string; error: string }>
      is_all_added: boolean
    }
  }>(`/v1/xui/account/add-to-all-inbounds/${accountId}`)
}
```

#### 类型更新 (`frontend/src/types/index.ts`)
```typescript
export interface ServerAccount {
  id: string
  username: string
  password: string
  user_id: string
  user?: User
  is_all_inbound_added: boolean  // 新增字段
  create_time: string
  update_time: string
}
```

#### 路由更新
- `frontend/src/router/index.tsx`: 更新 `xui/account` 路由使用 `XuiAccountList`
- `frontend/src/App.tsx`: 更新路由配置

### 4. 业务逻辑

#### 添加流程
1. 用户点击"添加到所有入站"按钮
2. 前端调用 API: `POST /v1/xui/account/add-to-all-inbounds/{account_id}`
3. 后端获取所有入站列表
4. 逐个调用 `add_account_to_inbound` 方法
5. 记录成功和失败的入站
6. 如果全部成功,更新 `is_all_inbound_added = True`
7. 返回详细结果给前端
8. 前端显示结果消息并刷新列表

#### 失败处理
- 添加失败会自动记录到 `xui_operation_logs` 表
- 可以在"操作日志"页面查看失败原因
- 支持重试失败的操作

#### 状态更新
- 只有当账号成功添加到**所有**入站时,`is_all_inbound_added` 才会设置为 `True`
- 如果有任何一个入站添加失败,状态保持为 `False`
- 用户可以重新点击按钮重试

## 使用流程

### 1. 查看账号列表
1. 进入"XUI 管理" -> "账号管理"
2. 查看所有服务器账号
3. 查看每个账号的入站添加状态

### 2. 添加账号到所有入站
1. 找到状态为"未全部添加"的账号
2. 点击"添加到所有入站"按钮
3. 确认操作
4. 等待添加完成
5. 查看结果消息

### 3. 处理失败情况
1. 如果部分入站添加失败,会显示警告消息
2. 进入"操作日志"页面查看失败详情
3. 可以使用"重试"功能重新添加
4. 或者重新点击"添加到所有入站"按钮

## API 端点

### 添加到所有入站
```
POST /v1/xui/account/add-to-all-inbounds/{account_id}
```

**权限**: ADMIN

**路径参数**:
- `account_id`: 账号 ID (UUID)

**响应**:
```json
{
  "code": 200,
  "message": "批量添加完成: 成功 9 个, 失败 1 个",
  "data": {
    "total": 10,
    "success": 9,
    "failed": 1,
    "failed_list": [
      {
        "inbound_id": "xxx",
        "inbound_info": "192.168.1.1:1080",
        "error": "连接超时"
      }
    ],
    "is_all_added": false
  }
}
```

## 文件清单

### 后端文件
```
backend/
├── app/
│   ├── models/server.py                    # ServerAccount 模型更新
│   ├── crud/xui/user.py                    # 新增 add_account_to_all_inbounds 方法
│   └── apis/v1/xui/user.py                 # 新增 API 端点
└── db/
    ├── add_is_all_inbound_added_field.sql  # 数据库迁移 SQL
    └── apply_is_all_inbound_added.py       # 迁移执行脚本
```

### 前端文件
```
frontend/src/
├── views/Xui/XuiAccountList.tsx            # 新页面
├── api/xui.ts                              # API 更新
├── types/index.ts                          # 类型更新
├── router/index.tsx                        # 路由更新
└── App.tsx                                 # 路由更新
```

## 技术细节

### 并发处理
- 逐个添加到入站,不使用并发
- 避免同时大量请求 XUI 面板
- 保证操作的可靠性

### 错误处理
- 每个入站添加失败都会记录到日志
- 不会因为一个失败而中断整个流程
- 返回详细的失败列表

### 状态管理
- 使用 `is_all_inbound_added` 字段标记状态
- 只有全部成功才更新为 `True`
- 前端根据状态显示不同的 UI

### 性能优化
- 使用索引加速查询
- 分页显示账号列表
- 添加过程显示 loading 状态

## 注意事项

1. **权限要求**: 只有 ADMIN 用户可以执行添加操作
2. **网络要求**: 需要能够连接到所有 XUI 服务器
3. **时间消耗**: 如果入站数量多,添加过程可能需要一些时间
4. **失败重试**: 失败的操作会记录到日志,可以在操作日志页面重试
5. **状态更新**: 状态只在全部成功时更新,部分成功不会更新

## 测试建议

1. ✅ 测试添加到所有入站功能
2. ✅ 测试部分入站添加失败的情况
3. ✅ 测试状态标签显示
4. ✅ 测试权限控制
5. ✅ 测试分页功能
6. ✅ 测试刷新功能

## 后续优化建议

1. 添加批量操作(选择多个账号批量添加)
2. 添加进度条显示添加进度
3. 添加筛选功能(按状态筛选)
4. 添加搜索功能(按用户名搜索)
5. 添加导出功能(导出账号列表)

## 总结

XUI 账号管理功能已完成,主要特性:
- ✅ 显示所有服务器账号
- ✅ 显示入站添加状态
- ✅ 一键添加到所有入站
- ✅ 详细的结果反馈
- ✅ 失败日志记录
- ✅ 权限控制
- ✅ 响应式 UI

系统现在可以方便地管理服务器账号与 XUI 入站的关联关系,大大提高了运维效率。
