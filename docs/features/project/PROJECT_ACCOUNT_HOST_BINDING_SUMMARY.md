# 项目账号 Host 自动绑定功能总结

## 更新时间
2026-01-25

## 功能
在创建或更新项目账号时，可以通过传入 `host` 字段自动查询并绑定对应的服务器。

## 使用方式

### 创建账号
```json
{
  "account": "test@example.com",
  "password": "password123",
  "project_id": "uuid",
  "host": "192.168.1.100",  // 新增：直接传 host
  "status": 1,
  "account_type": 1
}
```

### 更新账号
```json
{
  "host": "192.168.1.200"  // 更新绑定的服务器
}
```

## 工作原理

1. **传入 host** → 查询服务器信息表
2. **找到服务器** → 自动设置 `server_id`
3. **未找到** → `server_id` 为 `None`（宽松模式，不报错）
4. **host 不存储** → 只用于查询，不保存到数据库

## 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `backend/app/schemas/project/account.py` | Create 和 Update 添加 `host` 字段 |
| `backend/app/crud/project/account.py` | create、update、upsert 方法添加 host 查询逻辑 |

## 优势

- ✅ 无需先查询服务器 UUID
- ✅ 使用更直观的 host 地址
- ✅ 简化 API 调用流程
- ✅ 兼容现有代码（host 是可选字段）

## 示例对比

**之前：**
```python
# 1. 查询服务器
server = await get_server_by_host("192.168.1.100")
# 2. 创建账号
await create_account(server_id=server.id)
```

**现在：**
```python
# 一步完成
await create_account(host="192.168.1.100")
```

## 测试

```bash
cd backend
python test_host_binding.py
```

## 详细文档
查看 [PROJECT_ACCOUNT_HOST_BINDING.md](PROJECT_ACCOUNT_HOST_BINDING.md)
