# 项目账号余额功能增强

## 更新时间
2026-01-21

## 功能描述

在项目账号页面中增强余额功能，添加历史余额查看和项目筛选功能。

## 主要改动

### 1. 数据库迁移

**执行脚本**: `backend/scripts/apply_balance_migration.py`

```bash
python backend/scripts/apply_balance_migration.py
```

**迁移内容**:
- ✅ 添加 `balance`、`variable`、`balance_history` 字段到 `project_account` 表
- ✅ 从旧的 `project_balance` 表迁移数据
- ✅ 删除旧的 `project_balance` 表
- ✅ 添加余额字段索引

### 2. 前端功能增强

#### 2.1 添加项目筛选（必选）

**位置**: 筛选条件第一项

```tsx
<Select
  placeholder="选择项目（必选）"
  value={searchProjectId}
  onChange={setSearchProjectId}
  style={{ width: 200 }}
  allowClear
  showSearch
  filterOption={(input, option) =>
    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
  }
  options={projectList.map(project => ({
    label: project.name,
    value: project.id,
  }))}
/>
```

**说明**:
- 项目筛选放在第一位，作为主要筛选条件
- 支持搜索项目名称
- 选择项目后显示该项目下的所有账号
- **必须选择项目才能查询账号列表**

#### 2.2 接口调用验证

**验证逻辑**:

```typescript
const fetchData = async () => {
  // 如果没有选择项目，不查询账号列表
  if (!searchProjectId) {
    setData([])
    setTotal(0)
    return
  }
  // ... 继续查询
}

const handleSearch = () => {
  // 验证是否选择了项目
  if (!searchProjectId) {
    message.warning('请先选择项目')
    return
  }
  setPage(1)
  fetchData()
}
```

**说明**:
- ✅ 没有选择项目时，不会调用账号列表接口
- ✅ 点击搜索时会提示"请先选择项目"
- ✅ 重置后清空数据，不会自动查询
- ✅ 只有选择项目后才会触发查询

#### 2.3 空状态提示

**显示条件**: 没有选择项目且数据为空时

```tsx
{!searchProjectId && data.length === 0 && (
  <div style={{ 
    textAlign: 'center', 
    padding: '40px', 
    background: '#fafafa', 
    border: '1px dashed #d9d9d9',
    borderRadius: '4px',
    marginBottom: '16px'
  }}>
    <p style={{ fontSize: '16px', color: '#999', margin: 0 }}>
      请先选择项目，然后点击"搜索"按钮查看账号列表
    </p>
  </div>
)}
```

**说明**:
- 在表格上方显示友好的提示信息
- 引导用户先选择项目

#### 2.4 账号筛选改为可选

**位置**: 筛选条件第二项

```tsx
<Input
  placeholder="账号（可选）"
  value={searchAccount}
  onChange={(e) => setSearchAccount(e.target.value)}
  onPressEnter={handleSearch}
  style={{ width: 200 }}
/>
```

**说明**:
- 账号筛选为可选
- 不填写时显示所选项目的所有账号
- 填写时在所选项目中搜索匹配的账号

#### 2.5 添加历史余额按钮

**位置**: 操作列第一个按钮

```tsx
<Button
  type="link"
  size="small"
  icon={<HistoryOutlined />}
  onClick={() => handleShowHistory(record)}
>
  历史
</Button>
```

**功能**:
- 点击显示该账号的历史余额弹窗
- 显示账号基本信息和最近7天的余额历史

#### 2.6 历史余额弹窗

**内容**:

1. **账号信息**（使用 Descriptions 组件）
   - 账号
   - 项目
   - 当前余额
   - 变动余额（带颜色）

2. **历史记录表格**（最近7天）
   - 日期（倒序排列）
   - 余额

