# 快速修复指南

## Redis MISCONF 错误 - 立即修复

### 方法1：一键修复（推荐）

```bash
cd backend
python scripts/fix_redis_misconf.py
```

按提示选择 `1` 即可立即修复。

### 方法2：手动修复

```bash
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ CONFIG SET stop-writes-on-bgsave-error no
```

### 方法3：永久修复

编辑 `/etc/redis/redis.conf`，添加：

```conf
stop-writes-on-bgsave-error no
```

然后重启 Redis：

```bash
systemctl restart redis
```

## JSON 数据格式错误 - 自动修复

系统已自动添加 JSON 数据验证和清理功能：

- ✅ 自动检测无效 JSON 数据
- ✅ 自动清空无效字段
- ✅ 记录问题数据样本
- ✅ 避免无效数据重试

如果继续出现 JSON 错误，查看日志：

```bash
# 查看 JSON 错误
grep "JSON 格式错误" backend/logs/app.log | tail -10

# 查看问题数据样本
grep "问题数据样本" backend/logs/app.log | tail -5
```

## 清理磁盘空间

```bash
# 清理日志（保留7天）
cd backend
python scripts/cleanup_logs.py

# 检查磁盘空间
df -h
```

## 验证修复

```bash
# 测试 Redis 写入
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ SET test "ok"

# 查看日志（应该没有重复错误）
tail -f backend/logs/app.log
```

## 详细文档

- `JSON_DATA_FIX.md` - JSON 数据错误修复指南
- `REDIS_ERROR_FIX_SUMMARY.md` - 完整修复总结
- `REDIS_MISCONF_FIX.md` - 详细修复指南
- `LOG_CONFIG_UPDATE.md` - 日志配置说明

## 已完成的改进

✅ 错误去重机制（5分钟内相同错误只记录一次）  
✅ Redis 错误特殊处理（提供解决方案）  
✅ JSON 数据验证和清理（自动处理无效数据）  
✅ 日志优化（200MB分割，保留7天）  
✅ 自动化修复脚本  
✅ 详细文档和指南  

现在你的系统已经更加稳定和高效！
