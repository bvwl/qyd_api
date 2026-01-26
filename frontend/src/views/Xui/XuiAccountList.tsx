import { useState, useEffect } from 'react'
import { Table, Button, App, Space, Tag, Popconfirm, Card, Descriptions } from 'antd'
import { ReloadOutlined, PlusOutlined, MinusOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'
import { useUserStore } from '@/store/useUserStore'
import { addAccountToAllInbounds, removeAccountFromAllInbounds } from '@/api/xui'
import { getServerAccountList } from '@/api/server'

interface ServerAccount {
  id: string
  username: string
  user_id?: string
  is_all_inbound_added: boolean
  create_time: string
  update_time: string
}

const XuiAccountList = () => {
  const { message } = App.useApp()
  const [data, setData] = useState<ServerAccount[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [addingIds, setAddingIds] = useState<Set<string>>(new Set())
  const [removingIds, setRemovingIds] = useState<Set<string>>(new Set())
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getServerAccountList({
        page,
        limit: pageSize,
        res_count: true
      })
      setData(res.items || [])
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

  const handleAddToAllInbounds = async (accountId: string) => {
    setAddingIds(prev => new Set(prev).add(accountId))
    try {
      const result = await addAccountToAllInbounds(accountId)
      
      // 后台任务已提交，显示提示信息
      message.success({
        content: '已提交后台任务，正在添加账号到所有入站。任务将在后台执行，请稍后刷新页面查看结果。',
        duration: 5
      })
      
      // 延迟刷新数据，给后台任务一些执行时间
      setTimeout(() => {
        fetchData()
      }, 3000)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '提交任务失败')
    } finally {
      setAddingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(accountId)
        return newSet
      })
    }
  }

  const handleRemoveFromAllInbounds = async (accountId: string) => {
    setRemovingIds(prev => new Set(prev).add(accountId))
    try {
      const result = await removeAccountFromAllInbounds(accountId)
      
      // 后台任务已提交，显示提示信息
      message.success({
        content: '已提交后台任务，正在从所有入站删除账号。任务将在后台执行，请稍后刷新页面查看结果。',
        duration: 5
      })
      
      // 延迟刷新数据，给后台任务一些执行时间
      setTimeout(() => {
        fetchData()
      }, 3000)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '提交任务失败')
    } finally {
      setRemovingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(accountId)
        return newSet
      })
    }
  }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    } finally {
      setRemovingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(accountId)
        return newSet
      })
    }
  }

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 150,
    },
    {
      title: '用户 ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 280,
      render: (text: string) => text || '-',
    },
    {
      title: '入站状态',
      dataIndex: 'is_all_inbound_added',
      key: 'is_all_inbound_added',
      width: 120,
      render: (isAdded: boolean) => (
        isAdded ? (
          <Tag icon={<CheckCircleOutlined />} color="success">
            已全部添加
          </Tag>
        ) : (
          <Tag icon={<CloseCircleOutlined />} color="default">
            未全部添加
          </Tag>
        )
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 160,
    },
    {
      title: '更新时间',
      dataIndex: 'update_time',
      key: 'update_time',
      width: 160,
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right' as const,
      width: 200,
      render: (_: any, record: ServerAccount) => (
        <Space size="small">
          {isAdmin && !record.is_all_inbound_added && (
            <Popconfirm
              title="添加到所有入站？"
              description="将此账号添加到所有 XUI 入站"
              onConfirm={() => handleAddToAllInbounds(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="primary"
                size="small"
                icon={<PlusOutlined />}
                loading={addingIds.has(record.id)}
              >
                添加到所有入站
              </Button>
            </Popconfirm>
          )}
          {isAdmin && record.is_all_inbound_added && (
            <Popconfirm
              title="从所有入站删除？"
              description="将此账号从所有 XUI 入站删除"
              onConfirm={() => handleRemoveFromAllInbounds(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                danger
                size="small"
                icon={<MinusOutlined />}
                loading={removingIds.has(record.id)}
              >
                从所有入站删除
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
        <Descriptions title="XUI 账号管理" column={1} size="small">
          <Descriptions.Item label="说明">
            管理所有服务器账号,支持一键添加到所有 XUI 入站或从所有入站删除
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <div style={{ marginBottom: 16 }}>
        <Space wrap>
          <Button icon={<ReloadOutlined />} onClick={fetchData}>
            刷新
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1300 }}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 个账号`,
          onChange: (page, pageSize) => {
            setPage(page)
            setPageSize(pageSize)
          },
        }}
      />
    </div>
  )
}

export default XuiAccountList
