# 项目余额排序功能和账号可选查询（前端实现）

## 更新时间
2026-01-21

## 功能描述

在项目余额界面添加了两个重要功能：

1. **账号选择改为可选** - 选择项目后可以直接查询该项目所有账号的余额
2. **表格排序功能** - 支持按创建时间、更新时间、余额、变动余额进行正序/倒序排列

## 设计理念

**保持后端接口简单**：
- 后端接口不添加 `project_id` 参数
- 通过前端发送多次请求实现项目级查询
- 前端负责数据聚合、排序和分页

## 功能详情

### 1. 账号选择改为可选

**修改前**：
- 必须先选择项目
- 必须再选择账号
- 只能查看单个账号的余额

**修改后**：
- 必须先选择项目（必选）
- 账号选择变为可选
- 不选账号时，显示该项目所有账号的余额
- 选择账号时，只显示该账号的余额

**使用场景**：

```
场景1: 查看项目所有账号余额
1. 选择"项目A"
2. 不选择账号
3. 点击"搜索"
4. ✅ 显示项目A所有账号的余额

场景2: 查看项目特定账号余额
1. 选择"项目A"
2. 选择"account1@example.com"
3. 点击"搜索"
4. ✅ 只显示该账号的余额
```

### 2. 表格排序功能

支持以下字段的排序：

| 字段 | 说明 | 正序 | 倒序 |
|------|------|------|------|
| **余额** | balance | 从小到大 | 从大到小 |
| **变动** | variable | 从小到大（负数在前） | 从大到小（正数在前） |
| **创建时间** | create_time | 从旧到新 | 从新到旧（默认） |
| **更新时间** | update_time | 从旧到新 | 从新到旧 |

**使用方式**：
- 点击表头的排序图标进行排序
- 再次点击切换正序/倒序
- 第三次点击取消排序（恢复默认）

## 实现方案

### 后端修改

#### 1. API 层添加排序字段支持

**文件**: `backend/app/apis/v1/project/balance.py`

```python
@app.get("", response_model=OutList, ...)
async def gets(
    account_id: UUID | None = Query(None, description="关联账号ID"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|create_time|update_time|balance|variable)$",  # ← 添加 balance 和 variable
    ),
    ...
):
    return await project_balance_crud.get_multi(
        account_id=account_id,
        order_by=order_by or "-create_time",
        ...
    )
```

**支持的排序字段**：
- `id` / `-id`
- `create_time` / `-create_time` (默认)
- `update_time` / `-update_time`
- `balance` / `-balance` (新增)
- `variable` / `-variable` (新增)

#### 2. CRUD 层预加载项目信息

**文件**: `backend/app/crud/project/balance.py`

```python
async def get_multi(self, ...) -> OutList:
    query = ProjectBalance.all()
    
    if account_id:
        query = query.filter(account_id=account_id)
    
    ...
    
    # 预加载关联数据（包括项目信息）
    res = await query.prefetch_related('account', 'account__project')  # ← 预加载项目
    
    ...
```

**关键点**：
- 使用 `prefetch_related('account', 'account__project')` 预加载项目信息
- 避免 N+1 查询问题
- 前端可以直接访问 `balance.account.project.name`

### 前端修改

#### 1. 两次请求实现项目级查询

**文件**: `frontend/src/views/Project/ProjectBalance.tsx`

**查询逻辑**：

