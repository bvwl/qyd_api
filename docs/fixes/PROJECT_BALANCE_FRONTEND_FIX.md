# 项目余额前端修复

## 修复时间
2026-01-21

## 问题描述

前端项目余额页面控制台报错：
```
Uncaught TypeError: balance.toFixed is not a function
```

## 问题原因

### 后端返回的数据类型

后端使用 `Decimal` 类型存储余额和变量，序列化后返回**字符串类型**：

```json
{
  "balance": "1.000000",    // ← 字符串类型
  "variable": "0.000000"    // ← 字符串类型
}
```

**后端模型定义** (`backend/app/models/project.py`):
```python
class ProjectBalance(BaseModel):
    balance = fields.DecimalField(max_digits=18, decimal_places=6, description="余额")
    variable = fields.DecimalField(max_digits=18, decimal_places=6, description="变动余额")
```

### 前端代码问题

前端代码假设 `balance` 和 `variable` 是数字类型，直接调用 `.toFixed()` 方法：

```typescript
// ❌ 错误代码
render: (balance: number) => balance.toFixed(2)
```

但实际上后端返回的是字符串，字符串没有 `.toFixed()` 方法，导致报错。

## 解决方案

### 1. 修改前端渲染逻辑

在调用 `.toFixed()` 之前，先使用 `Number()` 转换为数字类型。

**修改文件**: `frontend/src/views/Project/ProjectBalance.tsx`

**修改前**:
```typescript
{
  title: '余额',
  dataIndex: 'balance',
  key: 'balance',
  render: (balance: number) => balance.toFixed(2),  // ❌ 假设是数字
},
{
  title: '变量',
  dataIndex: 'variable',
  key: 'variable',
  render: (variable: number) => {
    const color = variable > 0 ? 'green' : variable < 0 ? 'red' : 'default'
    return <span style={{ color }}>{variable > 0 ? '+' : ''}{variable.toFixed(2)}</span>
  },
},
```

**修改后**:
```typescript
{
  title: '余额',
  dataIndex: 'balance',
  key: 'balance',
  render: (balance: number | string) => Number(balance).toFixed(2),  // ✅ 先转换为数字
},
{
  title: '变量',
  dataIndex: 'variable',
  key: 'variable',
  render: (variable: number | string) => {
    const num = Number(variable)  // ✅ 先转换为数字
    const color = num > 0 ? 'green' : num < 0 ? 'red' : 'default'
    return <span style={{ color }}>{num > 0 ? '+' : ''}{num.toFixed(2)}</span>
  },
},
```

### 2. 更新 TypeScript 类型定义

更新类型定义以反映实际的数据类型。

**修改文件**: `frontend/src/types/index.ts`

**修改前**:
```typescript
export interface ProjectBalance {
  id: string
  balance: number      // ❌ 不准确
  variable: number     // ❌ 不准确
  history?: any[]
  account_id: string
  account?: ProjectAccount
  create_time: string
  update_time: string
}
```

**修改后**:
```typescript
export interface ProjectBalance {
  id: string
  balance: number | string   // ✅ 后端返回字符串类型的 Decimal
  variable: number | string  // ✅ 后端返回字符串类型的 Decimal
  history?: any[]
  account_id: string
  account?: ProjectAccount
  create_time: string
  update_time: string
}
```

## 为什么后端返回字符串？

### Decimal 类型的序列化

Python 的 `Decimal` 类型在 JSON 序列化时会转换为字符串，以保持精度：

```python
from decimal import Decimal
import json

balance = Decimal("1.000000")
print(json.dumps({"balance": balance}))
# 输出: {"balance": "1.000000"}
```

### 精度问题

使用字符串可以避免浮点数精度问题：

```javascript
// JavaScript 浮点数精度问题
0.1 + 0.2 === 0.3  // false
0.1 + 0.2          // 0.30000000000000004

// 使用字符串保持精度
Number("0.1") + Number("0.2")  // 0.3
```

## 其他可能受影响的字段

检查其他使用 `DecimalField` 的模型，确保前端正确处理：

| 模型 | 字段 | 类型 | 前端处理 |
|------|------|------|---------|
| ProjectBalance | balance | Decimal | ✅ 已修复 |
| ProjectBalance | variable | Decimal | ✅ 已修复 |

目前只有 `ProjectBalance` 模型使用了 `DecimalField`。

## 测试验证

### 测试场景

1. **查看余额列表**
   - 余额显示正确（保留两位小数）
   - 变量显示正确（正数绿色带+号，负数红色）

2. **编辑余额**
   - 可以正常编辑余额和变量
   - 保存后显示正确

3. **创建余额记录**
   - 可以正常创建
   - 显示正确

### 测试数据

```json
{
  "balance": "1234.567890",
  "variable": "-123.450000"
}
```

**预期显示**:
- 余额: `1234.57`
- 变量: `-123.45` (红色)

## 最佳实践

### 前端处理数字字符串

当后端返回数字字符串时，前端应该：

1. **类型定义要准确**
   ```typescript
   balance: number | string  // 明确可能是字符串
   ```

2. **使用前先转换**
   ```typescript
   const num = Number(balance)  // 转换为数字
   num.toFixed(2)               // 再调用数字方法
   ```

3. **处理边界情况**
   ```typescript
   const num = Number(balance)
   if (isNaN(num)) {
     return '-'  // 处理无效数字
   }
   return num.toFixed(2)
   ```

### 后端返回数字的选择

**选项1: 返回字符串（当前方案）**
- ✅ 保持精度
- ✅ 避免浮点数问题
- ⚠️ 前端需要转换

**选项2: 返回浮点数**
- ✅ 前端直接使用
- ❌ 可能有精度问题
- ❌ 不适合金融数据

**结论**: 对于金融相关的数据（余额、金额等），使用字符串更安全。

## 相关文件

### 前端文件
- ✅ `frontend/src/views/Project/ProjectBalance.tsx` - 余额页面（已修复）
- ✅ `frontend/src/types/index.ts` - 类型定义（已更新）

### 后端文件（参考）
- `backend/app/models/project.py` - 模型定义
- `backend/app/schemas/project/balance.py` - Schema 定义

### 文档
- ✅ `docs/fixes/PROJECT_BALANCE_FRONTEND_FIX.md` - 本文档
- `docs/fixes/PROJECT_BALANCE_API_FIX.md` - 后端 API 修复

## 总结

✅ 修复了前端 `.toFixed()` 调用错误
✅ 更新了 TypeScript 类型定义
✅ 使用 `Number()` 转换字符串为数字
✅ 保持了后端 Decimal 类型的精度优势
✅ 前端页面现在可以正常显示余额数据

前端现在可以正确处理后端返回的 Decimal 字符串类型数据！