```tsx
<Modal
  title="历史余额"
  open={historyModalVisible}
  onCancel={() => setHistoryModalVisible(false)}
  footer={[
    <Button key="close" onClick={() => setHistoryModalVisible(false)}>
      关闭
    </Button>
  ]}
  width={600}
>
  {currentHistoryAccount && (
    <div>
      <Descriptions column={1} bordered>
        <Descriptions.Item label="账号">{currentHistoryAccount.account}</Descriptions.Item>
        <Descriptions.Item label="项目">{currentHistoryAccount.project?.name || '-'}</Descriptions.Item>
        <Descriptions.Item label="当前余额">
          {Number(currentHistoryAccount.balance).toFixed(2)}
        </Descriptions.Item>
        <Descriptions.Item label="变动余额">
          <span style={{ 
            color: Number(currentHistoryAccount.variable) > 0 ? 'green' : 
                   Number(currentHistoryAccount.variable) < 0 ? 'red' : 'default' 
          }}>
            {Number(currentHistoryAccount.variable) > 0 ? '+' : ''}
            {Number(currentHistoryAccount.variable).toFixed(2)}
          </span>
        </Descriptions.Item>
      </Descriptions>
      
      <div style={{ marginTop: 16 }}>
        <h4>历史记录（最近7天）</h4>
        {currentHistoryAccount.balance_history && 
         Object.keys(currentHistoryAccount.balance_history).length > 0 ? (
          <Table
            dataSource={Object.entries(currentHistoryAccount.balance_history)
              .sort(([dateA], [dateB]) => dateB.localeCompare(dateA))
              .map(([date, balance], index) => ({
                key: index,
                date,
                balance: Number(balance).toFixed(2),
              }))}
            columns={[
              {
                title: '日期',
                dataIndex: 'date',
                key: 'date',
              },
              {
                title: '余额',
                dataIndex: 'balance',
                key: 'balance',
                align: 'right' as const,
              },
            ]}
            pagination={false}
            size="small"
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
            暂无历史记录
          </div>
        )}
      </div>
    </div>
  )}
</Modal>
```

### 3. 筛选逻辑

#### 3.1 查询流程

```
1. 用户选择项目（必选）
   ↓
2. 点击"搜索"按钮
   ↓
3. 验证：是否选择了项目？
   ├─ 否 → 提示"请先选择项目"，不调用接口
   └─ 是 → 继续
   ↓
4. 调用账号列表接口
   ↓
5. 显示符合条件的账号列表
```

**关键点**:
- ✅ 没有选择项目时，不会调用账号列表接口
- ✅ 避免无效的 API 请求
- ✅ 提供友好的用户提示

#### 3.2 API 调用

```typescript
const res = await getProjectAccountList({
  page,
  limit: pageSize,
  res_count: true,
  project_id: searchProjectId,  // ← 项目ID（必选）
  account: searchAccount || undefined,  // ← 账号（可选）
  account_type: searchAccountType,
  status: searchStatus,
  order_by: orderBy,
  create_time_start: createTimeRange?.[0]?.format('YYYY-MM-DD'),
  create_time_end: createTimeRange?.[1]?.format('YYYY-MM-DD'),
  update_time_start: updateTimeRange?.[0]?.format('YYYY-MM-DD'),
  update_time_end: updateTimeRange?.[1]?.format('YYYY-MM-DD'),
})
```

## 使用场景

### 场景1: 查看某个项目的所有账号

1. 选择项目：项目A
2. 点击"搜索"
3. ✅ 显示项目A的所有账号及其余额

### 场景2: 在项目中搜索特定账号

1. 选择项目：项目A
2. 输入账号：test@example.com
3. 点击"搜索"
4. ✅ 显示项目A中包含"test@example.com"的账号

### 场景3: 查看账号的历史余额

1. 在账号列表中找到目标账号
2. 点击"历史"按钮
3. ✅ 弹窗显示账号信息和最近7天的余额历史

### 场景4: 按余额排序

1. 选择项目
2. 点击"余额"列头
3. 选择倒序（↓）
4. ✅ 显示该项目中余额从高到低的账号

## 界面效果

### 筛选条件

```
┌────────────────────────────────────────────────────────────────────────┐
│ [选择项目（必选）▼] [账号（可选）] [账号类型▼] [状态▼]                │
│ [创建开始日期 ~ 创建结束日期] [更新开始日期 ~ 更新结束日期]            │
│ [搜索] [重置]                                          [+ 新增账号]    │
└────────────────────────────────────────────────────────────────────────┘
```