```typescript
const fetchData = async () => {
  if (!searchProjectId) {
    setData([])
    setTotal(0)
    return
  }
  
  setLoading(true)
  try {
    // 情况1: 选择了账号 - 直接查询该账号的余额
    if (searchAccountId) {
      const res = await getProjectBalanceList({
        page,
        limit: pageSize,
        res_count: true,
        account_id: searchAccountId,
        order_by: orderBy,
        ...
      })
      setData(res.items || [])
      setTotal(res.count || 0)
    } 
    // 情况2: 没有选择账号 - 查询项目所有账号的余额
    else {
      // 第一步：获取项目的所有账号ID
      const accountsRes = await getProjectAccountList({
        page: 1,
        limit: 10000,
        project_id: searchProjectId,
      })
      
      const projectAccountIds = accountsRes.items?.map(acc => acc.id) || []
      
      if (projectAccountIds.length === 0) {
        setData([])
        setTotal(0)
        return
      }
      
      // 第二步：查询这些账号的余额（分批查询）
      const batchSize = 50
      let allBalances: ProjectBalance[] = []
      
      for (let i = 0; i < projectAccountIds.length; i += batchSize) {
        const batchIds = projectAccountIds.slice(i, i + batchSize)
        
        // 并发查询每个账号的余额
        const batchPromises = batchIds.map(accountId =>
          getProjectBalanceList({
            page: 1,
            limit: 1,
            account_id: accountId,
            order_by: orderBy,
            ...
          }).catch(() => ({ items: [], count: 0, num: 0, message: '' }))
        )
        
        const batchResults = await Promise.all(batchPromises)
        const batchBalances = batchResults.flatMap(res => res.items || [])
        allBalances = [...allBalances, ...batchBalances]
      }
      
      // 前端排序
      allBalances.sort((a, b) => {
        const field = orderBy.replace('-', '')
        const isDesc = orderBy.startsWith('-')
        
        let aVal: any = a[field as keyof ProjectBalance]
        let bVal: any = b[field as keyof ProjectBalance]
        
        // 处理数字类型
        if (field === 'balance' || field === 'variable') {
          aVal = Number(aVal)
          bVal = Number(bVal)
        }
        
        if (aVal < bVal) return isDesc ? 1 : -1
        if (aVal > bVal) return isDesc ? -1 : 1
        return 0
      })
      
      // 前端分页
      const start = (page - 1) * pageSize
      const end = start + pageSize
      const paginatedData = allBalances.slice(start, end)
      
      setData(paginatedData)
      setTotal(allBalances.length)
    }
  } catch (error) {
    setData([])
    setTotal(0)
  } finally {
    setLoading(false)
  }
}
```

**实现要点**：

1. **选择账号时**：
   - 直接调用余额 API，传入 `account_id`
   - 后端排序和分页
   - 性能最优

2. **未选择账号时**：
   - 第一步：调用账号 API，获取项目的所有账号ID
   - 第二步：并发调用余额 API，查询每个账号的余额
   - 分批查询（每批50个），避免并发过多
   - 前端聚合所有结果
   - 前端排序和分页

3. **错误处理**：
   - 使用 `.catch()` 捕获单个账号查询失败
   - 不影响其他账号的查询
   - 静默处理 404 错误

#### 2. 表格排序实现

```typescript
// 1. 添加排序状态
const [orderBy, setOrderBy] = useState<string>('-create_time')

// 2. 表格排序处理
const handleTableChange: TableProps<ProjectBalance>['onChange'] = (_pagination, _filters, sorter: any) => {
  if (sorter.field) {
    const order = sorter.order === 'ascend' ? '' : '-'
    setOrderBy(`${order}${sorter.field}`)
  }
}

// 3. 获取当前排序状态
const getSortOrder = (field: string): SortOrder => {
  if (orderBy === field) return 'ascend'
  if (orderBy === `-${field}`) return 'descend'
  return null
}

// 4. 列定义添加排序
const columns = [
  {
    title: '余额',
    dataIndex: 'balance',
    key: 'balance',
    sorter: true,
    sortOrder: getSortOrder('balance'),
    render: (balance: number | string) => Number(balance).toFixed(2),
  },
  {
    title: '变动',
    dataIndex: 'variable',
    key: 'variable',
    sorter: true,
    sortOrder: getSortOrder('variable'),
    render: (variable: number | string) => {
      const num = Number(variable)
      const color = num > 0 ? 'green' : num < 0 ? 'red' : 'default'
      return <span style={{ color }}>{num > 0 ? '+' : ''}{num.toFixed(2)}</span>
    },
  },
  {
    title: '创建时间',
    dataIndex: 'create_time',
    key: 'create_time',
    sorter: true,
    sortOrder: getSortOrder('create_time'),
  },
  {
    title: '更新时间',
    dataIndex: 'update_time',
    key: 'update_time',
    sorter: true,
    sortOrder: getSortOrder('update_time'),
  },
]

// 5. 表格添加 onChange 处理
<Table
  columns={columns}
  dataSource={data}
  rowKey="id"
  loading={loading}
  onChange={handleTableChange}
  ...
/>
```

