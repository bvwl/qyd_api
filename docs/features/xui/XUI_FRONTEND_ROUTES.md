# XUI 前端路由和界面配置

## 概述

为 XUI 管理功能创建了完整的前端路由和界面，包括三个主要页面：

1. **XUI 服务器管理** (`/xui/server`)
2. **XUI 入站管理** (`/xui/inbound`)
3. **XUI 账号管理** (`/xui/account`)

## 路由配置

### 路由结构

```
/xui
  ├── /server      - XUI 服务器列表
  ├── /inbound     - XUI 入站列表
  └── /account     - XUI 账号管理（带 inbound_id 参数）
```

### 路由文件

#### `frontend/src/router/index.tsx`

```typescript
{
  path: 'xui/server',
  element: <XuiServerList />,
},
{
  path: 'xui/inbound',
  element: <XuiInboundList />,
},
{
  path: 'xui/account',
  element: <XuiAccountManage />,
},
```

#### `frontend/src/App.tsx`

```typescript
<Route path="xui/server" element={<XuiServerList />} />
<Route path="xui/inbound" element={<XuiInboundList />} />
<Route path="xui/account" element={<XuiAccountManage />} />
```

## 页面功能

### 1. XUI 服务器管理 (`XuiServerList.tsx`)

**路径**: `/xui/server`

**功能**:
- ✅ 服务器列表展示
- ✅ 添加服务器
- ✅ 编辑服务器
- ✅ 删除服务器
- ✅ 同步入站配置
- ✅ 密码显示/隐藏切换
- ✅ 分页和排序

**字段**:
- 名称
- 服务器地址（IP）
- 域名
- 端口
- 用户名
- 密码（仅管理员可见）
- HTTPS 开关
- Web 路径
- SSL 证书配置
- 状态
- 备注

**权限**:
- 查看：所有登录用户
- 添加/编辑/删除：仅 ADMIN

### 2. XUI 入站管理 (`XuiInboundList.tsx`)

**路径**: `/xui/inbound`

**功能**:
- ✅ 入站列表展示
- ✅ 按服务器筛选
- ✅ 按端口筛选
- ✅ 按协议筛选
- ✅ 添加入站
- ✅ 编辑入站
- ✅ 删除入站
- ✅ 跳转到账号管理
- ✅ 分页和排序

**字段**:
- 服务器
- 监听地址
- 监听端口（20000-33000）
- 协议（HTTP/SOCKS）
- 备注（用作服务器分组名称）
- 状态
- 默认用户名
- 默认密码

**权限**:
- 查看：所有登录用户
- 添加/编辑/删除：仅 ADMIN

### 3. XUI 账号管理 (`XuiAccountManage.tsx`)

**路径**: `/xui/account?inbound_id={id}`

**功能**:
- ✅ 入站账号列表展示
- ✅ 入站信息卡片
- ✅ 添加账号到入站
- ✅ 从入站移除账号
- ✅ 返回入站列表
- ✅ 分页

**字段**:
- 用户名
- 关联用户 ID
- 账号 ID

**权限**:
- 查看：所有登录用户
- 添加/移除：仅 ADMIN

## 页面交互流程

### 流程 1：创建 XUI 服务器

```
1. 访问 /xui/server
2. 点击"添加服务器"按钮
3. 填写服务器信息
   - 名称、地址、域名
   - 端口、用户名、密码
   - HTTPS、Web 路径
   - SSL 证书（可选）
4. 点击"确定"创建
5. 列表自动刷新
```

### 流程 2：同步入站配置

```
1. 在服务器列表中找到目标服务器
2. 点击"同步入站"按钮
3. 系统从 XUI 面板同步入站配置
4. 自动创建/更新入站记录
5. 自动同步到 ServerInfo 模型
```

### 流程 3：管理入站账号

