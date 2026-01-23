# 项目管理员（GM）权限更新

## 权限范围

项目管理员（GM）现在拥有以下权限：

### ✅ 允许的操作

1. **项目管理**
   - 创建项目
   - 编辑项目
   - 删除项目
   - 查看项目列表
   - 管理项目关联用户

2. **项目账户管理**
   - 创建项目账户
   - 编辑项目账户
   - 删除项目账户
   - 查看项目账户列表
   - 批量操作项目账户

3. **项目余额管理**
   - 创建项目余额记录
   - 编辑项目余额
   - 删除项目余额
   - 查看项目余额列表

### ❌ 不允许的操作

1. **项目钱包管理**（仅管理员）
   - 创建钱包
   - 编辑钱包
   - 删除钱包
   - 批量删除钱包

2. **用户管理**（仅管理员）
   - 创建用户
   - 编辑用户
   - 删除用户
   - 管理用户角色

3. **系统配置**（仅管理员）
   - 角色管理
   - 路由管理
   - 权限管理

## 修改内容

### 后端修改

#### 1. 项目信息 API (`backend/app/apis/v1/project/info.py`)
```python
# 修改前
@app.delete("/{id}")
async def delete(admin_user: dict = Depends(get_admin_user)):
    ...

# 修改后
@app.delete("/{id}")
async def delete(gm_user: dict = Depends(get_gm_user)):
    """删除项目信息（需要GM或管理员权限）"""
    ...
```

#### 2. 项目账户 API (`backend/app/apis/v1/project/account.py`)
```python
# 修改前
@app.delete("/{id}")
async def delete(admin_user: dict = Depends(get_admin_user)):
    ...

# 修改后
@app.delete("/{id}")
async def delete(gm_user: dict = Depends(get_gm_user)):
    """删除项目账号（需要GM或管理员权限）"""
    ...
```

#### 3. 项目余额 API (`backend/app/apis/v1/project/balance.py`)
```python
# 修改前
@app.delete("/{id}")
async def delete(admin_user: dict = Depends(get_admin_user)):
    ...

# 修改后
@app.delete("/{id}")
async def delete(gm_user: dict = Depends(get_gm_user)):
    """删除项目余额（需要GM或管理员权限）"""
    ...
```

#### 4. 项目钱包 API (`backend/app/apis/v1/project/wallet.py`)
```python
# 保持不变 - 仅管理员
@app.delete("/{id}")
async def delete(admin_user: dict = Depends(get_admin_user)):
    """删除项目钱包（仅管理员）"""
    ...
```

### 前端修改

#### 1. 项目列表 (`frontend/src/views/Project/ProjectList.tsx`)
```typescript
// 已有正确的权限控制
{(isAdmin || isGM) && (
  <Button onClick={handleEdit}>编辑</Button>
  <Button onClick={handleDelete}>删除</Button>
)}
```

#### 2. 项目账户 (`frontend/src/views/Project/ProjectAccount.tsx`)
```typescript
// 已有正确的权限控制
{(isAdmin || isGM) && (
  <Button onClick={handleEdit}>编辑</Button>
  <Button onClick={handleDelete}>删除</Button>
)}
```

#### 3. 项目钱包 (`frontend/src/views/Project/ProjectWallet.tsx`)
```typescript
// 修改前
{(isAdmin || isGM) && (
  <Button onClick={handleEdit}>编辑</Button>
  <Button onClick={handleDelete}>删除</Button>
)}

// 修改后 - 仅管理员
{isAdmin && (
  <Button onClick={handleEdit}>编辑</Button>
  <Button onClick={handleDelete}>删除</Button>
)}
```

## 权限验证函数

### `get_gm_user` 函数
位置: `backend/app/apis/deps.py`

```python
async def get_gm_user(user_info: dict = Depends(get_current_user_or_token)):
    """验证GM权限（GM或ADMIN都可以）"""
    try:
        user_roles = user_info.get('roles', [])
        if 'ADMIN' in user_roles or 'GM' in user_roles:
            return user_info
        raise HTTPException(status_code=403, detail="需要GM或管理员权限")
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
```

## 角色层级

```
ADMIN (管理员)
  └─ 所有权限
  
GM (项目管理员)
  ├─ 项目管理 ✅
  ├─ 项目账户管理 ✅
  ├─ 项目余额管理 ✅
  └─ 项目钱包管理 ❌
  
IT (技术人员)
  └─ 查看权限
  
MANUAL (手动操作员)
  └─ 基础操作权限
```

## 测试验证

### 1. 使用GM账户登录
```bash
# 登录GM账户
POST /v1/user/auth/login
{
  "email": "gm@example.com",
  "password": "password"
}
```

### 2. 测试项目操作
```bash
# 应该成功
DELETE /v1/project/info/{id}
DELETE /v1/project/account/{id}
DELETE /v1/project/balance/{id}

# 应该失败（403）
DELETE /v1/project/wallet/{id}
```

### 3. 前端验证
1. 使用GM账户登录前端
2. 访问项目列表 - 应该能看到编辑/删除按钮
3. 访问项目账户 - 应该能看到编辑/删除按钮
4. 访问项目钱包 - 不应该看到编辑/删除按钮（仅查看）

## 注意事项

1. **数据权限**: GM只能操作分配给自己的项目（通过数据权限过滤）
2. **钱包安全**: 钱包涉及资金，只有管理员才能操作
3. **权限继承**: ADMIN拥有所有权限，包括GM的所有权限
4. **前后端一致**: 前端隐藏按钮，后端验证权限，双重保护

## 相关文件

### 后端
- `backend/app/apis/v1/project/info.py`
- `backend/app/apis/v1/project/account.py`
- `backend/app/apis/v1/project/balance.py`
- `backend/app/apis/v1/project/wallet.py`
- `backend/app/apis/deps.py`

### 前端
- `frontend/src/views/Project/ProjectList.tsx`
- `frontend/src/views/Project/ProjectAccount.tsx`
- `frontend/src/views/Project/ProjectWallet.tsx`

---

**更新时间**: 2026-01-23  
**更新状态**: ✅ 完成  
**测试状态**: 待测试
