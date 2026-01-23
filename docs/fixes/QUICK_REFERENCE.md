# 权限管理API快速参考

## 🚀 新增API端点

### 1. 获取路由树
```bash
GET /v1/user/route/tree?status=1
Authorization: Bearer {token}
```

**响应**: 树形结构的路由列表

### 2. 获取角色路由权限
```bash
GET /v1/user/role/{role_id}/routes
Authorization: Bearer {token}
```

**响应**: 该角色拥有的路由（树形结构）

### 3. 设置角色路由权限
```bash
POST /v1/user/role/{role_id}/routes
Authorization: Bearer {token}
Content-Type: application/json

["route_id_1", "route_id_2", "route_id_3"]
```

**响应**: 
```json
{
  "message": "权限设置成功",
  "count": 3
}
```

## 📝 快速测试

```bash
# 运行完整测试
bash test_permission_complete.sh

# 查看API文档
open http://127.0.0.1:6080/docs

# 访问前端权限管理页面
open http://localhost:3000/user/permission
```

## 🔑 测试账号

```
邮箱: zhiyu
密码: 2201101122@qq.com
角色: 管理员 (ADMIN)
```

## ✅ 状态

- ✅ 后端API已实现
- ✅ 数据格式已匹配
- ✅ 所有测试通过
- ✅ 前端可正常使用
