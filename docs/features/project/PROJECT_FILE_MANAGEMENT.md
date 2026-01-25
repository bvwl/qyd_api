# 项目文件管理功能

## 功能描述

为项目管理添加文件上传和下载功能，支持项目管理员上传项目流程文档（PDF、Word等），IT和MANUAL角色可以下载查看。

## 权限说明

- **上传文件**：仅 ADMIN 和 GM（项目管理员）可以上传
- **下载文件**：所有登录用户（ADMIN、GM、IT、MANUAL）都可以下载
- **删除文件**：仅 ADMIN 和 GM 可以删除

## 支持的文件格式

- PDF (`.pdf`)
- Word (`.doc`, `.docx`)
- Excel (`.xls`, `.xlsx`)
- PowerPoint (`.ppt`, `.pptx`)
- 文本文件 (`.txt`)

## 文件存储

- **存储路径**：`status/{项目名称}/{文件名}`
- **自动创建**：如果项目文件夹不存在，系统会自动创建
- **文件大小限制**：最大 50MB

## 实现细节

### 1. 后端 API

#### 文件：`backend/app/apis/v1/project/file.py`

**API 端点**：

1. **上传文件**
   - 路径：`POST /v1/project/file/{project_id}/upload`
   - 权限：GM 和 ADMIN
   - 参数：multipart/form-data 文件

2. **获取文件列表**
   - 路径：`GET /v1/project/file/{project_id}/files`
   - 权限：所有登录用户
   - 返回：文件名、大小、修改时间

3. **下载文件**
   - 路径：`GET /v1/project/file/{project_id}/download/{filename}`
   - 权限：所有登录用户
   - 返回：文件流

4. **删除文件**
   - 路径：`DELETE /v1/project/file/{project_id}/delete/{filename}`
   - 权限：GM 和 ADMIN

### 2. 前端实现

#### 文件：`frontend/src/views/Project/ProjectList.tsx`

**新增功能**：

1. **文件管理按钮**
   - 位置：操作列第一个按钮
   - 图标：FileOutlined
   - 所有用户可见

2. **文件管理弹窗**
   - 显示项目所有文件列表
   - 文件信息：名称、大小、修改时间
   - 操作：上传、下载、删除

3. **上传功能**
   - 仅 GM 和 ADMIN 可见上传按钮
   - 支持拖拽上传
   - 自动验证文件类型和大小
   - 上传成功后自动刷新列表

4. **下载功能**
   - 所有用户可见下载按钮
   - 点击直接下载文件
   - 保持原文件名

5. **删除功能**
   - 仅 GM 和 ADMIN 可见删除按钮
   - 删除前需要确认
   - 删除成功后自动刷新列表

## 使用流程

### 项目管理员（ADMIN/GM）上传文件

1. 进入"项目管理" -> "项目列表"
2. 找到目标项目，点击"文件管理"按钮
3. 在弹窗中点击"上传文件"按钮
4. 选择要上传的文件（PDF、Word等）
5. 等待上传完成，文件会自动显示在列表中

### IT/MANUAL 下载文件

1. 进入"项目管理" -> "项目列表"
2. 找到目标项目，点击"文件管理"按钮
3. 在文件列表中找到需要的文件
4. 点击"下载"按钮
5. 文件会自动下载到本地

## API 示例

### 上传文件

```bash
curl -X POST 'http://127.0.0.1:6080/v1/project/file/{project_id}/upload' \
  -H 'Authorization: Bearer <token>' \
  -F 'file=@/path/to/document.pdf'
```

### 获取文件列表

```bash
curl 'http://127.0.0.1:6080/v1/project/file/{project_id}/files' \
  -H 'Authorization: Bearer <token>'
```

响应示例：
```json
{
  "message": "成功",
  "project_name": "项目A",
  "files": [
    {
      "name": "流程文档.pdf",
      "size": 1048576,
      "modified_time": 1706198400
    }
  ],
  "count": 1
}
```

### 下载文件

```bash
curl 'http://127.0.0.1:6080/v1/project/file/{project_id}/download/流程文档.pdf' \
  -H 'Authorization: Bearer <token>' \
  --output 流程文档.pdf
```

### 删除文件

```bash
curl -X DELETE 'http://127.0.0.1:6080/v1/project/file/{project_id}/delete/流程文档.pdf' \
  -H 'Authorization: Bearer <token>'
```

## 文件存储结构

```
status/
├── 项目A/
│   ├── 流程文档.pdf
│   ├── 操作手册.docx
│   └── 数据表格.xlsx
├── 项目B/
│   ├── 需求文档.pdf
│   └── 设计方案.pptx
└── 项目C/
    └── 说明.txt
```

## 注意事项

1. **文件命名**
   - 建议使用有意义的文件名
   - 避免使用特殊字符
   - 中文文件名完全支持

2. **文件大小**
   - 单个文件最大 50MB
   - 超过限制会提示错误

3. **文件安全**
   - 所有文件操作都需要登录认证
   - 上传和删除需要管理员权限
   - 文件存储在服务器本地，不对外公开

4. **文件管理**
   - 删除项目不会自动删除文件夹
   - 需要手动清理不需要的文件
   - 建议定期检查文件存储空间

## 相关文件

### 后端
- `backend/app/apis/v1/project/file.py` - 文件管理 API
- `backend/app/apis/v1/project/__init__.py` - 路由注册

### 前端
- `frontend/src/views/Project/ProjectList.tsx` - 项目列表页面
- `frontend/src/api/project.ts` - API 接口定义

## 完成时间

2026-01-26 00:00
