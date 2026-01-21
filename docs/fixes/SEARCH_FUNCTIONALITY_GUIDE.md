# 搜索功能添加指南

## 概述
为所有列表页面添加条件查询功能，提升用户体验。

## 搜索功能设计

### 通用搜索组件结构
```typescript
// 1. 添加搜索状态
const [searchField1, setSearchField1] = useState('')
const [searchField2, setSearchField2] = useState<number>()

// 2. 修改fetchData函数，添加搜索参数
const fetchData = async () => {
  const res = await getList({
    page,
    limit: pageSize,
    res_count: true,
    field1: searchField1 || undefined,
    field2: searchField2,
  })
}

// 3. 添加搜索和重置函数
const handleSearch = () => {
  setPage(1)
  fetchData()
}

const handleReset = () => {
  setSearchField1('')
  setSearchField2(undefined)
  setPage(1)
  setTimeout(() => {
    fetchData()
  }, 0)
}

// 4. 添加搜索UI
<Space style={{ marginBottom: '16px' }}>
  <Input
    placeholder="字段1"
    value={searchField1}
    onChange={(e) => setSearchField1(e.target.value)}
    onPressEnter={handleSearch}
    style={{ width: 200 }}
  />
  <Select
    placeholder="字段2"
    value={searchField2}
    onChange={setSearchField2}
    style={{ width: 120 }}
    allowClear
  >
    <Select.Option value={1}>选项1</Select.Option>
    <Select.Option value={2}>选项2</Select.Option>
  </Select>
  <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
    搜索
  </Button>
  <Button onClick={handleReset}>重置</Button>
</Space>
```

## 各页面搜索字段

### 用户管理

#### 1. 角色管理 (RoleList)
- ✅ 角色名称 (name) - Input
- ✅ 角色标识 (code) - Input

#### 2. 路由管理 (RouteList)
- ✅ 路由名称 (name) - Input
- ✅ 路由路径 (path) - Input
- ✅ 状态 (status) - Select

#### 3. Token管理 (TokenList)
- 用户ID (user_id) - Select
- 状态 (status) - Select

#### 4. 操作日志 (LogList)
- ✅ 用户ID (user_id) - Input (已实现)
- 操作类型 (action) - Select

### 项目管理

#### 1. 项目列表 (ProjectList)
- 项目名称 (name) - Input
- 状态 (status) - Select

#### 2. 项目账号 (ProjectAccount)
- 账号 (account) - Input
- 账号类型 (account_type) - Select
- 状态 (status) - Select
- 项目 (project_id) - Select

#### 3. 项目钱包 (ProjectWallet)
- 链 (chain) - Input
- 项目 (project_id) - Select

#### 4. 项目余额 (ProjectBalance)
- 账号 (account_id) - Select

### 服务器管理

#### 1. 国家管理 (CountryList)
- 简称 (short_name) - Input
- 国家名称 (name) - Input
- 状态 (status) - Select

#### 2. 分组管理 (GroupList)
- 分组名称 (name) - Input
- 国家 (country_id) - Select
- 状态 (status) - Select

#### 3. 服务器列表 (ServerList)
- 主机地址 (host) - Input
- 分组 (group_id) - Select
- 状态 (status) - Select
- 是否出售 (is_sale) - Select

#### 4. 服务器账号 (ServerAccount)
- 用户名 (username) - Input
- 用户 (user_id) - Select

### 邮箱管理

#### 1. 邮箱列表 (MailList)
- ✅ 邮箱 (email) - Input (已实现)
- ✅ 状态 (status) - Select (已实现)
- ✅ 邮箱类型 (email_type) - Select (已实现)

## 实现优先级

### 高优先级（核心搜索）
1. ✅ 角色管理 - 名称、标识
2. ✅ 路由管理 - 名称、路径、状态
3. Token管理 - 用户、状态
4. 项目列表 - 名称、状态
5. 项目账号 - 账号、类型、状态
6. 服务器列表 - 主机、分组、状态
7. 国家管理 - 名称、简称

### 中优先级（辅助搜索）
1. 分组管理 - 名称、国家
2. 服务器账号 - 用户名
3. 项目钱包 - 链
4. 项目余额 - 账号

