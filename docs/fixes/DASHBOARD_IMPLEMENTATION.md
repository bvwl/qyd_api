# 🎯 仪表盘功能实现文档

## 📋 功能概述

实现了基于角色的仪表盘系统，不同角色的用户看到不同的统计数据和项目列表。

## 🎭 角色权限说明

### ADMIN（管理员）
- ✅ 显示所有用户数量
- ✅ 显示所有项目数量
- ✅ 显示所有账户数量
- ✅ 查看所有项目列表

### GM（项目管理员）
- ✅ 显示所有项目数量
- ✅ 显示所有账户数量
- ✅ 查看所有项目列表
- ❌ 不显示用户数量

### IT（技术人员）
- ✅ 显示自己关联的项目数量
- ✅ 显示自己项目下的账户数量
- ✅ 只能查看自己关联的项目
- ❌ 不显示用户数量

### MANUAL（手动操作员）
- ✅ 显示自己关联的项目数量
- ✅ 显示自己项目下的账户数量
- ✅ 只能查看自己关联的项目
- ❌ 不显示用户数量

## 🔧 实现细节

### 后端 API

#### 1. 获取仪表盘统计

**接口：** `GET /v1/user/dashboard/stats`

**权限：** 需要登录（JWT Token）

**响应示例（管理员）：**
```json
{
  "user_count": 10,
  "project_count": 25,
  "account_count": 150,
  "role": "ADMIN",
  "user_email": "zhiyu",
  "user_nickname": "至宇"
}
```

**响应示例（IT/MANUAL）：**
```json
{
  "user_count": null,
  "project_count": 5,
  "account_count": 30,
  "role": "IT",
  "user_email": "it@example.com",
  "user_nickname": "技术人员"
}
```

#### 2. 获取项目列表统计

**接口：** `GET /v1/user/dashboard/projects`

**权限：** 需要登录（JWT Token）

**响应示例：**
```json
[
  {
    "id": "uuid",
    "name": "项目A",
    "account_count": 50,
    "status": 1
  },
  {
    "id": "uuid",
    "name": "项目B",
    "account_count": 30,
    "status": 1
  }
]
```

### 前端页面

#### 页面结构

1. **欢迎信息卡片**
   - 显示用户昵称
   - 显示当前角色
   - 显示用户邮箱

2. **统计卡片**
   - 用户总数（仅管理员）
   - 项目数量
   - 账户数量
   - 在线用户（仅管理员）

3. **项目列表表格**
   - 项目名称
   - 账户数量
   - 项目状态

4. **角色提示**（IT/MANUAL）
   - 提示用户只能查看自己的项目

## 📁 文件结构

### 后端文件

```
backend/app/apis/v1/user/
├── dashboard.py          # 仪表盘API（新增）
└── __init__.py          # 注册仪表盘路由（修改）
```

### 前端文件

```
frontend/src/
├── views/Dashboard/
│   └── index.tsx        # 仪表盘页面（新增）
├── api/user.ts          # 添加仪表盘API函数（修改）
└── router/index.tsx     # 添加仪表盘路由（修改）
```

## 🚀 使用方法

### 1. 启动服务

```bash
# 后端
cd backend
python start.py

# 前端
cd frontend
npm run dev
```

### 2. 访问仪表盘

登录后会自动跳转到仪表盘页面：`http://localhost:5173/dashboard`

### 3. 测试API

```bash
# 测试仪表盘API
python backend/test_dashboard.py
```

## 🧪 测试

### 后端测试

```bash
python backend/test_dashboard.py
```

测试内容：
- ✅ 管理员登录并获取统计数据
- ✅ 验证管理员可以看到用户数量
- ✅ 获取项目列表
- ✅ 验证数据格式正确

### 前端测试

1. 以不同角色登录
2. 查看仪表盘显示的数据
3. 验证权限控制是否正确

## 📊 项目状态说明

| 状态码 | 状态名称 | 颜色 |
|--------|---------|------|
| 1 | 正常 | 绿色 |
| 2 | 未编写 | 灰色 |
| 3 | 编写中 | 蓝色 |
| 4 | 项目结束 | 灰色 |
| 5 | 项目跑路 | 红色 |
| 6 | 项目维护 | 橙色 |
| 7 | 未分配 | 灰色 |
| 8 | 账号不支持 | 红色 |
| 9 | IP不支持 | 红色 |

## 🔐 权限控制

### 后端权限

使用 `get_current_user` 依赖获取当前用户信息，根据用户角色返回不同的数据：

```python
@app.get("/stats")
async def get_dashboard_stats(
    current_user: tuple = Depends(get_current_user)
):
    user_id, roles = current_user
    # 根据角色返回不同数据
```

### 前端权限

前端根据后端返回的数据自动调整显示：
- 如果 `user_count` 为 `null`，不显示用户数量卡片
- 根据 `role` 字段调整标题文案

## 📝 数据关联说明

### 用户与项目关联

用户和项目通过多对多关系关联：

```python
# 用户模型
class UserInfo(BaseModel):
    projects: ManyToManyRelation["ProjectInfo"]

# 项目模型
class ProjectInfo(BaseModel):
    users: ManyToManyRelation["UserInfo"]
```

### IT/MANUAL 用户查看数据

IT 和 MANUAL 用户只能查看自己关联的项目：

```python
# 获取用户关联的项目
user_projects = await user.projects.all()

# 获取这些项目下的账户数量
project_ids = [p.id for p in user_projects]
account_count = await ProjectAccount.filter(project_id__in=project_ids).count()
```

## 🎯 下一步建议

1. **实时数据更新**
   - 添加 WebSocket 支持
   - 实时更新统计数据

2. **更多统计维度**
   - 按时间范围统计
   - 按项目状态分组统计
   - 账户类型分布

3. **数据可视化**
   - 添加图表（折线图、饼图）
   - 趋势分析

4. **快捷操作**
   - 从仪表盘快速跳转到项目详情
   - 快速创建项目/账户

5. **性能优化**
   - 添加缓存
   - 数据分页加载

## ⚠️ 注意事项

1. **需要重启后端服务**才能使用新的API
2. **用户必须关联项目**才能在 IT/MANUAL 角色下看到数据
3. 如果用户有多个角色，系统会选择优先级最高的角色（ADMIN > GM > IT > MANUAL）
4. 项目列表默认显示前10条，可以通过分页查看更多

## 🐛 问题排查

### 仪表盘显示空数据

1. 检查用户是否已登录
2. 检查 JWT Token 是否有效
3. 对于 IT/MANUAL 用户，检查是否已关联项目

### 权限错误

1. 确认后端 API 已正确注册
2. 检查 `get_current_user` 依赖是否正常工作
3. 查看后端日志确认错误信息

### 前端显示异常

1. 检查浏览器控制台是否有错误
2. 确认 API 请求是否成功
3. 检查数据格式是否正确

## 📞 API 调用示例

### 使用 curl 测试

```bash
# 1. 登录获取 token
TOKEN=$(curl -s http://127.0.0.1:6080/v1/user/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"zhiyu","password":"2201101122@qq.com"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. 获取仪表盘统计
curl -s http://127.0.0.1:6080/v1/user/dashboard/stats \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

# 3. 获取项目列表
curl -s http://127.0.0.1:6080/v1/user/dashboard/projects \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

## ✨ 功能特点

- ✅ 基于角色的权限控制
- ✅ 响应式设计（支持移动端）
- ✅ 实时数据统计
- ✅ 清晰的数据可视化
- ✅ 友好的用户提示
- ✅ 完整的错误处理