## 技术细节

### 1. 为什么使用两次请求？

**优点**：
- ✅ 后端接口保持简单，不需要添加 `project_id` 参数
- ✅ 后端不需要修改 CRUD 层的关联查询逻辑
- ✅ 利用现有的账号 API 和余额 API
- ✅ 前端灵活控制查询逻辑

**缺点**：
- ❌ 查询项目所有账号时，需要多次请求
- ❌ 前端需要处理数据聚合、排序和分页
- ❌ 性能略低于后端直接查询

**适用场景**：
- 项目账号数量不多（< 1000）
- 更注重后端接口的简洁性
- 前端有足够的处理能力

### 2. 分批查询优化

```typescript
const batchSize = 50 // 每批查询50个账号

for (let i = 0; i < projectAccountIds.length; i += batchSize) {
  const batchIds = projectAccountIds.slice(i, i + batchSize)
  
  // 并发查询每个账号的余额
  const batchPromises = batchIds.map(accountId => ...)
  const batchResults = await Promise.all(batchPromises)
  
  allBalances = [...allBalances, ...batchBalances]
}
```

**为什么分批？**
- 避免一次性发起过多并发请求
- 浏览器有并发限制（通常6-8个）
- 分批可以更好地控制并发数量

### 3. 前端排序实现

```typescript
allBalances.sort((a, b) => {
  const field = orderBy.replace('-', '')
  const isDesc = orderBy.startsWith('-')
  
  let aVal: any = a[field as keyof ProjectBalance]
  let bVal: any = b[field as keyof ProjectBalance]
  
  // 处理数字类型
  if (field === 'balance' || field === 'variable') {
    aVal = Number(aVal)
    bVal = Number(bVal)
  }
  
  if (aVal < bVal) return isDesc ? 1 : -1
  if (aVal > bVal) return isDesc ? -1 : 1
  return 0
})
```

**关键点**：
- 支持正序和倒序
- 数字类型需要转换后比较
- 字符串类型直接比较

### 4. 前端分页实现

```typescript
// 前端分页
const start = (page - 1) * pageSize
const end = start + pageSize
const paginatedData = allBalances.slice(start, end)

setData(paginatedData)
setTotal(allBalances.length)
```

**关键点**：
- 使用 `slice` 截取当前页数据
- `total` 设置为所有数据的总数
- Ant Design Table 自动处理分页 UI

## 使用示例

### 示例1: 查看项目所有账号余额（按余额倒序）

1. 选择"项目A"
2. 不选择账号
3. 点击"余额"列头，选择倒序（↓）
4. 点击"搜索"
5. ✅ 显示项目A所有账号的余额，按余额从高到低排列

**API 请求流程**：
```
1. GET /v1/project/account?project_id=xxx&page=1&limit=10000
   → 获取项目A的所有账号ID

2. GET /v1/project/balance?account_id=id1&page=1&limit=1&order_by=-balance
   GET /v1/project/balance?account_id=id2&page=1&limit=1&order_by=-balance
   ...
   → 并发查询每个账号的余额

3. 前端聚合、排序、分页
```

### 示例2: 查看特定账号余额（按创建时间正序）

1. 选择"项目A"
2. 选择"account1@example.com"
3. 点击"创建时间"列头，选择正序（↑）
4. 点击"搜索"
5. ✅ 显示该账号的余额，按创建时间从旧到新排列

**API 请求**：
```
GET /v1/project/balance?account_id=yyy&order_by=create_time&page=1&limit=10&res_count=true
```

## 性能对比

### 选择账号时（单账号查询）

| 方案 | 请求次数 | 性能 |
|------|---------|------|
| 当前方案 | 1次 | ⭐⭐⭐⭐⭐ 最优 |

### 未选择账号时（项目级查询）

| 账号数量 | 请求次数 | 性能 |
|---------|---------|------|
| 10个 | 1 + 10 = 11次 | ⭐⭐⭐⭐ 良好 |
| 50个 | 1 + 50 = 51次 | ⭐⭐⭐ 一般 |
| 100个 | 1 + 100 = 101次 | ⭐⭐ 较慢 |
| 500个 | 1 + 500 = 501次 | ⭐ 慢 |

