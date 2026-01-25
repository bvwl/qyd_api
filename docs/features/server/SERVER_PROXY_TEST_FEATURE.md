# 服务器列表 - 代理测试功能

## 功能概述

在服务器列表中添加了"测试代理"按钮，允许用户快速测试服务器代理是否可用。

## 新增功能

### ✅ 已实现

1. **测试代理按钮**：在"复制代理"按钮旁边添加"测试代理"按钮
2. **实时检测**：点击按钮后立即检测代理可用性
3. **加载状态**：检测过程中显示加载动画
4. **结果展示**：使用 Modal 对话框展示详细的检测结果
5. **成功提示**：显示检测到的 IP 地址和来源
6. **失败提示**：显示失败原因和错误信息

## 界面展示

### 服务器列表

```
┌─────────────────────────────────────────────────────────────────────┐
│ 主机地址 | 域名 | 代理端口 | 分组 | 状态 | 是否可以出售 | 操作        │
├─────────────────────────────────────────────────────────────────────┤
│ 1.2.3.4  | -    | 1080     | 美国 | 正常 | 可以出售     | [复制代理]  │
│                                                         [测试代理]  │
│                                                         [编辑]      │
│                                                         [删除]      │
└─────────────────────────────────────────────────────────────────────┘
```

### 检测成功对话框

```
┌─────────────────────────────────┐
│ ✅ 代理检测成功                  │
├─────────────────────────────────┤
│ 代理地址：socks5h://1.2.3.4:1080│
│ 检测IP：5.6.7.8                 │
│ 检测来源：ipify                 │
│ ✅ 代理可用                      │
├─────────────────────────────────┤
│              [确定]              │
└─────────────────────────────────┘
```

### 检测失败对话框

```
┌─────────────────────────────────┐
│ ❌ 代理检测失败                  │
├─────────────────────────────────┤
│ 代理地址：socks5h://1.2.3.4:1080│
│ ❌ 代理不可用                    │
│ 原因：所有检测网站均无法访问     │
├─────────────────────────────────┤
│              [确定]              │
└─────────────────────────────────┘
```

## 使用说明

### 测试代理

1. **找到服务器**：在服务器列表中找到要测试的服务器
2. **点击测试代理**：点击"测试代理"按钮
3. **等待检测**：按钮显示加载动画，等待检测完成
4. **查看结果**：弹出对话框显示检测结果

### 检测过程

1. 点击"测试代理"按钮
2. 系统调用代理检测 API
3. 依次访问 3 个 IP 检测网站：
   - https://api.ipify.org/
   - https://api.myip.com/
   - https://iprust.io/ip.json
4. 如果任一网站返回 200，显示成功
5. 如果所有网站都失败，显示失败

## 技术实现

### 1. 添加系统 API

创建 `frontend/src/api/system.ts`：

```typescript
import api from './index'

export interface ProxyCheckResult {
  message: string
  status: 'success' | 'failed'
  proxy_url: string | null
  ip: string | null
  source: string | null
  details: any
}

export const checkProxy = (proxyUrl?: string) => {
  return api.get<any, ProxyCheckResult>('/v1/system/proxy/check', {
    params: { proxy_url: proxyUrl }
  })
}
```

### 2. 添加测试状态

```typescript
const [testingProxy, setTestingProxy] = useState<string | null>(null)
```

### 3. 实现测试函数

```typescript
const handleTestProxy = async (proxyUrl?: string, serverId?: string) => {
  if (!proxyUrl) {
    message.warning('代理信息不可用')
    return
  }

  setTestingProxy(serverId || null)
  
  try {
    const result = await checkProxy(proxyUrl)
    
    if (result.status === 'success') {
      Modal.success({
        title: '代理检测成功',
        content: (
          <div>
            <p><strong>代理地址：</strong>{proxyUrl}</p>
            <p><strong>检测IP：</strong>{result.ip}</p>
            <p><strong>检测来源：</strong>{result.source}</p>
            <p style={{ color: '#52c41a' }}>✅ 代理可用</p>
          </div>
        ),
      })
    } else {
      Modal.error({
        title: '代理检测失败',
        content: (
          <div>
            <p><strong>代理地址：</strong>{proxyUrl}</p>
            <p style={{ color: '#ff4d4f' }}>❌ 代理不可用</p>
            <p><strong>原因：</strong>{result.details?.error || '所有检测网站均无法访问'}</p>
          </div>
        ),
      })
    }
  } catch (error: any) {
    Modal.error({
      title: '代理检测失败',
      content: (
        <div>
          <p><strong>代理地址：</strong>{proxyUrl}</p>
          <p style={{ color: '#ff4d4f' }}>❌ 检测请求失败</p>
          <p><strong>错误：</strong>{error.message || '未知错误'}</p>
        </div>
      ),
    })
  } finally {
    setTestingProxy(null)
  }
}
```

