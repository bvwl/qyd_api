import { useEffect, useState } from 'react'
import { Card, Descriptions, Tag, Button, Space } from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined, WarningOutlined } from '@ant-design/icons'
import { Status, EmailType } from '@/types'
import { STATUS_MAP, EMAIL_TYPE_MAP } from '@/utils/constants'
import { formatDateTime, maskPassword } from '@/utils/format'
import { getEmailList } from '@/api/mail'

export default function Diagnostic() {
  const [results, setResults] = useState<any[]>([])

  useEffect(() => {
    runDiagnostics()
  }, [])

  const runDiagnostics = async () => {
    const testResults: any[] = []

    // 测试 1: 检查类型导入
    try {
      testResults.push({
        name: '类型导入测试',
        status: 'success',
        message: `Status: ${JSON.stringify(Status)}, EmailType: ${JSON.stringify(EmailType)}`,
      })
    } catch (error: any) {
      testResults.push({
        name: '类型导入测试',
        status: 'error',
        message: error.message,
      })
    }

    // 测试 2: 检查常量导入
    try {
      testResults.push({
        name: '常量导入测试',
        status: 'success',
        message: `STATUS_MAP: ${Object.keys(STATUS_MAP).length} 项, EMAIL_TYPE_MAP: ${Object.keys(EMAIL_TYPE_MAP).length} 项`,
      })
    } catch (error: any) {
      testResults.push({
        name: '常量导入测试',
        status: 'error',
        message: error.message,
      })
    }

    // 测试 3: 检查工具函数
    try {
      const testDate = '2024-01-01T12:00:00'
      const formattedDate = formatDateTime(testDate)
      const maskedPwd = maskPassword('test123456')
      testResults.push({
        name: '工具函数测试',
        status: 'success',
        message: `formatDateTime: ${formattedDate}, maskPassword: ${maskedPwd}`,
      })
    } catch (error: any) {
      testResults.push({
        name: '工具函数测试',
        status: 'error',
        message: error.message,
      })
    }

    // 测试 4: 检查 API 调用
    try {
      const res = await getEmailList({ page: 1, limit: 1, res_count: true })
      testResults.push({
        name: 'API 调用测试',
        status: 'success',
        message: `成功获取邮箱列表，共 ${res.count || 0} 条记录`,
      })
    } catch (error: any) {
      testResults.push({
        name: 'API 调用测试',
        status: 'error',
        message: error.message || '调用失败',
      })
    }

    // 测试 5: 检查 localStorage
    try {
      const accessToken = localStorage.getItem('access_token')
      const userStorage = localStorage.getItem('user-storage')
      const details = []
      
      if (accessToken) {
        details.push(`access_token: ${accessToken.substring(0, 20)}...`)
      } else {
        details.push('access_token: 不存在')
      }
      
      if (userStorage) {
        try {
          const parsed = JSON.parse(userStorage)
          details.push(`user-storage: 存在 (token: ${parsed.state?.token ? '有' : '无'})`)
        } catch {
          details.push('user-storage: 解析失败')
        }
      } else {
        details.push('user-storage: 不存在')
      }
      
      testResults.push({
        name: 'Token 存储测试',
        status: accessToken ? 'success' : 'error',
        message: details.join(', '),
      })
    } catch (error: any) {
      testResults.push({
        name: 'Token 存储测试',
        status: 'error',
        message: error.message,
      })
    }

    setResults(testResults)
  }

  const getIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 20 }} />
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 20 }} />
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14', fontSize: 20 }} />
      default:
        return null
    }
  }

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'success':
        return <Tag color="success">通过</Tag>
      case 'error':
        return <Tag color="error">失败</Tag>
      case 'warning':
        return <Tag color="warning">警告</Tag>
      default:
        return <Tag>未知</Tag>
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <Card title="系统诊断" extra={<Button onClick={runDiagnostics}>重新测试</Button>}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {results.map((result, index) => (
            <Card key={index} size="small">
              <Descriptions column={1}>
                <Descriptions.Item label={<Space>{getIcon(result.status)} {result.name}</Space>}>
                  <Space direction="vertical">
                    {getStatusTag(result.status)}
                    <div style={{ fontSize: 12, color: '#666' }}>{result.message}</div>
                  </Space>
                </Descriptions.Item>
              </Descriptions>
            </Card>
          ))}
        </Space>
      </Card>

      <Card title="环境信息" style={{ marginTop: 16 }}>
        <Descriptions column={1}>
          <Descriptions.Item label="浏览器">
            {navigator.userAgent}
          </Descriptions.Item>
          <Descriptions.Item label="当前路径">
            {window.location.pathname}
          </Descriptions.Item>
          <Descriptions.Item label="API 地址">
            {import.meta.env.VITE_API_BASE_URL || '/v1'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  )
}
