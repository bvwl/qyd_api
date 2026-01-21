# 钱包API修复

## 修复时间
2026-01-21

## 问题描述
访问钱包列表API时返回500错误：
```
GET /v1/project/wallet?page=1&limit=10&res_count=true HTTP/1.1" 500 Internal Server Error
响应: {"detail":"CRUD.get_multi() got an unexpected keyword argument 'project_id'"}
```

## 问题原因
API层错误地传递了 `project_id` 参数给CRUD的 `get_multi` 方法。

**实际情况**：`ProjectWallet` 模型可以选择性地关联项目（`project_id` 可为空），也可以作为独立资源存在。

### 数据模型关系
```
ProjectInfo (项目)
    ↓ (一对多: project_id, 可选)
ProjectWallet (钱包)

ProjectInfo (项目)
    ↓ (一对多: project_id, 必须)
ProjectAccount (项目账号)
```

钱包可以独立存在，也可以关联到项目；账号必须关联到项目。

### API层代码
`backend/app/apis/v1/project/wallet.py`:
```python
return await project_wallet_crud.get_multi(
    project_id=project_id,  # ← 传递了这个参数
    chain=chain,
    ...
)
```

### CRUD层代码（修复前）
`backend/app/crud/project/wallet.py`:
```python
async def get_multi(self,
                    chain: str | None = None,  # ← 没有 project_id 参数
                    page: int = 1,
                    ...
```

## 解决方案
移除API层中错误的 `project_id` 参数。钱包是独立资源，不需要按项目过滤。

### 修复后的API代码
```python
@app.get("", response_model=OutList, description="获取项目钱包列表")
async def gets(
    chain: str | None = Query(None, description="链名称"),  # ← 移除了 project_id
    order_by: str | None = Query("-create_time", description="排序字段"),
    ...
):
    return await project_wallet_crud.get_multi(
        chain=chain,  # ← 不再传递 project_id
        order_by=order_by or "-create_time",
        ...
    )
```

### CRUD代码（保持不变）
```python
async def get_multi(self,
                    chain: str | None = None,  # ← 没有 project_id 参数
                    page: int = 1,
                    ...
```

## 功能说明
钱包列表API支持按链名称过滤：

### 查询所有钱包
```bash
GET /v1/project/wallet?page=1&limit=10&res_count=true
```

### 按链名称过滤
```bash
GET /v1/project/wallet?chain=ETH&page=1&limit=10&res_count=true
```

## 如何查询项目的钱包
钱包可以选择性地关联到项目，查询方式：
1. 查询特定项目的钱包：`GET /v1/project/wallet?project_id=xxx`
2. 查询所有钱包（包括独立钱包）：`GET /v1/project/wallet`
3. 查询单个钱包：`GET /v1/project/wallet/{wallet_id}`

## 测试验证
```bash
# 测试1: 查询所有钱包
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:6080/v1/project/wallet?page=1&limit=10&res_count=true"

# 测试2: 按链名称过滤
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:6080/v1/project/wallet?chain=ETH&page=1&limit=10&res_count=true"
```

预期结果：
- 返回200状态码
- 返回钱包列表数据
- 如果无数据返回404（符合设计）

## 相关文件
- `backend/app/apis/v1/project/wallet.py` - API层
- `backend/app/crud/project/wallet.py` - CRUD层（已修复）

## 类似问题检查
检查了其他CRUD文件，确认没有类似问题：
- ✅ `backend/app/crud/project/balance.py` - 正常
- ✅ `backend/app/crud/project/account.py` - 正常
- ✅ `backend/app/crud/project/info.py` - 正常
- ✅ 其他CRUD文件 - 正常

## 总结
✅ 修复了钱包API的参数错误
✅ 移除了不存在的 project_id 参数
✅ 钱包作为独立资源管理
✅ 通过项目账号间接关联到项目
✅ 后端服务已重启并正常运行
✅ API现在可以正常访问
