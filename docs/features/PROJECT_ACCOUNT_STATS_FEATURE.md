# 项目账号统计功能实现

## 功能概述

在项目账号管理页面添加统计功能，根据筛选条件计算项目账号的余额和变动数据。

## 实现内容

### 1. 后端实现

#### 1.1 API 路由

**文件**: `backend/app/apis/v1/project/account.py`

新增统计接口：
```
GET /v1/project/account/stats
```

**查询参数**:
- `project_id` (必填): 项目ID
- `account` (可选): 账号筛选
- `status` (可选): 状态筛选
- `account_type` (可选): 账号类型筛选
- `create_time_start` (可选): 创建时间开始
- `create_time_end` (可选): 创建时间结束
- `update_time_start` (可选): 更新时间开始
- `update_time_end` (可选): 更新时间结束

**权限控制**:
- ADMIN/GM: 可以统计所有项目
- IT/MANUAL: 只能统计分配给自己的项目

**响应格式**:
```json
{
  "code": 1,
  "message": "成功",
  "data": {
    "total_count": 100,
    "balance": {
      "max": 1000.50,
      "min": 10.00,
      "avg": 500.25,
      "sum": 50025.00
    },
    "variable": {
      "max": 100.00,
      "min": -50.00,
      "avg": 25.50,
      "sum": 2550.00
    }
  }
}
```

#### 1.2 CRUD 方法

**文件**: `backend/app/crud/project/account.py`

新增 `get_stats()` 方法：
- 使用 Tortoise ORM 的聚合函数（Max, Min, Avg, Sum）
- 一次查询获取所有统计数据，避免多次数据库访问
- 支持所有筛选条件
- 返回字典格式的统计数据

**关键实现**:
```python
from tortoise.functions import Max, Min, Avg, Sum

stats = await query.annotate(
    max_balance=Max('balance'),
    min_balance=Min('balance'),
    avg_balance=Avg('balance'),
    sum_balance=Sum('balance'),
    max_variable=Max('variable'),
    min_variable=Min('variable'),
    avg_variable=Avg('variable'),
    sum_variable=Sum('variable'),
).values(...)
```

#### 1.3 Schema 定义

**文件**: `backend/app/schemas/project/account.py`

新增 Pydantic 模型：
- `BalanceStats`: 余额统计（最高分、最低分、平均分、总分）
- `VariableStats`: 变动统计（变动最高分、最低分、平均分、总分）
- `StatsData`: 统计数据（包含总数、余额统计、变动统计）
- `StatsOut`: 统计输出（包含状态码、消息、数据）

### 2. 前端实现

**文件**: `frontend/src/views/Project/ProjectAccount.tsx`

#### 2.1 统计按钮

在搜索表单旁边添加"统计"按钮：
```tsx
<Button type="primary" onClick={handleStats}>
  统计
</Button>
```

#### 2.2 统计弹窗

使用 Ant Design Modal 显示统计结果：
- 标题：项目账号统计
- 内容：表格展示统计数据
- 两列布局：指标名称 + 数值
- 数值保留2位小数

**统计指标**:
1. 统计账号数量
2. 当前最高分
3. 当前最低分
4. 当前平均分
5. 当前总分
6. 变动最高分
7. 变动最低分
8. 变动平均分
9. 变动总分

#### 2.3 API 调用

**文件**: `frontend/src/api/project.ts`

新增 API 方法：
```typescript
export const getProjectAccountStats = (params: any) => {
  return api.get<any, any>('/v1/project/account/stats', { params })
}
```

## 技术要点

### 1. 路由顺序问题

**重要**: FastAPI 路由匹配是按顺序的，必须将特定路径放在动态路径之前。

```python
# ✅ 正确：特定路径在前
@app.get("/stats", ...)  # 先匹配
@app.get("/{id}", ...)   # 后匹配

# ❌ 错误：动态路径会拦截所有请求
@app.get("/{id}", ...)   # 这个会拦截 /stats
@app.get("/stats", ...)  # 永远不会被执行
```

### 2. Tortoise ORM 聚合查询

使用 `.values()` 方法获取聚合结果：
```python
# ✅ 正确
stats = await query.annotate(...).values(...)
# stats 是一个列表，取第一个元素
result = stats[0]

# ❌ 错误
stats = await query.annotate(...).first().values(...)
# .first() 返回模型实例，没有 .values() 方法
```

### 3. 权限控制

使用数据权限工具过滤项目：
```python
from app.utils.data_permission import filter_by_user_projects

user_project_ids = await filter_by_user_projects(user_id)

if user_project_ids is not None:
    # 非全局权限，检查是否有权限访问该项目
    if str(project_id) not in user_project_ids:
        raise HTTPException(status_code=403, detail="没有权限访问该项目")
```

### 4. Decimal 转 Float

统计结果需要转换为 float 类型：
```python
from decimal import Decimal

def decimal_to_float(value):
    if value is None:
        return 0.0
    return float(Decimal(str(value)))
```

## 测试步骤

1. 启动后端服务：
   ```bash
   cd backend
   python start.py
   ```

2. 启动前端服务：
   ```bash
   cd frontend
   npm run dev
   ```

3. 访问项目账号页面：
   ```
   http://localhost:3000/project/account
   ```

4. 测试统计功能：
   - 选择项目
   - 点击"统计"按钮
   - 查看统计结果弹窗

5. 测试权限控制：
   - 使用 IT/MANUAL 角色登录
   - 尝试统计未分配的项目（应该返回403错误）

## 注意事项

1. **性能优化**: 使用数据库聚合函数，一次查询获取所有统计数据，避免在应用层循环计算
2. **数据精度**: 余额使用 Decimal 类型，保留6位小数；统计结果转换为 float 类型
3. **权限控制**: 非 ADMIN/GM 用户只能统计自己有权限的项目
4. **筛选条件**: 统计功能支持所有列表页面的筛选条件
5. **空数据处理**: 如果没有数据，返回默认值（0）

## 相关文件

### 后端
- `backend/app/apis/v1/project/account.py` - API 路由
- `backend/app/crud/project/account.py` - CRUD 方法
- `backend/app/schemas/project/account.py` - Schema 定义

### 前端
- `frontend/src/views/Project/ProjectAccount.tsx` - 页面组件
- `frontend/src/api/project.ts` - API 调用

## 完成状态

✅ 后端 API 实现
✅ 后端 CRUD 方法
✅ 后端 Schema 定义
✅ 前端统计按钮
✅ 前端统计弹窗
✅ 前端 API 调用
✅ 权限控制
✅ 路由顺序修复
✅ Tortoise ORM 聚合查询修复

## 下一步

功能已完成，可以进行测试验证。
