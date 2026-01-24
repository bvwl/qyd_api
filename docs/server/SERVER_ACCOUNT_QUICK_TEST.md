# 服务器账号功能快速测试指南

## 当前状态

✅ 后端服务运行中: http://127.0.0.1:6080
✅ 前端服务运行中: http://localhost:3000 或 http://localhost:5173
✅ API 文档: http://127.0.0.1:6080/docs

## 快速测试步骤

### 1. 前端测试（推荐）

#### 步骤 1: 登录系统
1. 打开浏览器访问前端地址
2. 使用测试账号登录：
   - 邮箱: `zhiyu`
   - 密码: `2201101122@qq.com`

#### 步骤 2: 进入仪表盘
1. 登录后自动跳转到仪表盘
2. 查看页面布局：
   - 左侧：API Token 卡片
   - 右侧：服务器账号卡片

#### 步骤 3: 生成服务器账号
1. 点击"生成服务器账号"按钮
2. 确认弹窗
3. 查看生成结果：
   - 用户名格式：`user_xxxxxxxx`
   - 密码长度：12位
   - 弹窗提示保存密码

#### 步骤 4: 查看密码
1. 密码默认隐藏（显示为 ••••••••）
2. 点击眼睛图标 👁
3. 首次点击：调用 API 解密密码
4. 密码显示为明文
5. 再次点击：隐藏密码

#### 步骤 5: 复制功能
1. 点击用户名输入框的复制图标 📋
2. 验证用户名已复制到剪贴板
3. 点击密码输入框的复制图标 📋
4. 验证密码已复制到剪贴板

#### 步骤 6: 测试重复生成
1. 再次点击"生成服务器账号"
2. 应该返回现有账号（不创建新账号）
3. 提示"服务器账号已存在"

### 2. API 测试（开发者）

#### 准备工作：获取 Token

```bash
# 登录获取 Token
curl -X POST 'http://127.0.0.1:6080/v1/user/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }'

# 保存返回的 access_token
export TOKEN="返回的access_token"
```

#### 测试 1: 生成服务器账号

```bash
curl -X POST 'http://127.0.0.1:6080/v1/server/account/generate' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json'
```

**预期返回**:
```json
{
  "message": "成功",
  "id": "uuid",
  "username": "user_7233165c",
  "password": "Base64加密密文",
  "raw_password": "aB3dE7fGhJ9k",
  "user_id": "uuid",
  "create_time": "2026-01-24 01:30:00",
  "update_time": "2026-01-24 01:30:00"
}
```

**验证点**:
- ✅ username 格式为 `user_xxxxxxxx`
- ✅ raw_password 长度为 12 位
- ✅ raw_password 包含大小写字母和数字

#### 测试 2: 重复生成（应返回现有账号）

```bash
curl -X POST 'http://127.0.0.1:6080/v1/server/account/generate' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json'
```

**预期返回**:
- 返回相同的账号信息
- 可能包含 raw_password（解密后的密码）

#### 测试 3: 获取账号列表

```bash
curl 'http://127.0.0.1:6080/v1/server/account?page=1&limit=10' \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**:
```json
{
  "message": "成功",
  "count": 1,
  "num": 1,
  "items": [
    {
      "id": "uuid",
      "username": "user_7233165c",
      "password": "Base64加密密文",
      "user_id": "uuid",
      "create_time": "2026-01-24 01:30:00",
      "update_time": "2026-01-24 01:30:00"
    }
  ]
}
```

**验证点**:
- ✅ 只返回当前用户的账号
- ✅ password 是加密后的密文（Base64）
- ✅ 不包含 raw_password

#### 测试 4: 获取解密密码

```bash
# 先获取账号ID
ACCOUNT_ID=$(curl -s 'http://127.0.0.1:6080/v1/server/account?page=1&limit=1' \
  -H "Authorization: Bearer $TOKEN" | jq -r '.items[0].id')

# 获取解密密码
curl "http://127.0.0.1:6080/v1/server/account/$ACCOUNT_ID/password" \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**:
```json
{
  "message": "成功",
  "id": "uuid",
  "username": "user_7233165c",
  "password": "Base64加密密文",
  "raw_password": "aB3dE7fGhJ9k",
  "user_id": "uuid",
  "create_time": "2026-01-24 01:30:00",
  "update_time": "2026-01-24 01:30:00"
}
```

**验证点**:
- ✅ 返回 raw_password（解密后的密码）
- ✅ raw_password 与首次生成时相同

#### 测试 5: 测试权限控制（尝试查看其他用户的密码）