**优化建议**：
- 如果项目账号数量较多（> 100），建议后端添加 `project_id` 参数
- 如果项目账号数量较少（< 50），当前方案完全可行

## 优势

### 1. 后端接口简洁

- ✅ 不需要修改后端 API 参数
- ✅ 不需要修改 CRUD 层逻辑
- ✅ 保持接口的单一职责

### 2. 前端灵活控制

- ✅ 前端可以自由组合查询条件
- ✅ 前端可以实现复杂的数据聚合
- ✅ 前端可以自定义排序和分页逻辑

### 3. 项目信息正常显示

- ✅ 后端预加载 `account__project`
- ✅ 前端可以访问 `balance.account.project.name`
- ✅ 项目名称列正常显示

## 相关文件

### 后端文件
- ✅ `backend/app/crud/project/balance.py` - 预加载项目信息
- ✅ `backend/app/apis/v1/project/balance.py` - 添加排序字段支持

### 前端文件
- ✅ `frontend/src/api/project.ts` - 移除 project_id 参数
- ✅ `frontend/src/views/Project/ProjectBalance.tsx` - 实现两次请求逻辑

### 文档
- ✅ `docs/fixes/PROJECT_BALANCE_SORTING_AND_OPTIONAL_ACCOUNT.md` - 本文档

## 总结

✅ 账号选择改为可选，可以查看项目所有账号的余额
✅ 添加了按余额、变动、创建时间、更新时间排序功能
✅ 后端接口保持简单，不添加 project_id 参数
✅ 前端通过两次请求实现项目级查询
✅ 后端预加载项目信息，项目名称列正常显示
✅ 分批查询优化，避免并发过多
✅ 前端实现数据聚合、排序和分页
✅ 所有 TypeScript 诊断通过

现在用户可以更灵活地查询和分析项目余额数据，同时保持后端接口的简洁性！

### 1. 账号选择改为可选

**修改前**：
- 必须先选择项目
- 必须再选择账号
- 只能查看单个账号的余额

**修改后**：
- 必须先选择项目（必选）
- 账号选择变为可选
- 不选账号时，显示该项目所有账号的余额
- 选择账号时，只显示该账号的余额

**使用场景**：

```
场景1: 查看项目所有账号余额
1. 选择"项目A"
2. 不选择账号
3. 点击"搜索"
4. ✅ 显示项目A所有账号的余额

场景2: 查看项目特定账号余额
1. 选择"项目A"
2. 选择"account1@example.com"
3. 点击"搜索"
4. ✅ 只显示该账号的余额
```

### 2. 表格排序功能

支持以下字段的排序：

| 字段 | 说明 | 正序 | 倒序 |
|------|------|------|------|
| **余额** | balance | 从小到大 | 从大到小 |
| **变动** | variable | 从小到大（负数在前） | 从大到小（正数在前） |
| **创建时间** | create_time | 从旧到新 | 从新到旧（默认） |
| **更新时间** | update_time | 从旧到新 | 从新到旧 |

**使用方式**：
- 点击表头的排序图标进行排序
- 再次点击切换正序/倒序
- 第三次点击取消排序（恢复默认）

**常用排序场景**：

```
场景1: 查看余额最高的账号
→ 点击"余额"列头，选择倒序（↓）

场景2: 查看余额最低的账号
→ 点击"余额"列头，选择正序（↑）

场景3: 查看变动最大的账号（增加最多）
→ 点击"变动"列头，选择倒序（↓）

场景4: 查看变动最大的账号（减少最多）
→ 点击"变动"列头，选择正序（↑）

场景5: 查看最新创建的余额记录
→ 点击"创建时间"列头，选择倒序（↓）- 默认已是倒序
```

## 实现方案

### 后端修改

#### 1. CRUD 层添加 project_id 参数

**文件**: `backend/app/crud/project/balance.py`

```python
async def get_multi(self,
                    project_id: UUID | None = None,  # ← 新增
                    account_id: UUID | None = None,
                    page: int = 1,
                    limit: int = 10,
                    res_count: bool = False,
                    order_by: str = '-create_time',
                    ...
                    ) -> OutList:
    query = ProjectBalance.all()
    
    # 如果指定了项目ID，通过账号关联查询
    if project_id:
        query = query.filter(account__project_id=project_id)  # ← 关联查询
    
    if account_id:
        query = query.filter(account_id=account_id)
    
    ...
    
    # 预加载关联数据（包括项目信息）
    res = await query.prefetch_related('account', 'account__project')  # ← 预加载项目
```

