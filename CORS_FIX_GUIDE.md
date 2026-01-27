# CORS 跨域问题修复指南

## 🐛 问题描述

前端访问后端 API 时出现 CORS 错误：

```
Access to XMLHttpRequest at 'http://192.168.13.6:6080/api/v1/user/login' 
from origin 'http://192.168.13.6:8080' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## 🔍 问题原因

前端使用 8080 端口访问，但后端的 CORS 配置中没有包含 `http://192.168.13.6:8080`。

当前 CORS 配置：
```env
CORS_ORIGINS=http://192.168.13.6,http://192.168.13.6:80
```

需要添加：
```env
CORS_ORIGINS=http://192.168.13.6,http://192.168.13.6:80,http://192.168.13.6:8080
```

## 🔧 快速修复

### 方法 1：使用自动修复脚本（推荐）

```bash
# 在服务器上运行
cd /opt/zy/qyd_api
chmod +x fix-cors.sh
bash fix-cors.sh
```

脚本会自动：
1. ✅ 检查当前 CORS 配置
2. ✅ 添加 8080 端口
3. ✅ 重启后端服务

### 方法 2：手动修改配置

```bash
# 1. 编辑 .env 文件
vim .env

# 2. 修改 CORS_ORIGINS 行
CORS_ORIGINS=http://192.168.13.6,http://192.168.13.6:80,http://192.168.13.6:8080

# 3. 重启后端服务
docker compose -f docker-compose.backend.yml restart backend-api

# 4. 查看日志确认
docker compose -f docker-compose.backend.yml logs -f backend-api
```

## 📝 CORS 配置说明

### 配置格式

```env
CORS_ORIGINS=origin1,origin2,origin3
```

**注意**：
- 多个源用逗号分隔
- 不要有空格
- 必须包含协议（http:// 或 https://）
- 端口号必须明确指定（除了默认端口 80 和 443）

### 常见配置示例

#### 开发环境

```env
# 允许本地开发
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000
```

#### 生产环境（单服务器）

```env
# 允许同一服务器的不同端口
CORS_ORIGINS=http://192.168.13.6,http://192.168.13.6:80,http://192.168.13.6:8080
```

#### 生产环境（前后端分离）

```env
# 允许前端服务器访问
CORS_ORIGINS=http://192.168.1.10,http://192.168.1.10:80,http://192.168.1.10:8080
```

#### 生产环境（使用域名）

```env
# 允许域名访问
CORS_ORIGINS=https://www.example.com,https://app.example.com
```

#### 生产环境（多个域名和端口）

```env
# 允许多个来源
CORS_ORIGINS=http://192.168.13.6:8080,https://www.example.com,https://app.example.com
```

## 🔒 安全建议

### ❌ 不推荐的配置

```env
# 允许所有来源（不安全！）
CORS_ORIGINS=*
```

### ✅ 推荐的配置

```env
# 只允许特定的来源
CORS_ORIGINS=https://www.example.com,https://app.example.com
```

### 安全检查清单

- [ ] 不要使用 `*` 允许所有来源
- [ ] 只添加需要的域名和端口
- [ ] 生产环境使用 HTTPS
- [ ] 定期审查 CORS 配置
- [ ] 使用具体的域名而不是 IP（生产环境）

## 🧪 验证 CORS 配置

### 方法 1：浏览器开发者工具

1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 刷新页面
4. 查看请求的 Response Headers
5. 确认有 `Access-Control-Allow-Origin` 头

### 方法 2：使用 curl 测试

```bash
# 测试 CORS 预检请求
curl -X OPTIONS http://192.168.13.6:6080/api/v1/user/login \
  -H "Origin: http://192.168.13.6:8080" \
  -H "Access-Control-Request-Method: POST" \
  -v

# 应该看到响应头包含：
# Access-Control-Allow-Origin: http://192.168.13.6:8080
# Access-Control-Allow-Methods: POST, GET, OPTIONS, ...
```

### 方法 3：查看后端日志

```bash
# 查看后端日志
docker compose -f docker-compose.backend.yml logs -f backend-api

# 应该看到类似的日志：
# INFO: CORS enabled for origins: ['http://192.168.13.6:8080', ...]
```

## 🐛 常见问题

### 问题 1：修改配置后仍然报错

**原因**：浏览器缓存或后端服务未重启

**解决**：
```bash
# 1. 清除浏览器缓存（Ctrl+Shift+Delete）
# 2. 重启后端服务
docker compose -f docker-compose.backend.yml restart backend-api

# 3. 硬刷新页面（Ctrl+Shift+R）
```

### 问题 2：OPTIONS 请求失败

**原因**：CORS 预检请求被拒绝

**解决**：
```bash
# 检查后端日志
docker compose -f docker-compose.backend.yml logs backend-api | grep CORS

# 确认 CORS 中间件已启用
```

### 问题 3：只有部分请求失败

**原因**：某些 API 路由没有应用 CORS 中间件

**解决**：
```python
# 检查 backend/app/main.py
# 确保 CORS 中间件在所有路由之前添加
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题 4：使用域名时 CORS 失败

**原因**：CORS 配置中使用了 IP 而不是域名

**解决**：
```env
# 如果前端使用域名访问，CORS 也要配置域名
CORS_ORIGINS=https://www.example.com,https://app.example.com
```

## 📚 相关文档

- [FastAPI CORS 文档](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS 文档](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS)
- [前后端分离部署指南](SEPARATE_DEPLOYMENT_GUIDE.md)

## 🔄 更新历史

- **2026-01-27**: 添加 8080 端口支持
- **2026-01-27**: 创建自动修复脚本

---

**最后更新**: 2026-01-27  
**版本**: v1.0.0
