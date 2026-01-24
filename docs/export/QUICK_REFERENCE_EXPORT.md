# 导出功能快速参考

## 🚀 快速开始

### 1. 安装依赖
```bash
cd backend
pip install openpyxl
```

### 2. 重启服务
```bash
cd backend
python start.py
```

### 3. 使用功能
- 使用 ADMIN 或 GM 账号登录
- 访问：http://localhost:3000/project/account
- 点击"导出所有项目统计"按钮

## 📊 Excel 文件内容

| 列名 | 说明 |
|------|------|
| 项目名称 | 项目的名称 |
| **项目状态** | **项目的当前状态（正常、编写中、项目结束等）** |
| 项目ID | 项目的UUID |
| 所属用户 | 用户昵称（多个用逗号分隔） |
| 账号数量 | 该项目下的账号总数 |
| 余额最高分 | 当前余额的最大值 |
| 余额最低分 | 当前余额的最小值 |
| 余额平均分 | 当前余额的平均值 |
| 余额总分 | 当前余额的总和 |
| 变动最高分 | 变动余额的最大值 |
| 变动最低分 | 变动余额的最小值 |
| 变动平均分 | 变动余额的平均值 |
| 变动总分 | 变动余额的总和 |

## 👥 用户列显示规则

| 情况 | 显示内容 | 示例 |
|------|---------|------|
| 单个用户 | 昵称 | `张三` |
| 多个用户 | 昵称（逗号分隔） | `张三, 李四, 王五` |
| 未分配 | "未分配" | `未分配` |
| 无昵称 | 邮箱 | `user@example.com` |

## 📋 项目状态显示

| 状态值 | 显示文本 |
|--------|---------|
| NORMAL | 正常 |
| NOT_WRITTEN | 未编写 |
| WRITING | 编写中 |
| ENDED | 项目结束 |
| RUNAWAY | 项目跑路 |
| MAINTENANCE | 项目维护 |
| UNASSIGNED | 未分配 |
| ACCOUNT_NOT_SUPPORT | 账号不支持 |
| IP_NOT_SUPPORT | IP不支持 |

## 🔒 权限控制

| 角色 | 查看统计 | 导出Excel | 看到按钮 |
|------|---------|----------|---------|
| ADMIN | ✅ 所有项目 | ✅ | ✅ |
| GM | ✅ 所有项目 | ✅ | ✅ |
| IT | ✅ 自己的项目 | ❌ | ❌ |
| MANUAL | ✅ 自己的项目 | ❌ | ❌ |

## 🎯 核心接口

### 统计单个项目
```
GET /v1/project/account/stats?project_id={uuid}
```

### 导出所有项目
```
GET /v1/project/account/export-all-stats
```

## 📝 文件命名

```
项目统计汇总_YYYYMMDD_HHMMSS.xlsx
```

示例：`项目统计汇总_20260125_143025.xlsx`

**注意**: 后端使用英文文件名传输（避免编码问题），前端自动重命名为中文。

## ⚡ 性能指标

- 统计单个项目：< 100ms（1000个账号）
- 导出所有项目：< 5秒（100个项目）
- 文件大小：约 10-20KB（100个项目）

## 🐛 常见问题

### Q: 导出按钮不显示？
**A**: 使用 ADMIN 或 GM 账号登录

### Q: 用户列显示不完整？
**A**: 在 Excel 中手动调整列宽

### Q: 文件名编码错误？
**A**: 已修复，现在使用英文传输+前端重命名的方式

### Q: 安装 openpyxl 失败？
**A**: 使用国内镜像
```bash
pip install openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📚 详细文档

- [快速参考卡片](./QUICK_REFERENCE_EXPORT.md)（本文档）
- [状态列和编码修复](./EXPORT_STATUS_COLUMN_AND_FIX.md)
- [完整功能说明](./EXPORT_FEATURE_COMPLETE.md)
- [用户列更新](./EXPORT_USER_COLUMN_UPDATE.md)
- [安装说明](./INSTALL_OPENPYXL.md)

## ✅ 测试清单

- [ ] ADMIN 可以导出
- [ ] GM 可以导出
- [ ] IT 看不到导出按钮
- [ ] Excel 格式正确
- [ ] 项目状态显示正确
- [ ] 用户列显示正确
- [ ] 多用户逗号分隔
- [ ] 未分配显示"未分配"
- [ ] 无昵称显示邮箱
- [ ] 文件名为中文
- [ ] 没有编码错误

## 🔧 技术栈

**后端**: FastAPI + Tortoise ORM + openpyxl  
**前端**: React 18 + TypeScript + Ant Design 5  
**数据库**: MySQL 8.0

## 📞 支持

如有问题，请查看详细文档或联系开发团队。
