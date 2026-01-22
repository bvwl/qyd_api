# 项目钱包功能更新总结

## 概述

对项目钱包页面进行了以下更新：
1. 所有用户都可以创建钱包（移除权限限制）
2. 添加公钥查询条件

## 修改详情

### 1. 前端修改 (`frontend/src/views/Project/ProjectWallet.tsx`)

#### 新增公钥搜索框

```typescript
// 添加公钥搜索状态
const [searchPublicKey, setSearchPublicKey] = useState('')

// 搜索表单中添加公钥输入框
<Input
  placeholder="搜索公钥"
  prefix={<SearchOutlined />}
  value={searchPublicKey}
  onChange={(e) => setSearchPublicKey(e.target.value)}
  style={{ width: 200 }}
/>

// API请求时传递公钥参数
const res = await getProjectWalletList({
  // ...其他参数
  public_key: searchPublicKey || undefined,
})
```

#### 移除创建权限限制

**之前**：
```typescript
{(isAdmin || isGM) && (
  <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
    新增钱包
  </Button>
)}
```

**现在**：
```typescript
<Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
  新增钱包
</Button>
```

### 2. 后端API修改 (`backend/app/apis/v1/project/wallet.py`)

#### 添加公钥查询参数

```python
@app.get("", response_model=OutList, description="获取项目钱包列表", summary="获取项目钱包列表")
async def gets(
    project_id: UUID | None = Query(None, description="所属项目ID"),
    chain: str | None = Query(None, description="链名称"),
    public_key: str | None = Query(None, description="公钥（模糊查询）"),  # 新增
    # ...其他参数
):
    """
    分页查询项目钱包列表
    """
    try:
        return await project_wallet_crud.get_multi(
            project_id=project_id,
            chain=chain,
            public_key=public_key,  # 传递公钥参数
            # ...其他参数
        )
```

### 3. CRUD层修改 (`backend/app/crud/project/wallet.py`)

#### 支持公钥模糊查询

```python
async def get_multi(self,
                    project_id: UUID | None = None,
                    chain: str | None = None,
                    public_key: str | None = None,  # 新增参数
                    # ...其他参数
                    ) -> OutList:
    query = ProjectWallet.all()
    
    if project_id:
        query = query.filter(project_id=project_id)
    
    if chain:
        query = query.filter(chain__icontains=chain)
    
    if public_key:
        query = query.filter(public_key__icontains=public_key)  # 模糊查询
    
    # ...其他过滤条件
```

## 功能特点

### 1. 公钥查询

- **模糊匹配**：支持公钥的部分匹配查询
- **实时搜索**：输入后点击搜索按钮即可查询
- **组合查询**：可以与链、项目、时间范围等条件组合使用

### 2. 创建权限

**之前**：
- 只有ADMIN和GM可以创建钱包

**现在**：
- 所有登录用户都可以创建钱包
- 创建时仍然受到项目权限控制（如果关联项目）

### 3. 其他权限保持不变

- **编辑权限**：仍然只有ADMIN和GM可以编辑
- **删除权限**：仍然只有ADMIN和GM可以删除
- **查看权限**：所有用户可以查看（受项目权限控制）

## 使用场景

### 公钥查询场景

1. **快速定位**：通过公钥的部分内容快速找到对应的钱包
2. **验证存在**：检查某个公钥是否已经录入系统
3. **批量管理**：配合其他条件筛选特定公钥的钱包

### 创建钱包场景

1. **项目成员**：项目成员可以为自己的项目添加钱包
2. **独立钱包**：用户可以创建不关联项目的独立钱包
3. **快速录入**：无需等待管理员，提高工作效率

## 界面变化

### 搜索表单

**之前**：
- 搜索链
- 选择项目
- 时间范围

**现在**：
- 搜索链
- **搜索公钥**（新增）
- 选择项目
- 时间范围

### 操作按钮

**之前**：
- 新增钱包按钮只对ADMIN和GM显示

**现在**：
- 新增钱包按钮对所有用户显示

## 权限控制说明

虽然所有用户都可以创建钱包，但仍然受到以下限制：

1. **项目关联**：如果钱包关联项目，用户必须是该项目的成员
2. **独立钱包**：用户可以创建不关联项目的独立钱包
3. **编辑删除**：创建后的编辑和删除仍需要ADMIN或GM权限

## 修改的文件

1. `frontend/src/views/Project/ProjectWallet.tsx` - 前端页面
2. `backend/app/apis/v1/project/wallet.py` - 后端API
3. `backend/app/crud/project/wallet.py` - CRUD层

## 状态

✅ 前端添加公钥搜索框完成
✅ 前端移除创建权限限制完成
✅ 后端API添加公钥查询参数完成
✅ CRUD层支持公钥模糊查询完成
✅ 前端编译检查通过
✅ 后端编译检查通过
✅ 后端服务已重启
