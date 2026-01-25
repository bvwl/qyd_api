# 服务器分组管理 - 国家筛选功能修复

## 问题描述

在服务器管理的"分组管理"页面,选择国家进行筛选时,仍然显示所有分组,筛选功能无效。

## 问题原因

前端正确传递了 `country_id` 参数,但后端没有接收和处理这个参数:

### 前端代码(正确)
```typescript
// frontend/src/views/Server/GroupList.tsx
const res = await getGroupList({
  page,
  limit: pageSize,
  res_count: true,
  name: searchName || undefined,
  country_id: searchCountryId,  // ✓ 前端传递了 country_id
  status: searchStatus,
  // ...
})
```

### 后端代码(缺失)
```python
# backend/app/apis/v1/server/group.py
@app.get("")
async def gets(
    name: str | None = Query(None, description="分组名称"),
    # ❌ 缺少 country_id 参数
    status: int | None = Query(None, description="状态"),
    # ...
):
    return await server_group_crud.get_multi(
        name=name_filter,
        # ❌ 没有传递 country_id
        status=status,
        # ...
    )
```

## 解决方案

### 1. 更新 CRUD 层

在 `backend/app/crud/server/group.py` 的 `get_multi` 方法中添加 `country_id` 参数:

```python
async def get_multi(self,
                    name: str | None = None,
                    country_id: UUID | None = None,  # 新增参数
                    status: int | None = None,
                    # ...
                    ) -> OutList:
    query = ServerGroup.all()
    if name:
        query = query.filter(name__icontains=name)
    if country_id:  # 新增筛选逻辑
        query = query.filter(country_id=country_id)
    if status is not None:
        query = query.filter(status=status)
    # ...
```

### 2. 更新 API 层

在 `backend/app/apis/v1/server/group.py` 的 `gets` 函数中添加 `country_id` 参数:

```python
@app.get("", response_model=OutList)
async def gets(
    name: str | None = Query(None, description="分组名称"),
    country_id: UUID | None = Query(None, description="国家ID"),  # 新增参数
    status: int | None = Query(None, description="状态"),
    # ...
):
    try:
        name_filter = name.upper() if name else None
        return await server_group_crud.get_multi(
            name=name_filter,
            country_id=country_id,  # 传递参数
            status=status,
            # ...
        )
```

## 修复效果

### 修复前
```
前端: 选择国家 "美国"
请求: GET /v1/server/group?country_id=xxx&page=1&limit=10
后端: 忽略 country_id 参数
结果: 返回所有分组 ❌
```

### 修复后
```
前端: 选择国家 "美国"
请求: GET /v1/server/group?country_id=xxx&page=1&limit=10
后端: 使用 country_id 筛选
SQL: SELECT * FROM server_group WHERE country_id = 'xxx'
结果: 只返回美国的分组 ✓
```

## 测试步骤

1. ✅ 进入"服务器管理" -> "分组管理"
2. ✅ 在国家下拉框中选择一个国家(如"美国")
3. ✅ 点击"搜索"按钮
4. ✅ 验证只显示该国家的分组
5. ✅ 点击"重置"按钮
6. ✅ 验证显示所有分组

## 相关文件

### 后端文件
- `backend/app/apis/v1/server/group.py` - API 层,添加 country_id 参数
- `backend/app/crud/server/group.py` - CRUD 层,添加 country_id 筛选逻辑

### 前端文件
- `frontend/src/views/Server/GroupList.tsx` - 分组管理页面(无需修改)

## 数据库查询

### 修复前
```sql
SELECT * FROM server_group
WHERE name LIKE '%xxx%'
  AND status = 1
ORDER BY create_time DESC
LIMIT 10 OFFSET 0;
```

### 修复后
```sql
SELECT * FROM server_group
WHERE name LIKE '%xxx%'
  AND country_id = 'xxx-xxx-xxx'  -- 新增筛选条件
  AND status = 1
ORDER BY create_time DESC
LIMIT 10 OFFSET 0;
```

## 其他筛选功能

分组管理页面支持的所有筛选条件:
- ✅ 分组名称(模糊搜索)
- ✅ 国家(精确匹配) - **已修复**
- ✅ 状态(正常/异常)
- ✅ 创建时间范围
- ✅ 更新时间范围

## 注意事项

1. **参数类型**: `country_id` 使用 `UUID` 类型,确保前端传递的是有效的 UUID 字符串
2. **可选参数**: `country_id` 是可选的,不传则不筛选
3. **关联查询**: 使用 `prefetch_related('country')` 预加载国家信息,避免 N+1 查询
4. **大小写**: 分组名称会自动转换为大写进行存储和查询

## 总结

问题已修复,现在国家筛选功能可以正常工作:
- ✅ 后端 API 接收 `country_id` 参数
- ✅ CRUD 层使用 `country_id` 进行数据库筛选
- ✅ 前端传递的参数被正确处理
- ✅ 筛选结果准确

用户现在可以通过选择国家来筛选对应的服务器分组了!
