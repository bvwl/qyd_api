# 后端文件组织说明

## 📋 文件组织原则

### 根目录
**只保留启动脚本和配置文件**

```
backend/
├── start.py                # ✅ 启动脚本（唯一的根目录 .py 文件）
├── README.md               # ✅ 项目文档
├── .env                    # ✅ 环境变量
├── .env.example            # ✅ 环境变量模板
├── requirements.txt        # ✅ 依赖列表
├── pyproject.toml          # ✅ 项目配置
├── pytest.ini              # ✅ pytest 配置
├── compose.yml             # ✅ Docker Compose
├── Dockerfile              # ✅ Docker 配置
└── run_tests.sh            # ✅ 测试脚本
```

### app/ 目录
**应用代码和测试**

```
app/
├── main.py                 # FastAPI 应用入口
├── models/                 # 数据模型
├── schemas/                # API Schema
├── crud/                   # 数据库操作
├── apis/                   # API 路由
├── clients/                # 外部客户端
├── core/                   # 核心配置
├── utils/                  # 工具函数
├── tests/                  # ✅ 所有测试文件
│   ├── test_user.py
│   ├── test_project.py
│   ├── test_server.py
│   ├── test_mail.py
│   └── test_logging_system.py  # 日志系统测试
└── logs/                   # 日志文档
```

### scripts/ 目录
**工具脚本和辅助程序**

```
scripts/
├── verify_setup.py         # ✅ 验证脚本
├── check_db_tables.py      # ✅ 检查数据库表
├── test_db_connection.py   # ✅ 测试数据库连接
├── cleanup_logs.py         # 日志清理
├── analyze_logs.py         # 日志分析
├── init_db.sh              # 初始化数据库
├── update_db.sh            # 更新数据库
├── reset_db.sh             # 重置数据库
└── log_manager.sh          # 日志管理
```

### examples/ 目录
**示例代码**

```
examples/
└── log_usage_examples.py   # 日志使用示例
```

## 🔄 文件移动记录

### 2026-01-21 文件重组

#### 移动到 app/tests/
- `test_logging_system.py` → `app/tests/test_logging_system.py`

#### 移动到 scripts/
- `verify_setup.py` → `scripts/verify_setup.py`
- `check_db_tables.py` → `scripts/check_db_tables.py`
- `test_db_connection.py` → `scripts/test_db_connection.py`

## 📝 路径更新说明

### 1. 运行验证脚本
```bash
# 之前
python verify_setup.py

# 之后
python scripts/verify_setup.py
```

### 2. 运行测试
```bash
# 之前
python test_logging_system.py

# 之后
python app/tests/test_logging_system.py

# 或使用 pytest
pytest app/tests/test_logging_system.py
```

### 3. 检查数据库
```bash
# 之前
python check_db_tables.py

# 之后
python scripts/check_db_tables.py
```

### 4. 测试数据库连接
```bash
# 之前
python test_db_connection.py

# 之后
python scripts/test_db_connection.py
```

## ✅ 代码路径修复

所有移动到 `scripts/` 的文件已更新路径：

```python
# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent  # 从 scripts/ 回到 backend/
sys.path.insert(0, str(backend_path))
```

## 🎯 组织优势

### 1. 清晰的目录结构
- **根目录**: 只有启动和配置文件
- **app/tests/**: 所有测试集中管理
- **scripts/**: 所有工具脚本集中管理
- **examples/**: 示例代码独立存放

### 2. 符合最佳实践
- 遵循 Python 项目标准结构
- 测试文件与应用代码在同一目录树
- 工具脚本独立于应用代码

### 3. 易于维护
- 文件位置清晰明确
- 减少根目录混乱
- 便于查找和管理

### 4. 便于部署
- 根目录文件少，部署配置简单
- 测试文件可选择性部署
- 工具脚本可独立管理

## 📚 相关文档

- `README.md` - 完整项目文档（已更新所有路径）
- `CLEANUP_SUMMARY.md` - 文件清理总结
- `FILE_ORGANIZATION.md` - 本文档

## 🔍 快速查找

### 我想运行...

| 任务 | 命令 |
|------|------|
| 启动服务 | `python start.py` |
| 验证配置 | `python scripts/verify_setup.py` |
| 运行测试 | `pytest app/tests/` |
| 测试日志 | `python app/tests/test_logging_system.py` |
| 检查数据库 | `python scripts/check_db_tables.py` |
| 清理日志 | `python scripts/cleanup_logs.py` |
| 分析日志 | `python scripts/analyze_logs.py` |
| 管理日志 | `./scripts/log_manager.sh help` |

### 我想查看...

| 内容 | 位置 |
|------|------|
| 项目文档 | `README.md` |
| 测试文件 | `app/tests/` |
| 工具脚本 | `scripts/` |
| 示例代码 | `examples/` |
| 应用代码 | `app/` |
| 配置文件 | 根目录 |

## ⚠️ 注意事项

1. **不要在根目录添加新的 .py 文件**
   - 测试文件 → `app/tests/`
   - 工具脚本 → `scripts/`
   - 示例代码 → `examples/`

2. **路径引用**
   - `scripts/` 中的文件需要添加 `backend_path` 到 `sys.path`
   - `app/tests/` 中的文件可以直接导入 `app` 模块

3. **文档更新**
   - 添加新文件时，更新 `README.md`
   - 移动文件时，更新相关文档中的路径

## ✨ 总结

文件组织已优化完成：
- ✅ 根目录简洁（只有启动和配置）
- ✅ 测试文件集中（app/tests/）
- ✅ 工具脚本集中（scripts/）
- ✅ 所有路径已更新
- ✅ 文档已同步更新

项目结构现在更加清晰和易于维护！