```
1. 访问 /xui/inbound
2. 找到目标入站
3. 点击"账号管理"按钮
4. 跳转到 /xui/account?inbound_id={id}
5. 查看当前入站的账号列表
6. 点击"添加账号"
7. 选择服务器账号
8. 点击"确定"添加
9. 账号自动同步到 XUI 面板
```

### 流程 4：移除入站账号

```
1. 在账号管理页面
2. 找到要移除的账号
3. 点击"移除"按钮
4. 确认操作
5. 账号从入站移除
6. XUI 面板同步更新
```

## 组件特性

### 通用特性

- ✅ 响应式设计
- ✅ Ant Design 组件库
- ✅ TypeScript 类型安全
- ✅ 权限控制（基于角色）
- ✅ 错误处理
- ✅ 加载状态
- ✅ 分页支持
- ✅ 搜索和筛选

### 表格特性

- ✅ 固定表头
- ✅ 横向滚动
- ✅ 列宽自适应
- ✅ 操作列固定在右侧
- ✅ 状态标签彩色显示
- ✅ 空数据提示

### 表单特性

- ✅ 表单验证
- ✅ 必填项标识
- ✅ 输入提示
- ✅ 密码隐藏/显示
- ✅ 下拉选择
- ✅ 数字输入范围限制

## 待实现的 API 调用

所有页面中的 API 调用都已预留位置，需要创建对应的 API 文件：

### 需要创建的 API 文件

`frontend/src/api/xui.ts`:

```typescript
// XUI 服务器 API
export const getXuiServerList = (params: any) => { }
export const getXuiServer = (id: string) => { }
export const createXuiServer = (data: any) => { }
export const updateXuiServer = (id: string, data: any) => { }
export const deleteXuiServer = (id: string) => { }
export const syncXuiInbounds = (serverId: string) => { }

// XUI 入站 API
export const getXuiInboundList = (params: any) => { }
export const getXuiInbound = (id: string) => { }
export const createXuiInbound = (data: any) => { }
export const updateXuiInbound = (id: string, data: any) => { }
export const deleteXuiInbound = (id: string) => { }

// XUI 账号 API
export const getXuiInboundAccounts = (inboundId: string, params: any) => { }
export const addXuiInboundAccount = (inboundId: string, accountId: string) => { }
export const removeXuiInboundAccount = (inboundId: string, accountId: string) => { }
```

## 类型定义

需要在 `frontend/src/types/index.ts` 中添加：

```typescript
// XUI 服务器
export interface XuiServer {
  id: string
  name: string
  host: string
  domain?: string
  port: number
  username: string
  password?: string
  is_ssl: boolean
  web_path: string
  status: number
  cert_file?: string
  key_file?: string
  remark?: string
  create_time: string
  update_time: string
}

// XUI 入站
export interface XuiInbound {
  id: string
  server_id: string
  inbound_id: number
  listen_host: string
  listen_port: number
  protocol: number
  remark?: string
  status: number
  default_username: string
  default_password?: string
  create_time: string
  update_time: string
}

// XUI 入站账号
export interface XuiInboundAccount {
  inbound_id: string
  account_id: string
  username: string
  user_id?: string
}
```

## 菜单配置

需要在侧边栏菜单中添加 XUI 管理入口。

### 建议的菜单结构

```
├── 仪表盘
├── 用户管理
├── 项目管理
├── 服务器管理
├── XUI 管理 (新增)
│   ├── 服务器列表
│   ├── 入站列表
│   └── 账号管理
├── 邮件管理
└── API 文档
```

### 菜单配置示例

在后端添加路由权限：

