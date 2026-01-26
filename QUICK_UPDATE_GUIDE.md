# 快速更新指南

## 问题说明

生产环境的后端容器运行的是旧代码，导致 `/v1/user/role/tree` 接口报错：
```
{"detail":"'UserRole' object has no attribute 'status'"}
```

最新代码已经修复了这个问题（commit: cef474e），但需要重新构建容器才能生效。

## 解决方案

在生产服务器上执行以下命令：

```bash
# 进入项目目录
cd /opt/zy/qyd_api

# 执行更新脚本（会自动拉取代码、重新构建并启动容器）
bash update-and-restart.sh
```

## 脚本执行步骤

`update-and-restart.sh` 会自动执行以下操作：

1. **拉取最新代码** - `git pull`
2. **加载环境变量** - 从 `.env.high_concurrency` 加载配置
3. **停止后端容器** - 停止 `backend-api` 和 `queue-worker`
4. **删除旧容器** - 删除旧的容器实例
5. **重新构建镜像** - 使用最新代码构建新镜像
6. **启动新容器** - 启动 5 个 API 实例 + 5 个队列实例

## 预计时间

- 拉取代码: ~5秒
- 构建镜像: ~2-3分钟
- 启动容器: ~15秒
- **总计**: ~3-4分钟

## 验证方法

脚本执行完成后，可以手动测试接口：

```bash
# 使用新的 Token 测试（需要先登录获取）
curl -H "Authorization: Bearer YOUR_TOKEN" http://192.168.13.6:6080/v1/user/role/tree
```

预期返回：
```json
[
  {
    "id": "...",
    "code": "ADMIN",
    "name": "管理员",
    "description": "系统管理员，拥有所有权限",
    "create_time": "2026-01-26 ...",
    "update_time": "2026-01-26 ..."
  },
  ...
]
```

## 注意事项

1. **服务中断**: 更新过程中后端服务会短暂中断（约3-4分钟）
2. **Token 过期**: 如果之前的 Token 已过期，需要重新登录获取新 Token
3. **前端缓存**: 如果前端还有问题，可能需要清除浏览器缓存或强制刷新（Ctrl+Shift+R）

## 其他可用脚本

- `rebuild-backend.sh` - 仅重新构建后端（不拉取代码）
- `restart-backend.sh` - 仅重启后端（不重新构建）
- `check_database.py` - 检查数据库数据

## 故障排查

如果更新后还有问题：

1. **检查容器状态**:
   ```bash
   docker compose ps
   ```

2. **查看容器日志**:
   ```bash
   docker compose logs -f backend-api --tail=100
   ```

3. **检查数据库数据**:
   ```bash
   python check_database.py
   ```

4. **验证代码版本**:
   ```bash
   git log --oneline -5
   ```
   应该看到最新的 commit: `6a776e7 fix: 更新部署脚本以重新构建镜像而不是仅重启容器`
