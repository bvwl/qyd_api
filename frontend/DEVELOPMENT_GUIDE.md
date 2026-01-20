# 开发指南

## 快速开始

### 1. 克隆项目并安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:3000

## 开发流程

### 新增一个列表页面

以"项目列表"为例：

#### 步骤 1：创建页面组件

```tsx
// src/views/Project/ProjectList.tsx
import { useState, useEffect } from 'react'
import { Table, Button, Space } from 'antd'
import { getProjectList } from '@/api/project'
import type { Project } from '@/types'

export default function ProjectList() {
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<Project[]>([])
  
  const fetchData = async () => {
    try {
      setLoading(true)
      const res = await getProjectList({ page: 1, limit: 10 })
      setDataSource(res.items || [])
    } catch (error) {
      setDataSource([])
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    fetchData()
  }, [])
  
  const columns = [
    { title: '项目名称', dataIndex: 'name', key: 'name' },
    { title: '状态', dataIndex: 'status', key: 'status' },
    // ... 其他列
  ]
  
  return (
    <div>
      <Table
        loading={loading}
        dataSource={dataSource}
        columns={columns}
        rowKey="id"
      />
    </div>
  )
}
```

#### 步骤 2：添加路由

```tsx
// src/router/index.tsx
import ProjectList from '@/views/Project/ProjectList'

// 在 children 中添加
{
  path: 'project/list',
  element: <ProjectList />,
}
```

#### 步骤 3：添加菜单（已在 Layout 中定义）

菜单项已经在 `src/components/Layout/index.tsx` 中定义好了，点击即可跳转。

### 新增一个表单页面

#### 步骤 1：创建表单组件

```tsx
// src/views/Project/ProjectForm.tsx
import { Form, Input, Button, message } from 'antd'
import { createProject } from '@/api/project'

export default function ProjectForm() {
  const [form] = Form.useForm()
  
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      await createProject(values)
      message.success('创建成功')
    } catch (error) {
      message.error('创建失败')
    }
  }
  
  return (
    <Form form={form} layout="vertical">
      <Form.Item
        name="name"
        label="项目名称"
        rules={[{ required: true, message: '请输入项目名称' }]}
      >
        <Input placeholder="请输入项目名称" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" onClick={handleSubmit}>
          提交
        </Button>
      </Form.Item>
    </Form>
  )
}
```

## 常用代码片段

### API 调用

```tsx
import { getUserList } from '@/api/user'

// 基础调用
const res = await getUserList()

// 带参数
const res = await getUserList({
  page: 1,
  limit: 10,
  email: 'test@example.com',
  status: 1,
})

// 错误处理（已在拦截器中统一处理）
try {
  const res = await getUserList()
  // 处理数据
} catch (error) {
  // 错误已自动提示，这里可以做额外处理
}
```

### 状态管理

```tsx
import { useUserStore } from '@/store/useUserStore'

function MyComponent() {
  // 获取状态
  const { userInfo, isLoggedIn } = useUserStore()
  
  // 获取方法
  const { login, logout } = useUserStore()
  
  // 使用
  const handleLogin = async () => {
    await login('email@example.com', 'password')
  }
  
  return <div>{userInfo?.nickname}</div>
}
```

### 表格列定义

```tsx
import type { ColumnsType } from 'antd/es/table'
import { Tag, Space, Button } from 'antd'
import { formatDateTime } from '@/utils/format'
import { USER_STATUS_MAP } from '@/utils/constants'

const columns: ColumnsType<User> = [
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    render: (status: UserStatus) => {
      const config = USER_STATUS_MAP[status]
      return <Tag color={config.color}>{config.text}</Tag>
    },
  },
  {
    title: '创建时间',
    dataIndex: 'create_time',
    key: 'create_time',
    render: (text: string) => formatDateTime(text),
  },
  {
    title: '操作',
    key: 'action',
    render: (_, record) => (
      <Space>
        <Button type="link" onClick={() => handleEdit(record)}>
          编辑
        </Button>
        <Button type="link" danger onClick={() => handleDelete(record)}>
          删除
        </Button>
      </Space>
    ),
  },
]
```

