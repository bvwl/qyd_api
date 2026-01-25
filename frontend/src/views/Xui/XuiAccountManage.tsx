import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, App, Space, Popconfirm, Tag, Select, Card } from 'antd'
import { PlusOutlined, DeleteOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import { useUserStore } from '@/store/useUserStore'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { 
  getXuiAccountsByInbound,
  getXuiInboundDetail,
  addAccountToInbound,
  removeAccountFromInbound,
  type XuiAccount
} from '@/api/xui'
import { getServerAccountList } from '@/api/server'

interface ServerAccount {
  id: string
  username: string
  user_id?: string
}

interface XuiInbound {
  id: string
  listen_host: string
  listen_port: number
  protocol: number
  remark?: string
}

const XuiAccountManage = () => {
  const { message } = App.useApp()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const inboundId = searchParams.get('inbound_id')
  
  const [data, setData] = useState<XuiAccount[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [inboundInfo, setInboundInfo] = useState<XuiInbound | null>(null)
  const [availableAccounts, setAvailableAccounts] = useState<ServerAccount[]>([])
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')

  const fetchInboundInfo = async () => {
    if (!inboundId) return
    
    try {
      const res = await getXuiInboundDetail(inboundId)
      setInboundInfo(res)
    } catch (error) {
      message.error('获取入站信息失败')
    }
  }

  const fetchAvailableAccounts = async () => {
    try {
      const res = await getServerAccountList({ page: 1, limit: 1000 })
      setAvailableAccounts(res.items || [])
    } catch (error) {
      setAvailableAccounts([])
    }
  }

  const fetchData = async () => {
    if (!inboundId) return
    
    setLoading(true)
    try {
      const res = await getXuiAccountsByInbound(inboundId)
      setData(res.items || [])
      setTotal(res.items?.length || 0)
    } catch (error) {
      setData([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (inboundId) {
      fetchInboundInfo()
      fetchAvailableAccounts()
    }
  }, [inboundId])

  useEffect(() => {
    fetchData()
  }, [page, pageSize, inboundId])

  const handleAdd = () => {
    form.resetFields()
    setModalVisible(true)
  }

  const handleRemove = async (accountId: string) => {
    if (!inboundId) return
    
    try {
      await removeAccountFromInbound(inboundId, accountId)
      message.success('移除成功')
      fetchData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '移除失败')
    }
  }

  const handleSubmit = async () => {
    if (!inboundId) return
    
    try {
      const values = await form.validateFields()
      
      await addAccountToInbound(inboundId, values.account_id)
      message.success('添加成功')
      
      setModalVisible(false)
      fetchData()
    } catch (error: any) {
      if (error.errorFields) {
        return
      }
      message.error(error.response?.data?.detail || '添加失败')
    }
  }

  const handleBack = () => {
    navigate('/xui/inbound')
  }

  const columns = [
    {
      title: '邮箱/用户名',
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: 'UUID',
      dataIndex: 'uuid',
      key: 'uuid',
      width: 250,
      ellipsis: true,
    },
    {
      title: '启用状态',
      dataIndex: 'enable',
      key: 'enable',
      width: 100,
      render: (enable: boolean) => (
        <Tag color={enable ? 'success' : 'default'}>
          {enable ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '流量限制',
      dataIndex: 'total_gb',
      key: 'total_gb',
      width: 120,
      render: (total_gb: number) => total_gb > 0 ? `${total_gb} GB` : '无限制',
    },
    {
      title: 'IP限制',
      dataIndex: 'limit_ip',
      key: 'limit_ip',
      width: 100,
      render: (limit_ip: number) => limit_ip > 0 ? limit_ip : '无限制',
    },
    {
      title: '上传流量',
      dataIndex: 'up',
      key: 'up',
      width: 120,
      render: (up: number) => `${(up / 1024 / 1024 / 1024).toFixed(2)} GB`,
    },
    {
      title: '下载流量',
      dataIndex: 'down',
      key: 'down',
      width: 120,
      render: (down: number) => `${(down / 1024 / 1024 / 1024).toFixed(2)} GB`,
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right' as const,
      width: 120,
      render: (_: any, record: XuiAccount) => (
        <Space size="small">
          {isAdmin && (
            <Popconfirm
              title="确定移除吗？"
              description="移除后该账号将无法使用此入站"
              onConfirm={() => handleRemove(record.email)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
              >
                移除
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  if (!inboundId) {
    return (
      <div style={{ padding: '24px' }}>
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <p>请从入站列表选择一个入站进行账号管理</p>
            <Button type="primary" onClick={handleBack}>
              返回入站列表
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={handleBack}>
              返回
            </Button>
            <h3 style={{ margin: 0 }}>入站账号管理</h3>
          </Space>
          
          {inboundInfo && (
            <div>
              <Space split="|">
                <span>监听地址: {inboundInfo.listen_host}:{inboundInfo.listen_port}</span>
                <span>
                  协议: 
                  <Tag color={inboundInfo.protocol === 1 ? 'blue' : 'green'} style={{ marginLeft: 8 }}>
                    {inboundInfo.protocol === 1 ? 'HTTP' : 'SOCKS'}
                  </Tag>
                </span>
                {inboundInfo.remark && <span>备注: {inboundInfo.remark}</span>}
              </Space>
            </div>
          )}
        </Space>
      </Card>

      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-end' }}>
        {isAdmin && (
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            添加账号
          </Button>
        )}
      </div>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="email"
        loading={loading}
        scroll={{ x: 1200 }}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPage(page)
            setPageSize(pageSize)
          },
        }}
      />

      <Modal
        title="添加账号到入站"
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          preserve={false}
        >
          <Form.Item
            label="选择服务器账号"
            name="account_id"
            rules={[{ required: true, message: '请选择服务器账号' }]}
          >
            <Select
              placeholder="选择账号"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={availableAccounts.map(account => ({
                label: `${account.username} ${account.user_id ? `(用户: ${account.user_id})` : ''}`,
                value: account.id,
              }))}
            />
          </Form.Item>

          <div style={{ color: '#666', fontSize: '12px' }}>
            <p>说明：</p>
            <ul style={{ paddingLeft: 20, margin: 0 }}>
              <li>添加账号后，该账号将可以使用此入站进行代理访问</li>
              <li>账号的用户名和密码将自动同步到 XUI 面板</li>
              <li>如果账号已存在于入站中，将提示错误</li>
            </ul>
          </div>
        </Form>
      </Modal>
    </div>
  )
}

export default XuiAccountManage