### 4. 添加测试按钮

```typescript
<Button
  type="link"
  icon={testingProxy === record.id ? <Spin size="small" /> : <ApiOutlined />}
  onClick={() => handleTestProxy(record.proxy_url, record.id)}
  disabled={testingProxy === record.id}
  title="测试代理是否可用"
>
  测试代理
</Button>
```

## 按钮状态

### 正常状态
- 图标：<ApiOutlined />（API 图标）
- 文本：测试代理
- 可点击

### 检测中状态
- 图标：<Spin size="small" />（加载动画）
- 文本：测试代理
- 禁用状态（不可点击）

### 无代理信息
- 点击后提示："代理信息不可用"

## 检测结果

### 成功结果

**显示内容**：
- ✅ 标题：代理检测成功
- 代理地址
- 检测到的 IP 地址
- 检测来源（ipify/myip/iprust）
- 成功提示

**示例**：
```
代理地址：socks5h://1.2.3.4:1080
检测IP：5.6.7.8
检测来源：ipify
✅ 代理可用
```

### 失败结果

**显示内容**：
- ❌ 标题：代理检测失败
- 代理地址
- 失败提示
- 失败原因

**示例**：
```
代理地址：socks5h://1.2.3.4:1080
❌ 代理不可用
原因：所有检测网站均无法访问
```

### 请求失败

**显示内容**：
- ❌ 标题：代理检测失败
- 代理地址
- 失败提示
- 错误信息

**示例**：
```
代理地址：socks5h://1.2.3.4:1080
❌ 检测请求失败
错误：Network Error
```

## 用户体验优化

### 1. 加载状态
- 检测过程中显示加载动画
- 按钮禁用，防止重复点击

### 2. 结果展示
- 使用 Modal 对话框展示结果
- 成功使用绿色，失败使用红色
- 显示详细的检测信息

### 3. 错误处理
- 无代理信息时提示用户
- 请求失败时显示错误信息
- 所有错误都有友好的提示

### 4. 视觉反馈
- 成功：✅ 绿色提示
- 失败：❌ 红色提示
- 加载：旋转动画

## 使用场景

### 场景 1：验证新添加的服务器

```
1. 添加新服务器
2. 点击"测试代理"
3. 查看检测结果
4. 确认代理可用
```

### 场景 2：排查代理问题

```
1. 发现代理不可用
2. 点击"测试代理"
3. 查看失败原因
4. 修复代理配置
5. 再次测试
```

### 场景 3：批量检测代理

```
1. 逐个点击"测试代理"
2. 记录可用的代理
3. 标记不可用的代理
4. 更新或删除失败的代理
```

## 注意事项

1. **检测时间**：每次检测可能需要几秒钟，请耐心等待
2. **网络环境**：检测结果受服务器网络环境影响
3. **代理类型**：支持 HTTP 和 SOCKS5 代理
4. **并发限制**：同一时间只能检测一个代理
5. **权限要求**：所有登录用户都可以测试代理

## 相关文件

### 前端
- `frontend/src/views/Server/ServerList.tsx` - 服务器列表（已更新）
- `frontend/src/api/system.ts` - 系统 API（新增）

### 后端
- `backend/app/apis/v1/system/proxy.py` - 代理检测 API
- `backend/app/utils/req.py` - 网络请求工具

## API 端点

```
GET /v1/system/proxy/check?proxy_url=socks5h://1.2.3.4:1080
```

**响应示例（成功）**：
```json
{
  "message": "代理检测成功",
  "status": "success",
  "proxy_url": "socks5h://1.2.3.4:1080",
  "ip": "5.6.7.8",
  "source": "ipify",
  "details": {
    "raw": "5.6.7.8"
  }
}
```

**响应示例（失败）**：
```json
{
  "message": "代理检测失败，所有检测网站均无法访问",
  "status": "failed",
  "proxy_url": "socks5h://1.2.3.4:1080",
  "ip": null,
  "source": null,
  "details": {
    "error": "所有检测网站均返回非 200 状态码或请求超时"
  }
}
```

## 更新日志

### 2026-01-25
- ✅ 添加"测试代理"按钮
- ✅ 实现代理检测功能
- ✅ 添加加载状态显示
- ✅ 添加结果对话框
- ✅ 优化用户体验
- ✅ 创建系统 API 文件

## 总结

服务器列表现在支持一键测试代理功能，用户可以快速验证代理是否可用。通过调用后端代理检测 API，依次访问多个 IP 检测网站，确保检测结果的准确性。界面友好，操作简单，大大提高了代理管理的效率。
