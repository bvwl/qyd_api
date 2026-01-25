# XUI 入站账号 404 错误修复

## 问题描述

API 接口 `/v1/xui/account/inbound/{inbound_id}` 在查询不到账号数据时，没有抛出 404 错误，而是返回空列表。

### 问题表现

**当前行为**（错误）：
```json
{
  "message": "成功",
  "count": -1,
  "num": 0,
  "items": []
}
```

**预期行为**（正确）：
```json
{
  "detail": "未查询到数据"
}
```
HTTP 状态码：404

## 根本原因

在 `backend/app/crud/xui/user.py` 的 `get_inbound_accounts` 方法中，虽然检查了入站是否存在，但没有检查账号列表是否为空。

### 原代码

```python
async def get_inbound_accounts(
    self,
    inbound_id: UUID,
    page: int = 1,
    limit: int = 10,
    res_count: bool = False
) -> XuiInboundAccountOutList:
    """获取入站的账号列表"""
    inbound = await XuiInbound.get_or_none(id=inbound_id)
    if not inbound:
        raise HTTPException(status_code=404, detail='入站不存在')
    
    # 获取关联的账号
    query = inbound.accounts.all()
    
    # 计数
    if res_count:
        count = await query.count()
    else:
        count = -1
    
    # 分页
    offset = (page - 1) * limit
    accounts = await query.limit(limit).offset(offset)
    
    # ❌ 缺少空数据检查
    items = [
        XuiInboundAccountOut(...)
        for account in accounts
    ]
    
    return XuiInboundAccountOutList(
        message='成功',
        count=count,
        num=len(items),
        items=items
    )
```

## 解决方案

添加空数据检查，与项目中其他接口保持一致。

### 修复后的代码

```python
async def get_inbound_accounts(
    self,
    inbound_id: UUID,
    page: int = 1,
    limit: int = 10,
    res_count: bool = False
) -> XuiInboundAccountOutList:
    """获取入站的账号列表"""
    inbound = await XuiInbound.get_or_none(id=inbound_id)
    if not inbound:
        raise HTTPException(status_code=404, detail='入站不存在')
    
    # 获取关联的账号
    query = inbound.accounts.all()
    
    # 计数
    if res_count:
        count = await query.count()
    else:
        count = -1
    
    # 分页
    offset = (page - 1) * limit
    accounts = await query.limit(limit).offset(offset)
    
    # ✅ 添加空数据检查
    if not accounts:
        raise HTTPException(status_code=404, detail='未查询到数据')
    
    items = [
        XuiInboundAccountOut(
            inbound_id=inbound_id,
            account_id=account.id,
            username=account.username,
            user_id=account.user_id
        )
        for account in accounts
    ]
    
    return XuiInboundAccountOutList(
        message='成功',
        count=count,
        num=len(items),
        items=items
    )
```

## 修改内容

### 文件

`backend/app/crud/xui/user.py`

### 变更

在查询账号列表后，添加空数据检查：

```python
# 如果没有查询到数据，抛出 404
if not accounts:
    raise HTTPException(status_code=404, detail='未查询到数据')
```

## 测试场景

### 场景 1：不存在的入站 ID

**请求**：
```bash
GET /v1/xui/account/inbound/00000000-0000-0000-0000-000000000000
```

**响应**：
```json
{
  "detail": "入站不存在"
}
```
**状态码**：404

### 场景 2：存在的入站但没有账号

**请求**：
```bash
GET /v1/xui/account/inbound/{valid_inbound_id}
```

**响应**：
```json
{
  "detail": "未查询到数据"
}
```
**状态码**：404

### 场景 3：存在的入站且有账号

**请求**：
```bash
GET /v1/xui/account/inbound/{valid_inbound_id}
```

**响应**：
```json
{
  "message": "成功",
  "count": -1,
  "num": 2,
  "items": [
    {
      "inbound_id": "xxx-xxx-xxx",
      "account_id": "yyy-yyy-yyy",
      "username": "user1",
      "user_id": "zzz-zzz-zzz"
    },
    {
      "inbound_id": "xxx-xxx-xxx",
      "account_id": "aaa-aaa-aaa",
      "username": "user2",
      "user_id": "bbb-bbb-bbb"
    }
  ]
}
```
**状态码**：200

