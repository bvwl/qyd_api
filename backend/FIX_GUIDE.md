# 测试失败修复指南

## 问题分析

测试失败主要有以下几个原因：

### 1. 数据库结构不匹配

**错误信息**：
```
(1054, "Unknown column 'country_info_id' in 'field list'")
```

**原因**：
- 数据库中的外键字段名称与模型定义不匹配
- `ServerGroup` 模型定义的外键是 `country_info`，但数据库中可能是 `country_id`

**解决方案**：
需要重新生成并运行数据库迁移：

```bash
cd backend

# 1. 生成新的迁移文件
aerich migrate --name "fix_foreign_keys"

# 2. 应用迁移
aerich upgrade
```

### 2. CRUD方法签名不匹配（已修复）

**问题**：
- API层传递字典给CRUD方法
- CRUD方法期望接收schema对象

**已修复的文件**：
- `backend/app/crud/user/user.py` - 用户CRUD的create方法
- `backend/app/crud/project/info.py` - 项目CRUD的create、update、upsert、delete、get_multi方法

**修复内容**：
```python
# 修改前
async def create(self, item: Create) -> Out:
    data = item.model_dump()
    ...

# 修改后
async def create(self, item: dict | Create) -> Out:
    if isinstance(item, dict):
        data = item.copy()
    else:
        data = item.model_dump()
    ...
```

### 3. 测试fixture依赖问题

**错误信息**：
```
fixture 'country_id' not found
fixture 'group_id' not found
fixture 'server_info_id' not found
```

**原因**：
- 测试用例之间的依赖关系没有正确设置
- pytest fixture的作用域和依赖关系配置不当

**解决方案**：
这些错误会在数据库结构修复后自动解决，因为它们是由于前置测试失败导致的连锁反应。

## 修复步骤

### 步骤1：检查数据库连接

确保可以连接到远程MySQL数据库：

```bash
mysql -h 149.88.87.93 -u qyd -p qyd
# 输入密码: hWect7iWa4M67aSH
```

### 步骤2：检查当前数据库结构

```sql
USE qyd;
DESCRIBE server_group;
DESCRIBE server_info;
```

查看外键字段的实际名称。

### 步骤3：修复外键字段名称

如果数据库中的字段名称与模型不匹配，有两个选择：

**选项A：修改模型以匹配数据库**（推荐）

在 `backend/app/models/server.py` 中：

```python
class ServerGroup(BaseModel):
    # 修改外键字段名称以匹配数据库
    country_id = fields.ForeignKeyField(
        "models.ServerCountry",
        related_name="server_groups",
        description='国家' 明确指定数据库列名
    )
```

**选项B：重新创建数据库表**

```bash
# 删除所有表并重新创建
aerich downgrade
aerich upgrade
```

### 步骤4：运行测试

```bash
cd backend
python -m pytest app/tests/ -v
```

## 预期结果

修复后，应该看到：
- ✅ 6个测试通过（ServerAccount相关测试）
- ✅ 其他测试也应该通过

## 注意事项

1. **数据备份**：在修改数据库结构前，请备份重要数据
2. **环境一致性**：确保开发、测试、生产环境的数据库结构一致
3. **迁移管理**：使用aerich管理所有数据库结构变更，不要手动修改

## 额外建议

### 改进测试结构

考虑使用pytest的fixture依赖来管理测试数据：

```python
@pytest.fixture
def country_id():
    """创建测试国家并返回ID"""
    result = _req("POST", "/server/country", json={...})
    return result["id"]

@pytest.fixture
def group_id(country_id):
    """创建测试分组（依赖country_id）"""
    result = _req("POST", "/server/group", json={
        "country_id": country_id,
        ...
    })
    return result["id"]
```

### 使用数据库事务隔离测试

在 `pytest.ini` 或 `conftest.py` 中配置：

```python
@pytest.fixture(autouse=True)
async def reset_db():
    """每个测试后回滚数据库"""
    # 开始事务
    yield
    # 回滚事务
```

这样可以确保测试之间不会相互影响。