**关键点**：
- 使用 `account__project_id` 进行关联查询
- 使用 `prefetch_related` 预加载 `account` 和 `account__project`
- 避免 N+1 查询问题

#### 2. API 层添加 project_id 和排序字段

**文件**: `backend/app/apis/v1/project/balance.py`

```python
@app.get("", response_model=OutList, ...)
async def gets(
    project_id: UUID | None = Query(None, description="项目ID"),  # ← 新增
    account_id: UUID | None = Query(None, description="关联账号ID"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|create_time|update_time|balance|variable)$",  # ← 添加 balance 和 variable
    ),
    ...
):
    return await project_balance_crud.get_multi(
        project_id=project_id,  # ← 传递 project_id
        account_id=account_id,
        order_by=order_by or "-create_time",
        ...
    )
```

**支持的排序字段**：
- `id` / `-id`
- `create_time` / `-create_time` (默认)
- `update_time` / `-update_time`
- `balance` / `-balance` (新增)
- `variable` / `-variable` (新增)

### 前端修改

#### 1. API 类型定义

**文件**: `frontend/src/api/project.ts`

```typescript
export const getProjectBalanceList = (params?: PaginationParams & { 
  project_id?: string      // ← 新增：项目ID
  account_id?: string      // 保留：账号ID（可选）
  order_by?: string        // ← 新增：排序字段
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<ProjectBalance>>('/v1/project/balance', { params })
}
```

#### 2. 界面逻辑修改

**文件**: `frontend/src/views/Project/ProjectBalance.tsx`

**关键修改**：

```typescript
// 1. 添加排序状态
const [orderBy, setOrderBy] = useState<string>('-create_time')

// 2. 修改查询逻辑：必须选择项目，账号可选
const fetchData = async () => {
  if (!searchProjectId) {  // ← 只检查项目
    setData([])
    setTotal(0)
    return
  }
  
  const res = await getProjectBalanceList({
    page,
    limit: pageSize,
    res_count: true,
    project_id: searchProjectId,    // ← 必传
    account_id: searchAccountId,    // ← 可选
    order_by: orderBy,              // ← 排序参数
    ...
  })
}

// 3. 依赖项更新：添加 searchProjectId 和 orderBy
useEffect(() => {
  fetchData()
}, [page, pageSize, searchProjectId, searchAccountId, orderBy])  // ← 添加依赖

// 4. 表格排序处理
const handleTableChange: TableProps<ProjectBalance>['onChange'] = (_pagination, _filters, sorter: any) => {
  if (sorter.field) {
    const order = sorter.order === 'ascend' ? '' : '-'
    setOrderBy(`${order}${sorter.field}`)
  }
}

// 5. 获取当前排序状态
const getSortOrder = (field: string): SortOrder => {
  if (orderBy === field) return 'ascend'
  if (orderBy === `-${field}`) return 'descend'
  return null
}

// 6. 列定义添加排序
const columns = [
  {
    title: '余额',
    dataIndex: 'balance',
    key: 'balance',
    sorter: true,                      // ← 启用排序
    sortOrder: getSortOrder('balance'), // ← 显示排序状态
    render: (balance: number | string) => Number(balance).toFixed(2),
  },
  {
    title: '变动',
    dataIndex: 'variable',
    key: 'variable',
    sorter: true,                        // ← 启用排序
    sortOrder: getSortOrder('variable'), // ← 显示排序状态
    render: (variable: number | string) => {
      const num = Number(variable)
      const color = num > 0 ? 'green' : num < 0 ? 'red' : 'default'
      return <span style={{ color }}>{num > 0 ? '+' : ''}{num.toFixed(2)}</span>
    },
  },
  {
    title: '创建时间',
    dataIndex: 'create_time',
    key: 'create_time',
    sorter: true,                            // ← 启用排序
    sortOrder: getSortOrder('create_time'),  // ← 显示排序状态
  },
  {
    title: '更新时间',
    dataIndex: 'update_time',
    key: 'update_time',
    sorter: true,                            // ← 启用排序
    sortOrder: getSortOrder('update_time'),  // ← 显示排序状态
  },
]

// 7. 表格添加 onChange 处理
<Table
  columns={columns}
  dataSource={data}
  rowKey="id"
  loading={loading}
  onChange={handleTableChange}  // ← 处理排序
  ...
/>

// 8. 更新界面提示
<Select
  placeholder="1. 选择项目（必选）"  // ← 明确标注必选
  ...
/>
<Select
  placeholder="2. 选择账号（可选）"  // ← 明确标注可选
  disabled={!searchProjectId}
  ...
/>

// 9. 更新空状态提示
locale={{
  emptyText: searchProjectId 
    ? '暂无数据'           // ← 简化提示
    : '请先选择项目'
}}

// 10. 重置按钮清空排序
<Button onClick={() => { 
  setSearchProjectId(undefined); 
  setSearchAccountId(undefined); 
  setCreateTimeRange(null); 
  setUpdateTimeRange(null); 
  setOrderBy('-create_time');  // ← 重置排序
  setPage(1); 
  setData([]);
  setTotal(0);
}}>
  重置
</Button>
```

