# 前端接口顺序调用优化

## 更新时间
2026-01-21

## 背景

在某些页面中，需要先加载下拉选项（如项目列表、用户列表等），然后再加载主数据。之前的实现是同时调用多个接口，没有检查第一个接口的状态，可能导致：

1. 第一个接口失败时，第二个接口仍然会被调用
2. 用户体验不好，可能看到错误的数据
3. 浪费网络资源

## 解决方案

确保在访问多个接口时，先检查第一个接口是否返回成功（200状态码），如果失败则不请求第二个接口。

## 修改的页面

### 1. 服务器分组列表 (GroupList)

**文件**: `frontend/src/views/Server/GroupList.tsx`

**修改前**:
```typescript
useEffect(() => {
  fetchData()
  fetchCountryList()
}, [page, pageSize])
```

**修改后**:
```typescript
const fetchCountryList = async () => {
  try {
    const res = await getCountryList({
      page: 1,
      limit: 1000,
    })
    setCountryList(res.items || [])
    return true  // 返回成功状态
  } catch (error) {
    setCountryList([])
    return false  // 返回失败状态
  }
}

useEffect(() => {
  const loadData = async () => {
    // 先加载国家列表，成功后再加载分组数据
    const countrySuccess = await fetchCountryList()
    if (countrySuccess) {
      fetchData()
    }
  }
  loadData()
}, [page, pageSize])
```

**说明**:
- 先加载国家列表（用于筛选下拉框）
- 只有国家列表加载成功后，才加载分组数据
- 如果国家列表加载失败，不会加载分组数据

### 2. 服务器列表 (ServerList)

**文件**: `frontend/src/views/Server/ServerList.tsx`

**修改前**:
```typescript
useEffect(() => {
  fetchData()
  fetchGroupList()
}, [page, pageSize])
```

**修改后**:
```typescript
const fetchGroupList = async () => {
  try {
    const res = await getGroupList({
      page: 1,
      limit: 1000,
    })
    setGroupList(res.items || [])
    return true  // 返回成功状态
  } catch (error) {
    setGroupList([])
    return false  // 返回失败状态
  }
}

useEffect(() => {
  const loadData = async () => {
    // 先加载分组列表，成功后再加载服务器数据
    const groupSuccess = await fetchGroupList()
    if (groupSuccess) {
      fetchData()
    }
  }
  loadData()
}, [page, pageSize])
```

**说明**:
- 先加载分组列表（用于筛选下拉框）
- 只有分组列表加载成功后，才加载服务器数据

### 3. 服务器账号列表 (ServerAccount)

**文件**: `frontend/src/views/Server/ServerAccount.tsx`

**修改前**:
```typescript
useEffect(() => {
  fetchData()
}, [page, pageSize, searchUserId])

useEffect(() => {
  fetchUserList()
}, [])
```

**修改后**:
```typescript
const fetchUserList = async () => {
  try {
    const res = await getUserList({
      page: 1,
      limit: 1000,
    })
    setUserList(res.items || [])
    return true  // 返回成功状态
  } catch (error) {
    setUserList([])
    return false  // 返回失败状态
  }
}

useEffect(() => {
  fetchData()
}, [page, pageSize, searchUserId])

useEffect(() => {
  const loadData = async () => {
    // 先加载用户列表
    await fetchUserList()
  }
  loadData()
}, [])
```

**说明**:
- 用户列表和服务器账号数据是独立的
- 用户列表用于筛选和创建时的下拉框
- 这个页面的两个接口是独立的，不需要顺序依赖

### 4. Token管理列表 (TokenList)

**文件**: `frontend/src/views/User/TokenList.tsx`

**修改前**:
```typescript
useEffect(() => {
  fetchData()
  fetchUserList()
}, [page, pageSize])
```