### 低优先级（可选）
1. 操作日志 - 操作类型（已有用户ID搜索）

## 搜索UI布局

### 标准布局
```tsx
<div style={{ padding: '24px' }}>
  {/* 搜索区域 */}
  <div style={{ marginBottom: '16px' }}>
    <Space style={{ marginBottom: '16px' }}>
      {/* 搜索字段 */}
      <Input placeholder="..." />
      <Select placeholder="..." />
      {/* 搜索按钮 */}
      <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
        搜索
      </Button>
      <Button onClick={handleReset}>重置</Button>
    </Space>
    {/* 操作按钮 */}
    <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
      新增
    </Button>
  </div>
  
  {/* 表格 */}
  <Table ... />
</div>
```

### 响应式布局（可选）
对于搜索字段较多的页面，可以使用Form布局：
```tsx
<Form layout="inline" style={{ marginBottom: '16px' }}>
  <Form.Item>
    <Input placeholder="..." />
  </Form.Item>
  <Form.Item>
    <Select placeholder="..." />
  </Form.Item>
  <Form.Item>
    <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
      搜索
    </Button>
    <Button onClick={handleReset} style={{ marginLeft: 8 }}>
      重置
    </Button>
  </Form.Item>
</Form>
```

## 搜索逻辑

### 1. 输入框搜索
- 支持回车键触发搜索
- 空值时不传递参数（使用 `|| undefined`）

### 2. 下拉框搜索
- 支持清除选项（`allowClear`）
- 清除后自动触发搜索

### 3. 搜索按钮
- 点击后重置页码到第1页
- 立即触发数据获取

### 4. 重置按钮
- 清空所有搜索条件
- 重置页码到第1页
- 使用setTimeout确保状态更新后再获取数据

## 注意事项

1. **状态管理**
   - 搜索条件作为独立状态管理
   - 不要将搜索条件放入useEffect依赖

2. **API参数**
   - 空字符串转为undefined（`|| undefined`）
   - 数字类型可以直接传递

3. **用户体验**
   - 输入框支持回车搜索
   - 下拉框支持清除
   - 搜索后保持搜索条件显示

4. **性能优化**
   - 避免频繁请求
   - 可以添加防抖（debounce）

## 已完成页面

- ✅ 用户列表 (UserList) - 邮箱、昵称、状态
- ✅ 角色管理 (RoleList) - 名称、标识
- ✅ 路由管理 (RouteList) - 名称、路径、状态
- ✅ 操作日志 (LogList) - 用户ID
- ✅ 邮箱列表 (MailList) - 邮箱、状态、类型

## 待完成页面

需要添加搜索功能的页面：
1. Token管理
2. 项目列表
3. 项目账号
4. 项目钱包
5. 项目余额
6. 国家管理
7. 分组管理
8. 服务器列表
9. 服务器账号

## 示例代码

完整的搜索功能实现示例（以角色管理为例）：

```typescript
import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, message, Space, Popconfirm, Tag } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'

const RoleList = () => {
  // ... 其他状态
  const [searchName, setSearchName] = useState('')
  const [searchCode, setSearchCode] = useState('')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getRoleList({
        page,
        limit: pageSize,
        res_count: true,
        name: searchName || undefined,
        code: searchCode || undefined,
      })
      setData(res.items || [])
      setTotal(res.count || 0)
    } catch (error) {
      console.error('获取角色列表失败:', error)
      message.error('获取角色列表失败')
      setData([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(1)
    fetchData()
  }

  const handleReset = () => {
    setSearchName('')
    setSearchCode('')
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '16px' }}>
        <Space style={{ marginBottom: '16px' }}>
          <Input
            placeholder="角色名称"
            value={searchName}
            onChange={(e) => setSearchName(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 200 }}
          />
          <Input
            placeholder="角色标识"
            value={searchCode}
            onChange={(e) => setSearchCode(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 200 }}
          />
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
            搜索
          </Button>
          <Button onClick={handleReset}>重置</Button>
        </Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增角色
        </Button>
      </div>
      <Table ... />
    </div>
  )
}
```

## 总结

搜索功能是提升用户体验的重要功能，建议：
1. 优先实现核心搜索字段
2. 保持UI一致性
3. 注意性能优化
4. 提供友好的交互体验