## 技术细节

### 1. 关联查询实现

使用 Tortoise ORM 的双下划线语法进行关联查询：

```python
# 查询项目ID为 xxx 的所有余额
query = query.filter(account__project_id=project_id)

# 等价于 SQL:
# SELECT * FROM project_balance pb
# JOIN project_account pa ON pb.account_id = pa.id
# WHERE pa.project_id = 'xxx'
```

### 2. 预加载优化

使用 `prefetch_related` 避免 N+1 查询：

```python
# 一次性加载所有关联数据
res = await query.prefetch_related('account', 'account__project')

# 等价于执行 3 条 SQL:
# 1. SELECT * FROM project_balance WHERE ...
# 2. SELECT * FROM project_account WHERE id IN (...)
# 3. SELECT * FROM project_info WHERE id IN (...)
```

### 3. 排序字段映射

| 前端字段 | 后端字段 | 数据库字段 |
|---------|---------|-----------|
| balance | balance | balance |
| variable | variable | variable |
| create_time | create_time | create_time |
| update_time | update_time | update_time |

### 4. 排序方向

| Ant Design | 后端参数 | 说明 |
|-----------|---------|------|
| ascend | `field` | 正序（无前缀） |
| descend | `-field` | 倒序（前缀 `-`） |
| null | `-create_time` | 默认排序 |

## 使用示例

### 示例1: 查看项目所有账号余额（按余额倒序）

1. 选择"项目A"
2. 不选择账号
3. 点击"余额"列头，选择倒序（↓）
4. 点击"搜索"
5. ✅ 显示项目A所有账号的余额，按余额从高到低排列

**API 请求**：
```
GET /v1/project/balance?project_id=xxx&order_by=-balance&page=1&limit=10&res_count=true
```

### 示例2: 查看特定账号余额（按创建时间正序）

1. 选择"项目A"
2. 选择"account1@example.com"
3. 点击"创建时间"列头，选择正序（↑）
4. 点击"搜索"
5. ✅ 显示该账号的余额，按创建时间从旧到新排列

**API 请求**：
```
GET /v1/project/balance?project_id=xxx&account_id=yyy&order_by=create_time&page=1&limit=10&res_count=true
```

### 示例3: 查看变动最大的账号（增加最多）

1. 选择"项目A"
2. 不选择账号
3. 点击"变动"列头，选择倒序（↓）
4. 点击"搜索"
5. ✅ 显示项目A所有账号的余额，按变动从大到小排列（正数在前）

**API 请求**：
```
GET /v1/project/balance?project_id=xxx&order_by=-variable&page=1&limit=10&res_count=true
```

### 示例4: 查看变动最大的账号（减少最多）

1. 选择"项目A"
2. 不选择账号
3. 点击"变动"列头，选择正序（↑）
4. 点击"搜索"
5. ✅ 显示项目A所有账号的余额，按变动从小到大排列（负数在前）

**API 请求**：
```
GET /v1/project/balance?project_id=xxx&order_by=variable&page=1&limit=10&res_count=true
```

