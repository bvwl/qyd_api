# 项目余额按项目搜索功能（级联查询）

## 添加时间
2026-01-21

## 功能描述

在项目余额界面实现严格的级联查询流程：**项目 → 账号 → 余额**

用户必须按照以下步骤操作：
1. **第一步**：选择项目
2. **第二步**：选择该项目下的账号
3. **第三步**：点击搜索查看余额

## 设计理念

### 为什么要级联查询？

1. **数据关系清晰**
   - 余额属于账号
   - 账号属于项目
   - 必须先确定项目，才能查看账号余额

2. **避免数据混乱**
   - 防止查询到不相关项目的余额
   - 确保用户明确知道在查看哪个项目的数据

3. **性能优化**
   - 不加载所有账号，只加载选定项目的账号
   - 减少不必要的数据传输

## 实现方案

### 1. 级联禁用逻辑

```
项目选择器：始终可用
    ↓
账号选择器：项目未选时禁用
    ↓
时间范围：账号未选时禁用
    ↓
搜索按钮：账号未选时禁用
```

### 2. 数据加载流程

```typescript
// 步骤1: 选择项目
选择项目 → 加载该项目的账号列表 → 清空账号选择 → 清空余额数据

// 步骤2: 选择账号
选择账号 → 启用搜索按钮

// 步骤3: 搜索余额
点击搜索 → 加载该账号的余额数据
```

### 3. 代码实现

**修改文件**: `frontend/src/views/Project/ProjectBalance.tsx`

#### 修改账号列表加载函数（必须传入项目ID）

```typescript
const fetchAccountList = async (projectId?: string) => {
  // 必须选择项目才能加载账号
  if (!projectId) {
    setAccountList([])
    return
  }
  
  try {
    const res = await getProjectAccountList({
      page: 1,
      limit: 1000,
      project_id: projectId,  // ← 必须传递项目ID
    })
    setAccountList(res.items || [])
  } catch (error) {
    setAccountList([])
  }
}
```

#### 修改余额加载函数（必须传入账号ID）

```typescript
const fetchData = async () => {
  // 必须选择账号才能查询余额
  if (!searchAccountId) {
    setData([])
    setTotal(0)
    return
  }
  
  setLoading(true)
  try {
    const res = await getProjectBalanceList({
      page,
      limit: pageSize,
      res_count: true,
      account_id: searchAccountId,  // ← 必须传递账号ID
      ...
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

#### 项目选择监听（级联清空）

```typescript
useEffect(() => {
  fetchAccountList(searchProjectId)
  setSearchAccountId(undefined) // 清空账号选择
  setData([]) // 清空余额数据
  setTotal(0)
}, [searchProjectId])
```

#### 界面禁用逻辑

```tsx
<Space wrap>
  {/* 项目选择器 - 始终可用 */}
  <Select
    placeholder="1. 选择项目"
    value={searchProjectId}
    onChange={setSearchProjectId}
    allowClear
    showSearch
    style={{ width: 200 }}
    ...
  />
  
  {/* 账号选择器 - 项目未选时禁用 */}
  <Select
    placeholder="2. 选择账号"
    value={searchAccountId}
    onChange={setSearchAccountId}
    disabled={!searchProjectId}  // ← 禁用逻辑
    allowClear
    showSearch
    style={{ width: 250 }}
    options={accountList.map(account => ({
      label: account.account,  // ← 只显示账号名，不显示项目名
      value: account.id,
    }))}
  />
  
  {/* 时间范围 - 账号未选时禁用 */}
  <RangePicker
    placeholder={['创建开始日期', '创建结束日期']}
    disabled={!searchAccountId}  // ← 禁用逻辑
    ...
  />
  
  {/* 搜索按钮 - 账号未选时禁用 */}
  <Button 
    type="primary" 
    icon={<SearchOutlined />} 
    onClick={() => { setPage(1); fetchData(); }}
    disabled={!searchAccountId}  // ← 禁用逻辑
  >
    搜索
  </Button>
  
  {/* 重置按钮 - 清空所有状态 */}
  <Button onClick={() => { 
    setSearchProjectId(undefined); 
    setSearchAccountId(undefined); 
    setCreateTimeRange(null); 
    setUpdateTimeRange(null); 
    setPage(1); 
    setData([]);  // ← 清空数据
    setTotal(0);
  }}>
    重置
  </Button>
</Space>
```

#### 表格空状态提示

```tsx
<Table
  columns={columns}
  dataSource={data}
  rowKey="id"
  loading={loading}
  locale={{
    emptyText: searchProjectId 
      ? (searchAccountId ? '暂无数据' : '请选择账号查看余额') 
      : '请先选择项目'
  }}
  ...
