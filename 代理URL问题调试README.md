# 代理 URL 问题调试 - 从这里开始

## 🎯 问题

点击"复制代理"和"测试代理"时报错，代理 URL 显示默认的 `username:password`。

## 🚀 快速开始

### 第一步：更新代码并重启服务

```bash
cd /opt/zy/qyd_api
git pull

# 重启后端
docker compose -f docker-compose.backend.yml restart backend-api

# 重新构建并重启前端
docker compose -f docker-compose.frontend.yml build frontend
docker compose -f docker-compose.frontend.yml restart frontend
```

### 第二步：打开浏览器开发者工具

1. 在浏览器中打开前端页面
2. 按 `F12` 打开开发者工具
3. 切换到 "Console"（控制台）标签
4. 刷新页面

### 第三步：查看控制台输出

查找这两行输出：

```javascript
服务器列表数据: {...}
第一条数据: {proxy_url: "...", ...}
```

**关键检查**：`proxy_url` 字段的值是什么？

- ✅ 如果是 `http://your_username:your_password@...` → 正常！
- ❌ 如果是 `http://username:password@...` → 需要创建服务器账号
- ❌ 如果是空字符串 `""` → 检查服务器端口配置

### 第四步：如果 proxy_url 不正常

运行检查脚本：

```bash
docker compose -f docker-compose.backend.yml exec backend-api bash
python check_server_account.py zhiyu  # 替换为你的用户邮箱
```

如果显示"未找到服务器账号"，按照提示创建账号。

## 📚 详细文档

| 文档 | 说明 |
|------|------|
| **`NEXT_STEPS.md`** | **详细的操作步骤（推荐）** |
| `PROXY_URL_COMPLETE_DEBUG.md` | 完整调试方案总览 |
| `FRONTEND_PROXY_DEBUG.md` | 前端调试指南 |
| `PROXY_URL_DEBUG_GUIDE.md` | 后端调试指南 |
| `PROXY_URL_DEBUG_QUICK_REF.md` | 快速命令参考 |

## 🔍 快速诊断

```
proxy_url 的值是什么？
  ├─ "http://your_username:your_password@..." → ✅ 正常
  ├─ "http://username:password@..." → ❌ 用户没有服务器账号
  ├─ "" (空字符串) → ❌ 服务器端口未配置
  └─ undefined → ❌ 后端返回数据有问题
```

## 💡 最可能的原因

根据经验，90% 的情况是：**用户在数据库中没有服务器账号记录**。

解决方法：创建服务器账号（参考 `NEXT_STEPS.md`）

## 🆘 需要帮助？

查看 `NEXT_STEPS.md` 获取完整的操作步骤和解决方案。
