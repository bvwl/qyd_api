# 移除 raw_password 字段

## 更新日期
2026-01-24

## 更新说明

由于所有接口已经统一在 `password` 字段返回密码（管理员返回明文，普通用户返回密文），`raw_password` 字段已经不再使用，因此从 Schema 定义中移除。

## 修改内容

### 文件：`backend/app/schemas/server/account.py`

**修改前**：
```python
class Out(Base):
    """
    输出模型
    """
    message: str = Field('成功', description='提示信息')
    id: UUID = Field(..., description='ID')
    create_time: datetime = Field(..., description='创建时间')
    update_time: datetime = Field(..., description='更新时间')
    user_id: UUID | None = Field(None, description='关联用户ID')
    user: UserBase | None = Field(None, description='关联用户信息')
    
    # 解密后的原始密码（仅在特定场景返回）
    raw_password: str | None = Field(None, description='解密后的原始密码')  # ← 移除此字段
```

**修改后**：
```python
class Out(Base):
    """
    输出模型
    """
    message: str = Field('成功', description='提示信息')
    id: UUID = Field(..., description='ID')
    create_time: datetime = Field(..., description='创建时间')
    update_time: datetime = Field(..., description='更新时间')
    user_id: UUID | None = Field(None, description='关联用户ID')
    user: UserBase | None = Field(None, description='关联用户信息')
    
    # raw_password 字段已移除
```

## 影响范围

### 后端
- ✅ Schema 定义更简洁
- ✅ 不再有冗余字段
- ✅ API 返回数据更清晰

### 前端
- ✅ 无影响（前端已经不使用 raw_password）
- ✅ 代码已经统一使用 password 字段

## API 返回示例

### 管理员查询（之前）
```json
{
  "username": "user_7233165c",
  "password": "e/AMEwBiza74duK+y4U83w...",  // 密文
  "raw_password": "aB3dE7fGhJ9k"  // 明文（冗余）
}
```

### 管理员查询（现在）
```json
{
  "username": "user_7233165c",
  "password": "aB3dE7fGhJ9k"  // 直接是明文，无冗余字段
}
```

## 优势

1. **简洁性**：移除冗余字段，Schema 定义更简洁
2. **一致性**：所有地方都使用 password 字段，不会混淆
3. **清晰性**：API 返回数据更清晰，没有多余字段
4. **维护性**：减少字段数量，降低维护成本

## 服务状态

- ✅ 后端已重启
- ✅ Schema 定义已更新
- ✅ 功能正常运行
- ✅ 无破坏性变更

## 总结

移除了不再使用的 `raw_password` 字段，使代码更简洁清晰。所有功能继续正常工作，无需额外修改。

---

**相关文档**：
- [SERVER_ACCOUNT_PASSWORD_FIELD_UPDATE.md](./SERVER_ACCOUNT_PASSWORD_FIELD_UPDATE.md) - 密码字段返回方式更新
- [SERVER_ACCOUNT_FINAL_SUMMARY.md](./SERVER_ACCOUNT_FINAL_SUMMARY.md) - 最终总结
