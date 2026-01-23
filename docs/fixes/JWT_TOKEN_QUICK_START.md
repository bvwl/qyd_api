# JWT Token 快速开始指南

## 🚀 快速生成Token

### 方法1：使用API（推荐）

```bash
# 1. 先登录获取JWT
curl -X POST "http://localhost:6080/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }'

# 2. 使用登录JWT生成API Token（10年有效期）
curl -X POST "http://localhost:6080/v1/user/token/generate" \
  -H "Authorization: Bearer YOUR_LOGIN_JWT"
```

### 方法2：使用前端Dashboard

1. 访问 http://localhost:5173
2. 登录系统
3. 进入Dashboard页面
4. 点击"重新生成Token"按钮
5. 复制新生成的Token

## 📝 使用Token

### 在API请求中使用

```bash
# 使用Bearer Token格式
curl -X GET "http://localhost:6080/v1/project/info" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### 在Python脚本中使用

```python
import requests

API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
BASE_URL = "http://localhost:6080"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# 获取项目列表
response = requests.get(f"{BASE_URL}/v1/project/info", headers=headers)
projects = response.json()
print(projects)
```

### 在JavaScript中使用

```javascript
const API_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
const BASE_URL = 'http://localhost:6080';

// 使用fetch
fetch(`${BASE_URL}/v1/project/info`, {
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`
  }
})
.then(response => response.json())
.then(data => console.log(data));

// 使用axios
const axios = require('axios');
axios.get(`${BASE_URL}/v1/project/info`, {
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`
  }
})
.then(response => console.log(response.data));
```

## 🔍 Token信息

### Token格式

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjIwODQ0OTc5OTMsImlhdCI6MTc2OTEzNzk5MywianRpIjoiNTFkMmY5My0xNmVjLTRkN2MtYjM1Zi0xN2I2NzdjNjhkZTIiLCJpZCI6IjcyMzMxNjVjLWNiYWUtNGU2Ny05NTczLTQ1ZGY2ZWYzMjJlYyIsImVtYWlsIjoiMjIwMTEwMTEyMkBxcS5jb20iLCJyb2xlcyI6WyJNQU5VQUwiLCJJVCJdfQ.JDPDUOIm5-Z9bbZvmQeNNSyYK3u9pAF7TGTSwS2M_EQ
```

### Token包含的信息

- **用户ID**: 唯一标识用户
- **邮箱**: 用户邮箱地址
- **角色**: 用户的所有角色（ADMIN, GM, IT, MANUAL）
- **签发时间**: Token生成时间
- **过期时间**: Token过期时间（10年后）
- **唯一标识**: 每个Token的唯一ID

### 解码Token（仅查看，不验证）

```bash
# 使用jwt.io网站
# 访问 https://jwt.io
# 粘贴Token到Encoded框中查看内容
```

```python
# 使用Python解码（不验证签名）
import jwt
token = "YOUR_TOKEN_HERE"
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)
```

## ⚙️ Token管理

### 查看当前Token

```bash
# 获取当前用户的Token列表
curl -X GET "http://localhost:6080/v1/user/token?user_id=YOUR_USER_ID" \
  -H "Authorization: Bearer YOUR_LOGIN_JWT"
```

### 重新生成Token

```bash
# 生成新Token（旧Token自动失效）
curl -X POST "http://localhost:6080/v1/user/token/generate" \
  -H "Authorization: Bearer YOUR_LOGIN_JWT"
```

### 撤销Token

```bash
# 删除Token（需要管理员权限）
curl -X DELETE "http://localhost:6080/v1/user/token/{token_id}" \
  -H "Authorization: Bearer ADMIN_JWT"
```

## 🔒 安全建议

### 1. 存储Token

```bash
# ✅ 推荐：使用环境变量
export API_TOKEN="your_token_here"

# ✅ 推荐：使用配置文件（不提交到git）
echo "API_TOKEN=your_token_here" > .env
echo ".env" >> .gitignore

# ❌ 不推荐：硬编码在代码中
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # 不要这样做！
```

### 2. 定期更换

虽然Token有效期为10年，但建议：
- 每年更换一次Token
- 如果怀疑Token泄露，立即重新生成
- 角色变更后重新生成Token

### 3. 权限控制

Token包含角色信息，系统会自动验证：
- **ADMIN**: 所有权限
- **GM**: 项目管理权限
- **IT**: 技术资源访问权限
- **MANUAL**: 基础操作权限

## 🐛 常见问题

### Q1: Token过长，如何处理？

A: JWT Token约300-350字符，这是正常的。数据库使用TEXT字段存储，支持最大65535字符。

### Q2: Token验证失败？

```bash
# 检查Token格式
# 正确格式：Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# 错误格式：eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...（缺少Bearer前缀）

# 检查Token是否过期
# 使用jwt.io解码查看exp字段

# 检查Token是否被撤销
# 查询数据库tokens表，status=1为有效，status=2为失效
```

### Q3: 角色变更后Token还有效吗？

A: Token中的角色信息在生成时固定，不会自动更新。建议在角色变更后重新生成Token。

### Q4: 如何在Postman中使用？

```
1. 打开Postman
2. 选择请求
3. 点击"Authorization"标签
4. Type选择"Bearer Token"
5. 粘贴Token到Token输入框
6. 发送请求
```

### Q5: 多个用户可以共用一个Token吗？

A: 不建议。每个Token绑定特定用户，包含该用户的ID和角色信息。共用Token会导致权限混乱。

## 📚 相关文档

- `API_TOKEN_JWT_10YEARS.md` - 详细实现文档
- `API_TOKEN_JWT_10YEARS_COMPLETE.md` - 完整技术文档
- `backend/tests/test_jwt_token_generation.py` - 测试脚本

## 🎯 总结

JWT Token系统提供：
- ✅ 10年有效期，长期使用
- ✅ 包含用户信息，无需额外查询
- ✅ 标准JWT格式，易于集成
- ✅ 自动权限验证
- ✅ 安全可靠

开始使用吧！🚀
