# 服务器列表筛选功能增强

## 功能描述

为服务器管理下的服务器列表添加了以下筛选功能：
1. **域名筛选** - 支持模糊搜索
2. **代理端口筛选** - 精确匹配端口号
3. **代理类型筛选** - 选择 HTTP 或 SOCKS5
4. **代理类型列** - 在表格中显示代理类型

## 实现细节

### 1. 后端修改

#### 1.1 API 层 (`backend/app/apis/v1/server/info.py`)

添加 `port` 查询参数：

```python
@app.get("", response_model=OutList)
async def gets(
    host: str | None = Query(None, description='服务器地址'),
    domain: str | None = Query(None, description='域名'),
    port: int | None = Query(None, description='代理端口'),  # ← 新增
    # ... 其他参数
):
    return await server_info_crud.get_multi(
        host=host,
        domain=domain,
        port=port,  # ← 新增
        # ... 其他参数
    )
```

更新排序字段正则表达式：
```python
pattern='^(?:-)?(?:id|host|domain|port|create_time|update_time)$'
```

#### 1.2 CRUD 层 (`backend/app/crud/server/info.py`)

添加 `port` 参数支持：

```python
async def get_multi(self,
                    host: str | None = None,
                    domain: str | None = None,
                    port: int | None = None,  # ← 新增
                    # ... 其他参数
                    ) -> OutList:
    query = ServerInfo.all()
    if host:
        query = query.filter(host__icontains=host)
    if domain:
        query = query.filter(domain__icontains=domain)
    if port is not None:  # ← 新增
        query = query.filter(port=port)
    # ... 其他过滤条件
```

### 2. 前端修改

#### 2.1 状态管理 (`frontend/src/views/Server/ServerList.tsx`)

添加新的状态变量：

```typescript
const [searchDomain, setSearchDomain] = useState('')
const [searchPort, setSearchPort] = useState<number>()
const [searchProxyType, setSearchProxyType] = useState<string>()
```

#### 2.2 数据获取

更新 `fetchData` 函数：

```typescript
const fetchData = async () => {
  const res = await getServerList({
    host: searchHost || undefined,
    domain: searchDomain || undefined,  // ← 新增
    port: searchPort,                   // ← 新增
    // ... 其他参数
  })
  
  let items = res.items || []
  
  // 客户端筛选：根据代理类型过滤
  if (searchProxyType) {
    items = items.filter(item => item.proxy_type === searchProxyType)
  }
  
  setData(items)
  setTotal(searchProxyType ? items.length : (res.count || 0))
}
```

#### 2.3 搜索表单

添加新的筛选控件：

```tsx
<Input
  placeholder="域名"
  value={searchDomain}
  onChange={(e) => setSearchDomain(e.target.value)}
  onPressEnter={handleSearch}
  style={{ width: 150 }}
/>

<InputNumber
  placeholder="代理端口"
  value={searchPort}
  onChange={(value) => setSearchPort(value || undefined)}
  onPressEnter={handleSearch}
  style={{ width: 120 }}
  min={1}
  max={65535}
/>

<Select
  placeholder="代理类型"
  value={searchProxyType}
  onChange={setSearchProxyType}
  style={{ width: 120 }}
  allowClear
>
  <Select.Option value="http">HTTP</Select.Option>
  <Select.Option value="socks5">SOCKS5</Select.Option>
</Select>
```

#### 2.4 表格列

添加代理类型列：

```tsx
{
  title: '代理类型',
  dataIndex: 'proxy_type',
  key: 'proxy_type',
  width: 90,
  render: (proxy_type: string) => {
    if (!proxy_type) return '-'
    return (
      <Tag color={proxy_type === 'http' ? 'blue' : 'green'}>
        {proxy_type.toUpperCase()}
      </Tag>
    )
  },
}
```

#### 2.5 重置功能

更新 `handleReset` 函数：

```typescript
const handleReset = () => {
  setSearchHost('')
  setSearchDomain('')        // ← 新增
  setSearchPort(undefined)   // ← 新增
  setSearchProxyType(undefined)  // ← 新增
  // ... 其他重置
}
```

## 筛选功能说明

### 1. 域名筛选
- **类型**：模糊搜索
- **后端实现**：使用 `domain__icontains` 进行不区分大小写的模糊匹配
- **示例**：输入 "0n.lv" 可以匹配 "sd7.0n.lv"

### 2. 代理端口筛选
- **类型**：精确匹配
- **输入范围**：1-65535
- **后端实现**：使用 `port=` 进行精确匹配
- **示例**：输入 "22024" 只匹配端口为 22024 的服务器

### 3. 代理类型筛选
- **类型**：下拉选择
- **选项**：HTTP / SOCKS5
- **实现方式**：客户端筛选（因为代理类型是根据端口范围计算的）
- **逻辑**：
  - HTTP: 端口在 22000-28999 范围内
  - SOCKS5: 端口在 32000-38999 范围内或其他

