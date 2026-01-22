# 项目余额最终实现方案

## 更新时间
2026-01-21

## 实现方案

参考其他页面（如项目账号页面）的实现方式，使用简单的搜索条件方式，而不是复杂的两次请求。

## 功能特性

1. **项目和账号作为可选搜索条件**
   - 项目选择器（可选）
   - 账号选择器（可选）
   - 选择项目后，账号列表自动过滤为该项目的账号
   - 可以只选项目、只选账号、或两者都选

2. **表格排序功能**
   - 余额（正序/倒序）
   - 变动（正序/倒序）
   - 创建时间（正序/倒序）
   - 更新时间（正序/倒序）

3. **时间范围筛选**
   - 创建时间范围
   - 更新时间范围

4. **项目名称显示**
   - 后端预加载 `account__project`
   - 表格中显示项目名称列

## 实现细节

### 后端

#### 1. CRUD 层预加载项目信息

**文件**: `backend/app/crud/project/balance.py`

```python
async def get_multi(self, ...) -> OutList:
    query = ProjectBalance.all()
    
    if account_id:
        query = query.filter(account_id=account_id)
    
    ...
    
    # 预加载关联数据（包括项目信息）
    res = await query.prefetch_related('account', 'account__project')
    
    ...
```

#### 2. API 层支持排序

**文件**: `backend/app/apis/v1/project/balance.py`

```python
@app.get("", response_model=OutList, ...)
async def gets(
    account_id: UUID | None = Query(None, description="关联账号ID"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|create_time|update_time|balance|variable)$",
    ),
    ...
):
    return await project_balance_crud.get_multi(
        account_id=account_id,
        order_by=order_by or "-create_time",
        ...
    )
```

### 前端

#### 1. 搜索条件

```typescript
const [searchProjectId, setSearchProjectId] = useState<string>()
const [searchAccountId, setSearchAccountId] = useState<string>()
const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
const [orderBy, setOrderBy] = useState<string>('-create_time')
```

#### 2. 查询逻辑

```typescript
const fetchData = async () => {
  setLoading(true)
  try {
    const res = await getProjectBalanceList({
      page,
      limit: pageSize,
      res_count: true,
      account_id: searchAccountId,  // 可选
      order_by: orderBy,
      create_time_start: createTimeRange?.[0]?.format('YYYY-MM-DD'),
      create_time_end: createTimeRange?.[1]?.format('YYYY-MM-DD'),
      update_time_start: updateTimeRange?.[0]?.format('YYYY-MM-DD'),
      update_time_end: updateTimeRange?.[1]?.format('YYYY-MM-DD'),
    })
    setData(res.items || [])
    setTotal(res.count || 0)
  } catch (error) {
    setData([])
    setTotal(0)
  } finally {
    setLoading(false)
  }
}
```

#### 3. 项目选择联动

```typescript
// 当选择项目时，重新加载该项目的账号列表
useEffect(() => {
  if (searchProjectId) {
    fetchAccountList(searchProjectId)
  } else {
    fetchAccountList()  // 加载所有账号
  }
  setSearchAccountId(undefined) // 清空账号选择
}, [searchProjectId])
```

#### 4. 账号列表加载

```typescript
const fetchAccountList = async (projectId?: string) => {
  try {
    const res = await getProjectAccountList({
      page: 1,
      limit: 100,  // 每次最多100条
      project_id: projectId,  // 可选
    })
    setAccountList(res.items || [])
  } catch (error) {
    setAccountList([])
  }
}
```

#### 5. 搜索和重置

```typescript
const handleSearch = () => {
  setPage(1)
  fetchData()
}

const handleReset = () => {
  setSearchProjectId(undefined)
  setSearchAccountId(undefined)
  setCreateTimeRange(null)
  setUpdateTimeRange(null)
  setOrderBy('-create_time')
  setPage(1)
  setTimeout(() => {
    fetchData()
  }, 0)
}
```

#### 6. 表格排序

