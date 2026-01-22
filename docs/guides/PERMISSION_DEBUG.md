# 权限管理页面调试指南

## 问题：权限管理页面显示空白

### 调试步骤

#### 1. 检查后端服务
```bash
# 检查后端是否运行
curl http://127.0.0.1:6080/docs

# 测试角色列表API
curl http://127.0.0.1:6080/v1/user/role?page=1&limit=10
```

#### 2. 检查前端控制台
打开浏览器开发者工具（F12），查看：
- Console标签：是否有JavaScript错误
- Network标签：API请求是否成功
- 查看API响应数据格式

#### 3. 使用简化测试页面
我已经创建了一个简化的测试页面：
```
访问: http://127.0.0.1:5173/user/permission
```

这个页面会显示：
- 角色数量
- 路由数量
- 原始API响应数据

#### 4. 常见问题

##### 问题1：API返回401未授权
**原因**：JWT token过期或无效

**解决**：
1. 退出登录
2. 重新登录
3. 再次访问权限管理页面

##### 问题2：API返回404
**原因**：后端路由未正确注册

**解决**：
```bash
# 检查后端路由
curl http://127.0.0.1:6080/openapi.json | grep "/v1/user/route/tree"
```

##### 问题3：数据加载但不显示
**原因**：前端渲染逻辑问题

**解决**：
1. 打开浏览器控制台
2. 查看是否有React错误
3. 检查数据格式是否正确

#### 5. 手动测试API

##### 测试角色列表
```bash
curl "http://127.0.0.1:6080/v1/user/role?page=1&limit=10"
```

预期响应：
```json
{
  "message": "成功",
  "count": -1,
  "num": 4,
  "items": [...]
}
```

##### 测试路由树（需要登录）
```bash
# 1. 先登录获取token
TOKEN=$(curl -s -X POST "http://127.0.0.1:6080/v1/user/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"zhiyu","password":"zhiyu666"}' | jq -r '.access_token')

# 2. 使用token访问路由树
curl "http://127.0.0.1:6080/v1/user/route/tree?status=1" \
  -H "Authorization: Bearer $TOKEN"
```

预期响应：
```json
[
  {
    "id": "...",
    "name": "dashboard",
    "path": "/dashboard",
    "title": "仪表盘",
    "children": []
  },
  ...
]
```

#### 6. 检查数据库
```bash
cd backend
python test_permission_apis.py
```

应该看到：
- 4个角色
- 28个路由
- 权限配置正常

### 当前状态

- ✅ 后端服务运行正常
- ✅ 数据库数据正常
- ✅ API端点工作正常
- ❓ 前端页面显示问题

### 下一步

1. 访问简化测试页面：http://127.0.0.1:5173/user/permission
2. 查看浏览器控制台输出
3. 检查API响应数据
4. 根据错误信息进行修复

### 联系支持

如果问题仍然存在，请提供：
1. 浏览器控制台截图
2. Network标签中的API请求/响应
3. 错误信息

## 临时解决方案

如果需要立即使用权限管理功能，可以：

### 方案1：使用API直接配置
```bash
# 获取角色ID
curl "http://127.0.0.1:6080/v1/user/role"

# 获取路由ID
curl "http://127.0.0.1:6080/v1/user/route/tree?status=1" \
  -H "Authorization: Bearer $TOKEN"

# 为角色分配权限
curl -X POST "http://127.0.0.1:6080/v1/user/role/{role_id}/routes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '["route_id_1", "route_id_2", ...]'
```

### 方案2：使用Python脚本
```bash
cd backend
python demo_permission_setup.py
```

这会为所有角色配置典型的权限。
