# QYD 前端维护手册

QYD 前端是基于 React、TypeScript 和 Ant Design 的管理后台，覆盖仪表盘、用户与权限、项目、服务器、邮箱和 XUI 等模块。本项目已经上线；前端 API 地址会在构建时写入静态资源，修改环境变量后必须重新构建并验证。

## 技术栈

- React 18.3
- TypeScript 5.6
- Ant Design 5
- Vite 6
- React Router DOM 7
- Zustand 5
- Axios
- Less
- ECharts 6
- xlsx

## 入口与目录

当前实际入口：

```text
index.html
  → src/main.tsx
  → src/App.tsx
```

`src/router/index.tsx` 维护了另一套路由定义，但当前入口没有使用它。后续调整路由时应先统一入口，避免两套路由长期漂移。

```text
frontend/
├── public/             # 原样复制的静态资源
├── src/
│   ├── api/            # Axios 实例与业务 API
│   ├── components/     # 布局、鉴权和通用组件
│   ├── hooks/          # 权限等自定义 Hook
│   ├── router/         # 备用路由配置
│   ├── store/          # Zustand 状态
│   ├── types/          # TypeScript 类型
│   ├── utils/          # Token、格式化和表单工具
│   ├── views/          # 页面模块
│   ├── App.tsx         # 当前路由与应用入口
│   └── main.tsx        # React 挂载入口
├── Dockerfile
├── nginx.conf
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 本地开发

要求 Node.js 18+ 和 npm。以下命令在 `frontend/` 目录执行：

```bash
npm ci
npm run dev
```

开发服务默认监听 `http://localhost:3000`。

可用 npm 命令：

| 命令 | 作用 |
| --- | --- |
| `npm run dev` | 启动 Vite 开发服务 |
| `npm run build` | 先执行 TypeScript 检查，再构建 |
| `npm run preview` | 本地预览构建产物 |
| `npm run lint` | ESLint 检查 |

仓库没有 `type-check` 命令，也未配置 Vitest、Jest、Playwright 或 Cypress 测试套件。

## 环境变量

开发环境示例：

```env
VITE_API_BASE_URL=http://127.0.0.1:6080
VITE_APP_TITLE=QYD 项目管理系统
```

- `VITE_API_BASE_URL` 必须是后端根地址，不要追加 `/v1`；业务 API 自身已经使用 `/v1/...`。
- `VITE_API_BASE_URL` 在构建时注入。更改生产 API 地址后必须重新构建镜像或静态资源。
- 所有 `VITE_*` 变量都会暴露给浏览器，禁止写入密码、Token 或其他秘密。
- `VITE_APP_TITLE` 当前虽已声明和传入构建，但页面标题仍由 `index.html` 设置。

开发配置中存在 Vite 的 `/v1` 代理；当 `VITE_API_BASE_URL` 使用绝对地址时，请求会直接访问该地址，代理不会生效。此时后端必须正确配置 CORS。

## API 与认证

- Axios 基础地址来自 `VITE_API_BASE_URL`。
- API 路径为 `/v1/*`，默认超时 60 秒。
- JWT 保存在 `localStorage.access_token`。
- 请求使用 `Authorization: Bearer <token>`。
- 收到 401 时会清除 Token 和用户状态，并跳转登录页。
- 当前没有自动刷新 Token 的实现。

不要在浏览器控制台、截图、Issue 或日志中暴露 Token。

## 构建与部署

### 常规构建

```bash
npm ci
npm run build
```

产物输出到 `dist/`。部署时应由 Nginx 或其他静态服务器提供该目录，并为 SPA 路由配置回退到 `index.html`。

### Docker 完整栈

仓库根目录的 `docker-compose.yml` 会通过 `frontend/Dockerfile` 构建前端，再由容器内 Nginx 提供静态资源。发布前先在仓库根目录校验配置：

```bash
docker compose config --quiet
docker compose build frontend
docker compose up -d frontend
```

完整栈模式通常还由外层 Nginx 统一暴露前端端口和后端 `6080`。浏览器会直接请求构建时指定的 `VITE_API_BASE_URL`，因此要同时验证网络可达性和后端 CORS。

### 前端独立部署

`docker-compose.frontend.yml` 将前端映射到宿主机 `8080`：

```bash
docker compose -f docker-compose.frontend.yml config --quiet
docker compose -f docker-compose.frontend.yml build
docker compose -f docker-compose.frontend.yml up -d
```

容器内 Nginx：

- 监听 80；
- 使用 `try_files` 支持 SPA 路由刷新；
- 对静态资源启用长期缓存；
- 提供 `/health` 健康检查；
- 不代理后端 API。

如果前端使用 HTTPS，后端 API 也必须使用 HTTPS，否则浏览器会拦截混合内容。

## 当前已知维护项

截至 2026-08-02：

- `npm run build` 会因现存 TypeScript 错误失败。
- Dockerfile 使用 `npx vite build` 跳过 `tsc`，因此 Docker 构建结果与常规构建门禁不一致。
- `npm run lint` 会因 ESLint 9 配置不在前端根目录而失败；现有配置位于 `tests/eslint.config.js`。
- 尚无自动化前端测试框架。
- `src/App.tsx` 与 `src/router/index.tsx` 存在两套路由来源。

这些问题不应通过长期跳过检查来掩盖。后续功能调整前，建议先恢复 TypeScript、ESLint 和最小化页面冒烟测试。

## 上线前检查

1. 确认 `VITE_API_BASE_URL` 指向目标环境，且没有携带 `/v1`。
2. 使用干净依赖执行构建，记录构建日志和 Commit。
3. 检查生成资源中没有测试地址、内网旧地址或秘密。
4. 验证登录、权限菜单、仪表盘和至少一个增删改查流程。
5. 验证刷新深层路由不会返回 404。
6. 验证 401 跳转、403 提示、上传/导出和长请求超时行为。
7. 检查桌面常用分辨率下的布局和浏览器控制台。
8. 保留上一版本镜像或上一份静态产物用于回滚。

## 回滚

前端发布应使用不可变镜像标签或带版本号的静态产物。出现问题时：

1. 停止继续扩大发布范围。
2. 恢复上一版本镜像或静态目录。
3. 检查浏览器与 CDN 缓存是否仍引用新资源。
4. 重新验证登录、主导航和 API 连通性。
5. 记录失败版本、环境变量和构建日志，修复后重新走完整验证。
