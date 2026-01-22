# 项目人员管理功能

## 实现时间
2026-01-22

## 功能概述

实现了项目与人员的关联管理功能，允许ADMIN和GM角色管理项目的人员分配。

## 功能特性

### 1. 权限控制
- ✅ 只有ADMIN和GM角色可以管理项目人员
- ✅ 其他角色只能查看自己关联的项目
- ✅ 人员关联后，可以查看和管理该项目的数据

### 2. 界面功能

#### 项目列表页面增强
- **新增列**：关联人员列，显示项目关联的所有人员
  - 显示人员昵称或邮箱
  - 使用蓝色标签展示
  - 未分配人员显示灰色提示

- **新增按钮**：管理人员按钮（只对ADMIN和GM显示）
  - 图标：TeamOutlined
  - 位置：操作列第一个按钮
  - 点击打开人员管理弹窗

#### 人员管理弹窗
- **穿梭框组件**：使用Ant Design的Transfer组件
  - 左侧：可选人员列表
  - 右侧：已关联人员列表
  - 支持搜索功能（按昵称或邮箱）
  - 支持批量选择和移动

- **人员信息展示**：
  - 主标题：昵称或邮箱
  - 副标题：邮箱地址
  - 清晰的视觉层次

- **操作按钮**：
  - 保存：提交人员关联更改
  - 取消：关闭弹窗，不保存更改

## 实现细节

### 前端实现

#### 1. 状态管理
```typescript
// 人员管理相关状态
const [userModalVisible, setUserModalVisible] = useState(false)
const [managingProject, setManagingProject] = useState<Project | null>(null)
const [allUsers, setAllUsers] = useState<User[]>([])
const [selectedUserKeys, setSelectedUserKeys] = useState<string[]>([])
const [userLoading, setUserLoading] = useState(false)
```

#### 2. 核心函数

**打开人员管理弹窗**：
```typescript
const handleManageUsers = async (record: Project) => {
  setManagingProject(record)
  setUserLoading(true)
  setUserModalVisible(true)
  
  try {
    // 获取所有用户
    const usersRes = await getUserList({ page: 1, limit: 1000 })
    setAllUsers(usersRes.items || [])
    
    // 设置当前项目已关联的用户
    const currentUserIds = record.users?.map(u => u.id) || []
    setSelectedUserKeys(currentUserIds)
  } catch (error) {
    message.error('获取用户列表失败')
  } finally {
    setUserLoading(false)
  }
}
```

**保存人员关联**：
```typescript
const handleSaveUsers = async () => {
  if (!managingProject) return
  
  try {
    setUserLoading(true)
    await updateProject(managingProject.id, {
      user_ids: selectedUserKeys,
    })
    message.success('人员关联更新成功')
    setUserModalVisible(false)
    fetchData()
  } catch (error) {
    message.error('更新失败')
  } finally {
    setUserLoading(false)
  }
}
```

#### 3. UI组件

**关联人员列**：
```typescript
{
  title: '关联人员',
  dataIndex: 'users',
  key: 'users',
  render: (users: any[]) => (
    <Space size={[0, 4]} wrap>
      {users && users.length > 0 ? (
        users.map(user => (
          <Tag key={user.id} color="blue">
            {user.nickname || user.email}
          </Tag>
        ))
      ) : (
        <span style={{ color: '#999' }}>未分配</span>
      )}
    </Space>
  ),
}
```

**穿梭框组件**：
```typescript
<Transfer
  dataSource={allUsers.map(user => ({
    key: user.id,
    title: user.nickname || user.email,
    description: user.email,
  }))}
  titles={['可选人员', '已关联人员']}
  targetKeys={selectedUserKeys}
  onChange={setSelectedUserKeys}
  render={item => (
    <div>
      <div style={{ fontWeight: 500 }}>{item.title}</div>
      <div style={{ fontSize: 12, color: '#999' }}>{item.description}</div>
    </div>
  )}
  listStyle={{
    width: 300,
    height: 400,
  }}
  showSearch
  filterOption={(inputValue, item) =>
    item.title.toLowerCase().includes(inputValue.toLowerCase()) ||
    item.description.toLowerCase().includes(inputValue.toLowerCase())
  }
  locale={{
    itemUnit: '人',
    itemsUnit: '人',
    searchPlaceholder: '搜索人员',
    notFoundContent: '无数据',
  }}
/>
```

### 后端支持

#### Schema定义
```python
class Update(BaseModel):
    """更新项目请求模型，支持部分更新"""
    name: str | None = Field(None, description="项目名称")
    status: ProjectStatus | None = Field(None, description="项目状态")
    content: str | None = Field(None, description="项目内容")
    user_ids: List[UUID] | None = Field(None, description="关联的用户ID列表")
```

