import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, App, Space, Popconfirm, Tag, Select, InputNumber } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, UserOutlined } from '@ant-design/icons'
import { useUserStore } from '@/store/useUserStore'
import { useNavigate } from 'react-router-dom'
import { 
  getXuiInboundList, 
  getXuiServerList,
  createXuiInbound, 
  updateXuiInbound, 
  deleteXuiInbound,
  type XuiInbound,
  type XuiServer
} from '@/api/xui'

const XuiInboundList = () => {
  const { message } = App.useApp()
  const navigate = useNavigate()
  const [data, setData] = useState<XuiInbound[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingInbound, setEditingInbound] = useState<XuiInbound | null>(null)
  const [serverList, setServerList] = useState<XuiServer[]>([])
  const [searchServerId, setSearchServerId] = useState<string>()
  const [searchPort, setSearchPort] = useState<number>()
  const [searchProtocol, setSearchProtocol] = useState<number>()
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')

  const fetchServerList = async () => {
    try {
      const res = await getXuiServerList({ page: 1, limit: 1000 })
      setServerList(res.items || [])
    } catch (error) {
      setServerList([])
    }
  }

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getXuiInboundList({
        page,
        limit: pageSize,
        res_count: true,
        server_id: searchServerId,
        listen_port: searchPort,
        protocol: searchProtocol,
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
    fetchServerList()
  }, [])

  useEffect(() => {
    fetchData()
  }, [page, pageSize])

  const handleSearch = () => {
    setPage(1)
    fetchData()
  }

  const handleReset = () => {
    setSearchServerId(undefined)
    setSearchPort(undefined)
    setSearchProtocol(undefined)
    setPage(1)
    fetchData()
  }

  const handleAdd = () => {
    setEditingInbound(null)
    form.resetFields()
    form.setFieldsValue({
      protocol: 1,
      status: 1,
      default_username: 'cqrxy',
      default_password: 'Zpaily88',
    })
    setModalVisible(true)
  }

  const handleEdit = (record: XuiInbound) => {
    setEditingInbound(record)
    form.setFieldsValue({
      ...record,
      default_password: undefined, // 不显示密码
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteXuiInbound(id)
      message.success('删除成功')
      fetchData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  const handleManageAccounts = (record: XuiInbound) => {
    navigate(`/xui/account?inbound_id=${record.id}`)
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      
      if (editingInbound) {
        await updateXuiInbound(editingInbound.id, values)
        message.success('更新成功')
      } else {
        await createXuiInbound(values)
        message.success('创建成功')
      }
      
      setModalVisible(false)
      fetchData()
    } catch (error: any) {
      if (error.errorFields) {
        return
      }
      message.error(error.response?.data?.detail || '操作失败')
    }
  }

  const columns = [
    {
      title: '服务器',
      dataIndex: 'server_id',
      key: 'server_id',
      width: 120,
      render: (serverId: string) => {
        const server = serverList.find(s => s.id === serverId)
        return server?.name || serverId
      },
    },
    {
      title: '监听地址',
      dataIndex: 'listen_host',
      key: 'listen_host',
      width: 150,
    },
    {
      title: '监听端口',
      dataIndex: 'listen_port',
      key: 'listen_port',
      width: 100,
    },
    {
      title: '协议',
      dataIndex: 'protocol',
      key: 'protocol',
      width: 80,
      render: (protocol: number) => {
        const protocolMap: Record<number, { text: string; color: string }> = {
          1: { text: 'HTTP', color: 'blue' },
          2: { text: 'SOCKS', color: 'green' },
        }
        const config = protocolMap[protocol] || { text: '未知', color: 'default' }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '备注',
      dataIndex: 'remark',
      key: 'remark',
      width: 150,
      ellipsis: true,
      render: (text: string) => text || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: number) => {
        const statusMap: Record<number, { text: string; color: string }> = {
          1: { text: '正常', color: 'success' },
          2: { text: '停用', color: 'default' },
          3: { text: '异常', color: 'error' },
        }
        const config = statusMap[status] || { text: '未知', color: 'default' }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '默认用户名',
      dataIndex: 'default_username',
      key: 'default_username',
      width: 120,
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
      width: 220,
      render: (_: any, record: XuiInbound) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<UserOutlined />}
            onClick={() => handleManageAccounts(record)}
          >
            账号管理
          </Button>
          {isAdmin && (
            <>
              <Button
                type="link"
                size="small"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Popconfirm
                title="确定删除吗？"
                onConfirm={() => handleDelete(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button
                  type="link"
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                >
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            placeholder="选择服务器"
            style={{ width: 200 }}
            allowClear
            value={searchServerId}
            onChange={setSearchServerId}
          >
            {serverList.map(server => (
              <Select.Option key={server.id} value={server.id}>
                {server.name}
              </Select.Option>
            ))}
          </Select>

          <InputNumber
            placeholder="监听端口"
            style={{ width: 150 }}
            value={searchPort}
            onChange={(value) => setSearchPort(value || undefined)}
          />

          <Select
            placeholder="协议类型"
            style={{ width: 120 }}
            allowClear
            value={searchProtocol}
            onChange={setSearchProtocol}
          >
            <Select.Option value={1}>HTTP</Select.Option>
            <Select.Option value={2}>SOCKS</Select.Option>
          </Select>

          <Button type="primary" onClick={handleSearch}>
            搜索
          </Button>
          <Button onClick={handleReset}>
            重置
          </Button>
          {isAdmin && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              添加入站
            </Button>
          )}
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
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPage(page)
            setPageSize(pageSize)
          },
        }}
      />

      <Modal
        title={editingInbound ? '编辑入站' : '添加入站'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          preserve={false}
        >
          <Form.Item
            label="服务器"
            name="server_id"
            rules={[{ required: true, message: '请选择服务器' }]}
          >
            <Select placeholder="选择服务器">
              {serverList.map(server => (
                <Select.Option key={server.id} value={server.id}>
                  {server.name} ({server.domain || server.host})
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="监听地址"
            name="listen_host"
            rules={[{ required: true, message: '请输入监听地址' }]}
          >
            <Input placeholder="例如: 0.0.0.0 或 192.168.1.1" />
          </Form.Item>

          <Form.Item
            label="监听端口"
            name="listen_port"
            rules={[
              { required: true, message: '请输入监听端口' },
              { type: 'number', min: 20000, max: 33000, message: '端口范围: 20000-33000' }
            ]}
          >
            <InputNumber min={20000} max={33000} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="协议类型"
            name="protocol"
            rules={[{ required: true, message: '请选择协议类型' }]}
          >
            <Select>
              <Select.Option value={1}>HTTP</Select.Option>
              <Select.Option value={2}>SOCKS</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="备注"
            name="remark"
          >
            <Input placeholder="备注信息（用作服务器分组名称）" />
          </Form.Item>

          <Form.Item
            label="状态"
            name="status"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select>
              <Select.Option value={1}>正常</Select.Option>
              <Select.Option value={2}>停用</Select.Option>
              <Select.Option value={3}>异常</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="默认用户名"
            name="default_username"
            rules={[{ required: true, message: '请输入默认用户名' }]}
          >
            <Input placeholder="默认: cqrxy" />
          </Form.Item>

          <Form.Item
            label="默认密码"
            name="default_password"
            rules={[
              { required: !editingInbound, message: '请输入默认密码' }
            ]}
          >
            <Input.Password placeholder={editingInbound ? '留空则不修改' : '默认: Zpaily88'} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default XuiInboundList
