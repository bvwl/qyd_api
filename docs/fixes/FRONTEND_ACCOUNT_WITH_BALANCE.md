# 前端账号页面集成余额功能

## 更新时间
2026-01-21

## 功能描述

将余额功能完全集成到项目账号页面中，删除独立的余额页面。

## 主要改动

### 1. 删除文件

- ✅ `frontend/src/views/Project/ProjectBalance.tsx` - 删除独立的余额页面

### 2. 修改账号页面

**文件**: `frontend/src/views/Project/ProjectAccount.tsx`

#### 2.1 添加余额列

```typescript
const columns = [
  {
    title: '账号',
    dataIndex: 'account',
    key: 'account',
    width: 200,
  },
  // ... 其他列
  {
    title: '余额',
    dataIndex: 'balance',
    key: 'balance',
    width: 120,
    sorter: true,  // 支持排序
    sortOrder: getSortOrder('balance'),
    render: (balance: number | string) => Number(balance).toFixed(2),
  },
  {
    title: '变动',
    dataIndex: 'variable',
    key: 'variable',
    width: 120,
    sorter: true,  // 支持排序
    sortOrder: getSortOrder('variable'),
    render: (variable: number | string) => {
      const num = Number(variable)
      const color = num > 0 ? 'green' : num < 0 ? 'red' : 'default'
      return <span style={{ color }}>{num > 0 ? '+' : ''}{num.toFixed(2)}</span>
    },
  },
  // ... 其他列
]
```

**说明**：
- 余额列显示两位小数
- 变动列根据正负显示不同颜色（绿色/红色）
- 两列都支持排序

#### 2.2 添加排序功能

```typescript
const [orderBy, setOrderBy] = useState<string>('-create_time')

const handleTableChange: TableProps<ProjectAccount>['onChange'] = (_pagination, _filters, sorter: any) => {
  if (sorter.field) {
    const order = sorter.order === 'ascend' ? '' : '-'
    setOrderBy(`${order}${sorter.field}`)
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }
}

const getSortOrder = (field: string): SortOrder => {
  if (orderBy === field) return 'ascend'
  if (orderBy === `-${field}`) return 'descend'
  return null
}
```

**支持的排序字段**：
- `balance` - 余额
- `variable` - 变动
- `create_time` - 创建时间
- `account` - 账号
- `status` - 状态

#### 2.3 编辑表单添加余额字段

```typescript
const handleEdit = (record: ProjectAccount) => {
  setEditingAccount(record)
  form.setFieldsValue({
    account: record.account,
    password: record.password,
    status: record.status,
    account_type: record.account_type,
    balance: record.balance,  // ← 添加余额字段
    project_id: record.project_id,
  })
  setModalVisible(true)
}
```

```tsx
<Form.Item
  label={
    <span>
      余额
      <Tooltip title="可选，不填默认为0。更新余额时会自动计算变动和记录历史">
        <span style={{ marginLeft: 4, color: '#999' }}>(?)</span>
      </Tooltip>
    </span>
  }
  name="balance"
>
  <InputNumber
    placeholder="请输入余额（可选）"
    style={{ width: '100%' }}
    min={0}
    precision={2}
  />
</Form.Item>
```

**说明**：
- 余额字段为可选，不填默认为0
- 添加了 Tooltip 提示用户余额的自动计算功能
- 使用 InputNumber 组件，限制最小值为0，精度为2位小数

#### 2.4 API 调用添加排序参数

```typescript
const fetchData = async () => {
  setLoading(true)
  try {
    const res = await getProjectAccountList({
      page,
      limit: pageSize,
      res_count: true,
      account: searchAccount || undefined,
      account_type: searchAccountType,
      status: searchStatus,
      order_by: orderBy,  // ← 添加排序参数
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

#### 2.5 表格添加横向滚动

```tsx
<Table
  columns={columns}
  dataSource={data}
  rowKey="id"
  loading={loading}
  onChange={handleTableChange}  // ← 添加排序处理
  scroll={{ x: 1200 }}  // ← 添加横向滚动
  pagination={{...}}
/>
```

**说明**：因为添加了余额和变动列，表格宽度增加，需要横向滚动

## 界面效果

### 表格列

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 账号 | 类型 | 状态 | 余额⇅ | 变动⇅ | 项目 | 创建时间⇅ | 操作          │
├──────────────────────────────────────────────────────────────────────────┤
│ test@example.com | 邮箱 | 正常 | 1000.50 | +50.00 | 项目A | ... | 编辑 删除 │
│ user@example.com | 邮箱 | 正常 | 950.00  | -20.00 | 项目B | ... | 编辑 删除 │
└──────────────────────────────────────────────────────────────────────────┘
```

### 编辑表单

```
┌─────────────────────────────────────┐
│ 编辑账号                             │
├─────────────────────────────────────┤
│ 账号: [test@example.com]            │
│ 密码: [••••••••]                    │
│ 账号类型: [邮箱 ▼]                  │
│ 状态: [正常 ▼]                      │
│ 项目: [项目A ▼]                     │
│ 余额 (?): [1000.50]                 │
│                                     │
│           [取消]  [确定]            │
└─────────────────────────────────────┘
```