#### CRUD实现
```python
async def update(self, id: UUID, item: dict | Update) -> Out:
    from app.models.user import UserInfo
    
    # ... 更新基本字段 ...
    
    # 处理多对多关系
    if user_ids is not None:
        await res.users.clear()
        if user_ids:
            # 获取UserInfo对象
            users = await UserInfo.filter(id__in=user_ids).all()
            if users:
                await res.users.add(*users)
    
    await res.fetch_related('users')
    return Out.model_validate(res)
```

## 使用流程

### 1. 查看项目人员
1. 进入项目列表页面
2. 在"关联人员"列查看每个项目的人员分配情况
3. 未分配人员的项目显示"未分配"

### 2. 管理项目人员（ADMIN/GM）
1. 点击项目操作列的"管理人员"按钮
2. 在弹窗中查看当前关联的人员（右侧列表）
3. 从左侧列表选择要添加的人员，点击右箭头添加
4. 从右侧列表选择要移除的人员，点击左箭头移除
5. 使用搜索框快速查找人员
6. 点击"保存"按钮提交更改

### 3. 数据权限生效
1. 人员关联后，该人员可以查看该项目的数据
2. 人员可以在仪表盘和项目列表中看到关联的项目
3. 人员可以查看该项目的账号、钱包等信息

## 技术要点

### 1. 穿梭框组件
- 使用Ant Design的Transfer组件
- 支持搜索、批量操作
- 自定义渲染项，显示更多信息
- 中文本地化配置

### 2. 权限控制
- 前端：通过`hasPermission`检查用户角色
- 后端：通过`check_data_permission`过滤数据
- 只有ADMIN和GM可以看到"管理人员"按钮

### 3. 数据同步
- 保存后自动刷新项目列表
- 显示最新的人员关联信息
- 错误处理和用户提示

### 4. 用户体验
- 加载状态提示
- 操作成功/失败提示
- 搜索功能提升效率
- 清晰的视觉反馈

## 相关文件

### 前端文件
- `frontend/src/views/Project/ProjectList.tsx` - 项目列表页面（主要修改）
- `frontend/src/types/index.ts` - 类型定义
- `frontend/src/api/project.ts` - 项目API

### 后端文件
- `backend/app/schemas/project/info.py` - 项目Schema
- `backend/app/crud/project/info.py` - 项目CRUD
- `backend/app/apis/v1/project/info.py` - 项目API
- `backend/app/models/project.py` - 项目模型

## 测试场景

### 1. 基本功能测试
- ✅ ADMIN可以看到"管理人员"按钮
- ✅ GM可以看到"管理人员"按钮
- ✅ 其他角色看不到"管理人员"按钮
- ✅ 点击按钮打开人员管理弹窗
- ✅ 弹窗显示所有用户和当前关联的用户

### 2. 人员操作测试
- ✅ 可以添加人员到项目
- ✅ 可以从项目移除人员
- ✅ 可以批量添加/移除人员
- ✅ 搜索功能正常工作
- ✅ 保存后数据正确更新

### 3. 数据权限测试
- ✅ 关联人员后，该人员可以看到项目
- ✅ 移除人员后，该人员看不到项目
- ✅ ADMIN和GM始终可以看到所有项目
- ✅ 数据权限过滤正常工作

### 4. 边界情况测试
- ✅ 项目没有关联人员时显示"未分配"
- ✅ 清空所有人员后保存成功
- ✅ 网络错误时显示友好提示
- ✅ 并发操作时数据一致性

## 扩展建议

### 1. 批量操作
可以添加批量管理人员的功能：
- 批量分配人员到多个项目
- 批量移除人员从多个项目
- 导入/导出人员分配关系

### 2. 人员角色
可以为项目人员添加角色：
- 项目负责人
- 项目成员
- 项目观察者
- 不同角色有不同的权限

### 3. 操作日志
记录人员分配的操作日志：
- 谁在什么时候添加了谁
- 谁在什么时候移除了谁
- 便于审计和追溯

### 4. 通知功能
人员分配变更时发送通知：
- 被添加到项目时收到通知
- 被移除时收到通知
- 邮件或站内信通知

## 总结

项目人员管理功能已完整实现：
- ✅ 直观的穿梭框界面
- ✅ 完善的权限控制
- ✅ 实时的数据同步
- ✅ 友好的用户体验
- ✅ 与数据权限系统集成

该功能使得项目人员的分配和管理变得简单高效，为团队协作提供了良好的支持。
