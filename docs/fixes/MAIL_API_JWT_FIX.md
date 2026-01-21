# 邮箱 API JWT 认证修复

## 问题描述

邮箱列表页面无法加载数据，API 返回 404 错误。

## 根本原因

邮箱 API 的 GET、PUT、DELETE、upsert 和 batch-update 端点缺少 JWT 认证依赖 `current_user: dict = Depends(get_current_user)`。

只有 POST 创建端点有认证，导致其他端点无法通过认证，返回 404。

## 修复内容

在 `backend/app/apis/v1/mail/info.py` 中为以下端点添加了 JWT 认证：

1. **GET /v1/mail/info** - 获取邮箱列表
2. **PUT /v1/mail/info/{id}** - 更新邮箱信息
3. **DELETE /v1/mail/info/{id}** - 删除邮箱信息
4. **POST /v1/mail/info/upsert** - 创建或更新邮箱信息
5. **POST /v1/mail/info/status/batch-update** - 批量更新邮箱状态

## 修改示例

### 修改前
```python
@app.get("", response_model=OutList)
async def gets(
    email: str | None = Query(None),
    status: int | None = Query(None),
    # ... 其他参数
):
    # 没有认证
```

### 修改后
```python
@app.get("", response_model=OutList)
async def gets(
    email: str | None = Query(None),
    status: int | None = Query(None),
    # ... 其他参数
    current_user: dict = Depends(get_current_user)  # 添加认证
):
    # 有认证保护
```

## 验证

修复后，所有邮箱 API 端点都需要有效的 JWT token 才能访问：

```bash
# 测试（需要有效的 token）
curl -X GET "http://127.0.0.1:6080/v1/mail/info?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 影响

- ✅ 邮箱列表页面现在可以正常加载数据
- ✅ 所有邮箱操作（查询、创建、更新、删除）都需要认证
- ✅ 提高了 API 安全性

## 注意事项

后端使用 `--reload` 参数启动时会自动重新加载，无需手动重启。

## 相关文件

- `backend/app/apis/v1/mail/info.py` - 邮箱 API 端点
- `backend/app/apis/deps.py` - JWT 认证依赖
- `frontend/src/views/Mail/MailList.tsx` - 邮箱列表页面
