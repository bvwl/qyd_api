# XUI 操作日志错误修复

## 问题描述

访问 XUI 操作日志页面时报错:
```
{"detail":"(1054, \"Unknown column 'status' in 'where clause'\")"}
```

## 问题原因

在 `backend/app/models/user.py` 文件中,`XuiOperationLog` 模型被定义了**两次**:

1. **第一个定义** (第40-82行): 旧版本,包含 `status` 字段
2. **第二个定义** (第283-325行): 简化版本,使用 `is_resolved` 字段

Python 在导入模块时,第二个定义会覆盖第一个定义,但 Tortoise ORM 可能在初始化时使用了第一个定义,导致查询时使用了不存在的 `status` 字段。

## 解决方案

删除第一个重复的 `XuiOperationLog` 定义,只保留简化版本(使用 `is_resolved` 字段)。

### 修改的文件

**backend/app/models/user.py**
- 删除第40-82行的旧版 `XuiOperationLog` 定义
- 保留第283-325行的简化版定义

### 验证步骤

1. **检查表结构**
```bash
python backend/check_xui_log_table_simple.py
```

输出确认:
- ✓ 表存在
- ✓ 没有 `status` 字段
- ✓ 有 `is_resolved` 字段

2. **检查模型定义**
```bash
grep -n "class XuiOperationLog" backend/app/models/user.py
```

输出确认:
- 只有一个定义(第283行)

3. **重启服务器**
```bash
# 停止旧进程
lsof -ti:6080 | xargs kill -9

# 启动新进程
cd backend && python start.py
```

4. **测试 API**
```bash
curl 'http://127.0.0.1:6080/v1/xui/account/failed-logs?page=1&limit=10&res_count=true' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

预期输出:
```json
{
  "code": 200,
  "message": "成功",
  "count": 0,
  "num": 0,
  "data": []
}
```

## 简化版 XuiOperationLog 模型

```python
class XuiOperationLog(BaseModel):
    """
    XUI 添加账号失败日志
    只记录添加账号失败的情况,方便重试
    """
    # 入站信息
    inbound_id = fields.UUIDField(index=True, description="入站 ID")
    inbound_info = fields.CharField(max_length=255, description="入站信息(host:port)")
    
    # 账号信息
    account_id = fields.UUIDField(index=True, description="账号 ID")
    account_username = fields.CharField(max_length=100, description="账号用户名")
    
    # 错误信息
    error_message = fields.TextField(description="错误信息")
    
    # 重试信息
    retry_count = fields.IntField(default=0, description="重试次数")
    is_resolved = fields.BooleanField(default=False, index=True, description="是否已解决")

    class Meta:
        table = "xui_operation_logs"
        table_description = "XUI 添加账号失败日志"
        ordering = ["-create_time"]
```

## 字段对比

| 旧版字段 | 简化版字段 | 说明 |
|---------|-----------|------|
| operation_type | ❌ 删除 | 只记录添加账号失败,不需要操作类型 |
| status | ❌ 删除 | 使用 is_resolved 替代 |
| ❌ | is_resolved | 新增,布尔值,更简洁 |
| inbound_id | ✓ 保留 | 入站 ID |
| account_id | ✓ 保留 | 账号 ID |
| error_message | ✓ 保留 | 错误信息 |
| retry_count | ✓ 保留 | 重试次数 |

## 前端更新

前端代码已同步更新:

### frontend/src/api/xui.ts
- 简化 `XuiOperationLog` 接口
- 移除 `operation_type` 和 `status` 字段
- 添加 `is_resolved` 字段

### frontend/src/views/Xui/XuiOperationLog.tsx
- 移除操作类型筛选器
- 更新状态列显示(已解决/未解决)
- 更新重试按钮条件(`!is_resolved`)

## 测试结果

✅ API 正常返回数据
✅ 前端页面正常加载
✅ 没有 SQL 错误
✅ 模型定义唯一

## 经验教训

1. **避免重复定义**: 同一个模型不要在同一个文件中定义多次
2. **及时清理**: 重构代码时要删除旧的定义
3. **验证表结构**: 修改模型后要验证数据库表结构是否匹配
4. **重启服务**: 修改模型定义后必须重启服务器

## 相关文件

- `backend/app/models/user.py` - 模型定义(已修复)
- `backend/check_xui_log_table_simple.py` - 表结构检查工具
- `frontend/src/api/xui.ts` - API 接口定义
- `frontend/src/views/Xui/XuiOperationLog.tsx` - 操作日志页面

## 总结

问题已完全解决,XUI 操作日志功能现在可以正常使用。系统使用简化的模型设计,只记录添加账号失败的情况,使用 `is_resolved` 布尔字段标记是否已解决,比旧版的 `status` 枚举更简洁明了。
