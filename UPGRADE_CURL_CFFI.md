# curl_cffi 升级说明

## 问题背景

Outlook 邮件功能使用 `curl_cffi` 库支持 `socks5h://` 代理协议，但旧版本 `0.6.2` 存在以下问题：

1. **异常处理不稳定**：`curl_cffi.requests.exceptions.Timeout` 在某些情况下无法正确捕获
2. **功能限制**：对 `socks5h://` 协议的支持不完善
3. **兼容性问题**：与新版本的异常类结构不同

## 升级内容

### 版本变更

```diff
- curl_cffi==0.6.2
+ curl_cffi~=0.14.0  # 最新稳定版本
```

### 改进点

- ✅ 更稳定的异常处理
- ✅ 完整支持 `socks5h://` 协议
- ✅ 更好的代理支持
- ✅ 性能优化
- ✅ 更多浏览器指纹支持
- ✅ 修复了大量已知问题

## 升级步骤

### Docker 部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像（会自动安装新版本）
docker compose build backend-api

# 3. 重启服务
docker compose up -d backend-api

# 4. 验证版本
docker compose exec backend-api python -c "import curl_cffi; print(curl_cffi.__version__)"
```

### 原生部署

```bash
# 1. 拉取最新代码
git pull

# 2. 升级依赖
cd backend
pip install --upgrade curl_cffi

# 3. 验证版本
python -c "import curl_cffi; print(curl_cffi.__version__)"

# 4. 重启服务
bash ../restart-backend-clean.sh
```

## 验证升级

### 检查版本

```bash
# Docker 环境
docker compose exec backend-api python -c "import curl_cffi; print(curl_cffi.__version__)"

# 原生环境
python -c "import curl_cffi; print(curl_cffi.__version__)"
```

应该显示 `0.14.0` 或更高版本。

### 测试 Outlook 功能

1. 访问 API 文档：`http://your-server:6080/docs`
2. 找到 `/v1/mail/outlook/messages` 接口
3. 测试获取邮件功能
4. 检查日志，不应该再出现 `module 'curl_cffi.requests.exceptions' has no attribute 'Timeout'` 错误

## 回滚方案

如果升级后出现问题，可以回滚到旧版本：

```bash
# 修改 requirements.txt
curl_cffi==0.6.2

# 重新安装
pip install -r requirements.txt

# 重启服务
bash restart-backend-clean.sh
```

## 注意事项

1. **Docker 部署**：必须重新构建镜像才能生效
2. **原生部署**：直接 `pip install --upgrade` 即可
3. **测试环境**：建议先在测试环境验证后再升级生产环境
4. **依赖冲突**：如果遇到依赖冲突，可以尝试 `pip install --upgrade --force-reinstall curl_cffi`

## 相关修改

- `backend/requirements.txt`：升级 curl_cffi 版本要求
- `backend/app/utils/req.py`：优化异常处理，兼容新旧版本
- `backend/app/clients/outlook.py`：使用 `_req2()` 方法支持 socks5h

## 技术说明

### 为什么使用 curl_cffi？

1. **完整的协议支持**：支持 `socks5h://`（DNS 在代理端解析）
2. **浏览器指纹模拟**：可以模拟真实浏览器请求
3. **性能优秀**：基于 libcurl，性能优于纯 Python 实现
4. **TLS 指纹**：可以绕过某些反爬虫检测

### socks5 vs socks5h

- `socks5://`：DNS 在本地解析（可能泄露）
- `socks5h://`：DNS 在代理服务器解析（更安全）

对于 Outlook API 这种敏感服务，使用 `socks5h://` 可以：
- 防止 DNS 泄露
- 绕过 DNS 污染
- 提高隐私保护

## 更新日志

- **2026-02-06**：升级 curl_cffi 从 0.6.2 到 ~=0.14.0（最新稳定版）
- **2026-02-06**：优化异常处理，兼容新旧版本
- **2026-02-06**：Outlook 客户端改用 _req2() 方法