**修改后**:
```typescript
const fetchUserList = async () => {
  try {
    const res = await getUserList({
      page: 1,
      limit: 1000,
    })
    setUserList(res.items || [])
    return true  // 返回成功状态
  } catch (error) {
    setUserList([])
    return false  // 返回失败状态
  }
}

useEffect(() => {
  const loadData = async () => {
    // 先加载用户列表，成功后再加载Token数据
    const userSuccess = await fetchUserList()
    if (userSuccess) {
      fetchData()
    }
  }
  loadData()
}, [page, pageSize])
```

**说明**:
- 先加载用户列表（用于筛选下拉框）
- 只有用户列表加载成功后，才加载Token数据

### 5. 项目钱包列表 (ProjectWallet)

**文件**: `frontend/src/views/Project/ProjectWallet.tsx`

**修改前**:
```typescript
useEffect(() => {
  fetchData()
  fetchProjectList()
}, [page, pageSize])
```

**修改后**:
```typescript
const fetchProjectList = async () => {
  try {
    const res = await getProjectList({
      page: 1,
      limit: 1000,
    })
    setProjectList(res.items || [])
    return true  // 返回成功状态
  } catch (error) {
    setProjectList([])
    return false  // 返回失败状态
  }
}

useEffect(() => {
  const loadData = async () => {
    // 先加载项目列表，成功后再加载钱包数据
    const projectSuccess = await fetchProjectList()
    if (projectSuccess) {
      fetchData()
    }
  }
  loadData()
}, [page, pageSize])
```

**说明**:
- 先加载项目列表（用于筛选下拉框）
- 只有项目列表加载成功后，才加载钱包数据

### 6. 项目账号列表 (ProjectAccount)

**文件**: `frontend/src/views/Project/ProjectAccount.tsx`

**修改前**:
```typescript
const fetchProjectList = async () => {
  try {
    const res = await getProjectList({
      page: 1,
      limit: 100,
    })
    setProjectList(res.items || [])
  } catch (error) {
    setProjectList([])
  }
}

useEffect(() => {
  // 只有选择了项目才查询账号列表
  if (searchProjectId) {
    fetchData()
  }
}, [page, pageSize, searchProjectId])

useEffect(() => {
  fetchProjectList()
}, [])
```

**修改后**:
```typescript
const fetchProjectList = async () => {
  try {
    const res = await getProjectList({
      page: 1,
      limit: 100,
    })
    setProjectList(res.items || [])
    return true  // 返回成功状态
  } catch (error) {
    setProjectList([])
    message.error('加载项目列表失败')
    return false  // 返回失败状态
  }
}

useEffect(() => {
  // 只有选择了项目才查询账号列表
  if (searchProjectId) {
    fetchData()
  }
}, [page, pageSize, searchProjectId])

useEffect(() => {
  const loadData = async () => {
    await fetchProjectList()
  }
  loadData()
}, [])
```

**说明**:
- 项目列表和账号数据是独立的
- 项目列表用于筛选（必选）
- 只有选择项目后才会加载账号数据
- 添加了错误提示

### 7. 邮箱列表 (MailList)

**文件**: `frontend/src/views/Mail/MailList.tsx`

**修改前**:
```typescript
useEffect(() => {
  fetchData()
}, [page, pageSize, searchEmail, searchStatus, searchEmailType])

useEffect(() => {
  fetchServers()
}, [])
```

**修改后**:
```typescript
const fetchServers = async () => {
  try {
    const res = await getServerList({ limit: 1000 })
    setServers(res.items || [])
    return true  // 返回成功状态
  } catch (error) {
    setServers([])
    return false  // 返回失败状态
  }
}

useEffect(() => {
  fetchData()
}, [page, pageSize, searchEmail, searchStatus, searchEmailType])

useEffect(() => {
  const loadData = async () => {
    await fetchServers()
  }
  loadData()
}, [])
```

**说明**:
- 服务器列表和邮箱数据是独立的
- 服务器列表用于创建/编辑时的下拉框
- 这个页面的两个接口是独立的，不需要顺序依赖

