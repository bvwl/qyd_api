# 🚀 API Token 实现 - 快速开始

## ⚡ 核心变更

注册接口不再返回 JWT `access_token`，改为返回 API `api_token`

## 📝 API Token 生成规则

```
API Token = MD5(邮箱 + 13位时间戳 + "9527")
```

## 🔧 修改的文件

1. **backend/app/core/tools.py** - 添加 `gen_api_token()` 函数
2. **backend/app/apis/v1/user/auth.py** - 修改注册接口

## 🧪 快速测试

### 1. 测试 Token 生成函数

```bash
python backend/test_gen_api_token.py
```

### 2. 测试注册接口

```bash
# 启动后端服务
cd backend
python start.py

# 在另一个终端运行测试
python backend/test_register_api_token.py
```

### 3. 手动测试

```bash
curl -X POST "http://127.0.0.1:6080/v1/user/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "nickname": "测试用户"
  }'
```

**预期响应：**

```json
{
  "message": "注册成功",
  "user": {
    "id": "...",
    "email": "test@example.com",
    "nickname": "测试用户",
    "roles": [{"code": "MANUAL", "name": "手动操作员"}]
  },
  "api_token": "32位MD5字符串"
}
```

## ⚠️ 重要提示

1. **需要重启后端服务**才能生效
2. 注册响应中**不再包含** `access_token`
3. 登录接口**仍然返回** JWT `access_token`（未修改）
4. API Token 会自动保存到数据库 `tokens` 表

## 📖 详细文档

查看完整文档：`backend/API_TOKEN_IMPLEMENTATION.md`

## 🎯 前端需要修改

前端注册成功后的处理逻辑需要调整：
- 不再缓存 JWT token
- 改为处理 `api_token`
- 或者注册后引导用户去登录页面