## 使用场景

### 场景1: 查看账号余额

1. 打开项目账号页面
2. 直接在列表中查看每个账号的余额和变动
3. ✅ 无需切换页面

### 场景2: 按余额排序

1. 点击"余额"列头
2. 选择倒序（↓）
3. ✅ 显示余额从高到低的账号

### 场景3: 按变动排序

1. 点击"变动"列头
2. 选择倒序（↓）
3. ✅ 显示变动最大的账号（增加最多）

### 场景4: 创建账号（不设置余额）

1. 点击"新增账号"
2. 填写账号、密码、类型、状态、项目
3. 不填余额字段
4. 点击"确定"
5. ✅ 账号创建成功，余额默认为0

### 场景5: 创建账号（设置初始余额）

1. 点击"新增账号"
2. 填写账号、密码、类型、状态、项目
3. 填写余额：1000.00
4. 点击"确定"
5. ✅ 账号创建成功，余额为1000.00

### 场景6: 更新账号余额

1. 点击账号的"编辑"按钮
2. 修改余额：1050.00
3. 点击"确定"
4. ✅ 余额更新成功
5. ✅ 变动自动计算（1050.00 - 昨天的余额）
6. ✅ 历史记录自动更新

## 数据展示

### 余额显示

```typescript
render: (balance: number | string) => Number(balance).toFixed(2)
```

- 始终显示两位小数
- 例如：`1000.50`、`0.00`

### 变动显示

```typescript
render: (variable: number | string) => {
  const num = Number(variable)
  const color = num > 0 ? 'green' : num < 0 ? 'red' : 'default'
  return <span style={{ color }}>{num > 0 ? '+' : ''}{num.toFixed(2)}</span>
}
```

- 正数显示绿色，带 `+` 号：`+50.00`
- 负数显示红色：`-20.00`
- 零显示默认颜色：`0.00`

## 优势

### 1. 界面更简洁

- ✅ 删除了独立的余额页面
- ✅ 账号和余额信息在同一页面
- ✅ 减少页面切换

### 2. 操作更便捷

- ✅ 直接在账号列表查看余额
- ✅ 编辑账号时可以同时更新余额
- ✅ 支持按余额和变动排序

### 3. 数据更直观

- ✅ 余额和变动一目了然
- ✅ 变动用颜色区分正负
- ✅ 支持排序快速找到目标账号

### 4. 功能更完整

- ✅ 余额自动计算
- ✅ 历史自动记录
- ✅ 变动实时更新

## 相关文件

### 前端文件

**修改**:
- ✅ `frontend/src/views/Project/ProjectAccount.tsx` - 添加余额列和编辑功能
- ✅ `frontend/src/types/index.ts` - ProjectAccount 类型包含余额字段
- ✅ `frontend/src/api/project.ts` - 删除余额 API，账号 API 支持排序

**删除**:
- ✅ `frontend/src/views/Project/ProjectBalance.tsx` - 删除独立的余额页面

### 后端文件

- ✅ `backend/app/models/project.py` - ProjectAccount 模型包含余额字段
- ✅ `backend/app/schemas/project/account.py` - 账号 Schema 包含余额字段
- ✅ `backend/app/crud/project/account.py` - 实现余额自动计算逻辑
- ✅ `backend/app/apis/v1/project/account.py` - 支持余额排序

### 文档

- ✅ `docs/fixes/FRONTEND_ACCOUNT_WITH_BALANCE.md` - 本文档
- ✅ `docs/fixes/MERGE_BALANCE_INTO_ACCOUNT.md` - 合并余额表文档
- ✅ `docs/fixes/BALANCE_AUTO_CALCULATION.md` - 余额自动计算文档

## 注意事项

1. **路由更新**: 需要删除或重定向原来的余额页面路由
2. **菜单更新**: 需要从菜单中移除余额菜单项
3. **权限检查**: 余额字段的编辑权限与账号编辑权限一致
4. **数据迁移**: 确保后端数据库迁移已完成

## 测试清单

- [ ] 账号列表显示余额和变动列
- [ ] 余额列可以排序
- [ ] 变动列可以排序
- [ ] 变动显示正确的颜色
- [ ] 创建账号时余额可选
- [ ] 编辑账号时可以更新余额
- [ ] 更新余额后变动自动计算
- [ ] 表格横向滚动正常
- [ ] 余额字段的 Tooltip 提示正常显示

## 总结

✅ 将余额功能完全集成到账号页面
✅ 删除了独立的余额页面
✅ 添加了余额和变动列，支持排序
✅ 编辑表单添加了余额字段
✅ 变动用颜色区分正负
✅ 界面更简洁，操作更便捷
✅ 所有 TypeScript 诊断通过

现在用户可以在账号页面直接管理余额，无需切换页面！
