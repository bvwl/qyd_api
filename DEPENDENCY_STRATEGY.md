# 依赖版本管理策略

## 版本符号说明

| 符号 | 含义 | 示例 | 允许范围 | 使用场景 |
|------|------|------|---------|---------|
| `==` | 精确版本 | `==1.2.3` | 只有 1.2.3 | 已知稳定版本 |
| `>=` | 最小版本 | `>=1.2.0` | 1.2.0 及以上 | 需要新特性 |
| `~=` | 兼容版本 | `~=1.2.3` | >=1.2.3, <1.3.0 | **推荐** |
| `^` | 主版本兼容 | `^1.2.3` | >=1.2.3, <2.0.0 | npm 风格 |

## 本项目策略

### 核心框架（固定版本）

**原因**：核心框架变更影响大，需要严格控制

```python
# 核心框架 - 使用固定版本
fastapi==0.109.0
uvicorn[standard]==0.27.0
tortoise-orm==0.20.0
```

**何时更新**：
- 有重大安全漏洞
- 需要新功能
- 定期维护（每季度评估）

### 工具库（兼容版本）

**原因**：工具库更新频繁，补丁版本通常向后兼容

```python
# HTTP 客户端 - 使用兼容版本
curl_cffi~=0.7.0      # 允许 0.7.x，不允许 0.8.0
httpx~=0.26.0
requests~=2.31.0

# 日志管理 - 使用兼容版本
loguru~=0.7.2

# 工具库 - 使用兼容版本
tenacity~=8.2.3
```

**何时更新**：
- 自动获取补丁更新（0.7.0 → 0.7.1）
- 手动评估小版本更新（0.7.x → 0.8.0）

### 安全相关（固定版本）

**原因**：安全库需要严格测试

```python
# 认证和加密 - 使用固定版本
python-jose[cryptography]==3.3.0
bcrypt==4.0.1
cryptography==41.0.7
```

**何时更新**：
- 有安全漏洞公告
- 经过充分测试后

### 数据库相关（固定版本）

**原因**：数据库操作需要稳定性

```python
# 数据库 - 使用固定版本
aiomysql==0.2.0
pymysql==1.1.0
redis==5.0.1
```

**何时更新**：
- 有性能优化
- 修复关键 bug
- 经过测试后

## 更新流程

### 1. 定期检查（每月）

```bash
# 检查过期的依赖
pip list --outdated

# 或使用工具
pip install pip-review
pip-review
```

### 2. 评估更新

对于每个过期的依赖，评估：
- ✅ 是否有安全漏洞？
- ✅ 是否有需要的新功能？
- ✅ 变更日志（CHANGELOG）是否有破坏性变更？
- ✅ 是否影响其他依赖？

### 3. 测试更新

```bash
# 在测试环境更新
pip install --upgrade package_name

# 运行测试
pytest

# 手动测试关键功能
```

### 4. 更新生产环境

```bash
# 更新 requirements.txt
# 提交代码
git add requirements.txt
git commit -m "chore(deps): 升级 package_name 到 x.y.z"

# 部署到生产
```

## 依赖锁定（推荐）

### 使用 pip-tools

```bash
# 安装 pip-tools
pip install pip-tools

# 创建 requirements.in（只列出直接依赖）
cat > requirements.in << EOF
fastapi~=0.109.0
uvicorn[standard]~=0.27.0
curl_cffi~=0.7.0
EOF

# 生成锁定文件（包含所有传递依赖的精确版本）
pip-compile requirements.in

# 安装
pip-sync requirements.txt
```

**优点**：
- ✅ 开发时灵活（requirements.in 使用 ~=）
- ✅ 部署时精确（requirements.txt 使用 ==）
- ✅ 可重现性强

### 使用 Poetry（更现代）

```bash
# 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 初始化项目
poetry init

# 添加依赖
poetry add "curl_cffi~=0.7.0"

# 安装依赖
poetry install

# 更新依赖
poetry update curl_cffi
```

## 安全扫描

### 使用 safety

```bash
# 安装
pip install safety

# 扫描已知漏洞
safety check

# 或使用 GitHub Dependabot（推荐）
# 在 .github/dependabot.yml 配置
```

### GitHub Dependabot 配置

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "your-username"
```

## 本项目当前策略总结

| 类别 | 策略 | 原因 |
|------|------|------|
| 核心框架 | `==` 固定 | 稳定性优先 |
| HTTP 客户端 | `~=` 兼容 | 需要安全补丁 |
| 安全库 | `==` 固定 | 需要严格测试 |
| 数据库 | `==` 固定 | 数据安全优先 |
| 工具库 | `~=` 兼容 | 灵活性优先 |

## 推荐阅读

- [PEP 440 - Version Identification](https://peps.python.org/pep-0440/)
- [pip-tools 文档](https://github.com/jazzband/pip-tools)
- [Poetry 文档](https://python-poetry.org/)
- [Semantic Versioning](https://semver.org/)

## 常见问题

### Q: 为什么不全部使用 `>=`？

A: `>=` 太宽松，可能引入破坏性变更。例如 `>=1.0.0` 会允许 2.0.0，可能完全不兼容。

### Q: 为什么不全部使用 `==`？

A: 太严格，无法获取安全补丁。例如 `==1.2.3` 即使 1.2.4 修复了严重漏洞也不会更新。

### Q: `~=` 和 `^` 有什么区别？

A:
- `~=1.2.3` 允许 `>=1.2.3, <1.3.0`（补丁更新）
- `^1.2.3` 允许 `>=1.2.3, <2.0.0`（小版本更新）

Python 推荐使用 `~=`，npm 使用 `^`。

### Q: 如何处理依赖冲突？

A:
```bash
# 查看依赖树
pip install pipdeptree
pipdeptree

# 查看冲突
pip check

# 解决冲突：调整版本范围或使用虚拟环境隔离
```

## 更新日志

- **2026-02-06**：创建依赖管理策略文档
- **2026-02-06**：curl_cffi 改用 `~=0.7.0` 兼容版本