## 测试

### 运行测试脚本

```bash
cd backend
python test_xui_account_404.py
```

### 测试内容

1. ✅ 测试不存在的入站 ID（预期：404 - 入站不存在）
2. ✅ 测试存在的入站但没有账号（预期：404 - 未查询到数据）
3. ✅ 测试存在的入站且有账号（预期：200 - 返回账号列表）

### 预期输出

```
============================================================
测试 XUI 入站账号 404 错误处理
============================================================

📋 测试 1: 查询不存在的入站
   ✅ 正确抛出 404: 入站不存在

📋 测试 2: 查询存在的入站但没有账号
   入站 ID: xxx-xxx-xxx
   入站地址: 192.168.1.1:22000
   已清空入站的账号关联
   ✅ 正确抛出 404: 未查询到数据

📋 测试 3: 查询存在的入站且有账号
   创建测试账号: test_user_404
   已关联账号到入站
   ✅ 成功返回账号列表
   账号数量: 1
   账号列表: ['test_user_404']
   已清理测试数据

✅ 测试完成！
```

## API 测试命令

### 1. 测试不存在的入站

```bash
curl -X GET 'http://127.0.0.1:6080/v1/xui/account/inbound/00000000-0000-0000-0000-000000000000' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**预期响应**：
```json
{"detail": "入站不存在"}
```

### 2. 测试存在的入站但没有账号

```bash
# 先获取一个入站 ID
curl -X GET 'http://127.0.0.1:6080/v1/xui/inbound' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# 使用获取到的入站 ID 查询账号
curl -X GET 'http://127.0.0.1:6080/v1/xui/account/inbound/{INBOUND_ID}' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**预期响应**（如果该入站没有账号）：
```json
{"detail": "未查询到数据"}
```

### 3. 测试存在的入站且有账号

```bash
# 先添加账号到入站
curl -X POST 'http://127.0.0.1:6080/v1/xui/account/add' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "inbound_id": "{INBOUND_ID}",
    "account_id": "{ACCOUNT_ID}"
  }'

# 然后查询账号列表
curl -X GET 'http://127.0.0.1:6080/v1/xui/account/inbound/{INBOUND_ID}' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**预期响应**：
```json
{
  "message": "成功",
  "count": -1,
  "num": 1,
  "items": [
    {
      "inbound_id": "xxx",
      "account_id": "yyy",
      "username": "user1",
      "user_id": "zzz"
    }
  ]
}
```

## 项目规范

### 空数据处理规范

根据项目中其他接口的实现，列表查询接口应该遵循以下规范：

1. **资源不存在**：抛出 404 - "资源名称不存在"
2. **数据为空**：抛出 404 - "未查询到数据"
3. **有数据**：返回 200 和数据列表

### 示例参考

项目中其他接口的实现：

```python
# backend/app/crud/user/user.py
if not res:
    raise HTTPException(status_code=404, detail='未查询到数据')

# backend/app/crud/server/info.py
if not res:
    raise HTTPException(status_code=404, detail='未查询到数据')

# backend/app/crud/xui/inbound.py
if not inbounds:
    raise HTTPException(status_code=404, detail='未查询到数据')
```

## 相关文件

- `backend/app/crud/xui/user.py` - 修复的文件
- `backend/app/apis/v1/xui/user.py` - API 接口定义
- `backend/test_xui_account_404.py` - 测试脚本

## 影响范围

### 受影响的接口

- `GET /v1/xui/account/inbound/{inbound_id}` - 获取入站的账号列表

### 不受影响的接口

- `POST /v1/xui/account/add` - 添加账号到入站
- `POST /v1/xui/account/batch-add` - 批量添加账号
- `DELETE /v1/xui/account/remove` - 从入站移除账号

## 完成状态

✅ 问题已识别
✅ 代码已修复
✅ 测试脚本已创建
✅ 文档已完善
✅ 符合项目规范

## 总结

修复了 XUI 入站账号查询接口的 404 错误处理问题，现在该接口的行为与项目中其他列表查询接口保持一致：

- ✅ 入站不存在时抛出 404
- ✅ 账号列表为空时抛出 404
- ✅ 有账号数据时返回 200

这个修复确保了 API 的一致性和可预测性，符合 RESTful API 的最佳实践。
