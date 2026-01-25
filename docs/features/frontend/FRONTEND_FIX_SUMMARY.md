# 前端空字符串处理修复总结

## 问题
编辑项目账号时，清空某个字段（如 password）会传空字符串 `""` 给后端，导致该字段被错误更新。

## 原因
前端表单清空字段时传 `""`，而不是 `undefined`，导致后端的 `exclude_unset=True` 无法正确工作。

## 解决方案
在提交前过滤掉空字符串：

```typescript
const filteredValues = Object.entries(values).reduce((acc, [key, value]) => {
  if (value === '') {
    return acc  // 不包含该字段
  }
  acc[key] = value
  return acc
}, {} as any)
```

## 修改文件
- `frontend/src/views/Project/ProjectAccount.tsx` - `handleSubmit` 函数

## 效果
- ✅ 清空字段 = 不修改该字段
- ✅ 填写字段 = 更新该字段
- ✅ 后端 `exclude_unset=True` 正确工作

## 示例

**修改前：**
```json
{
  "account": "test@example.com",
  "password": "",  // ❌ 会覆盖数据库中的密码
  "status": 1
}
```

**修改后：**
```json
{
  "account": "test@example.com",
  // password 不传，数据库保持不变 ✅
  "status": 1
}
```

## 详细文档
查看 [FRONTEND_EMPTY_STRING_FIX.md](FRONTEND_EMPTY_STRING_FIX.md)