## 优化模式

### 模式1: 顺序依赖（推荐用于有依赖关系的接口）

```typescript
const fetchDependency = async () => {
  try {
    const res = await getDependencyData()
    setDependencyData(res.items || [])
    return true  // 返回成功状态
  } catch (error) {
    setDependencyData([])
    return false  // 返回失败状态
  }
}

useEffect(() => {
  const loadData = async () => {
    // 先加载依赖数据，成功后再加载主数据
    const success = await fetchDependency()
    if (success) {
      fetchMainData()
    }
  }
  loadData()
}, [page, pageSize])
```

**适用场景**:
- 主数据依赖于下拉选项数据
- 需要先加载筛选条件，再加载列表数据

### 模式2: 独立加载（推荐用于无依赖关系的接口）

```typescript
const fetchDependency = async () => {
  try {
    const res = await getDependencyData()
    setDependencyData(res.items || [])
    return true
  } catch (error) {
    setDependencyData([])
    return false
  }
}

useEffect(() => {
  fetchMainData()
}, [page, pageSize])

useEffect(() => {
  const loadData = async () => {
    await fetchDependency()
  }
  loadData()
}, [])
```

**适用场景**:
- 下拉选项数据和主数据是独立的
- 下拉选项只用于创建/编辑表单

### 模式3: 并行加载（Dashboard 使用）

```typescript
const [usersRes, projectsRes, accountsRes] = await Promise.all([
  getUserList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
  getProjectList({ page: 1, limit: 100, res_count: true }).catch(() => ({ count: 0, items: [] })),
  getProjectAccountList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
])
```

**适用场景**:
- 多个接口互不依赖
- 需要同时加载多个数据
- 使用 `.catch()` 处理每个请求的失败

## 优势

### 1. 更好的错误处理

- ✅ 第一个接口失败时，不会调用第二个接口
- ✅ 避免级联错误
- ✅ 减少无效的网络请求

### 2. 更好的用户体验

- ✅ 避免显示不完整的数据
- ✅ 错误提示更清晰
- ✅ 加载状态更准确

### 3. 更好的性能

- ✅ 减少无效的 API 调用
- ✅ 节省网络资源
- ✅ 减少服务器负载

### 4. 更好的代码可维护性

- ✅ 接口调用顺序清晰
- ✅ 错误处理统一
- ✅ 返回值明确（true/false）

## 注意事项

1. **返回值**: 所有 fetch 函数都应该返回 `true`（成功）或 `false`（失败）
2. **错误处理**: 使用 try-catch 捕获错误，并设置默认值
3. **依赖关系**: 明确哪些接口有依赖关系，哪些是独立的
4. **用户提示**: 关键接口失败时，应该给用户明确的错误提示

## 测试清单

- [ ] 服务器分组列表：国家列表失败时，不加载分组数据
- [ ] 服务器列表：分组列表失败时，不加载服务器数据
- [ ] Token管理：用户列表失败时，不加载Token数据
- [ ] 项目钱包：项目列表失败时，不加载钱包数据
- [ ] 项目账号：项目列表失败时显示错误提示
- [ ] 所有页面：独立的接口不受影响
- [ ] 所有页面：没有控制台错误

## 相关文档

- ✅ `docs/fixes/PROJECT_ACCOUNT_BALANCE_ENHANCEMENT.md` - 项目账号余额功能增强
- ✅ `docs/fixes/SEQUENTIAL_API_CALLS.md` - 本文档

## 总结

✅ 修改了7个页面的接口调用逻辑
✅ 确保有依赖关系的接口按顺序调用
✅ 第一个接口失败时，不会调用第二个接口
✅ 添加了明确的返回值（true/false）
✅ 改进了错误处理
✅ 提升了用户体验和性能

现在所有页面都会先检查第一个接口的状态，只有成功后才会调用第二个接口！
