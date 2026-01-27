import { useState, useEffect } from 'react'
import type React from 'react'
import { 
  Card, 
  Select, 
  Input, 
  Button, 
  Space, 
  Tabs, 
  App,
  Table,
  Tag
} from 'antd'
import { 
  SendOutlined,
  PlusOutlined,
  DeleteOutlined,
  CopyOutlined
} from '@ant-design/icons'
import axios from 'axios'
import type { AxiosRequestConfig } from 'axios'
import { TokenManager } from '@/utils/token'
import { copyToClipboard } from '@/utils/format'

const { TextArea } = Input

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:6080'

interface Header {
  key: string
  value: string
  enabled: boolean
}

interface Param {
  key: string
  value: string
  enabled: boolean
}

interface Example {
  name: string
  method: string
  url: string
  params?: Param[]
  body?: string
}

interface ApiTesterProps {
  title: string
  description?: string
  defaultMethod?: string
  defaultUrl: string
  defaultParams?: Param[]
  defaultBody?: string
  examples?: Example[]
}

export default function ApiTester({
  title,
  description,
  defaultMethod = 'GET',
  defaultUrl,
  defaultParams = [],
  defaultBody = '{\n  \n}',
  examples = []
}: ApiTesterProps) {
  const { message } = App.useApp()
  const [method, setMethod] = useState<string>(defaultMethod)
  const [url, setUrl] = useState<string>(defaultUrl)
  const [headers, setHeaders] = useState<Header[]>([
    { key: 'Content-Type', value: 'application/json', enabled: true },
    { key: 'Authorization', value: `Bearer ${TokenManager.getToken()}`, enabled: true }
  ])
  const [params, setParams] = useState<Param[]>(defaultParams)
  const [body, setBody] = useState<string>(defaultBody)
  const [response, setResponse] = useState<unknown>(null)
  const [loading, setLoading] = useState(false)
  const [responseTime, setResponseTime] = useState<number>(0)
  const [statusCode, setStatusCode] = useState<number>(0)

  useEffect(() => {
    setMethod(defaultMethod)
    setUrl(defaultUrl)
    setParams(defaultParams)
    setBody(defaultBody)
  }, [defaultMethod, defaultUrl, defaultParams, defaultBody])

  const handleSend = async () => {
    try {
      setLoading(true)
      const startTime = Date.now()

      const fullUrl = `${API_BASE_URL}${url}`
      
      const requestHeaders: Record<string, string> = {}
      headers.forEach(h => {
        if (h.enabled && h.key && h.value) {
          requestHeaders[h.key] = h.value
        }
      })

      const queryParams: Record<string, string> = {}
      params.forEach(p => {
        if (p.enabled && p.key && p.value) {
          queryParams[p.key] = p.value
        }
      })

      const config: AxiosRequestConfig = {
        method: method.toLowerCase(),
        url: fullUrl,
        headers: requestHeaders,
        params: queryParams,
      }

      if (['POST', 'PUT', 'PATCH'].includes(method)) {
        try {
          config.data = body ? JSON.parse(body) : {}
        } catch (e) {
          message.error('请求体JSON格式错误')
          setLoading(false)
          return
        }
      }

      const res = await axios(config)
      const endTime = Date.now()
      
      setResponse(res.data)
      setStatusCode(res.status)
      setResponseTime(endTime - startTime)
      message.success('请求成功')
    } catch (error: unknown) {
      const endTime = Date.now()
      setResponseTime(endTime - Date.now())
      const axiosError = error as { response?: { status?: number; data?: unknown }; message?: string }
      setStatusCode(axiosError.response?.status || 0)
      setResponse(axiosError.response?.data || { error: axiosError.message || 'Unknown error' })
      message.error('请求失败')
    } finally {
      setLoading(false)
    }
  }

  const loadExample = (example: Example) => {
    setMethod(example.method)
    setUrl(example.url)
    if (example.params) setParams(example.params)
    if (example.body) setBody(example.body)
  }

  const addHeader = () => {
    setHeaders([...headers, { key: '', value: '', enabled: true }])
  }

  const removeHeader = (index: number) => {
    setHeaders(headers.filter((_, i) => i !== index))
  }

  const updateHeader = (index: number, field: 'key' | 'value' | 'enabled', value: string | boolean) => {
    const newHeaders = [...headers]
    if (field === 'enabled') {
      newHeaders[index][field] = value as boolean
    } else {
      newHeaders[index][field] = value as string
    }
    setHeaders(newHeaders)
  }

  const addParam = () => {
    setParams([...params, { key: '', value: '', enabled: true }])
  }

  const removeParam = (index: number) => {
    setParams(params.filter((_, i) => i !== index))
  }

  const updateParam = (index: number, field: 'key' | 'value' | 'enabled', value: string | boolean) => {
    const newParams = [...params]
    if (field === 'enabled') {
      newParams[index][field] = value as boolean
    } else {
      newParams[index][field] = value as string
    }
    setParams(newParams)
  }

  const copyResponse = async () => {
    const success = await copyToClipboard(JSON.stringify(response as Record<string, unknown>, null, 2))
    if (success) {
      message.success('已复制到剪贴板')
    } else {
      message.error('复制失败')
    }
  }

  const headerColumns = [
    {
      title: '启用',
      dataIndex: 'enabled',
      width: 60,
      render: (_: unknown, record: Header) => (
        <input
          type="checkbox"
          checked={record.enabled}
          onChange={(e) => {
            const index = headers.indexOf(record)
            updateHeader(index, 'enabled', e.target.checked)
          }}
        />
      ),
    },
    {
      title: 'Key',
      dataIndex: 'key',
      render: (_: unknown, record: Header) => {
        const index = headers.indexOf(record)
        return (
          <Input
            value={record.key}
            onChange={(e) => updateHeader(index, 'key', e.target.value)}
            placeholder="Header名称"
            size="small"
          />
        )
      },
    },
    {
      title: 'Value',
      dataIndex: 'value',
      render: (_: unknown, record: Header) => {
        const index = headers.indexOf(record)
        return (
          <Input
            value={record.value}
            onChange={(e) => updateHeader(index, 'value', e.target.value)}
            placeholder="Header值"
            size="small"
          />
        )
      },
    },
    {
      title: '操作',
      width: 80,
      render: (_: unknown, record: Header) => {
        const index = headers.indexOf(record)
        return (
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => removeHeader(index)}
            size="small"
          />
        )
      },
    },
  ]

  const paramColumns = [
    {
      title: '启用',
      dataIndex: 'enabled',
      width: 60,
      render: (_: unknown, record: Param) => (
        <input
          type="checkbox"
          checked={record.enabled}
          onChange={(e) => {
            const index = params.indexOf(record)
            updateParam(index, 'enabled', e.target.checked)
          }}
        />
      ),
    },
    {
      title: 'Key',
      dataIndex: 'key',
      render: (_: unknown, record: Param) => {
        const index = params.indexOf(record)
        return (
          <Input
            value={record.key}
            onChange={(e) => updateParam(index, 'key', e.target.value)}
            placeholder="参数名"
            size="small"
          />
        )
      },
    },
    {
      title: 'Value',
      dataIndex: 'value',
      render: (_: unknown, record: Param) => {
        const index = params.indexOf(record)
        return (
          <Input
            value={record.value}
            onChange={(e) => updateParam(index, 'value', e.target.value)}
            placeholder="参数值"
            size="small"
          />
        )
      },
    },
    {
      title: '操作',
      width: 80,
      render: (_: unknown, record: Param) => {
        const index = params.indexOf(record)
        return (
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => removeParam(index)}
            size="small"
          />
        )
      },
    },
  ]

  const requestTabs: Array<{
    key: string
    label: string
    children: React.ReactNode
  }> = [
    {
      key: 'params',
      label: 'Query参数',
      children: (
        <div>
          <Table
            dataSource={params}
            columns={paramColumns}
            pagination={false}
            size="small"
            rowKey={(_, index) => `param-${index}`}
          />
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={addParam}
            style={{ marginTop: 8, width: '100%' }}
            size="small"
          >
            添加参数
          </Button>
        </div>
      ),
    },
    {
      key: 'headers',
      label: 'Headers',
      children: (
        <div>
          <Table
            dataSource={headers}
            columns={headerColumns}
            pagination={false}
            size="small"
            rowKey={(_, index) => `header-${index}`}
          />
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={addHeader}
            style={{ marginTop: 8, width: '100%' }}
            size="small"
          >
            添加Header
          </Button>
        </div>
      ),
    },
    {
      key: 'body',
      label: 'Body',
      children: (
        <TextArea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="请输入JSON格式的请求体"
          rows={8}
          style={{ fontFamily: 'monospace', fontSize: 12 }}
        />
      ),
    },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <Card title={title} variant="outlined">
        {description && (
          <div style={{ marginBottom: 16, padding: 12, background: '#f0f2f5', borderRadius: 4 }}>
            <p style={{ margin: 0, color: '#666' }}>{description}</p>
          </div>
        )}

        {examples.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>示例：</div>
            <Space wrap>
              {examples.map((example, index) => (
                <Button
                  key={index}
                  size="small"
                  onClick={() => loadExample(example)}
                >
                  {example.name}
                </Button>
              ))}
            </Space>
          </div>
        )}

        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Space.Compact style={{ width: '100%' }}>
            <Select
              value={method}
              onChange={setMethod}
              style={{ width: 120 }}
            >
              <Select.Option value="GET">
                <Tag color="blue">GET</Tag>
              </Select.Option>
              <Select.Option value="POST">
                <Tag color="green">POST</Tag>
              </Select.Option>
              <Select.Option value="PUT">
                <Tag color="orange">PUT</Tag>
              </Select.Option>
              <Select.Option value="DELETE">
                <Tag color="red">DELETE</Tag>
              </Select.Option>
              <Select.Option value="PATCH">
                <Tag color="purple">PATCH</Tag>
              </Select.Option>
            </Select>
            <Input
              value={API_BASE_URL}
              disabled
              style={{ width: 200 }}
            />
            <Input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="请输入API路径"
              style={{ flex: 1 }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={loading}
            >
              发送
            </Button>
          </Space.Compact>

          <Tabs items={requestTabs} size="small" />
        </Space>
      </Card>

      {response !== null && (
        <Card
          title={
            <Space>
              <span>响应结果</span>
              <Tag color={statusCode >= 200 && statusCode < 300 ? 'success' : 'error'}>
                {statusCode}
              </Tag>
              <Tag>{responseTime}ms</Tag>
            </Space>
          }
          variant="outlined"
          extra={
            <Button
              icon={<CopyOutlined />}
              onClick={copyResponse}
              size="small"
            >
              复制
            </Button>
          }
        >
          <pre
            style={{
              background: '#f5f5f5',
              padding: 16,
              borderRadius: 4,
              maxHeight: 400,
              overflow: 'auto',
              fontFamily: 'monospace',
              fontSize: 12,
              margin: 0,
            }}
          >
            {JSON.stringify(response as Record<string, unknown>, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  )
}