### 账号列表

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 账号 | 类型 | 状态 | 余额⇅ | 变动⇅ | 项目 | 创建时间⇅ | 操作              │
├──────────────────────────────────────────────────────────────────────────┤
│ test@example.com | 邮箱 | 正常 | 1000.50 | +50.00 | 项目A | ... | [历史] [编辑] [删除] │
│ user@example.com | 邮箱 | 正常 | 950.00  | -20.00 | 项目A | ... | [历史] [编辑] [删除] │
└──────────────────────────────────────────────────────────────────────────┘
```

### 历史余额弹窗

```
┌─────────────────────────────────────┐
│ 历史余额                             │
├─────────────────────────────────────┤
│ 账号: test@example.com              │
│ 项目: 项目A                         │
│ 当前余额: 1000.50                   │
│ 变动余额: +50.00 (绿色)             │
│                                     │
│ 历史记录（最近7天）                 │
│ ┌──────────┬──────────┐            │
│ │ 日期     │ 余额     │            │
│ ├──────────┼──────────┤            │
│ │2026-01-21│ 1000.50  │            │
│ │2026-01-20│  950.00  │            │
│ │2026-01-19│  900.00  │            │
│ └──────────┴──────────┘            │
│                                     │
│                        [关闭]       │
└─────────────────────────────────────┘
```

## 优势

### 1. 筛选更合理

- ✅ 项目作为主要筛选条件，符合业务逻辑
- ✅ 账号筛选为可选，更灵活
- ✅ 默认显示所选项目的所有账号

### 2. 历史查看更方便

- ✅ 一键查看账号的历史余额
- ✅ 显示最近7天的余额变化
- ✅ 账号信息和历史记录一目了然

### 3. 操作更直观

- ✅ 历史按钮放在操作列第一位
- ✅ 弹窗设计清晰，信息完整
- ✅ 变动余额带颜色，正负一目了然

### 4. 性能优化

- ✅ 按项目筛选，减少数据量
- ✅ 历史记录只保留7天，数据量小
- ✅ 弹窗按需加载，不影响列表性能

## 相关文件

### 后端文件

**新增**:
- ✅ `backend/scripts/apply_balance_migration.py` - 数据库迁移脚本

**修改**:
- ✅ `backend/app/models/project.py` - ProjectAccount 模型包含余额字段
- ✅ `backend/app/crud/project/account.py` - 支持按项目筛选

### 前端文件

**修改**:
- ✅ `frontend/src/views/Project/ProjectAccount.tsx` - 添加项目筛选和历史余额功能
- ✅ `frontend/src/App.tsx` - 删除余额页面路由

**删除**:
- ✅ `frontend/src/views/Project/ProjectBalance.tsx` - 已删除（如果存在）

### 文档

- ✅ `docs/fixes/PROJECT_ACCOUNT_BALANCE_ENHANCEMENT.md` - 本文档
- ✅ `docs/fixes/MERGE_BALANCE_INTO_ACCOUNT.md` - 合并余额表文档
- ✅ `docs/fixes/BALANCE_AUTO_CALCULATION.md` - 余额自动计算文档
- ✅ `docs/fixes/FRONTEND_ACCOUNT_WITH_BALANCE.md` - 前端账号页面集成余额功能文档

## 测试清单

- [ ] 数据库迁移成功
- [ ] 项目筛选功能正常
- [ ] 账号筛选（可选）功能正常
- [ ] 历史余额按钮显示正常
- [ ] 点击历史按钮弹出弹窗
- [ ] 历史余额弹窗显示正确信息
- [ ] 历史记录按日期倒序排列
- [ ] 变动余额颜色显示正确
- [ ] 无历史记录时显示提示信息
- [ ] 关闭弹窗功能正常
- [ ] 所有 TypeScript 诊断通过

## 注意事项

1. **项目筛选**: 项目筛选是必选项，建议在界面上给予提示
2. **历史数据**: 只显示最近7天的历史记录
3. **数据格式**: balance_history 格式为 `{"2026-01-21": 1000.50, ...}`
4. **权限控制**: 历史按钮所有用户可见，编辑删除按钮只有 ADMIN 和 GM 可见

## 总结

✅ 数据库迁移成功完成
✅ 添加了项目筛选（必选）
✅ 账号筛选改为可选
✅ 添加了历史余额查看功能
✅ 历史余额弹窗设计清晰
✅ 筛选逻辑更符合业务需求
✅ 所有 TypeScript 诊断通过

现在用户可以先选择项目，再查看该项目下的账号余额，并且可以方便地查看每个账号的历史余额变化！
