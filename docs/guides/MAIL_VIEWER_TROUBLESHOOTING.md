# 邮件查看器问题排查指南

## 问题现状
邮件查看器菜单不显示，或点击后页面无法加载

## 已完成的修复

### ✅ 1. 添加完整的前端路由
**文件**: `frontend/src/router/index.tsx`

添加了所有缺失的路由：
- 项目管理路由（/project/list, /project/account, /project/wallet）
- 服务器管理路由（/server/list, /server/country, /server/group, /server/account）
- 邮件查看器路由（/mail/viewer）

### ✅ 2. 安装必需的依赖
**执行**: `npm install` 在 frontend 目录

安装了：
- dompurify@^3.0.8
- isomorphic-dompurify@^2.9.0
- @types/dompurify@^3.0.5

### ✅ 3. 修复管理员菜单显示
**文件**: `frontend/src/components/Layout/index.tsx`

修复了角色判断逻辑，管理员现在会自动显示完整菜单

### ✅ 4. 数据库路由已初始化
**执行**: `python backend/db/init_routes.py`

邮件查看器路由已添加到数据库

## 🚀 立即执行的操作

### 1. 重启前端服务（必须！）

如果前端正在运行，必须重启才能加载新的路由配置：

```bash
# 停止当前前端进程（Ctrl+C）
cd frontend
npm run dev
```

### 2. 清除浏览器缓存（必须！）

**方法1：硬刷新**
```
Mac: Cmd + Shift + R
Windows: Ctrl + Shift + R
```

**方法2：清除localStorage**
在浏览器控制台（F12）执行：
```javascript
localStorage.clear()
location.reload()
```

**方法3：完全清除**
1. 打开浏览器设置
2. 清除浏览器数据
3. 选择"缓存的图片和文件"
4. 清除数据
5. 刷新页面

### 3. 重新登录

1. 退出当前登录
2. 使用管理员账号登录
   - 邮箱：zhiyu
   - 密码：2201101122@qq.com

## 🔍 验证步骤

### 步骤1：检查控制台
打开浏览器控制台（F12），应该看到：
```
管理员用户，使用默认完整菜单
```

如果没有看到这个日志：
- 检查是否清除了缓存
- 检查是否重新登录
- 检查用户角色是否正确

### 步骤2：检查菜单
左侧菜单应该显示：
```
📊 仪表盘
👤 用户管理
  └─ 6个子菜单
📁 项目管理
  └─ 3个子菜单
☁️ 服务器管理
  └─ 4个子菜单
📧 邮箱管理
  ├─ 邮箱列表
  └─ 邮件查看器  ← 应该能看到
📖 API文档
  └─ 7个子菜单
```

### 步骤3：点击邮件查看器
1. 展开"邮箱管理"菜单
2. 点击"邮件查看器"
3. 应该跳转到 `/mail/viewer`
4. 页面应该正常显示（不是404）

### 步骤4：测试功能
在邮件查看器页面：
1. 输入邮箱地址
2. 点击"查看邮件"按钮
3. 验证功能是否正常

## 🐛 常见问题

### 问题1：菜单还是看不到
**可能原因**：
- 浏览器缓存未清除
- 前端服务未重启
- 用户不是管理员

**解决方法**：
1. 完全关闭浏览器，重新打开
2. 确认前端服务已重启
3. 确认使用管理员账号登录

### 问题2：点击后404
**可能原因**：
- 前端路由未加载
- 前端服务未重启

**解决方法**：
1. 检查 `frontend/src/router/index.tsx` 是否包含 `/mail/viewer` 路由
2. 重启前端服务
3. 清除浏览器缓存

### 问题3：页面显示错误
**可能原因**：
- 依赖未安装
- 组件导入错误

**解决方法**：
```bash
cd frontend
npm install
npm run dev
```

### 问题4：控制台报错 "Cannot find module 'dompurify'"
**原因**：依赖未安装

**解决方法**：
```bash
cd frontend
npm install dompurify isomorphic-dompurify
npm install --save-dev @types/dompurify
npm run dev
```

## 🔧 调试命令

### 检查用户角色
```javascript
// 在浏览器控制台执行
const storage = JSON.parse(localStorage.getItem('user-storage'))
console.log('用户信息:', storage.state.userInfo)
console.log('用户角色:', storage.state.userInfo.roles)
// 应该看到: [{ code: 'ADMIN', name: '管理员', ... }]
```

### 检查路由配置
```javascript
// 在浏览器控制台执行
console.log('当前路径:', window.location.pathname)
console.log('路由器:', window.__REACT_ROUTER__)
```

### 检查依赖安装
```bash
# 在终端执行
cd frontend
ls node_modules | grep dompurify
# 应该看到: dompurify 和 isomorphic-dompurify
```

### 检查前端进程
```bash
# 检查前端是否在运行
lsof -i :3000
# 或
netstat -an | grep 3000
```

## 📋 完整检查清单

- [ ] 前端依赖已安装（npm install）
- [ ] 前端服务已重启
- [ ] 浏览器缓存已清除
- [ ] 使用管理员账号登录
- [ ] 控制台显示"管理员用户，使用默认完整菜单"
- [ ] 左侧菜单显示所有模块
- [ ] 邮箱管理下能看到"邮件查看器"
- [ ] 点击后能正常跳转
- [ ] 页面正常显示（无404）
- [ ] 功能正常使用

## 🎯 如果所有方法都不行

### 最后的手段：完全重置

```bash
# 1. 停止所有服务
# 按 Ctrl+C 停止前端和后端

# 2. 清除前端依赖和缓存
cd frontend
rm -rf node_modules
rm -rf .vite
npm install

# 3. 重启前端
npm run dev

# 4. 在浏览器中
# - 完全关闭浏览器
# - 清除所有浏览器数据
# - 重新打开浏览器
# - 访问 http://localhost:3000
# - 重新登录
```

## 📞 需要帮助？

如果问题仍然存在，请提供：

1. **浏览器控制台的完整日志**
   - 打开控制台（F12）
   - 复制所有错误信息

2. **localStorage内容**
   ```javascript
   console.log(localStorage.getItem('user-storage'))
   ```

3. **网络请求**
   - 打开Network标签
   - 刷新页面
   - 查看是否有失败的请求

4. **前端服务状态**
   ```bash
   lsof -i :3000
   ```

## 📚 相关文档

- `QUICK_FIX_SUMMARY.md` - 修复总结
- `test_admin_menu.md` - 测试指南
- `MAIL_VIEWER_QUICK_START.md` - 功能使用指南
- `fix_mail_viewer_complete.sh` - 一键修复脚本
