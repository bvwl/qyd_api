# XUI DateTime 序列化修复

## 问题描述

创建 XUI 服务器时出现 Pydantic 验证错误：

```
2 validation errors for XuiServerOut
create_time
  Input should be a valid string [type=string_type, input_value=datetime.datetime(...), input_type=datetime]
update_time
  Input should be a valid string [type=string_type, input_value=datetime.datetime(...), input_type=datetime]
```

**原因**：Schema 中 `create_time` 和 `update_time` 定义为 `str` 类型，但从数据库返回的是 `datetime` 对象。

## 解决方案

参考项目中其他 Schema（如 `project/info.py`）的处理方式，使用 Pydantic 的 `@field_serializer` 装饰器自动将 `datetime` 对象序列化为字符串。

### 修改内容

#### 1. `backend/app/schemas/xui/server.py`

**导入更新**：
```python
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer
from app.utils.time_tool import CN_TZ
```

**XuiServerOut 更新**：
```python
class XuiServerOut(XuiServerBase):
    """XUI 服务器输出"""
    id: UUID = Field(..., description='ID')
    password: Optional[str] = Field(None, description='密码（仅管理员可见）')
    create_time: datetime = Field(..., description='创建时间')  # 改为 datetime 类型
    update_time: datetime = Field(..., description='更新时间')  # 改为 datetime 类型

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        # 统一格式化时间为东八区字符串
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True
```

#### 2. `backend/app/schemas/xui/inbound.py`

**导入更新**：
```python
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer
from app.utils.time_tool import CN_TZ
```

**XuiInboundOut 更新**：
```python
class XuiInboundOut(XuiInboundBase):
    """XUI 入站输出"""
    id: UUID = Field(..., description='ID')
    server_id: UUID = Field(..., description='XUI 服务器 ID')
    inbound_id: int = Field(..., description='XUI 面板中的入站 ID')
    create_time: datetime = Field(..., description='创建时间')  # 改为 datetime 类型
    update_time: datetime = Field(..., description='更新时间')  # 改为 datetime 类型

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        # 统一格式化时间为东八区字符串
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True
```

## 工作原理

1. **字段类型**：将 `create_time` 和 `update_time` 定义为 `datetime` 类型
2. **序列化器**：使用 `@field_serializer` 装饰器自动处理序列化
3. **时区转换**：使用 `CN_TZ`（东八区）统一时区
4. **格式化**：输出格式为 `YYYY-MM-DD HH:MM:SS`

## 优势

- ✅ **类型安全**：字段类型与数据库返回类型一致
- ✅ **自动转换**：Pydantic 自动处理 datetime → string 转换
- ✅ **统一格式**：与项目其他 Schema 保持一致
- ✅ **时区正确**：统一使用东八区时间

## 测试

现在可以正常创建 XUI 服务器：

```bash
curl -X POST 'http://127.0.0.1:6080/v1/xui/server' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "HK-004",
    "host": "202.155.155.88",
    "domain": "sd7.0n.lv",
    "port": 10010,
    "username": "cqrxy",
    "password": "Zpaily88",
    "is_ssl": true,
    "web_path": "/web3",
    "status": 1,
    "remark": "HK-004"
  }'
```

**预期响应**：
```json
{
  "id": "uuid",
  "name": "HK-004",
  "host": "202.155.155.88",
  "domain": "sd7.0n.lv",
  "port": 10010,
  "username": "cqrxy",
  "is_ssl": true,
  "web_path": "/web3",
  "status": 1,
  "remark": "HK-004",
  "create_time": "2026-01-25 12:34:56",
  "update_time": "2026-01-25 12:34:56"
}
```

## 相关文件

- `backend/app/schemas/xui/server.py` - XUI 服务器 Schema
- `backend/app/schemas/xui/inbound.py` - XUI 入站 Schema
- `backend/app/schemas/project/info.py` - 参考示例
- `backend/app/utils/time_tool.py` - 时区工具

## 注意事项

1. **统一模式**：项目中所有 Schema 的 datetime 字段都应使用此模式
2. **时区一致**：统一使用 `CN_TZ`（东八区）
3. **格式统一**：统一使用 `%Y-%m-%d %H:%M:%S` 格式
4. **类型定义**：字段定义为 `datetime`，序列化为 `str`

## 完成状态

✅ XUI 服务器 Schema datetime 序列化修复完成
✅ XUI 入站 Schema datetime 序列化修复完成
✅ 与项目其他 Schema 保持一致
✅ 可以正常创建和返回 XUI 资源
