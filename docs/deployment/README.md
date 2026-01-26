# 部署文档

本目录包含所有与部署相关的文档。

## 文档列表

### Docker 部署
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Docker 完整部署指南（60+页）
- [DOCKER_QUICK_REFERENCE.md](DOCKER_QUICK_REFERENCE.md) - Docker 快速参考
- [DOCKER_SETUP_COMPLETE.md](DOCKER_SETUP_COMPLETE.md) - Docker 部署方案总结
- [DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md) - 部署架构详解 ⭐
- [FRONTEND_DEPLOYMENT.md](FRONTEND_DEPLOYMENT.md) - 前端部署详解（多阶段构建）⭐

### 传统部署
- [COMPLETE_DEPLOYMENT_SETUP.md](COMPLETE_DEPLOYMENT_SETUP.md) - 完整部署设置
- [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) - 部署总结
- [FINAL_DEPLOYMENT_SUMMARY.md](FINAL_DEPLOYMENT_SUMMARY.md) - 最终部署总结

### 后端部署
- [../backend/DEPLOYMENT_GUIDE.md](../../backend/DEPLOYMENT_GUIDE.md) - 后端详细部署指南
- [../backend/QUICK_DEPLOY_REFERENCE.md](../../backend/QUICK_DEPLOY_REFERENCE.md) - 后端快速部署参考

⭐ 标记为新增文档（2026-01-26）

## 快速开始

### Docker 部署（推荐）

```bash
# 1. 配置环境变量
cp .env.docker .env
vim .env

# 2. 一键部署
bash docker-deploy.sh
```

详见：[DOCKER_QUICK_REFERENCE.md](DOCKER_QUICK_REFERENCE.md)

### 传统部署

```bash
# 后端
cd backend
bash quick_deploy.sh

# 前端
cd frontend
npm install
npm run build
```

详见：[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)

## 相关文档

- [项目主 README](../../README.md)
- [后端 README](../../backend/README.md)
- [前端 README](../../frontend/README.md)
- [性能优化文档](../performance/)
- [文档索引](../DOCUMENTATION_INDEX.md)

---

**最后更新**: 2026-01-26
