# 服务器列表界面更新

## 更新内容

### 1. 隐藏 SSH 端口列

SSH 端口是服务器管理的内部信息，不需要在列表中展示给用户。

**修改前**：
- 表格显示 SSH 端口列

**修改后**：
- 移除 SSH 端口列
- 添加代理端口列（更有用的信息）

### 2. 添加复制 SOCKS5 代理信息按钮

为每个服务器添加一键复制 SOCKS5 代理信息的功能，方便用户快速获取代理配置。

**功能特点**：
- 点击按钮一键复制完整的 SOCKS5 代理 URL
- 代理 URL 格式：`socks5://username:password@host:port`
- 代理 URL 中的用户名和密码是当前登录用户自己的服务器账号
- 复制成功后显示提示消息
- 如果代理信息不可用，显示警告消息

## 文件修改

### 1. 前端类型定义 (`frontend/src/types/index.ts`)

添加 `proxy_url` 字段到 `ServerInfo` 接口：

```typescript
export interface ServerInfo {
  id: string
  host: string
  ssh_port?: number
  password?: string
  status: Status
  domain?: string
  is_sale: number
  port?: number
  proxy_url?: string  // SOCKS5代理URL
  group_id?: string
  group?: ServerGroup
  create_time: string
  update_time: string
}
```

### 2. 服务器列表组件 (`frontend/src/views/Server/ServerList.tsx`)

#### 添加复制功能

```typescript
const handleCopyProxyUrl = (proxyUrl?: string) => {
  if (!proxyUrl) {
    message.warning('代理信息不可用')
    return
  }
  
  navigator.clipboard.writeText(proxyUrl).then(() => {
    message.success('SOCKS5代理信息已复制到剪贴板')
  }).catch(() => {
    message.error('复制失败，请手动复制')
  })
}
```

#### 更新表格列定义

```typescript
const columns = [
  {
    title: '主机地址',
    dataIndex: 'host',
    key: 'host',
  },
  {
    title: '域名',
    dataIndex: 'domain',
    key: 'domain',
    ellipsis: true,
  },
  {
    title: '代理端口',  // 新增：显示代理端口而不是 SSH 端口
    dataIndex: 'port',
    key: 'port',
  },
  // ... 其他列
  {
    title: '操作',
    key: 'action',
    render: (_: any, record: ServerInfo) => (
      <Space>
        <Button
          type="link"
          icon={<CopyOutlined />}
          onClick={() => handleCopyProxyUrl(record.proxy_url)}
          title="复制SOCKS5代理信息"
        >
          复制代理
        </Button>
        {/* 管理员操作按钮 */}
      </Space>
    ),
  },
]
```

## 用户体验改进

### 1. 信息展示优化
- **移除 SSH 端口**：SSH 端口是服务器管理信息，普通用户不需要看到
- **显示代理端口**：代理端口是用户实际使用的端口，更有价值

### 2. 操作便捷性
- **一键复制**：用户无需手动选择和复制代理信息
- **即时反馈**：复制成功或失败都有明确的提示消息
- **所有用户可用**：不仅管理员，所有用户都可以复制自己的代理信息

### 3. 安全性
- **个性化代理**：每个用户复制的代理 URL 包含自己的账号和密码
- **权限隔离**：普通用户看到的是加密密码，管理员看到的是明文密码

## 使用场景

1. **配置代理工具**：用户可以快速复制代理信息到浏览器插件或代理工具
2. **分享代理配置**：用户可以将代理信息分享给团队成员（每个人的账号不同）
3. **快速测试**：开发人员可以快速复制代理信息进行测试

## 示例

### 代理 URL 格式

```
socks5://user_7914cbac:Yvlo1k5gP4sR@zd1.0n.lv:30001
```

- `user_7914cbac`：用户的服务器账号用户名
- `Yvlo1k5gP4sR`：用户的服务器账号密码（解密后）
- `zd1.0n.lv`：服务器域名（如果没有域名则使用 IP）
- `30001`：代理端口

### 复制操作流程

1. 用户点击"复制代理"按钮
2. 系统将完整的 SOCKS5 代理 URL 复制到剪贴板
3. 显示"SOCKS5代理信息已复制到剪贴板"提示
4. 用户可以直接粘贴到需要的地方使用

## 注意事项

1. **浏览器兼容性**：使用 `navigator.clipboard.writeText()` API，需要 HTTPS 或 localhost 环境
2. **代理信息可用性**：如果服务器没有配置代理端口，会显示"代理信息不可用"
3. **用户账号依赖**：代理 URL 依赖用户的服务器账号，如果用户没有服务器账号，会显示默认的 "username:password"

## 测试建议

1. ✅ 测试复制功能是否正常工作
2. ✅ 测试不同用户复制的代理信息是否不同
3. ✅ 测试管理员和普通用户看到的密码是否符合预期
4. ✅ 测试没有代理端口的服务器是否正确提示
5. ✅ 测试表格列是否正确显示（SSH 端口已隐藏，代理端口已显示）

## 总结

通过隐藏 SSH 端口和添加复制代理信息按钮，提升了服务器列表的用户体验：
- 信息展示更加简洁和有用
- 操作更加便捷和高效
- 每个用户都能快速获取自己的代理配置