### 4. 代理类型列
- **显示**：表格中新增一列显示代理类型
- **样式**：
  - HTTP: 蓝色标签
  - SOCKS5: 绿色标签
- **数据来源**：后端根据端口范围自动计算

## 筛选组合

所有筛选条件可以组合使用：

### 示例 1：查找特定域名的 HTTP 代理
```
域名: 0n.lv
代理类型: HTTP
```

### 示例 2：查找特定端口的服务器
```
代理端口: 22024
```

### 示例 3：查找特定分组的 SOCKS5 代理
```
分组: HK-004
代理类型: SOCKS5
```

## 界面布局

筛选控件按以下顺序排列（从左到右）：
1. 主机地址 (150px)
2. 域名 (150px)
3. 代理端口 (120px)
4. 代理类型 (120px)
5. 分组 (180px)
6. 状态 (100px)
7. 是否可以出售 (130px)
8. 创建时间范围 (240px)
9. 更新时间范围 (240px)
10. 搜索按钮
11. 重置按钮

## 表格列顺序

1. 主机地址 (140px)
2. 域名 (150px)
3. 代理端口 (90px)
4. **代理类型 (90px)** ← 新增
5. 分组 (100px)
6. 状态 (70px)
7. 是否可以出售 (110px)
8. 创建时间 (160px)
9. 操作 (300px, 固定右侧)

## 性能优化

### 1. 后端筛选
- 主机地址、域名、端口：在数据库层面筛选
- 减少数据传输量
- 提高查询效率

### 2. 客户端筛选
- 代理类型：在前端筛选
- 原因：代理类型是计算字段，不存储在数据库
- 影响：当使用代理类型筛选时，总数显示为筛选后的数量

### 3. 分页处理
- 代理类型筛选会影响分页
- 建议：先使用其他条件缩小范围，再使用代理类型筛选

## 注意事项

1. **代理类型筛选的限制**
   - 代理类型是客户端筛选，不影响后端查询
   - 如果数据量大，建议先用端口范围筛选：
     - HTTP: 端口 22000-28999
     - SOCKS5: 端口 32000-38999

2. **端口筛选**
   - 只支持精确匹配，不支持范围查询
   - 如需范围查询，可以使用代理类型筛选

3. **域名筛选**
   - 支持模糊搜索
   - 不区分大小写
   - 可以输入部分域名

4. **重置功能**
   - 点击"重置"按钮会清空所有筛选条件
   - 包括新增的域名、端口、代理类型筛选

## 测试验证

### 测试用例 1：域名筛选
```
输入: 0n.lv
预期: 显示所有域名包含 "0n.lv" 的服务器
```

### 测试用例 2：端口筛选
```
输入: 22024
预期: 只显示端口为 22024 的服务器
```

### 测试用例 3：代理类型筛选
```
选择: HTTP
预期: 只显示代理类型为 HTTP 的服务器（端口 22000-28999）
```

### 测试用例 4：组合筛选
```
域名: 0n.lv
代理类型: HTTP
预期: 显示域名包含 "0n.lv" 且代理类型为 HTTP 的服务器
```

### 测试用例 5：重置功能
```
操作: 设置多个筛选条件后点击"重置"
预期: 所有筛选条件清空，显示所有服务器
```

## API 示例

### 请求示例 1：按域名和端口筛选
```bash
curl 'http://127.0.0.1:6080/v1/server/info?domain=0n.lv&port=22024&page=1&limit=10' \
  -H 'Authorization: Bearer <token>'
```

### 请求示例 2：按端口筛选
```bash
curl 'http://127.0.0.1:6080/v1/server/info?port=32024&page=1&limit=10' \
  -H 'Authorization: Bearer <token>'
```

### 响应示例
```json
{
  "message": "成功",
  "count": 2,
  "num": 2,
  "items": [
    {
      "host": "202.155.155.88",
      "domain": "sd7.0n.lv",
      "port": 22024,
      "proxy_type": "http",
      "proxy_url": "http://user_xxx:password@sd7.0n.lv:22024",
      "group": {
        "name": "HK-004"
      }
    },
    {
      "host": "202.155.155.88",
      "domain": "sd7.0n.lv",
      "port": 32024,
      "proxy_type": "socks5",
      "proxy_url": "socks5://user_xxx:password@sd7.0n.lv:32024",
      "group": {
        "name": "HK-004"
      }
    }
  ]
}
```

## 相关文件

### 后端
- `backend/app/apis/v1/server/info.py` - API 路由定义
- `backend/app/crud/server/info.py` - CRUD 操作实现

### 前端
- `frontend/src/views/Server/ServerList.tsx` - 服务器列表页面
- `frontend/src/types/index.ts` - TypeScript 类型定义

## 完成时间

2026-01-25 23:48