### 表单验证

```tsx
<Form form={form} layout="vertical">
  <Form.Item
    name="email"
    label="邮箱"
    rules={[
      { required: true, message: '请输入邮箱' },
      { type: 'email', message: '请输入有效的邮箱地址' },
    ]}
  >
    <Input placeholder="请输入邮箱" />
  </Form.Item>
  
  <Form.Item
    name="password"
    label="密码"
    rules={[
      { required: true, message: '请输入密码' },
      { min: 6, message: '密码至少6位' },
    ]}
  >
    <Input.Password placeholder="请输入密码" />
  </Form.Item>
</Form>
```

### 弹窗使用

```tsx
import { Modal, message } from 'antd'

// 确认弹窗
Modal.confirm({
  title: '确认删除',
  content: '确定要删除这条记录吗？',
  onOk: async () => {
    await deleteUser(id)
    message.success('删除成功')
  },
})

// 表单弹窗
const [modalVisible, setModalVisible] = useState(false)

<Modal
  title="新增用户"
  open={modalVisible}
  onOk={handleSubmit}
  onCancel={() => setModalVisible(false)}
>
  <Form form={form}>
    {/* 表单内容 */}
  </Form>
</Modal>
```

## 工具函数

### 格式化函数

```tsx
import { formatDateTime, formatDate, maskEmail, maskPassword } from '@/utils/format'

// 格式化日期时间
formatDateTime('2024-01-01 12:00:00') // 2024-01-01 12:00:00

// 格式化日期
formatDate('2024-01-01 12:00:00') // 2024-01-01

// 脱敏邮箱
maskEmail('test@example.com') // te***t@example.com

// 脱敏密码
maskPassword('123456') // ******
```

### 常量使用

```tsx
import { USER_STATUS_MAP, PROJECT_STATUS_MAP, STATUS_MAP } from '@/utils/constants'

// 获取状态配置
const config = USER_STATUS_MAP[UserStatus.NORMAL]
// { text: '正常', color: 'success' }

// 渲染标签
<Tag color={config.color}>{config.text}</Tag>

// 渲染下拉选项
<Select>
  {Object.entries(USER_STATUS_MAP).map(([key, value]) => (
    <Select.Option key={key} value={Number(key)}>
      {value.text}
    </Select.Option>
  ))}
</Select>
```

## 调试技巧

### 查看 API 请求

打开浏览器开发者工具 -> Network 标签，可以看到所有 API 请求。

### 查看状态

```tsx
import { useUserStore } from '@/store/useUserStore'

function DebugComponent() {
  const state = useUserStore()
  console.log('当前状态：', state)
  return null
}
```

### 查看类型定义

在 VSCode 中，按住 Ctrl（Mac: Cmd）点击类型名称，可以跳转到类型定义。

## 常见问题

### Q: API 请求返回 404

A: 检查后端服务是否启动，访问 http://127.0.0.1:6080/docs 查看 API 文档。

### Q: 类型错误

A: 确保导入了正确的类型，使用 `import type { User } from '@/types'`。

### Q: 路由不生效

A: 检查路由配置是否正确，确保路径以 `/` 开头。

### Q: 样式不生效

A: 确保导入了样式文件，Less 文件需要在组件中导入。

## 最佳实践

1. **使用 TypeScript**：所有变量都应该有类型
2. **使用 Hooks**：优先使用函数式组件
3. **拆分组件**：单个组件不超过 300 行
4. **统一错误处理**：使用拦截器统一处理
5. **代码复用**：抽取公共逻辑到 hooks 或工具函数

## 性能优化

1. **使用 React.memo**：避免不必要的重渲染
2. **使用 useMemo**：缓存计算结果
3. **使用 useCallback**：缓存函数引用
4. **路由懒加载**：使用 `React.lazy` 和 `Suspense`

## 下一步

查看 [README.md](./README.md) 了解完整文档。