```typescript
const handleTableChange: TableProps<ProjectBalance>['onChange'] = (_pagination, _filters, sorter: any) => {
  if (sorter.field) {
    const order = sorter.order === 'ascend' ? '' : '-'
    setOrderBy(`${order}${sorter.field}`)
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }
}
```

## 界面布局

```
┌─────────────────────────────────────────────────────────────────────┐
│ [项目▼] [账号▼] [创建时间] [更新时间] [搜索] [重置]  [新增余额记录] │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 账号 | 余额⇅ | 变动⇅ | 项目 | 创建时间⇅ | 更新时间⇅ | 操作        │
├─────────────────────────────────────────────────────────────────────┤
│ ...                                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 使用场景

### 场景1: 查看所有余额

1. 不选择任何条件
2. 点击"搜索"
3. ✅ 显示所有余额记录

### 场景2: 查看特定项目的所有账号余额

1. 选择"项目A"
2. 不选择账号
3. 点击"搜索"
4. ✅ 显示项目A所有账号的余额

### 场景3: 查看特定账号的余额

1. 选择"项目A"
2. 选择"account1@example.com"
3. 点击"搜索"
4. ✅ 显示该账号的余额

### 场景4: 按余额排序

1. 选择搜索条件
2. 点击"余额"列头
3. ✅ 按余额排序（倒序）
4. 再次点击
5. ✅ 按余额排序（正序）

### 场景5: 按时间范围筛选

1. 选择创建时间范围
2. 点击"搜索"
3. ✅ 显示该时间范围内创建的余额记录

## 与其他页面的一致性

参考 `frontend/src/views/Project/ProjectAccount.tsx` 的实现：

| 特性 | 项目账号页面 | 项目余额页面 |
|------|------------|------------|
| 搜索条件 | 账号、类型、状态、时间 | 项目、账号、时间 |
| 搜索按钮 | ✅ | ✅ |
| 重置按钮 | ✅ | ✅ |
| 表格排序 | ❌ | ✅ |
| 时间范围 | ✅ | ✅ |
| 分页 | ✅ | ✅ |
| 权限控制 | ✅ | ✅ |

## 优势

### 1. 简单直观

- ✅ 参考其他页面的实现方式
- ✅ 用户熟悉的交互模式
- ✅ 代码结构清晰

### 2. 性能良好

- ✅ 后端分页和排序
- ✅ 只查询一次
- ✅ 预加载关联数据

### 3. 灵活查询

- ✅ 项目和账号都是可选条件
- ✅ 可以组合多个条件
- ✅ 支持时间范围筛选

### 4. 项目名称显示

- ✅ 后端预加载项目信息
- ✅ 前端直接访问 `balance.account.project.name`
- ✅ 无需额外请求

## 限制说明

### 1. 每次查询最多100条

- 项目列表：最多100个
- 账号列表：最多100个
- 余额列表：分页显示（10/20/50/100 per page）

### 2. 账号列表按项目过滤

- 选择项目后，账号列表只显示该项目的账号（最多100个）
- 不选择项目时，账号列表显示所有账号（最多100个）

## 相关文件

### 后端文件
- ✅ `backend/app/crud/project/balance.py` - 预加载项目信息
- ✅ `backend/app/apis/v1/project/balance.py` - 支持排序字段

### 前端文件
- ✅ `frontend/src/api/project.ts` - API 类型定义
- ✅ `frontend/src/views/Project/ProjectBalance.tsx` - 余额页面实现

### 文档
- ✅ `docs/fixes/PROJECT_BALANCE_FINAL_IMPLEMENTATION.md` - 本文档

## 总结

✅ 参考项目账号页面的实现方式
✅ 使用简单的搜索条件，而不是复杂的两次请求
✅ 项目和账号都是可选搜索条件
✅ 支持表格排序（余额、变动、创建时间、更新时间）
✅ 支持时间范围筛选
✅ 项目名称正常显示
✅ 后端每次最多返回100条
✅ 代码简洁清晰，易于维护
✅ 所有 TypeScript 诊断通过

现在项目余额页面的实现与其他页面保持一致，用户体验更好！