/>
```

## 使用场景

### 场景1: 查看项目A的某个账号余额

1. 点击"1. 选择项目"，选择"项目A"
2. 账号选择器自动启用，显示项目A的账号列表
3. 点击"2. 选择账号"，选择"account1@example.com"
4. 搜索按钮自动启用
5. 点击"搜索"
6. ✅ 显示该账号的余额

### 场景2: 切换到另一个项目

1. 当前选择：项目A → account1
2. 切换项目到"项目B"
3. ✅ 账号选择自动清空
4. ✅ 余额数据自动清空
5. ✅ 账号列表更新为项目B的账号
6. 重新选择账号并搜索

### 场景3: 清空项目

1. 当前选择：项目A → account1
2. 点击项目选择器的清空按钮
3. ✅ 账号选择器禁用
4. ✅ 账号列表清空
5. ✅ 余额数据清空
6. ✅ 搜索按钮禁用

### 场景4: 使用重置按钮

1. 选择了项目、账号、时间范围
2. 点击"重置"按钮
3. ✅ 所有筛选条件清空
4. ✅ 余额数据清空
5. ✅ 回到初始状态

## 用户界面

### 搜索栏布局

```
┌────────────────────────────────────────────────────────────────────┐
│ [1. 选择项目▼] [2. 选择账号▼] [创建时间] [更新时间] [搜索] [重置]   │
└────────────────────────────────────────────────────────────────────┘
```

### 状态说明

**初始状态**:
- 项目选择器：✅ 可用
- 账号选择器：❌ 禁用（灰色）
- 时间范围：❌ 禁用（灰色）
- 搜索按钮：❌ 禁用（灰色）
- 表格提示："请先选择项目"

**选择项目后**:
- 项目选择器：✅ 可用（已选择）
- 账号选择器：✅ 可用（显示该项目的账号）
- 时间范围：❌ 禁用（灰色）
- 搜索按钮：❌ 禁用（灰色）
- 表格提示："请选择账号查看余额"

**选择账号后**:
- 项目选择器：✅ 可用（已选择）
- 账号选择器：✅ 可用（已选择）
- 时间范围：✅ 可用
- 搜索按钮：✅ 可用（蓝色）
- 表格提示："请点击搜索按钮"

**搜索后**:
- 显示余额数据
- 或显示"暂无数据"

### 交互流程

```
1. 初始状态
   项目: [未选择]
   账号: [禁用] ← 灰色不可点击
   搜索: [禁用] ← 灰色不可点击
   表格: "请先选择项目"

2. 选择项目后
   项目: [项目A]
   账号: [可选择] ← 显示项目A的账号
   搜索: [禁用] ← 还需要选择账号
   表格: "请选择账号查看余额"

3. 选择账号后
   项目: [项目A]
   账号: [account1]
   搜索: [可点击] ← 蓝色按钮
   表格: "请点击搜索按钮"

4. 点击搜索后
   表格: 显示余额数据
```

## 数据流

### 后端 API

项目账号列表 API 已支持按项目过滤：

```bash
GET /v1/project/account?project_id={project_id}&page=1&limit=1000
```

### 前端调用

```typescript
// 获取所有账号
getProjectAccountList({ page: 1, limit: 1000 })

// 获取特定项目的账号
getProjectAccountList({ 
  page: 1, 
  limit: 1000, 
  project_id: "project-uuid" 
})
```

### 余额查询

余额通过 `account_id` 查询，间接实现按项目查询：

```typescript
// 查询特定账号的余额
getProjectBalanceList({ account_id: "account-uuid" })

// 查询所有余额
getProjectBalanceList({})
```

## 优势

### 1. 数据关系清晰

- ✅ 强制用户按照 项目 → 账号 → 余额 的逻辑查询
- ✅ 避免查询到不相关项目的数据
- ✅ 用户明确知道在查看哪个项目的余额

### 2. 用户体验优化

- ✅ 步骤提示清晰（1. 选择项目，2. 选择账号）
- ✅ 禁用状态明确（灰色表示不可用）
- ✅ 空状态提示友好（告诉用户下一步该做什么）
- ✅ 级联清空避免数据混乱

### 3. 性能优化

- ✅ 不加载所有账号，只加载选定项目的账号
- ✅ 不加载所有余额，只加载选定账号的余额
- ✅ 减少不必要的数据传输和渲染

### 4. 数据安全

- ✅ 防止误查询其他项目的敏感数据
- ✅ 确保用户有明确的查询意图

## 测试场景

### 测试1: 选择项目查看余额

1. 打开项目余额页面
2. 点击"选择项目"下拉框
3. 选择"项目A"
4. 观察账号下拉框是否只显示项目A的账号
5. 点击"搜索"
6. 验证显示的余额都属于项目A的账号

### 测试2: 切换项目

1. 选择"项目A"
2. 选择账号"account1"
3. 切换到"项目B"
4. 验证账号选择被清空
5. 验证账号列表只显示项目B的账号

### 测试3: 清空项目

1. 选择"项目A"
2. 点击项目选择器的清空按钮
3. 验证账号列表恢复显示所有账号

### 测试4: 重置功能

1. 选择项目、账号、时间范围
2. 点击"重置"按钮
3. 验证所有筛选条件被清空

## 相关文件

### 前端文件
- ✅ `frontend/src/views/Project/ProjectBalance.tsx` - 余额页面（已修改）
- ✅ `frontend/src/api/project.ts` - API 方法（已有 getProjectList）
- ✅ `frontend/src/types/index.ts` - 类型定义（已有 Project 类型）

### 后端文件（无需修改）
- `backend/app/apis/v1/project/account.py` - 账号 API（已支持 project_id 过滤）
- `backend/app/apis/v1/project/balance.py` - 余额 API

### 文档
- ✅ `docs/fixes/PROJECT_BALANCE_SEARCH_BY_PROJECT.md` - 本文档

## 总结

✅ 实现了严格的级联查询：项目 → 账号 → 余额
✅ 添加了禁用逻辑，引导用户按步骤操作
✅ 优化了空状态提示，告诉用户下一步该做什么
✅ 级联清空避免数据混乱
✅ 性能优化，只加载必要的数据
✅ 数据关系清晰，符合业务逻辑
✅ 无需修改后端代码

现在用户必须按照 **项目 → 账号 → 余额** 的流程查询，数据关系更清晰！
