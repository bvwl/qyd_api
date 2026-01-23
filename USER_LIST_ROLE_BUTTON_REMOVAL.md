# 用户列表角色按钮移除

## 修改说明

移除了用户列表中的"角色"操作按钮，因为在编辑用户时也可以修改角色，避免功能重复。

## 修改内容

### 文件: `frontend/src/views/User/UserList.tsx`

#### 1. 移除导入
```typescript
// 移除前
import { TeamOutlined, ... } from '@ant-design/icons'
import { getUserRoles, assignUserRoles, ... } from '@/api/user'

// 移除后
// 不再导入 TeamOutlined, getUserRoles, assignUserRoles
```

#### 2. 移除状态变量
```typescript
// 移除以下状态
const [roleModalVisible, setRoleModalVisible] = useState(false)
const [selectedUser, setSelectedUser] = useState<User | null>(null)
const [selectedRoles, setSelectedRoles] = useState<string[]>([])
const [roleLoading, setRoleLoading] = useState(false)
```

#### 3. 移除函数
```typescript
// 移除以下函数
handleManageRoles()  // 打开角色管理弹窗
handleSaveRoles()    // 保存角色分配
```

#### 4. 移除操作列中的角色按钮
```typescript
// 移除前
<Space>
  {isAdmin && (
    <Button icon={<TeamOutlined />} onClick={() => handleManageRoles(record)}>
      角色
    </Button>
  )}
  <Button icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
  <Button icon={<DeleteOutlined />} onClick={() => handleDelete(record)}>删除</Button>
</Space>

// 移除后
<Space>
  <Button icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
  <Button icon={<DeleteOutlined />} onClick={() => handleDelete(record)}>删除</Button>
</Space>
```

#### 5. 移除角色管理弹窗
```typescript
// 移除整个角色管理 Modal 组件
```

## 保留的功能

用户角色管理功能仍然可以通过以下方式使用：

1. **编辑用户时修改角色**
   - 点击用户列表中的"编辑"按钮
   - 在编辑表单中有"角色"下拉选择框
   - 可以多选角色
   - 保存后角色立即生效

2. **创建用户时分配角色**
   - 点击"新增用户"按钮
   - 在创建表单中选择角色
   - 创建用户的同时分配角色

## 优势

1. **简化界面**: 减少操作按钮，界面更简洁
2. **避免重复**: 不需要两个地方都能修改角色
3. **统一体验**: 所有用户信息（包括角色）都在编辑界面统一管理
4. **减少代码**: 移除了约100行代码，降低维护成本

## 测试

1. 打开用户列表页面
2. 验证操作列只有"编辑"和"删除"按钮
3. 点击"编辑"按钮
4. 验证可以在编辑表单中修改角色
5. 保存后验证角色更新成功

---

**修改时间**: 2026-01-23  
**修改状态**: ✅ 完成
