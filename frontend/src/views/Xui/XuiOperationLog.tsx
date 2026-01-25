import { useState, useEffect } from 'react'
import { Table, Button, App, Space, Tag, Popconfirm, Card, Descriptions } from 'antd'
import { ReloadOutlined, RedoOutlined, SyncOutlined } from '@ant-design/icons'
import { useUserStore } from '@/store/useUserStore'
import { 
  getFailedLogs, 
  retryFailedLog, 
  batchRetryFailedLogs,
  type XuiOperationLog 
} from '@/api/xui'

const XuiOperationLogList = () => {
  const { message } = App.useApp()
  const [data, setData] = useState<XuiOperationLog[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [retryingIds, setRetryingIds] = useState<Set<string>>(new Set())
  const [batchRetrying, setBatchRetrying] = useState(false)
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getFailedLogs({
        page,
        limit: pageSize,
        res_count: true
      })
      setData(res.data || [])
      setTotal(res.count || 0)
    } catch (error) {
      setData([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, pageSize])

  const handleRetry = async (logId: string) => {
    setRetryingIds(prev => new Set(prev).add(logId))
    try {
      const result = await retryFailedLog(logId)
      if (result.data.success) {
        message.success('重试成功')
        fetchData()
      } else {
        message.error(result.data.message)
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '重试失败')
    } finally {
      setRetryingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(logId)
        return newSet
      })
    }
  }

  const handleBatchRetry = async () => {
    setBatchRetrying(true)
    try {
      const result = await batchRetryFailedLogs()
      message.success(result.message)
      fetchData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '批量重试失败')
    } finally {
      setBatchRetrying(false)
    }
  }

  const columns = [
    {
      title: '入站信息',
      dataIndex: 'inbound_info',
      key: 'inbound_info',
      width: 150,
    },
    {
      title: '账号用户名',
      dataIndex: 'account_username',
      key: 'account_username',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'is_resolved',
      key: 'is_resolved',
      width: 80,
      render: (isResolved: boolean) => (
        <Tag color={isResolved ? 'success' : 'error'}>
          {isResolved ? '已解决' : '未解决'}
        </Tag>
      ),
    },
    {
      title: '错误信息',
      dataIndex: 'error_message',
      key: 'error_message',
      ellipsis: true,
      render: (text: string) => (
        <span style={{ color: '#ff4d4f' }}>{text || '-'}</span>
      ),
    },
    {
      title: '重试次数',
      dataIndex: 'retry_count',
      key: 'retry_count',
      width: 90,
      align: 'center' as const,
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 160,
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right' as const,
      width: 100,
      render: (_: any, record: XuiOperationLog) => (
        <Space size="small">
          {isAdmin && !record.is_resolved && (
            <Popconfirm
              title="确定重试吗？"
              description="将尝试重新执行此操作"
              onConfirm={() => handleRetry(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="link"
                size="small"
                icon={<RedoOutlined />}
                loading={retryingIds.has(record.id)}
              >
                重试
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: 16 }}>
        <Descriptions title="XUI 操作日志" column={1} size="small">
          <Descriptions.Item label="说明">
            记录 XUI 添加账号失败的日志,失败的操作可以一键重试
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <div style={{ marginBottom: 16 }}>
        <Space wrap>
          <Button icon={<ReloadOutlined />} onClick={fetchData}>
            刷新
          </Button>

          {isAdmin && (
            <Popconfirm
              title="批量重试所有失败的操作？"
              description="将重试所有未解决的添加账号操作"
              onConfirm={handleBatchRetry}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="primary"
                icon={<SyncOutlined />}
                loading={batchRetrying}
              >
                批量重试失败操作
              </Button>
            </Popconfirm>
          )}
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1000 }}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条失败记录`,
          onChange: (page, pageSize) => {
            setPage(page)
            setPageSize(pageSize)
          },
        }}
      />
    </div>
  )
}

export default XuiOperationLogList
