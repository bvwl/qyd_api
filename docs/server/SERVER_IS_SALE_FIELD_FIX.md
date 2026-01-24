# 服务器 is_sale 字段修复

## 问题描述

在新增服务器时报错：
```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["body", "is_sale"],
      "msg": "Input should be 1 or 2",
      "input": 0,
      "ctx": {"expected": "1 or 2"}
    }
  ]
}
```

**原因**：前端传递的 `is_sale` 值为 `0`，但后端期望的是 `1` 或 `2`。

## 字段含义

### 后端定义

**文件**: `backend/app/models/server.py`

```python
class IsSale(IntEnum):
    YES = 1  # 可以出售
    NO = 2   # 不可以出售
```

**含义**：
- `1` = 可以出售（YES）
- `2` = 不可以出售（NO）

### Schema 定义

**文件**: `backend/app/schemas/server/info.py`

```python
is_sale: IsSale = Field(IsSale.YES, description='是否销售(1:是,2:否)')
```

## 修复内容

### 文件：`frontend/src/views/Server/ServerList.tsx`

#### 1. 修复默认值

**修复前**：
```typescript
form.setFieldsValue({
  status: Status.NORMAL,
  is_sale: 0,  // ❌ 错误：0 不是有效值
  ssh_port: 22,
})
```

**修复后**：
```typescript
form.setFieldsValue({
  status: Status.NORMAL,
  is_sale: 1,  // ✅ 正确：1 表示可以出售
  ssh_port: 22,
})
```

#### 2. 修复表单选项

**修复前**：
```typescript
<Form.Item
  label="是否出售"
  name="is_sale"
  rules={[{ required: true, message: '请选择是否出售' }]}
>
  <Select placeholder="请选择是否出售">
    <Select.Option value={0}>未出售</Select.Option>  {/* ❌ 错误 */}
    <Select.Option value={1}>已出售</Select.Option>
  </Select>
</Form.Item>
```

**修复后**：
```typescript
<Form.Item
  label="是否可以出售"
  name="is_sale"
  rules={[{ required: true, message: '请选择是否可以出售' }]}
>
  <Select placeholder="请选择是否可以出售">
    <Select.Option value={1}>可以出售</Select.Option>    {/* ✅ 正确 */}
    <Select.Option value={2}>不可以出售</Select.Option>  {/* ✅ 正确 */}
  </Select>
</Form.Item>
```

#### 3. 修复表格显示

**修复前**：
```typescript
{
  title: '是否出售',
  dataIndex: 'is_sale',
  key: 'is_sale',
  render: (is_sale: number) => (
    <Tag color={is_sale === 1 ? 'orange' : 'default'}>
      {is_sale === 1 ? '已出售' : '未出售'}
    </Tag>
  ),
}
```

**修复后**：
```typescript
{
  title: '是否可以出售',
  dataIndex: 'is_sale',
  key: 'is_sale',
  render: (is_sale: number) => (
    <Tag color={is_sale === 1 ? 'green' : 'default'}>
      {is_sale === 1 ? '可以出售' : '不可以出售'}
    </Tag>
  ),
}
```

#### 4. 修复搜索筛选

**修复前**：
```typescript
<Select
  placeholder="是否出售"
  value={searchIsSale}
  onChange={setSearchIsSale}
  style={{ width: 120 }}
  allowClear
>
  <Select.Option value={0}>未出售</Select.Option>  {/* ❌ 错误 */}
  <Select.Option value={1}>已出售</Select.Option>
</Select>
```

**修复后**：
```typescript
<Select
  placeholder="是否可以出售"
  value={searchIsSale}
  onChange={setSearchIsSale}
  style={{ width: 140 }}
  allowClear
>
  <Select.Option value={1}>可以出售</Select.Option>    {/* ✅ 正确 */}
  <Select.Option value={2}>不可以出售</Select.Option>  {/* ✅ 正确 */}
</Select>
```

## 修复对比

### 值的对应关系

| 修复前 | 修复后 | 含义 |
|--------|--------|------|
| `0` ❌ | `1` ✅ | 可以出售 |
| `1` ⚠️ | `2` ✅ | 不可以出售 |

### 文案对比

| 位置 | 修复前 | 修复后 |
|------|--------|--------|
| 表单标签 | "是否出售" | "是否可以出售" |
| 选项1 | "未出售" | "可以出售" |
| 选项2 | "已出售" | "不可以出售" |
| 表格列 | "是否出售" | "是否可以出售" |
| 表格标签1 | "已出售" (橙色) | "可以出售" (绿色) |
| 表格标签2 | "未出售" (灰色) | "不可以出售" (灰色) |

## 测试方法

### 1. 测试新增服务器

1. 进入"服务器管理" → "服务器列表"
2. 点击"新增服务器"
3. 填写表单：
   - 服务器地址：`82.152.142.11`
   - SSH端口：`9527`
   - 域名：`zd1.0n.lv`
   - 代理端口：`32000`
   - 分组：选择一个分组
   - 状态：正常
   - **是否可以出售**：选择"可以出售"或"不可以出售"
4. 点击"确定"
5. 验证：
   - ✅ 创建成功，无 422 错误
   - ✅ 表格中显示正确的标签

### 2. 测试编辑服务器

1. 点击某个服务器的"编辑"按钮
2. 修改"是否可以出售"字段
3. 点击"确定"
4. 验证：
   - ✅ 更新成功
   - ✅ 表格中显示更新后的值

### 3. 测试搜索筛选

1. 在搜索栏选择"是否可以出售"
2. 选择"可以出售"或"不可以出售"
3. 点击"搜索"
4. 验证：
   - ✅ 只显示符合条件的服务器
   - ✅ 筛选正确

## 语义说明

### 字段含义

**is_sale** = "是否可以出售"

- **值 `1`（可以出售）**：表示这个服务器可以出售给客户
- **值 `2`（不可以出售）**：表示这个服务器不可以出售（可能是自用、测试等）

### 为什么不用布尔值？

后端使用 `IntEnum` 而不是布尔值的原因：
1. **扩展性**：未来可能需要更多状态（如"已出售"、"预留"等）
2. **数据库兼容性**：整数类型在数据库中更通用
3. **一致性**：与其他枚举字段（如 `status`）保持一致

## 相关文档

- [SERVER_ACCOUNT_FINAL_SUMMARY.md](./SERVER_ACCOUNT_FINAL_SUMMARY.md) - 服务器账号功能总结

## 总结

### 修复的问题

- ✅ 修复新增服务器时的 422 错误
- ✅ 修正字段值（0 → 1, 1 → 2）
- ✅ 更新文案（更清晰的语义）
- ✅ 统一所有相关位置

### 修改的文件

- `frontend/src/views/Server/ServerList.tsx` - 修复默认值、表单选项、表格显示、搜索筛选

### 服务状态

- ✅ 前端会自动热更新
- ✅ 无需重启后端
- ✅ 刷新页面即可生效

现在新增服务器功能正常，`is_sale` 字段的值和含义都正确了！
