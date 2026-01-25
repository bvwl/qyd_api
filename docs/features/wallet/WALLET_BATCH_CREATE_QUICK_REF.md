# 批量创建钱包功能 - 快速参考

## 问题解决

### 问题描述
前端页面无法加载，显示 "No routes matched location" 错误。

### 根本原因
项目使用了两套路由系统：
1. **`frontend/src/App.tsx`** - 使用 `BrowserRouter` + `Routes/Route` (当前激活的系统)
2. **`frontend/src/router/index.tsx`** - 使用 `createBrowserRouter` (未使用)

批量创建钱包的路由只在 `router/index.tsx` 中定义，但应用实际使用的是 `App.tsx` 的路由配置。

### 解决方案
在 `frontend/src/App.tsx` 中添加批量创建钱包路由：

```typescript
// 1. 导入组件
import WalletBatchCreate from './views/Project/WalletBatchCreate'

// 2. 添加路由（注意顺序：更具体的路径在前）
<Route path="project/wallet/batch-create" element={<WalletBatchCreate />} />
<Route path="project/wallet" element={<ProjectWallet />} />
```

**关键点**：路由顺序很重要！`project/wallet/batch-create` 必须在 `project/wallet` 之前，否则会被通用路由拦截。

## 功能访问

### 访问路径
- **菜单路径**：项目管理 → 批量创建钱包
- **URL路径**：`/project/wallet/batch-create`

### 权限要求
- 只有 **ADMIN** 角色可以访问
- 非管理员用户会看到权限不足提示

## 功能特性

### 1. 批量创建
- 支持 ETH 和 Solana 两种链
- 一次可创建 1-100 个钱包
- 自动保存到数据库（使用 AES 加密）

### 2. 临时显示
- 创建后在前端显示 10 分钟
- 倒计时提醒
- 过期后前端数据清除（数据库保留）

### 3. 数据安全
- 私钥和助记词使用 AES 加密存储
- 加密密钥：MD5(项目名称 + "9527")
- 前端显示时支持显示/隐藏切换
- 支持一键复制

### 4. 导出功能
- 支持导出为 Excel 文件
- 包含明文私钥和助记词
- 文件名格式：`钱包_链类型_时间戳.xlsx`

## 技术实现

### 后端 API
```
POST /api/v1/project/wallet/batch
```

**请求参数**：
```json
{
  "project_name": "项目名称",
  "chain": "eth",  // 或 "solana"
  "count": 10,
  "remark": "备注信息（可选）"
}
```

**响应数据**：
```json
{
  "count": 10,
  "items": [
    {
      "id": "uuid",
      "chain": "eth",
      "public_key": "公钥（明文）",
      "private_key": "私钥（明文，仅ADMIN可见）",
      "mnemonic": "助记词（明文，仅ADMIN可见）",
      "create_time": "2026-01-25 12:00:00"
    }
  ]
}
```

### 前端组件
- **位置**：`frontend/src/views/Project/WalletBatchCreate.tsx`
- **状态管理**：使用 React Hooks (useState, useEffect)
- **UI组件**：Ant Design (Form, Table, Button, Statistic)
- **Excel导出**：动态导入 xlsx 库

### 数据库
- **表名**：`project_wallet`
- **加密字段**：`private_key`, `mnemonic`
- **加密方式**：AES-256-CBC
- **存储格式**：Base64 编码的加密数据

## 使用流程

1. **登录系统**（使用 ADMIN 账号）
2. **进入页面**：项目管理 → 批量创建钱包
3. **填写表单**：
   - 项目名称（必填，用于加密）
   - 链类型（ETH 或 Solana）
   - 创建数量（1-100）
   - 备注（可选）
4. **点击创建**：系统自动创建并保存到数据库
5. **查看结果**：
   - 表格显示创建的钱包
   - 私钥/助记词默认隐藏，可点击眼睛图标显示
   - 支持一键复制
6. **下载备份**：点击"下载钱包"按钮导出 Excel
7. **10分钟后**：前端临时数据自动清除

## 注意事项

1. **项目名称很重要**：用于加密私钥和助记词，请妥善保管
2. **及时下载**：前端数据只保留 10 分钟，请及时下载 Excel 备份
3. **数据库保留**：即使前端数据过期，数据库中的钱包仍然保留
4. **权限限制**：只有 ADMIN 可以创建和查看解密后的钱包
5. **Excel安全**：导出的 Excel 包含明文私钥，请妥善保管

## 相关文件

### 后端
- `backend/app/apis/v1/project/wallet.py` - API 端点
- `backend/app/crud/project/wallet.py` - 数据库操作
- `backend/app/schemas/project/wallet.py` - 数据模型
- `backend/app/core/tools.py` - 加密工具
- `backend/app/clients/wallet.py` - 钱包生成

### 前端
- `frontend/src/App.tsx` - 路由配置（已修复）
- `frontend/src/views/Project/WalletBatchCreate.tsx` - 页面组件
- `frontend/src/api/project.ts` - API 调用
- `frontend/src/components/Layout/index.tsx` - 菜单配置

### 数据库
- `backend/db/init_routes.py` - 路由初始化（已添加）
- `backend/db/bind_admin_routes.py` - 权限绑定（已执行）

## 测试验证

### 后端测试
```bash
cd backend
python test_wallet_encryption.py
```

### 前端测试
1. 刷新浏览器（Ctrl + Shift + R）
2. 登录 ADMIN 账号
3. 访问：项目管理 → 批量创建钱包
4. 创建测试钱包
5. 验证显示、复制、下载功能

## 故障排除

### 问题：页面显示 "No routes matched location"
**原因**：路由未在 `App.tsx` 中定义
**解决**：确认 `frontend/src/App.tsx` 中已添加路由

### 问题：显示 "权限不足"
**原因**：当前用户不是 ADMIN
**解决**：使用 ADMIN 账号登录

### 问题：无法下载 Excel
**原因**：xlsx 依赖未安装
**解决**：
```bash
cd frontend
npm install xlsx
```

### 问题：创建后看不到数据
**原因**：后端 API 调用失败
**解决**：
1. 检查浏览器控制台错误
2. 检查后端日志：`backend/logs/api.log`
3. 确认数据库连接正常

## 更新日志

### 2026-01-25
- ✅ 修复前端路由配置问题
- ✅ 在 `App.tsx` 中添加批量创建钱包路由
- ✅ 确保路由顺序正确（更具体的路径在前）
- ✅ 验证功能正常工作

### 之前的更新
- ✅ 实现后端批量创建 API
- ✅ 添加 AES 加密功能
- ✅ 创建前端页面组件
- ✅ 添加 Excel 导出功能
- ✅ 添加 10 分钟倒计时
- ✅ 注册后端路由权限
- ✅ 绑定 ADMIN 角色权限
