# 邮件查看器修复

## 问题描述

1. **接口错误**：前端调用了不存在的接口 `/v1/mail/outlook/inbox`，应该调用 `/v1/mail/outlook/messages`
2. **参数错误**：`from_email` 参数应该是 `@`（表示查看所有邮件）
3. **名称问题**：功能名称应该是"邮件查看器"而不是"邮箱查看器"

## 修复内容

### 1. 前端 API 修改 (`frontend/src/api/mail.ts`)

#### 修改前
```typescript
// 使用 GET 请求，调用不存在的 /inbox 接口
export const getInboxMessages = (params: {
  email: string
  top?: number
}) => {
  return api.get('/v1/mail/outlook/inbox', { params })
}
```

#### 修改后
```typescript
// 使用 POST 请求，调用正确的 /messages 接口
export const getInboxMessages = (params: {
  email: string
  top?: number
}) => {
  return api.post('/v1/mail/outlook/messages', {
    email: params.email,
    from_email: '@',  // @ 表示查看所有邮件
    num: params.top || 50,
    top: params.top || 50
  })
}
```

### 2. 前端组件适配 (`frontend/src/views/Mail/MailViewer.tsx`)

#### 数据结构调整

后端 `/v1/mail/outlook/messages` 接口返回的数据结构：

```typescript
{
  code: 1,
  message: "获取成功",
  data: [
    {
      from_email: "sender@example.com",
      title: "邮件主题",
      content: "<html>邮件内容</html>"
    }
  ]
}
```

前端组件需要适配这个简化的数据结构：

```typescript
interface EmailMessage {
  from_email: string
  title: string
  content: string
}

interface EmailDetail {
  subject: string
  from: string
  content: string
}
```

#### 表格列调整

移除了不存在的字段：
- ❌ 移除：状态（is_read）
- ❌ 移除：附件（has_attachments）
- ❌ 移除：接收时间（received_time）
- ✅ 保留：主题（title）
- ✅ 保留：发件人（from_email）
- ✅ 保留：预览（content）

#### 详情查看简化

由于后端只返回基本信息，详情弹窗也相应简化：
- 只显示主题、发件人和内容
- 移除了收件人、抄送、时间、附件等字段
- 内容使用 HTML 渲染（DOMPurify 清理）

### 3. 后端接口说明

#### 接口地址
```
POST /v1/mail/outlook/messages
```

#### 请求参数
```json
{
  "email": "zhiyu918918@outlook.com",
  "from_email": "@",  // @ 表示查看所有邮件
  "num": 50,          // 需要获取的匹配邮件数量
  "top": 50           // API 单次查询的邮件数量
}
```

#### 响应数据
```json
{
  "code": 1,
  "message": "获取成功",
  "data": [
    {
      "from_email": "sender@example.com",
      "title": "邮件主题",
      "content": "<html>邮件内容</html>"
    }
  ]
}
```

## 功能说明

### from_email 参数的作用

- `@`：查看所有邮件（不过滤发件人）
- `specific@email.com`：只查看来自特定发件人的邮件
- 支持模糊匹配：如果发件人地址包含指定字符串，就会被匹配

### 缓存机制

前端保留了 10 分钟的缓存机制：
- 首次查看邮件时从服务器获取
- 10 分钟内再次查看使用缓存数据
- 点击"刷新"按钮强制从服务器获取最新数据

### 搜索功能

支持两种搜索模式：
1. **文本搜索**：在主题、发件人、内容中搜索包含指定文本的邮件
2. **正则搜索**：使用正则表达式进行高级搜索

## 测试验证

### 测试步骤

1. 打开邮件查看器页面
2. 输入邮箱地址：`zhiyu918918@outlook.com`
3. 点击"查看邮件"按钮
4. 应该能看到邮件列表（主题、发件人、预览）
5. 点击"查看"按钮查看邮件详情
6. 测试搜索功能
7. 测试刷新功能

### 预期结果

- ✅ 能够成功获取邮件列表
- ✅ 显示邮件主题、发件人和内容预览
- ✅ 点击查看能显示完整的邮件内容（HTML 格式）
- ✅ 搜索功能正常工作
- ✅ 缓存机制正常工作
- ✅ 刷新功能正常工作

## 文件修改清单

- ✅ `frontend/src/api/mail.ts` - 修改 API 调用方式和参数
- ✅ `frontend/src/views/Mail/MailViewer.tsx` - 适配新的数据结构

## 注意事项

1. **数据结构简化**：后端返回的数据结构比较简单，只包含基本信息
2. **HTML 内容**：邮件内容是 HTML 格式，使用 DOMPurify 进行安全清理
3. **from_email 参数**：使用 `@` 表示查看所有邮件，这是后端的约定
4. **缓存策略**：10 分钟缓存可以减少服务器压力，但可能看不到最新邮件

## 后续优化建议

1. **增强后端接口**：返回更多邮件信息（时间、附件、已读状态等）
2. **分页加载**：支持加载更多邮件
3. **邮件操作**：支持标记已读、删除、移动等操作
4. **实时刷新**：定时自动刷新邮件列表
5. **邮件分类**：支持按文件夹查看（收件箱、垃圾邮件等）

## 总结

通过修复 API 调用和适配数据结构，邮件查看器现在可以正常工作了。用户可以：
- 输入邮箱地址查看所有邮件
- 查看邮件的主题、发件人和内容
- 搜索邮件
- 查看邮件详情（HTML 格式）

功能虽然简化了，但核心的邮件查看功能已经可以正常使用。