```sql
-- XUI 管理菜单
INSERT INTO frontend_route (id, name, path, parent_id, icon, sort, status) VALUES
(UUID(), 'XUI管理', '/xui', NULL, 'CloudServerOutlined', 60, 1);

-- XUI 子菜单
INSERT INTO frontend_route (id, name, path, parent_id, icon, sort, status) VALUES
(UUID(), '服务器列表', '/xui/server', (SELECT id FROM frontend_route WHERE path='/xui'), NULL, 1, 1),
(UUID(), '入站列表', '/xui/inbound', (SELECT id FROM frontend_route WHERE path='/xui'), NULL, 2, 1),
(UUID(), '账号管理', '/xui/account', (SELECT id FROM frontend_route WHERE path='/xui'), NULL, 3, 1);
```

## 样式和主题

所有页面使用统一的样式：

- **间距**: 24px 外边距
- **卡片**: Ant Design Card 组件
- **按钮**: Primary 主按钮，Link 链接按钮
- **标签**: 彩色 Tag 标签
- **表格**: 固定表头，横向滚动
- **表单**: 垂直布局，标签在上

## 响应式设计

- **桌面**: 完整功能，横向滚动表格
- **平板**: 自适应列宽
- **手机**: 建议使用桌面版（表格内容较多）

## 权限控制

### 角色权限

| 功能 | ADMIN | GM | IT | MANUAL |
|------|-------|----|----|--------|
| 查看服务器 | ✅ | ✅ | ✅ | ✅ |
| 添加服务器 | ✅ | ❌ | ❌ | ❌ |
| 编辑服务器 | ✅ | ❌ | ❌ | ❌ |
| 删除服务器 | ✅ | ❌ | ❌ | ❌ |
| 同步入站 | ✅ | ✅ | ❌ | ❌ |
| 查看入站 | ✅ | ✅ | ✅ | ✅ |
| 添加入站 | ✅ | ❌ | ❌ | ❌ |
| 编辑入站 | ✅ | ❌ | ❌ | ❌ |
| 删除入站 | ✅ | ❌ | ❌ | ❌ |
| 查看账号 | ✅ | ✅ | ✅ | ✅ |
| 添加账号 | ✅ | ❌ | ❌ | ❌ |
| 移除账号 | ✅ | ❌ | ❌ | ❌ |

## 文件清单

### 新增文件

```
frontend/src/views/Xui/
├── XuiServerList.tsx      - XUI 服务器列表页面
├── XuiInboundList.tsx     - XUI 入站列表页面
└── XuiAccountManage.tsx   - XUI 账号管理页面
```

### 修改文件

```
frontend/src/router/index.tsx  - 添加 XUI 路由
frontend/src/App.tsx           - 添加 XUI 路由
```

### 待创建文件

```
frontend/src/api/xui.ts        - XUI API 调用
frontend/src/types/index.ts    - 添加 XUI 类型定义
```

## 下一步

### 1. 创建 API 文件

创建 `frontend/src/api/xui.ts` 并实现所有 API 调用。

### 2. 添加类型定义

在 `frontend/src/types/index.ts` 中添加 XUI 相关的类型定义。

### 3. 配置菜单

在后端数据库中添加 XUI 管理菜单和路由权限。

### 4. 测试功能

- 测试服务器的增删改查
- 测试入站的增删改查
- 测试账号的添加和移除
- 测试同步功能
- 测试权限控制

### 5. 优化体验

- 添加加载动画
- 优化错误提示
- 添加操作确认
- 优化表单验证

## 完成状态

✅ 前端路由配置完成
✅ XUI 服务器管理页面完成
✅ XUI 入站管理页面完成
✅ XUI 账号管理页面完成
✅ 权限控制集成
✅ 响应式设计
✅ TypeScript 类型安全
⏳ API 调用待实现
⏳ 类型定义待添加
⏳ 菜单配置待添加

## 总结

XUI 前端路由和界面已完整配置，包括：

- 🎯 三个主要管理页面
- 🔐 完整的权限控制
- 📱 响应式设计
- 🎨 统一的 UI 风格
- 🔄 完整的交互流程
- 📝 清晰的代码结构

所有页面都已预留 API 调用位置，只需实现 API 文件即可完成前后端对接。