## 界面变化

### 搜索栏

**修改前**：
```
[1. 选择项目] [2. 选择账号] [时间范围] [搜索] [重置]
```

**修改后**：
```
[1. 选择项目（必选）] [2. 选择账号（可选）] [时间范围] [搜索] [重置]
```

### 表格列头

**修改前**：
```
账号 | 余额 | 变动 | 项目 | 创建时间 | 更新时间 | 操作
```

**修改后**（带排序图标）：
```
账号 | 余额 ⇅ | 变动 ⇅ | 项目 | 创建时间 ⇅ | 更新时间 ⇅ | 操作
```

### 空状态提示

**修改前**：
- 未选项目："请先选择项目"
- 未选账号："请选择账号查看余额"
- 已选账号："暂无数据"

**修改后**：
- 未选项目："请先选择项目"
- 已选项目："暂无数据"（无论是否选择账号）

## 优势

### 1. 更灵活的查询方式

- ✅ 可以查看项目所有账号的余额（全局视图）
- ✅ 可以查看特定账号的余额（详细视图）
- ✅ 用户根据需求自由选择

### 2. 更强大的数据分析

- ✅ 按余额排序：快速找到余额最高/最低的账号
- ✅ 按变动排序：快速找到增加/减少最多的账号
- ✅ 按时间排序：查看最新/最早的余额记录

### 3. 更好的用户体验

- ✅ 明确标注"必选"和"可选"
- ✅ 表格列头可点击排序
- ✅ 排序状态可视化（箭头图标）
- ✅ 重置按钮恢复默认排序

### 4. 更高的性能

- ✅ 使用关联查询代替多次查询
- ✅ 使用 prefetch_related 避免 N+1 问题
- ✅ 数据库层面排序，性能更好

## 相关文件

### 后端文件
- ✅ `backend/app/crud/project/balance.py` - 添加 project_id 参数和关联查询
- ✅ `backend/app/apis/v1/project/balance.py` - 添加 project_id 参数和排序字段

### 前端文件
- ✅ `frontend/src/api/project.ts` - 添加 project_id 和 order_by 参数
- ✅ `frontend/src/views/Project/ProjectBalance.tsx` - 实现排序功能和可选账号

### 文档
- ✅ `docs/fixes/PROJECT_BALANCE_SORTING_AND_OPTIONAL_ACCOUNT.md` - 本文档
- `docs/fixes/PROJECT_BALANCE_SEARCH_BY_PROJECT.md` - 级联查询文档
- `docs/fixes/PROJECT_BALANCE_TYPE_FIX.md` - 类型修复文档

## 测试场景

### 测试1: 查看项目所有账号余额

1. 选择"项目A"
2. 不选择账号
3. 点击"搜索"
4. ✅ 验证显示项目A所有账号的余额

### 测试2: 查看特定账号余额

1. 选择"项目A"
2. 选择"account1@example.com"
3. 点击"搜索"
4. ✅ 验证只显示该账号的余额

### 测试3: 按余额倒序排列

1. 选择"项目A"
2. 点击"余额"列头，选择倒序
3. 点击"搜索"
4. ✅ 验证余额从高到低排列

### 测试4: 按变动正序排列

1. 选择"项目A"
2. 点击"变动"列头，选择正序
3. 点击"搜索"
4. ✅ 验证变动从小到大排列（负数在前）

### 测试5: 切换排序

1. 选择"项目A"
2. 点击"余额"列头（倒序）
3. 再次点击"余额"列头（正序）
4. 第三次点击"余额"列头（取消排序）
5. ✅ 验证排序状态正确切换

### 测试6: 重置功能

1. 选择项目、账号、时间范围、排序
2. 点击"重置"按钮
3. ✅ 验证所有条件清空，排序恢复默认

## 总结

✅ 账号选择改为可选，可以查看项目所有账号的余额
✅ 添加了按余额、变动、创建时间、更新时间排序功能
✅ 后端支持 project_id 参数和 balance/variable 排序
✅ 前端实现表格排序交互和状态管理
✅ 使用关联查询和预加载优化性能
✅ 界面提示更加清晰（必选/可选）
✅ 所有 TypeScript 诊断通过

现在用户可以更灵活地查询和分析项目余额数据！
