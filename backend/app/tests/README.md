# API 接口测试文档

## 测试文件结构

```
tests/
├── README.md                 # 本文档
├── run_all_tests.py         # 运行所有测试的主入口
├── test_server.py           # 服务器相关接口测试
├── test_mail.py             # 邮箱相关接口测试
├── test_project.py          # 项目相关接口测试
├── test_user.py             # 用户相关接口测试
├── api_requests_test.py     # 旧版测试（保留）
└── user_requests_test.py    # 旧版用户测试（保留）
```

## 测试模块说明

### 1. test_server.py - 服务器相关接口
测试外键依赖顺序：Country → Group → ServerInfo → ServerAccount

**测试类：**
- `TestServerCountry` - 国家信息接口
  - 创建、获取、列表、更新、删除、upsert
- `TestServerGroup` - 分组信息接口（依赖 Country）
  - 创建、获取、列表、更新、删除
- `TestServerInfo` - 服务器信息接口（依赖 Group）
  - 创建、获取、列表、更新、删除
- `TestServerAccount` - 代理账号接口（独立）
  - 创建、获取、列表、更新、删除

### 2. test_mail.py - 邮箱相关接口
测试外键依赖：ServerInfo

**测试类：**
- `TestEmailInfo` - 邮箱信息接口（依赖 ServerInfo）
  - 创建、获取、列表、更新、删除、upsert

### 3. test_project.py - 项目相关接口
测试外键依赖顺序：ProjectInfo → ProjectAccount → ProjectBalance / ProjectWallet

**测试类：**
- `TestProjectInfo` - 项目信息接口
  - 创建、获取、列表、更新、删除、upsert
- `TestProjectAccount` - 项目账号接口（依赖 ProjectInfo, ServerInfo）
  - 创建、获取、列表、更新、删除
- `TestProjectBalance` - 项目余额接口（依赖 ProjectAccount）
  - 创建、获取、列表、更新、删除
- `TestProjectWallet` - 项目钱包接口（依赖 ProjectInfo）
  - 创建、获取、列表、更新、删除

### 4. test_user.py - 用户相关接口

**测试类：**
- `TestUserAuth` - 用户认证接口
  - 注册、登录、重复邮箱注册、错误密码登录
- `TestUserManagement` - 用户管理接口
  - 获取、列表、更新、删除

## 运行测试

### 前置条件

1. 确保后端服务已启动：
```bash
cd backend
python start.py
```

2. 安装测试依赖：
```bash
pip install pytest requests
```

### 运行方式

#### 1. 运行所有测试
```bash
cd backend/app/tests
python run_all_tests.py
```

或使用 pytest：
```bash
cd backend
pytest app/tests/ -v
```

#### 2. 运行单个测试文件
```bash
cd backend
pytest app/tests/test_server.py -v
pytest app/tests/test_mail.py -v
pytest app/tests/test_project.py -v
pytest app/tests/test_user.py -v
```

#### 3. 运行单个测试类
```bash
cd backend
pytest app/tests/test_server.py::TestServerCountry -v
pytest app/tests/test_project.py::TestProjectInfo -v
```

#### 4. 运行单个测试方法
```bash
cd backend
pytest app/tests/test_server.py::TestServerCountry::test_create_country -v
```

### 环境变量配置

可以通过环境变量配置测试服务器地址：

```bash
export APP_HOST=127.0.0.1
export APP_PORT=6080
```

或在运行时指定：
```bash
APP_HOST=localhost APP_PORT=8000 python run_all_tests.py
```

## 测试特点

### 1. 自动清理
每个测试方法都会在测试完成后自动清理创建的数据，确保测试环境干净。

### 2. 外键依赖处理
使用 pytest fixtures 自动创建和清理依赖的外键数据：

```python
@pytest.fixture
def setup_country(self):
    """创建测试用的国家"""
    country = _req("POST", "/server/country", json={...})
    yield country["id"]
    # 测试完成后自动清理
    _req("DELETE", f"/server/country/{country['id']}")
```

### 3. 随机数据生成
使用 UUID 和随机字符串生成测试数据，避免数据冲突：

```python
email = f"user{uuid.uuid4().hex[:6]}@example.com"
short_name = _rand_letters(2)
```

### 4. 完整的 CRUD 测试
每个接口都测试了完整的 CRUD 操作：
- Create（创建）
- Read（获取单个、列表）
- Update（更新）
- Delete（删除）
- Upsert（创建或更新，如果支持）

## 测试覆盖

### 已覆盖的接口

✅ 服务器模块
- `/v1/server/country` - 国家信息
- `/v1/server/group` - 分组信息
- `/v1/server/info` - 服务器信息
- `/v1/server/account` - 代理账号

✅ 邮箱模块
- `/v1/mail/info` - 邮箱信息

✅ 项目模块
- `/v1/project/info` - 项目信息
- `/v1/project/account` - 项目账号
- `/v1/project/balance` - 项目余额
- `/v1/project/wallet` - 项目钱包

✅ 用户模块
- `/v1/user/auth/register` - 用户注册
- `/v1/user/auth/login` - 用户登录
- `/v1/user/user` - 用户管理

### 待添加的测试

- Outlook 邮件操作接口
- 权限和角色管理接口
- Token 管理接口
- 用户日志接口

## 常见问题

### 1. 测试失败：连接被拒绝
确保后端服务已启动并监听正确的端口。

### 2. 测试失败：外键约束错误
检查数据库迁移是否已执行，确保所有表结构正确。

### 3. 测试失败：唯一约束冲突
测试使用随机数据，但如果数据库中已有大量数据，可能会偶尔冲突。重新运行测试即可。

## 贡献指南

添加新的测试时，请遵循以下规范：

1. **文件命名**：`test_<模块名>.py`
2. **类命名**：`Test<功能名>`
3. **方法命名**：`test_<操作>_<对象>`
4. **使用 fixtures**：处理外键依赖
5. **自动清理**：确保测试后清理数据
6. **断言充分**：验证关键字段和状态

示例：
```python
class TestNewFeature:
    @pytest.fixture
    def setup_dependency(self):
        # 创建依赖数据
        data = _req("POST", "/api/dependency", json={...})
        yield data["id"]
        # 清理
        _req("DELETE", f"/api/dependency/{data['id']}")
    
    def test_create_feature(self, setup_dependency):
        result = _req("POST", "/api/feature", json={
            "dependency_id": setup_dependency,
            ...
        })
        assert result["message"] == "成功"
        # 清理
        _req("DELETE", f"/api/feature/{result['id']}")
```
