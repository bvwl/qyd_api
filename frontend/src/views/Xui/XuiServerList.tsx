import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, App, Space, Popconfirm, Tag, Switch, InputNumber, Select } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SyncOutlined, EyeOutlined, EyeInvisibleOutlined } from '@ant-design/icons'
import { useUserStore } from '@/store/useUserStore'
import { 
  getXuiServerList, 
  createXuiServer, 
  updateXuiServer, 
  deleteXuiServer,
  syncXuiInbounds,
  type XuiServer 
} from '@/api/xui'

const XuiServerList = () => {
  const { message } = App.useApp()
  const [data, setData] = useState<XuiServer[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingServer, setEditingServer] = useState<XuiServer | null>(null)
  const [showPassword, setShowPassword] = useState<Record<string, boolean>>({})
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getXuiServerList({ page, limit: pageSize, res_count: true })
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

  const handleAdd = () => {
    setEditingServer(null)
    form.resetFields()
    form.setFieldsValue({
      port: 10010,
      username: 'cqrxy',
      password: 'Zpaily88',
      is_ssl: false,
      web_path: '/web3',
      cert_file: '/opt/xui/fullchain.pem',
      key_file: '/opt/xui/privkey.pem',
      status: 1,
    })
    setModalVisible(true)
  }

  const handleEdit = (record: XuiServer) => {
    setEditingServer(record)
    form.setFieldsValue({
      ...record,
      password: undefined, // 不显示密码
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteXuiServer(id)
      message.success('删除成功')
      fetchData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的服务器')
      return
    }

    Modal.confirm({
      title: '批量删除确认',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个服务器吗？`,
      okText: '确定',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        let successCount = 0
        let failCount = 0
        const errors: string[] = []

        for (const id of selectedRowKeys) {
          try {
            await deleteXuiServer(id as string)
            successCount++
          } catch (error: any) {
            failCount++
            const server = data.find(item => item.id === id)
            errors.push(`${server?.name} - ${error.response?.data?.detail || '删除失败'}`)
          }
        }

        if (failCount === 0) {
          message.success(`成功删除 ${successCount} 个服务器`)
        } else {
          Modal.warning({
            title: '批量删除完成',
            content: (
              <div>
                <p>成功: {successCount} 个</p>
                <p>失败: {failCount} 个</p>
                {errors.length > 0 && (
                  <>
                    <p style={{ marginTop: 8, fontWeight: 'bold' }}>失败详情:</p>
                    {errors.slice(0, 5).map((error, index) => (
                      <p key={index} style={{ fontSize: '12px', color: '#ff4d4f' }}>• {error}</p>
                    ))}
                    {errors.length > 5 && (
                      <p style={{ fontSize: '12px', color: '#ff4d4f' }}>... 还有 {errors.length - 5} 个错误</p>
                    )}
                  </>
                )}
              </div>
            ),
            width: 500,
          })
        }

        setSelectedRowKeys([])
        fetchData()
      },
    })
  }

  const handleSync = async (id: string) => {
    try {
      const res = await syncXuiInbounds(id)
      
      // 后台任务已提交，显示提示信息
      Modal.success({
        title: '同步任务已提交',
        content: (
          <div>
            <p>{res.message}</p>
            <p style={{ marginTop: 8, color: '#666' }}>
              任务正在后台执行，请稍后刷新页面查看结果。
            </p>
          </div>
        ),
      })
      
      // 3秒后自动刷新列表
      setTimeout(() => {
        fetchData()
      }, 3000)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '同步失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      
      if (editingServer) {
        await updateXuiServer(editingServer.id, values)
        message.success('更新成功')
      } else {
        await createXuiServer(values)
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

  const togglePasswordVisibility = (id: string) => {
    setShowPassword(prev => ({
      ...prev,
      [id]: !prev[id]
    }))
  }

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
    },
    {
      title: '服务器地址',
      dataIndex: 'host',
      key: 'host',
      width: 150,
    },
    {
      title: '域名',
      dataIndex: 'domain',
      key: 'domain',
      width: 150,
      render: (text: string) => text || '-',
    },
    {
      title: '端口',
      dataIndex: 'port',
      key: 'port',
      width: 80,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 100,
    },
    {
      title: '密码',
      dataIndex: 'password',
      key: 'password',
      width: 150,
      render: (text: string, record: XuiServer) => {
        if (!isAdmin || !text) return '-'
        return (
          <Space>
            <span>{showPassword[record.id] ? text : '••••••••'}</span>
            <Button
              type="link"
              size="small"
              icon={showPassword[record.id] ? <EyeInvisibleOutlined /> : <EyeOutlined />}
              onClick={() => togglePasswordVisibility(record.id)}
            />
          </Space>
        )
      },
    },
    {
      title: 'HTTPS',
      dataIndex: 'is_ssl',
      key: 'is_ssl',
      width: 80,
      render: (value: boolean) => (
        <Tag color={value ? 'green' : 'default'}>
          {value ? '是' : '否'}
        </Tag>
      ),
    },
    {
      title: 'Web路径',
      dataIndex: 'web_path',
      key: 'web_path',
      width: 100,
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
      title: '备注',
      dataIndex: 'remark',
      key: 'remark',
      width: 150,
      ellipsis: true,
      render: (text: string) => text || '-',
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
      width: 200,
      render: (_: any, record: XuiServer) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<SyncOutlined />}
            onClick={() => handleSync(record.id)}
          >
            同步入站
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
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <h2 style={{ margin: 0 }}>XUI 服务器管理</h2>
        </Space>
        {isAdmin && (
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            添加服务器
          </Button>
        )}
      </div>

      {isAdmin && selectedRowKeys.length > 0 && (
        <div style={{ marginBottom: 16, padding: '12px', background: '#f0f2f5', borderRadius: '4px' }}>
          <Space>
            <span>已选择 {selectedRowKeys.length} 项</span>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={handleBatchDelete}
            >
              批量删除
            </Button>
            <Button onClick={() => setSelectedRowKeys([])}>
              取消选择
            </Button>
          </Space>
        </div>
      )}

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1500 }}
        rowSelection={isAdmin ? {
          selectedRowKeys,
          onChange: (selectedRowKeys) => setSelectedRowKeys(selectedRowKeys),
        } : undefined}
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
        title={editingServer ? '编辑服务器' : '添加服务器'}
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
            label="服务器名称"
            name="name"
            rules={[{ required: true, message: '请输入服务器名称' }]}
          >
            <Input placeholder="例如: HK-001" />
          </Form.Item>

          <Form.Item
            label="服务器地址（IP）"
            name="host"
            rules={[{ required: true, message: '请输入服务器地址' }]}
          >
            <Input placeholder="例如: 192.168.1.1" />
          </Form.Item>

          <Form.Item
            label="域名（用于HTTPS访问）"
            name="domain"
          >
            <Input placeholder="例如: sd1.0n.lv" />
          </Form.Item>

          <Form.Item
            label="端口"
            name="port"
            rules={[{ required: true, message: '请输入端口' }]}
          >
            <InputNumber min={1} max={65535} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input placeholder="XUI 面板登录用户名" />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[
              { required: !editingServer, message: '请输入密码' }
            ]}
          >
            <Input.Password placeholder={editingServer ? '留空则不修改' : 'XUI 面板登录密码'} />
          </Form.Item>

          <Form.Item
            label="使用 HTTPS"
            name="is_ssl"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="Web 路径"
            name="web_path"
            rules={[{ required: true, message: '请输入 Web 路径' }]}
          >
            <Input placeholder="例如: /web3" />
          </Form.Item>

          <Form.Item
            label="SSL 证书文件路径"
            name="cert_file"
          >
            <Input placeholder="例如: /opt/xui/fullchain.pem" />
          </Form.Item>

          <Form.Item
            label="SSL 私钥文件路径"
            name="key_file"
          >
            <Input placeholder="例如: /opt/xui/privkey.pem" />
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
            label="备注"
            name="remark"
          >
            <Input.TextArea rows={3} placeholder="备注信息" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default XuiServerList
