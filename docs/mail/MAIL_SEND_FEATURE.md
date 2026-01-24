# 邮件发送功能实现

## 概述

将"Outlook授权"菜单改为"发送邮件"，并实现了完整的邮件发送功能，支持纯文本和HTML格式。

## 修改内容

### 1. 数据库菜单更新

**文件**: `backend/db/init_routes.py`

- 将菜单项从 "Outlook授权" 改为 "发送邮件"
- 路径: `/mail/outlook` → `/mail/send`
- 组件: `MailOutlook` → `MailSend`

```python
{
    "name": "mail-send",
    "path": "/mail/send",
    "title": "发送邮件",
    "component": "MailSend",
    "sort": 3,
}
```

### 2. 前端页面实现

**文件**: `frontend/src/views/Mail/MailSend.tsx`

创建了全新的邮件发送页面，功能包括：

#### 表单字段
- **发件人邮箱**: 必填，邮箱格式验证
- **收件人邮箱**: 必填，邮箱格式验证
- **邮件主题**: 必填
- **内容格式**: 选择 Text 或 HTML
- **邮件内容**: 必填，最多50000字符

#### 功能特性
- ✅ 支持纯文本格式 (Text)
- ✅ 支持HTML格式 (HTML)
- ✅ HTML格式提供示例代码
- ✅ 字符计数显示
- ✅ 表单验证
- ✅ 发送状态提示
- ✅ 重置表单功能

#### UI设计
- 使用 Card 组件包裹，居中显示
- 最大宽度 1200px
- 表单采用垂直布局
- 大尺寸输入框，提升用户体验
- HTML格式时显示示例代码

### 3. API接口

**文件**: `frontend/src/api/mail.ts`

API接口已存在，无需修改：

```typescript
export const sendOutlookEmail = (data: {
  email: string           // 发件人邮箱
  to_email: string        // 收件人邮箱
  subject: string         // 邮件主题
  content: string         // 邮件内容
  content_type?: 'Text' | 'HTML'  // 内容格式
}) => {
  return api.post<any, ApiResponse>('/v1/mail/outlook/send', data)
}
```

### 4. 路由配置

**文件**: `frontend/src/App.tsx`

添加了新的路由：

```tsx
import MailSend from './views/Mail/MailSend'

// 路由配置
<Route path="mail/send" element={<MailSend />} />
```

## 使用说明

### 发送纯文本邮件

1. 进入"邮箱管理" → "发送邮件"
2. 填写发件人邮箱（需要已授权的邮箱）
3. 填写收件人邮箱
4. 填写邮件主题
5. 选择"纯文本 (Text)"格式
6. 输入邮件内容
7. 点击"发送邮件"

### 发送HTML邮件

1. 进入"邮箱管理" → "发送邮件"
2. 填写发件人邮箱（需要已授权的邮箱）
3. 填写收件人邮箱
4. 填写邮件主题
5. 选择"HTML格式"
6. 输入HTML代码，例如：

```html
<html>
  <body>
    <h1>欢迎</h1>
    <p>这是一封HTML格式的邮件。</p>
    <ul>
      <li>支持列表</li>
      <li>支持样式</li>
    </ul>
  </body>
</html>
```

7. 点击"发送邮件"

## 部署步骤

### 1. 更新数据库菜单

```bash
cd backend
python db/init_routes.py
```

### 2. 删除旧的Outlook授权菜单（如果存在）

```bash
# 方式1: 使用SQL脚本
mysql -h 127.0.0.1 -P 3307 -u qyd -p qyd < db/delete_old_outlook_route.sql

# 方式2: 手动删除
# 登录数据库后执行:
# DELETE FROM frontend_route WHERE name = 'mail-outlook';
```

### 3. 重启后端服务

```bash
# 如果后端正在运行，需要重启
# 停止当前服务，然后重新启动
python start.py
```

### 4. 前端无需重新构建

前端代码已更新，刷新浏览器即可看到新菜单。

## 菜单结构

```
📁 邮箱管理 (/mail)
  └─ 邮箱列表 (/mail/list)
  └─ 邮件查看器 (/mail/viewer)
  └─ 发送邮件 (/mail/send)  ← 新增
```

## 注意事项

1. **发件人邮箱必须已授权**: 发送邮件前，需要先在"邮箱列表"中添加邮箱并完成Outlook授权
2. **内容格式选择**: 
   - 纯文本格式：适合简单的文字邮件
   - HTML格式：适合需要样式、图片、链接的邮件
3. **字符限制**: 邮件内容最多50000字符
4. **错误处理**: 如果发送失败，会显示具体的错误信息

## 测试建议

1. 测试纯文本邮件发送
2. 测试HTML邮件发送
3. 测试表单验证（空字段、邮箱格式错误）
4. 测试未授权邮箱发送（应该返回错误）
5. 测试长内容邮件发送

## 相关文件

- `backend/db/init_routes.py` - 路由初始化脚本
- `backend/db/delete_old_outlook_route.sql` - 删除旧路由的SQL脚本
- `frontend/src/views/Mail/MailSend.tsx` - 发送邮件页面
- `frontend/src/App.tsx` - 路由配置
- `frontend/src/api/mail.ts` - API接口定义

## 后端API说明

后端接口: `POST /v1/mail/outlook/send`

请求参数:
```json
{
  "email": "sender@example.com",
  "to_email": "receiver@example.com",
  "subject": "邮件主题",
  "content": "邮件内容",
  "content_type": "Text"  // 或 "HTML"
}
```

响应:
```json
{
  "code": 1,
  "message": "发送成功"
}
```
