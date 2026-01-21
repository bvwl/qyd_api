# API文档菜单实现总结

## 功能概述
新增了一个"API文档"菜单栏，包含多个二级子菜单，每个子菜单对应一个具体的API接口测试页面。类似Postman的功能，可以自定义HTTP方法、URL、参数、请求头和请求体。

## 实现内容

### 1. 创建通用API测试组件
**文件**: `frontend/src/components/ApiTester/index.tsx`

**功能特性**:
- 支持GET、POST、PUT、DELETE、PATCH等HTTP方法
- 可配置URL、Query参数、Headers、Body
- 支持启用/禁用单个参数或Header
- 显示响应状态码、响应时间和格式化的JSON响应
- 支持预设示例，一键加载
- 自动添加JWT Token到Authorization头
- 响应结果可一键复制

### 2. 创建各模块API测试页面

#### 用户模块
- **用户列表** (`UserApi.tsx`) - GET /v1/user/user
  - 支持分页、搜索、状态过滤
  - 预设示例：获取第一页、搜索用户
  
- **创建用户** (`UserCreate.tsx`) - POST /v1/user/user
  - 支持创建用户并分配角色
  - 预设示例：创建普通用户、创建管理员

- **角色列表** (`RoleApi.tsx`) - GET /v1/user/role
  - 获取所有角色信息

#### 项目模块
- **项目列表** (`ProjectApi.tsx`) - GET /v1/project/info
  - 支持分页、搜索、状态过滤
  - 预设示例：获取第一页、搜索项目

- **项目账号** (`ProjectAccountApi.tsx`) - GET /v1/project/account
  - 获取项目账号列表

#### 服务器模块
- **服务器列表** (`ServerApi.tsx`) - GET /v1/server/info
  - 支持分页和状态过滤

#### 邮箱模块
- **邮箱列表** (`MailApi.tsx`) - GET /v1/mail/info
  - 支持分页、搜索、状态过滤
  - 预设示例：获取所有邮箱、搜索邮箱

### 3. 更新路由配置
**文件**: `frontend/src/App.tsx`

**新增路由**:
- `/api-docs/user` - 用户列表API
- `/api-docs/user-create` - 创建用户API
- `/api-docs/role` - 角色列表API
- `/api-docs/project` - 项目列表API
- `/api-docs/project-account` - 项目账号API
- `/api-docs/server` - 服务器列表API
- `/api-docs/mail` - 邮箱列表API

### 4. 更新菜单配置
**文件**: `frontend/src/components/Layout/index.tsx`

**菜单结构**:
```
API文档
├── 用户列表
├── 创建用户
├── 角色列表
├── 项目列表
├── 项目账号
├── 服务器列表
└── 邮箱列表
```

## 使用说明

### 基本使用
1. 登录系统后，在左侧菜单栏点击"API文档"
2. 选择要测试的接口子菜单
3. 配置请求参数：
   - 选择HTTP方法（GET/POST/PUT/DELETE/PATCH）
   - 输入或修改URL路径
   - 在"Query参数"标签页添加查询参数
   - 在"Headers"标签页管理请求头
   - 在"Body"标签页编辑请求体（POST/PUT/PATCH）
4. 点击"发送"按钮执行请求
5. 查看响应结果（状态码、响应时间、JSON数据）

### 高级功能
- **启用/禁用参数**: 勾选/取消勾选参数前的复选框
- **使用示例**: 点击页面顶部的示例按钮快速加载预设配置
- **复制响应**: 点击响应区域的"复制"按钮复制JSON数据
- **自动认证**: JWT Token自动从localStorage读取并添加到请求头

### 参数说明

#### Query参数常用字段
- `page`: 页码（默认1）
- `limit`: 每页数量（默认10）
- `res_count`: 是否返回总数（true/false）
- `email`: 邮箱搜索
- `name`: 名称搜索
- `status`: 状态过滤
- `create_time_start`: 创建时间开始
- `create_time_end`: 创建时间结束

#### Headers默认配置
- `Content-Type`: application/json
- `Authorization`: Bearer {JWT_TOKEN}

## 技术实现

### 组件设计
- **ApiTester组件**: 可复用的API测试组件
  - Props配置：标题、描述、默认方法、URL、参数、示例
  - 状态管理：method, url, headers, params, body, response
  - 请求处理：使用axios发送HTTP请求
  - 响应展示：格式化JSON、显示状态码和响应时间

### 数据流
1. 用户配置请求参数
2. 点击发送按钮
3. 构建完整的axios配置对象
4. 发送HTTP请求到后端
5. 接收响应并更新状态
6. 渲染响应结果

### 错误处理
- JSON格式验证（请求体）
- 网络错误捕获
- 响应错误展示
- 用户友好的错误提示

## 文件清单
```
frontend/src/components/ApiTester/
  └── index.tsx                    # 通用API测试组件

frontend/src/views/ApiDocs/
  ├── UserApi.tsx                  # 用户列表API
  ├── UserCreate.tsx               # 创建用户API
  ├── RoleApi.tsx                  # 角色列表API
  ├── ProjectApi.tsx               # 项目列表API
  ├── ProjectAccountApi.tsx        # 项目账号API
  ├── ServerApi.tsx                # 服务器列表API
  └── MailApi.tsx                  # 邮箱列表API

frontend/src/App.tsx               # 路由配置
frontend/src/components/Layout/index.tsx  # 菜单配置
```

## 效果展示
- 左侧菜单"API文档"下有7个子菜单
- 每个子菜单打开一个独立的API测试页面
- 页面包含：接口描述、示例按钮、请求配置区、响应展示区
- 支持完整的HTTP请求配置和测试

## 后续扩展建议
1. 添加更多接口测试页面（更新、删除等）
2. 支持保存测试历史记录
3. 支持导出/导入测试配置
4. 添加批量测试功能
5. 集成接口文档说明
6. 支持环境变量切换（开发/生产）
7. 添加请求/响应拦截器日志
8. 支持WebSocket测试