```bash
# 使用另一个用户的 Token
export TOKEN2="另一个用户的token"

# 尝试查看第一个用户的账号密码
curl "http://127.0.0.1:6080/v1/server/account/$ACCOUNT_ID/password" \
  -H "Authorization: Bearer $TOKEN2"
```

**预期返回**:
```json
{
  "detail": "无权查看此账号密码"
}
```

**验证点**:
- ✅ 返回 403 错误
- ✅ 提示无权查看

### 3. AES 加密测试

```bash
cd backend
python test_aes_encryption.py
```

**预期输出**:
```
============================================================
AES 加密解密测试
============================================================

原始密码: TestPassword123!@#
用户ID: 7233165c-cbae-4e67-9573-45df6ef322ec

加密后 (Base64): xxxxxxxxxxxxxxxxxxxxx
加密后长度: 44 字符

解密后: TestPassword123!@#

✅ 加密解密测试通过！

============================================================
测试不同用户使用不同密钥
============================================================

用户1加密: xxxxxxxxxxxxxxxxxxxxx
用户2加密: yyyyyyyyyyyyyyyyyyyyy

✅ 不同用户使用不同密钥！

✅ 正确：用户2无法解密用户1的密码

============================================================
测试多种密码格式
============================================================

✅ 密码测试通过: simple
✅ 密码测试通过: Complex@Pass123
✅ 密码测试通过: 中文密码测试
✅ 密码测试通过: !@#$%^&*()_+-=[]{}|;:',.<>?/
✅ 密码测试通过: aaaaaaaaaaaaaaaaaaa...

============================================================
所有测试通过！
============================================================
```

## 测试检查清单

### 功能测试
- [ ] 用户可以生成服务器账号
- [ ] 用户名格式正确（`user_xxxxxxxx`）
- [ ] 密码长度为 12 位
- [ ] 密码包含大小写字母和数字
- [ ] 重复生成返回现有账号
- [ ] 首次生成弹窗显示密码
- [ ] 密码默认隐藏
- [ ] 点击眼睛图标可查看密码
- [ ] 点击复制图标可复制用户名/密码
- [ ] 仪表盘布局正确（左右对称）

### 权限测试
- [ ] 用户只能查看自己的账号列表
- [ ] 用户只能查看自己的账号密码
- [ ] 管理员也只能看自己的账号
- [ ] 尝试查看其他用户密码返回 403

### 安全测试
- [ ] 数据库存储的是加密密文
- [ ] 不同用户的密文不同（即使密码相同）
- [ ] 解密功能正常
- [ ] AES 加密测试全部通过

### 用户名去重测试
- [ ] 用户名不重复
- [ ] 重复时自动添加随机后缀
- [ ] 后缀格式正确（4位小写字母+数字）

## 常见问题

### Q1: 生成账号时报错 "Out object has no field raw_password"

**原因**: Schema 定义中缺少 `raw_password` 字段

**解决**: 已修复，`backend/app/schemas/server/account.py` 中的 `Out` 类已添加该字段

### Q2: 管理员看到其他用户的账号

**原因**: 权限控制未正确实现

**解决**: 已修复，所有用户（包括管理员）都只能查看自己的账号

### Q3: 密码长度不是 12 位

**原因**: 密码生成代码使用了错误的长度

**解决**: 已修复，密码生成长度改为 12 位

### Q4: 用户名重复

**原因**: 未实现用户名去重机制

**解决**: 已修复，添加了自动去重逻辑，重复时添加随机后缀

## 下一步

### 可选优化

1. **密钥管理**: 将 "9527" 改为环境变量
2. **密码策略**: 支持自定义密码长度和字符集
3. **批量操作**: 支持批量生成账号（管理员功能）
4. **账号状态**: 添加启用/禁用状态
5. **使用记录**: 记录账号使用情况

### 生产部署

1. **HTTPS**: 配置 HTTPS 证书
2. **数据库备份**: 定期备份数据库
3. **日志监控**: 监控账号生成和访问日志
4. **性能优化**: 添加 Redis 缓存
5. **安全审计**: 定期安全审计

## 相关文档

- [SOCKS5_ACCOUNT_IMPLEMENTATION_SUMMARY.md](./SOCKS5_ACCOUNT_IMPLEMENTATION_SUMMARY.md) - 完整实现总结
- [SOCKS5_ACCOUNT_AES_ENCRYPTION.md](./SOCKS5_ACCOUNT_AES_ENCRYPTION.md) - AES 加密详细说明
- [SERVER_ACCOUNT_FINAL_FIX.md](./SERVER_ACCOUNT_FINAL_FIX.md) - 最终修复总结

## 联系方式

如有问题，请查看相关文档或联系开发团队。
